# EmoBrain 전처리 검토: 자극별 반응과 시계열

_2026-10-06 · 현재 데이터·코드 미검증 · D04의 판단 근거와 실행 전 점검 · estimator 확정 아님_

---

## 📋 1. 질문과 현재 권고

질문은 “영상별 내용–정서 관계를 연구할 때, 블록 평균이 주 입력으로 충분한가?”다.

성립 조건은 정확한 자극–BOLD 정렬, 분석에 필요한 공간 패턴의 보존, 해석 가능한 자극별 추정치, 그리고 개발 자료에서의 안정성이다. 반례는 평균으로 소실된 시간 정보가 단순한 길이·운동·이웃 자극 효과가 아니라 독립적인 content/affect 예측과 일관된 신경 대응을 제공하는 경우다. 시계열이 이긴다는 결과 없이 우월성을 가정하지도 않는다.

권고는 **자극당 한 공간 반응 벡터**를 현재 주 모델의 입력 단위로 유지하고, 원문에 맞는 **HRF 지연 보정 블록 평균**을 출발점으로 사용하는 것이다. 단순한 onset–offset 평균이 이미 적절하거나 GLM보다 낫다고 확정하지 않는다. D04의 timing/derivative audit 후 사전 규칙으로 동결한다.

시계열은 잘라낸 조각만이 아니라 전처리된 연속 run, 정확한 time axis, events, nuisance/confounds와 함께 보존한다. 현재 응답은 서버 파일을 변경하거나 새 대규모 시계열 모델 실험을 승인하지 않는다.

## 🔍 2. 확인한 사실과 확인하지 못한 전제

### 후속 보고와 사용자 정정

2026-10-06 사용자가 전달한 산출물 보고에는 T1w 2 mm의 voxel별 블록 반응, 별도 runz, 반복별 행, samples의 content ID, 두 cohort의 atlas가 존재한다고 기록되어 있다. 이 보고를 읽었으나 `response_t1w.py`, `runz.py`, 실제 배열·events를 서버에서 직접 검증하지 않았다. 아래의 ‘미확인’은 보고가 없다는 뜻이 아니라 독립적인 구현 검증이 남았다는 뜻이다.

보고서에는 반복 test 신뢰도로 후보를 선택했다는 문장이 있었지만, 사용자는 이후 여러 전처리 후보를 비교 중이라고 정정했다. 따라서 test에 맞춰 최종 전처리를 확정했다고 단정하지 않는다. 후보 생성·비교와 최종 선택은 구분한다. Test 결과에 접근한 이력, 실제 선택 시점과 기준은 서버 audit에 기록하며, 앞으로의 최종 선택·동결 규칙은 따로 정한다.

보고서상 시계열 조각과 블록 반응은 filtering/smoothing이 다르므로 서로 동일한 derivative라고 가정하지 않는다. MindCaptioning 일부 참가자의 시상하부 coverage 저하도 보고되어 있어 D19의 hypothalamus 후보는 coverage·신호 QA가 선행되어야 한다. 이는 보고된 제한이며 실제 마스크 확인 전 전체 참가자에 적용하거나 해당 영역에 정보가 없다고 결론 내리지 않는다.

| 항목 | 확인 범위 | 의미 |
|---|---|---|
| 원본 prereg B1 | 로컬 문서 확인 | Block response는 재현 baseline; 대체 beta 검토 명시 |
| 최신 전달본 D04 | 로컬 문서 확인 | Estimator는 미동결 |
| MindCaptioning의 영상 길이 | 2025 원문 확인 | Median 4.51초는 원본 영상 길이 |
| 영상 반복 재생 | 두 원문 확인 | 2025는 10초, 2020은 8초 미만 영상을 block 안에서 반복 |
| 시간 지연 처리 | 두 원문 확인 | 4초 이동 후 평균; 동일한 세부 pipeline은 아님 |
| 현재 blocks_mcap 및 runz | 서버 코드 미확인 | 올바른 window·정규화·완료 상태 판정 불가 |
| 블록 5–47 volumes, 15초 초과 약 11% | 사용자 제공 설명 | 현재 derivative에서 재계산하지 않음 |

2025의 TR은 1초이며 run 내부 voxel z-score를 보고한다. 2020의 TR은 2초이며 평균 구간에 video presentation과 후속 2초 rest가 포함된다고 기술한다. Motion/nuisance 및 z-score scope도 다르므로 “두 논문이 완전히 같은 전처리”라고 쓰지 않는다.[^1][^2]

짧은 clip을 반복하는 설계에서는 원본 duration, 실제 presentation/block duration, 평균에 들어간 BOLD volume 수가 다른 변수다. 따라서 “median 4.5초이니 15초 이상 영상에서만 시간 정보가 의미 있다”는 결론은 뒷받침되지 않는다. 정확한 길이 분포는 events와 추출 코드로 계산한다.

원본 prereg B1의 “반복 test reliability로 선택”도 그대로 실행하지 않는다. 최종 test를 보고 estimator를 고르면 label-blind라도 test 적응이다. 최신 전달본 원칙대로 별도 개발 자료 또는 사전 단일 규칙을 사용한다. 실제 등록 계획과 충돌하면 amendment·노출 이력을 기록한다.

## 🎯 3. 무엇을 평균하고 무엇을 남기는가

| 구분 | 조작 | 유지·손실 |
|---|---|---|
| 블록 안 시간 평균 | 각 voxel의 여러 시점을 요약 | Voxel 간 공간 패턴 유지, 시간 순서 손실 |
| ROI 안 공간 평균 | ROI 내 voxel을 하나로 요약 | Within-ROI 패턴 손실 가능 |
| 반복 trial 평균 | 같은 clip의 여러 presentation 결합 | Trial 변동 소실, 별도 저장 필요 |
| 참가자 평균 | 참가자 반응 결합 | 개인 변동 소실; 현재 기본 입력 아님 |

블록 평균을 쓴다는 것이 뇌를 ROI별 scalar 하나로만 축약하거나 참가자를 평균한다는 뜻은 아니다. 현재 ROI-PCA 인터페이스는 voxel 공간 패턴을 유지한 자극별 response에 적용할 수 있다.

이 설계로 “어떤 공간 패턴이 어떤 visual/semantic content와 대응하는가?”를 조사할 수 있다. “먼저 시각 처리가 일어나고 다음에 의미와 감정이 생성된다”는 시간적 순서나 인과 과정은 검증하지 못한다.

## ⚙️ 4. 입력 선택의 이유와 대안

### 자극별 요약 벡터의 여섯 질문 rationale

1. **질문:** 각 영상의 공간적 뇌 반응과 장면 내용·normative profile의 관계는 무엇인가?
2. **없을 때의 대안 설명:** 불필요한 시간 자유도가 duration/order/motion이나 HRF 차이를 이용할 수 있고, 연구 질문보다 temporal architecture 비교가 중심이 될 수 있다.
3. **근거:** 두 Horikawa 연구는 지연 보정 후 자극별 반응을 사용했다. 현재 target도 영상 단위다. 이것이 현재 데이터에서 평균의 최적성을 입증하지는 않는다.[^1][^2]
4. **선택 이유:** 시간별 정서 annotation 없이 자극 수준 질문을 다루고, 작은 모델·동일한 입력 계약으로 encoding/probing/readout을 연결할 수 있다.
5. **변경 기준:** 개발 자료에서 시간 정보를 보존한 작은 대안이 nuisance를 고려한 뒤에도 재현 가능한 추가 content 신호를 제공하거나, 평균이 HRF/인접 자극에 심하게 오염되면 재검토한다.
6. **한계:** 영상 내 감정 dynamics, 개인 정서의 발생 순서, 평균이 통계적으로 최적이라는 주장을 하지 않는다.

### 세 후보의 위치

| 후보 | 현재 위치 | 필요한 조건 |
|---|---|---|
| 원문 정렬 lagged block mean | 주 입력 출발점 권고 | 정확한 window·nuisance·scope 확인 |
| Duration-aware trial GLM beta | 필요시 제한된 대안 | 실제 onset/duration, 식별 가능성, HRF·잡음 모델 QA |
| 작은 temporal encoder | 후속 질문 발생 시 개발 후보 | 독립적 시간 정보의 이득, leakage·capacity 통제 |

자극당 한 줄이라는 모델 인터페이스는 평균과 GLM beta 모두 수용한다. GLM은 원래 시계열과 timing으로 자극별 반응 계수를 추정한 뒤 한 벡터를 내놓으므로, “평균 또는 시계열 딥러닝”만이 선택지가 아니다.

입력에 T개 시점이 있다고 학습 파라미터나 과적합 위험이 반드시 T배가 되는 것은 아니다. 공유 가중치와 pooling을 쓰는 작은 시계열 모델도 가능하다. 반대로 T개 volume을 독립 학습 표본으로 세면 안 된다. 현재 주 모델의 단순성을 지지하는 이유는 estimand·annotation granularity·검증 비용이지 입력 차원 배수만이 아니다.

평균은 평균화할 잡음의 공분산과 response 안정성에 따라 도움이 될 수 있지만, 자기상관·systematic nuisance·HRF overlap을 자동 제거하지 않는다. 앞쪽 몇 volume을 삭제하는 방식도 이전 자극 성분만 골라 제거하지 않으며 현재 자극 신호를 잃을 수 있다. 임의 trimming을 기본 강건성 분석으로 추가하지 않는다.

### GLMsingle을 자동 교체안으로 두지 않는 이유

GLMsingle은 single-trial beta의 reliability와 시간상 이웃 trial 간 오염을 개선하기 위한 근거 있는 후보지만, 현재 EmoBrain의 효과는 미확인이다.[^3] 공식 문서는 서로 다른 event duration의 amplitude 해석이 어렵고 도구가 이를 특별히 잘 해결하는 것은 아니라고 명시한다. 데이터 기반 hyperparameter 선택에 필요한 repetition 구조와 train/test 이용 범위도 검토해야 한다.[^4]

먼저 actual duration을 반영하는 GLM의 식별 가능성과 데이터 가용성을 판단한다. GLMsingle을 언급했다는 이유만으로 모든 clip을 같은 길이로 강제하거나 반복 최종 test로 HRF/regularization을 고르지 않는다. 이 GLM의 regularization과 downstream brain encoder/probe의 ridge는 별도 단계다.

## 📚 5. Brain-JEPA의 위치

Brain-JEPA 원 논문은 UK Biobank resting-state fMRI 사전학습과 demographic/trait/clinical downstream 평가를 보고한다. 기본 입력은 450 ROI × 160 time points이고 시간 해상도를 약 2초로 맞추었다.[^5] 이는 짧은 영상별 task-evoked 공간 패턴을 내용·정서와 연결하는 현재 설정과 다른 출발점이다.

“Resting-state에서 사전학습했으니 task fMRI에 절대 사용할 수 없다”는 결론은 아니다. 다만 현재 연구에는 전이 이득이 검증되지 않았고, parcellation·within-ROI 정보·시간 길이·normalization 및 사전학습 목적의 차이를 관리해야 한다.

현재 primary에 넣지 않는 이유는 필수 과학적 질문이 없고 입력 mismatch 비용이 크기 때문이다. 나중에 별도 temporal question이 생기면 작은 비사전학습 baseline과 frozen transfer를 제한적으로 비교할 수 있다. Block vector를 시간축으로 복제하거나 서로 다른 clip을 이어 붙여 160점을 만들었다고 유효한 within-stimulus 시계열이 되는 것은 아니다. 이 문서는 그런 실험의 실행 승인이 아니다.

## 🔐 6. 지금 서버에서 확인할 것

1. **현재 estimator 추적:** blocks_mcap 생성 코드/commit, 입력 derivative, onset 기준 start/end, 4초 이동 방향, dummy scan 제거 후 onset 보정, rest 포함, 경계 clipping, censor mask, 유효 volume 수를 기록한다.
2. **원자료 보존:** Raw 및 전처리 continuous run, events, confounds, TR, native-space 정보, censor mask를 유지한다. 기존 평균·반복별 response도 삭제하지 않는다.
3. **세 가지 duration 구분:** 원본 clip, 실험 block, 실제 포함 BOLD window를 별도 열로 저장한다. Runz 전에 평균했는지와 block별 가중치도 기록한다.
4. **정규화 audit:** 이미 run z-score된 derivative인지 확인한다. Run의 volume 기준과 block vector 기준 z-score는 일반적으로 같지 않다. 모델의 scaler/PCA는 여전히 train-only다.
5. **평가 가정 명시:** Whole-run label-free normalization을 허용하면 offline complete-run inference로 보고한다. Train/test stimulus가 같은 run에 섞이면 공유 통계를 점검한다. 실시간/단일 trial zero-calibration과 동일하다고 주장하지 않는다.
6. **인접성·nuisance QC:** Run-group split을 유지하고 duration, FD/motion, missing volumes, 평가·언어 block 주변, 인접 자극 영향을 점검한다. 음의 인접 상관을 무조건 artifact라고 단정하거나 0으로 만드는 것을 최적화 목표로 삼지 않는다.
7. **개발 선택만 허용:** Lagged mean의 QA가 충분하면 이를 유지한다. 문제가 확인되면 제한된 duration-aware GLM 대안을 개발 자료에서 검토한다. 최종 72개 test의 반복 신뢰도를 선택 기준으로 사용하지 않는다.
8. **D04 동결:** Window, preprocessing, normalization scope, estimator 선택 이유와 노출 이력을 기록한다. Primary/replication에 반복 횟수 차이가 있음을 별도로 보고한다.

권장 산출물은 response_estimator_audit.md, response_window_manifest.tsv, normalization_provenance.tsv, timing_qc, estimator_decision.md다. 현재 이 파일들이 서버에 생성되었다는 뜻은 아니다.

## 🔗 7. 근거와 한계

[^1]: Horikawa, T. (2025). Mind captioning: Evolving descriptive text of mental content from human brain activity. Science Advances, 11, eadw1464. Materials and Methods: Visual stimuli, Video presentation experiment, MRI data preprocessing. https://pmc.ncbi.nlm.nih.gov/articles/PMC12588295/
[^2]: Horikawa, T., Cowen, A. S., Keltner, D., & Kamitani, Y. (2020). The neural representation of visually evoked emotion is high-dimensional, categorical, and distributed across transmodal brain regions. iScience, 23, 101060. 로컬 원문 Transparent Methods의 Experimental design와 MRI data preprocessing을 확인. https://doi.org/10.1016/j.isci.2020.101060
[^3]: Prince, J. S., Charest, I., Kurzawski, J. W., Pyles, J. A., Tarr, M. J., & Kay, K. N. (2022). Improving the accuracy of single-trial fMRI response estimates using GLMsingle. eLife, 11, e77599. https://pmc.ncbi.nlm.nih.gov/articles/PMC9708069/
[^4]: GLMsingle authors. Official documentation: different event durations, hyperparameter/data scope. https://glmsingle.readthedocs.io/en/latest/wiki.html ; https://github.com/cvnlab/GLMsingle/blob/main/docs/source/wiki.md
[^5]: Dong, Z., et al. (2024). Brain-JEPA: Brain Dynamics Foundation Model with Gradient Positioning and Spatiotemporal Masking. NeurIPS 2024. https://papers.neurips.cc/paper_files/paper/2024/file/9c3828adf1500f5de3c56f6550dfe43c-Paper-Conference.pdf ; official implementation https://github.com/Eric-LRL/Brain-JEPA

확인한 것은 원문 방법 및 로컬 설계 문서다. 서버의 입력 배열·전처리 코드·완료 상태·길이 분포·새 분석 효과는 확인하지 못했다. 4초 이동은 원문 재현 설정이지 각 참가자/ROI의 최적 HRF 지연이 밝혀졌다는 뜻은 아니다.
