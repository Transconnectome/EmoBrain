# (2026) Brain-aligning of semantic vectors improves neural decoding of visual stimuli

**Source:** (2026) Brain-aligning of semantic vectors improves neural decoding of visual stimuli.pdf

---

## Page 1

communications biology
Article
A Nature Portfolio journal
https://doi.org/10.1038/s42003-025-09482-x
Brain-aligning of semantic vectors
improves neural decoding of visual stimuli
Check for updates
Shirin Vafaei
1, Ryohei Fukuma
1,2, Takufumi Yanagisawa
1,2,3
, Huixiang Yang2, Satoru Oshino
1,3,
Naoki Tani
1,3, Hui Ming Khoo
1,3, Hidenori Sugano4, Yasushi Iimura4, Hiroharu Suzuki4,
Madoka Nakajima
4, Kentaro Tamura5,6 & Haruhiko Kishima
1
The development of algorithms to accurately decode neural information has long been a research focus in
the ﬁeld of neuroscience. Brain decoding typically involves training machine learning models to map
neural data onto a preestablished vector representation of stimulus features. These vectors are usually
derived from image- and/or text-based feature spaces. Nonetheless, the intrinsic characteristics of these
vectors might fundamentally differ from those that are encoded by the brain, limiting the ability of decoders
to accurately learn this mapping. To address this issue, we propose a framework, called brain-aligning of
semantic vectors, that ﬁne-tunes pretrained feature vectors to better align with the structure of neural
representations of visual stimuli in the brain. We trained this model with functional magnetic resonance
imaging (fMRI) and then performed zero-shot brain decoding on fMRI, magnetoencephalography (MEG),
and electrocorticography (ECoG) data. fMRI-based brain-aligned vectors improved decoding
performance across all three neuroimaging datasets when accuracy was determined by calculating the
correlation coefﬁcients between true and predicted vectors. Additionally, when decoding accuracy was
determined via stimulus identiﬁcation, this accuracy increased in speciﬁc category types; improvements
varied depending on the original vector space that was used for brain-alignment, and consistent
improvements were observed across all neuroimaging modalities.
The development of brain decoding algorithms is essential for advancing
brain–machine interfaces(BMIs)1–4 that enable precise communication and
motorcontrolforindividualswithspeechormotorimpairments.Moreover,
these algorithms offer a unique opportunity to explore the complexities and
fundamental mechanisms underlying information processing in the human
brain5–10. Furthermore, accurate decoding can improve the effectiveness of
neurofeedback systems by enabling the decoding of cognitive patterns and
delivering real-time neurofeedback, thereby assisting patients in the
reﬁnement of their cognitive and emotional faculties11–14.
Previous studies have shown that neural activity patterns can be
decoded to reveal information about perceived or imagined visual stimuli
(i.e., images). This information can take the form of semantic
attributes10,15–18, category-level classes5,7,15,19,20, or even reconstructed visual
representations of the images21–24. Decoding typically involves representing
a speciﬁed attribute as a pretrained feature vector, often derived from object
recognition neural networks15, multimodal models25,26, or word co-
occurrence statistics12,27–29. Then, machine learning models are trained to
map neural activity patterns to these feature vectors.
While pretrained feature vectors have enabled brain decoding with
above-chance accuracy, current models are still limited in accurately
learning this mapping, particularly in zero-shot decoding scenarios, where
decoders must generalize the learned information to novel semantic cate-
gories not encountered during training30. Given the impracticality of
training decoders to learn the representations of all possible semantic
categories, developing more robust and ﬂexible decoding models has
become imperative.
In this study, we hypothesized that if the vectors that are used to
represent stimuli are more aligned with how visual stimuli are encoded in
the human brain, decoders can better learn the mapping of neural activity
patterns to feature vectors and even generalize this mapping to novel
semantic categories using learned information encapsulated within the
more brain-aligned vectors.
1Department of Neurosurgery, Graduate School of Medicine, The University of Osaka, Suita, Japan. 2Department of Neuroinformatics, The University of Osaka
Graduate School of Medicine, Suita, Japan. 3Epilepsy Center, The University of Osaka Hospital, Suita, Japan. 4Department of Neurosurgery, Juntendo University,
Tokyo, Japan. 5Department of Neurosurgery, Nara Medical University, Kashihara, Japan. 6Department of Neurosurgery, National Hospital Organization, Nara
Medical Center, Nara, Japan.
e-mail: tyanagisawa@nsurg.med.osaka-u.ac.jp
Communications Biology |  (2026) 9:206 
1
1234567890():,;
1234567890():,;


## Page 2

This idea was inspired by recent ﬁndings that the use of brain-like or
brain-integrated features can improve object recognition31, few-shot
learning and anomaly detection tasks32, and that consistent and high-
performing latent spaces can be obtained by jointly learning from both
behavioral and neural data33. However, whether semantic spaces with
representations that are more aligned with neural encoding patterns can
lead to more accurate zero-shot brain decoding remains unclear.
To create a brain-aligned semantic vector representation of stimuli, we
propose a framework called brain-aligning of semantic vectors, which
reconstructs the pretrained feature vectors while ensuring that the second-
order statistical features of its latent space are as similar as possible to those
ofbrainactivitypatterns.Thevectorsthatareextractedfromthelatentspace
of the autoencoder after training are called brain-aligned semantic vectors.
We investigated whether utilizing these brain-aligned semantic vectors can
improvezero-shotdecodingaccuracytoidentifythepredictedvectorfroma
set of candidate vectors15,34 for (1) brain activity measured by the same
neuroimaging technique used to ﬁne-tune the pretrained feature spacesand
(2) brain activity measured by a different neuroimaging technique than that
used for ﬁne-tuning.
Speciﬁcally, we trained the brain-aligning framework by leveraging
brain activity patterns measured by functional magnetic resonance imaging
(fMRI) and then tested the zero-shot decoding performance of the resulting
brain-aligned vectors on brain activity data measured by fMRI, magne-
toencephalography (MEG), and electrocorticography (ECoG). This cross-
modality approach is critical because fMRI, MEG, and ECoG measure
distinct aspects of brain activity: fMRI captures hemodynamic changes
(BOLD signals)35, ECoG records electrical activity36, and MEG detects
magnetic ﬁelds37. Successful generalization across modalities would suggest
that our vectors represent fundamental aspects of neural coding that are
independent of speciﬁc measurement techniques.
Results
Brain-aligning of semantic vectors
We developed a multimodal learning autoencoder framework that takes
pretrained feature vectors and the brain activity patterns corresponding to
the visual stimuli dataset and aligns the feature space with the structure of
visual representations in the human brain. To select the pretrained feature
vectors, we used two different feature spaces. The ﬁrst is an image-based
featurespacethatincludesfeaturesfromtheimageencodermodelofCLIP26,
and the second is a text-based feature space that includes features from the
global vectors for word representation (GloVe) model29. The fMRI dataset
thatwasusedheretoﬁne-tunethepretrainedfeaturevectorswasthegeneric
object decoding (GOD) dataset15. This dataset contains fMRI recordings
from 5 subjects viewing 1200 images of 200 distinct object categories that
were selected from ImageNet38. The GOD dataset has been speciﬁcally
designedtopreventanyoverlapbetweenthecategoriesusedfortrainingand
those used for testing, facilitating assessment of the zero-shot prediction
capabilities of decoding models. Importantly, the use of this dataset ensures
that these models are evaluated on the basis of their ability to generalize to
entirely new categories without prior exposure.
First, we extracted the original feature vectors for each category in the
GOD dataset (see Methods) and represented each category by its corre-
sponding feature vector. To obtain the brain-aligned semantic space, we
trained the autoencoder with a two-term objective function. The ﬁrst term is a
simple mean squared error (MSE) loss between true and predicted pretrained
feature vectors (with the goal of reconstructing them). The second term is the
MSE loss between the representational similarity matrix (RSM)39 of the fMRI
signals and the autoencoder’s latent space in each batch. Mathematically:
loss ¼ 1
m
X
m
i¼1
ðαÞ y  y0

2 þ 1  α
ð
Þ RSMl  RSMb

2
h
i
ð1Þ
y is the original semantic vector, y' is the reconstructed semantic vector,
RSMl is the RSM of the autoencoder’s hidden layer, RSMb is the RSM of
the corresponding brain activity patterns, and m is the number of
samples in each batch. Finally, α is the hyperparameter that determines
the extent of brain alignment.
Given our aim to decode visual object categories, we used the fMRI data
from different brain regions of interest (ROIs) in the visual cortex (lower
visual areas (V1–V4), the lateral occipital complex (LOC)40, the fusiform face
area (FFA)41, and the parahippocampal place area (PPA)42; see the Methods
section for the deﬁnition of the ROIs). Concurrently, to choose the appro-
priate pretrained feature vectors, we extracted the category-speciﬁc pretrained
feature vectors of each category in the training data of the GOD dataset.
For each combination of ROIs, participants in the GOD dataset, pre-
trained feature vectors, and α values, we trained a different autoencoder
using a leave-one-subject-out procedure. Speciﬁcally, when creating brain-
aligned vectors for decoding a particular subject (e.g., Subject A), the auto-
encoder was trained using (1) the pretrained semantic vectors of all training
categories from the GOD dataset, and (2) the averaged RSMs computed
from the other 4 subjects’ fMRI brain signals for these same training cate-
gories. This leave-one-subject-out approach ensures that the brain-aligned
semantic space is not inﬂuenced by Subject A’s idiosyncratic neural response
patterns, thereby preventing information leakage and ensuring that the
semantic space captures generalizable neural structure across individuals.
We trained autoencoders on a wide range of values ofα (α = 0.0001, 0.001,
0.01, 0.1, and 1). We speciﬁcally included 1 as one of the values to determine
how excluding the brain-aligning part from this framework would affect the
downstream analyses. Figure 1 shows an overview of the proposed workﬂow.
fMRI brain decoding of visual stimuli
We performed brain decoding for each ROI, feature space type, and par-
ticipant separately. For each subject (e.g., Subject A), linear regression
decoders were trained to map that subject’s brain activity patterns from the
training categories to their corresponding brain-aligned semantic vectors
(whichwerecreatedwithoutusingSubjectA’sdata,asdescribedabove).The
traineddecoderswerethenevaluatedonSubjectA’sbrainactivityforthetest
categories, enabling zero-shot generalization to novel semantic categories
not encountered during decoder training. Importantly, for each ROI (e.g.,
V4), both the autoencoder and decoder were trained and tested exclusively
on the voxel activity from that same ROI, using the brain-aligned vectors
derivedfromthatROI’sautoencoder.Acrossallsamplesandforeachunitin
the semantic vectors, a separate set of linear regression models was trained.
We evaluated the identiﬁcation accuracies of the models to assess their
ability to correctly classify stimuli on the basis of the predicted feature
vectors. This evaluation is critical for determining the practical utility of
decoding models used in real-world applications, such as brain-machine
interfaces or neurofeedback systems6,34. For this purpose, we computed the
Pearson correlation coefﬁcient between the predicted semantic vector and
all the other candidate vectors. The accuracy is deﬁned as the percentage of
candidate categories whose correlation with the predicted vector is lower
than the correlation between the true and predicted vectors. The ﬁnal
identiﬁcation accuracy is determined by averaging the identiﬁcation
accuracies across all categories and subjects in the test dataset. Figure 2
shows an overview of the brain identiﬁcation algorithm.
Weﬁrstevaluatedtheperformanceofcategoryidentiﬁcationrelativeto
chance. Speciﬁcally, we compared the identiﬁcation results obtained from
the original data with those obtained from shufﬂed data. The shufﬂed
accuracy was obtained by correlating the predicted vectors with both the
shufﬂed true vector and all the other candidate vectors. The shufﬂed iden-
tiﬁcation accuracy was then deﬁned as the percentage of candidate cate-
gories whose correlation with the predicted vector was lower than the
correlation between the shufﬂed true and predicted vectors. The real
identiﬁcation accuracies were signiﬁcantly greater than the corresponding
shufﬂed accuracies for 42/42 of the CLIP perception data, 35/42 of the CLIP
imagery, 42/42 of the GloVe perception, and 42/42 of the GloVe imagery
(one-sidedt-test,p < 0.05,seeSupplementary Data 1–4for the exact values).
The identiﬁcation results revealed that brain-aligned semantic vectors
can enhance zero-shot visual stimulus identiﬁcation across the visual cortical
hierarchy. The higher-order visual areas, particularly V4, LOC, FFA, and
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
2


## Page 3

PPA, consistently outperformed the early visual areas (V1, V2, V3) in terms
of the identiﬁcation accuracy, reﬂecting their specialized role in object
recognition and semantic processing (Fig. 3; see Supplementary Fig. 1,
Supplementary
Notes,
Supplementary
Figs. 14–16,
Supplementary
Figs. 21–22, Supplementary Data 5–32, and Supplementary Data 41–48 for
the comprehensive statistical results and individual subject data). Impor-
tantly, the optimal degree of brain alignment varied depending on the
semantic feature space used. For the CLIP-based vectors, moderate
brain alignment (α = 0.1) yielded the best identiﬁcation performance,
whereas the GloVe-based vectors beneﬁted most from slightly stronger
alignment (α = 0.01). Both feature types showed peak performance when
aligned with V4 neural activity patterns, which is consistent with the
demonstrated specialization of V4 for object-like shape processing43,44. The
identiﬁcation accuracies remained robust across both the perception and the
imagery conditions, although the performance of the imagery condition was
slightly lower overall. These ﬁndings demonstrate that there exists an opti-
mal balance for brain alignment—neither too weak nor too strong—that
maximizes the model’s ability to correctly identify visual stimuli in zero-shot
scenarios and that this optimal alignment is best captured by intermediate
visual areas that balance perceptual detail with semantic abstraction.
Generalization of the decoding performance to other modalities:
MEG and ECoG datasets
To assess the generalizability of using the fMRI-derived brain-aligned vec-
tors to decode other types of neuroimaging brain data, we performed
decoding analysis on MEG and ECoG neural data from different partici-
pants who were exposed to the same visual stimuli.
Wetrainedseparatelinearregressionmodelsasbraindecodersforeach
of the MEG and ECoG datasets, subjects, and feature space types. The
decoders used brain-aligned vectors that were derived from fMRI V4 data
(which showed optimal performance in the fMRI experiments). For MEG,
the decoders were trained on source-estimated signals from the ventral
visual stream regions; for ECoG, the decoders were trained on high-γ power
from subdural electrodes covering the ventral visual cortex.
Figure 4 shows the identiﬁcation results of the MEG neural data using
the fMRI brain-aligned vectors obtained from the V4 brain region. We ﬁrst
evaluated whether the MEG neural data could be successfully decoded using
the original and fMRI-derived brain-aligned vectors from the V4 region by
comparing identiﬁcation accuracies against shufﬂed data using one-sided t-
tests. For the CLIP-based vectors, all conditions achieved signiﬁcantly above-
chance performance (p < 0.001, one-sided t-test, Fig. 4a, see Supplementary
Data 33 for the exact values). In contrast, for the GloVe-based vectors, the
original vectors failed to achieve above-chance performance (p = 0.446),
whereas brain-aligned vectors consistently exceeded chance levels (p < 0.001,
see Supplementary Data 34 for the exact values). These results demonstrate
that brain alignment transforms originally ineffective GloVe vectors into
successful decoders for MEG data, highlighting the importance of aligning
semantic representations with brain activity patterns for cross-modal gen-
eralization. Next, we examined differences in identiﬁcation accuracy between
the original, vectors with α = 1, and the optimal brain-aligned vectors from
the fMRI results. The MEG identiﬁcation results demonstrate that the brain-
aligned semantic vectors derived from the fMRI data effectively transfer to a
different neuroimaging modality. For the CLIP-based vectors, the optimal
brain-aligned condition (α = 0.1) substantially outperformed both the ori-
ginal pretrained vectors and the reconstruction-only condition (α = 1). With
respect to the GloVe-based vectors, compared with the original vectors, both
the reconstruction-only (α = 1) and the brain-aligned conditions (α = 0.01)
resulted in enhanced performance, with the brain-aligned conditions
achieving higher identiﬁcation accuracies. Importantly, the brain-alignment
parameters that proved optimal in the original fMRI training (α = 0.1 for
CLIP and α = 0.01 for GloVe) maintained their superior performance when
applied to MEG data. For the comprehensive statistical results and subject-
by-subject results, see Supplementary Figs. 2–3, Supplementary Figs. 17–18,
Supplementary Data 35–36 and Supplementary Data 49–52.
Similarly, we ﬁrst evaluated whether ECoG neural data could be suc-
cessfully decodled using the original and fMRI-derived brain-aligned vec-
tors from the V4 region by comparing identiﬁcation accuracies against
shufﬂed data. For the CLIP-based vectors, brain-aligned conditions with
α = 1 and α = 0.1 achieved signiﬁcantly above-chance performance
(p = 0.0029 and p < 0.001, respectively, one-sided t-test, Fig. 5a, see Sup-
plementary Data 37 for the exact values), whereas the original vectors failed
to reach signiﬁcance (p = 0.9991). For the GloVe-based vectors, all the
Fig. 1 | Examples of the visual stimuli and workﬂow of the brain-aligning fra-
mework. a Sample images from the GOD dataset. The rectangles represent the
sample image batches used for training. b Brain-aligning framework. First,
pretrained visual or textual features are extracted. Then, an autoencoder is trained to
reconstruct these features while aligning the representational similarity matrix
(RSM) of its latent space with the RSM of corresponding brain activity patterns.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
3


## Page 4

conditions achieved signiﬁcantly above-chance performance: original vec-
tors (p = 0.0007), α = 1 vectors (p < 0.001), and α = 0.01 vectors (p < 0.001,
Fig. 5b, see Supplementary Data 38 for the exact values).
Next, we examined differences in identiﬁcation accuracy between
the original vectors, vectors with α = 1, and the optimal brain-aligned vec-
tors identiﬁed from the fMRI results. The ECoG identiﬁcation results
demonstrate that the brain-aligned semantic vectors derived from the fMRI
data effectively transfer to invasive neural recordings. For the CLIP-based
vectors, the optimal brain-aligned condition (α = 0.1) substantially out-
performed both the original pretrained vectors and the reconstruction-only
condition (α = 1). With respect to the GloVe-based vectors, the perfor-
mance of the brain-aligned condition (α = 0.01) was better than that of the
original vectors. While the group-level analysis revealed comparable per-
formance between the brain-aligned vectors with α = 0.01 and the vectors
with α = 1, the individual subject analysis revealed that 3 out of 4 subjects
achieved higher identiﬁcation accuracy with α = 0.01 than with α = 1.
Importantly, the brain-alignment parameters that proved optimal in the
originalfMRItraining(α = 0.1forCLIPandα = 0.01forGloVe)maintained
their superior performance when applied to the ECoG data. These ﬁndings
highlight the robust cross-modal transferability of brain-aligned semantic
representations across different neuroimaging modalities (see Supplemen-
tary Figs. 4–5, Supplementary Figs. 19–20, Supplementary Data 39–40, and
Supplementary Data 53–56 for the subject-by-subject results).
Consistency of the identiﬁcation accuracy improvement among
neuroimaging modalities
We investigated whether brain alignment produced category-speciﬁc
changes in the identiﬁcation accuracy and tested whether these changes
were consistent across neuroimaging modalities. We ﬁrst clustered the
categories in ImageNet into 10 clusters in both the original CLIP and GloVe
space separately (see Supplementary Figs. 6–7 for the clustering results and
procedures). For each optimal α in each neuroimaging modality, original
semantic space (all derived from fMRI V4), and category, we calculated the
difference in the identiﬁcation accuracy between the aligned vectors and the
original vectors. Figure 6 shows the improvement and visualization of the
categories in the clusters for CLIP, and Fig. 7 shows the improvement and
visualizationofthecategoriesintheclustersforGloVe.Thebrain-alignment
effects varied by category type: the CLIP vectors showed greater improve-
ments for artifacts and object categories (e.g., vehicles, tools), whereas the
GloVe vectors demonstrated preferential enhancement for biological cate-
gories (e.g., animals), indicating that visual-semantic and text-based
representations align differently with brain activity patterns across seman-
tic domains (see Supplementary Figs. 8–13).
Comparison of category discriminability between the original
and brain-aligned CLIP features
To investigate whether brain alignment affects the intrinsic categorical
structure of semantic representations, we analyzed the category discrimin-
ability of individual feature units, deﬁned as the F statistic measuring the ratio
of intercategory to intracategory variation in the feature values15. Since the
GloVe vectors are identical for all images within a category, this analysis was
restricted to the CLIP-based feature vectors. We computed discriminability
metrics for each of the feature units across 19,933 ImageNet categories, with 8
images per category, and compared the original CLIP vectors against the
brain-aligned variants that were trained on the fMRI V4 neural patterns with
different alignment strengths. A direct paired statistical comparison between
the original (512-dimensional) and brain-aligned (256-dimensional) features
was not feasible because of unequal numbers of feature units for the Wilcoxon
signed-rank test. Instead, we compared the brain-aligned conditions (α ≤0.1)
against the α = 1 baseline, which represents autoencoder-compressed features
without neural constraints. All the brain-aligned conditions signiﬁcantly
outperformed this baseline (all p < 0.005, Wilcoxon signed-rank test, Fig. 8),
indicating that neural constraints improve feature representations beyond the
effects of dimensionality reduction.
Discussion
Here, we demonstrated the ability of our proposed brain-aligning method to
enhance zero-shot brain decoding across diverse neuroimaging datasets and
distinct individuals. Notably, the fMRI brain decoders that were trained on the
CLIP-based
and
GloVe-based
brain-aligned
feature
vectors
outperformed those that were trained on the original pretrained vectors
(Fig. 3). Importantly, this improvement was observed even when other types of
neuroimaging neural data (MEG and ECoG), subjects, and stimulus categories
Visual stimuli
Imagery
Perception
Pearson
correlation
Pearson correlations
True feature vectors
Candidate
categories for
identification
...
...
...
Brain activity patterns
Predicted feature vector
True feature vector
Decoder
0.07
0.13
*
0.73
Fig. 2 | Brain decoding and stimulus identiﬁcation procedure. Brain decoders are
trained to map neural activity patterns from visual stimuli (perception or imagery) to
their corresponding semantic feature vectors. For stimulus identiﬁcation, the pre-
dicted semantic vector is compared against a large set of candidate stimulus
categories using Pearson correlation coefﬁcients. The stimulus with the highest
correlation to the predicted vector is identiﬁed as the decoded stimulus. The iden-
tiﬁcation accuracy is calculated as the percentage of candidate categories with lower
correlations than the true target stimulus.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
4


## Page 5

that were not included in training the brain-aligning model were considered
(Figs. 4 and 5), highlighting the generalizability of our approach.
Previous studies have attempted to develop a brain-based semantic
representation space. For example, Binder et al.45. proposed a model in
which word meanings are represented as combinations of basic sensory,
motor, affective, and cognitive experiences. These authors introduced
a basic set of approximately 65 experiential attributes on the basis of
neurobiological considerations—spanning sensory, motor, spatial, tem-
poral, affective, social, and cognitive domains—and collected normative
data on these experiential attributes to create a semantic space based
on brain activity. In another study, Chersoni et al.46. advanced this
concept by demonstrating the decoding of word embeddings using
brain-based semantic features proposed by Binder et al. However, while
Binder et al. established a foundation for linking brain activity to semantic
representations, their approach relied on manually-deﬁned attributes
rather than directly using the raw neural data. In contrast, our approach
harnesses the inherent structure of neural representations by directly using
the second-order statistical characteristics of brain activity patterns,
avoiding the need to manually deﬁne attributes. This data-driven approach
may offer a more direct and potentially comprehensive representation of
neural semantic space.
In addition to creating brain-based semantic spaces, as exempliﬁed by
Binder et al., several studies have ﬁne-tuned neural representations with
human, monkey or rat brain data to enhance performance on downstream
Original
= 1
= 0.1
= 0.01
= 0.001
= 0.0001
PPA
FFA
LOC
V4
V3
V2
V1
ROIs
0.621
0.662
0.681
0.647
0.650
0.638
0.628
0.666
0.696
0.661
0.646
0.647
0.631
0.694
0.698
0.691
0.633
0.650
0.650
0.700
0.737
0.708
0.684
0.696
0.623
0.660
0.661
0.664
0.634
0.645
0.588
0.604
0.611
0.611
0.588
0.614
0.583
0.584
0.595
0.589
0.583
0.593
Perception (CLIP)
Original
= 1
= 0.1
= 0.01
= 0.001
= 0.0001
0.609
0.610
0.611
0.577
0.605
0.609
0.616
0.613
0.616
0.609
0.589
0.615
0.610
0.595
0.587
0.602
0.562
0.562
0.616
0.604
0.627
0.619
0.599
0.607
0.582
0.575
0.587
0.580
0.571
0.580
0.555
0.545
0.525
0.581
0.531
0.572
0.564
0.548
0.536
0.533
0.514
0.577
Imagery (CLIP)
Original
= 1
= 0.1
= 0.01
= 0.001
= 0.0001
Alpha values
PPA
FFA
LOC
V4
V3
V2
V1
ROIs
0.709
0.726
0.729
0.721
0.739
0.699
0.726
0.758
0.750
0.747
0.734
0.700
0.725
0.742
0.744
0.746
0.736
0.714
0.739
0.766
0.764
0.785
0.760
0.721
0.717
0.732
0.750
0.761
0.743
0.707
0.685
0.695
0.685
0.700
0.685
0.665
0.677
0.672
0.694
0.680
0.690
0.640
Perception (GloVe)
Original
= 1
= 0.1
= 0.01
= 0.001
= 0.0001
Alpha values
Alpha values
Alpha values
0.693
0.691
0.694
0.692
0.703
0.672
0.712
0.700
0.699
0.721
0.710
0.681
0.700
0.669
0.683
0.698
0.703
0.679
0.709
0.700
0.705
0.730
0.711
0.671
0.671
0.670
0.678
0.682
0.676
0.667
0.678
0.667
0.654
0.646
0.646
0.670
0.669
0.632
0.645
0.654
0.673
0.640
Imagery (GloVe)
0.50
0.55
0.60
0.65
0.70
0.75
Identification accuracy
0.625
0.650
0.675
0.700
0.725
0.750
0.775
0.800
Identification accuracy
a
b
Fig. 3 | fMRI identiﬁcation accuracy patterns using brain-aligned semantic
vectors across visual cortex regions and alignment parameters. Heatmapsshowing
zero-shot identiﬁcation accuracy for visual stimulus decoding using brain-aligned
semantic vectors derived from different regions of interest (ROIs) in the visual cortex.
TheresultsareshownforaCLIP-basedandbGloVe-basedsemanticvectorsunderboth
perception and imagery conditions. The rows represent different visual cortex ROIs
(V1–V4: primary and secondary visual areas; LOC lateral occipital complex, FFA
fusiform face area, PPA parahippocampal place area). The columns represent different
brain-alignment parameters (α), where “Original” indicates unaligned pretrained vec-
tors, α = 1 indicates reconstruction without brain alignment, and decreasing α values
(0.1–0.0001) indicate increasing degrees of brain alignment. The color intensity reﬂects
identiﬁcation accuracy, with warmer colors indicating better performance. The optimal
brain-alignment parameters varied by semantic vector type and brain region, with V4-
derived brain-aligned vectors showing particularly strong performance for both CLIP
(α = 0.1) and GloVe (α = 0.01) across perception and imagery conditions. n = 5 subjects
from the GOD dataset.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
5


## Page 6

tasks. For example, Federer et al.31. reported that training neural networks to
mimic the statistical properties of brain activity can improve object recog-
nition. Later, Li et al.47. integrated deep neural network features with brain
network information to enhance the prediction of brain activity during
naturalistic perception. Additionally, Muttenthaler et al.32. explored aligning
neural network representations with human similarity judgments to improve
few-shot learning and anomaly detection. Finally, Schneider et al.33. demon-
strated the power of combining behavioral and neural data through latent
embeddings for predicting behavior. However, despite these advancements,
these previous studies did not explicitly explore the ﬁne-tuning of pretrained
feature vectors to directly match the second-order statistical representations of
human brain activity, nor did they systematically investigate the resulting
zero-shot decoding performance on new subjects and neuroimaging mod-
alities. Our brain-aligning method addresses this gap by aligning feature
vector relationships with those observed in neural responses, demonstrating
robust cross-modality and cross-subject decoding capabilities.
Our ﬁndings are also aligned with the broader literature addressing
hyperalignment48 and the need to discover shared neural representational
spaces across individuals. While our primary goal was not to derive a
common high-dimensional space per se, our results nevertheless suggest
some degree of alignment across individuals. By creating brain-aligned
vectors on the basis of averaged representational similarity matrices (RSMs)
across subjects, we effectively leveraged the neural representations that
are common across individuals. The subsequent successful decoding of
neural activity patterns from a different set of subjects aligns with previous
ﬁndings, such as those of Guntupalli et al.49. who demonstrated the
feasibility of ﬁnding such shared spaces even at a ﬁne-grained, searchlight
level. Furthermore, our results build upon the notion of shared
representations across neuroimaging modalities39,50,51, which is consistent
with ﬁndings from studies such as Haxby et al.48. that suggest the existence
of common representational structures in fMRI data. Notably, in our
study, the successful decoding of MEG signals and even ECoG signals
via our fMRI-derived brain-aligned vectors provides evidence for a
shared representational space with consistent second-order statistical
characteristics across these distinct modalities.
In conclusion, our study demonstrates the notable potential of brain-
aligning semantic vectors in increasing the accuracy and generalizability of
neural decoding algorithms. By integrating brain-related information into
pretrained feature vectors, we improved zero-shot decoding performance
across different individuals and neuroimaging modalities, even with a rela-
tively small fMRI dataset (consisting of approximately 150 categories). This
suggests that our approach efﬁciently captures essential neural representations
Original
= 1
= 0.1
Alpha value
a
b
40
60
80
Identification accuracy (%)
Original
= 1
= 0.01
Alpha value
40
60
80
Identification accuracy (%)
Fig. 5 | Cross-modal generalization: ECoG identiﬁcation accuracy patterns using
the fMRI-derived brain-aligned semantic vectors. Violin plots showing zero-shot
identiﬁcation accuracy for visual stimulus decoding in ECoG data using brain-aligned
semantic vectors derived from the fMRI V4 region. a CLIP-based and b GloVe-based
semantic vectors with optimal α parameters determined from the fMRI results. The
individual data points from 4 subjects (E1–E4) are overlaid on violin plots. The white
circles indicate shufﬂed control data, demonstrating chance-level performance.
Original
= 1
= 0.1
Alpha value
40
60
80
Identification accuracy (%)
Original
= 1
= 0.01
Alpha value
a
CLIP
GloVe
b
40
60
80
Identification accuracy (%)
Fig. 4 | Cross-modal generalization: MEG identiﬁcation accuracy using the
fMRI-derived brain-aligned semantic vectors. Violin plots showing zero-shot
identiﬁcation accuracy for visual stimulus decoding in MEG data using brain-aligned
semantic vectors derived from the fMRI V4 region. a CLIP-based and b GloVe-based
semantic vectors with optimal α parameters determined from the fMRI results. The
individual data points from 3 subjects are overlaid on violin plots. The white circles
indicate shufﬂed control data, demonstrating chance-level performance.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
6


## Page 7

even with limited training data. While these results are promising, future
exploration of several issues is needed. For example, investigating the impact
of different autoencoder architectures and loss metrics, as well as leveraging
larger datasets, could further optimize the effectiveness of brain-aligning
vectors. Additionally, developing methods to mitigate potential biases in the
brain-aligning process and enhance the interpretability of the resulting vectors
would facilitate real-world applications. In addition to these immediate
reﬁnements, future work could explore the application of brain-aligning to a
broader range of cognitive domains and tasks, ultimately paving the way for
more powerful and versatile brain-machine interface technologies.
Methods
Creating semantic vectors
Semantic vectors are multidimensional representations of data that encode
the underlying semantics, relationships, and context within that data. These
vectors have been widely used to decode meaningful representations of
stimuli in the brain; thus, decoders are trained to map neural activity pat-
terns to corresponding semantic vector representations. Here, we used two
different types of semantic spaces that have been previously used in brain
decodingstudies.Speciﬁcally,weusepretrained featurevectorsfromthe last
layer of the CLIP image encoder and pretrained feature vectors from the
GloVe model. We created semantic vectors for all categories in the Ima-
geNet dataset (fall 2011 release)38.
GloVe. GloVe is a method that generates 300-dimensional semantic
vector representations of words based on normalized word co-
occurrence statistics obtained from a corpus containing more than 42
billion tokens. Words with similar meanings are associated with vectors
that are close in the vector space, enabling GloVe to capture the semantic
meaning of words and their contextual associations. Here, we used the
pretrained word vectors of the 42B token ﬁle (https://nlp.stanford.edu/
data/glove.42B.300d.zip). For each image category in the ImageNet
dataset, we used their crowdsourced annotations38 and calculated the
average GloVe representations of all available annotations in the GloVe
dictionary as a representation of that category. If any of the annotations of
a particular category did not exist in the GloVe dictionary, that category
was excluded from all subsequent analyses.
CLIP. CLIP is a model that connects vision and language by encoding
semantic vectors for both images and text. The unique advantage of using
CLIP lies in its ability to map images and textual descriptions into a
shared vector space, where the similarity or dissimilarity between vectors
accurately reﬂects the semantic relationships between the two modalities.
To create a CLIP semantic vector for each category in ImageNet, we
extracted an image from each category and then extracted the features
from the ViT-B/32 transformer image encoder of the CLIP model for
that image.
fMRI dataset
Dataset description. We used the publicly available “Generic Object
Decoding” dataset15. Five healthy subjects (one female and four males,
aged between 23 and 38 years) with normal or corrected-to-normal
vision participated in the experiments. The sample size was chosen to
match previous fMRI studies with comparable research objectives. The
experiments consisted of presenting natural object images to the subjects
and recording their brain activity while they viewed the visual stimuli
goat
camel
leopard
minaret
bulldozer
grand_piano
stained-glass
domestic_llama
airliner
barrow
canoe
cannon
gravestone
mailbox
snowmobile
sack
welder's_mask
covered_wagon
football_helmet
beer_mug
sock
coffin
planchet
washer
shredder
microwave
videocassette_recorder
fire_extinguisher
tweezer
iPod
knob
owl
duck
bat
umbrella
cowboy_hat
tambourine
mandolin
dress_hat
harp
electric_guitar
bowls
goldfish
butterfly
swan
housefly
crab
common_iguana
killer_whale
conch
Categories (grouped by cluster)
0.5
0.0
0.5
Accuracy improvement
C0
C1
C3
C4
C5
C6
C7
C8
fMRI (n=50)
MEG (n=50)
ECoG(n=50)
fMRI
MEG
ECoG
fMRI
MEG
ECoG
1.000
0.926 1.000
0.928 0.941 1.000
Original
fMRI
MEG
ECoG
fMRI
MEG
ECoG
1.000
0.532 1.000
0.653 0.610 1.000
Improvement
fMRI
MEG
ECoG
fMRI
MEG
ECoG
1.000
0.439 1.000
0.513 0.460 1.000
Final
0.0
0.5
1.0
Pearson r
a
b
Fig. 6 | Consistency of identiﬁcation accuracy improvement between the optimal
CLIP-based brain-aligned vectors and original CLIP-based vectors across all
three modalities. a Category-speciﬁc accuracy improvements following brain
alignment of CLIP vectors across the fMRI (blue circles), MEG (red squares), and
ECoG (green triangles) modalities. The brain-aligned vectors were trained on the
fMRI V4 region data, with the optimal α parameters determined from the fMRI V4
region identiﬁcation analysis and applied across allthe modalities. The categories are
grouped by semantic clusters (C0–C8) derived from whole ImageNet clustering
analysis (Supplementary Fig. 6). Each modality tested the same n = 50 categories.
The y-axis shows the accuracy improvement relative to the original CLIP vectors.
The dotted vertical lines separate the cluster boundaries. The consistent patterns in
identiﬁcation accuracy improvements across modalities demonstrate robust cross-
modal generalization of V4 region brain-alignment beneﬁts. b Pearson correlation
matrices comparing the accuracy patterns across neuroimaging modalities for ori-
ginal performance (left), improvement (center), and ﬁnal performance (right). All
the results use brain-aligned vectors trained on fMRI V4 region data with optimal α
parameters derived from fMRI V4 region identiﬁcation analysis. The values indicate
correlation coefﬁcients between modality pairs. The high correlations in the accu-
racy improvement matrix (center) demonstrate that categories beneﬁting from V4
brain alignment in fMRI consistently beneﬁt across the MEG and ECoG modalities,
supporting the robustness and generalizability of the brain alignment approach.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
7


## Page 8

(perception experiment) or imagined them (imagery experiment). Ima-
ges were selected from the ImageNet dataset (2011, fall release). The
training dataset consisted of neural recordings of 1200 images (150
categories, 8 images per category), all of which were viewed by the par-
ticipants. The test dataset consisted of neural recordings of 50 seen and 50
imagined images (50 images were selected from 50 categories, i.e., 1 image
per category, and were not used in the training dataset; the training and
test images were presented 35 and 10 times, respectively).
All the subjects provided written informed consent, and the study
protocol was approved by the Ethics Committee of the ATR. All ethical
regulations relevant to human research participants were followed.
ROI identiﬁcation and selection. In the GOD dataset, the borders of
visual cortical areas were delineated using both retinotopic mapping and
functional localizer experiments. In the retinotopic mapping experiment,
subjects were presented with two types of stimuli: rotating wedges and
Fig. 8 | Brain alignment progressively enhances feature unit category dis-
criminability. Kernel density distributions of the F statistics measuring category
discriminability across feature units for the original CLIP features and brain-aligned
variants. Stronger brain alignment (smaller α) systematically shifts the distributions
rightward, indicating improved discriminability. The dashed vertical lines indicate
the mean F statistic for each condition.
Categories (grouped by cluster)
Accuracy improvement
fMRI (n=50)
MEG (n=50)
ECoG(n=50)
fMRI
MEG
ECoG
fMRI
MEG
ECoG
1.000
0.920 1.000
0.934 0.936 1.000
Original
fMRI
MEG
ECoG
fMRI
MEG
ECoG
1.000
0.314 1.000
0.548 0.470 1.000
Improvement
fMRI
MEG
ECoG
fMRI
MEG
ECoG
1.000
0.714 1.000
0.771 0.839 1.000
Final
0.0
0.5
1.0
Pearson r
domestic_llama
minaret
coffin
gravestone
sock
sack
cowboy_hat
washer
shredder
welder's_mask
dress_hat
planchet
stained-glass
leopard
goldfish
killer_whale
common_iguana
camel
goat
duck
tambourine
fire_extinguisher
bulldozer
mandolin
harp
tweezer
electric_guitar
grand_piano
barrow
videocassette_recorder
knob
microwave
iPod
canoe
airliner
covered_wagon
mailbox
football_helmet
bowls
cannon
snowmobile
conch
bat
beer_mug
umbrella
housefly
swan
butterfly
crab
owl
0.0
0.5
C0
C2
C3
C4
C5
C6
C7
C8
C9
a
b
Fig. 7 | Consistency of identiﬁcation accuracy improvement between the optimal
GloVe-based brain-aligned vectors and original GloVe-based vectors across all
three modalities. a Category-speciﬁc accuracy improvements following brain
alignment of GloVe vectors across the fMRI (blue circles), MEG (red squares), and
ECoG (green triangles) modalities. The brain-aligned vectors were trained on the
fMRI V4 region data, with the optimal α parameters determined from the fMRI V4
region identiﬁcation analysis and applied across allthe modalities. The categories are
grouped by semantic clusters (C0–C9) derived from whole ImageNet clustering
analysis (Supplementary Fig. 7). Each modality tested the same n = 50 categories.
The y-axis shows the accuracy improvements relative to the original GloVe vectors.
The dotted vertical lines separate the cluster boundaries. The consistent patterns in
identiﬁcation accuracy improvements across modalities demonstrate robust cross-
modal generalization of V4 region brain-alignment beneﬁts. b Pearson correlation
matrices comparing the accuracy patterns across neuroimaging modalities for ori-
ginal performance (left), improvement (center), and ﬁnal performance (right). All
the results use brain-aligned vectors trained on fMRI V4 region data with optimal α
parameters derived from fMRI V4 region identiﬁcation analysis. The values indicate
correlation coefﬁcients between modality pairs. The high correlations in the accu-
racy improvement matrix (center) demonstrate that categories beneﬁting from V4
brain alignment in fMRI consistently beneﬁt across the MEG and ECoG modalities,
supporting the robustness and generalizability of the brain alignment approach.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
8


## Page 9

expanding rings composed of ﬂickering checkerboards. The retinotopy
data were then transformed into Talairach space, and the boundaries of
visual areas V1–V4 were identiﬁed on ﬂattened cortical surfaces using
BrainVoyager QX software (http://brainvoyager.com)19,52. Higher-level
visual regions (lateral occipital complex, LOC; fusiform face area, FFA;
and parahippocampal place area, PPA) were identiﬁed through func-
tional localizer experiments in which subjects viewed both intact and
scrambled images of faces, objects, houses, and scenes40–42.
MEG dataset
Subjects. Three healthy subjects (male, aged between 25 and 34 years)
with normal or corrected-to-normal vision participated in the experiments.
All the participants were informed about the experiment’s purpose and
procedure and provided written informed consent. The study adhered to
the Declaration of Helsinki and was performed in accordance with proto-
cols approved by the Ethics Committee of Osaka University Clinical Trial
Center (Protocol No. 18472-5). All ethical regulations relevant to human
research participants were followed.
Visual images. Visual stimuli were drawn from the GOD dataset, which
comprises images collected from ImageNet (2011, fall release). The
dataset contains images from 200 distinct object categories. Images
underwent square cropping preprocessing according to methods
described in a previous study15 Due to copyright restrictions associated
with ImageNet, the images displayed in Figs. 1, 2, and Supplementary
Fig. 14 are not the original experimental stimuli. For display purposes, we
replaced them with visually similar images obtained from Unsplash
(https://unsplash.com/), a platform providing freely usable photographs
under the Unsplash license.
MRI acquisition. T1-weighted MRI data from each subject were col-
lected using a 3.0-Tesla SYNAPSE VINCENT scanner (Fujiﬁlm, Tokyo,
Japan) located at Osaka University’s hospital.
MEG acquisition. Prior to starting the MEG recordings, ﬁve marker coils
were attached to the subject’s face to determine the position and orien-
tation of the MEG sensors relative to the head, and the head position was
evaluated using these coils before and after each recording (maximum
acceptable displacement: 5 mm). To coregister the MEG data of each
subject with their corresponding MRI data, 100 points were digitized on
the scalp of each participant (FastSCAN Cobra; Polhemus, Colche-
ster, VT, USA).
TheMEGsignalswererecordedusinga160-channelwhole-headMEG
system equipped with coaxial-type gradiometers housed in a magnetically
shielded room (MEGvision NEO; Yokogawa Electric Corporation, Kana-
zawa, Japan). The subjects were placed in a supine position with their head
centered on the gantry. To minimize shoulder movement artifacts, a
cushion was positioned under the subject’s elbows. The subjects were
explicitly instructed to keep their head stationary to prevent motion
artifacts.
Visual stimuli were presented using a projection screen that was
located in front of the subject’s face (Presentation; Neurobehavioral Sys-
tems, Albany, CA, USA) and a liquid crystal projector (LVP-HC6800;
Mitsubishi Electric, Tokyo, Japan). The MEG signals were passed through
an optical isolation circuit and sampled at 1000 Hz with an online 200 Hz
low-pass ﬁlter using FPGA DAQ boards (PXI-7854R; National Instru-
ments, Austin, TX, USA).
Experimental design. For all the images in the GOD visual stimuli
dataset, we conducted an image presentation experiment. All the visual
stimuli were rear-projected onto a screen in the MEG scanner bore using
a luminance-calibrated liquid crystal display projector (LVP-HC6800;
Mitsubishi Electric, Tokyo, Japan). Data from each subject were collected
over multiple scanning sessions. On each experimental day, one session
was conducted for a maximum of 1 h. Each session included two types of
runs: “rest” runs (ﬁrst and last runs, not counted in the 5–7 run total) and
“main” runs. In the rest runs, the images were presented at 1 Hz (1 image/
sec) for approximately 1.5 min, followed by a ﬁxation period of
approximately 2 min. In the main runs, the images were presented at 2 Hz
(0.5 s intervals), with each run containing 870–871 images and lasting
approximately 9 min. Each image in both the training and test datasets
was presented six times. The presentation order of the categories was
randomized across runs.
MEG cortical current source estimation and preprocessing. The
raw MEG data were preprocessed using Brainstorm software53.
Environmental noise was ﬁrst reduced using a high-pass ﬁlter at 0.5 Hz
and a notch ﬁlter at 60 Hz and its harmonics. Independent component
analysis (ICA) was then applied to identify and remove cardiac
and ocular artifacts. The noise covariance matrix was computed from
baseline periods (−500–0 ms). For MEG-MRI coregistration, individual
cortical surface models were constructed from T1-weighted MRI
anatomical
images
using
FreeSurfer
software
(Martinos
Center
Software)54. Each subject’s three-dimensional facial surface was scanned
and aligned with the MRI-derived anatomical facial surface using 100
digitized scalp points (FastSCAN Cobra; Polhemus, Colchester, VT,
USA). For source estimation, 15,002 elementary current dipoles were
distributed across the cortical surface and oriented perpendicular to the
local cortical surface. The forward model was computed using an over-
lapping sphere head model ﬁtted to the individual cortex tessellation. The
inverse problem was then solved using minimum norm estimation, with
the source covariance matrix set to the identity matrix and the regular-
ization parameter λ = 0.1. The estimated source activities were projected
onto the FsAverage template for group analysis. Stimulus onset was
marked using analog triggers. All the processes were performed by using
Brainstorm.
MEG ROI identiﬁcation and selection. To extract data from each ROI
in our MEG recordings, we used the Human Connectome Project Multi-
Modal Parcellation 1.0 (HCP-MMP 1.0) atlas55. This atlas provides a
comprehensive parcellation of the cerebral cortex, dividing each hemi-
sphere into 180 distinct cortical areas (360 areas total). These areas are
further organized into 22 larger regions on the basis of anatomical and
topographical criteria. The regions consist of adjacent cortical areas that
can be viewed completely from one perspective, either on the inﬂated
cortical surface or through ﬂatmap visualization55. For our analyses, we
focused on the MEG signals extracted from regions within the ventral
visual cortex as deﬁned by the HCP-MMP1.0 parcellation.
ECoG dataset
Subjects. In this study, seventeen subjects with normal or corrected-to-
normal vision participated in the image presentation tasks (six males;
26.7 ± 11.0 years old; mean ± standard deviation (SD)). All the partici-
pants had drug-resistant epilepsy and underwent intracranial electrode
implantation as part of their epilepsy treatment (number of subdural
electrodes: 64.9 ± 19.4; number of depth electrodes: 6.2 ± 9.3). The sub-
jects were recruited from three university hospitals (Osaka University,
Juntendo University, and Nara Medical University). All the participants
provided written informed consent after receiving a detailed explanation
of the purpose and procedures of the experiment. The study protocol was
approved by the institutional ethics committees at each hospital (Osaka
University Medical Hospital: Approval No. 14353, UMIN000017900;
Juntendo University Hospital: Approval No. 18–164; Nara Medical
University Hospital: Approval No. 2098). All ethical regulations relevant
to human research participants were followed.
Sample size. The duration of data collection varied among participants
and was dependent on both their clinical treatment schedules and their
voluntary participation time. The number of experimental trials was
established on the basis of our previous study12.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
9


## Page 10

Localization of intracranial electrodes. The process of localizing
intracranial electrodes was performed using presurgical T1-weighted
magnetic resonance (MR) images and postsurgical computed tomo-
graphy (CT) images as follows. Individual cortical surfaces were extracted
from MR images and registered to the fsaverage template brain using
FreeSurfer56. The locations of intracranial electrodes were manually
identiﬁed on CT images (coregistered to MR images) using BioImage
Suite57. The identiﬁed subdural electrodes were then projected onto
individual cortical surfaces using the intracranial electrode visualization
toolbox58. On the basis of the initial registration, the location of each
subdural electrode was mapped to the template brain. For region-based
analysis, the electrodes were categorized into 22 brain regions according
to the Human Connectome Project parcellation scheme55. T1-weighted
MRI data of each subject were collected using a 3.0-Tesla SYNAPSE
VINCENT scanner (Fujiﬁlm, Tokyo, Japan) located at Osaka Uni-
versity’s hospital.
Stimuli dataset. Similar to the fMRI and MEG experiments, we used the
GOD image dataset, which consists of 1200 training images from 150
categories (8 images per category) and 50 test images from 50 categories
(1 image per category). The baseline image dataset consisted of 60 images,
including ﬁve images each from three categories: faces, landscapes, and
words. These images were extracted from the stimulus movies used in a
previous study12. To create these datasets, all the images were pre-
processed by cropping them into squares using the methods outlined in a
previous study15. The GOD image dataset and images used as the baseline
stimuli had no overlap.
ECoG acquisition. The subjects viewed visual stimuli while seated either
on hospital beds or in chairs facing a computer screen. ECoG signals were
acquired using an EEG-1200 system (Nihon Koden, Tokyo, Japan) at a
10 kHz sampling rate, with reference to the average of two intracranial
electrodes. A DATAPixx3 system (VPixx Technologies, Quebec,
Canada) monitored the presentation timing of visual stimuli, synchro-
nizing this information with the ECoG recordings.
Experimental settings. The image presentation task was conducted over
multiple recording sessions (2–4 sessions across 1–3 days), with baseline
ECoG recordings acquired at the start of each session to compensate for
electrode impedance variations59. During all the tasks, the participants
maintained ﬁxation on a central point displayed on the screen. Four
subjects from the initial cohort were selected for detailed analysis on the
basis of two criteria: the presence of electrode implants in the ventral
stream visual cortex and above-chance initial samplewise and dimen-
sionwise decoding performance. These selected subjects had 74, 56, 30,
and 71 electrodes implanted, respectively.
Baseline recording task. To account for electrode impedance variations
between recording sessions, a baseline recording task was conducted at
the beginning of each session. The task comprised one run, during which
baseline dataset images were presented sequentially in random order for
1125 ± 25 ms each, without intervening blank screens.
Image presentation task. All the participants participated in the
image presentation task, where visuals from the GOD image dataset
were shown as stimuli. Each training session consisted of two runs
to display all the GOD training images, while each test session
included a single run. Within each run, 10 images from the preceding
stimulus dataset were presented ﬁrst in a randomized order, followed by
randomly ordered images from the GOD dataset. No blank intervals
separated the images, and each image was displayed for approximately
525 ± 25 ms.
Signal preprocessing and calculation of high-γ features. For each
subject, we performed a visual inspection of the raw data and excluded
noisy channels from all subsequent analyses. Common average refer-
encing was then applied to mitigate common noise sources and accent-
uate local neural activity. ECoG epochs, which were time-locked to
stimulus onset and extended 0.5 seconds after the stimulus, were
extracted to focus on stimulus-related processing. Power spectral density
analysis was performed on each epoch using Welch’s method with 1024-
sample windows, and the high gamma power component (80–150 Hz)
was extracted by summing the power within this frequency range for each
channel. To complete the preprocessing pipeline, we concatenated the
data corresponding to electrodes that were placed in the ventral visual
stream of patients as the ﬁnal ECoG data for the subsequent decoding
analyses.
Autoencoder framework. The autoencoder consists of two fully
connected layers with ReLU activation functions. The number of
dimensions in the autoencoder’s latent space was set to half the number
of dimensions of the original vectors. For each subject, brain region, and
semantic space type, a separate autoencoder was trained. When training
the autoencoder for a particular subject, we used the averaged brain
RSMs of all the other subjects. After we ﬁnished the training process, we
passed all the original semantic vectors to the trained model and used
the intermediate features of the resulting trained autoencoder as the
brain-aligned features.
The RSM matrices were created from the brain activity pattern or the
autoencoder’s latent space by calculating the pairwise cosine similarity of
each of the two data points. During the training process, we used the dif-
ference between the upper triangle of each of the RSM matrices to constrain
the autoencoder to make representations more brain-like.
Neural decoding of visual stimuli
We performed brain decoding by constructing linear regression models to
predict semanticvectorsfrombrainactivitypatterns. To predicteach unitof
semantic vectors, a separate set of linear regression models was trained.
Prior to regression analysis, we performed voxel selection via a method
similar to that used by Horikawa and Kamitani15, and the brain activity
patterns were Z-normalized.
More formally, given that x ¼
x1; x2; .. . ; xn

T represents the
activity of n neural activity data points (i.e., voxels in the fMRI data, source-
estimated neural activity patterns from MEG sensors, and neural amplitude
recordedfrom each channel in each second in the ECoG) from the region of
interest, the regression function can be represented as follows:
y xð Þ ¼
X
n
i¼1
wixi þ w0
wherexi isascalarvaluespecifyingtheamplitudeofthebraindatapointi,wi
is the weight of voxel i and w0 is the bias.
For each subject, semantic space type, and brain region, we trained a
separate set of linear regression functions as decoders. When the fMRI data
ofaparticularsubjectweredecodedtothebrain-alignedsemanticspaces,we
used the brain-aligned space in which that subject was not used to create.
When the MEG data of a particular subject were decoded, we used the
averaged brain-aligned semantic spaces of all the fMRI subjects.
Identiﬁcation analysis
For the identiﬁcation analysis, the predicted vector was identiﬁed among a
large set of candidate vectors. First, we prepared one random image from
1000 randomly selected classes of the ImageNet dataset. Then, for each
semantic space (i.e., the GloVe- and CLIP-based pretrained feature vectors
or the GloVe- and CLIP-based brain-aligned vectors for different values of
α), we calculated the corresponding semantic vectors of all the images that
had been randomly selected from ImageNet. If we could not obtain the
GloVe embeddings of a category, that category was excluded from all
analyses. After obtaining the brain-aligned vectors of all the ImageNet
categories, we input the original GloVe/CLIP-pretrained feature vectors to
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
10


## Page 11

the corresponding trained autoencoder and obtained the corresponding
brain-aligned vectors. Then, for each category in the GOD dataset, we
calculatedthePearsoncorrelationcoefﬁcientbetweenthetrueandpredicted
vectors and between the predicted vector and all other candidate vectors,
and assigned the identiﬁcation accuracy as the percentage of candidate
categories, in which their correlation with the test predicted vector is lower
than the correlation of the true and predicted vectors. The chance-level
identiﬁcation accuracy was determined by randomly shufﬂing the true
feature vectors and calculating the identiﬁcation accuracy for the shufﬂed
vectors, following the same procedure as for the unshufﬂed data.
Statistics and reproducibility
In the decoding analyses, we evaluated the performance of the brain
decoders using the Pearson correlation coefﬁcients between the predicted
and true feature vectors as well as between the predicted and shufﬂed true
feature vectors. We then applied Fisher’s z-transform to the correlations of
each case to stabilize variance, followed by one-sided t-tests for each feature
space type and neuroimaging modality. Similarly, in the identiﬁcation
analysis, we performed a one-sided t-test between the identiﬁcation results
of shufﬂed data and unshufﬂed data.
To compare the decoding and identiﬁcation accuracy means among
the original feature vectors and brain-aligned feature vectors, we applied
one-way analysis of variance (ANOVA) followed by Tukey’s honestly sig-
niﬁcant difference post hoc test. Prior to each t-test and ANOVA, we
assessed the normality of the data via the Shapiro‒Wilk test.
To calculate the signiﬁcant differences in F value distributions among
the different typesof CLIP-based feature vectors(original vs. brain-aligned),
we applied the two-sided Wilcoxon rank-sum test between each pairwise
combination of brain-aligned feature vectors.
Reporting summary
Further information on research design is available in the Nature Portfolio
Reporting Summary linked to this article.
Data availability
The datasets supporting the ﬁndings of this study include fMRI, MEG, and
ECoG data. The fMRI dataset used in this study is available at15. Source data
underlyingtheﬁguresareavailableinFigsharewiththeidentiﬁerhttps://doi.
org/10.6084/m9.ﬁgshare.30845336.
Code availability
The code used for data analysis in this study is available on our repository
(https://github.com/yanagisawa-lab). For any inquiries, please contact the
corresponding author.
Received: 12 September 2024; Accepted: 23 December 2025;
References
1.
Stavisky, S. D. & Wairagkar, M. Listening in to perceived speech with
contrastive learning. Nat. Mach. Intell. https://doi.org/10.1038/
s42256-023-00742-1 (2023).
2.
Lebedev, M. A. & Nicolelis, M. A. L. Brain–machine interfaces: past,
present and future. Trends Neurosci. 29, 536–546 (2006).
3.
Willett, F. R. et al. A high-performance speech neuroprosthesis.
Nature 620, 1031–1036 (2023).
4.
Willsey, M. S. et al. Real-time brain-machine interface in non-human
primates achieves high-velocity prosthetic ﬁnger movements using a
shallow feedforward neural network decoder. Nat. Commun. 13, 6899
(2022).
5.
Haynes, J.-D. & Rees, G. Decoding mental states from brain activity in
humans. Nat. Rev. Neurosci. 7, 523–534 (2006).
6.
Naselaris, T., Kay, K. N., Nishimoto, S. & Gallant, J. L. Encoding and
decoding in fMRI. Neuroimage 56, 400–410 (2011).
7.
Haxby, J. V. et al. Distributed and overlapping representations of faces
and objects in ventral temporal cortex. Science 293, 2425–2430 (2001).
8.
Yamins, D. L. K. et al. Performance-optimized hierarchical models
predict neural responses in higher visual cortex. Proc. Natl. Acad. Sci.
USA 111, 8619–8624 (2014).
9.
Kellis, S. et al. Decoding spoken words using local ﬁeld potentials
recorded from the cortical surface. J. Neural Eng. 7, 056007 (2010).
10. Brouwer, G. J. & Heeger, D. J. Decodingand reconstructing color from
responses in human visual cortex. J. Neurosci. 29, 13992–14003
(2009).
11. Sitaram, R. et al. Closed-loop brain training: the science of
neurofeedback. Nat. Rev. Neurosci. 18, 86–100 (2017).
12. Fukuma, R. et al. Voluntary control of semantic neural representations
by imagery with conﬂicting visual stimulation. Commun. Biol. 5, 214
(2022).
13. Chaudhary, U. et al. Spelling interface using intracortical signals in a
completely locked-in patient enabled via auditory neurofeedback
training. Nat. Commun. 13, 1236 (2022).
14. Cortese, A., Amano, K., Koizumi, A., Kawato, M. & Lau, H. Multivoxel
neurofeedback selectively modulates conﬁdence without changing
perceptual performance. Nat. Commun. 7, 13669 (2016).
15. Horikawa, T. & Kamitani, Y. Generic decoding of seen and imagined
objects using hierarchical visual features. Nat. Commun. 8, 15037
(2017).
16. Haynes, J.-D. & Rees, G. Predicting the orientation of invisible stimuli
from activity in human primary visual cortex. Nat. Neurosci. 8,
686–691 (2005).
17. Kamitani, Y. & Tong, F. Decoding the visual and subjective contents of
the human brain. Nat. Neurosci. 8, 679–685 (2005).
18. Thirion, B. et al. Inverse retinotopy: inferring the visual content of
images from brain activation patterns. Neuroimage 33, 1104–1116
(2006).
19. Cox, D. D. & Savoy, R. L. Functional magnetic resonance imaging (fMRI)
“brain reading”: detecting and classifying distributed patterns of fMRI
activity in human visual cortex. NeuroImage 19, 261–270 (2003).
20. Nakai, T., Koide-Majima, N. & Nishimoto, S. Correspondence of
categorical and feature-based representations of music in the human
brain. Brain Behav. 11, e01936 (2021).
21. Koide-Majima, N., Nishimoto, S. & Majima, K. Mental image
reconstruction from human brain activity: Neural decoding of mental
imagery via deep neural network-based Bayesian estimation. Neural
Networks 170, 349–363 (2024).
22. Miyawaki, Y. et al. Visual image reconstruction from human brain
activity using a combination of multiscale local image decoders.
Neuron 60, 915–929 (2008).
23. Shen, G., Dwivedi, K., Majima, K., Horikawa, T. & Kamitani, Y. End-to-
end deep image reconstruction from human brain activity. Front.
Comput. Neurosci. 13, 21 (2019).
24. Shen, G., Horikawa, T., Majima, K. & Kamitani, Y. Deep image
reconstruction from human brain activity. PLoS Comput. Biol. 15,
e1006633 (2019).
25. Liu, Y., Ma, Y., Zhou, W., Zhu,G. & Zheng, N. BrainCLIP: bridging brain
and visual-linguistic representation Via CLIP for generic natural visual
stimulus decoding. Preprint at https://doi.org/10.48550/arXiv.2302.
1297 (2023).
26. Radford, A. et al. Learning transferable visual models from natural
language supervision. in 8748–8763 (PMLR, 2021).
27. Pereira, F. et al. Toward a universal decoder of linguistic meaning from
brain activation. Nat. Commun. 9, 963 (2018).
28. Mikolov, T., Chen, K., Corrado, G. & Dean, J. Efﬁcient estimation of
word representations in vector space. arXiv preprint arXiv:1301.3781
(2013).
29. Pennington, J., Socher, R. & Manning, C. GloVe: Global Vectors for
Word Representation. in Proc. 2014 Conference on Empirical
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
11


## Page 12

Methods in Natural Language Processing (EMNLP) 1532–1543
(Association for Computational Linguistics, 2014).
30. Shirakawa, K. et al. Spurious reconstruction from brain activity. Neural
Netw. 190, 107515 (2025).
31. Federer, C., Xu, H., Fyshe, A. & Zylberberg, J. Improved object
recognition using neural networks trained to mimic the brain’s
statistical properties. Neural Netw. 131, 103–114 (2020).
32. Muttenthaler, L. et al. Improving neural network representations using
human similarity judgments. Advances in neural information
processing systems 36, 50978–51007 (2023).
33. Schneider, S., Lee, J. H. & Mathis, M. W. Learnable latent
embeddings for joint behavioural and neural analysis. Nature 617,
360–368 (2023).
34. Kay, K. N., Naselaris, T., Prenger, R. J. & Gallant, J. L. Identifying
naturalimages fromhumanbrain activity. Nature 452, 352–355 (2008).
35. Ogawa, S., Lee, T.-M., Kay, A. R. & Tank, D. W. Brain magnetic
resonance imaging with contrast dependent on blood oxygenation.
Proc. Natl. Acad. Sci. USA 87, 9868–9872 (1990).
36. Penﬁeld, W. & Jasper, H. Epilepsy and the functional anatomy of the
human brain. (Little, Brown & Co., Boston, 1954).
37. Cohen, D. Magnetoencephalography: evidence of magnetic ﬁelds
produced by alpha-rhythm currents. Science 161, 784–786 (1968).
38. Deng, J. et al. ImageNet: a large-scale hierarchical image database. in
2009 IEEE Conference on Computer Vision and Pattern Recognition
248–255 https://doi.org/10.1109/CVPR.2009.5206848 (2009).
39. Kriegeskorte, N., Mur, M. & Bandettini, P. Representational similarity
analysis—connecting the branches of systems neuroscience. Front.
Syst. Neurosci. 2, 4 (2008).
40. Kourtzi, Z. & Kanwisher, N. Cortical regions involved in perceiving
object shape. J. Neurosci. 20, 3310–3318 (2000).
41. Kanwisher, N., McDermott, J. & Chun, M. M. The fusiform face area: a
moduleinhumanextrastriatecortexspecializedfor faceperception.J.
Neurosci. 17, 4302–4311 (1997).
42. Epstein, R. & Kanwisher, N. A cortical representation of the local visual
environment. Nature 392, 598–601 (1998).
43. Gifford, A. T., Jastrzębowska, M. A., Singer, J. J. D. & Cichy, R. M. In
silico discovery of representational relationships across visual cortex.
Nat. Hum. Behav. https://doi.org/10.1038/s41562-025-02252-z
(2025).
44. Kobatake, E. & Tanaka, K. Neuronal selectivities to complex object
features in the ventral visual pathway of the macaque cerebral cortex.
J. Neurophysiol. 71, 856–867 (1994).
45. Binder, J. R. et al. Toward a brain-based componential semantic
representation. Cogn. Neuropsychol. 33, 130–174 (2016).
46. Chersoni, E., Santus, E., Huang, C.-R. & Lenci, A. Decoding word
embeddings with brain-based semantic features. Comput. Linguist.
47, 663–698 (2021).
47. Li, Y., Yang, H. & Gu, S. Enhancing neural encoding models for
naturalistic perception with a multi-level integration of deep neural
networks and cortical networks. Sci. Bull. https://doi.org/10.1016/j.
scib.2024.02.035 (2024).
48. Haxby, J. V. et al. A common, high-dimensional model of the
representational space in human ventral temporal cortex. Neuron 72,
404–416 (2011).
49. Guntupalli, J. S. et al. A model of representational spaces in human
cortex. Cereb. cortex 26, 2919–2934 (2016).
50. Cichy, R. M. & Pantazis, D. Multivariate pattern analysis of MEG and
EEG: A comparison of representational structure in time and space.
NeuroImage 158, 441–454 (2017).
51. Salmela, V., Salo, E., Salmi, J. & Alho, K. Spatiotemporal dynamics of
attention networks revealed by representational similarity analysis of
EEG and fMRI. Cereb. Cortex 28, 549–560 (2018).
52. Sereno, M. I. et al. Borders of multiple visual areas in humans revealed
by functional magnetic resonance imaging. Science 268, 889–893
(1995).
53. Tadel, F., Baillet, S., Mosher, J. C., Pantazis, D. & Leahy, R. M.
Brainstorm: a user-friendly application for MEG/EEG analysis.
Comput. Intell. Neurosci. 2011, 879716 (2011).
54. Yoshioka, T. et al. Evaluation of hierarchical Bayesian method through
retinotopic brain activities reconstruction from fMRI and MEG signals.
NeuroImage 42, 1397–1413 (2008).
55. Glasser, M. F. et al. A multi-modal parcellation of human cerebral
cortex. Nature 536, 171–178 (2016).
56. Dale, A. M., Fischl, B. & Sereno, M. I. Cortical surface-based analysis:
I. segmentation and surface reconstruction. NeuroImage 9, 179–194
(1999).
57. Papademetris, X. et al. BioImage suite: an integrated medical image
analysis suite: an update. Insight J. 2006, 209 (2006).
58. Groppe, D. M. et al. iELVis: an open source MATLAB toolbox for
localizing and visualizing human intracranial electrode data. J.
Neurosci. Methods 281, 40–48 (2017).
59. Fukuma, R. et al. Image retrieval based on closed-loop
visual–semantic neural decoding. Preprint at https://doi.org/10.1101/
2024.08.05.606113 (2024).
Acknowledgements
We acknowledge the use of open-source code from the Kamitani Lab.
Speciﬁcally, we used the Brain Decoding Toolbox (BDPy; https://github.
com/KamitaniLab/bdpy) for neuroimaging data processing and analysis,
and adapted decoding algorithms from the Generic Object Decoding
repository (https://github.com/KamitaniLab/GenericObjectDecoding; Hor-
ikawa & Kamitani, 2017). We thank the Kamitani Lab for making these
resources publicly available. We also thank all the subjects for their partici-
pation. This research was supported by the Japan Science and Technology
Agency (JST) Moonshot R&D (JPMJMS2012), the JST Core Research for
Evolutional Science and Technology (CREST) (JPMJCR18A5), the JST AIP
Acceleration Research (JPMJCR24U2), K Program (JPMJKP25Y7), and the
Japan Society for the Promotion of Science (JSPS) Grants-in-Aid for Sci-
entiﬁc Research (KAKENHI) (JP26560467 and JP20H05705).
Author contributions
S.V.andT.Y.conceptualizedtheproject.S.V.wasresponsibleforthetheory.
S.V., R.F., and T.Y. were responsible for the methodology. S.V. undertook
the analysis and investigation. R.F. and H.Y. were responsible for the MEG
and ECoG experiments. S.V. was responsible for data preprocessing and
curation. S.V. wrote the original draft and created the ﬁgures. S.V. and T.Y.
edited the ﬁnal version of the article. S.O., N.T., H.M.K., H.S., Y.I., H.S., M.N.,
H.K., and K.T. performed the neurosurgery of ECoG experiments.
Competing interests
The authors declare that they have no competing interests.
Additional information
Supplementary information The online version contains
supplementary material available at
https://doi.org/10.1038/s42003-025-09482-x.
Correspondence and requests for materials should be addressed to
Takufumi Yanagisawa.
Peer review information Communications Biology thanks Marijn van Vliet
and the other, anonymous, reviewer(s) for their contribution to the peer
review of this work. Primary Handling Editors: Shenbing Kuang and Jasmine
Pan. A peer review ﬁle is available.
Reprints and permissions information is available at
http://www.nature.com/reprints
Publisher’s note Springer Nature remains neutral with regard to
jurisdictional claims in published maps and institutional afﬁliations.
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
12


## Page 13

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
© The Author(s) 2026
https://doi.org/10.1038/s42003-025-09482-x
Article
Communications Biology |  (2026) 9:206 
13


