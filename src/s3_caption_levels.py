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
11/18 둘째 판(석진 님 "품사 근사 보완, 단어 순서 보완 진행"): scene graph parser로 수준을 직접 뽑고, 단어 순서만 깨뜨린 판을 더한다.
4. graph (GPU 환경): FACTUAL parser(Li 외 2023, Findings of ACL, flan-t5-large-VG-factual-sg, 입력 "Generate Scene Graph: " + 원래 캡션, greedy, 최대 256 token)로
   캡션마다 (주어, 관계, 목적어) 삼항을 낸다. 속성은 (물체, is, 속성) 꼴이다. <out>/caption_graph.tsv
5. graph_levels (CPU): 삼항에서 세 판을 만들고 정서어를 뺀다. 같은 삼항이 두 번 나오면 하나만 둔다. 물체는 처음 나온 순서다.
   - graph_objects: 물체 이름. ex) "man, road"
   - graph_objattr: 속성을 앞에 붙인 물체. ex) "old man, icy road"
   - graph_rel: 위 + object relations을 "주어 관계 목적어"로. ex) "old man, icy road, man slip on road". 부사와 문장 구조는 없다.
   - shuffled: Caption feature 정서어 제거판과 같은 글(s3_text.load_captions(True))의 단어를 캡션마다 무작위로 섞은 것(seed [20261118, 캡션 행]).
     단어는 같고 순서만 다르다. 문장 임베딩이 단어 순서에 얼마나 기대는지 보는 대조다.
   <out>/caption_graph_levels.tsv
6. embed --levels graph_objects,graph_objattr,graph_rel,shuffled: 위와 같은 임베딩. 출력 <s3_features>/deberta_<수준>/target.npy
   한계: parser에도 오류가 있다(ex) 동사를 속성으로 넣음 "vehicle is fighting"). 품사 판과 parser 판이 같은 방향인지를 함께 본다.
11/19 셋째 판(석진 님 "다 진행"): 단어 수를 맞춘 무작위 대조. 판이 올라갈수록 단어 수도 늘어서 "object relations 때문에 줄었다"와 "단어가 많아져서 줄었다"를 가르려는 것이다.
7. random_levels (CPU): 캡션마다, 정서어 제거판 캡션의 단어 가운데 parser 판(objects, objects + object states, + object relations)의
   겹치지 않는 단어 수(소문자 알파벳 단어)만큼을 무작위로 골라 원래 순서대로 남긴다(seed [20261119, 캡션 행, 판 번호]). 단어 수가 캡션 단어 수 이상이면 캡션 전체를 쓴다.
   object relations 판은 삼항마다 objects 이름이 되풀이되어 그냥 세면 단어 수가 부풀므로 겹치지 않는 단어로 센다.
   <out>/caption_random_levels.tsv(rand_objects, rand_objattr, rand_rel), random_levels_info.json
사용: s3_caption_levels.py export|parse|graph|graph_levels|random_levels|embed --out <작업 폴더> [--device cuda] [--levels <쉼표>]
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

LEVELS = ("objects", "objattr")
GRAPH_LEVELS = ("graph_objects", "graph_objattr", "graph_rel", "shuffled")
RANDOM_LEVELS = ("rand_objects", "rand_objattr", "rand_rel")  # 11/19. 같은 순서의 parser 판과 단어 수를 맞춘 무작위 판
LEVEL_FILE = {**{lv: "caption_levels.tsv" for lv in LEVELS}, **{lv: "caption_graph_levels.tsv" for lv in GRAPH_LEVELS}, **{lv: "caption_random_levels.tsv" for lv in RANDOM_LEVELS}}
RANDOM_SEED = 20261119
PARSER = "lizhuang144/flan-t5-large-VG-factual-sg"
SHUFFLE_SEED = 20261118
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


def graph(out, device, batch=64):
    import pandas as pd
    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    path = Path(snapshot_download(PARSER, local_files_only=True))
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSeq2SeqLM.from_pretrained(path).to(device).eval()
    cap = pd.read_csv(out / "captions.tsv", sep="\t", keep_default_na=False)
    text = cap.description.astype(str).tolist()
    order = sorted(range(len(text)), key=lambda i: len(text[i]))
    res = [None] * len(text)
    t0 = time.time()
    with torch.no_grad():
        for s in range(0, len(order), batch):
            pick = order[s:s + batch]
            enc = tok(["Generate Scene Graph: " + text[i] for i in pick], return_tensors="pt", padding=True, truncation=True, max_length=256).to(device)
            o = model.generate(**enc, max_length=256, num_beams=1)
            for i, g in zip(pick, tok.batch_decode(o, skip_special_tokens=True)):
                res[i] = g
            if s // batch % 50 == 0:
                print(f"{s + len(pick)}/{len(order)} {time.time() - t0:.0f}초", flush=True)
    cap["graph"] = res
    cap.to_csv(out / "caption_graph.tsv", sep="\t", index=False)
    info = dict(parser=PARSER, revision=path.name, prompt="Generate Scene Graph: ", max_length=256, num_beams=1, n_captions=len(cap), seconds=round(time.time() - t0, 1))
    (out / "graph_info.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info), flush=True)


TRIPLE = re.compile(r"\(\s*([^(),]+?)\s*,\s*([^(),]+?)\s*,\s*([^()]+?)\s*\)")


def render(g, drop):
    """삼항 글 → (물체, 물체 + 속성, 관계까지) 세 판. drop은 정서어를 지우는 함수다."""
    seen, ents, attrs, rels = set(), [], {}, []
    for sub, rel, obj in TRIPLE.findall(g):
        t = (sub.strip().lower(), rel.strip().lower(), obj.strip().lower())
        if t in seen:
            continue
        seen.add(t)
        for e in ((t[0],) if t[1] == "is" else (t[0], t[2])):
            if e not in ents:
                ents.append(e)
        if t[1] == "is":
            attrs.setdefault(t[0], []).append(t[2])
        else:
            rels.append(t)
    clean = lambda items: ", ".join(x for x in (drop(i) for i in items) if x)
    objattr = [" ".join(attrs.get(e, []) + [e]) for e in ents]
    return clean(ents), clean(objattr), clean(objattr + [" ".join(r) for r in rels])


def graph_levels(out):
    import numpy as np
    import pandas as pd
    import s3_text as T3
    words = T3.affect_words()
    pat = re.compile(r"\b(?:" + "|".join(words) + r")\b", re.I)
    drop = lambda t: re.sub(r"\s{2,}", " ", pat.sub("", t)).strip()
    cap = pd.read_csv(out / "caption_graph.tsv", sep="\t", keep_default_na=False)
    lv = [render(g, drop) for g in cap.graph.astype(str)]
    cap["graph_objects"], cap["graph_objattr"], cap["graph_rel"] = zip(*lv)
    vid, text = T3.load_captions(True)
    if not (np.asarray(vid) == cap.video_id.to_numpy()).all():
        raise SystemExit("정서어 제거판 캡션과 캡션 표의 순서가 다르다")
    cap["shuffled"] = [" ".join(np.random.default_rng([SHUFFLE_SEED, i]).permutation(t.split()).tolist()) for i, t in enumerate(text)]
    cap["no_emotion_original"] = text
    cap.to_csv(out / "caption_graph_levels.tsv", sep="\t", index=False)
    n_trip = cap.graph.astype(str).map(lambda g: len(TRIPLE.findall(g)))
    info = dict(n_captions=len(cap), mean_triples=float(n_trip.mean()), no_triples=int((n_trip == 0).sum()), **{f"empty_{k}": int((cap[k] == "").sum()) for k in GRAPH_LEVELS},
                n_with_relation=int(cap.graph.astype(str).map(lambda g: any(r.strip().lower() != "is" for _, r, _ in TRIPLE.findall(g))).sum()), shuffle_seed=SHUFFLE_SEED)
    (out / "graph_levels_info.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info), flush=True)


def random_levels(out):
    import numpy as np
    import pandas as pd
    cap = pd.read_csv(out / "caption_graph_levels.tsv", sep="\t", keep_default_na=False)
    words = lambda t: len(set(re.findall(r"[a-z]+", str(t).lower())))
    cols, full = {lv: [] for lv in RANDOM_LEVELS}, 0
    for i, row in enumerate(cap.itertuples()):
        tok = str(row.no_emotion_original).split()
        for j, (lv, src) in enumerate(zip(RANDOM_LEVELS, ("graph_objects", "graph_objattr", "graph_rel"))):
            k = words(getattr(row, src))
            if k >= len(tok):
                cols[lv].append(" ".join(tok))
                full += 1
            else:
                pick = np.sort(np.random.default_rng([RANDOM_SEED, i, j]).choice(len(tok), k, replace=False))
                cols[lv].append(" ".join(tok[q] for q in pick))
    for lv in RANDOM_LEVELS:
        cap[lv] = cols[lv]
    cap[["video_id", "description", "no_emotion_original", *RANDOM_LEVELS]].to_csv(out / "caption_random_levels.tsv", sep="\t", index=False)
    info = dict(seed=RANDOM_SEED, n_captions=len(cap), n_level_rows_using_full_caption=full,
                **{f"mean_words_{lv}": float(cap[lv].map(lambda t: len(str(t).split())).mean()) for lv in RANDOM_LEVELS},
                **{f"mean_unique_words_{src}": float(cap[src].map(words).mean()) for src in ("graph_objects", "graph_objattr", "graph_rel")})
    (out / "random_levels_info.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info), flush=True)


def embed(out, device, batch=256, levels=LEVELS):
    import numpy as np
    import pandas as pd
    import torch
    from transformers import AutoModel, AutoTokenizer
    import s3_common as c3
    import s3_text as T3
    snap = c3.hf_snapshot(T3.CHECKPOINT["deberta"])
    tok = AutoTokenizer.from_pretrained(snap["path"], local_files_only=True)
    model = AutoModel.from_pretrained(snap["path"], local_files_only=True).to(device).eval()
    info = dict(checkpoint=T3.CHECKPOINT["deberta"], revision=snap["revision"], weights_sha256=snap["weights_sha256"], layers=list(LAYERS), parse_info=json.loads((out / "parse_info.json").read_text()))
    for f in ("graph_info.json", "graph_levels_info.json", "random_levels_info.json"):
        if (out / f).exists() and any(lv in GRAPH_LEVELS + RANDOM_LEVELS for lv in levels):
            info[f.replace(".json", "")] = json.loads((out / f).read_text())
    for lv in levels:
        cap = pd.read_csv(out / LEVEL_FILE[lv], sep="\t", keep_default_na=False)
        vids = cap.video_id.to_numpy()
        if sorted(set(vids.tolist())) != list(range(1, 2197)):
            raise SystemExit("캡션 표의 영상이 1~2196이 아니다")
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
    ap.add_argument("step", choices=("export", "parse", "graph", "graph_levels", "random_levels", "embed"))
    ap.add_argument("--levels", default=",".join(LEVELS), help="embed할 수준(쉼표). 기본은 품사 판 둘")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    levels = tuple(a.levels.split(","))
    if set(levels) - set(LEVEL_FILE):
        raise SystemExit(f"모르는 수준: {set(levels) - set(LEVEL_FILE)}")
    {"export": lambda: export(out), "parse": lambda: parse(out), "graph": lambda: graph(out, a.device), "graph_levels": lambda: graph_levels(out), "random_levels": lambda: random_levels(out),
     "embed": lambda: embed(out, a.device, levels=levels)}[a.step]()


if __name__ == "__main__":
    main()
