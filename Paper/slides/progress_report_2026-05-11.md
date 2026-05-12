# 진행 사항 정리

> 2026-05-11 기준

---

## 1. EmoViS

**연구 셋업 — 추가**
- Background → RQ → H1 / H2 narrative 확정 (Barrett TCE 신경 기하구조 수준 검증)
- Brain RDM 5명 + group average (Horikawa 2,185 clips, 450 Schaefer parcel)
- Rating RDM 34 category / 14 dimension
- Video model spectrum embedding 추출 (final layer): VideoMAE v2, DINOv2, V-JEPA2, CLIP, Caption → SBERT
- Framework / methodology / README 정비 (EN / KR), research_overview.html 작성

---

## 2. SwiFT

**Downstream Task 진행 완료 — 추가**
- ADNI: MCI to AD Conversion prediction
- GARD: HC to MCI Conversion prediction
- 유광선 교수님 YooAttn: gradCPT, MOT, VSTM
- Yaakov: DgtSym, LetSet, Syn, WordOrder

오늘 미팅 후 추가 task 진행할 예정

---

## 3. FEELIN

**프로젝트 셋업 — 추가**
- 연구 명: FEELIN (Brain Foundation Model for Emotion-aware Experience Learning In Naturalistic Data)
- Goal / Research Question / Research Gap 확정
- Strategy roadmap: Phase 1 Benchmark → Phase 2 두 갈래 (Branch A: Pretraining + Adaptation, Branch B: Multimodal Brain–Stimulus)
- README, framework_EN/KR, methodology, ACTION_PLAN, research_overview, CONTEXT 정비

**Phase 1 Benchmark 설계 — 추가**
- 3축 매트릭스 확정: Datasets × (BFM × Init) × Tasks
- Datasets 5개: Horikawa / Cowen, Emo-FilM, REELMO, Koide-Majima / Nishimoto, IAPS / OASIS / NSD
- Models × Init: SwiFT, Brain-JEPA, NeuroSTORM 각각 resting-pretrained / scratch (BrainLM은 490 timepoint 비호환으로 제외)
- Tasks 5 levels: L0 high/low V/A binary, L1 V/A regression, L2 one-hot, L3 multi-label, L4 continuous dynamics
- Statistical floor 정의 (logistic / ridge / multinomial / multi-output ridge)
- Pass / Fail 기준 사전 정의 (Δ > 2×SE, Δ > 0.02, perm p < 0.05)

**핵심 결정사항 — 추가**
- Horikawa TR = 2.0 s, HRF shift 4 s 이미 전처리에서 적용 확인 (CSV T1~T_n 컬럼)
- Horikawa subject split: stimulus-stratified (8,740 train / 1,085 val / 1,090 test)
- 노이즈 ceiling: dataset 별 ISC 의무화
- 기존 EmoDe 캐시는 reference로만 사용, 새 benchmark에서 임베딩 재추출

**자동화 인프라 — 추가**
- /scientist-analyze 슬래시 커맨드 작성 (모델 디렉토리 → decision point + blind spot + 실험 트리 자동 생성)
- scripts/scientist_ai.py + scientist_ai.sh (NERSC 독립 실행 가능)

**산출물 — 추가**
- Slide 1: Research Overview + Roadmap
- Slide 2: Benchmark Overview (Datasets × Models × Tasks)
- Slide 3: 8주 Action Items (한국어)

오늘 미팅 후 Week 1 작업 (데이터셋 다운로드, ISC 계산, split manifest, floor 모델) 본격 시작 예정

---

## 4. EmoDe

**Old benchmark cache — 참고용**
- 4 BFM (Brain-JEPA, NeuroSTORM, SwiFT-v2, BrainLM) × Horikawa frozen embedding 결과 산출 완료
- Brain-JEPA 1위 (Pearson r = 0.165 on Emotion34), BrainLM 사실상 chance (r ≈ 0.012)
- 이 결과는 FEELIN Phase 1 benchmark에서 재산출 예정 (split / pooling / pipeline 표준화 후)

---

FEELIN | Progress Report | 2026-05-11
