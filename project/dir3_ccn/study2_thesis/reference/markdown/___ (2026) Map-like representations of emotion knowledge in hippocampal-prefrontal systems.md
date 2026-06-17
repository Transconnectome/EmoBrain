# *** (2026) Map-like representations of emotion knowledge in hippocampal-prefrontal systems

**Source:** *** (2026) Map-like representations of emotion knowledge in hippocampal-prefrontal systems.pdf

---

## Page 1

Article
https://doi.org/10.1038/s41467-025-68240-z
Map-like representations of emotion
knowledge in hippocampal-prefrontal
systems
Yumeng Ma1 & Philip A. Kragel
1,2
Emotional experiences involve more than bodily reactions and momentary
feelings—they depend on knowledge about the world that spans contexts and
time. Although it is well established that individuals conceptualize emotions
using a low-dimensional space organized by valence and arousal, the neural
mechanisms giving rise to this conﬁguration remain unclear. Here, we examine
whether hippocampal-prefrontal circuits—neural structures implicated in
forming cognitive maps—also support the structural abstraction of emotional
experiences. Using functional MRI data collected as participants viewed
emotionally evocative ﬁlm clips, we ﬁnd that hippocampal activity represents
emotion concepts in a structured hierarchy, whereas ventromedial prefrontal
cortex more accurately tracks locations in a two-dimensional affective space.
Computational modeling reveals that hippocampal-prefrontal responses to
ﬁlms can be predicted based on the statistical regularities of emotion transi-
tions across multiple temporal scales. These ﬁndings demonstrate that
hippocampal-prefrontal systems represent emotion concepts in a map-like
way at multiple levels of abstraction, offering insight into how the brain
organizes emotion knowledge.
Our experience of emotions is more than just momentary reactions to
the world and accompanying feelings. Humans rely on emotion con-
cepts—knowledge that helps us categorize, communicate, and make
sense of emotional events in our lives. Some emotional knowledge is
grounded in the particulars of individual episodes, such as the ador-
able features of a speciﬁc childhood pet or the growl of an aggressive
neighborhood dog. Other knowledge concerns properties of events
that generalize across episodes, like an opportunity for a reward or the
presence of a threat. Even though emotional events can differ widely in
what we see, hear, think, or feel, we learn to abstract them into distinct
categories of variable yet related instances.
Behavioral evidence demonstrates that humans compress infor-
mation about complex emotional episodes into a low-dimensional
affective space1–4. When individuals judge the meaning of words5,6,
emotions conveyed by others7, predict how others are likely to feel in a
given situation8, or self-report on their own experience9, their ratings
primarily vary along dimensions of valence and arousal, evidence
taken by some to suggest that these variables are among the most
fundamental properties of the mind3. Based on these observations, it
has been suggested that humans represent the structure of affect in a
map-like way3,5 using dimensions of valence and arousal as the orga-
nizing axes. If represented in such a format, emotion concepts would
be positioned at speciﬁc locations in a relational network, much like
landmarks are placed on a Cartesian map. With experience, individuals
would learn the structure of affective space, enabling them to predict
transitions from one experience to the next (e.g., the tendency to shift
from a state of anxiety to fear as a threat becomes more proximal10)
and to make decisions based on the anticipated consequences of
actions11.
Neuroscience research has begun to characterize how the brain
represents knowledge about emotional events. Work in nonhuman
animals12–16 and human neuroimaging studies17–21 has identiﬁed
Received: 8 May 2025
Accepted: 22 December 2025
Check for updates
1Department of Psychology, Emory University, Atlanta, Georgia, USA. 2Department of Psychiatry and Behavioral Sciences, Emory University, Atlanta, Georgia,
USA.
e-mail: pkragel@emory.edu
Nature Communications|   (2026) 17:1518 
1
1234567890():,;
1234567890():,;


## Page 2

functionally dissociable systems involved in valence and arousal pro-
cessing. Neuroimaging has revealed that different categories of emo-
tional events are differentiated by patterns of activity that are
distributed across subcortical and cortical brain networks22–24, with the
content represented varying across regions. Responses to emotional
situations range from more situation-dependent activity in sensory
cortices25–28 and more general category representations in transmodal
cortical areas29,30. Together, these studies show that the brain repre-
sents emotional events using multiple systems in parallel, and that
information processing occurs in a hierarchical fashion.
Although it is well-established that multiple aspects of emotional
events are reﬂected across brain systems, it remains unclear how
emotionally relevant signals are transformed into low-dimensional
affective spaces. One possibility is that memory systems necessary for
organizing knowledge across domains are involved in mapping rela-
tionships between emotional events. Evidence suggests that the hip-
pocampal formation—known for its involvement in spatial navigation31,
memory32, and emotion33–35—represents knowledge in a map-like
way36–40. To build a map of the environment, neural populations in
the hippocampus bind together highly processed sensory inputs with
their positions in relational space, forming conjunctive codes of con-
cepts that jointly represent what is experienced and where it lies within
a structured map41. Based on the coactivation of hippocampal inputs,
neural populations in the entorhinal cortex42 and ventromedial pre-
frontal cortex (vmPFC) learn relations among concepts using a grid-
like code36–40. This format abstracts away from the content of experi-
ences to deﬁne a relational structure which can be used to guide
decision making and navigation. If similar mechanisms are used to
construct maps of emotion concepts43, then knowledge about distinct
sets of emotional experiences should be encoded in patterns of hip-
pocampal activity, whereas the spatial bases that deﬁne affective space
(i.e., grid-like codes that span dimensions of valence and arousal)
should be present in entorhinal cortex and vmPFC44.
In this work, we evaluate the proposal43 that hippocampal-
prefrontal systems represent emotion concepts in a cognitive map.
In this account, entorhinal and ventromedial prefrontal cortex learn
a general relational structure that can be used to predict the valence
and arousal of upcoming events. Through associative learning, the
hippocampus binds this information with highly processed sensory
inputs to link speciﬁc emotion concepts with locations in valence-
arousal space. Thus, although both sets of regions can be considered
to have map-like properties, the hippocampus uniquely represents
emotion concepts embedded in a two-dimensional affective space.
We test this account by analyzing fMRI signals acquired as human
participants watched a series of cinematic videos (sampled from the
Emo-FilM dataset45, Fig. 1). As information about prototypical emo-
tional events is typically accessible to consciousness, we ﬁrst probe
whether self-report measures of emotional experience can be deco-
ded from patterns of hippocampal-prefrontal activity, and whether
representations of emotion categories are distinct from a two-
dimensional representation of affective space. Finding evidence of
map-like representations in hippocampal-prefrontal systems, we
complement these analyses using a computational model of rela-
tional memory (the Tolman-Eichenbaum Machine46, TEM) that for-
mulates how an agent might learn from event sequences to construct
cognitive maps. We train artiﬁcial agents to learn the regularities of
emotion-laden environments by binding sensory representations
with structural knowledge about the world. After training, we show
that patterns of BOLD time-series in hippocampal-prefrontal systems
covary with internal representations in computational agents, and
are associated with self-reported emotion. These experiments reveal
that hippocampal-prefrontal systems represent emotion concepts in
a map-like way, providing a neurocomputational explanation of how
humans organize abstract emotion knowledge.
Results
The hippocampus represents multiple emotion concepts in a
hierarchically organized structure
We ﬁrst evaluated whether hippocampal activity represents multiple
emotion concepts in a format that is not merely based on variation in
Fig. 1 | Experimental paradigm and behavior. a participants (n = 29) watched over
2.5 h of 14 brief cinematic videos while the BOLD signal was measured with fMRI
over the course of 4 scanning sessions. The video stimuli were additionally rated by
an independent group of 44 participants. We examined emotion captured by
continuous ratings of 13 emotion categories, 2 measures of valence, and 2 measures
of arousal. Representative frames are cropped from videos in the LIRIS-ACCEDE
dataset114, distributed under Creative Commons BY 3.0, BY-SA 3.0, or BY-NC 3.0
licenses. These frames are reproduced under the terms of these licenses and are
excluded from this article’s Creative Commons License. b Hexagonal binned plot of
self-report data. Each hexagon represents a region of a two-dimensional space
deﬁned by ratings of valence (x-axis) and arousal (y-axis) across ﬁlms. Bins are
colored to indicate the category with the highest rating across time points falling in
that region. Blank areas indicate bins without observations in the corresponding
valence-arousal range. Hexagonal binned plots for each individual emotion cate-
gory are shown in Supplementary Fig. 1.
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
2


## Page 3

affect. To this end, we trained multivariate decoders (Supplementary
Fig. 2) that map patterns of hippocampal fMRI time series (9538
measurements in 1816 voxels, per participant on average) onto either
multivariate emotion category ratings, or locations in a two-
dimensional space derived from multidimensional scaling of emo-
tion category ratings (hereafter referred to as affective space, see
Supplementary Fig. 3). Models were trained using data acquired from
multiple ﬁlm stimuli and evaluated by testing them on independent
stimuli (leave-one-ﬁlm-out cross-validation, 13 ﬁlms total for each of
n = 29 participants) and comparing the readout of category and
affective space decoders (see “Methods”). This analysis revealed that
category ratings were more accurately decoded (z = 0.0525, 95%
bootstrap CI [0.0454, 0.0592]) than locations in affective space
(z = 0.0428, 95% bootstrap CI [0.0347, 0.0505]; Δz = 0.0097, 95%
bootstrap CI [0.0025, 0.0169], d = 0.4946, p < .001; see Supplementary
Figs. 4, 5 for contributions of individual voxels). Together, these results
are consistent with the proposal that the hippocampus encodes
multiple emotion concepts in a format that is not reducible to a two-
dimensional representation of affect.
Because the hippocampus represents event sequences in a hier-
archal manner47–49, we expected that hippocampal responses to con-
cepts that tend to occur in temporal proximity (e.g., disgust, anger, and
guilt or anxiety, fear, and surprise) would be more similar to one
another48, reﬂecting the graded similarity structure typically observed
in ratings of emotion terms5,50,51 as opposed to a simple structure in
which emotion concepts are independent. We assessed whether this
was the case by analyzing the outputs of hippocampal decoders using
agglomerative clustering. For each participant, we computed the
similarity of model predictions over time to produce a conceptual
similarity matrix (Supplementary Fig. 6). We modeled the similarity
structure in two ways: with a model that estimated temporal similarity
by averaging across concepts of the same valence (referred to as the
valence model), and with another model that estimated temporal
similarity for all pairs of concepts (the full model; Fig. 2c). To estimate
Fig. 2 | Decoding the representation of emotion concepts in the human hip-
pocampus. a Performance of decoding models trained to predict emotion
category and binarized valence-arousal ratings from BOLD signal in anterior
hippocampus, posterior hippocampus, and amygdala. Each point represents the
prediction-outcome correlation averaged across rating items for category or
binarized valence-arousal from a single participant (n = 29 independent partici-
pants). Points from the same participants are connected by gray lines, black hor-
izontal lines indicate the mean, and gray dashed lines represent chance (i.e., zero
correlation between predicted and observed outcomes). b Agglomerative clus-
tering on the group-averaged (n = 29) similarity matrix of category ratings pre-
dicted from hippocampal BOLD signal (see Supplementary Fig. 7 for individual
participants’ dendrograms). c First-order correlation matrices illustrating the
similarity structure of predicted emotion concepts from hippocampal fMRI pat-
terns. Fully speciﬁed (all possible pairs of emotion concepts) and valence models
(simpliﬁed models averaging within and between positive and negative categories)
characterize covariation between emotions and are estimated using data from all
but one hold-out participant (S01 shown here; see Supplementary Fig. 6 for all 29
participants). d Second-order correlations between each held-out participant’s
similarity matrix and the full and valence models. Each point represents a partici-
pant (n = 29). Points from the same participants are connected by gray lines, black
horizontal lines indicate the group mean.
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
3


## Page 4

model generalizability, we performed a leave-one-participant-out
procedure in which temporal correlations were averaged across all
but one participant and compared to the similarity structure of the
held-out participant. This generalization test revealed that the corre-
spondence acrossparticipants in the fully speciﬁed model (Spearman’s
r = .978, SD =. 007, 95% bootstrap CI [.975, 0.980], p < .001) was greater
than that of the valence only model (Spearman’s r = .842, SD = .013,
95% bootstrap CI [.838, 847], p < .001; Fig. 2d), and that a substantial
portion of variance across participants remained after accounting for
valence (Spearman’s r = .486, SD = . 014, 95% bootstrap CI [.481, 491],
p < .001). These results suggest that the hippocampus does not
represent emotion concepts independently, but as a hierarchy that is
stable across participants (Fig. 2b) and captures relationships between
emotions primarily along a dimension of valence.
Central to accounts of memory, navigation, and emotion
processing52, the hippocampal long axis is characterized by gradients
in connectivity, gene expression53, neural timescale54, and behavioral
specialization55,56. Particularly relevant for the representation of emo-
tion knowledge are observations that hippocampal activity represents
event sequences at multiple timescales, with more rapid changes
coded in more posterior portions of the hippocampus54,56. Such var-
iation leads to the prediction that ﬁne-grained distinctions between
emotional events should be captured by activity in posterior hippo-
campus, whereas more general distinctions that take place over longer
timescales should be represented in more anterior portions of the
hippocampus. To examine variation in emotion representation along
the hippocampal long axis, we trained multivariate decoders to predict
variation in ﬁne-grained (e.g., fear, anger, pride, joy or surprise) and
broad emotion concepts (e.g., good, or activated) using signals either
in the posterior or anterior hippocampus (based on a segmentation at
the plane y = −21 in MNI space). Model comparisons revealed that
decoding performance depended on both hippocampal portion and
representational scale (Δz = 0.0101, 95% bootstrap CI [0.0054, 0.0149],
d = 0.7791, p = .003, Fig. 2a), with greater decoding performance in
posterior hippocampus as emotion granularity increased (see Sup-
plementary Fig. 8 for performance on all ratings).
Complementing observations that knowledge from multiple
domains is hierarchically organized in the hippocampus, evidence
shows that the amygdala encodes some forms of abstract relation-
ships, albeit in a different format than the hippocampus57. To assess
whether this was the case for emotion concepts in the present study,
we trained a new set of decoders on amygdala responses and com-
pared their performance to that of those trained on signals in anterior
and posterior hippocampus. We found amygdala responses did not
predict category ratings as accurately as signals in posterior hippo-
campus
(Δz = −0.0117,
95%
bootstrap
CI
[−0.0063,
−0.0171],
d = −0.7850, p = .001), particularly when compared to predictions of
binarized valence-arousal ratings (Δz = −0.0125, 95% bootstrap CI
[−0.0077, −0.0172], d = −0.9538, p = .002). By contrast, amygdala
decoders performed comparably to anterior hippocampal decoders
(category ratings: Δz = −0.0040, 95% bootstrap CI [−0.0095, 0.0015],
d = −0.2660, p = .229; region × target variable interaction: Δz =
−0.0023, 95% bootstrap CI [−0.0071, 0.0024], d = −0.1780, p = 0.481;
Fig. 2a). These results are broadly consistent with recent ﬁndings
showing that the hippocampus and amygdala differ in their repre-
sentations of abstract social relationships57,58, yet suggest that pos-
terior hippocampus may be particularly important for organizing
more ﬁne-grained emotion knowledge.
Ventromedial prefrontal cortex represents trajectories in a
two-dimensional affective space
We found that hippocampal BOLD signals contained information
about emotion concepts, and to a lesser degree, information about
trajectories in affective space. These observations suggest the hippo-
campus could play an important role in mapping emotion concepts—
conveying information to the entorhinal cortex or vmPFC to construct
an abstract, two-dimensional space36–40. If this is the case, then deco-
ders trained on signals from these neocortical regions should predict
trajectories in affective space more accurately than emotion category
ratings. Alternatively, we may have observed better hippocampal
prediction of category ratings because they were driven by particularly
salient events, or because they occurred at timescales that are more
easily captured by fMRI. In such cases, decoding performance should
be higher for category ratings than trajectories in affective space,
regardless of the neural origin of BOLD signals being decoded.
Therefore, to dissociate representations across regions, we compared
decoders trained to predict emotion category ratings and affective
space using signals acquired in the hippocampus, entorhinal cortex,
vmPFC, and the amygdala.
Consistent with a map-like representation, we found that signals
from vmPFC predicted locations in affective space (z = 0.0956, 95%
bootstrap CI [0.0831, 0.1076]) more accurately than emotion category
ratings (z = 0.0838, 95% bootstrap CI [0.0777, 0.0902]; Δz = 0.0118,
95% bootstrap CI [0.0047, 0.0191], d = 0.0118, p = .020), similar to
observations from studies examining decision-making about abstract
social relationships58. This difference substantiated a double dis-
sociation, such that the hippocampus contained more information
about emotion category ratings whereas vmPFC better captured
information about trajectories in affective space (Δz = 0.0215, 95%
bootstrap CI [0.0134, 0.0297], d = 0.9566, p = .001; Fig. 3c). By con-
trast, activity in the entorhinal cortex and amygdala predicted the two
target variables with comparable accuracy (entorhinal cortex: Δz =
−0.0004, 95% bootstrap CI [−0.0071, 0.0067], d = −0.0195, p = .918;
amygdala: Δz = −0.0036, 95% bootstrap CI [−0.0102, 0.0033],
d = −0.0195, p = .221). Together, these results show that multiple
regions carry information about emotion concepts (see Supplemen-
tary Fig. 9 for region-wise effect sizes and Supplementary Fig. 10 for
results from less constrained searchlight mapping), and that the
vmPFC contained more information about affective trajectories.
Of structures involved in relational and affective processing,
several are known to encode independent dimensions of valence
and arousal59–63 in addition to integrated, map-like representations.
We therefore tested whether direct coding of each affective
dimension measured in self-report could be decoded from BOLD
signals acquired during ﬁlm viewing using the same approach used
to decode trajectories in affective space. Decoding continuous self-
report ratings of valence and arousal produced similar results to
affective space decoding, with the exception that readouts in vmPFC
were not better predictors of valence and arousal than emotion
category ratings (Supplementary Table 1 and Supplementary
Figs. 11–14). These data suggest that vmPFC contains more inte-
grated representations of affect compared to simple coding of
independent affective dimensions.
Structural abstraction of emotion knowledge in hippocampal-
prefrontal systems
The results of multivariate decoding experiments indicated that
hippocampal-prefrontal systems represent emotion concepts in ways
that resemble a cognitive map. Hippocampal activity carried more
information about emotion category ratings while preserving their
similarity structure, reﬂecting a hierarchical organization. The vmPFC
more accurately tracked trajectories in affective space, suggestive of a
low-dimensional relational code. This dissociation of function aligns
with theoretical accounts suggesting that hippocampal binding of
information about “what” occurs during an event and “where” it occurs
in space and time could explain the formation of cognitive maps64,65.
To more explicitly probe the representational format of emotion
concepts in hippocampal-prefrontal systems, we simulated concept
formation using TEM46, a computational model of relational mem-
ory (Fig. 4).
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
4


## Page 5

In learning to map the environment, TEM factorizes sensory
observations into two separate bases—one that represents the con-
tents of experience and another that represents relationships between
experiences—and binds them together into a conjunctive code. This
conjunction is represented in layer p, which is used to make predic-
tions about upcoming sensory observations and locations in layer g.
Activity in layer p resembles hippocampal population activity that
encodes “what” is located “where” in an environment, with localized
ﬁring ﬁelds for speciﬁc concepts (Fig. 4c). In contrast, activity in layer g
resembles that of entorhinal cortex, with ﬁring ﬁelds that span the
entire space (e.g., grid cell-like activity; Fig. 4c), providing an abstract
structural code that can be used for making inferences in any envir-
onment or in new problems that have a similar relational structure. In
this way, TEM formalizes how an agent learns representations thought
to be present in hippocampal-prefrontal systems. This model allowed
us to test whether hippocampal signals more accurately predict the
conjunction of concepts and their location in the affective space
(activity in layer p), and whether vmPFC signals more accurately pre-
dict the relational structure of affective space (activity in layer g).
For TEM agents to experience transitions between emotional
events that approximate human experiences, we created an artiﬁcial
environment based on emotion category ratings provided by partici-
pants in the online sample. We discretized the affective space derived
from multidimensional scaling (Fig. 3b) into a grid environment
(Fig. 4a). During training, agents randomly explored this environment,
learning the relational structure of emotion concepts through
experience, mimicking one way the brain could learn to represent
emotion concepts over time. This simulation enabled us to deﬁne
representations of emotion concepts and relations between them and
evaluate how accurately they can be decoded from patterns of hip-
pocampal activity in the fMRI signal. To model human brain responses
during ﬁlm viewing, we generated TEM activation time series by
averaging the activation of layers p and g in artiﬁcial agents as they
navigated the affective space, weighting the responses in layers p and g
using a linear combination of ratings on all emotions at each point.
Similar to the multi-scale representations observed in place cells
across the hippocampal long axis66,67, TEM includes artiﬁcial neurons
at multiple levels of abstraction, allowing it to represent both ﬁne-
grained and coarse aspects of the environment. Because representa-
tions in layers p and g differed the most at small scales in our simu-
lations (Fig. 4c and Supplementary Fig. 15), we predicted that
hippocampal decoding of layer p would be more accurate than layer g
for units with narrow ﬁring ﬁelds (smaller scales), as they better cap-
ture transitions between speciﬁc emotions as opposed to large tran-
sitions in the affective space (larger scales). Consistent with this
prediction, we found higher cross-validated decoding performance for
layer p than g (Δz = 0.0017, 95% bootstrap CI [0.0001, 0.0034],
d = 0.3773, p = 0.015; Fig. 5a). Further, a linear contrast across
Fig. 3 | Decoding emotion category ratings and trajectories in affective space
from BOLD response patterns in hippocampal-prefrontal systems and the
amygdala. a Rendering of parcellations of hippocampus (orange), entorhinal
cortex (dark blue), and ventromedial prefrontal cortex (vmPFC; light blue).
b Trajectories of experience in an abstract, two-dimensional affective space from
an example ﬁlm (see Supplementary Fig. 3 for all ﬁlms). Orange circles show the
location of emotion categories embedded in the space. The blue line shows the
trajectory of one example ﬁlm projected into the two-dimensional space. Dots
along the trajectory indicate successive timepoints, increasing in size to denote
progression through the ﬁlm. For visualization, the trajectory coordinates were
linearly rescaled to match the range of the category positions; decoding analyses
were performed on unscaled trajectories. c Performance of decoding models
trained to predict emotion category ratings (orange circles) and locations in two-
dimensional affective space (blue circles) from BOLD signal in hippocampus,
entorhinal cortex, amygdala, and vmPFC. Each point represents the prediction-
outcome correlation averaged across category rating items or two-dimensional
locations from a single participant (n = 29 independent participants). Points from
the same participants are connected by gray lines, black lines indicate the mean,
and gray dashed lines represent chance.
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
5


## Page 6

representational scales revealed that as scale decreased, decoding
performance increased more for layer p than for layer g (Δz = 0.0352,
95% bootstrap CI [0.0254, 0.0448], d = 1.3232, p < .001; Fig. 5c), indi-
cating that more accurate decoding of layer p activity was driven by
information related to small-scale conjunctive codes.
Because ﬁring ﬁeld size varies along the hippocampal long
axis66,67, we next tested whether information about smaller-scale layer
p activity was more strongly represented in the posterior hippo-
campus. To this end, we trained separate decoding models to predict
TEM activations at small (0 and 1) and large representational scales (2
through 4), and compared the accuracy of readouts from anterior
versus posterior hippocampal fMRI activity. This analysis revealed
differences in decoding accuracy that depended on both hippocampal
portion and scale (Δz = 0.0052, 95% bootstrap CI [0.0033, 0.0071],
d = 0.9909, p = .002; Fig. 5b, d), indicating that smaller-scale layer p
activity was decoded more accurately in posterior than anterior
hippocampus.
We observed that hippocampal decoders predicted variation in
emotional experience as reﬂected in both human self-report and the
activity of TEM agents. To determine whether decoders utilized com-
mon patterns of hippocampal response, we compared decoding per-
formance before and after controlling for predictions of p (see
“Methods” ‘Comparing the decoding performance of TEM activity’ for
details). We found that accounting for hippocampal signals related to
layer p activity impaired the readout of emotion category ratings
(Δzcat = 0.0042, 95% bootstrap CI [0.0020, 0.0061]) more so than
trajectories in affective space (Δzspace = 0.0014, 95% bootstrap CI
[0.0000, 0.0029]) and valence-arousal ratings (Δzdim = 0.0002, 95%
bootstrap CI [0.0010, 0.0014]; Δzcat-space = 0.0028, 95% bootstrap CI
[0.0004, 0.0052], d = 0.4205, p = .003; Δzcat-dim = 0.0039, 95% boot-
strap CI [0.0021, 0.0057], d = 0.7890, p = .001). This result indicates
that a conjunctive representation of emotion concepts can account for
some, but not all, of the enhanced prediction of emotion category
ratings compared to affective dimensions in the hippocampus.
The entorhinal cortex and vmPFC are thought to represent rela-
tions among objects, locations, and goal-states in a domain general
way36,39,68,69. If these cortical areas play a similar role in representing
relations among emotion concepts, decoding layer g activity from
these regions should be more accurate than decoding layer p activity.
We tested this prediction by comparing the decoding accuracy as a
function of brain region (hippocampus, entorhinal cortex, and
vmPFC), layer (p and g), and scale (small and large). Analysis of var-
iance revealed that decoding performance depended on all three
variables (a three-way interaction: F(8, 616) = 12.44, partial η² = 0.14,
p < .001; Supplementary Fig. 16). Direct comparisons (Fig. 5c) indicated
that there was better readout of layer g than layer p activity at large
scales in vmPFC (Δz = 0.0712, 95% bootstrap CI [0.0614, 0.0809],
d = 2.6747, p < .001), and to a lesser degree in the entorhinal cortex
(Δz = 0.0099, 95% bootstrap CI [0.0001, 0.0199], d = 0.3680, p = .046).
Decoding layer g was more accurate at larger scales in the vmPFC than
in both hippocampus (Δz = 0.0542, 95% bootstrap CI [0.0447, 0.0640],
d = 2.0455, p < .001; Fig. 5c) and entorhinal cortex (Δz = 0.0604, 95%
bootstrap CI [0.0506, 0.0700], d = 2.2580, p < .001; Fig. 5c). Con-
versely, decoding layer p activity was better at small scales in the
hippocampus compared to both entorhinal cortex (Δz = 0.0191, 95%
bootstrap CI [0.0093, 0.0289], d = 0.7091, p < .001; Fig. 5c) and vmPFC
(Δz = 0.0182, 95% bootstrap CI [0.0086, 0.0279], d = 0.6815, p = .003;
Fig. 5c, left and right). Together, these results suggest that the vmPFC
contains more information about large-scale structural abstractions
(e.g., that one portion of a video was more pleasant than another),
whereas the hippocampus represents conjunctive codes of multiple
emotion concepts embedded in the affective space.
Discussion
Knowledge about the world is thought to be organized into a map-like
representation that enables organisms to ﬂexibly navigate complex
environments70.
In
these
accounts,
domain
general
cortico-
hippocampal networks use similar mechanisms to organize knowl-
edge of physical locations31, sensory percepts36, social relationships37,71,
and abstract concepts39. Here, we found that patterns of human
hippocampal-prefrontal activity represented a hierarchy of emotion
concepts in a map-like way that was not reducible to dimensions of
Fig. 4 | Simulating the construction of emotion maps using the Tolman-
Eichenbaum Machine (TEM). a 11 × 11 discrete environment created for emotion
concepts based on their locations in the multidimensional scaling of category
ratings. Nodes with an emotion category assigned are colored and labeled. Arrows
between nodes indicate possible movements of agents in the environment.
b Schematic of layers and hierarchical organization of TEM. The model consists of
two layers: g, which learns the relational structure between abstract locations in the
environment, and p, which receives inputs from sensory observations and abstract
locations to learn their associations. Different temporal ﬁlters for sensory obser-
vations are learned by separate streams of the model, capturing varying scales of
the spatiotemporal structure. c Rate maps of example hippocampal and entorhinal
cells obtained by averaging the activity of each cell at each node. The colorbar
represents the activity normalized per cell, ranging from each cell’s minimum to
maximum.
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
6


## Page 7

valence and arousal, suggesting that emotion knowledge may be
organized via similar mechanisms as knowledge for other domains.
Several prominent accounts of emotional experience suggest that
the hippocampus and vmPFC, as nodes in the default network, are
involved in the conceptualization of emotional experiences72,73. Con-
sistent with these accounts and past decoding studies17,18,22–24, we
found that information about emotion categories and valence-arousal
dimensions was represented in multiple regions of the default net-
work. Our observation that hippocampal representations generalized
across ﬁlm stimuli with different audiovisual and linguistic features
suggests that emotion concepts may result from the abstraction of
sensory signals in the environment. Further supporting this view, the
emotion concepts we decoded were based on self-report ratings from
independent observers, highlighting that these abstractions are shared
across individuals. Nevertheless, whether emotion concepts repre-
sented in hippocampal-prefrontal systems reﬂect the statistical reg-
ularities of important life events that are shared across individuals and
cultures, or whether they are constructed more ﬂexibly as ad hoc
categories74 shaped by individual experience, remains an open ques-
tion. Existing developmental research24 suggests that neural repre-
sentations of emotion concepts are present early in life, as young as
age ﬁve, and that they stabilize during adolescence, consistent with a
learning process that extracts regularities over time. However,
longitudinal research is needed to determine the extent to which
behaviors that draw on emotion knowledge follow a similar develop-
mental trajectory as the hippocampus.
Our ﬁndings go beyond the results of existing decoding studies by
demonstrating that representations from an unsupervised agent using
conjunctive coding—which binds sensory information and structural
knowledge about emotions (i.e., that some experiences feel more or
less pleasant or arousing than others)—can model hippocampal-
prefrontal responses to emotional ﬁlms. Whereas past work has
shown that information about different aspects of emotional experi-
ences is distributed across the cortex22,23, and that differences in
valence covary with BOLD responses in cortical midline regions17,18, our
computational experiments advance an account of how the human
brain organizes emotion concepts. We found that hippocampal signals
represented locations in an affective space produced through a con-
junctive process (as reﬂected in layer p of TEM). Although we did not
ﬁnd evidence that entorhinal cortex robustly represented affective
space, possibly reﬂecting challenges imaging this region75 or a differ-
ent role in organizing knowledge about emotions, vmPFC signals were
most strongly related to large scale bases that span affective space (i.e.,
layer g activity with low frequency ﬁring ﬁelds, see Fig. 4c). More
accurate readout of large-scale layer g activity in vmPFC aligns with its
longer temporal integration windows, a feature typical of brain regions
Fig. 5 | Decoding representations of conjunctive codes and relational structure
in hippocampal-prefrontal systems. a Performance of decoding models trained
to predict activity in layers p and g of the Tolman-Eichenbaum Machine (TEM) from
BOLD signal in the hippocampus. Each point represents the prediction-outcome
correlation averaged across cells and scales for one participant (n = 29 independent
participants). b Performance of decoding models trained to predict small- and
large-scale p activity from BOLD signal in anterior and posterior hippocampus. Each
point represents the prediction-outcome correlation for one participant (n = 29).
c Linear contrast of decoding performance across TEM scales. Negative values
indicate higher decoding performance at smaller scales; positive values indicate
higher performance at larger scales. Each point represents one participant (n = 29).
See Supplementary Fig. 16 for decoding performance at each individual scale.
d Maps indicating the scale with the largest PLS coefﬁcient, with smaller scales
shown with warm colors and large scales shown with cool colors (see also Sup-
plementary Fig. 17). Maps indicate the scale with the largest t-statistic (FDR q < 0.05)
averaged across cells for each layer (Supplementary Figs. 18–20). In the hippo-
campus, more warm colors are shown in the posterior portions for p relative to g. In
the ventromedial prefrontal cortex (vmPFC), more cool colors are shown for g
relative to p.
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
7


## Page 8

at the top of the cortical hierarchy76,77. Considered alongside evidence
that vmPFC and other nodes of the default network exhibit grid-like
activity during tasks from multiple domains36,39,78, these ﬁndings sug-
gest that similar neural mechanisms may be involved for reward-based
decision making79, social inferences80, and reporting emotional
experience18—all of which involve relational processing and could be
solved using map-based strategies81.
We observed variation in the granularity of emotion concepts
along the hippocampal long axis. This ﬁnding aligns with observations
that the posterior hippocampus encodes ﬁne-grained distinctions
between entities55, characterized by smaller, more precise ﬁring ﬁelds
compared to the anterior hippocampus66,67. It is also consistent with
evidence that the hippocampus represents event sequences hier-
archically, with longer timescales being represented in more anterior
portions of the hippocampus56. Notably, post hoc analyses revealed
that several emotion categories (e.g., love, satisfaction, guilt) were
better decoded from anterior compared to posterior hippocampus
(Supplementary Fig. 8 and Supplementary Table 2). This pattern could
reﬂect the temporal dynamics of these emotions, which often involve
the integration of various aspects of emotional events over longer
timescales than putatively basic emotions, which are thought to occur
with a rapid onset and short duration82.
Using computational models to characterize brain responses to
naturalistic stimuli provides a fresh look at how the brain constructs
cognitive maps more generally. Previous investigations have char-
acterized brain responses to less complex stimuli37,71, such as static
images or text-based narratives. Although our experimental paradigm
was not interactive, our use of naturalistic movies offers a more eco-
logically valid window into how hippocampal-prefrontal systems pro-
cess dynamic, rich, emotional experiences. Further, our application of
TEM46 to human fMRI data bridges theoretical models, animal elec-
trophysiology, and human neuroimaging. This approach allows us to
make testable predictions about the computational mechanisms
underlying the observed representational patterns, connecting mac-
roscale BOLD signals to principles consistent with those learned from
cellular-level organization.
Our computational modeling results suggest that map-like
representations in hippocampal-prefrontal systems could result from
learning the statistical regularities of event transitions. By recasting
continuous navigation as the problem of learning transitions in a dis-
crete state space, the same hippocampal-prefrontal representations
can be used to accomplish a variety of tasks, whether conceived as
learning linkages on a graph or directions in a two-dimensional Eucli-
dean map65. Our fMRI results are consistent with both conceptions of a
cognitive map, as we found hippocampal-prefrontal activity predicted
both locations in a twocontinuous affective space and activity inTEM—
a model trained to perform structural abstraction through learning
transitions between discrete states. Whether graph-like and map-like
representations result from sequential stages of abstraction or quali-
tatively distinct processes remains an open question for future
research.
Our ﬁndings extend our understanding of hippocampal concept
cells, which have primarily been linked to physical entities (e.g., per-
sons, objects) in single-unit recording studies83,84. Whereas prior fMRI
studies have explored hippocampal-prefrontal contributions to the
processing of abstract information, they have focused largely on grid-
like
coding
patterns
when
participants
traversed
conceptual
spaces36,39. Here, we reveal that the hippocampus represents emotion
concepts at multiple levels of abstraction, dovetailing with recent
ﬁndings showing that its representational capacity spans both physical
and abstract domains. Importantly, our decoding models generalize
across different ﬁlms, demonstrating that these representations are
not tied to low-level perceptual features but instead capture higher-
level, abstract properties of emotion concepts. This generalizability
highlights the hippocampus’ role in encoding conceptual structure
beyond speciﬁc sensory experiences, a role that could support the
organization of abstract conceptual knowledge.
Several limitations constrain the interpretation of our ﬁndings.
Our focus on dimensions of valence and arousal necessarily over-
simpliﬁes emotional experience, which can be organized by far more
than two dimensions85,86. Emotion knowledge may be organized in low-
dimensional embeddings of other variables, such as effort, certainty,
and situational control. In addition, the spatiotemporal resolution of
fMRI precludes measurement of neural dynamics and phase codes
thought to support navigation87,88. To the extent that neural mechan-
isms are shared across species, future research using high-density
neuronal
recordings
in
rodents89,90
and
human
intracranial
electrophysiology91 will be critical for testing whether navigating
affective spaces involves computations similar to those used for spatial
navigation. Further, TEM is not the only model of hippocampal com-
putations. Alternative models grounded in reinforcement learning92
may offer complementary insights, particularly for studying emotion
concepts, which inherently encode value and motivational relevance.
This frameworkaligns with evidence suggesting the role of the anterior
hippocampus
and
vmPFC
in
motivation
and
goal-directed
behavior93–95. Future research should examine whether models of
reinforcement learning can better predict hippocampal-prefrontal
representations of emotion concepts.
In sum, the present work demonstrated that hippocampal-
prefrontal systems exhibit map-like representations of emotion con-
cepts. Our ﬁndings shed light on the long-standing observation that
people report their feelings using a mental map organized by dimen-
sions of valence and arousal1. Although it has long been suggested that
our conceptualization of emotions emerges from these fundamental
dimensions74,96, we have shown that brain systems responsible for
computing relations between distinct experiences are capable of
structuring emotion knowledge in a low-dimensional affective space.
These ﬁndings raise the possibility that the map-like structure
observed in self-report is the product of computations performed in
hippocampal systems, rather than being an innate structure afforded
by the human brain.
Methods
Emo-FilM dataset
Both
the
fMRI
data
(https://openneuro.org/datasets/ds004892/
versions/1.0.0) and emotion ratings (https://openneuro.org/datasets/
ds004872/versions/1.0.1) used in this work are from the Emo-FilM
dataset45 publicly available on OpenNeuro. Both studies were
approved by the Geneva Cantonal Commission for Ethics in Research
and complied with the Code of Human Research Ethics (2014). No
formal statistical procedure was used to predetermine sample size
because this study analyzed pre-existing datasets.
fMRI data
Brain activity was measured using fMRI in 30 healthy participants who
watched 14 short ﬁlms (mean duration 11 min 26 s) in a pseudo-random
order over four sessions (see Morgenroth et al.45 for detailed
descriptions of the ﬁlms). Film stimuli were presented using the Psy-
chophysics Toolbox97 in MATLAB 2012. All participants were right-
handed and met the inclusion criteria of normal or corrected-to-
normal vision, high-level English comprehension, no history of psy-
chiatric or neurological illness, and no neuropharmacological or
recreational drugs. We excluded participant 07 due to missing data
from 3 ﬁlms on OpenNeuro, leaving 29 participants (18 females based
on self-report, aged 18–34). All participants provided written informed
consent. Sex/gender was not included as an experimental factor in the
analyses because we did not have prior predictions about sex/gender-
related differences in emotion knowledge. MRI data were acquired on
a 3 T Siemens Magnetom TIM Trio scanner with a 32-channel head coil
(Siemens, Erlangen, Germany). Anatomical T1 images were acquired
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
8


## Page 9

with a GRAPPA sequence for the purpose of co-registration (TR = 1.9 s,
TE = 2.27 ms, ﬂip angle = 9°, FOV = 256 mm, resolution = 1 mm3, in
plane resolution of 256 × 256 × 192 sagittal slices). Functional images
were acquired with the same multi-band frequency protocol (TR =
1.3 s,
TE = 30 ms,
ﬂip
angle = 64°,
FOV = 210 mm2,
resolution = 2.5 mm3, 54 interleaved slices).
fMRI preprocessing. Preprocessing of fMRI data, performed using
FEAT (FMRI Expert Analysis Tool) Version 6.00 from FSL (FMRIB’s
Software Library, www.fmrib.ox.ac.uk/fsl), included co-registration to
structural, standard space, and each participant’s functional volume,
motion correction, non-brain tissue removal, spatial smoothing (6 mm
FWHM), grand-mean intensity normalization, high-pass temporal ﬁl-
tering (50 s cutoff), and regression of white matter, cerebrospinal ﬂuid,
and six motion parameters.
Emotion ratings. Emotion ratings98 were collected from 44 inde-
pendent participants (23 females based on self-report, aged 20-39)
recruited online, using the same inclusion criteria as the fMRI sam-
ple. Participants were from the Geneva area, matched with the fMRI
sample, but with no overlap between the two samples. All partici-
pants provided written informed consent and were compensated at
20 CHF per hour. A total of 55 items were rated across six groups of
items: Appraisal, Expression, Physiology, Motivation, Feeling, and
Discrete Emotion. Participants completed the rating tasks at their
own pace within a six-week period, using the annotation software
CARMA99 on their own computers. To rate each item, participants
continuously moved a mouse-controlled cursor along a bar (sam-
pling rate = 1 Hz). Each participant rated six randomly assigned items
in total. For each item, participants rated it for all ﬁlms in a random
order before moving to the next item, ensuring a sufﬁcient delay
between repetitions of the same ﬁlm. Consensus ratings were
derived by averaging from three or four raters per item and ﬁlm (see
Morgenroth et al.45 for a detailed description of consensus calcula-
tion and quality control procedures). No participants were excluded
due to data quality issues.
In the current study, we used all 13 items (anger, anxiety, fear,
surprise, guilt, disgust, sad, regard, satisfaction, warmheartedness,
happiness, pride, love) in the Discrete Emotion category. For valence
and arousal, we selected four items (valence: good, bad; arousal: calm
(restless-calm), at ease (nervous-at ease) from the Feeling items, as
they best align with our goal of capturing emotion concepts in terms of
their location within the valence-arousal space. Other Feeling items
including intense emotion, strong (weak-strong), and alert (tired-alert)
were not used because they were less directly relevant to arousal or did
not align with the goal of capturing conceptual knowledge of emotion
rather than physiological states. For example, intense emotion reﬂects
the magnitude of emotions, weak-strong may reﬂect a sense of cap-
ability and self-efﬁcacy, and tired-alert is more indicative of wakeful-
ness rather than the concept of arousal.
Deﬁning regions of interest
Masks of the hippocampus and entorhinal cortex were obtained from
the Julich-Brain Cytoarchitectonic Atlas100 Masks of anterior and pos-
terior hippocampus were obtained by splitting the hippocampal mask
at y = −21 in the MNI space101. For the vmPFC mask, we selected
Brodmann areas 10, 11, 14, 24, 25, and 32, obtained from a multimodal
parcellation of the human cortex102.
Simulating hippocampal learning with the Tolman-Eichenbaum
Machine
TEM is an artiﬁcial neural network trained to navigate on a connected
graph46. At each time step, it takes the current sensory observation (x)
and an action (a) as inputs, and outputs a predicted sensory observa-
tion for the next timestep. To accomplish the objective of accurately
predicting next sensory inputs even when taking paths that have not
been experienced before, TEM factorizes its representation into
two parts: (1) relations between locations on the graph and (2) the
association between sensory observations and their location on
the graph.
TEM factorizes sensory information using two layers that are
inspired by the functional anatomy of the entorhinal cortex and hip-
pocampus. The entorhinal layer of the network (g) generates distinct
representations for each location and learns their relations through
path integration. At each timestep, g updates its representation based
on the received action, using a recurrent architecture with weights
updated via backpropagation during training. The hippocampal layer
of the network (p) receives sensory input along with the estimated
location from g. Memories of sensory-location associations are stored
in Hebbian weights between units in p and can later be retrieved by
attractor dynamics.
To efﬁciently represent environments, TEM is organized into
multiple parallel streams, each capturing information at different
temporal and spatial scales. Each stream processes input separately,
applying a unique temporal smoothing ﬁlter, and transitions via path
integration (see Whittington et al.46 for details). These streams remain
distinct during learning but integrate during memory retrieval through
attractor dynamics. Lower-index streams encode ﬁner-grained details,
while higher-index streams capture broader structure.
To enable TEM to learn a relational structure that generalizes
across different environments, we trained the model in 16 distinct
11 × 11
grid
environments,
each
with
randomly
generated
45-
dimensional one-hot sensory inputs. At each time step, the agent
could take one of ﬁve possible actions—moving up, down, left, right, or
staying still—with equal probabilities. The results presented in the main
text are based on the model trained for 32,000 iterations, at which
point the loss and performance in predicting next sensory observa-
tions began to plateau (Supplementary Fig. 21). Additional analyses
using models trained for 42,000 and 50,000 iterations showed con-
sistent results (Supplementary Fig. 22 and Supplementary Tables 3–6),
conﬁrming the robustness of our ﬁndings.
Creating the TEM environment for emotion concepts
We ﬁrst calculated the Pearson correlations of time series of ratings
between each pair of emotion categories concatenated across all 14
ﬁlms. Next, we computed the dissimilarity between pairs of emotion
categories using the Pearson correlation (i.e., 1 – r) and performed
metric multidimensional scaling103 (MDS) on the dissimilarity matrix.
The resulting two-dimensional MDS space was discretized into 121
locations, forming an 11 × 11 grid, to match the environments used
during training. Each emotion category was assigned to the location
closest to its MDS coordinate. If two emotion categories occupied a
single location, one was assigned to the nearest available, unoccupied
location.
To ensure that the MDS solution accurately reﬂected the (dis)
similarities between emotion categories as indicated by the ratings, we
repeated the process 500 times using different random seeds for the
MDS procedure. We selected the seed that resulted in the lowest
Spearman correlation between the city-block distances between
category pairs in the environment (which required the minimum
number of time steps to transition from one category to another) and
the Pearson correlations derived from the ratings.
As in the training environment, the agent in the emotion envir-
onment could take one of ﬁve actions—up, down, left, right, or staying
in the same location—each with equal probability. To ensure that each
emotion category had a unique sensory input, we randomly assigned a
distinct 45-dimensional one-hot code to each emotion category. For
locations without an associated emotion category, we assigned ran-
dom 45-dimensional one-hot codes that did not overlap with those of
the emotion categories.
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
9


## Page 10

Simulating emotional experience with TEM
With trained TEM model weights, the agent walked randomly in the
environment created for emotion concepts for 12,100 steps, roughly
sampling each of the 121 locations 100 times. For each emotion cate-
gory, we calculated the average activations of all units in p and g across
the second half of the steps to ensure that the agent had enough
experience to develop a stable representation of the new environment
it had never encountered during training. To generate a time series of
responses to emotion concepts throughout the ﬁlms, we computed
the weighted average activation across all categories, as we assume
that multiple emotion concepts can be coactivated during ﬁlm view-
ing. Speciﬁcally, we weighted the activations of units in layers p and g
based on emotion ratings at each time point, such that segments rated
more highly on certain emotions resulted in stronger activations for
those concepts, while minimizing contributions from unrelated
emotions.
Computing trajectories of emotional experiences in a two-
dimensional affective space
To derive a time series of locations in a low-dimensional affective
space, we projected the time series of category ratings into the same
MDS space that was used to construct the TEM environment. For each
ﬁlm, we multiplied the timepoint-by-category rating matrix with the
category coordinates estimated from the MDS solution. The resulting
time series of the two MDS coordinates were used as the outcome
variables in subsequent decoding analysis.
Multivariate decoding of BOLD signals
We speciﬁed partial least squares (PLS) regression models (SIMPLS
algorithm104) with 20 components separately for decoding patterns of
BOLD signal to predict emotion category ratings, valence-arousal rat-
ings, trajectories in affective space, and activation in different layers of
TEM (Supplementary Fig. 2). Fitting separate models for different
outcome variables simpliﬁes the interpretation of model performance,
because the different outcome blocks (e.g., category ratings and
valence-arousal ratings) are correlated and could inﬂuence the esti-
mation of betas for different outcome variables105,106. For all models,
the predictor block consisted of an ntimepoint× kvoxel dimensional
matrix of BOLD signal (n = 9,538 timepoints; phippocampus = 1,816 voxels,
kentorhinal cortex = 711 voxels, pvmPFC = 5,597 voxels). Outcome blocks
consisted of ntimepoint× kitem matrix of ratings (p = 13 category ratings
or p = 4 dimensional ratings), a ntimepoint× kdimension matrix of affective
space (p = 2 dimensions), or a ntimepoint× kunit matrix of TEM activity
(pp = 400 units, kg = 120 units). To align with BOLD sampling, time
series of the outcomes (ratings and TEM activity) were resampled to
match the sampling rate of BOLD data (i.e., 1/1.3 Hz) and convolved
with a canonical double gamma response function to account for
hemodynamic delay107. For each of the three regions of interest, we
therefore developed ﬁve models (category, affective space, valence-
arousal, p, and g). To test the granularity of emotion concepts and the
scale of p represented along the hippocampal long axis, we addition-
ally speciﬁed separate PLS models separately decoding signals from
the anterior and posterior hippocampus (kanterior
hippocampus = 745
voxels, kposterior hippocampus = 1139 voxels) to predict emotion category,
binarized valence-arousal, small-scale p (kp = 200 units), and large-
scale p (kp = 200 units).
We quantiﬁed decoding performance using leave-one-ﬁlm-out
cross-validation in which PLS regression models were trained on 13
ﬁlms and tested on the left-out ﬁlm.The predicted outcome time series
in the test fold were correlated with the observed time series of the
outcomes, and performance was calculated as the average correlation
across the 14 validation sets (ﬁlms) for each participant. To test whe-
ther self-report ratings predicted from BOLD signal were partially
explained by the decoded TEM activity, we used the time series of
decoded TEM activity to predict the ratings using PLS. We then
performed a partial correlation analysis between the decoded ratings
and the actual ratings, while controlling for the ratings predicted by
the decoded TEM activity.
Characterizing the representational geometry of emotion con-
cepts in the hippocampus
To assess the hierarchical organization of emotion concepts in hip-
pocampal representations, we computed the similarity between pre-
dicted rating time series for each pair of emotion categories using the
Pearson correlation coefﬁcient. We then applied agglomerative hier-
archical clustering using the average linkage method to the dissim-
ilarity matrix (1 – Pearson correlation). This procedure was repeated
for each participant, and the resulting dendrograms were used to
visualize the hierarchical relationships among emotion concepts.
To examine whether a shared conceptual similarity structure was
present across participants and whether it could be explained by
valence, we implemented a leave-one-participant-out analysis. For
each iteration, we averaged the pairwise category correlations across
all participants except the one held out, creating a group-level model
of similarity between emotion concepts. Two group-level models were
deﬁned: a full model consisting of the mean correlation for each pair of
the 13 categories, and a valence model, in which category pairs were
grouped
by
valence
(positive–positive,
negative–negative,
and
positive–negative) and averaged within each group. We assessed
model ﬁt by computing Spearman rank correlations between the held-
out participant’s pairwise category correlation matrix and each group-
level model. To test whether the full model explained variance in the
participant’s similarity structure beyond what could be attributed to
valence, we regressed out the ranked values of the valence model from
the participant’s category correlations and then computed a Spearman
correlation between the residuals and the full model. Inference on
group-level correlation coefﬁcients was performed using t tests
against zero.
Comparing multivariate decoding performance across
participants
We speciﬁed multiple linear mixed-effects models to compare
decoding performance across models trained for different objectives
(e.g., for categorical and dimensional self-report items) and using data
from different regions (e.g., hippocampal and entorhinal regions of
interest).
Comparing the decoding performance of self-report ratings. We
speciﬁed a linear mixed-effects model to analyze decoding perfor-
mance of self-reported ratings (i.e., Fisher z-transformed prediction-
outcome correlation) as a function of rating item (including both
category and valence-arousal), region, and their interaction as ﬁxed
effects. Random intercepts were included for participants nested
within rating items and regions. To compare the decoding perfor-
mance of category versus valence-arousal in the hippocampus, we
contrasted the estimated marginal means of the hippocampus by
taking the average of 13 category items and subtracting the average of
the four valence-arousal items, while setting other regions to zero. To
compare how the decoding performance of valence-arousal in the
hippocampus differed from that in the entorhinal cortex and vmPFC,
we contrasted the average estimated marginal means of the four
valence-arousal items in the entorhinal cortex and vmPFC against that
of the hippocampus ((entorhinal cortex + vmPFC)/2 – hippocampus)
for valence-arousal items only, while setting category items to zero. To
compare how the difference in rating type (emotion category vs.
valence-arousal dimension) varied across brain regions, we tested the
interaction between rating type and region (hippocampus - entorhinal
cortex or hippocampus - vmPFC).
To compare decoding performance between emotion category
and binarized valence-arousal items in the anterior and posterior
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
10


## Page 11

hippocampus, we speciﬁed a linear mixed-effects model with rating
item, hippocampal portion, and their interaction as ﬁxed effects, and
random intercepts for participants nested within rating items and
hippocampal portions. We contrasted the estimated marginal means
for emotion type and hippocampal portion. For the factor emotion, we
subtracted the average of the four binarized valence-arousal items
from the average of the 13 category items. For the factor hippocampal
portion, we subtracted performance in the anterior hippocampus
from that of the posterior hippocampus. We tested the interaction
between these two factors to determine whether the difference in
hippocampal portions (posterior - anterior) varied across emotion
types/granularities (category - binarized valence-arousal).
Comparing the decoding performance of TEM activity. We speciﬁed
a linear mixed-effects model to analyze decoding performance of TEM
activity as a function of brain region, TEM layer, scale, and their
interactions as ﬁxed effects. Random intercepts were included for
participants nested within regions, TEM layers and scales. In these
models, we averaged decoding performance across units for each
combination of brain region, TEM layer and scale with participants.
This approach simpliﬁed the models and ensured a more appropriate
estimation of degrees of freedom.
To compare the decoding performance of the p and g layers of
TEM in the hippocampus, we contrasted the estimated marginal means
of the hippocampus by taking the average of all the scales of p and
subtracting the average of all the scales of g, while setting other
regions to zero. To examine trends in decoding performance across
different scales (0 through 4), we speciﬁed a linear contrast on the
estimated marginal means, assigning weights from -2 to 2 to represent
the change in performance from small to large scales. This contrast
was performed separately for each combination of brain region and
TEM layer. We then conducted pairwise comparisons to assess the
differences in the estimated marginal means of the linear contrast on
scale between each pair of regions separately for each TEM layer and
between each pair of TEM layers separately for each region.
To compare the performance of models trained to predict the
activity of small- and large-scale units in layer p of TEM from signals in
the anterior and posterior hippocampus, we speciﬁed a linear mixed-
effects model with representational scale, hippocampal portion, and
their interaction as ﬁxed effects, with random intercepts for partici-
pants nested within scale and hippocampal portion. We contrasted the
estimated marginal means for the factors scale and hippocampal
portion. For the factor scale, we subtracted the average of the three
large scales (i.e., 2, 3, 4) from the average of the two small scales (i.e., 0,
1). For the factor hippocampal portion, we subtracted decoding per-
formance in the anterior hippocampus from that of the posterior
hippocampus. We tested the interaction between these two factors to
determine whether the difference in decoding performance between
hippocampal portions (posterior - anterior) varied across scales (small
- large).
To compare the correlation between BOLD-predicted and
observed self-report ratings after controlling for TEM p in the hippo-
campus, we speciﬁed a linear mixed-effects model with rating item,
correlation type (correlation vs. partial correlation controlling for TEM
p), and their interaction as ﬁxed effects, with random intercepts for
participants nested within rating items and correlation types. We
contrasted the estimated marginal means for the factors correlation
type and hippocampal portion. For the factor correlation type, we
subtracted the average of the partial correlations from the average of
the correlations. For the factor emotion, we subtracted the average of
the four valence-arousal items from the average of the 13 category
items. We tested the interaction between these two factors to deter-
mine whether the difference in correlation type (correlation - partial
correlation) varied across emotion types (category - valence-arousal).
We assessed the statistical signiﬁcance of all effects of interest
using a nonparametric permutation test based on sign ﬂipping108.
Speciﬁcally, for each permutation, we randomly ﬂipped the sign of all
data within each participant, thereby preserving the within-participant
correlation structure while assuming exchangeability of participants
under the null hypothesis. This procedure maintains the dependency
across repeated measures for each participant (e.g., brain regions,
emotion ratings, TEM layers, TEM scales) and permits inference at the
group level. For each randomized dataset, we reﬁt the linear mixed-
effects model and extracted estimates of interest. The randomization
null distribution was constructed from 10,000 permutations, and two-
sided p-values were computed as the proportion of permuted esti-
mates that were more extreme than the observed estimate. We addi-
tionally performed parametric bootstrapping to estimate the standard
error of parameter estimates and standardized effect sizes with 10,000
bootstrap
samples109.
For
each
sample,
synthetic
observations
were generated based on the parameter estimates of the ﬁtted
model, and the mixed effects model was re-ﬁt, producing a distribu-
tion of estimates use to derive 95% conﬁdence intervals using the
percentile method110. We also calculated a standardized effect size by
dividing the observed contrast by the standard deviation of the
bootstrap
distribution,
multiplied
by
the
square
root
of
the
sample size.
All analyses were performed using CanlabCore Tools (https://
github.com/canlab/CanlabCore) and SPM 12, as well as custom
MATLAB (R2024a), Python (3.10.14) and R (4.4.1) code.
Reporting summary
Further information on research design is available in the Nature
Portfolio Reporting Summary linked to this article.
Data availability
The fMRI data are available on OpenNeuro111 (https://doi.org/10.18112/
openneuro.ds004892.v1.0.0). The emotion rating data are available on
OpenNeuro112 (https://doi.org/10.18112/openneuro.ds004872.v1.0.1).
Code availability
Code
for
all
analyses
is
available
at
https://github.com/ecco-
laboratory/EmotionConceptRepresentation113
and
archived
on
Zenodo (https://doi.org/10.5281/zenodo.17856746). Code for training
the TEM is adapted from https://github.com/jbakermans/torch_tem.
The MATLAB interface used for creating TEM environments is available
at https://github.com/jbakermans/WorldBuilder.
References
1.
Russell, J. A. A circumplex model of affect. J. Pers. Soc. Psychol.
39, 1161–1178 (1980).
2.
Yik, M., Russell, J. A. & Steiger, J. H. A 12-Point circumplex structure
of core affect. Emotion 11, 705–731 (2011).
3.
Barrett, L. F. & Bliss-Moreau, E. Affect as a psychological primitive.
Adv. Exp. Soc. Psychol. 41, 167–218 (2009).
4.
Remington, N. A., Fabrigar, L. R. & Visser, P. S. Reexamining the
circumplex model of affect. J. Pers. Soc. Psychol. 79, 286–300
(2000).
5.
Barrett, L. F. & Fossum, T. Mental representations of affect
knowledge. Cogn. Emot. 15, 333–363 (2001).
6.
Heffner, J. & FeldmanHall, O. A probabilistic map of emotional
experiences during competitive social interactions. Nat. Commun.
13, 1718 (2022).
7.
Schlosberg, H. The description of facial expressions in terms of
two dimensions. J. Exp. Psychol. 44, 229–237 (1952).
8.
Thornton, M. A. & Tamir, D. I. Mental models accurately predict
emotion transitions. Proc. Natl. Acad. Sci. USA 114, 5982–5987
(2017).
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
11


## Page 12

9.
Feldman, L. A. Valence focus and arousal focus: Individual dif-
ferences in the structure of affective experience. J. Pers. Soc.
Psychol. 69, 153–166 (1995).
10.
Mobbs, D., Headley, D. B., Ding, W. & Dayan, P. Space, time, and
fear: Survival computations along defensive circuits. Trends Cogn.
Sci. 24, 228–241 (2020).
11.
Heffner, J., Son, J.-Y. & FeldmanHall, O. Emotion prediction errors
guide socially adaptive behaviour. Nat. Hum. Behav. 5,
1391–1401 (2021).
12.
Berridge, K. C. & Kringelbach, M. L. Pleasure systems in the brain.
Neuron 86, 646–664 (2015).
13.
Burgos-Robles, A. et al. Amygdala inputs to prefrontal cortex
guide behavior amid conﬂicting cues of reward and punishment.
Nat. Neurosci. 20, 824–835 (2017).
14.
Aston-Jones, G. & Cohen, J. D. An integrative theory of locus
coeruleus-norepinephrine function: adaptive gain and optimal
performance. Annu. Rev. Neurosci. 28, 403–450 (2005).
15.
Carter, M. E., de Lecea, L. & Adamantidis, A. Functional wiring of
hypocretin and LC-NE neurons: implications for arousal. Front.
Behav. Neurosci. 7, 43 (2013).
16.
Satpute, A. B., Kragel, P. A., Barrett, L. F., Wager, T. D. & Bianciardi,
M. Deconstructing arousal into wakeful, autonomic and affective
varieties. Neurosci. Lett. 693, 19–28 (2019).
17.
Kragel, P. A., Treadway, M. T., Admon, R., Pizzagalli, D. A. & Hahn,
E. C. A mesocorticolimbic signature of pleasure in the human
brain. Nat. Hum. Behav. 7, 1332–1343 (2023).
18.
Čeko, M., Kragel, P. A., Woo, C.-W., López-Solà, M. & Wager, T. D.
Common and stimulus-type-speciﬁc brain representations of
negative affect. Nat. Neurosci. 25, 760–770 (2022).
19.
Chang, C. et al. Tracking brain arousal ﬂuctuations with fMRI. Proc.
Natl. Acad. Sci. USA 113, 4518–4523 (2016).
20.
Lloyd, B., de Voogd, L. D., Mäki-Marttunen, V. & Nieuwenhuis, S.
Pupil size reﬂects activation of subcortical ascending arousal
system nuclei during rest. Elife 12, e84822 (2023).
21.
Eisenbarth, H., Chang, L. J. & Wager, T. D. Multivariate brain pre-
diction of heart rate and skin conductance responses to social
threat. J. Neurosci. 36, 11987–11998 (2016).
22.
Kragel, P. A. & LaBar, K. S. Multivariate neural biomarkers of
emotional states are categorically distinct. Soc. Cogn. Affect.
Neurosci. 10, 1437–1448 (2015).
23.
Saarimäki, H. et al. Discrete neural signatures of basic emotions.
Cerebral Cortex 26, 2563–2573 (2016).
24.
Camacho, M. C. et al. Large-scale encoding of emotion concepts
becomes increasingly similar between individuals from childhood
to adolescence. Nat. Neurosci. 26, 1256–1266 (2023).
25.
Kragel, P. A., Reddan, M. C., LaBar, K. S. & Wager, T. D. Emotion
schemas are embedded in the human visual system. Sci. Adv. 5,
eaaw4358 (2019).
26.
Wang, Y., Kragel, P. A. & Satpute, A. B. Neural predictors of fear
depend on the situation. J. Neurosci. 44, e0142232024 (2024).
27.
Horikawa, T., Cowen, A. S., Keltner, D. & Kamitani, Y. The neural
representation of visually evoked emotion is high-dimensional,
categorical, and distributed across transmodal brain regions.
iScience 23, 101060 (2020).
28.
Abdel-Ghaffar, S. A. et al. Occipital-temporal cortical tuning to
semantic and affective features of natural images predicts asso-
ciated behavioral responses. Nat. Commun. 15, 5531 (2024).
29.
Skerry, A. E. & Saxe, R. Neural representations of emotion are
organized around abstract event features. Curr. Biol. 25,
1945–1954 (2015).
30.
Skerry, A. E. & Saxe, R. A common neural code for perceived and
inferred emotion. J. Neurosci. 34, 15997–16008 (2014).
31.
O’Keefe, J. & Nadel, L. The Hippocampus as a Cognitive Map.
(Oxford University Press, London, England, 1978).
32.
Bird, C. M. & Burgess, N. The hippocampus and memory: insights
from spatial processing. Nat. Rev. Neurosci. 9, 182–194 (2008).
33.
Papez, J. W. A proposed mechanism of emotion. 1937. J. Neu-
ropsychiatry Clin. Neurosci. 7, 103–112 (1995).
34.
Maclean, P. D. Psychosomatic disease and the “visceral brain.
Psychosom. Med. 11, 338–353 (1949).
35.
Gray, J. A. & McNaughton, N. Neuropsychology of Anxiety. (Oxford
University Press, London, England, 2000).
36.
Constantinescu, A. O., O’Reilly, J. X. & Behrens, T. E. J. Organizing
conceptual knowledge in humans with a gridlike code. Science
352, 1464–1468 (2016).
37.
Park, S. A., Miller, D. S. & Boorman, E. D. Inferences on a multi-
dimensional social hierarchy use a grid-like code. Nat. Neurosci.
24, 1292–1301 (2021).
38.
Viganò, S., Bayramova, R., Doeller, C. F. & Bottini, R. Mental search
of concepts is supported by egocentric vector representations
and restructured grid maps. Nat. Commun. 14, 8132 (2023).
39.
Viganò, S., Rubino, V., Soccio, A. D., Buiatti, M. & Piazza, M. Grid-
like and distance codes for representing word meaning in the
human brain. Neuroimage 232, 117876 (2021).
40.
Nitsch, A., Garvert, M. M., Bellmund, J. L. S., Schuck, N. W. &
Doeller, C. F. Grid-like entorhinal representation of an abstract
value space during prospective decision making. Nat. Commun.
15, 1198 (2024).
41.
Manns, J. R. & Eichenbaum, H. Evolution of declarative memory.
Hippocampus 16, 795–808 (2006).
42.
Hafting, T., Fyhn, M., Molden, S., Moser, M.-B. & Moser, E. I.
Microstructure of a spatial map in the entorhinal cortex. Nature
436, 801–806 (2005).
43.
Ma, Y., Vafaie, N. & Kragel, P. A. Embedding emotion concepts in
cognitive maps. Neurosci. Biobehav. Rev. 172, 106089 (2025).
44.
Qasim, S. E., Reinacher, P. C., Brandt, A., Schulze-Bonhage, A. &
Kunz, L. Neurons in the human entorhinal cortex map abstract
emotion space. Preprint at https://doi.org/10.1101/2023.08.10.
552884 (2023).
45.
Morgenroth, E. et al. Emo-FilM: A multimodal dataset for affective
neuroscience using naturalistic stimuli. Sci. Data 12, 684 (2025).
46.
Whittington, J. C. R. et al. The Tolman-Eichenbaum machine:
Unifying space and relational memory through generalization in
the hippocampal formation. Cell 183, 1249–1263 (2020).
47.
Schapiro, A. C., Kustner, L. V. & Turk-Browne, N. B. Shaping of
object representations in the human medial temporal lobe based
on temporal regularities. Curr. Biol. 22, 1622–1627 (2012).
48.
Deuker, L., Bellmund, J. L. S., Navarro Schröder, T. & Doeller, C. F.
An event map of memory space in the hippocampus. Elife 5,
https://doi.org/10.7554/elife.16534 (2016).
49.
Hsieh, L.-T., Gruber, M. J., Jenkins, L. J. & Ranganath, C. Hippo-
campal activity patterns carry information about objects in tem-
poral context. Neuron 81, 1165–1178 (2014).
50.
Schimmack, U. & Reisenzein, R. Cognitive processes involved in
similarity judgments of emotions. J. Pers. Soc. Psychol. 73,
645–661 (1997).
51.
Shaver, P., Schwartz, J., Kirson, D. & O’Connor, C. Emotion
knowledge: further exploration of a prototype approach. J. Pers.
Soc. Psychol. 52, 1061–1086 (1987).
52.
Fanselow, M. S. & Dong, H.-W. Are the dorsal and ventral hippo-
campus functionally distinct structures? Neuron 65, 7–19
(2010).
53.
Vogel, J. W. et al. A molecular gradient along the longitudinal axis
of the human hippocampus informs large-scale behavioral sys-
tems. Nat. Commun. 11, 960 (2020).
54.
Liu, J. et al. Multi-scale goal distance representations in human
hippocampus during virtual spatial navigation. Curr. Biol. 33,
2024–2033.e3 (2023).
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
12


## Page 13

55.
Komorowski, R. W. et al. Ventral hippocampal neurons are shaped
by experience to represent behaviorally relevant contexts. J.
Neurosci. 33, 8079–8087 (2013).
56.
Collin, S. H. P., Milivojevic, B. & Doeller, C. F. Memory hierarchies
map onto the hippocampal long axis in humans. Nat. Neurosci. 18,
1562–1564 (2015).
57.
Kumaran, D., Melo, H. L. & Duzel, E. The emergence and repre-
sentation of knowledge about social and nonsocial hierarchies.
Neuron 76, 653–666 (2012).
58.
Park, S. A., Miller, D. S., Nili, H., Ranganath, C. & Boorman, E. D.
Map making: Constructing, combining, and inferring on abstract
cognitive maps. Neuron 107, 1226–1238.e8 (2020).
59.
Dolcos, F., LaBar, K. S. & Cabeza, R. Dissociable effects of arousal
and valence on prefrontal activity indexing emotional evaluation
and subsequent memory: an event-related fMRI study. Neuro-
image 23, 64–74 (2004).
60.
Lewis, P., Critchley, H., Rotshtein, P. & Dolan, R. Neural correlates
of processing valence and arousal in affective words. Cereb.
Cortex 17, 742–748 (2006).
61.
Anderson, A. K. et al. Dissociated neural representations of
intensity and valence in human olfaction. Nat. Neurosci. 6,
196–202 (2003).
62.
Hamann, S. B., Ely, T. D., Grafton, S. T. & Kilts, C. D. Amygdala
activity related to enhanced memory for pleasant and aversive
stimuli. Nat. Neurosci. 2, 289–293 (1999).
63.
Kim, M. J. et al. Human amygdala tracks a feature-based valence
signal embedded within the facial expression of surprise. J. Neu-
rosci. 37, 9510–9518 (2017).
64.
Eichenbaum, H. & Cohen, N. J. Can we reconcile the declarative
memory and spatial navigation views on hippocampal function?
Neuron 83, 764–770 (2014).
65.
Behrens, T. E. J. et al. What is a cognitive map? organizing
knowledge for ﬂexible behavior. Neuron 100, 490–509 (2018).
66.
Kjelstrup, K. B. et al. Finite scale of spatial representation in the
hippocampus. Science 321, 140–143 (2008).
67.
Jung, M. W., Wiener, S. I. & McNaughton, B. L. Comparison of
spatial ﬁring characteristics of units in dorsal and ventral hippo-
campus of the rat. J. Neurosci. 14, 7347–7356 (1994).
68.
Doeller, C. F., Barry, C. & Burgess, N. Evidence for grid cells in a
human memory network. Nature 463, 657–661 (2010).
69.
Howard, L. R. et al. The hippocampus and entorhinal cortex
encode the path and Euclidean distances to goals during navi-
gation. Curr. Biol. 24, 1331–1340 (2014).
70.
Tolman, E. C. Cognitive maps in rats and men. Psychol. Rev. 55,
189–208 (1948).
71.
Tavares, R. M. et al. A map for social navigation in the human brain.
Neuron 87, 231–243 (2015).
72.
Lindquist, K. A., Wager, T. D., Kober, H., Bliss-Moreau, E. & Barrett,
L. F. The brain basis of emotion: a meta-analytic review. Behav.
Brain Sci. 35, 121–143 (2012).
73.
Satpute, A. B. & Lindquist, K. A. The default mode network’s role in
discrete emotion. Trends Cogn. Sci. 23, 851–864 (2019).
74.
Barrett, L. F. Solving the emotion paradox: categorization and the
experience of emotion. Pers. Soc. Psychol. Rev. 10, 20–46 (2006).
75.
Olman, C. A., Davachi, L. & Inati, S. Distortion and signal loss in
medial temporal lobe. PLoS ONE 4, e8160 (2009).
76.
Murray, J. D. et al. A hierarchy of intrinsic timescales across pri-
mate cortex. Nat. Neurosci. 17, 1661–1663 (2014).
77.
Hasson, U., Chen, J. & Honey, C. J. Hierarchical process memory:
memory as an integral component of information processing.
Trends Cogn. Sci. 19, 304–313 (2015).
78.
Bao, X. et al. Grid-like neural representations support olfactory
navigation of a two-dimensional odor space. Neuron 102,
1066–1075 (2019).
79.
Grabenhorst, F. & Rolls, E. T. Value, pleasure and choice in the
ventral prefrontal cortex. Trends Cogn. Sci. 15, 56–67 (2011).
80.
Lockwood, P. L. et al. Human ventromedial prefrontal cortex is
necessary for prosocial motivation. Nat. Hum. Behav. 8,
1403–1416 (2024).
81.
Kaplan, R., Schuck, N. W. & Doeller, C. F. The role of mental maps
in decision-making. Trends Neurosci. 40, 256–259 (2017).
82.
Ekman, P. Basic Emotions. in Handbook of Cognition and Emotion
45–60 (John Wiley & Sons, Ltd, Chichester, UK, 2005).
83.
Quiroga, R. Q. Concept cells: the building blocks of declarative
memory functions. Nat. Rev. Neurosci. 13, 587–597 (2012).
84.
Rey, H. G. et al. Single neuron coding of identity in the human
hippocampal formation. Curr. Biol. 30, 1152–1159 (2020).
85.
Fontaine, J. R. J., Scherer, K. R., Roesch, E. B. & Ellsworth, P. C. The
world of emotions is not two-dimensional. Psychol. Sci. 18,
1050–1057 (2007).
86.
Cowen, A., Sauter, D., Tracy, J. L. & Keltner, D. Mapping the pas-
sions: Toward a high-dimensional taxonomy of emotional experi-
ence and expression. Psychol. Sci. Public Interest 20,
69–90 (2019).
87.
Burgess, N. & O’Keefe, J. Models of place and grid cell ﬁring and
theta rhythmicity. Curr. Opin. Neurobiol. 21, 734–744 (2011).
88.
Lisman, J. E. & Jensen, O. The θ-γ neural code. Neuron 77,
1002–1016 (2013).
89.
Wen, J. H., Sorscher, B., Aery Jones, E. A., Ganguli, S. & Giocomo,
L. M. One-shot entorhinal maps enable ﬂexible navigation in novel
environments. Nature 635, 943–950 (2024).
90.
Zutshi, I. et al. Hippocampal neuronal activity is aligned with
action plans. Nature 639, 153–161 (2025).
91.
Qasim, S. E., Fried, I. & Jacobs, J. Phase precession in the human
hippocampus and entorhinal cortex. Cell 184,
3242–3255.e10 (2021).
92.
Stachenfeld, K. L., Botvinick, M. M. & Gershman, S. J. The hippo-
campus as a predictive map. Nat. Neurosci. 20, 1643–1653 (2017).
93.
Viard, A., Doeller, C. F., Hartley, T., Bird, C. M. & Burgess, N.
Anterior hippocampus and goal-directed spatial decision making.
J. Neurosci. 31, 4613–4621 (2011).
94.
Strange, B. A., Witter, M. P., Lein, E. S. & Moser, E. I. Functional
organization of the hippocampal longitudinal axis. Nat. Rev. Neu-
rosci. 15, 655–669 (2014).
95.
Gazit, T. et al. The role of mPFC and MTL neurons in human choice
under goal-conﬂict. Nat. Commun. 11, 3192 (2020).
96.
Posner, J., Russell, J. A. & Peterson, B. S. The circumplex model of
affect: an integrative approach to affective neuroscience, cogni-
tive development, and psychopathology. Dev. Psychopathol. 17,
715–734 (2005).
97.
Brainard, D. H. The Psychophysics Toolbox. Spat. Vis. 10,
433–436 (1997).
98.
Morgenroth, E., Somarathna, R., Van De Ville, D., Mohammadi, G. &
Vuilleumier, P. Dissecting appraisal and multicomponential fea-
tures of emotion: Evidence from multilevel annotation during
naturalistic stimulation. Emotion https://doi.org/10.1037/
emo0001619 (2026).
99.
Girard, J. M. CARMA: Software for continuous affect rating and
media annotation. J. Open Res. Softw. 2, https://doi.org/10.5334/
jors.ar (2014).
100. Amunts, K., Mohlberg, H., Bludau, S. & Zilles, K. Julich-Brain: A 3D
probabilistic atlas of the human brain’s cytoarchitecture. Science
369, 988–992 (2020).
101.
Poppenk, J., Evensmoen, H. R., Moscovitch, M. & Nadel, L. Long-
axis specialization of the human hippocampus. Trends Cogn. Sci.
17, 230–240 (2013).
102.
Glasser, M. F. et al. A multi-modal parcellation of human cerebral
cortex. Nature 536, 171–178 (2016).
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
13


## Page 14

103.
Mead, A. Review of the development of multidimensional scaling
methods. Statistician 41, 27 (1992).
104.
de Jong, S. SIMPLS: An alternative approach to partial least
squares regression. Chemometr. Intell. Lab. Syst. 18,
251–263 (1993).
105.
Garthwaite, P. H. An interpretation of partial least squares. J. Am.
Stat. Assoc. 89, 122 (1994).
106.
Westerhuis, J. A., Kourti, T. & MacGregor, J. F. Analysis of multi-
block and hierarchical PCA and PLS models. J. Chemom. 12,
301–321 (1998).
107.
Friston, K. J., Ashburner, J. T., Kiebel, S. J.,Nichols, T. E. & Penny, W.
D. Statistical Parametric Mapping: The Analysis of Functional Brain
Images: The Analysis of Functional Brain Images. (Academic
Press, 2010).
108.
Winkler, A. M., Webster, M. A., Vidaurre, D., Nichols, T. E. & Smith,
S. M. Multi-level block permutation. Neuroimage 123,
253–268 (2015).
109.
Davison, A. C. & Hinkley, D. V. Cambridge Series in Statistical and
Probabilistic Mathematics: Bootstrap Methods and Their Applica-
tion Series Number 1. (Cambridge University Press, Cambridge,
England, 2014).
110.
Hall, P. Theoretical comparison of bootstrap conﬁdence intervals.
Ann. Stat. 16, 927–953 (1988).
111.
Morgenroth, E. et al. Emo-FilM. OpenNeuro. https://doi.org/10.
18112/openneuro.ds004892.v1.0.0 (2024).
112.
Morgenroth, E. et al. Emo-FilM Annotations. OpenNeuro. https://
doi.org/10.18112/openneuro.ds004872.v1.0.1 (2024).
113.
Ma, Y. & Kragel, P. A. Map-like representation of emotion knowl-
edge in the hippocampal-prefrontal systems. Zenodo. https://doi.
org/10.5281/zenodo.17856746 (2025).
114.
Baveye, Y., Dellandrea, E., Chamaret, C. & Chen, L. LIRIS-ACCEDE:
a video database for affective content analysis. IEEE Trans. Affect.
Comput. 6, 43–55 (2015).
Acknowledgements
This work was supported in part by NIH National Institute of Mental
Health R01MH134972 (P.A.K.). We thank Joseph Manns, Peter Hitchcock,
and members of the ECCO lab for discussions and comments on a
previous version of this manuscript.
Author contributions
Y.M. and P.A.K. contributed to designing the research, analyzing the
data, and writing the paper.
Competing interests
The authors declare no competing interests.
Additional information
Supplementary information The online version contains
supplementary material available at
https://doi.org/10.1038/s41467-025-68240-z.
Correspondence and requests for materials should be addressed to
Philip A. Kragel.
Peer review information Nature Communications thanks Raphael
Kaplan and the other anonymous reviewer(s) for their contribution to the
peer review of this work. A peer review ﬁle is available.
Reprints and permissions information is available at
http://www.nature.com/reprints
Publisher’s note Springer Nature remains neutral with regard to jur-
isdictional claims in published maps and institutional afﬁliations.
Open Access This article is licensed under a Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International License,
which permits any non-commercial use, sharing, distribution and
reproduction in any medium or format, as long as you give appropriate
credit to the original author(s) and the source, provide a link to the
Creative Commons licence, and indicate if you modiﬁed the licensed
material. You do not have permission under this licence toshare adapted
material derived from this article or parts of it. The images or other third
party material in this article are included in the article’s Creative
Commons licence, unless indicated otherwise in a credit line to the
material. If material is not included in the article’s Creative Commons
licence and your intended use is not permitted by statutory regulation or
exceeds the permitted use, you will need to obtain permission directly
from the copyright holder. To view a copy of this licence, visit http://
creativecommons.org/licenses/by-nc-nd/4.0/.
© The Author(s) 2026
Article
https://doi.org/10.1038/s41467-025-68240-z
Nature Communications|   (2026) 17:1518 
14


