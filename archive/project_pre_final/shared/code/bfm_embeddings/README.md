# BFM Embedding Extraction

FEEL Phase 1. Horikawa에서 7 BFM × 2 init × 3 padding 추출.

> 구조 참조: SwiFT_v2 `sample_scripts_phase4/{extract_embedding, new}/` 와 동일 패턴.

---

## 폴더

```
bfm_embeddings/
├── README.md
├── _lib/                          ← Python 추출 코드 (공유)
│   ├── brain_jepa.py
│   ├── neurostorm.py
│   ├── swift.py
│   └── SETTINGS_*.md
├── extract_embedding/             ← per-model 단일 job .sh (1 init + pad + sub)
│   ├── brain_jepa.sh
│   ├── neurostorm.sh
│   ├── swift_UAH_51M_SL20.sh
│   ├── swift_UAH_806M_SL20.sh
│   ├── swift_NewE36_SL20.sh
│   ├── swift_NewE96_SL20.sh
│   └── swift_NewE192_SL20.sh
└── run_full/                      ← per-model 30 runs loop .sh
    ├── README.md
    ├── brain_jepa.sh
    ├── neurostorm.sh
    ├── swift_UAH_51M_SL20.sh
    ├── swift_UAH_806M_SL20.sh
    ├── swift_NewE36_SL20.sh
    ├── swift_NewE96_SL20.sh
    └── swift_NewE192_SL20.sh
```

---

## 사용법

### 단일 job 실행 (디버깅용)

```bash
bash code/bfm_embeddings/extract_embedding/swift_NewE96_SL20.sh resting sub-01 replicate
# 인자: INIT SUBJECT PADDING [SEED] [LIMIT]
```

### 모델 전체 (30 runs) 실행

```bash
bash code/bfm_embeddings/run_full/swift_NewE96_SL20.sh
```

각 wrapper 안에서 `extract_embedding/{model}.sh` 를 30번 호출 (resume 가능, 이미 있는 npz skip).

### 병렬 (4 GPU node)

```bash
salloc -A m4641 -C gpu -q regular -t 8:00:00 --gpus=4 --nodes=1
conda activate /pscratch/sd/s/sjmoon/swift_PTL2
cd /pscratch/sd/s/sjmoon/FEEL

CUDA_VISIBLE_DEVICES=0 bash code/bfm_embeddings/run_full/swift_UAH_51M_SL20.sh   > /tmp/g0.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 bash code/bfm_embeddings/run_full/swift_NewE36_SL20.sh    > /tmp/g1.log 2>&1 &
CUDA_VISIBLE_DEVICES=2 bash code/bfm_embeddings/run_full/swift_NewE96_SL20.sh    > /tmp/g2.log 2>&1 &
CUDA_VISIBLE_DEVICES=3 bash code/bfm_embeddings/run_full/swift_NewE192_SL20.sh   > /tmp/g3.log 2>&1 &
wait
```

---

## 모델 / Output Mapping

| extract & run script (`.sh`) | Internal model | Output prefix | Env |
|---|---|---|---|
| `brain_jepa.sh` |. | `brain_jepa_` | brain-jepa-env |
| `neurostorm.sh` |. | `neurostorm_` | neurostorm_env + gcc-12 |
| `swift_UAH_51M_SL20.sh` | `UAH_P2_51M` | `swift_UAH_51M_SL20_` | swift_PTL2 |
| `swift_UAH_806M_SL20.sh` | `UAH_P3_806M` | `swift_UAH_806M_SL20_` | swift_PTL2 |
| `swift_NewE36_SL20.sh` | `NewUAH_newE36` | `swift_NewE36_SL20_` | swift_PTL2 |
| `swift_NewE96_SL20.sh` | `NewUAH_newE96` | `swift_NewE96_SL20_` | swift_PTL2 |
| `swift_NewE192_SL20.sh` | `NewUAH_newE192` | `swift_NewE192_SL20_` | swift_PTL2 |

---

## 명명 규칙

- 폴더/스크립트: `{family}_{architecture}_SL{seq_len}.sh`
- Output: `project/shared/output/embeddings/{tag}_{init}_pad-{padding}/sub-XX.npz`

향후 모델 추가:
1. `_lib/swift.py` 의 `MODEL_CONFIGS` 에 새 항목 추가 (internal name 정의)
2. `extract_embedding/{new_tag}.sh` 생성 (`swift_NewE96_SL20.sh` 복사 후 수정)
3. `run_full/{new_tag}.sh` 생성 (loop wrapper)

---

## 공통 정책 (FEEL Phase 1)

| 항목 | 결정 |
|---|---|
| Horikawa stimulus 수 | 2,185 canonical |
| Split | V/A quartile multilabel stratified |
| HRF lag | 원 데이터에서 이미 4 s shift + 평균 |
| Atlas (ROI) | Schaefer 400 + Tian S3 50 = 450 |
| 4D Volume | 96×96×96×20 |
| Padding | replicate / zero / mean |
| Init | resting-pretrained / scratch |
| Output | per-stimulus embedding (subject별 npz) |

자세한 settings: `_lib/SETTINGS_brain_jepa.md`, `_lib/SETTINGS_neurostorm.md`, `_lib/SETTINGS_swift_master.md`.
