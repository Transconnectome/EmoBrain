> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# Label-Query Pivot — Grounding and Positioning (2026-08)

Reference basis for the pivot away from an LLM backbone toward a label-query
(Query2Label-style) emotion decoder with semantic label queries, plus offline
distillation and cross-dataset transfer. Citations verified by web/venue lookup
(authors, venue, year) per the project reference rule.

## Why the pivot (our own numbers)
- ROI-mean brain emotion decoding saturates ~0.31 (ridge 0.294, kernel 0.313) = R0.
- Stimulus (V-JEPA2 video + human caption) decodes 0.493 alone; brain marginal +0.028.
- LLM teacher (Qwen3-VL-4B, 3 modalities) = 0.553 vs cheap MLP fusion 0.533 (+0.02 only).
- LLM-as-encoder student (brain-only) = 0.154, BELOW linear ridge 0.294.
=> The LLM is not load-bearing. The useful mechanism (label queries pooling
   features) is Query2Label and needs no LLM.

## Pillar A — label-query decoder (ML mechanism)
- DETR — Carion, Massa, Synnaeve, Usunier, Kirillov, Zagoruyko. End-to-End Object
  Detection with Transformers. ECCV 2020, pp. 213-229. arXiv:2005.12872. Learned
  queries + transformer decoder + set prediction. Origin of query-based readout.
- Query2Label — Shilong Liu, Lei Zhang, Xiao Yang, Hang Su, Jun Zhu. A Simple
  Transformer Way to Multi-Label Classification. arXiv:2107.10834 (2021). Label
  embeddings as queries; decoder cross-attention pools per-label features -> binary
  heads. 91.3 mAP MS-COCO. THIS IS OUR DECODER MECHANISM.
- C-Tran — Jack Lanchantin, Tianlu Wang, Vicente Ordonez, Yanjun Qi. General
  Multi-Label Image Classification with Transformers. CVPR 2021, pp. 16478-16488.
  DOI 10.1109/CVPR46437.2021.01621. Label mask training with ternary state
  (positive / negative / UNKNOWN). Grounds variable-label-set and held-out /
  zero-shot label prediction.

## Pillar B — distillation as privileged information
- Lopez-Paz, Bottou, Scholkopf, Vapnik. Unifying distillation and privileged
  information. ICLR 2016. arXiv:1511.03643. Teacher sees privileged modalities
  (video + caption), student is brain-only. Correct theoretical frame (LUPI /
  generalized distillation) for our teacher->student. NOTE: this predicts the
  transferred quantity is the privileged modalities, not "the LLM"; any teacher
  ingesting video+caption yields the same soft targets.

## Pillar C — neuroscience: stimulus-general emotion code (our novelty lane)
- Peelen, Atkinson, Vuilleumier. Supramodal representations of perceived emotions
  in the human brain. J Neurosci 2010, 30(30):10127. MPFC & STS encode emotion at
  a modality-independent, abstract level (basic emotions).
- Skerry & Saxe. A Common Neural Code for Perceived and Inferred Emotion
  (J Neurosci 2014); Neural Representations of Emotion Are Organized around
  Abstract Event Features (Curr Biol 2015). Abstract, stimulus-general emotion code.
- Cross-modal decoding of emotional expressions in fMRI (cross-session /
  cross-sample replication). Imaging Neuroscience 2024, DOI 10.1162/imag_a_00289.
- Cross-modality arousal/valence decoding (movies + text scenarios), 2026.
  => Precedent exists for cross-context emotion generalization, but ONLY at low
     dimension (valence/arousal or ~5-6 basic emotions). Fine-grained (34-category),
     cross-TAXONOMY transfer is open.

## Positioning — what is preempted vs our white space
PREEMPTED (Du/Fu/He group, CAS, SAME Horikawa data; see du_fu_group_review_0707.md):
- ML-BVAE (TNNLS 2022): label co-occurrence masked self-attention.
- GED (TMI 2023): emotion x ROI bipartite graph + GNN.
- EmoGrowth (ICML 2025): Augmented Emotional Relation Graph; AND an ablation showing
  NAIVE LLaMA-3.1-8B label sentence embeddings HURT performance.
=> "label relations / label semantics help decoding" cannot be our novelty; they
   own it, and naive semantic labels are shown harmful.

WHITE SPACE (grounded):
- Fine-grained (34) x cross-taxonomy (34 <-> Emo-FilM 15/50) x cross-dataset
  transfer, bridged by SEMANTIC label queries. Du/Fu are all single-dataset,
  fixed label set. Supramodal literature shows an abstract emotion code exists at
  the basic level but nobody has shown fine-grained cross-taxonomy transfer.
- Neuroscience claim is a PRESENCE claim (a neural emotion code generalizes across
  stimulus regimes), which dodges the reverse-inference / absence fallacy that
  killed the earlier 3-class taxonomy plan.

## Design answer forced by the references
EmoGrowth ("naive LLM labels hurt") + C-Tran (label mask training) =>
Do NOT hard-wire frozen LLM embeddings as labels. Use queries INITIALISED from
semantic emotion-word embeddings but LEARNABLE, trained with label masking, so the
model exploits label structure without over-relying on the raw embedding. This is
the disciplined form of semantic label queries and the mechanism that makes
cross-taxonomy transfer possible while avoiding the EmoGrowth failure mode.

## Boundary with EmoViS
EmoBrain owns model-level, representational claims (which emotions decodable;
cross-regime generality of the code). EmoViS owns brain-level cortical location /
RSA. Discovery framed as "code generality," not "cortical topography," stays on the
EmoBrain side.

## Learning strategy (Pillar 1) — grounding
Problem from our own data: stimulus decodes 0.493, brain marginal +0.028. Naive
joint training free-rides on stimulus and ignores the brain. The strategy's single
goal: a MODALITY- and LABEL-set-INVARIANT emotion code (what makes cross-dataset
transfer possible). Four mechanisms, each a development of a known technique, all
serving that one goal:
- Modality dropout — force each modality to be usable alone; counter stimulus
  free-riding; robustness when Emo-FilM lacks a modality. Refs: MMP (Masked
  Modality Projection, arXiv:2410.03010); Cross-Modal Proxy Tokens
  (arXiv:2501.17823); MICCAI 2025 contrastive fusion with improved modality
  dropout (papers.miccai.org/miccai-2025/paper/2038).
- Cross-modal consistency / modality-invariant representation — brain-alone read
  ~= full read, so the emotion code is stimulus-general (grounds the neuroscience
  presence-claim). Refs: alignment/InfoNCE + regression alignment losses;
  Sci Rep 2025 s41598-025-29558-2 (consistency under complete modality missing).
- Label masking — C-Tran (already cited): predict masked labels -> handle any label
  subset -> cross-taxonomy.
- Teacher->student distillation — LUPI / Lopez-Paz ICLR 2016 (already cited).

Novelty of the strategy itself is MODERATE (the mechanisms are known); the
contribution is the invariance-for-transfer recipe tailored to brain-emotion +
cross-dataset, and the strategy is justified as the mechanism that yields the real
novelty (transfer), not as a standalone claim.

## Cross-dataset emotion generalization landscape
Existing work is mostly EEG, valence/arousal, and domain ADAPTATION (needs target
data): DEAP / SEED / DREAMER benchmarks; source-free UDA (arXiv:2606.28202);
multi-source joint DA (PMC9520599). Reviews note that annotation-scheme (label
taxonomy) transfer is "yet to be systematically investigated" => fMRI +
fine-grained + cross-taxonomy + zero-shot label transfer is open (our lane).

## 2026-08-17 verification pass — additions, corrections, status
Repo PDFs were checked by actual text extraction (pypdf), not filename or notes.

CORRECTIONS
- `docs/reference/papers/Doerig2025_Aligning_representations.pdf` is MISLABELED. The
  actual paper is Muttenthaler, Greff, Born, Spitzer, Kornblith, Mozer, Muller,
  Unterthiner, Lampinen. "Aligning machine and human visual representations across
  abstraction levels." Nature 647 (2025-11-13) p.349. Cite as Muttenthaler et al.
  2025, never "Doerig". Method (verified): train a teacher to imitate human
  similarity judgements, then DISTIL the human-aligned representational STRUCTURE
  (pairwise distances -> KL soft labels) into a student model. = direct precedent for
  geometry/structure teacher->student transfer.
- BioReason (DNA-LLM, arXiv 2505.23579) is misfiled under BrainVLM_emotion; unrelated.
- Duplicate PDFs: 2505.23579, 2604.03619.

NEW LOAD-BEARING (repo PDF verified)
- OV-MER — Lian et al. 2025. Open-Vocabulary Multimodal Emotion Recognition. Predicts
  emotions "beyond a fixed label space", generalises to "unseen or new labels";
  zero-shot benchmarks; new dataset + metrics. STIMULUS-side (video/audio/text), NOT
  brain. => "open-vocabulary emotion" is preempted as a concept; our claim is the
  BRAIN version. Adopt their framing/metrics; cite head-on.

LEARNING-STRATEGY references (geometry-first)
- RKD — Park, Kim, Lu, Cho. Relational Knowledge Distillation. CVPR 2019. Distils
  distance-wise / angle-wise RELATIONS (geometry), not individual outputs.
  [search-level; NOTE: EmoGrowth's "RKD" is RSM-based (Kriegeskorte RSA), related but
  not identical to Park's distance/angle RKD.]
- ML-GCN — Chen, Wei, Wang, Guo. Multi-Label Image Recognition with GCN. CVPR 2019.
  Label word-embedding nodes + co-occurrence matrix -> inter-dependent classifiers.
  [search-level; corroborated as a baseline inside ML-BVAE's PDF.]
- CLIP — Radford et al. ICML 2021 (contrastive cross-modal, zero-shot). SupCon —
  Khosla et al. NeurIPS 2020 (labels define positives). [search-level.]
- Muttenthaler et al. Nature 2025 (above): structure/geometry teacher->student, verified.

Du/Fu preemption CONFIRMED from PDFs: ML-BVAE = masked self-attention co-occurrence
+ ML-GCN baseline; GED = bipartite emotion-ROI graph, MAE; EmoGrowth = RKD-RSM
distillation (2 teachers: affective-dim + old model) AND "naive LLaMA-3.1-8B label
embedding hurts" (Table 5 +SE worst). => relation/geometry learning is develop-not-invent.

VERIFICATION STATUS
- Verified from paper text: Du1-4, Muttenthaler, OV-MER.
- Search-level only (verify at final citation): RKD, ML-GCN, CLIP, SupCon, Query2Label,
  C-Tran, DETR, LUPI, Peelen 2010, Saarimaki 2016, Horikawa 2020.

## HEADWIND (mandatory control)
"Appraisal Dimensions Generalise Better than Emotion Labels for Cross-Age Affect
Recognition" (arXiv:2604.27938): fine-grained emotion LABELS transfer WORSE than
appraisal DIMENSIONS across datasets. This is the central risk to our cross-taxonomy
label-transfer novelty. Our semantic label queries are the countermeasure. MUST
include a dimension-transfer control: show our semantic-label transfer matches or
beats dimension transfer, or a reviewer rejects with this paper. This also revives
the arousal/valence + appraisal axes as a control condition, not the headline.
