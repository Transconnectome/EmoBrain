# *** (2025) Gromov-Wasserstein unsupervised alignment reveals structural correspondences between the color similarity structures of humans and large language models

**Source:** *** (2025) Gromov-Wasserstein unsupervised alignment reveals structural correspondences between the color similarity structures of humans and large language models.pdf

---

## Page 1

1
Vol.:(0123456789)
Scientific Reports |        (2024) 14:15917  
| https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports
Gromov–Wasserstein unsupervised 
alignment reveals structural 
correspondences between the color 
similarity structures of humans 
and large language models
Genji Kawakita 1*, Ariel Zeleznikow‑Johnston 2,3, Naotsugu Tsuchiya 2,3,4,5 & 
Masafumi Oizumi 6*
Large Language Models (LLMs), such as the General Pre-trained Transformer (GPT), have shown 
remarkable performance in various cognitive tasks. However, it remains unclear whether these 
models have the ability to accurately infer human perceptual representations. Previous research has 
addressed this question by quantifying correlations between similarity response patterns of humans 
and LLMs. Correlation provides a measure of similarity, but it relies pre-defined item labels and does 
not distinguish category- and item- level similarity, falling short of characterizing detailed structural 
correspondence between humans and LLMs. To assess their structural equivalence in more detail, 
we propose the use of an unsupervised alignment method based on Gromov–Wasserstein optimal 
transport (GWOT). GWOT allows for the comparison of similarity structures without relying on pre-
defined label correspondences and can reveal fine-grained structural similarities and differences that 
may not be detected by simple correlation analysis. Using a large dataset of similarity judgments 
of 93 colors, we compared the color similarity structures of humans (color-neurotypical and color-
atypical participants) and two GPT models (GPT-3.5 and GPT-4). Our results show that the similarity 
structure of color-neurotypical participants can be remarkably well aligned with that of GPT-4 and, 
to a lesser extent, to that of GPT-3.5. These results contribute to the methodological advancements 
of comparing LLMs with human perception, and highlight the potential of unsupervised alignment 
methods to reveal detailed structural correspondences.
Keywords  Large language models, Unsupervised alignment, Gromov–Wasserstein optimal transport, Color 
similarity structures
Large Language Models (LLMs) have demonstrated remarkable performance in a variety of cognitive ­tasks1–3. 
These LLMs, based on the Transformer architecture, use self-attention mechanisms to effectively process and 
generate sequences of ­data4. Among LLMs, the General Pre-trained Transformer (GPT) series developed by Ope-
nAI has received considerable public attention with the introduction of the ChatGPT conversational ­interface5,6. 
Recently introduced GPT models can generate human-like responses to prompts, and are reported to excel at 
tasks assessing Theory of Mind ­abilities7.
These observations raise two intriguing questions: To what extent can Large Language Models accurately 
infer human perceptual representations, and how can we effectively compare LLMs and human perceptual rep-
resentations? Previous research addressed this by comparing human similarity judgments with those generated 
OPEN
1Department of Bioengineering, Imperial College London, London, UK. 2School of Psychological Sciences, 
Monash University, Melbourne, Australia. 3Turner Institute for Brain and Mental Health, Monash University, 
Melbourne, Australia. 4Center for Information and Neural Networks (CiNet), National Institute of Information 
and Communications Technology (NICT), Osaka, Japan. 5Department of Qualia Structure, ATR Computational 
Neuroscience Laboratories, Kyoto, Japan. 6Graduate School of Arts and Science, The University of Tokyo, Tokyo, 
Japan. *email: g.kawakita22@imperial.ac.uk; c-oizumi@g.ecc.u-tokyo.ac.jp


## Page 2

2
Vol:.(1234567890)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
by GPT across various ­modalities8. They found correlations as high as ρ = 0.8 between human and LLM color 
similarity judgments.
To evaluate the similarity between representational structures, a supervised approach known as Representa-
tional Similarity Analysis (RSA) has been widely used in neuroscience to compare different similarity matrices 
obtained from behavioral, neural, and neural network model ­data9,10. The supervised approach (or supervised 
alignment method in ­general11) assumes that an element in one similarity structure (for example, the color 
’red’) corresponds to the same element in another similarity structure. It then quantifies the degree of similarity 
between the different structures, assuming a one-to-one correspondence as defined by the item labels. Previous 
studies comparing the similarity structures of humans and LLMs also use this supervised ­approach8,12,13.
While high correlations suggest remarkable representational similarity between humans and LLMs, inter-
preting their significance is challenging. First, correlation values lack appropriate controls, such as simple color 
space models (e.g., RGB or LAB), for comparison. These controls serve as baselines to determine whether the 
high correlations between human and LLM similarity judgments are truly indicative of sophisticated represen-
tational similarity or if they can be achieved by simpler models. Second, high correlations may indicate only 
coarse category-level alignment without capturing fine-grained structural ­correspondence9,14.
Regarding the first point, simple correlation can only be interpreted relative to other representational models, 
especially because simple correlation does not provide an absolute measure of representational equivalence. For 
example, even if correlation values in the range of 0.7–0.8 seem impressively high in the context of a color similar-
ity judgment task, this does not necessarily mean that such values can only be achieved by sophisticated neural 
network models such as GPT. If simpler color space models, such as RGB or LAB, can achieve similar correlation 
levels with human judgments, the significance of a high human-to-GPT correlation becomes less pronounced.
Regarding the second point, simple correlation does not necessarily entail a fine-item-level structural cor-
respondence between two similarity structures. For example, previous studies using representational similarity 
analysis (RSA)9, a common method for assessing perceptual representational similarity via simple correlations 
between similarity matrices, have shown that high correlation values (e.g., ρ = 0.9 ) may indicate only coarse 
category-level correspondence, even while fine-item-level alignment is completely absent (e.g., Fig. 3 ­in14). Thus, 
the mere presence of a high correlation does not clarify whether the structures have a fine-item-level alignment 
or simply a coarse-category-level correspondence.
To address these limitations, we propose using an unsupervised alignment approach to assess a more detailed 
level of structural correspondence between the similarity structures of humans and LLMs. In unsupervised align-
ment, the correspondence between items in two similarity structures is not assumed. Instead, the correspond-
ences need to be discovered through an alignment procedure (Fig. 1a), since information about external item 
labels is not used. After alignment, external labels are used only to evaluate the alignment (Fig. 1b).
For unsupervised alignment, Gromov–Wasserstein optimal transport (GWOT)15,16 (Fig. 1c) has recently 
emerged as a promising method for comparing and aligning similarity structures. GWOT has been successfully 
Figure 1.   Schematic of unsupervised alignment. (a) Unsupervised alignment of similarity structures without 
external labels, based only on similarity relations. (b) Evaluation of unsupervised alignment using external 
labels. (c) Schematic of Gromov–Wasserstein optimal transport. The elements of matrices D and D′ are the 
dissimilarities between the items. Ŵ is the transportation matrix, where each element indicates the probability 
of an item in one similarity structure corresponding to another item in the other similarity structure. Modified 
­from19.


## Page 3

3
Vol.:(0123456789)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
applied in various contexts, such as aligning word embedding spaces across ­languages17, single-cell multi-omics 
­data18. The unsupervised optimal transport method has revealed the structural correspondence of the similar-
ity structures of colors across ­individuals19 and ­objects14, facilitating a broad structural exploration of human 
perceptual structures. These advances in unsupervised alignment techniques provide new ways to understand 
the extent to which LLMs can accurately infer human perceptual structures.
Using GWOT, we compared the color similarity structures of color-neurotypical and color-atypical human 
participants with those of GPT-3.5, GPT-4, and color space models. Our larger 93-color dataset, compared to 
the 23 colors ­in8, allows studying higher-dimensional color similarity. We also contrasted GPT-4 and GPT-3.5 
to explore the effects of visual input integration and model/data size. As baselines, we considered color-atypical 
individuals and simple color space models (RGB and LAB). The inclusion of RGB and LAB is important to rule 
out the possibility that GPT responses are based solely on these models.
Our results show that the color similarity structure of color-neurotypical participants can be remarkably 
well aligned with that of GPT-4 and, to a lesser extent, with that of GPT-3.5. In contrast, the color similarity 
structures of color-neurotypical participants could not be aligned with those of color space models, despite 
reasonably high correlation values. These findings suggest a strong fine-item-level structural correspondence 
between color-neurotypical human participants and the recent GPT models, but not between color-neurotypical 
human participants and color-space models. The results provide insights into LLMs’ ability to capture human 
color perception and demonstrate the utility of unsupervised alignment methods in revealing detailed structural 
similarities and differences between human and LLM representations.
Results
Color dissimilarity matrices
In this study, we compared the similarity structures of 93 colors obtained from human participants (color-
neurotypical and color-atypical participants) with those of large language models (GPT-3.5 and GPT-4). As for 
the human participants data, we used a large-scale dataset including 426 color-neurotypical participants and 
257 color-atypical participants, which we previously ­collected19. Color-atypical participants in this study refer 
to individuals with red-green color blindness, who were screened using a modified online Ishihara test (see 
supplementary material for details on inclusion criteria and screening procedure)20–24. In the color similarity 
judgement experiment, human participants were asked to rate the perceived similarity between pairs of colors 
drawn from a set of 93 color stimuli. For each pair, participants provided a rating on a scale from 0 to 7, with 0 
indicating that the colors were perceived as very similar and 7 indicating that the colors were perceived as very 
different. The details of the experimental design and procedure can be found in the supplementary material. 
We obtained the dissimilarity matrices of 93 colors for the color-neurotypical and color-atypical participants 
group by simply averaging the similarity judgement responses for each color pair from all the participants in 
each participant group as shown in Fig. 2.
To obtain responses from GPT-3.5 (gpt-3.5-turbo) and GPT-4 (gpt-4-0314), we used a prompt that 
represented each color as a HEX code in line with a previous ­study8 (see Methods for the details). By collecting a 
Figure 2.   Color dissimilarity matrices. Displayed are the dissimilarity matrices of 93 colors from the color-
neurotypical participants group, the color-atypical participants group, GPT-4, GPT-3.5, and the RGB and 
LAB color space models. All matrices are normalized to have values between 0 and 1, where 0 means the no 
difference between colors and 1 means the maximum difference for each dissimilarity matrix.


## Page 4

4
Vol:.(1234567890)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
complete set of similarity judgements of 93 colors with the same prompt, we obtained the dissimilarity matrices 
of GPT-3.5 and GPT-4 as shown in Fig. 2. By visual inspection, we can clearly see that the dissimilarity matrix 
of GPT-4 is very similar to that of the color-neurotypical participants.
To examine the possibility that LLMs rely on established color space models when judging color similarity, 
we computed the dissimilarity matrices for the 93 colors using two representative color space models, RGB and 
LAB color space models, as shown in Fig. 2 (see Methods for the details). These simple color space models served 
as baselines to evaluate how well large language models can approximate the human color similarity structures.
Correlations between color dissimilarity matrices
Before evaluating the structural correspondences of the color dissimilarity matrices between humans and LLMs 
as per the unsupervised alignment analysis, we first computed the similarity between them by simply com-
puting correlations (the Spearman correlation) between them. This analysis corresponds to the conventional 
representational similarity ­analysis9, which implicitly assumes correspondence between the same colors across 
different similarity structures. Figure 3a summarizes the correlations between the similarity matrices of the 
color-neurotypical participants group, the color-atypical participants group, GPT-4, GPT-3.5, and the RGB and 
LAB color spaces.
This analysis yields the following three findings: 
1.	 The dissimilarity matrix of the human color-neurotypical participant group is the closest to that of GPT-4 
( ρ = 0.77 ) among the models considered (GPTs and color space models). In addition, other models such 
as GPT-3.5 ( ρ = 0.62 ), the RGB color space model ( ρ = 0.60 ), and the LAB color space model ( ρ = 0.71 ) 
also show reasonable correlation with the similarity structure of the color-neurotypical group.
2.	 GPT-3.5 shows lower correlations with the dissimilarity matrix of the human color-neurotypical group than 
GPT-4. In addition, the dissimilarity matrix of GPT-3.5 shows lower correlations with the color space models 
than GPT-4.
3.	 The human color-atypical group shows relatively low correlations with the other dissimilarity matrices, sug-
gesting that the similarity structure of the color-atypical group is significantly different from that of the the 
color-neurotypical group, the GPTs, and the color space models.
The scatter plots of similarity ratings of all the pairs of the dissimilarity matrices are available in Fig. S1, providing 
a visual aid for understanding the correlation trends between each pair of groups.
Unsupervised alignment of color similarity structures
We then evaluated the extent to which the color similarity structures of humans and LLMs could be aligned in 
an unsupervised manner using the Gromov–Wasserstein Optimal Transport (GWOT) algorithm. In Fig. 3b, 
we summarized the matching rates of the unsupervised GWOT alignment between all pairs of the dissimilar-
ity matrices shown in Fig. 2. In the following, the results of the most important pairs (color-neurotypical vs. 
GPT-4, GPT-3.5, LAB) are explained in more detail. The detailed results of the other pairs are shown in the 
Supplementary Figs. S2 and S3.
Figure 3.   Evaluating the similarity of similarity structures in a supervised and unsupervised method. (a) 
Conventional representational similarity analysis based on Spearman correlations. Spearman correlations 
between the dissimilarity matrices obtained from the color-neurotypical participants group (abbreviated 
by TYP), the color-atypical participants group (abbreviated by ATYP), GPT-4, GPT-3.5, and the RGB and 
LAB color spaces are shown. (b) Matching rates of unsupervised alignment based on GWOT between the 
dissimilarity matrices.


## Page 5

5
Vol.:(0123456789)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
Unsupervised alignment with GPT‑4
First, we showed the results of the unsupervised alignment between the color similarity structures of the human 
color-neurotypical participants and GPT-4 in Fig. 4. We applied entropic GWOT to the two dissimilarity matrices 
shown in Fig. 4a. Since entropic GWOT is a non-convex optimization problem involving hyperparameter search 
of ǫ , which controls the degree of entropy regularization, we performed a total of 500 optimization iterations 
with different ǫ values and initialization of transportation plans to search for a global optimum. The points in 
Fig. 4b correspond to the local minimum found in each iteration of the optimization performed on different ǫ 
values. Across different ǫ values, we selected the local minimum with the lowest GWD as the optimal solution 
(indicated by the red circle in Fig. 4b).
From the optimization process, we obtained the optimal transportation plan Ŵ between the human color-
neurotypical participants and GPT4 (Fig. 4c). As shown in Fig. 4c, most of the diagonal elements in Ŵ have high 
values, indicating that most of the colors in the color-neurotypical participants correspond with a high probability 
to the same colors in GPT-4. To quantitatively assess the degree of correspondence, we computed the matching 
rate of the 93 colors (see Methods for details), which was 91.4% (Fig. 3b). As can be seen in Fig. 4b, the local 
minima with low GWD (in the y-axis) tend to yield a high matching rate (points with yellowish color), which is 
necessary for unsupervised alignment to achieve a high matching rate.
To visually inspect the degree of the unsupervised alignment, we draw the embeddings of the color-neu-
rotypical participants and the aligned embeddings of GPT-4 in Fig. 4d (See Supplementary Movies S1 for the 
animation of the aligned embeddings). As detailed in Methods, we aligned the embeddings of GPT-4 to those 
of the color-neurotypical participants by solving a Procrustes-type problem using the optimized transportation 
plan Ŵ obtained through GWOT. Each color represents the label of a corresponding external color stimulus. 
Note that even though the color labels are shown in Fig. 4d, this is only for the visualization purpose and the 
whole alignment procedure is performed in a purely unsupervised manner without relying on the color labels. 
As depicted in Fig. 4d, identical colors from the color-neurotypical participants and GPT-4 are located in close 
proximity to each other. This shows that GPT-4 has a color similarity structure that is strikingly similar to that 
of the color-neurotypical participants, allowing for the successful unsupervised alignment.
While the main results presented above were obtained using GPT-4 with text input, we also observed qualita-
tively similar results when using GPT-4 Vision, which takes visual input (color patches) instead of text descrip-
tions. The unsupervised alignment between GPT-4 Vision and color-neurotypical participants revealed a high 
degree of structural similarity in their color representations, albeit with a slightly lower matching rate compared 
to GPT-4 with text input. See Supplementary Text 2 and Supplementary Figures S4 and S5 for detailed results 
and visualizations of the GPT-4 Vision analysis.
Unsupervised alignment with GPT‑3.5
Next, for comparison with GPT-4, we showed the results of the unsupervised alignment between the color 
similarity structures of the human color-neurotypical participants and GPT-3.5 in Fig. 5 (See Supplementary 
Movies S1 for the animation of the aligned embeddings). The results are presented in the same format as Fig. 4 
and the analysis procedure is also the same as explained in the previous section.
In contrast to the case of GPT-4, we found that the matching rate of the optimal solution (shown in the red 
circle in Fig. 5b) is much lower, 11.8%, than that of the GPT-4, 91.4%. However, this is still significantly higher 
than the chance level (1.08%). We can also see that the optimal transportation plan Ŵ in Fig. 5c is “roughly” 
diagonal, i.e., the diagonal elements or neighboring elements to diagonal elements of Ŵ tend to have large values. 
This roughly diagonal appearance of Ŵ means that similar colors correspond to each other between the color-
neurotypical participants and GPT-3.5 with a high probability. This is also confirmed by the aligned embeddings 
shown in Fig. 5d, where the embeddings of similar colors from the color-neurotypical participants and GPT-3.5 
are located close together. These results indicate that the similarity matrix of GPT-3.5, although less well aligned 
Figure 4.   Unsupervised alignment between the color similarity structure of the human color-neurotypical 
participants and that of GPT-4. (a) Dissimilarity matrices of 93 colors from the human color-neurotypical 
participants (abbreviated by TYP) and GPT-4. (b) The optimization results over 500 iterations with different 
ǫ values. GWD values of local minima represented by points are shown with respect to ǫ . Colors represent the 
matching rate of unsupervised alignment. (c) Optimal transportation plan Ŵ between the dissimilarity matrices 
of TYP and GPT-4. (d) Aligned embeddings of TYP and GPT-4 plotted in the embedded space of TYP.


## Page 6

6
Vol:.(1234567890)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
with the color-neurotypical similarity matrix than GPT-4, contains some structural features that can be aligned 
with the color-neurotypical similarity matrix.
Unsupervised alignment with color space models
To provide a baseline comparison, we showed the results of the unsupervised alignment between the color 
similarity structures of the human color-neurotypical participants and the LAB color space model in Fig. 6 (See 
Supplementary Movies S1 for the animation of the aligned embeddings). The results are presented in the same 
format as Figs. 4 and 5.
In contrast to the both cases of GPT-4 and GPT-3.5, we found that the matching rate of the optimal solution 
(shown in the red circle in Fig. 6b) is very low (4.30%), which is close to the chance level (1.08%). We also found 
that the appearance of the optimal transportation plan Ŵ (Fig. 6c) is qualitatively different from those of GPT-4 
(Fig. 4c) and GPT-3.5 (Fig. 5c). The optimal transportation plan (Fig. 6c) is not lined up diagonally, i.e., the 
diagonal elements or the neighboring elements to the diagonal elements of Ŵ are small. The aligned embeddings 
shown in Fig. 6d are also quite different from those of GPT-4 (Fig. 4d) and GPT-3.5 (Fig. 5d), i.e., the embed-
dings of similar colors are not closely positioned, indicating that similar colors are not correctly aligned by the 
unsupervised alignment. We also obtained the similar results for the RGB color space model. The matching rate 
between the color-neurotypical participants and RGB is 5.38% (Fig. 3b) and the optimal transportation plan Ŵ 
does not show roughly diagonal appearance (Supplementary Fig. S2).
Unsupervised alignment with color‑atypical participants
As another negative control, we also showed the results of the unsupervised alignment with the color-atypical 
participants in Supplementary Fig. S2 and Fig. 3b. As shown in Fig. 3b, the similarity structure of the color-
atypical participants is not aligned with either GPT-4 or the color-neurotypical participants (the matching rate 
is 1.08% and 7.53%, respectively). Note, however, that the correlations between the color-atypical participants 
Figure 5.   Unsupervised alignment between the color similarity structure of the human color-neurotypical 
participants and that of GPT-3.5. (a) Dissimilarity matrices of 93 colors from the human color-neurotypical 
participants (abbreviated by TYP) and GPT-3.5. (b) The optimization results over 500 iterations with different 
ǫ values. GWD values of local minima represented by points are shown with respect to ǫ . Colors represent the 
matching rate of unsupervised alignment. (c) Optimal transportation plan Ŵ between the dissimilarity matrices 
of TYP and GPT-3.5. (d) Aligned embeddings of TYP and GPT-3.5 plotted in the embedded space of TYP.
Figure 6.   Unsupervised alignment between the color similarity structure of the human color-neurotypical 
participants and that of LAB. (a) Dissimilarity matrices of 93 colors from the human color-neurotypical 
participants (abbreviated by TYP) and LAB. (b) The optimization results over 500 iterations with different ǫ 
values. GWD values of local minima represented by points are shown with respect to ǫ . Colors represent the 
matching rate of unsupervised alignment. (c) Optimal transportation plan Ŵ between the dissimilarity matrices 
of TYP and LAB. (d) Aligned embeddings of TYP and LAB plotted in the embedded space of TYP.


## Page 7

7
Vol.:(0123456789)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
and GPT-4 and the color-neurotypical participants are reasonably high, ρ = 0.67 and ρ = 0.57 , respectively 
(Fig. 3a). The subtle structural difference caused by red-green color deficiency is likely to prevent the successful 
unsupervised alignment between the color-atypical participants and GPT-4 and the color-neurotypical partici-
pants (see ­also19).
Comparison between conventional representational similarity analysis and unsupervised 
alignment
Finally, we mention several important differences between the results of conventional representational similar-
ity analysis and the unsupervised alignment based on GWOT. Comparing the Figs. 3a,b, we observe that the 
unsupervised alignment method was able to reveal more nuanced structural differences that were not observable 
using conventional representational similarity analysis. For example, the Spearman correlations between the 
color-neurotypical participants and the color space models ( ρ = 0.60 for RGB and ρ = 0.71 for LAB) are reason-
ably high. In particular, the correlation of LAB ( ρ = 0.71 ) is close to the correlation of GPT-4 ( ρ = 0.77 ) and 
higher than the correlation of GPT-3 ( ρ = 0.62 ). However, as we showed in the previous section, the matching 
rates of the unsupervised alignment between the color-neurotypical participants and the color space models are 
very low ( 5.38% for RGB and 4.30% for LAB), almost at chance level. This suggests that human color similarity 
structures are not adequately captured by color space models, but are remarkably well captured by GPT-4 and 
is captured to some extent by GPT-3.5. Such nuanced structural differences between the human color similarity 
structure, the color space models, and GPT-4 or GPT-3.5 cannot be detected by conventional representational 
similarity analysis, which is based on simple correlation between similarity structures.
Discussion
The primary objective of our work was to present a methodological advancement beyond simple correlation, 
enabled by an unsupervised alignment technique, Gromov–Wasserstein Optimal Transport (GWOT), for com-
paring the color similarity structures of humans and large language models (LLMs). Unlike previous studies with 
simple correlation analysis, our GWOT technique revealed more nuanced structural similarities and differences.
Specifically, among the models considered (GPT-4, GPT-3.5, RGB, and LAB), GPT-4 had a color similarity 
structure that most closely resembled that of the color-neurotypical participants with the highest matching rate 
with the color-neurotypical participants (91.4%). Compared to GPT-4, GPT-3.5 is less well aligned with the color-
neurotypical participants, but it still demonstrates a significant degree of alignment (11.8%), outperforming the 
RGB and LAB color space models. Despite reasonably high correlation coefficients ( ρ = 0.60 for RGB, ρ = 0.71 
for LAB), somewhat surprisingly, the similarity structures of the color space models could not be aligned with 
that of human color-neurotypical participants in an unsupervised manner ( 5.38% for RGB and 4.30% for LAB). 
These results indicate that our unsupervised alignment method can reveal nuanced structural similarities and 
differences between the similarity structures that are not discernible by simple correlation analysis. The qualita-
tive difference between the GPTs and the color space models means that neither GPT-4 nor GPT-3.5 similarity 
judgments are the simple reflections of the RGB and LAB color space models. Rather, GPTs reflect something 
learned from massive textual data, or the combination of textual and visual data in the case of GPT-4.
Despite our finding that color similarity structure of GPT-4 is remarkably well aligned with that of human 
color-neurotypical participants, it remains unclear whether GPT-4 maintains similar internal representations of 
color to humans. A valuable direction for future research would be to directly extract the embeddings of colors in 
GPT-4 and evaluate the similarity structures computed as distance matrices between these embeddings. However, 
note that the GPT-4 embeddings were not available at this time (January 2024).
For the GPT-human comparison studies including this ­study8, it is important to consider the potential influ-
ence of cultural factors, such as language. This consideration is important even in the case of color discrimination 
and ­categorization25. While the exact details of GPT’s training data are not publicly available, it is presumed that 
the model was primarily trained on English language data. Similarly, the human participants in our study were 
recruited from an English-speaking region. Given that both the GPT models and the human participants were 
from the same language/cultural background, it is possible that this shared background contributed to the strong 
alignment of their color similarity structures. Future research could explore how color similarity structures may 
differ across cultures and how the alignment between human and LLM color perception might be affected by 
cultural factors. Additionally, investigating the performance of LLMs trained on data from diverse cultural and 
linguistic backgrounds could provide insights into the role of culture in shaping color perception and categoriza-
tion in both humans and AI models.
While this study focused on comparing the similarity structures of colors as an initial tractable attempt, 
future research could explore other sensory modalities across a broader range of tasks (e.g., visual object simi-
larity judgment ­tasks26,27). This could provide a more comprehensive understanding of the extent to which large 
language models accurately capture the similarity structures inherent in human perception. Some studies have 
already begun to compare the similarity structures of LLMs and humans in other domains based on simple 
­correlation8,12,13. Our unsupervised alignment method may provide a novel computational tool to explore more 
detailed structural differences or similarities between human cognition and LLMs that cannot be detected by 
simple correlation analysis.
Methods
Collecting responses from large language models
To obtain responses from GPT-3.5 (gpt-3.5-turbo) and GPT-4 (gpt-4-0314), we used a prompt that 
represented each color as a HEX code in line with a previous ­study8.
The prompt we used is as follows:


## Page 8

8
Vol:.(1234567890)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
People described pairs of colors using their hex codes. Rate the dissimilarity of the pair of colors: Color 
1:[HEX code] and Color 2:[HEX code] on a scale of 0–7 with 0–1 being Very Similar, 2–3 being Similar, 
4–5 being Different, and 6–7 being Very Different. Your rating should be any real number between 0 and 
7. Your answer should be only the rating in the form of a number. No explanation is needed.
The temperature parameter, which determines the degree of randomness in GPT responses, was set to 0.7. We 
ran 5 trials for each model, collecting a complete set of similarity judgment responses using the same prompt for 
each trial. We averaged the responses of the similarity judgments for all possible pairs of 93 colors over 5 trials 
and obtained the dissimilarity matrices of 93 colors from GPT-3.5 and GPT-4.
Dissimilarity matrix of color space models
To obtain the dissimilarity matrix of the RGB color space model, we computed the Euclidean distance as a 
measure of dissimilarity between each color pair within the 3-dimensional RGB space. For the LAB color space 
model, we used the CIEDE 2000 color difference ­formula28 implemented in the Python package colormath 
(delta_e_cie2000) as a measure of the dissimilarity between colors. Then, by computing the dissimilari-
ties of all the pairs of 93 colors, we obtained the dissimilarity matrices of the RGB and LAB color space models.
Comparing color similarity structures
Conventional representational similarity analysis
To compare the color similarity structures between humans and GPTs in a supervised manner using external 
color label information, we used the conventional representational similarity analysis (RSA) approach. We com-
puted Spearman correlations between all pairs of similarity matrices (considering only the upper-triangular 
elements of each matrix). It is important to note that this analysis inherently assumes a correspondence between 
the same colors across different similarity structures.
Unsupervised alignment using Gromov–Wasserstein optimal transport
To evaluate the similarity between the color similarity structures in an unsupervised manner, i.e., without mak-
ing any assumptions about the correspondence of colors between different similarity structures, we used the 
Gromov–Wasserstein optimal transport (GWOT) algorithm. GWOT is an unsupervised alignment method that 
identifies the optimal transport plan between point clouds in two domains without requiring information about 
the correspondence between each item. The algorithm optimizes the Gromov–Wasserstein distance (GWD),
which quantifies the correspondence between the similarity structures in the two domains (Fig. 1C). In our 
problem setting, Dij denotes the dissimilarity between color i and j in one similarity matrix D, while D′
kl denotes 
the dissimilarity between color k and l in another similarity matrix D′ . We normalized each similarity matrix D 
so that the values range between 0 and 1. Solving the minimization problem of GWD yields the optimal trans-
portation plan, represented by the matrix Ŵ∗ , which effectively aligns the color structures in the two domains in 
an unsupervised manner. An element of the matrix Ŵik can be interpreted as the “probability” that the i-th color 
in one domain corresponds to the k-th color in the other domain.
Efficient optimization of GWD can be achieved by adding an entropy-regularization term, H(Ŵ) , as shown 
in the following equation.
This addition has been proven to enhance optimization ­efficiency29.
The optimization problem in Eq. (2) is non-convex, meaning that the optimal solutions found by the algo-
rithm are local optima, with no guarantee of achieving the global optimum. To find good local minima, we 
conducted hyperparameter tuning on ǫ and performed random initialization of the matrix Ŵ using the GWTune 
toolbox that we ­developed14. This toolbox uses ­Optuna30 for hyperparameter tuning and Python Optimal Trans-
port (POT)31 for GWOT optimization. We used ǫ values ranging from 10−4 to 10−1 with logarithmic spacing 
(500 different ǫ values), in line with previous ­works19. For each value of ǫ , we used a randomly initialized matrix 
Ŵ . After finding the optimized Ŵ for each ǫ value, we selected the solution that minimizes the GWD without the 
entropy term (Eq. 1) as the optimal transportation plan.
Evaluation of unsupervised alignment
To assess the degree of agreement between two similarity structures, we calculated the matching rate between 
the two dissimilarity matrices using color labels. For each color, we consider it as a match if the transportation 
plan assigns the highest probability between the same colors in the two similarity matrices, because the trans-
portation plan Ŵij represents the probability or weight of transporting the i-th color in matrix 1 to the j-th color 
in matrix 2. More precisely, for each color i from matrix 1, if Ŵij is the highest among j ∈{1, ..., n} and the i-th 
color in matrix 1 and the j-th color in matrix 2 are the same, then we consider the i-th color in matrix 1 to be a 
match with the same color, j, in matrix 2.
We denote the color labels in the two dissimilarity matrices as c1 and c2 respectively. The matching rate or 
accuracy is calculated by comparing the transportation plan Ŵ with these labels. For each color i in the matrix 1, 
denoted by c1i , the matching condition can be formalized as:
(1)
GWD = min
Ŵ

i,j,k,l
(Dij −D′
kl)2ŴikŴjl,
(2)
GWDǫ = min
Ŵ

i,j,k,l
(Dij −D′
kl)2ŴikŴjl −ǫH(Ŵ).


## Page 9

9
Vol.:(0123456789)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
This function indicates whether the i-th color in the matrix 1 c1i matches with the same color in the matrix 2 c2j . 
The matching rate is then the percentage of colors in the matrix 1 that match with the same color in the matrix 
2, which can be calculated as:
Visualization of unsupervised alignment
To visually assess the degree of similarity between the two color similarity structures in an unsupervised manner, 
we obtained 3-dimensional embeddings of 93 colors. To derive the color embeddings, we applied multidimen-
sional scaling (MDS) to the similarity matrices, yielding 3-dimensional embeddings. We then aligned a pair of 
embeddings, denoted X and Y, using the orthogonal rotation matrix Q. This matrix was obtained by solving a 
Procrustes-type problem using the optimized transportation plan Ŵ∗ derived from GWOT.
where  · F is the Frobenius norm AF =

i,j a2
ij . A solution to the problem can be found through the 
singular value decomposition of X(YŴ∗)⊤.
Data availability
Data for the behavioral experiments is available at https://​osf.​io/​9xwr2/.
Code availability
Code for the behavioral experiments is available at https://​osf.​io/​9xwr2/. Code for the data analysis is available 
at https://​oizumi-​lab.​github.​io/​GWTune/.
Received: 21 January 2024; Accepted: 21 June 2024
References
	 1.	 Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. BERT: Pre-training of deep bidirectional transformers for language under-
standing. In Proceedings of the Conference of the North American Chapter of the Association for Computational Linguistics: Human 
Language Technologies, 4171–4186 (2018).
	 2.	 Bubeck, S., Chandrasekaran, V., Eldan, R., Gehrke, J., Horvitz, E., Kamar, E., Lee, P., Lee, Y.T., Li, Y., Lundberg, S., Nori, H., Palangi, 
H., Ribeiro, M.T., & Zhang, Y. Sparks of artificial general intelligence: Early experiments with GPT-4. arXiv preprintarXiv:​2303.​
12712 (2023).
	 3.	 Binz, M. & Schulz, E. Using cognitive psychology to understand GPT-3. Proc. Natl. Acad. Sci 120(6), e2218523120 (2023).
	 4.	 Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł., & Polosukhin, I. Attention is all you need. 
In Advances in Neural Information Processing System, 5998–6008 (2017).
	 5.	 Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, 
S., Herbert-Voss, A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D. M., Wu, J., Winter, C., Hesse, C., Chen, M., Sigler, 
E., Litwin, M., Gray, S., Chess, B., Clark, J., Berner, C., McCandlish, S., Radford, A., Sutskever, I., & Amodei, D. Language models 
are Few-Shot learners. In Advances in Neural Information Processing Systems, 1877–1901 (2020).
	 6.	 OpenAI. GPT-4 technical report. arXiv preprintarXiv:​2303.​08774 (2023).
	 7.	 Kosinski, M. Theory of mind may have spontaneously emerged in large language models. arXiv preprintarXiv:​2302.​02083 (2023).
	 8.	 Marjieh, R., Sucholutsky, I., van Rijn, P., Jacoby, N., & Griffiths, T.L. Large language models predict human sensory judgments 
across six modalities. arXiv preprintarXiv:​2302.​01308 (2023).
	 9.	 Kriegeskorte, N. & Kievit, R. A. Representational geometry: Integrating cognition, computation, and the brain. Trends Cogn. Sci 
17, 401–412 (2013).
	10.	 Roads, B. D. & Love, B. C. Modeling similarity and psychological space. Annu. Rev. Psychol. 75, 215–40 (2024).
	11.	 Williams, A., Kunz, E., Kornblith, S. & Linderman, S. Generalized shape metrics on neural representations. Adv. Neural Inf. Process. 
Syst. 34, 4738–4750 (2021).
	12.	 Marjieh, R., van Rijn, P., Sucholutsky, I., Sumers, T. R., Lee, H., Griffiths, T. L., & Jacoby, N. Words are all you need? Capturing 
human sensory similarity with textual descriptors. arXiv preprintarXiv:​2206.​04105 (2022).
	13.	 Marjieh, R., Sucholutsky, I., Sumers, T. R., Jacoby, N., & Griffiths, T. L. Predicting human similarity judgments using large language 
models. arXiv preprintarXiv:​2202.​04728 (2022).
	14.	 Sasaki, M., Takeda, K., Abe, K., Oizumi M. Toolbox for Gromov–Wasserstein optimal transport: Application to unsupervised 
alignment in neuroscience. bioRxiv (2023).
	15.	 Mémoli, F. Gromov–Wasserstein distances and the metric approach to object matching. Found Comput. Math. 11, 417–487 (2011).
	16.	 Peyré, G., & Cuturi, M. Computational optimal transport. arXiv preprintarXiv:​1803.​00567 (2020).
	17.	 Alvarez-Melis, D., & Jaakkola, T. S. Gromov–Wasserstein alignment of word embedding spaces. In Proceedings of the 2018 Confer‑
ence on Empirical Methods in Natural Language Processing, 1881–1890 (2018).
	18.	 Demetci, P., Santorella, R., Sandstede, B., Noble, W.S., & Singh, R. Gromov–Wasserstein optimal transport to align single-cell 
multi-omics data. bioRxiv (2020).
	19.	 Kawakita, G., Zeleznikow-Johnston, A., Takeda, K., Tsuchiya, N. & Oizumi, M. Is my “red” your “red”?: Unsupervised alignment 
of qualia structures via optimal transport. PsyArXiv preprinthttps://​doi.​org/​10.​31234/​osf.​io/​h3pqm (2023).
	20.	 Epping, G. P., Fisher, E. L., Zeleznikow-Johnston, A., Pothos, E. & Tsuchiya, N. A quantum geometric model of color similarity 
judgements. Cogn. Sci. 47, e13231 (2023).
	21.	 Zeleznikow-Johnston, A., Aizawa, Y., Yamada, M. & Tsuchiya, N. Are color experiences the same across the visual field?. J. Cogn. 
Neurosci. 35(4), 509–542 (2023).
(3)
Match(i) =

1, if Ŵij = maxj∈{1,...,n}(Ŵij) and c1i = c2j
0, otherwise
(4)
Matching Rate =
n
i=1 Match(i)
n
(5)
min
Q X −QYŴ∗2
F,


## Page 10

10
Vol:.(1234567890)
Scientific Reports |        (2024) 14:15917  | 
https://doi.org/10.1038/s41598-024-65604-1
www.nature.com/scientificreports/
	22.	 Birch, J. Efficiency of the Ishihara test for identifying red–green colour deficiency. Ophthalmic Physiol. Opt. 17(5), 403–408 (1997).
	23.	 Pouw, A., Karanjia, R. & Sadun, A. A method for identifying color vision deficiency malingering. Graefes Arch. Clin. Exp. Oph‑
thalmol. 255(3), 613–618 (2017).
	24.	 Saji, N., Imai, M. & Asano, M. Acquisition of the meaning of the word orange requires understanding of the meanings of red, pink, 
and purple: Constructing a lexicon as a connected system. Cogn. Sci. 44(1), e12813 (2020).
	25.	 Winawer, J. et al. Russian blues reveal effects of language on color discrimination. Proc. Natl. Acad. Sci. USA 104(19), 7780–85 
(2007).
	26.	 Hebart, M. N., Zheng, C. Y., Pereira, F. & Baker, C. I. Revealing the multi-dimensional mental representations of natural objects 
underlying human similarity judgements. Nat. Hum. Behav. 4(11), 1173–1185 (2020).
	27.	 Hebart, M. N. et al. THINGS-data: A multimodal collection of large-scale datasets for investigating object representations in brain 
and behavior. eLife 12, e82580 (2023).
	28.	 Sharma, G., Wu, W. & Dalal, E. N. The CIEDE2000 color-difference formula: Implementation notes, supplementary test data, and 
mathematical observations. Color Res. Appl. 30(1), 21–30 (2005).
	29.	 Peyré, G., Cuturi, M., & Solomon, J. Gromov–Wasserstein averaging of kernel and distance matrices. In International Conference 
on Machine Learning, 2664–2672 (2016).
	30.	 Akiba, T., Sano, S., Yanase, T., Ohta, T., & Koyama, M. Optuna: A next-generation hyperparameter optimization framework. In 
Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, 2623–2631 (2019).
	31.	 Flamary, R. et al. Pot: Python optimal transport. J. Mach. Learn. Res. 22, 1–8 (2021).
Acknowledgements
G.K. and M.O. were supported by JST Moonshot R &D Grant Number JPMJMS2012. N.T. and M.O. were 
supported by Japan Promotion Science, Grant-in-Aid for Transformative Research Areas Grant Numbers 
20H05710, 23H04830 (N.T.) and 20H05712, 23H04834 (M.O.). N.T. was supported by Australian Research 
Council (DP180104128, DP180100396). N.T. and A.Z.J. were supported by National Health Medical Research 
Council (APP1183280) and Foundational Question Institute (FQXi-RFP-CPW-2017) and Fetzer Franklin Fund, 
a donor advised fund of Silicon Valley Community Foundation. We thank Dominik Kirsten-Parsch and Lonni 
Gomes for their help in collecting the color dissimilarity data.
Author contributions
G.K. and M.O. conceived the idea. G.K. ran experiments to collect the data from GPTs. A.Z.J. and N. T. designed 
and performed experiments to collect the data from human participants. G.K. and M.O. analyzed the data. G.K. 
and M.O. wrote the initial draft of the manuscript. All authors reviewed the manuscript, read and approved its 
final version.
Competing interests 
The authors declare no competing interests.
Additional information
Supplementary Information The online version contains supplementary material available at https://​doi.​org/​
10.​1038/​s41598-​024-​65604-1.
Correspondence and requests for materials should be addressed to G.K. or M.O.
Reprints and permissions information is available at www.nature.com/reprints.
Publisher’s note  Springer Nature remains neutral with regard to jurisdictional claims in published maps and 
institutional affiliations.
Open Access   This article is licensed under a Creative Commons Attribution 4.0 International 
License, which permits use, sharing, adaptation, distribution and reproduction in any medium or 
format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the 
Creative Commons licence, and indicate if changes were made. The images or other third party material in this 
article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the 
material. If material is not included in the article’s Creative Commons licence and your intended use is not 
permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from 
the copyright holder. To view a copy of this licence, visit http://​creat​iveco​mmons.​org/​licen​ses/​by/4.​0/.
© The Author(s) 2024


