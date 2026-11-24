#!/usr/bin/env python3
"""감정어를 지운 사람 캡션 임베딩 (2026-10-28).

목적: 내용 teacher 의 이득이 캡션 작성자의 정서 해석(감정어)에서 오는지 가르는 대조.
방법: MindCaptioning 사람 캡션(caption_ck20.csv)에서 아래 정서 상태어를 단어 단위로 지우고(대소문자 무시),
  build_lab_features.py 와 같은 인코더(all-mpnet-base-v2, 토큰 평균, L2 정규화)로 임베딩해 영상별 20개를 평균한다.
  웃다·울다 같은 보이는 행동은 영상 내용이라 지우지 않는다. 목록은 34개 범주 이름과 흔한 형태·유의어로 만든 것이다.
출력: <특징 폴더>/caption_human_noemo_mpnet.npy + _video_id.tsv, caption_human_noemo_build_info.json (지운 단어 빈도)
사용: python build_caption_noemo.py --bundle <자극 묶음> --out <특징 폴더> [--device cpu]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import build_lab_features as blf  # noqa: E402

AFFECT_WORDS = """
admiration admire admired admiring adoration adore adored adorable cute aesthetic beautiful beauty gorgeous lovely
amusement amused amusing funny hilarious humorous anger angry furious rage enraged mad annoyed irritated
anxiety anxious nervous worried worry tense uneasy awe awed awesome awestruck amazing amazed awkward awkwardness
embarrassing embarrassed embarrassment boredom bored boring calm calmness calming peaceful relaxing relaxed serene tranquil
confusion confused confusing contempt contemptuous scornful craving crave delicious tasty appetizing mouthwatering
disgust disgusted disgusting gross revolting repulsive nasty disappointment disappointed disappointing
empathic empathy sympathy sympathetic pity pitiful entrancement entranced entrancing mesmerizing mesmerized hypnotic
envy envious jealous jealousy excitement excited exciting thrilling thrilled fear afraid scared scary frightening frightened
fearful terrified terrifying guilt guilty horror horrified horrifying horrific horrible creepy dreadful terrible awful
interest interesting interested intriguing curious joy joyful joyous happy happiness happily glad delighted delightful cheerful
nostalgia nostalgic pride proud relief relieved romance romantic sad sadness sorrow sorrowful unhappy depressing depressed gloomy
satisfaction satisfied satisfying sexual sexy erotic sensual seductive surprise surprised surprising shocking shocked
triumph triumphant victorious emotion emotional emotions feeling feelings enjoy enjoys enjoying enjoyed love loving loved hate hated
""".split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args()
    cap = pd.read_csv(a.bundle / "captions/caption_ck20.csv", encoding="utf-8-sig")
    pat = re.compile(r"\b(?:" + "|".join(sorted(set(AFFECT_WORDS), key=len, reverse=True)) + r")\b", re.I)
    text = cap.description.fillna("").astype(str)
    hits = Counter(m.lower() for t in text for m in pat.findall(t))
    clean = text.map(lambda t: re.sub(r"\s{2,}", " ", pat.sub("", t)).strip() or ".")
    emb = blf.Encoder(a.device)(clean.tolist())
    X = np.vstack([emb[(cap.video_id == v).values].mean(0) for v in range(1, blf.N_VIDEOS + 1)]).astype(np.float32)
    name = "caption_human_noemo_mpnet"
    np.save(a.out / f"{name}.npy", X)
    pd.DataFrame(dict(video_id=np.arange(1, blf.N_VIDEOS + 1))).to_csv(a.out / f"{name}_video_id.tsv", sep="\t", index=False)
    changed = (clean != text)
    info = dict(encoder=blf.MODEL, n_words_in_list=len(set(AFFECT_WORDS)), n_captions=int(len(cap)),
                frac_captions_changed=float(changed.mean()), frac_videos_with_change=float(changed.groupby(cap.video_id).any().mean()),
                n_words_removed=int(sum(hits.values())), top_removed=hits.most_common(30), sha256=blf.sha256(a.out / f"{name}.npy"))
    (a.out / "caption_human_noemo_build_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    with open(a.out / "MANIFEST.tsv", "a") as f:
        f.write(f"{name}\t{X.shape[0]}\t{X.shape[1]}\t{info['sha256']}\tcaptions/caption_ck20.csv, 정서 상태어 {len(set(AFFECT_WORDS))}개 삭제 후 {blf.MODEL} 평균\n")
    print({k: v for k, v in info.items() if k != "top_removed"}); print(info["top_removed"][:15])


if __name__ == "__main__":
    main()
