> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

> **SUPERSEDED 2026-08-19.** open-vocabulary / cross-taxonomy 전이를 headline 으로 삼던 프레임은
> 폐기되었다. 현재 논증은 `docs/paper_logic_merged.md` (대전제·RQ·가설 H1–H4). 아래는 역사 기록.

# EmoBrain Direction v6 — Approach (2026-08-17, verified)

> **CURRENT FORWARD PLAN.** Supersedes the LLM-backbone framing (Qwen3-VL-4B,
> NV0-NV4). Every load-bearing reference here was checked against the actual paper
> (repo PDF text extraction) or is flagged as search-level-only. Grounding detail:
> `docs/reference/label_query_pivot_grounding.md`.

## 1. Why (measured, not assumed)
Per-clip 34D profile Pearson, same test split:
- ROI-mean brain emotion decoding saturates ~0.31 (ridge 0.294, kernel 0.313) = R0.
- Stimulus (V-JEPA2 video + human caption) alone = 0.493; brain marginal +0.028.
- LLM teacher (Qwen3-VL-4B, 3 modalities) 0.553 vs cheap MLP fusion 0.533 (+0.02).
- LLM-as-encoder brain-only student 0.154, BELOW linear ridge 0.294.
=> LLM is not load-bearing (dropped). The useful mechanism (label queries pooling
   features) is Query2Label and needs no LLM. Winning on accuracy is NOT our path
   (brain adds +0.028; "stimulus > brain" is near-trivial — the crowd labelled
   emotion from the same video). Our contribution is GENERALIZATION.

## 2. Novelty — precisely bounded (after verification)
Two established lines bound us, both confirmed from actual papers:
- **OV-MER** (Lian et al. 2025, repo PDF verified): open-vocabulary MER already
  predicts emotions "beyond a fixed label space", generalising to "unseen or new
  labels". BUT it is STIMULUS-side (video/audio/text); "brain" appears once, fMRI
  never. So open-vocabulary emotion is NOT ours to claim as a concept.
- **Du/Fu group** (ML-BVAE, GED, EmoGrowth; repo PDFs verified): fine-grained
  emotion decoding + emotion-emotion relation learning (co-occurrence attention,
  bipartite emotion-ROI graph, RKD-RSM geometry distillation) on THIS Horikawa data.
  Relation/geometry learning is NOT ours to claim either. EmoGrowth also verified
  that naive LLaMA-3.1-8B label embeddings HURT (+SE variant worst).

**Our white space = the intersection:** open-vocabulary / cross-taxonomy emotion
**decoding FROM BRAIN activity**, plus the neuroscience of a stimulus-general neural
emotion code. Nobody sits in this intersection. Frame the AI contribution as
"open-vocabulary emotion decoding from brain", adopting OV-MER's framing/metrics.

## 3. Research questions (two lenses)
### AI / DL
- **RQ-AI-1 (headline).** Can one semantic-label-query decoder decode fine-grained
  emotion FROM BRAIN across a different label taxonomy (CK34 <-> Emo-FilM 15/50) and
  to unseen labels (open-vocabulary)? -> C-AI-1: first open-vocab emotion brain decoder.
- **RQ-AI-2 (relation + integration learning).** Jointly learn emotion<->emotion AND
  emotion<->vision/semantic relations; which learning strategy makes the integrated
  code modality- and label-invariant (so it transfers)? -> C-AI-2: the invariance recipe.
- **RQ-AI-3 (interpretability).** Read the attention as an explanation — per emotion,
  which visual cue + which caption word + which co-occurring emotions drive it.
### Neuroscience
- **RQ-NS-1 (presence).** Does a fine-grained neural emotion code generalise across
  stimulus regimes (static clips -> narrative films)? -> stimulus-general code.
- **RQ-NS-2 (categories vs dimensions).** Does the neural code transfer better as
  categories or as affective dimensions? (tests the appraisal>labels headwind.)
- Dropped: brain-beyond-stimulus +0.028 (could be noise; belongs to EmoViS).

## 4. Model (LLM-free label-query decoder)
`project/code/decoder/label_query_decoder.py`, ~3.8M params.
- N emotion queries, INIT from semantic emotion-word embeddings (learnable — NOT
  frozen; EmoGrowth showed frozen naive LLM labels hurt).
- Inputs as TOKEN SEQUENCES so queries can attend to specific cues: brain = per-ROI
  tokens; video = V-JEPA2 patch/frame tokens; caption = text-encoder token sequence
  (SBERT/CLIP-text). No LLM in the loop.
- Transformer decoder: self-attention (emotion<->emotion) + cross-attention
  (queries -> brain+video+caption). Shared scalar head -> per-emotion log1p_z.
- Variable N -> swap the query set for a new taxonomy (open-vocabulary).

## 5. Learning strategy — geometry-first (WHAT the model must learn, not a loss name)
The strategy is a choice of STRUCTURE, not "use contrastive". We choose GEOMETRY over
co-occurrence because a co-occurrence graph is dataset-specific (does not transfer),
while a relational geometry anchored on semantic embeddings places new emotions by
their meaning and transfers.
- **Emotion<->emotion:** teach the relational GEOMETRY of the 34 queries (distances/
  angles / RSM), anchored on semantic word embeddings. Mechanisms: RKD-style
  distance/angle (Park 2019) or RSM alignment (as EmoGrowth does to affective dims);
  query self-attention; label masking (C-Tran) for co-occurrence as support.
- **Emotion<->vision/semantic:** per-emotion grounding via token-level cross-attention
  (Query2Label) + cross-modal alignment so brain-read ~= stimulus-read
  (contrastive/CLIP-style OR RSA). Muttenthaler (Nature 2025, verified) is the direct
  precedent for teacher->student transfer of representational STRUCTURE.
- **Force brain to contribute:** modality dropout (drop stimulus so brain must carry).
- **Transfer to brain-only:** cross-modal consistency (= self-distillation) and/or
  LUPI teacher->student.
Open decision (the real strategy detail): anchor the geometry to (a) a fixed target
(Cowen-Keltner semantic space), (b) a brain-derived geometry, or (c) learn it. To be
settled by ablation.

## 6. Evaluation plan
1. **Same-dataset sanity (gate):** the decoder must beat ridge 0.294 within CK34. If
   not, the encoder/decoder is the bottleneck — fix before any transfer claim.
2. **Cross-taxonomy / open-vocab transfer (headline):** CK34 -> Emo-FilM 15/50, unseen
   labels. Adopt OV-MER's open-vocab metrics. Needs Emo-FilM fMRI download (blocked).
3. **Categories vs dimensions (RQ-NS-2)** + mandatory dimension-transfer control
   (vs appraisal>labels headwind, arXiv:2604.27938).
4. **Interpretability:** per-emotion attention over vision/caption + emotion co-occurrence.
5. **Controls:** mean-profile floor, brain-shuffle (leakage), semantic-init vs random
   vs frozen-LLM-label (the EmoGrowth test), geometry vs co-occurrence vs none.

## 7. Positioning / related work (all verified against actual papers)
- OV-MER (Lian 2025): open-vocab emotion, stimulus-side -> we do it from brain.
- Du/Fu ML-BVAE/GED/EmoGrowth: relation/geometry decoding on this data -> we develop
  (semantic anchor for transfer + multimodal + open-vocab), not invent.
- Muttenthaler et al. Nature 2025 (the file mislabeled "Doerig2025"): geometry
  teacher->student transfer -> direct method precedent.
- Query2Label / C-Tran / DETR (decoder), CLIP / SupCon / RKD (learning), LUPI
  (distillation): technique grounding (search-level; verify at final citation).

## 8. EmoBrain / EmoViS (two separate papers, one shared arc)
Arc: emotion is largely visual-semantic-constituted. EmoViS = the NEURAL
characterization (RSA, cortical location) — a REAL committed analysis, its own paper.
EmoBrain = the model + open-vocab brain transfer + categories-vs-dimensions. EmoBrain
never claims cortical location. EmoBrain is the priority project.

## 9. Verification status (honest)
- Verified from actual paper text (repo PDF): Du1 ML-BVAE, Du2/Du3 GED, Du_4 EmoGrowth,
  Muttenthaler (Nature 2025), OV-MER (Lian 2025).
- Search-level only (existence/authors/venue, content NOT read): RKD, ML-GCN, CLIP,
  SupCon, Query2Label, C-Tran, DETR, LUPI, Peelen 2010, Saarimaki 2016, Horikawa 2020.
  ML-GCN corroborated as a baseline inside ML-BVAE's PDF. Verify all externals at
  final citation (bgpt/DOI or PDF).
- Repo issues found: `Doerig2025_*.pdf` mislabeled (= Muttenthaler); BioReason
  (DNA-LLM) misfiled under BrainVLM_emotion; duplicates 2505.23579, 2604.03619.

## 10. Approach roadmap (order of attack)
1. Finalize decoder: token-level inputs + semantic-init learnable queries + loss stack.
2. Same-dataset sanity gate (beat ridge 0.294 within CK34). Blocks everything downstream.
3. Learning-strategy ablations: geometry vs co-occurrence vs none; semantic-init vs
   random vs frozen-LLM; modality dropout; contrastive/RSA on/off.
4. Cross-taxonomy / open-vocab transfer (after Emo-FilM download): CK34 -> Emo-FilM,
   categories vs dimensions, OV-MER metrics.
5. Interpretability + neuroscience writeup (RQ-NS-1/2).
6. EmoViS proceeds as a parallel, separate paper.

## 11. Risks
- Cross-taxonomy label transfer may fail (labels transfer worse than dimensions) ->
  RQ-NS-2 absorbs it; semantic geometry is the countermeasure.
- Semantic query init may hurt (EmoGrowth) -> learnable + masking, ablated.
- Same-dataset numbers will not be SOTA; the story is generalization, not accuracy.
- Novelty is narrow (brain x open-vocab x neuroscience intersection) and contingent
  on the transfer result.
