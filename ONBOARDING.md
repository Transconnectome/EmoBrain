# FEEL Onboarding

새 협업자 또는 AI agent 가 처음 읽을 파일. FEEL 의 현재 framing (Masterplan v2.0, 2026-05-19) 과 읽을 순서를 정리.

## 프로젝트 정체성

FEEL = **Foundation Model for Emotion Embedding Learning**.

**Big Question (Masterplan v2.0)**:
Naturalistic emotional experience 의 brain representation 을 context-aware foundation model 로 어떻게 잘 잡아낼 수 있는가. 단일 stimulus snapshot, multimodal stimulus 표상, 혹은 language-grounded VLM 통합 중 어느 축이 emotion 을 결정하는가?

FEEL 은 emotion theory paper 도, 단순 benchmark paper 도 아니다. **세 가지 representation tier (statistical floor / brain foundation model ceiling / multimodal-VLM upper bound) 를 동일 protocol 로 비교하여 emotion 표상의 organizing principle 을 찾는 model-development 프로젝트**.

## 읽을 순서

1. **README.md**. 프로젝트 한눈에 (Big Q + 3-tier + phase status)
2. **README_KR.md**. 한국어 가이드
3. **docs/masterplan_v2.md**. 전체 phase plan / sub-question / go-no-go 기준 / agent review schedule
4. **reports/phase1_foundation.md**. 현재 진행 중인 Phase 1 progress
5. **Paper/framework_KR.md** (또는 EN). canonical narrative
6. **Paper/methodology.md**. 실험 방법
7. **notes/benchmark_design.md**. Dataset × BFM × Task 매트릭스 디테일
8. **notes/project_decisions.md**. 결정 로그
9. **reference/datasets.md, task.md, papers.md, code_resources.md, training_strategy.md**. 각 axis 별 reference
10. **ACTION_PLAN.md**. v1 legacy 실행 계획 (week-level detail, masterplan v2 와 함께 참조)

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

## 현재 진행 상황 (2026-05-19 기준)

- **Phase 1** (W1-6) 진행 중: floor + cross-BFM consistency + BrainVLM zero-shot transfer 병행
- **완료**: SwiFT NewE96 padding ablation, 3-BFM probe (NewE96 + Brain-JEPA + NeuroSTORM, spatial_only padding)
- **진행 중**: proper mean padding 으로 30 cell 재추출
- **대기**: 통계 floor (Schaefer ROI), BrainVLM env setup, SwiFT 다른 변종 추출
