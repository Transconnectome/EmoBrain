# (2025) fMRI-LM

**Source:** (2025) fMRI-LM.pdf

---

## Page 1

fMRI-LM: Towards a Universal Foundation Model for Language-Aligned fMRI
Understanding
Yuxiang Wei
TreNDS
weiyuxiang@gatech.edu
Yanteng Zhang
TreNDS
Xi Xiao
University of Alabama at Birmingham
Chengxuan Qian
Jiangsu University
Tianyang Wang
University of Alabama at Birmingham
Vince D. Cahoun
TreNDS
vcalhoun@gatech.edu
Abstract
Recent advances in multimodal large language models
(LLMs) have enabled unified reasoning across images, au-
dio, and video, but extending such capability to brain imag-
ing remains largely unexplored. Bridging this gap is es-
sential to link neural activity with semantic cognition and
to develop cross-modal brain representations. To this end,
we present fMRI-LM, a foundational model that bridges
functional MRI (fMRI) and language through a three-stage
framework. In Stage 1, we learn a neural tokenizer that
maps fMRI into discrete tokens embedded in a language-
consistent space. In Stage 2, a pretrained LLM is adapted
to jointly model fMRI tokens and text, treating brain activity
as a sequence that can be temporally predicted and linguis-
tically described. To overcome the lack of natural fMRI–text
pairs, we construct a large descriptive corpus that trans-
lates diverse imaging-based features into structured textual
descriptors, capturing the low-level organization of fMRI
signals. In Stage 3, we perform multi-task, multi-paradigm
instruction tuning to endow fMRI-LM with high-level se-
mantic understanding, supporting diverse downstream ap-
plications. Across various benchmarks, fMRI-LM achieves
strong zero-shot and few-shot performance, and adapts effi-
ciently with parameter-efficient tuning (LoRA), establishing
a scalable pathway toward a language-aligned, universal
model for structural and semantic understanding of fMRI.
1. Introduction
Functional magnetic resonance imaging (fMRI) provides a
noninvasive window into human brain activity by capturing
blood-oxygen-level-dependent (BOLD) fluctuations across
* Preliminary work. Codes and model checkpoints will be publicly
available soon.
Figure 1. The proposed fMRI-LM outperforms baselines on di-
verse tasks. fMRI-LM demonstrates comprehensive and powerful
performance.
distributed regions. Deep learning has achieved strong per-
formance on supervised fMRI tasks such as phenotype pre-
diction and disease diagnosis [3, 17, 19, 20, 23, 35], but
these models typically require task-specific tuning and la-
beled data, limiting scalability and cross-study generaliza-
tion. Recent fMRI foundation models, such as BrainLM
and Brain-JEPA [5, 9], pretrain on large neuroimaging cor-
pora and transfer well to downstream tasks, yet they remain
confined to neural-only objectives (e.g., masked prediction,
contrastive learning), requires task-specific tuning, and lack
grounding in language.
In parallel, large language models (LLMs) and multi-
modal LLMs (MLLMs) have demonstrated strong cross-
modal reasoning over images, audio, and video [4, 21, 22,
37]. MLLMs typically pair an off-the-shelf LLM with a
modality-specific encoder whose outputs are aligned with
the text embedding space. Inspired by this design, recent
work on EEG [14, 15] treats neural signals as a kind of “lan-
guage” by quantizing activity into symbolic representations
1
arXiv:2511.21760v1  [cs.CL]  24 Nov 2025


## Page 2

and aligning them with pretrained LLMs. However, these
approaches mainly rely on fixed single-question–single-
answer templates, underutilizing LLMs’ generative and rea-
soning capabilities; they also focus on EEG rather than
fMRI, and the absence of natural fMRI–text pairs prevents
modeling of linguistic semantics that describe brain func-
tion.
Although several recent works employ LLMs for
fMRI-to-text decoding [28, 36], they are tailored to task-
fMRI settings with explicit stimulus–text pairs and primar-
ily use the LLM’s embedding space to map neural activity
back to presented text. In contrast, our goal is to develop
a generalizable fMRI foundation model that understands
resting-state and task-independent neural patterns, without
relying on task-evoked paired text.
To explore the potential of LLMs for universal fMRI un-
derstanding, we propose fMRI-LM, a foundational model
that bridges fMRI and language through a unified multi-
stage framework. fMRI-LM is pretrained on over 50,000
fMRI scans spanning a wide age range. A key component
is a structured fMRI–text corpus that converts imaging-
derived features—functional connectivity, graph-theoretical
metrics, functional gradients, and ICA (independent com-
ponent analysis) components—into standardized textual de-
scriptions, providing language-grounded access to the low-
level structure of fMRI, understood as pre-semantic pat-
terns of connectivity and functional organization analogous
to low-level spatial and textural features in images.
In
Stage 1 (fMRI tokenizer training), a Transformer-based
tokenizer with vector quantization maps fMRI into token
embeddings aligned with the LLM’s text embedding space.
In Stage 2 (LLM fine-tuning), a pretrained LLM is tuned
to model fMRI tokens and synthetic fMRI–text pairs, en-
abling both temporal modeling of brain activity and fMRI-
conditioned text generation.
Stage 3 (downstream in-
struction tuning) performs multi-task, multi-paradigm in-
struction tuning—covering single- and multi-question an-
swering and open-ended description generation—to endow
fMRI-LM with high-level semantic understanding across
diverse neuroscience and clinical tasks. As summarized in
Fig. 1, fMRI-LM outperforms strong baselines on a range
of benchmarks.
Our key insight is that this descriptive corpus forms a
bridge between low-level neural organization and high-level
cognitive semantics, analogous to how captions connect im-
age structure to scene meaning in vision–language mod-
els. By aligning fMRI with language through this corpus,
fMRI-LM learns representations that are transferable across
datasets, subjects, and tasks. Overall, our contributions are:
• We introduce fMRI-LM, to our knowledge the first
LLM-aligned foundational framework for fMRI that
maps resting-state and task-independent brain activity
into a token space compatible with pretrained language
models, enabling a unified interface for fMRI modeling
and instruction tuning.
• We construct a large-scale descriptive corpus that
translates fMRI imaging-based features into structured,
caption-like text, providing language supervision that
helps the LLM capture the low-level organization and in-
terpretable structure of fMRI signals.
• We show that fMRI-LM significantly outperforms su-
pervised and foundation baselines on standard bench-
marks, while exhibiting strong generalization across
tasks and datasets. Moreover, the model shows notable
efficiency, delivering strong results even with limited
training data and a small fraction of tunable parameters.
2. Related Work
Brain-LLM Alignment and Convergent Representa-
tions:
Recent large-scale analyses reveal that high-
performing deep learning models, particularly LLMs, nat-
urally develop representations that align with brain activity.
Shen [31] found that brain–model alignment strongly cor-
relates with task performance and even precedes capabil-
ity gains during training. Likewise, Badr [2] suggested that
LLMs develop brain-like representations for language and
eventually outgrow linguistic rules. Such convergent evolu-
tion between biological and language model intelligence in-
dicates that language models may capture representational
structures more consistent with human cognition.
Moti-
vated by this, we hypothesize that LLMs provide a strong
semantic prior for modeling fMRI signals and can enable
richer interpretations than task-specific architectures.
Foundation Models for fMRI Understanding: Recent
work in fMRI analysis has shifted from task-specific pre-
diction to general representation learning, driving the de-
velopment of foundation models that extract transferable
neural features from large-scale data.
The early super-
vised CNN and GNN-based approaches performed well
in diagnostic tasks but generalized poorly across cohorts
[16, 17, 19, 20, 23]. Recent self-supervised models such
as BrainLM [5] and Brain-JEPA [9] improve robustness by
pretraining with masked reconstruction or contrastive ob-
jectives before task-specific fine-tuning.
However, these
models remain task-bound and lack semantic grounding.
Our work addresses this gap by aligning fMRI represen-
tations with an LLM backbone to enable unified, language-
informed understanding of brain activity.
3. Methodology
In this section, we explain the modules and training pipeline
of fMRI-LM. As illustrated in Fig. 4, we first train an fMRI
tokenizer composed of a ViT-based encoder [9] and a quan-
tizer [25, 34] that produces fMRI tokens aligned with the
frozen text space. A pretrained LLM is then tuned to predict
the fMRI tokens and text tokens, followed by supervised in-
2


## Page 3

Table 1. fMRI-text descriptors
type
level
name
FC
ROI
Network-pair connectivity
Global
Top/bottom connectivity patterns
FG
ROI
Network gradient values
Global
Principal/second/third gradient range
Global
Gradient variance
ICA
ROI
Network temporal amplitude, variability, spectral ratio
ROI
Network-pair FNC
ROI
Network fALFF
Global
Overall temporal amplitude, variability, spectral ratio
Graph
ROI
Network strength
Global
Modularity, global efficiency, average clustering coefficient
struction tuning.
Given the 4D fMRI Xraw ∈RT ×X×Y ×Z, we follow pre-
vious works [5, 9] and parcellate into ROI-level fMRI sig-
nals based on atlas Schaefer-400 [30] for cortical regions
and Tian-Scale III [33] for subcortical regions, resulting in
N = 450 ROIs: X ∈RT ×N.
3.1. fMRI-Text Descriptor Construction
In common vision–language model training, each image is
paired with one or more textual descriptions that capture its
spatial structure and semantic content. Such captions pro-
vide a bridge between visual and linguistic representations,
enabling effective multimodal alignment. However, due to
the abstract and high-dimensional nature of fMRI data, no
analogous text descriptions exist in prior studies.
To address this challenge, we curate a structured text
corpus that describes each fMRI data in terms of four
complementary feature domains: functional connectivity
(FC), functional gradient (FG), graph-theoretical metrics,
and independent component analysis (ICA). Each descrip-
tion summarizes both the region-of-interest (ROI)–level and
global characteristics derived from these representations, as
detailed in Tab. 1.
All functional brain measures are z-
scored and normalized relative to the cohort distribution
(UK Biobank) to enable interpretable, standardized com-
parisons across subjects. The quantitative values are then
fit to a template to generate cohesive text descriptions. To-
gether, these descriptors capture diverse aspects of intrinsic
brain organization and serve as linguistic analogs of neu-
ral representations, facilitating multimodal alignment with
language models. Complete explanations and the meaning
of each descriptor are elucidated in Appendix A. To ensure
the descriptors contain meaningful information, we train a
BERT classifier [7] with the 4 types of descriptors for UKB
sex prediction and compare it with the BrainNetCNN [19]
model, as presented in Fig. 3.
Subject attributes such as demographics are widely used
to enhance downstream task accuracy, especially disease
diagnosis [35, 38]. We further utilize the demographics,
phenotypical, cognitive, and physical attributes to construct
high-level subject descriptions.
These semantic descrip-
tions are only used in Stage 3 disease- and cognition-related
Timestep
ROI#1
Parcels
ROI#2
ROI#3
ROI#N
Transformer 
Blocks
Transformer 
Blocks
fMRI Encoder
Quantizer
fMRI 
Embeddings
Codebook
Codebook
fMRI Tokenizer
fMRI Tokens
Transformer 
Blocks
Transformer 
Blocks
fMRI Decoder
Reconstruction Loss
Random Text 
Tokens
Domain 
Classifier
Domain 
Classifier
Text or fMRI?
Domain Confusion 
Loss
reverse gradient
Paired fMRI
Descriptions
CLIP/SigLIP
CLIP/SigLIP
Contrastive
Loss
fMRI Data
Figure 2. Overview of the fMRI tokenizer, which consists of a
Transformer-based encoder and a vector quantizer. The tokenizer
is trained with reconstruction, domain-adversarial, and contrastive
alignment losses to align fMRI representations with the LLM’s
text-embedding space.
Figure 3. Descriptors’ predictive strength over UKB sex. Using
all descriptors (”All Desc”) can achieve about 70% accuracy.
tasks only. Further details are given in Sec. 4.1 and in Ap-
pendix A.5.
3.2. Text-Aligned fMRI Tokenizer
To enable pretrained LLMs to understand non-text modal-
ities, it is essential to first encode the input data into em-
beddings that are aligned with the frozen text space. We
therefore design a text-aligned fMRI tokenizer, which maps
fMRI signals into discrete neural tokens that share a consis-
tent representational geometry with language embeddings.
Architecture.
We employ a Transformer-based encoder
Eθ inspired by recent neural encoding frameworks [9], fol-
lowed by a vector quantizer to discretize the continuous
embeddings.
As shown in Fig. 2, given an fMRI input
X ∈RT ×N, the encoder Eθ(·) produces a latent feature
sequence z = Eθ(X), where z ∈RM×C, C denotes the
embedding dimension, and M = [ T
P ] × N = T ′ × N is the
sequence length. The patch size P is applied only along the
temporal dimension to preserve all ROI features.
A quantization module Q, then maps each continuous la-
tent vector zm to a discrete representation ezm. This module
can be implemented using various schemes, such as stan-
3


## Page 4

fMRI 
Tokenizer
fMRI 
Tokenizer
Domain Confusion 
Loss
Contrastive
Loss
Text
Encoder
Text
Encoder
Text
Encoder
Reconstruction
Loss
Random
Text
Functional 
Connectivity
Functional 
Gradient
ICA
fMRI Descriptors
Paired fMRI 
Descriptor
fMRI Data
Pretrained LLM
Pretrained LLM
Pretrained LLM
Pretrained LLM
Pretrained LLM
modularity=?
global 
efficiency=?
clustering 
coefficient=?
Graph Metrics
modularity=?
global 
efficiency=?
clustering 
coefficient=?
Graph Metrics
(a) fMRI-Text 
descriptor construction
(b) Stage 1: text-aligned fMRI tokenizer
cross-entropy
fMRI Tokens
Paired Text 
Tokens
Random Text 
Tokens
(c) Stage 2: LLM fine-tuning
Pretrained LLM
Pretrained LLM
Pretrained LLM
Pretrained LLM
Pretrained LLM
what is
the sex
fMRI Tokens
Question
Answer: male [eos]
cross-entropy
Text Tokens (Answer)
(d) Stage 3: multi-task multi-paradigm 
instruction tuning
multiple tasks
sex classification
AD diagnosis
age prediction
multiple paradigms
single-question 
single-answer
multi-question
multi-answer
open-ended 
question
High-Level Desc
Optional
Figure 4. Overall training pipeline of fMRI-LM. (a) fMRI–text pairs are constructed from four types of features: functional connectivity,
graph metrics, functional gradients, and ICA-based components. (b) Stage 1: align the fMRI tokenizer with the frozen text embedding
space. (c) Stage 2: tune a pretrained LLM to generate linguistic or temporal representations conditioned on fMRI tokens. Use either full
fine-tuning or LoRA [13]. (d) Stage 3: multi-task multi-paradigm instruction tuning for downstream tasks. High-level descriptions are
used as optional input for enhanced performance.
dard vector quantization (VQ) [34]. The resulting sequence
˜z = [˜z1, · · · , ˜zM] serves as discrete fMRI representation.
To preserve information fidelity, a lightweight decoder
Dϕ is trained to reconstruct the original input. The objective
for the tokenizer’s autoencoding component is:
Lquant = ∥X −Dϕ(˜z)∥2
2 + Lcommitment,
(1)
where the first term is the reconstruction loss and Lcommitment
is a regularizing term depends on Q.
Domain-Adversarial Alignment. Following the domain
adaptation strategy of [11, 14], we align fMRI embed-
dings with the text-embedding space of a pretrained LLM.
Specifically, we sample text embeddings ztext ∈RM×C
from a frozen LLM (e.g., GPT-2) using tokens drawn from
OpenWebText [12].
A domain classifier C is trained to
discriminate whether a given embedding originates from
fMRI or text, while a gradient reversal layer (GRL) is ap-
plied between Eθ and C to enforce confusion. The domain-
adversarial loss is defined as
Ldomain = −1
M
M
X
m=1
h
tm log C(zm)+(1−tm) log(1−C(zm))
i
(2)
where tm = 1 if the sample is from fMRI and tm = 0
otherwise. This adversarial objective encourages the fMRI
tokenizer to produce embeddings that are indistinguishable
from text embeddings in the LLM space.
Contrastive Cross-Modal Alignment. To further bridge
the modality gap, we leverage the synthetic text descriptors
introduced in Sec. 3.1 to form paired fMRI–text data. We
employ a SigLIP-style contrastive loss [40], which max-
imizes similarity between paired embeddings while mini-
mizing it across unpaired samples:
Lcontrast = −1
B
B
X
i=1
log
exp(σ · sim(zi, z+
i ))
PB
j=1 exp(σ · sim(zi, z+
j ))
(3)
where sim(·, ·) denotes cosine similarity, zi and z+
i repre-
sent matched fMRI and text features, σ is a temperature pa-
rameter, and B is the batch size.
Overall Objective. The final loss for the text-aligned fMRI
tokenizer combines reconstruction, domain-adversarial, and
contrastive terms:
Ltokenizer = Lquant + Lcontrast + λLdomain
(4)
where λ is empirically set to 0.5. Through this joint op-
timization, the tokenizer learns discrete neural tokens that
both preserve fMRI structure and align closely with the se-
mantic geometry of text embeddings.
3.3. LLM Fine-Tuning and Temporal Modeling
Given discrete fMRI tokens, we fine-tune a pretrained LLM
to model temporal dynamics and generate text. Let z =
4


## Page 5

What is the sex of this subject?
Male
What is the sex of this subject? 
Does it have Alzheimer?
This is a male subject with AD
Single-question Single-answer
Muti-question Multi-answer
Based on the fMRI scan, what subject’s 
information can you provide?
Mild cognitive impairment is present in this 
senior female, who has no APOE4 alleles 
and positve AV45 status
Open-ended question
Figure 5. Three paradigms for instruction tuning
{z(w,n)} denote the token sequence, where w = 1, . . . , T ′
is the time index and n = 1, . . . , N indexes ROIs, and let
I(w,n) ∈V be the corresponding vocabulary indices gener-
ated from the quantizer.
Model Input and Objectives. Unlike standard language
modeling, where the model predicts the next word in a tex-
tual sequence, fMRI data exhibit a temporal–spatial struc-
ture. Inspired by [14], we adapt the LLM to perform tem-
poral next-step prediction. Formally, given tokens from
N ROIs at time w, the LLM predicts the N tokens at w +1.
To endow the LLM with both neural and linguistic
competence, we introduce three complementary training
paradigms as illustrated in Fig. 4(c):
• fMRI-to-fMRI (F2F): temporal next-step prediction of
fMRI tokens using Eq. (5):
LF2F = −
T ′−1
X
w=1
N
X
n=1
log Pθ

I(w+1,n) | z(w,1), . . . , z(w,N)
(5)
where θ denotes the LLM parameters and Pθ represents
the autoregressive probability distribution over the ex-
tended vocabulary. This objective encourages the LLM
to capture temporal dependencies in neural activity.
• fMRI-to-Text (F2T): conditioned text generation, where
the model learns to produce descriptive text tokens given
an fMRI token sequence.
• Text-to-Text (T2T): standard language modeling with
random text to preserve LLM’s original linguistic ability.
The combined loss for LLM alignment is thus:
LLLM = LF2T + αLF2F + βLT2T
(6)
where α and β are empirically set to 0.1 and 0.5.
3.4. Multi-Task Multi-Paradigm Instruction Tun-
ing
Foundational vision–language models benefit greatly from
diverse instruction-tuning objectives, which enable strong
generalization across heterogeneous tasks [32]. To enable
flexible reasoning across diverse neuroscience and clinical
tasks, we perform multi-task, multi-paradigm instruc-
tion tuning on top of the aligned LLM (Stage 3). Tasks
are presented as natural-language queries paired with target
responses, covering phenotype prediction, cognitive state
classification, and disease diagnosis.
We adopt three paradigms (Fig. 5): (i) single-question
single-answer, (ii) multi-question multi-answer, and (iii)
open-ended description. The open-ended setting instructs
the model to produce free-form text (e.g., interpreting sub-
ject characteristics), encouraging generalizable semantic
understanding. Detailed prompt formats and task defini-
tions are provided in Appendix D.
Importantly, the three paradigms are designed primarily
as complementary evaluation protocols with increasing dif-
ficulty, not as a way to enlarge the instruction-tuning corpus.
They reuse the same underlying supervision (labels and at-
tributes) but present it under different interaction formats,
allowing us to probe how well fMRI-LM handles basic pre-
diction, multi-target reasoning, and free-form generation.
4. Experiments
4.1. Experimental Settings
Datasets. We primarily focus on resting-state fMRI due
to its wide availability and standardized acquisition pro-
tocols.
Two large-scale public datasets—UK Biobank
(UKB) [26] and Adolescent Brain Cognitive Development
(ABCD) [18]—are used in stage 1 and 2.
Each dataset
is randomly split with an 80%–20% ratio for pretraining
and held-out downstream evaluation. To assess generaliza-
tion and zero-shot transfer, we further include six external
datasets spanning multiple age groups and clinical condi-
tions, as summarized in Tab. 2.
Since these datasets vary in spatial and temporal reso-
lutions across imaging sites, we standardize all data to en-
sure consistent temporal resolution and input shape. Specif-
ically, we resample all fMRI time series to a repetition time
(TR) of 2.0 s and clip or linearly interpolate each sequence
to 160 time points, with 450 ROIs extracted using Schaefer-
400 and Tian-Scale III atlases [30, 33]. Before feeding the
data into the tokenizer, we perform robust z-score normal-
ization across time for each ROI and apply site-wise vari-
ance normalization to mitigate scanner-related biases.
Paired fMRI-Text Curation and Prompt Expansion. To
construct paired fMRI–text data, we generate imaging-
based textual descriptors for each scan in UKB. Each scan
is represented by 23 descriptors derived from four domains,
as described in Sec. 3.1. We use fixed templates to con-
vert numerical statistics into natural-language statements,
which are subsequently refined into cohesive paragraphs us-
ing DeepSeek-V3 [24]. Subject-level semantic descriptions
5


## Page 6

Table 2. Dataset summary. Datasets marked with * are also used
for zero-/few- shot evaluation. More details in Appendix B.
Dataset
Size
Age Group
Task
UKB* [26]
39305
37-87
Sex, Age, Fluid Intel
ABCD [18]
18337
9-11
Sex
HCP [10]
1079
22-37
Sex, Age, Fluid Comp
HCP-A* [10]
632
36-100
Sex, Age, Fluid Comp, Flanker
ADNI4 [27]
1030
55-90
Sex, Age, AD, Apoe4
ADHD200* [6]
624
7-22
ADHD
ABIDE2* [8]
1114
5-64
Autism
are similarly synthesized from demographic and diagnostic
attributes to capture broader cognitive or clinical informa-
tion. More information is in Appendix A.
For instruction tuning, we develop a diverse set of
prompts to improve generalization and linguistic robust-
ness. Each downstream paradigm is augmented with up to
200 paraphrased prompt variants generated via LLM rewrit-
ing. In training, a random subset of prompts is sampled at
each iteration to avoid overfitting to specific phrasings.
Implementation Details. We introduce three model sizes,
fMRI-LM-S, fMRI-LM-B, and fMRI-LM-L with train-
able parameters of 46M, 174M, and 610M, respectively (ex-
cluding the base LLM). The tokenizer employs a Trans-
former encoder with a temporal patch size of 32 and a
vanilla vector quantizer [34], although other quantizers
(e.g., FSQ [25]) can be substituted. Unless otherwise stated,
we report results for fMRI-LM-B with GPT-2 (124M) [29].
All three stages are trained for 50 epochs using AdamW
with a learning rate of 10−4, cosine-annealing scheduler,
and batch size of 32. In Stage 1, we freeze the text encoder
and train only the fMRI tokenizer. In Stages 2 and 3, the
tokenizer is frozen while the LLM is tuned using either full
fine-tuning or parameter-efficient LoRA [13]. More details
on training hyperparameters can be found in Appendix C.
4.2. Main Results
In this section, we systematically evaluate fMRI-LM to
answer the following questions: Baseline Comparison:
Can fMRI-LM surpass SOTA baselines on standard single-
question tasks? Versatility: Does instruction tuning allow
for diverse formats without performance loss? General-
ization: Does the model demonstrate zero- Efficiency: Is
the model effective under data and tuning parameter con-
straints?
Single-Question Single-Answer. We first evaluate fMRI-
LM-B with GPT-2 and Qwen3-0.6B backbones under
the single-question single-answer paradigm, and compare
against supervised and foundation models for fMRI. Note
that fMRI-LM is tuned jointly on the 5 datasets. For regres-
sion targets, the tokenized output space of LLMs is inher-
ently discrete and thus poorly suited for directly predicting
continuous values. We therefore adopt two strategies: (i)
linear probing [1] with a lightweight prediction head on top
Figure 6. Performance of fMRI-LM on the multi-question multi-
answer across UKB, HCP-A, and ADNI. We report results when
training independently on each dataset and when jointly training
on all three. ”baseline” refers to single-question single-answer.
Figure 7. Zero-shot and few-shot generalization of fMRI-LM. We
evaluate three settings: new task on the same dataset, same task on
a new dataset, and new task on a new dataset. ”baseline” refers to
single-question single-answer.
of the LLM’s hidden representations, and (ii) discretizing
continuous variables into ordinal bins and formulating them
as classification, allowing the model to output faithful dis-
crete responses. Details of the discretization and additional
results are provided in Appendices B, E, and F.
As shown in Tab. 3 and Tab. 4, the two variants of
fMRI-LM achieve the best or second-best performance on
most datasets and targets. Although fMRI-LM underper-
forms Brain-JEPA on ADNI-AD, we emphasize that the key
strength of our framework is its unified instruction-tuning
pipeline and its ability to handle diverse tasks without ex-
tensive task-specific fine-tuning.
Multi-Question Multi-Answer.
We next evaluate the
multi-question multi-answer paradigm, where each fMRI
scan is paired with multiple questions and the model must
predict all answers simultaneously. We report results on
UKB, HCP-A, and ADNI, as summarized in Fig. 6. De-
tailed definitions of each target and its possible values are
provided in Appendix D.2.
Compared
to
the
single-question
setting,
perfor-
6


## Page 7

Table 3. Compare fMRI-LM with supervised methods and foundation models on classification tasks. Bold denotes the best method and
underline denotes the 2nd best. Note: fMRI-LM-B(G) denotes fMRI-LM-B(GPT2).
Type
Method
UKB-Sex
HCP-Sex
ADNI-AD
ADHD200-ADHD
ABIDE2-ASD
Acc
AUC
Acc
AUC
Acc
AUC
Acc
AUC
Acc
AUC
Supervised
BrainNetCNN [19]
78.32 (1.12)
80.05 (1.06)
82.01 (2.11)
86.94 (1.64)
75.92 (2.24)
77.09 (1.62)
52.19 (3.14)
56.21 (2.82)
56.32 (2.45)
57.82 (2.51)
BrainGNN [23]
77.31 (2.47)
79.53 (1.46)
79.09 (1.81)
81.56 (0.49)
68.72 (2.84)
69.06 (3.11)
55.67 (2.49)
56.72 (1.69)
57.02 (2.67)
58.09 (3.73)
BNT [17]
72.71 (2.64)
73.38 (1.92)
72.67 (1.49)
72.05 (1.32)
70.19 (3.20)
72.34 (2.25)
55.54 (2.39)
57.05 (3.32)
52.19 (3.10)
54.22 (2.44)
FBNETGEN [16]
83.54 (4.67)
83.56(2.67)
80.64 (2.41)
79.29 (3.91)
76.74 (2.55)
77.64 (1.09)
49.18 (1.76)
52.42 (2.69)
51.12 (1.36)
54.65 (2.08)
SWiFT [20]
84.90 (1.88)
85.34 (3.19)
72.91 (1.49)
71.69 (1.64)
71.95 (2.22)
70.08 (1.5UY9)
57.70 (2.44)
58.04 (1.88)
52.33 (2.21)
55.46 (2.72)
Foundation
BrainLM [5]
88.72 (0.88)
90.42 (0.59)
81.09 (1.76)
82.34 (2.21)
78.82 (1.54)
75.21 (1.68)
71.22 (1.49)
65.21 (1.68)
65.22 (2.28)
67.29 (1.18)
BrainMass [39]
92.31 (0.19)
92.85 (0.22)
75.32 (0.49)
77.19 (1.01)
80.05 (2.21)
83.35 (1.98)
66.19 (2.27)
62.24 (1.79)
58.79 (1.12)
63.48 (1.79)
Brain-JEPA [9]
88.77 (0.75)
90.13 (0.63)
77.82 (1.12)
79.19 (1.62)
82.26 (2.17)
84.05 (2.64)
72.04 (2.39)
65.18 (2.42)
57.49 (1.49)
64.28 (1.95)
fMRI-LM-B(G)
94.89 (0.22)
94.90 (0.16)
89.58 (0.31)
89.13 (0.79)
77.92 (1.01)
79.91 (1.25)
72.92 (1.34)
68.72 (2.01)
65.97 (1.09)
68.72 (1.33)
Table 4. Compare fMRI-LM with supervised methods and foundation models on regression tasks. Bold denotes the best method and
underline denotes the 2nd best. Note: fMRI-LM-B(G) denotes fMRI-LM-B(GPT2).
Method
UKB
HCP
HCP-Aging
Age
Fluid Intel
Age
Fluid Comp
Flanker
Fluid Comp
MAE↓
p↑
MAE↓
p↑
MAE↓
p↑
MAE↓
p↑
MAE↓
p↑
MAE↓
p↑
SwiFT
3.40 (0.21)
0.49 (0.073)
1.85 (0.092)
0.67 (0.011)
2.58 (0.25)
0.51 (0.046)
5.15 (0.39)
0.62 (0.11)
6.85 (0.44)
0.19 (0.035)
5.32 (0.26)
0.59 (0.067)
BrainMass
2.01 (0.052)
0.77 (0.063)
1.59 (0.039)
0.88 (0.016)
3.01 (0.19)
0.49 (0.052)
5.29 (0.84)
0.55 (0.20)
5.66 (0.75)
0.40 (0.016)
5.05 (0.49)
0.58 (0.16)
Brain-JEPA
1.69 (0.088)
0.76 (0.10)
1.59 (0.042)
0.92 (0.011)
2.55 (0.15)
0.62 (0.069)
4.87 (0.096)
0.70 (0.062)
5.21 (0.13)
0.44 (0.036)
4.88 (0.056)
0.73 (0.074)
fMRI-LM-B(G)
1.82 (0.061)
0.85 (0.034)
1.51 (0.011)
0.95(0.006)
2.56 (0.13)
0.62 (0.11)
4.68 (0.25)
0.74 (0.033)
5.11 (0.075)
0.50 (0.006)
4.70 (0.29)
0.76 (0.029)
mance under the multi-question paradigm degrades only
marginally relative to strong baselines, with the largest drop
observed for AD prediction on ADNI. In contrast, fMRI-
LM achieves comparable or even higher accuracy on sev-
eral targets (e.g., sex, fluid composite, and flanker scores),
suggesting that jointly training on multiple, potentially cor-
related targets can help the model acquire more universal
fMRI representations and solve a broader set of tasks.
Open-Ended Question.
We further evaluate fMRI-LM
on open-ended questions on UKB, HCP-A, and ADNI, as
shown in Fig. 8. All datasets share three common target
fields, and each dataset additionally includes a small set of
unique targets. The “overall” metric requires all fields in a
generated sentence to match the ground-truth labels in order
for the prediction to be counted as correct. Detailed defini-
tions are given in Appendix D.3.
Since the model is tuned to generate cohesive free-form
text instead of structured single or multiple answers, we em-
ploy DeepSeek-V3 as an automatic evaluator to determine
whether the generated answer matches the target fields, and
subsequently perform manual verification by human ex-
perts. From Fig. 8, fMRI-LM performs surprisingly well
on several targets such as sex and fluid composite status,
achieving accuracy comparable to the structured paradigms.
Jointly training across datasets (except for ADNI, likely due
to its biomarker-driven, disease-specific distribution differ-
ing from the others) further improves performance, indicat-
ing that fMRI-LM benefits from task and dataset diversity
and can develop more universal fMRI understanding.
Zero-Shot and Few-Shot Generalization.
We finally
test whether fMRI-LM can generalize to unseen tasks or
datasets with no or limited labeled data (2, 4, and 10 sam-
ples, balanced by label). We explore three configurations:
(i) new task on the same dataset, (ii) same task on a new
dataset, and (iii) new task on a new dataset. Concretely,
we first train the model on UKB for sex classification, then
evaluate its zero-shot and few-shot performance on fluid in-
telligence status prediction in UKB, sex classification on
HCP-A, disease-related tasks on ADHD200 and ABIDE2.
As shown in Fig. 7, fMRI-LM performs relatively poorly
in the strict zero-shot setting, but its performance improves
substantially even with only two labeled samples. This sug-
gests that the model learns general fMRI representations
can be quickly adapted with minimal supervision. Notably,
fMRI-LM attains performance comparable to using the full
downstream training set under a 4-shot setting for fluid in-
telligence status prediction and ASD prediction, indicating
that the model does not rely heavily on large downstream
datasets and can flexibly adapt to a wide variety of tasks.
4.3. Ablation Studies
More ablations on model size and loss configurations are
provided in Appendix G.
Effect of Imaging-Based and Semantic Descriptors. To
assess the contribution of the imaging-based descriptors in-
troduced in Sec. 3.1 and Appendix A, we evaluate fMRI-
LM without any paired fMRI–text data during pretraining
(i.e., removing the contrastive loss in Eq. (3) and the F2T
7


## Page 8

Figure 8. Open-ended question performance of fMRI-LM on UKB, HCP-A, and ADNI. We show models trained independently on each
dataset as well as a jointly trained model. “Baseline” indicates performance on each target under the single-question single-answer setting.
(a)
(b)
Figure 9. (a) Effect of imaging-based and semantic descriptors.
Semantic descriptors are only used for disease- and cognition-
related tasks. (b) Effect of LoRA-based tuning on fMRI-LM.
objective in Sec. 3.3). We also ablate the high-level se-
mantic text descriptions used as complementary input dur-
ing downstream tuning. The results are shown in Fig. 9(a).
Removing the imaging-based descriptors—and thus the
fMRI–text pairs used during pretraining—significantly de-
grades performance, especially on sex classification. While
performance on ADNI-AD slightly improves after removal,
we hypothesize this is due to distributional differences
between the pretraining data (UKB/ABCD) and ADNI’s
disease-focused population, which may reduce the benefit
of descriptor-based alignment in this specific case.
Parameter-Efficient Tuning via LoRA. While full fine-
tuning of LLMs is effective, it can be computationally de-
manding and prone to overfitting with limited data. To ad-
dress this, we investigate a parameter-efficient fine-tuning
approach using Low-Rank Adaptation (LoRA) [13] for
Stages 2 and 3. As shown in Fig. 9(b), employing LoRA not
only maintained but in some cases, improved performance
on tasks such as HCP sex classification and ADHD diagno-
sis. This suggests that LoRA effectively adapts the model
to fMRI data by tuning only a small fraction of its parame-
ters. This approach preserves the rich linguistic knowledge
encoded in the pretrained LLM, which is crucial for strong
performance, while efficiently learning the relevant neuro-
semantic representations from the fMRI inputs.
(a) Percentage of UKB
(b) Percentage of ABCD
Figure 10. Effect of pretraining data size on downstream perfor-
mance for HCP sex classification and ADNI AD prediction.
Impact of Pretraining Data Size. To explore the effect
of pretraining data scale, we vary the fraction of UKB and
ABCD used for pretraining (from 0% to 100%) and evalu-
ate downstream performance on HCP sex classification and
ADNI AD prediction.
As shown in Fig. 10, even with-
out UKB or ABCD, the model achieves reasonable perfor-
mance (around 70% for sex and 50% for AD). Removing
ABCD has smaller impact than removing UKB, which may
be attributed to domain shift (ABCD focuses on children,
while most other datasets focus on adults). Overall, perfor-
mance improves consistently with more pretraining data.
5. Conclusion
We introduced fMRI-LM, a foundational framework for
universal fMRI understanding that aligns fMRI with LLMs
through the synthetic fMRI–text descriptor corpus, which
provides scalable linguistic supervision in the absence of
natural fMRI–text pairs.
Extensive experiments across
seven datasets demonstrate fMRI-LM’s strong performance
and generalization, with further ablation studies validat-
ing the importance of paired descriptors and confirming its
adaptability and scalability, even under parameter-efficient
(LoRA) and few-shot settings. highlighting its adaptabil-
ity and scalability. This work presents a step toward uni-
fied, language-grounded brain modeling.
By leveraging
8


## Page 9

the structure and reasoning capabilities of LLMs, it offers
a scalable way to interpret fMRI, integrate heterogeneous
tasks, and transfer knowledge across studies.
References
[1] Guillaume Alain and Yoshua Bengio. Understanding inter-
mediate layers using linear classifier probes. arXiv preprint
arXiv:1610.01644, 2016. 6
[2] Badr AlKhamissi, Greta Tuckute, Yingtian Tang, Taha
Osama
A
Binhuraib,
Antoine
Bosselut,
and
Martin
Schrimpf. From language to cognition: How llms outgrow
the human language network. In Proceedings of the 2025
Conference on Empirical Methods in Natural Language Pro-
cessing, pages 24332–24350, 2025. 2
[3] Hasan A Bedel, Irmak Sivgin, Onat Dalmaz, Salman UH
Dar, and Tolga C¸ ukur.
Bolt: Fused window transformers
for fmri time series analysis. Medical image analysis, 88:
102841, 2023. 1
[4] Tom Brown, Benjamin Mann, Nick Ryder, Melanie Sub-
biah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakan-
tan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Lan-
guage models are few-shot learners. Advances in neural in-
formation processing systems, 33:1877–1901, 2020. 1
[5] Josue Ortega Caro, Antonio Henrique de Oliveira Fonseca,
Syed A Rizvi, Matteo Rosati, Christopher Averill, James L
Cross, Prateek Mittal, Emanuele Zappala, Rahul Madhav
Dhodapkar, Chadi Abdallah, et al. Brainlm: A foundation
model for brain activity recordings. In The Twelfth Interna-
tional Conference on Learning Representations. 1, 2, 3, 7
[6] ADHD-200 consortium. The adhd-200 consortium: a model
to advance the translational potential of neuroimaging in
clinical neuroscience. Frontiers in systems neuroscience, 6:
62, 2012. 6
[7] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina
Toutanova. Bert: Pre-training of deep bidirectional trans-
formers for language understanding. In Proceedings of the
2019 conference of the North American chapter of the asso-
ciation for computational linguistics: human language tech-
nologies, volume 1 (long and short papers), pages 4171–
4186, 2019. 3
[8] Adriana Di Martino, David O’connor, Bosi Chen, Kaat
Alaerts, Jeffrey S Anderson, Michal Assaf, Joshua H Bal-
sters, Leslie Baxter, Anita Beggiato, Sylvie Bernaerts, et al.
Enhancing studies of the connectome in autism using the
autism brain imaging data exchange ii. Scientific data, 4(1):
1–15, 2017. 6
[9] Zijian Dong, Ruilin Li, Yilei Wu, Thuan Tinh Nguyen,
Joanna Chong, Fang Ji, Nathanael Tong, Christopher Chen,
and Juan Helen Zhou.
Brain-jepa: Brain dynamics foun-
dation model with gradient positioning and spatiotemporal
masking. Advances in Neural Information Processing Sys-
tems, 37:86048–86073, 2024. 1, 2, 3, 7
[10] Jennifer Stine Elam, Matthew F Glasser, Michael P Harms,
Stamatios N Sotiropoulos, Jesper LR Andersson, Gregory C
Burgess, Sandra W Curtiss, Robert Oostenveld, Linda J
Larson-Prior, Jan-Mathijs Schoffelen, et al. The human con-
nectome project: a retrospective. NeuroImage, 244:118543,
2021. 6
[11] Yaroslav Ganin, Evgeniya Ustinova, Hana Ajakan, Pas-
cal Germain, Hugo Larochelle, Franc¸ois Laviolette, Mario
March, and Victor Lempitsky. Domain-adversarial training
of neural networks. Journal of machine learning research,
17(59):1–35, 2016. 4
[12] Aaron Gokaslan, Vanya Cohen, Ellie Pavlick, and Stefanie
Tellex.
Openwebtext corpus.
http://Skylion007.
github.io/OpenWebTextCorpus, 2019. 4
[13] Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-
Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen, et al.
Lora: Low-rank adaptation of large language models. ICLR,
1(2):3, 2022. 4, 6, 8
[14] Wei-Bang Jiang, Yansen Wang, Bao-Liang Lu, and Dong-
sheng Li. Neurolm: A universal multi-task foundation model
for bridging the gap between language and eeg signals. arXiv
preprint arXiv:2409.00101, 2024. 1, 4, 5
[15] Wei-Bang Jiang,
Li-Ming Zhao,
and Bao-Liang Lu.
Large brain model for learning generic representations
with
tremendous
eeg
data
in
bci.
arXiv
preprint
arXiv:2405.18765, 2024. 1
[16] Xuan Kan, Hejie Cui, Joshua Lukemire, Ying Guo, and Carl
Yang.
Fbnetgen: Task-aware gnn-based fmri analysis via
functional brain network generation. In International confer-
ence on medical imaging with deep learning, pages 618–637.
PMLR, 2022. 2, 7
[17] Xuan Kan, Wei Dai, Hejie Cui, Zilong Zhang, Ying Guo, and
Carl Yang. Brain network transformer. Advances in Neural
Information Processing Systems, 35:25586–25599, 2022. 1,
2, 7
[18] Nicole R Karcher and Deanna M Barch. The abcd study: un-
derstanding the development of risk for mental and physical
health outcomes.
Neuropsychopharmacology, 46(1):131–
142, 2021. 5, 6
[19] Jeremy Kawahara, Colin J Brown, Steven P Miller, Brian G
Booth, Vann Chau, Ruth E Grunau, Jill G Zwicker, and
Ghassan Hamarneh. Brainnetcnn: Convolutional neural net-
works for brain networks; towards predicting neurodevelop-
ment. NeuroImage, 146:1038–1049, 2017. 1, 2, 3, 7
[20] Peter Kim, Junbeom Kwon, Sunghwan Joo, Sangyoon Bae,
Donggyu Lee, Yoonho Jung, Shinjae Yoo, Jiook Cha, and
Taesup Moon. Swift: Swin 4d fmri transformer. Advances
in Neural Information Processing Systems, 36:42015–42037,
2023. 1, 2, 7
[21] Chunyuan Li, Cliff Wong, Sheng Zhang, Naoto Usuyama,
Haotian Liu, Jianwei Yang, Tristan Naumann, Hoifung Poon,
and Jianfeng Gao. Llava-med: Training a large language-
and-vision assistant for biomedicine in one day. Advances
in Neural Information Processing Systems, 36:28541–28564,
2023. 1
[22] Junnan Li, Dongxu Li, Silvio Savarese, and Steven Hoi.
Blip-2:
Bootstrapping language-image pre-training with
frozen image encoders and large language models. In In-
ternational conference on machine learning, pages 19730–
19742. PMLR, 2023. 1
[23] Xiaoxiao Li, Yuan Zhou, Nicha Dvornek, Muhan Zhang,
Siyuan Gao, Juntang Zhuang, Dustin Scheinost, Lawrence H
9


## Page 10

Staib, Pamela Ventola, and James S Duncan.
Braingnn:
Interpretable brain graph neural network for fmri analysis.
Medical Image Analysis, 74:102233, 2021. 1, 2, 7
[24] Aixin Liu, Bei Feng, Bing Xue, Bingxuan Wang, Bochao
Wu, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu
Zhang, Chong Ruan, et al. Deepseek-v3 technical report.
arXiv preprint arXiv:2412.19437, 2024. 5
[25] Fabian Mentzer, David Minnen, Eirikur Agustsson, and
Michael Tschannen. Finite scalar quantization: Vq-vae made
simple. arXiv preprint arXiv:2309.15505, 2023. 2, 6
[26] Karla L Miller, Fidel Alfaro-Almagro, Neal K Bangerter,
David L Thomas, Essa Yacoub, Junqian Xu, Andreas J
Bartsch, Saad Jbabdi, Stamatios N Sotiropoulos, Jesper LR
Andersson, et al. Multimodal population brain imaging in
the uk biobank prospective epidemiological study. Nature
neuroscience, 19(11):1523–1536, 2016. 5, 6
[27] Ronald Carl Petersen, Paul S Aisen, Laurel A Beckett,
Michael C Donohue, Anthony Collins Gamst, Danielle J
Harvey, CR Jack Jr, William J Jagust, Leslie M Shaw,
Arthur W Toga, et al.
Alzheimer’s disease neuroimaging
initiative (adni) clinical characterization. Neurology, 74(3):
201–209, 2010. 6
[28] Weikang Qiu, Zheng Huang, Haoyu Hu, Aosong Feng, Yu-
jun Yan, and Rex Ying. Mindllm: A subject-agnostic and
versatile model for fmri-to-text decoding.
arXiv preprint
arXiv:2502.15786, 2025. 2
[29] Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario
Amodei, Ilya Sutskever, et al. Language models are unsu-
pervised multitask learners. OpenAI blog, 1(8):9, 2019. 6
[30] Alexander Schaefer, Ru Kong, Evan M Gordon, Timothy O
Laumann, Xi-Nian Zuo, Avram J Holmes, Simon B Eick-
hoff, and BT Thomas Yeo. Local-global parcellation of the
human cerebral cortex from intrinsic functional connectivity
mri. Cerebral cortex, 28(9):3095–3114, 2018. 3, 5
[31] Guobin Shen, Dongcheng Zhao, Yiting Dong, Qian Zhang,
and Yi Zeng. Alignment between brains and ai: Evidence for
convergent evolution across modalities, scales and training
trajectories. arXiv preprint arXiv:2507.01966, 2025. 2
[32] Sheng Shen, Shijia Yang, Tianjun Zhang, Bohan Zhai,
Joseph E Gonzalez, Kurt Keutzer, and Trevor Darrell. Mul-
titask vision-language prompt tuning. In Proceedings of the
IEEE/CVF Winter Conference on Applications of Computer
Vision, pages 5656–5667, 2024. 5
[33] Ye Tian, Daniel S Margulies, Michael Breakspear, and An-
drew Zalesky. Topographic organization of the human sub-
cortex unveiled with functional connectivity gradients. Na-
ture neuroscience, 23(11):1421–1432, 2020. 3, 5
[34] Aaron Van Den Oord, Oriol Vinyals, et al. Neural discrete
representation learning. Advances in neural information pro-
cessing systems, 30, 2017. 2, 4, 6
[35] Yuxiang Wei, Yanteng Zhang, Xi Xiao, Tianyang Wang,
Xiao Wang, and Vince D Calhoun.
4d multimodal co-
attention fusion network with latent contrastive alignment
for alzheimer’s diagnosis. arXiv preprint arXiv:2504.16798,
2025. 1, 3
[36] Weihao Xia, Raoul de Charette, Cengiz Oztireli, and Jing-
Hao Xue. Umbrae: Unified multimodal brain decoding. In
European Conference on Computer Vision, pages 242–259.
Springer, 2024. 2
[37] Xi Xiao, Yunbei Zhang, Xingjian Li, Tianyang Wang,
Xiao Wang, Yuxiang Wei, Jihun Hamm, and Min Xu.
Visual instance-aware prompt tuning.
arXiv preprint
arXiv:2507.07796, 2025. 1
[38] Jiaxing Xu, Kai He, Yue Tang, Wei Li, Mengcheng Lan, Xia
Dong, Yiping Ke, and Mengling Feng. Brainprompt: Multi-
level brain prompt enhancement for neurological condition
identification. In International Conference on Medical Im-
age Computing and Computer-Assisted Intervention, pages
172–182. Springer, 2025. 3
[39] Yanwu Yang, Chenfei Ye, Guinan Su, Ziyao Zhang, Zhikai
Chang, Hairui Chen, Piu Chan, Yue Yu, and Ting Ma. Brain-
mass: Advancing brain network analysis for diagnosis with
large-scale self-supervised learning. IEEE transactions on
medical imaging, 43(11):4004–4016, 2024. 7
[40] Xiaohua Zhai, Basil Mustafa, Alexander Kolesnikov, and
Lucas Beyer. Sigmoid loss for language image pre-training.
In Proceedings of the IEEE/CVF international conference on
computer vision, pages 11975–11986, 2023. 4
10


