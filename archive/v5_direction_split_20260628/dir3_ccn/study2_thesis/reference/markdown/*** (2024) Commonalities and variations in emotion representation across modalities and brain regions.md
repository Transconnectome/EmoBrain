www.nature.com/scientificreports 

**==> picture [71 x 14] intentionally omitted <==**

## **OPEN Commonalities and variations in emotion representation across modalities and brain regions** 

**Hiroaki Kiyokawa[1,2] & Ryusuke Hayashi[1]**[*] 

**Humans express emotions through various modalities such as facial expressions and natural language. However, the relationships between emotions expressed through different modalities and their correlations with neural activities remain uncertain. Here, we aimed to unveil some of these uncertainties by investigating the similarity of emotion representations across modalities and brain regions. First, we represented various emotion categories as multi-dimensional vectors derived from visual (face), linguistic, and visio-linguistic data, and used representational similarity analysis to compare these modalities. Second, we examined the linear transferability of emotion representation from other modalities to the visual modality. Third, we compared the representational structure derived in the first step with those from brain activities across 360 regions. Our findings revealed that emotion representations share commonalities across modalities with modality-type dependent variations, and they can be linearly mapped from other modalities to the visual modality. Additionally, emotion representations in uni-modalities showed relatively higher similarity with specific brain regions, while multi-modal emotion representation was most similar to representations across the entire brain region. These findings suggest that emotional experiences are represented differently across various brain regions with varying degrees of similarity to different modality types, and that they may be multi-modally conveyable in visual and linguistic domains.** 

**Keywords** Emotion, Facial expression, Representational similarity analysis, Multi-modal, fMRI, Deep learning 

During communication, humans convey their emotions to others through a variety of bodily reactions including facial expressions, utterances, and gestures, as well as through the use of language. Many researchers have investigated how humans express and/or recognize emotions in others using individual modalities, such as facial or linguistic  expression[1][–][7] . 

Pioneering research by Ekman reported that humans can express and recognize six distinct emotion categories (happiness, fear, disgust, anger, surprise, and sadness) through facial expressions, and this was found to be universal across different cultures (known as the “Basic 6 Emotions Theory”)[1] . Subsequent research has further supported the universality of facial expressions and the recognition of certain basic emotions visually expressed through facial action across  cultures[8][–][12] . 

Research in emotion expanded to cover a broader range of emotional experiences, not necessarily limited to those expressed through facial expressions, by representing emotions in a multi-dimensional space on the basis of several ‘core affective’ elements. For example, a pioneering approach by Russell demonstrated that a twodimensional circular structure, reflecting arousal and valence, could capture the semantic distribution of various emotion  categories[2] . Recent studies have demonstrated that our subjective emotional experience can be more fine-grained than that described by Ekman’s Basic 6 Emotion  Theory[3][,][9][,][13][–][16] . For instance, Cowen and Keltner reported that at least 27 distinct dimensions are required to distinguish human emotional experiences evoked by observing diverse visual  scenes[13] . The same authors also reported that human observers can recognize 28 emotion categories from facial  expressions[14] . Furthermore, a multi-dimensional representation of emotion expressed in text form was widely utilized in sentiment analysis by combining natural language processing  techniques[17][–][20] . A recent neuroscience study supported the theory of fine-grained emotion categories, with Horikawa et al.[21] demonstrating that scores for 34 emotions, rated by human annotators on various videos, could be decoded 

1Human Informatics and Interaction Research Institute, National Institute of Advanced Industrial Science and Technology (AIST), Tsukuba, Ibaraki, Japan.[2] Graduate School of Science and Engineering, Saitama University, Saitama, Japan.[*] email: r-hayashi@aist.go.jp 

**Scientific Reports** |        (2024) 14:20992 

| https://doi.org/10.1038/s41598-024-71690-y 

1 

www.nature.com/scientificreports/ 

using a regression model based on the brain activity evoked by observation of the videos. They also reported that different brain regions contributed to the prediction of different emotions. 

While we express and perceive various emotions through different modalities, the relationships between multiple emotion categories may change depending on the modality through which they are expressed. For instance, the variety of facial expression is constrained by the physical limitations of facial muscles. Therefore, emotion representations expressed through the face might differ from those expressed though language or those experienced by observing various types of emotional scenes, which has not been thoroughly examined. Given the involvement of various brain regions in emotion recognition and experience through various modalities, specific regions may also show emotion representations consistent with those of the modality involved. Although many studies have analyzed the common regions responding to emotions that do not depend on a specific modality[22][–][25] , few studies have analyzed the neural correlates of representational structures of various emotion categories expressed via different modalities across whole brain regions. 

Machine learning techniques for dimensionally representing emotions from data and representational similarity analysis (RSA)[26] are keys to addressing these unexplored issues. In recent years, advances in machine learning technologies have enabled us to represent a variety of emotions within specific modalities as multidimensional vectors (hereafter, referred to as emotion vectors) derived from extensive datasets of images and language[27][,][28] . Furthermore, a pretrained model utilizing the learning method known as “Contrastive LanguageImage Pre-training” (CLIP), designed to obtain a joint representation of visual and linguistic information from extensive paired datasets, has become publicly  available[29] . Using the vectorized representation of emotion categories for uni-modal and multi-modal data obtained via these machine learning techniques, we can examine which modality-type emotion representations are more similar to those expressed as brain activity patterns evoked by emotional experiences. RSA is a useful method for comparing differences in emotion representation across modalities and brain  regions[26] . The first step of RSA involves calculating representation similarity matrices (RSMs) by measuring the distances between all pairs of emotion vectors. Subsequently, the correlation between RSMs of different modalities is calculated to assess the similarity in the representational structure describing how the emotions within the same set are related to each other. 

In this study, we conducted three experiments on the representational relationships of emotions. Experiment 1 aimed to investigate how similarly multiple emotional categories are represented when they are expressed through different modalities using RSA. Specifically, we analyzed emotion vectors based on visual/facial expressions (Facial expression  dataset[14] ), linguistic expressions  (Word2Vec[27] ;  ConceptNet[30] ), and visio-linguistic expressions (CLIP’s multi-modal embeddings). In Experiment 2, given that facial expressions are constrained by the physical limitations of facial muscles, we aimed to examine the degree of similarity between emotion representations in facial expression with emotion representations expressed in other modalities using a method other than RSA. Specifically, we investigated whether emotional representations obtained from other modalities could be linearly transformed to those from facial expressions. Additionally, we evaluated such linear transformability using an artificial neural network (ANN) trained to classify emotions from facial image features. Experiment 3 aimed to evaluate which brain regions encode categorical emotions in a similar manner to the emotion representation expressed though different modality conditions. To this end, we calculated the similarity between the RSMs obtained in Experiment 1 and the RSMs derived from brain activity recorded while participants observed emotional movie stimuli (dataset from Horikawa et al.[21] ). Through the comparative analysis conducted in this study, we aimed to reveal the commonalities and differences in emotion representations across modalities and elucidate the correspondences with emotion representations in diverse brain regions. 

## **Methods** 

## **Experiment 1: Emotion vectors in different modality conditions** 

In Experiment 1, we compared representational relationships of emotions across three different modality conditions: facial expressions, linguistic expressions, and a multi-modal representation based on both images and text. 

First, to obtain a representational similarity matrix of emotion expressed by facial expression, we used a dataset available from https:// hume. ai/ produ cts/ facial- expre ssion- model as data breakdown list (referred to as ‘Facial expression dataset’), which consists of various facial images and their scores for 28 distinct emotion categories[14] , as rated by human annotators. For the following analysis, we selected 701 images in which faces were reliably detected with confidence scores higher than 0.5 using the Dlib automatic face detection  library[31] , and utilized their human-evaluated emotion scores for 28 emotion categories provided in the form of probability distributions (see Supplemental information for more details). Since only one image was assigned the maximum emotional score for the “Realization” emotion category, with all the other images having very low-score values for this category, we excluded “Realization” from the emotion categories in the following analysis (see Supplemental information for details). The remaining 27 emotion categories were: Amusement, Anger, Awe, Concentration, Confusion, Contemplation, Contempt, Contentment, Desire, Disappointment, Distress, Disgust, Doubt, Ecstasy, Elation, Embarrassment, Fear, Interest, Love, Pain, Pride, Relief, Sadness, Shame, Surprise, Sympathy, and Triumph. The co-occurrence/variance of the scores for each emotion pair served as a measure of the similarity between the emotion pairs perceived by human annotators from the same facial expressions. Therefore, we calculated the RSM for the 27 emotions on the basis of the correlation coefficients of the score values across all 701 images for each emotion pair (we refer to this matrix as the visual (face) emotion RSM). 

Second, to analyze how humans express emotions through natural language, we utilized models pretrained on two different natural language processing algorithms, Word2Vec (https:// code. google. com/ archi ve/p/ word2 vec/) and ConceptNet (https:// github. com/ commo nsense/ conce ptnet- numbe rbatch, Numberbatch 19.08). Both algorithms represent words as unit vectors in a high-dimensional space (300-dimensional space) based on the 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

2 

www.nature.com/scientificreports/ 

co-occurrence patterns of words observed in a large-scale text corpus. From these models, we extracted the two sets of vectors corresponding to the aforementioned 27 emotion category names used in the Facial expression dataset. These two sets of vectors for the 27 emotions were then used to calculate two RSMs on the basis of their correlation coefficients. We refer to these as the linguistic (Word2Vec) and linguistic (ConceptNet) emotion RSMs. 

Third, we examined how emotions are represented for both images and text in the joint representation space within the pretrained CLIP model. In this model, images and their corresponding text are embedded in the same space, making it possible to directly compare and measure the similarity between images and text. Therefore, the vectors in this joint space, corresponding to sentences (text prompts) describing the emotion categories, serve as emotional representations that reflect the semantics of both visual and linguistic information. For example, if we input the prompt “a photo of an emotion of {emotion category name}” into the CLIP model, we expected to obtain multi-dimensional vectors corresponding to the conceptual representation of the referred emotion category. Additionally, if we input the prompt “a photo of a {emotion category name} looking face”, we expected to obtain vectors related to the representation of the facial expression of the referred emotion category. We obtained two sets of multi-modal embedding vectors (512-dimensional unit vectors) corresponding to the 27 emotion category names from the CLIP model for two different types of prompt inputs. We then calculated two RSMs for two sets of vectors based on their correlation similarity, which we refer to as the visio-linguistic (concept) and visio-linguistic (face) emotion RSMs. 

Subsequently, we computed the Spearman’s rank-order correlation coefficients between the lower triangular components of the RSMs for five sub-conditions of three different modality conditions: visual (face), linguistic (Word2Vec), linguistic (ConceptNet), visio-linguistic (concept), and visio-linguistic (face). Permutation tests were then conducted to determine whether the correlation coefficients were significantly different from zero and to correct for multiple comparisons. Additionally, we assessed the significance of differences between subconditions using permutation tests (see Supplemental information for details of the permutation test procedure). 

## **Experiment 2: Linear transferability between different modalities** 

In Experiment 2, we investigated the extent to which the representational relationships between emotions expressed though facial expressions can be linearly projected from the representational relationships of other modalities. 

We employed two analytical methods for this evaluation: one applying orthogonal (rotation + reflection) transformation using singular value decomposition to emotion vectors, and the other using an ANN trained to classify facial expression categories (Fig. 1). Since the emotion vectors used in Experiment 1 had different dimensions across modalities, it was not feasible to directly apply them to these two analyses. To align the number of vector dimensions and normalize the lengths of emotion vectors in each modality while maintaining the semantic distance relationships between emotions, we employed a spherical multi-dimensional scaling (MDS) method to the RSMs of each modality defined as correlation distance matrices. Spherical MDS is a variant of MDS that embeds data samples onto the hypersphere in a dimensional space, with the constraint of preserving the L2 norm of the embedded vectors to a value of one. We used the Smacof package in the R programming language (https:// www. rdocu menta tion. org/ packa ges/ smacof/ versi ons/0. 9-5/ topics/ smaco fSphe re. dual) for this spherical MDS dimension reduction to create unit vectors of 27 emotions with 26 dimensions. In the analysis employing linear transformation, orthogonal matrices were calculated using leave-one-emotion-out cross-validation for the 27 emotion categories. Prediction accuracy was defined as the correlation coefficient between the orthogonally transformed vectors and the left-out vectors. We assessed the chance-level performance of this analysis by calculating the prediction accuracy of orthogonally transformed vectors from emotion vectors whose components were randomly shuffled across vector dimensions. We assessed the significance of differences between subconditions using permutation tests (see Supplemental information for details of the permutation test procedure). In the second analysis, we initially trained a multi-layer neural network consisting of three fully connected (FC) layers to predict 27 emotion scores from facial image features using the Facial expression dataset mentioned in Experiment 1 (please refer to the Supplemental information for details on how to extract facial image features from images). Each of the 27 units of 26-dimensional weights in the final layer in the trained model reflects a template of the image features related to each emotion expressed through facial expression, providing another form of emotion representation (which we refer to as the visual (ANN) emotion vectors). Therefore, the transfer accuracy, assessed after replacing the weights of the final layer with the emotion vectors of the other modalities (Fig. 1), could serve as a measure of the extent to which the emotion representations of facial expressions are transferable from those in other modalities. The weights of the final layer were set as 27 units of 26-dimensional vectors and were trained under the constraint of normalization to 1 (please refer to the Supplemental information for details of the ANN training conditions). The emotion vectors of the other modalities that best matched the visual (ANN) emotion vectors after the spherical MDS reduction and the linear orthogonal transformation described in the first analysis were used to replace the weights of the final layer to evaluate transfer accuracy. We defined the prediction accuracy of the trained ANN as the correlation coefficient between the predicted emotion scores and the ground-truth scores. To assess the chance-level performance of this ANN analysis, we calculated the prediction accuracy with the weights replaced with emotion vectors whose components were randomly shuffled across vector dimensions using 10 different seeds. The prediction accuracy was evaluated using a tenfold cross-validation method. We divided 701 images of the Facial Expression dataset into 10 subsets. The ANN model was trained on nine subsets and tested on the remaining subset. The prediction accuracy after weight replacement was also calculated using the same tenfold cross-validation method. We assessed the significance of differences between conditions using two-sample _t_ -tests. False discovery rate (FDR) correction using the Benjamini–Hochberg method was used to correct for multiple  comparisons[32] . 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

3 

www.nature.com/scientificreports/ 

**==> picture [398 x 287] intentionally omitted <==**

**Fig. 1.** Overview of the analysis process and the architecture of the ANN used in Experiment 2. The ANN estimates 27 emotion scores from facial image features. The frame colors represent modalities: blue corresponds to visual, red to linguistic, and green to visio-linguistic. Emotion vectors of different modalities were aligned according to the number of their dimensions and were normalized with L2-norm through spherical multidimensional scaling (MDS) reduction. We compared the prediction accuracy for emotion scores before and after replacing the weights of the final layer of the trained ANN with the weight vectors derived from emotion vectors from other modalities. 

## **Experiment 3: Emotion vectors in individual brain regions** 

In Experiment 3, we evaluated the neural representations of various emotions across different brain regions using the blood oxygen level dependent (BOLD) data, video data, human-rated emotion score data, and analysis scripts provided at https:// github. com/ Kamit aniLab/ Emoti onVid eoNeu ralRe prese ntati on by Horikawa et al.[21] . The BOLD signal data measured over 61 runs in this repository were recorded from five participants while they observed 2181 silent video stimuli selected to elicit various types of emotional experiences. Each video stimulus was associated with scores for the 34 distinct emotions defined by Cowen and  Keltner[13] . Although BOLD signals in this dataset were evoked only visually, they are considered to reflect brain activities related to a broad range of emotional experience, and to not be limited to the experience of perceiving facial expression. Using analysis scripts developed by Horikawa et al.[21] , we divided the time-averaged BOLD signal responses for each video into . We 360 cortical regions based on the human brain atlas (the HCP360 parcellation) defined by Glasser et al.[33] then trained a Ridge regression model for each participant to predict the rated emotion scores for 34 emotions from the BOLD signal responses and determined the optimal hyper-parameter for L2-norm regularization of the regressor through six-fold cross-validation. That is, we initially divided 61 runs of fMRI data into six subsets and used five subsets to select the top 500 voxels whose BOLD signal exhibited the highest correlation with the changes in emotion scores associated with the video stimuli presented within each brain region. The regression model was trained using the activity patterns of the selected voxels to predict the rated emotion scores for each brain region for each participant and we used the remaining subset to validate the performance of the trained regression model. The weights of this regression model reflect templates of brain activity patterns corresponding to each of the 34 emotions for each participant. Therefore, we calculated the RSM in each brain region (which we refer to as the brain emotion RSM) on the basis of the correlation coefficients between the weight vectors of the trained regressor for 15 emotion categories that were included in both the 27 emotion categories in Experiment 1 and the 34 emotion categories in the brain datasets. The 15 emotion categories used in Experiment 3 were: Amusement, Anger, Awe, Confusion, Contempt, Disappointment, Disgust, Fear, Interest, Pride, Relief, Sadness, Surprise, Sympathy, and Triumph. 

Subsequently, we calculated the correlation coefficients between a brain emotion RSM from 360 cortical regions for five participants and RSMs for three modality conditions (visual, linguistic, and visio-linguistic RSMs) to assess the extent to which each modality showed similarities in representational emotion relationships 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

4 

www.nature.com/scientificreports/ 

across different brain regions. For the statistical test, we grouped 360 regions into 13 coarser regions of interest (ROIs) and aggregated the data of the sub-regions within each ROI (from both hemispheres) across different participants. The names of the ROIs and their abbreviations were as follows: visual cortex [VC], inferior parietal lobule [IPL], precuneus [PC], temporo-parietal junction [TPJ], temporal area [TE], medial temporal cortex [MTC], superior temporal sulcus [STS], anterior cingulate cortex [ACC], insula, orbitofrontal cortex [OFC], dorsolateral prefrontal cortex [DLPFC], dorsomedial prefrontal cortex [DMPFC], and ventromedial prefrontal 5 cortex [VMPFC]. These regions are indicated in Fig. . We then calculated the correlation coefficients of the RSMs for the sub-regions in a target ROI for five participants and performed permutation testing with corrections for multiple comparisons to determine whether the correlation coefficient was statistically different between the three modality conditions within each ROI. 

## **Results** 

## **Experiment 1** 

In Experiment 1, we calculated the RSMs for 27 emotion vectors across three modality (visual, linguistic, and visio-linguistic) conditions. Specifically, RSMs for five sub-conditions, i.e. visual (face), linguistic (ConceptNet), linguistic (Word2Vec), visio-linguistic (concept), and visio-linguistic (face), were calculated to examine the extent of similarity in the representation of emotions between these sub-conditions. Figure 2 illustrates the RSMs for each condition/modality, while Fig. 3 displays the correlation coefficients between RSMs across conditions/ modalities. The RSMs showed significant correlations across all conditions/modalities ( _p_ < 0.001, with correction by permutation test). However, further inspection of the differences in correlation coefficients between each comparison showed modality-type dependent results, indicating that in many cases, intra-modality correlations (correlations between two sub-conditions within the same modality condition) were significantly higher than inter-modality correlations (correlations between two sub-conditions across different modality conditions) (Table 1). These findings suggest that emotional representations are similar within the same modality condition, regardless of the choice of model and method used to acquire emotion vectors, while the representational structure varies across three different modality conditions. 

## **Experiment 2** 

In Experiment 2, we performed two analyses to examine whether the representational relationships of emotions across modalities can be linearly mapped to each other. Figure 4a shows the results of using linear orthogonal transformation to predict visual (face) emotion vectors from emotion vectors of other modalities. Across all modalities, the prediction accuracies were significantly higher than under a random condition (linguistic (ConceptNet): _p_ < 0.001; linguistic (Word2Vec): _p_ < 0.01; visio-linguistic (concept): _p_ < 0.001; visio-linguisitc (face): _p_ < 0.01; permutation tested). 

In the second analysis, we initially trained an ANN to classify 27 emotions on the basis of facial image features. The weights of the final layer of the trained model reflected a template of the image features related to judgement of the emotions expressed through facial expression, serving as visual (ANN) emotion vectors. Therefore, if the representational relationships between emotions within a modality can be linearly mapped to those expressed though facial expression, we would expect the ANN to demonstrate significantly higher classification accuracy than chance level, even after replacing the weights of the final layer of the ANN with the weights derived from the emotion vectors of other modalities. 

Figure 4b shows the classification accuracy results before and after the weight replacement. There was no significant difference in classification accuracy before and after replacement of weights with the weights derived from visual (face) emotion vectors that were obtained from the same facial expression dataset used for the ANN training ( _t_ (18) = 0.65, _p_ = 0.52), supporting the idea that facial expression can be classified as accurately as by the original ANN model when the weight replacement method is used for alignment with the representation of emotions in facial expressions. In comparison with the chance level, we observed significantly higher classification accuracy in all replacement conditions (visual (ANN): _t_ (18) = 9.95, _p_ < 0.001; visual (face): _t_ (18) = 9.05, _p_ < 0.001; linguistic (ConceptNet): _t_ (18) = 5.61, _p_ < 0.001; linguistic (Word2Vec): _t_ (18) = 5.11, _p_ < 0.001; visiolinguistic(concept): _t_ (18) = 4.78, _p_ < 0.001; visio-linguistic (face): _t_ (18) = 5.07, _p_ < 0.001; FDR corrected). However, the transfer accuracies after the replacement of non-visual modality conditions (red and green bars in Fig. 4b) were significantly lower than the original classification accuracy (denoted as visual (ANN) in Fig. 4b) before the replacement (linguistic (ConceptNet): _t_ (18) = 5.25, _p_ < 0.001; linguistic (Word2Vec): _t_ (18) = 5.10, _p_ < 0.001; visiolinguistic (concept): _t_ (18) = 4.66, _p_ < 0.001; visio-linguistic (face): _t_ (18) = 3.68, _p_ < 0.01; FDR corrected). These results indicate that the representational relationships between multiple emotions within each modality can be aligned with each other through linear orthogonal transformations, although they may not be perfectly aligned. 

## **Experiment 3** 

For the representational relationships of multiple emotions derived in the first experiment, we observed higher similarities in comparisons within the same modality condition than in comparisons across different modality conditions, suggesting characteristic variations in emotion representation across modality conditions. In the next experiment, we quantified the neural representations of individual emotion categories in each brain region as multi-dimensional vectors and explored the extent to which modalities exhibited similarities in the representational relationship of emotion across diverse brain regions. 

Figure 5 depicts a flattened cortical map where the color of individual brain regions indicates the correlation coefficients between RSMs of each modality condition and the RSM of the corresponding brain region. Figure 5a, c, and e correspond to the results of the comparisons with the visual, linguistic, and visio-linguistic emotion RSMs, respectively. Only the results of the linguistic (Word2Vec) and visio-linguistic (concept) conditions are 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

5 

www.nature.com/scientificreports/ 

**==> picture [377 x 568] intentionally omitted <==**

**Fig. 2.** Representational similarity matrices (RSM) for 27 emotions. The color of each cell of the matrices represents the z-scored correlation coefficient between each emotion pair. The diagonal elements are colored in white. ( **a** ) Visual (face) emotion RSM, ( **b** ) Linguistic (ConceptNet) emotion RSM, ( **c** ) Linguistic (Word2Vec) emotion RSM, ( **d** ) Visio-linguistic (concept) emotion RSM, ( **e** ) Visio-linguistic (face) emotion RSM. 

shown as representatives of each modality condition because the mean correlation coefficients were higher for these sub-conditions than for the rest of the sub-conditions (the results for linguistic (ConceptNet) and 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

6 

www.nature.com/scientificreports/ 

**==> picture [234 x 181] intentionally omitted <==**

**Fig. 3.** Correlation coefficients between emotion RSMs for different conditions of three modalities. The numbers and colors in each block represent the correlation coefficients between corresponding conditions. 

**==> picture [515 x 29] intentionally omitted <==**

**----- Start of picture text -----**<br>
Intra-modality correlation Inter-modality correlation p  value Intra-modality correlation Inter-modality correlation p  value<br>Visual (face) & Visio-linguistic (concept) p  < 0.01 Visual (face) & Visio-linguistic (concept) p  = 0.09<br>**----- End of picture text -----**<br>


|**Intra-modality correlation**|**Inter-modality correlation**|**_p_ value**|**Intra-modality correlation**|**Inter-modality correlation**|**_p_ value**|
|---|---|---|---|---|---|
||Visual (face) & Visio-linguistic<br>(concept)|_p_< 0.01||Visual (face) & Visio-linguistic<br>(concept)|_p_= 0.09|
|Linguistic (ConceptNet)<br>&<br>Linguistic (Word2Vec)|Visual (face) & Visio-linguistic (face)|_p_< 0.01|Visio-linguistic (concept)<br>&<br>Visio-linguistic (face)|Visual (face) & Visio-linguistic (face)|_p_= 0.15|
||Visual (face) & Linguistic<br>(ConceptNet)|_p_< 0.001||Visual (face) & Linguistic<br>(ConceptNet)|_p_< 0.001|
||Visual (face) & Linguistic<br>(Word2Vec)|_p_< 0.001||Visual (face) & Linguistic<br>(Word2Vec)|_p_< 0.001|
||Linguistic (ConceptNet) & Visio-<br>linguistic(concept)|_p_< 0.001||Linguistic (ConceptNet) & Visio-<br>linguistic(concept)|_p_< 0.05|
||Linguistic (ConceptNet) & Visio-<br>linguistic (face)|_p_< 0.001||Linguistic (ConceptNet) & Visio-<br>linguistic (face)|_p_< 0.01|
||Linguistic (Word2Vec) & Visio-<br>linguistic (concept)|_p_< 0.001||Linguistic (Word2Vec) & Visio-<br>linguistic (concept)|_p_< 0.01|
||Linguistic (Word2Vec) & Visio-<br>linguistic (face)|_p_< 0.001||Linguistic (Word2Vec) & Visio-<br>linguistic (face)|_p_< 0.001|



**Table 1.** Comparisons between intra-modality correlations and inter-modality correlations using permutation test. 

visio-linguistic (face) are provided in Fig. S1). The correlation map for the visual (face) emotion RSM (Fig. 5a) primarily shows higher correlation in the occipital to parietal regions in comparison with other areas. By contrast, the correlation map for the linguistic (Word2Vec) emotion RSM (Fig. 5c) reveals higher correlation from parietal to frontal regions in comparison with other areas. The correlation map for the visio-linguistic (concept) emotion RSM (Fig. 5e) indicates high correlation across a broader area extending from occipital to frontal regions in comparison with the results for other modalities (mean RSM correlations: visual (face) emotion RSM: _r_ = 0.22; linguistic (Word2Vec) emotion RSM: _r_ = 0.26; visio-linguistic (concept) emotion RSM: _r_ = 0.40. Please see Fig. 5b, d, and f for histograms of the RSM correlations across 360 brain regions for each modality condition). These results indicate that for the representational relationships of emotions, the joint representation of both visual and linguistic information is more consistent with the neural representation in a wider range of brain regions than representations based solely on either visual (facial) or linguistic information. 

For statistical testing, we grouped the 360 cortical regions into 13 coarser-scale ROIs and examined the differences in correlation coefficients between different modality conditions for each of these 13 ROIs (Fig. 6) (note: we did not observe a strong tendency for inter-hemisphere differences in correlation, as indicated in Fig. S2; therefore, Fig. 6 shows the results of analysis of data merged across hemispheres). The visio-linguistic condition showed significantly higher correlations than the other two modalities in 12 out of 13 ROIs. The results of the permutation test in each ROI are summarized in Table 2. 

These results support the observation from Fig. 6 that the representational similarity in brain activity changes depending on the emotional experience, and that it is more similar to the joint representation of both visual and linguistic information than to representation based solely on either visual or linguistic information across diverse brain regions. Moreover, in many brain regions the brain emotion RSM showed higher correlation with the linguistic emotion RSM than with the visual emotion RSM (TE: _p_ < 0.001; MTC: _p_ < 0.001; STS: _p_ < 0.05; ACC: 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

7 

www.nature.com/scientificreports/ 

**==> picture [234 x 458] intentionally omitted <==**

**Fig. 4.** ( **a** ) The accuracy of visual (face) emotion vectors predicted from emotion vectors of other modalities using orthogonal transformation. The colors of the bars indicate the different modalities (red: linguistic, green: visio-linguistic, and gray: random). The lengths of the bars represent the mean prediction accuracy, assessed by the correlation coefficient between the predicted and left-out emotion vectors. Error bars represent ± 1 SEM for the leave-one-emotion-out cross-validation. ( **b** ) Classification accuracy results for the artificial neural network (ANN) predicting emotion scores from facial image features. Accuracy was assessed as the correlation coefficient between the predicted and ground-truth scores for the test data. The colors and labels of the bars indicate results before (denoted as visual (ANN)) and after replacement of the final layer weights with emotion vectors obtained from data from various modalities (blue: visual, red: linguistic, green: visio-linguistic, gray: random). Bar length represents the mean classification accuracy for each condition. The “From random vectors” condition corresponds to chance level. Error bars are ± 1 SEM for tenfold cross-validation results. 

_p_ < 0.001; Insula: _p_ < 0.05; OFC: _p_ < 0.001; DMPFC: _p_ < 0.001; VMPFC: _p_ < 0.001, permutation tested). However, in VC, PC, TPJ, and DLPFC there was no significant difference in correlation between the visual emotion RSM and the linguistic emotion RSM (VC: _p_ = 0.61, PC: _p_ = 0.89, TPJ: _p_ = 1.00, DLPFC: _p_ = 0.97, permutation tested), and in IPL, the visual emotion RSM showed significantly higher correlation with the brain emotion RSM than with the linguistic emotion RSM ( _p_ < 0.01, permutation tested). This result indicates that the representation of emotions based on brain activity in the IPL is more similar to the representation of emotions based on facial expressions than the representation based on linguistic expressions. These findings demonstrate, particularly in 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

8 

www.nature.com/scientificreports/ 

**==> picture [483 x 263] intentionally omitted <==**

**Fig. 5.** Correlations between brain emotion RSMs in 360 cortical regions and emotion RSMs obtained from each modality. ( **a** , **c** , and **e** ) depict the correlation maps (i.e., flattened cortical maps where the color of individual brain regions indicates the correlation coefficients) for visual (face), linguistic (Word2Vec), and visio-linguistic (concept) conditions, respectively. ( **b** , **d** , and **f** ) represent histograms of correlation coefficients corresponding to ( **a** ), ( **c** ), and ( **e** ), respectively. The regions enclosed by blue lines represent the coarser-scale 13 regions of interest (ROIs) parcellated by Horikawa et al.[21] . Abbreviations: VC (visual cortex), IPL (inferior parietal lobule), PC (precuneus), TPJ (temporo-parietal junction), TE (temporal area), MTC (medial temporal cortex), STS (superior temporal sulcus), ACC (anterior cingulate cortex), OFC (orbitofrontal cortex), and DLPFC/DMPFC/ VMPFC (dorsolateral/dorsomedial/ventromedial prefrontal cortex). 

**==> picture [234 x 214] intentionally omitted <==**

**Fig. 6.** Correlation coefficients between emotion RSMs for three modalities and brain emotion RSMs for 13 ROIs. The mean correlation coefficients for each modality in each ROI are plotted as differently colored bars: blue corresponds to visual modalities, red to linguistic, and green to visio-linguistic. Error bars indicate ± 1 SEM. * indicates conditions with _p_ < 0.05 after permutation test. 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

9 

www.nature.com/scientificreports/ 

**==> picture [194 x 34] intentionally omitted <==**

**----- Start of picture text -----**<br>
Linguistic vs. visio-<br>Visual vs. visio-linguistic linguistic<br>ROI p -value Significance p -value Significance<br>**----- End of picture text -----**<br>


|**ROI**|**Visual vs. visio-linguistic**|**Visual vs. visio-linguistic**|**Linguistic vs. visio-**<br>**linguistic**|**Linguistic vs. visio-**<br>**linguistic**|
|---|---|---|---|---|
||**_p_-value**|**Signifcance**|**_p_-value**|**Signifcance**|
||||||
|VC|_p_< 0.001|*|_p_< 0.001|*|
|IPL|_p_= 1.00||_p_< 0.001|*|
|PC|_p_< 0.001|*|_p_< 0.001|*|
|TPJ|_p_< 0.001|*|_p_< 0.001|*|
|TE|_p_< 0.001|*|_p_< 0.001|*|
|MTC|_p_< 0.001|*|_p_< 0.001|*|
|STS|_p_< 0.001|*|_p_< 0.001|*|
|ACC|_p_< 0.001|*|_p_< 0.001|*|
|Insula|_p_< 0.001|*|_p_< 0.001|*|
|OFC|_p_< 0.001|*|_p_< 0.05|*|
|DLPFC|_p_< 0.001|*|_p_< 0.001|*|
|DMPFC|_p_< 0.001|*|_p_< 0.001|*|
|VMPFC|_p_< 0.001|*|_p_< 0.001|*|



**Table 2.** The results of the permutation tests on the difference in the mean correlation coefficients between visual and visio-linguistic conditions, as well as between linguistic and visio-linguistic conditions, in each ROI. 

uni-modalities (visual and linguistic), the presence of regional differences in the representational relationship of emotional experiences. The visual emotion RSM is more similar to the brain emotion RSM in the posterior cortex, while the linguistic emotion RSM is more similar to the brain emotion RSM in the anterior cortex. 

## **Discussion** 

Through RSA, we showed that the emotions represented in three different modalities, i.e., visual, linguistic, and visio-linguistic modalities, share commonalities in relational structure with variations characteristic of the modality conditions (Experiment 1). We also explored the extent to which emotion representations based on facial expressions correspond to those of other modalities through prediction analysis using an orthogonal transformation and evaluation of transfer performance using an ANN trained on facial expression discrimination (Experiment 2). Furthermore, we observed that in individual brain regions, emotion representations derived from BOLD signal changes associated with emotional experiences showed different degrees of similarity to the emotion representations from visual, linguistic, and visio-linguistic modalities (Experiment 3). The results of the present study reveal three key points. (1) The representational relationships between emotions calculated from the same modality but using different methods are similar, although this similarity diminishes to some extent across different modalities. (2) The representational relationships between emotions across different modality conditions exhibit similar structures that allow them to be linearly mapped onto those of facial expressions. (3) The representational relationships of visual emotion and linguistic emotion show relatively strong correlations with neural responses in posterior and anterior brain regions, respectively. The representational relationships of visio-linguistic emotion are the most similar to neural responses across the entire brain region. 

This study extends the psychological and neuroscientific reports asserting that human emotions can be represented as multi-dimensional vectors categorized into distinct  dimensions[3][,][9][,][13][,][14][,][16][,][21][,][34] using a machine learning approach. Although in many cases the correlation coefficients between intra-modality correlations are significantly higher than those between inter-modality correlations, these representations still showed a certain degree of similarity, enabling linear mapping from other modalities to the visual modality. Our results indicate that the topology of emotion representation is somewhat preserved across different modalities. These findings are consistent with our daily life experience in which there is little discrepancy between emotions expressed through different modalities. 

Previous research reported that various brain regions process distinct emotion categories, and that the processing of a particular emotion category involves a distributed brain region network rather than localized one-to-one correspondence between specific brain areas and emotion  categories[21][,][35][–][37] . Our study aimed to use RSA to test whether different brain regions represent emotional experiences in distinct ways corresponding to different modalities by comparing RSMs based on brain activities with those calculated from various datasets. The most crucial finding of this study is that individual brain areas activate with varying degrees of similarity across different modality conditions in terms of 15 emotion categories. 

The overall similarity between the representation of emotions in brain regions and that in visio-linguistic modalities, which involve multi-modal representations of both visual and linguistic information, was higher than the single modality representation of either visual or linguistic information. Numerous previous studies investigated brain regions involved in multi-modal emotion representations across various  modalities[23][,][38] , and these studies consistently highlighted the contributions of areas such as PC, STS, medial prefrontal cortex (MPFC), and OFC to modality-independent emotion representations. In our study, several regions, including PC, STS, and MPFC, exhibited a high correlation between the brain emotion RSM and visio-linguistic emotion 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

10 

www.nature.com/scientificreports/ 

RSM (Table 2). This finding, which is in line with previous literature, supports the concept that these areas are involved in modality-independent processing of emotional expressions. 

To the contrary, our results showed that the OFC, which was previously reported to be involved in multimodal emotion  representations[39] , did not exhibit a high correlation with the emotion RSM of any modality condition. This discrepancy could be attributed to differences in analytical approach. Chikazoe et al.[39] analyzed OFC activity on the basis of emotions described using affective dimensions such as positive or negative valence, whereas the data we used from Horikawa et al.[21] involved an analysis based on emotion categories. Psychophysical studies[13][,][14] and a neuroscientific  approach[21] have shown that human emotions are better explained by emotion categories than by affective dimensions. Nevertheless, OFC activity patterns are reported to exhibit less correlation with evaluations based on emotion categories (see Fig. S1A in Horikawa et al.[21] ). We speculate that the OFC processes emotion attributes on the basis of coarse affective reactions, such as pleasant and unpleasant, rather than fine-grained emotion categories, such that the correlations between the RSM from the OFC and RSMs from three modality conditions—reflecting distinctly represented fine-grained emotion categories, as shown in Fig. 2—showed low values. 

In our study, several regions associated with visual information processing, such as the posterior areas and IPL, showed a tendency for high representational similarity with the visual modality. However, the brain regions other than posterior areas showed a tendency for high representational similarity with the linguistic modality. Previous research reported that the IPL processes emotional expressions specific to facial  expressions[40] . Therefore, our observation of the relatively high correlation with the visual modality in the IPL (compared with the other modalities) may be contingent on the emotional impressions conveyed by the facial images in the video stimuli. To explore this possibility, we conducted an additional analysis similar to Experiment 3, dividing the video stimuli into two sets according to whether the video included a human face or not (with and without face conditions). However, in this experiment there was no significant difference between videos with and without face conditions (refer to Fig. S4). This supplementary result suggests that although the representation of emotion in the activity of the IPL is highly correlated with the representation of emotion through facial expressions, it may depend on factors beyond reading emotions from facial expressions themselves. This observation is consistent with some previous studies reporting that visually evoked emotions can be decoded and categorized in posterior  regions[34][,][41] . It is also important to note that the absolute correlation coefficients between the IPL’s brain activity RSM and emotion RSMs from all modalities are relatively low. Further refined experiments are necessary to conclusively determine whether the processing of emotions in the IPL is solely attributable to facial expressions or whether it involves additional factors. 

A previous study that tested negative affect reported that stimulus-type-specific responses can be observed in sensory cortex and multi-modal responses can be observed in prefrontal  regions[42] . In contrast, the present study showed that the multi-modal (visio-linguistic) emotion RSM exhibited higher correlations with almost all brain regions than the visual emotion RSM (Experiment 3). Since our emotion RSMs used in Experiment 3 were 15-by-15, there was a concern that the high correlations could be driven by only a few outlier points. We found that the results shown in Fig. S5 did not indicate such outlier samples. 

The high correlation between the visio-linguistic emotion RSM and brain emotion RSMs was considered to reflect that brain emotion RSMs represent emotional experiences evoked by emotional scenes in general, and visio-linguistic emotion RSMs encompass more various aspects of emotions that can be expressed by both visual and linguistic modalities. However, the results can also be attributed to at least two factors other than the use of multi-modal representation. First, there is a possibility that transformer models, including attention mechanisms, i.e., the backbone of the pretrained CLIP model used for calculating visio-linguistic representation, are well-suited to the extraction of sematic representation from training data in general. Second, since the CLIP model was trained with 400 million pairs of images and text, the use of large-scale training data might be critical to capture a diverse range of precise emotion expressions. To examine the first factor, we performed a similar analysis to that in Experiment 3 using a transformer model trained only on text data and available as Go emotions[43] to extract linguistic emotion vectors (refer to Fig. S6 in Supplemental information). Fig. S6 indicates that the correlation map calculated using Go emotions is similar to those of ConceptNet and Word2Vec, and that the overall average correlation coefficients across diverse brain regions are comparable with those of other linguistic modality conditions. This suggests that the high correlation between the visio-linguistic emotion RSM and brain emotion RSM cannot be solely attributed to the use of a transformer model for calculating the emotion RSM. Instead, the importance lies in conducting multi-modal learning with large-scale data to acquire emotion representation that is highly similar to that in human brain. Our finding suggests that emotional experiences are represented differently in each brain region, with varying degrees of similarity across different modalities, and that they may be multi-modally conveyable in visual and linguistic domains. Further understanding of how different brain regions are involved in expressing, perceiving, and integrating emotion across different modalities, as partially revealed by the present study, could provide insights for developing AI systems capable of integrating multiple modalities to enhance understanding and responsiveness to human emotions. 

## **Data availability** 

The datasets analyzed during the current study are available in the github repository, https:// github. com/ Kamit aniLab/ Emoti onVid eoNeu ralRe prese ntati on, and in the web page https:// hume. ai/ produ cts/ facial- expre ssionmodel (acquired as of August 26, 2022). The datasets generated during the current study are available from the corresponding author on reasonable request. 

Received: 23 April 2024; Accepted: 30 August 2024 

**==> picture [133 x 12] intentionally omitted <==**

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

11 

www.nature.com/scientificreports/ 

## **References** 

1. Ekman, P., Sorenson, E. R. & Friesen, W. V. Pan-cultural elements in facial displays of emotion. _Science_ **164** , 86–88 (1969). 

2. Russell, J. A. Affective space is bipolar. _J. Personal. Soc. Psychol._ **37** (3), 345–356 (1979). 

3. Cowen, A. S. _et al._ Sixteen facial expressions occur in similar contexts worldwide. _Nature_ **589** , 251–257 (2021). 

4. Lindquist, K. A. _et al._ Language and the perception of emotion. _Emotion_ **6** (1), 125–138 (2006). 

5. Lindquist, K. A., MacCormack, J. K. & Shablack, H. The role of language in emotion: Predictions from psychological constructionism. _Front. Psychol._ **6** , 444 (2015). 

6. Barrett, L. F., Lindquist, K. A. & Gendron, M. Language as context for the perception of emotion. _Trends Cogn. Sci._ **11** (8), 327–332 (2007). 

7. Matsumoto, D. & Assar, M. The effects of language on judgments of universal facial expressions of emotion. _J. Nonverbal Behav._ **16** (2), 85–99 (1992). 

8. Cordaro, D. T. _et al._ The recognition of 18 facial-bodily expressions across nine cultures. _Emotion_ **20** , 1292–1300 (2020). 

9. Cowen, A. S., Laukka, P., Elfenbein, H. A., Liu, R. & Keltner, D. The primacy of categories in the recognition of 12 emotions in speech prosody across two cultures. _Nat. Hum. Behav._ **3** , 369–382 (2019). 

10. Ekman, P. Facial expression and emotion. _Am. Psychol._ **48** , 384–392 (1993). 

11. Elfenbein, H. A. & Ambady, N. On the universality and cultural specificity of emotion recognition: A meta-analysis. _Psychol. Bull._ **128** , 203–235 (2002). 

12. Sauter, D. A., Eisner, F., Ekman, P. & Scott, S. K. Cross-cultural recognition of basic emotions through nonverbal emotional vocalizations. _Proc. Natl. Acad. Sci. U.S.A._ **6** , 2408–2412 (2010). 

13. Cowen, A. S. & Keltner, D. Self-report captures 27 distinct categories of emotion bridged by continuous gradients. _Proc. Natl. Acad. Sci. U.S.A._ **114** , E7900–E7909 (2017). 

14. Cowen, A. S. & Keltner, D. What the face displays: Mapping 28 emotions conveyed by naturalistic expression. _Am. Psychol._ **75** , 349–364 (2020). 

15. Keltner, D., Sauter, D., Tracy, J. & Cowen, A. Emotional expression: Advances in basic emotion theory. _J. Nonverbal Behav._ **43** , 133–160 (2019). 

16. Koide-Majima, N., Nakai, T. & Nishimoto, S. Distinct dimensions of emotion in the human brain and their representation on the cortical surface. _Neuroimage_ **222** , 117258 (2020). 

17. Plutchik, R. The nature of emotions. _Am. Sci._ **89** (4), 344–350 (2001). 

18. Cambria, E., Poria, S., Gelbukh, A. & Thelwall, M. Sentiment analysis is a big suitcase. _IEEE Intell. Syst._ **32** (6), 74–80 (2017). 

19. Susanto, Y., Livingstone, A. G., Ng, B. C. & Cambria, E. The Hourglass model revisited. _IEEE Intell. Syst._ **35** (5), 96–102 (2020). 

20. Wankhade, M., Rao, A. C. S. & Kulkarni, C. A survey on sentiment analysis methods, applications, and challenges. _Artif. Intell. Rev._ **55** (7), 5731–5780 (2022). 

21. Horikawa, T., Cowen, A. S., Keltner, D. & Kamitani, Y. The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. _iScience_ **23** , 101060 (2020). 

22. Peelen, M. V., Atkinson, A. P. & Vuilleumier, P. Supramodal representations of perceived emotions in the human brain. _J. Neurosci._ **30** (30), 10127–10134 (2010). 

23. Klasen, M. _et al._ Supramodal representation of emotions. _J. Neurosci._ **31** (38), 13635–13643 (2011). 

24. Klasen, M., Kreifelts, B., Chen, Y. H., Seubert, J. & Mathiak, K. Neural processing of emotion in multimodal settings. _Front. Hum. Neurosci._ **8** , 822 (2014). 

25. Milesi, V. _et al._ Multimodal emotion perception after anterior temporal lobectomy (ATL). _Front. Hum. Neurosci._ **8** , 275 (2014). 

26. Kriegeskorte, N., Mur, M. & Bandettini, P. A. Representational similarity analysis-connecting the branches of systems neuroscience. _Front. Syst. Neurosci._ https:// doi. org/ 10. 3389/ neuro. 06. 004. 2008 (2008). 

27. Mikolov, T., Chen, K., Corrado, G., & Dean, J. Efficient estimation of word representations in vector space. arXiv preprint arXiv: 1301. 3781 (2013). 

28. Karras, T. _et al._ Analyzing and Improving the Image Quality of StyleGAN. In _Proceedings of the IEEE/CVF conference on computer vision and pattern recognition_ 8110–8119 (2020). 

29. Radford, A. _et al_ . Learning Transferable Visual Models from Natural Language Supervision. In _International conference on machine learning_ 8748–8763 (2021). 

30. Speer, R., Chin, J., & Havasi, C. Conceptnet 5.5: An Open Multilingual Graph of General Knowledge. In _Proceedings of the AAAI conference on artificial intelligence_ **31** , (2017). 

31. King, D. E. Dlib-ml: A machine learning toolkit. _J. Mach. Learn. Res._ **10** , 1755–1758 (2009). 

32. Benjamini, Y. & Hochberg, Y. Controlling the false discovery rate: A practical and powerful approach to multiple testing. _J. R. Stat. Soc._ **B57** , 289–300 (1995). 

33. Glasser, M. _et al._ A multi-modal parcellation of human cerebral cortex. _Nature_ **536** , 171–178 (2016). 

34. Kragel, P. A., Reddan, M. C., LaBar, K. S. & Wager, T. D. Emotion schemas are embedded in the human visual system. _Sci. Adv._ **5** , eaaw4358 (2019). 

35. Hamann, S. Mapping discrete and dimensional emotions onto the brain: Controversies and consensus. _Trends Cogn. Sci._ **16** (9), 458–466 (2012). 

36. Saarimäki, H. _et al._ Discrete neural signatures of basic emotions. _Cereb. Cortex_ **26** (6), 2563–2573 (2016). 

37. Lindquist, K. A. & Barrett, L. F. A functional architecture of the human brain: Emerging insights from the science of emotion. _Trends Cogn. Sci._ **16** (11), 533–540 (2012). 

38. Gao, C. & Shinkareva, S. V. Modality-general and modality-specific audiovisual valence processing. _Cortex_ **138** , 127–137 (2021). 39. Chikazoe, J., Lee, D. H., Kriegeskorte, N. & Anderson, A. K. Population coding of affect across stimuli, modalities and individuals. _Nat. Neurosci._ **17** , 1114–1122 (2014). 

40. Sarkheil, P., Goebel, R., Schneider, F. & Mathiak, K. Emotion unfolded by motion: A role for parietal lobe in decoding dynamic facial expressions. _Soc. Cogn. Affect. Neurosci._ **8** (8), 950–957 (2013). 

41. Bo, K. _et al._ Decoding neural representations of affective scenes in retinotopic visual cortex. _Cereb. Cortex_ **31** (6), 3047–3063 (2021). 

42. Čeko, M. _et al._ Common and stimulus-type-specific brain representations of negative affect. _Nat. Neurosci._ **25** (6), 760–770 (2022). 43. Demszky, D. _et al_ . GoEmotions: A dataset of fine-grained emotions. In _Proc. 58th Annual Meeting of the Association for Computational Linguistics._ 4040–4054 (ACL, 2020) 

## **Acknowledgements** 

We thank Dr. Daiki Nakamura for his insightful comments and advice, which have contributed to enhancing the quality of this paper. His expertise and support were invaluable in collecting the datasets and on implementing neural networks for our study. This work was financially supported by the Japan Science and Technology Agency, Moonshot Research & Development Program grant JPMJMS2012, and the National Institute of Information and Communications Technology (NICT) grant NICT 22301 awarded to R.H. H.K. was supported by JSPS KAKENHI (23K16985). 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

12 

www.nature.com/scientificreports/ 

## **Author contributions** 

R.H. supervised this study. R.H. and H.K. contributed to conceptualization, visualization and writing the manuscript text. H.K. conducted the experiments. H.K. and R.H. analyzed the data and interpreted the results. All authors reviewed the manuscript. 

## **Competing interests** 

The authors declare no competing interests. 

## **Ethical approval** 

The data used in this paper were obtained from open-source repositories. This study has no ethical issues according to the criteria of the Institutional Review Board of AIST. 

## **Additional information** 

**Supplementary Information** The online version contains supplementary material available at https:// doi. org/ 10. 1038/ s41598- 024- 71690-y. 

**Correspondence** and requests for materials should be addressed to R.H. 

**Reprints and permissions information** is available at www.nature.com/reprints. 

**Publisher’s note** Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations. 

**Open Access** This article is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License, which permits any non-commercial use, sharing, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if you modified the licensed material. You do not have permission under this licence to share adapted material derived from this article or parts of it. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http:// creat iveco mmons. org/ licen ses/ by- nc- nd/4. 0/. 

© The Author(s) 2024 

**Scientific Reports** |        (2024) 14:20992  | 

https://doi.org/10.1038/s41598-024-71690-y 

13 

