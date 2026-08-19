# Red-Team / Blue-Team Review Workflow

Purpose: stress-test EmoBrain claims, model plans, and experiment designs
before they become project narrative.

## Reviewer Personas

| Persona | Attacks |
|---|---|
| fMRI methods reviewer | preprocessing, HRF, leakage, subject split, metric validity |
| affective neuroscience reviewer | target validity, emotion-label ambiguity, overinterpretation |
| ML foundation-model reviewer | scale, pretraining evidence, baselines, ablation quality |
| data/compute feasibility reviewer | access, runtime, memory, file format, annotation timing |
| skeptical project reviewer | two-month feasibility and strategic focus |

## Steps

1. Select target: framework claim, dataset plan, model architecture, or
   experiment card.
2. Red team:
   - identify the strongest objection from each persona,
   - mark severity: low / medium / high / blocking.
3. Blue team:
   - rewrite the claim,
   - add missing experiment or citation,
   - downgrade overclaim when evidence is not available.
4. Record outcome using `docs/archive/templates/review_card.md`.
5. Update canonical docs only after the review changes the project direction.

## Output Format

```markdown
## Target

## Red-Team Findings

## Blue-Team Response

## Required Edits

## Decision
```

## Pass Criteria

- No unsupported "emotion foundation model" claim.
- TRIBE v2 is not described as an fMRI encoder replacing SwiFT.
- Dataset limitations are explicit.
- Decision rule remains tied to model development.
