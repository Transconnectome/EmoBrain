# EmoBrain 핵심 연구 완결 로드맵 (`FUTURE_RESEARCH_PLAN.md`)

> **[2026-11-16 정본 단일화 업데이트 (`origin/design/emobrain-final-2026-11-03 @ 431c1bc`)]**
> - 공식 브랜치 `design/emobrain-final-2026-11-03`(`431c1bc`)에서 Perlmutter 정품 `roi_voxels` 기반 주 모델 개선(`voxel_sampling = 0.375`, `weight_decay = 100`, 조건별 `{1e-4, 1e-3}` 검증 $r$ 병합 `s6_merge_lr.py`) 및 공식 `S5(370-ROI map)`·`S8(MC transfer)`·`S9(swap, stimulus_swap, per-video perturb, path_eval)`·`S10(Part 1/2, K1/K1a, sensitivity, 6-4c geometry & rating_parts)` 구현이 완료됨을 확인했다.
> - 이에 따라 `b300-01`의 구버전(`f5c8569`) 독자 재학습 대기는 종료하고, 로컬 및 `b300-01:/scratch/emobrain/code`의 `src/` 전체를 `431c1bc` 정본과 100% 일치시켰다.
> - 후속 진행은 ① Perlmutter 완료 `s10_stats/` 요약표 반입·검증 및 그림/요약 통합, ② Perlmutter 잔여 미완료 GPU 과업(`D·E` 묶음, `S8 6-2 / 6-4a / MC 6-3`, `A-1 depth4` 등) 확인 시 정품 `roi_voxels` 11개와 함께 `b300-01`에서 동일 `431c1bc` 코드로 분담 실행하는 단일 트랙으로 운영한다.

본 문서는 `b300-01` 서버의 데이터 정합성 감사 결과와 3중 비평(신경과학 인과식별·실행 함정·신규 합류자 관점)을 반영하여, **불필요하거나 교란된 가지치기 실험을 전면 배제하고 논문 핵심 주장에 직결되는 4단계 실행만 남긴 공식 로드맵**이다.

---

## 1. 현황 진단 및 데이터 정합성 경계

| 파이프라인 계층 | 현재 상태 | 과학적·통계적 유효성 판정 | 조치 |
| :--- | :--- | :--- | :--- |
| **`S1` 분할 · `S3` 자극 특징 8종 · `S4` 자극 모델 전체** | **100% 정품 확정** | `roi_voxels`를 전혀 사용하지 않음. `s4_stimulus`(`0.4766`), `s4_noemo`(`0.4810`), `s4_clip`(`0.5595`), `s4_k1a` 등 모든 수치 확정. | **재실행 불필요 (그대로 사용)** |
| **`S5` 전뇌 선형 복원·기준선 · `S9 K1 / K1a + B4`** | **보수적 하한치 확인** | 초기 이관본의 구형 근사 `roi_voxels`로 인해 고유 복셀의 `60.3%`만 포함되었으나, 그 하한 조건에서도 64개 층 복원(`[사전] 2-1`), `K1`(`0.2952`), `K1a`(`0.4530 > B4 0.3712`)가 5명 전원 유의(`p = 0.0001`). | **Step 1 (`<1시간`)에서 정품 `roi_voxels`로 100% 커버리지 갱신 + 심화 3종 추가** |
| **`S6` 뇌 신경망 · `S9 2-2 / 6-4b`** | **v1 예비 실행** | ROI별 선형 투영층(`W_r x_r + b_r`)이 구형 근사 좌표에 묶여 있어 해부학적 네트워크 결론에 인용 불가. 또한 `A-1`(`0.2329`) < `A-1_pool`(`0.2660`) < `S5 Ridge`(`0.2931`)로 확인됨(`N22`, `N23`). | **Step 2 (`~5시간`)에서 핵심 11개 조건만 정품 `roi_voxels`로 압축 재실행** |

---

## 2. 과감히 생략하는 5가지 가지치기 목록 (`Cut List`)

1. **`S8` 신경망 60개 구역 제외 재학습 (`6-2`) 생략**: GPU ~30시간 소요 대비 `A-1`/`C-1` 자체가 전뇌 선형 모델보다 낮아 과학적 이득이 없다. **Step 1의 전뇌 선형 `K1_zone` (60개 분할 × 5명, GPU 30초)**으로 대체한다.
2. **`S5 ML-BVAE` 잔여 18개 fold 및 외부 문헌 신경망(`GED`, `EmoGrowth`) 재학습 생략**: 부분 완료(`12/30`) 상태의 합산은 금지하며, 정품 ROI 복구 후에도 `S5 Ridge`·`MLP`·`H2020` 주 기준선만으로 비교가 완결된다.
3. **`S6` 비핵심 파생 조건 10종 생략 (`290 -> 117 runs/fold`, GPU 시간 60% 절감)**: `D-3_paired`(68 runs), `D-3`(29 runs), `C-1_grad`(26 runs), `D-4`(20 runs), `multimodal`(11 runs), `E-고정`/`E-학습`(16 runs), `D-2`(8 runs), 섞기 대조군 2종(`ctrl_stimulus_shuffle`, `ctrl_feature_shuffle`, 16 runs)을 생략한다.
4. **신경망 13개 네트워크 단독 재학습(`S8 6-4a`) 생략 및 `6-4b` 주 해석 격하**: `C-1`은 글로벌 해독 특징(`v_hat, c_hat`) 경로가 추가된 구조이므로 단일 ROI 토큰 교란(`6-4b`)에서 구조적 완충 교란이 발생한다. 주 해부학 분석은 **Step 1의 교란 없는 전뇌 `S5 Ridge` 13네트워크 `LONO`·`SNO`**로 대체한다.
5. **신규 아키텍처(`Brain-IT`, `ROI-cells`, Graph-CNN 등) 탐색 금지**: 설계 동결(`f5c8569`) 및 `src/` 무수정 원칙을 엄수한다.

---

## 3. 정선된 핵심 4단계 실행 계획 (`Essential 4-Step Plan`)

### Step 0 — 코드 안전장치 확립 및 정품 `roi_voxels` 반입 (완료/진행 중)
- 합성 구형 생성 스크립트 삭제 및 정품 SHA256 검증기 [`scripts/b300/verify_s2_roi_voxels.py`](../scripts/b300/verify_s2_roi_voxels.py) 도입 (`manifests/s2/provenance.json` 내 11개 파일 SHA256 대조; 불일치 시 모든 GPU sbatch 자동 차단).
- Perlmutter 원본 `/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/s2_manifest/roi_voxels/{hk_sub-01..05,mc_sub-01..06}.npz` (총 ~15 MB)를 `b300-01:/scratch/emobrain/outputs/s2_manifest/roi_voxels/`에 복사 후 `verify_s2_roi_voxels.py` 통과(`exit 0`) 확인.

### Step 1 — 전뇌 선형 핵심 사슬 정품 갱신 + 비순환·구역·네트워크 보강 (1 GPU `< 1시간`)
- **실행 명령**:
  ```bash
  sbatch scripts/b300/step1_linear_core_b300.sbatch
  ```
- **포함 내용**:
  1. 기존 v1 합성 산출물 `/scratch/emobrain/outputs_v1_synthetic_roi/` 무손실 백업.
  2. 정품 `roi_voxels` 기준 `s2_roi_cells.py` → `s5_decoding`(64개 층) → `s5_baselines`(`ridge`, `soft_bce`, `signal`, `zone`, `h2020`, `mlp`, `video`) → `s5_collect.py` → `s9_pathway_k1_k1a.py` 일괄 실행.
  3. [`scripts/s9_s10/step1_linear_enrichments.py`](../scripts/s9_s10/step1_linear_enrichments.py) 자동 실행:
     - **비순환성 검증 (`K1_noemo` & `K1_clip`)**: 캡션에서 정서 단어 181개를 제거한 `DeBERTa_noemo`를 뇌에서 해독해 고정 `S4 noemo` head에 통과시켜도 `K1` 경로가 성립하는지 검증.
     - **미시청 장면 구역 일반화 (`K1_zone`)**: 5개 내용 구역 × 6 fold × (`excluded` vs `control`)에서 선형 의미 매개 경로의 구역 외 일반화 검증.
     - **교란 없는 13개 뇌 묶음 분석 (`LONO` & `SNO`)**: `CAB-NP` 12개 피질 네트워크 + `Subcortex`(피질하 해부학적 묶음) 각각을 제외한 전뇌 `S5 Ridge` 하락폭(`LONO Δr`, 복셀 수 정규화 병기) 및 단일 묶음 예측력(`SNO r`) 산출.

### Step 2 — `S6` 핵심 11개 조건 압축 재실행 + `S9/S10` 통합 갱신 (6 GPUs `~5시간`)
- **실행 명령**:
  ```bash
  # Fold 1~6 병렬 학습 (타 사용자 점유 시 --array=1-6%4 등으로 조절)
  STEP2_JID=$(sbatch --parsable scripts/b300/step2_s6_core_b300.sbatch)
  # 학습 완료 직후 S9·S10 전체 표·판정표·벡터 그림 6종 자동 재생성
  sbatch --dependency=afterok:${STEP2_JID} scripts/b300/step2_post_s9_s10_b300.sbatch
  ```
- **핵심 11개 조건 (`S.ORDER` 의존성 닫힘)**:
  `brain_only`(`A-1`), `brain_only_featdec`(`B-1`), `brain_decoded`(`C-1`), `brain_decoded_additive`(`C-1_add`), `brain_only_distill`(`A-2`), `brain_decoded_distill`(`C-2`), `feature_encoder`(`encoder_2`), `brain_decoded_sep`(`D-1`), `control_label_smoothing`(`[사전] 2-3(라)` 대조군), `brain_only_pool`(`A-1_pool`), `brain_decoded_pool`(`C-1_pool`).
- 이로써 사전등록 `[2-1]`(2개), `[2-2]`(3개), `[2-3(가)~(바)]`(6개 전체) **총 11개 HK 사전등록 검정 전수**와 `1-2(가)/(나)`, `O33`, `K1/K1a`, `6-4b`, `F7/N22`가 단 하나의 누락 없이 정품 ROI 위에서 완결된다.

### Step 3 — `MindCaptioning` 외부 데이터셋(`mc_test72`) 단판 전이 검증 (`6-3`, 1 GPU `< 1.5시간`)
- **엄수 규칙 (`L10`, `O28`~`O30`)**:
  - `final_for_mc` 공유 가중치 학습 시 새 하이퍼파라미터 탐색 없이 6개 바깥 fold 선택값의 최빈/중앙 설정(`--fixed-selected`)으로 고정한다(`L10`).
  - MC 참가자 6명(`mc_sub-01..06`)의 학습 영상(`manifests/s2/mc_blocks.tsv`)에서는 참가자별 선형 입력 어댑터만 맞추고, 시험 영상 72개는 반복 제시 평균(`manifests/s2/mc_test_repeats.tsv`) 후 **단 1회(`1-shot`) 채점**한다(`O28`~`O30`; 시험 결과 확인 후 수정 금지).
  - 전이 대상은 ① 전뇌 선형 `S5 Ridge + K1/K1a`, ② `A-1_pool`, ③ Step 2 최우수 특징 결합 모델(`C-1`/`C-2` 또는 `D-1`) 3종으로 한정한다.
