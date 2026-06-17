bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## Visual Emotion Perception in a Deep Neural Network Model with Both Bottom-Up and Top-Down Connections 

Peng Liu[1] , Ke Bo[2] , Yujun Chen[1] , Andreas Keil[4] , Mingzhou Ding[1] *, Ruogu Fang[1,3] * 

1J. Crayton Pruitt Family Department of Biomedical Engineering, Herbert Wertheim College of Engineering, University of Florida, Gainesville, Florida, USA 

2Department of Psychological and Brain Sciences, Dartmouth College, Hanover, New Hampshire, USA 

3Center for Cognitive Aging and Memory, McKnight Brain Institute, University of Florida, Gainesville, Florida, USA 

4Department of Psychology and Center for the Study of Emotion & Attention, University of Florida, Gainesville, Florida, USA 

*mding@bme.ufl.edu (MD) ruogu.fang@bme.ufl.edu (RF) 

## Abstract 

Emotion reshapes perception by modulating sensory processing through top-down feedback—a process referred to as emotional perception. The computational mechanisms by which distinct affective signals influence visual representations however remain poorly understood.  Here, we use a deep neural network to simulate this process and test mechanistic hypotheses about how top-down feedback guides emotional peception. Most existing models treat the perception of emotional content as a static, feedforward task, overlooking the dynamic interplay between internal states, external goals, and sensory input that characterizes affective perception in the brain. We introduce EmoFB, a biologically inspired model that integrates an affective system with a visual processing hierarchy through two functionally distinct feedback signals: intrinsic feedback, arising from the model’s own affective appraisal of perceptual input, and external steering, conveying contextual priors such as task expectations or target categories. We evaluated EmoFB on three tasks varying in perceptual ambiguity (Single Image, Side-by-Side, and Overlay). External steering exerted the strongest influence, not only improving recognition under challenging conditions but also restructuring internal representations by sharpening categoryspecific clustering in feature space. Crucially, top-down feedback increased brain–model representational similarity, strengthening alignment with human fMRI responses across early visual cortex, ventral visual areas, and the amygdala. EmoFB provides a computational framework for testing neurocognitive theories of emotion appraisal and top-down feedback modulation. It bridges affective neuroscience and artificial intelligence, offering mechanistic insight into how emotional signals shape perception in both brains and machines. 

**Keywords:** Emotion perception, top-down feedback, emotion modulation, deep neural networks, NeuroAI, visual cognition, fMRI, amygdala 

1 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **Introduction** 

Emotion fundamentally shapes how we perceive and interpret the world around us. The brain has evolved sophisticated mechanisms to process the emotional information embedded in the sensory input. In vision, rather than proceeding as a purely bottom-up process, visual perception of emotion is dynamically modulated by internal emotional states and externally generated goals (Vuilleumier 2005; Pourtois et al. 2013). This flexibility enables humans to anticipate and prioritize emotionally salient information, disambiguate noisy inputs, and adaptively respond to complex visual scenes (Pessoa and Adolphs 2010; L. f. Barrett and Bar 2009). Anatomically, this operation is supported by recurrent connections between anterior emotion-modulating regions, such as the amygdala and ventromedial prefrontal cortex (vmPFC), and various hierarchical levels of the visual system (Cardinal et al. 2002; Amaral et al. 2003; Catani et al. 2003; Vuilleumier 2005; Pessoa 2009). Functionally, these bidirectional pathways underlie such distinct forms of emotion modulation as emotion expectation and emotion appraisal (Arnold 1960; C. A. Smith and Ellsworth 1985; C. A. Smith and Lazarus 1993; Sander et al. 2005; Cunningham and Brosch 2012; Moors et al. 2013; Yeo and Ong 2024). Impairments of these mechanisms are characteristic of many psychiatric disorders, including depression and schizophrenia. Thus, understanding recurrent processing in the visual-emotion circuit has both basic science and clinical significance. 

Computational modeling has always played an active role in our pursuit to understand visual emotion processing. Recent advances in AI-inspired computational models are taking the field in a new and promising direction. However, the current deep learning models of emotion inference, though effective in static visual classification, rely on predominantly feedforward architectures (Krizhevsky et al. 2012; LeCun et al. 2015; Simonyan and Zisserman 2015; He et al. 2016; Kragel et al. 2019). They treat emotional perception as a direct mapping from image features to affective categories, overlooking the recursive, context- and goal-oriented dependent aspects of emotion perception (L. F. Barrett and Simmons 2015; Pei et al. 2024; Maniquet et al. 2024). As a result, they are not able to capture phenomena such as emotion anticipation and emotion regulation (Cunningham and Brosch 2012; R. Smith and Lane 2015). Bridging this gap calls for novel architectures that incorporate feedback and top-down mechanisms that enable context and internal state dynamics to better approximate the brain’s mechanisms for affective perception. 

Recent NeuroAI work in the non-emotion domain has taken steps in this direction. For example, drawing inspiration from bidirectional cortico-cortical connections in the brain, Konkle and Alvarez (2023b) proposed a deep neural network architecture that incorporates long-range modulatory feedback connections to examine the influence of top-down cognitive steering on visual object recognition. Feedback pathways, along which topdown signals travel from high-level areas to early visual areas (Fişek et al. 2023; Gilbert and Li 2013), enable higher-level representations or external goals to dynamically influence lower-layer activations during recurrent inference (Lamme and Roelfsema 2000; Roelfsema and de Lange 2016). By integrating both internally generated and externally guided steering signals, architectures with feedback properties improve recognition performance for natural images, especially in ambiguous and target–distractor conditions, demonstrating the important role of feedback in solving the object recognition problem under environmental uncertainty. However, these types of models remain restricted to feedback within the visual hierarchy and do not address interactions between the visual and affective systems, which, as discussed earlier, are critical for visual emotion perception (Pessoa and Adolphs 2010; Sander et al. 2005; Pourtois et al. 2013). 

In the present work, we attempted to address this problem by introducing EmoFB, a biologically inspired deep neural network model of human emotion perception. EmoFB consists of a visual system module and an affective system module, and the two modules interact bidirectionally. EmoFB supports two functionally distinct feedback routes: intrinsic feedback, arising from internal affective appraisals based on the model’s own perceptual representations, and external steering, which reflects broal contextual priors such as those derived from prior information or emotional anticipation. These higher-level signals are projected in a top-down fashion from the affective module, e.g., the amygdala–prefrontal system, back into the convolutional layers within the visual module recursively, forming a hierarchical cascade of modulatory signals that influence sensory processing. We evaluated EmoFB across multiple visual emotional perception tasks with varying levels of uncertainty and stimulus degradation, and assessed the underlying neural mechanisms using representational 

2 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

geometry. In addition, fMRI data recorded from participants viewing affective pictures were analyzed and compared with the deep neural network model to examine whether the introduction of feedback connections and bidirectional interactions helps to increase model-brain alignment. 

## **Results** 

**==> picture [325 x 299] intentionally omitted <==**

**----- Start of picture text -----**<br>
A Feedback<br>Affective<br>system<br>Visual Input Visual Encoding Emotion Recognition<br>B<br>Frozen weights Trainable weights<br>FC8 Emotion recognition<br>FC9<br>amusement<br>FC10 anger<br>awe<br>contentment<br>disgust<br>8 excitement<br>fear<br>1000 sadness<br>4096<br>Visual system  Affective system<br>C<br>Visual system<br>**----- End of picture text -----**<br>


**==> picture [321 x 129] intentionally omitted <==**

**Fig. 1 | Architecture and training dynamics of the EmoFB network** . **A** _**.**_ The EmoFB model consists of two modules: a visual system module and an affective system module. The schematic illustrates that in addition to the conventional feedforward pathway, thee is a reentrant feedback pathway, allowing the modulation of the visual system by the affective system. **B.** Detailed connectivity within the EmoFB model. In addition to the layer-to-layer feedforward connection, feedback connections from FC9→Conv5 and Conv4→Conv2 are included, as well as an additional feedforward connection from Conv5→FC8. **C.** The model was trained to recognize the discrete emotion portrayed in the input image. Model performance as a function of learning: Top-1 accuracy over epochs for three model variants: full model with emotionrelated feedback (black), no emotion-related feedback (gray solid), and no feedback (gray dashed). Models with full emotion feedback consistently outperform the others throughout training although the performance difference is quite modest. Shaded regions represent ±SEM (standard error of the mean) across 10 independently initialized EmoFB networks. FC: fully connected; Conv: convolutional. 

3 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **The EmoFB network model: Architecture, training, and performance** 

Prior deep neural network models of emotion perception contain only feedforward connections linking visual input to emotion categorization. In the biological brain, it is well-established that anterior emotion-sensitive brain areas both receive input from the visual system and send top-down signals to modulate visual processing (Vuilleumier 2005; L. f. Barrett and Bar 2009; Pessoa and Adolphs 2010). The EmoFB network, shown in Fig. 1A, builds on our previous feedforward Visual Cortex Amygdala (VCA) model (P. Liu et al. 2025), which demonstrated the effectiveness of coupling a visual system module with an affective system module. EmoFB extends this framework by connecting the two modules reciprocally with both feedforward and feedback connections. Specifically, in our model, the visual system module is based on a deep convolutional neural network (AlexNet) pretrained on recognizing natural images (Krizhevsky et al. 2012). It has been shown that the rich hierarchical representations of visual input in the AlexNet architecture parallel those of the human brain (Agrawal et al. 2020). For emotion processing and recognition, we modified the network by replacing its final object classification layer (1000 units) with a three-layered fully connected affective system module, which was then trained to recognize 8 discrete categories of emotion (Yang et al. 2023a). 

As shown in Fig. 1B, in addition to hierarchically organized feedforward pathways, we added another feedforward connection (green line) from Conv5 to FC8 to transmit relatively less processed visual features into the affective system. This connection, after network training for visual object recognition, was fixed during emotion recognition training to preserve the integrity of bottom-up visual features while allowing us to isolate the effects of feedback. To integrate top-down modulation into the predominantly feedforward architecture, we added two types of feedback connections: (1) fixed connections within the visual system (gray arrows, e.g., Conv5→Conv2), whose weights were trained during visual object recognition and then held frozen during emotion recognition training, and (2) trainable connections from the affective system to the visual system (orange arrows, e.g., FC9→Conv5). The trainable feedback connections allow the affective system to learn to dynamically modulate visual representations based on high-level emotion recognition goals. 

Training was carried out in two phases. The network was first trained on object recognition to establish stable visual representations. It was then trained on emotion recognition, during which the affective system module and its top-down feedback connections learned to modulate visual representations based on emotion classification demands. During the object recognition training phase, the visual system module, including hierarchically organized feedforward pathways and local feedback connections within the visual hierarchy, was optimized using a standard supervised learning objective. After this phase, all visual system module’s weights, including the Conv5→FC8 feedforward connection transmitting intermediate visual features to the affective system module, were frozen. Emotion recognition training was then performed in a supervised fashion to classify images into one of eight emotion categories: amusement, anger, awe, contentment, disgust, excitement, fear, and sadness (Yang et al. 2023a). During this phase, learning was restricted to the affective system module and the top-down feedback connections from the affective system module to the visual system module, allowing emotion-driven modulation of visual representations while preserving the integrity of bottom-up visual features. Two types of feedback are implemented in the EmoFB network. The first is intrinsic feedback, where the feedback signal is derived internally from the network itself—for example, from the activation of a deeper layer (e.g., FC9) in response to the current input stimulus (as shown in Fig. 1B). The second is external steering feedback, where the top-down modulation is guided by a category-level template signal (detailed in the next section). We first present results from intrinsic feedback below, and then examine the effects of external steering feedback. 

As shown in Fig. 1C, networks equipped with top-down emotion-modulating feedback achieved consistently higher Top-1 accuracy throughout training compared to models with no feedback or with only objectrecognition related feedback connections although the improvement is quite modest. The model with only object-recognition related feedback connections (gray solid line) performed better than the pure feedforward, no-feedback model (gray dashed line), indicating partial benefits from the local feedback within the visual system. Shaded regions denote ±SEM across 10 independently trained models (i.e., from 10 different random initializations), confirming the reliability of performance improvements driven by emotion-based feedback (see Method for more details). 

4 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **A** 

**==> picture [442 x 359] intentionally omitted <==**

**----- Start of picture text -----**<br>
External Steering<br>Affective<br>system<br>EmoFB network<br>External<br>Steering Signal<br>FC9<br>Visual system<br>…<br>Visual system<br>**----- End of picture text -----**<br>


Images in the same emotion Layer feature extraction Mean features category (e.g., excitement) 

## **B** 

**==> picture [443 x 282] intentionally omitted <==**

**----- Start of picture text -----**<br>
External Steering<br>Task 1<br>Single Image<br>Emotion Recognition<br>Task 2<br>Side-by-side Image<br>( target alongside distractor )<br>Task 3<br>EmoFB<br>Overlay Image<br>( target-distractor overlay )<br>**----- End of picture text -----**<br>


5 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

**Fig. 2 | Model performance evaluation paradigm with external steering. A** _._ Schematic of the EmoFB network with external steering. The external steering signal is constructed by averaging response patterns in layer FC9 (penultimate layer) evoked by images from the same emotion category as the visual input. This steering signal is fed back to the visual system module to modulate visual feature representations via top-down feedback. **B** _._ The network’s performance is tested on three input formats—single image (target only), side-by-side image (target + distractor), and overlay image (target-distractor superposition)—to evaluate emotion recognition under varying levels of visual ambiguity. Example images shown are from the EmoSet dataset(Yang et al. 2023b), a publicly available large-scale visual emotion dataset. 

## **Top-down goal-oriented steering: Procedure and performance** 

As introduced above, the second type of feedback in EmoFB is external steering, where top-down modulation is guided by a template-like signal. For the task of recognizing whether a visual stimulus belongs to a specific emotion category, the steering signal is computed by averaging the FC9 activations across all images from the same emotion category in a held-out validation set (Fig. 2A). This averaged feature vector serves as a prototype representation of the target emotion, or a “template” (Duncan and Humphreys 1989; Desimone and Duncan 1995), and is injected into the model’s early layers to bias its visual processing. 

We tested how this external steering signal influences the network’s emotion recognition performance across three tasks of increasing visual complexity: (1) single image, where only the target image is shown; (2) sideby-side image, where the target is presented next to a distractor; and (3) overlay image, where the target and the distractor are fused into a single composite image (Fig. 2B). By applying external steering in each condition, we evaluate whether category-level top-down steering feedback enhances emotion recognition accuracy, even under strong distracting influence. 

To evaluate the role of top-down modulation during recursive inference, the model performed up to five sequential feedforward-feedback passes (Fig. 3A), mimicking the brain’s recurrent computation between lower and higher level brain areas (Lamme and Roelfsema 2000; Gilbert and Li 2013). In the first pass, the network processes the visual input without top-down steering. In subsequent passes, feedback signals derived from the previous pass (intrinsic feedback) or from the template are applied to modulate target layers, progressively refining the network’s internal representational state. Each pass, therefore, builds on the prior one, allowing feedback to iteratively shape the representation before the final emotion recognition output. 

Across all three tasks, top-down steering consistently outperformed intrinsic feedback (Fig. 3B, left). In the most challenging experimental condition, in which the target image and the distractor image are superimposed, intrinsic feedback plateaued below 40% even after four modulation passes, whereas top-down steering drove performance above 80% after a single pass and over 90% at its peak performance. This highlights the effectiveness of top-down steering, which provides a category-prototype prior that helps disambiguate complex inputs. In addition, the magnitude of improvement scaled with task difficulty. For example, in the single-image task (low ambiguity), external steering improved accuracy by ~20% over intrinsic feedback; in the side-by-side condition (moderate ambiguity), the improvement widened to over 65%; and in the overlay condition (high ambiguity), accuracy jumped from ~27% under intrinsic feedback to ~92% with external steering. 

6 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

**==> picture [398 x 536] intentionally omitted <==**

**----- Start of picture text -----**<br>
A<br>Visual Input EmoFB<br>1 [st] Feedforward Pass Apply Feedback<br>no steering modulation Each feedforward pass produces a<br>State1 network state in which source<br>2 [nd] Feedforward Pass layers store their activations,<br>making them available for<br>1 [st] steering modulation modulation of their respective<br>State2 target layers in the next<br>feedforward pass.<br>N [th] Feedforward Pass<br>Emotion Recognition<br>(N-1) [th] steering modulation<br>Staten<br>B Task1: Single image<br>Task2: Side-by-side image<br>Task3: Overlay image<br>( No. modulation pass = No. feedforward pass -1 )<br>… …<br>**----- End of picture text -----**<br>


**Fig. 3 | Model evaluation procedure and performance. A.** Schematic of the behavioral testing algorithm. The EmoFB model performs multiple feedforward passes, with steering modulation (intrinsic or external) introduced after the first pass. Each feedforward pass generates a network state that modulates the next pass, enabling recurrent top-down influence. **B.** Top-1 emotion recognition accuracy across the three tasks. Left panels: Accuracy comparisons between intrinsic feedback and external steering across increasing numbers of modulation passes. Right panels: Accuracy as a function of steering tuning strength. Each bar reflects the mean ± standard deviation across 10 independently trained models initialized with random weights. Statistical significance was assessed using Welch’s t-test (two-sided, unequal variances) and ANOVA followed by post hoc tests.  (***p < .001, **p < .01, *p < .05). 

7 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

Interestingly, with external steering applied, recognition performance saturated after three feedforward passes (two modulation passes), with little or no gain from additional iterations. At this point, accuracy converged across tasks, 91% for side-by-side and 94% for overlay images, closely matching the 96% achieved in the singleimage normal (ceiling-level) condition. This plateau suggests that the network rapidly settles into a stable representational state once feedback has reorganized the pattern based on early visual activations. A similar pattern is seen in biological vision, where (Lamme and Roelfsema 2000) noted that the feedforward sweep through the visual hierarchy is completed within ~100 ms, after which recurrent feedback operates within a limited window to stabilize perception. Moreover, (Wyatte et al. 2012) showed that feedback strengthens degraded inputs until a stable state is reached, with further cycles offering little additional benefit. Thus, topdown goal-oriented steering functions as a rapid refinement mechanism, yielding most improvements in the first few iterations. These findings show that external steering feedback not only improves recognition when inputs are ambiguous but can also restore degraded perception in the distractors to the normal levels, paralleling the role of recurrent feedback in the brain in resolving uncertainty and stabilizing perception. 

As discussed above, top-down steering based on category specific priors showed its greatest benefit under distracting conditions, a pattern that can be seen in biological vision. When sensory evidence is weak or uncertain, top-down signals from prefrontal and limbic regions shape perception by relying on prior expectations to resolve ambiguity (Summerfield and Egner 2009; Panichello and Buschman 2021). EmoFB captures the same principle. When input is clear, feedback adds only minor improvements, but when input is ambiguous, it becomes essential, adjusting internal representations toward the target or expected category, reducing the impact of distractors, and restoring recognition accuracy **.** In this way, the model offers a mechanistic account of how the brain relies on feedback most strongly when sensory evidence is unreliable, helping to stabilize perception in uncertain environments. 

We further tested how top-down steering strength affected performance (Fig. 3B, right), mimicking how the brain regulates the gain of top-down signals to balance stability and flexibility (Grossberg 1980; Friston 2005). Accuracy improved as tuning strength increased from 0, reaching its best around ~1.5, but declined when the strength was pushed further. This shows that top-down steering works best within an optimal range of feedback strength, where both too little or too much lead to suboptimal performance. This inverted-U pattern is similar to the Yerkes–Dodson law observed in biological systems (Yerkes and Dodson 1908), which showed that there is an optimal range of arousal that supports the best performance; very low or very high arousal both lead to degraded performance. Later studies extended this idea to cognitive control, showing that neuromodulators such as norepinephrine and dopamine are most effective at intermediate levels, with disrupted performance resulting when the levels are too low or too high (Grossberg 1980; Aston-Jones et al. 1999; Aston-Jones and Cohen 2005; Cools and D’Esposito 2011). At the systems level, (Reynolds and Heeger 2009) found that the effect of attention depends on how strongly neurons are already responding. Attention has the largest impact at medium stimulus contrasts, when responses are most flexible, but little effect once responses saturate at high contrast. This supports a general rule that top-down signals are most effective within a limited range. In line with these findings, our results show that feedback in EmoFB is most helpful at moderate tuning strength, while weaker or stronger signals reduce accuracy. 

We reiterate that all results above are averaged over 10 independently initialized models, which enables significance testing using repeated-measures ANOVA, followed by post hoc comparisons. Together, the findings highlight that both the source (intrinsic vs. external) and the strength of top-down feedback are key determinants of emotion recognition. Notably, external steering allows the model to achieve near-ceiling level accuracy even under highly ambiguous conditions, paralleling the role of recurrent feedback in biological vision in resolving uncertainty and stabilizing perception. 

8 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **A** 

**==> picture [11 x 11] intentionally omitted <==**

**----- Start of picture text -----**<br>
B<br>**----- End of picture text -----**<br>


**==> picture [167 x 147] intentionally omitted <==**

**==> picture [238 x 125] intentionally omitted <==**

**----- Start of picture text -----**<br>
Hypothesis :<br>𝑆𝑖𝑚𝑖𝑙𝑎𝑟𝑖𝑡𝑦 (𝐸𝑅𝑆𝑀, 𝑇𝑅𝑆𝑀)  ><br>𝑆𝑖𝑚𝑖𝑙𝑎𝑟𝑖𝑡𝑦 (𝐼𝑅𝑆𝑀, 𝑇𝑅𝑆𝑀)<br>where  𝑇𝑅𝑆𝑀 is the theoretical RSM; IRSM<br>and ERSM  are the DNN layer  RSM derived<br>from intrinsic feedback and external<br>steering, respectively.<br>**----- End of picture text -----**<br>


## Task1: Single image 

Task2: Side-by-side image 

**==> picture [445 x 188] intentionally omitted <==**

**----- Start of picture text -----**<br>
Task3: Overlay image<br>**----- End of picture text -----**<br>


9 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

**Fig. 4 | Neural representational geometry. A.** Theoretical representational similarity matrix (TRSM) constructed based on categorical identity, where each image shares maximum similarity with others from the same emotion category (diagonal blocks). This matrix serves as a hypothesis-driven benchmark for evaluating model representations. **B.** Layerwise representational similarity between the model’s RSMs and the theoretical RSM across three tasks: single image (top), side-by-side image (middle), and overlay image (bottom). Pearson correlation coefficients were computed between the theoretical RSM and the model-derived RSMs from each layer under intrinsic feedback (blue) and external steering (orange). Bars reflect the mean ± standard deviation across 10 independently trained models. External steering consistently enhances representational alignment with the theoretical structure, particularly in deeper layers (FC6–FC9) and under increased visual ambiguity. Statistical significance was assessed using Welch’s t-test (two-sided, unequal variances); asterisks indicate significance levels (***p < .001, **p < .01, *p < .05). 

## **Neural mechanisms revealed by representational geometry** 

What are the neural mechanisms underlying the improved performance by top-down steering? To assess how top-down modulation shapes the internal structure of visual representations, we compared the model’s layerwise representational similarity matrices (RSMs) with a theoretical RSM (TRSM) that encodes idealized category structure (Fig. 4A). In this theoretical RSM, images from the same emotion category are maximally similar (i.e., similarity=1), whereas images from different emotion categories are maximally dissimilar (i.e., similarity=0), resulting in a block-diagonal pattern. While this formulation does not capture graded similarities between different emotion categories, it provides a clear normative reference for evaluating the extent to which top-down modulation sharpens category separability. Pearson correlations between model-derived RSMs and the TRSM were computed across layers under both intrinsic feedback and external steering and evaluated separately for the three tasks (Fig. 4B). 

Across all conditions, external steering consistently enhanced representational alignment with the theoretical RSM, particularly in deeper layers and in tasks with greater visual ambiguity. In the single-image task, correlations under external steering increased steadily across layers, peaking at r = 0.69 (FC8) and r = 0.71 (FC9), compared to r = 0.40 and r = 0.46, respectively, under intrinsic feedback. Mid-layer gains were also substantial (e.g., Conv5: 0.53 vs. 0.19). In the more difficult side-by-side task, the representational correlation peaked at r = 0.66 (FC8) under external steering, while intrinsic feedback remained near zero (r ≈ 0.05) across all layers. Similarly, in the highly ambiguous overlay task, external steering yielded r = 0.63 (FC8) and r = 0.49 (FC9), while intrinsic feedback again failed to form meaningful category structure (r ≤ 0.05 throughout). These effects were statistically significant at nearly every layer (Welch’s t-test, ***p < .001), with 3–10× greater correlations under external steering relative to intrinsic feedback in the mid-to-late layers. 

These results suggest that top-down steering reorganizes internal geometry by tightening within-category similarity and separating categories more clearly, thereby restoring meaningful structure even when sensory input is degraded and in the presence of distractors. Crucially, this reorganization mirrors the model performance results (Fig. 3). Just as external steering pushed recognition accuracy to near-ceiling (normal) levels under ambiguity, it also imposed a category-consistent structure on internal representations. In other words, the model performance gains emerge from representational restructuring, where top-down priors guide the network toward stable and semantically organized geometry despite noisy input. 

10 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

**==> picture [371 x 410] intentionally omitted <==**

**Fig. 5 | Comparing neural representations in the brain and EmoFB network. A.** Schematic of the brain-model representational similarity analysis (RSA). Sixty affective images (20 pleasant, 20 neutral, 20 unpleasant) were presented to both the EmoFB model and human participants during fMRI scanning. The EmoFB model generated two representational similarity matrices (RSMs): one before steering (after the first feedforward pass), and one after steering (after the final feedforward pass). Corresponding brain RSMs were computed from fMRI activity in predefined regions of interest (ROIs), such as the amygdala. Representational similarity was quantified as the Pearson correlation between modelderived and brain-derived RSMs. **B.** Model–brain similarity (Pearson correlation) across layer–ROI pairs, where each x- axis label indicates the specific pairing between a brain ROI and a corresponding EmoFB layer (e.g., V1–Conv1 compares the V1 ROI with Conv1 layer representations; Amygdala–(FC8, FC9) compares the amygdala ROI with concatenated features from FC8 and FC9). Bars show the mean similarity before steering (hatched) and after steering (solid), averaged over 10 independently initialized models. External steering significantly enhanced brain-model alignment in most regions, especially in later stages of visual processing and the amygdala. Error bars denote standard deviation. Statistical significance was assessed using Welch’s t-test (***p < .001, **p < .01, *p < .05, ns = not significant). 

## **Model–brain alignment assessed via representational geometry** 

To evaluate whether EmoFB captures human-like neural representations, we performed representational similarity analysis (RSA) between model-derived and fMRI-derived similarity matrices (RSMs) using 60 affective images (20 pleasant, 20 neutral, 20 unpleasant). RSMs were computed before steering (after the first feedforward pass) and after steering (after the final feedforward pass), and then compared to RSMs from different brain regions of interest (ROIs). Following prior work on brain and deep neural networks correspondence (Yamins et al. 2014; Khaligh-Razavi and Kriegeskorte 2014; Cichy et al. 2016; Pham et al. 2023), early convolutional layers (Conv1–Conv2) corresponded to V1, mid-level layers (Conv3–Conv4) to V4, 

11 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

and higher fully connected layers (FC5–FC7) to Lateral Occipital Complex (LOC). The highest affect-related layers (FC8–FC9) were compared with the amygdala, consistent with recent work showing that artificial neural networks can model human amygdala responses to emotional stimuli (Jang and Kragel 2025). This mapping reflects the known gradient from low-level features in V1, to object-level coding in LOC, to affective evaluation in the amygdala (Amaral, Behniea, et al. 2003). 

As shown in Fig. 5B, external steering increased model–brain similarity across most regions, with the largest gains observed in higher-level visual and affective areas. In the early visual cortex, similarity increased modestly. _V1–Conv1_ rose from r = 0.19 to r = 0.21 and _V1–Conv2_ from r = 0.23 to r = 0.26. In mid-level visual cortex, the improvements were more pronounced. _V4–Conv3_ improved from r = 0.28 to r = 0.31 and _V4–Conv4_ from r = 0.28 to r = 0.32. In higher-level regions, changes were subtler but still significant in some cases. _LOC–FC5_ remained stable (r = 0.27 before and after steering), _LOC–FC6_ increased from r = 0.35 to r = 0.37 (95% CI = [0.02, 0.01]), and _LOC–FC7_ showed no change (r = 0.36 both before and after steering). The most notable effect was observed in the amygdala (FC8, FC9) comparison, where model–brain similarity improved from r = 0.22 to r = 0.27, representing a robust and statistically significant increase (95% CI = [0.06, 0.03], *p < .001). 

These findings provide two insights. First, they show that external steering reorganizes internal representations in a way that brings the model closer to the brain’s representational geometry, from low-level visual encoding to higher-order affective perception. Second, they mirror biological evidence that emotion-related feedback alters sensory coding throughout the visual hierarchy. For example, emotional context modulates early visual cortex (Vuilleumier 2005), sharpens category distinctions in ventral temporal regions (Kensinger and Schacter 2006), and engages the amygdala to evaluate the emotional relevance of stimuli (Pessoa and Adolphs 2010). Thus, the improvement in model–brain alignment under external steering supports the view that contextual priors can reshape distributed representations in both artificial and biological systems, stabilizing perception and enhancing the salience of emotionally meaningful categories. 

**==> picture [363 x 262] intentionally omitted <==**

**----- Start of picture text -----**<br>
A<br>Visual Input EmoFB<br>No Steering<br>#1 Feedforward Pass<br>Emotion Recognition<br>Steering<br>B<br>Task1: Single image Task2: Side-by-side image Task3: Overlay image<br>C<br>**----- End of picture text -----**<br>


**==> picture [355 x 99] intentionally omitted <==**

12 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

**==> picture [14 x 13] intentionally omitted <==**

**----- Start of picture text -----**<br>
D<br>**----- End of picture text -----**<br>


**==> picture [453 x 162] intentionally omitted <==**

**----- Start of picture text -----**<br>
Task1: Single image<br>**----- End of picture text -----**<br>


Task2: Side-by-side image 

Task3: Overlay image 

**Fig. 6 | Pure top-down steering without recurrent modulation. A.** Schematic of the pure top-down steering condition. Unlike the recurrent version used in previous figures, where steering is applied after the first feedforward pass, here, the external steering signal is injected before the first pass. Target layers are pre-activated by the steering signal, and the network performs only a single feedforward pass. No recurrent modulation is used. **B.** Top-1 emotion recognition accuracy across three tasks, single image (left), side-by-side image (middle), and overlay image (right), comparing pure feedforward (no steering) and pure external steering (steering applied only once at input). **C.** Accuracy as a function of tuning strength under pure top-down steering. **D.** Layer-wise representational similarity (Pearson correlation) between model RSMs and the theoretical RSM under pure feedforward vs. pure top-down external steering. Here, FC8 and FC9 are shown separately to reveal layer-specific effects of steering within the affective system module; in Fig. 5B, they were grouped by their shared brain ROI (amygdala) for model–brain comparison. Steering improves category structure in deeper layers, especially for 

13 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

more ambiguous tasks. Error bars denote the standard error of the mean across 10 model initializations. Asterisks mark statistical significance (Welch’s t-test: ***p < .001, **p < .01, *p < .05, ns = not significant). 

## **Top-down steering in advance of stimulus input** 

Up to this point, top-down steering is triggered by bottom-up stimulus input. In many neuroscience experiments, an anticipatory state is established before the stimulus is shown. To examine the effect of top-down modulation of  “brain state” on stimulus processing, we evaluated EmoFB when an external category-level signal was injected into the visual system before the first feedforward pass (Fig. 6A), referred to as pure external steering, conceptually resembling prestimulus neural activation by expectations, such as contextual- or category-specific priors conveyed from prefrontal or amygdala circuits to visual cortex (Bar et al. 2006; Summerfield and Egner 2009; Kok et al. 2017). In other words, unlike the recurrent computational setup studied earlier (Figs. 3–5), where steering follows the first pass and influences the network over multiple iterations, this condition tests whether a one-time provision of prior knowledge is sufficient to improve performance and reorganize internal representations. 

Behaviorally, pure external steering produced significant gains in Top-1 accuracy across all three tasks compared to the pure feedforward condition (Fig. 6B). In the single-image task, accuracy increased from 69% to 92%. In the side-by-side condition, performance rose from 29% to 89%, and in the overlay condition, from 28% to 87%, roughly tripling of accuracy in the two ambiguous conditions the absence of recurrent processing. We next examined the effect of tuning strength on performance under pure external steering (Fig. 6C). Across all tasks, Top-1 accuracy followed an inverted-U profile, peaking at a tuning strength of 1.5. For example, in the overlay task, accuracy peaked at 87% at a strength of 1.5, then declined slightly at higher strengths. This pattern mirrors the behavior seen under recurrent steering, suggesting that optimal integration of priors is tunable even in a single-pass context. 

Finally, we assessed how pure external steering influenced internal representational structure by comparing model RSMs with the theoretical category-based RSM (Fig. 6D). As in previous analyses, steering enhanced representational similarity in deeper layers, especially under ambiguous conditions. In the overlay task, Pearson correlation in FC8 rose from r = 0.03 to 0.57, and in FC9 from r = 0.05 to 0.43. In the side-by-side task, FC8 improved from r = 0.04 to 0.60 **,** and FC9 from r = 0.04 to 0.38. Even in the single-image task, steering enhanced FC9 similarity from r = 0.40 to 0.69. All improvements were statistically significant (Welch’s t-test, ***p < .001). 

Taken together, these findings demonstrate that anticipatory modulation of visual cortex implemented by topdown steering can markedly enhance emotion recognition and reinforce category-specific clustering in representational geometry, even without recurrent processing. This parallels behavioral priming in humans, where expectations pre-activate task-relevant representations, which in turn accelerate recognition and sharpen category structure. 

14 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

**==> picture [440 x 276] intentionally omitted <==**

**----- Start of picture text -----**<br>
A<br>**----- End of picture text -----**<br>


**==> picture [443 x 18] intentionally omitted <==**

**----- Start of picture text -----**<br>
B<br>Task1: Single image Task2: Side-by-side image Task3: Overlay image<br>**----- End of picture text -----**<br>


**==> picture [479 x 131] intentionally omitted <==**

**Fig. 7 | Pure external steering performance as a function of tuning strength in target-absent trials. A.** Schematic representation of steering a target emotion category (e.g., sadness) in input images that do not initially exhibit the target emotion. **B.** Top-1 accuracy plotted as a function of tuning strength across three image display conditions: single, side-byside, and overlay. 

## **Effect of top-down steering on false positive rates** 

One drawback of top-down steering is that it increases false positive rates. We assessed how pure top-down external steering (i.e., steering applied before the first feedforward pass, as in Fig. 6) influenced recognition in target-absent trials, where the input images did not contain the steered emotion category (Fig. 7A). As shown in Fig. 7B, steering substantially increased false positive responses across all three task conditions. At tuning strength = 0, false positive rates were low, but they rose sharply with increasing tuning strength, peaking at intermediate values of 1.5 before declining slightly at stronger levels of steering. This inverted-U pattern indicates that steering progressively biases the model toward reporting the steered emotion, even when it is absent. The magnitude of this bias varied with task difficulty. False positives were most pronounced in the sideby-side and overlay conditions, reaching peak levels above 60–70%, consistent with the greater perceptual ambiguity in these tasks. In contrast, the single-image condition showed only a modest increase, with peak false positives remaining below ~50%, an intriguing result given that, in the target-present case, steering yielded the strongest performance gains on ambiguous composite conditions (overlay and side-by-side) compared to single- 

15 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

image conditions (Fig. 3B, Fig. 6B). This asymmetry suggests that the effect of top-down steering scales with perceptual ambiguity. In all three conditions, steering substantially improved target-present recognition, but the improvement was greatest when competing emotional inputs increased perceptual uncertainty. Correspondingly, false positive rates in target-absent trials were also highest in these ambiguous conditions (Fig. 7B), indicating that the same ambiguity that allows steering to enhance detection also makes the model more susceptible to misattributing the steered emotion when it is absent. This pattern parallels human perception, where top-down expectations enhance detection under clear conditions but, in the presence of ambiguity, can lead to misperceptions, such as mistaking a vague shadow or blurred spot for a threatening stimulus like a spider or snake (Öhman 2005; Sterzer et al. 2008). Ambiguity amplifies the influence of priors, making false alarms more likely when multiple interpretations are possible. 

Thus, while external steering effectively enhances recognition when the target emotion is present, it also heightens the risk of false alarms in its absence, particularly under conditions of competing emotional content. Together, these findings highlight a fundamental trade-off of top-down steering. It increases sensitivity to target emotions but reduces specificity, with the greatest vulnerability to false positives emerging in ambiguous contexts. This trade-off provides a computational parallel to human emotion perception (Moratti and Keil 2009; Bradley et al. 2012; Gruss and Keil 2019), where expectation-driven feedback can sharpen recognition of relevant signals but also increase susceptibility to false alarms under uncertainty. 

16 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **Discussion** 

In this study, we introduced EmoFB, a deep neural network model designed to examine how top-down feedback mechanisms shape visual emotion recognition. The model integrates a feedforward visual system module with an affective system module through both bottom-up and top-down pathways, allowing high-level emotional representations to modulate early visual processing. This cross-system design, inspired by anatomical pathways linking the anterio emotion-modulating structures such as the amygdala and prefrontal cortex to visual cortex (Amaral, Behniea, et al. 2003; Pessoa and Adolphs 2010; Barbas 2015), extends prior models by embedding an explicit affective–visual loop that captures the dynamic interplay between appraisal and perception (Gilbert and Li 2013; Lamme and Roelfsema 2000; Roelfsema and de Lange 2016). Across tasks with varying levels of ambiguity, feedback improved emotion recognition, with externally guided steering providing the largest benefits. It greatly boosted accuracy, sharpened category structure in the model’s internal representations, and made these representations more consistent with fMRI responses in both visual and affective brain regions. Concurrent with these positives we also note the negative effect of external steering in terms of increased false positives. 

## **Emotion shapes perception** 

Emotion recognition is not just a feedforward process. In real-world contexts, emotion perception, which depends on the recognition of objects, faces, and scenes,  often requires resolving ambiguity and integrating prior knowledge, expectations, and internal states (Vuilleumier 2005). Top-down feedback is central to this process; rather than passively encoding sensory data, the brain continuously reinterprets visual input in light of prior knowledge about its emotional relevance (Pourtois et al. 2013). EmoFB demonstrates this principle computationally. We show that feedback signals, constructed from emotion-category prototypes, reorganize intermediate visual features, improving recognition accuracy and restoring category structure even under ambiguous input. This mirrors neuroscience evidence that the amygdala and medial prefrontal cortex project back to visual areas, biasing processing toward emotionally salient information (Amaral, Behniea, et al. 2003; Vuilleumier and Driver 2007). Functionally, such feedback enhances detection of threat- or reward-related cues under uncertainty, tuning perception toward motivationally relevant features (Öhman 2005; Pessoa and Adolphs 2010; Pourtois et al. 2013). By integrating these behavioral and representational findings with neurobiological evidence, EmoFB highlights how emotional feedback can sharpen perception under ambiguity. The model thus provides a computational framework for testing hypotheses about how emotional states reshape sensory coding in the brain. 

## **Multiple forms of top-down control** 

EmoFB incorporates two complementary forms of top-down modulation: intrinsic feedback and external steering. Intrinsic feedback is appraisal-like and stimulus-driven, using activations within the affective module, derived directly from the current input, to modulate early visual layers. External steering, by contrast, is expectation-based, injecting category-prototype signals into early layers as state-dependent priors (Vuilleumier 2005; Pourtois et al. 2013). Our results show that both mechanisms improve performance. Whereas intrinsic feedback yields modest gains, external steering produces substantial accuracy improvements, especially under ambiguous conditions. This difference arises because intrinsic feedback is limited to the information in the current stimulus. Such signals resemble cognitive appraisal in the brain, where affective interpretations of incoming stimuli are formed and updated (Sander et al. 2005; Cunningham and Brosch 2012; Moors et al. 2013), but without the influence of learned priors or contextual cues. As a result, the intrinsic signal carries internal noise and is insufficient to drive great improvements in recognition when inputs are degraded or conflicting. External steering, by contrast, provides a clear and structured prior. Importantly, external steering can be applied in advance of stimulus input (referred to as pure external steering), paralleling anticipatory modulation in the brain, where task demands, contextual cues, and past experience bias perception toward anticipated emotional categories (Summerfield and Egner 2009; W. Li and Keil 2023). Neuroimaging and behavioral studies further show that emotional cues capture attention automatically but have much stronger and more reliable effects when they are directly relevant to current goals, reflecting interactions between prefrontal control signals and amygdala-based affective signals (Vuilleumier 2005; Pourtois et al. 2013). By injecting prototype-based signals, 

17 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

whether bottom-triggered or top-down applied in the absence of stimulu inpus, EmoFB reshapes internal representations and imposes categorical structure on early visual processing, enabling the network to resolve ambiguity and align perception with task-relevant emotional states. 

## **Model-brain representational alignment** 

Top-down feedback not only improved task performance but also increased the similarity between EmoFB’s internal representations and human brain activity. Using RSA, we found that external steering strengthened correlations between model and brain RSMs, particularly in V1, V2, LOC, and the amygdala. These results parallel the role of emotional top-down feedback in the brain. Emotional stimuli engage the amygdala, whose outputs influence activity in visual cortical areas, amplifying processing of emotionally salient information. fMRI and ERP studies report stronger responses to emotional versus neutral stimuli in early visual cortex (Lang et al. 1998; Pourtois et al. 2004; Padmala and Pessoa 2008; Y. Liu et al. 2011) and in higher-order regions such as fusiform cortex (Morris et al. 1998; Vuilleumier and Schwartz 2001; Sabatinelli et al. 2005). Anatomical and imaging studies provide a mechanistic basis for these effects, revealing bidirectional pathways linking the amygdala and prefrontal cortex with both early and mid-level visual areas (Amaral, Behniea, et al. 2003; Catani et al. 2003).  Lesion studies further demonstrate causality: amygdala damage abolishes the visual enhancement normally observed for emotional stimuli (Vuilleumier et al. 2004). 

The enhanced brain–model alignment observed in EmoFB suggests that its steering signals mimic this biological feedback mechanism. Notably, the effect extended from early visual regions to higher ventral areas, consistent with the view that affective feedback cascades through the visual hierarchy, shaping perception from its earliest stages (Amaral, Behniea, et al. 2003; Vuilleumier and Driver 2007). This mirrors our network architecture, where top-down pathways from the affective module modulate higher layers (e.g., Conv5) and recursively influence earlier ones (e.g., Conv2), echoing amygdala–visual feedback loops described in neuroanatomical studies (Pessoa and Adolphs 2010). Electrophysiological evidence supports this interpretation, showing that emotional stimuli boost very early visual responses, such as the first wave of activity in primary visual cortex and slightly later signals in nearby extrastriate areas, consistent with attentional gain-control mechanisms (Pourtois et al. 2004; Rotshtein et al. 2010; Y. Liu et al. 2011). 

## **False alarms in brains and machines** 

Although emotional top-down steering can substantially enhance emotion recognition, it can also increase false positives. In these cases, the steering signal biases the model to detect the target emotion even when it is not present in the stimulus. Our target-absent analysis (Fig. 7) showed that false alarms were not uniform across tasks; they were much higher in the side-by-side and overlay conditions than in the single-image condition. This pattern suggests that stimulus ambiguity amplifies the influence of top-down expectations, when multiple emotions compete within a scene, steering is more likely to bias recognition toward the cued category, even in its absence. 

A similar phenomenon is well documented in the brain, where emotional states can bias perception and, through feedback, override bottom-up sensory input. For example, expectations about threat can shift the interpretation of ambiguous stimuli toward fearful meanings even in the absence of actual threat cues (Phelps 2006). Electrophysiological evidence further shows that emotional states amplify early visual responses, even when stimuli are neutral or degraded (Pourtois et al. 2004; Rotshtein et al. 2010). This pattern is consistent with an “expectation overweighting” mechanism, whereby affective priors exert disproportionate influence on perception, biasing ambiguous input toward anticipated emotional categories (Phelps 2006; Vuilleumier 2005; Pessoa and Adolphs 2010). In anxiety and post-traumatic stress disorder (PTSD), heightened expectations of threat amplify false alarms, leading individuals to misperceive neutral or ambiguous cues as threatening (Bishop 2007; Fani et al. 2012). Such biases illustrate how mechanisms that are adaptive in uncertain or threatening environments, where missing an emotional cue carries a greater cost than mistakenly perceiving one, can become maladaptive when feedback is chronically overweighted. 

## **Comparisons with related work** 

18 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

Most existing deep learning models for emotion recognition rely on feedforward architectures, treating emotional categories as static labels (Mollahosseini et al. 2019; S. Li and Deng 2022). Few attempt to capture how emotional interpretation dynamically reshapes perception. Even models that incorporate recurrence or attention generally lack explicit affective-to-visual feedback (Kollias and Zafeiriou 2020; Zhang et al. 2015). When feedback is included, it typically remains confined within a single processing system rather than crossing between affective and perceptual systems. 

EmoFB is a biologically inspired model that explicitly incorporates top-down feedback between affective and visual systems. While informed by prior vision-based feedback models (Konkle and Alvarez 2023b), it advances them by introducing a dedicated affective system module and redirecting feedback from a purely visual–tovisual pathway to a visual–to–affective–to–visual pathway. In this way, EmoFB was designed to simulate the emotional attentional control mechanisms thought to operate in human perception. By introducing cross-system feedback from an affective module into a visual module, EmoFB implements a biologically inspired mechanism of top-down modulation. This design yields an interpretable architecture with emotion-specific feedback that goes beyond performance optimization, offering a principled framework for investigating how emotional states shape perception. EmoFB integrates prior work on visual feedback with a neurobiologically grounded account of emotion–perception integration. 

## **Summary** 

This study introduces EmoFB, a biologically inspired neural network that integrates an affective system with a visual processing system through top-down feedback. By allowing emotional representations to modulate visual layers, EmoFB captures the reciprocal influence between perception and emotion. The model implements two complementary feedback mechanisms: (1) intrinsic feedback, stimulus-driven and appraisal-like feedback; (2) external steering, bottom-up triggered and expectation-based feedback. Both improve recognition under ambiguity, with external steering providing the strongest gains. Representational analyses show that steering sharpens category structure and increases alignment with human brain activity, particularly in the early visual cortex, LOC, and the amygdala, underscoring the model’s biological plausibility. EmoFB thus provides a framework for testing how emotion-based feedback shapes perception across hierarchical layers, how internally versus externally guided cues influence recognition, and how feedback alters brain–model alignment, questions directly testable with fMRI, EEG, or behavioral paradigms. 

19 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **Materials and Methods** 

## **Image datasets for model training and testing** 

Training and testing of the EmoFB network utilized two primary image datasets: ImageNet (Deng et al. 2009) and EmoSet (Yang et al. 2023b). The ImageNet dataset, a widely used dataset in computer vision and deep learning, was used to pretrain the visual system module for object recognition, enabling it to extract rich, general-purpose visual features from natural scenes. The EmoSet dataset, a more recently published dataset, was developed for emotion recognition. It contained images from diverse visual sources such as social media and artistic platforms (Yang et al. 2023b). EmoSet comprises over 3.3 million images, including 118,102 labeled images, each annotated with one of eight emotion categories: amusement, anger, awe, contentment, disgust, excitement, fear, and sadness. In this study, the labeled EmoSet data were divided into three sets: 80% training **,** 5% validation, and 15% test. Accordingly, we used 90,664 images for training **,** 7,998 for validation, and 19,440 for testing (see Supplementary Fig. S1A). To mitigate class imbalance during training, we applied class weighting based on the inverse frequency of each emotion category in the training set (Supplementary Fig. S1B). 

To systematically evaluate model performance under different visual tasks, we constructed a composite test set of triplets from the EmoSet test images. Each triplet includes three presentation formats: original _,_ overlay _,_ and side-by-side (see Fig. 7A). The number of images per format was approximately balanced across emotion categories to ensure fair comparisons across conditions. Roughly 1,200 images were included in each format, forming the basis for all top-down feedback–related model testing and theoretical RSA analysis. 

All input images were resized to 224×224 pixels. During training, we applied random resized cropping, random horizontal flipping, and ImageNet-style normalization (mean = [0.485, 0.456, 0.406]; std = [0.229, 0.224, 0.225], scaled by 255). For the test, images were center-cropped to the same resolution and normalized identically. Pixel values were cast to float16 for memory efficiency. Since image files are typically stored in Height × Width × Channel (HWC) format, all images were converted to Channel × Height × Width (CHW) format before being passed into the network, as required by PyTorch convolutional layers. 

We additionally evaluated EmoFB using the International Affective Picture System  (IAPS) (Bradley and Lang 2007), a standard stimulus set in affective neuroscience with normative ratings along continuous valence and arousal dimensions. IAPS images were not used for training or validation. They were reserved exclusively for post-training analyses to assess whether affective representations learned from EmoSet generalized to a canonical neuroscience dataset. 

All IAPS images were preprocessed identically to EmoSet test images (224×224 resolution, ImageNet normalization, CHW format) and passed through the trained network in inference mode. Internal representations were extracted from selected layers and analyzed using RSA. 

## **Deep neural networks** 

The proposed EmoFB network consists of two modules: a visual system module and an affective system module (Fig. 1A–B). The visual system module was adapted from the study (Konkle and Alvarez 2023b), which was based upon AlexNet, but with the addition of feedback connections from the final fully-connected layer to earlier fully-connected and convolutional layers. The visual system was trained on ImageNet for object recognition. For our implementation, we retrained this module for 300 epochs on ImageNet using four NVIDIA A100 GPUs. Training was conducted with a batch size of 1024, an initial learning rate of 0.1 decayed by a factor of 0.1 every 50 epochs, and cross-entropy loss as the optimization objective. 

For emotion recognition, we replaced the last fully connected layer for object recognition with the affective system module, which includes 3 fully connected layers. Feedbacks come from the second-to-the-last layer of the affective system module and connects to Conv5 and Conv4 layers of the visual module. The rationale for choosing the second-to-the-last layer instead of the last layer of the affective system module as the source of the top-down feedback signal is that this layer has richer emotion-related semantic features compared to the last 

20 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

layer, which has only 8 units corresponding to 8 discrete emotions (Yang et al. 2023a): amusement, anger, awe, contentment, disgust, excitement, fear, sadness. 

To complete the EmoFB network model, we added one additional feed-forward connection from Conv5 of the visual system to the first layer (FC8) of the affective system. The information from this connection is integrated (concatenated) with the feed-forward connection from FC7 in the visual system. In this way, the affective system receives not only the high-level visual semantic features but also the less-processed features, which are dynamically influenced by the top-down feedback. This addition was inspired by biological studies in the brain, where there are bidirectional connections between lower-order and higher-order visual areas (Gilbert and Li 2013). 

∙ _Visual Feature Extraction:_ Let 𝐼∈ℝ[!×#×$] denote the input image. The visual system 𝑉( ) transforms the input into high-level visual features: 

**==> picture [227 x 11] intentionally omitted <==**

Here, 𝑦%&'()* ∈ℝ[+] represents the activation vector from the final visual layer (e.g., FC7), and 𝑑 is the feature dimensionality. 

∙ _Emotion Recognition_ The affective system, 𝐴( ), receives the visual features in Eq. (1) and maps them to a set of 8 discrete emotion categories (e.g., amusement, fear, disgust, etc.) via three fully connected layers trained on emotion classification: 

**==> picture [247 x 13] intentionally omitted <==**

where 𝑦),,-./&%- ∈ℝ[-] and 𝑒= 8 is the number of emotion classes. 

_Feedback Modulation_ : Following the long-range modulatory feedback framework proposed by (Konkle and Alvarez 2023a) _,_ we introduce feedback connections from the layer FC9 (source layer) in the affective system to the two target layers in the visual system: ℓ∈{𝐶𝑜𝑛𝑣4, 𝐶𝑜𝑛𝑣5}. These connections modulate activations in the two visual layers using outputs from the affective layer FC9. Let 𝚾,. ∈ℝ[0×1] denote the batch-wise output of a fully connected layer (e.g., FC9) in the affective system, and let 𝚾.23% ∈ℝ[0×4×!×#] be the activation tensor of a target convolutional layer in the visual system, with 𝐵 as batch size, 𝐹 as the number of  units in the source layer, 𝐶 as the number of channels, and 𝐻× 𝑊 as spatial dimensions. 

The feedback modulation proceeds as follows: 

1. Normalization 

The FC output is normalized using layer normalization: 

**==> picture [249 x 14] intentionally omitted <==**

2. Activation Bounding 

A tanh nonlinearity is applied to constrain the signal: 

**==> picture [233 x 14] intentionally omitted <==**

3. Learned Scaling 

21 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

The bounded vector is scaled by a learnable weight vector 𝒔 ∈ℝ[1] , which encodes the contribution of each unit in the source layer: 

**==> picture [217 x 14] intentionally omitted <==**

where ⨀ denotes elementwise multiplication. 

4. Global Tuning Strength 

An additional scalar parameter 𝜆∈ℝ, referred to as the tuning strength, is applied to globally control the overall influence of the feedback signal: 

**==> picture [224 x 11] intentionally omitted <==**

Unlike 𝒔, which is learned during training, 𝜆 is manually controlled at test time to modulate the intensity of the top-down signal. 

5. Reshaping and Broadcasting 

𝚾/(3-+ is reshaped to shape (B, F, 1, 1) to prepare for channel alignment. 

6. Channel Alignment via 1×1 Convolution 

A 1×1 convolution projects the feedback signal to match the convolutional layer’s channel dimension C: 

**==> picture [286 x 12] intentionally omitted <==**

7. Multiplicative Modulation 

The original activation 𝚾.23%  is modulated through multiplicative gain control, consistent with biological evidence from attention studies (Treue and Trujillo 1999; Reynolds et al. 2000): 

**==> picture [261 x 11] intentionally omitted <==**

8. Nonlinearity 

Finally, a ReLU activation is applied to the modulated output: 

**==> picture [246 x 12] intentionally omitted <==**

This mechanism allows the network to contextually modulate image processing in the visual system based on high-level affective representations, echoing theories of emotion-guided perception in biological systems (Pessoa 2008; Vuilleumier 2005; L. f. Barrett and Bar 2009; Pourtois et al. 2013). 

_Top-down Steering Modulation_ : Top-down steering modulation is designed to isolate the influence of categorylevel expectations on visual processing while holding the feedback circuitry fixed. In biological systems, topdown signals often convey abstract, task-relevant, or contextual information that biases sensory processing toward behaviorally relevant features ((Vuilleumier 2005; Reynolds and Heeger 2009; Summerfield and de Lange 2014). 

22 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

It uses the same feedback pathways described earlier. The only difference is that instead of taking the FC9 activation (𝚾,.) from the current input image as the feedback signal, the modulation begins with a category prototype vector (𝑝7 ∈ℝ[1] ) computed as the mean FC9 activation across validation exemplars of category 𝑘: 

**==> picture [261 x 38] intentionally omitted <==**

(&) where 𝑁7 is the number of validation images in category 𝑘, and 𝚾,. is the FC9 activation vector for image _i_ This prototype replaces 𝚾,. at the normalization step, while all subsequent operations remain unchanged. 

## **fMRI Dataset** 

_Participants_ : The experimental protocol was approved by the University of Florida Institutional Review Board. Twenty healthy volunteers with normal or corrected-to-normal vision participated in fMRI scanning after providing written informed consent (mean age = 20.4 ± 3.1 years; 10 male, 10 female). 

_Experimental Paradigm_ : Participants passively viewed affective images selected from the International Affective Picture System (IAPS; Bradley and Lang 2007) while simultaneous EEG-fMRI was acquired (EEG data are not analyzed in this study). Each picture was presented for 3 s, followed by a variable interstimulus interval (ISI) of either 2800 ms or 4300 ms. Jittered ISIs were employed to minimize temporal predictability and optimize event-related hemodynamic modeling. Each session consisted of 60 trials (one picture per trial), and participants completed five sessions in total. Across sessions, the 60 images were randomized in order. Stimuli were displayed on an MR-compatible monitor outside the bore and viewed through a reflective mirror. Participants were instructed to maintain central fixation throughout (see Fig. 8). 

23 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

**==> picture [376 x 475] intentionally omitted <==**

**Fig. 8 | fMRI data acquisition and the distribution of the emotion variables in dataset IAPS** . **A** . The protocol of brain data recording. It shows an image to a subject every 2.8 or 4.3 seconds. Forty-eight images are randomly selected from IAPS. The interval resting time is randomly set to be 2.8 or 4.3 seconds to reduce the priming rate before seeing an image. **B** . The emotion valence and arousal distribution in IAPS. (left) includes the 60 images, and (right) includes all IAPS images. As one can see, the selected 60 images are still following the same distribution pattern as all IAPS images. C. The relationship between valence and subcategories in IAPS images. Low valences are mostly related to vomit, bloody scenes, and mutilate body; the middle range valences are more associated with neutral people, landscapes, and household objects; the high valences include delicious food, smiling faces, and erotic couples. Example images shown in panel B are from the International Affective Picture System (IAPS; (Bradley and Lang 2007) 

_Data Acquisition and Preprocessing_ : Imaging was conducted on a 3T Philips Achieva scanner (Philips Medical Systems). Functional scans were acquired with the following parameters: TR = 1.98 s, TE = 30 ms, flip angle = 80°, 36 slices, FOV = 224 mm, matrix = 64 × 64, voxel size = 3.5 × 3.5 × 3.5 mm³. Slices were collected in ascending order and aligned parallel to the AC–PC plane. A high-resolution T1-weighted anatomical scan was also obtained (see Fig. 8). 

24 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

Preprocessing was performed in SPM (http://www.fil.ion.ucl.ac.uk/spm/). The first five volumes from each run were discarded to allow for scanner equilibration. Standard steps included slice-timing correction, realignment (six motion parameters), normalization to the Montreal Neurological Institute (MNI) template with resampling to 3 × 3 × 3 mm³ voxels, and spatial smoothing with an 8 mm FWHM Gaussian kernel. A high-pass temporal filter (1/128 Hz) was applied to remove low-frequency drifts. 

_Single-Trial Beta-Series Estimation_ : To capture trial-specific responses, we applied the beta-series approach (Mumford et al. 2012). For each trial, a general linear model (GLM) was fit with the target trial modeled by its own regressor, while all remaining trials were grouped into a separate regressor. Six motion parameters were included as nuisance covariates. This process produced a unique beta estimate for every trial. For reliability, beta estimates corresponding to repeated presentations of the same picture across sessions were averaged, resulting in 60 distinct picture-specific activation patterns per participant. These trial-level patterns served as input for representational similarity analysis. 

## **Representational Similarity Analysis (RSA)** 

To evaluate how well the EmoFB network model captured category-level structure in its internal representations, we performed a representational similarity analysis comparing model-derived representational similarity matrices (RSMs) to a predefined theoretical RSM. 

_Theoretical RSM_ : The theoretical RSM encodes idealized representational geometry in which stimuli belonging to the same emotion category are maximally similar (similarity = 1), and stimuli from different categories are maximally dissimilar (similarity = 0). This matrix reflects the hypothesis that emotion category identity should shape the representational structure of the model. 

_Model-based RSMs_ : For each network layer (Conv1–Conv5, FC6–FC9), we extracted activation vectors in response to all test images and computed an empirical RSM by calculating Pearson correlations between all image pairs. This was done under two feedback conditions: 

- Intrinsic Feedback: Top-down modulation was derived from instance-specific activations of the source layer (e.g., FC9) from the previous feedforward pass. This mechanism reflects internal recurrent processing within the model, where the feedback signal is stimulus-dependent and dynamically generated. 

- External Steering: Top-down modulation was instead driven by a category-level prototype signal, computed as the average activation of the source layer (e.g., FC9) across all training exemplars belonging to the same emotion category. This form of feedback introduces an externally defined expectation that generalizes across instances. 

Separate RSA analyses were conducted for each of the three task contexts: single image, side-by-side image, and overlay image. 

_Comparison to theoretical RSM_ : To quantify the alignment between empirical and theoretical representational structures, we computed the Pearson correlation between the lower triangular portions (excluding the diagonal) of each empirical RSM and the theoretical RSM. This resulted in a similarity score per layer, per task, and per feedback condition. 

_Statistical Analysis_ : Paired two-sided t-tests were used to compare the theoretical RSM similarity scores between the external steering and intrinsic feedback conditions at each layer, using asterisk notation: p < 0.05 (*), p < 0.01 (**), and p < 0.001 (***). 

## **Comparison with the human brain RSM** 

We performed representational similarity analyses to examine how closely the internal representations of the EmoFB model aligned with brain activity patterns across multiple visual and affective regions. This analysis 

25 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

was based on functional MRI (fMRI) data from 20 participants who viewed 60 emotional images selected from the IAPS. The image set was evenly divided into three affective categories **—** pleasant, neutral, and unpleasant **,** with 20 images per category. The same 60 images were used as input to the EmoFB network. 

_Brain RSM Construction_ : Neural activation patterns were extracted from six bilateral regions of interest: early visual areas (V1–V4), the lateral occipital complex (LOC), and the amygdala. For each image and subject, we extracted voxel-wise beta estimates from each ROI. The resulting 𝑣𝑜𝑥𝑒𝑙 ×  𝑖𝑚𝑎𝑔𝑒 ×  𝑠𝑢𝑏𝑗𝑒𝑐𝑡 matrices were cleaned by removing missing values (NaNs) and standardized using z-score normalization within each subject and image. 

For each subject 𝑠 and image 𝑖, we normalize the voxel activation 𝒗&,' ∈ℝ[=] as: 

**==> picture [293 x 26] intentionally omitted <==**

where 𝜇',& and 𝜎',& are the mean and standard deviation of the non-NaN voxel activations for subject 𝑠 and image 𝑖.  We then compute the average normalized activation across all subjects for each voxel and image: 

**==> picture [287 x 36] intentionally omitted <==**

where 𝐚& ∈ℝ[=] is the averaged activation vector for image 𝑖. For each pair of images (𝑖, 𝑗),  we compute the Pearson correlation: 

**==> picture [336 x 16] intentionally omitted <==**

This yielded a 60 × 60 brain RSM for each ROI. 

_DNN RSM Construction_ : We extracted activation vectors from selected layers of the EmoFB model (Conv1– Conv5, FC6–FC9) in response to the same 60 IAPS images. RSMs were computed for each layer under two conditions: 

- Before Steering: Activation patterns from the initial feedforward pass, prior to any top-down modulation. 

- After Steering: Activation patterns from the final feedforward pass, following application of categorylevel external steering. 

Pairwise Pearson correlations 𝑟 between image activation vectors were computed, forming a 60 × 60 model RSM for each layer and condition. 

_Brain-Model Similarity_ : To assess representational correspondence, we computed the Pearson correlation between the lower triangular (off-diagonal) values of each DNN RSM and its corresponding brain RSM. This analysis was performed for each ROI and layer, both before and after steering. 

_Statistical Analysis:_ Similarity scores were compared using paired two-sided t-tests between the Before Steering and After Steering conditions. Significance levels were denoted as follows: p < 0.05 (*), p < 0.01 (**), p < 0.001(***), and “ns” for non-significant results. 

26 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **Top-down steering in advance of stimulus input** 

To test the extent to which abstract, category-level expectations can bias the initial feedforward sweep of visual processing, in the pure top-down steering condition, the EmoFB model received visual input through a single feedforward pass, whereas intermediate visual layers (e.g., Conv4 and Conv5) were already modulated by externally supplied category-level steering signals. In other words, the activity of the network was already biased by the steering signal in anticipation of the visual input. No recurrent passes or additional stimulus presentations were used, ensuring that any modulation originated solely from the top-down steering input. 

Each test image was presented once to establish a baseline condition. In the pure external steering setting, the model did not reprocess the image or rely on recurrent passes. Instead, a category-level steering signal, computed as a prototype vector from validation set exemplars, was injected into designated layers during a single feedforward pass. The validation set was used to generate these prototypes to avoid overlap with training images and ensure an unbiased source of category-level information. This signal propagated forward through the network to generate an emotion prediction without direct image input. We evaluated two conditions: 

- Pure Feedforward: A standard forward pass with the test image, with no external modulation. 

- • Pure External Steering: A forward pass using only the category-level steering signal to modulate internal representations. 

We assessed Top-1 classification accuracy across three emotion recognition tasks—single image, side-by-side image, and overlay image. Paired two-sided t-tests confirmed statistical significance. Significance levels were denoted as follows: p < 0.05 (*), p < 0.01 (**), p < 0.001(***), and “ns” for non-significant results. To examine the effect of steering intensity, we varied a scalar tuning strength parameter (range: 0.0 to 3.0 in 0.5 increments), which scaled the external modulation signal. Across all tasks, accuracy followed an inverted-U profile, peaking at moderate strength (1.5). One-way repeated measures ANOVA revealed a significant main effect of tuning strength ( _F_ > 500, _p_ < 1e−50), and post hoc tests showed significant pairwise differences between tuning levels (denoted by *, **, or ***).  To evaluate whether pure top-down steering enhanced category structure, we applied the same representational similarity analysis used in Fig. 4, comparing each model layer’s RSM to a theoretical category-based RSM. Statistical differences between conditions were assessed using paired t-tests, where p < 0.05 (*), p < 0.01 (**), p < 0.001(***), and “ns” for non-significant results. 

## **Target-absent evaluation** 

Target-absent evaluation followed the same procedure as the pure top-down steering condition, with the only difference being the stimuli: test trials contained no image from the target category. As in the target-present case, a category-level steering signal (derived from validation exemplars) was injected into the designated layers during a single feedforward pass. This setup allowed us to quantify false alarm rates by measuring how often the model incorrectly reported the presence of the target emotion in the absence of a corresponding stimulus (i.e., false positives). 

27 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **Acknowledgements** 

This work was supported in part by the National Science Foundation grants 1908299 and 2318984 and the National Institutes of Health/National Institute of Mental Health grants MH112558 and MH125615, the University of Florida Artificial Intelligence Research Catalyst Fund, and the University of Florida Informatics Institute Graduate Student Fellowship. The funders had no role in study design, data collection and analysis, decision to publish, or preparation of the manuscript. 

28 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

## **References** 

Agrawal, Pulkit, Dustin Stansbury, Jitendra Malik, and Jack L. Gallant. 2020. “Convolutional Neural Networks Mimic the Hierarchy of Visual Representations in the Human Brain.” _Journal of Cognitive Neuroscience_ 32 (12): 1–15. 

- Amaral, D. G., M. D. Bauman, and C. Mills Schumann. 2003. “The Amygdala and Autism: 

   - Implications from Non-Human Primate Studies.” _Genes, Brain, and Behavior_ 2 (5): 295–302. https://doi.org/10.1034/j.1601-183x.2003.00043.x. 

- Amaral, D. G., H. Behniea, and J. L. Kelly. 2003. “Topographic Organization of Projections from the Amygdala to the Visual Cortex in the Macaque Monkey.” _Neuroscience_ 118 (4): 1099– 120. https://doi.org/10.1016/S0306-4522(02)01001-1. 

- Arnold, Magda B. 1960. _Emotion and Personality_ . Emotion and Personality. Columbia University Press. 

- Aston-Jones, Gary, and Jonathan D. Cohen. 2005. “AN INTEGRATIVE THEORY OF LOCUS COERULEUS-NOREPINEPHRINE FUNCTION: Adaptive Gain and Optimal Performance.” _Annual Review of Neuroscience_ 28 (Volume 28, 2005): 403–50. https://doi.org/10.1146/annurev.neuro.28.061604.135709. 

- Aston-Jones, Gary, Janusz Rajkowski, and Jonathan Cohen. 1999. “Role of Locus Coeruleus in Attention and Behavioral Flexibility.” _Biological Psychiatry_ 46 (9): 1309–20. https://doi.org/10.1016/S0006-3223(99)00140-7. 

- Bar, M., K. S. Kassam, A. S. Ghuman, et al. 2006. “Top-down Facilitation of Visual Recognition.” _Proceedings of the National Academy of Sciences_ 103 (2): 449–54. https://doi.org/10.1073/pnas.0507062103. 

- Barbas, Helen. 2015. “General Cortical and Special Prefrontal Connections: Principles from Structure to Function.” _Annual Review of Neuroscience_ 38 (Volume 38, 2015): 269–89. https://doi.org/10.1146/annurev-neuro-071714-033936. 

- Barrett, L. f., and Moshe Bar. 2009. “See It with Feeling: Affective Predictions during Object Perception.” _Philosophical Transactions of the Royal Society B: Biological Sciences_ 364 (1521): 1325–34. https://doi.org/10.1098/rstb.2008.0312. 

- Barrett, Lisa Feldman, and W. Kyle Simmons. 2015. “Interoceptive Predictions in the Brain.” _Nature Reviews Neuroscience_ 16 (7): 419–29. https://doi.org/10.1038/nrn3950. 

- Bishop, Sonia J. 2007. “Neurocognitive Mechanisms of Anxiety: An Integrative Account.” _Trends in Cognitive Sciences_ 11 (7): 307–16. https://doi.org/10.1016/j.tics.2007.05.008. 

- Bradley, Margaret M., Andreas Keil, and Peter J. Lang. 2012. “Orienting and Emotional Perception: Facilitation, Attenuation, and Interference.” _Frontiers in Psychology_ 3 (November). https://doi.org/10.3389/fpsyg.2012.00493. 

- Bradley, Margaret M., and Peter J. Lang. 2007. “The International Affective Picture System (IAPS) 

   - in the Study of Emotion and Attention.” In _Handbook of Emotion Elicitation and Assessment_ . Series in Affective Science. Oxford University Press. 

- Cardinal, Rudolf N., John A. Parkinson, Jeremy Hall, and Barry J. Everitt. 2002. “Emotion and Motivation: The Role of the Amygdala, Ventral Striatum, and Prefrontal Cortex.” _Neuroscience & Biobehavioral Reviews_ 26 (3): 321–52. https://doi.org/10.1016/S01497634(02)00007-6. 

- Catani, Marco, Derek K. Jones, Rosario Donato, and Dominic H. ffytche. 2003. “Occipito‐temporal Connections in the Human Brain.” _Brain_ 126 (9): 2093–107. https://doi.org/10.1093/brain/awg203. 

- Cichy, Radoslaw Martin, Aditya Khosla, Dimitrios Pantazis, Antonio Torralba, and Aude Oliva. 2016. “Comparison of Deep Neural Networks to Spatio-Temporal Cortical Dynamics of Human Visual Object Recognition Reveals Hierarchical Correspondence.” _Scientific Reports_ 6 (1): 1. https://doi.org/10.1038/srep27755. 

29 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

Cools, Roshan, and Mark D’Esposito. 2011. “Inverted-U-Shaped Dopamine Actions on Human Working Memory and Cognitive Control.” _Biological Psychiatry_ 69 (12): e113-125. https://doi.org/10.1016/j.biopsych.2011.03.028. 

- Cunningham, William A., and Tobias Brosch. 2012. “Motivational Salience: Amygdala Tuning from Traits, Needs, Values, and Goals.” _Current Directions in Psychological Science_ (US) 21 (1): 54–59. https://doi.org/10.1177/0963721411430832. 

- Deng, J., W. Dong, R. Socher, L. Li, Kai Li, and Li Fei-Fei. 2009. “ImageNet: A Large-Scale Hierarchical Image Database.” _2009 IEEE Conference on Computer Vision and Pattern Recognition_ , June, 248–55. https://doi.org/10.1109/CVPR.2009.5206848. 

- Desimone, Robert, and John Duncan. 1995. “Neural Mechanisms of Selective Visual Attention.” _Annual Review of Neuroscience_ 18 (Volume 18, 1995): 193–222. 

https://doi.org/10.1146/annurev.ne.18.030195.001205. 

- Duncan, John, and Glyn W. Humphreys. 1989. “Visual Search and Stimulus Similarity.” 

   - _Psychological Review_ (US) 96 (3): 433–58. https://doi.org/10.1037/0033-295X.96.3.433. 

- Fani, N., E. B. Tone, J. Phifer, et al. 2012. “Attention Bias toward Threat Is Associated with Exaggerated Fear Expression and Impaired Extinction in PTSD.” _Psychological Medicine_ 42 (3): 533–43. https://doi.org/10.1017/S0033291711001565. 

- Fişek, Mehmet, Dustin Herrmann, Alexander Egea-Weiss, et al. 2023. “Cortico-Cortical Feedback Engages Active Dendrites in Visual Cortex.” _Nature_ 617 (7962): 769–76. https://doi.org/10.1038/s41586-023-06007-6. 

- Friston, Karl. 2005. “A Theory of Cortical Responses.” _Philosophical Transactions of the Royal Society B: Biological Sciences_ 360 (1456): 815–36. https://doi.org/10.1098/rstb.2005.1622. 

- Gilbert, Charles D., and Wu Li. 2013. “Top-down Influences on Visual Processing.” _Nature Reviews Neuroscience_ 14 (5): 350–63. https://doi.org/10.1038/nrn3476. 

- Grossberg, Stephen. 1980. “How Does a Brain Build a Cognitive Code?” _Psychological Review_ (US) 87 (1): 1–51. https://doi.org/10.1037/0033-295X.87.1.1. 

- Gruss, L. Forest, and Andreas Keil. 2019. “Sympathetic Responding to Unconditioned Stimuli Predicts Subsequent Threat Expectancy, Orienting, and Visuocortical Bias in Human Aversive Pavlovian Conditioning.” _Biological Psychology_ 140 (January): 64–74. https://doi.org/10.1016/j.biopsycho.2018.11.009. 

- He, Kaiming, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. 2016. “Deep Residual Learning for Image Recognition.” _2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)_ , June, 770–78. https://doi.org/10.1109/CVPR.2016.90. 

- Jang, Grace, and Philip A. Kragel. 2025. “Understanding Human Amygdala Function with Artificial Neural Networks.” Research Articles. _Journal of Neuroscience_ 45 (18). https://doi.org/10.1523/JNEUROSCI.1436-24.2025. 

- Kensinger, Elizabeth A., and Daniel L. Schacter. 2006. “Processing Emotional Pictures and Words: Effects of Valence and Arousal.” _Cognitive, Affective, & Behavioral Neuroscience_ 6 (2): 110–26. https://doi.org/10.3758/CABN.6.2.110. 

- Khaligh-Razavi, Seyed-Mahdi, and Nikolaus Kriegeskorte. 2014. “Deep Supervised, but Not Unsupervised, Models May Explain IT Cortical Representation.” _PLOS Computational Biology_ 10 (11): e1003915. https://doi.org/10.1371/journal.pcbi.1003915. 

- Kok, Peter, Pim Mostert, and Floris P. de Lange. 2017. “Prior Expectations Induce Prestimulus Sensory Templates.” _Proceedings of the National Academy of Sciences_ 114 (39): 10473–78. https://doi.org/10.1073/pnas.1705652114. 

- Kollias, Dimitrios, and Stefanos Zafeiriou. 2020. “Exploiting Multi-CNN Features in CNN-RNN Based Dimensional Emotion Recognition on the OMG in-the-Wild Dataset.” arXiv:1910.01417. Preprint, arXiv, April 10. https://doi.org/10.48550/arXiv.1910.01417. 

30 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

- Konkle, Talia, and George Alvarez. 2023a. “Cognitive Steering in Deep Neural Networks via LongRange Modulatory Feedback Connections.” _Advances in Neural Information Processing Systems_ 36 (December): 21613–34. 

- Konkle, Talia, and George Alvarez. 2023b. “Cognitive Steering in Deep Neural Networks via LongRange Modulatory Feedback Connections.” In _Advances in Neural Information Processing Systems_ , edited by A. Oh, T. Naumann, A. Globerson, K. Saenko, M. Hardt, and S. Levine, vol. 36. Curran Associates, Inc. 

   - https://proceedings.neurips.cc/paper_files/paper/2023/file/444b09beab8438d4a58e9bc694dca 32a-Paper-Conference.pdf. 

- Kragel, Philip A., Marianne C. Reddan, Kevin S. LaBar, and Tor D. Wager. 2019. “Emotion Schemas Are Embedded in the Human Visual System.” _Science Advances_ 5 (7): eaaw4358. https://doi.org/10.1126/sciadv.aaw4358. 

- Krizhevsky, Alex, Ilya Sutskever, and Geoffrey E. Hinton. 2012. “ImageNet Classification with Deep Convolutional Neural Networks.” In _Advances in Neural Information Processing Systems_ , edited by F. Pereira, C. J. Burges, L. Bottou, and K. Q. Weinberger, vol. 25. Curran Associates, Inc. 

   - https://proceedings.neurips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c 45b-Paper.pdf. 

- Lamme, Victor A. F., and Pieter R. Roelfsema. 2000. “The Distinct Modes of Vision Offered by Feedforward and Recurrent Processing.” _Trends in Neurosciences_ 23 (11): 571–79. https://doi.org/10.1016/S0166-2236(00)01657-X. 

- Lang, Peter J., Margaret M. Bradley, Jeffrey R. Fitzsimmons, et al. 1998. “Emotional Arousal and Activation of the Visual Cortex: An fMRI Analysis.” _Psychophysiology_ 35 (2): 199–210. https://doi.org/10.1111/1469-8986.3520199. 

- LeCun, Yann, Yoshua Bengio, and Geoffrey Hinton. 2015. “Deep Learning.” _Nature_ 521 (7553): 436–44. https://doi.org/10.1038/nature14539. 

- Li, Shan, and Weihong Deng. 2022. “Deep Facial Expression Recognition: A Survey.” _IEEE Transactions on Affective Computing_ 13 (3): 1195–215. https://doi.org/10.1109/TAFFC.2020.2981446. 

- Li, Wen, and Andreas Keil. 2023. “Sensing Fear: Fast and Precise Threat Evaluation in Human Sensory Cortex.” _Trends in Cognitive Sciences_ 27 (4): 341–52. https://doi.org/10.1016/j.tics.2023.01.001. 

- Liu, Peng, Ke Bo, Yujun Chen, Andreas Keil, Mingzhou Ding, and Ruogu Fang. 2025. “Biologically Inspired Deep Neural Network Models for Visual Emotion Processing.” _bioRxiv_ , ahead of print. https://doi.org/10.1101/2025.10.20.683439. 

- Liu, Yuelu, Andreas Keil, and Mingzhou Ding. 2011. “Effects of Emotional Conditioning on Early Visual Processing: Temporal Dynamics Revealed by ERP Single‐trial Analysis.” _Human Brain Mapping_ 33 (4): 909–19. https://doi.org/10.1002/hbm.21259. 

- Maniquet, Tim, Hans Op de Beeck, and Andrea Ivan Costantino. 2024. “Recurrent Issues with Deep Neural Network Models of Visual Recognition.” Preprint, bioRxiv, April 10. https://doi.org/10.1101/2024.04.02.587669. 

- Miller, Earl K., and Jonathan D. Cohen. 2001. “An Integrative Theory of Prefrontal Cortex Function.” _Annual Review of Neuroscience_ 24 (Volume 24, 2001): 167–202. https://doi.org/10.1146/annurev.neuro.24.1.167. 

- Mollahosseini, Ali, Behzad Hasani, and Mohammad H. Mahoor. 2019. “AffectNet: A Database for Facial Expression, Valence, and Arousal Computing in the Wild.” _IEEE Transactions on Affective Computing_ 10 (1): 18–31. https://doi.org/10.1109/TAFFC.2017.2740923. 

- Moors, Agnes, Phoebe C. Ellsworth, Klaus R. Scherer, and Nico H. Frijda. 2013. “Appraisal Theories of Emotion: State of the Art and Future Development.” _Emotion Review_ 5 (2): 119– 24. https://doi.org/10.1177/1754073912468165. 

31 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

Moratti, Stephan, and Andreas Keil. 2009. “Not What You Expect: Experience but Not Expectancy Predicts Conditioned Responses in Human Visual and Supplementary Cortex.” _Cerebral Cortex_ 19 (12): 2803–9. https://doi.org/10.1093/cercor/bhp052. 

- Morris, J. S., K. J. Friston, C. Büchel, et al. 1998. “A Neuromodulatory Role for the Human Amygdala in Processing Emotional Facial Expressions.” _Brain_ 121 (1): 47–57. https://doi.org/10.1093/brain/121.1.47. 

- Mumford, Jeanette A., Benjamin O. Turner, F. Gregory Ashby, and Russell A. Poldrack. 2012. “Deconvolving BOLD Activation in Event-Related Designs for Multivoxel Pattern Classification Analyses.” _NeuroImage_ 59 (3): 2636–43. https://doi.org/10.1016/j.neuroimage.2011.08.076. 

- Öhman, Arne. 2005. “The Role of the Amygdala in Human Fear: Automatic Detection of Threat.” _Psychoneuroendocrinology_ , Stress, sensitisation and somatisation: A special issue in honour of Holger Ursin, vol. 30 (10): 953–58. https://doi.org/10.1016/j.psyneuen.2005.03.019. 

- Padmala, Srikanth, and Luiz Pessoa. 2008. “Affective Learning Enhances Visual Detection and Responses in Primary Visual Cortex.” Articles. _Journal of Neuroscience_ 28 (24): 6202–10. https://doi.org/10.1523/JNEUROSCI.1233-08.2008. 

- Panichello, Matthew F., and Timothy J. Buschman. 2021. “Shared Mechanisms Underlie the Control of Working Memory and Attention.” _Nature_ 592 (7855): 601–5. https://doi.org/10.1038/s41586-021-03390-w. 

- Pei, Guanxiong, Haiying Li, Yandi Lu, Yanlei Wang, Shizhen Hua, and Taihao Li. 2024. “Affective Computing: Recent Advances, Challenges, and Future Trends.” _Intelligent Computing_ 3 (January): 0076. https://doi.org/10.34133/icomputing.0076. 

- Pessoa, Luiz. 2008. “On the Relationship between Emotion and Cognition.” _Nature Reviews Neuroscience_ 9 (2): 148–58. https://doi.org/10.1038/nrn2317. 

- Pessoa, Luiz. 2009. “How Do Emotion and Motivation Direct Executive Control?” _Trends in Cognitive Sciences_ 13 (4): 160–66. https://doi.org/10.1016/j.tics.2009.01.006. 

- Pessoa, Luiz, and Ralph Adolphs. 2010. “Emotion Processing and the Amygdala: From a ‘low Road’ to ‘Many Roads’ of Evaluating Biological Significance.” _Nature Reviews Neuroscience_ 11 (11): 11. https://doi.org/10.1038/nrn2920. 

- Pham, Trung Quang, Teppei Matsui, and Junichi Chikazoe. 2023. “Evaluation of the Hierarchical Correspondence between the Human Brain and Artificial Neural Networks: A Review.” _Biology_ 12 (10): 1330. https://doi.org/10.3390/biology12101330. 

- Phelps, Elizabeth A. 2006. “Emotion and Cognition: Insights from Studies of the Human Amygdala.” _Annual Review of Psychology_ 57 (Volume 57, 2006): 27–53. https://doi.org/10.1146/annurev.psych.56.091103.070234. 

- Pourtois, Gilles, Didier Grandjean, David Sander, and Patrik Vuilleumier. 2004. 

   - “Electrophysiological Correlates of Rapid Spatial Orienting Towards Fearful Faces.” _Cerebral Cortex_ 14 (6): 619–33. https://doi.org/10.1093/cercor/bhh023. 

- Pourtois, Gilles, Antonio Schettino, and Patrik Vuilleumier. 2013. “Brain Mechanisms for Emotional Influences on Perception and Attention: What Is Magic and What Is Not.” _Biological Psychology_ , Specificity, Methodology and Psychopathology of Emotional Attention, vol. 92 (3): 492–512. https://doi.org/10.1016/j.biopsycho.2012.02.007. 

- Reynolds, John H., and David J. Heeger. 2009. “The Normalization Model of Attention.” _Neuron_ 61 (2): 168–85. https://doi.org/10.1016/j.neuron.2009.01.002. 

- Reynolds, John H., Tatiana Pasternak, and Robert Desimone. 2000. “Attention Increases Sensitivity of V4 Neurons.” _Neuron_ 26 (3): 703–14. https://doi.org/10.1016/S0896-6273(00)81206-4. 

- Roelfsema, Pieter R., and Floris P. de Lange. 2016. “Early Visual Cortex as a Multiscale Cognitive Blackboard.” _Annual Review of Vision Science_ 2 (October): 131–51. https://doi.org/10.1146/annurev-vision-111815-114443. 

32 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

Rotshtein, Pia, Mark P. Richardson, Joel S. Winston, et al. 2010. “Amygdala Damage Affects EventRelated Potentials for Fearful Faces at Specific Time Windows.” _Human Brain Mapping_ 31 (7): 1089–105. https://doi.org/10.1002/hbm.20921. 

- Sabatinelli, Dean, Margaret M. Bradley, Jeffrey R. Fitzsimmons, and Peter J. Lang. 2005. “Parallel Amygdala and Inferotemporal Activation Reflect Emotional Intensity and Fear Relevance.” _NeuroImage_ 24 (4): 1265–70. https://doi.org/10.1016/j.neuroimage.2004.12.015. 

- Sander, David, Didier Grandjean, Gilles Pourtois, et al. 2005. “Emotion and Attention Interactions in Social Cognition: Brain Regions Involved in Processing Anger Prosody.” _NeuroImage_ 28 (4): 848–58. https://doi.org/10.1016/j.neuroimage.2005.06.023. 

- Simonyan, Karen, and Andrew Zisserman. 2015. “Very Deep Convolutional Networks for LargeScale Image Recognition.” _arXiv:1409.1556 [Cs]_ , April 10. http://arxiv.org/abs/1409.1556. 

- Smith, Craig A., and Phoebe C. Ellsworth. 1985. “Patterns of Cognitive Appraisal in Emotion.” _Journal of Personality and Social Psychology_ (US) 48 (4): 813–38. https://doi.org/10.1037/0022-3514.48.4.813. 

- Smith, Craig A., and Richard S. Lazarus. 1993. “Appraisal Components, Core Relational Themes, and the Emotions.” _Cognition and Emotion_ (United Kingdom) 7 (3–4): 233–69. https://doi.org/10.1080/02699939308409189. 

- Smith, Ryan, and Richard D. Lane. 2015. “The Neural Basis of One’s Own Conscious and Unconscious Emotional States.” _Neuroscience & Biobehavioral Reviews_ 57 (October): 1–29. https://doi.org/10.1016/j.neubiorev.2015.08.003. 

- Sterzer, Philipp, Chris Frith, and Predrag Petrovic. 2008. “Believing Is Seeing: Expectations Alter Visual Awareness.” _Current Biology_ 18 (16): R697–98. https://doi.org/10.1016/j.cub.2008.06.021. 

- Summerfield, Christopher, and Tobias Egner. 2009. “Expectation (and Attention) in Visual Cognition.” _Trends in Cognitive Sciences_ 13 (9): 403–9. https://doi.org/10.1016/j.tics.2009.06.003. 

- Summerfield, Christopher, and Floris P. de Lange. 2014. “Expectation in Perceptual Decision Making: Neural and Computational Mechanisms.” _Nature Reviews Neuroscience_ 15 (11): 745–56. https://doi.org/10.1038/nrn3838. 

- Treue, Stefan, and Julio C. Martínez Trujillo. 1999. “Feature-Based Attention Influences Motion Processing Gain in Macaque Visual Cortex.” _Nature_ 399 (6736): 575–79. https://doi.org/10.1038/21176. 

- Vuilleumier, Patrik. 2005. “How Brains Beware: Neural Mechanisms of Emotional Attention.” _Trends in Cognitive Sciences_ 9 (12): 585–94. https://doi.org/10.1016/j.tics.2005.10.011. 

- Vuilleumier, Patrik, and Jon Driver. 2007. “Modulation of Visual Processing by Attention and Emotion: Windows on Causal Interactions between Human Brain Regions.” _Philosophical Transactions of the Royal Society B: Biological Sciences_ 362 (1481): 837–55. https://doi.org/10.1098/rstb.2007.2092. 

- Vuilleumier, Patrik, Mark P. Richardson, Jorge L. Armony, Jon Driver, and Raymond J. Dolan. 2004. “Distant Influences of Amygdala Lesion on Visual Cortical Activation during Emotional Face Processing.” _Nature Neuroscience_ 7 (11): 1271–78. https://doi.org/10.1038/nn1341. 

- Vuilleumier, Patrik, and Sophie Schwartz. 2001. “Emotional Facial Expressions Capture Attention.” _Neurology_ 56 (2): 153–58. https://doi.org/10.1212/WNL.56.2.153. 

- Wyatte, Dean, Tim Curran, and Randall O’Reilly. 2012. “The Limits of Feedforward Vision: Recurrent Processing Promotes Robust Object Recognition When Objects Are Degraded.” _Journal of Cognitive Neuroscience_ 24 (11): 2248–61. https://doi.org/10.1162/jocn_a_00282. 

- Yamins, D. L. K., H. Hong, C. F. Cadieu, E. A. Solomon, D. Seibert, and J. J. DiCarlo. 2014. “Performance-Optimized Hierarchical Models Predict Neural Responses in Higher Visual 

33 

bioRxiv preprint doi: https://doi.org/10.64898/2026.04.06.716704; this version posted April 8, 2026. The copyright holder for this preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under aCC-BY 4.0 International license. 

Cortex.” _Proceedings of the National Academy of Sciences_ 111 (23): 8619–24. https://doi.org/10.1073/pnas.1403112111. 

- Yang, Jingyuan, Qirui Huang, Tingting Ding, Dani Lischinski, Daniel Cohen-Or, and Hui Huang. 2023a. “EmoSet: A Large-Scale Visual Emotion Dataset with Rich Attributes.” _2023 IEEE/CVF International Conference on Computer Vision (ICCV)_ , 20326–37. https://doi.org/10.1109/ICCV51070.2023.01864. 

- Yang, Jingyuan, Qirui Huang, Tingting Ding, Dani Lischinski, Daniel Cohen-Or, and Hui Huang. 2023b. “EmoSet: A Large-Scale Visual Emotion Dataset with Rich Attributes.” arXiv:2307.07961. Preprint, arXiv, July 28. https://doi.org/10.48550/arXiv.2307.07961. 

- Yeo, Gerard C., and Desmond C. Ong. 2024. “Associations between Cognitive Appraisals and Emotions: A Meta-Analytic Review.” _Psychological Bulletin_ (US) 150 (12): 1440–71. https://doi.org/10.1037/bul0000452. 

- Yerkes, Robert M., and John D. Dodson. 1908. “The Relation of Strength of Stimulus to Rapidity of Habit-Formation.” _Journal of Comparative Neurology and Psychology_ 18 (5): 459–82. https://doi.org/10.1002/cne.920180503. 

- Zhang, Zhanpeng, Ping Luo, Chen Change Loy, and Xiaoou Tang. 2015. “Learning Social Relation Traits from Face Images.” arXiv:1509.03936. Preprint, arXiv, September 14. https://doi.org/10.48550/arXiv.1509.03936. 

34 

