#!/usr/bin/env python3
"""캡션의 어떤 단어·맥락이 teacher 이득을 만드는지 가르는 캡션 변형 특징 (2026-10-28).

모두 MindCaptioning 사람 캡션(caption_ck20.csv, 영상당 20개)에서 만들고, build_lab_features.py 와 같은 인코더로 임베딩해 영상별 평균한다.
  caption_human_scrambled_mpnet : 캡션마다 단어 순서를 무작위로 섞음 (단어는 그대로, 문장 맥락만 깨짐)
  caption_bow_tfidf             : 영상별 20개 캡션을 합친 단어 빈도 TF-IDF (단어만 쓰는 해석 가능한 표현, 임베딩 없음)
  caption_minus_<범주>_mpnet    : 범주 단어를 지운 캡션. 범주 단어는 장면 개념 annotation(semantic_features.csv)과 함께 나오는 정도가 가장 큰
                                  단어 40개 (영상 캡션에 단어가 있는지와 범주 개념 점수의 상관, 10개 영상 이상에 나오는 단어)
  caption_minus_random<k>_mpnet : 같은 수의 단어를 비슷한 빈도의 단어 중 무작위로 지운 대조 (범주와 무관한 정보 손실의 크기)
출력: <특징 폴더>/<이름>.npy + _video_id.tsv, caption_variants/lexicons.json (범주별 단어), caption_variants/<이름>.json (지운 단어, 바뀐 캡션 비율)
여러 노드에서 --only 로 나눠 돌릴 수 있게 변형마다 정보 파일을 따로 쓴다.
사용: python build_caption_variants.py --bundle <자극 묶음> --out <특징 폴더> [--only scrambled,bow,animals,...] [--lexicon-only]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import build_lab_features as blf  # noqa: E402

SEM = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/semantic_features.csv")
GROUPS = {
    "animals": ["Aquatic animals", "Birds", "Cats", "Dogs", "Insects", "Land animals", "Large animals", "Small animals"],
    "food": ["Food"],
    "people": ["Men", "Women", "Boys", "Girls", "Elderly people", "People"],
    "affiliation": ["Babies", "Couples"],
    "harm": ["Blood", "Dead bodies", "Injuries", "Guns", "Weapons", "Explosions", "Fire", "Sharp objects", "Hospitals", "Soldiers"],
    "sexual": ["Sexual activity", "Naked people", "Genitalia"],
    "sports": ["Sports", "Stunts", "Gymnasiums", "Fast-moving objects"],
    "nature": ["Nature", "Mountains", "Vast landscapes", "Clouds", "Snow", "Plants", "Underwater scenes", "Above water scenes"],
    "bodily": ["Feces/urine/vomit"],
}
N_WORDS = 40
STOP = set("a an the is are was were be been being of in on at to and or but with by for from as into onto over under up down out off "
           "it its his her their he she they them this that these those there here who whom which what while when where then than so very also".split())


def tokens(t):
    return [w for w in re.findall(r"[a-z]+", t.lower()) if len(w) > 2 and w not in STOP]


def lexicons(cap):
    sem = pd.read_csv(SEM); sem.index = sem.pop("stimulus_num").str.replace("stimulus_", "").astype(int)
    vids = np.arange(1, 2186)
    vw = cap.groupby("video_id").description.apply(lambda s: set(w for t in s.fillna("") for w in tokens(t)))
    vocab = sorted({w for s in vw for w in s})
    X = np.zeros((len(vids), len(vocab)), bool); pos = {w: i for i, w in enumerate(vocab)}
    for r, v in enumerate(vids):
        for w in vw.get(v, ()):
            X[r, pos[w]] = True
    keep = X.sum(0) >= 10; X = X[:, keep]; vocab = np.array(vocab)[keep]
    Xz = (X - X.mean(0)) / X.std(0)
    out = {}
    for g, cols in GROUPS.items():
        y = sem.reindex(vids)[cols].max(1).values; yz = (y - y.mean()) / y.std()
        r = Xz.T @ yz / len(yz); out[g] = list(vocab[np.argsort(-r)[:N_WORDS]])
    freq = dict(zip(vocab, X.sum(0)))
    return out, freq


def random_lexicon(words, freq, k, seed):
    """범주 단어와 빈도가 비슷한 단어를 무작위로 같은 수만큼 (범주 단어는 제외)."""
    rng = np.random.RandomState(seed); pool = [w for w in freq if w not in words]
    fv = np.array([freq[w] for w in pool]); out = []
    for w in words:
        cand = [i for i in np.argsort(np.abs(np.log(fv) - np.log(freq[w])))[:30] if pool[i] not in out]
        out.append(pool[rng.choice(cand)])
    return out


def remove_words(texts, words):
    pat = re.compile(r"\b(?:" + "|".join(sorted(map(re.escape, words), key=len, reverse=True)) + r")\b", re.I)
    clean = texts.map(lambda t: re.sub(r"\s{2,}", " ", pat.sub("", t)).strip() or ".")
    return clean, float((clean != texts).mean())


def save(out, name, X, info, note):
    X = X.astype(np.float32); np.save(out / f"{name}.npy", X)
    pd.DataFrame(dict(video_id=np.arange(1, blf.N_VIDEOS + 1))).to_csv(out / f"{name}_video_id.tsv", sep="\t", index=False)
    with open(out / "MANIFEST.tsv", "a") as f:
        f.write(f"{name}\t{X.shape[0]}\t{X.shape[1]}\t{blf.sha256(out / f'{name}.npy')}\t{note}\n")
    info[name] = info.get(name, {}) | dict(shape=list(X.shape)); print(name, X.shape, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--device", default="cpu"); ap.add_argument("--only"); ap.add_argument("--lexicon-only", action="store_true")
    a = ap.parse_args()
    cap = pd.read_csv(a.bundle / "captions/caption_ck20.csv", encoding="utf-8-sig"); text = cap.description.fillna("").astype(str)
    lex, freq = lexicons(cap)
    idir = a.out / "caption_variants"; idir.mkdir(exist_ok=True)
    (idir / "lexicons.json").write_text(json.dumps(lex, ensure_ascii=False, indent=1)); info = {}
    if a.lexicon_only:
        for g, ws in lex.items():
            print(f"{g}: {', '.join(ws[:20])}")
        return
    todo = a.only.split(",") if a.only else ["scrambled", "bow"] + list(GROUPS) + ["random1", "random2"]
    enc = None
    def embed(texts):
        nonlocal enc
        enc = enc or blf.Encoder(a.device); e = enc(texts.tolist())
        return np.vstack([e[(cap.video_id == v).values].mean(0) for v in range(1, blf.N_VIDEOS + 1)])
    for t in todo:
        if t == "scrambled":
            rng = np.random.RandomState(0)
            sc = text.map(lambda s: " ".join(rng.permutation(s.split())) if s.split() else ".")
            save(a.out, "caption_human_scrambled_mpnet", embed(sc), info, "사람 캡션 단어 순서 섞음 (seed 0), mpnet 평균")
        elif t == "bow":
            from sklearn.feature_extraction.text import TfidfVectorizer
            docs = cap.groupby("video_id").description.apply(lambda s: " ".join(s.fillna(""))).reindex(range(1, blf.N_VIDEOS + 1)).fillna("")
            tv = TfidfVectorizer(min_df=5, max_features=5000, stop_words="english", sublinear_tf=True)
            Xb = tv.fit_transform(docs).toarray()
            info["caption_bow_tfidf"] = dict(vocab=list(tv.get_feature_names_out()))
            save(a.out, "caption_bow_tfidf", Xb, info, "영상별 20개 캡션 합친 TF-IDF (min_df 5, 최대 5000 단어)")
        elif t.startswith("random"):
            k = int(t[6:]); words = random_lexicon(set(w for ws in lex.values() for w in ws), freq, N_WORDS, seed=k)
            clean, frac = remove_words(text, words); info[f"caption_minus_random{k}_mpnet"] = dict(words=words, frac_captions_changed=frac)
            save(a.out, f"caption_minus_random{k}_mpnet", embed(clean), info, f"빈도 맞춘 무작위 단어 {N_WORDS}개 삭제 (seed {k})")
        else:
            clean, frac = remove_words(text, lex[t]); info[f"caption_minus_{t}_mpnet"] = dict(words=lex[t], frac_captions_changed=frac)
            save(a.out, f"caption_minus_{t}_mpnet", embed(clean), info, f"{t} 범주 단어 {N_WORDS}개 삭제")
        for k, v in info.items():
            (idir / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
