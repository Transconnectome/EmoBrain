# (2024) Emergence of Emotion Selectivity in Deep Neural Networks Trained to Recognize Visual Objects

**Source:** (2024) Emergence of Emotion Selectivity in Deep Neural Networks Trained to Recognize Visual Objects.pdf

---

## Page 1

RESEARCH ARTICLE
Emergence of Emotion Selectivity in Deep
Neural Networks Trained to Recognize Visual
Objects
Peng LiuID1,2, Ke Bo2, Mingzhou Ding1*, Ruogu FangID1,3*
1 J. Crayton Pruitt Family Department of Biomedical Engineering, Herbert Wertheim College of Engineering,
University of Florida, Gainesville, Florida, United States of America, 2 Department of Psychological and Brain
Sciences, Dartmouth College, Hanover, New Hampshire, United States of America, 3 Center for Cognitive
Aging and Memory, McKnight Brain Institute, University of Florida, Gainesville, Florida, United States of
America
* mding@bme.ufl.edu (MD); ruogu.fang@bme.ufl.edu (RF)
Abstract
Recent neuroimaging studies have shown that the visual cortex plays an important role in
representing the affective significance of visual input. The origin of these affect-specific
visual representations is debated: they are intrinsic to the visual system versus they arise
through reentry from frontal emotion processing structures such as the amygdala. We
examined this problem by combining convolutional neural network (CNN) models of the
human ventral visual cortex pre-trained on ImageNet with two datasets of affective images.
Our results show that in all layers of the CNN models, there were artificial neurons that
responded consistently and selectively to neutral, pleasant, or unpleasant images and
lesioning these neurons by setting their output to zero or enhancing these neurons by
increasing their gain led to decreased or increased emotion recognition performance
respectively. These results support the idea that the visual system may have the intrinsic
ability to represent the affective significance of visual input and suggest that CNNs offer a
fruitful platform for testing neuroscientific theories.
Author summary
What is the role played by sensory cortices in assessing the emotional significance of sen-
sory input? This question is attracting increasing research interest. Recent work has found
affect-specific neural representations in visual cortex. The origins of these representations
are debated. According to the reentry hypothesis, these representations result from reen-
trant feedback arising from anterior emotion processing structures such as the amygdala.
An alternative hypothesis holds that sensory cortex may have the intrinsic capacity to rep-
resent the emotional qualities of sensory input. We examined this problem by utilizing the
convolutional neural networks (CNNs) trained to recognized visual objects as computa-
tional models of the primate ventral visual system. Emotionally charged images were
divided into three broad categories (pleasant, neutral and unpleasant) and presented to
the CNNs. Responses of artificial neurons to these images were found to exhibit robust
PLOS COMPUTATIONAL BIOLOGY
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
1 / 22
a1111111111
a1111111111
a1111111111
a1111111111
a1111111111
OPEN ACCESS
Citation: Liu P, Bo K, Ding M, Fang R (2024)
Emergence of Emotion Selectivity in Deep Neural
Networks Trained to Recognize Visual Objects.
PLoS Comput Biol 20(3): e1011943. https://doi.
org/10.1371/journal.pcbi.1011943
Editor: Xue-Xin Wei, UT Austin: The University of
Texas at Austin, UNITED STATES
Received: May 29, 2023
Accepted: February 24, 2024
Published: March 28, 2024
Copyright: © 2024 Liu et al. This is an open access
article distributed under the terms of the Creative
Commons Attribution License, which permits
unrestricted use, distribution, and reproduction in
any medium, provided the original author and
source are credited.
Data Availability Statement: The data and code to
replicate the key results are available at https://
zenodo.org/records/10720551.
Funding: Funding: This work was supported in part
by the National Science Foundation grant 1908299
(RF, MD) and 2318984 (RF, MD), the National
Institutes of the National Institutes of Health/
National Institute of Mental Health grants
MH112558 (MD) and MH125615 (MD, RF), the
University of Florida Artificial Intelligence Research
Catalyst Fund (RF, MD), the University of Florida
Informatics Institute Graduate Student Fellowship


## Page 2

emotion selectivity. Importantly, enhancing the neurons that were selective for a given
emotion led to the increased ability in recognizing that emotion, whereas lesioning these
neurons led to the decrease in that ability. This research lends support to the notion that
emotional perception might be an intrinsic property of the visual cortex. It also under-
scores the CNNs’ value in examining neuroscientific theories.
Introduction
Human emotions are complex and multifaceted and under the influence of many factors,
including individual differences, cultural backgrounds, and the context in which the emotion
is experienced [1–5]. Still, a large number of people, across different cultures, different levels of
education, and different socioeconomic backgrounds, experience similar feelings when view-
ing images of varying affective content [6–9]. What fundamental principles in the functions of
the human visual system underlie such universality requires elucidation.
Previous studies of emotion perception have primarily relied on empirical cognitive experi-
ments [10–12]. Some of them have focused on capturing human behavioral valence or arousal
judgment on affective images [13–16], while others have recorded brain activities to look for
neural correlates of affective stimuli processing [17–21]. Despite decades of effort, how the
brain transforms visual stimuli into subjective emotion judgments (e.g., happy, neutral, or
unhappy) remains not well understood. The advent of machine learning especially artificial
neural networks (ANNs) opens the possibility of addressing this problem using a modeling
approach.
Artificial neural networks can project visual images to a feature space in which the activa-
tion patterns of hidden layers are the features used for object classification and recognition.
One type of artificial neural network, convolutional neural networks (CNNs), owing to their
hierarchical organization resembling that of the visual system, are increasingly used as models
of visual processing in the primate brain [22–26]. CNNs trained to recognize visual objects can
achieve performance levels rivaling or even exceeding that of humans. Interestingly, CNNs
trained on images from such databases as ImageNet [27] are found to demonstrate neural
selectivity for a variety of stimuli that are not included in the training data. For instance, [28]
showed that neurons in a CNN trained on ImageNet became selective for numbers without
having been trained on any "number" datasets. Similarly, [29] demonstrated that a CNN, when
trained on non-face objects, can develop a recognition performance for faces that significantly
exceeds chance levels. These instances demonstrate that CNNs may possess recognition capa-
bilities beyond the primary task they are trained on.
The role of the visual cortex in visual emotion processing is debated [30,31]. [32] argued
that emotion representation is an intrinsic property of the visual cortex. They used a CNN pre-
trained on ImageNet to show that the model can accurately predict the emotion categories of
affective images. [20], on the other hand, showed that the affective representations found in
the visual cortex during affective scene processing might arise as the result of reentry from
anterior emotion-modulating structures such as the amygdala. The goal of this study is to fur-
ther examine this question using CNN models.
CNN models are well suited for addressing questions related to the human visual system.
Among the many well-established CNN models, VGG-16 [33] has an intermediate level of
complexity and is shown to have superior object recognition performance [34]. Using VGG-
16, recent cognitive neuroscience studies have explored how encoding and decoding of sen-
sory information are hierarchically processed in the brain [23,35,36]. [23] used VGG-16 to
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
2 / 22
(PL). The funders had no role in study design, data
collection and analysis, decision to publish, or
preparation of the manuscript. None of the authors
received a salary from the funders.
Competing interests: The authors declare that they
have no competing interests.


## Page 3

quantitatively demonstrate an explicit gradient of feature complexity encoded in the ventral
visual pathway. [35] used VGG-16 to model the visual cortical activity of human participants
viewing images of objects and demonstrated that activities in different layers of the model
highly correlate with brain activities in different visual areas. [36] investigated qualitative simi-
larities and differences between VGG-16 and other feed-forward CNNs in the representation
of the visual object and showed these CNNs exhibit multiple perceptual and neural phenom-
ena such as the Thatcher effect [37] and Weber’s law [38].
In this study, we mainly focused on VGG-16 pre-trained on ImageNet as the model of the
human visual system and used AlexNet [39], which is another well-established CNN model of
visual processing, to test whether the results can be replicated. Using two well-established
affective image datasets: International Affective Picture System (IAPS) [15] and Nencki Affec-
tive Picture System (NAPS) [16], we examined whether emotion selectivity can spontaneously
emerge in such systems and whether such emotion selectivity has functional significance. For
each filter within a layer of the model, the emotional selectivity for the resulting feature map
was established by first computing neural responses to three broad classes of images: pleasant,
neutral, and unpleasant (tuning curves) at the level of each unit and then averaging these
responses across all the units within the feature map. A feature map, also referred to as a neu-
ron in what follows, is considered selective for a particular emotion if its tuning responses are
robust and exhibit the strongest responses to images of that category from both datasets. To
test whether these emotion-selective neurons have a functional role, we replaced the last
1000-unit object-recognition layer of the VGG-16 with a two-unit emotion-recognition layer
and trained the connections to this layer to decode pleasant versus non-pleasant, neutral vs.
non-neutral, and unpleasant vs. non-unpleasant images. Two neural manipulations were car-
ried out: lesion and feature attention enhancements. Lesioning the neurons selective for a spe-
cific emotion is expected to degrade the network’s performance in recognizing that emotion,
whereas applying attention enhancement to the neurons selective for the emotion is expected
to increase the network’s performance in recognizing that emotion.
Results
We tested whether emotion selectivity can naturally arise in a CNN model trained to recognize
visual objects. VGG-16 pre-trained on ImageNet data [27] was used for this purpose (see
Fig 1). Filters/channels within a layer were referred to as neurons and responses from the units
within the feature maps were averaged and treated as neuronal responses. Selectivity for pleas-
ant, neutral, and unpleasant emotions was defined for each neuron based on its response pro-
files to images from two affective picture sets (IAPS and NAPS). The functional significance of
these neurons was then assessed using lesion and attention enhancement methods.
Neuronal responses to emotional images in different convolutional layers
The tuning curve for a neuron is defined as the normalized mean response (tuning value) to
pleasant, neutral, and unpleasant images in a given dataset plotted as a function of the emotion
category. The maximum of the tuning curve indicates the neuron’s preferred emotion category
for that picture set. Fig 2A (top) shows the tuning curves of three neurons from the Convolu-
tional Layer 3 (an early layer) for both IAPS and NAPS datasets. According to the definition
above, these neurons are selective for pleasant, neutral, and unpleasant categories, respectively.
For the top 100 images from IAPS and NAPS that elicited the strongest response in these neu-
rons, Fig 2A (bottom) shows the valence distribution of these images. As can be seen, for these
early layer neurons, while the pleasant neuron is more activated by images with high valence
ratings (pleasant), for the neutral and unpleasant neurons, the patterns are less clear. For the
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
3 / 22


## Page 4

neurons in Convolutional Layer 6 (a middle layer), however, as shown in Fig 2B, their emotion
selectivity and the category of images they prefer show greater agreement. Namely, the pleas-
ant neuron prefers predominately images with high valence (pleasant), the neural neuron pre-
fers predominately images with intermediate valence (neutral), and the unpleasant neuron
prefers predominately images with low valence (unpleasant). The results for the three neurons
from Convolutional Layer 13 (a deep layer) are similar to those from Layer 6; see Fig 2C.
Emotion selectivity in different convolutional layers
Whereas tuning value and tuning curve characterize a neuron’s response to images from dif-
ferent emotion categories, the selectivity index (SI), which highlights the difference between
responses to different emotion categories of images, is a better index for defining emotion
selectivity. As shown in Fig 3A, emotion selectivity became stronger as one ascended the layers
from early to deep, an effect that is especially noticeable for the IAPS datasets, supporting the
notion that emotion differentiability increases as we go from earlier to deeper layers. In light of
the computational principle that earlier layer neurons encode lower-level stimulus properties
(e.g., shapes and edges) and deeper layer neurons encode higher-level properties such as
semantic meaning (e.g., object identities) [40–42], the results in Fig 3A as well as Fig 2 suggest
that from earlier to deeper layers, emotion as a higher level cognitive construct becomes pro-
gressively better defined and better differentiated.
To examine the role of the training to recognize objects in the foregoing observations, we
performed the same analysis in a VGG-16 with randomly initialized weights (i.e., not trained
to recognize objects). As seen in Fig 3A, emotion selectivity is generally low as evaluated by
both datasets, and there is no clear layer-dependence in emotion selectivity, suggesting that the
increased ability to represent and differentiate emotion in deeper network layers of the pre-
trained VGG-16 is an ability acquired through the training for object recognition.
Fig 1. The architecture of the VGG-16 model. We used the VGG-16 pre-trained on ImageNet to model the visual system. VGG-16 has 13
convolutional layers and three fully connected (FC) layers. Each convolutional layer (light yellow color) is followed by a ReLU activation layer (yellow
color) and a max-pooling layer (red color). Each FC layer (light purple color) is followed by a ReLU layer (purple color). The last FC layer is followed by
a ReLU and a SoftMax layer (dark purple color). In the original VGG-16, the last layer was used to recognize 1000 different objects. In our model it was
replaced by a two-unit layer whose connections to the preceding layer were trained to recognize different emotions: pleasant vs. non-pleasant; neutral
vs. non-neutral; unpleasant vs. non-unpleasant. Affective images in grayscale from two datasets (IAPS and NAPS) were presented to the model to define
the emotion-selectivity of neurons in the convolutional layers. Lesion and attention enhancement were applied to assess these neurons’ functional
significance.
https://doi.org/10.1371/journal.pcbi.1011943.g001
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
4 / 22


## Page 5

Generalizability of emotion-selective neurons
Fig 2 shows that a neuron can be tuned for the same emotion for both IAPS and NAPS data-
sets. A natural question is whether such neurons arise as the result of random chance or as an
emergent property of the trained network. Further, based on the value of SI, all neurons are
Fig 2. Tuning curves and emotion selectivity. (A-C) Tuning curves of example neurons from different convolutional
layers (top panel) along with the valence distribution of the top 100 images that elicited the strongest responses for a
given neuron.
https://doi.org/10.1371/journal.pcbi.1011943.g002
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
5 / 22


## Page 6

selectivity for one emotion or the other. Small SIs are likely subject to the influence of chance,
and as such, neurons with small SIs should be removed from further consideration. How to
determine the threshold for removal?
Fig 3. Emotion selectivity and its generalizability. (A) Emotion selectivity as a function of layer for IAPS and NAPS. (B-
top) Number of neurons determined to be selective for a given emotion for both IAPS and NAPS datasets compared with
the number of neurons in the overlap of two random sets of neurons. (B-bottom) The number of neurons determined to be
selective for a given emotion for both IAPS and NAPS datasets in VGG-16 pretrained on ImageNet and with randomly
initialized weights. (C) Removing successively larger percentages of neurons with small SI values and comparing the
performance of attention-enhancing the remaining neurons yielded a threshold of 80% for determining emotion selectivity.
https://doi.org/10.1371/journal.pcbi.1011943.g003
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
6 / 22


## Page 7

We performed two analyses to address the two questions. First, we rank-ordered neurons
according to their SI values, removed certain percentages of neurons with small SI values, and
attention-enhanced the remaining neurons (see next subsection) and observed the resulting
performance improvement. The results in Fig 3C suggest that removing neurons whose SIs fell
in the lower 20% (keeping 80%) is a reasonable threshold. Second, neurons determined to be
emotion selective according to IAPS and that according to NAPS were subjected to an overlap
analysis. Fig 3B (top) compares the number of neurons selective for the same emotion for both
IAPS and NAPS datasets against the number of neurons to be expected from the overlap of
two random sets of neurons. The former is consistently higher than the latter across all layers,
with the effect becoming more prominent in deeper layers, suggesting that emotion selectivity
generalizes across the two datasets and the generalizability is not due to chance.
What is the role of training to recognize visual objects in the generalizable emotion selectiv-
ity? To answer this question, we compared the number of emotion-selective neurons from the
overlap analysis derived from pre-trained VGG-16 on ImageNet against that derived from ran-
domly initialized VGG-16. Fig 3B (bottom) shows that for all emotion categories—pleasant,
neutral, and unpleasant—the pre-trained network consistently demonstrated a higher number
of emotion-selective neurons in the later layers, especially from Layer 5 onwards. These find-
ings suggest that emotion selectivity is an emergent property as the result of a neural network
undergoing training for object recognition.
The functionality of emotion-selective neurons
To test whether emotion-selective neurons have a functional role, we followed [43] and
replaced the last layer of the VGG-16, which originally contained 1,000 units for recognizing
1000 different types of objects, with a fully connected layer containing two units for recogniz-
ing two types of emotions. Three models were trained and tested for each of the two affective
picture datasets: Model 1: pleasant versus non-pleasant, Model 2: neutral versus non-neutral,
and Model 3: unpleasant versus non-unpleasant. Once these models were shown to have ade-
quate emotion recognition performance (see Table 1), two neural manipulations were consid-
ered: feature attention enhancement and lesion. For feature attention enhancement [44–46],
the gain of the neurons selective for a given emotion for both datasets is increased by increas-
ing the slope of the ReLU activation function (see Methods) [47–50], whereas for lesion, the
output of the neurons selective for a given emotion for both datasets was set to 0, which effec-
tively removes the contribution of these neurons, i.e., they are lesioned. We hypothesized that
[1] with attention enhancement, the network’s ability to recognize emotion is increased [2]
with lesioning, the network’s ability to recognize emotion is decreased, and [3] such effects are
not observed for modulating randomly selected neurons.
Table 1. Original and Enhanced and Lesioned Performance (F1-score) in VGG-16. The maximum performance changes for both enhancing and lesioning selective
neurons across different layers are shown below.
Dataset
Emotion to Recognize
Original Performance
Enhanced Performance
Enh. Increased (%)
Lesioned
Performance
Les. Decreased (%)
IAPS
Pleasant
0.70
0.73
4.29%
0.56
20%
Neutral
0.63
0.69
9.52%
0.26
58%
Unpleasant
0.62
0.69
11.29%
0.13
80%
NAPS
Pleasant
0.70
0.72
2.86%
0.49
31%
Neutral
0.63
0.67
6.35%
0.25
61%
Unpleasant
0.67
0.71
5.97%
0.41
39%
https://doi.org/10.1371/journal.pcbi.1011943.t001
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
7 / 22


## Page 8

Feature attention enhancement.
For IAPS images, Fig 4 compares performance changes
after enhancing the emotion-selective neurons as well as enhancing the same number of ran-
domly sampled neurons; see also Table 1. The optimal tuning strength for which we achieved
the best performance enhancement was chosen for each layer in the plot. As one can see, for
pleasant versus non-pleasant, neutral versus non-neutral, and unpleasant versus non-unpleas-
ant emotions, enhancing the gain of the neurons selective for a specific emotion can signifi-
cantly improve the emotion recognition performance of the CNN model for that emotion.
Moreover, deeper layer attention enhancement tends to yield greater performance improve-
ments than earlier layer attention enhancement. Increasing the gain in randomly selected
Fig 4. Effects of enhancing emotion-selective neurons and randomly selected neurons on IAPS dataset.
https://doi.org/10.1371/journal.pcbi.1011943.g004
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
8 / 22


## Page 9

neurons, however, shows either a marginal performance improvement or a significant perfor-
mance decline. The feature-attention performance of emotion-selective neurons over random
neurons is highly statistically significant in the middle and deeper layers (p< 1.2e-02). Fig 4
(right) shows the performance changes across layers as the tuning strength varied from 0 to 5.
We carried out the same analysis for the NAPS dataset in Fig 5. The results largely repli-
cated that in Fig 4 for the IAPS dataset.
Lesion analysis. The functional importance of the emotion-selective neurons can be fur-
ther assessed through lesion analysis [51–54]. As shown in Fig 6 (see also Table 1), we com-
pared the emotion recognition performance changes by setting the output from emotion-
Fig 5. Effects of enhancing emotion-selective neurons and randomly selected neurons on NAPS dataset.
https://doi.org/10.1371/journal.pcbi.1011943.g005
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
9 / 22


## Page 10

selective neurons to 0 as well as by setting the output of an equal number of randomly chosen
neurons to 0. As can be seen, lesioning the emotion-selective neurons led to significant perfor-
mance declines, especially for the deeper layers; the performance decline can be as high as
80%. In contrast, lesioning randomly selected neurons produces almost no performance
changes. These results, replicated across both datasets, further support the hypothesis that
emotion-selective neurons are important for emotion recognition, and the importance is
higher in deeper layers than in earlier layers.
Discussion
It has been argued that the human visual system has the intrinsic ability to recognize the moti-
vational significance of environmental inputs [55]. We examined this problem using convolu-
tional neural networks (CNNs) as models of the human visual system [56–61]. Selecting the
VGG16 pre-trained on images from the ImageNet as our model [62–64] and using two sets of
affective images (IAPS and NAPS) as test stimuli, we found the existence of emotion-selective
neurons in all layers of the model even though the model has never been explicitly trained to
recognize emotion. Additionally, emotion selectivity becomes stronger and more consistent in
the deeper layers, in agreement with prior literature suggesting that the deeper layers of CNNs
encode higher-level semantic information. For VGG-16 with randomly initialized weights
(i.e., not trained to recognize objects), however, no such effects were observed, suggesting that
emotion selectivity may be an emergent property through network training. Applying two
manipulations: feature attention enhancement and lesion, we can show further that the
Fig 6. Lesion Analysis. Performance changes were compared between lesioning emotion-selective neurons and randomly selected neurons.
https://doi.org/10.1371/journal.pcbi.1011943.g006
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
10 / 22


## Page 11

emotion-selective neurons are functionally significant, specifically: [1] after increasing the gain
of emotion-selective neurons (e.g., feature attention enhancement), the network’s performance
in emotion recognition is enhanced relative to increasing the gain of randomly selected neu-
rons and [2] in contrast, after lesioning the emotion-selective neurons, the network’s perfor-
mance in emotion recognition is degraded relative to lesioning randomly selected neurons.
These performance differences are stronger and more noticeable in deeper layers than in ear-
lier layers. In Figs F, G H, and I in S1 Text, we reported similar findings on the AlexNet, which
is a simpler CNN that has also been used in numerous studies as a model of the ventral visual
system [65–68]. Together, our findings indicate that emotion selectivity can spontaneously
emerge in CNN models trained to recognize visual objects, and these emotion-selective neu-
rons play a significant role in recognizing emotion in natural images, lending credence to the
notion that the visual system’s ability to represent affective information may be intrinsic.
Affective processing in the visual cortex
The perception of opportunities and threats in complex visual scenes represents one of the
main functions of the human visual system. The underlying neurophysiology is often studied
by having observers view pictures varying in affective content. [69] reported greater functional
activity in the visual cortex when subjects viewed pleasant and unpleasant pictures than neutral
images. [70] showed the visual cortex has differential sensitivities in response to emotional sti-
muli compared to the amygdala. [71] demonstrated that emotional significance (e.g., valence
or arousal) could modulate the perceptual encoding in the visual cortex. Two competing but
not mutually exclusive groups of hypotheses have been advanced to account for emotion-spe-
cific modulations of activity in the visual cortex. The so-called reentry hypothesis states that
the increased visual activation evoked by affective pictures results from reentrant feedback,
meaning that signals arising in subcortical emotion processing structures such as the amygdala
propagate to the visual cortex to facilitate the processing of motivationally salient stimuli [72–
74]. Recent work [20] provides support for this view. Using multivariate pattern analysis and
functional connectivity, these authors showed that [1] different emotion categories (e.g., pleas-
ant versus neutral and unpleasant versus neutral) are decodable based on the multivoxel pat-
terns in the visual cortex and [2] the decoding accuracy is positively associated with the
strength of connectivity from anterior emotion-modulating regions to ventral visual cortex. A
second group of hypotheses states that the visual cortex may itself have the ability to code for
the emotional qualities of a stimulus, without the necessity for recurrent processing (see [75]
for a review). Evidence supporting this hypothesis comes from empirical studies in experimen-
tal animals [76,77] as well as in human observers [78], in which the extensive pairing of simple
sensory cues such as tilted lines or sinusoidal gratings with emotionally relevant outcomes
shapes early sensory responses [79]. Beyond simple visual cues, recent computational work
using deep neural networks has also suggested that the visual cortex may intrinsically represent
emotional value as contained in complex visual media such as video clips of varying affective
content [32]. Our findings reveal that emotion-selective neurons are present in all layers of
two CNN models, which are computational representations of the visual cortex. These neurons
play a crucial role in emotion recognition. This contributes to the growing computational evi-
dence suggesting that the visual cortex may inherently possess the capability to evaluate the
emotional significance of visual stimuli.
Neural selectivity in ANNs and the brain
That CNNs, or more generally ANNs, can be trained to recognize a large variety of visual
objects has long been recognized. Remarkably, recent studies note that ANNs trained on
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
11 / 22


## Page 12

recognizing visual objects can spontaneously develop selectivity for other types of input,
including visual numbers and faces [80]. The number sense is considered an inherent ability of
the brain to estimate the quantity of certain items in a visual set [81,82]. There is significant
evidence demonstrating that the number sense exists in both humans (e.g., adults and infants)
[83–85] and non-human primates (e.g., numerically naïve monkeys) [86–88]. [89] found that
number-selective units spontaneously emerged in a deep artificial neural network trained on
ImageNet for object recognition. [90] demonstrated that number selectivity can even arise
spontaneously in randomly initialized deep neural networks without any training. Both studies
focused on the last convolutional layers, in which the number-selective units were found, and
they also demonstrated that the emergence of number-selective units could result from the
weighted sum of both decreasing and increasing the activity of some units. In addition, it is
well known that face-selective neurons exist in humans [91] and non-human primates. [80]
showed that neurons in a randomly initialized deep neural network without training could
selectively respond to faces, and the neurons in the deeper layers are more selective. [92] dem-
onstrated that brain-like functional segregation can emerge spontaneously in deep neural net-
works trained on object recognition and face perception and proposed that the development
of functional segregation of face recognition in the brain is a result of computational optimiza-
tion in the cortex. Augmenting this rapidly growing literature, our study demonstrates that
emotion selectivity can emerge in deep artificial neural network models of the human visual
system trained to recognize objects.
Layer dependence
Like the biological brain, the CNN model has a layered structure which allows the processing
of information in a hierarchical fashion. Our layer-wise analysis showed that the extent and
strength of emotion selectivity are a function of the model layers. Compared to the early layers,
the deeper layers have larger portions of neurons that show emotion selectivity, and the selec-
tivity is stronger, consistent with the previous observations that deeper layers of CNN models
encode more abstract concepts. For example, [40,93] examined the internal representations of
different layers in a CNN and found that deeper layers of the network tend to encode more
abstract concepts, such as object parts and textures. The layered processing of emotional infor-
mation may have several functional benefits. First, by processing visual information in hierar-
chical stages, the brain can quickly and efficiently respond to stimuli without the need for a
complete and detailed analysis of the entire stimulus at once [94–96]. This is especially impor-
tant for the processing of emotionally salient stimuli, as quick and accurate emotional
responses can be crucial for survival. Second, it would offer more flexibility for the processing
of emotion at different levels of detail, which may depend on the perception task and the envi-
ronmental context. For example, if the stimulus is perceived as significant or crucial for sur-
vival, it elicits a stronger and more widespread neural response, engaging multiple regions and
processing stages. On the other hand, if the stimulus is not significant, it elicits a weaker and
more limited neural response involving fewer regions or layers and processing stages [97–99].
Third, the integration of information from different levels allows for a more complete and
nuanced representation of the visual stimulus and emotional response. This allows for the cre-
ation of a final representation that takes into account not just the visual properties of the stim-
ulus but also its emotional significance and its impact on the individual [100–102]. Lastly, by
processing information in a layer-dependent manner, the brain can adapt and change the pro-
cessing of information based on experience and learning [103]. This allows the brain to refine
its processing strategies and improve its performance over time [104].
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
12 / 22


## Page 13

Relation to prior literature
[32], to the best of our knowledge, is the first to examine emotion processing in deep neural
networks. Their model, which is a modified AlexNet called the EmoNet, was shown to have
the ability to classify affective images into 20 different emotion categories. Importantly, using a
20-way linear decoder, they further showed that neural activities in different layers of the net-
work especially the deeper layers can differentiate different emotions in the input images, sug-
gesting the existence of emotion selectivity neurons in CNNs. Building on this work, our main
contributions are threefold: [1] confirming and characterizing emotion selectivity at the single
filter (neuron) level, [2] demonstrating the functional significance of emotion-selective neu-
rons through the application of lesion and attention enhancement methods, and [3] replicating
the findings across two CNN models (VGG-16 and AlexNet) and two affective image sets
(IAPS and NAPS).
Limitations and other considerations
Several limitations of our study should be noted. Firstly, emotion was divided into three broad
categories: pleasant, unpleasant, and neutral. While this is in line with many neurophysiologi-
cal studies in humans, future work should examine finer differentiations of emotion, e.g., joy,
sadness, horror, disgust, and so on, and their neural representations in the brain. Secondly,
there might be other factors (e.g., low-level features) that drive the emotion selectivity of neu-
rons. Since we used grayscale images in this study, we can rule out color as a possible con-
founding low-level feature. Applying the GIST algorithm [105] to extract low-level features
from images and the support vector machine (SVM) algorithm [106], we found that images
from different emotion categories cannot be decoded from the low-level features; see Fig J in
S1 Text. The impact of an image’s object category and its emotion category on neural activa-
tion was examined by placing images in the IAPS and NAPS datasets into object categories
based on the descriptions of the images (Figs LA and MA in S1 Text) and applying Two-Way
ANOVA tests to filter activations in the VGG-16 model. We found that the neurons responded
more strongly to emotion categories than object categories and there were significant interac-
tions between the two categories in deeper layers (Fig LB and MB in S1 Text). We do note that,
as the number of images in different object categories are relatively small in both affective data-
sets, this analysis should be viewed as preliminary. The influence of other factors such as the
presence of faces and image animacy is more difficult to ascertain. Thirdly, although the pres-
ent study is motivated by neuroscience questions, to what extent our results have a direct bear-
ing on understanding brain function is unclear. Whereas previous work did compare activities
in VGG-16 and other deep neural networks with neural recordings during object recognition
[67, 107–109], there is no study to date comparing activities in deep neural networks and neu-
ral recordings during emotion recognition. In this sense, this work’s neural relevance should
be considered speculative.
Materials and methods
Affective picture sets
Two sets of widely used affective images were used in this study. The IAPS library includes
1,182 images covering approximately 20 subclasses of emotions such as joy, surprise, entrance-
ment, sadness, romance, disgust, and fear. The NAPS library has 1,356 images that can be
divided into similar subclasses. For both libraries, each image has a normative valence rating,
ranging from 1 to 9, indicating whether the image expresses unpleasant, neutral, or pleasant
emotions; the distributions of the valence rating from the two datasets were given in Fig AC
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
13 / 22


## Page 14

(right) in S1 Text. In this study, for simplicity and following the common practice in human
imaging studies of emotion [20,110–112], we classified images into three main categories
based on their valence scores: "pleasant," "neutral," and "unpleasant." For images that fell near
the boundary between categories, we used soft thresholds of 4.3±0.5 and 6.0±0.5 to determine
their classification as either "unpleasant" or "neutral," or "neutral" or "pleasant." We also visu-
ally examined each image to confirm its category. Finally, any images that we could not confi-
dently classify were marked as "unknown" and removed from the analysis. This process
resulted in some differences in the number of images in each category from the original data-
sets. After this categorization, IAPS images were divided into 296 pleasant, 390 neutral, and
341 unpleasant images, and NAPS images into 352 pleasant, 477 neutral, and 281 unpleasant
images (see Figs AB in S1 Text). These images were transformed from the original color
images to grayscale images prior to the commencement of the study reported here. The goal
was to remove color as a possible low-level visual feature confounding the emotion selectivity
analysis.
The convolutional neural network model
VGG-16, a well-tested deep convolutional neural network for natural image recognition, was
used in this study to evaluate emotion selectivity. It has 13 convolutional layers followed by
three fully connected layers, with the last fully connected layer containing 1000 units for recog-
nizing 1000 different types of visual objects. Each layer of VGG-16 contains a large number of
filters/channels, the application of each of which results in a feature map consisting of a large
number of units. For convenience, and to stress neurobiological relevance, these filters/chan-
nels were often referred to as artificial neurons or simply neurons in this paper. Each neuron is
characterized by a ReLU activation function (see Fig A in S1 Text). Through this function,
neurons within a given layer, upon receiving and processing the input from the previous layer,
yield activation maps (i.e., feature maps) which become the input for the next layer. Previous
studies have compared the activation patterns of the VGG-16 model with experimental record-
ings from both humans and non-human primates and found that early layers of the model
behave similarly to early visual areas such as V1, whereas deeper layers of the model are more
analogous to higher-order visual areas such as the object-selective lateral occipital areas
[22,113–115].
In this study, VGG-16 was used in two ways. First, to examine whether emotional selectivity
emerges in neurons trained to recognize objects, we took the VGG-16 model pre-trained on
1.2 million natural images from the ImageNet, presented affective pictures from the two afore-
mentioned affective picture datasets to the model, and analyzed the activation profiles of neu-
rons from each layer. The emotional selectivity of each neuron was determined from these
activation profiles (see below). Second, to test the functionality of the emotion-selective neu-
rons, we replaced the last layer of the VGG-16 with a two-unit fully connected layer and
trained the connections to this two-unit layer to recognize two categories of emotion: pleasant
versus non-pleasant, neutral versus non-neutral, or unpleasant versus non-unpleasant. The
training of the last two-unit emotion recognition layer used cross-entropy as the objective
function. It is worth noting that, aside from the last emotion-recognition layer, the other lay-
ers’ weights in the VGG-16 network remained the same as that trained on the ImageNet data;
in other words, they were frozen.
The training data and the testing data for the final 2-unit emotion recognition layer of our
model were separate for IAPS and NAPS to avoid overfitting. Specifically, for each emotion
category, we partitioned the images from both datasets into training, validation, and testing
subsets at a ratio of 50%:25%:25%. We used a learning rate of 1e−3, trained for 10 epochs, and
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
14 / 22


## Page 15

set the batch size to 128. Finally, we employed the F1-score to assess the performance of our
model in emotion recognition.
Emotion selectivity definition
We used two methods to evaluate the differential responses of a neuron to images from differ-
ent emotion categories (pleasant, neutral, or unpleasant). Tuning value emphasizes the nor-
malized response to images from the same category. It is used in Fig 2 to illustrate possible
response profiles or tuning curves of different neurons. The selective index (SI), in contrast,
emphasizes the difference between responses to images from one emotion category and those
from other emotion categories. It is thus more suitable for quantifying the emotion selectivity
of a neuron. Results reported in Figs 3 and 4 as well as in Figs F, G, H, and I in S1 Text were
done with the SI.
Tuning value calculation.
We followed the method in [43] for calculating the tuning
value in Fig 2. The tuning v focuses on the strength or magnitude of a neuron’s response to a
particular emotion, relative to its average response. The details can be found below.
The output from each filter also referred to as a neuron in this study, see Fig A in S1 Text,
can be written as:
xlk ¼ ð1 þ aÞmax½0; wlk  xl  1
½1
where wlk indicates the weights of the kth filter in the lth convolutional layer, and * indicates
mathematical convolution which applies matrix multiplication between w and the outputs X
from the (l−1)th layer. Of note in Eq [1] is that the ReLU activation function typically has a
slope of 1 (α = 0). Here in this work, the slope is a tunable parameter. By tuning the slope of
the ReLU function, we change the gain of the neuron, simulating the effect of feature-based
attention control [43, 53].
Let Xlk
i;jðnÞ represents the response of the unit located at coordinates (i,j) in the kth filter in
layer l to image n. Then
plk n
ð Þ ¼
1
WH
XW
i¼1
XH
j¼1 Xlk
i;jðnÞ
½2
is the response to the image averaged across the entire filter. Here W and H represent the
width and height of the feature map. Thus, the mean activity of the filter k in layer l in response
to all images in a dataset can be formulated as:
^plk ¼ 1
N
XN
n¼1 plkðnÞ
½3
where N represents the total number of images in a given set. The tuning value of the filter is
calculated according to
Slk
e ¼
1
Ne
PNe
n¼1 plkðnÞ   ^plk
ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi
1
N
PN
n¼1 ðplkðnÞ   ^plkÞ
2
q
½4
where Slk
e represents the normalized activation of filter k in layer l in response to all images of
emotion category e, where e2{pleasant, neutral, unpleasant}. A neuron is considered selective
for a specific emotion if the normalized activation for the images within that emotion category
is highest among the three possible values. For example, if Slk
e¼pleasant = -0.1, Slk
e¼neutral ¼ 0:2, and
Slk
e¼unpleasant = 0.3, the artificial neuron k is considered selective for “unpleasant images”.
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
15 / 22


## Page 16

Selectivity index calculation: Selectivity Index (SI) [116] is defined as follows. First, consider
d0 pleasant
ð
Þ ¼
Xpleasant  XneutralþXunpleasant
2
ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi
σ2
pleasantþσ2
neutralþσ2
unpleasant
2
q
d0 neutral
ð
Þ ¼
Xneutral  XpleasantþXunpleasant
2
ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi
σ2
neutralþσ2
pleasantþσ2
unpleasant
2
q
½5
d0 unpleasant
ð
Þ ¼
Xunpleasant  XpleasantþXneutral
2
ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi
σ2
unpleasantþσ2
pleasantþσ2
neutral
2
q
where Xpleasant, Xneutral, and Xunpleasant represents the mean response to the pleasant, neutral,
and unpleasant categories, respectively; s2
pleasant; s2
neutral, and s2
unpleasant represents the variance of
the response to the pleasant, neutral, and unpleasant category, respectively. SI is the largest d0
and the emotion that gives rise to the largest d0 defines the emotion for which the neuron is
selective.
Identification of emotion-selective neurons.
To guard against spurious identification of
emotion selectivity and ensure that neurons designated to be selective for an emotion do so for
both datasets, we applied two analyses. First, we rank-ordered neurons according to their SI
values, eliminated neurons with small SI values, and tested the emotion recognition perfor-
mance under attention enhancement of the remaining neurons (see below). Increasing the
percentage of neurons eliminated until we saw a significant change in performance. That per-
centage was then defined as the threshold for defining emotion selectivity within a dataset (see
Fig 3C for an example of finding the threshold for the pleasant category on the IAPS dataset).
Second, for neurons identified as selective for certain emotions based on IAPS and that based
on NAPS, we overlapped the two sets of neurons and considered the overlapped neurons to be
the genuine emotion-selective neurons.
Testing the functionality of the emotion-selective neurons
Do the emotion-selective neurons defined above have a functional role? We applied two differ-
ent approaches to examine this question: lesion and attention enhancement.
Lesion.
If the emotion-selective neurons are functionally important, then lesioning these
neurons should lead to degraded performance in recognizing the emotion of a given image.
Here the lesion of a specific neuron is achieved by setting its output to 0 (namely, setting α =
−1 in Eq [1]). In our experiments, we lesioned the neurons selective for a given emotion as
well as randomly selected neurons in a particular layer and observed the changes in the emo-
tion recognition performance of the model.
Attention enhancement.
We further tested whether enhancing the activity of an emo-
tion-selective neuron can lead to performance improvement in emotion recognition. Follow-
ing [43], the strength of α was increased from 0 to 5 with interval step size 0.1, where α = 0 is
the conventional choice and α>0 represents increased neuronal gain (i.e., enhanced feature
attention). According to the feature similarity gain theory, increasing the gain of a neuron
leads to enhanced performance of the neuron in perceiving stimuli with the relevant features.
In our experiments, we enhanced the neurons selective for a given emotion as well as ran-
domly selected neurons in a particular layer and observed the changes in the emotion recogni-
tion performance of the model [43] (see Figs BA and BB in S1 Text).
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
16 / 22


## Page 17

Supporting information
S1 Text. Supplementary information file, including Figs A-N and Tables A-C.
(DOCX)
Author Contributions
Conceptualization: Peng Liu, Mingzhou Ding, Ruogu Fang.
Data curation: Peng Liu, Ke Bo.
Formal analysis: Peng Liu.
Funding acquisition: Mingzhou Ding, Ruogu Fang.
Investigation: Peng Liu, Ke Bo, Mingzhou Ding, Ruogu Fang.
Methodology: Peng Liu, Ke Bo, Mingzhou Ding, Ruogu Fang.
Project administration: Peng Liu, Mingzhou Ding, Ruogu Fang.
Resources: Peng Liu, Mingzhou Ding, Ruogu Fang.
Software: Peng Liu.
Supervision: Mingzhou Ding, Ruogu Fang.
Validation: Peng Liu, Ke Bo, Mingzhou Ding, Ruogu Fang.
Visualization: Peng Liu, Ke Bo.
Writing – original draft: Peng Liu, Mingzhou Ding, Ruogu Fang.
Writing – review & editing: Peng Liu, Ke Bo, Mingzhou Ding, Ruogu Fang.
References
1.
Kitayama S., Emotion and Culture: Empirical Studies of Mutual Influence ( American Psychological
Association, Washington, DC, US, 1994).
2.
McCarthy E. D., The Social Construction of Emotions: New Directions from Culture Theory. Sociology
Faculty Publications (1994).
3.
Banks S. J., Eddy K. T., Angstadt M., Nathan P. J., Phan K. L., Amygdala–frontal connectivity during
emotion regulation. Social Cognitive and Affective Neuroscience 2, 303–312 (2007). https://doi.org/
10.1093/scan/nsm029 PMID: 18985136
4.
Gross J. J., “Emotion regulation: Conceptual and empirical foundations” in Handbook of Emotion Reg-
ulation, 2nd Ed ( The Guilford Press, New York, NY, US, 2014), pp. 3–20.
5.
Barrett L. F., Lewis M., Haviland-Jones J. M., Handbook of Emotions ( Guilford Publications, 2016;
https://books.google.com/books?id=cbKhDAAAQBAJ).
6.
Elfenbein H. A., Ambady N., On the universality and cultural specificity of emotion recognition: a meta-
analysis. Psychol Bull 128, 203–235 (2002). https://doi.org/10.1037/0033-2909.128.2.203 PMID:
11931516
7.
Hareli S., Kafetsios K., Hess U., A cross-cultural study on emotion expression and the learning of
social norms. Frontiers in Psychology 6 (2015). https://doi.org/10.3389/fpsyg.2015.01501 PMID:
26483744
8.
Ford B. Q., Mauss I. B., Culture and emotion regulation. Curr Opin Psychol 3, 1–5 (2015). https://doi.
org/10.1016/j.copsyc.2014.12.004 PMID: 25729757
9.
Olderbak S., Wilhelm O., Emotion perception and empathy: An individual differences test of relations.
Emotion 17, 1092–1106 (2017). https://doi.org/10.1037/emo0000308 PMID: 28358563
10.
Lazarus R. S., Emotion and Adaptation ( Oxford University Press, 1991).
11.
Coan J. A., Handbook of Emotion Elicitation and Assessment ( Oxford University Press, New York,
NY, US, 2007)Handbook of emotion elicitation and assessment.
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
17 / 22


## Page 18

12.
LoBue V., Behavioral evidence for a continuous approach to the perception of emotionally valenced
stimuli. Behavioral and Brain Sciences 38, e79 (2015). https://doi.org/10.1017/S0140525X14000934
PMID: 26785638
13.
Greenwald M. K., Cook E. W., Lang P. J., Affective judgment and psychophysiological response:
Dimensional covariation in the evaluation of pictorial stimuli. Journal of Psychophysiology 3, 51–64
(1989).
14.
Bradley M. M., Lang P. J., Measuring emotion: The self-assessment manikin and the semantic differ-
ential. Journal of Behavior Therapy and Experimental Psychiatry 25, 49–59 (1994). https://doi.org/10.
1016/0005-7916(94)90063-9 PMID: 7962581
15.
Lang P., International affective picture system (IAPS): affective ratings of pictures and instruction man-
ual. undefined (2005).
16.
Marchewka A., Żurawski Ł., Jednoro´g K., Grabowska A., The Nencki Affective Picture System
(NAPS): Introduction to a novel, standardized, wide-range, high-quality, realistic picture database.
Behav Res 46, 596–610 (2014). https://doi.org/10.3758/s13428-013-0379-1 PMID: 23996831
17.
Canli T., Zhao Z., Desmond J. E., Kang E., Gross J., Gabrieli J. D. E., An fMRI study of personality
influences on brain reactivity to emotional stimuli. Behavioral Neuroscience 115, 33–42 (2001).
https://doi.org/10.1037/0735-7044.115.1.33 PMID: 11256451
18.
Vrticka P., Simioni S., Fornari E., Schluep M., Vuilleumier P., Sander D., Neural Substrates of Social
Emotion Regulation: A fMRI Study on Imitation and Expressive Suppression to Dynamic Facial Sig-
nals. Frontiers in Psychology 4 (2013).
19.
Re´sibois M., Verduyn P., Delaveau P., Rotge´ J.-Y., Kuppens P., Van Mechelen I., Fossati P., The neu-
ral basis of emotions varies over time: different regions go with onset- and offset-bound processes
underlying emotion intensity. Social Cognitive and Affective Neuroscience 12, 1261–1271 (2017).
https://doi.org/10.1093/scan/nsx051 PMID: 28402478
20.
Bo K., Yin S., Liu Y., Hu Z., Meyyappan S., Kim S., Keil A., Ding M., Decoding Neural Representations
of Affective Scenes in Retinotopic Visual Cortex. Cerebral Cortex 31, 3047–3063 (2021). https://doi.
org/10.1093/cercor/bhaa411 PMID: 33594428
21.
Saarima¨ki H., Naturalistic Stimuli in Affective Neuroimaging: A Review. Frontiers in Human Neurosci-
ence 15 (2021).
22.
Yamins D. L. K., Hong H., Cadieu C. F., Solomon E. A., Seibert D., DiCarlo J. J., Performance-opti-
mized hierarchical models predict neural responses in higher visual cortex. Proceedings of the
National Academy of Sciences 111, 8619–8624 (2014). https://doi.org/10.1073/pnas.1403112111
PMID: 24812127
23.
Gu¨c¸lu¨ U., van Gerven M. A. J., Deep Neural Networks Reveal a Gradient in the Complexity of Neural
Representations across the Ventral Stream. J. Neurosci. 35, 10005–10014 (2015). https://doi.org/10.
1523/JNEUROSCI.5023-14.2015 PMID: 26157000
24.
Yamins D. L. K., DiCarlo J. J., Using goal-driven deep learning models to understand sensory cortex.
Nat Neurosci 19, 356–365 (2016). https://doi.org/10.1038/nn.4244 PMID: 26906502
25.
Marblestone A. H., Wayne G., Kording K. P., Toward an Integration of Deep Learning and Neurosci-
ence. Front. Comput. Neurosci. 10 (2016). https://doi.org/10.3389/fncom.2016.00094 PMID:
27683554
26.
Richards B. A., Lillicrap T. P., Beaudoin P., Bengio Y., Bogacz R., Christensen A., Clopath C., Costa
R. P., de Berker A., Ganguli S., Gillon C. J., Hafner D., Kepecs A., Kriegeskorte N., Latham P., Lindsay
G. W., Miller K. D., Naud R., Pack C. C., Poirazi P., Roelfsema P., Sacramento J., Saxe A., Scellier B.,
Schapiro A. C., Senn W., Wayne G., Yamins D., Zenke F., Zylberberg J., Therien D., Kording K. P., A
deep learning framework for neuroscience. Nat Neurosci 22, 1761–1770 (2019). https://doi.org/10.
1038/s41593-019-0520-2 PMID: 31659335
27.
Deng J., Dong W., Socher R., Li L., Li Kai, Fei-Fei Li, “ImageNet: A large-scale hierarchical image
database” in 2009 IEEE Conference on Computer Vision and Pattern Recognition (2009), pp. 248–
255.
28.
Nasr K., Viswanathan P., Nieder A., Number detectors spontaneously emerge in a deep neural net-
work designed for visual object recognition. Science Advances 5, eaav7903 (2019).
29.
Dobs K., Kell A., Martinez J., Cohen M., Kanwisher N., Kanwisher N., Why Are Face and Object Pro-
cessing Segregated in the Human Brain? Testing Computational Hypotheses with Deep Convolutional
Neural Networks (2020).
30.
Vuilleumier P., Richardson M. P., Armony J. L., Driver J., Dolan R. J., Distant influences of amygdala
lesion on visual cortical activation during emotional face processing. Nat Neurosci 7, 1271–1278
(2004). https://doi.org/10.1038/nn1341 PMID: 15494727
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
18 / 22


## Page 19

31.
Shuler M. G., Bear M. F., Reward Timing in the Primary Visual Cortex. Science 311, 1606–1609
(2006). https://doi.org/10.1126/science.1123513 PMID: 16543459
32.
Kragel P. A., Reddan M. C., LaBar K. S., Wager T. D., Emotion schemas are embedded in the human
visual system. Science Advances 5, eaaw4358 (2019). https://doi.org/10.1126/sciadv.aaw4358
PMID: 31355334
33.
K. Simonyan, A. Zisserman, Very Deep Convolutional Networks for Large-Scale Image Recognition.
arXiv:1409.1556 [cs] (2015).
34.
Russakovsky O., Deng J., Su H., Krause J., Satheesh S., Ma S., Huang Z., Karpathy A., Khosla A.,
Bernstein M., Berg A. C., Fei-Fei L., ImageNet Large Scale Visual Recognition Challenge. Int J Com-
put Vis 115, 211–252 (2015).
35.
Seeliger K., Fritsche M., Gu¨c¸lu¨ U., Schoenmakers S., Schoffelen J.-M., Bosch S. E., van Gerven M. A.
J., Convolutional neural network-based encoding and decoding of visual object recognition in space
and time. NeuroImage 180, 253–266 (2018). https://doi.org/10.1016/j.neuroimage.2017.07.018
PMID: 28723578
36.
Jacob G., Pramod R. T., Katti H., Arun S. P., Qualitative similarities and differences in visual object
representations between brains and deep networks. Nat Commun 12, 1872 (2021). https://doi.org/10.
1038/s41467-021-22078-3 PMID: 33767141
37.
Thompson P., Margaret Thatcher: A New Illusion. Perception 9, 483–484 (1980).
38.
Sowden P. T., “Psychophysics” in APA Handbook of Research Methods in Psychology, Vol 1: Founda-
tions, Planning, Measures, and Psychometrics ( American Psychological Association, Washington,
DC, US, 2012)APA handbooks in psychology®, pp. 445–458.
39.
Krizhevsky A., Sutskever I., Hinton G. E., ImageNet classification with deep convolutional neural net-
works. Commun. ACM 60, 84–90 (2017).
40.
Zeiler M. D., Fergus R., “Visualizing and Understanding Convolutional Networks” in Computer Vision–
ECCV 2014, Fleet D., Pajdla T., Schiele B., Tuytelaars T., Eds. ( Springer International Publishing,
Cham, 2014), pp. 818–833.
41.
G. Lee, Y.-W. Tai, J. Kim, Deep Saliency with Encoded Low level Distance Map and High Level Fea-
tures. arXiv:1604.05495 [cs] (2016).
42.
Lindsay G. W., Convolutional Neural Networks as a Model of the Visual System: Past, Present, and
Future. Journal of Cognitive Neuroscience, 1–15 (2020).
43.
Lindsay G. W., Miller K. D., How biological attention mechanisms improve task performance in a large-
scale visual system model. eLife 7, e38105 (2018). https://doi.org/10.7554/eLife.38105 PMID:
30272560
44.
Maunsell J. H. R., Treue S., Feature-based attention in visual cortex. Trends in Neurosciences 29,
317–322 (2006). https://doi.org/10.1016/j.tins.2006.04.001 PMID: 16697058
45.
G. W. Lindsay, Feature-based Attention in Convolutional Neural Networks. arXiv:1511.06408 [cs]
(2015).
46.
Yeh C.-H., Lin M.-H., Chang P.-C., Kang L.-W., Enhanced Visual Attention-Guided Deep Neural Net-
works for Image Classification. IEEE Access 8, 163447–163457 (2020).
47.
Cardin J. A., Palmer L. A., Contreras D., Cellular mechanisms underlying stimulus-dependent gain
modulation in primary visual cortex neurons in vivo. Neuron 59, 150–160 (2008). https://doi.org/10.
1016/j.neuron.2008.05.002 PMID: 18614036
48.
Eldar E., Cohen J. D., Niv Y., The effects of neural gain on attention and learning. Nat Neurosci 16,
1146–1153 (2013). https://doi.org/10.1038/nn.3428 PMID: 23770566
49.
Jarvis S., Nikolic K., Schultz S. R., Neuronal gain modulability is determined by dendritic morphology:
A computational optogenetic study. PLOS Computational Biology 14, e1006027 (2018). https://doi.
org/10.1371/journal.pcbi.1006027 PMID: 29522509
50.
H. Bos, A.-M. Oswald, B. Doiron, Untangling stability and gain modulation in cortical circuits with multi-
ple interneuron classes. bioRxiv [Preprint] (2020). https://doi.org/10.1101/2020.06.15.148114.
51.
Aharonov R., Segev L., Meilijson I., Ruppin E., Localization of Function via Lesion Analysis. Neural
Computation 15, 885–913 (2003). https://doi.org/10.1162/08997660360581949 PMID: 12689391
52.
Chareyron L. J., Amaral D. G., Lavenex P., Selective lesion of the hippocampus increases the differen-
tiation of immature neurons in the monkey amygdala. Proceedings of the National Academy of Sci-
ences 113, 14420–14425 (2016). https://doi.org/10.1073/pnas.1604288113 PMID: 27911768
53.
Yang G. R., Joglekar M. R., Song H. F., Newsome W. T., Wang X.-J., Task representations in neural
networks trained to perform many cognitive tasks. Nat Neurosci 22, 297–306 (2019). https://doi.org/
10.1038/s41593-018-0310-2 PMID: 30643294
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
19 / 22


## Page 20

54.
Cohen-Zimerman S., Khilwani H., Smith G. N. L., Krueger F., Gordon B., Grafman J., The neural basis
for mental state attribution: A voxel-based lesion mapping study. Human Brain Mapping 42, 65–79
(2021). https://doi.org/10.1002/hbm.25203 PMID: 33030812
55.
Lang P. J., Bradley M. M., Cuthbert B. N., “Motivated attention: Affect, activation, and action” in Atten-
tion and Orienting: Sensory and Motivational Processes ( Lawrence Erlbaum Associates Publishers,
Mahwah, NJ, US, 1997), pp. 97–135.
56.
Kriegeskorte N., Deep Neural Networks: A New Framework for Modeling Biological Vision and Brain
Information Processing. Annual Review of Vision Science 1, 417–446 (2015). https://doi.org/10.1146/
annurev-vision-082114-035447 PMID: 28532370
57.
Brachmann A., Barth E., Redies C., Using CNN Features to Better Understand What Makes Visual
Artworks Special. Frontiers in Psychology 8 (2017). https://doi.org/10.3389/fpsyg.2017.00830 PMID:
28588537
58.
Iigaya K., Yi S., Wahle I. A., Tanwisuth K., O’Doherty J. P., Aesthetic preference for art can be pre-
dicted from a mixture of low- and high-level visual features. Nat Hum Behav 5, 743–755 (2021).
https://doi.org/10.1038/s41562-021-01124-6 PMID: 34017097
59.
van Dyck L. E., Kwitt R., Denzler S. J., Gruber W. R., Comparing Object Recognition in Humans and
Deep Convolutional Neural Networks—An Eye Tracking Study. Frontiers in Neuroscience 15 (2021).
https://doi.org/10.3389/fnins.2021.750639 PMID: 34690686
60.
Singer J. J. D., Seeliger K., Kietzmann T. C., Hebart M. N., From photos to sketches—how humans
and deep neural networks process objects across different levels of visual abstraction. Journal of
Vision 22, 4 (2022). https://doi.org/10.1167/jov.22.2.4 PMID: 35129578
61.
Lee J., Jung M., Lustig N., Lee J.-H., Neural representations of the perception of handwritten digits
and visual objects from a convolutional neural network compared to humans. Human Brain Mapping
n/a (2023). https://doi.org/10.1002/hbm.26189 PMID: 36637109
62.
Kaurama¨ki J., Ja¨a¨skela¨inen I. P., Sams M., Selective Attention Increases Both Gain and Feature
Selectivity of the Human Auditory Cortex. PLOS ONE 2, e909 (2007). https://doi.org/10.1371/journal.
pone.0000909 PMID: 17878944
63.
Moldakarimov S., Bazhenov M., Sejnowski T. J., Top-Down Inputs Enhance Orientation Selectivity in
Neurons of the Primary Visual Cortex during Perceptual Learning. PLOS Computational Biology 10,
e1003770 (2014). https://doi.org/10.1371/journal.pcbi.1003770 PMID: 25121603
64.
Pasternak T., Tadin D., Linking Neuronal Direction Selectivity to Perceptual Decisions About Visual
Motion. Annu Rev Vis Sci 6, 335–362 (2020). https://doi.org/10.1146/annurev-vision-121219-081816
PMID: 32936737
65.
Kubilius J., Schrimpf M., Kar K., Rajalingham R., Hong H., Majaj N. J., Issa E. B., Bashivan P., Pres-
cott-Roy J., Schmidt K., Nayebi A., Bear D., Yamins D. L. K., DiCarlo J. J., “Brain-like object recogni-
tion with high-performing shallow recurrent ANNs” in Proceedings of the 33rd International
Conference on Neural Information Processing Systems (Curran Associates Inc., Red Hook, NY, USA,
2019), pp. 12805–12816.
66.
Rose O., Johnson J., Wang B., Ponce C. R., Visual prototypes in the ventral stream are attuned to
complexity and gaze behavior. Nat Commun 12, 6723 (2021). https://doi.org/10.1038/s41467-021-
27027-8 PMID: 34795262
67.
Zhuang C., Yan S., Nayebi A., Schrimpf M., Frank M. C., DiCarlo J. J., Yamins D. L. K., Unsupervised
neural network models of the ventral visual stream. Proc Natl Acad Sci USA 118, e2014196118
(2021). https://doi.org/10.1073/pnas.2014196118 PMID: 33431673
68.
Bonnen T., Yamins D. L. K., Wagner A. D., When the ventral visual stream is not enough: A deep
learning account of medial temporal lobe involvement in perception. Neuron 109, 2755–2766.e6
(2021). https://doi.org/10.1016/j.neuron.2021.06.018 PMID: 34265252
69.
Lang P. J., Bradley M. M., Fitzsimmons J. R., Cuthbert B. N., Scott J. D., Moulder B., Nangia V., Emo-
tional arousal and activation of the visual cortex: An fMRI analysis. Psychophysiology 35, 199–210
(1998). PMID: 9529946
70.
Rotshtein P., Malach R., Hadar U., Graif M., Hendler T., Feeling or Features: Different Sensitivity to
Emotion in High-Order Visual Cortex and Amygdala. Neuron 32, 747–757 (2001). https://doi.org/10.
1016/s0896-6273(01)00513-x PMID: 11719213
71.
Schupp H. T., Markus J., Weike A. I., Hamm A. O., Emotional Facilitation of Sensory Processing in the
Visual Cortex. Psychol Sci 14, 7–13 (2003). https://doi.org/10.1111/1467-9280.01411 PMID:
12564747
72.
Sabatinelli D., Bradley M. M., Fitzsimmons J. R., Lang P. J., Parallel amygdala and inferotemporal acti-
vation reflect emotional intensity and fear relevance. Neuroimage 24, 1265–1270 (2005). https://doi.
org/10.1016/j.neuroimage.2004.12.015 PMID: 15670706
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
20 / 22


## Page 21

73.
Lang P. J., Bradley M. M., Emotion and the motivational brain. Biol Psychol 84, 437–450 (2010).
https://doi.org/10.1016/j.biopsycho.2009.10.007 PMID: 19879918
74.
Pessoa L., Emotion and Cognition and the Amygdala: From “what is it?” to “what’s to be done?” Neu-
ropsychologia 48, 3416–3429 (2010). https://doi.org/10.1016/j.neuropsychologia.2010.06.038 PMID:
20619280
75.
Miskovic V., Anderson A. K., Modality general and modality specific coding of hedonic valence. Curr
Opin Behav Sci 19, 91–97 (2018). https://doi.org/10.1016/j.cobeha.2017.12.012 PMID: 29967806
76.
Weinberger N. M., Specific long-term memory traces in primary auditory cortex. Nat Rev Neurosci 5,
279–290 (2004). https://doi.org/10.1038/nrn1366 PMID: 15034553
77.
Li Z., Yan A., Guo K., Li W., Fear-Related Signals in the Primary Visual Cortex. Curr Biol 29, 4078–
4083.e2 (2019). https://doi.org/10.1016/j.cub.2019.09.063 PMID: 31668624
78.
Thigpen N. N., Bartsch F., Keil A., The malleability of emotional perception: Short-term plasticity in reti-
notopic neurons accompanies the formation of perceptual biases to threat. Journal of Experimental
Psychology: General 146, 464–471 (2017). https://doi.org/10.1037/xge0000283 PMID: 28383987
79.
Miskovic V., Keil A., Acquired fears reflected in cortical sensory processing: A review of electrophysio-
logical studies of human classical conditioning. Psychophysiology 49, 1230–1241 (2012). https://doi.
org/10.1111/j.1469-8986.2012.01398.x PMID: 22891639
80.
Baek S., Song M., Jang J., Kim G., Paik S.-B., Face detection in untrained deep neural networks. Nat
Commun 12, 7328 (2021). https://doi.org/10.1038/s41467-021-27606-9 PMID: 34916514
81.
Burr D., Ross J., A Visual Sense of Number. Current Biology 18, 425–428 (2008). https://doi.org/10.
1016/j.cub.2008.02.052 PMID: 18342507
82.
Nieder A., The neuronal code for number. Nat Rev Neurosci 17, 366–382 (2016). https://doi.org/10.
1038/nrn.2016.40 PMID: 27150407
83.
Xu F., Spelke E. S., Large number discrimination in 6-month-old infants. Cognition 74, B1–B11
(2000). https://doi.org/10.1016/s0010-0277(99)00066-9 PMID: 10594312
84.
Xu F., Spelke E. S., Goddard S., Number sense in human infants. Dev Sci 8, 88–101 (2005). https://
doi.org/10.1111/j.1467-7687.2005.00395.x PMID: 15647069
85.
Santens S., Roggeman C., Fias W., Verguts T., Number Processing Pathways in Human Parietal Cor-
tex. Cerebral Cortex 20, 77–88 (2010). https://doi.org/10.1093/cercor/bhp080 PMID: 19429864
86.
Hauser M. D., Carey S., Hauser L. B., Spontaneous number representation in semi-free-ranging rhe-
sus monkeys. Proc Biol Sci 267, 829–833 (2000). https://doi.org/10.1098/rspb.2000.1078 PMID:
10819154
87.
Sawamura H., Shima K., Tanji J., Numerical representation for action in the parietal cortex of the mon-
key. Nature 415, 918–922 (2002). https://doi.org/10.1038/415918a PMID: 11859371
88.
Hauser M. D., Tsao F., Garcia P., Spelke E. S., Evolutionary foundations of number: spontaneous
representation of numerical magnitudes by cotton–top tamarins. Proceedings of the Royal Society of
London. Series B: Biological Sciences 270, 1441–1446 (2003). https://doi.org/10.1098/rspb.2003.
2414 PMID: 12965007
89.
Nasr K., Viswanathan P., Nieder A., Number detectors spontaneously emerge in a deep neural net-
work designed for visual object recognition. Science Advances 5, eaav7903.
90.
Kim G., Jang J., Baek S., Song M., Paik S.-B., Visual number sense in untrained deep neural net-
works. Science Advances 7, eabd6127 (2021). https://doi.org/10.1126/sciadv.abd6127 PMID:
33523851
91.
Kanwisher N., McDermott J., Chun M. M., The Fusiform Face Area: A Module in Human Extrastriate
Cortex Specialized for Face Perception. J. Neurosci. 17, 4302–4311 (1997). https://doi.org/10.1523/
JNEUROSCI.17-11-04302.1997 PMID: 9151747
92.
Dobs K., Martinez J., Kell A. J. E., Kanwisher N., Brain-like functional specialization emerges sponta-
neously in deep neural networks. Science Advances 8, eabl8913 (2022). https://doi.org/10.1126/
sciadv.abl8913 PMID: 35294241
93.
C. Zhang, S. Bengio, M. Hardt, B. Recht, O. Vinyals, Understanding deep learning requires rethinking
generalization. arXiv:1611.03530 [cs] (2017).
94.
VanRullen R., Thorpe S. J., The time course of visual processing: from early perception to decision-
making. J Cogn Neurosci 13, 454–461 (2001). https://doi.org/10.1162/08989290152001880 PMID:
11388919
95.
Srinivasan N., Gupta R., Rapid communication: Global-local processing affects recognition of distrac-
tor emotional faces. Q J Exp Psychol (Hove) 64, 425–433 (2011). https://doi.org/10.1080/17470218.
2011.552981 PMID: 21347993
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
21 / 22


## Page 22

96.
Cabral L., Stojanoski B., Cusack R., Rapid and coarse face detection: With a lack of evidence for a
nasal-temporal asymmetry. Atten Percept Psychophys 82, 1883–1895 (2020). https://doi.org/10.
3758/s13414-019-01877-3 PMID: 31907838
97.
Zipser K., Lamme V. A. F., Schiller P. H., Contextual Modulation in Primary Visual Cortex. J. Neurosci.
16, 7376–7389 (1996). https://doi.org/10.1523/JNEUROSCI.16-22-07376.1996 PMID: 8929444
98.
Tschechne S., Neumann H., Hierarchical representation of shapes in visual cortex—from localized
features to figural shape segregation. Front Comput Neurosci 8, 93 (2014). https://doi.org/10.3389/
fncom.2014.00093 PMID: 25157228
99.
Willems R. M., Peelen M. V., How context changes the neural basis of perception and language.
iScience 24, 102392 (2021). https://doi.org/10.1016/j.isci.2021.102392 PMID: 33997677
100.
Bradley M. M., Lang P. J., Affective reactions to acoustic stimuli. Psychophysiology 37, 204–215
(2000). PMID: 10731770
101.
Harmon-Jones E., Gable P. A., Peterson C. K., The role of asymmetric frontal cortical activity in emo-
tion-related phenomena: A review and update. Biological Psychology 84, 451–462 (2010). https://doi.
org/10.1016/j.biopsycho.2009.08.010 PMID: 19733618
102.
Niedenthal P. M., Wood A., Does emotion influence visual perception? Depends on how you look at it.
Cognition and Emotion 33, 77–84 (2019). https://doi.org/10.1080/02699931.2018.1561424 PMID:
30636535
103.
Li G., Forero M. G., Wentzell J. S., Durmus I., Wolf R., Anthoney N. C., Parker M., Jiang R., Hasenauer
J., Strausfeld N. J., Heisenberg M., Hidalgo A., A Toll-receptor map underlies structural brain plasticity.
eLife 9, e52743 (2020). https://doi.org/10.7554/eLife.52743 PMID: 32066523
104.
Tierney A. L., Nelson C. A., Brain Development and the Role of Experience in the Early Years. Zero
Three 30, 9–13 (2009). PMID: 23894221
105.
Oliva A., Torralba A., Modeling the Shape of the Scene: A Holistic Representation of the Spatial Enve-
lope. International Journal of Computer Vision 42, 145–175 (2001).
106.
Cortes C., Vapnik V., Support-vector networks. Mach Learn 20, 273–297 (1995).
107.
Tiago Marques, Martin Schrimpf, James J. DiCarlo, Multi-scale hierarchical neural network models
that bridge from single neurons in the primate primary visual cortex to object recognition behavior.
bioRxiv, 2021.03.01.433495 (2021).
108.
Ratan Murty N. A., Bashivan P., Abate A., DiCarlo J. J., Kanwisher N., Computational models of cate-
gory-selective brain regions enable high-throughput tests of selectivity. Nat Commun 12, 5540 (2021).
https://doi.org/10.1038/s41467-021-25409-6 PMID: 34545079
109.
Uran C., Peter A., Lazar A., Barnes W., Klon-Lipok J., Shapcott K. A., Roese R., Fries P., Singer W.,
Vinck M., Predictive coding of natural images by V1 firing rates and rhythmic synchronization. Neuron
110, 1240–1257.e8 (2022). https://doi.org/10.1016/j.neuron.2022.01.002 PMID: 35120628
110.
Sato W., Kochiyama T., Yoshikawa S., Naito E., Matsumura M., Enhanced neural activity in response
to dynamic facial expressions of emotion: an fMRI study. Brain Res Cogn Brain Res 20, 81–91
(2004). https://doi.org/10.1016/j.cogbrainres.2004.01.008 PMID: 15130592
111.
Cichy R. M., Pantazis D., Oliva A., Resolving human object recognition in space and time. Nat Neu-
rosci 17, 455–462 (2014). https://doi.org/10.1038/nn.3635 PMID: 24464044
112.
Putnam P. T., Gothard K. M., Multidimensional Neural Selectivity in the Primate Amygdala. eNeuro 6
(2019). https://doi.org/10.1523/ENEURO.0153-19.2019 PMID: 31533960
113.
Cadieu C. F., Hong H., Yamins D. L. K., Pinto N., Ardila D., Solomon E. A., Majaj N. J., DiCarlo J. J.,
Deep Neural Networks Rival the Representation of Primate IT Cortex for Core Visual Object Recogni-
tion. PLOS Computational Biology 10, e1003963 (2014). https://doi.org/10.1371/journal.pcbi.
1003963 PMID: 25521294
114.
Cichy R. M., Khosla A., Pantazis D., Torralba A., Oliva A., Comparison of deep neural networks to spa-
tio-temporal cortical dynamics of human visual object recognition reveals hierarchical correspon-
dence. Sci Rep 6, 27755 (2016). https://doi.org/10.1038/srep27755 PMID: 27282108
115.
Eickenberg M., Gramfort A., Varoquaux G., Thirion B., Seeing it all: Convolutional network layers map
the function of the human visual system. NeuroImage 152, 184–194 (2017). https://doi.org/10.1016/j.
neuroimage.2016.10.001 PMID: 27777172
116.
H. Lee, E. Margalit, K. M. Jozwik, M. A. Cohen, N. Kanwisher, D. L. K. Yamins, J. J. DiCarlo, Topo-
graphic deep artificial neural networks reproduce the hallmarks of the primate inferior temporal cortex
face processing network. bioRxiv, 2020.07.09.185116 (2020).
PLOS COMPUTATIONAL BIOLOGY
Emotion selectivity in deep neural networks
PLOS Computational Biology | https://doi.org/10.1371/journal.pcbi.1011943
March 28, 2024
22 / 22


