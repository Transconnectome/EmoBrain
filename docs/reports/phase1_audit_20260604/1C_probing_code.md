# Phase 1 Audit — 1C. Probing code audit (deep)

Date: 2026-06-04
Auditor: Claude (Opus 4.7)
Scope:
- `project/shared/code/probes/run_unified_probe.py` (814 line, BFM probe)
- `project/shared/code/probes/run_video_probe.py` (464 line, video probe)
- `project/shared/code/probes/build_5fold_split.py` (46 line, CV split)
- `project/shared/code/probes/run_chance_baseline.py` (258 line)
- `project/shared/code/probes/extract_roi_features.py` (110 line, Tier 1 ROI)
- `project/shared/code/probes/_summary_helper.py` (68 line, aggregation)
- `project/shared/code/analysis/_lib/heads.py` (132 line, SwiftMLP + SmallMLP)
- `project/shared/code/probes/wrappers/` (모든 SLURM wrapper)

---

## 점검 대상 핵심 질문

1. Frozen encoder + head 만 학습인가?
2. Linear head (sklearn) 구현 정확한가?
3. MLP head (SwiftMLP) 구현 정확한가? 어떤 block 구조?
4. 5-fold stim-stratified CV?
5. Per-subject + pooled mode 정합성?
6. Input normalize (StandardScaler) 적용?
7. Target / split CSV 정합성?
8. Summary aggregation 정확한가?
9. Chance baseline 정확한가?
10. Wrapper SLURM 이 어떤 config 로 launch 됐는지?

## 점검 방법

`Read` 로 모든 probe 파일과 helper / wrapper 들을 라인 단위로 검토. 각 핵심 함수 (linear_probe, mlp_probe, _train_one_mlp, build_task_data, eval_metrics, summarize_probe_csv, run_dummy) 의 dispatch 분기 검증.

---

## PASS 항목

### P_C1. Frozen feature probe 확정

- `run_unified_probe.py:1`: "Unified frozen-feature probe"
- `load_subject_emb` (line 165-173): `.pt` 의 `embeddings` 텐서 직접 로드, encoder 학습 코드 없음
- MLP head 만 optimizer 등록 (`_train_one_mlp:573`)
- video probe 동일 패턴 (`run_video_probe.py:110-117`)

### P_C2. Input standardization

- `build_task_data` (line 266-268): `StandardScaler().fit(X_train)` 후 train/val/test 동일 transform
- video probe 동일 (`run_video_probe.py:175-178`)
- 1B 의 F_B1 (VideoMAE std=18.46) 해결

### P_C3. y standardization for regression (MLP only)

- `build_task_data:271-281`: regression / multi_reg 만 y_train mean/std 로 standardize
- MLP train 시 standardized y 학습 (`_train_one_mlp:553-557`)
- Predict 시 `pred * y_std + y_mean` 으로 un-standardize (`:622-624, :656-661`)
- Linear (Ridge) 은 closed-form 이라 y standardize 불필요. 정상.

### P_C4. Linear head 구현 정확

| Task type | Estimator | HP grid |
|-----------|-----------|---------|
| binary | LogisticRegression(L2, class_weight=balanced, lbfgs, max_iter=5000) | C ∈ {1e-3, 1e-2, 1e-1, 1, 10, 100} (6점) |
| regression | Ridge | alpha 동일 grid |
| multinomial | LogisticRegression(L2, class_weight=balanced) | C 6점 |
| multi_reg | MultiOutputRegressor(Ridge, n_jobs=8) | alpha 6점 |
| multilabel | per-cat L2 logistic, joblib threading, balanced | C ∈ {1e-2, 1, 100} (**3점 축소**, F9) |
| soft_dist | MultiOutputRegressor(Ridge), clip+normalize | alpha 6점 |

HP 선택: val_main 으로 best HP → test 평가. 정상.

### P_C5. MLP head (SwiftMLP) 구조 정확

`project/shared/code/analysis/_lib/heads.py:16-89` 라인 단위 확인.

```
SwiftMLP(num_classes, num_blocks=2, hidden_dim=in_dim,
         mlp_ratio=4.0, drop_rate=0.3)
```

**구조** (forward path 기준):
1. Input x: (B, in_dim) (already_pooled=True 이므로 pooling skip)
2. 2 blocks 의 sequential:
   - 각 block = `Sequential(MLPBlock(hidden=hidden_dim, mlp_dim=hidden_dim×4, dropout=0.3), LayerNorm(hidden_dim))`
   - MLPBlock (monai): `Linear(hidden→mlp_dim) → GELU → Dropout → Linear(mlp_dim→hidden) → Dropout`
   - 즉 한 block 안에 2 Linear (up-projection 4x → down-projection back). residual 은 monai MLPBlock 안에서 처리.
3. Final `head = Linear(hidden_dim, num_classes)`
4. Init: `trunc_normal_(weight, std=0.02)` for Linear, `bias=0`, `LayerNorm(weight=1, bias=0)`

**Params**: BFM probe 입장에서 in_dim = 288 / 768 / 1536 일 수 있어 head size 가 모델별 다름.
- in_dim=288: ~0.83M params
- in_dim=768: ~5.9M params
- in_dim=1536: ~23.7M params

큰 in_dim 에 대해 head 크기가 크게 자라는 점 (특히 SwiFT NewE192 와 UAH 202M 의 1536 dim) 은 F_C1 으로 기록 (overfitting 가능성).

### P_C6. MLP training loop

`_train_one_mlp` (line 530-663):
- Optimizer: Adam, lr ∈ {1e-4, 3e-4, 1e-3, 3e-3, 1e-2} (5점), weight_decay=1e-4
- Batch: 8, Epochs: 40, Early stop patience: 10
- Loss dispatch: CrossEntropy (binary/multinomial), BCEWithLogits (multilabel), KLDivLoss (soft_dist), MSE (regression)
- Balanced sampling for binary / multinomial (line 562-567): inverse frequency, 0-count bin clamp to 1
- best_val 기준 best state 저장 후 test 평가
- Reproducibility: `torch.manual_seed(seed)` + `np.random.seed(seed)` at start (line 531). seed 별 fully reproducible.

### P_C7. 5-fold stim-stratified CV

`build_5fold_split.py` (46 line):
- canonical V quartile × A quartile = 16 cell joint label
- `StratifiedKFold(n_splits=5, shuffle=True, random_state=0)` (line 27)
- 출력: `horikawa_5fold.csv` (stimulus_num, fold ∈ {1..5})
- 같은 stimulus → 같은 fold (stim-level leakage 없음)

`_get_fold_split` (`run_unified_probe.py:225-233`, video probe 동일):
- test = fold k, val = (k%5)+1, train = remaining 3 folds
- 60/20/20 split (3:1:1)

### P_C8. Class imbalance 대응

- Linear: `class_weight="balanced"` for binary, multinomial, multilabel
- MLP: balanced inverse-frequency sampling (line 562-567), 0-count bin clamp

### P_C9. Pooled vs per_subject mode

`run_unified_probe.py:745-749`:
- pooled: 5 subj 의 emb concat → 한 split 안에서 학습
- per_subject: subj 별 독립 split + 학습
- 두 모드 모두 stim-level split 공유 (한 stim 의 5 subj 가 모두 같은 split)
- video probe 는 stim-level (no subject dim)

### P_C10. Stim 매칭 assert

`build_task_data:247-249`: `stim_to_idx` 매핑 + `df["row"].notna().all()` assert. 모든 stim 이 embedding 안에 있어야 함.

### P_C11. _summary_helper aggregation (정확한 로직 확인)

`_summary_helper.py:33-68`:
- groupby cols = `["feature", "init", "padding", "task", "task_type", "main_metric", "head", "mode", "subject"]`
- 모든 `test_*` 컬럼 중 numeric 만 aggregate
- skip: `test_pearson_r_per_dim` (list-encoded), `test_main` 은 직접 mean/std 포함
- 출력: `{metric}_mean`, `{metric}_std`, `count`
- `keep_default_na=False`: `init="n/a"` 같은 string "n/a" 가 NaN 으로 변환되지 않도록 (ROI / video / chance 가 group 에서 살아남도록)

**핵심**: aggregation 의 평균 dimension 은 **fold × seed 만**. subject 와 다른 condition 은 group axis 로 유지. 즉 per_subject mode 에서 각 subject 의 결과가 별도 row (subject 별로 따로 mean+std).

**Single seed 시**: fold 5 개 만 평균 → std 는 fold 간 variance.

### P_C12. Chance baseline 정확

`run_chance_baseline.py` (258 line):
- Dummy strategies:
  - binary / multinomial: stratified (seed-dependent) + most_frequent (deterministic)
  - regression: mean + median (deterministic)
  - multi_reg: mean
- 6 task (V/A binary, V/A reg, Cat34_top1, Dim14_multi), 5 fold
- seeds default `[0, 1, 2]` for stratified (비결정적), `[0]` for deterministic
- `build_split` 가 task 별 label_df merge 후 train/val/test 분리 → 각 task 의 N 이 다른 점 (V binary N=1131, V reg N=2185 등) 자동 반영. 1D 의 F14 (V/A binary 의 N 차이) 자동 해결.
- 출력: `chance_baseline.csv` + `chance_baseline_summary.csv`

### P_C13. ROI feature extraction (Tier 1 floor)

`extract_roi_features.py` (110 line):
- Schaefer 17n400p (400) + Tian S3 50 = 450 ROI
- 각 stim 의 (450, T) ROI time-series 를 **시간축 mean** → (450,)
- 모든 2185 stim stack → (2185, 450)
- 출력: `project/shared/output/embeddings/roi_schaefer400tian50_mean/sub-XX.pt`, BFM payload 와 동일 schema (probe pipeline 그대로 사용 가능)
- padding 영향 없음 (시간 mean 이라 T 가 5 든 47 이든 같은 차원)

### P_C14. Wrapper SLURM 구조 명확

`project/shared/code/probes/wrappers/` 디렉토리:

**BFM wrappers** (`wrappers/bfm/`):
| Wrapper | Tasks | Note |
|---------|-------|------|
| `Brain-JEPA/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | config_set=main, features=Brain-JEPA |
| `NeuroSTORM.sh` | single, all 6 task | config_set=main, features=NeuroSTORM |
| `NeuroSTORM_split/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | NS 도 task 별 split 존재 (중복) |
| `SwiFT_NewE96/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | |
| `SwiFT_NewE36/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | |
| `SwiFT_NewE192/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | |
| `SwiFT_UAH_5M/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | |
| `SwiFT_UAH_51M/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | |
| `SwiFT_UAH_202M/{V,A}_{binary,reg}.sh` | 4 wrapper × 1 task | |
| `SwiFT_variants.sh` | 5 variants × all task, padding param | config_set=swift_variants |
| `SwiFT_padding_ablation/` | task 별 SwiFT NewE96 × 4 padding | |
| `SwiFT_padding_cyclic_only/` | SwiFT NewE96 × cyclic_replicate | |
| `_task_masters/{V,A}_{binary,reg}_all_swift.sh` | 6 SwiFT variants sequential 한 task | 한 GPU 에서 sequential |
| `ROI_Schaefer400Tian50.sh` | single, all task | config_set=main |
| `chance_baseline.sh` | single, all task | run_chance_baseline.py |

**Video wrappers** (`wrappers/video/`):
| Wrapper | Note |
|---------|------|
| `CLIP.sh` | pretrained + scratch 동시 |
| `DINOv2.sh` | 동일 |
| `VideoMAE.sh` | 동일 |
| `V-JEPA2.sh` | 동일 |
| `Qwen-VL_caption.sh` | caption embedding |

**Master**:
- `wrappers/run_all_phase1.sh`: bfm/*.sh + video/*.sh 전부 sequential (fallback)
- `run_cat34_phase1.sh`: BJ + SwiFT NewE96 + NS, Cat34_multilabel + Cat34_soft, **linear only (`--skip_mlp`)**

모든 wrapper 의 padding default = main grid = **zero** (사용자 결정 일관).

### P_C15. Result CSV naming pattern

- BFM 의 task-split 결과: `bfm_probe_{model}_{task}.csv` (Brain-JEPA, NS_split, SwiFT_NewE96, SwiFT 변종들)
- BFM 의 single launch 결과: `bfm_probe_{model}.csv` (NS single, ROI)
- SwiFT padding ablation: `bfm_probe_SwiFT_padding_ablation_{task}.csv`
- SwiFT variants: `bfm_probe_SwiFT_variants_pad-{padding}.csv`
- Cat34 (multilabel + soft): `cat34_probe_linear.csv` (단일 파일, linear only)
- Chance: `chance_baseline.csv` + `chance_baseline_summary.csv`
- Video: `video_probe_{model}.csv`

### P_C16. SmallMLP 정의 존재하나 사용 안 함

`heads.py:92-132` 의 `SmallMLP` 는 small-N regime 용 (in_dim → 256 → 256, ~0.4M params) 으로 vendored. unified probe 에서는 SwiftMLP 만 사용. SmallMLP 는 future ablation 용.

## FLAG / 발견

### F_C1. SwiftMLP hidden_dim=in_dim 정책으로 head 크기가 input dim 에 비례

| in_dim | head params (대략) |
|--------|---------------------|
| 288 | ~0.83M |
| 450 (ROI) | ~2.0M |
| 768 | ~5.9M |
| 1024 (CLIP) | ~10.5M |
| 1280 (VideoMAE) | ~16.4M |
| 1408 (V-JEPA2) | ~19.8M |
| 1536 (DINOv2, SwiFT NewE192, UAH 202M) | ~23.7M |

stim N ≈ 1700 (train, V_binary 의 경우 ~680), V_reg 의 경우 ~1750 train. **head 의 params 가 train sample 수와 비교해 큼**. 특히 큰 in_dim 모델 (DINOv2, V-JEPA2, SwiFT NewE192, UAH 202M) 의 MLP 가 overfitting 위험.

대응: drop=0.3 + weight_decay=1e-4 + balanced sampling + early stopping (patience 10) + val 기반 lr 선택 으로 완화. 그러나 cross-model 비교 시 in_dim 이 다른 모델 간의 fair 한 비교 인지 의문.

행동 권고: 1E 단계에서 MLP 결과의 best_hp (선택된 lr) 와 best_epoch 가 모델별로 어떻게 분포하는지 확인. 큰 in_dim 모델이 1e-4 (가장 작은 lr) 와 early stopping 으로 갔다면 underfitting / overfitting 한쪽으로 쏠림 가능.

### F_C2. Linear multilabel HP grid 축소 (3 vs 6)

`run_unified_probe.py:482`: `ML_CS = [1e-2, 1.0, 100.0]`. 다른 task 의 6 점 grid 대비 절반. 코드 코멘트 "Reduced grid for multilabel (3 instead of 6) to bound runtime". 정당화 됐지만 best C 가 1e-2 또는 100 의 grid 경계에 붙어있을 경우 saturate 안 됐을 가능성 (1E 에서 확인 권고).

### F_C3. Cat34_top1 의 "broken folds" (1A 의 F8, 1D 의 F13 confirm)

`run_unified_probe.py:13` docstring 명시. 1D 에서 fold 1 의 class 25 가 train 에 없음을 측정으로 확인. paper / report 에서 Cat34_top1 metric 사용 금지 권고.

### F_C4. SEEDS=[0] default → 모든 결과 단일 seed

`run_unified_probe.py:126`, `run_video_probe.py:91`: `SEEDS = [0]`. comment "Final paper 직전에 --seeds 0,1,2 로 늘리기". MLP 결과 의 cross-seed variance 없음. **fold 평균 std 만 존재** (즉 summary 의 std 는 5 fold variance only).

### F_C5. NS 의 wrapper 중복 (single + split)

`NeuroSTORM.sh` (single, all task) + `NeuroSTORM_split/{V,A}_{binary,reg}.sh` (task 별 split) 둘 다 존재. 둘 다 실행되면 `bfm_probe_NeuroSTORM.csv` 와 `bfm_probe_NeuroSTORM_{task}.csv` 둘 다 생성. 1E 에서 어느 쪽이 main result 로 쓰였는지 cross-check.

### F_C6. Cat34_multilabel + Cat34_soft 는 linear only

`run_cat34_phase1.sh:14-19`: `--skip_mlp`. 즉 Cat34_multilabel 과 Cat34_soft 의 MLP 결과가 없음. paper / report 에서 Cat34 의 MLP 결과 surface 시 주의 (없을 가능성).

### F_C7. Video probe docstring outdated "3 seeds"

1B 의 F_B2 와 동일. 코드 SEEDS=[0] 이지만 docstring 은 "3 seeds". 결과 영향 없음, doc 수정 만.

### F_C8. _summary_helper 의 std 가 5 fold 기준 (n=5)

`_summary_helper.py:58`: `df.groupby(grp).agg({c: ["mean", "std"]})`. 1 seed × 5 fold → std 는 5 fold variance 의 sample std (n=5). Cross-seed variance 없음. 결과 표에서 std 가 작아 보이는 이유 (F10 와 결합).

## FAIL 항목

없음.

## Verdict

**Step 1C (deep): PASS with multiple flags.**

- 모든 코드의 구조적 정합성 확인 (frozen, scaler, CV, HP selection, MLP head, summary, chance, ROI, wrapper).
- F_C1 (in_dim 따른 head 크기), F_C3 (Cat34_top1 broken), F_C4 (single seed) 는 결과 해석 시 반드시 반영.
- F_C5 (NS wrapper 중복), F_C6 (Cat34 multilabel/soft linear only) 는 1E 결과 정합성 단계에서 cross-check.

## Action items (1E 단계로 이월)

1. F_C1: MLP 결과의 best_hp (lr) 분포 분석. 큰 in_dim 모델이 grid 경계로 가는지.
2. F_C2: multilabel 의 best C 가 grid 경계에 붙어 있는지.
3. F_C3: paper / report 에서 Cat34_top1 surface 여부 확인 및 retract.
4. F_C4 / F_C8: MLP 결과의 "n=1 seed, std = 5 fold std" 명기 여부 확인.
5. F_C5: NS 의 main result 가 single (`bfm_probe_NeuroSTORM.csv`) 인지 split 인지 확정.
6. F_C6: paper / report 에서 Cat34_multilabel / Cat34_soft 의 MLP 결과 잘못 surface 됐는지 확인.
