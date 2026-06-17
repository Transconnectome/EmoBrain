# 전체 연구 파이프라인
## 뇌의 감정 표상은 개인화된 구조와 공유된 구조를 동시에 가지는가? 공유된 구조는 몇 차원이며, 뇌의 감정 표상 geometry를 AI 모델에 transfer했을 때 감정 예측이 향상되는가?

---

## 데이터

- 감정 유발 비디오 2,181개 (Horikawa et al., 2020)
- Whole-brain fMRI, 5명 피험자, 전처리 완료
- 감정 레이블: 비디오당 34개 감정 카테고리 + 14개 affective dimension 점수 (Cowen & Keltner, 2017)

---

## 모델

- 비디오 인코더: V-JEPA2 (TRIBE v2 backbone 활용), CLIP (베이스라인)
- 뇌 인코더: Brain-JEPA
- 뇌-비디오 정렬: TRIBE v2 Transformer (frozen) + subject block (피험자별 학습)

---

## Figure 1: 개인화된 구조 확인

**질문:** 감정의 신경 표상은 통증처럼 (Lee et al., 2026) 완전히 개인화되어 있는가?

**방법:**

각 피험자별로 subject block을 하나씩 학습한다. Brain-JEPA로 추출한 fMRI 임베딩을 target으로 사용하며, TRIBE v2 Transformer는 frozen 상태로 유지하고 subject block만 각 피험자의 fMRI 반응 패턴을 학습하도록 훈련한다.

**분석:**

피험자 내 예측 정확도는 비디오에 대한 leave-one-out cross-validation으로 평가한다. 피험자 간 예측은 5명의 모든 쌍에 대해 수행한다. 피험자 A의 subject block으로 피험자 B의 fMRI 반응을 예측하는 방식이다. 5개의 subject block 표상 간 쌍별 RSA를 계산하여 피험자 간 유사도를 정량화한다.

**기대 결과:**

피험자 간 예측이 피험자 내 예측보다 유의미하게 낮아 개인화된 구조가 존재함을 확인한다. 그러나 통증(Lee et al., 2026)과 달리 예측이 완전히 실패하지는 않으며, 이는 개인화된 구조와 함께 공유된 구조가 존재할 가능성을 시사한다.

---

## Figure 2: 공유된 구조 발견

**질문:** 개인화된 구조 안에 공유된 subspace가 존재하며, 그것이 감정 카테고리 구조를 포착하는가?

**방법:**

5개의 학습된 subject block에 PCA 또는 CCA를 적용하여 공유 subspace를 추출한다. 공유 subspace를 제거한 나머지 분산이 각 피험자의 개인 residual이 된다.

공유 subspace 내에서 2,181개 비디오에 대한 RSM을 계산한다. 동일한 방식으로 개인 residual 내에서도 RSM을 계산한다. 두 RSM을 감정 카테고리 점수와 affective dimension 점수(valence, arousal)로 각각 정렬하여 비교한다.

공유 subspace RSM과 비디오 임베딩 RSM(V-JEPA2) 간의 CKA를 계산하고, 개인 residual RSM과 비디오 임베딩 RSM 간의 CKA도 별도로 계산한다. 공유 subspace와 개인 residual 각각에 UMAP을 적용하고, 감정 카테고리별로 색상을 입혀 시각화한다.

**분석:**

공유 subspace RSM과 감정 카테고리 레이블 간의 RSA, 그리고 affective dimension 레이블 간의 RSA를 비교한다. 개인 residual RSM에 대해서도 동일하게 수행한다. 공유 subspace와 비디오 임베딩 간의 CKA, 개인 residual과 비디오 임베딩 간의 CKA를 비교한다.

**기대 결과:**

공유 subspace에서 감정 카테고리별 구조가 명확하게 나타나며, 이는 Horikawa et al.의 결과를 피험자 간 공유 표상 공간에서 재현하는 것이다. 개인 residual은 덜 구조화되어 있고 피험자마다 다른 패턴을 보인다. 비디오 임베딩은 개인 residual보다 공유 subspace와 더 잘 align된다. 공유 subspace에서 affective dimension보다 감정 카테고리가 더 많은 분산을 설명한다.

---

## Figure 3: 공유 구조의 차원성

**질문:** 공유된 구조는 몇 차원이며, ~27차원으로 수렴하는가?

**실험 1: 내재적 차원수 측정**

공유 subspace의 내재적 차원수를 설명된 분산 곡선의 elbow 탐지, participation ratio, 최근접 이웃 기반 내재적 차원수 추정기(예: TwoNN)를 통해 측정한다. 이를 통해 공유된 신경 감정 geometry에서 자연스럽게 몇 개의 차원이 출현하는지에 대한 데이터 기반 답을 얻는다.

**실험 2: 차원 수 탐색 (Dimension sweep)**

공유 subspace를 k차원으로 projection하여 k = 5, 10, 15, 20, 27, 34, 50, 100에서 세 가지 지표를 평가한다. 첫째, downstream 감정 태스크 성능(valence/arousal regression, 감정 카테고리 분류). 둘째, 전체 뇌 RSM과의 CKA. 셋째, Cowen의 27개 감정 레이블 구조(행동 기반 RSM, Cowen & Keltner, 2017)와의 RSA 대응도. 어느 k에서 대응도가 최대화되는지 확인한다.

**실험 3: 레벨 간 Mantel test**

k를 27로 고정하고 세 레벨에서 RSM을 계산한다. 행동 공간(Cowen의 2,181개 비디오 감정 평점), 신경 공간(Horikawa fMRI 공유 subspace RSM), 모델 공간(V-JEPA2 비디오 임베딩 RSM). 모든 RSM 쌍 간 Mantel test를 수행하여 세 레벨이 k=27에서 동일한 기하학적 구조를 공유하는지 검증한다.

**기대 결과 시나리오:**

| 시나리오 | 결과 | 해석 |
|---------|------|------|
| A (강한 결과) | k=27에서 모든 지표 최적 | 27차원은 감정의 보편적 구조 |
| B (현실적) | k=20~30에서 plateau | ~27차원 구조, Cowen & Keltner와 일치 |
| C (유의미한 반례) | 최적 k가 27과 다름 | 행동과 신경의 차원성이 다름, 추가 질문 제기 |

---

## Figure 4: AI 모델로의 transfer (Brain Tuning)

**질문:** 공유된 신경 geometry를 AI 모델에 transfer했을 때 감정 예측이 향상되는가? 그리고 공유된 구조와 개인화된 구조는 기능적으로 분리 가능한가?

**Step 1: Shared Brain Tuning**

공유 subspace RSM을 target 구조로 사용하여 V-JEPA2를 fine-tuning한다. 두 가지 loss를 함께 적용한다. RSM loss는 비디오 임베딩 RSM과 뇌의 공유 subspace RSM 사이의 Frobenius 거리를 최소화한다. Contrastive loss는 같은 감정 카테고리의 비디오를 가깝게, 다른 감정 카테고리의 비디오를 멀게 학습시키며, 공유 subspace 구조에서 도출된 카테고리 레이블을 사용한다.

**Step 2: Personalized Brain Tuning**

Shared Brain-Tuned 모델 위에 피험자별 경량 adapter를 추가한다. 각 adapter는 Figure 1에서 학습된 개인 subject block을 target으로 하여 소수의 파라미터로 개인화된 잔여 구조를 포착한다.

**분석:**

네 가지 조건을 비교한다. 베이스라인 V-JEPA2, Shared Brain-Tuned 모델, Personalized Brain-Tuned 모델, 그리고 참조 베이스라인으로 CLIP. 평가 지표는 공유 subspace RSM과의 CKA, 개인 subject block RSM과의 CKA, Figure 1과 동일한 방식의 피험자 간 예측 정확도, 그리고 downstream 감정 태스크(valence/arousal regression, 감정 카테고리 분류, Recall@K로 측정하는 affective video retrieval)를 포함한다.

정성적 분석으로는 tuning 전후 감정 공간의 UMAP 시각화, 그리고 어떤 감정 카테고리에서 가장 큰 표상 변화가 일어나는지를 확인한다.

**핵심 가설:**

Shared Brain Tuning은 공유 subspace와의 alignment를 높이고 downstream 감정 태스크 성능을 향상시킨다. Personalized adapter는 개인 subject block과의 alignment를 추가로 높인다. Shared Brain Tuning 이후에도 피험자 간 예측은 여전히 낮아, 개인화된 구조가 overwrite되지 않고 보존됨을 보인다. 이 분리는 공유된 구조와 개인화된 구조가 신경 감정 표상 안에서 기능적으로 분리 가능함을 보여주는 증거가 된다.

---

## Figure 간 연결 서사

Figure 1은 신경 감정 표상이 부분적으로 개인화되어 있음을 확인한다. 완전히 개인화된 통증(Lee et al., 2026)과 달리 부분적 개인화는 공유 구조의 존재 가능성을 시사한다.

Figure 2는 공유 subspace를 식별하고 특성화한다. 감정 카테고리가 공유 구조를 조직하며, 개인 residual은 덜 구조화되어 있음을 보인다.

Figure 3은 이 공유 구조가 몇 차원인지를 묻는다. 행동 데이터(Cowen & Keltner, 2017)와 신경 데이터(Horikawa et al., 2020)에서 발견된 ~27차원으로 수렴하는지 검증한다.

Figure 4는 이 geometry를 AI 모델에 transfer했을 때 감정 예측이 향상되는지를 검증하고, 공유된 구조와 개인화된 구조가 transfer 이후에도 기능적으로 분리 가능한지를 확인한다.

---

## 최종 주장

신경 감정 표상은 개인화된 구조와 공유된 구조를 동시에 포함한다. 공유된 구조는 ~27차원으로 수렴하며, 이는 행동, 신경, 계산 세 레벨에서 일관되게 나타난다. 이 geometry를 Brain Tuning을 통해 AI 모델에 transfer하면 감정 예측이 향상되며, 개인화된 구조는 그대로 보존된다. 이는 ~27차원이 생물학적 제약이 아니라 감정 정보 처리의 계산적 필연성임을 시사한다.
