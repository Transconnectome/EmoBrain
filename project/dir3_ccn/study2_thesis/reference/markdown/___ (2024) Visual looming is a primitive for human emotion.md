# *** (2024) Visual looming is a primitive for human emotion

**Source:** *** (2024) Visual looming is a primitive for human emotion.pdf

---

## Page 1

iScience
Article
Visual looming is a primitive for human emotion
Monica K. Thieu,
Vladislav
Ayzenberg, Stella
F. Lourenco, Philip
A. Kragel
pkragel@emory.edu
Highlights
The human superior
colliculus encodes
representations of visual
looming
Looming representations
predict defensive blinking
in human infants
Looming representations
predict subjective emotion
in human adults
A simple neural network
optimized for a survival-
relevant task predicts
human emotion
Thieu et al., iScience 27, 109886
June 21, 2024 ª 2024 The
Author(s). Published by Elsevier
Inc.
https://doi.org/10.1016/
j.isci.2024.109886
ll
OPEN ACCESS


## Page 2

iScience
Article
Visual looming is a primitive for human emotion
Monica K. Thieu,1 Vladislav Ayzenberg,1,2 Stella F. Lourenco,1 and Philip A. Kragel1,3,*
SUMMARY
The neural computations for looming detection are strikingly similar across species. In mammals, informa-
tion about approaching threats is conveyed from the retina to the midbrain superior colliculus, where
approach variables are computed to enable defensive behavior. Although neuroscientiﬁc theories posit
that midbrain representations contribute to emotion through connectivity with distributed brain systems,
it remains unknown whether a computational system for looming detection can predict both defensive
behavior and phenomenal experience in humans. Here, we show that a shallow convolutional neural
network based on the Drosophila visual system predicts defensive blinking to looming objects in infants
and superior colliculus responses to optical expansion in adults. Further, the neural network’s responses
to naturalistic video clips predict self-reported emotion largely by way of subjective arousal. These ﬁnd-
ings illustrate how a simple neural network architecture optimized for a species-general task relevant for
survival explains motor and experiential components of human emotion.
INTRODUCTION
Emotions guide people to make sense of and react adaptively to the world around them. A hallmark of human emotion is the complexity of
emotionally evocative situations and the varied ways in which they are appraised. Nevertheless, certain events consistently drive similar ex-
periences across individuals. A spectator at a baseball game is likely to ﬂinch in the face of an oncoming foul ball. A pedestrian might report
feeling frightened after a speeding car cuts too close to them in the crosswalk. Even if emotional experience is ultimately highly personalized
by a variety of developmental and cultural factors,1 some aspects of this experience are likely built upon mechanisms that are shared across
people and across phylogeny. These building blocks of emotion are considered ‘‘primitives’’ because they are either psychologically irreduc-
ible,2 are encoded within evolutionarily old neural circuits for survival,3 or because they have properties that are present across species.4
Through their inﬂuence on distributed cortical processing,3,5 such primitives can contribute to emotional experience by conveying informa-
tion relevant to broad affective dimensions like valence or arousal,6 or speciﬁc emotion categories like fear.7 To understand the nature and
origins of human emotion, we must identify the extent to which features are shared across species and the means by which speciﬁc sensory
inputs drive speciﬁc emotional states.
Humans are tuned to detect and react to certain classes of ancestrally relevant stimuli, and threats to survival in particular.8,9 Predators
make up one such class of threats. For example, human observers—including infants and children—detect images of snakes faster than other
objects.10–14 Macaques also rapidly detect and learn to avoid snakes,15,16 two behaviors thought to be implemented in a subcortical pathway
through the superior colliculus and pulvinar.17 Emotional expressions make up another such class of sensory signals indicative of threat. For
example, fearful facial expressions are detected more rapidly than other expressions.18 This heightened sensitivity may be subserved by the
detection of speciﬁc visual features, like widened eyes, in the amygdala via similar inputs from the pulvinar nucleus.19 Anatomical and func-
tional data suggest that similar subcortical pathways from the colliculus to the amygdala are involved in threat detection across primates.20–22
Although these ﬁndings may be taken to suggest that threats are detected through similar neural mechanisms, not all animals are as sensitive
to predatory snakes, or the wide-eyed facial expressions of conspeciﬁcs, suggesting these behaviors are unlikely to be supported by neural
mechanisms that are shared across species.
One type of stimulus that is generally perceived as threatening and evokes defensive behavior across species is visual looming. As an ob-
ject approaches the viewer, or looms, it tends to block light, and its edges expand optically. Additionally, if the object is on a collision course,
its edges will expand radially in the observer’s frame of reference. Rapidly approaching objects in the environment are almost invariably
dangerous, like predators, or projectiles that may cause physical damage upon contact, and very few other types of environmental motion
will create such a combination of visual features. Dark-shape radial expansion thus affords threat of collision to any animal that can detect it.23
Many species of animals show defensive responses to looming stimuli that are subserved by functionally similar neural pathways. Rapidly
looming shadows elicit escape behaviors in animals including but not limited to insects, birds, rodents, and nonhuman primates.24–27 Hu-
mans, as well, show defensive responses—when faced with physically looming objects, human infants and adults blink and ﬂinch
1Emory University, Atlanta, GA, USA
2University of Pennsylvania, Philadelphia, PA, USA
3Lead contact
*Correspondence: pkragel@emory.edu
https://doi.org/10.1016/j.isci.2024.109886
iScience 27, 109886, June 21, 2024 ª 2024 The Author(s). Published by Elsevier Inc.
This is an open access article under the CC BY-NC license (http://creativecommons.org/licenses/by-nc/4.0/).
1
ll
OPEN ACCESS


## Page 3

respectively.28–31 Across mammals, detecting and responding to looming motion involves the superior colliculus, a midbrain structure whose
neural organization and role in sensorimotor orienting is highly conserved across species.32 Indeed, the human superior colliculus responds to
looming visual stimuli,33 even in the absence of awareness.34 Information about looming is used to coordinate defensive behavior via pro-
jections to subcortical structures including the periaqueductal gray, ventral tegmental area, and the thalamus.35 The computations involved
in detecting and responding to visually looming threats are comparable across vertebrates,36 suggesting they may produce a ‘‘central
emotion state’’ that is a building block of emotion.4 This convergence of computation across species suggests models of looming detection
from nonhuman animal studies can be applied to predict human responses to similar stimuli.
We hypothesized that visual looming contributes to human emotional experience via computations that are common across species and
only require information available in the optical array.23 If this is the case, then a species-general neural network optimized for collision detec-
tion should predict brain activity, defensive responses to looming objects, and subjective experience in humans. Here, we tested this hypoth-
esis in three ways. First, we assessed whether representations of looming from the convolutional neural network are encoded in patterns of
superior colliculus responses to dynamic videos37 in human adults. Second, we tested whether the convolutional neural network predicts
defensive blinking to looming objects in human infants. Third, we evaluated whether representations of looming relate to valence and arousal
or speciﬁc emotion categories, using the neural network to predict self-reported emotions following exposure to naturalistic videos.38
Through these analyses, we test which aspects of human affective experience could be modeled by a simple computational system based
on algorithms implemented in the nervous system of multiple species.
RESULTS
Visual looming is encoded in the human superior colliculus
To model looming, we adapted a pre-trained shallow convolutional neural network with connections constrained by the connectivity of
Drosophila LPLC2 neurons,39 directly inputting the pre-trained ﬁlter for a single LPLC2 ‘‘neuron’’ as the kernel (Figure 1A). Unlike parametric
models that use variables such as the relative rate of expansion t (tau) and the optical variable h (eta) to compute the approach of looming
objects,40,41 the network takes sequences of optical ﬂow as input, providing a model that can process naturalistic videos. This property makes
the network more similar to circuits involved in looming that receive inputs from motion-sensitive neurons,42,43 and simultaneously enables it
to learn representations similar to optical variables speciﬁed in established parametric models. Four channels of inputs are analyzed per
frame–one for each of the cardinal directions of optical ﬂow—and each channel is convolved with a characteristic radial outward motion ﬁlter,
producing a two-dimensional spatial representation of looming. This representation is summed across units to produce a framewise estimate
of collision probability over the sequence of visual inputs.
We ﬁrst tested whether variables used to predict imminent collision in the shallow convolutional neural network are encoded in human
superior colliculus activity, and compared them to models using the optical variables t and h. We ﬁt encoding models44 of looming motion
to predict fMRI signal acquired as participants (N = 15) viewed dynamic visual stimuli used for retinotopic mapping37 (see STAR Methods).
The visual stimuli included four types of motion: clockwise and counterclockwise sweeping wedges in addition to contracting and expand-
ing rings. These stimuli uniquely activated units in the convolutional network depending on their receptive ﬁeld (Figure S1). Because ex-
panding rings involve symmetric radial expansion, a hallmark of looming that activates the superior colliculus,33,34,45 we hypothesized re-
sponses to expanding rings should be best explained by encoding models utilizing features that are useful for detecting imminent
collision.
Accordingly, we also compared the performance between two varieties of each encoding model: a stimulus-general version trained to
identify mappings between representations of looming and human brain activity using responses to all four stimulus types, and an expan-
sion-speciﬁc version trained to identify mappings using only responses to optical expansion. If neural populations in the human superior col-
liculus responses encode visual looming, then the model trained to predict patterns of BOLD response from optical expansion alone should
outperform the stimulus-general model with the same parameters, whereas regions that are sensitive to visual motion more broadly, such as
primary visual cortex,46,47 should be best predicted by the stimulus-general version of the model.
We found that an expansion-speciﬁc encoding model built using features from the collision detection model predicted BOLD responses in
the superior colliculus (leave-one-subject-out cross-validated r = 0.119, SE = 0.039, 99.0% of noise ceiling, p < 0.001, permutation test; Fig-
ure 1D), and that it outperformed its associated stimulus-general model (Dr = 0.046, SE = 0.021, 63.0% change, p = 0.020, permutation test;
responses of individual units are shown in Figure S2). Critically, the enhanced performance of the expansion-speciﬁc collision detection en-
coding model was greater than that of the contraction- and wedge-speciﬁc models on matched stimuli (Dr = 0.092, SE = 0.031, p < 0.001,
158.2% change, permutation test; Figure 1D). Further, adding estimates of looming based on the optical variables t and h to the encoding
model did not improve prediction (Dr = 0.003, SE = 0.004, 2.7% change, p = 0.198, permutation test, see Table S1), demonstrating that these
variables do not capture aspects of superior colliculus function beyond those learned by the collision detection model.
Because the superior colliculus receives inputs from primary visual cortex, we next evaluated whether the sensitivity of the superior colli-
culus to looming is distinct from cortical processing of visual motion. We did so by testing whether representations of looming from the colli-
sion detection model differ in their ability to predict responses in superior colliculus and primary visual cortex (V1). This comparison provides a
strong analytical control because V1 is sensitive to motion generally but does not selectively respond to coherent motion. The expansion-
speciﬁc collision detection encoding model robustly predicted BOLD responses in V1 (r = 0.368, SE = 0.025, 83.0% of noise ceiling,
p < 0.001, permutation test), and outperformed its associated stimulus-general model (Dr = 0.050, SE = 0.010, 15.8% change, p < 0.001, per-
mutation test). We also observed a relative improvement of the looming-speciﬁc collision detection model compared to its associated
ll
OPEN ACCESS
2
iScience 27, 109886, June 21, 2024
iScience
Article


## Page 4

stimulus-general version in V1 compared to the contraction- and wedge-speciﬁc models (Dr = 0.043, 13.1% change, SE = 0.010, p = 0.002,
permutation test; Figure S3).
To compare performance between the superior colliculus and primary visual cortex on a balanced scale, as they have different sources of
noise and hemodynamics, we estimated the noise ceiling for each region of interest (see STAR Methods) and scaled correlation coefﬁcients
separately for each region based on these estimates. Testing on these adjusted values demonstrated that the relative boost in performance of
the expansion-speciﬁc collision detection model over its stimulus-general version was larger in the superior colliculus than in V1 (61.7% of
Figure 1. Visual looming is encoded in the human superior colliculus
(A) Dynamic retinotopic mapping stimuli featuring clockwise and counterclockwise sweeping wedges (top) and contracting and expanding rings (bottom) used in
the fMRI experiment.
(B) The shallow convolutional neural network originally trained to detect imminent collision. The pre-trained convolutional units (left) ﬁlter each frame for outward
motion in the four cardinal directions and output a matrix of activations corresponding to the timecourse of looming motion at various points in the visual ﬁeld.
Panel adapted with permission from ref.39
(C) Exemplar timecourses used to ﬁt encoding models. Predictor variables are shown for a 5-cycle run of the expanding ring stimulus from two units at the center
(blue) and periphery (orange) of the visual ﬁeld. Units at the center tend to peak in activation early in the cycle, when the ring is in the center of the visual ﬁeld, and
units at the periphery tend to peak later in the cycle, when the ring has expanded.
(D) Model performance estimated using leave-one-subject-out cross-validated Pearson’s r between encoding model-predicted and observed BOLD. Gray points
and lines show model ﬁt estimates for each held-out subject. Black summary points and error bars show mean G 2 standard errors across cross-validation folds.
The expansion-speciﬁc model of superior colliculus activity outperforms a stimulus-general model on the same data (left subplot).
(E) Difference in model ﬁt between the stimulus-speciﬁc and stimulus-general encoding models for expanding rings.
(F) Voxelwise activity explained by the expansion-speciﬁc model across the superior colliculus.
(G) Voxelwise whole-brain, model-based connectivity with the collision detection encoding model trained on superior colliculus activity, expansion-speciﬁc
connectivity > all other conditions. Color bar shows corrected model-based connectivity (expanding ring > all other conditions). Statistical image is
thresholded at uncorrected p < 0.01 for display purposes; peaks are visible across the visual cortex, and in the amygdala. All brain visualizations are
displayed using radiologic convention.
ll
OPEN ACCESS
iScience 27, 109886, June 21, 2024
3
iScience
Article


## Page 5

noise ceiling, SE = 26.5%, p = 0.002, permutation test). Taken together, these results show that whereas V1 responses more generally encode
information about visual motion, regardless of its coherence and direction, patterns of BOLD activity in the human superior colliculus encode
representations of looming motion that has been linked to defensive behavior across species.
As the superior colliculus coordinates emotional behavior through its connections with distributed cortical and subcortical networks,48–50
we conducted a model-based connectivity analysis to determine which regions covaried with representations of looming encoded in the su-
perior colliculus. To identify covariation related to looming as opposed to nonspeciﬁc visual motion, we contrasted connectivity estimates
during expanding ring stimulation with those from the other experimental conditions. This analysis revealed widespread looming-related
covariation between superior colliculus and the visual cortex, parietal cortex, and amygdala. (uncorrected p < 0.01; permutation test; Fig-
ure 1G). These data suggest that information about looming is transmitted through a distributed network of regions including the amygdala,
consistent with observations from studies using naturalistic threats.51
Representations of looming predict defensive blinking in infants
To investigate whether the shallow convolutional network can characterize putatively fear- or threat-related behaviors that depend on supe-
rior colliculus function, we evaluated whether it predicts defensive blinking in human infants. Infants develop a propensity to blink in the face
of looming stimuli beginning at 4–6 months.30 Defensive blinking is selective to impending collision and could involve looming computations
like the ones modeled by our shallow neural network. If this is the case, and the shallow neural network contains representations of looming
that are functionally similar to those used by newborn infants, then infants’ tendency to blink while viewing looming objects should be related
to model-estimated collision probability on each frame.
Analyzing defensive blinking in response to visually looming objects (see Figure S4 for timeseries data), we found that collision probability
predicted blink count across all frames (beta = 0.427, SE = 0.038, Poisson regression, p < 0.001, permutation test; Figure 2D). To quantify the
strength of this relationship, we leveraged the neural network’s stronger activation to faster-approaching stimuli and tested whether infants
are similarly sensitive to the velocity of looming stimuli. We found that time points at the end of videos that consistently produced defensive
blinking (R5 blinks, see STAR Methods) could be accurately discriminated from other portions of the video (area under the ROC curve
Figure 2. Representations of looming predict defensive blinking to looming objects in infants
(A) Videos of looming objects generated by radially expanding static images over time to simulate the appearance of approach motion.
(B) Depiction of the convolutional neural network, which rectiﬁes and sums unit activations and then applies a softmax activation function to estimate collision
probability on each frame.
(C) Extracted collision probabilities for one representative video. Loess smoothing line and 95% conﬁdence error ribbon are shown for illustration.
(D) Videos with varying apparent times-to-contact showed that greater looming collision probability was associated with increased blinking on a given frame
(Poisson regression). Black curve shows model predictions with 95% conﬁdence interval ribbon.
(E) Receiver operating characteristic curves showing separability of ‘‘high-blink’’ (R5 blinks) and ‘‘low-blink’’ (<5 blinks) frames.
ll
OPEN ACCESS
4
iScience 27, 109886, June 21, 2024
iScience
Article


## Page 6

(AUROC) = 0.902, SE = 0.025, p < 0.001, permutation test), and that discriminability increased with object speed (Kendall’s t = 0.657, p = 0.046,
permutation test; Figure 2E).
Unlike models of superior colliculus responses, models of defensive blinking based on t and h were highly predictive (t: beta = 0.493,
SE = 0.041, p < 0.001; h: beta = 0.311, SE = 0.044, p < 0.001; permutation test; Table S2). Combining these variables with outputs from
the convolutional neural network improved prediction of blink count (DAIC = 149; see Table S2 and Figure S5). Together, these observations
show that simple computations based on optical expansion are sufﬁcient to predict velocity-sensitive human defensive responses to dynamic
looming stimuli, although among candidate models the convolutional neural network alone predicted superior colliculus responses to optical
expansion.
Representations of looming predict subjective emotion elicited by naturalistic videos
Although our ﬁndings are consistent with a large literature studying the neural basis of visual looming detection and accompanying defensive
behavior across species, it remains unclear how looming contributes to affective experience in humans. Looming is such a strong threat cue
that one can readily imagine experiencing an emotional response to, say, seeing a ball hurtle toward one’s head, even if the ball does not
actually make contact. Even though looming is well-established as an aversive and arousing experience,52,53 we still lack a mechanistic under-
standing of how looming relates to subjective experience. For example, looming might predominantly inform experience through its relation-
ship with valence and arousal. Alternatively, looming objects may be more speciﬁcally related to the experience of fear, because they activate
schemas of impending threat (e.g., approaching predators).7 To test these alternative hypotheses, we evaluated whether the convolutional
network could identify looming motion from a large database of over 2,000 naturalistic videos38 and whether activation in the network pre-
dicted emotion ratings to the same stimuli.
We trained a partial least squares classiﬁer to discriminate whether 1,315 clips from the database featured an object approaching the
camera, using responses to these stimuli from the looming motion model. We tested this classiﬁer on 332 held-out videos from the
same database and conﬁrmed that the model predicted human-coded looming above chance (AUROC = 0.739, chance = 0.5,
SE = 0.0007, p = 0.003, permutation test). To test the extent to which visual looming predicts self-reported emotional experience,
we then trained a 20-way linear discriminant analysis classiﬁer to identify the consensus emotion category of the same training videos
from their looming representations. We found that representations of looming only predicted the top consensus emotion category in
the same held-out testing set, though only weakly (16.9%, SE = 2.1%, chance = 13.0%, p = 0.010, permutation test; Figure 3D). The
AUROC was 0.538 (chance = 0.5, SE = 0.024, p = 0.024, permutation test), showing that looming information could discriminate be-
tween a subset of emotion classes, but could not fully disentangle the full set of emotions (see Figure S6 for mappings between speciﬁc
units and different emotion categories).
To assess which dimensions of experience were predicted by looming, we next quantiﬁed the extent to which speciﬁc emotion categories
(e.g., fear) and more general dimensions such as valence and arousal were the basis for classiﬁcation. To do so, we compared the similarity of
predictions in the 20-way classiﬁcation (Figure S8) to the similarity of self-report ratings of fear, valence, and arousal (a representational sim-
ilarity analysis;54 see Figures S9 and S10 and Table S3). This analysis revealed that the similarity of emotion categories in the looming-based
classiﬁer positively correlated with arousal (partial r = 0.169, p = 0.015, permutation test; Figure 3F) but not subjective fear (partial r = 0.110,
p = 0.121, permutation test) or valence (partial r = 0.047, p = 0.495, permutation test; Figure 3F). These ﬁndings suggest that in this set of
naturalistic videos, representations of looming motion that facilitate the detection of imminent collision discriminate emotional experiences
along a dimension of subjective arousal.
It is possible that information about looming motion is unique in its contribution to emotional experience. Motion and static visual features
(e.g., texture, shape, color) convey different types of threat-relevant information (e.g., threat imminence versus the source and type of threat55)
and are processed by distinct neural pathways. A rapidly approaching spider can evoke fear both due to its proximity and appearance.7 To
test whether the shallow convolutional neural network predicts emotion ratings independently from information related to static visual fea-
tures, we compared the performance of the looming motion-based emotion classiﬁer to a deep network that categorizes emotional situations
based on the static content of individual video frames.56 The ability of the looming classiﬁer and the static feature classiﬁer to classify emotion
categories were uncorrelated (Kendall’s t = 0.189, p = 0.122, permutation test). Differences in classiﬁcation accuracy and comparisons of
higher order dimensions (see Figure S7) suggest that some emotion categories (e.g., ‘joy’ and ‘fear’) were better predicted by the presence
of looming motion, whereas other categories (e.g., ‘craving’ and ‘desire’) were better predicted by the presence of speciﬁc visual features,
irrespective of how they move in the environment. These ﬁndings suggest that the experience of a looming threat may be aversive due to the
presence of other properties that may be integrated with motion (e.g., static visual features), rather than looming motion being inherently
aversive on its own.
DISCUSSION
Here, we demonstrate how an incredibly simple network architecture can have broad explanatory powers, accounting for different neurobe-
havioral measures across the lifespan. Recent advances using goal-driven optimization with much more complex architectures (on the order of
107 more parameters) to characterize cortical systems involved in object recognition, speech perception, and language processing57–59 have
been based on the idea that large, overparameterized models are necessary to explain the human mind. The present ﬁndings stand in
contrast to this approach, illustrating how a much simpler architecture trained with the right objective function—a computational primi-
tive—characterize multiple aspects of human behavior that are not explained by more complex models of cortical brain systems.56
ll
OPEN ACCESS
iScience 27, 109886, June 21, 2024
5
iScience
Article


## Page 7

We found that representations of optical expansion from a convolutional neural network for collision detection are encoded in human su-
perior colliculus activity. Although prior related research in humans has demonstrated that the superior colliculus responds to looming mo-
tion,33,34 it has not examined whether brain activity tracks optical variables that can be used to predict imminent collision. For instance, one
recent study used high-ﬁeld imaging to show that the superior colliculus responds more to objects on a collision course compared to near-
miss stimuli,34 but these responses could be equally well-explained by any number of computational accounts. Here, we found that represen-
tations from a shallow convolutional network predict colliculus responses to optical expansion that are consistent with parametric models
based on the optical variables t and h. Direct readouts of such representations in the superior colliculus could drive defensive behavior in hu-
mans, analogously to synaptic mechanisms identiﬁed in rodents that involve connections with the dorsal periaqueductal gray,49 with the amyg-
dala via the pulvinar nucleus,48 and with the ventral tegmental area.50 Future work is needed to determine if similar circuit-level mechanisms are
present in humans, and to characterize how the superior colliculus interacts with cortical and subcortical networks to coordinate defensive
behavior.60 In particular, future studies can test human responses to a broader range of loom speeds to chart the full range of looming repre-
sentations in the human superior colliculus, including speeds closer to thresholds that elicit freezing and escape behavior as in other animals.61
The present results also contribute to a growing body of evidence implicating the dorsal midbrain in emotional experience.62–64 Several
human neuroimaging studies have revealed that the superior colliculus responds to the aversiveness of visual images.65–68 It is possible that
observations from these studies originate from the same underlying representation of aversiveness. However, our present ﬁndings suggest
this is not likely the case, as the representations of looming that were encoded in the superior colliculus were largely unrelated to differences
in self-reported valence. Given the functional distinction between superﬁcial layers of the colliculus which receive inputs from visual cortex,
and deeper layers that contain more specialized loom-sensitive neurons,32 it is plausible that BOLD responses to static images observed in
past studies reﬂect a subset of neural population activity in the superior colliculus that is not specialized for motion.
In contrast to the typical focus on valence as a building block of emotion, the present work highlights the importance of arousal in explain-
ing emotional behavior. Studies that measure self-reported experience identify hedonic valence as the single dimension that best predicts the
semantic structure of emotion.69 Experience-sampling suggests that adults organize their emotions primarily using valence,70 and develop-
mental studies further show that infants and children ﬁrst distinguish facial expressions and linguistic concepts using valence.71,72 We found
that computations supporting a species-general behavior predominantly relate to subjective arousal, suggesting that primitive aspects of
phenomenal experience may be implemented at the level of the human midbrain64 before they contribute to cortical processes thought
Figure 3. Representations of looming predict subjective emotion evoked by naturalistic videos in adults
(A) Participants viewed short video clips depicting a variety of situations. Frames are shown from a stimulus with apparent looming motion.
(B) We passed the optical ﬂow from these videos through the same convolutional neural network and extracted unit activations from the convolutional layer.
(C) We trained a 20-way linear discriminant classiﬁer to predict the normative emotion category of each video from its looming activations.
(D) Distance between emotion categories in the collision detection emotion classiﬁer is unrelated to subjective valence, after adjusting for information from the
static feature-based emotion classiﬁer. Lines of best ﬁt for (D) and (E) are shown with 95% conﬁdence interval ribbons.
(E) Distance between emotion categories in the collision detection classiﬁer is associated with subjective arousal, after adjusting for information from the static
visual feature-based classiﬁer. Distance based on static visual features positively correlated with that of subjective fear, arousal, and valence (Table S2).
ll
OPEN ACCESS
6
iScience 27, 109886, June 21, 2024
iScience
Article


## Page 8

to produce conscious emotions.3,5 More generally, our ﬁndings caution against the assumption that certain stimuli which evoke defensive
behaviors produce experiences that resemble prototypical instances of fear in adults, because the computations that underlying these be-
haviors do not strongly predict subjective valence or fear in a broader array of naturalistic stimuli.
Here, we have revealed one way in which human emotions could be based on computations conserved across species. Although we have
focused on sensory evaluation, our observations provide a sketch of what understanding emotion might look like from a neurocomputational
perspective. Precisely characterizing species-general central emotion states4 by modeling how environmental and social affordances shape
behavior will likely explain a substantial portion of human emotion. By shifting the focus from a small number of apparently simple, interpret-
able variables to computationally explicit models that match the complexity of the brain,73 this approach promises to yield new insights into
the origins and nature of emotion.
Limitations of the study
We show that a simple neural network architecture modeled after a Drosophila looming detection circuit accounts for variation in human infant
defensive behavior and adult brain activation and subjective experience. We ﬁnd it striking that looming computations previously argued to be
similar across nonhuman animals36 also generalize to human emotion. However, we caveat that although invertebrate and vertebrate looming
detection systemsdo appeartoimplement similarcomputations, theyare not structurally homologous. Demonstrating homology would require
comparisons of in silico models of looming based on the inputs, computations, and outputs of vertebrate circuits like the mammalian superior
colliculus or the avian optical tectum. Further, our shallow neural network model yields a representation of looming that can modulate contin-
uously, including at levels too low to evoke defensive behavior. Our fMRI results indicate that human superior colliculus BOLD activity encodes
such representations of looming, and our self-report results indicate that the activation of such looming representations is associated with vari-
ation in subjective arousal. The looming stimuli examined did not evoke active escape behavior. Indeed, it may not be possible to study the brain
basisofescapebehaviorwithfMRI,astheheadmotionproducedbyrobust,naturalisticstimuliwouldlikelycausetask-correlatedmotionartifacts.
STAR+METHODS
Detailed methods are provided in the online version of this paper and include the following:
d KEY RESOURCES TABLE
d RESOURCE AVAILABILITY
B Lead contact
B Materials availability
B Data and code availability
d EXPERIMENTAL MODEL AND STUDY PARTICIPANT DETAILS
B Study 1: Retinotopic fMRI study
B Study 2: Infant behavioral study
B Study 3: Adult behavioral study
d METHOD DETAILS
B Implementation of the shallow convolutional neural network
B Study 1: Retinotopic fMRI study
B Study 2: Infant behavioral study
B Study 3: Adult behavioral study
d QUANTIFICATION AND STATISTICAL ANALYSIS
B Study 1: Retinotopic fMRI study
B Study 2: Infant behavioral study
B Study 3: Adult behavioral study
SUPPLEMENTAL INFORMATION
Supplemental information can be found online at https://doi.org/10.1016/j.isci.2024.109886.
ACKNOWLEDGMENTS
We thank Baohua Zhou for assistance with conﬁguring the shallow neural network model, and the ECCO Lab at Emory University for helpful
feedback on the project. This work was supported by the National Institutes of Health Institutional Research and Career Development Award
(IRACDA) grant K12GM000680 to MKT.
AUTHOR CONTRIBUTIONS
Conceptualization: P.A.K. and M.K.T. Methodology: P.A.K., S.F.L., and M.K.T. Investigation: V.A. Formal analysis: P.A.K. and M.K.T. Software:
M.K.T. Visualization: M.K.T. Project administration: P.A.K. and S.F.L. Supervision: P.A.K. and S.F.L. Writing – original draft: P.A.K. and M.K.T.
Writing – review and editing: V.A., P.A.K., S.F.L., and M.K.T.
ll
OPEN ACCESS
iScience 27, 109886, June 21, 2024
7
iScience
Article


## Page 9

DECLARATION OF INTERESTS
The authors declare that they have no competing interests.
Received: January 15, 2024
Revised: March 11, 2024
Accepted: April 30, 2024
Published: May 3, 2024
REFERENCES
1. Lindquist, K.A., Jackson, J.C., Leshin, J.,
Satpute, A.B., and Gendron, M. (2022). The
cultural evolution of emotion. Nat. Rev.
Psychol. 1, 669–681. https://doi.org/10.1038/
s44159-022-00105-4.
2. Barrett, L.F., and Bliss-Moreau, E. (2009).
Affect as a Psychological Primitive. Adv. Exp.
Soc. Psychol. 41, 167–218. https://doi.org/10.
1016/S0065-2601(08)00404-8.
3. LeDoux, J.E. (2022). As soon as there was life,
there was danger: the deep history of survival
behaviours and the shallower history of
consciousness. Philos. Trans. R. Soc. B 377,
20210292. https://doi.org/10.1098/rstb.
2021.0292.
4. Anderson, D.J., and Adolphs, R. (2014). A
Framework for Studying Emotions across
Species. Cell 157, 187–200. https://doi.org/
10.1016/j.cell.2014.03.003.
5. LeDoux, J.E., and Brown, R. (2017). A higher-
order theory of emotional consciousness.
Proc. Natl. Acad. Sci. USA 114, E2016–E2025.
https://doi.org/10.1073/pnas.1619316114.
6. Russell, J.A. (2003). Core affect and the
psychological construction of emotion.
Psychol. Rev. 110, 145–172. https://doi.org/
10.1037/0033-295X.110.1.145.
7. Riskind, J.H., Kelley, K., Harman, W., Moore,
R., and Gaines, H.S. (1992). The loomingness
of danger: Does it discriminate focal phobia
and general anxiety from depression? Cogn.
Ther. Res. 16, 603–622. https://doi.org/10.
1007/BF01175402.
8. Cosmides, L., and Tooby, J. (2000).
Evolutionary Psychology and the Emotions. In
Handbook of emotions, M. Lewis and J.M.
Haviland-Jones, eds. (Guilford).
9. LoBue, V., and Rakison, D.H. (2013). What we
fear most: A developmental advantage for
threat-relevant stimuli. Dev. Rev. 33, 285–303.
https://doi.org/10.1016/j.dr.2013.07.005.
10. Alvarez, L.C., and Pipitone, R.N. (2013).
Replication of LoBue & DeLoache (2008, PS,
Study 3).
11. Lazarevic, L.B., Puric, D., Zezelj, I.,
Belopavlovic, R., Bodroza, B., Colic, M.V.,
Ebersole, C.R., Ford, M., Orlic, A., Pedovic, I.,
et al. (2020). Many Labs 5: Registered
Replication of LoBue and DeLoache (2008).
Adv. Methods Pract. Psychol. Sci. 3, 377–386.
https://doi.org/10.1177/2515245920953350.
12. Bertels, J., Bourguignon, M., de Heering, A.,
Chetail, F., De Tie` ge, X., Cleeremans, A., and
Destrebecqz, A. (2020). Snakes elicit speciﬁc
neural responses in the human infant brain.
Sci. Rep. 10, 7443. https://doi.org/10.1038/
s41598-020-63619-y.
13. LoBue, V., and DeLoache, J.S. (2008).
Detecting the Snake in the Grass: Attention
to Fear-Relevant Stimuli by Adults and Young
Children. Psychol. Sci. 19, 284–289. https://
doi.org/10.1111/j.1467-9280.2008.02081.x.
14. O¨ hman, A., Flykt, A., and Esteves, F. (2001).
Emotion drives attention: Detecting the
snake in the grass. J. Exp. Psychol. Gen. 130,
466–478. https://doi.org/10.1037/0096-3445.
130.3.466.
15. Shibasaki, M., and Kawai, N. (2009). Rapid
Detection of Snakes by Japanese Monkeys
(Macaca fuscata): An Evolutionarily
Predisposed Visual System. J. Comp. Psychol.
123, 131–135. https://doi.org/10.1037/
a0015095.
16. O¨ hman, A., and Mineka, S. (2003). The
Malicious Serpent: Snakes as a Prototypical
Stimulus for an Evolved Module of Fear. Curr.
Dir. Psychol. Sci. 12, 5–9.
17. Van Le, Q., Isbell, L.A., Matsumoto, J.,
Nguyen, M., Hori, E., Maior, R.S., Tomaz, C.,
Tran, A.H., Ono, T., and Nishijo, H. (2013).
Pulvinar neurons reveal neurobiological
evidence of past selection for rapid detection
of snakes. Proc. Natl. Acad. Sci. USA 110,
19000–19005. https://doi.org/10.1073/pnas.
1312648110.
18. Adolphs, R. (2008). Fear, faces, and the
human amygdala. Curr. Opin. Neurobiol. 18,
166–172. https://doi.org/10.1016/j.conb.
2008.06.006.
19. Barrett, L.F. (2018). Seeing Fear: It’s All in the
Eyes? Trends Neurosci. 41, 559–563. https://
doi.org/10.1016/j.tins.2018.06.009.
20. McFadyen, J., Mattingley, J.B., and Garrido,
M.I. (2019). An afferent white matter pathway
from the pulvinar to the amygdala facilitates
fear recognition. Elife 8, e40766. https://doi.
org/10.7554/eLife.40766.
21. Rafal, R.D., Koller, K., Bultitude, J.H., Mullins,
P., Ward, R., Mitchell, A.S., and Bell, A.H.
(2015). Connectivity between the superior
colliculus and the amygdala in humans and
macaque monkeys: virtual dissection with
probabilistic DTI tractography.
J. Neurophysiol. 114, 1947–1962. https://doi.
org/10.1152/jn.01016.2014.
22. Elorette, C., Forcelli, P.A., Saunders, R.C., and
Malkova, L. (2018). Colocalization of Tectal
Inputs With Amygdala-Projecting Neurons in
the Macaque Pulvinar. Front. Neural Circuits
12, 91. https://doi.org/10.3389/fncir.2018.
00091.
23. Gibson, J.J. (2014). The Theory of
Affordances. In The Ecological Approach to
Visual Perception, Classic Edition
(Psychology Press), pp. 119–135. https://doi.
org/10.4324/9781315740218.
24. Card, G.M. (2012). Escape behaviors in
insects. Curr. Opin. Neurobiol. 22, 180–186.
https://doi.org/10.1016/j.conb.2011.12.009.
25. Schiff, W., Caviness, J.A., and Gibson, J.J.
(1962). Persistent Fear Responses in Rhesus
Monkeys to the Optical Stimulus of
‘‘Looming’’. Science 136, 982–983. https://
doi.org/10.1126/science.136.3520.982.
26. Wang, Y., and Frost, B.J. (1992). Time to
collision is signalled by neurons in the nucleus
rotundus of pigeons. Nature 356, 236–238.
https://doi.org/10.1038/356236a0.
27. Yilmaz, M., and Meister, M. (2013). Rapid
Innate Defensive Responses of Mice to
Looming Visual Stimuli. Curr. Biol. 23, 2011–
2015. https://doi.org/10.1016/j.cub.2013.
08.015.
28. Ball, W., and Tronick, E. (1971). Infant
Responses to Impending Collision: Optical
and Real. Science 171, 818–820. https://doi.
org/10.1126/science.171.3973.818.
29. King, S.M., Dykeman, C., Redgrave, P., and
Dean, P. (1992). Use of a Distracting Task to
Obtain Defensive Head Movements to
Looming Visual Stimuli by Human Adults in a
Laboratory Setting. Perception 21, 245–259.
https://doi.org/10.1068/p210245.
30. Yonas, A., Bechtold, A.G., Frankel, D.,
Gordon, F.R., McRoberts, G., Norcia, A., and
Sternfels, S. (1977). Development of
sensitivity to information for impending
collision. Percept. Psychophys. 21, 97–104.
31. Kayed, N.S., and van der Meer, A. (2000).
Timing strategies used in defensive blinking
to optical collisions in 5- to 7-month-old
infants. Infant Behav. Dev. 23, 253–270.
https://doi.org/10.1016/S0163-6383(01)
00043-1.
32. Basso, M.A., and May, P.J. (2017). Circuits for
Action and Cognition: A View from the
Superior Colliculus. Annu. Rev. Vis. Sci. 3,
197–226. https://doi.org/10.1146/annurev-
vision-102016-061234.
33. Billington, J., Wilkie, R.M., Field, D.T., and
Wann, J.P. (2011). Neural processing of
imminent collision in humans. Proc. Biol. Sci.
278, 1476–1481. https://doi.org/10.1098/
rspb.2010.1895.
34. Guo, F., Zou, J., Wang, Y., Fang, B., Zhou, H.,
Wang, D., He, S., and Zhang, P. (2024).
Human subcortical pathways automatically
detect collision trajectory without attention
and awareness. PLoS Biol. 22, e3002375.
https://doi.org/10.1371/journal.pbio.
3002375.
35. Liu, X., Huang, H., Snutch, T.P., Cao, P.,
Wang, L., and Wang, F. (2022). The Superior
Colliculus: Cell Types, Connectivity, and
Behavior. Neurosci. Bull. 38, 1519–1540.
https://doi.org/10.1007/s12264-022-00858-1.
36. Peek, M.Y., and Card, G.M. (2016).
Comparative approaches to escape. Curr.
Opin. Neurobiol. 41, 167–173. https://doi.
org/10.1016/j.conb.2016.09.012.
37. Sengupta, A., Kaule, F.R., Guntupalli, J.S.,
Hoffmann, M.B., Ha¨usler, C., Stadler, J., and
Hanke, M. (2016). A studyforrest extension,
retinotopic mapping and localization of
higher visual areas. Sci. Data 3, 160093.
https://doi.org/10.1038/sdata.2016.93.
38. Cowen, A.S., and Keltner, D. (2017). Self-
report captures 27 distinct categories of
emotion bridged by continuous gradients.
Proc. Natl. Acad. Sci. USA 114, E7900–E7909.
https://doi.org/10.1073/pnas.1702247114.
39. Zhou, B., Li, Z., Kim, S., Lafferty, J., and Clark,
D.A. (2022). Shallow neural networks trained
to detect collisions recover features of visual
ll
OPEN ACCESS
8
iScience 27, 109886, June 21, 2024
iScience
Article


## Page 10

loom-selective neurons. Elife 11, e72067.
https://doi.org/10.7554/eLife.72067.
40. Lee, D.N. (1976). A Theory of Visual Control of
Braking Based on Information about Time-to-
Collision. Perception 5, 437–459. https://doi.
org/10.1068/p050437.
41. Hatsopoulos, N., Gabbiani, F., and Laurent,
G. (1995). Elementary Computation of Object
Approach by a Wide-Field Visual Neuron.
Science 270, 1000–1003. https://doi.org/10.
1126/science.270.5238.1000.
42. Perry, V.H., and Cowey, A. (1984). Retinal
ganglion cells that project to the superior
colliculus and pretectum in the macaque
monkey. Neuroscience 12, 1125–1137.
https://doi.org/10.1016/0306-4522(84)
90007-1.
43. Kerschensteiner, D. (2022). Feature Detection
by Retinal Ganglion Cells. Annu. Rev. Vis. Sci.
8, 135–169. https://doi.org/10.1146/annurev-
vision-100419-112009.
44. Naselaris, T., Kay, K.N., Nishimoto, S., and
Gallant, J.L. (2011). Encoding and decoding
in fMRI. Neuroimage 56, 400–410. https://doi.
org/10.1016/j.neuroimage.2010.07.073.
45. Lee, K.H., Tran, A., Turan, Z., and Meister, M.
(2020). The sifting of visual information in the
superior colliculus. Elife 9, e50678. https://
doi.org/10.7554/eLife.50678.
46. Braddick, O.J., O’Brien, J.M.D., Wattam-Bell,
J., Atkinson, J., Hartley, T., and Turner, R.
(2001). Brain Areas Sensitive to Coherent
Visual Motion. Perception 30, 61–72. https://
doi.org/10.1068/p3048.
47. Andersen, R.A. (1997). Neural Mechanisms of
Visual Motion Perception in Primates. Neuron
18, 865–872. https://doi.org/10.1016/S0896-
6273(00)80326-8.
48. Wei, P., Liu, N., Zhang, Z., Liu, X., Tang, Y., He,
X., Wu, B., Zhou, Z., Liu, Y., Li, J., et al. (2015).
Processing of visually evoked innate fear by a
non-canonical thalamic pathway. Nat.
Commun. 6, 6756. https://doi.org/10.1038/
ncomms7756.
49. Evans, D.A., Stempel, A.V., Vale, R., Ruehle,
S., Leﬂer, Y., and Branco, T. (2018). A synaptic
threshold mechanism for computing escape
decisions. Nature 558, 590–594. https://doi.
org/10.1038/s41586-018-0244-6.
50. Zhou, Z., Liu, X., Chen, S., Zhang, Z., Liu, Y.,
Montardy, Q., Tang, Y., Wei, P., Liu, N., Li, L.,
et al. (2019). A VTA GABAergic Neural Circuit
Mediates Visually Evoked Innate Defensive
Responses. Neuron 103, 473–488.e6. https://
doi.org/10.1016/j.neuron.2019.05.027.
51. Mobbs, D., Yu, R., Rowe, J.B., Eich, H.,
FeldmanHall, O., and Dalgleish, T. (2010).
Neural activity associated with monitoring
the oscillating threat value of a tarantula.
Proc. Natl. Acad. Sci. USA 107, 20582–20586.
https://doi.org/10.1073/pnas.1009076107.
52. Bach, D.R., Neuhoff, J.G., Perrig, W., and
Seifritz, E. (2009). Looming sounds as warning
signals: The function of motion cues. Int. J.
Psychophysiol. 74, 28–33. https://doi.org/10.
1016/j.ijpsycho.2009.06.004.
53. Riskind, J.H., and Maddux, J.E. (1993).
Loomingness, Helplessness, and Fearfulness:
An Integration of Harm-Looming and Self-
Efﬁcacy Models of Fear. J. Soc. Clin. Psychol.
12, 73–89. https://doi.org/10.1521/jscp.1993.
12.1.73.
54. Kriegeskorte, N., Mur, M., and Bandettini, P.
(2008). Representational similarity analysis -
connecting the branches of systems
neuroscience. Front. Syst. Neurosci. 2, 4.
https://doi.org/10.3389/neuro.06.004.2008.
55. Branco, T., and Redgrave, P. (2020). The
Neural Basis of Escape Behavior in
Vertebrates. Annu. Rev. Neurosci. 43,
417–439. https://doi.org/10.1146/annurev-
neuro-100219-122527.
56. Kragel, P.A., Reddan, M.C., LaBar, K.S., and
Wager, T.D. (2019). Emotion schemas are
embedded in the human visual system. Sci.
Adv. 5, eaaw4358. https://doi.org/10.1126/
sciadv.aaw4358.
57. Yamins, D.L.K., and DiCarlo, J.J. (2016). Using
goal-driven deep learning models to
understand sensory cortex. Nat. Neurosci. 19,
356–365. https://doi.org/10.1038/nn.4244.
58. Richards, B.A., Lillicrap, T.P., Beaudoin, P.,
Bengio, Y., Bogacz, R., Christensen, A.,
Clopath, C., Costa, R.P., de Berker, A.,
Ganguli, S., et al. (2019). A deep learning
framework for neuroscience. Nat. Neurosci.
22, 1761–1770. https://doi.org/10.1038/
s41593-019-0520-2.
59. Saxe, A., Nelli, S., and Summerﬁeld, C. (2021).
If deep learning is the answer, what is the
question? Nat. Rev. Neurosci. 22, 55–67.
https://doi.org/10.1038/s41583-020-00395-8.
60. Mobbs, D., Headley, D.B., Ding, W., and
Dayan, P. (2020). Space, Time, and Fear:
Survival Computations along Defensive
Circuits. Trends Cogn. Sci. 24, 228–241.
https://doi.org/10.1016/j.tics.2019.12.016.
61. Yang, X., Liu, Q., Zhong, J., Song, R., Zhang,
L., and Wang, L. (2020). A simple threat-
detection strategy in mice. BMC Biol. 18, 93.
https://doi.org/10.1186/s12915-020-00825-0.
62. Coker-Appiah, D.S., White, S.F., Clanton, R.,
Yang, J., Martin, A., and Blair, R.J.R. (2013).
Looming animate and inanimate threats: The
response of the amygdala and
periaqueductal gray. Soc. Neurosci. 8,
621–630. https://doi.org/10.1080/17470919.
2013.839480.
63. Mobbs, D., Marchant, J.L., Hassabis, D.,
Seymour, B., Tan, G., Gray, M., Petrovic, P.,
Dolan, R.J., and Frith, C.D. (2009). From
Threat to Fear: The Neural Organization of
Defensive Fear Systems in Humans.
J. Neurosci. 29, 12236–12243. https://doi.
org/10.1523/JNEUROSCI.2378-09.2009.
64. Damasio, A., and Carvalho, G.B. (2013). The
nature of feelings: evolutionary and
neurobiological origins. Nat. Rev. Neurosci.
14, 143–152. https://doi.org/10.1038/
nrn3403.
65. Wang, Y.C., Bianciardi, M., Chanes, L., and
Satpute, A.B. (2020). Ultra High Field fMRI of
Human Superior Colliculi Activity during
Affective Visual Processing. Sci. Rep. 10, 1331.
https://doi.org/10.1038/s41598-020-57653-z.
66. Kragel, P.A., Ceko, M., Theriault, J., Chen, D.,
Satpute, A.B., Wald, L.W., Lindquist, M.A.,
Feldman Barrett, L., and Wager, T.D. (2021). A
human colliculus-pulvinar-amygdala pathway
encodes negative emotion. Neuron 109,
2404–2412.e5. https://doi.org/10.1016/j.
neuron.2021.06.001.
67. Ceko, M., Kragel, P.A., Woo, C.-W., Lo´ pez-
Sola`, M., and Wager, T.D. (2022). Common
and stimulus-type-speciﬁc brain
representations of negative affect. Nat.
Neurosci. 25, 760–770. https://doi.org/10.
1038/s41593-022-01082-w.
68. Morris, J.S., deBonis, M., and Dolan, R.J.
(2002). Human Amygdala Responses to
Fearful Eyes. Neuroimage 17, 214–222.
https://doi.org/10.1006/nimg.2002.1220.
69. Jackson, J.C., Watts, J., Henry, T.R., List,
J.-M., Forkel, R., Mucha, P.J., Greenhill, S.J.,
Gray, R.D., and Lindquist, K.A. (2019).
Emotion semantics show both cultural
variation and universal structure. Science 366,
1517–1522. https://doi.org/10.1126/science.
aaw8160.
70. Barrett, L.F. (2006). Valence is a basic building
block of emotional life. J. Res. Pers. 40, 35–55.
https://doi.org/10.1016/j.jrp.2005.08.006.
71. Nook, E.C., Sasse, S.F., Lambert, H.K.,
McLaughlin, K.A., and Somerville, L.H. (2017).
Increasing verbal knowledge mediates
development of multidimensional emotion
representations. Nat. Hum. Behav. 1,
881–889. https://doi.org/10.1038/s41562-
017-0238-7.
72. Nelson, C.A., and De Haan, M. (1997). A
neurobehavioral approach to the recognition
of facial expressions in infancy. In The
Psychology of Facial Expression, J.A. Russell
and J.M. Ferna´ndez-Dols, eds. (Cambridge
University Press), pp. 176–204. https://doi.
org/10.1017/CBO9780511659911.010.
73. Jolly, E., and Chang, L.J. (2019). The Flatland
Fallacy: Moving Beyond Low–Dimensional
Thinking. Top. Cogn. Sci. 11, 433–454.
https://doi.org/10.1111/tops.12404.
74. OpenCV (2022, Version 4.6.0.
75. Farneba¨ck, G. (2003). Two-frame motion
estimation based on polynomial expansion.
In Lecture Notes in Computer Science
(Springer), pp. 363–370.
76. PyTorch (2022, Version 1.12.1.
77. Schneider, K.A., and Kastner, S. (2005). Visual
Responses of the Human Superior Colliculus:
A High-Resolution Functional Magnetic
Resonance Imaging Study. J. Neurophysiol.
94, 2491–2503. https://doi.org/10.1152/jn.
00288.2005.
78. McIlwain, J.T. (1991). Distributed spatial
coding in the superior colliculus: A review.
Vis. Neurosci. 6, 3–13. https://doi.org/10.
1017/S0952523800000857.
79. FIL Methods Group (2020 (SPM12).
80. MathWorks (2022). MATLAB. Version R2022a.
81. Friston, K.J., Ashburner, J., Frith, C.D., Poline,
J., Heather, J.D., and Frackowiak, R.S.J.
(1995). Spatial Registration and
Normalization of Images. Hum. Brain Mapp.
3, 165–189.
82. Ashburner, J., Neelin, P., Collins, D.L., Evans,
A., and Friston, K. (1997). Incorporating Prior
Knowledge into Image Registration.
Neuroimage 6, 344–352. https://doi.org/10.
1006/nimg.1997.0299.
83. Ashburner, J., and Friston, K.J. (1999).
Nonlinear spatial normalization using basis
functions. Hum. Brain Mapp. 7, 254–266.
https://doi.org/10.1002/(SICI)1097-
0193(1999)7:4<254::AID-HBM4>3.0.CO;2-G.
84. Neuroimaging_Pattern_Masks (2023).
Cognitive and Affective Neuroscience
Laboratory.
85. Glasser, M.F., Coalson, T.S., Robinson, E.C.,
Hacker, C.D., Harwell, J., Yacoub, E., Ugurbil,
K., Andersson, J., Beckmann, C.F., Jenkinson,
M., et al. (2016). A multi-modal parcellation of
human cerebral cortex. Nature 536, 171–178.
https://doi.org/10.1038/nature18933.
86. Adobe Systems. Adobe Photoshop CS5.
San Jose, CA, USA.
87. Bacher, L.F., and Smotherman, W.P. (2004).
Systematic temporal variation in the rate of
spontaneous eye blinking in human infants.
Dev. Psychobiol. 44, 140–145.
88. Rohart, F., Gautier, B., Singh, A., and Leˆ Cao,
K.A. (2017). mixOmics: An R package for
‘omics feature selection and multiple data
integration. PLoS Comput. Biol. 13,
e1005752. https://doi.org/10.1371/journal.
pcbi.1005752.
89. Kuhn, M., and Wickham, H. (2020).
Tidymodels: A Collection of Packages for
ll
OPEN ACCESS
iScience 27, 109886, June 21, 2024
9
iScience
Article


## Page 11

Modeling and Machine Learning Using
Tidyverse Principles. Version 1.1.0.
90. R Core Team (2022). R: A Language and
Environment for Statistical Computing (R
Foundation for Statistical Computing).
Version 4.2.1.
91. Esterman, M., Tamber-Rosenau, B.J., Chiu,
Y.-C., and Yantis, S. (2010). Avoiding non-
independence in fMRI data analysis: Leave
one subject out. Neuroimage 50, 572–576.
https://doi.org/10.1016/j.neuroimage.2009.
10.092.
92. Sun, H., and Frost, B.J. (1998). Computation
of different optical variables of looming
objects in pigeon nucleus rotundus neurons.
Nat. Neurosci. 1, 296–303. https://doi.org/10.
1038/1110.
93. Winkler, A.M., Webster, M.A., Vidaurre, D.,
Nichols, T.E., and Smith, S.M. (2015). Multi-
level block permutation. Neuroimage 123,
253–268. https://doi.org/10.1016/j.
neuroimage.2015.05.092.
94. Freedman, D., and Lane, D. (1983). A
Nonstochastic Interpretation of Reported
Signiﬁcance Levels. J. Bus. Econ. Stat. 1,
292–298. https://doi.org/10.2307/1391660.
95. Anderson, M.J., and Robinson, J. (2001).
Permutation Tests for Linear Models. Aust. N.
Z. J. Stat. 43, 75–88. https://doi.org/10.1111/
1467-842X.00156.
ll
OPEN ACCESS
10
iScience 27, 109886, June 21, 2024
iScience
Article


## Page 12

STAR+METHODS
KEY RESOURCES TABLE
RESOURCE AVAILABILITY
Lead contact
Further information and requests for resources should be directed to and will be fulﬁlled by the lead contact, Philip Kragel (pkragel@
emory.edu).
Materials availability
This study did not generate new unique reagents.
Data and code availability

Study 1 and Study 3 analyzed existing, publicly available data. These accession numbers for the datasets are listed in the key resources
table. Study 2’s data have been deposited at OSF and are publicly available as of the date of publication. The DOI is listed in the key
resources table.

All original code and model weights have been uploaded to GitHub and are publicly available as of the date of publication. The URL is
listed in the key resources table.

Any additional information required to reanalyze the data reported in this paper is available from the lead contact upon request.

All data and materials that were generated for this study are posted on Open Science Framework and all code is posted on GitHub. The
URLs are listed in the key resources table.
EXPERIMENTAL MODEL AND STUDY PARTICIPANT DETAILS
Study 1: Retinotopic fMRI study
This study analyzed an existing, publicly available dataset of retinotopic mapping fMRI scans collected on 15 healthy adult participants37
(mean age = 29.4 years, range = 21–39, 6 females; race/ethnicity were not reported; see key resources table for dataset information). No sam-
ple size estimation procedure was reported by the dataset’s original authors.
Study 2: Infant behavioral study
A total of 62 healthy infants participated in this study. Of the 62 infants, four infants looked less than 35% of the (total) trial durations and, thus,
were excluded from subsequent analyses. An additional 12 infants failed to complete the study due to fussiness or technical difﬁculties, leav-
ing 58 infants in the ﬁnal sample (range = 6.2–11.7 months, M = 8.7 months; 22 boys and 36 girls; race/ethnicity not reported). Target sample
size was based on similar prior studies. Parents provided written informed consent on behalf of their infants. All procedures were approved by
the Institutional Review Board at Emory University.
Study 3: Adult behavioral study
This study analyzed an existing, publicly available dataset of short, naturalistic videos and normative emotion ratings38 provided by a total of
853 healthy adult participants (mean age = 36 years, 403 females, race/ethnicity not reported; see key resources table for dataset information).
No sample size estimation procedure was reported by the dataset’s original authors.
REAGENT or RESOURCE
SOURCE
IDENTIFIER
Deposited data
Retinotopic mapping fMRI data
studyforrest project
OpenNeuro: https://doi.org/10.18112/openneuro.ds000113.v1.3.0
Infant blink count behavioral data
This paper
OSF: https://doi.org/10.17605/osf.io/as4vm
Naturalistic videos and emotion rating data
Cowen and Keltner, 201738
Available upon request from corresponding
author at https://goo.gl/forms/XErJw9sBeyuOyp5Q2
Software and algorithms
Neural network model & statistical code
This paper
https://github.com/ecco-laboratory/ﬂynet-looming
SPM12
Wellcome Trust Centre
for Neuroimaging
https://www.ﬁl.ion.ucl.ac.uk/spm/
software/spm12/; RRID:SCR_007037
CANLab Core Tools
CAN Lab, Dartmouth College
https://github.com/canlab/CanlabCore/
ll
OPEN ACCESS
iScience 27, 109886, June 21, 2024
11
iScience
Article


## Page 13

METHOD DETAILS
Implementation of the shallow convolutional neural network
We implemented a shallow neural network model originally built to model the Drosophila LPLC2 pathway and trained to identify whether
dynamic stimuli are on a collision course with the viewer.39 The network takes in a 4D timecourse of visual motion in each of the 4 cardinal
directions. The network has two layers that operate on each frame of the timeseries: one convolutional layer, which, once trained, passes
a 12 3 12 px outward motion ﬁlter over the visual ﬁeld to generate a 256-unit representation of looming, and one summation layer, which
rectiﬁes, sums, and applies a softmax activation function to estimate looming collision probability for that frame.
For each of the studies described below, we ﬁrst resized the study’s stimuli to 132 3 132 px to yield 256 convolutional units given the ﬁlter
size and stride parameters. We then estimated each stimulus’ optical ﬂow using the Farneback algorithm as implemented by OpenCV74,75
and re-cast the optical ﬂow from 2D (positive/negative motion in the x and y directions) to 4D (positive motion in each of the cardinal direc-
tions, hereafter referred to as cardinal ﬂow) in accordance with the model.
We then adapted the pre-trained collision detection model from operating on ﬂy-like to human-like vision, instantiating it as a 2D convolu-
tional neural network in PyTorch76 that passes the pre-trained 12 3 12 px outward motion ﬁlter over the optical ﬂow from a human-watchable
video stimulus, with 11 px stride and 0 px padding, to replicate the unit-to-unit visual ﬁeld overlap from the original ﬂy-like model. We left the
summation layer identical to the original model. Finally, we passed each stimulus’ cardinal ﬂow through the modiﬁed collision detection
model and extracted representations of looming at various stages of the model to map onto human responses (described further for
each study below).
Study 1: Retinotopic fMRI study
Overview
In Study 1, we tested whether looming representations in our model were encoded in human superior colliculus BOLD activity. We leveraged
whole-brain fMRI responses to dynamic visual stimuli used for retinotopic mapping to maximize potential looming-related variance in supe-
rior colliculus activity. We hypothesized that BOLD responses to visual stimuli would be driven by two types of neural populations: retinotopi-
cally organized populations in superﬁcial layers that respond irrespective of motion direction77 and populations in intermediate and deep
layers of the colliculus that respond primarily to expanding radial motion.78 We tested this hypothesis by ﬁtting multivariate encoding models
to predict patterns of colliculus response using the shallow convolutional neural network for collision detection as a feature extractor. If the
human superior colliculus contains neural populations that code for visual looming, and they are engaged by the retinotopic videos, then
encoding model performance should be the highest on models trained and tested speciﬁcally on video stimuli that include optical expansion.
Experimental paradigm and stimuli
Participants were scanned while viewing four types of dynamic retinotopy stimuli: clockwise and counterclockwise sweeping wedges, and
contracting and expanding rings. The stimuli cycled across the visual ﬁeld with a period of 32 s, with ﬁve repetitions per run, with each run
lasting 3 min. In particular, the ring stimuli expanded/contracted linearly at a rate of 1.9/sec.
MRI preprocessing
fMRI data were preprocessed using SPM12 in MATLAB.79,80 Images were ﬁrst realigned to the ﬁrst image of the series using a six parameter,
rigid-body transformation.81 The realigned images were then normalized to MNI152 space using a 12-parameter afﬁne transformation fol-
lowed by nonlinear deformations using a three-dimensional discrete cosine transform basis set, as implemented in SPM.82,83 No additional
smoothing was applied to the normalized images. Normalized images were subsequently temporally bandpass ﬁltered with cutoff fre-
quencies centered around the stimulus frequency (0.667/32 and 2/32 Hz).
Measurements
We extracted preprocessed BOLD timeseries from a hand-drawn ROI of the superior colliculus,66,84 as well as an ROI of V1 from a multimodal
cortical parcellation85 as a positive control.
Study 2: Infant behavioral study
Overview
In Study 2, we tested whether looming representations in our model could predict infant defensive blinking in response to looming stimuli.
Procedure and stimuli
Infants were tested individually in a dimly lit, soundproof room. Each infant sat in a highchair or on his/her parent’s lap at a distance of approx-
imately 60 cm from a large projection screen (92.5 3 67.5 cm). Parents were instructed to keep their eyes closed and to refrain from interacting
with their infants during the study, except for soothing them if they became fussy. Stimuli were videos of a looming two-dimensional image,
which were rear-projected onto the screen at eye-level to the infant. Each infant’s face was recorded for later coding using a concealed
ll
OPEN ACCESS
12
iScience 27, 109886, June 21, 2024
iScience
Article


## Page 14

camcorder placed just under the projection screen. Video feed was transmitted directly to a computer in an adjoining room where an exper-
imenter monitored the session remotely.
Images in each of the videos were of individual animals (snakes, spiders, butterﬂies, and rabbits; two of each type). Images were selected
from an Internet search for their high quality and to match roughly in color and brightness. Images were cropped, resized, and presented
against a uniform gray background using Adobe Photoshop CS5.86 Looming videos were created in MATLAB by manipulating the rate of
expansion of the image size.
Each trial was experimenter controlled, beginning with a centrally presented attention-getter (e.g., swirling star; randomly selected across
trials) that played until infants oriented to the screen. A looming video immediately followed. Each video began with a two-dimensional image
that expanded symmetrically and linearly to a maximum size of 75  3 59  (visual angle). There was a 1 s inter-trial interval (ITI) consisting of a
gray screen. Videos were created such that the virtual animal approached the infant at one of six velocities, indicating times-to-contact of 3, 4,
5, 6, 7, or 8 s. Velocity was negatively correlated with approach time, such that as approach time increased, the velocity of the virtual object
decreased. Infants were presented with a total of 48 trials (randomized).
Video coding
High quality videos of each infant were saved digitally. Video frames were coded at 33.33 ms intervals by observers blind to the stimuli pre-
sented to infants. All videos were coded by one observer for blinks (and total looking time) on each trial. Eye closures were counted as blinks if
the lids of the opened eyes covered at least half of the exposed eye surface.87 Incomplete eye closures associated with large head turns were
not counted as blinks. Also not counted as blinks were eye closures associated with yawns, sneezes, coughs, and hand movements to or near
the face or mouth. A second observer coded a random sample of videos (20%) to assess reliability. Inter-observer reliability was high for the
coding of both blinks and looking times (rs > 0.9).
Measurements
For each looming video stimulus presented to the infants, we summed the total number of blinks made by all infants on each coded frame to
generate one timecourse of blink counts per video stimulus. We then further summed the blink count timecourses for each video of a given
time-to-contact duration to generate one timecourse of total blink counts per time-to-contact condition (Figure S4).
Study 3: Adult behavioral study
Overview
In Study 3, we tested whether looming representations in our model could predict normative self-report affect ratings in response to short,
naturalistic videos.
Stimuli and behavioral measurements
Each short, naturalistic video was rated by approximately 10 raters (range = [9, 17]), each of whom reported the categorical emotions elicited
by the video, as well as 9-point valence and arousal ratings. For each video, we took its most frequently selected categorical emotion label,
and its mean valence and arousal ratings. Videos spanned 20 consensus emotion categories. To quantify ground-truth looming, author PAK
coded each video for the presence of objects approaching the camera.
QUANTIFICATION AND STATISTICAL ANALYSIS
Study 1: Retinotopic fMRI study
We passed sequences of cardinal ﬂow from each retinotopic mapping stimulus through the convolutional layer of the collision detection
model. We then convolved the timecourse of units in the shallow convolutional neural network to each of the retinotopy stimuli with the
SPM double-gamma hemodynamic response function to generate a multivariate encoding model of looming-related BOLD signal. We
applied partial least-squares (PLS) regression, implemented through the mixOmics and tidymodels packages in R,88–90 to map our loom-
ing-predicted BOLD onto observed multivariate BOLD from each ROI separately. We trained the PLS multivariate encoding model on
data from 14 participants and then assessed model ﬁt as the Pearson correlation between PLS-predicted BOLD and observed BOLD in
the last held-out participant. We cross-validated model ﬁt in a leave-one-subject-out manner by repeating this process for every participant
and averaging across repetitions.91
Because the collision detection model contains units that tile the visual ﬁeld, the resulting BOLD encoding model encodes both retino-
topic responses and responses to looming motion. Accordingly, to test for looming speciﬁcity, we compared performance between two types
of encoding models: a stimulus-general model, with the PLS mapping trained on data from all four stimulus types, and stimulus-speciﬁc
models, with the PLS mapping trained separately on data from each stimulus type. We expected the stimulus-speciﬁc model trained on ex-
panding ring motion would predict superior colliculus responses more so than other stimulus-speciﬁc models, or the stimulus-general model.
In order to clarify the nature of the looming representations in our BOLD encoding model, we also compared performance between the
neural network encoding model and encoding models predicting BOLD responses as a function of the optical looming variables t and h. For
the retinotopic ring stimuli, we calculated timecourses using t and h based on the visual angle parameters at which the videos were presented
ll
OPEN ACCESS
iScience 27, 109886, June 21, 2024
13
iScience
Article


## Page 15

to participants, using formulas from.92 We ﬁt this optical variable encoding model, along with several variations using different combinations
of predictors (Table S1), using the same method described above.
In order to facilitate comparisons of model performance between the superior colliculus and V1, we adjusted model ﬁt correlations by the
noise ceilings from their respective ROIs. In each ROI, we estimated the noise ceiling on each cross-validation fold by calculating the Pearson
correlation between the average timeseries of that fold’s training participants and the held-out participant and averaging across folds. We
estimated a separate noise ceiling for each retinotopic stimulation condition and used the highest noise ceiling to normalize all encoding
model ﬁt estimates.
We generated block permutation distributions against which to compare the model ﬁt correlations by randomizing TRs of observed BOLD
within each stimulus cycle to preserve the autocorrelation structure of the data.93 We then re-estimated each shufﬂed model ﬁt correlation
over 5,000 iterations to generate p-values for inference.
Finally, in order to examine how looming threat information computed by the superior colliculus might be transmitted to other regions, we
conducted an exploratory whole-brain model-based connectivity analysis, using the collision detection encoding model trained on superior
colliculus activity as a seed. This model-based connectivity analysis allowed us to estimate whole-brain connectivity with the looming-speciﬁc
component of superior colliculus activity, as indexed by the expansion-speciﬁc collision detection encoding model. First, we correlated the
expansion-speciﬁc trained model’s predicted timecourse of BOLD response to expanding ring stimulation with the timecourses observed in
each voxel, using the same leave-one-subject-out cross-validation structure that we used to assess encoding model ﬁt. Then, we calculated
the same model-based superior colliculus connectivity in each of the other three stimulation conditions using each condition’s stimulus-spe-
ciﬁc predicted superior colliculus timecourse as a seed, and averaged the three timecourses together within each voxel and cross-validation
fold to yield an estimate of baseline connectivity in the non-expansion conditions. Finally, we calculated the difference in connectivity between
expansion and the average of the other three conditions within each cross-validation fold, averaging across folds to yield an overall corrected
model-based connectivity map.
We generated permutation distributions against which to compare model-based connectivity estimates by randomizing the sign of each
fold’s connectivity difference estimate, and then averaging those sign-randomized estimates across folds to yield a permuted connectivity
difference. As before, we re-estimated each voxel’s permuted connectivity estimate over 5,000 iterations to generate p-values for inference.
Study 2: Infant behavioral study
We extracted the cardinal optical ﬂow for each looming video stimulus at a frame rate of 33.33 ms/frame, and then passed the ﬂow videos
through the convolutional and summation layers of the collision detection model to generate a 1D timecourse of estimated collision prob-
ability for each stimulus. We then averaged the timecourses for each video of a given time-to-contact duration to generate one timecourse of
looming collision probability per time-to-contact duration.
Then, we used Poisson regression to predict framewise blink counts as a function of framewise collision probability and condition-wise
time-to-contact. We generated a permutation distribution against which to compare the coefﬁcient for collision probability by randomizing
blink counts across all trials. We then re-ﬁt the Poisson regression and extracted the shufﬂed coefﬁcient over 10,000 iterations to generate
p-values for inference.
Similar to Study 1, we compared this Poisson model to another Poisson model with the optical variables t and h added as predictors, in
order to clarify the nature of the looming representations encoded in collision probability. First, we estimated timecourses of t and h for each
stimulus video, based on the visual angle parameters at which the videos were presented to participants. We then included these timecourses
as predictors in an expanded Poisson model. We ran this model as a principal components regression, applying PCA to the three collision
variables (collision probability, t, and h) and including the three rotated components as predictors in the Poisson regression along with con-
dition-wise time-to-contact.
Finally, we examined the potentially threshold-like relationship between blink counts and collision probability by using collision probability
to classify frames as ‘‘high-blink’’ (5 or more blinks across infants/stimuli on that frame, to isolate trials where blinks were most likely to be
defensive) or ‘‘low-blink’’ (fewer than 5 blinks). We calculated the area under the receiver operating curve (AUROC) both overall and as a func-
tion of time-to-contact condition, using tools implemented in the tidymodels family of R packages.89 We evaluated whether AUROC varied
with time to collision by calculating Kendall’s t between the observed rank-ordering of times-to-contact based on AUROC (highest to lowest)
and duration (3 s–7 s). We generated a non-parametric sampling distribution for overall AUROC by bootstrap resampling and re-calculating
AUROC over 10,000 iterations. We also generated a permuted distribution against which to compare the observed AUROC by randomizing
binarized blink counts across all trials and re-estimating AUROC over 10,000 iterations. Similarly, we generated a block permutation distribu-
tion against which to compare the observed Kendall rank correlation between time-to-contact and AUROC by randomizing binarized blink
count within each time-to-contact condition. We then re-estimated the shufﬂed AUROC for each time-to-contact and re-calculated Kendall’s
t over 10,000 iterations to generate p-values for inference.
Study 3: Adult behavioral study
We resampled each video stimulus to a standard frame rate of 10 fps and passed the cardinal ﬂow from each video stimulus through the con-
volutional layer of the collision detection model to yield 256 timecourses of activations per video. Next, we ﬂattened each video’s looming
representation along the time dimension. The original looming model tends to increase activation over time for ‘‘hit’’ stimuli as the stimuli
approach the viewer and activate an increasing number of units across the visual ﬁeld. Accordingly, we assumed that stronger looming
ll
OPEN ACCESS
14
iScience 27, 109886, June 21, 2024
iScience
Article


## Page 16

activations woullid have a more positive slope over time. We calculated the linear slope of each unit’s timecourse over time, generating a
looming representation of 256 unit activation slopes per video.
We applied partial least squares classiﬁcation, implemented through the mixOmics and tidymodels packages in R, to classify whether each
video was coded as containing looming motion using its 256 looming activation slopes. We trained the partial least squares classiﬁer using a
prior training split of 1,315 videos.56 We then applied linear discriminant analysis, implemented through the MASS and tidymodels packages
in R, to classify each video’s consensus emotion category (out of 20) using its 256 looming activation slopes. We trained the linear discriminant
classiﬁer using the same prior training split as the partial least squares looming classiﬁer. All model performance statistics are reported as
evaluated on the associated prior held-out testing split of 332 videos.
We compared the emotion classiﬁcation performance of the looming model to the performance of a deep convolutional neural network
originally trained to classify stimulus-elicited emotions based on their static image features.56 Because that model was originally used to iden-
tify the emotion categories of individual video frames, we calculated video-wise category predictions by averaging each of the 20 emotion
class probabilities across each frame of the video and taking the emotion category with the highest across-video average probability. We
generated non-parametric sampling distributions for our statistics by bootstrapping and re-calculating classiﬁcation accuracy, over 10,000
iterations. We also generated non-parametric null distributions against which to compare classiﬁcation accuracies by permuting the
consensus emotion category labels across videos and re-calculating shufﬂed classiﬁcation accuracy, over 10,000 iterations. Finally, we gener-
ated a permutation distribution against which to compare Kendall’s t for category rankings by model AUROC by randomizing consensus
emotion category label the across videos. We then re-estimated shufﬂed category-speciﬁc AUROCs for both the looming model and the
static image model and re-calculated a shufﬂed Kendall’s t over 10,000 iterations to generate p-values for inference.
We used representational similarity analysis54 to assess whether the representations learned by the emotion classiﬁcation models encoded
information consistent with valence and/or arousal. For both the looming motion-based and static visual feature-based classiﬁers, we calcu-
lated the representational distance between every pair of emotion categories. For a given emotion classiﬁcation model and pair of emotion
categories, we calculated the distance as 1 minus the average pairwise Pearson correlation between the 20 class probabilities for any two
videos from those two emotion categories. We then used linear regression to predict between-category distances in mean valence ratings
from distances from both convolutional networks, allowing us to assess the independent contributions of information gleaned from optical
ﬂow and static visual features. From this regression, we estimated the partial correlation coefﬁcients that identify the relationship between
representations of looming and valence (accounting for static visual features), and between representations of static visual features and
valence (accounting for looming). We conducted similar regressions using mean ratings of arousal and fear and extracted partial correlation
coefﬁcients using the same approach. We generated permutation distributions against which to compare these partial correlation coefﬁ-
cients,94,95 calculating randomized partial correlation coefﬁcients over 10,000 iterations to generate p-values for inference.
ll
OPEN ACCESS
iScience 27, 109886, June 21, 2024
15
iScience
Article


