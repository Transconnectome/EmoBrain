> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Canonical Implementation Specification

Updated 2026-07-22. This document supersedes all earlier E1-E4 and Qwen2.5
specifications. Historical decisions remain in `project_decisions.md` but are not
active implementation requirements.

## 1. Scientific Objective

EmoBrain tests whether pretrained brain/vision representations and multimodal
stimulus context improve fine-grained emotion decoding under three constraints:
short fMRI windows, limited task-fMRI samples, and pretraining-to-task domain
shift. Performance is one outcome; transfer behavior, contextual supervision,
generalization, and cortical interpretability are also primary outcomes.

## 2. Data and Target

- Horikawa task-fMRI: five subjects, 2,185 stimulus videos.
- Split by stimulus, never by repeated subject-stimulus row.
- Output: 34 Cowen emotion endorsement proportions.
- Transform: per-emotion `log1p` followed by train-only z-scoring.
- Loss: independent per-emotion MSE. No 34-way softmax or sum-to-one constraint.
- Primary metrics: per-clip 34D Pearson and CCC, supported by per-emotion
  correlation, MSE/R2, RSA, and retrieval metrics.

## 3. Canonical Model

Backbone is fixed to `Qwen/Qwen3-VL-4B-Instruct`. Brain/video vectors are mapped
to the Qwen hidden dimension by modality-specific projectors. Caption and fixed
question strings enter through the Qwen tokenizer. A linear head reads the last
valid question token and emits 34 real values.

Variable caption padding can create zeros inside the concatenated attention mask.
Before Qwen, each sample is compacted to remove those internal holes and is
right-padded only at the end. Readout also uses the maximum valid token index,
not `mask.sum()-1`, as a defensive invariant.

## 4. Encoder Families

### E1 ViT

An image-pretrained ViT receives a deterministic 22x22 arrangement of the 450
ROI values. Frozen and LoRA adaptation are allowed. This family asks whether an
image prior can be adapted to task-fMRI geometry; it is not assumed to be
biologically native.

### E2 BFM

Brain foundation representations are provided by Brain-JEPA or SwiFT.

- Brain-JEPA: use `brain_jepa_pretrained_native_mean`. It preserves the native
  16-TR patchification, uses one temporal patch, and retains the model-generated
  one-patch fixed sinusoidal code. It is short-window transfer, not native
  long-range temporal inference.
- SwiFT: use an SL20 checkpoint with the matched 20-frame extraction setting.

E1 and E2 are competing encoder families in a common slot. The main architecture
does not concatenate raw fMRI with a BFM representation.

## 5. Direct Student

Input is brain representation plus a fixed task question. Qwen base weights are
frozen and LoRA, the brain projector, segment markers, and 34D head are trained.
Checkpoint selection uses validation profile Pearson. The selected checkpoint is
evaluated once on stimulus-held-out test.

## 6. Context Teacher

Input order is V-JEPA2 video, human-written MindCaptioning description, brain,
and fixed question. The MindCaptioning paper describes the captions as
crowdsourced detailed visual-content descriptions with manual quality checks; it
does not establish affect neutrality. They are therefore called human-written
descriptive captions, and their effect must be controlled empirically.

The teacher is supervised on the same 34D target and stores its best validation
checkpoint. Teacher predictions for train and val are cached by
`subject|stimulus_num` with checkpoint, modality, and brain-source provenance.

## 7. Distilled Student

The student has exactly the brain-only inference form. It minimizes:

```text
L = lambda_hard * MSE(student, label)
  + lambda_dist * MSE(student, cached_teacher)
```

Missing teacher cache keys are fatal. The main run uses `lambda_hard=1` and
`lambda_dist=1`. Hard-only, context-only, shuffled-brain, and modality ablations
are a subsequent student-analysis stage, not prerequisites for wiring the core
teacher-cache-student path.

## 8. Required Provenance

Every result records model ID, encoder family/variant, source embedding, seed,
split, best validation score, held-out test metrics, and checkpoint path. Legacy
Qwen2.5 output is never pooled with canonical Qwen3-VL-4B results.

## 9. Planned Scientific Analyses

- pretrained versus scratch transfer under short windows
- sensitivity to valid TR length and padding ratio
- per-emotion and cortical-network decoding maps
- visual/semantic controls and prediction-level variance partitioning
- cross-subject transfer
- future cross-dataset generalization
