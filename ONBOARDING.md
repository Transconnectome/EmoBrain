# FEELIN Onboarding

새 협업자 또는 AI agent 가 처음 읽을 파일. FEELIN 의 현재 framing (Masterplan v2.0, 2026-05-19) 과 읽을 순서를 정리.

## 프로젝트 정체성

FEELIN = **Transferable Emotion Brain Foundation Model**.

**Big Question (Masterplan v4, 2026-06-02)**:
Naturalistic fMRI 로부터 학습한 multi-dimensional emotion brain representation 이, 단일 dataset 과 label taxonomy 에 종속되지 않고 새로운 subject, 자극, emotion 어휘로 transfer 되는 emotion brain foundation model 이 될 수 있는가?

<sub>운영 정의 (operationalization, FEELIN testbed): Horikawa naturalistic fMRI 로 학습한 multi-dimensional emotion brain representation 이, metadata 가 풍부하지 않은 independent dataset / 새 subject / 다른 emotion taxonomy 로 transfer 되는 emotion brain foundation model 이 될 수 있는가? 그리고 어떤 supervision (scalar V/A vs Cowen 34-category vs 14-dimension vs open-vocabulary description) 과 어떤 brain encoder 가 가장 transferable 한 표상을 만드는가? supervision 과 encoder 비교는 SQ2 와 encoder-swap 축에서 다룬다.</sub>

FEELIN 은 emotion theory paper 가 아니라 **model-development 프로젝트**. contribution 은 "brain 이 video 를 이기나" 가 아니라 representation 의 transfer / generalization / data-efficiency / universality 다. v3 의 질문 ("fMRI + video fusion 이 video baseline 을 넘는가") 은 Phase 1 + Phase 2 joint 가 "넘지 못한다 (crowd V/A label = stimulus 속성이라 trivial)" 로 답했고, 그 측정 결과는 보존된다 (`reports/phase1_wrapup/`, `docs/masterplan_v2.md` 7.0). v4 는 질문을 transfer 로 옮긴다.

## 읽을 순서

1. **README.md** — 프로젝트 한눈에 (Big Q + 3-tier + phase status)
2. **README_KR.md** — 한국어 가이드
3. **docs/masterplan_v2.md** — 전체 phase plan / sub-question / go-no-go 기준 / agent review schedule
4. **reports/phase1_foundation.md** — 현재 진행 중인 Phase 1 progress
5. **Paper/framework_KR.md** (또는 EN) — canonical narrative
6. **Paper/methodology.md** — 실험 방법
7. **notes/benchmark_design.md** — Dataset × BFM × Task 매트릭스 디테일
8. **notes/project_decisions.md** — 결정 로그
9. **reference/datasets.md, task.md, papers.md, code_resources.md, training_strategy.md** — 각 axis 별 reference
10. **ACTION_PLAN.md** — v1 legacy 실행 계획 (week-level detail, masterplan v2 와 함께 참조)

## 새 파일 추가 전 체크

1. 기존 canonical 문서 (Paper/, notes/, reference/, docs/masterplan_v2.md) 에 들어갈 내용 아닌지 확인
2. `templates/` 의 카드 사용 (paper, dataset, model, experiment, review, decision)
3. 검증:
   ```bash
   python3 scripts/check_md_completeness.py
   ```
4. 상태 갱신:
   ```bash
   python3 scripts/build_project_status.py
   ```

## 주요 workflow

| 의도 | Workflow |
|---|---|
| 새 논문 / 데이터셋 찾기 | `workflows/literature_sota_workflow.md` |
| 아이디어를 실험으로 | `workflows/experiment_planning_workflow.md` |
| 전략/모델 주장 stress-test | `workflows/red_blue_team_review.md` |
| 진척도 정리 | `workflows/weekly_update_workflow.md` |

## 현재 진행 상황 (2026-06-02 기준)

- **Phase 1** (W1-6) 완료: frozen probe benchmark + padding ablation + 6 SwiFT variants. `reports/phase1_wrapup/main.pdf` (15p) + supplementary (11p). 측정값은 `docs/masterplan_v2.md` 7.0 에 보존.
- **Phase 2** (W7-12) 진행 중: 4 fusion arch joint inference 완료 (video saturate, 질문 A 종료). brain-only 4 method 학습 중.
- **현재 framing (v4)**: 질문 축 = transfer. target = Cat34 / Dim14 / OV-text-embedding (V/A 는 reference). cross-dataset zero-shot / few-shot 평가, OV-MER / AffectGPT 는 label-poor target dataset 의 harmonization 도구. 변경 경위는 `notes/project_decisions.md` 2026-06-02.
- **대기 (next)**: AffectGPT Horikawa sanity check, brain → emotion-text projector prototype, Horikawa per-subject rating 존재 확인.
