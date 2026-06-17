# Thesis Rationale v1 — Snapshot (2026-04-15)

**상태:** RQ 정제 중. 방법론 lineup 확정, central question 미확정.

---

## 1. Thesis umbrella

**"뇌의 감정 표상: 구조와 역학"**

감각 입력에서 감정 경험으로의 변환 과정에서, 뇌가 감정을 어떤 구조로 표상하고
시간에 따라 어떻게 전개하는지를 — AI foundation model과 최신 deep learning 방법론을
도구로 사용하여 — 규명한다.

---

## 2. 세 축 (Brain — Behavior — Stimulus)

| 축 | 내용 | 데이터 |
|----|------|--------|
| **Brain** | fMRI activation patterns | Horikawa: 5 subj × 2185 videos × 450 parcels; Emo-FilM: 30 subj, 2.5h continuous |
| **Behavior** | Emotion ratings | Horikawa: 34 cat + 14 dim = 48 targets (crowd-sourced); Emo-FilM: 50 items (본인 rating) |
| **Stimulus** | Video features | V-JEPA2 (1408d, 32 layers), CLIP (512d, 24 layers), Vision (1000d), Semantic (73d) |

세 축의 관계를 각각 pairwise로, 그리고 jointly 분석하는 것이 framework의 핵심.

---

## 3. 왜 Video foundation model인가

1. **감정은 본질적으로 동적** — 공포는 긴장 누적, 놀람은 전환, 기쁨은 발현. Static image 모델은 이를 못 잡음.
2. **자극이 video** — Horikawa (3초 video clips), Emo-FilM (2.5h 영화). Stimulus-model match 필수.
3. **V-JEPA2 특성** — 1M hours 자기지도학습, physical reasoning (object permanence, motion trajectory) 학습. 감정에 관련된 low-level primitive (visual looming 등) 포착.
4. **Field benchmark** — Algonauts 2025 우승 (TRIBE, Meta FAIR)이 video+audio+text trimodal. Video model이 brain encoding의 standard.

참고:
- V-JEPA2: Meta, 2025 (arXiv 2506.09985)
- TRIBE v2: Meta, 2026 (Algonauts 2025 winner)
- Sartzetaki et al. (2025): 99 video models benchmarked on Horikawa data (ICLR)

---

## 4. Two Papers

### Paper 1: 감정 표상의 구조 (Horikawa 중심)

> "뇌의 감정 표상은 어떤 구조를 가지며, AI/행동 표상과 어떻게 다른가?"

| Method | 출처 (original field) | 감정 적용 시 RQ | Horikawa 적용 |
|--------|--------------------|----------------|---------------|
| **GW-OT** (Gromov-Wasserstein Optimal Transport) | 계산 기하학 → Neuro toolbox 2025 | 뇌-AI-행동 감정 기하의 구조적 대응은? 어디서 왜곡? | 3개 distance matrix (brain/stim/behav) × GW alignment |
| **SAE** (Sparse Autoencoder) | LLM interpretability (Anthropic 2024) | 뇌는 감정을 discrete code로 표상하나, sparse superposition으로 표상하나? 어떤 감정이 pure/compound? | fMRI (2185×450) → overcomplete sparse features → monosemantic 분석 |
| **CBM** (Adaptive Concept Bottleneck Model) | Interpretable ML (ICLR 2025) | stimulus→brain 변환을 매개하는 interpretable concept은? | V-JEPA2 → concept layer → brain/emotion prediction |
| **RepE** (Representation Engineering / Steering Vectors) | LLM safety (Zou 2023) | brain emotion space에 감정 방향 벡터 존재하나? 벡터 산술 성립? | brain latent → direction extraction → arithmetic test |

**흐름:**
```
GW-OT (macro: 3축 전체 구조 비교)
  → SAE (micro: brain emotion의 atomic features)
  → CBM (pathway: stimulus→brain 매개 concept)
  → RepE (geometry: emotion space 방향/산술)
```

**핵심 reference 대비 positioning:**

| 선행연구 | 그들이 한 것 | 우리가 다르게 하는 것 |
|---------|-----------|-------------------|
| Horikawa 2020 | Unsupervised clustering → 27 discrete emotion clusters | SAE → superposition (compound) 표상 발견 가능 |
| Conwell 2025 (Perceptual Primacy) | Affectless vision models → 50-73% affect 설명 | GW-OT로 "설명 안 되는 부분의 구조" characterize |
| Sartzetaki 2025 (ICLR 99 models) | 99 model RSA benchmark on Horikawa | 우리는 RSA를 넘어 GW-OT로 매핑 구조 자체를 분석 |
| Du 2025 (MLLM) | MLLM > self-report for brain geometry | CBM으로 "왜" — 매개 concept 식별 |
| Gao 2025 (Objects drive emotion) | Object model > emotion model | CBM이 object-level concept의 역할 직접 정량화 |
| Lee 2025 (Awe) | CEBRA로 awe의 ambivalent 표상 | SAE로 전체 34 감정의 pure/compound 체계적 분류 |

### Paper 2: 감정 표상의 역학 (Emo-FilM 중심)

> "영화 시청 중 뇌의 감정 상태는 어떤 dynamical landscape를 따르는가?"

| Method | 출처 | RQ |
|--------|-----|-----|
| **BCNE** (Brain-dynamic CNN Embedding) | Nature Comp Sci 2025 | 감정 manifold의 topology — discrete cluster인가 continuous gradient인가? |
| **Neural ODE** | Dynamical systems + DL | 감정 전환의 dynamics — attractor, trajectory, bifurcation |

**흐름:**
```
BCNE: fMRI 시계열 → emotion state manifold 추출
  → Neural ODE: manifold 위에서 dynamics 모델링
  → attractor map + trajectory + phase portrait
```

---

## 5. Datasets

| Dataset | 역할 | 특징 |
|---------|------|------|
| **Horikawa** | Paper 1 메인 | 5 subj, 2185 videos, 34 cat + 14 dim, vision/semantic features |
| **Emo-FilM** | Paper 2 메인 + Paper 1 validation | 30 subj, 2.5h continuous, 본인 rating, component-process annotation |
| **Algonauts 2025 / CNeuroMod** | 선택적 generalization | 80h movies, 4 subj, TRIBE benchmark과 직접 비교 가능 |

---

## 6. 핵심 방법론 reference

| Method | Primary reference |
|--------|------------------|
| GW-OT | Thual et al. (2025) Toolbox, J Neurosci Methods; Peyré et al. (2019) Computational OT |
| SAE | Bricken et al. (2023) Anthropic "Towards Monosemanticity"; Gao et al. (2024) OpenAI scaling SAEs |
| CBM | Koh et al. (2020) ICML; Adaptive CBM (ICLR 2025) |
| RepE | Zou et al. (2023) "Representation Engineering" |
| BCNE | Zhou et al. (2025) Nature Computational Science |
| Neural ODE | Chen et al. (2018) NeurIPS; torchdiffeq |

fMRI 선행:
| Reference | 역할 |
|-----------|------|
| Brain Algebra (Comms Bio 2025) | fMRI compositionality 선례 (SAE 연결) |
| DeepCor (Nature Methods 2025) | Autoencoder on fMRI 선례 |
| Arousal as universal embedding (Nature 2025) | Brain dynamics + behavior 선례 |
| Mathis et al. (Nature Rev Neurosci 2025) | Joint brain-behavior modeling 리뷰 |

---

## 7. Video model rationale (상세)

V-JEPA2 선택 이유:
1. Self-supervised (no label bias) — 감정 label 없이 학습 → 감정에 대한 가정 없음
2. 32 layers → layer-wise hierarchy analysis 가능 (Conwell 2025 스타일)
3. 1M hours internet video → naturalistic stimulus에 최적화
4. Physical reasoning (motion, object permanence) → emotion primitive (looming, approach) 포착
5. Open-source (Meta, GitHub facebookresearch/vjepa2)

CLIP 추가 이유:
1. Vision + language alignment → semantic 정보 포함
2. V-JEPA2 (no language) vs CLIP (with language) 비교 → "언어가 감정 표상에 기여하는가?"

---

## 8. Central question — 미확정

현재 thesis의 central question은 정제 중.

후보:
- "뇌의 감정 표상은 어떤 구조(structure)와 역학(dynamics)을 가지며,
   이는 시각 자극 표상 및 행동적 감정 경험과 어떻게 대응하는가?"

이 질문이 아직 "dataset에서 짜낸" 느낌. 연구자 본인의 genuine curiosity와
연결되는 sharper version을 찾는 중.

핵심 tension:
- "내가 진짜 궁금한 게 뭔가?"
- 감각-감정 변환에 관심 있음
- Hierarchical processing에 관심 있음
- Brain-specific emotion의 정체에 관심 있음
- 하지만 이것들이 아직 하나의 question으로 수렴하지 않음

→ 다음 단계: RQ 정제 대화 필요.

---

## 9. Timeline (2개월, 2026-04-15 기준)

### Paper 1 (Horikawa)
```
Week 1-2: V-JEPA2 layer-wise feature 추출 + GW-OT 구현
Week 3:   SAE 구현 + sparse feature 분석
Week 4:   CBM 구현 + concept 식별
Week 5:   RepE analysis on latent space
Week 6:   Cross-method integration + figures
Week 7:   Writing
```

### Paper 2 (Emo-FilM)
```
Week 1-2: Emo-FilM data download + preprocessing + embedding 추출
Week 3-4: BCNE manifold extraction
Week 5:   Neural ODE on manifold
Week 6:   Integration + figures
Week 7:   Writing
```

두 Paper 병렬 진행 가능하되, Paper 1 우선.

---

## 10. 요약

```
Thesis = "뇌의 감정 표상: 구조와 역학"

Paper 1 (Horikawa): 구조 — GW-OT + SAE + CBM + RepE
  → 3축 대응, superposition, concept 매개, 기하학

Paper 2 (Emo-FilM): 역학 — BCNE + Neural ODE
  → manifold, attractor, trajectory, dynamics

모든 방법론은 "다른 분야에서 가져와 감정 뇌과학 첫 적용"
모든 분석은 "Brain × Behavior × Stimulus 3축" 위에서 진행
```

---

*v1 — 2026-04-15. RQ refinement pending.*
