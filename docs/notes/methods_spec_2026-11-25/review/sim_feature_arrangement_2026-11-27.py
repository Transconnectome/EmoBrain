"""Selected-vs-random head list: brain-based neighbour estimate of emotion rating e.

Generative model
  z  : latent stimulus content (d_z dims), iid N(0,1)
  e  : rating = 0.8 z0 + 0.4 z1 + 0.45 eps  (content-driven rating, var ~ 1)
  x_sel, x_rand : head features (p dims) = z[:,S] @ M + feature noise
  y  : voxels = sqrt(snr) * signal + N(0,1) noise, signal var per voxel = 1

Scenarios (how lists and brain differ)
  subset   : x_sel carries {z0,z1}+8 other dims; x_rand carries 10 random non-e dims.
             brain encodes all z equally -> equal encoding accuracy by symmetry.
  reweight : both lists carry ALL z dims; x_sel has 4x variance on z0,z1.
             (same content, only feature-space geometry differs)
  direct_e : lists as in `subset`; brain encodes e itself (+ content unseen by
             either list), not z. "brain carries e info, heads merely correlate with e".

Procedure (as in the document)
  W: ridge x->y on scanned training videos (alpha by inner holdout).
  estimate(t): Pearson over voxels between query q_t and W x_c for every candidate c
               (candidates = scanned train videos + unscanned rated videos; never t);
               mean e of top-N candidates. Score = Pearson r(estimate, e_test).
  queries: brain   q_t = y_t
           ref_nf  q_t = W x_t              (reviewer's noise-free reference)
           ref_x   kNN in raw z-scored feature space x (no brain, no W)
"""
import numpy as np, sys

D_Z, P, V = 40, 128, 300
N_TRAIN, N_TEST, N_EXTRA, TOPN = 400, 100, 400, 10


def zs(a, ref):
    return (a - ref.mean(0)) / (ref.std(0) + 1e-12)


def rowcorr(A, B):
    A = A - A.mean(1, keepdims=True); A /= np.linalg.norm(A, axis=1, keepdims=True) + 1e-12
    B = B - B.mean(1, keepdims=True); B /= np.linalg.norm(B, axis=1, keepdims=True) + 1e-12
    return A @ B.T


def ridge(X, Y, alpha):
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    return Vt.T @ np.diag(s / (s ** 2 + alpha)) @ U.T @ Y


def fit_W(X, Y, rng):
    n = len(X); idx = rng.permutation(n); cut = int(0.8 * n)
    a, b = idx[:cut], idx[cut:]
    best, besta = -np.inf, None
    for alpha in 10.0 ** np.arange(-1, 6):
        Wt = ridge(X[a], Y[a], alpha)
        r = np.mean(np.diag(rowcorr((X[b] @ Wt).T, Y[b].T)))
        if r > best:
            best, besta = r, alpha
    return ridge(X, Y, besta)


def knn_est(Q, Pc, e_c):
    C = rowcorr(Q, Pc)
    idx = np.argpartition(-C, TOPN, axis=1)[:, :TOPN]
    return e_c[idx].mean(1)


def pr(a, b):
    return np.corrcoef(a, b)[0, 1]


def make_features(z, S, M, fnoise, rng):
    return z[:, S] @ M + fnoise * rng.standard_normal((len(z), M.shape[1]))


def run(scenario, snr, seed):
    rng = np.random.default_rng(seed)
    n = N_TRAIN + N_TEST + N_EXTRA
    z = rng.standard_normal((n, D_Z))
    e = 0.8 * z[:, 0] + 0.4 * z[:, 1] + 0.45 * rng.standard_normal(n)

    others = rng.permutation(np.arange(2, D_Z))
    if scenario in ("subset", "direct_e", "brain_no_e"):
        S_sel = np.r_[0, 1, others[:8]]
        S_rand = rng.permutation(np.arange(2, D_Z))[:10]
        M_sel = rng.standard_normal((10, P)); M_rand = rng.standard_normal((10, P))
        fn = 2.0
    elif scenario == "reweight":
        S_sel = S_rand = np.arange(D_Z)
        M_sel = rng.standard_normal((D_Z, P)); M_sel[:2] *= 4.0
        M_rand = rng.standard_normal((D_Z, P))
        fn = 4.0
    x_sel = make_features(z, S_sel, M_sel, fn, rng)
    x_rand = make_features(z, S_rand, M_rand, fn, rng)

    if scenario == "direct_e":
        q = rng.standard_normal((n, 9))           # content no list carries
        src = np.c_[(e - e.mean()) / e.std(), q]
        B = rng.standard_normal((10, V)) / np.sqrt(10)
    elif scenario == "brain_no_e":               # brain encodes all content EXCEPT z0,z1
        src = z.copy(); src[:, :2] = 0.0
        B = rng.standard_normal((D_Z, V)) / np.sqrt(D_Z - 2)
    else:
        src = z
        B = rng.standard_normal((D_Z, V)) / np.sqrt(D_Z)
    sig = src @ B
    y = np.sqrt(snr) * sig + rng.standard_normal((n, V))

    tr = np.arange(N_TRAIN); te = np.arange(N_TRAIN, N_TRAIN + N_TEST)
    ex = np.arange(N_TRAIN + N_TEST, n)
    cand = np.r_[tr, ex]                         # never contains a test video

    out = {}
    for name, x in (("sel", x_sel), ("rand", x_rand)):
        X = zs(x, x[tr]); Y = zs(y, y[tr])
        W = fit_W(X[tr], Y[tr], rng)
        Pc = X[cand] @ W
        enc = np.mean(np.diag(rowcorr((X[te] @ W).T, Y[te].T)))
        r_brain = pr(knn_est(Y[te], Pc, e[cand]), e[te])
        r_nf = pr(knn_est(X[te] @ W, Pc, e[cand]), e[te])
        r_x = pr(knn_est(X[te], X[cand], e[cand]), e[te])
        out[name] = dict(enc=enc, brain=r_brain, nf=r_nf, xonly=r_x)
    return out


if __name__ == "__main__":
    nseed = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    snrs = {"0 (none)": 0.0, "low": 0.02, "high": 0.2}
    for scen in (sys.argv[2].split(",") if len(sys.argv) > 2 else ("subset", "reweight", "direct_e", "brain_no_e")):
        print(f"\n=== scenario: {scen} ===")
        print(f"{'SNR':9s} {'enc_sel':>8s} {'enc_rnd':>8s} | {'brain_sel':>9s} {'brain_rnd':>9s} "
              f"{'diff':>14s} | {'nf_sel':>6s} {'nf_rnd':>6s} | {'x_sel':>5s} {'x_rnd':>5s}")
        for lab, snr in snrs.items():
            R = [run(scen, snr, 1000 * s + 7) for s in range(nseed)]
            g = lambda l, k: np.array([r[l][k] for r in R])
            d = g("sel", "brain") - g("rand", "brain")
            print(f"{lab:9s} {g('sel','enc').mean():8.3f} {g('rand','enc').mean():8.3f} | "
                  f"{g('sel','brain').mean():9.3f} {g('rand','brain').mean():9.3f} "
                  f"{d.mean():+6.3f}+-{d.std(ddof=1):.3f} | "
                  f"{g('sel','nf').mean():6.3f} {g('rand','nf').mean():6.3f} | "
                  f"{g('sel','xonly').mean():5.2f} {g('rand','xonly').mean():5.2f}")
