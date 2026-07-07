# EmoBrain Claude Instructions

Read `CONTEXT_EMOBRAIN.md` first. Active spine narrative 는 `Paper/framework_EN.md` + `Paper/framework_KR.md`, architecture spec 은 `docs/notes/architecture_design_20260629.md`, ground-level action 은 `ACTION_PLAN.md`.

Project name = EmoBrain (2026-06-08 rename, path preserved). Repo path `/pscratch/sd/s/sjmoon/EmoBrain/`. 이전 framing 은 `archive/` 아래 보존.

## Operating Rules

- Root .md 파일 새로 만들지 않음. 7 개 (README.md, README_KR.md, CONTEXT_EMOBRAIN.md, ONBOARDING.md, CLAUDE.md, CODEX.md, ACTION_PLAN.md) 로 유지.
- Forward plan / phase report 은 `docs/` 와 `docs/reports/` 에만 추가.
- Narrative 는 `Paper/framework_EN.md`, `framework_KR.md`.
- Methodology 는 `Paper/methodology.md`.
- Decision log 는 `docs/notes/project_decisions.md` (chronological, 최신 위).
- 실험 코드는 single unified pipeline. `project/code/{adapters,brain_encoder,vision_encoder,caption_loader,fusion,training,evaluation}/` (main). 공통 자원은 `project/shared/code/{probes,bfm_embeddings,ssl_pretrain,analysis,tools}/`.
- 입력 데이터 (splits, target matrix) 는 `project/shared/data/`.
- 추출된 features / log 는 `project/shared/output/`.
- 분석 결과 (CSV, figure, slide text) 는 `project/shared/results/`.
- 모델 checkpoint 는 `external/checkpoints/` 또는 `project/output/checkpoints/`.
- 추출된 raw data / checkpoint / output 덮어쓰지 않음.
- Sbatch 명령은 사용자 사전 승인 필수. 모든 .py 는 .sh 동반. Bash 명령은 절대경로.

## Scientific Rules

- EmoBrain 은 active brain decoding for emotion 의 model-development project. Emotion theory paper 아님.
- **Single project, 5 novelty framing** (2026-06-29 pivot). NV0 LLM-based brain emotion decoder (framing axis) + NV1 3-modality LLM fusion + NV2 MindCaptioning bridge + NV3 modular brain encoder + NV4 34-distribution curriculum. 자세히 `Paper/framework_EN.md`, `CONTEXT_EMOBRAIN.md`.
- 이전 Three Directions (D1 BrainVLM + D2 fMRI-LM + D3 CCN) framing 은 폐기 (2026-06-29). `archive/v5_direction_split_20260628/` 에 보존.
- **Core novelty**. Framework 자체 (multi-modal LLM fusion + modular brain encoder + 34-distribution curriculum) 와 "emotion 은 high-dimensional 이다" (34D distribution + V/A continuous output). "어떤 encoder 가 제일 좋은가" 가 spine 이 아님.
- **Red-team 완료 (2026-06-30)**. 4 panel (Architecture / Training stability / Inference paradigm / RoPE position-shift) 로 7 blocker + 12 redesign recommendation. `docs/notes/redteam_review_20260630.md`. Training start 전 Week 0 engineering sprint 로 blocker resolve.
- Background benchmark (Phase 1) 의 frozen BFM (SwiFT NewE96 + 5 변종, Brain-JEPA, NeuroSTORM) 은 ROI ridge baseline 못 넘음을 확정. EmoBrain framing 의 motivation evidence. `docs/reports/phase1_audit_20260604/`.
- Stimulus 수 = **2185 unique canonical**. fMRI session 에는 2196 presentation 이 있지만 그 중 **11 개 는 reliability check 로 두 번 제시된 중복** (EmoViS DECISIONS 2026-05-08). Unique stimulus = 2196 − 11 = **2185**. fmri_raw.npy 축 2196 은 presentation 수 (중복 포함), 우리 canonical 은 2185 unique. label CSV / split / ROI pt 모두 2185. 5 subject × 2185 stim pooled 이 primary paradigm.
- Claim 과 measured result 분리. Over-claim 금지.
- 약어 (BFM, VLM, LLM, ROI, RSA, CKA) 첫 등장 시 풀어쓰기.
- **Baseline 의무**. 모든 task 결과는 standard baseline suite (chance / ROI mean + Ridge / Phase 1 best BFM frozen reference / Video baseline) 와 함께 reporting. Baseline 없는 result 는 unreliable. 자세히 `ACTION_PLAN.md` §S11.1.
- **Noise ceiling 의무**. 모든 main claim 은 Stage 0 noise ceiling (inter-rater agreement, inter-subject brain similarity, ISC + repeated-trial + Lage-Castellanos analytical) 로 anchor. Ceiling 대비 gap_filled = (best_encoder - ridge) / (noise_ceiling - ridge) 가 primary metric.
- Reference 인용 전 파일 실체 read 로 author/title/journal/DOI verify.

## Style Rules

- 응답 언어 한국어 (기술적 고유명사 코드/논문 제목/경로 는 영어 유지 가능).
- Em dash (—) 사용 금지. 괄호/comma/문장 재구성 으로 대체.
- 학술 산문 에서 colon 회피. 자연스러운 절 로 재작성.
- No sycophancy. 사용자 반박 시 자체 evaluation 후 답변. 반사적 동의 금지. 증거 강도 에 맞는 claim 강도.
- 결과 summary 는 숫자 만 나열 하지 말고 "무엇을 의미 하는가" 단락 필수.
- 코드 제시 전 4 항목 pre-framing (what / process / expected outcome / narrative role).

## Implementation CAUTION (from `docs/notes/implementation_spec_20260702.md` §14)

Code 구현 시 반드시 지켜야 할 항목. 이 규칙 위반 은 framework claim 을 무너뜨림.

- 34D 출력 에 softmax 사용 금지. 감정 공존 (bittersweet) 이 사라짐.
- Test / val 통계 로 z-score 정규화 금지. Train 통계 만.
- 텍스트 (caption, question) 에 projector 붙이지 금지. Tokenizer 만.
- Video embedding 은 고차 layer 사용. 초기 layer 금지 (감정 관련 시각 정보 는 고차 layer 에 있음).
- Caption 을 question 안 문자열 로 합치지 금지. 별도 field.
- Frozen 과 fine-tune 은 encoder 종류 와 무관 한 독립 축. Config 로 제어.
- E4 (ViT fine-tune) 을 full fine-tune 으로 실행 금지. Default LoRA / partial.
- Student 최종 평가 는 brain + question 만 인 추론 form 으로.
- Cross-subject 결과 를 cross-stimulus 로 서술 금지. MindCaptioning 은 subject 겹치지 않지만 stimulus 는 겹침.
- E2 ridge encoder (LLM 경유) 와 B1 ridge (LLM 없음) 혼동 금지. Framework 그래프 에 B1 없음.

## Required Checks

문서 구조 변경 후.
```bash
python3 tools/check_md_completeness.py
python3 tools/build_project_status.py
```
