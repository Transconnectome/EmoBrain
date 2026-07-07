# EmoBrain Project Decisions Log

Decision 기록은 시간순. 가장 최신이 위.

---

## 2026-07-07 (2). report 외부 검토. Stimulus 수 + RSA 비교 오류 정정 + distillation 검증 승격

**Decision.** report_0707 외부 검토 지적 을 verify 후 반영. 사실/해석 오류 2 개 확정 정정.

1. **Stimulus 수 = 2185 unique (재확인).** 검토자 "2196" 제안 → 사용자 정정 + EmoViS DECISIONS (2026-05-08) 확인 결과 **2185 가 맞음**. fMRI 2196 presentation 중 11 개 는 reliability check 중복 (두 번 제시). Unique = 2196 − 11 = 2185. 우리 canonical 2185 정확. 정확한 표현 은 "2185 unique / 2196 presentation w/ 11 repeat". CLAUDE.md 는 이 설명 을 명시 하도록 갱신 (이전 "2185 canonical" 만 이던 것 을 왜 2185 인지 근거 포함).

2. **EmoMind RSA 비교 철회.** "우리 RSA 0.78 > EmoMind 0.09 = 우리가 낫다" 는 apples-to-oranges (성립 안 함). EmoMind RSA = cross-modal (brain RDM vs caption RDM, 원래 낮음), 우리 RSA = same-space (predicted 34D vs target 34D, 원래 높음). 우리 자체 노트 (emomind_exploitation) 도 "정량 동일시 금지" 명시 했었음. report 에서 대소 비교 제거, 두 정의 명시.

3. **Distillation 검증 을 Track B 필수 로 승격.** "distillation 이 brain 정보 를 학습 하나 video 우회 주입 하나" 가 프로젝트 최대 날카로운 질문. 열어두지 않고 Track B 성공 판정 = context lift + 검증 A (variance partitioning) + 검증 B (brain-ablated student). architecture §8.9.2 + ACTION_PLAN S10.2 필수 항목.

**부수 정정.** MindCaptioning 연도 2025 (Science Advances, bioRxiv 2024). Label 스케일 명시 (원점수 0-1 vs log1p_z 후 z-space). ISC 는 decoding ceiling 아님 (신호 신뢰도 축).

**Rationale.** 사실 오류 (stimulus, RSA) 는 리뷰어 즉시 지적. 검토자 가 "반드시 고칠 것 2 개" 로 우선순위 명확히 줌. Verify 후 전부 타당 확인, 반사적 동의 아님.

---

## 2026-07-07. Cowen 2017 원문 검증. "ICC 0.54" 오류 정정 + 34D 라벨 정의 확정

**Decision.** 사용자 지적 으로 Cowen-Keltner 2017 원문 (PMC5617253) 을 직접 검증. 우리 문서 여러 곳 의 "inter-rater ICC ≈ 0.54" 서술 이 오류 임 을 확정 하고 정정.

**원문 사실 (검증).**
- "75% of the videos elicited significant concordance for at least one category of emotion across raters (FDR < 0.05), with concordance averaging 54% (chance level being 27%)".
- **ICC 가 아님.** Concordance = 한 영상 에 같은 emotion category 를 고른 rater 의 비율 (평균 54%, chance 27%).
- 영상 당 9-17 rater 가 34 emotion category 를 yes/no 판단. 34 category 로 rating, 27 cluster 로 축소 (우리 는 34 사용).
- Ratings averaged (individual rater-level 아님).

**34D 라벨 정의 확정 (우리 데이터 로 검증).**
- 우리 label 의 각 값 = 그 category 를 고른 rater 비율 (crowd proportion, 0-1, k/n 형태). "1-9 점수" 아님.
- 우리 데이터 로 확인. Nonzero 값 이 k/n (n = 영상별 rater 수 9-30, median 13, 최빈 12). 기약분수 로 저장 되어 분모 가 달라 보이지만 영상별 고정 rater 수 로 나눈 yes 비율.
- 영상당 34D 합 평균 1.71 (rater 가 영상당 평균 1.7 category 선택). 73.8% 가 0 인 sparse 는 yes/no 응답 의 본질 이지 오류 아님.
- V/A/dominance 등 affective feature 는 별도 1-9 Likert (score 컬럼 과 구분).

**철회된 계획.**
- "ICC 0.54 를 continuous metric 의 ceiling 으로 삼아 fraction normalize" (framework_EN 구 line 425). Concordance 54% 는 categorical 일치율, 우리 headline 은 continuous 34D Pearson. 단위 달라 직접 환산 부적절.
- Stage 0 noise ceiling 의 4 estimator 중 "Cowen-Keltner ICC 0.54" 를 제외. Estimator 는 brain cross-subject ISC + repeated-trial split-half + label crowd split-half + Lage-Castellanos analytical 로 재구성. Concordance 54% 는 참고 값 으로만 인용.

**Files updated.**
- `Paper/framework_EN.md`, `framework_KR.md`. Spine question, sub-question (a), baseline ladder Tier C, "Cowen concordance note" section (구 "inter-rater concordance ceiling anchor"), R0 근거, competitor 비교. 6 곳.
- `docs/notes/architecture_design_20260629.md`. §8.5.4 (제목 + 내용 재작성), §8.5.5 (estimator 에서 concordance 제외), §11 open Q 14.
- `docs/notes/implementation_spec_20260702.md`. §3 (34D 라벨 정의 = crowd proportion), §5-1 (라벨 정의), §5-2 (reporting 변환).
- `ACTION_PLAN.md` Stage 0 estimator. `docs/notes/ppt_outline_20260630.md` sub-question (a).
- 과거 entry (2026-06-30 lock 의 "ICC 0.54") 는 당시 기록 으로 유지, 본 entry 가 supersede.

**Rationale.** 원출처 없이 "ICC 0.54" 를 신뢰 하고 여러 문서 에 전파 했던 오류. 사용자 가 "제대로 확인 하라" 지적 → 원문 직접 검증 으로 concordance (categorical) 임 을 확인. Continuous metric 의 ceiling 으로 쓸 수 없음 이 핵심. 진짜 noise ceiling 은 brain ISC 또는 label crowd split-half 로 별도 측정 필요.

---

## 2026-07-03. Track B scope 축소 + Framework 검증 축 재확인

**Decision.** Track B (P2-B teacher-student distillation) 는 Track A 에서 확정 된 **best encoder 1 개** 만 진행. E1-E4 각각 distillation 하지 않음.

**Framework 검증 축 재확인.**

Framework 검증 의 핵심 은 **"context (video + caption) 가 brain-only 예측 을 얼마나 끌어 올리는가"**. "어느 encoder 가 distillation 이랑 잘 맞는가" 가 아님.

이 두 축 은 명확히 다름.

| 축 | 실험 위치 |
|----|-----------|
| Encoder 순위 확정 | Track A 에서 E1-E4 각각 학습 (brain + question only, direct MSE) |
| Context lift 정량 (framework 검증) | Track B 에서 Track A best encoder × (teacher soft label → student brain-only) |

Encoder 를 여러 개 Track B 로 돌리면 자원 낭비 이자 검증 축 혼동. Encoder 순위 는 Track A 만 으로 확정 됨.

**Spec §13 실험 매트릭스 관계.**
Implementation_spec §13 은 "E1-E4 각각 student + distillation" 도 이론상 나열. 그러나 실용 적 채택 은 Track A best × Track B 1 개 만. §13 원문 은 canonical 로 유지, 실행 계획 은 project_decisions 의 이 결정 이 우선.

**Files updated.**
- `docs/notes/architecture_design_20260629.md` §8.9 Track B 서술 재작성 + 검증 축 명시.
- `Paper/framework_EN.md`, `Paper/framework_KR.md` Track B section 정정 (E1-E4 각각 → best 1 개), Framework 검증 축 강조 문단 추가.
- `ACTION_PLAN.md` S10.2 재작성 (E1-E4 → best 1 개).
- `docs/notes/implementation_spec_20260702.md` §13 에 scope note 추가 (실행 은 best 1 개, §13 은 이론 매트릭스 로만 유지).
- `README.md`, `README_KR.md`, `CONTEXT_EMOBRAIN.md` Track B / distillation 언급 정합.

**Rationale.** 자원 절약 + 검증 축 명확화. Spec §13 은 이론 매트릭스, 실행 spec 은 이 decision 이 우선. Framework 검증 의 primary question 이 encoder × distillation 그리드 로 흐르는 것 을 방지.

---

## 2026-07-02. Code 구현 명세 (implementation_spec) 반영

**Decision.** 사용자 canonical implementation spec 을 `docs/notes/implementation_spec_20260702.md` 로 이동 하고 delta 를 framework / architecture / action plan / CLAUDE 에 반영.

**Spec 위치.** `docs/notes/implementation_spec_20260702.md` (Claude Code 대상, 487 line, DECIDED / OPEN / CAUTION, Acceptance 기준, config schema, repo layout, 34개 감정 순서 포함).

**주요 delta 반영.**

1. **Prompt token 순서 변경 (implementation_spec §6-5).**
   - Teacher. `video → Caption field → brain → Question field`.
   - Student. `brain → Question field`.
   - 이전 default (`brain → video → caption → instruction`, architecture_design §7.2) 폐기. Video 를 앞 에 두어 시각 anchor, brain 을 Question 직전 에 두어 마지막 hidden state 가 brain 반영.
2. **Modality dropout 을 caption 만 유지 (implementation_spec §8-2).**
   - Teacher 학습 시 Bernoulli(p_drop) 로 caption field 제거. Video 는 항상 유지.
   - Red-team recommendation 18 의 "video+caption 둘 다" 를 caption 만 으로 축소.
   - 이유. Video 를 학습 시 빼면 teacher 의 시각 anchor 불안정. Caption dropout 만 으로 도 (a) caption 없는 forward pass 훈련, (b) student 가 teacher 다양성 흡수 목적 달성.
   - p_drop default 0.5, sweep {0.0, 0.3, 0.5, 0.7}.
3. **Cross-subject external test caveat 명문화 (implementation_spec §5-4, §9-4).**
   - MindCaptioning 은 cross-subject 이지만 cross-stimulus 아님 (subject 6 명 이 Horikawa 5 명 과 안 겹치지만 stimulus 는 Cowen 계열 과 겹침).
   - 리포트 마다 "cross-subject external test, NOT cross-stimulus" 명시 필수. Cross-subject 를 cross-stimulus 로 서술 하면 over-claim.
   - Cross-stimulus 평가 는 별도. Horikawa 내부 held-out stimuli split (config `data.holdout_stimuli`) 에서.
4. **Headline metric 확장 (implementation_spec §9-1).**
   - Per-clip 34D profile correlation 을 **Pearson r + Spearman ρ 둘 다** 계산. 이전 spec (Pearson r 단독) 을 확장. Rank 안정성 검증 목적.
5. **34개 감정 canonical 순서 확정 (implementation_spec 부록 A).**
   - admiration, adoration, ..., triumph 의 34개 순서 를 `project/shared/data/cowen34_order.txt` 에 저장.
   - 라벨 / 예측 / mu, std 파일 이 모두 이 순서 를 따르도록 강제.
6. **B1 ridge (LLM 없음) vs E2 ridge encoder (LLM 경유) 구분 명문화.** CLAUDE.md CAUTION 에 포함.
7. **Config schema 위치.** `docs/notes/implementation_spec_20260702.md` §10 이 canonical YAML schema. `project/config/train.yaml` 은 이 spec 을 따름.
8. **Repo layout crosswalk.** ACTION_PLAN 에 implementation_spec `emobrain/` layout ↔ 현재 `project/code/` skeleton 매핑 table 신설. S7 진입 시 crosswalk 적용.
9. **CLAUDE.md CAUTION section 신설.** Implementation_spec §14 의 10 개 CAUTION 을 CLAUDE.md 에 병합 (softmax 금지, train 통계 만, projector text 금지, video 고차 layer, caption 별도 field, encoder 축 독립, E4 full fine-tune 금지, student 최종 평가 form, cross-subject caveat, B1 vs E2 구분).

**Files updated.**
- `docs/notes/implementation_spec_20260702.md` (신규, 이전 `/pscratch/sd/s/sjmoon/EmoBrain/emobrain_implementation_spec.md` 에서 이동).
- `project/shared/data/cowen34_order.txt` (신규, 34개 감정 canonical 순서).
- `docs/notes/architecture_design_20260629.md`. §7.2 token order (teacher/student 별), §8.6.2 caption dropout (video dropout 제거), §9.0 headline metric (Pearson + Spearman), §9.6-9.8 재편 (cross-subject / cross-stimulus / cross-cohort 분리), §12 cross-references (implementation_spec pointer 추가).
- `Paper/framework_EN.md`, `Paper/framework_KR.md`. Token concatenation (teacher/student 순서), Primary metric (Pearson + Spearman), Cross-subject external test caveat (기존 Cross-cohort stretch 를 replace).
- `ACTION_PLAN.md`. Repo layout crosswalk table 신설, config schema pointer, implementation_spec pointer.
- `CLAUDE.md`. Implementation CAUTION section 신설 (10 개 rule).
- `README.md`, `README_KR.md`, `CONTEXT_EMOBRAIN.md`, `ONBOARDING.md`. Pointer 추가 (implementation_spec, cowen34_order.txt), CONTEXT_EMOBRAIN 에 cross-subject caveat section, ONBOARDING 읽을 순서 재정렬.

**Rationale.** 사용자 canonical spec 이 framework 를 실제 로 구현 가능 한 수준 으로 정제. DECIDED / OPEN / CAUTION 구분 + Acceptance 기준 + config schema + repo layout 이 모두 갖춰짐. 지금까지 흩어져 있던 spec 을 하나 의 code-implementation entry point 로 통합. Delta (prompt 순서, dropout 범위, cross-subject caveat, metric) 는 spec 을 canonical 로 삼아 다른 doc 을 정합.

---

## 2026-06-30 (late-4). 감사 지적 3 개 정정 (framework/tools/project README 잔재 제거)

**Decision.** 외부 감사 (codex 검토) 가 지적 한 3 개 미완료 문제 를 정정.

**정정 사항.**

1. **Framework/architecture 본문 의 이전 formulation 잔재 제거.**
   - `Paper/framework_EN.md` §Training paradigm, `Paper/framework_KR.md` §Training paradigm, `docs/notes/architecture_design_20260629.md` §8.6 P2-B 세 곳 에 남아 있던 "P2-B main lock (KL 또는 cross-entropy)" 표현 을 per-emotion MSE 로 통일.
   - Student loss 를 `KL(student_pred || teacher_soft_label) + λ × L_main` 에서 `L_main (subset MSE on z-scored target) + λ × L_distill (subset MSE on teacher 34D)` 로 교체.
   - Teacher soft label caching 을 "34D soft label (probability 또는 logit)" 에서 "34D raw score (softmax 없음)" 로 정정.
2. **Modality dropout 을 student → teacher 로 이동 (red-team recommendation 18).**
   - 이전 spec 은 P2-A modality dropout 을 student 에 배치. Student 는 항상 brain-only 이므로 dropout 무의미.
   - 정정. Teacher 학습 시 video / caption 각각 확률 p=0.3 (grid 0.1 / 0.3 / 0.5) 으로 mask + padding. Soft label 이 다양한 modality 조합 에서 생성 되어 student 의 inference-time OOD 완화.
   - Student 는 modality dropout 없음. Caption dropout (§7.6) 은 별개 유지.
3. **Sanity comparison 추가.** Student-from-teacher (P2-B) vs student-from-hard-label (Track A A4) 을 같은 brain-only input 으로 비교. Tie within noise 면 distillation 이 overhead 로 판정.

**Tools path fix.**
- `tools/check_md_completeness.py`. `CONTEXT_EmoBrain.md` → `CONTEXT_EMOBRAIN.md`, `reference/*` → `docs/reference/*`, `workflows/*` → `docs/workflows/*`, `templates/*` → `docs/templates/*`, `setup/README.md` 삭제, `GENERATED_MARKDOWN` 경로 도 `docs/reports/status/PROJECT_STATUS.md` 로. `DATASET_REQUIRED_BLOCKS` 를 tuple variant 로 relax (`**Role in EmoBrain**` 또는 `**Role**` 수용, SwiFT / TRIBE-specific block 제거).
- `tools/build_project_status.py`. `reference/*` → `docs/reference/*`, `OUT` 경로 를 `docs/reports/status/PROJECT_STATUS.md` 로, `Next Operating Checks` 안 의 `scripts/` → `tools/`.
- `CONTEXT_EMOBRAIN.md`. `Workflow triggers` section 신설 (5 trigger tag 노출).
- `CODEX.md`. `CONTEXT_EMOBRAIN.md` 명시 (agent memory link check).

**project/README.md data schema 정정.**
- §3 architecture diagram OUTPUT 을 NV4 재정의 (34D independent regression + curriculum) 반영.
- §4 데이터 schema 를 §4.1 present (실제 존재), §4.2 S7 생성 예정, §4.3 partial present, §4.4 S7 fetch 예정 으로 4 분할.
- 이전 spec 에서 primary 로 적혀 있던 `roi_timeseries_schaefer400tian50/`, `stimulus_features/qwen_vl_captions.jsonl`, `va_continuous_z.csv`, `cat34_soft_distribution.csv` 는 S7 예정 으로 이동.
- 실제 존재 하는 파일 은 `horikawa_5fold.csv`, `horikawa_split.csv`, `cowen_horikawa_labels.csv`, binary subset 2 개, `feelin_canonical_stimuli.csv`, `stimulus_features/{captions.json, caption_embed.npy, stim_idx.npy, clip/vjepa2/dinov2/videomae × pretrained/scratch .npy}`.
- `cat34_soft_distribution.csv` (sum=1 soft distribution) 은 NV4 재정의 로 폐기. Z-scored raw score 로 대체.

**Tools 실행 결과 (late-4).**
- `tools/build_project_status.py`. Exit 0, `docs/reports/status/PROJECT_STATUS.md` 생성 성공.
- `tools/check_md_completeness.py`. Path/case/trigger/agent memory link 문제 는 모두 해결. 남은 failure 는 `docs/reference/datasets.md` 의 dataset section 이 required block (`**Role in EmoBrain**`, `**Risks**`, `**Source**`) 을 만족 안 함. 이 파일 은 FEEL v2/v3 시절 legacy content 이므로 EmoBrain 5 NV framing 으로 재작성 필요 (별도 작업, out of scope).

**Rationale.** Late-2/late-3 entry 갱신 시 framework 본문 의 Training paradigm section 을 놓쳤음. 새 원칙 (per-emotion MSE, teacher-side dropout) 이 spec 문서 여러 곳 에 걸쳐 있었 는데 일부만 갱신 되고 잔재 가 남아 decision log 와 본문 이 충돌. Tools path fix 는 v5 pivot (dir3_ccn 아래 → single project) 시 tools 를 갱신 안 한 유산. project/README.md data schema 는 forward-looking spec 이 present state 를 앞서 나가는 문제 를 present vs planned 로 분리 하여 해소.

---

## 2026-06-30 (late-3). NV4 correction. Curriculum staging 복구 (KL / softmax 폐기 는 유지)

**Decision.** late-2 entry 의 "curriculum staging 자체 도 폐기" 부분 을 사용자 correction 후 되돌림. Curriculum (top-1 → top-2 → top-k → full 34D) 은 practical stepwise validation tool 로 유지. Softmax / KL / class weighting 폐기 는 그대로.

**사용자 correction (원문).** "우리도 바로 34개 독립으로 갈 건 아니고, 하나씩 일단 해보는지는 확인 해봐야할 것 같아."

**정정 사항.**
1. **Curriculum staging 복구**. top-1 → top-2 → top-k → full 34D 의 4 sub-stage. 하나 라도 학습 되는지 부터 sanity check 후 dimension 확장.
2. **각 stage 의 loss 는 subset MSE**. `L_main(pred, target; A) = sum_{k ∈ A} (pred_k - target_k)^2`. A 가 stage 별 active target subset. 원리 는 여전히 per-emotion independent MSE.
3. **Non-active 감정 처리**. Loss 계산 에서 masked (gradient 없음). Prediction head 는 항상 34-dim.
4. **Stage transition**. 이전 stage checkpoint 에서 weight inherit. Head dim 변경 없음.
5. **Curriculum 의 status**. Practical stepwise validation tool. Stage 4 (full 34D) 가 안정 적 으로 실행 되면 향후 curriculum 없이 direct 34D 로 통합 가능.

**폐기 유지 항목** (late-2 entry 그대로 유지).
- Softmax head.
- KL divergence with 34D distribution target.
- Class weighting (inverse frequency).
- Sum-to-1 constraint.
- Cross-entropy, multi-label BCE.

**Naming 재정리 (2-level 계층).**
- **Track A**. Brain-only direct supervised (context 없음). Track A 안 curriculum sub-stage A1 → A2 → A3 → A4.
- **Track B**. P2-B distillation (teacher context + student brain-only). Track B 안 도 curriculum B1 → B4.

용어 충돌 방지 를 위해 이전 "Stage 1 / Stage 2" 대신 "Track A / Track B" 사용.

**Files updated.**
- `docs/notes/architecture_design_20260629.md`. §8 curriculum 부활 (§8.3 loss 를 subset MSE 로 재정의, §8.3.1 stage 별 active target subset table). §8.9 를 Track A / Track B × curriculum sub-stage 2-level 구조 로 재정리. §2 diagram OUTPUT block 에 curriculum table 추가.
- `Paper/framework_EN.md`, `Paper/framework_KR.md`. NV4 정의 에 curriculum 복구. Loss section 에 subset MSE + curriculum table. "이전 formulation 폐기" section 을 "폐기 부분 vs 유지 부분" 으로 재정리. Two-stage execution 을 Track A / Track B naming 으로.
- `ACTION_PLAN.md`. S8.3 trainer 에 curriculum sub-stage handler + non-active masking. S10.1 을 Track A curriculum A1-A4 로, S10.2 를 Track B curriculum B1-B4 로 재작성.
- `README.md`, `README_KR.md`, `CONTEXT_EMOBRAIN.md`. NV4 한 줄 요약 + architecture diagram OUTPUT block 에 curriculum table 추가.

**Rationale.** 사용자 의 실용 적 우려. 처음 부터 34 개 모두 학습 가능 한지 는 open. Curriculum staging 으로 하나 라도 되는지 확인 후 확장 하는 것 이 안전. Section 9 의 34D independent 원칙 은 curriculum 과 orthogonal (curriculum 안 에서 도 subset MSE 로 원칙 준수 가능). 두 아이디어 (curriculum + independent MSE) 를 결합 하면 practical validation + principled formulation 을 동시 달성.

---

## 2026-06-30 (late-2). NV4 재정의. 34D independent regression + z-score + MSE (curriculum + KL + softmax 폐기)

**Decision.** 사용자 canonical summary section 9 반영. NV4 를 "4-stage curriculum with KL on 34D softmax" 에서 "34D independent emotion regression with per-emotion MSE" 로 근본적 재정의.

**핵심 원칙.**
1. **34 개 감정 은 서로 경쟁 하지 않음**. Bittersweet 처럼 기쁨 과 슬픔 이 둘 다 높을 수 있음. Softmax / sum-to-1 / KL divergence / cross-entropy / multi-label BCE 사용 금지.
2. **필수 전처리 = per-emotion z-score**. 감정 별 로 mean 0, std 1 로 rescale (training set fit, test set transform). 클래스 불균형 이 curriculum 이 아니라 z-score 로 해결.
3. **Loss = per-emotion MSE sum**. `L_main = sum_{k=1..34} (pred_k - target_k)^2`. 34 개 독립 항. Class weighting 불필요.
4. **Distillation 도 동일 원칙**. Teacher 34D soft label caching, student 가 per-emotion MSE 로 재현. `L_distill = sum_k (student_k - teacher_k)^2`. Softmax 금지.
5. **시작 = teacher 없이 direct MSE, 그 다음 distillation 얹기**. Curriculum staging (top-1 → top-k → 34D) 자체 가 불필요.

**Loss ≠ metric.**
- Loss (MSE) = 학습 을 굴리는 연료.
- Metric = 결과 를 채점 하는 성적표.
- **Headline metric = per-stimulus 34D profile shape similarity**. 개별 감정 점수 정확도 가 아니라 영상 하나 에 대한 34 개 숫자 의 전체 profile shape 이 정답 profile 과 닮았는지. Per-stimulus Pearson r 34D vector correlation (또는 cosine similarity), test stim 마다 계산 후 mean.

**폐기 된 formulation.**
- ~~4-stage curriculum (top-1 → top-2 → top-k → full 34D KL)~~. 34D 를 distribution 으로 오해 한 결과.
- ~~34D softmax head~~. 34 개 감정 이 서로 경쟁 하지 않으므로 부적절.
- ~~KL divergence with rater empirical distribution target~~.
- ~~Class weighting (inverse frequency)~~. Z-score 가 이미 균등 가중.
- ~~Curriculum stage 간 checkpoint inheritance~~. Stage 개념 자체 삭제.

**새 실행 순서 (§8.9 의 2-stage validation order 로 이동).**
- Stage 1. Teacher / context 없이 E1-E4 를 34D 독립 점수 에 직접 지도 학습. Loss = per-emotion MSE sum, z-score 전처리.
- Stage 2. Stage 1 의 best encoder 위 에 teacher (brain+video+caption) 학습 → 34D soft label cache → student (brain-only) 가 teacher 34D 를 MSE 로 재현.

**새 OD.** OD-D2 (distillation loss weight λ, 0.5 / 1.0 / 2.0 grid). ~~OD-E (KL target smoothing)~~ SUPERSEDED (KL 자체 폐기).

**Files updated.**
- `docs/notes/architecture_design_20260629.md`. §2 diagram OUTPUT block (softmax + KL 제거 → 34D regression + MSE). §8 전체 재작성 (4-stage curriculum → NV4 34D independent regression). §8.1-8.6 (정답 형식, z-score preprocessing, MSE loss, distillation loss, aux recon, metric). §8.9 (2-stage validation order 의 MSE + distillation 반영). §9.0 (headline metric = per-stimulus profile shape).
- `Paper/framework_EN.md`, `Paper/framework_KR.md`. NV4 정의 재작성 (Section 5 Novelties). "4-stage curriculum" 큰 섹션 을 "34D independent emotion regression" 으로 대체. Evaluation Primary metric 을 per-stimulus profile shape headline 으로.
- `ACTION_PLAN.md`. S8.2 (dist_head.py → regression_head.py, softmax 없음). S8.3 (curriculum stage 별 CE / KL → per-emotion MSE + distillation MSE). S8.4 (train_curriculum.yaml → train.yaml + z-score sanity check). S10.1 (top-1/2/k/full 삭제 → Stage 1 direct MSE 단일). S10.2 (student loss KL → MSE distillation). OD-E SUPERSEDED, OD-D2 신설.
- `README.md`, `README_KR.md`, `CONTEXT_EMOBRAIN.md`. NV4 한 줄 요약 갱신. Architecture diagram OUTPUT 블록 재작성.

**Rationale.** 이전 NV4 formulation 은 두 가지 실수. (a) Cowen-Keltner 34-cat rating (1-9 독립 Likert) 을 probability distribution 으로 오해 하여 sum-to-1 constraint 부여, (b) 클래스 불균형 문제 를 curriculum staging 으로 해결 하려 했으나 z-score preprocessing 이 훨씬 더 clean 한 해법. Bittersweet 같은 mixed emotion 이 34D 를 non-competitive 로 취급 해야 하는 이유 의 최종 증거.

---

## 2026-06-30 (late). Framework master summary 반영 (사용자 제출 summary 문서)

**Decision.** 사용자 canonical framework summary (`emotion_framework_master_summary.md`) 를 architecture_design + framework_EN/KR + ACTION_PLAN 에 반영.

1. **Novelty 위치 재확인.** Framework 자체 (multi-modal 학습 + brain-only 추론 비대칭 + modality 별 역할 분리 + 34D 고차원 readout) 가 novelty. E1-E4 encoder ablation 은 framework 가 열어주는 후속 질문 이지 spine result 아님. "어떤 encoder 가 best 인가" 는 spine question 아님.

2. **공통 patchify frontend 없음 을 명문화.** fMRI 가 곧장 각 encoder 로 들어가고 patchify 는 각 encoder 내부 에서 발생. 공통 인 것 은 output 이 brain token 이라는 사실 뿐. 진짜 변수 는 사전 학습 유무 + fMRI 적응 설계.

3. **Prompt 구조 명문화.** Caption field vs question field 로 분리. Question 은 모든 sample fixed → shortcut 아님. 진짜 shortcut 위험 은 caption 이 brain 을 대신 하는 경로 → student 학습 시 caption field 만 확률적 dropout, question 은 항상 유지.

4. **Teacher-student prompt asymmetry + caption dropout 이중 효과.** (a) Student 가 caption 없는 prompt 에 미리 익숙 해짐 (distribution shift 완화), (b) Student 가 caption 을 못 기대 하게 되어 brain-only 신호 를 강제 학습. Dropout 확률 = OD-P (0.5 / 0.7 / 0.9 grid).

5. **Caption-video overlap 대응 절차 lock.** 세 가지. (i) Video 를 caption 위 에 residualize 후 잔차 caption 조건 vs 원본 caption 조건 비교, (ii) Full / no-caption / no-video / brain-only 4 조건 ablation, (iii) 초기 layer 하강 회피 (V-JEPA2 마지막 hidden 유지, 저수준 residualize 후 에도 categorical 연속 성 유지 라는 CCN evidence).

6. **Caption 중립성 검증 절차 lock.** MindCaptioning 규정 인용 만 으로 는 부족. `verify_caption_neutrality.py` 로 substring match + 100 개 sample 인간 검토. S7 gate.

7. **2-stage validation order lock.** Stage 1 (context 없는 direct 34D supervised, brain-only) 완료 를 gate 로 Stage 2 (P2-B distillation) 진입. Stage 1 만 성공 해도 modular encoder ablation + high-D readout 이 하나 의 contribution 으로 publishable. Stage 2 실패 도 P2-B limits 로 별도 finding.

8. **Primary metric 재확인.** 1 차 = 고차원 구조 보존 (per-emotion Pearson r, rare-emotion recovery, 34×34 correlation matrix Frobenius norm, dimension compression curve) + LOSO cross-subject 일반화. 2 차 = 절대 정확도 + ridge sanity check. Ridge 0.72 는 valence binary 특정, 34D floor 아님.

9. **새 OD 4 개.** OD-P (caption dropout 확률), OD-T (projector token 개수, bottleneck width), OD-R (residualize 절차), OD-V (Stage 1 vs Stage 2 sequential vs parallel, sequential default).

**Files updated.**
- `docs/notes/architecture_design_20260629.md` §4 (E1-E4 재정의 + patchify note + projector 두 목적), §7.5-7.6 (prompt field + caption dropout), §8.8 (caption-video overlap), §8.9 (2-stage order), §9.0 (primary metric), §11 (open Q 16-19).
- `Paper/framework_EN.md`, `Paper/framework_KR.md`. Modular brain encoder section (patchify note + encoder 순위 spine 아님), Multi-modal fusion (prompt field + teacher-student asymmetry), 새 section (caption-video overlap).
- `ACTION_PLAN.md`. S7.6 (caption 검증 + residualize), Stage 0 (S10 gate), S10.1-10.3 (2-stage validation + ablation). Open decisions OD-P/T/R/V 추가.

**Rationale.** Red-team recommendation 과 사용자 summary 가 대부분 수렴. Summary 의 novelty framing (framework > encoder) 이 그동안 문서 여러 곳 에서 흔들렸음. 이번 갱신 으로 canonical framing lock.

---

## 2026-06-30. NV3 framework final lock. P2-B distillation main + R0 + Stage 0 ceiling estimation

**Decision.** Lock the NV3 framework with the following.

1. **Training paradigm.** P2-B knowledge distillation 이 main, light P2-A modality dropout 이 auxiliary, P2-C alignment 는 excluded (structural conflict with P2-A).
   - Teacher. brain + video + caption 의 3-modality 학습, Qwen3-VL backbone + LoRA-A.
   - Student. brain-only 학습, 같은 backbone + LoRA-B, distillation target = teacher 의 34D soft label.
   - Soft label 의 caching 후 student 학습 cost 가 단일 model 과 유사.

2. **Three-stage execution.**
   - Stage 0. Noise ceiling estimation (ISC + repeated-trial split-half + Lage-Castellanos 2019 analytical + Cowen-Keltner ICC 0.54 의 theoretical max).
   - Stage 1. Brain-only direct supervised E1-E4 의 encoder ablation. Teacher 없음, context 없음.
   - Stage 2. P2-B distillation 의 context contribution measurement (Stage 1 의 best encoder 위 에서).

3. **Pre-registered success criterion (ceiling-anchored).**
   - `gap_filled = (best_encoder_brainonly - ridge) / (noise_ceiling - ridge)`.
   - Case I (noise_ceiling - ridge < 0.05). R0 realized. Framework reframing 필요.
   - Case II (0.05 - 0.15). Narrow headroom. Reservation 명시.
   - Case III (> 0.15). Wide headroom. 정상 진행.

4. **Risk 추가. R0.** Noise ceiling 자체 가 ridge 와 가까움. High prior probability (Phase 1 의 6 BFM variant plateau + D1 v1/v2 의 3 size plateau + Cowen-Keltner ICC 0.54 의 absolute ceiling). Stage 0 이 직접 test.

5. **Ridge baseline 의 reframing.** Floor to beat 가 아닌 sanity-check reference on same 34D task. Ridge 0.72 의 valence binary 가 우리 34D task 와 같은 자 위 에 있지 않음.

6. **Primary metric 의 변경.** 절대 accuracy 가 아닌 high-D structure preservation (per-emotion correlation + rare-emotion recovery + inter-dimension correlation preservation + dimension compression curve).

7. **Negative outcome publishability spec.** Distillation 의 boost near-zero 가능. 그 경우 의 publishability 의 minimum = variance partitioning (teacher 의 modality 별 unique contribution) + transfer gap analysis vs noise ceiling. Negative outcome 의 단독 보고 금지.

8. **E4 label 확정.** "Image pretrain + fMRI fine-tune" (NOT "image pretrain only"). D1 의 fMRI 적응 단계 가 가려지지 않도록.

**Rationale.**

Multi-round critic feedback 의 수렴.
- 2026-06-29 의 3-panel review (literature + methodology + publishability).
- 2026-06-30 의 후속 2 round 의 adversarial critique.

핵심 통찰.
- P2-A + P2-C 의 combination 의 structural conflict. P2-C 의 alignment 가 video 의 representation 을 brain token 으로 leak back. P2-B 의 teacher/student 분리 가 이 leakage 회피.
- Ceiling-anchored framing 의 의미. Encoder competition 이 *의미 있는* 것은 headroom 이 존재 할 때 만. headroom 의 width 의 estimate 없이 encoder ranking 보고 는 R0 risk 의 무시.

**Action items.**
- Caption neutral 의 verify (pending). MindCaptioning sample 의 affect vocabulary substring match.
- Stage 0 noise ceiling estimation (pending). 4 estimator 의 implementation + consensus value 의 확정.
- gap_filled threshold 의 final lock (pending). Stage 0 결과 + literature consensus 후 학습 시작 전 lock.

**영향.**
- `Paper/framework_EN.md` + `framework_KR.md` 에 §Training paradigm + §Two-stage execution + §Risks (R0) + §Negative outcome reporting + SC6 의 추가.
- `docs/notes/architecture_design_20260629.md` 에 §8.5 Stage 0 noise ceiling protocol + §8.6 Training paradigm details + §8.7 Pre-registered success criterion 의 추가.
- §11 Open Questions 의 13-15 (caption neutral + Stage 0 timing + gap_filled threshold) 의 추가.

---

## 2026-06-29. Spine pivot. Direction 폐기 + single project + framework novelty path

**결정.**

1. **EmoBrain 의 project framing 의 변경.** D1 BrainVLM / D2 fMRI-LM / D3 CCN 의 3 direction split 폐기. **single project = 한 paper**.
2. **Title lock.** *"EmoBrain: Decoding fine-grained emotion from human brain activity."*
3. **Spine = framework novelty path** (R-full-new). 5 novelty 의 결합 의 multi-modal foundation model.
    - NV0. LLM-based brain emotion decoder. emotion 분야 의 LLM 통합 의 first instrument.
    - NV1. 3-modality (brain + video + caption) 의 LLM 통합 fusion.
    - NV2. MindCaptioning 의 human-written neutral caption 의 brain-context bridge.
    - NV3. Modular brain encoder (raw / Ridge / BFM / VLM 의 swappable).
    - NV4. 34-distribution output 의 4 stage curriculum (top-1 → top-2 → top-k → full distribution KL).
4. **기존 작업 (Phase 1, D1, D2, D3) 의 보존.** Section 4 (modular brain encoder ablation) 의 evidence 로 활용. 결과 의 *날리지 않음*.

**근거.**

2026-06-29 의 Mode 3 panel (literature + methodology + publishability 의 3 agent parallel) 의 수렴 verdict.

(a) **Reframe option A/B/C/D 의 evaluation.** 모두 약 함 또는 redesign 필요. spine reframe 의 진짜 답 = 새 framework novelty path 의 R-full-new.

(b) **EmoMind 의 NeurIPS 의 borderline-to-reject 의 predicted verdict** (literature + publishability agent 의 수렴). 단 framework novelty path 의 *path 자체* 는 publishable. 우리 도 같은 path.

(c) **우리 의 4 backbone 의 plateau 의 결과.** capacity 의 issue 가 아닌 *output formulation + multi-modal 의 부족* 의 의심. 새 framework 의 5 NV 의 결합 의 시도 의 의미.

(d) **사용자 의 design 의 결정.** "fMRI → Brain Encoder (modular) + Video → Vision encoder + MindCaptioning caption + Prompt → LLM 통합 fusion → 34D distribution output" 의 architecture 가 emotion 분야 의 first.

**영향.**

- 새 directory `project/code/` 생성 (adapters/brain_encoder/vision_encoder/caption_loader/fusion/training/evaluation 의 subdirectories).
- `archive/v5_direction_split_20260628/` 생성. 기존 dir1_brainvlm/dir2_fmri_lm/dir3_ccn 의 symlink reference (학습 종료 후 진짜 mv).
- `Paper/framework_EN.md` + `framework_KR.md` 통째 rewrite (직전 의 D1/D2/D3 framing 폐기, single project + 5 NV 의 spine).
- `README.md` + `README_KR.md` + `CONTEXT_EMOBRAIN.md` + `ACTION_PLAN.md` update.
- 기존 D1 의 학습 (REG variant 의 VA binary + regression) 의 *그대로 진행*. 결과 는 paper 의 Section 4 의 modular encoder ablation 의 일부 로 활용.

**다음 step (12-16 주 의 큰 build).**

- S7. 3-modality adapter (brain + video frame + MindCaptioning caption + 우리 generated caption) 의 dataset 통합.
- S8. Multi-modal model 의 main + trainer (LLM 의 multi-modal token fusion + 34D head + soft KL target).
- S9. SMOKE test + 사용자 launch.
- S10. 4 stage curriculum 학습.
- S11. Evaluation (variance partitioning + ceiling anchor + dissociation) + paper draft.

---

## 2026-06-28. D1 BrainVLM VA task 2/2 FAIL 확정 + Option B + C 병렬 진행

**결정.**
1. D1 BrainVLM 의 *XML token output + cross-entropy* setup 의 fundamental limit 확정. Plan A (Qwen3-VL family size sweep, 2B/4B/8B/v1+v2) 의 학습 종료.
2. **Option B (Plan C). Regression head 직접 attach** code 작성 시작. main_umbrella_training_qwen 의 새 variant. backbone hidden state → small MLP → scalar 직접 numeric output. cross-entropy 대신 MSE.
3. **Option C. D2 fMRI-LM (Wei 2026 architecture)** code 작성 시작 (병렬). 3-stage (ViT tokenizer + paired alignment + instruction tuning).
4. 두 옵션 의 학습 결과 비교 1 주 후 + spine 의 next iteration 결정.

**근거.**

(a) **2/2 VA task FAIL + 4 backbone size 모두 동일 plateau.**

| Backbone | VA binary best token_acc | VA regression best V Pearson r |
|---|---|---|
| 2B (v1, lr 5e-4 epoch 50) | 0.597 (vs baseline 0.720) | 0.035 (vs baseline 0.416) |
| 4B (v2, lr 1e-4 epoch 10) | 0.586 | 0.008 |
| 8B (v2, lr 1e-4 epoch 10) | 0.606 | (학습 안 됨) |

token_acc 0.6 plateau = XML boilerplate token 의 match 의 noise. 실제 numeric Pearson r 의 학습 거의 없음 (baseline 의 1/10 ~ 1/20).

backbone size 의 increase 가 *전혀 차이 안 만듦* = backbone capacity 의 issue 가 아님 = *output formulation 의 fundamental limit*.

(b) **Root cause = token-level autoregressive output 의 형식 한계.** Model 이 number 를 *digit by digit token* 으로 출력 → cross-entropy loss 가 *digit-level token distribution* 학습 → brain signal 의 continuous nature 와 mapping 안 됨.

(c) **EmoMind 의 paradigm 의 시사.** EmoMind (Mohammed et al., 2026) 도 stage 1 에서 *ridge regression 으로 brain → 34D vector 의 continuous mapping 직접 학습* + stage 2 에서 token output 은 *condition 으로 만* 사용. 우리 도 *token output 의 mapping 학습 폐기 + continuous head 직접 attach* 의 paradigm 으로 가야 함.

**영향.**

- `docs/reports/d1_brainvlm_va_negative_result_20260628.md` 작성 = 본 결정 의 evidence base.
- `Paper/framework_EN.md` + `Paper/framework_KR.md` 의 §Status section update. VA 박살 + 4 backbone size FAIL + Option B+C plan.
- `project/dir1_brainvlm/code/` 에 새 variant `main_umbrella_training_qwen_NoPool_REG.py` 작성 (Option B).
- `project/dir2_fmri_lm/code/` 시작 (Option C).
- 1 주 후 두 옵션 의 결과 비교 + spine 의 next iteration (SC1 의 재시도 또는 reframe).

**Lessons learned.**

- token_acc 같은 *string-level metric* 은 *task-native metric* (Pearson r, balanced acc, AUROC) 과 분리 reporting. token_acc 0.638 의 *misleading appearance* 의 trap 회피.
- Baseline 의 *exact 비교 가능 한 metric* 학습 *전* 에 확정. learning curve 의 *진짜 의미* 가 학습 중 보이게.
- 50 epoch full training 의 cost (24-48 hr/task) 전에 *5 epoch pilot* 으로 actual metric (Pearson r) 확인.
- Backbone size sweep 의 진단 가치 (size 의 issue 인지 output formulation 의 issue 인지 분리).

---

## 2026-06-24. Spine rewrite. SQ 4 component + Model 3 trick + VA binary FAIL

**결정.** Framework 의 spine 을 이전 SC1-3 (outcome 위주 framing) 에서 **SQ 4 component + Model novelty 3 trick + Status** 의 3 축 spine 으로 재구성.

**SQ 4 component.**
- (a) Universal region map. 같은 영상 의 5 brain 의 model attention 일치 ROI.
- (b) Idiosyncratic region map. attention 갈 림 ROI.
- (c) Stimulus law. 영상 별 prediction error 와 영상 property 의 correlation.
- (d) Cross-subject transfer. 4 subj train → 5th subj zero-shot via ICL.

**Model novelty 3 trick.**
- T1. Multi-image ICL with cross-subject pool. 여러 사람 brain 한 prompt. SQ-(d) instrument.
- T2. Subject ID embedding tag. 사람 별 path 분리. SQ-(a)(b) instrument.
- T3. ROI-attention readout head. 학습 부산물 로 region map. SQ-(a)(b) instrument.

**근거.**
1. **이전 candidate spine = NQ3 (caption 을 brain emotion decoding 실패 mechanism evidence 로 사용 하는 trial-level variance decomposition) 폐기.** 2026-06-24 의 3-panel red-team review (literature critic + methodology critic + publishability critic 의 parallel spawn) 의 fatal flaw 3 개 수용.
    - Caption circular instrument. caption 이 same LoRA downstream, prediction 과 같은 weight 산물, brain evidence 가 model internal consistency 와 분리 불가.
    - N=5 subject d.f.=4 underpowered. variance decomposition 의 dominance 주장 통계 적 불가.
    - Story coherence mismatch. 6 task suite + LoRA + ICL 의 train objective 가 multi-task generalization, variance decomposition 아님.
2. **위 SQ 4 component 가 우리 자산 + model design 과 perfect align.** Story coherence 확보.
3. **Bush 2018 / EmoMind / MindCaptioning 의 어느 paper 도 4 component 통합 측정 안 함.** 진짜 incremental novelty (literature critic 의 verdict "marginally new, but integration novel").
4. **EmoMind 와 의 spectrum framing 유지.** EmoMind = per-subject endpoint, EmoBrain = universal endpoint. 정면 충돌 X.

**Model novelty 의 EmoMind 대응.** EmoMind 의 axis matrix A (34×768) + classifier-free guidance + 2-stage retrieval+rewriter 와 의 architectural 대응 = 우리 의 T1 + T2 + T3.

**Video form decision.**
- Main paper = brain only. Horikawa silent video 의 visual content 는 input 으로 안 넣음.
- Supplementary = brain + video raw frame. 학습 후 추가 학습 1 form 만. SC3 의 multi-modal lift 측정 용.
- CLIP feature / caption / low-level feature = 안 함 (scope creep 회피).

**SC revised.**
- SC1. Universal code existence. pooled VLM ≥ Phase 1 ROI ridge baseline.
- SC2. Cross-subject transfer. LOSO setting 의 zero-shot 평가.
- SC3. Multi-modal lift (supplementary). brain+video vs brain-only.
- SC4. Multi-task consistency. 6 task output internal consistency.

**Status. VA Binary FAIL 의 1 차 evidence.**
- D1 BrainVLM 의 V/A binary 학습 완료 (50 epoch, 1750 step).
- Best ckpt = step 200 (epoch 5.7), token acc 0.597.
- **Phase 1 ROI mean + Ridge baseline (balanced acc 0.720) 못 넘 음. SC1 의 first task FAIL.**
- Final ckpt 의 acc 0.49 (chance 아래). epoch 6 peak 후 collapse. 심한 overfit.
- 원인 후보. LR 5e-4 너무 큼 / LoRA capacity mismatch / token-level prediction 의 형식 한계 / ICL ref random 의 noise.
- VA regression 학습 진행 중. 결과 가 SC1 운명 결정.

**영향.**
- `Paper/framework_EN.md` + `Paper/framework_KR.md` rewrite (SQ 4 component + Model 3 trick + revised SC + Status section + EmoMind positioning + open decision 6).
- `docs/notes/paper_spine_v1.md` + `docs/notes/evaluation_framework_v1.md` 폐기 (CLAUDE.md rule "narrative 는 Paper/framework_EN.md, framework_KR.md" 위반 file. 합의 내용 모두 framework_EN/KR 로 이전 후 제거).
- `ACTION_PLAN.md` 의 stale reference (paper_spine_v1.md, evaluation_framework_v1.md) 정리 + framework_EN reference.
- 다음 action. (1) VA regression 결과 대기, (2) Plan B hyperparameter tuning 의 trigger 결정 (regression 도 FAIL 인 경우), (3) Cat34 학습 진행.

---

## 2026-06-08 (today). Framing pivot v4 → EmoBrain (sj_NEW_20260608_perlmutter)

**결정**. 기존 v4 framing (universal emotion code 검증, Track A SSL pretrain main + Track B Multimodal main + Track C BrainVLM supplementary) 를 EmoBrain framing (BrainVLM main + Brain-Video Multimodal main 의 2 axis) 로 전환.

**근거**.
1. Phase 1 측정 결과 (`reports/phase1_audit_20260604/`) 가 frozen BFM (BJ, NS, SwiFT 6 변종) 이 simple ROI baseline 을 못 넘음을 확정. V/A binary, V/A reg, Cat34 multilabel, Cat34 soft 모든 task 에서 일관. 원인은 Horikawa 자극의 짧은 T 분포 (median 5 TR, 71.6% 가 T=5) 와 BFM 입력의 평균 63-70% zero padding.
2. Broader field trend 가 frozen BFM 단독 대비 VLM / LLM 기반 brain decoding 의 우세를 보여줌. MindLLM (2025) subject-agnostic fMRI-to-text, UMBRAE (ECCV 2024), Mind Captioning (Horikawa Science Advances 2025) 모두 frozen LLM/VLM 을 prior 로 활용. BFM frozen embedding 단독은 거의 안 보고됨.
3. Multimodal brain alignment 의 standard evaluation 정착. TRIBE (Meta FAIR, Algonauts 2025 1 위) 의 frozen large encoder + transformer fusion + variance partitioning 이 표준. EmoBrain 의 Direction 2 가 그 framework 의 emotion specific 확장.

**영향**.
- Branch `sj_NEW_20260608_perlmutter` 신설. 이전 framing 은 `archive/v4_20260602/` 에 보존.
- BFM 의 main 작업 (Track A SSL pretrain, subject-invariant SSL 학습) 은 main scope 제외. 단 Direction 2 의 brain encoder 후보로 활용 가능.
- 새 main = Direction 1 BrainVLM + Direction 2 Brain-Video Multimodal. 둘 다 main, complementary.
- EmoFM 이라는 name 후보가 BFM 의미와 충돌하므로 EmoBrain 으로 전환.

**문서 update**.
- `README.md`, `README_KR.md`, `CONTEXT_EMOBRAIN.md`, `ACTION_PLAN.md` 모두 EmoBrain framing 으로 재작성.
- `docs/masterplan_v3_emobrain.md` 작성 예정.
- `Paper/framework_EN.md`, `framework_KR.md`, `methodology.md` 재작성 예정.
- 이전 .md 는 `archive/v4_20260602/` 에 보존.

---

## 2026-06-07. Cat34 multilabel threshold 변경 0.15 → 0.10

**결정**. Cat34 multilabel task 의 threshold 를 `0.15` 에서 `0.10` (= 1/10 raters, 자연 단위) 으로 변경.

**근거**. Threshold sensitivity 분석 (`reports/phase1_audit_20260604/` 의 Cat34 audit).
1. **자연 단위**. 0.10 = "rater 의 10% (= 10 명 중 1 명) 이상 평가" 의 명확한 의미. 0.15 는 1/8 과 1/6 사이 임의 round number, 자연 단위 아님.
2. **모든 자극이 supervision 받음**. 0.10 에서 zero-label 자극 = 0 (모든 자극이 적어도 1 category 양성). 0.167 부터 일부 자극에서 양성 없음.
3. **Minority category 안정성**. 0.10 에서 가장 minority category 의 양성 비율 0.007 (= 약 15 자극). 5-fold CV 에서 fold 당 3 자극, 학습 안정. 0.15 는 0.0037 (= 8 자극) 으로 fragile.
4. **mixed emotion 의 적절한 표현**. 0.10 에서 평균 자극당 4.93 cat 양성. Vaccaro 2024 의 mixed valence framework 와 일관.

**영향**.
- `project/shared/code/probes/run_unified_probe.py:147`, `project/shared/code/probes/run_chance_cat34.py:41`, `project/dir3_ccn/code/legacy_phase2/_lib.py:41` 의 `CAT34_MULTILABEL_THRESHOLD` 변경.
- Cat34_multilabel + Cat34_soft 재측정 launch. 결과 CSV 는 `_t010` suffix 로 저장 (기존 0.15 결과 보존).
- 발표 / paper 의 method section 에 threshold 선택 근거 명시.

---

## 2026-06-04. Phase 1 audit + BFM 의 한계 확정

**결정**. Phase 1 의 5 단계 deep audit (1A 임베딩 → 1B video features → 1C probing code → 1D task definitions → 1E results consistency) 진행. 모든 audit 결과는 `reports/phase1_audit_20260604/` 에.

**주요 발견**.
- E1 (BFM 의 T 처리 정책 모델별 상이). BJ center crop 16 TR, NS/SwiFT first 20 truncate.
- E2 (BJ pretrained checkpoint adaptation). pos_embed 10 time patches → 1 평균 + patch_embed kernel linear interp.
- E3 (Horikawa T 분포 짧음). median 5, 71.6% T=5, BFM 입력의 평균 63-70% zero.
- F8 / F13 (Cat34_top1 broken folds). 일부 fold 에서 minority class 가 train 에 없음. 결과 unreliable, 제외 권고.
- F_C5 (NeuroSTORM wrapper 중복). single + split 둘 다 존재, 어느 게 main 인지 확인 필요.
- F_C6 (Cat34 multilabel / soft 의 MLP 결과 없음). `--skip_mlp` 로 launch.

**Phase 1 결론**. Frozen BFM 이 simple ROI baseline 을 넘지 못함. EmoBrain framing pivot 의 evidence base.

---

## 2026-06-04. Phase 1 method + result PDF 작성

**결정**. Phase 1 의 method (data, split, BFM extraction, probing protocol, tasks, baselines) + result (V/A binary, V/A reg, Cat34 multilabel + soft 의 BFM vs ROI vs chance 비교) 를 한국어 + LaTeX 로 정리한 self-contained PDF 작성.

**위치**. `reports/phase1_audit_20260604/_pdf/main.pdf` (10 page).

**의의**. 발표 / hackathon / paper 의 reference 자료.

---

## 2026-06-04. Cat34 baseline 보강 (ROI + chance)

**결정**. Cat34_multilabel + Cat34_soft 의 ROI baseline 과 chance baseline 이 phase 1 launch 에서 누락된 점 발견. 보강 launch (`cat34_roi.sh` + `cat34_chance.sh`). 코드 `project/shared/code/probes/run_chance_cat34.py` 신설.

**결과**. Cat34_multilabel macro AUROC: ROI 0.711, BJ resting 0.679, NS 0.669, SwiFT NewE96 0.629, chance 0.500. ROI 가 모든 BFM 보다 높음, Phase 1 의 V/A 패턴과 동일.

---

## 2026-06-04. Zero padding only 결정

**결정**. Phase 1 의 BFM embedding 분석 scope 를 zero padding 만 사용으로 통일.

**근거**. mean padding 과 spatial_only padding 의 결과가 cosine 0.9999 이상으로 사실상 동일 (mean padding 재추출 의도 안 됨). Replicate / cyclic_replicate 도 mean 과 매우 가까움. Zero padding 만 명확히 다른 representation 산출. Padding 변종 ablation 의 단순화.

**영향**. Audit 보고서 (`reports/phase1_audit_20260604/1A_embeddings.md`) 의 scope 갱신.

---

## 2026-06-02. v4 framing 정리 (이전 framing, 현재 archive)

이전 framing 의 decision log 는 `archive/v4_20260602/notes/project_decisions.md` 에 보존.
