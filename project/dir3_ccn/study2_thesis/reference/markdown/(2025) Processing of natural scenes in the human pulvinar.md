# (2025) Processing of natural scenes in the human pulvinar

**Source:** (2025) Processing of natural scenes in the human pulvinar.pdf

---

## Page 1

Article
https://doi.org/10.1038/s41467-025-67472-3
Processing of natural scenes in the human
pulvinar
Daniel R. Guest
1
, Emily J. Allen
2,3, Kendrick N. Kay
3,5 &
Michael J. Arcaro
4,5
Theories of high-level visual processing and object recognition have typically
focused on ventral visual cortex, often overlooking potential contributions of
subcortical structures. The pulvinar, via extensive connections with visual
cortex, is well-positioned to play a role in high-level vision. Here, we investi-
gated how the pulvinar represents visual information using a high-resolution
7 T fMRI dataset of responses to tens of thousands of natural scenes. Encoding
models targeting different stimulus features revealed a pulvinar region
selective for bodies and faces presented in the contralateral visual hemiﬁeld.
Complementary model-free analyses demonstrated that this region is co-
active with body- and face-selective cortical areas during natural scene view-
ing. These ﬁndings challenge cortico-centric models of object vision by
demonstrating that principles of cortical organization, including functional
clustering and hierarchical organization, also manifest in subcortex. Moreover,
they highlight the value of using naturalistic stimuli to probe visual function.
Higher visual functions, particularly object and face recognition, are
crucial for interacting with and making sense of the environment. A
hallmark of primate vision is our ability to rapidly and effortlessly
identify and categorize objects across variations in the retinal input1.
This remarkable capacity relies on the brain’s ability to extract relevant
visual features from complex visual input and integrate them into a
coherent percept.
The hierarchical organization of the ventral visual cortex has long
been recognized as a key factor in transforming retinal input into
useful perceptual representations2. This hierarchy progresses from
early visual cortex (V1, V2) responding to low-level features such as
local contrast and orientation, through intermediate areas (V4)
encoding more complex features such as textures and shapes, to
anterior regions exhibiting categorical distinctions in their respon-
siveness to faces, bodies, and objects3–5. In addition to feedforward
pathways giving rise to increasingly complex representations, recur-
rent and feedback connections are thought to help ensure robust
recognition in the face of challenges during natural visual experience,
such as partial occlusion or varying light conditions6,7.
However, this cortico-centric view is incomplete. Recent evidence
suggests that recurrent connectivity with the thalamus, particularly
the pulvinar, may play a critical role in achieving robust perceptual and
cognitive functions8–10. The pulvinar, with its extensive reciprocal
connections to visual cortex, is well-positioned to inﬂuence visual
processing at multiple levels. While much research has focused on the
pulvinar’s
involvement
in
early
sensory
processing11–13,
visual
attention14,15, and visuomotor behaviors16,17, its distinct anatomical
connectivity with ventral visual cortex18 suggests a potential role in
high-level object recognition processes.
Despite the presence of distinct anatomical connectivity between
the pulvinar and cortical regions supporting high-level visual processes,
our understanding of the pulvinar’s role in complex visual functions,
such as object recognition, remains limited. Previous investigations of
pulvinar function have predominantly employed simple stimuli, focus-
ing on low-level visual features, such as orientation and image
contrast11,19. Some evidence hints at the pulvinar’s involvement in
higher-level visual representations: anatomical tracing in non-human
primates reveals connections between the pulvinar and face-selective
Received: 1 April 2025
Accepted: 1 December 2025
Check for updates
1Department of Biomedical Engineering, University of Rochester, Rochester, NY, USA. 2Department of Psychology, University of Minnesota, Minneapolis, MN,
USA. 3Center for Magnetic Resonance Research (CMRR), Department of Radiology, University of Minnesota, Minneapolis, MN, USA. 4Department of Psy-
chology, University of Pennsylvania, Philadelphia, PA, USA. 5These authors jointly supervised this work: Kendrick N. Kay, Michae J. Arcaro.
e-mail: daniel_guest@urmc.rochester.edu
Nature Communications|   (2026) 17:789 
1
1234567890():,;
1234567890():,;


## Page 2

cortical regions20; electrophysiological recordings have identiﬁed pul-
vinar neurons sensitive to face-like shapes21 and facial emotion22; and
fMRI studies in humans have identiﬁed functional substructure within
the pulvinar with sensitivity to visual categories23,24. However, the spe-
ciﬁcity of these ﬁndings to object recognition processes remains
unclear. For example, medial pulvinar damage can impair emotion
recognition, while sparing other aspects of visual recognition25. More-
over, individual pulvinar regions receive convergent inputs from func-
tionally diverse cortical regions, potentially resulting in broadly tuned
representations. Finally, whereas prior work has demonstrated the
existence
of
retinotopic
maps
in
pulvinar
for
low-level
visual
features11,19,26, it is presently unknown whether such spatial coding is
also present in areas of the pulvinar that may be responsive to higher-
level visual features. Thus, how the pulvinar represents complex visual
information, its functional topography, and its relationship to cortical
processing of visually presented objects remains unclear.
To investigate the pulvinar’s role in object recognition and the
relationship of the pulvinar to cortical areas, we leveraged the
Natural Scenes Dataset (NSD; http://naturalscenesdataset.org), a 7T
fMRI dataset consisting of responses to tens of thousands of natural
scenes. NSD constitutes an especially promising opportunity to
study the pulvinar, given the use of ultra-high magnetic ﬁeld
strength (7T) to improve signal-to-noise ratio and achieve high
spatial resolution (1.8 mm). We ﬁrst developed encoding models to
characterize spatial coding and responsiveness to different visual
features present within natural scenes, including low-level image
content and selectivity to speciﬁc visual categories. We then used
model-free correlation analyses to identify co-activation patterns
between the pulvinar and visual cortex during the processing of
natural scenes. These analyses revealed a pulvinar region selectively
responsive to faces and bodies, distinct from portions of the pul-
vinar sensitive to low-level visual content. Notably, both regions
exhibited retinotopic organization, suggesting a common organiz-
ing principle across different levels of visual processing. The body-
and face-selective pulvinar regions also showed speciﬁc co-
activation patterns with corresponding body- and face-selective
cortical areas. Furthermore, there was some evidence that these
clusters were embedded within a broader gradient of cortical cor-
relations across the pulvinar. These ﬁndings position the pulvinar as
an important structure in high-level vision, potentially interfacing
with cortex at multiple levels of visual processing.
Results
Using pRF models to characterize representations of features in
natural scenes
We ﬁrst characterized the pulvinar’s response to different visual fea-
tures within natural scenes by building and testing encoding models
for the Natural Scenes Dataset (NSD). We evaluated a wide range of
image features, including low-level properties, such as local contrast,
and high-level content, such as bodies and faces. To predict voxel-wise
responses, we coupled features extracted from the NSD images with a
population receptive ﬁeld (pRF) model27 (Fig. 1). This approach char-
acterizes each voxel as being jointly tuned for a speciﬁc stimulus fea-
ture and an area of visual space. We tested models corresponding to
seven different features prevalent in real-world scenes: local contrast,
salience, faces, bodies, words, foreground, and background (Supple-
mentary Fig. 1; see Methods for details about how each feature was
computed). For each feature, we obtained a full set of best-ﬁtting pRF
parameters, including pRF position, size, and gain for every voxel
within each participant. This model-based approach allowed us to
assess multiple levels of visual processing within the pulvinar. Impor-
tantly, when applied in cortex, these pRF models revealed selective
responses in the ventral visual stream regions tuned for particular
visual categories, including the body-selective FBA and the face-
selective FFA (Supplementary Fig. 6), thereby validating the approach
before probing subcortex.
Fig. 1 | Identifying stimulus features encoded in voxel responses using popu-
lation receptive ﬁeld (pRF) models. Each NSD image was converted into feature
maps that indicated the presence of a given feature at each location in the image.
Seven types of feature maps, corresponding to different low-, mid-, and high-level
image properties (see Methods for details), were prepared (background was
deﬁned as the inverse of foreground). To predict the response to an image, a given
feature map is weighted by a 2D isotropic Gaussian, summed over the visual ﬁeld,
and then a compressive static nonlinearity is applied (Kay, Winawer, et al., 2013).
Model parameters are optimized to minimize error between observed BOLD
amplitudes (gray circle markers) and predicted BOLD amplitudes (purple “X”
markers). For each voxel, a separate model was ﬁt for each feature type, attempting
to account for the fMRI response amplitudes to the 9000–10,000 natural scenes
seen by each NSD subject. Image examples are reproduced from the NSD stimulus
set, derived from the Microsoft COCO image database57 licensed under CC-BY-4.0.
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
2


## Page 3

Distinct pulvinar regions responsive to low- and high-level
features
Our analyses revealed distinct regions within the pulvinar responsive
to different types of visual content within natural scenes. We observed
a clear functional segregation between regions of the pulvinar that
process low-level visual features and those responsive to high-level
object categories (Fig. 2). The variance explained by the pRF models
was relatively low in the pulvinar compared to cortex (Supplementary
Fig. 6). This difference can be attributed to many factors that impair
signal detection within the thalamus, including the relatively high
distance from the radiofrequency coils, the intermixing of cell bodies
and white matter, the close proximity to ventricles, and other intrinsic
differences
in
noise
sources
between
midbrain
and
cortical
structures28. Despite this, the observed patterns of activation were
consistent across individuals, underscoring the reliability and func-
tionalrelevance of thesedistinctions.Acrosssubjects, low-level feature
processing was predominantly localized to the inferior-lateral portions
of the pulvinar and the neighboring lateral geniculate nucleus (LGN).
The local contrast and image salience models yielded highly correlated
variance-explained maps (r = 0.8;SupplementaryFig. 2). We found that
these models best accounted for BOLD responses in the LGN (green
outline) and inferior-lateral portions (light blue) of the pulvinar
(Fig. 2A, B; Supplementary Fig. 3). This ﬁnding aligns with previous
human neuroimaging studies demonstrating these regions’ sensitivity
to basic visual patterns, such as ﬂickering checkerboards26,29,30. In
contrast, high-level feature processing was localized to medial and
posterior regions of the pulvinar across subjects. The body and face
pRF models best accounted for BOLD responses in these regions
(Fig. 2A, B; Supplementary Fig. 3). The high correlation between face
and body variance-explained maps (r = 0.93) may reﬂect the frequent
co-occurrences of these features in natural scenes. The foreground
pRF model showed a broader pattern of responsiveness, accounting
for variance in both low-level and feature-responsive regions. Fore-
ground maps were correlated with image contrast (r = 0.6) and sal-
ience (r = 0.65) as well as with face (r = 0.41) and body (r = 0.35) feature
maps. As an important control comparison, not all features were linked
to activations in the pulvinar. Background and word pRF models
explained little variance in pulvinar activations (Supplementary Fig. 4),
and we therefore do not examine these models further.
A winner-take-all analysis comparing the variance explained by
different feature models further illustrates this feature segregation
within the pulvinar. Activity in the inferior-lateral pulvinar was best
explained by image contrast and salience, while activity in the
posterior-medial pulvinar was best explained by bodies and faces
(Fig. 2C). Notably, none of these models captured substantial variance
in dorsal parts of the pulvinar associated with attentional ﬁltering23,
suggesting that object-recognition processes are speciﬁcally linked to
the ventral pulvinar. The limited overlap between variance-explained
maps for the contrast model versus the body and face models, com-
bined with the lack of correlation in variance explained across models
(Supplementary Fig. 2), demonstrates a clear functional substructure
within the pulvinar, with anatomically distinct regions exhibiting
selective responses to low- and high-level visual features.
Organized spatial coding of low- and high-level visual features
within the pulvinar
Having identiﬁed distinct pulvinar regions responsive to low- and high-
level visual content in real-world scenes, we next examined their spa-
tial coding. Each pRF feature model produced a set of parameter
estimates characterizing voxel-wise spatial selectivity throughout the
Fig. 2 | Distinct regions of the pulvinar responsive to low- and high-level visual
features. A Group-average (n = 8) variance-explained maps for six pRF feature
models shown in three adjacent coronal images covering the LGN and pulvinar. The
ﬁrst column shows colored contours of ﬁve functionally deﬁned subcortical ROIs
derived from independent data overlaid on corresponding MNI anatomical coronal
slices (green LGN; light blue ventral pulvinar; dark blue dorsolateral pulvinar; dark
purple dorsomedial pulvinar; magenta superior colliculus; see Methods for details;
Arcaro et al. 2015; 2018). Remaining columns show variance-explained maps for
each pRF model. Only voxels with >0.2% variance explained are shown. B Maximum
intensity projection of variance-explained results along the anterior-posterior axis
for each feature model. Dashed colored contours indicate the ﬁve ROIs. Variance-
explained values from voxels outside the thalamus ROI were set to 0%. C Left,
sagittal view of anatomy with red lines indicating which slices are plotted in sub-
sequent panels. Right, coronal views of winner-take-all analysis, showing which
feature model explained the most variance for each voxel within the posterior
thalamus ROI. Only voxels with >0.2% variance explained by any feature model are
included.
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
3


## Page 4

pulvinar (Supplementary Fig. 4). We focused on the image contrast and
body pRF models, as these models explained the most variance in
responses to the NSD stimuli within the lateral and medial pulvinar,
respectively (Fig. 2C).
With respect to low-level features, the contrast model revealed a
bilateral topographic organization of contralateral visual space within
inferior-lateral portions of the pulvinar across subjects (Fig. 3B). The
upper visual ﬁeld (Fig. 3B, ﬁrst row; red) was represented ventral-lat-
erally, while the lower visual ﬁeld (blue) was represented superior and
medially. Between these vertical meridian representations, there was a
qualitative gradual progression of preferred visual angle crossing the
horizontal midline (green). Quantitatively, pRF angle estimates could
be predicted by a linear gradient oriented in 3D largely along the
ventral-lateral to dorsal-medial axis (left hemisphere: R2 = 0.16; right
hemisphere: R2 = 0.16; Supplementary Fig. 8A–D). These representa-
tions were predominantly within central visual space (Fig. 3B, second
row) and exhibited strong lateralization to the contralateral visual ﬁeld
(Fig. 3B, third row). At the group-average level, 73% of voxels having at
least 0.1% variance explained had pRFs tuned within 3° eccentricity
(range at individual subject level: 49–79%). pRF eccentricity estimates
could be predicted by a simple model consisting of foveal center
surrounded by more peripheral representations in 3D (left hemi-
sphere: R2 = 0.26; right hemisphere: R2 = 0.36; Supplementary Fig. 8E).
pRF organization was consistent across individual subjects (Fig. 3D)
and aligns with prior electrophysiological work in non-human
primates11,19 and fMRI studies in humans26,30 showing an inverted reti-
notopic map in this region of the pulvinar. These results demonstrate
that the spatial coding of the ventral pulvinar can be effectively probed
by modeling responses to low-level feature content in real-world
scenes.
Surprisingly, responses to high-level visual content also exhibited
clear topographic organization. The body pRF model revealed bilateral
representations of contralateral visual space in pulvinar regions pos-
terior and medial to the contrast model activations (Fig. 3C, ﬁrst row).
Upper visual ﬁeld representations were localized to dorsal medial
portions, while horizontal meridian and lower visual ﬁeld representa-
tions were ventral and lateral. The medial pulvinar contained a central
visual ﬁeld representation surrounded by peripheral representations
(Fig. 3C, second row). Body pRFs were generally lateralized to the
contralateral visual hemiﬁeld (Fig. 3C, third row) and covered the
extent of the visual ﬁeld stimulated by the NSD images (Fig. 3E). At the
group-average level, only 19% of voxels having at least 0.1% variance
explained had pRFs tuned within 3° eccentricity (range at individual
level: 17–57%). Similar to the contrast maps, body pRF angle estimates
(left hemisphere: R2 = 0.07; right hemisphere: R2 = 0.03; Supplemen-
tary Fig. 8F–I) and eccentricity estimates (left hemisphere: R2 = 0.33;
right hemisphere: R2 = 0.43; Supplementary Fig. 8J) could be partially
predicted by simple low-dimensional spatial models. These results
demonstrate that the processing of high-level categorical content in
the pulvinar is anchored to spatial coding of sensory input.
Comparison of visual ﬁeld representations derived from the
contrast and body models revealed two distinct, mirror symmetric
retinotopic zones. The organization of visual space along the polar
angle dimension for the body model was inverted relative to that in the
lateral pulvinar for the contrast model. The lower visual ﬁeld repre-
sentations of both models overlapped (Fig. 3B, C; Supplementary
Fig. 5, dashed lines), whereasthe upper visualﬁeld representation from
the contrast model was located ventrolaterally and that of the body
model dorsomedially. In the left hemisphere, this qualitative char-
acterization of map orientations was reinforced by the quantitative
analysis results (Supplementary Fig. 8). Together, these ﬁndings indi-
cate that lateral and medial regions of the pulvinar each contain dis-
tinct retinotopic maps, and that their relative positioning suggests a
continuity
of
retinotopic
organization
across
the
pulvinar.
Fig. 3 | Spatial coding of low- and high-level visual features in the pulvinar. A An
MNI anatomical reference illustrating the location and extent of the coronal slices
used in panels (B and C). Colored contours indicate the ﬁve subcortical ROIs shown
in Fig. 2. B Group-average (n = 8) results from the contrast pRF model. From top to
bottom, polar angle, eccentricity, and visual-ﬁeld laterality are shown for three
coronal sections. Data were thresholded at 0.1% variance explained (by the contrast
pRF model). C Group-average results from the body pRF model. Same format as
panel (B) (with data thresholded based on body pRF model results). D Visual ﬁeld
coverage plots for the contrast pRF model. pRFs from the top 100 voxels in each
hemisphere (in terms of variance explained) are plotted on the visual ﬁeld. Dots
indicate the centers of pRFs while circles indicate the extent of the pRFs (±1 stan-
dard deviation). The gray square indicates the size and location of the stimulus.
Dashed lines indicate the vertical and horizontal meridians. The larger subpanel
shows results from a group average (i.e., based on averaging pRF parameters across
participants in each voxel), while the other subpanels show results from individual
subjects. E Visual ﬁeld coverage for the body pRF model, in the same format as
panel (D).
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
4


## Page 5

This organization parallels the layout of multiple retinotopic maps in
visual cortex, where adjacent areas are arranged so that visual ﬁeld
representations progress smoothly from one map to the next.
Model-free analyses reveal similarity in representations between
cortex and pulvinar
As a complement to our model-based analyses, we devised a model-
free approach to relate cortical and subcortical representations of
natural scenes. Prior research has shown that different regions of the
pulvinar are anatomically connected31 and functionally coupled23 with
different parts of visual cortex. The anatomical locations of the con-
trast- and body-selective subregions align with evidence for a gradient
of pulvino-cortical connectivity26,31, suggesting that visually evoked
activity in different parts of the pulvinar might resemble activity in
functionally corresponding cortical regions. To test this hypothesis
and the functional speciﬁcity of such connectivity, we conducted a
correlational analysis between the pulvinar and cortex based on acti-
vations from the NSD dataset.
We analyzed single-trial BOLD response amplitudes in the pulvi-
nar and cortex, derived using GLMsingle to capture the response of
each voxel to individual image trials in NSD (Fig. 4A; see Methods for
details). For each subject, we identiﬁed pulvinar voxels showing the
highest variance explained by the contrast and body models. We then
computed trial-by-trial correlations between the BOLD responses in
these pulvinar voxels and all cortical voxels (Fig. 4B). This analysis
revealed robust correlations between the pulvinar and extensive
portions of the visual cortex for both the contrast-peak and body-peak
pulvinar voxels, with weaker correlations in non-visual cortex (Fig. 4D).
Contrast-peak voxels showed strong correlations with both early and
anterior visual cortex, whereas body-peak voxels correlated more
selectively with anterior visual cortex. Importantly, qualitatively simi-
lar maps are produced using different voxel seed selections (Supple-
mentary Fig. 7), indicating the robustness of these ﬁndings. These
ﬁndings demonstrate distinct patterns of cortical coupling for lateral
and medial regions of the ventral pulvinar.
To isolate correlations driven by stimulus-evoked responses from
other potential sources of co-activation (such as arousal and atten-
tion), we recomputed correlations between the pulvinar and cortex
using responses to the same image but from different trials (Fig. 5A).
This approach yielded more spatially localized correlations. For the
contrast peak, cortical correlations were predominantly conﬁned to
posterior occipital cortex, aligning with the extent of early visual
retinotopic maps (V1-hV4) identiﬁed from a separate localizer experi-
ment (Fig. 5B; see Methods for details). Body peak co-activations were
primarily constrained to extrastriate visual cortical areas responsive to
faces and bodies, including EBA, FBA, and FFA (Fig. 5C). Notably, the
body peak showed no correlation with early visual cortex or other
category-selective extrastriate areas, such as place (e.g., TOS, PPA) and
word areas (e.g., OWFA, VWFA). These ﬁndings demonstrate func-
tionally speciﬁc coupling between pulvinar and cortex in response to
real-world stimulation, reﬂecting an alignment of processing between
the thalamus and cortex.
Fig. 4 | Contrast- and body-selective pulvinar subregions are co-active with
distinct cortical regions. A Schematic showing the same-trial correlation analysis,
where correlation is computed between BOLD responses observed at the same
time. Image examples are reproduced from the NSD stimulus set, derived from the
Microsoft COCO image database57 licensed under CC-BY-4.0. B Schematic showing
how subcortical-to-cortical correlations are computed. For a given seed voxel in the
pulvinar, we correlated the activity in that seed voxel with activity in each vertex on
the cortical surface, resulting in a map of correlations across the cortical surface.
C Extents of the pRFs (±1 standard deviation) for seed voxels selected from each
subject. Contrast seed voxels are shown in purple, body seed voxels in yellow. The
gray square indicates the size and location of the stimulus. Dashed lines indicate the
vertical and horizontal meridians. D Cortical correlations resulting from seeding
the peak voxel in the pulvinar for the (left) contrast and (right) body models. Data
are thresholded based on a bootstrap procedure (see Methods for details). Inset
images show unthresholded maps.
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
5


## Page 6

To contextualize these results with respect to the entire pulvinar,
we performed a third analysis correlating responses from various
cortical areas with responses from each voxel within the pulvinar
(Fig. 6A). As in Fig. 5, this analysis was performed using responses to
the same images from different trials. This analysis revealed that V1
correlations were strongest within the LGN and ventrolateral areas of
the pulvinar (Fig. 6B), consistent with the greater anatomical con-
nectivity of those subcortical regions with early visual cortex31. In
contrast, FFA and FBA correlations were biased toward superior and
medial aspects of pulvinar (Fig. 6B). Notably, voxels best explained by
the contrast pRF model (Fig. 6B; purple circles) aligned with the peak
V1 correlation, while those best explained by the face (yellow circles) or
body (green circles) pRF models aligned with the peak FFA and FBA
correlations.
Visualizing cortical correlation maps with half-max contours
revealed a progression across the pulvinar from anterior-inferior-
lateral to posterior-superior-medial as the cortical seed area shifted
from V1 in the posterior visual cortex to hV4 anteriorly (Fig. 6C; see
Methods for details). While all early visual cortical areas showed cor-
relations with the LGN and ventrolateral pulvinar, the superior-medial
extent of correlation increased systematically across successive cor-
tical seeds. Because fMRI responses from nearby cortical ROIs are
themselves correlated, we tested whether unique contributions from
individual areas could be isolated using multiple regression (Supple-
mentary Fig. 9). This analysis yielded more focal correlations in the
pulvinar for V1, V2, V3, hV4, and FBA. Notably, while the main analysis
showed both V1 and V2 correlating with anterior coronal slices over-
lapping the LGN, multiple regression isolated focal LGN correlations
for V1, with V2 peaking instead in adjacent pulvinar. Similarly, whereas
the main analysis showed widespread MT correlations, the multiple
regression revealed a more focal ventral pulvinar region just medial to
the V1/V2 peaks, consistent with the location of pulvinar subregion
PIm, which connects exclusively with MT32. These patterns mirror prior
ﬁngerprint functional connectivity results23, suggesting that multi-
variate approaches such as regression or pattern analysis can better
separate shared variance between nearby cortical areas. Overall, these
ﬁndings reinforce the conclusion of structured subcortical–cortical
correlations.
Discussion
Our analysis of BOLD responses to tens of thousands of natural scenes
revealed a complex functional architecture within the pulvinar. Using
pRF models, we identiﬁed distinct regions responsive to low-level
visual features and high-level object categories, particularly faces and
bodies. These regions each contained orderly retinotopic maps and
together formed a continuous organization across the pulvinar. Cor-
relational analyses further demonstrated functional coupling between
pulvinar subregions and cortical areas selective for low- and high-level
visual features, matching the distinctions revealed by the pRF analysis.
Together, these ﬁndings suggest that the pulvinar interacts with cortex
Fig. 5 | Different-trials analysis reveals highly speciﬁc pulvino-cortical corre-
spondences. A Correlation is computed between BOLD responses evoked by the
same stimulus image but on different trials.Image examples are reproduced from
the NSD stimulus set, derived from the Microsoft COCO image database 57 licensed
under CC-BY-4.0. B Cortical correlations corresponding to the peak pulvinar voxel
for the contrast pRF model. Data are thresholded based on a bootstrap procedure
(see Methods for details). Bottom image shows zoomed-in view of peak
correlations within occipital cortex and correspondence to occipital retinotopic
map ROIs (V1, V2, V3, hV4) deﬁned based on separate localizer experiments (see
Methods and Allen et al., 2022 for details). C Cortical correlations corresponding to
the peak pulvinar voxel for the body pRF model. Same conventions as (B), except
that ROI outlines instead indicate category-selected areas: face-selective (OFA, FFA)
in green, body-selective (EBA, FBA) in dark blue, word-selective (OWFA, VWFA, mfs)
in cyan, and scene-selective (TOS, PPA) in white.
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
6


## Page 7

at multiple levels of cortical processing, and that the pulvinar may play
a more integral role in visual processing than previously appreciated.
High-level visual processing in the pulvinar
The pulvinar has long been associated with visual processing, with
most studies emphasizing its role in low-level visual feature analysis11,12,
attention14 or motor processes17. The present results conﬁrm prior
evidence for low-level feature sensitivity in the ventral lateral
pulvinar11,12, consistent with its strong anatomical connections with
early visual areas31. At the same time, our results provide clear evidence
that the pulvinar also participates in high-level visual perception. We
identiﬁed a focal region in the posterior medial pulvinar that responds
selectively to images of faces and bodies. Although previous macaque
electrophysiology has reported responses to face-like images21 and
facial emotion22, and human fMRI studies have reported weak category
preferences under artiﬁcial contexts23,24, our ﬁndings demonstrate
robust category-speciﬁc responses under ecologically valid conditions
with tens of thousands of natural scenes. A key contribution of the
present work is demonstrating the speciﬁcity of these responses in
relation to spatial coding, stimulus feature selectivity, anatomical
localization within the pulvinar, and functional coupling with corre-
sponding category-selective cortical regions.
Our results suggest that the pulvinar may play a more integral role
in object recognition than previously thought, potentially contributing
to the rapid and efﬁcient processing of socially relevant stimuli like
faces and bodies33. Converging with recent work showing face
responses in the superior colliculus34, our results indicate a broader
role for subcortex in both low- and high-level vision.
Retinotopy as an organizing principle of the visual pulvinar
A striking feature of our results is the prominence of retinotopic
organization at multiple levels of visual responsiveness in the pulvinar.
Prior fMRI studies demonstrated retinotopic maps in portions of the
human pulvinar interconnected with posterior visual cortex and sen-
sitive to low-level features26, consistent with single-unit physiology in
non-human primates11,19. The present results demonstrate that retino-
topy is a more general organizational principle of the pulvinar, with
orderly visual ﬁeld maps present even in regions selective for higher-
order features such as faces and bodies. This preservation of retino-
topy mirrors ﬁndings in inferotemporal cortex, where spatial sensi-
tivity persists35 even in face- and object-selective areas36–38. Such
consistent spatial coding across cortical and subcortical structures
suggests that retinotopy provides a common framework for integrat-
ing diverse information, from basic feature detection to complex
object representations.
These results also align with proposals that retinotopic organi-
zation shapes development of visual cortex, potentially serving as a
scaffold for the emergence of complex functional specializations39.
Pulvinar connectivity with cortex emerges early in gestation40, and is
hierarchically and retinotopically organized at birth41, preceding the
Fig. 6 | Progression along ventral cortical hierarchy recapitulated in the pul-
vinar. A Schematic showing how cortical-to-subcortical correlations were com-
puted. For a given cortical surface ROI, we correlated the ROI-averaged cortical
activity with activity in each subcortical voxel, resulting in a volumetric correlation
map throughout the pulvinar. Correlations were computed on BOLD responses to
the same stimulus across different trials. B Coronal slices showing pulvinar corre-
lation maps corresponding to V1, FFA, and FBA cortical ROIs. At each subcortical
voxel, we plot the number of subjects for whom correlation values passed a
threshold of |r|> 0.01 (see Methods for details). We also label the peak model-based
variance-explained value for the contrast, face, and body models for the depicted
slice. Faint gray dashed lines in the coronal slice indicate the same location across
maps. Different rows correspond to different coronal slices as in Fig. 2. C Com-
parison of correlations across the pulvinar for visual areas V1, V2, V3, hV4, OFA, and
FFA. Colored lines indicate half-max contours of the maximum intensity projection
of cortical-to-subcortical correlation results for six cortical ROIs. Tick marks indi-
cate the position of the maximum cortical-to-subcortical correlation value for a
given cortical ROI. Gray lines indicate contours of maximum intensity projections
of the anatomical ROIs from Fig. 2B.
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
7


## Page 8

development of functional clusters in cortex such as face-42 and word-
selective regions43. This developmental timeline suggests that the
pulvinar may play a critical role in shaping the ventral visual cortical
hierarchy44, potentially providing error-driven signals that support the
emergence of categorical representations45.
The pulvinar within the visual hierarchy
How does the pulvinar integrate with the established cortical archi-
tecture of object vision to support recognition? The pulvinar is an
associative thalamic nucleus with limited internal connectivity46,
forming input and output relationships primarily with cerebral cortex.
Prior studies have revealed a gradient of anatomical18,47,48 and
functional23 connectivity across the pulvinar, progressing from pos-
terior to anterior visual cortex. Rather than constituting a distinct,
parallel processing pathway, the pulvinar’s topographically organized,
but overlapping, cortical connection zones enable indirect transcor-
tical communication31, effectively integrating with the ventral visual
cortex at multiple hierarchical stages. Converging with these prior
studies, our analysis of processing during natural scene viewing
revealed a gradient of functional coactivation between the pulvinar
and cortex that recapitulates the hierarchical organization of the
ventral visual pathway. This hierarchical organization of thalamo-
cortical connections suggests that the pulvinar functions as an integral
part of the ventral visual cortical pathway, as we discuss below.
We speculate that these connectivity patterns reﬂect the pulvi-
nar’s role in gating cortical visual processing and synchronizing
cortico-cortical communication via cortico-thalamic loops. Studies in
macaques have shown that pulvinar neurons can modulate the gain of
visual responses in cortex13 and facilitate communication between
distant cortical areas15. While most work pursuing this hypothesis has
focused on the pulvinar’s role in cortical attention networks15,49,50, our
results provide evidence that the pulvinar also plays an important role
in regulating cortical networks dedicated to object vision. These
inﬂuences occur at multiple stages of the cortical hierarchy10,51,
potentially integrating diverse visual information and facilitating the
binding of relatively basic visual features into coherent object repre-
sentations. While our results emphasize the integration of processing
within the ventral visual pathway, it remains an open question the
extent to which the pulvinar might integrate information across mul-
tiple processing streams, and even potentially serve as a hub for multi-
sensory integration52.
The connection between the pulvinar and object vision suggested
by our results can be considered in light of theories that the pulvinar
contributes to fast detection circuits that support rapid, evolutionarily
important visual behaviors53. In macaques, some pulvinar neurons
sensitive to face-like features respond with latencies shorter than
50 ms21, much earlier than typical responses in inferotemporal cortex.
Such rapid responses could arise within the pulvinar or reﬂect input
from the superior colliculus54, where similarly fast face-selective
responses have been observed34. Importantly, not all pulvinar neu-
rons respond this quickly, and population-level face responses accu-
mulate more gradually21. Rather than being inconsistent with a role in
ventral visual stream processing, these temporal differences may
reﬂect complementary functions with fast pulvinar responses provid-
ing early predictive signals that help shape slower, more detailed
cortical analysis45.
Towards studying visual networks with higher ecological
validity
Our study demonstrates the utility of using naturalistic stimuli to
probe processing throughout the visual system. While naturalistic
stimuli are often regarded as too uncontrolled for systematic investi-
gation, we have shown that computational approaches can be used to
quantify the contribution of various aspects of visual processing, from
low- to high-level visual properties, and link this processing with
speciﬁc neural circuits. Our ﬁndings isolating regions of the ventral
lateral pulvinar selective to local image contrast content in the real-
world scenes converges with prior work using less naturalistic stimuli,
serving as a validation of this approach and demonstrating a principled
way to explore neural responses to basic visual properties within real-
world contexts.
The use of naturalistic stimuli in conjunction with computational
modeling approaches offers several advantages. First, it allows for the
investigation of visual processing under conditions that more closely
approximate real-world vision. Second, it enables the simultaneous
examination of multiple levels of visual processing, from low-level
features to high-level object categories. Third, it may reveal functional
properties that are not easily observable with more constrained sti-
muli, as evidenced by our discovery of robust visual-category selec-
tivity in the pulvinar. The success of this approach in uncovering such
aspects of pulvinar function underscores its potential for embracing
complexity of natural visual input. This shift towards more ecologically
valid paradigms promises to deepen our understanding of how the
brain processes the rich visual world.
Future directions for study of the human pulvinar
The present work opens several avenues for advancing our under-
standing of the pulvinar’s role in perceptual and cognitive processing.
While our results demonstrate clear involvement in both low- and high-
level visual features, the full range of category selectivity in the pul-
vinar remains to be mapped. For example, we found limited evidence
for regions specialized for scenes, text, or inanimate objects. Some of
these gaps could be addressed by reanalysis of the NSD data with
improved pRF models for additional features, such as tools24 and food,
whereas others may require follow-up experiments with more con-
trolled stimuli.
Our ﬁndings also generate speciﬁc experimental predictions
about the pulvinar’s functional organization and development.
Decoding analyses should reveal stronger face-versus-non-face classi-
ﬁcation in the posterior medial pulvinar compared to anterior lateral
regions, with posterior responses approaching those of cortical face-
selective areas and anterior response better suited to low-level feature
discrimination. Developmental studies could test whether face and
body selectivity emerges earlier in the pulvinar than in cortex, con-
sistent with its early forming connectivity to cortical targets in
neonates41 and supporting a role in scaffolding cortical organization.
The overlapping representations of faces and bodies further suggest
that the pulvinar may serve as an integration hub, a possibility that
could be evaluated with representational similarity analyses to deter-
mine whether pulvinar responses reﬂect weighted averages of nearby
cortical representations.
Beyond representational structure, future work could examine
the pulvinar’s contribution to behavior55. Studies explicitly focused on
sampling different visual tasks could test whether the pulvinar sup-
ports face detection versus identiﬁcation of faces, while naturalistic
paradigms could investigate whether it contributes to extracting
contextual associations. Such integrative processes may be particu-
larly important for learning statistical regularities in everyday envir-
onments and could help explain how advanced recognition abilities
emerge before cortical circuitry fully matures.
Our study demonstrates that the pulvinar contains multiple reti-
notopic representations of the visual scenes, including low-level fea-
tures and high-level object categories. These representations are
localized to distinct anatomical regions that align well with known
patterns of pulvino-cortical anatomical connectivity. Our results sup-
port the hypothesis that the pulvinar plays an integral role in coordi-
nating communication between visual cortical areas across multiple
levels of processing.
These ﬁndings underscore the importance of considering sub-
cortical contributions to object vision. Unraveling the complexities of
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
8


## Page 9

cortical visual processing, such as in face and body recognition, may
require a more comprehensive understanding of their interactions
with subcortical structures like the pulvinar and superior colliculus34.
Our work provides a foundation for future investigations into the
computational roles of the pulvinar in object recognition and other
high-level visual processes.
Methods
Participants
Eight participants (six females and two males; age range, 19–32 years)
participated in the NSD study, which was approved by the Institutional
Review Panel of the University of Minnesota. All participants provided
informed consent and had normal or corrected-to-normal acuity. For
detailed participant information, see ref. 56.
Dataset
The NSD comprises fMRI measurements from 8 participants viewing
9000–10,000 distinct natural color scenes (22,000–30,000 trials)
over 30–40 scan sessions. Scanning was conducted using a 7T MRI
scanner, with whole-brain gradient-echo EPI at 1.8-mm isotropic reso-
lution and 1.6-s repetition time. Images were sourced from the
Microsoft Common Objects in Context (COCO) database57, square
cropped, and presented at 8.4° × 8.4° visual angle. Stimulus images
reproduced here (Figs. 1, 4, and 5, and Supplementary Fig. 1) are thus
modiﬁcations of the original images used in compliance with COCO
database’s Creative Commons 4.0 license (https://creativecommons.
org/licenses/by/4.0/). A set of 1000 images was shared across partici-
pants, with the remaining images unique to each participant. Images
were presented for 3 s each, with 1-s gaps between them.
Data preprocessing included temporal interpolation for slice time
correction and spatial interpolation for head motion correction and
compensation for spatial distortion. Single-trial beta weights, repre-
senting BOLD response amplitudes, were estimated using a general
linear model. The study utilized “Version 3” trial response estimates56,
which incorporate voxel-speciﬁc hemodynamic response functions,
denoising using GLMdenoise 1.458, and ridge regression for trial
responses estimation. For cortical surface data, we utilized the NSD-
prepared subject-native surface data, registered and transferred to the
fsaverage template using nearest neighbor interpolation. For sub-
cortical data, we used the 1.0-mm volumetric preparation of the NSD
data in subject-native space, mapped into the MNI template space
using the provided T1-to-MNI transformation. To control for inter-
session variability, all data were z-scored within each voxel (or vertex
for surface preparations) on a session-by-session basis.
Regions of interest (ROIs)
Subcortical analyses focused on a manually deﬁned region of the
posterior thalamus that included the pulvinar, lateral geniculate
nucleus (LGN) and superior colliculus (SC). This region was identiﬁed
on each participant’s native-space T1-weighted anatomical image,
using the contrast between gray and white matter (for more details,
see ref. 26). To ensure consistency across subjects, each subject’s
subcortical ROI was then transformed to 1 mm MNI space using
nearest-neighbor interpolation. A group average was constructed by
selecting all voxels labeled as posterior thalamus in at least 3 out of 8
participants, then projected back to each participant’s native 0.8-mm
anatomical space.
Speciﬁc structures within this ROI were identiﬁed based on pre-
viously reported group average functional data26. These data were
warped from 1-mm MNI space to each participant’s native space. The
ventral pulvinar was deﬁned by voxels in vPul1 or vPul2 retinotopic
maps. Dorsomedial and dorsolateral pulvinar were deﬁned by corre-
lations with the precuneus and retinotopic portions of the frontopar-
ietal cortex (IPS1-5, SPL1, FEF, and IFS), respectively. The LGN and SC
were deﬁned by their respective retinotopic maps. ROIs were manually
edited to exclude voxels outside the anatomical extent of each struc-
ture and transformed back to 1 mm MNI space for group-average ROI
construction.
Stimulus feature maps
Feature maps for image contrast, saliency, foreground, background,
and speciﬁc image categories (faces, bodies, and words) were gener-
ated for fMRI analyses. Local image contrast maps were computed by
converting images to greyscale, resizing to 800 × 800 pixels, squaring
to approximate luminance response, and calculating local contrast
within a 51 × 51 grid (grid element size: 0.168 × 0.168 degrees). The grid
was padded with half a grid element on all sides to capture transitions
between the image and the mean gray background (for more detail,
see ref. 56). Saliency maps were generated using a pre-trained deep
neural network model59 trained on the SALICON dataset, a ﬁxation
dataset based on the COCO image database60. As the NSD images also
were sourced from the COCO database, this model was expected to
generalize well to the NSD stimuli. Saliency maps were cropped and
resampled to match the NSD stimuli from the COCO database56. All
other feature maps comprised binary mask annotations. Face anno-
tations were generated using the RetinaFace model (https://github.
com/deepinsight/insightface/tree/master/RetinaFace), which identi-
ﬁes rectangular bounding boxes around faces. Word annotations were
created using the EAST text detector (https://github.com/argman/
EAST), which outputs bounding quadrangles or rectangles around
text. Quadrangles were converted to enclosing rectangles for con-
sistency with other annotations. Whole body annotations were
sourced from the Microsoft COCO dataset (http://images.cocodataset.
org/annotations/annotations_trainval2017.zip), using bounding boxes
for human bodies (category ID 1) and animals (categories 16:25).
Foreground annotations were derived from segmentations across all
80 object categories, and background annotations were deﬁned as the
inverse of the foreground annotations.
Population receptive ﬁeld (pRF) analysis
A pRF encoding model with compressive spatial summation was
employed to characterize spatially speciﬁc responses to stimulus fea-
ture maps within each subject’s subcortical ROI. The model was
implemented using a modiﬁed version of AnalyzePRF (http://cvnlab.
net/analyzePRF/), which estimates voxel-wise parameters for each
feature map58, including spatial position, pRF size, gain, and variance
explained. Separate models were ﬁt for each feature map, with var-
iance explained (R2) reﬂecting the percentage of variance in trial-
averaged BOLD responses accounted for by the model. Only stimuli
unique to each subject were included, excluding the common stimuli
viewed by all participants. For non-contrast and non-saliency pRF
models, a baseline term was added to account for responses to image
regions covered by the annotated feature. For group-level analysis,
voxel-wise parameter estimates were transformed to 1 mm MNI space
using linear interpolation, and median values then were calculated
across participants for all parameters.
Winner-take-all pRF analysis
The performance of different features was evaluated with a winner-
take-all analysis. Variance explained values for each feature model
were averaged across participants in the shared 1 mm MNI space (see
above). Then, each voxel within the thalamus ROI with at least 0.2%
variance explained by any feature was labeled to indicate which feature
model explained the most variance.
pRF map characterization
To characterize the organization of retinotopic maps derived from the
pRF analysis, follow-up analyses were carried out on the contrast and
body pRF parameter estimates. To test whether pRF angle maps fol-
lowed a consistent orientation, we extracted group-averaged pRF
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
9


## Page 10

angle values that exceeded a 0.15% variance-explained criterion within
the thalamus ROI. Voxel coordinates were then projected onto can-
didate map orientations, represented as oriented 3D unit vectors.
Scalar projection values for each voxel were then correlated with the
voxels’ pRF angle value (transformed to span 0° = lower vertical mer-
idian to 180° = upper vertical meridian). A strong correlation coefﬁ-
cient indicated that voxel positions along the tested orientation
predicted pRF angle values. This procedure was repeated across 60
candidate orientations evenly distributed in 3D space (azimuth values
from 0 to 2π, elevation values from 0 to π), separately for each
hemisphere. Resulting correlation coefﬁcients were visualized on the
surface of a unit sphere (Supplementary Fig. 8). To assess signiﬁcance
of the best-ﬁt orientation, the analysis was repeated with shufﬂed
voxel-to-pRF correspondences to generate a null distribution of peak
correlation coefﬁcients, against which the observed peak was
compared.
To test whether pRF eccentricity values followed a systematic
spatial arrangement, we ﬁt an isotropic 3D Gaussian to the eccentricity
parameter estimates. The model had six parameters: a 3D mean (x, y,
z), a single standard deviation, a baseline term, and a gain term. Note
that when the baseline term is high (e.g., 4° eccentricity) and the gain
negative, the model predicts central visual ﬁeld eccentricities near the
Gaussian center and peripheral eccentricities further away. The model
was ﬁt using the nonlinear minimizer from SciPy61 with standard
parameter settings and 1-R2 as the objective function, separately for the
contrast and body maps in each hemisphere. Analyses were restricted
to voxels within the thalamus ROI exceeding a 0.15% variance-
explained threshold in the pRF analysis. For each ﬁt, 50 random initi-
alizations of the Gaussian mean within the 3D bounding box were
attempted, and the best-ﬁtting model was retained.
Pulvino-cortical correlation analysis
Correlation analyses comprised two parts: (1) correlating single-voxel
pulvinar responses with those across the entire cortical surface, and (2)
correlating average responses for cortical ROIs with all pulvinar voxels.
For the ﬁrst analysis, we identiﬁed voxels with the highest variance
explained for the contrast model (contrast peaks) and for the body
model (body peaks) in each participant’s native space. Trial response
estimates from these voxels were correlated with response estimates
from every vertex on the fsaverage cortical surface. This process was
repeated 1000 times for each participant with trials randomly resam-
pled with replacement (i.e., bootstrapped). For visualization of results
on the cortical surface (Figs. 4 and 5), the correlation coefﬁcient,
averaged across bootstrap replicates and participants, was shown only
if at least 95% of the bootstrapped correlation coefﬁcients exceeded a
value of 0 in a majority of participants in the given vertex.
For the second analysis, we constructed a set of cortical ROIs
covering most of the visual cortex. These included: (1) retinotopic
areas (V1, V2, V3, and hV4) deﬁned from the pRF localizer experiment
included with NSD56, (2) additional retinotopic areas from the Wang
probabilistic retinotopic atlas62, and (3) category-selective areas (OFA,
FFA, aTL-faces, EBA, FBA, PPA, and VWFA) from the NSD functional
category localizer experiment56. ROIs were pruned on an individual-
participant basis to avoid overlap. Average responses were generated
for each cortical ROI in fsaverage space and correlated with the trial
response estimates from voxels within the subcortical ROI.
We performed analyses between the pulvinar and cortex using
both same-trial and different-trial (for same image) pairings of
response estimates. For same-trial correlations, each response in the
subcortex was correlated with responses from the same trials in the
cortex. For different-trial correlations, we leveraged that each partici-
pant viewed each distinct image three times. Thisallowed us to identify
six possible pairs of image repeats, resulting in six response pairings
for 10,000 images across different trials of the same image. We com-
puted the correlation for each pairing, and averaged the resulting six
correlation coefﬁcients to derive a ﬁnal correlation estimate between
the pulvinar and cortex.
Programming languages and packages
Analyses were carried out and ﬁgures were produced using custom
code written in MATLAB R2018a (data preprocessing, stimulus feature
map generation, pRF analysis, correlation analysis, surface visualiza-
tions) or Python 3.13.9 (pRF map characterization, volume visualiza-
tions). The following packages were essential in this process, some of
which were already mentioned in the text above: analyzePRF 1.2
(https://github.com/cvnlab/analyzePRF/),
NumPy
2.2.4
(https://
numpy.org/),
SciPy
1.15.2
(https://scipy.org/),
matplotlib
3.10.1
(https://matplotlib.org/), and nibabel 5.3.2 (https://nipy.org/nibabel/).
Reporting summary
Further information on research design is available in the Nature
Portfolio Reporting Summary linked to this article.
Data availability
The MRI data used in this paper are available online at http://
naturalscenesdataset.org/.
Code availability
Code used to perform the analyses and generate the ﬁgures are
available online63.
References
1.
DiCarlo, J. J., Zoccolan, D. & Rust, N. C. How does the brain solve
visual object recognition?. Neuron 73, 415–434 (2012).
2.
DiCarlo, J. J. & Cox, D. D. Untangling invariant object recognition.
Trends Cogn. Sci. 11, 333–341 (2007).
3.
Grill-Spector, K. & Weiner, K. S. The functional architecture of the
ventral temporal cortex and its role in categorization. Nat. Rev.
Neurosci. 15, 536–548 (2014).
4.
Kourtzi, Z. & Connor, C. E. Neural representations for object per-
ception: structure, category, and adaptive coding. Annu. Rev.
Neurosci. 34, 45–67 (2011).
5.
Roe, A. W. et al. Toward a uniﬁed theory of visual area V4. Neuron
74, 12–29 (2012).
6.
Kar, K. & DiCarlo, J. J. Fast recurrent processing via ventrolateral
prefrontal cortex is needed by the primate ventral stream for robust
core visual object recognition. Neuron 109, 164–176.e5 (2021).
7.
Kay, K. N. & Yeatman, J. D. Bottom-up and top-down computations
in word- and face-selective cortex. eLife 6, e22341 (2017).
8.
Halassa, M. M. & Kastner, S. Thalamic functions in distributed
cognitive control. Nat. Neurosci. 20, 1669–1679 (2017).
9.
Reinhold, K., Lien, A. D. & Scanziani, M. Distinct recurrent versus
afferent dynamics in cortical visual processing. Nat. Neurosci. 18,
1789–1797 (2015).
10.
Sherman, S. M. Functioning of circuits connecting thalamus and
cortex. In Comprehensive Physiology (ed. Prakash, Y. S.) 713–739
(Wiley, 2017). https://doi.org/10.1002/cphy.c160032.
11.
Bender, D. B. Retinotopic organization of macaque pulvinar. J.
Neurophysiol. 46, 672–693 (1981).
12.
Petersen, S. E., Robinson, D. L. & Keys, W. Pulvinar nuclei of the
behaving rhesus monkey: visual responses and their modulation. J.
Neurophysiol. 54, 867–886 (1985).
13.
Purushothaman, G., Marion, R., Li, K. & Casagrande, V. A. Gating and
control of primary visual cortex by pulvinar. Nat. Neurosci. 15,
905–912 (2012).
14.
Kastner, S. et al. Functional imaging of the human lateral geniculate
nucleus and pulvinar. J. Neurophysiol. 91, 438–448 (2004).
15.
Saalmann, Y. B., Pinsk, M. A., Wang, L., Li, X. & Kastner, S. The
pulvinar regulates information transmission between cortical areas
based on attention demands. Science 337, 753–756 (2012).
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
10


## Page 11

16.
Mundinano, I.-C. et al. Transient visual pathway critical for normal
development of primate grasping behavior. Proc. Natl. Acad. Sci.
USA 115, 1364–1369 (2018).
17.
Wilke, M., Turchi, J., Smith, K., Mishkin, M. & Leopold, D. A. Pulvinar
inactivation disrupts selection of movement plans. J. Neurosci. 30,
8650–8659 (2010).
18.
Webster, M. J., Bachevalier, J. & Ungerleider, L. G. Subcortical
connections of inferior temporal areas TE and TEO in macaque
monkeys. J. Comp. Neurol. 335, 73–91 (1993).
19.
Gattass, R., Oswaldo-Cruz, E. & Souza, A. P. B. Visuotopic organi-
zation of the cebus pulvinar: a double representation of the con-
tralateral hemiﬁeld. Brain Res. 152, 1–16 (1978).
20. Grimaldi, P., Saleem, K. S. & Tsao, D. Anatomical connections of the
functionally-deﬁned ‘face patches’ in the macaque monkey. Neuron
90, 1325–1342 (2016).
21.
Nguyen, M. N. et al. Neuronal responses to face-like stimuli in the
monkey pulvinar. Eur. J. Neurosci. 37, 35–51 (2012).
22. Maior, R. S., Hori, E., Tomaz, C., Ono, T. & Nishijo, H. The
monkey pulvinar neurons differentially respond to emotional
expressions of human faces. Behav. Brain Res. 215, 129–135
(2010).
23. Arcaro, M. J., Pinsk, M. A., Chen, J. & Kastner, S. Organizing princi-
ples of pulvino-cortical functional coupling in humans. Nat. Com-
mun. 9, 1–14 (2018).
24. Wen, H. et al. Pulvinar response proﬁles and connectivity patterns
to object domains. J. Neurosci. 43, 812–826 (2023).
25. Ward, R., Calder, A. J., Parker, M. & Arend, I. Emotion recognition
following human pulvinar damage. Neuropsychologia 45,
1973–1978 (2007).
26. Arcaro, M. J., Pinsk, M. A. & Kastner, S. The anatomical and func-
tional organization of the human visual pulvinar. J. Neurosci. 35,
9848–9871 (2015).
27.
Kay, K. N., Winawer, J., Mezer, A. & Wandell, B. A. Compressive
spatial summation in human visual cortex. J. Neurophysiol. 110,
481–494 (2013).
28. Barry, R. L. et al. On the origins of signal variance in FMRI of the
human midbrain at high ﬁeld. PLoS One 8, e62708 (2013).
29. Cotton, P. L. & Smith, A. T. Contralateral visual hemiﬁeld repre-
sentations in the human pulvinar nucleus. J. Neurophysiol. 98,
1600–1609 (2007).
30. DeSimone, K., Viviano, J. D. & Schneider, K. A. Population receptive
ﬁeld estimation reveals new retinotopic maps in human subcortex.
J. Neurosci. 35, 9836–9847 (2015).
31.
Shipp, S. The functional logic of cortico-pulvinar connections.
Philos. Trans. R. Soc. Lond. Ser. B 358, 1605–1624 (2003).
32. Gutierrez, C., Cola, Seltzer, B. & Cusick, C. Neurochemical and
connectional organization of the dorsal pulvinar complex in mon-
keys. J. Comp. Neurol. 419, 61–86 (2000).
33. Pessoa, L. & Adolphs, R. Emotion processing and the amygdala:
from a ‘low road’ to ‘many roads’ of evaluating biological sig-
niﬁcance. Nat. Rev. Neurosci. 11, 773–782 (2010).
34. Yu, G., Katz, L., Quaia, C. & Krauzlis, R. Face-related activity in
superior colliculus and temporal cortex of primates. J. Vis. 24,
769 (2024).
35. Op De Beeck, H. & Vogels, R. Spatial sensitivity of macaque inferior
temporal neurons. J. Comp. Neurol. 426, 505–518 (2000).
36. Arcaro, M. J., Ponce, C. & Livingstone, M. The neurons that mistook a
hat for a face. eLife 9, e53798 (2020).
37. Hasson, U., Levy, I., Behrmann, M., Hendler, T. & Malach, R.
Eccentricity bias as an organizing principle for human high-order
object areas. Neuron 34, 479–490 (2002).
38. Kay, K. N., Weiner, K. S. & Grill-Spector, K. Attention reduces spatial
uncertainty in human ventral temporal cortex. Curr. Biol. 25,
595–600 (2015).
39. Arcaro, M. J. & Livingstone, M. S. On the relationship between maps
and domains in inferotemporal cortex. Nat. Rev. Neurosci. 22,
573–583 (2021).
40. Shatz, C. J. & Rakic, P. The genesis of efferent connections from the
visual cortex of the fetal rhesus monkey. J. Comp. Neurol. 196,
287–307 (1981).
41.
Ayzenberg, V., Song, C. & Arcaro, M. J. An intrinsic hierarchical,
retinotopic organization of visual pulvinar connectivity in the
human neonate. Curr. Biol. 35, 300–314.e5 (2025).
42. Livingstone, M. S. et al. Development of the macaque face-patch
system. Nat. Commun. 8, 14897 (2017).
43. Dehaene-Lambertz, G., Monzalvo, K. & Dehaene, S. The emergence
of the visual word form: longitudinal evolution of category-speciﬁc
ventral visual areas during reading acquisition. PLoS Biol. 16,
e2004103 (2018).
44. Bourne, J. A. & Rosa, M. G. P. Hierarchical development of the pri-
mate visual cortex, as revealed by neuroﬁlament immunoreactivity:
early maturation of the middle temporal area (MT).Cereb.Cortex 16,
405–414 (2006).
45. O’Reilly, R. C., Russin, J. L., Zolfaghar, M. & Rohrlich, J. Deep pre-
dictive learning in neocortex and pulvinar. J. Cogn. Neurosci. 33,
1158–1196 (2021).
46. Imura, K. & Rockland, K. S. Long-range interneurons within the
medial pulvinar nucleus of macaque monkeys. J. Comp. Neurol.
498, 649–666 (2006).
47. Adams, M. M., Hof, P. R., Gattass, R., Webster, M. J. & Ungerleider, L.
G. Visual cortical projections and chemoarchitecture of macaque
monkey pulvinar. J. Comp. Neurol. 419, 377–393 (2000).
48. Baleydier, C. & Morel, A. Segregated thalamocortical pathways to
inferior parietal and inferotemporal cortex in macaque monkey. Vis.
Neurosci. 8, 391–405 (1992).
49. Fiebelkorn, I. C., Pinsk, M. A. & Kastner, S. The mediodorsal pulvinar
coordinates the macaque fronto-parietal network during rhythmic
spatial attention. Nat. Commun. 10, 215 (2019).
50. Zhou, H., Schafer, R. J. & Desimone, R. Pulvinar-cortex interactions
in vision and attention. Neuron 89, 209–220 (2016).
51.
De Souza, B. O. F., Cortes, N. & Casanova, C. Pulvinar modulates
contrast responses in the visual cortex as a function of cortical
hierarchy. Cereb. Cortex 30, 1068–1086 (2020).
52. Froesel, M., Cappe, C. & Ben Hamed, S. A multisensory perspective
onto primate pulvinar functions. Neurosci. Biobehav. Rev. 125,
231–243 (2021).
53. Soares, S. C., Maior, R. S., Isbell, L. A., Tomaz, C. & Nishijo, H. Fast
detector/ﬁrst responder: interactions between the superior
colliculus-pulvinar pathway and stimuli relevant to primates. Front.
Neurosci. 11, 67 (2017).
54. Berman, R. A. & Wurtz, R. H. Functional identiﬁcation of a pulvinar
path from superior colliculus to cortical area MT. J. Neurosci. 30,
6342–6354 (2010).
55. Kay, K., Bonnen, K., Denison, R. N., Arcaro, M. J. & Barack, D. L. Tasks
and their role in visual neuroscience. Neuron 111, 1697–1713 (2023).
56. Allen, E. J. et al. A massive 7T fMRI dataset to bridge cognitive
neuroscience and artiﬁcial intelligence. Nat. Neurosci. 25,
116–126 (2022).
57. Lin, T.-Y. et al. Microsoft COCO: Common objects in context. In
Computer Vision – ECCV 2014. ECCV 2014. Lecture Notes in Com-
puter Science. (eds Fleet, D., Pajdla, T., Schiele, B. & Tuytelaars, T.)
Vol 8693, 740–755 (Springer, Cham., 2014).
58. Kay, K. N., Rokem, A., Winawer, J., Dougherty, R. F. & Wandell, B. A.
GLMdenoise: a fast, automated technique for denoising task-based
fMRI data. Front. Neurosci. 7, 247 (2013).
59. Kroner, A., Senden, M., Driessens, K. & Goebel, R. Contextual
encoder-decoder network for visual salience prediction. Neural
Netw. 129, 261–270 (2020).
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
11


## Page 12

60. Jiang, M., Huang, S., Duan, J. & Zhao, Q. SALICON: Saliency in
context. In The IEEE conference on computer vision and pattern
recognition (CVPR) (IEEE, 2015).
61.
Virtanen, P. et al. SciPy 1.0: fundamental algorithms for scientiﬁc
computing in Python. Nat. Methods 17, 261–272 (2020).
62. Wang, L., Mruczek, R. E. B., Arcaro, M. J. & Kastner, S. Probabilistic
maps of visual topography in human cortex. Cereb. Cortex 25,
3911–3931 (2015).
63. Guest, D. guestdaniel/Guestetal2025_NSDPulvinar: v1.0.0. Zenodo
https://doi.org/10.5281/ZENODO.17476802 (2025).
Acknowledgements
This work was supported by NSF CRCNS IIS-1822683 (K.N.K.), NIH
P50MH132642 (M.J.A.), and by NSF NRT-UtB1734815 (D.R.G., as trainee).
Author contributions
D.R.G. performed the analyses, produced the ﬁgures, and wrote the
original draft. E.J.A. collected the original neuroimaging data (see Allen
et al., 2022 for details), edited the paper, and assisted with ﬁgure design.
K.N.K. designed and supervised the original neuroimaging experiments
and analyses (see Allen et al., 2022 for details), edited the paper, and co-
supervised the project (analysis, ﬁgures, and writing). M.J.A. provided
ROI labels, edited the paper, and co-supervised the project (analysis,
ﬁgures, and writing).
Competing interests
The authors declare no competing interests.
Additional information
Supplementary information The online version contains
supplementary material available at
https://doi.org/10.1038/s41467-025-67472-3.
Correspondence and requests for materials should be addressed to
Daniel R. Guest.
Peer review information Nature Communications thanks Robbe Goris,
Maximilian Riesenhuber and the other anonymous reviewer(s) for their
contribution to the peer review of this work. A peer review ﬁle is avail-
able.
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
© The Author(s) 2025
Article
https://doi.org/10.1038/s41467-025-67472-3
Nature Communications|   (2026) 17:789 
12


