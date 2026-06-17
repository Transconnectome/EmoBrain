# (2022) Emotions as computations

**Source:** (2022) Emotions as computations.pdf

---

## Page 1

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
Available online 24 November 2022
0149-7634/© 2022 Elsevier Ltd. All rights reserved.
Emotions as computations☆ 
Aviv Emanuel a,b,*, Eran Eldar a,b,* 
a Department of Psychology, Hebrew University of Jerusalem, Jerusalem 9190501, Israel 
b Department of Cognitive and Brain Sciences, Hebrew University of Jerusalem, Jerusalem 9190501, Israel   
A R T I C L E  I N F O   
Keywords: 
Emotion 
Mood 
Computational modeling 
Reinforcement learning 
Reward 
A B S T R A C T   
Emotions ubiquitously impact action, learning, and perception, yet their essence and role remain widely debated. 
Computational accounts of emotion aspire to answer these questions with greater conceptual precision informed 
by normative principles and neurobiological data. We examine recent progress in this regard and find that 
emotions may implement three classes of computations, which serve to evaluate states, actions, and uncertain 
prospects. For each of these, we use the formalism of reinforcement learning to offer a new formulation that 
better accounts for existing evidence. We then consider how these distinct computations may map onto distinct 
emotions and moods. Integrating extensive research on the causes and consequences of different emotions 
suggests a parsimonious one-to-one mapping, according to which emotions are integral to how we evaluate 
outcomes (pleasure & pain), learn to predict them (happiness & sadness), use them to inform our (frustration & 
content) and others’ (anger & gratitude) actions, and plan in order to realize (desire & hope) or avoid (fear & 
anxiety) uncertain outcomes.   
1. Introduction 
Emotional states ubiquitously impact action, perception and 
learning. Through these influences and others, emotions are thought to 
have played a crucial role throughout evolution in increasing the sur­
vivability of our species (Darwin, 2015; Nesse and Ellsworth, 2009). 
Conversely, when emotions malfunction, they can have debilitating 
consequences for the individual. Indeed, emotional disturbances play 
key roles in a wide range of mental disorders, such as depression, bipolar 
disorder, borderline personality disorder, phobias, and other anxiety 
disorders. These disorders, however, differ substantially from one 
another in the types and timescales of emotions they involve (Greenberg 
et al., 2003; Hazlett et al., 2021; Matsunaga et al., 2008; Miyamoto et al., 
2013; Regier et al., 2013; Sobocki et al., 2006; Regier et al., 2013; 
Seligman, 1971; Tsanas et al., 2016; Carpenter & Trull, 2013; Fernandez 
& Johnson, 2016; Houben & Kuppens, 2020; Keltner & Kring, 1998). It is 
thus not an exaggeration to say that without a thorough understanding 
of emotions, we cannot hope to fully understand how human cognition 
functions or dysfunctions. Nevertheless, despite decades of emotion 
research, the literature remains rife with disagreement, even on basic 
questions such as what emotional states are, what causes them, and what 
are their roles (Adolphs et al., 2019; Ekman et al., 1987; Frijda, 1993; 
Lench et al., 2011; Moors et al., 2013; Parkinson, 1997; Russell, 1980, 
2003; Russell and Barrett, 1999; Scherer, 2005). 
At the same time, advances in computational cognitive science have 
given rise to a new understanding of how people form evaluations, and 
how these evaluations influence actions and physiological responses 
(Baker et al., 2009; Friston, 2009; Montague et al., 1996; Shenhav et al., 
2017; Tobler et al., 2007; Westbrook et al., 2020). Critically, evalua­
tions, action tendencies and physiological responses are precisely what 
most emotion theorists accept as central constituents of emotions 
(Ellsworth, 2013; Frijda, 1993; Lazarus and Lazarus, 1991; Moors et al., 
2013; Parkinson, 1997; Scherer, 2009a). Somewhat surprisingly, how­
ever, in studying these functions computational cognitive science has 
rarely considered emotions. It thus stands to reason that both emotion 
research and computational cognitive science can benefit a great deal 
from integrating their respective insights into a coherent theory. 
Emotion research provides theoretical frameworks for conceptualizing 
emotions, and empirical knowledge on the evaluations and behavioral 
responses that emotions entail. Conversely, computational cognitive 
science provides quantitative tools for linking between perceptual input, 
its evaluation, and ensuing behavior, in a manner that is constrained by 
normative principles and neurobiological data. The goal of this paper is 
to facilitate an integration between these two closely related, yet largely 
☆The authors are supported by NIH grants R01MH124092 and R01MH125564, ISF grant 1094/20 and US-Israel BSF grant 2019801 
* Corresponding authors at: Department of Psychology, Hebrew University of Jerusalem, Jerusalem 9190501, Israel. 
E-mail addresses: aviv.emanuel@mail.huji.ac.il (A. Emanuel), eran.eldar@mail.huji.ac.il (E. Eldar).  
Contents lists available at ScienceDirect 
Neuroscience and Biobehavioral Reviews 
journal homepage: www.elsevier.com/locate/neubiorev 
https://doi.org/10.1016/j.neubiorev.2022.104977 
Received 14 July 2022; Received in revised form 26 October 2022; Accepted 22 November 2022   


## Page 2

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
2
independent, fields. 
Luckily, we do not need to start from scratch. An increasing number 
of researchers have begun to lay foundations for a computational 
cognitive science of emotions. Broadly, these efforts have taken one of 
three approaches. The first aims to explain how experiences of emotions 
(i.e., feelings) arise, specifically, by classifying patterns of interoceptive 
and exteroceptive sensations that correspond with past exemplars of 
each feeling (Barrett, 2017; Seth and Friston, 2016). Researchers taking 
this approach often consider specific feelings to be too variable across 
individuals and cultures for them to be systematically characterized. The 
second approach aims to explain how emotions simplify action selection 
and inferences about the environment, specifically by constraining the 
set of probable states and actions to those that are congruent with the 
present emotion (Bach and Dayan, 2017; Huys and Renz, 2017). Re­
searchers taking this approach view emotions as heuristics that are 
evoked due to lack of information or cognitive resources, and which do 
not necessarily constitute veridical representations. They thus have 
relatively little to say about what emotions might represent about the 
environment and oneself. 
We therefore focus here on a third approach, which aims to under­
stand what computations about the environment and oneself emotions 
represent. This approach draws from non-computational theories that 
view emotions as constituted, in whole or in part, from appraisals – a set 
of cognitive judgments concerning the satisfaction of one’s needs by the 
environment (Clore and Ortony, 2000; Ellsworth, 2013; Frijda, 1986, 
1993, p. 19; Lazarus, 1991; Lazarus and Lazarus, 1991; Moors, 2013; 
Moors et al., 2013; Nussbaum, 2004; Reisenzein, 1995; Solomon, 1988). 
Researchers taking this approach have begun to replace the plethora of 
traditional appraisal dimensions, such as pleasantness, goal relevance, 
agency, and controllability, to name just a few, with a more parsimo­
nious set of computations. 
In what follows, we examine this literature through the lens of the 
computational framework of reinforcement learning.1 Our examination 
reveals three classes of proposed computations: computations concern­
ing expected reward (Eldar et al., 2016; Joffily and Coricelli, 2013), 
computations concerning the effectiveness of actions in obtaining 
reward (Bennett et al., 2021), and computations concerning uncertain 
future reward (Hagen, 1991; Peters et al., 2017). In each case, we pro­
pose modifications of previous suggestions that may more parsimoni­
ously account for existing evidence. We then consider how well these 
different classes of computations cohere with one another, and whether 
together they could offer a comprehensive computational account of 
emotion. First, however, we begin by considering the significance to 
emotions of a concept that all the computations we identify are predi­
cated on – the concept of reward. 
2. Reward in machines and humans 
2.1. The computational concept of reward 
In reinforcement learning, a reward function specifies to what degree 
different states and actions are of value to the agent and should thus be 
pursued, and to what degree they are harmful and should thus be 
avoided. Correspondingly, the goal of a reinforcement learning agent is 
to maximize its expected cumulative reward: 
E
[
rt + γrt+1 + γ2rt+2 + γ3rt+3 + …
]
(2.1.1)  
where t denotes the present time step, and γ is a discount rate between 
0 and 1 that serves to discount future rewards. In this expected sum, 
rewards may also be negative (r < 0) in which case they are often 
referred to as ‘punishment’. The agent typically does not know in 
advance which available options are most rewarding. To learn this, the 
agent needs to try them out and observe the reward associated with 
each. Thus, through trial and error, it can come to choose options that 
maximize its expected cumulative reward. 
2.2. Reward as pleasure and pain 
In humans, reward does not only reinforce choices but also has he­
donic value. This has led psychologists (Frijda, 2001a, 2001b) philoso­
phers (Helm, 2002), and even computational scientists (Sutton and 
Barto, 2018; Turing, 1969) to converge on the idea that reward is rep­
resented in humans by pleasure and pain. As an example, consider how 
remarkably similar the following phenomenological analysis of pleasure 
is to the computational definition of reward (Frijda, 2001a, 2001b): 
“The core of affective experience, whatever its guise, is its evaluative 
nature. Affect introduces value in a world of factual perceptions and 
sensations. It creates preferences, manifest or experienced palatability 
and aversiveness of stimuli, and behavioral priorities other than as are 
based on habit strength. Pleasure is good, and pain is bad, and so are their 
objects.” 
Like reward and punishment, pleasure is primarily evoked by expe­
riences that promote our well-functioning, such as consuming food, 
performing something well or achieving a goal, whereas pain is inflicted 
by experiences that harm us (Frijda, 2001a, 2001b). The goal of maxi­
mizing expected cumulative pleasure is thought to guide our behavior 
(Bentham, 1838; Mellers et al., 1999). And to know how pleasurable an 
experience is going to be, we normally first need to try it out (e.g., when 
tasting new food). 
This correspondence between pleasure and reward is further 
underscored by empirical findings. Like pleasure, the reward function 
that guides human decisions adapts to homeostatic needs (e.g., eating is 
less pleasurable when we are not hungry; Keramati and Gutkin, 2014) 
and changing goals (e.g., winning a game is less pleasurable when we do 
not aim to win; Juechems and Summerfield, 2019). Moreover, outcomes 
that for most people constitute reward are less rewarding to people who 
suffer from an inability to feel pleasure (i.e., anhedonia; Huys et al., 
2013), and more rewarding under the influence of pleasure-enhancing 
opioids (van Steenbergen et al., 2019). 
However, though they lie at the core of emotional experiences, 
pleasure and pain are not themselves considered emotions. Rather, they 
are primary evaluative processes, to which emotions are in some way 
secondary (Frijda, 2001a, 2001b; Jacobson, 2021; Price, 2000). To un­
derstand precisely in what way, we inquire what computations about 
reward emotions may represent. 
3. Computation of expected reward 
Recent work has argued that emotional states represent mismatches 
between actual and expected rewards (Eldar et al., 2016; Joffily and 
Coricelli, 2013), often referred to as ‘reward prediction errors’. To un­
derstand why representing these errors can be useful, it is helpful to 
consider their role in reinforcement learning. 
3.1. Value learning 
A reinforcement learning problem (Sutton and Barto, 2018) is often 
operationalized by assuming that each state s the agent can occupy may 
be associated with a different amount of reward r. The value of a state 
(denoted V(s)), however, includes not only this immediate reward but 
also the expected reward associated with all future states that follow s: 
V(s) ≡E
[
rt + γrt+1 + γ2rt+2 + γ3rt+3 + …
⃒⃒st = s
]
(3.1.1) 
A popular algorithm for learning the values of different states relies 
1 Though we use here the formalism of reinforcement learning to describe 
computations, note these can also be described using the formalism of ‘active 
inference’ (Friston et al., 2016). 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 3

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
3
on what are typically referred to as temporal-difference prediction er­
rors (Sutton and Barto, 2018): 
δt = rt + γ̂V t(st+1) −
̂V t(st)
(3.1.2)  
where ̂Vt denotes value as it is estimated at time step t. Prediction errors 
are computed in this way since the value of each state st should equal, on 
average, the immediate reward obtained in it, rt, plus the discounted 
value of the succeeding state, st+1. Once we compute these prediction 
errors, value learning simply consists of using them to update existing 
value estimates: 
̂V t+1(st) = ̂V t(st) + ηδt
(3.1.3)  
where η is a learning rate between 0 and 1, which need not be fixed. 
Bayesian inference dictates that the update should be smaller (i.e., η will 
be lower) the more confident we are in our existing value estimate 
relative to how reliably we think the observed reward is associated with 
the present state (Mathys et al., 2011). 
A large body of cognitive science research indicates that humans and 
animals employ value learning (Daw and O’Doherty, 2014; Kable and 
Glimcher, 2009; Levy and Glimcher, 2012; Montague and Berns, 2002; 
Padoa-Schioppa, 2011). For example, many brain imaging studies have 
shown that activation in specific brain areas, such as the ventromedial 
prefrontal cortex and ventral striatum, is correlated with learned values 
(Bartra et al., 2013; Levy and Glimcher, 2012; O’Reilly, 2020). More­
over, early foundational work in primates (Schultz et al., 1997) showed 
that brainstem dopaminergic neurons signal the reward prediction er­
rors defined in Eq. (3.1.2). Though in some instances people may not 
learn values as described above, but rather relative preferences among 
sets of states (Bennett et al., 2021; Shteingart and Loewenstein, 2014), 
value learning in one form or another remains a key building block of 
any comprehensive account of human learning and decision making. 
3.2. Emotion as change in value 
Empirical work has shown that positive reward prediction errors are 
associated with positive emotions, and negative reward prediction er­
rors (i.e., disappointments) with negative emotions (Mellers et al., 1997; 
Rutledge et al., 2014). The relationship between emotional state and 
reward prediction errors has also been demonstrated outside the lab, in 
the impact of real world outcomes such as sports matches and student 
exams on mood (Otto and Eichstaedt, 2018; Villano et al., 2020). 
But is it the prediction error per se (δ) that evokes emotional state, or 
is it the magnitude of the change in value (i.e., ηδ in Eq. 3.1.3)? Intui­
tively, changes in value may be the more likely cause since surprising 
outcomes that change our future expectations (high η; e.g., a good exam 
score revealing that our abilities are better than we thought) seem more 
emotionally meaningful than surprises that we consider to be chance 
events (low η; e.g., a good exam score due to a grading error). In the 
studies mentioned above, changes in value were mostly not measured, at 
least not in a way that was dissociable from reward prediction errors. A 
recent study, however, decoupled these two quantities by introducing 
trial-to-trial changes in reward magnitude that impacted only reward 
prediction errors and not expected values (Blain and Rutledge, 2020). 
Subjects’ self-reports during the task suggested that emotional state is 
primarily driven by changes in value (ηδ). 
3.3. Emotional state as cumulative change in value 
Emotional states may persist for seconds, hours, weeks or even 
months. Extension in time endows them with two key properties. First, 
rather than constituting a response to a single specific event, enduring 
emotional states accumulate the impact of multiple events. This cumu­
lative property has long been theoretically postulated (Mendl et al., 
2010; Nettle and Bateson, 2012; Parducci, 1995; Ruckmick, 1936; Webb 
et al., 2019) and has also been empirically demonstrated over small 
timescales (Rutledge et al., 2014). This suggests a formulation of 
emotional state as cumulative change in value: 
MV
t+1 = (1 −λ)
( ηδt + ληδt−1 + λ2ηδt−2 + λ3ηδt−3 + …
)
(3.3.1)  
where λ ∈[0, 1] serves to discount value updates made longer ago. This 
sum, which extends infinitely into the past with diminishing weights, 
can be continuously estimated using the following recursive update rule: 
̂M
V
t+1 = ̂M
V
t +
(
1 −λ
)( ηδt −
̂M
V
t
)
(3.3.2) 
This construal of an enduring emotional state is intuitively summa­
rized by saying that we are in a positive emotional state when reward is 
becoming generally more available to us, and in a negative emotional 
state when the availability of reward is decreasing. 
Though the computation of change in the general availability of 
reward can, and likely is, made using different algorithms, a useful 
property of the formula presented above is that the setting of λ modu­
lates the two properties that are thought to distinguish emotions and 
moods, namely, how long the emotional state lasts and whether it 
constitutes a response to a specific event (Ekman, 1999; Ketai, 1975; 
Morris, 2012; Schnurr, 1989). With λ = 0, the emotional state only re­
flects the very last change in value, and the impact of a change only lasts 
one time step. The closer λ is to 1, the more equal are the weights of older 
and newer changes in value, and consequently, each individual value 
change has a longer lasting impact on emotional state. Thus, different 
settings of λ offer a continuum of possibilities for modeling emotional 
state, from an instantaneous emotion to a long-lasting mood. 
3.4. The role of enduring emotional states 
According to our formulation, an instantaneous emotion corresponds 
to an individual change in value and has no extension in time. Thus, it is 
most parsimonious to assume that its role is to execute or signal the 
value update. But what role does an enduring emotional state serve? 
This question brings us to the second property enabled by extension in 
time. Empirical work indicates that enduring emotional states tend to 
generalize the information that evoked them (Eldar et al., 2016) via the 
operation of an emotion-congruent bias (Clore, 1992; Eldar and Niv, 
2015; Lerner and Keltner, 2000; Michely et al., 2020; Slovic et al., 2007; 
Vinckier et al., 2018). Having been evoked by a series of positive value 
updates, an enduring positive emotional state may make subsequent 
outcomes seem better than they normally seem, and thus lead to further 
positive value updates. For example, winning a wheel-of-fortune draw 
can improve people’s emotional state and positively enhance values 
learned from subsequent outcomes for a set of unrelated slot machines 
(Eldar and Niv, 2015). In this way, the emotional state generalizes the 
positive outcome obtained from one source of reward (i.e., the 
wheel-of-fortune draw) by incorporating it into the values of other, 
subsequently sampled, sources of reward (i.e., the slot machines). 
In this example, generalization is irrational because the outcomes of 
the wheel of fortune draw and of playing the slot machines are mutually 
independent. However, in ecological settings, changes in reward avail­
ability may often be linked across time and across different sources of 
reward. As an example of a link between consecutive time steps (i.e., 
trends), consider how when spring arrives, the availability of food 
doesn’t change overnight, but rather, it increases gradually, which 
means that an initial increase predicts further increases. As an example 
of a link between different sources of reward, consider how a change of 
season may make multiple types of food, water, and shelter synchro­
nously more abundant. Similarly, in social animals, success in obtaining 
one type of reward (e.g., gathering food) can increase the individual’s 
social status, and thus increase their access to other types of reward (e.g., 
sexual partners). 
In each of these cases, individual rewards are probabilistically 
determined, and therefore value can only be estimated up to some 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 4

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
4
approximation error. But these estimates will be more accurate if we 
take into account correlations across sources of reward and across time. 
This can be achieved by biasing each individual value update towards 
the recently typical update, that is, in accordance with the emotional 
state: 
̂V t+1(st) = ̂V t(st) + ηδt +
(
1 −η
) ̂M
V
t
(3.4.1) 
This emotion-biased value update can in fact be mathematically 
derived as the optimal equation for inferring the location of a moving 
object from a sequence of noisy observations, with value corresponding 
to the object’s location and emotional state to its velocity (Eldar et al., 
2016). The idea is that in inferring the value of a specific source of 
reward, an unbiased agent only considers rewards already obtained 
from that source, and therefore neglects global changes in expected 
reward. Conversely, an emotion-biased agent informs its specific value 
estimates with the recent global trend. 
4. Computation of action evaluation 
Reward depends not only on the states a reinforcement learning 
agent occupies, but also on the actions the agent chooses to take. 
Correspondingly, the second class of computations that have been sug­
gested to be represented by emotional states comprise evaluations of 
how effective actions are in obtaining reward (Bennett et al., 2021; 
Kurzban et al., 2013). Thus, we next consider how agents evaluate their 
own actions and accordingly adjust their action-selection policy. 
4.1. Learning how to obtain reward 
In reinforcement learning, the expected reward associated with 
taking action a in state s is defined as the action’s value, Q: 
Q(a, s) ≡E
[
rt + γrt+1 + γ2rt+2 + γ3rt+3 + …
⃒⃒at = a, st = s
]
(4.1.1) 
There is a close correspondence between values of actions and values 
of states, in that the latter equals a weighted sum of the former: 
V(s) ≡
∑
a
π(a|s)Q(a, s)
(4.1.2)  
where π(a|s) is the agent’s policy, that is, the probability it will take 
action a in state s. Consequently, the relative effectiveness of an action in 
obtaining reward can be represented as the advantage (A) it confers 
above the value of the state in which it was taken: 
Aat|st ≡Q(at, st) −V(st)
(4.1.3) 
A rational agent should always strive to eliminate advantage, since 
negative advantage (i.e., A < 0) means that the evaluated action is 
disadvantageous and should thus be excluded from the policy, whereas 
positive advantage (i.e., A > 0) means that alternative disadvantageous 
actions are unnecessarily included in the policy. Indeed, eliminating 
advantage is a useful learning algorithm in various machine learning 
applications (Baird, 1994), and is consistent with how humans often 
adjust their behavior when learning by trial and error (Bennett et al., 
2021; Palminteri et al., 2015; Solomyak et al., 2022). 
Advantage is typically estimated based on a reward, rt, that was 
received following action at: 
̂Aat|st = rt + V(st+1) −V(st)
(4.1.4) 
In this, advantage closely resembles a reward prediction error 
(compare with Eq. 3.1.2). However, meaningful differences between 
these two quantities can be observed once we re-express advantage as a 
function of the values of chosen (at) and alternative (̃a) actions: 
Aat|st
=
Q(at, st) −
∑
a
π(a|, st)Q(a, st)
=
∑
̃a∕=at
π(̃a|, st)(Q(a, st) −Q(̃at, st))
(4.1.5) 
This formulation exposes that advantage concerns the relative dif­
ference between the values of chosen and unchosen actions. Conse­
quently, computations of advantage and reward prediction error differ 
substantially in cases where the agent finds out that an action it did not 
choose is either more or less valuable than it previously estimated. 
As an illustration, imagine you are standing in line to buy tickets for 
the theatre. You choose one of two alternative queues and then find out 
that the other queue is moving much faster than you expected. In this 
case, the advantage you would compute for your choice of queue is 
negative, appropriately signaling a missed opportunity (Bennett et al., 
2021; Coricelli et al., 2005; Loomes and Sugden, 1982), but you would 
experience no prediction error with respect to this queue since it is 
moving as expected. Moreover, you will in fact experience a positive 
prediction error with respect to the state ’about to choose a queue’, 
regardless of whether it is your queue or the alternative queue that is 
faster than expected. Conversely, if both queues suddenly move faster 
than expected, advantage remains at zero, and the improvement in your 
situation will be captured as a positive reward prediction error with 
respect to your current state’s value. Thus, although reward prediction 
errors and advantage are often correlated, they diverge in that the 
former generally signals changes in expected reward, whereas the latter 
signals differences in expected reward between chosen and alternative 
actions. 
4.2. Emotion as relative action effectiveness 
It is widely recognized that emotions are involved in how we eval­
uate and adjust our actions. Negative emotions, in particular, are 
thought to signal that we are not doing as well as we could be doing, and 
should therefore change our course of action (Kurzban et al., 2013). 
Such policy adjustment makes sense whenever we find that an alterna­
tive course of action may work better, which is to say, whenever the 
effectiveness of our current course of action is lower than that of alter­
native courses of action. In such cases, the resulting emotional state 
facilitates a search for alternative courses of action (Goldberg et al., 
1999), thereby helping us adjust our policy to avoid further loss. 
The measure of advantage precisely captures the comparison be­
tween chosen and alternative actions, and thus, it has recently been 
suggested to be represented by emotional state (Bennett et al., 2021). 
This suggestion can explain not only the general involvement of emotion 
in how we evaluate and adjust our actions, but also more subtle 
empirical observations. First, it inherently explains why we feel bad 
when an action we could have taken, but didn’t, is found to have better 
outcomes than expected (Coricelli et al., 2005; Loomes and Sugden, 
1982). In addition, it explains why we typically have stronger emotional 
responses to outcomes of actions that we don’t normally take (Kahne­
man and Miller, 1986; Kutscher and Feldman, 2019). This is because 
outcomes of more typical actions similarly impact both sides of the 
advantage equation (i.e., both Q(a, s) and V(s), since the latter is an 
average of the value of typical actions) and thus partially cancel out. 
There are at least two factors, however, that moderate the usefulness 
of an estimated advantage as a measure of action effectiveness. The first 
is that the observed outcome based on which advantage is estimated 
may only be probabilistically determined by the action. For this reason, 
advantage-based updates of policies are usually moderated by a learning 
rate between 0 and 1, which reflects the degree to which observed 
outcomes are thought to be controlled through action. This learning rate 
can be thought of as an index of estimated environmental controllability 
(Ligneul et al., 2022). 
The second potential moderating factor is self-control, that is, the 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 5

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
5
degree to which the agent can control its own action. Self-control could 
be low for actions that we are innately predisposed to take or avoid, that 
have become habitual, or that require skill, planning, or training (e.g., 
telling a joke effectively, or shooting a basketball into the basket). To 
formalize self-control, we assume that rather than being controlled 
directly, the agent changes its policy by adjusting a set of control pa­
rameters θa|s, one for each action, such that the probability of taking an 
action is: 
π(a|s)∝eβa|sθa|s
(4.2.1)  
.Here, βa|s represents how difficult it is to acquire or eliminate action a. 
This formulation ensures that while the control parameters are uni­
formly controllable, the actions they control are not. The controllability 
of action a in state s is thus denoted as: 
∇θa|sπ(a|s) = βa|sπ(a|s)(1 −π(a|s) )
(4.2.2) 
Combining environmental and self-control into a measure of overall 
controllability, ̂
C at|st = η∇θa|sπ(a|s), allows expressing policy adjustment 
as (Williams, 1992)2: 
θa|s
t+1 = θa|s
t
+ ̂
C at|st ̂Aat|st
(4.2.3) 
Compared to estimated advantage alone, the multiplication of 
controllability and estimated advantage, ̂
C at|st ̂Aat|st, offers a more ac­
curate representation of the gains and losses that are attributable to our 
choices. 
4.3. Emotional state as cumulative action effectiveness 
The accumulation of multiple gains and losses that are attributable to 
our choices is thought to be represented by an enduring emotional state 
(Bennett et al., 2021). To also account for controllability, here we pro­
pose the following formulation of this accumulation: 
MA
t+1 = (1 −λ)
(
Δθa|s
t
+ λΔθa|s
t−1 + λ2Δθa|s
t−2 + λ3Δθa|s
t−3 + …
)
(4.3.1)  
where Δθa|s
t
= ̂
C at|st ̂Aat|st. As in the case of value changes, if modelled 
with λ = 0, the computed emotional state only reflects the last action, 
but the higher λ is, the more it will reflect actions taken longer ago. 
Like other emotional states, enduring emotional states representing 
action effectiveness also have the consequence of generalizing the in­
formation that evoked them. Thus, negative emotional states evoked by 
poor outcomes of actions make subsequent outcomes seem worse and 
more attributable to actions (Ask and Pina, 2011; DeSteno et al., 2000; 
Lerner and Tiedens, 2006; Quigley and Tedeschi, 1996; Tetlock, 2002). 
In similar to Eq. (3.3.1), this impact of emotional state may be formu­
lated as: 
θa|s
t+1 = θa|s
t
+ ̂
C at|st ̂Aat|st +
(
1 −̂
C at|st
)
MA
t
(4.3.2) 
Why is such generalization beneficial? In a noisy environment, each 
individual observation provides relatively little information. Averaging 
over multiple recent outcomes via MA
t accumulates information from 
multiple observations, and thus offers a more informative measure of 
how well the current policy is doing. It is precisely this rationale that 
underlies the widespread use of ‘momentum’ in machine learning al­
gorithms (Rumelhart et al., 1985). Indeed, simulations have shown that 
informing policy updates by a cumulative measure of advantage accel­
erates learning in various artificial settings (Bennett et al., 2021). 
To draw the parallel to real world problems, consider that an 
enduring negative emotional state due to recurrent underperformance 
may signal that a person’s overall approach is suboptimal, indicating 
they should more critically examine their subsequent actions. For 
example, a student may experience a series of failures in achieving their 
goals such as failing an exam, not being able to focus during class, and 
making repeated errors in their assignments. Together, these may indi­
cate that the student has adopted inefficient working habits. By nega­
tively biasing the processing of subsequent outcomes, a negative 
emotional state may aid the student to more quickly identify and modify 
additional cases of poor performance. 
4.4. Emotions about other people’s actions 
Other people’s actions can evoke emotions that are as strong and 
meaningful as the emotions we have about our own actions (Feldman­
Hall and Chang, 2018). We propose such emotions can also be under­
stood as representations of action effectiveness that serve to adjust 
policy. Except that in this case, the policy that is being adjusted is 
someone else’s. Indeed, it is well known that emotions are often 
expressed in order to influence other people’s behavior (Jones et al., 
2011; Parkinson, 1996). For instance, when someone acts in a way that 
harms us, we may express a negative emotion with the hope that the 
person will change their ways. Moreover, there is evidence that such 
emotions represent not only (dis)advantage (to us due to someone else’s 
actions) but also controllability. Thus, emotional responses are stronger 
in response to the outcomes of peers’ actions that are perceived as 
intentional, and therefore, as more amenable to control (De Quervain 
et al., 2004). Similarly, when people aim to change a peer’s behavior, 
and believe that to be achievable, they tend to experience more negative 
emotions towards the peer (Lemay et al., 2012). 
5. Computation of uncertain prospects 
The classes of computations we considered so far identify changes in 
expected reward that are indicated by evident outcomes. An additional 
computation we need to consider concerns outcomes that may or may 
not happen in the future. Indeed, dangers and opportunities have long 
been thought to be the subject of emotions. Computational work has 
suggested that our emotions about such uncertain prospects may 
represent the width and skewness of the distribution of possible out­
comes (Hagen, 1991; Wu et al., 2011), and more generally, our uncer­
tainty about these outcomes (Peters et al., 2017). In reinforcement 
learning, computations about uncertain prospects can be captured in 
two broad ways, either by associating a given state or action with a 
distribution of rewards (‘distributional RL’; Dabney et al., 2018), or by 
associating a given action in a given state with a distribution of suc­
ceeding states, each of which is associated with a scalar reward (‘Mod­
el-based RL’; Doll et al., 2012). Here we use the latter formalism because 
it offers a way to represent the effects of our actions on specific pro­
spective outcomes, which often serve as the objects of our emotions. 
5.1. Prospecting for reward 
A prospective reinforcement-learning agent computes the value of a 
present state st based on the values of the future states st+1 that are likely 
to follow it, given the different actions it may choose: 
V(st)
=
E[rt + γV(st+1)|st, πt]
=
E[rt|st, πt] + γE[V(st+1)|st, πt]
=
E[rt|st, πt] + γ
∑
s
p(st+1 = s|st, πt)V(s)
=
E[rt|st, πt] + γ
∑
a
π(at = a|st)
∑
s
p(st+1 = s|st, at = a)V(s)
(5.1.1) 
Here, the left term represents the expected immediate reward, and 
the right term represents the prospective reward, computed as a 
2 Note that this update is often divided by πt(at|st) to prevent a bias in policy 
adjustment resulting from the fact that some actions are executed more and 
therefore their relevant parameters are updated more. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 6

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
6
weighted average over possible future actions (a) and states (s). To 
perform this computation the agent requires a model of the world that 
specifies which future states are likely given different actions (i.e., 
p(st+1|st, at)). For this reason, prospective reinforcement-learning is often 
referred to as ‘model-based’ (Daw et al., 2011; Daw and Dayan, 2014; 
Doll et al., 2015; Gl¨ascher et al., 2010). Notably, the values of future 
states can also be expanded as a function of the states that follow them, 
and so can the values of those states, and so on ad infinitum. 
A main benefit of performing such prospective computation is that it 
allows us to compute values for states that we never experienced. For 
example, we can infer a positive value for exercising regularly, before 
ever having done so, based on a model of the world that specifies that 
exercising regularly improves health. Another related benefit of this 
form of computation is that it quickly and efficiently adjusts to changes 
in the environment. It does so since new information regarding the 
probability of a future state s instantly changes the value estimated for 
any state that s might follow. Prospection rids us of the need to expe­
rience these states anew to know that their values changed. For example, 
upon learning that a highly infectious virus is spreading in our city, 
prospection allows us to decrease our estimated values for attending any 
type of crowded social event. 
5.2. Emotion as danger and opportunity 
Using the formalism of prospective reinforcement learning, we 
devise a representation of danger and opportunity that is sensitive to the 
computations implicated by previous work, namely, the width and 
skewness of the distribution of possible outcomes. We first consider 
skewness. 
Positive and negative skewness are associated with positive and 
negative anticipatory emotions (Hagen, 1991; Wu et al., 2011), or in 
other words, emotion is positive when there are prospects that are much 
better than the expected outcome, and negative when there are pros­
pects that are much worse. We can represent how the value of an indi­
vidual prospect differs from expectations as: 
Gs,t+Δt = V(s) −E[V(st+Δt)|st, πt ]
(5.2.1)  
where V(s) is the value of a prospective state s that may materialize Δt 
time steps following present time t, and E[V(st+Δt)|st, πt ] is the expected 
value for that future time, averaged over the possible future states the 
agent may occupy, given current state st and its action-selection policy 
πt. G tells us whether it would be a good thing if the prospect materi­
alizes. If a prospect with G > 0 materializes, that means things turned 
out better than expected, whereas if a prospect with G < 0 materializes, 
things turned out worse than expected. 
G, however, does not provide information about the probability the 
prospect will materialize. It is thus susceptible to any prospect no matter 
how imaginary or irrelevant it might be. This problem can be solved by 
modulating G by the probability of the prospect, p(st+Δt = s|st,πt). The 
question here is whether this probability should be counted as such, or 
whether what primarily drives emotions are prospects whose probabil­
ity is potentially controllable. From a rational perspective, there is no 
use in devoting mental resources to a prospect we cannot control. 
Anecdotal evidence seems to support this perspective. For example, 
people who report being less concerned with death attribute this to their 
understanding that death is inevitable or not under their control (Feifel, 
1974). Additionally, accepting that one cannot control a negative 
prospect is a common coping strategy that serves to mitigate negative 
emotions (Jackson et al., 2012; McCracken and Keogh, 2009; Zettler 
et al., 1995). And in the positive domain, availability of desirable 
prospects increases positive anticipatory emotions (Ghoniem et al., 
2020). 
Thus, we propose that emotions may only be affected by probabilities 
of prospects that, to the person’s estimation, are potentially controllable. 
In the case of a positive prospect, what we should care about is whether 
there is a course of action, a, by which we may be able to increase the 
prospect’s probability, whereas with regards to a negative prospect, we 
care about whether we can do something (that we are not already 
planning to do, as specified by our present policy πt) to avoid it: 
C s,t+Δt =
{ ifG > 0
max
a ∇θa|sπ(a|s)(p(st+Δt = s|st, a) −p(st+Δt = s|st, πt) )
ifG < 0
max
a ∇θa|sπ(a|s)(p(st+Δt = s|st, πt) −p(st+Δt = s|st, a) )
}
(5.2.2) 
Using these definitions, prospective emotions anticipating individual 
prospects can be expressed as an upper confidence bound (UCB; Garivier 
and Moulines, 2011) on the prospective change in value modulated by 
the potential to do something about it: 
[C G]UCB
s,t+Δt
(5.2.3) 
An upper confidence bound on a given computation is the largest 
probable quantity it might produce given our uncertainty about the 
estimates involved. 
This computation satisfies all properties suggested by prior work 
(Fig. 1). First, the upper confidence bound is inherently higher the more 
uncertain we are about the values and probabilities of prospective states, 
and thus the computed emotion will scale with the width of the esti­
mated distribution of outcomes that is attributable to lack of knowledge 
(i.e., estimation uncertainty). Second, if it is the true distribution of 
possible outcomes that is wider (i.e., higher irreducible uncertainty), 
that means that on average probable prospects deviate more from the 
expected value (i.e., higher absolute G), and thus the computed emo­
tions will also be stronger. Third, if the distribution of possible outcomes 
is positively skewed, that means there are prospects with greater posi­
tive deviations which would lead to stronger positive emotions, whereas 
if the skewness is negative, that means there are prospects with greater 
negative deviations leading to stronger negative emotions. 
5.3. Emotional state as cumulative prospection 
Prospective emotions do not always concern a single definite pros­
pect (Grupe and Nitschke, 2013; LeDoux and Pine, 2016). To represent 
prospective emotions in the presence of uncertainty about when and 
where the prospect will materialize and what precisely it might involve, 
we can sum over different possible prospects and time delays: 
MP
t = (1 −γ)
∑
s
∑∞
i=t+1γi−t[C G]UCB
s,t+Δt
(5.3.1) 
This sum represents prospective emotional states that extend in time 
and are not specific to a single prospect. 
Like the other types of emotional states, empirical research suggests 
that prospective emotional states also serve to generalize, in this case, 
from old to new prospects. Thus, having been evoked by a recognized 
danger, a negative prospective emotional state increases our tendency to 
recognize and respond to additional dangers (Abend et al., 2020; 
Bar-Haim et al., 2007; Mogg and Bradley, 1998; Pitman et al., 1993; 
Rosen and Schulkin, 1998). Such enhanced threat detection may be 
mediated, for instance, by increased attention to threat-related words 
(MacLeod et al., 1986) or images (¨Ohman et al., 2001). A prototypical 
example of increased threat detection is offered by the enhanced startle 
responses people and animals exhibit under threat (Davis et al., 1993). 
In a dangerous environment where taking risks is ill advised (e.g., a 
jungle with predators and poisonous animals), this effect may be life­
saving. Drawing the parallel in the domain of positive prospects, we can 
conceptualize a positive prospective emotional state as a motivational 
state in which a person is primed to recognize and pursue opportunities 
(Luthans and Jensen, 2002). 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 7

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
7
6. Mapping computations onto emotions 
6.1. Three classes of computations 
We identified three classes of computations that emotions may 
represent: computations of changes in expected reward, of the advan­
tageousness of controllable actions, and of potentially controllable 
dangers and opportunities. As we have seen, all three are useful, in ways 
that complement each other, to an agent striving to maximize reward. 
Tracking expected reward is necessary for performing the two other 
computations, and can help arbitrate between action and inaction (Niv 
et al., 2006) as between exploration and exploitation (Le Heron et al., 
2020; McClure et al., 2005). Evaluating actions based on experience 
helps improve one’s policies even absent a world model that enables 
prospection, whereas prospection enables estimating expected reward 
and the advantageousness of actions in the absence of direct experience. 
Indeed, the cognitive science literature strongly suggests that humans 
utilize all three of these computations. 
Seen as appraisals, one might be tempted to assume a many-to-many 
mapping between the computations we described and emotions 
(Scherer, 2009a). However, these computations lie one step above the 
primary appraisals often invoked in theories of emotions. For example, 
the computation of reward lost or gained due to potentially controllable 
actions incorporates multiple appraisal dimensions such as pleasantness, 
goal relevance, agency, and controllability. This raises a more parsi­
monious possibility, that of a one-to-one mapping between computa­
tions and emotions. 
6.2. Three classes of emotions 
Our proposal here (Fig. 2) leans on Nesse and Ellsworth’s (2009) 
evolutionary analysis of the roles of different emotions, as on an 
extensive psychological literature examining the antecedents and con­
sequences of different emotions (Averill, 1968; Carver, 2004; Carver and 
Harmon-Jones, 2009; Cunningham, 1988, 1988; Frijda, 1986, 1987; 
Harmon-Jones and Sigelman, 2001; Keltner et al., 1993; Kreibig, 2010; 
Lench et al., 2011, 2016; Levine, 1996; Levine and Pizarro, 2004; Nesse 
and Ellsworth, 2009; Oatley et al., 2006; Oatley and Duncan, 1994; 
Roseman, 1996). Closely resembling our three classes of computations, 
this literature identifies two classes of emotions that are evoked by 
evident outcomes, and one that is evoked in anticipation of prospective 
outcomes. 
The first two classes involve, on one hand, emotions such as happi­
ness and sadness, and on the other hand, emotions such as frustration, 
anger, and content. Both sets of emotions are evoked by evident out­
comes, but they differ in whether those outcomes are potentially 
controllable. Thus, happiness and sadness are evoked by outcomes that 
are not necessarily attributable to someone’s actions and thus there may 
not be anything one can, or needs to, do to about them. The appropriate 
response is to adjust one’s expectations, upwards (happiness) or 
downwards (sadness), and carry on. Happiness and sadness are thus well 
suited to represent positive and negative changes in value. 
By contrast, emotions such as frustration, anger, and content occur 
when outcomes warrant positive or negative evaluations of actions. 
Correspondingly, these emotions are associated with behavioral changes 
that can be understood as adjustments of one’s policy in favor of ad­
vantageous, and away from disadvantageous, actions. This class of 
Fig. 1. Determinants of positive and negative prospective emotions. A. If the distribution of possible outcomes is wider, there are more probable prospects with high 
deviation from the expected value, and thus both positive and negative emotions are stronger. The estimated distribution can be wider either because outcomes are 
random (irreducible uncertainty) or due to lack of information (estimation uncertainty). B. If the skewness of the distribution is negative, then there are more 
probable prospects with a high negative deviation from the expected value, and thus negative emotions predominate. Conversely, if skewness is positive, then there 
are more prospects with a high positive deviation, and thus positive emotions predominate. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 8

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
8
emotions is the most social and diverse out of the three classes due to 
two reasons: (i) we evaluate and influence not only our, but also other 
people’s, actions, and (ii) our actions impact not only ourselves but also 
others. In many languages, different combinations of responsible and 
affected agent are labeled as distinct emotions (Fig. 3). Thus, when we 
suffer because of our own mistakes, we get ‘frustrated’ (Dollard et al., 
1939), whereas if someone else is at fault, we get ‘angry’ (Averill, 1983; 
Berkowitz, 1999; Ortony et al., 1990). If we harmed someone else we 
feel ‘guilt’ (Chang and Smith, 2015; Leith and Baumeister, 1998; 
Tangney and Fischer, 1995), whereas if it was someone else that harmed 
another person, we feel ’moral indignation’. What is common to all 
these scenarios is that we estimate that things are not going as well as 
they could go due to our or others’ actions. The emotions that represent 
this judgment serve to change the responsible party’s policy, either 
directly or through a social expression of the emotion. 
Finally, the quintessential prospective emotions are fear and desire 
(T. Brown, 1846; Nesse and Ellsworth, 2009). Both emotions are evoked 
by negative and positive prospects, and both motivate planning, to avoid 
or realize the emotion-inducing prospect. These emotions also each have 
their polar opposite. Specifically, the lack of desirable prospects is often 
referred to as apathy, and the lack of fearful prospects as calm. Of all 
emotions, fear has probably been most extensively studied in relation to 
learning, with decades of research devoted to what was once called “fear 
conditioning” and is now more commonly referred to as “threat condi­
tioning”. This change in terminology has to do with the predominant use 
of animals in such research, and the inability to question animals about 
their emotions (LeDoux, 2014). Perhaps as a result, research in humans 
on fear conditioning has also neglected the emotional aspect of this 
much studied phenomenon. Our computational formulation of fear as a 
representation of potentially controllable danger, and the quantitative 
predictions such a formulation can generate, may facilitate a reconsid­
eration of the role of fear in threat conditioning in humans and animals. 
6.3. Three classes of moods 
Though general theories on the subject of moods are lacking, many 
researchers implicitly or explicitly assume that there are different types 
of moods (Harmatz et al., 2000; Jansson and Nordgaard, 2016; McGo­
wan et al., 2020; Rottenberg, 2005; Truax and Selthon, 2003; Tsanas 
et al., 2016). Moreover, the classifications of moods in the literature 
often parallel classifications of emotions. For example, extended diffuse 
(i.e., non-specific) sadness is often referred to as a sad or depressed 
mood, extended diffuse anger is referred to an angry or irritable mood, 
and extended diffuse fear is referred to as an anxious mood. This cor­
respondence between emotions and moods, as well as the distinction 
between them in timescale and specificity, are well captured by 
assuming that moods are constructed through temporal integration of 
Fig. 2. Summary of computations we propose are represented by emotional states.  
Fig. 3. Action-evaluation emotions. Different emotion labels are used for 
different combinations of culpable agent (‘poor outcome due to’) and the agent 
suffering as a result (‘poor outcome suffered by’). These labels are paralleled by 
corresponding labels in the domain of positive outcomes (e.g., ‘anger’ corre­
spond to ‘gratitude’, ‘frustration corresponds to ‘content’). 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 9

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
9
momentary emotions. As we have seen, this perspective can be imple­
mented with regards to each of the computations we identified through 
a cumulative sum. These sums provide running averages of recent 
changes in expected reward, of recent success or failure of our and 
others’ actions, and of recently encountered dangers and opportunities. 
Defined as these computations, moods accelerate learning through 
generalization, that is, by biasing the agent in favor of computations that 
are similar in type and valence to those the present mood represents. 
This is helpful for the simple reason that whenever similar changes, 
evaluations, or prospects are frequently encountered, it makes sense to 
regard them as a priori more likely. It is important to note, however, that 
the benefit of emotional states as prior expectations concerning the 
present environment extends beyond the domain of learning. Specif­
ically, such prior expectations could explain the patterns of automatic 
physiological responses and action tendencies associated with emotional 
states (Scherer, 2009b). As an example, consider how increased arousal 
and quick reactivity to potential threats, both features of an anxious 
mood, can be helpful in the dangerous environments that an anxious 
mood signals. 
A key open question about moods is where to draw the line between 
them and emotions, and whether a line should be drawn at all. 
Convention has it that emotions last moments to minutes, whereas 
moods last hours to weeks. We are not aware, however, of empirical 
evidence that justifies such a categorical distinction. Indeed, our for­
mulations in this paper allow a continuum of possibilities for modeling 
emotional states, from a momentary emotion to a lasting mood. Future 
work could investigate whether emotional states temporally integrate 
computations on only a few fixed timescales, or on a whole continuum of 
timescales. 
7. Summary and general implications 
The emotions we examined in this paper combine to form a set of 
interdependent computations necessary for an agent to behave adap­
tively given limited information in an uncertain world. Though we have 
presented specific algorithms for carrying out each computation (Fig. 2), 
the essential part of our proposal concerns what is being computed, 
namely, obtained reward (pleasure and pain), changes in expected 
reward (happiness/sadness), the relative effectiveness of actions in 
obtaining reward (content/anger), potential changes in expected reward 
the agent could plan for (fear/desire), and global changes in the prior 
probability of each of these computations (the different types of mood). 
This proposed framework generates a plethora of quantitative pre­
dictions that are amenable to testing in and outside the lab. There are 
two prerequisites for testing these hypotheses in human subjects. First, 
rather than querying subjects about one or two dimensions of their 
emotional states, as done so far in computationally inspired in­
vestigations of emotion (Rutledge et al., 2014; Eldar and Niv, 2015; 
Villano et al., 2020), finer-grained information needs to be collected 
about different types of emotions and moods. Second, the experimental 
design needs to be powerful enough to allow independently manipu­
lating changes in expected reward, action evaluations, and prospective 
computations. 
Recent progress has also charted a way towards studying emotions in 
animals (Anderson and Adolphs, 2014), a critical endeavor if we are to 
understand emotional function and dysfunction at the neural level. In 
the absence of subjective reports, it is proposed that emotional states in 
animals are operationalized via a set of objective canonical character­
istics, which include scalability, valence, persistence, and generaliza­
tion. The computations we outlined here fit exceptionally well with this 
approach since they possess all these characteristics. Future studies of 
emotions in animals could thus make use of the computations we pro­
posed to design manipulations that would evoke specific emotions, as 
well as to generate quantitative hypotheses about the downstream ef­
fects of these manipulations on learning and behavior. This could help 
map the neural chain of events that is necessary for each computation to 
be properly performed. 
In this regard, it is important to remember that the algorithmic de­
tails that we delineated likely underestimate the complexity and so­
phistication of the brain mechanisms in place. Thus, for example, it is 
likely that a change in expected reward will evoke stronger or longer- 
lasting happiness if there is reason to believe that this change is 
particularly likely to generalize to other sources of reward. Additionally, 
our formulation of how action effectiveness is computed directly couples 
these computations with changes in policy, though in practice decisions 
about policy could dissociate from these computations. We also left open 
the question of whether and how people infer specific relevant time­
scales for computing mood, and whether this computation is equipped to 
detect discrete, as opposed to gradual, global changes. Thus, substantial 
additional research is required to investigate the finer details of how 
these computations are performed and used. Nevertheless, our frame­
work offers a first comprehensive account of the computations mediated 
by different emotional states, together with a set of biologically plau­
sible and empirically supported algorithms for performing these com­
putations. We next examine several general implications that arise from 
a consideration of this framework as a whole. 
7.1. Disentangling emotions 
The task of differentiating between different types of emotion is 
complicated by the observation that different emotions tend to co-occur. 
This is especially evident regarding the three major negative emotions: 
sadness, anger, and fear (or anxiety). All three types of emotion are 
prevalent, for instance, in depression, in bipolar disorder, and in 
borderline personality disorder (Goldberg and Fawcett, 2012; Riley 
et al., 1989; Tsanas et al., 2016). And all three strongly covary in the 
general population (Diener and Emmons, 1984). Our account provides a 
natural explanation for this co-occurrence since it posits that all three 
types of emotion can be evoked by new information that portends a poor 
outcome. Sadness will be evoked to the extent that the new information 
lowers expectations of the future. Anger will also be evoked if the poor 
outcome is attributed to ours or others’ actions. And fear will also be 
evoked if there is uncertainty about whether the poor outcome will 
eventually materialize, such that we might be able to avoid it. These 
three possibilities are mutually compatible and often occur together. 
Given the complexity and uncertainty involved in performing these 
computations, it is also no wonder that we often find ourselves not 
knowing what to feel. So far, an inability to report one’s emotions (i.e. 
alexithymia) has been taken as evidence that a person has a problem 
perceiving or verbalizing their emotions (Taylor and Bagby, 2004), 
possibly because the concepts they hold for different emotions are not 
well differentiated (Demiralp et al., 2012). Our account suggests, how­
ever, that in many cases the difficulty might not be in the act of inter­
oceptive perception and categorization but rather in making inferences 
about the external environment and one’s state in it. For instance, 
whether we respond with anger or sadness depends on our ability to 
assign (or not assign) credit for a poor outcome to someone’s actions. If 
we are uncertain about this, then an undifferentiated negative emotional 
response may the best we can do. 
On longer timescales, our account suggests that meaningful in­
teractions likely exist between different types of mood. For instance, 
enduring sadness entails that reward availability is decreasing, which 
should impact the significance and likelihood of prospective computa­
tions responsible for emotions such as fear and desire. At the same time, 
a prospective emotion such as anxiety might focus attention on negative 
implications of experienced outcomes and thus bias computations con­
cerning changes in value, potentially tempering happiness and pro­
moting sadness. Indeed, phenomenological studies have exposed 
complex emotion dynamics with meaningful consequences for mental 
health (Houben et al., 2015). Future work could consider how these 
empirically observed dynamics cohere with the computations delin­
eated here. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 10

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
10
7.2. Situational, developmental, and innate priors 
Another consequence of the uncertainty inherent in emotion- 
mediated computations is that they are invariably informed by prior 
expectations. Such prior expectations can be situational, developmental, 
or innate. Here we proposed that the primary role of moods is to act as 
situational priors. A sad mood biases computations towards sadness, an 
irritable mood biases computations towards anger, an anxious mood 
biases computations towards fear, and so on. These impacts of different 
moods are rational to the extent that decreases in value portend further 
decreases in value (sadness; Eldar et al., 2016), suboptimal actions 
portend further suboptimal actions (anger; Bennett et al., 2021), and 
looming dangers portend further dangers (fear; Bolles and Fanselow, 
1980). 
By contrast to temporary moods, lasting developmental and innate 
priors could underlie stable individual predispositions to experience one 
or another type of emotion (Akiskal et al., 2005; Davidson and Irwin, 
1999; Marteau and Bekker, 1992; Spielberger et al., 1983; Wilkowski 
and Robinson, 2008). Besides genetic variation, such priors may be 
shaped by a person’s predominant childhood experiences. For instance, 
growing up with an abusive parent rationally motivates a prior expec­
tation that one is likely to be harmed by others’ actions, thus leading the 
child to be quick to respond with anger and aggression (Trickett and 
Kuczynski, 1986). 
A particularly important prior expectation, the impact of which cuts 
across multiple types of emotion, concerns controllability. Beliefs about 
controllability may be informed by innate, developmental, and situa­
tional factors. For instance, it is well established that experiencing lack 
of controllability over outcomes can generate “learned helplessness”, 
which can be understood as a belief that outcomes cannot be controlled 
by our actions (Lieder et al., 2013; Maier and Seligman, 1976). Our 
account predicts, and indeed evidence supports, that such a belief will 
have a substantial impact on one’s temperament, diminishing a ten­
dency to respond actively with anger and enhancing a tendency to 
respond passively with sadness and resignation (Launius and Lindquist, 
1988; Peterson and Seligman, 1983; Sedek and Kofta, 1990). 
Within a given situation, the expected relationship between 
controllability and anger is made more complex when we consider not 
only how intense anger is expected to be but also how long it is likely to 
persist. If controllability is very low then there is no point getting angry, 
but if it is very high, any disadvantageous action that is identified will be 
quickly eliminated from the policy, and then anger will quickly fade. 
The maximum amount of anger is thus expected at some medium level of 
controllability. Based on this rationale, we may also expect abnormal 
amounts of anger in cases where the estimated level of controllability is 
higher than the actual level. A similar logic applies to the relationship of 
controllability with the prospective emotional states of fear, anxiety, 
desire, and hope. 
7.3. Function and malfunction 
It is increasingly recognized that psychopathologies of mood and 
anxiety may be rooted in dysfunctions of computational mechanisms 
used to obtain reward and avoid punishment (Aylward et al., 2019; 
Bach, 2021; Brown et al., 2021; Chiu and Deldin, 2007; Gillan et al., 
2020; Halahhakoon et al., 2022; Huys and Browning, 2021; Levy and 
Schiller, 2021; McCabe et al., 2010; Montague et al., 2012; Sharp et al., 
2021; Sharp and Eldar, 2019; Szanto et al., 2015; Zorowitz et al., 2021). 
However, this rapidly evolving literature has so far mostly shied away 
from defining what constitutes functional and dysfunctional emotional 
responses. The normative definitions we proposed here fill this crucial 
gap, and can thus advance existing research towards identification and 
investigation of psychopathological emotions. 
Emotional malfunction may arise within our framework if a 
computational algorithm does not work properly (e.g., changes in value 
are inferred when there aren’t any), if a person’s prior assumptions are 
inappropriate (e.g., controllability is believed to be lower or higher than 
it is), or relatedly, if the person has adapted to one environment but now 
resides in a different one wherein past computations are no longer 
suitable (Montague et al., 2012). Importantly, each of these failures may 
apply to each of the different factors that impact a given emotion. For 
instance, excessive anxiety could result due to overestimation of po­
tential decreases in value (422) or due to misestimation of self-control 
(Zorowitz et al., 2020; 423). Similarly, excessive sadness could result 
due to underestimation of obtained reward (i.e., diminished pleasure; r 
in Eq. 3.1.2) or due to an asymmetry in learning that makes negative 
value updates predominate over positive value updates (e.g., due to 
differences in η in Eq. 3.1.3). Ultimately, given the extent to which 
psychopathological processes have so far resisted elucidation, a multi­
factorial approach is most likely to bear fruit. 
That said, at least one specific pathological mechanism might 
engender multiple types of emotional disturbances. This mechanism 
concerns the generalizing impact of mood, which entails, for instance, 
that sadness which is evoked by recent negative value updates promotes 
further negative value updates. The critical question here is whether 
sadness-induced negative value updates make a person even sadder. 
Normatively, this should not be the case (notice that the computation of 
mood in Eq. (3.3.2) does not factor in the mood-induced component of 
value updates). However, if the brain does not dissociate between value 
updating that is induced by mood and that which is induced by external 
information, and thus factors both into the computation of mood, then 
sadness and happiness will recursively self-intensify. Such lack of 
dissociation may either constitute normal function, given the brain’s 
implementational constraints, or a specific form of malfunction. Either 
way, preliminary evidence indicates that self-intensifying moods might 
be key to explaining individual predispositions to mood disorders (Eldar 
and Niv, 2015). The possibility that irritable and anxious moods also 
self-intensify has yet to be thoroughly investigated, but it is easy to see 
how this mechanism could contribute to mental disorders involving 
extreme rage or anxiety. 
8. Brain implementation 
Whether distinct emotions are implemented by distinct neural cir­
cuits is a matter of ongoing debate (Berridge, 2019; Hamann, 2012). 
Some meta-analyses found that different emotions are associated with 
different patterns of brain activity (Vytal and Hamann, 2010), whereas 
others failed to find such dissociation (Lindquist et al., 2012). Our ac­
count of emotions as reflective of distinct types of computation entails 
that different emotions must be implemented by dissociable neural 
circuits. However, since each emotion-mediated computation involves 
multiple cognitive functions (e.g., perception, valuation, prediction, and 
learning, to name just a few of the processes involved in value learning), 
the neural circuits implementing these computations are likely spread 
over large, partially overlapping networks of brain regions. It is unclear 
whether current macroscopic neuroimaging techniques are best suited 
to dissociate such overlapping circuits. Indeed, one methodological 
difference that seems to distinguish the works that do find unique neural 
signatures for different emotions is that these works admitted signatures 
that consist of granular partially overlapping multi-voxel patterns of 
brain activity (Kragel et al., 2016). 
Ultimately, our account suggests that the debate concerning the 
brain basis of emotion may be most effectively solved by focusing on 
computational mechanisms as a bridge between emotion and brain 
function (LeDoux, 2000; Sander et al., 2005). The computational 
mechanisms we associated here with distinct emotions – the reward 
function, value learning, policy learning, and prospection – have all 
been, for some time now, major targets for neuroscientific study. Thus, 
in combination with our account, existing neuroscience research gen­
erates clear hypotheses concerning the likely neural substrates of each 
type of emotion. We next review several of these hypotheses. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 11

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
11
8.1. Liking vs wanting 
The functional dissociation that we proposed between pleasure on 
one hand, and happiness and content on the other, fits with a familiar 
dissociation from the neuroscience literature between ‘liking’ and 
‘wanting’. A substantial body of empirical work dissociates between 
gaining pleasure from consuming a given reward (i.e., liking) and 
motivation to obtain the reward (i.e., wanting; Berridge, 1996; Berridge 
et al., 2009). The dissociation between these two functions is most 
evident in pathological conditions such as schizophrenia (where liking 
can be intact while wanting is suppressed) and addiction (where 
wanting persists in the absence of liking; Berridge and Robinson, 2016). 
Indeed, these two functions seem to be implemented by distinct neural 
mechanisms. Thus, liking is thought to be at least partially mediated by 
opioids, whereas wanting is thought to be partially mediated by dopa­
mine (Berridge, 2007). 
In normal function, liking and wanting are dissociated in time, in the 
sense that one can be observed in the absence of the other (Berridge and 
Dayan, 2021). Our account explains this dissociation by positing that 
liking (i.e., pleasure) represents the reward value of present experience, 
whereas wanting (i.e., policy) relies on information gained from past 
experience (McClure et al., 2003). It thus makes sense that wanting will 
follow liking and will persist for some time in its absence. In addition, 
our account enriches the concepts of liking and wanting by offering a 
computational role for the inherently affective liking – namely, that of a 
reward function – and an affective aspect to the computational construct 
of wanting, or more precisely for the learning that leads to wanting – 
namely, that of happiness and content. A neural prediction to which this 
perspective directly leads is that whereas pleasure is mediated by opi­
oids, happiness and content should be mediated by dopamine. Several 
studies already offer preliminary empirical support for this prediction 
(Rutledge et al., 2014, 2015; van Steenbergen et al., 2019). 
An intriguing open question relates to the possibility that pleasures 
may not only drive the learning that leads to wanting, but could them­
selves be modified through learning from other types of reward signals 
(Dayan, 2021). An illustrative example of such modification is how we 
naturally acquire a taste for foods that made us satiated and an aversion 
of foods that made us nauseous (Birch, 1999; Myers and Sclafani, 2001). 
How and when different types of pleasure (e.g., gustatory, sexual, 
affiliative, achievement-related) are modified is thus a promising target 
for future work. 
8.2. Value vs policy learning 
The distinction between value and policy learning, which we pro­
posed differentiates between sadness and anger, is a key characteristic of 
“actor-critic” reinforcement learning models (Sutton and Barto, 2018). 
In addition to their usefulness for solving machine learning problems 
(Grondman et al., 2012; Haarnoja et al., 2018; Konda and Tsitsiklis, 
2000; Peters and Schaal, 2008), this class of models has been widely 
used for understanding how the brain learns to predict and maximize 
reward. This body of work suggests that value learning is mediated by 
dopaminergic prediction error signals transmitted from the ventral 
tegmental area to the ventral striatum and frontal areas (Barto, 1995; 
Houk and Adams, 1995; Joel and Weiner, 2000; Miller and Wickens, 
1991; Waelti et al., 2001; Wickens and K¨otter, 1995), whereas policy 
learning is mediated by dopaminergic signals from the substantia nigra 
pars compacta to the dorsal striatum (Lerner et al., 2015; O’Doherty 
et al., 2004; Roeper, 2013; Rossi et al., 2013). Though this simple picture 
still requires further elaboration and investigation (Averbeck and 
O’Doherty, 2022; Niv, 2009), it already offers a way to think about how 
sadness and anger may be differentiated in the brain. A key principle to 
notice here is that the circuits for value and policy learning closely 
interact with one another. In fact, policy updates are thought to be 
guided by learned values, and brain-stem dopaminergic prediction error 
signals drive both types of learning. Thus, dissociating these two circuits 
would require carefully designed theory-driven manipulations and an 
ability to differentiate between neighboring and interacting neural 
populations. 
8.3. Prospection vs retrospection 
Our account distinguishes between emotions that are evoked by 
prospection concerning what may or may not happen (e.g., fear and 
desire) and emotions that reflect learning from what has already 
happened (e.g., happiness and anger). Despite having been proposed by 
the very person who is thought to have coined the term ‘emotion’ 
(Brown, 1846), such distinction between prospective and retrospective 
emotion has since been oddly absent from the literature (with the 
notable exception of Nesse and Ellsworth, 2009). Computationally, we 
propose this distinction is most precisely defined by saying that retro­
spective emotions are evoked by actual changes in expected value that 
are believed to have happened (‘happened’ only in the sense that the 
expected value has already changed, not in the sense that it already 
materialized and was consumed as reward), whereas prospective 
emotion are evoked by potential changes in value which may or may not 
happen. Empirically, this distinction is marked by the fact that pro­
spective emotions intensify with time as the prospect they are concerned 
with draws near (Mobbs et al., 2007), whereas retrospective emotion are 
typically maximal when evoked and then decay with time (Rutledge 
et al., 2014). 
The computations we proposed prospective and retrospective emo­
tions mediate map onto what has been widely characterized in the 
literature as model-based and model-free reinforcement learning, 
respectively (Daw and Dayan, 2014; Daw and O’Doherty, 2014; Sutton, 
1990). Thus, the large body of literature investigating how model-based 
and model-free learning are implemented in the brain could shed light 
on the neural basis of prospective and retrospective emotion. An overlap 
between these two types of emotion is suggested by the finding that both 
model-based and model-free learning are correlated with activity in the 
human striatum (Daw et al., 2011). Yet the two systems are also neurally 
distinguished in that model-free learning was found to be associated 
with reward prediction error signals in the putamen, whereas 
model-based learning associates with activity in the dorsomedial pre­
frontal cortex (Doll et al., 2015). Thus, here too, a picture of partially 
overlapping and partially distinct neural circuits emerges. 
Further undermining the separation between these two circuits is the 
likely possibility that model-based prospection itself contributes to 
model-free learning. This contribution may take at least two main forms: 
model-based inferences may guide model-free credit assignment during 
actual experience (Moran et al., 2021), and the model-free system could 
learn from model-based simulation of possible experiences (Gershman 
et al., 2014; Mattar and Daw, 2018; Russek et al., 2017; Sutton, 1990). 
Indeed, recent studies indicate that simulating sequences of possible 
future states enables people to update their values and policy prior to 
actual experience (Eldar et al., 2020; Liu et al., 2019, 2021). It is easy to 
imagine how this such prospective simulation, by acting as a substitute 
for actual experience, could evoke retrospective emotions such as 
happiness and anger. 
8.4. Mood 
We proposed that moods serve to generalize inferences to subsequent 
experiences and prospects. To date, we are aware of only one study that 
investigated the neural substrates of this generalizing impact in humans 
(Vinckier et al., 2018). The findings indicates that the generalizing 
impact of a positive emotional state are mediated by activity in the 
ventromedial prefrontal cortex, whereas those of a negative emotional 
state are mediated by activity in the insula. Further research is required 
to substantiate these findings in other experimental settings, as well as to 
investigate different types and timescales of mood. Particularly prom­
ising in this respect is the development of animal models of affective 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 12

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
12
biases (Hales et al., 2014). Manipulating rodents’ emotional states biases 
their judgements in a manner that is broadly consistent with the ideas 
proposed here. Developing animal models of affective biases that 
correspond to distinct emotions is a promising target for future research. 
9. Relationship with other theoretical accounts 
9.1. Other computational accounts 
Our account builds on several previous suggestions concerning the 
computations that emotions mediate, which to date have not been 
jointly considered. Here we integrated these proposed computations 
into a unified framework that clarifies each computation’s role and the 
relations between them. Thus, the valence of one’s mood has previously 
been suggested to represent either changes in value (Eldar et al., 2016; 
and see Joffily and Coricelli, 2013 for a similar suggestion formalized 
using the free energy framework) or action effectiveness (i.e., integrated 
advantage; Bennett et al., 2021). As these two types of computation 
warrant different behavioral responses, we proposed that they are rep­
resented by different classes of emotions (happiness/sadness vs. con­
tent/anger) that motivate different types of behavior (activity/inactivity 
vs. behavioral perseverance/change). 
Similarly, computations of uncertainty have been previously sug­
gested to be represented by people’s anticipatory emotions (Hagen, 
1991) and levels of stress (Peters et al., 2017). The term ‘stress’ has 
different definitions and is not universally recognized as an emotional 
state, but it is closest to what in the emotion literature is typically 
referred to as anxiety. Indeed, our definition of anxiety in the present 
paper includes uncertainty as a precondition, since there is no use trying 
to prevent inevitable or impossible prospects. However, for the same 
reason, we propose that anxiety should scale only with uncertainty that 
is potentially reducible through our control over the environment. 
Additionally, Peters et al.’s definition of stress does not distinguish be­
tween uncertainty about a prospect and the change in value it would 
bring should it materialize. Here, we proposed that both factors interact 
in determining a person’s level of anxiety. 
Defining the computations each emotion represents (i.e., at Marr’s 
computational level of analysis; Marr, 2010) opens the way to investi­
gating algorithmic characteristics of these computations. Of particular 
interest is the common notion that emotions act as heuristics, in the 
sense that they do not represent optimal computations, but rather, 
cost-saving mental shortcuts. To test this idea, however, we first need to 
agree on what computation a particular emotion may represent, and 
only then can we ask whether emotions mediate these computations 
optimally or not. So far, this question has not been properly studied or 
even explicitly asked, likely due to a lack of clarity about the compu­
tations involved. We suspect that once the question is posed in this way, 
the common view of emotions as a type of heuristics that provides 
oversimplified answers to complicated problems might be put into 
doubt. Indeed, we have recently highlighted how rational inferences 
concerning higher order constructs such as global changes in value may 
often be mistaken for heuristics (Sharp et al., 2022). Briefly, the reason is 
that such inferences represent general properties of the environment (or 
of one’s state in it) that predict individual outcomes only on average, 
and can thus seem extraneous to a naïve observer focusing on an indi­
vidual case. Instead, we propose, such inferences are best viewed as a 
rational consequence of operating with limited information in an un­
certain world. 
9.2. The circumplex model of emotion 
Previous work linking emotion to the processing of reward and 
punishment has primarily considered emotion as described by the cir­
cumplex model (Russell, 1980). This influential model maps different 
emotions onto a two-dimensional space of valence and arousal. Within 
this space, it is suggested that reward drives emotional states of high 
arousal and positive valence, whereas punishment drives states of high 
arousal and negative valence. Failing to obtain reward is thought to be 
associated with a more complex pattern beginning with high-arousal 
and then culminating in low-arousal negative states (Mendl et al., 
2010). Our account differs from this idea by invoking distinct emotions, 
and the computations associated with them, to mediate the impact of 
reward and punishment on valence and arousal. The result can be 
thought of as a three-dimensional space of emotion, with the additional 
dimension distinguishing between retrospective and prospective emo­
tions (Fig. 4). 
Our account and previous accounts make fairly similar predictions 
with regards to prospective emotions, but substantial differences exist 
with regards to retrospective emotions. First, we propose that retro­
spective emotions represent value differences, not reward pe se (Eldar 
et al., 2021). Second, our account suggests that an important dimension 
of emotion is the degree to which outcomes are attributed to actions, 
which determines where emotion lies on the continuum between anger 
and sadness. Third, our account predicts that a similar emotion will be 
evoked by decreases in expected punishment as by increases in expected 
reward. The evidence reviewed throughout this manuscript already 
provides support for some of these unique predictions, but future 
research could more exhaustively study points of disagreement with 
previous theory. 
9.3. Appraisal and evolutionary accounts 
In offering computational roles for emotions, our account is inher­
ently grounded in appraisal theory (Clore and Ortony, 2000; Ellsworth, 
2013; Frijda, 1986; Lazarus, 1991; Moors et al., 2013; Scherer, 1984) 
and evolutionary accounts (Nesse and Ellsworth, 2009) of emotion. At 
the heart of appraisal theory is the assertion that emotions reflect 
cognitive judgments assessing the satisfaction of one’s needs by the 
environment. Although different theories hold different views on which 
variables are appraised, there is mostly a consensus regarding central 
variables such as goal relevance, goal congruence, certainty, coping 
potential and agency (Moors et al., 2013). The appraised variables 
associated with an emotion are thought to determine the circumstances 
that give rise to the emotion and the action the emotion favors (Lazarus, 
1991). Our account can be thought of as a mathematical formalization 
and specification of this broad idea. However, unlike basic appraisals, 
the computations we identify directly map onto distinct emotions, and 
thus improve on the explanatory power of appraisals in terms of 
parsimony. 
9.4. Social accounts 
Social accounts of emotion suggest that emotions have evolved in 
social animals in order to solve social situations that are critical to their 
survival (Keltner and Haidt, 1999, 2001). Most emblematic of the social 
function of emotions are the facial expressions with which they are 
associated. These expressions are regularly used to communicate 
emotional states (Adolphs, 2002; Ekman, 1992), and are often a main 
means of communication between infants and caregivers (Niedenthal 
and Brauer, 2012). Such a mechanism may have developed over 
evolutionary history in order to convey information to others regarding 
our own internal state. Of course, for this mechanism to be socially 
useful, there needs to be some degree of correspondence between the 
expressed emotion and one’s internal states. In other words, each 
emotion must be tied to a distinct cognitive process or computation. Our 
account proposes what these computations are. 
A related view is that emotional experiences in humans take place 
within a socially construed context and thus differences in such context, 
for instance between different cultures, result in different emotional 
reactions to similar events (Frijda and Mesquita, 1994). This may seem 
to suggest that the role of emotions cannot be uniform as we have 
proposed. However, the computations we delineated can have markedly 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 13

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
13
different results depending on one’s social environment. This is espe­
cially true since all these computations reflect in one way or another 
one’s reward function, which is highly dependent on what other people 
in one’s society value. Thus, our account agrees with social accounts of 
emotion that emotional responses will differ substantially across cul­
tures, yet we maintain that the computations underlying these responses 
will be similar. 
9.5. Constructionist accounts 
A major controversy among theories of emotion separates between 
basic emotions (Ekman, 1992; Sauter et al., 2010) and constructionist 
accounts (Barrett, 2006; Lindquist et al., 2013) of emotion. Unlike basic 
emotions accounts, constructionist accounts argue that the distinction 
between different emotions is not inherent to our biology. Rather, 
emotions are socially constructed in the sense that people learn what 
each emotion is from other people. We entirely concur with the idea that 
people learn to recognize emotions from social experience, and that 
there are differences in how emotions are understood by different people 
in different cultures. However, the widespread and effective use of 
emotion terms in common language requires that each of these terms 
will have a common meaning that is recognized by most people most of 
the time (Adolphs et al., 2019). Thus, like any socially constructed 
concept (consider for instance the set of objects the word ‘table’ maps 
onto), it is not unreasonable to expect that emotion terms will map with 
some regularity onto prevalent processes that characterize our external 
or internal worlds (Cunningham et al., 2013). It is these processes that 
our account aimed to delineate. Thus, ultimately, we believe that 
emotions can and should be viewed as both constructed and basic – 
constructed in terms of how people categorize and verbalize emotions, 
and basic in terms of the computations that emotions mediate. 
9.6. Detailed taxonomies 
Whereas our account proposes quantitative definitions mostly for a 
few primary emotions, a substantial body of work has developed more 
detailed categorizations of secondary emotions (Cowen et al., 2019; 
Jarymowicz and Imbir, 2015; Keltner, 2019; Shiota et al., 2017). These 
include emotions like guilt, jealousy, pride, gratitude, and love, which 
are often thought of as subtypes of the primary emotions. As an example 
of how our account could accommodate such diversity, in our discussion 
of emotions that evaluate others’ actions, we have sketched how the 
same computation may explain both guilt and moral indignation 
depending on the agent that suffers the poor outcome (see Fig. 3). A 
similar set of secondary emotions can also be derived in the domain of 
positive action effectiveness (e.g., ‘pride’ and ‘admiration’). Addition­
ally, by incorporating counterfactual information about what we could 
have done, computations of action effectiveness can capture the familiar 
emotion of regret. And extending this idea to a comparison between the 
outcomes we experience and those experienced by concrete other people 
could furnish a definition for the common emotion of jealousy (Farrell, 
1980; Salovey and Rodin, 1986). Future work can follow this approach 
to more comprehensively map these and other computations that sec­
ondary emotions mediate. 
10. Conclusion 
In this work, we offered a formal account of the human emotional 
landscape as composed of multiple interacting elements, each mediating 
a different type of computation. Together these elements serve to eval­
uate outcomes (pleasure & pain), to form expectations based on these 
evaluations (happiness & sadness), to favor actions that lead to more 
valuable outcomes (anger & content), and to identify valuable or 
harmful prospects we could plan for (fear & desire). Each of these 
emotions can also extend in time, as mood, and thus represent global 
inferences concerning the environment and oneself that are useful for 
informing subsequent computations. This quantitative account in­
tegrates a very large body of empirical research on emotion, but except 
for a handful of studies, most of this research has so far been qualitative. 
We are hopeful this work will inspire future quantitative studies which 
could formally test and develop the definitions set forth here, and 
investigate their implications for a broad range of human behaviors in 
health and disease. 
Acknowledgements 
We thank Peter Dayan, Daniel Bennett, Alexandre Y. Dombrovski, 
and Vanessa M. Brown for thoughtful comments and suggestions. 
Conflict of interest 
None. 
References 
Abend, R., Gold, A.L., Britton, J.C., Michalska, K.J., Shechner, T., Sachs, J.F., Winkler, A. 
M., Leibenluft, E., Averbeck, B.B., Pine, D.S., 2020. Anticipatory threat responding: 
associations with anxiety, development, and brain structure. Biol. Psychiatry 87 
(10), 916–925. 
Fig. 4. Proposed impact of reward within the emotion circumplex. The impact differs for changes in expected reward that have already happened (retrospective) and 
those that may happen in the future (prospective). Note that ‘reward’ in our account refers to a reward function that sums across both rewarding (positive) and 
punishing (negative) attributes of states and actions. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 14

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
14
Adolphs, R., 2002. Neural systems for recognizing emotion. Curr. Opin. Neurobiol. 12 
(2), 169–177. 
Adolphs, R., Mlodinow, L., Barrett, L.F., 2019. What is an emotion? Curr. Biol. 29 (20), 
R1060–R1064. 
Akiskal, H.S., Akiskal, K.K., Haykal, R.F., Manning, J.S., Connor, P.D., 2005. TEMPS-A: 
progress towards validation of a self-rated clinical version of the Temperament 
Evaluation of the Memphis, Pisa, Paris, and San Diego Autoquestionnaire. J. Affect. 
Disord. 85 (1–2), 3–16. 
Anderson, D.J., Adolphs, R., 2014. A framework for studying emotions across species. 
Cell 157 (1), 187–200. 
Ask, K., Pina, A., 2011. On being angry and punitive: How anger alters perception of 
criminal intent. Soc. Psychol. Personal. Sci. 2 (5), 494–499. 
Averbeck, B., O’Doherty, J.P., 2022. Reinforcement-learning in fronto-striatal circuits. 
Neuropsychopharmacology 47 (1), 147–162. 
Averill, J.R., 1968. Grief: its nature and significance. Psychol. Bull. 70, 721, 6p1.  
Averill, J.R., 1983. Studies on anger and aggression: Implications for theories of emotion. 
Am. Psychol. 38 (11), 1145. 
Aylward, J., Valton, V., Ahn, W.-Y., Bond, R.L., Dayan, P., Roiser, J.P., Robinson, O.J., 
2019. Altered learning under uncertainty in unmedicated mood and anxiety 
disorders. Nat. Hum. Behav. 3 (10), 1116–1123. 
Bach, D.R., 2021. Cross-species anxiety tests in psychiatry: pitfalls and promises. Mol. 
Psychiatry 1–10. 
Bach, D.R., Dayan, P., 2017. Algorithms for survival: a comparative perspective on 
emotions. Nat. Rev. Neurosci. 18 (5), 311–319. 
Baird, L.C. (1994). Reinforcement learning in continuous time: Advantage updating. 
Proceedings of 1994 IEEE International Conference on Neural Networks (ICNN’94), 4, 
2448–2453. 
Baker, C.L., Saxe, R., Tenenbaum, J.B., 2009. Action understanding as inverse planning. 
Cognition 113 (3), 329–349. 
Bar-Haim, Y., Lamy, D., Pergamin, L., Bakermans-Kranenburg, M.J., Van Ijzendoorn, M. 
H., 2007. Threat-related attentional bias in anxious and nonanxious individuals: a 
meta-analytic study. Psychol. Bull. 133 (1), 1. 
Barrett, L.F., 2006. Are emotions natural kinds? Perspect. Psychol. Sci. 1 (1), 28–58. 
Barrett, L.F., 2017. The theory of constructed emotion: an active inference account of 
interoception and categorization. Soc. Cogn. Affect. Neurosci. 12 (1), 1–23. 
Barto, A.G. (1995). Adaptive critics and the basal ganglia. 
Bartra, O., McGuire, J.T., Kable, J.W., 2013. The valuation system: a coordinate-based 
meta-analysis of BOLD fMRI experiments examining neural correlates of subjective 
value. Neuroimage 76, 412–427. 
Bennett, D., Davidson, G., Niv, Y., 2021. A model of mood as integrated advantage. 
Psychol. Rev. 
Bennett, D., Niv, Y., Langdon, A.J., 2021. Value-free reinforcement learning: policy 
optimization as a minimal model of operant behavior. Curr. Opin. Behav. Sci. 41, 
114–121. 
Bentham, J., 1838. Teoría de las penas y de las recompensas. Imprenta de Manuel Saurí. 
Berkowitz, L. (1999). Anger. Handbook of Cognition and Emotion, 409–428. 
Berridge, K.C., 1996. Food reward: brain substrates of wanting and liking. Neurosci. 
Biobehav. Rev. 20 (1), 1–25. 
Berridge, K.C., 2007. The debate over dopamine’s role in reward: the case for incentive 
salience. Psychopharmacology 191 (3), 391–431. 
Berridge, K.C., 2019. Affective valence in the brain: modules or modes? Nat. Rev. 
Neurosci. 20 (4), 225–234. 
Berridge, K.C., Dayan, P., 2021. Liking. Curr. Biol. 31 (24), R1555–R1557. 
Berridge, K.C., Robinson, T.E., 2016. Liking, wanting, and the incentive-sensitization 
theory of addiction. Am. Psychol. 71 (8), 670. 
Berridge, K.C., Robinson, T.E., Aldridge, J.W., 2009. Dissecting components of reward: 
‘liking’,‘wanting’, and learning. Curr. Opin. Pharmacol. 9 (1), 65–73. 
Birch, L.L., 1999. Development of food preferences. Annu. Rev. Nutr. 19 (1), 41–62. 
Blain, B., Rutledge, R.B., 2020. Momentary subjective well-being depends on learning 
and not reward. Elife 9, e57977. 
Bolles, R.C., Fanselow, M.S., 1980. A perceptual-defensive-recuperative model of fear 
and pain. Behav. Brain Sci. 3 (2), 291–301. 
Brown, T., 1846. Lectures on the Philosophy of the Mind, Vol. 4. William Tait. 
Brown, V.M., Zhu, L., Solway, A., Wang, J.M., McCurry, K.L., King-Casas, B., Chiu, P.H., 
2021. Reinforcement learning disruptions in individuals with depression and 
sensitivity to symptom change following cognitive behavioral therapy. JAMA 
Psychiatry 78 (10), 1113–1122. 
Carver, C.S. (2004). Self-regulation of action and affect. 
Carpenter, R.W., Trull, T.J., 2013. Components of emotion dysregulation in borderline 
personality disorder: A review. Current psychiatry reports 15 (1), 1–8. 
Carver, C.S., Harmon-Jones, E., 2009. Anger is an approach-related affect: evidence and 
implications. Psychol. Bull. 135 (2), 183. 
Chang, L.J., Smith, A., 2015. Social emotions and psychological games. Curr. Opin. 
Behav. Sci. 5, 133–140. 
Chiu, P.H., Deldin, P.J., 2007. Neural evidence for enhanced error detection in major 
depressive disorder. Am. J. Psychiatry 164 (4), 608–616. 
Clore, G.L., 1992. Cognitive phenomenology: Feelings and the construction of judgment. 
Constr. Soc. Judgm. 10, 133–163. 
Clore, G.L., Ortony, A., 2000. Cognition in emotion: Always, sometimes, or never. Cogn. 
Neurosci. Emot. 24–61. 
Coricelli, G., Critchley, H.D., Joffily, M., O’Doherty, J.P., Sirigu, A., Dolan, R.J., 2005. 
Regret and its avoidance: a neuroimaging study of choice behavior. Nat. Neurosci. 8 
(9), 1255–1262. 
Cowen, A., Sauter, D., Tracy, J.L., Keltner, D., 2019. Mapping the passions: toward a 
high-dimensional taxonomy of emotional experience and expression. Psychol. Sci. 
Public Interest 20 (1), 69–90. 
Cunningham, M.R., 1988. What do you do when you’re happy or blue? Mood, 
expectancies, and behavioral interest. Motiv. Emot. 12 (4), 309–331. 
Cunningham, W.A., Dunfield, K.A., Stillman, P.E., 2013. Emotional states from affective 
dynamics. Emot. Rev. 5 (4), 344–355. 
Dabney, W., Rowland, M., Bellemare, M., & Munos, R. (2018). Distributional 
reinforcement learning with quantile regression. Proceedings of the AAAI Conference 
on Artificial Intelligence , 32. 
Darwin, C., 2015. The Expression of the Emotions in Man and Animals. University of 
Chicago Press. 
Davidson, R.J., Irwin, W., 1999. The functional neuroanatomy of emotion and affective 
style. Trends Cogn. Sci. 3 (1), 11–21. 
Davis, M., Falls, W.A., Campeau, S., Kim, M., 1993. Fear-potentiated startle: a neural and 
pharmacological analysis. Behav. Brain Res. 58 (1–2), 175–198. 
Daw, N.D., Dayan, P., 2014. The algorithmic anatomy of model-based evaluation. Philos. 
Trans. R. Soc. B: Biol. Sci. 369 (1655), 20130478. 
Daw, N.D., O’Doherty, J.P., 2014. Multiple systems for value learning. Neuroeconomics. 
Elsevier, pp. 393–410. 
Daw, N.D., Gershman, S.J., Seymour, B., Dayan, P., Dolan, R.J., 2011. Model-based 
influences on humans’ choices and striatal prediction errors. Neuron 69 (6), 
1204–1215. 
Dayan, P. (2021). ’liking’as a First Draft of the Affective Future. 
De Quervain, D.J.-F., Fischbacher, U., Treyer, V., Schellhammer, M., Schnyder, U., 
Buck, A., Fehr, E., 2004. The neural basis of altruistic punishment. Science 305 
(5688), 1254–1258. 
Demiralp, E., Thompson, R.J., Mata, J., Jaeggi, S.M., Buschkuehl, M., Barrett, L.F., 
Ellsworth, P.C., Demiralp, M., Hernandez-Garcia, L., Deldin, P.J., 2012. Feeling blue 
or turquoise? Emotional differentiation in major depressive disorder. Psychol. Sci. 23 
(11), 1410–1416. 
DeSteno, D., Petty, R.E., Wegener, D.T., Rucker, D.D., 2000. Beyond valence in the 
perception of likelihood: the role of emotion specificity. J. Personal. Soc. Psychol. 78 
(3), 397. 
Diener, E., Emmons, R.A., 1984. The independence of positive and negative affect. 
J. Personal. Soc. Psychol. 47 (5), 1105. 
Doll, B.B., Simon, D.A., Daw, N.D., 2012. The ubiquity of model-based reinforcement 
learning. Curr. Opin. Neurobiol. 22 (6), 1075–1081. 
Doll, B.B., Duncan, K.D., Simon, D.A., Shohamy, D., Daw, N.D., 2015. Model-based 
choices involve prospective neural activity. Nat. Neurosci. 18 (5), 767–772. 
Dollard, J., Miller, N.E., Doob, L.W., Mowrer, O.H., & Sears, R.R. (1939). Frustration and 
aggression. 
Ekman, P., 1992. Facial expressions of emotion: an old controversy and new findings. 
Philos. Trans. R. Soc. Lond. Ser. B: Biol. Sci. 335 (1273), 63–69. 
Ekman, P., 1999. Basic emotions. Handb. Cogn. Emot. 98 (45–60), 16. 
Ekman, P., Friesen, W.V., O’sullivan, M., Chan, A., Diacoyanni-Tarlatzis, I., Heider, K., 
Krause, R., LeCompte, W.A., Pitcairn, T., Ricci-Bitti, P.E., 1987. Universals and 
cultural differences in the judgments of facial expressions of emotion. J. Personal. 
Soc. Psychol. 53 (4), 712. 
Eldar, E., Niv, Y., 2015. Interaction between emotional state and learning underlies mood 
instability. Nat. Commun. 6 (1), 1–10. 
Eldar, E., Rutledge, R.B., Dolan, R.J., Niv, Y., 2016. Mood as representation of 
momentum. Trends Cogn. Sci. 20 (1), 15–24. 
Eldar, E., Li`evre, G., Dayan, P., Dolan, R.J., 2020. The roles of online and offline replay in 
planning. ELife 9, e56911. 
Eldar, E., Pessiglione, M., van Dillen, L., 2021. Positive affect as a computational 
mechanism. Curr. Opin. Behav. Sci. 39, 52–57. 
Ellsworth, P.C., 2013. Appraisal theory: old and new questions. Emot. Rev. 5 (2), 
125–131. 
Farrell, D.M., 1980. Jealousy. Philos. Rev. 89 (4), 527–559. 
Feifel, H., 1974. Religious conviction and fear of death among the healthy and the 
terminally ill. J. Sci. Study Relig. 353–360. 
FeldmanHall, O., Chang, L.J., 2018. Social learning: emotions aid in optimizing goal- 
directed social behavior. Goal-directed Decision Making. Elsevier, pp. 309–330. 
Frijda, N.H. (2001a). The nature of pleasure. 
Fernandez, E., Johnson, S.L., 2016. Anger in psychological disorders: Prevalence, 
presentation, etiology and prognostic implications. Clinical Psychology Review 46, 
124–135. 
Frijda, N.H., 1986. The Emotions. Cambridge University Press. 
Frijda, N.H., 1987. Emotion, cognitive structure, and action tendency. Cogn. Emot. 1 (2), 
115–143. 
Frijda, N.H., 1993. The place of appraisal in emotion. Cogn. Emot. 7 (3–4), 357–387. 
Frijda, N.H., 2001b. The nature of pleasure. In: Bargh, J.A., Apsley, D.K. (Eds.), 
Unraveling the Complexities of Social Life: A Festschrift in Honor of Robert B. 
Zajonc. American Psychological Association, pp. 71–94. https://doi.org/10.1037/ 
10387-006. 
Frijda, N.H., & Mesquita, B. (1994). The social roles and functions of emotions. 
Friston, K., 2009. The free-energy principle: a rough guide to the brain? Trends Cogn. Sci. 
13 (7), 293–301. 
Friston, K., FitzGerald, T., Rigoli, F., Schwartenbeck, P., Pezzulo, G., 2016. Active 
inference and learning. Neurosci. Biobehav. Rev. 68, 862–879. 
Garivier, A., Moulines, E., 2011. On upper-confidence bound policies for switching 
bandit problems. Int. Conf. Algorithm Learn. Theory 174–188. 
Gershman, S.J., Markman, A.B., Otto, A.R., 2014. Retrospective revaluation in sequential 
decision making: a tale of two systems. J. Exp. Psychol.: Gen. 143 (1), 182. 
Ghoniem, A., van Dillen, L.F., Hofmann, W., 2020. Choice architecture meets motivation 
science: How stimulus availability interacts with internal factors in shaping the 
desire for food. Appetite 155, 104815. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 15

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
15
Gillan, C.M., Kalanthroff, E., Evans, M., Weingarden, H.M., Jacoby, R.J., 
Gershkovich, M., Snorrason, I., Campeas, R., Cervoni, C., Crimarco, N.C., 2020. 
Comparison of the association between goal-directed planning and self-reported 
compulsivity vs obsessive-compulsive disorder diagnosis. JAMA Psychiatry 77 (1), 
77–85. 
Gl¨ascher, J., Daw, N., Dayan, P., O’Doherty, J.P., 2010. States versus rewards: 
dissociable neural prediction error signals underlying model-based and model-free 
reinforcement learning. Neuron 66 (4), 585–595. 
Goldberg, D., Fawcett, J., 2012. The importance of anxiety in both major depression and 
bipolar disorder. Depress Anxiety 29 (6), 471–478. 
Goldberg, J.H., Lerner, J.S., Tetlock, P.E., 1999. Rage and reason: the psychology of the 
intuitive prosecutor. Eur. J. Soc. Psychol. 29 (5-6), 781–795. 
Greenberg, P.E., Kessler, R.C., Birnbaum, H.G., Leong, S.A., Lowe, S.W., Berglund, P.A., 
Corey-Lisle, P.K., 2003. The economic burden of depression in the United States: 
how did it change between 1990 and 2000? J. Clin. Psychiatry 64 (12), 1465–1475. 
Grondman, I., Busoniu, L., Lopes, G.A., Babuska, R., 2012. A survey of actor-critic 
reinforcement learning: standard and natural policy gradients. IEEE Trans. Syst. Man 
Cybern. Part C 42 (6), 1291–1307. 
Grupe, D.W., Nitschke, J.B., 2013. Uncertainty and anticipation in anxiety: an integrated 
neurobiological and psychological perspective. Nat. Rev. Neurosci. 14 (7), 488–501. 
Haarnoja, T., Zhou, A., Abbeel, P., Levine, S., 2018. Soft actor-critic: Off-policy maximum 
entropy deep reinforcement learning with a stochastic actor. Int. Conf. Mach. Learn. 
1861–1870. 
Hagen, O., 1991. Decisions under risk: a descriptive model and a technique for decision 
making. Eur. J. Polit. Econ. 7 (3), 381–405. 
Halahhakoon, C., Kaltenboeck, A., Martens, M., Geddes, J.G., Harmer, C.J., Cowen, P., & 
Browning, M. (2022). Pramipexole Enhances Reward Learning by Preserving Value 
Estimates. MedRxiv. 
Hales, C.A., Stuart, S.A., Anderson, M.H., Robinson, E.S., 2014. Modelling cognitive 
affective biases in major depressive disorder using rodents. Br. J. Pharmacol. 171 
(20), 4524–4538. 
Hamann, S., 2012. Mapping discrete and dimensional emotions onto the brain: 
controversies and consensus. Trends Cogn. Sci. 16 (9), 458–466. 
Harmatz, M.G., Well, A.D., Overtree, C.E., Kawamura, K.Y., Rosal, M., Ockene, I.S., 2000. 
Seasonal variation of depression and other moods: a longitudinal approach. J. Biol. 
Rhythms 15 (4), 344–350. 
Harmon-Jones, E., Sigelman, J., 2001. State anger and prefrontal brain activity: evidence 
that insult-related relative left-prefrontal activation is associated with experienced 
anger and aggression. J. Personal. Soc. Psychol. 80 (5), 797. 
Hazlett, L.I., Moieni, M., Irwin, M.R., Haltom, K.E.B., Jevtic, I., Meyer, M.L., Breen, E.C., 
Cole, S.W., Eisenberger, N.I., 2021. Exploring neural mechanisms of the health 
benefits of gratitude in women: a randomized controlled trial. Brain Behav. Immun. 
Helm, B.W., 2002. Felt evaluations: a theory of pleasure and pain. Am. Philos. Q. 39 (1), 
13–30. 
Houben, M., Kuppens, P., 2020. Emotion dynamics and the association with depressive 
features and borderline personality disorder traits: Unique, specific, and prospective 
relationships. Clinical Psychological Science 8 (2), 226–239. 
Houben, M., Van Den Noortgate, W., Kuppens, P., 2015. The relation between short-term 
emotion dynamics and psychological well-being: a meta-analysis. Psychol. Bull. 141 
(4), 901. 
Houk, J.C., & Adams, J.L. (1995). 13 A Model of How the Basal Ganglia Generate and 
Use Neural Signals That. Models of Information Processing in the Basal Ganglia, 249. 
Huys, Q.J., Browning, M., 2021. A Computational View on the Nature of Reward and 
Value in Anhedonia. Springer. 
Huys, Q.J., Renz, D., 2017. A formal valuation framework for emotions and their control. 
Biol. Psychiatry 82 (6), 413–420. 
Huys, Q.J., Pizzagalli, D.A., Bogdan, R., Dayan, P., 2013. Mapping anhedonia onto 
reinforcement learning: a behavioural meta-analysis. Biol. Mood Anxiety Disord. 3 
(1), 1–16. 
Jackson, T., Yang, Z., Li, X., Chen, H., Huang, X., Meng, J., 2012. Coping when pain is a 
potential threat: the efficacy of acceptance versus cognitive distraction. Eur. J. Pain 
16 (3), 390–400. 
Jacobson, H., 2021. The role of valence in perception: an ARTistic treatment. Philos. Rev. 
130 (4), 481–531. 
Jansson, L., Nordgaard, J., 2016. The Psychiatric Interview for Differential Diagnosis, 
Vol. 270. Springer. 
Jarymowicz, M.T., Imbir, K.K., 2015. Toward a human emotions taxonomy (based on 
their automatic vs. reflective origin). Emot. Rev. 7 (2), 183–188. 
Joel, D., Weiner, I., 2000. Striatal contention scheduling and the split circuit scheme of 
basal ganglia-thalamocortical circuitry: from anatomy to behaviour. Brain Dynamics 
and the Striatal Complex. CRC Press, pp. 221–248. 
Joffily, M., Coricelli, G., 2013. Emotional valence and the free-energy principle. PLoS 
Comput. Biol. 9 (6), e1003094. 
Jones, R.M., Somerville, L.H., Li, J., Ruberry, E.J., Libby, V., Glover, G., Voss, H.U., 
Ballon, D.J., Casey, B.J., 2011. Behavioral and neural properties of social 
reinforcement learning. J. Neurosci. 31 (37), 13039–13045. 
Juechems, K., Summerfield, C., 2019. Where does value come from? Trends Cogn. Sci. 23 
(10), 836–850. 
Kable, J.W., Glimcher, P.W., 2009. The neurobiology of decision: consensus and 
controversy. Neuron 63 (6), 733–745. 
Kahneman, D., Miller, D.T., 1986. Norm theory: comparing reality to its alternatives. 
Psychol. Rev. 93 (2), 136. 
Keltner, D., 2019. Toward a consensual taxonomy of emotions. Cogn. Emot. 33 (1), 
14–19. 
Keltner, D., Haidt, J., 1999. Social functions of emotions at four levels of analysis. Cogn. 
Emot. 13 (5), 505–521. 
Keltner, D., & Haidt, J. (2001). Social functions of emotions. 
Keltner, D., Ellsworth, P.C., Edwards, K., 1993. Beyond simple pessimism: effects of 
sadness and anger on social perception. J. Personal. Soc. Psychol. 64 (5), 740. 
Keltner, D., Kring, A.M., 1998. Emotion, social function, and psychopathology. Review of 
general Psychology 2 (3), 320–342. 
Keramati, M., Gutkin, B., 2014. Homeostatic reinforcement learning for integrating 
reward collection and physiological stability. Elife 3, e04811. 
Ketai, R., 1975. Affect, mood, emotion, and feeling: Semantic considerations. Am. J. 
Psychiatry. 
Konda, V.R., Tsitsiklis, J.N., 2000. Actor-critic algorithms. Adv. Neural Inf. Process. Syst. 
1008–1014. 
Kragel, P.A., Knodt, A.R., Hariri, A.R., LaBar, K.S., 2016. Decoding spontaneous 
emotional states in the human brain. PLoS Biol. 14 (9), e2000106. 
Kreibig, S.D., 2010. Autonomic nervous system activity in emotion: a review. Biol. 
Psychol. 84 (3), 394–421. 
Kurzban, R., Duckworth, A., Kable, J.W., Myers, J., 2013. An opportunity cost model of 
subjective effort and task performance. Behav. Brain Sci. 36 (6), 661–679. 
Kutscher, L., Feldman, G., 2019. The impact of past behaviour normality on regret: 
replication and extension of three experiments of the exceptionality effect. Cogn. 
Emot. 33 (5), 901–914. 
Launius, M.H., Lindquist, C.U., 1988. Learned helplessness, external locus of control, and 
passivity in battered women. J. Interpers. Violence 3 (3), 307–318. 
Lazarus, R.S., 1991. Progress on a cognitive-motivational-relational theory of emotion. 
Am. Psychol. 46 (8), 819. 
Lazarus, R.S., Lazarus, R.S., 1991. Emotion and Adaptation. Oxford University Press on 
Demand. 
Le Heron, C., Kolling, N., Plant, O., Kienast, A., Janska, R., Ang, Y.-S., Fallon, S., 
Husain, M., Apps, M.A., 2020. Dopamine modulates dynamic decision-making 
during foraging. J. Neurosci. 40 (27), 5273–5282. 
LeDoux, J.E., 2000. Emotion circuits in the brain. Annu. Rev. Neurosci. 23 (1), 155–184. 
LeDoux, J.E., 2014. Coming to terms with fear. Proc. Natl. Acad. Sci. U.S.A. 111 (8), 
2871–2878. 
LeDoux, J.E., Pine, D.S., 2016. Using neuroscience to help understand fear and anxiety: a 
two-system framework. Am. J. Psychiatry. 
Leith, K.P., Baumeister, R.F., 1998. Empathy, shame, guilt, and narratives of 
interpersonal conflicts: Guilt-prone people are better at perspective taking. 
J. Personal. 66 (1), 1–37. 
Lemay Jr, E.P., Overall, N.C., Clark, M.S., 2012. Experiences and interpersonal 
consequences of hurt feelings and anger. J. Personal. Soc. Psychol. 103 (6), 982. 
Lench, H.C., Flores, S.A., Bench, S.W., 2011. Discrete emotions predict changes in 
cognition, judgment, experience, behavior, and physiology: a meta-analysis of 
experimental emotion elicitations. Psychol. Bull. 137 (5), 834. 
Lench, H.C., Tibbett, T.P., Bench, S.W., 2016. Exploring the toolkit of emotion: What do 
sadness and anger do for us? Soc. Personal. Psychol. Compass 10 (1), 11–25. 
Lerner, J.S., Keltner, D., 2000. Beyond valence: Toward a model of emotion-specific 
influences on judgement and choice. Cogn. Emot. 14 (4), 473–493. 
Lerner, J.S., Tiedens, L.Z., 2006. Portrait of the angry decision maker: How appraisal 
tendencies shape anger’s influence on cognition. J. Behav. Decis. Mak. 19 (2), 
115–137. 
Lerner, T.N., Shilyansky, C., Davidson, T.J., Evans, K.E., Beier, K.T., Zalocusky, K.A., 
Crow, A.K., Malenka, R.C., Luo, L., Tomer, R., 2015. Intact-brain analyses reveal 
distinct information carried by SNc dopamine subcircuits. Cell 162 (3), 635–647. 
Levine, L.J., 1996. The anatomy of disappointment: a naturalistic test of appraisal models 
of sadness, anger, and hope. Cogn. Emot. 10 (4), 337–360. 
Levine, L.J., Pizarro, D.A., 2004. Emotion and memory research: a grumpy overview. 
Soc. Cogn. 22 (5), 530–554. 
Levy, D.J., Glimcher, P.W., 2012. The root of all value: a neural common currency for 
choice. Curr. Opin. Neurobiol. 22 (6), 1027–1038. 
Levy, I., Schiller, D., 2021. Neural computations of threat. Trends Cogn. Sci. 25 (2), 
151–171. 
Lieder, F., Goodman, N.D., Huys, Q.J., 2013. Learned helplessness and generalization. 
Proc. Annu. Meet. Cogn. Sci. Soc. 35. 
Ligneul, R., Mainen, Z.F., Ly, V., Cools, R., 2022. Stress-sensitive inference of task 
controllability. Nat. Hum. Behav. 1–11. 
Lindquist, K.A., Wager, T.D., Kober, H., Bliss-Moreau, E., Barrett, L.F., 2012. The brain 
basis of emotion: a meta-analytic review. Behav. Brain Sci. 35 (3), 121. 
Lindquist, K.A., Siegel, E.H., Quigley, K.S., & Barrett, L.F. (2013). The hundred-year 
emotion war: are emotions natural kinds or psychological constructions? Comment on 
Lench, Flores, and Bench (2011). 
Liu, Y., Dolan, R.J., Kurth-Nelson, Z., Behrens, T.E., 2019. Human replay spontaneously 
reorganizes experience. Cell 178 (3), 640–652 e14.  
Liu, Y., Mattar, M.G., Behrens, T.E., Daw, N.D., Dolan, R.J., 2021. Experience replay is 
associated with efficient nonlocal learning. Science 372, 6544. 
Loomes, G., Sugden, R., 1982. Regret theory: an alternative theory of rational choice 
under uncertainty. Econ. J. 92 (368), 805–824. 
Luthans, F., Jensen, S.M., 2002. Hope: A new positive strength for human resource 
development. Hum. Resour. Dev. Rev. 1 (3), 304–322. 
MacLeod, C., Mathews, A., Tata, P., 1986. Attentional bias in emotional disorders. 
J. Abnorm. Psychol. 95 (1), 15. 
Maier, S.F., Seligman, M.E., 1976. Learned helplessness: theory and evidence. J. Exp. 
Psychol.: Gen. 105 (1), 3. 
Marr, D. (2010). Vision: A computational investigation into the human representation and 
processing of visual information. 
Marteau, T.M., Bekker, H., 1992. The development of a six-item short-form of the state 
scale of the Spielberger State—Trait Anxiety Inventory (STAI). Br. J. Clin. Psychol. 
31 (3), 301–306. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 16

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
16
Mathys, C., Daunizeau, J., Friston, K.J., Stephan, K.E., 2011. A Bayesian foundation for 
individual learning under uncertainty. Front. Hum. Neurosci. 5, 39. 
Matsunaga, M., Isowa, T., Kimura, K., Miyakoshi, M., Kanayama, N., Murakami, H., 
Sato, S., Konagaya, T., Nogimori, T., Fukuyama, S., 2008. Associations among 
central nervous, endocrine, and immune activities when positive emotions are 
elicited by looking at a favorite person. Brain Behav. Immun. 22 (3), 408–417. 
Mattar, M.G., Daw, N.D., 2018. Prioritized memory access explains planning and 
hippocampal replay. Nat. Neurosci. 21 (11), 1609–1617. 
McCabe, C., Mishor, Z., Cowen, P.J., Harmer, C.J., 2010. Diminished neural processing of 
aversive and rewarding stimuli during selective serotonin reuptake inhibitor 
treatment. Biol. Psychiatry 67 (5), 439–445. 
McClure, S.M., Daw, N.D., Montague, P.R., 2003. A computational substrate for incentive 
salience. Trends Neurosci. 26 (8), 423–428. 
McClure, S.M., Gilzenrat, M.S., Cohen, J.D., 2005. An exploration-exploitation model 
based on norepinepherine and dopamine activity. Adv. Neural Inf. Process. Syst. 18. 
McCracken, L.M., Keogh, E., 2009. Acceptance, mindfulness, and values-based action 
may counteract fear and avoidance of emotions in chronic pain: an analysis of 
anxiety sensitivity. J. Pain 10 (4), 408–415. 
McGowan, N.M., Goodwin, G.M., Bilderbeck, A.C., Saunders, K.E., 2020. Actigraphic 
patterns, impulsivity and mood instability in bipolar disorder, borderline personality 
disorder and healthy controls. Acta Psychiatr. Scand. 141 (4), 374–384. 
Mellers, B., Schwartz, A., Ritov, I., 1999. Emotion-based choice. J. Exp. Psychol.: Gen. 
128 (3), 332. 
Mellers, B.A., Schwartz, A., Ho, K., Ritov, I., 1997. Decision affect theory: Emotional 
reactions to the outcomes of risky options. Psychol. Sci. 8 (6), 423–429. 
Mendl, M., Burman, O.H., Paul, E.S., 2010. An integrative and functional framework for 
the study of animal emotion and mood. Proc. R. Soc. B: Biol. Sci. 277 (1696), 
2895–2904. 
Michely, J., Eldar, E., Martin, I.M., Dolan, R.J., 2020. A mechanistic account of 
serotonin’s impact on mood. Nat. Commun. 11 (1), 1–11. 
Miller, R., Wickens, J.R., 1991. Corticostriatal cell assemblies in selective attention and 
in representation of predictable and controllable events. Concepts Neurosci. 2 (1), 
65–95. 
Miyamoto, Y., Boylan, J.M., Coe, C.L., Curhan, K.B., Levine, C.S., Markus, H.R., Park, J., 
Kitayama, S., Kawakami, N., Karasawa, M., 2013. Negative emotions predict 
elevated interleukin-6 in the United States but not in Japan. Brain Behav. Immun. 
34, 79–85. 
Mobbs, D., Petrovic, P., Marchant, J.L., Hassabis, D., Weiskopf, N., Seymour, B., 
Dolan, R.J., Frith, C.D., 2007. When fear is near: threat imminence elicits prefrontal- 
periaqueductal gray shifts in humans. Science 317 (5841), 1079–1083. 
Mogg, K., Bradley, B.P., 1998. A cognitive-motivational analysis of anxiety. Behav. Res. 
Ther. 36 (9), 809–848. 
Montague, P.R., Berns, G.S., 2002. Neural economics and the biological substrates of 
valuation. Neuron 36 (2), 265–284. 
Montague, P.R., Dayan, P., Sejnowski, T.J., 1996. A framework for mesencephalic 
dopamine systems based on predictive Hebbian learning. J. Neurosci. 16 (5), 
1936–1947. 
Montague, P.R., Dolan, R.J., Friston, K.J., Dayan, P., 2012. Computational psychiatry. 
Trends Cogn. Sci. 16 (1), 72–80. 
Moors, A., 2013. On the causal role of appraisal in emotion. Emot. Rev. 5 (2), 132–140. 
Moors, A., Ellsworth, P.C., Scherer, K.R., Frijda, N.H., 2013. Appraisal theories of 
emotion: State of the art and future development. Emot. Rev. 5 (2), 119–124. 
Moran, R., Dayan, P., Dolan, R.J., 2021. Human subjects exploit a cognitive map for 
credit assignment. Proc. Natl. Acad. Sci. U.S.A. 118, 4. 
Morris, W.N., 2012. Mood: The Frame of Mind. Springer Science & Business Media. 
Myers, K.P., Sclafani, A., 2001. Conditioned enhancement of flavor evaluation reinforced 
by intragastric glucose: II. Taste reactivity analysis. Physiol. Behav. 74 (4–5), 
495–505. 
Nesse, R.M., Ellsworth, P.C., 2009. Evolution, emotions, and emotional disorders. Am. 
Psychol. 64 (2), 129–139. https://doi.org/10.1037/a0013503. 
Nettle, D., Bateson, M., 2012. The evolutionary origins of mood and its disorders. Curr. 
Biol. 22 (17), R712–R721. 
Niedenthal, P.M., Brauer, M., 2012. Social functionality of human emotion. Annu. Rev. 
Psychol. 63, 259–285. 
Niv, Y., 2009. Reinforcement learning in the brain. J. Math. Psychol. 53 (3), 139–154. 
Niv, Y., Joel, D., Dayan, P., 2006. A normative perspective on motivation. Trends Cogn. 
Sci. 10 (8), 375–381. 
Nussbaum, M. (2004). Emotions as Judgments of. Thinking about Feeling: Contemporary 
Philosophers on Emotions, 183. 
O’Doherty, J., Dayan, P., Schultz, J., Deichmann, R., Friston, K., Dolan, R.J., 2004. 
Dissociable roles of ventral and dorsal striatum in instrumental conditioning. Science 
304 (5669), 452–454. 
O’Reilly, R.C., 2020. Unraveling the mysteries of motivation. Trends Cogn. Sci. 24 (6), 
425–434. 
Oatley, K., Duncan, E., 1994. The experience of emotions in everyday life. Cogn. Emot. 8 
(4), 369–381. 
Oatley, K., Keltner, D., Jenkins, J.M., 2006. Understanding Emotions. Blackwell 
Publishing. 
¨Ohman, A., Flykt, A., Esteves, F., 2001. Emotion drives attention: detecting the snake in 
the grass. J. Exp. Psychol.: Gen. 130 (3), 466. 
Ortony, A., Clore, G.L., Collins, A., 1990. The Cognitive Structure of Emotions. 
Cambridge University Press. 
Otto, A.R., Eichstaedt, J.C., 2018. Real-world unexpected outcomes predict city-level 
mood states and risk-taking behavior. PLoS One 13 (11), e0206923. 
Padoa-Schioppa, C., 2011. Neurobiology of economic choice: a good-based model. Annu. 
Rev. Neurosci. 34, 333–359. 
Palminteri, S., Khamassi, M., Joffily, M., Coricelli, G., 2015. Contextual modulation of 
value signals in reward and punishment learning. Nat. Commun. 6 (1), 1–14. 
Parducci, A., 1995. Happiness, Pleasure, and Judgment: The Contextual Theory and its 
Applications. Lawrence Erlbaum Associates, Inc. 
Parkinson, B., 1996. Emotions are social. Br. J. Psychol. 87 (4), 663–683. 
Parkinson, B., 1997. Untangling the appraisal-emotion connection. Personal. Soc. 
Psychol. Rev. 1 (1), 62–79. 
Peters, A., McEwen, B.S., Friston, K., 2017. Uncertainty and stress: Why it causes diseases 
and how it is mastered by the brain. Prog. Neurobiol. 156, 164–188. https://doi.org/ 
10.1016/j.pneurobio.2017.05.004. 
Peters, J., Schaal, S., 2008. Natural actor-critic. Neurocomputing 71 (7–9), 1180–1190. 
Peterson, C., Seligman, M.E., 1983. Learned helplessness and victimization. J. Soc. Issues 
39 (2), 103–116. 
Pitman, R.K., Orr, S.P., Shalev, A.Y., 1993. Once bitten, twice shy: beyond the 
conditioning model of PTSD. Biol. Psychiatry. 
Price, D.D., 2000. Psychological and neural mechanisms of the affective dimension of 
pain. Science 288 (5472), 1769–1772. 
Quigley, B.M., Tedeschi, J.T., 1996. Mediating effects of blame attributions on feelings of 
anger. Personal. Soc. Psychol. Bull. 22 (12), 1280–1288. 
Regier, D.A., Kuhl, E.A., Kupfer, D.J., 2013. The DSM-5: Classification and criteria 
changes. World Psychiatry 12 (2), 92–98. 
Reisenzein, R., 1995. On appraisals as causes of emotions. Psychol. Inq. 6 (3), 233–237. 
Riley, W.T., Treiber, F.A., Woods, M.G., 1989. Anger and hostility in depression. J. Nerv. 
Ment. Dis. 
Roeper, J., 2013. Dissecting the diversity of midbrain dopamine neurons. Trends 
Neurosci. 36 (6), 336–342. 
Roseman, I.J., 1996. Appraisal determinants of emotions: Constructing a more accurate 
and comprehensive theory. Cogn. Emot. 10 (3), 241–278. 
Rosen, J.B., Schulkin, J., 1998. From normal fear to pathological anxiety. Psychol. Rev. 
105 (2), 325. 
Rossi, M.A., Sukharnikova, T., Hayrapetyan, V.Y., Yang, L., Yin, H.H., 2013. Operant self- 
stimulation of dopamine neurons in the substantia nigra. PLoS One 8 (6), e65799. 
Rottenberg, J., 2005. Mood and emotion in major depression. Curr. Dir. Psychol. Sci. 14 
(3), 167–170. 
Ruckmick, C.A. (1936). The psychology of feeling and emotion. 
Rumelhart, D.E., Hinton, G.E., Williams, R.J., 1985. Learning internal representations by 
error propagation. California Univ San Diego La Jolla Inst for Cognitive Science,. 
Russek, E.M., Momennejad, I., Botvinick, M.M., Gershman, S.J., Daw, N.D., 2017. 
Predictive representations can link model-based reinforcement learning to model- 
free mechanisms. PLoS Comput. Biol. 13 (9), e1005768. 
Russell, J.A., 1980. A circumplex model of affect. J. Personal. Soc. Psychol. 39 (6), 
1161–1178. https://doi.org/10.1037/h0077714. 
Russell, J.A., 2003. Core affect and the psychological construction of emotion. Psychol. 
Rev. 110 (1), 145. 
Russell, J.A., Barrett, L.F., 1999. Core affect, prototypical emotional episodes, and other 
things called emotion: dissecting the elephant. J. Personal. Soc. Psychol. 76 (5), 805. 
Rutledge, R.B., Skandali, N., Dayan, P., Dolan, R.J., 2014. A computational and neural 
model of momentary subjective well-being. Proc. Natl. Acad. Sci. U.S.A. 111 (33), 
12252–12257. https://doi.org/10.1073/pnas.1407535111. 
Rutledge, R.B., Skandali, N., Dayan, P., Dolan, R.J., 2015. Dopaminergic modulation of 
decision making and subjective well-being. J. Neurosci. 35 (27), 9811–9822. 
Salovey, P., Rodin, J., 1986. The differentiation of social-comparison jealousy and 
romantic jealousy. J. Personal. Soc. Psychol. 50 (6), 1100. 
Sander, D., Grandjean, D., Scherer, K.R., 2005. A systems approach to appraisal 
mechanisms in emotion. Neural Netw. 18 (4), 317–352. 
Sauter, D.A., Eisner, F., Ekman, P., Scott, S.K., 2010. Cross-cultural recognition of basic 
emotions through nonverbal emotional vocalizations. Proc. Natl. Acad. Sci. U.S.A. 
107 (6), 2408–2412. 
Scherer, K.R., 1984. On the nature and function of emotion: a component process 
approach. Approaches Emot. 2293 (317), 31. 
Scherer, K.R., 2005. What are emotions? And how can they be measured? Soc. Sci. Inf. 44 
(4), 695–729. 
Scherer, K.R., 2009a. Emotions are emergent processes: they require a dynamic 
computational architecture. Philos. Trans. R. Soc. B: Biol. Sci. 364 (1535), 
3459–3474. 
Scherer, K.R., 2009b. The dynamic architecture of emotion: evidence for the component 
process model. Cogn. Emot. 23 (7), 1307–1351. 
Schnurr, P.P., 1989. Endogenous factors associated with mood. Mood. Springer, 
pp. 35–69. 
Schultz, W., Dayan, P., Montague, P.R., 1997. A neural substrate of prediction and 
reward. Science 275 (5306), 1593–1599. 
Sedek, G., Kofta, M., 1990. When cognitive exertion does not yield cognitive gain: toward 
an informational explanation of learned helplessness. J. Personal. Soc. Psychol. 58 
(4), 729. 
Seligman, M.E., 1971. Phobias and preparedness. Behav. Ther. 2 (3), 307–320. 
Seth, A.K., Friston, K.J., 2016. Active interoceptive inference and the emotional brain. 
Philos. Trans. R. Soc. B: Biol. Sci. 371 (1708), 20160007. 
Sharp, P.B., Eldar, E., 2019. Computational models of anxiety: nascent efforts and future 
directions. Curr. Dir. Psychol. Sci. 28 (2), 170–176. 
Sharp, P.B., Dolan, R.J., Eldar, E., 2021. Disrupted state transition learning as a 
computational marker of compulsivity. Psychol. Med. 1–11. 
Sharp, P.B., Fradkin, I., Eldar, E., 2022. Hierarchical inference as a source of human 
biases. Cogn. Affect. Behav. Neurosci. 1–15. 
Shenhav, A., Musslick, S., Lieder, F., Kool, W., Griffiths, T.L., Cohen, J.D., Botvinick, M. 
M., 2017. Toward a rational and mechanistic account of mental effort. Annu. Rev. 
Neurosci. 40, 99–124. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


## Page 17

Neuroscience and Biobehavioral Reviews 144 (2023) 104977
17
Shiota, M.N., Campos, B., Oveis, C., Hertenstein, M.J., Simon-Thomas, E., Keltner, D., 
2017. Beyond happiness: building a science of discrete positive emotions. Am. 
Psychol. 72 (7), 617. 
Shteingart, H., Loewenstein, Y., 2014. Reinforcement learning and human behavior. 
Curr. Opin. Neurobiol. 25, 93–98. 
Slovic, P., Finucane, M.L., Peters, E., MacGregor, D.G., 2007. The affect heuristic. Eur. J. 
Oper. Res. 177 (3), 1333–1352. 
Sobocki, P., J¨onsson, B., Angst, J., Rehnberg, C., 2006. Cost of depression in Europe. 
J. Ment. Health Policy Econ. 
Solomon, R.C., 1988. On emotions as judgments. Am. Philos. Q. 25 (2), 183–191. 
Solomyak, L., Sharp, P.B., & Eldar, E. (2022). Training diversity promotes absolute-value- 
guided choice. 
Spielberger, C.D., Jacobs, G., Russell, S., Crane, R.S., 1983. Assessment of anger: the 
state-trait anger scale. Adv. Person. Assess. 2, 161–189. 
Sutton, R.S., 1990. Integrated architectures for learning, planning, and reacting based on 
approximating dynamic programming. Machine Learning Proceedings 1990. 
Elsevier, pp. 216–224. 
Sutton, R.S., Barto, A.G., 2018. Reinforcement Learning: An Introduction. MIT Press. 
Szanto, K., de Bruin, W.B., Parker, A.M., Hallquist, M.N., Vanyukov, P.M., 
Dombrovski, A.Y., 2015. Decision-making competence and attempted suicide. 
J. Clin. Psychiatry 76 (12), 4053. 
Tangney, J.P.E., ([___])#38; Fischer, K.W. (1995). Self-conscious emotions: The 
psychology of shame, guilt, embarrassment, and pride. The Idea for in this issue Grew 
out of 2 Pivotal Conferences. The 1st Conference, on Emotion and Cognition in 
Development, Was Held in Winter Park, CO, Sum 1985. The 2nd Conference, on Shame 
and Other Self-Conscious Emotions, Was Held in Asilomar, CA, Dec 1988. 
Taylor, G.J., Bagby, R.M., 2004. New trends in alexithymia research. Psychother. 
Psychosom. 73 (2), 68–77. 
Tetlock, P.E., 2002. Social functionalist frameworks for judgment and choice: intuitive 
politicians, theologians, and prosecutors. Psychol. Rev. 109 (3), 451. 
Tobler, P.N., O’Doherty, J.P., Dolan, R.J., Schultz, W., 2007. Reward value coding 
distinct from risk attitude-related uncertainty coding in human reward systems. 
J. Neurophysiol. 97 (2), 1621–1632. 
Trickett, P.K., Kuczynski, L., 1986. Children’s misbehaviors and parental discipline 
strategies in abusive and nonabusive families. Dev. Psychol. 22 (1), 115. 
Truax, P., Selthon, L., 2003. Mood disorders. Diagnostic Interviewing. Springer, 
pp. 111–147. 
Tsanas, A., Saunders, K.E.A., Bilderbeck, A.C., Palmius, N., Osipov, M., Clifford, G.D., 
Goodwin, G., De Vos, M., 2016. Daily longitudinal self-monitoring of mood 
variability in bipolar disorder and borderline personality disorder. J. Affect. Disord. 
205, 225–233. 
Turing, A., 1969. Intelligent machinery. 1948. Essent. Turing 395. 
van Steenbergen, H., Eikemo, M., Leknes, S., 2019. The role of the opioid system in 
decision making and cognitive control: a review. Cogn. Affect. Behav. Neurosci. 19 
(3), 435–458. 
Villano, W.J., Otto, A.R., Ezie, C.E., Gillis, R., Heller, A.S., 2020. Temporal dynamics of 
real-world emotion are more strongly linked to prediction error than outcome. 
J. Exp. Psychol.: Gen. 149 (9), 1755. 
Vinckier, F., Rigoux, L., Oudiette, D., Pessiglione, M., 2018. Neuro-computational 
account of how mood fluctuations arise and affect decision making. Nat. Commun. 9 
(1), 1–12. 
Vytal, K., Hamann, S., 2010. Neuroimaging support for discrete neural correlates of basic 
emotions: a voxel-based meta-analysis. J. Cogn. Neurosci. 22 (12), 2864–2885. 
Waelti, P., Dickinson, A., Schultz, W., 2001. Dopamine responses comply with basic 
assumptions of formal learning theory. Nature 412 (6842), 43–48. 
Webb, L.E., Veenhoven, R., Harfeld, J.L., Jensen, M.B., 2019. What is animal happiness? 
Ann. N. Y. Acad. Sci. 1438 (1), 62–76. 
Westbrook, A., van den Bosch, R., M¨a¨att¨a, J.I., Hofmans, L., Papadopetraki, D., Cools, R., 
Frank, M.J., 2020. Dopamine promotes cognitive effort by biasing the benefits versus 
costs of cognitive work. Science 367 (6484), 1362–1366. 
Wickens, J., & K¨otter, R. (1995). Cellular models of reinforcement. 
Wilkowski, B.M., Robinson, M.D., 2008. The cognitive basis of trait anger and reactive 
aggression: an integrative analysis. Personal. Soc. Psychol. Rev. 12 (1), 3–21. 
Williams, R.J., 1992. Simple statistical gradient-following algorithms for connectionist 
reinforcement learning. Mach. Learn. 8 (3), 229–256. 
Wu, C.C., Bossaerts, P., Knutson, B., 2011. The affective impact of financial skewness on 
neural activity and choice. PLoS One 6 (2), e16838. 
Zettler, A., Duran, G., Waadt, S., Herschbach, P., Strian, F., 1995. Coping with fear of 
long-term complications in diabetes mellitus: a model clinical program. Psychother. 
Psychosom. 64 (3–4), 178–184. 
Zorowitz, S., Momennejad, I., Daw, N.D., 2020. Anxiety, avoidance, and sequential 
evaluation. Comput. Psychiatry 4, 1–17. 
Zorowitz, S., Katzman, P., Daw, N., 2021. Anxiety is associated with reduced value of 
control in sequential decision making. Biol. Psychiatry 89 (9), S311–S312. https:// 
doi.org/10.1016/j.biopsych.2021.02.777. 
A. Emanuel and E. Eldar                                                                                                                                                                                                                      


