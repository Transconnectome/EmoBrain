> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Hypothesis Ledger

가설 상태 backbone. status: `proposed → shortlisted → running(job-id) → done → confirmed | refuted | parked`.
evidence 없는 `confirmed` 금지. 갱신 규칙은 `README.md`.

---

## Round 1 — D1 (BrainVLM)

**Goal (Gate).** D1 의 V/A Pearson r 이 Phase 1 ROI baseline (V 0.40, A 0.23) 을 fold 평균에서
의미있게(>baseline+0.05, stimulus-level paired bootstrap p<0.05) 넘는 조건을 찾아라.
**Date.** 2026-06-18. **Direction.** D1. **Status.** 단계 3 완료 (critic Revise). GATE 1 대기.

> ⚠ **Gate 결함 (critic, MAJOR).** "stimulus-level paired bootstrap" 은 5-subj pooling 의 subject clustering 을
> 무시해 표준오차 과소추정(anti-conservative). → **subject-clustered (또는 subject×stim 이중 cluster) bootstrap** 으로 수정.
> 또 `baseline+0.05` 의 0.05 가 baseline 의 fold-level 신뢰구간 안인지 미확인. → **baseline CR 먼저 측정 후 threshold 확정.**
> 이 둘을 고치기 전엔 어떤 가설이 이겨도 p<0.05 신뢰 불가.

### 가설 + 자가 점수 (0~5, 합 25)

자가 점수(합) → critic 재조정 후 status. critic 이 자가 채점의 self-serving inflation (Medium-High) 을 지적함.

| ID | 한 줄 | 자가 합 | critic 재조정 | status |
|----|-------|:--:|:--:|--------|
| H-007 | grid 자체가 정보 손실 → 450-dim ROI 벡터 직접 주입 control | 19 | 유지 (단 capacity-matched 조건 필수) | **shortlisted (1순위)** |
| H-008 | (신규) temporal pooling sweep: mean/max/last/AUC, 입력단만 | — | H-001 의 정직·저비용 대체 | **shortlisted (1순위급)** |
| H-009 | (신규) subject-mean baseline + subject-mean-centered 평가 | — | r 이 신경신호인지 subject bias 인지 폭로 | **shortlisted (control 필수)** |
| H-005 | loss weighting 이 V/A 굶김 → λ1 ∈ {1,3,10} sweep | 14 | **승격**: 다른 실험의 전제(sanity) | shortlisted |
| H-003 | 2D ROI 배치(L1)가 임의적 → network/gradient 정렬 배치 | 19 | 19→**15**: frozen tower 가 layout confound | parked (H-002 와 묶을 때만) |
| H-001 | 시간축 평균이 arousal 파괴 → (450,T) full temporal arch | 19 | 19→**13~14**: T=5 에서 mechanism 붕괴 | **parked** (비싼 버전) |
| H-006 | 5-subj pooling → subject token | 18 | leakage 가 "주의" 이상: response-bias 암기 | parked (Gate 수정 + control 전제) |
| H-002 | vision tower last-N block unfreeze | 17 | — | parked |
| H-004 | V/A 자연어 target | 17 | — | parked |

### 가설 상세

**H-001** 시간축 평균.
- 조작: `dir1_brainvlm/code/fmri_patchify.py` 의 time-axis mean(단일 image) → L3 (450,T) matrix + temporal patch embed.
- 예측: A(현재 0.23, floor)가 V 보다 더 크게 개선. emotion arousal 은 temporal dynamics 의존.
- 기전: arousal 의 신경 표상은 BOLD 시간 변화에 강하게 결합 (정적 평균이 이를 소거).
- 반증: A 가 불변 또는 악화.
- 위험: temporal arch 추가로 cost 증가, 짧은 T(Horikawa median 5)에서 정보 부족.

**H-003** ROI 배치 정렬.
- 조작: L1 layout(임의 순서) → Schaefer network / gradient 순 정렬 배치. L1 vs 정렬 비교.
- 예측: locality 가 중요하면 V/A 동시 개선. 차이 없으면 ViT 가 layout 무시(그것도 정보).
- 기전: ViT patch embed 는 공간 locality 가정. 임의 ROI 순서는 무관 영역을 한 patch 에 섞음.
- 반증: 정렬 배치가 L1 과 동일.
- 위험: 낮음.

**H-007** grid-vs-vector control (falsification-first).
- 조작: 2D image 경로 대신 450-dim ROI mean 을 직접 token 으로 projection. grid ≤ vector 면 2D-image framing 자체가 정당화 안 됨.
- 예측: grid 가 vector 를 못 넘으면 D1 의 핵심 설계 가정 붕괴 (de-risking 가치 큼).
- 기전: 2D 이미지화는 ViT backbone 재사용 목적이지 신경과학적 필연 아님.
- 반증: grid > vector (이 경우 framing 정당화됨).
- 위험: 낮음. 가장 싸고 가장 근본적.

**H-006** subject token.
- 조작: 5-subj pooled 학습에 subject embedding/token 추가.
- 예측: inter-subject 분산이 크면 V/A 개선.
- 기전: 같은 stim 의 5명 BOLD pooling 은 subject 분산을 label noise 로 취급.
- 반증: 개선 없음 → 분산이 이미 작음.
- 위험: subject id 가 stim 정보로 leak 되지 않게 주의.

**H-002 / H-004 / H-005**: 위 표 참조. 1라운드 후보 아님(점수 하위), parked 후보.

### 신규 가설 (critic 발굴)

**H-008** temporal pooling sweep.
- 조작: 입력단에서 time → {mean, max, last, AUC} 만 교체. backbone 재학습 비용 동일.
- 예측: mean 이 정보를 죽이면 max/AUC 가 A 개선. 차이 없으면 H-001 의 비싼 temporal arch 는 불필요.
- 기전: T median 5 는 단일 HRF 의 거친 샘플링이라 "arousal dynamics" 가 아니라 HRF 진폭/지연. mean 외 pooling 으로 회수 가능.
- 반증: 모든 pooling 동일 → 시간 정보 자체가 무의미.

**H-009** subject-mean baseline (control).
- 조작: 각 test stim 예측 = train 의 그 subject 평균 V/A (trivial). + 모든 모델을 subject-mean-centered 로도 평가.
- 예측: 이 trivial baseline 이 ROI baseline 상당 부분을 설명하면, 모델 r 은 신경 디코딩이 아니라 subject bias fitting.
- 반증: subject-mean 이 chance 수준 → r 은 진짜 stim-driven.

### critic 적대적 검증 (요약)

Verdict: **Revise**. 자가 채점 self-serving inflation (Medium-High).

| 판정 | 심각도 | 내용 |
|------|:--:|------|
| H-001 mechanism 붕괴 | **FATAL** | T median 5 에서 시간축은 arousal dynamics 가 아니라 단일 HRF 샘플. emotion 은 trial-averaged **공간 패턴**에서 디코딩됨(Nummenmaa 2012 PNAS, Saarimäki 2016 Cereb Cortex — *인용 미검증, 원문 확인 요*). 비싼 temporal arch 불필요, pooling sweep(H-008)로 대체. |
| Gate 통계 결함 | **MAJOR** | stimulus-level bootstrap 이 subject clustering 무시 → anti-conservative. baseline+0.05 threshold 가 baseline CI 안일 수 있음. (위 Goal 경고 참조) |
| H-003 frozen confound | **MAJOR** | frozen ImageNet 필터가 ROI 인접성을 못 읽음 → layout 효과가 H-002(unfreeze)와 교란. 단독 해석 불가. |
| H-006 leakage | **MAJOR** | stimulus-level split 에서 subject token 이 response bias 를 암기해 stim 무관하게 r 상승. subject-mean-centered 재평가 없이는 해석 불가. |
| H-007 공정비교 미명시 | minor | vector 경로의 param 수/LoRA 용량/step 을 grid 와 매칭해야. 안 하면 capacity 차이를 layout 효과로 오독. |

### [GATE 1] 사용자 선택 — 권고 1라운드

critic 권고: 비싼 가설 전에 **입력/평가 레벨만 바꾸는 저비용 3종을 fold 1 한 학습 설정에서 동시에** 돌려 D1 의 세 load-bearing 가정을 한 번에 de-risk.

1. **H-007** grid-vs-vector (capacity-matched) — "2D-image framing 이 정당한가"
2. **H-008** temporal pooling sweep — "mean 이 정말 정보를 죽이는가"
3. **H-009** subject-mean baseline + centered 평가 — "r 이 신경신호인가 subject bias 인가"
4. (병행) **H-005** λ1 sanity — V/A head 가 굶지 않는지 (다른 비교의 전제)

선결: Gate 통계 수정 (subject-clustered bootstrap + baseline CI 측정).

**→ 사용자 결정 대기. 위 1~4 중 1라운드로 무엇을 돌릴지, Gate 수정안 승인 여부.**
