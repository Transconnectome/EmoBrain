# EmoBrain Project Decisions Log

Decision 기록은 시간순. 가장 최신이 위.

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
- `README.md`, `README_KR.md`, `CONTEXT_FEEL.md`, `ACTION_PLAN.md` 모두 EmoBrain framing 으로 재작성.
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
- `project/shared/code/probes/run_unified_probe.py:147`, `project/shared/code/probes/run_chance_cat34.py:41`, `project/dir2_multimodal/code/legacy_phase2/_lib.py:41` 의 `CAT34_MULTILABEL_THRESHOLD` 변경.
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
