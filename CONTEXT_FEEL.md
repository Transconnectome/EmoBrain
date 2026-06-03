# FEEL Compact Context

Agent / 협업자가 빠르게 참조할 single source of truth. 자세한 내용은 각 reference 파일.

## 정체성

**FEEL** = Foundation Model for Emotion Embedding Learning (내부 / repo / 연구실 정체성 이름).
**Paper title** = "Universal Emotion Code in Naturalistic Brain Data" 또는 "Transferable Emotion Brain Foundation Model" (Bommasani 2021 의 FM 정의 scale 미달 + reviewer negativity bias 회피, naming dual-track).

## Big Question (v4 final, 2026-06-02)

> Brain 에 paradigm, label taxonomy, subject 의 surface variation 을 가로지르는 *universal emotion code* 가 존재하는가? Multi-source naturalistic emotion fMRI 의 adaptation 으로 그 universal code 를 학습하고 검증할 수 있는가?

핵심 scientific bet. Wager-style universal pain signature 시도의 emotion 판. Affective neuroscience 의 미해결 질문 (universal vs idiosyncratic emotion representation) 에 falsifiable 한 evidence 제공.

이 프로젝트는 emotion theory paper 가 아니라 **universal emotion code 의 존재 검증을 위한 model-development project**. "Brain 이 video 를 이겨야" 전제 없음 (Phase 1-2 결과로 falsified, group-level V/A 는 video 가 saturate).

## Sub-claims (falsifiable)

- (사실 claim 1) Universal emotion code 가 존재한다면, multi-source pretrain (Horikawa + Emo-FilM + StudyForrest + Affective Videos) 의 representation 이 single-source pretrain 보다 cross-dataset transfer 에서 의미 있게 더 invariant 해야 한다.
- (사실 claim 2) Universal code 는 brain 의 특정 ROI / network 에 localize 되어야 한다 (Cowen 2020 transmodal 가설과 align 또는 disagree).
- (사실 claim 3) Universal code 는 subject-invariant SSL 학습 후 같은 stim 의 다른 subject 의 representation 이 alignment 되어야 한다.
- (Null) Universal code 가 없으면 multi-source pretrain 의 invariance 이득 = 0, subject-invariant SSL 의 alignment 이득 = 0, cross-dataset transfer 도 acquisition floor 수준. 이 경우 negative result 자체가 paper.

## 2 Main Track + 1 Supplementary (각 track 이 다른 angle 에서 universal code triangulate)

| Track | 답하는 sub-Q | Universal code 측정 방식 | 자원 |
|---|---|---|---|
| **Track A (main). BFM SSL pretrain + LoRA adaptation** | Multi-source SSL pretrain 이 emotion-relevant invariance 를 emerge 시키는가? Subject-invariant / multi-source / stimulus-contrastive SSL 의 marginal contribution? | Pretrain 후 representation 의 cross-dataset invariance metric (RSA preservation, ROI-wise transfer) | GPU 1-2 주 |
| **Track B (main). Brain+Video framework (Phase 2 reuse + task 재설계)** | Brain unique contribution 의 universal component 가 무엇인가? Video 가 못 잡는 brain emotion variance 의 cross-dataset preservation? | Joint - video baseline = brain unique. 그 brain unique 의 cross-dataset RSA / alignment 측정 | ✅ 이미 학습 코드 |
| **Track C (supplementary). BrainVLM generative path** | Universal code 가 generative 표현 가능한가? Free-form caption / OV label 의 cross-dataset consistency? | Phase 3a fold 1 결과 reporting + inference parsing fix. Supplementary figure 만 | ✅ Fold 1 완료, parsing fix 만 |

**왜 BrainVLM 이 supplementary 인가**. (a) LLM 의 visual semantic bias 가 brain 의 invariance 측정을 가림 (Phase 2 video saturate 와 같은 함정), (b) Generation noise 가 measurement reliability 낮춤, (c) Phase 3a inference 자체 (V_reg r = NaN, MAE 2.55, scale mismatch) 가 약함, (d) Multi-source 확장에 자원 부담 큼. Track C 로 본격 진행하는 건 risk 대비 evidence 약함.

Track A + Track B 의 **converging evidence** 가 paper 의 강점. Universal code 가 (A) SSL invariance 로 emerge AND (B) Brain unique 로 cross-dataset preserve 면 강한 evidence. 한 track 만 positive 도 paper 가능, 둘 다 negative 면 negative result paper.

## Track A 의 SSL pretrain 후보 (5 → 우선순위 명확)

자원 부담 manageable 한 후보. 모두 진행하되 priority 순서.

**우선순위 1 (둘 다 main, 반드시 진행)**

1. **Subject-invariant SSL**. 같은 video 를 본 5 subject 의 brain response 가 서로 비슷해지도록 contrastive 학습.
   - 구체. Stimulus k 를 subject A → brain_Ak. 같은 k 를 subject B → brain_Bk. 다른 stim m → brain_Am. Loss = brain_Ak ↔ brain_Bk 의 cosine ↑, brain_Ak ↔ brain_Am 의 cosine ↓. InfoNCE.
   - Universal code 와의 연결. Subject 간 invariance 가 universal code 의 정의 그 자체. 학습 후 representation 이 subject 간 align 되면 universal code emerge 의 직접 evidence.
   - 자원. GPU 며칠.

2. **Multi-source SSL (masked autoencoder, BrainLM-style)**. Horikawa + Emo-FilM + StudyForrest + Affective Videos 의 fMRI 모두 모음. Brain 의 일부 ROI / time window 를 가리고 예측하도록 학습.
   - 구체. 450 ROI 중 30% 를 가린 후 나머지 70% 로 가린 부분 예측. Loss = MSE. 4 dataset 모두 같은 model 에 input. Dataset 별 헤더 추가.
   - Universal code 와의 연결. Paradigm 간 invariance 의 evidence. Single-source (Horikawa only) vs multi-source pretrain 의 representation invariance 차이가 universal code 의 multi-paradigm 존재 증거.
   - 자원. GPU 1-2 주.

**우선순위 2 (main, 가능하면 진행)**

3. **Brain-stimulus contrastive (TRIBE-style)**. Brain representation 과 video representation (V-JEPA2 / CLIP) 의 alignment.
   - 구체. Brain_k 의 encoder output 과 Video_k 의 V-JEPA2 feature 의 cosine ↑, 다른 stim 과는 ↓. Brain-video pair contrastive.
   - Universal code 와의 연결. Universal code 가 stimulus-driven 이면 alignment 가 자연스럽게 emerge. Brain unique 가 stimulus 와 분리된 axis 면 alignment 안 됨. 두 경우의 분리 측정.
   - 자원. GPU 며칠.

**우선순위 3 (optional, 시간 남으면)**

4. **Curriculum pretrain**. Resting (Brain-JEPA prior, 이미 한 stage) → naturalistic movie SSL (HCP 7T movie) → emotion-aware (Horikawa Cowen) 의 3-stage. 각 stage 의 prior contribution ablation.
5. **Distillation**. 큰 BFM 의 representation 을 작은 specialized model 로 transfer. 부수적, universal code 의 *효율적 표현* 방법.

## Target hierarchy

Task / supervision 은 V/A 특화 아님. New task design 가능 (universal code probe).

| Tier | Target | 비고 |
|---|---|---|
| **Primary** | Cross-dataset emotion-text alignment + Cowen 34-cat multilabel + 14-dim regression + OV description retrieval | Universal code 의 invariance 측정에 직접 |
| **Reference (floor)** | V/A binary + regression | Phase 1-2 에서 video saturate 한 axis 임이 확정. Floor only |

## Cross-dataset evaluation 4 전략

1. **Shared text-embedding zero-shot (main)**. brain → emotion-text space, native label 이름만으로 zero-shot retrieval
2. **Label-space intersection (안전)**. target dataset 의 축만 잘라
3. **MLLM universal annotator**. OV-MER pipeline 의 local LLM (Qwen2.5-72B / Llama-3.3-70B) frozen artifact
4. **Representational alignment (label-free)**. RSA / ISC ceiling

## Independent dataset

| Dataset | Subj × Stim | Label | Role |
|---|---|---|---|
| **Horikawa** | 5 × 2185 (1 min clips) | Cowen 34-cat behavioral consensus | Base / Track A pretrain source / Track B testbed |
| **Emo-FilM** (Cordoni 2025 Nat SciData) | 30 × 14 films (2.5h) | 13 discrete + 42 CPM, 1 Hz | Track A multi-source pretrain + cross-dataset transfer test |
| **StudyForrest** | 20 × Forrest Gump 2h | 8 portrayed emotion + V/A | Track A multi-source pretrain + cross-dataset transfer test |
| **NNDb** (Aliko 2020) | 86 × 10 movies | 없음 (label-free) | 전략 4 RSA (Appendix) |
| **Affective Videos** (ds000205) | 11 × 32×4 | V/A | Track A multi-source pretrain |
| **Koide-Majima** | 옵션 | 80 emotion labels | Track A multi-source pretrain (접근 가능 시) |

## Build recipe (Track A + B 의 공통 backbone)

5 subj × 2185 stim 으로는 emotion brain FM 을 from-scratch pretrain 불가. **대규모 pretrained brain backbone + 소수 multi-source emotion data 의 SSL pretrain + emotion-text space adaptation** 이 honest scope.

```
fMRI ─► 450-ROI parcel (Schaefer-400 + Tian-50, scanner / dataset 무관 substrate)
        │
        ▼ Brain-JEPA backbone (pretrained on ABCD resting)
        │
        ▼ Track A SSL pretrain (multi-source masked + subject-invariant contrastive
                                 + optional brain-stimulus alignment)
        │
        ▼ LoRA adaptation
        │
        ▼ projection
        z_emo ─► frozen emotion-text embedding space (sentence-transformer / CLIP-text)
                  target = embed(Cowen 34-cat + 14-dim 문장화 또는 OV description)
                  loss  = contrastive InfoNCE + 보조 regression + caption baseline delta
        │
        ▼ multi-source pooling
        ▼ 평가 (freeze 후)
            Track A. invariance metric (subject-align, paradigm-align)
            Track B. brain unique cross-dataset RSA (Brain+Video framework reuse)
            Track C. BrainVLM Phase 3a parsing fix (supplementary)
```

## Phase 1-2 측정 결과 (evidence 보존, v4 framing 의 근거)

- **Phase 1 frozen probe**. ROI Schaefer400+Tian50 mean (linear) V_binary AUROC 0.7889 > all BFM (best Brain-JEPA 0.7402) ≫ Video CLIP 0.9708. Brain 정교화가 group-level emotion 에 effect 없음.
- **Phase 2 trained integration**. D late fusion V_binary 0.9718, CLIP-only 0.9708 → Δ = +0.001 (noise). 4 fusion architecture 모두 video baseline 못 넘음. Group-level emotion 의 brain 추가 contribution = 0. **이게 universal code question 의 motivation**. Brain 의 universal code 가 있다면 group-level V/A 가 아닌 *invariance / cross-dataset preservation* 의 axis 에 있어야 함.
- **Phase 3a BrainVLM**. Fold 1 학습 완료 (loss 0.151). Inference V_reg r = NaN (parsing failure), MAE 2.55, scale mismatch. Track C 의 supplementary baseline.

## Critic-informed control (필수, 2 main track + 1 supplementary 공통)

- **Acquisition control**. ComBat (Fortin 2018) + phase-scrambled null + trivial ROI mean null. Transfer Δ > 2σ × max(null) 만 의미.
- **Caption baseline (Doerig 2025 위협 대응)**. Qwen-VL caption → text embedding probe. Brain unique variance = B_joint - B_caption + paired bootstrap p.
- **Naming retreat**. Paper title 에서 "foundation model" 명사 자제, 내부 이름 FEEL 유지.

## Future Extensions (post-submission, v5 candidates)

v4 main 의 universal code 가 first (foundation model 의 generalization 본질). 그 위에 추후 2 extension 으로 brain emotion 의 완전 분해.

```
Brain emotion representation =
    Universal code              (v4 main, Track A priority 1)
  + Context-conditional         (Extension 1, text-based modulation)
  + Individual differences      (Extension 2, subject embedding + residual)
  + Acquisition noise           (control, ComBat)
```

- **Extension 1. Context-aware emotion (text 형식)**. 영화 subtitle / scene caption 의 text embedding 으로 stimulus 의 context modulation 표현. Brain emotion = universal code × context-text modulation. StudyForrest narrative, Emo-FilM 1 Hz continuous rating 으로 측정.
- **Extension 2. Individual differences (subject embedding + residual analysis)**. (a) Subject embedding (TRIBE v2 / Défossez 2023 style) 추가 학습. (b) Track A 의 subject-invariant SSL 의 *non-aligned residual* PCA + subject 별 행동 metric correlation.

Priority. v4 main (6 month 안) = universal code. v5 (post-submission) = Extension 1 + 2. 자세히 `docs/masterplan_v2.md` Section 14.

## Canonical Data

- Horikawa / Cowen stimulus 수 = **2185** (resting 0 제외)
- Horikawa subject = **5명 (sub-01..05)**, 모두 동일 자극 본 fMRI
- Split = stimulus-stratified (V × A quartile) 80/10/10, 같은 자극 → 모든 subject 동일 split
- Independent dataset 다운로드 + sanity check 는 Phase 3b W15

## Canonical 파일

| 파일 | 역할 |
|---|---|
| `README.md`, `README_KR.md` | 사람 entry point (Big Q + 2 track + 1 supp + Phase status) |
| `docs/masterplan_v2.md` | **forward-looking masterplan v4 final** (Big Q + 2 track sub-Q + SSL pretrain 1+2+3 detail + build recipe + 4 cross-dataset 전략 + go-no-go) |
| `reports/phase{1,2}_wrapup/main.pdf`, `reports/phase1_foundation.md` | Phase 1/2 진행 + 결과 PDF |
| `Paper/framework_KR.md`, `framework_EN.md` | canonical narrative |
| `Paper/methodology.md` | canonical 실험 방법 |
| `notes/benchmark_design.md` | Dataset × BFM × Task 매트릭스 디테일 |
| `notes/project_decisions.md` | 영구 decision log (2026-06-02 v4 final 결정 포함) |
| `reference/{datasets, task, papers, code_resources, training_strategy}.md` | 각 axis 별 reference |
| `ACTION_PLAN.md` | v1 legacy 실행 plan |
| `workflows/README.md` | operating workflow 안내 |

## Git workflow

- Branch `v4_20260602_perlmutter` (현재 active). 이 framing 의 모든 작업이 여기에.
- Main 은 paper 단계에서 merge.
- 다른 framing 으로 pivot 필요하면 새 branch 파고 그곳에서 작업. 기존 branch 는 보존.

## 운영 규칙

- Root markdown 새로 만들지 말 것. Narrative 는 `Paper/framework_*.md`, methods 는 `Paper/methodology.md`, 실행은 `docs/masterplan_v2.md` + `reports/phase{N}_*.md`.
- 약어 (BFM / VLM / RSA / CKA / ComBat / W matrix / OV / SSL / JEPA / LoRA) 첫 등장 시 풀어쓰기.
- 통계 vs measured 명확히 분리. Over-claim 금지.
- "Brain 이 video 를 이긴다" framing 금지. v4 는 universal emotion code question.
- Paper-side naming 은 "foundation model" 명사 직접 사용 자제.
- Track A + Track B 의 converging evidence 가 paper 의 강점. 한 track 의 negative result 도 정직 reporting.

## Workflow trigger

| Trigger | 의미 |
|---|---|
| `[deep search]` | literature / code / dataset 검색, reference 업데이트 |
| `[experiment card]` | 아이디어를 구조화된 experiment card 로 |
| `[red team]` | 모델 / 데이터 / 주장 / 계획 비판 |
| `[weekly status]` | decision / change / blocker / next action 요약 |
| `[verification]` | citation / path / completeness / overclaim 검증 |
