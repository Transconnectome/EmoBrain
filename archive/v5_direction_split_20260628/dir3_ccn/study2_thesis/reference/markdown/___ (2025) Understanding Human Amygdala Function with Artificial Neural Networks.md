# *** (2025) Understanding Human Amygdala Function with Artificial Neural Networks

**Source:** *** (2025) Understanding Human Amygdala Function with Artificial Neural Networks.pdf

---

## Page 1

Behavioral/Cognitive
Understanding Human Amygdala Function with Artiﬁcial
Neural Networks
Grace Jang1 and
Philip A. Kragel1,2
1Neuroscience Graduate Program, Emory University, Atlanta, Georgia 30322 and 2Department of Psychology, Emory University, Atlanta, Georgia 30322
The amygdala is a cluster of subcortical nuclei that receives diverse sensory inputs and projects to the cortex, midbrain, and other
subcortical structures. Numerous accounts of amygdalar contributions to social and emotional behavior have been offered, yet an
overarching description of amygdala function remains elusive. Here, we adopt a computationally explicit framework that aims to
develop a model of amygdala function based on the types of sensory inputs it receives, rather than individual constructs such as
threat, arousal, or valence. Characterizing human fMRI signal acquired as male and female participants viewed a full-length
ﬁlm, we develop encoding models that predict both patterns of amygdala activity and self-reported valence evoked by naturalistic
images. We use deep image synthesis to generate artiﬁcial stimuli that distinctly engage encoding models of amygdala subregions
that systematically differ from one another in terms of their low-level visual properties. These ﬁndings characterize how the
amygdala compresses high-dimensional sensory inputs into low-dimensional representations relevant to behavior.
Key words: amygdala; arousal; emotion; encoding; fMRI; valence
Signiﬁcance Statement
The amygdala is a cluster of subcortical nuclei critical for motivation, emotion, and social behavior. Characterizing the
contribution of the amygdala to behavior has been challenging due to its structural complexity, broad connectivity, and
functional heterogeneity. Here, we use a combination of human neuroimaging and computational modeling to investigate
how visual inputs relate to low-dimensional representations encoded in the amygdala. We ﬁnd that the amygdala encodes
an array of visual features, which systematically vary across speciﬁc nuclei and relate to the affective properties of the sensory
environment.
Introduction
Animals navigate complex environments which contain diverse
threats and opportunities for reward. Succeeding at this task
depends on the amygdaloid complex—a subcortical cluster of
nuclei in the medial temporal lobe (Swanson and Petrovich,
1998; Murray and Wise, 2004). The amygdala receives inputs
from multiple sensory modalities (McDonald, 1998; Sah et al.,
2003; Janak and Tye, 2015) and is a convergence zone with
connections to much of the cortex, subcortex, and midbrain
systems involved in motivated behavior and autonomic control
(Pessoa and Adolphs, 2010). The primate amygdala receives
information about the environment predominantly from the
ventral visual stream (Pessoa and Adolphs, 2010; Kravitz et al.,
2013). Through computations performed on these and other
inputs, the amygdala is thought to detect events of biological
relevance and prepare animals to react appropriately (Sander
et al., 2003; Cunningham and Brosch, 2012).
Human neuroimaging has shed light on amygdala function by
examining its sensitivity to diﬀerences in reward, threat, valence,
salience, and aﬀective intensity. Typical experiments identify
associations between diﬀerent stimulus properties and amygdala
responses. Meta-analytic summaries of this work show that the
amygdala is sensitive to a wide array of biologically relevant inputs
(Costafreda et al., 2008; Vytal and Hamann, 2010; Lindquist et al.,
2012, 2016; Kragel and LaBar, 2016). One explanation of these
ﬁndings is that the amygdala is involved in multiple functions
and that diﬀerent neural ensembles process diﬀerent stimulus
properties relevant to distinct behaviors. However, identifying
the set of variables that best explain amygdala function has been
a challenge, as most studies only manipulate one or a few variables
at a time, limiting strong inferences about amygdala specialization.
An alternative way to understand amygdala function is
through systems identiﬁcation. This approach involves building
Received July 29, 2024; revised Jan. 7, 2025; accepted Jan. 16, 2025.
Author contributions: G.J. and P.A.K. designed research; G.J. and P.A.K. performed research; G.J. and P.A.K.
analyzed data; G.J. and P.A.K. wrote the paper.
This work was partially supported by grants from the NIH (R01MH134972 to P.A.K.) and (T32NS096050 to G.J.).
The authors declare no competing ﬁnancial interests.
Correspondence should be addressed to Philip A. Kragel at pkragel@emory.edu.
https://doi.org/10.1523/JNEUROSCI.1436-24.2025
Copyright © 2025 Jang and Kragel
This is an open-access article distributed under the terms of the Creative Commons Attribution 4.0
International license, which permits unrestricted use, distribution and reproduction in any medium provided that
the original work is properly attributed.
1–11 • The Journal of Neuroscience, April 30, 2025 • 45(18):e1436242025


## Page 2

models of a system from measurements of its inputs and outputs.
From this perspective, a complete understanding of amygdala
function would comprise a model that transforms amygdala
inputs (e.g., projections originating in the ventral visual stream)
onto output variables conveyed to downstream structures (e.g., the
hypothalamus, striatum, and midbrain structures). Compared to
conventional approaches that involve manipulating a small num-
ber of variables and measuring changes in amygdala activity, sys-
tems identiﬁcation requires experiments with complex sensory
inputs that better match the diversity of amygdala inputs. The per-
formance of computational models that predict amygdala
responses to a given set of sensory inputs provides a metric for
quantifying our understanding of brain function.
Here, we probe multiple aspects of amygdala function from a
systems identiﬁcation perspective. Given evidence that the major-
ity of sensory inputs to the primate amygdala originate from the
ventral visual cortex (Kravitz et al., 2013), we predict that a com-
putational proxy of the ventral stream should be suﬃcient to pre-
dict amygdala responses to emotionally evocative stimuli. Because
sensory inputs predominantly project to the basal and lateral
nuclei, whereas other nuclei are involved in diﬀerent functions,
prediction accuracy should systematically diﬀer across amygdala
subregions. We test these predictions using a combination of
human neuroimaging, computational models of visual processing,
and self-reported emotion. We analyze human brain responses to a
full-length motion picture ﬁlm (Aliko et al., 2020) and develop lin-
ear encoding models to predict amygdala responses using a deep
convolutional neural network (Kragel et al., 2019) trained to recog-
nize the emotional content of scenes.
We validate these models in two in silico experiments focused
on prediction and control. First, we examine whether the models
predict valence and arousal ratings in response to naturalistic
images from two aﬀective image databases (Bradley and Lang,
2007; Kurdi et al., 2017). Second, we use deep image synthesis
(Nguyen et al., 2016; Bashivan et al., 2019) to generate visual sti-
muli that maximally engage amygdala subregions and subse-
quently identify which visual properties make them distinct.
Collectively, these tests establish a framework for understanding
amygdala function by characterizing how it transforms visual
inputs into low-dimensional representations that can be used
to guide behavior.
Materials and Methods
Development of amygdala encoding models
We ﬁt encoding models (Naselaris et al., 2011) to develop image-
computable models that take images presented to 10 male and 10 female
participants as inputs and predict amygdala responses (Fig. 1). Based on
anatomical and functional connectivity (Amaral and Price, 1984; Kravitz
et al., 2013), we used a deep convolutional neural network that approx-
imates the primate ventral visual stream (Kar et al., 2019) as it extracts
highly processed visual features that are fed forward into the lateral
amygdala. We ﬁt models using brain responses to naturalistic audiovi-
sual stimuli with rich socioemotional content known to engage the
amygdala. If these encoding models capture the responses of neural pop-
ulations that encode valence or arousal, they should be able to predict
normative self-report ratings of evocative stimuli and can be used to gen-
erate images that vary in aﬀective content.
Neuroimaging experiment. Functional magnetic resonance imaging
(fMRI) data for this study were sampled from the Naturalistic
Neuroimaging Database (Aliko et al., 2020). Detailed descriptions of
the participants, the paradigm used for data acquisition, and the prepro-
cessing of the fMRI data have been described elsewhere (Aliko et al.,
2020; Soderberg et al., 2023). Brieﬂy, blood oxygen level-dependent
(BOLD) data from 20 subjects viewing a full-length motion picture
ﬁlm 500 Days of Summer were previously collected in a 1.5 T Siemens
MAGNETOM Avanto with a 32-channel head coil (Siemens Healthcares)
and consequently used for this study.
Feature extraction. We used a deep convolutional neural network
trained to classify visual scenes into 20 emotion categories, EmoNet
(Kragel et al., 2019), as a feature extractor for encoding models. This
model was ﬁnetuned from AlexNet (Krizhevsky et al., 2012) to classify
emotional scenes and consists of ﬁve convolutional layers and three fully
connected layers. We passed every ﬁfth frame of the movie shown to par-
ticipants during scanning as inputs to EmoNet and extracted features
from the penultimate layer fc7 (i.e., activation in 4,096 units) because
this layer best approximates later stages of processing in the ventral visual
pathway (Horikawa and Kamitani, 2017; Kragel et al., 2019).
Figure 1.
Schematic of encoding model workﬂow. A full-length movie was shown to participants concurrent with fMRI and was input to a deep convolutional neural network to extract
features from frames of the video stimulus. Partial least squares regression identiﬁed a mapping between visual features and amygdala response patterns for each subject (N = 20). V1–V4, visual
areas 1–4; IT, inferotemporal cortex; conv, convolutional layer; fc, fully connected layer; PLS, partial least squares.
2 • J. Neurosci., April 30, 2025 • 45(18):e1436242025
Jang and Kragel • Modeling Amygdala Function


## Page 3

Regions of interest. We modeled patterns of fMRI signal localized to
amygdala masks based on cytoarchitecture (Amunts et al., 2005) and
included voxels in the bilateral amygdala (247–252 voxels) from the
basolateral complex (LB), the centromedial nucleus (CM), the superﬁcial
(SF) group, and the amygdalostriatal transition zone (AStr). The extent
of subregions ranged from 29 to 178 voxels. Some participants had par-
tial coverage in some regions of interest (4 out of 20 subjects had <252
voxels for the amygdala). We also ﬁt encoding models for two control
regions, namely, early cortical visual areas (V1–V3; 3,061–3,069 voxels)
and the inferotemporal cortex (TE2, TF; 700–1,010 voxels), examined
bilaterally as delineated by multimodal parcellation (Glasser et al., 2016).
Model speciﬁcation. After extracting the image features from the
movie using the activations from layer fc7 of EmoNet (4,096 dimensions),
we convolved these features to account for the hemodynamic time delay of
the BOLD data using a canonical double gamma response function
(Friston, 2007) and truncated the convolved variables to match the length
of BOLD time series. We used these variables to specify separate partial
least squares (PLS) regressions (Wold et al., 2001) for each subject to
obtain regression coeﬃcients (beta estimates) for encoding models. The
convolved image features from the movie formed the predictor block
and the observed BOLD activations masked by the voxels of the amygdala
and other control regions of interest formed the outcome block. We
explored more complex models which can account for variable hemody-
namic responses (Nishimoto et al., 2011; Huth et al., 2012; Lescroart
and Gallant, 2019), although we opted to use more parsimonious models
as performance did not substantially diﬀer. We speciﬁed one encoding
model for each region of interest (i.e., the amygdala, visual cortex, and
inferotemporal cortex) for each subject that predicts voxel-wise activations
in response to the dynamic visual stimuli. Model performance was
assessed in each of the three regions, in four anatomically deﬁned amyg-
dala subregions, and in voxel-wise mapping.
Model estimation and evaluation. After specifying these encoding
models, we ﬁt mappings between visual features and BOLD response pat-
terns using partial least squares regression. This was accomplished using
the plsregress function in MATLAB, which uses the SIMPLS algorithm.
Regression models were regularized by constraining the model to 20
latent dimensions instead of using the full dimensionality of the predic-
tor block (which was on the order of 1,000 dimensions). This value was
selected a priori, and diﬀerent dimensionalities were not explored.
Performance was quantiﬁed as the correlation between voxel-wise
encoding model predictions and the observed BOLD time series for
each subject. We used ﬁvefold cross-validation with a random partition-
ing of all data for each subject to estimate generalization error (Kohavi,
1995). We calculated the correlation between the predicted and observed
activations for each voxel and normalized the correlation coeﬃcients
using the Fisher transformation for group inference.
Statistical inference. To assess whether performance was above
chance levels, we conducted one-sample t tests on voxel-wise and region-
average data. Voxel-wise inference was performed using false discovery
rate correction (Benjamini and Hochberg, 1995) with a threshold of
q < 0.05. To test for diﬀerences in predictive performance across amygdala
subregions, we performed a one-way repeated measures ANOVA. We spe-
ciﬁed planned contrasts that compared the performance of amygdala
encoding models in the LB subregion with other amygdala subregions
(CM, SF, and AStr), the performance of the CM subregion to the SF and
AStr subregions, and the performance in the SF subregion to the AStr
subregion.
Evaluating encoding model responses to affective images
We validated encoding models to determine whether their predicted acti-
vations would behave similarly to human brains—exhibiting increased
engagement along the dimensions of valence or arousal (Lindquist et al.,
2016). This was accomplished using naturalistic images from standardized
aﬀective image databases [i.e., the International Aﬀective Picture System
(IAPS; Bradley and Lang, 2007) and the Open Aﬀective Standardized
Image Set (OASIS; Kurdi et al., 2017)], and testing whether predicted acti-
vations in response to these images varied in terms of valence and arousal.
Because it is well-established that diﬀerences in low-level visual properties
are associated with alterations in valence and arousal in these databases
(Anders et al., 2008; Styliadis et al., 2014; Bonnet et al., 2015; Hartling
et al., 2021), we also accounted for variation with low-level visual features,
namely, color (red, green, blue) and spatial power (high and low spatial
frequencies).
We used the naturalistic images as inputs to encoding models and
tested for associations with normative valence and arousal ratings
and their interactions. We performed this analysis on both the IAPS
and OASIS datasets. For each of the seven regions, the responses to every
image for each of the 20 encoding models (one per subject) were obtained
by multiplying the activation produced in layer fc7 of EmoNet with the
regression coeﬃcients of that subject’s encoding model (sampling
responses from 140 encoding models total). We obtained the normative
valence and arousal ratings for each of the naturalistic images. Because
the amygdala is particularly sensitive to low frequency information
(Delplanque et al., 2007) and the images in these databases systematically
vary in terms of their color content, we then extracted the low-level visual
features of color intensity (red, blue, and green) and spectral power (high
and low frequencies). We produced color histograms for each IAPS and
OASIS image and calculated the median value for each color. We calcu-
lated the power spectral density of each image using fast Fourier trans-
form and then deﬁned low frequencies as those with a radius <6 pixels
in Fourier space and high frequency as those with a radius >24 pixels.
To test for associations with valence and arousal, we conducted linear
regressions with predicted voxel-wise activations and the region averages
of predictions as the outcome variable. Standardized valence ratings;
arousal ratings; the interaction between valence and arousal (coded such
that more positive and arousing images would produce the strongest
response in an encoding model); median intensity of red, green, and
blue; and the power in high- and low-spatial frequency bands comprised
the eight predictor variables in the regression. We used the ﬁtlme function
in the MATLAB Statistics and Machine Learning Toolbox (The
MathWorks Inc., 2024) to build the models for each subject and performed
second-level group t tests on the eight betas of interest, treating the subject
as a random variable.
Controlling amygdala encoding model responses using deep image
synthesis
After verifying the performance of our encoding models on naturalistic
images, we wanted to synthesize artiﬁcial stimuli that could engage the
encoding models of the amygdala and diﬀerent amygdala subregions.
Previous studies have demonstrated related approaches can target activa-
tion to speciﬁed units within the visual cortex in both humans and non-
human primates (Nguyen et al., 2016; Bashivan et al., 2019; Xiao and
Kreiman, 2020; Wang and Ponce, 2022). Here, we extended this method
to generate artiﬁcial stimuli that would target the amygdala (Fig. 2). We
used a deep generator network trained on ImageNet (Nguyen et al., 2016)
and the outputs of encoding models separately ﬁt on each region of inter-
est to map activation in layer fc7 of EmoNet as the objective for activation
maximization. This was accomplished by computing the dot product
with diﬀerent sets of encoding model coeﬃcients (beta estimates) that
predicted the responses of diﬀerent amygdala voxels. Optimization was
performed using an evolutionary algorithm (Wang and Ponce, 2022)
implemented in Python (https://github.com/Animadversio/ActMax-
Optimizer-Dev). We used this procedure to generate artiﬁcial stimuli tar-
geting the average amygdala response, individual amygdala subregions
(LB, CM, SF, and AStr), visual cortex, and inferotemporal cortex.
Artiﬁcial stimuli were generated with a random starting seed for each
image. The optimization algorithm did not converge for some seeds
(producing an identical image); these images were excluded from subse-
quent analyses. As a result, 4–5 diﬀerent artiﬁcial stimuli were generated
for each region of interest for each subject, resulting in 80 artiﬁcial sti-
muli synthesized per region of interest. An exception to this was the
artiﬁcial stimuli generated for the inferotemporal cortex; because it
was used as a control region, 8–9 artiﬁcial stimuli were generated for
each subject resulting in a total of 160 artiﬁcial stimuli for this region.
To assess the selectivity of encoding models, we assessed whether
they responded diﬀerentially to generated stimuli optimized for diﬀerent
Jang and Kragel • Modeling Amygdala Function
J. Neurosci., April 30, 2025 • 45(18):e1436242025 • 3


## Page 4

regions of interest. Following the same procedures used to evaluate the
naturalistic stimuli, we fed the artiﬁcial stimuli (n = 686) into all encod-
ing models and obtained a predicted activation for each of the artiﬁcial
stimuli. We also characterized low-level visual features such as color
(red, blue, and green) and spectral power (high and low frequencies)
found in the synthesized artiﬁcial stimuli. We performed linear
mixed-eﬀects regressions on standardized variables for the low-level
visual features to conﬁrm that the synthesized images activated their
intended targets. We ﬁt mixed-eﬀects regressions for each subject with
a target region for image synthesis (on vs oﬀtarget), the subject used
for image synthesis, and the low-level visual features described above
as predictors for within-subject ﬁxed eﬀects. Separate regressions were
run to predict the activation of the amygdala, each of its subregions
(LB, CM, SF, and AStr), and the visual cortex. We used the ﬁtlme func-
tion in MATLAB (The MathWorks Inc., 2024) for estimation and made
inference on regression betas with t tests.
To evaluate the discriminability of artiﬁcial stimuli, we performed a
supervised classiﬁcation and examined confusions between the predicted
and actual region targeted for optimization. Multiway classiﬁcation
models were estimated using partial least squares discriminant analyses
with seven latent dimensions. Generalization performance was estimated
using leave-one-subject-out cross-validation, in which classiﬁers were
trained on data from all but one subject and tested on data from the
remaining participant. Confusions between diﬀerent image classes
were assessed using a hierarchical approach in a seven-way classiﬁcation,
with the number of clusters set to be the maximum number of clusters in
which all pairs of clusters are statistically discriminable from one
another. To visualize the results of this analysis, we generated a t-SNE
plot (van der Maaten and Hinton, 2008) based on the model predictions
for each of the artiﬁcial stimuli.
A randomization test of the same procedure was repeated for amyg-
dala subregions. In this test, we randomly assigned each amygdala voxel
to one of four sets and averaged the encoding model betas for each ran-
dom subregion to create a synthetic stimulus. This procedure was
repeated 1,000 times to construct a two-tailed 95% conﬁdence interval
based on the percentile method for comparison.
Results
We found that visual features captured by deep convolutional neu-
ral networks are encoded in amygdala responses to naturalistic,
dynamic videos. Voxel-wise validation tests showed that the
mean performance of encoding models was well above chance
(Fig. 3). A mixed-eﬀects model revealed that the average
predicted amygdala response was above chance (ˆb = 0.046,
SD = 0.023,t(19) = 9.17,p< 0.001)andthat there weremarkeddiﬀer-
ences in performance across amygdala subregions (ΔBIC = 23.5,
likelihood ratio = 36.5, p < 0.001). Conﬁrmatory analyses demon-
strated
successful
prediction
in
early
visual
(ˆb = 0.2174,
SD= 0.0349, t(19)= 27.86, p < 0.001) and inferotemporal cortex
(ˆb = 0.0727, SD = 0.0283, t(19) = 11.49, p < 0.001).
Model comparisons revealed diﬀerences in predictive
performance across subregions. The ﬁrst planned contrast
comparing LB to the other three subregions did not result in
statistical signiﬁcance (ˆb = −0.0012, SE = 0.0012, t(53) = −1.04,
p = 0.304). The other two contrasts indicated diﬀerences between
the performances of CM and the average of SF and AStr
(ˆb = 0.0036, SE = 0.0015, t(53) = 2.39, p = 0.020) and between
the SF and AStr (ˆb = 0.017, SE = 0.0026, t(53) = 6.47, p < 0.001).
Post hoc tests indicated that there were diﬀerences between
CM and AStr (ˆb = 0.027, SE = 0.0050, z = 5.45, p < 0.001), SF
and AStr (ˆb = 0.033, SE = 0.0050, z = 6.64, p < 0.001), SF and
LB (ˆb = 0.018, SE = 0.0054, z = 3.33, p = 0.005), and LB and
AStr (ˆb = 0.015, SE = 0.0054, z = 2.84, p = 0.023), but not
between CM and LB or between SF and CM. Thus, the sets of
voxels in SF and CM exhibited the highest performance, followed
by voxels in LB, and then the voxels in AStr.
To further quantify the ability of the model to characterize
amygdala response patterns, we compared the performance of
the voxel-wise encoding model to one trained to predict the average
response of all amygdala voxels. Consistent with the observed
diﬀerences in performance across subregions, the voxel-wise
encoding model performed better than the model based on the
average amygdala response [t(19) = 7.62, p < 0.001, SD= 0.0204,
95% CI= (0.0252, 0.0443)]. Together, this ﬁnding and comparisons
between subregions demonstrate that the multivariate encoding
model captures meaningful variation in amygdala response across
voxels above and beyond the region’s average response.
Predicting the response of amygdala-based models along
dimensions of valence and arousal
We validated our encoding models on aﬀective images from the
IAPS and OASIS datasets that have been shown to produce
increases in amygdala activity (Britton et al., 2006; Haj-Ali et
al., 2020; Hartling et al., 2021) along the dimensions of valence
(Garavan et al., 2001; Anders et al., 2004, 2008; Mather et al.,
2004; Aldhafeeri et al., 2012; Styliadis et al., 2014) and arousal
in humans (Canli et al., 2000; Kensinger and Schacter, 2006).
Consistent with previous fMRI studies that show increased
amygdala responses to positively valent stimuli, we found that
the amygdala encoding model captured linear increases in
valence (ˆb = 0.0097, t(19) = 3.17, p = 0.005, d = 0.71; Fig. 4).
Encoding model responses did not track arousal (ˆb = 0.0011,
t(19) = 0.34, p = 0.740, d = 0.08) or the interaction between valence
and arousal (ˆb = −0.0034, t(19) = −1.44, p = 0.166, d = −0.32).
Moreover, we found that the high-frequency spatial power
(ˆb = 0.0246, t(19) = 3.24, p = 0.004, d = 0.72) and marginally the
amount of red color within images (ˆb = 0.0067, t(19) = 2.07,
p = 0.053, d = 0.46) also predicted activations in amygdala models.
Figure 2.
Artiﬁcial image synthesis procedure. A deep generator network (DGN; blue arrow) initialized with a random code produces an artiﬁcial stimulus (yellow) that is fed as input into the
encoding model (red arrow). Beta estimates specifying the relationship between unit activity in the deep convolutional network and BOLD response patterns serve as the target for activation
maximization. Forward and backpropagation update the code to modify and generate an artiﬁcial stimulus that maximizes activation patterns in the target region. up, upconvolutional layer;
conv, convolutional layer; fc, fully connected layer.
4 • J. Neurosci., April 30, 2025 • 45(18):e1436242025
Jang and Kragel • Modeling Amygdala Function


## Page 5

Given recent ﬁndings from multivariate decoding studies
demonstrating that the amygdala encodes valence along a single
dimension that ranges from unpleasantness to pleasantness (Jin
et al., 2015; Tiedemann et al., 2020), we performed a series of
regressions examining associations with valence separately for
negative (z < 0), neutral (absolute value of z < 1), and positive
(z > 1) images. If the amygdala encoding model predicts valence
across the full valence spectrum using a single continuous
Figure 3.
ANN-based encoding models predict human amygdala responses to naturalistic videos. a, Amygdala activation is predicted by encoding models ﬁt on naturalistic videos (group
t-statistic computed on the cross-validated correlation between predicted and observed BOLD responses). Maps are displayed with a threshold of qFDR < 0.05. b, Rendering of amygdala par-
cellation (Julich–Brain Cytoarchitectonic Atlas). Blue, LB, laterobasal; yellow, SF, superﬁcial; orange, CM, centromedial; green, AStr, amygdalostriatal. c, Violin plots of average predictive per-
formance of encoding models in each subregion. Each point corresponds to a single subject (N = 20). Error bars reﬂect the standard error of the mean. *p < 0.05, ** p < 0.01, *** qFDR < 0.05.
Figure 4.
Amygdala encoding model responses to standardized aﬀective images. The predicted response to images from the International Aﬀective Picture System (IAPS) and the Open
Aﬀective Standardized Image Set (OASIS) are shown. Predictions were generated from regression models predicting responses based on valence, arousal, and the interaction between valence
and arousal. Surface plots show responses averaged across the entire amygdala, visual cortex, and within amygdala subregions.
Jang and Kragel • Modeling Amygdala Function
J. Neurosci., April 30, 2025 • 45(18):e1436242025 • 5


## Page 6

representation, then we would expect all three regressions to
exhibit a positive relationship. Alternatively, the amygdala may
encode coarse-grained diﬀerences in valence extremes using a
discontinuous function, consistent with bivalent models of
aﬀect (Bradburn, 1969; Watson and Tellegen, 1985; Cacioppo
et al., 2012; Mattek et al., 2017).
Consistent with the latter hypothesis, we found amygdala
encoding models respond to valence in a piecewise, discontinu-
ous manner. Increasingly negative images produced greater
activations in the encoding model (ˆb = −0.0136, t(19) = −2.51,
p = 0.021, d = −0.56). Valence coding shifted within the neutral
range, as more positive images produced greater activations
(ˆb = 0.0182, t(19) = 4.34, p < 0.001, d = 0.97). This coding contin-
ued for more extreme positive images, as they produced greater
activations in the encoding model (ˆb = 0.0144, t(19) = 2.78,
p = 0.012, d = 0.62). These results suggest that the encoding
model captures coarse-grained diﬀerences between valence
extremes and a more ﬁne-grained, nonlinear representation of
valence.
As our overarching hypothesis is that the amygdala functions
to select among many possible behaviorally relevant sensory
features, we next examined whether aﬀective variables encoded
in the activity of the visual cortex diﬀered from those of amygdala
responses. Examining
relationships
between visual cortex
encoding model predictions and normative aﬀective variables,
we found a positive association with valence (ˆb = 0.0201,
t(19) = 5.33,
p < 0.001,
d = 1.19)
and
arousal
(ˆb = 0.0130,
t(19) = 3.50, p = 0.002, d = 0.78) and a signiﬁcant interaction
(ˆb = −0.025, t(19) = −8.06, p < 0.001, d = −1.80), such that the
encoding model responded more with increasing arousal for
negative compared with positive stimuli. These results are
broadly consistent with data showing that amygdala feedback
modulates early visual responses (Liu et al., 2022) and that the
visual cortex encodes representations of multiple aﬀective vari-
ables (Miskovic and Anderson, 2018; Kragel et al., 2019; Li
et al., 2019; Bo et al., 2021).
To evaluate whether amygdala and visual cortex encoding of
aﬀective variables diﬀered, we compared the strength of associa-
tions between regions. The amygdala encoding models had weaker
associations
with
both
valence
(ˆb = −0.010,
t(19)= −2.40,
p = 0.027, d = −0.54) and arousal (ˆb = −0.012, t(19)= −2.78,
p = 0.012, d = −0.62) compared with visual cortex models.
Similarly, the amygdala models exhibited a weaker (less negative)
interaction between valence and arousal compared with the visual
cortex encoding models (ˆb = 0.0219, t(19) = 6.09, p < 0.001,
d = 1.36).
Given the functional heterogeneity of the amygdala and past
evidence demonstrating interactions between valence and
arousal (Winston et al., 2005), we next tested whether there
were diﬀerences in the encoding of valence and its interaction
with arousal in amygdala subregions. To this end, we ﬁt separate
encoding models for each amygdala subregion. We performed
ANOVAs comparing activations between subregions and found
that responses related to valence did not diﬀer across subregions
(F(1,19) = 3.82,
p = 0.066), whereas
the
interaction
between
valence and arousal varied across subregions (F(1,19) = 7.34,
p = 0.014). Exploratory post hoc tests did not reveal any signiﬁ-
cant eﬀects after correcting for multiple comparisons, although
AStr and LB demonstrated a diﬀerence with a modest eﬀect
size [ˆb = 0.0045, SE = 0.0023, p = 0.249, 95% CI = (−0.0021,
0.0111), d = −0.432; Table 1].
To characterize functional heterogeneity without assuming a
single, ﬁxed anatomical delineation of the amygdala, we next eval-
uated whether there were voxel-wise diﬀerences in the encoding of
valence, arousal, and their interaction. Consistent with gross diﬀer-
ences in subregion-average ﬁndings, voxel-wise correlations varied
across the extent of the amygdala. Correlations between valence
and voxel-wise predictions were generally positive (Fig. 5), with
peaks in the basolateral amygdala [MNIx,y,z = (29, −2, −26),
t(19) = 3.23, p = 0.004, and MNIx,y,z = (−23, −5, −17), t(19) = 2.34,
p = 0.030]. We also found correlations between arousal and
voxel-wise predictions for positive eﬀects in the basolateral amyg-
dala [MNIx,y,z = (38, −2, −23), t(19)= 3.23, p = 0.004]. Additionally,
we found negative correlations between model predictions and
the interaction between valence and arousal, such that voxels in
basolateral amygdala had larger responses to negative, intense
images [MNIx,y,z = (−26, −2, −17), t(19) = −2.96, p = 0.008, and
MNIx,y,z = (23, 2, −14), t(19) = −2.95, p = 0.008].
Controlling encoding models of distinct amygdala subregions
To further evaluate regional speciﬁcity, we generated artiﬁcial sti-
muli optimized to activate anatomically deﬁned amygdala subre-
gions (i.e., LB, SF, AStr, and CM amygdala; Fig. 6). We then
compared the activity produced by on- versus oﬀ-target artiﬁcial
stimuli within the respective encoding models in validation tests.
This analysis revealed that artiﬁcial stimuli selectively engaged
on-target subregions compared with oﬀ-target subregions (AStr:
ˆb = 0.026,
t(19) = 4.51,
p < 0.001,
d = 1.01.
CM:
ˆb = 0.031,
t(19) = 5.97,
p < 0.001,
d = 1.33.
LB:
ˆb = 0.009,
t(19)= 2.24,
p = 0.037, d = 0.50), with the exception of SF (ˆb = 0.025,
t(19) = 1.39, p = 0.180, d = 0.31). A supervised classiﬁcation analysis
revealed all image types were distinct from one another in pairwise
comparisons, with the exception of the artiﬁcial stimuli generated
to target the LB and SF subregions. The six distinct image clusters
could be discriminated from one another in a six-way classiﬁcation
with 71.7 ± 1.7% (SE) accuracy (chance accuracy= 21.96 ± 16.4%),
demonstrating a high degree of functional specialization (Fig. 7).
Finally, we veriﬁed that the stimulus generation was based on
local patterning within the amygdala as opposed to arbitrary
structure in EmoNet. We performed an additional control anal-
ysis in which we compared the discriminability of stimuli target-
ing amygdala subregions to that of stimuli targeting randomly
selected sets of amygdala voxels. Images targeting anatomically
deﬁned subregions could be classiﬁed with a four-way accuracy
Table 1. Eﬀects of valence and arousal on amygdala subregions
Subregion
Valence (main eﬀect)
Valence by arousal (interaction)
Coeﬃcient
SE
p
Cohen’s d
Coeﬃcient
SE
p
Cohen’s d
LB
0.0069
0.0028
0.022
0.56
−0.0043
0.0017
0.024
−0.55
SF
0.0026
0.0077
0.745
0.07
−0.0076
0.0063
0.245
−0.27
CM
0.0071
0.0037
0.070
0.43
−0.0075
0.0039
0.071
−0.43
AStr
0.0101
0.0035
0.010
0.64
−0.0088
0.0023
0.001
−0.86
LB, basolateral complex; SF, superﬁcial group; CM, centromedial nucleus; AStr, amygdalostriatal transition zone.
6 • J. Neurosci., April 30, 2025 • 45(18):e1436242025
Jang and Kragel • Modeling Amygdala Function


## Page 7

of 70.42 ± 5.4% (SE), whereas artiﬁcial stimuli targeting ran-
domly selected voxels were not discriminable above chance levels
[mean = 27.4%, 95% CI = (21.88%, 32.50%)].
Discussion
We found that amygdala processing can be characterized using a
systems identiﬁcation framework. Encoding models using fea-
tures from deep convolutional neural predicted BOLD activity
within multiple amygdala subregions during free viewing of a
cinematic ﬁlm. In independent validation tests, the amygdala
encoding model consistently responded to diﬀerences in valence
and its interaction with arousal, the amount of red color, and
high spatial frequency power of aﬀective images, consistent
with prior work investigating amygdala responses to these sti-
muli (Garavan et al., 2001; Anders et al., 2004, 2008; Styliadis
et al., 2014). Furthermore, stimuli synthesized to engage amyg-
dala subregions were visually distinct, alluding to diﬀerences in
the specialization of amygdala subregions. We take these ﬁndings
to show that one function of the amygdala is to transform sensory
inputs from the ventral visual stream to produce representations
related to valence.
Our ﬁndings demonstrate how encoding models can be used
to characterize the interface between sensory pathways and
downstream regions involved in cognition and emotion. A large
body of work has used hand-engineered (Jones and Palmer, 1987;
Lee, 1996; Dumoulin and Wandell, 2008) and data-driven
(Fukushima, 1988; Riesenhuber and Poggio, 1999) features to
characterize the primate visual system. Deep convolutional neu-
ral networks have been developed as models of the ventral visual
stream—providing a better match to the complexity of biological
systems underlying perception (Yamins and DiCarlo, 2016; Kar
et al., 2019). The existing literature work has generally focused
on identifying the best one-to-one mappings between speciﬁc
features and the responses of distinct visual areas to carefully
controlled stimuli, with the goal of identifying a fully mappable
model of the visual system (Yamins and DiCarlo, 2016) ranging
from the retina to the anterior temporal lobe. Here, we explored
mappings that diverge from ventral stream involvement in visual
recognition to characterize a system central to emotional beha-
vior, the amygdaloid complex (O’Neill et al., 2018).
Characterizing amygdala function using an encoding model
framework is a departure from common methods that involve
measuring amygdala responses to one or a few variables at a
time (Garavan et al., 2001; Anderson et al., 2003; Anders et al.,
2004, 2008; Kensinger and Schacter, 2006; Styliadis et al., 2014;
Figure 5.
Voxel-wise correlations between predicted amygdala responses and normative
valence, arousal, and their interaction. Group t-maps of the average cross-validated correlation
between predicted amygdala responses to images from the IAPS and OASIS datasets and the
dimensions of valence, arousal, and their interaction. Warm colors indicate positive correla-
tions, and cool colors indicate negative correlations.
Figure 6.
Representative artiﬁcial stimuli for amygdala subregions in three subjects.
LB, laterobasal amygdala; SF, superﬁcial amygdala; CM, centromedial amygdala; AStr, amyg-
dalostriatal transition area.
Jang and Kragel • Modeling Amygdala Function
J. Neurosci., April 30, 2025 • 45(18):e1436242025 • 7


## Page 8

Jin et al., 2015; Haj-Ali et al., 2020; Tiedemann et al., 2020).
Whereas conventional studies are built upon well-founded
assumptions that the amygdala is involved in processing speciﬁc
variables such as threat, reward, pleasure, and intensity, among
others, we relaxed these constraints and predicted that amygdala
responses can be approximated as an image-computable function
of signals present in the sensory array. Thus, although we did
not assume any speciﬁc variable was encoded in amygdala activity,
we found that amygdala encoding models were sensitive to varia-
tion in the normative valence and arousal evoked by images.
In line with our observation that the average response of the
amygdala encoding model increased from negative to positive
extremes of the valence continuum, recent multivariate decoding
studies have shown that the amygdala unidimensionally represents
the valence of odors (Jin et al., 2015) and images of food (Tiedemann
et al., 2020). Together, these ﬁndings are broadly consistent with
studies reporting the amygdala is involved in reward learning and
evaluating social images (Baxter and Murray, 2002; Adolphs and
Spezio, 2006). They are also congruent with work in nonhuman pri-
mates showing that both pleasant and unpleasant stimuli engage
distributed neural populations in the amygdala (Paton et al., 2006;
Belova et al., 2008) and with fMRI evidence showing that the amyg-
dala participates in a distributed network of brain regions sensitive
to ﬂuctuations in hedonic valence (Kragel et al., 2023).
In addition to variation related to valence extremes, we
observed nonlinearities in amygdala encoding model responses
to aﬀective images, such that responses were greater for highly
valent compared with neutral stimuli. This pattern of results
has been observed in response to olfactory (Winston et al.,
2005) and auditory (Fecteau et al., 2007) stimulation. Whereas
unidimensional coding of valence was widespread throughout
the amygdala, we found this interactive eﬀect modestly diﬀered
across amygdala subregions, with the largest eﬀect in the amyg-
dalostriatal transition area, a region that encodes the valence of
threatening stimuli and is important for the expression of condi-
tioned defensive behavior in nonhuman animal models (Goto
et al., 2022; Mills et al., 2022). It is possible that overlapping neu-
ral populations in the amygdala relate to valence in diﬀerent
ways, based on contextual factors that inﬂuence connectivity
with distributed brain networks (Gothard, 2020). For instance,
one recent study (Čeko et al., 2022) identiﬁed representations
of negative aﬀect from diﬀerent sensory origins (visually evoked
and domain-general across somatic, thermal, visual, and auditory
sources) and nonspeciﬁc arousal that were distributed across
brain systems, yet overlapped in the amygdala. The amygdala
activity captured by our encoding models could reﬂect visual-
speciﬁc or domain-general coding of aﬀect; adjudicating between
these alternatives requires further study that evaluates the gener-
alizability of encoding models across varied stimuli and contexts.
We found that stimuli generated to selectively engage amyg-
dala subregions were clustered such that stimuli generated to
engage the input centers of the amygdala (such as the LB) were
Figure 7.
ANN-generated stimuli selectively engage encoding models of diﬀerent regions of interest. a, t-SNE plot, (b) optimal clustering solution, and (c) normalized confusion matrix of
predicted activations of stimuli in encoding models color-coded by region of interest. The confusion matrix shows above chance performance. amy, whole amygdala; IT, inferotemporal cortex; VC,
visual cortex; AStr, amygdalostriatal transition zone; CM, centromedial nucleus; LB, basolateral complex; SF, superﬁcial group.
8 • J. Neurosci., April 30, 2025 • 45(18):e1436242025
Jang and Kragel • Modeling Amygdala Function


## Page 9

distinct from output centers of the amygdala (such as the CM and
AStr). This result is broadly consistent with models of amygdala
processing that suggest the amygdala identiﬁes a subset of sen-
sory variables that are relevant for learning and motivating beha-
vior (Pessoa, 2010; Sladky et al., 2024). However, the overall
distinctiveness of synthetic stimuli raises other possibilities.
Diﬀerences in synthetic stimuli could result from local processing
within the amygdala or connections to the amygdala that bypass
the basolateral complex and directly inﬂuence population activity
in downstream nuclei.
Despite exhibiting large eﬀect sizes, voxel-wise predictions
were far from explaining all amygdala activity. This is perhaps
unsurprising, given the complexity of the movie stimulus and
the relative simplicity of the encoding model used. We ﬁt encod-
ing models using the simplifying assumption of a common
hemodynamic response across individuals and amygdala subre-
gions. As we developed encoding models using static visual fea-
tures useful for classifying emotional scenes, amygdala responses
to emotional stimuli from other sensory modalities (e.g., auditory
and linguistic signals), those that habituated over time, or were
dependent on learning taking place over the course of the movie
stimulus could not be predicted using our approach. We antici-
pate that amygdala responses inﬂuenced by these factors can be
characterized using encoding models that incorporate additional
nonlinearities related to these processes, given connections
between the amygdala and brain regions involved in reinforce-
ment learning, audition, and language (Price, 2003; Koelsch
et al., 2013; Abivardi and Bach, 2017) and the success of compu-
tational models in characterizing the function of these systems
(Yamins and DiCarlo, 2016; Cross et al., 2021).
Amygdala encoding models were trained on the visual input of
one full-length motion picture ﬁlm, 500 Days of Summer, and on the
corresponding brain data of 20 subjects viewing this movie. This
full-length movie is suﬃciently complex with both positive and neg-
ative valence scenes, faces, and other visual content, although it may
have been limited in its ability to evoke robust and varied emotional
experiences, including acute fear (Hudson et al., 2020). Future stud-
ies using diﬀerent movies, videos, or other dynamic visual stimuli to
train encoding models are needed to identify the set of variables
encoded by the amygdala and to assess the extent to which they
are context dependent or generalize across stimulus types (Čeko
et al., 2022) and situations (Kragel et al., 2023).
In conclusion, our study shows that the amygdala encodes mul-
tiple features of visual stimuli, ranging from low-level features such
as color and spectral power to more complex features along the
dimension of valence, with marked diﬀerences between the features
that individual amygdala subregions represent. Thus, perhaps what
is driving the amygdala can be thought of as something beyond a
single dimension or a handful of constructs, but rather a large array
of features yet to be identiﬁed and objectively examined to under-
stand how the amygdala coordinates emotional behavior.
Data Availability
The fMRI data used to ﬁt encoding models are available at https://
openneuro.org/datasets/ds002837/versions/2.0.0. Data used for
ﬁne-tuning EmoNet are available upon request from https://
goo.gl/forms/XErJw9sBeyuOyp5Q2. Data relevant to this project
are available at https://osf.io/r48gc/.
Code Availability
Code for all analyses is available on GitHub at https://github.
com/ecco-laboratory/AMOD. The code used for implementing
EmoNet in Python is available at https://github.com/ecco-
laboratory/emonet-pytorch.
References
Abivardi A, Bach DR (2017) Deconstructing white matter connectivity of
human amygdala nuclei with thalamus and cortex subdivisions in vivo.
Hum Brain Mapp 38:3927–3940.
Adolphs R, Spezio M (2006) Role of the amygdala in processing visual social
stimuli. Prog Brain Res 156:363–378.
Aldhafeeri FM, Mackenzie I, Kay T, Alghamdi J, Sluming V (2012) Regional
brain responses to pleasant and unpleasant IAPS pictures: different net-
works. Neurosci Lett 512:94–98.
Aliko S, Huang J, Gheorghiu F, Meliss S, Skipper JI (2020) A naturalistic neu-
roimaging database for understanding the brain using ecological stimuli.
Sci Data 7:347.
Amaral DG, Price JL (1984) Amygdalo-cortical projections in the monkey
(Macaca fascicularis). J Comp Neurol 230:465–496.
Amunts K, Kedo O, Kindler M, Pieperhoff P, Mohlberg H, Shah NJ, Habel U,
Schneider F, Zilles K (2005) Cytoarchitectonic mapping of the human
amygdala, hippocampal region and entorhinal cortex: intersubject vari-
ability and probability maps. Anat Embryol 210:343–352.
Anders S, Eippert F, Weiskopf N, Veit R (2008) The human amygdala is sen-
sitive to the valence of pictures and sounds irrespective of arousal: an
fMRI study. Soc Cogn Affect Neurosci 3:233–243.
Anders S, Lotze M, Erb M, Grodd W, Birbaumer N (2004) Brain activity
underlying emotional valence and arousal: a response-related fMRI study.
Hum Brain Mapp 23:200–209.
Anderson AK, Christoff K, Stappen I, Panitz D, Ghahremani DG, Glover G,
Gabrieli JDE, Sobel N (2003) Dissociated neural representations of inten-
sity and valence in human olfaction. Nat Neurosci 6:196–202.
Bashivan P, Kar K, DiCarlo JJ (2019) Neural population control via deep
image synthesis. Science 364:eaav9436.
Baxter MG, Murray EA (2002) The amygdala and reward. Nat Rev Neurosci
3:563–573.
Belova MA, Paton JJ, Salzman CD (2008) Moment-to-moment tracking of
state value in the amygdala. J Neurosci 28:10023–10030.
Benjamini Y, Hochberg Y (1995) Controlling the false discovery rate: a prac-
tical and powerful approach to multiple testing. J R Stat Soc Series B Stat
Methodol 57:289–300.
Bo K, Yin S, Liu Y, Hu Z, Meyyappan S, Kim S, Keil A, Ding M (2021)
Decoding neural representations of affective scenes in retinotopic visual
cortex. Cereb Cortex 31:3047–3063.
Bonnet L, Comte A, Tatu L, Millot J, Moulin T, Medeiros de Bustos E (2015)
The role of the amygdala in the perception of positive emotions: an
“intensity detector”. Front Behav Neurosci 9:178.
Bradburn NM (1969) The structure of psychological well-being. Oxford,
England: Aldine.
Bradley MM, Lang PJ (2007) The international affective picture system
(IAPS) in the study of emotion and attention. In: Handbook of emotion
elicitation and assessment, series in affective science (Coan JA, Allen JJB,
eds), pp 29–46. New York, NY, US: Oxford University Press.
Britton JC, Taylor SF, Sudheimer KD, Liberzon I (2006) Facial expressions
and complex IAPS pictures: common and differential networks.
Neuroimage 31:906–919.
Cacioppo J, Berntson G, Norris C, Gollan J (2012) The evaluative space
model. In: Handbook of theories of social psychology: volume 1, pp 50–
72. Thousand Oaks, California: SAGE Publications Inc.
Canli T, Zhao Z, Brewer J, Gabrieli JD, Cahill L (2000) Event-related activa-
tion in the human amygdala associates with later memory for individual
emotional experience. J Neurosci 20:RC99.
Čeko M, Kragel PA, Woo C-W, López-Solà M, Wager TD (2022) Common
and stimulus-type-speciﬁc brain representations of negative affect. Nat
Neurosci 25:760–770.
Costafreda SG, Brammer MJ, David AS, Fu CHY (2008) Predictors of amyg-
dala activation during the processing of emotional stimuli: a meta-analysis
of 385 PET and fMRI studies. Brain Res Rev 58:57–70.
Cross L, Cockburn J, Yue Y, O’Doherty JP (2021) Using deep reinforcement
learning to reveal how the brain encodes abstract state-space representa-
tions in high-dimensional environments. Neuron 109:724–738.e7.
Cunningham WA, Brosch T (2012) Motivational salience: amygdala tuning
from traits, needs, values, and goals. Curr Dir Psychol Sci 21:54–59.
Jang and Kragel • Modeling Amygdala Function
J. Neurosci., April 30, 2025 • 45(18):e1436242025 • 9


## Page 10

Delplanque S, N’diaye K, Scherer K, Grandjean D (2007) Spatial frequen-
cies or emotional effects? A systematic measure of spatial frequencies
for IAPS pictures by a discrete wavelet analysis. J Neurosci Methods
165:144–150.
Dumoulin SO, Wandell BA (2008) Population receptive ﬁeld estimates in
human visual cortex. Neuroimage 39:647–660.
Fecteau S, Belin P, Joanette Y, Armony JL (2007) Amygdala responses to non-
linguistic emotional vocalizations. Neuroimage 36:480–487.
Friston KJ (2007) Statistical parametric mapping: the analysis of functional
brain images, Ed 1st. Amsterdam Boston: Elsevier/Academic Press.
Fukushima K (1988) Neocognitron: a hierarchical neural network capable of
visual pattern recognition. Neural Netw 1:119–130.
Garavan H, Pendergrass JC, Ross TJ, Stein EA, Risinger RC (2001) Amygdala
response to both positively and negatively valenced stimuli. Neuroreport
12:2779–2783.
Glasser MF, et al. (2016) A multi-modal parcellation of human cerebral cor-
tex. Nature 536:171–178.
Gothard KM (2020) Multidimensional processing in the amygdala. Nat Rev
Neurosci 21:565–575.
Goto F, et al. (2022) Gastrin-releasing peptide regulates fear learning under
stressed conditions via activation of the amygdalostriatal transition
area. Mol Psychiatry 27:1694–1703.
Haj-Ali H, Anderson AK, Kron A (2020) Comparing three models of arousal
in the human brain. Soc Cogn Affect Neurosci 15:1–11.
Hartling C, Metz S, Pehrs C, Scheidegger M, Gruzman R, Keicher C, Wunder
A, Weigand A, Grimm S (2021) Comparison of four fMRI paradigms
probing emotion processing. Brain Sci 11:525.
Horikawa T, Kamitani Y (2017) Generic decoding of seen and imagined
objects using hierarchical visual features. Nat Commun 8:15037.
Hudson M, Seppälä K, Putkinen V, Sun L, Glerean E, Karjalainen T, Karlsson
HK, Hirvonen J, Nummenmaa L (2020) Dissociable neural systems for
unconditioned acute and sustained fear. Neuroimage 216:116522.
Huth AG, Nishimoto S, Vu AT, Gallant JL (2012) A continuous semantic
space describes the representation of thousands of object and action cat-
egories across the human brain. Neuron 76:1210–1224.
Janak PH, Tye KM (2015) From circuits to behaviour in the amygdala. Nature
517:284–292.
Jin J, Zelano C, Gottfried JA, Mohanty A (2015) Human amygdala represents
the complete spectrum of subjective valence. J Neurosci 35:15145–15156.
Jones JP, Palmer LA (1987) An evaluation of the two-dimensional Gabor ﬁlter
model of simple receptive ﬁelds in cat striate cortex. J Neurophysiol 58:
1233–1258.
Kar K, Kubilius J, Schmidt K, Issa EB, DiCarlo JJ (2019) Evidence that recur-
rent circuits are critical to the ventral stream’s execution of core object
recognition behavior. Nat Neurosci 22:974–983.
Kensinger EA, Schacter DL (2006) Processing emotional pictures and words:
effects of valence and arousal. Cogn Affect Behav Neurosci 6:110–126.
Koelsch S, Skouras S, Fritz T, Herrera P, Bonhage C, Küssner MB, Jacobs AM
(2013) The roles of superﬁcial amygdala and auditory cortex in
music-evoked fear and joy. Neuroimage 81:49–60.
Kohavi R (1995) A study of cross-validation and bootstrap for accuracy
estimation and model selection. In: IJCAI’95: proceedings of the 14th inter-
national joint conference on artiﬁcial intelligence - volume 2, pp 1137–1143.
San Francisco, CA, USA: Morgan Kaufmann Publishers Inc.
Kragel PA, LaBar KS (2016) Decoding the nature of emotion in the brain.
Trends Cogn Sci 20:444–455.
Kragel PA, Reddan MC, LaBar KS, Wager TD (2019) Emotion schemas are
embedded in the human visual system. Sci Adv 5:eaaw4358.
Kragel PA, Treadway MT, Admon R, Pizzagalli DA, Hahn EC (2023) A meso-
corticolimbic signature of pleasure in the human brain. Nat Hum Behav 7:
1332–1343.
Kravitz DJ, Saleem KS, Baker CI, Ungerleider LG, Mishkin M (2013) The ven-
tral visual pathway: an expanded neural framework for the processing of
object quality. Trends Cogn Sci 17:26–49.
Krizhevsky A, Sutskever I, Hinton GE (2012) ImageNet classiﬁcation with
deep convolutional neural networks. In: Advances in neural information
processing systems. Curran Associates, Inc.
Kurdi B, Lozano S, Banaji MR (2017) Introducing the open affective standard-
ized image set (OASIS). Behav Res 49:457–470.
Lee TS (1996) Image representation using 2D Gabor wavelets. IEEE Trans
Pattern Anal Mach Intell 18:959–971.
Lescroart MD, Gallant JL (2019) Human scene-selective areas represent 3D
conﬁgurations of surfaces. Neuron 101:178–192.e7.
Li Z, Yan A, Guo K, Li W (2019) Fear-related signals in the primary visual
cortex. Curr Biol 29:4078–4083.e2.
Lindquist KA, Satpute AB, Wager TD, Weber J, Barrett LF (2016)
The brain basis of positive and negative affect: evidence from a
meta-analysis of the human neuroimaging literature. Cereb Cortex 26:
1910–1922.
Lindquist KA, Wager TD, Kober H, Bliss-Moreau E, Barrett LF (2012) The
brain basis of emotion: a meta-analytic review. Behav Brain Sci 35:121–
143.
Liu TT, Fu JZ, Chai Y, Japee S, Chen G, Ungerleider LG, Merriam EP (2022)
Layer-speciﬁc, retinotopically-diffuse modulation in human visual cortex
in response to viewing emotionally expressive faces. Nat Commun 13:
6302.
Mather M, Canli T, English T, Whitﬁeld S, Wais P, Ochsner K, Gabrieli JDE,
Carstensen LL (2004) Amygdala responses to emotionally valenced sti-
muli in older and younger adults. Psychol Sci 15:259–263.
Mattek AM, Wolford GL, Whalen PJ (2017) A mathematical model captures
the structure of subjective affect. Perspect Psychol Sci 12:508–526.
McDonald AJ (1998) Cortical pathways to the mammalian amygdala. Prog
Neurobiol 55:257–332.
Mills F, et al. (2022) Amygdalostriatal transition zone neurons encode sus-
tained valence to direct conditioned behaviors. 2022.10.28.514263.
Available at: https://www.biorxiv.org/content/10.1101/2022.10.28.514263v1
[Accessed July 21, 2023].
Miskovic V, Anderson A (2018) Modality general and modality speciﬁc cod-
ing of hedonic valence. Curr Opin Behav Sci 19:91–97.
Murray EA, Wise SP (2004) What, if anything, is the medial temporal lobe,
and how can the amygdala be part of it if there is no such thing?
Neurobiol Learn Mem 82:178–198.
Naselaris T, Kay KN, Nishimoto S, Gallant JL (2011) Encoding and decoding
in fMRI. Neuroimage 56:400–410.
Nguyen A, Dosovitskiy A, Yosinski J, Brox T, Clune J (2016) Synthesizing the
preferred inputs for neurons in neural networks via deep generator net-
works. Available at: http://arxiv.org/abs/1605.09304 [Accessed October
24, 2022].
Nishimoto S, Vu AT, Naselaris T, Benjamini Y, Yu B, Gallant JL (2011)
Reconstructing visual experiences from brain activity evoked by natural
movies. Curr Biol 21:1641–1646.
O’Neill P-K, Gore F, Salzman CD (2018) Basolateral amygdala circuitry in
positive and negative valence. Curr Opin Neurobiol 49:175–183.
Paton JJ, Belova MA, Morrison SE, Salzman CD (2006) The primate amyg-
dala represents the positive and negative value of visual stimuli during
learning. Nature 439:865.
Pessoa L (2010) Emotion and cognition and the amygdala: from “what is it?”
to “what’s to be done?” Neuropsychologia 48:3416–3429.
Pessoa L, Adolphs R (2010) Emotion processing and the amygdala: from a
‘low road’ to ‘many roads’ of evaluating biological signiﬁcance. Nat Rev
Neurosci 11:773–783.
Price JL (2003) Comparative aspects of amygdala connectivity. Ann N Y Acad
Sci 985:50–58.
Riesenhuber M, Poggio T (1999) Hierarchical models of object recognition in
cortex. Nat Neurosci 2:1019–1025.
Sah P, Faber ESL, Lopez De Armentia M, Power J (2003) The amygdaloid
complex: anatomy and physiology. Physiol Rev 83:803–834.
Sander D, Grafman J, Zalla T (2003) The human amygdala: an evolved system
for relevance detection. Rev Neurosci 14:303–316.
Sladky R, Kargl D, Haubensak W, Lamm C (2024) An active inference per-
spective for the amygdala complex. Trends Cogn Sci 28:223–236.
Soderberg K, Jang G, Kragel P (2023) Sensory encoding of emotion conveyed
by the face and visual context. Available at: http://biorxiv.org/lookup/doi/
10.1101/2023.11.20.567556 [Accessed April 4, 2024].
Styliadis C, Ioannides AA, Bamidis PD, Papadelis C (2014) Amygdala
responses to valence and its interaction by arousal revealed by MEG.
Int J Psychophysiol 93:121–133.
Swanson LW, Petrovich GD (1998) What is the amygdala? Trends Neurosci
21:323–331.
The MathWorks Inc. (2024) Statistics and machine learning toolbox: 22.4
(R2024a), Natick, Massachusetts: The MathWorks Inc. Available at:
https://www.MathWorks.com
10 • J. Neurosci., April 30, 2025 • 45(18):e1436242025
Jang and Kragel • Modeling Amygdala Function


## Page 11

Tiedemann LJ, Alink A, Beck J, Büchel C, Brassen S (2020) Valence encoding
signals in the human amygdala and the willingness to eat. J Neurosci 40:
5264–5272.
van der Maaten L, Hinton G (2008) Visualizing data using t-SNE. J Mach
Learn Res 9:2579–2605.
Vytal K, Hamann S (2010) Neuroimaging support for discrete neural correlates
of basic emotions: a voxel-based meta-analysis. J Cogn Neurosci 22:2864–
2885.
Wang B, Ponce CR (2022) High-performance evolutionary algorithms for
online neuron control. In: Proceedings of the genetic and evolutionary
computation conference, pp 1308–1316. Available at: http://arxiv.org/
abs/2204.06765 [Accessed May 12, 2023].
Watson D, Tellegen A (1985) Toward a consensual structure of mood.
Psychol Bull 98:219–235.
Winston JS, Gottfried JA, Kilner JM, Dolan RJ (2005) Integrated neural rep-
resentations of odor intensity and affective valence in human amygdala.
J Neurosci 25:8903–8907.
Wold S, Sjöström M, Eriksson L (2001) PLS-regression: a basic tool of chemo-
metrics. Chemometr Intell Lab Syst 58:109–130.
Xiao W, Kreiman G (2020) XDream: ﬁnding preferred stimuli for visual neu-
rons using generative networks and gradient-free optimization. PLoS
Comput Biol 16:e1007973.
Yamins DLK, DiCarlo JJ (2016) Using goal-driven deep learning models to
understand sensory cortex. Nat Neurosci 19:356–365.
Jang and Kragel • Modeling Amygdala Function
J. Neurosci., April 30, 2025 • 45(18):e1436242025 • 11


