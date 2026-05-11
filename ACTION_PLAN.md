# NetFeeliX 실행 계획

이 문서는 현재 해야 할 일을 한글로 정리한 active action plan입니다. 완성된 논문
개요는 `Paper/framework_KR.md`, 방법론은 `Paper/methodology.md`, 데이터/모델
상세 reference는 `reference/`에 둡니다.

## 0. 핵심 원칙

NetFeeliX의 목표는 SwiFT를 무조건 살리는 것도, benchmark table 하나를 만드는
것도 아닙니다. 목표는 **emotion representation을 잘 담아내는
emotion-specific brain foundation model / brain model을 개발하는 것**입니다.

따라서 운영 원칙은 다음입니다.

1. SwiFT-first지만 SwiFT-locked는 아니다.
2. old EmoDe cache는 참고만 하고, 새 실험은 canonical manifest에서 다시 시작한다.
3. Horikawa/Cowen 기준은 `2185` stimuli다.
4. 모든 모델은 같은 target, split, metric에서 비교한다.
5. prediction 성능뿐 아니라 어떤 neural representation이 중요한지도 본다.
6. 먼저 Brain Foundation Model benchmark를 넓게 돌려 search space를 줄이고,
   그 다음에 pretraining/adaptation branch와 multimodal framework branch를
   실험한다.

## 0.5 Benchmark-first 운영 방식

NetFeeliX는 먼저 benchmark에 실제로 올라갈 항목만 깔끔하게 정렬합니다. 이 단계는
최종 목적이 아니라, 이후 큰 model-development search를 위한 empirical gate입니다.
전체 benchmark 공간은 다음 3축입니다.

```text
Dataset x BFM x Task
```

중요한 구분:

- `Dataset axis`에는 emotion/affect downstream benchmark dataset만 넣는다.
- `Model axis`에는 현재 benchmark에서 평가할 Brain Foundation Model만 넣는다.
- `Task axis`에는 예측할 target/task type만 넣는다.
- HCP, CNeuroMod, StudyForrest, Narratives 같은 movie/story fMRI는 지금
  emotion benchmark dataset이 아니라, benchmark 이후의 pretraining/alignment
  resource로 따로 관리한다.
- video/audio/text model, TRIBE, stimulus-only baseline은 현재 BFM benchmark가
  끝난 뒤의 control/extension으로 둔다.
- adapter, fine-tuning, modality fusion, pretraining objective는 Model axis가
  아니라 benchmark 이후 선택할 strategy다.

### 세부 설명 위치

`ACTION_PLAN.md`는 실행 순서만 담습니다. Dataset/model/task의 자세한 설명은
아래 문서가 canonical source입니다.

| 항목 | 자세한 설명 |
|---|---|
| Dataset 특징, target, risk, source | `reference/datasets.md` |
| BFM/model 특징, input, risk, source | `reference/code_resources.md`, `reference/papers.md` |
| Task 정의와 metric | `reference/task.md` |
| 전체 master matrix | `notes/benchmark_design.md` |
| benchmark 이후 training/adaptation 전략 | `reference/training_strategy.md` |

### Dataset axis

| Tier | Dataset | 첫 역할 |
|---|---|---|
| P0 | Horikawa/Cowen | high-dimensional affect geometry, valence/arousal sanity |
| P0/P1 | Emo-FilM | naturalistic component/appraisal downstream |
| P1 | Affective Videos, IAPS fMRI | fast valence/arousal/category sanity |
| P2 | NeuroEmo, Koide-Majima, REELMO / Jojo Rabbit fMRI | expansion/transfer benchmark |

### Model axis

현재 benchmark의 model axis는 Brain Foundation Model입니다.

| Model | 역할 |
|---|---|---|
| SwiFT | primary brain foundation model |
| Brain-JEPA | alternative brain foundation model |
| NeuroSTORM | alternative 4D brain foundation model |
| BrainLM | alternative time-series brain foundation model |

최소 통계 baseline은 floor로만 둡니다.

| Baseline | 역할 |
|---|---|
| logistic regression | binary/multiclass floor |
| ridge regression | regression/vector floor |
| ROI/voxel ridge | simple brain-feature floor |

현재 benchmark 밖에 두는 model/resource:

| Later model/resource | 나중 역할 |
|---|---|
| V-JEPA2, VideoMAE, CLIP | stimulus-only visual control |
| Whisper/Wav2Vec | stimulus-only audio control |
| text encoder / LLM embedding | stimulus-only language control |
| TRIBE v2 | stimulus-to-brain teacher/alignment branch |

### Task axis

| Family | 예시 | 첫 metric |
|---|---|---|
| binary classification | high/low valence, high/low arousal | AUROC, balanced accuracy |
| regression | arousal, valence, dominance | Pearson/Spearman, MAE/MSE |
| multiclass classification | positive/neutral/negative, discrete emotion | macro F1, balanced accuracy |
| multi-label/vector | emotion distribution, 34D emotion score | mean correlation, macro AUROC |
| dynamic/component | binned affect trajectory, appraisal/component | CCC/correlation |

### 소거 원칙

1. 먼저 `Dataset x BFM x Task` master matrix를 만든다.
2. 각 조합마다 target, split, metric, statistical floor, BFM score를 채운다.
3. statistical floor보다 약한 BFM은 tuning 전에 window, pooling, split을 먼저 점검한다.
4. SwiFT가 다른 BFM보다 좋으면 SwiFT adaptation branch를 유지한다.
5. frozen/generic BFM이 부족하면 task-fMRI/movie-fMRI pretraining, loss term,
   adapter/fine-tuning strategy를 실험한다.
6. brain-only 결과만으로 emotion representation이 부족하거나 stimulus shortcut
   통제가 필요하면 multimodal framework branch로 간다: TRIBE-like alignment,
   video/audio/text feature injection, late fusion, joint latent를 비교한다.
5. 다른 BFM이 SwiFT보다 좋으면 SwiFT-first 가정을 축소한다.
6. high-dimensional/component task에서 이기는 BFM을 main branch 후보로 올린다.
7. BFM benchmark 이후에야 stimulus-only, modality 추가, TRIBE alignment를 control/extension으로 진행한다.

## 1. 현재 정리된 파일 구조

### scripts

`scripts/`는 project-operation automation만 둡니다.

| 파일 | 역할 |
|---|---|
| `scripts/check_md_completeness.py` | 문서 구조와 stale reference 검사 |
| `scripts/build_project_status.py` | generated status 작성 |
| `scripts/generate_experiment_cards.py` | experiment card 생성 |

### setup/code

실행성 setup script는 `setup/code/`에 둡니다.

| 파일 | 역할 |
|---|---|
| `setup/code/build_horikawa_window_manifest.py` | Horikawa canonical 2185 stimulus window manifest 생성 |
| `setup/code/run_tribe_horikawa.py` | TRIBE v2를 Horikawa stimulus에 적용 |
| `setup/code/run_tribe_horikawa.sh` | TRIBE v2 batch 실행 wrapper |

## 2. Canonical Data 기준

### Horikawa / Cowen

현재 첫 기준 dataset입니다.

| 항목 | 결정 |
|---|---|
| canonical stimulus count | `2185` |
| subjects | `sub-01` to `sub-05` |
| canonical subject-stimulus rows | `10925` |
| local extra rows | stimulus `2186-2196`, project 기준에서는 제외 |
| window length | observed 5-47 frames |
| 역할 | high-dimensional affect geometry benchmark |

실행:

```bash
python3 setup/code/build_horikawa_window_manifest.py
```

산출물:

- `setup/data/horikawa_window_manifest.csv`
- `reports/status/horikawa_window_manifest_summary.json`

### 다음으로 확인할 dataset

| Dataset | 우선 역할 | 먼저 확인할 것 |
|---|---|---|
| Emo-FilM | component/appraisal/naturalistic emotion downstream | access, annotation timing, fMRI format, windowing |
| Affective Videos | arousal/valence sanity benchmark | OpenNeuro format, TR/event timing, target |
| IAPS fMRI | positive/neutral/negative beta-map check | NeuroVault map format, subject-level split |
| HCP 7T movie | naturalistic pretraining | local path, TR, run metadata, parcel/volume format |
| CNeuroMod / Algonauts | multimodal alignment | stimulus feature/timing/fMRI alignment |
| StudyForrest | long-movie continuity | film timing, preprocessing, subject count |
| Narratives | language/story context | transcript timing, fMRI format |
| 101 Dalmatians | modality control | visual-only/audio-only/audiovisual condition |
| NeuroEmo / REELMO / Koide-Majima | emotion-labeled expansion | access, target type, REELMO Jojo Rabbit-only fMRI availability |

## 3. Target 설계

처음부터 하나의 emotion label만 맞히면 안 됩니다. Target ladder를 둡니다.

| Level | Target | Dataset |
|---|---|---|
| sanity | arousal, valence, dominance regression | Horikawa, Emo-FilM, Affective Videos |
| category | positive/neutral/negative, discrete emotion | IAPS, Affective Videos, NeuroEmo |
| rich geometry | 34D or high-dimensional emotion vector | Horikawa, Koide-Majima |
| multi-label | multi-emotion presence/probability | Horikawa labels, Emo-FilM |
| temporal | time-resolved affect trajectory | Emo-FilM, REELMO |
| component/appraisal | appraisal/component ratings | Emo-FilM |
| stimulus reasoning | cue, cause, rationale embedding | REELMO, MLLM-derived targets |

필수 metric:

- regression: Pearson r, Spearman r, MAE, MSE.
- binary/category: balanced accuracy, macro F1, AUROC.
- multi-label: macro/micro F1, macro AUROC.
- high-dimensional: mean correlation, RSA/CKA with emotion-rating geometry,
  retrieval accuracy.
- transfer: held-out subject, held-out stimulus, held-out dataset.

## 4. Neural Representation Search

이게 가장 중요합니다. Whole-brain 4D가 항상 최선이라는 가정은 버립니다.

### 4.1 기본 ROI / Parcel 후보

첫 ROI 기준은 기존 Brain-JEPA preprocessing과 맞추기 위해 다음을 우선합니다.

| 후보 | 이유 | 사용 |
|---|---|---|
| Schaefer 400 | 안정적 cortical parcel, Yeo network label 가능 | default cortical ROI |
| Tian subcortex 50/54 | amygdala, hippocampus, thalamus, striatum 등 포함 | default subcortical ROI |
| Schaefer 600 | 더 세밀한 cortical parcel | 400이 너무 coarse할 때 |
| HCP-MMP 360 | functional/anatomical cortical map | secondary validation |
| Harvard-Oxford / AAL | 접근성 좋은 anatomical ROI | 빠른 sanity check |

첫 default는:

```text
Schaefer 400 cortical parcels + Tian subcortical parcels
```

이유:

- 이미 Brain-JEPA 쪽에서 유사한 ROI 구조를 사용했습니다.
- subject 간 harmonization이 쉽습니다.
- whole-brain voxel보다 빠르게 baseline을 만들 수 있습니다.
- cortical/subcortical 분리를 볼 수 있습니다.

### 4.2 Network-restricted 분석

ROI 전체를 한 번에 쓰는 것만으로는 어떤 system이 중요한지 알 수 없습니다.
따라서 network group별 모델을 따로 돌립니다.

| Network group | 포함 후보 | 가설 |
|---|---|---|
| visual | early visual, higher visual, ventral temporal | Horikawa short video emotion은 visual feature가 강할 수 있음 |
| auditory | auditory cortex, superior temporal | movie/audio cue, speech/prosody 관련 |
| salience | insula, ACC, midcingulate | arousal, bodily salience, affective relevance |
| limbic/subcortical | amygdala, hippocampus, striatum, thalamus, hypothalamus 가능 시 | valence, memory/context, reward/threat |
| DMN | mPFC, PCC/precuneus, angular gyrus | narrative, social/context appraisal |
| frontoparietal/control | dlPFC, IPL, control network | appraisal, regulation, task/control signal |
| attention | dorsal/ventral attention | stimulus salience and orienting |
| somatomotor | motor/somatosensory | action, bodily expression, arousal confound |

각 network마다 같은 모델을 돌립니다.

```text
network ROI time series -> ridge/elastic-net/MLP -> emotion target
```

산출물:

- target별 best network.
- arousal만 잘 맞히는 network vs high-dimensional emotion geometry를 맞히는 network.
- stimulus-only feature와 겹치는 sensory shortcut 여부.

### 4.3 Voxel-weighted 분석

ROI 평균이 signal을 잃을 수 있으므로 voxel weighting도 봅니다.

우선순위:

1. gray-matter mask 안의 voxel만 사용.
2. subject별 variance/coverage가 너무 낮은 voxel 제거.
3. ridge regression으로 전체 voxel baseline.
4. elastic-net 또는 sparse linear model로 sparse voxel contribution 확인.
5. fold별 coefficient stability를 계산.
6. 가능하면 searchlight나 cluster-level summary로 확장.

주의:

- voxel weight는 해석을 과하게 하지 않습니다.
- fold와 subject에 걸쳐 안정적인 voxel/network만 중요하다고 봅니다.
- prediction이 좋아도 motion/visual shortcut일 수 있으므로 stimulus feature control이 필요합니다.

### 4.4 Dynamic Connectivity

Emotion, 특히 arousal은 local activation보다 connectivity에 더 잘 잡힐 수 있습니다.

후보:

- sliding-window FC.
- ROI graph feature.
- CPM-style feature selection.
- temporal graph summary.
- arousal/valence regression first.

사용 기준:

- arousal은 FC가 강하고 valence/high-dimensional target은 약한지 확인.
- movie/naturalistic dataset에서 더 중요할 가능성이 큽니다.

## 5. Model 비교

### 5.1 Simple Brain Baselines

먼저 이것들이 돌아가야 합니다.

| Model | Input | 목적 |
|---|---|---|
| ridge | ROI/parcel, voxel | minimum linear baseline |
| elastic-net | voxel/ROI | sparse importance |
| MLP | ROI/parcel | nonlinear sanity |
| temporal MLP/TCN | ROI time window | temporal baseline |
| dynamic FC | ROI time series | arousal/context dynamics |

### 5.2 SwiFT

SwiFT는 먼저 제대로 확인합니다.

조건:

- pretrained-native SL20/SL40.
- standardized SL5/SL10/SL20/SL40.
- all observed windows.
- frozen feature + linear/ridge/MLP.
- adapter/subject adapter/affective token/multi-task head.
- scratch SL5/10/20/40.

Exit rule:

- ROI/voxel/network baseline보다 약하면 SwiFT 중심 개발 축소.
- arousal만 맞히고 high-dimensional target을 못 맞히면 target-specific head 또는 다른 representation으로 pivot.
- padding/SL sensitivity가 너무 크면 SwiFT temporal path를 재설계하거나 폐기.

### 5.3 Alternative BFMs

| Model | 역할 | 주의 |
|---|---|---|
| Brain-JEPA | ROI/time-series predictive representation | mask가 실제로 쓰이는지 확인 |
| NeuroSTORM | raw 4D fMRI BFM comparison | padding/pooling sensitivity 확인 |
| BrainLM | time-series BFM reference | weight/code availability 확인 |

### 5.4 Benchmark 이후: Stimulus-only / Alignment

이 branch는 현재 BFM benchmark가 끝난 뒤 진행합니다. 지금 단계에서는
Dataset x Brain Foundation Model x Task를 먼저 고정합니다.

이후 BFM 결과를 해석하려면 stimulus-only가 필요할 수 있습니다.

| Component | Feature |
|---|---|
| video | V-JEPA2, VideoMAE, CLIP frame |
| audio | Wav2Vec-BERT, Whisper, spectrogram |
| text | subtitle/caption/LLM embedding |
| TRIBE v2 | predicted cortical response, multimodal latent |

비교:

1. stimulus-only -> emotion.
2. fMRI-only -> emotion.
3. stimulus + fMRI late fusion.
4. contrastive alignment.
5. TRIBE-predicted brain response -> emotion.
6. fMRI latent aligned to stimulus latent -> emotion.

## 6. Pretraining 전략

Pretraining은 세 갈래로 비교합니다.

| Strategy | Data | Question |
|---|---|---|
| naturalistic SSL | HCP, CNeuroMod, StudyForrest, Narratives | stimulus-locked brain dynamics가 emotion transfer를 돕는가 |
| emotion-labeled supervised/weak supervised | Horikawa, Emo-FilM, Affective Videos, IAPS, NeuroEmo | target-aware affect structure가 transfer를 돕는가 |
| two-stage | naturalistic -> emotion-labeled | dynamics 먼저, emotion specialization 나중이 좋은가 |

Objective 후보:

- masked fMRI segment modeling.
- temporal contrastive learning.
- JEPA/future latent prediction.
- subject-invariant contrastive learning.
- stimulus-conditioned fMRI prediction.
- multi-task emotion label/vector/component prediction.
- emotion geometry alignment loss.

평가:

- Horikawa -> Emo-FilM.
- Emo-FilM -> Horikawa.
- mixed emotion dataset -> held-out emotion dataset.
- arousal-only gain인지 high-dimensional/component gain인지 분리.

## 7. 즉시 할 일

### Step 0. Benchmark contract 확정

- [ ] `notes/benchmark_design.md`의 Dataset x BFM x Task master matrix 확정.
- [ ] 각 cell을 `RUN`, `CHECK`, `NA`로 표시.
- [ ] HRF lag/window alignment 정책 결정.
- [ ] variable duration -> all observed, SL5, SL10, SL20, SL40 변환 정책 결정.
- [ ] primary split을 LOSO로 정의하고 stimulus/movie split control을 추가.
- [ ] normalization 정책 결정: subject-wise z-score, min-max, global scaling 비교 여부.
- [ ] noise ceiling 계산 가능 조건 정의.
- [ ] pooling 정책 결정: mean, late-frame, temporal/attention pooling.
- [ ] first result table schema 확정: `Dataset | BFM | Task | Target | Split | Metric | Statistical floor | BFM score | Status | Decision`.

### Step 1. Horikawa manifest 확정

- [ ] `setup/code/build_horikawa_window_manifest.py` 실행.
- [ ] `setup/data/horikawa_window_manifest.csv` 확인.
- [ ] frame length distribution 확인.
- [ ] SL5/10/20/40 condition manifest를 파생할지 결정.

### Step 2. Target matrix 생성

- [ ] Horikawa arousal/valence/dominance regression target.
- [ ] Horikawa binary/category target.
- [ ] Horikawa 34D score target.
- [ ] Horikawa multi-label target.
- [ ] missing label handling rule.
- [ ] subject/stimulus split rule.

### Step 3. ROI/parcel baseline

- [ ] Schaefer 400 + Tian subcortex preprocessing 확인.
- [ ] per-stimulus window summary 생성: mean, late-window mean, slope, max.
- [ ] ridge/elastic-net baseline.
- [ ] network-restricted baseline.
- [ ] subject-wise result table.

### Step 4. Voxel baseline

- [ ] gray-matter mask 결정.
- [ ] voxel variance/coverage filtering.
- [ ] ridge baseline.
- [ ] elastic-net/sparse baseline.
- [ ] coefficient stability map.

### Step 5. Temporal and FC baseline

- [ ] SL5/10/20/40 ROI window input.
- [ ] temporal MLP/TCN.
- [ ] dynamic FC arousal/valence baseline.
- [ ] compare local activation vs FC.

### Step 6. SwiFT smoke test

- [ ] checkpoint-native SL 확인.
- [ ] input shape, padding, window attention config 확인.
- [ ] frozen feature extraction smoke test.
- [ ] SL sensitivity test.
- [ ] simple baseline보다 좋은지 확인.

### Step 7. Alternative BFM smoke test

- [ ] Brain-JEPA ROI input and mask path 확인.
- [ ] NeuroSTORM padding/pooling 확인.
- [ ] BrainLM availability 확인.
- [ ] 동일 target/split으로 비교 가능하게 정리.

### Deferred. TRIBE/stimulus branch

BFM benchmark 이후에 진행합니다.

- [ ] `setup/code/run_tribe_horikawa.sh` 경로 확인.
- [ ] Horikawa 2185 stimuli 전체 coverage 확인.
- [ ] TRIBE predicted brain response summary.
- [ ] stimulus-only emotion baseline.
- [ ] fMRI latent와 TRIBE/stimulus latent alignment 후보 정의.

### Step 9. Decision table 작성

최소 table:

| Axis | Best candidate | Evidence | Decision |
|---|---|---|---|
| arousal | TBD | metric | keep/pivot |
| valence | TBD | metric | keep/pivot |
| 34D emotion | TBD | metric | keep/pivot |
| component/appraisal | TBD | metric | keep/pivot |
| cross-dataset transfer | TBD | metric | keep/pivot |
| interpretability | TBD | stable region/network | keep/pivot |

### Step 10. Model-development 방향 결정

가능한 결론:

1. SwiFT가 좋다 -> SwiFT adapter/pretraining 확장.
2. ROI/voxel/network가 더 좋다 -> neural representation model 중심으로 pivot.
3. stimulus-only가 강하다 -> stimulus-brain residual/alignment 중심.
4. Brain-JEPA/NeuroSTORM이 더 좋다 -> alternative BFM adaptation.
5. 모든 brain model이 약하다 -> target timing/preprocessing/label quality 재검토.

## 8. 당장 만들면 좋은 산출물

- `setup/data/horikawa_window_manifest.csv`
- `setup/data/horikawa_target_matrix.*`
- `setup/data/horikawa_splits.*`
- `setup/results/roi_baseline_results.*`
- `setup/results/voxel_baseline_results.*`
- `setup/results/network_ablation_results.*`
- `setup/results/swift_smoke_test_report.*`
- `setup/results/tribe_horikawa_coverage.*`
- `reports/status/first_signal_report.md`
- `reports/status/model_direction_decision.md`

## 9. 성공 기준

2개월 안에 완성 모델을 만드는 것이 아니라, 다음을 결정할 수 있으면 성공입니다.

1. 어떤 dataset/target이 실제로 runnable한가.
2. emotion signal이 ROI/voxel/network/fMRI model 중 어디에 있는가.
3. SwiFT를 계속 밀 가치가 있는가.
4. pretraining은 naturalistic, emotion-labeled, two-stage 중 무엇이 유망한가.
5. TRIBE/stimulus model이 brain representation을 개선하거나 해석하는 데 도움이 되는가.
6. 최종 논문 방향이 model development인지, neural representation discovery인지, stimulus-brain alignment인지 정해지는가.
