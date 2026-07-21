# (2026) Representational differentiation and integration within the hippocampal circuit during naturalistic stimuli

**Source:** (2026) Representational differentiation and integration within the hippocampal circuit during naturalistic stimuli.pdf

---

## Page 1

communications biology
Article
A Nature Portfolio journal
https://doi.org/10.1038/s42003-026-09554-6
Representational differentiation and
integration within the hippocampal
circuit during naturalistic stimuli
Check for updates
Lili Sun
1,2, Qiuyi Liu1,2, Siyang Li
3, Wencai Ding
4, Zhipeng Li
5, Kaizhou Li1,2, Wenbin Qu1,2 &
Xia Liang2,6
The hippocampus is essential for transforming dynamic experiences into structured knowledge,
forming internal models of the world that guide planning, decision-making, and behavior. Recent
research has demonstrated that complementary hippocampal mechanisms—speciﬁcally, the
differentiation of distinct experiences and the integration of related information—fundamentally
underlie cognitive map formation during spatial navigation. However, there is limited empirical
evidence on how these processes support network-based, map-like representations during complex
continuous stimuli. Here, using the Human Connectome Project 7T naturalistic dataset, we explored
how the canonical hippocampal circuit (DG-CA3-CA1) supports differentiation and integration from
movie stimuli. Our results found that the hippocampus encoded both semantic features and small-
world network representations from movie stimuli. Moreover, we observed representational
differentiation in geodesic network distances within the DG-CA3 pathway, while integration
predominated in the CA3-CA1 pathway. Inter-subject functional correlation analysis revealed that
stronger hippocampal-cortical connectivity—especially with the retrosplenial cortex,
parahippocampal cortex, medial prefrontal cortex, and visual regions—was positively correlated with
CA3-CA1 integration capacity. Notably, CA1-retrosplenial connectivity emerged as a key mediator
linking hippocampal integration to individual cognitive performance. These insights reveal how the
hippocampus dynamically differentiates and integrates movie information, highlighting the
importance of hippocampal-retrosplenial interactions in linking hippocampal integration processes
with cognitive abilities.
In our increasingly complex and dynamic world, the human brain must
efﬁciently abstract common features from diverse stimuli and infer rela-
tional structures to form organized knowledge systems. Cognitive maps—
internal models representing relationships between environmental ele-
ments—emerge as a fundamental mechanism underlying this process1–4.
These mental representations allow efﬁcient navigation, organization, and
retrieval of information based on prior experiences. Recent studies in graph
learning provide a powerful framework for understanding how humans
processandrepresentsuchnetworkedinformation5–8.Throughthisprocess,
people construct map-like internal representations that capture network
topologies, transforming environmental elements into interconnected
nodes and their relationships into edges. This network science approach
connects neural representation topologies with cognitive maps, offering
theoretical frameworks and methodological tools to investigate how the
brain constructs and utilizes these maps to navigate complexity4,7.
Thehippocampus,longrecognized foritsroleinspatialnavigationand
cognitive map formation, extends its inﬂuence far beyond physical envir-
onments. Emerging evidence highlights that the hippocampal circuitry
supports the organization of diverse non-spatial information, including
conceptual knowledge structures, social relationships networks, and even
1School of Life Science and Technology, HIT Faculty of Life Science and Medicine, Harbin Institute of Technology, Harbin, China. 2Research Center for Social
Computing and Interactive Robotics, Harbin Institute of Technology, Harbin, China. 3School of Biomedical Engineering, Faculty of Medicine, Dalian University of
Technology, Dalian, China. 4Department of Neurology, The Second Afﬁliated Hospital of Wannan Medical College, Wuhu, China. 5Center for Sleep and Circadian
Medicine, The Afﬁliated Brain Hospital of Guangzhou Medical University, Guangzhou, China. 6Frontiers Science Center for Matter Behave in Space Environment,
Harbin Institute of Technology, Harbin, China.
e-mail: xia.liang@hit.edu.cn
Communications Biology |  (2026) 9:274 
1
1234567890():,;
1234567890():,;


## Page 2

dynamical transitions among spontaneous brain states9–13. Investigating
these broader hippocampal functions necessitates a shift toward naturalistic
paradigms (e.g., movies and narratives). Unlike controlled experiments,
exposure to a movie or a narrative better mirrors the complexity of real-
world experiences, allowing for a deeper investigation into how the brain
processes continuous, intricate information14,15. Studies employing audio-
visual narratives have shown enhanced memory for central, semantically
rich connected events, highlighting the importance of structured repre-
sentations in learning16. However, a pivotal question that remains to be
resolved is whether the hippocampus can systematically extract relational
information embedded within complex non-spatial stimuli—such as those
embedded in narrative ﬁlms—and construct structured network repre-
sentations that are analogous to the well-characterized cognitive maps of
spatial environments.
The hippocampus is a heterogeneous brain structure composed of the
dentate gyrus (DG) and cornu ammonis (CA1-4) subﬁelds17,18, with each
subﬁeld playing distinct roles in hippocampal function. For instance, the
DG subﬁeld is primarily implicated in pattern separation, a computational
processthatdifferentiatessimilarmemoryrepresentationstoreduceoverlap
across input information19–22. In contrast, CA3 and CA1 subﬁelds are more
involved in pattern completion, which facilitates the retrieval of complete
memories or contextual regularities from partial cues22–24. Our recent
work25, examining hippocampal activity during a naturalistic audio-movie
task, demonstrated that the canonical hippocampalcircuit exhibits evidence
of pattern separation within the DG-CA3 pathway and pattern completion
within the CA3-CA1 pathway. This reveals a dynamic interplay within the
hippocampal circuit, where the initial differentiation of experiences in the
DG subﬁeld is followed by integration and generalization in downstream
regions. Recent evidence from spatial cognition studies demonstrates that
the hippocampus simultaneously differentiates (pattern separation) and
integrates (pattern completion) neural representations to build coherent
models of the spatial environment, illustrating how these computational
processes collectively contribute to the formation of structured cognitive
maps26. Previous studies investigating pattern separation and completion
processes have frequently employed methodologies that quantify temporal
distances between neural patterns associated with distinct inputs25,27,28.
While these approaches provide valuable insights, they often simplify
complex representational transformations to basic distance metrics,
potentially overlooking the intricate organization of neural representations.
Standard measures, such as Euclidean distance, compute straight-line dis-
tances in a ﬂat space, which can fail to account for the topological rela-
tionships that exist within neural data as information ﬂows through the
hippocampal circuit. To address these limitations, we propose the use of
geodesicdistance,whichisthelengthoftheshortestpathtraversingbetween
two nodes within a network, offering a metric that is sensitive to the
underlying topology of the neural representations29,30. This approach facil-
itates a more comprehensive understanding of how representational
structures undergo systematic transformations across hippocampal sub-
ﬁelds, thereby highlighting the organizational principles of neural codes and
their evolution throughout cognitive map formation.
Mounting evidence suggests that the hippocampus does not function
in isolation but cooperates with a broader network of cortical regions. For
instance, successful memory encoding correlates with enhanced functional
connectivity between hippocampal structures and speciﬁc cortical regions,
including the parahippocampal cortex (PHC), retrosplenial cortex (RSC),
and medial prefrontal cortex31. Similarly, during episodic memory retrieval,
strengthened hippocampal-cortical interactions facilitate the reinstatement
of complete neural patterns, particularly in the context of naturalistic tasks
like movie viewing32. These ﬁndings underscore the crucial role of tight
hippocampal-cortical coupling in supporting learning and memory pro-
cesses. However, it remains unclear how the computational processes of
differentiation and integration within hippocampal subﬁelds inﬂuence the
broader hippocampal-cortical interactions during complex, naturalistic
information processing.
In this study, based on the Human Connectome Project (HCP) 7T
naturalistic dataset, we aim to investigate hippocampal mechanisms
underlyingcomplex,real-worldcognitiveprocessing.First,weestablishhow
hippocampal subﬁelds represent semantic features and their relational
structures during movie encoding, using representational similarity analysis
andgraph-theoreticalanalysis.Then,weassessgeodesicdistanceinnetwork
representation for each hippocampal subﬁeld. This approach allows us to
measuretopologicalrepresentationdifferentiationandintegrationalongthe
hippocampal circuit by comparing geodesic distances between representa-
tions within each subﬁeld pathway (i.e., DG-CA3, CA3-CA1). Speciﬁcally,
increased geodesic distances in network representation (differentiation)
indicate evidence consistent with the occurrence of pattern separation,
whereas decreased geodesic distances (integration) suggest evidence con-
sistent with pattern completion. Furthermore, we map the broader
hippocampal-cortical network using inter-subject functional correlation
analysis to identify cortical regions signiﬁcantly co-activated with each
subﬁeld,andexaminehowtheseinteractionsrelatetothedifferentiationand
integrationprocesseswithinthehippocampalcircuit.Finally,weexplorethe
relationship betweenhippocampal function and individual behavioral traits
during movie viewing. Speciﬁcally, we evaluate whether the neural differ-
entiation and integration of topological distance representations, along with
hippocampal-cortical interactions, respectively predict cognitive and emo-
tional scores. We further apply mediation analysis to elucidate potential
causal pathways linking hippocampal computations, hippocampal-cortical
connectivity patterns, and individual behavioral performance.
Materials and methods
Datasets
Participants. All data in this study are sourced from the 7T release of the
HCP33, initially with 184 participants. In this study, we removed parti-
cipants who failed to meet the speciﬁc quality-control criteria deﬁned by
the HCP. Speciﬁcally, we excluded participants with anatomical
anomalies (code A), segmentation problems in the structural pipeline
(code B), and head-coil instabilities (code C). This procedure resulted in
the ﬁnal set of 157 participants that were used for our analyses. These
participants were healthy young adults, aged from 22 to 36 years (97
females). The study wasapproved bythelocal IRB Committee (Comité de
Ética de la Investigación y de Bienestar Animal) of the Universidad de La
Laguna (CEIBA2017-270).
Behavioral data. The HCP dataset collects comprehensive behavioral
measures across cognitive, emotional, sensory, and motor domains for
each participant, providing essential data for understanding brain-
behavior relationships (HCP S1200 Release Reference Manual). Previous
study has shown that functional connectivity during naturalistic viewing
yields more accurate predictions of cognitive and emotional behaviors
compared to resting-state assessments34, suggesting that naturalistic sti-
muli amplify individual differences in behaviorally relevant brain net-
works, thus better capturing the brain-behavior relationships. Moreover,
the hippocampus has emerged as a pivotal neural substrate underlying
cognitive and emotional processes35,36. We therefore focused on behavior
measures in cognitive and emotional domains (Table S1) to explore their
relationship with hippocampal function, hypothesizing that hippo-
campal pattern integration may provide a mechanistic explanation for
individual variations in cognitive and emotional traits. To handle mul-
tiple comparisons issues and consider correlations among measures in
each domain, we utilized the ﬁrst principal component (PC1) scores for
each participant offered by Finn et al.34. These behavioral scores were
derived
from
principal
components
analysis
of
the
cognitive
(movie_cpm/cogn_pc_scores.csv)
and
emotional
(movie_cpm/
emot_pc_scores.csv) domains. Speciﬁcally, higher cognitive PC1 scores
(“cognition score”) reﬂect better performance on tasks measuring read-
ing ability, vocabulary, ﬂuid intelligence, and spatial orientation. Higher
emotional PC1scores (“emotion score”) indicate greater self-reported life
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
2


## Page 3

satisfaction, emotional support, positive affect, lower sadness, and per-
ceived stress.
Movie stimuli and semantic features. Participants were instructed to
watch a series of audiovisual movie clips presented in four MOVIE runs.
Each MOVIE run consisted of 4–5 movie clips, interspersed with 20 s of
rest (indicated by the word “REST” in white on a black background).
MOVIE1 and MOVIE3 had clips from independent ﬁlms (both ﬁction
and documentary) licensed under Creative Commons on Vimeo, while
MOVIE2 and MOVIE4 included clips from Hollywood ﬁlms. Across the
four MOVIE runs, the duration of movie clips ranged from 1:03 to 4:19.
Notably, the ﬁnal clip in each MOVIE run was a montage of a brief video
(1.5 s), identical across all four runs. Given that having more data typi-
cally improves result reliability and accuracy, we retained only movie
clips with durations longer than the shortest clips (2:22, 142TRs),
retaining 13 movie clips for analysis (Table 1). Further details regarding
movie stimuli and experimental procedures are given in the HCP refer-
ence manual (HCP S1200 Release Reference Manual).
The HCP dataset provides semantic category features (7T_movie_r-
esources/WordNetFeatures.hdf5) extracted from movie stimuli. These fea-
tures describe high-level semantic content using a semantic category
model37 that generates labels for salient object and action categories within
each scene at 1-s (1TR) temporal resolution, enabling systematic compar-
ison with neural representations in the human brain. All labels were
assigned using the WordNet semantic taxonomy, which offers two
advantages for semantic encoding. First, WordNet synsets use numerical
identiﬁers to disambiguate homographs (e.g., “plant.n.01” for factory,
“plant.n.02” for organism, and “plant.v.01” for planting). Second, WordNet
includes information about is-a relationships between categories, which are
used to supplement the manually tagged labels. For example, “wolf” is an
instance of “canine,” which is an instance of “carnivore,” “placental mam-
mal,” “mammal,” and so on. Adding these superordinate categories
improves encoding model performance by allowing poorly sampled cate-
gories to share information with their WordNet neighbors. To ensure
labeling reliability, HCP used rigorous multi-stage validation procedures:
(1) one observer labeled all scenes, (2) eight observers each checked and
corrected labels for 1/8 of the movies, and (3) a different observer reviewed
all moviesfor label consistency. Further details are available in the 7T Movie
Stimulus Files module (ConnectomeDB).
MRIacquisition parameters. The structural magnetic resonance images
acquisition involved high-resolution T1- and T2-weighted images, and
all of which were performed on a customized 3T Siemens Connectome
Skyra scanner. The T1-weighted images were acquired via a 3D-
MPRAGE protocol: repetition time (TR) = 2400 ms, echo time (TE) =
2.14 ms, inversion time (TI) = 1000 ms, ﬂip angle (FA) = 80°, resulting in
0.7 mm isotropic voxels; The T2-weighted images were acquired using a
3D T2-SPACE protocol: TE = 565 ms, TR = 3200 ms, with a variable FA,
also yielding 0.7 mm isotropic voxels.
The functional MRI dataset was collected on a 7T Siemens Magnetom
scanner located at the Center for Magnetic Resonance Research at the
University of Minnesota in Minneapolis, using a 32-channel Siemens
receive head coil. The fMRI scanning parameters were as follows: TR =
1000 ms, TE = 22.2 ms, FA = 45°, matrix = 130 × 130, ﬁeld of view = 208
× 208 mm, number of slices = 85, spatial resolution = 1.6 mm3, image
acceleration factor (iPAT) = 2, multiband factor = 5, partial Fourier sam-
pling = 7/8, echo spacing = 0.64 ms, bandwidth = 1924 Hz/Px. The phase
encoding direction alternated between anterior-to-posterior for MOVIE1
and MOVIE4, and posterior-to-anterior for MOVIE2 and MOVIE3. The
durations of MOVIE1–4 runs were 921, 918, 915, and 901 TRs, respectively.
Further details of acquisition protocols are given in the HCP reference
manual (HCP S1200 Release Reference Manual).
MRI data preprocessing. In this study, we utilized the FIX-Denoised
naturalistic datasets in volume space for each participant (e.g., tfMRI_-
MOVIE1_7T_AP_hp2000_clean.nii.gz), which had undergone standard
preprocessing according to HCP minimal preprocessing pipelines38.
Speciﬁcally, the preprocessing steps mainly included, in order: head
motion correction, EPI image distortion correction, nonlinear alignment
to the MNI template space, and high-pass ﬁltering (1/2000 Hz). More-
over, the HCP took a denoising method combining independent com-
ponents analysis (ICA) with an automated component classiﬁer known
as FIX (FMRIB’s ICA-based X-noisiﬁer) to remove non-neural spatio-
temporal artifacts39,40. This also incorporated 24 framewise motion esti-
mates, including 6 rigid-body parameter time series, their backward-
looking temporal derivatives, plus all 12 resulting regressors squared to
minimize motion-related noise41. Comprehensive preprocessing details
are available in the HCP reference manual (HCP S1200 Release Reference
Manual). Note that the time courses of all movie scanning runs were
shifted by 5s (5TR) to accommodate the hemodynamic response delay.
Region of interest (ROI)
Segmentation of hippocampal subﬁelds. We used Freesurfer v7.1.1 to
automatically segment the hippocampal subﬁelds for each participant
using both T1- and T2-weighted MRI images as the inputs42. We chose
the templates “FS60” from the Segmentation of the Hippocampal Sub-
ﬁelds and Nuclei of the Amygdala (v21, cross-sectional and longitudinal)
to obtain complete segmentation results43. Here, we focused on two
pathways (i.e., DG-CA3 and CA3-CA1) based on the projection order
along the hippocampal circuit (DG-CA3-CA1), including three subﬁelds:
DG (the granule cell layer of the dentate gyrus), CA3 (the combined CA3/
2 region), and CA144. To guarantee segmentation quality across all par-
ticipants, we visually checked for the overlap between the dark band in
the T2-weighted images and the molecular layer detected by the seg-
mentation algorithm (Fig. S1). For each participant, we extracted voxel-
wise time courses for each movie clip from the hippocampal subﬁeld
masks and averaged across the voxel dimension. The number of voxels
for each hippocampal subﬁeld from the fMRI data is provided in
Table S2.
Cortical parcellation. For whole-brain-based analyses, we used the
Schaefer parcellation atlas based on fMRI functional connectivity
Table 1 | Description of 13 movie clips from the four
MOVIE runs
MOVIE Run
Clip
Film name
Duration
(TRs)
Duration
(min:s)
MOVIE1
1
Two Men
244
04:04
MOVIE1
2
Welcome to
Bridgeville
220
03:40
MOVIE1
3
Pockets
188
03:08
MOVIE2
4
Inception
227
03:47
MOVIE2
5
The Social
Network
259
04:19
MOVIE2
6
Ocean’s Eleven
250
04:10
MOVIE3
7
Off The Shelf
180
03:00
MOVIE3
8
1212
184
03:04
MOVIE3
9
Mrs. Meyer’s
Clean Day
204
03:24
MOVIE3
10
Northwest
Passage
142
02:22
MOVIE4
11
Home Alone
233
03:53
MOVIE4
12
Erin Brockovich
230
03:50
MOVIE4
13
The Empire
Strikes Back
256
04:16
MOVIE1 and MOVIE3 contain movie clips from independent ﬁlms freely available under a Creative
Commons license. MOVIE2 and MOVIE4 feature Hollywood ﬁlm clips. Note that this table only lists
the movie clips used in our analyses.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
3


## Page 4

patterns45. Speciﬁcally, this atlas parcellates the cortical surface of the
brain into 400 parcels (200 parcels per hemisphere), which are organized
into 17 functional networks46. For each participant, we similarly extracted
voxel-wise time courses for each movie clip from each of the parcel masks
and averaged across voxels.
Representational similarity analysis (RSA)
We applied representational similarity analysis by comparing similarity
matrices derived from two types of movie representations: (1) the text
descriptions of semantic features (i.e., object and action categories deli-
neated for each 1-s frame, see the section “Movie stimuli and semantic
features” for more details) and (2) the neural activity patterns recorded in
the hippocampal subﬁelds47.
To estimate the semantic similarity matrix, we ﬁrst extracted the
semantic features matrix from the HCP dataset, which captures high-level
movie features based on a semantic category model37. Next, we calculated
the pairwise cosine similarity between feature vectors of all TRs within each
movie clip, yielding K semantic similarity matrices of size M × M, where K is
the number of movie clips and M is the number of TRs within corre-
sponding clip (Fig. 1A).
For each hippocampal subﬁeld, a fMRI neural similarity matrix was
generated for each movie clip. This matrix was computed by calculating the
Pearson correlation of fMRI activity patterns across voxels between every
pair of TRs in each movie clip. This process led to K × N neural similarity
matrices, each of size M × M, where K is the number of movie clips, N is the
numberofparticipants,andMisthenumberofTRspermovieclip(Fig.1B).
The representational similarity between the semantic similarity matrix
and a neural similarity matrix was evaluated by calculating the Pearson
correlation between the lower triangles of the two matrices. To address
potential inﬂation of similarity estimates due to temporal autocorrelation, we
employed an off-diagonal RSA approach that excluded a diagonal band
(bandwidth K) from each matrix. The value of K was determined by ﬁrst
computing the autocorrelation function for each hippocampal subﬁeld (DG,
CA3, CA1), movie clip, and participant. Signiﬁcance at each lag was assessed
using 95% conﬁdence intervals (CIs) derived from Bartlett’s formula. The
resulting K values were averaged across movie clips, producing a participant-
speciﬁc distribution for each subﬁeld. This analysis established that a
bandwidth of K = 7 TRs was sufﬁcient to cover over 99% of participants in all
hippocampal subﬁelds (Fig. S2A, B), effectively controlling for autocorrela-
tion while preserving sufﬁcient data for RSA. To assess statistical signiﬁcance,
we employed a block permutation test (block length = 10 TRs). For each of
1000 iterations, the neural time series were shufﬂed in blocks, and the RSA
procedure was then repeated to generate a null distribution of correlation
coefﬁcients. One-tailed p values were calculated as the proportion of per-
muted RSA values that exceeded the actual mean representational similarity:
p value ¼
Pnnull
i¼1 I rnull;i > ractual


þ 1
nnull þ 1
wherennull represents the number of randomization iterations (1000), rnull;i
are therandomRSAvaluesfromeachshufﬂe(averagedacrossparticipants),
ractual is the actual mean RSA value across participants, and I is an indicator
function that returns 1 if the condition rnull;i > ractual is true, and 0 otherwise.
The signiﬁcant threshold was set at 0.05 following Bonferroni correction for
the 39 comparisons across 13 movie clips and 3 hippocampal subﬁelds. To
ensure our ﬁndings were not dependent on a speciﬁc block length, we
validated the results using block permutation tests with block lengths
varying from 15 to 40 TRs (in 5-TR increments).
In
addition
to
block
permutation,
we
adopted
the
phase-
randomization method, generating 1000 surrogate time series as a com-
plementary null model to further validate our results.
To evaluate whether the observed representational correlations are
meaningful given measurement noise, we estimated group-level noise ceil-
ings using split-half analyses48. Speciﬁcally, for each split, all participants were
randomly divided into two equal groups, and we calculated the Pearson
correlation between the average neural similarity matrix of the two halves. To
account for biases resulting from the split-half calculations, we applied a
Spearman–Brown correction. We report these noise ceilings in Table S3.
To investigate changes in representational capacity within the hippo-
campal circuit, we averaged the Pearson correlation coefﬁcients across
movie clips to obtain a single RSA value for each subﬁeld and participant.
Then,
we
calculated
the
difference
in
representational
similarity
(RSAA-RSAB) for each hippocampal ROIA-ROIB pathway (e.g., DG-CA3
and CA3-CA1) and conducted one-sample t-tests. To account for multiple
comparisons across the two hippocampal pathways, the signiﬁcance
threshold was set at 0.05/2 using Bonferroni correction.
Graph-theoretical analysis
To characterize the topological structure of the movie stimuli, we applied
graph-theoretical analysis to the semantic similarity matrix and the neural
similarity matrices, where TRs served as network nodes and the similarity
between TR pairs deﬁned network edges. We employed a range of sparsity
thresholds (top 20% similarity) to the semantic and neural similarity
matrices to remove unreliable edges potentially caused by various noise
sources. Then, we calculated global efﬁciency (Eglob) and local efﬁciency
(Elocal) forboth thesemantic and neuralsimilaritynetworks. To evaluate the
non-random architecture of these networks, we compared Eglob and Elocal of
the real networks to those derived from 1000 comparable random null
networks with the same nodes, edges, and weight distributions as the real
networks for each participant. Small-worldness was deﬁned using nor-
malized global efﬁciency (Ereal
glob=Erand
glob  1) and normalized local efﬁ-
ciency (Ereal
local=Erand
local > 1).
Geodesic distance of representations
Geodesic distance is a metric that captures the underlying non-Euclidean
geometry of functional correlation matrices, providing a sensitive measure of
topological proximity within the neural state spaces29,30. Unlike traditional
Euclidean distance, which measures straight-line distances between points in
ﬂat Euclidean space, geodesic distance represents the weighted length of the
shortest path traversing two points within a network (i.e., the neural simi-
larity matrix in our case). This calculation yields a representational geodesic
distance matrix, which includes the shortest paths between all pairs of nodes.
To explore whether neural representations are differentiated or integrated
within the hippocampal circuit, we measured and compared the geodesic
distances of neural representations across different hippocampal subﬁelds.
Speciﬁcally, for each participant and clip, we calculated the shortest path
distances between all pairs of nodes within the neural similarity matrix of
each hippocampal subﬁeld, resulting in a geodesic distance matrix M.
To evaluate representational changes along the hippocampal circuit,
we then compared the geodesic distance matrices of two subﬁelds within
each hippocampal ROIA – ROIB [pathway (e.g., DG-CA3 and CA3-CA1)],
yielding a geodesic distance difference matrix (Mdiff = MB-MA). Increased
distances from ROIA to ROIB reﬂect a differentiation process, while
decreased distances indicate an integration process. We quantiﬁed these
processes in two ways. First, we calculated the proportion of increased
distances and decreased distances within the lower triangular of each Mdiff
matrix. Paired t-tests were conducted across participants to compare the
number of node pairs showing differentiation versus integration for each
hippocampal pair. Second, we averaged the lower triangle of Mdiff to cal-
culate the mean distance change for each participant and performed one-
sample t-tests to assess whether the given hippocampal pathway showed
signiﬁcantdifferentiationorintegrationprocesses.Thesigniﬁcant threshold
was set at 0.05/26 using Bonferroni correction for multiple tests across 13
movie clips and two hippocampal pathways.
Hippocampal subﬁeld-based inter-subject functional correlation
(ISFC) analysis
Inter-subject functional correlation was performed to assess the coordina-
tion patterns between each hippocampal subﬁeld and all cortical areas
across individuals during movie viewing49. We applied ISFC analysis rather
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
4


## Page 5

than traditional within-subject functional connectivity for several metho-
dological reasons that are essential to the naturalistic paradigm. First, ISFC
effectivelyﬁltersoutintrinsicneuralﬂuctuations,physiologicalartifacts,and
non-neuronal noise that are speciﬁc to individual subjects but uncorrelated
across participants49,50. This approach substantially improves the signal-to-
noise ratio for detecting stimulus-driven functional coupling between brain
regions during complex naturalistic processing. Second, during movie
viewing,ISFCspeciﬁcallyisolatesbrainactivitypatternsthataretime-locked
Movie stimuli
Semantic category labels
Semantic feature vectors
Semantic similarty matirx/network 
...
...
...
For each subfield and participant
...
...
fMRI pattern similarity matrix/network
fMRI time serise
CA3/2
GC-DG
CA1
"man.n.01" "sit.v.01" "hat.n.01"
"vegetation.n.01" "house.n.01"
"car.n.01" "fence.n.01" "look.v.01"
"stick.n.01" "hold.v.02"
TR 1
... 0 1 1 0 1 1 0 1 0 ...
"male_child.n.01" "girl.n.01" 
"uniform.n.01" "helmet.n.02" 
"racetrack.n.01" "bleachers.n.01"
"fence.n.01" "tree.n.01" "talk.v.02"
"walk.v.01" "sky.n.01" "smile.n.01"
TR n
... 0 1 0 1 1 0 0 1 0 ...
"man.n.01" "land.n.02" "tree.n.01"
"run.v.01" "building.n.01" 
"car.n.01" "chase.v.01" "road.n.01"
TR 2
... 0 0 1 0 0 1 1 1 0 ...
Cosine  similarity
Pattern  similarity
Representational similarity 
Global efficiency
Local efficiency
TR
cos(TR,TR)
corr(TR,TR)
TR
TR
TR
0.2
1.0
TR
TR
-0.2
0.3
0
25
TR
TR
Geodesic distance matrix
 Mean geodesic distance changes
Schaefer 400 parcels
A
B
Individual
behavioral measures
Subfields-cortical 
Inter-subject functional correlation (ISFC)
③predict
② predict
① pearson correlation
pearson correlation
Floyd-Warshall algorithm
C
mediation analyses
-0.04
-0.02
0.04
0.02
0.00
-0.02
-0.01
-0.03
0.01
0.00
0.03
0.02
0.04
DG
CA3
CA1
MDS component 1
MDS component 2
MDS analysis
Hippo. circuit
voxel 1
voxel 2
voxel n
Fig. 1 | Methodological overview of semantic feature and neural representation
analysis within the hippocampal circuit. A Semantic similarity networks. To generate
semantic similarity networks, movie stimuli were split into TRs, each of which was
annotated with independent semantic category labels that provided textual descriptions.
Semantic similarity matrix was calculated using the cosine similarity between the
semantic feature vectors generated from the semantic category model. This resulted in a
semantic similarity network, where nodes represent the movie TRs and edge weights
indicate the semantic similarities between them. B Hippocampal subﬁelds neural simi-
larity network. Pattern-similarity matrix was computed using the Pearson correlation
between voxel time courses for each hippocampal subﬁeld. The neural similarity network
was deﬁned with TRs as nodes and edge weights representing pattern similarities between
TRs. Edge weights were thresholded at the top 20% similarity for network visualization.
Representational similarity analysis was applied to compare the semantic similarity
matrix with pattern-similarity matrices from each subﬁeld; global and local efﬁciency
were assessed and compared between the semantic similarity network and each subﬁeld’s
neural similarity network. C The relationship among hippocampal-cortical inter-subject
functional correlation, geodesic distance changes along the hippocampal circuit, and
individual behavioral measures. The multidimensional scaling (MDS) plot illustrates the
distribution of geodesic distances for each subﬁeld. Speciﬁcally, geodesic distance changes
were assessed by comparing TR-to-TR geodesic distances across hippocampal subﬁelds,
revealing either increased distance (differentiation) or decreased distance (integration)
along the hippocampal circuit.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
5


## Page 6

with the shared external stimulus, thereby capturing the neural responses
directly related to processing the narrative content51,52. This is particularly
important for examining how hippocampal subﬁelds interact with cortical
regions during ongoing narrative comprehension. Third, ISFC has been
demonstrated to reveal network dynamics that remain undetected in tra-
ditional within-subject analyses, particularly regarding memory encoding
and retrieval during naturalistic stimulation52–54.
Speciﬁcally, we applied an fMRI-based parcellation atlas with 400
cortical parcels (200 parcels per hemisphere) to generate whole-brain ISFC
maps for three hippocampal subﬁelds across all movie clips45,46. For each
movie clip, Pearson correlations were calculated between the time series of
each subﬁeld from one participant and those of 400 cortical parcels from
other participants. This resulted in 13 ISFC matrices of size 3 × M × N (with
13 movie clips, 3 hippocampal subﬁelds, M parcels, and N participants).
Correlation coefﬁcients were averaged across participants to obtain the
mean ISFC for each parcel. To assess the statistical signiﬁcance of each
observed ISFC, we performed permutation testing using phase-randomized
surrogatedatathatkeepsthesamepowerspectrumastheoriginalfMRIdata
but will remove any meaningful temporal relationships among time series49.
Foreachsurrogatedata,ISFCmetricswerecomputedinthesamemanneras
for the original fMRI data. This procedure was repeated 1000 times to
generate null distributions. A one-tailed p value was deﬁned as the pro-
portion of the null distribution that exceeded the observed mean ISFC. The
whole-brain p values were corrected for multiple comparisons across all
parcels using the Benjamini-Hochberg procedure (q < 0.05).
To examine the relationship between hippocampal-cortical coordi-
nation patterns and the processes of differentiation and integration in the
hippocampal circuit, we explored the associations between signiﬁcant ISFC
for each subﬁeld-parcel pair and geodesic distance changes from each
hippocampal pathway. Speciﬁcally, we identiﬁed subﬁeld-parcel pairs
showing signiﬁcant ISFC across all movie clips and computed the clip-
averaged ISFC for each subﬁeld-parcel pair. Similarly, we calculated the
mean distance changes for eachparticipant from Mdiff across all movie clips
toobtaintheclip-averaged distancechangesforeachhippocampalpathway.
Then, Pearson correlation was conducted to assess the relationship between
the clip-averaged ISFC (subﬁeld-parcel pairs) and clip-averaged geodesic
distance changes (hippocampal pathways). Finally, we selected the hippo-
campal subﬁeld-parcel pairs and hippocampal pathways demonstrating
statistically signiﬁcant correlations between ISFC values and geodesic dis-
tance changes for subsequent analyses.
Predictive analysis of behavior using hippocampal features
To assess the relationship between hippocampal features and individual
behavioral measures during naturalistic viewing, we performed predictive
linear regression analyses to determine whether: (1) geodesic distance
changes (selected hippocampal pathways), or (2) ISFC values (selected
subﬁeld-parcel pairs) could predict individual behavioral capacities (cog-
nition or emotion scores; see the section “Behavioral data”). These two
predictor types were analyzed separately, eachutilizing leave-half-out cross-
validationforreliability.Speciﬁcally,werandomlysplitparticipantsintotwo
groups: one half was used to train the predictive model, and the other was
used to test the model by predicting their behavioral scores. Prediction
accuracy was assessed using Spearman correlation between predicted
(model-generated) and observed (true) scores. This process was repeated
100 times to evaluate the model robustness to different splits. To determine
the statistical signiﬁcance of prediction accuracies, we generated a null
distribution by randomly shufﬂing behavior scores and re-running the
above analysis 10,000 times. A non-parametric p value for the observed
accuracy was then calculated as follows:
p value ¼
P rnull > median robs




þ 1
nnull þ 1
wherennull = 10,000andmedianðrobsÞ representsthemedianaccuracyofthe
1000 true models.
To investigate potential mechanistic relationships between neural
measures and behavior (Fig. 1C), we examined whether hippocampal-
cortical connectivity mediates the association between representational
geometry changes and behavioral traits, or conversely, whether geodesic
distance transformations mediate connectivity-behavior relationships. We
implementedformalmediationanalysestotestthesecompetinghypotheses,
employing a three-variable path model framework55,56. For each potential
pathway, we systematically tested models where either subﬁeld-parcel ISFC
or hippocampal geodesic distance changes served as the mediator (M)
betweenapredictorvariable(X)andindividualbehavioralperformance(Y).
Using the mediation package in Python, we quantiﬁed: (1) the effect of the
predictoronthemediator(patha);(2)theeffectofthemediatoronbehavior
while controlling for the predictor (path b); (3) the total effect of the pre-
dictor on behavior (path c); and (4) the direct effect of the predictor on
behavior after accounting for the mediator (path c’). The product of coef-
ﬁcients (a × b) represented the mediation effect, which was tested for sig-
niﬁcance using bias-corrected bootstrap CIs with 5000 resamples. The
mediationresult was consideredstatistically signiﬁcantwhen the 95% CIfor
the indirect effect excluded zero.
Voxel count matching across hippocampal subﬁelds
To mitigate the confound of differing voxel counts and temporal signal-to-
noise ratios (tSNRs) across hippocampal subﬁelds, we controlled for the
number of voxels in our analyses. For each participant, we randomly
selected a subset of non-overlapping voxels from each hippocampal sub-
ﬁeld,matchedtothesubﬁeldwiththesmallestvolume.Allkeyanalyseswere
repeated on this voxel-matched subset.
Statistics and reproducibility
Statistical analyses were conducted using Python (version 3.9). Data nor-
mality was assessed prior to hypothesis testing, with non-parametric tests
applied when the assumptions of normal distribution were not met. P
values < 0.05 were considered statistically signiﬁcant unless stated other-
wise. For representational similarity analysis, statistical signiﬁcance was
assessed using non-parametric block permutation tests (with block lengths
varying from 15 to 40 TRs) and phase-randomization tests, in which
observed RSA values were compared to null distributions generated from
1000 random tests. Similarly, for graph-theoretical analyses and subﬁeld-
based ISFC analyses, statistical signiﬁcance was evaluated using phase-
randomization tests (1000 permutations). Comparisons of RSA between
subﬁelds and geodesic distances between hippocampal pathways were
performed using one-sample t-tests and paired t-tests as appropriate, with
Bonferroni correction applied to account for multiple comparisons,
including 3 subﬁelds, 2 pathways, and 13 movie clips (N = 157 participants).
Moreover, whole-brain ISFC p values were corrected using the
Benjamini–Hochberg procedure (q < 0.05). For predictive analyses, leave-
half-out cross-validation was applied with 100 random splits. Statistical
signiﬁcance was determined by comparing observed prediction accuracies
against null distributions generated from 10,000 permutations with shufﬂed
behavioral scores. Mediation analyses employed bias-corrected bootstrap
CIs with 5000 resamples, and mediation effects were signiﬁcant when 95%
CI excluded zero. To ensure reproducibility, group-level noise ceilings were
estimated using split-half analyses with Spearman–Brown correction. Main
analyses were validated using voxel-matched subsets to control for differ-
ences in subﬁeld volumes and tSNR across hippocampal subﬁelds.
Results
Hippocampal subﬁelds encode semantic and topological fea-
tures of movie content
We investigated whether hippocampal subﬁelds’ activity patterns encode
semantic features of the movie narratives. Off-diagonal RSA was performed
by comparing the semantic similarity matrix with fMRI pattern-similarity
matrices (computed for DG, CA3, and CA1 subﬁelds) for eachmovie clip at
the individual level (Fig. 2A). Our results demonstrated robust semantic
encoding across all hippocampal subﬁelds, with RSA values signiﬁcantly
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
6


## Page 7

higher than the block permutation-based null distribution in most movie
clips (p = 0.039, Bonferroni correction; Fig. 2B). The robustness of our
ﬁndings was further conﬁrmed through sensitivity analyses using varying
blocklengthsinpermutationtests(TableS4)andphase-randomizationtests
(Table S5), both of which yielded results broadly consistent with our pri-
mary observations. Moreover, we observed signiﬁcant differences between
subﬁelds: DG showed stronger semantic alignment than CA3 (one-sample
t-test: t156 = 4.29, p < 0.001, Bonferroni correction; Fig. 2C), while CA3
exhibited
weaker
representational
similarity
compared
to
CA1
(t156 = −11.31, p < 0.001, Bonferroni correction; Fig. 2D). The data relevant
to the above analyses are provided inthe supplementary ﬁle,Supplementary
Data 1—Representational similarity analysis.xlsx. These effects remained
consistent in a control analysis utilizing a voxel-matched dataset that con-
trolled for differences in voxel count and tSNR across subﬁelds (Table S6
and Fig. S3).
Previous research has established the hippocampus’s ability to extract
structural regularities from sequential inputs57, prompting us to investigate
whether hippocampal representations during movie viewing mirror the
higher-order topological organization of movie content features. To this
end, we leveraged two widely used graph-theoretical metrics—local efﬁ-
ciency (clustering of interconnected nodes) and global efﬁciency (integra-
tion across distributed nodes)—to assess topological structures of movie
representations.
Our results revealed that movie semantic networks exhibited sig-
niﬁcantly higher local efﬁciency but lower global efﬁciency compared to
random networks (all p < 0.05, Fig. 3). By normalizing these metrics against
their random counterparts, we found that movie semantic networks
displayed characteristics consistent with small-world organization, speciﬁ-
cally at higher density thresholds. The normalized local efﬁciency
(Ereal
local=Erand
local) consistently exceeded 1 across thresholds, while the normal-
izedglobalefﬁciency(Ereal
glob=Erand
glob )approached1onlyathigherdensitylevels
(speciﬁcally when sparsity thresholds ranged from 0.15 to 0.2, Fig. 3).
In contrast, neural representation networks within each hippo-
campal subﬁeld exhibited a different pattern of global efﬁciency com-
pared to semantic networks. While semantic networks demonstrated
lower global efﬁciency than random networks, hippocampal repre-
sentation networks showed global efﬁciency values comparable to or
slightly higher than their random counterparts. Both network types
exhibited higher local efﬁciency compared to matched random networks.
This pattern was reﬂected in their small-world metrics: all subﬁeld
representation
networks
exhibited
normalized
local
efﬁciency
(Ereal
local=Erand
local) values greater than 1 across thresholds, with normalized
global efﬁciency (Ereal
glob=Erand
glob ) consistently closer to or slightly above 1
across thresholds (Fig. 3). These ﬁndings indicate that both semantic and
neural representation networks demonstrate small-world properties,
though with different patterns of global efﬁciency that may reﬂect their
different functional roles in information processing. The data relevant to
the above analyses are provided in the supplementary ﬁle, Supplementary
Data 2—Graph theoretical analysis.xlsx.
Transformation of network representations along the hippo-
campal circuit
Having demonstrated that hippocampal subﬁelds can encode the higher-
order topological structure of movie stimuli, with the capacity in facilitating
A
B
C
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
12
13
movie clips
RSA (Pearson r)
DG
0.0
0.1
*
*
*
*
*
*
ns
*
*
*
ns
*
*
RSA (Pearson r)
CA3
*
*
*
*
*
*
ns
*
*
*
ns
*
*
0.0
0.1
RSA (Pearson r)
CA1
*
*
*
*
*
*
ns
*
*
*
ns
*
*
0.0
0.1
CA3
CA1
Diff
***
***
 Clip-averaged RSA (Pearson r)
-0.02
0.00
0.02
0.04
0.06
-0.02
0.00
0.02
0.04
0.06
DG
CA3
Diff
 Clip-averaged RSA (Pearson r)
***
***
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
12
13
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
12
13
D
Movie semantic features
similarity matrix 
TR
TR
Hippocampal subfield fMRI
similarity matrix
TR
TR
Pearson’s r
K
K
Fig. 2 | Representational similarity analysis between movie semantic features and
hippocampal subﬁelds activation patterns during movie viewing. A Schematic of
the off-diagonal RSA, illustrating the Pearson correlation between the movie
semantic features similarity matrix (from movie clip 1, top 50 TRs) and the fMRI
neural similarity matrix of the CA1 subﬁeld (from participant 100610, movie clip 1,
top 50 TRs). Gray-masked regions indicate the excluded diagonal band (K = 7 TRs).
Pearson correlation was computed between unmasked, off-diagonal elements to
quantify semantic-neural correspondence. B Distribution of RSA values for hip-
pocampal subﬁelds across movie clips. Each dot represents an individual partici-
pant’s RSA correlation for DG (blue), CA3 (green), and CA1 (orange). Red lines
indicate the mean RSA across all participants (N = 157). The boxplots depict null
distributions generated through 1000 block permutations (block length = 10 TRs)
from all participants for each movie clip and subﬁeld. Statistical signiﬁcance was
assessed by comparing the observed mean RSA value to the permutation-based null
distribution using one-tailed tests. The signiﬁcance threshold was set at p < 0.05
following Bonferroni correction for the 39 tests across 13 movie clips and 3 hip-
pocampal subﬁelds. ns: p > 0.05; *p < 0.05, Bonferroni correction. Representational
similarity changes in the hippocampal circuit, revealing distinct patterns along the
(C) DG-CA3 and D CA3-CA1 pathways. Hollow circles represent individual par-
ticipants’ RSA averaged across movie clips (N = 157), and blue violin plots show the
distribution of representational similarity differences for hippocampal pathways.
Statistical signiﬁcance reﬂects differences from 0 based on two-tailed randomization
tests. ***P < 0.001. Bonferroni correction.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
7


## Page 8

efﬁcient global integration, we next investigated how these structured
representations are progressively transformed along the hippocampal circuit.
To quantify the representational transformations between subﬁelds,
we employed geodesic distance analysis, a recently developed and robust
measure of topological representational differences29,30. By calculating the
geometric distances between BOLD activation patterns evoked by pairs of
movie frames, we evaluated how structured representations were differen-
tially separated or integrated as information traverses the hippocampal
circuit from DG through CA3 to CA1. This approach allowed us to directly
examine the computationaltransformationsthat structured representations
undergo at each processing stage of the hippocampal circuit (DG →
CA3 →CA1). Our analyses revealed distinct transformation patterns
between successive processing stages. Between DG and CA3, we observed
thatboththeproportionofnodepairsexhibitingincreaseddistancesandthe
mean geodesic distance were signiﬁcantly greater in CA3 relative to DG
across movie clips (all p < 0.001, Bonferroni-corrected; Fig. 4A). This indi-
cates enhanced representational differentiation as information propagates
from DG to CA3, consistent with pattern separation functions. Between
CA3 and CA1, however, we found the opposite pattern: signiﬁcantly more
node pairs showed decreased rather thanincreased distances,with the mean
geodesic distance signiﬁcantly decreasing in CA3 compared to CA1 across
clips (all p < 0.001, Bonferroni correction; Fig. 4B). This systematic reduc-
tion in representational distance suggests that CA1 integrates separated
information from CA3 into more cohesive representations. These trans-
formation patterns remained consistent in a control analysis utilizing a
voxel-matched dataset (Fig. S4). The data relevant to the above analyses are
provided in the supplementary ﬁle, Supplementary Data 3—Geodesic dis-
tance of representations.xlsx.
Hippocampal-cortical interactions support hippocampal
integration
To elucidate the functional architecture of hippocampal-cortical interac-
tions during naturalistic processing, we implemented ISFC analysis to
characterize coupling patterns between individual hippocampal subﬁelds
and 400 cortical ROIs during movie viewing. Our analysis revealed that
different hippocampal subﬁelds demonstrate similar ISFC patterns with
distinct cortical networks. Speciﬁcally, we found robust connectivity
between hippocampal subﬁelds and several key cortical regions, including
the RSC, PHC, inferior parietal lobule, medial and dorsolateral prefrontal
cortex, and striate/extra-striate visual regions (Fig. 5A and Table S7).
We further investigated whether these subﬁeld-cortical ISFC patterns
covaried with representational distance changes along the hippocampal
circuitry. No signiﬁcant correlations were found between subﬁeld-cortical
ISFC and the mean geodesic distance changes along the DG-CA3 pathway
(all p > 0.05, uncorrected; Table S8). We observed robust correlations
between CA3-CA1 representational transformations and ISFC involving a
0
0.2
0.4
0.6
0.8
1.0
0
5
10
15
20
0.1
0.2
0.3
0.4
0.5
0
0
5
10
15
20
0
5
10
15
20
0.1
0.2
0.3
0.4
0.5
0
0
5
10
15
20
0.1
0.2
0.3
0.4
0.5
0
Local Efficiency
Movie Semantic Networks
DG Networks
CA3 Networks
CA1 Networks
0.1
0.2
0.3
0.4
0.5
0
0
5
10
15
20
0
5
10
15
20
0
5
10
15
20
0
5
10
15
20
0.1
0.2
0.3
0.4
0.5
0
0.1
0.2
0.3
0.4
0.5
0
0.1
0.2
0.3
0.4
0.5
0
Global Efficiency
2
1
3
4
0
2
1
3
4
0
2
1
3
4
0
10
20
30
40
50
0
60
0
5
10
15
20
0
5
10
15
20
0
5
10
15
20
0
5
10
15
20
Normalized Efficiency
Sparsity thresholds (%)
Sparsity thresholds (%)
Sparsity thresholds (%)
Sparsity thresholds (%)
2
1
3
4
0
Local Efficiency
Global Efficiency
Fig. 3 | Network efﬁciency reveals small-world properties in semantic similarity
and hippocampal pattern-similarity networks. Network efﬁciency of movie
semantic similarity networks (ﬁrst column) and subﬁeld DG (second column), CA3
(third column), and CA1 (fourth column) pattern-similarity networks under a range
of sparsity thresholds (top 20% similarity). Real networks (solid lines), including
individual movie clip (thin) and clip-averaged networks (bold), exhibited higher
local efﬁciency (top panel, red) and lower global efﬁciency (middle panel, blue)
compared to their corresponding 1000 permuted null networks (dotted lines). In
subﬁeld networks, the network efﬁciency values in each movie clip were averaged
across all participants (N = 157). Small-worldness analysis (bottom panel) demon-
strated clip-averaged normalized local efﬁciency (red bold lines) and normalized
global efﬁciency (blue bold lines) relative to 1000 permuted networks. Error bars
indicate the standard errors of the mean across 13 movie clips.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
8


## Page 9

subset of cortical regions with CA1 (all p < 0.05, uncorrected; Fig. 5B and
Table S8). Speciﬁcally, reduced geodesic distances from CA3 to CA1
(reﬂecting enhanced pattern integration) were correlated with increased
ISFC between CA1 and a network of regions including the RSC, PHC, and
extra-striate visual cortex. The data relevant to the above analyses are pro-
vided in the supplementary ﬁle, Supplementary Data 4—ISFC analysis.xlsx.
CA1-RSC connectivity mediates individual cognition through
hippocampal integration
Having established the relationship between hippocampal network repre-
sentational integration and hippocampal-cortical interactions, we sought to
examine how these factors contribute to individual behavioral traits. We
employedgeodesicdistancechangesalongtheCA3-CA1pathwaytopredict
individualcognitionandemotionscoresseparately.Ourcorrelationanalysis
revealed an association between individual differences in cognition scores
and changes in mean geodesic distance along the CA3-CA1 pathway
(median r = 0.21, permutation-based p = 0.031, uncorrected; Fig. 6A). This
correlation indicates that greater decreases in mean geodesic distance
(indicating stronger pattern integration) were associated with higher cog-
nition scores, though this relationship would not reach signiﬁcance under
Bonferroni correction for multiple comparisons (required α = 0.025).
Moreover, emotion scores showed no correlation with hippocampal
representational integration measures (r = −0.06,
p = 0.677, uncor-
rected; Fig. 6A).
Furthermore, we sought to predict individual cognition and emo-
tion scores based on hippocampal-cortical ISFC, focusing on the seven
identiﬁed CA1-cortical pairs from the previous section (Table S8). The
results revealed that individual cognition scores were predicted by ISFC
between CA1 and the retrosplenial regions (left Rsp1: median r = 0.22,
p = 0.024; left Rsp2: median r = 0.26, p = 0.017; right Rsp1: r = 0.23,
p = 0.026; right Rsp2: r = 0.22, p = 0.026; uncorrected; Fig. 6B). Stronger
CA1-retrosplenial connectivity was associated with better cognitive
scores, indicating that enhanced functional coupling between CA1 and
RSC
supports
individual
cognitive
performance.
None
of
the
hippocampal-cortical ISFC pairs were found to predict emotion scores
(all p > 0.05, uncorrected; Fig. S5).
Given the extensive connectivity of the RSC with both the hippo-
campus and cortical areas, we hypothesized that the connectivity between
CA1 and RSC may serve as a pivotal mediator linking network integration
within the CA3-CA1 pathway to cognitive outcomes. This suggests that
functional interaction between CA1 and the RSC (encompassing bilateral
Rsp1 and Rsp2) could facilitate the transfer and integration of hippocampal
network representations into distributed cortical networks, thereby sup-
porting cognitive functions. To test this hypothesis, we performed a med-
iation analysis with geodesic distance changes along the CA3-CA1 pathway
as the predictor, cognition scores as the outcome, and CA1-RSC con-
nectivity as the mediator.
The mediation analysis conﬁrmed a signiﬁcant mediation effect
(p(a × b) = 0.006,95%CI = [−365.9,−30.9])withthetotaleffect(p(c) = 0.018,
95% CI = [−1203.6, −107.9]), revealing that representational changes from
CA3 to CA1 contribute to cognition scores by enhancing connectivity
between CA1 and the RSC (Fig. 6C and Table 2). Accounting for the
mediator, the direct effect became non-signiﬁcant (p(c’) = 0.078, 95% CI =
[−1007.9, 60.7]; Fig. 6C and Table 2), indicating that CA1-RSC
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
12
13
Movie clip
100
80
60
40
20
0
***
***
***
***
***
***
***
***
***
***
***
***
***
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
12
13
Node pairs(%)
A
DG-CA3
CA3-CA1
B
Node pairs(%)
Decreased distance
Increased distance
100
80
60
40
20
0
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
12
13
Mean geodesic distance change
0
-2
-4
8
6
4
2
+
e-3
-4
-6
-8
4
2
0
-2
+
e-3
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
12
13
Movie clip
Mean geodesic distance change
Movie clip
Movie clip
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
***
Fig. 4 | Differentiation and integration processes of geodesic distance repre-
sentations within hippocampal pathways across movie clips. A DG-CA3 pathway.
B CA3-CA1 pathway. The left y-axis represents the percentage of node pairs with
increased (pink) and decreased (violet) geodesic distances in the geodesic distance
difference matrix, and the x-axis represents the movie clips. Each dot represents an
individual participant. The right panel exhibited the distribution of mean geodesic
distance changes across all participants (N = 157) within the hippocampal pathways.
The x-axis represents the mean geodesic distance changes in the geodesic distance
difference matrix, and the y-axis represents the movie clips. The signiﬁcant threshold
was set at p < 0.05 following Bonferroni correction for the 26 tests across 13 movie
clips and 2 hippocampal pathways. ***P < 0.001. Bonferroni correction.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
9


## Page 10

connectivity mediates the relationship between hippocampal pattern inte-
gration and cognition scores. Furthermore, the reverse mediation model,
which examined changes in CA3-CA1 geodesic distance as a mediator for
the effects of CA1-RSC connectivity on cognition scores, did not reach
statistical signiﬁcance (p = 0.094, 95% CI = [−0.1, 3.5]), supporting the
directionality of our proposed pathway (Table 2). Notably, connectivity
between CA1 and individual retrosplenial parcels (bilateral Rsp1 and Rsp2)
similarly revealed signiﬁcant mediation effects (p(a × b) < 0.05; Table S9).
These ﬁndings suggest that CA1-RSC connectivity, whether analyzed
separately or combined, is vital for understanding how the hippocampal
network inﬂuences individual cognitive behavior. The data relevant to the
above analyses are provided in the supplementary ﬁle, Supplementary
Data 5—Predictive analysis.xlsx.
These mediation effects remained consistent in a control analysis uti-
lizing a voxel-matched dataset. In this analysis, near-signiﬁcant mediation
effects were observed for connectivity between CA1 and the individual
retrosplenial parcels (bilateral Rsp1 and Rsp2), approaching signiﬁcance
(p(a × b) < 0.05, Table S10).
A
DG-Cortex ISFC
DG-Cortex ISFC
CA3
CA3-Cortex
-Cortex ISFC
 ISFC
CA1
CA1-Cortex
-Cortex ISFC
 ISFC
0.12
-0.12
r
B
Geodesic Distance Change
0.1
0.2
0.0
ISFC value
0.1
0.2
0.0
0.1
0.2
0.0
-5
-4
-3
-2 10-3
+
-5
-4
-3
-2 10-3
+
-5
-4
-3
-2 10-3
+
0.1
0.2
0.0
ISFC value
0.1
0.2
0.0
-5
-4
-3
-2 10-3
+
-5
-4
-3
-2 10-3
+
0.1
0.2
0.0
ISFC value
0.1
0.2
0.0
-5
-4
-3
-2 10-3
+
-5
-4
-3
-2 10-3
+
-16
-8
0
8
16
24
-16
-8
0
8
16
24
-16
-8
0
8
16
24
LH Rsp1
LH Rsp3
RH Rsp2
LH Rsp2
LH PHC3
RH ExStrInf2
RH Rsp1
r = -0.22**
r = -0.21**
r = -0.18*
r = -0.19*
r = -0.20*
r = -0.17*
r = -0.20*
Fig. 5 | Hippocampal-cortical connectivity patterns and their association with
pathway dynamics. A Whole-brain map exhibiting signiﬁcant ISFC with hippo-
campal subﬁelds (DG, CA3, and CA1) across all movie clips. ISFC values were
calculated between each subﬁeld and 400 cortical parcels from the Schaefer atlas for
each movie clip. Color intensity represents participant-averaged ISFC strength for
cortical parcels that demonstrated consistent signiﬁcance (FDR-corrected in each
movie clip). B Correlation between geodesic distance changes (x-axis) within the
CA3-CA1 pathway and ISFC values (y-axis) of the CA1-coupled cortical parcels is
shown. Each dot represents values averaged across all movie clips for an individual
participant (N = 157). *P < 0.05, **P < 0.01.
B
A
Spearman r(obs, pred)
Spearman r(obs, pred)
ISFC
CA1-RSC connectivity
Cognitive 
scores
(CS)
Decreased
geodesic
distance
ab=0.006**
c’=0.078
c=0.018*
a=0.008**
b=0.003**
C
LH Rsp1
RH Rsp1
LH Rsp2
RH Rsp2
*
*
*
*
Cognition
Emotion
ns
*
-0.4
-0.2
0.0
0.2
0.4
-0.4
-0.2
0.0
0.2
0.4
Mediation model
Fig. 6 | CA1-retrosplenial connectivity mediates the relationship between hip-
pocampal integration and cognitive performance. Prediction of behavior based on
(A) mean geodesic distance changes within the CA3-CA1 pathway and B CA1-
parcels ISFC. Accuracy was measured using Spearman correlation between pre-
dicted (model-generated) and observed (true) scores (y-axis). Each dot represents
results from 100 iterations of leave-half-out cross-validation. Light gray boxen plots
illustrate the null distribution from 10,000 permutations. The red line denotes
median accuracy for true models. Signiﬁcance was assessed by comparing true
model medians to the null distribution. ns: P > 0.05; *uncorrected P < 0.05.
C Mediation model for the relationship among CA1-retrosplenial connectivity,
geodesic distance changes within the CA3-CA1 pathway, and individual cognition
scores. In this model, CA1-RSC connectivity is a complete mediator of the rela-
tionship between representational integration in the CA3-CA1 pathway and indi-
vidual cognition scores. Path a is the relationship between the predictor and the
mediator. Path b is the relationship between the mediator and the outcome. The total
effect (path c) is the relationship between the predictor and the outcome. The direct
effect (path c’) is the relationship between the predictor and the outcome, controlling
for the mediator. Path a × b is the mediation effect. *P < 0.05; **P < 0.01.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
10


## Page 11

Discussion
Our results revealed that all hippocampal subﬁelds construct structured
representations of complex experiences, encoding both semantic features
and small-world topological properties extracted from dynamic movie sti-
muli. This representational process leverages functional specialization
within the hippocampal circuit: the DG-CA3 pathway supports repre-
sentational differentiation, while the CA3-CA1 pathway facilitates the
integration process of network distance representations. Furthermore, the
efﬁciency of this CA3-CA1 integration correlates positively with stronger
functional coupling between CA1 and key cortical regions, particularly the
RSC, PHC, and extra-striate visual processing areas. Notably, mediation
analyses identiﬁed CA1-retrosplenial connectivity as a key mechanism
bridging these processes. This speciﬁc pathway statistically mediates the
relationship betweenthe efﬁciencyof hippocampalnetwork integrationand
individual differences in cognition scores. Collectively, these ﬁndings
demonstrate that the hippocampus maps structured network representa-
tions of elements in natural environments through specialized representa-
tional differentiation and integration processes within the hippocampal
circuit. Moreover, hippocampal-retrosplenial interactions serve as a key
mediator, bridging hippocampal network integration representations and
individual cognitive performance, providing a mechanistic explanation for
individual cognitive variability in real-world information processing.
We applied RSA to determine whether the activation patterns of
hippocampal subﬁelds could reﬂect the whole movie’s semantic structure
during movie encoding. The results revealed that all subﬁelds within the
hippocampal circuit signiﬁcantly represented movie semantic features. This
aligns with the hippocampus’s established role in integrating multimodal
contextual information to construct coherent memory representations51,58.
Notably, this representational capacity transcends simple associative
encoding and reﬂects the hippocampus’s fundamental role in generating
cognitive maps —organized neural representations that capture relational
structures across both spatial and non-spatial domains2–4. Recent evidence
reveals that this map-like organizational capacity extends to extracting
structural information from sequential inputs4,7,8. For instance, Lee et al.
observed that events with stronger semantic connections elicited greater
hippocampal responses during movie encoding, suggesting that the hip-
pocampusmapsrelationshipsbetweennarrativeeventstofacilitatememory
formation16. Building upon this cognitive mapping framework, we con-
structed network representations of movie stimuli and analyzed their efﬁ-
ciency properties. Rather than conducting whole-brain analyses with events
as nodes, we focused on hippocampal subﬁelds and utilized ﬁner temporal
resolution (TRs) as nodes to build movie network representations. Our
results showed that both the semantic similarity network and the fMRI
pattern-similarity networks exhibited high efﬁciency in local processing
across all subﬁelds. Notably, hippocampal representations showed superior
globalprocessingefﬁciency,suggestingthathippocampalsubﬁeldsintegrate
individual semantic elements into coherent map-like structures that facil-
itate efﬁcient information processing across the entire narrative.
Hippocampal computational processes of pattern separation and
patterncompletionarefundamentaltotheformationofthecognitivemap26.
Pattern separation transforms similar inputs into distinct neural repre-
sentations, enabling cognitive maps to discriminate and represent closely
related but different elements in the environment. Conversely, pattern
completion reconstructs complete representations from partial inputs,
facilitating navigation through cognitive maps despite incomplete infor-
mation.Intheclassicalview,patternseparationisprimarilyattributed to the
DG subﬁeld itself 59,60, while pattern completion is associated with the
recurrent collateral networks within the CA3 subﬁeld61,62. However, our
ﬁndings reveal a more nuanced, circuit-level understanding of these pro-
cesses during naturalistic information processing. By calculating shortest
path distances between all nodes in our network representations, we
assessed the manifestation of these hippocampal computational processes
along the canonical circuit (DG-CA3-CA1). Speciﬁcally, we observed
increased network distance representation in the DG-CA3 pathway,
demonstrating enhanced differentiation of similar inputs as information
ﬂows from DG to CA3. Conversely, we found decreased network distances
in the CA3-CA1 pathway, indicating integration of related elements as
information progresses from CA3 to CA1 subﬁeld. These ﬁndings extend
thetraditionalsubﬁeld-speciﬁcmodeltoapathway-basedframeworkwhere
pattern separation and pattern completion emerge from the transformation
of information between subﬁelds. This circuit-level perspective aligns with
recent anatomical and physiological evidence. While the sparse coding
properties of DG contribute to pattern separation, the sparse yet powerful
synaptic connections form the DG-CA3 mossy ﬁber pathway may further
enhance this differentiation process. Similarly, while the recurrent col-
laterals of CA3 support pattern completion within that subﬁeld, the precise
transformation occurring as information transfers from CA3 to CA1
appears to further integrate related representations. Additionally, our use of
complex naturalistic stimuli may reveal aspects of circuit function not
apparent in the simpliﬁed experimental paradigms typically used to estab-
lish the traditional view.
This pathway-based perspective may inform our understanding of
cognitive map formation. Recent literature demonstrates that effective
cognitive mapping necessitates both differentiation of similar elements (via
pattern separation) and integration of related information (via pattern
completion) in a balanced, coordinated manner across the entire hippo-
campal circuit. For example, Knierim et al. proposed that disruptions to this
circuit-level coordination impair the ability to generate and utilize cognitive
maps, even when individual hippocampal subﬁelds appear to function
normally63. Our network analysis during naturalistic viewing extends these
ﬁndings by elucidating speciﬁc pathway contributions—pattern separation
along the DG-CA3 pathway may create distinct representational nodes
within the cognitive maps, while pattern completion along the CA3-CA1
pathway may help to establish the relational links among these nodes.
Episodic memory formation relies on dynamic interactions between
the hippocampus and neocortex. Speciﬁcally, hippocampal-cortical con-
nectivity patterns during memory processing are signiﬁcantly enhanced,
particularly with the entorhinal cortex, temporal pole, orbitofrontal, para-
hippocampal, and RSC, parietal cortex, precuneus, and prefrontal
cortex64–67. Similarly, in our subﬁeld-based ISFC analysis, we observed sig-
niﬁcant connectivity between hippocampal subﬁelds and neocortical
regions—includingthePHC,RSC,medialprefrontalcortex,inferiorparietal
lobule, and orbitofrontal cortex—despite subtle differences among sub-
ﬁelds. This hippocampal-cortical integration process plays a pivotal role in
processing narrative content. Empirical research reveals that hippocampal-
cortical interactions facilitate narrative information integration across
Table 2 | Mediation results for the relationship between CA1-
RSC connectivity, geodesic distance changes along the CA3-
CA1 pathway, and individual cognition scores (CS; N = 157)
Model path
Estimate
95% CI
p value
Mediator: CA1-RSC
Total effect:
direct + mediation effects
−659.4
[−1203.6,
−107.9]
0.018
Direct effect: distance→CS
−483.1
[−1007.9, 60.7]
0.078
Mediation effect:
distance→CA1-RSC→CS
−176.4
[−365.9, −30.9]
0.006
Mediator: geodesic distance change
Total effect:
direct + mediation effects
11.8
[5.0, 18.1]
0.001
Direct effect: CA1-RSC→CS
10.5
[3.7, 17.0]
0.004
Mediation effect: CA1-
RSC→distance→CS
1.3
[−0.1, 3.5]
0.094
The total effect represents the relationship between the predictor and the outcome. The direct effect
represents the relationship between the predictor and the outcome, controlling for the mediator. The
mediation effect indicates the difference between the total and direct effect. An effect is statistically
signiﬁcant if the 95% bias-corrected conﬁdence interval (CI) does not include 0.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
11


## Page 12

movie segments, particularly involving the RSC, medial prefrontal cortex,
and posterior cingulate cortex32. Notably, the ISFC between hippocampus
and medial prefrontal cortex exhibited a strong correlation with the
“storyline effect,” where overlapping narrative components trigger the
reinstatement of related event representations68. Furthermore, greater ISFC
between hippocampus and posterior medial cortex correlates signiﬁcantly
with higher event centrality, which in turn predicts more robust and precise
memory recall16. These ﬁndings highlight the integral role of the coordi-
natedhippocampal-corticalinteractions inthedynamicencodingand recall
of interconnected representations within naturalistic contexts. Importantly,
our analysis revealed that greater ISFC associated with CA1 positively
correlated with the distance integration process in the CA3-CA1 pathway,
but not with distance separation within the DG-CA3 pathway. This func-
tional dissociation indicates that the pattern integration process speciﬁcally
supports hippocampal-cortical interactions, while the pattern separation
mechanismmayoperatemoreindependentlywithinhippocampalcircuitry.
Such pathway-speciﬁc organization provides a mechanistic explanation for
how these integrated cognitive maps are constructed within the hippo-
campus and subsequently shared across distributed cortical networks dur-
ing complex real-world experiences.
Our study investigated the relationship between hippocampal
differentiation-integration processes and hippocampal-cortical interac-
tions, with a focused examination of how these mechanisms relate to
individual differences in behavioral performance. We identiﬁed two neural
predictors: (1) network distance integration in the CA3-CA1 pathway, and
(2) connectivity between the RSC and CA1, both of which predicted cog-
nition scores, but not emotion measures (Fig. 6A, B). The observation of
CA3-CA1 integration effects reﬁnes the understanding of hippocampal
pathway-speciﬁc functional specialization, suggesting that individual dif-
ferences in hippocampal integration efﬁciency may contribute to cognitive
ﬂexibility. Moreover, the hippocampus and RSC have been implicated in
supporting the path integration process, the continuous updating of spatial
position and orientation during navigation69–72. Beyond spatial cognition,
these brain regions are involved in episodic memory, autobiographical
memory, scene perception, and social cognition73–75. Moreover, the
hippocampal-retrosplenialinteractionsmediateessentialmemoryencoding
and consolidation processes76–78, with sleep-associated CA1-RSC coordi-
nation particularly important for spatial memory integration79. Empirical
research reveals that hippocampal-retrosplenial connectivity declines with
age, with connectivity changes in young adults closely linked to memory
performance80,81. This converging evidence suggests that the CA1-RSC
connectivity may serve as a potential predictor of individual cognitive dif-
ferences. Further, our mediation analysis revealed that while both hippo-
campal integration effects and CA1-RSC connectivity patterns respectively
predict individual cognitive performance, CA1-RSC connectivity speciﬁ-
cally mediates the effect of hippocampal integration on cognitive outcomes.
These ﬁndings suggest a mechanistic pathway: network integration pro-
cesses along the CA3-CA1 pathway improve cognitive performance by
strengthening CA1-RSC connectivity, which serves as the essential link
translating hippocampal integration capabilities into individual cognitive
differences. The hippocampus-retrosplenial system, as a pivotal neural
architecture, may support contextual memory representation through
information processing within the hippocampal circuit74,82. This pathway
providesinsightintohownaturalistic cognitivemapsconstructedwithinthe
hippocampalcircuit are communicated to corticalregionstosupporthigher
cognitive functions.
Our study has several limitations. Firstly, a proper segmentation of
hippocampal subﬁelds is crucial to prevent misattribution and spurious
results. In this study, we made several efforts to improve the reliability of
hippocampal segmentation: (i) we applied multispectral information from
both T1- and T2-weighted images to enhance the segmentation reliability44;
(ii) visual inspection of segmentation results was carefully conducted.
However, hippocampal subﬁelds segmentation can be challenging and
prone to potential disagreement between different tools and anatomists.
Moreover, despite the use of the HCP 7T dataset, the resolution (1.6 mm3)
was still not optimal, especially for differentiating DG from CA3. Future
studiesusingfMRIdatawithhigherresolutionandalternativesegmentation
tools83,84 are needed to validate the current results. The second limitation is
that we did not consider the entorhinal cortex, a key brain structure that
plays a crucial role in cognitive map formation85. The structured activity
patterns within the entorhinal cortex are intimately linked to the endo-
genous recruitment of cognitive maps during mental navigation86. Future
investigations should explore the function of the hippocampal-entorhinal
system in facilitating the differentiation and integration of memoriesduring
naturalistic experiences. Thirdly, participants were not asked if they had
seen any of the ﬁlms previously. Many of them may have seen these ﬁlms in
full before the scanning session, which could help them place the short
movie clips within a broader context and evoke richer mental representa-
tions compared to unfamiliar ﬁlms. Future studies should incorporate this
information to help investigate and control these effects. Moreover, in our
study, cognitive maps primarily reﬂect the representational differentiation
and integration of semantic features derived from movie stimuli. However,
we recognize that cognitive maps could also encompass a broader array of
representations, including the visual features of the ﬁlms and the social
relationships among characters. Future research should investigate the
integration of semantic models with these additional dimensions to achieve
a more comprehensive understanding of the multifaceted nature of cogni-
tive maps. Notwithstanding these limitations, our ﬁndings provide
empirical evidence for incorporating naturalistic paradigms when exam-
ining complex hippocampal-behavior relationships.
In conclusion, we explored how hippocampal function relates to
individual behavioral traits during naturalistic stimuli. We demonstrated
that hippocampal subﬁelds can represent the semantic features and their
relationships using both representational similarity analysis and graph-
theoretical analysis. Our ﬁndings show that the hippocampus simulta-
neously engages in representational differentiation and integration pro-
cesses during continuous stimuli, with hippocampal distance integration
capacity positively correlating with hippocampal-cortical connectivity
strength.
Moreover,
while
both
representational
integration
and
hippocampal-cortical connectivity predicted cognitive scores, the med-
iation analysis demonstrated that hippocampal-cortical connectivity
mediated the relationship between representational integration and
individual cognitive performance. These ﬁndings advance our under-
standing of hippocampal-cortical interactions in supporting memory
formation during complex, real-world-like experiences. The proposed
model not only provides a framework for studying hippocampal cogni-
tive function in naturalistic contexts but also has potential implications
for enhancing memory in daily life and developing interventions for
memory-related clinical conditions.
Data availability
Neuroimaging data analyzed in this study were obtained from the Human
Connectome Project33. All preprocessed anatomical and functional MRI
data, movie semantic category features, and raw behavioral dataare publicly
available on the HCP ConnectomeDB database for download to anyone
agreeing to the Open Access data use terms (https://db.humanconnectome.
org/). Behavioral PC1 scores for each participant derived from PCA of
cognitive and emotional domains, as provided by Finn et al.34 (GitHub -
esﬁnn/movie_cpm). Data for Figs. 2–6 are available in Supplementary
Data 1–5 ﬁles.
Code availability
Segmentation of hippocampal subﬁelds was automatically performed using
the Freesurfer v7.1.1 (https://surfer.nmr.mgh.harvard.edu/); the “FS60” tem-
plate from the segmentation of the hippocampal subﬁelds and nuclei of the
amygdala (v21, cross-sectional and longitudinal) was chosen to obtain com-
plete segmentation results (HippocampalSubﬁeldsAndNucleiOfAmygdala -
Free Surfer Wiki); Functional MRI data analyses were conducted using
Python scripts (version 3.9). All analyzed codes are available from the cor-
responding author on reasonable request.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
12


## Page 13

Received: 26 May 2025; Accepted: 8 January 2026;
References
1.
Tolman, E. C. Cognitive maps in rats and men. Psychol. Rev. 55,
189–208 (1948).
2.
Epstein, R. A. et al. The cognitive map in humans: spatial navigation
and beyond. Nat. Neurosci. 20, 1504–1513 (2017).
3.
Behrens, T. E. J. et al. What is a cognitive map? Organizing knowledge
for ﬂexible behavior. Neuron 100, 490–509 (2018).
4.
Peer, M. et al. Structuring knowledge with cognitive maps and
cognitive graphs. Trends Cogn. Sci. 25, 37–54 (2021).
5.
Braun, U. et al. Dynamic reconﬁguration of frontal brain networks
during executive cognition in humans. Proc. Natl. Acad. Sci. USA 112,
11678–11683 (2015).
6.
Lynn, C. W. et al. Abstract representations of events arise from mental
errors in learning and memory. Nat. Commun. 11, 2313 (2020).
7.
Lynn, C. W. & Bassett, D. S. How humans learn and represent
networks. Proc. Natl. Acad. Sci. USA 117, 29407–29415 (2020).
8.
Qian, W. et al. Optimizing the human learnability of abstract
network representations. Proc. Natl. Acad. Sci. USA 119,
e2121338119 (2022).
9.
Tavares, R. M. et al. A map for social navigation in the human brain.
Neuron 87, 231–243 (2015).
10. Milivojevic, B. et al. Coding of event nodes and narrative context in the
hippocampus. J. Neurosci. 36, 12412–12424 (2016).
11. Aronov, D., Nevers, R. & Tank, D. W. Mapping of a non-spatial
dimension by the hippocampal-entorhinal circuit. Nature 543,
719–722 (2017).
12. Theves, S. et al. Category boundaries modulate memory in a place-
cell-like manner. Curr. Biol. 34, 5546–5553.e5543 (2024).
13. Li, S. et al. Predictable navigation through spontaneous brain states
with cognitive-map-like representations. Prog. Neurobiol. 233,
102570 (2024).
14. Sonkusare, S., Breakspear, M. & Guo, C. Naturalistic stimuli in
neuroscience: critically acclaimed. Trends Cogn. Sci. 23, 699–714
(2019).
15. Simony, E. & Chang, C. Analysis of stimulus-induced brain dynamics
during naturalistic paradigms. Neuroimage 216, 116461 (2020).
16. Lee, H. & Chen, J. Predicting memory from the network structure of
naturalistic events. Nat. Commun. 13, 4235 (2022).
17. Dalton, M. A. et al. Segmenting subregions of the human
hippocampus on structural magnetic resonance image scans:
an illustrated tutorial. Brain Neurosci. Adv. 1, 2398212817701448
(2017).
18. Fogwe, L. A., Reddy, V. & Mesﬁn, F. B. Neuroanatomy, Hippocampus
(StatPearls, 2023).
19. O’reilly, R. C. & Mcclelland, J. L. Hippocampal conjunctive encoding,
storage, and recall: avoiding a trade-off. Hippocampus 4, 661–682
(1994).
20. Leutgeb, J. K. et al. Pattern separation in the dentate gyrus and CA3 of
the hippocampus. Science 315, 961–966 (2007).
21. Yassa, M. A. & Stark, C. E. Pattern separation in the hippocampus.
Trends Neurosci. 34, 515–525 (2011).
22. Rolls, E. T. Pattern separation, completion, and categorisation in the
hippocampus and neocortex. Neurobiol. Learn Mem. 129, 4–28
(2016).
23. Marr, D. Simple memory: a theory for archicortex. Philos. Trans. R.
Soc. Lond. B Biol. Sci. 262, 23–81 (1971).
24. Binte Mohd Ikhsan, S. N. et al. EPS mid-career prize 2018: Inference
within episodic memory reﬂects pattern completion. Q J. Exp.
Psychol. 73, 2047–2070 (2020).
25. Sun, L. et al. Pattern separation and pattern completion within the
hippocampal circuit during naturalistic stimuli. Hum. Brain Mapp. 46,
e70150 (2025).
26. Fernandez, C. et al. Representational integration and differentiation in
the human hippocampus following goal-directed navigation. eLife 12,
https://doi.org/10.7554/eLife.80281 (2023).
27. Madar, A. D., Ewell, L. A. & Jones, M. V. Pattern separation of
spiketrains in hippocampal neurons. Sci. Rep. 9, 5282 (2019).
28. Madar,A. D., Ewell,L. A. & Jones, M. V. Temporal pattern separationin
hippocampal neurons through multiplexed neural codes. PLOS
Comput. Biol. 15, https://doi.org/10.1371/journal.pcbi.1006932
(2019).
29. Venkatesh, M., Jaja, J. & Pessoa, L. Comparing functional
connectivity matrices: a geometry-aware approach applied to
participant identiﬁcation. Neuroimage 207, 116398 (2020).
30. Lin, B. & Kriegeskorte, N. The topology and geometry of neural
representations. Proc.Natl.Acad. Sci.USA 121,e2317881121 (2024).
31. Ranganath, C. et al. Functional connectivity with the hippocampus
during successful memory formation. Hippocampus 15, 997–1005
(2005).
32. Chen, J. et al. Accessing real-life episodic information from minutes
versus hours earlier modulates hippocampal and high-order cortical
dynamics. Cereb. Cortex 26, 3428–3441 (2016).
33. Van Essen, D. C. et al. The Human Connectome Project: a data
acquisition perspective. Neuroimage 62, 2222–2231 (2012).
34. Finn, E. S. & Bandettini, P. A. Movie-watching outperforms rest for
functional connectivity-based prediction of behavior. Neuroimage
235, 117963 (2021).
35. Wang, T. et al. Modulation of cortical and hippocampal functional MRI
connectivity following transcranial alternating current stimulation in
mild Alzheimer disease. Radiology 315, e241463 (2025).
36. Li, K. et al. Distinct ventral hippocampal inhibitory microcircuits
regulating anxiety and fear behaviors. Nat. Commun. 15, 8228 (2024).
37. Huth, A. G. et al. A continuous semantic space describes the
representation of thousands of object and action categories across
the human brain. Neuron 76, 1210–1224 (2012).
38. Glasser, M. F. et al. The minimal preprocessing pipelines for the
Human Connectome Project. Neuroimage 80, 105–124 (2013).
39. Salimi-Khorshidi, G. et al. Automatic denoising of functional MRI data:
combining independent component analysis and hierarchical fusion
of classiﬁers. Neuroimage 90, 449–468 (2014).
40. Griffanti, L. et al. ICA-based artefact removal and accelerated fMRI
acquisition for improved resting state network imaging. Neuroimage
95, 232–247 (2014).
41. Satterthwaite, T. D. et al. An improved framework for confound
regression and ﬁltering for control of motion artifact in the
preprocessing of resting-state functional connectivity data.
Neuroimage 64, 240–256 (2013).
42. Fischl, B. FreeSurfer. Neuroimage 62, 774–781 (2012).
43. Kahhale, I. et al. Quantifying numerical and spatial reliability of
hippocampal and amygdala subdivisions in FreeSurfer. Brain Inf. 10, 9
(2023).
44. Iglesias, J. E. et al. A computational atlas of the hippocampal
formation using ex vivo, ultra-high resolution MRI: application to
adaptive segmentation of in vivo MRI. Neuroimage 115, 117–137
(2015).
45. Schaefer, A. et al. Local-global parcellation of the human cerebral
cortex from intrinsic functional connectivity MRI. Cereb. Cortex 28,
3095–3114 (2018).
46. Yeo, B. T. et al. The organization of the human cerebral cortex
estimated by intrinsic functional connectivity. J. Neurophysiol. 106,
1125–1165 (2011).
47. Kriegeskorte, N., Mur, M. & Bandettini, P. Representational similarity
analysis—connecting the branches of systems neuroscience. Front.
Syst. Neurosci. 2, 4 (2008).
48. Lu, Z. et al. End-to-end topographic networks as models of cortical
map formation and human visual behaviour. Nat. Hum. Behav. 9,
1975–1991 (2025).
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
13


## Page 14

49. Simony, E. et al. Dynamic reconﬁguration of the default mode
network during narrative comprehension. Nat. Commun. 7, 12141
(2016).
50. Nastase, S. A. et al. Measuring shared responses across subjects
using intersubject correlation. Soc. Cogn. Affect Neurosci. 14,
667–685 (2019).
51. Hasson, U. et al. Intersubject synchronization of cortical activity
during natural vision. Science 303, 1634–1640 (2004).
52. Chen, J. et al. Shared memories reveal shared structure in neural
activity across individuals. Nat. Neurosci. 20, 115–125 (2017).
53. Zadbood, A. et al. How we transmit memories to other brains:
constructing shared neural representations via communication.
Cereb. Cortex 27, 4988–5000 (2017).
54. Chang, C. H. C., Nastase, S. A. & Hasson, U. Information ﬂow across
the cortical timescale hierarchy during narrative construction. Proc.
Natl. Acad. Sci. USA 119, e2209307119 (2022).
55. Mackinnon, D.P., Lockwood,C. M. & Williams, J. Conﬁdencelimitsfor
the indirect effect: distribution of the product and resampling
methods. Multivar. Behav. Res. 39, 99 (2004).
56. Baron, R. M. & Kenny, D. A. The moderator-mediator variable
distinction in social psychological research: conceptual, strategic,
and statistical considerations. J. Pers. Soc. Psychol. 51, 1173–1182
(1986).
57. Tacikowski, P. et al. Human hippocampal and entorhinal neurons
encode the temporal structure of experience. Nature 635, 160–167
(2024).
58. Hasson, U. et al. Enhanced intersubject correlations during movie
viewing correlate with successful episodic encoding. Neuron 57,
452–462 (2008).
59. Berron, D. et al. Strong evidence for pattern separation in human
dentate gyrus. J. Neurosci. 36, 7569–7579 (2016).
60. Baker, S. et al. The human dentate gyrus plays a necessary role in
discriminating new memories. Curr. Biol. 26, 2629–2634 (2016).
61. Neunuebel, J. P. & Knierim, J. J. CA3 retrieves coherent
representations from degraded input: direct evidence for CA3 pattern
completion and dentate gyrus pattern separation. Neuron 81,
416–427 (2014).
62. Grande, X. et al. Holistic recollection via pattern completion
involves hippocampal subﬁeld CA3. J. Neurosci. 39, 8100–8111
(2019).
63. Knierim, J. J. & Neunuebel, J. P. Tracking the ﬂow of hippocampal
computation: pattern separation, pattern completion, and attractor
dynamics. Neurobiol. Learn. Mem. 129, 38–49 (2016).
64. Eichenbaum, H. Prefrontal-hippocampal interactions in episodic
memory. Nat. Rev. Neurosci. 18, 547–558 (2017).
65. Rolls, E. T. et al. The effective connectivity of the human hippocampal
memory system. Cereb. Cortex 32, 3706–3725 (2022).
66. Ma, Q. et al. Extensive cortical functional connectivity of the human
hippocampal memory system. Cortex 147, 83–101 (2022).
67. Raud, L. et al. Hippocampal-cortical functional connectivity
during memory encoding and retrieval. Neuroimage 279, 120309
(2023).
68. Chang, C. H. C. et al. Relating the past with the present: information
integration and segregation during ongoing narrative processing. J.
Cogn. Neurosci. 33, 1106–1128 (2021).
69. Sherrill, K. R. et al. Hippocampus and retrosplenial cortex combine
path integration signals for successful navigation. J. Neurosci. 33,
19304–19313 (2013).
70. Chrastil, E. R. et al. There and back again: hippocampus and
retrosplenial cortex track homing distance during human path
integration. J. Neurosci. 35, 15442–15452 (2015).
71. Patai, E. Z. et al. Hippocampal and retrosplenial goal distance coding
after long-term consolidation of a real-world environment. Cereb.
Cortex 29, 2748–2758 (2019).
72. Qiu, Y. et al. Forming cognitive maps for abstract spaces: the roles of
the human hippocampus and orbitofrontal cortex. Commun. Biol. 7,
517 (2024).
73. Henderson, J. M., Larson, C. L. & Zhu, D. C. Full scenes produce more
activation than close-up scenes and scene-diagnostic objects in
parahippocampal and retrosplenial cortex: an fMRI study.Brain Cogn.
66, 40–49 (2008).
74. Ranganath, C. & Ritchey, M. Two cortical systems for memory-guided
behaviour. Nat. Rev. Neurosci. 13, 713–726 (2012).
75. Alexander, A. S. et al. Rethinking retrosplenial cortex: perspectives
and predictions. Neuron 111, 150–175 (2023).
76. Miller, A. M. et al. Cues, context, and long-term memory: the role of the
retrosplenial cortex in spatial cognition. Front. Hum. Neurosci. 8, 586
(2014).
77. De Almeida-Filho, D. G. et al. Hippocampus-retrosplenial cortex
interaction is increased during phasic REM and contributes to
memory consolidation. Sci. Rep. 11, 13078 (2021).
78. Ziontz, J. et al. Hippocampal connectivity with retrosplenial cortex is
linked to neocortical tau accumulation and memory function. J.
Neurosci. 41, 8839–8847 (2021).
79. Hou, R. et al. Coordinated interactions between the hippocampus
and retrosplenial cortex in spatial memory. Research 7, 0521
(2024).
80. Fjell, A. M. et al. Brain events underlying episodic memory changes in
aging: a longitudinal investigation of structural and functional
connectivity. Cereb. Cortex 26, 1272–1286 (2016).
81. Damoiseaux, J. S. et al. Differential effect of age on posterior and
anterior hippocampal functional connectivity. Neuroimage 133,
468–476 (2016).
82. Navratilova, Z. et al. Pattern completion and rate remapping in
retrosplenial cortex. Research Square. https://doi.org/10.21203/rs.3.
rs-2736384/v1 (2023).
83. Wisse, L. E., Biessels, G. J. & Geerlings, M. I. A critical appraisal of the
hippocampal subﬁeld segmentation package in FreeSurfer. Front.
Aging Neurosci. 6, 261 (2014).
84. Wisse, L. E. et al. Automated hippocampal subﬁeld segmentation at
7T MRI. AJNR Am. J. Neuroradiol. 37, 1050–1057 (2016).
85. Zheng, X. Y. et al. Parallel cognitive maps for multiple knowledge
structures in the hippocampal formation. Cereb. Cortex 34, https://
doi.org/10.1093/cercor/bhad485 (2024).
86. Neupane, S., Fiete, I. & Jazayeri, M. Mental navigation in the primate
entorhinal cortex. Nature 630, 704–711 (2024).
Acknowledgements
This work was supported by the National Natural Science Foundation of
China (www.nsfc.gov.cn/; grant numbers 82072000 and 81671769), the
Natural Science Foundation of Heilongjiang Province, China (http://kjt.hlj.
gov.cn/, grant number YQ2023H016), the Fundamental Research Funds for
the Central Universities (Grant No. HIT.OCEF.2023015), and the State Key
Laboratory of Space Environment Interaction with Matters. We thank
SVGRepo for the brain schematic illustration (https://www.svgrepo.com/
vectors/brain/).
Author contributions
L.S., Q.L., S.L., and X.L. contributed to the conception and design of this
study; L.S.,Q.L., and S.L performed data analysisand curation; L.S. and X.L.
drafted and revised the manuscript. L.S., Q.L., S.L., W.D., Z.L., K.L., W.Q.,
and X.L. conducted the investigation. L.S., Q.L., and W.D. carried out
validation. X.L. supervised the study and acquired funding. All authors
reviewed and approved the ﬁnal manuscript.
Competing interests
The authors declare no competing interests.
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
14


## Page 15

Additional information
Supplementary information The online version contains
supplementary material available at
https://doi.org/10.1038/s42003-026-09554-6.
Correspondence and requests for materials should be addressed to
Xia Liang.
Peer review information Communications Biology thanks the anonymous
reviewers for their contribution to the peer review of this work. Primary
Handling Editor: Benjamin Bessieres. [A peer review ﬁle is available].
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
© The Author(s) 2026
https://doi.org/10.1038/s42003-026-09554-6
Article
Communications Biology |  (2026) 9:274 
15


