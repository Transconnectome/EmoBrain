# (2025) Heritability of movie-evoked brain activity and connectivity

**Source:** (2025) Heritability of movie-evoked brain activity and connectivity.pdf

---

## Page 1

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
1 of 37
Neuroscience
Heritability of movie-evoked
brain activity and connectivity
David C Gruskin
, Daniel J Vieira, Jessica K Lee, Gaurav H Patel
Medical Scientist Training Program, Columbia University Irving Medical Center, New York, United States • Division
of Experimental Therapeutics, New York State Psychiatric Institute, New York, United States • Department of
Psychiatry, Columbia University Irving Medical Center, New York, United States
https://en.wikipedia.org/wiki/Open_access
Copyright information
eLife Assessment
This paper addresses a valuable research question on the heritability of the brain's
response to movie watching, given various parameters such as regional spatial
hyperalignment and BOLD frequency bands. The topic of this paper would be of
interest to fMRI methodological experts, and potentially to a broader cognitive
neuroscience audience, and those with an interest in understanding the heritable
sources of individual differences in brain function. However, the current findings
provide incomplete support for the conclusions, since several key methodological
concerns need to be addressed to ensure the validity of the analyses and results.
https://doi.org/10.7554/eLife.106081.1.sa3
Abstract
The neural bases of sensory processing are conserved across people, but no two individuals
experience the same stimulus in exactly the same way. Recent work has established that the
idiosyncratic nature of subjective experience is underpinned by individual variability in
brain responses to sensory information. However, the fundamental origins of this individual
variability have yet to be systematically investigated. Here, we establish a genetic basis for
individual differences in sensory processing by quantifying (1) the heritability of high-
dimensional brain responses to movies and (2) the extent to which this heritability is
grounded in lower-level aspects of brain function. Specifically, we leverage 7T fMRI data
collected from a twin sample to first show that movie-evoked brain activity and connectivity
patterns are heritable across the cortex. Next, we use hyperalignment to decompose this
heritability into genetic similarity in where vs. how sensory information is processed. Finally,
we show that the heritability of brain activity patterns can be partially explained by the
heritability of the neural timescale, a one-dimensional measure of local circuit functioning.
These results demonstrate that brain responses to complex stimuli are heritable, and that this
heritability is due, in part, to genetic control over stable aspects of brain function.
Reviewed Preprint
v1 • May 7, 2025
Not revised


## Page 2

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
2 of 37
Introduction
Although the neural machinery that allows us to process sensory information is broadly conserved
across people, no two individuals experience the same sensory stimulus in exactly the same way.
What underlying factors give rise to this person-to-person variability in subjective experience?
Recent work has established that the idiosyncratic nature of subjective experience is reflected in
idiosyncratic brain responses to sensory information, and that how an individual processes a
stimulus is shaped by their psychosocial background and previous experiences. For example,
individuals who share more similar personality traits (Finn et al., 2018     ) and political
orientations (van Baar et al., 2021     ) exhibit more similar interpretations of, and functional
magnetic resonance imaging (fMRI) responses to, relevant audiovisual stimuli, as do individuals
who are primed with more similar contextual information before listening to an ambiguous
narrative (Yeshurun et al., 2017     ). Here, we extend this work by investigating a more
fundamental source of variability in sensory-evoked brain responses and the experiences they
represent: our genes.
Whether individual variability in a given trait is due to environmental or genetic factors is a
central question in biology, and the extent to which this variability is underpinned by variation in
genetics (or “under genetic control”) is measured by its heritability (or h2). Recent studies have
quantified the heritability of various aspects of sensory brain function, revealing a genetic basis
for patterns of brain activity elicited by auditory tones and visual gratings in sensory cortices
(Alvarez et al., 2021     ; Pelt et al., 2012     ; Renvall et al., 2012     ). However, the unimodal and low-
dimensional nature of these stimuli may not capture the full complexity of real-life sensory
experiences and the brain responses they evoke. Consequently, the extent to which genetic factors
influence brain responses to more naturalistic stimuli remains unclear, especially for high-level
(e.g., social and narrative) information encoded across longer timescales in association cortex.
In addition to activity patterns within individual brain areas, information can also be encoded in
the functional connectivity (FC) between multiple areas or networks (Chen et al., 2014     ; Kohn et
al., 2016     ). Research into the heritability of FC and related measures has largely focused on data
acquired while subjects are at rest, during which an individual’s unique FC profile (i.e., pattern of
pairwise FC strengths), describes their brain’s intrinsic functional architecture (Anderson et al.,
2021     ; Burger et al., 2022     ; Busch et al., 2023     ; Dworetsky et al., 2024     ; Glahn et al., 2010     ;
Sinclair et al., 2015     ; van den Heuvel & Hulshoff Pol, 2010     ). These studies have demonstrated
that a range of resting state FC (rest FC)-derived measures are moderately heritable, and similar
findings have resulted from work characterizing the heritability of FC during task performance,
which additionally reflects the processing of information relevant to the task at hand (Cole et al.,
2021     ; Elliott et al., 2019     ; Korgaonkar et al., 2014     ). Although this work has shed significant
light on the genetic basis of FC during rest and cognition, the heritability of sensory-evoked FC
patterns, which are known to encode stimulus features (Chen et al., 2014     ) and track individual
differences in behavior (Finn & Bandettini, 2021     ), has yet to be investigated.
Finally, brain activity and connectivity patterns are complex phenomena that arise from a variety
of physiological processes. Although the heritability estimates established by previous work could
reflect emergent aspects of brain function, it might instead be possible to reduce them to genetic
control over lower-level neural, vascular, and metabolic processes. For example, although the
human cortex is topographically organized into areas that are specialized for processing specific
kinds of information (e.g., facial features), the locations of these areas and the tuning patterns
within them vary widely across individuals (Gordon et al., 2017     ; Haxby et al., 2020     ; Petersen
et al., 2024     ). As such, these cortical topographies, or individual-specific maps of where stimulus
features are processed, emerge over the course of development and constrain the activity and
connectivity patterns an individual will exhibit during sensory processing. Independent of where


## Page 3

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
3 of 37
stimuli are processed, stable aspects of brain function also shape high-dimensional activity and
connectivity patterns by influencing how information is processed. For example, recent work from
Shinn et al. (Shinn et al., 2023     ) showed that individual variability in higher-order aspects of
brain function like FC profiles can be traced back to variability in simpler, low-level phenomena
like temporal autocorrelation of the blood oxygen level-dependent (BOLD) signal. More
specifically, a measure of temporal autocorrelation known as the neural timescale (NT) is thought
to reflect the strength of local recurrent excitation (Cavanagh et al., 2020     ) but is also closely tied
to the organization of brain-wide FC profiles (Shinn et al., 2023     ). Given that lower-level
properties like functional topography (Alvarez et al., 2021     ; Anderson et al., 2021     ; Dworetsky et
al., 2024     ) and BOLD temporal autocorrelation (Christova et al., 2022     ) are themselves heritable,
it remains unclear (1) to what extent high-dimensional brain responses to naturalistic stimuli are
heritable and (2) how much of this heritability can be reduced to genetic control over these stable
spatial and temporal aspects of brain function.
In the present work, we address these questions by analyzing 7T fMRI recordings of a twin sample
acquired by the Human Connectome Project (Van Essen et al., 2013     ) to quantify the heritability
of stimulus-evoked brain activity and connectivity across the cortex. Here, we focus on fMRI data
acquired during movie-watching, as the rich and multimodal nature of movies engages multiple
sensory and associative regions as well as the connections between them, making them well-suited
for broadly assessing individual differences in sensory processing. Leveraging a multi-
dimensional estimator of heritability (Anderson et al., 2021     ), we first show that movie-evoked
BOLD time courses are heritable across the cortex. We extend this result by showing that BOLD
time course heritability is greater in slower frequency bands, and especially in more associative
parcels, suggesting that the neural processing of more abstract vs. lower-level sensory information
is under greater genetic control. Next, we ground the heritability of high-dimensional BOLD time
courses in genetic control over stable spatial (e.g., functional cortical topography) and temporal
(e.g., neural timescale) aspects of brain function. Finally, we reveal a similar pattern of results for
a different set of high-dimensional brain responses: functional connectivity profiles. Taken
together, these results characterize the degree to which sensory processing is controlled by
genetics and illustrate the benefits of a reductionist approach to studying the heritability of
complex neurobiological phenomena, providing a foundation for future multi-scale studies of the
mechanisms that underlie heritable differences in brain function.
Methods
Participants
Data used for this project come from the 178 subjects in the Human Connectome Project (HCP)
Young Adult 7T release who completed every movie-watching run (Van Essen et al., 2013     ). All
participants were healthy individuals between the ages of 22 and 36 (mean age = 29.4 years,
standard deviation = 3.3) and provided informed written consent as part of their participation in
the study. Self-reported racial identity in this sample was 87.6% White, 7.3% Black or African
American, 3.9% Asian/Native Hawaiian/Other Pacific Islander, and 1.1% unknown/not reported,
and 1.7% of the sample identified as Hispanic/Latino. HCP twin zygosity was determined by
genotyping (166 subjects) or self-report (4 subjects), which identified 51 monozygotic (MZ) twin
pairs and 34 dizygotic (DZ) twin pairs in the present sample, which also contains 2 pairs of non-
twin siblings and 4 singletons. All sibling pairs shared the same gender. Out of these 178 subjects,
we identified 690 unrelated dyads who were matched in gender and age in years. Because two of
these participants (from two separate MZ twin pairs) did not complete every resting state run,
analyses involving resting state data use a sample size of n = 176.


## Page 4

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
4 of 37
fMRI data
All fMRI data were collected on a 7T Siemens Magnetom scanner across four sessions spanning
multiple days. Each day involved two resting state (900 volumes) and two movie-watching scans
(variable durations) across two sessions, all with the following sequence: time of repetition (TR) =
1000 ms, echo time (TE) = 22.2 ms, number of slices = 85, flip angle = 45 degrees, spatial resolution
= 1.6 mm3. During movie runs, subjects passively watched short clips from either independent
films or major motion pictures as well as a montage of brief videos. More information on these
clips can be found at https://db.humanconnectome.org     . Each video clip was preceded by 20
seconds of rest, so we discarded all volumes that took place during these rest blocks as well as the
first 20 volumes of each clip to prevent rest data and onset transients from biasing our
intersubject correlation (ISC) measurements. Rest and movie data from the same day were
normalized and concatenated, yielding one rest run (1800 volumes) and one movie run (1432
volumes Day 1, 1409 volumes Day 2) for each day of data collection.
Preprocessing and parcellation
The fMRI data used here were preprocessed as described in a previous publication (Gruskin &
Patel, 2022     ). Briefly, we used ICA-FIX denoised data from which the global signal and its
temporal derivative were removed. To examine the effects of parcellation resolution, data were
parcellated using the 10 resolutions of the Schaefer atlas (100 to 1000 parcels; Schaefer et al.,
2018     ). The ICA-FIX data downloaded here were aligned across subjects using the HCP’s MSMAll
(henceforth “MSM”) method, which registers data based on several multimodal properties in a
topology-preserving manner (Feilong et al., 2021     ; Robinson et al., 2014     ).
Intersubject correlation (ISC)
Dyadic ISC analyses were used to quantify BOLD time course similarity between all pairs of
participants. For each vertex or parcel, each participant’s BOLD signal time course from a given
day’s movie-watching scan was normalized and (Pearson) correlated with the corresponding
BOLD signal time courses from all other participants to yield an ISC matrix. We used non-
parametric permutation testing to quantify average differences in ISC for each parcel in the
Schaefer 400 atlas for each day of data collection across three groups: MZ dyads, DZ dyads, and
unrelated (UR) dyads, where all UR dyads were matched for gender and age in years. All Pearson r
values in this and all other analyses were Fisher z-transformed before averaging (and converted
back to Pearson r for visualization). Because some participants contributed to ISC values for
multiple dyads (thus violating independence assumptions), we shuffled dyad labels 10,000 times to
generate a null distribution against which we compared the empirical group difference using the
following two-sided test (which we used for all other permutation tests):
The resulting 2,400 p-values (400 parcels x 3 group differences x 2 days) were then false discovery
rate (FDR) corrected using the Benjamini-Hochberg method (Benjamini & Hochberg, 1995     ).
Functional connectivity (FC)
We constructed resting state functional connectivity (rest FC) and movie-watching functional
connectivity (movie FC) matrices by (Pearson) correlating the time courses of all parcel pairings
from the 400-parcel Schaefer atlas, using data from the two concatenated rest scans. These
matrices were produced for each subject and for each day of data collection. We applied the same
procedure to the movie-watching data, enabling us to compare the heritability of rest and movie
FC profile similarities and strengths.


## Page 5

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
5 of 37
To evaluate the similarity of FC profiles for each combination of the 17 networks defined by Yeo et
al. (Yeo et al., 2011     ), we first vectorized the FC matrices of each subject. We then extracted the
correlation coefficients corresponding to the parcel-level connections comprising each Yeo
network combination and computed correlations for these vectorized profiles across all subject
pairs. We also assessed subject-level FC strengths for each network combination by averaging the
correlation coefficients for all parcel-level connections within a network combination.
Significance testing for the group (MZ, DZ, and UR) differences in FC profile similarity was
performed with the non-parametric permutation method used to test group differences in ISC in
the previous section.
ISC and FC profile heritability analyses
BOLD time courses and FC profiles are high-dimensional variables, and reducing their
dimensionality in order to use classical heritability analyses would sacrifice both statistical power
and interpretability. As such, we quantified their heritability with a multidimensional estimator
that has been used in several similar studies (Anderson et al., 2021     ; Busch et al., 2023     ; Ge et
al., 2016     ). This model (detailed in Anderson et al., 2021     ) takes as input a Subjects x Subjects
kinship matrix describing the degree of genetic relatedness between individuals (1 for MZ twins,
0.5 for non-MZ siblings, 0 for all other pairs) as well as a Subjects x Subjects phenotypic similarity
matrix. Here, each value of the phenotypic similarity matrix corresponded to a Pearson
correlation coefficient describing either BOLD time course (per parcel or voxel) or FC profile
similarity (per network combination) for a given subject pair. To estimate heritability, the variance
in phenotypic similarity is then partitioned into a component attributable to genetic factors,
represented by the kinship matrix, with age, gender, and per-scan head motion included as
covariates. Significance testing of individual multidimensional heritability values and calculation
of their standard errors was performed using the method established in Anderson et al., 2021     .
Specifically, the kinship matrix was shuffled 10,000 times to generate a null distribution against
which the observed value could be compared, and the resulting p-values were FDR corrected.
Standard errors (SEs) were derived through a block jackknife method in which heritability was
recalculated 90 times after leaving out all members of one of the 90 families in the dataset on each
iteration. We then used these SEs to generate 95% confidence intervals (CIs).
To compare the heritability of movie and rest FC profiles, we used the following non-parametric
permutation approach. For each day of data collection, we randomly shuffled each subject’s movie
and rest FC matrices (and their corresponding framewise displacement (FD) covariates) and
recalculated FC profile heritability using the shuffled FC matrices. We then subtracted the two
resulting heritability values for each of the 153 unique network combinations and averaged these
across networks to obtain 17 values reflecting the null difference in FC profile heritability for each
network. We repeated this procedure 10,000 times and then used the two-sided test described
above to generate a p-value for each network, and these 34 p-values (17 networks x 2 days) were
then FDR corrected. Because complete resting state datasets were not available for 2/178 movie-
watching subjects, we only used movie-watching data from the 176 subjects who also had
complete resting state data for this permutation test.
To determine the sample size necessary for stable multidimensional heritability results, we
conducted our BOLD time course heritability analysis multiple times while systematically
excluding between 5% and 90% of families. At each exclusion level, we performed 100 iterations,
each time randomly removing a subset of families. After each iteration, we calculated the absolute
difference between the heritability values obtained from the subsample and those from the full
sample for each parcel. We then averaged these differences across all parcels and iterations to
obtain the mean absolute error (MAE) for that exclusion level. Similarly, to assess the stability of
the spatial pattern of our results, we computed Spearman correlations between the subsample and
full sample heritability values across parcels and averaged these correlations across all iterations.


## Page 6

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
6 of 37
Frequency-dependent ISC heritability analyses
To characterize the frequency-specific heritability of movie-evoked BOLD time courses, we
performed a spectral analysis of the BOLD time series data across all subjects and parcels. First,
we set a high-frequency cutoff equal to the Nyquist frequency of our data (0.5 Hz) and defined a
low-frequency cutoff at 0.0042 (1/238) Hz, corresponding to the length of the longest clip. We then
computed the power spectrum for each parcel, subject, and day of data collection by applying a
Fast Fourier Transform to the time series data of each subject and then averaging these spectra
across all subjects, parcels, and scanning days. To ensure consistent comparison across
frequencies, we interpolated the power spectra onto a common frequency axis with a resolution of
0.001 Hz. The cumulative power distribution was then calculated from this averaged power
spectrum. To partition the frequency range into bands containing equal fractions of the total
power, we identified frequency cutoffs corresponding to quintiles of the cumulative power
distribution. This resulted in five frequency bands: Band 1 (0.004–0.02 Hz), Band 2 (0.02–0.04 Hz),
Band 3 (0.04–0.07 Hz), Band 4 (0.07–0.14 Hz), and Band 5 (0.14–0.50 Hz). For each of these bands,
we applied fourth-order Butterworth bandpass filters to the concatenated BOLD time courses of
each subject and parcel and recalculated ISC and BOLD time course heritability as described
above. To further characterize frequency-dependent changes in heritability at the parcel level, we
then Spearman-correlated the spatial patterns of heritability with the sensorimotor-association
hierarchy rankings from Sydnor et al. (2023)     . Significance testing for these sensorimotor-
association results was performed using BrainSMASH, as described below.
FC strength heritability analysis
Because FC strengths are inherently one-dimensional traits, their heritability was quantified with
SOLAR (Almasy & Blangero, 1998     ), which generates estimates using variance-component linkage
analyses. Age, gender, and head motion were used as covariates in all FC strength analyses, and
SEs were calculated using the block jackknife procedure described above. To test the significance
of differences in rest vs. movie FC strength heritability, we compared the observed differences to
null distributions generated by 1,000 permutations of the same procedure described above for FC
profiles.
Hyperalignment
We used piecewise response and connectivity hyperalignment (RHA and CHA, respectively), two
complementary methods for aligning data into a topography-independent common space, to
functionally align vertex-level BOLD time courses across subjects. We decided to use piecewise
hyperalignment, in which vertices are aligned within non-overlapping parcels, instead of
searchlight hyperalignment because it has been shown to be both more accurate and more
efficient (Bazeille et al., 2021     ). We then repeated our BOLD time course and FC profile
heritability analyses using these hyperaligned datasets to quantify the extent to which brain
response heritability reflects genetic control over cortical topography. RHA: For each Schaefer
atlas parcel and day of data collection, we used iterative Procrustes transformations to align
vertex-level BOLD time courses to a common model information space. This yielded one invertible
transformation matrix per parcel and per subject, which we then used to project data from the
other day of data collection (which was not used to generate the transformation matrices) into the
common information space. CHA: The same iterative Procrustes approach was used for CHA, but
here the input data consisted of rest FC profiles for each vertex within a given parcel. Each
vertex’s functional connectivity profile consisted of the Pearson correlation coefficients between
that vertex’s time course and the average time courses from all other parcels, the number of which
varied with different parcellation resolutions. After training a model whose dimensions
correspond to shared rest FC properties (instead of the shared response properties in RHA), we
used the corresponding transformation matrices to align movie-watching timeseries data from the
other day of data collection. To quantify the spatial scale at which cortical topographies contribute


## Page 7

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
7 of 37
to brain response heritability, we repeated the RHA and CHA procedures described above for each
of the 10 Schaefer atlas resolutions to yield 21 datasets per subject (10 RHA-aligned datasets, 10
CHA-aligned datasets, and the original MSM-aligned dataset).
Relationships between parcel area and heritability
We used power law modeling to characterize the relationship between cortex-level heritability
and hyperalignment area. To calculate parcel areas, we first generated vertex-level areas using the
-surface-vertex-areas function in wb_command and then summed the areas of all vertices included
in each parcel. Next, for each hyperalignment method and each day of data collection, we used
nonlinear least squares regression to fit a power law model (y = a · xb + c) to the 11 heritability
values calculated from the 10 Schaefer atlas resolutions and one from MSM-only aligned data and
the 10 average Schaefer atlas parcel areas as well as 0 (corresponding to no hyperalignment in the
MSM-only data).
Neural timescale (NT) analyses
To determine the extent to which BOLD time course heritability reflects genetic control over NTs,
we took an approach used in numerous studies to calculate NT at rest (known as intrinsic neural
timescale, or INT; Watanabe et al., 2019     ; Wengler et al., 2020     ) and applied it to movie-
watching data. NTs were calculated separately for each day of data collection as the sum of the
autocorrelation coefficients from the first lag until the first lagged timepoint with a non-positive
autocorrelation coefficient (Wengler et al., 2020     ) for each vertex. Because time courses that are
themselves more temporally autocorrelated will have a higher variance in their correlations with
each other (Shinn et al., 2023     ), and because stimulus-evoked BOLD time courses tend to be
positively correlated across subjects, we reasoned that pairs of individuals with longer collective
NTs would have more correlated BOLD time courses. To test this directly, we (Spearman)
correlated ISC values from one day of data collection with NTs calculated using the other day’s
data across all possible subject pairs. We tested the significance of the resulting vertex-wise
correlation coefficients by randomly pairing the ISC values from one subject pair with the
summed NTs from another and repeated the process 1,000 times to generate a null distribution
against which we performed the aforementioned two-sided test.
We then averaged NT values across all vertices to get a single, cortex-wide NT measure for each
subject and each day of data collection. Dyadic NT similarity was quantified as the absolute value
of the difference between each subject pair’s cortex-wide NT values. This differencing approach
yielded several extreme values. We thus used the 1.5*IQR method to identify 4% of dyadic NT
values as outliers and excluded them from the group differences analyses. We then used the
permutation procedure described in section 2.4 to test the significance of these group differences
in NT similarity. We also included subject-level NTs as covariates in some multidimensional
heritability analyses. When calculating heritability at a given vertex for one day of data collection,
the NTs for that vertex from the other day of data collection were used as covariates. To evaluate
whether including NTs as covariates decreased BOLD time course heritability, we generated a null
distribution of 1,000 heritability values by randomly shuffling vertex-level NT vectors such that
the NTs for one subject were paired with the ISC values and covariates from another subject. We
then calculated two-sided permutation p-values using the formula described above.
Significance testing for autocorrelated brain maps and FC matrices
We used Spearman correlations to quantify the reliability of ISC and FC heritability maps across
days, as well as relationships between these heritability maps and the sensorimotor-association
hierarchy ranking from Sydnor et al. (2023)     . Because cortical spatial maps are significantly auto-
correlated, we used the variogram matching approach from BrainSMASH (Brain Surrogate Maps
with Autocorrelated Spatial Heterogeneity; Burt et al., 2020      to assess the significance of these
correlations. Briefly, this test works by generating autocorrelation-matched surrogates for one of


## Page 8

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
8 of 37
the empirical maps from each correlation, calculating Spearman correlations between these
surrogates and the other empirical map, and then comparing these null correlations to the
correlation between both empirical maps. We performed independent tests using 1,000 unique
surrogates for each hemisphere and averaged the two p-values to get the whole-cortex p-values we
report in this manuscript. Because values in FC heritability matrices are similarly not independent
of each other, we used Mantel tests with 10,000 permutations to test their reliability.
Analyses were performed in MATLAB (R2023b), Python, and R. All cortical surface visualizations
were performed with Connectome Workbench (Marcus et al., 2011     ).
Results
Similarity in movie-evoked brain activity
increases with genetic relatedness
To characterize the heritability of brain responses to complex stimuli, we used 7T fMRI data from
178 HCP Young Adult subjects to (1) quantify the heritability of brain activity and connectivity
patterns during movie-watching and (2) determine the extent to which the heritability of these
dynamic, high-dimensional brain responses is grounded in stable and fundamental aspects of
brain function like cortical topographies and neural timescales.
We first aimed to determine how closely movie-evoked brain responses were shared among pairs
of individuals, and whether this similarity was influenced by their genetic relationship. Using
inter-subject correlation (ISC) of parcellated BOLD time courses to index brain activity similarity,
we found that identical (or monozygotic, MZ), fraternal (or dizygotic, DZ) and age- and gender-
matched unrelated (UR) dyads differed significantly in their level of brain activity similarity in a
manner consistent with their relative degrees of genetic relatedness (although spatial distributions
of ISC were consistent across groups, Fig. S1A). More specifically, identical twins’ BOLD time
courses were 59% more similar than those from pairs of unrelated individuals, with this finding
being statistically significant in 95% of brain parcels after correcting for multiple comparisons (P <
.05, FDR-corrected). When comparing identical twins to fraternal twins, the identical twins’ brain
activity was still more similar, but by a smaller margin of 24%, and with fewer brain parcels
showing a significant effect (10% of parcels significant at P <.05, FDR-corrected). Fraternal twins
also had more similar time courses than unrelated pairs, but again, this was less pronounced than
the identical/unrelated comparison (29% higher ISC, with 20% of parcels significant at P <.05, FDR-
corrected). We observed the greatest group differences in parcels with medium levels of ISC
(separation between the three traces in Fig. 1B     ), suggesting that floor and ceiling effects may
limit the degree to which genetic relatedness impacts brain activity in regions that are not driven
by audiovisual stimuli and regions that exhibit highly stereotyped activity across all subjects,
respectively.
Patterns of brain activity during movie-watching are heritable
After establishing that more genetically similar individuals share more similar movie-evoked
BOLD time courses, we next sought to quantify the heritability of these brain responses. To do this,
we leveraged a multidimensional estimator that has been used to assess the heritability of similar
brain phenotypes (Anderson et al., 2021     ; Busch et al., 2023     ; Ge et al., 2016     ). Controlling for
age, gender, and head motion, we found that movie-evoked BOLD time courses were heritable
across almost all of cortex on both days of data collection (Fig. 2A     , Day 1 mean h2 = .064 ± .034,
Day 2 mean h2 = .068 ± .036, 99% of parcels significant on both days at FDR-corrected P < .05), and
the spatial pattern of heritability across the cortex was very consistent across days of data
collection (Spearman ρ = .96, PbrainSMASH < .001).


## Page 9

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
9 of 37
David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
9 of 37
Figure 1.
BOLD time course similarity scales with genetic relatedness across the cortex. (A) Group differences in average BOLD time
course similarity (indexed by ISC) show that BOLD time course similarity is greater among dyads who are more genetically
related (51 MZ dyads, 34 DZ dyads, 690 UR dyads). (B) Group-average ISC values used to create the difference maps in A,
plotted in order of average ISC across all subject pairs, show that group differences are most pronounced in parcels with
medium to high ISC (shading = SEM).
Figure 2.
BOLD time courses are heritable across the cortex. (A) Cortical surfaces show heritability of BOLD time courses parcellated
using the Schaefer 400 atlas, controlling for age, gender, and head motion (mean h2 Day 1 / Day 2 = .064 ± .034/.068 ± .036).
(B) Residuals after regressing parcel-level ISC from parcel-level heritability show that BOLD time courses in auditory cortices
are less heritable than would be expected based on ISC, whereas the opposite is true for lateral prefrontal and temporo-
occipito-parietal junction parcels.


## Page 10

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
10 of 37
Although heritability studies of one-dimensional traits (e.g., height) tend to require larger samples
than the one used here, the multidimensional nature of our analysis affords us considerable
power to detect small effects even with our relatively modest sample size (Anderson et al., 2021     ;
Ge et al., 2016     ). To illustrate this point, we repeated our BOLD time course heritability analysis
after excluding up to 90% of families in the present dataset and found that even after excluding
half of our subjects, the average difference in h2 magnitude across parcels and between each
subsample and the results reported above was less than .01, and the average spatial correlation
(Spearman ρ) between subsample and full sample heritability values was greater than .9 (Fig. S2).
Unsurprisingly, the spatial pattern of BOLD time course heritability was closely related to the
spatial pattern of ISC (Day 1: Spearman ρ = .88, PbrainSMASH < .001, Day 1: Spearman ρ = .86,
PbrainSMASH < .001), reflecting the simple fact that the heritability of movie-evoked BOLD time
courses will be lower in parcels with less movie-driven activity to begin with. To characterize the
heritability of BOLD time courses relative to the amount of movie-driven activity in each parcel,
we regressed parcel-level ISC values (averaged across subject pairs) from heritability values and
plotted the residuals in Fig. 2B     . Here, we observed that BOLD time courses were
disproportionately more heritable in more associative lateral prefrontal and temporo-parieto-
occipital junction parcels, while responses in lower-level auditory areas were less heritable than
would be expected given their ISC. This indicates that although these more associative parcels do
not encode a substantial amount of stimulus-specific information, what information they do
encode and/or how they encode it is under increased genetic control compared to auditory
parcels.
After establishing that movie-evoked BOLD time courses are heritable, we next sought to
determine the extent to which this heritability reflects genetic control over high- vs. low-level
sensory processing. To do this, we leveraged the fact that low-level features of movie stimuli (e.g.,
visual motion and speech) tend to oscillate on the order of seconds (or faster), whereas higher-
level aspects of the stimulus (e.g., social content and narrative structures) are encoded at lower
frequencies (Baldassano et al., 2017     ; Honey et al., 2012     ; Kauppi et al., 2010     ). Similar to
previous work on frequency-specific ISC (Kauppi et al., 2010     ), we filtered our data into five non-
overlapping frequency bands, each containing an equal proportion of the total spectral power,
and generated overall and residualized (with respect to ISC) heritability maps for each band (Fig.
3A and D     ). We observed that cortex-wide BOLD time course heritability increased
monotonically with the period of the frequency band, such that heritability was over 50% higher
in the slowest frequency band (0.004–0.02 Hz) compared to the unfiltered data (Fig. 3B and E     ).
This suggests that genetic factors influence the neural processing of complex audio-visual features,
and that this influence is greater than for lower-level sensory features. Interestingly, we also
observed that both overall and residualized heritability were considerably lower in the one supra-
BOLD frequency band (0.14–0.5 Hz; Fig. 3      second column from the left) compared to the
unfiltered data. This indicates that although there is synchronized high-frequency information in
our data (possibly due to aliased cardiovascular and respiratory signals; Pérez et al., 2021     ), this
information is largely not heritable and further supports a BOLD etiology for the heritability
results shown above.
Previous studies have shown that during movie-watching, more associative regions process
abstract information at longer timescales that range from tens of seconds to minutes, whereas
sensory areas encode lower-level features at higher frequencies (Baldassano et al., 2017     ; Hasson
et al., 2008     ; Honey et al., 2012     ). As such, we hypothesized that the higher heritability we
observed in slower frequency bands was driven by increased heritability in associative (vs.
sensory) parcels. To test this hypothesis, we correlated parcel-level differences in heritability
between the slowest and fastest BOLD-sensitive frequency bands with sensorimotor-association
hierarchy rankings from Sydnor et al., 2023      (higher ranking = more associative) and found that
heritability increases from the fastest to slowest frequency band were indeed larger for more
associative parcels (Day 1: Spearman ρ = .47, PbrainSMASH < .001, Day 1: Spearman ρ = .35,


## Page 11

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
11 of 37
David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
11 of 37
Figure 3.
BOLD time course heritability is greater in slower frequency bands, especially for more associative parcels. (A) Purple/yellow
cortical surfaces (upper row) show unfiltered BOLD time course heritability (upper left is identical to Fig. 2A     ) as well as the
heritability of BOLD time courses filtered with five frequency bands, with greater heritability in slower bands for Day 1 data.
Red/blue cortical surfaces show BOLD time course heritability residuals after regressing out parcel- and frequency-level
differences in ISC (lower left is identical to Fig. 2B     ), with greater residuals in slower frequencies and more associative
parcels. (B) Scatter plot shows heritability averaged across the cortex for each frequency band (i.e., the averages of the upper
row of surfaces in A; shading = jackknife SEM). (C) Scatter plot shows the difference in heritability between the slowest and
fastest BOLD-sensitive frequency bands for each of the Schaefer 400 parcels plotted against parcel ranks from the Sydnor et
al. sensorimotor-association hierarchy (higher = more associative). Least squares lines were added to highlight the positive
relationships between average h2 and parcel ranks but note that these relationships were formally tested with Spearman
correlations. (D–F) Same as A–C for Day 2 data.


## Page 12

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
12 of 37
PbrainSMASH < .001; Fig. 3C and F     ). Because removing rest and onset blocks from each clip and
concatenating the two movie-watching runs from each day introduced temporal discontinuities
that could impact our filtering results, we re-ran our analyses using the original, uncensored time
courses and observed similar results (Fig. S3).
We chose to initially analyze BOLD time courses parcellated using the Schaefer 400 atlas because
parcellation reduces multiple comparisons, noise, and computational burden. However, we
repeated our heritability analyses using data parcellated with 9 other resolutions of the Schaefer
atlas and found that heritability reliably increased with average parcel size (Fig. S4). Moreover, the
interpretation of parcellated BOLD time course heritability is complicated by the fact that
macroscale areal boundaries are known to be heritable (Xu et al., 2016     ). As such, we use vertex-
level data in our subsequent BOLD time course analyses.
Heritable movie-evoked BOLD time courses
reflect heritable cortical topographies
Our analyses of data aligned using standard anatomical methods (i.e., MSM) have demonstrated
that patterns of movie-evoked brain activity and connectivity are heritable. Importantly, these
patterns reflect two distinct and fundamental aspects of brain function: how stimuli are processed
and where stimuli are processed. For example, when analyzing brain responses in a dorsal brain
region (as shown in Fig. 5A     ), two twins (left and center) may appear to process stimulus
information more similarly than an unrelated individual (right), based on having higher ISC
values for that region. However, this apparent disparity arises purely from spatial differences in
where the same information is processed: the unrelated individual in fact exhibits the same
functional responses as the twins (i.e., the green and purple time courses), just in different cortical
locations. These individual-specific maps of how shared brain functions are spatially distributed
are known as cortical topographies (Haxby et al., 2011     , 2020     ), and recent work has shown
that cortical topographies defined at rest are influenced by genetic factors (Anderson et al.,
2021     ; Burger et al., 2022     ; Busch et al., 2023     ). Therefore, we hypothesized that part of the
heritability observed in our previous analyses might reflect genetic control over cortical
topography (or “where” information is processed), in addition to genetic influences on
information processing itself.
One effective method used to separate the topography-dependent and topography-independent
aspects of cortical information processing is known as hyperalignment. Hyperalignment aligns
individual brains into a common high-dimensional functional space based on shared functional
responses during the same task or stimulus (Haxby et al., 2011     ). By aligning fMRI data across
subjects into a topography-independent functional space, hyperalignment yields datasets that
allow for a direct comparison of how information is processed across individuals, independent of
individual differences in where that information is processed.
In this study, we used hyperalignment to quantify the extent to which brain response heritability
reflects genetic control over how vs. where information is processed. To hyperalign each subject’s
movie-watching data to a common functional space for a given day of data collection, we used
idiosyncratic transformation matrices that were learned from either the other day’s movie activity
time courses (response hyperalignment, or RHA) or from rest FC profiles calculated from the other
day’s scans (connectivity hyperalignment, or CHA). Although RHA and CHA align fMRI data with
similar fidelity (Guntupalli et al., 2018     ; Haxby et al., 2020     ), using both methods allows us to
evaluate whether heritable functional topographies reflect the brain’s intrinsic functional
architecture or movie watching-specific response functions. We performed both RHA and CHA in a
piecewise fashion (Bazeille et al., 2021     ), aligning vertex-level data within individual Schaefer
parcels—in other words, a vertex in one Schaefer parcel would be aligned with other vertices in
that parcel and never with vertices from other parcels.


## Page 13

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
13 of 37
Hyperalignment aligns vertices with similar functional responses across subjects, inherently
increasing ISC for all subject pairs. However, to the extent that cortical topographies are under
genetic control, twins’ brains are intrinsically more aligned than those of unrelated individuals.
Therefore, we predicted that hyperalignment would decrease observed heritability across the
cortex by eliminating the topography-dependent component of heritability and increasing
response similarity more in unrelated dyads than in twin pairs.
Starting with the coarsest Schaefer atlas resolution (100 parcels, mean parcel area = 1,013 mm2),
we found that RHA and CHA significantly decreased BOLD time course heritability to similar
degrees across the cortex. Compared to MSM-aligned data (Fig. 4C     , left column), hyperalignment
reduced BOLD time course heritability across the cortex by 33% on Day 1 (95% CI = [25–40%]) and
31% on Day 2 [22–39%] for RHA (Fig. 4C     , middle column), and by 30% [21–39%] and 25% [18–
33%] for CHA (Fig. 4C     , right column). These decreases were most apparent in visual cortex, but
were also prominent in associative areas like the right temporoparietal junction and bilateral area
55b (Fig. 4D     ), and the spatial pattern of this effect was consistent across days (RHA: Spearman ρ
= .66, PbrainSMASH < .001, CHA: Spearman ρ = .69, PbrainSMASH < .001) and hyperalignment methods
(Day 1: Spearman ρ = .76, PbrainSMASH < .001, Day 2: Spearman ρ = .74, PbrainSMASH < .001).
To quantify the spatial scale at which cortical topography influences BOLD time course
heritability, we then repeated RHA and CHA using the 9 other Schaefer atlas resolutions (200 to
1000 parcels). Because hyperalignment can eliminate more heritable differences in cortical
topography when it is performed in larger parcels, we predicted that hyperalignment across larger
parcels would decrease BOLD time course heritability to a greater extent. As expected, the
magnitude of these reductions decreased as hyperalignment was performed across smaller areas
(Fig. 5E     ). To quantify this relationship, we fit power law models of the form y = a · xb + c to the
11 hyperalignment resolutions (corresponding to the average parcel areas for the 10 Schaefer
atlases as well as 0 for no hyperalignment) and their corresponding average h2 values. We found
that these power law models accurately characterized how heritability scaled with
hyperalignment resolution for both RHA and CHA on Day 1 (RHA: y = −0.0008 ⋅ x0.32 + 0.023, R2
adj.
= .99, CHA: y = −0.0004 ⋅ x0.41 + 0.023, R2
adj. = .99) and Day 2 (RHA: y = −0.0007 ⋅ x0.34 + 0.023, R2
adj. =
.99, CHA: y = −0.0003 ⋅ x0.43 + 0.023, R2
adj. = .99), whereas linear, quadratic, and logarithmic models
performed worse (Fig. S5).
Heritability of BOLD time courses is related to neural timescales
In the previous section, we found that individual differences in a stable aspect of brain function
(cortical topography) accounted for 30–40% of the heritability of movie-evoked brain responses.
Importantly, cortical topography is a largely spatial trait. Although it captures significant inter-
individual variability in how brain function varies over space, it is not directly related to how
brain responses evolve over time. As such, we reasoned that the heritability of high-dimensional
brain responses might also be grounded in the heritability of stable, temporal properties of brain
function. One such property is the neural timescale (NT), which is thought to index the duration of
information storage in a given circuit or region. Across the cortex, more associative areas are
known to have longer NTs (which is consistent with our frequency-dependent heritability results
in Fig. 3     ), but substantially and behaviorally-relevant variability in NTs also exists across
individuals, such that individuals with longer NTs in a given region integrate sensory information
across longer periods of time (Wengler et al., 2020     ). NTs are commonly operationalized as the
area under the curve of the autocorrelation function (ACF) until the lag preceding the first
negative ACF value (Wengler et al., 2020     ). Because stimulus-evoked time courses that are more
autocorrelated will tend to be more correlated with each other (see Methods), we suspected that
NTs could be an important determinant of ISC. To test this, we correlated the sum of each dyad’s
NTs from one day’s movie watching scan with their ISC from the other movie watching scan and
found that we could explain a considerable portion of the variability in pairwise ISC from NTs
alone (max/mean correlation Day 1: ρ = 0.56/0.10, Day 2: ρ = 0.65/0.11, 44% of vertices significant at


## Page 14

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
14 of 37
David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
14 of 37
Figure 4.
Hyperalignment reduces BOLD time course heritability. (A) Cartoon illustrates the difference between shared cortical
topographies and shared (topography-independent) information content. (B) Diagrams illustrate the inputs to response and
connectivity hyperalignment (RHA and CHA, respectively) using the Schaefer 100 atlas. RHA topographies were learned using
BOLD time course data from the other day’s movie-watching scans, while CHA topographies were learned from vertex-level
FC profiles (i.e., correlations between one vertex’s BOLD time course and the average time course from each of the 99 other
parcels) calculated from the other day’s resting state scans. (C) Vertex-level BOLD time course heritability is highest for data
aligned via MSM (multimodal surface matching) and lower for data hyperaligned within 100 Schaefer atlas parcels using both
response hyperalignment (RHA) and connectivity hyperalignment (CHA). (D) Differences between the MSM-only and
hyperaligned heritability maps shown in (C) are distributed across the cortex but are most apparent in visual areas. (E) BOLD
time course heritability decreases as a function of hyperalignment parcel size according to a power law (purple and orange
lines); each dot corresponds to average cortex-wide heritability for data hyperaligned using one of the 10 Schaefer atlas
resolutions (shading = jackknife SEM).


## Page 15

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
15 of 37
David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
15 of 37
Figure 5.
Controlling for neural timescales (NTs) reduces heritability of BOLD time courses. (A) Bar plots show average pairwise
differences in cortex-wide NT across MZ, DZ, and unrelated dyads on both days of data collection, where only MZ and UR
group means differed significantly on both days (MZ Day 1/Day 2 means = 0.15/0.15, UR = 0.24/0.27, FDR-corrected Pperm <
.05). (B) Cortical surfaces show decreases in BOLD time course heritability after NTs calculated from the other day of data
collection were included as covariates in the multidimensional heritability analyses for MSM-aligned and RHA-aligned (using
the Schaefer 100 parcellation) data, most prominently in mid-level auditory and visual regions. These maps are thresholded
at Δh2 = ±0.01 to aid comparisons of MSM- and RHA-aligned results. The maximum differences in h2 after controlling for NTs
were −0.025 for MSM-aligned data and −0.007 for RHA-aligned data, respectively.


## Page 16

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
16 of 37
FDR-corrected Pperm < .05 on both days, Fig. S10). Given this relationship between NTs and ISC as
well as the fact that a similar measure of BOLD autocorrelation was recently shown to be heritable
(Christova et al., 2022     ), we hypothesized that some of the BOLD time course heritability not
accounted for by topography is underpinned by heritability of NTs.
Before testing this hypothesis directly, we first sought to establish that more genetically similar
individuals have more similar NTs. After calculating NTs at each vertex from each day’s movie-
watching data, we averaged these values to generate a single cortex-wide NT for each subject and
each day of data collection. We then examined pairwise differences in NT across MZ twins, DZ
twins, and age- and gender-matched unrelated dyads. As expected, we found that differences in
MZ twins’ NTs were significantly smaller than in unrelated individuals’ NTs on both days (Fig.
5A     , Day 1: ΔNTMZ = 0.15 ± .016, ΔNTUR = 0.24 ± .007, Pperm = .0005, Day 2: ΔNTMZ = 0.15 ± .014,
ΔNTUR = 0.27 ± .008, Pperm < .0001, and although the other comparisons also went in the expected
direction (MZ < DZ and DZ < UR), these differences were not statistically significant (FDR-corrected
Pperm > .05).
To quantify the extent to which BOLD time course heritability reflects genetic control over NTs, we
repeated the heritability analyses from earlier for each day of data collection, this time including
vertex-level NTs calculated from the other day’s data as co-variates (in addition to age, gender, and
head motion). We observed that controlling for NTs significantly reduced BOLD time course
heritability on both days in 5.7% of vertices (Fig. 5B      upper row, FDR-corrected Pperm < .05), most
prominently in speech and language areas (e.g., auditory/superior temporal cortices, area 55b) and
motion-sensitive visual areas (e.g., medial temporal and medial superior temporal cortices).
Although these reductions in heritability were more focal than those observed following
hyperalignment, they reached similar strengths, with decreases of 20–30% observed throughout
the superior temporal gyri on both days of data collection. After establishing that cortical
topographies and neural timescales both contribute to the heritability of high-dimensional brain
responses, we next sought to determine if these contributions are independent of one another. To
test this, we recalculated BOLD time course heritability following RHA using the Schaefer 100
parcellation (the most aggressive hyperalignment approach from the previous section), this time
controlling for NTs calculated from these RHA-aligned data. If cortical topography and neural
timescale constitute separable processes through which genetics shapes brain responses, we
would expect controlling for NTs in the RHA- and MSM-aligned data to reduce brain response
heritability to similar degrees. Instead, we observed a mixed result: although controlling for NTs
after hyperalignment further reduced BOLD time course heritability on both days in 1.5% of
vertices (FDR-corrected Pperm < .05, Fig. 6B     , lower row), the average magnitude of this decrease
across the cortex was 40% smaller than for the MSM-aligned data. This suggests that cortical
topography and neural timescale each account for some unique variance in brain response
heritability, but their contributions are not entirely independent.
Movie-evoked FC profiles are heritable
and reflect heritable cortical topographies
Thus far, we have demonstrated that movie-evoked BOLD time courses are heritable, and that this
heritability is related to genetic control over stable spatial and temporal aspects of brain function.
However, sensory information is encoded and processed not just in the activities of single regions
but also in the functional connectivity (FC) between multiple regions (Chen et al., 2014     ). To
determine if this other kind of movie-evoked brain response is similarly heritable, we repeated
our analyses using movie-watching FC (movie FC) profiles. Here, a given individual’s movie FC
profiles were calculated for each pair of 17 Yeo networks and each day of data collection as their
set of movie FC values for all connections between parcels in that pair of networks.


## Page 17

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
17 of 37
David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
17 of 37
Figure 6.
FC profile similarity scales with genetic relatedness across the cortex. (A) Group differences in average FC profile similarity
show that FC profiles are more similar for dyads who are more genetically related (51 MZ dyads, 34 DZ dyads, 690 UR dyads).
(B) Group-average FC profile similarity values used to create the difference maps in A, plotted in order of average FC profile
similarity across all subject pairs (shading = SEM).


## Page 18

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
18 of 37
Starting again with a dyadic similarity analysis, we observed that for all comparisons, the more
genetically related the dyads, the more similar their movie FC patterns (Fig. 6A     , MZ>UR / MZ>DZ
/ DZ>UR: 49% / 26% / 18% greater similarity across network combinations, 100% / 97% / 92% of
combinations significant at FDR-corrected P<.05 on both days).
Compared to group differences in ISC, movie FC profile similarities showed greater separation
between groups (Fig. 6B     , group average FC profile similarity shown in Fig. S7).
Given the greater between-group separation in FC profile similarity (vs. BOLD time course
similarity) in Fig. 6B      vs. Fig 1B     , we expected movie FC profiles to be more heritable than
movie-evoked BOLD time courses. Applying the same multidimensional heritability analysis to
movie FC profiles, we indeed found that FC profiles were around six times as heritable as BOLD
time courses (Fig. 7     , left column, Day 1 mean h2 = .36 ± .035, Day 2 mean h2 = .37 ± .038, all
network combinations significant on both days at FDR-corrected P < .05), and the pattern of
heritability values across network combinations was very consistent between days (Spearman ρ =
.92, PPerm < .001). The six-fold higher heritability of multidimensional FC profiles compared to
BOLD time courses likely results from each FC profile dimension representing a connectivity
strength calculated over many time-points between two cortical areas, whereas each BOLD time
course dimension reflects an activity magnitude at a single timepoint in one cortical area.
Consequently, FC profile dimensions are less noisy (due to being defined across many timepoints)
and capture more individual differences (due to being defined across multiple areas).
Although we are unaware of any previous studies that have investigated FC heritability during
movie watching, the heritability of resting state FC (rest FC) measures has been well established
(Anderson et al., 2021     ; Busch et al., 2023     ; Glahn et al., 2010     ). Compared to rest FC, movie FC
profiles serve as better identifiers of individuals (Vanderwal et al., 2017     ) and better predict
individual differences in behavior (Finn & Bandettini, 2021     ). Given movie FC’s increased
sensitivity to individual variability, we reasoned that movie FC profiles would be more heritable
than rest FC profiles. Using resting state data collected from the same subjects and on the same
days of data collection, we calculated rest FC profile heritability using the approach described
above and found that heritability was indeed lower than for movie FC profiles (Figure 7     ,
rightmost column), but this effect was limited to more sensory-oriented networks (Language,
Auditory, Somatomotor A and B, Visual A, B, and C, and Dorsal Attention B networks significant at
FDR-corrected P < .05 on both days). Across these networks, movie (vs. rest) FC profiles were 20%
more heritable on Day 1 (min. = 11%, max. = 30%) and 30% more heritable on Day 2 (min. = 19%,
max. = 44%). Rest FC profiles were not significantly more heritable than movie FC profiles in any
network. Because subjects tend to move more during resting state vs. movie-watching scans, and
because this could explain the higher heritability of movie FC profiles, we repeated our analyses
after censoring all frames with FD >0.2 mm and found the with- and without-censoring results to
be nearly identical (data not shown). Our connectivity analyses thus far have focused on FC
profiles (i.e., correlations across FC values) instead of FC strengths (i.e., the average of FC values),
as the low power afforded by our sample size precludes us from measuring the heritability of one-
dimensional phenotypes with high precision (Benson et al., 2022     ; Busch et al., 2023     ).
However, FC strengths are clinically and behaviorally relevant, and measuring how task
conditions and alignment approaches affect FC strength heritability across the cortex requires
substantially less power than resolving FC strength heritability values for individual network
combinations. With this in mind, we used SOLAR (Almasy & Blangero, 1998     ) to estimate the
heritability of FC strength in this and subsequent analyses and provide the corresponding figures
in the Supplementary Materials (Fig. S8).
We next repeated our FC profile (and strength) analyses using the hyperaligned data. Similar to
the effects of RHA and CHA on BOLD time course heritability, hyperalignment within the Schaefer
100 parcels significantly reduced FC profile heritability across network combinations by 39% on
Day 1 (95% CI = [32–46%]) and 41% on Day 2 [34–48%] for RHA, and by 20% [13–28%] and 18% [12–


## Page 19

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
19 of 37
David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
19 of 37
Figure 7.
FC profiles are heritable across network combinations. Heatmaps show heritability of FC profiles for all unique within- and
between-network combinations of the 17 Yeo networks after controlling for age, gender, and head motion. FC profiles during
movie-watching (left column) were more heritable than resting state FC profiles (middle column) for more sensory-oriented
networks (red rows in the right column).


## Page 20

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
20 of 37
25%] for CHA (Fig. 8A     ). However, we did observe some consistent differences between effects of
hyperalignment on FC profile vs. BOLD time course heritability. First, RHA decreased FC profile
heritability to a significantly greater extent than did CHA, seen in the larger separation between
purple and orange traces in Fig. 8B     . Second, hyperalignment’s effects on FC profile (vs. BOLD
time course) heritability were less variable across the different parcellation resolutions, seen in
the relatively flat slope between orange/purple dots. This is reflected in the lower power law b
coefficient values for FC profile (0.08–0.11, Fig. 8B     ) vs. BOLD time course heritability (0.32–0.43,
Fig. 4E     ). We observed a similar area-independent pattern of results for our FC strength analyses,
although here only RHA (and not CHA) significantly decreased FC strength heritability (Fig. S9).
Once again, linear, quadratic, and logarithmic models failed to explain the relationships between
hyperalignment resolution and FC profile (Fig. S10) and strength (Fig. S11) heritability compared
to power law models.
Discussion
In this study, we examined the heritability of movie-evoked BOLD activity and connectivity. First,
we showed that BOLD time courses and FC profiles are heritable across the cortex, especially in
and between the sensory and associative regions that are most reliably activated by the stimuli.
Second, we showed that this heritability is underpinned by genetic control over fundamental
spatial and temporal characteristics of brain function that reflect both where and how individuals
process sensory information. More specifically, our findings demonstrate that genetics influences
cortical topography as a power law function of cortical area, and that a key property of brain
function—the neural timescale—is responsible for an additional portion of BOLD time course
heritability, especially in auditory and speech-sensitive areas. Just as importantly, these results
suggest a modest ceiling for how much of this stimulus-driven activity and connectivity is under
genetic control, leaving the rest to non-genetic individual variation.
Studies using ISC to examine similarity of movie-evoked BOLD activity typically find highly
conserved responses in auditory and visual areas. We found that more genetically related
individuals exhibited greater ISC not only in these sensory areas, but also across most of cortex.
This increased ISC could reflect more similar stimulus processing in a number of ways. For
example, high-level attentional effects, such as twins attending to more similar aspects of the
stimulus, could account for this increase (Ki et al., 2016     ; Song et al., 2021     ). Such an attentional
effect would explain our finding that BOLD time courses in auditory cortex (vs. mid-level visual
and oculomotor areas) were less (vs. more) heritable than would be expected based on their
overall ISC (Fig. 2B     ), as eye movements gate incoming visual information but no analogous
mechanism exists in the auditory system, and eye movement patterns during complex scene
viewing are themselves moderately heritable (Kennedy et al., 2017     ). Alternatively, low-level
stimulus processing effects, such as twins having more similar population tuning than non-twins,
could also lead to greater ISC.
Our frequency-dependent heritability results offer some preliminary insights into the specific
aspects of sensory processing that these shared activity patterns represent. Here, we observed that
BOLD time course heritability was over 50% greater in the slowest frequency band compared to
the unfiltered data, and that this effect was driven by increased low-frequency heritability in more
associative parcels. Because these regions and frequency bands encode more abstract stimulus
features, this result suggests that the neural processing of high- vs. low-level sensory information
is under greater genetic control. Importantly, we note that interpretation of this result is limited by
reverse inference, and future studies that directly modulate low- and high-level stimulus
information will be necessary to more conclusively answer this question. Our approach differs
from previous studies of stimulus- or task-driven brain activity heritability in that our ISC-based
analyses don’t require assumptions about the nature of neural responses that, if inaccurate, could
decrease the sensitivity of heritability estimates. Furthermore, instead of collapsing brain activity


## Page 21

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
21 of 37
David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
21 of 37
Figure 8.
Hyperalignment reduces FC profile heritability. (A) Heatmaps show decreased FC profile heritability for most combinations of
17 Yeo networks following RHA (left) and CHA (right) compared to the MSM-only baseline. (B) Scatter plots show that
hyperalignment, especially with RHA, decreases FC profile heritability according to a power law function; each dot
corresponds to average cortex-wide heritability for data hyperaligned using one of the 10 Schaefer atlas resolutions (or MSM-
only alignment, shading = jackknife SEM).


## Page 22

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
22 of 37
measurements across trials or epochs, our analyses exploit the high-dimensional nature of BOLD
time courses by considering the unique information present at each timepoint. This multi-
dimensional aspect of our analyses allowed us to leverage the significant amount of data available
per subject to detect reliable (spatial ρ >.9 for heritability maps across days) effects even at the
level of individual vertices. Furthermore, although our BOLD time course heritability effect sizes
were modest (h2 ≤ .25 for parcels, h2 ≤ .12 for individual vertices), we note that these are
commensurate with other twin-based heritability estimates of sensory phenotypes measured with
fMRI (Alvarez et al., 2021     ).
Compared to our activity-based analyses, our FC analyses were more in line with previous work.
Indeed, the heritability of FC profiles has been investigated on multiple occasions, sometimes with
the same multidimensional estimator of heritability used here (Busch et al., 2023     ; Elliott et al.,
2019     ; Miranda-Dominguez et al., 2018     ). Still, several aspects of our study allowed us to reveal
novel results and add new context to established findings. For example, by analyzing resting state
and movie-watching data from the same subjects, we were able to show that FC profiles involving
sensory-oriented networks were significantly more heritable during movie-watching than at rest.
This finding is consistent with reports that movie FC profiles better identify individuals (Vanderwal
et al., 2017     ) and predict variability in behavioral traits (Finn & Bandettini, 2021     ) than resting
state FC profiles, and that including task data increases estimates of FC profile heritability (Elliott
et al., 2019     ).
Although BOLD time courses and FC profiles often serve as the fundamental brain phenomena to
be studied in fMRI experiments, they are complex entities that are underpinned by a variety of
lower-level biological processes (Hillman, 2014     ). As such, the heritability of movie-evoked brain
responses established here likely reflects genetic control over more basic aspects of brain function.
We demonstrated how two of these aspects, cortical topography and neural timescale, contribute
to the heritability of stimulus-driven BOLD activity.
First, we found that controlling for idiosyncratic cortical topographies via response and
connectivity hyperalignment (RHA and CHA) decreased activity heritability across the cortex. This
decrease was bigger when data were aligned across larger parcels, but the rate of this decrease
slowed as a power law function of parcel area, illustrating that genetic control of cortical
topography is greatest at the fine scale. In addition to decreasing BOLD time course heritability, we
found that RHA and CHA also decreased FC profile heritability, echoing recent work showing that
CHA decreases rest FC profile heritability in a developmental population (Busch et al., 2023     ).
Compared to our activity-based analyses, we noticed a far weaker effect of hyperalignment
resolution on FC profile heritability, likely because this analysis was performed at the parcel level
and across spatially distributed brain networks (thereby reducing the impact of local functional
alignment). Although hyperalignment served to reduce heritable individual variability across our
analyses, the residual post-hyperalignment heritability might be more behaviorally relevant, as
hyperalignment has been shown to increase associations between FC profiles and cognitive test
scores (Feilong et al., 2021     ). With this in mind, future studies that investigate genetic
correlations between brain function and behavioral variables may benefit from hyperalignment
in spite of the deleterious effects it had on heritability here.
Just as cortical topographies spatially constrain individual responses to incoming stimuli, neural
timescales (NTs) are stable temporal features of brain function that shape high-dimensional
activity and connectivity patterns (Shinn et al., 2023     ; Wengler et al., 2020     ). More specifically,
longer NTs are thought to reflect greater recurrent excitation at the micro-circuit level and yield
more stable integration of sensory information (Cavanagh et al., 2020     ; Watanabe et al., 2019     ).
Here, we found that MZ twins had more similar NTs than unrelated dyads; the fact that NTs
measured by fMRI track electrophysiological activity (Watanabe et al., 2019     ) suggests that this
reflects similarities in how movie stimuli were neurally encoded. We next showed that this genetic
similarity in NT magnitude contributes to genetic similarity in movie-evoked BOLD time courses,


## Page 23

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
23 of 37
such that controlling for vertex-level NTs accounted for up to ~30% of BOLD time course
heritability, an effect that was strongest in speech-related areas like the superior temporal gyri.
Importantly, controlling for NTs had a weaker effect on BOLD time course heritability after
hyperalignment. This is evidence that the topographic distribution of NTs, over and above their
magnitude, is under genetic control. Beyond genetics, our finding that subjects with longer NTs
had more correlated movie-evoked BOLD time courses suggests that decreased ISC in patients with
schizophrenia (Patel et al., 2021     ; Tu et al., 2019     ), autism (Salmi et al., 2013     ), and depression
(Gruskin et al., 2020     ) may be underpinned by shorter NTs in these same populations (Watanabe
et al., 2019     ; Wengler et al., 2020     ; Zheng et al., 2024     ).
Our work should be considered in light of an important demographic limitation. Almost 90% of
subjects in the present sample identified as White, and all subjects were between the ages of 22
and 36. As heritability estimates are known to differ across populations and age groups (Schmitt et
al., 2014     ; Zhang et al., 2023     ), the generalizability of our findings is limited by the demographic
characteristics of the HCP Young Adult sample used here (Ricard et al., 2023     ). In spite of this
limitation, this work constitutes an important first link between the growing fields of
neuroimaging genetics and “naturalistic” neuroscience. By considering BOLD time courses and FC
profiles alongside cortical topographies and neural timescales derived from independent data, we
reveal a multi-layered genetic influence that extends from basic features of brain function to
complex, individual-specific sensory processing patterns. This comprehensive approach paves the
way for future research to dissect the biological mechanisms that link genetics with sensory
processing in both typical and atypical populations. Finally, we note that less than half of the inter-
individual variability we observed in movie-evoked BOLD time courses and FC profiles was
heritable, leaving the majority of this variability to be explained by gene-environment interactions
as well as non-genetic factors such as life experiences and current behavioral state. As such,
additional work will be necessary to characterize these non-genetic factors.
Acknowledgements
We thank Avram Holmes and Erica Busch for helpful conversations regarding this project. Author
D.C.G. was supported by a NIH MSTP training grant (T32GM007367). Author G.H.P. was supported
by the NIMH (K23MH108711, R01MH121790, and R01MH123639) and by a David Mahoney
Neuroimaging Grant from the DANA Foundation. Data were provided by the Human Connectome
Project, WU-Minn Consortium (Principal Investigators: David Van Essen and Kamil Ugurbil,
1U54MH091657) funded by the 16 NIH Institutes and Centers that support the NIH Blueprint for
Neuroscience Research; and by the McDonnell Center for Systems Neuroscience at Washington
University. Author G.H.P. receives income and equity from Pfizer, Inc through family. Authors
D.C.G. and D.J.V. have no competing interests to declare. This preprint was created using the
LaPreprint template (https://github.com/roaldarbol/lapreprint     ) by Mikkel Roald-Arbøl.
Additional information
Citation diversity statement
Recent work in several fields of science has identified a bias in citation practices such that papers
from women and other minority scholars are under-cited relative to the number of such papers in
the field (Bertolero et al., 2020     ; Caplar et al., 2017     ; Chatterjee & Werner, 2021     ; Dion et al.,
2018     ; Dworkin et al., 2020     ; Fulvio et al., 2021     ; Maliniak et al., 2013     ; Mitchell et al., 2013     ;
Wang et al., 2021     ). Here we sought to proactively consider choosing references that reflect the
diversity of the field in thought, form of contribution, gender, race, ethnicity, and other factors.
First, we obtained the predicted gender of the first and last author of each reference by using


## Page 24

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
24 of 37
databases that store the probability of a first name being carried by a woman (Dworkin et al.,
2020     ; Zhou et al., 2020     ). By this measure and excluding self-citations to the first and last
authors of our current paper), our references contain 8.33% woman(first)/woman(last), 6.67%
man/woman, 26.67% woman/man, and 58.33% man/man. This method is limited in that a) names,
pronouns, and social media profiles used to construct the databases may not, in every case, be
indicative of gender identity and b) it cannot account for intersex, non-binary, or transgender
people. Second, we obtained predicted racial/ethnic category of the first and last author of each
reference by databases that store the probability of a first and last name being carried by an
author of color (Ambekar et al., 2009     ; Chintalapati et al., 2023     ). By this measure (and
excluding self-citations), our references contain 13.96% author of color (first)/author of color(last),
17.01% white author/author of color, 21.40% author of color/white author, and 47.63% white
author/white author. This method is limited in that a) names and Florida Voter Data to make the
predictions may not be indicative of racial/ethnic identity, and b) it cannot account for Indigenous
and mixed-race authors, or those who may face differential biases due to the ambiguous
racialization or ethnicization of their names. We look forward to future work that could help us to
better understand how to support equitable practices in science.
Data and code availability:
The raw HCP data used for this project can be downloaded from ConnectomeDB     . Code for all
analyses will be posted on Github      upon publication.
Author contributions
David C. Gruskin: Conceptualization, Methodology, Formal Analysis, Visualization, Writing–
Original Draft, Writing–Review & Editing
Daniel J. Vieira: Code review
Jessica K. Lee: Supervision
Gaurav H. Patel: Conceptualization, Writing–Review & Editing, Supervision
Additional files
Supplementary Material     


## Page 25

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
25 of 37
References
Almasy L., Blangero J. (1998) Multipoint quantitative-trait linkage analysis in general
pedigrees American Journal of Human Genetics 62:1198–1211 https://doi.org/10.1086/301844
Alvarez I., Finlayson N. J., Ei S., de Haas B., Greenwood J. A., Schwarzkopf S. (2021) Heritable
functional architecture in human visual cortex Neuroimage 239:118286 https://doi.org/10
.1016/j.neuroimage.2021.118286
Ambekar A., Ward C., Mohammed J., Male S., Skiena S. (2009) Name-ethnicity classification
from open sources In: Proceedings of the 15th ACM SIGKDD International Conference on
Knowledge Discovery and Data Mining pp. 49–58 https://doi.org/10.1145/1557019.1557032
Anderson K. M., Ge T., Kong R., Patrick L. M., Spreng R. N., Sabuncu M. R., Yeo B. T. T., Holmes A.
J. (2021) Heritability of individualized cortical network topography Proceedings of the
National Academy of Sciences 118:e2016271118 https://doi.org/10.1073/pnas.2016271118
Baldassano C., Chen J., Zadbood A., Pillow J. W., Hasson U., Norman K. A. (2017) Discovering
Event Structure in Continuous Narrative Perception and Memory Neuron 95:709–
721 https://doi.org/10.1016/j.neuron.2017.06.041
Bazeille T., DuPre E., Richard H., Poline J.-B., Thirion B. (2021) An empirical evaluation of
functional alignment using inter-subject decoding NeuroImage 245:118683 https://doi.org
/10.1016/j.neuroimage.2021.118683
Benjamini Y., Hochberg Y. (1995) Controlling the false discovery rate: A practical and
powerful approach to multiple testing Journal of the Royal Statistical Society. Series B
(Methodological) 57:289–300
Benson N. C., Yoon J. M. D., Forenzo D., Engel S. A., Kay K. N., Winawer J. (2022) Variability of
the surface area of the V1, V2, and V3 maps in a large sample of human observers The
Journal of Neuroscience 42:8629–8646 https://doi.org/10.1523/JNEUROSCI.0690-21.2022
Bertolero M. A., Dworkin J. D., David S. U., Lloreda C. L., Srivastava P., Stiso J., Zhou D., Dzirasa
K., Fair D. A., Kaczkurkin A. N., Marlin B. J., Shohamy D., Uddin L. Q., Zurn P., Bassett D. S. (2020)
Racial and ethnic imbalance in neuroscience reference lists and intersections with
gender bioRxiv https://doi.org/10.1101/2020.10.12.336230
Burger B., Nenning K.-H., Schwartz E., Margulies D. S., Goulas A., Liu H., Neubauer S., Dauwels
J., Prayer D., Langs G. (2022) Disentangling cortical functional connectivity strength and
topography reveals divergent roles of genes and environment NeuroImage
247:118770 https://doi.org/10.1016/j.neuroimage.2021.118770
Burt J. B., Helmer M., Shinn M., Anticevic A., Murray J. D. (2020) Generative modeling of brain
maps with spatial autocorrelation NeuroImage 220:117038 https://doi.org/10.1016/j
.neuroimage.2020.117038
Busch E. L., Rapuano K. M., Anderson K. M., Rosenberg M. D., Watts R., Casey B. J., Haxby J. V.,
Feilong M. (2023) Dissociation of reliability, heritability, and predictivity in coarse- and


## Page 26

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
26 of 37
fine-scale functional connectomes during development Journal of Neuroscience https://doi
.org/10.1523/JNEUROSCI.0735-23.2023
Caplar N., Tacchella S., Birrer S. (2017) Quantitative evaluation of gender bias in
astronomical publications from citation counts Nature Astronomy 1:0141 https://doi.org/10
.1038/s41550-017-0141
Cavanagh S. E., Hunt L. T., Kennerley S. W. (2020) A diversity of intrinsic timescales underlie
neural computations Frontiers in Neural Circuits 14 https://doi.org/10.3389/fncir.2020.615626
Chatterjee P., Werner R. M. (2021) Gender disparity in citations in high-impact journal
articles JAMA Network Open 4:e2114509 https://doi.org/10.1001/jamanetworkopen.2021.14509
Chen M., Han J., Hu X., Jiang X., Guo L., Liu T. (2014) Survey of encoding and decoding of
visual stimulus via FMRI: An image analysis perspective Brain imaging and behavior 8:7–
23 https://doi.org/10.1007/s11682-013-9238-z
Chintalapati R., Laohaprapanon S., Sood G. (2023) Predicting race and ethnicity from the
sequence of characters in a name arXiv https://doi.org/10.48550/arXiv.1805.02109
Christova P., Uğurbil K., Georgopoulos A. P. (2022) Heritability of brain neurovascular
coupling Journal of Neurophysiology 128:1307–1311 https://doi.org/10.1152/jn.00402.2022
Cole M. W., Ito T., Cocuzza C., Sanchez-Romero R. (2021) The functional relevance of task-
state functional connectivity Journal of Neuroscience 41:2684–2702 https://doi.org/10.1523
/JNEUROSCI.1713-20.2021
Dion M. L., Sumner J. L., Mitchell S. M. (2018) Gendered citation patterns across political
science and social science methodology fields Political Analysis 26:312–327 https://doi.org
/10.1017/pan.2018.12
Dworetsky A., Seitzman B. A., Adeyemo B., Nielsen A. N., Hatoum A. S., Smith D. M., Nichols T.
E., Neta M., Petersen S. E., Gratton C. (2024) Two common and distinct forms of variation in
human functional brain networks Nature Neuroscience 27:1187–1198 https://doi.org/10.1038
/s41593-024-01618-2
Dworkin J. D., Linn K. A., Teich E. G., Zurn P., Shinohara R. T., Bassett D. S. (2020) The extent
and drivers of gender imbalance in neuroscience reference lists Nature Neuroscience
23:918–926 https://doi.org/10.1038/s41593-020-0658-y
Elliott M. L., Knodt A. R., Cooke M., Kim M. J., Melzer T. R., Keenan R., Ireland D., Ramrakha S.,
Poulton R., Caspi A., Moffitt T. E., Hariri A. R. (2019) General functional connectivity: Shared
features of resting-state and task fMRI drive reliable and heritable individual differences
in functional brain networks NeuroImage 189:516–532 https://doi.org/10.1016/j.neuroimage
.2019.01.068
Feilong M., Guntupalli J. S., Haxby J. V. (2021) The neural basis of intelligence in fine-grained
cortical topographies (F. P. de Lange, T. Yeo, J. D. Bijsterbosch, & E. Gordon, Eds.) eLife
10:e64058 https://doi.org/10.7554/eLife.64058


## Page 27

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
27 of 37
Finn E. S., Bandettini P. A. (2021) Movie-watching outperforms rest for functional
connectivity-based prediction of behavior NeuroImage 235:117963 https://doi.org/10.1016/j
.neuroimage.2021.117963
Finn E. S., Corlett P. R., Chen G., Bandettini P. A., Constable T. (2018) Trait paranoia shapes
inter-subject synchrony in brain activity during an ambiguous social narrative Nature
Communications 9 https://doi.org/10.1038/s41467-018-04387-2
Fulvio J. M., Akinnola I., Postle B. R. (2021) Gender (im)balance in citation practices in
cognitive neuroscience Journal of Cognitive Neuroscience 33:3–7 https://doi.org/10.1162/jocn
_a_01643
Ge T., Reuter M., Winkler A. M., Holmes A. J., Lee P. H., Tirrell L. S., Roffman J. L., Buckner R. L.,
Smoller J. W., Sabuncu M. R. (2016) Multidimensional heritability analysis of
neuroanatomical shape Nature Communications 7:13291 https://doi.org/10.1038
/ncomms13291
Glahn D. C., Winkler A. M., Kochunov P., Almasy L., Duggirala R., Carless M. A., Curran J. C.,
Olvera R. L., Laird A. R., Smith S. M., Beckmann C. F., Fox P. T., Blangero J. (2010) Genetic
control over the resting brain Proceedings of the National Academy of Sciences 107:1223–
1228 https://doi.org/10.1073/pnas.0909969107
Gordon E. M., Laumann T. O., Gilmore A. W., Newbold D. J., Greene D. J., Berg J. J., Ortega M.,
Hoyt-Drazen C., Gratton C., Sun H., Hampton J. M., Coalson R. S., Nguyen A. L., McDermott K. B.,
Shimony J. S., Snyder A. Z., Schlaggar B. L., Petersen S. E., Nelson S. M., Dosenbach N. U. F.
(2017) Precision functional mapping of individual human brains Neuron 95:791–807 https:
//doi.org/10.1016/j.neuron.2017.07.011
Gruskin D. C., Patel G. H. (2022) Brain connectivity at rest predicts individual differences in
normative activity during movie watching NeuroImage 253:119100 https://doi.org/10.1016/j
.neuroimage.2022.119100
Gruskin D. C., Rosenberg M. D., Holmes A. J. (2020) Relationships between depressive
symptoms and brain responses during emotional movie viewing emerge in adolescence
NeuroImage 216:116217 https://doi.org/10.1016/j.neuroimage.2019.116217
Guntupalli J. S., Feilong M., Haxby J. (2018) A computational model of shared fine-scale
structure in the human connectome PLOS Computational Biology 14:e1006120 https://doi
.org/10.1371/journal.pcbi.1006120
Hasson U., Yang E., Vallines I., Heeger D. J., Rubin N. (2008) A Hierarchy of Temporal
Receptive Windows in Human Cortex The Journal of Neuroscience 28:2539–2550 https://doi
.org/10.1523/JNEUROSCI.5487-07.2008
Haxby J. V., Guntupalli J. S., Connolly A. C., Halchenko Y. O., Conroy B. R., Gobbini M. I., Hanke
M., Ramadge P. J. (2011) A common, high-dimensional model of the representational space
in human ventral temporal cortex Neuron 72:404–416 https://doi.org/10.1016/j.neuron.2011
.08.026
Haxby J. V., Guntupalli J. S., Nastase S. A., Feilong M. (2020) Hyperalignment: Modeling shared
information encoded in idiosyncratic cortical topographies (C. I. Baker & F. P. de Lange,
Eds.) eLife 9:e56601 https://doi.org/10.7554/eLife.56601


## Page 28

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
28 of 37
Hillman E. M. (2014) Coupling mechanism and significance of the BOLD signal: A status
report Annual review of neuroscience 37:161–181 https://doi.org/10.1146/annurevneuro-071013
-014111
Honey C. J., Thesen T., Donner T. H., Silbert L. J., Carlson C. E., Devinsky O., Doyle W. K., Rubin N.,
Heeger D. J., Hasson U. (2012) Slow Cortical Dynamics and the Accumulation of
Information over Long Timescales Neuron 76:423–434 https://doi.org/10.1016/j.neuron.2012
.08.011
Kauppi J.-P., Jääskeläinen I. P., Sams M., Tohka J. (2010) Inter-subject correlation of brain
hemodynamic responses during watching a movie: Localization in space and frequency
[PMID: 20428497 PMCID: PMC2859808] Frontiers in Neuroinformatics 4:5 https://doi.org/10
.3389/fninf.2010.00005
Kennedy D. P., D’Onofrio B. M., Quinn P. D., Bölte S., Lichtenstein P., Falck-Ytter T. (2017)
Genetic influence on eye movements to complex scenes at short timescales Current
biology 27:3554–3560 https://doi.org/10.1016/j.cub.2017.10.007
Ki J. J., Kelly S. P., Parra L. C. (2016) Attention strongly modulates reliability of neural
responses to naturalistic narrative stimuli The Journal of Neuroscience 36:3092–3101 https://
doi.org/10.1523/JNEUROSCI.2942-15.2016
Kohn A., Coen-Cagli R., Kanitscheider I., Pouget A. (2016) Correlations and neuronal
population information Annual review of neuroscience 39:237–256 https://doi.org/10.1146
/annurev-neuro-070815-013851
Korgaonkar M. S., Ram K., Williams L. M., Gatt J. M., Grieve S. M. (2014) Establishing the
resting state default mode network derived from functional magnetic resonance
imaging tasks as an endophenotype: A twins study Human Brain Mapping 35:3893–
3902 https://doi.org/10.1002/hbm.22446
Maliniak D., Powers R., Walter B. F. (2013) The gender citation gap in international relations
International Organization 67:889–922 https://doi.org/10.1017/S0020818313000209
Marcus D. S., Harwell J., Olsen T., Hodge M., Glasser M. F., Prior F., Jenkinson M., Laumann T.,
Curtiss S. W., Van Essen D. C. (2011) Informatics and data mining tools and strategies for
the human connectome project Frontiers in Neuroinformatics 5:4 https://doi.org/10.3389
/fninf.2011.00004
Miranda-Dominguez O., Feczko E., Grayson D. S., Walum H., Nigg J. T., Fair D. A. (2018)
Heritability of the human connectome: A connectotyping study Network Neuroscience
(Cambridge, Mass.) 2:175–199 https://doi.org/10.1162/netn_a_00029
Mitchell S. M., Lange S., Brus H. (2013) Gendered citation patterns in international relations
journals International Studies Perspectives 14:485–492 https://doi.org/10.1111/insp.12026
Patel G. H., Arkin S. C., Ruiz-Betancourt D. R., Plaza F. I., Mirza S. A., Vieira D. J., Strauss N. E.,
Klim C. C., Sanchez-Peña J. P., Bartel L. P. (2021) Failure to engage the temporoparietal
junction/posterior superior temporal sulcus predicts impaired naturalistic social
cognition in schizophrenia Brain: a journal of neurology 144:1898–1910
Pelt V. S., Boomsma D. I., Fries P. (2012) Magnetoencephalography in twins reveals a strong
genetic determination of the peak frequency of visually induced gamma-band


## Page 29

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
29 of 37
synchronization Journal of Neuroscience 32:3388–3392 https://doi.org/10.1523/JNEUROSCI
.5592-11.2012
Pérez P., Madsen J., Banellis L., Türker B., Raimondo F., Perlbarg V., Valente M., Niérat M.-C.,
Puybasset L., Naccache L., Similowski T., Cruse D., Parra L. C., Sitt J. D. (2021) Conscious
processing of narrative stimuli synchronizes heart rate between individuals Cell Reports
36:109692 https://doi.org/10.1016/j.celrep.2021.109692
Petersen S. E., Seitzman B. A., Nelson S. M., Wig G. S., Gordon E. M. (2024) Principles of cortical
areas and their implications for neuroimaging Neuron 0:0 https://doi.org/10.1016/j.neuron
.2024.05.008
Renvall H., Salmela E., Vihla M., Illman M., Leinonen E., Kere J., Salmelin R. (2012) Genome-wide
linkage analysis of human auditory cortical activation suggests distinct loci on
chromosomes 2, 3, and 8 The Journal of Neuroscience 32:14511–14518 https://doi.org/10.1523
/JNEUROSCI.1483-12.2012
Ricard J. A., Parker T. C., Dhamala E., Kwasa J., Allsop A., Holmes A. J. (2023) Confronting
racially exclusionary practices in the acquisition and analyses of neuroimaging data
Nature Neuroscience 26:4–11 https://doi.org/10.1038/s41593-022-01218-y
Robinson E. C., Jbabdi S., Glasser M. F., Andersson J., Burgess G. C., Harms M. P., Smith S. M.,
Van Essen D. C., Jenkinson M. (2014) MSM: A new flexible framework for multimodal
surface matching NeuroImage 100:414–426 https://doi.org/10.1016/j.neuroimage.2014.05.069
Salmi J., Roine U., Glerean E., Lahnakoski J., Nieminen-von Wendt T., Tani P., Leppämäki S.,
Nummenmaa L., Jääskeläinen I., Carlson S., Rintahaka P., Sams M. (2013) The brains of high
functioning autistic individuals do not synchronize with those of others NeuroImage:
Clinical 3:489–497 https://doi.org/10.1016/j.nicl.2013.10.011
Schaefer A., Kong R., Gordon E. M., Laumann T. O., Zuo X.-N., Holmes A. J., Eickhoff S. B., Yeo B.
T. T. (2018) Local-global parcellation of the human cerebral cortex from intrinsic
functional connectivity mri Cerebral Cortex (New York, N.Y.: 1991) 28:3095–3114 https://doi
.org/10.1093/cercor/bhx179
Schmitt J. E., Neale M. C., Fassassi B., Perez J., Lenroot R. K., Wells E. M., Giedd J. N. (2014) The
dynamic role of genetics on cortical patterning during childhood and adolescence
Proceedings of the National Academy of Sciences 111:6774–6779 https://doi.org/10.1073/pnas
.1311630111
Shinn M., Hu A., Turner L., Noble S., Preller K. H., Ji J. L., Moujaes F., Achard S., Scheinost D.,
Constable R. T., Krystal J. H., Vollenweider F. X., Lee D., Anticevic A., Bullmore E. T., Murray J. D.
(2023) Functional brain networks reflect spatial and temporal autocorrelation Nature
Neuroscience 26:867–878 https://doi.org/10.1038/s41593-023-01299-3
Sinclair B., Hansell N. K., Blokland G. A., Martin N. G., Thompson P. M., Breakspear M., de
Zubicaray G. I., Wright M. J., McMahon K. L. (2015) Heritability of the network architecture of
intrinsic brain functional connectivity NeuroImage 121:243–252 https://doi.org/10.1016/j
.neuroimage.2015.07.048


## Page 30

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
30 of 37
Song H., Finn E. S., Rosenberg M. D. (2021) Neural signatures of attentional engagement
during narratives and its consequences for event memory Proceedings of the National
Academy of Sciences 118:e2021905118 https://doi.org/10.1073/pnas.2021905118
Sydnor V. J., Larsen B., Seidlitz J., Adebimpe A., Alexander-Bloch A. F., Bassett D. S., Bertolero M.
A., Cieslak M., Covitz S., Fan Y., Gur R. E., Gur R. C., Mackey A. P., Moore T. M., Roalf D. R.,
Shinohara R. T., Satterthwaite T. D. (2023) Intrinsic activity development unfolds along a
sensorimotor–association cortical axis in youth [PMID: 36973514] Nature neuroscience
26:638 https://doi.org/10.1038/s41593-023-01282-y
Tu P.-C., Su T.-P., Lin W.-C., Chang W.-C., Bai Y.-M., Li C.-T., Lin F.-H. (2019) Reduced
synchronized brain activity in schizophrenia during viewing of comedy movies Scientific
Reports 9:12738 https://doi.org/10.1038/s41598-019-48957-w
van Baar J. M., Halpern D. J., FeldmanHall O. (2021) Intolerance of uncertainty modulates
brain-to-brain synchrony during politically polarized perception Proceedings of the National
Academy of Sciences 118:e2022491118 https://doi.org/10.1073/pnas.2022491118
van den Heuvel M. P., Hulshoff Pol H. E. (2010) Exploring the brain network: A review on
resting-state fMRI functional connectivity European Neuropsychopharmacology 20:519–
534 https://doi.org/10.1016/j.euroneuro.2010.03.008
Van Essen D. C., Smith S. M., Barch D. M., Behrens T. E., Yacoub E., Ugurbil K. (2013) The WU-
Minn Human Connectome Project: An overview NeuroImage 80:62–79 https://doi.org/10
.1016/j.neuroimage.2013.05.041
Vanderwal T., Eilbott J., Finn E. S., Craddock R. C., Turnbull A., Castellanos F. X. (2017) Individual
differences in functional connectivity during naturalistic viewing conditions NeuroImage
157:521–530 https://doi.org/10.1016/j.neuroimage.2017.06.027
Wang X., Dworkin J. D., Zhou D., Stiso J., Falk E. B., Bassett D. S., Zurn P., Lydon-Staley D. M.
(2021) Gendered citation practices in the field of communication Annals of the International
Communication Association 45:134–153 https://doi.org/10.1080/23808985.2021.1960180
Watanabe T., Rees G., Masuda N. (2019) Atypical intrinsic neural timescale in autism (J. I.
Gold, M. Breakspear, & L. L Gollo, Eds.) eLife 8:e42256 https://doi.org/10.7554/eLife.42256
Wengler K., Goldberg A. T., Chahine G., Horga G. (2020) Distinct hierarchical alterations of
intrinsic neural timescales account for different manifestations of psychosis (M. J. Frank,
C. M. Gillan, & P. R. Corlett, Eds.) eLife 9:e56151 https://doi.org/10.7554/eLife.56151
Xu T., Opitz A., Craddock R. C., Wright M. J., Zuo X.-N., Milham M. P. (2016) Assessing variations
in areal organization for the intrinsic brain: From fingerprints to reliability Cerebral Cortex
26:4192–4211 https://doi.org/10.1093/cercor/bhw241
Yeo T., Krienen F. M., Sepulcre J., Sabuncu M. R., Lashkari D., Hollinshead M., Roffman J. L.,
Smoller J. W., Zöllei L., Polimeni J. R., Fischl B., Liu H., Buckner R. L. (2011) The organization of
the human cerebral cortex estimated by intrinsic functional connectivity Journal of
Neurophysiology 106:1125–1165 https://doi.org/10.1152/jn.00338.2011


## Page 31

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
31 of 37
Yeshurun Y., Swanson S., Simony E., Chen J., Lazaridi C., Honey C. J., Hasson U. (2017) Same
story, different story Psychological Science 28:307–319 https://doi.org/10.1177
/0956797616682029
Zhang J., Zhang S., Qiao J., Wang T., Zeng P. (2023) Similarity and diversity of genetic
architecture for complex traits between East Asian and European populations BMC
Genomics 24:314 https://doi.org/10.1186/s12864-023-09434-x
Zheng R., Bu C., Chen Y., Wei Y., Zhou B., Jiang Y., Zhu C., Wang K., Wang C., Li S., Han S., Zhang
Y., Cheng J. (2024) Decreased intrinsic neural timescale in treatment-naïve adolescent
depression Journal of Affective Disorders 348:389–397 https://doi.org/10.1016/j.jad.2023.12.048
Zhou D., Cornblath E. J., Stiso J., Teich E. G., Dworkin J. D., Blevins A. S., Bassett D. S. (2020)
Gender diversity statement and code notebook v1.0 Zenodo https://doi.org/10.5281
/zenodo.3672110
Author information
David C Gruskin
Medical Scientist Training Program, Columbia University Irving Medical Center, New York,
United States
ORCID iD: 0000-0001-6504-191X
For correspondence: david.gruskin@columbia.edu
Daniel J Vieira
Division of Experimental Therapeutics, New York State Psychiatric Institute, New York,
United States
ORCID iD: 0009-0001-0112-5177
Jessica K Lee
Division of Experimental Therapeutics, New York State Psychiatric Institute, New York,
United States
ORCID iD: 0009-0005-2619-0871
Gaurav H Patel
Division of Experimental Therapeutics, New York State Psychiatric Institute, New York,
United States, Department of Psychiatry, Columbia University Irving Medical Center, New
York, United States
ORCID iD: 0000-0003-0028-2098
Editors
Reviewing Editor
Emma Sprooten
Donders Institute for Brain, Cognition and Behaviour, Nijmegen, Netherlands


## Page 32

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
32 of 37
Senior Editor
Andre Marquand
Radboud University Nijmegen, Nijmegen, Netherlands
Reviewer #1 (Public review):
Summary:
Gruskin and colleagues use twin data from a movie-watching fMRI paradigm to show how
genetic control of cortical function intersects with the processing of naturalistic audiovisual
stimuli. They use hyperalignment to dissect heritability into the components that can be
explained by local differences in cortical-functional topography and those that cannot. They
show that heritability is strongest at slower-evolving neural time scales and is more evident
in functional connectivity estimates than in response time series.
Strengths:
This is a very thorough paper that tackles this question from several different angles. I very
much appreciate the use of hyperalignment to factor out topographic differences, and I found
the relationship between heritability and neural time scales very interesting. The writing is
clear, and the results are compelling.
Weaknesses:
The only "weaknesses" I identified were some points where I think the methods,
interpretation, or visualization could be clarified.
(1) On page 16, the authors compare heritability in functional connectivity (FC) and response
time series, and find that the heritability effect is larger in FC. In general, I agree with your
diagnosis that this is in large part due to the fact that FC captures the covariance structure
across parcels, whereas response time series only diverge in terms of univariate time-point-
by-time-point differences. Another important factor here is that (within-subject) FC can be
driven by intrinsic fluctuations that occur with idiosyncratic timing across subjects and are
unrelated to the stimulus (whereas time-locked metrics like ISC and time-series differences
cannot, by definition). This makes me wonder how this connectivity result would change if
the authors used intersubject functional connectivity (ISFC) analysis to specifically isolate the
stimulus-driven components of functional connectivity (Simony et al., 2016). This, to me,
would provide a closer comparison to the ISC and response time series results, and could
allow the authors to quantify how much of the heritability in FC is intrinsic versus stimulus-
driven. I'm not asking that the authors actually perform this analysis, as I don't think it's
critical for the message of the manuscript, but it could be an interesting future direction. As
the authors discuss on page 17, I also suspect there's something fundamentally shared
between response time series and connectivity as they relate to functional topography (Busch
et al., 2021) that drives part of the heritability effect.
(2) The observation that regions with intermediate ISC have the largest differences between
MZ, DZ, and UR is very interesting, but it's kind of hard to see in Figure 1B. Is there any other
way to plot this that might make the effect more obvious? For example, I could imagine three
scatter plots where the x- and y-axes are, e.g., MZ ISC and UR ISC, and each data point is a
parcel. In this kind of plot, I would expect to see the middle values lifted visibly off the
diagonal/unity line toward MZ. The authors could even color the data points according to
networks, like in Figure 3C. (They also might not need to scale the ISC axis all the way to r = 1,
which would make the differences more visible.)
(3) On page 9, if I understand correctly, the authors regress the vector of ISC values across
parcels out of the vector of heritability values across parcels, and then plot the residual
heritability values. Do they center the heritability values (or include some kind of intercept)


## Page 33

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
33 of 37
in the process? I'm trying to understand why the heritability values go from all positive
(Figure 2A) to roughly balanced between positive and negative (Figure 2B). Important
question for me: How should we interpret negative values in this plot? Can the authors
explain this explicitly in the text? (I also wonder if there's a more intuitive way to control for
ISC. For example, instead of regressing out ISC at the parcel/map level, could they go into a
single parcel and then regress the subject-level pairwise ISC values out when computing the
heritability score?).
(4) On page 4 (line 155), the authors say "we shuffled dyad labels"- is this equivalent to
shuffling rows and columns of the pairwise subject-by-subject matrix combined across
groups? I'm trying to make sure their approach here is consistent with recommendations by
Chen et al., 2016. Is this the same kind of shuffling used for the kinship matrix mentioned in
line 189?
(5) I found panel A in Figure 4 to be a little bit misleading because their parcel-wise approach
to hyperalignment won't actually resolve topographic idiosyncrasies across a large cortical
distance like what's depicted in the illustration (at the scale of the parcels they are
performing hyperalignment within). Maybe just move the green and purple brain areas a bit
closer to each other so they could feasibly be "aligned" within a large parcel. Worth keeping
in mind when writing that hyperalignment is also not actually going to yield a one-to-one
mapping of functionally homologous voxels across individuals: it's effectively going to model
any given voxel time series as a linear combination of time series across other voxels in the
parcel.
(6) I believe the subjects watched all different movies across the two days, however, for a
moment I was wondering "are Day 1 and Day 2 repetitions of the same movies?" Given that
Day 1 and Day 2 are an organizational feature of several figures, it might be worth making
this very explicit in the Methods and reminding the reader in the Results section.
References:
Busch, E. L., Slipski, L., Feilong, M., Guntupalli, J. S., di Oleggio Castello, M. V., Huckins, J. F.,
Nastase, S. A., Gobbini, M. I., Wager, T. D., & Haxby, J. V. (2021). Hybrid hyperalignment: a
single high-dimensional model of shared information embedded in cortical patterns of
response and functional connectivity. NeuroImage, 233, 117975. https://doi.org/10.1016/j
.neuroimage.2021.117975
Chen, G., Shin, Y. W., Taylor, P. A., Glen, D. R., Reynolds, R. C., Israel, R. B., & Cox, R. W. (2016).
Untangling the relatedness among correlations, part I: nonparametric approaches to inter-
subject correlation analysis at the group level. NeuroImage, 142, 248-259. https://doi.org/10
.1016/j.neuroimage.2016.05.023
Simony, E., Honey, C. J., Chen, J., Lositsky, O., Yeshurun, Y., Wiesel, A., & Hasson, U. (2016).
Dynamic reconfiguration of the default mode network during narrative comprehension.
Nature Communications, 7, 12141. https://doi.org/10.1038/ncomms12141
https://doi.org/10.7554/eLife.106081.1.sa2
Reviewer #2 (Public review):
Summary:
The authors attempt to estimate the heritability of brain activity evoked from a naturalistic
fMRI paradigm. No new data were collected; the authors analyzed the publicly available and
well-known data from the Human Connectome Project. The paper has 3 main pieces, as
described in the Abstract:


## Page 34

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
34 of 37
(1) Heritability of movie-evoked brain activity and connectivity patterns across the cortex.
(2) Decomposition of this heritability into genetic similarity in "where" vs. "how" sensory
information is processed.
(3) Heritability of brain activity patterns, as partially explained by the heritability of neural
timescales.
Strengths:
The authors investigate a very relevant topic that concerns how heritable patterns of brain
activity among individuals subjected to the same kind of naturalistic stimulation are. Notably,
the authors complement their analysis of movie-watching data with resting-state data.
Weaknesses:
The paper has numerous problems, most of which stem from the statistical analyses. I also
note the lack of mapping between the subsections within the Methods section and the
subsections within the Results section. We can only assess results after understanding and
confirming the methods are valid; here, however, Methods and Results, as written, are not
aligned, so we can't always be sure which results are coming from which analysis.
(A) Intersubject correlation (ISC) (section that starts from line 143): "We used non-parametric
permutation testing to quantify average differences in ISC for each parcel in the Schaefer 400
atlas for each day of data collection across three groups: MZ dyads, DZ dyads, and unrelated
(UR) dyads, where all UR dyads were matched for gender and age in years." ... "some
participants contributed to ISC values for multiple dyads (thus violating independence
assumptions)"
This is an indirect attempt to demonstrate heritability. And it's also incorrect since, as the
authors themselves point out, some subjects contribute to more than one dyad.
Permutation tests don't quantify "average differences", they provide a measure of evidence
about whether differences observed are sufficient to reject a hypothesis of no difference.
Matching subjects is also incorrect as it artificially alters the sample; covarying for age and
sex, as done in standard analyses of heritability, would have been appropriate.
It isn't clear why the authors went through the trouble of implementing their own non-
parametric test if HCP recommends using PALM, which already contains the validated and
documented methods for permutation tests developed precisely for HCP data.
The results from this analysis, in their current form, are likely incorrect.
(B) Functional connectivity (FC) (section that starts from line 159): Here the authors compute
two 400x400 FC matrix for each subject, one for rest, one for movie-watching, then correlate
the correlations within each dyad, then compared the average correlation of correlations for
MZ, DZ, and UR. In addition to the same problems as the previous analysis, here it is not clear
what is meant by "averaging correlations [...] within a network combination". What is a
"network combination"? Further, to average correlations, they need to be r-to-z transformed
first. As with the above, the results from this analysis in its current form are likely incorrect.
(C) ISC and FC profile heritability analyses (section that starts from line 175): Here, the
authors use first a valid method remarkably similar to the old Haseman-Elston approach to
compute heritability, complemented by a permutation test. That is fine. But then they proceed
with two novel, ill-described, and likely invalid methods to (1) "compare the heritability of
movie and rest FC profiles" and (2) to "determine the sample size necessary for stable
multidimensional heritability results". For (1), they permute, seemingly under the alternative,


## Page 35

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
35 of 37
rest and movie-watching timeseries, and (2), by dropping subjects and estimating changes in
the distribution.
The (1) might be correct, but there are items that are not clearly described, so the reader
cannot be sure of what was done. What are the "153 unique network combinations"? Why do
the authors separate by day here, whereas the previous analyses concatenated both days?
Were the correlations r-to-z transformed before averaging?
The (2) is also not well described, and in any case, power can be computed analytically; it isn't
clear why the authors needed to resort to this ad hoc approach, the validity of which is
unknown. If the issue is the possibility that the multidimensional phenotypic correlation
matrix is rank-deficient, it suffices that there are more independent measurements per
subject than the number of subjects.
(D) Frequency-dependent ISC heritability analysis (from line 216): Here, the authors
decompose the timeseries into frequency bands, then repeat earlier analyses, thus bringing
here the same earlier problems and questions of non-exchangability in the permutations
given the dyads pattern, r-z transforms, and sex/age covariates.
(E) FC strength heritability analysis (from line 236): Here, the authors use the univariate FC to
compute heritability using valid and well-established methods as implemented in SOLAR.
There is no "linkage" being done here (thus, the statement in line 238 is incorrect in this
application. SOLAR already produces SEs, so it's unclear why the authors went out of their
way to obtain jackknife estimates. If the issue is non-normality, I note that the assumption of
normality is present already at the stage in which parameters themselves are estimated, not
just the standard errors; for non-normal data, a rank-based inverse-normal transformation
could have been used. Moreover, typically, r-to-z transformed values tend to be fairly
normally distributed. So, while the heritabilities might be correct, the standard errors may
not be (the authors don't demonstrate that their jackknife SE estimator is valid). The
comparison of h2 between dyads raises the same questions about permutations, age/sex
covariates, and r-z transforms as above.
(F) Hyperalignment (from line 245): It isn't clear at this point in the manuscript in what way
hyperalignment would help to decompose heritability in "where vs. how" (from the Abstract).
That information and references are only described much later, from around line 459. The
description itself provides no references, and one cannot even try to reproduce what is
described here in the Methods section. Regardless, it isn't entirely clear why this analysis was
done: by matching functional areas, all heritabilities are going to be reduced because there
will be less variance between subjects. Perhaps studying the parameters that drive the
alignment (akin to what is done in tensor-based and deformation-based morphometry) could
have been more informative. Plus, the alignment process itself may introduce errors, which
could also reduce heritability. This could be an alternative explanation for the reduced
heritability after hyperalignment and should be discussed. An investigation of hyperaligment
parameters, their heritability, and their co-heritability with the BOLD-phenotypes can inform
on this.
(G) Relationships between parcel area and heritability (from line 270): As under F), how
much the results are distorted likely depends on the accuracy of the alignment, and the error
variance (vs heritable variance) introduced by this.
(H) Neural timescale analyses (from line 280): Here, a valid phenotype (NT) is assessed with
statistical methods with the same limitations as those previously (exchangability of dyads,
age/sex covariates, and r-z transforms). NT values are combined across space and used as
covariates in "some multivariate analyses". As a reader, I really wanted to see the results
related to NT, something as simple as its heritability, but these aren't clearly shown, only
differences between types of dyads.


## Page 36

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
36 of 37
(I) Significance testing for autocorrelated brain maps and FC matrices (from line 310): Here,
the authors suddenly bring up something entirely different: reliability of heritability maps,
and then never return to the topic of reliability again. As a reader, I find this confusing. In
any case, analyses with BrainSMASH with well-behaved, normally distributed data are ok.
Whether their data is well behaved or whether they ensured that the data would be well
behaved so that BrainSMASH is valid is not described. As to why Spearman correlations are
needed here, Mantel tests, or whether the 1000 "surrogate" maps are valid realizations of the
data under the null, remains undemonstrated.
(J) Global signal was removed, and the authors do not acknowledge that this could be a
limitation in their analyses, nor offer a side analysis in which the global signal is preserved.
(K) FDR is used to control the error rate, but in many cases, as it's applied to multiple sets of p-
values, the amount of false discoveries is only controlled across all tests, but not within each
set. The number of errors within any set remains unknown.
(L) Generally, when studying the heritability of a trait, the trait must be defined first. Here,
multiple traits are investigated, but are never rigorously defined. Worse, the trait being
analyzed changes at every turn.
https://doi.org/10.7554/eLife.106081.1.sa1
Reviewer #3 (Public review):
Strengths:
It's sort of novel to study the heritability of movie-watching fMRI data. The methodology the
authors used in the paper is also supportive of their findings. Figures are nicely organized
and plotted. They finally found that sensory processing in the human brain is under genetic
control over stable aspects of brain function (here referring to neural timescale and resting
state connectivity).
Weaknesses:
What I am worried about most is the sample size and interpretation of heritability.
(1) Figure 1. I assumed that the authors just calculated the ISC within each group (MZ, DZ, and
UR). Of course, you can get different variations between each group. Therefore, there is
heritability. Why not calculate ISC across the whole sample, then separate MZ, DZ, and UR?
(2) Heritability scores in the paper are sort of small. If the sample size is small, please
consider p-values, which will tell more about the trustworthiness of your heritability.
(3) I don't understand the high-frequency signals in fMRI data. It's always regarded as noise,
the band 1 here in particular.
(4) The statement "we show that the heritability of brain activity patterns can be partially
explained by the heritability of the neural timescale" should come from Figure 5. However,
after controlling for NT, the heritability decreased max. 0.025 in temporal areas. I am not sure
this change supports the statement. If the visual cortex is outlined, and combining ISC
changes in the visual cortex, I think this would somehow be answered. Instead of delta h2,
adding a new model h2 would be obvious to the readers.
(5) Figures 7 and 8, when getting the difference of heritability, please also consider the
standard errors of the heritability estimates. Then you can compare across networks/regions.


## Page 37

David C Gruskin et al., 2025 eLife. https://doi.org/10.7554/eLife.106081.1
37 of 37
(6) I think movie VS resting state is a really important result in this paper. However, there is
almost no discussion. Discussing this part would be more beneficial for understanding the
genetic control over the neuron arousal and excitation circuits.
https://doi.org/10.7554/eLife.106081.1.sa0


