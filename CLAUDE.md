# NetFeeliX Project Instructions

## Folder Structure

```text
NetFeeliX/
├── ONBOARDING.md    # first-read guide for humans and AI agents
├── CONTEXT_NETFEELIX.md # compact SSOT for project framing
├── CLAUDE.md
├── CODEX.md
├── Paper/          # canonical framework + methodology only
├── reference/      # 문헌, 데이터셋, 코드 리소스, 검색 로그
├── notes/          # 결정사항, 회의 메모, 실행 계획
├── templates/      # paper/dataset/model/experiment/review/decision templates
├── workflows/      # research operating workflows
├── scripts/        # project-operation automation
├── reports/        # generated status, review, and weekly reports
├── code/           # 공통 코드 설명 및 shared utilities 계획
└── setup/
    ├── code/       # .py, .sh, .md 설명 파일
    ├── data/       # 중간 산출물
    ├── logs/       # SLURM/stdout/stderr/logging
    └── results/    # 결과, figure, table
```

## Hard Rules

- 초기 실행 스크립트는 `setup/code/`에 둔다. 명확한 공통 유틸리티는 `code/`에 둔다.
- Project-operation scripts live in `scripts/`. Initial runnable experiment scripts live in `setup/code/`.
- `data/`는 중간 처리물, `results/`는 분석 결과물, `logs/`는 실행 로그다.
- 전체 프로젝트 프레임, 내러티브, proposal-level 내용은 반드시 `Paper/framework_EN.md`와 `Paper/framework_KR.md`에 기록한다. 새 brief/proposal/narrative 파일을 만들지 않는다.
- 방법론 세부사항은 `Paper/methodology.md`에 기록한다.
- 문헌 주장은 `reference/papers.md` 또는 `reference/systematic_reference_map.md`에 출처와 함께 남긴다.
- 실험 결정은 `notes/project_decisions.md`에 날짜와 함께 기록한다.
- 결과 수치가 없는 주장은 hypothesis 또는 planned analysis로 표시한다.
- `.md` 파일을 무작정 늘리지 않는다. 기존 canonical 문서에 병합 가능한 내용은 병합한다.
- Use `templates/` for new structured research objects and `workflows/` for process. Do not create one-off Markdown files outside these conventions.
- Run `python3 scripts/check_md_completeness.py` after structural documentation edits.

## Operating System

- `ONBOARDING.md` defines the first-read path.
- `CONTEXT_NETFEELIX.md` is the compact project SSOT.
- `workflows/literature_sota_workflow.md` governs literature, dataset, and code expansion.
- `workflows/experiment_planning_workflow.md` turns ideas into experiment cards.
- `workflows/red_blue_team_review.md` stress-tests claims and model plans.
- `workflows/weekly_update_workflow.md` produces durable progress summaries.
- `scripts/build_project_status.py` writes `reports/status/PROJECT_STATUS.md`.

## Confirmed Framing

NetFeeliX is a **model-development project**, not a theory paper about emotion. Emotion theory should be kept minimal and used only to justify target design and naturalistic data. The core work is screening-benchmark-driven model selection and development for emotion-aware brain representation learning.

Canonical one-line framing:

> NetFeeliX treats emotion representation as a model-development problem over brain dynamics, stimulus dynamics, and affective annotations, using initial benchmarks to decide which architecture and training objectives are worth developing.

The central comparison is:

1. **Generic brain representation learning**
   - Example: SwiFT, BrainLM, Brain-JEPA, NeuroSTORM.
   - Question: does generic fMRI pretraining transfer to affective downstream tasks?

2. **Naturalistic movie fMRI pretraining**
   - Example: HCP 7T movie-watching fMRI.
   - Question: does pretraining on stimulus-driven fMRI improve emotion transfer?

3. **Stimulus-to-brain encoding and alignment**
   - Example: TRIBE and TRIBE v2.
   - Question: do multimodal stimulus encoders provide emotion-relevant context that brain-only models miss?

4. **Brain-tuned affective LLM/VLM extension**
   - Example: affective LLM/VLM + brain-alignment adapter.
   - Question: can brain responses improve or regularize external affective foundation model representations?

Important priority:

- Use SwiFT as the default brain backbone unless there is a documented reason not to.
- Start with existing models and datasets for initial benchmark experiments.
- Use benchmark results to choose model-development direction.
- Do not over-invest in abstract emotion theory or claim a final foundation model before evidence.
- When refining NetFeeliX, keep the narrative as benchmark-to-model-development: benchmark results decide whether to prioritize SwiFT adapters, naturalistic movie/story pretraining, TRIBE-SwiFT alignment, or brain-tuned affective LLM/VLM.
- Avoid informal exploratory-benchmark wording in project prose. Use "initial benchmark", "screening benchmark", "feasibility benchmark", or "Stage 0/1".

## Important Model Facts

- **TRIBE is a brain encoding model**, not an fMRI encoder in the same sense as SwiFT or BrainLM. It predicts fMRI responses from video, audio, and text stimulus features.
- This does not make TRIBE incomparable to SwiFT. It means comparison requires a shared interface or model surgery: attach emotion heads, add fMRI encoders, add stimulus-brain alignment losses, or train bidirectional encoding/decoding variants.
- **TRIBE v2** is a newer multimodal brain encoding foundation model direction, using video/audio/language features and a transformer to predict high-resolution brain responses.
- **TRIBE v2 is not a replacement for SwiFT.** It is a multimodal stimulus-to-brain component that can provide stimulus features, predicted brain responses, and teacher/alignment signals.
- **SwiFT** is a 4D fMRI Swin Transformer for direct spatiotemporal fMRI modeling and the default NetFeeliX brain backbone.
- **SwiFUN** predicts task activation maps from resting-state fMRI using a Swin fMRI UNet Transformer structure.
- **Brain-JEPA** uses a joint-embedding predictive architecture for brain dynamics, with spatiotemporal masking and functional positional ideas.
- **NeuroSTORM** is a large-scale raw 4D fMRI foundation model with efficient spatiotemporal modeling and lightweight adaptation.

## Core Datasets

- **HCP Young Adult 7T movie watching**
  - 184 subjects in the release.
  - Four movie-watching runs of roughly 15 minutes each.
  - TR = 1 s, 1.6 mm isotropic 7T fMRI.
  - Role: first naturalistic pretraining candidate, not the only candidate.

- **CNeuroMod / Algonauts, StudyForrest, Narratives, 101 Dalmatians**
  - Role: hypothesis-specific naturalistic sources for multimodal alignment,
    long-film continuity, language/story context, and modality controls.

- **Horikawa / Cowen emotional video fMRI**
  - 2,185 emotion-evoking video clips.
  - High-dimensional emotion category annotations.
  - Role: core downstream benchmark.

- **Koide-Majima / Nishimoto emotional movie fMRI**
  - About 3 hours of emotion-inducing audiovisual movies.
  - 80 emotion annotations.
  - Role: high-dimensional emotion representation benchmark if data access allows.

- **Emo-FilM**
  - 30 participants, 14 short films, over 2.5 hours, 50 emotion/appraisal/component annotations.
  - Role: modern multimodal affective neuroscience downstream dataset.

## Primary Experimental Tracks

### Track A: Existing BFM Transfer

Goal: evaluate whether pretrained BFMs already contain emotion-useful representation.

Order:
1. Frozen representation + linear/ridge probe.
2. Adapter or LoRA fine-tuning where supported.
3. Full fine-tuning only after small baselines are stable.

Models:
- SwiFT, first by default
- BrainLM
- Brain-JEPA
- NeuroSTORM if code/weights are available
- Omni-fMRI or Brain-DiT only if availability and setup are realistic

### Track B: Naturalistic Movie/Story Pretraining

Goal: test whether stimulus-locked fMRI dynamics learned from movie/story data
improve transfer to emotion targets. HCP is the first candidate because of
scale and standardization; use CNeuroMod/Algonauts, StudyForrest, Narratives, or
modality-control movie datasets only when they answer a concrete model question.

Candidate objectives:
- Masked fMRI modeling.
- Temporal contrastive learning.
- JEPA-style latent prediction.
- Subject-invariant contrastive learning.
- Future brain state prediction.
- Optional stimulus-conditioned prediction with visual/audio/text features.

Start small with parcel-level time series before expensive 4D volume training.

### Track C: Stimulus-Brain-Emotion Alignment

Goal: test whether emotion representation improves when brain dynamics are aligned with stimulus features.

Candidate stimulus encoders:
- Video: V-JEPA2, VideoMAE, CLIP visual features.
- Audio: Wav2Vec-BERT, Whisper, audio spectrogram models.
- Text: captions, subtitles, LLaMA or sentence-transformer embeddings.

Candidate losses:
- Brain response prediction.
- Emotion prediction.
- Stimulus-brain contrastive loss.
- Emotion prototype alignment.
- HRF-aware temporal alignment loss.

### Track D: Brain-Tuned Affective LLM/VLM

Goal: test whether brain responses can regularize external affective foundation-model representations.

Use only lightweight methods at first:

1. Freeze affective LLM/VLM embeddings.
2. Train small adapters from stimulus embeddings to fMRI latents or emotion targets.
3. Add brain-geometry alignment or contrastive loss.
4. Distill shared stimulus-brain latents into an affective embedding usable without fMRI at inference.

Do not full fine-tune an LLM/VLM on small fMRI datasets. Activate this track only if screening benchmarks show strong stimulus-side features or measurable brain-stimulus alignment.

## Primary Metrics

- Arousal/valence: Pearson r, Spearman r, MSE, subject-wise bootstrap CI.
- Discrete emotions: macro F1, AUROC, balanced accuracy, top-k accuracy if multi-label.
- High-dimensional emotion embeddings: CKA/RSA correlation, retrieval accuracy, explained variance.
- Brain response prediction: voxel/parcel-wise correlation, noise-ceiling-normalized score where possible.
- Transfer: within-dataset, cross-dataset, leave-subject-out, leave-movie-out.

## Writing Rules

- Keep project claims separated from experimental results.
- Always keep the main framework in `Paper/framework_EN.md` and `Paper/framework_KR.md`.
- Keep emotion theory concise. The project narrative should emphasize model development, screening benchmarks, architecture comparison, and training objectives.
- Keep the four model-development tracks explicit: existing BFM transfer, naturalistic movie/story pretraining, stimulus-brain-emotion alignment, and brain-tuned affective LLM/VLM.
- Use "encoding model" carefully for TRIBE-style stimulus-to-brain models.
- Use "fMRI encoder" or "brain foundation model" for fMRI-to-representation models.
- Do not claim NetFeeliX is a foundation model until pretraining and transfer are demonstrated.
- Prefer "emotion-specific brain representation model" or "emotion-aware fMRI foundation-model strategy" until there is pretraining/transfer evidence.

## TRIBE-SwiFT Comparison Rule

Do not write that TRIBE and SwiFT "cannot be compared." Write that their original input-output tasks differ, so NetFeeliX should compare modified variants:

- SwiFT-style fMRI encoder plus emotion head.
- TRIBE-style stimulus fusion plus emotion head.
- fMRI encoder aligned to TRIBE-style stimulus latent.
- TRIBE-style stimulus encoder plus fMRI response decoder plus emotion head.
- Bidirectional model with shared latent, fMRI prediction, emotion prediction, and contrastive/JEPA-style alignment.
