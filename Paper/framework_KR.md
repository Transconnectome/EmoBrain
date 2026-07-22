# EmoBrain Framework

## Working Title

**EmoBrain: Foundation-Model Transfer for Fine-Grained Emotion Decoding from
Short-Window Task fMRI**

## Scientific Question

짧은 시간창과 제한된 표본을 가진 task-fMRI에서 foundation model의 사전학습
표상은 어떤 감정 정보를 전달하는가? 영상과 의미 context를 학습 시에 제공하면
brain-only 추론의 34차원 감정 구조 복원이 개선되는가?

## Contribution Axes

1. **Constrained transfer.** Resting/large-scale pretraining을 short-window
   task-fMRI에 적용할 때 보존되는 정보와 잃는 정보를 정량화한다.
2. **Two-family encoder test.** E1 ViT와 E2 BFM(Brain-JEPA/SwiFT)을 동일한
   Qwen3-VL-4B decoding stack에서 비교한다.
3. **Context-to-brain distillation.** Video와 human description을 사용하는
   teacher의 지식을 brain-only student로 전달한다.
4. **Fine-grained output.** 공존 가능한 34개 emotion endorsement를 독립
   회귀로 복원한다.
5. **Neuroscience extension.** Emotion별 cortical contribution, visual/semantic
   control, short-window sensitivity, cross-subject 및 cross-dataset 일반화를
   분석한다.

## Architecture

```text
Direct student
fMRI -> E1 ViT or E2 BFM -> projector -> Qwen3-VL-4B -> 34D

Teacher
brain + V-JEPA2 video + MindCaptioning human description
    -> modality projectors/tokens -> Qwen3-VL-4B -> 34D

Distilled student
brain -> same encoder/projector/Qwen stack -> 34D
loss = hard-label MSE + teacher-output MSE
```

동일 fMRI의 raw와 BFM을 함께 넣는 dual branch는 사용하지 않는다. BFM의 고유
가치는 독립 encoder condition, pretrained-scratch contrast, downstream
distillation benefit, 그리고 neuroscientific interpretation으로 평가한다.

## Caption Terminology

MindCaptioning caption은 20명의 crowd worker가 영상당 작성한 detailed visual
description이다. 원 논문은 quality checking과 proofreading을 보고하지만
affect-neutral annotation이라고 명시하지 않는다. 따라서 본 연구는 이를
`human-written descriptive caption`으로 부르고, caption-only 및 student-side
ablation으로 affective shortcut 가능성을 측정한다.

## Claims and Boundaries

- Brain-JEPA condition은 native 16-TR patch를 유지한 one-patch short-window
  transfer다. 장기 temporal dynamics를 사용했다고 주장하지 않는다.
- Encoder 우열만으로 연구를 정의하지 않는다.
- Context teacher의 높은 점수를 brain decoding 성능으로 부르지 않는다.
- 핵심 비교는 동일한 brain-only student의 hard-only와 distilled condition이다.
- Cross-dataset 및 cortical discovery는 후속 main analysis로 명시한다.
