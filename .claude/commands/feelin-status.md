FEEL 프로젝트 상태를 점검하라.

## 읽을 파일

1. `/pscratch/sd/s/sjmoon/FEEL/README.md`
2. `/pscratch/sd/s/sjmoon/FEEL/ONBOARDING.md`
3. `/pscratch/sd/s/sjmoon/FEEL/CONTEXT_EMOBRAIN.md`
4. `/pscratch/sd/s/sjmoon/FEEL/CLAUDE.md`
5. `/pscratch/sd/s/sjmoon/FEEL/notes/project_decisions.md`
6. `/pscratch/sd/s/sjmoon/FEEL/notes/two_month_plan.md`
7. `/pscratch/sd/s/sjmoon/FEEL/reference/papers.md`
8. `/pscratch/sd/s/sjmoon/FEEL/reports/status/PROJECT_STATUS.md`
9. `study*/results/` 안의 최신 결과 파일

## 실행할 점검

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
```

## 출력 형식

```markdown
## Current State

## Completed

## Running or Blocked

## Next 3 Actions

## Risks

## Files Updated Recently
```
