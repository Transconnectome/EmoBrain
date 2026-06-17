# *** (2025) Evidence for compositionality in fMRI visual representations via Brain Algebra

**Source:** *** (2025) Evidence for compositionality in fMRI visual representations via Brain Algebra.pdf

---

## Page 1

communications biology
Article
A Nature Portfolio journal
https://doi.org/10.1038/s42003-025-08706-4
Evidence for compositionality in fMRI
visual representations via Brain Algebra
Check for updates
Matteo Ferrante
1
, Tommaso Boccato
1
, Nicola Toschi
2,6
& Ruﬁn VanRullen
3,4,5,6
Electrophysiological and neuroimaging studies have revealed how the brain encodes various visual
categories and concepts. An open question is how combinations of multiple visual concepts are
represented in terms of the component brain patterns: are brain responses to individual concepts
composed according to algebraic rules? To explore this, we generated “conceptual perturbations" in
neural space by averaging fMRI responses to images with a shared concept (e.g., “winter" or
“summer"). After thresholding to ensure speciﬁcity, we applied these perturbations to the neural
pattern associated with a base image, forming new brain patterns that incorporate the added concept.
These modiﬁed brain patterns were then decoded into images using a pretrained fMRI-to-image
decoding model. Qualitative and quantitative inspection of the resulting images provides insight into
how the brain might combine visual concepts. For example, adding a “winter" perturbation to the brain
pattern of a man on a skateboard yields a new pattern representing a man on a snowboard in a winter
scene—even when the perturbation modiﬁes only a small subset of voxels. Our ﬁndings reveal that
compositional processes in neural representations may lead to predictable perceptual outcomes, as
interpreted by our decoding model. This suggests that the brain’s combinatory encoding of concepts
may follow a systematic, algebraic-like process—what we term “brain algebra." Although our study is
model-driven, it opens avenues for future empirical work into the mechanisms of compositionality in
the brain.
The compositionality of latent representations in artiﬁcial intelligence (AI)
systems has contributed to recent advancements in deep learning. Model-
based techniques like word embeddings have demonstrated that semantic
relationships between concepts can be captured through vector arithmetic
—for example, “king” minus “man” plus “woman” yields a vector close to
“queen"1. Similarly, image and text representations in AI models exhibit
compositional properties that allow for the manipulation and combination
of visual and semantic concepts2–7.
In neuroscience, machine learning has spurred signiﬁcant progress
through the development of encoding and decoding models. These models
have established bidirectional mappings between visual or linguistic inputs
and corresponding brain activity8–22. Notably, the use of larger, multimodal,
and more complex models—which often exhibit some amount of compo-
sitionality—has led to signiﬁcant improvements in predicting brain activity
with encoding models. This suggests that better embeddings, enriched with
compositional properties, capture more nuanced information that aligns
more closely with the brain’s representations23–25. This raises a fundamental
question:doesthehumanbrainemployasimilarcompositionalstructure
in its neural code for vision26? Recent evidence suggests that brain-pattern
compositionality may indeed occur in speciﬁc linguistic contexts27: infor-
mation regarding analogy questions can be effectively retrieved through the
additionandsubtractionoffunctionalMagneticResonanceImaging(fMRI)
patterns. In their study, participants were presented with sequences of
related concepts, such as professions, tools, and places (e.g., “doctor",
“stethoscope", “hospital"). The researchers demonstrated that the algebraic
combination of fMRI activation patterns could reﬂect analogical reasoning,
akin to vector operations in word embeddings (e.g., “mechanic-doctor
+stethoscope=wrench").Moreover, the vector space representations uti-
lized by AI models appear to exhibit key properties essential for supporting
cognition, such as high-dimensional representations, compositionality,
concept distances, and similarity measures26.
Building on these ﬁndings, we investigate whether brain-pattern
compositionality holds for visual representations. Speciﬁcally, we aim to
determine whether the neural activity elicited by viewing a composite image
1Department of Biomedicine and Prevention, University of Rome, Tor Vergata (IT), Roma, Italy. 2Martinos Center For Biomedical Imaging, MGH and Harvard
Medical School (USA), Charlestown, USA. 3CerCo, CNRS UMR5549, Toulouse, France. 4Universite de Toulouse, Toulouse, France. 5ANITI, Toulouse, France.
6These authors contributed equally: Nicola Toschi, Ruﬁn VanRullen.
e-mail: matteo.ferrante@uniroma2.it; tommaso.boccato@uniroma2.it;
toschi@med.uniroma2.it; ruﬁn.vanrullen@cnrs.fr
Communications Biology |  (2025) 8:1263 
1
1234567890():,;
1234567890():,;


## Page 2

can be approximated by algebraically combining the neural patterns asso-
ciatedwithitsconstituentparts—aconceptwerefertoas"brainalgebra."In
this framework, adding the neural pattern associated with a particular
concept to the neural pattern of a base image should yield a new neural
pattern corresponding to the perception of the base image modiﬁed by the
added concept. This idea mirrors the compositional operations observed in
AI models, where vector arithmetic in latent spaces captures semantic
relationships between concepts. By testing this hypothesis in the context of
visual perception, we aim to uncover whether the brain employs a similar
mechanism for combining visual information.
In doing so, we also test a related hypothesis: if compositional structure
is embedded in neural representations, then it should manifest in the ability
to perturb only a sparse subset of voxels and still observe meaningful
transformations in perceptual content. This hypothesis enables us to
examine whether compositionality is supported by localized coding, dis-
tributed patterns, or a hybrid of both. While we do not aim to resolve the
broaderdebateonsemanticbrainorganization,our ﬁndingsprovide anovel
lens through which this question can be revisited.
While compositionality has been extensively studied in the context of
language models and visual generative systems in AI1,6,7, and recent neu-
roimaging work has shown compositional effects in linguistic reasoning
tasks27, little is known about whether similar compositional mechanisms
operate in the brain’s visual representations. Our study aims to bridge this
gap by testing whether algebraic operations on neural patterns derived from
real fMRI data can yield predictable and interpretable visual transforma-
tions. In doing so, we extend the investigation of compositionality from
semantic and multimodal embeddings to empirical neural representations
of visual cognition.
To address this question, we use the Natural Scenes Dataset (NSD)28, a
large-scale fMRI dataset where participants viewed approximately 10,000
natural images while their brain activity was recorded using a 7T fMRI
scanner.Wedeﬁne“base”brainpatternsasthefMRIresponsestoindividual
testimagesfromthisdataset.Wealsodeﬁne“concept”brainpatterns,where
we average the fMRI responses to multiple training set images that share a
speciﬁc concept. The presence of these concepts in training images is
identiﬁed using semantic embedding models (i.e., CLIP;6), ensuring that the
selected images are strongly related, from a semantic point of view, to the
target concept. By algebraically combining these patterns in brain space, we
create a perturbed brain pattern that hypothetically represents the base
image with the added concept. This is done by adding the thresholded
concept pattern to the base pattern. For example, starting with a base brain
pattern corresponding to an image of a man on a skateboard, we might add
the concept pattern for “winter" to generate a perturbed pattern that should
represent a man on a snowboard during winter.
A critical challenge is evaluating whether this perturbed brain pattern
truly corresponds to the brain representation of the base image with the
added concept. One approach would be to create corresponding composite
images—for instance, using generative AI models to synthesize images that
combine the base image with the added concept—and then present them to
participants in an fMRI experiment. By recording the brain activity elicited
by these composite images, we could compare the observed neural patterns
with the predicted ones derived from our “brain algebra” operations (ana-
logous to the approach used in ref. 27). However, this method presents
severaldifﬁculties.First,thenumberofpossiblecombinationsofbaseimages
and concepts leads to a combinatorial explosion in the number of stimuli
required. Testing a wide range of concepts and their combinations would
necessitate a prohibitive number of experimental trials. fMRI experiments
are inherently long and expensive, with limitations on how long participants
can be scanned and associated ﬁnancial costs with data acquisition. These
logistical constraints make it impractical to collect sufﬁcient data to robustly
evaluate compositionality across diverse concepts. Second, even if such
extensive experiments were feasible, interpreting the results would remain
challenging. Differences between the expected and observed brain patterns
could arisefromvarioussources,includingfMRInoise,individualvariability
in neural responses, or limitations in the quality and realism of the generated
stimuli. These confounding factors would challenge any deﬁnitive conclu-
sions about compositionality in the brain’s neural code.
Additionally, existing neurostimulation technologies do not currently
permit to directly manipulate speciﬁc voxel activations in the brain to test
compositionality.Wecannotselectivelystimulateoralterprecisepatternsof
neural activity at the voxel level to create the exact perturbed brain patterns
hypothesized by our “brain algebra” model. This limitation means that we
cannot empirically test the predicted neural patterns by artiﬁcially inducing
them in the brain.
Given these challenges, we employ an alternative approach that eval-
uates the “brain algebra” results using a decoding model. By transforming
the perturbed brain patterns into reconstructed images, we can indirectly
assess whether the algebraic combination of neural patterns corresponds to
meaningful composite perceptions. This method leverages existing fMRI
data and advanced decoding algorithms to infer the perceptual content
associated with the combined neural patterns, providing a practical lens to
explore our research question within the constraints of current technology.
Thus, instead of attempting to collect new fMRI data or manipulating
brain activity directly, we employ Brain-Diffuser10, a well-established
decoding modelthat maps brain activity into the latent space of a generative
model.Bydecodingtheperturbed brainpatterns,wecanreconstructimages
that represent the hypothetical perception resulting from our brain algebra
operations. The resulting images can be assessed qualitatively—through
visual inspection—or quantitatively using automated semantic analysis
tools based on AI systems like CLIP6. In summary, our study explores
whether the compositionality observed in AI systems and linguistic brain
representations extends to visual processing in the human brain. We
introduce a novel method to assess “brain algebra," combining base and
concept brain patterns derived from actual fMRI data, and employ the
Brain-Diffuser model to decode these patterns into images. Through this
method, we aim to provide evidence for or against the existence of com-
positional neural codes in visual cognition. In the following sections, we
detail our methodology for deﬁning and combining the base and concept
brain patterns, describe how we employ the Brain-Diffuser model for
decoding, and present our qualitative and quantitative analyses of the
reconstructed images to evaluate compositionality. See Fig. 1 for a visual
explanation of perturbation deﬁnition and Fig. 2 for a visual overview of our
approach.
Results
We explored 12 different semantic concepts encompassing themes such as
season (winter, summer), gender (man, woman), lighting (night, day),
numerosity (empty, crowded), location (indoor, outdoor) and emotions
(happy, sad). Each corresponding perturbation vector was thresholded by a
variable amount (retaining between 5% and 100% of the voxels, the rest
being set to zero), and scaled by various factors α (from 1 to 4) before being
summed with base fMRI patterns corresponding to a random subset
composed of 100 test images. We begin this section by discussing the
qualitative results, focusing on the exemplary Figs. 3 and 4, which were
generated using a scaling factor of α = 2 and a 50% threshold to visually
highlight the key outcomes. Additional ﬁgures with varying scaling values
and thresholds are provided in the supplementary materials for a more
comprehensive evaluation.
In the ﬁrst set of images (top of Fig. 3), showing horses in a ﬁeld and an
indoor bathroom, compositionality is evident. Concepts like “summer,"
“winter," and “night” alter the landscape and lighting in the horse scene,
while“woman”and “man”introduceanadditionalperson.Inthebathroom
scene, “crowded” and “empty” adjust the number of objects or people, and
“summer” and “winter” change the mood. The bottom row, showing a
skater and a social gathering, also demonstrates compositional transfor-
mations. “Summer” and “winter” modify the environment, “woman”
changes the skater’s gender, and “crowded” and “happy” alter social
dynamics and expressions.
Similarly, perturbations in Fig. 4 introduce clear modiﬁcations based
on the perturbation concepts. For the bus scene, “summer” brings brighter
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
2


## Page 3

environments with outdoor activities (however, the bus is no longer pre-
sent), while “night” darkens the scene with illuminated elements. The
“indoorscene”concepttransforms the businto amoreenclosed space,like a
terminal. Perturbations applied to the man holding a sandwich show clear
changes—“woman” alters the subject’s gender, “empty” reduces the per-
son’s size within the scene, and “crowded” adds individuals to the scene. In
the outdoor table scene and paragliding activity, compositional adjustments
are also evident. These results suggest that the model effectively generates
Fig. 2 | Illustration of the “brain algebra” approach used in our study. The
leftmost image represents the initial visual stimulus presented to the participant,
with corresponding fMRI activations shown as heatmaps across different brain
regions. Perturbations are introduced by summing the base brain pattern with a
concept-speciﬁc perturbation vector, such as “summer,” “winter,” “man,” or
“woman.” The perturbation vector is computed as a thresholded average of brain
patterns evoked by visual perception of images with that content (see Fig. 1). The
perturbed brain patterns (center) are subsequently decoded using a pretrained fMRI
decoder, producing modiﬁed images that reﬂect the added conceptual information
(right). The results demonstrate how small changes in neural patterns can lead to
predictable and meaningful changes in visual perception, supporting the hypothesis
of compositionality in neural representations.
Fig. 1 | A visual overview of the process used to deﬁne conceptual perturbation
vectors based on “winter” and “summer” concepts. First, the textual representa-
tions of the concepts are encoded using the CLIP Text model, generating 512-
dimensional embeddings. Simultaneously, images from the NSD training set are
processed through the CLIP Vision model to obtain vision embeddings. Cosine
similarity is calculated between the vision embeddings and the textual concept
embeddings (e.g., “winter” and “summer”), allowing us to select the top-matching
images that best represent each concept. The fMRI patterns corresponding to these
selected images are then averaged to generate concept-speciﬁc perturbation patterns
in brain space, such as zwinter for winter and zsummer for summer. These perturbation
vectors are later thresholded, and combined with base fMRI patterns in the brain
algebra framework to modulate visual representations (see Fig. 2).
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
3


## Page 4

coherent and predictable changes in response to targeted brain perturba-
tions. Overall, these results support the hypothesis that compositionality in
brain patterns can be decoded into visually meaningful images. The per-
turbations introduced lead to expected modiﬁcations in both human-
relatedandenvironmentalaspects,whilegenerallymaintainingtheintegrity
of the original base scenes. This indicates that the brain perturbation pat-
terns successfully capture abstract conceptual information and translate it
into visual content, providing strong evidence for compositionality in the
brain’s visual representations.
While these qualitative examples generally support our hypothesis of
visual concept compositionality, they also include some perturbations for
which the desired concept did not obviously appear or was difﬁcult to
evaluate (e.g., paragliding+day appears similar to the base image stimulus),
and perturbations that replaced the initial content rather than com-
plementing it (such as the disappearing bus in the bus+summer pertur-
bation). To provide a more systematic evaluation of compositionality, we
quantitatively measured the presence of both the perturbation concept and
the base image concepts in the decoded images from perturbed brain pat-
terns,byleveragingcosine similarityintheCLIP latent space asa measureof
semantic content (since this metric is shown to be aligned with human
judgments on image similarity29,30).
This quantitative evaluation of the decoded perturbed images reveals
cleartrendsinthesimilaritybetweentheimagesandtwotargets:theoriginal
image and the concept used for perturbation. In the bottom panel of Fig. 5,
Fig. 3 | Qualitative evaluation of brain algebra perturbations applied to base
images (images best viewed digitally). Starting from the central base images,
decoded from a (non-perturbed) base fMRI pattern, perturbations corresponding to
various concepts---such as “summer,” “winter,” “day,” “night,” “man,” “woman,”
and more---are applied to the brain patterns. The resulting decoded images show
how the base visual perception is altered by the addition of each conceptual per-
turbation, reﬂecting changes in environmental conditions, the presence or absence
of people, and other context-speciﬁc details. This demonstrates the ability of brain
algebra to generate compositional modiﬁcations in visual representations based on
abstract conceptual inputs.
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
4


## Page 5

which assesses the similarity (in the CLIP-vision latent space) between the
decoded perturbed images and the original images, we observe that simi-
larity decreases as the scaling value increases. This is expected, since larger
scaling values apply a stronger perturbation, causing more deviation from
the original image. The similarity between the decoded perturbed images
and the original images remains signiﬁcantly above the baseline for all
conditions (calculated by contrasting decoded images against randomly
chosen base images), indicating that elements of the original image are still
retained even as the perturbation intensiﬁes.
The top panelof Fig. 5, which compares the decoded perturbed images
to the target concept (across CLIP-vision and CLIP-text latent spaces,
respectively), shows the opposite trend: similarity increases as the scaling
value rises. This suggests that larger scaling values make the images more
representative of the added concept. Lower thresholds allow the perturba-
tion to have a broader effect, leading to faster increases in similarity to the
target concept, while higher thresholds limit the impact of the perturbation,
resulting in slightly more modest increases. In all cases, the similarity
between the decoded images and the target concept remains consistently
above the baseline (calculated by contrasting random images with the target
concept), demonstrating that the perturbation effectively introduces the
desired conceptual information into the images. Interestingly, even at high
thresholds,where only a small portionof the brain’s activityisperturbed, we
still observe notable changes in similarity to the target concept. The fact that
meaningful conceptual shifts occur even when the perturbation is restricted
to higher thresholds indicates that the brain might encode these abstract
concepts in localized areas, and only subtle changes in activity within these
regions are required to reﬂect concept-driven modiﬁcations in the decoded
images. Overall, these results illustrate a trade-off between maintaining
similarity to the original image and introducing conceptual modiﬁcations.
As scaling increases, the perturbed images deviate more from the original
content but become more aligned with the target concept. The thresholding
mechanism provides a way to control the extent of the perturbation, with
Fig. 4 | More examples as in Fig. 3.
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
5


## Page 6

Fig. 5 | Top: Average similarity between decoded perturbed images and the target
concept (across CLIP-vision and CLIP-text latent spaces, respectively) across dif-
ferent thresholds (0, 25, 50, 75, 90, 95th percentiles of the voxel distribution) and
scaling values (0 to 4, with zero corresponding to the base pattern without pertur-
bation). The similarity increases with higher scaling values, reﬂecting that larger
perturbations align the decoded image more closely with the target concept. The
green shaded region represents variability (standard deviations across 4 subjects, 100
images per concept, 12 concepts) in similarity, while the red dashed line represents
the baseline similarity between random images and the target concept. Bottom:
Average similarity (in the CLIP-vision latent space) between decoded perturbed
images and the original images across the same thresholds and scaling values. The
similarity decreases as the scaling value increases, indicating that larger perturba-
tions deviate more from the original image. The red dashed line shows the baseline
similarity between the original image and random images.These results indicate a
trade-off between maintaining original image features and introducing conceptual
modiﬁcations, depending on the scaling value and threshold.
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
6


## Page 7

higher thresholds preserving more of the original image and lower
thresholds allowing for greater conceptual compositionality.
While our focus is on subject-speciﬁc decoding, we note that the
compositional effects observed in our perturbation experiments generalize
across the four participants includedin our study. This is evident both in the
consistency of decoding trends and in the qualitative similarity of recon-
structed outputs across subjects (see Fig. 5).
To further explore the spatial characteristics of conceptual perturba-
tions, we visualized the top 10% most active voxels (thresholded at the 90th
percentile) for each of the 12 semantic concepts in a representative subject
(Fig. 6). These maps reveal that different concepts elicit distinct spatial
patterns in visual cortex. Scene-related concepts suchas indoor and outdoor
show broad bilateral activation in occipital and parahippocampal regions,
while social categories like man, woman, and crowded engage more lateral
and ventral regions, consistent with areas implicated in face and body
perception (e.g., FFA, EBA). Emotion-related concepts such as happy and
sad exhibit more diffuse patterns, yet still evoke reproducible changes in
localized patches. Importantly, conceptually opposing categories (e.g.,
summer vs. winter, crowded vs. empty) result in spatially distinct pertur-
bation maps, suggesting that these brain-based concept representations are
separable and consistent with a compositional structure. These ﬁndings are
in line with our hypothesis that the brain can perform algebraic operations
withinconcept-speciﬁcsubspacesofneuralrepresentation.Whatappearsto
matter is not solely the anatomical localization of activity, but rather the
patterned distribution of neural responses across the voxel space. This
supports the notion that conceptual information is embedded in a vectorial
format, enabling systematic operations akin to those observed in semantic
embeddings and artiﬁcial models of compositionality.
Discussion
The ﬁndings from this study provide a promising indication of composi-
tionality in neural representations. By manipulating brain patterns in a
“brain algebra” framework—combining a base neural state with a thre-
sholded and scaled perturbation vector—we observed distinct, meaningful
changes in the decoded images. This suggests that visual processing in the
brainmayfollowacompositionalstructure,muchlikelanguage,wherebasic
elements can be combined to create more complex representations. The
ability to successfully decode these perturbations aligns with broader the-
ories on compositionality in cognition, such as in language, where concepts
are combined to produce new meanings (e.g., “queen” = “king” - “man” +
“woman”). This parallel between vision and language highlights how the
brain may generalize compositional principles across different domains of
cognition, supporting ﬂexible and dynamic perceptual and cognitive
processes2,4,27.
The use of natural images as stimuli is integral to our approach, as it
enables the study of brain patterns in conditions that closely mimic real-
world visual experiences. These images contain a variety of visual and
semantic elements that reﬂect everyday interactions with the environment.
By leveraging these stimuli, we can investigate how the brain processes
complex compositional patterns that are more representative of natural
vision, compared to more controlled or artiﬁcial stimuli.
There are, however, important limitations to consider. While our
results suggest compositionality in neural representations, our evaluation
relies on a decoding model to interpret the perturbed brain patterns.
Although the two brain patterns we are combining are derived from actual
fMRI data, the interpretation of their combination is model-driven because
it depends on the decoder’s ability to accurately reconstruct images from
brain activity. This means that our conclusions are contingent upon the
performance and limitations of the decoding model, and we are not directly
observing brain processes in real-time but interpreting them through the
lensofthemodel.Thislimitstheextenttowhichwecanconﬁrmthatsimilar
compositional operations happen naturally in the brain. Additionally, we
are constrained by the need for sufﬁcient training data—only concepts with
ample representation in the training set allow us to generate reliable per-
turbation vectors. As a result, our exploration of neural compositionality is
bounded by the availability of data, limiting the range of concepts we can
examine. Furthermore, some concepts are not orthogonal, and their
representations in the training set can lead to biased perturbations in brain
patterns. For instance, visual inspection shows that adding the concept of
“happiness” occasionally introduces food elements, likely because in data-
setslikeCOCO,“happiness”isoftenassociatedwith,orco-occursalongside,
imagesoffood.Similarly,conceptslikenumerosityoremotionmightalsobe
biased due to their frequent co-occurrence with humans. As a result,
applyinga“crowded”perturbationmayaddhumanstosceneswithanimals,
even when the intended effect is only to increase the number of animals.
One intriguing aspect of our results is that meaningful changes were
observed even when the perturbation involved only a small subset of voxels
(e.g., the top 5% of voxels). This suggests that relatively small, localized
regions of the brain can signiﬁcantly inﬂuence the representation of speciﬁc
concepts. This ﬁnding contributes to the ongoing debate between dis-
tributed and localized cortical representations in visual processing31–33. On
the one hand, proponents of distributed representations, such as Haxby and
colleagues, argue that visual information is encoded across widespread
patternsofneuralactivity,withobjectandcategoryinformationrepresented
in distributed and overlapping voxel patterns34. On the other hand,
researchers like Kanwisher propose that certain visual categories are pro-
cessed in specialized, localized cortical regions—for example, the fusiform
face area (FFA) for face perception35. Our observation that concept per-
turbations are effective even when modifying only a small portion of voxels
aligns with the idea that speciﬁc cortical areas play a crucial role in repre-
senting certain concepts. These perturbations, when decoded, yield image
reconstructions that reﬂect conceptually altered visual content, suggesting a
shift in perceptual representation as inferred by the decoding model.
Theseﬁndingsinviteanuancedinterpretationofhowcompositionality
and modularity coexist in neural coding. While compositionality typically
refers to operations within a single high-dimensional space, our results
suggest that different concepts may be encoded in partially distinct, func-
tionally specialized subspaces within that space. This modular organization
does not preclude algebraic manipulation but rather supports it: perturba-
tions restricted to voxels most strongly associated with a concept can still
generatecoherentsemantictransformationswhencombinedwithunrelated
base patterns. This suggests that the brain’s representational geometry may
be composed of overlapping but structured subspaces that enable both
modular specialization and compositional generalization.
In summary, our ﬁndings provide evidence suggesting composition-
ality in the brain’s processing of visual stimuli. This compositional structure
could be key to understanding how the brain ﬂexibly combines sensory
information to form different percepts, furthering our understanding of
neural coding, perception, and learning.
Conclusions
In this study, we explored the compositionality of neural representations
through the novel framework of “brain algebra," combining base fMRI
patterns with conceptual perturbations to decode visual representations.
Our ﬁndings provide evidence that the brain may employ compositional
mechanisms similar to those seen in language and cognition, where smaller
elements are combined to form more complex representations. The results
demonstrate that neural patterns can be manipulated to create distinct and
predictable changes in decoded images, aligning with the target concepts,
even when only small portions of brain activity are perturbed.
The ﬁndings suggest that neural representations of visual concepts
involve both localized and distributed processing. The ability to change
perceived images by modifying a small number of voxels indicates that
certain brain regions are specialized for processing speciﬁc visual infor-
mation, supporting the idea of localized specialization. However, these
localized changes also integrate with broader neural networks, aligning with
the view that visual perception involves distributed representations. This
dual role of localized and distributed coding contributes to the debate in
neuroscience and underscores the complexity of how the brain processes
and combines visual information.
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
7


## Page 8

Overall, this work contributes to a deeper understanding of neural
compositionality in vision and highlights the brain’s capacity to integrate
conceptual information. By offering new perspectives on how perturbations
inneuralspacecorrespondtochangesinperception,thisresearchprovidesa
foundation for future studies on neural coding, perceptual constancy, and
cognitive ﬂexibility. Expanding this line of inquiry could also reveal insights
into how the brain composes and generalizes across other cognitive
domains, such as language and broader semantic representations. This
Fig. 6 | Spatial distribution of the top 10% most active voxels (90th percentile) for
each concept for Subj01, visualized on cortical surfaces. Distinct patterns emerge
across categories---e.g., scene-related ("indoor", “outdoor"), social ("man", “woman",
“crowded"), and emotional ("happy", “sad")---highlighting the diversity and speci-
ﬁcity of conceptual representations in brain space.
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
8


## Page 9

suggests that the principles underlying “brain algebra” in vision might
extend to other brain functions, hence providing a more comprehensive
framework
for
understanding
compositional
processes
in
neural
representations.
Methods
In this section, we describe the proposed method and the data we used. The
data
are
publicly
available
and
can
be
requested
at
https://
naturalscenesdataset.org/. All experiments and models were trained on a
server equipped with eight NVIDIA A100 GPU cards (80GB RAM each
connected through NVLINK) and 2 TB of System RAM.
Data
The study employs the Natural Scenes Dataset (NSD)28, an extensive fMRI
dataset gathered from eight participants who were shown images from the
COCO21 dataset. Our analysis focused on four subjects, resulting in a
specialized training set containing 8859 images and 24,980 fMRI trials per
subject, as well as a shared dataset consisting of 982 images and 2770 trials
per subject. To reduce the spatial dimensionality of the fMRI signals (with a
resolution of 1.8mm isotropic), we applied a mask using the provided
NSDGeneral ROI, targeting multiple visual areas. This deliberate selection
of ROIs improved the signal-to-noise ratio and reduced data complexity,
enabling the investigation of both low- and high-level visual features.
Temporal dimensionality was further minimized by leveraging pre-
computed betas derived from a general linear model (GLM;36,37) with an
adjustedhemodynamicresponsefunction(HRF)andadenoisingprocessas
detailed in the NSD publication.
BrainDiffuser
The “Brain-Diffuser” model10 is a two-stage framework designed to
reconstruct natural scenes from fMRI signals. In the ﬁrst stage, a Very Deep
Variational Autoencoder (VDVAE) generates an “initial guess” of the
reconstruction, capturing low-level details. This guess is then reﬁned using
high-level semantic features from CLIP-Text and CLIP-Vision models, and
a latent diffusion model (Versatile Diffusion;38) is used for the ﬁnal image
generation. The model takes fMRI signals as input and produces recon-
structed images that reﬂect both low-level properties and the overall scene
layout. Brain-Diffuser, was trained subject-wise with data from Subj01,
Subj02, Subj05, Subj07). More information about the decoding model is
detailed in the original paper. While this speciﬁc pipeline is used in our
study, our proposed method is universally applicable and can enhance any
single-subject decoding pipeline. It offers a versatile, adaptable tool that can
seamlessly integrate with novel, advanced pipelines. By focusing on pre-
processing input data, our approach enables the underlying pipeline—
regardless of its unique aspects—to effectively work with single-subject
fMRI data to generate images, without requiring direct modiﬁcations to the
pipeline itself.
Main experiment
Here we outline our main experiment, which aims to decode synthetic brain
patterns derived from the algebraic sum of real brain patterns, and examine
compositionality in the decoded images. The NSD dataset provides paired
fMRIdataandcorrespondingimages.Let’sdeﬁnefMRIdataaszandimages
as x, giving us a training set of pairs (ztr, xtr) and a test set (zts, xts). Addi-
tionally, we have a decoder d, a function that maps z to x, such that x ≈d(z).
The essence of our work is as follows: we explore the outcome when
decodingz0, deﬁned as z0 ¼ zbase þ αzperturb, where α is a scalingfactor, zbase
is a brain pattern drawn from the test set, and zperturb is a perturbation
pattern computed by averaging training set brain patterns associated with a
speciﬁc concept. One way to investigate compositionality in the brain is to
hypothesize that the resulting image, x0 ¼ dðz0Þ, represents a combination
of the base image xbase and an additional concept.
For instance, if the base pattern zbase corresponds to an image of an
indoor scene xbase, and we add a perturbation brain pattern zperturb related to
the concept of a man, then decoding z0 might produce an image of a man in
an indoor scene. Similarly, if the perturbation pattern corresponds to a
woman, we might expectthe decoded image to depict a woman in the scene,
and so on. We tested our framework for a random subset (identical for all
subjects) of 100 images drawn from the test set.
Pattern deﬁnition and thresholding. A natural question arises: how do
we deﬁne the perturbation pattern relative to a speciﬁc concept? We
adopted a straightforward approach by ﬁltering the image-fMRI pairs in
the training dataset based on their similarity to the concept, which is
deﬁned in natural language and measured using a CLIP-based cosine
similarity.
We explored 12 different semantic concepts: ["man", “woman",
“indoor", “outdoor", “summer", “winter", “day", “night", “crowded",
“empty", “happy", “sad"]. These concepts encompass themessuch as season,
gender, lighting, numerosity, emotions.
Each concept was represented as a word and encoded using the CLIP
Text model6, producing a 512-dimensional representation (using version
clip-vit-base-patch32). We then used the CLIP Vision encoder to encode all
the images in the training set and calculated the cosine similarity between
each image and all the concepts. This resulted in a similarity matrix of shape
(8859, 12). For each concept, we selected the top 100 pairs with the highest
similarity scores to extract the corresponding fMRI and image indices. The
perturbation patterns were then deﬁned by averaging the fMRI patterns
associatedwiththesetop-100pairs,therebyestablishingtheirrepresentation
in brain space.
We applied various threshold values to the perturbation patterns based
on their percentile values. Speciﬁcally, in our experiments, we evaluated the
outcomes by thresholding zperturb and retaining only the values above the
0th, 25th, 50th, 75th, 90th, or 95th percentiles. This allows us to assess
whether the representation of the chosen broad semantic concepts is dis-
tributed across the entire visual cortexor if only a small region is responsible
for encoding changes, with the composition of values in these small regions
being sufﬁcient to produce compositional images when decoded. Impor-
tantly, it is worth emphasizing that all compositional operations in our
framework are performed directly in brain space—that is, on real fMRI-
derived neural patterns—before any decoding takes place. This distinction,
coupled with sparsity and non-linearity introduced by thresholding pro-
cedure avoids circularity and ensuresthat any emerging semantic effects are
a result of the structure present in the fMRI data itself, rather than learned
priors in the decoding model. Moreover, our use of voxel-wise thresholding
enables us to probe whether concept representations are localized or dis-
tributed, and to what extent localized subspaces are sufﬁcient for compo-
sitional decoding. This design choice allows us to explore the neural
geometryunderlyingcompositionalitywithoutassumingfulldistributionor
strict modularity. Please see Supplementary Table 1 for an assessment of
Brain-Diffuser performances on threhsolded patterns and Supplementary
Figs. for activation patterns for all concepts and subjects.
Evaluation
The ﬁrst part of our evaluation is qualitative, focusing on visually assessing
decoded images from perturbed brain patterns to examine the composi-
tionality of the original stimulus image and the perturbation concept.
However, a quantitative measure is necessary to rigorously evaluate this
compositionality. Compositionality can be loosely deﬁned as the co-
occurrence of two concepts within an image. In our framework, we adopt a
practicalworking deﬁnition of compositionalitythat aligns with approaches
in large-scale neural models such as CLIP or GPT. Speciﬁcally, we deﬁne
compositionality as the ability to algebraically combine neural patterns
associated with distinct concepts to produce a new, coherent representation
that reﬂects both components. This does not imply formal semantic com-
positionality in the linguistic sense (i.e., deriving a compound meaning
strictly from parts and syntax), but rather refers to the integration of mul-
tiple conceptual features into a uniﬁed and plausible perceptual scene. Thus,
we need to quantify how closely the decoded image resembles the target
perturbation concept while retaining similarity to the original content. If the
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
9


## Page 10

scaling factor α is too large, the perturbation may replace the original
content entirely, leading to misleading results if we only measure the
similarity between the decoded images and the perturbation concept.
To address this, we calculated the CLIP cosine similarity between the
decoded perturbedimagesand theoriginalstimuli to ensure thattheoriginal
content was not entirely replaced. Simultaneously, we measured the CLIP
cosine similarity between the decoded perturbed images and the perturba-
tionconcept.Intheﬁrstcase,wemeasuredcosinesimilaritybetweenimages,
while in the second case, the similarity was measured between images and
text. As these two metrics may have different baselines, we also computed a
randombaselinebymeasuringthecosinesimilaritybetweeneachbaseimage
and 100 randomly selected images from the training set. Similarly, we
established a baseline for each concept using 100 random images.
Finally, we averaged the results as a function of the scaling factor α for
each threshold across all decoded images and subjects.
Statistics and Reproducibility
All experiments were conducted using data from four participants in the
publiclyavailableNaturalScenesDataset(NSD).Foreachsubject,thetraining
set included 24,980 fMRI trials corresponding to 8859 unique images, and the
test set included 2770 fMRI trials for 982 unique images. A ﬁxed random
subset of 100 test images was used consistently across subjects in the main
decoding experiments. For each semantic concept, perturbation vectors were
computed by averagingthe fMRI patternsof the top 100 training images most
semantically related to the target concept (measured via cosine similarity in
CLIP-embedding space). Quantitative analyses were based on computing
cosine similarity in the CLIP latent space between the decoded images and
both the original base images and the textual representations of target con-
cepts. These measurements were averaged across subjects, concepts, and test
images, and variability was reported as standard deviation across the four
subjects. No formal statistical hypothesis testing (e.g., p-values or conﬁdence
intervals) was conducted, as the objective was to characterize systematic
decoding trends rather than population-level inference.
Reproducibility is supported by the use of a public dataset (NSD),
standard pretrained models (CLIP and Brain-Diffuser), and a ﬁxed
experimental pipeline. All custom code and scripts used for preprocessing,
perturbation generation, and decoding will be made publicly available upon
publication.
Reporting summary
Further information on research design is available in the Nature Portfolio
Reporting Summary linked to this article.
Data availability
The data supporting the ﬁndings of this study are publicly available. The
fMRIdataandcorrespondingimagestimuliwereobtainedfromtheNatural
Scenes Dataset (NSD)28. All preprocessing scripts and derived datasets used
in the analyses will be public released upon acceptance. Supplementary
Data 1 and Supplementary Data 2 provide numerical sources to repro-
duce Fig. 5.
Code availability
The custom code used for preprocessing fMRI data, generating brain per-
turbation patterns, and performing image decoding with the Brain-Diffuser
model will be made publicly available upon acceptance of this manuscript at
this link: https://github.com/matteoferrante/BrainAlgebra. The Brain-
Diffuser model itself is described in detail in its original publication39.
Received: 13 January 2025; Accepted: 11 August 2025;
References
1.
Mikolov, T., Yih, W.-t. & Zweig, G. Linguistic regularities in continuous
space word representations. In Vanderwende, L., Daumé III, H. &
Kirchhoff, K. (eds.) Proceedings of the 2013 Conference of the North
American Chapter of the Association for Computational Linguistics:
Human Language Technologies, 746–751 (Association for
Computational Linguistics, Atlanta, Georgia, 2013). https://
aclanthology.org/N13-1090.
2.
Lepori, M. A., Serre, T. & Pavlick, E. Break it down: Evidence for
structural compositionality in neural networks https://arxiv.org/abs/
2301.10884 (2023).
3.
Lake, B. M. & Baroni, M. Human-like systematic generalization
through a meta-learning neural network. Nature 623, 115–121 (2023).
4.
Russin, J., McGrath, S. W., Williams, D. J. & Elber-Dorozko, L. From
frege to chatgpt: Compositionality in language, cognition, and deep
neural networks https://arxiv.org/abs/2405.15164 (2024).
5.
Shi, C. et al. Exploring compositional visual generation with latent
classiﬁer guidance https://arxiv.org/abs/2304.12536 (2023).
6.
Radford, A. et al. Learning transferable visual models from natural
language supervision (2021).
7.
Goh, G. et al. Multimodal neurons in artiﬁcial neural networks. Distill
https://distill.pub/2021/multimodal-neurons (2021).
8.
Oota, S. R. et al. Deep Neural Networks and Brain Alignment: Brain
Encoding and Decoding (Survey) http://arxiv.org/abs/2307.10246
(2023). ArXiv:2307.10246 [cs, q-bio].
9.
Scotti, P. S. et al. Reconstructing the mind’s eye: fmri-to-image with
contrastive learning and diffusion priors (2023).
10. Ozcelik, F. & VanRullen, R. Brain-diffuser: Natural scene
reconstruction from fmri signals using generative latent diffusion
(2023).
11. Caucheteux, C. & King, J. Brains and algorithms partially converge in
natural language processing. Commun. Biol. 5, 134 (2022).
12. Tang, J. et al. Semantic reconstruction of continuous language from
non-invasive brain recordings. Nat. Neurosci. 26, 858–866 (2023).
13. Huth, A., Nishimoto, S., Vu, A. & Gallant, J. A continuous semantic
space describes the representation of thousands of object and action
categories across the human brain. Neuron 76, 1210–1224 (2012).
14. Ferrante, M., Boccato, T. & Toschi, N. Semantic brain decoding: from
fmri to conceptually similar image reconstruction of visual stimuli
(2023).
15. Ferrante, M., Boccato, T., Ozcelik, F., VanRullen, R. & Toschi, N.
Multimodal decoding of human brain activity into images and text. In
UniReps: the First Workshop on Unifying Representations in Neural
Models https://openreview.net/forum?id=rGCabZfV3d (2023).
16. Ferrante, M., Boccato, T. & Toschi, N. Through their eyes: multi-
subject brain decoding with simple alignment techniques (2023).
17. Antonello, R., Vaidya, A. & Huth, A. G. Scaling laws for language
encoding models in fmri (2023).
18. Caucheteux, C., Gramfort, A. & King, J. Evidence of a predictive
coding hierarchy in the human brain listening to speech. Nat. Hum.
Behav. 7, 430–441 (2023).
19. Takagi, Y. & Nishimoto, S. High-resolution image reconstruction with
latent diffusion models from human brain activity. bioRxiv https://
www.biorxiv.org/content/early/2023/03/11/2022.11.18.517004
(2023).
20. Chen, Z., Qing, J., Xiang, T., Yue, W. L. & Zhou, J. H. Seeing beyond
the brain: conditional diffusion model with sparse masked modeling
for vision decoding (2022).
21. Lin, S., Sprague, T. & Singh, A. K. Mind reader: Reconstructing
complex images from brain activities (2022).
22. Ferrante, M., Ciferri, M. & Toschi, N. R&b – rhythm and brain: cross-
subject decoding of music from human brain activity https://arxiv.org/
abs/2406.15537 (2024).
23. Choksi, B., Mozafari, M., VanRullen, R. & Reddy, L. Multimodal neural
networks better explain multivoxel patterns in the hippocampus.
Neural Netw. 154, 538–542 (2022).
24. Antonello, R. & Huth,A. Predictive coding or just feature discovery?an
alternative account of why language models ﬁt brain data. Neurobiol.
Lang. 5, 64–79 (2024).
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
10


## Page 11

25. Gifford, A. T. et al. The algonauts project 2023 challenge: How the
human brain makes sense of natural scenes (2023).
26. Piantadosi, S. T. et al. Why concepts are (probably) vectors. Trends
Cogn. Sci. 28, 844–856 (2024).
27. Wu, M.-H., Anderson, A. J., Jacobs, R. A. & Raizada, R. D. S. Analogy-
related information can be accessed by simple addition and
subtraction of fMRI activation patterns, without participants
performing any analogy task. Neurobiol. Lang. 3, 1–17 (2022).
28. Allen, E. J. et al. A massive 7t fmri dataset to bridge cognitive
neuroscience and artiﬁcial intelligence. Nat. Neurosci. 25, 116–126
(2022).
29. Hernández-Cámara, P., Vila-Tomás, J., Malo, J. & Laparra, V.
Measuring human-CLIP alignment at different abstraction levels. In
ICLR 2024 Workshop on Representational Alignment https://
openreview.net/forum?id=xQyhHjLGmj (2024).
30. Muttenthaler, L. et al. Aligning machine and human visual
representations across abstraction levels https://arxiv.org/abs/2409.
06509 (2024).
31. Tsao, D. Y., Freiwald, W. A., Knutsen, T. A., Mandeville, J. B. & Tootell,
R. B. Faces and objects in macaque cerebral cortex. Nat. Neurosci. 6,
989–995 (2003).
32. Reddy, L. & Kanwisher, N. Coding of visual objects in the ventral
stream. Curr. Opin. Neurobiol. 16, 408–414 (2006).
33. Grill-Spector, K. & Weiner, K. The functional architecture of the ventral
temporal cortex and its role in categorization. Nat. Rev. Neurosci. 15,
536–548 (2014).
34. Haxby,J.V. et al. Distributedandoverlappingrepresentations of faces
and objects in ventral temporal cortex. Science 293, 2425–2430
(2001).
35. Kanwisher, N., McDermott, J. & Chun, M. M. The fusiform face area: a
moduleinhumanextrastriatecortexspecializedfor faceperception.J.
Neurosci. 17, 4302–4311 (1997).
36. Prince, J. S. et al. Improving the accuracy of single-trial fmri response
estimates using glmsingle. eLife 11, e77599 (2022).
37. Kay, K., Rokem, A., Winawer, J., Dougherty, R. & Wandell, B.
Glmdenoise: a fast, automated technique for denoising task-based
fmri data. Frontiers in Neuroscience 7, https://www.frontiersin.org/
journals/neuroscience/articles/10.3389/fnins.2013.00247 (2013).
38. Xu, X., Wang, Z., Zhang, E., Wang, K. & Shi, H. Versatile diffusion: Text,
images and variations all in one diffusion model https://arxiv.org/abs/
2211.08332 (2024).
39. Ozcelik, F. & VanRullen, R. Natural scene reconstruction from fmri
signals using generative latent diffusion. Sci. Rep. 13, 15666 (2023).
Acknowledgements
This work was supported by NEXTGENERATIONEU (NGEU) and funded by
the ItalianMinistryofUniversity and Research (MUR),National Recovery and
Resilience Plan (NRRP), project MNESYS (PE0000006) (to NT)- A Multiscale
integratedapproachtothestudyofthenervoussysteminhealthanddisease
(DN. 1553 11.10.2022); by the MUR-PNRR M4C2I1.3 PE6 project
PE00000019 Heal Italia (to NT); by the NATIONAL CENTRE FOR HPC, BIG
DATA AND QUANTUM COMPUTING, within the spoke “Multiscale Model-
ing and Engineering Applications” (to NT); the EXPERIENCE project (Eur-
opean Union’s Horizon 2020 Research and Innovation Programme under
grant agreement No. 101017727); the CROSSBRAIN project (European
Union’s European Innovation Council under grant agreement No.
101070908), ANITI Chair (ANR grant ANR-19-PI3A-004), an ANR grant AI-
REPS ANR-18-CE37-0007-01 and an ERC Advanced Grant GLoW (grant
101096017) to RV.
Author contributions
M.F. and R.V.R. conceived the study. M.F. implemented the code,
conducted the analyses, and drafted the initial manuscript. T.B. contributed
to the interpretation of results and critically revised the manuscript. R.V.R.
and N.T. provided scientiﬁc guidance, mentorship, and overall supervision
throughout the project. All authors reviewed and approved the ﬁnal version
of the manuscript.
Competing interests
The authors declare no competing interests.
Additional information
Supplementary information The online version contains
supplementary material available at
https://doi.org/10.1038/s42003-025-08706-4.
Correspondence and requests for materials should be addressed to
Matteo Ferrante, Tommaso Boccato, Nicola Toschi or Ruﬁn VanRullen.
Peer review information Communications Biology thanks Olaf Hauk and
the other, anonymous, reviewer(s) for their contribution to the peer review of
this work. Primary Handling Editor: Jasmine Pan. A peer review ﬁle is
available.
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
© The Author(s) 2025
https://doi.org/10.1038/s42003-025-08706-4
Article
Communications Biology |  (2025) 8:1263 
11


