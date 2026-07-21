# (2025) Scaling laws for decoding images from brain activity

**Source:** (2025) Scaling laws for decoding images from brain activity.pdf

---

## Page 1

Scaling laws for decoding images from brain activity
Hubert Banville1,∗, Yohann Benchetrit1,∗, Stéphane d’Ascoli1, Jérémy Rapin1, Jean-Rémi King1
1Meta AI
∗Equal contribution.
Generative AI has recently propelled the decoding of images from brain activity. How do these
approaches scale with the amount and type of neural recordings? Here, we systematically compare
image decoding from four types of non-invasive devices: electroencephalography (EEG), magnetoen-
cephalography (MEG), high-field functional Magnetic Resonance Imaging (3T fMRI) and ultra-high
field (7T) fMRI. For this, we evaluate decoding models on the largest benchmark to date, encompassing
8 public datasets, 84 volunteers, 498 hours of brain recording and 2.3 million brain responses to natural
images. Unlike previous work, we focus on single-trial decoding performance to simulate real-time
settings. This systematic comparison reveals three main findings. First, the most precise neuroimaging
devices tend to yield the best decoding performances, when the size of the training sets are similar.
However, the gain enabled by deep learning – in comparison to linear models – is obtained with the
noisiest devices. Second, we do not observe any plateau of decoding performance as the amount of
training data increases. Rather, decoding performance scales log-linearly with the amount of brain
recording. Third, this scaling law primarily depends on the amount of data per subject. However,
little decoding gain is observed by increasing the number of subjects. Overall, these findings delineate
the path most suitable to scale the decoding of images from non-invasive brain recordings.
Date: January 28, 2025
Correspondence: {hubertjb,ybenchetrit,sdascoli,jrapin,jeanremi}@meta.com
1
Introduction
Decoding natural images from brain activity originated in the 2000s (Kamitani and Tong, 2005; Miyawaki
et al., 2008; Naselaris et al., 2009) but progressed rapidly over the past two years. Reconstructing images
from functional Magnetic Resonance Imaging (fMRI) (Ozcelik and VanRullen, 2023; Mai and Zhang, 2023;
Zeng et al., 2023; Ferrante et al., 2022; Scotti et al., 2024) and magnetoencephalography (MEG) (Benchetrit
et al., 2024) can now be achieved by training a deep neural network to predict, from brain signals, the latent
representation of an image, and then using this prediction to condition an image generation model (see
Figure 1A).
Four main factors are presumably responsible for this recent progress. First, recent studies train their decoders
on a larger amount of data than in the past: it is now common to train models on several hours of brain
recordings per subject (Défossez et al., 2022; Gwilliams et al., 2023; Schoffelen et al., 2019; Tang et al., 2023;
Armeni et al., 2022; Allen et al., 2022; Scotti et al., 2024; Benchetrit et al., 2024; Hebart et al., 2023; Chehab
et al., 2022). Second, several approaches benefited from hardware improvements, such as the development
of ultra high field (7T) fMRI (Allen et al., 2022). Third, modern deep learning has effectively provided
neuroscience with powerful representations of images in the brain (Kriegeskorte and Diedrichsen, 2016; Yamins
et al., 2014; Eickenberg et al., 2017; Schrimpf et al., 2018). Indeed, computer vision models like OpenAI
CLIP (Radford et al., 2021; Ozcelik and VanRullen, 2023; Conwell et al., 2022) and DINOv2 (Oquab et al.,
2023; Benchetrit et al., 2024; Adeli et al., 2023), have been shown to learn representations that linearly predict
brain responses to natural images. Fourth, recent models based on diffusion effectively help reconstructing
plausible images from the decoding of these latent image features.
What are the best paths to improve brain-to-image decoding? In spite of a flourishing field, this issue
is particularly difficult to address. First, most studies focus on a single neuroimaging device, i.e., either
electroencephalography (EEG), MEG, fMRI at 3 Tesla (3T fMRI) or 7T fMRI. Second, existing datasets contain
1
arXiv:2501.15322v1  [eess.IV]  25 Jan 2025


## Page 2

EEG
MEG
7T MRI
3T MRI
A
B
3T fMRI
Hebart2023
0.00
0.13
R
EEG 
Giﬀord2022
0.00
0.09
R
MEG
Hebart2023
0.00
0.18
R
7T fMRI
Allen2022
0.00
0.32
R
Brain
AI
Encode
Encode
Decode
2.3M images
84 subjects
498 h of brain signals
Visual
embedding
C
Figure 1 (A) Brain-to-image decoding and encoding pipeline. In decoding, brain models are trained to predict, from
brain activity, the embeddings of the images learned by a pretrained computer vision model. Decoding predictions can
then be fed to an image generation model to reconstruct the images. In encoding, models are instead trained to predict
brain activity from image embeddings. (B) Our analyses rely on multiple datasets of brain data and image pairs,
focusing on four neuroimaging devices: EEG, MEG, 3T fMRI and 7T fMRI. (C) We validate the content of the datasets
using encoding models trained to predict each M/EEG channel or fMRI voxel from the presented images, which yield
the expected spatial response over the occipital region as measured with Pearson correlation. See Appendix C for
more details.
different numbers of subjects and of recordings per subject. Third, each study uses different preprocessing
steps, some of which are incompatible with single-trial (and therefore, real-time) evaluation of decoding
pipelines. Fourth, most studies use different image generation models – making it difficult to credit any
improvements to the data, the original method, or, more trivially, to a better image generation model. Finally,
the evaluation metrics are often disparate. In sum, this methodological variability obscures the factors critical
for brain-to-image decoding.
Here, we address this issue by disentangling the specific contributions of neuroimaging devices, data quantity
and pretrained models. To achieve this, we systematically compare the decoding performance obtained using
a variety of experimental setups within a unified benchmark. Our analysis is based on the brain activity of 84
healthy volunteers who watched a total of 2.3M images over 498 h while being recorded with EEG (Gifford
et al., 2022; Grootswagers et al., 2022; Xu et al., 2024), MEG (Hebart et al., 2023), 3T fMRI (Hebart et al.,
2023; Shen et al., 2019; Chang et al., 2019), or 7T fMRI (Allen et al., 2022). We systematically evaluate
single-trial (real-time-like) decoding performance using the Pearson correlation between the true features of a
state-of-the-art image embedding (Oquab et al., 2023) and the predictions obtained with brain decoders.
2
Methods
2.1
Problem statement
Goal
We aim to systematically compare brain-to-image decoding approaches, and identify potential scaling
laws, i.e., how decoding improves with the type and amount of data. For this, we curate the largest public
datasets into a unified benchmark and compare single-trial decoding performance across different experimental
setups.
Formalization
Decoding images from brain signals at the pixel-level is challenging because the brain does
not represent images in this feature space (Miyawaki et al., 2008). Over the years, it has thus become
standard to learn to predict latent embeddings of images and to use these predictions to condition an image
generation model (Lin et al., 2019; VanRullen and Reddy, 2019; Ozcelik and VanRullen, 2023; Chen et al.,
2023). Formally, this approach involves three components:
• Image module fθ : RH×W ×3 →RF , to transform image Ii into a latent embedding zi,
2


## Page 3

• Brain module gθ : RS×T →RF , to predict an estimate ˆzi,k of latent zi,k from the recording of brain
activity Xi,k in response to the kth presentation of Ii,
• Generating module hθ : RF →RH×W ×3 to transform ˆzi,k into ˆIi,k ,
where:
• S is the number of channels (M/EEG) or voxels (fMRI),
• T is the number of time points in the brain signal window, or repetition times (TRs) for fMRI,
• i ∈[1, N] indexes the unique images I with a common size H × W × 3,
• k ∈[1, K] indexes the image presentations Ii,k of the same image Ii,
• Xi,k ∈RS×T is the brain data within a time window relative to Ii,k,
• zi ∈RF is the representation of dimension F of image Ii obtained with the pretrained image module fθ.
2.2
Denoising
Brain signals are often denoised before they are fed into the brain module gθ. For example, it is common
to average the K brain responses to the same image ( ¯Xi =
1
K
PK
k=1 Xi,k) or to average the K predicted
embeddings (¯zi = 1
K
PK
k=1 ˆzi,k). For fMRI, it is also common to first fit a Generalized Linear Model (GLM)
(Friston et al., 1995) on the whole dataset (or on each of its recordings). Generally, GLMs estimate the
fMRI response from the convolution of each image-presentation boxcar function with a parameterizable
hemodynamic response function (HRF). However, as the resulting parameters ˆβ cannot be applied in real-time
and are typically computed irrespective of train/test splits, we will here focus on predicting images from X
directly. More generally, denoising strategies are often paradigm-dependent (e.g. the results will depend on the
number of repetitions within and across subjects), which can hinder the comparison of decoding performances
and limit their transferability to real-time applications. To address this, we primarily focus on single-trial
performance without denoising.
2.3
Brain modules
We implement two state-of-the-art architectures to predict image embeddings from brain activity. A detailed
description of the hyperparameter search procedure and architecture configurations is provided in Appendix D.
For clarity, we compare these architectures to a simple ridge-regularized linear regression trained to predict
image embeddings from either M/EEG or fMRI.
Linear model baseline
The linear model is a ridge regression (Hoerl and Kennard, 1970). In practice, we
use scikit-learn’s RidgeCV (Pedregosa et al., 2011), with α selected log-linearly between 10−4 and 108 and
otherwise default parameters. We train and evaluate on each subject separately.
As compared to linear models, deep learning architectures make it easier to learn on data from multiple
individuals at once (e.g. with subject-specific layers or embeddings (Défossez et al., 2022; Chehab et al., 2022)),
leveraging cross-subject brain activity patterns into representations that maximally align with the pretrained
image representation.
M/EEG deep learning module
We use the convolutional architecture of Défossez et al. (2022); Benchetrit
et al. (2024). This architecture includes a spatial attention layer, a subject-specific linear layer, a series of
residual dilated convolutional blocks, a temporal aggregation layer, and two projection heads (one for each
loss term described below in Equation (3)). In the largest configuration obtained with hyperparameter search,
this yields a total of 20.8M parameters.
fMRI deep learning module
We adapt the convolutional architecture of Scotti et al. (2023) for (1) multi-subject
training and (2) handling BOLD data with a time dimension 1. For this, we first apply a subject-specific
1The original architecture is designed to receive GLM ˆβ as input, and thus does not expect a temporal dimension on its input.
3


## Page 4

linear projection in the spatial dimension, akin to what is done in the M/EEG module and similar to recent
work on architectures designed to work with fMRI ˆβ (Scotti et al., 2024). Second, a timestep-wise linear
spatial projection (TR layer) is used to facilitate the extraction of time-varying information. As in the original
architecture, this projection is followed by layer normalization, a GELU non-linearity, dropout (p=0.5), and
residual convolutional blocks. A temporal aggregation layer then pools the temporal dimension, followed by a
linear projection. Finally, as in the M/EEG module, projection heads map predictions to the different loss
terms2. In its largest configuration, this yields a total of 146.3M parameters.
Training objective
To learn to predict image embeddings from brain activity, we use a combined retrieval3
and reconstruction loss, as in Benchetrit et al. (2024):
LCLIP (θ) = −1
B
B
X
i=1
log
exp(s( ˆzi, zi)/τ)
PB
j=1 exp(s( ˆzi, zj)/τ)
(1)
LMSE(θ) =
1
NF
N
X
i=1
∥zi −ˆzi∥2
2
(2)
LCombined = λLCLIP + (1 −λ)LMSE
(3)
where s is the cosine similarity and τ is a temperature parameter that we set to 1 in all experiments. Based
on early experiments, we fix λ = 0.25 to balance out the contribution of the two loss terms.
Training details
We train M/EEG and fMRI modules using the Adam optimizer (Kingma and Ba, 2014)
with default parameters (β1=0.9, β2=0.999) for up to 50 epochs. The learning rate and batch size were
selected as part of the hyperparameter search procedure and differ per neuroimaging device and data regime
(Appendix D). We use early stopping on a validation set obtained by randomly sampling 20% of the training
data, with a patience of 10 epochs, and evaluate the performance of the selected model on a held-out test set.
Models are trained on a single Volta GPU with 32 GB of memory. We repeat training using three different
random seeds for the weight initialization of the brain module, with two exceptions in Section 3.7: first, when
analyzing the impact of the number of subjects, we additionally repeat the sampling of subjects three times;
second, when analyzing the impact of trial quantity, we instead use two random seeds for weight initialization
and two random seeds for subsampling training trials.
2.4
Image and reconstruction modules
We focus our benchmark on the ability to predict, from brain activity, the latent embeddings of a state-of-
the-art computer vision model. For this, we use DINOv2-giant (Oquab et al., 2023)4 and take the average
output token as target for our embedding prediction task (F = 1536). DINOv2 image embeddings have
shown great transferability and performance on multiple computer vision downstream tasks and yielded high
brain-to-image retrieval performance in previous work (Benchetrit et al., 2024). We z-score-normalize the
latent embeddings of the images of each dataset by using the training set statistics5. Additionally, we compare
images reconstructed from brain activity using the methodology of Ozcelik and VanRullen (2023), for four
representative datasets (see description in Section 3.6).
2Of note, we use layer normalization and GELU activation in the CLIP head only, as in the original architecture.
3We use only the brain-to-image term of the CLIP loss as in Défossez et al. (2022); Benchetrit et al. (2024).
4https://huggingface.co/facebook/dinov2-giant
5Normalization is only applied to the targets of LMSE, as LCLIP already contains a normalization step through the use of
cosine similarity.
4


## Page 5

Table 1 Image decoding datasets used in this study. See Appendix A for a detailed description of each dataset.
Study
Device
# subjects
# sessions
# unique images
# trials
Time (h)
Xu et al. (2024)
EEG
8
12
960
43,070
11.6
Grootswagers et al. (2022)
EEG
48
48
22,448
1,168,416
44.2
Gifford et al. (2022)
EEG
10
40
16,740
83,0640
79.9
Hebart et al. (2023)
MEG
4
48
22,448
98,592
46.4
Shen et al. (2019)
fMRI (3T)
3
45
1,250
23,760
57.4
Hebart et al. (2023)
fMRI (3T)
3
36
8,740
29,520
42.6
Chang et al. (2019)
fMRI (3T)
4
54
4,916
18,870
55.0
Allen et al. (2022)
fMRI (7T)
4
160
37,000
120,000
160.4
Total
84
2,332,868
497.5
2.5
Data
We use eight publicly available datasets of brain activity recorded in response to image stimuli: Xu2024
(Alljoined) (Xu et al., 2024), Grootswagers2022 (THINGS-EEG1) (Grootswagers et al., 2022), Gifford2022
(THINGS-EEG2) (Gifford et al., 2022), Hebart2023meg (THINGS-MEG) (Hebart et al., 2023), Shen2019
(DeepRecon) (Shen et al., 2019), Hebart2023fmri (THINGS-fMRI) (Hebart et al., 2023), Chang2019
(BOLD5000) (Chang et al., 2019) and Allen2022 (Natural Scenes Dataset, or NSD) (Allen et al., 2022).
The datasets are summarized in Table 1. A detailed description of each dataset is provided in Appendix A.
The brain imaging data was collected and publicly shared by the authors of each dataset (Xu et al., 2024;
Grootswagers et al., 2022; Gifford et al., 2022; Hebart et al., 2023; Shen et al., 2019; Chang et al., 2019; Allen
et al., 2022).
For the THINGS-derived datasets (Grootswagers2022, Gifford2022, Hebart2023meg, Hebart2023fmri), we
removed from the training set the images whose category was also in the test set to avoid categorical leakage
between the train and test splits as in Benchetrit et al. (2024). On Allen2022, we follow previous image
decoding work and use only the four (out of eight) subjects that completed all 40 recording sessions.
We subsample the test set of each dataset by randomly selecting 100 unique test images (except for Shen2019,
which has only 50 test images available), and keeping all repetitions for these 100 images. When studying the
impact of averaging over multiple repetitions at test time, we also vary the number of available repetitions in
the test set, and evaluate decoding on averaged repetitions (either within- or across-subjects).
2.6
Preprocessing
M/EEG
We apply minimal preprocessing to M/EEG data following previous work (Défossez et al., 2022;
Benchetrit et al., 2024). First, raw data is highpass-filtered above 0.1 Hz and downsampled to 120 Hz. Each
channel is independently normalized using a robust scaler and values outside [-20, 20] are clipped to minimize
the impact of large outliers. Data is then epoched relative to stimulus onset and baseline-corrected by
subtracting the channel-wise average value from the pre-stimulus interval. Epochs always extend to 1 s after
stimulus onset, but have different start times t0 based on previous research: -0.1 for Grootswagers2022 (as in
Grootswagers et al. (2022)), -0.2 for Gifford2022 (as in Gifford et al. (2022)) and -0.5 for Hebart2024meg
(as in Benchetrit et al. (2024)). For Xu2024, we start epochs -0.3 s relative to stimulus onset to use as much
of the previous interstimulus interval segments as possible, however, we use the same interval as in Xu et al.
(2024) for baseline correction, i.e., (-0.05, 0.0).
fMRI
We use fMRIPrep 23.2.0 (Esteban et al., 2019) with default parameters to process the fMRI datasets
into the standard space MNI152NLin2009aSym (Fonov et al., 2009). Each brain volume of the time series
is then projected onto the fsaverage5 surface (Fischl et al., 1999). This yields, for each recording run, a
time series of brain volumes of shape (20484, T) where T is the total number of TRs recorded for this run.
Following this, we remove low-frequency noise in the fMRI signal using an additional detrending step: we fit a
cosine-drift linear model to each voxel in the time series, and subtract it from the raw signal. Each time series
5


## Page 6

is then z-score-normalized. Finally, data is epoched into windows of five TRs with the following (start, end)
times relative to stimulus onset (in seconds): Shen2019 (3.0, 13.0), Hebart2024fmri (3.0, 10.5), Chang2019
(3.0, 13.0) and Allen2022 (3.0, 11.0).
2.7
Evaluation
We evaluate the ability of brain modules to predict zi,k given Xi,k across different datasets, subjects and
numbers of unique image presentations. To evaluate prediction performance, we compute the average feature-
wise Pearson correlation R = 1
F
PF
f=1 corr(z(f), ˆz(f)). Whenever applicable, we also report the standard error
of the mean computed across subjects. Of note, we use the output of the MSE head to evaluate performance
as the reconstruction objective LMSE is conceptually more aligned with the feature-wise Pearson correlation
evaluation metric.
2.8
Scaling laws
We evaluate the scaling behavior of image decoding models by varying data quantity along two axes: (1)
number of training trials and (2) number of subjects.
Image quantity analysis
We focus on single-subject models and vary, in the training set, the number of
unique images as well as the number of image repetitions, whenever available (i.e., in Allen2022, Gifford2022,
Xu2024). We repeat this analysis for the first 10 subjects of every dataset.
Subject quantity analysis
We vary the number of subjects seen by the models from one to all subjects available
in a given dataset. For this, we compare two additional configurations: first, we use all available data per
dataset (all-trials) and second, we approximately match the number of trials across datasets (matched-trials,
described in Appendix B).
2.8.1
Recording time estimation
While the number of image presentations is a straightforward measure of data quantity, it does not reflect
the longer stimulus presentation times and interstimulus intervals used in some datasets. For instance, fMRI
datasets relied on much longer stimulus onset asynchrony (SOA) durations (i.e., the time elapsed between
the start of one image presentation and the start of the following image presentation) than M/EEG to
account for the slow hemodynamic response. For instance, the SOA is 10 s for Chang2019 but only 100 ms
for Grootswagers2022. Therefore, we additionally study scaling laws from the angle of recording duration, as
computed by multiplying the number of training trials by the SOA.
2.8.2
Cost estimation
When building a new dataset, the choice of neuroimaging device and the targeted quantity of data is strongly
influenced by the cost of data acquisition. As cost varies greatly between different neuroimaging devices, it is
therefore useful to also study how it relates to decoding performance. To provide an approximate scaling
cost for each device, we surveyed publicly available information about neuroimaging data collection services
(Appendix F). Based on this information, hourly cost (in USD) is estimated at $263 for EEG, $550 for MEG,
$935 for 3T fMRI and $1093 for 7T fMRI. The reader should bear in mind that these are rough estimates and
that data acquisition costs can vary significantly between countries and institutions.
2.9
Image reconstruction
The analyses described above focus on the decoding of an image embedding given single-trial or test-time
averaged brain signals. However, it is becoming increasingly common to evaluate decoding pipelines on their
ability to reconstruct the original image rather than its latent representation only. Following this approach,
we implement an additional generation step for all decoders.
6


## Page 7

Reconstruction pipeline
Adapted from Ozcelik and VanRullen (2023), our reconstruction pipeline consists in
using the predicted embedding as input to a pretrained image generation model. We thus re-trained each
decoder to predict the three required embeddings, namely CLIP-Image (257 tokens × 768), CLIP-Text (77
tokens × 768), and AutoKL (4 channels × 64 × 64), using the same objective as before (Equation (3)).
Images are center-cropped and rescaled to 512 × 512 pixels. Following Ozcelik and VanRullen (2023), we use
a renormalization step before running image generation: we z-score normalize predicted embeddings, then
“de-normalize” them using the inverse z-score transform, fitted on the training set. We run diffusion with 50
DDIM steps, a guidance scale of 7.5, a strength of 0.75 and a mixing of 0.4. We additionally blur all human
faces generated by the model.
For THINGS-derived datasets, the CLIP-Text embedding is obtained from the THINGS-Image database
object-category of the stimulus image. For Allen2022, we follow Ozcelik and VanRullen (2023) and average
the CLIP-Text embeddings of the (at most 5) captions of the corresponding image.
Training details
In decoding experiments, we predict the same embedding zi for the MSE and CLIP heads
(i.e., the token-average of DINOv2-giant). By contrast, we obtain better reconstruction performance by
predicting distinct embeddings on each head. Specifically, for each of the three embedding prompts needed
for reconstructing an image, we train a model to predict the full embedding on the MSE head and a pooled
version on the CLIP head (for the CLIP-Image model, we pool by using the class-token; for CLIP-Text, the
token-average; for the AutoKL model, the channel-average).
This particular choice of pooling for each embedding was found to perform significantly better across studies
and devices. Finally, for simplicity, we showcase the image reconstructions of one representative study per
recording device. We focused on studies using the images from THINGS-dataset whenever possible.
3
Results
3.1
Encoding analysis
To validate the datasets, we first test a standard linear encoding pipeline (Naselaris et al., 2011). Here,
encoding refers to the prediction of brain responses given the image features. For this, we build a time-lag
concatenation of image features to predict, with a ridge regression, the amplitude of the neural time series at
each time point relative to stimulus onset (see Appendix C). We use DINOv2 (Oquab et al., 2023) to extract
image features, as this unsupervised model has been shown to capture representations similar to those of the
brain (Benchetrit et al., 2024) (see Section 3.6 for analyses using other pre-trained image representations).
These linear encoding models are trained for each subject separately. Finally, we use the Pearson correlation
(R) to evaluate the similarity between the true and predicted brain responses held out from the same subject.
The encoding results confirm that EEG, MEG, 3T and 7T fMRI can be reliably predicted from the features of
the images that subjects watched (see Figure 1B and S1). As expected, brain responses to visual stimuli are
best predicted in the occipital lobe, host of the visual cortices, but these responses are visible in a distributed
set of brain regions. Overall, these results confirm that the brain responses to visual stimuli can be modeled,
for each of these datasets, from the pretrained embedding of a computer vision model.
3.2
Linear decoding
Encoding analyses make it difficult to compare different types of brain recordings, because the space in which
they are evaluated (e.g. voxels or sensors) varies arbitrarily between datasets. Thus, we now turn to linear
decoding. We train and evaluate linear ridge regression decoders at each time step relative to image onset,
and evaluate how well image features can be predicted from brain activity patterns across time.
Figure 2A and C show that image embeddings can be maximally decoded 110 ms and 380 ms after image onset
for EEG and MEG, respectively. For fMRI, which captures the slow blood-oxygen-level-dependent (BOLD)
response, decoding performance peaks around 4.5-5.2 s after image onset. The decoding performance then
decreases to chance-level around 750 ms (EEG), 1,500 ms (MEG), 7.5 s (3T fMRI) and 16 s (7T fMRI) after
image onset.
7


## Page 8

0.00
0.25
0.50
0.75
1.00
1.25
1.50
Time (s)
0.0
0.1
Pearson R
A
Linear
0.00
0.25
0.50
0.75
1.00
1.25
1.50
Time (s)
0.0
0.1
Pearson R
B
Deep neural networks
0.0
2.5
5.0
7.5
10.0
12.5
15.0
Time (s)
0.0
0.2
Pearson R
C
0.0
2.5
5.0
7.5
10.0
12.5
15.0
Time (s)
0.0
0.2
Pearson R
D
Subjects
0.0
0.1
0.2
0.3
0.4
Pearson R
E
1h
10h
40h
EEG: Xu2024
EEG: Gifford2022
EEG: Grootswagers2022
MEG: Hebart2023meg
fMRI 3T: Shen2019
fMRI 3T: Hebart2023fmri
fMRI 3T: Chang2019
fMRI 7T: Allen2022
Figure 2 Image decoding analyses show the expected temporal response for all datasets. (Left) Subject-specific stepwise
decoding using linear ridge regression as a function of time elapsed since image onset (t = 0). (Right) Sliding window
decoding using deep learning models trained across subjects on 100-ms windows for M/EEG or 1 TR for fMRI. We
report the average performance across subjects and show the standard error of the mean with shaded areas or error bars.
(Bottom) Peak Pearson correlation obtained in the linear (empty circles) and deep learning (filled circles) analyses, for
each subject of each study. Circle size indicates the total recording time available for each subject. See Figure S2 for
results in the matched-trials setting.
Switching to the matched-trials setting to allow comparing datasets using similar numbers of unique images
(Figure S2), we observe that linear decoding is best achieved with 7T fMRI (R=0.238), followed by 3T fMRI
(R=0.075-0.126), MEG (R=0.057) and EEG (R=0.018-0.033).
3.3
Decoding with deep learning
To what extent can these linear decoding scores be improved with deep learning models? To address this
question, we implemented and trained the deep learning pipelines described in Section 2.3 on sliding windows.
To account for different temporal resolutions across devices, we used 100-ms windows for M/EEG, and a
single TR per window for fMRI (1 TR corresponds to 1.5 to 2 s in the curated datasets).
These deep learning models reveal a similar decoding dynamic (Figure 2B-D). Critically, we observe a
significant improvement over linear baselines (two-sided Wilcoxon signed rank test (Wilcoxon, 1945) across
subjects and datasets, p < 10−14; see Figure 2E). Device performance was ordered similarly to linear models,
with EEG and 7T fMRI leading to the worst and best performances, respectively. Interestingly however, the
gain in performance observed between linear and deep models varies across devices: 1.9-2.4x for EEG, 1.5x
for MEG, 1.1-1.2x for 3T fMRI, and 1.2x for 7T fMRI. In other words, the devices that benefit the most from
deep learning pipelines appear to be those that are typically associated with lower signal-to-noise ratios.
8


## Page 9

0
2
Time (s)
0.0
0.1
Pearson R
A
EEG
Xu2024
0
2
Time (s)
0.0
0.1
EEG
Grootswagers2022
0
2
Time (s)
0.0
0.1
0.2
EEG
Gifford2022
0
2
Time (s)
0.0
0.1
0.2
MEG
Hebart2023meg
0
20
Time (s)
0.0
0.1
fMRI 3T
Shen2019
0
20
Time (s)
0.0
0.1
fMRI 3T
Hebart2023fmri
0
20
Time (s)
0.0
0.1
0.2
fMRI 3T
Chang2019
0
20
Time (s)
0.0
0.2
0.4
fMRI 7T
Allen2022
0
2
Time (s)
0.0
0.1
0.2
Pearson R
B
0
2
Time (s)
0.0
0.1
0
2
Time (s)
0.0
0.2
0
2
Time (s)
0.0
0.1
0.2
0
20
Time (s)
0.0
0.1
0
20
Time (s)
0.0
0.1
0
20
Time (s)
0.0
0.1
0.2
0
20
Time (s)
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
Pearson R
C
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test repetitions
1
2
3
6
12
24
48
80
All (cross subject)
Figure 3 Decoding of the image embedding as a function of time (x-axis) and number of test-time repetitions (color)
using deep learning models. (A) Sliding window decoding (100 ms for M/EEG; 1 TR for fMRI) and (B) growing
window decoding (t0=-0.5 for M/EEG; 0.0 for fMRI) show the expected time-locked response and highlights the
consistent improvement obtained by adding test-time image repetitions. Grey areas indicate the interval during which
images were shown. (C) Peak sliding window performance for each dataset. Black lines and bars indicate performance
obtained when averaging predictions over all repetitions of all subjects for each unique test image. We report the
average performance across subjects and show the standard error of the mean with shaded areas or error bars. We use
“large” architecture configurations everywhere (Appendix D) except for Grootswagers2022 for which the "medium"
configuration yielded more stable training dynamics. See Figure S3 for results in the matched-trials setting.
3.4
Impact of test-time averaging
In all datasets, test set images were shown multiple times to each subject. This allows improving signal-to-noise
ratio and decoding performance, by e.g. learning to predict from an averaged response, or averaging single-trial
predictions before evaluating metrics.
To evaluate whether this multiple-repetition approach effectively scales decoding performance, we systematically
vary the number of test image repetitions used for averaging over the test set. Results for both sliding- and
growing-window models are shown in Figure 3A-B. For all devices, adding more test repetitions improves
decoding performance (Spearman rank correlation of 0.33-0.72, 0.51, 0.58-0.97 and 0.82 for EEG, MEG,
3T and 7T fMRI, respectively). However, this gain follows a moderate log-linear relationship: the gain in
decoding performance rapidly decreases with the increasing number of repetitions. Further averaging test
predictions across subjects (black lines and bars in Figure 3) leads to additional small improvements. Overall,
we observe diminishing returns for all datasets, suggesting test-time averaging may not be ideal to scale
decoding performance.
3.5
Image retrieval
Next, we evaluate the performance of our decoding pipeline in a retrieval setting: given the predicted DINOv2-
giant embedding ˆz for an image in the test set, we identify the image, among the 100 (50 for Shen2019)
unique images in the test set whose true image embedding is most similar to ˆz. Of note, the prediction we use
is the output of the CLIP head of our model, as it is specifically trained using a retrieval objective (LCLIP ).
Figure 4A shows a sample of the best retrievals obtained across one representative dataset per device, to
align with reconstruction analyses (Figure 5). For all devices, top-1 or top-2 predictions are often correct,
and wrong predictions usually share categorical semantic information with the ground truth (e.g. animals,
inanimate objects, etc.). Of note, the performance on Shen2019 can be partially attributed to the smaller
size of its retrieval set (50 vs. 100).
9


## Page 10

Figure 4 Image retrieval across devices. (A) For each representative dataset of each device, a sample of three stimulus
images showing some of the most convincing retrievals obtained with our approach. Ground truth images are shown on
the top row. Top-1 retrieved images are shown underneath (top-2 image overlaid on bottom right): single-trial brain
responses (second row), subject-averaged predictions (third row) and predictions averaged across all subjects (bottom
row). (B) Top-5 retrieval accuracies for each dataset and each test-time averaging strategy, grouped by recording
device. See Figure S4 for the matched-trials setting.
Overall, these results confirm that the deep learning models can accurately identify an image given a pool of
candidate images. See Appendix E for comparable results in the matched-trials setting.
3.6
Image reconstruction
Image retrieval requires having access to the true image in the test set. To alleviate this constraint, we also
evaluate image reconstructions from our decoders. For this, we conditioned the generation of images from the
decoded image embeddings, as described in Section 2.9.
Figure 5 shows a sample of the reconstructions obtained on the same images as in Figure 4. Overall, the
images are never perfectly reconstructed, but nevertheless often share low-level as well as semantic features
with the images seen by the subjects.
To quantify these qualitative observations, we evaluate reconstructions with pixel-, low- and semantic-level
metrics, and compare them across decoding approaches (Section 3.4). Specifically, to evaluate the consistency
between a stimulus image I and its reconstruction ˆI, we select a representation method τ and compute the
Pearson correlation between τ(I) and τ(ˆI). In our study, we choose three different representations for τ,
covering both perceptual and semantics aspects of images: (1) the unmodified image itself as an array of pixels,
(2) the AlexNet-2 embedding, and (3) the CLIP-final embedding of an image. Averaging these correlations
across unique images for each representation τ, we obtain three different metrics that we respectively denote
10


## Page 11

Figure 5 Image reconstruction across devices. (A) For each study, a sample of 3 stimuli showing some of the most
convincing reconstructions obtained with our approach: from single-trial brain signals, and two increasingly large
aggregations (averaging embedding predictions at subject-level and at instance-level). (B) The comparison of the three
image generation metrics PixCorr (pixel space), AlexNet-2-R (low-level, latent space) and CLIP-Final-R (high-level,
latent space) for single-trial decoding and aggregations. As expected, performance increases overall when averaging
more than one trial, even at subject-level.
as PixCorr, AlexNet-2-R and CLIP-Final-R. Of note, these last two metrics slightly differ from the 2-way
comparison metrics AlexNet-2 and CLIP-Final, defined in Ozcelik and VanRullen (2023). The use of the
simpler average correlation (a point-wise metric), instead of the 2-way comparison score, allows us to compare
different denoising approaches using a two-sided Wilcoxon signed-rank test, as shown in Figure 5B.
The results confirm that the best reconstructions are achieved from 7T fMRI. In addition, the quality of
reconstructions increases when averaging embeddings across image repetitions, both qualitatively (Figure 5A)
and quantitatively (Figure 5B). This is the case when averaging all predicted embeddings for a given image
across a single subject (“subject-average”), and even more so when averaging all predicted embeddings for a
given image across all subjects (“instance-average”).
3.7
Comparing decoding performance across data quantities
How does image decoding scale with the amount of brain signals? To address this question, we train our
decoders on increasingly larger subsets of neuroimaging data and measure the corresponding single-trial
decoding performance (i.e., without test-time averaging).
Scaling trials
First, we consider the scaling of decoding performance within subjects. Figure 6A shows that
different devices require different numbers of trials to reach the same decoding performance. A log-linear fit
shows that, to reach R = 0.01, 7T fMRI only requires 57 trials, whereas 3T fMRI requires between 123 and
522 trials, MEG requires 2,3K trials, and EEG requires between 4,9K and 5K trials.
11


## Page 12

101
102
103
104
# train and valid trials
0.0
0.1
0.2
0.3
Pearson R
A
Single-subject models
1
10
# subjects
B
Multi-subject models
EEG: Xu2024
EEG: Gifford2022
EEG: Grootswagers2022
MEG: Hebart2023meg
fMRI 3T: Shen2019
fMRI 3T: Hebart2023fmri
fMRI 3T: Chang2019
fMRI 7T: Allen2022
Figure 6 Decoding performance as a function of (A) number of training and validation trials for single-subject models
and (B) number of subjects for multi-subject models. The horizontal dashed line in (A) indicates the threshold of
R =0.01 which we use as a comparison point for the number of trials required to perform better than chance. Shaded
areas represent the standard error of the mean across subjects.
Scaling subjects
Second, we consider the scaling of decoding performance across subjects (Figure 6B). Results
suggest that scaling the number of subjects yields limited improvement in most cases and may even lead
to a decrease in performance (Shen2019, Hebart2023fmri). Although our models are trained and tested on
the same subjects, inter-subject variability (see also Figure 2E) appears to harm overall model performance,
especially in low-subject regimes, e.g. fewer than 10 subjects. Of note, the Grootswagers2022 dataset, with
48 subjects, has the largest number of subjects in our benchmark. Yet, the improvement of 0.004 obtained
by doubling the number of subjects from 24 to 48 is not significant (two-sided t-test, p = 0.49). Scaling the
number of EEG subjects does not seem to provide clear benefits for decoding performance.
Scaling both trials and subjects
Next, we compare data quantity across a mixture of data regimes (i.e.,
number of subjects and trials) by considering (1) the total number of training trials across subjects) and (2)
the recording duration (i.e., the number of hours corresponding to a given number of trials). As shown in
Figure 7, decoding performance increases with the amount of data across all datasets. This increase follows
a log-linear trend, whose slope and intercept depends on the recording device. For example, focusing on
models fitted on the number of recording hours (Figure 7B, middle column), EEG has a slope of 0.045 (±0.003
standard error of the mean), MEG of 0.064 (±0.011), 3T fMRI of 0.048 (±0.009) and 7T fMRI of 0.075
(±0.009).
Strikingly, 7T fMRI (Allen2022) yields the best decoding performance across the board, both in terms of
number of trials and hours of recording. 7T fMRI aside, the device that best scales decoding performance
depends on what factor (trials, time, cost) is considered (Figure 7B). When considering the number of trials, 3T
fMRI either outperforms (Chang2019) or works similarly to MEG with a similar number of trials, while EEG
lags behind. When considering the amount of recording time, we find instead that fMRI 3T (Chang2019),
MEG and EEG with trial scaling (Gifford2022) yield similar performance for the same number of hours.
When considering the potential of scaling, MEG has the largest slope after 7T fMRI (Figure 7B), suggesting
it may be a promising avenue to scale decoding performances. Finally, we do not currently find evidence of a
saturation effect: decoding performance does not appear to plateau after a specific quantity of data.
3.8
Estimating cost of data acquisition
The possibility of scaling does not solely depend on performance, but also on the cost of data acquisition.
To address this issue, we estimate the cost associated with each type of device, by using publicly available
information (see Appendix F), and modeled the log-linear relationship between cost and decoding performance.
Fitted models are shown in Figure 7B (last column). We can then estimate the cost or the gain associated with
different hypothetical objectives. First, with these cost estimates, we retrospectively infer that the acquisition
of the present datasets costs $1.5k for Xu2024, $6.9k for Grootswagers2022, $9.7k for Gifford2022, $19.4k
12


## Page 13

1000
Cost
1
10
Time
0.00
0.15
Pearson R
$10k
1000
$10k
Cost
1
10h
Time
0.000
0.175
1000
$10k
Cost
1
10h
Time
0.00
0.15
1000
10k
$100k
Cost
1
10
100h
Time
0.00
0.35
104
106
Trials
0.0
0.1
0.2
0.3
Pearson R
1
10
100h
Time
1000
$100k
Cost
0.00
0.05
Slope (R vs. log(time))
0.030
0.023
0.045
0.064
0.039
0.048
0.051
0.075
EEG: Gifford2022
EEG: Grootswagers2022
EEG: Xu2024
MEG: Hebart2023meg
fMRI 3T: Chang2019
fMRI 3T: Hebart2023fmri
fMRI 3T: Shen2019
fMRI 7T: Allen2022
A
B
C
Figure 7 Decoding performance for each dataset as a function of data quantity. (A) Per-device performance as a
function of image presentation time (bottom x-axis) and of the estimated average data collection cost (top x-axis). (B)
Performance is shown on the same x-axis (number of trials, recording time in hours or estimated cost in USD) for all
devices to facilitate comparison. We vary the data quantity by training medium-size models on (i) single subjects, (ii)
all subjects but with matched trials (see Appendix B) or (iii) all subjects and all trials. (C) Slope of log-linear models
fitted on the number of recording hours. Shaded areas and error bars represent the standard error of the mean of the
fitted log-linear model parameters.
13


## Page 14

for Hebart2023meg, $41.1k for Shen2019, $26k for Hebart2023fmri, $44.8k for Chang2019, and $131.2k for
Allen2022. Second, according to log-linear models, a budget of $131.2k (i.e., the estimate for the ultra-high
field fMRI dataset) would lead to Pearson correlations of 0.123-0.197 for EEG, 0.210 for MEG, 0.122-0.172 for
fMRI 3T and 0.363 for fMRI 7T (the actual maximum Pearson R for fMRI 7T is 0.372).
These estimates highlight the fact that despite the considerable difference between 7T fMRI and other
modalities, the high cost and slow temporal resolution of 7T fMRI may not lead to the most effective path to
scaling the decoding of images from brain activity.
4
Discussion
We aimed to characterize the factors which are critical to improving brain-to-image decoding performance.
For this, we conducted a comprehensive comparison of decoding pipelines on the largest benchmark to
date encompassing 84 subjects who watched 2.3M natural images over 498 h while their brain activity was
recorded with EEG, MEG, 3T fMRI or 7T fMRI. To ensure meaningful comparisons, we focused on a unified
preprocessing and modeling pipeline, evaluated decoding on single-trial and controlled for the amount and
type of training data.
4.1
Contributions
This work provides three main contributions.
Decoding performance and deep learning gain
First, both linear and deep learning models highlight the
importance of recording devices: as expected, when the size of the training sets are similar, 7T fMRI leads to
the best results, followed by 3T fMRI, MEG and ultimately EEG. However, the decoding gain enabled by
deep learning algorithms, as compared to linear models, unexpectedly appears to benefit the noisiest devices,
namely EEG and MEG (Figure 2). We speculate that the noise associated with brain recordings may have
specific spatial (sensors or voxels) and temporal structures that can only be separated in a latent space. If
confirmed, this hypothesis would highlight the importance of developing, in the future, foundational models
of brain activity, to automatically perform such separation between brain signals and recording noise (e.g.
Thomas et al. (2022); Ortega Caro et al. (2023); Yang et al. (2024); Yuan et al. (2024)).
Scaling laws
Second, and in spite of analyzing the largest amount of brain responses to images to date, we
do not observe any plateau of decoding performance as the amount of training data increases. Rather, the
log-linear scaling laws presently observed strengthens previous findings (Antonello et al., 2024; Bonnasse-Gahot
and Pallier, 2024; Défossez et al., 2022; Benchetrit et al., 2024). Together, these results suggest that the
decoding of brain activity may be most simply improved by recording more data. Interestingly, not all data
regimes are equivalent in that regard. In particular, our results show that the amount of within-subject
recordings steadily improves decoding, whereas the amount of across-subject recordings lead to modest, if any,
improvements. This result emphasizes the importance of inter-individual differences when it comes to neural
representations and brain activity patterns. While additional research incorporating large databases across
many more subjects (Van Essen et al., 2012; Nastase et al., 2021; Schoffelen et al., 2019) remains necessary,
this result suggests that future efforts may benefit most from focusing on building datasets with a few subjects
recorded over many sessions (Allen et al., 2022; Hebart et al., 2023; Armeni et al., 2022). Finally, the study
of scaling laws often considers the impact of data size in relation to the size of the model. The systematic
exploration of increasingly large architectures remains an open question (Kaplan et al., 2020; Hoffmann et al.,
2024).
Beyond performance: the importance of time and cost
Third, the present comparisons highlight that decoding
performance should not be the sole factor to consider when deciding which device to use for data collection.
As illustrated in Figure 7, the temporal resolution and the costs associated with fMRI is such that, depending
on the budget, and/or the targeted decoding performance, the most cost- and time-efficient route may not
necessarily be in favor of MRI devices. For instance, when comparing performance for equivalent numbers of
trials, 3T fMRI is better or equivalent to MEG, which itself is better than EEG. However, if we look instead
14


## Page 15

at recording duration, MEG and EEG (Gifford2022 and Xu2024) reach better performance than two of the
three 3T fMRI datasets.
4.2
Limitations
Experimental protocols
Our main scaling law analysis (Figure 7) compares devices by subsampling their
corresponding datasets. However, each dataset is also marked by differences in experimental paradigms. For
instance, while Gifford2022, Grootswagers2022, Hebart2023meg and Hebart2023fmri used pictures from
the THINGS database (Hebart et al., 2019), Allen2022 and Xu2024 used images from COCO (Lin et al.,
2014). Yet, different image datasets may imply different biases (e.g. category bias, field of view, scene- vs.
object-centered), which in turn could impact decoding performance (Shirakawa et al., 2024). In addition,
the duration of the image presentations, and of the pause in-between trials, varies across studies, in part to
accommodate the temporal resolution of the corresponding brain recording device (e.g. SOA of 100 ms for
Grootswagers vs. 10 s for Chang2019). It will be crucial for the research community to collect additional
datasets so as to formally evaluate the impact of stimulus design choices on brain decoding performance.
Suboptimal image reconstructions
The present study focuses on a unified pipeline to decode images from
single-trial brain responses. This choice, motivated by real-time-like evaluation, may lead to suboptimal
decoding performances. First, unlike many fMRI studies, we do not systematically explore the variety of
denoising strategies. In particular, many fMRI studies rely on “beta-values”, i.e., statistical estimates optimized
to specifically isolate the brain response to each image (Section 2.2). This decision stems from the fact that
the results of GLMs (1) are not usable in real-time, (2) vary with the number of repetitions and (3) risk
mixing the train/test signals, since they are applied before such splitting. Yet, the resulting brain patterns
have higher signal-to-noise ratio, and thus lead to better decoding performances (Ozcelik and VanRullen,
2023). Second, most recent decoding studies have made use of models pretrained on fMRI and/or EEG, with
demonstrable improvements (Chen et al., 2023). Third, we here focus on two state-of-the-art architectures, for
M/EEG on the one hand (Benchetrit et al., 2024; Défossez et al., 2022), and 3T and 7T fMRI on the other
hand (Scotti et al., 2023). However, other architectures and optimizations have been proposed too (Ozcelik
et al., 2022; Shen et al., 2024; Yang et al., 2024; Yuan et al., 2024). Finally, image reconstruction appears to
continue improving from the continuous development of generative image models (Scotti et al., 2024). Overall,
the continuously-developed architectural, preprocessing, and modeling tricks employed in the field should be
prioritized when optimizing for reconstruction quality.
4.3
Ethical considerations
The improvement in brain decoding methodology has raised ethical discussions (Poldrack, 2017). While the
present study confirms that we can decode images from brain activity, it is restricted to the decoding of visual
perception, i.e., exogenously-elicited representations that experimenters can easily control and repeat. For
endogenous representations, such as imagination, recall, internal reasoning, etc., current studies show that
decoding can only achieve statistical significance if subjects actively engage in a controlled task, and that the
decoding performances are effectively mediocre (Tang et al., 2023; Horikawa et al., 2013). Consequently, these
results suggest that it will not be possible to decode, from neuroimaging, spontaneous train-of-thoughts in
real-time and without the consent of the subjects. While these technical hurdles certainly provide a degree
of security against the misuse of brain decoding, they also effectively limit the feasibility of applying these
approaches in clinical settings, where brain-lesioned patients may benefit from brain-computer-interfacing
technology.
4.4
Conclusion
Overall, the present study seeks to contribute to the maturation of neuroscience: as our discipline continues to
produce increasingly larger datasets (Markiewicz et al., 2021; Gorgolewski et al., 2016) and extensive research
findings (Yarkoni et al., 2011; Dockès et al., 2020), comprehensive benchmarking is going to be an essential
tool for modeling and understanding the neural representations of human cognition.
15


## Page 16

References
Hossein Adeli, Sun Minni, and Nikolaus Kriegeskorte. Predicting brain activity using transformers. bioRxiv, 2023. doi:
10.1101/2023.08.02.551743. https://www.biorxiv.org/content/early/2023/08/05/2023.08.02.551743.
Emily J Allen, Ghislain St-Yves, Yihan Wu, Jesse L Breedlove, Jacob S Prince, Logan T Dowdle, Matthias Nau, Brad
Caron, Franco Pestilli, Ian Charest, et al. A massive 7T fMRI dataset to bridge cognitive neuroscience and artificial
intelligence. Nature neuroscience, 25(1):116–126, 2022.
Richard Antonello, Aditya Vaidya, and Alexander Huth. Scaling laws for language encoding models in fMRI. Advances
in Neural Information Processing Systems, 36, 2024.
Kristijan Armeni, Umut Güçlü, Marcel van Gerven, and Jan-Mathijs Schoffelen.
A 10-hour within-participant
magnetoencephalography narrative dataset to test models of language comprehension. Scientific Data, 9(1):278,
2022.
Yohann Benchetrit, Hubert Banville, and Jean-Rémi King. Brain decoding: toward real-time reconstruction of visual
perception. In ICLR 2024, 2024.
Laurent Bonnasse-Gahot and Christophe Pallier. fMRI predictors based on language models of increasing complexity
recover brain left lateralization. arXiv preprint arXiv:2405.17992, 2024.
Nadine Chang, John A Pyles, Austin Marcus, Abhinav Gupta, Michael J Tarr, and Elissa M Aminoff. BOLD5000, a
public fMRI dataset while viewing 5000 visual images. Scientific data, 6(1):49, 2019.
Omar Chehab, Alexandre Défossez, Loiseau Jean-Christophe, Alexandre Gramfort, and Jean-Remi King. Deep
recurrent encoder: an end-to-end network to model magnetoencephalography at scale. Neurons, Behavior, Data
Analysis, and Theory, 2022.
Zijiao Chen, Jiaxin Qing, Tiange Xiang, Wan Lin Yue, and Juan Helen Zhou. Seeing beyond the brain: Conditional
diffusion model with sparse masked modeling for vision decoding. In Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition, pages 22710–22720, 2023.
Colin Conwell, Jacob S Prince, Kendrick N Kay, George A Alvarez, and Talia Konkle. What can 1.8 billion regressions
tell us about the pressures shaping high-level visual representation in brains and machines? BioRxiv, pages 2022–03,
2022.
Alexandre Défossez, Charlotte Caucheteux, Jérémy Rapin, Ori Kabeli, and Jean-Rémi King. Decoding speech from
non-invasive brain recordings. arXiv preprint arXiv:2208.12266, 2022.
Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. Imagenet: A large-scale hierarchical image
database. In 2009 IEEE conference on computer vision and pattern recognition, pages 248–255. IEEE, 2009.
Jérôme Dockès, Russell A Poldrack, Romain Primet, Hande Gözükan, Tal Yarkoni, Fabian Suchanek, Bertrand Thirion,
and Gaël Varoquaux. NeuroQuery, comprehensive meta-analysis of human brain mapping. elife, 9:e53385, 2020.
Michael Eickenberg, Alexandre Gramfort, Gaël Varoquaux, and Bertrand Thirion. Seeing it all: Convolutional network
layers map the function of the human visual system. NeuroImage, 152:184–194, 2017.
Oscar Esteban, Christopher J Markiewicz, Ross W Blair, Craig A Moodie, A Ilkay Isik, Asier Erramuzpe, James D
Kent, Mathias Goncalves, Elizabeth DuPre, Madeleine Snyder, et al. fMRIPrep: a robust preprocessing pipeline for
functional MRI. Nature methods, 16(1):111–116, 2019.
Matteo Ferrante, Tommaso Boccato, and Nicola Toschi. Semantic brain decoding: from fMRI to conceptually similar
image reconstruction of visual stimuli. arXiv preprint arXiv:2212.06726, 2022.
Bruce Fischl, Martin I. Sereno, Roger B.H. Tootell, and Anders M. Dale. High-resolution intersubject averaging and a
coordinate system for the cortical surface. Human Brain Mapping, 8(4):272–284, 1999.
V. S. Fonov, A. C. Evans, R. C. McKinstry, C. R. Almli, and D. L. Collins. Unbiased nonlinear average age-appropriate
brain templates from birth to adulthood. NeuroImage, 47:S102, 2009. ISSN 1053-8119. doi: https://doi.org/10.
1016/S1053-8119(09)70884-5. https://www.sciencedirect.com/science/article/pii/S1053811909708845.
Karl J Friston, Chris D Frith, Robert Turner, and Richard SJ Frackowiak. Characterizing evoked hemodynamics with
fMRI. Neuroimage, 2(2):157–165, 1995.
Alessandro T Gifford, Kshitij Dwivedi, Gemma Roig, and Radoslaw M Cichy. A large and rich EEG dataset for
modeling human visual object recognition. NeuroImage, 264:119754, 2022.
16


## Page 17

Krzysztof J Gorgolewski, Tibor Auer, Vince D Calhoun, R Cameron Craddock, Samir Das, Eugene P Duff, Guillaume
Flandin, Satrajit S Ghosh, Tristan Glatard, Yaroslav O Halchenko, et al. The brain imaging data structure, a
format for organizing and describing outputs of neuroimaging experiments. Scientific data, 3(1):1–9, 2016.
Tijl Grootswagers, Ivy Zhou, Amanda K Robinson, Martin N Hebart, and Thomas A Carlson. Human EEG recordings
for 1,854 concepts presented in rapid serial visual presentation streams. Scientific Data, 9(1):3, 2022.
Laura Gwilliams, Graham Flick, Alec Marantz, Liina Pylkkänen, David Poeppel, and Jean-Rémi King. Introducing
MEG-MASC a high-quality magneto-encephalography dataset for evaluating natural speech processing. Scientific
data, 10(1):862, 2023.
Martin N Hebart, Adam H Dickter, Alexis Kidder, Wan Y Kwok, Anna Corriveau, Caitlin Van Wicklin, and Chris I
Baker. Things: A database of 1,854 object concepts and more than 26,000 naturalistic object images. PloS one, 14
(10):e0223792, 2019.
Martin N Hebart, Oliver Contier, Lina Teichmann, Adam H Rockter, Charles Y Zheng, Alexis Kidder, Anna Corriveau,
Maryam Vaziri-Pashkam, and Chris I Baker. THINGS-data, a multimodal collection of large-scale datasets for
investigating object representations in human brain and behavior. eLife, 12:e82580, feb 2023. ISSN 2050-084X. doi:
10.7554/eLife.82580. https://doi.org/10.7554/eLife.82580.
Arthur E Hoerl and Robert W Kennard. Ridge regression: Biased estimation for nonorthogonal problems. Technometrics,
12(1):55–67, 1970.
Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego
de Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, Tom Hennigan, Eric Noland, Katie Millican,
George van den Driessche, Bogdan Damoc, Aurelia Guy, Simon Osindero, Karen Simonyan, Erich Elsen, Oriol
Vinyals, Jack W. Rae, and Laurent Sifre. Training compute-optimal large language models. In Proceedings of the
36th International Conference on Neural Information Processing Systems, NeurIPS ’22, Red Hook, NY, USA, 2024.
Curran Associates Inc. ISBN 9781713871088.
Tomoyasu Horikawa, Masako Tamaki, Yoichi Miyawaki, and Yukiyasu Kamitani. Neural decoding of visual imagery
during sleep. Science, 340(6132):639–642, 2013.
Yukiyasu Kamitani and Frank Tong. Decoding the visual and subjective contents of the human brain. Nature
neuroscience, 8(5):679–685, 2005.
Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B. Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec
Radford, Jeffrey Wu, and Dario Amodei. Scaling laws for neural language models, 2020. https://arxiv.org/abs/
2001.08361.
Jean-Rémi King, Laura Gwilliams, Chris Holdgraf, Jona Sassenhagen, Alexandre Barachant, Denis Engemann, Eric
Larson, and Alexandre Gramfort. Encoding and Decoding Framework to Uncover the Algorithms of Cognition. In
The Cognitive Neurosciences. The MIT Press, 05 2020. ISBN 9780262356176. doi: 10.7551/mitpress/11442.003.0076.
https://doi.org/10.7551/mitpress/11442.003.0076.
Diederik P Kingma and Jimmy Ba. Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980,
2014.
Nikolaus Kriegeskorte and Jörn Diedrichsen. Inferring brain-computational mechanisms with models of activity
measurements. Philosophical Transactions of the Royal Society B: Biological Sciences, 371(1705):20160278, 2016.
Tsung-Yi Lin, Michael Maire, Serge J. Belongie, Lubomir D. Bourdev, Ross B. Girshick, James Hays, Pietro Perona,
Deva Ramanan, Piotr Doll’a r, and C. Lawrence Zitnick. Microsoft COCO: common objects in context. CoRR,
abs/1405.0312, 2014. http://arxiv.org/abs/1405.0312.
Yunfeng Lin, Jiangbei Li, and Hanjing Wang. DCNN-GAN: Reconstructing realistic image from fMRI. In 2019 16th
International Conference on Machine Vision Applications (MVA), pages 1–6. IEEE, 2019.
Weijian Mai and Zhijun Zhang. UniBrain: Unify image reconstruction and captioning all in one diffusion model from
human brain activity. arXiv preprint arXiv:2308.07428, 2023.
Christopher J Markiewicz, Krzysztof J Gorgolewski, Franklin Feingold, Ross Blair, Yaroslav O Halchenko, Eric Miller,
Nell Hardcastle, Joe Wexler, Oscar Esteban, Mathias Goncavles, et al. The OpenNeuro resource for sharing of
neuroscience data. Elife, 10:e71774, 2021.
17


## Page 18

Yoichi Miyawaki, Hajime Uchida, Okito Yamashita, Masa-aki Sato, Yusuke Morito, Hiroki C Tanabe, Norihiro Sadato,
and Yukiyasu Kamitani. Visual image reconstruction from human brain activity using a combination of multiscale
local image decoders. Neuron, 60(5):915–929, 2008.
Thomas Naselaris, Ryan J Prenger, Kendrick N Kay, Michael Oliver, and Jack L Gallant. Bayesian reconstruction of
natural images from human brain activity. Neuron, 63(6):902–915, 2009.
Thomas Naselaris, Kendrick N Kay, Shinji Nishimoto, and Jack L Gallant. Encoding and decoding in fMRI. Neuroimage,
56(2):400–410, 2011.
Samuel A Nastase, Yun-Fei Liu, Hanna Hillman, Asieh Zadbood, Liat Hasenfratz, Neggin Keshavarzian, Janice Chen,
Christopher J Honey, Yaara Yeshurun, Mor Regev, et al. The “Narratives” fMRI dataset for evaluating models of
naturalistic language comprehension. Scientific data, 8(1):250, 2021.
Maxime Oquab, Timothée Darcet, Théo Moutakanni, Huy Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez,
Daniel Haziza, Francisco Massa, Alaaeldin El-Nouby, Mahmoud Assran, Nicolas Ballas, Wojciech Galuba, Russell
Howes, Po-Yao Huang, Shang-Wen Li, Ishan Misra, Michael Rabbat, Vasu Sharma, Gabriel Synnaeve, Hu Xu, Hervé
Jegou, Julien Mairal, Patrick Labatut, Armand Joulin, and Piotr Bojanowski. DINOv2: Learning robust visual
features without supervision, 2023.
Josue Ortega Caro, Antonio Henrique Oliveira Fonseca, Christopher Averill, Syed A Rizvi, Matteo Rosati, James L
Cross, Prateek Mittal, Emanuele Zappala, Daniel Levine, Rahul M Dhodapkar, et al. BrainLM: A foundation model
for brain activity recordings. bioRxiv, pages 2023–09, 2023.
Furkan Ozcelik and Rufin VanRullen. Natural scene reconstruction from fMRI signals using generative latent diffusion.
Scientific Reports, 13(1):15666, 2023.
Furkan Ozcelik, Bhavin Choksi, Milad Mozafari, Leila Reddy, and Rufin VanRullen. Reconstruction of perceived
images from fmri patterns and semantic brain exploration using instance-conditioned gans, 2022. https://arxiv.org/
abs/2202.12692.
F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss,
V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, M. Perrot, and E. Duchesnay. Scikit-learn:
Machine learning in Python. Journal of Machine Learning Research, 12:2825–2830, 2011.
Russ Poldrack. Neuroscience: The risks of reading the brain. Nature, page 156, 2017.
Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda
Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, and Ilya Sutskever. Learning transferable visual models
from natural language supervision, 2021.
Jan-Mathijs Schoffelen, Robert Oostenveld, Nietzsche HL Lam, Julia Uddén, Annika Hultén, and Peter Hagoort. A
204-subject multimodal neuroimaging dataset to study language processing. Scientific data, 6(1):17, 2019.
Martin Schrimpf, Jonas Kubilius, Ha Hong, Najib J Majaj, Rishi Rajalingham, Elias B Issa, Kohitij Kar, Pouya
Bashivan, Jonathan Prescott-Roy, Franziska Geiger, et al. Brain-score: Which artificial neural network for object
recognition is most brain-like? BioRxiv, page 407007, 2018.
Paul S Scotti, Atmadeep Banerjee, Jimmie Goode, Stepan Shabalin, Alex Nguyen, Ethan Cohen, Aidan J Dempster,
Nathalie Verlinde, Elad Yundler, David Weisberg, et al. Reconstructing the mind’s eye: fMRI-to-image with
contrastive learning and diffusion priors. arXiv preprint arXiv:2305.18274, 2023.
Paul S Scotti, Mihir Tripathy, Cesar Kadir Torrico Villanueva, Reese Kneeland, Tong Chen, Ashutosh Narang, Charan
Santhirasegaran, Jonathan Xu, Thomas Naselaris, Kenneth A Norman, et al. MindEye2: Shared-subject models
enable fMRI-to-image with 1 hour of data. arXiv preprint arXiv:2403.11207, 2024.
Guobin Shen, Dongcheng Zhao, Xiang He, Linghao Feng, Yiting Dong, Jihang Wang, Qian Zhang, and Yi Zeng.
Neuro-vision to language: Enhancing brain recording-based visual reconstruction and language interaction, 2024.
https://arxiv.org/abs/2404.19438.
Guohua Shen, Tomoyasu Horikawa, Kei Majima, and Yukiyasu Kamitani. Deep image reconstruction from human
brain activity. PLoS computational biology, 15(1):e1006633, 2019.
Ken Shirakawa, Yoshihiro Nagano, Misato Tanaka, Shuntaro C. Aoki, Kei Majima, Yusuke Muraki, and Yukiyasu
Kamitani. Spurious reconstruction from brain activity. arXiv preprint arXiv:2405.10078, 2024. https://doi.org/10.
48550/arXiv.2405.10078. Submitted on 16 May 2024.
18


## Page 19

Jerry Tang, Amanda LeBel, Shailee Jain, and Alexander G Huth. Semantic reconstruction of continuous language
from non-invasive brain recordings. Nature Neuroscience, 26(5):858–866, 2023.
Armin Thomas, Christopher Ré, and Russell Poldrack.
Self-supervised learning of brain dynamics from broad
neuroimaging data. Advances in neural information processing systems, 35:21255–21269, 2022.
D.C. Van Essen, K. Ugurbil, E. Auerbach, D. Barch, T.E.J. Behrens, R. Bucholz, A. Chang, L. Chen, M. Corbetta,
S.W. Curtiss, S. Della Penna, D. Feinberg, M.F. Glasser, N. Harel, A.C. Heath, L. Larson-Prior, D. Marcus,
G. Michalareas, S. Moeller, R. Oostenveld, S.E. Petersen, F. Prior, B.L. Schlaggar, S.M. Smith, A.Z. Snyder, J. Xu,
and E. Yacoub. The human connectome project: A data acquisition perspective. NeuroImage, 62(4):2222–2231,
2012. ISSN 1053-8119. doi: https://doi.org/10.1016/j.neuroimage.2012.02.018. https://www.sciencedirect.com/
science/article/pii/S1053811912001954. Connectivity.
Rufin VanRullen and Leila Reddy. Reconstructing faces from fMRI patterns using deep generative neural networks.
Communications biology, 2(1):193, 2019.
Frank Wilcoxon. Individual comparisons by ranking methods. Biometrics Bulletin, 1(6):80–83, 1945. ISSN 00994987.
http://www.jstor.org/stable/3001968.
Jianxiong Xiao, James Hays, Krista A Ehinger, Aude Oliva, and Antonio Torralba. Sun database: Large-scale scene
recognition from abbey to zoo. In 2010 IEEE computer society conference on computer vision and pattern recognition,
pages 3485–3492. IEEE, 2010.
Jonathan Xu, Bruno Aristimunha, Max Emanuel Feucht, Emma Qian, Charles Liu, Tazik Shahjahan, Martyna Spyra,
Steven Zifan Zhang, Nicholas Short, Jioh Kim, et al. Alljoined–a dataset for EEG-to-Image decoding. arXiv preprint
arXiv:2404.05553, 2024.
Daniel LK Yamins, Ha Hong, Charles F Cadieu, Ethan A Solomon, Darren Seibert, and James J DiCarlo. Performance-
optimized hierarchical models predict neural responses in higher visual cortex. Proceedings of the national academy
of sciences, 111(23):8619–8624, 2014.
Chaoqi Yang, M Westover, and Jimeng Sun. BIOT: Biosignal transformer for cross-data learning in the wild. Advances
in Neural Information Processing Systems, 36, 2024.
Tal Yarkoni, Russell A Poldrack, Thomas E Nichols, David C Van Essen, and Tor D Wager. Large-scale automated
synthesis of human functional neuroimaging data. Nature methods, 8(8):665–670, 2011.
Zhizhang Yuan, Fanqi Shen, Meng Li, Yuguo Yu, Chenhao Tan, and Yang Yang. BrainWave: A brain signal foundation
model for clinical applications, 2024. https://arxiv.org/abs/2402.10251.
Bohan Zeng, Shanglin Li, Xuhui Liu, Sicheng Gao, Xiaolong Jiang, Xu Tang, Yao Hu, Jianzhuang Liu, and Baochang
Zhang. Controllable mind visual diffusion model. arXiv preprint arXiv:2305.10135, 2023.
19


## Page 20

Appendix
A
Detailed description of image decoding datasets
A.1
Xu2024 (Alljoined)
Device. EEG was recorded at 512 Hz using a 64-channel BioSemi ActiveTwo system. Subjects. Eight subjects
(two females and six males, mean age of 22 ± 0.64 years old) underwent one or two one-hour sessions, for a
total of 12 sessions. Stimuli. A total of 960 natural images were selected from the shared set of test images
used in Allen et al. (2022) (initially taken from MS-COCO (Lin et al., 2014)). Each image was shown up to
four times per subject across sessions. Images were presented for 300 ms, followed by a 300 ms blank screen.
We set aside 20% of the unique 960 images to use as test set.
A.2
Grootswagers2022 (THINGS-EEG1)
Device. EEG was recorded at 1 kHz using a 64-channel BrainVision ActiChamp system, referenced to Cz.
Subjects. 50 healthy volunteers (36 females and 14 males, mean age of 20.44 ± 2.72 years old) underwent a
single one-hour session each. We discard the last two subjects as their recordings contained a different number
of EEG channels. Stimuli. A total of 22,448 unique images from the THINGS dataset (Hebart et al., 2019)
were shown across sessions for each subject. Out of these, 200 images from distinct categories were selected to
form the test set and were shown 12 times to each subject. Each image was presented for 50 ms, followed by
a 50-ms fixation screen. Of note, test set annotations are not available for subjects 1 and 6. As a result, while
data from these two subjects is included in our training sets, models are not evaluated on them.
A.3
Gifford2022 (THINGS-EEG2)
Device. EEG was recorded at 1 kHz using a 64-channel BrainVision ActiChamp system, referenced to Fz.
Subjects. Ten healthy volunteers (eight females and two males, mean age of 28.5 ± 4 years old) each underwent
four sessions of about 1.6 h each. Stimuli. A total of 16,740 unique images from the THINGS dataset (Hebart
et al., 2019) were shown across sessions for each subject. Among these images, 200 images from distinct
categories were selected to form the test set. Training set images were shown four times to each subject, while
test set images were shown 80 times to each subject. Each image was displayed for 100 ms, followed by a
fixation period of 100 ms.
A.4
Hebart2023meg (THINGS-MEG)
Device. MEG was recorded with a 275-channel CTF system which incorporates a whole-head array of 275
radial 1st order gradiometer SQUID channels sampled at 1,200 Hz. Subjects. Four healthy volunteers (two
females and two males, mean age of 23.25 year old) each underwent 12 sessions of about one hour each. Stimuli.
A total of 22,448 unique images from the THINGS dataset (Hebart et al., 2019) were shown across sessions
for each subject. Among these images, 200 images from distinct categories were selected to form the test
set and shown 12 times to each subject. Each image was displayed for 500 ms, followed by a fixation period
varying from 800 to 1,200 ms.
A.5
Shen2019 (DeepRecon)
Device. Functional MRI was obtained using a 3 Tesla Siemens MAGNETOM Verio scanner. The imaging
used a T2*-weighted gradient-echo EPI multi-band pulse sequence recording the entire brain at TR=2 s (76
slices, slice-thickness 2 mm, slice gap 0 mm and a field-of-view of 192×192 mm). Subjects. To allow fair
comparison with the other datasets included in our study, which contain only natural images, we restrict our
analysis to the training and test natural-image sessions. In this context, three healthy volunteers (one female
and one male, age range 23 to 33 years old) each underwent 18 fMRI sessions of up to 2 hours each. Stimuli.
The subjects saw a total of 1,250 unique images sampled from ImageNet (Deng et al., 2009). During training
sessions (which form our training set), 1,200 unique images were presented 5 times (a total of 6,000 training
20


## Page 21

trials). During test sessions (which form our test set), 50 unique images were shown 24 times each (a total of
1,200 test trials). Each image was displayed for 8 s, with no rest between consecutive image presentations.
A.6
Hebart2023fmri (THINGS-fMRI)
Device. Functional MRI was recorded with a 3 Tesla Siemens Magnetom Prisma scanner and a 32-channel
head coil, using a repetition time (TR) of 1.5 s. The resolution consisted of the whole-brain with 2 mm
isotropic resolution (60 axial slices, 2 mm slice thickness without slice gap, a matrix size of 96×96 and a
field-of-view of 192×192 mm). Subjects. Three healthy volunteers (two females and one male, mean age of
25.33 years old) each underwent 12 sessions of about one hour each. Stimuli. A total of 8,740 unique images
from the THINGS database (Hebart et al., 2019) were shown across sessions for each subject. Among these
images, 100 images from distinct categories were selected to form the test set and shown 12 times to each
subject. Each image was displayed for 500 ms, followed by a fixation period of 4 s.
A.7
Chang2019 (BOLD5000)
Device. Functional MRI was obtained using a 3 Tesla Siemens Verio MR scanner with a 32-channel phased
array head coil. The imaging used a T2*-weighted-gradient recalled-echo EPI multi-band pulse sequence,
sampled at TR=2 s and captured with a resolution of 2×2 mm (69 slices co-planar with the AC/PC line,
slice-thickness 2 mm, slice gap 0 mm, matrix size 106×106 and a field-of-view of 212×212 mm). Subjects. Four
healthy volunteers (three females and one male, age range 25 to 27 years old) each participated in 15 sessions,
except one who completed 9 sessions only. Each session lasted 1.5 hours. Stimuli. The subjects who went
through all 15 sessions saw a total of 4,916 unique images sampled from three datasets: Scene UNderstanding
(Xiao et al., 2010), MS-COCO (Lin et al., 2014) and ImageNet (Deng et al., 2009). A subset of 112 images
were shown 4 times (or 2, 3 or 5 times for a small sample of images) to each subject and were selected to form
the test set. Each image was presented for 1 s, followed by a fixation cross displayed for 9 s.
A.8
Allen2022 (Natural Scenes Dataset, or NSD)
Device. Functional MRI was recorded with a 7 Tesla Siemens Magnetom passively shielded scanner and
a single-channel-transmit, 32-channel-receive RF head coil (Nova Medical) sampled at TR=1.6 s, using a
gradient-echo EPI at 1.8 mm isotropic resolution with whole-brain coverage (84 axial slices, slice thickness
1.8 mm, slice gap 0 mm, a matrix size 120×120 and a field-of-view of 216×216 mm). Subjects. Eight healthy
volunteers (six females and two males, mean age range 19 to 32 years old) each underwent 30-40 fMRI sessions
of about one hour each. Following previous work on this dataset, we use only data from the subjects who
completed the full 40 recording sessions (namely subjects 1, 2, 5, 7). Stimuli. A total of 73,000 natural images
from the MS-COCO dataset (Lin et al., 2014) were shown across subjects and sessions. Each subject saw a
total of 10,000 unique images (each repeated 3 times) across 40 sessions. Of these, 9,000 images were selected
for training, while a common set of 1,000 images seen by all subjects was used for the test set. Each image
was shown for 3 s, with a 1 s blank interval between consecutive image presentations.
B
Matching dataset sizes
Image decoding datasets vary in size across several dimensions including the numbers of subjects, the amount
of recordings per subject, the number of unique images used as well as the number of repetitions of each
unique image. To minimize the impact of these factors for the comparison of different datasets and devices, we
define a matched-trials configuration, where datasets are downsampled to match as closely as possible the size
of Hebart2023fmri, the smallest of the THINGS-derived datasets. We report the numbers of unique images
and presentation trials in the matched-trials and all-trials data configurations for each dataset in Table S1.
For the neuroimaging datasets based on the THINGS images (Hebart et al., 2019) (Grootswagers2024,
Gifford2022, Hebart2023meg and Hebart2023fmri), we use 7,428 unique images (i.e., the number of training
images in Hebart2023fmri after removing test set categories from the original training set; see Section 2.5)
for the training set, each presented only once. In Gifford2022, contrarily to other datasets, each training
image was presented multiple times. Therefore, we sample a unique presentation of each training image per
21


## Page 22

Table S1 Description of the data quantity configurations. The number of trials corresponds to the number of total
images presentations available in a configuration when including all subjects and repetitions.
Matched trials
All trials
Both configurations
Study
# train+valid
unique images
# train+valid
trials
# train+valid
unique images
# train+valid
trials
# test unique
images
# test
trials
Xu2024
777
34,868
777
34,868
100
4,472
Grootswagers2022
7,428
353,172
19,848
943,892
100
55,200
Gifford2022
7,428
300,145
16,540
668,400
100
81,091
Hebart2023meg
7,428
29,712
19,848
79,392
100
4,800
Shen2019
1,200
19,800
1,200
19,800
50
3,960
Hebart2023fmri
7,428
22,284
7,428
22,284
100
3,600
Chang2019
4,803
17,255
4,803
17,255
100
1,422
Allen2022
29,712
89,136
36,000
108,000
100
1,200
subject. Since the ultra-high field fMRI dataset (Allen2022) does not make use of the THINGS images, we
randomly select 7,428 unique images per subject to build a training set (with a single presentation per image).
Xu2024, Shen2019 and Chang2019 contain fewer image presentations than Hebart2023fmri, therefore we
do not downsample them and keep all available training examples. Finally, for each dataset, we build a test
set by randomly selecting 100 unique images (50 for Shen2019) from the original test splits. This test set is
used in both matched and all trial configurations.
C
Encoding analysis
We perform encoding analyses (King et al., 2020) to verify that the image decoding datasets (Table 1) capture
the expected spatial response over the occipital cortex. We extract the DINOv2-giant average token of the
output layer (see Section 2.4) for the images of each dataset. For each subject of each dataset, we build a
collection of image latent and brain response pairs, where we use the brain response at a fixed time tenc after
stimulus onset (picked using the approximate maximal response seen in Figure 2A and B). We use tenc = 0.2 s
for M/EEG datasets, and dataset-specific offsets for fMRI datasets (Shen2019: 9.5 s, Hebart2023fmri: 4.5 s,
Chang2019: 5.0 s and Allen2022: 5.5 s). Linear ridge regression encoders (RidgeCV with alpha sampled
log-linearly between 10−12 and 1022) are then trained to map image latents to the response of a single M/EEG
channel or single fMRI voxel. We use Pearson correlation between ground truth and predicted brain responses
on a held-out test set (2-fold cross-validation) to evaluate the quality of the encoding. Finally, correlation
values are averaged across subjects within each dataset, and the average is plotted on topographical maps and
inflated brain volumes (Figure 1C and S1).
D
Hyperparameter search and brain module configurations
We ran a random hyperparameter search to identify optimal architecture configurations for the different
brain devices under different data regimes. We picked one representative dataset per brain device family
(EEG: Gifford2022, MEG: Hebart2023meg, fMRI: Hebart2023fmri) and define two data regimes: “large”
(all subjects, all trials) and “medium” (one subject, all trials). To perform hyperparameter search on a given
dataset, we further split the existing training set by randomly sampling 20% of the image categories and using
the corresponding examples as an inner test set on which model performance is to be compared. For both
data regimes, we then randomly sampled values for the following hyperparameters:
• Batch size: uniform over {32, 64, 128, 256, 512}
• Learning rate: uniform over [3 × 10−5, 3 × 10−4, 3 × 10−3]
For the M/EEG module only:
• Number of convolutional blocks: uniform over {0, 1, 2, 3, 4, 5}
22


## Page 23

Figure S1 Encoding models trained to predict each M/EEG channel or fMRI voxel from the presented images yield the
expected spatial response over the occipital region as measured with Pearson correlation.
Table S2 Results of hyperparameter search on EEG data.
Hyperparameter
Medium
Large
# convolutional blocks
2
4
Hidden size
50
396
Backbone output size
152
1411
Batch size
32
256
Learning rate
3 × 10−4
3 × 10−4
• Hidden size: log-uniform over [32, 512]
• Backbone output size: log-uniform over [64, 2048]
For the fMRI module only:
• Hidden size: log-uniform over [32, 2048]
• Number of blocks: uniform over {0, 1, 2, 3}
• CLIP head: with/without
Sampling of hyperparameters was repeated a total of 75 times for each brain device and data regime. Moreover,
the search was repeated three times (on three different random subjects) when searching on the “medium”
data regime. Finally, the configuration yielding the best Pearson R on the inner test set was selected to be
used in the different experiments. The chosen configurations for EEG, MEG and fMRI modules are presented
in Table S2, S3 and S4. The resulting architectures are presented in Table S5, S6 and S7.
E
Reproduction of main results in the matched-trials setting
We reproduce the results presented in the main text by using the matched-trials setting (see Appendix B),
i.e., we match the available quantity of data across datasets as closely as possible to allow comparing devices
more directly. Figure S2 presents stepwise decoding results. Figure S3 presents results from the test-time
averaging analyses.
23


## Page 24

Table S3 Results of hyperparameter search on MEG data.
Hyperparameter
Medium
Large
# convolutional blocks
4
5
Hidden size
181
442
Backbone output size
564
1526
Batch size
64
512
Learning rate
3 × 10−4
3 × 10−4
Table S4 Results of hyperparameter search on fMRI data.
Hyperparameter
Medium
Large
Hidden size
553
1552
# blocks
2
0
CLIP head
No
Yes
Batch size
256
64
Learning rate
3 × 10−4
3 × 10−3
Table S5 Description of the brain module architectures used with EEG data. We provide the input and output shapes
for each layer, as well as the corresponding number of parameters.
Medium
Large
Layer
Input
Output
# params
Input
Output
# params
Spatial attention
(64, 144)
(270, 144)
552,960
(64, 144)
(270, 144)
552,960
Linear projection
(270, 144)
(181, 144)
49,051
(270, 144)
(442, 144)
119,782
Subject layer
(181, 144)
(181, 144)
32,761
(442, 144)
(442, 144)
1,953,640
Residual dilated conv blocks
(181, 144)
(181, 144)
1,578,320
(442, 144)
(442, 144)
11,739,520
1x1 conv block
(181, 144)
(564, 144)
270,616
(442, 144)
(1526, 144)
1,742,122
Temporal aggregation
(564, 144)
(564, 1)
145
(1526, 144)
(1526, 1)
145
MSE projection head
(564, 1)
(564, 1536)
867,840
(1526, 1)
(1536, 1)
2,345,472
CLIP projection head
(564, 1)
(564, 1536)
867,840
(1526, 1)
(1536, 1)
2,345,472
Total
4,219,533
20,799,113
Table S6 Description of the brain module architectures used with MEG data.
Medium
Large
Layer
Input
Output
# params
Input
Output
# params
Spatial attention
(272, 180)
(270, 180)
552,960
(272, 180)
(270, 180)
552,960
Linear projection
(270, 180)
(50, 180)
13,550
(270, 180)
(396, 180)
107,316
Subject layer
(50, 180)
(50, 180)
2,500
(396, 180)
(396, 180)
627,264
Residual dilated conv blocks
(50, 180)
(50, 180)
60,800
(396, 180)
(396, 180)
7,539,840
1x1 conv block
(50, 180)
(152, 180)
20,452
(396, 180)
(1411, 180)
1,433,347
Temporal aggregation
(152, 180)
(152, 1)
181
(1411, 180)
(1411, 1)
181
MSE projection head
(152, 1)
(1536, 1)
235,008
(1411, 1)
(1536, 1)
2,168,832
CLIP projection head
(152, 1)
(1536, 1)
235,008
(1411, 1)
(1536, 1)
2,168,832
Total
1,120,459
14,598,572
24


## Page 25

Table S7 Description of the brain module architectures used with fMRI data.
Medium
Large
Layer
Input
Output
# params
Input
Output
# params
Subject layer
(20484, 5)
(553, 5)
33,982,956
(20484, 5)
(1552, 5)
127,164,672
TR layer
(553, 5)
(553, 5)
1,532,916
(1552, 5)
(1552, 5)
12,054,384
Residual conv blocks
(553, 5)
(553, 5)
614,936
-
-
-
Temporal aggregation
(553, 5)
(553, 1)
6
(1552, 5)
(1552, 1)
6
Linear projection
(553, 1)
(1536, 1)
850,944
(1552, 1)
(1536, 1)
2,385,408
MSE projection head
(1536, 1)
(1536, 1)
2,360,832
(1536, 1)
(1536, 1)
2,360,832
CLIP projection head
(1536, 1)
(1536, 1)
-
(1536, 1)
(1536, 1)
2,363,904
Total
39,342,590
146,329,206
Figure S4 and S5 show the retrieval and generation results.
F
Cost estimation of neuroimaging data collection
We surveyed publicly available hourly cost estimates from research institutions or third-party providers that
offer a neuroimaging data collection service. For EEG, we used commercial third-party pricing for US-based
services6. For MEG, we used cost estimates from a European-based research center7, which we converted
from EUR to USD at a rate of 1.1 (November 2024). For fMRI 3T and 7T, we used cost estimates from a
US-based research hospital center8. Finally, when a price range was provided (e.g. corresponding to different
pricing tiers for internal vs. external collaborators), we used the average between lowest and highest price for
each device type. Based on this information, hourly cost (in USD) was estimated at $263 for EEG, $550 for
MEG, $935 for 3T fMRI and $1093 for 7T fMRI.
G
Quality of image reconstructions across devices and test-time averaging
strategies
Figure S7 shows for each device the reconstructions we obtain for a sample of three stimuli. These three stimuli
were chosen to present a broader view of reconstruction quality, compared to the best-case cherry-picking
of Figure 5. Figure S6 shows the same results, but in the matched-trials data configuration. These results
confirm that aggregating predictions benefits high- and medium-quality reconstructions, though it is unclear
whether it actually benefits bad reconstructions.
Finally, Table S8 and S9 presents the generation metrics defined in Section 2.9 and the additional metrics
reported in recent works (Ozcelik and VanRullen, 2023; Scotti et al., 2023, 2024) for each representative
dataset, each test-time averaging strategy and for each of the all-trials and matched-trials settings.
6https://brainarcevaluations.com/pricing/ and https://sadarpsych.com/services/data-collection/.
7https://www.bcbl.eu/en/infrastructure-equipment/meg.
8https://www.brighamandwomens.org/radiology/research-imaging-core/pricing.
25


## Page 26

0.0
0.5
1.0
1.5
Time (s)
0.00
0.05
Pearson R
A
Linear
0.0
0.5
1.0
1.5
Time (s)
0.00
0.05
Pearson R
B
Deep neural networks
0
5
10
15
Time (s)
0.0
0.2
Pearson R
C
0
5
10
15
Time (s)
0.0
0.2
Pearson R
D
Subjects
0.0
0.1
0.2
0.3
Pearson R
E
1h
10h
40h
EEG: Xu2024
EEG: Gifford2022
EEG: Grootswagers2022
MEG: Hebart2023meg
fMRI 3T: Shen2019
fMRI 3T: Hebart2023fmri
fMRI 3T: Chang2019
fMRI 7T: Allen2022
Figure S2 Stepwise image decoding analyses in the matched-trials setting for (left) linear and (right) deep learning
models. See description of Figure 2.
0
2
Time (s)
0.0
0.1
Pearson R
A
EEG
Xu2024
0
2
Time (s)
0.00
0.05
0.10
EEG
Grootswagers2022
0
2
Time (s)
0.0
0.1
EEG
Gifford2022
0
2
Time (s)
0.0
0.1
MEG
Hebart2023meg
0
20
Time (s)
0.0
0.1
fMRI 3T
Shen2019
0
20
Time (s)
0.0
0.1
fMRI 3T
Hebart2023fmri
0
20
Time (s)
0.0
0.1
0.2
fMRI 3T
Chang2019
0
20
Time (s)
0.0
0.2
0.4
fMRI 7T
Allen2022
0
2
Time (s)
0.0
0.1
0.2
Pearson R
B
0
2
Time (s)
0.0
0.1
0
2
Time (s)
0.0
0.1
0.2
0
2
Time (s)
0.0
0.1
0.2
0
20
Time (s)
0.0
0.1
0
20
Time (s)
0.0
0.1
0
20
Time (s)
0.0
0.1
0.2
0
20
Time (s)
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
Pearson R
C
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test reps
0.0
0.2
0.4
# test repetitions
1
2
3
6
12
24
48
80
All (cross subject)
Figure S3 Decoding of the image embedding as a function of time (x-axis) and number of test-time repetitions (color)
using deep learning models, in the matched-trials setting. See description of Figure 3.
26


## Page 27

Figure S4 Image retrieval across devices in the matched-trials setting. See description of Figure 4.
27


## Page 28

Figure S5 Image reconstruction across devices in the matched-trials setting. See description of Figure 5.
Figure S6 Image reconstruction across devices in the full-trials setting. For each study, a sample of 3 stimuli showing
various qualities of reconstructions obtained (left: good quality, middle: lower quality, right: failure case) from
single-trial brain signals, and two increasingly large aggregations (averaging embedding predictions at subject-level
and at instance-level).
28


## Page 29

Figure S7 Image reconstruction across devices in the matched-trials setting. For each study, a sample of 3 stimuli
showing various qualities of reconstructions obtained (left: good quality, middle: lower quality, right: failure case) from
single-trial brain signals, and two increasingly large aggregations (averaging embedding predictions at subject-level
and at instance-level).
Table S8 Quantitative evaluation of reconstruction quality from each reconstructed study with different test-time
averaging strategies, in the all-trials setting (see Section 2.9 for AlexNet-2-R and CLIP-Final-R metric definitions).
Study
Averaging
PixCorr ↑
SSIM ↑
AlexNet-2 ↑
AlexNet-5 ↑
CLIP-Final ↑
InceptionV3 ↑
SwAV ↓
AlexNet-2-R ↑
CLIP-Final-R ↑
Gifford2022
single-trial
0.084
0.252
0.681
0.722
0.621
0.561
0.631
0.096
0.567
subject-average
0.138
0.265
0.793
0.86
0.754
0.695
0.573
0.118
0.596
instance-average
0.126
0.249
0.822
0.883
0.777
0.728
0.571
0.125
0.608
Hebart2023meg
single-trial
0.064
0.292
0.702
0.762
0.696
0.601
0.61
0.098
0.565
subject-average
0.081
0.294
0.799
0.869
0.743
0.685
0.573
0.12
0.591
instance-average
0.083
0.286
0.78
0.892
0.807
0.701
0.569
0.116
0.603
Hebart2023fmri
single-trial
0.08
0.234
0.62
0.667
0.682
0.596
0.642
0.087
0.561
subject-average
0.086
0.25
0.658
0.741
0.718
0.608
0.622
0.093
0.577
instance-average
0.058
0.233
0.67
0.754
0.736
0.62
0.62
0.093
0.573
Allen2022
single-trial
0.119
0.19
0.742
0.793
0.781
0.768
0.533
0.11
0.588
subject-average
0.11
0.19
0.75
0.807
0.839
0.793
0.503
0.118
0.616
instance-average
0.192
0.221
0.842
0.89
0.888
0.846
0.452
0.139
0.661
Table S9 Quantitative evaluation of reconstruction quality from each reconstructed study with different test-time
averaging strategies, in the matched-trials setting.
Study
Averaging
PixCorr ↑
SSIM ↑
AlexNet-2 ↑
AlexNet-5 ↑
CLIP-Final ↑
InceptionV3 ↑
SwAV ↓
AlexNet-2-R ↑
CLIP-Final-R ↑
Gifford2022
single-trial
0.077
0.22
0.621
0.687
0.625
0.597
0.648
0.084
0.557
subject-average
0.132
0.246
0.678
0.734
0.671
0.63
0.624
0.091
0.576
instance-average
0.101
0.239
0.711
0.776
0.716
0.652
0.61
0.1
0.587
Hebart2023meg
single-trial
0.088
0.258
0.636
0.729
0.64
0.589
0.642
0.087
0.553
subject-average
0.09
0.259
0.695
0.772
0.715
0.631
0.621
0.099
0.567
instance-average
0.083
0.264
0.733
0.823
0.751
0.593
0.606
0.103
0.586
Hebart2023fmri
single-trial
0.08
0.234
0.62
0.667
0.682
0.596
0.642
0.087
0.561
subject-average
0.086
0.25
0.658
0.741
0.718
0.608
0.622
0.093
0.577
instance-average
0.058
0.233
0.67
0.754
0.736
0.62
0.62
0.093
0.573
Allen2022
single-trial
0.124
0.185
0.672
0.742
0.753
0.708
0.551
0.102
0.586
subject-average
0.129
0.19
0.728
0.799
0.78
0.772
0.535
0.111
0.596
instance-average
0.154
0.22
0.773
0.858
0.862
0.837
0.471
0.124
0.644
29


