# (2025) Object representations drive emotion schemas across a large and diverse set of daily-life scenes

**Source:** (2025) Object representations drive emotion schemas across a large and diverse set of daily-life scenes.pdf

---

## Page 1

communications biology
Article
A Nature Portfolio journal
https://doi.org/10.1038/s42003-025-08145-1
Object representations drive emotion
schemas across a large and diverse set of
daily-life scenes
Check for updates
Chuanji Gao
1
, Susan Ajith2,3 & Marius V. Peelen
4
The rapid emotional evaluation of objects and events is essential in daily life. While visual scenes
reliably evoke emotions, it remains unclear whether emotion schemas evoked by daily-life scenes
depend on object processing systems or are extracted independently. To explore this, we collected
emotion ratings for 4913 daily-life scenes from 300 participants, and predicted these ratings from
representations in deep neural networks and functional magnetic resonance imaging (fMRI) activity
patterns in visual cortex. AlexNet, an object-based model, outperformed EmoNet, an emotion-based
model, in predicting emotion ratings for daily-life scenes, while EmoNet excelled for explicitly
evocative scenes. Emotion information was processed hierarchically within the object recognition
system, consistent with the visual cortex’s organization. Activity patterns in the lateral occipital
complex (LOC), an object-selective region, reliably predicted emotion ratings and outperformed other
visual regions. These ﬁndings suggest that the emotional evaluation of daily-life scenes is mediated by
visual object processing, with additional mechanisms engaged when object content is uninformative.
The rapid emotional evaluation of objects and events facilitates the pursuit
of valuable resources and the avoidance of potential harm. Accordingly,
visual scenes readily and reliably evoke feelings of happiness, disgust, awe,
horror, amusement, etc1–6. Previous research has shown that there is
agreement between observers in the emotion category labels they use to
judge their emotional experience when viewing emotionally evocative sti-
muli (e.g., scenes showing births, risky stunts, sexual acts1,2). For example,
one study found that 2185 emotionally evocative short videos consistently
elicited 27 distinct emotion categories, which provided a more accurate
representation of emotional experiences than ratings on 14 affective
dimensions, such as valence and arousal1. These ﬁndings prompt further
investigationintotheneuralandcomputationalmechanismsunderlyingthe
evocation of diverse emotions by visual scenes.
One possibility is that emotions are inferred from the objects, object
states, and/or object relations that are present in a scene. For example, a scene
showingapersonholdingaguncouldevokefeelingsoffear,sadness,orhorror,
whileasceneshowingpreparedfoodonaplatecouldevokefeelingsofcraving.
On this account, emotional experience would follow the recognition of the
visual scene, with the visual processing stage of the process relying on known
mechanisms of object and scene recognition in ventral temporal cortex7–11.
Alternatively, emotions may be evoked by visual cues before, or in
parallel with, object recognition. Certain visual features could be
consistently associated with speciﬁc emotions and evoke emotions without
requiring object recognition12,13. Evidence for this account comes from a
study showing that a convolutional neural network trained to categorize
emotions from visual images (EmoNet) accurately predicts emotion ratings
of human observers2. Importantly, EmoNet outperformed emotion cate-
gorization usingobject category labels fromAlexNet, a convolutionalneural
network trained to categorize objects in scenes14,15. EmoNet was created by
keeping all layers of AlexNet ﬁxed, except for the last fully connected layer,
which was retrained. This adjustment shifted the focus from classifying
images into 1000 object categories to classifying images into 20 emotion
categories. The connections between sensory features and emotions are
referred to as emotion schemas2. Furthermore, the study showed that pat-
terns of visual cortical activity could be used to decode human emotion
ratings. Together, these ﬁndings suggest that emotion may serve as an
organizing principle of the visual system, with emotion schemas being
extracted from visual input without being mediated by object recognition.
EmoNet was developed using an emotional scene database2 that
included emotionally evocative stimuli gathered by querying search engines
and content aggregation websites with contextual phrases targeting various
emotion categories1. While these stimuli encompassed a broad array of
psychologicallysigniﬁcantsituations,theywereexplicitlyselectedemotional
scenes that may not be representative of our daily-life experience.
1School of Psychology, Nanjing Normal University, Nanjing, China. 2Department of Medicine, Justus-Liebig-Universität Gießen, Gießen, Germany. 3Max Planck
Institute for Human Cognitive and Brain Sciences, Leipzig, Germany. 4Donders Institute for Brain, Cognition and Behaviour, Radboud University, Nijmegen, the
Netherlands.
e-mail: chuanji.gao@njnu.edu.cn; marius.peelen@donders.ru.nl
Communications Biology |  (2025) 8:697 
1
1234567890():,;
1234567890():,;


## Page 2

Furthermore, most of the scenes involved human actions, such that there
was relatively little variability in terms of object content across the image set.
This raises the possibility that the inferior performance of AlexNet (relative
to EmoNet)reﬂectedthelackof variabilityintheobject categories presentin
the scenes. While human actions are clearly important for many expressive
emotions, we also experience emotions for a wide variety of daily-life scenes
that do not include humans. For example, images of food (associated with
craving), spiders (associated with fear), or ﬂowers (associated with esthetic
appreciation) are also consistently tied to speciﬁc emotions. This raises the
question of whether an emotion-speciﬁc recognition mechanism, such as
modeled by EmoNet, is also used for evaluating emotions from a broader
and more representative set of scenes.
To address this question, the present study took a large and diverse set
of images for which fMRI data are available16. We presented this extensive
collection of ~5000 images to 300 volunteers to gather emotion ratings for
each image. Speciﬁcally, the dataset comprised 1000 images depicting
indoor and outdoor scenes across 250 categories with a general focus rather
than a focus on speciﬁc objects, actions, or people; it included 2000 complex
images featuring multiple objects, often set within realistic contexts and
depicting interactions with other animate or inanimate entities; and it
included 1916 images predominantly showing individual objects, covering
958 distinct object categories. Analyzing this dataset allows for a compre-
hensive evaluation of the hypothesis that emotions are evoked through an
emotion-speciﬁc recognition system rather than based on object repre-
sentations. The fMRI dataset included data from participants who observed
~5000 unique images, which is more effective for uncovering universal
principles of human brain function and offers several unique beneﬁts over
studies that involve a more restricted set of stimuli17.
Our results demonstrate that while an emotion-driven model
(EmoNet) excels in predicting emotion responses to explicitly evocative
stimuli,anobject-based model(AlexNet) bettercapturesemotionresponses
to a broader set of common, everyday scenes. Additionally, we found that
emotional information is represented hierarchically within the object
recognition system, with the lateral occipital complex (LOC) playing a
particularly prominent role. These ﬁndings indicate that emotions evoked
by daily-life scenes are mediated by object recognition. Only when object
content is not informative, additional visual processing mechanisms are
needed to map visual input to emotional experience.
Results
Object representations in deep neural networks predict emotion
ratings of daily-life scenes
Here, we tested whether emotion recognition relies on emotion-speciﬁc
visual processing or can similarly be explained by established object and
scene processing systems. To investigate this, we used the AlexNet deep
convolutional neural network (DCNN) model as a representation of object
processing14,15. AlexNet was chosen due to its established use in vision
research and to allow comparison with EmoNet2. EmoNet, a convolutional
neural network derived from AlexNet, shifts its focus from object classiﬁ-
cation to categorizing images into 20 distinct emotion categories. We
hypothesized that if emotion acts as a general organizing principle within
the visual system, EmoNet should outperform AlexNet in predicting
emotion ratings. Alternatively, if emotion recognition relies on existing
objectprocessingsystems,AlexNetshouldbeatleastcomparablyeffectivein
predicting emotion ratings relative to EmoNet.
We recruited 300 volunteers who viewed 4913 images for which fMRI
dataareavailableBOLD500016.Threeoutofthe4916uniqueimageswerenot
included in the experiment due to a technical issue. The 4913 images were
randomly distributed into 30 sets: 29 sets contained 165 images each, while
one set included 128 images (Fig. 1a). Volunteers were assigned to evaluate
eachsetseparately,withthegoalofhavingtenparticipantsperset.Thesample
size aligns with prior studies demonstrating that judgments from ~ten par-
ticipants are sufﬁcient to reliably estimate population-level means1,18. After
viewingeachimage,participantswereasked torespondtoapromptfeaturing
20 emotion categories: adoration, esthetic appreciation, amusement, anxiety,
awe, boredom, confusion, craving, disgust, empathic pain, entrancement,
4913 images
1
2
3
4
30
…
30 sets 
~163 images
~10 raters
1
2
3
8
Break
Break
8 blocks
~20 trials
…
a. 
b.
d. 
c. 
(
) =
= Emotion category
g
y
= Number of participants who 
selected emotion category
= Number of participants
e.g., 'Joy' selected by 4 
participants for a particular 
image, (
) =
= 0.4
+
250 ms
1s
Self-paced
Multiple choice
…
…
…
Select as
many as
desired
How do
you feel?
A single-trial
procedure
Fig. 1 | Behavioral study procedure and rating results. a Overall experimental
procedure. The 4913 images were randomly divided into 30 sets, with a target of ten
participants per set. Each participant rated around 163 images, which were divided
into eight blocks. b A single-trial procedure. Every trial began with a 250 ms ﬁxation
cross, succeeded by the presentation of an image for 1 s. This was followed by the
emotion category prompt. If participants were uncertain about the meaning of any
emotion while responding, they could view a description of each emotion by moving
the mouse over the emotion category labels. c Computation of emotion probabilities.
The mean probability for each of the 20 emotion categories was calculated by
dividing the number of times an emotion category was selected by the total number
of participants, which is ten. d Structure of images revealed by the t Distributed
stochastic neighbor embedding (t-SNE) analysis. Each dot was marked according to
the emotion that had the highest probability.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
2


## Page 3

excitement, fear, horror, interest, joy, romance, sadness, sexual desire, and
surprise. We deliberately adopted the 20 emotion categories employed by
Krageletal.(2019)toenableafaircomparisonofthepredictiveperformances
of EmoNet and AlexNet, as EmoNet is trained to classify these 20 emotion
categories. Participants were instructed to select at least one category thatbest
described their emotional response to the image, but they could choose
multiple categories if desired (Fig. 1b). For each image, we recorded the
frequency with which each emotion category was selected by the ten parti-
cipants. The probability of each of the 20 emotion categories was then cal-
culated by dividing the number of times an emotion category was chosen by
the total number of participants, which was ten (Figs. 1c and S1).
We evaluated the reliability of emotion ratings for images by assessing
the proportion of pictures exhibiting signiﬁcant concordance in judgment
rates across the 20 emotion categories following Cowen et al. (2017). We
found that out of the 4913 images, 79% of the pictures have signiﬁcant
concordance (or rates of interrater agreement) for at least one category of
emotion across raters [false discovery rate (FDR) < 0.05]. 55% of the raters
chose the most agreed-upon emotion category for each picture [chance
level = 13.5%, Monte Carlo simulation of all category judgments matching
the same overall proportions of categories that were selected by the real
participants].Theseresultsarecomparableorbettertothosedocumentedin
previous studies (e.g., Cowen et al., 2017) (Supplementary text).
We explored the structure of images using the technique of t-Dis-
tributed stochastic neighbor embedding (t-SNE). The t-SNE analysis
revealed that images were distinctly clustered within the two lower-
dimensional spaces (Fig. 1d). Each dot was color coded based on the
emotion with the highest probability, showing that images of the same
emotion category are more likely to cluster together. The t-SNE analysis was
applied to the full 20-dimensional emotion probability vectors (derived
from participant ratings) for each image, rather than relying solely on
dominant emotion labels. This method preserves the complete distribution
of emotion responses, including secondary and tertiary emotional associa-
tions. The resulting grouping of images by emotion category in a lower-
dimensional space reveals inherent structural patterns in the data that
extend beyond dominant labels. Furthermore, the clustering of images by
their dominant emotion underscores the robustness and consistency of
primary emotion responses as a key organizational feature of the dataset.
Emotion dissimilarity between each pair of emotions and hierarchical
clustering analyses showed meaningful clustering of emotion categories
(Supplementary text and Fig. S2).
Having established that common everyday scenes and objects we fre-
quently encounter are associated with various emotions, we proceeded to
address our primary research question: comparing the performance of
AlexNet and EmoNet in predicting emotion ratings. EmoNet differs from
AlexNet in the retraining of the weights in the ﬁnal fully connected layer
(fc8), while the preceding seven layers are identical between the two models.
Therefore, we focused our comparison on the predictive performance of the
fc8 layer in both models in relation to emotion ratings. We used the partial
least squares regression (PLSR) analysis approach19,20. This multivariate,
data-driven approach identiﬁes latent variables within a multidimensional
input space (fc8 layer activations) and a multidimensional output space
(emotion ratings) that are optimized to maximize the covariance between
the two variable sets, enabling the prediction of emotion ratings from deep
neuralnetworklayeractivations(Fig.2a).ThechoiceofPLSRwasmotivated
by three main reasons: ﬁrst, its efﬁcacy in handling datasets characterized by
predictors that exhibit both high multicollinearity and high dimensionality;
second, its capability to model complex multivariate patterns across both
predictors and outcomes; and third, it is particularly suited for predicting
behavior at the item-level, which is our primary objective.
We found that both fc8 layer of AlexNet (average leave-one-session-
out cross-validated r = 0.407, p < 0.001, permutation test) and fc8 layer of
EmoNet(averageleave-one-session-out cross-validatedr = 0.292,p < 0.001,
permutation test) signiﬁcantly predicted emotion ratings. The confusion
matrices demonstrated no bias in predictions (Fig. S3). Importantly, Alex-
Net outperformed EmoNet in predicting emotion ratings (Δr = 0.115,
p < 0.001, permutation test) (Fig. 2b). Emotion ratings for images were
predicted from the fc8 layer of AlexNet through a transformation matrix of
1000 object categories by 20 emotions. Images corresponding to object
labels with the top positive weights in this matrix had a higher likelihood of
being rated as associated with the respective emotion (Fig. 3). The top
example images predicted from the fc8 layer of AlexNet for each emotion
align with intuition. For instance, images of mountains, ﬂowers, and houses
are associated with esthetic appreciation; pizza, dishes, and other foods are
linked to craving; cockroaches, tiger beetles, and other insects are related to
Fig. 2 | Object representations predict emotion
ratings of daily-life scenes. a Decoding emotions
from deep convolutional neural network (DCNN)
representations using partial least squares regres-
sion. b fc8 layer in the AlexNet model outperformed
fc8 layer in EmoNet model in predicting emotion
ratings. Each line and dot represent the result of a
cross-validated fold. c AlexNet consistently out-
performed EmoNet in predicting emotion ratings
across three subsets of BOLD5000 images.
d EmoNet outperformed AlexNet in predicting
emotion ratings for the Cowen17 dataset. In con-
trast, for the BOLD5000 dataset, AlexNet out-
performed EmoNet in predicting emotion ratings.
Error bars represent the standard error across cross-
validated folds.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
3


## Page 4

horror; bulletproof vests and military uniforms are associated with sadness;
while faces, sunglasses, and women wearing lipstick are connected to sexual
desire. These examples show that common everyday scenes and objects are
consistently tied to different emotions.
To evaluate the consistency of the comparison between AlexNet and
EmoNet across diverse image datasets, we analyzed three subsets of
BOLD5000 images: Scenes, COCO21, and ImageNet22. The Scenes subset
consists of 1000 images depicting both indoor (e.g., restaurants) and out-
door (e.g., mountains and rivers) environments, with a general focus on the
broader scene rather than speciﬁc objects, actions, or people. The images
encompassed 250 unique scene categories, primarily drawn from the SUN
dataset23, with images selected using Google Search queries based on the
category names. The COCO subset includes 2000 complex images from the
COCO dataset, featuring multiple objects, often situated in realistic contexts
and involved in interactions with other animate or inanimate entities (e.g.,
scenes of human social interactions). The ImageNet subset comprises 1916
images, predominantly depicting individual objects, selected from the
ImageNet dataset. These three subsets are distinct from one another, and
comparing the results across them allows us to assess the consistency of our
ﬁndings across the broader set of images in BOLD5000. The results con-
sistently show that AlexNet outperformed EmoNet in predicting emotion
ratings (Fig. 2c).
In addition, given that a previous study2 demonstrated that EmoNet
outperformedAlexNetinpredictingemotions,weanalyzedtheimagesfrom
Cowen and Keltner1 used in that study to assess whether we could replicate
their ﬁndings and to examine differences in results between the BOLD5000
images and this earlier dataset. From each video in the Cowen17 dataset, we
extracted three representative frames at 25, 50, and 75% of the video length,
yielding 6555 images. Unlike the BOLD5000 images, which depict common
everyday scenes and objects that we frequently encounter, the Cowen17
images consist of more emotionally evocative stimuli that were explicitly
selected for their emotional content. We found that EmoNet outperformed
AlexNet in predicting emotion ratings for these images, t(14) = 24.55,
p < 0.001, paired t test (Fig. 2d), which is consistent with Kragel, et al.2. This
ﬁnding contrasts with the results from BOLD5000 images, where AlexNet
outperformed EmoNet in predicting emotion ratings. For explicitly emo-
tionally evocative scenes, EmoNet (an emotion-based visual system model)
outperformed AlexNet (an object-based visual system model), while Alex-
Net was superior for common daily-life scenes.
Emotion information is processed in hierarchical stages of the
object recognition system
Having established that object representations reliably predict emotion ratings
of daily-life scenes, we next aimed to determine whether emotional informa-
tion is processed in a hierarchical manner. If emotion recognition is mediated
by known object processing systems, as we have demonstrated, we would
expect emotional information to be processed hierarchically, consistent with
the organization of the visual cortex for object recognition. AlexNet comprises
ﬁve convolutional layers and three fc layers, mirroring the hierarchical struc-
ture of regions in the ventral visual stream24–27. As activation progresses
through the layers, the processed features grow increasingly complex, starting
from low-level features in conv1 to complex object parts in conv5. Each
convolutional neuron is connected to a limited subset of neurons in the next
convolutionallayer,transferringonlyaportionof thetop-weighted activations
tothenextlayer.Informationfromconv5isthenpassedtothefclayers(fc6–8),
where each neuron connects with all neurons in the next fc layer.
We employed PLSR to explore the relationship between layer activa-
tions and the emotion ratings. Speciﬁcally, we predicted emotion prob-
abilities based on activations from various layers of AlexNet, including
conv1, conv2, through to fc8. We found that emotion ratings could be
predicted above chance from activity in all layers (ps < 0.001, permutation
test, FDR corrected; Fig. 4a; Supplementary text and Fig. S4), and confusion
matrices revealed no evidence of systematic bias in predictions (Fig. S3).
To compare the difference across layers (conv1, conv2, conv3, conv4,
conv5, fc6, fc7, and fc8), we performed repeated measures ANOVAs on the
prediction-outcome correlation across different cross-validation folds, and
Greenhouse–Geisser corrections were applied where necessary to account
for violations of sphericity. We found a main effect of layer: F(2.93,
41.04) = 999.42,p < 0.001,partialη2 = 0.99.Theseresultsdemonstratedthat
differentlayersvaryintheircapabilitytopredictemotionratings(Fig.4a).In
Fig. 3 | Top weights of predicting emotion ratings from fc8 layer of AlexNet for
six example emotions. The transformation matrix (1000 object labels x 20 emo-
tions) between AlexNet’s fc8 layer and emotion ratings was averaged across 15 cross-
validation folds. For six example emotions, the top ten positive and top ten negative
weights (out of 1000 object labels) are displayed.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
4


## Page 5

addition, we examined whether emotional information is processed in
hierarchical stages. Results showed signiﬁcant improvements across suc-
cessive layers, suggesting a monotonic increase in predictive power with
layer depth (ps < 0.001, permutation test, FDR corrected; Fig. 4a, b; Sup-
plementary text).
Toevaluatethelayeredprocessingresultsacrossdiverseimagedatasets,
we analyzed three subsets of BOLD5000 images: Scenes, COCO, and
ImageNet. We observed hierarchical processing of emotional information
consistently across the three subsets of BOLD5000 images (Fig. 4c). In
addition, we examined the layered processing results for the Cowen17 sti-
muli set. The results consistently show that deeper layers yield better pre-
dictions of emotion ratings compared to earlier layers in AlexNet
representations, regardless of whether the BOLD5000 or Cowen17 dataset
was used (Fig. 4d). These ﬁndings suggest that the hierarchical nature of
emotional processing within the object recognition system remains con-
sistent across different stimuli. However, whether emotion recognition
primarily depends on the established object recognition system may vary
depending on the speciﬁc stimuli.
We evaluated the predictive performance of layer 7 (fc7) and EmoNet
layer 8(fc8) activationsforemotionratingswith the two datasets:BOLD5000
(diverse daily-life scenes) and Cowen17 (emotionally evocative scenes with
constrained object categories). While decreased performance was observed
for EmoNet fc8 compared to fc7 for the BOLD5000 dataset, t(14) = 25,
p < 0.001,pairedttest(Fig.4e),predictiveperformanceincreasedforEmoNet
fc8comparedtofc7fortheCowen17dataset,t(14) = 17.62,p < 0.001,pairedt
test (Fig. 4f). These results indicate that object-level representations in fc7 of
EmoNet—which were originally trained for object recognition—are critical
for predicting emotion ratings in daily-life scenes of BOLD5000. However,
the performance gain from fc7 to fc8 of EmoNet in Cowen17 suggests that
abstract emotion-related categorical information encoded in fc8 provides
additional predictive power beyond object categories.
Representational similarity of emotional information is greater
within than between object categories
Having established that object categories (the fc8 layer in the AlexNet
model) exhibit the strongest emotion predictions, we further investigated
whether these features encode emotional information by organizing
representations in a way that reﬂects emotional distinctions. We tested
whether the representational similarity of emotional information within an
object cluster is greater than that between object clusters. For instance,
related object categories such as pizza and burger might exhibit higher
emotional representational similarity compared to unrelated categories,
such as pizza and car. Additionally, we sought to determine whether the fc8
layer encodes more emotional information compared to the early conv1
layer. If this is the case, the difference in pattern similarity values between
within-cluster and between-cluster comparisons should be larger for the fc8
layer than for the conv1 layer. To explore these hypotheses, we applied
k-means clustering across four different cluster numbers (k = 20, 30, 40, 50).
The k-means algorithm was executed ten times with varying initial cluster
centroids and the best clustering result was chosen. Images within a cluster
means similar images in terms of fc8 layer or conv1 layer. We computed
representationalsimilarities(Pearsoncorrelations)betweenemotionratings
within and between clusters for both the conv1 and fc8 layers.
We observed signiﬁcant differences between within-cluster and
between-cluster similarities across various cluster numbers for both conv1
layer and for the fc8 layer (ps < 0.001, FDR corrected; Fig. 5a, b; Supple-
mentarytext).Wethencomputedthedifferencebetweenwithin-clusterand
between-cluster similarities for each cluster number and conducted paired
t-tests to compare these differences between the conv1 and fc8 layers. Sig-
niﬁcant differences were found between the fc8 and conv1 layers across
various cluster numbers (ps < 0.001, FDR corrected; Fig. 5c; Supplementary
text). These results demonstrated that the representational similarities of
emotional information within object clusters were greater than those
Fig. 4 | Emotion information is hierarchically represented in an object recog-
nition system. a Results of decoding emotions from AlexNet representations. These
results show that emotion information is processed hierarchically in a visual object
processing system. b Differences between AlexNet layers in predicting emotion
ratings. c The hierarchical processing of emotion information was consistent across
the three subsets of BOLD5000 images. d The hierarchical processing of emotion
information was consistent regardless of whether the BOLD5000 or Cowen17
dataset wasused.e fc7 layer outperformed fc8 layer of EmoNet in predicting emotion
ratings for the BOLD5000 dataset. f fc8 layer of EmoNet outperformed fc7 layer in
predicting emotion ratings for the Cowen17 dataset. Error bars represent the
standard error across cross-validated folds and each dot represents the result of a
cross-validated fold.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
5


## Page 6

between object clusters, suggesting that related object categories share
common emotional features.
Activity patterns in object-selective cortex predict emotion ratings
The previous analyses showed that object category representations reliably
predict emotion ratings of daily-life scenes, suggesting that emotion
recognition can rely on established object processing systems, at least for
common, everyday scenes, and objects. If emotion recognition relies pri-
marily on the visual object recognition system, we would expect the object-
selective visual cortex (i.e., the LOC) to outperform all other visual regions
(e.g., early visual cortex (EarlyVis) or scene-selective regions) in predicting
emotion ratings.
Totestthishypothesis,weanalyzedthefMRIdatafromtheBOLD5000
dataset, which includes data from four individuals who observed ~5000
uniqueimages16.The fMRIdata comprise a completedatasetforthreeoutof
four participants across 15 functional sessions, with the fourth participant
having data from nine functional sessions. Each trial consisted of an image
presented for 1 s, followed by a 9 s ﬁxation cross. After viewing the image,
participants were instructed to perform a valence judgment task, in which
they rated their preference for the image by choosing “like,” “neutral,” or
“dislike.” (Fig. 6a). The functional localizer sessions consisted of three types
of conditions: scenes, objects, and scrambled images, with stimuli that were
distinct from those used in the main fMRI study (Fig. 6a). The following
regions of interest were included: EarlyVis; object selective LOC; and scene
selective regions of interest, including the parahippocampal place area
(PPA), the retrosplenial complex (RSC), and the occipital place area (OPA).
We included Heschl’s gyrus (Heschl) as a control region because it is a
primary sensory area for the auditory modality, and it is not expected to
signiﬁcantly contribute to visual emotion representation (Fig. 6b).
We used PLSR to predict emotion ratings from activity patterns in the
visual cortex (Fig. 7a). We found that all visual regions could signiﬁcantly
predict emotion ratings (Fig. 7b; Supplementary text; Table S1; Fig. S5. To
compare the effectsof region(Heschl, EarlyVis,LOC,OPA,PPA,and RSC),
we performed repeated measures ANOVAs on the prediction-outcome
correlation across different cross-validation folds, and Greenhouse-Geisser
corrections were applied where necessary to account for violations of
Fig. 5 | Representational similarities of emotional information within object
clusters were greater than those between object clusters. The representational
similarity analysis results indicated that both (a) the conv1 layer and (b) the fc8 layer
of AlexNet exhibited greater within-cluster similarity than between-cluster simi-
larity, suggesting that both layers encode emotional information, regardless of the
number of K-means clusters. c The fc8 layer demonstrated a larger difference in
pattern similarity between within-cluster and between-cluster comparisons than the
conv1 layer, indicating that the fc8 layer encodes more emotional information. Error
bars represent the standard error across clusters and each dot represents the result of
a cluster.
Fig. 6 | BOLD5000 experimental procedure and the regions of interest from the
functional localizer. a The main fMRI data comprise a complete dataset for three
out of four participants across 15 functional sessions, with the fourth participant
having data from nine functional sessions. Eight functional localizer sessions were
conducted (six sessions for participant CSI4. b The regions of interest from the
functional localizer were deﬁned using the following way. Early visual cortex was
deﬁned by comparing scrambled images to baseline. An object-selective regions of
interest, the lateral occipital complex (LOC) was deﬁned by comparing objects to
scrambled images. Scene-selective regions of interest included the parahippocampal
place area (PPA), the retrosplenial complex (RSC), and the occipital place area
(OPA), deﬁned by comparing scenes with objects and scrambled images.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
6


## Page 7

sphericity. We found main effects of region for all subjects: CSI1, F(4.61,
64.49) = 245.62, p < 0.001, partial η2 = 0.95; CSI2, F(3.69, 51.61) = 175.11,
p < 0.001, partial η2 = 0.93; CSI3, F(3.45, 48.27) = 258.91, p < 0.001, partial
η2 = 0.95; CSI4, F(2.61, 20.91) = 196.15, p < 0.001, and partial η2 = 0.96.
These results indicate that different brain regions vary in their capability to
predict emotion ratings.
Our main question was to investigate whether fMRI activity in the
visual cortices provide better predictions of emotional ratings compared to
activity in Heschl’s gyrus, and whether fMRI activity in the LOC region
outperforms that in the EarlyVis, OPA, PPA, and RSC regions. We found
that fMRI activity in all visual regions outperformed Heschl’s gyrus in
predicting emotion ratings (Fig. 7b; Supplementary text; Table S2), and
fMRI activity in the LOC region outperformed that in the EarlyVis, OPA,
PPA, and RSC regions in predicting emotion ratings (Fig. 7b; Supplemen-
tary text; Table S2).
To further examine the representation of emotions within the LOC
region, we constructed confusion matrices grounded in the PLSR model,
using LOC cortical activity to predict emotion ratings. For each participant
and each cross-validation iteration, we correlated the emotion ratings pre-
dicted by the PLSR model, based on LOC cortical activity, with a vector of
actual emotion ratings spanning 20 distinct emotion categories. This pro-
cess yielded a20 × 20correlation matrixperiteration. The emotioncategory
with the highest correlation was designated as the most likely emotion
inferred from brain activity. Subsequently, the confusion matrices derived
from all cross-validation folds were aggregated. Finally, we normalized the
confusionmatrixtoascalebetween0and1,andplotted themeanconfusion
matrix across all subjects (Fig. 7c). The data reveal several instances of
emotion categorization that align with intuitive ambiguities, encompassing
the conﬂation of joy with amusement, awe with adoration, anxiety with
excitement, and interest with excitement. However, the ﬁndings also show
several counterintuitive associations, notably the grouping of craving with
disgust, and empathic pain with sexual desire (Fig. 7c, d). These ﬁndings
suggest that while the LOC region does not perfectly capture human
emotion ratings, it does contain a rich representation of emotion categories.
Confusion matrices and dendrograms for other brain regions are presented
in Fig. S6.
The fMRI results revealed that all visual regions signiﬁcantly predicted
emotion ratings, with object-selective regions outperforming other visual
areas in their predictive ability. These ﬁndings are consistent with previous
ﬁndings showing that successive layers in AlexNet lead to signiﬁcant
improvements in predicting emotion ratings. These results suggest that
emotion ratings are driven by object representations encoded in the LOC
region, indicating that emotion recognition primarily relies on the visual
object recognition system.
Discussion
Scenes and objects that we encounter in daily life are consistently associated
with various emotions. However, the neural and computational mechan-
isms underlying the elicitation of diverse emotions by visual scenes remain
unclear. To address this, we analyzed a large set of daily-life scenes along
with a broad spectrum of object categories. We presented ~5000 images
from this collection to 300 volunteers to obtain emotion ratings for each
image. Analyzing this dataset allowed to evaluate whether emotions are
evoked by an emotion-speciﬁc recognition system or whether they are
driven by established mechanisms of object recognition.
We found that for explicitly emotionally evocative scenes from Cowen
and Keltner1, EmoNet (an emotion-based visual system model) out-
performed AlexNet (an object-based visual system model), replicating the
ﬁndings of Kragel, et al.2. However, AlexNet outperformed EmoNet in
predicting emotion ratings for images of daily-life scenes and objects. This
pattern was consistent across three subsets of the image dataset. Our ﬁnd-
ings thereby highlight the role of established object processing systems in
driving emotion schemas for daily-life scenes.
If emotion recognition relies on established object processing systems
for daily-life scenes, as our ﬁndings suggest, we would expect emotion
information to be processed hierarchically, in line with the organization of
the visual cortex for object recognition. Supporting this hypothesis, we
observed a monotonic increase in the ability to predict emotion ratings with
a. 
b. 
c. 
d. 
CSI1
CSI2
CSI3
CSI4
Fig. 7 | Object-selective cortex (LOC) outperformed other visual cortex regions in
predicting emotion ratings. a Decoding emotions from fMRI activity in visual
cortices using partial least squares regression. b Results of decoding emotions from
fMRI activity in the visual cortices for CSI1, CSI2, CSI3, CSI4, and all subjects. fMRI
activity in all visual cortex regions outperformed Heschl’s gyrus in predicting
emotion ratings, and fMRI activity in the lateral occipital complex (LOC) region
outperformed that in the EarlyVis, OPA, PPA, and RSC regions in predicting
emotion ratings. c The averaged, normalized confusion matrix across four subjects
for the relationship between the multivariate pattern responses in the LOC and
emotion ratings. Rows represent the actual categories of the cross-validated data, and
columns denote the predicted categories. Gray colormap indicates the proportion of
predictions within the dataset, with each row summing to 1. Correct predictions fall
on the diagonal of the matrix, whereas off-diagonal elements reﬂect wrong predic-
tions. We correlated the predicted emotion ratings from the PLSR model for LOC
cortical activity with vectors of emotion ratings across 20 emotion categories,
resulting in a 20 × 20 correlation matrix. d Dendrogram constructed using Ward’s
method based on the confusion matrix in (c). ***p < 0.001; **p < 0.01; *p < 0.05; ns
not signiﬁcant.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
7


## Page 8

increasing layer depth in AlexNet, consistent with recent studies28. While
prior work has focused on broad valence categories (i.e., positive, neutral,
and negative), we extended these ﬁndings28 by demonstrating layered pro-
cessing of emotional information using more ﬁne-grained emotional cate-
gories. This layer-wise pattern was consistent across three distinct subsets of
theBOLD5000dataset,whichvariedinfocus,withsomesubsetsbeingmore
object-focused and others more scene-focused. Our representational simi-
larity analyses further revealed that the emotion rating distances within
object clusters, based on high-level object classes (from the fc8 layer of
AlexNet), were greater than those between object clusters, indicating that
object categories encode emotional information. The difference in pattern
similarity between within-category and between-category comparisons was
more pronounced in the fc8 layer thaninthe conv1 layer, indicatingthat the
fc8 layer encodes more emotional information than earlier layers. These
ﬁndings suggest that visual emotional representations of everyday scenes
and objects are processed hierarchically in the visual object processing
system,allowing forboth rapid,coarse evaluations of emotionalsigniﬁcance
based on simple visual features (e.g., prototypical shapes and textures) and
more detailed analyses of complex object features and concepts, depending
on context29.
We found that EmoNet outperformed AlexNet in predicting emotion
ratings for scenes from Cowen and Keltner1. These results indicate that
object categories alone do not provide sufﬁcient information for emotion
prediction, suggesting that other visual features may play a critical role.
When there is limited variability in the object categories present in the
scenes(e.g.,predominantlyhumans,asintheimagesusedtotrainEmoNet),
the ﬁnal layer of AlexNet, which reﬂects object categories, becomes less
important for predicting emotions. It is important to note that EmoNet was
developed by keeping all layers of AlexNet ﬁxed, except for the ﬁnal fully
connected layer, which was retrained. Consequently, the features from
EmoNet’s earlier layers (conv1 to fc7) were originally trained for object
categorization. Therefore, EmoNet performance still makes use of object
representations, though not object categories as encoded in AlexNet’s ﬁnal
layer. Consistent with this, our results revealed that object-level repre-
sentations in the fc7 layer of EmoNet/AlexNet are critical for predicting
emotion ratings in daily-life scenes from BOLD5000. However, the fc8 layer
of EmoNet outperformed the fc7 layer in predicting emotion ratings for the
Cowen and Keltner (2017), suggesting that emotion-speciﬁc categorical
information encoded in fc8 provides additional predictive power beyond
object categories.
If emotion recognition primarily relies on the visual object recognition
system, we would expect the object-selective visual cortex, speciﬁcally the
LOC, to outperform other visual regions (e.g., EarlyVis) in predicting
emotion ratings. To test this, we analyzed fMRI data from a comprehensive
set of 5000 images alongside emotion ratings reported while viewing these
images.Our results showed that fMRI activity inallvisual regions, including
EarlyVis, LOC, OPA, and PPA, outperformed Heschl’s gyrus (an auditory
region) in predicting emotion ratings. These ﬁndings replicate previous
research2, demonstrating that activity in the visual cortex signiﬁcantly
predictsemotionratingsforimages30,31.Ourstudyprovidesnovelinsightsby
analyzing a larger and more diverse set of stimuli, capturing a broader range
ofvarianceacrossvisualimages,ratherthanrelyingonsmallersetsoftensor
hundreds of stimuli. This approach offers several unique beneﬁts for
uncovering universal principles of human brain function. Importantly,
fMRI activity in the LOC exceeded that of other visual regions in predicting
emotion ratings, suggesting that emotion ratings are primarily driven by
object representations encoded in the LOC region7–10. Together with the
demonstrated link between object categories and emotion and the ﬁndings
ofhierarchicalprocessingofemotionalinformationinAlexNet,theseresults
collectively illustrate that emotion processing in everyday scenes and objects
depends on the visual object recognition system.
These ﬁndings support theories emphasizing that object categorization
is a necessary condition for emotional responses to visual scenes32–35. They
are inline with recent evidence showingthat objectrecognition precedes the
onset of affective feelings36, with the two latencies being positively correlated
across participants37. In addition, experimental manipulations that delayed
object recognition also delayed the onset of affective feelings, and this effect
was at least partially mediated by the delayed recognition of objects38,39.
Furthermore,studies have shownthat subjective valence and arousalratings
were modulated by the affective content of a scene only when the scene’s
content was correctly reported; no affective modulation occurred when the
picture content was not accurately identiﬁed40. A recent study also
demonstrated that object categorization is necessary for the late positive
potential (an emotion-related EEG marker) to be evoked41. Our ﬁndings
contribute to this literature by showing superior predictive performance of
emotion ratings based on object content, supporting a strong link between
object categories and emotion, even when using ﬁner differentiation of
emotional categories (over 20) compared to previous studies.
A potential limitation of the current study is the discrepancy between
the fMRI task (valence rating) and the emotion categorization task, as task
demands can modulate neural processing42–44. The valence-rating task for
the fMRI data diverges from both typical naturalistic perception in daily life
and the emotion categorization task employed in our rating study. This
divergence raises questions about the direct comparability of neural pro-
cesses across tasks. However, our results indicate that despite these differ-
ences, visual cortical activity can predict emotion ratings successfully,
suggesting that core emotion representations are preserved even when task
demands shift. In addition, our results cannot exclusively be interpreted as
supporting a causal relationship between object categorization (cause) and
emotion (effect). It remains possible that object features facilitate emotion
responses, or that affective responses assist in object recognition45. Future
studies combining our approach with EEG/MEG could help to clarify the
temporal stages at which these effects manifest.
Method
Behavioral study
Participants. A total of 300 volunteers (143 females, 155 males, and two
individuals who did not report their sex; mean age = 27.78 ± 4.38 years,
and one participant who did not provide age information), recruited
through Proliﬁc, were included in the analyses. Additionally, six parti-
cipants participated in the experiment but did not complete it due to
technical issues or other reasons. These individuals were compensated
but not included in the analyses. Participants were required to be over 18
years of age, possess normal or corrected-to-normal vision, and be ﬂuent
in English. This experiment received approval from the Ethics Com-
mittee of the Faculty of Social Sciences at Radboud University (ECSW-
LT-2022-8-4-35788). Informed consent was obtained from all partici-
pants. All ethical regulations relevant to human research participants
were followed.
Stimuli. The stimuli included 4913 images, selected from the BOLD5000
public fMRI dataset involving human subjects, which contains 5254
images, with 4916 being unique16. These stimuli featured real-world
scenes, showcasing a broad diversity of images. They encompassed both
outdoor and indoor scenes, complex interactions among objects, human
social interactions, and objects situated within real-world contexts. Three
out of the 4916 unique images were not included in the experiment due to
a technical issue. Additionally, to prepare participants for the main
experiment, we introduced ten new images from the OASIS affective
image database46 in a practice task.
Procedure. The 4913 images were randomly divided into 30 sets; 29 of
these sets contained 165 images each, while one set comprised 128
images. Participants were recruited to evaluate each set individually, with
a target of ten participants per set. Additionally, for each set, eight images
were shown twice to assess the consistency of the ratings. At the begin-
ning of the experiment, participants were briefed that they would be
shown a series of images individually. Their task involved identifying the
emotions each image elicited in them. After each image was displayed,
participants were presented with a prompt featuring 20 emotion
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
8


## Page 9

categories: adoration, esthetic appreciation, amusement, anxiety, awe,
boredom, confusion, craving, disgust, empathic pain, entrancement,
excitement, fear, horror, interest, joy, romance, sadness, sexual desire,
and surprise. These categories, chosen based on prior research, have been
thoroughly validated as distinct by human evaluators2. Participants were
instructed to select at least one category that best reﬂected their feelings
towards the image, although they could select as many as desired. To
ensure participants fully understood the meaning of each emotion
category, they were guided through detailed descriptions of all 20 cate-
gories. Subsequently, they undertook ten practice trials to become
accustomed to the procedure.
Themainpartoftheexperimentwasdividedintoeightblocks.Theﬁrst
seven blocks each contained 20 images, with the remainder displayed in the
ﬁnalblock.Therewasaself-pacedrestperiodbetweeneachblock.Everytrial
began with a 250 ms ﬁxation cross, succeeded by the presentation of an
image for 1 s. This was followed by the emotion category prompt. If parti-
cipantswereuncertainaboutthemeaningofanyemotionwhileresponding,
theycouldviewadescriptionofeachemotionbymovingthemouseoverthe
emotion category labels. Afterwards, a prompt would inquire about their
conﬁdence in their selection. Both the emotion categorization and con-
ﬁdence assessment were conducted at the participants’ own pace.
fMRI dataset
Participants. The fMRI data were sourced from the BOLD5000 dataset16,
which are publicly available at: https://kilthub.cmu.edu/articles/dataset/
BOLD5000_Release_2_0/14456124. Participants were graduate students
from Carnegie Mellon University. The demographic details of the par-
ticipants are as follows: CSI1, a 27-year-old male; CSI2, a 26-year-old
female; CSI3, a 24-year-old female; and CSI4, a 25-year-old female. All
participants were right-handed, with no reported history of psychiatric or
neurological disorders, nor any current psychoactive medication use.
Each participant provided written informed consent, adhering to pro-
tocols approved by the Institutional Review Board at Carnegie Mellon
University.
Stimuli. The stimuli consisted of 4916 unique images, categorized as
follows: 1000 hand-selected images depicting indoor (for example, res-
taurants) and outdoor (such as mountains and rivers) scenes with a
general focus rather than on speciﬁc objects, actions, or people; 2000
complex images featuring multiple objects, where these objects were
often situated within a realistic context and depicted as interacting with
other animate or inanimate entities (for instance, scenes of human social
interactions); and 1916 images predominantly showcasing individual
objects. The luminance of all images was standardized through a gray-
world normalization technique.
Procedure
Main fMRI experiment. The fMRI data include a full set of recordings for
three of the four participants across 15 functional sessions, while the fourth
participant’s data cover nine functional sessions. These sessions are divided
intotwotypes:eightsessionseachconsistingofnineruns,andsevensessions
comprising ten runs each. Every run included 37 trials, with each trial
featuring an image displayed for1 sfollowed bya 9 sﬁxationcross.After the
stimulus presentation, participants were asked to perform a valence judg-
ment task, where they evaluated their preference for the image by selecting
“like,” “neutral,” or “dislike.” This was accomplished using an MRI-
compatible response glove on their dominant hand.
Functional localizer. Eight functional localizer sessions were conducted (six
sessions for participant CSI4). These localizers were conducted at the end of
the day’s session when a participant had completed a main functional ses-
sion of nine runs, but not those with ten runs. The functional localizer
sessions included three types of conditions: scenes, objects, and scrambled
images, and the stimuli presented did not overlap with the images used in
the main fMRI study. There were four blocks per condition, with each block
containing16trialsthatincluded14uniqueimagesandtworepeatedimages
(Fig. 1b). Participants were asked to perform a one-back task, which
required them to press a button if an image was immediately repeated.
MRI acquisition. MRI data were collected using a 3 T Siemens Verio MR
scanner at Carnegie Mellon University. Functional images were acquired
through a T2*-weighted gradient-recalled echo-planar imaging multi-band
pulse sequence. The in-plane resolution was set at 2 × 2 mm, with a matrix
sizeof106 × 106. The slicethicknesswas 2 mmwithout anygap. The ﬁeld of
view was 212 mm. The repetition time was 2000 ms, echo time was 30 ms,
and the ﬂip angle was set at 79 degrees. The multi-band factor was three.
Additional details can be found in the original paper16.
fMRI data preprocessing. We analyzed Release 2.0 of BOLD5000 (version
descriptor:
TYPED-FITHRF-GLMDENOISE-RR),
which
employed
GLMsingle, a denoising toolbox47. This toolbox includes a custom hemo-
dynamic response function estimation, GLM denoising48, and regulariza-
tion via ridge regression. It has been shown that this approach greatly
enhancesthequalityofdata.BeforetheGLMsingledenoisingprocedurewas
applied, the data were preprocessed using fMRIPrep49.
Functional localizer data were also preprocessed using fMRIPrep49.
Subsequently, SPM12 was employed for GLM analyses, incorporating three
conditions: scenes, objects, and scrambled images50. Additionally, nine
nuisance regressors were included, comprising six motion parameters, the
average signal within the cerebral spinal ﬂuid mask and white matter mask,
as well as global signal within the whole-brain mask.
Data analyses
Emotion rating analyses
Computation of emotion probabilities. For each image, we compiled the
frequency of selected emotion categories from ten participants. The prob-
ability for each of the 20 emotion categories was calculated by dividing the
number of times an emotion category was selected by the total number of
participants, which is ten. For instance, for a particular image, if ‘‘joy’’ was
selected by four out of ten participants, ‘‘adoration’’ by all ten, and ‘‘disgust’’
by none, the probability for ‘‘joy’’ would be 40%, for ‘‘adoration’’ 100%, and
for‘‘disgust’’0%.Thisapproachestablishesthemaximumprobabilityofany
emotion evoked by an image at 100% and the minimum at 0% without
assuming that emotion categories are mutually inclusive or exclusive.
t‑Distributed stochastic neighbor embedding (t‑SNE). To explore the
structure of images, we used the Barnes-Hut version of t-SNE, setting the
perplexity to 30 and theta to 0, as an approach to visualize data in high
dimensions. This approach took a normalized matrix of 4913 observations
by 20 emotions of emotion probabilities and computed pairwise Euclidean
distances between observations. These Euclidean distances in high-
dimensional space between variables were then transformed into condi-
tional probabilities. These probabilities are then mapped onto a two-
dimensional space through the Student’s t distribution, aiming to minimize
the Kullback–Leibler divergence in the process. This method has the
advantage of revealing the global structure but also capturing the local
structure within the high-dimensional data51.
Emotion dissimilarity. To assess how different categories of emotions are
related, we used the matrix of emotion probabilities of 4913 images by 20
emotions as input and calculated the pairwise Pearson correlation distance
between two emotions across all evaluated images. We chose the Pearson
correlation distance for its direct relationship with the squared Euclidean
distancesof normalized vectors,which simpliﬁesunderstanding.Tocalculate
dissimilarity, we subtracted the Pearson correlation coefﬁcient from 1.
Hierarchical clustering analysis. To further visualize how emotion categories
cluster together based on the probabilities associated with the 20 distinct
emotion categories, we conducted an analysis of hierarchical clustering. This
analysis was carried out utilizing Ward’s method as the criterion52.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
9


## Page 10

Comparing object and emotion DCNN representations in pre-
dicting emotions
To test whether emotion recognition relies on emotion-speciﬁc visual
processing or can similarly be explained by established object and scene
processing systems, we compared the performance of object and emotion
DCNN representations in predicting emotions. We used the EmoNet
DCNN model as an emotion DCNN model to extract features from 4913
images. EmoNet is a convolutional neural network derived from
AlexNet14,15, with its objective modiﬁed from object class recognition to the
classiﬁcation of images into 20 distinct emotion categories. This was
achieved by retraining the weights in its ﬁnal fully connected layer2. The
AlexNet DCNN model was implemented via MATLAB’s Deep Learning
Toolbox, to extract features from 4913 images. The number of units in each
layer of AlexNet is: conv1, 96 × 55 × 55; conv2, 256 × 27 × 27; conv3 and
conv4, 384 × 13 × 13; conv5, 256 × 13 × 13; fc6 and fc7, 4096; and fc8, 1000.
For convolutional layers, we averaged activations over the spatial domain,
resulting in vector lengths of 96, 256, 384, 384, and 256, respectively. This
averaging reduces dimensionality, aligns convolutional outputs with the
fully connected layers, and emphasizes the global presence of features over
their exact spatial locations see ref. 53 for a similar approach.
Using PLSR, we predicted emotion probabilities from features
extracted from the fc8 layer of EmoNet or AlexNet in a leave-one-session-
out cross-validation approach. PLSR analyses were conducted using the
‘‘plsregress’’ function in MATLAB. The prediction performance was
assessedby calculating the Pearson correlation between observedand cross-
validated predicted emotion ratings, with permutation testing employed for
inference.
Comparative analyses across three subsets of
BOLD5000 images
To evaluate the consistency of the comparison between AlexNet and
Emonet across diverse image datasets, we conducted a comparative analysis
using three distinct subsets of BOLD5000 images: Scenes23, COCO21, and
ImageNet22. Speciﬁcally, we conducted two analyses: ﬁrst, decoding emo-
tions from AlexNet fc8 representations, and second, decoding emotions
from the fc8 layer in the EmoNet model. The analysis procedure was
identical to the previous analyses, with the exception that ﬁve-fold cross-
validation was used instead of 15-fold due to the smaller number of images
in each of the three subsets.
In addition, we analyzed videos from Cowen and Keltner1, following
Kragel, et al.2. The 2185 videos, along with their mean emotion ratings from
853 participants, were sourced from Cowen and Keltner1. To be consistent
with our other analyses and the previous study2, we selected 20 emotion
categories. We extracted three representative frames from each video at 25,
50, and 75% of the video length, resulting in 6555 images. We then per-
formed the two analyses described above on these 6555 images. The analysis
procedure was consistent with the previous analyses, employing a 15-fold
cross-validation method, where the dataset was partitioned into 15 folds.
Decoding emotions from AlexNet layer activations
To determine whether emotional information is processed in a hierarchical
manner, we predicted emotion probabilities based on activations from
various layers of AlexNet. We implemented PLSR models with 20 dimen-
sions to prevent overﬁtting, in accordance with previous research54,55. PLSR
models were trained using a leave-one-session-out cross-validation
approach. PLSR was employed to establish a linear relationship between
layer activations and emotion ratings within the training set. This trans-
formation was then applied to the activations from the test set (the left-out
session) to decode emotion probabilities for each image in that session. To
evaluate out-of-sample prediction performance, we calculated the Pearson
correlation between observed and cross-validated predicted emotion rat-
ings. Inference on prediction performance was conducted using permuta-
tion testing, involving 1000 iterations of PLSR analyses with random
shufﬂing of emotion ratings to generate a null distribution of correlation
coefﬁcients (r values). Statistical signiﬁcance was determined by comparing
the actual r values to this permutation distribution, and multiple compar-
isons were corrected using the FDR method56.
The link between object deep neural network representations
and emotion ratings via representational similarity analyses
To investigate whether object features encode emotional information by
organizing representations that reﬂect emotional distinctions, we evaluated
whether the representational similarity of emotional information within an
object cluster exceeds that between object clusters. To achieve this, we ﬁrst
performed k-means clustering analyses to ensure a larger number of images
within each object cluster. We used multiple replicates (ten in this case) to
minimize the risk of converging on a suboptimal clustering solution due to
an unfavorable initial conﬁguration. The selected cluster numbers were
chosen to cover a range of potential cluster granularities, from relatively
coarse (k = 20) to ﬁner (k = 50) groupings. This approach allowed us to
assess how clustering structure and the resulting emotion similarity metrics
might vary with the number of clusters.
We calculated representational similarities (using Pearson correla-
tions)betweenemotionratingsbothwithinandacrossclustersfortheconv1
and fc8 layers. Within-cluster similarity was calculated as the average of the
lower triangle correlations in the Pearson correlation matrix for stimuli
within the same cluster, while between-cluster similarity was the average
correlation for stimuli across different clusters. Paired t-tests were con-
ducted to evaluate the signiﬁcance of within- versus between-cluster simi-
laritiesforeachlayerindividually.Furthermore,we computedthedifference
between within- and between-cluster similarities for each cluster number
and performed paired t-tests to compare these differences between the
conv1 and fc8 layers. All p-values were corrected for multiple comparisons
using the FDR method56.
Regions of interest
The regions of interest from the functional localizer were deﬁned using the
following way. EarlyVis was deﬁned by comparing scrambled images to
baseline. LOCwas deﬁned by comparing objects to scrambled images. PPA,
the RSC, and the OPA were deﬁned by comparing scenes with objects and
scrambled images See ref. 16 for more details. Heschl’s gyrus was identiﬁed
using the anatomical automatic labeling (AAL) system version 3 (www.gin.
cnrs.fr/en/tools/aal/).
Decoding emotions from fMRI activity in visual cortices
Before conducting PLSR analyses, both the predictors (voxel-wise fMRI
activity) and emotion probabilities (emotion probabilities on 20
dimensions) were normalized across trials for each participant in the
fMRI experiment to yield a mean of 0 and a standard deviation of 1. PLSR
analyses were then conducted for each participant (CSI1, CSI2, CSI3, and
CSI4) and each ROI (Heschl, EarlyVis, LOC, OPA, PPA, and RSC) in a
leave-one-session-out cross-validated approach. It is worth noting that
CSI4 had a different number of sessions compared to the other three
participants, resulting in a varied number of folds for cross-validation:
15-fold cross-validation for CSI1, CSI2, and CSI3, and nine-fold cross-
validation for CSI4.
PLSR was used to establish a linear transformation between fMRI
components and emotion components within a training set. This learned
transformation was then applied to the fMRI components from the test set
(i.e., the left-out session) to decode emotion probabilities for each image
within that session.
To assess out-of-sample prediction performance, we computed the
Pearson correlation between observed and cross-validated predicted emo-
tion ratings. Inference on prediction performance was made using per-
mutationtesting.ThisinvolvedrerunningthePLSR analysesusing the same
data and analytic procedure, but with random shufﬂing of the emotion
ratings. This process was iterated 1000 times to generate a null distribution
of correlation coefﬁcients (r values). Statistical signiﬁcance was determined
by comparing the true r values to the permutation distribution. The FDR
was used to correct for multiple comparisons56.
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
10


## Page 11

Statistics and reproducibility
Statistical analyses were performed using MATLAB (version R2024a)
and R (version 4.3.3). The behavioral study sample size was consistent
with prior research demonstrating that judgments obtained from ~ten
participants are sufﬁcient to reliably estimate population-level means1,18.
The fMRI study sample size was aligned with previous work in which
individual participants were extensively sampled across a large number
of stimuli. Statistical signiﬁcance was assessed using permutation tests,
and FDR correction was applied to control for multiple comparisons.
Additional methodological details are provided in the method and data
and code availability sections.
Reporting summary
Further information on research design is available in the Nature Portfolio
Reporting Summary linked to this article.
Data availability
The MRI data are publicly available at: https://kilthub.cmu.edu/articles/
dataset/BOLD5000_Release_2_0/1445612416; The emotion ratings data are
availableatopenscienceframework(https://osf.io/eks8u/)57.Sourcedatafor
all the ﬁgures in the manuscript are available at Open Science Framework
(https://osf.io/eks8u/).
Code availability
The custom code for data analysis is available at open science framework
(https://osf.io/eks8u/).
Received: 21 January 2025; Accepted: 29 April 2025;
References
1.
Cowen, A. S. & Keltner, D. Self-report captures 27 distinct categories
of emotion bridged by continuous gradients. Proc. Natl. Acad. Sci.
USA 114, E7900–E7909 (2017).
2.
Kragel, P. A., Reddan, M. C., LaBar, K. S. & Wager, T. D. Emotion
schemas are embedded in the human visual system. Sci. Adv. 5,
eaaw4358 (2019).
3.
Ekman, P. An argument for basic emotions. Cognit. Emot. 6, 169–200
(1992).
4.
Cowen, A. S. et al. Sixteen facial expressions occur in similar contexts
worldwide. Nature 589, 251–257 (2021).
5.
Lench, H. C., Flores, S. A. & Bench, S. W. Discrete emotions predict
changes in cognition, judgment, experience, behavior, and
physiology: a meta-analysis of experimental emotion elicitations.
Psychol. Bull. 137, 834 (2011).
6.
Riegel, M. et al. Characterization of the Nencki affective picture
system by discrete emotional categories. Behav. Res. Methods 48,
600–612 (2016).
7.
Epstein, R. A. & Baker, C. I. Scene perception in the human brain.
Annu. Rev. Vis. Sci. 5, 373–397 (2019).
8.
Grill-Spector, K., Kourtzi, Z. & Kanwisher, N. The lateral occipital
complex and its role in object recognition. Vis. Res. 41, 1409–1422
(2001).
9.
Grill-Spector, K. & Malach, R. The human visual cortex. Annu. Rev.
Neurosci. 27, 649–677 (2004).
10. Malach, R. et al. Object-related activity revealed by functional
magnetic resonance imaging in human occipital cortex. Proc. Natl.
Acad. Sci. USA 92, 8135–8139 (1995).
11. Peelen, M. V., Berlot, E. & de Lange, F. P. Predictive processing of
scenes and objects. Nat. Rev. Psychol. 3, 13–26 (2024).
12. Bar, M. & Neta, M. Humans prefer curved visual objects. Psychol. Sci.
17, 645–648 (2006).
13. Lakens, D., Fockenberg, D. A., Lemmens, K. P. & Ham, J. & Midden, C.
J. Brightness differencesinﬂuencethe evaluationof affectivepictures.
Cognit. Emot. 27, 1225–1246 (2013).
14. Krizhevsky, A., Sutskever, I. & Hinton, G. E. Imagenet classiﬁcation
with deep convolutional neural networks. Adv. Neural Inf. Process.
Syst. 25, 84–90 (2012).
15. Krizhevsky, A., Sutskever, I. & Hinton, G. E. ImageNet classiﬁcation
with deep convolutional neural networks. Commun. ACM 60, 84–90
(2017).
16. Chang, N. et al. BOLD5000, a public fMRI dataset while viewing 5000
visual images. Sci. Data 6, 49 (2019).
17. Naselaris, T., Allen, E. & Kay, K. Extensive sampling for complete
models of individual brains. Curr. Opin. Behav. Sci. 40, 45–51 (2021).
18. Cowen, A. S., Elfenbein, H. A., Laukka, P. & Keltner, D. Mapping 24
emotions conveyed by brief human vocalization. Am. Psychol. 74,
698–712 (2018).
19. Abdi, H. Partial least squares regression and projection on latent
structure regression. Wiley Interdiscip. Rev. Comput. Stat. 2, 97–106
(2010).
20. Krishnan, A., Williams, L. J., McIntosh, A. R. & Abdi, H. Partial least
squares (PLS) methods for neuroimaging: a tutorial and review.
Neuroimage 56, 455–475 (2011).
21. Lin, T.-Y. et al. In Computer Vision–ECCV 2014: 13th European
Conference, Zurich, Switzerland, Proceedings, Part V 13. 740–755
(Springer, 2014).
22. Russakovsky, O. et al. Imagenet large scale visual recognition
challenge. Int. J. Comp. Vis. 115, 211–252 (2015).
23. Xiao, J., Hays, J., Ehinger, K. A., Oliva, A. & Torralba, A. In Proc. IEEE
Computer Society Conference on Computer Vision and Pattern
Recognition. 3485–3492 (IEEE, 2010).
24. Khaligh-Razavi, S.-M. & Kriegeskorte, N. Deep supervised, but not
unsupervised, models may explain IT cortical representation. PLoS
Comput. Biol. 10, e1003915 (2014).
25. Güçlü, U. & Van Gerven, M. A. Deep neural networks reveal a gradient
in the complexity of neural representations across the ventral stream.
J. Neurosci. 35, 10005–10014 (2015).
26. Eickenberg, M., Gramfort, A., Varoquaux, G. & Thirion, B. Seeing it all:
convolutional network layers map the function of the human visual
system. NeuroImage 152, 184–194 (2017).
27. Wen, H. et al. Neural encoding and decoding with deep learning for
dynamic natural vision. Cereb. Cortex 28, 4136–4160 (2018).
28. Liu, P., Bo, K., Ding, M. & Fang, R. Emergence of emotion selectivity in
deep neural networks trained to recognize visual objects. PLOS
Comput. Biol. 20, e1011943 (2024).
29. Öhman, A., Flykt, A. & Esteves, F. Emotion drives attention: detecting
the snake in the grass. J. Exp. Psychol. Gen. 130, 466 (2001).
30. Bo, K. et al. Decoding neural representations of affective scenes in
retinotopic visual cortex. Cereb. Cortex 31, 3047–3063 (2021).
31. Abdel-Ghaffar, S. A. et al. Occipital-temporal cortical tuning to
semantic and affective features of natural images predicts associated
behavioral responses. Nat. Commun. 15, 5531 (2024).
32. Lazarus, R. S. Thoughts on the relations between emotion and
cognition. Am. Psychol.37, 1019 (1982).
33. Lazarus, R. S. On the primacy of cognition. Am. Psychol. 39, 124–129
(1984).
34. Storbeck, J. & Clore, G. L. On the interdependence of cognition and
emotion. Cognit. Emot. 21, 1212–1237 (2007).
35. Storbeck, J., Robinson, M. D. & McCourt, M. E. Semantic processing
precedes affect retrieval: the neurological case for cognitive primacy
in visual processing. Rev. Gen. Psychol. 10, 41–55 (2006).
36. Nummenmaa, L., Hyönä, J. & Calvo, M. G. Semantic categorization
precedes affective evaluation of visual scenes. J. Exp. Psychol. Gen.
139, 222 (2010).
37. Reisenzein, R. & Franikowski, P. On the latency of object recognition
and affect: evidence from temporal order and simultaneity judgments.
J. Exp. Psychol. Gen. 151, 3060 (2022).
38. Franikowski, P., Kriegeskorte, L.-S. & Reisenzein, R. Perceptual
latencies of object recognition and affect measured with the rotating
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
11


## Page 12

spot method: chronometric evidence for semantic primacy. Emotion
21, 1744 (2021).
39. Franikowski, P. & Reisenzein, R. On the latency of object recognition
and affect: evidence from speeded reaction time tasks. Emotion 23,
486 (2023).
40. Mastria, S., Codispoti, M., Tronelli, V. & De Cesarei, A. Subjective
affective responses to natural scenes require understanding, not
spatial frequency bands. Vision 8, 36 (2024).
41. Codispoti, M., Micucci, A. & De Cesarei, A. Time will tell: object
categorization and emotional engagement during processing of
degraded natural scenes. Psychophysiology 58, e13704 (2021).
42. Koc, A. N., Urgen, B. A. & Afacan, Y. Task-modulated neural
responses in scene-selective regions of the human brain. Vis. Res.
227, 108539 (2025).
43. Harel, A., Kravitz, D. J. & Baker, C. I. Task context impacts visual
object processing differentially across the cortex. Proc. Natl. Acad.
Sci. USA 111, E962–E971 (2014).
44. VanRullen, R. & Thorpe, S. J. The time course of visual processing:
from early perception to decision-making. J. Cognit. Neurosci. 13,
454–461 (2001).
45. Barrett, L. F. & Bar, M. See it with feeling: affective predictions during
object perception. Philos. Trans. R. Soc. B Biol. Sci. 364, 1325–1334
(2009).
46. Kurdi, B., Lozano, S. & Banaji, M. R. Introducing the open affective
standardized image set. Behav. Res. Methods 49, 457–470 (2017).
47. Prince, J. S. et al. Improving the accuracy of single-trial fMRI response
estimates using GLMsingle. eLife 11, e77599 (2022).
48. Kay, K., Rokem, A., Winawer, J., Dougherty, R. & Wandell, B.
GLMdenoise: a fast, automated technique for denoising task-based
fMRI data. Front. Neurosci. 7, 247 (2013).
49. Esteban, O. et al. fMRIPrep: a robust preprocessing pipeline for
functional MRI. Nat. Methods 16, 111–116 (2019).
50. Penny, W. D., Friston, K. J., Ashburner, J. T., Kiebel, S. J. & Nichols, T.
E. Statistical Parametric Mapping: the Analysis of Functional Brain
Images (Elsevier, 2011).
51. Van der Maaten, L. & Hinton, G. Visualizing data using t-SNE. J. Mach.
Learn. Res. 9, 2579–2605 (2008).
52. Murtagh, F. & Legendre, P. Ward’s hierarchical agglomerative
clustering method: which algorithms implement Ward’s criterion?. J.
Class.31, 274–295 (2014).
53. Lindh, D., Sligte, I. G., Assecondi, S., Shapiro, K. L. & Charest, I.
Conscious perception of natural images is constrained by category-
related visual features. Nat. Commun. 10, 4106 (2019).
54. Čeko, M., Kragel, P. A., Woo, C.-W., López-Solà, M. & Wager, T. D.
Common and stimulus-type-speciﬁc brain representations of
negative affect. Nat. Neurosci. 25, 760–770 (2022).
55. Soderberg, K., Jang, G. & Kragel, P. Sensory encoding of emotion
conveyed by the face and visual context. bioRxiv, 2023.2011.
2020.567556 (2023).
56. Benjamini, Y. & Yekutieli, D. The control of the false discovery rate in
multiple testing under dependency. Ann. Stat., 29, 1165–1188 (2001).
57. Gao, C., Ajith, S. & Peelen, M. V. Behavioral data - Object
representations drive emotion schemas across a large and diverse set
of daily-life scenes [Data set]. OSF https://osf.io/eks8u/ (2025).
Acknowledgements
C.G. was supported by National Natural Science Foundation of China
(32300863),anda RadboudExcellenceFellowshipfromRadboudUniversity
in Nijmegen, the Netherlands. M.V.P. was supported by European Research
Council (ERC) under the European Union’s Horizon 2020 research and
innovation program (grant agreement No 725970). We thank the Peelen Lab
members for the helpful discussions during lab meetings.
Author contributions
C.G. and M.V.P. designed the study. C.G. collected and analyzed the data.
C.G. drafted the original version of the manuscript. C.G., S.A., and M.V.P.
reviewed and edited the manuscript.
Competing interests
The authors declare no competing interests.
Additional information
Supplementary information The online version contains
supplementary material available at
https://doi.org/10.1038/s42003-025-08145-1.
Correspondence and requests for materials should be addressed to
Chuanji Gao or Marius V. Peelen.
Peer review information Communications Biology thanks the anonymous
reviewers for their contribution to the peer review of this work. Primary
Handling Editors: J.P. A peer review ﬁle is available.
Reprints and permissions information is available at
http://www.nature.com/reprints
Publisher’s note Springer Nature remains neutral with regard to
jurisdictional claims in published maps and institutional afﬁliations.
Open Access This article is licensed under a Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International License,
which permits any non-commercial use, sharing, distribution and
reproduction in any medium or format, as long as you give appropriate
credit to the original author(s) and the source, provide a link to the Creative
Commons licence, and indicate if you modiﬁed the licensed material. You
do not have permission under this licence to share adapted material
derived from this article or parts of it. The images or other third party
material in this article are included in the article’s Creative Commons
licence, unless indicated otherwise in a credit line to the material. If material
isnot includedin thearticle’s CreativeCommons licenceandyour intended
use is not permitted by statutory regulation or exceeds the permitted use,
you will need to obtain permission directly from the copyright holder. To
view a copy of this licence, visit http://creativecommons.org/licenses/by-
nc-nd/4.0/.
© The Author(s) 2025
https://doi.org/10.1038/s42003-025-08145-1
Article
Communications Biology |  (2025) 8:697 
12


