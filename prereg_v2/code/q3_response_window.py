"""Preprocessing census q3. Which time window carries the response to a clip?

Scientific question
-------------------
The existing stimulus response is the mean over [onset, offset) with no
hemodynamic delay, while clips follow one another with no gap. Does that
window carry the response to its own clip, or a mixture that includes the
preceding clip? Is a delayed window or a GLM better, judged without any
emotion label?

What this excludes
------------------
If the zero-delay window is contaminated by the preceding clip, every
downstream result built on roi_mean rests on patterns that partly belong to a
neighbour, and because all five participants saw the same order, the
contamination is shared across participants and would pass for a shared
stimulus-locked response. prereg_v2 B1 requires the response estimate to be
chosen label-blind; these criteria use no annotation.

Criteria, fixed before looking at the result
--------------------------------------------
Primary. Repeat reliability over the 16 canonical stimuli presented twice.
  The two presentations sit at different positions after different
  predecessors, so contamination cannot inflate their agreement.
Secondary. Neighbour contamination. Because the order is identical across
  participants, a pattern x_k = s_k + c s_{k-1} + noise gives, across
  participants, (r(a_k,b_{k-1}) - r_far) / (r(a_k,b_k) - r_far) ~ c/(1+c^2).
  Within participants, r(k, k-1) - r_far is reported as well.
Physiological check. Latency of the response to the first clip after the 32 s
  baseline that opens each run, in ROIs selected on even runs and measured on
  odd runs.

Methods compared: window means delayed by 0 to 4 TR (window length = presented
duration), and a least-squares-all GLM with one canonical-HRF regressor per
presentation and a 128 s DCT drift basis.

Change after the first run (exploratory, recorded per AGENTS.md)
---------------------------------------------------------------
The first run showed the zero-delay window best, delays monotonically worse,
a GLM whose adjacent betas were nearly identical, and a run-start response
that begins rising 2 to 4 s before the nominal first onset. The simplest
explanation is that step7 already delayed its segment onsets by about 4 s.
That evidence, not a new argument, caused three additions: windows starting
1 and 2 TR before the nominal onset, a least-squares fit of the onset offset
delta to the run-start response, and a GLM with onsets moved by -4 s. The
primary criterion is unchanged.

Outputs
-------
qc/response_window.tsv     method x ROI form x participant
qc/response_window.json    subject means and the onset-latency check
qc/onset_response.tsv      onset-locked mean time course
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import gamma  # noqa: E402

from _assets import MANIFESTS, provenance, read_tsv, write_json, write_tsv  # noqa: E402
from _qc import QC, QC_ROI, SUBJECTS, TR  # noqa: E402

SCRIPT = "prereg_v2/code/q3_response_window.py"
SHIFTS = [-2, -1, 0, 1, 2, 3, 4]
GLM_OFFSETS_S = [0.0, -4.0]
FAR = 5          # positions apart within a run counted as unrelated
DCT_CUTOFF = 128.0
DT = 0.1


def canonical_hrf(dt=DT, length=32.0):
    t = np.arange(0, length, dt)
    h = gamma.pdf(t, 6) - gamma.pdf(t, 16) / 6.0
    return h / h.sum()


def dct_basis(n, tr, cutoff):
    k = int(np.floor(2 * n * tr / cutoff)) + 1
    t = np.arange(n)
    B = [np.ones(n)]
    for j in range(1, k):
        B.append(np.cos(np.pi * j * (2 * t + 1) / (2 * n)))
    return np.stack(B, 1)


def load_runs(subj, form):
    z = np.load(QC_ROI / f"{subj}.npz", allow_pickle=True)
    runs = []
    for i in range(len(z["run_keys"])):
        Y = z[f"{form}__{i}"].astype(np.float64)
        if np.isnan(Y).any():
            col = np.nanmean(Y, 0)
            Y = np.where(np.isnan(Y), col, Y)
        runs.append((str(z["run_keys"][i]), Y, pd.DataFrame(z[f"segtable__{i}"])))
    return runs


def patterns(runs, method, hrf):
    """dict stimulus_number -> (450,) pattern, and dict of run positions."""
    P, pos = {}, {}
    for key, Y, st in runs:
        n = Y.shape[0]
        stims = st[~st.is_baseline]
        if method.startswith("shift"):
            s = int(method[5:])
            for r in stims.itertuples():
                a = max(int(r.onset_tr) + s, 0)
                b = min(int(r.onset_tr) + s + int(r.duration_tr), n)
                P[int(r.stimulus_number)] = Y[a:b].mean(0)
        elif method.startswith("glm_lsa"):
            off = float(method.split("@")[1]) if "@" in method else 0.0
            fine = int(round(n * TR / DT))
            cols = []
            for r in stims.itertuples():
                box = np.zeros(fine)
                a0 = max(int(round((r.onset_tr * TR + off) / DT)), 0)
                a1 = max(int(round(((r.onset_tr + r.duration_tr) * TR + off) / DT)), 0)
                box[a0:a1] = 1
                reg = np.convolve(box, hrf)[:fine]
                cols.append(reg[(np.arange(n) * TR / DT).astype(int)])
            X = np.column_stack(cols + [dct_basis(n, TR, DCT_CUTOFF)])
            beta = np.linalg.lstsq(X, Y, rcond=None)[0]
            for j, r in enumerate(stims.itertuples()):
                P[int(r.stimulus_number)] = beta[j]
        order = stims.sort_values("onset_tr").stimulus_number.astype(int).tolist()
        for i, sn in enumerate(order):
            pos[sn] = (key, i, order)
    return P, pos


def zcols(M):
    M = M - M.mean(0)
    sd = M.std(0); sd[sd == 0] = 1
    return M / sd


def rowcorr(A, B):
    A = A - A.mean(1, keepdims=True); B = B - B.mean(1, keepdims=True)
    return (A * B).sum(1) / np.sqrt((A ** 2).sum(1) * (B ** 2).sum(1))


def main() -> None:
    prov = provenance(SCRIPT, {"shifts_tr": SHIFTS, "far_positions": FAR,
                               "dct_cutoff_s": DCT_CUTOFF, "hrf": "SPM canonical double gamma 6/16/6"})
    cw = read_tsv(MANIFESTS / "stimulus_crosswalk.tsv")
    pairs = [sorted(g.video_number.astype(int).tolist())
             for _, g in cw.groupby("canonical_stimulus_id") if len(g) == 2]
    assert len(pairs) == 16, len(pairs)
    hrf = canonical_hrf()
    methods = [f"shift{s}" for s in SHIFTS] + [f"glm_lsa@{o:g}" for o in GLM_OFFSETS_S]
    rng = np.random.default_rng(20260927)

    rows, cross = [], []
    for form in ("roi_all", "roi_brain"):
        runs_by_s = {s: load_runs(s, form) for s in SUBJECTS}
        for m in methods:
            Z, POS = {}, None
            for s in SUBJECTS:
                P, pos = patterns(runs_by_s[s], m, hrf)
                ids = np.array(sorted(P))
                M = zcols(np.stack([P[i] for i in ids]))
                Z[s] = (ids, M)
                POS = pos
            ids = Z[SUBJECTS[0]][0]
            ix = {int(v): i for i, v in enumerate(ids)}
            prev, far = [], []
            for sn in ids:
                key, i, order = POS[int(sn)]
                if i == 0:
                    continue
                cand = [order[j] for j in range(len(order)) if abs(j - i) >= FAR]
                prev.append((ix[int(sn)], ix[order[i - 1]]))
                far.append((ix[int(sn)], ix[cand[rng.integers(len(cand))]]))
            prev = np.array(prev); far = np.array(far)
            for s in SUBJECTS:
                M = Z[s][1]
                rep = [np.corrcoef(M[ix[a]], M[ix[b]])[0, 1] for a, b in pairs]
                rep_null = rowcorr(M[[ix[a] for a, _ in pairs] * 20],
                                   M[rng.integers(0, len(ids), 16 * 20)])
                wp = rowcorr(M[prev[:, 0]], M[prev[:, 1]]).mean()
                wf = rowcorr(M[far[:, 0]], M[far[:, 1]]).mean()
                rows.append({"form": form, "method": m, "participant_id": s,
                             "repeat_r_mean": float(np.mean(rep)),
                             "repeat_r_twins_1_11": float(np.mean(rep[:11])),
                             "repeat_r_inset_5": float(np.mean(rep[11:])),
                             "repeat_r_null_mean": float(rep_null.mean()),
                             "within_prev_r": float(wp), "within_far_r": float(wf),
                             "within_prev_minus_far": float(wp - wf)})
            for a, b in combinations(SUBJECTS, 2):
                A, B = Z[a][1], Z[b][1]
                same = rowcorr(A, B).mean()
                pr = rowcorr(A[prev[:, 0]], B[prev[:, 1]]).mean()
                fr = rowcorr(A[far[:, 0]], B[far[:, 1]]).mean()
                cross.append({"form": form, "method": m, "pair": f"{a}|{b}",
                              "cross_same_r": float(same), "cross_prev_r": float(pr), "cross_far_r": float(fr),
                              "contamination_ratio": float((pr - fr) / (same - fr))})
            print(f"  {form:9s} {m:8s} done", flush=True)

    df = pd.DataFrame(rows); cx = pd.DataFrame(cross)
    agg = (df.groupby(["form", "method"])
             [["repeat_r_mean", "repeat_r_null_mean", "within_prev_minus_far"]].mean()
             .join(cx.groupby(["form", "method"])[["cross_same_r", "cross_prev_r", "contamination_ratio"]].mean()))
    agg["repeat_r_min_over_participants"] = df.groupby(["form", "method"]).repeat_r_mean.min()

    # ---- onset offset after the opening baseline --------------------------
    # Fit a canonical-HRF block response shifted by delta to the run-start
    # curve, over the rising part only (TR 6 to 22), with free baseline and
    # amplitude. delta < 0 means the response behaves as if the stimulus began
    # before the nominal onset.
    fine_t = np.arange(0, 41 * TR, DT)
    def block_pred(delta):
        box = (fine_t >= 16 * TR + delta).astype(float)
        r = np.convolve(box, hrf)[:fine_t.size]
        return r[(np.arange(41) * TR / DT).astype(int)]
    deltas = np.arange(-10.0, 6.01, 0.5)
    on_rows, lat = [], {}
    for s in SUBJECTS:
        runs = load_runs(s, "roi_all")
        segs = [(k, Y, st) for k, Y, st in runs if st.iloc[0].is_baseline and int(st.iloc[0].duration_tr) == 16]
        W = np.stack([Y[:41, :400] for _, Y, _ in segs if Y.shape[0] >= 41])
        even, odd = W[0::2].mean(0), W[1::2].mean(0)
        gain = even[18:25].mean(0) - even[6:12].mean(0)
        top = np.argsort(gain)[-20:]
        tc = odd[:, top].mean(1)
        fit = slice(6, 23)
        sse = []
        for dlt in deltas:
            X = np.column_stack([np.ones(41), block_pred(dlt)])[fit]
            b = np.linalg.lstsq(X, tc[fit], rcond=None)[0]
            sse.append(float(((X @ b - tc[fit]) ** 2).sum()))
        best = float(deltas[int(np.argmin(sse))])
        lo = tc[8:14].min(); hi = tc[17:23].max()
        half = lo + 0.5 * (hi - lo)
        t_half = next((t for t in range(10, 30) if tc[t] >= half), None)
        f = (half - tc[t_half - 1]) / (tc[t_half] - tc[t_half - 1])
        emp_half = (t_half - 1 + f - 16) * TR
        pr = block_pred(0.0); pl, ph = pr[8:14].min(), pr[17:23].max()
        ph_half = pl + 0.5 * (ph - pl)
        tp = next(t for t in range(10, 30) if pr[t] >= ph_half)
        fp = (ph_half - pr[tp - 1]) / (pr[tp] - pr[tp - 1])
        can_half = (tp - 1 + fp - 16) * TR
        lat[s] = {"n_runs": int(W.shape[0]), "fitted_onset_offset_s": best,
                  "empirical_half_rise_s_from_nominal_onset": float(emp_half),
                  "canonical_half_rise_s_from_onset": float(can_half),
                  "implied_offset_s": float(emp_half - can_half)}
        for t in range(41):
            on_rows.append({"participant_id": s, "tr_from_run_start": t,
                            "seconds_from_first_onset": (t - 16) * TR, "mean_top20_roi": float(tc[t]),
                            "canonical_at_fitted_offset": float(block_pred(best)[t])})
    lat_mean = float(np.mean([v["fitted_onset_offset_s"] for v in lat.values()]))

    out = {"provenance": prov,
           "n_repeat_pairs": len(pairs),
           "summary_by_method": agg.reset_index().to_dict(orient="records"),
           "onset_offset": lat,
           "fitted_onset_offset_s_mean": lat_mean,
           "reading_note": (
               "repeat_r is the primary criterion. contamination_ratio estimates "
               "c/(1+c^2) for a predecessor weight c. The onset latency says how many "
               "seconds after a clip starts its response reaches half height; with a "
               "5 TR window and no delay, that span of the window is dominated by the "
               "preceding clip.")}
    write_tsv(QC / "response_window.tsv", df.merge(
        cx.groupby(["form", "method"])[["cross_same_r", "cross_prev_r", "contamination_ratio"]].mean().reset_index(),
        on=["form", "method"]), prov)
    write_tsv(QC / "onset_response.tsv", pd.DataFrame(on_rows), prov)
    write_json(QC / "response_window.json", out)
    pd.set_option("display.width", 200)
    print(agg.round(4).to_string())
    for k, v in lat.items():
        print(f"  {k}: fitted offset {v['fitted_onset_offset_s']:+.1f} s, empirical half-rise "
              f"{v['empirical_half_rise_s_from_nominal_onset']:+.2f} s vs canonical {v['canonical_half_rise_s_from_onset']:+.2f} s "
              f"-> implied {v['implied_offset_s']:+.2f} s")
    print("  mean fitted onset offset (s):", round(lat_mean, 2))


if __name__ == "__main__":
    main()
