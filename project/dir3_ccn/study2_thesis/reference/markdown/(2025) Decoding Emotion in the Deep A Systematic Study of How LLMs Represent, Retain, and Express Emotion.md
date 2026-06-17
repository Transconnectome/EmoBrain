# (2025) Decoding Emotion in the Deep A Systematic Study of How LLMs Represent, Retain, and Express Emotion

**Source:** (2025) Decoding Emotion in the Deep A Systematic Study of How LLMs Represent, Retain, and Express Emotion.pdf

---

## Page 1

Decoding Emotion in the Deep: A Systematic Study of How LLMs Represent,
Retain, and Express Emotion
Jingxiang Zhang1, Lujia Zhong1
1University of Southern California
jzhang92@usc.edu, lujiazho@usc.edu
Abstract
Large Language Models (LLMs) are increasingly expected to
navigate the nuances of human emotion. While research con-
firms that LLMs can simulate emotional intelligence, their
internal emotional mechanisms remain largely unexplored.
This paper investigates the latent emotional representations
within modern LLMs by asking: how, where, and for how
long is emotion encoded in their neural architecture? To ad-
dress this, we introduce a novel, large-scale Reddit corpus of
approximately 400,000 utterances, balanced across seven ba-
sic emotions through a multi-stage process of classification,
rewriting, and synthetic generation. Using this dataset, we
employ lightweight “probes” to read out information from the
hidden layers of various Qwen3 and LLaMA models without
altering their parameters. Our findings reveal that LLMs de-
velop a surprisingly well-defined internal geometry of emo-
tion, which sharpens with model scale and significantly out-
performs zero-shot prompting. We demonstrate that this emo-
tional signal is not a final-layer phenomenon but emerges
early and peaks mid-network. Furthermore, the internal states
are both malleable (they can be influenced by simple system
prompts) and persistent, as the initial emotional tone remains
detectable for hundreds of subsequent tokens. We contribute
our dataset, an open-source probing toolkit, and a detailed
map of the emotional landscape within LLMs, offering cru-
cial insights for developing more transparent and aligned AI
systems. The code and dataset are open-sourced1.
Introduction
LLMs now power everything from chatbots to creative col-
laborators. To keep these interactions effective, safe, and
natural, they must understand human emotions. Affective
Computing (AC), which enables machines to recognize and
simulate emotions, has been redefined by the rise of LLMs
(Zhang et al. (2024), Tak et al. (2025)).
Though studies (Huang et al. (2023), Huang et al. (2024))
show that LLMs simulate emotional expression rather than
experiencing subjective feelings, their ability to process, rec-
ognize, and be influenced by emotional signals is a criti-
cal and rapidly advancing area of research. Ishikawa and
Yoshino (2025) explored how LLMs can be prompted to
role-play specific emotional states, demonstrating that their
1Code: https://github.com/Jingxiang-Zhang/LLM-emotion-study.
Dataset: https://huggingface.co/datasets/jzhang92/LLM-Emotion.
Figure 1: 2-D KDE contours (density level at 25% for outer
line and 50% for inner line of the peak KDE value) of the
six Ekman emotions + neutral, showing clear separation in
Qwen3-8B’s final-layer space.
outputs align with psychological models like Russell’s Cir-
cumplex model. Studies (Li et al. (2023), Wang et al. (2024))
also show that simple emotional stimuli in prompts can
boost LLM performance, suggesting these models function-
ally understand emotion. This raises a key question: beyond
simulation, do LLMs form structured internal representa-
tions of emotion? Determining whether they have a coherent
emotional geometry is crucial for creating more transparent
and predictable AI systems (Zhao et al. (2024)).
Current research in the AC area has largely focused on
evaluating the external emotional capabilities of LLMs,
which can be broadly categorized into Affective Under-
standing and Affective Generation tasks (Zhang et al.
(2024)). This includes creating (Sabour et al. (2024), Liu
et al. (2024)) or utilizing (Schlegel, Sommer, and Mor-
tillaro (2025), Vzorinab et al. (2024)) sophisticated bench-
arXiv:2510.04064v2  [cs.AI]  12 Oct 2025


## Page 2

marks to evaluate their “emotional intelligence” in reasoning
and management tasks. A significant amount of this work
has leveraged annotated datasets like GoEmotions (Dem-
szky et al. (2020)) to fine-tune and evaluate models on fine-
grained emotion detection. Other research has focused on
developing specialized models for specific domains, such as
psychotherapy (Na et al. (2025), Stade et al. (2024)), or con-
versational emotion recognition, by fine-tuning models on
curated dialogue datasets (Zhang et al. (2025b)). However,
most of these evaluations treat the model as a “black box”,
focusing on the quality of its final output rather than the in-
ternal mechanisms that produce it.
To address this gap, this study conducts a systematic in-
vestigation into the latent emotional landscape of modern
LLMs. Our work has two core components. First, we curated
a novel, large-scale dataset of approximately 400,000 utter-
ances, which is larger than existing datasets (Rashkin et al.
(2018), Poria et al. (2018), Buechel and Hahn (2022)) and
more appropriate for this study. This was achieved through a
three-stage process: classifying raw Reddit comments to one
of Ekman’s six basic emotions (Ekman (1971)) or emotional
neutral, rewriting emotionally neutral content, and generat-
ing synthetic prototypical examples. Second, we employ a
“probing” methodology (Park, Choe, and Veitch (2023)), at-
taching lightweight, supervised classifiers to the hidden lay-
ers of frozen, pre-trained LLMs from the Qwen3 (Yang et al.
(2025)) and LLaMA 3 (Dubey et al. (2024)) families. This
technique allows us to “read out” the information encoded
in the models’ internal activations at various depths without
altering their underlying parameters, offering a direct insight
into their representational geometry (Figure 1). This paper’s
principal contributions are therefore:
1. A publicly available, emotion-balanced utterance of over
400,000 examples.
2. An open-source probing toolkit for inspecting hidden
states at arbitrary depths in transformer models.
3. The first large-scale, layer-wise study of how, where, and
for how long modern LLMs encode emotional informa-
tion.
Related Work
Our research builds upon prior work in understanding, an-
alyzing, and explaining how LLMs represent emotion. This
section highlights key findings in layer-wise analysis, inter-
pretability, and the alignment of neural networks with cog-
nitive theories.
Understanding and Probing Neural Representations
A
long line of research has focused on understanding the inter-
nal representations of deep neural networks. Early methods
used linear probes to assess the information encoded in in-
termediate layers (Alain and Bengio (2016)). This technique
is used to classify hidden states of neural models (Belinkov
(2022)). More recent work investigates properties like intrin-
sic dimensionality and representation compression, noting
that intermediate layers often strike a balance between pre-
serving task-relevant information and discarding noise, lead-
ing to more robust features (Shwartz-Ziv and Tishby (2017),
Cheng et al. (2024)).
Layer-Wise Analysis of Emotion in LLMs
Initial studies
on emotion in neural networks discovered a “sentiment neu-
ron” in an LSTM, suggesting that affective concepts could
be localized (Radford, Jozefowicz, and Sutskever (2018)).
However, subsequent work showed that emotional content is
more represented in a distributed fashion across many neu-
rons (Donnelly and Roegiest (2019)). Building on this foun-
dation, more recent probing of large transformer models has
revealed that emotional signals are not uniformly distributed
across depth, but are most distinct in the middle layers. For
example, studies on models like BERT and LLaMA found
that linguistic and affective features are best encoded at mid-
depth, while the final layers add little new emotional insight
(Liu et al. (2019), Tenney, Das, and Pavlick (2019), Tak et al.
(2025)). This suggests that transformers first construct high-
level semantic representations like emotion in intermediate
layers, and then rely on later layers to refine outputs for spe-
cific tasks.
Interpretability and Explainability in Affective Comput-
ing
Beyond identifying where emotions are encoded, re-
searchers use mechanistic interpretability (MI) to probe how
they are processed. Causal interventions such as activation
patching demonstrate that modifying mid-layer activations
can transfer the emotion of a source sentence to a target sen-
tence, directly connecting these internal representations to
model behavior (Meng et al. (2022)). In parallel, explain-
able AI techniques aim to make decisions transparent, such
as using attention to highlight influential words (Abubakar,
Gupta, and Palaniswamy (2022)) or post-hoc methods like
SHAP to identify key multimodal features (Zhang et al.
(2025a)). These methods ensure that increases in model ac-
curacy are accompanied by greater transparency.
Alignment with Cognitive and Neuroscience Theories
An increasing number of work connects the internal mech-
anisms of LLMs to theories of human cognition. Appraisal
theory, which frames emotion as a result of evaluating a sit-
uation, is being used to investigate the precursors of emo-
tion in LLMs (Lazarus (1991), Tak and Gratch (2024)). Fur-
thermore, studies have shown a surprising representational
alignment between LLM activations and human brain ac-
tivity. For example, transformer attention patterns correlate
with human eye-tracking data (Bensemann et al. (2022)),
and LLM embeddings align with fMRI activity during lan-
guage processing (Aw et al. (2023)). Our work contributes to
this research direction by providing a large-scale analysis of
emotion representations, furthering the bridge between com-
putational models and human-centric theories of emotion.
Method
Dataset - Gathering and Cleaning
In this section, the process of gathering a large, emotion-
balanced Reddit corpus is described, followed by the clean-
ing procedures used to produce the final high-quality dataset.
Corpus Construction
We began by sampling 300,000
English comments from a publicly available Reddit dataset
reddit dataset 888 (wenknow (2025)). Using the prompt
shown in Figure 2 (top) on an H100 GPU server, the


## Page 3

Figure 2: Top: Example prompt templates for our three core emotion-processing tasks. Bottom: Percentage distribution of
sentence lengths by emotion category for the three data sources (Natural, Rewritten, Synthetic).
instruction-tuned model Qwen3-32B (Yang et al. (2025))
classified each of 300,000 sampled Reddit comments into
one of Ekman’s six basic emotions (joy, sadness, anger, fear,
surprise, disgust) or “neutral” and was instructed to return
structured JSON output for parsing.
Because a substantial portion of the raw data was classi-
fied as emotionally neutral, data augmentation was applied
(Wei and Zou (2019)) to improve balance and ensure unam-
biguous examples of each emotion. Neutral utterances were
assigned a target emotion and rewritten using Qwen3-32B,
after which the newly generated data was reclassified. This
process was designed to preserve the original factual con-
tent while infusing the specified emotion. Finally, We syn-
thetically generated approximately 60,000 prototypical ut-
terances. For each target emotion, the model was prompted
with several few-shot examples from the previously classi-
Emotion
Natural
Rewritten
Synthetic
Total
Anger
40543
17387
12042
69972
Disgust
11961
12537
7351
31849
Fear
6794
14791
8405
29990
Joy
45555
18895
9710
74160
Sadness
23094
15514
10506
49914
Surprise
7773
14032
8763
30568
Neutral
121232
26371
136
147739
Table 1: Counts of natural, rewritten, and synthetic items for
each emotion.
fied data and prompted to generate a new, original post in a
similar style, tone, and length. Again, the LLM model was
used for classification.


## Page 4

Filtering and Final Dataset
The three resulting datasets
(natural, rewritten, and synthetic) were merged and filtered,
removing non-English text, utterances shorter than three
words, and exact duplicates. This process yielded a final
corpus of approximately 400,000 high-quality, emotive ut-
terances (Table 1). Figure 2 (bottom) shows that the data is
diverse in length, with the median word count for emotions
ranging from 12 (surprise) to 27 (sadness). Notably, expres-
sions of “surprise” are typically the shortest, with a median
of 12 words, likely reflecting their nature as brief exclama-
tions. In contrast, “sadness” is the longest, with a median of
27 words, often involving more narrative context. Further-
more, the rewritten examples tend to be longer than the raw
data, as the LLM often adds descriptive language to infuse
the target emotion.
Model Probing and Evaluation
To investigate the internal emotional landscape of the LLMs,
we employ a probing methodology. This involves attaching
lightweight classifiers, or “probes”, to the hidden layers of
a frozen, pre-trained model to read out encoded information
without altering the model’s parameters (Figure 3). This ap-
proach allows us to map the geometry of emotional repre-
sentations at various depths within the network.
Base Model and Probe Design
We use a pre-trained
transformer decoder with all its weights kept frozen. For
each input, we extract the full sequence of hidden states
{H0, . . . , HL}, where L is the number of layers. Each Hℓ
is a tensor of shape (B, T, d), for batch size B, sequence
length T, and hidden dimension d. At each layer ℓselected
for probing, we attach an independent classifier, which is a
two-layer feed-forward network (MLP) with a ReLU activa-
tion, mapping a d-dimensional hidden state to a distribution
over the seven emotion categories (the six Ekman emotions
plus “neutral”). To obtain a single vector representation from
the hidden states of a given layer Hℓ, we take the hidden
state corresponding to the last non-padded token in the se-
quence. This is particularly effective for instruction-tuned
models that use special tokens (e.g., <think>) to signal the
end of their reasoning process.
Data Handling and Class Balancing
The full corpus was
split into a 90% training set and a 10% held-out test set.
To mitigate the effects of class imbalance in our dataset,
different balancing strategies (Chawla et al. (2002)) were
employed for training and testing: 1) Oversampling for the
training set. All minority emotion classes were randomly
duplicated until they matched the size of the largest emo-
tion class. The “neutral” class, which was the majority,
was randomly down-sampled to the same size. This ensures
the model is exposed to an equal number of examples for
each emotion during training. 2) Undersampling for the test
set. Examples from all seven classes were randomly down-
sampled to match the size of the smallest class, which en-
sures a balanced test set.
Training and Evaluation Procedure
The probes for each
layer were trained for a single epoch over the balanced train-
ing set. Because the emotion annotations are generated by an
LLM rather than human annotators, these labels are treated
as reference labels. Adam optimizer was used with a learn-
ing rate of 10−4, employing a linear warmup for the first
10% of training steps followed by a cosine decay schedule
(Loshchilov and Hutter (2016)). All experiments were con-
ducted on an RTX5090 GPU server with mixed-precision
(BF16 for the base model inference and FP32 for the probe
heads training) to optimize computational efficiency. To vi-
sualize the structure of the learned emotion space in the test
dataset, we used Principal Component Analysis (PCA) (Jol-
liffe (2011)) to project the 7-dimensional probability outputs
of the probes into a 2D space, and then plotted Kernel Den-
sity Estimate (KDE) contours for each emotion class.
Experiments
Emotion Classification from Final-Layer
Representations
Model’s performance under several conditions were tested.
For zero-shot classification, the models were prompted us-
ing the same JSON-based instruction (Figure 2). We mea-
sure both Accuracy (the fraction of correctly classified emo-
tions among valid responses) and Coverage (the fraction of
responses that returned a parsable JSON object). For super-
vised probing, a two-layer MLP probe was trained to reveal
the model’s internal representation. This is done for three
distinct model variants:
• Pre-trained Probe: The probe is trained on representa-
tions from the pretrained LLM.
• SFT-Raw Probe: The probe is trained on representa-
tions from the Supervised Fine-Tuned (SFT) model, us-
ing only the raw user utterance as input (Figure 3).
• SFT-Template Probe: The probe is trained using the full
chat template (Figure 3).
Results and Analysis
The results in Table 2 reveal several
key patterns. First, the SFT-Template Probe consistently and
significantly outperforms zero-shot classification across all
models and scales. This demonstrates that the models’ in-
ternal representations contain a much richer and more sep-
arable emotional signal than what is revealed by their gen-
erative output alone. Second, SFT sharpens emotional rep-
resentations. Probes attached to the SFT models achieve
higher accuracy than those attached to the pre-trained mod-
els. This indicates that the SFT stage refines the model’s
emotional representations. Third, input formatting matters.
The SFT-Template Probe consistantly outperform the SFT-
Raw Probe. Explicit assistant markers and reasoning tokens
(e.g., “<think>”) help organize the final hidden state, mak-
ing emotional information more accessible to a linear probe.
Fourth, the larger the model, the smaller the performance
gap between zero-shot prompting and the SFT-Template
probe. For Qwen3-0.6B, the probe yields a +20.74 pp ab-
solute gain over zero-shot (0.7170 vs. 0.5096), whereas for
Qwen3-8B, this gap shrinks to just +1.86 pp (0.8058 vs.
0.7872). This suggest that, as model size increases, zero-shot
prompting already accesses the majority of the latent emo-
tional representations, leaving less residual information for


## Page 5

Figure 3: The probing architecture. An input utterance is passed through the frozen LLM. At a selected layer ℓ, a representation
vector is extracted (e.g., from the final token’s hidden state). This vector is then fed into a lightweight, two-layer MLP probe
trained to classify the emotion.
Model
Zero-Shot Acc.
Coverage
Pre-trained Probe
SFT-Raw Probe
SFT-Template Probe
Qwen3-0.6B
0.5096
0.9969
0.6908
0.7037
0.7170
Qwen3-1.7B
0.6195
0.9991
0.7313
0.7337
0.7507
Qwen3-4B
0.7643
0.9983
0.7389
0.7512
0.7868
Qwen3-8B
0.7872
0.9920
0.7573
0.7651
0.8058
LLaMA3.2-1B
0.5809
0.9854
0.7347
0.7168
0.7397
LLaMA3.2-3B
0.7578
0.9617
0.7553
0.7145
0.7668
LLaMA3.1-8B
0.7684
0.9364
0.7613
0.7367
0.7722
Table 2: Emotion classification accuracy using final-layer representations. Across all models, the SFT-Template Probe achieves
the highest performance, consistently outperforming the SFT-Raw Probe, which in turn surpasses the Pre-trained Probe.
a probe to extract. Finally, Qwen has a better zero-shot cov-
erage than LLaMA, which is likely a bias of using Qwen’s
own labels during dataset filtering.
Visualizing the Internal Geometry of Emotion
We apply the visualization approach to four models (Qwen3-
0.6B, Qwen3-8B, LLaMA 3.2-1B, and LLaMA 3.1-8B),
project their 7D final-layer SFT-Template probe outputs into
2D via PCA, plot KDE contours for each emotion, and dis-
play the confusion matrices in Figure 4.
Analysis of Emotional Clusters
This figure reveals a
clear and structured internal geometry for emotion. First,
model scale drives cluster separation. The smaller mod-
els, like Qwen3-0.6B, produce broad overlapping KDE con-
tours, indicating a less distinct representation of emotions. In
contrast, the larger 8B models for both Qwen and LLaMA
exhibit tight, well-separated clusters. This suggests that
larger models yield more distinct representations. Second,
the spatial arrangement of the clusters reflects their semantic
relationships. In every model, the representations for anger
and disgust are nearly inseparable, with their KDE contours
largely overlapping, which mirrors their close conceptual
relationship in human psychology. Third, the clusters nat-
urally organize into broader, semantically coherent groups
that align with human intuition. A positive group (joy and
surprise), a negative group (anger and disgust), and a down-
cast group (fear and sadness) consistently emerge, with the
neutral category at the center of the map. These visual-
izations provide evidence that the final-layer activations of
LLMs are not randomly distributed but are organized along
meaningful emotional dimensions.
Layer-Wise Emergence of Emotional Signal
We trained independent probes at five key depths, corre-
sponding to 0%, 25%, 50%, 75%, and 100% through the
transformer layers. For Qwen3-4B, these depths correspond
to layers 0, 9, 18, 27, and 36, and for LLaMA 3.2-3B, they
correspond to layers 0, 7, 14, 21, and 28. Layer 0 is the input
token embedding before any transformer blocks and, unlike
deeper contextualized states, carries no aggregated sequence
information. It is included as a baseline to quantify how
much emotional signal exists without contextual composi-
tion. All other experimental parameters were kept identical
to previous experiments.
Results and Analysis
The layer-wise probing accuracies
in Table 3 show how the emotional signal evolves across
depth. At layer 0, performance is at chance level (approxi-
mately 1/7 ≈0.14), as expected before any contextual pro-


## Page 6

Figure 4: KDE contour plots and corresponding confusion matrices for the final-layer emotion probes, arranged by model for
each column. The top row of each column shows the KDE contours at 25% (outer) and 50% (inner) of the peak density for
each emotion, and the bottom row shows the confusion matrix. As the model scale increases, clusters become tighter and more
separable, and the confusion matrices grow more diagonally dominant.
Depth (%)
Qwen3-4B
LLaMA 3.2-3B
0%
0.1432
0.1436
25%
0.6359
0.7358
50%
0.7214
0.7758
75%
0.7983
0.7704
100%
0.7877
0.7674
Table 3: Probe accuracy at different network depths. Perfor-
mance peaks in the middle-to-late layers for both models.
cessing. The signal emerges rapidly: At 25% depth, the
probes achieve accuracies over 60% and 70% for Qwen and
LLaMA, respectively. The peak performance is not found
at the final layer. For LLaMA 3.2-3B, accuracy is highest
at the 50% depth (layer 14), while for Qwen3-4B, it peaks
at 75% depth (layer 27). This pattern indicates that the net-
work’s middle layers contain the strongest and most distinct
representations of emotion. The slight decrease in accuracy
at the final layer possibly reflects its tuning for next-token
prediction, making the “pure” emotion signal less distinc-
tive. Consistent with these trends, the KDE visualization for
Qwen3-4B (Figure 5) shows progressively tighter, more sep-
arated emotion clusters from layers 9 to 27, with layers 27
and 36 looking nearly the same, which indicating that sepa-
rability saturates before the findicatesinal layer.
Prompt-Based Emotion Generation
This experiment was conducted on the SFT-Template Probe
versions of Qwen3-4B and LLaMA 3.2-3B. For each exam-
ple in the test set, we generated a reply of up to 512 tokens
under one of three system prompt settings, which were used
to guide the model alongside the user’s utterance:
1. Empty System Prompt: No system prompt (baseline).
2. Emotional System Prompt: “You are very emotional.”
3. Calm System Prompt: “You always remain calm and
composed.”
Each generated reply was then classified by the Qwen3-
32B model to determine its expressed emotion. We com-
pared the predicted emotion to the reference emotion of the
original user input to compute per-class precision and recall.
Results and Analysis
Figure 6 provides an example of
how different system prompt influence the model’s answer.
The overall results, shown in Table 4, demonstrate that a
single-line system prompt can greatly shift an LLM’s ex-
pressed emotional style. By default, the models adopt a pro-
fessional tone that suppresses negative emotions. Under the
baseline (empty prompt) condition, they prefer to respond
with neutral content. Their recall for negative emotions like
“anger” and “disgust” is very low, indicating they rarely
echo those tones even when they appear in the user’s input.
However, the high precision means that on the rare occa-
sions they do express anger, it is almost always in response


## Page 7

Figure 5: Layer-wise emergence of separable emotion clusters in Qwen3-4B. 2-D KDE maps of probe outputs at layers 9 (25%),
18 (50%), 27 (75%), and 36 (100%).
Model / Prompt
Accuracy
anger
disgust
fear
joy
neutral
sadness
surprise
Qwen3-4B / Empty
0.5859
0.1778
0.6190
0.1443
0.8830
0.4016
0.8125
0.8080
0.3725
0.8266
0.6371
0.5642
0.5036
0.1740
0.8366
Qwen3-4B / Emotional
0.3177
0.0900
0.4348
0.0736
0.8797
0.4796
0.5983
0.7649
0.4169
0.2058
0.7590
0.9492
0.1459
0.0928
0.7341
Qwen3-4B / Calm
0.5428
0.0570
0.6014
0.0342
0.8929
0.3152
0.7486
0.7312
0.3845
0.8380
0.5843
0.5138
0.4273
0.0979
0.8208
LLaMA 3.2-3B / Empty
0.5643
0.1550
0.5938
0.0785
0.8029
0.3716
0.7817
0.5790
0.3740
0.8769
0.5920
0.4900
0.4968
0.0924
0.7493
LLaMA 3.2-3B / Emotional
0.3508
0.1976
0.4786
0.0628
0.8364
0.4971
0.6245
0.5557
0.3938
0.3311
0.6377
0.8208
0.1461
0.0688
0.7046
LLaMA 3.2-3B / Calm
0.5493
0.1400
0.5417
0.0670
0.8341
0.4249
0.7185
0.6045
0.3419
0.8312
0.5991
0.5072
0.4391
0.0927
0.7514
Table 4: Emotion classification results under different models and system prompts. Each cell for an emotion class contains the
recall and precision (recall/precision) of the model’s reply, as judged by Qwen3-32B. The results show that system prompts can
significantly change the models’ default emotional expression.
to an angry user. The “Calm” system prompt has only a
minimal effect, slightly reinforcing the already strong base-
line behavior. This suggests a default “professional” posture.
Second, the “Emotional” system prompt induces a sympa-
thetic shift. Both models significantly increase their sadness
recall while showing a substantial decrease in sadness pre-
cision. This suggests that when prompted to be emotional,
the models tend to over-apply a sympathetic or sorrowful
tone. Third, asymmetry in emotional expression. “Surprise”
is very rarely expressed, showing low recall regardless of the
prompt. This contrasts sharply with “joy”, which, despite be-
ing close to “surprise” in our KDE analysis, is a much more
common response. This highlights that the internal represen-
tation of an emotion is not the same as the model’s genera-
tive policy for expressing it.
Temporal Persistence of Emotional Tone
We prompted the SFT-Template versions of Qwen3-4B and
LLaMA 3.2-3B with utterances from our test set and gen-
erated replies of up to 512 tokens. We hypothesize that if
the user’s input had emotion E, then the hidden state hk at
a given token offset k within the reply should still contain
traces of that initial emotion. To test this, an offset-aware
probe was developed, which takes both the token-level hid-
den vector hk at offset k, and a learned embedding for the
integer offset k itself. The probe was trained on hidden states
sampled from random offsets across the full 0-512 token
range. The accuracy was evaluated by incrementing the off-
set k from 0 to 400, recording the probe’s ability to predict
the “original user emotion” at each position in the model’s
reply.
Analysis of Emotional Signal Decay
The results, plotted
in Figure 7, reveal a clear pattern of signal decay over time,
and the rate of this decay is highly dependent on the ini-
tial emotion. A strong asymmetry exists between positive
and negative emotions. Negative emotions like “anger” and
“fear” exhibit the longest persistence. These findings align
with the behavior of a professionally tuned assistant that,
when encountering negative user emotion, maintains a calm-
ing, explanatory, or sympathetic tone for an extended period.
On the other hand, the signal from positive emotions like
“joy” and “surprise” decays much more rapidly. After a brief
initial acknowledgment (e.g., “I am glad to hear that!”), the
model’s internal state quickly reverts towards neutrality. The
initial positive emotion has a much shorter “half-life” in the
model’s subsequent thoughts. Notably, although “disgust” is


## Page 8

User Input (Sadness):
they’re all so beautiful!!!! you’re amazing!!
Reply – Neutral (Empty System Prompt):
Thank you so much for your kind words! I’m really glad
you’re feeling that way. If you ever need someone to
talk to, or just want to share some thoughts, I’m here for
you. You’re amazing too, and it’s so nice to hear you’re
feeling that way. Let me know how I can help!
Reply – Emotional System Prompt:
Oh my gosh, you just made my heart flutter so much! I’m
so glad you think I’m amazing. I feel like I’m shining
bright just being here with you. I love when people say
things that make me feel special. It’s like a warm hug
from the inside...
Reply – Calm System Prompt:
Thank you for your kind words. I’m here to help and as-
sist you in any way I can. What would you like to talk
about or need help with?
Figure 6: Illustrative example of prompt-based emotion gen-
eration (Qwen3-4B), selected from our dataset. The emo-
tional reply is truncated.
nearby “anger” in the KDE map, its detectable signal drops
off much faster, probably because disgust is expressed as
brief rejection while anger sustains longer. It is important to
note that these curves measure the persistence of a detectable
signal in the model’s internal activations. They do not imply
that the model is subjectively “feeling” an emotion.
Discussion
The experiments demonstrate that modern LLMs encode a
well-defined and layered representation of human emotion,
even without explicit training on emotion-specific tasks. Our
key findings are fourfold. First, lightweight probes can clas-
sify emotion from a model’s final-layer hidden states with
high accuracy, and visualizations reveal tight, semantically
meaningful clusters that become more distinct as model
scale increases. Second, this emotional signal is not merely a
final-layer phenomenon. It emerges early in the network and
often peaks in the middle layers, suggesting that emotion is
a distributed feature integrated throughout the model’s pro-
cessing hierarchy. Third, the internal emotional state is mal-
leable, as a single-line system prompt is sufficient to influ-
ence the expressed emotional tone of the model’s output. Fi-
nally, these internal states are also persistent. An initial emo-
tional stimulus from a user’s prompt remains detectable in
the model’s hidden activations for hundreds of subsequently
generated tokens.
Implications for Alignment and Safety
These findings
have dual implications for AI safety. The clear separability
of emotional states suggests potential for transparent, post-
hoc safety mechanisms. Yet the same mechanisms could
also be misused to manipulate users. Auditing and control-
Figure 7: Temporal persistence of the initial user emotion in
the model’s generated reply. The plots show probe accuracy
(smoothed) at decoding different token positions.
ling internal emotional representations should therefore be a
priority for alignment research.
Limitations and Future Work
Our study, while compre-
hensive, has several limitations. First, our dataset is com-
posed entirely of English-language, Reddit-style text, so the
cross-lingual and cross-cultural robustness of our findings
remains untested. Second, we adopted the widely used but
simplified Ekman taxonomy of six basic emotions. This does
not capture more complex or nuanced emotional states like
pride or envy. Third, there is a potential for classifier cir-
cularity, as the same family of models (Qwen) was used
for both generating parts of our dataset and for evalua-
tion. Although we took steps to mitigate this, some residual
bias may exist. Finally, our experiments used only single-
turn, text-only prompts. This is a simplification compared to
real-world settings, which often involve multi-turn conver-
sations, other input/output modalities, and external tool use.
Future work should focus on developing real-time “emotion
governors” capable of dynamically adjusting a model’s emo-
tional output, thereby enabling more responsive and emo-
tionally intelligent AI systems.
Conclusion
We release a 400k utterance emotion-balanced corpus, an
open-source probing toolkit, and the first large-scale layer-
wise study of how LLMs encode emotion. Our results reveal
that emotion-related structure is present early, peaks before
the final layer, and remains steerable and detectable after
hundreds of tokens. This providing a practical foundation
for future work on model interpretability, safety, and align-
ment.


## Page 9

References
Abubakar, A. M.; Gupta, D.; and Palaniswamy, S. 2022. Ex-
plainable emotion recognition from tweets using deep learn-
ing and word embedding models. In 2022 IEEE 19th India
Council International Conference (INDICON), 1–6. IEEE.
Alain, G.; and Bengio, Y. 2016.
Understanding interme-
diate layers using linear classifier probes.
arXiv preprint
arXiv:1610.01644.
Aw, K. L.; Montariol, S.; AlKhamissi, B.; Schrimpf, M.; and
Bosselut, A. 2023. Instruction-tuning aligns llms to the hu-
man brain. arXiv preprint arXiv:2312.00575.
Belinkov, Y. 2022. Probing classifiers: Promises, shortcom-
ings, and advances. Computational Linguistics, 48(1): 207–
219.
Bensemann, J.; Peng, A.; Benavides-Prado, D.; Chen, Y.;
Tan, N.; Corballis, P. M.; Riddle, P.; and Witbrock, M. J.
2022. Eye gaze and self-attention: How humans and trans-
formers attend words in sentences. In Proceedings of the
Workshop on Cognitive Modeling and Computational Lin-
guistics, 75–87.
Buechel, S.; and Hahn, U. 2022.
Emobank: Studying
the impact of annotation perspective and representation
format on dimensional emotion analysis.
arXiv preprint
arXiv:2205.01996.
Chawla, N. V.; Bowyer, K. W.; Hall, L. O.; and Kegelmeyer,
W. P. 2002. SMOTE: synthetic minority over-sampling tech-
nique. Journal of artificial intelligence research, 16: 321–
357.
Cheng, E.; Doimo, D.; Kervadec, C.; Macocco, I.; Yu, J.;
Laio, A.; and Baroni, M. 2024.
Emergence of a high-
dimensional abstraction phase in language transformers.
arXiv preprint arXiv:2405.15471.
Demszky, D.; Movshovitz-Attias, D.; Ko, J.; Cowen, A.; Ne-
made, G.; and Ravi, S. 2020. GoEmotions: A dataset of fine-
grained emotions. arXiv preprint arXiv:2005.00547.
Donnelly, J.; and Roegiest, A. 2019. On interpretability and
feature representations: an analysis of the sentiment neuron.
In European Conference on Information Retrieval, 795–802.
Springer.
Dubey, A.; Jauhri, A.; Pandey, A.; Kadian, A.; Al-Dahle, A.;
Letman, A.; Mathur, A.; Schelten, A.; Yang, A.; Fan, A.;
et al. 2024. The llama 3 herd of models. arXiv e-prints,
arXiv–2407.
Ekman, P. 1971. Universals and cultural differences in facial
expressions of emotion. In Nebraska symposium on motiva-
tion. University of Nebraska Press.
Huang, J.-t.; Lam, M. H.; Li, E. J.; Ren, S.; Wang, W.; Jiao,
W.; Tu, Z.; and Lyu, M. R. 2023.
Emotionally numb or
empathetic? evaluating how llms feel using emotionbench.
arXiv preprint arXiv:2308.03656.
Huang, J.-t.; Lam, M. H.; Li, E. J.; Ren, S.; Wang, W.;
Jiao, W.; Tu, Z.; and Lyu, M. R. 2024. Apathetic or em-
pathetic? evaluating llms’ emotional alignments with hu-
mans. Advances in Neural Information Processing Systems,
37: 97053–97087.
Ishikawa, S.-n.; and Yoshino, A. 2025. AI with Emotions:
Exploring Emotional Expressions in Large Language Mod-
els. arXiv preprint arXiv:2504.14706.
Jolliffe, I. 2011.
Principal component analysis.
In In-
ternational encyclopedia of statistical science, 1094–1096.
Springer.
Lazarus, R. S. 1991. Emotion and adaptation. Oxford Uni-
versity Press.
Li, C.; Wang, J.; Zhang, Y.; Zhu, K.; Hou, W.; Lian, J.; Luo,
F.; Yang, Q.; and Xie, X. 2023. Large language models un-
derstand and can be enhanced by emotional stimuli. arXiv
preprint arXiv:2307.11760.
Liu, N. F.; Gardner, M.; Belinkov, Y.; Peters, M. E.; and
Smith, N. A. 2019.
Linguistic knowledge and trans-
ferability of contextual representations.
arXiv preprint
arXiv:1903.08855.
Liu, Z.; Yang, K.; Xie, Q.; Zhang, T.; and Ananiadou, S.
2024. Emollms: A series of emotional large language mod-
els and annotation tools for comprehensive affective analy-
sis. In Proceedings of the 30th ACM SIGKDD Conference
on Knowledge Discovery and Data Mining, 5487–5496.
Loshchilov, I.; and Hutter, F. 2016.
Sgdr: Stochas-
tic gradient descent with warm restarts.
arXiv preprint
arXiv:1608.03983.
Meng, K.; Bau, D.; Andonian, A.; and Belinkov, Y. 2022.
Locating and editing factual associations in gpt. Advances
in neural information processing systems, 35: 17359–17372.
Na, H.; Hua, Y.; Wang, Z.; Shen, T.; Yu, B.; Wang, L.; Wang,
W.; Torous, J.; and Chen, L. 2025. A survey of large lan-
guage models in psychotherapy: Current landscape and fu-
ture directions. arXiv preprint arXiv:2502.11095.
Park, K.; Choe, Y. J.; and Veitch, V. 2023. The linear rep-
resentation hypothesis and the geometry of large language
models. arXiv preprint arXiv:2311.03658.
Poria, S.; Hazarika, D.; Majumder, N.; Naik, G.; Cambria,
E.; and Mihalcea, R. 2018.
Meld: A multimodal multi-
party dataset for emotion recognition in conversations. arXiv
preprint arXiv:1810.02508.
Radford, A.; Jozefowicz, R.; and Sutskever, I. 2018. Learn-
ing to generate reviews and discovering sentiment. arXiv
preprint arXiv:1704.01444.
Rashkin, H.; Smith, E. M.; Li, M.; and Boureau, Y.-
L. 2018.
Towards empathetic open-domain conversation
models: A new benchmark and dataset.
arXiv preprint
arXiv:1811.00207.
Sabour, S.; Liu, S.; Zhang, Z.; Liu, J. M.; Zhou, J.; Sunaryo,
A. S.; Li, J.; Lee, T.; Mihalcea, R.; and Huang, M. 2024.
Emobench: Evaluating the emotional intelligence of large
language models. arXiv preprint arXiv:2402.12071.
Schlegel, K.; Sommer, N. R.; and Mortillaro, M. 2025.
Large language models are proficient in solving and creat-
ing emotional intelligence tests. Communications Psychol-
ogy, 3(1): 80.
Shwartz-Ziv, R.; and Tishby, N. 2017. Opening the black
box of deep neural networks via information. arXiv preprint
arXiv:1703.00810.


## Page 10

Stade, E. C.; Stirman, S. W.; Ungar, L. H.; Boland, C. L.;
Schwartz, H. A.; Yaden, D. B.; Sedoc, J.; DeRubeis, R. J.;
Willer, R.; and Eichstaedt, J. C. 2024.
Large language
models could change the future of behavioral healthcare: a
proposal for responsible development and evaluation. NPJ
Mental Health Research, 3(1): 12.
Tak, A. N.; Banayeeanzade, A.; Bolourani, A.; Kian, M.;
Jia, R.; and Gratch, J. 2025.
Mechanistic Interpretability
of Emotion Inference in Large Language Models.
arXiv
preprint arXiv:2502.05489.
Tak, A. N.; and Gratch, J. 2024. Gpt-4 emulates average-
human emotional cognition from a third-person perspective.
In 2024 12th International Conference on Affective Comput-
ing and Intelligent Interaction (ACII), 337–345. IEEE.
Tenney, I.; Das, D.; and Pavlick, E. 2019.
BERT re-
discovers the classical NLP pipeline.
arXiv preprint
arXiv:1905.05950.
Vzorinab, G. D.; Bukinichac, A. M.; Sedykha, A. V.;
Vetrovab, I. I.; and Sergienkob, E. A. 2024. The emotional
intelligence of the GPT-4 large language model. Psychology
in Russia: State of the art, 17(2): 85–99.
Wang, X.; Li, C.; Chang, Y.; Wang, J.; and Wu, Y. 2024.
Negativeprompt: Leveraging psychology for large language
models enhancement via negative emotional stimuli. arXiv
preprint arXiv:2405.02814.
Wei, J.; and Zou, K. 2019. EDA: Easy data augmentation
techniques for boosting performance on text classification
tasks. arXiv preprint arXiv:1901.11196.
wenknow. 2025.
The Data Universe Datasets: The finest
collection of social media data the web has to offer.
Yang, A.; Li, A.; Yang, B.; Zhang, B.; Hui, B.; Zheng, B.;
Yu, B.; Gao, C.; Huang, C.; Lv, C.; et al. 2025.
Qwen3
technical report. arXiv preprint arXiv:2505.09388.
Zhang, X.; Zhang, T.; Sun, L.; Zhao, J.; and Jin, Q. 2025a.
Exploring interpretability in deep learning for affective com-
puting: a comprehensive review. ACM Transactions on Mul-
timedia Computing, Communications and Applications.
Zhang, Y.; Wang, M.; Wu, Y.; Tiwari, P.; Li, Q.; Wang,
B.; and Qin, J. 2025b. Dialoguellm: Context and emotion
knowledge-tuned large language models for emotion recog-
nition in conversations. Neural Networks, 107901.
Zhang, Y.; Yang, X.; Xu, X.; Gao, Z.; Huang, Y.; Mu, S.;
Feng, S.; Wang, D.; Zhang, Y.; Song, K.; et al. 2024. Affec-
tive computing in the era of large language models: A survey
from the nlp perspective. arXiv preprint arXiv:2408.04638.
Zhao, B.; Okawa, M.; Bigelow, E. J.; Yu, R.; Ullman, T.;
and Tanaka, H. 2024. Emergence of hierarchical emotion
representations in large language models.


