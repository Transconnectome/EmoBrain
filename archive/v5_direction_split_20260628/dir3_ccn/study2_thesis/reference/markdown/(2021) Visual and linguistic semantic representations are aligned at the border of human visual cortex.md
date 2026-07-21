# (2021) Visual and linguistic semantic representations are aligned at the border of human visual cortex

**Source:** (2021) Visual and linguistic semantic representations are aligned at the border of human visual cortex.pdf

---

## Page 1

Articles
https://doi.org/10.1038/s41593-021-00921-6
1Helen Wills Neuroscience Institute, University of California, Berkeley, Berkeley, CA, USA. 2Department of Psychology, University of California, 
Berkeley, Berkeley, CA, USA. 3Present address: Departments of Neuroscience & Computer Science, The University of Texas at Austin, Austin TX, 
USA. 4Present address: Department of Software Engineering and Theoretical Computer Science, Technische Universität Berlin, Berlin, Germany. 
✉e-mail: gallant@berkeley.edu
H
umans can visually recognize thousands of objects and 
actions in the natural world, and they can communicate and 
reason about these semantic categories through language. 
This flexible language capacity suggests that there might be a rich 
connection between the functional networks that represent seman-
tic information acquired directly through the senses and semantic 
information conveyed in spoken language1–3. There are currently 
two prevailing theories of how semantic information from vision, 
language and other modalities are combined. The hub-and-spoke 
view3 holds that unimodal processing units in modality-specific 
cortex are independent spokes that converge at the amodal hub in 
the anterior temporal lobe (ATL). This model is consistent with 
evidence that ATL degeneration results in semantic dementia4–6, 
whereas other aspects of cognition (syntax, numerical abilities and 
executive function) appear to be relatively spared7–10. In contrast, 
the convergence zone view2,11,12 holds that modality-specific and 
amodal semantic representations are combined at multiple points 
across the cortex, outside of the ATL. This view is supported by 
evidence that other regions, such as the angular gyrus, precuneus 
and middle temporal gyrus, respond to the same semantic category 
whether presented either visually or through language13,14.
Functional magnetic resonance imaging (fMRI) studies have 
provided substantial evidence that visual semantic information is 
represented as a mosaic of modality- and category-specific func-
tional areas that are distributed across anterior portions of occipital 
cortex and posterior temporal and parietal cortex15–18. Furthermore, 
we recently showed that semantic information during narrative lan-
guage comprehension is represented as a mosaic of category-specific 
functional areas located anterior to visual cortex19, and further work 
from our lab showed that the semantic selectivity for most of this 
mosaic is the same for both listening and reading20. Finally, past 
studies reported that some regions along the border between these 
two networks appear to represent the same semantic category when 
it is presented either visually or through language13,14, a finding 
that we have replicated independently18,19 (Fig. 1). Therefore, one 
interesting possibility is that information from the modal visual 
semantic system enters the amodal semantic system along a set of 
parallel semantically selective pathways that are arranged along the 
border between these networks. Evidence supporting this hypoth-
esis would lend more support to the convergence zone view of 
semantic cognition, as this border would effectively form a network 
of convergence zones.
This possibility suggests a strong and novel prediction about the 
relationship between functional semantic maps anterior and pos-
terior to the border: for each location along the anterior border of 
visual cortex that is selective for a particular visual category, there 
should be an area immediately anterior to it that is selective for that 
same semantic category in language. Hereafter, we will refer to this 
as the ‘semantic alignment hypothesis’.
Results
To test this semantic alignment hypothesis, we compared semantic 
maps obtained in two different experiments in the same partici-
pants: a vision experiment that used natural movies as stimuli18 and 
a language experiment that used naturally spoken narrative stories 
as stimuli19. We used the data from these two fMRI experiments to 
construct two sets of voxel-wise encoding models21–24. These models 
predict blood oxygen level-dependent (BOLD) responses in each 
voxel in each individual brain, based on the semantic content of the 
movies and stories. To do this, we first created a 985-dimensional 
semantic feature space based on the co-occurrence statistics of words 
in a large corpus of English text (details in Methods). Then, seman-
tic features in the movie experiment were obtained by labeling each 
object and action in the movies using WordNet25 and projecting 
those labels into the 985-dimensional feature space19. Semantic fea-
tures in the language experiment were obtained by projecting each 
word in the stories into the same 985-dimensional feature space. 
Next, for each voxel in each participant, separate visual and linguis-
tic encoding models were estimated through regularized regression. 
The fit regression weights indicate how each semantic category in 
Visual and linguistic semantic representations are 
aligned at the border of human visual cortex
Sara F. Popham1, Alexander G. Huth1,3, Natalia Y. Bilenko1, Fatma Deniz1,4, James S. Gao1, 
Anwar O. Nunez-Elizalde1 and Jack L. Gallant   1,2 ✉
Semantic information in the human brain is organized into multiple networks, but the fine-grain relationships between them 
are poorly understood. In this study, we compared semantic maps obtained from two functional magnetic resonance imaging 
experiments in the same participants: one that used silent movies as stimuli and another that used narrative stories. Movies 
evoked activity from a network of modality-specific, semantically selective areas in visual cortex. Stories evoked activity from 
another network of semantically selective areas immediately anterior to visual cortex. Remarkably, the pattern of semantic 
selectivity in these two distinct networks corresponded along the boundary of visual cortex: for visual categories represented 
posterior to the boundary, the same categories were represented linguistically on the anterior side. These results suggest that 
these two networks are smoothly joined to form one contiguous map.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1628


## Page 2

Articles
NaTuRE NEuRoScIEncE
the movies or stories modulates BOLD signals evoked from each 
individual voxel and in every participant separately. Finally, we 
used these fit models to predict brain activity to new stimuli that 
were not used to train the models. From these predictions, we could 
then see whether the activity of each voxel was driven by visual 
and/or linguistic semantic information (Extended Data Fig. 1). 
b
a
S11
S2
S3
S1
S10
S4
S5
S8
S6
S7
S9
Weight correlation
0
0.5
NS
Fig. 1 | Voxels with correlated visual and linguistic semantic representations. a, Shown here is the flattened cortex around the occipital pole for one 
typical participant, along with inflated hemispheres. This map shows the correlation of the visual and linguistic model weights for each voxel. Only voxels 
with significant weight correlations (rweights > 0.0625, P < 0.05, two-sided, uncorrected) and high prediction performance of the semantic models (at least 
one with rperformance > 0.1) are shown. High correlation values indicate candidate multi-modal regions of the brain. There are clusters of voxels with high 
correlation values in the precuneus (PrCu) and angular gyrus (AG), which replicate previous findings that these are high-level semantic convergence 
zones. b, Flattened occipital lobes for the ten other participants. All participants show high correlation values in PrCu and AG, further supporting the 
possibility that these are high-level semantic convergence zones. NS, not significant.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1629


## Page 3

Articles
NaTuRE NEuRoScIEncE
By examining the patterns of semantic selectivity across these two 
models, we were able to test the hypothesis that there is a systematic 
spatial correspondence between the semantic networks selective for 
visual versus linguistic categories.
Preliminary inspection suggests semantic alignment. Before 
undertaking a thorough test of the semantic alignment hypothesis, 
we ran a preliminary test to determine if the hypothesis was plau-
sible. To do this, we examined a few semantic categories that are 
well-represented in anterior portions of the visual system: places, 
body parts and faces. Previous studies found that images of places, 
such as buildings, parks, streets, cities and mountains, selectively 
elicit responses in the parahippocampal place area (PPA16), occipi-
tal place area (OPA26–28) and retrosplenial complex (RSC29). The 
semantic alignment hypothesis predicts that areas that represent 
linguistic descriptions of places should be found in areas neighbor-
ing these known place-selective visual regions of interest (ROIs). To 
identify voxels that encode semantic information related to places 
in either modality, we used the vision and language model weights 
to quantify how much place-related information in the movies and 
in the stories is represented in the activity of each voxel (details in 
Methods). Figure 2a indicates that the voxels that represent place 
information in movies are concentrated in PPA, OPA and RSC, 
whereas voxels just anterior to these areas appear to represent place 
information in the stories (see Extended Data Fig. 2 for other par-
ticipants). A similar examination of semantic selectivity for body 
parts and faces suggests that these modality shifts from visual to 
linguistic semantic representations also appear along other por-
tions of the boundary of visual cortex (Fig. 2b,c and Extended Data 
Figs. 3 and 4). For example, voxels that represent body part informa-
tion in the stories appear to be located just anterior to the extrastri-
ate body area (EBA17), and voxels that represent face information 
in the stories appear to be located just anterior to the fusiform face 
area (FFA15). Each of these patterns appears in all 11 participants. 
(See Supplementary Table 1 for a full evaluation of each participant 
per ROI.) All of these qualitative observations are consistent with 
the semantic alignment hypothesis.
Analysis of modality shift magnitude around visual cortex. 
We next wanted to test whether a modality shift from visual to lin-
guistic representation of a single semantic category was a general 
property of the border of visual cortex. However, some portions 
of the border of occipital lobe are ill-defined; the only clear land-
marks are the parieto-occipital sulcus and the preoccipital notch30. 
Therefore, we manually defined the entire boundary in each partici-
pant individually. This border followed the parieto-occipital sulcus 
along the dorsal surface and then connected on both ends to the 
preoccipital notch on the ventral surface. When possible, the border 
followed sulcal fundi but otherwise took the shortest paths between 
these landmarks. Because this definition was approximate and not 
based on functional activations (for example, this border does not 
include areas with visual representations in temporal and pari-
etal cortex), later analyses were run on a larger area of the cortex. 
Thus, the analysis that searched for modality shifts was expanded 
to all vertices within 50 mm of the drawn border. The extent of the 
areas selected for further analysis in each participant is shown in 
Extended Data Fig. 5.
To quantify the effects that Fig. 2 shows qualitatively, we designed 
a method to search exhaustively for all locations where there was 
a modality shift from visual to linguistic representation of a single 
semantic category (Fig. 3). In our analysis, each participant’s cor-
tical surface is formed from a triangular mesh that is made up of 
approximately 150,000 vertices per hemisphere. We chose to search 
for modality shifts at vertices within the analysis region shown in 
Extended Data Fig. 5. Modality shifts were calculated at all possible 
angles through each location using an algorithm that maps geodesic 
lines onto the surface of the brain (Fig. 3a). Next, a window around 
each line was selected, and we looked for a modality shift within 
each window. Each vertex in the window was given a coordinate 
along the geodesic line (Fig. 3b).
To understand how semantic representations changed both 
visually and linguistically along the length of the window, we first 
needed to determine the average semantic concept that was rep-
resented within the entire window for each modality. The average 
semantic tuning within each window was found by calculating the 
mean vision model weights and language model weights for all ver-
tices, within each modality separately. For each vertex, the vision 
and language model weights were projected onto that average visual 
model weight vector. Then, to measure representational shifts along 
the region, a linear regression model was fit for the weight projec-
tions as a function of coordinate along the line (Fig. 3c). This was 
done separately for the movie and story weight projections. Finally, 
we created a single metric that could describe locations where the 
visual representations were getting weaker and the linguistic rep-
resentations were getting stronger along the length of the win-
dow—and that, in fact, there is a shift from one modality to another 
(equation in Fig. 3c; see Methods for details). This entire process 
was then repeated for the average linguistic model weight vector, 
and the stronger of the two metrics was retained. There were some 
important edge cases that we specifically chose to avoid when con-
structing the metric. Examples of these types of windows are shown 
in Fig. 3d–h, and they all have very small modality shift metrics, 
as intended. These examples show why this metric is superior to a 
simpler metric, such as correlation of weights across two halves of 
the window. In d, the visual representation is not changing strongly 
over the course of the window, as indicated by the flat red line. In 
e, the same is true for the linguistic representation, as indicated by 
the flat blue line. In f, both the visual and linguistic representations 
do not change much over the course of the window, but the aver-
age weights across models are correlated. In g, the analysis window 
seems to be approaching the boundary between visual and linguis-
tic representations, but the regression lines for each modality do not 
cross within the window. In h, the visual and linguistic representa-
tions are actually diverging from each other. The negative examples 
shown in d–h indicate that we were successful in creating a modal-
ity shift metric that is specific to only the representational shift, 
which is consistent with the semantic alignment hypothesis. These 
edge cases might have been incorrectly identified as modality shifts 
through alternative analysis methods.
To evaluate the significance of these modality shifts, we con-
structed a permutation test that would reveal which shifts were 
semantically specific to only the concept represented in that win-
dow. A null distribution was obtained by replacing all vertices 
from one modality, and their respective model weights, with those 
of other windows across the cortical surface for each participant. 
In this test, the permuted modality was the one that was not used 
as the average semantic weight vector in the original calculation of 
the metric.
Because all 11 participants took part in both experiments, we 
were able to analyze data within each participant individually, 
resulting in 11 separate and independent tests of this hypoth-
esis. Additionally, we separated our data for training and valida-
tion at two different points in the analysis pipeline. First, the data 
acquired from each participant were divided into separate fit and 
test sets for initial encoding model fitting. Then, because the data 
analysis procedures that we used while refining our methods were 
heavily exploratory, we restricted all pilot analyses to only par-
ticipants 1–5. This was done to avoid overfitting and to ensure 
that our results would generalize to new participants. The results 
for all 11 participants are presented here, but it is important to 
note that the analysis pipeline was frozen before it was applied to 
participants 6–11.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1630


## Page 4

Articles
NaTuRE NEuRoScIEncE
In all 11 participants, we found significant (false discovery 
rate (FDR) corrected, q < 0.05) modality shifts for semantic cat-
egories located along almost the entire boundary of visual cortex. 
These regions include the visual category-selective regions dis-
cussed above as well as other semantically selective regions that 
were not distinguished as visual ROIs in previous localizer studies 
but which we reported earlier as, indeed, semantically selective14 
(Fig. 4). The only regions where we cannot yet verify this pattern 
are where MRI dropout obscures functional signals (see the purple 
hatch marks in Fig. 4). (The dropout regions are voxels with a low 
signal-to-fluctuation-noise ratio (SFNR; ref. 31), and these tend to 
occur in areas of the brain that are near tissues that are magnetically 
inhomogeneous, such as air sinuses32. See Methods for details on 
calculation of SFNR.)
Figure 4 also shows that there are a few regions of modality shifts 
that are directed anterior to posterior at locations that do not fall 
along the boundary of visual cortex, such as the right posterior supe-
rior temporal sulcus (pSTS) in Fig. 4a. The modality shifts point in 
this direction because the visual semantic selectivity in pSTS is sim-
ilar to the linguistic semantic selectivity of voxels just posterior to 
that region. However, because these modality shifts do not lie along 
the boundary of visual cortex, they are not within the scope of this 
manuscript and, therefore, will not be discussed further.
The modality shift metric was designed to identify locations 
where there is a strong shift between two unimodal representa-
tions of the same semantic category. However, the correlation of 
the semantic weights themselves are not directly used in the met-
ric calculation. To directly quantify the semantic correspondence 
a
RSC
RSC
OPA
PPA
PPA
OPA
c
b
EBA
EBA
FFA
FFA
S10
S9
S8
Language representation 
of face concept
Neither
Just
visual
Just
language
Both
Language representation 
of body concept
Neither
Just
visual
Just
language
Both
Language representation
of place concept 
Visual representation
of face concept 
Visual representation
of body concept 
Visual representation
of place concept 
Neither
Just
visual
Just
language
Both
Fig. 2 | Visual and linguistic representations of semantic concepts known to be well-represented in visual cortex. a, Shown here is the flattened cortex 
around the occipital pole for one typical participant, along with inflated hemispheres. The color of each voxel indicates the representation of place-related 
information according to the legend at the right. The model weights for vision and language are shown in red and blue, respectively. White borders indicate 
ROIs found in separate localizer experiments. Three relevant place ROIs are labeled: PPA, OPA and RSC. Centered on each ROI, there is a modality shift 
gradient that runs from visual semantic categories (red) posterior to linguistic semantic categories (blue) anterior. b, Format is the same as a except that 
one body ROI is labeled: EBA. EBA also shows a modality shift gradient that runs from visual to linguistic in this example participant. c, Format is the same 
as a and b except that one face ROI is labeled: FFA. FFA also shows a modality shift gradient that runs from visual to linguistic in this example participant. 
All of these qualitative observations are consistent with the semantic alignment hypothesis.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1631


## Page 5

Articles
NaTuRE NEuRoScIEncE
across the boundary that was found, each significant window was 
divided into visual and linguistic portions. This division occurred at 
the point where the two fit lines crossed (see variable P in Fig. 3c). 
Then, the average of the visual model weights in the visual portion 
of the window was correlated with the average linguistic model 
weights in the linguistic portion of the window. The correlation 
b
Position along window
c
Lm
Vm
Lm
Vm
,
R = sign(VmLm)min
M =
Vm + Lm
2
Modality
shift
metric
Language weights
Vision weights
Language fit
Vision fit
Position along window (mm)
Projection onto semantic vector
0.04
0.03
0.02
0.01
0
[Vi,Vm]
[Li,Lm]
d
e
f
g
0.04
0.03
0.02
0.01
0
0.04
0.03
0.02
0.01
0
0.04
0.03
0.02
0.01
0
0.04
0.03
0.02
0.01
0
Position along window (mm)
Vm – Lm
Li – Vi
P =
C =
Min(X) < P <max(X)
otherwise
1
0
Projection onto
semantic vector
Projection onto
semantic vector
Projection onto
semantic vector
Projection onto
semantic vector
S = 5.81 × 10–4
S = –1 × 10–6
S = 2 × 10–6
S = 0
P
h
0.03
0.02
0.01
0.00
–0.01
Projection onto
semantic vector
S = 0
Y =
1
otherwise
YV
n
*
YL
n
> 0
0
a
0
12.5
25
Position along window (mm)
0
12.5
25
Position along window (mm)
0
12.5
25
Position along window (mm)
0
12.5
25
Position along window (mm)
0
12.5
25
0
5
10
15
20
25
S = –R*M*C*Y 
S = –2 × 10–6
Fig. 3 | Method for detecting category-specific modality shifts. Modality shifts were estimated at thousands of locations near the boundary of the 
occipital lobe for each participant individually. Calculating the modality shift metric required three steps. a, First, for each location, possible modality 
gradient axes were identified by generating geodesic lines in all directions centered on the location. Here, one example location is shown in red, and 
geodesic lines are shown in black. b, Second, for each geodesic line, a window was centered on the line, and each vertex in the window was assigned a 
coordinate. One example is shown here, where each vertex is colored according to its coordinate. c, Third, the magnitude of the modality shift along the 
length of each window was estimated in terms of a summary metric, S. The average semantic concept that was represented in each window was found 
by calculating the mean of the vision and language model weights across all vertices in the window. Then, the visual and linguistic representations of that 
concept were calculated at each vertex as the projection of the weights of that vertex onto the average weights. In this panel, each location is plotted 
twice, once in red for its vision weight projection and once in blue for its language weight projection. Linear regression was then used to fit lines to these 
values. The intercepts (Li, Vi) and slopes (Lm, Vm) of these lines were used to derive the modality shift metric, S. Shown here is a region that is fit well by this 
model. This process is repeated for each location on each brain, and the full results of that analysis are shown in Fig. 3. d–h, These five examples illustrate 
why the chosen analysis method is optimal. This method selects only regions where there is a strong shift from visual to linguistic representation and not 
other related changes in semantic representation. We specifically constructed the modality shift metric, S, to be small in all five of these edge cases.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1632


## Page 6

Articles
NaTuRE NEuRoScIEncE
0
+
Modality shift (a.u.)
b
a
S11
S2
S3
S1
S10
S4
S5
S8
S6
S7
S9
Fig. 4 | Locations of category-specific modality shifts across cortex. a, Shown here is the flattened cortex around the occipital pole for one typical 
participant, along with inflated hemispheres. The modality shift metric calculated at each location near the boundary of the occipital lobe is plotted 
as arrows on the flattened cortex and on inflated hemispheres. The color of each arrow indicates the magnitude of the shift (a.u., arbitrary units). The 
direction of each arrow indicates the shift from vision to language. Arrows are shown only at locations where the modality shift is statistically significant 
(P < 0.05, one sided, FDR corrected). Areas of fMRI signal dropout are indicated with purple hatch marks. There are strong modality shifts in a clear ring 
around the anterior border of visual cortex. b, Flattened occipital lobes for the ten other participants. All participants show the same pattern of strong 
modality shifts organized into a clear ring around visual cortex.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1633


## Page 7

Articles
NaTuRE NEuRoScIEncE
value for each window is shown in Fig. 5. The vast majority of these 
correlations are strongly positive, which shows that our modal-
ity shift analysis is picking up on semantic correlation across the 
boundary as expected.
It is important to note that the results shown in Fig. 5 alone 
are not sufficient support for the semantic alignment hypothesis. 
The modality shift analysis shown in Fig. 4 was absolutely neces-
sary to identify the location of the boundary. The negative examples 
b
a
S11
S2
S3
S1
S10
S4
S5
S8
S6
S7
S9
–0.3
+0.3
Weight correlation
Fig. 5 | Quantitative summary of semantic correspondence across the boundary. a, Flattened cortex around the occipital pole for one typical 
participant, along with inflated hemispheres. Arrows indicate the correlation between semantic selectivity of vertices on each side of the visual–
linguistic boundary. Red indicates positive correlations, blue indicates negative correlations and arrow weight indicates the strength of correlation.  
b, Flattened occipital lobes for the ten other participants. All participants show the same pattern of semantic correlations organized into a clear  
ring around visual cortex.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1634


## Page 8

Articles
NaTuRE NEuRoScIEncE
presented in Fig. 3d–f indicate why this is the case. The correlation 
value for each of those windows is significant and positive; how-
ever, none of these examples are the shifts from visual to linguistic 
representation that we are looking for. If only the results in Fig. 5 
were presented, we would be drawing incorrect conclusions about 
the semantic alignment at those cortical locations. Therefore, it 
is important to consider the results presented in Fig. 5 only after 
having completed the modality shift analysis (Figs. 3 and 4). Taken 
together, Figs. 4 and 5 suggest that the two individual semantic 
maps are indeed aligned along the anterior border of visual cortex.
The analyses in Figs. 3–5 strongly support the semantic align-
ment hypothesis. However, it is not clear from these analyses which 
semantic categories are actually represented along the visual cor-
tex boundary. To examine this, we plotted a subset of the semantic 
model weights onto the cortical sheet along this boundary (Fig. 6). 
Figure 6 shows that a wide variety of semantic concepts are rep-
resented along the anterior boundary of visual cortex. Inspection 
reveals a clear spatial correspondence of the visual and linguistic 
maps. The only exception seems to be ‘mental’ concepts (purple ver-
tices located in dorsal region of boundary), which appear to be rep-
resented only in the stories. However, these abstract concepts were 
not labeled explicitly in the movies and, therefore, cannot be found 
in our visual semantic maps. This does not necessarily mean that 
the two semantic maps are misaligned at these locations, but future 
experiments and analyses would be required to resolve this matter.
Discussion
The results presented here support the semantic alignment hypothe-
sis, which is that, for each location along the anterior border of visual 
cortex that is selective for a particular visual category, there is an area 
immediately anterior to it that is selective for that same semantic 
category in language. This suggests that the border of visual cortex 
acts as a convergence zone where information from the modal visual 
semantic system enters the amodal semantic system along a set of 
parallel, semantically selective pathways. Given the close spatial 
proximity and correspondence of these modal and amodal semantic 
maps, we speculate that this functional arrangement likely reflects 
direct anatomical connections between corresponding modal and 
amodal semantically selective areas33–35. However, we cannot evalu-
ate this possibility with the data available currently.
If these pathways provide a direct route from the visual semantic 
system into the amodal semantic system, bypassing the ATL, then 
what are we to make of the extensive evidence that ATL lesions 
impair semantic recognition3–6? We suspect that the pathways that 
we identified here connect modal visual experience to amodal rep-
resentations, but these amodal representations alone are not suf-
ficient to provide semantic labels to sensory experience. Instead, 
semantic comprehension also requires input from the memory 
system. This is provided by pathways that proceed through the 
ATL. This explanation would reconcile the large body of research 
supporting both the hub-and-spoke model and the theory of 
c
a
S11
S2
S3
S1
S10
S4
S5
S8
S6
S7
S9
Shifts from vision
to language
Vision vertices
Language vertices
S11
b
Violence
Body part
Number
Person
Social
Mental
Place
Time
Outdoor
Tactile
Visual
Fig. 6 | Alignment of semantic selectivity along the boundary between vision and language. a, Semantic selectivity of vertices near the visual–linguistic 
boundary shown on the flattened cortex around the occipital pole for one typical participant. Vertices selective for visual semantics are shown in red, those 
selective for language semantics are shown in blue and those selective for both types of information are shown in black. b, The flattened cortex around the 
occipital pole, along with inflated hemispheres, for the same participant shown in a. Each vertex that is selective for either visual or linguistic categories 
is colored according to its semantic selectivity. The pattern of semantic selectivity corresponds along both sides of the visual–linguistic boundary in most 
locations. c, Semantic selectivity for the ten remaining participants, which all show a similar pattern to the participant shown in b.
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1635


## Page 9

Articles
NaTuRE NEuRoScIEncE
high-level convergence zones. In other words, these two theories 
might merely describe different aspects of semantic comprehension.
We cannot comment on the nature of the semantic represen-
tations in the ATL in this study. This is because the fMRI pulse 
sequences used here were optimized for the cortex as a whole rather 
than for specifically recovering signal in the ATL. Because the ATL 
is particularly susceptible to signal dropout, it is nearly impossible 
to study the ATL effectively without specialized pulse sequences36. 
In the future, we hope to look deeper into this topic with a targeted 
study of the ATL using the methods presented here.
We speculate that the precise spatial relationship that we report 
here between visual semantic maps and amodal language maps 
might also occur in other modal semantic systems. For example, 
the auditory semantic maps found in the temporal lobe37,38 might 
be spatially aligned with nearby amodal semantic maps, and the 
same might be true of unimodal somatosensory semantic maps. 
Performing detailed semantic mapping in every modality thus has 
the potential to reveal the entire network of convergence zones that 
feed modal sensory information into the amodal semantic network.
Our results also raise the interesting possibility that the organi-
zation of the modal and amodal semantic systems might influence 
one another during development. Because the large-scale organiza-
tion of category-selective areas in visual cortex appears to depend 
on genetically encoded gradients, such as retinotopy39, it seems 
most likely that the organization of the amodal semantic system is 
influenced by the visual semantic system. One possible way to test 
this hypothesis would be to map the semantic representation of nar-
rative language comprehension in congenitally blind participants. 
If their amodal semantic representations near occipital cortex are 
organized differently than those found in sighted participants, it 
would support the idea that organization of the amodal semantic 
system is shaped by the visual semantic system. If not, it might sug-
gest that other factors influence the organization of both systems.
Online content
Any methods, additional references, Nature Research report-
ing summaries, source data, extended data, supplementary infor-
mation, acknowledgements, peer review information; details of 
author contributions and competing interests; and statements of 
data and code availability are available at https://doi.org/10.1038/
s41593-021-00921-6.
Received: 28 June 2019; Accepted: 11 August 2021;  
Published online: 28 October 2021
References
	1.	 Barsalou, L. W. Perceptual symbol systems. Behav. Brain Sci. 22, 577–609 (1999).
	2.	 Damasio, A. R. The brain binds entities and events by multiregional 
activation from convergence zones. Neural Comput. 1, 123–132 (1989).
	3.	 Ralph, M. A. L., Jefferies, E., Patterson, K. & Rogers, T. T. The neural and 
computational bases of semantic cognition. Nat. Rev. Neurosci. 18, 42–55 (2017).
	4.	 Snowden, J. S., Goulding, P. J. & Neary, D. Semantic dementia: a form of 
circumscribed cerebral atrophy. Behav. Neurol. 2, 167–182 (1989).
	5.	 Warrington, E. K. The selective impairment of semantic memory. Q. J. Exp. 
Psychol. 27, 635–657 (1975).
	6.	 Wilkins, A. & Moscovitch, M. Selective impairment of semantic memory 
after temporal lobectomy. Neuropsychologia 16, 73–79 (1978).
	7.	 Jefferies, E., Patterson, K., Jones, R. W., Bateman, D. & Lambon Ralph, M. A. 
A category-specific advantage for numbers in verbal short-term memory: 
evidence from semantic dementia. Neuropsychologia 42, 639–660 (2004).
	8.	 Kramer, J. H. et al. Distinctive neuropsychological patterns in frontotemporal 
dementia, semantic dementia, and Alzheimer disease. Cogn. Behav. Neurol. 
16, 211–218 (2003).
	9.	 Hodges, J. R., Patterson, K., Oxbury, S. & Funnell, E. Semantic dementia. 
Progressive fluent aphasia with temporal lobe atrophy. Brain 115,  
1783–1806 (1992).
	10.	Hodges, J. R. et al. The differentiation of semantic dementia and frontal lobe 
dementia (temporal and frontal variants of frontotemporal dementia) from 
early Alzheimer’s disease: a comparative neuropsychological study. 
Neuropsychology 13, 31–40 (1999).
	11.	Damasio, H., Grabowski, T. J., Tranel, D., Hichwa, R. D. & Damasio, A. R. A 
neural basis for lexical retrieval. Nature 380, 499–505 (1996).
	12.	Damasio, H., Tranel, D., Grabowski, T., Adolphs, R. & Damasio, A. Neural 
systems behind word and concept retrieval. Cognition 92, 179–229 (2004).
	13.	Devereux, B. J., Clarke, A., Marouchos, A. & Tyler, L. K. Representational 
similarity analysis reveals commonalities and differences in the semantic 
processing of words and objects. J. Neurosci. 33, 18906–18916 (2013).
	14.	Fairhall, S. L. & Caramazza, A. Brain regions that represent amodal 
conceptual knowledge. J. Neurosci. 33, 10552–10558 (2013).
	15.	Kanwisher, N., McDermott, J. & Chun, M. M. The fusiform face area:  
a module in human extrastriate cortex specialized for face perception.  
J. Neurosci. 17, 4302–4311 (1997).
	16.	Epstein, R. & Kanwisher, N. A cortical representation of the local visual 
environment. Nature 392, 598–601 (1998).
	17.	Downing, P. E., Jiang, Y., Shuman, M. & Kanwisher, N. A cortical area selective 
for visual processing of the human body. Science 293, 2470–2473 (2001).
	18.	Huth, A. G., Nishimoto, S., Vu, A. T. & Gallant, J. L. A continuous semantic 
space describes the representation of thousands of object and action 
categories across the human brain. Neuron 76, 1210–1224 (2012).
	19.	Huth, A. G., de Heer, W. A., Griffiths, T. L., Theunissen, F. E. & Gallant, J. L. 
Natural speech reveals the semantic maps that tile human cerebral cortex. 
Nature 532, 453–458 (2016).
	20.	Deniz, F., Nunez-Elizalde, A. O., Huth, A. G. & Gallant, J. L. The 
representation of semantic information across human cerebral cortex during 
listening versus reading is invariant to stimulus modality. J. Neurosci. 39, 
7722–7736 (2019).
	21.	Kay, K. N., Naselaris, T., Prenger, R. J. & Gallant, J. L. Identifying natural 
images from human brain activity. Nature 452, 352–355 (2008).
	22.	Mitchell, T. M. et al. Predicting human brain activity associated with the 
meanings of nouns. Science 320, 1191–1195 (2008).
	23.	Naselaris, T., Kay, K. N., Nishimoto, S. & Gallant, J. L. Encoding and 
decoding in fMRI. Neuroimage 56, 400–410 (2011).
	24.	Nishimoto, S. et al. Reconstructing visual experiences from brain activity 
evoked by natural movies. Curr. Biol. 21, 1641–1646 (2011).
	25.	Miller, G. A. WordNet: a lexical database for English. Commun. ACM 38, 
39–41 (1995).
	26.	Nakamura, K. et al. Functional delineation of the human occipito-temporal 
areas related to face and scene processing. A PET study. Brain 123, 
1903–1912 (2000).
	27.	Hasson, U., Harel, M., Levy, I. & Malach, R. Large-scale mirror-symmetry 
organization of human occipito-temporal object areas. Neuron 37,  
1027–1041 (2003).
	28.	Dilks, D. D., Julian, J. B., Paunov, A. M. & Kanwisher, N. The occipital place 
area is causally and selectively involved in scene perception. J. Neurosci. 33, 
1331–6a (2013).
	29.	Aguirre, G. K., Zarahn, E. & D’Esposito, M. An area within human ventral 
cortex sensitive to ‘building’ stimuli: evidence and implications. Neuron 21, 
373–383 (1998).
	30.	Ono, M., Kubik, S. & Abernathy, C. D. Atlas of the Cerebral Sulci (Thieme 
Medical Publishers, 1990).
	31.	Friedman, L. & Glover, G. H., Fbirn Consortium. Reducing interscanner 
variability of activation in a multicenter fMRI study: controlling for 
signal-to-fluctuation-noise-ratio (SFNR) differences. Neuroimage 33,  
471–481 (2006).
	32.	Ojemann, J. G. et al. Anatomic localization and quantitative analysis of 
gradient refocused echo-planar fMRI susceptibility artifacts. Neuroimage 6, 
156–167 (1997).
	33.	Van Essen, D. C., Anderson, C. H. & Felleman, D. J. Information processing 
in the primate visual system: an integrated systems perspective. Science 255, 
419–423 (1992).
	34.	Modha, D. S. & Singh, R. Network architecture of the long-distance pathways 
in the macaque brain. Proc. Natl Acad. Sci. USA 107, 13485–13490 (2010).
	35.	Ercsey-Ravasz, M. et al. A predictive network model of cerebral cortical 
connectivity based on a distance rule. Neuron 80, 184–197 (2013).
	36.	Visser, M., Jefferies, E. & Lambon Ralph, M. A. Semantic processing in the 
anterior temporal lobes: a meta-analysis of the functional neuroimaging 
literature. J. Cogn. Neurosci. 22, 1083–1094 (2009).
	37.	Lewis, J. W., Talkington, W. J., Puce, A., Engel, L. R. & Frum, C. Cortical 
networks representing object categories and high-level attributes of familiar 
real-world action sounds. J. Cogn. Neurosci. 23, 2079–2101 (2011).
	38.	Norman-Haignere, S., Kanwisher, N. G. & McDermott, J. H. Distinct cortical 
pathways for music and speech revealed by hypothesis-free voxel 
decomposition. Neuron 88, 1281–1296 (2015).
	39.	Levy, I., Hasson, U., Avidan, G., Hendler, T. & Malach, R. Center–periphery 
organization of human object areas. Nat. Neurosci. 4, 533 (2001).
Publisher’s note Springer Nature remains neutral with regard to jurisdictional claims in 
published maps and institutional affiliations.
© The Author(s), under exclusive licence to Springer Nature America, Inc. 2021
Nature Neuroscience | VOL 24 | November 2021 | 1628–1636 | www.nature.com/natureneuroscience
1636


## Page 10

Articles
NaTuRE NEuRoScIEncE
Methods
This study was approved by the Committee for Protection of Human Subjects at the 
University of California, Berkeley. All participants gave informed consent.
MRI data collection. MRI data were collected on a 3T Siemens Tim Trio scanner 
at the University of California, Berkeley Brain Imaging Center using a 32-channel 
Siemens volume coil. MRI data were collected using syngo MR software distributed 
by Siemens (versions 15 and 17A). Functional scans were collected using gradient 
echo EPI with repetition time (TR) = 2.0045 s, echo time (TE) = 31 ms, flip angle = 
70°, voxel size = 2.24 × 2.24 × 4.1 mm (slice thickness = 3.5 mm with 18% slice gap), 
matrix size = 100 × 100 and field of view = 224 mm × 224 mm. Thirty axial slices 
were prescribed to cover the entire cortex and were scanned in interleaved order. A 
custom-modified bipolar water excitation radiofrequency pulse was used to avoid 
signal from fat. Anatomical data were collected using a T1-weighted multi-echo 
MP-RAGE sequence on the same 3T scanner.
Participants. This study was approved by the Committee for Protection of Human 
Subjects at the University of California, Berkeley. All participants gave informed 
consent. Functional data were collected on 11 participants (three females and 
eight males) between the ages of 23 and 32. All participants were healthy and had 
normal or corrected-to-normal vision.
There was no random assignment into groups. All individuals participated 
in each experiment, and there were no experimental manipulations. No blinding 
was performed as there were no experimental groups in this study. No data were 
excluded from analysis.
No sample size calculation was performed. Instead, we show the effect within 
each individual participant. In addition, these data were initially collected for other 
projects. Each of those projects reported on fewer participants in its published 
paper (five and seven participants) but had sufficient power to show the desired 
effect. Because of this, we determined that 11 participants would be sufficient to 
show ours.
Separation of exploratory and confirmatory analyses. The data analysis 
procedures were performed completely independently for every one of the 11 
participants in the experiment. The only components that were shared across the 
participants were the stimuli they were presented and the features extracted from 
those stimuli. Finding these modality shifts along the visual cortex boundary in 
one participant, therefore, has no bearing on whether this effect will be seen in 
another participant.
Many of the pilot analyses were heavily exploratory before the final analysis 
pipeline was determined. To prevent over-fitting, exploratory analyses were run 
only on participants 1–5. No analyses were done on participants 6–11 until the 
workflow was set. Results shown here are the only iteration of analyses run on 
those six participants. All changes to the analysis pipeline that occurred during the 
review process also followed this guideline. Alterations to the analysis were run 
only on participants 1–5 while editing the manuscript, and results for participants 
6–11 were viewed only while preparing the revised figures.
Natural movie stimuli. Model estimation data were collected in 12 separate 
10-min scans. Movie stimuli consisted of color natural movies drawn from the 
Apple QuickTime HD gallery (http://trailers.apple.com/) and YouTube (http://
www.youtube.com/). Movies were then clipped to 10–20 s in length, and the 
stimulus sequence was created by randomly drawing movies from the entire set. 
Validation data were collected in nine separate 10-min scans, each consisting of ten 
1-min validation blocks, taken from the same stimulus set. Each 1-min validation 
block was presented ten times within the 90 min of validation data. The movies 
were shown on a projection screen at 24 × 24 degrees of visual angle.
Natural story stimuli. The model estimation dataset consisted of ten 10- to 15-min 
stories taken from The Moth Radio Hour. In each story, a single speaker tells an 
autobiographical story in front of a live audience. The ten selected stories cover 
a wide range of topics and are highly engaging. Each story was played during a 
separate fMRI scan. The length of each scan was tailored to the story and included 
10 s of silence both before and after the story. The model validation dataset 
consisted of one 10-min story, also taken from The Moth Radio Hour. Stories were 
played over Sensimetrics S14 in-ear piezoelectric headphones.
Fitting encoding models. Semantic features used to fit the encoding models were 
derived from a 985-dimensional word co-occurrence space. To create this, we first 
constructed a 10,470-word lexicon from the union of the set of all words appearing 
in the stories and the 10,000 most common words in the large text corpus. We 
then selected 985 basis words from Wikipedia’s List of 1,000 Basic Words (contrary 
to the title, this list contained only 985 unique words at the time it was accessed). 
This basis set was selected because it consists of common words that span a 
very broad range of topics. The text corpus used to construct this feature space 
includes the transcripts of 13 Moth stories (including the ten used as stimuli in 
this experiment), 604 popular books, 2,405,569 Wikipedia pages and 36,333,459 
user comments scraped from reddit.com. In total, the 10,470 words in our lexicon 
appeared 1,548,774,960 times in this corpus.
Next, we constructed a word co-occurrence matrix, M, with 985 rows and 
10,470 columns. Iterating through the text corpus, we added 1 to Mi,j each time 
word j appeared within 15 words of basis word i. A window size of 15 was selected 
to be large enough to suppress syntactic effects (for example, word order) but no 
larger. Once the word co-occurrence matrix was complete, we log-transformed the 
counts, replacing Mi,j with log(1 + Mi,j). Next, each row of M was z-scored to correct 
for differences in basis word frequency, and then each column of M was z-scored to 
correct for word frequency. Each column of M is now a 985-dimensional semantic 
vector representing one word in the lexicon.
The matrix used for voxel-wise model estimation was then constructed 
from the stories: for each word–time pair (w,t) in each story, we selected the 
corresponding column of M, creating a new list of semantic vector–time pairs, 
(Mw,t). These vectors were then resampled at times corresponding to the fMRI 
acquisitions using a three-lobe Lanczos filter with the cutoff frequency set to the 
Nyquist frequency of the fMRI acquisition (0.249 Hz).
For the movie stimuli, an observer manually labeled all objects and actions in 
each 1-s clip of the movie using WordNet synsets25. For each synset (for example, 
bank.n.02), we then extracted the corresponding set of lemma names (for example, 
‘depository_financial_institution’, ‘bank’, ‘banking_concern’ and ‘banking_
company’) and, for multi-word lemma names (for example, ‘banking_company’), 
split them with underscores. The resulting list of tokens for each synset were 
then concatenated with tokens from all other synsets appearing in the same 1-s 
movie clip. In addition to these annotations, we included textual descriptions of 
each 1-s scene provided by users on Amazon Mechanical Turk. Finally, to form a 
985-dimensional semantic vector for each 1-s clip, we fetched the vector for each 
word in the full annotation list (including token lists from all the WordNet synsets 
and the Mechanical Turk annotations) that was in the set of the 10,470-word 
lexicon and then averaged all of these vectors together. The vectors for the two 1-s 
clips comprising each 2-s fMRI acquisition were then averaged together.
In addition, we extracted a set of low-level features from each set of stimuli to 
control for that type of information in each model. For the movies, we extracted a 
set of 2,139 motion energy features24, in which each filter consisted of a quadrature 
pair of space-time Gabor filters. For the stories, the 41 low-level features were word 
rate (one feature), phoneme rate (one feature) and phonemes (39 features).
Before regression, each stimulus feature within each story or movie run was 
z-scored through time. This was done to match the features to the fMRI responses, 
which were also z-scored through time for each functional run.
To model our data, we used a modified version of ridge regression called 
banded ridge40. In this framework, each voxel in the brain is assigned two different 
ridge parameters: one for the semantic features and one for the low-level features. 
These pairs of ridge parameters can vary across each voxel, and this allows the 
model to effectively weight the two sets of features independently across the brain.
A separate linear temporal filter with four delays (1, 2, 3 and 4 time points) 
was fit for each feature. This was accomplished by concatenating feature vectors 
that had been delayed by 1, 2, 3 and 4 time points (2 s, 4 s, 6 s and 8 s). Thus, in the 
concatenated feature space, one channel represents the word rate 2 s earlier, another 
4 s earlier and so on. Taking the dot product of this concatenated feature space with 
a set of linear weights is functionally equivalent to convolving the original stimulus 
vectors with linear temporal kernels that have non-zero entries for 1, 2, 3 and 4 
time point delays.
As in previous publications18–20, data were split into a training set and a test set, 
and ridge parameters were selected through cross-validation within the training 
set. Model performance for both the semantic and low-level submodels was 
evaluated by multiplying the fit model weights by the features for the test story/
movie and then taking the correlation coefficient of that predicted time course per 
voxel with the actual brain data.
All model fitting was performed using custom software, available as a Python 
package called tikreg (https://github.com/gallantlab/tikreg)40.
Multi-modal voxels. After separate encoding models were fit for the visual and 
language experiments in the semantic feature space, semantic tuning across those 
models was directly correlated within each participant. We first found the average 
tuning to each feature across delays as a 985-dimensional weight vector per voxel 
and model. Then, the voxel weights across the two models were directly correlated. 
The correlation values, which indicate an overlap in semantic tuning across the two 
modalities, are shown in Fig. 1.
Calculation of MRI signal dropout. MRI signal dropout tends to occur in areas 
of the brain that are near tissues that are magnetically inhomogeneous, such as 
air sinuses. This phenomenon is generally quantified by the SFNR31. This was 
calculated for each voxel in each functional run individually by dividing the mean 
of the signal by its standard deviation. That value was averaged across all runs and 
then thresholded at a value of 15. Voxels below this value are tagged as dropout 
regions and are indicated with hash marks in Figs. 4 and 5.
Modality shifts of chosen categories. Our initial analysis of modality shifts 
examined only a few semantic categories that are known to be represented in 
anterior portions of the visual system: places, body parts and faces. To look at 
the brain representations of each of these categories across the cortex, we created 
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 11

Articles
NaTuRE NEuRoScIEncE
a generic representation of the categories within the 985-dimensional semantic 
feature space. First, we constructed a list of words related to each category:
Places: house, building, hotel, office, parking, lot, park, street, road, sidewalk, 
highway, path, field and mountain
Faces: face, eyes, nose, mouth, hair, cheek, cheeks, smile, frown and teeth
Body parts: body, arm, arms, leg, legs, hand, hands, foot, feet, torso, head,  
back and thigh
Each word in each list was projected into the 985-dimensional 
word-embedding feature space. This location is based on each word’s 
co-occurrence with each of the 985 basis words. Then, within each category, 
all vectors were averaged to get a general 985-dimensional category vector. 
Finally, the vision and language model weights for each voxel were projected 
onto each category vector: high visual projections onto the vector were voxels 
that represented that category visually; voxels with high linguistic projections 
were voxels that represented that category linguistically; and voxels where 
both projections were high represented that category in both modalities. These 
projection values are shown in the two-dimensional color maps shown in Fig. 2 
and Extended Data Figs. 2–4 for each semantic category separately (that is, places, 
faces and body parts).
Surface-based analyses surrounding visual cortex. To find modality shifts, 
we first selected the appropriate regions of the cortical surface using a software 
package developed in our lab called pycortex41. In pycortex, each participant’s 
cortical surface is formed from a triangular mesh that is made up of approximately 
150,000 vertices per hemisphere. To save computation time, vertices were 
sub-selected from each surface such that any location on the surface was no more 
than 2.5 mm away from a chosen vertex. (A pilot analysis run on one participant 
indicated that this sub-selection did not affect results—data not shown here.) 
Because we were interested only in the pattern that exists around the border of 
visual cortex, we further limited the analysis to a window within 50 mm of the 
defined border of occipital cortex, as shown in Extended Data Fig. 5. This process 
resulted in about 15,000–20,000 cortical locations per participant.
Next, we searched for modality shifts at all possible angles through each vertex. 
First, a circular patch on the cortical surface within 22.5 mm of the starting vertex 
was selected. All vertices along the outer edge of the patch were then selected as 
endpoints of lines. Then, geodesic lines were drawn starting from each endpoint. 
Each line passed through the center vertex and continued in the same direction 
until leaving the patch. This was done using the geodesic_distance and geodesic_
path functions in pycortex41. For each vertex, this process resulted in about 200–
300 lines passing through the center at all possible angles (Fig. 3a).
Finally, a window around each line was formed, and we looked for modality 
shifts within each window. All vertices within 10 mm of the line were selected.  
We formed a coordinate system within the window based on the vertices along the 
geodesic line. Each vertex in the window was given a coordinate along the geodesic 
line (Fig. 3b), which was a weighted sum of the line vertex coordinates and the 
distances to each line vertex:
W =
e
( −Dp
s
)
∑
i e
( −Dp,i
s
)
C = DvW
Dp = pairwise distances between window vertices and line vertices
Dv = cumulative distance between line vertices
s = smoothing factor for exponential
W = weighting value for each vertex
C = coordinate of each vertex along window
Only the vertices with coordinates within 12.5 mm of the original center vertex 
were retained. This resulted in a total window size of 20 mm across by 25 mm long, 
centered on the initial vertex.
Additional analyses were run where the size of the window was 10 mm × 25 
mm and 10 mm × 10 mm. The results of these analyses are shown in Extended 
Data Figs. 6 and 7. The results with 10 mm × 25 mm windows show no discernible 
difference to those shown in the main test with a 20 mm × 25 mm window. The 
results using 10 mm × 10 mm windows resulted in noisier maps, suggesting that a 
long axis across the boundary between networks is necessary to reliably detect the 
shifts. Nonetheless, a similar pattern of significant shifts is still clearly visible.
Definition of modality shift summary statistic. To quantify how representations 
of a semantic category changed within a window, we first calculated the average 
semantic tuning within each region by calculating the mean vision model weights 
and language model weights for all vertices, within each modality separately. These 
average tuning vectors were normalized such that their L2 norms were equal to 1. 
Next, for each vertex, the vision and language model weights were projected onto 
that average visual model weight vector. (This entire process will also be repeated 
for the average linguistic model weigh vector.) Then, to measure representational 
shifts along the region, a linear regression model was fit for the weight projections 
as a function of coordinate along the line (Fig. 3c). This was done separately for the 
movie and story weight projections:
X =
[
1T, CT]
YV = WT
VwA
YL = WT
LwA
[Vi, Vm] =
(
XTX
)−1
XTYV
[Li, Lm] =
(
XTX
)−1
XTYL
C = coordinate of each vertex along window
wA = average tuning vector within window
WV = visual tuning vector for each vertex in window
WL = linguistic tuning vector for each vertex in window
Vi = intercept term for visual fit line
Vm = slope term for visual fit line
Li = intercept term for linguistic fit line
Lm = slope term for linguistic fit line
Finally, we created a single metric that could describe locations where the 
visual representations were getting weaker and the linguistic representations were 
getting stronger along the length of the window. Thus, all windows were oriented 
such that the first half of each region was visually responsive, and the second half 
was linguistically responsive. If the results are consistent with the hypothesis, 
then the ratio of the slopes found above should be around −1. To find locations 
with large overall changes in selectivity, we opted to scale this ratio by the average 
magnitude of the slopes. Because we only wanted to identify locations at which 
there was a shift from visual to linguistic representation, we also included an 
indicator variable, which was 1 when the fit lines cross within the analysis window 
and was 0 otherwise. Finally, because we only wanted to identify locations where 
the semantic tuning across modalities was similar and not diverging from each 
other, we included an indicator variable, which was 1 when the average projection 
value across all vertices was a positive number and was 0 otherwise. Thus, those are 
the components included in our summary statistic for modality shift magnitude (as 
well as a negation so that the strongest shifts are positive values):
R = sign (VmLm) min

Vm
Lm
 ,

Lm
Vm


M = |Vm| + |Lm|
2
P =
Li −Vi
Vm −Lm
C =
( 1 min (X) < P < max (X)
0
otherwise
)
Y =

1
( ∑Yv
n
)
∗
( ∑Yl
n
)
> 0
0
otherwise


S = −R ∗M ∗C ∗Y
Vi = intercept term for visual fit line
Vm = slope term for visual fit line
Li = intercept term for linguistic fit line
Lm = slope term for linguistic fit line
R = ratio of slope terms, bounded between (−1, 1)
M = average magnitude of slope terms
P = x-coordinate of fit line intersection
X = coordinates of all vertices along window
C = indicator variable of fit lines crossing in window
Yv = weight projections for the visual vertices
Yl = weight projections for the linguistic vertices
n = number of vertices in window
Y = indicator variable of positive average projections
S = magnitude of modality shift
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 12

Articles
NaTuRE NEuRoScIEncE
This entire process was then repeated for the average linguistic model weigh 
vector, and the stronger of the two metrics was retained.
Significance testing. For each vertex on the cortical surface, the shift magnitude 
was evaluated. For each vertex, the strongest metric is plotted on the cortical flat 
maps in Fig. 4. Statistical significance of the putative shifts was evaluated through a 
permutation test. This test illustrated that the two maps were precisely aligned and 
did not simply identify locations where large visual weights were near locations 
with large linguistic weights.
In this test, the shuffled component depended upon which average semantic 
weight vector was used in the original calculation of the metric (that is, visual or 
linguistic). If the average visual semantic weight vector was used, then linguistic 
information from the windows was permuted. If the average linguistic semantic 
weight vector was used, then visual information from the window was permuted. 
The weights for the vertices from the chosen modality, and their respective positions 
along the window, were swapped with all other possible windows across cortex. 
Because the number of vertices within a window is variable due to differences 
in cortical folding, the vertices for each permuted window were selected with 
replacement to match the original number of vertices for that window. Then, the 
shift magnitude was calculated for all of these possible permutations. This resulted in 
a distribution of shift metrics for each window. From this distribution, we obtained 
a one-tailed P value for the original shift metric. The P values for all windows were 
then FDR corrected and thresholded at 0.05. Only significant locations after FDR 
correction are shown in Figs. 4–6 and Extended Data Figs. 6 and 7.
Reporting Summary. Further information on research design is available in the 
Nature Research Reporting Summary linked to this article.
Data availability
Data are available on Box (https://berkeley.box.com/s/
l95gie5xtv56zocsgugmb7fs12nujpog) and at https://gallantlab.org/. All data other 
than anatomical brain images (as there is concern that anatomical images could 
violate participant privacy) have been shared. However, we have provided matrices 
that map from volumetric data to cortical flat maps for visualization purposes.
Code availability
Custom code used for cortical surface-based analyses is available at https://github.
com/gallantlab/vl_interface.
References
	40.	Nunez-Elizalde, A. O., Huth, A. G. & Gallant, J. L. Voxelwise encoding 
models with non-spherical multivariate normal priors. Neuroimage 197, 
482–492 (2019).
	41.	Gao, J. S., Huth, A. G., Lescroart, M. D. & Gallant, J. L. Pycortex:  
an interactive surface visualizer for fMRI. Front. Neuroinform. 9,  
23 (2015).
Acknowledgements
We thank J. Nguyen for assistance transcribing and aligning story stimuli and  
B. Griffin and M.-L. Kieseler for segmenting and flattening cortical surfaces.  
Funding: This work was supported by grants from the National Science Foundation 
(NSF) (IIS1208203), the National Eye Institute (EY019684 and EY022454) and the 
Center for Science of Information, an NSF Science and Technology Center, under 
grant agreement CCF-0939370. S.F.P. was also supported by the William Orr Dingwall 
Neurolinguistics Fellowship. A.G.H. was also supported by the William Orr Dingwall 
Neurolinguistics Fellowship and the Burroughs-Wellcome Fund Career Award at the 
Scientific Interface.
Author contributions
S.F.P., A.G.H. and J.L.G. conceptualized the experiment. A.G.H., N.Y.B. and F.D. collected 
the data. S.F.P., A.G.H., N.Y.B., J.S.G. and A.O.N.-E. contributed to analysis. S.F.P., A.G.H. 
and J.L.G. wrote the paper.
Competing interests
The authors declare no competing financial interests.
Additional information
Extended data is available for this paper at https://doi.org/10.1038/s41593-021-00921-6.
Supplementary information The online version contains supplementary material 
available at https://doi.org/10.1038/s41593-021-00921-6.
Correspondence and requests for materials should be addressed to Jack L. Gallant.
Peer review information Nature Neuroscience thanks Christopher Baldassano and Johan 
Carlin for their contribution to the peer review of this work.Reprints and permissions 
information is available at www.nature.com/reprints.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 13

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 1 | See next page for caption.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 14

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 1 | Evaluation of the visual and linguistic semantic models. Model weights are estimated on the training dataset, then are used 
to predict brain activity to a held-out dataset. Prediction performance is the correlation of actual and predicted brain activity for each voxel. These 
performance values are presented simultaneously using a 2-dimensional colormap on the flattened cortex around the occipital pole for each subject. Red 
voxels are locations where the visual semantic model is performing well, blue voxels are where the linguistic semantic model is performing well, and white 
voxels are where both models are performing equally well. These maps show where the visual and linguistic networks of the brain abut each other.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 15

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 2 | See next page for caption.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 16

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 2 | Visual and linguistic representations of place concepts. Identical analysis to Fig. 2a, but for the other 10 subjects. The color of each 
voxel indicates the representation of place-related information according to the legend at the right. The model weights for vision and language are shown 
in red and blue, respectively. White borders indicate ROIs found in separate localizer experiments. Three relevant place ROIs are labeled: PPA, OPA, and 
RSC. Centered on each ROI there is a modality shift gradient that runs from visual semantic categories (red) posterior to linguistic semantic categories 
(blue) anterior.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 17

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 3 | See next page for caption.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 18

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 3 | Visual and linguistic representations of body part concepts. Identical analysis to Fig. 2b, but for the other 10 subjects. The color 
of each voxel indicates the representation of body-related information according to the legend at the right. The model weights for vision and language are 
shown in red and blue, respectively. White borders indicate ROIs found in separate localizer experiments. The relevant body ROI is labeled: EBA. Centered 
on each ROI there is a modality shift gradient that runs from visual semantic categories (red) posterior to linguistic semantic categories (blue) anterior.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 19

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 4 | See next page for caption.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 20

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 4 | Visual and linguistic representations of face concepts. Identical analysis to Fig. 2c, but for the other 10 subjects. The color of each 
voxel indicates the representation of face-related information according to the legend at the right. The model weights for vision and language are shown 
in red and blue, respectively. White borders indicate ROIs found in separate localizer experiments. The relevant face ROI is labeled: FFA. Centered on each 
ROI there is a modality shift gradient that runs from visual semantic categories (red) posterior to linguistic semantic categories (blue) anterior.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 21

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 5 | See next page for caption.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 22

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 5 | Analysis region around the boundary of the occipital lobe. The thin yellow line indicates the estimated border of the occipital  
lobe of the brain in each individual subject. This was manually drawn to follow the parieto-occipital sulcus and connect to the preoccipital notch on 
both ends. The area of the brain which was analyzed in this study was limited to vertices within 50 mm of this border, which is shown in black on each 
individual’s brain.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 23

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 6 | See next page for caption.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 24

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 6 | Locations of category-specific modality shifts across cortex for alternate parameter set 1. Identical analysis to Fig. 4, but with an 
ROI size of 10x25mm. Shown here is the flattened cortex around the occipital pole for one typical subject, along with inflated hemispheres. The modality 
shift metric calculated at each location near the boundary of the occipital lobe is plotted as an arrow. The arrow color represents the magnitude of the 
shift. The arrow is directed to show the shift from vision to language. Only locations where the modality shift is statistically significant are shown. Areas of 
fMRI signal dropout are indicated with hash marks. There are strong modality shifts in a clear ring around visual cortex in the same locations seen in Fig. 4.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 25

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 7 | See next page for caption.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 26

Articles
NaTuRE NEuRoScIEncE
Extended Data Fig. 7 | Locations of category-specific modality shifts across cortex for alternate parameter set 2. Identical analysis to Fig. 4, but with an 
ROI size of 10x10mm. Shown here is the flattened cortex around the occipital pole for one typical subject, along with inflated hemispheres. The modality 
shift metric calculated at each location near the boundary of the occipital lobe is plotted as an arrow. The arrow color represents the magnitude of the 
shift. The arrow is directed to show the shift from vision to language. Only locations where the modality shift is statistically significant are shown. Areas 
of fMRI signal dropout are indicated with hash marks. There are strong modality shifts in a ring around visual cortex in the same locations seen in Fig. 4, 
though the pattern is more noisy due to the shortened analysis windows.
Nature Neuroscience | www.nature.com/natureneuroscience


## Page 27

1
nature research  |  reporting summary
October 2018
Corresponding author(s):
Jack L. Gallant
Last updated by author(s): Jul 26, 2021
Reporting Summary
Nature Research wishes to improve the reproducibility of the work that we publish. This form provides structure for consistency and transparency 
in reporting. For further information on Nature Research policies, see Authors & Referees and the Editorial Policy Checklist.
Statistics
For all statistical analyses, confirm that the following items are present in the figure legend, table legend, main text, or Methods section.
n/a Confirmed
The exact sample size (n) for each experimental group/condition, given as a discrete number and unit of measurement
A statement on whether measurements were taken from distinct samples or whether the same sample was measured repeatedly
The statistical test(s) used AND whether they are one- or two-sided 
Only common tests should be described solely by name; describe more complex techniques in the Methods section.
A description of all covariates tested
A description of any assumptions or corrections, such as tests of normality and adjustment for multiple comparisons
A full description of the statistical parameters including central tendency (e.g. means) or other basic estimates (e.g. regression coefficient) 
AND variation (e.g. standard deviation) or associated estimates of uncertainty (e.g. confidence intervals)
For null hypothesis testing, the test statistic (e.g. F, t, r) with confidence intervals, effect sizes, degrees of freedom and P value noted 
Give P values as exact values whenever suitable.
For Bayesian analysis, information on the choice of priors and Markov chain Monte Carlo settings
For hierarchical and complex designs, identification of the appropriate level for tests and full reporting of outcomes
Estimates of effect sizes (e.g. Cohen's d, Pearson's r), indicating how they were calculated
Our web collection on statistics for biologists contains articles on many of the points above.
Software and code
Policy information about availability of computer code
Data collection
MRI data was collected using syngoMR software distributed by Siemens (versions 15 and 17A). Stimuli were presented with python 2.7.
Data analysis
Python 2.7 was used to preprocess the MRI data, making use of FSL (5.0) and freesurfer (5.3). Python 2.7 was used to analyze the data, 
which primarily relied on pycortex (version 0.0.1; https://github.com/gallantlab/pycortex/), cottoncandy (version 0.2.0; https://
github.com/gallantlab/cottoncandy), and tikreg (version 0.0.1; https://github.com/gallantlab/tikreg). 
 
Custom code used for cortical surface based analyses is available at: https://github.com/gallantlab/vl_interface
For manuscripts utilizing custom algorithms or software that are central to the research but not yet described in published literature, software must be made available to editors/reviewers. 
We strongly encourage code deposition in a community repository (e.g. GitHub). See the Nature Research guidelines for submitting code & software for further information.
Data
Policy information about availability of data
All manuscripts must include a data availability statement. This statement should provide the following information, where applicable: 
- Accession codes, unique identifiers, or web links for publicly available datasets 
- A list of figures that have associated raw data 
- A description of any restrictions on data availability
Data has been made available on Box (https://berkeley.box.com/s/l95gie5xtv56zocsgugmb7fs12nujpog) and https://gallantlab.org/. All data other than anatomical 
brain images has been be shared (as there is concern that anatomical images could violate subject privacy). However, we have also provided matrices that map 
from volumetric data to cortical flatmaps for visualization purposes.


## Page 28

2
nature research  |  reporting summary
October 2018
Field-specific reporting
Please select the one below that is the best fit for your research. If you are not sure, read the appropriate sections before making your selection.
Life sciences
Behavioural & social sciences
 Ecological, evolutionary & environmental sciences
For a reference copy of the document with all sections, see nature.com/documents/nr-reporting-summary-flat.pdf
Life sciences study design
All studies must disclose on these points even when the disclosure is negative.
Sample size
No sample-size calculation was performed. Instead, we show the effect within each individual subject. 
 
In addition, these data were initially collected for other projects. Each of those projects had fewer subjects in its published paper (5 and 7 
subjects) but had sufficient power to show the desired effect. Because of this, we determined that 11 subjects would be sufficient to show 
ours.
Data exclusions
No data were excluded from analysis.
Replication
The data analysis procedures were performed completely independently for every one of the 11 subjects in the experiment. This is effectively 
11 separate and independent replications of the result.  
 
However, many of the pilot analyses were heavily exploratory before the final analysis pipeline was determined. To prevent over-fitting, 
exploratory analyses were run only on subjects 1-5. No analyses were done on subjects 6-11 until the workflow was set. Results shown here 
are the only iteration of analyses run on those 6 subjects. All changes to the analysis pipeline that occurred during the review process also 
followed this guideline. Alterations to the analysis were run only on subjects 1-5 while editing the manuscript, and results for subjects 6-11 
were viewed only while preparing the revised figures. The results seen in our two groups of subjects are comparable.
Randomization
There was no assignment into groups. All subjects participated in each experiment and there were no experimental manipulations.
Blinding
No blinding was performed as there were no experimental groups in this study. 
Reporting for specific materials, systems and methods
We require information from authors about some types of materials, experimental systems and methods used in many studies. Here, indicate whether each material, 
system or method listed is relevant to your study. If you are not sure if a list item applies to your research, read the appropriate section before selecting a response. 
Materials & experimental systems
n/a Involved in the study
Antibodies
Eukaryotic cell lines
Palaeontology
Animals and other organisms
Human research participants
Clinical data
Methods
n/a Involved in the study
ChIP-seq
Flow cytometry
MRI-based neuroimaging
Human research participants
Policy information about studies involving human research participants
Population characteristics
The study involved 11 subjects (three female, eight male) between the ages of 23-32.
Recruitment
Human subjects were recruited from the lab (4 subjects are authors on the paper). However, because there are no experimental 
manipulations in this study and subjects are only performing naturalistic tasks, we do not expect this to have an effect on our 
results in any way.
Ethics oversight
The study was approved by the Committee for Protection of Human Subjects (CPHS) at UC Berkeley. All subjects gave informed 
consent.
Note that full information on the approval of the study protocol must also be provided in the manuscript.


## Page 29

3
nature research  |  reporting summary
October 2018
Magnetic resonance imaging
Experimental design
Design type
This question is not relevant to our procedure as our study involved only naturalistic tasks where subjects either 
watched movies or listened to narrative stories. 
Design specifications
There are not specified "trials" in the experiments in this study. For the vision experiment, subjects watched movies for 
120 minutes (model training data), and then another 9 minutes of movies repeated 10 times (model validation data). 
For the language experiment, subjects listened to stories for 120 minutes (model training data), and then another 11 
minutes of stories repeated 2-4 times (model validation data). 
Behavioral performance measures
There was no explicit task in either experiment. Subjects were only passively watching movies or listening to stories.
Acquisition
Imaging type(s)
fMRI
Field strength
3T
Sequence & imaging parameters
Functional scans were collected using gradient echo EPI with repetition time (TR) = 2.0045 s, echo time (TE) = 31ms, flip 
angle = 70°, voxel size = 2.24 × 2.24 × 4.1mm (slice thickness = 3.5mm with 18% slice gap), matrix size = 100 × 100, and 
field of view = 224 × 224 mm. Thirty axial slices were prescribed to cover the entire cortex and were scanned in 
interleaved order. A custom-modified bipolar water excitation radiofrequency (RF) pulse was used to avoid signal from 
fat. Anatomical data were collected using a T1-weighted multi-echo MP-RAGE sequence on the same 3T scanner.
Area of acquisition
Whole brain
Diffusion MRI
Used
Not used
Preprocessing
Preprocessing software
Functional data were preprocessed using the fMRI Software Library (FSL) and custom python code including pycortex. 
Each scan of functional data was temporally interpolated to align the data for each slice in time. Temporally 
interpolated data were motion corrected and averaged together into a single volume. For each scan, this average 
volume was aligned to the temporal average of the first functional run using the FMRIB Linear Image Registration Tool 
(FLIRT) in FSL. Transformations from motion correction and interrun alignment were concatenated, and the raw 
functional data were transformed and spatially resampled using trilinear interpolation. Transformed data were then 
temporally detrended with a Savitsky-Golay filter and z-scored before model fitting.
Normalization
The data were not normalized as we were looking for effects within individual subjects. These effects may not be found 
in group average spaces where the fine-scale organization of the semantic maps is smoothed across individuals.
Normalization template
The data were not normalized.
Noise and artifact removal
All data was motion corrected as specified above.  
 
Unfortunately, heart rate and respiration data was not available for all subjects. In order to keep analyses consistent 
across individuals, we did not regress out that information for any subjects. However, in data not shown here, we 
looked at these effects in subjects in which we can regress out these physiological variables, and it does not impact our 
findings.
Volume censoring
There were no volumes with sufficient motion to warrant censoring. Many subjects were wearing customized 
headcases to prevent excessive movement.
Statistical modeling & inference
Model type and settings
To model our data, we used a modified version of ridge regression called banded ridge. In this framework, each voxel in 
the brain is assigned two different ridge parameters: one for the semantic features and one for the low-level features. 
For each experiment, data were split into a training and test set, and ridge parameters were selected through cross-
validation within the training set. 
 
Model performance for both the semantic and low-level submodels was evaluated by multiplying the fit model weights 
by the features for the test story/movie, then taking the correlation coefficient of that predicted time course per voxel 
with the actual brain data.
Effect(s) tested
There were no tasks or stimulus conditions, thus, no t-tests or ANOVAs were performed.
Specify type of analysis:
Whole brain
ROI-based
Both


## Page 30

4
nature research  |  reporting summary
October 2018
Anatomical location(s)
We manually defined the entire boundary of the occipital lobe in each subject individually. This border 
followed the parieto-occipital sulcus along the dorsal surface, then connected on both ends to the 
preoccipital notch on the ventral surface. When possible, the border followed sulcal fundi, but otherwise 
took shortest paths between these landmarks. Since this definition was approximate and furthermore 
not based on functional activations (e.g. this border does not include areas with visual representations in 
temporal and parietal cortex), later analyses were run on a larger area of the cortex. Thus, the analysis 
which searched for modality shifts was expanded to all all vertices within 50mm of the drawn border.
Statistic type for inference
(See Eklund et al. 2016)
The magnitude of modality shifts were estimated for each "window." For statistical purposes, this can be thought of as 
similar to a cluster. The significance of the modality shift magnitude of each window was evaluated through a 
permutation test, from which we obtained a one-tailed p-value.
Correction
FDR correction was run on the p-values obtained from the permutation test described above.
Models & analysis
n/a Involved in the study
Functional and/or effective connectivity
Graph analysis
Multivariate modeling or predictive analysis
Multivariate modeling and predictive analysis
For each experiment, data were split into a training and test set, and ridge parameters were selected 
through cross-validation within the training set. Model performance for both the semantic and low-level 
submodels was evaluated by multiplying the fit model weights by the features for the test story/movie, 
then taking the correlation coefficient of that predicted time course per voxel with the actual brain data.


