#!/usr/bin/env python3
"""S3 캡션을 내용 수준으로 나눈 Caption feature(11/18 석진 님 "그 다음 거 진행"; 06 14절 4번, 01 1-1 내용의 수준). 세 단계, 세 환경.

수준(06 3절, scene graph의 objects, attributes, relationships를 품사로 근사)
- objects(물체): 명사(NOUN)와 고유명사(PROPN)만 원래 순서로 남긴 캡션. ex) "An old man slips on the icy road" → "man road"
- objattr(물체 + 속성): 위에 형용사(ADJ)와 수사(NUM)를 더한 캡션. ex) → "old man icy road"
- 전체(관계 포함)는 기존 Caption feature 정서어 제거판(deberta_no_emotion_words/target)을 그대로 쓴다. 동사, 전치사 같은 관계 단어가 들어 있다.
- 세 판 모두 정서어 181개(s3_text.affect_words, 정서어 제거판과 같은 목록)를 뺀다. 품사 분석은 원래 캡션에서 하고, 고른 단어에서 정서어를 지운다.
- 한계: 품사 근사라 scene graph parser(Schuster 외 2015)와 같지 않다. 문장 임베딩은 단어 순서에 둔감하다(Doerig 외 2025)는 한계가 같이 있다(01 1-3, 06 6절).
단계
1. export (EmoBrain CPU 환경): 캡션 표(caption_ck20.csv)와 정서어 목록을 <out>/captions.tsv, affect_words.txt로 쓴다.
2. parse (spaCy 환경 /pscratch의 nlp_spacy, spacy 3.7.5, en_core_web_sm 3.7.1): <out>/caption_levels.tsv(video_id, 원문, objects, objattr)
3. embed (GPU 환경): DeBERTa-large, 특수 token을 뺀 token 평균, 층 6/12/18/24를 이어 붙인 4,096차원(s3_text와 같은 정의), 영상마다 캡션 평균.
   빈 문자열(그 수준의 단어가 없는 캡션)은 평균에서 빼고 수를 기록한다. 영상의 캡션이 모두 비면 0 벡터로 두고 기록한다.
   출력: <s3_features>/deberta_objects/target.npy, deberta_objattr/target.npy(2196 × 4096, video_id 1~2196 순서), manifest.json
사용: s3_caption_levels.py export|parse|embed --out <작업 폴더> [--device cuda]
"""
import argparse
import json
import sys
import time
from pathlib import Path

LEVELS = ("objects", "objattr")
KEEP = {"objects": {"NOUN", "PROPN"}, "objattr": {"NOUN", "PROPN", "ADJ", "NUM"}}
LAYERS = (6, 12, 18, 24)


def export(out):
    import pandas as pd
    import s3_common as c3
    import s3_text as T3
    cap = pd.read_csv(c3.CAPTIONS, encoding="utf-8-sig")
    cap[["video_id", "description"]].to_csv(out / "captions.tsv", sep="\t", index=False)
    (out / "affect_words.txt").write_text("\n".join(sorted({w.lower() for w in T3.affect_words()})))
    print(f"캡션 {len(cap)}개, 영상 {cap.video_id.nunique()}개", flush=True)


def parse(out):
    import pandas as pd
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    affect = set((out / "affect_words.txt").read_text().split())
    cap = pd.read_csv(out / "captions.tsv", sep="\t")
    rows = {lv: [] for lv in LEVELS}
    for doc in nlp.pipe(cap.description.astype(str).tolist(), batch_size=512):
        for lv in LEVELS:
            rows[lv].append(" ".join(t.text.lower() for t in doc if t.pos_ in KEEP[lv] and t.text.lower() not in affect and t.text.isalpha()))
    for lv in LEVELS:
        cap[lv] = rows[lv]
    cap.to_csv(out / "caption_levels.tsv", sep="\t", index=False)
    info = dict(spacy=spacy.__version__, model="en_core_web_sm", n_captions=len(cap), **{f"empty_{lv}": int((cap[lv] == "").sum()) for lv in LEVELS})
    (out / "parse_info.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info), flush=True)


def embed(out, device, batch=256):
    import numpy as np
    import pandas as pd
    import torch
    from transformers import AutoModel, AutoTokenizer
    import s3_common as c3
    import s3_text as T3
    snap = c3.hf_snapshot(T3.CHECKPOINT["deberta"])
    tok = AutoTokenizer.from_pretrained(snap["path"], local_files_only=True)
    model = AutoModel.from_pretrained(snap["path"], local_files_only=True).to(device).eval()
    cap = pd.read_csv(out / "caption_levels.tsv", sep="\t", keep_default_na=False)
    vids = cap.video_id.to_numpy()
    if sorted(set(vids.tolist())) != list(range(1, 2197)):
        raise SystemExit("캡션 표의 영상이 1~2196이 아니다")
    info = dict(checkpoint=T3.CHECKPOINT["deberta"], revision=snap["revision"], weights_sha256=snap["weights_sha256"], layers=list(LAYERS), parse_info=json.loads((out / "parse_info.json").read_text()))
    for lv in LEVELS:
        text = cap[lv].astype(str).tolist()
        ok = np.array([len(t) > 0 for t in text])
        per = np.zeros((len(text), len(LAYERS) * 1024), np.float32)
        idx = np.flatnonzero(ok)
        order = idx[np.argsort([len(text[i]) for i in idx], kind="stable")]
        t0 = time.time()
        with torch.no_grad():
            for s in range(0, len(order), batch):
                pick = order[s:s + batch]
                enc = tok([text[i] for i in pick], padding=True, return_tensors="pt", return_special_tokens_mask=True)
                special = enc.pop("special_tokens_mask").bool()
                enc = {k: v.to(device) for k, v in enc.items()}
                h = model(**enc, output_hidden_states=True).hidden_states
                m = (enc["attention_mask"].bool() & ~special.to(device)).unsqueeze(-1).float()
                v = torch.cat([(h[i] * m).sum(1) / m.sum(1).clamp(min=1) for i in LAYERS], 1)
                per[pick] = v.cpu().numpy()
        target = np.zeros((2196, per.shape[1]), np.float32)
        n_empty_video = 0
        for v in range(1, 2197):
            sel = (vids == v) & ok
            if sel.any():
                target[v - 1] = per[sel].mean(0)
            else:
                n_empty_video += 1
        d = c3.OUT / f"deberta_{lv}"
        d.mkdir(parents=True, exist_ok=True)
        np.save(d / "target.npy", target)
        info[lv] = dict(n_captions_used=int(ok.sum()), n_captions_empty=int((~ok).sum()), n_videos_all_empty=n_empty_video, seconds=round(time.time() - t0, 1),
                        target_sha256=c3.sha256(d / "target.npy"))
        (d / "manifest.json").write_text(json.dumps(dict(info, level=lv), indent=1, ensure_ascii=False, default=str))
        print(lv, json.dumps(info[lv]), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("export", "parse", "embed"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    {"export": lambda: export(out), "parse": lambda: parse(out), "embed": lambda: embed(out, a.device)}[a.step]()


if __name__ == "__main__":
    main()
