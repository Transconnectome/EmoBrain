> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# FEEL Research Operating Workflows

This folder defines how FEEL should run as an AI-assisted research
project. These workflows are not extra narrative documents; they are operating
protocols.

## Workflow Map

| Intent | Use |
|---|---|
| Literature or dataset expansion | `literature_sota_workflow.md` |
| Turning an idea into runnable experiments | `experiment_planning_workflow.md` |
| Stress-testing a claim or strategy | `red_blue_team_review.md` |
| Weekly synthesis and project management | `weekly_update_workflow.md` |

## Natural-Language Triggers

| Trigger | Action |
|---|---|
| `[deep search]` | search external literature/code/data and update reference docs |
| `[experiment card]` | create a structured experiment card from a model idea |
| `[red team]` | generate multi-reviewer critique and blue-team response |
| `[weekly status]` | build a status report from git changes and canonical docs |
| `[verification]` | run path, completeness, and overclaim checks |

## Required Checks

Run before committing research-operations changes:

```bash
python3 scripts/check_md_completeness.py
python3 scripts/build_project_status.py
git status --short
```
