# *** (2025) Bridging the behavior-neural gap- A multimodal AI reveals the brain's geometry of emotion more accurately than human self-reports

**Source:** *** (2025) Bridging the behavior-neural gap- A multimodal AI reveals the brain's geometry of emotion more accurately than human self-reports.pdf

---

## Page 1

Bridging the behavior-neural gap: A multimodal AI
reveals the brain’s geometry of emotion more
accurately than human self-reports
Changde Du1,3,†, Yizhuo Lu1,2,†, Zhongyu Huang1,3,†, Yi Sun1,3, Zisen Zhou4, Shaozheng
Qin4, and Huiguang He1,2,3,*
1State Key Laboratory of Brain Cognition and Brain-inspired Intelligence Technology, Institute of Automation,
Chinese Academy of Sciences, Beijing, China
2School of Future Technology, University of Chinese Academy of Sciences, Beijing, China
3School of Artificial Intelligence, University of Chinese Academy of Sciences, Beijing, China
4State Key Laboratory of Cognitive Neuroscience and Learning, Beijing Normal University, Beijing, China
†These authors contributed equally.
*corresponding author: Huiguang He (huiguang.he@ia.ac.cn)
ABSTRACT
The ability to represent emotion plays a significant role in human cognition and social interaction, yet the high-dimensional
geometry of this affective space and its neural underpinnings remain debated. A key challenge, the ‘behavior-neural gap,’
is the limited ability of human self-reports to predict brain activity. Here we test the hypothesis that this gap arises from the
constraints of traditional rating scales and that large-scale similarity judgments can more faithfully capture the brain’s affective
geometry. Using AI models as ‘cognitive agents,’ we collected millions of triplet odd-one-out judgments from a multimodal
large language model (MLLM) and a language-only model (LLM) in response to 2,180 emotionally evocative videos. We found
that the emergent 30-dimensional embeddings from these models are highly interpretable and organize emotion primarily
along categorical lines, yet in a blended fashion that incorporates dimensional properties. Most remarkably, the MLLM’s
representation predicted neural activity in human emotion-processing networks with the highest accuracy, outperforming not
only the LLM but also, counterintuitively, representations derived directly from human behavioral ratings. This result supports
our primary hypothesis and suggests that sensory grounding—learning from rich visual data—is critical for developing a truly
neurally-aligned conceptual framework for emotion. Our findings provide compelling evidence that MLLMs can autonomously
develop rich, neurally-aligned affective representations, offering a powerful paradigm to bridge the gap between subjective
experience and its neural substrates. Project page: ai-emotion.github.io
Introduction
How is emotion encoded in the brain and abstracted into a computable cognitive representation? This question remains a central
puzzle in understanding human intelligence. For decades, the scientific debate on the structure of emotion has been dominated
by two competing views: one posits that emotions are comprised of a set of discrete, universal categories like joy and fear1–4,
while the other contends that they are constructed from a few continuous dimensions, such as valence and arousal5–9. This
long-standing dichotomy, however, may fundamentally overlook the true nature of affective representation—a high-dimensional,
blended geometry that transcends simple categorical or dimensional frameworks10,11. More recent theories, such as the
theory of constructed emotion, posit that emotions are not monolithic entities but are constructed from more fundamental
psychological and neural components in the moment9. This perspective offers a theoretical framework for understanding modern
neuroscientific evidence, which suggests that emotion is not supported by discrete, emotion-specific modules but emerges from
dynamic interactions within large-scale brain networks that implement more fundamental psychological processes12–16. Yet,
despite our growing understanding of this neural complexity17–23, models of emotion built from human self-reports (e.g., rating
scales) show limited power in predicting this neural activity24–29, creating an intractable ‘behavior-neural gap.’
Traditional rating scales, by forcing subjective experience into a fixed set of predefined labels or dimensions30,31, may
inadvertently constrain and distort the very phenomena they seek to measure. Participants may struggle to map their nuanced
feelings onto discrete numerical scales, and the choice of labels itself introduces experimenter bias. An alternative paradigm,
based on large-scale similarity judgments (e.g., millions of triplet odd-one-out choices), circumvents these limitations. By
relying on simple, qualitative decisions, this approach minimizes experimenter priors and allows the underlying representational
structure to emerge organically from the data itself32–34. This leads to a critical, untested hypothesis: the behavior-neural
1
arXiv:2509.24298v1  [cs.HC]  29 Sep 2025


## Page 2

gap in affective science may arise from the constraints and distortions imposed by traditional rating scales. A comprehensive
map of emotion, constructed from millions of similarity judgments, might more faithfully reflect the brain’s native affective
geometry. This hypothesis, however, has remained purely theoretical, as it is practically hard for human participants to complete
behavioral experiments of such a massive scale.
Could we, then, find a valid agent for human emotional judgment? In recent years, large language models (LLMs) have
demonstrated impressive, often human-level, performance on a wide range of complex cognitive tasks35–40. Crucially, recent
studies have already confirmed their considerable sensitivity to affective content41–48. This capability is understood to arise
not from phenomenal experience, but from a profound, implicit knowledge of the statistical regularities of human expression,
learned from vast corpora of human language and behavior. Their ‘decisions’ in a similarity judgment task can thus be
conceptualized as a high-throughput, data-driven reflection of the conventional structure of human emotion. Based on this, we
pioneer the ‘cognitive agent’ paradigm: a framework that employs LLMs as indefatigable cognitive agents to perform tasks
previously hard for humans, and ultimately, validating this surrogacy against the gold standard of alignment with real brain
activity.
Furthermore, this powerful paradigm also provides an unprecedented opportunity to address a central debate in cognitive
science: the role of sensory grounding in the formation of abstract concepts38,49–53. For non-sensorimotor concepts such as
emotion, the necessity of grounding is far from settled54–56. Indeed, recent work suggests that language-only models, even
without direct sensory connection to the world, can successfully represent non-sensorimotor features of concepts, including
emotion38. This leads to a more nuanced and critical question, which we term the ‘neural alignment hypothesis for sensory
grounding’: while language alone may be sufficient to form a coherent semantic space for emotion, is sensory grounding
nonetheless essential for developing a representational geometry that is truly aligned with the neural architecture of human
affective processing? To directly test this hypothesis, our study systematically compares two types of artificial intelligence (AI)
models with distinct cognitive architectures: a language-only model (LLM), which learns from abstract textual symbols, and a
vision-language multimodal LLM (MLLM), which learns from both visual and textual data, a process more akin to the visual
sensory experience of humans.
To test these hypotheses, we introduce a framework based on large-scale machine-behavioral experiments. By prompting an
LLM and an MLLM to make millions of similarity judgments on 2,180 emotionally evocative videos (or their descriptions), we
map their emergent affective representational spaces and systematically compare them to human behavioral ratings and fMRI
data (Fig. 1). The results yield a striking discovery: the MLLM’s emergent representation predicts neural activity in the human
brain with significantly greater accuracy than models derived from human behavioral ratings themselves. This superior neural
alignment provides the strong empirical support for our central hypothesis—that a paradigm based on large-scale similarity
judgments can indeed capture the brain’s native affective geometry more faithfully than traditional rating scales. Further analysis
of this neurally-aligned representation reveals that it is highly interpretable; its structure, while primarily organized along
categorical lines, artfully blends features of continuous dimensions, forming a hybrid representation that is highly consistent
with modern Semantic Space Theory of emotion10,11 and thus computationally reconciles the long-standing ‘category’ versus
‘dimension’ debate1,6. Finally, the superior performance of the multimodal model offers compelling computational neuroscience
evidence for the theory of sensory grounding, suggesting that a connection to the world through sensory modalities is key to
developing a truly neurally-aligned conceptual framework for emotion. This work not only establishes MLLM as a powerful
tool for exploring the computational underpinnings of affective cognition but also opens a path toward bridging the gap between
subjective experience and its neural substrates.
Results
To construct a comprehensive map of the human affective space—a goal previously intractable due to the immense scale of data
required—we introduced a novel framework that leverages large AI models as indefatigable ‘cognitive agents’. Our approach
centered on a large-scale dataset of 2,180 emotionally evocative videos, which are richly annotated with human emotion
ratings30, textual descriptions57, and corresponding fMRI activity24 (Fig. 1a). We probed the representational geometry of each
system using a triplet odd-one-out behavioral paradigm32,34,36,58 (Fig. 1b-e), generating over 5.5 million similarity judgments
for the LLM (Llama-3.159, using text captions) and 7.1 million similarity judgments for the MLLM (Qwen2-VL60, using video
input). For a human benchmark, we simulated judgments based on prior human ratings across 34 emotion categories and 14
affective dimensions30, creating two distinct human representational models. From these four sets of behavioral judgments, we
used Sparse Positive Similarity Embedding (SPoSE)58 to learn a 30-dimensional affective embedding space for each system
(Fig. 1f). Finally, we compared the structure of these learned spaces to each other and assessed their alignment with human
brain activity using representational similarity analysis (RSA)61 and voxel-wise encoding (Fig. 1g).
Before assessing their neurobiological plausibility, we first validated that the learned affective embeddings are both
stable and predictive. The 30-dimensional spaces, a dimensionality at which predictive performance saturated, were highly
reproducible across independent model initializations (Extended Data Fig. 1a-e). Crucially, these embeddings demonstrated
2/48


## Page 3

Prompt:
'Your role is an expert in analyzing the emotions conveyed in 
videos, each video is replaced by its corresponding textual 
description. Describe the specific emotions evoked by each video 
and identify which one is distinctly different (answer format: 
"Video+ID is noticeably different"), explaining the reason for 
this difference, while judging solely based on emotional tone 
without influence from video order.
video1: A soccer player is overcome with emotion and falls to the 
ground as his teammates pile on.
video2: A man does flips and takes his beer.
video3: A man crouches down, and a child comes onto his lap. 
He gets up, and they go towards the sea.'
1. Video1:  The scene depicts overwhelming joy, camaraderie, 
and triumph. 
2. Video2:  The man doing flips and taking his beer conveys 
a
lighthearted and playful
mood. The emotions here 
are amusement, light-hearted joy.
3. Video3:  The interaction between the man and the child, 
followed by walking toward the sea, evokes tenderness, warmth, 
and serenity. The emotions are gentle, affectionate, and peaceful.
Considering these emotional responses, **Video2 is noticeably 
different from the other two.**  Video2 conveys a light, 
playful, and individualistic emotion, while Video1 and Video3 
evoke deeper, emotionally rich experiences—triumphant group 
celebration and tender familial bonding, respectively. 
Parsing
Choice
LLM (Llama 3.1) : 
“Then, tell me Which clip evokes an emotional response that is 
noticeably different from the other two? (The answer format is 
“Video+ID is noticeably different from the other two.”)  Explain 
the reason for this difference.
Precautions:
1. You should focus your judgement on the emotional tone.
2. Do not provide ambiguous answers.
3. You are not given constraints as to the strategy you use.”
“Your role is an expert in analyzing the emotions conveyed in 
videos. 
Firstly,  describe the content and your evoked emotional response 
of each of these videos individually.”
Video 2 is noticeably different from the other two in terms of 
the emotional response it evokes. 
While Video 1 and Video 3 convey a sense of joy and happiness, 
Video 2 evokes a sense of excitement and thrill. The man 
performing a backflip in Video 2 is captured mid-air, which adds to 
the sense of adrenaline and excitement. The other two videos do 
not have such a dynamic and action-packed moment, making 
Video 2 stand out in terms of emotional response.
Prompt:
MLLM (Qwen2_VL): 
Parsing
Choice
Ratings of 
34 emotion categories
Ratings of 
14 affective dimensions
2,180 emotionally evocative short videos
Human 
annotators/subjects 
…
Video 2180
Video 1
Video 2
Video 2179
fMRI recording
…
Brain 
Affective representational geometries
Voxel-wise Neural 
Encoding
Error backpropagation
Predicted
Chosen
videos
Compute proximity for each pair 
(dot product)
Iteratively 
optimization 
Vector representations 
for video triplet
i
j
k
S(i, k)
S(j, k)
S(i, j)
i
j
k
MLLM
Qwen2_VL
    (7.1 Million trials)
Large-scale
 similarity judgements
SPoSE 
modeling
(see panel 
f.)
Experiment 3 
(Vision-Language-based odd-one-out task ) 
Prompt: Which video evokes an emotional 
response that is noticeably different from the other 
two?
SPoSE 
modeling
(see panel f.)
Video 1: A soccer player is overcome with emotion  …
Large-scale 
similarity judgements
Video 3: A man crouches down, and a child comes …
Video 2: A man does flips and takes his beer.
Prompt:
Which video evokes an emotional 
response that is noticeably different from the 
other two? 
SPoSE 
modeling
(see panel 
f.)
Experiment 2 
(Language-based odd-one-out task )
LLM
Llama 3.1
  (5.5 Million trials)  
SPoSE 
modeling
(see panel f.)
SPoSE 
modeling
(see panel 
f.)
Experiment 1
 (Emotion-rating-based odd-one-out task) 
Large-scale 
similarity judgements
Human 
C
B
A
B
Categorical Ratings
Cosine-distance
Emotion ratings
Dimensional Ratings 
(7.1 Million trials)  
…
Video 1
Video 2
Video 3
Video N
Chosen
(7.1 Million trials)  
SPoSE 
modeling
(see panel f.)
0.31 
0.46 
0.54 
0.69 
0
0.5
1
Excitement
Pride
Awe
Joy
…
Video 1
Video captions
Video 1: The sprinters are dashing  ...
Video 2: A famous singer is performing ...
   …
Video 2179: A mermaid dances …
Video 2180: A little cat is frolicking …
0.17 
0.25 
0.25 
0.75 
0
0.5
1
Valence
Arousal
Attention
Dominance
…
Video 1
…
…
#1
#2
#2180
RSA
Human
LLM
MLLM
a
b
c
d
e
f
g
Figure 1. Overview of the experimental and analytical pipeline. a, The study utilized a database of 2,180 emotionally
evocative videos with rich, pre-existing annotations, including human ratings on discrete emotion categories and continuous
affective dimensions, detailed textual descriptions, and corresponding fMRI data from viewers. b-d, Affective embeddings
were derived for four systems—human categorical ratings, human dimensional ratings, LLM, and MLLM—using a triplet
odd-one-out behavioral paradigm. Human similarity judgments were simulated based on the cosine similarity of their prior
ratings, while models performed the task directly. e, Example prompts and responses for the LLM and MLLM. f-g, Latent
embeddings were learned from over 7.1 million triplet judgments using SPoSE (f), and the resulting representational spaces
were compared to each other and to neural data (g).
excellent predictive validity: they accurately predicted triplet choices on held-out data, capturing the majority of explainable
variance (up to 91.59% for MLLM), and their global representational structure generalized to unseen stimuli (r up to 0.85
for MLLM; Extended Data Fig. 1f-j). This confirms that our machine-behavioral paradigm yields robust and generalizable
affective representations, providing a solid foundation for the primary analyses that follow.
Bridging the behavior-neural gap with affective representations derived from MLLM.
Our central hypothesis was that a comprehensive affective map, derived from large-scale similarity judgments, would bridge
the ‘behavior-neural gap’ by aligning more closely with the brain’s native geometry. To directly test this, we compared the
representational geometry of each model to that of human brain activity recorded during video viewing. A searchlight RSA61
across the brain revealed a two-fold result (Fig. 2a,b).
First, and most remarkably, the MLLM’s representation outperformed the representations derived directly from human
3/48


## Page 4

Thalamus
Hippocampus
Pallidum
Caudate
Putamen
Nucleus accumbens
Amygdala
Cerebellum
Hypothalamus
Brainstem
0.000
0.005
0.010
0.015
0.020
0.025
0.030
0.035
0.040
Subcortical RSA score
LLM
MLLM
Human (category)
Human (dimension)
Human (concat)
*
* * *
*
* * *
VC
ACC
Insula
IPL
MST
MTC
OFC
PC
STS
TE
TF
TPJ
DLPFC
DMPFC
VLPFC
VMPFC
0.00
0.02
0.04
0.06
0.08
0.10
0.12
0.14
0.16
Cortical Surface RSA score
* ***
*
*
* ***
* ***
* ***
*
*
* ***
*
**
*
**
* ***
* ***
*
*
*
0.00
0.05
0.10
0.15
0.186
0
0.1
0.2
0.3
Human (cat.) Performance (r)
0
0.1
0.2
0.3
MLLM Performance (r)
Searchlight RSA
Human (cat.) level
120% Human (cat.) level
100
101
102
103
104
105
0
0.1
0.2
0.3
Human (dim.) Performance (r)
0
0.1
0.2
0.3
MLLM Performance (r)
Searchlight RSA
Human (dim.) level
160% Human (dim.) level
100
101
102
103
104
105
0
0.1
0.2
0.3
Human (concat) Performance (r)
0
0.1
0.2
0.3
MLLM Performance (r)
Searchlight RSA
Human (concat) level
120% Human (concat) level
100
101
102
103
104
105
a
b
c
d
Searchlight RSA (r)
Subject 1
(All coloured voxels
P < 0.05, FDR corrected)
MLLM
LLM
Human (cat.)
Human (dim.)
Figure 2. MLLM representations show superior alignment with neural representations of emotion. a, b, Results of
searchlight RSA between model and brain, averaged in subcortical (a) and cortical (b) ROIs (averaged across subjects (N=5)).
Dots represent individual subjects; error bars reflect standard deviation (s.d.); all statistics are two-tailed t-tests across subjects,
with false discovery rate (FDR) correction; stars indicate significant differences between MLLM and the compared model (P <
0.05). c, Whole-cortex maps of searchlight RSA for a representative subject, illustrating the MLLM’s superior performance
across distributed emotion-processing networks. All coloured voxels are predicted significantly (P < 0.05, FDR-corrected,
two-tailed t-tests). d, Voxel-wise comparison of the MLLM’s performance against the human categorical, dimensional and
concatenated ratings model, using searchlight RSA.
4/48


## Page 5

behavioral ratings. Voxel-wise encoding analyses in Extended Data Fig. 3a,b also reveal consistent trends favoring the MLLM.
To ensure this counterintuitive finding was not an artifact of using separate human rating systems, we performed a critical
control analysis by creating a comprehensive ‘Human-concat’ model that combined categorical and dimensional ratings. Even
this unified human model was substantially outperformed by the MLLM. This finding is robust, as the SPoSE-derived human
embedding used for this comparison is a faithful representation of the original behavioral data, demonstrating a comparable
level of neural alignment to the raw self-report ratings themselves (Extended Data Fig. 2). This result provides the strong
empirical support for our central hypothesis: the ‘behavior-neural gap’ in affective science may be a direct consequence of the
methodological constraints of traditional rating scales. The machine-behavioral paradigm, by enabling similarity judgments at
an unprecedented scale, appears to capture the brain’s affective geometry with higher fidelity, allowing the MLLM to converge
on a representational scheme that is fundamentally more neurally-aligned.
Second, the MLLM’s representation showed significantly higher alignment with neural patterns than its language-only
LLM counterpart. This finding provides powerful computational evidence for the ‘sensory grounding’ hypothesis, suggesting
that a direct connection to the world through rich, dynamic visual data—rather than abstract linguistic symbols—is critical for
an AI model to develop a truly neurally-aligned affective framework.
The MLLM’s superior neural alignment was particularly evident in a distributed network of regions critical for emotion and
social cognition. Whole-cortex searchlight maps (Fig. 2c, Extended Data Fig. 3c and Extended Data Figs. 4-7a,b) revealed
that the MLLM exhibited a significant advantage in several cortical areas, including the temporoparietal junction (TPJ)62–65,
the inferior parietal lobule (IPL), high-level visual cortex (VC)66,67, the medial superior temporal area (MST)68–70, and the
medial temporal cortex (MTC). Furthermore, this advantage extended to key subcortical and cerebellar structures, including
the hippocampus and the cerebellum. Additionally, in Extended Data Fig. 8, we projected several affective components (the
dimensions of the learned embedding space, so termed to distinguish them from theoretical affective dimensions like valence) of
MLLM onto the cortical surface. The results reveal that a single affective component is processed concurrently across multiple
functionally related brain regions, albeit with varying activation intensities. A voxel-wise comparison across the entire brain
further confirmed the MLLM’s robust advantage (Fig. 2d, Extended Data Fig. 3d). The vast majority of voxels showed higher
alignment with the MLLM than with the best-performing human model, with the MLLM’s performance reaching up to 160%
of the human model’s performance. This pattern was highly consistent across all five subjects (Extended Data Figs. 4-7c,d),
underscoring the robustness of this discovery.
Models develop interpretable, categorical, and blended affective representations.
This remarkable brain alignment, particularly the MLLM’s advantage over human-derived models, raises a critical question:
What is the underlying structure of this neurally-superior affective space? To understand why this representation is so effective,
we dissected its emergent geometry, probing its interpretability and its fundamental organizational principles to see if it
conforms to traditional theories or finds a novel synthesis of its own.
To visualize the global structure of the learned embeddings, we projected the 2,180 video stimuli into a two-dimensional
space using t-SNE (Fig. 3a). Despite receiving no explicit categorical labels during the triplet judgment task, both LLM and
MLLM spontaneously organized their representations into distinct clusters corresponding to human emotion categories (e.g.,
amusement, fear, craving). These emergent structures mirrored those derived from human categorical ratings and, to a lesser
extent, human dimensional ratings, underscoring the foundational role of categorical organization in emotion representation24,30.
Moreover, the visualizations revealed smooth, psychologically meaningful transitions between clusters along continuous axes,
such as increasing arousal linking romance to sexual desire, and decreasing valence connecting amusement to fear. These
patterns closely align with established models of human affective space10,11,24,30.
A nearest-centroid classifier confirmed the strong categorical structure within the embeddings (Fig. 3b). While embeddings
from human categorical ratings performed best (top-3 accuracy: 98.58%), both LLM (72.43%) and MLLM (70.14%) substan-
tially outperformed chance, demonstrating robust categorical separability. To interpret the individual affective components, we
correlated each one with human ratings of 34 emotion categories and 14 affective dimensions30 (see Extended Data Table 1 and
Extended Data Figs. 9-14). This revealed that the vast majority of components were highly interpretable across all systems (Fig.
3f; We defined a component as interpretable if the correlation between it and any known label is greater than 0.1).
The models developed both shared and unique affective components, revealing their distinct cognitive architectures. For
example, both LLM and MLLM formed a component for adoration in response to cute animals and another for triumph from
victorious moments (Fig. 3c). However, models’ unique components offered compelling evidence for the ‘sensory grounding’
hypothesis (Fig. 3d). The LLM, constrained to abstract symbols, formed abstract components like low-control for scenes of
disasters, whereas the MLLM leveraged its direct perceptual access to the visual world to make far more granular distinctions,
such as separating romance from sexual desire and identifying anxiety in videos of extreme sports—nuances the LLM missed.
This divergence demonstrates how sensory grounding enables a fine-grained, object-centric affective representation, whereas a
purely symbolic system must compensate by relying on more abstract conceptual relationships.
5/48


## Page 6

chance
Human (cat.)
Human (dim.)
LLM
MLLM
0
20
40
60
80
100
Top3 Categorization performance (%)
a
Human (category)
Human (dimension)
LLM
MLLM
LLM
MLLM
c
LLM and MLLM share common affective components.
d
LLM and MLLM also possess distinctive affective components.
e
Both LLM and MLLM exhibit blended affective components.
b
f
g
Figure 3. Models develop interpretable, categorical, and blended affective components. a, t-SNE visualization of the
2,180 stimuli reveals the global structure of the affective spaces. Points are colored by their highest-rated human emotion
category, showing spontaneous clustering. b, Top-3 nearest-centroid accuracy, quantifying the categorical structure. c-e,
Examples of shared (c), unique (d), and blended (e) affective components, with top-weighted video frames and word clouds
(label size ∝correlation with human ratings). f, Proportion of components that were interpretable versus uninterpretable. g,
Proportion of interpretable components best described as purely categorical, purely dimensional, or a mix of both.
6/48


## Page 7

Ultimately, the most profound discovery was that both models converged on a hybrid coding scheme that intrinsically
blended categorical and dimensional features (Fig. 3e). For instance, LLM associated scenes of car crashes with both horror
(a category) and low-upswing (a dimension). Across the models, we found that 15 of the LLM’s components and 13 of the
MLLM’s were of this mixed type (Fig. 3g). This organization, which is neither purely categorical nor purely dimensional,
strongly aligns with the Semantic Space Theory of human emotion10,11, suggesting a convergent organizational principle for
affective representation in both artificial and biological intelligence.
Amusement
Interest
Awe
Aesthetic Appreciation
Surprise
Disgust
Fear
Joy
Confusion
Horror
Adoration
Boredom
Anxiety
Sexual Desire
Excitement
Sadness
Romance
Entrancement
Satisfaction
Calmness
Nostalgia
Admiration
Awkwardness
Sympathy
Envy
Empathic Pain
Triumph
Craving
Relief
Anger
Contempt
Disappointment
Guilt
Pride
valence
upswing
fairness
approach
attention
effort
obstruction
safety
dominance
arousal
commitment
control
identity
certainty
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
The 30 SPoSE Dimensions of Human Category
Joy
Aesthetic Appreciation
Sexual Desire
Horror
Excitement
Anxiety
Amusement
Interest
Boredom
Satisfaction
Sympathy
Confusion
Triumph
Calmness
Admiration
Romance
Fear
Nostalgia
Disgust
Craving
Awkwardness
Relief
Empathic Pain
Adoration
Entrancement
Sadness
Disappointment
Surprise
Guilt
Contempt
Anger
Awe
Envy
Pride
approach
valence
dominance
effort
arousal
obstruction
certainty
upswing
identity
control
commitment
fairness
safety
attention
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
The 30 SPoSE Dimensions of Human Dimension
Amusement
Fear
Aesthetic Appreciation
Excitement
Adoration
Romance
Surprise
Boredom
Sympathy
Sadness
Triumph
Awe
Empathic Pain
Entrancement
Joy
Nostalgia
Disgust
Satisfaction
Guilt
Confusion
Admiration
Envy
Relief
Contempt
Pride
Interest
Calmness
Horror
Anxiety
Disappointment
Anger
Awkwardness
Craving
Sexual Desire
valence
effort
control
arousal
commitment
identity
dominance
safety
attention
obstruction
certainty
fairness
approach
upswing
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
The 30 SPoSE Dimensions of LLM
Aesthetic Appreciation
Romance
Surprise
Nostalgia
Triumph
Adoration
Joy
Contempt
Craving
Sexual Desire
Fear
Envy
Sympathy
Admiration
Pride
Boredom
Disappointment
Amusement
Disgust
Horror
Anger
Entrancement
Awe
Relief
Calmness
Interest
Anxiety
Sadness
Empathic Pain
Excitement
Awkwardness
Confusion
Guilt
Satisfaction
valence
safety
effort
identity
dominance
approach
commitment
attention
control
certainty
obstruction
fairness
arousal
upswing
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
The 30 SPoSE Dimensions of MLLM
1.00
0.75
0.50
0.25
0.00
0.25
0.50
0.75
1.00
0.8
0.6
0.4
0.2
0.0
0.2
0.4
0.6
0.8
Emotion Categories
Affective Dimensions
Emotion Categories
Affective Dimensions
a.
Human Category
b. Human Dimension
c.
LLM
d. MLLM
Figure 4. Learned affective spaces are primarily organized by emotion categories. Correlation heatmaps showing the
relationship between the 30 learned affective components (y-axes) and the 48 categories/dimensions from human self-reports
(x-axes; 34 categories and 14 dimensions from Cowen et al.30). Each cell represents the PCC between a learned component and
a human-rated category or dimension. The strong diagonal patterns observed for the LLM (c) and MLLM (d)—mirroring the
pattern from human categorical data (a) but not dimensional data (b)—indicate that the models’ affective spaces are
predominantly structured along categorical, rather than dimensional, lines.
Models computationally reconcile the category-dimension debate with a hybrid coding scheme.
A central debate in affective science concerns whether emotions are represented as discrete categories1–4 or as constructions of
continuous dimensions6–9. Our neurally-aligned machine representations provide a unique computational testbed to adjudicate
this long-standing dichotomy. Fig. 4 shows the full cross-correlation matrices between the 30 learned components and the
7/48


## Page 8

human ratings across 34 emotion categories and 14 affective dimensions30. As expected, the human-derived embeddings served
as unambiguous benchmarks: the ‘human-category’ space showed a clean, one-to-one mapping with discrete categories (Fig. 4a,
r > 0.95 for 28 components; Extended Data Table 1), while the ‘human-dimension’ space strongly mapped onto continuous
dimensions (Fig. 4b).
Both the LLM and MLLM representations revealed a sophisticated synthesis of these two frameworks. On one hand, they
showed a powerful allegiance to the categorical benchmark, with their learned components forming a strong diagonal pattern
analogous to the human-category data (Fig. 4c,d). This indicates that a categorical structure serves as the primary organizing
backbone of the models’ affective space. On the other hand, the representations were not rigidly categorical. Unlike the cleanly
separated human-category data, a single model component often showed significant correlations not only with several related
emotion categories (e.g., MLLM component-27 correlating with anxiety, excitement, and fear) but also with one or more
continuous affective dimensions.
This evidence demonstrates that (M)LLMs do not adopt either theoretical framework exclusively but instead forge a hybrid,
blended coding scheme. This emergent organization offers a data-driven, computational reconciliation for the long-standing
‘category’ versus ‘dimension’ debate, providing compelling support for the Semantic Space Theory10,11, which posits that
human emotion concepts are simultaneously categorical and graded.
adoration
valence-high, upswing-high, 
amusement
adoration
amusement
surprise
upswing-high
approach-high, safety-high, 
valence-high
valence-high, upswing-high, 
amusement
excitement, anxiety, fear
anxiety, excitement, 
fear
fear, safety-low, 
control-low
aesthetic appreciation
joy
fear
dominance-high, certainty-
high, obstruction-low
upswing-high
valence-high, aesthetic 
appreciation, control-high
sympathy, disappointment, 
sadness
a
LLM
MLLM
Human
(category)
Human
(dimension)
b
LLM
MLLM
Human
(category)
Human
(dimension)
Figure 5. Attribution methods reveal the visual drivers of affective components. a, Illustration of example videos with
their affective decomposition. Each colored petal represents a specific affective component, and its length is proportional to that
component’s weight for the given video. b, Grad-CAM heatmaps identify the specific visual regions that drive responses in
selected components. Red indicates a strong positive contribution from that region to the component’s activation.
8/48


## Page 9

Learned affective components functionally control visual features.
Having established the hybrid structure of the affective space, we next sought to probe the functional role of its individual
constituents. Decomposing individual videos into their constituent affective components revealed consistent and interpretable
affective signatures across all systems. Rose diagrams (Fig. 5a), where each petal represents a component and its length
reflects the component’s weight, illustrate this consistency. For instance, a video of a dog playing in a pool reliably elicited
the component of amusement and high valence in both humans and models. Similarly, a first-person perspective of a bicycle
skydiving stunt was consistently decomposed into components of anxiety, excitement, and fear.
To move beyond correlational evidence and investigate the functional role of these components, we developed a two-stage
validation framework. First, we used gradient-weighted class activation mapping (Grad-CAM)71 to localize the precise visual
features that drove the activation of specific affective components. This attribution analysis revealed that the models’ affective
components were linked to semantically appropriate visual elements (Fig. 5b). For example, the MLLM’s fear component was
activated by the sight of a hand pierced by an arrow, with the heatmap concentrated on the injury. The LLM’s valence-low
component was triggered by an exploding vehicle, with attribution focused on the blast regions. In a positive context, the
MLLM’s adoration component was activated by a child on a slide, with the heatmap highlighting the child.
These attribution patterns were notably consistent across the MLLM, LLM, and human-derived representations. Remarkably,
despite processing only textual descriptions and having no direct visual input, LLM correctly inferred the likely visual objects
responsible for eliciting specific emotions, generating heatmaps nearly indistinguishable from the MLLM’s in many cases.
However, this result does not suggest that sensory experience is superfluous. Rather, it reveals that human language is itself
a vast repository of implicitly encoded sensory knowledge. Through large-scale language training, the LLM has learned to
construct a sophisticated conceptual blueprint of emotion, one that robustly links abstract affective states to their most probable
and prototypical visual causes38,41,42. The LLM’s success, therefore, lies not in replicating perception itself, but in masterfully
reverse-engineering a conceptual model of it from the statistical shadow it leaves in language.
The second stage of our framework, generative editing, provided strong evidence for the functional influence of the learned
components. By directly manipulating the activation value of a single component, we could predictably and precisely alter
the visual content of the video (Fig. 6). For instance, decreasing the activation of the sexual desire component (from 0.513 to
0.2) transformed a runway model’s undergarments into a formal dress (Fig. 6a). Similarly, attenuating a sympathy component
removed the chains from a man’s back piercings. Conversely, increasing a component’s activation could generate emotionally
congruent content. Elevating the anger, disappointment component (from 0.003 to 0.8) converted a documentary scene of a
concentration camp into footage of a riot, while amplifying the fear, safety-low component transformed a peaceful campfire
into a dangerous scene with a vehicle leaping through flames (Fig. 6b). Extended Data Figs. 17 and 18 present closed-loop
validation results where MLLM was presented with both original and edited videos for categorical judgment and explanation.
The MLLM’s altered responses to edited videos confirm successful manipulation of its affective interpretations (Extended
Data Figs. 17 and 18). Extended Data Fig. 19 presents more editing results. Together, these experiments provide compelling
evidence for a functional link: the learned affective components appear to not merely correlate with emotional content, but to
actively encode and influence the specific visual features that generate an affective response.
Convergent evolution and divergent signatures in human and artificial affect.
To map the high-level organizational principles, we visualized the affective spaces of all four systems as graphs of correlated
components and their community structures, revealing profound convergences and divergences (Fig. 7a-d). Graph analysis
immediately highlighted the impact of cognitive architecture: the MLLM and human rating-derived spaces possess a richly
interconnected structure, whereas the LLM’s space was significantly more fragmented, with substantially more isolated,
uncorrelated components (14 for LLM vs. 1-4 for other systems). This relative isolation in the LLM likely reflects its abstract,
non-grounded nature. Furthermore, community detection revealed that the MLLM developed the most granular affective
structure with seven distinct clusters, whereas the human dimensional space was the most consolidated with only three. This
superior granularity in the MLLM may partly explain its superior neurally-alignment. These affective communities were
annotated through systematic analysis of intra-cluster label commonality (Extended Data Table 2) and representative stimuli,
aligning well with established emotion theories72–82.
Despite these structural differences, we identified a High-arousal negative affect cluster82 that was remarkably conserved
across all four systems—a shared continental feature in the affective landscape (Fig. 7e). This shared core, maximally responsive
to threatening stimuli like car crashes and horror scenes (Extended Data Figs. 9-11), likely reflects its fundamental evolutionary
salience in humans3, which is mirrored in the high frequency of threat-related language in the models’ training data83. Beyond
this shared core, the systems diverged in ways that again underscored the importance of sensory grounding. Specialized clusters
for complex socio-cultural emotions, such as those related to Erotic content and Achievement, emerged in both the MLLM and
human categorical representations but were notably absent in the LLM. The MLLM’s ability to grasp these nuanced, embodied
concepts—which the purely symbolic LLM cannot—provides compelling final evidence for the sensory grounding hypothesis.
9/48


## Page 10

Sexual desire: 0.513 
Reduce 0.513 to 0.200 
Reduce 0.857 to 0.200 
Reduce 0.406 to 0.200 
Reduce 0.432 to 0.200 
Increase 0.003 to 0.800 
Increase 0.008 to 0.800 
Increase 0.005 to 0.800 
Increase 0.061 to 0.800 
Safety-low, fear, 
control-low: 0.857 
Disgust, effort-high, 
valence-low: 0.406 
Sympathy, disappointment, 
sadness: 0.432 
Anger, disappointment, 
control-low: 0.003 
Sexual desire: 0.008 
Adoration, joy: 0.005 
Fear, safety-low, 
control-low: 0.061 
Input video
SPoSE 
embedding
Grad-CAM
Edited video
Input video
SPoSE 
embedding
Edited video
a
b
Figure 6. Generative editing reveals how learned affective components control video content. a, Targeted removal of
emotional content by decreasing the activation of a specific affective component. Top to bottom: original video frames; the
targeted component (marked by red box) and its corresponding label as well as original activation (normalized to [0,1]); the
Grad-CAM heatmap identifying the visual drivers; and the edited video frames, where decreasing the component’s activation
transforms the visual drivers into irrelevant contents. b, Generative elicitation of emotional content by increasing component
activations. For example, increasing the fear component’s activation converts a peaceful campfire scene into a dangerous scene
with a vehicle leaping through flames. These manipulations demonstrate that the learned components functionally control the
visual elements that evoke specific emotions. For closed-loop validation, see Extended Data Figs. 17 and 18.
This was also reflected in the Delight cluster, where the MLLM fractionated into more specific, fine-grained sub-clusters.
Furthermore, we identified a unique Affective Dissonance cluster in human dimensional representations, containing both
positive (amusement, joy) and negative (fear) embeddings while bridging the Delight and High-arousal negative affect clusters.
This valence-ambivalent organization, absent in human categorical representations, likely represents an intermediate state along
the valence continuum. Its presence in both LLM and MLLM indicates that artificial systems employ hybrid strategies beyond
strict categorical or dimensional frameworks for affective processing.
Finally, a difference emerged not in the content but in the efficiency and richness of the representations. To probe these
representations, we assessed the number of components required to explain behavior. Although all systems initially represented
each stimulus with 30 components, we found these representations to be highly reducible. For any given stimulus, retaining
only a small subset of its most critical components was sufficient to achieve 95–99% of the full model’s predictive accuracy in
the odd-one-out task, as shown by the average number of components required per stimulus in Fig. 7f. Crucially, the AI models
required far fewer components (LLM: 3–4; MLLM: 1–4) than the human rating-derived representations (human-category:
7–10; human-dimension: 6–9). This suggests that while (M)LLMs develop human-like affective structures, their underlying
representations are currently more compressed than their human counterparts.
10/48


## Page 11

Erotic
Aesthetic 
Contemplation
Achievement 
and Glorification
Delight
High-arousal negative affect
High-arousal negative affect
Affective Dissonance
Delight
High-arousal negative affect
Empathy-related
Delight
Affective Dissonance
Attentional 
Immersion
High-arousal negative affect
Vigilant Passivity
Affective Dissonance
Erotic
High Arousal
Achievement and Glorification
Attentional Immersion
1
2
3
4
5
6
7
8
10
11
13
14
15
16
17
18
19
20
22
24
25
26
27
28
29
30
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
26
27
28
29
30
1
2
5
7
8
9
10
13
14
16
17
19
20
22
25
26
1
2
3
4
5
6
7
9
10
11
12
13
14
15
16
17
19
20
21
22
23
24
25
26
27
28
30
Human (category)
Human (dimension)
LLM
MLLM
1
2
1
1
2
1
1
1
4
3
2
1
0
Shared  Models
0
10
20
30
Number of components retained
100
80
60
40
20
0
Accuracy (%)
Human category
5
15
25
0
10
20
30
Number of components retained
100
80
60
40
20
0
Accuracy (%)
Human dimension 
5
15
25
0
10
20
30
Number of components retained
70
60
50
40
30
20
10
0
Accuracy (%)
 LLM 
5
15
25
0
10
20
30
Number of components retained
80
60
40
20
0
Accuracy (%)
MLLM
5
15
25
Human (category)
Human (dimension)
LLM
MLLM
a
b
c
d
e
f
Human (cat.)
Human (dim.)
LLM
MLLM
Pagerank value
0.01
0.18
Affective Clusters
Delight
Attentional Immersion
Affective Dissonance
High Arousal
Erotic
Achievement and Gloriﬁcation
Empathy-related
Vigilant Passivity
High-arousal negative affect
Aesthetic Contemplation
Figure 7. Convergent and divergent structures of affective spaces across humans and models. a-d, Affective graphs (left)
and community structure (right) for each of the four embedding spaces. In the graphs, nodes are affective components, and
edge width is proportional to the Pearson correlation between them (r > 0.2). In the community plots, components are grouped
into clusters using the Louvain algorithm, with node size reflecting PageRank centrality. Isolated nodes are excluded. e, The
overlap of affective clusters across all four systems, highlighting both shared and unique high-level structures. f,
Dimensionality reduction analysis showing the minimum number of principal components required to retain 95%–99% of the
predictive accuracy on the behavioral task (gray shaded area). The chance-level accuracy is marked by the red dashed line.
11/48


## Page 12

Discussion
Here, we provide compelling evidence that MLLMs can autonomously develop rich, neurally-aligned representations of human
emotion. By employing (M)LLMs as indefatigable cognitive agents to perform millions of similarity judgments, we uncovered
an emergent affective space that is not only highly interpretable and structurally analogous to human emotion concepts, but also
strikingly predictive of neural activity. Our central finding—that an MLLM’s learned representation explains brain activity in
emotion-processing networks with greater accuracy than representations derived from human self-reports—offers a potential
resolution to the long-standing ‘behavior-neural gap’ in affective science. This work provides strong support for two critical
hypotheses: first, that large-scale, similarity-based behavioral paradigms can capture the brain’s native affective geometry more
faithfully than traditional rating scales; and second, that sensory grounding is essential for developing a truly neurally-aligned
conceptual framework for emotion.
A machine-behavioral paradigm: MLLMs as computational cognitive agents.
A critical aspect of our study is the conceptualization of large AI models not merely as objects of study, but as revolutionary
tools for psychological and neuroscientific inquiry. While some research focuses on understanding the internal mechanisms of
these models by analyzing their weights and activations84–88, our work pioneers a complementary approach that can be termed
‘large-scale machine behavior.’ In this paradigm, the model serves as an indefatigable ‘cognitive agent,’ performing behavioral
tasks at a scale previously unimaginable for human participants35. The innovation lies not in dissecting the model’s internal
parameters, but in leveraging its emergent behavioral judgments to reconstruct a high-fidelity map of a complex affective space.
The resulting affective representational geometry is then validated against the gold standard of human brain activity. This
positions our work as a methodological advance, demonstrating how to use the outputs of AI to generate and test hypotheses
about the structure of human emotion, thus opening a frontier for theory-driven research in the affective sciences.
Bridging the behavior-neural gap.
A persistent challenge in affective neuroscience is the ‘behavior-neural gap’—the discrepancy between behavioral models of
emotion derived from self-reports and the actual neural representations of affective states24,25,27–29. Our findings suggest this
gap may not be an intractable problem of subjective-objective mapping, but rather a methodological artifact of the tools we
use. Traditional rating scales, by forcing subjective experience into predefined and often limited categorical or dimensional
labels30, may distort the underlying high-dimensional and blended geometry of emotion. Many behavioral studies of LLMs
adopt this very paradigm, administering standardized psychological scales to compare human and model rating vectors38,89–91.
While practical, this approach imposes strong human priors, constraining LLM responses within predetermined frameworks
and potentially obscuring the models’ true representational capabilities.
The machine-behavioral paradigm we introduced bypasses these constraints. The process of inferring a quantitative
geometry from millions of simple, qualitative similarity judgments is central to our approach’s success. Each triplet odd-one-out
decision, while simple, imposes a local constraint on the relative distances between three points in the affective space. By
aggregating millions of such constraints, we allowed the representational structure to emerge organically, enabling the SPoSE
algorithm to robustly reconstruct the global, multi-dimensional structure without the experimenter-imposed biases inherent in
rating scales32,34. The resulting MLLM representation showed superior alignment with neural data, suggesting it converged on
a geometry more consonant with the brain’s own organizational principles. This provides the strong empirical support for the
hypothesis that the ‘behavior-neural gap’ can be bridged with more sensitive, high-throughput behavioral methods, establishing
our approach as a powerful framework for exploring the computational underpinnings of affective cognition.
Sensory grounding as a prerequisite for neurally-aligned affective representation.
A central debate in cognitive science concerns the necessity of sensory grounding for forming abstract concepts38,49–53. Our
study offers critical evidence by testing the ‘neural alignment hypothesis for sensory grounding’. We found that while a
language-only LLM developed a coherent affective space, a vision-language-trained MLLM achieved significantly superior
alignment with human brain activity. This divergence suggests that while language alone can support the construction of
a conceptual blueprint of emotion38,41,42, direct sensory experience is critical for developing a representational geometry
that is truly aligned with the brain’s affective architecture. This finding resonates with studies comparing blind and sighted
individuals’ knowledge of sensory-related concepts92,93. Wang et al. reveals two forms of knowledge representation in the brain:
a sensory-derived one in perceptual regions, present only in the sighted, and a language-derived, sensory-independent one in
the dorsal anterior temporal lobe, present in both groups92. Our studies map onto this framework: the LLM successfully learns
the language-derived representation, explaining its considerable competence. The MLLM, however, additionally develops
a functional equivalent of the sensory-derived pathway. Its superior neural alignment stems from its ability to model the
complete, dual-representation architecture found in sighted individuals, where these two pathways are functionally connected.
Furthermore, language effectively transmits deep, causal-explanatory knowledge, not just superficial facts. Kim et al. showed
12/48


## Page 13

that while blind individuals are less consistent on arbitrary associative facts (e.g., "bananas are yellow"), they share a rich,
"intuitive theory" of color with sighted people, acquired through language93. The success of LLM lies in extracting this profound
structure of emotion embedded in language, masterfully reverse-engineering a conceptual model from the statistical shadow
sensory experience leaves in language. Nevertheless, the MLLM’s advantage demonstrates that this linguistically derived
knowledge is incomplete for achieving full brain alignment. Direct sensory grounding provides a granular, object-centric
representational layer necessary to mirror the complete neural architecture of human affective processing54–56.
A convergent hybrid coding scheme for emotion.
For decades, affective science has been dominated by the debate between discrete category theories1–4 and continuous dimension
theories5–9. Our findings offer a data-driven, computational reconciliation. The learned affective spaces, particularly in the
MLLM, were neither purely categorical nor purely dimensional. Instead, they revealed a hybrid, blended coding scheme.
The representations were primarily organized along a categorical backbone, spontaneously forming clusters corresponding to
human emotion labels. Yet, these categories were not discrete islands; they were connected by smooth, meaningful gradients
and individual components often encoded a mix of categorical and dimensional features (e.g., horror and low-upswing). This
emergent architecture provides compelling support for the Semantic Space Theory of emotion10,11, which posits that human
emotion concepts are simultaneously categorical and graded. The convergence of this organizational principle in both biological
intelligence and AI suggests it may be a highly efficient and fundamental solution for representing the complex landscape of
affective experience.
Broad applications of this study.
Our findings offer several immediate applications and broader implications. As AI models demonstrate increasingly human-like
capabilities in conceptual32,34,36,38,39 and emotional cognition43,44,47,91,94–99, understanding their alignment with human
cognition becomes crucial. Our work contributes a powerful paradigm for this endeavor. Early approaches often addressed
alignment by extracting activations from specific model layers to predict neural activity84–88,100. However, this paradigm faces
challenges with contemporary large-scale proprietary models where internal activations are inaccessible, and even with open
models, selecting the correct layer is non-trivial. By deriving representations from model behavior rather than internal states,
our approach offers a more generalizable and principled way to systematically compare AI and human cognition.
First, the interpretable and neurally-aligned affective components we uncovered provide a blueprint for building AI systems
with more genuine emotional intelligence. These representations could be used to create empathetic human-agent interfaces and
social robots capable of more nuanced interactions101,102. Critically, they also open avenues in computational psychiatry. For
example, they could serve as a more objective and fine-grained feature set for mental health support tools that better understand
user affect, potentially aiding in the early detection of depression from behavioral cues103,104. Furthermore, for conditions like
autism spectrum disorder, which often involve challenges in emotion recognition, these neurally-grounded components could
form the basis of novel training paradigms designed to align an individual’s affective judgments with neurotypical patterns.
Besides, our two-stage attribution and editing framework serves as a generalizable tool for validating and interpreting affective
representations in any AI system. It also provides a novel methodology for creating controlled, diverse affective stimuli by
systematically editing neutral videos to elicit targeted emotions, addressing a common bottleneck in affective science research.
Finally, the large-scale machine behavior dataset collected in this study provides a valuable benchmark for evaluating and
fine-tuning the emotional alignment of future AI models, accelerating the development of systems that can safely and effectively
navigate the human social-emotional world.
Limitations and future directions.
A potential limitation of machine-behavioral studies is the sensitivity of model responses to the specific structure and wording
of the prompts. This raises the concern that the observed judgments might reflect artifacts of the prompt design rather than
the models’ intrinsic representational geometry. We explicitly addressed this issue during our data collection protocol. Initial
tests revealed a strong positional bias where the MLLM preferentially selected the last item in a triplet with naive prompts. To
mitigate this, we developed a text-video interleaved prompt that, as demonstrated in our supplementary analyses (Supplementary
Fig. 1), successfully eliminated this bias and produced an approximate uniform choice distribution (Supplementary Fig. 2d).
While prompt engineering remains a critical variable in AI-based cognitive science, our methodological validation ensures
that the large-scale behavioral data used in this study faithfully reflects the models’ emergent affective structures, thereby
strengthening the reliability of our conclusions.
This study has several other limitations that open promising avenues for future research. Our large-scale behavioral data
collection was focused on two primary models, which, while powerful, may not represent the full diversity of AI architectures.
Although our smaller-scale analysis of 22 models provides evidence for the generalizability of our findings (Extended Data Fig.
20), future work should extend the large-scale analysis to a wider range of models. Furthermore, our human benchmark was
simulated from prior rating data; a valuable next step would be to collect large-scale triplet judgments directly from human
13/48


## Page 14

participants to enable a direct comparison of AI- and human-derived behavioral geometries. Finally, both the video stimuli,
primarily sourced from Western cultures30, and the training data of the AI models may contain cultural biases. The learned
affective geometry might therefore reflect a culturally-specific representation of emotion31,105. Future research should validate
our findings using cross-cultural emotional datasets to explore the universality of the emergent affective space.
Looking forward, our findings suggest several exciting research directions. Our generative editing framework provides
a powerful tool for probing functional mechanisms. A future study could use this framework to create minimally-paired
video stimuli where only a single affective component is altered. Presenting these stimuli to participants in a real-time fMRI
experiment would allow for a direct test of whether manipulating a specific MLLM-derived component selectively modulates
activity in the brain networks we identified. Furthermore, as noted above, the potential cultural bias in the stimuli and models
necessitates research on the universality of our findings. A crucial next step would be to apply our machine-behavioral paradigm
to a large-scale, cross-cultural database of emotional videos to determine which aspects of the affective geometry are culturally
invariant and which are culturally specific. These future steps will be critical for building a truly comprehensive and universal
model of human emotion.
Methods
Stimuli and associated data. The stimuli were 2,180 unique, emotionally evocative short video clips (mean duration ≈5
s) obtained from the dataset compiled by Cowen et al.30 (totally 2,196 video clips, where 16 duplicate clips were removed,
resulting in 2,180 unique videos). These videos were originally sourced to represent a broad spectrum of 34 distinct emotion
categories and depict a diverse range of psychologically significant content, from major life events and social interactions to
aesthetic experiences and survival-related threats106–109. Our analyses leveraged four data modalities associated with these
stimuli: (1) human behavioral ratings of the videos across 34 emotion categories and 14 affective dimensions30; (2) detailed
textual descriptions of video content (20 unique captions per video)57; (3) human brain responses (fMRI) recorded while
participants viewed the videos24; and (4) the video clips themselves.
Human behavioral ratings. Human behavioral ratings for the video stimuli were obtained from Cowen et al.30, where
they were originally collected via Amazon Mechanical Turk (AMT). These ratings consisted of two types. First, for 34
discrete emotion categories, participants rated the extent to which each video elicited each emotion (0–100 scale); these were
subsequently processed to reflect the proportion of raters who reported feeling the emotion. Second, a separate cohort of
participants rated each video on 14 continuous affective dimensions using a 9-point Likert scale. For both rating types, final
scores for each video were generated by averaging across participants (9–17 raters per video).
Video content descriptions. Textual descriptions of the video content were obtained from Horikawa57. These descriptions
were collected on AMT following the protocol of the Microsoft COCO Captions dataset110. This process yielded 20 unique,
detailed captions for each video stimulus, which served as the linguistic input for the LLMs in our study.
Triplet odd-one-out task. To probe the models’ intrinsic representational structure, we used a triplet odd-one-out task. In
each trial, a model was presented with three stimuli (either videos for MLLMs or text descriptions for LLMs) and was asked
to identify which of the three was most different from the other two in terms of emotional content. Crucially, no constraints
or specific criteria (e.g., valence, arousal, or specific emotion categories) were provided, allowing the models to use any
features they deemed relevant. This unconstrained approach minimizes the influence of experimenter priors on the emergent
representations.
Trial sampling strategy. The total number of possible triplets from 2,180 stimuli is computationally intractable (
 2180
3

≈
1.72×109). Therefore, we employed a sparse yet comprehensive sampling strategy to generate the trial set. First, all possible
unique pairs of stimuli were generated (
 2180
2

= 2,375,110 dyads). Then, for each dyad, we created three unique triplets by
pairing it with three different, randomly selected stimuli from the remaining pool. This procedure resulted in a final set of
7,125,330 triplets (0.41% coverage) that was used for the primary behavioral data collection for all systems.
Simulating human behavioral responses. To create human benchmark datasets for the triplet odd-one-out task, we simulated
judgments based on the behavioral ratings from Cowen et al.30. This simulation was performed for each of the 7.1 million
triplets. For any given triplet of stimuli (A, B, C), we calculated the pairwise cosine similarities between their vector represen-
tations (A-B, A-C, B-C). The pair with the highest similarity was considered the ‘non-odd’ pair, and the third stimulus was
designated the ‘odd-one-out’. This procedure was performed independently using the 34-dimensional emotion category vectors
and the 14-dimensional affective dimension vectors, resulting in two distinct human behavioral datasets: ‘Human-category’ and
14/48


## Page 15

‘Human-dimension’.
Collecting behavioral responses from MLLMs. We collected behavioral data from several MLLMs, with a primary focus
on Qwen2-VL 7B60 for the main analysis. For this model, we collected responses for all 7.1 million triplets. To mitigate the
positional bias observed in initial tests (see Supplementary Fig. 1), we used a text-video-text interleaved prompt:
Text input 1: "Now we need to perform a role-playing task. Your role is an expert in analyzing the emotions conveyed in videos.
Firstly, please describe the content and your evoked emotional response of each of these videos individually."
Video input: {[Video_1], [Video_2], [Video_3]}
Text input 2: "Then, tell me Which clip evokes an emotional response that is noticeably different from the other two? (The
answer format is "Video+ID is noticeably different from the other two") Explain the reason for this difference. /n Precautions:
1. You should focus your judgement on the emotional tone, never be influenced by the video index or location when making
judgments. 2. Assume you are an emotional judgment expert with the ability to feel specific emotions for each video. Do not
provide ambiguous answers. Never be influenced by the video index or location when making judgments. 3. You are not given
additional constraints as to the strategy you should use."
During inference, videos were resized to 256×256 pixels, and frames were sampled at a variable rate depending on video
duration (see Eq. 1). Model choices were extracted from the generated text using regular expressions matching the key phrase
"noticeably different".
fps =









2.0
if d ≤5
1.0
if 5 < d ≤15
0.5
if 15 < d ≤20
0.2
otherwise
(1)
For the comparative analysis of model scaling (see Fig. 20), we collected data from a wider range of MLLMs (Qwen2-VL
2B, 72B; Llama3.2-vision 11B; ChatGPT4o-mini) on a smaller, fully-sampled validation set of 214,500 triplets derived from
66 prototypical stimuli. These 66 prototypical stimuli were selected as the two highest-rated videos per emotion category,
with duplicates consolidated. The triplet sampling protocol comprised two stages: (1) random selection of video pairs from
the 66 prototypical stimuli (
 66
2

possible combinations), followed by (2) augmentation with 100 randomly selected distinct
videos from the complete 2,180 stimuli. This systematic approach generated 214,500 total trials (
 66
2

×100), thereby ensuring
comprehensive sampling coverage that includes all possible triplet combinations among the 66 core stimuli. Note that these
214,500 triplet judgments are not included in the training data of embedding learning stage.
To estimate the noise ceiling (the upper bound of predictive performance), we measured inter-trial reliability by collecting
20 responses for each of 2,000 randomly selected triplets and calculating the mean choice consistency.
Collecting behavioral responses from LLMs. Behavioral data from LLMs were collected with a primary focus on Llama3.1
(70B)59, for which we evaluated 5.5 million triplets (a sample size shown to be sufficient for stable embeddings, see Supple-
mentary Fig. 2e). The prompt was analogous to the one used for MLLMs, with video inputs replaced by their corresponding
textual descriptions, which were randomly sampled from the 20 available captions for each trial:
Text input 1: "Now we need to perform a role-playing task. Your role is an expert in analyzing the emotions conveyed in videos,
each video is replaced by its corresponding textual description. /n Firstly, please describe your evoked emotional response of
each of these videos individually. Then, tell me Which video evokes an emotional response that is noticeably different from the
other two? Never be influenced by the video index when making judgments. (The answer format is "Video+ID is noticeably
different from the other two.") Explain the reason for this difference. /n Precautions: 1. You should focus your judgement on the
emotional tone, never be influenced by the video index when making judgments. /n 2. Assume you are an emotional judgment
expert with the ability to feel specific emotions for each video. Do not provide ambiguous answers. Never be influenced by the
video index when making judgments. /n 3. You are not given additional constraints as to the strategy you should use."
Text input 2: {[Video_1: caption_1], [Video_2: caption_2], [Video_3: caption_3]}
For the comparative scaling analysis, we collected data from a range of other LLMs (Qwen2.5-instruct 7B111, Qwen2-emotion
7B112, Llama3.1 8B59, Llama3.1-empathy 8B112, Llama3.1 405B59, Deepseek-R1 series (7B-671B)113) on the same 214,500-
triplet validation set used for the MLLMs. This included models (Qwen2-emotion 7B and Llama3.1-empathy 8B) specifically
fine-tuned on empathy datasets. Due to computational constraints, a subset of over 100,000 trials was collected for some models
(Qwen2-VL 72B, ChatGPT4o_mini, and Deepseek-R1 series).
Deriving behavioral responses from non-generative models. For models that do not have generative question-answering
capabilities (e.g., CLIP114, ResNet115, VideoMAE116), we simulated their behavioral responses based on the similarity of their
15/48


## Page 16

feature representations. For each stimulus, we first extracted a single feature vector from a pre-trained model. For image-based
models (e.g., ResNet, CLIP-image), features from individual video frames were temporally averaged. For text-based models
(e.g., CLIP-text), features were extracted from the video captions. For each triplet, the odd-one-out choice was determined by
computing the pairwise cosine distances between the three feature vectors; the stimulus with the greatest average distance to the
other two was selected as the odd-one-out.
Learning affective embeddings with SPoSE. We used the SPoSE algorithm32,58 to learn a low-dimensional, sparse, and
non-negative representation for each stimulus from the triplet odd-one-out behavioral data. SPoSE models the probability that a
given pair (ˆi, ˆj) within a triplet (i, j,k) is chosen as the most similar. This probability is modeled via a softmax function over
the inner products of the stimuli’s respective embedding vectors, x:
Pr
 (ˆi, ˆj)
 (i, j,k)

=
exp(x⊤
ˆi x ˆj)
exp(x⊤
i x j)+exp(x⊤
i xk)+exp(x⊤
j xk).
(2)
The embeddings xi for all stimuli i = 1...N are optimized by maximizing the log-likelihood of the observed behavioral choices
across all M trials in the dataset B. To encourage sparsity, an L1 regularization term is added to the objective function:
L =
∑
{(i,j,k),(ˆi, ˆj)}∈B
log
 
exp(x⊤
ˆi x ˆj)
exp(x⊤
i x j)+exp(x⊤
i xk)+exp(x⊤
j xk)
!
+λ
N
∑
i=1
∥xi∥1,
(3)
where λ is the regularization hyperparameter. Optimization was performed iteratively. The learning rate (lr) was set to 0.001
for all models. The regularization coefficient (λ) was set to 0.0025 for MLLM and LLM, 0.004 for Human-category, and 0.005
for Human-dimension.
Reproducibility of embedding dimensions. To assess the stability of the learned embeddings, we performed 10 independent
runs of the SPoSE algorithm for each system, each with a different random initialization. To quantify reproducibility, for each
dimension in a given run, we identified the dimension in each of the ten runs with which it had the highest Pearson correlation.
Following established methods32,36, these correlation coefficients were Fisher z-transformed before being averaged across runs
to yield a final reproducibility score for each dimension. The mean scores were then inverse-transformed.
Nearest-centroid classification. To quantitatively assess the categorical structure of the learned embeddings, we performed a
classification analysis. We used a nearest-centroid classifier with a leave-one-out cross-validation scheme across 2,166 videos
from 27 emotion categories (categories with <10 samples were excluded). In each fold, a category’s centroid was computed as
the mean embedding vector of all stimuli in that category, excluding the held-out stimulus. The held-out stimulus was then
assigned to the category of the nearest centroid (Euclidean distance). Overall performance was reported as the mean top-3
classification accuracy. The empirical chance level was determined via 1,000 permutation tests where category labels were
randomly shuffled.
fMRI data acquisition and preprocessing. The fMRI dataset was obtained from Horikawa et al.24. Data from five subjects
were acquired on a 3T Siemens MAGNETOM Verio scanner as they viewed the 2,180 video clips. Stimuli were presented using
a luminance-calibrated projector, and head motion was minimized with individualized bite-bars. The experiment consisted of
61 runs, each 7-10 minutes long, with functional scans acquired every 2 seconds (TR=2s).
The fMRI data were preprocessed using fMRIPrep 1.2.1117. The pipeline included susceptibility distortion correction,
slice-timing correction (AFNI 3dTshift118), motion correction (FSL mcflirt119), and coregistration to the subject’s T1-weighted
anatomical scan (FreeSurfer bbregister120). After projection to the cortical surface, nuisance variables (baseline, linear trend,
and six motion parameters) were regressed out. The resulting time-series data were compensated for a 4s hemodynamic delay,
despiked (removing fluctuations >3 s.d.), averaged within each video block, and finally z-scored for each voxel.
fMRI regions of interest (ROIs). Cortical surfaces were reconstructed using FreeSurfer121 and visualized using Pycortex122.
Cortical ROIs were defined based on the Human Connectome Project’s multimodal parcellation atlas123, and included areas in
the visual cortex (VC), temporo-parietal junction (TPJ), inferior parietal lobule (IPL), precuneus (PC), superior temporal sulcus
(STS), temporal area TE (TE), temporal area TF (TF), medial temporal cortex (MTC), medial superior temporal (MST), insula,
dorsolateral prefrontal cortex (DLPFC), dorsomedial prefrontal cortex (DMPFC), ventrolateral prefrontal cortex (VLPFC),
ventromedial prefrontal cortex (VMPFC), anterior cingulate cortex (ACC), and orbitofrontal cortex (OFC). Subcortical ROIs,
including the thalamus, hippocampus, hypothalamus, pallidum, brainstem, caudate, putamen, nucleus accumbens, amygdala,
16/48


## Page 17

and cerebellum, were defined following the procedure of Horikawa et al.24.
Neuroimaging analyses: Voxel-wise encoding and searchlight RSA. We used two complementary methods to compare the
learned representations with fMRI data: voxel-wise encoding and searchlight RSA.
Voxel-wise encoding. We trained a regularized linear regression model (ridge regression) to predict the activity of each individual
brain voxel as a linear combination of the 30 dimensions of a given representation (e.g., MLLM). Models were trained and
evaluated using a 5-fold cross-validation scheme. Within each training fold, the optimal regularization parameter for each voxel
was selected from 100 logarithmically spaced values (10−3 to 103) via a nested 6-fold cross-validation. Model performance
was quantified as the Pearson correlation between predicted and actual fMRI responses on the held-out test data.
Searchlight RSA. To optimize the signal-to-noise ratio for RSA, we first selected a subset of 100 stimuli that elicited the most
reliable neural patterns. Reliability was determined using a leave-one-out voxel-wise encoding procedure: for each of the 2,180
stimuli, a model was trained on the other 2,179 stimuli and used to predict the response to the held-out stimulus. The 1,000
stimuli with the highest prediction accuracy were selected for the RSA. The searchlight analysis61 was then performed on
this subset. For each voxel, a neural RSM was computed from the patterns of activity within a spherical searchlight (radius
= 3 voxels). This neural RSM was then compared to each model’s RSM using Spearman’s rank correlation, resulting in a
whole-brain map of representational similarity.
Cortical surface visualization. All cortical brain maps were visualized on flattened surface representations of each subject’s
native anatomy to allow for comprehensive inspection of the results. Cortical surface meshes were reconstructed from individual
T1-weighted anatomical scans using FreeSurfer121. The functional data were then aligned to these surfaces and plotted using
Pycortex122.
Measuring human-model behavioral consistency. To compare the behavioral patterns of different models to humans (Fig.
20), we used the validation set of 214,500 triplets derived from 66 prototypical stimuli. For each model and for the human
benchmark data, we constructed a 66×66 RSM, where each entry represented the choice probability for a given pair of stimuli.
Human-model consistency was then quantified as the Pearson correlation between the model’s RSM and the human RSM,
adjusted for the reliability of each RSM using the correction formula from Rajalingham et al.124. Reliability was estimated
using a split-half correlation on the behavioral trials. The calculation formula is expressed as follows:
˜ρ(m,h) =
ρ(RSMm,RSMh)
q
ρ(RSMhalf1
m
,RSMhalf2
m
)·ρ(RSMhalf1
h
,RSMhalf2
h
)
,
(4)
where RSMhalf1
m
and RSMhalf2
m
were constructed from split-half behavioral data of the 66 prototypical stimuli, with analogous
computation for the human RSM components.
Labeling of the learned affective components. To interpret the meaning of each of the 30 learned components, we correlated
each component’s vector (a 2,180-element vector of stimulus weights) with the corresponding human rating vectors for the 34
emotion categories and 14 affective dimensions from Cowen et al.30. A component was assigned the labels of the top three
most highly correlated human-rated terms (based on absolute Pearson’s r), subject to a cutoff rule: if the top-correlated term’s
coefficient was at least 0.1 greater than the second, only the top term was kept. This process was iterated for the second and
third terms. Component’s labels were suffixed with ‘-high’ or ‘-low’ to indicate the sign of the correlation (e.g., valence-high or
arousal-low). The full list of labels is provided in Extended Data Table 1.
Attribution analysis using Grad-CAM. To identify the visual features driving each affective component, we employed an
attribution analysis based on Grad-CAM71. First, to bridge the learned affective space with a vision model’s feature space, we
trained a simple linear model to project video features (temporally averaged from the frame-wise features) from the pre-trained
CLIP visual encoder into our 30-dimensional SPoSE space. This model was optimized via mean squared error minimization.
With this projection in place, for any target affective component and input video frame, we computed the gradient of the
component’s activation with respect to the feature maps of the CLIP encoder’s final convolutional layer. These gradients were
then used to produce a saliency heatmap, which was upsampled and overlaid on the original frame to visualize the specific
image regions responsible for activating that component (see Extended Data Fig. 15).
Probing the functional role of components via generative emotion editing. To probe the relationship between the learned
affective components and the visual content of videos, we developed a generative editing framework that operates by mapping
between our affective space and a pre-trained semantic space (Extended Data Fig. 16). The core of this framework is an
17/48


## Page 18

‘emotion projector’ model, which learns to translate manipulations in the affective space into targeted changes in the semantic
space, which then guide a video generation model.
Emotion projector training. The emotion projector is a five-layer MLP with LayerNorm, trained to map a 30-dimensional
SPoSE embedding (fSPoSE) to CLIP’s 768-dimensional joint latent space. The training objective was to align the projector’s
output, fproj = MLPLN(fSPoSE), with the corresponding text and vision embeddings from the original video, using a tri-modal
contrastive loss:
LCLIP = LBiInfoNCE(fproj,fvision)+LBiInfoNCE(fproj,flanguage),
(5)
LBiIn foNCE = −1
B
B
∑
i=1

log
exp(s(ˆzi,zi)/τ)
∑B
j=1 exp(s(ˆzi,z j)/τ) +log
exp(s(ˆzi,zi)/τ)
∑B
k=1 exp(s(ˆzk,zi)/τ)

,
(6)
where s(·,·) is the cosine similarity, z and ˆz are representation from the two modalities, B is the batch size, and τ is a learned
temperature parameter. For training stability, MSE loss directly supervises fproj against flanguage:
Lproj1 = ∥fproj −flanguage∥2
2.
(7)
To enable token-level editing, we supervise an up-projected representation against token features:
Lproj2 = ∥(Wup ·fproj +bup)−ftext-token∥2
2,
Wup ∈R768×(77×768).
(8)
The composite loss combines these objectives with adjustable hyperparameters:
L = Lproj1 +λ1 ·LCLIP +λ2 ·Lproj2.
(9)
The model was trained for 600 epochs, with a 50-epoch warm-up period, using an Adam optimizer, a learning rate of 2×10−4,
and a batch size of 128. The loss weighting hyperparameters were set to λ1 = 0.5 and λ2 = 1.
Video editing inference pipeline. The editing process at inference proceeded as follows. First, a target dimension in a video’s
original SPoSE embedding (fSPoSE) was manually modified to create an edited embedding (ˆfSPoSE). This edited embedding was
then passed through the trained emotion projector to generate a new set of target semantic tokens. In parallel, the original video
was encoded into a latent representation by a VQVAE encoder. DDIM inversion was applied to this latent representation to
generate an initial noise tensor that preserved the temporal structure and content of the original video. Finally, a pre-trained
Stable Diffusion model (v1.5) was conditioned on the new target semantic tokens to denoise this initial tensor, generating
the edited video frame by frame in the latent space. The edited latent frames were then reconstructed into pixel space by the
VQVAE decoder to produce the final output video.
Emotion graph construction and analysis. To analyze the high-level structure of the learned affective spaces, we first
constructed an ‘emotion graph’ for each system. In these graphs, the 30 learned components were treated as nodes. An edge
was drawn between any two nodes if the absolute Pearson correlation of their stimulus weights exceeded a threshold of ρ > 0.2,
with the edge weight set to the correlation value. To identify clusters of related components, we applied the standard Louvain
community detection algorithm to partition the graph into non-overlapping communities125. We removed the resulting isolated
nodes. Finally, to identify the most central or influential components within each graph, we calculated the PageRank centrality
for each node126.
Data availability
The short videos and their human ratings can be requested from https://goo.gl/forms/XErJw9sBeyuOyp5Q2. The
preprocessed fMRI: https://github.com/KamitaniLab/EmotionVideoNeuralRepresentationPython.
The video captions are available at https://github.com/horikawa-t/MindCaptioning. The machine-behavioral
judgments can be found at https://osf.io/wtp98/?view_only=0ad8badccb2a4bbcac5c887f53e96238.
Code availability
The codes used for data collection, embedding learning, result analysis, and visualization in this study are publicly available at
https://osf.io/wtp98/?view_only=0ad8badccb2a4bbcac5c887f53e96238.
18/48


## Page 19

References
1. Ekman, P. An argument for basic emotions. Cogn. & emotion 6, 169–200 (1992).
2. Prinz, J. Which emotions are basic. Emot. evolution, rationality 69, 88 (2004).
3. Panksepp, J. Affective neuroscience: The foundations of human and animal emotions (Oxford university press, 2004).
4. LeDoux, J. Rethinking the emotional brain. Neuron 73, 653–676 (2012).
5. Russell, J. A. A circumplex model of affect. J. personality social psychology 39, 1161 (1980).
6. Barrett, L. F. Are emotions natural kinds? Perspectives on psychological science 1, 28–58 (2006).
7. Russell, J. A. Core affect and the psychological construction of emotion. Psychol. review 110, 145 (2003).
8. Lindquist, K. A., Wager, T. D., Kober, H., Bliss-Moreau, E. & Barrett, L. F. The brain basis of emotion: a meta-analytic
review. Behav. brain sciences 35, 121–143 (2012).
9. Barrett, L. F. How emotions are made: The secret life of the brain (Pan Macmillan, 2017).
10. Cowen, A. S. & Keltner, D. Semantic space theory: A computational approach to emotion. Trends Cogn. Sci. 25, 124–136
(2021).
11. Keltner, D., Brooks, J. A. & Cowen, A. Semantic space theory: Data-driven insights into basic emotions. Curr. Dir.
Psychol. Sci. 32, 242–249 (2023).
12. Lindquist, K. A., Satpute, A. B., Wager, T. D., Weber, J. & Barrett, L. F. The brain basis of positive and negative affect:
evidence from a meta-analysis of the human neuroimaging literature. Cereb. cortex 26, 1910–1922 (2016).
13. Kragel, P. A. & LaBar, K. S. Decoding the nature of emotion in the human brain. Trends cognitive sciences 20, 444–455
(2016).
14. Zhang, R. et al. A neurofunctional signature of affective arousal generalizes across valence domains and distinguishes
subjective experience from autonomic reactivity. Nat. Commun. 16, 6492 (2025).
15. Saarimäki, H. et al. Discrete neural signatures of basic emotions. Cereb. Cortex 28, 2563–2573 (2018).
16. Phan, K. L., Wager, T., Taylor, S. F. & Liberzon, I. Functional neuroanatomy of emotion: a meta-analysis of emotion
activation studies in pet and fmri. Neuroimage 16, 331–348 (2002).
17. ˇCeko, M., Kragel, P. A., Woo, C.-W., López-Solà, M. & Wager, T. D. Common and stimulus-type-specific brain
representations of negative affect. Nat. neuroscience 25, 760–770 (2022).
18. Bo, K. et al. A systems identification approach using bayes factors to deconstruct the brain bases of emotion regulation.
Nat. Neurosci. 27, 975–987 (2024).
19. Reddan, M. C. et al. Neural signatures of emotional intent and inference align during social consensus. Nat. Commun. 16,
6156 (2025).
20. Zhou, F. et al. A distributed fmri-based signature for the subjective experience of fear. Nat. communications 12, 6643
(2021).
21. Liu, X. et al. A neural signature for the subjective experience of threat anticipation under uncertainty. Nat. Commun. 15,
1544 (2024).
22. Gan, X. et al. A neurofunctional signature of subjective disgust generalizes to oral distaste and socio-moral contexts. Nat.
human behaviour 8, 1383–1402 (2024).
23. Zhang, H. et al. The role of negative emotions in sex differences in pain sensitivity. Neuroimage 245, 118685 (2021).
24. Horikawa, T., Cowen, A. S., Keltner, D. & Kamitani, Y. The neural representation of visually evoked emotion is
high-dimensional, categorical, and distributed across transmodal brain regions. iScience 23 (2020).
25. Koide-Majima, N., Nakai, T. & Nishimoto, S. Distinct dimensions of emotion in the human brain and their representation
on the cortical surface. NeuroImage 222, 117258 (2020).
26. Giordano, B. L. et al. The representational dynamics of perceived voice emotions evolve from categories to dimensions.
Nat. human behaviour 5, 1203–1213 (2021).
27. Du, C., Fu, K., Wen, B. & He, H. Topographic representation of visually evoked emotional experiences in the human
cerebral cortex. iScience 26 (2023).
28. Lettieri, G. et al. Dissecting abstract, modality-specific and experience-dependent coding of affect in the human brain.
Sci. advances 10, eadk6840 (2024).
19/48


## Page 20

29. Saarimäki, H. et al. Cerebral topographies of perceived and felt emotions. Imaging Neurosci. 3, 00517 (2025).
30. Cowen, A. S. & Keltner, D. Self-report captures 27 distinct categories of emotion bridged by continuous gradients. Proc.
national academy sciences 114, E7900–E7909 (2017).
31. Cowen, A. S., Fang, X., Sauter, D. & Keltner, D. What music makes us feel: At least 13 dimensions organize subjective
experiences associated with music across different cultures. Proc. Natl. Acad. Sci. 117, 1924–1934 (2020).
32. Hebart, M. N., Zheng, C. Y., Pereira, F. & Baker, C. I. Revealing the multidimensional mental representations of natural
objects underlying human similarity judgements. Nat. human behaviour 4, 1173–1185 (2020).
33. Contier, O., Baker, C. I. & Hebart, M. N. Distributed representations of behaviour-derived object dimensions in the
human visual system. Nat. Hum. Behav. 8, 2179–2193 (2024).
34. Mahner, F. P., Muttenthaler, L., Güçlü, U. & Hebart, M. N. Dimensions underlying the representational alignment of deep
neural networks with humans. Nat. Mach. Intell. 1–12 (2025).
35. Binz, M. et al. A foundation model to predict and capture human cognition. Nature 1–8 (2025).
36. Du, C. et al. Human-like object concept representations emerge naturally in multimodal large language models. Nat.
Mach. Intell. 1–16 (2025).
37. Luo, X. et al. Large language models surpass human experts in predicting neuroscience results. Nat. human behaviour 9,
305–315 (2025).
38. Xu, Q. et al. Large language models without grounding recover non-sensorimotor but not sensorimotor features of human
concepts. Nat. human behaviour 1–16 (2025).
39. Cui, Z., Li, N. & Zhou, H. A large-scale replication of scenario-based experiments in psychology and management using
large language models. Nat. Comput. Sci. 1–8 (2025).
40. Lu, J. G., Song, L. L. & Zhang, L. D. Cultural tendencies in generative AI. Nat. Hum. Behav. 1–10 (2025).
41. Li, M. et al. Language-specific representation of emotion-concept knowledge causally supports emotion inference.
iScience 27 (2024).
42. Schlegel, K., Sommer, N. R. & Mortillaro, M. Large language models are proficient in solving and creating emotional
intelligence tests. Commun. Psychol. 3, 80 (2025).
43. Rubin, M. et al. Comparing the value of perceived human versus AI-generated empathy. Nat. Hum. Behav. 1–15 (2025).
44. Huang, J.-t. et al. Apathetic or empathetic? evaluating LLMs’ emotional alignments with humans. Adv. Neural Inf.
Process. Syst. 37, 97053–97087 (2024).
45. Boji´c, L. et al. Comparing large language models and human annotators in latent content analysis of sentiment, political
leaning, emotional intensity and sarcasm. Sci. reports 15, 11477 (2025).
46. Wang, X., Li, X., Yin, Z., Wu, Y. & Liu, J. Emotional intelligence of large language models. J. Pac. Rim Psychol. 17,
18344909231213958 (2023).
47. Sabour, S., Ghasemzadeh, H., Farhad, A. & Ghazvininejad, M. EmoBench: Evaluating the emotional intelligence of large
language models. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (2024).
48. Li, C. et al. The good, the bad, and why: unveiling emotions in generative AI. In Proceedings of the 41st International
Conference on Machine Learning, 28905–28934 (JMLR.org, 2024).
49. Barsalou, L. W. Grounded cognition. Annu. Rev. Psychol. 59, 617–645 (2008).
50. Barsalou, L. W. Grounded cognition: Past, present, and future. Top. cognitive science 2, 716–724 (2010).
51. LeCun, Y. Do large language models need sensory grounding for meaning and understanding. In Workshop on Philosophy
of Deep Learning, NYU Center for Mind, Brain, and Consciousness and the Columbia Center for Science and Society
(2023).
52. Chemero, A. LLMs differ from human cognition because they are not embodied. Nat. Hum. Behav. 7, 1828–1829 (2023).
53. Dove, G. Symbol ungrounding: what the successes (and failures) of large language models reveal about human cognition.
Philos. Transactions B 379, 20230149 (2024).
54. Niedenthal, P. M. Embodying emotion. science 316, 1002–1005 (2007).
55. Barrett, L. F. & Lindquist, K. A. The embodiment of emotion. Embodied grounding: Social, cognitive, affective,
neuroscientific approaches 237–262 (2008).
20/48


## Page 21

56. Winkielman, P., Coulson, S. & Niedenthal, P. Dynamic grounding of emotion concepts. Philos. Transactions Royal Soc.
B: Biol. Sci. 373, 20170127 (2018).
57. Horikawa, T. Mind captioning: Evolving descriptive text of mental content from human brain activity. bioRxiv 2024–04
(2024).
58. Zheng, C. Y., Pereira, F., Baker, C. I. & Hebart, M. N. Revealing interpretable object representations from human behavior.
In International Conference on Learning Representations (2019).
59. Touvron, H. et al. Llama: Open and efficient foundation language models. arXiv preprint arXiv:2302.13971 (2023).
60. Wang, P. et al. Qwen2-VL: Enhancing vision-language model’s perception of the world at any resolution. arXiv preprint
arXiv:2409.12191 (2024).
61. Kriegeskorte, N., Mur, M. & Bandettini, P. A. Representational similarity analysis-connecting the branches of systems
neuroscience. Front. systems neuroscience 2, 249 (2008).
62. Lettieri, G. et al. Emotionotopy in the human right temporo-parietal cortex. Nat. communications 10, 1–13 (2019).
63. Saxe, R. & Kanwisher, N. People thinking about thinking people: the role of the temporo-parietal junction in “theory of
mind”. In Social neuroscience, 171–182 (Psychology Press, 2013).
64. Decety, J. & Lamm, C. The role of the right temporoparietal junction in social interaction: how low-level computational
processes contribute to meta-cognition. The neuroscientist 13, 580–593 (2007).
65. Schiller, B., Gianotti, L. R., Baumgartner, T. & Knoch, D. Theta resting EEG in the right TPJ is associated with individual
differences in implicit intergroup bias. Soc. cognitive affective neuroscience 14, 281–289 (2019).
66. Kragel, P. A., Reddan, M. C., LaBar, K. S. & Wager, T. D. Emotion schemas are embedded in the human visual system.
Sci. advances 5, eaaw4358 (2019).
67. Gao, C., Ajith, S. & Peelen, M. V. Object representations drive emotion schemas across a large and diverse set of daily-life
scenes. Commun. Biol. 8, 697 (2025).
68. Nassi, J. J. & Callaway, E. M. Parallel processing strategies of the primate visual system. Nat. reviews neuroscience 10,
360–372 (2009).
69. Dukelow, S. P. et al. Distinguishing subregions of the human mt+ complex using visual fields and pursuit eye movements.
J. neurophysiology 86, 1991–2000 (2001).
70. Huk, A. C., Dougherty, R. F. & Heeger, D. J. Retinotopy and functional subdivision of human areas MT and MST. J.
Neurosci. 22, 7195–7205 (2002).
71. Selvaraju, R. R. et al. Grad-CAM: Visual explanations from deep networks via gradient-based localization. In Proceedings
of the IEEE international conference on computer vision, 618–626 (2017).
72. Barrett, L. F. & Bliss-Moreau, E. Affect as a psychological primitive. Adv. experimental social psychology 41, 167–218
(2009).
73. Chatterjee, A. & Vartanian, O. Neuroaesthetics. Trends cognitive sciences 18, 370–375 (2014).
74. Nadal, M. & Pearce, M. T. The copenhagen neuroaesthetics conference: prospects and pitfalls for an emerging field.
Brain cognition 76, 172–183 (2011).
75. Kringelbach, M. L. & Berridge, K. C. The neuroscience of happiness and pleasure. Soc. Res. An Int. Q. 77, 659–678
(2010).
76. Lambert, L., Passmore, H.-A. & Holder, M. D. Foundational frameworks of positive psychology: Mapping well-being
orientations. Can. Psychol. Can. 56, 311 (2015).
77. Ulrich, M., Keller, J., Hoenig, K., Waller, C. & Grön, G. Neural correlates of experimentally induced flow experiences.
Neuroimage 86, 194–202 (2014).
78. Van Veen, V., Krug, M. K., Schooler, J. W. & Carter, C. S. Neural activity predicts attitude change in cognitive dissonance.
Nat. neuroscience 12, 1469–1474 (2009).
79. Colosio, M., Shestakova, A., Nikulin, V. V., Blagovechtchenski, E. & Klucharev, V. Neural mechanisms of cognitive
dissonance (revised): An eeg study. J. Neurosci. 37, 5074–5083 (2017).
80. Georgiadis, J. R. & Kringelbach, M. L. The human sexual response cycle: brain imaging evidence linking sex to other
pleasures. Prog. neurobiology 98, 49–81 (2012).
21/48


## Page 22

81. Panksepp, J.
Affective neuroscience of the emotional brainmind: evolutionary perspectives and implications for
understanding depression. Dialogues clinical neuroscience 12, 533–545 (2010).
82. LeDoux, J. E. Emotion circuits in the brain. Fear anxiety 259–288 (2013).
83. Bender, E. M., Gebru, T., McMillan-Major, A. & Shmitchell, S. On the dangers of stochastic parrots: Can language
models be too big? In Proceedings of the 2021 ACM conference on fairness, accountability, and transparency, 610–623
(2021).
84. Wang, A. Y., Kay, K., Naselaris, T., Tarr, M. J. & Wehbe, L. Better models of human high-level visual cortex emerge
from natural language supervision with a large and diverse dataset. Nat. Mach. Intell. 5, 1415–1426 (2023).
85. Sartzetaki, C., Roig, G., Snoek, C. G. & Groen, I. I. One hundred neural networks and brains watching videos: Lessons
from alignment. In The Thirteenth International Conference on Learning Representations (2025).
86. Conwell, C., Prince, J. S., Kay, K. N., Alvarez, G. A. & Konkle, T. A large-scale examination of inductive biases shaping
high-level visual representation in brains and machines. Nat. communications 15, 9383 (2024).
87. Antonello, R., Vaidya, A. & Huth, A. Scaling laws for language encoding models in fMRI. Adv. Neural Inf. Process. Syst.
36, 21895–21907 (2023).
88. Conwell, C., Graham, D., Boccagno, C. & Vessel, E. A. The perceptual primacy of feeling: Affectless visual machines
explain a majority of variance in human visually evoked affect. Proc. Natl. Acad. Sci. 122, e2306025121 (2025).
89. Antonello, R. et al. A generative framework to bridge data-driven models and scientific theories in language neuroscience.
arXiv preprint arXiv:2410.00812 (2024).
90. Bartnik, C. G. et al. Representation of locomotive action affordances in human behavior, brains, and deep neural networks.
Proc. Natl. Acad. Sci. 122, e2414005122 (2025).
91. Asanuma, H. et al. Correspondence of high-dimensional emotion structures elicited by video clips between humans and
multimodal LLMs. Sci. reports 15, 32175 (2025).
92. Wang, X., Men, W., Gao, J., Caramazza, A. & Bi, Y. Two forms of knowledge representations in the human brain. Neuron
107, 383–393 (2020).
93. Kim, J. S., Aheimer, B., Montané Manrara, V. & Bedny, M. Shared understanding of color among sighted and blind
adults. Proc. Natl. Acad. Sci. 118, e2020192118 (2021).
94. Abdel-Ghaffar, S. A. et al. Occipital-temporal cortical tuning to semantic and affective features of natural images predicts
associated behavioral responses. Nat. Commun. 15, 5531 (2024).
95. Lai, W., Xie, H., Xu, G., Li, Q. & Qin, S. J. When LLMs team up: The emergence of collaborative affective computing.
arXiv preprint arXiv:2506.01698 (2025).
96. Ishikawa, S.-n. & Yoshino, A. AI with emotions: Exploring emotional expressions in large language models. arXiv
preprint arXiv:2504.14706 (2025).
97. Zhao, B. et al. Emergence of hierarchical emotion representations in large language models. In NeurIPS Workshop on
Scientific Methods for Understanding Deep Learning.
98. Chen, Y. et al.
Emotionqueen: A benchmark for evaluating empathy of large language models.
arXiv preprint
arXiv:2409.13359 (2024).
99. Huang, J.-t. et al. Emotionally numb or empathetic? evaluating how LLMs feel using emotionbench. arXiv preprint
arXiv:2308.03656 (2023).
100. Ren, Y., Jin, R., Zhang, T. & Xiong, D. Do large language models mirror cognitive language processing? arXiv preprint
arXiv:2402.18023 (2024).
101. Spezialetti, M., Placidi, G. & Rossi, S. Emotion recognition for human-robot interaction: Recent advances and future
perspectives. Front. Robotics AI 7, 532279 (2020).
102. Stock-Homburg, R. Survey of emotions in human–robot interactions: Perspectives from robotic psychology on 20 years
of research. Int. J. Soc. Robotics 14, 389–411 (2022).
103. Ben-Zion, Z. et al. Assessing and alleviating state anxiety in large language models. npj Digit. Medicine 8, 132 (2025).
104. Inzlicht, M., Cameron, C. D., D’Cruz, J. & Bloom, P. In praise of empathic AI. Trends Cogn. Sci. 28, 89–91 (2024).
105. Cowen, A. S. et al. How emotion is experienced and expressed in multiple cultures: a large-scale experiment across north
america, europe, and japan. Front. Psychol. 15, 1350631 (2024).
22/48


## Page 23

106. Shiota, M. N., Neufeld, S. L., Yeung, W. H., Moser, S. E. & Perea, E. F. Feeling good: autonomic nervous system
responding in five positive emotions. Emotion 11, 1368 (2011).
107. Shiota, M. et al. Beyond happiness: Toward a science of discrete positive emotions. Manuscr. accepted for publication
Am. Psychol. (2013).
108. Fredrickson, B. L. What good are positive emotions? Rev. general psychology 2, 300–319 (1998).
109. Rozin, P. & Cohen, A. B. High frequency of facial expressions corresponding to confusion, concentration, and worry in
an analysis of naturally occurring facial expressions of americans. Emotion 3, 68 (2003).
110. Chen, X. et al. Microsoft coco captions: Data collection and evaluation server. arXiv preprint arXiv:1504.00325 (2015).
111. Team, Q. Qwen2 technical report. arXiv preprint arXiv:2412.15115 (2024).
112. Liu, Z. et al. SynthVLM: High-efficiency and high-quality synthetic data for vision language models. arXiv preprint
arXiv:2407.20756 (2024).
113. Guo, D. et al. Deepseek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning. arXiv preprint
arXiv:2501.12948 (2025).
114. Radford, A. et al. Learning transferable visual models from natural language supervision. In International conference on
machine learning, 8748–8763 (PmLR, 2021).
115. He, K., Zhang, X., Ren, S. & Sun, J. Deep residual learning for image recognition. In Proceedings of the IEEE conference
on computer vision and pattern recognition, 770–778 (2016).
116. Tong, Z., Song, Y., Wang, J. & Wang, L. VideoMAE: Masked autoencoders are data-efficient learners for self-supervised
video pre-training. Adv. neural information processing systems 35, 10078–10093 (2022).
117. Esteban, O. et al. fMRIPrep: a robust preprocessing pipeline for functional MRI. Nat. methods 16, 111–116 (2019).
118. Cox, R. W. AFNI: software for analysis and visualization of functional magnetic resonance neuroimages. Comput.
Biomed. research 29, 162–173 (1996).
119. Jenkinson, M., Bannister, P., Brady, M. & Smith, S. Improved optimization for the robust and accurate linear registration
and motion correction of brain images. Neuroimage 17, 825–841 (2002).
120. Greve, D. N. & Fischl, B. Accurate and robust brain image alignment using boundary-based registration. Neuroimage 48,
63–72 (2009).
121. Fischl, B. Freesurfer. Neuroimage 62, 774–781 (2012).
122. Gao, J. S., Huth, A. G., Lescroart, M. D. & Gallant, J. L. Pycortex: an interactive surface visualizer for fMRI. Front.
neuroinformatics 9, 23 (2015).
123. Glasser, M. F. et al. A multi-modal parcellation of human cerebral cortex. Nature 536, 171–178 (2016).
124. Rajalingham, R. et al. Large-scale, high-resolution comparison of the core visual object recognition behavior of humans,
monkeys, and state-of-the-art deep artificial neural networks. J. Neurosci. 38, 7255–7269 (2018).
125. Blondel, V. D., Guillaume, J.-L., Lambiotte, R. & Lefebvre, E. Fast unfolding of communities in large networks. J.
statistical mechanics: theory experiment 2008, P10008 (2008).
126. Brin, S. & Page, L. The anatomy of a large-scale hypertextual web search engine. Comput. networks ISDN systems 30,
107–117 (1998).
Acknowledgements
This work was supported in part by the Strategic Priority Research Program of the Chinese Academy of Sciences (Grant No.
XDB1010202); in part by the National Natural Science Foundation of China under Grant 62020106015 and Grant 62206284;
in part by Beijing Natural Science Foundation under Grant L243016, and in part by the Beijing Nova Program under Grant
20230484460. We would like to thank Alan S. Cowen and Dacher Keltner for sharing the emotionally evocative video database
and the human behavioral ratings on 34 emotion categories and 14 affective dimensions. We also thank Yukiyasu Kamitani and
Tomoyasu Horikawa for sharing the corresponding fMRI data and video captions. We also thank Martin N. Hebart, Jack L.
Gallant, et al. for sharing the code and tools for embedding learning and visualization analysis.
Author contributions
C.D., Y.L. and H.H. designed the research; Y.L., Z.H. and C.D. conducted the experiments; Y.L. and Z.H. collected the data;
Y.L., C.D. and Z.H. wrote the paper; all the authors analyzed the results; all the authors approved the paper.
23/48


## Page 24

Competing interests
The authors declare no competing interests.
Additional information
Correspondence and requests for materials should be addressed to H.H.
Extended data
24/48


## Page 25

1
6
11
16
21
26
31
36
41
Number of Components Retained
0.15
0.2
0.25
0.3
0.35
0.4
0.45
0.5
0.55
0.6
0.65
0.7
0.75
0.8
0.85
0.9
0.95
1
Representational similarity score
Prediction of measured RSM
LLM
MLLM
Human category
Human dimension
0
10
20
30
Human (category) component number
0
0.2
0.4
0.6
0.8
1
Reproducibility score
0
10
20
30
Human (dimension) component number
0
0.2
0.4
0.6
0.8
1
Reproducibility score
0
10
20
30
LLM component number
0
0.2
0.4
0.6
0.8
1
Reproducibility score
0
10
20
30
MLLM component number
0
0.2
0.4
0.6
0.8
1
Reproducibility score
30
35
40
45
50
55
60
65
70
75
80
85
90
95
100
Odd-one-out accuracy (%)
 noise celling
chance
LLM
MLLM
Human category
Human dimension
Predicted Human
category RSM
Measured Human
category RSM
0
0.5
1
0
0.5
1
predicted similarity
0
0.5
1
Model fit
measured similarity
R = 0.96
66 diverse videos
Predicted Human
dimension RSM
66 diverse videos
Measured Human
dimension RSM
0
0.5
1
0
0.5
1
predicted similarity
0
0.5
1
measured similarity
Model fit
R = 0.94
Predicted LLM RSM
66 diverse videos
Measured LLM RSM
0
0.5
1
0
0.5
1
predicted similarity
0
0.5
1
measured similarity
Model fit
R = 0.83
Predicted MLLM RSM
66 diverse videos
Measured MLLM RSM
0
0.5
1
0
0.5
1
predicted similarity
0
0.5
1
measured similarity
Model fit
R = 0.85
a
b
c
d
e
f
g
h
i
j
Extended Data Fig. 1. Learned affective embeddings are stable and predictive. a, Effect of dimensionality on the ability
of embeddings to predict held-out similarity judgments, showing performance saturation at approximately 30 components. b-e,
Reproducibility of the 30 learned components across ten independent model runs. Each point is the maximum correlation of a
component from one run with all components from the other runs. Shaded areas represent 95% confidence intervals (CIs). f,
Prediction accuracy of the 30-dimensional embeddings on a held-out set of triplet choices. Noise ceilings (upper bound of
performance) were estimated from trial-to-trial reliability (across 10,000 triplets). Error bars are 95% CIs. g-j, Comparison of
RSMs for 66 validation stimuli. Left: RSMs predicted by the learned embeddings. Middle: RSMs measured from empirical
behavioral choices (unavailable in the SPoSE training). Right: Pearson’s correlation between predicted and measured RSMs,
indicating high global correspondence.
Supplementary information
25/48


## Page 26

Extended Data Table 1. Affective labels for the 30 learned latent components. Labels were assigned by correlating each
learned component with human ratings on 34 emotion categories and 14 affective dimensions from Cowen et al.30. For each
component, the top three most correlated terms are shown with their Pearson correlation coefficient in parentheses.
Component
Human (category)
Human (dimension)
LLM (Llama 3.1)
MLLM (Qwen2-VL)
1
amusement (0.977)
approach (0.867), safety (0.855), valence (0.839)
valence (0.612), upswing (0.580), amusement (0.544)
aesthetic appreciation (0.672), calmness (0.594)
2
interest (0.975)
valence (0.486), aesthetic appreciation (0.472), control (0.463) control (-0.775), valence (-0.770), approach (-0.770)
romance (0.538)
3
awe (0.977)
dominance (0.714)
aesthetic appreciation (0.490), entrancement (0.465), interest (0.402)
control (-0.306), safety (-0.287), surprise (0.265)
4
aesthetic appreciation (0.976) valence (-0.832), control (-0.807), upswing (-0.802)
excitement (0.490), anxiety (0.454), fear (0.399)
nostalgia (0.318), awkwardness (0.283), identity (0.244)
5
surprise (0.974)
arousal (0.506), upswing (0.465), attention (0.375)
adoration (0.590)
triumph (0.501)
6
disgust (0.975)
anxiety (0.666), safety (-0.660), fear (0.634)
romance (0.730), sexual desire (0.699)
adoration (0.226), calmness (0.193), safety (0.184)
7
fear (0.978)
dominance (0.462), certainty (0.384), obstruction (-0.322)
amusement (0.474)
adoration (0.398), joy (0.377)
8
joy (0.981)
effort (-0.464)
boredom (0.288), awkwardness (0.286), arousal (-0.250)
contempt (0.053), dominance (0.051)
9
confusion (0.976)
identity (0.251), certainty (0.250), control (0.233)
sympathy (0.361), relief (0.339), commitment (0.288)
craving (0.794)
10
horror (0.975)
upswing (0.464)
sadness (0.584)
romance (0.610), sexual desire (0.598)
11
adoration (0.978)
commitment (0.324), attention (0.323)
triumph (0.379)
safety (-0.268), fear (0.256), control (-0.238)
12
boredom (0.983)
certainty (-0.188), fairness (0.172), attention (0.150)
awe (0.132), joy (0.118), commitment (0.103)
sexual desire (0.504)
13
anxiety (0.958)
amusement (0.302), upswing (0.291), effort (-0.282)
empathic pain (0.362), sympathy (0.283), control (-0.219)
sympathy (0.120), disappointment (0.107), sadness (0.104)
14
sexual desire (0.634)
arousal (-0.450), safety (0.392), control (0.378)
entrancement (0.299), aesthetic appreciation (0.284), interest (0.245)
admiration (0.181), amusement (0.145), triumph (0.126)
15
excitement (0.975)
attention (0.257), control (0.206), fairness (0.195)
joy (0.120), amusement (0.104), commitment (0.095)
pride (0.227), triumph (0.155), admiration (0.109)
16
sadness (0.975)
control (0.290), sexual desire (0.236), effort (-0.166)
nostalgia (0.250)
boredom (0.278), arousal (-0.215), nostalgia (0.188)
17
sexual desire (0.973)
approach (-0.387), safety (-0.386), commitment (-0.377)
disgust (0.310), horror (0.310), upswing (-0.306)
contempt (0.281), disappointment (0.189), arousal (-0.167)
18
entrancement (0.973)
certainty (0.409)
surprise (0.119), commitment (-0.090), certainty (-0.086)
nostalgia (0.557)
19
satisfaction (0.964)
effort (0.386)
sadness (0.280), sympathy (0.233), fairness (-0.187)
disgust (0.161), attention (-0.127)
20
calmness (0.974)
approach (0.328), certainty (0.327), control (0.289)
safety (-0.191), approach (-0.180), control (-0.177)
horror (0.299)
21
nostalgia (0.982)
identity (0.409), arousal (-0.368), attention (-0.293)
surprise (0.084), triumph (0.078), admiration (0.062)
anger (0.271), disappointment (0.212), control (-0.181)
22
admiration (0.970)
commitment (-0.264), approach (-0.210)
identity (0.097), nostalgia (0.090), admiration (0.082)
entrancement (0.484), interest (0.448)
23
awkwardness (0.976)
approach (-0.445), control (-0.439), obstruction (0.402)
relief (0.134), fairness (-0.086), safety (-0.083)
adoration (0.632)
24
sympathy (0.955)
attention (-0.228), certainty (0.205), arousal (0.152)
triumph (0.063), amusement (0.055), identity (0.050)
fear (0.360), safety (-0.357), control (-0.354)
25
romance (0.979)
dominance (-0.482)
awe (0.121), fairness (0.110), valence (0.097)
romance (0.199), control (0.196), safety (0.194)
26
empathic pain (0.969)
certainty (-0.472), effort (0.457), valence (-0.403)
approach (-0.234), identity (-0.214), safety (-0.190)
awe (0.206), interest (0.180)
27
triumph (0.972)
attention (-0.560), arousal (-0.466), disgust (0.425)
admiration (0.224)
anxiety (0.400), excitement (0.373), fear (0.322)
28
craving (0.970)
safety (-0.238), certainty (-0.230), valence (-0.180)
safety (-0.136), control (-0.123), fairness (-0.113)
anger (0.460), fairness (-0.456), horror (0.447)
29
relief (0.976)
sadness (0.529), sympathy (0.490), fairness (-0.390)
safety (-0.138), fear (0.127), control (-0.116)
disgust (0.266), effort (0.207), valence (-0.173)
30
anger (0.865)
safety (0.236), attention (-0.163)
aesthetic appreciation (0.102), commitment (-0.098), approach (-0.095) anxiety (0.474), fear (0.397)
26/48


## Page 27

Extended Data Table 2. Description and composition of affective clusters. Affective clusters were identified by applying
the Louvain community detection algorithm to the component-by-component correlation graphs (see Fig. 7). This table
provides a descriptive name for each cluster, a brief summary of its core affective theme, and the corresponding component IDs
that belong to it for each of the four systems.
Clusters
Descriptions
LLM
MLLM
Human (cat.)
Human (dim.)
High-arousal
negative affect
This cluster represents content eliciting
strong physiological/psychological responses
(tension, anxiety, sexual arousal) while evoking
negative affect or cognitive dissonance: horror or
suspense scenarios (anxiety, empathy, high
approach), moral/social conflicts (disgust,
embarrassment, confusion), or sexual
desire with subjective discomfort.
2, 13,
17, 19,
20
3, 11,
13, 21,
28
5, 6, 7, 10,
13, 16, 24,
26, 29, 30
4, 6, 9, 12,
15, 17, 19,
22, 23, 26,
27, 28
Delight
This cluster is characterized by positive affect
(amusement, interest, contentment) and
sexual desire as core features, with content
likely exhibiting high hedonic value,
attractiveness, or romantic qualities,
eliciting approach rather than avoidance
tendencies in subjects.
22, 25
Nan
1, 3, 8, 11
1, 2, 3, 5,
7, 8, 10, 13,
14, 20, 21
Affective
Dissonance
This cluster captures paradoxical emotional
blends where reward-driven states
(amusement, sexual desire) collide with
threat responses (anxiety, awkwardness).
1, 5,
7, 26
6, 7,
12, 19,
23, 26
Nan
11, 16, 18, 24,
29, 30
Achievement
and
Glorification
This cluster reflects amplified positive
emotions after accomplishing goals, blending
triumph (pride, excitement) with social
validation needs, alongside high attention and
self-confidence, typically seen in competitive
wins or professional successes.
Nan
4, 5,
15, 24
15, 19, 22, 27
Nan
Erotic
This cluster predominantly comprises stimuli
associated with romance and sexual desire,
characterized by high valence and
approach-related motivational tendencies.
Nan
1, 2,
10, 25
14, 17, 25, 28
Nan
Attentional
Immersion
This cluster comprises stimuli from extreme sports,
animated scenes, culinary content, and sexual
cues that elicit strong attentional engagement
and cognitive absorption, characterized by
flow-state induction and sustained focus.
14, 16
9, 22
Nan
Nan
Aesthetic
Contemplation
This cluster reveals a distinct affective response
pattern to scenic nature, high art and slow-paced
content, characterized by sustained aesthetic
immersion requiring cognitive engagement
rather than immediate pleasure or
negative avoidance.
Nan
Nan
2, 4, 18, 20
Nan
Empathy-
related
This cluster predominantly features content eliciting
empathic distress and compassion in response
to harmed animals or humans, characterized
by affective resonance with suffering.
8, 9, 10
Nan
Nan
Nan
Vigilant
Passivity
This cluster comprises paradoxical states blending
low-arousal calmness with covert
threat monitoring.
Nan
16, 17,
20
Nan
Nan
High Arousal
This cluster captures intense emotional responses
elicited by extreme sports, recreational activities,
or hazardous events (e.g., natural disasters,
accidents), characterized by heightened arousal.
Nan
10, 27,
30
Nan
Nan
27/48


## Page 28

Thalamus
Hippocampus
Pallidum
Caudate
Putamen
Nucleus accumbens
Amygdala
Cerebellum
Hypothalamus
Brainstem
0.000
0.005
0.010
0.015
0.020
0.025
0.030
0.035
Subcortical RSA score
SPoSE-derived (cat.)
Self-reported (cat.)
SPoSE-derived (dim.)
Self-reported (dim.)
*
*
VC
ACC
Insula
IPL
MST
MTC
OFC
PC
STS
TE
TF
TPJ
DLPFC
DMPFC
VLPFC
VMPFC
0.00
0.02
0.04
0.06
0.08
0.10
0.12
Cortical Surface RSA score
*
*
*
*
*
*
*
*
0
0.1
0.2
0.3
SPoSE Performance (r)
0
0.1
0.2
0.3
Raw Performance (r)
Searchlight RSA
Human (cat.) level
100
101
102
103
104
105
0
0.1
0.2
0.3
SPoSE Performance (r)
0
0.1
0.2
0.3
Raw Performance (r)
Searchlight RSA
Human (dim.) level
100
101
102
103
104
105
Thalamus
Hippocampus
Pallidum
Caudate
Putamen
Nucleus accumbens
Amygdala
Cerebellum
Hypothalamus
Brainstem
0.00
0.01
0.02
0.03
0.04
0.05
0.06
0.07
0.08
Subcortical Encoding score
SPoSE-derived (cat.)
Self-reported (cat.)
SPoSE-derived (dim.)
Self-reported (dim.)
VC
ACC
Insula
IPL
MST
MTC
OFC
PC
STS
TE
TF
TPJ
DLPFC
DMPFC
VLPFC
VMPFC
0.00
0.05
0.10
0.15
0.20
Cortical Surface Encoding score
*
*
*
*
0
0.2
0.4
0.6
SPoSE Performance (r)
0
0.2
0.4
0.6
Raw Performance (r)
Voxel-wise Encoding
Human (cat.) level
100
101
102
103
104
105
0
0.2
0.4
0.6
SPoSE Performance (r)
0
0.2
0.4
0.6
Raw Performance (r)
Voxel-wise Encoding
Human (dim.) level
100
101
102
103
104
105
a
b
c
d
e
f
Extended Data Fig. 2. SPoSE-derived human embeddings show comparable neural alignment to original self-report
ratings. a, b, Comparison of neural alignment using searchlight RSA, averaged across subcortical (a) and cortical (b) ROIs. c,
d, Comparison of neural alignment using voxel-wise encoding, averaged across subcortical (c) and cortical (d) ROIs.
Performance (Pearson’s r) is averaged across subjects (N=5), with individual subjects shown as dots and error bars representing
standard deviation (s.d.). The results indicate that the performance of the SPoSE-derived human embeddings is comparable to
their corresponding self-report rating vector counterparts, with few statistically significant differences observed (marked by
stars, P < 0.05, FDR corrected). e, f, 2D histogram comparison for a representative subject (Subject 1), plotting the
performance of the SPoSE-derived human embeddings against the original self-report ratings. Results are shown for both
searchlight RSA (e) and voxel-wise encoding (f). The voxels are distributed symmetrically around the identity line, indicating
that both methods capture neural information to a similar degree across the brain.
28/48


## Page 29

Thalamus
Hippocampus
Pallidum
Caudate
Putamen
Nucleus accumbens
Amygdala
Cerebellum
Hypothalamus
Brainstem
0.00
0.01
0.02
0.03
0.04
0.05
0.06
0.07
Subcortical Encoding score
LLM
MLLM
Human (category)
Human (dimension)
Human (concat)
*
*
*
VC
ACC
Insula
IPL
MST
MTC
OFC
PC
STS
TE
TF
TPJ
DLPFC
DMPFC
VLPFC
VMPFC
0.00
0.05
0.10
0.15
0.20
0.25
Cortical Surface Encoding score
* ***
***
*
*
*
* ***
* ***
*
*
*
*
* ***
* ***
* ***
***
***
*
*
0
0.2
0.4
0.6
Human (cat.) Performance (r)
0
0.2
0.4
0.6
MLLM Performance (r)
Voxel-wise Encoding
Human (cat.) level
110% Human (cat.) level
100
101
102
103
104
105
0
0.2
0.4
0.6
Human (dim.) Performance (r)
0
0.2
0.4
0.6
MLLM Performance (r)
Voxel-wise Encoding
Human (dim.) level
160% Human (dim.) level
100
101
102
103
104
105
0
0.2
0.4
0.6
Human (concat) Performance (r)
0
0.2
0.4
0.6
MLLM Performance (r)
Voxel-wise Encoding
Human (concat) level
110% Human (concat) level
100
101
102
103
104
105
0.00
0.20
0.40
0.60
Voxel-wise Encoding (r)
Subject 1
(All coloured voxels
P < 0.05, FDR corrected)
MLLM
LLM
Human (cat.)
Human (dim.)
a
b
c
d
Extended Data Fig. 3. Results of voxel-wise encoding. Prediction accuracy (Pearson’s r) averaged for subcortical (a) and
cortical (b) ROIs (averaged across subjects (N=5)). Dots represent individual subjects; error bars reflect standard deviation; all
statistics are two-tailed t-tests across subjects, with FDR correction; stars indicate significant differences between MLLM and
the compared model (P < 0.05). c, Flattened cortical maps of voxel-wise encoding accuracy (Pearson’s r) for Subject 1. All
coloured voxels are predicted significantly (P < 0.05, FDR-corrected, two-tailed t-tests). d, Voxel-wise comparison of the
MLLM’s performance against the human categorical, dimensional and concatenated ratings model for Subject 1.
29/48


## Page 30

Extended Data Fig. 4. Results of searchlight RSA and voxel-wise encoding for Subject 2. a, b Flattened cortical maps of
searchlight RSA (a) and voxel-wise encoding (b). All coloured voxels are predicted significantly (P < 0.05, FDR-corrected,
two-tailed t-tests). c, d, Voxel-wise comparison of the MLLM’s performance against the human categorical, dimensional and
concatenated ratings model, using searchlight RSA (c) and voxel-wise encoding (d).
30/48


## Page 31

Extended Data Fig. 5. Results of searchlight RSA and voxel-wise encoding for Subject 3. a, b Flattened cortical maps of
searchlight RSA (a) and voxel-wise encoding (b). All coloured voxels are predicted significantly (P < 0.05, FDR-corrected,
two-tailed t-tests). c, d, Voxel-wise comparison of the MLLM’s performance against the human categorical, dimensional and
concatenated ratings model, using searchlight RSA (c) and voxel-wise encoding (d).
31/48


## Page 32

Extended Data Fig. 6. Results of searchlight RSA and voxel-wise encoding for Subject 4. a, b Flattened cortical maps of
searchlight RSA (a) and voxel-wise encoding (b). All coloured voxels are predicted significantly (P < 0.05, FDR-corrected,
two-tailed t-tests). c, d, Voxel-wise comparison of the MLLM’s performance against the human categorical, dimensional and
concatenated ratings model, using searchlight RSA (c) and voxel-wise encoding (d).
32/48


## Page 33

Extended Data Fig. 7. Results of searchlight RSA and voxel-wise encoding for Subject 5. a, b Flattened cortical maps of
searchlight RSA (a) and voxel-wise encoding (b). All coloured voxels are predicted significantly (P < 0.05, FDR-corrected,
two-tailed t-tests). c, d, Voxel-wise comparison of the MLLM’s performance against the human categorical, dimensional and
concatenated ratings model, using searchlight RSA (c) and voxel-wise encoding (d).
33/48


## Page 34

Extended Data Fig. 8. Neural correlates of specific MLLM affective components. This figure shows the brain activation
patterns triggered by three distinct, interpretable affective components from the MLLM, generated from the weights of the
voxel-wise encoding models. Each row displays the results for a single subject (S1–S5), and each column corresponds to a
specific component (e.g., nostalgia, sexual desire, anger). Red indicates positive weights, reflecting brain regions where
activity is positively associated with the affective component; blue indicates negative weights, reflecting regions with a negative
association. The high degree of consistency in the spatial patterns across all five subjects suggests that these learned affective
components capture neurally meaningful and stable components of emotion processing.
34/48


## Page 35

Extended Data Fig. 9. Visualization of learned affective components 1–10 for the LLM and MLLM (related to Fig. 3).
For each component, we display its assigned affective label(s) and the six video frames that received the highest weight.
35/48


## Page 36

Extended Data Fig. 10. Visualization of learned affective components 11–20 for the LLM and MLLM (related to Fig.
3). For each component, we display its assigned affective label(s) and the six video frames that received the highest weight.
36/48


## Page 37

Extended Data Fig. 11. Visualization of learned affective components 21–30 for the LLM and MLLM (related to Fig.
3). For each component, we display its assigned affective label(s) and the six video frames that received the highest weight.
37/48


## Page 38

Extended Data Fig. 12. Visualization of learned affective components 1–10 for human-category and
human-dimension (related to Fig. 3). For each component, we display its assigned affective label(s) and the six video frames
that received the highest weight.
38/48


## Page 39

Extended Data Fig. 13. Visualization of learned affective components 11–20 for human-category and
human-dimension (related to Fig. 3). For each component, we display its assigned affective label(s) and the six video frames
that received the highest weight.
39/48


## Page 40

Extended Data Fig. 14. Visualization of learned affective components 21–30 for human-category and
human-dimension (related to Fig. 3). For each component, we display its assigned affective label(s) and the six video frames
that received the highest weight.
40/48


## Page 41

Extract 
video frames
CLIP 
vision 
encoder
…
…
Averaged 
CLIP feature
Linear projection
SPoSE feature
…
…
Extract Gradients for dimension j 
Superimpose
Dimension j
Extended Data Fig. 15. Schematic of the Grad-CAM attribution method. To identify the visual drivers for any given
affective component, we first trained a linear projection from CLIP visual features to the learned SPoSE embeddings. For a
target component (j), we then compute the gradient of its activation with respect to the input video frames. These gradients are
used to generate saliency heatmaps that highlight the specific image regions responsible for activating the component. The
snowflake and flame symbols denote frozen and trainable parameters, respectively.
41/48


## Page 42

Extended Data Fig. 16. Framework for generative editing of video emotion via dimensional manipulation.. a,
Motivation and feasibility of emotion editing. Affective states constitute integrated products of semantic information
processing, establishing profound connections between emotion space and semantic space. This linkage enables generative
emotion editing through cross-space mapping, as exemplified by semantically distant concepts—such as "a child sliding on a
playground" versus "dogs playing together"—converging in emotion space due to shared affective qualities (e.g., amusement
clustering). b, raining pipeline for the emotion projector. The emotion projector is trained end-to-end through simultaneous
optimization of: (1) contrastive learning loss aligning SPoSE-derived emotion embeddings with CLIP’s latent space, and (2)
mean squared error (MSE) loss synchronizing these projections with raw textual features, collectively enabling granular
emotion editing. c, Inference pipeline for video editing. The editing pipeline begins with DDIM inversion of original videos
into noise preserving temporal priors (VQVAE encoder omitted), followed by controlled modification of emotion embedding
dimensions. These edited embeddings are transformed into semantic tokens by the trained projector and, together with the
inverted noise, guide Stable Diffusion (v1.5) to synthesize edited frames in latent space before VQVAE decoder-based
pixel-space reconstruction.
42/48


## Page 43

'Now we need to perform a role-playing task. Your 
role is an expert in analyzing the emotions conveyed 
in videos. Firstly, please describe the content and your 
evoked emotional response of the video. '
'Then, report whether you can perceive the emotion of 
"Fear, safety-low, control-low" from this video. If so, 
rate its intensity on a scale from 1 to 10, with a higher 
score indicating a greater degree of intensity. Otherwise, 
simply respond with "No."  Explain the reasons for this 
result. '
Prompt:
Response (Qwen2-VL 7B):
 'The video depicts a scene of a vehicle driving through 
a desert landscape, with a large explosion occurring in 
the background. The explosion is quite intense, with a 
large amount of debris and smoke being thrown into the 
air. The vehicle appears to be moving quickly, and there 
is a sense of urgency and danger in the scene.
Based on this description, I would say that the video 
conveys a strong sense of fear and low safety. The 
explosion is quite dramatic and intense, and the vehicle 
appears to be in danger of being caught in the blast. The 
sense of urgency and danger is heightened by the fact 
that the vehicle is moving quickly, and there is a sense of 
the explosion happening in the background.
On a scale from 1 to 10, I would rate the intensity of the 
"Fear, safety-low, control-low" conveyed in the video as 
a 9. The explosion is quite dramatic and intense, and the 
sense of danger is palpable. The vehicle appears to be in 
immediate danger, and there is a sense of urgency and 
tension in the scene. Overall, the video is quite effective 
in conveying a strong sense of fear. '
'Now we need to perform a role-playing task. Your 
role is an expert in analyzing the emotions conveyed 
in videos. Firstly, please describe the content and your 
evoked emotional response of the video. '
'Then, report whether you can perceive the emotion of 
"Fear, safety-low, control-low" from this video. If so, 
rate its intensity on a scale from 1 to 10, with a higher 
score indicating a greater degree of intensity. Otherwise, 
simply respond with "No."  Explain the reasons for this 
result. '
Prompt:
Response (Qwen2-VL 7B):
 'The video depicts a serene scene of a person 
standing next to a white SUV parked on a road with 
a beautiful sunset in the background. The colors of 
the sky are warm and inviting, and the overall 
atmosphere is peaceful and calm. As an expert in 
analyzing emotions conveyed in videos, I would 
describe my emotional response to this video as one 
of tranquility and contentment.
Regarding the perception of the emotion of "Fear, 
safety-low, control-low" I do not perceive any fear 
and low-safety in this video. The scene is peaceful 
and serene, with no indication of any danger or 
threat. The sunset and the natural surroundings 
evoke a sense of calm and relaxation, rather than 
fear or anxiety. Therefore, I would rate the intensity 
of the emotion  as 0 on a scale from 1 to 10.'
Modify the value of 
the 'Fear, safety-
low, control-low' 
component in the 
emotional space 
from 0.857 to 0.200.
Extended Data Fig. 17. Closed-loop validation of emotion editing: removing ‘Fear’. The MLLM’s judgments confirm
the successful manipulation of affective content. Left, The original video elicits a fear response from the MLLM. Right, After
editing to reduce the ‘Fear, safety-low, control-low’ component’s activation from 0.857 to 0.2, the visual elements driving fear
(dust, explosion) are removed, and the MLLM no longer reports fear when analyzing the edited video.
43/48


## Page 44

'Now we need to perform a role-playing task. Your 
role is an expert in analyzing the emotions conveyed 
in videos. Firstly, please describe the content and your 
evoked emotional response of the video. '
'Then, report whether you can perceive the emotion of 
"Anger, disappointment, control-low" from this video. 
If so, rate its intensity on a scale from 1 to 10, with a 
higher score indicating a greater degree of intensity. 
Otherwise, simply respond with "No."  Explain the 
reasons for this result. '
Prompt:
Response (Qwen2-VL 7B):
 'The video depicts a group of people standing in a 
room, with some individuals appearing to be engaged 
in a conversation or an activity. The overall 
atmosphere seems to be one of social interaction, 
possibly a gathering or a party. The black and white 
filter gives it a vintage or nostalgic feel.
Regarding the perception of emotion, I do not 
perceive any strong emotion of anger or control-low 
in this video. The body language and facial 
expressions of the individuals do not indicate any 
signs of anger or aggression. The scene appears to be 
calm and relaxed, with no visible signs of conflict or 
tension. Therefore, I would rate the intensity of 
emotion in this video as 0 on a scale from 1 to 10. '
'Now we need to perform a role-playing task. Your 
role is an expert in analyzing the emotions conveyed 
in videos. Firstly, please describe the content and your 
evoked emotional response of the video. '
'Then, report whether you can perceive the emotion of 
"Anger, disappointment, control-low" from this video. 
If so, rate its intensity on a scale from 1 to 10, with a 
higher score indicating a greater degree of intensity. 
Otherwise, simply respond with "No."  Explain the 
reasons for this result. '
Prompt:
Response (Qwen2-VL 7B):
 'The video depicts a group of police officers in a 
confrontational stance, holding batons and shields, 
and engaging in a physical altercation with a crowd 
of protesters. The scene is chaotic and tense, with the 
officers and protesters both appearing to be in a state 
of heightened emotion.
Based on the visual cues and the context of the video, 
I can perceive the emotion of anger. The intensity of 
this emotion is rated at a 9 on the scale from 1 to 10. 
The reasons for this result include the physical 
altercation, the aggressive postures of the officers and 
protesters, and the overall chaotic atmosphere of the 
scene. The anger is likely due to the conflict between 
the police and the protesters, who may be expressing 
their anger and frustration at the police actions.'
Modify the value of 
the 'Anger, 
disappointment, 
control-low' 
component in the 
emotional space from 
0.003 to 0.800.
Extended Data Fig. 18. Closed-loop validation of emotion editing: adding ‘Anger’. In this experiment, we evaluated the
emotional perception capabilities of an MLLM. Specifically, the MLLM was presented with a video, and its emotional
perception was measured (Left). By modifying the ‘Anger, disappointment, control-low’ component value of the video from
0.003 to 0.8, the original crowd scene was transformed into police suppressing riots (Right). The results indicate that the
MLLM exhibited strong anger detection when processing the manipulated video.
44/48


## Page 45

Extended Data Fig. 19. Additional examples of generative emotion editing. These examples further demonstrate the
precise control over visual content afforded by manipulating single affective components. Each panel shows the original
frames, the target component and its activation value, and the resulting edited frames. The manipulations showcase a wide
range of transformations.
45/48


## Page 46

ResNet50
ResNet50_EMO
ViT
VideoMAE
CLIP_vision
CLIP_text
CLIP_Video_finetuned
Qwen2-VL_2B
Qwen2.5_7B_instruct
Qwen2_7B_emotion
Qwen2-VL_7B
DeepSeek_R1_7B
Llama3.1_8B
Llama3.1_8B_empathy
Llama3.2-vision_11B
DeepSeek-R1_32B
DeepSeek-R1_70B
Llama3.1_70B
Qwen2-VL_72B
Llama3.1_405B
DeepSeek-R1_671B
ChatGPT4o_mini
0.0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
Human consistency measured by RSA
Compared with Human Categorical Rating
Compared with Human Dimensional Rating
Extended Data Fig. 20. Model scale, specialized training, and multimodality drive human alignment. Behavioral
alignment of 22 AI models with human similarity judgments on the odd-one-out task. Models vary in architecture, scale (25M
to 671B parameters), and training data (e.g., unimodal, multimodal, empathy-finetuned). Bars represent the Pearson correlation
between a model’s RSM and human RSMs derived from either categorical ratings (slash-shaded) or dimensional ratings (solid).
The results reveal strong scaling laws and highlight the benefits of multimodal and empathy-focused training. Error bars
represent 95% CIs.
46/48


## Page 47

Supplementary Fig. 1. Controlling for positional bias in MLLM behavioral data collection. Initial tests revealed a
strong positional bias where the MLLM preferentially selected the last item in a triplet. a-c, Prompt templates that presented all
three videos before the question failed to mitigate this bias, as shown by the skewed selection frequencies (right panels). d, In
contrast, an interleaved prompt structure, where videos and descriptive text were presented in an interleaved way, successfully
eliminated the bias. This optimized template was therefore used for all subsequent data collection.
47/48


## Page 48

1
2
3
The selected video ID
0.0
0.5
1.0
1.5
2.0
Trials
1e6
33.5%
32.9%
33.7%
1
2
3
The selected video ID
0.0
0.5
1.0
1.5
2.0
Trials
1e6
33.2%
33.4%
33.4%
1
2
3
The selected video ID
0.0
0.5
1.0
1.5
2.0
Trials
1e6
21.6%
42.5%
36.0%
1
2
3
The selected video ID
0
1
2
3
Trials
1e6
36.0%
22.0%
42.0%
50
100
150
200
250
300
350
400
470
Dataset size (in 10k trials)
0
10
20
30
40
Raw data
Mean ± SD
Number of components
a
b
c
d
e
Human (category)
Human (dimension)
LLM
MLLM
Supplementary Fig. 2. Validation of data quality and sampling saturation. a-d, Frequency distributions of triplet choices
for the final datasets used in the main analysis. The approximate uniform distributions for the LLM and MLLM confirm that
the optimized prompt (see Supplementary Fig. 1) successfully eliminated positional bias. e, Data saturation analysis for the
LLM. The number of recoverable affective components (y-axis) stabilizes as the number of triplet judgments increases (x-axis),
indicating that our sample of 5.5 million trials was sufficient to capture the stable underlying representational structure. Box
plots show the distribution over n=5 bootstrap replicates.
48/48


