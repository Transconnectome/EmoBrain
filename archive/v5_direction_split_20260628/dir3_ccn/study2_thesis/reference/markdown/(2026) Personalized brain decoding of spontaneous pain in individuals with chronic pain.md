# (2026) Personalized brain decoding of spontaneous pain in individuals with chronic pain

**Source:** (2026) Personalized brain decoding of spontaneous pain in individuals with chronic pain.pdf

---

## Page 1

Nature Neuroscience
nature neuroscience
https://doi.org/10.1038/s41593-026-02221-3
Article
Personalized brain decoding of spontaneous 
pain in individuals with chronic pain
 
Jae-Joong Lee 
  1, Seongwoo Jo2,6, Sungkun Cho2 & Choong-Wan Woo 
  1,3,4,5 
Spontaneous pain is a hallmark of chronic pain disorders, but its assessment 
remains limited by the lack of objective biomarkers. Here we used precision 
functional magnetic resonance imaging data, collected over more than 
half a year from two individuals with chronic pain, to develop personalized 
brain-decoding models of spontaneous pain. The personalized decoding 
models accurately tracked fluctuations in spontaneous pain intensity across 
sessions, runs and minutes (Participant 1: prediction–outcome correlation, 
r = 0.40–0.61; Participant 2: r = 0.51–0.65) and effectively discriminated 
between median-dichotomized high- versus low-pain states (Participant 1: 
area under the curve = 0.71–0.87; Participant 2: area under the curve =  
0.76–0.93). Model performance improved with increased training data, 
with conventional data quantities failing to achieve significant predictive 
accuracy. Furthermore, each model relied on individually unique brain 
features and did not generalize across participants. This study indicates 
that functional magnetic resonance imaging can assess spontaneous pain, 
highlighting the need for precise, patient-specific approaches.
Chronic pain is one of the most prevalent healthcare problems and 
a leading cause of disability1. It is characterized by the presence of 
spontaneous pain, which occurs without an overt noxious stimulus and 
fluctuates across multiple timescales2,3. The current clinical assessment 
of chronic pain largely relies on self-reported intensity ratings, a meas-
ure that is neither fully reliable4 nor informative about the underlying 
neurophysiological mechanisms5. Pain biomarkers based on brain 
features could supplement the self-reported measures by providing 
additional information about pain, offering a pluralistic approach to 
pain assessment. These biomarkers could also improve our understand-
ing of the neural mechanisms underlying pain and provide a basis for 
more effective diagnosis and treatment5.
To date, no brain-based biomarker has demonstrated clinical 
potential as a surrogate for subjective pain reports. Although a few 
neuroimaging studies identified brain patterns that track self-reported 
intensity ratings of stimulus-evoked pain in healthy participants6–8, 
their generalizability to stimulus-free spontaneous pain in clinical 
population remains unclear9,10. Furthermore, clinically useful surrogate 
endpoints should ideally capture the temporal fluctuations of pain 
within individuals3,11, a need not addressed by cross-sectional studies 
predicting pain severity measured at a single time point8,12,13.
Personalized brain decoding may hold promise for addressing this 
unmet need14–16. This approach involves intensive longitudinal sam-
pling of individuals to develop precise, person-specific brain markers, 
providing a unique opportunity to directly track intra-individual varia-
tions in spontaneous pain3,17,18. Importantly, personalized brain decod-
ing leverages densely sampled data of individuals while accounting 
for interindividual heterogeneity in brain representations, potentially 
enhancing predictive power16,18. This approach has shown promising 
results in domains such as limb movement19, speech20 and depres-
sion21. However, progress in developing personalized biomarkers for 
spontaneous pain remains limited.
All existing models have primarily targeted to differentiate 
between simplified binary states of spontaneous pain (that is, high 
versus low) and have not been successful in predicting continuous 
self-reported pain ratings22, limiting their clinical application, where 
Received: 25 April 2025
Accepted: 23 January 2026
Published online: xx xx xxxx
 Check for updates
1Center for Neuroscience Imaging Research, Institute for Basic Science, Suwon, South Korea. 2Department of Psychology, Chungnam National University, 
Daejeon, South Korea. 3Department of Biomedical Engineering, Sungkyunkwan University, Suwon, South Korea. 4Department of Intelligent Precision 
Healthcare Convergence, Sungkyunkwan University, Suwon, South Korea. 5Department of Brain Science and Engineering, Sungkyunkwan University, 
Suwon, South Korea. 6Deceased: Seongwoo Jo. 
 e-mail: waniwoo@skku.edu


## Page 2

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
Results
Brain decoding of spontaneous pain intensity
We examined a series of patients (n = 3, with two included in the final 
analyses) with fibromyalgia, a prevalent chronic pain condition char-
acterized by widespread, spontaneous pain26. To achieve extensive 
sampling of brain activity within individuals, participants underwent 
longitudinal fMRI scanning across multiple sessions on separate days 
(Fig. 1a). Two of the three enrolled participants completed more than 
the requisite 15 sessions (Participant 1: 23 sessions; Participant 2: 28 
sessions) and are the focus of this study (see Supplementary Fig. 1 for 
Participant 3’s results). Each session consisted of three 10-minute fMRI 
runs, during which participants provided continuous self-reports of 
their spontaneous pain (Fig. 1b; see Supplementary Fig. 2 for continu-
ous pain ratings of all runs and sessions). Before the second run, a per-
sonalized maneuver was performed to induce naturalistic yet tolerable 
fluctuations in pain (Participant 1: muscle tightening; Participant 2: 
straight leg raising; Supplementary Methods).
We estimated concurrent, moment-by-moment changes in 
brain functional connectivity (that is, edge timeseries27) from the 
fMRI data (Fig. 1c). Note that we employed individual-specific brain 
sensitivity to gradual changes in pain is crucial5,11,23. Also, previous 
personalized decoding models have relied on intracranial neural 
recordings from a restricted number of brain regions19–22, which 
may be suboptimal for decoding pain, as pain engages distributed 
brain networks6,24,25. Functional magnetic resonance imaging (fMRI), 
in contrast, provides a whole-brain measurement with reasonable 
spatiotemporal resolution and has shown promise in identifying 
distributed brain patterns associated with self-reported spontane-
ous pain8,12,13. Moreover, fMRI is non-invasive, making it accessible 
to a broader population of patients with chronic pain. Thus, fMRI 
offers an advantage over intracranial recordings that require 
surgical implantation.
Here we investigated whether personalized brain-decoding mod-
els based on fMRI could predict fluctuations in spontaneous pain 
intensity. To this end, we conducted an intensive longitudinal study 
over more than half a year in individuals with chronic pain, repeat-
edly measuring self-reported pain alongside whole-brain activity. By 
leveraging these densely sampled data, we aimed to develop precise, 
person-specific models capable of tracking moment-by-moment 
changes in spontaneous pain.
0
50
100
150
200
250
Participant 1
Participant 2
23 sessions
28 sessions
0.92
0.87
0.75
0.08
Brain
connectivity
Pain ratings
Positive
Negative
Weights
×
Decoding model
=
0.47
Brain
connectivity
Predicted
pain reports
Training data
Testing data
×
Decoding model
=
Machine learning
(LASSO-PCR)
d
Please continuously 
report the intensity 
of the current pain.
Time
Pain report (VAS)
0
1.0
0.5
b
Positive
Negative
Time
...
Region
Region
i
j
Edge ij 
Region i 
Region j 
Edge ij 
Time
c
Time
Time
e
a
Days since the first session
Participant 2, session 5, run 3
fMRI session
10 min  3 runs
Temporal binning
Predicted
pain report
Time
...
Unit of
averaging
1 min
2 min
Run
Session
Session
1 2 3
N
Training
data
Testing
data
Iteration 1
Iteration 2
Iteration 3
Iteration N
Classification
1 – Specificity
Sensitivity
Correlation
Actual 
pain report
Predicted
pain report
Fig. 1 | Study overview. a, Participants underwent longitudinal, multiple sessions 
of fMRI scans. Each session consisted of three 10-minute runs. b, Participants 
provided continuous self-reports of spontaneous pain intensity ratings in 
the scanner. Left: rating instruction and scale. Right: example trajectory of 
pain reports. c, Temporal changes in brain functional connectivity patterns 
were estimated as edge timeseries, representing the moment-by-moment 
cofluctuation of fMRI signals between each pair of brain regions. d, A machine 
learning model was trained to predict spontaneous pain reports based on 
corresponding brain connectivity patterns. The resulting model was tested on a 
separate dataset not used for training. e, Prediction results for each session were 
obtained from a model trained on all other sessions (that is, cross-validation), 
which was repeated for all sessions. The continuous timeseries of predicted pain 
reports was averaged into temporal bins of 1 min, 2 min, one run and one session. 
Prediction performance was then assessed using Pearson correlation between 
actual and predicted pain reports or classification accuracy between median-
dichotomized high versus low pain. VAS, visual analog scale; neg, negative; 
pos, positive; LASSO-PCR, least absolute shrinkage and selection operator-
regularized principal components regression.


## Page 3

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
parcellations to derive connectivity features, excluding parcels poten-
tially affected by task-related visual processing to minimize confounds 
(see Supplementary Fig. 3 for excluded parcels, Supplementary Fig. 4 
for decoding results without exclusion and Supplementary Fig. 5 for 
decoding results using only the excluded vision-related parcels). Using 
these connectivity patterns, we trained person-specific machine 
learning models to predict the participants’ pain ratings (Fig. 1d). 
We generated model predictions using cross-validation to separate 
training and test data and evaluated prediction performance across 
multiple timescales by varying the unit of temporal averaging (Fig. 1e; 
see Supplementary Fig. 6 for time-averaged pain ratings of all runs 
and sessions).
The personalized decoding models accurately tracked 
moment-by-moment changes in spontaneous pain ratings (Fig. 2a,b). 
For a timescale of 1 min, the Pearson correlation coefficient between 
actual and predicted pain ratings was 0.40 (95% CI, 0.23–0.55, P < 0.001) 
for Participant 1 and 0.51 (95% CI, 0.37–0.63, P < 0.001) for Participant 
2. Prediction performance improved monotonically with longer time-
scales for both Participant 1 (r = 0.47, 0.59, 0.61 for timescales of 2 min, 
run and session, respectively) and Participant 2 (r = 0.56, 0.63, 0.65 for 
the same timescales, respectively), which may reflect an increased 
signal-to-noise ratio due to greater temporal averaging28.
Although the personalized decoding models were not specifi-
cally trained for classification, the models could effectively discrim-
inate between median-dichotomized high- versus low-pain states 
using predicted pain ratings (Fig. 2c,d). For a timescale of 1 min, the 
area under the receiver operating characteristic curve (AUC) was 
0.71 (95% CI, 0.62–0.79, P < 0.001) for Participant 1 and 0.76 (95% CI, 
0.68–0.84, P < 0.001) for Participant 2. Classification performance 
also improved monotonically with longer timescales for both Par-
ticipant 1 (AUC = 0.76, 0.81, 0.87 for timescales of 2 min, run and ses-
sion, respectively) and Participant 2 (AUC = 0.80, 0.84, 0.93 for the 
same timescales).
In addition, the personalized pain decoding models showed 
significant prediction performance when evaluated using only the 
first run, which was not affected by the pain-exacerbating maneu-
ver (Supplementary Fig. 7). The models were also able to predict 
session-to-session variations in spontaneous pain ratings based on the 
resting-state fMRI data, which did not involve any rating procedure and 
was not used in model training (Supplementary Fig. 8). Furthermore, 
the models did not show significant performance when using only the 
vision-related parcels (Supplementary Fig. 9).
The personalized pain decoding models were sensitive not 
only to changes across multiple sessions but also to within-run and 
within-session variations (Supplementary Fig. 10). Furthermore, 
model predictions were not significantly associated with head 
motion (Supplementary Fig. 11). Decoding based on a population-level 
brain parcellation also yielded significant prediction performance 
(Supplementary Fig. 12). However, an a priori decoding model of sus-
tained pain—the Tonic Pain Signature8, which was developed to capture 
functional connectivity patterns generalizable at the group level—did 
not show significant prediction performance in either participant 
(Supplementary Fig. 13). Together, these findings support the validity 
of personalized fMRI models in capturing ongoing, spontaneous pain.
0
0.2
0.4
0.6
0.8
1.0
0
0.2
0.4
0.6
0.8
1.0
0
0.2
0.4
0.6
0.8
1.0
0
0.2
0.4
0.6
0.8
0
0.2
0.4
0.6
0.8
Predicted pain report
0
0.4
0.8
0
0.4
0.8
0.4
0.5
0.6
0.7
0.8
0.4
0.5
0.6
0.7
0.8
Actual pain report
Predicted pain report
AUC = 0.71, P = 0.0002
AUC = 0.76, P = 0.0004
AUC = 0.81, P = 0.001
AUC = 0.87, P = 0.002
AUC = 0.76, P = 0.0002
AUC = 0.80, P = 0.0002
AUC = 0.84, P = 0.0002
AUC = 0.93, P = 0.0002
0.4
0.6
0.8
0.4
0.6
0.8
0.4
0.6
0.8
0.4
0.6
0.8
0.5
0.6
0.7
0.5
0.6
0.7
1 – Specificity
Actual pain report
1 – Specificity
Sensitivity
a
c
r = 0.40, P = 0.0002 
r = 0.47 
P = 0.0008
r = 0.59
P = 0.0004
r = 0.61
P = 0.01
r = 0.51, P = 0.0002
r = 0.56
P = 0.0002
r = 0.63
P = 0.0002
r = 0.65
P = 0.0002
Unit of
averaging
1 min
2 min
Run
Session
Unit of
averaging
1 min
2 min
Run
Session
b
d
0
0.4
0.8
0
0.4
0.8
0
0.4
0.8
0
0.4
0.8
0
0.2
0.4
0.6
0.8
1.0
Sensitivity
Fig. 2 | Prediction performance. a,b, Actual versus predicted pain reports for 
Participant 1 (a) and Participant 2 (b). Colors represent the unit of averaging 
(that is, length of temporal bins). Pearson correlations between actual and 
predicted pain reports are shown in the plots (Participant 1: 95% CI 0.23–0.55, 
0.27–0.65, 0.29–0.82 and 0.17–0.89 for timescales of 1 min, 2 min, run and 
session, respectively; Participant 2: 95% CI 0.37–0.63, 0.40–0.70, 0.45–0.79 
and 0.46–0.82 for the same timescales). c,d, Receiver operating characteristic 
(ROC) curves for classifying median-dichotomized high- versus low-pain 
states for Participant 1 (c) and Participant 2 (d). Colors represent the unit of 
averaging. AUC values are shown in the plots (Participant 1: 95% CI 0.62–0.79, 
0.65–0.86, 0.63–0.94 and 0.69–1.00 for timescales of 1 min, 2 min, run and 
session, respectively; Participant 2: 95% CI 0.68–0.84, 0.71–0.88, 0.70–0.94 
and 0.82–1.00 for the same timescales). Statistical significance was determined 
using two-tailed bootstrap tests.


## Page 4

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
Effect of training data size on decoding performance
To evaluate how the amount of training data influences decoding accu-
racy, we systematically varied the number of fMRI sessions used to train 
the personalized models. For each training size, we randomly selected 
sessions from the full training set during each fold of cross-validation, 
repeating this procedure 100 times to ensure stability and robustness. 
We then calculated the Pearson correlation coefficients between actual 
and predicted pain ratings for each iteration and examined how these 
correlations changed with increasing training data.
Decoding performance improved as the training data size 
increased (Fig. 3). We found a significant linear relationship between 
the number of training sessions and the mean correlation coefficients 
across all 100 iterations of random subsampling for both Participant 1 
( ̂β= 57.48, 50.18, 37.53, 36.70 and t19 = 17.15, 17.46, 20.07, 27.47, for time-
scales of 1 min, 2 min, run and session, respectively; subscript denotes 
degrees of freedom; all P values < 0.001) and Participant 2 ( ̂β = 47.51, 
42.56, 37.22, 34.89 and t24 = 12.06, 12.19, 11.92, 11.79, for the same time-
scales; subscript denotes degrees of freedom; all P values < 0.001).
The minimum number of sessions required to achieve significant 
decoding performance in more than half of the 100 iterations was 8, 9, 
12 and 20 for timescales of 1 min, 2 min, run and session in Participant 1 
and 6, 6, 7 and 7 for the same timescales in Participant 2. These numbers 
exceed the typical number of fMRI sessions (for example, four or five) 
in previous longitudinal studies on chronic pain17,29, highlighting the 
importance of extensive sampling.
To further examine the role of data variability beyond quantity 
alone, we additionally trained models using the first 12 sessions, rather 
than randomly subsampling the same number of sessions from the 
full datasets (Supplementary Fig. 14). We chose 12 sessions because 
this matched the total number of sessions available for Participant 3, 
thereby allowing a direct comparison. Interestingly, these models did 
not show significant prediction performance for either Participant 
1 or Participant 2, despite using the same amount of training data. 
This finding suggests that model generalization depends not only on 
dataset size but also on the diversity and representativeness of the 
training data. Random subsampling from a larger dataset likely helps 
capture a broader range of variability in the data30, which appears to 
be critical for successful decoding and generalizability and may also 
explain the poor decoding performance observed in Participant 3 
(Supplementary Fig. 1).
Person-specific model weights and brain features
To investigate the individual specificity of our personalized 
brain-decoding models, we first identified key brain features that 
contributed to spontaneous pain prediction within each partici-
pant using a permutation-based feature importance analysis. This 
method assesses each brain region’s contribution by quantifying the 
drop in model performance when all connections to that region are 
randomly permuted.
The results showed that the personalized decoding models relied 
on individually distinct brain features for prediction (Fig. 4). For Par-
ticipant 1, brain regions with high feature importance included the left 
temporal pole and right posterior hippocampus, which are known to 
be involved in semantic and episodic memory31,32 and may play a role 
in learning and memory aspects of pain33,34. In contrast, the important 
brain regions for Participant 2 included the left premotor and primary 
somatomotor cortices, which have been primarily associated with the 
sensory-discriminative aspect of pain in previous literature35,36. To aid 
interpretation further, we mapped the important regions for each 
participant onto personalized canonical functional brain networks 
(Supplementary Fig. 15; for details on identifying personalized brain 
networks, see Supplementary Methods). These regions were distrib-
uted across multiple networks, which differed between participants, 
suggesting that spontaneous pain may be decoded by individually 
distinct brain systems that span multiple functional domains. We also 
present univariate general linear model analysis results using pain 
intensity as the independent variable in Supplementary Fig. 16.
To further evaluate individual specificity beyond visual inspec-
tion of feature maps, we performed cross-testing of the personal-
ized brain-decoding models (Fig. 5). Specifically, we used the model 
trained on Participant 2 to predict pain ratings for Participant 1 and vice 
versa. Each participant’s model failed to predict the other participant’s 
pain, resulting in non-significant prediction–outcome correlations 
(r = −0.05 to 0.04 and r = −0.27 to −0.07, across all the timescales) and 
classification performances (AUC = 0.49–0.56 and AUC = 0.48–0.52, 
across all the timescales), suggesting the models’ individual specificity. 
Cross-testing of models derived from a population-level brain parcel-
lation also yielded non-significant results (Supplementary Fig. 17), 
suggesting that this individual specificity was not simply due to the 
use of personalized brain parcellations.
Discussion
In this study, we developed personalized decoding models of sponta-
neous pain based on densely sampled fMRI data. These models pre-
dicted changes in pain ratings and discriminated between high- versus 
low-pain states across timescales ranging from minutes to days. Predic-
tion accuracy was associated with training data size, with conventional 
data quantities failing to achieve significant predictions. The models 
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
12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
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
12 13 14 15 16 17
18 19 20 21
0
0.1
0.2
0.3
0.4
0.5
Training data size (number of sessions)
a
b
Unit of averaging
1 min
2 min
Run
Session
Unit of averaging
1 min
2 min
Run
Session
Training data size (number of sessions)
Correlation
Correlation
Significant performance in more than 50% of iterations
Significant performance in more than 50% of iterations
Fig. 3 | Effect of training data size on decoding performance. a,b, Pearson 
correlations between actual and predicted pain reports from personalized 
decoding models trained on varying amounts of data for Participant 1 (a) and 
Participant 2 (b). Each dot represents the mean correlation coefficient across 
100 iterations of random subsampling. Error bars indicate the 95% CI. Colors 
represent the unit of averaging. The number of sessions that yielded significant 
decoding performance in more than half of the 100 iterations is marked as 
colored horizontal lines above the x axis of the plot.


## Page 5

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
relied on individiual-specific brain features and could not predict the 
pain ratings of other participants, highlighting their specificity at the 
individual level.
Despite the distributed nature of pain processing6,24,25, previous 
personalized decoding of spontaneous pain has been limited to record-
ing from a few selected brain regions22. This study employed fMRI to 
address this limitation by identifying whole-brain interaction pat-
terns associated with spontaneous pain. The significant decoding of 
spontaneous pain ratings across multiple timescales, which was not 
successful with local intracranial recordings22, highlights the impor-
tance of modeling global brain activity in chronic pain25. These findings 
further suggest the potential of neuroimaging to provide an objective 
assessment for disease progression and treatment response in chronic 
pain, leading to more informed clinical decision-making and guiding 
the development of targeted therapeutics5,11.
We demonstrated that extensive sampling of fMRI data is essen-
tial for accurate prediction. However, not all individuals with chronic 
pain can undergo multiple fMRI sessions due to mobility limitations, 
discomfort from prolonged scanning and the high cost of MRI. There-
fore, it is important to consider the feasibility and clinical utility of 
this approach for clinical translation. In addition, more time-efficient 
methods for acquiring high-quality data, such as multi-echo fMRI37, 
could help expand accessibility to a broader patient population.
The individual specificity of prediction models emphasizes the 
heterogeneity of chronic pain17 and the importance of a personalized 
approach14–16. For example, we observed that memory-related regions, 
including the hippocampus and temporal pole, were important for 
Participant 1, whereas sensorimotor-related regions, including 
premotor and primary somatomotor cortices, were important for 
Participant 2. One possibility is that the difference in pain duration 
(Participant 1: 7 years versus Participant 2: 10 months) may lead to 
distinct influences of pain-related memory38 and sensorimotor func-
tions39 on pain, which warrants further investigation.
It is important to note that the decoding models in our study con-
text may rely on neural signals that are non-specific to pain, because 
our study did not include a specificity condition during model training 
and testing. As a result, the models can draw on any reliable corollary 
information distributed across the brain, potentially including signals 
related to memory, salience, self-monitoring and the introspective 
evaluation of pain. In this sense, our decoding maps may be more 
individual-specific and more spatially distributed than pain-encoding 
maps or than decoding maps explicitly trained for pain specificity. 
Accordingly, the high degree of individual specificity observed in our 
decoding models may reflect not only heterogeneity in pain-related 
neural processing itself but also person-specific factors that shape 
the available decoding signals. These factors may include differences 
in pain chronicity, past experience and memory, as well as variability in 
task-related pain introspection, ongoing medication use and broader 
disease-related neural plasticity.
Despite this individual specificity, it remains possible that general-
izable brain representations exist within certain subtypes of patients40. 
Given the small number of participants in the present study, how-
ever, we were unable to identify potential subtypes or systematically 
examine the sources of this variability. Addressing these questions 
0
0.01
0.02
0
0.02 0.04
Importance
(–∆corr)
Importance
(–∆corr)
Importance
(–∆corr)
0
0.05
0
0.02
a
b
z = 18
z = 9
z = –1
L
R
x = –25
x = –2
x = 25
z = 18
z = 9
z = –1
L
R
x = –25
x = –2
x = 25
Temporal pole (L)
Hippocampus body (R)
Hippocampus tail (R)
Primary somatosensory
cortex (R)
Inferior temporal cortex (R)
Premotor cortex (L)
Primary somatosensory
and motor cortex (L)
Middle temporal cortex (R)
Inferior parietal lobule (L)
Dorsolateral prefrontal
cortex (R)
Importance
(–∆corr)
0.0472
0.0415
0.0390
0.0366
0.0360
0.0223
0.0124
0.0121
0.0108
0.0095
Region 1
1
Regions 2 and 3
2
3
4
5
1
2
3
4
5
Region 4
Region 5
Regions 1 and 2
Region 3
Region 4
Region 5
Fig. 4 | Feature importance maps. a,b, Permutation-based feature importance 
maps of personalized pain decoding models for Participant 1 (a) and 
Participant 2 (b). Mean decrease of prediction–outcome correlation (−Δcorr) 
after permutation was used as a measure of feature importance. To optimize 
visualization, brain regions with negative feature importance were set to zero. 
The top five brain regions with the highest feature importance are highlighted.


## Page 6

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
represents a promising direction for future research and will require 
larger samples and experimental designs to enable causal testing.
Overall, our study presents a new opportunity to identify personal-
ized biomarkers for spontaneous pain with clinical validity for single 
patients, which could potentially advance the diagnosis and treatment 
of chronic pain.
Online content
Any methods, additional references, Nature Portfolio reporting sum-
maries, source data, extended data, supplementary information, 
acknowledgements, peer review information; details of author contri-
butions and competing interests; and statements of data and code avail-
ability are available at https://doi.org/10.1038/s41593-026-02221-3.
References
1.	
Dahlhamer, J. et al. Prevalence of chronic pain and high-impact 
chronic pain among adults - United States, 2016. MMWR Morb. 
Mortal. Wkly Rep. 67, 1001–1006 (2018).
2.	
Foss, J. M., Apkarian, A. V. & Chialvo, D. R. Dynamics of pain: fractal 
dimension of temporal variability of spontaneous pain differentiates 
between pain States. J. Neurophysiol. 95, 730–736 (2006).
3.	
Mun, C. J. et al. Investigating intraindividual pain variability: 
methods, applications, issues, and directions. Pain 160,  
2415–2429 (2019).
4.	
Smith, S. M. et al. Pain intensity rating training: results from an 
exploratory study of the ACTTION PROTECCT system. Pain 157, 
1056–1064 (2016).
5.	
Davis, K. D. et al. Discovery and validation of biomarkers to aid the 
development of safe and effective pain therapeutics: challenges 
and opportunities. Nat. Rev. Neurol. 16, 381–400 (2020).
6.	
Wager, T. D. et al. An fMRI-based neurologic signature of physical 
pain. N. Engl. J. Med. 368, 1388–1397 (2013).
7.	
Woo, C. W. et al. Quantifying cerebral contributions to pain 
beyond nociception. Nat. Commun. 8, 14211 (2017).
8.	
Lee, J. J. et al. A neuroimaging biomarker for sustained 
experimental and clinical pain. Nat. Med. 27, 174–182 (2021).
9.	
Baliki, M. N. et al. Chronic pain and the emotional brain: specific 
brain activity associated with spontaneous fluctuations of 
intensity of chronic back pain. J. Neurosci. 26, 12165–12173  
(2006).
10.	 Jaillard, A. & Ropper, A. H. Pain, heat, and emotion with functional 
MRI. N. Engl. J. Med. 368, 1447–1449 (2013).
0.4
0.5
0.6
0.7
0.8
0.4
0.5
0.6
0.7
0.8
Predicted pain report
a
r = –0.05, P = 0.35
0.4
0.6
0.8
0.4
0.6
0.8
r = –0.04
P = 0.58
0.4
0.6
0.8
0.4
0.6
0.8
r = 0.04
P = 0.74
0.4
0.6
0.8
0.4
0.6
0.8
r = 0.002
P = 0.96
0
0.2
0.4
0.6
0.8
1.0
0
0.2
0.4
0.6
0.8
1.0
AUC = 0.49, P = 0.75
AUC = 0.50, P = 0.98
AUC = 0.56, P = 0.60
AUC = 0.54, P = 0.82
AUC = 0.48, P = 0.77
AUC = 0.49, P = 0.92
AUC = 0.48, P = 0.83
AUC = 0.52, P = 0.87
1 – Specificity
Sensitivity
c
0
0.2
0.4
0.6
0.8
0
0.2
0.4
0.6
0.8
Predicted pain report
b
r = –0.07, P = 0.50
0
0.4
0.8
0
0.4
0.8
r = –0.08
P = 0.50
0
0.4
0.8
0
0.4
0.8
r = –0.14
P = 0.43
0
0.4
0.8
0
0.4
0.8
r = –0.27
P = 0.19
0
0.2
0.4
0.6
0.8
1.0
0
0.2
0.4
0.6
0.8
1.0
1 – Specificity
Sensitivity
d
Unit of
averaging
1 min
2 min
Run
Session
Unit of
averaging
1 min
2 min
Run
Session
Actual pain report
Actual pain report
Fig. 5 | Cross-testing of personalized decoding models. We predicted the  
pain reports of Participant 1 using the decoding model of Participant 2 and the 
pain reports of Participant 2 using the decoding model of Participant 1.  
a,b, Actual versus predicted pain reports for Participant 1 (a) and Participant 2 
(b). Colors represent the unit of averaging. Pearson correlations between actual 
and predicted pain report are shown in the plots (Participant 1: 95% CI −0.16 to 
0.06, −0.20 to 0.11, −0.24 to 0.31 and −0.36 to 0.39 for timescales of 1 min, 2 min, 
run and session, respectively; Participant 2: 95% CI −0.24 to 0.12, −0.29 to  
0.14, −0.42 to 0.21 and −0.59 to 0.14 for the same timescales). c,d, ROC curves for 
classifying median-dichotomized high- versus low-pain states for Participant 
1 (c) and Participant 2 (d). Colors represent the unit of averaging. AUC values 
are shown in the plots (Participant 1: 95% CI 0.42–0.56, 0.40–0.60, 0.35–0.75 
and 0.29–0.80 for timescales of 1 min, 2 min, run and session, respectively; 
Participant 2: 95% CI 0.38–0.58, 0.36–0.62, 0.30–0.66 and 0.29–0.75 for the  
same timescales). Statistical significance was determined using two-tailed 
bootstrap tests.


## Page 7

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
11.	
FDA-NIH Biomarker Working Group. BEST (Biomarkers, EndpointS, 
and other Tools) Resource (FDA, 2016).
12.	 Cheng, J. C. et al. Multivariate machine learning distinguishes 
cross-network dynamic functional connectivity patterns in state 
and trait neuropathic pain. Pain 159, 1764–1776 (2018).
13.	 Lee, J. et al. Machine learning-based prediction of clinical pain 
using multimodal neuroimaging and autonomic metrics. Pain 
160, 550–560 (2019).
14.	 Gordon, E. M. et al. Precision functional mapping of individual 
human brains. Neuron 95, 791–807 e797 (2017).
15.	 Porter, A. et al. Masked features of task states found in individual 
brain networks. Cereb. Cortex 33, 2879–2900 (2023).
16.	 Kraus, B. et al. Insights from personalized models of brain and 
behavior for identifying biomarkers in psychiatry. Neurosci. 
Biobehav Rev. 152, 105259 (2023).
17.	 Mayr, A. et al. Patients with chronic pain exhibit individually 
unique cortical signatures of pain encoding. Hum. Brain Mapp. 
43, 1676–1693 (2022).
18.	 Reddan, M. C. Recommendations for the development of 
socioeconomically-situated and clinically-relevant neuroimaging 
models of pain. Front. Neurol. 12, 700833 (2021).
19.	 Vansteensel, M. J. et al. Fully implanted brain-computer interface 
in a locked-in patient with ALS. N. Engl. J. Med. 375, 2060–2066 
(2016).
20.	 Moses, D. A. et al. Neuroprosthesis for decoding speech in a 
paralyzed person with anarthria. N. Engl. J. Med. 385, 217–227 (2021).
21.	 Alagapan, S. et al. Cingulate dynamics track depression recovery 
with deep brain stimulation. Nature 622, 130–138 (2023).
22.	 Shirvalkar, P. et al. First-in-human prediction of chronic pain state 
using intracranial neural biomarkers. Nat. Neurosci. 26,  
1090–1099 (2023).
23.	 Altman, D. G. & Royston, P. The cost of dichotomising continuous 
variables. Br. Med. J. 332, 1080 (2006).
24.	 Coghill, R. C. The distributed nociceptive system: a framework for 
understanding pain. Trends Neurosci. 43, 780–794 (2020).
25.	 Farmer, M. A., Baliki, M. N. & Apkarian, A. V. A dynamic network 
perspective of chronic pain. Neurosci. Lett. 520, 197–203 (2012).
26.	 Clauw, D. J. Fibromyalgia: a clinical review. JAMA 311, 1547–1555 
(2014).
27.	 Zamani Esfahlani, F. et al. High-amplitude cofluctuations in 
cortical activity drive functional connectivity. Proc. Natl Acad. Sci. 
USA 117, 28393–28401 (2020).
28.	 Lee, D. H., Lee, S. & Woo, C. W. Decoding pain: uncovering the 
factors that affect the performance of neuroimaging-based pain 
models. Pain 166, 360–375 (2025).
29.	 Hashmi, J. A. et al. Shape shifting pain: chronification of back pain 
shifts brain representation from nociceptive to emotional circuits. 
Brain 136, 2751–2768 (2013).
30.	 Ooi, L. Q. R. et al. Longer scans boost prediction and cut  
costs in brain-wide association studies. Nature 644, 731–740 
(2025).
31.	 Patterson, K., Nestor, P. J. & Rogers, T. T. Where do you know what 
you know? The representation of semantic knowledge in the 
human brain. Nat. Rev. Neurosci. 8, 976–987 (2007).
32.	 Setton, R., Mwilambwe-Tshilobo, L., Sheldon, S., Turner, G. R. &  
Spreng, R. N. Hippocampus and temporal pole functional 
connectivity is associated with age and individual differences 
in autobiographical memory. Proc. Natl Acad. Sci. USA 119, 
e2203039119 (2022).
33.	 Moulton, E. A. et al. Painful heat reveals hyperexcitability of the 
temporal pole in interictal and ictal migraine States. Cereb. 
Cortex 21, 435–448 (2011).
34.	 Branco, P. et al. Hippocampal functional connectivity after 
whiplash injury is linked to the development of chronic pain. Nat. 
Ment. Health 2, 1362–1370 (2024).
35.	 Coghill, R. C., Sang, C. N., Maisog, J. M. & Iadarola, M. J. Pain 
intensity processing within the human brain: a bilateral, 
distributed mechanism. J. Neurophysiol. 82, 1934–1943  
(1999).
36.	 Frot, M., Magnin, M., Mauguiere, F. & Garcia-Larrea, L. Cortical 
representation of pain in primary sensory-motor areas (S1/M1)—a 
study using intracortical recordings in humans. Hum. Brain Mapp. 
34, 2655–2668 (2013).
37.	 Lynch, C. J. et al. Rapid precision functional mapping of 
individuals using multi-echo fMRI. Cell Rep. 33, 108540  
(2020).
38.	 Apkarian, A. V. Pain perception in relation to emotional learning. 
Curr. Opin. Neurobiol. 18, 464–468 (2008).
39.	 Kim, J. et al. Somatotopically specific primary somatosensory 
connectivity to salience and default mode networks encodes 
clinical pain. Pain 160, 1594–1605 (2019).
40.	 Drysdale, A. T. et al. Resting-state connectivity biomarkers define 
neurophysiological subtypes of depression. Nat. Med. 23, 28–38 
(2017).
Publisher’s note Springer Nature remains neutral with regard to 
jurisdictional claims in published maps and institutional affiliations.
Springer Nature or its licensor (e.g. a society or other partner) holds 
exclusive rights to this article under a publishing agreement with 
the author(s) or other rightsholder(s); author self-archiving of the 
accepted manuscript version of this article is solely governed by the 
terms of such publishing agreement and applicable law.
© The Author(s), under exclusive licence to Springer Nature America, 
Inc. 2026


## Page 8

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
Methods
Participants
We studied patients with fibromyalgia, a common type of chronic 
pain disorder primarily characterized by chronic widespread pain. 
Participants were eligible for enrollment if they had a confirmed diag-
nosis of fibromyalgia and had been experiencing pain for more than 
six months, with an average intensity greater than 4/10 on the visual 
analog scale. We excluded participants with chronic secondary pain (for 
example, autoimmune disease, tumor, fracture or infection), a history 
of substance use disorder, MRI contraindications, left-handedness or 
previous experience with psychological interventions. Three partici-
pants who met the inclusion and exclusion criteria were recruited from 
the general public of South Korea through online advertisement and 
telephone interviews.
Participant 1 was a 44-year-old woman who had experienced pain 
since childhood. Her first episode of pain occurred without preced-
ing physical injuries, and she was diagnosed with fibromyalgia seven 
years before enrollment. Participant 2 was a 37-year-old woman who 
developed pain after a traffic accident one year and four months before 
enrollment, although physical and radiological examinations at the 
time of the accident showed no signs of physical injury. She had a 
confirmed diagnosis of fibromyalgia ten months before enrollment. 
Participant 3 was a 37-year-old woman who reported that her pain began 
a week after giving birth and was diagnosed with fibromyalgia seven 
years before enrollment.
The overall pain intensity scores at the time of enrollment were 
5 out of 10, 7 out of 10 and 7 out of 10 on the visual analog scale for 
Participants 1, 2 and 3, respectively. All participants were taking medi-
cations to manage their symptoms (Participant 1: pregabalin, tram-
adol, milnacipran, celecoxib; Participant 2: pregabalin, celecoxib, 
trazodone, sertraline, alprazolam; Participant 3: antidepressants and 
anxiolytics (declined to specify the exact medications)). All partici-
pants provided written informed consent. The institutional review 
board of Sungkyunkwan University approved the study (approval 
number 2021-08-013).
Study design
We conducted longitudinal, multisession fMRI scans (for details on 
data acquisition and preprocessing, see Supplementary Methods). 
The total number of planned fMRI sessions was 30, with a minimum 
requirement of 15 sessions for inclusion in the study. Participants 
were encouraged to complete as many sessions as possible. Two of 
the three enrolled participants completed more than 15 fMRI sessions 
(Participant 1: 23 sessions; Participant 2: 28 sessions; Participant 3: 12 
sessions); therefore, we present analysis results from Participants 1 
and 2 here (Fig. 1a; see Supplementary Fig. 1 for Participant 3’s results).
Each fMRI session consisted of a resting condition and three dis-
tinct experimental tasks (for details, see Supplementary Methods). In 
this study, we used the spontaneous pain rating task data to train and 
test personalized pain decoding models. The spontaneous pain rating 
task consisted of three 10-minute runs. During this task, participants 
continuously reported their moment-by-moment spontaneous pain 
intensity using a trackball mouse (Fig. 1b). To induce fluctuations in 
spontaneous pain in a naturalistic and tolerable manner, participants 
performed an individualized physical maneuver while lying on the 
bed before the second run (for details, see Supplementary Methods). 
Participants were instructed to continue their medications to ensure 
safe participation in the experiment.
Training and evaluation of personalized pain decoding models
We developed personalized decoding models for spontaneous 
pain as follows. First, we removed the initial 66 volumes (30 s) of 
fMRI images, which could be affected by initial rating motion, and 
shifted the timing of these images by 13 volumes (6 s) to account for 
the hemodynamic delay. Then, we averaged the voxel-wise fMRI data 
within the individual-specific brain parcels (for details on deriving 
individual-specific parcellation, see Supplementary Methods). We 
excluded parcels in the occipital areas and those assigned to the visual 
network from further analyses to mitigate potential confounds from 
visual processing of the rating bar (Supplementary Fig. 3).
We then estimated the moment-by-moment whole-brain cofluc-
tuations by computing the framewise product of z-standardized fMRI 
signals between each pair of brain parcels. This method, termed ‘edge 
timeseries’27, provides a measure of instantaneous inter-regional con-
nectivity (Fig. 1c). The edge timeseries and the corresponding sponta-
neous pain ratings were binned into deciles by sorting the pain ratings 
within each run into ten levels of pain intensity. We then averaged the 
edge timeseries and pain ratings within each bin to use them as the 
dependent and independent variables in model training. We trained 
decoding models that predicted the binned average pain ratings based 
on the binned average edge timeseries data using the least absolute 
shrinkage and selection operator-regularized principal components 
regression algorithm (Fig. 1d; Supplementary Methods).
We tested the models on edge timeseries data that were not used 
for model training (Fig. 1e). The separation of training and test data was 
based on leave-one-session-out cross-validation, which could provide 
less biased estimates of prediction performance while maximizing the 
training sample size. The predicted continuous pain ratings were then 
averaged into temporal bins. We used time-based binning instead of 
intensity-based binning, as it does not require rating information for 
binning, making it better suited for unbiased tests. The averaging units 
were 10 bins per run (1 min), 5 bins per run (2 mins), a run (10 mins) and 
a session (30 mins), each representing decoding results at different 
timescales. We assessed the prediction performance by calculating the 
Pearson correlation between actual and predicted pain reports. For the 
other metrics, including coefficients of determination (R2) and mean 
absolute error, please see Supplementary Table 1. We also evaluated 
classification performance for median-dichotomized high- versus 
low-pain states by computing the AUC.
Training size dependence
To examine the impact of the training data size on prediction per-
formance, we trained the decoding models while varying the num-
ber of training sessions. For each iteration of leave-one-session-out 
cross-validation, we randomly selected a given number of sessions from 
the training set instead of using all available sessions. We repeated this 
random subsampling procedure 100 times per cross-validation itera-
tion and for each training set size. We kept the regularization parameter 
for each iteration the same as in the original model. We then calculated 
correlation coefficients between actual and predicted pain reports for 
each iteration of random subsampling. We assessed the linear relation-
ship between the number of training sessions and mean correlation 
coefficients across all 100 iterations using linear regression. We also 
determined the minimum number of training sessions that yielded a 
statistically significant correlation coefficient (P < 0.05) in more than 
half of the 100 iterations.
Feature importance
To identify the key brain features for decoding spontaneous pain 
within individuals, we measured permutation-based feature impor-
tance from the personalized decoding models. In this approach, we 
randomly permuted a set of brain features from the final model and 
measured the resulting changes in prediction performance. A large 
decline in performance indicates that the permuted features have an 
important contribution to the prediction. We assessed the permuta-
tion feature importance of each brain region by removing all its con-
nections (that is, edge timeseries) to the region from the decoding 
model and calculating the decrease in prediction performance at 
the 10-bins-per-run version (that is, one minute-level) test data using 
leave-one-session-out cross-validation. We repeated the permutation 


## Page 9

Nature Neuroscience
Article
https://doi.org/10.1038/s41593-026-02221-3
procedure 10,000 times and used the average performance decrease 
as the feature importance score.
Statistical analysis
We set 15 sessions as the minimum requirement for the main analysis. 
This minimum number of sessions ensures 80% power to detect a cor-
relation of r = 0.66, which represents the median of the individual-level 
correlation coefficients between prefrontal gamma oscillations and 
spontaneous pain intensity41. The 15 sessions provide 7.5 h of fMRI data, 
which corresponded to the minimum training data required to reach a 
performance plateau for personalized decoding models, as reported 
in a previous study42.
We computed 95% confidence intervals (CIs) and statistical signifi-
cance of correlation coefficients and AUCs using bootstrap tests with 
10,000 iterations. To account for dependence in longitudinal data, we 
obtained bootstrap samples sequentially at each level of the data hierar-
chy (for example, session, run and time-bin)43. For run-level prediction, 
we obtained bootstrap samples first from sessions and then from runs 
within the selected sessions. For time-bin-level prediction, we also 
obtained bootstrap samples sequentially from sessions, from runs for 
the selected sessions and then from time-bins within the selected runs.
Reporting summary
Further information on research design is available in the Nature 
Portfolio Reporting Summary linked to this article.
Data availability
Raw MRI data are publicly available at https://openneuro.org/datasets/
ds006815. All the data to generate the figures are available via figshare 
at https://doi.org/10.6084/m9.figshare.31064431 (ref. 44). Source data 
are provided with this paper.
Code availability
Code for the main analyses is available via GitHub at https://github.
com/cocoanlab/DEIPP (ref. 45).
References
41.	 May, E. S. et al. Prefrontal gamma oscillations reflect ongoing 
pain intensity in chronic back pain patients. Hum. Brain Mapp. 40, 
293–305 (2019).
42.	 Tang, J., LeBel, A., Jain, S. & Huth, A. G. Semantic reconstruction 
of continuous language from non-invasive brain recordings. Nat. 
Neurosci. 26, 858–866 (2023).
43.	 Saravanan, V., Berman, G. J. & Sober, S. J. Application  
of the hierarchical bootstrap to multi-level data in  
neuroscience. Neuron. Behav. Data Anal. Theory 3, 1–25  
(2020).
44.	 Lee, J.-J. & Woo, C. W. DEIPP. figshare https://doi.org/10.6084/
m9.figshare.31064431 (2026).
45.	 Lee, J.-J. et al. Repository for “Personalized Brain Decoding of 
Spontaneous Pain in Individuals With Chronic Pain”. GitHub 
https://github.com/cocoanlab/DEIPP (2025).
Acknowledgements
We thank all patients for their participation in this study. We thank 
J. Lee and S.-G. Kim for help with participant recruitment. We thank 
E.-J. Jeong, J. Han and Y. Park for help with conducting experiments. 
This work was supported by Institute for Basic Science (grant no. 
IBS-R015-D2 to C.-W.W.).
Author contributions
J.-J.L. and C.-W.W. conceived and designed the experiment. S.J. and 
S.C. contributed to the experimental design, participant management 
and psychotherapy. J.-J.L. conducted the data analysis. J.-J.L. and 
C.-W.W. interpreted the results. J.-J.L. wrote the manuscript. C.-W.W. 
provided supervision and edited the manuscript. All authors reviewed 
and approved the final manuscript, except for S.J., who passed away in 
November 2023.
Competing interests
The authors declare no competing interests.
Additional information
Supplementary information The online version  
contains supplementary material available at  
https://doi.org/10.1038/s41593-026-02221-3.
Correspondence and requests for materials should be addressed to 
Choong-Wan Woo.
Peer review information Nature Neuroscience thanks Benjamin 
Becker, Markus Ploner and the other, anonymous, reviewer(s) for their 
contribution to the peer review of this work.
Reprints and permissions information is available at  
www.nature.com/reprints.


## Page 10

1
nature portfolio  |  reporting summary
April 2023
Corresponding author(s):
Choong-Wan Woo
Last updated by author(s): Jan 13, 2026
Reporting Summary
Nature Portfolio wishes to improve the reproducibility of the work that we publish. This form provides structure for consistency and transparency 
in reporting. For further information on Nature Portfolio policies, see our Editorial Policies and the Editorial Policy Checklist.
Statistics
For all statistical analyses, confirm that the following items are present in the figure legend, table legend, main text, or Methods section.
n/a Confirmed
The exact sample size (n) for each experimental group/condition, given as a discrete number and unit of measurement
A statement on whether measurements were taken from distinct samples or whether the same sample was measured repeatedly
The statistical test(s) used AND whether they are one- or two-sided 
Only common tests should be described solely by name; describe more complex techniques in the Methods section.
A description of all covariates tested
A description of any assumptions or corrections, such as tests of normality and adjustment for multiple comparisons
A full description of the statistical parameters including central tendency (e.g. means) or other basic estimates (e.g. regression coefficient) 
AND variation (e.g. standard deviation) or associated estimates of uncertainty (e.g. confidence intervals)
For null hypothesis testing, the test statistic (e.g. F, t, r) with confidence intervals, effect sizes, degrees of freedom and P value noted 
Give P values as exact values whenever suitable.
For Bayesian analysis, information on the choice of priors and Markov chain Monte Carlo settings
For hierarchical and complex designs, identification of the appropriate level for tests and full reporting of outcomes
Estimates of effect sizes (e.g. Cohen's d, Pearson's r), indicating how they were calculated
Our web collection on statistics for biologists contains articles on many of the points above.
Software and code
Policy information about availability of computer code
Data collection
We collected data using Psychtoolbox (version 3.0, http://psychtoolbox.org/) running on Matlab (version 2017a, Mathworks).
Data analysis
Code for preprocessing and main analyses is available on Github (https://github.com/cocoanlab/DEIPP).
For manuscripts utilizing custom algorithms or software that are central to the research but not yet described in published literature, software must be made available to editors and 
reviewers. We strongly encourage code deposition in a community repository (e.g. GitHub). See the Nature Portfolio guidelines for submitting code & software for further information.
Data
Policy information about availability of data
All manuscripts must include a data availability statement. This statement should provide the following information, where applicable: 
- Accession codes, unique identifiers, or web links for publicly available datasets 
- A description of any restrictions on data availability 
- For clinical datasets or third party data, please ensure that the statement adheres to our policy 
 
Raw MRI data are publicly available at https://openneuro.org/datasets/ds006815. All the data to generate the figures are available at https://doi.org/10.6084/
m9.figshare.31064431.


## Page 11

2
nature portfolio  |  reporting summary
April 2023
Research involving human participants, their data, or biological material
Policy information about studies with human participants or human data. See also policy information about sex, gender (identity/presentation), 
and sexual orientation and race, ethnicity and racism.
Reporting on sex and gender
This study included three female participants. The sex and gender of participants were collected by self-report. We did not 
perform sex- or gender-based analysis.
Reporting on race, ethnicity, or 
other socially relevant 
groupings
N/A
Population characteristics
The participants were aged 44, 37, and 37 years and had been diagnosed with fibromyalgia.
Recruitment
The participants were recruited from the general public of South Korea through online advertisement and telephone 
interviews. While this recruitment approach may introduce self-selection bias toward motivated individuals who can tolerate 
and complete repeated MRI sessions, the main analyses focus on within-participant prediction evaluated on held-out 
sessions.
Ethics oversight
The institutional review board of the Sunkyunkwan University approved the study (approval number 2021-08-013). All 
participants provided written informed consent for the participation.
Note that full information on the approval of the study protocol must also be provided in the manuscript.
Field-specific reporting
Please select the one below that is the best fit for your research. If you are not sure, read the appropriate sections before making your selection.
Life sciences
Behavioural & social sciences
 Ecological, evolutionary & environmental sciences
For a reference copy of the document with all sections, see nature.com/documents/nr-reporting-summary-flat.pdf
Life sciences study design
All studies must disclose on these points even when the disclosure is negative.
Sample size
This study employed an intensive longitudinal design, with a minimum requirement of 15 sessions per participant for inclusion in the main 
analysis. This threshold was set to ensure 80% statistical power to detect a correlation of r = 0.66, which represents the median of the 
individual-level correlation coefficients between prefrontal gamma oscillations and spontaneous pain intensity (May et al., 2019). The 15 
sessions provide 7.5 hours of fMRI data, which corresponded to the minimum training data required to reach a performance plateau for 
personalized decoding models, as reported in a previous study (Tang et al., 2023). Three participants completed 23, 28, and 13 sessions, 
respectively. Therefore, the two participants who completed more than the requisite 15 sessions are the focus of this study.
Data exclusions
The participant who completed fewer than 15 sessions (Participant 3) was excluded from the primary analyses.
Replication
We used leave-one-session-out cross-validation to evaluate the decoding performance of the personalized models on each participant’s 
unseen data. To assess the individual specificity of the models, we also tested each model on data from a different participant. No additional 
independent cohorts were collected.
Randomization
No randomization was needed for this study because there was no experimental group allocation.
Blinding
No blinding was needed for this study because there was no experimental group allocation.
Reporting for specific materials, systems and methods
We require information from authors about some types of materials, experimental systems and methods used in many studies. Here, indicate whether each material, 
system or method listed is relevant to your study. If you are not sure if a list item applies to your research, read the appropriate section before selecting a response. 


## Page 12

3
nature portfolio  |  reporting summary
April 2023
Materials & experimental systems
n/a Involved in the study
Antibodies
Eukaryotic cell lines
Palaeontology and archaeology
Animals and other organisms
Clinical data
Dual use research of concern
Plants
Methods
n/a Involved in the study
ChIP-seq
Flow cytometry
MRI-based neuroimaging
Novel plant genotypes
Describe the methods by which all novel plant genotypes were produced. This includes those generated by transgenic approaches, 
gene editing, chemical/radiation-based mutagenesis and hybridization. For transgenic lines, describe the transformation method, the 
number of independent lines analyzed and the generation upon which experiments were performed. For gene-edited lines, describe 
the editor used, the endogenous sequence targeted for editing, the targeting guide RNA sequence (if applicable) and how the editor 
was applied.
Seed stocks
Report on the source of all seed stocks or other plant material used. If applicable, state the seed stock centre and catalogue number. If 
plant specimens were collected from the field, describe the collection location, date and sampling procedures.
Authentication
Describe any authentication procedures for each seed stock used or novel genotype generated. Describe any experiments used to 
assess the effect of a mutation and, where applicable, how potential secondary effects (e.g. second site T-DNA insertions, mosiacism, 
off-target gene editing) were examined.
Plants
Magnetic resonance imaging
Experimental design
Design type
Resting state, block design task
Design specifications
Each fMRI session consisted of a resting condition and three distinct experimental tasks (spontaneous pain rating, 
speaking, listening). This study used the (1) resting state data for deriving individual-specific brain parcels and networks 
and generalizability testing, and (2) spontaneous pain rating task data for training and testing personalized pain 
decoding models. 
(1) Resting state: One run, each for 10 minutes 
(2) Spontaneous pain rating task: Three runs, each for 10 minutes
Behavioral performance measures
For (2) spontaneous pain rating task, participants continuously reported their moment-by-moment spontaneous pain 
intensity using a trackball mouse.
Acquisition
Imaging type(s)
Functional, structural
Field strength
3 Tesla
Sequence & imaging parameters
Imaging was performed using a 3T Siemens Prisma scanner at Sungkyunkwan University. For each session, whole-brain 
fMRI images were acquired using a gradient-echo EPI sequence with TR = 460 ms, TE = 26 ms, flip angle = 90 degrees, 
multiband acceleration factor = 8, field of view = 216 mm, 80 × 80 × 56 matrix, 2.7 × 2.7 × 2.7 mm voxels. We also 
acquired the two spin-echo EPI scans, one with the same phase encoding direction as the fMRI images and the other 
with the reversed phase encoding direction. For the session 1, 11, and 21, T1-weighted structural images were acquired 
with TR = 2400 ms, TE = 2.34 ms, TI = 1150 ms, flip angle = 8 degrees, 224 × 320 × 320 matrix, 0.7 × 0.7 × 0.7 mm voxels. 
For the session 2, 12, and 22, T2-weighted structural images were acquired with TR = 3100 ms, TE = 566 ms, 224 × 320 × 
320 matrix, 0.7 × 0.7 × 0.7 mm voxels.
Area of acquisition
Whole brain
Diffusion MRI
Used
Not used
Preprocessing
Preprocessing software
FSL 6.0 
Freesurfer 7.2 
AFNI 23.0 
ciftify (https://github.com/edickie/ciftify/) 
Code for preprocessing: https://github.com/cocoanlab/DEIPP


## Page 13

4
nature portfolio  |  reporting summary
April 2023
Normalization
Combining linear transformation (BOLD -> T1) and non-linear transformation (T1 -> MNI)
Normalization template
MNI152
Noise and artifact removal
We conducted motion censoring, denoising, and temporal filtering using AFNI (‘3dTproject’). First, the motion-contaminated 
volumes with framewise displacement (FD) > 0.2 mm were removed and replaced through linear interpolation over time. To 
prevent overly aggressive motion censoring due to respiratory artifacts, head motion parameters were low pass-filtered (< 
0.1 Hz) prior to FD calculation. Subsequently, denoising and temporal filtering were carried out in a single nuisance 
regression step. Regressors for denoising include a linear trend, 6 head motion parameters derived from motion correction, 5 
principal components of white matter (WM) signals and 5 principal components of cerebrospinal fluid (CSF) signals. For 
temporal filtering, we applied band-pass filter (0.005 Hz – 0.1 Hz) for the resting condition and high-pass filter (> 0.005 Hz) 
for the other conditions.
Volume censoring
The motion-contaminated volumes as defined above (FD > 0.2 mm) were excluded from further analyses.
Statistical modeling & inference
Model type and settings
We used the principal component regression with LASSO regularization to predict tonic pain ratings based on whole-brain 
edge timeseries features.
Effect(s) tested
We calculated Pearson's correlation between actual and predicted pain reports within individuals as a primary indicator of 
prediction performance. We also evaluated classification performance for median-dichotomized high vs. low pain states by 
computing the area under the receiver-operating-characteristic curve (AUC).
Specify type of analysis:
Whole brain
ROI-based
Both
Statistic type for inference
(See Eklund et al. 2016)
This study used edge timeseries methods for inference.
Correction
We used false discovery rate (FDR) correction method. 
Models & analysis
n/a Involved in the study
Functional and/or effective connectivity
Graph analysis
Multivariate modeling or predictive analysis
Functional and/or effective connectivity
We computed the framewise product of z-standardized fMRI signals between each pair of brain parcels (i.e., 
edge timeseries) to derive a measure of instantaneous inter-regional functional connectivity.
Multivariate modeling and predictive analysis
We used the principal component regression (PCR) with LASSO regularization to predict pain ratings across 
time based on whole-brain edge timeseries features. First, we reduced the dimensionality of the edge 
timeseries features using the principal component analysis (PCA). Then, the principal component scores 
were used as the predictor variables of LASSO regression to predict pain ratings. The selection of LASSO 
regularization parameter (λ) and model evaluation was performed using nested cross-validation.


