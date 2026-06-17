# Research Plan
## Shared and Individual-Specific Structures in the Neural Representation of Emotion

---

## 읽어야 할 페이퍼

### 핵심 데이터 / 프레임
- Horikawa, T., Cowen, A. S., Keltner, D., & Kamitani, Y. (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. *iScience*, 23(5), 101060. https://doi.org/10.1016/j.isci.2020.101060
- Cowen, A. S., & Keltner, D. (2017). Self-report captures 27 distinct categories of emotion bridged by continuous gradients. *Proceedings of the National Academy of Sciences*, 114(38), E7900–E7909. https://doi.org/10.1073/pnas.1702247114
- Lee, J.-J., Jo, S., Cho, S., & Woo, C.-W. (2026). Personalized brain decoding of spontaneous pain in individuals with chronic pain. *Nature Neuroscience*. https://doi.org/10.1038/s41593-026-02221-3

### 모델
- d'Ascoli, S., Rapin, J., Benchetrit, Y., Brookes, T., Begany, K., Raugel, J., Banville, H., & King, J.-R. (2026). A foundation model of vision, audition, and language for in-silico neuroscience (TRIBE v2). *FAIR at Meta*. https://github.com/facebookresearch/tribev2
- Bedel, H. A., Sivgin, I., Dalmaz, O., Dar, S. U. H., & Çukur, T. (2024). BrainJEPA: Representation learning for brain activity using joint-embedding predictive architecture. *arXiv*. https://arxiv.org/abs/2409.19407
- Assran, M., et al. (2025). V-JEPA 2: Self-supervised video models enable understanding, prediction and planning. *arXiv*. https://arxiv.org/abs/2506.09985

### 방법론
- Kornblith, S., Norouzi, M., Lee, H., & Hinton, G. (2019). Similarity of neural network representations revisited (CKA). *Proceedings of the 36th ICML*, PMLR 97:3519–3529. https://proceedings.mlr.press/v97/kornblith19a.html
- Kriegeskorte, N., Mur, M., & Bandettini, P. (2008). Representational similarity analysis – connecting the branches of systems neuroscience. *Frontiers in Systems Neuroscience*, 2, 4. https://doi.org/10.3389/neuro.06.004.2008
- Margulies, D. S., et al. (2016). Situating the default-mode network along a principal gradient of macroscale cortical organization. *Proceedings of the National Academy of Sciences*, 113(44), 12574–12579. https://doi.org/10.1073/pnas.1608282113
- Mantel, N. (1967). The detection of disease clustering and a generalized regression approach. *Cancer Research*, 27(2), 209–220. *(Mantel test 원논문)*

### 배경 — Affective Neuroscience
- Barrett, L. F. (2017). The theory of constructed emotion: an active inference account of interoception and categorization. *Social Cognitive and Affective Neuroscience*, 12(1), 1–23. https://doi.org/10.1093/scan/nsw154
- Lindquist, K. A., & Barrett, L. F. (2012). A functional architecture of the human brain: emerging insights from the science of emotion. *Trends in Cognitive Sciences*, 16(11), 533–540. https://doi.org/10.1016/j.tics.2012.09.005
- Satpute, A. B., & Lindquist, K. A. (2019). The default mode network's role in discrete emotion. *Trends in Cognitive Sciences*, 23(10), 851–864. https://doi.org/10.1016/j.tics.2019.07.003
- Cowen, A. S., & Keltner, D. (2021). Semantic space theory: A computational approach to emotion. *Trends in Cognitive Sciences*, 25(2), 124–136. https://www.cell.com/trends/cognitive-sciences/fulltext/S1364-6613(20)30276-X

---

## 핵심 질문

> **뇌의 감정 표상은 개인화된 구조와 공유된 구조를 동시에 가지는가?**
> **그리고 공유된 구조는 몇 차원이며, AI 모델에 주입할 수 있는가?**

---

## 배경 및 동기

| 연구 | 발견 | 우리 연구와의 관계 |
|------|------|-------------------|
| Cowen & Keltner (2017) | 행동 데이터에서 감정은 27차원으로 표상 | 공유 구조의 차원성 예측 |
| Horikawa et al. (2020) | 뇌에서도 동일한 구조 확인, transmodal regions | 데이터 + 뇌 구조 근거 |
| Lee et al. (2026) | 통증 표상은 완전히 개인화, 피험자 간 일반화 안 됨 | 프레임 차용 + 감정으로 확장 |

**Lee et al.과의 차별점:**
- Lee et al.: 통증은 완전히 개인화 → personalized approach 필요
- 우리: 감정은 개인화 + **공유 구조 공존** → 공유 구조가 27차원 → Brain Tuning 가능

---

## 전체 구조

```
CCN 2-page (4/2 데드라인)
    Preliminary: 개인화 + 공유 구조 공존 확인
            ↓
Full Paper
    Figure 1: 개인화된 구조 확인
    Figure 2: 공유된 구조 발견
    Figure 3: 공유 구조의 차원성 (~27차원)
    Figure 4: Brain Tuning
```

---

## CCN 2-page (3/26 ~ 4/2)

### 목표
풀 페이퍼의 Figure 1 + 2 preliminary version.
"감정 표상에 개인화된 구조와 공유된 구조가 공존한다"는 첫 번째 증거.

### 파이프라인
```
비디오 (2,181개)
    ↓
TRIBE v2 Transformer (frozen)
    ↓
Video Embedding (V-JEPA2 기반)

fMRI (whole-brain, 5 subjects)
    ↓
Brain-JEPA Embedding
    ↓
Subject Block (per-subject, 학습)
    ↑ target
```

### 분석
**개인화된 구조:**
- Cross-subject prediction: 다른 피험자의 subject block으로 감정 예측 실패하는가?
- Subject block 간 pairwise similarity → 얼마나 다른가?

**공유된 구조:**
- 5명 subject block의 공통 subspace 추출 (PCA)
- 공유 subspace에서 감정 카테고리별 clustering
- Video embedding과의 RSA/CKA alignment

### Figure
- Figure 1: Cross-subject prediction matrix (개인화)
- Figure 2: 공유 subspace UMAP — 감정 구조 시각화

### 제목
> *"Shared and Individual-Specific Structures in Neural Emotional Representations: A Preliminary Investigation"*

### 타임라인

| 날짜 | 할 일 |
|------|-------|
| 3/26 (오늘) | TRIBE v2 세팅, subject block 학습 시작 |
| 3/27 | Brain-JEPA + V-JEPA2 임베딩 추출 |
| 3/28 | Cross-subject prediction + CKA/RSA 분석 |
| 3/29 | Figure 제작, 결과 해석 |
| 3/30-31 | 글 작성 |
| 4/1 | 수정 버퍼 |
| 4/2 | 제출 |

---

## Full Paper

### 제목
> *"Shared and Individual-Specific Structures in the Neural Representation of Emotion"*

---

### Figure 1: 개인화된 구조 확인

**질문:** 감정 표상은 통증처럼 완전히 개인화되어 있는가?

**방법:**
- Lee et al. 프레임 그대로: subject block cross-prediction
- 피험자 A의 subject block으로 피험자 B의 감정 반응 예측
- 모든 피험자 쌍에 대해 반복

**기대 결과:**
- Cross-subject prediction 부분적 실패
- 단, 통증(Lee et al.)보다는 덜 개인화
- → 감정에는 공유 구조가 존재할 가능성 시사

---

### Figure 2: 공유된 구조 발견

**질문:** 개인화된 구조 안에 공유된 subspace가 존재하는가?

**방법:**
```
5명 subject block
    ↓
공통 subspace 추출 (PCA / CCA)
    ↓
공유 subspace에서:
    - 감정 카테고리별 RSM 계산
    - UMAP 시각화
    - Video embedding (V-JEPA2)과 CKA 비교
```

**기대 결과:**
- 공유 subspace에서 감정 카테고리별 구조 존재
- Video embedding은 공유 구조를 부분적으로만 포착
- 개인 고유 subspace에서는 구조가 덜 명확

---

### Figure 3: 공유 구조의 차원성

**질문:** 공유된 감정 표상 구조는 몇 차원인가? 27차원과 수렴하는가?

**실험 1: Intrinsic dimensionality**
```
공유 subspace의 내재적 차원수 측정:
    - Explained variance curve elbow
    - Participation ratio
    - Intrinsic dimensionality estimation
→ 자연스럽게 몇 차원이 나오는가?
```

**실험 2: Dimension sweep**
```
k = 5, 10, 15, 20, 27, 34, 50, 100
각 k에서:
    (a) Downstream emotion task 성능
    (b) 뇌 RSM과의 CKA alignment
    (c) Cowen의 27 label과의 correspondence
→ 최적 k가 어디에서 수렴하는가?
```

**실험 3: Cross-level Mantel test**
```
k = 27로 고정:
    행동 공간 (Cowen, 2,181 videos)
    뇌 공간 (Horikawa, fMRI RSM)
    공유 subspace (우리)

세 공간의 RSM 간 Mantel test
→ 세 레벨에서 동일한 기하학적 구조를 공유하는가?
```

**기대 결과 시나리오:**

| 시나리오 | 결과 | 해석 |
|---------|------|------|
| A (강) | k=27에서 모두 최적 | 27차원은 감정의 보편적 구조 |
| B (현실적) | k=20~30에서 plateau | ~27차원 구조, Cowen과 일치 |
| C (반례) | 최적 k가 27과 다름 | 행동/뇌/모델의 차원성 차이 → 왜 다른가? |

---

### Figure 4: Brain Tuning

**질문:** 공유된 감정 표상 구조를 video 모델에 주입할 수 있는가?
**그리고 개인화된 구조도 함께 포착할 수 있는가?**

**Shared Brain Tuning:**
```
공유 subspace RSM (target)
    ↓
V-JEPA2 fine-tuning
    Loss 1 — RSM loss:
        L = ||RSM_video - RSM_brain_shared||²
    Loss 2 — Contrastive loss:
        같은 감정 카테고리 → 가깝게
        다른 감정 카테고리 → 멀게
    ↓
Shared Brain-Tuned Video Model
```

**Personalized Brain Tuning:**
```
Shared Brain-Tuned Model
    ↓
Subject-specific lightweight adapter
    - 각 피험자 subject block을 target으로
    - 소수 파라미터로 개인 구조 포착
    ↓
Personalized Brain-Tuned Video Model (per subject)
```

**평가:**
```
정량적:
    - 뇌 RSM과의 CKA (tuning 전후 비교)
    - Cross-subject prediction: 여전히 실패? (Figure 1과 비교)
    - Downstream: emotion recognition, valence/arousal regression

정성적:
    - UMAP: Brain Tuning 전후 감정 공간 변화
    - 어떤 감정 카테고리에서 가장 큰 변화?
```

**핵심 가설:**
> Shared tuning → 공유 구조 포착, cross-subject prediction 개선
> Personalized adapter → 개인 구조 추가 포착
> 두 구조가 분리 가능함을 시사

---

## 최종 주장

> *감정 표상은 통증과 달리 개인화된 구조와 공유된 구조를 동시에 가진다.
> 공유된 구조는 ~27차원으로 수렴하며,
> 이는 인간 행동(Cowen), 뇌(Horikawa), Brain-Tuned 모델
> 세 레벨에서 일관되게 나타나는 감정의 보편적 계산적 구조다.
> 이는 27차원이 생물학적 제약이 아니라
> 감정 정보 처리의 계산적 필연성임을 시사한다.*
