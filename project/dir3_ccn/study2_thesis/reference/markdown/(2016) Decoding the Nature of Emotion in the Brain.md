# (2016) Decoding the Nature of Emotion in the Brain

**Source:** (2016) Decoding the Nature of Emotion in the Brain.pdf

---

## Page 1

Review
Decoding the Nature
of Emotion in the Brain
Philip A. Kragel1 and Kevin S. LaBar1,*
A central, unresolved problem in affective neuroscience is understanding how
emotions are represented in nervous system activity. After prior localization
approaches largely failed, researchers began applying multivariate statistical
tools to reconceptualize how emotion constructs might be embedded in large-
scale brain networks. Findings from pattern analyses of neuroimaging data
show that affective dimensions and emotion categories are uniquely repre-
sented in the activity of distributed neural systems that span cortical and
subcortical regions. Results from multiple-category decoding studies are
incompatible with theories postulating that speciﬁc emotions emerge from
the neural coding of valence and arousal. This ‘new look’ into emotion repre-
sentation promises to improve and reformulate neurobiological models of
affect.
Mapping the Brain Basis of Emotion
Emotions are often experienced as discrete feelings, yet the brain basis of speciﬁc emotions
remains poorly understood. The inherent challenges in localizing the neural basis of human
emotions with fMRI are well illustrated by research investigating the correspondence between
amygdala activity and emotional states of fear. Meta-analytic summaries of this literature [1–3]
demonstrate consistent increases in blood oxygen level-dependent (BOLD) response within the
amygdala during experimental manipulations eliciting states of fear. Yet, amygdala activation is
observed during the elicitation of diverse affective states (see Glossary), including both positive
and negative emotions [4], and during manipulations of broader affective dimensions, such as
arousal and valence (Figure 1A). This combination of results and the limited spatiotemporal
resolution of fMRI (compared with other methods discussed in Box 1) complicate specifying the
role of the amygdala. Due to the variety of stimuli that engage this region, the amygdala has been
proposed to play a broader role in detecting salient stimuli [5,6] and in eliciting central and
autonomic arousal [7,8], of which fear is a particularly potent example. These kinds of obser-
vations have led theorists and researchers to abandon simple one-to-one mappings between a
given brain structure and a given emotion [4,9–11]. In response, two divergent lines of thinking
have emerged: one that abandons the notion of emotion-speciﬁc representations in the brain
[4,12] and another that has refocused enquiry towards identifying distributed neural systems that
underlie emotional behavior [9,13] (Box 2).
Seeking new ways to characterize emotion representations, imaging researchers have begun
applying multivariate techniques – namely, pattern classiﬁcation and representational similarity
analysis [14] – to investigate how emotions may be decoded from distributed patterns of brain
activity. These methods, broadly termed multivoxel pattern analysis (MVPA) when applied to
fMRI data, show much promise in other domains of cognitive neuroscience to specify how neural
systems are linked to separable mental states, such as the category of perceived objects or the
contents of working memory (for reviews see [15,16]). By identifying mappings between multiple
measures of neural activity and single mental states, MVPA can overcome the limiting
Trends
Due 
to 
limitations 
of 
univariate
approaches, scientists have begun to
apply multivariate statistical tools to
decode how emotion constructs are
represented in high-dimensional pat-
terns of human brain activity.
Recent studies show that functional
neuroimaging data can be accurately
classiﬁed along affective dimensions
and discrete emotion categories.
Data from studies classifying brain
states into multiple emotion categories
suggest that dimensions of valence
and arousal do not principally organize
neural 
representations 
of 
speciﬁc
emotions.
1Department of Psychology and
Neuroscience, Duke University,
Durham, NC 27708, USA
*Correspondence: klabar@duke.edu
(K.S. LaBar).
444 
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6 
http://dx.doi.org/10.1016/j.tics.2016.03.011
© 2016 Elsevier Ltd. All rights reserved.


## Page 2

Glossary
Affect: the manner in which
emotional events inﬂuence behavior
and subjective feelings, often
operationalized in terms of valence
and arousal.
Arousal: the degree of activation
experienced during an instance of
emotion, ranging from calm to
excited.
Bootstrapping: statistical method
used to assess the accuracy of a
parameter estimate through repeated
resampling with replacement. The
method is commonly used to
estimate conﬁdence intervals.
Cross-validation: a statistical
technique for estimating the degree
to which a model will generalize to
independent data. The method
involves repeatedly partitioning data
into independent samples for training
and evaluating models.
Decoding: predicting the mental
state associated with a pattern of
brain activity or similar dependent
measure.
International Affective Picture
System (IAPS): a set of
standardized images that includes
negative, neutral, and positive visual
scenes.
Isomorphic: two representational
spaces are isomorphic if there exists
a one-to-one correspondence
between all elements in both spaces,
such that they have the same
structural properties.
Gaussian naïve Bayes classiﬁer: a
multivariate classiﬁcation model that
assumes that continuous features
predictive of each class from
Gaussian distributions. The mean and
covariance of these distributions can
be estimated on training data for
each class, which can then be used
to compute the probability of class
membership for testing data.
Least absolute shrinkage and
selector operator principal
component regression (LASSO-
PCR): a multivariate regression
procedure that combines ‘1
regularization and principal
component analysis. High-
dimensional data are reduced to a
smaller number of components that
are then regressed onto outcome
variables while penalizing the
absolute size of the regression
coefﬁcients. This approach can
identify sparse models in the
presence of many features, making it
well suited for fMRI data.
assumption that emotions are represented by dedicated modules or functionally homogeneous
units [17]. Accordingly, MVPA shifts the focus of inquiry to emotion-speciﬁc patterns that emerge
across locally distributed populations of neurons within a region or across neural networks at
larger spatial scales, which is more closely aligned with contemporary views of mental state
representations [9,13].
(A) 
(B)
10
8
6
4
2
8
6
4
15
10
5
4
9
26
R2 = .01
R2 = .04
 
R2 = .02
-26
Fear
3
-3
6 
8 
4 
6 
8 
5
10
15
Fear
Unpleasant
Unpleasant
Arousal
Arousal
Figure 1. Overlapping Yet Distinct Proﬁles of Amygdala Activation Predict Experimental Manipulations of
Arousal, Unpleasantness, and Fear. (A) Probabilistic reverse-inference maps from an automated meta-analysis of the
neuroimaging literature [62] indicate the probability of a study including the terms ‘arousal’ (227 studies), ‘unpleasant’ (106
studies), or ‘fear’ (298 studies) given the observed activation. Color maps reﬂect z-scores and are additive as indicated by
the legend; the white region indicates voxels predictive of all three processes. (B) Spatial cross-correlations of amygdala
voxels [63] that commonly predict arousal, unpleasantness, and fear (displayed in white). Each point corresponds to a single
voxel and solid lines indicate the best least-squares ﬁt. Despite shared localization, patterns of predictive scores for arousal
or unpleasantness explain relatively little variance across voxels predictive of fear.
Box 1. Methodological Considerations for Studying the Neural Basis of Emotion
Although fMRI is advantageous because it can noninvasively sample neural activation spanning the whole brain, this
neuroimaging method has several limitations when used to map emotion onto the brain. In terms of spatial resolution,
smoothed voxels typically have an in-plane resolution on the order of 10 mm2 and have been estimated to contain, on
average, over 5 million neurons [64]. Moreover, simultaneous electrophysiological recording and fMRI acquisition in
macaques has shown that the BOLD response best correlates with local ﬁeld potentials, indicative of inputs and local
processing of a brain region as opposed to its spiking output [65]. Consequently, the activation of a single voxel can be
driven by diverse neural populations and can be regarded as a complex spatiotemporal ﬁlter [66] rather than a simple
summation of neuronal activity over space and time. This mismatch between the spatiotemporal resolution of fMRI and
the neural substrates underlying emotional behavior makes it unlikely that a single voxel will demonstrate emotion-speciﬁc
activation (i.e., consistently exhibit increased activation for one emotion but not for other emotions [4]), even if specialized
neurons reside within a voxel.
Electrophysiological recording methods such as measuring local ﬁeld potentials or single-unit recordings provide a
means to quantify emotion-related neuronal activity at the cellular level (e.g., see [67–69] for reviews of affective
processing in the human and nonhuman primate amygdala). One such study [70] measured local ﬁeld potentials from
depth electrodes in the amygdala and found that aversive stimuli – threatening images in particular – showed elevated
gamma-band power, which is most closely linked to the BOLD fMRI response in humans [71]. Although there are
relatively few studies relating electrophysiological measures to the subjective experience of distinct emotions (compared
with functional neuroimaging), data collected using these invasive methods are generally consistent with evidence from
functional neuroimaging [72], demonstrating that neuronal representations of emotion categories are distributed across a
number of cortical and subcortical brain regions. Future work manipulating neuronal activity and measuring the impact on
the experience of emotion (e.g., using electrical stimulation mapping [73]) will inform causal brain–behavior relationships
that can facilitate functional interpretations.
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6 
445


## Page 3

Multivariate approaches have several other advantages over univariate ones, which have been
the mainstay of emotion imaging research historically. Multivariate approaches have high
sensitivity because they incorporate more information than a single summary statistic of the
most signiﬁcantly activated voxel in a brain region. Their data-driven nature can reveal novel or
counterintuitive insights relative to approaches that rely on testing a priori hypotheses derived
from existing theories; rather than testing a theoretical assumption of how researchers postulate
emotions are represented in the brain, the analysis technique decodes the complex fMRI data to
inform the researcher how the brain organizes emotions. Outcomes from MVPA can then be
compared with existing theories to help adjudicate between different perspectives. As with
univariate approaches, multivariate approaches will detect any difference between conditions,
even those that are not of primary interest to the researcher [18]. Thus, well-controlled experi-
mental designs combined with additional analysis of the information content being decoded
should be conducted to provide support for the interpretation of the results. Finally, pattern
classiﬁcation approaches can particularly beneﬁt from inclusion of error analyses and measures
from signal detection theory such as sensitivity, speciﬁcity, and area under the receiver
operating characteristic (ROC) curve, as accuracy measures alone are not the most
informative indices of classiﬁer performance [19].
This review examines recent functional neuroimaging studies that use MVPA to investigate how
emotions are reﬂected in distributed patterns of brain activity, focusing on work that sheds light
on the representational space that best organizes instances of emotional experience
(Figure 2, Key Figure). Related work using multivariate techniques to study the perception
of emotional expressions is not covered here (e.g., [20,21]; see [13] for a review). The ﬁrst
section reviews research classifying brain states in terms of the affective dimension of valence,
or pleasantness [22]. The second part covers studies that decode fMRI activity into multiple
discrete emotion categories [23,24]. Finally, we conclude by evaluating the correspondence
between high-dimensional brain activity and theoretical models describing the organization of
emotions.
Multivoxel pattern analysis
(MVPA): analysis approach that
assesses the information contained in
patterns of fMRI (or
electrophysiological) activity, either by
comparing the similarity of responses
across multiple experimental
conditions or by learning a mapping
from multiple voxels to a categorical
or continuous outcome variable.
Psychological construction
accounts of emotion: views that
stress that emotions are not
biologically innate categories but are
constructed from multiple processes
(e.g., facial expression, somatic
activity, cognitive appraisals,
subjectively experienced valence) that
are not speciﬁc to any emotion.
Receiver operating characteristic
(ROC) curve: a plot of the true-
positive rate (sensitivity) against the
false-positive rate (1 – speciﬁcity)
indicating the performance of a binary
classiﬁer at multiple decision
thresholds.
Representational space: a high-
dimensional space in which instances
of emotion can be related to one
another. The dimensionality of the
space depends on the number of
features sampled (e.g., voxels, self-
report items).
Valence: the hedonic tone of
emotional experience, ranging from
bad (unpleasant) to good (pleasant).
Box 2. Representational Spaces for Emotional States
A major advantage of MVPA over subtraction-based methods is its capacity to efﬁciently relate representational spaces
to one another [15]. By treating each multivariate pattern of BOLD response as a point in high-dimensional space,
theoretical models can be directly related to distributed patterns of neural activity, either within local regions or across the
whole brain. Thus, MVPA offers a framework for constraining conceptual or computational theories of emotion with neural
data.
The usefulness of representational spaces is evident in contrasting different cognitive models of emotion, which predict
different relationships among emotions. In one account of basic emotions [48], happiness, sadness, disgust, fear, and
anger are considered functionally independent because they are associated with speciﬁc antecedent events: making
progress towards a goal, the loss of a goal, perceiving something to reject, perceiving a threat to survival, or blocking of a
goal. Alternatively, a circumplex model of emotions derived from judgments about emotion concepts and self-reported
emotional experience [22] suggests that these emotions are fundamentally represented along affective dimensions of
valence (pleasantness) and arousal (activation).
To quantitatively map these models onto distributed patterns of neural activity, representational spaces can be
constructed based on their core assumptions (see Figure 2 in main text). In one formulation of a dimensional model,
emotions are represented in a 2D space characterized by valence and arousal axes. This model assumes that instances
of fear, anger, and disgust are less distinct from one another than sadness and happiness because they share negative
valence and high arousal. For this model, emotions tend to cluster in a low-dimensional space. In the basic emotions
view, instances of different emotions are approximately equidistant from one another and form distinct categories. In this
model, emotions are sparse, relatively independent, and span a higher-dimensional space. With these model-based
representational spaces in hand, MVPA can be applied (e.g., through decoding or representational similarity analyses) to
identify brain regions with consistent representational geometries. Model comparison can be directly conducted to
identify the theoretical perspective that best explains the activity patterns; for instance, by determining whether a pattern
classiﬁer's errors conform more to one model or another [14].
446 
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6


## Page 4

Decoding Affectively Valenced Brain States
Classic behavioral studies in psychology using the multivariate tools of factor analysis and
multidimensional scaling show that facial expressions of emotions, self-reported moods, and
similarity ratings of emotion words are principally organized according to valence ([25]; but see
[26] for a counterexample in autobiographical memory). Because valence is accordingly thought
to be a ‘core’ affective feature of our emotional lives [27,28], researchers have begun utilizing
MVPA to investigate the manner in which patterns of fMRI activity encode information according
to this affective dimension.
One such study [29] employed representational similarity analysis [30] to identify brain regions
whose activity reﬂects a continuous dimension of subjective valence spanning from negative to
positive affect. Drawing on evidence from single-cell electrophysiological studies in monkeys
demonstrating that different populations of neurons in the orbitofrontal cortex (OFC) code
positive and negative value both independently and in an integrated fashion [31], the
Key Figure
Representational Spaces Suggested by Some Models of Emotion
(A)
Anger
Happiness
Happiness
14
12
10
8
6
dEuclidean
dEuclidean
4
2
0
20
15
10
5
0
Sadness
Disgust
Fear
Anger
Happiness
Sadness
Disgust
Fear
Anger
Sadness
Happiness
Key:
Sadness
Disgust
Fear
Anger
Excited
Bad
Calm
Good
Fear
Disgust
(B)
(C) 
(D)
Figure 2. (A) Representational space characterized by basic emotion models. Instances of emotion are drawn from
multivariate Gaussian distributions with a simple structure (each distribution is centered along one of ﬁve independent
dimensions). (B) Euclidean distance matrix illustrates how emotions are discrete and equidistant in this representational
space. (C) Radar plot depicting locations of affective concepts based on a 2D model. Each point corresponds to a single
instance of emotion, drawn from one of ﬁve multivariate Gaussian distributions with unique locations in valence–arousal
space. (D) Euclidean distance matrix illustrates how instances of disgust, fear, and anger are proximal to one another in this
representational space.
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6 
447


## Page 5

investigators hypothesized that MVPA would be able to detect voxel-level biases in the
distribution of such neurons when measured via fMRI in humans. Accordingly, patterns of
OFC response to different instances of positive affect were predicted to be similar to one another
and distinct from subjectively negative experiences. To assess the speciﬁcity of valence
representations, single-trial estimates of neural responses to visual scenes and gustatory stimuli
were anatomically localized within the OFC. The information content of this region was charac-
terized by constructing representational similarity matrices [32] that indexed the correlation of
OFC activation between all possible pairs of stimulus valence levels. Regression models were
then used to examine the relationship between the similarity of OFC response proﬁles and
differences in subjective valence, quantiﬁed using online self-reports of positive and negative
experience.
These analyses revealed that differences in subjective ratings of valence predicted the similarity
of responses within the OFC when comparing responses both within and between visual and
gustatory stimuli. Furthermore, classiﬁcation of subjective valence based on the similarity of
neural activation within this region was found to generalize across participants (cross-validat-
ing the classiﬁer on data from held-out subjects), although the observed accuracy (55.6%,
where chance was 50%) was considerably lower than an analogous classiﬁcation of object
categories on the basis of activation within the ventral temporal cortex (80.1%; Figure 3A). Such
low levels of discrimination indicate that patterning within the OFC alone may not effectively serve
as an objective marker of subjective valence. Nevertheless, the results demonstrate that a
(A)
(B)
OFC
VTC
50
Item
Valence
55
60
65
70
75
80
PINES
Classiﬁcaon
accuracy(%)
Average predicon
Emoon rang
100%
1
1
2
3
4
5
2 
3 
4 
5
100%
91%
Holdout test (n=61)
Cross- validaon (n=121)
Figure 3. Decoding Local and Global Brain Representations along a Continuous Dimension of Valence. (A)
Double dissociation from [29], wherein patterns of the orbitofrontal cortex (OFC) response to visual stimuli were found to
predict differences in subjective valence in novel subjects whereas ventral temporal cortex (VTC) activation predicted the
items conveyed in the images. Brain regions highlighted in yellow depict regions of interest used for classiﬁcation. (B) Peak
classiﬁcation weights from the Picture Induced Negative Emotion Signature [36], which maps whole-brain activation
patterns to a continuous prediction of negative emotional experience. The model performed in excess of 90% accuracy
when testing in independent subjects. (A) Reproduced, with permission, from [29]; (B) reproduced, with permission, from
[36].
448 
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6


## Page 6

portion of neural activity within the OFC is consistent with a representation of subjective valence
that is shared across stimulus modalities and individuals. Additionally, while external, perceptual
aspects of stimuli are well characterized in modality-speciﬁc cortices [33,34], the coding of
valence in the OFC is likely to involve a transformation from basic stimulus features into a more
abstract, common representation (see also [35] for related work on the coding of subjective
value in this region).
Another study of the valence continuum [36] classiﬁed patterns of fMRI activity to identify a neural
signature that predicts differences in the subjective experience of negative emotion in response
to aversive pictures. To identify patterns of BOLD response that accurately predicted negative
emotional experience with a high degree of generalization, a large sample of 182 subjects was
presented negative and neutral scenes from the International Affective Picture System (a set of
standardized images that reliably evoke negative, neutral, and positive affective reactions [37]).
Following the presentation of images on every trial, participants made behavioral ratings
indicating their current emotional state, ranging from neutral (a rating of 1) to strongly negative
(a rating of 5). Machine-learning models using least absolute shrinkage and selector
operator principal component regression (LASSO-PCR) were then trained to predict
the ﬁve levels of negative emotional experience from whole-brain estimates of BOLD response.
The resulting neural model, termed the Picture Induced Negative Emotion Signature (PINES),
demonstrated high levels of sensitivity when testing in independent subjects, both between
extreme ratings of negative emotion (ratings of 1 vs 5 were classiﬁed at 100% accuracy) and
between adjacent ratings (90.7% and 100% accuracy for ratings of classifying trials rated 5 vs 3
and 3 vs 1, respectively). In terms of spatial localization, increased activation of several regions,
including the anterior cingulate, insula, amygdala, and periaqueductal gray, contributed to the
prediction of negative emotional experience. Importantly, the distributed model was found to be
a better predictor of negative emotion than the average response within individual subregions or
resting state networks [38], demonstrating that MVPA provided unique insight into the repre-
sentation of negative emotion across activation patterns spanning the whole brain. These results
clearly demonstrate that a continuous dimension of negative affect is effectively predicted by a
distinct and distributed pattern of neural activation spanning multiple brain regions.
Although these results are notable in terms of signal detection capacity, it is possible that factors
other than negative emotion informed the classiﬁcation model. To evaluate the speciﬁcity of the
PINES, the researchers applied it to fMRI data acquired during painful thermal stimulation (which
is similarly negative and arousing) and compared it against a biomarker sensitive and speciﬁc to
physical pain, the neurologic pain signature (NPS) (see [39] for details of its development and
validation). The results of this analysis demonstrated a clear double dissociation: whereas the
PINES accurately classiﬁed negative versus neutral emotional experiences, but not high- versus
low-intensity pain, the NPS accurately discriminated between differences in pain reports but not
emotional intensity. Although the observed speciﬁcity suggests that commonalities between
experiencing pain and aversive images did not drive the results, it is still possible that other
factors could inform the PINES, such as differences in attentional orienting or visual processing,
which are likely to differ across negative and neutral images. Notwithstanding these limitations,
the ﬁndings of this study illustrate how neural biomarkers developed using MVPA can discrimi-
nate between brain states that are similar in terms of valence and arousal at high levels of
speciﬁcity.
The above studies demonstrate that valenced brain states can be differentiated on the basis of
neural activity (see also [40,41] for related work), partially supporting both dimensional and
psychological construction views of emotion that assume a prominent role of valence in the
neural representation of core affect [4]. In particular, the medial OFC was found to contain
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6 
449


## Page 7

valence-related information in both studies (albeit at uncorrected thresholds in [36]). However,
this emerging body of research is limited in its capacity to address how emotions are repre-
sented in a higher-dimensional space. Valence is a useful construct in part because it relates
emotions to one another based on a shared feature and can accordingly be used to infer the
emotional state of an individual (e.g., an individual in a positive state is less likely to report
experiencing anger or sadness). However, these studies have not tested whether brain-based
predictions of valence inform on-line reports of speciﬁc emotions, which would be expected if
brain systems dedicated to valence and arousal form the basis of emotional experience [28,42].
Additionally, these studies do not differentiate subjective valence from arousal, which plays a
prominent role in emotion and is often confounded with self-reports of valence when sampling a
small number of emotional states (i.e., when classifying responses to negative and neutral
images). Thus, it is not yet clear whether brain-based models of valence are concordant with
dimensional theories of emotion in terms of parameterization or generalizability.
Decoding Brain States during the Experience of Discrete Emotions
Although emotions can be understood by studying features shared across emotional states,
such as their valence or arousal, categorical models instead focus on differences in the
antecedent events, neural circuitry, and behavioral outputs speciﬁc to each emotion [43]. These
models commonly posit that emotions are experienced as independent categories in humans
and are differentiated in their neurophysiological expression. Following this logic, a number of
experiments have been conducted using fMRI with the goal of classifying neural activity along
multiple distinct emotion categories.
In one of the ﬁrst studies using MVPA methods to predict the experience of speciﬁc emotions on
the basis of fMRI activity [44], ten method actors (eight female) were asked to experience
multiple emotions (anger, disgust, envy, fear, happiness, lust, pride, sadness, and shame)
through script-driven imagery when prompted by corresponding cue words. Patterns of BOLD
response within the most stable 240 voxels (spanning the whole brain, but predominantly
comprising orbital and lateral frontal regions) during the presentation of verbal cues were used
as input to Gaussian naïve Bayes classiﬁers. The nine emotions were classiﬁed at 84%
mean rank accuracy when training and testing within the same subject and at 70% mean rank
accuracy when training and testing was performed on independent subjects (where chance
was 50%) – establishing that emotional states can be objectively differentiated on the basis of
brain activity.
To better understand the relationship between patterns of BOLD response and the affective
content of the scripts (i.e., valence, arousal, control, certainty, and attention), the authors
conducted an exploratory factor analysis. Although a number of associations were identiﬁed
between pre-scan ratings of the scripts and factors decomposed from neural activity, none was
speciﬁc. For instance, the factor explaining the most variance across patterns of neural response
(which the authors interpreted to reﬂect valence) was not only correlated with valence ratings but
was also correlated with ratings of arousal, certainty, and control. This lack of speciﬁcity may be
partly due to the fact that only two positive emotions (happiness and pride) were sampled in this
study, both of which are highly arousing. Additionally, the sample size was extremely small for the
application of exploratory factor analysis [45] and little time was provided for participants to
experience the emotions on each trial (9 s), thereby under-sampling the experiential aspects of
the emotion induction. Despite these complications in relating speciﬁc emotions to broader
affective constructs, this study set the stage for research classifying discrete emotions in
distributed patterns of brain activity. Additionally, the study acknowledged the difﬁculty of
evaluating psychological construction [4,28,46] and basic emotion [47,48] views with MVPA,
as successful pattern classiﬁcation could be the product of either cognitive constructions or
emotion-speciﬁc neural systems.
450 
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6


## Page 8

A more recent study [49] utilized script-driven imagery and short movie clips to elicit the basic
emotions of disgust, fear, happiness, anger, surprise, and sadness. Patterns of BOLD response
from gray matter voxels spanning the whole brain were accurately classiﬁed into the six emotion
categories using linear neural networks (34% and 23% accuracy for movies and imagery, where
chance was 20% and 16.7%, respectively). Further, the researchers found that post-scan
similarity judgments of emotion words used to cue imagery were positively correlated with the
number of misclassiﬁcations made in MVPA, demonstrating that the words that were distinct in
terms of their meaning were more accurately classiﬁed. Together, these ﬁndings provide
evidence that subjective judgments about emotional events are consistent with the expression
of distinct neural substrates probabilistically linked to their occurrence.
Whereas the previously described studies used behavioral ratings of stimuli outside the scanner,
either before or after scanning, we [50] conducted an fMRI experiment in which participants
reported on their emotional experience following emotion induction in the scanner using
instrumental music and cinematic ﬁlms (states of contentment, amusement, surprise, fear,
anger, and sadness and a neutral control condition were elicited). Such on-line veriﬁcation of
emotional experience is critical for conﬁrming coherence across emotional systems [51] and for
isolating which affective factors contribute to classiﬁcation. Participants’ ratings conﬁrmed that
emotions were experienced discretely in accordance with the intended category for each
stimulus and ratings on dimensional terms also discriminated among some emotions (e.g.,
valence ratings differentiated contentment and amusement from fear, anger, and sadness).
Together, these behavioral analyses established that participants’ subjective experience was
concordant with theoretical models proposing dimensional and categorical representation of
emotions.
Supporting the notion that emotions are represented in distributed neural systems, whole-brain
patterns of BOLD response during the music and ﬁlm induction were classiﬁed using partial
least-squares discriminant analysis at 37.3% accuracy compared with chance levels of 14.3%
(when training and testing models on independent subjects). The activity patterns of the discrete
emotions predicted the induction of discrete emotional states consistently across subjects with
a high degree of sensitivity and speciﬁcity. By bootstrapping regression coefﬁcients of their
classiﬁcation models, the researchers found that activity informing the classiﬁcation models for
each emotion was localized in relatively non-overlapping brain regions, spanning cortical and
subcortical areas (Figure 4).
To relate neural classiﬁcation to emotional experience, the investigators used on-line measures
of emotional experiences to construct a categorical model, with each emotion represented along
an independent axis, and a 2D model organized by valence and arousal. Regression models
were then constructed to assess the extent to which errors in classifying fMRI activation could be
predicted on the basis of self-report. This analysis revealed that differences in categorical
aspects of experience were associated with improved decoding accuracy. By contrast, instan-
ces that differed the most in terms of valence and arousal were more frequently associated with
classiﬁcation errors, indicating that these dimensional constructs may inefﬁciently discriminate
among speciﬁc emotional brain states.
Although unexpected from the viewpoint of dimensional models, impaired classiﬁcation of
emotions that differ in terms of valence and arousal is concordant with ﬁndings from meta-
analytic efforts that utilized MVPA to discriminate among basic emotion categories [52] but failed
to differentiate positive and negative valence [53]. These meta-analytic ﬁndings were interpreted
by the authors as supporting constructionist models of emotion [52] because the patterns of
activity that predicted each emotion category spanned multiple intrinsic brain systems (see also
[54]). However, direct model comparisons to rule out alternative interpretations based on
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6 
451


## Page 9

categorical theories were not conducted. Further, the ﬁndings suggest that valence is not the
primary driver of brain activity that distinguishes discrete emotions. Together, these emerging
results suggest that patterns of brain activity indicative of affective dimensions such as arousal
and valence may not account for a given brain region's contribution to a speciﬁc emotion, such
(A)
L 
R
Predicted
True
True
Predicted
Predicted
Happy 
Sad
Fear
Disgust
Anger
True
Anger
1
0.8
0.6
0.4
0.2
0
70
50
40
30
20
10
0
60
Fear
Happiness
Sadness
Surprise
Disgust
Content
Key:
Content
Content
Amusement
Amusement
Amusement
Surprise
Surprise
Surprise
Fear
Fear
Fear
Anger
Anger
Anger
Sad
Sad
Sad
Neutral
Neutral
Anger 0.43
0.07
0.28
0.15
0.08
0.03
0.76
0.08
0.08
0.06
0.02
0.04
0.86
0.06
0.03
0.00
0.07
0.23
0.58
0.11
0.00
0.07
0.20
0.09
0.65
Anger
Disgust
Disgust
Fear
Fear
Happy
Happy
Sad
Sad
Neutral
(B)
(C)
Figure 4. Brain-Based Models of Discrete Emotion Categories. (A) Importance maps (indicating the top 1% of features) computed for within-subject classiﬁcation
of six basic emotions in the imagery experiment from [49]. (B) Partial least-squares regression coefﬁcients indicate voxels in which activation reliably predicts the music-
and ﬁlm-evoked emotional states in independent subjects from [50]. (C) Intensity maps from the Bayesian Spatial Point Process model developed from the peak
coordinates of 148 neuroimaging studies of emotion [52]. The intensity maps indicate the expected number of activations from studies assigned to each emotion
category. The confusion matrices indicate the correspondence between ground truth and predicted labels. In general, most entries fall along the diagonal indicating good
performance, with few errors between similarly valenced emotions (e.g., fear, anger, and sadness). (A) Reproduced, with permission, from [49]; right panel of (B)
reproduced, with permission, from [50]; and (C) reproduced, with permission, from [52].
452 
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6


## Page 10

as fear, as illustrated for the amygdala in Figure 1B. Given that dimensional models explain many
aspects of self-reported emotions (as discussed above), neurophysiological and behavioral
facets of emotion representation may not be isomorphic (for a similar conclusion using MVPA in
the autonomic nervous system, see [55]).
Concluding Remarks
Whereas efforts focusing on functional localization have largely failed at mapping emotions onto
individual brain regions, emerging research using MVPA has demonstrated that information
encoded in both local neural ensembles and whole-brain activation patterns can be utilized to
predict affective dimensions and discrete emotions with high levels of speciﬁcity. Findings across
multiple studies demonstrate that machine learning approaches can fruitfully be used to
characterize self-reports of emotional experience. Contrary to the assumption held by dimen-
sional and psychological construction accounts that hedonic valence is at the core of emotional
experience with an innate neural basis in humans [46,56], MVPA has revealed that brain
representations of emotions are better characterized as discrete categories as opposed to
points in a low-dimensional space parameterized along the valence continuum. However, it is
not yet clear whether these category-speciﬁc, distributed activation patterns reﬂect evolutionarily
ingrained networks, constructive processes, or a combination of factors.
Despite some broad overlap at a larger spatial scale (Figure 4), the localization of emotion-
predictive patterns varies at the voxel level across the few MVPA studies of emotion induction
conducted thus far [44,49,50]. Proponents of constructionist models argue that this variability
indicates that multivariate classiﬁers do not learn the essence of emotion categories [54,56] but
instead differentiate among populations of emotional instances sampled within a study. Thus,
disparities in patterning across studies could be driven by differences in induction procedures,
analytical methods, and inclusion of different emotions and varying numbers of emotions in each
study. One important consideration is that some studies reported only the most informative
voxels within their sample (e.g., [44,49]) and did not verify the extent to which emotion-predictive
patterns were consistent across subjects, making it less likely that the effects will generalize to
independent samples. In light of these issues, it is premature to draw any strong conclusions
about the localization of emotion-speciﬁc patterning: it is possible that some aspects of
classiﬁcation models are idiosyncratic to particular samples or experimental manipulations,
while some aspects of emotion-speciﬁc patterning could be invariant across studies, potentially
linked to common functional and behavioral changes associated with speciﬁc emotions. Fully
understanding which factors contribute to differences in emotion-predictive patterns across
studies and whether a single, invariant neural model of emotion categories can sufﬁciently
predict subjective experience remain questions open to future investigation.
Although categorical representation of emotions in the brain is concordant with accounts
suggesting that emotions are the product of adaptive pressures [57,58], the MVPA results
are compatible with a broad range of models because emotions can be considered discrete
without necessitating an evolutionary stance regarding their origin [47]. For example, appraisal
theories suggest that some emotions can be considered modal based on their frequency and
prototypically [59] or that instances of the same emotion are similar because their antecedents
share core relational themes [60]. Due to the diversity of biological, social, psychological, and
computational models of emotion, there is much to be learned about the organization of affective
brain states (see Outstanding Questions). Future research in this area should focus on additional
analyses of the information content used by classiﬁers to predict emotions from neural data
(such as the role of speciﬁc appraisals) and should conduct comparisons across other models of
emotion for the imaging data to maximally inform theory development. For example, one recent
study explored how emotions are attributed to others using verbal scenarios and found that
more complex appraisal features better explained neural representations of emotional stimuli
Outstanding Questions
Do patterns of emotion-speciﬁc neural
activation play a causal role in the expe-
rience of emotion?
How does emotion regulation affect
neural biomarkers of speciﬁc emotional
states?
Can multivariate neural biomarkers be
used to track the dynamics of emotions
over time?
Given that basic emotions are thought
to be driven by innate circuitry, can
high-resolution functional imaging pro-
vide novel insight into their representa-
tion in the local activity of subcortical
neural networks?
Do emotion-speciﬁc patterns of cogni-
tive 
appraisal 
have 
distinct 
neural
bases?
How do neural representations of emo-
tion change across development or
across cultures?
Do neural biomarkers of emotional
states have practical utility in diagnosis
or predicting clinical outcomes?
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6 
453


## Page 11

than basic or dimensional accounts [61]. Using this direct model-comparison approach to
understand brain responses during emotion induction (see also [50]) is a promising avenue for
future studies. As is evident from this brief review, advances in multivariate approaches to
neuroimaging have reinvigorated the quest to solve one of the biggest puzzles in affective
neuroscience: to identify how speciﬁc feelings emerge from complex patterns of neural activity.
References
1. 
Vytal, K. and Hamann, S. (2010) Neuroimaging support for dis-
crete neural correlates of basic emotions: a voxel-based meta-
analysis. J. Cogn. Neurosci. 22, 2864–2885
2. 
Murphy, F.C. et al. (2003) Functional neuroanatomy of emotions: a
meta-analysis. Cogn. Affect. Behav. Neurosci. 3, 207–233
3. 
Phan, K.L. et al. (2002) Functional neuroanatomy of emotion: a
meta-analysis of emotion activation studies in PET and fMRI.
Neuroimage 16, 331–348
4. 
Lindquist, K.A. et al. (2012) The brain basis of emotion: a meta-
analytic review. Behav. Brain Sci. 35, 121–143
5. 
Cunningham, W.A. and Brosch, T. (2012) Motivational salience:
amygdala tuning from traits, needs, values, and goals. Curr. Dir.
Psychol. Sci. 21, 54–59
6. 
Sander, D. et al. (2003) The human amygdala: an evolved system
for relevance detection. Rev. Neurosci. 14, 303–316
7. 
Cardinal, R.N. et al. (2002) Emotion and motivation: the role of the
amygdala, ventral striatum, and prefrontal cortex. Neurosci. Bio-
behav. Rev. 26, 321–352
8. 
Murray, E.A. (2007) The amygdala, reward and emotion. Trends
Cogn. Sci. 11, 489–497
9. 
Hamann, S. (2012) Mapping discrete and dimensional emotions
onto the brain: controversies and consensus. Trends Cogn. Sci.
16, 458–466
10. Pessoa, L. (2012) Beyond brain regions: network perspective of
cognition–emotion interactions. Behav. Brain Sci. 35, 158–159
11. Scarantino, A. (2012) Functional specialization does not require a
one-to-one mapping between brain regions and emotions. Behav.
Brain Sci. 35, 161–162
12. Barrett, L.F. (2006) Are emotions natural kinds? Perspect. Psy-
chol. Sci. 1, 28–58
13. Kragel, P.A. and LaBar, K.S. (2014) Advancing emotion theory
with multivariate pattern classiﬁcation. Emot. Rev. 6, 160–174
14. Kriegeskorte, N. and Kievit, R.A. (2013) Representational geome-
try: integrating cognition, computation, and the brain. Trends
Cogn. Sci. 17, 401–412
15. Haxby, J.V. et al. (2014) Decoding neural representational
spaces using multivariate pattern analysis. Annu. Rev. Neurosci.
37, 435–456
16. Haynes, J.D. (2015) A primer on pattern-based approaches to
fMRI: principles, pitfalls, and perspectives. Neuron 87, 257–270
17. Scarantino, A. and Grifﬁths, P. (2011) Don’t give up on basic
emotions. Emot. Rev. 3, 444–454
18. Todd, M.T. et al. (2013) Confounds in multivariate pattern analy-
sis: theory and rule representation case study. Neuroimage 77,
157–165
19. Sokolova, M. et al. (2006) Beyond accuracy, f-score and ROC: a
family of discriminant measures for performance evaluation. In
Proceedings of the 19th Australian Joint Conference on Artiﬁcial
Intelligence: Advances in Artiﬁcial Intelligence, pp. 1015–1021,
Springer-Verlag
20. Ethofer, T. et al. (2009) Decoding of emotional information in voice-
sensitive cortices. Curr. Biol. 19, 1028–1033
21. Peelen, M.V. et al. (2010) Supramodal representations of per-
ceived emotions in the human brain. J. Neurosci. 30, 10127–
10134
22. Russell, J.A. (1980) A circumplex model of affect. J. Pers. Soc.
Psychol. 39, 1161–1178
23. Ekman, P. and Cordaro, D. (2011) What is meant by calling
emotions basic? Emot. Rev. 3, 364–370
24. Oatley, K. and Johnson-Laird, P.N. (2014) Cognitive approaches
to emotions. Trends Cogn. Sci. 18, 134–140
25. Feldman Barrett, L. and Russell, J.A. (1999) The structure of
current affect: controversies and emerging consensus. Curr.
Dir. Psychol. Sci. 8, 10–14
26. Talarico, J.M. et al. (2004) Emotional intensity predicts autobio-
graphical memory experience. Mem. Cogn. 32, 1118–1132
27. Barrett, L.F. (2006) Solving the emotion paradox: categorization
and the experience of emotion. Pers. Soc. Psychol. Rev. 10,
20–46
28. Russell, J.A. (2003) Core affect and the psychological construction
of emotion. Psychol. Rev. 110, 145–172
29. Chikazoe, J. et al. (2014) Population coding of affect across
stimuli, modalities and individuals. Nat. Neurosci. 17, 1114–1122
30. Kriegeskorte, N. et al. (2006) Information-based functional brain
mapping. Proc. Natl. Acad. Sci. U.S.A. 103, 3863–3868
31. Morrison, S.E. and Salzman, C.D. (2009) The convergence of
information about rewarding and aversive stimuli in single neurons.
J. Neurosci. 29, 11471–11483
32. Kriegeskorte, N. et al. (2008) Representational similarity analysis –
connecting the branches of systems neuroscience. Front. Syst.
Neurosci. 2, 4
33. Brouwer, G.J. and Heeger, D.J. (2009) Decoding and reconstruct-
ing color from responses in human visual cortex. J. Neurosci. 29,
13992–14003
34. Kamitani, Y. and Tong, F. (2005) Decoding the visual and subjec-
tive contents of the human brain. Nat. Neurosci. 8, 679–685
35. McNamee, D. et al. (2013) Category-dependent and category-
independent goal-value codes in human ventromedial prefrontal
cortex. Nat. Neurosci. 16, 479–485
36. Chang, L.J. et al. (2015) A sensitive and speciﬁc neural signature
for picture-induced negative affect. PLoS Biol. 13, e1002180
37. Lang, P.J. et al. (2008) International Affective Picture System
(IAPS): Affective Ratings of Pictures and Instruction Manual, Uni-
versity of Florida
38. Yeo, B.T. et al. (2011) The organization of the human cerebral
cortex estimated by intrinsic functional connectivity. J. Neurophy-
siol. 106, 1125–1165
39. Wager, T.D. et al. (2013) An fMRI-based neurologic signature of
physical pain. N. Engl. J. Med. 368, 1388–1397
40. Baucom, L.B. et al. (2012) Decoding the neural representation of
affective states. Neuroimage 59, 718–727
41. Shinkareva, S.V. et al. (2014) Representations of modality-speciﬁc
affective processing for visual and auditory stimuli derived from
functional magnetic resonance imaging data. Hum. Brain Mapp.
35, 3558–3568
42. Barrett, L.F. (2006) Valence is a basic building block of emotional
life. J. Res. Person. 40, 35–55
43. Tracy, J.L. and Randles, D. (2011) Four models of basic emotions:
a review of Ekman and Cordaro, Izard, Levenson, and Panksepp
and Watt. Emot. Rev. 3, 397–405
44. Kassam, K.S. et al. (2013) Identifying emotions on the basis of
neural activation. PLoS ONE 8, e66032
45. MacCallum, R.C. et al. (1999) Sample size in factor analysis.
Psychol. Methods 4, 84
46. Lindquist, K.A. (2013) Emotions emerge from more basic psycho-
logical ingredients: a modern psychological constructionist model.
Emot. Rev. 5, 356–368
47. Ekman, P. (1992) An argument for basic emotions. Cogn. Emot. 6,
169–200
48. Johnson-Laird, P.N. and Oatley, K. (1992) Basic emotions, ratio-
nality, and folk theory. Cogn. Emot. 6, 201–223
454 
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6


## Page 12

49. Saarimäki, H. et al. (2015) Discrete neural signatures of basic
emotions. Cereb. Cortex. Published online April 29, 2015.
http://dx.doi.org/10.1093/cercor/bhv086
50. Kragel, P.A. and LaBar, K.S. (2015) Multivariate neural biomarkers
of emotional states are categorically distinct. Soc. Cogn. Affect.
Neurosci. 10, 1437–1448
51. Mauss, I.B. et al. (2005) The tie that binds? Coherence among
emotion experience, behavior, and physiology. Emotion 5, 175
52. Wager, T.D. et al. (2015) A Bayesian model of category-speciﬁc
emotional brain responses. PLoS Comput. Biol. 11, e1004066
53. Lindquist, K.A. et al. (2016) The brain basis of positive and negative
affect: evidence from a meta-analysis of the human neuroimaging
literature. Cereb Cortex. 26, 1910–1922
54. Clark-Polner, E. et al. (2016) Multivoxel pattern analysis does not
provide evidence to support the existence of basic emotions.
Cereb. Cortex. Published online February 29, 2016. http://dx.
doi.org/10.1093/cercor/bhw028
55. Kragel, P.A. and LaBar, K.S. (2013) Multivariate pattern classiﬁ-
cation reveals autonomic and experiential representations of dis-
crete emotions. Emotion 13, 681–690
56. Barrett, L.F. (2014) The conceptual act theory: a précis. Emot.
Rev. 6, 292–297
57. Damasio, A. and Carvalho, G.B. (2013) The nature of feelings:
evolutionary and neurobiological origins. Nat. Rev. Neurosci. 14,
143–152
58. Anderson, D.J. and Adolphs, R. (2014) A framework for studying
emotions across species. Cell 157, 187–200
59. Scherer, K.R. (2005) What are emotions? And how can they be
measured? Soc. Sci. Inform. 44, 695–729
60. Lazarus, R.S. (1991) Progress on a cognitive–motivational–rela-
tional theory of emotion. Am. Psychol. 46, 819
61. Skerry, A.E. and Saxe, R. (2015) Neural representations of emo-
tion are organized around abstract event features. Curr. Biol. 25,
1945–1954
62. Yarkoni, T. et al. (2011) Large-scale automated synthesis of
human functional neuroimaging data. Nat. Methods 8, 665–670
63. Tzourio-Mazoyer, N. et al. (2002) Automated anatomical label-
ing of activations in SPM using a macroscopic anatomical
parcellation of the MNI MRI single-subject brain. Neuroimage
15, 273–289
64. Logothetis, N.K. (2008) What we can do and what we cannot do
with fMRI. Nature 453, 869–878
65. Logothetis, N.K. et al. (2001) Neurophysiological investigation of
the basis of the fMRI signal. Nature 412, 150–157
66. Kriegeskorte, N. et al. (2010) How does an fMRI voxel sample the
neuronal activity pattern: compact-kernel or complex spatiotem-
poral ﬁlter? Neuroimage 49, 1965–1976
67. Rutishauser, U. et al. (2015) The primate amygdala in social
perception – insights from electrophysiological recordings and
stimulation. Trends Neurosci. 38, 295–306
68. Murray, R.J. et al. (2014) The functional proﬁle of the human
amygdala in affective processing: insights from intracranial record-
ings. Cortex 60, 10–33
69. Salzman, C.D. and Fusi, S. (2010) Emotion, cognition, and mental
state representation in amygdala and prefrontal cortex. Annu. Rev.
Neurosci. 33, 173–202
70. Oya, H. et al. (2002) Electrophysiological responses in the human
amygdala discriminate emotion categories of complex visual stim-
uli. J. Neurosci. 22, 9502–9512
71. Lachaux, J.P. et al. (2007) Relationship between task-related
gamma oscillations and BOLD signal: new insights from combined
fMRI and intracranial EEG. Hum. Brain Mapp. 28, 1368–1375
72. Guillory, S.A. and Bujarski, K.A. (2014) Exploring emotions using
invasive methods: review of 60 years of human intracranial electro-
physiology. Soc. Cogn. Affect. Neurosci. 9, 1880–1889
73. Borchers, S. et al. (2012) Direct electrical stimulation of human
cortex – the gold standard for mapping brain functions? Nat. Rev.
Neurosci. 13, 63–70
Trends in Cognitive Sciences, June 2016, Vol. 20, No. 6 
455


