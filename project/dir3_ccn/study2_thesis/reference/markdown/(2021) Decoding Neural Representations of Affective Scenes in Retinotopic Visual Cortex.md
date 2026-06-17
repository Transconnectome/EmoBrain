# (2021) Decoding Neural Representations of Affective Scenes in Retinotopic Visual Cortex

**Source:** (2021) Decoding Neural Representations of Affective Scenes in Retinotopic Visual Cortex.pdf

---

## Page 1

© The Author(s) 2021. Published by Oxford University Press. All rights reserved. For permissions, please e-mail: journals.permissions@oup.com
Cerebral Cortex, June 2021;31: 3047–3063
doi: 10.1093/cercor/bhaa411
Advance Access Publication Date: 16 February 2021
Original Article
O R I G I N A L A RT I C L E
Decoding Neural Representations of Affective
Scenes in Retinotopic Visual Cortex
Ke Bo1, Siyang Yin1, Yuelu Liu2, Zhenhong Hu1, Sreenivasan Meyyappan1,
Sungkean Kim1, Andreas Keil
3 and Mingzhou Ding
1
1J. Crayton Pruitt Family Department of Biomedical Engineering, University of Florida, Gainesville, FL 32611,
USA, 2Center for Mind and Brain, University of California, Davis, CA 95618, USA and 3Department of
Psychology, University of Florida, Gainesville, FL 32611, USA
Address correspondence to Mingzhou Ding. Email: mding@bme.ufl.edu; Andreas Keil. Email: akeil@ufl.edu.
Abstract
The perception of opportunities and threats in complex visual scenes represents one of the main functions of the human
visual system. The underlying neurophysiology is often studied by having observers view pictures varying in affective
content. It has been shown that viewing emotionally engaging, compared with neutral, pictures (1) heightens blood flow in
limbic, frontoparietal, and anterior visual structures and (2) enhances the late positive event-related potential (LPP). The
role of retinotopic visual cortex in this process has, however, been contentious, with competing theories predicting the
presence versus absence of emotion-specific signals in retinotopic visual areas. Recording simultaneous
electroencephalography–functional magnetic resonance imaging while observers viewed pleasant, unpleasant, and neutral
affective pictures, and applying multivariate pattern analysis, we found that (1) unpleasant versus neutral and pleasant
versus neutral decoding accuracy were well above chance level in retinotopic visual areas, (2) decoding accuracy in ventral
visual cortex (VVC), but not in early or dorsal visual cortex, was correlated with LPP, and (3) effective connectivity from
amygdala to VVC predicted unpleasant versus neutral decoding accuracy, whereas effective connectivity from ventral
frontal cortex to VVC predicted pleasant versus neutral decoding accuracy. These results suggest that affective scenes
evoke valence-specific neural representations in retinotopic visual cortex and that these representations are influenced by
reentry signals from anterior brain regions.
Key words: affective scenes, amygdala, late positive potential, multivariate pattern analysis, visual cortex
Introduction
Visual media are a major source of information as well as
entertainment and, as such, have become a central element
in people’s lives. Using pictures or videos of varying emotional
content to elicit strong viewer response is a key aspect of visual
media usage. Studies have shown that compared with affec-
tively neutral visual stimuli, emotionally engaging visual stimuli
are viewed longer (Bradley et al. 2001), rated as being more
arousing (Lang et al. 1993), and accompanied by heightened
autonomic as well as neurophysiological responses (Bradley
2009). Because of these properties, viewing affective pictures
has been extensively used as a laboratory model of emotional
engagement, resulting in an immense literature (Bradley et al.
2012), which includes studies aiming to characterize the neuro-
physiological basis of emotional picture perception (Sabatinelli
et al. 2011; Frank and Sabatinelli 2017).
Functional magnetic resonance imaging (fMRI) studies have
shown that viewing emotionally arousing pictures, relative to
neutral pictures, prompts higher blood oxygen level-dependent
(BOLD) activity in a widespread network of regions, includ-
ing the amygdaloid complex, pulvinar, medial prefrontal cor-
tex (MPFC), orbitofrontal cortex, and widespread extrastriate
parieto-occipital and temporal cortices, with strong responses in
higher-order, but not retinotopic, visual areas (Lang et al. 1998;
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 2

3048
Cerebral Cortex, 2021, Vol. 31, No. 6
Bradley et al. 2003, 2015; Norris et al. 2004; Sabatinelli et al.
2005). Over the past decade, however, evidence from other mea-
surement modalities [e.g., electroencephalography (EEG) and
event-related potential (ERP); Thigpen et al. 2017], ranging from
experimental animals (Li et al. 2019) to computational modeling
(Kragel et al. 2019), has supported the strong involvement of
early, retinotopic visual areas in representing emotional content.
Although these findings are in line with behavioral studies
showing that emotion facilitates early visual processing (Phelps
et al. 2006), hemodynamic imaging work has to date failed to
observe consistent differential activation between emotional
and neutral pictures in primary visual cortex and other retino-
topic areas (Lang et al. 1998; Sabatinelli et al. 2014).
The lack of consistent findings may be partly attributable
to the limitations of univariate analysis methods used in most
of the prior fMRI studies. The recent advent of multivariate
pattern analysis (MVPA) provides a potential avenue to close the
gap. MVPA examines voxel-level activation within a region of
interest (ROI) as a multivariate pattern and yields a decoding
accuracy to quantify the difference between patterns of different
classes of stimuli at the single subject level (Norman et al. 2006).
This technique has been successfully applied in affective neuro-
science and has extended the field beyond univariate studies by
decoding multivoxel neural representations of emotion within
specific brain regions (Ethofer et al. 2009; Peelen et al. 2010)
and within large-scale neural networks (Baucom et al. 2012;
Saarimäki et al. 2015; Bush et al. 2017). Building on this body of
work, the present study applied MVPA to systematically define
the multivoxel patterns evoked by emotional stimuli within
specific regions along the retinotopic visual hierarchy, extending
from primary visual cortex (V1) to intraparietal cortex along
the dorsal pathway and to parahippocampal cortex (PHC) along
the ventral pathway, and tested the hypothesis that voxel pat-
terns in retinotopic cortex code for valence-specific emotional
content.
If visuocortical activation patterns encode emotional con-
tent, this would raise the question regarding the origin of these
patterns. Two competing but not mutually exclusive groups of
hypotheses have been advanced to account for emotion-specific
modulations of activity in retinotopic visual areas. First, the
so-called reentry hypothesis states that the increased visual
activation evoked by affective pictures results from reentrant
feedback, meaning that signals arising in subcortical emotion-
processing structures such as the amygdala propagate to visual
cortex to facilitate the processing of motivationally salient stim-
uli (Sabatinelli et al. 2005; Lang and Bradley 2010; Pessoa 2010).
According to tracer studies in macaques, such reentrant projec-
tions exist, and they are more sparse for retinotopic, compared
with anterior visual regions (Amaral et al. 2003; Freese and Ama-
ral 2005), consistent with findings from univariate fMRI studies
(Sabatinelli et al. 2011) and from ERP studies (Keil et al. 2002).
Neuroimaging studies have also lent support to the reentry
hypothesis by comparing enhanced hemodynamic responses
evoked by emotionally arousing stimuli in the amygdala and
in the visual cortex (Lane et al. 1997; Pessoa et al. 2002; Sato
et al. 2004; Sabatinelli et al. 2005). For example, a fast-sample
fMRI study demonstrated that the response enhancement in the
amygdala precedes that in extrastriate visual cortex (Sabatinelli
et al. 2009). Moreover, amygdala and visual cortical activity
strongly covary during emotional picture viewing (Sabatinelli
et al. 2005; Kang et al. 2016). Critically, patients with amygdala
lesions showed no enhancement in visual cortical activity when
fearful faces were presented even though their visual system
remains intact (Vuilleumier et al. 2004). This evidence suggests
that amygdala is possibly a source of the reentrant signals.
A second group of hypotheses states that sensory cortex,
including retinotopic visual areas, may itself code for emotional
qualities of a stimulus, without the necessity for recurrent pro-
cessing (see Miskovic and Anderson 2018 for a review). Evi-
dence supporting this hypothesis comes from empirical studies
in experimental animals (Weinberger 2004; Li et al. 2019) as
well as in human observers (Thigpen et al. 2017), in which the
extensive pairing of simple sensory cues such as tilted lines or
sinusoidal gratings with emotionally relevant outcomes shapes
early sensory responses (Miskovic and Keil 2012). Beyond simple
cues, recent computational work using deep neural networks
has also suggested that visual cortex may intrinsically represent
emotional value as contained in complex visual media such as
video clips of varying affective content (Kragel et al. 2019).
The competing notions discussed above may be aligned
under the perspective that novel, complex emotional scenes
initially
elicit
widespread
recurrent
processing,
including
between retinotopic visual and limbic/frontal areas, prompting
emotion-specific signaling in visual cortex (Bradley et al. 2012).
If repeated extensively, critical stimulus properties of emotional
stimuli may well be represented natively in retinotopic visual
areas (McTeague et al. 2015). Hampering advancement of either
group of hypotheses, however, is the fact that it is unclear
to what extent retinotopic visual areas contain information
specific to emotional content and—if so—how this information
emerges. Here, we use multimodal neuroimaging together with
novel computational techniques to examine the hypotheses that
(1) retinotopic visual cortex contains voxel pattern information
that is specific to emotional content and (2) these patterns are
formed under the influence of reentrant signals from anterior
brain structures, for example, the amygdala.
Recurrent processing such as the engagement of large-scale
reentrant feedback projections may be assessed in different
ways. First, slow hemodynamic interarea interactions can be
quantified through suitable BOLD-based functional connectivity
analyses, allowing us to quantify, for example, the functional
interaction between amygdala and visual cortex (Freese and
Amaral 2005; Sabatinelli et al. 2009, 2014). Second, recurrent
processing may be characterized by leveraging the greater time
resolution of scalp-recorded brain electric activity. For example,
human EEG studies have shown that the late positive potential
(LPP), a positive-going, long-lasting ERP component that starts
about 300–400 ms after picture onset, may serve as an index of
signal reentry. Robust LPP enhancement has been found when
comparing emotion stimuli with neutral stimuli (Cacioppo et al.
1994; Schupp et al. 2000; Keil et al. 2002; Pastor et al. 2008). More-
over, the amplitude of the LPP enhancement is linearly related
to BOLD activity, both in visual cortex and in the amygdala
(Sabatinelli et al. 2009, 2013; Liu et al. 2012), and is thought to
reflect heightened processing of motivational relevant stimuli in
perceptual, memory, and motor systems, associated with signal
reentry (Vuilleumier 2005; Hajcak et al. 2006; Lang and Bradley
2010).
We recorded simultaneous EEG-fMRI data from subjects
viewing pleasant, unpleasant, and neutral pictures selected
from the International Affective Picture System (IAPS; Lang et al.
1997). Given the questions and hypotheses stated above, the
primary focus here was on the fMRI data, with the EEG data used
mainly to yield the LPP amplitude for each participant, serving
as a proxy for recurrent processing among visual and extravisual
regions in the brain’s emotion network (Liu et al. 2012).
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 3

Decoding Neural Representations of Affective Scenes
Bo et al.
3049
In addition to conventional univariate BOLD activation and
LPP analyses, BOLD responses were estimated on a trial-by-
trial basis, and MVPA was applied to decode single-trial BOLD
responses to investigate if the neural patterns within retinotopic
visual cortex were distinct between emotional and neutral
scenes. Strength of reentrant feedback indexed by LPP amplitude
and frontotemporal→visual cortex effective connectivity (EC)
was correlated with MVPA decoding accuracy in visual cortex
to test the impact of signal reentry on neural representations of
emotional stimuli.
Materials and Methods
Overview
Simultaneous EEG-fMRI was recorded from human subjects
viewing pleasant, unpleasant, and neutral pictures from the
IAPS library (Lang et al. 1997). Following signal preprocessing,
univariate and multivariate analyses were applied to examine
the neural representations of affective pictures in retinotopic
visual cortex. To help with reading, a table explaining the
abbreviated labels of each investigated brain region is included
in the supplementary materials (Supplementary Table S1).
Participants
The experimental protocol was approved by the Institutional
Review Board of the University of Florida. A total of 26 healthy
volunteers with normal or corrected-to-normal vision gave writ-
ten informed consent and participated in this study. Before the
magnetic resonance imaging (MRI) scan, two subjects withdrew
from the experiment. In addition, data from four participants
were discarded due to artifacts generated by excessive move-
ments inside the scanner. The data from the remaining 20
subjects were analyzed and reported here (10 women; mean age:
20.4 ± 3.1).
Stimuli
The stimuli consisted of 60 gray-scaled pictures selected from
the IAPS (Lang et al. 1997). Their IAPS IDs are as follows: (1)
20 pleasant pictures: 4311, 4599, 4610, 4624, 4626, 4641, 4658,
4680, 4694, 4695, 2057, 2332, 2345, 8186, 8250, 2655, 4597, 4668,
4693, 8030; (2) 20 neutral pictures: 2398, 2032, 2036, 2037, 2102,
2191, 2305, 2374, 2377, 2411, 2499, 2635, 2347, 5600, 5700, 5781,
5814, 5900, 8034, 2387; (3) 20 unpleasant pictures: 1114, 1120,
1205, 1220, 1271, 1300, 1302, 1931, 3030, 3051, 3150, 6230, 6550,
9008, 9181, 9253, 9420, 9571, 3000, 3069. The pleasant pictures
included sports scenes, romance, and erotic couples and had
an average valence rating of 7.0 ± 0.45. The unpleasant pictures
included threat/attack scenes and bodily mutilations and had
an average valence rating of 2.8 ± 0.88. The neutral pictures
consisted of images containing landscapes and neutral humans
and had an average valence rating of 6.3 ± 0.99. The arousal
ratings of these pictures are as follows: pleasant (5.8 ± 0.90),
unpleasant (6.2 ± 0.79), both being higher than that of neutral
pictures (4.2 ± 0.97) (all ratings are based on a 1–9 scale). To
minimize confounds, across categories, pictures were chosen to
be similar overall in composition and in rated complexity and
matched in picture file size. In addition, no significant difference
was found across categories in entropy (F = 1.05, P = 0.35) and in
pixel contrast (F = 0.52, P = 0.60).
Procedure
As shown in Figure 1, each IAPS picture was displayed on a
magnetic resonance (MR)-compatible monitor for 3 s, which was
followed by a variable (2800 or 4300 ms) interstimulus interval.
There were five sessions. Each session comprised 60 trials corre-
sponding to the 60 different pictures. The same 60 pictures were
shown in each session, but the order of picture presentation was
randomized from session to session. Stimuli were presented on
the monitor placed outside the scanner and viewed via a reflec-
tive mirror. Participants were instructed to maintain fixation on
the cross at the center of the screen during the whole session.
After the experiment, participants were instructed to rate the
hedonic valence and emotional arousal level of 12 representative
IAPS pictures (four pleasant, four neutral, and four unpleasant),
which were not part of the 60-picture set. The rating was done
using a paper and pencil version of the self-assessment manikin
(Bradley and Lang 1994). As shown in Supplementary Table S2
of the supplementary materials, the ratings of the 12 pictures
by the participants are consistent with the normative ratings of
these pictures (Lang et al. 1997).
Data Acquisition
Functional MRI data were collected on a 3 T Philips Achieva scan-
ner (Philips Medical Systems), with the following parameters:
echo time, 30 ms; repetition time, 1.98 s; flip angle, 80◦; slice
number, 36; field of view, 224 mm; voxel size, 3.5 × 3.5 × 3.5 mm;
matrix size, 64 × 64. Slices were acquired in ascending order
and oriented parallel to the plane connecting the anterior and
posterior commissure. T1-weighted high-resolution structural
image was also obtained.
EEG data were recorded simultaneously with fMRI using a 32-
channel MR-compatible EEG system (Brain Products GmbH). A
total of 31 sintered Ag/AgCl electrodes were placed on the scalp
according to the 10–20 system, and one additional electrode was
placed on subject’s upper back to monitor electrocardiograms
(ECGs). The recorded ECG was used to detect heartbeat events
and assist in the removal of the cardioballistic artifacts. The EEG
channels were referenced to the FCz electrode during recording.
EEG signal was recorded with an online 0.1–250 Hz band-pass
filter and digitized to 16-bit at a sampling rate of 5 kHz. The EEG
recording system was synchronized with the scanner’s internal
clock throughout recording to ensure the successful removal of
the gradient artifact in subsequent preprocessing.
Data Preprocessing
The fMRI data were preprocessed with SPM (http://www.
fil.ion.ucl.ac.uk/spm/).
The
first
five
volumes
from
each
session were discarded to eliminate artifacts caused by the
transient instability of scanner. Slice timing was corrected using
interpolation to account for differences in slice acquisition
time. The images were then corrected for head movement
by spatially realigning them to the sixth image of each
session, normalized and registered to the Montreal Neurological
Institute template, and resampled to a spatial resolution of
3 × 3 × 3 mm. The transformed images were smoothed by a
Gaussian filter with a full width at half maximum of 8 mm.
Low-frequency temporal drift was removed from the functional
images by applying a high-pass filter with a cutoff frequency of
1/128 Hz.
The EEG data were first processed using Brain Vision Ana-
lyzer 2.0 (Brain Products GmbH) to remove scanner artifacts. For
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 4

3050
Cerebral Cortex, 2021, Vol. 31, No. 6
Figure 1. Picture viewing paradigm. There were five sessions. Each session lasted 7 min. A total of 60 IAPS pictures, including 20 pleasant, 20 unpleasant, and 20 neutral,
were presented in each session, the order of which randomly varied from session to session. Each picture lasted 3 s and was followed by a fixation period referred to
as intertrial interval (ITI) (2.8 or 4.3 s). Participants were required to fixate on the cross in the center of screen throughout the session.
removing gradient artifacts, a modified version of the original
algorithm proposed for this purpose was applied (Allen et al.
2000). Briefly, an artifact template was created by segmenting
and averaging the data according to the onset of each volume
and subtracted from the raw EEG data. The cardioballistic arti-
fact was removed by an average artifact subtraction method
(Allen et al. 1998). Specifically, R peaks were detected in the
low-pass-filtered ECG signal and used to establish a delayed
average artifact template over 21 consecutive heartbeat events
by sliding-window approach. The artifact was then subtracted
from the original EEG signal. After gradient and cardioballistic
artifacts were removed, the EEG data were low-pass filtered with
the cutoff set at 50 Hz, downsampled to 250 Hz, re-referenced
to the average reference, and exported to EEGLAB for further
processing (Delorme and Makeig 2004). Second-order blind iden-
tification (Belouchrani et al. 1993) was then applied to correct
for eye blinking, residual cardioballistic, and movement-related
artifacts. The artifact-corrected data were epoched from −300–
2000 ms with 0 ms denoting picture display onset. The prestim-
ulus baseline was defined as −300–0 ms for ERP analysis.
Single-Trial Estimation of fMRI-BOLD
Trial-by-trial picture-evoked BOLD signal was estimated by
using the beta series method (Mumford et al. 2012). In this
method, the trial of interest was represented by one regressor
and all the other trials were represented by another regressor.
Six motion regressors were also included to account for any
movement-related artifacts during scan. Repeating the process
for all the trials, we obtained the BOLD response to each
picture presentation in each brain voxel. These single-trial BOLD
responses were used in the MVPA decoding analysis.
ROIs in Retinotopic Visual Cortex
ROIs were defined according to a recently published probabilistic
visual retinotopic atlas (Wang et al. 2015). A total of 17 ROIs
in the retinotopic visual atlas were included: V1v, V1d, V2v,
V2d, V3v, V3d, V3a, V3b, hV4, ventral occipital (VO1), VO2, PHC1,
PHC2, lateral occipital (LO1), LO2, human middle temporal (hMT),
and intraparietal sulcus (IPS) (Fig. 3A). The homologous regions
from the two hemispheres were combined, and the IPS ROI was
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 5

Decoding Neural Representations of Affective Scenes
Bo et al.
3051
formed by combining the voxels from IPS0, IPS1, IPS2, IPS3, IPS4,
and IPS5. There were a total of 17 ROIs.
MVPA
MVPA was performed by the linear support vector machine
(SVM) method using the LibSVM package (http://www.csie.ntu.e
du.tw/&#x007E;cjlin/libsvm/) (Chang and Lin 2011). Single-trial
voxel patterns evoked by pleasant, unpleasant, and neutral pic-
tures were decoded in a pairwise fashion (e.g., pleasant vs.
neutral) within 17 retinotopic ROIs. The classification accuracy
was calculated by 10-fold validation. Specifically, all the data
was divided into 10 equal subdatasets, nine of which comprised
training data to train the classifier and the remaining one of
which was used for testing. The decoding accuracies of 10 such
procedures were averaged. To further ensure the stability of the
decoding result, we repeated 10-fold partition 100 times, con-
ducted the same procedure to acquire decoding accuracies for
each partition, and averaged the accuracies to yield the decoding
accuracy for each ROI. Repeating the process for each partici-
pant, group-level decoding accuracy was computed by averaging
individual accuracies across 20 participants. A nonparametric
permutation-based technique (Stelzer et al. 2013) was applied
to test whether the statistical significance of decoding accuracy
was above chance level for each ROI. At the individual subject
level, the class labels were randomly shuffled 100 times, and
each shuffled run generated one chance-level decoding accu-
racy. At the group level, one of the chance-level decoding accu-
racies was extracted randomly from each subject and averaged
across subjects. This process was repeated 105 times to obtain an
empirical distribution of the chance-level accuracy at the group
level for each ROI. The accuracy corresponding to P = 0.001 in
the probability distribution of the permutation test was used as
the threshold to determine whether decoding accuracy is above
chance level.
EC Via Directed Acyclic Graphs
Functional connectivity analysis is typically based on cross-
correlation analyses. Cross-correlation has a key limitation: It
does not provide directional information. To test the potential
sources of reentrant signals, we thus used an EC measurement
called the directed acyclic graph (DAG), derived from linear
non-Gaussian acyclic models (LiNGAM) (Shimizu et al. 2006,
2011). LiNGAM is a linear non-Gaussian variant of structural
equation modeling. It has been successfully applied in fMRI
work to assess EC (Schlösser et al. 2003; Marrelec et al. 2009;
Liu et al. 2015). Briefly, LiNGAM estimates causal order using
the recurrent regression method to find exogenous variables
in the system and analyze the connection strength via least
squares regression. The algorithm achieves better efficiency
when prior knowledge is provided. In the current work, given the
evidence from prior anatomical and causality studies showing
direct synaptic connection and significantly greater directional
connection from amygdala to the ventral visual system (Amaral
et al. 2003; Sabatinelli et al. 2014), we provided the prior knowl-
edge that signal in amygdala leads the directional connection
towards ventral visual cortex (VVC) to the algorithm. With such
prior knowledge, the estimation of LiNGAM is equivalent to
a structural equation model. The connection coefficient from
LiNGAM is used to represent EC strength.
Two types of EC analysis were considered: one based on a
priori considerations and the other a seed-based whole-brain
analysis. In the analysis based on the a priori considerations,
ROIs were the amygdala and the VVC. Amygdala ROI consisted
of two spherical masks of 5 mm in radius centered at [−16, 0,
−24] and [20, 0, −20] (Hamann et al. 2004). The VVC ROI consisted
of retinotopic visual regions VO1, VO2, PHC1, and PHC2. For the
seed-based whole-brain analysis, VVC was used as the seed, and
the EC into VVC was assessed for all the voxels in the brain.
ERP Analysis
The LPP was used here as an index of recurrent processing
among brain regions in the emotion network (Liu et al. 2012).
Preprocessed EEG data (see Data Preprocessing) was low-pass
filtered at 30 Hz and averaged within each picture category to
yield the ERP for that category. Figure 2C showed grand average
LPPs at Pz for the three categories of pictures (left) and the
topographic maps of LPP differences between affective scenes
and neutral scenes (right). Here, the choice of using Pz as the
site for estimating LPP was based on two considerations: (1) best
separation between emotional and neutral categories and (2)
balance between pleasant and unpleasant images. A paired t-
test comparing the two topographic maps in Figure 2C (right)
demonstrated that Pz met these two conditions. In addition
to grand average LPP, for each subject, the LPP amplitude was
obtained by using the time interval of 500 ms in duration around
the peak of LPP (Liu et al. 2012).
Results
Univariate Analysis of fMRI BOLD
Relative to neutral pictures, unpleasant pictures activated
bilateral
occipitotemporal
junctions,
pre/postcentral
gyrus,
bilateral ventral lateral prefrontal cortices, left orbital frontal
cortex, bilateral amygdalae/hippocampi, and insula (Fig. 2A).
Other activated areas included bilateral posterior parietal
cortices, fusiform gyrus, lingual gyrus, and temporal pole.
Pleasant pictures, relative to neutral pictures, activated bilateral
occipitotemporal junctions, bilateral posterior parietal cortices,
right amygdala/hippocampus, bilateral inferior frontal gyrus
(IFG), MPFC, and left orbital frontal cortex (Fig. 2B). Other
activated areas included fusiform gyrus, lingual gyrus, middle
frontal gyrus, and temporal pole. Thus, in addition to limbic
and
frontal
emotion-processing
structures,
both
pleasant
and unpleasant affective scenes, relative to neutral scenes,
more strongly engaged regions of the higher-order visual
cortex, consistent with previous reports (Lane et al. 1997;
Phan et al. 2002; Liu et al. 2012; see the review by Sabatinelli
et al. 2011). Statistically, the activation map in Figure 2 was
thresholded at P < 0.05, corrected for multiple comparisons by
the false discovery rate (FDR) method. The transformed effect
size of activation threshold is d = 0.62 (t = 2.78) for unpleas-
ant versus neutral and d = 0.63 (t = 2.82) for pleasant versus
neutral.
ERP Analysis
Grand average ERPs at Pz are shown for each of the three cat-
egories of pictures in Figure 2C. The LPP, starting ∼300 ms after
picture onset, was higher for pleasant and unpleasant pictures
compared with neutral pictures. A one-way analysis of variance
confirmed that LPP amplitude was significantly different among
the three conditions (F = 21.96, P < 0.05,η2
partial = 0.53). Post hoc
analysis confirmed that the mean LPP amplitudes for both
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 6

3052
Cerebral Cortex, 2021, Vol. 31, No. 6
Figure 2. Univariate fMRI and ERP analysis. (A) Activation map (P < 0.05, FDR) contrasting unpleasant versus neutral pictures. (B) Activation map (P < 0.05, FDR)
contrasting pleasant versus neutral pictures. (C) Grand average ERP (n = 20) at Pz showing ERP evoked by three classes of pictures (left) and scalp topography of LPP
enhancement (300–800 ms after picture onset). PPC, posterior parietal cortex; OFC, orbital frontal cortex; OTJ, occipitotemporal junction.
pleasant (1.972 ± 1.882 μV) and unpleasant (2.263 ± 2.052 μV)
pictures were significantly larger than that for neutral pictures
(0.781 ± 1.860 μV; pleasant vs. neutral: t(19) = 4.41, P < 0.001,
d = 0.99; unpleasant vs. neutral: t(19) =6.52, P < 0.001, d = 1.46); no
significant difference was found in LPP amplitude between the
pleasant and unpleasant categories (t(19) = 1.39, P = 0.18, d = 0.31).
The topographical maps depicting the scalp distribution of
differential LPP amplitudes are also shown in Figure 2C. This
distribution showed that LPP enhancement in pleasant versus
neutral and in unpleasant versus neutral was both characterized
by a centroparietal/centrofrontal distribution of positive voltage.
These findings are consistent with numerous previous reports
using the same paradigm (Cuthbert et al. 2000; Keil et al. 2001;
Schupp et al. 2003; Liu et al. 2012).
MVPA Analysis of fMRI BOLD
For MVPA, 17 retinotopic ROIs were selected according to a
recently published probabilistic atlas (Wang et al. 2015), includ-
ing V1d, V1v, V2d, V2v, V3v, V3d, hV4, VO1, VO2, PHC1, PHC2, hMT,
LO1, LO2, V3a, V3b, and IPS (Fig. 3A). The accuracy of decoding
between unpleasant and neutral and between pleasant and
neutral was shown for each ROI in Figure 3B. Across all visual
ROIs, both unpleasant versus neutral decoding as well as
pleasant versus neutral decoding accuracy was well above
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 7

Decoding Neural Representations of Affective Scenes
Bo et al.
3053
chance level, as determined by group-level random permutation
test (54% being the statistical threshold at P < 0.001), demon-
strating the presence of emotional signals in retinotopic visual
areas including V1.
For comparison, whereas univariate analysis identified six
ROIs (V3d, hMT, LO1, LO2, V3a, and IPS) as being more activated
in pleasant > neutral (P < 0.05, FDR corrected), and 11 ROIs
(V2v, V3v, V3d, hV4, VO1, VO2, LO1, LO2, hMT, V3a, and IPS) as
being more activated in unpleasant > neutral (P < 0.05, FDR cor-
rected), multivariate analysis revealed that decoding accuracy
in all 17 retinotopic visual ROIs were significantly above chance
level for both unpleasant versus neutral decoding and pleas-
ant versus neutral decoding, highlighting the importance of
multivoxel-level activity patterns in revealing the full extent of
emotional signaling in the retinotopic visual cortex (see Fig. 3C
for visualization of retinotopic visual regions revealed by uni-
variate vs. multivariate approaches as containing emotional
signals).
Affective pictures are often characterized along two dimen-
sions: valence and arousal. Relative to neutral pictures, pleasant
and unpleasant pictures are different both in terms of valence
as well as in terms of arousal. We attempted to control
for one of the two factors (i.e., normative arousal ratings)
by decoding between unpleasant and pleasant pictures. As
shown in Figure 4A, there was no significant difference in
normative arousal ratings between pleasant and unpleasant
pictures (P = 0.2, Fig. 4A), but normative valence ratings between
them was significantly different (P < 0.0001, Fig. 4A). Decoding
accuracy between the two classes of pictures in all the
retinotopic ROIs was significantly above chance level (Fig. 4B,
where 54% is the statistical threshold at P < 0.001 according to
a random permutation test), suggesting that the differences
in multivoxel patterns between pleasant versus neutral and
unpleasant versus neutral comparison were not simply driven
by emotional intensity of the stimuli.
Reentrant Modulation of Visual Representations of
Affective Scenes
It has been well established that viewing emotionally engaging
scenes is associated with facilitated visuocortical processing,
which can be measured by EEG, fMRI, and behavior. This facil-
itated processing is thought to be the consequence of reentrant
signals that arise from emotion-modulated deep brain struc-
tures such as the amygdala and back-project into the visual sys-
tem, in particular the VVC, to modulate visual processing. This
hypothesis would be supported and extended to the domain
of multivoxel neural representations if decoding accuracy in
retinotopic areas is parametrically related to evidence of feed-
back signaling. To examine this issue, we divided the retinotopic
ROIs into three broader visual regions based on consistency of
anatomical location and functional role: (1) early visual cortex
(EVC), located on the posterior portion of the occipital lobe and
involved in perception of basic visual features (Sereno et al.
1995; DeYoe et al. 1996; Engel et al. 1997), which included v1v,
v1d, v2v, v2d, v3v, v3d; (2) dorsal visual cortex (DVC), located
along dorsal parietal pathway and known to carry out motor and
high-order spatial functions such as motion perception, spatial
attention, and motor preparation (Bressler et al. 2008; Konen
and Kastner 2008; Wandell and Winawer 2011), which included
the combined ROIs of IPS; and (3) VVC, located along ventral
temporal pathway and known to be involved in object and
scene recognition (Brewer et al. 2005; Arcaro et al. 2009), which
included VO1, VO2, PHC1, and PHC2. The visualized anatom-
ical location of the three broader visual regions is shown in
Figure 5A. We expected that VVC, anatomically shown as the
visual structure that receives major feedback projections from
the medial temporal and frontal regions (Amaral et al. 2003;
Vuilleumier et al. 2004; Freese and Amaral 2005), would show sig-
nificant correlation between decoding accuracy and the strength
of signal reentry.
First, using LPP as an index of signal reentry, we correlated
the decoding accuracy in EVC, VVC, and DVC with LPP. As shown
in Figure 5B, for VVC, unpleasant versus neutral decoding accu-
racy and LPP amplitude were significantly correlated (R = 0.69,
P = 0.0008); pleasant versus neutral decoding accuracy in VVC
was also significantly correlated with LPP amplitude, albeit with
a smaller R value (R = 0.50, P = 0.026). LPP was not significantly
correlated with unpleasant versus neutral decoding accuracy in
either EVC (R = 0.37, P = 0.11) or DVC (R = 0.36, P = 0.12). Similarly,
LPP was not significantly correlated with pleasant versus neu-
tral decoding accuracy in either EVC (R = 0.34, P = 0.14) or DVC
(R = 0.29, P = 0.22).
Next, assessing the amygdala to VVC feedback more directly
via DAG, a measure of directed connectivity, we computed
amygdala→VVC EC and correlated it with the decoding accuracy
in VVC. Amygdala→VVC EC and VVC unpleasant versus
neutral decoding accuracy was significantly correlated (r = 0.66,
P = 0.001) (Fig. 5D, left), whereas amygdala→VVC EC and VVC
pleasant versus neutral decoding accuracy was not significantly
correlated (r = 0.27, P = 0.25) (Fig. 5D, right). We then conducted
a whole-brain EC analysis using VVC as the seed. EC from
each voxel in the brain to VVC was computed and correlated
with VVC decoding accuracy. Voxels with correlation coefficient
exceeding 0.61 (P < 0.005) and being part of a contiguous cluster
of >10 such voxels were considered significant. For pleasant
versus neutral comparison, as shown in Figure 6A, the potential
sources of reentrant signals are bilateral superior temporal
sulcus (STS)/superior temporal gyrus (STG) regions, right IFG,
and right ventral lateral prefrontal cortex (VLPFC), whereas for
unpleasant versus neutral comparison, the potential sources of
reentrant signals are the amygdala, agreeing with the result
from the ROI-based analysis, and the right STS/STG region
(Fig. 6C). To examine the collective contribution of the reentry
from these regions to the neural representations of emotional
pictures in VVC, we constructed a multiple regression model
using VVC decoding accuracy as the predicted variable and the
following ECs as the predictor variables: Pleasant: IFG→VVC,
VLPFC→VVC, and STS/STG→VVC; Unpleasant: Amygdala→VVC
and STS/STG→VVC. Mathematically, for pleasant, the model can
be written as: VVC decoding accuracy = β0+β1∗EC(IFG →VVC)+
β2 ∗EC(VLPFC →VVC)+β3 ∗EC(STS/STG →VVC)+ϵ; for unpleas-
ant, the model can be written as: VVC decoding accuracy =
β0+β1∗EC(Amygdala →VVC)+β2∗EC(STS/STG →VVC)+ϵ. Here,
EC stands for effective connectivity. As shown in Figure 6B and
D, the predicted decoding accuracy is strongly correlated with
actual VVC decoding accuracy (R = 0.95 for pleasant vs. neutral
decoding and R = 0.84 for unpleasant vs. neutral decoding,
P < 0.0001), demonstrating that a large portion of the variance
in VVC decoding accuracy can be explained by EC from anterior
temporal and prefrontal regions back to VVC.
A further analysis was carried out to test whether LPP as an
index of signal reentry is linearly related to the frontotemporal
EC to VVC. Again, a multiple regression model was used with LPP
as the predicted variable and ECs as the predictor variables. That
is, for Pleasant, LPP = β0 + β1 ∗EC(IFG →VVC) + β2 ∗EC(VLPFC →
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 8

3054
Cerebral Cortex, 2021, Vol. 31, No. 6
Figure 3. MVPA decoding analysis of neural representations of emotional scenes in retinotopic visual cortex. (A) Retinotopic ROIs visualized on the flattened brain. (B)
Group average decoding accuracy between unpleasant versus neutral and pleasant versus neutral in different ROIs. Dashed line indicates the statistical significance
threshold (54%). (C) Comparison between visual cortical contribution to the representation of affective scenes revealed by (top) univariate activation analysis (data
from Fig. 2A,B replotted here) and by (bottom) multivariate decoding from B.
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 9

Decoding Neural Representations of Affective Scenes
Bo et al.
3055
Figure 4. MVPA decoding of pleasant versus unpleasant scenes. (A) Normative valence and arousal ratings of unpleasant and pleasant images used in this study. The
error bar depicts the standard error of the mean for the normative ratings of 20 pictures in one category. Arousal is not significantly different between the two classes of
pictures, whereas pleasant pictures have significantly higher valence than unpleasant pictures. (B) Group average decoding accuracy between unpleasant and pleasant
in retinotopic ROIs. Dashed line indicates the statistical significance threshold (54%) at P < 0.001 according to a random permutation test.
VVC) + β3 ∗EC(STS/STG →VVC) + ϵ; and for Unpleasant, LPP =
β0 + β1 ∗EC(Amygdala →VVC) + β2 ∗EC(STS/STG →VVC) +
ϵ. The predicted LPP and the recorded LPP for pleasant pictures
and for unpleasant pictures were correlated at R = 0.63 (P = 0.002)
and R = 0.56 (P = 0.01), respectively. These results provide further
support to prior assertions that LPP is an index of signal reentry
and shed light on the specific frontotemporal sources of these
reentrant signals.
Picture Repetition Effects
In our paradigm, each of the 60 pictures was repeated five times
across five runs or sessions (Fig. 1). We tested whether there
were repetition effects on LPP amplitude and decoding accuracy
across the five runs. As shown in Figure 7A, LPP enhancement
across runs exhibited a slightly negative average slope, but
the slope was not significantly different from zero (pleasant
vs. neutral: t = −0.67, P = 0.51, d = 0.15; unpleasant vs. neutral:
t = −1.44, P = 0.17, d = 0.32). Linear fits to LPP enhancement across
runs at the individual participant level were shown in Figure 7B.
These results, indicating a lack of significant repetition effects
on LPP, were consistent with a previous report (Schupp et al.
2006). Decoding accuracy, averaged over all retinotopic regions,
was shown as a function of run in Figure 7C. Here, for a given
run, an SVM classifier was trained on the data from the other
four runs and tested on the data from the given run. The
average slope was again slightly negative, but was not signif-
icantly different from zero for either pleasant versus neutral
decoding (t = −1.48, P = 0.16, d = 0.33) or unpleasant versus neu-
tral decoding (t = −1.92, P = 0.07, d = 0.43). Linear fits to decoding
accuracy across runs at the individual participant level were
shown in Figure 7D. The negative slopes in Figure 7C, while
not statistically different from zero, were nevertheless associ-
ated with a small effect size, and may thus still prompt the
hypothesis that decoding accuracy declines with repetition over
runs.
Discussion
We examined the neural representations of affective scenes by
recording simultaneous EEG-fMRI from subjects viewing pleas-
ant, unpleasant, and neutral pictures from the IAPS library.
Consistent with previous reports, relative to neutral scenes,
both pleasant and unpleasant scenes evoked enhanced LPP on
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 10

3056
Cerebral Cortex, 2021, Vol. 31, No. 6
Figure 5. Relation between decoding accuracy and measures of signal reentry.
(A) Anatomical location of EVC, VVC, and DVC on flattened brain. (B) LPP –
decoding accuracy correlation for unpleasant versus neutral (left) and pleasant
versus neutral (right) in EVC, VVC, and DVC. Only decoding accuracy in VVC is
significantly correlated with LPP. (C) Scatter plots showing relationship between
LPP and decoding accuracy for unpleasant versus neutral (left) and pleasant
versus neutral (right) in VVC. (D) Relationship between amygdala→VVC effec-
tive connectivity (EC) and decoding accuracy in VVC. This relationship is only
significant in unpleasant versus neutral decoding (∗P < 0.05).
the scalp and stronger BOLD activation in a large-scale brain
network that included limbic and frontal structures as well as
higher-order visual cortices. Applying MVPA to retinotopic visual
ROIs, we further found that the multivoxel patterns evoked by
pleasant and unpleasant scenes were distinct from one another
and from those evoked by neutral scenes in all retinotopic visual
regions, including the primary visual cortex V1. Concurrently
recorded LPP amplitude, an electrophysiological index of recur-
rent signaling between anterior brain areas and visual cortex,
was shown to predict decoding accuracy in VVC. This was cor-
roborated by an EC analysis using DAG, which demonstrated that
for unpleasant scenes, the amygdala was a likely source of the
reentrant signals, whereas for the pleasant scenes, frontal lobe
structures including right IFG and right VLPFC were found to be
the likely sources of the reentrant signals.
Representation of Emotional Scenes in Retinotopic
Visual Cortex
The
canonical
network
selectively
activated
by
affective
scenes includes anterior temporal lobe, limbic structures,
and prefrontal cortex (Sabatinelli et al. 2011). Mixed findings,
however, have been reported regarding the involvement of
retinotopic visual areas in the representation of emotional
content.
Many
electrophysiological
studies
have
reported
differential retinotopic responses to emotional versus neutral
visual cues, both in human observers (Keil et al. 2003; Thigpen
et al. 2017; Li 2019) as well as in experimental animals (Li
et al. 2019). Similarly, the existence of emotion-specific signals
in retinotopic areas is predicted by theoretical work based
on animal model data (Amaral et al. 2003) as well as on
computational models (Kragel et al. 2019). By contrast, univariate
BOLD analyses of retinotopic ROIs, including all early visual
areas, tend to not show differences in activation as a function
of emotional content (Sabatinelli et al. 2009; meta-analysis in
Sabatinelli et al. 2011). This well-established finding was also
replicated in the present report, where retinotopic visual areas
as well as some higher-order visual cortices like PHC1, PHC2, and
V3b were found to be not differentially activated by emotional
pictures. Only after we applied multivariate techniques did
we find strong evidence for emotion-specific visuocortical
engagement across a wide range of retinotopic visual regions
including primary visual cortex V1.
In univariate fMRI analysis, for a voxel to be reported as
activated by an experimental condition, it needs to be consis-
tently activated across individuals. As such, individual differ-
ences in voxel activation patterns could lead to failure to detect
the presence of neural activity in a given region of the brain.
MVPA overcomes this limitation. In MVPA, multivoxel patterns
of activation within a ROI are the unit of analysis, and pattern
differences between experimental conditions are assessed at
the individual subject level, followed by summary statistics com-
puted at the population level (e.g., decoding accuracy averaged
across participants). In the past decade, studies have begun
to apply MVPA to paradigms where emotional stimuli were
used (Said et al. 2010; Sitaram et al. 2011; Baucom et al. 2012;
Kotz et al. 2013; Saarimäki et al. 2015; see Kragel and LaBar
2014 for review). Our study extends this line of research. When
multivoxel patterns of neural activation between emotion and
neutral pictures were compared, all retinotopic visual cortices,
including primary visual cortex, were shown to contain affective
signals.
Affective pictures are characterized along two dimensions:
valence and arousal. When decoding unpleasant versus pleas-
ant viewing conditions, in which emotional arousal ratings were
largely matched, it was found that the decoding accuracy was
above chance in all the visual ROIs, suggesting that valence-
specific information is encoded in retinotopic visual cortex. This
result is consistent with previous work showing that affective
valence modulates the gating of early visual input and scope
of sensory encoding (Schmitz et al. 2009). The observation that
valence-specific information is coded in visual areas is also
consistent with an emerging theoretical framework (Miskovic
and Anderson 2018; Todd et al. 2020), supported by multivariate
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 11

Decoding Neural Representations of Affective Scenes
Bo et al.
3057
Figure 6. VVC-seeded whole-brain effective connectivity analysis. (A) Brain maps showing voxels whose effective connectivity into VVC predicts VVC pleasant vs
neutral decoding accuracy. (B) Measured VVC pleasant vs neutral decoding accuracy vs predicted VVC pleasant vs neutral decoding accuracy according to a linear
model accounting for the collective contributions of reentry signaling from regions identified in panel A (see Results). (C) Brain maps showing voxels whose effective
connectivity into VVC predicts VVC unpleasant vs neutral decoding accuracy. (D) Measured VVC unpleasant vs neutral decoding accuracy vs predicted VVC unpleasant
vs neutral decoding accuracy according to a linear model accounting for the collective contributions of reentry signaling from regions identified in panel C (see Results).
STG, superior temporal gyrus; STS, superior temporal sulcus; IFG, inferior frontal gyrus; VLPFC, ventral lateral prefrontal cortex. All maps were thresholded at R > 0.61,
p < 0.005 and clusters containing more than 10 contiguous such voxels are shown.
analyses of fMRI data (Chikazoe et al. 2014), in which sen-
sory representations are inherently characterized by the valence
(pleasant and unpleasant) of the represented information (Sat-
pute et al. 2015) in modality-specific sensory areas (Shinkareva
et al. 2014). The neurophysiological implications of this view
continue to produce interesting questions for future research,
because sensory processing itself is an inherently parallel, dis-
tributed process (Nassi and Callaway 2009). Thus, although stim-
ulus valence may well be represented similarly to other sen-
sory dimensions extracted from the external world, hypothe-
ses regarding how specific neurocomputations encode these
physical and affective dimensions remain to be formulated and
tested. Using DAGs, the present study offers one avenue for link-
ing connectivity and decoding analyses to test such hypotheses.
Despite the promising results, we hasten to point out that the
number of stimuli used in the current study is rather small
(20 per category), and that in future studies, a wider range
of stimuli combined with more objective stimulus ratings are
required to further establish valence modulation of sensory
processing.
Although the IAPS pictures used in this study were carefully
selected to match for content and image composition, an
obvious question is whether the differences in multivoxel
patterns between different emotional categories are attributable
to differences in physical properties that are of a nonemotional
nature. To address this concern, we conducted a control
analysis by subdividing neutral pictures into pictures with
neutral people and pictures with neutral scenes. As shown
in
Supplementary Figure S1
of
the
supplementary
materi-
als, decoding accuracy between neutral people and neutral
scenes
was
at
chance
level
within all
retinotopic
visual
regions, suggesting that it is the emotional content of the
pictures
rather
than
the
physical/categorical
composition
(e.g., people vs. scenes) that determined the observed pattern
differences
in
the
retinotopic
regions
considered
in
this
study.
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 12

3058
Cerebral Cortex, 2021, Vol. 31, No. 6
Figure 7. Effects of picture repetition. (A) LPP enhancement as a function of run. (B) Linear fits to LPP as a function of run for each individual participant (n = 20). The
slopes were not significantly different from zero (P = 0.51 for pleasant vs. neutral and P = 0.17 for unpleasant vs. neutral). (C) Decoding accuracy as a function of run. (D)
Linear fits to decoding accuracy as a function of run for each individual participant (n = 20). The slopes were not significantly different from zero (P = 0.16 for pleasant
vs. neutral and P = 0.07 for unpleasant vs. neutral).
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 13

Decoding Neural Representations of Affective Scenes
Bo et al.
3059
Among all the visual ROIs considered here, the highest
decoding accuracy was consistently observed in LO regions LO1
and LO2. These regions are part of the lateral occipital complex
(LOC) and known for their role in object recognition (Larsson
and Heeger 2006). A recent fMRI–pupillometry study reports
that BOLD activity in LOC is modulated by the valence of the
stimulus (Kuniecki et al. 2018). Specifically, by superimposing
pink noise on IAPS pictures, these authors found greater
increase of LOC activity for unpleasant pictures compared
with neutral ones when the noise level is decreased. We
subdivided unpleasant scenes into attack scenes and disgust
scenes, pleasant scenes into happy people and erotic people,
and neutral scenes into neutral people and nature scenes. The
pairwise decoding accuracies of the six subcategories, shown
in Supplementary Table S3 of the supplementary materials,
showed that whereas any two subcategories belonging to two
different broad picture categories (e.g., pleasant vs. neutral)
are always decodable, the two subcategories within a broad
picture category are sometimes decodable (e.g., attack scenes
vs. disgust scenes within unpleasant) and sometimes not (e.g.,
neutral people vs. nature scenes within neutral). These results
suggest that the differences in distributed activities in LOC may
reflect both semantic differences as well as valence differences.
However, as pointed out above, the small number of stimuli
used in this study limits our ability to make strong inferences
regarding the specific role of LOC in object versus emotion
processing.
Role of Reentrant Signals in Visual Representations of
Emotion
Where do affective signals in retinotopic visual cortex come
from? One recent hypothesis stresses that visual cortex can
innately discriminate stimuli varying in affective significance
(see Miskovic and Anderson 2018 for a review). For example, both
animal model studies and human studies (Weinberger 2004;
Thigpen et al. 2017; Li et al. 2019) have found that sensory cortex
is able to encode the threat content of a visual stimulus, typically
after extensive learning. A recent computational study sup-
ported this hypothesis by showing that an artificial deep neural
network, whose training requires a large amount of stimuli with
repetition, has the ability to encode emotional content (Kragel
et al. 2019). In human observers, such differential sensitivity
to visual features associated with emotional content may be
acquired through daily experience (McTeague et al. 2018). How-
ever, given that the exemplars used in the present study were
novel for the participants and presented only five times across
the duration of the study, it is unlikely that retinotopic visual
cortex learned to represent individual features that are linked
to emotional significance during the course of the experimental
session. Thus, we examined the evidence for the alternative
hypothesis that affective signals in retinotopic areas emanate
from anterior frontotemporal structures via the mechanism of
reentry.
The signal reentry hypothesis proposes that when viewing
emotional stimuli, subcortical structures such as the amygdala,
upon receiving the initial sensory input, send feedback signals
into visual cortex to enhance the processing of the motiva-
tionally salient visual input (Keil et al. 2009; Sabatinelli et al.
2009; Lang and Bradley 2010; Pessoa 2010). Such enhanced visual
processing prompts increased vigilance towards appetitive or
aversive stimuli, ultimately promoting the deployment of adap-
tive action in the interest of survival. The reentry hypothesis
is indirectly supported by neuroanatomy studies showing feed-
back projections from the amygdala to the ventral visual stream
(Amaral et al. 2003; Freese and Amaral 2005). Patients with
amygdala lesion tend to show no visual cortex enhancement in
response to threat, even when their visual cortex is structurally
intact (Vuilleumier et al. 2004). In human imaging studies, it has
been shown that BOLD activation in amygdala precedes activa-
tion in visual cortex, and the functional connectivity between
amygdala and VVC is increased during affective picture viewing
(Sabatinelli et al. 2005, 2009). Analysis using Granger causality
further demonstrated heightened directional connectivity from
amygdala to fusiform cortex when viewing emotional scenes
(Sabatinelli et al. 2014; Frank et al. 2019).
To examine how signal reentry is affecting neural represen-
tations of affective pictures in retinotopic visual cortex, we first
used the LPP to index reentrant processing (Lang et al. 1998; Haj-
cak et al. 2006; Lang and Bradley 2010), which was well motivated
based on prior studies (Liu et al. 2012; Sabatinelli et al. 2013).
That the LPP amplitude was statistically significantly correlated
with decoding accuracy in VCC, but not in EVC and DVC, is
understandable from an anatomical perspective because VVC,
beginning at the anterior edge of V4 and extending anteriorly
to posterior PHC, receives extensive input from anterior tempo-
ral and frontal structures, and is thus expected to be strongly
influenced by these structures. Upon receiving reentrant feed-
back, VVC may also play the role of transmitting the reentrant
signals down to EVC. Functionally, given that VVC is involved in
object and scene perception, which is essential for the current
experimental paradigm requiring participants to perceive static
pictures with complex affective contents, the purpose of reentry
could be to selectively enhance the visual regions mostly related
to the ongoing task.
DVC contains higher-order visual cortex IPS along the dorsal
parietal pathway. In our data, decoding accuracy in DVC was
higher relative to VVC and EVC, but was not correlated with LPP
amplitude, suggesting that neural representations of emotional
content in DVC was not influenced by reentry indexed by LPP.
Neuroscientifically, DVC is known to play essential roles in
visual spatial attention, motion perception, and motor prepara-
tion (Bressler et al. 2008; Wandell and Winawer 2011). A previous
study using naturalistic emotional videos (Goldberg et al. 2014)
reported a preferential activation in the dorsal parietal visual
stream, which, the authors hypothesized, was related to motor
preparation associated with emotionally salient information.
Our results can be seen as lending support to this hypothesis
by showing that affective stimuli evoke emotion-specific neural
patterns in dorsal association cortices that lie at the interface
between visual perception and motor preparation for survival-
relevant actions (Lang and Bradley 2010). Furthermore, along
with the findings in VVC, our results also suggest that viewing
emotional scenes prompts parallel emotional processes along
ventral and dorsal visual pathways, serving possibly different
functional purposes.
In addition to LPP amplitude, we also used inter-regional
EC as an index of reentry, with an initial emphasis on the
role of amygdala in generating the feedback signals. The suc-
cessful indexing for unpleasant emotion lent credence to the
idea that the reentrant signals arising from limbic structures
modulate the visuocortical representations of negative emotion.
Although this relationship is not observed when viewing pleas-
ant pictures, a further whole-brain level EC analysis indicated
that for pleasant scenes, the potential sources of reentrant
signals include bilateral STS/STG, right IFG, and right VLPFC.
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 14

3060
Cerebral Cortex, 2021, Vol. 31, No. 6
Interpreting this finding, we note that VLPFC has been consid-
ered part of the ventral affective system, which includes VLPFC,
MPFC, and amygdala (Dolcos and McCarthy 2006). Anatomi-
cally, VLPFC has strong connections with sensory areas as well
as emotion-modulated structures such as the amygdala and
orbitofrontal cortex (Carmichael and Price 1995a, 1995b; Petrides
and Pandya 2002; Kennerley and Wallis 2009). The VLPFC inte-
grates reward information and provides top-down signals to
sensory cortex to improve behavioral performance (Kennerley
and Wallis 2009). Right IFG is known to be involved both in cog-
nitive control tasks and in emotional processing by exerting top-
down control of STS/STG (Frye et al. 2010) and ventral sensory
stream (Tops and Boksem 2011).
For unpleasant scenes, the whole-brain EC analysis again
revealed that the amygdala was an important source of reen-
trant feedback, along with STS/STG. Whereas the appearance
of amygdala in the whole-brain map agrees with and confirms
the ROI-based analysis, the appearance of the STS/STG region
in the brain map was a new finding; the same STS/STG region
appeared both in the processing of pleasant and unpleasant
scenes (Narumoto et al. 2001), suggesting that the STS/STG
region may serve as a way station, which transmits the sig-
nals received from the limbic and/or prefrontal structures to
visual cortex. Primate studies have found that STS/STG recipro-
cally interacts with the ventral visual stream (Cusick 1997; Alli-
son et al. 2000). In addition, STS/STG is structurally connected
with the amygdala from which it receives feedback projections
(Grezes et al. 2014; Pitcher et al. 2017). Thus, the present study
helps advance an interesting hypothesis for further studies
to test, which, by integrating animal model work, computa-
tional modeling, and advanced neuroimaging in humans, can
potentially lead to more precisely defined pathways of neural
feedback signaling in emotional scene perception.
In this work, both LPP and EC were used to index signal
reentry from frontotemporal cortices. That a large portion of LPP
variance was ECs from anterior structures such as amygdala and
VLPFC demonstrates that the two measures of signal reentry
are related, providing a connectivity-level neural substrate of
LPP, which in the previous studies has been mainly linked to
activations of distributed brain regions without regards to how
these regions functionally interact (Liu et al. 2012; Sabatinelli
et al. 2013).
Potential Effects of Picture Repetition
The repetition effects in emotion scene perception are usually
studied by presenting the same affective picture in consecutive
trials or repeatedly within the same block of trials (Ferrari et al.
2011; Bradley et al. 2015). These studies have consistently found
reduced but still robust emotional responses evoked by repeated
picture presentations. The effects of picture repetition across
blocks, as is the case here, have been shown to be small. For
example, Schupp et al. (2006) showed the same 40 IAPS images
over 90 runs with the order of presentation varying in each run
and found that emotional enhancement measured by ERPs did
not vary across runs. We replicated the Schupp et al. (2006) find-
ings by showing that the LPP amplitude did not systematically
change across subsequent runs. The effects of picture repetition
on fMRI decoding accuracy have not been studied before. Across
five runs, the decoding accuracy as a function of run exhibited a
negative slope. Although the negative slope is not significantly
different from zero, it nevertheless prompts the need to further
examine the possible hypothesis in future studies, employing
larger number of runs and subjects, which decoding accuracy
between different categories of affective scenes could decrease
over runs.
Summary and Outlook
We recorded simultaneous EEG-fMRI from participant viewing
natural images containing affective scenes. Applying MVPA
to fMRI data, we found the presence of affective signals in
the entire retinotopic visual cortex, including V1. Using scalp
potential LPP as indices of recurrent signaling between anterior
brain regions and visual cortex, emotion-sensitive neural
representations in the ventral portion of retinotopic visual
cortex were found to be related to signal reentry from anterior
brain structures. Further analysis using EC identified the sources
of these reentrant signals, which include amygdala and STS/STG
in the case of unpleasant scene processing and IFG, VLPFC, and
STS/STG in the case of pleasant scene processing.
The present analyses focused on the nature and origin of
fMRI voxel pattern signatures during emotional picture view-
ing. Analysis of EEG data was limited to the estimation of LPP,
which was used to index recurrent processing among visual and
extravisual regions. Future work focusing on the EEG data in
greater detail may address questions concerning the temporal
dynamics of affective scene processing. In this vein, a recent EEG
study (Greene and Hansen 2020) suggests that the perception
of naturalistic scenes can be decomposed into multiple stages,
where processing of low-level visual features is associated with
early visual ERPs, whereas the processing of high-level visual
features is associated with late visual ERPs. To what extent
similar temporal profiles apply to affective scene perception is
unknown. Leveraging the temporal resolution of EEG and spatial
resolution of fMRI, the current data is expected to shed light on
this question.
Supplementary Material
Supplementary material can be found at Cerebral Cortex online.
Notes
Conflict of Interest: None declared.
Funding
National Institutes of Health (grant R01 MH112558).
References
Allen PJ, Josephs O, Turner R. 2000. A method for removing imag-
ing artifact from continuous EEG recorded during functional
MRI. Neuroimage. 12(2):230–239.
Allen PJ, Polizzi G, Krakow K, Fish DR, Lemieux L. 1998. Iden-
tification of EEG events in the MR scanner: the problem of
pulse artifact and a method for its subtraction. Neuroimage.
8(3):229–239.
Allison T, Puce A, McCarthy G. 2000. Social perception from
visual cues: role of the STS region. Trends Cogn Sci. 4(7):
267–278.
Amaral DG, Behniea H, Kelly JL. 2003. Topographic organization
of projections from the amygdala to the visual cortex in the
macaque monkey. Neuroscience. 118(4):1099–1120.
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 15

Decoding Neural Representations of Affective Scenes
Bo et al.
3061
Arcaro MJ, McMains SA, Singer BD, Kastner S. 2009. Retino-
topic organization of human ventral visual cortex. J Neurosci.
29(34):10638–10652.
Baucom LB, Wedell DH, Wang J, Blitzer DN, Shinkareva SV.
2012. Decoding the neural representation of affective states.
Neuroimage. 59(1):718–727.
Belouchrani A, Abed-Meraim K, Cardoso JF, Moulines E. 1993.
Second-order blind separation of temporally correlated
sources. In: Proc Int Conf on Digital Sig Proc, Cyprus. p. 346–351.
Bradley MM. 2009. Natural selective attention: orienting and
emotion. Psychophysiology. 46(1):1–11.
Bradley MM, Codispoti M, Cuthbert BN, Lang PJ. 2001. Emo-
tion and motivation I: defensive and appetitive reactions in
picture processing. Emotion. 1(3):276.
Bradley MM, Costa VD, Ferrari V, Codispoti M, Fitzsimmons JR,
Lang PJ. 2015. Imaging distributed and massed repetitions of
natural scenes: spontaneous retrieval and maintenance. Hum
Brain Mapp. 36(4):1381–1392.
Bradley MM, Keil A, Lang PJ. 2012. Orienting and emotional
perception: facilitation, attenuation, and interference. Front
Psychol. 3:493.
Bradley MM, Lang PJ. 1994. Measuring emotion: the self-
assessment manikin and the semantic differential. J Behav
Ther Exp Psychiatry. 25(1):49–59.
Bradley MM, Sabatinelli D, Lang PJ, Fitzsimmons JR, King W,
Desai P. 2003. Activation of the visual cortex in motivated
attention. Behav Neurosci. 117(2):369.
Bressler SL, Tang W, Sylvester CM, Shulman GL, Corbetta M.
2008. Top-down control of human visual cortex by frontal
and parietal cortex in anticipatory visual spatial attention.
J Neurosci. 28(40):10056–10061.
Brewer AA, Liu J, Wade AR, Wandell BA. 2005. Visual field maps
and stimulus selectivity in human ventral occipital cortex.
Nat Neurosci. 8(8):1102–1109.
Bush KA, Inman CS, Hamann S, Kilts CD, James GA. 2017. Dis-
tributed neural processing predictors of multi-dimensional
properties of affect. Front Hum Neurosci. 11:459.
Cacioppo
JT, Crites
SL, Gardner
WL, Berntson
GG. 1994.
Bioelectrical echoes from evaluative categorizations: I. A
late positive brain potential that varies as a function of
trait negativity and extremity. J Pers Soc Psychol. 67(1):
115.
Carmichael ST, Price JL. 1995a. Limbic connections of the orbital
and medial prefrontal cortex in macaque monkeys. J Comp
Neurol. 363:615–641.
Carmichael ST, Price JL. 1995b. Sensory and premotor connec-
tions of the orbital and medial prefrontal cortex of macaque
monkeys. J Comp Neurol. 363:642–664.
Chang CC, Lin CJ. 2011. LIBSVM: a library for support vector
machines. ACM Trans Intell Syst Technol. 2(3):27.
Chikazoe J, Lee DH, Kriegeskorte N, Anderson AK. 2014. Popula-
tion coding of affect across stimuli, modalities and individu-
als. Nat Neurosci. 17(8):1114–1122.
Cusick CG. 1997. The superior temporal polysensory region in
monkeys. In: Rockland K, Kaas JH, Peters A, editors, Cerebral
Cortex, vol. 12. New York: Plenum Press, pp. 435–468.
Cuthbert BN, Schupp HT, Bradley MM, Birbaumer N, Lang PJ.
2000. Brain potentials in affective picture processing: covaria-
tion with autonomic arousal and affective report. Biol Psychol.
52(2):95–111.
Delorme A, Makeig S. 2004. EEGLAB: an open source toolbox for
analysis of single-trial EEG dynamics including independent
component analysis. J Neurosci Methods. 134(1):9–21.
DeYoe EA, Carman GJ, Bandettini P, Glickman S, Wieser JO, Cox
R, Miller D, Neitz J. 1996. Mapping striate and extrastriate
visual areas in human cerebral cortex. Proc Natl Acad Sci.
93(6):2382–2386.
Dolcos F, McCarthy G. 2006. Brain systems mediating cog-
nitive interference by emotional distraction. J Neurosci.
26(7):2072–2079.
Engel SA, Glover GH, Wandell BA. 1997. Retinotopic organiza-
tion in human visual cortex and the spatial precision of
functional MRI. Cereb Cortex. 7(2):181–192.
Ethofer T, Van De Ville D, Scherer K, Vuilleumier P. 2009. Decod-
ing of emotional information in voice-sensitive cortices. Curr
Biol. 19(12):1028–1033.
Ferrari V, Bradley MM, Codispoti M, Lang PJ. 2011. Repetitive
exposure: brain and reflex measures of emotion and atten-
tion. Psychophysiology. 48(4):515–522.
Frank DW, Costa VD, Averbeck BB, Sabatinelli D. 2019. Directional
interconnectivity of the human amygdala, fusiform gyrus,
and orbitofrontal cortex in emotional scene perception. J
Neurophysiol. 122(4):1530–1537.
Frank DW, Sabatinelli D. 2017. Primate visual perception: moti-
vated attention in naturalistic scenes. Front Psychol. 8:226.
Freese JL, Amaral DG. 2005. The organization of projections
from the amygdala to visual cortical areas TE and V1 in the
macaque monkey. J Comp Neurol. 486(4):295–317.
Frye RE, Wu M-H, Liederman J, McGraw Fisher J. 2010. Greater
pre-stimulus effective connectivity from the left inferior
frontal area to other areas is associated with better phono-
logical decoding in dyslexic readers. Front Syst Neurosci. 4:156.
Goldberg H, Preminger S, Malach R. 2014. The emotion–action
link? Naturalistic emotional stimuli preferentially activate
the human dorsal visual stream. Neuroimage. 84:254–264.
Greene MR, Hansen BC. 2020. Disentangling the independent
contributions of visual and conceptual features to the spa-
tiotemporal dynamics of scene categorization. J Neurosci.
40(27):5283–5299.
Grezes J, Valabregue R, Gholipour B, Chevallier C. 2014. A direct
amygdala-motor pathway for emotional displays to influ-
ence action: a diffusion tensor imaging study. Hum Brain
Mapp. 35(12):5974–5983.
Hajcak G, Moser JS, Simons RF. 2006. Attending to affect:
appraisal strategies modulate the electrocortical response to
arousing pictures. Emotion. 6(3):517.
Hamann S, Herman RA, Nolan CL, Wallen K. 2004. Men and
women differ in amygdala response to visual sexual stimuli.
Nat Neurosci. 7(4):411–416.
Kang D, Liu Y, Miskovic V, Keil A, Ding M. 2016. Large scale func-
tional brain connectivity during emotional engagement as
revealed by beta-series correlation analysis. Psychophysiology.
53(11):1627–1638.
Keil A, Bradley MM, Hauk O, Rockstroh B, Elbert T, Lang PJ. 2002.
Large-scale neural correlates of affective picture processing.
Psychophysiology. 39(5):641–649.
Keil A, Gruber T, Müller MM, Moratti S, Stolarova M, Bradley
MM, Lang PJ. 2003. Early modulation of visual perception by
emotional arousal: evidence from steady-state visual evoked
brain potentials. Cogn Affect Behav Neurosci. 3(3):195–206.
Keil A, Müller MM, Gruber T, Wienbruch C, Stolarova M, Elbert
T. 2001. Effects of emotional arousal in the cerebral hemi-
spheres: a study of oscillatory brain activity and event-
related potentials. Clin Neurophysiol. 112(11):2057–2068.
Keil A, Sabatinelli D, Ding M, Lang PJ, Ihssen N, Heim S. 2009.
Re-entrant projections modulate visual cortex in affective
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 16

3062
Cerebral Cortex, 2021, Vol. 31, No. 6
perception: evidence from Granger causality analysis. Hum
Brain Mapp. 30(2):532–540.
Kennerley SW, Wallis JD. 2009. Reward-dependent modulation
of working memory in lateral prefrontal cortex. J Neurosci.
29(10):3259–3270.
Kragel PA, LaBar KS. 2014. Advancing emotion theory with mul-
tivariate pattern classification. Emotion Review. 6(2):160–174.
Kragel PA, Reddan MC, LaBar KS, Wager TD. 2019. Emotion
schemas are embedded in the human visual system. Sci Adv.
5(7):eaaw4358.
Konen CS, Kastner S. 2008. Representation of eye movements
and stimulus motion in topographically organized areas of
human posterior parietal cortex. J Neurosci. 28(33):8361–8375.
Kotz SA, Kalberlah C, Bahlmann J, Friederici AD, Haynes JD. 2013.
Predicting vocal emotion expressions from the human brain.
Hum Brain Mapp. 34(8):1971–1981.
Kuniecki M, Wołoszyn K, Domagalik A, Pilarczyk J. 2018. Disen-
tangling brain activity related to the processing of emotional
visual information and emotional arousal. Brain Struct Funct.
223(4):1589–1597.
Lane
RD,
Reiman
EM,
Bradley
MM,
Lang
PJ,
Ahern
GL,
Davidson RJ, Schwartz GE. 1997. Neuroanatomical corre-
lates of pleasant and unpleasant emotion. Neuropsychologia.
35(11):1437–1444.
Lang PJ, Bradley MM. 2010. Emotion and the motivational brain.
Biol Psychol. 84(3):437–450.
Lang PJ, Bradley MM, Cuthbert BN. 1997. International Affective
Picture System (IAPS): technical manual and affective ratings.
Gainesville, Florida, USA: NIMH Center for the Study of Emo-
tion and Attention, pp. 39–58.
Lang PJ, Bradley MM, Fitzsimmons JR, Cuthbert BN, Scott JD,
Moulder B, Nangia V. 1998. Emotional arousal and activa-
tion of the visual cortex: an fMRI analysis. Psychophysiology.
35(2):199–210.
Lang PJ, Greenwald MK, Bradley MM, Hamm AO. 1993. Looking at
pictures: affective, facial, visceral, and behavioral reactions.
Psychophysiology. 30(3):261–273.
Larsson J, Heeger DJ. 2006. Two retinotopic visual areas in human
lateral occipital cortex. J Neurosci. 26(51):13128–13142.
Li W. 2019. Perceptual mechanisms of anxiety and its disorders.
In: Olatunji BO, editor. The Cambridge handbook of anxiety
and related disorders. Cambridge, United Kingdom: Cambridge
University Press, pp. 59–88.
Li Z, Yan A, Guo K, Li W. 2019. Fear-related signals in the primary
visual cortex. Curr Biol. 29(23):4078–4083.
Liu Y, Huang H, McGinnis-Deweese M, Keil A, Ding M. 2012.
Neural substrate of the late positive potential in emotional
processing. J Neurosci. 32(42):14563–14572.
Liu Y, Wu X, Zhang J, Guo X, Long Z, Yao L. 2015. Altered effective
connectivity model in the default mode network between
bipolar and unipolar depression based on resting-state fMRI.
J Affect Disord. 182:8–17.
Marrelec G, Kim J, Doyon J, Horwitz B. 2009. Large-scale neural
model validation of partial correlation analysis for effective
connectivity investigation in functional MRI. Hum Brain Mapp.
30(3):941–950.
McTeague LM, Gruss LF, Keil A. 2015. Aversive learning shapes
neuronal orientation tuning in human visual cortex. Nat
Commun. 6:7823.
McTeague LM, Laplante M-C, Bulls HW, Shumen JR, Lang PJ,
Keil A. 2018. Face perception in social anxiety: visuocortical
dynamics reveal propensities for hypervigilance or avoid-
ance. Biol Psychiatry. 83(7):618–628.
Miskovic V, Anderson A. 2018. Modality general and modal-
ity specific coding of hedonic valence. Curr Opin Behav Sci.
19:91–97.
Miskovic V, Keil A. 2012. Acquired fears reflected in cor-
tical sensory processing: a review of electrophysiological
studies of human classical conditioning. Psychophysiology.
49(9):1230–1241.
Mumford JA, Turner BO, Ashby FG, Poldrack RA. 2012. Deconvolv-
ing BOLD activation in event-related designs for multivoxel
pattern classification analyses. Neuroimage. 59(3):2636–2643.
Narumoto J, Okada T, Sadato N, Fukui K, Yonekura Y. 2001.
Attention to emotion modulates fMRI activity in human right
superior temporal sulcus. Cogn Brain Res. 12(2):225–231.
Nassi JJ, Callaway EM. 2009. Parallel processing strategies of the
primate visual system. Nat Rev Neurosci. 10(5):360–372.
Norman KA, Polyn SM, Detre GJ, Haxby JV. 2006. Beyond mind-
reading: multi-voxel pattern analysis of fMRI data. Trends
Cogn Sci. 10(9):424–430.
Norris CJ, Chen EE, Zhu DC, Small SL, Cacioppo JT. 2004. The
interaction of social and emotional processes in the brain.
J Cogn Neurosci. 16:1818–1829.
Pastor MC, Bradley MM, Löw A, Versace F, Moltó J, Lang PJ. 2008.
Affective picture perception: emotion, context, and the late
positive potential. Brain Res. 1189:145–151.
Peelen MV, Atkinson AP, Vuilleumier P. 2010. Supramodal rep-
resentations of perceived emotions in the human brain. J
Neurosci. 30(30):10127–10134.
Pessoa L. 2010. Emotion and cognition and the amygdala:
from “what is it?” to “what’s to be done?”. Neuropsychologia.
48(12):3416–3429.
Pessoa L, McKenna M, Gutierrez E, Ungerleider LG. 2002. Neural
processing of emotional faces requires attention. Proc Natl
Acad Sci. 99(17):11458–11463.
Petrides M, Pandya DN. 2002. Comparative cytoarchitectonic
analysis of the human and the macaque ventrolateral pre-
frontal cortex and corticocortical connection patterns in the
monkey. Eur J Neurosci. 16:291–310.
Phan KL, Wager T, Taylor SF, Liberzon I. 2002. Functional neu-
roanatomy of emotion: a meta-analysis of emotion activation
studies in PET and fMRI. Neuroimage. 16(2):331–348.
Phelps EA, Ling S, Carrasco M. 2006. Emotion facilitates per-
ception and potentiates the perceptual benefits of attention.
Psychol Sci. 17(4):292–299.
Pitcher D, Japee S, Rauth L, Ungerleider LG. 2017. The superior
temporal sulcus is causally connected to the amygdala: a
combined TBS-fMRI study. J Neurosci. 37(5):1156–1161.
Saarimäki H, Gotsopoulos A, Jääskeläinen IP, Lampinen J,
Vuilleumier P, Hari R, Sams M, Nummenmaa L. 2015. Dis-
crete neural signatures of basic emotions. Cereb Cortex.
26(6):2563–2573.
Sabatinelli D, Bradley MM, Fitzsimmons JR, Lang PJ. 2005. Parallel
amygdala and inferotemporal activation reflect emotional
intensity and fear relevance. Neuroimage. 24(4):1265–1270.
Sabatinelli D, Fortune EE, Li Q, Siddiqui A, Krafft C, Oliver
WT, Beck S, Jeffries J. 2011. Emotional perception: meta-
analyses of face and natural scene processing. Neuroimage.
54(3):2524–2533.
Sabatinelli D, Frank DW, Wanger TJ, Dhamala M, Adhikari BM,
Li X. 2014. The timing and directional connectivity of human
frontoparietal and ventral visual attention networks in emo-
tional scene perception. Neuroscience. 277:229–238.
Sabatinelli D, Keil A, Frank DW, Lang PJ. 2013. Emotional per-
ception: correspondence of early and late event-related
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


## Page 17

Decoding Neural Representations of Affective Scenes
Bo et al.
3063
potentials with cortical and subcortical functional MRI. Biol
Psychol. 92(3):513–519.
Sabatinelli D, Lang PJ, Bradley MM, Costa VD, Keil A. 2009. The
timing of emotional discrimination in human amygdala and
ventral visual cortex. J Neurosci. 29(47):14864–14868.
Said CP, Moore CD, Engell AD, Todorov A, Haxby JV. 2010. Dis-
tributed representations of dynamic facial expressions in the
superior temporal sulcus. J Vis. 10(5):11.
Sato W, Kochiyama T, Yoshikawa S, Naito E, Matsumura M.
2004. Enhanced neural activity in response to dynamic
facial expressions of emotion: an fMRI study. Cogn Brain Res.
20(1):81–91.
Satpute AB, Kang J, Bickart KC, Yardley H, Wager TD, Barrett LF.
2015. Involvement of sensory regions in affective experience:
a meta-analysis. Front Psychol. 6:1860.
Schlösser R, Gesierich T, Kaufmann B, Vucurevic G, Hunsche S,
Gawehn J, Stoeter P. 2003. Altered effective connectivity dur-
ing working memory performance in schizophrenia: a study
with fMRI and structural equation modeling. Neuroimage.
19(3):751–763.
Schmitz TW, De Rosa E, Anderson AK. 2009. Opposing influ-
ences of affective state valence on visual cortical encoding.
J Neurosci. 29(22):7199–7207.
Schupp HT, Cuthbert BN, Bradley MM, Cacioppo JT, Ito T, Lang
PJ. 2000. Affective picture processing: the late positive poten-
tial is modulated by motivational relevance. Psychophysiology.
37(2):257–261.
Schupp HT, Markus J, Weike AI, Hamm AO. 2003. Emotional
facilitation of sensory processing in the visual cortex. Psychol
Sci. 14(1):7–13.
Schupp HT, Stockburger J, Codispoti M, Junghöfer M, Weike
AI, Hamm AO. 2006. Stimulus novelty and emotion percep-
tion: the near absence of habituation in the visual cortex.
Neuroreport. 17(4):365–369.
Sereno MI, Dale AM, Reppas JB, Kwong KK, Belliveau JW, Brady
TJ, Rosen BR, Tootell RB. 1995. Borders of multiple visual
areas in humans revealed by functional magnetic resonance
imaging. Science. 268(5212):889–893.
Shimizu S, Hoyer PO, Hyvarinen A, Kerminen A. 2006. A linear
non-Gaussian acyclic model for causal discovery. J Mach Learn
Res. 7:2003–2030.
Shimizu S, Inazumi T, Sogawa Y, Hyvärinen A, Kawahara Y,
Washio T, Hoyer PO, Bollen K. 2011. DirectLiNGAM: a direct
method for learning a linear non-Gaussian structural equa-
tion model. J Mach Learn Res. 12:1225–1248.
Shinkareva SV, Wang J, Kim J, Facciani MJ, Baucom LB, Wedell
DH. 2014. Representations of modality-specific affective pro-
cessing for visual and auditory stimuli derived from func-
tional magnetic resonance imaging data. Hum Brain Mapp.
35(7):3558–3568.
Sitaram R, Lee S, Ruiz S, Rana M, Veit R, Birbaumer N. 2011. Real-
time support vector classification and feedback of multiple
emotional brain states. Neuroimage. 56(2):753–765.
Stelzer J, Chen Y, Turner R. 2013. Statistical inference and mul-
tiple testing correction in classification-based multi-voxel
pattern analysis (MVPA): random permutations and cluster
size control. Neuroimage. 65:69–82.
Thigpen NN, Bartsch F, Keil A. 2017. The malleability of emo-
tional perception: short-term plasticity in retinotopic neu-
rons accompanies the formation of perceptual biases to
threat. J Exp Psychol Gen. 146(4):464–471.
Todd RM, Miskovic V, Chikazoe J, Anderson AK. 2020. Emo-
tional objectivity: neural representations of emotions and
their interaction with cognition. Annu Rev Psychol. 71(1):
25–48.
Tops M, Boksem MA. 2011. A potential role of the infe-
rior frontal gyrus and anterior insula in cognitive control,
brain rhythms, and event-related potentials. Front Psychol. 2:
330.
Vuilleumier P. 2005. How brains beware: neural mechanisms of
emotional attention. Trends Cogn Sci. 9(12):585–594.
Vuilleumier P, Richardson MP, Armony JL, Driver J, Dolan RJ.
2004. Distant influences of amygdala lesion on visual cortical
activation during emotional face processing. Nat Neurosci.
7(11):1271.
Wandell BA, Winawer J. 2011. Imaging retinotopic maps in the
human brain. Vision Res. 51(7):718–737.
Wang L, Mruczek RE, Arcaro MJ, Kastner S. 2015. Probabilistic
maps of visual topography in human cortex. Cereb Cortex.
25(10):3911–3931.
Weinberger NM. 2004. Specific long-term memory traces in
primary auditory cortex. Nat Rev Neurosci. 5(4):279–290.
Downloaded from https://academic.oup.com/cercor/article/31/6/3047/6137655 by Institute for int'l & area studies user on 12 January 2026


