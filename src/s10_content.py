#!/usr/bin/env python3
"""S10 정서마다 뇌 decoder가 기대는 장면 내용 (11/17 석진 님 요청: "성능 말고, 어떤 정보인지 보여 달라. ex) awe는 mountain, sky, surprise는 clown, blood"). GPU 없음.

저장된 시험 예측만 읽는다(다시 학습하지 않음). 탐색, 기술 분석이고 판정은 없다.
- 뇌 예측: S6 최종(A-1, seed 0)의 시험 예측. 영상마다 그 영상을 시험으로 본 참가자들의 예측을 평균한다(6 fold를 모으면 개발 영상마다 한 번씩 시험).
  네트워크마다: 6-4a의 그 네트워크만으로 학습한 A-1(s6_brain_net_<묶음>)의 시험 예측을 같은 방식으로 평균한다.
- 사람 평정: 같은 영상의 규범 평정. 정서는 27개판(Cowen & Keltner의 7개 제외, 01 0절, 11/17)이다.
- 장면 내용 두 가지
  1. 캡션 단어: 영상마다 사람이 쓴 캡션 20개(caption_ck20.csv) 가운데 그 단어가 나온 캡션의 비율. 소문자, 알파벳 단어, 영어 불용어와 정서어 181개(s3_text.affect_words, 정서어 제거판 Caption feature와 같은 목록)를 뺀다.
     개발 영상 가운데 30개 이상에 나온 단어만 쓴다.
  2. 이름표 73개(Horikawa 외 2020 공개 semantic features, s10_beyond_scene.SEMANTIC).
- 연결의 크기: 영상들에 걸친 Spearman 순위 상관. 정서마다 (가) 뇌 예측과 내용, (나) 사람 평정과 내용, (다) 사람 평정을 통제한 뇌 예측과 내용(순위 잔차끼리의 상관)을 낸다.
  (다)는 "평정과 상관없이 뇌 decoder가 그 내용에 끌리는 정도"다. 검정과 보정은 하지 않는다(기술).
출력(--out): words.tsv(정서 × 단어의 (가), (나), (다)), labels.tsv(정서 × 이름표의 (가), (나)), top_words.tsv(정서마다 위 10개),
  network_top_words.tsv(네트워크마다, 정서마다 위 10개), vocab.tsv, run_info.json
사용: s10_content.py --s6-dir <s6_brain_final> --net-root <final_2026-11 폴더(s6_brain_net_* 위)> --out <폴더> --design-freeze <커밋>
"""
import argparse
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

import s3_common as c3
import s3_text as T3
import s4_common as c
import s10_beyond_scene as BS
import s10_performance as PF

CK7 = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")
NETS = ("Visual1", "Visual2", "Dorsal-Attention", "Posterior-Multimodal", "Somatomotor", "Auditory", "Cingulo-Opercular", "Frontoparietal", "Default",
        "Language", "Ventral-Multimodal", "Orbito-Affective", "Subcortex")
MIN_VIDEOS = 30
TOP = 10


def video_mean_predictions(s6_dir, split, n_emotions, cond="brain_only", seed=0):
    found = PF.find_predictions(s6_dir)
    f = found[(found.condition == cond) & (found.seed == seed) & (found.status == "ok")]
    if sorted(f.fold.tolist()) != list(range(1, PF.N_FOLDS + 1)):
        raise SystemExit(f"{s6_dir}: {cond} seed {seed}의 6 fold 예측이 없다")
    plan_rows = {k: PF.plan_test_rows(s6_dir, k) for k in range(1, PF.N_FOLDS + 1)}
    data = PF.load_condition(dict(zip(f.fold.astype(int), f.path)), split, plan_rows, n_emotions)
    frames = [pd.DataFrame(p, index=v) for v, p in data.values()]
    return pd.concat(frames).groupby(level=0).mean()


def rank(a):
    return pd.DataFrame(a).rank().to_numpy()


def corr_cols(X, Y):
    """X: 영상 × p, Y: 영상 × q의 순위끼리 Pearson(= Spearman). 돌려주는 값: p × q."""
    Xr, Yr = rank(X), rank(Y)
    Xr = (Xr - Xr.mean(0)) / Xr.std(0)
    Yr = (Yr - Yr.mean(0)) / Yr.std(0)
    return Xr.T @ Yr / len(Xr)


def partial_rank_corr(P, R, Y):
    """사람 평정 R의 순위를 통제한 뇌 예측 P와 내용 Y의 순위 상관(정서마다 따로). P, R: 영상 × 정서, Y: 영상 × 내용."""
    Pr, Rr, Yr = rank(P), rank(R), rank(Y)
    out = np.empty((P.shape[1], Y.shape[1]))
    Yz = (Yr - Yr.mean(0)) / Yr.std(0)
    for e in range(P.shape[1]):
        A = np.column_stack([np.ones(len(Rr)), Rr[:, e]])
        res = Pr[:, e] - A @ np.linalg.lstsq(A, Pr[:, e], rcond=None)[0]
        resY = Yz - A @ np.linalg.lstsq(A, Yz, rcond=None)[0]
        res = (res - res.mean()) / res.std()
        resY = (resY - resY.mean(0)) / resY.std(0)
        out[e] = res @ resY / len(res)
    return out


def caption_words(video_ids):
    cap = pd.read_csv(c3.CAPTIONS, encoding="utf-8-sig")
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    stop = set(ENGLISH_STOP_WORDS)
    affect = {w.lower() for w in T3.affect_words()}
    tok = lambda s: set(re.findall(r"[a-z]+", str(s).lower()))
    per_video = {}
    for v, g in cap.groupby("video_id"):
        sets = [tok(s) for s in g.description]
        words = set().union(*sets) - stop - affect
        per_video[int(v)] = {w: sum(w in s for s in sets) / len(sets) for w in words if len(w) > 2}
    vocab_count = pd.Series([w for v in video_ids for w in per_video.get(int(v), {})]).value_counts()
    vocab = sorted(vocab_count[vocab_count >= MIN_VIDEOS].index)
    M = np.zeros((len(video_ids), len(vocab)))
    col = {w: i for i, w in enumerate(vocab)}
    for i, v in enumerate(video_ids):
        for w, x in per_video.get(int(v), {}).items():
            if w in col:
                M[i, col[w]] = x
    return M, vocab, vocab_count.loc[vocab]


def long(mat, rows, cols, rname, cname):
    return pd.DataFrame(mat, index=rows, columns=cols).stack().rename("rho").reset_index().rename(columns={"level_0": rname, "level_1": cname})


def run(s6_dir, net_root, out):
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    emotions = pd.read_csv(c.LABEL_MAP, sep="\t").set_index("score_col").loc[cols, "name"].tolist()
    keep = [i for i, e in enumerate(emotions) if e not in CK7]
    names = [emotions[i] for i in keep]
    P = video_mean_predictions(s6_dir, split, len(emotions))
    vids = P.index.to_numpy()
    pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    R = np.asarray(y, np.float64)[[pos[v] for v in vids]][:, keep]
    Pm = P.to_numpy()[:, keep]
    W, vocab, counts = caption_words(vids)
    sem = pd.read_csv(BS.SEMANTIC)
    ids = sem.iloc[:, 0].str.replace("stimulus_", "").astype(int).to_numpy()
    L = sem.set_index(ids).iloc[:, 1:].loc[vids]
    lab_names = [str(x) for x in L.columns]
    L = L.to_numpy(np.float64)
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    wb, wr, wp = corr_cols(Pm, W), corr_cols(R, W), partial_rank_corr(Pm, R, W)
    lb, lr = corr_cols(Pm, L), corr_cols(R, L)
    long(wb, names, vocab, "emotion", "word").assign(rho_rating=long(wr, names, vocab, "emotion", "word").rho, rho_brain_given_rating=long(wp, names, vocab, "emotion", "word").rho).to_csv(o / "words.tsv", sep="\t", index=False)
    long(lb, names, lab_names, "emotion", "label").assign(rho_rating=long(lr, names, lab_names, "emotion", "label").rho).to_csv(o / "labels.tsv", sep="\t", index=False)
    top = []
    for e, name in enumerate(names):
        for kind, mat, voc in (("brain", wb, vocab), ("rating", wr, vocab), ("brain_given_rating", wp, vocab), ("label_brain", lb, lab_names)):
            idx = np.argsort(-mat[e])[:TOP]
            top.append(dict(emotion=name, kind=kind, top=", ".join(f"{voc[i]}({mat[e, i]:.2f})" for i in idx)))
    pd.DataFrame(top).to_csv(o / "top_words.tsv", sep="\t", index=False)
    net_rows = []
    for n in NETS:
        d = Path(net_root) / f"s6_brain_net_{n}"
        Pn = video_mean_predictions(d, split, len(emotions)).loc[vids].to_numpy()[:, keep]
        wn = corr_cols(Pn, W)
        for e, name in enumerate(names):
            idx = np.argsort(-wn[e])[:TOP]
            net_rows.append(dict(network=n, emotion=name, top=", ".join(f"{vocab[i]}({wn[e, i]:.2f})" for i in idx),
                                 match_whole_brain=float(np.corrcoef(wn[e], wb[e])[0, 1])))
    pd.DataFrame(net_rows).to_csv(o / "network_top_words.tsv", sep="\t", index=False)
    pd.DataFrame(dict(word=vocab, n_videos=counts.to_numpy())).to_csv(o / "vocab.tsv", sep="\t", index=False)
    return dict(n_videos=len(vids), n_words=len(vocab), n_labels=len(lab_names), emotions=names, min_videos=MIN_VIDEOS)


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 정서마다 뇌 decoder가 기대는 장면 내용")
    ap.add_argument("--s6-dir", required=True)
    ap.add_argument("--net-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", required=True)
    a = ap.parse_args(argv)
    c.guard(a.design_freeze)
    t0 = time.time()
    info = run(a.s6_dir, a.net_root, a.out)
    info.update(stage="S10 장면 내용", s6_dir=str(a.s6_dir), net_root=str(a.net_root), design_freeze=a.design_freeze, code_commit=c.START_HEAD,
                code_dirty=c.START_DIRTY, elapsed_seconds=round(time.time() - t0, 1))
    (Path(a.out) / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"끝: {info['elapsed_seconds']}초, 영상 {info['n_videos']}, 단어 {info['n_words']}", flush=True)


if __name__ == "__main__":
    main()
