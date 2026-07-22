# EmoBrain

**Short-window, low-data task-fMRI에서 fine-grained emotion profile을 해독하는
foundation-model framework.**

## Research Question

짧고 noisy한 task-fMRI만 주어진 상황에서 사전학습된 brain/vision
representation과 video-semantic context를 이용해 34차원 감정 구조를 얼마나
복원할 수 있는가? 그리고 학습 시의 context가 추론 시 brain-only decoder에
전달될 수 있는가?

성능 향상만이 목적은 아니다. 연구 축은 세 가지다.

1. **Transfer under constraint.** 짧은 TR window, 적은 task-fMRI 데이터,
   resting-to-task domain shift에서 foundation representation이 무엇을 전달하는가.
2. **Contextual supervision.** video와 human caption을 본 teacher가 brain-only
   student의 fine-grained decoding을 개선하는가.
3. **Neuroscientific interpretation.** 어떤 emotion dimension과 cortical system이
   transfer/context benefit을 지지하는가. 향후 cross-dataset 일반화로 확장한다.

## Canonical Architecture

- Backbone: `Qwen/Qwen3-VL-4B-Instruct` only
- E1: ViT, fMRI ROI grid에 image-pretrained prior를 적응
- E2: BFM, Brain-JEPA 또는 SwiFT의 pretrained embedding
- Output: 34개 독립 emotion score의 `log1p_z` regression
- Direct student: brain + fixed question
- Teacher: brain + V-JEPA2 video + MindCaptioning human caption + question
- Distilled student: brain + question, hard MSE + teacher-output MSE

Encoder는 E1/E2 두 종류뿐이다. 동일 fMRI의 raw와 BFM을 동시에 넣는 dual
branch는 사용하지 않는다. corrected Brain-JEPA는 native one-patch sinusoidal
position code를 사용한 short-window transfer representation으로 명시한다.

## Run

먼저 corrected Brain-JEPA를 canonical format으로 가져온다.

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/import_corrected_brain_jepa.sh
```

Direct runs:

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/trainer.sh /pscratch/sd/s/sjmoon/EmoBrain/project/code/configs/e1_vit_direct_qwen3vl4b.yaml
bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/trainer.sh /pscratch/sd/s/sjmoon/EmoBrain/project/code/configs/e2_brain_jepa_direct_qwen3vl4b.yaml
bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/trainer.sh /pscratch/sd/s/sjmoon/EmoBrain/project/code/configs/e2_swift_direct_qwen3vl4b.yaml
```

Teacher, cache, distilled student 전체 흐름:

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/run_e2_brain_jepa_distillation.sh
```

과거 Qwen2.5 구현은 `project/legacy/qwen25/`에 provenance 목적으로만 보존한다.
현재 구현 명세는 `docs/notes/implementation_spec_20260702.md`가 기준이다.
