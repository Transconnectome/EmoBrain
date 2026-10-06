# EmoBrain 참고문헌·원천 기록

_2026-10-06 · 전달 설계에서 실제 사용하는 근거와 확인 범위 · 새로 140편을 전부 재검토했다는 기록이 아님_

---

## 📚 1. 이론·데이터의 핵심 문헌

### Kragel et al., 2019

Kragel, P. A., Reddan, M. C., LaBar, K. S., & Wager, T. D. *Emotion schemas are embedded in the human visual system*. Science Advances, 5, eaaw4358. [원문](https://doi.org/10.1126/sciadv.aaw4358).

연결: Visual emotion schema라는 개념적 출발점. 우리의 BVS teacher 설계나 ‘감정=감각+의미’ 전체 명제가 이 논문에서 이미 검증되었다고 쓰지 않는다.

### Horikawa et al., 2020

Horikawa, T., Cowen, A. S., Keltner, D., & Kamitani, Y. *The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions*. iScience, 23, 101060. [원문](https://doi.org/10.1016/j.isci.2020.101060).

연결: Normative category/dimension annotation과 neural encoding/decoding. 로컬 원문·Transparent methods에서 참가자 수, unique video 수, run 구조, duplicate 처리와 전처리 설명을 확인했다. 원문을 확인한 것이 서버 derivative 확인을 대신하지 않는다.

### Horikawa, 2025

Horikawa, T. *Mind captioning: Evolving descriptive text of mental content from human brain activity*. Science Advances, 11, eadw1464. [원문](https://doi.org/10.1126/sciadv.adw1464).

연결: Video-viewing cohort, caption reference, 반복 test와 학습 자극 제외 구조. 로컬 corpus 파일명에는 `(2024)`가 있으나 PDF 본문은 2025 정식 출판본이다. Imagery 부분은 현재 연구 범위에서 제외한다.

### Cowen and Keltner, 2017

Cowen, A. S., & Keltner, D. *Self-report captures 27 distinct categories of emotion bridged by continuous gradients*. PNAS, 114, E7900–E7909. [원문](https://doi.org/10.1073/pnas.1702247114).

연결: 영상 기반 고차원 annotation의 원천 맥락. 이 논문의 최종 category 수와 Horikawa release의 34-D 열 수를 같은 것으로 취급하지 않는다. 실제 분석 target은 release codebook으로 결정한다.

## ⚙️ 2. 표현·모델·학습 근거

### V-JEPA 2

Assran et al. (2025). *V-JEPA 2: Self-supervised video models enable understanding, prediction and planning*. [논문](https://arxiv.org/abs/2506.09985).

연결: Frozen spatiotemporal video representation의 후보. 인간의 순수 시각 시스템이나 emotion-free feature라는 근거는 아니다. 실제 checkpoint와 pooling의 적합성은 미확정이다.

### Encoding과 regularization

Naselaris, T., Kay, K. N., Nishimoto, S., & Gallant, J. L. (2011). *Encoding and decoding in fMRI*. NeuroImage, 56, 400–410. [원문](https://doi.org/10.1016/j.neuroimage.2010.07.073).

Nunez-Elizalde, A. O., Huth, A. G., & Gallant, J. L. (2019). *Voxelwise encoding models with non-spherical multivariate normal priors*. NeuroImage, 197, 482–492. [원문](https://doi.org/10.1016/j.neuroimage.2019.04.012).

연결: Encoding/decoding 질문의 구분, feature-group regularization. 현재 데이터에서 banded/multi-kernel ridge가 최선이라는 보증은 아니다.

### Privileged information과 shortcut

Lopez-Paz, D., Bottou, L., Schölkopf, B., & Vapnik, V. (2016). *Unifying distillation and privileged information*. ICLR. [논문](https://arxiv.org/abs/1511.03643).

Wang, W., Tran, D., & Feiszli, M. (2020). *What makes training multi-modal classification networks hard?* CVPR. [저자 논문](https://arxiv.org/abs/1905.12681).

연결: Training-only additional information의 활용, modality별 optimization/overfitting 차이. 두 논문은 EmoBrain teacher가 fMRI를 무시했다는 직접 증거가 아니다. Brain reliance는 본 연구의 controls로 검정한다.

Frank, S., Bugliarello, E., & Elliott, D. (2021). *Vision-and-Language or Vision-for-Language? On Cross-Modal Influence in Multimodal Transformers*. EMNLP, 9847–9857. [원문](https://aclanthology.org/2021.emnlp-main.775/).

연결: Cross-modal input ablation으로 modality 영향의 비대칭성을 진단하는 근거. 공식 초록과 서지 정보를 확인했다. 원 논문의 vision/language 결과가 fMRI 활용, brain swap의 분포 내 타당성, dropout rescue의 성공을 검증한 것은 아니다. Wang et al.의 저자 공개 초록도 다시 확인했으며 modality별 일반화·과적합 차이의 근거로만 사용한다.

### 학습 불균형 보완 전략의 추가 근거

Peng, X., Wei, Y., Deng, A., Wang, D., & Hu, D. (2022). *Balanced Multimodal Learning via On-the-Fly Gradient Modulation*. CVPR, 8238–8247. [공식 논문 페이지](https://openaccess.thecvf.com/content/CVPR2022/html/Peng_Balanced_Multimodal_Learning_via_On-the-Fly_Gradient_Modulation_CVPR_2022_paper.html).

확인 범위: 공식 서지와 공개 초록의 modality별 학습 불균형·gradient modulation 설명. Wang et al. (2020)과 함께 학습 전략 검토의 근거로 사용한다. EmoBrain의 Brain-first 초기화나 공유 Affect Head 조합을 이 논문에서 검증했다고 쓰지 않는다. Gradient modulation 자체도 현재 채택된 학습법이 아니다. Warm-up/보조 loss의 선택은 D20/D21의 프로젝트 설계이며, circular-analysis 문헌과 연결해 학습 목표가 유도한 표상과 독립적인 뇌 증거를 구분한다.

## 🔍 3. 해석·통계·전처리 근거

### Probing과 geometry

Hewitt, J., & Liang, P. (2019). *Designing and interpreting probes with control tasks*. EMNLP-IJCNLP, 2733–2743. [원문](https://aclanthology.org/D19-1275/).

Kornblith, S., Norouzi, M., Lee, H., & Hinton, G. (2019). *Similarity of neural network representations revisited*. ICML, 3519–3529. [원문](https://proceedings.mlr.press/v97/kornblith19a.html).

연결: Probe의 제약과 CKA의 representation comparison. Linear probe 양성을 computation의 사용으로, CKA 양성을 causal equivalence로 해석하지 않는다.

### Activation patching

Heimersheim, S., & Nanda, N. (2024). *How to use and interpret activation patching*. [논문](https://arxiv.org/abs/2404.15255).

연결: Patching metric과 해석의 주의점. Whole-state 복원이 자명한 QA가 되는 문제는 이 프로젝트 계산 그래프를 검토한 별도의 논증이다. 이 논문이 현재 fMRI architecture의 selective patching을 검증한 것으로 인용하지 않는다.

### Participant와 stimulus 일반화

Schütt, H. H., Kipnis, A. D., Diedrichsen, J., & Kriegeskorte, N. (2023). *Statistical inference on representational geometries*. eLife, 12, e82566. [원문](https://doi.org/10.7554/eLife.82566), [저자 공개본](https://arxiv.org/abs/2112.09200).

연결: Participant와 condition을 함께 고려하는 inference. n=5/6에서 어떤 hierarchical model이나 bootstrap이 자동으로 충분하다는 인용으로 사용하지 않는다.

### Response와 atlas

Prince et al. (2022). *Improving the accuracy of single-trial fMRI response estimates using GLMsingle*. eLife, 11, e77599. [원문](https://elifesciences.org/articles/77599).

Schaefer et al. (2018). *Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI*. Cerebral Cortex, 28, 3095–3114. [원문](https://doi.org/10.1093/cercor/bhx179).

Tian et al. (2020). *Topographic organization of the human subcortex unveiled with functional connectivity gradients*. Nature Neuroscience, 23, 1421–1432. [원문](https://doi.org/10.1038/s41593-020-00711-6).

연결: 선택 가능한 response estimation과 anatomical grouping. 이 문헌의 존재만으로 atlas resolution이나 GLMsingle 적용이 자동 확정되지는 않는다.

## 🔄 4. 2026-10-06 보강에 사용한 근거

### Predictive overlap

Lescroart, M. D., Stansbury, D. E., & Gallant, J. L. (2015). *Fourier power, subjective distance, and object categories all provide plausible models of BOLD responses in scene-selective visual areas*. Frontiers in Computational Neuroscience, 9, 135. [원문](https://doi.org/10.3389/fncom.2015.00135).

연결: 내용·정서 encoding의 성능 순위만으로 공유/고유 설명력을 구분할 수 없으므로 1b의 결합 모델 비교를 두는 근거다. 논문 페이지의 encoding과 variance partitioning 설명을 확인했다. 현재 제안의 공통 SSE score는 프로젝트 운영 권고이며 논문의 score를 그대로 복제한 것으로 쓰지 않는다.

### Independent selection and validation

Kriegeskorte, N., Simmons, W. K., Bellgowan, P. S. F., & Baker, C. I. (2009). *Circular analysis in systems neuroscience: the dangers of double dipping*. Nature Neuroscience, 12, 535–540. [원문](https://doi.org/10.1038/nn.2303), [서지/초록](https://pubmed.ncbi.nlm.nih.gov/19396166/).

연결: Discovery 선택과 최종 검증 자료를 분리하는 원칙. 현재 2d content-side bridge 자체를 검증한 논문은 아니다. 같은 B와 f(B)를 다시 비교하는 문제는 프로젝트의 별도 계산 그래프 논증이다.

기존 Kragel 2019는 모델의 정서 관련 출력과 fMRI 관계를 별도로 검증했다는 점에서도 2d를 뒷받침한다. Affect-neighborhood retrieval은 Hewitt/ Liang의 control-probe 원칙에 동기를 둔 새 설계 제안이지 해당 논문의 기법을 그대로 적용했다는 뜻이 아니다. 1b·2d·채택된 보조 retrieval의 실제 효과는 미확인이다.

## 📌 5. 인용 확인의 경계

2026-10-04 전달본에 기록된 중심 사실 확인은 로컬 설계 4종, 원문 corpus의 두 Horikawa Methods, 그리고 관련 방법론의 공식 논문 페이지·공개본을 대상으로 했다. 이번 2026-10-06 보강은 그 기록을 계승했으며 전체 원문을 새로 정독했다는 뜻이 아니다. 새 확인 범위는 앞 절과 06 보강 문서에 명시한다. 설계 권고와 계산 그래프에 대한 논증은 기존 논문의 실증 결과와 구분한다.

과거 대화의 ‘Du et al.’은 정확한 title/year가 이번 인수인계에서 확정되지 않았으므로 특정 논문으로 임의 매칭하지 않았다. 원래 자료를 찾기 전까지 핵심 설계의 유일한 근거로 사용하지 않는다. 이 목록은 기존 전체 참고문헌을 삭제하는 목록이 아니다. Gao, Elazar, Meng, Vig 등 기존 원고의 추가 인용은 실제 본문 사용 여부와 원문 근거를 확인한 뒤 유지한다.

## 💾 6. 원본 문서 provenance

이전 로컬 문서군 이름 (개인 Mac 절대 경로는 저장소에 복제하지 않음):

```text
EmoBrain_Study_Documents/
```

서버의 편집 기준은 `docs/current`다. 다음 hash는 2026-10-04 전달본에 기록된 원본 식별자다. 이번 2026-10-06 보강에서 원본 4종을 재작성하거나 이 hash를 새 실행 증거로 사용하지 않았다.

```text
paper_v15.md
08ee0c556828e6b1caf5aa9b846fc16d9f7eff92fbdf55d66de81632e75be0f9

prereg_v2.md
e5dd6dac6d24451a23db1e27c92034975cc2e9d87ec9ce8acf4110c044c21973

implementation_v2.md
80be787455480700db81881c2093b7ccb9bf8e426c754a6eb5f5edad0d1667b4

action_items_v1.md
fc9d26db1916471f7a1489ea47ffe50960a640dbdb200f4d3ce61ee55959e997
```

원본은 보존했다. 과거 설계와의 차이는 [결정·정정 기록](04_DECISION_REGISTER.md)을 따른다. 서버 AI가 갖고 있는 버전의 hash가 다르면 이전 작업을 덮어쓰지 말고 내용 차이를 먼저 비교한다.

## 📚 7. 전처리 재검토 근거

[07 전처리 검토](07_RESPONSE_ESTIMATION_REVIEW.md)에 두 Horikawa 원문의 block/window/TR 차이, GLMsingle의 가변 duration·데이터 이용 범위, Brain-JEPA 원 논문과 공식 구현을 기록했다. 이 근거는 estimator 선택의 이유와 한계를 설명하며 새 모델 도입을 뜻하지 않는다. 현재 blocks_mcap·runz·서버 timing은 미확인이다.

## 📚 8. ROI increment 검토 후보의 근거

[D19/R15](04_DECISION_REGISTER.md)의 문헌 근거이며 새 분석의 포함 승인은 아니다.

- Kragel, Reddan, LaBar & Wager (2019). *Emotion schemas are embedded in the human visual system*. Science Advances, 5, eaaw4358. https://doi.org/10.1126/sciadv.aaw4358 — 시각피질에서 emotion-related 모델 출력과 decoding을 조사한 선례. 저자 소속기관 공개 PDF의 초록·Introduction을 재확인했다: https://dibs-web01.vm.duke.edu/labar/pdfs/Kragel_et_al_2019.pdf . Amygdala 추가 효과의 근거로 확대하지 않는다.
- Horikawa, Cowen, Keltner & Kamitani (2020). *The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions*. iScience, 23, 101060. https://doi.org/10.1016/j.isci.2020.101060 — 여러 뇌 영역의 고차원 decoding이라는 기존 연구 맥락. 이번 확인은 공개 논문 초록/검색 본문 범위이며 원문 전체를 새로 읽었다고 주장하지 않는다.
- Billot, Bocchetta, Todd, Dalca, Rohrer & Iglesias (2020). *Automated segmentation of the hypothalamus and associated subunits in brain MRI*. NeuroImage, 223, 117287. https://doi.org/10.1016/j.neuroimage.2020.117287 — 작은 크기와 주변 contrast 부족으로 인한 hypothalamus 분할의 어려움. PubMed 초록과 서지 확인: https://pubmed.ncbi.nlm.nih.gov/32853816/ . 구조 MRI 분할 연구이며 우리 task-fMRI의 신뢰도 또는 decoding 효과를 검증한 논문은 아니다.

현재 dataset의 실제 ROI 신호·coverage·예측 증분은 검증되지 않았다. 성능 향상, 피질하의 고유 정서 기능 또는 새 논문의 성립 가능성을 문헌만으로 확정하지 않는다.
