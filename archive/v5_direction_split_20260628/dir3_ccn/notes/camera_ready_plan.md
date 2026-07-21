# Camera-Ready Plan (CCN 2026)

**Deadline**: 2026-06-11 11:59 PM AoE. No extensions.
**Constraint**: 2-page limit including title-author block. "Not intended to be a significant revision; major changes require withdrawal and resubmission to CCN 2027."

## Required mechanical work (reviewer-independent)

- [ ] Download LaTeX v2026.1+ template from official CCN repository
- [ ] Port current abstract content into new template
- [ ] Deanonymize: author block + institutional affiliation (must match OpenReview metadata exactly)
- [ ] Add Acknowledgments / Disclosure section (before References, does not count toward 2 pages):
  - [ ] LLM use disclosure per CCN policy (Claude Code for analysis & critique)
  - [ ] Funding / compute acknowledgement (NERSC m4641)
- [ ] Cite any overlapping in-press work (check what's in press by 6/11)

## Allowed text-level revisions (Tier 0, safe)

- [ ] Abstract framing softening: "self-supervised learning ... spontaneously produces a low-dimensional, categorically organized affective subspace" → "the brain-readable subset of V-JEPA2 features carries more categorical than dimensional emotion information than the full V-JEPA2 space, suggesting that the visual statistics captured by self-supervised video pretraining contain a category-organized affective signal accessible to the brain"
- [ ] Discussion: add 1 sentence about baseline-control limitation ("Further work is required to establish that this categorical organization is specific to self-supervised video pretraining rather than to generic visual category statistics")
- [ ] Methods: justify V-A choice as Russell circumplex canonical axes; 14-dim full comparison left to supplementary

## Statistical sentence additions (Tier 1, allowed if from existing data)

- [ ] Paired bootstrap CI + p-value for ratio 1.44 vs 1.26
- [ ] Per-subject ratio values (table or 1 sentence with 5 values + Wilcoxon)
- [ ] Partial R² specific numbers replacing "attenuated but preserved"
- [ ] PC1-only ratio vs PC1+2+3 ratio (1 sentence on PC1 dominance)

## Reviewer-dependent decisions (wait until ~5/26 reviews)

- [ ] Map reviewer concerns to Tier 0/1 fixes above
- [ ] Decide what figure tweaks are warranted (significance markers, error bars)
- [ ] Decide if Discussion needs additional reframing based on what reviewers flag

## What MUST be excluded from camera-ready

- New baseline models (untrained ViT, ImageNet ViT) — qualifies as "significant revision"
- New analyses (PC1-3 layer-wise, region-wise) — same
- New control experiments beyond what current data supports

These are for the August poster and full follow-up paper, not camera-ready.

## Risk register

- Author list change is not allowed after submission (per email). Confirm OpenReview metadata matches the deanonymized version exactly.
- Major revision is grounds for withdrawal. Any new analysis result added must be presented as already-computed-but-not-shown, not as new work.
- LLM disclosure missing is a policy violation. Cannot be skipped.
