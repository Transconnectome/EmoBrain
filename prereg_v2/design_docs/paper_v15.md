---
title: "Learning brain–content relations for high-dimensional affect readout from fMRI"
subtitle: "논문형 통합 초안 v15 — 주장, 분석, 해석 경계를 한 서사로 정리"
date: "2026-09-23"
---

# Abstract

정서를 유발하는 자연 장면은 지각 가능한 시공간적 내용과 행위·상황에 관한 의미적 내용을 함께 포함한다. 그러나 뇌 반응에서 정서 profile을 예측할 수 있다는 사실만으로는 model이 이 content와 무관한 통계적 규칙을 이용했는지, brain–content relation을 학습했는지, 또는 학습한 관계를 실제 output에 사용했는지 구분할 수 없다. 본 연구는 이 문제를 neural organization, learned relation, functional readout의 연속된 세 단계로 검정한다. 첫째, 정서 label로 최적화하지 않은 low-level visual, spatiotemporal visual, caption-semantic representation이 held-out natural-video fMRI response를 얼마나 예측하는지 cross-validated multi-kernel encoding으로 측정한다. 둘째, training-only teacher가 participant-specific brain tokens, frozen video representation, frozen caption representation을 결합하도록 학습한 뒤, correct와 mismatched triplet을 비교하여 brain–visual–semantic correspondence가 fusion 과정에서 형성되는지를 검정한다. Stimulus-wise out-of-fold teacher output으로만 안내받은 brain-only student가 teacher-joint, visual, semantic content를 Direct 및 Shuffled-guided control보다 더 회복하는지는 low-capacity held-out probe와 retrieval로 측정하고, linear CKA는 전체 geometry의 보조 요약으로 사용한다. Teacher activation patching과 student anatomical-network perturbation은 decodable information이 frozen model의 affect output에 기능적으로 사용되는지를 검정한다. 셋째, 34-D normative category-proportion profile의 brain-only prediction을 기능적 endpoint로 평가한다. 14-D affective-appraisal, VA-2, VAD-3 target은 parameter를 공유하지 않는 독립 model로 분석하여 결과가 하나의 annotation ontology 또는 저차원 core에만 의존하는지 판정한다. 두 participant cohort에 동일한 frozen decision rule을 적용하여 participant-level replication을 평가한다. 이 설계는 감정을 감각과 의미의 합으로 정의하거나 fMRI 참가자의 주관적 감정을 복원한다고 주장하지 않는다. 대신 공유된 stimulus-locked brain response가 장면 content와 갖는 관계를 model이 학습하고, brain-only representation에 보존하며, normative affect readout에 사용하는지를 단계적으로 검정한다. [Analysis 1 결과.] [Analysis 2 결과.] [Analysis 3 및 replication 결과.]

# Introduction

같은 감정 label로 기술되는 장면도 서로 다른 색, 형태, 움직임, 대상, 행위와 사회적 상황을 포함할 수 있다. 생일 케이크를 받는 장면과 오랜 친구를 다시 만나는 장면이 모두 “기쁨”으로 평가되더라도 그 장면에서 뇌로 들어오는 정보와 처리 경로가 동일하다고 가정할 수 없다. 두 장면에서 공통으로 나타나는 pattern도 category-specific code일 수 있지만, 장면의 공통 content, 자극 선택, 언어적 범주화 또는 공유된 생리적 반응을 반영할 수 있다. 따라서 이 연구의 중심 질문은 특정 감정에 단일한 brain pattern이 존재하는가가 아니라, 정서를 유발하는 상황들에 대한 공유된 brain response가 장면의 시공간적·상황의미적 content와 어떤 관계를 이루며 그 관계가 어떤 정서적 readout을 허용하는가이다.

다양한 영상에 대한 정서 평정은 one-hot label이 아니라 여러 category와 dimension이 동시에 변하는 고차원 profile을 이룬다(Cowen & Keltner, 2017; Horikawa et al., 2020). 본 연구의 34-D target도 하나의 영상을 하나의 감정으로 분류하는 label이 아니라 각 category가 선택된 비율의 벡터다. 따라서 34-D를 사용한다는 사실 자체가 discrete-category ontology의 진실을 가정하지 않는다. 다만 category-proportion profile은 valence–arousal만으로는 사라질 수 있는 세밀한 자극 간 관계를 보존하므로 primary functional readout으로 적합하다. 동시에 34-D만 분석하면 결과가 category-anchored annotation에 특이적인지 알 수 없으므로, 14-D appraisal space와 그 안의 VA-2 및 VAD-3를 독립적으로 학습한다. Target 사이에는 trainable parameter, loss, standardizer 또는 out-of-fold cache를 공유하지 않는다.

이 annotation들은 fMRI 참가자의 자기보고가 아니라 외부 평정자 집단에서 얻은 normative reference다. 그러므로 성공적인 예측은 참가자가 실제로 느낀 감정이나 개인 기억을 복원했다는 증거가 아니다. 현재 자료가 직접 허용하는 결론은 반복 가능한 stimulus-locked brain response와 집단 수준의 affective annotation 사이의 대응이다. Subjectivity는 중요하지만 현재 연구에서 직접 관찰되지 않는 성분이며, 이후 participant-specific report를 확보한 연구의 대상으로 남는다.

Kragel et al.(2019)은 emotion schema가 visual system에 embedded될 수 있음을 보여주어 이 연구의 핵심 출발점을 제공한다. Gao et al.(2025)은 넓은 daily-life scene에서 object representation이 emotion rating을 강하게 설명할 수 있음을 보고했다. 반면 Horikawa et al.(2020)은 category feature가 object-recognition 및 semantic-concept feature를 넘어서는 brain-response variance를 보고했다. 이 결과들은 서로 배타적이지 않다. 기존 object feature가 짧은 영상의 움직임, 상태 변화, 행위와 situation semantics를 충분히 담지 못했다면, “object model로 설명되지 않는 정서 신호”와 “content로 설명되지 않는 정서 고유 신호”는 동일하지 않다.

본 연구는 visual과 semantic을 순수하고 상호배타적인 심리 구성개념으로 취급하지 않는다. V-JEPA 2 representation은 appearance, object, motion과 event dynamics를 함께 포함할 수 있고, caption representation도 object와 action을 포함한다. 두 representation이 겹치는 것은 오류가 아니라 자연 장면의 실제 구조다. 핵심은 각 source의 고유한 causal essence를 찾는 것이 아니라, 서로 부분적으로 겹치는 두 content view가 held-out brain response 및 model computation에 제공하는 조건부 정보를 검정하는 것이다. 이를 위해 Analysis 1에서는 nested kernel contribution을, teacher에서는 matched B/BV/BS/BVS capacity control을, mechanistic analysis에서는 correct–mismatch contrast를 사용한다.

Elementary visual feature는 primary explanatory representation이 아니라 confound control로 사용한다. Luminance와 color, spatial-frequency 또는 orientation-energy, motion-energy는 brain–content relation이 단순한 image statistics로 설명되는지를 묻는다. Monocular depth estimate는 현재 pretrained model의 semantic prior와 분리하기 어려우므로 primary low-level control에 포함하지 않고, 필요할 때만 exploratory robustness로 사용한다. Static AlexNet fc7은 Kragel 및 Gao 계열과의 역사적 연결을 위한 supplementary anchor이며 primary teacher branch가 아니다. 이 선택은 object와 event를 임의로 이분화하거나 backbone 차이를 심리 구성개념 차이로 오해하지 않기 위한 것이다.

Encoding은 content representation이 held-out brain response를 예측하는지 검정하지만, brain-only learner가 어떤 관계를 학습했는지 또는 그 관계가 affect output에 사용되는지는 알려주지 않는다(Naselaris et al., 2011). 반대로 decoding 성능만 보고하면 model이 무엇을 사용했는지 알기 어렵다. 따라서 본 연구는 organization, inheritance, functional use를 분리한다. Training-only multimodal teacher는 brain, video, caption을 결합하고, brain-only student는 시험 시 brain만 사용한다. Student는 teacher latent를 직접 복제하지 않고 stimulus-wise out-of-fold soft output으로만 안내받는다. 그러므로 사후에 발견되는 visual, semantic 또는 joint information은 직접 target으로 강제된 결과가 아니라 검정 대상이다(Lopez-Paz et al., 2016).

Model interpretation은 정보의 존재와 사용을 구분한다. Low-capacity probe와 retrieval은 student stage에서 content가 읽히는지를 묻고, linear CKA는 전체 stimulus geometry의 유사성을 보조적으로 요약한다(Kornblith et al., 2019). Correct와 mismatched teacher triplet은 correspondence가 fusion stage에 미치는 영향을 보이며, clean activation patching은 손상된 computation의 일부를 복원했을 때 content와 affect output이 함께 회복되는지를 묻는다. Frozen student의 사전 정의 anatomical-network perturbation은 특정 brain-token group을 교란했을 때 같은 readout이 저하되는지를 평가한다. 이 개입은 trained model의 계산적 의존성을 보이지만 인간 뇌의 인과기제를 확립하지 않는다.

이 연구의 thesis는 다음과 같다. 정서를 유발하는 자연 장면에 대한 공유된 stimulus-locked brain response는 장면의 spatiotemporal visual 및 situation-semantic content와 체계적인 관계 구조를 보이며, brain-grounded model은 이 관계를 학습하고 brain-only representation에 보존하며 high-dimensional normative affect readout에 기능적으로 사용할 수 있다. Model의 목적은 최고 decoding 성능을 만드는 것이 아니라 이 명제를 반증 가능한 분석 사슬로 만드는 것이다.

# Hypotheses and decision logic

첫째, spatiotemporal visual representation은 low-level control보다 held-out brain response를 더 잘 예측하고, caption semantics는 visual representation 위에 조건부 예측력을 추가할 것이다. 둘째, primary 34-D teacher의 aligned BVS condition은 B, BV, BS 및 shuffled-alignment control보다 유용한 held-out representation을 형성하고, correct triplet은 modality mismatch보다 안정적인 fused brain-token state와 cross-modal retrieval을 보일 것이다. Full-guided brain-only student는 Direct 및 Shuffled-guided student보다 teacher-joint, visual, semantic information을 더 잘 회복할 것이다. 셋째, clean activation patching과 anatomical-network perturbation은 content retrieval과 affect output을 함께 변화시키고, Full-guided student는 34-D normative profile에서 Direct와 Shuffled-guided control을 넘어설 것이다.

Mechanistic conclusion은 두 gate를 모두 통과할 때만 허용한다. Clean brain-only affect readout이 training-fold mean-profile 및 mandatory linear baseline을 넘어야 하고, 관련 content retrieval이 stimulus-permutation null을 넘어야 한다. Prediction만 향상되면 privileged supervision 또는 regularization 효과로 제한한다. Retrieval만 향상되고 intervention이 수렴하지 않으면 decodable content가 존재하지만 output에 사용된다는 주장은 철회한다. Teacher mismatch, student inheritance, intervention, affect readout과 replication이 모두 같은 방향일 때만 brain–content relation의 학습과 기능적 사용을 주장한다.

# Methods

## Study status and evidence boundary

본 문서는 분석 전 또는 결과 입력 전 원고다. 결과 절의 대괄호는 실제 산출물로 대체해야 하며, 방향과 유의성을 미리 가정하지 않는다. 프로젝트 기록은 primary cohort 6명과 replication cohort 5명을 명시하지만, 최종 표본 수, 2,180/2,181 stimulus 차이, 반복 test 구조, 34-D raw count와 14-D codebook은 공식 dataset manifest를 대조하기 전까지 검증 대기 상태다. 최종 Methods의 수치와 용어는 Phase 0 data audit를 통과한 값으로만 교체한다.

## Data and split unit

Primary 및 replication cohort는 동일하거나 크게 중첩된 silent natural-video stimulus를 본 서로 다른 participant 집단으로 취급한다. Split의 통계적 단위는 stimulus다. 한 stimulus는 모든 participant에서 동일 outer fold에 배정하여 participant 간 leakage를 막는다. 반복 presentation은 stimulus-level response estimate 또는 reliability 계산에 사용하며 독립 sample로 세지 않는다. Replication은 새로운 stimulus distribution에 대한 generalization이 아니라 frozen decision rule의 participant-level 재현으로 해석한다.

## Normative targets

34-D category-proportion vector는 raw [0,1] scale의 graded profile로 유지하고 one-hot 또는 dominant label로 변환하지 않는다. Primary metric은 held-out stimulus 안에서 predicted profile과 observed profile의 Pearson correlation을 Fisher z로 변환한 값이다. Mean-profile baseline, Brier score, RMSE, calibration, dimension-wise across-stimulus macro correlation과 base-rate-residualized profile correlation을 함께 보고한다. 14-D continuous appraisal는 training fold 안에서 dimension별 표준화하며 dimension-wise across-stimulus correlation의 macro-Fisher-z를 primary metric으로 둔다. VA-2와 VAD-3는 codebook에서 사전 지정된 열로 구성하고 개별 dimension 결과, RMSE 및 concordance correlation coefficient를 보고한다.

## Brain response and participant-specific mapping

기존 response estimate를 reproducibility baseline으로 유지하고, raw timing 정보로 GLMsingle beta를 추정할 수 있을 때 반복 test reliability를 label-blind하게 비교한다(Prince et al., 2022). Participant-native voxel pattern은 Schaefer cortical 및 Tian subcortical ROI로 묶는다(Schaefer et al., 2018; Tian et al., 2020). ROI별 standardization과 PCA는 outer-training fold에서만 fit한다. Participant-specific linear adapter는 서로 다른 participant의 native measurement basis를 공통 token width로 변환하되 ROI identity를 보존한다. 이 adapter는 개인 정서 성분을 모델링한다고 해석하지 않으며, 이후 개인별 report가 확보될 경우 별도의 subject-specific component를 brain token에 추가하는 확장과 구분한다.

## Frozen content representations

Low-level control은 luminance/color summary, spatial-frequency 또는 orientation-energy, motion-energy를 포함한다. Primary visual coordinate는 affect target으로 fine-tuning하지 않은 frozen V-JEPA 2의 사전 지정 checkpoint, layer와 temporal pooling에서 추출한다(Assran et al., 2025). Caption coordinate는 stimulus별 human caption을 frozen sentence encoder로 변환한 뒤 사전 지정 aggregation rule로 결합한다. 정확한 checkpoint와 layer는 결과를 보기 전에 재현성, 입력 적합성, 계산 가능성에 근거해 동결한다. V-JEPA 2와 caption의 overlapping content는 제거하지 않고 nested contribution, matched teacher ladder, mismatch control로 다룬다.

## Analysis 1: cross-validated neural encoding

Low-level, spatiotemporal visual, spatiotemporal visual plus caption의 세 nested feature set을 centered normalized kernel로 구성한다. Kernel regularization과 feature reduction은 inner training folds에서만 선택한다. Participant별 ROI-PCA response pattern의 held-out prediction correlation을 primary outcome으로 사용하고 explained variance와 reliability-normalized score를 secondary로 보고한다. Confirmatory contrasts는 visual minus low-level, full minus visual, full minus low-level이다. 이 분석은 tested feature space와 brain response의 out-of-sample correspondence를 보이지만, brain이 해당 network와 같은 알고리즘을 구현하거나 affect output에 그 정보가 쓰인다는 것을 보이지 않는다.

## Training-only multimodal teacher

Teacher는 participant-specific brain tokens, frozen video feature, frozen caption feature를 modality-specific projector로 공통 width에 맞춘 뒤 compact fusion module에서 fused brain-token state와 joint latent를 만든다. Primary 34-D analysis는 B, BV, BS, BVS, B plus shuffled visual/semantic alignment의 matched ladder를 사용한다. Missing modality는 mask token으로 처리하고 brain encoder, fusion depth, head capacity를 가능한 한 맞춘다. 34-D teacher는 sigmoid output과 unweighted soft binary cross-entropy를 사용한다. Raw selection count k와 rater count n을 확인할 수 있을 때만 binomial negative log-likelihood를 robustness로 추가한다. Continuous target teacher는 training-fold standardized target에 dimension-normalized MSE를 사용한다.

각 held-out stimulus의 guidance는 그 stimulus를 모든 participant에서 제외한 fold-specific teacher가 생성한다. 이 stimulus-wise out-of-fold procedure는 teacher가 본 stimulus label을 student에게 되돌려주는 leakage를 막는다. Student는 teacher probability 또는 continuous prediction만 받으며 teacher latent, CKA, visual embedding, caption embedding 또는 pairwise geometry를 직접 맞추지 않는다.

## Brain-only student and learning conditions

Student는 ROI-PCA brain tokens, participant-specific adapter, small shared encoder와 target-specific joint head로 구성한다. 동일 input의 multi-output ridge 또는 reduced-rank regression을 mandatory baseline으로 사용한다. Small nonlinear encoder가 nested validation에서 baseline을 안정적으로 넘지 못하면 단순 model을 primary로 승격한다. Direct는 normative label loss만, Full-guided는 aligned BVS teacher의 out-of-fold output loss를 추가하며, Shuffled-guided는 teacher vector 내부 구조와 loss 규모를 보존한 채 stimulus pairing만 training fold 안에서 순열화한다.

34-D student objective는 `SoftBCE(y,pS) + λ MSE(pT_OOF,pS)`다. 첫 항은 observed category proportion에 대한 supervised loss이고 두 번째 항은 probability scale의 Brier-type guidance다. 14-D, VA-2, VAD-3 objective는 `MSE(yz,yS) + λ MSE(yT_OOF,yS)`다. λ와 early stopping은 inner validation으로만 선택한다. 모든 test condition은 brain-only다.

## Analysis 2A: teacher relation formation

Frozen primary BVS teacher에 correct `(Bi,Vi,Si)`, video-swap `(Bi,Vj,Si)`, caption-swap `(Bi,Vi,Sj)`, both-swap `(Bi,Vj,Sj)` triplet을 입력한다. j는 held-out set 안의 derangement로 정하고 여러 사전 생성 permutation에 걸쳐 평균한다. Both-swap은 video–caption coherence를 보존하면서 brain–content alignment를 끊는다. Single-swap은 한 source의 correspondence와 video–caption coherence를 동시에 바꾸므로 unique modality mechanism으로 해석하지 않는다. Projected token, fused brain token, joint latent와 output에서 correct–mismatch distance, correct-stimulus retrieval 및 affect-output shift를 기록한다.

## Analysis 2B: student inheritance and representation geometry

Frozen student의 adapter, encoder block, final latent를 완전히 held-out stimulus에서 추출한다. Linear 또는 reduced-rank probe는 teacher joint latent, training-fold PCA로 축약한 video feature와 caption embedding을 예측한다. Correct-stimulus retrieval의 top-k accuracy, median rank, mean reciprocal rank와 neighborhood overlap을 계산한다. Probe hyperparameter는 training fold에서만 선택하고 shuffled-label 및 matched-capacity null을 포함한다. 동일 held-out order에서 student stage와 teacher-joint, visual, semantic, affect reference 사이의 centered linear CKA를 secondary heatmap으로 보고한다. Probe와 CKA는 training loss 또는 model selection에 사용하지 않는다.

## Analysis 2C: functional use

Teacher activation patching은 modality-mismatched run에서 선택된 fused brain-token 또는 joint activation을 같은 stimulus의 clean activation으로 교체한다. Video, caption, teacher-joint retrieval과 affect output에 대해 `recovery=(patched−mismatch)/(clean−mismatch)`를 계산하고, 분모가 사전 tolerance보다 작을 때 normalized value를 결측 처리한 뒤 raw difference를 보고한다. Wrong-stimulus, random-stage와 same-size patch를 matched null로 사용한다.

Student perturbation은 결과를 보기 전에 정한 anatomical network의 ROI tokens를 participant 안의 다른 held-out stimulus와 공동 순열하여 marginal distribution을 유지하면서 stimulus-specific information을 끊는다. Teacher-joint, video, caption retrieval과 affect readout의 drop을 측정한다. Training-fold mean replacement와 leave-one-network-out refit은 robustness다. ROI identity가 preprocessing에서 보존되지 않으면 이 분석은 실행하지 않는다.

## Analysis 3: independent affect readouts

34-D, 14-D, VA-2, VAD-3는 동일 stimulus split과 architecture-selection rule만 공유하고 별도 random initialization, teacher, student, head, standardizer와 OOF cache를 사용한다. 각 target 안에서 Full minus Direct와 Full minus Shuffled를 primary contrasts로 평가한다. Target 사이의 raw metric을 직접 순위화하지 않는다. 모든 target에서 aligned guidance가 지지되면 core affect에서 fine-grained profile까지 일반화되는 것으로, VA/VAD에서만 지지되면 broad polarity·activation·control로, 34-D에서만 지지되면 category-profile-specific effect로 해석을 제한한다.

## Statistical inference and replication

Participant-level effect를 primary inferential unit으로 유지하고 seed는 독립 sample로 세지 않는다. Participant-clustered bootstrap으로 confidence interval을 계산하며 stimulus-label permutation은 전체 pairing structure를 보존한다. Teacher conditional-source, mismatch by stage, patch by readout, student condition, network by readout을 별도 family로 정의해 multiple-comparison correction을 적용한다. Primary cohort에서 feature checkpoint, response pipeline, architecture, λ grid, metrics, mismatch와 perturbation rule을 동결한 뒤 replication cohort에 적용한다. Replication에서는 사전 규칙에 따른 participant adapter만 새로 적합한다.

# Planned Results

## Analysis 1: neural organization

Full content model의 held-out brain-response prediction은 low-level control보다 [effect, CI, corrected p], visual-only model보다 [effect, CI, corrected p]였다. Visual minus low-level contrast는 [result], full minus visual contrast는 [result]였으며 participant-level direction은 [result]였다. Reliability-normalized analysis와 supplementary AlexNet anchor는 [result]였다. 이 결과는 [tested content coordinates가 shared response와 관계함 / primary hypothesis를 지지하지 않음]으로 해석했다.

## Analysis 2: relation formation, inheritance, and use

Primary 34-D teacher ladder에서 BV minus B, BS minus B, BVS minus BV, BVS minus BS와 BVS minus shuffled의 held-out effects는 [results]였다. Correct–mismatch contrast는 [stage]에서 [representation/retrieval/output effect]를 보였다. Full-guided student의 teacher-joint, video와 caption retrieval은 Direct보다 [result], Shuffled-guided보다 [result]였고, secondary CKA는 [convergent/divergent] pattern을 보였다. Clean activation patching은 [readouts]을 [recovered/not recovered]했으며 anatomical-network perturbation은 [readouts]에 [drop/no reliable drop]을 만들었다. Prediction 및 retrieval gate는 [passed/failed]했다.

## Analysis 3: affect readout and replication

34-D profile correlation은 mean-profile baseline [value], linear baseline [value], Direct [value], Full-guided [value], Shuffled-guided [value]였다. Full minus Direct 및 Full minus Shuffled effects는 [results]였다. Independent 14-D, VA-2와 VAD-3 analyses는 [pattern]을 보였다. Frozen analysis rule을 적용한 replication cohort에서 primary effect direction은 [replicated/not replicated/heterogeneous]였다.

# Discussion

본 연구는 자연 장면의 정서적 brain readout을 단일 category pattern의 탐색이 아니라 brain–content relation의 학습과 기능적 사용 문제로 재구성한다. 세 분석이 모두 지지된다면, shared stimulus-locked brain response가 spatiotemporal visual 및 situation-semantic content와 체계적 관계를 이루고, aligned multimodal teacher가 이 관계를 brain-only student에 전달하며, 그 결과가 high-dimensional normative affect profile의 기능적 readout에 사용된다는 수렴 증거를 제공한다. 이 결론은 Kragel et al.(2019)의 visual emotion schema 논의를 natural video의 dynamics, caption semantics와 brain-grounded student representation으로 확장한다.

결과가 부분적으로만 지지될 가능성도 핵심 해석의 일부다. Analysis 1만 성공하면 tested content space가 brain response를 예측한다는 결론에 그친다. Full-guided prediction이 향상되지만 Shuffled-guided와 다르지 않으면 generic soft-target regularization으로 제한한다. Retrieval은 향상되지만 intervention effect가 없으면 information은 decodable하지만 affect output에 사용된다는 증거는 부족하다. 34-D가 baseline을 넘지 못하면 mechanistic analysis는 model diagnostic으로 남고 neuroscience conclusion은 철회한다. Primary cohort에서만 나타나면 participant-level generality를 주장하지 않는다.

본 연구는 감정을 sensory plus semantic의 합으로 정의하지 않는다. V-JEPA 2와 caption representation은 부분적으로 겹치며, 선택한 pretrained model은 인간의 internal representation과 동일하지 않다. Normative target은 참가자 자기보고가 아니고, 현재 design은 기억, interoception, appraisal history와 개인적 의미를 직접 측정하지 않는다. Activation patching과 network perturbation도 trained model 내부의 computation을 시험할 뿐 뇌 회로의 인과성을 보이지 않는다.

그럼에도 이 접근은 향후 emotion foundation model과 연결될 수 있다. 본 연구가 제공하는 것은 foundation model 자체가 아니라 brain-grounded multimodal representation을 평가하는 원칙이다. 즉, 모델은 높은 평균 성능뿐 아니라 어떤 brain–content relation을 형성하고, brain-only 상태에서 무엇을 보존하며, intervention에 의해 어떤 output이 변하는지를 보여야 한다. 이후 participant-specific self-report와 longitudinal context가 추가되면 shared stimulus-locked component와 individual-specific affective component를 분리하는 방향으로 확장할 수 있다.

# Figures and Tables

Figure 1은 neural organization, teacher relation formation, student inheritance, functional use와 affect readout의 전체 study logic을 제시한다. Figure 2는 paired brain–video–caption training, stimulus-wise out-of-fold guidance, brain-only inference와 post-training mechanistic analyses를 제시한다. Figure 3은 Analysis 1 nested encoding과 participant-level effects, Figure 4는 teacher mismatch, student retrieval, CKA, patching 및 network perturbation, Figure 5는 34-D primary와 independent 14-D, VA-2, VAD-3 및 replication 결과를 제시한다.

Table 1은 dataset provenance, cohort, stimulus, annotation과 response-estimation audit를, Table 2는 각 model component의 과학적 역할과 선택 이유를, Table 3은 confirmatory contrast, metric, statistical unit과 falsifying result를, Table 4는 제거 또는 supplementary로 격하한 분석과 그 이유를 기록한다.

# References

Assran, M., Bardes, A., Fan, D., Garrido, Q., Howes, R., Komeili, M., et al. (2025). V-JEPA 2: Self-supervised video models enable understanding, prediction and planning. arXiv:2506.09985.

Cowen, A. S., & Keltner, D. (2017). Self-report captures 27 distinct categories of emotion bridged by continuous gradients. Proceedings of the National Academy of Sciences, 114, E7900–E7909.

Elazar, Y., Ravfogel, S., Jacovi, A., & Goldberg, Y. (2021). Amnesic probing: Behavioral explanation with amnesic counterfactuals. Transactions of the Association for Computational Linguistics, 9, 160–175.

Gao, C., Ajith, S., & Peelen, M. V. (2025). Object representations drive emotion schemas across a large and diverse set of daily-life scenes. Communications Biology, 8, 697.

Hewitt, J., & Liang, P. (2019). Designing and interpreting probes with control tasks. Proceedings of EMNLP-IJCNLP, 2733–2743.

Horikawa, T. (2025). Mind captioning: Evolving descriptive text of mental content from human brain activity. Science Advances, 11, eadw1464.

Horikawa, T., Cowen, A. S., Keltner, D., & Kamitani, Y. (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. iScience, 23, 101060.

Khosla, M., Ngo, G. H., Jamison, K., Kuceyeski, A., & Sabuncu, M. R. (2021). Cortical response to naturalistic stimuli is largely predictable with deep neural networks. Science Advances, 7, eabe7547.

Kornblith, S., Norouzi, M., Lee, H., & Hinton, G. (2019). Similarity of neural network representations revisited. Proceedings of ICML, 3519–3529.

Kragel, P. A., Reddan, M. C., LaBar, K. S., & Wager, T. D. (2019). Emotion schemas are embedded in the human visual system. Science Advances, 5, eaaw4358.

Lopez-Paz, D., Bottou, L., Schölkopf, B., & Vapnik, V. (2016). Unifying distillation and privileged information. International Conference on Learning Representations.

Meng, K., Bau, D., Andonian, A., & Belinkov, Y. (2022). Locating and editing factual associations in GPT. Advances in Neural Information Processing Systems, 35.

Naselaris, T., Kay, K. N., Nishimoto, S., & Gallant, J. L. (2011). Encoding and decoding in fMRI. NeuroImage, 56, 400–410.

Nunez-Elizalde, A. O., Huth, A. G., & Gallant, J. L. (2019). Voxelwise encoding models with non-spherical multivariate normal priors. NeuroImage, 197, 482–492.

Prince, J. S., Charest, I., Kurzawski, J. W., Pyles, J. A., Tarr, M. J., & Kay, K. N. (2022). Improving the accuracy of single-trial fMRI response estimates using GLMsingle. eLife, 11, e77599.

Russell, J. A. (1980). A circumplex model of affect. Journal of Personality and Social Psychology, 39, 1161–1178.

Russell, J. A., & Mehrabian, A. (1977). Evidence for a three-factor theory of emotions. Journal of Research in Personality, 11, 273–294.

Schaefer, A., Kong, R., Gordon, E. M., Laumann, T. O., Zuo, X.-N., Holmes, A. J., et al. (2018). Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. Cerebral Cortex, 28, 3095–3114.

Tian, Y., Margulies, D. S., Breakspear, M., & Zalesky, A. (2020). Topographic organization of the human subcortex unveiled with functional connectivity gradients. Nature Neuroscience, 23, 1421–1432.

Vig, J., Gehrmann, S., Belinkov, Y., Qian, S., Nevo, D., Singer, Y., & Shieber, S. (2020). Investigating gender bias in language models using causal mediation analysis. Advances in Neural Information Processing Systems, 33.
