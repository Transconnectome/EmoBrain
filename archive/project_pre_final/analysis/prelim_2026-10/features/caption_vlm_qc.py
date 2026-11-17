#!/usr/bin/env python3
"""VLM 생성 캡션 점검 (2026-10-29).

대상: EmoViS 에서 만든 captions.json (Qwen2.5-VL-7B-Instruct, 영상당 정지 프레임 3장 = 25·50·75% 지점,
프롬프트 "Describe the setting, objects, people, actions, and events visible in this video. Do not name any emotions.").
키는 stim_idx (0 부터) 라서 영상 번호 = 키 + 1. 사람 캡션(caption_ck20.csv, 영상당 20개)은 점검 기준으로만 쓰고 특징 값은 바꾸지 않는다.

score  : 영상 1~2185 마다 두 가지를 잰다.
  검색 순위   : VLM 캡션 임베딩과 2185개 영상의 사람 캡션 평균 임베딩의 cosine 중 같은 영상의 순위 (1 = 가장 비슷).
  단어 대조   : 사람 캡션 절반 이상이 쓴 단어를 VLM 이 빠뜨렸는지 (missed), VLM 이 첫 문장이나 두 번 이상 쓴 단어를
                사람 20명이 아무도 쓰지 않았는지 (unsupported). 같은 어간이거나 단어 임베딩 cosine 0.70 이상이면 같은 말로 본다.
                사람을 가리키는 말은 한 묶음으로 본다. 색·크기·위치·흔한 동사는 뺀다.
  출력: <out>/caption_vlm_qc.tsv, <out>/summary.json
sheets : 확인 목록 영상마다 VLM 이 본 3장 + 10·90% 지점 2장을 한 줄로 붙인 그림. <out>/sheets/sheet_XX.png (그림 한 장에 영상 3개)
사용: python caption_vlm_qc.py score|sheets --captions <captions.json> --bundle <자극 묶음> --feat <특징 폴더> --videos <mp4 폴더> --out <출력>
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import build_lab_features as blf  # noqa: E402
from build_caption_variants import STOP  # noqa: E402

N = 2185
TAU = 0.70
MAJORITY = 0.5
VLM_POS = [0.25, 0.50, 0.75]
SHEET_POS = [0.10, 0.25, 0.50, 0.75, 0.90]
PEOPLE = set("man men woman women person people guy guys lady ladies girl girls boy boys child children kid kids baby babies "
             "infant toddler individual individuals someone adult adults teenager teen gentleman male female couple crowd".split())
GENERIC = set(
    "video scene shows showing shown show visible background foreground appears appear appearing image clip frame view seen see "
    "stand stands standing stood sit sits sitting wear wears wearing wore look looks looking hold holds holding held "
    "can could would will may might one two three four several some another other each both all just being has have had "
    "does doing make makes making take takes taking while near around front behind side left right top bottom next through "
    "toward towards across along about after before during again back away together also only still "
    "small large big little huge tiny long short tall white black red blue green yellow brown gray grey dark light bright "
    "orange pink purple colorful various different another area part setting moment time first then place located "
    "seems seem appears likely possibly perhaps something thing things way lot lots how between having tries trying "
    "depicts depicting depicted features featuring suggesting suggests engaged sequence frames environment close closeup "
    "similar captured capturing setting overall atmosphere entire various visible display displayed displaying".split())
DET = set("a an the two three four five several some his her their its this that another one many few".split())
SEX = re.compile(r"\b(penis\w*|vagina\w*|breasts?|sex|sexual\w*|naked|nude|masturbat\w*|genital\w*|porn\w*|intercourse|erect\w*)\b", re.I)
SOFT = re.compile(r"\b(intimate\w*|romantic\w*|affection\w*|embrac\w*|sensual\w*|passionate\w*)\b", re.I)
N_AUDIT = 24
FFMPEG = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg"  # 시스템 ffmpeg 에는 h264 디코더가 없다
FFPROBE = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffprobe"
SEED = 20261029


def stem(w):
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    for suf in ("ing", "ed"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[:-len(suf)]
            if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "aeiouls":
                w = w[:-1]
            break
    return w


def words(text):
    """(어간, 원형) 목록. 사람 말은 'person' 하나로."""
    out = []
    for w in re.findall(r"[a-z]+", text.lower()):
        if len(w) <= 2 or w in STOP or w in GENERIC:
            continue
        out.append(("person", "person") if w in PEOPLE else (stem(w), w))
    return out


def noun_ratio(texts):
    """어간마다 바로 앞 단어가 관사·수사·소유격인 비율. 품사 분석기 대신 쓰는 명사 근사 (gun 높음, falls·kissing 낮음)."""
    det, tot = {}, {}
    for t in texts:
        toks = re.findall(r"[a-z]+", t.lower())
        for i, w in enumerate(toks):
            if len(w) <= 2 or w in STOP or w in GENERIC:
                continue
            s = "person" if w in PEOPLE else stem(w)
            tot[s] = tot.get(s, 0) + 1
            det[s] = det.get(s, 0) + (i > 0 and toks[i - 1] in DET)
    return {s: det[s] / tot[s] for s in tot}


def read_captions(path, full=True):
    """v1 captions.json 은 키가 stim_idx (0 부터), build_caption_vlm_video.py 출력은 키가 영상 번호 (1 부터)."""
    vlm = json.loads(path.read_text())
    base = 0 if "0" in vlm else 1
    vlm = {int(k) + 1 - base: v for k, v in vlm.items()}
    if full:
        assert sorted(vlm) == list(range(1, N + 1)), f"{path} 가 영상 1~2185 를 다 덮지 않음"
    return vlm


def load(a, full=True):
    vlm = read_captions(a.captions, full)
    cap = pd.read_csv(a.bundle / "captions/caption_ck20.csv", encoding="utf-8-sig")
    cap = cap[cap.video_id <= N]
    human = {v: g.description.fillna("").astype(str).tolist() for v, g in cap.groupby("video_id")}
    assert sorted(human) == list(range(1, N + 1))
    return vlm, human


def retrieval_rank(feat, name_vlm="caption_vlm_mpnet"):
    def get(name):
        ids = pd.read_csv(feat / f"{name}_video_id.tsv", sep="\t").video_id.values
        X = np.load(feat / f"{name}.npy").astype(np.float64)
        X = pd.DataFrame(X, index=ids).loc[range(1, N + 1)].values
        return X / np.linalg.norm(X, axis=1, keepdims=True)
    V, H = get(name_vlm), get("caption_human_mpnet")
    S = V @ H.T
    d = np.diag(S)
    return 1 + (S > d[:, None]).sum(1), d


def score(a):
    vlm, human = load(a)
    rank, cos_true = retrieval_rank(a.feat, a.feature)
    surf = {}
    for t in list(vlm.values()) + [c for cs in human.values() for c in cs]:
        for s, w in words(t):
            surf.setdefault(s, {}).setdefault(w, 0); surf[s][w] += 1
    rep = {s: max(ws, key=ws.get) for s, ws in surf.items()}
    noun = noun_ratio(list(vlm.values()) + [c for cs in human.values() for c in cs])
    is_obj = lambda s: s != "person" and noun.get(s, 0) >= 0.4
    vid_df = {}
    for cs in human.values():
        for s in {s for c in cs for s, _ in words(c)}:
            vid_df[s] = vid_df.get(s, 0) + 1
    vocab = sorted(rep)
    E = dict(zip(vocab, blf.Encoder(a.device)([rep[s] for s in vocab])))

    def matched(s, pool):
        if s in pool:
            return True
        P = np.array([E[p] for p in pool]) if pool else np.zeros((0, 768))
        return len(P) > 0 and float((P @ E[s]).max()) >= TAU

    rows = []
    for v in range(1, N + 1):
        caps = human[v]; nh = len(caps)
        share = {}
        for c in caps:
            for s in {s for s, _ in words(c)}:
                share[s] = share.get(s, 0) + 1 / nh
        vw = words(vlm[v]); vset = {s for s, _ in vw}
        first = {s for s, _ in words(re.split(r"(?<=[.!?])\s", vlm[v].strip(), maxsplit=1)[0])}
        cnt = pd.Series([s for s, _ in vw]).value_counts() if vw else pd.Series(dtype=int)
        salient = first | set(cnt[cnt >= 2].index)
        consensus = {s: sh for s, sh in share.items() if sh >= MAJORITY}
        missed = {s: sh for s, sh in consensus.items() if not matched(s, vset)}
        unsup = sorted(s for s in salient if s not in share and not matched(s, set(share)))
        miss_obj = {s: sh for s, sh in missed.items() if is_obj(s)}
        miss_act = {s: sh for s, sh in missed.items() if not is_obj(s) and s != "person"}
        unsup_obj = [s for s in unsup if is_obj(s) and vid_df.get(s, 0) >= 10]
        n_sex = sum(bool(SEX.search(c)) for c in caps)
        fmt = lambda d: ", ".join(f"{rep[s]}:{sh:.2f}" for s, sh in sorted(d.items(), key=lambda x: -x[1]))
        rows.append(dict(video_id=v, retrieval_rank=int(rank[v - 1]), cos_vlm_human=round(float(cos_true[v - 1]), 4),
                         flag_gross=bool(rank[v - 1] > 500),
                         flag_substitution=bool(miss_obj and max(miss_obj.values()) >= 0.6 and unsup_obj),
                         flag_sexual_softened=bool(n_sex >= nh / 2 and not SEX.search(vlm[v])),
                         vlm_soft_word=bool(SOFT.search(vlm[v])),
                         n_consensus=len(consensus), n_missed=len(missed),
                         max_missed_share=round(max(missed.values()), 2) if missed else 0.0,
                         missed_objects=fmt(miss_obj), missed_actions=fmt(miss_act), unsupported_objects=", ".join(rep[s] for s in unsup_obj),
                         missed=fmt(missed), consensus=fmt(consensus),
                         n_unsupported=len(unsup), unsupported=", ".join(rep[s] for s in unsup),
                         vlm_first_sentence=re.split(r"(?<=[.!?])\s", vlm[v].strip(), maxsplit=1)[0][:200],
                         human_example=caps[0][:200]))
    df = pd.DataFrame(rows)
    rng = np.random.default_rng(SEED)
    df["audit_random"] = df.video_id.isin(rng.choice(df.video_id.values, N_AUDIT, replace=False))
    a.out.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out / "caption_vlm_qc.tsv", sep="\t", index=False)
    sub = df[df.flag_substitution].sort_values("max_missed_share", ascending=False)
    review = dict(gross=df[df.flag_gross].video_id.tolist(), substitution_top=sub.video_id.head(12).tolist(),
                  audit_random=df[df.audit_random].video_id.tolist())
    (a.out / "review_list.json").write_text(json.dumps(review, indent=1))
    summ = dict(n_videos=N, tau=TAU, majority=MAJORITY,
                n_flag_gross=int(df.flag_gross.sum()), n_flag_substitution=int(df.flag_substitution.sum()),
                n_sexual_majority=int(sum(sum(bool(SEX.search(c)) for c in human[v]) >= len(human[v]) / 2 for v in human)),
                n_flag_sexual_softened=int(df.flag_sexual_softened.sum()),
                n_sexual_softened_with_soft_word=int((df.flag_sexual_softened & df.vlm_soft_word).sum()),
                n_missed_action_ge07=int(df.missed_actions.str.contains(r":(?:0\.[7-9]|1\.0)").sum()),
                rank1=float((df.retrieval_rank == 1).mean()), rank_median=float(df.retrieval_rank.median()),
                rank_le50=float((df.retrieval_rank <= 50).mean()),
                n_rank_gt_k={k: int((df.retrieval_rank > k).sum()) for k in [10, 50, 100, 200, 500]},
                n_missed_share_ge={t: int((df.max_missed_share >= t).sum()) for t in [0.5, 0.6, 0.7, 0.8, 0.9]},
                n_any_unsupported=int((df.n_unsupported > 0).sum()),
                consensus_words_per_video=float(df.n_consensus.mean()))
    (a.out / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


def grab(path, frac, dur, out):
    subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-ss", f"{frac * dur:.3f}", "-i", str(path),
                    "-frames:v", "1", "-vf", "scale=320:-2", str(out)], check=True)


def sheets(a):
    from PIL import Image, ImageDraw
    vlm, human = load(a, full=False)
    ref = read_captions(a.compare, full=False) if a.compare else None
    ids = [int(x) for x in a.ids.split(",")]
    tmp = a.out / "sheets" / "frames"; tmp.mkdir(parents=True, exist_ok=True)
    rows = []
    for v in ids:
        p = a.videos / f"{v:04d}.mp4"
        dur = float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                   capture_output=True, text=True, check=True).stdout)
        ims = []
        for f in SHEET_POS:
            fp = tmp / f"{v:04d}_{int(f * 100):02d}.png"
            if not fp.exists():
                grab(p, min(f, 0.98), dur, fp)
            ims.append(Image.open(fp).convert("RGB"))
        h = max(im.height for im in ims); W = sum(im.width for im in ims) + 4 * len(ims)
        row = Image.new("RGB", (W, h + (88 if ref else 70)), "white"); x = 0
        for f, im in zip(SHEET_POS, ims):
            row.paste(im, (x, 0)); ImageDraw.Draw(row).rectangle([x, 0, x + im.width - 1, h - 1],
                                                                outline="red" if f in VLM_POS else "gray", width=3)
            x += im.width + 4
        d = ImageDraw.Draw(row)
        d.text((4, h + 4), f"video {v}  (red = the 3 frames the v1 VLM saw)", fill="black")
        d.text((4, h + 22), "VLM: " + vlm[v][:150], fill="darkred")
        d.text((4, h + 40), "Human: " + human[v][0][:150], fill="darkblue")
        if ref:
            d.text((4, h + 58), "VLM v1: " + ref[v][:150], fill="gray")
        rows.append(row)
    for i in range(0, len(rows), 3):
        grp = rows[i:i + 3]; W = max(r.width for r in grp)
        sheet = Image.new("RGB", (W, sum(r.height + 10 for r in grp)), "white"); y = 0
        for r in grp:
            sheet.paste(r, (0, y)); y += r.height + 10
        sheet.save(a.out / "sheets" / f"sheet_{i // 3 + 1:02d}.png")
    print(f"그림 {(len(rows) + 2) // 3}장, 영상 {len(rows)}개")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score", "sheets"])
    ap.add_argument("--captions", type=Path, required=True); ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--feat", type=Path); ap.add_argument("--videos", type=Path); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ids", help="sheets: 쉼표로 구분한 영상 번호"); ap.add_argument("--device", default="cpu")
    ap.add_argument("--feature", default="caption_vlm_mpnet", help="score: 검색 순위에 쓸 VLM 캡션 임베딩 이름")
    ap.add_argument("--compare", type=Path, help="sheets: 함께 보일 기준 캡션 (예: v1 captions.json)")
    a = ap.parse_args()
    score(a) if a.cmd == "score" else sheets(a)


if __name__ == "__main__":
    main()
