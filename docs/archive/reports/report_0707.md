> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Progress Report (2026-07-07)

외부 검토용 self-contained report. EmoBrain 프로젝트 의 framework, 지금 까지 의 baseline / 진단 결과, 열린 질문 을 정리. 다른 AI / 협업자 가 이 문서 하나 로 현황 을 파악 하고 비평 할 수 있도록 작성.

---

## 1. 프로젝트 한 줄

Human brain fMRI 에서 fine-grained emotion (Cowen-Keltner 34-category) 을 decode 하는 multi-modal LLM framework. Brain + video + caption 을 teacher 로 학습 하고, 추론 은 brain-only student 가 distillation 으로 이어받는 구조. Novelty 는 특정 encoder 가 아니라 이 framework 자체 (multi-modal 학습 + brain-only 추론 비대칭 + 34D 고차원 readout).

## 2. 데이터

| 항목 | 값 |
|------|-----|
| fMRI | Horikawa 2020. 5 subject 가 short silent video 시청. ROI mean (Schaefer-400 + Tian-S3-50 = 450). |
| Stimulus 수 | **2185 unique canonical**. fMRI session 에 2196 presentation 이 있으나 그 중 **11 개 는 reliability check 로 두 번 제시된 중복** (EmoViS DECISIONS 2026-05-08). Unique = 2196 − 11 = 2185. label CSV / split / ROI pt 모두 2185. (fmri_raw.npy 축 2196 은 presentation 수, 중복 포함.) |
| Label | 34D Cowen-Keltner. 각 값 = 영상당 9-17 rater 가 그 emotion category 를 고른 crowd 비율 (**원점수 0-1**, NOT sum-to-1). 73.8% 가 0 (영상당 평균 1.7 category 만 활성). Sparse 는 yes/no 응답 의 본질. |
| Split | stimulus-level. train 1748 / val 217 / test 220 stim (합 2185). Pooled = 5 subj × stim (train 8740 / val 1085 / test 1100 sample). |
| Video/caption feature | stimulus-level embedding. CLIP / V-JEPA2 / VideoMAE / DINOv2 (각 pretrained + scratch), caption embedding (768d). |
| Cross-subject test | MindCaptioning (Horikawa, Science Advances **2025**; bioRxiv preprint 2024). Cross-subject 이지만 cross-stimulus 아님 (stimulus 겹침). |

**Label 스케일 (혼동 주의).** 원점수 = crowd 비율 0-1. 학습/평가 는 per-emotion **log1p_z** 변환 후 z-space 에서 (log1p 후 z-score, train fit only). Heavy-tail 완화 + rare emotion 이득. 아래 §4.1 의 정답 range [-1, +4] 는 log1p_z 변환 후 값 (원점수 0-1 아님). zscore mode 도 파일 유지.

## 3. Framework 핵심 설계

**3.1 Subject pooling = universal emotion code 학습.**
5 subject 를 pool 로 학습 하는 이유 는 데이터 증강 이 아니라 subject-공통 (universal) emotion code 만 학습 하려는 것. 개인차 극복 이 아니라 개인차 를 의도적 배제. Spine question 이 "사람 일반 의 뇌 에서 감정 이 어떻게 표상 되나" 이므로.

**3.2 Track A / Track B.**
- **Track A.** Brain-only encoder ablation (E1-E4). Context 없이 각 encoder 를 34D 에 직접 지도학습. Encoder 순위 확정. E1 raw ROI projection / E2 ridge latent / E3 BFM frozen (SwiFT, Brain-JEPA, NeuroSTORM) / E4 image-pretrain + fMRI fine-tune (Qwen vision encoder).
- **Track B.** Track A best encoder 1 개 만 distillation. Teacher (brain+video+caption) → soft label → student (brain-only) 가 MSE 로 재현. Framework 검증 의 primary question = "context 가 brain-only 를 얼마나 끌어올리나 (context lift)". Encoder × distillation 그리드 아님.

**3.3 34D independent regression (NV4).**
34 감정 은 서로 배타적 아님 (bittersweet = joy + sadness 동시 가능). Softmax / sum-to-1 / KL 금지. Per-emotion MSE (독립 회귀). Curriculum (top-1 → top-2 → top-k → full 34D) 은 subset MSE 로 stepwise validation. Structure loss (34×34 correlation matching) 는 optional, 기본 OFF.

**3.4 Task 정의 (명확화).**
영상 → 34개 감정 각각 의 crowd 비율 (0-1 연속값) 을 독립 회귀. Yes/no 분류 아님 (원본 rater 는 yes/no 지만 우리 는 9-17명 평균낸 연속값). Distribution (softmax, 합=1) 아님 (감정 은 배타적 아님, bittersweet = joy+sadness 동시). 정확히 **34D independent regression (per-emotion)**. Loss = per-emotion MSE.

**3.5 Loss vs metric (headline 3축).**
Loss = per-emotion MSE (학습 연료). Metric headline 은 세 축 함께 (하나만 보면 속음).
- **Pearson r** (모양). 영상별 34D 예측-정답 shape correlation. 값을 절반으로 눌러도 1.0 (scale-blind).
- **CCC (Concordance Correlation Coefficient)** (모양 + 값). `2ρσxσy/(σx²+σy²+(μx−μy)²)`. shape + scale/bias 동시 penalize. 감정 인식 (AVEC) 표준. Pearson 맞아도 진폭 작으면 CCC 낮음.
- **MSE/MAE/R2** (절대 오차). Label 73.8% zero 라 무딤 ("전부 0" 이 이미 낮음). 보조.
부가 = per-emotion Pearson+CCC, RSA (34×34 structure), dim-compression, sparse retrieval (p@k).

## 4. 지금 까지 결과 (ridge baseline + 진단)

모든 실험 은 sklearn ridge (LLM 없음), 같은 split / label (log1p_z) / metric. Test split 기준.

### 4.1 B1 Brain-only ridge (baseline)

| Metric | 값 | 의미 |
|--------|-----|------|
| profile Pearson (headline 모양) | 0.296 | 영상별 34D 윤곽 correlation |
| **profile CCC (headline 모양+값)** | **0.173** | Pearson 의 58%. Ridge 가 진폭 못 살림 (값 mismatch) |
| profile Spearman | 0.213 | 순위 correlation |
| per-emotion Pearson / CCC | 0.277 / 0.165 | 감정별 (Pearson range 0.09-0.47) |
| rare-emotion Pearson / CCC | 0.201 / 0.096 | 빈도 하위 10 감정. CCC 특히 낮음 |
| RSA (34×34, same-space) | 0.777 | predicted vs target 의 감정 간 correlation matrix 유사도. 같은 34D label 공간 내 (cross-modal RSA 아님, §6-4 주의) |
| sparse p@1 / p@5 | 0.19 / 0.34 | top-k 감정 검출. predicted top-k 와 target top-k 의 겹침 (chance 0.03 / 0.15) |
| dim-compression @k | k=1 0.66 → k≥2 0.28-0.37 | target PCA top-k 축 사영 후 유지 되는 profile Pearson. 저차원 잡고 고차원 약함 |
| MSE(z) / R2(z) | 0.91 / 0.08 | all-zero(0.99) 대비 개선. sparse 라 무딤 |

**Pearson vs CCC gap 이 핵심.** Ridge 는 regularization 으로 예측 진폭 을 눌러 (예측 range [-0.45,+0.36] vs 정답 range [-1,+4], **둘 다 log1p_z 공간** 값. 원점수 0-1 아님) 패턴 (Pearson 0.30) 은 어느 정도 맞지만 값 (CCC 0.17) 은 절반 도 안 맞음. CCC 가 이 진짜 상태 를 드러냄. 우리 LLM model 은 Pearson 뿐 아니라 CCC (진폭) 도 올려야.

**Null 검증.** profile 0.296 은 trivial 아님. 평균-profile 예측 -0.03, label shuffle +0.004, fMRI shuffle 후 ridge +0.0003. 실제 fMRI-label 매칭 있을 때만 나옴.

**감정별 편차.** 잘 되는 감정 (sexual desire 0.46, aesthetic appreciation 0.46, disgust 0.44, amusement 0.43, 시각적으로 뚜렷) vs 안 되는 감정 (guilt 0.10, envy 0.09, contempt 0.13, 추상적/사회적). 빈도 낮은 감정 이 대체로 낮음.

### 4.2 Brain cross-subject ISC (noise ceiling estimator)

| 지표 | 값 |
|------|-----|
| Spatial ISC (자극별 450-ROI pattern, subject 간) | 0.235 |
| Per-ROI ISC (ROI별 자극 profile, subject 간) | 0.149 |
| Top ROI ISC | 0.51 (초기 시각 피질 추정) |

뇌 신호 가 subject 간 상당히 idiosyncratic (ISC 0.23 낮음). 시각 영역 만 공통, 고차 영역 개인차 큼.

### 4.3 Subject regime (within / pooled / LOSO)

| 조건 | profile Pearson | n_train | 의미 |
|------|-----------------|---------|------|
| Within-subject (각 subject 따로) | 0.305 | 1748 (각) | 개인 특화 포함. 데이터 1/5 인데도 최고 |
| Pooled (5 subj) | 0.294 | 8740 | universal 지향 |
| LOSO (4 train → 1 held-out) | 0.232 | ~7000 | pure universal (새 subject) |

**Within > Pooled > LOSO.** 개인 뇌-label 매핑 이 subject 마다 다름 (ISC 낮은 것 과 일치). LOSO chance = 0.001 ± 0.015 (permutation), real 0.232 는 15.3 SD 위 = universal code 압도적 존재.

**해석.** Within > Pooled 는 feature (개인 특화 배제 의 대가). Within 은 subject-specific 질문 이라 우리 spine 과 비교 대상 아님. LOSO 0.232 = universal emotion code 가 뇌 에 존재 하는 증거. 단 pooled 대비 하락 이라 새 subject 전이 는 성능 하락 인정 하며 서술.

### 4.4 B2 Modality solo (baseline ladder)

| Modality | Pearson | CCC | RSA | sparse p@1 |
|----------|---------|-----|-----|-----------|
| Brain ROI mean | 0.296 | 0.173 | 0.777 | 0.19 |
| Video V-JEPA2 | 0.449 | 0.343 | 0.796 | 0.31 |
| **Video CLIP** | **0.597** | **0.506** | **0.868** | **0.45** |
| Caption | 0.479 | 0.377 | 0.835 | 0.31 |

Pearson-CCC gap 은 brain 이 가장 큼 (-42%, 신호 약해 특히 conservative), CLIP 이 가장 작음 (-15%, 신호 강함). 순위 는 CCC 로 봐도 동일 (video 지배).

**Video 지배 34D 에서도 명확.** CLIP video 0.60 vs brain 0.30 (2배). VA binary 의 dominance (video probe 0.97 vs brain 0.72) 가 34D 에서 재현. 이는 leakage 위험 의 실증 → teacher 에 video 직접 주고 joint 학습 하면 model 이 video 에 의존, brain 무시. 그래서 Track B distillation (student brain-only, video 는 soft label 통해 간접) 필수.

### 4.5 Baseline ladder 종합

```
                          Pearson   CCC
chance (permutation)       ~0.00     ~0.00
Brain ROI ridge (B1)        0.30      0.17   ← 우리 뇌 baseline
Video V-JEPA2 solo          0.45      0.34
Caption solo                0.48      0.38
Video CLIP solo             0.60      0.51   ← modality 최고
--- 참고 (다른 축) ---
Brain cross-subject ISC     0.23             (뇌 신호 일관성, decoding ceiling 아님)
LOSO universal transfer     0.23             (새 subject, chance 0.001 대비 15 SD)
```

## 5. 현재 판단

1. **Brain-only 34D decoding 은 어렵다 (Pearson 0.30, CCC 0.17).** Chance (0) 대비 확실 히 신호 지만, CCC 로 보면 값 (진폭) 을 절반 도 못 맞춤. Pearson (모양) 은 그럭저럭, CCC (값) 는 낮음. 우리 model 이 진폭 까지 맞추면 CCC 개선 여지 큼.
2. **Universal emotion code 는 존재한다 (LOSO 0.23, 15.3 SD).** 새 subject 에도 전이.
3. **Video/caption 이 brain 을 크게 앞선다 (0.60 vs 0.30).** Multi-modal fusion 의 leakage 위험 실증. Framework 의 distillation 설계 정당화.
4. **RSA (감정 간 구조) 는 이미 높다 (0.78).** 개선 여지 는 profile 절대값 + 고차원 (dim-compression k≥5) + sparse retrieval + rare emotion.
5. **Framework 의 가치 = context lift.** 뇌 만 으로 는 0.30 한계. Teacher context (video 0.60 수준) 가 student brain-only 를 얼마나 끌어올리나 가 다음 핵심 실험 (Track B).

## 6. 열린 질문 (외부 비평 요청)

1. **Noise ceiling 정밀화.** 진짜 감정 decoding 상한 을 못 구함 (label crowd split-half 는 rater-level 원본 없음, 뇌 repeated-trial 은 자극 반복 없음). **주의. ISC (0.23) 는 decoding ceiling 이 아니라 뇌 신호 의 subject 간 신뢰도 (다른 축) 이고, LOSO (0.23) 는 universal transfer 성능 이지 상한 이 아님.** 둘 다 상한 의 직접 대리 가 아니라 "뇌 신호 품질/공통성" 의 참고 지표. 진짜 상한 은 Cowen 원본 rater-level 확보 시 crowd split-half 로. 다른 ceiling 추정법?
2. **Video dominance 대응 (이 프로젝트 의 가장 날카로운 질문 → Track B 필수 검증 으로 승격).** B2 에서 video (0.60) >> brain (0.30). Distillation (teacher soft label) 이 brain-only student 를 brain 자체 정보 로 학습 시키나, 아니면 video 지식 을 우회 주입 하나? Student 가 video 정보 를 간접 흡수 하면 "brain decoding" 주장 이 무너짐. 열어두지 않고 Track B 의 필수 검증 항목 으로 지정.
   - **검증 A. Variance partitioning.** Student 예측 성능 을 brain 으로 설명 되는 부분 vs video 로 설명 되는 부분 으로 분해. Distillation 이 brain 고유 성분 을 키웠는지, video 공유 성분 만 키웠는지 판정.
   - **검증 B. Brain-ablated student.** Brain 을 shuffle / 제거 한 student 의 남는 성능 측정. 성능 이 크게 안 떨어지면 student 가 brain 을 안 쓰고 있다는 경고 (video 우회 주입 신호).
   - 이 둘 은 §8 다음 단계 의 variance partitioning 과 이어짐. Track B 성공 판정 은 context lift (성능 상승) 뿐 아니라 "brain 고유 성분 이 실제 로 커졌나" 까지 통과 해야.
3. **Pooling trade-off.** Within (0.31) > Pooled (0.29). Universal framing 으로 정당화 하지만, "성능 손해 를 감수 하고 universal 만 본다" 가 reviewer 를 설득할까? Pooled 를 쓰는 더 강한 argument?
4. **절대 수준 (Pearson 0.30 / CCC 0.17) 의 해석.** 이게 "의미 있는 신호" 인지 "너무 낮아 발표 불가" 인지. 비교 가능한 선행 연구 벤치마크? CCC 를 headline 에 추가 했는데, brain CCC 0.17 이 낮은 게 문제 인가 아니면 baseline 이라 당연 한가?
   - **RSA 비교 주의 (apples-to-oranges).** 우리 RSA 0.78 을 EmoMind 의 RSA 0.09 와 직접 대소 비교 하면 안 됨. 두 RSA 는 측정 대상 이 다름. EmoMind 의 RSA = brain-decoded RDM vs caption CK34 RDM 의 cross-modal Spearman (뇌 ↔ 텍스트 라는 이질 공간 정렬 → 원래 낮음). 우리 RSA 0.78 = predicted 34D vs target 34D 의 감정 간 correlation matrix 유사도 (같은 34D label 공간 안 → 원래 높음). 우리 자체 노트 (`docs/notes/emomind_exploitation_20260622.md`) 도 "정량 동일시 금지, 정성 수렴만 주장" 명시. 따라서 "0.78 > 0.09 = 우리가 낫다" 는 성립 안 함. 벤치마크 를 찾을 때 는 같은 정의 의 RSA 여야.
5. **Label 정의.** Crowd proportion (yes/no 비율) 을 continuous regression target 으로 쓰는 게 정당한가? Cowen 원논문 도 averaged proportion 으로 분석. 대안 (binary threshold, ordinal)?
6. **34D independent regression.** Softmax/KL 금지 하고 per-emotion MSE. 감정 간 관계 는 model shared representation + optional structure loss (기본 OFF). 이 설계 가 emotion 의 non-exclusive 성질 을 제대로 다루나?

## 7. 코드 / 재현

모든 결과 는 sklearn ridge, CPU 수 분. 재현 명령 (절대경로).

```bash
# 데이터 준비
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/labels_fit.sh          # 34D z-score (log1p_z)
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/build_roi_timeseries.sh # ROI pt

# baseline + 진단
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/train_baseline_ridge.sh  # B1
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/train_modality_solo.sh   # B2
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/measure_brain_isc.sh     # ISC
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/ridge_subject_regimes.sh # within/pooled/LOSO
```

상세 설계. `Paper/framework_EN.md`. 사이클 로그. `docs/notes/build_log.md`. 결정 로그. `docs/notes/project_decisions.md`. 구현 명세. `docs/notes/implementation_spec_20260702.md`.

## 8. 다음 단계

- Step 4. Models (encoder E1-E4, projector, prompt, LLM backbone). Track A brain-only encoder ablation.
- Step 5-7. Teacher / student / distillation. Track B context lift. **Track B 성공 판정 = context lift (성능 상승) + distillation 검증 (variance partitioning + brain-ablated student) 둘 다 통과.** 뇌 고유 성분 이 실제 로 커졌는지 확인 하지 않으면 video 우회 주입 을 "brain decoding" 으로 오인.
- Step 8. Evaluation 확장 (variance partitioning, cross-subject external test, mixed emotion).

지금 까지 는 세팅 (data + loss + metric) + baseline/진단 (ridge). LLM model 은 아직 없음. Baseline 이 앞으로 모든 LLM 결과 의 참조점.
