# Setup: Data Readiness And First Baselines

`setup`은 최종 논문 번호가 아니라, NetFeeliX의 첫 번째 실행 준비 공간입니다.

목적은 간단합니다.

```text
dataset과 target이 실제로 준비되는지 확인하고,
SwiFT를 포함한 첫 baseline을 돌릴 수 있는 상태를 만든다.
```

## 왜 `setup`이 필요한가?

NetFeeliX는 문헌/전략만으로 진행할 수 없습니다. fMRI dataset은 접근 방식,
preprocessing, timing, target annotation이 모두 다르기 때문에, 가장 먼저
"실제로 돌아가는 최소 실험 단위"가 필요합니다.

`setup`은 그 역할을 합니다.

## Scope

`setup`에서 다루는 것:

- dataset local path 확인
- fMRI shape, TR, timing 확인
- target matrix 생성
- train/validation/test split 정의
- ROI/parcel ridge baseline
- dynamic FC baseline
- frozen SwiFT feature baseline
- stimulus-only baseline이 쉬운 경우만 추가

`setup`에서 아직 하지 않는 것:

- 대규모 naturalistic movie/story pretraining
- full 4D SwiFT continued pretraining
- 복잡한 TRIBE-SwiFT dual encoder
- affective LLM/VLM brain-tuning

## Candidate Datasets

| Dataset | First use |
|---|---|
| Horikawa / Cowen | high-dimensional emotion vector baseline |
| Emo-FilM | component/appraisal target readiness |
| Affective Videos | arousal/valence sanity check |
| IAPS fMRI NeuroVault | beta-map valence category check |
| HCP 7T movie | first naturalistic pretraining-readiness check |
| CNeuroMod / StudyForrest / Narratives | later alignment, long-context, or language-context readiness only |

## Folder Rules

```text
setup/
├── code/       # runnable scripts
├── data/       # derived metadata, target matrices, split files
├── logs/       # stdout/stderr/logs
└── results/    # tables, metrics, reports, figures
```

Rules:

- raw datasets should not be copied into this repo.
- derived metadata can go in `setup/data/`.
- metrics and plots go in `setup/results/`.
- logs go in `setup/logs/`.
- scripts go in `setup/code/`.

## First Scripts To Create

| Script | Purpose |
|---|---|
| `build_dataset_availability.py` | scan local paths and write availability table |
| `build_target_matrices.py` | create target matrices for available datasets |
| `run_roi_baselines.py` | ridge/elastic-net on ROI or parcel features |
| `extract_swift_features.py` | frozen SwiFT feature extraction |
| `run_swift_probe.py` | linear/MLP head on frozen SwiFT features |
| `check_bfm_readiness.py` | fresh BFM code/checkpoint/output readiness check |
| `prepare_horikawa_bfm_fresh_extraction.py` | write fresh extraction commands under `setup/jobs/` |
| `run_horikawa_bfm_benchmark.py` | Horikawa BFM benchmark wrapper using fresh embeddings only |
| `summarize_tribe_progress.py` | TRIBE Horikawa output progress report |
| `summarize_horikawa_bfm_results.py` | fresh Horikawa BFM result table |

## First Outputs

| Output | Path |
|---|---|
| dataset availability table | `setup/results/dataset_availability.md` |
| target construction report | `setup/results/target_construction.md` |
| split metadata | `setup/data/splits/` |
| baseline metrics | `setup/results/baseline_metrics.csv` |

## Decision Rule

`setup` should answer:

1. Which datasets are actually runnable now?
2. Which emotion targets are clean enough to use?
3. Does frozen SwiFT beat or match simple baselines?
4. Is the next investment SwiFT adaptation, naturalistic pretraining, or
   TRIBE-SwiFT alignment?
