# *** (2025) Comprehensive Neural Representations of Naturalistic Stimuli through Multimodal Deep Learning

**Source:** *** (2025) Comprehensive Neural Representations of Naturalistic Stimuli through Multimodal Deep Learning.pdf

---

## Page 1

|
Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
1 of 43
Comprehensive Neural
Representations of Naturalistic
Stimuli through Multimodal Deep
Learning
Mingxue Fu, Guoqiu Chen, Yijie Zhang, Mingzhe Zhang, Yin Wang
State Key Laboratory of Cognitive Neuroscience and Learning, and IDG/McGovern Institute for Brain Research,
Beijing Normal University, Beijing, China
eLife Assessment
This study presents a valuable application of a video-text alignment deep neural network
model to improve neural encoding of naturalistic stimuli in fMRI. The authors provide
convincing evidence that models based on multimodal and dynamic embedding features
of audiovisual movies predicted brain responses better than models based on unimodal
or static features. The work will be of interest to researchers in cognitive neuroscience
and AI-based brain modeling.
https://doi.org/10.7554/eLife.107607.2.sa4
Abstract
A central challenge in cognitive neuroscience is understanding how the brain represents and
predicts complex, multimodal experiences in naturalistic settings. Traditional neural encoding
models, often based on unimodal or static features, fall short in capturing the rich, dynamic
structure of real-world cognition. Here, we address this challenge by introducing a video-text
alignment encoding framework that predicts whole-brain neural responses by integrating visual
and linguistic features across time. Using a state-of-the-art deep learning model (VALOR; Vision-
Audio-Language Omni-peRception), we achieve more accurate and generalizable encoding than
unimodal (AlexNet, WordNet) and static multimodal (CLIP) baselines. Beyond improving
prediction, our model automatically maps cortical semantic spaces, aligning with human-
annotated dimensions without requiring manual labeling. We further uncover a hierarchical
predictive coding gradient, where different brain regions anticipate future events over distinct
timescales—an organization that correlates with individual cognitive abilities. These findings
provide new evidence that temporal multimodal integration is a core mechanism of real-world
brain function. Our results demonstrate that deep learning models aligned with naturalistic
stimuli can reveal ecologically valid neural mechanisms, offering a powerful, scalable approach
for investigating perception, semantics, and prediction in the human brain. This framework
advances naturalistic neuroimaging by bridging computational modeling and real-world
cognition.
Introduction
One of the central goals of neuroscience is to understand how the brain interprets and integrates
information from the rich, dynamic, and multidimensional world we experience every day. Neural
encoding models have proven valuable in this effort, offering quantitative predictions of brain
activity under various conditions and providing insight into how information is represented in the
brain1–3. Early work in this area focused on highly controlled, simplified stimuli to establish
foundational principles. However, it is now widely recognized that such designs do not reflect the
complex, continuous, and context-rich nature of real-world cognition. Rather than responding to
For correspondence:
mirrorneuronwang@gmail.com
Competing interests: No
competing interests declared
Funding: See page 19
Reviewing editor: Anna C Schapiro,
University of Pennsylvania, United
States
© 2025, Fu et al. This article is
distributed under the terms of the
Creative Commons Attribution
License, which permits unrestricted
use and redistribution provided that
the original author and source are
credited.
Reviewed Preprint
v1 • August 26, 2025
Not revised
Reviewed Preprint
v2 • March 2, 2026
Revised by authors


## Page 2

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
2 of 43
isolated, static inputs, the brain continuously processes streams of multisensory information,
integrates them over time, and interprets them within dynamic environments. This realization has
motivated a growing push toward encoding models that better reflect the richness and variability
of naturalistic experience 4,5.
Naturalistic paradigms—such as movie watching—have emerged as powerful tools for studying
brain function in ecologically valid contexts6,7. Functional MRI (fMRI) during movie viewing
increases participant engagement and enables researchers to investigate how the brain processes
complex, time-varying inputs. Building on this foundation, several influential studies have
modeled cortical responses to naturalistic stimuli using visual and semantic features 5,8,9, while
others have advanced applications in non-invasive neural decoding5,8,9. These efforts have
deepened our understanding of brain function in real-world settings. Yet, most existing encoding
models are limited to a single modality, such as vision or language 4,10–12. Visual models (e.g.,
AlexNet11) perform well in early visual regions but generalize poorly to high-level areas, while
semantic models (e.g., WordNet13) perform the opposite. Critically, semantic models often rely on
dense human annotation. In early naturalistic encoding studies, trained raters watched the
stimulus and labeled what was happening within each TR or short time window—for example,
identifying objects, actions, or events present in the scene. These labels were then mapped onto a
predefined semantic ontology (such as WordNet), yielding high-dimensional categorical feature
vectors that served as regressors in encoding models. While this approach provides interpretable
semantic features, it is labor-intensive, time-consuming, and inherently subjective, as annotations
depend on rater judgment, labeling guidelines, and dataset-specific conventions, limiting
scalability and reproducibility. These limitations highlight the need for automated, multimodal
approaches that can more fully capture how the brain responds to naturalistic stimuli.
A second major challenge in naturalistic neuroimaging is improving model generalizability—the
ability to predict brain responses to new, unseen stimuli. Many current models show sharp
performance declines outside their training distribution. For example, a recent study reported that
encoding models trained on one image set dropped to 20% accuracy when tested on out-of-
distribution stimuli 14. Unimodal models may generalize within specific cortical domains but fail
in broader, whole-brain contexts. To build truly useful encoding models, we must develop
approaches that generalize across diverse stimuli, subjects, and cognitive domains.
These challenges have spurred the growth of ‘AI for neuroscience’, a field that uses advances in
deep learning to model brain function with increasing accuracy15,16. Deep neural networks have
shown promise in predicting neural responses to sensory and cognitive inputs17. However, many
of these models remain modality-specific, limiting their ability to mirror how the brain integrates
multisensory information 4,10–12. As a result, researchers are turning to multimodal deep learning,
which learns from visual, linguistic, and auditory streams to model complex brain functions18–20.
This trend is supported by neuroscience evidence that cortical responses across regions can be
jointly modeled within a common representational space 21,22. Still, popular models like CLIP
(Contrastive Language-Image Pretraining) 23—while successful in aligning image and text features
—treat perception as a series of static snapshots, falling short of capturing the temporal continuity
central to real-world cognition. Because the brain processes stimuli as events unfolding over time,
models that incorporate temporal structure, such as video-text alignment, may offer a more
biologically plausible and cognitively meaningful framework.
In this study, we ask a fundamental question in cognitive neuroscience: How can we build models
that accurately predict whole-brain neural responses to rich, dynamic, and naturalistic
experiences? To answer this, we apply a video-text alignment encoding framework, using VALOR
(Vision-Audio-Language Omni-peRception) 24—a high-performing, open-source model that aligns
visual and linguistic features over time—to predict brain responses during movie watching. By
analyzing naturalistic fMRI data from the Human Connectome Project (HCP) 25, we conducted four
experiments (Fig. 1     ) to show that our model (1) achieves superior predictive accuracy across
both sensory and high-order cognitive areas, (2) generalizes robustly to out-of-distribution stimuli
(ShortFunMovies dataset), (3) automatically maps semantic dimensions of cortical organization
without manual labeling, and (4) reveals predictive coding gradients linked to individual
Neuroscience


## Page 3

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
3 of 43
differences in cognitive ability. Together, these findings demonstrate that multimodal, temporally
aligned models offer a powerful and ecologically valid approach to understanding how the brain
processes complex, real-world information.
Results
Study 1: Enhanced whole-brain encoding with video-text
alignment
In Study 1, we tested whether video-text alignment features offer superior whole-brain neural
encoding compared to unimodal and image-based multimodal approaches. We analyzed high-
resolution 7T fMRI data from 178 participants in the Human Connectome Project (HCP) as they
passively watched one hour of movie stimuli. The movie segments were split into training and test
sets, and voxel-wise encoding models were built using kernel ridge regression 26 to predict brain
responses from four types of input features: (1) AlexNet (visual features), (2) WordNet (semantic
features), (3) CLIP (image-based multimodal features), and (4) VALOR, a video-text alignment
model that encodes multimodal features from continuous video sequences (Fig. 1b     ).
As shown in Fig. 2a      (left panel), each model exhibited domain-specific strengths: AlexNet
performed best in early visual regions, while WordNet, CLIP, and VALOR achieved higher accuracy
in language-related and high-level association areas. However, VALOR stood out by achieving
significantly higher whole-brain prediction accuracy than all other models (all ps < .04, FDR
corrected). To quantify these effects, we computed average prediction accuracy within three sets
of regions of interest (ROIs): (1) Visual cortex including V1 and V4, (2) Language-related regions
including middle temporal gyrus (MTG) and angular gyrus (AG), and (3) High-level association
areas including precuneus (PCu), posterior cingulate cortex (PCC) and medial prefrontal cortex
(mPFC).
As shown in Fig. 2a      (right panel), AlexNet outperformed others in visual regions, while WordNet
and the multimodal models performed better in language and association areas. Importantly,
VALOR matched WordNet in language and high-level regions but surpassed CLIP across multiple
ROIs, particularly in the precuneus and PCC. Moreover, VALOR showed significantly higher
accuracy in visual cortex than WordNet (all ps < .001), demonstrating its balanced predictive
coverage across both sensory and cognitive domains. These results were further supported by
representational similarity analysis, which revealed stronger correspondence between VALOR
features and actual brain activity across ROIs (see Supplementary Fig. S1     ).
Together, these findings demonstrate that integrating visual and linguistic information over time
yields more accurate and comprehensive neural predictions than static or unimodal models. The
video-text alignment approach captures the temporal and semantic continuity of naturalistic
stimuli, offering a powerful framework for modeling whole-brain activity and advancing our
understanding of how the brain processes complex, dynamic experiences.
Study 2: Robust cross-dataset generalization through video-text
alignment
Generalizability is a key benchmark for neural encoding models, reflecting their capacity to
predict brain responses to unseen, out-of-distribution stimuli. To evaluate this, we tested whether
the video-text alignment model trained on the HCP dataset could generalize to an independent,
qualitatively distinct dataset. Specifically, we used our in-house ShortFunMovies (SFM) dataset, in
which 20 participants viewed eight short films—six animated and two live-action—differing
substantially in style and content from the HCP movies. Full dataset details and analysis
procedures are provided in the Methods.
As shown in Fig. 2b      (left panel), voxel-wise analysis revealed that VALOR (video-text alignment)
significantly outperformed all baseline models—including AlexNet (visual), WordNet (linguistic),
and CLIP (image-based multimodal)—across much of the cortex. ROI-level analysis confirmed this
Neuroscience


## Page 4

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
4 of 43
Fig. 1. Overview of the Study Design.
a Encoding model construction and generalization testing (Study 1 & Study 2). Left panel: Whole-brain BOLD responses were
recorded while participants viewed naturalistic movies from the HCP 7T dataset. Visual, linguistic, and multimodal (video–text
aligned) features were extracted at each TR and used to train voxel-wise encoding models. During training, the encoding
model learns voxel-specific weight matrices that map stimulus features to BOLD responses, capturing each voxel’s feature
tuning. Right panel: To assess generalization, the learned voxel-wise weights were held fixed and applied to features
extracted from novel movies in an independent dataset (ShortFunMovies, SFM), collected at a different site with different
participants. Predicted BOLD responses were compared with empirically measured group-mean fMRI responses in the SFM
dataset using Pearson correlation, providing a test of cross-subject and cross-dataset transfer of stimulus-locked
representations. b Schematic of the video–text alignment model (VALOR). VALOR encodes temporally extended video
segments (comprising multiple consecutive frames over several seconds) and their associated textual descriptions into
separate visual and linguistic embedding spaces. These representations are aligned into a shared 512-dimensional joint
embedding space via contrastive learning, such that matched video–text pairs are pulled together while mismatched pairs
are pushed apart. By operating on dynamic video input rather than isolated frames, VALOR captures both semantic content
and temporal structure, distinguishing it from static image–text alignment models such as CLIP. c Using VALOR to study
predictive coding (Study 4). To probe predictive coding, the encoding model was extended to include a temporal forecast
window. Features at the current time point (Ft) were combined with features from a future time point (Ft+d), where d denotes
the prediction distance in TRs. Comparing models with and without future features allowed us to quantify regional
differences in predictive timescales across cortex. All human-related images in this figure are AI-generated illustrations. No
real faces or identifiable individuals are shown.
Neuroscience


## Page 5

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
5 of 43
Fig. 2. Comparison of encoding and generalization performance across models.
a Whole-brain encoding performance (Study 1). Voxel-wise and ROI-level comparisons of four encoding models trained on
the HCP 7T dataset: VALOR (video-text alignment, red), AlexNet (visual features, blue), WordNet (semantic features, pink), and
CLIP (image-based multimodal features, gray). Left panel: Cortical surface maps show the best-performing model at each
voxel. Mean whole-brain prediction accuracy across participants, with VALOR significantly outperforming all baselines. Right
panel: ROI-wise prediction accuracy across predefined regions (e.g., visual, language, high-level association areas). Bars
indicate group-level means, with error bars denoting standard error of the mean (SEM). Statistical comparisons (two-sided
paired t-tests, FDR-corrected) are reported only between VALOR and each of the other models. b Generalization performance
on independent data (Study 2). Models trained on HCP data were tested on the independent ShortFunMovies (SFM) dataset
to assess generalizability. Left: Voxel-wise surface maps highlight where VALOR outperforms other models across cortex.
Right: ROI-level generalization performance, with color coding and statistical tests consistent with panel (a). For both voxel-
wise and ROI analyses, VALOR demonstrates broad generalization across both sensory and high-level regions, exceeding the
performance of all other models. For the display of larger brain rendering, please check the Supplementary material (Figure
S4     )
Neuroscience


## Page 6

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
6 of 43
pattern: VALOR consistently achieved higher prediction accuracy across nearly all unimodal and
multimodal brain regions (Fig. 2b     , right panel). These results underscore the importance of
temporally integrated multimodal representations for capturing generalizable brain responses.
Although this analysis is not a classical within-subject out-of-distribution generalization test, it
evaluates the extent to which different feature spaces capture stimulus-locked representations
that are consistent across subjects and transferable across datasets, stimuli, and acquisition
environments. Notably, VALOR achieved this without requiring manual preprocessing steps such
as principal component analysis (PCA) or semantic annotation, unlike unimodal models. This
highlights its strength as a scalable, automated, and ecologically valid framework for modeling
brain activity in response to diverse, real-world stimuli.
Study 3: Comparing data-driven multimodal representations with
category-based semantic annotation
A central question in naturalistic encoding is how data-driven feature representations derived
from pretrained models relate to more interpretable, category-based semantic annotations that
have historically been used to study cortical semantic organization. Although recent work has
shown that pretrained language and vision–language models can capture semantic structure
without explicit annotation, category-based approaches such as WordNet remain valuable as
interpretable reference frameworks. Here, we leverage the WordNet-based semantic components
reported by Huth et al. (2012) 5 not as a state-of-the-art alternative, but as a historically grounded
benchmark, allowing a controlled comparison between data-driven multimodal representations
and manually defined semantic categories under matched naturalistic movie stimuli.
To test whether our model could automatically derive similar semantic structures, we applied the
video-text alignment encoding model to fMRI data from Huth et al. (2012), in which five
participants watched two hours of naturalistic movie clips. First, we assessed voxel-wise
prediction accuracy using our multimodal features. As shown in Fig. 3a      (and Supplementary Fig.
S2     ), the video-text alignment model consistently outperformed the original WordNet-based
model across most of the cortex. Next, we applied principal component analysis (PCA) to encoding
model weights, following the approach of Huth et al. (2012). Projecting stimulus features onto each
principal component (PC) revealed interpretable semantic dimensions, while projecting encoding
weights showed how each PC was represented across the cortex. Analysis of over 20,000 video
clips from VALOR’s training set revealed meaningful semantic axes. For instance, PC1
distinguished mobile vs. static content, PC2 separated social vs. non-social categories, PC3
contrasted mechanical vs. non-mechanical stimuli, and PC4 differentiated natural vs. civilizational
themes (Fig. 3b     ). These components closely mirrored those reported in the original WordNet-
based model. To quantify this similarity, we computed the Jaccard index between cortical
projections of the top four PCs from our model and those derived from WordNet features. As
shown in Fig. 3c     , we observed substantial spatial overlaps, indicating that our model recovered
the semantic organization of human brain comparable to human-labeled ground truth—without
any manual annotation.
Together, these results demonstrate that the video-text alignment encoding model can
automatically uncover meaningful, brain-wide semantic structures from naturalistic stimuli. This
provides a powerful and scalable alternative to manual labeling, offering new opportunities to
study semantic representations in the human brain with greater efficiency and ecological validity.
Study 4 Neural predictive coding mechanisms through video-text
alignment
Predictive processing is a core principle of brain function by which the brain interprets and
interacts with the world through actively anticipating future events and continuously updating its
internal model to minimize prediction errors27. While much of the existing evidence for predictive
coding has come from tightly controlled experimental settings28–30, its manifestation during
naturalistic experiences remains less understood.
Neuroscience


## Page 7

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
7 of 43
Fig. 3. Cortical semantic mapping from video-text alignment features.
a Voxel-wise prediction performance. Top: Encoding accuracy maps based on video-text alignment features (VALOR) versus
WordNet-based semantic features from Huth et al. (2012). Bottom: Difference map showing voxel-wise performance gains
(VALOR minus WordNet). Red areas indicate regions where VALOR outperforms WordNet. Results are shown for one
representative subject; similar patterns were observed in the remaining four participants (see Supplementary Fig. S2     ). b
Semantic dimensions revealed by video-text alignment. Principal component analysis (PCA) was applied to encoding weights
derived from VALOR features across ∼20,000 video clips. Example frames illustrate the semantic meaning of the top four PCs:
PC1=Mobility (e.g., movement vs. stillness; aligns with Huth’s PC1), PC2=Social content (e.g., people interaction vs. nature;
aligns with Huth’s PC2), PC3=Mechanical vs. non-mechanical stimuli (aligns with Huth’s PC4), PC4=Civilization vs. natural
environments (aligns with Huth’s PC3). All human-related images in this figure have been replaced with AI-generated
illustrations to avoid including identifiable individuals. No real faces or photographs of people are shown. c Spatial
correspondence with manually annotated semantic maps in Huth et al, (2012). Jaccard similarity matrix quantifying spatial
overlap between the top four PCs from the VALOR model (rows) and those from the WordNet-based model (columns). The
highest similarity scores for each column were diagonal, indicating strong alignment between automatically derived and
manually annotated semantic components. Detailed projections of each semantic component onto the cortical surface can be
found in the Supplementary Material (Fig. S3     ).
Neuroscience


## Page 8

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
8 of 43
To investigate predictive coding in an ecologically valid context, we used the HCP 7T fMRI dataset,
focusing on runs where participants viewed Hollywood films—narratives that naturally engage
anticipation and inference. We then tested whether incorporating representations of upcoming
events—using a “forecast window”—could improve the video-text alignment encoding model’s
prediction of neural responses (Fig. 1c     ). Specifically, for each time point, we combined the
current feature representation (Ft) with that of a future segment (Ft+d), where d indicates the
prediction distance 31. Comparing models with and without future information yielded “predictive
scores”, which quantify the neural benefit of forward-looking representations.
As shown in Fig. 4a     , several regions exhibited significant predictive enhancements, including
the superior temporal gyrus (STG), middle temporal gyrus (MTG), superior parietal gyrus (SPG),
and precuneus (PCu). These findings suggest that the brain actively anticipates upcoming content
during movie viewing. To test whether different brain areas operate on distinct predictive
timescales, we calculated a “prediction distance” metric for each voxel. Averaging these distances
across four ROIs revealed a hierarchical gradient: the STG showed shorter-range predictions, while
the MTG, SPG, and especially the PCu anticipated further into the future (Fig. 4b     ). This pattern
aligns with theories of cortical hierarchy32–34, suggesting that higher-order regions integrate
information over longer temporal windows.
Finally, we examined whether prediction horizons were linked to individual differences in
cognition. We focused on fluid intelligence (gF) because gF is widely taken to index domain-
general capacities such as maintaining and updating relational context over several seconds,
integrating multiple constraints, and exerting flexible top-down control — functions that should
support anticipating what will happen next in a continuous narrative. We targeted two parietal
regions, the SPG and the PCu, which have both been repeatedly linked to gF and high-level
cognitive control in the individual-differences literature35,36. For each participant, we correlated
fluid cognition scores with that participant’s average prediction horizon in each region. As shown
in Fig. 4c     , individuals with longer prediction horizons in SPG showed higher fluid cognition
scores (SPG: r = 0.172, FDR-corrected p = 0.047). PCu showed a similar positive trend (PCu: r =
0.111, FDR-corrected p = 0.146) but did not reach significance. These associations suggest that the
ability to sustain a longer predictive timescale during naturalistic perception co-varies with
broader fluid cognitive capacity. No additional brain regions or behavioral measures were
examined in this analysis.
In summary, these results show that the video-text alignment model not only captures real-time
brain responses to ongoing stimuli but also reveals how the brain projects forward in time,
supporting hierarchical prediction and linking anticipatory processing to individual cognitive
abilities.
Discussion
This study introduces video-text alignment encoding as a powerful and ecologically valid
framework for modeling whole-brain responses to naturalistic stimuli. By integrating visual and
linguistic features over time, our approach addresses long-standing limitations in traditional
encoding models and offers key advances across four dimensions: predictive accuracy (Study 1),
cross-dataset generalization (Study 2), semantic space mapping (Study 3), and predictive coding
mechanisms (Study 4). Collectively, these findings demonstrate that temporally aligned
multimodal deep learning can uncover how the brain processes complex, dynamic information in
real-world contexts.
In Study 1, we show that video-text alignment models outperform both unimodal and static
multimodal approaches in predicting cortical activity (Fig. 2a     ). While AlexNet and WordNet
capture localized visual or linguistic responses, respectively, they fail to generalize beyond their
domains. In contrast, VALOR—which fuses visual and linguistic information over time—achieves
high prediction accuracy across both low-level sensory and high-level integrative regions,
including the precuneus (PCu), insula, and medial prefrontal cortex37–39. VALOR matches WordNet
in language regions (e.g., angular gyrus) and significantly outperforms it in visual areas (e.g., V1,
V4), underscoring that semantic models alone are insufficient to capture naturalistic perception.
Neuroscience


## Page 9

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
9 of 43
Fig. 4. Predictive coding revealed by video-text alignment features.
a voxel-wise predictive scores. For each voxel, a predictive score was computed as the improvement in prediction accuracy
when future stimulus features (Ft+d) were added to current features (Ft) in the encoding model. Only voxels with significant
predictive enhancement across participants are shown (Wilcoxon rank-sum test, FDR-corrected). b regional prediction
distances. Voxels that showed highest predictive scores were STG, MTG, SPG and PCu. We calculated prediction distance for
these regions on a per-voxel, per-participant basis, and then averaged the values. c brain–behavior correlation. Scatter plot
showing a positive correlation between prediction distance in the SPG and individual fluid cognitive scores across HCP
participants (r = 0.172, p < .05, FDR-corrected). This suggests that individuals with broader predictive horizons in the parietal
cortex tend to exhibit stronger fluid reasoning ability.
Neuroscience


## Page 10

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
10 of 43
Additionally, VALOR exceeds the performance of CLIP, a leading static multimodal model, as its
training objective aligns multi-second video–text units, enforcing a temporal integration window
and event-level semantics that maintain cross-frame consistency and narrative context, whereas
CLIP’s image-level alignment provides no intrinsic mechanism for such temporal continuity 40.
More broadly, this difference reflects distinct inductive biases in how the two models represent
visual–linguistic information. CLIP is optimized for framewise image–text correspondence,
encouraging representations that emphasize instantaneous visual semantics but remain agnostic
to temporal structure. In contrast, VALOR is explicitly biased toward aggregating information over
multiple consecutive frames and aligning representations at the level of temporally extended
events. These inductive biases favor context maintenance, semantic stabilization, and narrative
coherence over time, which are known to be critical for driving responses in association cortex
during continuous movie perception. Interestingly, both VALOR and CLIP showed unexpectedly
high accuracy in traditionally unimodal sensory areas (e.g., certain voxels in cuneus and lingual
gyrus, see Fig. 2a     , left panel), suggesting that even early visual cortex may integrate multimodal
information during dynamic, real-world experiences 41,42. This conclusion is further supported by
representational similarity analysis (Supplementary Fig. S1     ), which shows VALOR’s feature
space aligns more closely with measured brain activity than all other models. Together, the
relative gains over AlexNet (purely visual), WordNet (manual semantic annotation), and CLIP
(static image–text alignment) indicate cortical systems whose responses are best captured by
multi-second, multimodal integration, and highlight regions that accumulate and stabilize
narrative context over time. At the same time, these findings do not imply that visual–text
alignment in the brain gives rise to fully amodal, modality-independent semantic representations.
Instead, we suggest that alignment between visual and linguistic signals may serve to stabilize and
coordinate scene-level meaning across modalities and over time. From this perspective, VALOR’s
architecture—by integrating visual information over multi-second windows and aligning
temporally extended video segments with language—provides a computational proxy for how the
brain may use linguistic constraints to organize, disambiguate, and maintain coherent
representations of unfolding events. The observed encoding gains therefore highlight regions
engaged in temporally stabilized, cross-modal integration during naturalistic perception, rather
than providing evidence for abstract semantic codes divorced from sensory input.
Beyond predictive accuracy, Study 2 highlights the ecological validity of video-text alignment
models by demonstrating their robust generalization to novel stimuli (Fig. 2b     ). Traditional
unimodal models (e.g., AlexNet, WordNet) require manual preprocessing (e.g., PCA, annotation
alignment) to adapt to new datasets, while static image-based multimodal models (e.g., CLIP) lack
temporal structure, limiting their ability to capture dynamic neural responses. By contrast, VALOR
exhibited stronger generalization in a cross-cohort, cross-stimulus, and cross-site transfer
evaluation. Together, these findings underscore the importance of distinguishing encoding models
that primarily capture shared, stimulus-driven neural structure from those whose performance
relies more heavily on subject-specific heterogeneity, particularly when evaluating generalization
across participants and datasets. Consistent with this distinction, integrating visual and semantic
information over time appears to support more stable and flexible neural representations. This
aligns with the idea that the brain continuously adapts to ever-changing environments by
integrating multimodal cues across time 10,43. By demonstrating robust performance across
different datasets, our approach moves beyond static encoding models toward a framework that
more closely reflects the brain’s natural adaptability and predictive processing, advancing the ‘AI
for neuroscience’ field toward more biologically plausible models of real-world cognition 44–47.
Study 3 demonstrates the utility of video–text alignment models for probing higher-order semantic
representations during naturalistic perception. Our comparison between VALOR-derived
representations and WordNet-based semantic components highlights an important distinction
between data-driven and category-based approaches to modeling meaning in the brain. While
multimodal pretrained models offer flexible, high-dimensional representations that capture
semantic structure without explicit annotation, category-based frameworks provide
interpretability and theoretical anchoring 4,48. Using WordNet-based labeling from prior work as
an interpretable reference point, we show that VALOR automatically extracts semantic dimensions
Neuroscience


## Page 11

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
11 of 43
—including mobility, sociality, and civilization—that closely mirror those identified using manual
semantic categories (Fig. 3     ). The observed alignment between VALOR PCs and WordNet
semantic components suggests that large-scale semantic organization emerges consistently across
these approaches, even though they differ in how semantic structure is defined and learned. This
convergence supports the use of pretrained multimodal models as practical encoding tools for
naturalistic stimuli, while also underscoring the continued value of interpretable semantic
benchmarks for understanding which aspects of meaning are represented across cortex. We do
not argue that semantic annotation is required for modern encoding models; rather, WordNet-
based features serve here as a historically grounded and interpretable reference for
contextualizing data-driven multimodal representations.
In Study 4, we used a video-text alignment model to investigate predictive coding mechanisms.
Because our analysis incorporates only future-aligned features, the reported effects should be
interpreted as reflecting forward-oriented representations rather than generic sensitivity to
temporal context; directly contrasting past- and future-aligned features will be an important
direction for future work. By incorporating a forecast window, we found that different brain
regions encode future events over distinct timescales (Fig. 4a–b     ). Short-term predictions were
strongest in the superior temporal gyrus (STG), while longer-range forecasts emerged in regions
such as the precuneus (PCu), consistent with theories of cortical hierarchy 32–34,49. Notably, we
observed that individuals with longer prediction distances in the superior parietal gyrus (SPG)
exhibited higher fluid cognition scores. This finding suggests a potential link between anticipatory
processing and individual cognitive capacity, offering new insights into how the brain predicts and
organizes unfolding information in complex environments.
Despite these advances, several limitations remain. First, our analyses relied on a single
multimodal architecture (VALOR), operated primarily on TR-level features, and were validated in
part on a relatively small independent cohort (n = 20); future work should test whether the same
principles hold across alternative models, longer adaptive temporal windows, and larger, more
diverse samples. Second, we did not directly compare VALOR to state-of-the-art video-only
spatiotemporal models (e.g., Video Swin Transformer, VideoMAE, and related architectures) that
are designed to capture temporal visual structure without language grounding; such comparisons
will be important for isolating the specific contributions of temporal visual processing versus
cross-modal video–text alignment in naturalistic neural responses. Third, for comparability across
models we evaluated each model using its single best-performing layer within a matched encoding
pipeline rather than using multilayer fusion or ensembling, which allowed us to attribute
performance differences to representational format but likely underestimates the absolute
performance ceiling. Finally, Finally, part of VALOR’s advantage may reflect model capacity: larger
pretrained models often yield higher encoding accuracy, so repeating these analyses with size-
matched image-only and image–text models will be critical for disentangling model scale from
representational content.
In conclusion, this work establishes video-text alignment encoding as a robust, scalable, and
biologically informed framework for studying the brain’s response to naturalistic stimuli. By
capturing the temporal and semantic richness of real-world input, this approach advances the
field beyond static, modality-limited models and provides new tools for investigating semantic
cognition, predictive processing, and individual differences. Beyond theoretical insights, our
framework holds practical promise for applications in brain-computer interfaces, clinical
neuroimaging, and the development of next-generation cognitive models. As encoding models
evolve, video-text alignment stands out as a crucial bridge between deep learning and naturalistic
neuroscience, bringing us closer to a comprehensive understanding of the brain in action.
Neuroscience


## Page 12

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
12 of 43
Methods
HCP Naturalistic fMRI Dataset
We analyzed high-resolution 7T fMRI data from 178 individuals who participated in the HCP
movie-watching protocol. The dataset included four audiovisual movie scans (1 hour in total) with
varying content, from Hollywood film clips to independent Vimeo videos. The fMRI data
underwent preprocessing using the HCP pipeline, which included correction for motion and
distortion, high-pass filtering, regression of head motion effects using the Friston 24-parameter
model, removal of artifactual time series identified with ICA, and registration to the MNI template
space. Further details on data acquisition and preprocessing can be found in previous
publications25,50. For our analysis, we excluded rest periods and the first 20 seconds of each movie
segment, resulting in approximately 50 minutes of audiovisual stimulation data paired with the
corresponding fMRI response.
Movie Feature Extraction
1. Video–text alignment features (VALOR): To extract video-based multimodal features, we
used VALOR (VALOR-large checkpoint), an open-source pretrained video–text alignment
model24. VALOR combines visual encoders (CLIP and Video Swin Transformer) for extracting
visual features and a text encoder (BERT) for extracting textual features 23,51,52. These
representations are aligned in a shared embedding space through contrastive learning. We
segmented each movie at the TR level and, for each segment, extracted VALOR’s projected
video–text embedding from the final projection head of the alignment module to obtain a
512-dimensional feature vector. These embeddings were then time-aligned to the
corresponding BOLD responses.
2. CLIP features: To compare with static image-based multimodal models, we utilized CLIP (ViT-
B/32), which aligns visual and textual representations through contrastive learning but
processes individual frames independently without capturing temporal context. One video
frame was sampled per TR, and the pooled image embedding after CLIP’s projection into the
shared image–text space was extracted to obtain a 512-dimensional feature vector. These
TR-aligned vectors were used directly as regressors in the voxel-wise encoding models.
3. AlexNet features: Visual features were extracted by sampling frames at the TR level and
processing them with AlexNet, an eight-layer convolutional neural network comprising five
convolutional layers followed by three fully connected layers. Features from all five
convolutional layers were evaluated in preliminary analyses; the fifth convolutional layer
showed the best performance and was used in subsequent analyses. Intra-image z-score
normalization was applied to reduce amplitude effects. Principal component analysis (PCA)
was used to reduce dimensionality, retaining the top 512 components to match the
dimensionality of multimodal feature spaces. This pipeline was implemented using the
DNNBrain toolkit 53.
Neuroscience


## Page 13

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
13 of 43
4. WordNet features: Semantic features were obtained from publicly available WordNet
annotations provided with the HCP dataset (7T_movie_resources/WordNetFeatures.hdf5),
following the procedure of Huth et al. (2012). Throughout this manuscript, we use the term
“semantic features” to refer to such human-annotated, category-based representations of
scene content, and we reserve the term “linguistic features” for continuous language
embeddings derived automatically from pretrained language or vision–language models.
Each second of the movie clips was manually annotated with WordNet categories according
to predefined guidelines: (a) identifying clear objects and actions in the scene; (b) labeling
categories that dominated for more than half of the segment duration; and (c) using specific
category labels rather than general ones. A semantic feature matrix was constructed with
rows corresponding to time points and columns to semantic categories, with category
presence coded as binary values. More specific categories from the WordNet hierarchy were
added to each labeled category, yielding a total of 859 semantic features. These features
were used directly as regressors. We also evaluated a PCA-reduced 512-dimensional variant
(fit within each training fold to avoid leakage); because this version performed slightly
worse, we report results from the full 859-dimensional representation in the main text. For
the generalization analysis in Study 2, annotations for the SFM dataset were aligned to the
same WordNet category space to ensure consistency.
These processes described above were performed on a compute node equipped with two Intel(R)
Xeon(R) Platinum 8383C CPUs and three NVIDIA GeForce RTX 4090 GPUs. To comply with the
journal’s policy, we replaced all human-related video frames used for illustrative purposes (e.g., in
Fig. 1      and Fig. 3     ) with AI-generated images that do not depict real individuals. These synthetic
images were created solely for explanatory visualization and were not used in any model training,
testing, or analysis.
Voxel-wise encoding models
Voxel-wise encoding models were created to establish connections between different stimuli and
the corresponding brain responses. These models were developed for each individual using visual,
linguistic, and multimodal features, and kernel ridge regression was used to map them to brain
activation while preserving the interpretability of the model weights. The training set consisted of
all movie segments from the HCP 7T movie dataset, excluding repeated segments, while the test set
consisted of the repeated segments to improve noise reduction and reliability by averaging the
brain imaging data over four runs per participant. A finite impulse response model with four
delays (2, 4, 6, and 8 seconds) was used to account for the hemodynamic response. The
regularization parameters for each voxel and subject were optimized through 10-fold cross-
validation, exploring 30 parameters ranging logarithmically from 10 to 1030. Model performance
was assessed on the test data by calculating Pearson correlation coefficients between predicted
and observed voxel activation sequences.
Novel movie dataset for generalizability test
To evaluate the generalizability of encoding models trained on the HCP dataset, we collected a new
fMRI dataset—referred to as “ShortFunMovies”(SFM)—from 20 adult female Chinese participants
(mean age = 23.76 ± 2.26 years). This dataset offers exceptional stimulus diversity through eight
different movie segments (45 mins in total), including six animations and two live actions, that
differ markedly in content and style from the HCP movie stimuli. Each participant watched these
eight audiovisual movies while undergoing an fMRI scan using a 3 Tesla Siemens Prisma
Magnetom scanner at the MRI Center of Beijing Normal University. The scanning parameters were
as follows: TR = 2000 ms, TE = 30 ms, flip angle = 90°, FOV = 210 × 210 mm, spatial resolution = 2.5
mm3, and multiband factor = 6. After preprocessing the fMRI data with fMRIPrep, we denoised
and smoothed the brain imaging data (fwhm = 6 mm). We then extracted visual, linguistic, image-
based and video-based multimodal features from the movie stimuli and fed them into subject-
specific encoding models that were pretrained on the HCP dataset. These models were used to
predict each individual’s brain activation patterns in response to the new stimuli. To assess the
Neuroscience


## Page 14

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
14 of 43
generalizability of the models, we calculated Pearson correlation coefficients between the
predicted brain activations of each HCP subject models and the actual group-level mean activation
observed in participants exposed to the new movie dataset. This new data collection was approved
by the Institutional Review Board of Beijing Normal University (IRB_A_0024_2021002), and
informed consent was obtained from all participants. All participants received monetary
compensation after completing the MRI scanning. The SFM dataset was deposited in the OSF
website.
Semantic space analysis
Whole-brain semantic space analysis has traditionally relied on manual stimulus annotation. Huth
et al. (2012) created a semantic feature matrix by manually annotating video content and decoding
semantic dimensions across the brain. To address this challenge, we wanted to verify whether our
video-text alignment model could accurately and efficiently automate the analysis of whole-brain
semantic space. Therefore, we repeated Huth et al.’s analysis and compared our results with
theirs.
We first fit voxel-wise encoding models using VALOR features for each of the five participants in
the Huth et al. dataset. For each participant, this yielded a weight map linking each VALOR feature
to each voxel. We then stacked these weight maps across participants to form a single voxel-by-
feature weight matrix and applied principal component analysis (PCA).
The top four principal components from this analysis (“VALOR PCs”) captured shared spatial
patterns of VALOR feature weights across cortex. To interpret these components, we projected
VALOR feature vectors from >20,000 video segments in the VALOR training set onto each PC, which
revealed dominant semantic axes (e.g., mobility, sociality, civilization). For comparison, we used
the semantic principal components reported by Huth et al. (2012) from their WordNet-based
encoding model; these “WordNet PCs” were taken directly from the published work and were not
refit or reweighted using VALOR. To analyze how PCs from WordNet and video-text alignment
features are distributed in the cortex, we projected their weights onto the cortical surfaces of
subjects. By calculating Jaccard coefficients for the PC distributions in both encoding models, we
measured variations and similarities across different cortical regions. The overall Jaccard index,
obtained by averaging these coefficients across all participants, provides a comprehensive view of
the shared neural patterns.
Probing Predictive Coding Mechanisms
To test predictive coding when watching movies, we incorporated forecast representations— so-
called ‘forecast window’ — and examined whether this significantly improved the prediction
accuracy of video-text alignment encoding models across different voxels31. These forecast
windows, denoted as Ft+d, include features extracted by the video-text alignment model from n-
second clips, where n aligns with the TR duration of one second. The end frame of each segment is
aligned with a temporal offset d from the current TR. Ft+d contains information from a segment
subsequent to the current TR, reflecting the brain’s prediction mechanism for potential future
stimuli encounters.
For each subject s and voxel v, we calculated the ‘Brain score’ B(s,v), reflecting the effectiveness of
using features from the current TR clip to predict brain activation:
with W as the kernel ridge regression, Ft as the feature of the current TR clip, corr as Pearson’s
correlation and Y(s,v) as the fMRI signals of one individual s at one voxel v .
For each prediction distance d, subject s, and voxel v, we computed the ‘Brain score’ B(d,s,v),
reflecting the model’s accuracy when it includes features of the forecast window alongside the
present TR clip features:
Neuroscience


## Page 15

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
15 of 43
where Ft⊕Ft+d represents the integrated feature set combining the current and forecast clip
features.
The ‘Predictive score’ P(d,s,v) was computed as the improvement in brain score when
concatenating forecast windows to present multimodal features:
To ensure dimensionality compatibility between Ft ⊕ Ft+d, we applied PCA for dimensionality
reduction, reducing both feature types to 100 dimensions each.
We defined the optimal ‘prediction distance’ for each individual s and voxel v as:
This process utilized the HCP movie-watching dataset, specifically focusing on the second and
fourth runs due to their Hollywood film content, which typically evokes continual plot conjectures
during viewing, and regarded the last movie segment of run 4 as the test set and other segments as
the training set.
Supplementary Materials
Representational Similarity Analysis (RSA) in Study 1
To assess the relationship between video-text alignment features and neural activity prior to
constructing the encoding model, we conducted a representational similarity analysis (RSA). This
approach allowed us to evaluate how well different feature types—AlexNet (visual), WordNet
(linguistic), CLIP (image-based multimodal), and VALOR (video-based multimodal)—aligned with
multivoxel brain activation patterns across key cortical regions. We focused on three groups of
functionally defined regions of interest (ROIs): (i) Visual regions including V1 and V4, (ii)
Language-associated regions including middle temporal gyrus (MTG) and angular gyrus (AG), (iii)
Higher-order cognitive regions including medial prefrontal cortex (mPFC), posterior cingulate
cortex (PCC), and precuneus (PCu)
Each HCP movie run was split into 4–5 stimulus segments that exhibited consistency in visual or
linguistic content. Each segment was analyzed independently using a multivariate RSA
framework. We computed representational dissimilarity matrices (RDMs) based on pairwise
Pearson correlations between multivoxel patterns across timepoints (TRs), yielding TR-by-TR
matrices for each ROI. Corresponding feature-based RDMs were constructed for each model using
the extracted features. To account for the hemodynamic delay, the first four TRs of each run were
excluded. We then computed feature-brain RSA similarity by correlating each brain RDM with the
feature RDM using Spearman’s rank correlation. Analyses were performed at the individual
subject level and results were aggregated across participants for group-level comparisons. We
used paired-sample t-tests with FDR correction to assess statistical differences in RSA values
between models.
Figure S1      summarizes the results. In early visual cortex (V1), VALOR’s RSA performance
matched that of AlexNet and exceeded that of WordNet and CLIP. In V4, VALOR outperformed all
other models. In language areas (MTG and AG), VALOR showed substantially higher RSA values
than both unimodal and static multimodal features. This advantage also extended to high-level
cognitive regions (PCu, PCC), where VALOR consistently yielded the highest RSA scores. The mPFC
was the only region where VALOR and WordNet features performed comparably.
These results underscore the broad representational fidelity of video-text alignment features
across visual, language, and integrative networks. By capturing both semantic and temporal
structure, VALOR provides a more comprehensive approximation of real neural representations,
supporting its use in modeling whole-brain responses to naturalistic stimuli.
Neuroscience


## Page 16

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
16 of 43
Fig. S1. Representational similarity analysis (RSA) across feature types and brain regions.
Bar plots show RSA results comparing four feature extraction models—video-text alignment (VALOR), CLIP, AlexNet,
and WordNet—across seven predefined regions of interest (ROIs): V1, V4 (visual), MTG, AG (language), and PCu, PCC,
mPFC (higher-order cognitive regions). RSA values reflect the similarity between multivoxel neural patterns and
feature-derived representational dissimilarity matrices (RDMs), aggregated across all participants and movie
segments from the HCP 7T dataset. VALOR consistently outperformed or matched other models across most ROIs,
particularly in V4, MTG, AG, PCu, and PCC, indicating its ability to capture both low-level perceptual and high-level
semantic structure. In V1, VALOR was comparable to AlexNet. In mPFC, performance was similar between VALOR and
WordNet. Statistical comparisons were conducted using paired-sample t-tests, with false discovery rate (FDR)
correction applied for multiple comparisons. Asterisks indicate significance levels (*p < .05, ***p < .001); "n.s." = not
significant. Error bars represent ±1 standard error of the mean (SEM) across participants.
Neuroscience


## Page 17

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
17 of 43
Figure S2. Individual subject maps showing performance difference between feature models
(related to Figure 3a     ).
Cortical flat maps show voxel-wise differences in prediction accuracy between the video-text alignment model
(VALOR) and the WordNet-based semantic model, computed as VALOR minus WordNet. Data are shown for four
individual subjects (S2–S5) from the Huth et al. (2012) dataset. Red voxels indicate regions where VALOR achieved
higher prediction accuracy than WordNet; blue voxels reflect regions where WordNet outperformed VALOR. These
maps mirror the analysis presented in Figure 3a      (main text) and demonstrate that VALOR consistently
outperforms WordNet across a wide range of cortical areas, including both hemispheres and across subjects. The
color scale reflects the magnitude of performance differences, ranging from -0.10 to 0.10 in Pearson correlation
units.
Neuroscience


## Page 18

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
18 of 43
Figure S3. Projections of semantic components onto the cortical surface.
Left: Component 1 (PC1) loadings projected onto the individual surface of S1 as continuous, signed weights (color
bar indicates magnitude). Right: Components 2–4 displayed with a discrete scheme: PC2 = red, PC3 = green, PC4 =
blue (greater saturation denotes larger loadings; near-zero shown in gray).
Neuroscience


## Page 19

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
19 of 43
Figure S4. Cortical surface projections of voxel-wise winner-take-all maps showing the best-
performing representation at each voxel.
(a) Encoding performance on HCP (Study 1). (b) Generalization performance on SFM (Study 2; trained on HCP, tested
on SFM). Colors indicate the representation with the highest prediction accuracy: VALOR (red), AlexNet (blue),
WordNet (pink), and CLIP (gray).
Data availability
All data and analysis codes in this project were uploaded to Open Science Framework
(https://osf.io/2fnr4/     ).
Acknowledgements
This work was supported by National Natural Science Foundation of China (32422033, 32171032,
32430041), National Science and Technology Innovation 2030 Major Program (2022ZD0211000,
2021ZD0200500), Open Research Fund of the State Key Laboratory of Cognitive Neuroscience and
Learning (CNLZD2103) and the start-up funding from the State Key Laboratory of Cognitive
Neuroscience and Learning, IDG/McGovern Institute for Brain Research, Beijing Normal University
(to Y.W.)
Additional information
Author contributions
M.F. and Y.W. conceived and designed the research. M.F., G.C., Y.Z., and M.Z. collected and analyzed
the data. M.F., G.C., Y.Z., and M.Z. wrote the initial draft of the manuscript. M.F. and Y.W. edited and
reviewed the final manuscript.
Funding
Funder
Grant reference number
Author
MOST | National Natural Science Foundation
of China (NSFC)
32422033
Yin Wang
MOST | National Natural Science Foundation
of China (NSFC)
32171032
Yin Wang
MOST | National Natural Science Foundation
of China (NSFC)
32430041
Yin Wang
Author ORCID iDs
Yin Wang: https://orcid.org/0000-0002-3444-000X
Neuroscience


## Page 20

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
20 of 43
References
Naselaris T., Kay K. N., Nishimoto S., Gallant J. L. (2011) Encoding and decoding in fMRI. NeuroImage
56:400‑410 
Tang J., Du M., Vo V. A., Lal V., Huth A. G (2023) Brain encoding models based on multimodal
transformers can transfer across language and vision. arXiv  http://arxiv.org/abs/2305.12248
Wang A. Y., Kay K., Naselaris T., Tarr M. J., Wehbe L. (2023) Better models of human high-level visual
cortex emerge from natural language supervision with a large and diverse dataset. Nat. Mach. Intell
 https://doi.org/10.1038/s42256-023-00753-y
Huth A. G., Nishimoto S., Vu A. T., Gallant J. L (2012) A Continuous Semantic Space Describes the
Representation of Thousands of Object and Action Categories across the Human Brain. Neuron
76:1210‑1224 
Huth A. G., De Heer W. A., Griffiths T. L., Theunissen F. E., Gallant J. L (2016) Natural speech reveals the
semantic maps that tile human cerebral cortex. Nature 532:453‑458 
Finn E. S (2021) Is it time to put rest to rest?. Trends Cogn. Sci 25:1021‑1032 
Simony E., Chang C (2020) Analysis of stimulus-induced brain dynamics during naturalistic
paradigms. NeuroImage 216 
Wen H., Shi J., Chen W., Liu Z (2018) Transferring and generalizing deep-learning-based neural
encoding models across subjects. NeuroImage 176:152‑163 
Tang J., LeBel A., Jain S., Huth A. G (2023) Semantic reconstruction of continuous language from non-
invasive brain recordings. Nat. Neurosci 26:858‑866 
Khosla M., Ngo G. H., Jamison K., Kuceyeski A., Sabuncu M. R (2021) Cortical response to naturalistic
stimuli is largely predictable with deep neural networks. Sci. Adv 7:eabe7547 
Ratan Murty N. A., Bashivan P., Abate A., DiCarlo J. J., Kanwisher N. (2021) Computational models of
category-selective brain regions enable high-throughput tests of selectivity. Nat. Commun 12:5540 
Van Uden C. E., et al. (2018) Modeling Semantic Encoding in a Common Neural Representational
Space. Front. Neurosci 12 
Miller G. A., Beckwith R., Fellbaum C., Gross D., Miller K. J (1990) Introduction to WordNet: An On-line
Lexical Database*. Int. J. Lexicogr 3:235‑244 
Madan S., et al. (2024) Benchmarking Out-of-Distribution Generalization Capabilities of DNN-based
Encoding Models for the Ventral Visual Cortex. arXiv  http://arxiv.org/abs/2406.16935
Akkus C., et al. (2023) Multimodal Deep Learning. arXiv  http://arxiv.org/abs/2301.04856
Perez-Martin J., et al. (2022) A comprehensive review of the video-to-text problem. Artif. Intell. Rev
55:4165‑4239 
Yamins D. L. K., DiCarlo J. J (2016) Using goal-driven deep learning models to understand sensory
cortex. Nat. Neurosci 19:356‑365 
Dirani J., Pylkkänen L (2023) The time course of cross-modal representations of conceptual
categories. NeuroImage 277:120254 
Kehl M. S., et al. (2024) Single-neuron representations of odours in the human brain. Nature
634:626‑634 
Van Der Linden M., Van Turennout M., Fernández G (2011) Category Training Induces Cross-modal
Object Representations in the Adult Human Brain. J. Cogn. Neurosci 23:1315‑1331 
Du C., Fu K., Li J., He H (2023) Decoding Visual Neural Representations by Multimodal Learning of
Brain-Visual-Linguistic Features. IEEE Trans. Pattern Anal. Mach. Intell 45:10760‑10777 
Oota S. R., Arora J., Rowtula V., Gupta M., Bapi R. S. (2022) Visio-Linguistic Brain Encoding. arXiv  
http://arxiv.org/abs/2204.08261
Radford A., et al. (2021) Learning Transferable Visual Models From Natural Language Supervision.  
1.
2.
3.
4.
5.
6.
7.
8.
9.
10.
11.
12.
13.
14.
15.
16.
17.
18.
19.
20.
21.
22.
23.
Neuroscience


## Page 21

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
21 of 43
Chen S., et al. (2023) VALOR: Vision-Audio-Language Omni-Perception Pretraining Model and
Dataset. arXiv  http://arxiv.org/abs/2304.08345
Glasser M. F., et al. (2013) The minimal preprocessing pipelines for the Human Connectome Project.
NeuroImage 80:105‑124 
Dupré La Tour T., Eickenberg M., Nunez-Elizalde A. O., Gallant J. L. (2022) Feature-space selection with
banded ridge regression. NeuroImage 264:119728 
Millidge B., Seth A., Buckley C. L (2022) Predictive Coding: a Theoretical and Experimental Review.
arXiv  http://arxiv.org/abs/2107.12979
Meyer T., Olson C. R (2011) Statistical learning of visual transitions in monkey inferotemporal cortex.
Proc. Natl. Acad. Sci 108:19401‑19406 
Shain C., Blank I. A., Van Schijndel M., Schuler W., Fedorenko E (2020) fMRI reveals language-specific
predictive coding during naturalistic sentence comprehension. Neuropsychologia 138:107307 
Todorovic A., Van Ede F., Maris E., De Lange F. P (2011) Prior Expectation Mediates Neural Adaptation
to Repeated Sounds in the Auditory Cortex: An MEG Study. J. Neurosci 31:9118‑9123 
Caucheteux C., Gramfort A., King J.-R (2023) Evidence of a predictive coding hierarchy in the human
brain listening to speech. Nat Hum Behav 7:430‑441 
Baldassano C., et al. (2017) Discovering Event Structure in Continuous Narrative Perception and
Memory. Neuron 95:709‑721.e5 
Hasson U., Yang E., Vallines I., Heeger D. J., Rubin N (2008) A Hierarchy of Temporal Receptive
Windows in Human Cortex. J. Neurosci 28:2539‑2550 
Raut R. V., Snyder A. Z., Raichle M. E (2020) Hierarchical dynamics as a macroscopic organizing
principle of the human brain. Proc. Natl. Acad. Sci 117:20890‑20897 
Jung R. E., Haier R. J (2007) The Parieto-Frontal Integration Theory (P-FIT) of intelligence: Converging
neuroimaging evidence. Behav. Brain Sci 30:135‑154 
Preusse F., Elke V. D. M., Deshpande G., Krueger F., Wartenburger I (2011) Fluid Intelligence Allows
Flexible Recruitment of the Parieto-Frontal Network in Analogical Reasoning. Front. Hum. Neurosci 5 
Grall C., Equita J., Finn E. S (2023) Neural unscrambling of temporal information during a nonlinear
narrative. Cereb. Cortex 33:7001‑7014 
Kauttonen J., Hlushchuk Y., Jääskeläinen I. P., Tikka P (2018) Brain mechanisms underlying cue-based
memorizing during free viewing of movie Memento. NeuroImage 172:313‑325 
Richter F. R., Cooper R. A., Bays P. M., Simons J. S (2016) Distinct neural mechanisms underlie the
success, precision, and vividness of episodic memory. eLife 5:e18260 
https://doi.org/10.7554/eLife.18260
Rasheed H., Khattak M. U., Maaz M., Khan S., Khan F. S (2023) Fine-tuned CLIP Models are Efficient
Video Learners. In: 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR).
Vancouver, Canada. pp. 6545‑6554 https://doi.org/10.1109/CVPR52729.2023.00633
Bonnici H. M., Richter F. R., Yazar Y., Simons J. S (2016) Multimodal Feature Integration in the Angular
Gyrus during Episodic and Semantic Retrieval. J. Neurosci 36:5462‑5471 
Sepulcre J., Sabuncu M. R., Yeo T. B., Liu H., Johnson K. A (2012) Stepwise Connectivity of the Modal
Cortex Reveals the Multimodal Organization of the Human Brain. J. Neurosci 32:10649‑10661 
Driver J., Noesselt T (2008) Multisensory Interplay Reveals Crossmodal Influences on ‘Sensory-
Specific’ Brain Regions, Neural Responses, and Judgments. Neuron 57:11‑23 
Brodersen K. H., et al. (2011) Generative Embedding for Model-Based Classification of fMRI Data.
PLoS Comput. Biol 7:e1002079 
Kriegeskorte N., Douglas P. K. (2019) Interpreting encoding and decoding models. Curr. Opin.
Neurobiol 55:167‑179 
24.
25.
26.
27.
28.
29.
30.
31.
32.
33.
34.
35.
36.
37.
38.
39.
40.
41.
42.
43.
44.
45.
Neuroscience


## Page 22

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
22 of 43
Sohn W., Di X., Liang Z., Zhang Z., Biswal B. B (2024) Explorations of using a convolutional neural
network to understand brain activations during movie watching. Psychoradiology 4:kkae021 
Suter G., Černis E., Zhang L (2025) Interpersonal computational modelling of social synchrony in
schizophrenia and beyond. Psychoradiology 5:kkaf011 
Finn E. S., Bandettini P. A (2021) Movie-watching outperforms rest for functional connectivity-based
prediction of behavior. NeuroImage 235 
Hasson U., Chen J., Honey C. J (2015) Hierarchical process memory: memory as an integral
component of information processing. Trends Cogn. Sci 19:304‑313 
Vu T., et al. (2017) Tradeoffs in pushing the spatial resolution of fMRI for the 7T Human Connectome
Project. NeuroImage 154:23‑32 
Devlin J., Chang M.-W., Lee K., Toutanova K (2019) BERT: Pre-training of Deep Bidirectional
Transformers for Language Understanding. arXiv  http://arxiv.org/abs/1810.04805
Liu Z., et al. (2022) Video Swin Transformer. In: 2022 IEEE/CVF Conference on Computer Vision and
Pattern Recognition (CVPR). New Orleans, United States. pp. 3192‑3201 
https://doi.org/10.1109/CVPR52688.2022.00320
Chen X., et al. (2020) DNNBrain: A Unifying Toolbox for Mapping Deep Neural Networks and Brains.
Front. Comput. Neurosci 14:580632 
Peer reviews
Reviewer #1 (Public review):
Summary:
This study compares four models-VALOR (dynamic visual-text alignment), CLIP (static visual-
text alignment), AlexNet (vision-only), and WordNet (text-only)-in their ability to predict
human brain responses using voxel-wise encoding modeling. The results show that VALOR
not only achieves the highest accuracy in predicting neural responses but also generalizes
more effectively to novel datasets. In addition, VALOR captures meaningful semantic
dimensions across the cortical surface and demonstrates impressive predictive power for
brain responses elicited by future events.
Strengths:
The study leverages a multimodal machine learning model to investigate how the human
brain aligns visual and textual information. Overall, the manuscript is logically organized,
clearly written, and easy to follow. The results well support the main conclusions of the
paper.
Comments on revisions:
I am happy with the response letter. I have no further comments on this manuscript.
https://doi.org/10.7554/eLife.107607.2.sa3
Reviewer #2 (Public review):
Summary:
Fu and colleagues have shown that VALOR, a model of multimodal and dynamic stimulus
features, better predicts brain responses compared to unimodal or static models such as
AlexNet, WordNet, or CLIP. The authors demonstrated robustness of their findings from
generalizing encoding results to an external dataset. They demonstrated the models' practical
benefit by showing that semantic mappings were comparable to another model that required
46.
47.
48.
49.
50.
51.
52.
53.
Neuroscience


## Page 23

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
23 of 43
labor-intensive manual annotation. Finally, the authors showed that the model reveals
predictive coding mechanisms of the brain, which held meaningful relationship with
individuals' fluid intelligence measure.
Strengths:
Recent advances in neural network models that extract visual, linguistic, and semantic
features from real-world stimuli have enabled neuroscientists to build encoding models that
predict brain responses from these features. Higher prediction accuracy indicates greater
explained variance in neural activity, and therefore a better model of brain function.
Commonly used models include AlexNet for visual features, WordNet for audio-semantic
features, and CLIP for visuo-semantic features; these served as comparison models in the
study. Building on this line of work, the authors developed an encoding model using VALOR,
which captures the multimodal and dynamic nature of real-world stimuli. VALOR
outperformed the comparison models in predicting brain responses. It also recapitulated
known semantic mappings and revealed evidence of predictive processing in the brain. These
findings support VALOR as a strong candidate model of brain function.
Weaknesses:
The authors argue that this modeling contributes to better understanding how the brain
works. However, upon reading, I am less convinced how VALOR's superior performance than
other models tell us more about the brain. VALOR is a better model of the audiovisual
stimulus because it processes multimodal and dynamic stimuli compared to other unimodal
or static models. If the model better captures real-world stimuli, then I almost feel that it has
to better capture brain responses, assuming that the brain is a system that is optimized to
process multimodal and dynamic inputs from the real world. The authors could strengthen
the manuscript if the significance of their encoding model findings is better explained.
In Study 3, the authors show high alignment between WordNet and VALOR feature PCs. Upon
reading the method together with Figure 3, I suspect that the alignment almost has to be high,
given that the authors projected VALOR features to the Huth et al.'s PC space. Could the
authors conduct non-parametric permutation tests, such as shuffling the VALOR features
prior to mapping onto Huth et al.'s PC space, and then calculating the Jaccard scores? I
imagine that the null distribution would be positively shifted. Still, I would be convinced if
the alignment is higher than this shifted null distribution for each PC. If my understanding
about this is incorrect, I suggest editing the relevant Method section (line 508) because this
analysis was not easy to understand.
In Study 4, the authors show that individuals whose superior parietal gyrus (SPG) exhibited
high prediction distance had high fluid cognitive scores (Figure 4C). I had a hard time
believing that this was a hypothesis-driven analysis. The authors motivate the analysis that
"SPG and PCu have been strongly linked to fluid intelligence (line 304)". Did the authors
conduct two analyses only-SPG-fluid intelligence and PCu-fluid intelligence-without relating
other brain regions with other individual differences measures? Even if so, the authors
should have reported the same r value and p value for PCu-fluid intelligence. If SPG-fluid
intelligence indeed hold specificity in terms of statistical significance compared to all possible
scenarios that were tested, is this rationally an expected result and could the authors explain
the specificity? Also, the authors should explain why they considered fluid intelligence to be
the proxy of one's ability to anticipate upcoming scenes during movie watching. I would have
understood the rationale better if the authors have at least aggregated predictive scores for
all brain regions that held significance into one summary statistics and have found
significant correlation with the fluid intelligence measure.
Comments on revisions:
The revision has addressed these concerns.
Neuroscience


## Page 24

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
24 of 43
https://doi.org/10.7554/eLife.107607.2.sa2
Reviewer #3 (Public review):
Summary:
In this work, the authors aim to improve neural encoding models for naturalistic video
stimuli by integrating temporally aligned multimodal features derived from a deep learning
model (VALOR) to predict fMRI responses during movie viewing.
Strengths:
The major strength of the study lies in its systematic comparison across unimodal and
multimodal models using large-scale, high-resolution fMRI datasets. The VALOR model
demonstrates improved predictive accuracy and cross-dataset generalization. The model also
reveals inherent semantic dimensions of cortical organization and can be used to evaluate
the integration timescale of predictive coding.
This study demonstrates the utility of modern multimodal pretrained models for improving
brain encoding in naturalistic contexts. While not conceptually novel, the application is
technically sound, and the data and modeling pipeline may serve as a valuable benchmark
for future studies.
Weaknesses:
The overall framework of using data-driven features derived from pretrained AI models to
predict neural response has been well studied and accepted by the field of neuroAI for over a
decade. The demonstrated improvements in prediction accuracy, generalization, and
semantic mapping are largely attributable to the richer temporal and multimodal
representations provided by the VALOR model, not a novel neural modeling framework per
se. As such, the work may be viewed as an incremental application of recent advances in
multimodal AI to a well-established neural encoding pipeline, rather than a conceptual
advance in modeling neural mechanisms.
Within this setup, the finding that VALOR outperforms CLIP, AlexNet, and WordNet is
somewhat expected. VALOR encodes rich spatiotemporal information from videos, making it
more aligned with movie-based neural responses. CLIP and AlexNet are static image-based
models and thus lack temporal context, while WordNet only provides coarse categorical
labels with no stimulus-specific detail. Therefore, the results primarily reflect the advantage
of temporally-aware features in capturing shared neural dynamics, rather than revealing
surprising model generalization. A direct comparison to pure video-based models, such as
Video Swin Transformers or other more recent video models, would help strengthen the
argument.
Moreover, while WordNet-based encoding models perform reasonably well within-subject in
the HCP dataset, their generalization to group-level responses in the Short Fun Movies (SFM)
dataset is markedly poorer. This could indicate that these models capture a considerable
amount of subject-specific variance, which fails to translate to consistent group-level activity.
This observation highlights the importance of distinguishing between encoding models that
capture stimulus-driven representations and those that overfit to individual heterogeneities.
https://doi.org/10.7554/eLife.107607.2.sa1
Author response:
The following is the authors’ response to the original reviews.
Neuroscience


## Page 25

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
25 of 43
Public Reviews:
Reviewer #1 (Public review):
This study compares four models - VALOR (dynamic visual-text alignment), CLIP (static
visual-text alignment), AlexNet (vision-only), and WordNet (text-only) - in their ability to
predict human brain responses using voxel-wise encoding modeling. The results show
that VALOR not only achieves the highest accuracy in predicting neural responses but
also generalizes more effectively to novel datasets. In addition, VALOR captures
meaningful semantic dimensions across the cortical surface and demonstrates
impressive predictive power for brain responses elicited by future events.
Strengths:
The study leverages a multimodal machine learning model to investigate how the human
brain aligns visual and textual information. Overall, the manuscript is logically
organized, clearly written, and easy to follow. The results well support the main
conclusions of the paper.
(1) My primary concern is that the performance difference between VALOR and CLIP is
not sufficiently explained. Both models are trained using contrastive learning on visual
and textual inputs, yet CLIP performs significantly worse. The authors suggest that this
may be due to VALOR being trained on dynamic movie data while CLIP is trained on
static images. However, this explanation remains speculative. More in-depth discussion is
needed on the architectural and inductive biases of the two models, and how these may
contribute to their differences in modeling brain responses.
Thank you for this thoughtful comment. We agree that attributing VALOR’s advantage over
CLIP solely to ‘dynamic (video) versus static (image) pretraining’ would be incomplete, and
that the architectural and inductive biases of the two models are central to understanding the
observed performance gap.
Both VALOR and CLIP use contrastive learning to align visual and textual representations, but
they differ in several key inductive biases that are particularly relevant for modeling brain
responses during continuous movie viewing. First, VALOR is trained to align temporally
extended video segments with text, introducing an explicit temporal integration window that
aggregates information across consecutive frames. This encourages representations that
maintain context, stabilize semantics across time, and encode event-level structure. Second,
VALOR’s alignment operates at the level of multi-second narrative units, rather than isolated
visual snapshots, biasing the model toward representations that are sensitive to unfolding
events and cross-frame consistency.
In contrast, CLIP processes frames independently and aligns single static images with text. As
a result, it lacks an intrinsic mechanism for temporal binding, context accumulation, or
event-level representation. While CLIP can capture rich visual–semantic associations at the
image level, it is less well suited to represent higher-order temporal structure, which is
known to strongly drive responses in association cortex during naturalistic narrative
perception.
We therefore interpret VALOR’s superior encoding performance as reflecting not only
exposure to dynamic audiovisual data, but also inductive biases—temporal integration and
event-level alignment—that more closely match how the brain integrates information over
time during movie watching. We have revised the Discussion (p. 16) to articulate these
architectural and representational differences explicitly, rather than attributing the effect
solely to training data modality.
Neuroscience


## Page 26

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
26 of 43
(On page 16) “Additionally, VALOR exceeds the performance of CLIP, a leading static
multimodal model, as its training objective aligns multi-second video–text units, enforcing a
temporal integration window and event-level semantics that maintain cross-frame
consistency and narrative context, whereas CLIP’s image-level alignment provides no
intrinsic mechanism for such temporal continuity.”
(2) The methods section lacks clarity regarding which layers of VALOR and CLIP were
used to extract features for voxel-wise encoding modeling. A more detailed
methodological description is necessary to ensure reproducibility and interpretability.
Furthermore, discussion of the inductive biases inherent in these models-and their
implications for brain alignment - is crucial.
Thank you for this comment. We agree that reproducibility and interpretability require
precise specification of which model representations were used for voxel-wise encoding, as
well as clearer discussion of the inductive biases inherent in these models and their
implications for brain alignment.
In the revised Methods, we now explicitly specify the feature sources for both models. For
CLIP (ViT-B/32), we use the final pooled image embedding after projection into the shared
image–text space, extracted frame-by-frame; one representative frame is sampled per TR, and
its projected embedding serves as the regressor. For VALOR, we use the final joint video–text
projection head, yielding a 512-dimensional embedding computed at the segment/TR level
that integrates information across consecutive frames and aligns each multi-second video
segment with its associated text. These procedures are now described step-by-step in the
Methods (p. 21).
In addition, we expanded the Discussion (p. 16) to explicitly articulate the models’ inductive
biases and their relevance for brain alignment. In particular, we contrast CLIP’s image-level,
framewise alignment—which lacks intrinsic temporal integration—with VALOR’s event-level,
temporally extended video–text alignment, which biases representations toward context
maintenance and narrative continuity. This distinction helps explain why the two models
differ in their ability to predict neural responses during continuous movie viewing.
(Methods, On page 21)
“(1) Video–text alignment features (VALOR): To extract video-based multimodal features, we
used VALOR (VALOR-large checkpoint), an open-source pretrained video–text alignment
model24. VALOR combines visual encoders (CLIP and Video Swin Transformer) for extracting
visual features and a text encoder (BERT) for extracting textual features 23,51,52. These
representations are aligned in a shared embedding space through contrastive learning. We
segmented each movie at the TR level and, for each segment, extracted VALOR’s projected
video–text embedding from the final projection head of the alignment module to obtain a
512-dimensional feature vector. These embeddings were then time-aligned to the
corresponding BOLD responses.
(2) CLIP features: To compare with static image-based multimodal models, we utilized CLIP
(ViT-B/32), which aligns visual and textual representations through contrastive learning but
processes individual frames independently without capturing temporal context. One video
frame was sampled per TR, and the pooled image embedding after CLIP’s projection into the
shared image–text space was extracted to obtain a 512-dimensional feature vector. These TR-
aligned vectors were used directly as regressors in the voxel-wise encoding models.”
(Discussion, On page 16)
“Additionally, VALOR exceeds the performance of CLIP, a leading static multimodal model, as
its training objective aligns multi-second video–text units, enforcing a temporal integration
Neuroscience


## Page 27

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
27 of 43
window and event-level semantics that maintain cross-frame consistency and narrative
context, whereas CLIP’s image-level alignment provides no intrinsic mechanism for such
temporal continuity. More broadly, this difference reflects distinct inductive biases in how the
two models represent visual–linguistic information. CLIP is optimized for framewise image–
text correspondence, encouraging representations that emphasize instantaneous visual
semantics but remain agnostic to temporal structure. In contrast, VALOR is explicitly biased
toward aggregating information over multiple consecutive frames and aligning
representations at the level of temporally extended events. These inductive biases favor
context maintenance, semantic stabilization, and narrative coherence over time, which are
known to be critical for driving responses in association cortex during continuous movie
perception.”
(3) A broader question remains insufficiently addressed: what is the purpose of visual-
text alignment in the human brain? One hypothesis is that it supports the formation of
abstract semantic representations that rely on no specific input modality. While VALOR
performs well in voxel-wise encoding, it is unclear whether this necessarily indicates the
emergence of such abstract semantics. The authors are encouraged to discuss how the
computational architecture of VALOR may reflect this alignment mechanism and what
implications it has for understanding brain function.
Thank you for this important conceptual question. We agree that improved voxel-wise
encoding performance does not, by itself, imply the emergence of fully amodal or modality-
independent semantic representations in the brain. In the revision, we therefore avoid
framing our findings as evidence for abstract amodal semantics and instead clarify a more
constrained interpretation.
Specifically, we suggest that visual–text alignment may support the stabilization and
coordination of scene-level meaning across modalities and over time, rather than the
formation of modality-free semantic codes. From this perspective, VALOR’s advantage reflects
inductive biases that promote (i) integration of visual information over multi-second
windows and (ii) alignment of temporally extended visual events with linguistic descriptions,
yielding representations that are more temporally stable, context-sensitive, and constrained
by language.
We therefore interpret VALOR’s superior encoding performance as identifying cortical
regions whose responses are better captured by temporally stabilized, cross-modal
representations, rather than as evidence that these regions encode fully abstract semantics
independent of input modality. We have expanded the Discussion (p. 16) to articulate this
interpretation and to clarify the implications of video–text alignment for understanding how
the brain integrates perception and language during naturalistic cognition.
(On page 16) “Together, the relative gains over AlexNet (purely visual), WordNet (manual
semantic annotation), and CLIP (static image–text alignment) indicate cortical systems whose
responses are best captured by multi-second, multimodal integration, and highlight regions
that accumulate and stabilize narrative context over time. At the same time, these findings do
not imply that visual–text alignment in the brain gives rise to fully amodal, modality-
independent semantic representations. Instead, we suggest that alignment between visual
and linguistic signals may serve to stabilize and coordinate scene-level meaning across
modalities and over time. From this perspective, VALOR’s architecture—by integrating visual
information over multi-second windows and aligning temporally extended video segments
with language—provides a computational proxy for how the brain may use linguistic
constraints to organize, disambiguate, and maintain coherent representations of unfolding
events. The observed encoding gains therefore highlight regions engaged in temporally
stabilized, cross-modal integration during naturalistic perception, rather than providing
evidence for abstract semantic codes divorced from sensory input.”
Neuroscience


## Page 28

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
28 of 43
(4) The current methods section does not provide enough details about the network
architectures, parameter settings, or whether pretrained models were used. If so, please
provide links to the pretrained models to facilitate reproducible science.
We appreciate this comment and agree that our original description of model sources and
implementation details was not sufficiently explicit. These details are essential for both
reproducibility and interpretability. We have now made these specifications explicit in the
revised Methods.
In particular, we now state for each model:
VALOR. We use the publicly released pretrained VALOR-large checkpoint. For each movie
segment, we extract the joint video–text projection head output (512-D) that encodes the
aligned segment-level audiovisual semantics. We report the checkpoint source, the segment
duration (in frames/seconds), and how these segment-level embeddings are temporally
aligned to TRs for voxel-wise encoding.
CLIP (ViT-B/32). We use the standard pretrained CLIP weights. For each video frame, we
extract the final pooled image representation after projection into CLIP’s shared image–text
embedding space (512-D). We also clarify that one representative frame is sampled and
aligned to each TR, and that these projected embeddings are used as regressors in the
encoding model.
AlexNet. We use the ImageNet-pretrained AlexNet. We take activations from conv5, and then
apply PCA to reduce them to 512 dimensions before mapping them to the fMRI time series.
For each model, the revised Methods now specify: the pretrained source/checkpoint, the layer
or head from which features were taken, output dimensionality, any preprocessing or
dimensionality reduction, and the temporal alignment procedure used to generate TR-level
regressors. These revisions appear in the updated Methods (page 21).
(On page 21) “(1) Video–text alignment features (VALOR): To extract video-based multimodal
features, we used VALOR (VALOR-large checkpoint), an open-source pretrained video–text
alignment model24. VALOR combines visual encoders (CLIP and Video Swin Transformer) for
extracting visual features and a text encoder (BERT) for extracting textual features 23,51,52.
These representations are aligned in a shared embedding space through contrastive learning.
We segmented each movie at the TR level and, for each segment, extracted VALOR’s projected
video–text embedding from the final projection head of the alignment module to obtain a
512-dimensional feature vector. These embeddings were then time-aligned to the
corresponding BOLD responses.
(2) P features: To compare with static image-based multimodal models, we utilized CLIP (ViT-
B/32), which aligns visual and textual representations through contrastive learning but
processes individual frames independently without capturing temporal context. One video
frame was sampled per TR, and the pooled image embedding after CLIP’s projection into the
shared image–text space was extracted to obtain a 512-dimensional feature vector. These TR-
aligned vectors were used directly as regressors in the voxel-wise encoding models.
(3) AlexNet features: Visual features were extracted by sampling frames at the TR level and
processing them with AlexNet, an eight-layer convolutional neural network comprising five
convolutional layers followed by three fully connected layers. Features from all five
convolutional layers were evaluated in preliminary analyses; the fifth convolutional layer
showed the best performance and was used in subsequent analyses. Intra-image z-score
normalization was applied to reduce amplitude effects. Principal component analysis (PCA)
was used to reduce dimensionality, retaining the top 512 components to match the
Neuroscience


## Page 29

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
29 of 43
dimensionality of multimodal feature spaces. This pipeline was implemented using the
DNNBrain toolkit 53.
(4) WordNet features: Semantic features were obtained from publicly available WordNet
annotations provided with the HCP dataset (7T_movie_resources/WordNetFeatures.hdf5),
following the procedure of Huth et al. (2012). Each second of the movie clips was manually
annotated with WordNet categories according to predefined guidelines: (a) identifying clear
objects and actions in the scene; (b) labeling categories that dominated for more than half of
the segment duration; and (c) using specific category labels rather than general ones. A
semantic feature matrix was constructed with rows corresponding to time points and
columns to semantic categories, with category presence coded as binary values. More specific
categories from the WordNet hierarchy were added to each labeled category, yielding a total
of 859 semantic features. These features were used directly as regressors. We also evaluated a
PCA-reduced 512-dimensional variant (fit within each training fold to avoid leakage); because
this version performed slightly worse, we report results from the full 859-dimensional
representation in the main text. For the generalization analysis in Study 2, annotations for
the SFM dataset were aligned to the same WordNet category space to ensure consistency.”
Reviewer #2 (Public review):
Fu and colleagues have shown that VALOR, a model of multimodal and dynamic stimulus
features, better predicts brain responses compared to unimodal or static models such as
AlexNet, WordNet, or CLIP. The authors demonstrated the robustness of their findings by
generalizing encoding results to an external dataset. They demonstrated the models'
practical benefit by showing that semantic mappings were comparable to another model
that required labor-intensive manual annotation. Finally, the authors showed that the
model reveals predictive coding mechanisms of the brain, which held a meaningful
relationship with individuals' fluid intelligence measures.
Strengths:
Recent advances in neural network models that extract visual, linguistic, and semantic
features from real-world stimuli have enabled neuroscientists to build encoding models
that predict brain responses from these features. Higher prediction accuracy indicates
greater explained variance in neural activity, and therefore a better model of brain
function. Commonly used models include AlexNet for visual features, WordNet for audio-
semantic features, and CLIP for visuo-semantic features; these served as comparison
models in the study. Building on this line of work, the authors developed an encoding
model using VALOR, which captures the multimodal and dynamic nature of real-world
stimuli. VALOR outperformed the comparison models in predicting brain responses. It
also recapitulated known semantic mappings and revealed evidence of predictive
processing in the brain. These findings support VALOR as a strong candidate model of
brain function.
(1) The authors argue that this modeling contributes to a better understanding of how
the brain works. However, upon reading, I am less convinced about how VALOR's
superior performance over other models tells us more about the brain. VALOR is a better
model of the audiovisual stimulus because it processes multimodal and dynamic stimuli
compared to other unimodal or static models. If the model better captures real-world
stimuli, then I almost feel that it has to better capture brain responses, assuming that
the brain is a system that is optimized to process multimodal and dynamic inputs from
the real world. The authors could strengthen the manuscript if the significance of their
encoding model findings were better explained.
We thank the reviewer for this thoughtful comment and agree with the premise that a model
preserving multimodal and temporal structure might a priori be expected to better predict
Neuroscience


## Page 30

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
30 of 43
brain responses to naturalistic stimuli. Our intent is not to claim that higher accuracy alone
explains brain function, but rather that where and how VALOR improves prediction provides
diagnostic insight into cortical processing. We have revised the Discussion to make this
distinction explicit.
Specifically, we clarify three ways in which VALOR’s gains are scientifically informative
rather than merely unsurprising:
(1) Anatomical specificity of improvement. VALOR’s advantage is not uniform across the
cortex; gains are largest in regions implicated in multi-second, cross-modal integration. This
spatial pattern constrains where the brain accumulates information over time and stabilizes
visual representations using linguistic context.
(2) Model as a computational probe. Beyond prediction accuracy, VALOR’s feature space
recovers large-scale semantic organization without manual annotation and enables targeted
tests of predictive processing. Features reflecting upcoming content selectively improve fits in
specific regions, consistent with anticipatory coding during continuous narrative perception.
(3) Link to individual differences. Individuals whose neural responses are better captured by
anticipatory features show higher fluid intelligence, suggesting that VALOR indexes
meaningful variability in forward-looking representations rather than merely tracking
stimulus complexity.
Accordingly, we have revised the Discussion (p. 16) to frame VALOR as a tool for mapping
cortical integration profiles, probing semantic and predictive structure, and linking
representational dynamics to cognition, rather than asserting that higher encoding accuracy
alone explains brain function.
(On page 16) “Together, the relative gains over AlexNet (purely visual), WordNet (manual
semantic annotation), and CLIP (static image–text alignment) indicate cortical systems whose
responses are best captured by multi-second, multimodal integration, and highlight regions
that accumulate and stabilize narrative context over time.”
(2) In Study 3, the authors show high alignment between WordNet and VALOR feature
PCs. Upon reading the method together with Figure 3, I suspect that the alignment
almost has to be high, given that the authors projected VALOR features to the Huth et
al.'s PC space. Could the authors conduct non-parametric permutation tests, such as
shuffling the VALOR features prior to mapping onto Huth et al.'s PC space, and then
calculating the Jaccard scores? I imagine that the null distribution would be positively
shifted. Still, I would be convinced if the alignment is higher than this shifted null
distribution for each PC. If my understanding of this is incorrect, I suggest editing the
relevant Method section (line 508) because this analysis was not easy to understand.
Thank you for this helpful comment and for pointing out a potential source of confusion. We
apologize that the original Methods description was not sufficiently clear. Importantly,
VALOR features were never projected into the Huth et al. PC space, and no optimization or
rotation toward the WordNet basis occurred at any stage.
The analysis proceeded as follows:
(1) VALOR PCs. We first fit voxel-wise encoding models using VALOR features on the Huth et
al. dataset. We then applied PCA to the resulting cortical weight maps, yielding spatial
components (‘VALOR PCs’) that summarize shared patterns of VALOR feature weights across
the cortex.
(2) WordNet PCs. We used the semantic principal components reported by Huth et al. (2012)
directly as published, with no refitting, projection, or modification using VALOR.
Neuroscience


## Page 31

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
31 of 43
(3) Correspondence analysis. Only after obtaining these two independent sets of cortical maps
did we threshold each to their top-loading vertices and compute Jaccard overlap between
VALOR PCs and WordNet PCs.
Although a permutation that shuffles VALOR features prior to projection addresses a scenario
that does not apply here, we agree that the Methods description should more clearly convey
the independence of the two decompositions. We have therefore revised the Methods (p. 24)
to describe the procedure step-by-step and explicitly state that no projection, refitting, or
optimization toward the WordNet basis was performed.
(On page 24) “We first fit voxel-wise encoding models using VALOR features for each of the
five participants in the Huth et al. dataset. For each participant, this yielded a weight map
linking each VALOR feature to each voxel. We then stacked these weight maps across
participants to form a single voxel-by-feature weight matrix and applied principal
component analysis (PCA). The top four principal components from this analysis (“VALOR
PCs”) captured shared spatial patterns of VALOR feature weights across cortex. To interpret
these components, we projected VALOR feature vectors from >20,000 video segments in the
VALOR training set onto each VALOR PC, which revealed dominant semantic axes (e.g.,
mobility, sociality, civilization). For comparison, we used the semantic principal components
reported by Huth et al. (2012) from their WordNet-based encoding model; these “WordNet
PCs” were taken directly from the published work and were not refit or reweighted using
VALOR.”
(3) In Study 4, the authors show that individuals whose superior parietal gyrus (SPG)
exhibited high prediction distance had high fluid cognitive scores (Figure 4C). I had a
hard time believing that this was a hypothesis-driven analysis. The authors motivate the
analysis that "SPG and PCu have been strongly linked to fluid intelligence (line 304)". Did
the authors conduct two analyses only-SPG-fluid intelligence and PCu-fluid intelligence-
without relating other brain regions to other individual differences measures? Even if so,
the authors should have reported the same r-value and p-value for PCu-fluid intelligence.
If SPG-fluid intelligence indeed holds specificity in terms of statistical significance
compared to all possible scenarios that were tested, is this rationally an expected result,
and could the authors explain the specificity? Also, the authors should explain why they
considered fluid intelligence to be the proxy of one's ability to anticipate upcoming
scenes during movie watching. I would have understood the rationale better if the
authors had at least aggregated predictive scores for all brain regions that held
significance into one summary statistic and found a significant correlation with the fluid
intelligence measure.
We thank the reviewer for this careful and constructive comment and agree that greater
transparency about analytic intent, specificity, and rationale is needed. We have revised the
manuscript accordingly.
(1) Analytic scope and a priori restriction. The analysis in Fig. 4C was hypothesis-driven and
restricted a priori to two regions — superior parietal gyrus (SPG) and precuneus (PCu) —
based on convergent evidence linking frontoparietal and medial parietal systems to fluid
reasoning, relational integration, and domain-general cognitive control. Importantly, we did
not conduct a whole-brain search across regions or behaviors to identify the strongest
correlation post hoc.
(2) Specificity and reporting. In response to the reviewer’s request, we now report the full
results for both hypothesized regions. Prediction horizon in SPG showed a statistically
reliable association with fluid intelligence, whereas PCu showed a positive but weaker trend
that did not survive correction. Reporting both results makes the regional specificity explicit
rather than implicit.
Neuroscience


## Page 32

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
32 of 43
(3) Why SPG over PCu? Although both regions are implicated in fluid cognition, SPG has been
more consistently linked to active maintenance and manipulation of relational structure and
top-down attentional control, whereas PCu is more often associated with internally oriented
and mnemonic processes. We therefore interpret the stronger SPG association as consistent
with a role for sustained, externally driven predictive processing during continuous
perception, rather than as evidence of exclusivity.
(4) Why fluid intelligence? We do not equate fluid intelligence with “anticipation” per se.
Rather, we used gF as an a priori proxy for domain-general capacities — maintaining and
updating relational context over multi-second windows, integrating multiple constraints, and
exerting flexible control — that are plausibly recruited when anticipating upcoming events
during naturalistic narratives. The reported relationship is associative and hypothesis-
consistent, not causal.
(5) Why not aggregate across regions? We agree that aggregation could reveal more global
relationships; however, our goal in this analysis was to test whether predictive timescales in
theoretically motivated control regions relate to individual differences, rather than to
maximize correlation by pooling heterogeneous regions. We now clarify this rationale in the
Results.
These clarifications and additional statistics have been incorporated in the revised Results
section (p. 14).
(On page 14) “Finally, we examined whether prediction horizons were linked to individual
differences in cognition. We focused on fluid intelligence (gF) because gF is widely taken to
index domain-general capacities such as maintaining and updating relational context over
several seconds, integrating multiple constraints, and exerting flexible top-down control —
functions that should support anticipating what will happen next in a continuous narrative.
We targeted two parietal regions, the SPG and the PCu, which have both been repeatedly
linked to gF and high-level cognitive control in the individual-differences literature 36,37. For
each participant, we correlated fluid cognition scores with that participant’s average
prediction horizon in each region. As shown in Fig. 4c, individuals with longer prediction
horizons in SPG showed higher fluid cognition scores (SPG: r = 0.172, FDR-corrected p =
0.047). PCu showed a similar positive trend (PCu: r = 0.111, FDR-corrected p = 0.146) but did
not reach significance. These associations suggest that the ability to sustain a longer
predictive timescale during naturalistic perception co-varies with broader fluid cognitive
capacity. No additional brain regions or behavioral measures were examined in this
analysis.”
Reviewer #3 (Public review):
In this work, the authors aim to improve neural encoding models for naturalistic video
stimuli by integrating temporally aligned multimodal features derived from a deep
learning model (VALOR) to predict fMRI responses during movie viewing.
Strengths:
The major strength of the study lies in its systematic comparison across unimodal and
multimodal models using large-scale, high-resolution fMRI datasets. The VALOR model
demonstrates improved predictive accuracy and cross-dataset generalization. The model
also reveals inherent semantic dimensions of cortical organization and can be used to
evaluate the integration timescale of predictive coding.
This study demonstrates the utility of modern multimodal pretrained models for
improving brain encoding in naturalistic contexts. While not conceptually novel, the
Neuroscience


## Page 33

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
33 of 43
application is technically sound, and the data and modeling pipeline may serve as a
valuable benchmark for future studies.
(1) Lines 95-96: The authors claim that "cortical areas share a common space," citing
references [22-24]. However, these references primarily support the notion that different
modalities or representations can be aligned in a common embedding space from a
modeling perspective, rather than providing direct evidence that cortical areas
themselves are aligned in a shared neural representational space.
We thank the reviewer for this important clarification. We agree that the cited works do not
provide direct evidence that cortical areas themselves are aligned in a single neural
representational space. Rather, they demonstrate that representations derived from different
modalities can be mapped into a shared embedding space from a modeling and
computational perspective.
We have therefore revised the text to avoid overstatement and to more precisely reflect what
these studies support. In the revised manuscript (p. 4), we now frame the claim in terms of a
shared representational framework or feature space used for modeling, rather than implying
that cortical areas themselves intrinsically share a unified neural space. This clarification
aligns the conceptual claim with the scope of the cited literature.
(On page 4) “As a result, researchers are turning to multimodal deep learning, which learns
from visual, linguistic, and auditory streams to model complex brain functions. This trend is
supported by neuroscience evidence that cortical responses across regions can be jointly
modeled within a common representational space.”
(2) The authors discuss semantic annotation as if it is still a critical component of
encoding models. However, recent advances in AI-based encoding methods rely on
features derived from large-scale pretrained models (e.g., CLIP, GPT), which
automatically capture semantic structure without requiring explicit annotation. While the
manuscript does not systematically address this transition, it is important to clarify that
the use of such pretrained models is now standard in the field and should not be
positioned as an innovation of the present work. Additionally, the citation of Huth et al.
(2012, Neuron) to justify the use of WordNet-based annotation omits the important
methodological shift in Huth et al. (2016, Nature), which moved away from manual
semantic labeling altogether. Since the 2012 dataset is used primarily to enable
comparison in study 3, the emphasis should not be placed on reiterating the
disadvantages of semantic annotation, which have already been addressed in prior
work. Instead, the manuscript's strength lies in its direct comparison between data-
driven feature representations and semantic annotation based on WordNet categories.
The authors should place greater emphasis on analyzing and discussing the differences
revealed by these two approaches, rather than focusing mainly on the general
advantage of automated semantic mapping.
Thank you for this thoughtful and constructive comment. We agree with the reviewer that
the field has largely transitioned away from manual semantic annotation toward features
derived from large-scale pretrained models (e.g., CLIP, GPT-style architectures), and that this
shift is now standard rather than a novelty of the present work.
We have revised the manuscript to clarify this positioning. Our goal is not to claim automated
semantic extraction as an innovation, but rather to demonstrate how a multimodal,
temporally informed video–text model can be used as a direct feature space for voxel-wise
encoding of naturalistic movie fMRI data. VALOR is used as a representative example of this
broader class of pretrained models, and our emphasis is on the general modeling approach
rather than on promoting a specific architecture.
Neuroscience


## Page 34

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
34 of 43
We also agree that our original discussion underemphasized the important methodological
shift introduced in Huth et al. (2016, Nature), which moved away from manual semantic
labeling in the context of continuous spoken narratives. We now explicitly acknowledge this
work and clarify that our use of WordNet-based annotations from Huth et al. (2012) serves a
different purpose: it provides an interpretable, historically grounded benchmark for
comparison in Study 3, rather than a claim that semantic annotation remains necessary or
state-of-the-art.
In response to the reviewer’s suggestion, we have revised the Results (p.10) and Discussion
(p.18) to place greater emphasis on what is revealed by directly comparing data-driven
multimodal features with category-based semantic annotation under matched conditions.
Specifically, we focus on how these two approaches converge at the level of large-scale
semantic organization while differing in their flexibility, temporal resolution, and
dependence on human-defined categories. These revisions better reflect the current state of
the field and sharpen the manuscript’s central contribution as a principled comparison
between modeling approaches, rather than a general argument for automated semantic
mapping.
(On page 10) “Study 3: Comparing data-driven multimodal representations with category-
based semantic annotation
A central question in naturalistic encoding is how data-driven feature representations
derived from pretrained models relate to more interpretable, category-based semantic
annotations that have historically been used to study cortical semantic organization.
Although recent work has shown that pretrained language and vision–language models can
capture semantic structure without explicit annotation, category-based approaches such as
WordNet remain valuable as interpretable reference frameworks. Here, we leverage the
WordNet-based semantic components reported by Huth et al. (2012) 5 not as a state-of-the-art
alternative, but as a historically grounded benchmark, allowing a controlled comparison
between data-driven multimodal representations and manually defined semantic categories
under matched naturalistic movie stimuli.”
(On page 18) “Study 3 demonstrates the utility of video–text alignment models for probing
higher-order semantic representations during naturalistic perception. Our comparison
between VALOR-derived representations and WordNet-based semantic components
highlights an important distinction between data-driven and category-based approaches to
modeling meaning in the brain. While multimodal pretrained models offer flexible, high-
dimensional representations that capture semantic structure without explicit annotation,
category-based frameworks provide interpretability and theoretical anchoring 4,48. Using
WordNet-based labeling from prior work as an interpretable reference point, we show that
VALOR automatically extracts semantic dimensions—including mobility, sociality, and
civilization—that closely mirror those identified using manual semantic categories (Fig. 3).
The observed alignment between VALOR PCs and WordNet semantic components suggests
that large-scale semantic organization emerges consistently across these approaches, even
though they differ in how semantic structure is defined and learned. This convergence
supports the use of pretrained multimodal models as practical encoding tools for naturalistic
stimuli, while also underscoring the continued value of interpretable semantic benchmarks
for understanding which aspects of meaning are represented across cortex. We do not argue
that semantic annotation is required for modern encoding models; rather, WordNet-based
features serve here as a historically grounded and interpretable reference for contextualizing
data-driven multimodal representations.”
(3) The authors use subject-specific encoding models trained on the HCP dataset to
predict group-level mean responses in an independent in-house dataset. While this
analysis is framed as testing model generalization, it is important to clarify that it is not
Neuroscience


## Page 35

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
35 of 43
assessing traditional out-of-distribution (OOD) generalization, where the same subject is
tested on novel stimuli, but rather evaluating which encoding model's feature space
contains more stimulus-specific and cross-subject-consistent information that can
transfer across datasets.
We thank the reviewer for this helpful clarification and agree that the type of generalization
tested here should be described more precisely. Our analysis does not assess classical within-
subject out-of-distribution (OOD) generalization, in which the same individual is tested on
novel stimuli.
Instead, for each HCP participant we train a subject-specific encoding model and transfer it to
predict group-mean responses in an independent in-house dataset collected at a different site,
with different participants, different movies, and different acquisition conditions. This design
evaluates which encoding model’s feature space contains stimulus-locked representations
that are consistent across individuals and robust to changes in dataset and experimental
context, rather than within-subject stimulus novelty per se.
We have revised the Results (p. 10) and Discussion section (p. 17) to explicitly describe this
analysis as a test of cross-subject and cross-dataset transferability of stimulus
representations, and to clarify the distinction from traditional OOD generalization.
(On Page 10) “Although this analysis is not a classical within-subject out-of-distribution
generalization test, it evaluates the extent to which different feature spaces capture stimulus-
locked representations that are consistent across subjects and transferable across datasets,
stimuli, and acquisition environments.”
(On Page 17) “By contrast, VALOR exhibited stronger generalization in a cross-cohort, cross-
stimulus, and cross-site transfer evaluation.”
(4) Within this setup, the finding that VALOR outperforms CLIP, AlexNet, and WordNet is
somewhat expected. VALOR encodes rich spatiotemporal information from videos,
making it more aligned with movie-based neural responses. CLIP and AlexNet are static
image-based models and thus lack temporal context, while WordNet only provides
coarse categorical labels with no stimulus-specific detail. Therefore, the results primarily
reflect the advantage of temporally-aware features in capturing shared neural dynamics,
rather than revealing surprising model generalization. A direct comparison to pure
video-based models, such as Video Swin Transformers or other more recent video
models, would help strengthen the argument.
We thank the reviewer for this baseline-focused comment and agree that, in naturalistic
movie paradigms, a temporally structured audiovisual model would be expected to
outperform static or unimodal feature spaces. Our intent in this comparison is therefore not
to claim a surprising advantage, but to isolate which inductive biases matter for cross-dataset
transfer of movie-evoked neural responses.
The baseline models were chosen deliberately to span feature spaces that are widely used
and interpretable in cognitive neuroscience: AlexNet (vision-only, frame-based), WordNet
(human-defined semantic categories without learned visual features), and CLIP (static image–
text alignment without temporal context). Comparing VALOR against these established
baselines under matched preprocessing, TR alignment, and dimensionality control allows us
to attribute performance differences specifically to temporal integration and audiovisual
alignment, rather than to generic model capacity.
We agree that a direct comparison with purely visual spatiotemporal encoders (e.g., Video
Swin or TimeSformer-style models) would further dissociate the contribution of temporal
visual processing from cross-modal video–text alignment. We now explicitly note this as an
important direction for future work and frame VALOR as one representative of a broader
Neuroscience


## Page 36

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
36 of 43
class of multimodal video models, rather than as a uniquely optimal solution (Discussion, p.
16).
(On page 16) “Second, we did not directly compare VALOR to state-of-the-art video-only
spatiotemporal models (e.g., Video Swin Transformer, VideoMAE, and related architectures)
that are designed to capture temporal visual structure without language grounding; such
comparisons will be important for isolating the specific contributions of temporal visual
processing versus cross-modal video–text alignment in naturalistic neural responses.”
(5) Moreover, while WordNet-based encoding models perform reasonably well within-
subject in the HCP dataset, their generalization to group-level responses in the Short Fun
Movies (SFM) dataset is markedly poorer. This could indicate that these models capture a
considerable amount of subject-specific variance, which fails to translate to consistent
group-level activity. This observation highlights the importance of distinguishing between
encoding models that capture stimulus-driven representations and those that overfit to
individual heterogeneities.
Thank you for this thoughtful observation. We agree with the reviewer’s interpretation. In
our analyses, WordNet-based models perform reasonably well when fit and evaluated within
individual HCP participants, but their performance degrades substantially when transferred
to predict group-averaged responses in the independent SFM dataset. This dissociation
suggests that, while WordNet annotations capture meaningful variance at the individual
level, a larger fraction of that variance may be subject-specific or idiosyncratic, and therefore
does not translate into consistent, stimulus-locked responses at the group level.
One motivation for our cross-dataset, cross-subject evaluation is precisely to distinguish
encoding models that primarily capture shared stimulus-driven structure from those whose
apparent performance depends more strongly on individual heterogeneity. In this context,
the reduced transferability of WordNet-based models highlights a potential limitation of
category-based semantic features for capturing population-consistent neural dynamics
during naturalistic viewing.
We note that this effect likely reflects multiple factors rather than a single failure mode,
including differences in annotation schemes, labeling granularity, and semantic coverage
across datasets. By contrast, video–text models provide time-aligned linguistic features
directly from the stimulus itself, reducing reliance on dataset-specific human annotation and
exhibiting stronger transfer across cohorts. We have clarified this interpretation in the
revised Discussion (p. 17).
(Page 17) “Together, these findings underscore the importance of distinguishing encoding
models that primarily capture shared, stimulus-driven neural structure from those whose
performance relies more heavily on subject-specific heterogeneity, particularly when
evaluating generalization across participants and datasets.”
Recommendations for the authors:
Reviewer #1 (Recommendations for the authors):
(1) In the Methods section, please clarify which specific layer of VALOR the 512-
dimensional feature vector was extracted from.
Thank you for this suggestion. We have revised the Methods to state explicitly that the 512-
dimensional feature vector is extracted from VALOR’s joint video–text projection head, i.e.,
the final projection layer of the contrastive alignment module that maps video and text
representations into a shared embedding space. We also clarify that these 512-D embeddings
are computed at the segment/TR level and then time-aligned to the BOLD signal (Methods, p.
21).
Neuroscience


## Page 37

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
37 of 43
(On page 21) “We segmented each movie at the TR level and, for each segment, extracted
VALOR’s projected video–text embedding from the final projection head of the alignment
module to obtain a 512-dimensional feature vector. These embeddings were then time-
aligned to the corresponding BOLD responses.”
(2) It would be helpful to include more detailed descriptions of the network architectures
and parameters for all models used.
Thank you for the suggestion. We have revised the Methods to include model-specific
subsections for all feature spaces used (VALOR, CLIP, AlexNet, and WordNet). For each model,
we now explicitly report (i) the backbone architecture and training objective, (ii) the exact
feature source (layer or projection head) and output dimensionality, and (iii) how features
were temporally aligned to the BOLD signal. All models were used with their publicly
released pretrained parameters, without additional fine-tuning. These additions are intended
to improve transparency and reproducibility (Methods, p. 21).
(On page 21) “Movie Feature Extraction
(1) Video–text alignment features (VALOR): To extract video-based multimodal features, we
used VALOR (VALOR-large checkpoint), an open-source pretrained video–text alignment
model24. VALOR combines visual encoders (CLIP and Video Swin Transformer) for extracting
visual features and a text encoder (BERT) for extracting textual features 23,51,52. These
representations are aligned in a shared embedding space through contrastive learning. We
segmented each movie at the TR level and, for each segment, extracted VALOR’s projected
video–text embedding from the final projection head of the alignment module to obtain a
512-dimensional feature vector. These embeddings were then time-aligned to the
corresponding BOLD responses.
(2) CLIP features: To compare with static image-based multimodal models, we utilized CLIP
(ViT-B/32), which aligns visual and textual representations through contrastive learning but
processes individual frames independently without capturing temporal context. One video
frame was sampled per TR, and the pooled image embedding after CLIP’s projection into the
shared image–text space was extracted to obtain a 512-dimensional feature vector. These TR-
aligned vectors were used directly as regressors in the voxel-wise encoding models.
(3) AlexNet features: Visual features were extracted by sampling frames at the TR level and
processing them with AlexNet, an eight-layer convolutional neural network comprising five
convolutional layers followed by three fully connected layers. Features from all five
convolutional layers were evaluated in preliminary analyses; the fifth convolutional layer
showed the best performance and was used in subsequent analyses. Intra-image z-score
normalization was applied to reduce amplitude effects. Principal component analysis (PCA)
was used to reduce dimensionality, retaining the top 512 components to match the
dimensionality of multimodal feature spaces. This pipeline was implemented using the
DNNBrain toolkit 53.
(4) WordNet features: Semantic features were obtained from publicly available WordNet
annotations provided with the HCP dataset (7T_movie_resources/WordNetFeatures.hdf5),
following the procedure of Huth et al. (2012). Throughout this manuscript, we use the term
“semantic features” to refer to such human-annotated, category-based representations of
scene content, and we reserve the term “linguistic features” for continuous language
embeddings derived automatically from pretrained language or vision–language models.
Each second of the movie clips was manually annotated with WordNet categories according
to predefined guidelines: (a) identifying clear objects and actions in the scene; (b) labeling
categories that dominated for more than half of the segment duration; and (c) using specific
category labels rather than general ones. A semantic feature matrix was constructed with
Neuroscience


## Page 38

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
38 of 43
rows corresponding to time points and columns to semantic categories, with category
presence coded as binary values. More specific categories from the WordNet hierarchy were
added to each labeled category, yielding a total of 859 semantic features. These features were
used directly as regressors. We also evaluated a PCA-reduced 512-dimensional variant (fit
within each training fold to avoid leakage); because this version performed slightly worse, we
report results from the full 859-dimensional representation in the main text. For the
generalization analysis in Study 2, annotations for the SFM dataset were aligned to the same
WordNet category space to ensure consistency.”
(3) In Figure 3, consider following Huth et al.'s approach by using 3-4 distinct colors to
visualize semantic representations across the cortical surface more clearly.
Thank you for this excellent suggestion. We have generated an alternative visualization using
a discrete 3–4 color scheme following Huth et al. to display the semantic components on the
cortical surface. This version makes the spatial correspondence between components and the
boundaries between cortical territories easier to see. We now include this visualization in the
Supplement (Fig. S3)
(4) In Figure 2, the brain renderings are too small. Please consider creating a separate,
enlarged figure with clearer delineation of relevant ROIs.
We appreciate this suggestion and agree that clear delineation of ROIs is important. We
evaluated larger brain renderings; however, within the multi-panel layout of Fig. 2, enlarging
them compressed accompanying plots/legends and introduced visual crowding, which
reduced overall readability. To preserve a balanced layout and consistent typography across
panels, we have kept the current rendering size in the main text and added Fig. S4 with
enlarged brain renderings showing clearer ROI boundaries for the same ROIs.
Reviewer #2 (Recommendations for the authors):
(1) From the introduction, I feel like naïve readers would have a hard time understanding
what semantic models (e.g., WordNet) are, which the authors write are based on "labor-
intensive and subjective manual annotation of semantic content". It would be
straightforward to explain the process-how scientists have written descriptions or
denoted categories of what's happening within a TR and transformed these into
embedding vectors based on language models. This description would explain what the
authors mean by "labor-intensive, time-consuming, and subjective". Related to this point,
the authors seem to be using the words "semantic model/feature" and "linguistic
model/feature" interchangeably, which may exacerbate the confusion.
Thank you for this helpful suggestion. We agree that naïve readers would benefit from a
clearer explanation of how “semantic” models such as WordNet are constructed and from a
more precise distinction between semantic and linguistic features.
In response, we expanded the Introduction (p. 3) to explicitly describe the process by which
semantic features are generated via dense human annotation (i.e., raters label objects,
actions, and events within each TR and map these labels onto a predefined ontology to form
feature vectors), clarifying why this approach is labor-intensive, time-consuming, and subject
to rater variability.
To avoid disrupting the conceptual flow of the Introduction, we placed the explicit
terminology clarification in the Methods section (p. 22), where feature extraction is described.
There, we now define semantic features as human-annotated, category-based representations
of scene content, and linguistic features as continuous language embeddings derived
automatically from pretrained language or vision–language models. These revisions are
intended to improve clarity and consistency for both expert and non-expert readers.
Neuroscience


## Page 39

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
39 of 43
(On page 3) “Critically, semantic models often rely on dense human annotation. In early
naturalistic encoding studies, trained raters watched the stimulus and labeled what was
happening within each TR or short time window—for example, identifying objects, actions, or
events present in the scene. These labels were then mapped onto a predefined semantic
ontology (such as WordNet), yielding high-dimensional categorical feature vectors that served
as regressors in encoding models. While this approach provides interpretable semantic
features, it is labor-intensive, time-consuming, and inherently subjective, as annotations
depend on rater judgment, labeling guidelines, and dataset-specific conventions, limiting
scalability and reproducibility.”
(On page 22) “Throughout this manuscript, we use the term “semantic features” to refer to
such human-annotated, category-based representations of scene content, and we reserve the
term “linguistic features” for continuous language embeddings derived automatically from
pretrained language or vision–language models.”
(2) Figure 1A does not look like an accurate schematic of the encoding method. For
example, shouldn't the "Train" give rise to weight matrices, and Movies come from
moments at Test? I would appreciate it if this schematic figure would explain what the
encoding model is to naïve readers.
(3) Figure 1B emphasizes that VALOR is utilizing multimodal features, but does not
emphasize that the model is trained on dynamic video. The current figure looks like the
model extracted visual and linguistic features from a screenshot of the video, much like
the CLIP model.
Thank you for this helpful comment. We agree that the original Fig. 1A did not sufficiently
clarify what is learned during training versus what is applied during testing, and that this
distinction is particularly important for naïve readers unfamiliar with encoding models. We
also agree that the original Fig. 1B did not sufficiently emphasize that VALOR is trained on
dynamic video segments, and that the schematic could be misinterpreted as aligning a single
video frame with text, similar to CLIP-style image–text models.
We have revised Fig. 1A (p. 6) to make the encoding procedure explicit and pedagogical.
Specifically, we now clearly depict that, during the training phase (HCP dataset), voxel-wise
encoding models learn feature-to-voxel weight matrices from stimulus features and BOLD
responses. These learned weights are explicitly labeled as voxel-wise weight matrices and
visually associated with the training stage. In the testing/generalization phase (SFM dataset),
we now indicate that these learned weights are held fixed and applied to features extracted
from novel movies to generate predicted BOLD responses. Additional labels were added to
distinguish “Training (learn weights)” from “Testing/Transfer (apply fixed weights)” and to
clarify that the encoding model implements a linear mapping from stimulus features to voxel
responses. We have also rewritten the Fig. 1 legend (p. 6) to explicitly explain the encoding
workflow in words, including (i) the learning of voxel-specific weights during training, (ii)
their reuse during cross-dataset transfer, and (iii) how generalization performance is
evaluated. These changes are intended to ensure that Fig. 1A accurately reflects the encoding
methodology and is understandable to readers without prior experience with encoding
models.
We have revised Fig. 1B (p. 6) to explicitly highlight the temporal nature of the video input
used by VALOR. In the updated schematic, the visual stream is depicted as a sequence of
consecutive frames spanning multiple seconds, grouped into a video segment, rather than as
a single static image. Additional labels indicate that VALOR encodes temporally extended
video clips and aligns them with corresponding textual descriptions in a shared embedding
space via contrastive learning. We have also updated the figure legend (p. 6) to clarify that
VALOR operates on multi-frame video segments and explicitly models temporal structure,
Neuroscience


## Page 40

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
40 of 43
distinguishing it from static image–text models such as CLIP. These changes are intended to
make clear that VALOR’s advantage derives not only from multimodality, but also from
learning representations over time.
(4) Regarding Figure 2, why were paired t-tests conducted in one-sided comparisons?
Shouldn't this be two-sided, given that there is no reason to assume one is higher or
lower than another?
Thank you for raising this point. We agree that, in the absence of a preregistered directional
hypothesis, paired comparisons should be evaluated using two-sided statistical tests.
In response, we have re-run all paired comparisons reported in Figure 2 (p. 9) using two-
sided paired t-tests, recomputed the corresponding p-values and false discovery rate (FDR)
corrections, and updated the significance markers in the figure and captions accordingly.
Importantly, this change does not alter the qualitative pattern of results or the main
conclusions reported in the manuscript.
(5) Regarding Study 4, I am curious whether the results are specific to forward-looking
representations (predictive coding) or whether the results broadly reveal regions that are
sensitive to contexts. For example, if the authors were to incorporate nearby past scenes
in the analysis rather than the nearby future scenes, would different brain regions light
up?
Thank you for this thoughtful question. We agree that it is important to distinguish forward-
looking (predictive) representations from more general sensitivity to temporal context. In
Study 4, we deliberately operationalized prediction using future-aligned features, such that
only information from upcoming scenes was incorporated into the encoding model.
Accordingly, the reported effects should be interpreted as reflecting forward-oriented
representations rather than generic context sensitivity.
To make this interpretive scope explicit, we have added a clarifying sentence at the beginning
of the Study 4 paragraph in the Discussion (p.18), noting that our analysis incorporates only
future-aligned features and that directly contrasting past- and future-aligned features will be
an important direction for future work. This clarification is intended to clearly bound our
claims while addressing the reviewer’s conceptual distinction..
(On page 18) “In Study 4, we used a video-text alignment model to investigate predictive
coding mechanisms. Because our analysis incorporates only future-aligned features, the
reported effects should be interpreted as reflecting forward-oriented representations rather
than generic sensitivity to temporal context; directly contrasting past- and future-aligned
features will be an important direction for future work.”
(6) In the paragraph starting in line 447, were WordNet feature time series also reduced
to 512 dimensions like the rest of the model features?
Thank you for the question. In the main analyses, WordNet feature time series were not
reduced to 512 dimensions and were instead used at their full dimensionality (859 features).
For comparability with the other feature spaces, we additionally conducted a control analysis
in which WordNet features were reduced to 512 dimensions using PCA. The PCA was fit
within each training fold to avoid information leakage, and the resulting 512-D features were
evaluated using the same encoding pipeline. This PCA-reduced version performed slightly
worse than the full 859-D WordNet representation. Accordingly, we report results from the
full 859-D WordNet features in the main text. We have clarified this point in the Methods
section (p. 22).
Neuroscience


## Page 41

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
41 of 43
(On page 22) “We also evaluated a PCA-reduced 512-dimensional variant (fit within each
training fold to avoid leakage); because this version performed slightly worse, we report
results from the full 859-dimensional representation in the main text.”
(7) I don't think authors have written what VALOR stands for.
Thank you for the reminder. We now define the VALOR acronym at its first mention in the
Abstract and Introduction and use the abbreviation thereafter.
(On page 2) “Using a state-of-the-art deep learning model (VALOR; Vision-Audio-Language
Omni-peRception)”
(On page 5) “To answer this, we apply a video-text alignment encoding framework, using
VALOR (Vision-Audio-Language Omni-peRception)—a high-performing, open-source model
that aligns visual and linguistic features over time—to predict brain responses during movie
watching.”
(8) When calculating equation (3), please make sure that the correlation values are
Fisher's r-to-z transformed.
Thank you for this reminder. We confirm that all correlation coefficients used in Equation (3)
are now Fisher r-to-z transformed prior to any averaging, contrasts, or statistical testing, and
this procedure is now explicitly stated in the Methods. We have also updated Fig. 4a (p. 15) to
reflect this transformation. Importantly, applying the r-to-z transformation does not change
the qualitative pattern of results or their statistical significance.
(9) I wasn't able to check the OSF data/codes because it required permission.
Thank you for flagging this, and we apologize for the inconvenience. We have removed the
permission restriction and set the OSF repository to public read-only access, which should
resolve the issue.
Reviewer #3 (Recommendations for the authors):
(1) The current approach extracts features from a single "best" layer of each model,
which may be suboptimal for predicting neural responses. Prior work has shown that
combining features across multiple layers through optimized fusion strategies (e.g., St-
Yves et al., 2023) or using model ensembles (e.g., Li et al., 2024) can substantially
improve encoding performance. The authors may consider these more comprehensive
approaches either as additional baselines or as alternative directions to enhance model
accuracy.
Thank you for this constructive suggestion. We agree that combining features across multiple
layers or using optimized fusion and ensemble strategies, as demonstrated in recent work
(e.g., St-Yves et al., 2023; Li et al., 2024), can substantially improve absolute encoding
performance.
In the present study, however, we intentionally evaluated each model using its single best-
performing layer within a matched encoding pipeline. This design choice was made to
maintain model-agnostic comparability and interpretability, and to ensure that performance
differences could be attributed primarily to the type of representation (e.g., temporally
informed video–text features versus static or unimodal features), rather than to differences
in model complexity, parameter count, or fusion strategy. Importantly, this constraint was
applied uniformly across all models and therefore does not favor VALOR over the baselines.
We now explicitly note in the Discussion (p. 19) that multilayer fusion and ensemble
approaches represent a natural and promising extension of our framework and are likely to
Neuroscience


## Page 42

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
42 of 43
further improve absolute prediction accuracy. Our goal in the current work was to establish
the practical utility and generalizability of temporally aligned video–text features for
naturalistic movie fMRI under a controlled and comparable evaluation setting..
(On page 19) “Third, for comparability across models we evaluated each model using its
single best-performing layer within a matched encoding pipeline rather than using
multilayer fusion or ensembling, which allowed us to attribute performance differences to
representational format but likely underestimates the absolute performance ceiling.”
(2) Given the naturalistic video-based task, the manuscript would benefit from including
state-of-the-art video-only models (e.g., Video Swin Transformer, VideoMAE, and other
more recent architectures) as explicit baselines. These models are designed to capture
spatiotemporal structure without relying on language input and would provide a more
targeted comparison to assess the specific contribution of temporal visual processing.
Thank you for this thoughtful suggestion. We agree that state-of-the-art video-only
spatiotemporal models (e.g., Video Swin Transformer, VideoMAE) are highly relevant
baselines for naturalistic movie paradigms and would provide a more targeted comparison
for isolating the contribution of temporal visual processing independent of language input.
In the present study, our primary goal was not to exhaustively benchmark all possible video
architectures, but to evaluate whether temporally informed video–text features can serve as
a practical and general-purpose encoding framework that improves upon the models most
commonly used in cognitive neuroscience for naturalistic fMRI (e.g., AlexNet for vision,
WordNet for semantic annotation, and CLIP for static multimodal alignment). Using these
established baselines allowed us to place our results in direct continuity with prior
neuroimaging work and to attribute performance differences to representational format
under a controlled encoding pipeline.
We agree that incorporating modern video-only spatiotemporal encoders is an important
next step, particularly for disentangling the relative contributions of temporal visual
structure and cross-modal video–text alignment. We now explicitly note this point in the
Discussion (p.19) as a limitation and future direction, and view such comparisons as a natural
extension of the current framework within the same TR-aligned encoding setup.
(On page 19) “Second, we did not directly compare VALOR to state-of-the-art video-only
spatiotemporal models (e.g., Video Swin Transformer, VideoMAE, and related architectures)
that are designed to capture temporal visual structure without language grounding; such
comparisons will be important for isolating the specific contributions of temporal visual
processing versus cross-modal video–text alignment in naturalistic neural responses.”
(3) An additional consideration is the scale of the AI models used for feature extraction.
Previous studies (e.g., Matsuyama et al., 2023) have indicated that model size -
particularly the number of parameters - can influence neural prediction performance,
independently of architecture. A discussion or analysis of how model size contributes to
the observed encoding gains would help clarify whether improvements are due to the
representational quality of the model or simply its scale
Thank you for this important point. We agree that model scale—particularly parameter count
—can influence neural prediction performance independently of architecture, as noted in
prior work (e.g., Matsuyama et al., 2023).
In the present study, our primary goal was to evaluate whether temporally informed video–
text representations provide practical advantages over unimodal and static multimodal
baselines that are widely used in cognitive neuroscience for naturalistic movie fMRI, under a
matched encoding pipeline. We did not perform a systematic scale-controlled analysis in this
revision because doing so would require training or evaluating multiple size-matched
Neuroscience


## Page 43

Fu et al., 2025 eLife 14:RP107607.  https://doi.org/10.7554/eLife.107607.2
43 of 43
variants across video-only and video–text architectures, which is beyond the scope of the
current work.
We therefore agree that part of the observed performance gains may reflect model capacity
in addition to representational format, and we caution against attributing all improvements
solely to cross-modal alignment or temporal structure. We now explicitly acknowledge this
limitation in the Discussion and note that comparing size-matched video-only and video–text
models within the same pipeline is an important next step for disentangling model scale from
representational content.
(On page 19) “Finally, part of VALOR’s advantage may reflect model capacity: larger
pretrained models often yield higher encoding accuracy, so repeating these analyses with
size-matched image-only and image–text models will be critical for disentangling model scale
from representational content.”
https://doi.org/10.7554/eLife.107607.2.sa0
Neuroscience


