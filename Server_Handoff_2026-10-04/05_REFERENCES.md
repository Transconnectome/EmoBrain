# EmoBrain 참고문헌·원천 기록

_2026-10-04 · 전달 설계에서 실제 사용하는 근거와 확인 범위 · 새로 140편을 전부 재검토했다는 기록이 아님_

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

## 📌 4. 인용 확인의 경계

이번 전달본의 중심 사실 확인은 로컬 설계 4종, 원문 corpus의 두 Horikawa Methods, 그리고 관련 방법론의 공식 논문 페이지·공개본을 대상으로 했다. 모든 논문 전체를 이번 작업에서 다시 정독한 것은 아니다. 설계 권고와 계산 그래프에 대한 논증은 기존 논문의 실증 결과와 구분했다.

과거 대화의 ‘Du et al.’은 정확한 title/year가 이번 인수인계에서 확정되지 않았으므로 특정 논문으로 임의 매칭하지 않았다. 원래 자료를 찾기 전까지 핵심 설계의 유일한 근거로 사용하지 않는다. 이 목록은 기존 전체 참고문헌을 삭제하는 목록이 아니다. Gao, Elazar, Meng, Vig 등 기존 원고의 추가 인용은 실제 본문 사용 여부와 원문 근거를 확인한 뒤 유지한다.

## 💾 5. 원본 문서 provenance

로컬 기준 폴더:

```text
/Users/moonseokjin/Documents/Connectome Lab/Project/EmoBrain/EmoBrain_Study_Documents/
```

서버에서는 이 경로를 자동 사용하지 않는다. 다음 hash는 이번 정리에서 확인한 원본을 식별한다.

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

