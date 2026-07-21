# (2026) Human-like Affective Cognition in Foundation Models

**Source:** (2026) Human-like Affective Cognition in Foundation Models.pdf

---

## Page 1

Human-like Affective Cognition in Foundation
Models
Kanishk Gandhi1*, Zoe Lynch1, Jan-Philipp Fr¨anken2,
Kayla Patterson1, Sharon Wambu1, Tobias Gerstenberg2,
Desmond C. Ong3, Noah D. Goodman1,2
1*Computer Science, Stanford University, 450 Jane Stanford Way,
Stanford, 94305, CA, USA.
2Psychology, Stanford University, 450 Jane Stanford Way,
Stanford, 94305, CA, USA.
3Psychology, The University of Texas, 110 Inner Campus Drive,
Austin, 78712, TX, USA.
*Corresponding author(s). E-mail(s): kanishk.gandhi@stanford.edu;
Contributing authors: zlynch@stanford.edu; janphilipp.franken@gmail.com;
kpatterson@alumni.stanford.edu ; swambu@stanford.edu ; gerstenberg@stanford.edu ;
desmond.c.ong@gmail.com ; ngoodman@stanford.edu;
Abstract
Understanding emotions is fundamental to human interaction and experience,
and also for AI models that interact with people. Such understanding goes beyond
recognizing emotions from facial expressions or language; it involves reasoning
over how people subjectively make sense of their experienced situations given
their beliefs and goals, and integrating multiple sources of information. Start-
ing from psychological theory on affective cognition, we introduce a principled
evaluation framework for assessing such reasoning in AI models. Using this frame-
work, we generate 1,280 diverse scenarios systematically varying the relationships
between appraisals, emotions, expressions, and situation outcomes, and evaluated
the responses of three Large Language Models (GPT-4, Claude-3.5, Gemini-
1.5) and humans (N = 567). Our results show that these models tend to agree
with human intuitions, matching and in some cases exceeding interparticipant
agreement, and that all models’ performances increase using chain-of-thought
reasoning. This suggests that Large Language Models seem to have acquired a
conceptual understanding of, and are able to reason about, human emotions.
Keywords: Affective Cognition, Large Language Models, LLMs, Affective
Computing, Cognitive Science
1
arXiv:2409.11733v3  [cs.CL]  16 Feb 2026


## Page 2

1 Introduction
Having emotions is fundamental to being human, and our emotions are shaped by how
we view our experiences. For instance, consider Amy, a high school student who is
applying to college. She wants to attend a local state college, but her parents want her
to go to a private liberal arts college. If she is admitted to the private liberal arts college
and not the local state college, she is disappointed; but she would be happy if she gets
into the local state college. A friend who observes Amy’s disappointment and knows her
preferences can infer her rejection from the state college. Similarly another friend who
doesn’t know her preference but observes the outcome and her emotion may infer which
colleges she wanted to go to. This ability to understand others’ emotions in the context
of their mental states, known as affective cognition (Ong, Zaki, & Goodman, 2015;
Saxe & Houlihan, 2017), allows people to gain deeper insights into others’ thoughts
and experiences
(De Melo, Carnevale, Read, & Gratch, 2014; Houlihan, Kleiman-
Weiner, Hewitt, Tenenbaum, & Saxe, 2023; Wu, Baker, Tenenbaum, & Schulz, 2018),
fostering better connections and interactions. This fundamentally human capacity is
the ability that allows us to be understanding friends, empathetic counselors, and
compassionate partners.
Recent advances in foundation models (Achiam et al., 2023; Anthropic, 2024; Gem-
ini, 2023; Touvron et al., 2023) have led to AI becoming an increasing part of our
daily interactions (Bommasani et al., 2021; Demszky et al., 2023; Tamkin, Brundage,
Clark, & Ganguli, 2021). Indeed, recent statistics published by Anthropic (McCain et
al., 2025) and OpenAI (Chatterji et al., 2025; Phang et al., 2025) suggests that a small
percentage of conversations with Claude (about 3%) and chatGPT are affective in
nature—e.g., users seeking advice on relationships, career development, self-reflection,
managing loneliness. While this percentage may seem small, this translates to poten-
tially millions of affective conversations a day for these “general purpose” models; and
the numbers are likely higher for models labeled as “empathic” or “emotionally intel-
ligent” (e.g., Inflection’s Pi, Hume’s EVI), or personas built on top of general purpose
models. It is thus important to measure how well models understand people, includ-
ing our emotions. If AI assistants and companions do not understand the nuances
of common emotions such as sadness, joy, or frustration, they will be fundamentally
limited in their ability to connect with us (Picard, 2000). This raises an important
question: Can modern AI models understand emotions, making the same inferences
that humans do?
Crucially, emotion understanding goes beyond emotion recognition from faces
(facial expression recognition; Kleinsmith & Bianchi-Berthouze, 2012; Li & Deng,
2020; Shan, Gong, & McOwan, 2009), text (sentiment analysis; Medhat, Hassan, &
Korashy, 2014; Rathje et al., 2024; Zhang, Wang, & Liu, 2018), or other modalities
like voice. Conceptually, these emotion recognition tasks are perception tasks—they
attempt to recover some “ground truth” label solely from information only in the
stimulus. By contrast, people employ more complex types of reasoning to understand
emotions. For instance, affective cognition requires a rich, causal intuitive theory of
how emotions are related to mental states and contexts (Doan, Ong, & Wu, 2025;
Ong, Zaki, & Goodman, 2019; Saxe & Houlihan, 2017). Central to connecting mental
states with emotions is an understanding of how people evaluate events based on their
2


## Page 3

x
Appraisal 2
Outcome
Emotion
Expression
Causal Template
Variables
Appraisal 1
Amy, is a high school student applying to 
college. Amy completes and submits her 
college applications. Amy believes she can 
control the outcome of her college admissions 
by crafting a quality application. Amy wants to 
go to a local state college, and hopes that she 
is admitted. She also applied to a private 
liberal arts college to appease her parents, 
but she dislikes the private liberal arts college 
and does not want to attend. Amy gets into 
the private liberal arts college and not to the 
local state college.  Amy feels disappointed.
Example Scenario
Fig. 1 Causal Template for generating affective scenarios and an Example Scenario.
(left) The causal template used to generate stimuli for testing affective inferences. Experiments 1a
and 1b use the left four text-only causal factors, while Experiments 2a and 2b use all five factors
including the Expression factor (represented as an image). (right) An example scenario generated
with our causal template for affective inferences. The color of the text indicates the causal variable
associated with it.
prior expectations, beliefs and desires, a process called cognitive appraisal (Ellsworth
& Scherer, 2003; Scherer, Schorr, & Johnstone, 2001; Skerry & Saxe, 2015; Weiner,
1985; Yeo & Ong, 2024). For example, when Amy receives news of her rejection from
the local state college, her emotions reflect not just the outcome but her interpreta-
tion of the outcome. This appraisal is critical to how a situation leads to an emotion.
Given the same outcome, a different appraisal can lead to a different emotion—if Amy
thought she would certainly get into the college on a second try, she would not feel as
disappointed, and instead would feel motivated to try again. In this example, Amy’s
emotions were a consequence of her appraising the outcome (a rejection) as being
incongruent with her goals. There are many other dimensions of appraisal which could
lead to other nuances in her emotions. For example, if Amy thought that she had a
great deal of influence over the outcome of the college admission process and that it
was mostly her application that caused a rejection, she might feel regret, or frustration.
We do not yet know the extent to which recent AI models, especially founda-
tion models, can reason about human emotions. Some recent work has investigated
the ability of LLMs like GPT-4 to infer people’s emotions and appraisals from
vignettes (Broekens et al., 2023; Tak & Gratch, 2023, 2024; Yongsatianchot, Torshizi,
& Marsella, 2023; Zhan, Ong, & Li, 2023), and finding some promising initial results.
However, these studies lack a principled way of (i) defining a taxonomy of different
types of affective inferences, and (ii) systematically benchmarking those inferences.
To address these gaps, we propose a framework to generate structured tests for
affective cognition, and compare how recent AI models perform. Our items are built
synthetically, extending techniques for evaluating language models using language
models (Fr¨anken et al., 2024; Gandhi, Fr¨anken, Gerstenberg, & Goodman, 2024; Perez,
Huang, et al., 2022; Perez, Ringer, et al., 2022). Our approach starts with a strong
theoretical grounding, which allows us to exhaustively define various types of infer-
ences within affective cognition. We then use a systematic approach to isolate each of
these inferences, and procedurally generate a range of items to test them. The proce-
dural generation of stimuli has 3 stages: 1) Defining an abstract causal template. 2)
Populating the template using language models. 3) Composing the stimuli from the
populated causal template.
3


## Page 4

In Stage 1, we start by specifying an abstract causal graph for affective reasoning
(Figure 1), grounded in psychological theory (Ong et al., 2019; Saxe & Houlihan, 2017),
which describes some of the causal relationships between outcomes, appraisals, and
emotions (Ellsworth & Scherer, 2003; Yeo & Ong, 2024). In Experiments 1a and 1b,
we use a four-factor causal model (Figure 1, “Causal Template”) where an outcome
and two appraisals cause an emotion. In Experiments 2a and 2b, we add a fifth
factor to the causal model, such that the emotion causes an expression; we create
images depicting a facial expression, and which allows us to test multimodal models.
For the example scenario in Figure 1, we have a background story (applying to
college) and what the person’s goals and expectations are (e.g., Amy wants to attend
the local state college, and that application and results are well within her control).
When the outcome occurs (Amy gets rejected from the local state college), the person
would make certain appraisals (e.g., she experienced an outcome incongruent with
her goal (goal-congruency); and she perceives that she had control over the outcome).
According to cognitive appraisal theory, these specific appraisals should lead her to feel
an emotion (like disappointed). In this particular example, and in Experiments 1a
and 2a, we consider two appraisal dimensions (goal-congruency and perceived control),
while in Experiments 1b and 2b, we consider safety and expectedness (see Table 1).
These two sets of experiments serve as proofs-of-concept, and this paradigm can be
extended to cover a wider range of appraisals and emotions (e.g., Yeo & Ong, 2024
identified 47 distinct appraisal dimensions and how they relate to 63 different emotions
and affective states).
Table 1 Appraisal Dimensions and Assigned Emotion Labels. Appraisal
dimensions and their corresponding emotion labels assignment prior to collecting human
judgments, based on theory. ✓indicates a positive value for the appraisal dimension and
✗indicates a negative value. The left table shows the two appraisals studied in Experiments
1a and 2a, while the right table shows the appraisals in Experiments 1b and 2b.
Goal
Control
Emotion
Safety
Expectedness
Emotion
Congruency
(from theory)
(from theory)
✓
✓
Joyful
✓
✓
Relieved
✗
✓
Frustrated
✗
✓
Resigned
✓
✗
Grateful
✓
✗
Surprised
✗
✗
Disappointed
✗
✗
Devastated
In Stage 2, once this causal template is specified, we prompt a language model
to generate values for these factors. We first have the language model generate a
background story, such as: “Amy is a high school student applying to college.” We
then use the model to generate text corresponding to two (binary) values for each of
the appraisal dimensions. For goal-congruence, the model generates “Amy wants to go
to a local state college and not a private liberal arts college.” and its complementary
value “Amy wants to go to a private liberal arts college and not a local state college.”
For perceived control over the outcome, the model would generate “Amy thinks that
she can influence the decision of the admission process.” and “Amy thinks that the
admission process is mostly random and she has little influence over the decision.” We
4


## Page 5

also have the model generate two possible outcomes, “Amy is accepted at the local
state college and rejected from the private liberal arts college” and “Amy is accepted
at the private liberal arts college and rejected from the local state college.”. Based on
the specific appraisal factors and appraisal theory, we define four emotion values that
the person in the story might feel (Table 1) — for example, “Amy feels disappointed”.
Finally, to create the image stimuli we use in Experiments 2a and 2b, we match each
emotion with facial expressions that are defined using Facial Action Units (Ekman &
Friesen, 1978) and rendered in Unity (Figure 1).
Importantly, the language model does not have to make affective inferences while
generating values for the variables in the template; it simply needs to follow prompts
to populate the causal template.
Finally, in Stage 3, we compose the text completions to produce individual stimuli
items. Populating the abstract causal template for a single background story yields
eight possible filled-out scenarios (2 values for each of 2 appraisals, and 2 values for
the outcome; the emotion is determined from these other variables). The Example
Scenario in Figure 1 is one out of eight possible scenarios for the same background
story (e.g., applying to college).
Now given a four-factor causal graph, we can define (4-choose-1 =) 4 inference
tasks, where three of the factors are observed and one is inferred. Specifically, we can
query for the emotion (given the two appraisals and outcome); query for the first or
second appraisal (given the other appraisal, outcome, and emotion); or query for the
outcome (given both appraisals and the emotion).
For a given background story (e.g., applying to college), we have 8 scenarios, which
could be applied to each of the 4 inference tasks, producing 32 stimuli items. For
example, we can construct a query for an inference of goal (“Which college did Amy
want to go to?”), by specifying the outcome (“Amy got accepted at the local state
college, and was rejected from the liberal arts college”), the appraisal of perceived con-
trol (“Amy thought that she could influence the decision of the admission process.”),
and the emotion (“Amy was joyful.”).
This procedure allows us to flexibly and systematically query for various types of
affective inference tasks. This pipeline for generating stimuli allows us to scalably and
flexibly generate high quality stimuli that are novel. It offers a diverse set of tasks
for testing affective reasoning and includes closely matched controls for these tasks,
ensuring reliable measurements of capabilities (Frank, 2023a).
One natural extension, as mentioned above, is to multimodal reasoning. We include
FACS-based generated facial expressions as another possible observed factor in all the
tasks, resulting in another 32 (multimodal) questions, which we test in Experiments
2a and 2b (Note that we do not query the models for emotional expression, but simply
provide it as another observed factor).
Using the same approach, in Experiment 1b and 2b, we generate stimuli based on
two additional appraisal dimensions: the safety and expectedness of the outcome (see
Figure 2 bottom). As with the stimuli for the appraisal dimensions of goal-congruence
and perceived-control, these scenarios are crafted such that the outcome itself is not
inherently safe or expected. Instead, these are determined based on the context and
the interpretation of the person in the story.
5


## Page 6

Amy, is a high school student 
applying to college. Amy 
completes and submits her 
college applications.
Amy wants to go to a local state 
college, and hopes that she is 
admitted. She also applied to a 
private liberal arts college  to 
appease her parents, but  does 
not want to attend it.
Amy believes she can control 
the outcome of her college 
admissions by crafting a quality 
application.
Amy is admitted to the private 
liberal arts college and not the 
local state college. 
How does Amy feel?
Context
Expression
Appraisal 1
Appraisal 2
Outcome
Emotion
Goal Congruence and Control Over Outcome
Amy, is a high school student 
applying to college. Amy 
completes and submits her 
college applications.
Which college did Amy want to 
go to?
Amy believes she can control 
the outcome of her college 
admissions by crafting a quality 
application.
Amy is admitted to the private 
liberal arts college and not the 
local state college.
Context
Expression
Appraisal 1
Appraisal 2
Outcome
Amy feels joyful.
Emotion
Sarah, a solo hiker, is 
navigating a challenging trail 
on a mountain. Sarah starts her 
ascent. 
Did Sarah expect to encounter 
adverse weather events?
Sarah thinks that it would be 
dangerous if she encountered 
fog and can safely navigate if 
she encounters snowfall.
Sarah encounters snowfall when 
reaching the summit.
Sarah is surprised.
Context
Expression
Appraisal 1
Appraisal 2
Outcome
Emotion
Safety and Expectedness of Outcome
Goal Congruence and Control Over Outcome
👀
👀
🤔
👀
👀
👀
👀
🤔
🤔
👀
👀
👀
👀 
Inferred
Observed
👀 
Inferred
Observed
👀 
Inferred
Observed
Sarah, a solo hiker, is 
navigating a challenging trail 
on a mountain. Sarah starts her 
ascent. 
Sarah expects the weather to be 
pleasant.
What did Sarah think about her 
safety if she encountered 
snowfall or fog?
Sarah encounters fog.
Sarah feels devastated.
Context
Expression
Appraisal 1
Appraisal 2
Outcome
Emotion
Safety and Expectedness of Outcome
👀
👀
🤔
👀
👀 
Inferred
Observed
Fig. 2 Example stimuli used for our experiments. We can generate stories to ask questions
about different affective inferences. Each factor in the causal model, such as appraisals, outcomes,
emotions, or expressions, can be varied to elicit different responses. We define different Facial Action
Units (Ekman & Friesen, 1978) for different emotions to generate expressions using Unreal Engine.
Note that these stimuli are representative of Experiment 2a (top) and 2b (bottom); the corresponding
stimuli for Experiments 1a and 1b are text-only, and so would not have the facial expression.
For Experiments 1a and 2a, we generate 10 background stories for the goal-
congruence and perceived-control appraisal dimensions; and for Experiments 1b and
2b, we generate 10 background stories for the safety and expectedness dimensions. For
each of these stories, we generate 32 text-only stimuli items (Experiments 1a and 1b)
and 32 multimodal stimuli items (Experiments 2a and 2b), for a total of 1280 stimuli
items.
6


## Page 7

2 Results
2.1 Validating our stimuli with human judgments
We first establish the validity of our stimuli. Although our procedural generation
pipeline assigns labels to stimuli, based on psychological theory, these may not exactly
match human intuition. For instance, people have variability in the intuitive theories
they use to make these judgments (Ong et al., 2019; Saxe & Houlihan, 2017), and psy-
chological theory may not capture such diversity. Thus, we collected responses from
567 native English-speaking participants, averaging about 20 responses per question 1,
for each of the 1280 questions in our stimuli set. The stimuli are presented in the form
of a story, and a question with multiple answer options (Figure 2). To measure the
agreement among participants, we check if an individual’s choice matches the major-
ity’s choice, calculated without including that individual’s response. The agreement
score is the average agreement-with-majority-choice across all participants. For the
inference task where participants predict emotions, participants choose between four
options; random choice would cause the agreement score to be 25%. On other infer-
ence tasks, participants choose between two options; random choice would cause the
agreement score to be 50%.
We find that the agreement between participants is high, and significantly above
what would be expected from random choice (see Figure 4, right-most bars). In
Experiment 1a (with goal-conduciveness × control scenarios), participants had high
agreement when inferring the emotion (63.97%, 95% CI = [61.65, 66.29]) given the
outcome and appraisals. People also showed high agreement inferring the outcome
(91.67%, 95% CI = [90.66, 92.68]), the goal-conduciveness appraisal (86.09% [84.82,
87.36]), and the control appraisal (72.79%, 95% CI = [70.47, 75.11]). These results
replicate when instead we considered a different set of appraisals in Experiment 1b
(safety × expected): with high rates of agreement for emotion (69.38, 95% CI= [67.06,
71.70]), outcome (76.10%, 95%CI = [74.54, 77.66]), safety (70.31% [68.63, 71.99]), and
expectedness (75.30%, 95% CI = [73.06, 77.54]). In Experiment 2a and 2b, stimuli
items also had facial expressions, and agreement patterns were also very similar. That
is, participants can successfully integrate facial expressions with their contexts to make
inferences about emotions, outcomes and appraisals. The high agreement shows that
our stimuli are able to elicit coherent human judgments, validating their effectiveness.
We compared these judgments with the a priori labels assigned to the stimuli
by our procedural generation pipeline (see Figure 3, compare blue and yellow). We
compute label-participant agreement by comparing the labels to the choices that the
majority of participants made for each question. Our findings indicate that participants
generally predict each other’s judgments more accurately than the labels assigned
a priori during the generation of the stimuli; in other words, the inter-participant
agreement is usually the same as or higher than the participant-label agreement.
For example, for emotion inference in safety and expectedness stimuli items, inter-
participant agreement is at 69.38% [67.67, 71.09], compared to a label-participant
agreement of 41.49% [39.66, 43.32] (t=18.05, p <0.001). This finding underscores the
1https://osf.io/ajkt6, https://osf.io/7bxwk
7


## Page 8

(a) Participant Agreement Scores for Stimuli with Appraisals of 
 Goal Congruence and Control Over Outcomes
Inferences Without Expressions
Inferences With Expressions
Interparticipant Agreement
Participant agreement with apriori labels
(b) Participant Agreement Scores for Stimuli with Appraisals of 
 Safety and Expectedness of Outcomes
Inferences Without Expressions
Inferences With Expressions
Interparticipant Agreement
Participant agreement with apriori labels
chance
chance
chance
chance
Fig. 3 Comparison of Inter-participant and Pre-assigned Label Agreement Scores. Inter-
participant agreement scores compared to the agreement scores between participant responses and
labels assigned to stimuli prior to collecting human responses. Error bars represent 95% Confidence
Intervals.
importance of gathering and using participant labels in these subjective affective infer-
ence tasks. Using psychological theories to assign labels is useful for generating diverse
stimuli, but these may diverge substantially from how laypeople judge these stimuli.
Now, given that we have high inter-participant agreement for our stimuli items, we
can now reliably test if model predictions align with human intuitions. For the rest of
the results presented below, we use the modal participant response (i.e., the majority
answer) as the label that we calculate model agreement with, rather than the a priori
label used by our pipeline.
2.2 Analyzing affective cognition in foundation models
To test if contemporary foundation models show human-like patterns in affec-
tive reasoning, we prompt three models: claude-3.5-sonnet2, gpt-4-turbo3, and
gemini-1.5-pro4. We use two prompting strategies: 0-shot and a zero-shot chain-
of-thought (CoT), 0-shot-cot (Kojima, Gu, Reid, Matsuo, & Iwasawa, 2022; Wei et
al., 2022). We use the most deterministic setting for inference, setting temperature to
0. Additional details and analysis, including specific prompts, other hyperparameter
settings and analysis of model and participant response distributions, are available
in the supplementary materials. We compare model responses to the choices that the
majority of participants made.
2claude-3.5-sonnet-20240620
3gpt-4-turbo-1106
4gemini-1.5-pro-002
8


## Page 9

🤔
👀
👀
👀
(a) Emotion Inference without Expressions
🤔
👀
👀
👀
👀
👀
🤔
👀
👀
(c) Emotion Inference with Expressions
🤔
👀
👀
👀
Goal Congruence & Control Over Outcome
Safety & Expectedness of Outcome
Outcome
Appraisal 1
Appraisal 2
Emotion
Expression
Goal Congruence & Control Over Outcome
Safety & Expectedness of Outcome
Outcome
Appraisal 1
Appraisal 2
Emotion
Expression
👀 
Inferred
Observed
👀 
Inferred
Observed
👀 
Inferred
Observed
👀 
Inferred
Observed
Chance
Chance
Chance
Chance
(d) Outcome Inference with Expressions
(b) Outcome Inference without Expressions
Fig. 4 Agreement Analysis for Emotion and Outcome Inference. Inter-participant agree-
ments and model-participant agreements for inferring the (a) emotions and (b) outcomes from the
context in Experiments 1a and 1b. (c) and (d): The corresponding agreements for Experiments 2a
and 2b, when models and participants were also presented with expressions. Error bars represent 95%
Confidence Intervals.
9


## Page 10

In Experiment 1a, when inferring emotions (Figure 4 a) from outcomes and
appraisals, we find that model-participant agreement is comparable to interpartici-
pant agreement and significantly above chance. For example, claude has an agreement
score of (62.31 %, 95% CI=[60.24, 64.38]). Agreements scores are generally higher for
the goal-conduciveness × control stimuli we used in Experiment 1a, compared to the
safety × expectedness stimuli in Experiment 1b.
The foundation models are also excellent at inferring outcomes from emotions and
appraisals (79.06%, 95% CI = [77.01, 81.12]). For example, for gpt-4, agreement is at
80.88% [78.83, 82.93] (t=14.03, p <0.001) for goal-conduciveness × control stimuli and
90.38% [88.85, 91.91] for safety × expectedness stimuli. claude, gemini and gpt-4
with CoT again exceed inter-participant agreement scores for the safety × expected-
ness stimuli; for instance, the agreement scores for claude at 89.20% [87.59, 90.80] is
greater than inter-participant agreement at 76.10% [73.89, 78.31] (t=9.41, p <0.001).
In general, inter-participant agreement for outcomes in Experiment 1a is higher than
in Experiment 1b, and so we only observe models being “better” than humans in
Experiment 1b.
For the task of inferring appraisals from emotions and outcomes (see Figure 5),
we see that model-participant agreement scores are highest for predicting the goal-
congruency, gpt-4 has a score of 88.61% [86.26, 90.96] compared to an interparticipant
agreement score of 86.09% [84.30, 87.88]. Similarly, for perceived control, claude has
an agreement score of 86.75% [84.98, 88.52] which is higher than the interparticipant
agreement of 72.79% [70.47, 75.11] (t=9.37, p <0.001). Model agreement scores are
much lower for inferring the appraisal of the safety: for instance, claude has an agree-
ment score of 60.93% [58.39, 63.47] compared to the interparticipant agreement of
70.31% [67.93, 72.69] (t=5.28, p < 0.001).
2.2.1 Incorporating facial expression information.
When also provided with facial expression stimuli in Experiments 2a and 2b, the agree-
ment scores for emotion inference generally increase (a linear model shows that access
to facial expressions increases agreement with human majority responses by 8.9 per-
centage points (β = 8.9, 95% CI: [7.5,10.3]). For outcome inference (see Figure 6), we
see that claude is unable to incorporate facial expressions in making inferences about
the goal × control stimuli, with the agreement score for outcome inference dropping
from 87.01% [85.26, 88.76] to 73.14% [70.84, 75.45] with expressions. In contrast, given
facial expressions, gpt-4 exceeds or matches the scores for inter-participant agree-
ment; for example, for safety × expectedness gpt-4 scores 89.57% [87.98, 91.16] while
interparticipant agreement is at 83.58% [81.65, 85.51], (t=4.70, p <0.001). Model par-
ticipant agreement scores also fall when the task is to infer appraisals from expressions
instead of emotions, suggesting that while models are able to integrate expressions
when making inferences for outcome and emotions, they struggle while trying to infer
appraisals.
2.2.2 The role of reasoning.
We find overall that models prompted with chain-of-thought do much better than
those without – a linear model comparing CoT vs. vanilla prompting across all models
10


## Page 11

👀
👀
🤔
👀
(a) Goal Congruence of Outcome Appraisal Inference
Chance
👀 
Inferred
Observed
Outcome
Appraisal 1
Appraisal 2
Emotion
👀
👀
👀
🤔
(b) Control over Outcome Appraisal Inference
Chance
👀
👀
🤔
👀
(c) Safety of Outcome Appraisal Inference
Chance
Outcome
Appraisal 1
Appraisal 2
Emotion
👀
👀
👀
🤔
(d) Expectedness of Outcome Appraisal Inference
Chance
👀 
Inferred
Observed
👀 
Inferred
Observed
👀 
Inferred
Observed
Fig. 5 Agreement Analysis for Inferring Appraisals from Context without Expressions.
Interparticipant agreements and model participant agreements for inferring the appraisals from the
context, for (a, b) Experiment 1a and (c, d) Experiment 1b. Error bars represent 95% Confidence
Intervals.
shows that CoT increases agreement with human majority responses by 6.9 percent-
age points (β = 0.069, 95% CI: [0.062, 0.075]) – suggesting that reasoning plays a
crucial role in improving affective judgment (see Figure 7 for an example reasoning
trace). Across different conditions and models, we find that prompting the model to
reason (“thinking step-by-step”) before picking an answer increases agreement scores
11


## Page 12

(a) Goal Congruence of Outcome Appraisal Inference
👀
🤔
👀
👀
👀 
�� 
Inferred
Observed
Outcome
Appraisal 1
Appraisal 2
Emotion
Expression
(b) Control over Outcome Appraisal Inference
👀
👀
👀
🤔
Chance
(c) Safety of Outcome Appraisal Inference
👀
🤔
👀
👀
Outcome
Appraisal 1
Appraisal 2
Emotion
Expression
Chance
(d) Expectedness of Outcome Appraisal Inference
👀
👀
👀
🤔
Chance
Chance
👀 
Inferred
Observed
👀 
Inferred
Observed
👀 
Inferred
Observed
👀 
Inferred
Observed
Fig. 6 Agreement Analysis for Inferring Appraisals from Context with Expressions.
Interparticipant agreements and model participant agreements for inferring the appraisals from the
context, for (a, b) Experiment 2a and (c, d) Experiment 2b. Error bars represent 95% Confidence
Intervals.
with human modal judgments. For example, for gpt-4, mean agreement for goal-
conduciveness inferences rises from 71.14% [68.79, 73.49] to 88.61% [86.96, 90.26]
(t=11.94, p < 0.001), for claude, mean agreement rises from 69.39% [67.00, 71.78] to
88.05% [75.19, 79.53] (t=11.94, p < 0.001), and for gemini from 74.00% [71.73, 76.27]
to 79.73% [77.65, 81.81] (t=3.64, p < 0.001). Step-by-step reasoning helps the model
arrive at inferences that are more aligned with human judgments in many but not all
12


## Page 13

x
Amy, is a high school student applying to college. Amy 
completes and submits her college applications. Amy 
believes she can control the outcome of her college 
admissions by crafting a quality application. Amy wants to 
go to Stanford, and hopes that she is admitted. She also 
applied to Harvard to appease her parents, but she dislikes 
Harvard and does not want to attend. 
Which college did Amy get into?
(a)
Harvard
(b)
Stanford
Example Question
Example Reasoning (GPT-4V)
Let's think step by step:
- Amy applied to both Stanford and Harvard.
- She wants to go to Stanford and does not want to attend 
Harvard.
- The expression on the person's face in the image is one of 
disappointment or sadness.
- Since Amy dislikes Harvard and the expression indicates a 
negative emotion, it suggests that the outcome is not what 
she desired.
- Therefore, it is likely that Amy got into Harvard, which is 
the outcome she did not want.
x
Sarah, a solo hiker, is navigating a challenging trail on a 
mountain. Sarah expects the weather to be pleasant. 
Sarah starts her ascent. Sarah encounters snowfall when 
reaching the summit. 
What did Sarah think about her safety if she encountered 
snowfall or fog? Choose the most likely answer.
(a)
Sarah thought that it would be dangerous if she 
encountered fog and could safely navigate if she 
encountered snowfall.
(b)
Sarah thought that it would be dangerous if she 
encountered snowfall and could safely navigate if 
she encountered fog.
Example Question
Example Reasoning (GPT-4V)
Let's think step by step:
- The story mentions that Sarah expected the weather to 
be pleasant but encountered snowfall at the summit.
- The image shows a person with an expression that could 
be interpreted as concern or worry.
- Based on the expression, it seems that Sarah did not 
expect the snowfall and is likely concerned about her 
safety.
- The question asks us to choose between whether Sarah 
thought it would be dangerous to encounter fog or 
snowfall.
- Since the story mentions snowfall and the expression 
indicates concern, it is reasonable to infer that Sarah might 
have thought encountering snowfall could be dangerous.
Fig. 7 Examples of GPT-4 Reasoning Traces Using 0-Shot Chain-of-Thought Prompt-
ing. Examples of a reasoning traces from gpt-4 elicited with chain-of-thought prompting, by asking
the model to ‘think step-by-step.’
conditions (Figure 4, Figure 5). The improvement in affective judgment through rea-
soning may mean that as the reasoning capabilities of foundation models improve, so
will their affective judgments.
Finally, to evaluate models’ ability to capture human response distributions, we
sampled 20 responses per model at temperature 1.0 and compared them to human
response distributions using Wasserstein distance, with a uniform distribution serv-
ing as a baseline. The analysis (see Figure 12 and Figure 13) revealed that models
performed above chance across all tasks, with strongest performance in predicting out-
comes, followed by emotions, while showing more variation in appraisal judgments.
Models excelled particularly at goal-conduciveness × control judgments and had more
difficulty with safety × expectedness judgments. But overall, these results suggesting
that foundation models can effectively represent not just modal human responses but
full response distributions (see Supplement for more details).
Overall, we find that across our Experiments, foundation models’ agreement rates
with human modal judgments are high, and match, or sometimes exceed, inter-
participant agreements. It does seem that these foundation models are able to integrate
information from outcomes, appraisals, emotions, and facial expressions to reason
about each of these in turn.
3 Discussion
As AI models continue to advance and become more “intelligent,” we need to define
key facets of intelligence, and construct rigorous tests for these facets. Here we build
from psychological theory to define inferences related to affective cognition—reasoning
over and understanding people’s emotions. Importantly, this goes beyond perception
13


## Page 14

(e.g., detecting sentiment from text, or emotions from facial expressions alone), and
involves integrating information from multiple cues (e.g., mental state appraisals, situ-
ation outcomes). We propose a framework for systematically constructing a benchmark
evaluation dataset for affective cognition in foundation models. Our automated evalu-
ation pipeline allowed us to generate diverse and naturalistic stimuli that can be used
to systematically, scalably evaluate affective reasoning.
Using these stimuli, we established human ground-truth, gathering enough judge-
ments for each question to establish the modal human response and agreement of the
human population with this response. We then performed a comprehensive evalua-
tion of several foundation models (GPT-4, Gemini-1.5, Claude-3), with and without
chain-of-thought prompting. We found that foundation models tend to agree with
human intuitions, matching or in some cases even exceeding inter-participant agree-
ment (predicting the modal human judgments better than the average human did.
Importantly, we found that chain-of-thought reasoning improved performance, sug-
gesting that improvement in reasoning capabilities of foundation models could lead
to even more accurate affective judgments. Finally, we found that some dimensions of
appraisal, such as goal congruency, were more salient for participants and models com-
pared to others, such as inferences about perceived control over the outcome. Overall,
this suggests that foundation models have acquired the ability to infer emotions in a
nuanced way and understand how they influence beliefs and behavior.
Here we only tested a small number of appraisals, and a small number of back-
ground stories (20 stories, which expand to 1280 stimuli items), but our framework is in
principle generalizable to a larger number of appraisals (e.g., Yeo & Ong, 2024 identi-
fied 47 in the literature) and a potentially infinite number of scenarios. Our framework
is also generalizable to other types of social and affective cognition (Fr¨anken et al.,
2024; Gandhi et al., 2024). More such research is needed to determine the robustness
and limits of these models’ mentalizing capabilities.
A number of foundational cognitive questions are raised by these findings: How
is affective cognition represented mechanistically in the weights and activations of
the neural network? What types of data are needed for the emergence of emotional
reasoning capablities? How are these capabilities influenced by post-training alignment
versus pretraining on large data? Discovering the origins of affective representations
in language models could provide insights and research directions for understanding
human cognition (Frank, 2023b).
Our work also hints at an interesting future where foundation models might be
better at understanding the emotions and mental states of others than the average
person. We could also envision a future where these models’ affective capabilities
could be used to develop new approaches for mental health support and intervention
(Hecht et al., 2025; Lee, Suh, Zhan, Li, & Ong, 2024; Sharma, Lin, Miner, Atkins,
& Althoff, 2023; Zhan et al., 2024)—already, people are finding responses generated
by foundation models as more empathic than even those written by trained crisis
responders (Ong, Goldenberg, Inzlicht, & Perry, 2025; Ovsyannikova, de Mello, &
Inzlicht, 2025). However, models like these can also introduce potential risks (Moore et
al., 2025), especially if misused to manipulate or deceive. It is essential to be proactive
about measuring capabilities and mitigating the associated risks (Ong, 2021). Further
14


## Page 15

research around evaluating these models and an ongoing discussion around the ethics
of affective computing will be crucial as foundation models continue to improve.
This work presents a rigorous methodology for evaluating affective cognition in
both humans and AI systems. We find a broad correspondence between human and
model predictions. This points to exciting future directions in using foundation models
for interactions requiring emotional understanding.
Acknowledgements.
We would like to thank Michael Bernstein, and the members
of the Computation and Cognition Lab for their support and feedback. This work
was supported by the Stanford Human-Centered Artifical Intelligence (HAI) - Google
grant. This material is based upon work supported by the National Science Foundation
under Award No. 2443038 to D.C.O., and an Expeditions Grant, Award Number
(FAIN) 1918771 to N.D.G. Any opinions, findings and conclusions or recommendations
expressed in this material are those of the author(s) and do not necessarily reflect the
views of the National Science Foundation.
15


## Page 16

4 Materials and Methods
The complete methods and materials for reproduction are available at:
https://github.com/kanishkg/affective-cog
Here we detail the main prompts and parameters used for evaluation.
Prompts and Parameters
For inference, we use a temperature of 0.0 and a top-p value of 0.9. For GPT-4, we used
gpt-4-1106. For Claude-3.5, we used claude-3.5-sonnet-20240620. For Gemini, we
used gemini-1.5-pro-002. Please see Figure 8 for the 0-shot prompt, and Figure 9
for the 0-shot chain-of-thought prompt that was used for the text-only stimuli. The
prompts for the stimuli with expression are presented in Figure 10, for 0-shot and
Figure 11 for 0-shot chain-of-thought.
Distributional distance between responses
To evaluate how well models capture the full distribution of human responses rather
than just the most common answer, we generated 20 responses from each model using
temperature 1.0 to create response distributions. We then measured the similarity
between model and human response distributions using Wasserstein distance (also
known as Earth Mover’s distance). For comparison, we calculated the Wasserstein
distance between human responses and a uniform distribution as a baseline measure
of chance performance (“chance” in Figure 12 and Figure 13). When models refused
to answer at temperature 1.0, we assigned equal probability to all possible responses
to maintain consistent distribution sizes.
By sampling multiple model responses and comparing their distributions to human
answers using Wasserstein distance, we found models performed best at predicting
outcomes (Figure 12b), followed by emotions (Figure 12b), and showed most variation
in appraisal judgments (Figure 13). While performing above chance across all tasks,
models were particularly good at understanding goal congruence and control, but
struggled more with safety and expectedness judgments. These findings suggest that
in addition to representing human modal responses, foundation models can represent
human response distributions too.
Prompt for 0-shot Evaluation
Answer
the
questions
based on the
story.
Choose
your
answer
from
the
options
provided.
Provide
your
best
guess
from
the
options
provided.
Answer
precisely
in the
following
format:
A:<option >. <answer >
Example: A:a. cat
Fig. 8 Prompt for 0-shot Evaluation. This prompt is used as the system prompt for 0-shot
evaluation of the language model.
16


## Page 17

Prompt for 0-shot CoT Evaluation
Answer
the
questions
based on the
story.
Choose
your
answer
from
the
options
provided.
Reason
step by step
before
answering
in
‘Thought: Let ’s think
step by step:’.
Provide
your
best
guess
from
the
options
provided.
Answer
in the
following
format:
Thought: Let ’s think
step by step:
<thought >
A:<option >. <answer >
Example: A:a. cat
Fig. 9 Prompt for 0-shot CoT Evaluation. This prompt is used as the system prompt for 0-
shot CoT evaluation of the language model.
Prompt for 0-shot Evaluation with Multimodal Stimuli
Answer
the
questions
based on the
story
and the
image.
The
image
shows
the
expression
that
the
person
in the
story
feels.
Only
pay
attention
to the
expression
and
not the person ’s physical
appearance .
Choose
your
answer
from
the
options
provided.
Provide
your
best
guess
from
the
options
provided.
Answer
precisely
in the
following
format:
A:<option >. <answer >
Example: A:a. cat
Fig. 10 Prompt for 0-shot Evaluation. This prompt is used as the system prompt for 0-shot
evaluation of the model when using stimuli with facial expressions.
References
Achiam, J., Adler, S., Agarwal, S., Ahmad, L., Akkaya, I., Aleman, F.L., . . . others
(2023). Gpt-4 technical report. arXiv preprint arXiv:2303.08774, ,
Anthropic (2024). Claude 2. https://www.anthropic.com/news/claude-2. (Accessed:
2024-02-29)
Bommasani, R., Hudson, D.A., Adeli, E., Altman, R., Arora, S., von Arx, S., . . . others
(2021). On the opportunities and risks of foundation models. arXiv preprint
arXiv:2108.07258, ,
Broekens, J., Hilpert, B., Verberne, S., Baraka, K., Gebhard, P., Plaat, A. (2023).
Fine-grained affective processing capabilities emerging from large language mod-
els. 2023 11th international conference on affective computing and intelligent
interaction (acii) (pp. 1–8).
17


## Page 18

Prompt for 0-shot CoT Evaluation with Multimodal Stimuli
Answer
the
questions
based on the
story
and the
image.
The
image
shows
the
expression
that
the
person in the
story
feels.
Only
pay
attention
to the
expression
and
not the person ’s physical
appearance .
Choose
your
answer
from
the
options
provided.
Reason
step by step
before
answering
in
‘Thought: Let ’s think
step by step:’.
Provide
your
best
guess
from
the
options
provided.
Answer
in the
following
format:
Thought:
Let ’s think
step by step:
<thought >
A:<option >. <answer >
Example: A:a. cat
Fig. 11 Prompt for 0-shot CoT Evaluation. This prompt is used as the system prompt for 0-
shot CoT evaluation of the model when using stimuli with facial expressions.
🤔
👀
👀
👀
(a) Emotion Inference
(b) Outcome Inference
Goal Congruence & Control Over Outcome
Safety & Expectedness of Outcome
Outcome
Appraisal 1
Appraisal 2
Emotion
👀 
Inferred
Observed
Chance
Chance
👀
🤔
👀
👀
Goal Congruence & Control Over Outcome
Safety & Expectedness of Outcome
👀 
Inferred
Observed
Chance
Chance
Fig. 12 Distributional Analysis of Responses for Emotion and Outcome Predictions
Wasserstein Distance (or Earthmover’s distance) between model responses and human responses for
emotion inference and outcome inference.
Chatterji, A., Cunningham, T., Deming, D.J., Hitzig, Z., Ong, C., Shan, C.Y., Wad-
man, K.
(2025).
How people use chatgpt (Tech. Rep.).
National Bureau of
Economic Research.
De Melo, C.M., Carnevale, P.J., Read, S.J., Gratch, J.
(2014).
Reading people’s
minds from emotion expressions in interdependent decision making. Journal of
18


## Page 19

👀
👀
🤔
👀
(a) Goal Congruence of Outcome Appraisal Inference
Chance
👀 
Inferred
Observed
👀
👀
👀
🤔
(b) Control over Outcome Appraisal Inference
Chance
(c) Safety of Outcome Appraisal Inference
(d) Expectedness of Outcome Appraisal  Inference
Outcome
Appraisal 1
Appraisal 2
Emotion
👀 
Inferred
Observed
👀
👀
🤔
👀
Chance
👀 
Inferred
Observed
👀
👀
👀
🤔
Chance
Outcome
Appraisal 1
Appraisal 2
Emotion
👀 
Inferred
Observed
Fig. 13 Distributional Analysis of Responses for Appraisal Predictions Wasserstein Dis-
tance (or Earthmover’s distance) between model responses and human responses for different
appraisal predictions.
personality and social psychology, 106(1), 73,
Demszky, D., Yang, D., Yeager, D.S., Bryan, C.J., Clapper, M., Chandhok, S., . . .
others
(2023).
Using large language models in psychology.
Nature Reviews
Psychology, 2(11), 688–701,
Doan, T., Ong, D.C., Wu, Y.
(2025).
Emotion understanding as third-person
appraisals: Integrating appraisal theories with developmental theories of emo-
tion. Psychological Review, 132(1), 130–153,
Ekman, P., & Friesen, W.V. (1978). Facial action coding system. Environmental
Psychology & Nonverbal Behavior, ,
Ellsworth, P.C., & Scherer, K.R. (2003). Appraisal processes in emotion.
Frank, M.C. (2023a). Baby steps in evaluating the capacities of large language models.
Nature Reviews Psychology, 2(8), 451–452,
Frank, M.C.
(2023b).
Openly accessible llms can help us to understand human
cognition. Nature Human Behaviour, 7(11), 1825–1827,
19


## Page 20

Fr¨anken, J.-P., Gandhi, K., Qiu, T., Khawaja, A., Goodman, N.D., Gerstenberg, T.
(2024). Procedural dilemma generation for evaluating moral reasoning in humans
and language models.
Gandhi, K., Fr¨anken, J.-P., Gerstenberg, T., Goodman, N. (2024). Understanding
social reasoning in language models with language models. Advances in Neural
Information Processing Systems, 36, ,
Gemini, T. (2023). Gemini: a family of highly capable multimodal models. arXiv
preprint arXiv:2312.11805, ,
Hecht, C.A., Ong, D.C., Clapper, M., Jones, M., Demszky, D., Yang, D., . . . Yeager,
D.S. (2025). Using large language models in behavioral science interventions:
Promise & risk. Behavioral Science & Policy, 11(1), 1–9,
Houlihan, S.D., Kleiman-Weiner, M., Hewitt, L.B., Tenenbaum, J.B., Saxe, R.
(2023). Emotion prediction as computation over a generative theory of mind.
Philosophical Transactions of the Royal Society A, 381(2251), 20220047,
Kleinsmith, A., & Bianchi-Berthouze, N. (2012). Affective body expression perception
and recognition: A survey. IEEE Transactions on Affective Computing, 4(1),
15–33,
Kojima, T., Gu, S.S., Reid, M., Matsuo, Y., Iwasawa, Y. (2022). Large language mod-
els are zero-shot reasoners. Advances in neural information processing systems,
35, 22199–22213,
Lee, Y.K., Suh, J., Zhan, H., Li, J.J., Ong, D.C.
(2024).
Large language models
produce responses perceived to be empathic. 2024 12th international conference
on affective computing and intelligent interaction (acii).
Li, S., & Deng, W.
(2020).
Deep facial expression recognition: A survey.
IEEE
transactions on affective computing, 13(3), 1195–1215,
McCain, M., Linthicum, R., Lubinski, C., Tamkin, A., Huang, S., Stern, M.,
. . . Ganguli, D.
(2025).
How people use claude for support, advice, and
companionship. Retrieved from https://www.anthropic.com/news/how-people-
use-claude-for-support-advice-and-companionship
20


## Page 21

Medhat, W., Hassan, A., Korashy, H.
(2014).
Sentiment analysis algorithms and
applications: A survey. Ain Shams engineering journal, 5(4), 1093–1113,
Moore, J., Grabb, D., Agnew, W., Klyman, K., Chancellor, S., Ong, D.C., Haber, N.
(2025). Expressing stigma and inappropriate responses prevents llms from safely
replacing mental health providers. Proceedings of the 2025 acm conference on
fairness, accountability, and transparency (pp. 599–627).
Ong, D.C. (2021). An ethical framework for guiding the development of affectively-
aware artificial intelligence.
2021 9th international conference on affective
computing and intelligent interaction (acii).
Ong, D.C., Goldenberg, A., Inzlicht, M., Perry, A. (2025). Ai-generated empathy:
Opportunities, limits, and future directions.
Ong, D.C., Zaki, J., Goodman, N.D. (2015). Affective cognition: Exploring lay theories
of emotion. Cognition, 143, 141–162,
Ong, D.C., Zaki, J., Goodman, N.D. (2019). Computational models of emotion infer-
ence in theory of mind: A review and roadmap. Topics in cognitive science,
11(2), 338–357,
Ovsyannikova, D., de Mello, V.O., Inzlicht, M. (2025). Third-party evaluators perceive
ai as more compassionate than expert humans. Communications Psychology,
3(1), 4,
Perez, E., Huang, S., Song, F., Cai, T., Ring, R., Aslanides, J., . . . Irving, G.
(2022). Red teaming language models with language models. arXiv preprint
arXiv:2202.03286, ,
Perez, E., Ringer, S., Lukoˇsi¯ut˙e, K., Nguyen, K., Chen, E., Heiner, S., . . . others
(2022). Discovering language model behaviors with model-written evaluations.
arXiv preprint arXiv:2212.09251, ,
Phang, J., Lampe, M., Ahmad, L., Agarwal, S., Fang, C.M., Liu, A.R., . . . others
(2025). Investigating affective use and emotional well-being on chatgpt. arXiv
preprint arXiv:2504.03888, ,
21


## Page 22

Picard, R.W. (2000). Affective computing. MIT press.
Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C.E., Van Bavel,
J.J. (2024). Gpt is an effective tool for multilingual psychological text analysis.
Proceedings of the National Academy of Sciences, 121(34), e2308950121,
Saxe, R., & Houlihan, S.D. (2017). Formalizing emotion concepts within a bayesian
model of theory of mind. Current opinion in Psychology, 17, 15–21,
Scherer, K.R., Schorr, A., Johnstone, T.
(2001).
Appraisal processes in emotion:
Theory, methods, research. Oxford University Press.
Shan, C., Gong, S., McOwan, P.W. (2009). Facial expression recognition based on
local binary patterns: A comprehensive study. Image and vision Computing,
27(6), 803–816,
Sharma, A., Lin, I.W., Miner, A.S., Atkins, D.C., Althoff, T.
(2023).
Human–ai
collaboration enables more empathic conversations in text-based peer-to-peer
mental health support. Nature Machine Intelligence, 5(1), 46–57,
Skerry, A.E., & Saxe, R. (2015). Neural representations of emotion are organized
around abstract event features. Current biology, 25(15), 1945–1954,
Tak, A.N., & Gratch, J. (2023). Is GPT a computational model of emotion? 2023
11th international conference on affective computing and intelligent interaction
(acii).
Tak, A.N., & Gratch, J. (2024). GPT-4 emulates average-human emotional cognition
from a third-person perspective. 2024 12th international conference on affective
computing and intelligent interaction (acii).
Tamkin, A., Brundage, M., Clark, J., Ganguli, D. (2021). Understanding the capabil-
ities, limitations, and societal impact of large language models. arXiv preprint
arXiv:2102.02503, ,
Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi, A., Babaei, Y., . . . others
(2023). Llama 2: Open foundation and fine-tuned chat models. arXiv preprint
arXiv:2307.09288, ,
22


## Page 23

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Xia, F., Chi, E., . . . others (2022).
Chain-of-thought prompting elicits reasoning in large language models. Advances
in Neural Information Processing Systems, 35, 24824–24837,
Weiner, B. (1985). An attributional theory of achievement motivation and emotion.
Psychological Review, 92(4), 548,
Wu, Y., Baker, C.L., Tenenbaum, J.B., Schulz, L.E. (2018). Rational inference of
beliefs and desires from emotional expressions. Cognitive science, 42(3), 850–
884,
Yeo, G.C., & Ong, D.C.
(2024).
Associations between cognitive appraisals and
emotions: A meta-analytic review. Psychological Bulletin, 150(12), 1440-1471,
Yongsatianchot, N., Torshizi, P.G., Marsella, S. (2023). Investigating large language
models’ perception of emotion using appraisal theory. 2023 11th international
conference on affective computing and intelligent interaction workshops and
demos (aciiw) (pp. 1–8).
Zhan, H., Ong, D.C., Li, J.J. (2023). Evaluating subjective cognitive appraisals of emo-
tions from large language models. Findings of the association for computational
linguistics: Emnlp 2023 (pp. 14418–14446).
Zhan, H., Zheng, A., Lee, Y.K., Suh, J., Li, J.J., Ong, D.C. (2024). Large language
models are capable of offering cognitive reappraisal, if guided. 1st conference on
language modeling (colm).
Zhang, L., Wang, S., Liu, B. (2018). Deep learning for sentiment analysis: A survey.
Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery, 8(4),
e1253,
23


