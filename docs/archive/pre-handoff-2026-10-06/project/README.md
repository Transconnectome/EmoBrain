# EmoBrain Project

`project/code/` 가 유일한 활성 파이프라인이다. 논증은 `docs/paper_logic_merged.md`.

## Components

```text
project/code/
  decoder/         LabelQueryDecoder — CANONICAL model (LLM-free, ~3.8M params)
  brain_encoder/   brain -> token(s); roi_mean per-ROI tokens
  adapters/        MLP / Q-Former token projector
  fusion/          LEGACY Qwen3-VL assembly (pivot negative evidence; not current)
  training/        LEGACY LLM trainers (teacher/cache/student); superseded
  configs/         LEGACY Qwen3-VL configs; superseded
project/scripts/   cheap_fusion_and_floor, train_label_query, ...
project/data/      labels, fMRI, caption, feature sources
project/evaluation metrics and noise-ceiling utilities
project/legacy/    unsupported historical implementations
```

## Canonical model

`decoder/label_query_decoder.py`: 34개 감정 query (감정 이름 의미 임베딩으로 초기화, 학습 가능) 가
brain + video + caption 토큰에 cross-attend 하고 query 끼리 self-attend 한 뒤, 공유 scalar head 가
감정별 `log1p_z` 를 낸다. softmax 없음. LLM 없음.

`fusion/`, `training/`, Qwen3-VL `configs/` 는 pivot 의 **negative evidence** 로만 보존한다
(LLM teacher 0.553 ≈ cheap fusion 0.533; LLM student 0.154 < ridge 0.294). 현재 결과가 아니다.

## 데이터·타깃 계약 (변경 금지)

- Horikawa task-fMRI 5명, 2,185 고유 자극 영상.
- **split 은 자극 단위로만.** 같은 자극의 subject 반복 행을 가로질러 나누지 않는다.
- 출력 = 34개 Cowen-Keltner 감정 endorsement 비율.
- 변환 = 감정별 `log1p` 후 **train 통계로만** z-score.
- 손실 = 감정별 독립 MSE. **34-way softmax 나 sum-to-one 제약을 걸지 않는다.**
- 주 지표 = per-clip 34차원 Pearson + CCC. 보조 = 감정별 상관, MSE/R², RSA.

## 저장된 feature source 정의

`project/data/` 및 EmoViS 심볼릭으로 접근하는 자극 feature 의 정확한 추출 조건. 저장된 배열을 해석
하려면 이 표가 필요하다.

| 약어 | 정체 | shape |
|---|---|---|
| `video.vjepa2` | V-JEPA2 ViT-G pretrained, **16-frame uniform sampling**, last-block embed | (2185, 1408) |
| `video.clip` | OpenAI CLIP ViT-L/14 **image** encoder, 3-frame mean (25/50/75%) | (2185, 1024) |
| `video.dinov2` | DINOv2 ViT-G pretrained, 3-frame mean | (2185, D) |
| `video.videomae` | VideoMAE v2 ViT-G pretrained, 16-frame | (2185, D) |
| `video.caption` | **Qwen2.5-VL 생성** caption → SBERT `all-mpnet-base-v2` | (2185, 768) |
| `brain.roi_mean` | Schaefer-400 + Tian-S3 50 = 450 ROI mean BOLD, 5명 평균 | (2185, 450) |
| `brain.brain_jepa` | Brain-JEPA resting-pretrained hidden state, 5명 평균 | (2185, 768) |
| `brain.swift` | SwiFT NewE96_SL20 resting-pretrained hidden state, 5명 평균 | (2185, 768) |

⚠️ `video.caption` 은 **모델이 생성한** caption 이다. 인간이 쓴 MindCaptioning caption
(`caption_ck20.csv`, 영상당 crowd worker 20명)과 **다른 것**이므로 혼동하지 않는다.
BFM 임베딩의 추출 하이퍼파라미터·체크포인트 provenance 는
`project/shared/code/bfm_embeddings/_lib/SETTINGS_*.md` 에 있다.

## Provenance 요구사항

모든 결과는 model ID, encoder family/variant, source embedding, seed, split,
best validation score, held-out test metrics, checkpoint path 를 기록한다.
LEGACY Qwen2.5 / Qwen3-VL 산출물은 현행 결과와 절대 합산하지 않는다.

## Run (GPU job 은 사용자가 실행)

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/train_label_query.sh
```

모든 full run 은 val 로 checkpoint 를 고르고, 건드리지 않은 stimulus-held-out test 를 보고한다.
