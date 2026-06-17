# (2024) Bridging Discrete and Continuous A Multimodal Strategy for Complex Emotion Detection

**Source:** (2024) Bridging Discrete and Continuous A Multimodal Strategy for Complex Emotion Detection.pdf

---

## Page 1

1
Bridging Discrete and Continuous: A Multimodal Strategy for
Complex Emotion Detection
Jiehui Jia
Huan Zhang
Jinhua Liang
Queen Mary University of London , Centre for Digital Music, London, United Kingdom
jessiejia27@gmail.com, jinhua.liang@qmul.ac.uk
Abstract—In the domain of human-computer interaction, accurately
recognizing and interpreting human emotions is crucial yet challenging due
to the complexity and subtlety of emotional expressions. This study explores
the potential for detecting a rich and flexible range of emotions through a
multimodal approach which integrates facial expressions, voice tones, and
transcript from video clips. We propose a novel framework that maps
variety of emotions in a three-dimensional Valence-Arousal-Dominance
(VAD) space, which could reflect the fluctuations and positivity/negativity
of emotions to enable a more variety and comprehensive representation
of emotional states. We employed K-means clustering to transit emotions
from traditional discrete categorization to a continuous labeling system and
built a classifier for emotion recognition upon this system. The effectiveness
of the proposed model is evaluated using the MER2024 dataset, which
contains culturally consistent video clips from Chinese movies and TV
series, annotated with both discrete and open-vocabulary emotion labels.
Our experiment successfully achieved the transformation between discrete
and continuous models, and the proposed model generated a more diverse
and comprehensive set of emotion vocabulary while maintaining strong
accuracy.
Index Terms—Multimodal emotion recognition, Emotional variability,
Valence-Arousal-Dominance (VAD) framework, Machine learning in
emotion detection
I. INTRODUCTION
Human emotions are complex and described through diverse
vocabularies across languages, reflecting our thoughts, feelings, and
reactions via facial expressions, body language, voice tone, and
speech. [1]. Accurate comprehension and response to human emotions
by machines can significantly benefit areas such as marketing, music,
mental health monitoring, and human-computer interaction [2]–[5].
Thus, developing systems capable of precisely identifying varieties of
human emotions is essential.
However, the challenge in emotion detection lies in the subjective
nature of emotions. It is hard to set a clear boundary to categorize
emotions, so as to choose a ‘basic’ emotion group [6]. Moreover,
emotion datasets vary in their annotation schemes (e.g., differing
discrete labels) and domains, hindering direct comparisons across
previous works. These variations restrict prior research to specific data
sources, limiting their generalizability to real-world applications [7].
Recognizing the challenges, this paper proposes a multimodal
framework that transforms different discrete emotion labels into one
continuous emotion label framework. We propose to use a fixed
emotion Valence, Arousal, and Dominance rating scale to standardize
the scoring of a variety of emotion labels in a multidimensional
space. By using K-means clustering, we build a classifier which could
transit discrete emotion with continuous emotions which suits both
close-set and open set emotion recognition. In our case, we grouped
the emotion labels into six clusters based on the six basic emotion
labels which been annotated for the dataset we chosen. We built a
multimodal model that integrates facial expressions, voice tones, and
transcript from video clips to predict the Valence-Arousal-Dominance
(VAD) scores of the emotions. Finally the VAD score was mapped
back to the original emotion labels for evaluation. We also generated
open-vocabulary emotional responses from discrete emotion inputs
Fig. 1: Emotion Vocabularies in 3D VAD Space
to explore the possibility of a more dynamic and adaptable emotion
recognition system.
The experimental results demonstrate that the framework success-
fully achieved the transformation between discrete and continuous
models. By comparing their evaluation metrics, we conclude that the
proposed framework performs the transformation with a comparable
level of accuracy. We also compared the similarity score between
the generated open emotion vocabulary set and the original dataset’s
open set, achieving a high score that indicates significant semantic
overlap. This shows that our model can reliably produce a nuanced
and flexible emotion vocabulary, which could be effectively applied
to tasks requiring more detailed emotion recognition and analysis.
The contribution of this paper is summarized as follows:
• We introduce a multimodal system that aligns with human
perception by mapping emotions into a continuous hidden space.
The proposed framework outperforms existing classifier in the
close-set dataset.
• We incorporate VAD rating system with an emotion classifier,
which learns a more nuance representation of emotion states than
learning from discrete categories.
• We benchmark the open-set emotion classification task by
applying the wav2vec model. Experiments demonstrate a high
correlation between the ground truth and our proposed model.
II. RELATED WORK
Multimodal emotion detection methods primarily differ in two key
areas: the approaches to categorizing and measuring emotions, and
the techniques used to extract and integrate features from various
modalities.
A. The measurement of emotion
There are two main approaches to measuring emotions: the discrete
method and the multidimensional approach [8]. The discrete method
classifies emotions into a few fundamental categories believed to be
universal. Proponents argue that combinations of these basic emotions
arXiv:2409.07901v1  [cs.MM]  12 Sep 2024


## Page 2

2
can explain complex emotional states. For instance, fear, surprise,
happiness, disgust, anger, and sadness has been identified as the six
basic emotions [9].
Building upon these basic feelings, a thorough emotional model
known as Plutchik’s wheel of emotions has been developed [10],
which consists of eight main emotions. It is believed that different
intensities of these main emotions might mix to create additional
related feelings. Studies have been conducted on dataset with 15
Compound emotion mixed with two basic emotions and 7 Basic facial
emotions as a way for compound emotion detection [11]. In some
situations, the discrete method works well enough with a simplified
emotional assessment [12], [13]. For example, when it comes to
driving systems in vehicles, determining a driver’s stress level can
be accomplished by concentrating just on the most fundamentally
feelings, like anger and happiness [13].
The multidimensional approach, on the other hand, uses continuous
dimensions—valence, arousal, and sometimes dominance—to map
emotions. Valence measures positivity or negativity, arousal indicates
the level of activity, and dominance reflects control over the emotional
state [14]. This creates a nuanced two- or three-dimensional emotional
space, often referred to as the circumplex model of affect [15].
B. Multimodal Emotion Detection
Multimodal methods have been widely chosen in research because
they can extract features from various modalities [16]–[19]. While
basic emotions like happy or angry are readily expressed through body
language or facial expressions, complex emotions such as jealousy,
pride, or hope require additional context and language for accurate in-
terpretation [16]. Multimodal methods are thus preferable to unimodal
ones for recognizing such emotions. This approach allows researchers
to analyze data from different sources—such as visual, audio, and
textual inputs—in ways that enhance the accuracy and robustness
of emotion detection systems. By utilizing these different streams
of information, multimodal methods capture a more comprehensive
understanding of emotional states, accommodating variations and
subtleties that might be missed by unimodal approaches [17].
Visual, audio, and textual features are captured separately using
different methods. Visual features primarily focus on facial expres-
sions, which can be seen as facial muscle movements. The Facial
Action Coding System (FACS) [20] has been developed to manually
code facial expressions using action units (AUs) based on specific
muscle movements. Inspired by their work, many researchers have
utilized image and video processing to analyze and categorize facial
expressions by tracking features and measuring movement, applying
these methods to the “basic expressions” identified in multimodal
emotion studies [21]–[24]. Similar to other audio domains [25]–[27],
emotion-related features consist of two main categories: linguistic
information, which pertains to the content of speech, and paralinguistic
information, which captures emotions through the tone and manner of
delivery [28]. In addition to commonly used models like CNN, RNN,
and LSTM [29], [30], other approaches also make promising prediction.
For instance, the use of features such as mel-frequency cepstral
coefficient (MFCC), perceptual linear prediction coefficient (PLPC),
and perceptual minimum variance distortionless response (PMVDR)
coefficient [31] . Textual emotions are expressed through speech and
can be abstract by transcripts. Traditional techniques such as the bag-
of-words (BoW) model [32], [33] have been commonly used. Then
word embedding methods like tf-idf, word2vec [34] and GloVe [35]
were based mainly on syntactic contexts. For handling larger text,
BERT (Bidirectional Encoder Representations from Transformers) uses
transformer-based encoders that assess both preceding and subsequent
contexts to better predict words in sentences [36].
III. METHODOLOGY
The project aims to bridge discrete and continuous emotion systems,
using a multimodal model to detect emotions and produce more
nuanced emotion labels beyond the basic six. This approach allows
for working with diverse datasets and improves the variety and depth
of emotion detection.
We first transformed discrete emotion labels into continuous emotion
labels, then applied and refined several models for the task. The first
model, Multimodal End-to-End Sparse Model (ME2E) [37], is a
multimodal emotion detection model that uses discrete emotion labels
as input and outputs corresponding discrete emotions, serving as our
baseline. The second, ME2E Lite model, a refined version of ME2E
to better align with our dataset for improved performance. The third,
Proposed VAD, builds on the ME2E Lite pipeline but uses 3D VAD
score as input, outputting continuous VAD scores that can be mapped
to discrete emotions while also generating a broader range of nuanced
emotion vocabularies.
A. The K-means clustering classifier - Transformation between discrete
emotion labels and continuous emotion labels
To transition from discrete to multidimensional emotion methods,
we developed a classifier that enables the transformation between dis-
crete and continuous emotion labels using the NRC-VAD lexicon [38].
We extracted 195 emotion vocabularies with assigned VAD scores
from the 20,000-vocabularies NRC-VAD lexicon, using the polar term
based on a -1 to 1 scale, as taking the absolute values of these scores
is likely to yield better features than those derived from a 0 to 1 scale.
The six basic emotions selected—happy, sad, worried, surprised, angry,
and neutral—align with the categories used in our dataset. As VAD
scores are available for all selected basic emotions except neutral,
we assigned a VAD score of (0,0,0) to neutral, reflecting a lack of
significant emotional fluctuations typically associated with this state.
At this stage, each basic emotion can be transformed into a 3D
VAD score, but to enable the inversion from the continuous emotions
to discrete labels, we employed a K-means clustering classifier. By
setting k to 6, the classifier is configured to convert continuous VAD
scores back into six basic emotion categories.
To build the emotion classifier, we first mapped the 195 extracted
emotion vocabularies, along with their associated VAD scores, into
a 3D emotion space. The six basic emotions—happy, sad, worried,
surprised, angry, and neutral—were set as the initial cluster centers.
We then set the number of clusters to six, corresponding to the number
of basic emotions.
The underlying assumption is that people experiencing similar
emotions will exhibit similar VAD scores, meaning their emotional
reactions should cluster closely in the VAD space. By applying K-
means clustering, we grouped these similar emotions into clusters.
Each cluster represents a collection of VAD scores that align with one
of the basic emotions. After clustering, the centroid of each cluster
corresponds to a discrete emotion, allowing us to map continuous
VAD scores back to a specific emotion category.
This approach effectively allows us to bridge continuous and discrete
emotional labels, with the results of the clustering visualized in
Figure 1 and Table I, demonstrating how similar emotions are grouped
together based on their VAD scores.
B. ME2E - Baseline Model
The ME2E model processes data from video, audio, and text
modalities. Facial features are extracted from video frames using the
MTCNN model from FaceNet [39], while both these facial features
and audio spectrograms are then processed through convolutional
layers. These features are further analyzed using a Transformer [40]


## Page 3

3
Fig. 2: VAD Model Pipline
TABLE I: Emotion Clustering
Emotion Name
Sampled Emotion in Cluster
Happy
delighted, inspired, glad, humorous, cheerful
Sad
fatigued, mournful, vulnerable, doubtful, regretful
Worried
guilty, offended, wounded, annoyed, frightened
Neutral
kind, warm, thoughtful, sympathetic, humble
Surprised
emotional, elated, expectant, curious, impressed
Angry
grumpy, vengeful, moody, offended, frantic
to capture temporal and contextual nuances. Text data is processed
through ALBERT [41], which optimized for short sentences and
requiring fewer parameters than BERT. Finally, features from each
modality are individually processed and merged via a weighted fusion
mechanism, producing a final emotion prediction across six possible
outcomes: happy, angry, sad, neutral, worried, or surprised.
C. ME2E Lite - The refined Model
Building on the work of [37], we revised the architecture in our
ME2E Lite model by replacing the original 11-layer CNN+VGG
video path with AlexNet [42], and simplified the audio path’s CNN by
removing one VGG layer, effectively halving the processed parameters
to better suit our smaller dataset.
D. Proposed VAD Model – The model bridges the gap between
discrete and continuous emotions
The proposed VAD model shown in Figure 2 uses VAD scores as
input, making it compatible with both continuous labels and discrete
emotions which been represented by VAD scores using the NRC-VAD
lexicon. We employed the same pipeline as ME2E Lite but replaced
the softmax function with mean squared error (MSE) as the loss
function. The model features a fully connected layer that directly
outputs three continuous values corresponding to the VAD dimensions
This model independently processes each of these dimensions by
predicting the distribution for valence, arousal, and dominance, then
identifying the most likely score for each. These predicted VAD scores
are then mapped to the K-means clustering classifier. By determining
which emotion cluster each result falls into, we can transform the
continuous VAD scores into discrete emotion labels for evaluation.
This allows for a comparison of the continuous emotion model’s
performance against the discrete emotion model. Alternatively, by
selecting the emotion close to the predicted VAD score, we can
generate a broader, open set of possible emotions, offering more
nuanced emotion representations.
IV. DATASET
We have selected the MER2024 dataset [43] for our study. This
dataset consists of raw video clips collected from Chinese movies and
TV series, ensuring cultural consistency. The raw video samples
were split into smaller video clips, each containing a complete
segment from the same character. The dataset has been labeled
with six discrete emotions: happy, angry, sad, neutral, worried, and
surprised. Additionally, there is a subset of open-vocabulary labels
and explanations [44], which allows us to evaluate a more dynamic
emotion output. Each sample contains audio data with a sampling
rate of 44.1 kHz, text transcript and video frames. The video operates
at 25 frames per second (FPS), and the frames are sampled every
500 milliseconds which result in capturing about two frames each
second.We created a dataloader to split the data into training (70%),
validation (15%), and test sets (15%).The details of our data split are
shown in Table II.
TABLE II: Dataset Distribution
Emotion
Total
Train
Val
Test
Clip Avg
Words Avg
Happy
931
538
120
113
3.51s
12.18
Angry
1100
683
141
116
3.90s
15.49
Sad
564
282
42
80
5.66s
12.70
Neutral
1142
679
153
150
3.81s
13.88
Worried
585
282
75
68
4.54s
15.23
Surprised
183
108
20
25
2.92s
8.05
V. EXPERIMENTS SETUP AND EVALUATION
For all three models, the SGD optimizer was employed. To mitigate
initial overfitting, batch normalization and dropout layers were added
after each convolution layer, coupled with ReLU activation functions
to add non-linearity. The learning rate was dynamically adjusted
during training using the CosineAnnealingLR scheduler to help the
model steer clear of local minima. The model has been trained on a
single NVIDIA Tesla V40 GPU with 48GB of memory, spanning 30
epochs and completing in about 1.2 hours.
The ME2E and ME2E Lite models We used a batch size of
32, achieving the best performance with a learning rate of 0.0001
and a weight decay of 0.005. As it is a single-label, multi-class task
for these two models, we employed the Cross-Entropy loss function,
given by L = −PN
i=1 yi log(pi), where L is the loss for an example,
N is the number of classes, yi is the binary indicator for correct
class classification, and pi is the predicted probability for class i. We
applied Softmax activation which ensures a probability distribution
over classes for classification. Evaluation metrics include precision,
recall, F1 score, and Accuracy.
The Proposed VAD model We used a batch size of 8, reaching
optimal performance with a learning rate of 0.0005 and a weight decay
of 0.0001. Since it is a continuous task, we used Mean Squared Error
(MSE) as the loss function and evaluation metric.We also evaluate us-
ing L2 distance, Mean Absolute Error (MAE), and Pearson Correlation
Coefficient (PCC) to assess the linear relationship between predictions
and actual values, where PCC =
PN
i=1(yi−µy)(ˆyi−µˆy)
√PM
i=1(yi−µy)2·√PM
i=1(ˆyi−µˆy)2 .
VI. RESULTS ANALYSIS
We have trained the baseline model, ME2E Lite model and the
proposed VAD model on the MER2024 dataset and evaluated their
performance using the metrics described above.


## Page 4

4
A. Model performance on continuous emotion detection
Table III illustrates the performance of proposed VAD model which
deals with the continuous VAD emotion labels. The L2 distance of
0.64 suggests that the model’s predictions are relatively close to the
actual values, while the MSE of 0.19 and MAE of 0.36 indicate
that the model’s predictions are generally accurate. The PCC of 0.47
further confirms that the model has learned to predict the emotional
values and has achieved a reasonable level of correlation between the
predicted and actual values.
TABLE III: Result on Continuous Emotion Detection
Model
L2 distance
MSE
MAE
PCC
Raw VAD Model
0.96
0.38
0.48
-0.01
Proposed VAD model
0.64
0.19
0.36
0.47
B. Model performance comparison on discrete emotion detection
To assess the performance on discrete emotion detection, we
transformed the continuous VAD outputs from the proposed VAD
model back into discrete emotion labels. We then evaluated these
results alongside the ME2E and ME2E Lite models using F1 score,
precision, and recall as performance metrics.
Table IV shows that the the proposed VAD model stands out with
higher precision (0.49) and recall (0.45), suggesting it is more effective
in accurately identifying and capturing emotions. ME2E Lite model
also performs well, with an F1 score of 0.42, and balanced precision
and recall at 0.42 and 0.43, respectively. The baseline ME2E model
had the lowest performance, with an F1 score of 0.33 and lower
precision and recall (both at 0.32).
While both the ME2E Lite and proposed VAD models share the
same F1 score of 0.42, the VAD model’s higher precision indicates
it predicts relevant emotions more accurately, and its higher recall
means it identifies a greater proportion of true positive emotions.
TABLE IV: Result on Discrete Emotion Detection
Model
F1
Precision
Recall
ME2E (Baseline)
0.33
0.32
0.32
ME2E Lite
0.42
0.42
0.43
Proposed VAD model
0.42
0.49
0.45
C. Open-vocabulary exploration
At the final stage of our study, we explored the possibility of
generating open-vocabulary emotional responses based on six discrete
emotion classes. For this, we utilized a subset of 68 samples from
the MER2024 dataset which contains the open-vocabulary outputs.
We then applied our proposed VAD model to this subset and mapped
the resulting VAD labels into the 3D emotion word space showed in
the Introduction.
To output the final dataset, we used an L2 distance threshold of
0.25, calculated based on the distance which could output an average
of five emotion vocabularies from our 3D Emotion Vocabulary Space.
Our finds (see supplementary material for details) indicate that our
model effectively predicts nuanced emotional states. For instance,
in Sample 00000368, the MER2024 dataset listed emotions like
’Alert,’ ’Excited,’ ’Confused,’ and ’Curious,’ and our model predicted
’Shocked.’ This aligns well as ’Shocked’ can encapsulate alertness,
excitement, and confusion. In Sample 0002419, the dataset included
’Calm,’ ’Relaxed,’ and ’Happy,’ while our model suggested ’Caring’
and ’Curious.’ These predictions are compatible, with ’Caring’
reflecting a relaxed and content state. Full output list of To further
examine the alignment of our open vocabulary, we assess the semantic
similarity across various model’s output of emotion labels.
Similarity between open-set vocabularies: We employed the pre-
trained Word2Vec model from Google News [45]. This model
enabled us to compare the word sets by converting them into vector
representations and calculating their cosine similarity based on of the
vector space embeddings.
Fig. 3: Emotion Vocabularies in 3D VAD Space
We began by assessing the similarity between EMER24’s discrete
emotion ground truth and the EMER24 OPEN emotion set, achieving a
mean similarity of approximately 0.879. This establishes a benchmark,
indicating that ideal model performance should aim for this level to
ensure consistent ground truth alignment.
We then evaluated the similarity between the EMER24 OPEN set
and the proposed VAD open set, resulting in a lower mean value of
0.85. This decrease was mainly due to outliers with a similarity of 0,
stemming from an insufficient emotion vocabulary in the 3D emotion
space affecting the VAD score distribution, due to the distribution of
emotion lexicon. Despite this, the median similarity in this comparison
is higher, illustrating a strong central tendency that supports the VAD
set’s reliability.
Lastly, we compared the EMER24 OPEN set with the ME2E
Lite model’s predictions, observing a slightly higher mean similarity
of 0.86. This suggests a marginally better alignment compared to
the VAD set, indicating that the ME2E Lite model also produces a
consistent and reliable outputs.
VII. CONCLUSION
Emotions, inherently complex, can be effectively analyzed through
a three-dimensional representation, offering a nuanced approach
to categorization adaptable to various needs and contexts. The
spatial representation within the VAD framework allows for precise,
quantitative analysis and easier conversion between different labeling
systems, enhancing our understanding of emotional expressions across
multiple modalities.
However, our study has limitations, including suboptimal model
performance and a small dataset that may hinder generalization.
The reliance on the NRC-VAD lexicon, primarily based on English,
introduces potential biases in other linguistic or cultural settings.
Future work could focus on enhancing model performance through
larger, more diverse datasets, advanced modeling techniques, and
cross-cultural adaptations to better capture the variability in emotional
expressions. Further exploration into multimodal integration and more
flexible emotion labeling could also provide deeper insights and
improve model robustness. Lastly, applying time series analysis to
track emotional shifts over time could offer valuable perspectives on
emotional dynamics.


## Page 5

5
REFERENCES
[1] R. Pally, “Emotional processing; the mind-body connection,” The
International journal of psycho-analysis, vol. 79, no. 2, p. 349, 1998.
[2] A. Esposito, A. M. Esposito, and C. Vogel, “Needs and challenges in
human computer interaction for processing social emotional information,”
Pattern Recognition Letters, vol. 66, pp. 41–51, 2015.
[3] A. Thieme, D. Belgrave, and G. Doherty, “Machine learning in mental
health: A systematic review of the hci literature to support the develop-
ment of effective and implementable ml systems,” ACM Transactions on
Computer-Human Interaction (TOCHI), vol. 27, no. 5, pp. 1–53, 2020.
[4] M. M. Mariani, R. Perez-Vega, and J. Wirtz, “Ai in marketing, consumer
research and psychology: A systematic literature review and research
agenda,” Psychology & Marketing, vol. 39, no. 4, pp. 755–776, 2022.
[5] H. Zhang, S. Chowdhury, C. E. Cancino-Chac´on, J. Liang, S. Dixon, and
G. Widmer, “Dexter: Learning and controlling performance expression
with diffusion models,” Applied Sciences, vol. 14, no. 15, 2024. [Online].
Available: https://www.mdpi.com/2076-3417/14/15/6543
[6] J. Prinz, “Which emotions are basic,” Emotion, evolution, and rationality,
vol. 69, p. 88, 2004.
[7] L. A. M. Oberl¨ander and R. Klinger, “An analysis of annotated corpora
for emotion classification in text,” in Proceedings of the 27th international
conference on computational linguistics, 2018, pp. 2104–2119.
[8] S. K. Khare, V. Blanes-Vidal, E. S. Nadimi, and U. R. Acharya, “Emotion
recognition and artificial intelligence: A systematic review (2014–2023)
and research recommendations,” Information Fusion, vol. 102, p. 102019,
2024.
[9] P. Ekman and W. V. Friesen, “Constants across cultures in the face and
emotion.” Journal of personality and social psychology, vol. 17, no. 2,
p. 124, 1971.
[10] R. Plutchik, “The nature of emotions: Human emotions have deep
evolutionary roots, a fact that may explain their complexity and provide
tools for clinical practice,” American scientist, vol. 89, no. 4, pp. 344–350,
2001.
[11] P. Heenakausar, N. Sushma, R. Sandeep, K. Lubna, and V. Saurabh,
“Compound emotions: A mixed emotion detection (may 26, 2022).”
Proceedings of the International Conference on Innovative Computing
and Communication (ICICC), 2022.
[12] A. Mitchell, E. Brown, R. Deo, Y. Hou, J. Kirton-Wingate, J. Liang,
A. Sheinkman, C. Soelistyo, H. Sood, A. Wongprommoon, K. Xing,
W. Yip, and F. Aletta, “Deep learning techniques for noise annoyance
detection: Results from an intensive workshop at the Alan Turing Institute,”
The Journal of the Acoustical Society of America, vol. 153, 03 2023.
[13] W. Li, B. Zhang, P. Wang, C. Sun, G. Zeng, Q. Tang, G. Guo, and D. Cao,
“Visual-attribute-based emotion regulation of angry driving behaviors,”
IEEE Intelligent Transportation Systems Magazine, vol. 14, no. 3, pp.
10–28, 2022.
[14] S. PS and G. Mahalakshmi, “Emotion models: a review,” International
Journal of Control Theory and Applications, vol. 10, no. 8, pp. 651–657,
2017.
[15] J. A. Russell, “A circumplex model of affect.” Journal of personality
and social psychology, vol. 39, no. 6, p. 1161, 1980.
[16] A. Kazemzadeh, “Natural language description of emotion,” Ph.D.
dissertation, University of Southern California, 2013.
[17] H. Lian, C. Lu, S. Li, Y. Zhao, C. Tang, and Y. Zong, “A survey of deep
learning-based multimodal emotion recognition: Speech, text, and face,”
Entropy, vol. 25, no. 10, p. 1440, 2023.
[18] J. Liang, X. Liu, H. Liu, H. Phan, E. Benetos, M. D. Plumbley, and
W. Wang, “Adapting language-audio models as few-shot audio learners,”
in INTERSPEECH 2023, 2023, pp. 276–280.
[19] J. Liang, X. Liu, W. Wang, M. D. Plumbley, H. Phan, and E. Benetos,
“Acoustic prompt tuning: Empowering large language models with
audition capabilities,” 2023.
[20] P. Ekman and W. V. Friesen, “Facial action coding system,” Environmental
Psychology & Nonverbal Behavior, 1978.
[21] Z. Zhang, J. M. Girard, Y. Wu, X. Zhang, P. Liu, U. Ciftci, S. Canavan,
M. Reale, A. Horowitz, H. Yang et al., “Multimodal spontaneous
emotion corpus for human behavior analysis,” in Proceedings of the
IEEE conference on computer vision and pattern recognition, 2016, pp.
3438–3446.
[22] D. Keltner and D. T. Cordaro, “Understanding multimodal emotional
expressions,” The science of facial expression, 1798.
[23] P. Metri, J. Ghorpade, and A. Butalia, “Facial emotion recognition using
context based multimodal approach,” 2011.
[24] S. Thushara and S. Veni, “A multimodal emotion recognition system
from video,” in 2016 International Conference on Circuit, Power and
Computing Technologies (ICCPCT).
IEEE, 2016, pp. 1–5.
[25] B. Ding, T. Zhang, C. Wang, G. Liu, J. Liang, R. Hu, Y. Wu, and D. Guo,
“Acoustic scene classification: A comprehensive survey,” Expert Systems
with Applications, vol. 238, p. 121902, 2024.
[26] H. Zhang, E. Karystinaios, S. Dixon, G. Widmer, and C. E. Cancino-
Chac´on, “Symbolic music representations for classification tasks: A
systematic evaluation,” in Proceeding of the 24th International Society
on Music Information Retrieval (ISMIR), Milan, Italy, 2023.
[27] J. Liang, H. Phan, and E. Benetos, “Learning from taxonomy: Multi-label
few-shot classification for everyday sound recognition,” in ICASSP 2024
- 2024 IEEE International Conference on Acoustics, Speech and Signal
Processing (ICASSP), 2024, pp. 771–775.
[28] M. El Ayadi, M. S. Kamel, and F. Karray, “Survey on speech emotion
recognition: Features, classification schemes, and databases,” Pattern
recognition, vol. 44, no. 3, pp. 572–587, 2011.
[29] W. Lim, D. Jang, and T. Lee, “Speech emotion recognition using
convolutional and recurrent neural networks,” in 2016 Asia-Pacific signal
and information processing association annual summit and conference
(APSIPA).
IEEE, 2016, pp. 1–4.
[30] A. Satt, S. Rozenberg, R. Hoory et al., “Efficient emotion recognition
from speech using deep learning on spectrograms.” in Interspeech, 2017,
pp. 1089–1093.
[31] F. Daneshfar, S. J. Kabudian, and A. Neekabadi, “Speech emotion
recognition using hybrid spectral-prosodic features of speech signal/glottal
waveform, metaheuristic-based dimensionality reduction, and gaussian
elliptical basis function network classifier,” Applied Acoustics, vol. 166,
p. 107360, 2020.
[32] M. Schmitt, F. Ringeval, and B. Schuller, “At the border of acoustics
and linguistics: Bag-of-audio-words for the recognition of emotions in
speech,” 2016.
[33] E. Spyrou, T. Giannakopoulos, D. Sgouropoulos, and M. Papakostas,
“Extracting emotions from speech using a bag-of-visual-words approach,”
in 2017 12th International Workshop on Semantic and Social Media
Adaptation and Personalization (SMAP).
IEEE, 2017, pp. 80–83.
[34] D. E. Cahyani and I. Patasik, “Performance comparison of tf-idf and
word2vec models for emotion text classification,” Bulletin of Electrical
Engineering and Informatics, vol. 10, no. 5, pp. 2780–2788, 2021.
[35] P. Gupta, I. Roy, G. Batra, and A. K. Dubey, “Decoding emotions in
text using glove embeddings,” in 2021 International Conference on
Computing, Communication, and Intelligent Systems (ICCCIS).
IEEE,
2021, pp. 36–40.
[36] J. Devlin, “Bert: Pre-training of deep bidirectional transformers for
language understanding,” arXiv preprint arXiv:1810.04805, 2018.
[37] W. Dai, S. Cahyawijaya, Z. Liu, and P. Fung, “Multimodal end-to-end
sparse model for emotion recognition,” in Proceedings of the 2021
Conference of the North American Chapter of the Association for
Computational Linguistics: Human Language Technologies.
Online:
Association for Computational Linguistics, Jun. 2021, pp. 5305–5316.
[38] S. Mohammad, “Obtaining reliable human ratings of valence, arousal,
and dominance for 20,000 english words,” in Proceedings of the 56th
annual meeting of the association for computational linguistics (volume
1: Long papers), 2018, pp. 174–184.
[39] F. Schroff, D. Kalenichenko, and J. Philbin, “Facenet: A unified
embedding for face recognition and clustering,” in Proceedings of the
IEEE conference on computer vision and pattern recognition, 2015, pp.
815–823.
[40] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez,
L. u. Kaiser, and I. Polosukhin, “Attention is all you need,” in Advances
in Neural Information Processing Systems, I. Guyon, U. V. Luxburg,
S. Bengio, H. Wallach, R. Fergus, S. Vishwanathan, and R. Garnett, Eds.,
vol. 30.
Curran Associates, Inc., 2017.
[41] Z. Lan, M. Chen, S. Goodman, K. Gimpel, P. Sharma, and
R.
Soricut,
“Albert:
A
lite
bert
for
self-supervised
learning
of
language
representations,”
2020.
[Online].
Available:
https:
//arxiv.org/abs/1909.11942
[42] A. Krizhevsky, I. Sutskever, and G. E. Hinton, “Imagenet classification
with deep convolutional neural networks,” Advances in neural information
processing systems, vol. 25, 2012.
[43] Z. Lian, H. Sun, L. Sun, Z. Wen, S. Zhang, S. Chen, H. Gu, J. Zhao,
Z. Ma, X. Chen et al., “Mer 2024: Semi-supervised learning, noise
robustness, and open-vocabulary multimodal emotion recognition,” arXiv
preprint arXiv:2404.17113, 2024.
[44] Z. Lian, L. Sun, M. Xu, H. Sun, K. Xu, Z. Wen, S. Chen, B. Liu,
and J. Tao, “Explainable multimodal emotion reasoning,” arXiv preprint
arXiv:2306.15401, 2023.
[45] T. Mikolov, K. Chen, G. Corrado, and J. Dean, “Efficient estimation
of word representations in vector space,” 2013. [Online]. Available:
https://arxiv.org/abs/1301.3781


