#!/usr/bin/env python3
"""S9 합성 자료 시험 (2026-11-13). 실제 정답과 실제 뇌 반응은 읽지 않는다. S2 표(roi_table, cabnp_groups)만 읽는다."""
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))  # 코드는 src에 있다
import os
import sys
import tempfile

os.environ["S9_OUT"] = tempfile.mkdtemp(prefix="s9_tests_")
os.environ.setdefault("OMP_NUM_THREADS", "4")  # login node를 다 쓰지 않는다
import numpy as np
import pandas as pd
import torch
torch.set_num_threads(4)

import s4_common as c
import s6_model as M
import s9_saved_models as s9

RESULTS = []


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print("통과" if ok else "실패", name, flush=True)


class FakeFD:
    """FoldData에서 S9가 쓰는 부분만. x는 참가자마다 ROI 순서로 이어 붙인 voxel 열이다."""

    def __init__(self, n_per, counts, seed=0):
        g = torch.Generator().manual_seed(seed)
        self.participants = ["sub-01", "sub-02"]
        self.voxel_counts = {p: list(counts) for p in self.participants}
        self.x = {p: torch.randn(n_per, sum(counts), generator=g) for p in self.participants}
        self.row_participant = np.repeat(np.arange(2), n_per)
        self.row_local = np.tile(np.arange(n_per), 2)
        self.row_video = np.concatenate([np.arange(1, n_per + 1), np.arange(1, n_per + 1)])
        self.row_role = np.full(2 * n_per, 2)
        self.device = "cpu"

    def rows(self, role):
        return np.flatnonzero(self.row_role == {"train": 0, "val": 1, "test": 2}[role])

    def participant_names(self, rows):
        return np.array(self.participants)[self.row_participant[rows]]

    def batch(self, rows):
        xs, positions = {}, {}
        for i, pid in enumerate(self.participants):
            at = np.flatnonzero(self.row_participant[rows] == i)
            if len(at):
                xs[pid] = self.x[pid][torch.as_tensor(self.row_local[rows[at]])]
                positions[pid] = torch.as_tensor(at)
        return M.BrainBatch(xs, positions, len(rows))


def small_model(n_roi=370, decoded=False, seed=0):
    torch.manual_seed(seed)
    counts = [2] * n_roi
    model = M.BrainModel({"sub-01": counts, "sub-02": counts}, 4, feature_head=decoded, decoded=decoded, rank=2 if decoded else None)
    return model.eval(), counts


def t_token_equals_input():
    model, counts = small_model()
    fd = FakeFD(10, counts)
    rows = fd.rows("test")
    part = fd.row_participant[rows]
    donors = s9.donor_table(fd, rows, 1)
    Tk = s9.tokens(model, fd, rows)
    ok = True
    for idx in (np.array([0]), np.array([5, 7, 300]), np.arange(370)):
        p0 = np.flatnonzero(part == 1)
        local = {g: i for i, g in enumerate(p0)}
        with torch.no_grad():
            direct = model(s9.raw_perturbed_batch(fd, rows[p0], np.array([local[g] for g in donors[3][p0]]), idx)).z.sigmoid()
        Tp = Tk[p0].clone()
        Tp[:, idx] = Tk[torch.as_tensor(donors[3][p0])][:, idx]
        ok &= torch.allclose(direct, s9.predict_from_tokens(model, Tp), atol=1e-5)
    check("ROI 입력을 다른 영상 값으로 바꾼 것과 그 ROI token을 바꾼 것이 같다(선형 입력층)", ok)
    m2 = M.BrainModel({"sub-01": counts, "sub-02": counts}, 4, tokenizer="brainit")
    try:
        s9.tokens(m2.eval(), fd, rows)
        check("Brain-IT 입력층에서는 token 교체를 막는다", False)
    except ValueError:
        check("Brain-IT 입력층에서는 token 교체를 막는다", True)


def t_donors():
    fd = FakeFD(7, [2] * 5)
    rows = fd.rows("test")
    a, b = s9.donor_table(fd, rows, 3), s9.donor_table(fd, rows, 3)
    part = fd.row_participant[rows]
    check("다른 영상 배정은 같은 참가자의 다른 시험 행이다", (part[a] == part[None]).all() and (a != np.arange(len(rows))[None]).all())
    check("배정표는 fold로 정한 seed로 다시 만들면 같다", (a == b).all() and a.shape == (s9.PERTURB_REPEATS, len(rows)))
    check("fold가 다르면 배정표가 다르다", not (a == s9.donor_table(fd, rows, 4)).all())


def t_units():
    u = s9.units_table()
    roi = pd.read_csv(c.S2 / "roi_table.tsv", sep="\t")
    check("교란 단위는 13묶음과 ROI 370개다", sum(x[0] == "group" for x in u) == 13 and sum(x[0] == "roi" for x in u) == len(roi) == 370)


def t_perturb_sums():
    m1, counts = small_model(seed=1)
    m2, _ = small_model(decoded=True, seed=2)
    fd = FakeFD(9, counts, seed=5)
    g = np.random.default_rng(0)
    y_by_video = {v: g.random(34) for v in range(1, 10)}
    s9.test_ratings = lambda split, vids: np.array([y_by_video[int(v)] for v in vids])
    arr = s9.perturb_fold({"brain_only": m1, "brain_decoded": m2}, fd, None, 2, repeats=8)
    rows = fd.rows("test")
    Y = np.array([y_by_video[int(v)] for v in fd.row_video[rows]])
    part = fd.row_participant[rows]
    base = s9.predict_from_tokens(m2, s9.tokens(m2, fd, rows)).double().numpy()
    r = s9.pooled_r(arr["brain_decoded_base"], arr["sum_y"], arr["sum_yy"], arr["n"])
    direct = np.array([[np.corrcoef(base[part == p, e], Y[part == p, e])[0, 1] for e in range(34)] for p in range(2)])
    check("합으로 낸 원래 r이 직접 계산한 r과 같다", np.allclose(r, direct, atol=1e-8))
    u, t = 20, 7  # 13묶음 뒤의 ROI 하나
    Tk = s9.tokens(m2, fd, rows)
    idx = s9.units_table()[u][2]
    Tk[:, idx] = Tk[torch.as_tensor(arr["donors"][t])][:, idx]
    pert = s9.predict_from_tokens(m2, Tk).double().numpy()
    rp = s9.pooled_r(arr["brain_decoded_perturbed"][u, t], arr["sum_y"], arr["sum_yy"], arr["n"])
    dp = np.array([[np.corrcoef(pert[part == p, e], Y[part == p, e])[0, 1] for e in range(34)] for p in range(2)])
    check("합으로 낸 교란 r이 직접 계산한 r과 같다", np.allclose(rp, dp, atol=1e-8))
    check("두 모델이 같은 배정표를 쓴다(하나만 저장)", arr["donors"].shape == (8, len(rows)) and arr["brain_only_perturbed"].shape[1] == 8)


def t_swap():
    model, counts = small_model(n_roi=6, decoded=True, seed=3)
    fd = FakeFD(8, counts, seed=7)
    g = np.random.default_rng(1)
    y_by_video = {v: g.random(34) for v in range(1, 10)}
    s9.test_ratings = lambda split, vids: np.array([y_by_video[int(v)] for v in vids])
    fd.row_video = fd.row_video.copy()
    fd.row_video[fd.row_participant == 1] = np.array([1, 2, 3, 4, 5, 6, 7, 9])  # sub-02에는 영상 8이 없고 9가 있다
    pairs = pd.DataFrame(dict(fold=[3] * 4 + [4], video_a=[1, 2, 8, 5, 1], video_b=[2, 3, 1, 6, 3]))
    res, log = s9.swap_fold(model, fd, None, 3, 0, "x", pairs)
    l = pd.DataFrame(log).set_index("participant")
    check("바꿔 끼우기: 그 fold의 짝만 쓰고, 영상이 없는 짝은 빼고 수를 남긴다", l.loc["sub-01", "n_pairs"] == 4 and l.loc["sub-02", "n_pairs"] == 3 and l.loc["sub-02", "n_pairs_missing"] == 1)
    r = res["sub-01"]
    H = model.encode(fd.batch(fd.rows("test")[:8]))
    o = model.readout(H)
    z_vis = model.readout.combine(o.g[[0]], o.v_hat[[1]], o.c_hat[[0]])  # 짝 (1 → 2): 시각만 B
    check("바꿔 끼우기: 시각만 교체는 g(H_A)와 A의 캡션, B의 시각으로 계산한다", torch.allclose(r.z[0, 1, 0], z_vis[0], atol=1e-5))
    check("바꿔 끼우기: 대조 seed는 참가자와 fold로 정한다", r.control_seed == s9.fixed_seed("swap", "sub-01", 3, 0))
    model2, _ = small_model(n_roi=6, decoded=False)
    try:
        s9.swap_fold(model2, fd, None, 3, 0, "x", pairs)
        check("decoded features가 없는 모델에서는 바꿔 끼우기를 막는다", False)
    except ValueError:
        check("decoded features가 없는 모델에서는 바꿔 끼우기를 막는다", True)


def main():
    for f in (t_token_equals_input, t_donors, t_units, t_perturb_sums, t_swap):
        f()
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
