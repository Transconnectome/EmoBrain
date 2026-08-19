> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Methodology

> **SUPERSEDED 2026-08-17 — LLM backbone removed.** Current methodology is the
> label-query decoder in `docs/direction_v6_labelquery_20260817.md`. The Qwen3-VL-4B
> encoder/teacher/student methodology below is historical and pending rewrite.

## Data

Five-subject Horikawa task-fMRI responses are aligned to 2,185 videos. Train,
validation, and test are disjoint at the stimulus level. Each target is a vector
of 34 independent Cowen emotion endorsement proportions. Targets are transformed
with `log1p` and standardized using training-stimulus statistics only.

## Encoders

- E1 ViT maps the 450-ROI response to a fixed 22x22 grid and adapts a pretrained
  ViT with LoRA.
- E2 BFM consumes frozen Brain-JEPA or SwiFT embeddings. Corrected Brain-JEPA
  uses the native one-patch fixed sinusoidal position code and is interpreted as
  short-window transfer.

Both return an embedding sequence projected into Qwen3-VL-4B token space. They
are evaluated as separate conditions, not concatenated branches.

## Direct Decoding

Brain tokens and a fixed question are processed by Qwen3-VL-4B. The base model
is frozen; LoRA, projector, segment markers, and linear 34D head are trained with
independent MSE. Validation profile Pearson selects a checkpoint, which is then
evaluated on the untouched test stimuli.

## Context Teacher and Distillation

The teacher receives brain tokens, V-JEPA2 video tokens, one human-written
MindCaptioning description, and the fixed question. Its raw 34D outputs are
cached for train/val with checkpoint and source provenance. A brain-only student
minimizes hard-label MSE plus MSE to the cached teacher outputs.

## Evaluation and Analysis

Primary metrics are per-stimulus 34D Pearson and CCC. Supporting metrics include
per-emotion correlation, MSE/R2, RSA, and sparse top-k agreement. Planned
analyses quantify pretrained-versus-scratch transfer, valid-window sensitivity,
cortical-network contributions, visual/semantic controls, cross-subject transfer,
and future cross-dataset generalization.
