# (2023) Better models of human high-level visual cortex emerge from natural language supervision with a large and diverse dataset

**Source:** (2023) Better models of human high-level visual cortex emerge from natural language supervision with a large and diverse dataset.pdf

---

## Page 1

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1415
nature machine intelligence
https://doi.org/10.1038/s42256-023-00753-y
Article
Better models of human high-level visual 
cortex emerge from natural language 
supervision with a large and diverse dataset
Aria Y. Wang1,2, Kendrick Kay3, Thomas Naselaris3,4, Michael J. Tarr 
  1,2,5 & 
Leila Wehbe 
  1,2,5 
High-performing neural networks for vision have dramatically advanced 
our ability to account for neural data in biological systems. Recently, further 
improvement in performance of these neural networks has been catalysed 
by joint training on images and natural language, increased dataset sizes 
and data diversity. We explored whether the same factors (joint training, 
dataset size and diversity) support similar improvements in the prediction 
of visual responses in the human brain. We used models pretrained with 
Contrastive Language-Image Pretraining (CLIP)—which learns image 
embeddings that best match text embeddings of image captions from 
diverse, large-scale datasets—to study visual representations. We built 
voxelwise encoding models based on CLIP image features to predict brain 
responses to real-world images. We found that ResNet50 with CLIP is a better 
model of high-level visual cortex, explaining up to R2 = 79% of variance in 
voxel responses in held-out test data, a substantial increase from models 
trained only with image/label pairs (ImageNet trained ResNet) or text 
(BERT). Comparisons across different model backbones ruled out network 
architecture as a factor in performance improvements. Comparisons across 
models that controlled for dataset size and data diversity demonstrated 
that language feedback along with large and diverse datasets are important 
factors in explaining neural responses in high-level visual brain regions. 
Visualizations of model embeddings and principal component analysis 
revealed that our models capture both global and fine-grained semantic 
dimensions represented within human visual cortex.
A long-term goal of visual neuroscience has been accounting for and 
elucidating the representations that bridge between visual inputs and 
our ability to understand, reason about and interact with the physical 
world around us. Until recently, models of visual perception were con-
structed according to pre-specified hypotheses and explained only a 
small portion of the variance outside the early visual cortex1. Advances 
in deep learning have led to a new generation of computational models 
of vision. Heretofore unaccounted for brain responses can now be pre-
dicted by deep neural networks that share task goals and learned repre-
sentations with natural systems1–3. However, this endeavour has been 
Received: 9 November 2022
Accepted: 3 October 2023
Published online: 13 November 2023
 Check for updates
1Neuroscience Institute, Carnegie Mellon University, Pittsburgh, PA, USA. 2Machine Learning Department, Carnegie Mellon University, Pittsburgh, PA, 
USA. 3Center for Magnetic Resonance Research (CMRR), Department of Radiology, University of Minnesota, Minneapolis, MN, USA. 4Department of 
Neuroscience, University of Minnesota, Minneapolis, MN, USA. 5Department of Psychology, Carnegie Mellon University, Pittsburgh, PA, USA.  
 e-mail: lwehbe@cmu.edu


## Page 2

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1416
Article
https://doi.org/10.1038/s42256-023-00753-y
To preview our findings, models using CLIP lead to encoding mod-
els that are much better at predicting high-level visual representations 
in the human brain as compared to single modality models that are 
pretrained with smaller and less diverse datasets. Controlled com-
parisons suggest that these improvements are not due to architectural 
differences and, beyond a certain training dataset size, are related to 
the diversity of the data, as well as the joint image/caption training 
that this data affords. Critically, when dataset factors are controlled, 
we still see improvement with language feedback. We are also able to 
predict visual brain responses using image captions alone—indicating 
that models using CLIP learn a robust latent space bridging natural 
language and vision. In this vein, we observed the greatest improve-
ments in prediction and were able to account for more of the unique 
variance in visual regions that process scenes of humans interacting 
with one another and their environment.
Results
Multimodal embeddings best predict high-level visual cortex
Our central question is whether incorporating joint natural language 
and image pretraining with large, diverse datasets leads to better mod-
els for understanding human high-level visual cortex. As a first step, we 
extracted representations from the last layer of the ResNetCLIP image 
encoder and ResNetImageNet—networks that have the same architecture 
but are trained with different objectives. In a later section we address 
the fact that they were also trained with datasets that differ in size and 
diversity.
We expect that images are represented differently by ResNetCLIP 
and ResNetImageNet, such that ResNetCLIP embeddings contain more 
semantic information and ResNetImageNet embeddings contain more 
visual information. In Fig. 1b, we show the pairwise similarity between 
embeddings of 10,000 randomly sampled stimulus images in both 
ResNetCLIP and ResNetImageNet. Image representations in the two model 
spaces are correlated. However, when zooming in to the ‘corner’ images 
in the similarity plot (Fig. 1b), images represented more similarly in 
ResNetCLIP, but not in ResNetImageNet, are semantically related, while 
those represented more similarly in ResNetImageNet are visually related. 
Within ResNetCLIP, images of people surfing and skateboarding, as well 
as images of giraffes and an elephant, are more similar. In contrast, 
within ResNetImageNet, images with different contexts are more similarly 
represented according to their visual similarity, for example, people 
wearing dark suits with a white shirt and a contrasting tie. These corner 
images indicate that ResNetCLIP captures contextual similarities that are 
not present in ResNetImageNet.
We used the image representations from ResNetCLIP image encoder 
and ResNetImageNet to predict fMRI voxelwise responses across the brain. 
In Fig. 1c we show the R2 performance in the held-out data across the 
whole brain. The overall level and the pattern of prediction perfor-
mance were both highly consistent across subjects S1–S8 (Fig. 1 for 
subject S5 and Supplementary Figs. 2 and 3 for subjects S1–S8). The 
encoding model built with the last layer of the ResNetCLIP visual encoder 
explains variance close to the voxel noise ceiling (see Supplementary 
Fig. 1 for performance measured in r). As a reference, earlier voxel-
wise encoding models for brain prediction report well below 0.7 in 
maximum correlation28,29, while in ref. 24, a brain optimized model of 
early visual cortex explains up to 0.8 in R2; similar to what we observe 
here in high-level visual cortex. However, directly comparing per-
formance across models is challenging in that different studies use 
distinct experimental designs and rely on different data processing 
pipelines. Studies that report performance as averages within region of 
interests (ROIs) or as representation similarity scores are also difficult 
to compare to our results.
Beyond overall performance metrics, peaks in the brain predic-
tion maps were aligned with common category-selective ROIs. Peaks 
within regions implicated as scene-selective30, body-selective31 and 
face-selective32,33 were sufficiently well defined so as to allow ROI 
limited by the fact that most models used for brain prediction learn a low 
dimensional task objective (for example, categorization) and are based 
on pretraining with ImageNet4. In contrast, natural vision solves multi-
ple tasks and has evolved over millions of years, incorporating diverse 
perceptual, conceptual and language sources5–8. A major challenge 
for understanding biological systems is to consider such multimodal 
sources in network training, for example, by including incorporating 
complex datasets that capture human-relevant information.
We have recently seen dramatic performance improvements in 
both vision and language tasks for state-of-the-art models. These 
advances may be attributed, in part, to learning more complex human 
semantics from multiple modalities that help delineate what is impor-
tant in training sets that are larger and more diverse than those used in 
earlier models9–13. Language is particularly effective in drawing atten-
tion to human semantics in training data in that language is generated 
by humans and has evolved to highlight aspects of the world that are 
behaviourally relevant14. At the same time, larger training set sizes 
provide more (and possibly better) examples for high-dimensional 
supervisory signals such as natural language15. Reinforcing the impor-
tance of these factors, we also see dramatic improvements in our ability 
to explain aspects of human vision using these same, state-of-the- 
art models.
We took models using Contrastive Language-Image Pretraining 
(CLIP)9 as representative of the class of models that leverage supervi-
sion from natural language (image captions) for vision and from vision 
(scene images) for language10–12,16. CLIP models are trained with image/
caption pairs, learning separate image and text encoders from scratch 
that encode each pair from the training data with similar representa-
tions at the final layer. As compared to previous multimodal models (for 
example, VisualBERT17 and LXMERT18), multimodal loss signals in the 
final layer are propagated through earlier layers of both the visual and 
language encoders. As compared to earlier models, model learning with 
CLIP may be more similar to human visual learning, where top-down 
knowledge influences the earliest layers of the visual pathway19,20. As 
such, CLIP is an attractive model for studying brain prediction along 
many dimensions. CLIP’s joint natural language and image pretraining 
and large, diverse training set better capture fine-grained human visual 
experience. Moreover, the versatile CLIP scheme allows us to explore 
the impact of different model architectures, while further controlled 
comparisons using related models and datasets likewise allow us to 
explore the impact of dataset size and diversity.
We extracted network representations from neural network 
models trained with CLIP, including ResNetCLIP and ViTCLIP and from 
several single modality models: ImageNet4 pretrained ResNet5021  
(ResNetImageNet) and BERT22 (associated captions). We then constructed 
voxelwise encoding models23 (Fig. 1a) to predict brain responses (func-
tional magnetic resonance imaging (fMRI)) arising from viewing images 
from the Natural Scenes Dataset (NSD)24. We found that brain predic-
tion performance was consistently higher for CLIP as compared to 
these other models.
A variety of factors characteristic of CLIP, and different from most 
prior models used for brain prediction, may be contributing to this 
superior prediction performance. However, as a proprietary model, we 
are unable to individually vary these factors. To explore these factors 
in a controlled manner, we selected several recent open source models 
that allow for more direct comparisons between four factors: architec-
ture, feedback, dataset size and data diversity. Our extended analyses 
included a self-supervised model, simCLR25, a self-supervised model 
that included language feedback, SLIP16 and several open versions of 
CLIP26. These models were trained with datasets that included 15 mil-
lion (YFCC27), 400 million (as in the original CLIP model) or 2 billion 
examples from LAION26. We constructed encoding models with these 
networks to explain responses from NSD, which allowed us to more 
precisely evaluate and quantify the contributions of architecture, 
pretraining, dataset size and data diversity.


## Page 3

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1417
Article
https://doi.org/10.1038/s42256-023-00753-y
localization based solely on the prediction performance of ResNetCLIP. 
We speculate that these alignments reflect the importance of semantic 
associations in scene understanding and person recognition.
To rule out performance improvements based on specific network 
architectures, we extracted features from two backbones pretrained 
with CLIP: visual transformer (ViT-32) and ResNet50. Differences in pre-
diction performance were small (Supplementary Fig. 6), indicating that 
the observed improvement was not due to any particular neural-net 
architecture.
To explore whether the captions associated with images could 
predict the brain activity for viewing the corresponding image, rep-
resentations extracted from the last layer of the CLIP text encoder 
were also used to predict voxelwise responses across the brain. In the 
absence of image information, we were able to predict responses in 
SimCLIP
SimImageNet
“A living room scene with a laptop
and a television.”
 
“A person eating with chopsticks and
reading books in their living room”
 
“A few graphic novels and a laptop
on a couch in front of a tv”
 
fMRI
Image
encoder
Text
encoder
Optimized
to be similar
during training
Predict
Predict
a
b
c
Prediction performance (R2)
(All coloured voxels P < 0.05, FDR corrected)
NS
0
Predict
Image
encoder
–0.2
0
0.2
0.4
0.6
0.8
1.0
0.2
0.4
0.6
0.8
1.0
0
0
0.2
0.4
0.6
0
0.2
0.4
0.6
0.8
1.0
Noise ceiling
85% noise ceiling
0.2
0.4
0.6
0.8
1.0
10
0
10
1
10
2
10
3
Noise ceiling
Model performance (R2)
Fig. 1 | Model pipeline, motivation and prediction performance for the 
ResNetCLIP visual encoder. a, Last-layer representations from the CLIP image and 
text encoders are extracted from images and captions and used in voxelwise 
encoding models to predict brain responses to each image. b, Similarities of pairs 
of images when using embeddings from ResNetCLIP and ResNetImageNet are 
compared. For each pair of 10,000 randomly sampled images, a similarity score 
was computed (measured in correlation) between the representations of these 
two images extracted from ResNetCLIP and ResNetImageNet (that is Sim
CLIP
i, j  and 
Sim
ImageNet
i, j
). The position of each dot in the scatter plot is determined by 
similarity scores for the same pair of images in ResNetCLIP and ResNetImageNet model 
spaces. Pairs of images in the bottom-right corner are those most similar in 
ResNetCLIP and most dissimilar in ResNetImageNet; for example, images of people 
surfing and skateboarding and images of giraffes and an elephant. In contrast, 
pairs of images in the top left corner are those most similar in ResNetImageNet and 
least similar in ResNetCLIP; for example, visually similar pictures of people wearing 
dark suits with a white shirt and a contrasting tie. c, Voxelwise prediction 
performance (measured in R2) on a held-out test set is shown for subject S5 in a 
flattened view of the brain with overlays for functionally defined, category-
selective ROIs (top), as well as in lateral, posterior and bottom views (bottom row, 
left-to-right). Two-dimensional histogram of model performance in R2 against 
noise ceiling and 85% noise ceiling across all voxels in the whole brain (bottom-
right). Density of voxels are shown in a log scale. Most voxels are predicted close 
to its noise ceiling and some are above the 85% noise ceiling. For visualization 
purpose, we only plot in the brain maps the voxels that are predicted significantly 
higher than chance (P < 0.05, FDR-corrected59, one-sided test).


## Page 4

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1418
Article
https://doi.org/10.1038/s42256-023-00753-y
high-level visual cortex comparable to predictions from the ResNetCLIP 
image encoder (Fig. 2). From this result, we infer that pretraining with 
CLIP enables learning a meaningful latent space that bridges between 
vision and natural language as is represented in the brain. At the same 
time, the text encoder explained less unique variance than the CLIP 
visual encoder, especially in the early visual cortex, suggesting that 
this is not a general effect (Supplementary Fig. 7).
Visual CLIP embeddings explain more unique variance
To assess the impact of joint natural language and image pretrain-
ing with large, diverse datasets, we compared the unique variance 
accounted for by the last layer of the ResNetCLIP image encoder to the 
last layer of ResNetImageNet (with the same ResNet50 architecture).
A variance partitioning analysis34,35 (Fig. 3) revealed that 
ResNetCLIP accounts for the majority of the unique variance in high- 
level visual cortex, particularly in ROIs implicated in scene and per-
son perception. With the exception of early visual areas (for exam-
ple, V1v and h4v), the last layer of ResNetCLIP accounts for more 
of the unique variance for the majority of voxels in high-level ROIs 
(Fig. 3b). Beyond category-selective ROIs that respond to faces, 
places and bodies, two areas, TPOJ and angular gyrus (AG), associated 
with theory of mind and language36, were likewise better explained 
by ResNetCLIP.
The last layer of ResNetCLIP explained less variance in early visual 
cortex as compared to ResNetImageNet; however, this does not imply 
that ResNetCLIP failed to capture information represented in these 
regions. The last layer of ResNetCLIP is the bottleneck layer that encodes 
image embeddings optimized to match in similarity with text embed-
dings. The entire visual pathway is best predicted by a progression of 
ResNetCLIP layers (including below the bottleneck layer; Supplemen-
tary Fig. 8). More generally, ResNetCLIP is the best predictive model 
for visual cortex.
ResNetCLIP boosts regions encoding human/scene interactions
To explore the semantic dimensions learned in the encoding model 
built with CLIP, we performed principal component analysis (PCA) on 
the learned encoding model weight matrix concatenated across the 
20,000 top predicted voxels from each of the eight subjects in NSD. 
We projected the concatenated voxels onto the principal component 
(PC) dimensions to understand the tuning of the entire voxel space, 
Prediction performance (R2)
(All coloured voxels P < 0.05, FDR corrected)
NS
0
0.2
0.4
0.6
Predict
“A living room scene with a
laptop and a television.”
“A person eating with
chopsticks and reading
books in their living room”
Text
encoder
Fig. 2 | Prediction performance for the CLIP text encoder. Prediction 
performance for voxelwise responses (in R2) in held-out data for the CLIP text 
encoding model for subject S5 with overlays for functionally defined, category-
selective ROIs. The brain maps show the voxels that are predicted significantly 
higher than chance (P < 0.05, FDR-corrected59, one-sided test). Captions of 
the images viewed in the scanner were provided to the text encoder and the 
representation was then used to make voxelwise brain predictions. Despite only 
having access to the captions of the images that the subjects viewed, the CLIP text 
encoder was still able to predict fMRI data in many functionally defined ROIs (for 
example, EBA, PPA, RSC and FFA). The similarity in brain prediction for the image 
and text encoders reinforces the hypothesis that the information encoded in 
high-level visual areas is anchored in semantics.


## Page 5

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1419
Article
https://doi.org/10.1038/s42256-023-00753-y
following previous works29,37. Visualizing each PC of the learned model 
and its corresponding voxel projection revealed the dimensions that 
underlie semantic organization in the brain. To interpret different PCs, 
we visualized the images that lie closest to a given PC in the model space 
for the top five PCs (which account for most of the explained variance; 
Supplementary Figs. 10 and 11).
a
b
0.10
0.02 ResNetImageNet
ResNetCLIP
ResNetImageNet
ResNetCLIP
0.10
(All coloured
voxels P < 0.05,
FDR corrected)
c
–0.1
0
0.1
0.2
–0.1
0
0.1
0.2
0.3
0.4
10
0
10
1
10
2
10
3
10
4
10
0
10
1
10
2
10
3
10
4
–0.1
0
0.1
0.2
0.3
0.4
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
–0.1
0
0.1
0.2
0.3
–0.1
0
0.1
0.2
0.3
V1v
RSC
OPA
FFA-1
TPOJ1
TPOJ3
h4v
PPA
EBA
FFA-2
TPOJ2
AG
–0.1
0
0.1
0.2
–0.1
0
0.1
Unique var. of ResNetImageNet
ResNetImageNet
Unique variance
Model performance (R2)
ResNetImageNet
Unique variance of ResNetCLIP
ResNetCLIP
ResNetCLIP
0.2
–0.1
0
0.1
0.2
–0.1
0
0.1
0.2
–0.1
0
0.1
0.2
Fig. 3 | Performance for the CLIP visual encoder using a ResNet backbone as 
compared to ResNetImageNet. a, Two-dimensional distribution plots of voxels from 
the whole brain for subject S5 in model performance (in R2) and unique variance 
comparison between ResNetCLIP and ResNetImageNet. The red lines indicates equal 
performance for the two models. ResNetCLIP predicts much better in terms of total 
variance and unique variance. b, Unique variance accounted for by ResNetCLIP as 
compared to ResNetImageNet for 12 different ROIs for all eight subjects. Individual 
voxels are plotted as blue points. The red lines indicate iso-variance, that is, 
(y = x). ResNetCLIP accounts for overwhelmingly more variance than ResNetImageNet 
in high-level visual cortex. In contrast, ResNetImageNet only accounts for more 
variance in ventral V1 and a reasonable proportion of the variance in ventral V4. 
c, Unique variance accounted for by ResNetCLIP as compared to ResNetImageNet 
for subject S5—obtained by subtracting R2 for each model from that of the joint 
model (with concatenated feature spaces). Voxels where ResNetCLIP accounts 
for greater unique variance are orange and voxels where ResNetImageNet accounts 
for greater unique variance are blue. Only voxels with significantly higher than 
chance unique variance are plotted for both models (P < 0.05, FDR-corrected, 
one-sided test).


## Page 6

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1420
Article
https://doi.org/10.1038/s42256-023-00753-y
Through PC visualization, we found that PC1 separates animate 
and inanimate images and its brain projections correspond to body 
and face regions (Fig. 4d). PC2 separates scene and food images. When 
we split the functional areas identified from PC1 with PC2; its brain 
projections corresponded to place regions and the food region (Sup-
plementary Fig. 12)38–40. We obtained interpretable PC dimensions 
up to PC10 (despite the relatively low explained variance from PC6 
onwards), allowing us to identify fined-grained semantic distinctions 
(Supplementary Fig. 11).
Comparing the brain projection for PC1 and the unique variance 
map for ResNetCLIP we found that voxels that have large negative values 
on PC1 overlap with voxels where ResNetCLIP explains the most unique 
variance (Fig. 4a,b). These voxels clustered in ventral EBA, FFA-1 and 
FFA-2, as well as ventral RSC. The more negatively a voxel lies along 
PC1, the more unique variance that can be explained by ResNetCLIP for 
this voxel (Fig. 4c).
The projected images can be used to interpret which images had 
the largest benefit in brain prediction using ResNetCLIP. The images 
lying on the negative side of PC1 are people participating in sports 
(Fig. 4d). This separation is consistent with the best predicted voxels 
from ResNetCLIP being centred on the body area. Further validating this 
finding, images that lie on the negative end of the PC1 contain more 
people, animals and sports items (based on the known category and 
super-category labels of COCO images; Fig. 4d). These observations 
suggest that the representation of people in ResNetCLIP is the domain 
for which the model provided the most leverage for predicting brain 
responses. More generally, ResNetCLIP is more effective at capturing 
scene semantics as compared to models trained with image/label pairs.
+
–
PC projection
Unique variance (R2)
a
b
c
d
e
(All coloured voxels P < 0.05, FDR corrected)
–0.4
–0.2
0
0.2
0.4
0
0.05
0.10
0.15
0.20
0.25
0.30
–1.00
–0.05
0
0.05
0.10
0.15
0.20
0.25
0.30
0.35
–0.75
–0.50
–0.25
0
Projection onto first PC
COCO super categories
Unique variance of CLIP
Proportions
0.25
0.50
0.75
1.00
Person
Vehicle
Outdoor
Animal
Accessory
Sports
Kitchen
+
–
Food
Furtniture
Electronics
Appliance
Indoor
0
0.05
0.10
0.15
0.20
0.25
0.30
Fig. 4 | Better representations of scenes with people in a model trained  
with CLIP can account for gains in unique variance. a, Unique variance 
explained by ResNetCLIP plotted on a flatmap from subject S5. b, Projection of 
voxels onto PC1 of ResNetCLIP for subject S5. The voxels that are best explained 
by ResNetCLIP overlap largely with the voxels that lie on positive side when 
projected onto the 1st PC. c, A voxelwise scatter plot illustrating that, for voxels 
lying on the negative side of the 1st PC projection, the further down on the 
projection that the voxel lies, the better it is explained by ResNetCLIP. Note that 
the sign of the PC is arbitrary and can be flipped; we use ‘negative’ here to refer 
to one of the sides of PC1. d, Images are grouped into ‘+’ and ‘−’ depending on 
which side of the PC the image lies on when projected onto the PC1. The top 10 
images that best align with either end of PC1 are shown in the yellow and green 
boxes respectively. For the positive projection we observe images of inanimate 
indoor scenes, whereas for the negative projection we observe images of 
people participating in animate outdoor sports. e, Category distribution  
of the two image groups validates the observation that images on the negative 
side, relative to images on the positive side, consist more of people, animals 
and sports.


## Page 7

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1421
Article
https://doi.org/10.1038/s42256-023-00753-y
Disentangling language feedback from other model attributes
Beyond natural language supervision, CLIP training uses larger train-
ing datasets and may have greater diversity as compared to earlier 
models— factors that may also contribute to CLIP’s effectiveness in 
brain prediction. To assess the contributions of these factors for predic-
tion, we include three variance partitioning analyses using additional 
Model
Dataset
Dataset size
Feedback
ResNet ImageNet
ImageNet
1.5 million
Categories
OpenAI CLIP
–
400 million
Lang
YFCC simCLR
YFCC
15 million
SSL
YFCC SLIP
YFCC
15 million
SSL + Lang
YFCC CLIP
YFCC
15 million
Lang
LAION 400M CLIP
LAION
400 million
Lang
LAION 2B CLIP
LAION
2 billion
Lang
Lang
SSL
YFCC SLIP versus YFCC simCLR
15 million (SSL + Lang)
15 million SSL
LAION 2B versus LAION 400M
2 billion Lang 400 million Lang
OpenAI CLIP versus LAION 400M
400 million Lang
400 million Lang
Varying data distribution only
Varying dataset size only
Varying language feedback only
b
a
d
e
c
EBA voxels
EBA voxels
EBA voxels
S5
S2
S1
S7
0.05
0
0.05
EarlyVis
0.08
Mean performance (R2)
0.10
0.12
0.14
0.16
0.18
0.20
1 million
15 million
400 million
2 billion
Model type
Dataset size
Categories
Lang (YFCC)
SSL
SSL + Lang (YFCC)
Lang (Laion)
Lang (OpenAI)
Scene
Body
Regions
Face
TPOJ
–0.04
–0.05
0
0.05
YFCC SLIP
YFCC simCLR
LAION 400M CLIP
LAION 400M CLIP
LAION 2B CLIP
OpenAI CLIP
0.10
10
0
10
1
10
0
10
1
10
0
10
1
–0.05
0
0.05
0.10
–0.05
0
0.05
0.10
–0.02
0
0.02
0.04
0.06
0.08
0.10
–0.04
–0.02
0
0.02
0.04
0.06
0.08
0.10
–0.04
–0.02
0
0.02
0.04
0.06
0.08
0.10
Fig. 5 | Variance partitioning analyses controlling for model architecture, 
data distribution and dataset size indicate that dataset size and diversity 
have comparatively smaller effects on voxel prediction than language 
input. a, The models we consider with their relevant characteristics. b, Brain 
prediction performance averaged across all voxels in a given brain region for 
each model + dataset combination (SSL denotes self-supervised learning; Lang 
denotes natural language feedback for a given model). Each point is a region’s 
average performance across eight subjects; error bars indicate standard error 
across eight subjects. When looking at average brain prediction performance 
with an ROI, all three CLIP pretrained models and the SSL model perform 
substantially better than ImageNet trained ResNet50, while differences between 
all three CLIP models and the SSL model are relatively small. c–e, Cortical 
flatmaps showing the fine-grained, spatial distribution of unique variance for 
model comparisons varying a single factor while controlling for the others. 
Each unique variance comparison is thresholded by statistical significance 
(P < 0.05, FDR-corrected59). For each comparison, the first row shows brain maps 
from subject S5, while the second row shows unique variance brain maps from 
subjects S1, S2 and S7, respectively. The third row of each comparison shows a 
two-dimensional histogram of unique variance for individual voxels in EBA for all 
eight subjects. The red line indicates identical unique variance (y = x). Notably, 
as shown in c, when the same dataset is used for training across models, SLIP, 
a model that includes language feedback, accounts for more unique variance 
in high-level brain areas such as EBA and some parts of FFA, relative to simCLR, 
an otherwise identical model that does not include language feedback. Beyond 
language feedback, as shown in e, a good data distribution appears to also 
account for unique variance in some high-level visual areas, while, as shown in 
d, dataset size per se appears to account for very small improvements in unique 
variance past a certain size.


## Page 8

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1422
Article
https://doi.org/10.1038/s42256-023-00753-y
models as listed with their relevant characteristics in Fig. 5a. These 
models allowed us to use the publicly available YFCC (Yahoo Flickr 
Creative Commons)27 and LAION26 datasets to control for dataset size 
and diversity. Both the YFCC and LAION datasets provide sufficient 
multimodal data to retrain CLIP with different and better controlled 
dataset parameters.
We visualized averaged model performance across all models in 
Fig. 5b for several well-characterized ROIs within each general anatomi-
cal and semantic categories (EarlyVis: early visual cortex, V1v: ventral 
primary visual cortex, h4v: ; Scene, PPA: parahippocampal place area, 
OPA: occipital place area, RSC: retrosplenial cortex; Body, EBA: extras-
triate body area; Face, FFA-1: fusiform face area 1, FFA-2: fusiform face 
area 2; TPOJ: temporoparietal junction, TPOJ-1: temporoparietal junc-
tion 1, TPOJ-2: temporoparietal junction 2). Each point in the figure is 
a region’s average performance across eight subjects. All CLIP models 
and the SSL models explained brain responses in high-level visual cor-
tex substantially better than ResNetImageNet, while differences among SSL 
and CLIP are small. Note that these summary results describe average 
responses across all voxels in a given ROI, and therefore they do not 
reflect spatial patterns of unique variance within an ROI. Critically, ROI 
average analyses—particularly for ROIs containing large numbers of 
voxels—may mask meaningful spatial prediction patterns. For example, 
in work similar to ours, model comparisons that appear similar on aver-
age may actually carry fine-grained spatial information41.
To understand how model feedback, dataset size and diversity 
affect predictions for individual voxels, we present cortical maps of 
the unique variance for three voxelwise analyses (Fig. 5c–e). Encod-
ing models were used to predict individual voxel responses and the 
voxelwise unique variance explained by each model was computed. 
We compared the effect of language feedback when controlling for the 
dataset parameters of distribution and size; the effect of dataset size 
when controlling for the data distribution, feedback type and model 
architecture; and the effect of data distribution when controlling 
for feedback type, dataset size and model architecture. These three 
comparisons vary along single dimensions and, thus, are maximally 
informative in terms of isolating factors with respect to their impact 
on brain prediction performance. Other comparisons between these 
models would vary along more than one dimension, thereby confound-
ing which factors were contributing to any observed effect.
We evaluated the effect of language feedback while controlling for 
dataset size and data distribution by comparing the last layer of simCLR 
and SLIP (which combines simCLR and CLIP losses) trained on 15 million 
YFCC photo/caption pairs. We found more unique variance explained 
by SLIP in EBA, FFA and adjacent to the boundary of RSC, while simCLR 
showed more unique variance explained in early visual cortex and 
posterior EBA (Fig. 5c). The histogram of unique variance across all 
EBA voxels for all subjects revealed a bimodal distribution of voxels 
preferring one model or the other, with more voxels skewing towards 
YFCC SLIP. Flatmaps of significant unique variance explained by SLIP 
showed consistent patterns across subjects in Montreal Neurological 
Institute (MNI) space (Supplementary Fig. 13). These visualizations 
suggest that interpreting brain prediction across models requires 
analysis at the voxel, rather than the ROI, level.
We evaluated the effect of dataset size while controlling for data 
distribution by comparing CLIP models trained on 400 million or 
2 billion image/caption pairs from LAION26. The representations aris-
ing from the larger dataset explained more unique variance than those 
arising from the smaller dataset in EBA, FFA and areas outside of RSC 
(Fig. 5d). However, the improvement in prediction performance due 
to dataset size was small. The histogram of EBA voxels revealed that 
dataset size, after reaching a critical level for model training, did not 
seem to be a major factor in improved brain prediction with CLIP.
We evaluated the effect of data distribution while controlling both 
feedback type and dataset size by comparing CLIP models trained on 
400 million image/caption pairs from OpenAI9 and from LAION26. The 
representations using OpenAI’s dataset explained more unique vari-
ance than those using LAION’s dataset in regions including the EBA, FFA 
and areas outside of RSC (Fig. 5e). This aligns with the argument that 
data diversity in the training dataset contributes substantially to the 
robustness of the OpenAI CLIP model15. The histogram of EBA voxels 
revealed that differences arising from data distribution are larger than 
those arising from dataset size, indicating that data diversity is a likely 
factor in improved brain prediction with OpenAI CLIP.
Discussion
Do higher performing models using natural language feedback together 
with larger, more diverse training sets also better predict brain response 
to complex, real-world scenes? We evaluated and quantified the contri-
butions of large-scale, diverse multimodal pretraining as provided by 
CLIP for generating semantically grounded representations of natural 
scenes. These models are extraordinarily good at predicting voxelwise 
responses to viewing scenes in the NSD24. A recent study confirms our 
results, finding that models with CLIP pretraining better predicted 
responses in NSD as compared to other models41–43.
While it is appealing to attribute the improved prediction perfor-
mance of CLIP to language feedback during training, it is important 
to disentangle several other factors that may contribute to the high 
level of brain prediction performance. CLIP models, as compared to 
prior models used for brain prediction1,28, can have different model 
architectures and are pretrained with many more examples. Conse-
quently, model architecture, multimodal pretraining, dataset size and 
data diversity (or some combination therein) are all characteristics of 
CLIP that may underlie improved brain prediction.
First, we found that model architecture, as realized in different 
visual backbones, had little impact on prediction performance (see 
also refs. 41–43). Second, to better isolate the potential contribu-
tions of other factors, we examined prediction performance for pairs 
of open CLIP models that differ from one another along only single 
dimensions. We found that: models trained with natural language 
feedback show a consistent advantage in prediction performance in 
high-level brain regions, especially the EBA and TPOJ; the diversity 
and quantity of the training data may set a ceiling for improvements in 
prediction arising from adding language feedback; the size of the train-
ing dataset for the CLIP model appears to be both less consequential 
for improved prediction performance and shows diminishing returns 
as compared to other data characteristics (that is, data diversity). We 
conclude that models trained with natural language feedback, together 
with sufficient data diversity and dataset size, are attractive candi-
date models for understanding representation in high-level human 
visual cortex.
More broadly, rather than simply quantifying overall brain predic-
tion performance across a range of models, we selected models with 
characteristics that reflect human-like training and experience in the 
form of natural language feedback and larger, more diverse datasets. 
In addition to ROI-level analyses, we also provided finer-grained analy-
ses that shed light on how language training in tandem with a diverse 
dataset facilitates learning brain-like representations. Visualizations 
of ResNetCLIP and unimodal network representations revealed that 
ResNetCLIP better captured semantic information—consistent with 
natural language feedback being an important factor in improved pre-
diction performance, as well as this improvement being associated with 
better prediction of high-level visual cortex. PCA analyses built on these 
results, revealed that, within ResNetCLIP, the fine-grained representation 
of scenes depicting human interactions lead to the largest gains in brain 
prediction—particularly in EBA. We suggest that ResNetCLIP captures 
information about humans interacting with the world around them, 
and, as such, is predictive of similar representations in high-level brain 
regions44. One potential limitation to this conclusion is that, despite 
the semantic diversity of CLIP-trained models, NSD is not particularly 
diverse, providing less than 100 category labels (albeit embedded in 


## Page 9

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1423
Article
https://doi.org/10.1038/s42256-023-00753-y
complex, natural scenes). As such, some of our interpretations may 
be biased by the content of NSD. Future studies should consider using 
semantically broader datasets45,46.
Our results support the theory that, beyond object identity, human 
high-level visual representations reflect semantics and the relational 
structure of the visual world; for example, non-perceptual associations 
such as function or meaning6,44,47. An embedding model based on text 
captions for viewed images also concluded that high-level visual cortex 
represents semantic information related to those images48. Similarly, 
a study combining a deep neural network for vision with an attractor 
network of semantics was able to account for patterns of activation 
in high-level visual cortex49. Indeed, there is evidence that, along with 
playing a role in the acquisition of semantics50,51, language influences 
the acquisition of visual categories during development, where visual 
learning occurs concurrently with language and conceptual learn-
ing51–53. Our present study reinforces these findings, suggesting that 
language and semantics strongly influence the high-level organization 
of visual information encoded in the human brain.
What it is about models incorporating natural language training 
together with large, diverse datasets that enables them to excel not 
just at visual tasks such as zero-shot learning, but also at brain predic-
tion? In our view, the same natural language feedback, in tandem with 
data diversity and dataset size, underlies higher performance in both 
domains—an example of the principle whereby higher performing mod-
els also perform better at brain prediction2. However, while dataset size 
may be a contributing factor to higher performance, beyond a certain 
size, its impact on brain prediction may be diminished except to the 
extent that size contributes to diversity. Our intuition is that re-training 
ResNet with a much bigger dataset, but continuing to include only 
category labels, would produce a model that would be unlikely to 
learn fine-grained representations of complex scenes. Such nuanced 
information regarding human interactions in real-world scenes is not 
carried by category labels: while some labels do contain semantic 
information beyond the category (for example, ‘party’), language 
feedback provides context and a broader understanding, for example, 
the semantic relationships between actors and objects in real-world 
scenes. Supporting this point, given equivalent training data, models 
with natural language feedback outperformed self-supervised and 
unimodal models in high-level visual areas. Thus, the natural language 
feedback present in models pretrained with CLIP appears crucial to 
their excellent performance in tasks related to both machine and bio-
logical intelligence.
In sum, the impressive ability of vision models incorporating 
natural language supervision along with large, diverse datasets for 
predicting brain responses opens new possibilities for developing a 
deeper understanding of the functional architecture of the human 
brain. Exploring the implications of this finding will require new ways 
of thinking about both artificial and natural systems. Future large-scale 
efforts should incorporate stimuli, tasks, representations, models and 
datasets that reflect the natural complexity of how we interact with the 
world around us.
Methods
Datasets
fMRI data. Brain recordings were obtained from NSD24, an open dataset 
of 7T whole brain high-resolution fMRI responses from eight subjects 
(S1–S8) who each viewed ~10,000 unique images of natural scenes, each 
image repeated three times. These scene images were a subset of the 
images in the annotated Microsoft Common Objects in Context (COCO) 
dataset54. Of the 70,566 total images presented across subjects, ~1,000 
images were viewed by all subjects. fMRI data were collected during 
30–40 scan sessions. Stimulus images were square cropped, presented 
for 3 s at a size of 8.4∘ × 8.4∘ with 1 s gaps in between image presentations. 
Subjects were instructed to fixate on a central point and to press a but-
ton after each image if they had seen that image previously.
The fMRI data were acquired at 7T using whole-brain gradient-echo 
EPI at 1.8 mm resolution and 1.6 s repetition time. Preprocessing 
steps included a temporal interpolation (correcting for slice time 
differences) and a spatial interpolation (correcting for head motion). 
Single-trial beta weights were estimated with a general linear model. 
In this paper we used the betas_fithrf_GLMdenoise_RR preparation 
of the betas. FreeSurfer55,56 was used to generate cortical surface 
reconstructions to which the beta weights were mapped. The beta 
weights were z-scored across run and were averaged across repeti-
tions of the image (up to three repetitions of each image), resulting 
in one averaged fMRI response to each image per voxel, in each 
subject. NSD also includes several visual ROIs that were identified 
using separate functional localization experiments. We drew the 
boundaries of those ROIs for each subject on their native surface 
for better visualization and interpretation of the results (for exam-
ple, Fig. 1). All brain visualizations were produced using Pycortex 
software57.
Natural scene images. All stimulus images used in NSD and in our 
experiments were drawn from the COCO dataset54. COCO is unique 
among large-scale image datasets in that COCO images contain con-
textual relationships and non-iconic (or non-canonical) object views. 
In comparison to ImageNet4, COCO contains fewer labelled categories 
(91), but includes more examples for each category (>5,000 for 82 
of the categories). Note, however, that many labelled categories in 
ImageNet are at the subordinate level—COCO likely contains at least 
as many unlabelled subordinate categories. The complete set of COCO 
images and additional details can be found on the COCO website: 
https://cocodataset.org.
Model details and feature extraction
Models used in the analysis include: (1) OpenAI trained CLIP (with ViT-
32 transformer and ResNet50 backbones); (2) YFCC trained SLIP, CLIP 
and simCLR; (3) Open CLIP models trained on LAION 400M and LAION 
2B; (4) ImageNet pretrained ResNet50. YFCC is a 100 million example 
dataset comprised of multimedia ‘objects’ which includes 15 million 
photos with captions selected from Flickr27, while LAION is a large-scale 
dataset that contains 5.85 billion multilingual CLIP-filtered image-text 
pairs26. All NSD stimulus images were input into the these models.
For model comparison, we use the output of the ‘image encoder’ in 
CLIP models and the second to the last layer in ImageNet trained models 
as feature spaces for the encoding models. The feature dimensions 
for each of the model feature spaces are as follows: ImageNet trained 
ResNet50, 2048; OpenAI CLIP with ViT-32 backbone, 512; OpenAI CLIP 
with ResNet50 backbone, 1024; YFCC simCLR, 768; YFCC SLIP, 512; 
YFCC CLIP, 512; LAION 400M CLIP, 512; LAION 2B CLIP, 512.
For image captions, we use the human generated captions for each 
of the NSD images provided by the COCO dataset and input them into 
both BERT and CLIP-based models’ text encoders for their layerwise 
activations. On average, COCO provides five to six captions for each 
image. Caption embeddings for a image are extracted individually and 
the average is used in the encoding models.
Voxelwise encoding models
We built a ridge regression model (implemented in PyTorch; see ref. 58) 
to predict one averaged fMRI response to each image per voxel, in each 
subject. We chose to use a ridge regression model instead of more 
complicated models to retain the interpretability of model weights, 
which may provide insights into the underlying dimensions of the brain 
responses. We randomly split the total number of images a subject 
sees into a training and test set with a 4-to-1 ratio. For each subject, 
each voxel’s regularization parameter was chosen independently via 
7-fold cross-validation across the training set. We swept through 100 
regularization parameters spaced evenly on a log scale from 10−8 to 
1010, that is np.logspace(-8, 10, 100). Cross-validation was handled by 


## Page 10

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1424
Article
https://doi.org/10.1038/s42256-023-00753-y
sklearn.model_selection.KFold, where data are split into consecutive 
folds without shuffling. Each fold is used once as validation while the 
rest of the set are used for training. Model performance was evaluated 
on the test data using both Pearson’s correlation and the coefficient 
of determination (R2). To determine the significance of the predic-
tions, we perform a bootstrap test where we resample the test set with 
replacement for 2,000 times and compute the FDR-corrected P-value 
threshold for various performance statistics59.
Variance partitioning
To obtain unique variance by two models A and B, we first create a joint 
model of A and B by concatenating features from these two models. 
We then fit the voxelwise ridge regression model to the joint model and 
obtain R2
A&B. The variance explained by individual model A and B are 
denoted as R2
A and R2
B, respectively. We then calculated the unique vari-
ance for model A and B, where R2
A = R2
A&B −R2
B, R2
B = R2
A&B −R2
A.
PCA analysis
To recover the semantic basis of the learned encoding model we per-
formed PCA on the learned weight matrix concatenated across the 
20,000 top predicted voxels from each of the eight subjects in NSD. 
These voxels were selected based on the noise corrected model per-
formance of ResNetCLIP. We then concatenated the weight matrices 
(used in the encoding model with ResNetCLIP) corresponding to these 
voxels from all eight subjects along the voxel dimension. We then 
centred the matrix, performed PCA, and obtained the first 20 principal 
components (PCs). As in prior work29,37, we projected the concatenated 
voxels onto the PC dimensions to understand the tuning of the entire 
voxel space. Explained variance by these PCs are plotted in Supple-
mentary Fig. 10.
Statistics and reproducibility. Statistical analyses were performed 
using Python and data visualizations were accomplished using Pycor-
tex57. Significant voxels from encoding models were identified by com-
puting the P value from each R2 and corrected for multiple comparisons 
using the Benjamini–Hochberg false discovery rate procedure (FDR)59 
and α = 0.05.
Data availability
We use the Natural Scenes Dataset (NSD), a large-scale fMRI dataset of 
participants viewing thousands of natural images. The NSD was made 
available by ref. 24.
Code availability
Our code is available as a public Github repository https://github.com/
ariaaay/clip2brain.git (ref. 60).
References
1.	
Yamins, D. L. K. et al. Performance-optimized hierarchical models 
predict neural responses in higher visual cortex. Proc. Natl Acad. 
Sci. USA 111, 8619–8624 (2014).
2.	
Yamins, D. L. K. & DiCarlo, J. J. Using goal-driven deep learning 
models to understand sensory cortex. Nat. Neurosci. 19,  
356–365 (2016).
3.	
Toneva, M., Mitchell, T. M. & Wehbe, L. Combining computational 
controls with natural text reveals aspects of meaning 
composition. Nat. Comput. Sci. 2, 745–757 (2022).
4.	
Deng, J. et al. ImageNet: a large-scale hierarchical image 
database. In IEEE Conference on Computer Vision and Pattern 
Recognition 248–255 (IEEE, 2009).
5.	
Aminoff, E. M. & Tarr, M. J. Associative processing is inherent in 
scene perception. PLoS ONE 10, e0128840 (2015).
6.	
Gauthier, I., James, T. W., Curby, K. M. & Tarr, M. J. The influence 
of conceptual knowledge on visual discrimination. Cogn 
Neuropsychol. 20, 507–523 (2003).
7.	
Schaffner, J., Bao, S. D., Tobler, P. N., Hare, T. A. & Polania, R. 
Sensory perception relies on fitness-maximizing codes. Nat. Hum. 
Behav. 7, 1135–1151 (2023).
8.	
Lupyan, G., Thompson-Schill, S. L. & Swingley, D. Conceptual 
penetration of visual processing. Psychol. Sci. 21, 682–691 
(2010).
9.	
Radford, A. et al. Learning transferable visual models from natural 
language supervision. In International Conference on Machine 
Learning (eds. Meila, M. & Zhang, T.) 8748–8763 (PMLR, 2021).
10.	 Li, L. H. et al. Grounded language-image pre-training. In IEEE/CVF 
Conference on Computer Vision and Pattern Recognition  
10955–10965 (IEEE, 2022).
11.	
Yuan, L. et al. Florence: a new foundation model for computer 
vision. Preprint at https://doi.org/10.48550/arxiv.2111.11432 
(2021).
12.	 Jia, C. et al. Scaling up visual and vision-language representation 
learning with noisy text supervision. In International Conference 
on Machine Learning (eds. Meila, M. & Zhang, T.) 4904–4916 
(PMLR, 2021).
13.	 Wu dao 2.0. https://gpt3demo.com/apps/wu-dao-20 (accessed 
20 October 2022).
14.	 Pinker, S.The language Instinct: How the Mind Creates Language 
(HarperCollins, 2007).
15.	 Fang, A. et al. Data determines distributional robustness in 
contrastive language image pre-training (CLIP). In Proceedings of 
international Conference on Machine Learning (eds. Chaudhuri, K. 
et al.) 6216–6234 (PMLR, 2022).
16.	 Mu, N., Kirillov, A., Wagner, D. & Xie, S. SLIP: self-supervision 
meets language-image pre-training. In Proceedings 17th European 
Conference on Computer Vision (eds. Avidan, S. & Brostow, G.) 
529–544 (Springer Nature, 2022).
17.	 Li, L. H., Yatskar, M., Yin, D., Hsieh, C.-J. & Chang, K.-W. VisualBERT: 
a simple and performant baseline for vision and language. 
Preprint at https://doi.org/10.48550/arXiv.1908.03557 (2019).
18.	 Tan, H. & Bansal, M. LXMERT: learning cross-modality encoder 
representations from transformers. In Conference on Emperical 
Natural Language Processing (eds Inui, K. et al.) 5099–5110 
(Association for Computational Linguistics, 2019).
19.	 Murray, S. O., Boyaci, H. & Kersten, D. The representation of 
perceived angular size in human primary visual cortex. Nat. 
Neurosci. 9, 429–434 (2006).
20.	 Gilbert, C. D. & Li, W. Top-down influences on visual processing. 
Nat. Rev. Neurosci. 14, 350–363 (2013).
21.	 He, K., Zhang, X., Ren, S. & Sun, J. Deep residual learning for 
image recognition. In Proceedings of the IEEE Conference on 
Computer Vision and Pattern Recognition 770–778 (IEEE, 2016).
22.	 Devlin, J., Chang, M., Lee, K. & Toutanova, K. BERT: pre-training 
of deep bidirectional transformers for language understanding. 
In Proceedings of the 2019 Conference of the North American 
Chapter of the Association for Computational Linguistics: Human 
Language Technologies, Volume 1 (Long and Short Papers)  
(eds. Burstein, J. et al.) 4171–4186 (Association for Computational 
Linguistics, 2019).
23.	 Naselaris, T., Kay, K. N., Nishimoto, S. & Gallant, J. L. Encoding and 
decoding in fMRI. Neuroimage 56, 400–410 (2011).
24.	 Allen, E. J. et al. A massive 7T fMRI dataset to bridge cognitive 
neuroscience and artificial intelligence. Nat. Neurosci. 25,  
116–126 (2022).
25.	 Chen, T., Kornblith, S., Norouzi, M. & Hinton, G. A simple 
framework for contrastive learning of visual representations. In 
International Conference on Machine Learning (eds. Daumé III, H. & 
Singh, A.) 1597-1607 (PMLR, 2020).
26.	 Schuhmann, C. et al. LAION-5B: an open large-scale dataset 
for training next generation image-text models. Adv. Neural Inf. 
Process. Syst. 35, 25278–25294 (2022).


## Page 11

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1425
Article
https://doi.org/10.1038/s42256-023-00753-y
27.	 Thomee, B. et al. YFCC100M: the new data in multimedia 
research. Commun. ACM 59, 64–73 (2016).
28.	 Güçlü, U. & van Gerven, M. A. Deep neural networks reveal a 
gradient in the complexity of neural representations across the 
ventral stream. J. Neurosci. 35, 10005–10014 (2015).
29.	 Huth, A. G., De Heer, W. A., Griffiths, T. L., Theunissen, F. E. & 
Gallant, J. L. Natural speech reveals the semantic maps that tile 
human cerebral cortex. Nature 532, 453–458 (2016).
30.	 Epstein, R. A. & Baker, C. I. Scene perception in the human brain. 
Annu. Rev. Vis. Sci. 5, 373–397 (2019).
31.	 Downing, P. E., Jiang, Y., Shuman, M. & Kanwisher, N. A cortical 
area selective for visual processing of the human body. Science 
293, 2470–2473 (2001).
32.	 Sergent, J., Ohta, S. & MacDonald, B. Functional neuroanatomy 
of face and object processing: a positron emission tomography 
study. Brain 115, 15–36 (1992).
33.	 Kanwisher, N., McDermott, J. & Chun, M. M. The fusiform face 
area: a module in human extrastriate cortex specialized for face 
perception. J. Neurosci. 17, 4302–4311 (1997).
34.	 Lescroart, M. D., Stansbury, D. E. & Gallant, J. L. Fourier power, 
subjective distance, and object categories all provide plausible 
models of bold responses in scene-selective visual areas. Front. 
Comput. Neurosci. 9, 135 (2015).
35.	 de Heer, W. A., Huth, A. G., Griffiths, T. L., Gallant, J. L. & 
Theunissen, F. E. The hierarchical cortical organization of human 
speech processing. J. Neurosci. 37, 6539–6557 (2017).
36.	 Saxe, R. & Kanwisher, N. People thinking about thinking people: 
the role of the temporo-parietal junction in “theory of mind”. 
NeuroImage. 19, 1835–1842 (2003).
37.	 Çukur, T., Nishimoto, S., Huth, A. G. & Gallant, J. L. Attention 
during natural vision warps semantic representation across the 
human brain. Nat. Neurosci. 16, 763–770 (2013).
38.	 Jain, N. et al. Selectivity for food in human ventral visual cortex. 
Commun. Biol. 6, 175 (2023).
39.	 Pennock, I. M. L. et al. Color-biased regions in the ventral visual 
pathway are food selective. Curr. Biol. 33, 134–146.e4 (2023).
40.	 Khosla, M., Apurva Ratan Murty, N. & Kanwisher, N. A highly 
selective response to food in human visual cortex revealed  
by hypothesis-free voxel decomposition. Curr. Biol. 32, 4159–4171.
e9 (2022).
41.	 Conwell, C., Prince, J. S., Hamblin, C. J. & Alvarez, G. A. Controlled 
assessment of CLIP-style language-aligned vision models in 
prediction of brain & behavioral data. In ICLR 2023 Workshop on 
Mathematical and Empirical Understanding of Foundation Models 
(eds. Kumar, A. et al.) (2023).
42.	 Conwell, C., Prince, J. S., Alvarez, G. A. & Konkle, T. Large-scale 
benchmarking of diverse artificial vision models in prediction  
of 7T human neuroimaging data. Preprint at https://doi.org/ 
10.1101/2022.03.28.485868 (2022).
43.	 Conwell, C., Prince, J., Alvarez, G., Konkle, T. & Kay, K. 
Opportunistic experiments on a large-scale survey of diverse 
artificial vision models in prediction of 7T human fMRI data.  
In Conference on Cognitive Computational Neuroscience  
(2022).
44.	 Bracci, S. & Op de Beeck, H. P. Understanding human object 
vision: a picture is worth a thousand representations. Annu. Rev. 
Psychol. 74, 113–135 (2023).
45.	 Chang, N., Pyles, J. A., Marcus, A., Gupta, A., Tarr, M. J. &  
Aminoff, E. M. BOLD5000, a public fMRI dataset while viewing 
5000 visual images. Sci. Data 6, 49 (2019).
46.	 Hebart, M. N., Contier, O., Teichmann, L., Rockter, A. H.,  
Zheng, C. Y., Kidder, A., Corriveau, A., Vaziri-Pashkam, M. &  
Baker, C. I. THINGS-data, a multimodal collection of large-scale 
datasets for investigating object representations in human brain 
and behavior. eLife 12, e82580 (2023).
47.	 Maier, M. & Abdel Rahman, R. No matter how: top-down effects 
of verbal and semantic category knowledge on early visual 
perception. Cogn. Affect. Behav. Neurosci. 19, 859–876 (2019).
48.	 Charest, I., Allen, E., Wu, Y., Naselaris, T. & Kay, K. Precise 
identification of semantic representations in the human brain.  
J. Vis. 20, 539–539 (2020).
49.	 Devereux, B. J., Clarke, A. & Tyler, L. K. Integrated deep 
visual and semantic attractor neural networks predict fMRI 
pattern-information along the ventral object processing pathway. 
Sci. Rep. 8, 10636 (2018).
50.	 Nappa, R., Wessel, A., McEldoon, K. L., Gleitman, L. R. &  
Trueswell, J. C. Use of Speaker’s Gaze and Syntax in Verb 
Learning. Lang. Learn. Dev. 5, 203–234 (2009).
51.	 Waxman, S. R. & Markow, D. B. Words as invitations to form 
categories: evidence from 12- to 13-month-old infants. Cogn. 
Psychol. 29, 257–302 (1995).
52.	 Lupyan, G., Rakison, D. H. & McClelland, J. L. Language is not 
just for talking: redundant labels facilitate learning of novel 
categories. Psychol. Sci. 18, 1077–1083 (2007).
53.	 Shusterman, A. & Spelke, E. in The Innate Mind: Structure and 
Contents (eds Carruthers, P. et al.) Ch. 6, 89–106 (Oxford Univ. 
Press, 2005).
54.	 Lin, T. Y. et al. Microsoft COCO: common objects in context. In 
European Conference on Computer Vision – ECCV 2014. Lecture 
Notes in Computer Science, 8693 (eds. Fleet, D., Pajdla, T., 
Schiele, B., & Tuytelaars, T.) 740–755 (Springer, 2014).
55.	 Dale, A. M., Fischl, B. & Sereno, M. I. Cortical surface-based 
analysis: I. segmentation and surface reconstruction. NeuroImage 
9, 179–194 (1999).
56.	 Fischl, B., Sereno, M. I. & Dale, A. M. Cortical surface-based 
analysis: II. Inflation, flattening, and a surface-based coordinate 
system. NeuroImage 9, 195–207 (1999).
57.	 Gao, J. S., Huth, A. G., Lescroart, M. D. & Gallant, J. L. Pycortex: an 
interactive surface visualizer for fMRI. Front. Neuroinform. 9 (2015).
58.	 Koushik, J. torch-gel. GitHub https://github.com/jayanthkoushik/
torch-gel (2017).
59.	 Benjamini, Y. & Hochberg, Y. Controlling the false discovery rate: 
a practical and powerful approach to multiple testing. J. R. Stat. 
Soc. Series B Methodol. 57, 289–300 (1995).
60.	 Wang, A. ariaaay/clip2brain: initial release. Zenodo https://doi.
org/10.5281/zenodo.8234313 (2023).
Acknowledgements
A.Y.W. and M.J.T. were supported by the AFRL/AFOSR award FA9550-
18-1-0251. The NSD was supported by NSF IIS-1822683 and NSF IIS-
1822929. We would like to thank the following people for contributing 
technical assistance, ideas and commentary to this project: J. Koushik, 
N. Chang and M. Henderson.
Author contributions
A.Y.W., M.J.T. and L.W. conceived the experiments. K.K. and  
T.N. collected the neuroimaging data. A.Y.W. conducted the 
experiments and analysed the results. All authors wrote and  
edited the manuscript.
Competing interests
The authors declare no competing interests.
Additional information
Supplementary information The online version  
contains supplementary material available at  
https://doi.org/10.1038/s42256-023-00753-y.
Correspondence and requests for materials should be addressed  
to Leila Wehbe.


## Page 12

Nature Machine Intelligence | Volume 5 | December 2023 | 1415–1426
1426
Article
https://doi.org/10.1038/s42256-023-00753-y
Peer review information Nature Machine Intelligence thanks the 
anonymous reviewers for their contribution to the peer review  
of this work.
Reprints and permissions information is available at  
www.nature.com/reprints.
Publisher’s note Springer Nature remains neutral with regard to 
jurisdictional claims in published maps and institutional affiliations.
Springer Nature or its licensor (e.g. a society or other partner)  
holds exclusive rights to this article under a publishing  
agreement with the author(s) or other rightsholder(s); author 
self-archiving of the accepted manuscript version of this article is 
solely governed by the terms of such publishing agreement and 
applicable law.
© The Author(s), under exclusive licence to Springer Nature Limited 
2023


