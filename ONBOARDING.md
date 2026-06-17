# EmoBrain Onboarding

새 협업자 또는 AI agent 가 처음 읽을 파일. EmoBrain 의 현재 framing (Three Directions, 2026-06-08~06-12 pivot) 과 읽을 순서를 정리.

## 프로젝트 정체성

**EmoBrain** = Active brain decoding for emotion. **Three Directions** framing (since 2026-06-08).

| Direction | Method | 위치 |
|-----------|---------|------|
| **D1. BrainVLM** | Qwen3-VL + ROI patchify + LoRA + multi-task heads | `project/dir1_brainvlm/` |
| **D2. fMRI-LM** | Wei 2026 fMRI-LM 3-stage 그대로 사용 (submodule) | `project/dir2_fmri_lm/` |
| **D3. CCN** | Brain-Video alignment (SigLIP + GRL) + context clustering (workshop path) | `project/dir3_ccn/` |

D1 + D2 가 main paper 의 2 axis (Horikawa + Emo-FilM 의 2 × 2 grid). D3 는 CCN workshop 발표 path (결과 강하면 paper 까지).

이전 framing.
- v3 (2026-05-27, individual difference). `archive/v4_20260602/`.
- v4 (2026-06-02, universal emotion code, FEEL). `archive/v4_20260602/`.

## 환경 + clone

```bash
git clone --recursive git@github.com:Transconnectome/EmoBrain.git
# 이미 clone 했다면
cd EmoBrain && git submodule update --init --recursive
```

| 항목 | 위치 |
|------|------|
| Python (general) | `/pscratch/sd/s/sjmoon/tribev2/.venv` |
| Python (LLM) | `/pscratch/sd/s/sjmoon/brainvlm_qwen_env` |
| Compute | NERSC m4641 (cpu / gpu queue, A100 80GB) |
| Submodule. BrainVLM (D1 reference) | `external/repos/BrainVLM` |
| Submodule. fMRI-LM (D2 본체) | `external/repos/fMRI-LM` |

## 읽을 순서

1. **README.md / README_KR.md** — 프로젝트 한눈에 (3 directions + 2 × 2 grid + Phase 1 background).
2. **CONTEXT_EMOBRAIN.md** — Compact single-source-of-truth. agent 가 빠르게 reference.
3. **project/README.md** — 4 폴더 (D1/D2/D3/shared) 의 input shape + atlas + env + 학습 entry + 데이터 schema + 협업자 onboarding 4 step.
4. **docs/masterplan_v3_emobrain.md** — Forward plan (Direction 별 deliverable + gate, hackathon, paper plan).
5. **ACTION_PLAN.md** — Ground-level weekly action (D1/D2/D3 의 Action 1.x ~ 3.x).
6. **CLAUDE.md** — Operating rules + scientific rules (claim/result 분리, baseline 의무 등).
7. **project/dir{1,2}/docs/getting_started.md** — D1, D2 의 학습 entry 와 새 dataset 추가 4 step.
8. **project/dir{1,2}/docs/design.md** — Direction 별 architecture / loss / hypothesis / gate 의 세부 설계.
9. **docs/reports/phase1_audit_20260604/** — Phase 1 background benchmark (frozen BFM 한계 audit + PDF report).
10. **Paper/framework_EN.md, framework_KR.md** — Canonical narrative draft.
11. **docs/notes/project_decisions.md** — 결정 로그 (chronological).

## 새 파일 추가 전 체크

1. Root .md 는 7 개 (README, README_KR, CONTEXT_EMOBRAIN, ONBOARDING, CLAUDE, CODEX, ACTION_PLAN) 만. 새로 추가 금지.
2. Forward plan / phase report 는 `docs/` 와 `docs/reports/` 에만.
3. Narrative 는 `Paper/framework_{EN,KR}.md`.
4. Methodology 는 `Paper/methodology.md`.
5. Decision log 는 `docs/notes/project_decisions.md`.
6. 실험 코드는 per-direction (`project/dir{1,2,3}/code/`) 또는 공유 (`project/shared/code/`).
7. 검증.
   ```bash
   python3 tools/check_md_completeness.py
   python3 tools/build_project_status.py
   ```

## 주요 workflow

| 의도 | Workflow |
|---|---|
| 새 논문 / 데이터셋 찾기 | `docs/workflows/literature_sota_workflow.md` |
| 아이디어를 실험으로 | `docs/workflows/experiment_planning_workflow.md` |
| 전략 / 모델 주장 stress-test | `docs/workflows/red_blue_team_review.md` |
| 진척도 정리 | `docs/workflows/weekly_update_workflow.md` |

## 현재 진행 상황 (2026-06-17 기준)

- **Background (Phase 1)** 완료. Frozen BFM (Brain-JEPA, NeuroSTORM, SwiFT 6 변종) 의 ROI baseline 못 넘음을 audit 으로 확정. `docs/reports/phase1_audit_20260604/`.
- **D1 BrainVLM** scaffolding 완료 (`project/dir1_brainvlm/code/`, `scripts/`). smoke test PASS. backbone 통합 + pilot 학습 진입 대기.
- **D2 fMRI-LM** upstream submodule + NERSC wrapper 완료. 새 dataset adapter template + emotion descriptor 생성기 + emotion-specific metric 추가. Stage 1/2/3 launch 사전 승인 대기.
- **D3 CCN** alignment_pilot scaffolding (SigLIP + GRL) 완료 + smoke PASS. Pilot launch 사전 승인 대기.
- **Datasets**. Horikawa (5 subj × 2185 stim) 사용 중. **Emo-FilM 다운로드 예정**.

## Operating rules (요약)

- 모든 .py 는 .sh 동반.
- Bash 명령은 절대경로. cd + relative 금지.
- sbatch 는 사용자 사전 승인 필수.
- 결과 reporting 은 standard baseline suite (chance / ROI Ridge / BFM frozen reference / Video baseline) 와 함께.

자세한 내용은 `CLAUDE.md`.
