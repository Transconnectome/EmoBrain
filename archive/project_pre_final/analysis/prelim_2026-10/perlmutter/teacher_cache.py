#!/usr/bin/env python3
"""teacher 의 교차검증 밖 예측을 피험자별로 한 번 계산해 저장한다 (soft BCE·MLP student 공용, 2026-10-28).

teacher = 내용 (V-JEPA 2 + 사람 캡션 임베딩) → 정서 ridge (linear_distill.teacher_oof 와 같다).
저장 (07_students/cache/sub-XX.npz)
  B, fold, Y34, Y14, vids, names, dims14 : 피험자 자료 (run_stage1.load_subject 와 같은 행)
  T_<공간>_f<f>       : 바깥 fold f 의 학습 행 (공간 mask 적용) 에 대한 teacher 예측. 학습 행 순서.
  T_<공간>_f<f>_h<h>  : 그 학습 행 중 안쪽 묶음 h 를 뺀 행에 대한 teacher 예측 (h 를 보지 않은 teacher). 같은 순서.
사용: python teacher_cache.py --sub 01
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import linear_distill as ld  # noqa: E402

rs, bb = ld.rs, ld.bb
CACHE = rs.OUT / "07_students/cache"


def build(sub):
    t0 = time.time(); CACHE.mkdir(parents=True, exist_ok=True)
    rows, fold, FB, Y34, names, Y14, meta = rs.load_subject(sub)
    vids = rows.video_id.values; B = FB["brain_roi469"]
    F = rs.load_features(); C = np.hstack([F[n].loc[vids].values for n in ld.TEACHER])
    obs14 = np.isfinite(Y14).all(1)
    arrs = dict(B=B.astype(np.float32), fold=fold, Y34=Y34, Y14=Y14, vids=vids, names=np.array(names), dims14=np.array(bb.DIMS14))
    for f in np.unique(fold):
        for space, Y, mask in [("A34", Y34, np.ones(len(fold), bool)), ("A14", Y14, obs14)]:
            trm = (fold != f) & mask; g = fold[trm]; Ytr = Y[trm]; Ctr = C[trm]
            arrs[f"T_{space}_f{f}"] = ld.teacher_oof(Ctr, Ytr, g)
            for h in np.unique(g):
                a = g != h
                arrs[f"T_{space}_f{f}_h{h}"] = ld.teacher_oof(Ctr[a], Ytr[a], g[a])
        print(f"  sub-{sub} fold {f} ({time.time() - t0:.0f}초)", flush=True)
    np.savez(CACHE / f"sub-{sub}.npz", **arrs)
    print(f"sub-{sub} teacher cache 완료 ({time.time() - t0:.0f}초)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sub", required=True)
    build(ap.parse_args().sub)
