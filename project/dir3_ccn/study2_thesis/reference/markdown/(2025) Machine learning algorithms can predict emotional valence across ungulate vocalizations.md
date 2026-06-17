# (2025) Machine learning algorithms can predict emotional valence across ungulate vocalizations

**Source:** (2025) Machine learning algorithms can predict emotional valence across ungulate vocalizations.pdf

---

## Page 1

Article
iScience
Machine learning algorithms can predict emotional
valence across ungulate vocalizations
Graphical abstract
Highlights
d Machine learning achieves 89.49% accuracy in classifying
emotions across ungulate calls
d Key features include call duration, pitch, amplitude
modulation, and energy quartiles
d Species differences highlight the need for broader datasets
across diverse taxa
d Findings suggest universal tools for welfare monitoring,
needing further validation
Authors
Romain A. Lefe` vre, Ciara C. R. Sypherd,
E´ lodie F. Briefer
Correspondence
romain.adrien.lefevre@protonmail.com
(R.A.L.),
elodie.briefer@bio.ku.dk (E´ .F.B.)
In brief
Algorithms; Artiﬁcial intelligence;
Bioacoustics; Wildlife behavior; Zoology;
Lefe` vre et al., 2025, iScience 28, 111834
February 21, 2025 ª 2025 The Authors. Published by Elsevier Inc.
https://doi.org/10.1016/j.isci.2025.111834
ll


## Page 2

iScience
Article
Machine learning algorithms can predict emotional
valence across ungulate vocalizations
Romain A. Lefe` vre,1,3,* Ciara C. R. Sypherd,1,2,3 and E´ lodie F. Briefer1,3,4,*
1Behavioural Ecology Group, Section for Ecology & Evolution, Department of Biology, University of Copenhagen, 2100 Copenhagen Ø,
Denmark
2School of Engineering and Applied Sciences, Harvard University, Cambridge, MA, USA
3Bluesky: @behaveco.bsky.social
4Lead contact
*Correspondence: romain.adrien.lefevre@protonmail.com (R.A.L.), elodie.briefer@bio.ku.dk (E´ .F.B.)
https://doi.org/10.1016/j.isci.2025.111834
SUMMARY
Vocalizations can vary as a function of their context of production and provide an immediate measure of an
animal’s affective states. If vocal expression of emotions has been conserved throughout evolution, direct
between-species comparisons using the same set of acoustic indicators should be possible. The present
study used a machine learning algorithm (eXtreme Gradient Boosting [XGBoost]) to distinguish between con-
tact calls indicating positive (pleasant) and negative (unpleasant) emotional valence, produced in various
contexts by seven species of ungulates. With an accuracy of 89.49% (balanced accuracy: 83.90%), we found
that the most important predictors of emotional valence were acoustic variables reﬂecting changes in dura-
tion, energy quartiles, fundamental frequency, and amplitude modulation. This approach is critical in the ﬁeld
of emotional communication, where more information is needed to reach a better understanding of the
emotional origins of human language. In addition, these results can help toward the development of auto-
mated tools for animal well-being monitoring.
INTRODUCTION
Emotions can be deﬁned as short-lived and vital reactions that
elicit changes in the autonomic and somatic nervous systems.1
They can be categorized in a two-dimensional space: arousal
(bodily activation) and valence (positive/pleasant versus nega-
tive/unpleasant).2 Emotional arousal is relatively straightforward
to infer in non-human animals using, among others, physiolog-
ical (heart rate or cortisol) or behavioral (body movement) indica-
tors. By contrast, valence is both crucial for animal welfare and
notoriously difﬁcult to assess.3 However, behavior and, notably,
vocalizations are promising valence indicators.4
During vocal production, emotion-related changes result in
modiﬁcations of acoustic features through tension and action
of muscles used for voice production.5 As a result, consistent
changes in vocal expression of arousal have been found across
species,6 enabling not only humans to recognize emotional
arousal in the vocalizations of a wide range of vertebrate spe-
cies,7 but also distant vertebrates such as crocodiles to perceive
distress in human baby cries.8 It is less clear, however, whether
this is also the case for vocal expression of emotional valence.9
Yet, few acoustic features (e.g., duration) seem to encode
valence across species,6 and recent studies suggest that hu-
mans can also identify emotional valence above chance levels
in the vocalizations of a number of other species.9,10
The recent expansion of computational statistics and their
use in detecting and categorizing animal vocalizations widens
the potential to decode animal vocalizations.11 In recent
years, studies that have been interested in sound-emitting
species have beneﬁted from the automation of analyses,
leading to diverse applications,12 such as the detection of vo-
calizations of endangered bird species for automatic habitat
mapping,13 conservation status assessment of species,14
and
automated
information
retrieval
from
soundscape
recordings.15 Recent studies exploring automatic acoustic
recognition systems also reported promising results in evalu-
ating the effects of environmental enrichment on separation
stress behavior in chicks,16 detecting estrus in cattle17 and
distress in chickens,18 or classifying emotional valence in
pigs’ vocalizations.19 However, despite recent advances, ma-
chine-driven acoustic classiﬁcation of emotions has never
been explored in multiple species within the same study.
The present study represents a ﬁrst attempt at employing a
machine learning algorithm, speciﬁcally the eXtreme Gradient
Boosting (XGBoost) algorithm, for simultaneous analysis of
emotional valence in the vocalizations of multiple species.
By analyzing vocal data from several ungulates, we aim to un-
cover shared acoustic correlates of emotional valence, testing
the hypothesis that speciﬁc vocal characteristics universally
signal positive or negative emotions. This cross-species
approach not only distinguishes our work from previous sin-
gle-species studies but also sets the groundwork for the
development
of
a
universal
tool
for
emotional
valence
classiﬁcation.
iScience 28, 111834, February 21, 2025 ª 2025 The Authors. Published by Elsevier Inc.
1
This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).
ll
OPEN ACCESS


## Page 3

RESULTS
We performed a series of complementary analyses that aimed at
understanding the acoustic correlates of emotional valence in
seven species of domestic and wild ungulates: cows, sheep,
horses, Przewalski’s horses, pigs, wild boars, and goats20
(Table S1 and Data S1). For all these calls, the context of produc-
tion associated with vocal production was known and allowed us
to determine the emotional valence experienced by the animals
(validated during previous studies based on behavioral indica-
tors20). The limitation to contact calls meant that all calls had
the same biological function, hence eliminating this confounding
factor. It also ensured a balanced number of low- and high-
arousal contexts of each valence, as well as avoided very high
arousal contexts such as distress or fear, in order to control for
the effect of arousal on vocalizations (Table S1, Data S1). We ex-
tracted 17 representative acoustic features from these calls
(Data S2 and Table S2), which were used as input variables in
our analyses (see STAR Methods for more details).
These analyses aimed to (1) explore and visualize patterns of
separability between species and emotional valence categories
through
dimensionality
reduction,
using
uniform
manifold
approximation and projection (UMAP), (2) quantify within- and
between-species variation in the acoustic features coding for
emotional valence, (3) assess the degree of separability of
emotional valence for each species using clustering (k-means)
and classiﬁcation (Naive Bayes), (4) achieve automated classiﬁ-
cation of emotional valence across species using a decision-
tree-based ensemble algorithm (XGBoost), (5) identify the most
inﬂuential acoustic features contributing to valence classiﬁcation
and model predictions through Shapley additive explanations
(SHAP), and (6) test the generalizability of the model by relying
on cross-validation and species-speciﬁc classiﬁers. The results
of these analyses are presented in the following paragraphs,
beginning with the exploration of the underlying structure of
the acoustic features using UMAP, k-means clustering, and
Naive Bayes to assess the separability and classiﬁcation accu-
racy of emotional valence within each species, followed by the
automated classiﬁcation of emotional valence using XGBoost,
and concluding with the identiﬁcation of the most important
acoustic features driving valence classiﬁcation through SHAP.
Context, valence, and species separation with UMAP
First, we relied on a stochastic algorithm (UMAP algorithm) to
visually explore and evaluate the degree of separability between
the contexts of vocal production, the emotional valence, and the
species. UMAP is a dimensionality reduction technique that visu-
alizes complex, high-dimensional data in lower-dimensional
space, preserving both local and global data structures.21 The
primary goal of employing UMAP was to complement our ana-
lyses by offering insights into the data distribution, rather than
to perform explicit cluster analysis.
Results revealed the separability of positive and negative calls
across species (Figure 1). Horses and Przewalski’s horses stood
apart from the other species, with their respective clusters being
more distant from those of other species. Despite this distance,
they both showed clear separability in vocalizations with respect
to emotional valence. Sheep vocalizations also stood apart from
other species regardless of emotional valence, but showed mod-
erate discrimination between positive and negative valences
Figure 1. UMAP visualization of emotional valence classiﬁcation in ungulate vocalizations
Valence and species classiﬁcation based on UMAP mapping. UMAP1 and UMAP2 represent the ﬁrst and second dimensions, respectively, derived from high-
dimensional data to visualize clustering based on similarity. Colors represent the different ungulate species.
See also Figure S1 for species-speciﬁc visualizations.
2
iScience 28, 111834, February 21, 2025
iScience
Article
ll
OPEN ACCESS


## Page 4

within their calls. Pig vocalizations formed multiple and scattered
clusters with respect to valence, suggesting signiﬁcant valence
separability in their calls. Wild boar calls demonstrated notice-
able separation between positive and negative valence, while
also showing overlap with other species, indicating both distinct
valence separability and potential similarities in emotional
expression with other species. Goat calls, on the other hand, ex-
hibited indistinct clusters, with less clear boundaries between
positive and negative valence. Finally, cow vocalizations showed
moderate overlap between positive and negative valence. Over-
all, the species’ separation in acoustic features was visible, but
the clarity of emotional valence separation varied between spe-
cies (Figure 1; Figure S1).
Following this visualization, we performed k-means clustering
on the UMAP projections for each species to quantify valence
separability and calculate clustering purity and classiﬁcation ac-
curacy using Naive Bayes classiﬁer. K-means clustering was
employed as an unsupervised learning method to identify under-
lying patterns in the UMAP-reduced feature space by grouping
vocalizations into clusters that minimize within-cluster variance.
This method allowed us to explore natural groupings based on
emotional valence within each species, leveraging the reduced
dimensionality representation provided by UMAP to enhance
interpretability and cluster formation.22 In parallel, we applied
Naive Bayes classiﬁcation, a supervised probabilistic algorithm,
to the UMAP-projected acoustic features, in order to estimate
the probability of vocalizations belonging to positive or negative
valence categories. This algorithm is known for its efﬁciency and
effectiveness in datasets where dimensionality is reduced and
the features are well deﬁned, such as with UMAP-derived dimen-
sions.23 The results of these analyses revealed that pig vocaliza-
tions achieved the highest classiﬁcation accuracy (94.84%) with
a conﬁdence interval ranging from 91.68% to 97.60%, and a
clustering purity of 69.66% (conﬁdence interval: 63.81%–
76.55%). This suggests that pig vocalizations may contain
acoustic cues that are reliable enough to allow for successful
emotional valence classiﬁcation and clustering. Similarly, cow
vocalizations displayed moderate accuracy (57.18%) but high
clustering purity (78.03%), suggesting that, while classiﬁcation
performance is moderate, the high clustering purity still indicates
a degree of emotional valence differentiation. In contrast, goat
and wild boar vocalizations exhibited lower accuracy rates
(49.03% and 49.10%, respectively), with relatively high clus-
tering purity (76.30% for goats and 72.85% for wild boars). The
wide
conﬁdence
intervals
for
accuracy
(goats:
36.54%–
61.07%; wild boars: 32.73%–66.42%) suggest that the classiﬁer
struggled to predict valence accurately, likely due to overlapping
acoustic patterns between positive and negative vocalizations.
Similarly, sheep and Przewalski’s horses demonstrated poor
classiﬁcation accuracy (48.25% and 48.03%, respectively), but
higher clustering purity (77.65% for sheep and 84.87% for Prze-
walski’s horses). Speciﬁcally, the large conﬁdence intervals for
accuracy in Przewalski’s horses (31.93%–62.37%) indicate
important variability in the classiﬁcation model’s performance
for this species (Table S3). Overall, these results suggest that
while UMAP provides some degree of discrimination, its effec-
tiveness for emotional valence separability may have been inﬂu-
enced by both the complexity of our acoustic data and the
intrinsic limitations of the UMAP algorithm in capturing subtle
emotional patterns across species.
Automated valence classiﬁcation with XGBoost
Following this exploratory phase, we used a decision tree
ensemble learning algorithm (XGBoost) to discriminate calls
based on their valence. XGBoost is an implementation of
gradient-boosted decision trees, and a method used to build a
series of trees that are each trained to minimize the residual error
and favor the correct classiﬁcation of cases that were previously
misclassiﬁed.24 Our XGBoost model reported an overall accu-
racy in classifying valence of 89.49% (conﬁdence interval:
87.31%, 91.41%), a Cohen’s kappa of 0.66, and a balanced ac-
curacy of 83.90% with a sensitivity of 75.00% and a speciﬁcity of
92.80%. The model also reported 70.39% of correct classiﬁca-
tion for the positive calls, 94.21% for the negative calls, and an
F-score of 72.62% (Table S4). The confusion matrix reported
126 true positive, 683 true negative, 53 false positive, and 42
false negative classiﬁcations.
To strengthen our claims and ensure the identiﬁcation of uni-
versal rather than species-speciﬁc features in emotional classi-
ﬁcation, we additionally trained individual XGBoost classiﬁers
for each species and extracted the ten most important acoustic
features based on their gain. This approach enabled us to high-
light key features that consistently inﬂuenced valence classiﬁ-
cation across species. Results reported that pigs (99.91%)
and Przewalski’s horses (97.78%) achieved the highest model
accuracies, suggesting clearer separability between valence
categories in these species. Goats, cows, and sheep also
demonstrated
strong
performance,
with
an
accuracy
of
90.74%, 92.93%, and 88.55%, respectively. In contrast, spe-
cies such as wild boars (82.71%) and horses (81.38%) showed
lower accuracies, which may suggest more overlapping acous-
tic patterns, making valence classiﬁcation more challenging.
Based on the ten most important gain values, we found that
the interquartile range of amplitude modulation depth (‘‘amEnv-
Dep_iqr’’), duration, the 25th percentile of energy quartiles
(‘‘quartile25_median’’), and the interquartile range of the 75th
percentile of energy quartiles for voiced parts (‘‘quartile75Voi-
ced_iqr’’) were highly relevant across all species. Additional
inﬂuential features included the median amplitude modulation
depth (‘‘amEnvDep_median’’), the median frequency of ampli-
tude modulation for voiced parts (‘‘amEnvFreqVoiced_me-
dian’’),
the
interquartile
range
of
amplitude
modulation
frequency (‘‘amEnvFreq_iqr’’), the median fundamental fre-
quency (‘‘pitch_median’’), the median frequency modulation
(‘‘fmFreq_median’’), the interquartile ranges of roughness
(‘‘roughness_iqr’’) and the spectral centroid (‘‘specCentroi-
d_iqr’’), each consistently important across six species. Finally,
though less frequent, the interquartile range of fundamental fre-
quency (‘‘pitch_iqr’’) and the median roughness for voiced parts
(‘‘roughnessVoiced_median’’) were inﬂuential across ﬁve spe-
cies, while the interquartile range of frequency modulation
(‘‘fmFreq_iqr’’) appeared in four species (Table S5). While
some acoustic features may serve as robust predictors of
emotional valence across species, our results suggest that
there is also a degree of species-level variability in how
emotional states are expressed vocally.
iScience 28, 111834, February 21, 2025
3
iScience
Article
ll
OPEN ACCESS


## Page 5

Model explanation with SHAP
SHAP values are a method from game theory applied in machine
learning to explain model predictions. They quantify the contri-
bution of each variable to a speciﬁc prediction, providing
detailed insights into model behavior with accuracy and consis-
tency.25 We therefore used this approach to evaluate the impor-
tance of acoustic variables and their effect on our classiﬁer using
SHAP values. Results showed that the ten acoustic variables im-
pacting the prediction of the emotional valence the most in our
XGBoost model included variables characterizing the amplitude
modulation depth and frequency (‘‘am’’), the duration, the energy
distribution across quartiles (e.g., ‘‘quartile25’’) and the funda-
mental frequency (‘‘pitch’’) (Figure 2A).
In complement, we used Spearman’s coefﬁcient correlations
to analyze the strength and directionality of each acoustic vari-
able with its respective contribution to the model’s predictions,
as indicated by SHAP values. This helped us understand which
variables were most inﬂuential in classifying emotional valence.
Looking at moderate (R0.30) to strong correlations, positive
contact calls exhibited lower depth of amplitude modulation
(‘‘amEnvDep_median’’), lower fundamental frequency variability
(‘‘pitch_iqr’’), less spectral energy in high frequencies (‘‘quarti-
le25_median,’’ ‘‘quartile75Voiced_median,’’ and ‘‘quartile50Voi-
ced_iqr’’), and shorter duration (‘‘duration’’) compared with
negative calls (Figure 2B).
DISCUSSION
The present work provides quantitative evidence for shared
acoustic correlates of emotional valence in the contact calls of
seven species of ungulates, which could also apply to a broader
range of species. Our XGBoost model achieved an overall accu-
racy of 89.49% in classifying emotional valence, with a balanced
accuracy of 83.90%. The model demonstrated high speciﬁcity
(92.80%) and sensitivity (75.00%), highlighting its effectiveness
in distinguishing emotional valence. The detailed insights pro-
vided by SHAP revealed the most inﬂuential acoustic variables
driving these classiﬁcations, enhancing our comprehension of
the complex interplay between vocal characteristics and
emotional expressions. Positive calls were characterized by
lower amplitude modulation and lower fundamental frequency
variability, contained less spectral energy in high frequencies,
and were shorter in duration compared to negative calls. By
training individual XGBoost classiﬁers for each species, we
also identiﬁed duration and amplitude modulation as acoustic
features that consistently ranked highly in their importance to
classify valence across species. Overall, our ﬁndings hence
corroborate the notion that certain acoustic variables may serve
as universal indicators of emotional valence across species,
supporting previous investigations.6,26 These results support
the idea that positive emotional valence is associated with lower
energy quartiles, as similarly explored in horses,27 Przewalski’s
horses,28 and wild boars,29 as well as less variable fundamental
frequency and shorter call duration, two consistent indicators of
emotional valence across species.6
By training individual XGBoost classiﬁers for each species, our
models demonstrated high overall accuracy in valence classiﬁ-
cation, with accuracy values ranging from 81.38% in horses to
99.91% in pigs. More importantly, these models conﬁrmed the
relevance of key acoustic features such as the interquartile range
of amplitude modulation depth (‘‘amEnvDep_iqr’’), duration, and
energy quartiles (‘‘quartile25_median,’’ ‘‘quartile75Voiced_iqr’’),
which were identiﬁed as important predictors in both individual
species classiﬁers, based on gain, and the general XGBoost
model based on SHAP. This alignment between the individual
and general XGBoost classiﬁers strengthens the claim that, while
species-speciﬁc variability exists, common acoustic correlates
may still underpin the vocal expression of emotional valence
across ungulates.
UMAP analysis also demonstrated species-speciﬁc patterns
in acoustic variables and revealed that the clarity of emotional
valence separation varied across species. Horses and Przewal-
ski’s horses, grouped together away from other species, both
showed signiﬁcant separability between the two emotional va-
lences. This distinction from other species could be attributed
to the fact that horse whinnies can be very long in duration (up
to 5 s long) and have a complex frequency modulation.27,28
Sheep vocalizations also set apart from other species and
showed moderate discrimination between positive and negative
valence. Similarly, pig vocalizations formed multiple and scat-
tered clusters with respect to the two emotional valences, indi-
cating clear separability. This dispersion, with apparent sub-
types with respect to emotional valence, could reﬂect short
and long grunts, mostly indicative of positive and negative
valence,
respectively.30
Wild
boars’
grunts
demonstrated
noticeable separation between positive and negative valence
as well, but with more overlap compared to pigs’ positive and
negative grunts, which showed greater separability, therefore
suggesting that the expression of emotional valence could differ
between pigs and wild boars, as previously reported.29 Goat
calls exhibited indistinct clusters with less clear boundaries,
indicative of overlapping acoustic variables across different
emotional states. Finally, cow vocalizations showed moderate
overlap between positive and negative valences.
The application of k-means clustering and Naive Bayes classi-
ﬁcation to the UMAP projections provided preliminary insights
into the separability of emotional valence within each species.
Pigs demonstrated the clearest separation, with high classiﬁca-
tion accuracy (94.84%) and clustering purity (69.66%). This sug-
gests that their contact calls contain distinguishable emotional
information, likely due to well-differentiated vocal patterns be-
tween positive and negative valence, such as the previously re-
ported distinction between short and long grunts.30 In contrast,
species like goats, wild boars, and Przewalski’s horses exhibited
lower classiﬁcation accuracy, despite relatively high clustering
purity. The variability in performance across species indicates
that emotional valence may not be uniformly distinguishable
based solely on UMAP projections. While UMAP results indi-
cated that Przewalski’s horses stood apart from other species,
the large conﬁdence intervals observed in k-means and Naive
Bayes classiﬁcations highlight variability in valence-level separa-
bility for this species. The high accuracy achieved by the individ-
ual XGBoost classiﬁer for Przewalski’s horses may reﬂect its ca-
pacity to capture nuanced acoustic patterns missed by other
methods. These differences further highlight the complementary
nature of these analyses: UMAP provides a visual overview of
4
iScience 28, 111834, February 21, 2025
iScience
Article
ll
OPEN ACCESS


## Page 6

Figure 2. Multivariate analysis of acoustic variables impacting the emotional valence classiﬁcation in ungulate vocalizations using an
XGBoost model
(A) Shapley summary plot visualizing the contribution of the ten most important acoustic variables (among 17 extracted variables in total) to the model’s prediction
of emotional valence. Each data point on the plot is a Shapley value for a given variable and instance. Acoustic variables are ordered on the y axis according to
their mean Shapley value. Shapley values deﬁne the direction and magnitude of a variable’s impact on the model’s output. Positive Shapley values indicate that a
variable’s value contributes to an increase in the predicted outcome, namely the positive valence, while negative Shapley values indicate a contribution to a
decrease in that prediction, pointing toward the negative valence. Color intensity codes for the variable value.
(B) SHAP paired correlation plot illustrating the Spearman coefﬁcient correlations (r) and p value between variable values and their corresponding SHAP values.
Positive correlations indicate higher values for a given acoustic variable in positive vocalizations compared with negative ones, while negative correlations
indicate higher values for a given acoustic variable in negative vocalizations compared with positive ones.
iScience 28, 111834, February 21, 2025
5
iScience
Article
ll
OPEN ACCESS


## Page 7

patterns of interest, k-means and Naive Bayes offer statistical
quantiﬁcations, and XGBoost delivers predictive performance
by leveraging complex relationships in the data.
Incorporating UMAP for dimensionality reduction provided
insightful visualizations of our complex dataset, showing poten-
tial relationships in how different ungulate species use similar
acoustic features to convey positive and negative affective
states. However, the UMAP structures might not necessarily
represent distinct biological clusters due to their emphasis on
preserving data relationships in reduced dimensions. Interpreta-
tions of these visual patterns should be made carefully and be
complemented with statistical analyses to ensure that conclu-
sions are grounded in veriﬁable data due to algorithm limitations.
In addition, while the overrepresentation of negative calls in cows
could have inﬂuenced our results, this potential bias under-
scores the importance of balanced datasets for training models
to ensure generalizability and unbiased performance across
various contexts and species.
Our investigation was constrained by the limited availability of
validated emotional state datasets, which included seven spe-
cies. While diverse, this selection highlights the challenges of
assembling comprehensive databases across a broader range
of species, as well as assessing and validating emotional states
under comparable conditions. This limitation highlights the need
for increased collaborative efforts to expand these datasets. To
this extent, our study serves as a valuable ﬁrst step, paving the
way for future research to further explore the universal aspects
of vocal expression of emotional valence across more species.
This work should further support the application of machine
learning in acoustic communication as a transformative tool for
animal welfare research and beyond, with implications for con-
servation efforts, bioacoustics monitoring, and enhancing hu-
man-animal interactions.
Limitations of the study
While this study provides preliminary insights into the acoustic
correlates of emotional valence in ungulates, several limitations
should be considered. First, while our dataset encompasses a
diverse set of species and achieves high classiﬁcation accuracy
(e.g., 89.49% with XGBoost), the inclusion of additional species
and emotional contexts would further enhance the generaliz-
ability of our ﬁndings. Second, differences in species-speciﬁc
classiﬁcation performance (e.g., lower separability in goats and
cows) highlight that vocal emotional expression may vary across
taxa, and future studies should account for such variability
when developing universal models. Finally, the slight overrepre-
sentation of negative calls in some species, such as cows, em-
phasizes the importance of balanced datasets for training
unbiased models. Addressing these limitations in future research
will be fundamental to expand the applicability of machine
learning tools for understanding emotional communication and
improving animal welfare monitoring.
RESOURCE AVAILABILITY
Lead contact
For further information and resource requests, please contact Elodie F. Briefer
elodie.briefer@bio.ku.dk.
Materials availability
This research did not produce any new unique materials.
Data and code availability
d The dataset used in this study (i.e., the sound database) has been up-
loaded on Zenodo and is publicly available as of the date of publication
at https://doi.org/10.5281/zenodo.14636641.
d The original R scripts used for data preprocessing, feature extraction,
and model training are not publicly available but will be shared by the
lead contact upon request.
d Any additional information required to reanalyze the data reported in this
paper is available from the lead contact upon request.
ACKNOWLEDGMENTS
We are grateful to Jeppe H Rasmussen for useful suggestions, Andrey Anikin
for his attention and support on using soundgen package as well as for com-
menting on our manuscript, and Anne-Laure Maigrot, Monica Padilla de la
Torre, and Piera Filippi for collecting some of the vocalizations. This research
was funded by Swiss National Science Foundation awarded to E.F.B. (grant
nos. PZ00P3_148200 and 310030_185198).
AUTHOR CONTRIBUTIONS
All authors conceptualized the project. R.A.L. and C.C.S. designed and per-
formed the analyses and wrote the ﬁrst draft. E.F.B. supervised and funded
the project. All authors commented on the manuscript.
DECLARATION OF INTERESTS
The authors declare no competing interests.
STAR+METHODS
Detailed methods are provided in the online version of this paper and include
the following:
d KEY RESOURCES TABLE
d EXPERIMENTAL MODEL AND STUDY PARTICIPANT DETAILS
d METHOD DETAILS
B Data extraction
d QUANTIFICATION AND STATISTICAL ANALYSIS
B Data manipulation
d ADDITIONAL RESOURCES
SUPPLEMENTAL INFORMATION
Supplemental information can be found online at https://doi.org/10.1016/j.isci.
2025.111834.
Received: November 10, 2023
Revised: June 17, 2024
Accepted: January 15, 2025
Published: January 17, 2025
REFERENCES
1. Paul, E.S., and Mendl, M.T. (2018). Animal emotion: Descriptive and pre-
scriptive deﬁnitions and their implications for a comparative perspective.
Appl. Anim. Behav. Sci. 205, 202–209. https://doi.org/10.1016/j.appla-
nim.2018.01.008.
2. Russell, J.A. (1980). A circumplex model of affect. J. Pers. Soc. Psychol.
39, 1161–1178. https://doi.org/10.1037/h0077714.
3. Kremer, L., Klein Holkenborg, S.E.J., Reimert, I., Bolhuis, J.E., and Webb,
L.E. (2020). The nuts and bolts of animal emotion. Neurosci. Biobehav.
Rev. 113, 273–286. https://doi.org/10.1016/j.neubiorev.2020.01.028.
6
iScience 28, 111834, February 21, 2025
iScience
Article
ll
OPEN ACCESS


## Page 8

4. Hinchcliffe, J.K., Mendl, M., and Robinson, E.S.J. (2020). Rat 50 kHz calls
reﬂect graded tickling-induced positive emotion. Curr. Biol. 30, R1034–
R1035. https://doi.org/10.1016/j.cub.2020.08.038.
5. Scherer, K. (2003). Vocal communication of emotion: A review of research
paradigms. Speech Commun. 40, 227–256. https://doi.org/10.1016/
S0167-6393(02)00084-5.
6. Briefer, E.F. (2020). Vocal expression of emotional arousal and valence in
non-human animals. In Animal Signals and Communications: Coding stra-
tegies in vertebrate acoustic communication, 7 (Springer), pp. 137–162.
https://doi.org/10.1007/978-3-030-39200-0_6.
7. Filippi, P., Congdon, J.V., Hoang, J., Bowling, D.L., Reber, S.A., Pa-
sukonis, A., Hoeschele, M., Ocklenburg, S., de Boer, B., Sturdy, C.B.,
et al. (2017). Humans recognize emotional arousal in vocalizations across
all classes of terrestrial vertebrates: evidence for acoustic universals.
Proc. Biol. Sci. 284, 20170990. https://doi.org/10.1098/rspb.2017.0990.
8. The´ venet, J., Papet, L., Coureaud, G., Boyer, N., Levre´ ro, F., Grimault, N.,
and Mathevon, N. (2023). Crocodile perception of distress in hominid baby
cries. Proc. R. Soc. A B 290, 20230201. https://doi.org/10.1098/rspb.
2023.0201.
9. Laurijs, K.A., Briefer, E.F., Reimert, I., and Webb, L.E. (2021). Vocalisations
in farm animals: a step towards positive welfare assessment. Appl. Anim.
Behav.
Sci.
236,
105264.
https://doi.org/10.1016/j.applanim.2021.
105264.
10. Greenall, J.S., Cornu, L., Maigrot, A.-L., de la Torre, M.P., and Briefer, E.F.
(2022). Age, empathy, familiarity, domestication and call features enhance
human perception of animal emotion expressions. R. Soc. Open Sci. 9,
221138. https://doi.org/10.1098/rsos.221138.
11. Rutz, C., Bronstein, M., Raskin, A., Vernes, S.C., Zacarian, K., and Blasi,
D.E. (2023). Using machine learning to decode animal communication.
Science 381, 152–155. https://doi.org/10.1126/science.adg7314.
12. Rasmussen, J.H., Stowell, D., and Briefer, E.F. (2024). Sound evidence for
biodiversity monitoring. Science 385, 138–140. https://doi.org/10.1126/
science.adh2716.
13. Bardeli, R., Wolff, D., Kurth, F., Koch, M., Tauchert, K.H., and Frommolt,
K.H. (2010). Detecting bird sounds in a complex acoustic environment
and application to bioacoustic monitoring. Pattern Recogn. Lett. 31,
1524–1534. https://doi.org/10.1016/j.patrec.2009.09.014.
14. Davidson, A.D., Boyer, A.G., Kim, H., Pompa-Mansilla, S., Hamilton, M.J.,
Costa, D.P., Ceballos, G., and Brown, J.H. (2012). Drivers and hotspots of
extinction risk in marine mammals. Proc. Natl. Acad. Sci. USA 109, 3395–
3400. https://doi.org/10.1073/pnas.1121469109.
15. Lin, T., and Tsao, Y. (2019). Source separation in ecoacoustics: A roadmap
towards versatile soundscape information retrieval. Remote Sens. Ecol.
Conserv. 6, 236–247. https://doi.org/10.1002/rse2.141.
16. Kim, E.H., and Sufka, K.J. (2011). The effects of environmental enrichment
in the chick anxiety-depression model. Behav. Brain Res. 221, 276–281.
https://doi.org/10.1016/j.bbr.2011.03.013.
17. Ro¨ ttgen, V., Scho¨ n, P.C., Becker, F., Tuchscherer, A., Wrenzycki, C.,
D€upjan, S., and Puppe, B. (2020). Automatic recording of individual oes-
trus vocalisation in group-housed dairy cattle: development of a cattle
call
monitor.
Animal
14,
198–205.
https://doi.org/10.1017/S175173
1119001733.
18. Mao, A., Giraudet, C.S.E., Liu, K., De Almeida Nolasco, I., Xie, Z., Xie, Z.,
Gao, Y., Theobald, J., Bhatta, D., Stewart, R., and McElligott, A.G. (2022).
Automated identiﬁcation of chicken distress vocalizations using deep
learning models. J. R. Soc. Interface 19, 20210921. https://doi.org/10.
1098/rsif.2021.0921.
19. Briefer, E.F., Sypherd, C.C.R., Linhart, P., Leliveld, L.M.C., Padilla de la
Torre, M., Read, E.R., Gue´ rin, C., Deiss, V., Monestier, C., Rasmussen,
J.H., et al. (2022). Classiﬁcation of pig calls produced from birth to
slaughter according to their emotional valence and context of production.
Sci. Rep. 12, 3409. https://doi.org/10.1038/s41598-022-07174-8.
20. Lefe` vre, R.A., Sypherd, C.C.-R., and Briefer, E.F. (2024). Universal
Emotional Translators Database. Zenodo. https://doi.org/10.5281/zen-
odo.14636641.
21. McInnes, L., Healy, J., and Melville, J. (2018). UMAP: Uniform Manifold
Approximation and Projection. J. Open Source Softw. 3, 861. https://
doi.org/10.21105/joss.00861.
22. Jain, A.K. (2010). Data clustering: 50 years beyond k-means. Pattern Re-
cogn. Lett. 31, 651–666. https://doi.org/10.1016/j.patrec.2009.09.011.
23. Zhang, H. (2005). Exploring conditions for the optimality of Naı¨ve Bayes.
Int. J. Pattern Recognit. Artif. Intell. 19, 183–198. https://doi.org/10.
1142/S0218001405003983.
24. Friedman, J.H. (2001). Greedy function approximation: a gradient boosting
machine.
Ann.
Stat.
29,
1189–1232.
https://doi.org/10.1214/aos/
1013203451.
25. Lundberg, S., and Lee, S. (2017). A uniﬁed approach to interpreting model
predictions. In Proceedings of the 31st International Conference on Neural
Information Processing Systems (NIPS ’17) (Curran Associates Inc).
https://doi.org/10.48550/arXiv.1705.07874.
26. Briefer, E.F. (2012). Vocal expression of emotions in mammals: mecha-
nisms of production and evidence. J. Zool. 288, 1–20. https://doi.org/10.
1111/j.1469-7998.2012.00920.x.
27. Briefer, E.F., Maigrot, A.L., Mandel, R., Freymond, S.B., Bachmann, I., and
Hillmann, E. (2015). Segregation of information about emotional arousal
and valence in horse whinnies. Sci. Rep. 4, 9989. https://doi.org/10.
1038/srep09989.
28. Maigrot, A.L., Hillmann, E., Anne, C., and Briefer, E.F. (2017). Vocal
expression of emotional valence in Przewalski’s horses (Equus przewal-
skii). Sci. Rep. 7, 8779. https://doi.org/10.1038/s41598-017-09437-1.
29. Maigrot, A.L., Hillmann, E., and Briefer, E.F. (2018). Encoding of emotional
valence in wild boar (Sus scrofa) calls. Animals 8, 85. https://doi.org/10.
3390/ani8060085.
30. Briefer, E.F., Vizier, E., Gygax, L., and Hillmann, E. (2019). Expression of
emotional valence in pig closed-mouth grunts: involvement of both
source- and ﬁlter-related parameters. J. Acoust. Soc. Am. 145, 2895.
https://doi.org/10.1121/1.5100612.
31. Boersma, P. (2014). Acoustic analysis. In Research methods in linguistics,
R.
Podesva
and
D.
Sharma,
eds.
(Cambridge
University
Press),
pp. 375–396. https://doi.org/10.1017/cbo9781139013734.020.
32. R Core Team (2024). R: A Language and Environment for Statistical
Computing (Vienna, Austria: R Foundation for Statistical Computing).
https://www.R-project.org/.
33. The MathWorks Inc (2022). MATLAB Version: 9.13.0 (R2022b) (Natick, MA:
The MathWorks Inc.). https://www.mathworks.com.
34. Padilla de la Torre, M., Hillmann, E., and Briefer, E.F. (2015). Vocal expres-
sion of emotion in cattle. In Proc. 25th Int. Congress of the Bioacoustics
Council, Murnau, Germany, 7–12 September 2015.
35. Briefer, E.F., Tettamanti, F., and McElligott, A.G. (2015). Emotions in goats:
mapping physiological, behavioural and vocal proﬁles. Anim. Behav. 99,
131–143. https://doi.org/10.1016/j.anbehav.2014.11.002.
36. Lefe` vre, R., Filippi, P., Leboffe, A., and Briefer, E.F. (2024). Emotions in
Sheep (Ovis aries): A Quantitative Approach. In prepration.
37. RStudio Team (2020). RStudio: Integrated Development for R (RStudio,
PBC, Boston). http://www.rstudio.com/.
38. Anikin, A. (2019). Soundgen: An open-source tool for synthesizing
nonverbal vocalizations. Behav. Res. Methods 51, 778–792. https://doi.
org/10.3758/s13428-018-1095-7.
39. Oppenheim, A.V., Schafer, R.W., and Buck, J.R. (1999). Discrete-time
Signal Processing (Upper Saddle River, NJ: Prentice Hall).
40. Kim, J.H. (2019). Multicollinearity and misleading statistical results. Korean
J. Anesthesiol. 72, 558–569. https://doi.org/10.4097/kja.19087.
iScience 28, 111834, February 21, 2025
7
iScience
Article
ll
OPEN ACCESS


## Page 9

41. Vittinghoff, E. (2005). Regression Methods in Biostatistics: Linear, Logistic,
Survival, and Repeated Measures Models (New York, NY: Springer).
https://doi.org/10.1007/978-1-4614-1353-0.
42. Naimi, B., Hamm, N.A.S., Groen, T.A., Skidmore, A.K., and Toxopeus,
A.G. (2014). Where is positional uncertainty a problem for species distribu-
tion modelling. Ecography 37, 191–203. https://doi.org/10.1111/j.1600-
0587.2013.00205.x.
43. Kuhn, M. (2022). caret: Classiﬁcation and Regression Training. R package
version 6.0-93. https://doi.org/10.32614/CRAN.package.caret.
44. Wongvorachan, T., He, S., and Bulut, O. (2023). A Comparison of Under-
sampling, Oversampling, and SMOTE Methods for Dealing with Imbal-
anced Classiﬁcation in Educational Data Mining. Information 14, 54.
https://doi.org/10.3390/info14010054.
45. Hvitfeldt, E. (2023). themis: Extra Recipes Steps for Dealing with Unbal-
anced
Data.
R
package
version
1.0.2.
https://doi.org/10.1007/
11538059_91.
46. Kuhn, M., Wickham, H., and Hvitfeldt, E. (2017). recipes: Preprocessing
and Feature Engineering Steps for Modeling. R package version 1.0.1.
https://doi.org/10.32614/CRAN.package.recipes.
47. Hvitfeldt, E., and Kuhn, M. (2018). embed: Extra Recipes for Encoding Pre-
dictors. R package version 1.0.0. https://doi.org/10.32614/CRAN.pack-
age.embed.
48. Wickham, H. (2016). ggplot2: Elegant Graphics for Data Analysis
(Springer-Verlag New York). https://doi.org/10.1007/978-3-319-24277-4.
49. Meyer, D., Dimitriadou, E., Hornik, K., Weingessel, A., and Leisch, F.
(2023). e1071: Misc Functions of the Department of Statistics, Probability
Theory Group (Formerly: E1071), TU Wien. R package version 1.7-14.
https://doi.org/10.32614/CRAN.package.e1071.
50. Chen, T., and Guestrin, C. (2016). XGBoost: A scalable tree boosting sys-
tem. In Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min.,
pp. 785–794. https://doi.org/10.1145/2939672.2939785.
51. Hastie, T., Tibshirani, R., and Friedman, J. (2009). Model inference aver-
aging. In The Elements of Statistical Learning: Data Mining, Inference,
and Prediction, T. Hastie, R. Tibshirani, and J. Friedman, eds. (New
York, NY: Springer), pp. 279–284.
52. Chen, T., He, T., Benesty, M., Khotilovich, V., Tang, Y., Cho, H., Chen, K.,
Mitchell, R., Cano, I., Zhou, T., et al. (2014). xgboost: Extreme Gradient
Boosting. R package version 1.6.0.1. https://doi.org/10.32614/CRAN.
package.xgboost.
53. Liu, Y., and Just, A. (2021). SHAPforxgboost: SHAP Plots for ‘XGBoost’. R
package version 0.1.1. https://doi.org/10.32614/CRAN.package.SHAP-
forxgboost.
8
iScience 28, 111834, February 21, 2025
iScience
Article
ll
OPEN ACCESS


## Page 10

STAR+METHODS
KEY RESOURCES TABLE
EXPERIMENTAL MODEL AND STUDY PARTICIPANT DETAILS
This study did not involve human subjects or samples. The data we analyzed were derived from the contact calls of seven ungulate
species: cows (Bos taurus), goats (Capra hircus), horses (Equus caballus), Przewalski’s horses (Equus przewalskii), pigs (Sus scrofa
domesticus), wild boars (Sus scrofa), and sheep (Ovis aries). Details about the species, sex and age, maintenance and care for the
animals whose contact calls were used in this study are available in the original studies from which the data were collected27–30,34–36
(see also Table S1 and Data S1). All acoustic recordings were collected in accordance with the current laws of the UK (goats) and
Switzerland (other species), and approved by ethical committees as part of our previous studies. The experiments carried out to
collect the goat recordings were reviewed by the U.K. Government Home Ofﬁce inspector for Queen Mary, University of London.
For the other species, experiments were approved by the Swiss Cantonal authorities (approval numbers: pigs, TG02/2014; wild boars
and Przewalski’s horses, ZH011/15; sheep, ZH233/18; horses, VD2689; cattle, ZH49/2014). In total, 3181 contact calls were
analyzed across the seven species. The sample size per species and emotional valence is detailed in Table S1 and Data S1.
METHOD DETAILS
Data extraction
We extracted acoustic features of a total of 3181 contact calls collected during our previous studies27–30,34–36 (Table S1, Data S1 and
S2). None of these collected calls had been produced consecutively by the animals. These vocalizations reﬂected emotions that were
validated as being of either positive or negative valence based on their context of production, such as social interactions versus isola-
tion, behavioral indicators including postural adjustments and movement patterns, as well as physiological measures for domestic
species. Each call therefore represented a single instance in the dataset, which was grouped by species, context, and valence during
analysis.
Initially, we manually assessed the data quality by listening to the recordings and examining their spectrograms in MATLAB
(version R2022b).33 During this assessment, 23 calls were identiﬁed as having signiﬁcant environmental acoustic interference,
such as overlapping frequencies with other sounds. These calls were excluded from further analysis. The remaining dataset, consist-
ing of 3181 calls, was then manually categorized into two quality levels - ’high quality’ and ’moderate quality’ - based on the signal-to-
noise ratio, both audibly and visually through spectrogram analysis. Then, for the purpose of evaluating the feasibility of including
moderate-quality calls in our analysis, we investigated their impact on the performance of a model. This investigation involved 1)
training a convolutional neural network, a ResNet-50 architecture, using only the high-quality calls to classify their context of produc-
tion and species and 2) creating and training a second classiﬁer that included a randomly selected mix of both high- and moderate-
quality calls. We then compared the accuracies of these two classiﬁers to assess if the inclusion of moderate-quality calls had a sig-
niﬁcant impact on the model’s predictive performance. Our comparative analysis revealed no signiﬁcant differences in performance
between the classiﬁers trained on high-quality calls alone and those trained on the mixed-quality dataset. This thus suggested that
moderate-quality calls maintained sufﬁcient information to contribute meaningfully to our analysis, thereby justifying their inclusion in
the combined dataset of 3181 calls for subsequent analysis.
QUANTIFICATION AND STATISTICAL ANALYSIS
Acoustic feature processing and statistical analyses were performed in RStudio (version 2022.07.1 + 554).37 Amplitude of the calls
was normalized prior to extraction with soundgen package38 and the normalizeFolder() function. The median and interquartile range
of 16 acoustic features (i.e., resulting in 32 feature-derived variables) related to frequency, energy, amplitude modulation, noise, and
REAGENT or RESOURCE
SOURCE
IDENTIFIER
Software and algorithms
Praat
Boersma31
http://www.praat.org/
R Studio
R Core Team32
http://www.rstudio.com/
MATLAB
The MathWorks Inc33
http://www.mathworks.com
Deposited data
Zenodo
http://zenodo.org/
Zenodo: https://doi.org/10.5281/zenodo.14636641
iScience 28, 111834, February 21, 2025
e1
iScience
Article
ll
OPEN ACCESS


## Page 11

harmonicity were then extracted based on soundgen package’s analyze() function. The duration of the calls was also extracted (33
variables in total; Table S6). These acoustic features were chosen among all possible features, as they have previously been shown to
vary with emotional valence in the previous studies where these calls were recorded27–30,34–36 (Data S1).
For each species, context and valence, acoustic features were extracted based on a 100 ms short-time Fourier transform and a
50 ms sliding window. Only horse and Przewalski’s horse calls were processed using a 50 ms short-time Fourier transform and a
10 ms sliding window to account for rapid variation in the frequency of their calls, as previously reported.27 To determine the settings
for the automated fundamental frequency (fo) extraction using soundgen, we ﬁrst estimated the fo range for each species in Praat
(version 6.2.14).31 To do so, we obtained the minimum, maximum, and mean fo values using a custom-built script on a balanced data-
set consisting of 10 randomly selected calls per species, for each type of context and valence. A similar procedure was used to
choose the settings for the frequency range of amplitude modulation, based on the minimum and maximum cumulative variation
in amplitude divided by the total call duration (dB/s). Acoustic features were then automatically extracted using soundgen with Han-
ning windowing function39 combining autocorrelation, spectral and cepstral methods of estimation of the fo to determine its contour
more precisely. The acoustic data preprocessing involved restricting the frequency range of analysis to between the minimum
observed fundamental frequency (fo) of the vocalizations and 20 kHz. This decision aimed to focus on the spectral content most rele-
vant to the animal vocalizations by excluding higher frequencies predominantly associated with background noise, thereby
enhancing the signal’s clarity for variable extraction. To determine the fundamental frequency, we performed an automated spectral
analysis in soundgen to assess the frequency components in each call and identiﬁed the lowest frequency at which vocalization en-
ergy was consistently present. In addition, we graphically checked the quality of pitch tracking using soundgen’s spectrogram() func-
tion for 10 randomly selected calls from each species, across each identiﬁed context and valence (see examples in Figure S2).
Data manipulation
We decided to replace observations affected by missing data (mean ± SD per species = 3.10 ± 2.85%, range = 0–17.50%; Table S7)
by 0 using lapply() framework and is.na() function from the base package.32 This decision aligns with the biological context of our data,
as imputation could inadvertently introduce biases that do not reﬂect the inherent properties of non-voiced vocalizations. Subse-
quently, to account for species-speciﬁc variations in the acoustic feature-derived variables, we normalized them by species based
on z-scaling, addressing inﬁnite values and applying natural log-transformation to positive, non-zero numeric variables to reduce
skew and enhance comparability using the log() and scale() function from the base package.32 This ensured that our dataset met
the required assumptions for subsequent Uniform Manifold Approximation and Projection (UMAP) and eXtreme Gradient Boosting
(XGBoost) analysis. Finally, we addressed potential multicollinearity40 based on the Variance Inﬂation Factor (VIF) method. This
approach involved identifying and removing variables with a VIF superior to 5,41 and then recalculating the VIFs for all remaining vari-
ables by using the vif() function from the usdm package.42 This iterative process was repeated until all variables had VIFs below our
given threshold. This process led to retaining 17 (Table S2) out of the 33 acoustic feature-derived variables initially included after per-
forming recursive VIF.
Then, we performed a stratiﬁed train-test split (70/30) for each individual with createDataPartition() function from caret package,43
ensuring that calls from the same individual were uniquely assigned to either the training or testing sets in order to minimize bias due
to individual differences. This approach prevented the subsequent models from learning individual-speciﬁc acoustic variables
instead of those associated with emotional valence. The ﬁnal selection of the train-test split and sampling method was further opti-
mized based on the F1-score extracted from the XGBoost classiﬁer across species, as described in subsequent sections, ensuring
that the chosen split maximized the model’s performance in distinguishing emotional valence. Then, we oversampled the training set
to rebalance the number of calls to be equal between emotional valence and species based on synthetic minority oversampling
(SMOTE). SMOTE was chosen for its ability to synthetically balance the class distribution, thereby preserving the integrity of the orig-
inal dataset, mitigating model bias toward the majority class, reducing the risk of overﬁtting, and enhancing model generalization.
This method ensures a more equitable representation of all classes, which is crucial for the performance of our model in an imbal-
anced dataset scenario.44 Functions used during this process were recipe(), step_smotenc(), prep() and bake() from the themis45 and
recipes package.46 To ensure consistency, the same training set was used across all analyses, including UMAP, k-means clustering,
Naive Bayes classiﬁcation, and XGBoost models. The test set was used, where relevant, to evaluate model performance. All results
reported in this study are also based exclusively on the test set, hence avoiding data leakage from the training process.
Context, valence and species separation with UMAP
We relied on the Uniform Manifold Approximation and Projection (UMAP) algorithm to visualize the separability between the species
and the valence of call emission. UMAP is a non-linear dimensionality reduction algorithm that seeks to build a uniform representation
of the data based on combinatorial structures. It uses Fuzzy K-nearest neighbors distances and spectral embedding to preserve the
local and global integrity of the data.21 Compared to other widely used dimensionality reduction techniques, such as t-distributed
Stochastic Neighbor Embedding (t-SNE), UMAP is a stochastic algorithm that exhibits a stronger emphasis on the global structure
of the data to make inter-cluster relationships more meaningful. The distance metric in the UMAP analysis was Euclidean, the number
of dimensions was 2, the number of nearest neighbors was 30, and the effective minimum distance between embedded points was
0.001. To perform the UMAP, we used the step_umap() function from embed package47 to project the variables based on unsuper-
vised learning and ggplot() function from ggplot2 package48 to visualize the species and valence separability (Figure 1) between spe-
cies, and the valence separability within each species (Figure S1).
e2
iScience 28, 111834, February 21, 2025
iScience
Article
ll
OPEN ACCESS


## Page 12

Additionally, to quantitatively assess the separability of positive and negative calls, we applied k-means clustering to the UMAP
projections for each species using the kmeans() function from the stats package.32 K-means was used as an unsupervised method
to identify clusters based on the acoustic features, without using the true emotional valence labels. To evaluate the quality of the clus-
tering, we computed clustering purity, which measures the proportion of calls in each cluster that belong to the most frequent valence
category. Higher purity indicates better alignment between the clusters and the actual valence labels. In parallel, we applied a Naive
Bayes classiﬁer, where valence was the response variable and the ﬁrst and second UMAP dimensions were the predictors, using the
naiveBayes() function from the e1071 package.49 Unlike k-means, this is a supervised learning method, which we used to calculate
the classiﬁcation accuracy, by comparing the predicted valence with the actual valence labels. Both k-means clustering and Naive
Bayes training set were split using a group-based K-fold cross-validation approach based on the groupKFold() function from the
caret package,43 ensuring that calls from the same individual were assigned exclusively to either the training or test sets. This
approach minimized bias from individual differences and prevented models from learning individual-speciﬁc acoustic features,
focusing on valence-related patterns instead. Additionally, this cross-validation simulated scenarios where models were trained
on a subset of individuals and tested on entirely separate individuals within the same species, avoiding data leakage. Finally, we eval-
uated the statistical robustness of both clustering purity and classiﬁcation accuracy by calculating 95% conﬁdence intervals using
bootstrapping with 1000 iterations, with the quantile() function from the base package32 to account for variability. During bootstrap-
ping, we resampled the accuracies and purities from the cross-validation folds and calculated the average for each iteration, using
the mean values across folds as the ﬁnal estimate (Table S3).
Automated valence classiﬁcation with XGBoost
We aimed at evaluating the performance of a machine learning algorithm to discriminate the emotional valence (i.e., negative/
positive) of our vocalizations by training a XGBoost model. XGBoost takes advantage of parallel processing, tree-pruning, handling
missing values, and regularization to provide more accurate approximations that are less prone to overﬁtting. We chose this algo-
rithm for its efﬁciency to outperform most other supervised learning algorithms due to its speed and versatility to deal with a wide
range of tasks.50 To validate the generalizability of our model beyond the speciﬁc conditions of our dataset, we also employed a strat-
iﬁed group k-fold cross-validation approach with groupKFold() function from caret package.43 Each fold contained unique individ-
uals, preventing data leakage between training and testing set. Subsequently, we trained a binary classiﬁer using a 10-fold group
cross-validation method to determine the emotional valence of vocalizations from our multiple ungulate species under various con-
texts. This approach leveraged individual and species-speciﬁc identiﬁers to maintain distinct subsets of data in each fold, thus cir-
cumventing the model’s potential bias toward individual- or species-speciﬁc characteristics. Hyperparameters were tuned based on
grid search optimization technique, in order to test the effectiveness of our model,51 using expand.grid() function from the base pack-
age32 to create the grid with potential candidate values, and trainControl() as well as train() functions from caret package43 to estimate
optimal parameters. This step aimed at facilitating a gradual and more robust learning process, reducing the likelihood of overﬁtting.
We set the number of decision trees in the ﬁnal model to 500, the maximum depth of individual trees to 10 and the learning rate to 0.10
(Table S8). We evaluated model performance based on the trade-off between the true positive rate and the positive predictive value
from the Precision-Recall curve (PR-AUC). To provide valid and consistent indicators of emotional valence to be explored in future
studies, we used the decision-tree-based ensemble algorithm eXtreme Gradient Boosting (XGBoost) with xgboost() function from
xgboost package.52 Finally, we trained individual XGBoost classiﬁers for each species separately using the train() function from
the caret package,43 following the same methodology as described for the overall model, including cross-validation and hyperpara-
meter tuning, speciﬁc to each species. We then compared the 10 most important acoustic feature-derived variables across species
based on their gain, which reﬂects each feature’s contribution to improving model accuracy, using the xgb.importance() function from
the xgboost package52 (Table S5).
Model explanation with SHAP
After modeling the data, we assessed the importance of each acoustic variable and their respective effect on the model by selecting
the ten most important contributors based on SHapley Additive exPlanations (SHAP) with SHAPforxgboost package53 (Figure 2A).
SHAP is a method used to explain individual contributions to a particular model output across all possible combinations by consid-
ering the local accuracy of variable coalition, variable absence, and consistency to be scored with Shapley values. Model explanation
based on Shapley values provides a good alternative to information gain attributes in order to evaluate variable importance in driving
the predicted outcomes. In recent years, SHAP has become one of the most efﬁcient tools to make global interpretations more
consistent with local explanations and decipher the ‘‘black box’’ of any machine learning algorithm.25 In addition, we explored the
relationships between acoustic variables and their contributions to model predictions, as quantiﬁed by SHAP values. Instead of using
straight lines to represent these associations, we used the geom_smooth() function from the ggplot2 package48 to incorporate non-
linear trend lines and hence provide a better understanding of the acoustic variables inﬂuencing emotional valence classiﬁcation
(Figure 2B).
ADDITIONAL RESOURCES
No additional resources were created or further expanded as part of this study. Clinical registry numbers and links are not applicable
to this research.
iScience 28, 111834, February 21, 2025
e3
iScience
Article
ll
OPEN ACCESS


