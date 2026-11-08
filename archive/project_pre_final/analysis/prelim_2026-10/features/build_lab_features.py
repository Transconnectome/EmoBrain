#!/usr/bin/env python3
"""랩서버 content_ladder.py 표준 형식의 영상·caption 특징 만들기 (Perlmutter, 2026-10-26).

표준 형식: <이름>.npy (영상 × 차원, float32) + <이름>_video_id.tsv (열 video_id, 1~2196).
content_ladder.py 는 /storage/bigdata/EmoBrain_response/features/ 의 이 쌍을 자동으로 읽는다.

만드는 특징
  vjepa2_vitg_final   : V-JEPA 2 ViT-g 마지막 block 토큰 평균 (1408). 원본 2185 행.
  caption_vlm_mpnet   : 우리가 VLM 으로 만든 캡션의 all-mpnet-base-v2 임베딩 (768). 원본 2185 행. 일부 캡션 오류 확인됨.
  caption_human_mpnet : MindCaptioning 사람 캡션(영상당 20개)의 all-mpnet-base-v2 임베딩 평균 (768). 2196 행.
영상 2186~2196 은 영상 1~11 과 디코딩 결과가 같은 파일이다 (stimulus_crosswalk.tsv). 원본에 행이 없는 특징은
canonical 영상의 행을 복사한다.
사람 캡션 임베딩은 sentence-transformers 없이 같은 모델 구성(Transformer → 토큰 평균 → L2 정규화, 최대 384 토큰)으로
계산한다. 먼저 생성 캡션 일부를 다시 계산해 기존 caption_embed_final.npy 와 같은지 확인한다.
사용: python build_lab_features.py --bundle <자극 묶음> --out <출력 폴더> [--device cuda]
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

MODEL = "sentence-transformers/all-mpnet-base-v2"
N_VIDEOS = 2196


def read_crosswalk(bundle):
    cw = pd.read_csv(bundle / "index/stimulus_crosswalk.tsv", sep="\t", comment="#")
    canon = dict(zip(cw.video_number, cw.canonical_stimulus_id))
    assert sorted(canon) == list(range(1, N_VIDEOS + 1)), "crosswalk 영상 번호가 1~2196 이 아님"
    return canon


def expand_2185(X, canon):
    """행 i = 영상 i+1 (1~2185) 인 배열을 1~2196 으로. 2186~2196 은 canonical 영상 행."""
    assert X.shape[0] == 2185
    rows = [canon[v] - 1 if v > 2185 else v - 1 for v in range(1, N_VIDEOS + 1)]
    assert max(rows) < 2185
    return X[rows]


class Encoder:
    def __init__(self, device):
        import torch
        from transformers import AutoModel, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModel.from_pretrained(MODEL).to(device).eval()
        self.device = device

    def __call__(self, texts, batch_size=128):
        torch, out = self.torch, []
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                b = self.tok(texts[i:i + batch_size], padding=True, truncation=True, max_length=384, return_tensors="pt").to(self.device)
                h = self.model(**b).last_hidden_state
                m = b["attention_mask"].unsqueeze(-1).to(h.dtype)
                e = (h * m).sum(1) / m.sum(1).clamp(min=1e-9)
                out.append(torch.nn.functional.normalize(e, dim=1).float().cpu().numpy())
        return np.vstack(out)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    canon = read_crosswalk(a.bundle)
    E = a.bundle / "embeddings"
    for d in ["vjepa2", "caption"]:
        assert np.array_equal(np.load(E / d / "stim_idx.npy"), np.arange(2185)), f"{d} 행 순서가 영상 1~2185 가 아님"

    # 기존 생성 캡션 임베딩 재계산으로 인코더 확인
    enc = Encoder(a.device)
    gen = json.loads((E / "caption/captions.json").read_text())
    old = np.load(E / "caption/caption_embed_final.npy")
    idx = list(range(0, 2185, 37))
    cos = (enc([gen[str(i)] for i in idx]) * old[idx] / np.linalg.norm(old[idx], axis=1, keepdims=True)).sum(1)
    print(f"인코더 확인: 생성 캡션 {len(idx)}개, 기존 임베딩과 cosine 최소 {cos.min():.6f}", flush=True)
    assert cos.min() > 0.999, "기존 caption_embed_final.npy 와 다른 인코딩"

    # 사람 캡션
    cap = pd.read_csv(a.bundle / "captions/caption_ck20.csv", encoding="utf-8-sig")
    assert sorted(cap.video_id.unique()) == list(range(1, N_VIDEOS + 1))
    emb = enc(cap.description.fillna("").astype(str).tolist())
    human = np.vstack([emb[(cap.video_id == v).values].mean(0) for v in range(1, N_VIDEOS + 1)])
    n_per = cap.groupby("video_id").size()
    names34 = [l.strip().lower() for l in open(a.bundle / "index/cowen34_order.txt") if l.strip()]
    pat = re.compile(r"\b(?:" + "|".join(re.escape(w) for w in names34) + r")\b", re.I)
    has_emo = cap.description.fillna("").str.contains(pat)

    feats = {
        "vjepa2_vitg_final": (expand_2185(np.load(E / "vjepa2/vjepa2_pretrained_final.npy"), canon),
                              "embeddings/vjepa2/vjepa2_pretrained_final.npy; 2186~2196 = canonical 1~11 행"),
        "caption_vlm_mpnet": (expand_2185(old, canon),
                              "embeddings/caption/caption_embed_final.npy (생성 캡션, 검수 전); 2186~2196 = canonical 1~11 행"),
        "caption_human_mpnet": (human, f"captions/caption_ck20.csv, 영상당 캡션 {n_per.min()}~{n_per.max()}개의 {MODEL} 임베딩 평균"),
    }
    man = []
    for name, (X, src) in feats.items():
        X = X.astype(np.float32); assert X.shape[0] == N_VIDEOS and np.isfinite(X).all()
        np.save(a.out / f"{name}.npy", X)
        pd.DataFrame(dict(video_id=np.arange(1, N_VIDEOS + 1))).to_csv(a.out / f"{name}_video_id.tsv", sep="\t", index=False)
        man.append(dict(name=name, rows=X.shape[0], dims=X.shape[1], sha256=sha256(a.out / f"{name}.npy"), source=src))
        print(f"{name}: {X.shape}", flush=True)
    pd.DataFrame(man).to_csv(a.out / "MANIFEST.tsv", sep="\t", index=False)
    stats = dict(encoder=MODEL, encoder_check_min_cosine=float(cos.min()), n_human_captions=int(len(cap)),
                 frac_human_captions_with_category_word=float(has_emo.mean()),
                 frac_videos_with_any_category_word=float(has_emo.groupby(cap.video_id).any().mean()))
    (a.out / "build_info.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1))
    print(stats)


if __name__ == "__main__":
    main()
