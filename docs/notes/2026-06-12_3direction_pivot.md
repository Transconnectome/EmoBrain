# 2026-06-12. 3-Direction Pivot + Emo-FilM Dataset Addition

## 결정

EmoBrain framing 을 **2 direction (BrainVLM + Multimodal Alignment) → 3 direction** 으로 확장.

- **Direction 1. BrainVLM** (그대로). Qwen3-VL + LoRA + emotion VQA.
- **Direction 2. fMRI-LM** (NEW). Wei 2026 paper (arXiv 2511.21760) 의 architecture (Brain-JEPA-like tokenizer + GPT-2/Qwen3 LLM + SigLIP + GRL + F2F+F2T+T2T 3-objective tuning) 차용 후 emotion specific 으로 발전. 이전의 Multimodal Alignment 가 fMRI-LM 으로 교체됨.
- **Direction 3. CCN** (NEW, 별도 axis). Brain-Video alignment + context clustering. 이전의 Multimodal Alignment 작업이 여기로 이동. 별도 workshop 발표 path.

## Dataset 추가

- 기존 Horikawa (5 subj × 2185 stim) 만 사용.
- **Emo-FilM 추가** (다운로드 예정). narratives + temporal dynamics 강조.
- D1 + D2 가 **2 × 2 grid** (2 model × 2 dataset).

## Task 재정의 (3 종류)

- A. 기존 언어 task (공통, 두 dataset). V/A binary, V/A reg, categorical.
- B. 새로운 공통 task (공통, 두 dataset). independent dataset 에도 적용되는 label 을 어떻게 만들 것인가. clustering 등.
- C. 개별 dataset task. Horikawa = visual feature 위주. Emo-FilM = narratives + dynamics.

## Repository reorg

- `/pscratch/sd/s/sjmoon/CCN_Emotion/` 전체 → `project/dir3_ccn/` 안으로 mv (2.1G, 한 번에 관리).
- 기존 `project/dir2_multimodal/code/` 의 SigLIP + GRL alignment 코드 → `project/dir3_ccn/code/alignment_pilot/` 으로 이동.
- 기존 `project/dir2_multimodal/code/legacy_phase2/` (v4 Brain+Video framework) → `project/dir3_ccn/code/legacy_phase2/` 로 이동.
- `project/dir2_fmri_lm/{code,data,output,results,docs}` 신설 (빈 디렉토리).
- `project/dir2_multimodal/` 디렉토리 삭제.

## Path migration

- 20 파일 in CCN_Emotion 의 hardcoded path `/pscratch/sd/s/sjmoon/CCN_Emotion/` → `/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/`.
- dir2_multimodal alignment 코드의 hardcoded path → `dir3_ccn/code/alignment_pilot/`.
- 모든 docs 의 `dir2_multimodal/` → `dir3_ccn/code/alignment_pilot/` (path) + Direction 2 의 의미적 reframe (Multimodal Alignment → fMRI-LM).

## 영향 받은 docs

- `README.md`, `README_KR.md`, `CONTEXT_FEEL.md`, `ACTION_PLAN.md`, `CLAUDE.md`, `docs/masterplan_v3_emobrain.md` 의 Direction 표, layout, tasks, dataset.
- Paper/framework_EN/KR.md 의 Two Axes → Three Directions (다음 commit 에).

## 진행 상태

- Direction 3 alignment pilot 의 scaffolding 은 이미 완료 (SigLIP + GRL + local smoke test PASS), 단 sbatch launch 는 사용자 결정 대기.
- Direction 1, 2 의 scaffolding 은 미진행.
