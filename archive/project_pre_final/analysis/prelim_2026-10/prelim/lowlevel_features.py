#!/usr/bin/env python3
"""EmoBrain 선행 점검 0-6: 라벨이 화면의 저수준 시각 특징과 얼마나 얽혀 있나 (2026-10-22).

1) 영상 2,196개에서 저수준 시각 특징 33개를 뽑는다 (MindCaptioning 왜곡 보정 검증 때와 같은 정의):
   밝기 평균·대비·채도, RGB 평균, 프레임 간 변화(움직임) 평균·변동, 경계 세기, 화면 3×4 칸별 밝기·움직임.
   초당 4장, 32×18 화소로 줄여 계산. ffmpeg 가 필요해서 node1 에서 실행한다. 이미 뽑은 영상은 건너뛴다.
2) 34개 감정·14개 척도를 이 특징으로 얼마나 설명하나 (5겹 교차검증 R²) + 대표 특징과의 순위 상관.
출력: /storage/bigdata/EmoBrain_response/prelim/lowlevel_video_features.tsv, label_lowlevel_*.tsv
사용: nice -n 19 python lowlevel_features.py [--workers 4]
"""
import argparse
import json
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent))
from label_structure import cv_r2, DIMS14, LAB, META  # noqa: E402

OUT = Path("/storage/bigdata/EmoBrain_response/prelim")
VIDEOS = Path("/storage/bigdata/Horikawa/CowenEmotionVideos")
NAMES = (["밝기", "대비", "채도", "R", "G", "B", "움직임_평균", "움직임_변동", "경계세기"]
         + [f"밝기_칸{i}" for i in range(12)] + [f"움직임_칸{i}" for i in range(12)])


def video_features(vid):
    cmd = ["ffmpeg", "-v", "error", "-i", str(VIDEOS / f"{vid:04d}.mp4"), "-vf", "fps=4,scale=32:18",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    try:
        raw = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=300).stdout
        F = np.frombuffer(raw, np.uint8).reshape(-1, 18, 32, 3).astype(np.float64) / 255.0
    except Exception as e:  # noqa: BLE001
        return vid, None, str(e)[:200]
    gray = F.mean(-1); mx, mn = F.max(-1), F.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.where(mx > 0, mx, 1), 0)
    diff = np.abs(np.diff(gray, axis=0)) if len(gray) > 1 else np.zeros((1,) + gray.shape)
    gy, gx = np.gradient(gray, axis=(1, 2))
    grid = lambda a: a.reshape(a.shape[0], 3, 6, 4, 8).mean((0, 2, 4)).ravel()
    f = np.concatenate([[gray.mean(), gray.std(axis=(1, 2)).mean(), sat.mean()], F.mean((0, 1, 2)),
                        [diff.mean(), diff.mean((1, 2)).std(), np.sqrt(gx ** 2 + gy ** 2).mean()], grid(gray), grid(diff)])
    return vid, f, ""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    fpath = OUT / "lowlevel_video_features.tsv"
    done = pd.read_csv(fpath, sep="\t", index_col=0) if fpath.exists() else pd.DataFrame(columns=NAMES)
    todo = [v for v in range(1, 2197) if v not in done.index]
    print(f"뽑을 영상 {len(todo)}개 (이미 {len(done)}개)", flush=True)
    rows, errs = {}, {}
    with Pool(a.workers) as pool:
        for k, (vid, f, err) in enumerate(pool.imap_unordered(video_features, todo, chunksize=4), 1):
            if f is None:
                errs[vid] = err
            else:
                rows[vid] = f
            if k % 200 == 0 or k == len(todo):
                new = pd.DataFrame.from_dict(rows, orient="index", columns=NAMES)
                pd.concat([done, new]).sort_index().to_csv(fpath, sep="\t", float_format="%.6g")
                print(f"  {k}/{len(todo)} 완료, 실패 {len(errs)}", flush=True)
    if errs:
        print("실패 영상:", errs)
    Fv = pd.read_csv(fpath, sep="\t", index_col=0)
    print(f"특징 {Fv.shape}, 빠진 영상 {2196 - len(Fv)}개", flush=True)

    # 0-6 라벨 × 저수준 특징
    names = [l.strip() for l in open(LAB / "cowen34_order.txt") if l.strip()]
    D = pd.read_csv(META); D.index = D.stimulus_num.str.replace("stimulus_", "").astype(int)
    Y = D[[f"score_{i}" for i in range(34)]].copy(); Y.columns = names
    C = pd.read_csv(LAB / "cowen_horikawa_labels.csv"); C.index = C.stim_num_int
    Z = C[[f"{d}_score" for d in DIMS14]].copy(); Z.columns = DIMS14
    T = pd.read_csv("/storage/bigdata/Horikawa/response_t1w/sub-01/v3/sub-01_samples.tsv", sep="\t")
    T = T[~T.exclude_duplicate.astype(bool)].drop_duplicates("video_id")
    vids = [v for v in T.video_id.values if v in Fv.index]
    X = Fv.loc[vids].values; dur = T.set_index("video_id").loc[vids, "duration_sec"].values.astype(float)
    L = pd.concat([Y.loc[vids].add_prefix("감정:"), Z.reindex(vids).add_prefix("척도:")], axis=1)
    rows = []
    for l in L.columns:
        y = L[l].values; ok = np.isfinite(y)
        r2 = cv_r2(X[ok], y[ok]); r2d = cv_r2(np.column_stack([X[ok], np.log(dur[ok])]), y[ok])
        top = {n: stats.spearmanr(Fv.loc[vids, n].values[ok], y[ok])[0] for n in ["밝기", "채도", "움직임_평균", "경계세기"]}
        rows.append(dict(라벨=l, 저수준특징_R2=r2, 저수준특징과길이_R2=r2d, **{f"r_{k}": v for k, v in top.items()}))
    tab = pd.DataFrame(rows).sort_values("저수준특징_R2", ascending=False)
    tab.to_csv(OUT / "label_lowlevel_r2.tsv", sep="\t", index=False, float_format="%.4f")
    summ = {"영상수": len(vids), "R2_중앙값": round(float(tab.저수준특징_R2.median()), 3),
            "R2_0.05넘는_라벨수": int((tab.저수준특징_R2 > 0.05).sum()),
            "R2_상위10": {r.라벨: round(r.저수준특징_R2, 3) for r in tab.head(10).itertuples()}}
    (OUT / "label_lowlevel_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    print(tab.round(3).head(20).to_string(index=False))
    print(f"저장: {OUT}")


if __name__ == "__main__":
    main()
