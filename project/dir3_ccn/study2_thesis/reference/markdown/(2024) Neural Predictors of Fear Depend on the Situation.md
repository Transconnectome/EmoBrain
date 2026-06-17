# (2024) Neural Predictors of Fear Depend on the Situation

**Source:** (2024) Neural Predictors of Fear Depend on the Situation.pdf

---

## Page 1

Behavioral/Cognitive
Neural Predictors of Fear Depend on the Situation
Yiyu Wang,1 Philip A. Kragel,2 and
Ajay B. Satpute1,3
1Department of Psychology, Northeastern University, Boston, Massachusetts 02115, 2Department of Psychology, Emory University, Atlanta, Georgia
30322, and 3Department of Radiology, Athinoula A. Martinos Center for Biomedical Imaging, Massachusetts General Hospital and Harvard Medical
School, Charlestown, Massachusetts 02129
The extent to which neural representations of fear experience depend on or generalize across the situational context has remained
unclear. We systematically manipulated variation within and across three distinct fear-evocative situations including fear of heights,
spiders, and social threats. Participants (n = 21; 10 females and 11 males) viewed ∼20 s clips depicting spiders, heights, or social
encounters and rated fear after each video. Searchlight multivoxel pattern analysis was used to identify whether and which brain
regions carry information that predicts fear experience and the degree to which the fear-predictive neural codes in these areas
depend on or generalize across the situations. The overwhelming majority of brain regions carrying information about fear did
so in a situation-dependent manner. These ﬁndings suggest that local neural representations of fear experience are unlikely to
involve a singular pattern but rather a collection of multiple heterogeneous brain states.
Key words: emotion; fear; fMRI; multivariate pattern analysis; subjective experience
Signiﬁcance Statement
Much of the debate on the nature of emotion concerns the uniformity or heterogeneity of representation for particular
emotion categories. Here we provide evidence that widely distributed activation patterns characteristic of recent neural
signatures of fear reﬂect an amalgam of functionally heterogeneous brain states. Participants completed a novel fMRI task
that parametrically examined subjective fear within and across three content-rich and naturalistic situations: fear of heights,
spiders, and social threats. Using searchlight analysis and machine learning methods, we show that the overwhelming majority of
brain regions that predict fear only do so for certain situations. These ﬁndings carry implications for the generalization of ﬁndings
on fear across species, translational models of fear and anxiety, and developing neural signatures of fear.
Introduction
For over a century, philosophers, psychologists, and neuroscien-
tists have debated the nature of emotions (Dalgleish et al., 2009;
Gendron and Feldman Barrett, 2009; Barrett and Satpute, 2019).
Much of this debate concerns the uniformity or heterogeneity of
representation for particular emotion categories (Lindquist et al.,
2013; Mobbs et al., 2019). For example, is there a particular brain
state that underlies fearful experiences (Vytal and Hamann, 2010;
Celeghin et al., 2017; Nummenmaa and Saarimäki, 2019), or does
fear involve a collection of heterogeneous brain states (Wilson-
Mendenhall et al., 2011; Satpute and Lindquist, 2019; Doyle et
al., 2022)? Addressing this question has broad implications for
translational neuroscience models of mood and anxiety disorders
(LeDoux and Pine, 2016; Fanselow and Pennington, 2017).
Recent functional magnetic resonance imaging (fMRI) studies
have searched for the “brain signatures” of emotion categories
(Kassam et al., 2013; Kragel and LaBar, 2015, 2016; Saarimäki
et al., 2016, 2018). Brain signatures (sometimes called “neuro-
markers” or “neural signatures”) are a type of multivoxel pattern
analysis (MVPA) that uses brain data to predict behavior (Kragel
et al., 2018). Brain signatures of emotion draw on information
that is widely distributed throughout cortical and subcortical
areas. However, whether this information is organized into a sin-
gle prototypical pattern, or reﬂects an amalgam of heterogeneous
functional states, remains unclear because neural signatures do
not inherently provide direct insight about neural representation
(Kragel et al., 2018; Lindquist et al., 2022). Classiﬁcation is
possible even if none of the individual brain regions carry
category-level representations of emotion (for details, see
Clark-Polner et al., 2017; Kragel et al., 2018; Azari et al., 2020;
Lindquist et al., 2022).
Some ﬁndings suggest there is functional heterogeneity in the
neural representation of fear. Univariate fMRI studies have found
that distinct sets of brain regions are engaged depending on the
Received Jan. 23, 2023; revised July 9, 2024; accepted Sept. 9, 2024.
Author contributions: A.B.S. designed research; Y.W. and A.B.S. performed research; Y.W., P.A.K., and A.B.S.
contributed unpublished reagents/analytic tools; Y.W. analyzed data; Y.W. and A.B.S. wrote the paper.
Research reported in this publication was supported by the National Science Foundation Division of Graduate
Education (NCS 1835309).
The authors declare no competing ﬁnancial interest.
Correspondence should be addressed to Yiyu Wang at wang.yiyu@northeastern.edu or Ajay Satpute at
a.satpute@northeastern.edu.
https://doi.org/10.1523/JNEUROSCI.0142-23.2024
Copyright © 2024 the authors
1–8 • The Journal of Neuroscience, November 13, 2024 • 44(46):e0142232024


## Page 2

fear-evocative content (e.g., pictures of spiders, blood, social
encounters;
Caseras
et
al.,
2010;
Lueken
et
al.,
2011;
Michalowski et al., 2017). However, two limitations to this
work preclude a clear conclusion. First, these studies either com-
pared categories of stimuli with distinct semantic content (e.g.,
stereotypically fearful stimuli, e.g., spiders or snakes, vs “neutral”
stimuli, e.g., ordinary objects), participant groups (phobic vs
nonphobic; Caseras et al., 2010), or both (Lueken et al., 2011;
Michalowski et al., 2017). Accordingly, observed diﬀerences
may be due to the semantic content of the stimuli or between
individuals that are unrelated to fear. Second, these studies
focused on activation magnitude, yet patterns of activation
may carry information about psychological states irrespective
of diﬀerences in activation magnitude.
Here, we tested the extent to which functional activity
throughout the brain predicts fear in a situation-general or
situation-dependent manner. Participants viewed ∼20 s clips
depicting spiders, heights, or social encounters and rated fear
after each video. We selected these situations because they span
a wide variety of properties. For instance, while fear is often stud-
ied in a predator–prey context, fear of heights is potent and yet
does not involve a predator. Critically, video stimuli were also
curated to evoke a wide range of fear within each situation
(Fig. 1). This design enabled us to systematically examine the neural
predictors of fear within and across each situation. We used search-
light MVPA (Kriegeskorte et al., 2006) with least absolute shrinkage
and selection operator (LASSO)-PCR (Tibshirani, 1996; Wager
et al., 2011; Chang et al., 2015) to identify brain regions with
functional information that predicts fear ratings. A brain region
may carry fear-predictive information that generalizes across all
situations using the same “neural codes” (i.e., shared model
parameters) or using diﬀerent neural codes (i.e., unshared model
parameters). Thus, we trained our models in two distinct ways to
test these possibilities. Our ﬁndings suggest that, regardless of the
training approach, functional activity that predicts fear is widely
distributed throughout the brain and largely dependent on the
fear-evocative context.
Materials and Methods
Participants. Neurotypical participants who reported no clinical psy-
chiatric diagnosis were recruited from the Greater Los Angeles area.
Exclusion criteria consisted of claustrophobia, psychiatric medication,
left-handedness, metal in the body, and age (under 18 years or over
55 years). After excluding three individuals with excessive motion (crite-
ria described below), the sample included 21 participants (11 male; 10
female; ages 22–40 years; mean age, 30.4).
Stimuli. Thirty-six silent videos were used in the experiment (12 vid-
eos per situation; duration, 18–22 s/video). While silent videos might be
less evocative, they provide a more conservative test of the situation-
dependent hypothesis since it has already been shown that neural
responses during aﬀective experiences are modality dependent. For eco-
logical validity, all videos depicted naturalistic footage and were shot
from an immersive ﬁrst-person perspective. Videos were selected to be
relatively stable (i.e., did not involve dramatic changes or “jump scares”)
to mitigate motion artifacts and maintain the consistency of psycholog-
ical experience across the duration. Video stimuli were obtained and
normed in an independent online sample (Extended Data Stimulus
Norms). Stimuli were curated to elicit a wide range of variation in
self-reported fear across three distinct situations such that models could
be estimated to predict fear within each situation (Fig. 1). In the heights
condition,
for
example,
a
normatively
high-fear
video
depicts
ﬁrst-person footage of walking along the edge of a sheer cliﬀ, whereas
a normatively low-fear video depicts ﬁrst-person footage of walking
downstairs. While norms were used to select stimuli for inclusion,
analyses were conducted using subjective reports. A short description
of the content and the normative ratings from the independent online
sample for each video are available online: https://github.com/yiyuwang/
AﬀVids_mvpa/tree/main/video_info.
Experimental task. Video stimuli were presented across three func-
tional runs (12 videos/run) in the MRI scanner. Each run included an
equal number of videos from each situation category, with an equal num-
ber of high- and low-fear videos (based on median normative ratings)
within each category. The order of video stimulus presentations was
pseudorandomized to ensure uniformity of stimulus types over time
(Extended Data Fig. 1-1). Videos of a given category were preceded by
videos of the same and diﬀerent categories equally often, and videos
with a given normative fear rating were preceded by videos of higher-
and lower-normative-fear ratings equally often. Participants were
instructed and reminded in between scans “to immerse yourself in the
situation shown” and also to “respond according to how you, in partic-
ular, feel in response to viewing the videos.” After each video, partici-
pants consecutively rated experienced fear, arousal, and valence, on a
sliding scale, ranging from “low” to “high” for fear and arousal and
from “negative” to “positive” for valence. Participants used a trackball
to move a cursor along a continuous scale and then clicked a button
under their right thumb to log their rating. Four seconds were
allotted to make each rating (12 s total). The task included an anticipa-
tory period before each video, wherein the word (“heights,” “social,” or
“spider”) corresponding to the category of the upcoming video was
presented for 3 s, followed by a jittered ﬁxation interval of 3–5 s,
during which participants rated their expected fear on a sliding
scale anchored by “low” to “high.” The purpose of this period was
to mitigate eﬀects pertaining to semantic updating that would otherwise
occur when transitioning from a ﬁxation cross to a rich visual image
and to address other research questions regarding anticipatory
activity prior to video watching. This period was not analyzed to
address the present hypotheses. Trials were presented across three
9 min runs. Participants failed to provide fear ratings within the
allotted time on a small proportion of trials. Missing fear ratings were
interpolated (Extended Data Interpolation) and included in analyses.
Stimuli
were presented
using MATLAB
(MathWorks) and the
Psychophysics Toolbox, and behavioral responses were recorded using
a scanner-compatible trackball.
fMRI data acquisition and preprocessing. MRI data were collected
using a 3 T Siemens Trio MRI scanner. Functional images were
acquired in interleaved order using a T2*-weighted multiband echo
planar imaging (EPI) pulse sequence (transverse slices; TR, 1,000 ms;
TE, 3,000 ms; ﬂip angle, 60°; FOV, 200 mm; 2.5 mm; thickness slices;
voxel dimension, 2.5 × 2.5 × 2.5 mm; phase encoding direction anterior
to posterior (AP); multiband acceleration factor, 4). Functional scans
included
coverage
of
the
amygdala
and
orbitofrontal
cortex
(Extended Data Figs. 3-4 and 3-5). Anatomical images were acquired
at the start of the session with a T1-weighted pulse sequence (TR,
2,400 ms; TE, 2,600 ms; ﬂip angle, 8°; FOV, 256 mm; 1-mm-thickness
slices; voxel dimension, 1 × 1× 1 mm).
Image volumes were preprocessed using fMRIprep (Esteban et al.,
2019). Preprocessing included motion correction, slice-timing correc-
tion, removal of high frequency drifts using a temporal high-pass ﬁlter
(discrete cosine transform, 100 s cutoﬀ), and spatial smoothing (6 mm
FWHM). For analysis, functional volumes were downsampled to a
3 mm space to speed up searchlight analyses and registered to participants’
anatomical image and then to a standard template (MNI152) using FSL
FLIRT (Jenkinson et al., 2002). Participants with at least two runs without
excessive head motion (deﬁned as >2 mm maximum framewise displace-
ment) were included in the analysis yielding 18 participants with three
runs of data and 3 participants with two runs of data.
General linear model. A general linear model (GLM) was used to
model the neural data. The GLM included a separate boxcar regressor
for each video stimulus, convolved with a canonical hemodynamic
response function from SPM12. Nuisance regressors included six
2 • J. Neurosci., November 13, 2024 • 44(46):e0142232024
Wang et al. • Neural Predictors of Fear Depend on the Situation


## Page 3

regressors corresponding with motion parameters, three regressors
for physiological noise artifacts (CSF, white matter, framewise displace-
ment), and nonsteady states outliers (stick function per outlier). Three
regressors were included to model low-level visual properties of the stimuli.
Speciﬁcally, luminance, contrast, and the complexity of each extracted
frame were calculated using MATLAB scripts (https://github.com/
yiyuwang/AﬀVids_mvpa/tree/main/calculate_visual_property). Pixel val-
ues were extracted from each frame occurring at the beginning of each
TR. Luminance was calculated as the mean value of the grayscale image
of the frame. Contrast was calculated as the diﬀerence between the max-
imum luminance and the minimum luminance. Complexity was calcu-
lated as the entropy of the grayscale image of the frame. The GLM was
conducted using custom scripts in the Python nilearn module. Beta
maps for each video and participant were used for training the searchlight
LASSO-PCR (see below).
Searchlight LASSO-PCR. For the searchlight multivariate pattern
analysis, betas from the GLM were extracted from voxels within the
voxel’s searchlight neighborhood using a 15 mm (ﬁve voxel) radius.
Because voxel data is nonindependent, we ﬁrst run a principal component
analysis (PCA) with the same number of components as the number voxels
in the searchlight. The PCA transforms nonindependent activity across
voxels as a set of orthogonal components. The components are then
used as regressors in a LASSO regression (Tibshirani, 1996; Chang et
al., 2015) to predict continuous fear ratings. A relatively lenient penalty
term of 0.05 was used since the searchlight analysis already constrains the
dimensionality of the fMRI data. The analysis was performed using
modiﬁed functions from the scikit-learn and nilearn Python module
(Pedregosa et al., 2011). All code is publicly available at https://github.
com/yiyuwang/AﬀVids_mvpa.
Cross-validation. Prior studies that examined the neural predictors
of fear trained and tested their model across groups of individuals
(Kragel and LaBar, 2015; Zhou et al., 2021). Here, we follow suit with
this approach by combining data across participants and training and
testing our models using threefold, leave-whole-subject-out, cross-
validation for statistical robustness (Poldrack et al., 2020). Participants
were randomly divided into three groups (folds) of seven participants
each (we selected three since it evenly divides the 21 participants in
the sample). Models (i.e., searchlight with LASSO-PCR) were iteratively
trained on two groups and tested on the left-out group. The dot product
of the model weights from LASSO-PCR from the training data, and acti-
vation data from the testing sample yields predicted fear ratings.
Pearson’s correlations between the predicted fear ratings and the actual
fear ratings were calculated and assigned to the center voxel of the sphe-
rical searchlight. After iterating the searchlight across the whole brain,
the analysis resulted in a whole brain map of the correlation values
between the predicted ratings and the observed ratings of the testing
sample for each of the threefold. We averaged the maps from the three-
fold as our ﬁnal result.
Model training and testing. In the across-situation training method,
models were trained on data across all three stimulus categories. In each
fold, the model was trained on data corresponding with all 36 videos
from 14 participants (i.e., 504 samples) and was then tested on data
for each stimulus category from the 7 left-out participants. In the
situation-by-situation training method, models were trained on data
from one stimulus category at a time. For example, the model was trained
using data corresponding with 12 heights video stimuli from 14 partici-
pants (i.e., 168 samples) and then tested on data for heights video stimuli
from the 7 left-out participants. The across-situation training method
has the advantage of more training samples, which yields more robust
results. Thus, we performed analyses with more balanced training sets,
too, and found that this training advantage for the situation-general
model is unlikely to impact our conclusions (Extended Data Fig. 3-3).
Permutation testing and statistical correction. Permutation testing
(N = 1,200/voxelwise neighborhood) was used to identify voxels with
nonzero predictions. Models were trained and tested using shuﬄed
data to generate a null distribution of correlation values. A familywise
error (FWE) rate of 0.05 was used to threshold the permutation test
(Nichols and Holmes, 2002; Nichols and Hayasaka, 2003).
Results
Behavioral ﬁndings conﬁrmed the central aim of the task design,
namely, that fear ratings varied from low to high levels within
each content condition and within participants (Fig. 1). Thus,
we proceeded to examine whether and which brain regions con-
tained functional activity that predicts fear ratings within and
across situations. There are three possible outcomes. First, pop-
ulation activity of neurons in a brain region may code for fear
in the same way across situations. If so, then functional activity
for a given brain region may predict fear ratings across situations
using the same “neural codes” (model parameters). Second, pop-
ulation activity may code for fear in diﬀerent ways for diﬀerent
situations, for example, if a brain region contains segregated neu-
ral pathways or the same pathway functionally organizes into dis-
tinct conﬁgurations. If so, then functional activity for a given
brain region may predict fear ratings across situations, but the
neural codes depend on the situation. Finally, a third possibility
is that population activity may code for fear in one or two situa-
tions, but not all three, suggesting that both the brain regions and
neural codes that predict fear are situation dependent. These
Figure 1.
Within-category variation in fear ratings. Each box and whiskers plot shows the mean and variation (quartiles and max/min values) in fear ratings (0, “low fear”; 1, “high fear”)
across participants by video rank. Videos (x-axis) are sorted from lowest to highest on subjective fear ratings by participant, regardless of the video identity, since diﬀerent videos evoked diﬀerent
levels of fear experience across participants. The plot illustrates that the videos were eﬀective at evoking a wide range of fear experiences within each situation and for each person. Thus, MVPA
can be used to examine which brain regions predict fear within and across situations. Extended Data: see Extended Data Figure 1-1 for fear ratings by the order of video presentation.
Wang et al. • Neural Predictors of Fear Depend on the Situation
J. Neurosci., November 13, 2024 • 44(46):e0142232024 • 3


## Page 4

hypothetical possibilities dictate two diﬀerent model training and
testing approaches, as described below.
Across-situation model training: shared neural codes
If a brain region carries situation-general neural codes, then
model training should include instances across situations to
enable the model to best learn which signals are, indeed, situation
general. However, if a brain region contains situation-dependent
neural codes, then even upon training the model with data across
situations, it may only predict fear in one or two situations. To
investigate these possibilities, we ﬁrst trained the searchlight
MVPA using data across all three situations and tested how
well the model predicted fear for every situation using held-out
data. As in prior studies, fear-predictive functional activity was
widely distributed throughout cortical and subcortical areas
(Fig. 2). A breakdown of the situation-general map showed
that 1.9% of voxelwise neighborhoods met criteria of having
model parameters that predicted fear across situations. Of the
remaining voxelwise neighborhoods, 48.2% predicted fear in
one situation, whereas 49.9% predicted fear in two of three situ-
ations. The reported ﬁndings use FWE-corrected signiﬁcance
tests; the proportions of voxels classiﬁed as situation general
and situation dependent did not substantially change when using
a more lenient threshold (Extended Data Fig. 2-1). Voxelwise
neighborhoods that predicted fear across situations were located
in the right posterior insula and the right superior temporal cor-
tex (Fig. 2, red; for a list of ROIs, see Extended Data Table 2-1).
Yet, the overwhelming majority of brain regions that predicted
fear did so in only one or two situations.
Situation-by-situation model training: unshared neural codes
If a brain region carries situation-dependent neural codes, then
model training should occur situation by situation. We trained
and tested the searchlight with LASSO-PCR models situation
by situation (i.e., trained and tested using data from the heights
condition only and the same for spider and social conditions).
This approach resulted in a Pearson’s correlation map per situa-
tion. We performed a conjunction analysis (Nichols et al., 2005)
to identify which voxelwise neighborhoods predict fear across sit-
uations. The conjunction map may reveal areas with functional
activity that predicts fear across all three situations but only
when using unshared neural codes. This is a more lenient
approach for identifying brain regions that predict fear across sit-
uations since the model parameters are allowed to vary by situa-
tion. It may also reveal areas that predict fear in one or two
situations, but not all three. A breakdown of the conjunction
map showed that only 4% of fear-predictive voxelwise neighbor-
hoods carried information in all three situations (Fig. 3, in brown
instead of red shading to distinguish these areas that predict fear
across situations but with unshared neural codes from those in
Fig. 2; for a list of ROIs, see Extended Data Table 3-1). Of the
remaining voxelwise neighborhoods, 66.4% predicted fear in
only one situation, and 29.5% predicted fear in two of the three
situations. We present our ﬁndings using FWE-corrected signiﬁ-
cance tests; however, we performed analyses across a range of
lenient and stringent statistical thresholds to ensure that conclu-
sions were robust across thresholding. The proportions of voxel-
wise neighborhoods classiﬁed as situation general or situation
dependent did not meaningfully change when using a more
lenient threshold (Extended Data Fig. 3-1).
Discussion
In this study, we characterized each brain region based on
whether it contained functional activity that predicted fear rat-
ings across situations using either the same neural code (i.e.,
situation general, shared parameters) or ﬂexible neural codes
Figure 2.
Across-situation model training: shared neural codes. Models were trained using data across all three situations. A, The pie chart illustrates the percentage of voxels that predicted
fear in held-out data in one (dark blue), two (light blue), or all three (red) situations. Only 1.9% of voxelwise neighborhoods predicted fear across all three situations. B, The maps illustrate which
brain regions carried situation-general and situation-dependent information in predicting fear. Situation-dependent areas (both the dark blue and the light blue) are distributed across the whole
brain. The situation-general with shared neural codes areas (red) included the superior temporal cortex, posterior insula areas, and the somatosensory cortex. C, A detailed breakdown of
the neural pattern by each situation and their combinations. Color codes signify the speciﬁc situation or combination of situations predicted by the voxelwise neighborhood. Note, even
with across-situation training, some areas only predicted fear for spider-, social-, or heights-related stimuli. Extended Data: see Extended Data Table 2-1 for the list of situation-general
ROIs in red. See Extended Data Table 2-2 for MVPA studies of fear signatures; Extended Data Figure 2-1 for results using a more lenient threshold; and Extended Data Figure 2-2 for
Pearson’s correlation values in the identiﬁed brain regions.
4 • J. Neurosci., November 13, 2024 • 44(46):e0142232024
Wang et al. • Neural Predictors of Fear Depend on the Situation


## Page 5

(i.e., situation general, unshared parameters) or, alternatively,
whether it only predicted fear in some but not all situations
(i.e., situation dependency). For the overwhelming majority of
brain regions, models of functional activity for predicting fear
were situation dependent (∼98%; Fig. 2). A small portion of vox-
elwise neighborhoods (∼2%) predicted fear across all three situ-
ations using the same model parameters. Even upon allowing the
model parameters to ﬂexibly vary by situation, few areas (∼4%;
Fig. 3) carried information that predicted fear across all three sit-
uations. These results suggest that regional representations of
fear are dominated by functionally heterogeneous, situation-
dependent signals.
These ﬁndings have important implications for understanding
the neural representations and “brain signatures” of fear. The
term brain signature seems to imply uniformity of representation
(Kassam et al., 2013; Peelen and Downing, 2023). However, algo-
rithms commonly used to estimate brain signatures aim to identify
the best functional mapping between patterns of brain activity and
emotion categories, given the inductive bias of the estimation tech-
nique. In the case that there are multiple solutions that leverage
diﬀerent brain representations (Edelman and Gally, 2001; Price
and Friston, 2002; Friston and Price, 2003; Marder and Taylor,
2011), diﬀerent estimation techniques can converge on diﬀerent
solutions, suggesting that there may be multiple signatures of
the same emotion category (for details, see Clark-Polner et al.,
2017; Kragel et al., 2018; Khan et al., 2022; Lindquist et al.,
2022). Correspondingly, “brain signatures” should be interpreted
as an analytical approach wherein brain data are used to opti-
mally predict behavior but for which additional considerations
are required to test theories regarding the neural representations
of emotion (Kragel et al., 2018; Čeko et al., 2022; Lindquist et al.,
2022).
Questions regarding how the brain represents emotions lie at
the crux of emotion theory (Ekman, 1992; Lindquist and Barrett,
2008; Panksepp, 2011; Lindquist et al., 2013; Barrett and Satpute,
2019; Mobbs et al., 2019). Constructionist theory posits substan-
tial within-category heterogeneity in neural representations of
emotion (Barrett, 2006, 2017a,b; Lindquist et al., 2012; Wilson-
Mendenhall et al., 2015; Doyle et al., 2022). According to this
view, fear refers to a population category constituted from
instances with diverse and heterogeneous features (Barrett,
2017a,b; Siegel et al., 2018). Fear occurs when incoming sensory
input is made meaningful with respect to similar previous
instances in a predictive processing neural architecture (Barrett,
2017b). We reasoned that instances from similar situations are
more likely to share features in common with each other, and
thus, the situation may provide a useful heuristic to guide
whether and which instances serve as priors for conceptualizing
future sensory inputs as instances of fear (Satpute and Lindquist,
2019). By this account, fearful situations are not necessarily
organized into “types” (e.g., a predator type, a heights type)
with type-speciﬁc brain states. Rather, some instances of fear
involving spiders, for example, may be similar to those involving
heights, depending on the constituent features (Barrett, 2013;
McVeigh et al., 2023). Consistent with this notion, a substantial
portion of brain regions contained fear-predictive codes that
generalized across two situations even though few brain regions
predicted fear across all three situations. These ﬁndings coincide
with recent theoretical and empirical approaches wherein con-
text is integral to representation rather than modulating a core
response proﬁle (Wilson-Mendenhall et al., 2011; Skerry and
Saxe, 2015; Tamir et al., 2016; Satpute and Lindquist, 2019).
Constructionist theory also proposes that brain representations
of emotion categories will depend on the person, including
Figure 3.
Situation-by-situation model training: unshared neural codes. Models were trained and tested on data from only a single situation, resulting in three maps. A conjunction analysis
was used to identify which brain regions carried information that predicted fear across situations. This is a more lenient approach than across-situation training since model parameters are
allowed to vary, situation-by-situation, in predicting fear. A, The pie chart illustrates the percentage of voxels that predicted fear in held-out data in one (dark blue), two (light blue), or all three
(brown) situations. Four percent of voxelwise neighborhoods predicted fear across all three situations. B, The maps illustrate which brain regions carry situation-general and situation-dependent
information in predicting fear. The situation-general areas but with unshared neural codes areas (brown) included the superior temporal cortex and posterior insula areas, as before, but note
these areas may involve model parameters that still vary by situation. C, A detailed breakdown of the neural pattern by each situation and their combinations. Color codes signify the speciﬁc
situation or combination of situations predicted by the voxelwise neighborhood. Extended Data: see Extended Data Table 3-1 for the list of situation-general ROIs (in brown); Extended Data
Figure 3-1 for results using a more lenient threshold; Extended Data Figure 3-2 for Pearson’s correlation values in the identiﬁed brain areas; Extended Data Figure 3-3 for results comparing
diﬀerent training samples; Extended Data Figures 3-4 and 3-5 for demonstration of signals in amygdala and orbitofrontal cortex; and Extended Data Figure 3-6 for stimulus constant analysis to
investigate the eﬀect of visual properties.
Wang et al. • Neural Predictors of Fear Depend on the Situation
J. Neurosci., November 13, 2024 • 44(46):e0142232024 • 5


## Page 6

one’s cultural background (Immordino-Yang et al., 2016;
Immordino-Yang and Yang, 2017; Lindquist et al., 2022; Pugh
et al., 2022). While our study cannot address this aspect of the
theory due to sampling limitations, person-dependent predictive
models may be tested in future work. Such work may beneﬁt
from using functional hyperalignment to help mitigate variation
in functional neuroanatomy across individuals (Haxby et al.,
2011).
Appraisal theories suggest that emotions result from evaluat-
ing an event’s signiﬁcance to one’s well-being and goals (Lazarus,
1991; Moors et al., 2013). If fear involves a particular appraisal
conﬁguration (Roseman and Smith, 2001) and speciﬁc appraisal
dimensions involve the functioning of speciﬁc neural circuits or
networks (e.g., amygdala for relevance appraisals, hippocampus/
amygdala for novelty appraisals; Brosch and Sander, 2013; Smith
and Lane, 2015), then one might expect activity in those circuits
to generalize in predicting fear across situations. Alternatively,
some appraisal models have proposed that fear is associated
with many, heterogeneous appraisal patterns (Meuleman and
Scherer, 2013) wherein appraisals are not necessarily causal ante-
cedents of a “core fear” state but rather are descriptive features of
emotion (Ellsworth and Scherer, 2003; Ortony and Clore, 2015).
Our ﬁndings showing substantial functional heterogeneity in fear
suggest that many diﬀerent appraisals may take place during
instances of fear, although the causal role of the information cap-
tured by decoding remains to be tested.
Functionalist models posit that fear refers to a goal (e.g., pre-
vent harm from a predator) that may be achieved by diﬀerent
defensive behaviors (e.g., running, freezing, ﬁghting; Fanselow,
1994; Fendt and Fanselow, 1999; Anderson and Adolphs, 2014;
Mobbs et al., 2019). These behaviors are thought to involve a cir-
cuit that traverses the amygdala, hypothalamus, and periaque-
ductal gray, among other primarily subcortical structures.
Diﬀerent conﬁgurations of this circuit may drive diﬀerent defen-
sive behaviors, depending on the situation (e.g., the imminence of
the predator). It remains contested as to whether this circuit
underlies both defensive behaviors and fearful experiences in a
one-system model (Panksepp, 2011; Panksepp et al., 2011) or
whether survival behaviors and fearful experiences involve dis-
tinct neural systems in a two-system model (LeDoux and Pine,
2016; LeDoux and Brown, 2017).
Notwithstanding issues of spatial resolution with standard 3 T
fMRI (Satpute et al., 2013) and constraints of the searchlight
approach (Kragel et al., 2018; Zhou et al., 2021), our ﬁndings sug-
gest that single-system accounts may not fully account for “fear”
(Kragel and LaBar, 2015; Taschereau-Dumouchel et al., 2020).
For instance, functional activity in the amygdala predicted fear
in some but not all situations—even when the neural codes
were allowed to vary to accommodate the idea that a single circuit
may engage in diﬀerent functional conﬁgurations to support
fear. Establishing boundary conditions for generalization would
be a critical avenue for future work. For instance, macrolevel
architecture associated with defensive behavior may generalize
in predicting fear in situations that share features of a preda-
tor–prey interaction, such as predatory imminence (Fanselow,
1994), or, alternatively, when there are similar allostatic
demands, regardless of whether the situation resembles preda-
tor–prey (Schulkin, 2004; Barrett and Finlay, 2018).
Notably, functional activity in some brain regions, including
the posterior temporal cortex and posterior insula, may support
situation-general representations. The presence of these represen-
tations, although less frequent than situation-dependent signals,
suggests that the brain may contain circuitry that processes fearful
events (or aspects of fear) in ways that generalize across situations.
These areas have been inconsistently implicated in prior MVPA
studies on emotion experience (Extended Data Table 2-2). A better
understanding of the nature of generalizable signals may help
address these inconsistencies. Areas overlapping with (Skerry and
Saxe, 2015) or contralateral to (Peelen et al., 2010) the posterior
superior temporal sulcus have been implicated in emotion catego-
rization in the context of emotion perception. The posterior insula
receives sensory inputs from the body and may play a more general
role in arousal or interoception that is shared across mental phe-
nomena (Damasio, 1999; Craig, 2002, 2009; Damasio and
Carvalho, 2013; Kleckner et al., 2017; Satpute et al., 2019). The
mere processing of emotion words (e.g., the word “fear”) in the
absence of an evocative stimulus also involves functional activity
that is widely distributed throughout the brain, including in the lat-
eral temporal cortex (Lee and Satpute, 2024), suggesting that con-
ceptual information may also play a factor in explaining whether
and which brain regions carry generalizable neural representations
of fear. Future work may focus on these areas to replicate these
ﬁndings; determine if they carry generalizable, and speciﬁc, neural
codes that predict fear; and understand the nature of this
information.
Our ﬁndings underscore the importance of testing for exter-
nal validity and generalizability of a given brain–behavior rela-
tionship (Shackman and Wager, 2019; Lee et al., 2021). Many
studies in aﬀective neuroscience preclude tests for external valid-
ity by examining fear in a single context or averaging ﬁndings
across trials. Yet, our ﬁndings suggest that generalizability may
be strongly constrained by the situation. To eﬀect, and perhaps
owing to the lack of robust predictive models of valence (for a
review, see Lee et al., 2021), recent theoretical models in aﬀective
neuroscience incorporated modality as an organizing factor
(Chikazoe et al., 2014; Chang et al., 2015; Satpute et al., 2015;
Kim et al., 2017; Miskovic and Anderson, 2018; Kim et al.,
2019; Lee et al., 2021). For instance, recent work has advanced
a “visually induced fear signature” (Zhou et al., 2021). Yet, we
only used visual stimuli and yet we still found robust evidence
of context dependence. These ﬁndings suggest that representa-
tions of emotion categories are not necessarily organized into
modality-dependent “types” but rather that the sensory modality
is just one aspect of a broader interpretation of context, wherein
context could be characterized in terms of predictions and pre-
diction errors that are derived from prior experience (Lee et al.,
2021; Barrett, 2022).
One potential explanation for our ﬁndings is that the visual
features that drive higher fear in the context of spiders vary
from those that drive higher fear in social or heights contexts.
These diﬀerences in visual features could be viewed as part of
the emotion representation or auxiliary to it (depending on
one’s theoretical perspective), and their role may be investigated
in future work in which these features are explicitly modeled. We
also conducted an additional analysis wherein we estimated pre-
dictive models of fear while holding the stimulus constant and
found that even when doing so, functional activity that predicts
fear ratings was widely distributed throughout the brain and var-
ied by situation (Extended Data Fig. 3-6).
Insofar as fear holds a central position in emotion theory, it
stands to reason that other emotion categories, too, are likely
to exhibit degeneracy, or many-to-one relationships between
brain states and psychological constructs (Friston and Price,
2003; Barrett and Satpute, 2019; Doyle et al., 2022; Khan et al.,
2022). Notably, our ﬁndings converge with recent work showing
strong evidence of situation dependence in the peripheral
6 • J. Neurosci., November 13, 2024 • 44(46):e0142232024
Wang et al. • Neural Predictors of Fear Depend on the Situation


## Page 7

autonomic correlates of fear, too (McVeigh et al., 2023).
Modeling this variation may be key to developing a fundamental
understanding of complex mind–brain–behavior relationships
alongside personalized treatments in clinical populations.
Data Availability
Anonymized data will be deposited in OpenNeuro (https://
openneuro.org/) after publication. Analysis scripts are available
in Github at https://github.com/yiyuwang/AﬀVids_mvpa.
References
Anderson DJ, Adolphs R (2014) A framework for studying emotions across
species. Cell 157:187–200.
Azari B, et al. (2020) Comparing supervised and unsupervised approaches to
emotion categorization in the human brain, body, and subjective experi-
ence. Sci Rep 10:1–17.
Barrett LF (2006) Are emotions natural kinds? Perspect Psychol Sci 1:28–58.
Barrett LF (2013) Psychological construction: the Darwinian approach to the
science of emotion. Emot Rev 5:379–389.
Barrett LF (2017a) How emotions are made: the secret life of the brain. New
York City: Pan Macmillan.
Barrett LF (2017b) The theory of constructed emotion: an active inference
account of interoception and categorization. Soc Cogn Affect Neurosci
12:1–23.
Barrett LF (2022) Context reconsidered: complex signal ensembles, relational
meaning, and population thinking in psychological science. Am Psychol
77:894.
Barrett LF, Finlay BL (2018) Concepts, goals and the control of survival-
related behaviors. Curr Opin Behav Sci 24:172–179.
Barrett LF, Satpute AB (2019) Historical pitfalls and new directions in the
neuroscience of emotion. Neurosci Lett 693:9–18.
Brosch T, Sander D (2013) Comment: the appraising brain: towards a neuro-
cognitive model of appraisal processes in emotion. Emot Rev 5:163–168.
Caseras X, Mataix-Cols D, Trasovares MV, López-Solà M, Ortriz H, Pujol J,
Soriano-Mas C, Giampietro V, Brammer MJ, Torrubia R (2010)
Dynamics of brain responses to phobic-related stimulation in speciﬁc
phobia subtypes. Eur J Neurosci 32:1414–1422.
Čeko M, Kragel PA, Woo C-W, López-Solà M, Wager TD (2022) Common
and stimulus-type-speciﬁc brain representations of negative affect. Nat
Neurosci 25:760–770.
Celeghin A, Diano M, Bagnis A, Viola M, Tamietto M (2017) Basic emotions
in human neuroscience: neuroimaging and beyond. Front Psychol 8:1432.
Chang LJ, Gianaros PJ, Manuck SB, Krishnan A, Wager TD (2015) A sensitive
and speciﬁc neural signature for picture-induced negative affect. PLoS
Biol 13:e1002180.
Chikazoe J, Lee DH, Kriegeskorte N, Anderson AK (2014) Population coding
of affect across stimuli, modalities and individuals. Nat Neurosci 17:1114–
1122.
Clark-Polner E, Johnson TD, Barrett LF (2017) Multivoxel pattern analysis
does not provide evidence to support the existence of basic emotions.
Cereb Cortex 27:1944–1948.
Craig AD (2002) How do you feel? Interoception: the sense of the physiolog-
ical condition of the body. Nat Rev Neurosci 3:655–666.
Craig AD (2009) How do you feel—now? The anterior insula and human
awareness. Nat Rev Neurosci 10:59–70.
Dalgleish T, Dunn BD, Mobbs D (2009) Affective neuroscience: past, present,
and future. Emot Rev 1:355–368.
Damasio AR (1999) The feeling of what happens: body and emotion in the
making of consciousness. Orlando, FL: Houghton Mifﬂin Harcourt.
Damasio A, Carvalho GB (2013) The nature of feelings: evolutionary and neu-
robiological origins. Nat Rev Neurosci 14:143–152.
Doyle CM, Lane ST, Brooks JA, Wilkins RW, Gates KM, Lindquist KA (2022)
Unsupervised classiﬁcation reveals consistency and degeneracy in neural
network patterns of emotion. Soc Cogn Affect Neurosci 17:995–1006.
Edelman GM, Gally JA (2001) Degeneracy and complexity in biological sys-
tems. Proc Natl Acad Sci U S A 98:13763–13768.
Ekman P (1992) Are there basic emotions? Psychol Rev 99:550–553.
Ellsworth PC, Scherer KR (2003) Appraisal processes in emotion. In:
Handbook of affective sciences (Davidson RJ, Scherer KR, Goldsmith
HH, eds). Oxford, UK: Oxford University Press.
Esteban O, et al. (2019) fMRIPrep: a robust preprocessing pipeline for func-
tional MRI. Nat Methods 16:111–116.
Fanselow MS (1994) Neural organization of the defensive behavior system
responsible for fear. Psychon Bull Rev 1:429–438.
Fanselow MS, Pennington ZT (2017) The danger of LeDoux and Pine’s two-
system framework for fear. Am J Psychiatry 174:1120–1121.
Fendt M, Fanselow MS (1999) The neuroanatomical and neurochemical basis
of conditioned fear. Neurosci Biobehav Rev 23:743–760.
Friston KJ, Price CJ (2003) Degeneracy and redundancy in cognitive anat-
omy. Trends Cogn Sci 7:151–152.
Gendron M, Feldman Barrett L (2009) Reconstructing the past: a century of
ideas about emotion in psychology. Emot Rev 1:316–339.
Haxby JV, Guntupalli JS, Connolly AC, Halchenko YO, Conroy BR, Gobbini
MI, Hanke M, Ramadge PJ (2011) A common, high-dimensional model
of the representational space in human ventral temporal cortex. Neuron
72:404–416.
Immordino-Yang MH, Yang X-F (2017) Cultural differences in the neural
correlates of social–emotional feelings: an interdisciplinary, developmen-
tal perspective. Curr Opin Psychol 17:34–40.
Immordino-Yang MH, Yang X-F, Damasio H (2016) Cultural modes of
expressing emotions inﬂuence how emotions are experienced. Emotion
16:1033.
Jenkinson M, Bannister P, Brady M, Smith S (2002) Improved optimization
for the robust and accurate linear registration and motion correction of
brain images. Neuroimage 17:825–841.
Kassam KS, Markey AR, Cherkassky VL, Loewenstein G, Just MA (2013)
Identifying emotions on the basis of neural activation. PLoS One 8:
e66032.
Khan Z, Wang Y, Sennesh E, Dy J, Ostadabbas S, van de Meent J-W,
Hutchinson JB, Satpute AB (2022) A computational neural model for
mapping degenerate neural architectures. Neuroinformatics 20:1–15.
Kim H-C, Bandettini PA, Lee J-H (2019) Deep neural network predicts emo-
tional responses of the human brain from functional magnetic resonance
imaging. NeuroImage 186:607–627.
Kim J, Shinkareva SV, Wedell DH (2017) Representations of modality-
general valence for videos and music derived from fMRI data.
NeuroImage 148:42–54.
Kleckner IR, Zhang J, Touroutoglou A, Chanes L, Xia C, Simmons WK,
Quigley KS, Dickerson BC, Feldman Barrett L (2017) Evidence for a
large-scale brain system supporting allostasis and interoception in
humans. Nat Hum Behav 1:1–14.
Kragel PA, Koban L, Barrett LF, Wager TD (2018) Representation, pattern
information, and brain signatures: from neurons to neuroimaging.
Neuron 99:257–273.
Kragel PA, LaBar KS (2015) Multivariate neural biomarkers of emotional
states are categorically distinct. Soc Cogn Affect Neurosci 10:1437–1448.
Kragel PA, LaBar KS (2016) Decoding the nature of emotion in the brain.
Trends Cogn Sci 20:444–455.
Kriegeskorte N, Goebel R, Bandettini P (2006) Information-based functional
brain mapping. Proc Natl Acad Sci U S A 103:3863–3868.
Lazarus RS (1991) Emotion and adaptation. Oxford, UK: Oxford University
Press.
LeDoux JE, Brown R (2017) A higher-order theory of emotional conscious-
ness. Proc Natl Acad Sci U S A 114:E2016–E2025.
LeDoux JE, Pine DS (2016) Using neuroscience to help understand fear and
anxiety: a two-system framework. Am J Psychiatry 173:1083.
Lee KM, Ferreira-Santos F, Satpute AB (2021) Predictive processing models
and affective neuroscience. Neurosci Biobehav Rev 131:211–228.
Lee KM, Satpute AB (2024) More than labels: neural representations of
emotion words are widely distributed across the brain. Soc Cogn Affect
Neurosci 19:nsae043.
Lindquist KA, Barrett LF (2008) Constructing emotion: the experience of fear
as a conceptual act. Psychol Sci 19:898–903.
Lindquist KA, Jackson JC, Leshin J, Satpute AB, Gendron M (2022) The cul-
tural evolution of emotion. Nat Rev Psychol 1:669–681.
Lindquist KA, Siegel EH, Quigley KS, Barrett LF (2013) The hundred-year
emotion war: Are emotions natural kinds or psychological constructions?
Comment on Lench, Flores, and Bench (2011). Psychol Bull 139:255–263.
Lindquist KA, Wager TD, Kober H, Bliss-Moreau E, Barrett LF (2012) The
brain basis of emotion: a meta-analytic review. Behav Brain Sci 35:121.
Lueken U, Kruschwitz JD, Muehlhan M, Siegert J, Hoyer J, Wittchen H-U
(2011) How speciﬁc is speciﬁc phobia? Different neural response patterns
in two subtypes of speciﬁc phobia. NeuroImage 56:363–372.
Wang et al. • Neural Predictors of Fear Depend on the Situation
J. Neurosci., November 13, 2024 • 44(46):e0142232024 • 7


## Page 8

Marder E, Taylor AL (2011) Multiple models to capture the variability in bio-
logical neurons and networks. Nat Neurosci 14:133–138.
McVeigh K, Kleckner IR, Quigley KS, Satpute AB (2023) Fear-related psycho-
physiological patterns are situation and individual dependent: a Bayesian
model comparison approach. Emotion 24:506–521.
Meuleman B, Scherer KR (2013) Nonlinear appraisal modeling: an applica-
tion of machine learning to the study of emotion production. IEEE
Trans Affect Comput 4:398–411.
Michalowski JM, Matuszewski J, Droździel D, Koziejowski W, Rynkiewicz A,
Jednoróg K, Marchewka A (2017) Neural response patterns in spider,
blood-injection-injury and social fearful individuals: new insights from
a simultaneous EEG/ECG–fMRI study. Brain Imaging Behav 11:829–845.
Miskovic V, Anderson A (2018) Modality general and modality speciﬁc cod-
ing of hedonic valence. Curr Opin Behav Sci 19:91–97.
Mobbs D, Adolphs R, Fanselow MS, Barrett LF, LeDoux JE, Ressler K, Tye
KM (2019) Viewpoints: approaches to deﬁning and investigating fear.
Nat Neurosci 22:1205–1216.
Moors A, Ellsworth PC, Scherer KR, Frijda NH (2013) Appraisal theories of
emotion: state of the art and future development. Emot Rev 5:119–124.
Nichols T, Brett M, Andersson J, Wager T, Poline J-B (2005) Valid conjunc-
tion inference with the minimum statistic. NeuroImage 25:653–660.
Nichols T, Hayasaka S (2003) Controlling the familywise error rate in functional
neuroimaging: a comparative review. Stat Methods Med Res 12:419–446.
Nichols TE, Holmes AP (2002) Nonparametric permutation tests for func-
tional neuroimaging: a primer with examples. Hum Brain Mapp 15:1–25.
Nummenmaa L, Saarimäki H (2019) Emotions as discrete patterns of systemic
activity. Neurosci Lett 693:3–8.
Ortony A, Clore G (2015) Can an appraisal model be compatible with psycho-
logical constructionism. In: The psychological construction of emotion
(Barrett LF, Russell JA, eds), pp 305–333. New York, NY: Guilford Press.
Panksepp J (2011) The basic emotional circuits of mammalian brains: do
animals have affective lives? Neurosci Biobehav Rev 35:1791–1804.
Panksepp J, Fuchs T, Iacobucci P (2011) The basic neuroscience of emotional
experiences in mammals: the case of subcortical FEAR circuitry and
implications for clinical anxiety. Appl Anim Behav Sci 129:1–17.
Pedregosa F, et al. (2011) Scikit-learn: machine learning in python. J Mach
Learn Res 12:2825–2830.
Peelen MV, Atkinson AP, Vuilleumier P (2010) Supramodal representations
of perceived emotions in the human brain. J Neurosci 30:10127–10134.
Peelen MV, Downing PE (2023) Testing cognitive theories with multivariate
pattern analysis of neuroimaging data. Nat Hum Behav 7:1430–1441.
Poldrack RA, Huckins G, Varoquaux G (2020) Establishment of best practices
for evidence for prediction: a review. JAMA Psychiatry 77:534–540.
Price CJ, Friston KJ (2002) Degeneracy and cognitive anatomy. Trends Cogn
Sci 6:416–421.
Pugh ZH, Choo S, Leshin JC, Lindquist KA, Nam CS (2022) Emotion depends
on context, culture and their interaction: evidence from effective connec-
tivity. Soc Cogn Affect Neurosci 17:206–217.
Roseman IJ, Smith CA (2001) Appraisal theory. In: Appraisal processes in
emotion: theory, methods, research (Scherer KR, Schorr A, Johnstone T,
eds), pp 3–19. Oxford, UK: Oxford University Press.
Saarimäki H, Ejtehadian LF, Glerean E, Jääskeläinen IP, Vuilleumier P, Sams
M, Nummenmaa L (2018) Distributed affective space represents multiple
emotion categories across the human brain. Soc Cogn Affect Neurosci 13:
471–482.
Saarimäki H, Gotsopoulos A, Jääskeläinen IP, Lampinen J, Vuilleumier P,
Hari R, Sams M, Nummenmaa L (2016) Discrete neural signatures of
basic emotions. Cereb Cortex 26:2563–2573.
Satpute AB, Kang J, Bickart KC, Yardley H, Wager TD, Barrett LF (2015)
Involvement of sensory regions in affective experience: a meta-analysis.
Front Psychol 6:1860.
Satpute AB, Kragel PA, Barrett LF, Wager TD, Bianciardi M (2019)
Deconstructing arousal into wakeful, autonomic and affective varieties.
Neurosci Lett 693:19–28.
Satpute AB, Lindquist KA (2019) The default mode network’s role in discrete
emotion. Trends Cogn Sci 23:851–864.
Satpute AB, Wager TD, Cohen-Adad J, Bianciardi M, Choi J.-K, Buhle JT,
Wald LL, Barrett LF (2013) Identiﬁcation of discrete functional subre-
gions of the human periaqueductal gray. Proc Natl Acad Sci U S A 110:
17101–17106.
Schulkin J (2004) Allostasis, homeostasis and the costs of physiological adapta-
tion, pp 164–227. Cambridge: Cambridge University Press.
Shackman AJ, Wager TD (2019) The emotional brain: fundamental questions
and strategies for future research. Neurosci Lett 693:68–74.
Siegel EH, Sands MK, Van den Noortgate W, Condon P, Chang Y, Dy J,
Quigley KS, Barrett LF (2018) Emotion ﬁngerprints or emotion popula-
tions? A meta-analytic investigation of autonomic features of emotion
categories. Psychol Bull 144:343.
Skerry AE, Saxe R (2015) Neural representations of emotion are organized
around abstract event features. Curr Biol 25:1945–1954.
Smith R, Lane RD (2015) The neural basis of one’s own conscious and
unconscious emotional states. Neurosci Biobehav Rev 57:1–29.
Tamir DI, Thornton MA, Contreras JM, Mitchell JP (2016) Neural evidence
that three dimensions organize mental state representation: rationality,
social impact, and valence. Proc Natl Acad Sci U S A 113:194–199.
Taschereau-Dumouchel V, Kawato M, Lau H (2020) Multivoxel pattern
analysis reveals dissociations between subjective fear and its physiological
correlates. Mol Psychiatry 25:2342–2354.
Tibshirani R (1996) Regression shrinkage and selection via the lasso. J R Stat
Soc Series B Methodol 58:267–288.
Vytal K, Hamann S (2010) Neuroimaging support for discrete neural corre-
lates of basic emotions: a voxel-based meta-analysis. J Cogn Neurosci
22:2864–2885.
Wager TD, Atlas LY, Leotti LA, Rilling JK (2011) Predicting individual
differences in placebo analgesia: contributions of brain activity during
anticipation and pain experience. J Neurosci 31:439–452.
Wilson-Mendenhall CD, Barrett LF, Barsalou LW (2015) Variety in emotional
life: within-category typicality of emotional experiences is associated with
neural activity in large-scale brain networks. Soc Cogn Affect Neurosci 10:
62–71.
Wilson-Mendenhall CD, Barrett LF, Simmons WK, Barsalou LW (2011)
Grounding emotion in situated conceptualization. Neuropsychologia
49:1105–1127.
Zhou F, Zhao W, Qi Z, Geng Y, Yao S, Kendrick KM, Wager TD, Becker B
(2021) A distributed fMRI-based signature for the subjective experience
of fear. Nat Commun 12:1–16.
8 • J. Neurosci., November 13, 2024 • 44(46):e0142232024
Wang et al. • Neural Predictors of Fear Depend on the Situation


