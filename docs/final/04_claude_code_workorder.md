# EmoBrain Claude Code 작업 지시서

2026-11-03

통합문서(2026-11-03판)에서 만든 판이다. 통합문서와 다르면 통합문서를 따른다. 작업 전에 같은 폴더의 01_integrated_document.md(통합문서)를 처음부터 끝까지 읽는다.

- 같은 폴더의 문서
    - 01_integrated_document.md: 통합문서. 유일한 기준이다.
    - 02_proposal.md: proposal(한국어)
    - 03_thesis.md: thesis(영어)
    - 04_claude_code_workorder.md: 이 문서
    - CLAUDE_EmoBrain.md: Claude Code가 매 세션 먼저 읽는 지침. claude.ai 프로젝트의 지침과 글쓰기 규칙을 옮겼다.
    - references.bib: 참고문헌 113개(통합문서 부록 4와 같음)
    - emobrain_fig5-6.pdf, emobrain_fig5-6.png: 통합문서 5-6의 구조 그림
    - 7-O(실행 사양 세부)는 통합문서 안에 있다.

## 0. 읽는 법과 고정 규칙

### 0-1. 읽는 법

- 근거 표기
    - 숫자로 된 것은 통합문서의 절이다. ex) 3-2, 6-1
    - 영문자와 숫자로 된 것은 통합문서 7단계 표의 행이다. ex) G16, L9, N34
    - O와 숫자로 된 것은 7-O의 행이다. ex) O4
    - "부록 3"은 통합문서 부록 3(실행 전에 확인할 것)이다.
- 인용은 APA 저자-연도로 쓴다. ex) Horikawa 외(2020), (Winkler 외, 2014)
    - MindCaptioning 논문은 Horikawa(2025)다. 그 자료(시청과 회상 fMRI, 사람 캡션)는 MC라고 부른다.
    - Horikawa 외(2020)의 자료는 HK라고 부른다.
- 7단계 표와 7-O의 상태
    - "정함"과 "추천"은 모두 그대로 구현한다.
    - "대체"는 그 행이 가리키는 절을 따른다.
    - 7-O의 다섯 묶음(O1~O5)은 11/3 사용자가 확정했다. 상태는 "정함"이다. "석진 님 결정"으로 남은 행은 없다.
- 이 문서의 표시
    - [레포에서 확인]: 통합문서가 경로나 이름을 주지 않은 것이다. 레포에서 찾아 기록 칸(2절)에 적는다.
    - [미확인]: 통합문서가 원문으로 확인하지 못했다고 적은 것이다. 그대로 둔다.
- 단계마다 같은 틀을 쓴다: 목적, 근거, 입력, 할 일, 출력, 확인 기준, 실행 주체, 7-O 항목.
    - "7-O 항목"은 그 단계에 걸린 7-O의 행이다. 통합문서로 정할 수 없던 세부는 모두 7-O로 옮겼다.
- 조건 이름(1-1). 한국어 이름과 thesis 영어 이름을 같이 쓴다.
    - Brain → Emotion: Direct training
    - Brain → Emotion [distillation]: Response-based distillation
    - Brain → Emotion + Vision + Caption: Auxiliary feature decoding
    - Brain + Decoded Feature → Emotion: Decoded-feature readout
    - Brain + Decoded Feature → Emotion [distillation]: Decoded-feature readout + response-based distillation
    - Multimodal Model의 중간 표현 비교(G16, 01 5-A의 E-고정, E-학습): E-고정은 frozen-head distillation, E-학습은 head를 복사해 함께 학습
    - 5-6의 그림에는 이전 영어 이름이 남아 있다. 코드와 결과 폴더에는 1-1의 이름을 쓴다(M3).
- 기호
    - s는 참가자다. 식 t(s, r)의 r은 ROI 번호다.
    - 상호작용 head의 r은 랭크다. ROI 번호와 글자가 같으므로 코드에서는 이름을 나눈다. ex) roi, rank
    - y는 규범 평정 34개(0~1)다. p는 모델 출력 확률, z는 sigmoid 전의 logit 34개다.
    - v는 시각 목표(5,632차원), c는 캡션 목표(4,096차원)다.
    - v̂, ĉ는 decoded visual features, decoded caption features다.
    - d는 모델 폭이다. H는 encoder를 거친 ROI token이다.
    - D_k는 바깥 fold k를 시험으로 둘 때의 바깥 학습 자료(나머지 run fold 5개)다.
    - K는 d와 입력층 weight decay의 후보 조합 수다(7-L).
    - "D9 좌표"는 D9의 차원별 표준화를 거친 좌표다.

### 0-2. 고정 규칙

- 설계를 바꾸지 않는다.
    - 문서와 레포가 다르면 멈추고 기록 칸에 적어 보고한다.
    - 문서로 정할 수 없는 일이 새로 생겨도 멈추고 기록 칸에 적어 보고한다.
    - 결과 수치에 영향을 줄 수 있는 값은 Claude Code가 정하지 않는다. ex) 후보값, 선택 기준, 전처리
    - 결과에 영향이 없는 구현 세부는 정해서 기록 칸에 적는다. ex) 새 파일 이름, 함수 구조
    - 설계 결정은 석진 님과 Claude가 통합문서에서 한다. 통합문서를 먼저 고치고 이 문서를 다시 만든다.
    - 메모리나 실행 시간 때문에 설계를 바꿔야 할 때도 직접 바꾸지 않는다. 측정값과 함께 보고한다(5-4).
    - 예외: 5-5는 d와 입력층 weight decay의 후보 범위를 Claude Code가 성능을 보기 전에 정하게 했다(S7).
- GPU 작업은 석진 님이 실행한다(M4). Claude Code는 스크립트와 실행 지시서(job script와 명령)만 만든다.
- 자료 경계
    - 시험 fold를 설정 선택, 조기 종료, 표준화, Stimulus Model 학습에 쓰지 않는다(H5).
    - 내용 구역과 이름표 짝을 정할 때 사람 평정, 뇌 자료, 모델 결과를 쓰지 않는다. 구역 수도 이것으로 정하지 않는다(4-2, 4-3, H5).
        - 내용 구역 k-means는 개발 영상 전체의 이름표 73개로 만든다(4-3).
        - 짝은 같은 시험 fold 안의 영상끼리 이름표 73개로 정한다(4-2).
    - MC 최종 시험 영상 72개와 그 중복 영상은 HK 개발의 모든 단계에서 뺀다(0절, 6-3). 학습, 설정 선택, 표준화, Stimulus Model, 내용 구역, 짝이 모두 해당한다.
    - 한 영상의 5명 행은 항상 같은 쪽(학습 또는 시험)에 둔다(H6).
    - 시험 때 뇌 모델에 넣는 것은 뇌 반응뿐이다(0절). 실제 Vision feature와 Caption feature는 학습 목표와 채점 기준으로만 쓴다.
- 정서 예측 모델의 설정 선택과 조기 종료는 모든 조건에서 실제 규범 평정에 대한 공통 검증 기준을 쓴다(7-O 3절, 11/3 사용자).
    - 설정 선택: 검증 자료의 정서별 Pearson r을 참가자마다 내고 34개 정서와 참가자에 걸쳐 평균한 값(5-5의 주 지표)
    - 조기 종료: 검증 자료의 정서 soft BCE(G13). patience 30, 최대 300 epoch
    - Stimulus 예측 평정, label smoothing 목표, 섞은 목표, feature decoding loss로 고르지 않는다.
    - 적용 세부는 O6이다.
- 결과를 보고 설계를 바꾸지 않는다. 결과에 따라 설계를 고르는 조건부 규칙도 만들지 않는다(0절). 결과에 따라 달라지는 것은 주장 범위뿐이다.
- 레포의 docs/archive/pre-final-2026-10와 04_DECISION_REGISTER는 옛 설계다(0절, N37). 이 폴더의 문서와 충돌하면 이 폴더의 문서를 따른다.
    - 옛 Study 1(joint latent 해석), Study 2 틀, 뇌를 받는 모델 T_BVS는 구현하지 않는다(0절).
    - 뇌를 받는 모델의 성능 점검(T_BVS 대 Stimulus Model)은 필수 실행 범위 밖이다(E7, 1-3 관점 B).
- 10월 사전 분석과 11/3 KHBM 초록용 분석의 수치는 논문 결과에 쓰지 않는다. 새 분할과 새 특징으로 다시 낸다(M6). 사전 분석에 노출된 선택은 노출로 기록한다(N1).
- 용어(1-1)
    - 모델 이름과 역할 이름을 섞지 않는다.
        - Feature Extractor: V-JEPA 2, DeBERTa처럼 특징을 뽑는 고정된 모델이다. Stimulus Model이 아니다.
        - Stimulus Model(visual-caption emotion predictor): Vision feature와 Caption feature로 정서를 내는 모델이다. Brain → Emotion [distillation]에 쓴다. 논문에서는 Stimulus Model다.
        - 뇌 모델(brain-only emotion decoder): 뇌 반응만 받는 모델이다. 논문에서는 Brain Model다.
    - 뇌에서 특징을 맞히는 일은 feature decoding, 그 값은 decoded features, 그 손실은 feature decoding loss다. distillation이나 reconstruction이라고 부르지 않는다(5-2).
    - 측정치는 Vision feature와 Caption feature다. Horikawa 외(2020)의 의미 이름표는 "이름표 73개"라고 부른다.

### 0-3. 자료 경계 요약

| 자료 | 쓰는 곳 | 쓰지 않는 곳 |
| --- | --- | --- |
| 바깥 시험 fold k | 평가 | 설정 선택, 조기 종료, 표준화, Stimulus Model 학습, nested OOF |
| 검증 fold(H2, D_k 안의 1개) | 뇌 모델의 설정 선택과 조기 종료, N8의 보정 통계 | 뇌 모델의 가중치 학습 |
| 남은 학습 fold 4개 | 뇌 모델의 가중치 학습 | |
| D_k 전체(5개 fold) | 최종 Stimulus Model과 K1 head의 표준화(N3. 표준화는 모델마다 그 학습 자료로 맞춘다), Stimulus Model의 시험 fold 예측과 K1 head(O16), ridge의 안쪽 5겹(H3) | Brain → Emotion [distillation]의 nested OOF(E4) |
| H2의 학습 fold 4개 | Brain → Emotion [distillation]의 nested OOF(E4, 안쪽 4겹) | |
| MC 최종 시험 72개와 그 중복 | 6-3의 시험, decoded features 채점 기준 | HK 개발 전부, MC 입력층 학습과 설정 선택 |
| 빠진 내용 구역(6-2) | 그 구역의 시험 | 그 실행의 학습, 설정 선택, 표준화, Stimulus Model |

## 1. 단계별 작업

### S0. 레포 점검과 보고

- 목적: 구현 전에 레포의 옛 설계, 코드, 자료, 캐시 상태를 파악한다. 그다음 설계를 레포에 동결한다.
- 근거: 0절, N37, M5, M2, 3-2(기존 캐시), 4-2(semantic_features.csv), 5-5(이전 지도), 5-2(GED 코드), 7-L 실행 순서 1
- 입력: 레포 전체, Perlmutter의 자료 폴더
- 할 일
    - 옛 설계 문서
        - docs/archive/pre-final-2026-10와 04_DECISION_REGISTER의 위치와 문서 목록을 적는다.
        - 이 폴더의 문서와 다른 점 가운데 구현에 영향을 주는 것을 적는다. ex) Study 1, Study 2, T_BVS, 이전 F6 구조, PCA 64
    - 기존 코드: 아래 파일이 있는지, 무엇을 하는지, 새 설계에 그대로 쓸 수 있는지 적는다. 경로는 [레포에서 확인].
        - make_horikawa_split.py, horikawa_rungroup6_v1.tsv: 분할(2-0)
        - stimulus_crosswalk.tsv: 중복 영상(B2)
        - runs.tsv, events_audited.tsv, stimuli.tsv: 세션, 상영 기록, 영상 길이(2-0, 3-2)
        - archive/.../extract_video_embeddings.py: 예전 V-JEPA 2 추출. NUM_FRAMES = 16, linspace(3-2)
        - lowlevel_features.py: 간단한 화면 통계 33개(3-6)
        - build_lab_features.py: 영상 기반 캡션 생성 모델의 오류 기록(3-4)
        - run_baselines.py, third_party/GED: GED를 우리 분할로 돌리는 코드. 이전 469개 지도로 돌렸다(5-2).
        - archive의 01_glasser_parcellation.py: Glasser 370개로 다시 나누는 코드. 결과 파일을 쓸 수 있는지 확인하지 못했다(5-5).
        - mlp_pooled.sh: 파일럿의 공통 영역 규칙. HK 5명 기준이다(C6).
        - Foundation_baseline/Brain-JEPA/atlas: 이전 469개 지도. 쓰지 않는다(5-5).
        - PREPROC_QC_REPORT, PRELIM_STAGE0_REPORT.md: 0단계 기록
    - 자료 경로: 아래 자료의 위치를 적는다. 모두 [레포에서 확인].
        - HK 5명의 voxel 원자료 캐시(C1의 run 안 z, v3_qc)
        - 34개 사람 평정 파일(N2)
        - 14개 정서 차원(1~9점) 파일(B4)
        - semantic_features.csv(영상 2,196개 × 73개)와 그 출처인 Perlmutter의 Horikawa_Haka/meta(4-2, 4-3)
        - MC 사람 캡션(영상마다 20개, 3-4)
        - MC 시청 fMRI(6명)와 그 사건 기록(6-3)
        - MC 최종 시험 72개 목록 파일(0절. 위치를 찾지 못했다)
        - Horikawa 외(2020)의 공개 자료 figshare 11988351(5-5)
        - 영상 파일 2,196개
    - 분할 파일 horikawa_rungroup6_v1: 열 구성, 영상 수, fold 수, 중복 15개 표시, MC 72개 제외가 들어 있는지 적는다.
    - 라벨: 열 이름이 score_0~33인지, 이름을 붙인 방식(알파벳 순)을 적는다. 대조는 S1에서 한다(N2).
    - 특징 캐시
        - 있는 캐시마다 모델, 체크포인트, 층, 프레임 규칙, 크기 조정, pooling, 코드 버전이 기록되어 있는지 적는다(M2).
        - 10월 V-JEPA 2 캐시와 예전 추출 코드의 연결을 적는다(3-2). V-JEPA 2는 새 규칙으로 다시 뽑는다(3-2).
        - 10월 MPNet 캐시의 추출 설정을 적는다. 7-O 3절의 MPNet 처리와 맞는지 본다.
    - 지침 연결(S0의 첫 작업)
        - 석진 님 컴퓨터의 EmoBrain 폴더에 CLAUDE.md가 있고, 이 파일이 `@EmoBrain_final_2026-11-03/CLAUDE_EmoBrain.md`를 불러온다(11/3). EmoBrain 폴더나 그 안에서 시작한 세션은 지침을 자동으로 읽는다.
        - Claude Code는 지침이 읽히는지만 확인한다. 레포에는 설계 동결 커밋 전까지 쓰지 않는다.
    - 설계 동결 커밋(N37, M5). 석진 님이 GPT 전체 검증 반영이 끝났다고 말한 뒤에 한다.
        - 문서 위치: docs/final에 둔다. 10월까지의 옛 설계 폴더는 docs/archive/pre-final-2026-10으로 옮겼고, 레포 지침과 README의 경로를 고쳤다(11/7 석진 님).
        - 레포 CLAUDE.md 끝에 CLAUDE_EmoBrain.md를 불러오는 한 줄을 더한다.
        - 레포 AGENTS.md와 docs/coordination의 역할 규칙(10/7)을 11/3 방식으로 고친다. 고칠 문장은 Claude Code가 초안을 만들고 석진 님이 확인한다. git과 Perlmutter 안전 규칙은 그대로 둔다.
        - 레포가 public이면 이 커밋으로 01~04가 공개된다. 커밋 전에 석진 님에게 공개해도 되는지 확인한다.
        - 커밋 메시지에 날짜를 넣는다. ex) 2026-11-03
        - 이 커밋이 통합문서의 결정과 6-1의 예측, 판정 문장을 결과 전에 동결한다(M5).
        - 브랜치와 push 규칙은 레포 CLAUDE.md를 따른다.
- 출력
    - 기록 칸의 S0 행
    - 레포 기준 문서 폴더의 문서, 옛 문서의 대체 표시나 archive 이동, 고친 AGENTS.md와 docs/coordination
    - 설계 동결 commit 해시(기록 칸)
- 확인 기준
    - 위 목록의 모든 항목에 위치나 "없음"이 적혀 있다.
    - 레포 기준 문서 폴더의 문서가 이 폴더의 문서와 같다.
- 실행 주체: Claude Code
- 7-O 항목: 없음

### S1. 실행 전 확인

- 목적: 실행 전에 확인하기로 한 사실을 확인한다. 확인하지 못한 것은 [미확인]으로 남긴다.
- 근거: 부록 3, N39, N2, B2, B6, B7, B8, C6, 0절, 2-0, 2-7, 3-1, 3-2, 3-6, 4-2, 4-3, 5-5, 6-3, 6-4, I7, K7, A9
- 입력: S0에서 찾은 자료와 코드
- 할 일
    - 라벨(N2, 부록 3)
        - score_0~33에 알파벳 순으로 이름을 붙였다. 의미 범주로 확인한 것은 disgust, romance, adoration, sexual desire 4개뿐이다.
        - 나머지 30개를 원 자료의 범주 순서와 맞춘다. 원 자료의 위치는 [레포에서 확인].
        - 하나라도 어긋나면 멈추고 보고한다. 어긋난 채로는 어떤 학습도 돌리지 않는다.
    - 영상 집합(0절, B2, 6-3)
        - 파일 2,196개, 분석 영상 2,181개(중복 15개 제외), 개발 영상(분석 영상에서 MC 최종 시험 72개를 뺀 것, 약 2,109개)의 실제 수를 센다.
        - 중복 15개의 구성을 적는다. B2에 따라 쌍마다 먼저 제시된 반응을 남긴 것을 확인한다.
        - 1349와 1363이 둘 다 분석 영상에 있고 같은 fold에 묶였는지 확인한다(B2).
        - 분석 영상 안에 같은 내용 영상이 남는지 확인한다. 남으면 그 목록을 만든다(O4의 순열과 bootstrap에서 묶음으로 다룬다).
        - MC 최종 시험 72개 목록 파일을 찾는다. 72개와 같은 내용의 영상도 찾는다.
        - MC는 파일 2,196개에서 중복 16개를 빼 2,180개를 썼다. HK의 중복 15개와 어느 영상이 다른지 대조한다(B2).
    - 평정자 수(B8, 부록 3)
        - 비율에서 거꾸로 센 평정자 수가 17을 넘는 영상 목록을 뽑는다.
        - 그 목록이 중복 영상과 겹치는지 확인한다.
        - 거꾸로 센 값은 가중치나 신뢰도 계산에 쓰지 않는다.
    - voxel과 ROI(5-5, C6, N39, 부록 3)
        - 참가자별 voxel 수와 ROI별 voxel 수를 HK 5명과 MC 6명 모두에서 센다. S7에서 d 후보와 가중치 수를 정하는 자료다.
        - 개인 공간 지도(5-5, 정할 것 5, 7, 11/4 정함). 피질 360개는 저자가 공개한 참가자별 ROI를 쓴다. 피질하 10개(편도체, 뇌간, 미상핵, 소뇌, 해마, 시상하부, BA34 기반 ROI, 창백핵, 조가비핵, 시상)는 11명 모두 새로 만든다. PickAtlas의 MNI_T1.nii를 개인 T1w에 ANTs로 직접 등록하고, 라벨을 T1w 1 mm로 최근접 이웃으로 옮긴 뒤, ROI에 속한 1 mm voxel의 중심이 드는 2 mm voxel을 포함한다. 코드 s1_original_rois.py, s1_subcortex_rebuild.py(overlap_2mm).
            - 재료의 위치와 검증은 PM/atlas_sources/README.md에 있다. 피질하는 좌우를 합친다(공개 코드 확인).
        - 공통 ROI(C6): HK 5명과 MC 참가자 모두에서 유효한 ROI만 남긴다.
            - 유효 여부는 해부학적 mask와 촬영 범위(QC mask)의 교집합으로만 정한다. 교집합이 비어 있지 않으면 유효하다(정할 것 6, 11/4 정함).
            - MC 시험 반응의 신뢰도나 예측 성능으로 고르지 않는다.
            - 남은 ROI 수를 기록한다. MC의 촬영 정보를 HK 입력 정의에 썼다는 사실도 기록한다.
        - 0단계 신뢰도를 새 지도(370개)로 다시 낸다(5-5). 그 결과로 지도를 바꾸지 않는다.
    - 참가자(6-3, 2-7, A9)
        - MC 참가자와 HK 참가자가 겹치는지 확인한다. Horikawa 외(2020)의 본문에는 참가자 정보가 없고 보충자료에 있다.
        - HK 참가자의 국적을 확인한다. 확인하지 못하면 [미확인]으로 둔다.
    - Horikawa 외(2020)의 보충자료(N39)
        - 복셀 선택 규칙(I7). 공개 코드로 확인했다(기록 칸). 학습 자료에서 목표와 상관이 높은 voxel을 ROI마다, 목표마다 최대 500개 고르고, 정칙화 강도는 안쪽 5겹으로 목표마다 정한다. S5에서 복셀 선택 ridge를 넣는다.
        - fold 정의(2-0)
        - Yeo 17과 주 경사의 세부(6-4)
    - 이름표 73개(4-2, 4-3)
        - semantic_features.csv가 Horikawa 외(2020)의 공개 자료와 같은지 확인한다.
        - 변환 이력을 적은 문서를 찾는다.
        - 지금 아는 것: 값은 0~1이고 82%가 0이다. 73개 열 가운데 44개의 최댓값이 1보다 작다(가장 작은 최댓값 0.5).
    - 특징 추출에 필요한 확인(3-1, 3-2, 3-6, 부록 3)
        - V-JEPA 2 공식 평가 설정의 프레임 간격과 해상도, 기존 캐시의 추출 설정
        - Horikawa(2025)의 공개 코드: 평균한 DeBERTa 층의 범위와 층 번호 규칙(O15), DeBERTa-large 체크포인트 이름, TimeSformer 체크포인트와 클립 구성(O14)
        - Horikawa(2025)가 쓴 CLIP 판(보충 자료). 확인하지 못하면 OpenAI ViT-B/16을 쓴다(3-1).
        - VideoMAE 공식 ViT-B/16 사전학습 전용 가중치의 체크포인트 이름(O11). 다른 baseline 모델의 사전학습 전용 가중치가 공개됐는지(3-1)
        - 8초 미만 영상의 반복이 끝나는 시점. 기록 칸의 불일치 8과 정할 것 11을 본다(3-2).
        - Du 외(2023)의 OSF(osf.io/9uyn2) 공개 특징을 받을 수 있는지(3-6)
        - 캡션 파일의 출처와 영상당 캡션 수(부록 3)
        - 정서어 181개 목록의 위치(부록 2)
    - MC 시청 자료(6-3)
        - 시청 학습 세션 2,180개, 시험 72개가 든 마지막 두 run, 입력층 학습 자료 2,108개를 확인한다.
        - 2,108개가 든 run의 순서와 수를 적는다(O29의 검증 run 배정에 쓴다).
        - run마다 3~4개 끼어 있는 평가 구간(앞 영상의 캡션 5개를 읽고 일치도를 매김)을 영상 제시 구간과 구분할 사건 기록과 반응 추출 코드를 찾는다.
    - 0단계 기록에서 찾을 것
        - 0단계에서 표시한 튀는 block과 run의 목록(B6. 기록용이고 빼지 않는다)
        - sub-05의 block 수 2,085개(B7)
        - 뇌 전체 평균과 block 신호 크기의 정의(I7, C1). 정의가 없으면 멈추고 보고한다.
        - 참가자 간 일치도의 계산 방법(K7)
    - 문헌 항목(부록 3, N39)
        - Cowen 평정자가 소리를 들었는지
        - He 외 2026(같은 자료, 신규성 위협 여부), Conwell 2025 DOI 연도, GED와 GE-END의 같은 DOI, KHBM 초록 마감, 신규성 검색(A4)
        - 레포 안의 기록만 찾는다. 없으면 [미확인]으로 둔다. 문헌 판단은 통합문서에서 한다.
    - 이번에 하지 않는 확인: MC 회상의 단서 읽기 구간과 떠올리는 구간의 분리(부록 3). 회상은 필수 실행 범위 밖이다(6-3).
- 출력
    - 기록 칸의 S1 행
    - 라벨 대조표
    - 영상 집합 목록: 분석 영상, 개발 영상, MC 72개와 그 중복, 남은 같은 내용 영상
    - 참가자별, ROI별 voxel 수 표
    - 공통 ROI 목록
    - 새 파일 이름은 Claude Code가 정해 기록한다.
- 확인 기준
    - 34개 열이 모두 원 자료의 범주와 맞는다.
    - 개발 영상 목록에 MC 72개와 그 중복이 없다.
    - 공통 ROI 수와 그 결정에 쓴 자료(mask, 촬영 범위)가 기록되어 있다.
- 실행 주체: Claude Code
- 7-O 항목: 없음. 라벨 대조, MC 72개 목록, 공통 ROI가 확인되지 않으면 S2를 시작하지 않고 보고한다. 나머지 항목은 [미확인]으로 적고 다음 단계로 간다.

### S2. manifest

- 목적: 모든 실행이 같은 자료 경계를 쓰도록 분할, 제외 목록, 내용 구역, 짝, ROI, 묶음을 파일로 고정한다.
- 근거: 2-0, B2, B6, B7, H6, 4-2, 4-3, J2, C6, 5-5, 6-4, K7, 6-3, M1, 7-L 실행 순서 3
- 입력: horikawa_rungroup6_v1.tsv, runs.tsv, events_audited.tsv, semantic_features.csv, S1의 영상 집합과 공통 ROI, CAB-NP 배정(출처 [레포에서 확인])
- 할 일
    - run 분할(2-0)
        - run 묶음을 6 fold에 배정하되 정서 평정과 영상 길이로 층화한다(2-0, 기록 칸 정할 것 12). horikawa_rungroup6_v1의 fold는 탐색의 시작점으로만 쓴다.
        - fold별 정서, 길이, 이름표 분포를 manifests/s2/fold_balance.tsv에 적는다. 이름표 73개는 맞추지 않고 결과만 적는다.
        - run 단위로 나눈다. 같은 내용 영상 쌍이 든 run은 같은 fold에 둔다.
        - MC 최종 시험 72개와 그 중복을 뺀다.
        - 5명은 같은 영상을 같은 순서로 봤다(레포 PREPROC_QC_REPORT 3.10). 시험 영상은 5명 모두 같다.
        - 한 영상의 5명 행은 같은 쪽에 둔다(H6).
        - 반응 크기 기준으로는 block과 run을 빼지 않는다(B6). 0단계에서 표시한 튀는 block 5개와 sub-03의 튀는 run은 manifest에 표시만 한다.
        - sub-05는 있는 block만 쓴다(B7). 5명 공통 영상 목록도 만든다.
        - 바깥 fold마다 H2의 검증 fold를 적는다. fold k의 검증은 fold k + 1, fold 6의 검증은 fold 1이다(H2, 11/3 사용자).
    - 세션 조건 검사(2-0, O8)
        - 참가자마다 61 run이 8개 세션에 나뉜다. 세션 경계는 참가자마다 다르다(runs.tsv).
        - 참가자마다, fold마다 두 지표를 표로 낸다. 시험 run이 온 세션 수, 한 세션에서 온 run 수의 최댓값이다.
        - 이 검사를 분할 코드에 넣는다. 판정은 O8이다.
        - 11/1의 근사 점검은 fold마다 시험 run 10~11개가 6~8개 세션에서 왔고, 한 세션에서 온 run은 최대 3개였다. 서버의 분할 파일로 다시 확인한다.
        - 사람 평정만으로 세션별 34개 정서 평균의 차이를 확인해 둔다.
    - 내용 구역(4-3, J2)
        - 재료는 개발 영상의 이름표 73개 원래 비율이다. 표준화하지 않는다.
        - 사람 평정과 뇌 자료는 쓰지 않는다.
        - k-means 5개. scikit-learn KMeans(n_init=10, random_state=0). 11/2 계산은 scikit-learn 1.9.1이었다. 쓴 판을 기록한다.
        - 크기 제약을 두지 않는다.
        - 구역 배정 파일을 저장한다.
        - 구역마다 기록할 것: 크기, 구역 평균이 높은 이름표 세 개, 표본 영상, 정서별 0이 아닌 학습 영상 수
        - 거리 점검을 개발 영상으로 다시 한다. 11/2 계산은 MC 72개를 빼지 않았다(4-3).
            - 거리는 아래 짝의 거리와 같은 정의다.
            - 구역 제외 학습: 시험 run fold 전체와 그 구역 전체를 뺀 영상
            - 학습량 대조: H2의 학습 fold 4개와 검증 fold에서 구역 제외 조건과 같은 수를 각각 무작위로 뽑은 영상. 그 구역을 후보에서 빼지 않는다. 20번 반복해 평균한다.
            - 구역마다, fold마다 낼 것: 시험 영상에서 가장 가까운 학습 영상까지 거리의 중앙값(구역 제외 대 학습량 대조), 그 비율, 대조보다 먼 시험 영상의 비율. 실제 학습에 쓰는 고정 표본의 거리와 비율도 함께 적는다(20번 평균은 진단 통계다). 주 지표는 실제 가중치 학습 영상 기준이고 검증을 포함한 값도 함께 적는다
        - 어떤 구역에서 거리가 늘지 않아도 구역 수를 바꾸지 않는다. 그 구역의 주장 범위만 줄인다(4-3).
        - 구역 크기, 구성 이름표, 정서 분포를 보고 구역을 바꾸지 않는다.
        - 6-2의 실제 학습에 쓸 학습량 대조 표본을 구역과 fold마다 하나 뽑아 manifest에 고정한다. 뽑을 때 쓴 seed를 기록한다.
    - 이름표 짝(4-2, O9)
        - 거리: 원래 비율의 동일 가중치 유클리드 거리다. 거리 = √(73개 이름표마다 두 영상의 값 차이를 제곱해 평균한 값)
        - 짝: 같은 fold의 시험 영상 가운데 자기 자신을 뺀, 거리가 가장 가까운 영상 하나다. 동점이면 O9를 따른다.
        - 거리 상한은 두지 않는다.
        - 같은 짝 목록을 모든 참가자와 모든 모델 조건에 쓴다.
        - 사람 평정과 모델 결과는 쓰지 않는다.
        - 짝마다 거리를 기록한다.
        - 짝이 없는 영상도 전체 정서 평가(2-3)에서는 빼지 않는다.
        - 짝 연결 묶음(O4 (2)): 최근접 짝으로 이어진 영상을 한 묶음으로 묶는다. ex) A→B와 C→B가 있으면 A, B, C가 한 묶음이다. fold마다 묶음 배정과 묶음 크기 분포를 저장한다. 바꿔 끼우기와 쌍 비교의 재표집 단위다.
        - 쌍 비교용 순서 없는 쌍 목록(O4 (7)): 서로 최근접인 쌍은 한 번만 넣고, 영상 번호가 작은 쪽을 A로 둔다.
    - 순열 단위(O4 (1)): 시험 영상마다 그 영상이 제시된 원래 run 번호를 manifest에 둔다. 6-2에서는 구역 번호도 같이 둔다.
    - ROI(C6, 5-5)
        - 370개(피질 HCP360 360개 + 피질하 Horikawa 외(2020)의 10개) 가운데 S1의 공통 ROI만 쓴다.
        - ROI마다 참가자별 voxel 목록을 manifest에 둔다. 저자 지도의 행 순서를 쓰지 않고, 좌표를 QC mask의 NumPy 순서 열 번호로 옮겨 둔다. 한 voxel이 여러 ROI에 들 수 있고 배타적인 라벨로 바꾸지 않는다.
    - 네트워크 묶음(6-4)
        - HCP360 영역을 CAB-NP(Ji 외, 2019)의 피질 12개 네트워크에 배정한다. 1차 시각, 2차 시각, 청각, 체성감각운동, cingulo-opercular, dorsal attention, frontoparietal, Default, 언어, posterior multimodal, ventral multimodal, orbito-affective
        - 피질하 10개는 해부학적 1묶음으로 둔다. 기능 네트워크라고 부르지 않는다.
        - 모두 13묶음이다. 공통 ROI를 적용한 뒤 묶음마다 ROI 수를 기록한다.
        - 참가자 간 일치도를 13묶음으로 다시 계산해 적는다(K7). 계산 방법은 0단계 방법을 따른다[레포에서 확인]. 그 결과로 묶음을 바꾸지 않는다.
    - MC 쪽(6-3)
        - 입력층 학습 자료 2,108개, 시험 72개(QC 뒤 남은 반복의 평균), 평가 구간을 뺀 영상 제시 구간을 manifest에 둔다.
        - 2,108개의 run을 학습 run과 검증 run으로 나눠 둔다(O29).
        - HK와 MC의 영상 ID 대응을 둔다.
- 출력
    - split manifest(M1)
    - 구역 배정 파일과 구역 기록, 학습량 대조 표본
    - 짝 목록(거리 포함), 짝 연결 묶음과 그 크기 분포
    - 시험 영상의 원래 run 번호(순열 단위)
    - 제외 block 목록, 5명 공통 영상 목록
    - 공통 ROI와 ROI별 voxel 목록
    - CAB-NP 13묶음 배정
    - MC manifest
    - 위치는 [레포에서 확인]. 새 파일 이름은 Claude Code가 정해 기록한다.
- 확인 기준
    - 어느 fold에서도 한 영상의 5명 행이 학습과 시험에 나뉘지 않는다.
    - 같은 내용 영상 쌍이 서로 다른 fold에 있지 않다.
    - 어느 manifest에도 MC 72개와 그 중복이 없다.
    - 세션 검사 표가 있다.
    - 구역 배정을 같은 설정으로 다시 돌리면 같은 배정이 나온다.
- 실행 주체: Claude Code. 계산이 가볍다. 직접 돌릴 수 있는지는 레포 CLAUDE.md를 따른다.
- 7-O 항목: O4(순열 단위와 짝 연결 묶음), O8(세션 조건 판정), O9(짝 동점과 빠진 block), O29(MC 검증 run)

### S3. 특징 추출

- 목적: 학습 목표, baseline 특징, 저수준 Vision feature를 참가자가 본 영상 그대로 뽑는다. 추출 기록을 함께 저장한다.
- 근거: 3-1, 3-2, 3-3, 3-4, 3-4b, 3-6, D3~D7, D9, M2, 7-L 실행 순서 2
- 입력: 영상 파일 2,196개, MC 사람 캡션(영상마다 20개), events_audited.tsv, stimuli.tsv, S1의 확인 결과
- 공통 규칙
    - 대상 영상
        - 파일 2,196개 전부를 뽑는다.
        - MC 72개의 특징은 6-3에서 decoded features를 채점하는 기준으로만 쓴다. HK 개발의 어느 단계에도 넣지 않는다(0-2).
    - 참가자가 본 영상을 재현한다(3-2).
        - 8초 미만 영상은 같은 영상을 반복해 8.0초에서 자른다(기록 칸 정할 것 11). 제시 길이는 코드 한 곳에서 받는다.
        - 반복 사이의 끊김도 그대로 둔다. 마지막 프레임으로 채우지 않는다.
        - 이 입력을 모든 Vision feature(V-JEPA 2, VideoMAE, TimeSformer, CLIP)와 저수준 Vision feature에 쓴다.
    - 화면(3-2)
        - 종횡비를 유지해 줄인 뒤 가운데 정사각형을 자른다.
        - 크기는 체크포인트의 공식 설정을 따른다(11/6 석진 님). V-JEPA 2는 짧은 변 292에서 가운데 256, VideoMAE와 CLIP은 짧은 변 224에서 224, TimeSformer는 짧은 변 224에서 세 위치 224다. 코드는 시작할 때 설정 파일과 같은지 확인한다. 모델 사이의 화면 범위 차이는 모델 차이에 포함해 해석한다.
        - 화소 정규화와 보간 방식은 체크포인트 전처리 설정의 값을 쓴다(V-JEPA 2, VideoMAE, TimeSformer는 bilinear, CLIP은 bicubic).
        - RGB 중앙값(O13)은 줄이지 않은 원래 화소의 가운데 정사각형에서 낸다.
        - 무작위 자르기와 뒤집기는 쓰지 않는다.
    - 프레임 뽑기는 O10이다. 실제 시간으로 초당 f장을 뽑고 보간하지 않는다.
    - window 나누기와 프레임 수는 O11이다.
    - 층 번호는 O15다. V-JEPA 2의 block 10, 20, 30, 40은 깊이 25%, 50%, 75%, 100%다(3-2).
    - 추출 기록(M2): 체크포인트 이름과 해시, 코드 commit, 해상도, 초당 프레임, 클립 길이와 간격, 짧은 영상 처리, 층 번호, pooling, 크기 조정을 manifest에 적는다.
- 할 일
    - V-JEPA 2(주 시각 모델, 3-1, 3-2, D3~D6)
        - 체크포인트: facebook/vjepa2-vitg-fpc64-256(ViT-g, 64프레임, 256화소). 인코더는 고정한다.
        - 입력: 초당 4장, 최대 64프레임(16초)을 한 입력으로 처리한다. 뽑은 프레임 수 N이 64를 넘는 영상(파일 81개)은 O11의 window 규칙으로 나눠 평균한다. 기준은 초가 아니라 N이다. N이 홀수인 처리는 N이 64 이하일 때만 한다(O11).
        - 저장: 40개 block(폭 1,408) 모두의 token 평균
            - token 평균은 입력 안의 시공간 token 평균이다.
            - window가 여럿이면 window 평균이다(D6). window로 나뉜 영상은 window별 특징도 저장한다. 설계를 바꾸지 않고, 평균으로 묻히는 정도를 나중에 확인하기 위해서다.
            - attentive probe는 쓰지 않는다.
        - 학습 목표(D9): block 10, 20, 30, 40을 이어 붙인 5,632차원. PCA를 쓰지 않는다.
    - DeBERTa-large(주 캡션 encoder, 3-3, 3-4, 3-4b, D7)
        - 모델은 DeBERTa-large다. DeBERTa-v3-large가 아니다. 체크포인트는 microsoft/deberta-large다(Horikawa, 2025 공개 코드).
        - 캡션은 MC 사람 캡션 원문 20개다. 정서어를 지우지 않은 판이 주다.
        - 캡션마다 층별로 token 임베딩을 평균한다. 특수 token은 뺀다.
        - 20개 캡션의 특징을 평균해 영상당 하나로 만든다.
        - 저장: 24개 층 모두(폭 1,024)의 영상 평균, 그리고 캡션별(문장별) 벡터
        - 학습 목표(D9): 층 6, 12, 18, 24를 이어 붙인 4,096차원. PCA를 쓰지 않는다.
        - 정서어 제거판(3-4, D8, SI): 부록 2의 정서어 181개를 지운 캡션으로 같은 절차를 한 번 더 한다.
    - baseline 시각 모델(3-1, 3-2). 층 분석과 ROI 분석은 하지 않는다.
        - VideoMAE
            - 공식 ViT-B/16 사전학습 전용 가중치. Kinetics로 미세조정한 가중치는 쓰지 않는다.
            - 16프레임만 받으므로 4초 window(초당 4장)으로 나눠 평균한다(O11).
            - block 3, 6, 9, 12의 token 평균을 이어 붙인다.
        - TimeSformer: Horikawa(2025) 공개 코드의 프레임 선택, 자르기, 층 추출을 우리의 반복 재현 영상에 적용한다(O14). 원 논문 전체의 재현이라고 쓰지 않는다.
            - 시간: 32프레임 간격으로 고른다. 위치가 8개 미만이면 영상 전체에서 8프레임을 고르게 뽑는다.
            - 공간: 224 × 224. 세 위치(왼쪽, 가운데, 오른쪽 또는 위, 가운데, 아래)에서 자른 결과의 특징을 평균한다.
            - 층마다 공간 평균을 내고, 세 위치와 시간에 걸쳐 평균한다(층 12개 × 768차원).
            - block 3, 6, 9, 12를 이어 붙인다.
            - 입력 영상만 참가자가 본 그대로(8초 반복 포함)다. 4초 window, 초당 2장 안은 쓰지 않는다.
            - 다른 모델의 가운데 자르기와 화면 범위가 다르다. 이 차이도 모델 차이에 포함해 해석한다.
        - CLIP 이미지 인코더
            - 판은 S1의 확인 결과를 따른다. 확인하지 못하면 OpenAI ViT-B/16이다.
            - 초당 4장으로 프레임마다 마지막 투영 이미지 벡터를 구한다.
            - L2 정규화 뒤 평균하고 다시 정규화한다.
    - MPNet(baseline 캡션 encoder, 3-3. 처리는 7-O 3절에서 정함)
        - 체크포인트는 sentence-transformers/all-mpnet-base-v2다.
        - 모델 카드의 처리를 그대로 쓴다. 마지막 층 token 임베딩을 attention mask로 평균하고 L2 정규화한다. 384 word piece를 넘는 글은 기본값대로 잘린다.
        - 캡션 20개를 각각 임베딩해 평균한다. 평균한 뒤 다시 정규화하지 않는다(3-4b).
        - 10월 캐시는 M2의 추출 기록이 이 처리와 맞을 때만 쓰고, 아니면 다시 뽑는다.
    - 저수준 Vision feature(3-6). 모두 6,558개
        - 움직임 에너지 6,555개(Du 외, 2023의 설정)
            - pymoten을 쓴다.
            - 프레임을 96 × 96화소로 만든다. 종횡비를 유지해 줄인 뒤 가운데를 자른다.
            - CIE L*a*b*로 바꾸고 L*만 남긴다.
            - 시공간 Gabor 필터 쌍: 공간 주파수 {0, 2, 4, 8, 16, 32}, 시간 주파수 {0, 2, 4} Hz, 방향 8개
            - pymoten 기본 설정에 이 주파수를 넣으면 정확히 6,555개다.
            - 초당 15장을 쓴다(공식 예제). 초당 15장보다 적은 영상의 처리는 O10이다.
            - 필터 출력으로 움직임 에너지를 계산하고 로그 변환한다. 영상의 시작과 끝 처리와 로그 변환 식은 O12다.
            - 영상 하나의 값: 참가자가 본 영상 전체에 필터를 이어서 적용하고, 로그 변환한 값을 시간에 걸쳐 평균한다.
            - 6,555개를 줄이지 않는다.
            - Du 외(2023)의 OSF 공개 특징을 받을 수 있으면 영상별로 맞춰 본다.
        - RGB 중앙값 3개(Jang & Kragel, 2025). 프레임과 화소 범위는 O13이다.
    - 간단한 화면 통계 33개(lowlevel_features.py)는 기록과 자료 점검에만 남긴다. 저수준 특징이나 기준선으로 쓰지 않는다(3-6).
- 출력
    - 모델별 특징 파일과 추출 manifest(M2)
    - 특징 파일 체크섬(M1)
    - 위치는 outputs/s3_features/<모델>/다(git 무시 대상). 파일 이름은 s3_collect.py의 머리말에 있다.
- 확인 기준
    - 차원: V-JEPA 2는 block마다 1,408, 목표 5,632다. DeBERTa는 층마다 1,024, 목표 4,096이다. 움직임 에너지는 6,555다.
    - 실제 캐시 차원을 기록 칸에 적는다. 5-4는 실제 캐시 차원을 확인 전이라고 적었다.
    - 영상 수가 2,196개이고 NaN이 없다.
    - 반복한 영상의 프레임 수가 상영 기록의 길이와 맞는다.
    - 추출 manifest에 M2의 항목이 모두 있다.
- 실행 주체: 석진 님 GPU. Claude Code는 추출 스크립트, job script, 실행 명령을 만든다(M4).
- 7-O 항목: O10(프레임 뽑기), O11(window와 프레임 수), O12(움직임 에너지의 시작과 끝), O13(RGB 중앙값), O14(TimeSformer 클립), O15(층 번호)
- SI(7-L의 추출 목록에 없다): V-JEPA 2의 4초 window(16프레임) 평균판(3-2). 보류한다(11/5 석진 님). 평균 문제의 해결책이 아니라 입력 시간 범위에 대한 보조 비교다. 짧은 영상도 32프레임 한 입력에서 16프레임 두 입력의 평균으로 바뀌므로, 하게 되면 전체 자료에 적용하는 별도 SI로 미리 정해서 한다. 주 결과를 본 뒤 결과에 따라 꺼내지 않는다.

### S4. 뇌 없는 분석

- 목적: Stimulus Model을 학습해 Brain → Emotion [distillation]에 쓸 fold 밖 출력과 경로 평가의 head(K1, K1a)를 만든다. 뇌 없이 두 특징의 겹침과 block의 성격을 확인한다.
- 근거: 5-3, E1~E4, E6, H3, H4, N3, N26, N43, D12, 3-4, D8, J3, 4-3, 6-2, K1, K1a, B4, G10, 7-L 실행 순서 4
- 입력: S3의 시각 목표(5,632차원)와 캡션 목표(4,096차원), 사람 평정 34개, 14개 차원 사람 평정(S5의 입력과 같은 파일), S2의 manifest
- 할 일
    - Stimulus Model Stimulus Model(E1, E2, E3, 5-3)
        - 입력은 v와 c다. 뇌는 받지 않는다. PCA를 쓰지 않는다.
        - 표준화: 모델마다 그 모델의 학습 자료로 맞춘다(N3, H4). 안쪽 모델은 안쪽 학습 자료로, 최종 모델과 K1 head는 D_k로 맞춘다.
        - 꼴: logit = a(v) + b(c) + U[(Av) ⊙ (Bc)]
            - a: 5,632 → 34 선형
            - b: 4,096 → 34 선형
            - A: r × 5,632, B: r × 4,096, U: 34 × r
            - 출력 = sigmoid(logit)
        - 랭크 r ∈ {0, 1, 2, 4, 8}. r = 0이면 마지막 항이 없는 더하기 모델이다.
        - 손실: 가중하지 않은 soft BCE(2-2). 34개 정서와 영상에 같은 가중치를 둔다.
        - learning rate ∈ {1e-4, 1e-3, 1e-2}, weight decay ∈ {1e-4, 1e-3, 1e-2}(E3). 후보는 rank와 합쳐 45개다
        - 학습과 선택은 O16이다. D_k 안의 안쪽 5겹으로 epoch 수, r, weight decay를 고른다(H3).
        - Feature Extractor는 고정이다. 결합부만 학습한다(5-3).
    - nested OOF 출력(E4, O16)
        - 바깥 fold k마다 H2의 학습 fold 4개(D_k에서 검증 fold를 뺀 것) 안의 안쪽 4겹으로 만든다. 후보와 epoch 수도 이 4겹 안에서 O16의 절차로 고른다.
        - 안쪽 fold j의 출력은 나머지 3개 안쪽 fold로 학습한, 고른 후보의 Stimulus Model이 낸다.
        - H2의 검증 fold는 Stimulus Model의 학습, 설정 선택, 조기 종료에 쓰지 않는다(11/3 사용자, 기록 칸 정할 것 2).
        - 6-3의 두 조건은 Stimulus 예측 평정을 쓰지 않으므로 6-3 전용 출력은 만들지 않는다(11/6 석진 님).
        - 영상 단위로 만든다.
        - 바깥 시험 fold의 영상을 쓰지 않는다.
        - 출력은 0~1로 자른다. 자르기 전 값과 자른 값을 모두 저장한다.
        - 이 출력이 Brain → Emotion [distillation]과 Brain + Decoded Feature → Emotion [distillation]의 Stimulus 예측 평정 t다(5-2). Brain Model에게는 학습 영상마다 이 34개 값만 준다.
    - 바깥 시험 fold의 Stimulus Model 성능
        - 고른 후보로 D_k 전체에서 다시 학습한 모델로 낸다(O16).
        - 사전 분석으로만 보고한다(E6, N43). 뇌에 대한 결론으로 쓰지 않는다.
        - 더하기(r = 0) 대 상호작용 결과도 사전 분석이다.
        - r = 0이 뽑힌 fold는 G10과 같은 규칙으로 보고한다. 상호작용 해석은 r > 0이 뽑힌 fold로 한정한다(N26).
    - 경로 평가(K1)의 head(O17)
        - D_k 전체로 학습한 Stimulus Model 두 개를 저장한다. 더하기판(r = 0)과 상호작용판(r ∈ {1, 2, 4, 8})이다.
        - 두 head는 Vision feature와 Caption feature를 함께 받는 하나의 Stimulus Model이다. 시각만, 캡션만 받는 head는 만들지 않는다(K1).
    - 경로 평가의 14개 차원판(K1a, 보조)에 쓰는 Stimulus Model
        - 입력과 그 표준화는 Stimulus Model와 같다(N3, H4, D9). decoded features를 같은 좌표로 넣기 위해서다.
        - 꼴: 출력 = a(v) + b(c) + U[(Av) ⊙ (Bc)]
            - a: 5,632 → 14 선형
            - b: 4,096 → 14 선형
            - A: r × 5,632, B: r × 4,096, U: 14 × r
            - sigmoid를 쓰지 않고 연속값을 낸다.
        - 판은 O17과 같게 나눈다. 더하기판(r = 0)과 상호작용판(r ∈ {1, 2, 4, 8})을 둘 다 학습한다.
        - 손실: MSE. 14개 차원과 영상에 같은 가중치를 둔다.
        - 사람 평정: 입력처럼 모델마다 그 학습 자료로 표준화한다(N3). 최종 모델의 통계를 저장해 되돌린다(S9, S10).
        - AdamW, batch 64, 최대 300 epoch, learning rate와 weight decay는 Stimulus Model와 같은 후보(O16, E3)
        - 학습과 선택은 Stimulus Model와 같은 절차다(H3, O16, O17, 기록 칸 정할 것 10). D_k의 run fold 5개를 안쪽 5겹으로 쓴다.
            - 후보마다 안쪽 검증 MSE의 5겹 평균 곡선이 가장 낮은 epoch를 그 후보의 epoch 수로 정한다.
            - 그 epoch에서 안쪽 검증의 14개 차원 Pearson r 평균을 5겹 평균해 판마다 가장 큰 후보를 고른다.
            - 고른 후보와 epoch 수로 D_k 전체에서 다시 학습한다.
        - 14개 차원에는 뇌 모델을 학습하지 않는다(B4).
    - 긴 영상의 window 사이 변화량(3-2)
        - window로 나뉜 개발 영상마다, 개발 영상으로 표준화한 좌표의 block 10, 20, 30, 40에서 window 쌍의 cosine distance 평균과, 그 영상 평균 feature와 다른 개발 영상 500개(seed 20261106) 사이 cosine distance의 중앙값을 낸다. 뇌와 정서를 쓰지 않는다. 점검용 설계 선택이다. window끼리의 차이가 영상끼리의 차이에 비해 어느 정도인지만 말하고, 정보 손실량이나 정서 예측에 중요한 정보가 사라졌는지로 읽지 않는다(11/6 석진 님).
        - 결과로 평균 규칙을 바꾸지 않는다.
    - 겹침과 block의 성격(D12, O22)
        - V-JEPA 2의 40개 block 각각(1,408차원)으로 두 목표를 얼마나 예측하는지 ridge 교차 R²로 낸다.
            - 캡션 목표(DeBERTa 네 층, 4,096차원)
            - 저수준 Vision feature(6,558개)
        - 뇌와 정서를 쓰지 않는다.
        - 결과는 block의 성격을 자료로 보이는 데 쓴다(3-2). 두 특징을 독립된 정보원으로 해석하지 않는 근거로도 쓴다(5-0).
        - 그 결과로 목표 block을 다시 고르지 않는다.
    - 정서어 제거판(3-4, D8, SI, O22)
        - DeBERTa Caption feature로 정서를 예측하는 ridge를 원 캡션과 정서어 제거 캡션에서 낸다. 사전 분석의 MPNet 값은 원 캡션 0.605, 정서어 181개를 지운 캡션 0.604였다(부록 2).
        - 정서어 제거 Caption feature로 Stimulus Model도 만든다(D8).
    - 내용 구역 제외(4-3, J3, 6-2)
        - 구역 제외 학습과 학습량 대조 학습(S2의 표본)마다 표준화와 보조 Stimulus Model을 그 학습 자료로 다시 만든다.
        - 빠진 구역은 쓰지 않는다.
        - Stimulus Model은 6-2의 보조 모델이다. 구역 시험 영상에서 평가한다.
        - 6-2의 두 조건(Brain → Emotion, Brain + Decoded Feature → Emotion)은 Stimulus 예측 평정과 frozen head를 쓰지 않는다(4-3). 그래서 구역 제외 학습의 nested OOF 출력과 K1 head는 만들지 않는다.
- 출력
    - fold마다 Stimulus Model(체크포인트, 고른 epoch 수, r, weight decay)
    - nested OOF 출력(자르기 전 값, 자른 값)
    - 시험 fold 예측
    - K1 head 두 개
    - K1a Stimulus Model 두 개와 사람 평정 표준화 통계, fold마다 고른 epoch 수, r, weight decay
    - D12 표, 정서어 제거판 결과
    - 위치는 project/output/ 아래(M3)
- 확인 기준
    - OOF 출력의 영상 ID가 D_k에만 있다.
    - 각 OOF 출력이 그 영상을 학습에 쓰지 않은 모델에서 나왔다.
    - 표준화 통계(14개 차원 사람 평정 포함)에 시험 fold와 MC 72개가 들어가지 않았다.
    - fold마다 고른 epoch 수, r, weight decay의 표가 있다.
    - K1a Stimulus Model의 입력 좌표가 K1 head와 같다.
- 실행 주체: Claude Code가 스크립트와 job script를 만든다. GPU가 필요하면 석진 님이 실행한다(M4).
- 7-O 항목: O16(Stimulus Model의 학습과 선택), O17(K1 head), O18(ridge λ), O22(뇌 없는 ridge의 분할)

### S5. ridge

- 목적: 뇌에서 Vision feature와 Caption feature를 층별로 얼마나 decoding할 수 있는지 본다(2-1). 정서 기준선을 낸다(I7).
- 근거: 2-1, 2-2, 3-2, 3-3, H3, N5, N15, N16, N21, I7, I10, B4, 2-0 (나), C1, C5, 6-1의 0행과 2-1행, 6-2, 7-L 실행 순서 5
- 입력: 참가자별 voxel 반응, S2의 manifest와 공통 ROI, S3의 특징, 사람 평정 34개, 14개 차원 사람 평정(data/cowen_horikawa_labels.csv의 *_score 열 14개, content_id로 붙임, 기록 칸 S0)
- 공통
    - 영상당 반응은 v3_qc의 블록 평균이다. 신호를 4초 밀어 영상 제시 구간과 뒤따르는 2초 휴지로 된 블록 안에서 평균하고(Horikawa 외(2020)의 구간), run 안에서 voxel마다 z-score했다(C1).
    - 입력은 뇌 모델과 같은 voxel이다. 공통 ROI 안의 voxel을 모두 쓰고, ROI가 겹치는 voxel은 한 번만 쓴다(I10). 참가자당 125,496~149,080개다.
    - 학습 자료의 encoding 성능으로 voxel을 고르지 않는다(3-2).
    - 표준화: voxel은 참가자별로, 특징 목표는 차원마다 그 모델의 실제 학습 자료로 맞춘다(C5, D9, N3). 안쪽 5겹은 안쪽 학습 자료, 최종 모델은 D_k, 주 비교판은 H2의 학습 fold 4개다.
    - 참가자마다 따로 학습한다(2-0의 (나)).
    - 정서 ridge의 손실은 제곱 오차다(2-2). 사람 평정은 비율 그대로 쓰고 z-score하지 않는다(B3).
    - λ 후보와 선택 지표는 O18이다. 모든 ridge에 같은 λ 후보를 쓴다. Horikawa 외(2020)의 복셀 선택 ridge만 그 공개 코드의 후보를 쓴다.
    - 같은 뇌 입력을 한 번 분해하면 목표가 늘어도 행렬 곱만 는다(3-2). 실제 실행 시간을 기록한다.
- 할 일
    - 층별 feature decoding(3-2, 3-3, H3)
        - 목표: V-JEPA 2의 40개 block 각각(1,408차원), DeBERTa의 24개 층 각각(1,024차원)
        - 층마다 ridge decoder를 따로 둔다.
        - 정칙화 강도는 층, 모델, 참가자마다 D_k 안의 안쪽 5겹으로 고른다(Horikawa, 2025의 방식). 기준은 안쪽 검증의 차원별 r 평균이다(O18).
        - 고른 값으로 D_k 전체에서 학습해 시험 fold를 예측한다.
        - 평가(N5, 6-1의 2-1행): 시험 영상에서 차원별 r의 평균(O20의 좌표), 같은 fold 안 영상 식별(O19), 순열 기준(O4)
        - 결과는 보고만 한다. 그 결과로 Brain Model의 목표 층을 다시 고르지 않는다.
    - 주 목표의 ridge decoded features(O21)
        - 층별 ridge의 block 10, 20, 30, 40 출력과 DeBERTa 층 6, 12, 18, 24 출력을 이어 붙인다.
        - 6-1의 [사전 2] 검정과 K1의 ridge판에 쓴다. [사전 2]의 검정 통계량은 차원별 r 평균이다(O19).
        - 바깥 시험 fold의 decoded features를 저장한다.
        - 안쪽 5겹의 fold 밖 decoded features도 저장한다. N8의 ridge 보정 통계에 쓴다(O34).
    - 정서 기준선(I7). 평가는 2-3의 방식이다(S10). 기준선은 통과 조건이 아니다(6-1).
        - 평균 예측: 학습 fold의 정서별 평균이다. 예측이 상수라 r을 낼 수 없다. 오차 지표(2-4, O25)의 기준선으로만 쓴다.
        - 영상 길이 기준선(O23): 원래 영상 길이의 자연로그 하나로 정서마다 ridge
        - 저수준 Vision feature(6,558개)만으로 정서를 예측하는 기준선
        - 뇌 전체 평균과 block 신호 크기의 기준선. 정의는 0단계 기록을 따른다[레포에서 확인].
        - 정서 ridge(voxel 입력, 정서마다 따로, O18)
            - 주 비교판은 뇌 모델과 같은 규칙이다(N15). H2의 검증 fold 하나로 고르고, 남은 4개 fold로 학습한 모델을 그대로 시험한다.
            - 안쪽 5겹판은 문헌 비교용이다.
        - soft BCE 선형(N16, O24): 같은 입력, sigmoid, soft BCE. 설정 선택과 조기 종료는 공통 검증 기준이다.
        - Horikawa 외(2020)의 복셀 선택 ridge: S1에서 규칙을 확인했다(I7). 코드는 s5_baselines.py의 h2020이다.
        - 외부 baseline 셋은 S6과 S8에서 한다.
    - 길이 지름길(N21, O25): 기준선 비교와 함께 길이를 통제한 편상관을 보조로 낸다.
    - 내용 구역 제외(6-2, I10): 정서 ridge(주 비교판)를 구역 제외 학습과 학습량 대조 학습에서 다시 학습한다. 구역 시험 영상에서 평가한다. 보조 모델이다.
    - 14개 정서 차원(B4, 보조, 부록에 보고)
        - 목표는 1~9점 평정의 평균 14개다. 모두 같은 지위로 다루고 미리 골라 둔 차원은 없다.
        - 정서 ridge와 같은 절차다. 분할, 표준화, 시험 fold 사용 금지(H5), MC 72개와 그 중복 영상 제외가 모두 같고, 사람 평정은 값 그대로 쓴다.
        - 주 비교판(N15): 참가자와 차원마다 H2 검증 fold의 그 차원 r로 λ를 고르고, 남은 4개 fold로 학습한 모델을 그대로 시험한다(O18).
        - 안쪽 5겹판(H3): 문헌 비교용이다(O18).
        - 14개 차원으로 뇌 모델을 학습하지 않고 교체 분석도 하지 않는다.
- 출력
    - 참가자, 층, fold마다 고른 정칙화 값과 양 끝이 뽑힌 횟수
    - 시험 decoded features와 안쪽 fold 밖 decoded features
    - 층별 지표 표
    - 기준선의 시험 예측
    - 14개 차원 ridge의 시험 예측과 고른 λ
    - 위치는 project/output/ 아래(M3)
- 확인 기준
    - 정칙화 선택에 시험 fold를 쓰지 않았다(H5).
    - 64개 층(40 + 24) × 5명의 결과가 모두 있다.
    - 정서 ridge의 주 비교판과 뇌 모델이 같은 검증 fold를 쓴다.
    - 14개 차원 × 5명 × 6 fold의 ridge 결과가 두 판 모두 있다.
- 실행 주체: Claude Code가 스크립트와 job script를 만든다. 석진 님이 실행한다(M4). 계산 노드 없이 돌릴 수 있는 가벼운 계산인지는 레포 CLAUDE.md를 따른다.
- 7-O 항목: O18(λ 후보와 선택 지표), O19([사전 2] 통계량과 영상 식별), O20(fold를 모을 때의 좌표), O21(주 목표 ridge), O23(영상 길이 기준선), O24(soft BCE 선형), O25(오차 감소와 길이 편상관)

### S6. 뇌 모델 구현

- 목적: A~C 묶음 다섯 조건, 더하기 head, 대조군, E-고정과 E-학습(G16), 평균 pooling판, 외부 baseline을 같은 자료 경계에서 돌릴 수 있게 구현한다. 입력, 출력, loss는 01 5-A를 따른다.
- 근거: 2-0 (가), 2-1, 2-2, 5-0, 5-2, 5-4, 5-5, 5-6, C4, C5, F3~F8, G1~G16, N4, N24, H2, M1
- 입력: S2의 manifest, S3의 목표, S4의 nested OOF 출력, voxel 반응
- 할 일
    - 입력층(5-5, C4)
        - t(s, r) = W(s, r) x(s, r) + b(s, r) + e(r)
            - x(s, r): 참가자 s의 ROI r 안 voxel 값. C5로 표준화한 값이다.
            - W(s, r): 그 voxel 수 → d의 선형층. 참가자와 ROI마다 따로 둔다.
            - b(s, r): d차원 편향
            - e(r): ROI embedding. 참가자 공통이다.
        - ROI token은 그 ROI의 voxel만으로 만든다. ROI 수는 S1의 공통 ROI 수다.
        - 입력층 weight decay는 d와 함께 고른다(H2, 5-5).
        - 칸 평균(ROI pooling)은 쓰지 않는다.
    - encoder(F3, O26)
        - self-attention block 1개, pre-LN, head 4, FFN d → 2d → d(GELU), dropout 0.1
        - 마지막에 LayerNorm 하나를 더 둔 출력을 H로 쓴다(O26).
        - d는 4의 배수다.
    - feature head(F5, O26)
        - 학습하는 query 2개(시각, 캡션)가 H를 교차 주의 1층(head 4)으로 읽는다. 층의 세부는 O26이다.
        - query마다 자기 선형층으로 목표를 낸다. v̂: d → 5,632, ĉ: d → 4,096
    - emotion query(F4, O26)
        - 학습하는 query 34개가 H를 교차 주의 1층(head 4)으로 읽는다.
        - 정서마다 선형층(d → 1)으로 logit g(H)를 낸다.
        - query끼리 self-attention은 두지 않는다.
        - emotion query는 ROI token만 읽는다. decoded features는 emotion query가 읽지 않고, 따로 둔 경로로 예측 평정에 더해진다(2-1, 5-4).
    - emotion head(5-4, G4)
        - Brain → Emotion, Brain → Emotion [distillation], Brain → Emotion + Vision + Caption: z = g(H)
        - Brain + Decoded Feature → Emotion의 상호작용 head(기본): z = g(H) + a(v̂) + b(ĉ) + U[(Av̂) ⊙ (Bĉ)]
            - a(v̂), b(ĉ)는 편향이 있는 선형층이다. a: 5,632 → 34, b: 4,096 → 34. 더하기 head와 상호작용 head에서 같다(O5).
            - A: r × 5,632, B: r × 4,096, U: 34 × r. r ∈ {1, 2, 4, 8}. 편향 없는 선형이다(O5).
        - Brain + Decoded Feature → Emotion의 더하기 head(1-2의 비교 조건): 마지막 항을 뺀다.
        - 출력 p = sigmoid(z). 경로별 점수를 더한 뒤에는 sigmoid만 둔다.
        - 두 decoded feature 경로를 합친 attention이나 공통 MLP를 더하기 앞에 두지 않는다.
        - 이전 F6(decoded features를 token으로 만들어 ROI token과 함께 읽음)은 쓰지 않는다.
        - Stimulus Model의 가중치를 공유하거나 복사하지 않는다(5-4).
    - stop-gradient(G8, 5-0)
        - Brain + Decoded Feature → Emotion과 Brain + Decoded Feature → Emotion [distillation]에서 v̂, ĉ가 a(v̂), b(ĉ), 상호작용 항으로 들어가기 전에 기울기를 끊는다.
        - 값은 그대로 전달된다. 막는 것은 기울기다.
        - 그래서 feature head는 feature decoding loss로만 학습된다.
        - 공유 encoder와 입력층은 g(H)를 거쳐 정서 손실도 받는다.
        - 기울기를 흘리는 판은 만들지 않는다. 그 판은 후속이다(5-0).
    - A~C 묶음 다섯 조건(5-0, G1~G5)
        - Brain → Emotion: 손실 = soft BCE(p, y). feature head가 없다.
        - Brain → Emotion [distillation]: 손실 = soft BCE(p, (1 − α) y + α t). t는 S4의 nested OOF 출력이다. emotion head는 Brain → Emotion과 같다. feature head가 없다.
        - Brain → Emotion + Vision + Caption: 손실 = soft BCE(p, y) + λ × L_feat. emotion head는 Brain → Emotion과 같다(z = g(H)).
        - Brain + Decoded Feature → Emotion: 손실은 Brain → Emotion + Vision + Caption과 같다. emotion head만 Brain + Decoded Feature → Emotion의 꼴이다.
        - Brain + Decoded Feature → Emotion [distillation]: 손실 = soft BCE(p, (1 − α) y + α t) + λ × L_feat. emotion head는 Brain + Decoded Feature → Emotion의 꼴이다.
    - 손실(G7, N4, 2-2)
        - soft BCE = −[y log p + (1 − y) log(1 − p)]
        - 34개 정서와 행에 같은 가중치를 둔다. 평정자 수로 가중하지 않는다.
        - L_feat = (MSE(v̂, v) + MSE(ĉ, c)) / 2. MSE는 차원 평균이다.
        - v, c는 차원마다 H2의 학습 fold 4개로 표준화한 값이다(D9, N3). 통계를 저장한다. K1에 넣을 때는 원래 척도로 되돌린 뒤 K1 head의 D_k 눈금으로 바꾼다.
        - λ는 시각과 캡션에 하나로 공유한다(G9).
    - 후보값(G9)
        - learning rate: 모든 조건에서 {1e-4, 1e-3, 1e-2}를 후보에 넣는다(G13, 11/7 석진 님). 아래 후보 수에 곱해진다
        - Brain → Emotion: d와 입력층 weight decay의 조합 K개(S7에서 정함)
        - Brain → Emotion [distillation]: α ∈ {0, 0.25, 0.5}. α = 0은 Brain → Emotion과 같으므로 0.25와 0.5만 새로 학습한다.
        - Brain → Emotion + Vision + Caption: λ ∈ {0, 0.1, 1.0}. λ = 0은 Brain → Emotion과 같으므로 0.1과 1.0만 새로 학습한다.
        - Brain + Decoded Feature → Emotion(상호작용 head): λ ∈ {0.1, 1.0} × r ∈ {1, 2, 4, 8}, 8개. λ = 0은 없다(G9: stop-gradient 때문에 λ = 0이면 feature head가 실제 Vision feature와 Caption feature를 맞히도록 학습되지 않는다).
        - Brain + Decoded Feature → Emotion(더하기 head): λ ∈ {0.1, 1.0}, 2개
        - Brain + Decoded Feature → Emotion [distillation]: Brain + Decoded Feature → Emotion에서 고른 λ와 r을 고정한다. α ∈ {0, 0.25, 0.5}이고 0.25와 0.5만 새로 학습한다.
        - 고른 d와 입력층 weight decay는 그 바깥 fold의 모든 내부 조건에 같이 쓴다(5-5).
        - 0.1과 1.0은 문헌이 보장한 최적값이 아니라 시험 전에 고정한 탐색 후보다(G9).
    - 설정 선택과 조기 종료: 모든 조건에서 공통 검증 기준(0-2)과 O6을 따른다.
    - 최적화(G13)
        - AdamW, learning rate는 후보에서 고름, weight decay는 01 G13의 묶음을 따름, batch 64, 최대 300 epoch, warmup 없음(O26)
        - 조기 종료: 검증 자료의 정서 soft BCE, patience 30. 가장 낮았던 epoch의 가중치로 되돌린다(O6).
        - S7에서 fold 1의 안쪽 검증 자료로 수렴만 확인한다. 값을 고르지 않는다. 수렴하지 않으면 혼자 바꾸지 않고 측정값과 함께 보고한다.
    - 배치(2-0, G15)
        - 한 행은 참가자 한 명의 영상 하나다.
        - 5명의 행을 섞어 배치를 만든다.
        - 사람 평정은 영상마다 하나이고 5명 행에 같다.
    - seed는 0, 1, 2다(G14, L9). 재현성 설정은 O32다.
    - 대조군(G6, G11, G12). 평균 계산과 섞기는 그 학습 분할 안에서만 한다.
        - label smoothing(G11)
            - Brain → Emotion [distillation]과 같은 구조에서 t 대신 학습 자료의 정서별 평균 비율 ȳ를 쓴다.
            - 목표 = (1 − α) y + α ȳ. α ∈ {0.25, 0.5}
        - Stimulus Model 출력 섞기(G6, G12): Brain → Emotion [distillation]에 적용한다. 학습 영상 사이에 t를 바꿔 준다. α ∈ {0.25, 0.5}
        - Vision feature와 Caption feature 짝 섞기(G6, G12): Brain → Emotion + Vision + Caption에 적용한다. 학습 영상 사이에 (v, c) 목표를 같은 순열로 바꾼다. 시각과 캡션은 같은 영상의 짝을 유지한다. λ ∈ {0.1, 1.0}
        - 순열의 규칙(O1)
            - 바깥 fold와 seed마다 학습 영상(H2의 학습 fold 4개) 안에서 영상 단위 순열 하나를 만들어 모든 epoch에 유지한다.
            - 같은 fold와 seed에서는 설정 후보(α, λ)가 달라도 같은 순열을 쓴다.
            - 자기 영상으로 다시 배정되는 경우는 없게 한다.
            - 시각과 캡션은 같은 영상의 짝을 유지한 채 함께 옮긴다(G12).
            - 같은 영상의 5명 행은 같은 섞인 목표를 받는다.
            - 검증 자료와 시험 자료는 섞지 않는다.
            - Stimulus Model 출력 섞기에도 같은 규칙을 쓴다.
            - 순열과 그 seed를 저장한다(M1).
    - E-학습은 E-고정과 같고, Multimodal Model의 head를 복사해 초기값으로 쓴 뒤 encoder와 함께 학습한다. Multimodal Model 원본은 고정한다.
    - E-고정(G16, frozen-head distillation). 보조 성능 비교다. 기본 run 분할에서만 한다.
        - Multimodal Model과 Brain Model의 구조, 후보, seed(O5)
            - Multimodal Model: 뇌 모델과 같은 입력층, encoder(F3), emotion query(F4)를 쓴다. 실제 Vision feature와 Caption feature를 각각 선형층으로 d차원 token으로 바꿔 ROI token과 함께 encoder에 넣는다. 중간 표현은 emotion query 34개의 출력(34 × d, O26의 LayerNorm 뒤)이고, head는 정서별 선형층(d → 1)과 sigmoid다.
            - Multimodal Model 후보: d와 입력층 weight decay는 그 바깥 fold의 Brain → Emotion이 고른 값이다. 두 특징 선형층의 weight decay ∈ {1e-4, 1e-3, 1e-2}와 learning rate(G13)를 공통 검증 기준으로 고른다.
            - Brain Model: Brain → Emotion과 같은 뇌 모델(같은 d)이다. 연결층은 두지 않는다.
            - seed: Multimodal Model을 seed 0으로 고르고 seed 1, 2를 더 학습한다. Brain Model seed s는 같은 seed s의 Multimodal Model과 짝짓는다.
            - token으로 넣는 결합과 연결층 생략은 이번 비교에서 고른 설계 선택이다. 그래야만 한다는 뜻이 아니다(O5).
            - Multimodal Model의 섞는 구조는 Brain + Decoded Feature → Emotion의 분리된 경로와 더하기 구조에 적용하지 않는다(O5).
        - Brain Model 손실 = soft BCE(head_T(o_S), y) + λ × MSE(s(o_S), s(o_T))
            - 고정 head에는 Brain Model 표현 o_S를 Multimodal Model이 학습할 때의 좌표 그대로 넣는다.
            - s는 MSE 계산에만 쓰는 표준화다. Multimodal Model 표현의 차원별 평균과 표준편차로 나누며, 통계는 Multimodal Model이 학습한 4개 fold의 행에서 낸다.
            - λ ∈ {0.1, 1.0}(G9). 0은 없다.
            - Multimodal Model과 head의 가중치는 고정한다. 정서 손실은 고정된 head를 거쳐 Brain Model까지 전달된다. Brain + Decoded Feature → Emotion의 stop-gradient와 다르다.
            - Multimodal Model의 정서 출력을 따라 하는 손실은 넣지 않는다.
        - 자료 경계
            - Multimodal Model과 Brain Model 모두 같은 학습 fold 4개로 가중치를 학습한다.
            - 검증 fold는 설정 선택과 조기 종료에만 쓴다. 시험 fold는 평가에만 쓴다.
            - Multimodal Model을 5개 fold 전체로 학습하지 않는다. 고정된 head가 검증 영상의 사람 평정을 이미 보게 되기 때문이다.
            - 한 학습 실행에서 Multimodal Model 하나를 고정해 그 표현만 목표로 쓴다. 서로 다른 Multimodal Model의 표현을 섞지 않는다.
        - 뇌 표현 복사 대조는 넣지 않는다.
        - Multimodal Model의 시험 성능은 참고로만 보고한다.
        - 비교 대상은 Brain → Emotion, Brain + Decoded Feature → Emotion, E-고정, E-학습이다. 시험 입력은 모두 뇌뿐이다.
        - 내용 구역 제외, MC, 네트워크 분석, 대조군으로 넓히지 않는다.
    - 평균 pooling판(F7, 보조와 SI, O31)
        - Brain → Emotion: ROI token 평균 → 선형 34개
        - Brain + Decoded Feature → Emotion: ROI 경로만 ROI token 평균 → 선형 34개로 바꾼다. 두 decoded feature 경로와 feature head는 그대로다.
        - 설정은 그 바깥 fold의 표준 실행에서 고른 값을 그대로 쓴다(O31).
    - 외부 baseline 셋(5-2, O27, O28)
        - 공통
            - 과제만 우리 것으로 맞춘다: run 묶음 분할, 34개 연속 사람 평정, 우리 평가 지표
            - 나머지는 원 논문과 공개 코드 그대로 둔다: 모델 구조, 입력 전처리, 손실, 정서 관계 그래프 기준(0.1), 구조의 크기, 참가자별 학습
            - 34개 가운데 그들의 27개에 없는 7개(contempt, disappointment, envy, guilt, pride, sympathy, triumph)도 함께 학습한다.
            - 원 논문이 탐색한 하이퍼파라미터는 H2의 검증 fold에서 공통 검증 기준으로 고른다(O27).
            - 원 논문에서 바꾼 항목을 SI용으로 모두 기록한다.
        - GED(Huang 외, 2022. github.com/zhongyu1998/GED)
            - 입력은 원래의 370개 영역이다.
            - 레포의 run_baselines.py와 third_party/GED를 370개 지도로 다시 돌린다.
            - 공개 코드는 사람 평정을 정서마다 전체 자극의 최소~최대로 정규화한다(utils.py의 load_data, 시험 자극 포함).
            - 최소와 최대를 바깥 학습 fold에서만 구하고, 평가 때 원래 비율로 되돌린다. 학습 fold의 최소~최대 밖은 예측하지 못한다.
            - 정서 관계 그래프도 바깥 학습 fold의 사람 평정으로만 만든다.
            - MSE 손실은 그대로 둔다.
        - ML-BVAE(Fu 외, 2022. github.com/KaichengFu1997/ML-BVAE)
            - 입력은 HCP360 피질 360개의 칸 평균이다.
            - 칸 수는 참가자마다 {8, 27, 64, 125, 216, 343} 가운데 H2의 검증 fold에서 공통 검증 기준으로 고른다.
            - 비용 때문에 후보를 줄이는 기준은 O28이다.
            - asymmetric focal loss는 soft BCE로 바꾼다.
            - λ1/λ2는 같은 방식으로 고른다.
        - EmoGrowth(Fu 외, 2025. github.com/ChangdeDu/EmoGrowth)
            - 입력은 HCP360 360개 × 8칸이다.
            - 가져오는 것: 정서 관계 그래프와 graph autoencoder의 정서 embedding, 정서별 특징 분리(semantic-guided feature decoupling), 정서별 분류기, 그래프 복원 손실
            - 빼는 것: 증분 학습 절차(라벨 모호성 해소, 이전 단계 모델 teacher), RKD
            - BCE는 그대로 둔다. λ3 등은 같은 방식으로 고른다.
    - 학습 가중치 수(F8): 조건마다 학습 가중치 수를 표로 낸다. 입력층(참가자당 약 d × 사용 voxel 수)을 따로 적는다.
    - 저장(M1)
        - config, git commit, 특징 파일 체크섬, split manifest, 체크포인트
        - 안쪽 선택 기록: d, 입력층 weight decay, 특징 선형층 weight decay, λ, α, r, learning rate, epoch
        - 시험 예측: sigmoid 전 logit과 확률
        - decoded features(시험 fold와 H2 검증 fold 모두. N8의 보정 통계에 검증 fold 값을 쓴다)
        - emotion query와 feature query의 attention 값
        - Brain + Decoded Feature → Emotion과 Brain → Emotion + Vision + Caption은 학습 영상과 검증 영상의 decoding 정확도도 기록한다(5-0의 남는 주의).
        - 후보별 시험 예측을 저장하고, 시험 성능은 S10에서 계산해 민감도 표에만 쓴다. 선택에는 쓰지 않는다(N24).
- 출력: 모델 코드, 조건별 설정 파일, 단위 시험, 학습 가중치 수 표
- 확인 기준(단위 시험으로 만든다)
    - 더하기 head에서 ROI token을 고정하고 v̂, ĉ만 바꾸면 결합 지표 I가 수치 오차 안에서 0이다.
    - Brain + Decoded Feature → Emotion에서 정서 손실만 역전파하면 feature head 가중치의 기울기가 0이다.
    - Brain → Emotion과 Brain → Emotion [distillation] 모델에 feature head가 없다.
    - 시험 때 forward가 뇌 반응만 받는다.
    - Stimulus 예측 평정 t가 학습 영상에만 붙는다.
    - E-고정의 Multimodal Model과 그 head는 Brain Model 학습 중 바뀌지 않는다. 정서 손실의 기울기는 Brain Model에 도달한다.
    - 표준화 통계와 섞기에 시험 fold와 MC 72개가 들어가지 않는다.
    - 설정 선택과 조기 종료가 모든 조건에서 실제 y로 계산된다.
- 실행 주체: Claude Code(구현과 단위 시험). GPU 실행은 S7과 S8에서 석진 님이 한다.
- 7-O 항목: O1(섞기 순열), O5(a(v̂), b(ĉ)와 E-고정, E-학습 구조), O6(공통 검증 기준의 세부), O26(교차 주의 층), O27(외부 baseline 검증), O28(ML-BVAE 칸 수), O31(평균 pooling판), O32(재현성)

### S7. 파일럿과 실행 사양 동결

- 목적: 본 실행 전에 실행 시간과 메모리를 측정한다. d와 입력층 weight decay의 후보를 정한다. 실행 사양을 동결한다.
- 근거: N34, 5-5, 5-4, G13, 7-L, L9, M5, 5-2(ML-BVAE 칸 수), 6-1, 7-L 실행 순서 6
- 입력: S6의 구현, S1의 voxel 수, 바깥 fold 1의 학습 자료(안쪽 자료). 시험 fold 1은 쓰지 않는다.
- 할 일
    - 파일럿(N34)
        - fold 1의 안쪽 자료만 쓴다. 파일럿 fold는 노출로 기록한다.
        - 학습 한 번의 실행 시간, GPU 메모리, epoch 수를 측정한다. 대상은 A~C 묶음 다섯 조건, 더하기 head, 대조군, Multimodal Model, E-고정과 E-학습, 외부 baseline 셋, 평균 pooling판이다.
        - G13의 값으로 수렴하는지 fold 1의 안쪽 검증 자료로만 확인한다. 값을 고르지 않는다. 그 자료는 다른 fold의 시험 영상이다.
        - learning rate 후보를 모든 조건에 넣을 때의 실행 시간을 측정한다(G13). 실행 예산을 넘으면 Brain → Emotion에서 고른 값을 다른 조건이 따르는 판으로 줄이고 본 실행 전에 확정한다. 성능을 보지 않는다.
        - 파일럿 뒤 구조를 바꿔야 하면 바꾸지 않고 보고한다(0-2). 바뀌면 그 사실을 기록한다(N34).
    - d와 입력층 weight decay의 후보(5-5). 5-5가 Claude Code에게 맡긴 결정이다.
        - 실제 mask로 ROI별 voxel 수, 입력층 가중치 수(참가자당 약 d × 사용 voxel 수), 메모리, 실행 비용을 계산한다.
        - 성능을 보기 전에 범위를 정한다. 파일럿의 검증 성능을 근거로 쓰지 않는다.
        - d는 4의 배수다(F3).
        - 후보는 적게 둔다(Cawley & Talbot, 2010).
        - 64로 고정하지 않는다. 64는 F3의 출처(GPT 10/30안)이고 근거가 없었다.
        - 범위를 "계산 예산에 따른 설계 선택"으로 기록한다. 조합 수가 K다.
    - ML-BVAE 칸 수 후보: 비용 때문에 줄이면 O28의 순서로 이때 범위를 고정한다. 원 논문에서 바꾼 점으로 기록한다(5-2).
    - 실행량 재계산: 7-L의 식에 정한 K와 측정한 실행 시간을 넣는다(아래 표).
    - 외부 baseline은 7-L 표에 학습 횟수가 없다. 측정한 실행 시간으로 따로 적는다.
    - 실행 사양 동결 커밋(M5)
        - 넣을 것: K와 후보값, G13 확인 결과, ML-BVAE 칸 수 범위, 실행량과 예상 GPU 시간, 기록 칸에서 통합문서로 정한 항목
        - 7-O의 O1~O5는 확정됨(11/3 사용자). 통합문서 7-O가 이 커밋에 들어간다.
        - commit 해시를 기록 칸에 적는다. 이 해시는 논문 방법 절에 들어간다.

| 묶음 | 학습 횟수 | 7-L의 계산(K = 6이면) |
| --- | --- | --- |
| 사다리(A~C 묶음 다섯 조건과 더하기 head) | 18K + 360 | learning rate 후보 3개를 포함한 값(G13). fold마다 Brain → Emotion 3K + 2, Brain → Emotion + Vision + Caption 8, Brain + Decoded Feature → Emotion(상호작용 head) 26, Brain + Decoded Feature → Emotion(더하기 head) 8, Brain → Emotion [distillation] 8, Brain + Decoded Feature → Emotion [distillation] 8. 각각 후보 수 + seed 2(L9). 468회 |
| 필수 대조군(G6) | 144 | 셋 × fold마다 8(후보 2 × learning rate 3 + seed 2) × 6 fold |
| 처음 보는 장면(6-2) | 180K + 1,680 | 구역 5 × fold 6 × 제외 방식 2 × (Brain → Emotion 3K + 2 + Brain + Decoded Feature → Emotion 26). 2,760회 |
| 네트워크 단독 학습(6-4a) | 468 | 13묶음 × 6 fold × seed 3 × 2조건(L10) |
| MC 시청 전이(6-3) | (3K + 28) + 입력층 36 | HK 최종 모델(Brain → Emotion 3K + 2, Brain + Decoded Feature → Emotion 26). MC 입력층은 2조건 × seed 3 × 6명. 46회 + 36회 |
| 본문 소계 | | 약 3,920회 |
| baseline 특징(보조) | 624 | VideoMAE, TimeSformer, CLIP, MPNet 넷 × Brain + Decoded Feature → Emotion fold마다 26 × 6 |
| 정서어 제거판(SI) | 156 | Brain + Decoded Feature → Emotion fold마다 26 × 6 |
| E-고정, E-학습(G16) | 162 | 7-L의 값. fold마다 Multimodal Model 11, E-고정과 E-학습 각각 8 |
| 평균 pooling판(F7, 보조) | 36 | O31: 2조건 × seed 3 × 6 fold |

- 출력: 파일럿 기록(실행 시간, 메모리, 수렴), K와 후보값, 실행량 표, 실행 사양 동결 commit 해시
- 확인 기준
    - 파일럿이 시험 fold 1을 쓰지 않았다.
    - 후보를 정한 근거(voxel 수, 가중치 수, 메모리, 실행 시간)가 기록되어 있다. 근거에 성능 수치가 없다.
    - 확정된 O1~O5가 들어간 통합문서가 동결 커밋에 있다.
- 실행 주체: 파일럿 실행은 석진 님 GPU. Claude Code는 파일럿 job script, 측정 집계, 후보 계산, 동결 커밋을 맡는다.
- 7-O 항목: O28(ML-BVAE 칸 수), O31(평균 pooling판 실행량). O1~O5는 확정됨.

### S8. 본 실행 지시서

- 목적: 석진 님이 돌릴 본 실행의 job script와 명령을 묶음별로 만든다.
- 근거: 7-L(실행 순서, 실행량), L1, L3, L9, L10, H2, G9, G10, G14, G16, N24, 3-1, 3-3, 3-4, 5-2, 6-2, 6-3, 6-4a, 7-L 실행 순서 7, 9~11
- 입력: S7에서 동결한 실행 사양
- 설정 선택 규칙(모든 뇌 모델)
    - H2
        - 바깥 fold k마다 학습 fold 5개 가운데 하나를 검증으로 쓴다. fold k + 1이고, fold 6의 검증은 fold 1이다(11/3 사용자).
        - 남은 4개 fold로 학습한다. 검증 fold로 조기 종료와 설정 선택을 한다.
        - 고른 모델을 그대로 시험한다. 5개 fold로 다시 학습하지 않는다.
        - 검증 fold는 N8의 보정 통계도 낸다. 이 fold는 설정 선택과 보정에 쓴 개발 자료이고, 모델 선택과 독립된 자료라고 부르지 않는다.
    - 공통 검증 기준(0-2, O6): 선택은 실제 y에 대한 정서별 r 평균, 조기 종료는 실제 y에 대한 정서 soft BCE다. 모든 조건에 같다.
    - L9
        - 설정 후보는 seed 0으로만 학습해 고른다.
        - 고른 설정으로 seed 1, 2를 더 학습한다. 같은 4개 fold로 학습하고 같은 검증 fold로 조기 종료한다.
        - 세 seed를 모두 보고한다. 가장 좋은 seed만 고르지 않는다.
        - seed 0 모델은 검증 fold에서 뽑힌 것이다. seed 사이 차이를 볼 때 이 점을 적는다.
        - 방법 절에 뇌 모델의 설정 선택을 "안쪽 5-fold 교차검증"이라고 쓰지 않는다.
    - 바깥 fold 안의 순서
        - Brain → Emotion으로 d와 입력층 weight decay를 먼저 고른다.
        - 그 값으로 나머지 조건을 학습한다.
        - Brain + Decoded Feature → Emotion [distillation]은 Brain + Decoded Feature → Emotion에서 고른 λ와 r을 쓴다.
    - G10
        - Brain → Emotion + Vision + Caption에서 λ = 0, 또는 Brain → Emotion [distillation]이 들어간 조건에서 α = 0이 뽑힌 fold는 "그 fold에서 이득이 확인되지 않음"으로 보고한다.
        - 그 fold의 결과는 앞 조건(Brain → Emotion이나 Brain + Decoded Feature → Emotion)의 모델이다.
        - fold별 선택값을 표로 낸다.
        - Brain + Decoded Feature → Emotion과 E-고정, E-학습에는 0 후보가 없다(G9).
    - L10: 6-4a는 그 바깥 fold의 표준 실행에서 고른 d, 입력층 weight decay, λ, r을 그대로 쓴다.
    - N24: 후보별 시험 성능은 저장만 한다. 선택에 쓰지 않는다.
- 묶음별 실행
    - 사다리(필수, L1)
        - A~C 묶음 다섯 조건과 더하기 head. 6 fold. 후보는 S6에 있다.
        - 18K + 360회(learning rate 후보 포함, 7-L)
    - 필수 대조군(G6)
        - label smoothing, Stimulus Model 출력 섞기(Brain → Emotion [distillation]에 적용), Vision feature와 Caption feature 짝 섞기(Brain → Emotion + Vision + Caption에 적용). 6 fold
        - 순열은 O1의 결정을 따른다.
        - 144회
    - 처음 보는 장면(6-2, 필수)
        - 구역 5개 × 바깥 fold 6개 × 제외 방식 2개(구역 제외, 학습량 대조)
        - 조건은 Brain → Emotion과 Brain + Decoded Feature → Emotion(상호작용 head)이다. 두 조건은 Stimulus 예측 평정과 frozen head를 쓰지 않는다(4-3).
        - 시험: 시험 run fold 안의 그 구역 영상. 두 제외 방식과 두 조건이 같은 시험 영상을 쓴다.
        - 학습 자료
            - 구역 제외: 시험 run fold 전체와 그 구역 전체를 뺀 영상
            - 학습량 대조: S2에서 고정한 표본
        - 설정 선택(d, 입력층 weight decay, λ, r), 조기 종료, 표준화를 그 학습 자료 안에서 다시 한다. 검증 fold도 그 자료 안의 H2 규칙이다.
        - 빠진 구역은 어디에도 쓰지 않는다(4-3).
        - 180K + 1,680회
    - 네트워크 단독 학습(6-4a, 필수)
        - 13묶음 각각의 ROI token만 넣고 다시 학습한다. 다른 영역의 정보가 섞이기 전부터 입력을 제한한다.
        - Brain → Emotion과 Brain + Decoded Feature → Emotion. 6 fold × seed 3. 설정은 L10이다.
        - Brain + Decoded Feature → Emotion에서는 decoded visual features와 decoded caption features도 채점한다(2-1의 지표).
        - 468회
    - MC 시청 전이(6-3). 시점은 일정 결정에서 정한다(6-3, L1).
        - HK 최종 모델
            - 개발 영상 전체로 학습한 Brain → Emotion과 Brain + Decoded Feature → Emotion이다.
            - 설정은 H2 규칙(검증 fold 하나)을 개발 영상 전체에 적용해 고른다. 검증 fold는 O7이다.
            - seed 3개
        - 고정하는 것: encoder, query, feature head, emotion head, e(r) 등 HK의 공유 가중치 전부
        - 새로 학습하는 것: MC 참가자마다 W(s, r), b(s, r)만
            - 각 조건의 원래 손실을 그대로 쓴다. Brain → Emotion은 정서 손실, Brain + Decoded Feature → Emotion은 정서 손실과 feature decoding loss다.
            - feature decoding loss의 목표 좌표는 O30이다(HK 개발 영상의 D9 통계).
            - 학습 자료는 MC 시청 학습 세션 2,108개다. 검증 run은 O29다.
            - 입력층의 weight decay와 조기 종료는 검증 run에서 공통 검증 기준으로 고른다.
            - MC 입력 표준화는 이 2,108개의 통계로 한다(C5).
        - 시험: 72개 영상의 반복 평균 뇌 반응만 넣는다. QC 뒤 남은 반복으로 평균한다(정할 것 9, manifests/s2/mc_test_repeats.tsv).
        - seed 3개를 각각 전이한다. 결과를 seed마다 낸다.
        - (3K + 28) + 36회
    - E-고정, E-학습(G16, 보조)
        - 핵심 분석 다음 순서다.
        - S7에서 측정한 시간으로 우선순위를 정한다.
        - 자동으로 빼는 규칙은 두지 않는다. 실행하지 못하면 기록 칸에 미실행으로 적는다.
        - 162회(E-고정, E-학습, Multimodal Model 포함, 7-L)
    - baseline 특징(3-1, 3-3, 보조)
        - VideoMAE, TimeSformer, CLIP: 시각 목표만 바꾼다. 캡션 목표는 DeBERTa 그대로 둔다.
        - MPNet: 캡션 목표만 바꾼다.
        - Stimulus Model과 Brain + Decoded Feature → Emotion만 같은 절차로 다시 돌린다. 층 분석과 ROI 분석은 하지 않는다.
        - 624회
    - 정서어 제거판(3-4, SI): 정서어 제거 Caption feature로 Brain + Decoded Feature → Emotion을 돌린다. 156회
    - 외부 baseline(I7, 5-2): GED, ML-BVAE, EmoGrowth. 우리 run 분할의 6 fold. I7의 기준선이므로 필수 실행 범위다(L1). seed와 검증은 O27이다.
    - 평균 pooling판(F7, 보조): 36회(O31). L3의 순서에 따라 남는 시간에 한다.
- 순서(7-L)
    1. 사다리와 필수 대조군
    2. 저장된 모델로 하는 분석(S9)
    3. 처음 보는 장면(6-2)
    4. 네트워크 단독 학습(6-4a)
    5. MC 시청 전이(6-3, 시점은 일정 결정에서)
    6. 검정, 표, 그림(S10)
    - E-고정, E-학습은 핵심 분석 다음이다(L1).
- 시간이 모자랄 때 줄이는 순서(L3). 시간 기준이고 결과를 보고 바꾸지 않는다.
    1. baseline 특징과 정서어 제거판을 필수 실행 범위 밖으로 뺀다.
    2. 6-4a의 Brain + Decoded Feature → Emotion을 seed 1로 줄인다.
    3. 보조 분석 전체의 seed를 3에서 2로 줄인다.
    4. 본문 조건의 seed를 3에서 2로 줄인다.
    - 6-1의 [사전] 비교 15개에 필요한 조건은 끝까지 유지한다.
    - 4-3의 규칙(빠진 구역은 설정 선택에도 쓰지 않음)은 줄일 때도 바꾸지 않는다.
- 출력
    - 묶음별 job script와 실행 명령 목록
    - 묶음별 예상 시간
    - 결과는 project/output/ 아래 조건 이름 폴더에 둔다(M3). 폴더 이름은 1-1의 영어 이름에서 만든다.
- 확인 기준
    - 모든 job script가 실행 사양 동결 commit에서 돈다.
    - 실행마다 M1의 저장 항목이 남는다.
    - fold별 선택값 표와 0이 뽑힌 fold 표가 나온다.
- 실행 주체: 석진 님 GPU. Claude Code는 job script와 명령을 만들고, 끝난 실행의 저장 항목을 점검한다.
- 7-O 항목: O1, O5, O6, O7(6-3의 검증 fold), O27(외부 baseline), O29(MC 검증 run), O30(MC 특징 목표 좌표), O31(평균 pooling판)

### S9. 저장된 모델로 하는 분석

- 목적: 다시 학습하지 않고 저장된 모델과 예측으로 경로 의존(2-2, 1-1), 결합(1-2), 쌍 비교, 경로 평가, 네트워크 교란(2-4)을 계산한다.
- 근거: 4-1, 4-2, 5-0, 5-4, 6-1(2-2, 1-1, 1-2행), K1, K1a, N6, N7, N8, 6-4b, 7-L 실행 순서 8
- 입력: S8의 체크포인트, decoded features(시험 fold와 검증 fold), 시험 예측, S2의 짝 목록, S4의 K1 head와 K1a Stimulus Model, S5의 ridge decoded features
- 할 일
    - 바꿔 끼우기(4-2, 5-0)
        - 모델: Brain + Decoded Feature → Emotion의 상호작용 head(5-4). 바깥 fold마다, seed마다, 참가자마다 한다.
        - 짝: 영상 A와 같은 시험 fold의 짝 B(S2)
        - v̂_B, ĉ_B는 같은 참가자, 같은 fold, 같은 모델이 B에서 낸 값이다. 다른 fold의 모델이 만든 값을 섞지 않는다.
        - 네 조건(ROI token, decoded visual features, decoded caption features)
            - 원래 예측: (A, A, A)
            - 시각만 교체: (A, B, A)
            - 캡션만 교체: (A, A, B)
            - 둘 다 교체: (A, B, B). 같은 짝 B의 두 값을 가져온다. 시각 B, 캡션 C 같은 조합은 만들지 않는다.
        - 계산: ROI token은 A로 고정이다. z = g(H_A) + a(v̂) + b(ĉ) + U[(Av̂) ⊙ (Bĉ)]에 바꾼 값만 넣는다. logit과 확률을 모두 저장한다.
        - 경로마다 실제로 바뀐 decoded features의 크기(D9 좌표의 유클리드 길이)와 짝의 이름표 거리를 기록한다. 단위가 다른 경로의 길이를 그대로 비교하지 않는다.
        - 같은 크기의 무작위 변경 대조(O3)
            - 같은 참가자, 같은 시험 fold에서 A와 B가 아닌 영상 C를 무작위로 고른다.
            - (C의 decoded features − A의 decoded features)를 방향으로 쓰고, 길이를 실제 A→B 변경의 길이(D9 좌표의 유클리드 길이)와 같게 맞춘다.
            - 두 경로를 함께 바꿀 때는 같은 C를 쓰고 경로마다 길이를 맞춘다.
            - 채점은 원래 짝 B와의 사람 평정 차이 Δy = y_B − y_A로 한다.
            - 반복은 100회로 고정한다. 매회 전체 쌍의 통계량을 낸 뒤 100개 통계량을 평균한다. 이것이 대조 평균이다. 예측값을 먼저 평균하지 않는다.
            - 이 100회에서는 p 값을 내지 않는다. 실제 교체와 대조 평균의 차이는 O4의 재표집(10,000회)으로 평가한다(S10).
            - 쌍마다, 반복마다의 대조 결과를 저장한다. 재표집 때 쌍과 함께 가져온다.
        - 효과(6-1의 2-2행, 1-1행, O2)
            - 예측 변화 Δp = 교체 후 확률 − 원래 확률, 사람 평정 차이 Δy = y_B − y_A다.
            - 참가자, 정서, 교체 조건마다 6 fold의 모든 쌍에 걸친 Pearson r(Δp, Δy)을 대응으로 쓴다.
            - Δy가 0인 쌍도 넣는다(4-1). Δy가 모든 쌍에서 0인 정서는 빼고, Δp가 상수인 정서는 계산 불가로 따로 센다(2-6).
            - 효과는 실제 교체의 r에서 대조 평균의 r을 뺀 값이다.
            - 2-2는 34개 정서 평균이다. 1-1은 정서마다 시각 효과와 캡션 효과의 차이다.
        - 보조 비교(1-1)
            - Kragel 외(2019)에서 정지 프레임 분류 성능이 높았던 정서(craving, sexual desire, entrancement, horror)와 낮았던 정서(confusion, awe, surprise)의 두 경로 효과를 비교한다.
            - 이름은 "EmoNet에서 정지 프레임 분류 성능이 높았던 정서, 낮았던 정서"로 쓴다.
            - 우리 34개 열 이름과의 대응은 S1의 라벨 대조 뒤에 맞춘다.
        - 결합 지표(1-2의 (나))
            - I = z(B, B) − z(A, B) − z(B, A) + z(A, A)
            - 괄호는 (시각 출처, 캡션 출처)다. ROI token은 A로 고정이다.
            - logit으로 계산한다. 최종 점수의 변화도 따로 낸다(5-0).
            - 정서별 요약은 쌍에 걸친 평균 \|I\|다(O2). 무작위 변경 대조에도 같은 계산을 하고, 100회의 평균을 대조 평균으로 쓴다(O3).
            - 더하기 head에서는 I가 0이어야 한다(S6의 단위 시험).
        - 같은 영상이 여러 쌍과 여러 참가자에 반복되므로 쌍은 독립이 아니다. 쌍 수를 표본 수로 세지 않는다(O4).
    - 내용이 비슷한 영상 쌍 비교(4-2의 분석 1, 보조 점검, O33)
        - 이미 얻은 시험 예측으로 계산한다. 학습을 더 하지 않는다.
        - 모델은 Brain → Emotion과 Brain + Decoded Feature → Emotion이다.
        - 정서마다 쌍의 실제 점수 차이(B 빼기 A)와 예측 차이(B 빼기 A)의 Pearson r을 내고 34개 평균도 낸다.
        - 쌍은 순서 없는 쌍으로 센다(O4 (7), O33). 서로 최근접인 쌍은 한 번만 쓰고 영상 번호가 작은 쪽을 A로 둔다. S2의 순서 없는 쌍 목록을 쓴다.
        - 구간은 O4 (2)의 이어진 묶음 단위 재표집으로 낸다.
        - 다른 결과를 해석하기 위한 관문으로 두지 않는다.
    - 상호작용 head 대 더하기 head(1-2의 (가)): 정서마다 두 head의 시험 성능을 비교한다(S10).
    - 경로 평가(K1, 보조)
        - 두 decoded features만 Stimulus Model의 고정 head(S4, 두 특징을 함께 받는 것 하나)에 넣어 정서를 예측한다. ROI token 경로는 넣지 않는다.
        - 넣는 값은 두 가지다: ridge decoded features(S5), Brain + Decoded Feature → Emotion decoded features
        - Stimulus Model의 더하기판과 상호작용판 둘 다 한다.
        - 뇌 모델은 더 학습하지 않는다.
        - decoded features는 Stimulus Model이 학습한 실제 Vision feature와 Caption feature와 같은 차원, 좌표, 표준화(D9)에 있어야 한다(5-4).
        - 크기 보정(N8)
            - 보정 전 판과 보정판을 함께 보고한다. 시험 결과를 보고 둘 중 하나를 고르지 않는다.
            - 보정판은 decoded features의 차원별 평균과 분산을 실제 Vision feature와 Caption feature에 맞춘 것이다. Stimulus Model head가 받도록 학습한 좌표(D9)에서 맞춘다.
            - 보정 통계는 H2의 검증 fold에서 낸다. 사람 평정과 시험 fold는 쓰지 않는다. 통계를 고정해 시험 영상에 적용한다.
            - ridge의 보정 통계를 내는 자료는 O34, 분산이 아주 작은 차원의 처리는 O35다.
        - 보고: Brain → Emotion과 경로 평가 각각의 절대 성능(정서별 Pearson r)과, 같은 시험 영상에서 계산한 두 성능의 차이와 구간(O4). 비율은 쓰지 않는다(K1, N6).
    - 경로 평가의 14개 차원판(K1a, 보조)
        - S4의 K1a Stimulus Model에 세 가지 값을 넣어 14개 차원을 예측한다. 실제 Vision feature와 Caption feature, ridge decoded features(S5), Brain + Decoded Feature → Emotion decoded features(상호작용 head, seed 3개)다.
        - 넣는 decoded features는 K1과 같다. 같은 참가자, 같은 fold, 같은 모델, 같은 seed의 값을 쓴다. ROI token 경로는 넣지 않는다.
        - 더하기판과 상호작용판 둘 다 한다. 뇌 모델과 Stimulus Model은 더 학습하지 않는다.
        - N8 보정은 K1과 같다. 보정 전 판과 보정판을 함께 내고, K1에서 낸 통계(O34, O35)를 그대로 쓴다.
        - 예측은 fold의 사람 평정 표준화 통계로 되돌려 1~9점 척도로 저장한다. 6 fold를 모으는 계산은 S10에서 한다(O20과 같은 이유).
        - 14개 차원의 교체 분석은 하지 않는다(B4). 경로 사용은 34개 범주의 바꿔 끼우기만 답한다.
    - 네트워크 단위 입력 교란(6-4b)
        - 모델: 전체 뇌로 학습한 Brain → Emotion과 Brain + Decoded Feature → Emotion(상호작용 head)을 고정한다. 다시 학습하지 않는다.
        - 13묶음마다 그 묶음 ROI의 입력 x(s, r)만 같은 참가자의 다른 영상 값으로 바꾼다. 0으로 지우지 않는다.
        - ROI token은 그 ROI의 voxel만으로 만들어지므로, 이것은 shared self-attention 전에 바꾸는 것과 같다.
        - 한 묶음 안의 ROI는 같은 참가자의 같은 다른 영상에서 함께 가져온다.
        - 두 모델에 같은 교체를 적용한다.
        - 다른 영상을 고르는 규칙과 반복 수(O3)
            - 시험 영상마다 같은 바깥 시험 fold의 다른 시험 영상을 무작위로 하나 고른다.
            - 두 모델과 13묶음 모두에 같은 영상 배정표를 쓴다.
            - 20회 반복한다. 매회 성능 하락(원래 − 교란)을 낸 뒤 20회를 평균한다.
            - 배정표와 그 seed를 저장한다.
        - 각 모델의 성능 하락과 두 모델 사이의 하락폭 차이를 낸다. 검정은 S10에서 한다.
- 출력
    - 쌍마다, 조건마다의 logit과 확률, 바뀐 크기, 무작위 대조 결과, I
    - 쌍 비교 표, 경로 평가 표(보정 전과 보정판), 교란 결과
    - K1a의 시험 예측(참가자, fold, seed, 넣은 값, 판, 보정 여부마다 14개 차원의 1~9점 값)
    - 위치는 project/output/ 아래(M3)
- 확인 기준
    - 교체에 쓴 값이 모두 같은 참가자, 같은 fold, 같은 모델에서 나왔다.
    - 더하기 head의 I가 0이다.
    - 교란에 쓴 다른 영상과 무작위 변경에 쓴 영상이 기록되어 있다.
    - N8의 보정 통계에 시험 fold가 들어가지 않았다.
    - K1a에 넣은 decoded features와 보정 통계가 K1과 같다.
- 실행 주체: Claude Code가 스크립트를 만든다. GPU가 필요하면 석진 님이 실행한다.
- 7-O 항목: O2, O3, O16, O17(K1a의 학습 설정과 판), O20(K1a의 척도), O33(쌍 비교), O34(N8 보정 자료), O35(분산이 작은 차원)

### S10. 통계와 표

- 목적: 6-1의 판정 규칙대로 검정하고 표를 만든다.
- 근거: 2-3, 2-4, 2-6, 4-2, 6-1, 6-2, 6-3, 6-4, I5, N10~N13, N19~N23, G10, G14, B7, B4, F8, K1, K1a, 3-2
- 입력: S5, S8, S9의 시험 예측과 분석 결과
- 할 일
    - 주 지표(2-3, N12)
        - 참가자마다, 정서마다 6 fold의 시험 예측을 모은다(약 2,100개 영상).
        - 모은 예측과 사람 평정으로 Pearson r을 한 번 낸다. fold별 r을 평균하지 않는다.
        - 34개를 산술평균해 참가자 점수를 낸다.
        - 5명의 점수, 5명 평균, 정서별 결과를 모두 보고한다.
        - 계산할 수 없는 r(사람 평정이나 예측에 변동이 없음)은 0으로 채우지 않는다. 빼고 그 수를 보고한다(2-6, N12).
        - Fisher z 평균은 SI다.
        - seed마다 점수를 내고, 평균과 표준편차를 보고한다. seed 예측을 평균한 앙상블 점수는 내지 않는다(G14).
        - 모든 조건 비교는 같은 참가자, 같은 영상 행에서 한다(N11).
        - 5명 공통 영상 기준 결과도 낸다(B7).
        - decoded features의 차원별 r은 O20의 좌표에서 낸다.
    - 보조 평가(2-4, N19)
        - 평균 예측 대비 오차 감소(O25)
        - 영상별 프로필 상관: 한 영상 안에서 34개 예측과 사람 평정의 상관이다. 학습 자료의 평균 프로필을 늘 내는 기준선을 함께 둔다.
        - 사람 평정이 0인 영상과 0보다 큰 영상을 나눈 오차, R²와 MAE 합을 r과 함께 낸다(N19).
        - 영상 식별(Horikawa 외, 2020의 범주 81.9%)은 선행 연구 비교용 보조 자료다.
        - 이진화 지표와 분포 거리는 내지 않는다.
    - 정서별 보고(2-6)
        - 정서마다 0이 아닌 영상 수, 평정의 분산, bootstrap 구간을 함께 낸다.
        - 상관을 계산할 수 없으면 "계산 불가"로 표시한다.
        - 드문 정서를 일괄 제외하지 않는다.
    - 판정 규칙(6-1)
        - 참가자 다섯 명 각자의 효과 크기와 95% 구간을 모두 낸다.
        - 효과가 확인된 사람 수를 적는다. 그 수가 다중비교 보정 전인지 후인지 함께 적는다.
        - "5명 중 4명 이상" 같은 문턱은 두지 않는다.
        - 5명 평균과 그 구간도 낸다. 이 다섯 명에 대한 결과로만 쓴다.
        - 모집단 유병률 추정(Ince 외, 2021)과 동등성 검정은 하지 않는다.
        - 구간은 학습된 모델을 고정한 채 시험 영상을 다시 뽑은 것이다. 다시 학습할 때의 변동은 담지 않는다(Bates 외, 2024). 학습 변동은 seed 3개의 표준편차로 따로 낸다.
    - 재표집과 순열(6-1, I5, N13, O4)
        - 정해진 것: 주 재표집 단위는 영상이다. 같은 영상에 대한 두 조건의 예측과 5명의 예측을 함께 다시 뽑는다. 같은 내용 영상 묶음이 남아 있으면 묶음으로 뽑는다. run 단위 bootstrap은 민감도다. 재표집은 10,000번이다.
        - 순열(O4 (1))
            - 섞는 것: 사람 평정과 영상의 대응이다. 정서 검정은 규범 평정 벡터(34개)를, 2-1 검정은 실제 Vision feature와 Caption feature 벡터를 다른 영상에 다시 배정하고 예측은 그대로 둔다.
            - 섞는 범위(exchangeability block): HK에서는 같은 시험 fold 안에서도 같은 원래 run 안의 영상끼리만 섞는다(Winkler 외, 2014). 6-2에서는 구역 경계도 넘지 않는다. MC의 72개 반복 평균 자료는 72개 안에서 섞는다.
            - 34개 정서 벡터와 5명에 같은 순열을 쓴다. 같은 내용 쌍은 한 단위로 다룬다.
            - 검정력 때문에 범위를 넓히지 않는다(O4).
            - p 값(O4 (6)): 순열은 10,000회다. 6-1의 예상 방향(순열 기준보다 높다)으로 한쪽 검정을 한다. p = (1 + 귀무 값이 관찰 값 이상인 횟수) / (순열 수 + 1)이다.
        - 재표집 단위
            - 바꿔 끼우기와 쌍 비교: 최근접 짝으로 이어진 영상 묶음(S2의 짝 연결 묶음) 전체를 단위로 다시 뽑는다. 그 안의 쌍과 쌍마다의 대조 결과(O3의 100회)를 함께 가져온다. 묶음 크기 분포를 기록한다(O4 (2), (7)).
            - 다른 분석: 기존 영상 단위 재표집
        - 구간과 p(O4 (3))
            - 구간은 basic bootstrap 95%다. 관찰 값 θ와 재표집 값 θ*의 분위수로 [2θ − q(0.975), 2θ − q(0.025)]를 낸다.
            - 조건 차이의 p는 중심을 맞춘 양측 bootstrap 검정이다. 재표집한 차이에서 관찰한 차이를 뺀 분포(Δ* − Δ)를 귀무분포로 쓰고, p = (1 + #(\|Δ* − Δ\| ≥ \|Δ\|)) / (B + 1)이다(Hall & Wilson, 1991).
            - 바꿔 끼우기(2-2, 1-1, 1-2 (나))의 차이는 실제 교체와 대조 평균의 차이다. 재표집마다 뽑힌 쌍으로 실제 교체의 통계량과 100회 대조 통계량의 평균을 다시 낸다.
        - 정서끼리 비교하는 예측의 검정은 영상 단위 순열이고(N20), 섞는 범위는 위의 순열과 같다. 남은 정서가 적으면 검정 없이 서술한다.
    - 다중비교(6-1, 6-4)
        - [사전] 15개(아래 표)는 Holm 보정을 쓴다. 5명 평균의 검정 묶음과 참가자마다의 검정 묶음에 각각 적용한다.
        - 정서 34개별 분석(1-1, 1-2)은 탐색으로 표시하고 BH-FDR을 쓴다. 보정 묶음은 참가자마다, 비교마다 34개 정서다.
        - 2-4(6-4b)는 13묶음의 하락폭 차이 검정을 한 묶음으로 Holm 보정한다.
        - 6-4의 나머지는 탐색으로 표시하고 BH-FDR을 쓴다. 나머지 10묶음의 단독 학습 결과, Brain + Decoded Feature → Emotion의 결과, 묶음 안 정서별 결과가 해당한다. 보정 묶음을 결과와 함께 밝힌다.
        - 보조 비교는 Holm 15개에 넣지 않고 따로 보고한다. 방향을 예측하지 않는다. G6의 올바른 대응 대 섞은 대응, E-고정, E-학습 대 Brain + Decoded Feature → Emotion과 Brain → Emotion이 해당한다.
        - 0행(전제 검정, O4 (4)): Brain → Emotion과 Brain + Decoded Feature → Emotion 각각의 34개 정서 평균 r을 순열 기준과 비교한다. 두 검정을 [사전] 15개와 따로 한 Holm 묶음(2개)으로 보정한다. 5명 평균과 참가자마다 각각 적용한다(6-1).
        - MC 전이(6-3, O4 (5))는 보정 없이 따로 보고한다.

| 질문 | [사전] 비교 | 수 |
| --- | --- | --- |
| 2-1 decoding | Vision feature, Caption feature의 ridge decoding 대 순열 기준. 통계량은 차원별 r 평균(O19) | 2 |
| 2-2 이용 | Brain + Decoded Feature → Emotion의 시각만, 캡션만, 둘 다 교체 대 같은 크기 무작위 변경 | 3 |
| 2-3 성능 | (가) Brain → Emotion + Vision + Caption 대 Brain → Emotion, (나) Brain + Decoded Feature → Emotion 대 Brain → Emotion + Vision + Caption, (다) Brain → Emotion [distillation] 대 Brain → Emotion, (라) Brain → Emotion [distillation] 대 label smoothing, (마) Brain → Emotion + Vision + Caption 대 Brain → Emotion [distillation], (바) Brain + Decoded Feature → Emotion [distillation] 대 Brain + Decoded Feature → Emotion | 6 |
| 처음 보는 장면 | Brain + Decoded Feature → Emotion 대 Brain → Emotion의 "다섯 내용 구역의 평균 성능" | 1 |
| 1-3 영역 | 1차 시각, 2차 시각, Default 묶음의 Brain → Emotion 모델 대 순열 기준 | 3 |

- 할 일(이어서)
    - 처음 보는 장면(6-2)
        - 구역마다 6 fold의 시험 예측을 모아 참가자별, 정서별 r을 낸다. 다섯 구역을 섞은 r 하나로 대신하지 않는다.
        - 평가 정서 목록: 구역마다, 그 구역 시험 영상에서 사람 평정이 모두 같은 정서만 뺀다.
        - 같은 구역에서는 네 설정(Brain → Emotion과 Brain + Decoded Feature → Emotion, 각각 구역 제외와 학습량 대조)에 같은 목록을 쓴다. 구역마다 포함된 정서 수를 낸다.
        - 모델이 상수만 예측한 경우는 사람 평정이 상수인 경우와 따로 센다. 그 정서는 그 구역에서 네 설정 모두의 평균에서 뺀다. 어느 모델의 어느 정서였는지 적는다.
        - 요약값: 구역마다 평가 정서의 r을 평균하고, 다섯 구역을 같은 무게로 평균한다. 이것이 "다섯 내용 구역의 평균 성능"이다.
        - 낼 것
            - 절대 성능(구역 제외), 학습량 대조 대비 하락폭, 두 모델의 차이, 구역별 결과
            - 정서별로 남은 0이 아닌 학습 영상 수(두 제외 방식), 시험 쪽 사람 평정 분포
            - 보조 모델(ridge, Stimulus Model)의 결과
            - Brain + Decoded Feature → Emotion decoded features의 2-1 지표
        - "더 높다"와 "덜 떨어진다"는 따로 판정한다. 하락폭 차이는 직접 비교한다. 방향은 정하지 않았다.
    - MC 시청 전이(6-3)
        - 참가자별, 정서별로 72개 영상에 걸친 r을 내고 34개를 평균한다.
        - 72개 시험 영상에서 사람 평정이 모두 같은 정서는 두 조건 모두에서 빼고 그 수를 낸다.
        - 예측이 일정한 경우는 따로 낸다. 그 정서를 한 모델에서만 빼고 평균하지 않는다.
        - seed 3개를 참가자 3명처럼 다루지 않는다.
        - 시험 영상이 72개뿐이라 구간이 넓을 수 있음을 적는다.
    - 영역(6-4)
        - 6-4a의 평가 정서는 34개 모두다. 시험 영상 전체에서 사람 평정이나 예측이 상수라 r을 계산할 수 없는 정서만 빼고 그 수를 보고한다(6-4a, 2-6).
        - 6-4a: 묶음마다 정서 예측 성능과 두 decoded features의 decoding 성능을 나란히 낸다. decoding 성능은 Brain + Decoded Feature → Emotion에서만 낸다.
        - 6-4b: 묶음마다 두 모델의 하락과 하락폭 차이의 불확실성을 낸다.
        - 13묶음의 참가자 간 일치도(S2)를 함께 적는다.
    - 경로 평가(K1): Brain → Emotion과 경로 평가의 절대 성능, 두 성능의 차이와 구간을 낸다. 보정 전과 보정판을 둘 다 낸다. 비율은 쓰지 않는다.
    - 14개 차원(B4, K1a, 보조). 표 하나로 낸다.
        - 차원마다 시험 영상에 걸친 Pearson r로 세 성능을 나란히 둔다. 참가자별 값과 5명 평균을 낸다. 6 fold를 모아 r을 한 번 낸다(2-3).
            - (1) B4 ridge의 뇌 직접 decoding(주 비교판)
            - (2) 실제 Vision feature와 Caption feature를 넣은 Stimulus Model. 참고값이고 상한이 아니다.
            - (3) decoded features를 넣은 Stimulus Model. ridge판과 Brain + Decoded Feature → Emotion판, 더하기판과 상호작용판, 보정 전과 보정판이다. Brain + Decoded Feature → Emotion판은 seed마다 내고 평균과 표준편차를 적는다(G14).
        - (3)의 판마다 (1)과의 차이와 구간을 같은 참가자, 같은 시험 영상에서 낸다(N11, O4 (3)). 비율은 쓰지 않는다.
        - 차원별 검정은 탐색으로 표시하고 BH-FDR을 쓴다. 보정 묶음은 참가자마다, 비교마다 14개 차원이다. [사전] 15개의 Holm 묶음에 넣지 않는다.
        - 차원별 평정 신뢰도 칸은 [미확인]으로 둔다(기록 칸 S0). 값이 확인되어도 분석에 넣거나 빼는 조건으로 쓰지 않는다.
    - 그 밖의 표
        - 조건별 학습 가중치 수(F8)
        - fold별 선택값(d, 입력층 weight decay, λ, α, r)과 0이 뽑힌 fold(G10)
        - 영상 길이 기준선과 길이를 통제한 편상관(N21, O25)
        - 영상 길이 구간별 결과(3-2, SI)와 window로 나뉜 영상(개발 영상 80개)을 뺀 주 지표. 저장된 예측으로 계산하고 재학습하지 않는다.
        - ridge에서 λ의 양 끝이 뽑힌 횟수(O18), N8에서 평균만 옮긴 차원 수(O35)
- 해석 문장 규칙. 결과 문장은 6-1 표의 행을 따른다. 아래는 짧게 모은 것이다.
    - 사람 평정은 규범 평정이다. 참가자가 느낀 정서를 읽었다고 쓰지 않는다.
    - 차이가 확인되지 않으면 "확인하지 못했다"와 구간을 쓴다. "같다"고 쓰지 않는다.
    - 구간이 예상과 반대쪽으로 0을 넘으면 "낮아졌다"고 쓴다.
    - 한쪽만 유의하다는 이유로 둘이 다르다고 쓰지 않는다. 차이를 직접 검정한다.
    - 경로 결과는 "이번 교환 조건에서 모델이 그 경로에 기댔다"까지다. 시각 정보나 의미 정보의 기여로 옮기지 않는다. 두 경로를 더해 비율로 나누지 않는다.
    - 한 경로를 바꿔 효과가 작아도 그 경로가 정보를 담지 않았거나 쓰이지 않았다고 쓰지 않는다. ROI token 경로가 남아 있다.
    - 두 경로를 함께 바꾼 효과는 두 경로에 대한 공동 의존성이다. 공유 정보의 양이 아니다.
    - I는 모델 계산의 비가산성이다. 공유 정보량이나 뇌의 인과적 상호작용이 아니다.
    - 경로 평가가 잘되어도 "고정된 규칙을 decoded features에 적용할 수 있었다"까지다. Brain + Decoded Feature → Emotion이 그 특징을 실제로 썼는지는 바꿔 끼우기가 답한다(K1). 보정판은 크기 차이를 보는 보조 결과다(N8).
    - 14개 차원은 "뇌에서 decoding한 장면 특징으로 일부 정서 차원도 예측할 수 있었다"까지다. "뇌 모델이 정서 차원 예측에 장면 정보 경로를 썼다", "범주 결과가 valence나 arousal로 설명된다", "설명되지 않는다"고 쓰지 않는다. 결과를 본 뒤 메인 분석으로 올리지 않는다(K1a).
    - Brain → Emotion [distillation]의 이득은 label smoothing을 넘을 때만 Stimulus 예측 평정의 내용 효과로 쓴다. 이득이 모든 정서에 고르면 정칙화 효과일 가능성을 함께 쓴다(N10).
    - Stimulus Model 성능은 뇌 모델의 상한이 아니다. "격차를 몇 % 메웠다"고 쓰지 않는다. 고른 λ, α를 기여 비율로 읽지 않는다(N10).
    - Brain → Emotion + Vision + Caption에서 λ = 0이 뽑힌 실행을 "특징 학습의 이득"으로 해석하지 않는다(G10).
    - 영역 결과는 "그 묶음의 신호만으로 예측할 수 있었다" 또는 "이번 교체 조건에서 그 묶음 입력에 더 민감했다"까지다. 신뢰도가 낮은 묶음의 낮은 성능을 "정보 없음"으로 읽지 않는다.
    - 처음 보는 장면은 "학습에서 뺀 이름표 구역"이다. 사전학습 모델이 본 적 없는 장면이라고 쓰지 않는다.
    - MC 결과를 "외부 검증"이나 "가벼운 보정"이라고 부르지 않는다.
    - E-고정, E-학습의 결과는 학습 방식 전체의 차이로만 쓴다. Multimodal Model의 뇌 사용이나 시각과 캡션의 고유한 기여를 입증했다고 쓰지 않는다(G16).
    - 딥러닝 모델이 ridge보다 나빠도 설계를 바꾸지 않는다. 경로와 ROI 결과를 "이 모델 조건부"로 보고한다(N23).
    - 평균 pooling판이 query판과 같거나 나으면 "정서별 query" 주장을 거둔다(N22).
- 출력: 6-1의 판정표, 정서별 표, 보조 평가 표, 구역별 표, 영역 표, 14개 차원 표, 선택값 표. 요약 표만 커밋한다(M3).
- 확인 기준
    - 모든 [사전] 비교에 참가자별 효과 크기, 95% 구간, 보정 전과 후의 확인 수가 있다.
    - 표마다 "계산 불가"의 수가 있다.
- 실행 주체: Claude Code
- 7-O 항목: O2, O3, O4, O19, O20, O25

### S11. 저장과 기록

- 목적: 다시 학습하지 않고 해석 분석을 할 수 있게 모든 실행의 중간 결과와 기록을 남긴다.
- 근거: M1, M2, M3, M5, M6, N1, N34
- 입력: 모든 단계의 실행
- 할 일
    - M1: 실행마다 저장한다.
        - config, git commit, 특징 파일 체크섬, split manifest, 체크포인트
        - 안쪽 선택 기록: d, 입력층 weight decay, 특징 선형층 weight decay, λ, α, r, learning rate, epoch
        - 시험 예측: logit과 확률
        - decoded features(시험 fold와 검증 fold)
        - emotion query와 feature query의 attention 값
        - 섞기 순열, 무작위 변경과 교란에 쓴 영상의 난수 seed
    - M2: 특징 추출 기록(S3)
    - M3
        - 결과는 git에 올리지 않는 project/output/ 아래, 조건 이름 폴더에 둔다.
        - 요약 표만 커밋한다.
        - 폴더 이름은 1-1의 영어 이름에서 만든다. ex) direct_training, response_based_distillation, auxiliary_feature_decoding, decoded_feature_readout_interaction, decoded_feature_readout_additive, decoded_feature_readout_plus_response_based_distillation, frozen_head_distillation
    - M5: 설계 동결(S0)과 실행 사양 동결(S7)의 commit 해시를 기록한다.
    - M6, N1, N34
        - 10월 사전 분석 수치는 결과에 쓰지 않는다.
        - 사전 분석에 노출된 선택과 파일럿 fold를 노출로 기록한다.
    - 기록 칸(2절)을 단계마다 채운다. 채운 값은 석진 님과 Claude가 통합문서에 반영한다.
- 출력: 실행마다의 저장 묶음, 갱신한 기록 칸
- 확인 기준: 저장된 것만으로 S9의 분석을 다시 할 수 있다.
- 실행 주체: Claude Code
- 7-O 항목: O32(재현성)

## 2. 기록 칸

- Claude Code가 채운다. 실제 값이나 발견을 적고, 통합문서의 관련 행과 날짜를 단다.
- 이 표를 석진 님과 Claude가 통합문서에 반영한다.
- 아래 행은 미리 정한 항목이다. 새로 생긴 불일치와 정할 수 없던 일은 맨 아래에 행을 더한다.

| 항목 | 실제 값 또는 발견 | 통합문서의 관련 행 | 날짜 |
| --- | --- | --- | --- |
| S0. docs/archive/pre-final-2026-10와 04_DECISION_REGISTER의 위치, 옛 설계와 다른 점 | 점검한 레포: Transconnectome/EmoBrain, 브랜치 `docs/unify-study-design-20261006`, commit cb3a29f(10/28), Mac의 임시 clone에서 읽기만 함. 위치: `docs/archive/pre-final-2026-10/` 13개 파일(00~10, CHANGELOG, SERVER_PROMPT), `docs/archive/pre-final-2026-10/04_DECISION_REGISTER.md`. main에는 없음. 구현에 영향을 주는 차이: (1) Study 1(B, V, S latent 해석)과 Study 2 틀 (2) teacher 사다리 T_B~T_BVS_SHUF와 cross-attention teacher(02:219~246) 대 Stimulus Model 하나(E2) (3) distillation 손실 MSE(p_S, p_T)(02:268) 대 (1 − α)y + αp_T의 soft BCE(G7) (4) 조건 3개(Direct, Full-guided, Shuffled-guided) 대 5개, student에 feature head와 feature decoding loss가 없음 (5) 469개 지도와 ROI PCA 32(02:132~164) 대 370개 ROI 선형 투영(C4) (6) V-JEPA 2 ViT-L block 6/12/24, 8 fps 16프레임 window(02:192~207) 대 ViT-g 40 block, 4 fps 최대 64프레임(3-2) (7) 주 지표가 영상 안 34개 값의 r을 Fisher z로 모은 것(02:388) 대 정서별 r(2-3) (8) 14-D 독립 학습, encoding 분석(1a, 1b, 2d), Brain-JEPA식 보조 손실은 필수 범위 밖 (9) MC를 학습과 tuning에 쓰지 않음(04 D13) 대 MC 입력층 학습(6-3). "이전 F6 구조"와 "PCA 64"는 docs/archive/pre-final-2026-10에 없다. GPT 10/30 초안에서 온 항목이다. docs/archive/pre-final-2026-10를 경로로 가리키는 곳: 문서 10개(루트 README, AGENTS, CLAUDE, CONTEXT_EMOBRAIN, project/README, project/baseline/README, docs/coordination/README, threads/T004, docs/reports/prelim_2026-10/decisions_proposed, prereg_v2/design_docs/AGENTS), 코드 주석 1줄(project/data/pilot_adapter.py:64), 설정 문자열 1개(project/baseline/brain_decoding/config.json:29). 실행 중에 docs/archive/pre-final-2026-10를 읽는 코드는 없다 | 0절, N37 | 2026-11-03 |
| S0. 기존 코드의 위치와 새 설계에서의 사용 여부 | 분할: archive/project_pre_final/analysis/prelim_2026-10/splits/make_horikawa_split.py, docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv, .json. 고쳐서 쓴다(MC 72개 제외, 1349/1363 묶기, 세션 조건 검사가 없음. 아래 불일치 행). 기록: data/stimulus_crosswalk.tsv, runs.tsv, events_audited.tsv, stimuli.tsv는 그대로 쓴다. events_audited의 duration_sec는 TR 단위 block 길이이고 반복 횟수 기록은 없다. 다시 쓸 논리: project/data/pilot_adapter.py의 load_canonical_map, reserved_contents(MC part == test), compute_run_groups, select_dev_subset. V-JEPA 2: archive/v5_direction_split_20260628/dir3_ccn/study1/code/archive/extraction/extract_video_embeddings.py(16프레임 균등, 마지막 출력만)는 쓰지 않는다. 같은 폴더의 03_extract_layer_embeddings.py(40 block 평균 저장)를 출발점으로, 4 fps 제시 영상 규칙, 64프레임 상한, 가운데 정사각형 자르기, 버전 기록을 더한다. lowlevel_features.py: 33개 추출만 기록용으로 쓰고, 정서 R² 부분과 stage 1의 lowlevel_L 특징은 쓰지 않는다. build_lab_features.py: 캡션 생성 모델 오류는 "일부 캡션 오류 확인됨", "생성 캡션, 검수 전" 두 줄만 기록(9, 109행). run_baselines.py: 469개 지도(roi469, subroi4)로 돌렸다. third_party/GED는 git 밖이다(.gitignore:202, Perlmutter 사본에만 있음, zhongyu1998/GED 3ea8492). 370개 ROI로 다시 돌려야 한다. ML-BVAE, EmoGrowth 구현은 없다. archive의 01_glasser_parcellation.py: 쓰지 않는다(QC에서 실패한 MNI frame을 입력으로 씀, Tian S1을 10개로 가정, 결과 없음). mlp_pooled.sh: 공통 ROI = roi_valid와 유한값 조건의 5명 교집합(469개 중 466개). C6 규칙(HK와 MC 모두, 370개)으로 다시 센다. Brain-JEPA/atlas: Perlmutter EmoDe/Foundation_baseline/Brain-JEPA/atlas, Schaefer400 + Tian S3 = 450개다. 469개 지도는 참가자별 T1w dseg(v3/atlas)다. 둘 다 쓰지 않는다. PREPROC_QC_REPORT(9/28)는 옛 MNI 자료만 다룬다. PRELIM_STAGE0_REPORT(10/22)는 v3_qc 기준 block 수와 라벨 이름 규칙을 적는다 | S0 목록 | 2026-11-03 |
| S0. 자료 경로(voxel 캐시, 사람 평정, 14개 차원, semantic_features.csv, MC 캡션, MC fMRI) | Perlmutter 메인 세션이 /pscratch에서 직접 확인함(11/3). PM = /pscratch/sd/s/sjmoon. HK voxel: PM/Horikawa/sub-0X/v3_qc/ 5명 모두 있다. 파일 11개(blocks_common36_qc_runz.npy, 정규화 전 blocks_common36_qc.npy, samples_qc_usable.tsv, mask_qc.nii.gz, voxel_keep.npy, roi_valid.tsv, samples_qc.tsv, runs_qc.tsv, segments_qc.tsv, QC_SUMMARY.json, SUCCESS.json). 배열(block × voxel, float32): sub-01 2,191 × 202,143, sub-02 2,195 × 183,468, sub-03 2,187 × 164,116, sub-04 2,175 × 198,779, sub-05 2,085 × 199,936. QC 전 결과(v3: atlas/, atlas_counts/, confounds/, timeseries_stim/, code/)와 v2도 PM/Horikawa/sub-0X/에 있다. 전처리 설명 PREPROCESSING_FINAL.md는 Perlmutter에도 있다(PM/Horikawa/, PM/MindCaptioning/). 지도: roi_valid.tsv와 v3/atlas/의 지도 19종(Schaefer 100~400의 7, 17 네트워크판, Tian S1~S4, FSaseg, CerebLobules, Buckner 7, 17, HypoBNSTNBM, HypothalamusNuclei, MASSPsub, 450개와 469개 조합)에 HCP360이 없다(불일치 7). fMRIPrep 해부 결과(PM/Horikawa/fmriprep/horikawa_preprocess_sub0X/fmriprep/output/sub-0X/ses-anatomy/anat/)에는 개인 표면(white, pial, midthickness), fsaverage와 fsLR 등록 구면, T1w와 fsnative, MNI 사이 변환이 있다. FreeSurfer 원 폴더(sourcedata/freesurfer)는 Perlmutter에 없다. 34개 사람 평정: 레포 data/cowen_horikawa_labels.csv(2,185행 = content_id 1~2185, score_0~33과 14개 차원). 연구실 서버 파일의 Perlmutter 사본 PM/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv(2,196행)의 score_0~33은 레포 파일과 2,185개 모두 같다(최대 차이 0). 14개 차원: 레포 csv의 2,185개 모두 값이 있다. "분석 영상 7개에 값 없음"은 라벨을 video_id로 붙일 때 생긴다. 분석 영상 가운데 7개(2186, 2189, 2190, 2191, 2192, 2193, 2196)는 B2에 따라 남긴 먼저 제시된 복사본이고 레포 csv에는 1~2185만 있으므로, 라벨은 content_id로 붙인다. 10월 사전 분석 코드는 video_id 2185 이하로 걸러 이 7개를 빼고 2,174개를 썼다(N1의 노출 기록에 함께 적는다). semantic_features.csv: PM/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/와 출처 /pscratch/sd/t/tylee/Horikawa_Haka/meta/ 둘 다 있고 md5가 같다(2,196행, id 열과 73개). MC 캡션: 레포 caption_ck20.csv와 PM/transfer/emobrain_stimulus_features_20261025/captions/의 사본은 md5가 같다(영상 2,196개 × 20개). MC 시청 fMRI: PM/MindCaptioning/sub-0X/v2_qc/ 6명 모두 있고 HK와 같은 11개 파일 구성이다. 사건 기록은 samples 표(session, run, run_index, onset_sec, duration_sec, part, rep, test_video_in_train_session 등)뿐이다. MC 72개: 목록 파일은 없다. 6명 모두 part == test의 영상이 72개로 같고, 학습 세션 안의 같은 영상 72행에 test_video_in_train_session이 표시되어 있다. 목록은 S1에서 이 표로 만든다. figshare 11988351: PM 아래(깊이 3)에서 찾지 못했다. 영상: PM/EmoViS/data/raw/CowenEmotionVideos에 mp4 2,196개(0001~2196) | N39 | 2026-11-03 |
| S0. 기존 특징 캐시의 상태와 추출 기록 | Perlmutter에서 직접 확인함(11/3). 새 설계(3-2, 3-3, 3-6)에 그대로 쓸 수 있는 캐시는 MPNet 하나이고 나머지는 다시 뽑는다. (1) V-JEPA 2: PM/transfer/emobrain_lab_features_20261026/vjepa2_vitg_final.npy(2,196 × 1,408, 마지막 block, 2186~2196은 1~11의 복사. 체크포인트와 16프레임 균등은 EmoViS 기록 archive/.../dir3_ccn/CLAUDE.md:139~140에만 있음). PM/EmoViS/study1/results/00_embeddings/vjepa2_layerwise/(block 4, 8, 12, ..., 40의 10개, 2,185행. block 10과 30이 없음)와 vjepa2/(마지막 출력). 10월 말 사전 분석용 video_models/vjepa2_win(같은 체크포인트, 2초 window 초당 8장, block 20, 32, 40, info.json에 모델 이름만). 모두 3-2의 규칙(초당 4장, 최대 64프레임, 8초 반복, 가운데 정사각형, 40개 block 저장, O10, O11)과 다르다. (2) DeBERTa-large: 캐시가 없다(PM의 transfer, EmoViS, EmoBrain/project, MindCaptioning 아래 깊이 5에서 찾지 못함). (3) MPNet: caption_human_mpnet.npy(2,196 × 768). 처리는 build_lab_features.py 기록과 같고 7-O 3절의 MPNet 처리와 맞는다. HF revision과 코드 버전 기록은 없다. 정서어를 지운 판 caption_human_noemo_mpnet.npy도 있다(3-4의 SI는 DeBERTa로 다시 낸다). (4) baseline 시각 모델: VideoMAE 캐시(videomae.npy, videomaewin.npy, EmoViS videomae/)는 Kinetics로 미세조정한 videomae-huge라 3-1의 ViT-B/16 사전학습 전용과 다르다. CLIP 캐시(clip_vitl14.npy, clip2fps.npy, EmoViS clip_layerwise/)는 ViT-L/14다(3-1은 MC가 쓴 판, 확인하지 못하면 ViT-B/16). TimeSformer 캐시(timesformer_l12.npy, timesformer_l6.npy, video_models/timesformer 12층)는 facebook/timesformer-base-finetuned-k400로 32프레임 간격과 세 위치 자르기를 따랐지만 8초 반복 영상이 아니라 원 영상에서 뽑았다(O14). DINOv2, X-CLIP, SigLIP2(추출 중단, parts만)는 3-1에서 쓰지 않는다. (5) 저수준: 움직임 에너지(3-6) 캐시가 없고 pymoten도 brainvlm_qwen_env에 설치되어 있지 않다. RGB 중앙값 캐시도 없다. 10월의 lowlevel_motion.npy(28개), EmoViS lowlevel/, sadeghi/는 3-6과 다른 특징이다. (6) 뇌: PM/EmoBrain/project/output/prelim_2026-10/roi_blocks/의 469개 지도 영역 평균은 5-5(370개 ROI의 voxel 입력)와 달라 쓰지 않는다 | 3-2, M2 | 2026-11-03 |
| S0. 설계 동결 commit 해시 | 아직 하지 않음. 석진 님이 "GPT 전체 검증 반영이 끝났다"고 말한 뒤에 한다 | M5 | |
| S1. 34개 라벨 열 대조 결과 | 일치(11/3). score_0~33(이름은 project/shared/data/cowen34_order.txt의 알파벳 순)을 원 범주 이름이 든 Horikawa 형식의 특징 파일 archive/v5_direction_split_20260628/dir3_ccn/data/raw/feature/category.mat(L.feat 2,196 × 34, 0~1, L.featname)의 같은 이름 열과 비교했고 34개 모두 값이 같다(최대 차이 0, content_id 1~2185). 같은 폴더의 categcontinuous.mat는 0~100 척도의 다른 평정이라 같은 이름 열과 r 0.92~0.99로 맞고 다른 이름 열과는 0.77 이하다. 대조표: manifests/s1/label_map_34.tsv, 코드 s1_labels_mc72.py. archive 코드(dir3_ccn/study1/code/archive/legacy_pipeline/21_cca_brain_video.py:36~43)의 다른 34개 이름 목록은 틀린 목록이다 category.mat은 공개 figshare 11988351 feature.tar.gz의 파일과 md5가 같다(11/4) | N2 | 2026-11-03 |
| S1. 파일, 분석 영상, 개발 영상의 실제 수 | 파일 2,196개, 분석 영상 2,181개(분할 파일의 analysis_row이고 exclude_duplicate가 아닌 행), 개발 영상 2,109개(분석 영상에서 MC 72개의 내용에 해당하는 72개를 뺀 것). 개발 영상 목록은 S2의 새 분할에서 만든다 | 0절 | 2026-11-03 |
| S1. 중복 15개의 구성, 분석 영상에 남은 같은 내용 영상 | 같은 content_id인 파일 쌍 15개 모두 먼저 제시된 쪽을 남겼다(B2와 같음, 제시 순서는 run_index와 run 안 순서). 남긴 쪽: 2186(내용 1), 2, 3, 2189(4), 2190(5), 2191(6), 2192(7), 2193(8), 9, 10, 2196(11), 259, 472, 846, 2184(2157). 분석 영상에 남은 같은 내용 영상은 1349와 1363 한 쌍이고 지금 분할에서 fold 4와 5에 따로 있다(S2에서 같은 fold로 묶는다). 표: manifests/s1/duplicates_15.tsv(코드 s1_sets_raters_runs.py) | 0절, B2, O4 | 2026-11-03 |
| S1. MC 72개 목록 파일의 위치와 그 중복 | 목록 파일이 없어 만들었다: manifests/s1/mc_test72.tsv(코드 s1_labels_mc72.py). MC 6명의 samples 표에서 part == test인 영상이 6명 모두 같은 72개다. 같은 내용 영상은 crosswalk의 canonical_stimulus_id로 찾았다. 중복 파일이 있는 시험 영상은 1번 하나(1과 2186)이고, HK 분석 영상에는 B2에 따라 2186이 남아 있다. 72개 모두 HK 분석 영상에 같은 내용이 하나씩 있다. 거의 같은 내용 쌍 1349, 1363은 72개에 없다 | 0절, 6-3 | 2026-11-03 |
| S1. MC 중복 16개와 HK 중복 15개의 차이 | 1363 하나다. PM/MindCaptioning/manifests/stimulus_crosswalk_summary.txt: 내용 기준 교집합 2,180개, "Horikawa에만 [1363]". crosswalk(prereg_v2/manifests, MC 쪽 사본과 같은 생성 코드)는 해시가 같은 15쌍(1~11과 2186~2196, 259/866, 472/859, 846/1673, 2157/2184)에 1363을 1349와 같은 내용(canonical 1349, is_exact_duplicate_file True)으로 더해 canonical 2,180개로 둔다. MC는 1363을 중복으로 뺐고, HK는 B2에 따라 둘 다 남긴다. 1349와 1363은 MC 72개에 없어 시험 영상 제외에는 영향이 없다. 당시 HK 분할(v1)은 1349(fold 4)와 1363(fold 5)을 따로 두므로 S2에서 같은 fold로 묶는다 | B2 | 2026-11-03 |
| S1. 거꾸로 센 평정자 수 17 초과 목록과 중복의 관계 | 영상마다 34개 비율 p에 대해 p × n이 모두 정수에 가까운(차이 2e-3 이하) 가장 작은 n을 1~60에서 찾았다. 2,185개 모두 정해졌고 범위 7~32, 중앙값 13. 9 미만 1개, 9~17 1,565개, 17 초과 619개. 17 초과 619개는 모두 짝수이고 그 절반이 9~17이다(18 14개, 20 21, 22 115, 24 156, 26 221, 28 46, 30 27, 32 19). 같은 수의 평정자 두 집단의 비율을 평균한 값일 수 있지만 확인하지 못했다. 중복 내용과 겹치는 것은 259, 2157 두 개뿐이라 중복으로 설명되지 않는다. B8대로 역산 n은 쓰지 않는다. 표: manifests/s1/rater_count_inferred.tsv | B8 | 2026-11-03 |
| S1. 참가자별 voxel 수(HK 5명, MC 6명) | QC 뒤 voxel 수. HK sub-01 202,143, sub-02 183,468, sub-03 164,116, sub-04 198,779, sub-05 199,936. MC sub-01 195,764, sub-02 175,129, sub-03 200,185, sub-04 156,312, sub-05 176,405, sub-06 177,837. 표: manifests/s1/voxel_counts.tsv(코드 s1_public_checks.py) | 5-5 | 2026-11-04 |
| S1. ROI별 voxel 수 | 공개 ROI 기준이고 지도 결정 전의 값이다(정할 것 5). 표: manifests/s1/original_roi_voxels.tsv(11명 × 370개, 원래 수와 우리 QC mask 안의 수, 코드 s1_original_rois.py). HK 피질 360개의 5명 평균은 92.4~2,121.6개, 중앙값 339.4개로 논문 값(92~2,122, 중앙값 339)과 같다. 즉 논문 값은 피질 ROI 기준이다. MC 피질은 93.0~2,033.7개, 중앙값 318.5개. 피질하 평균(HK sub-03 포함)은 HK 시상하부 96, 측좌핵 597, 편도체 763, 창백핵 890, 미상핵 2,072, 조가비핵 2,426, 시상 2,738, 해마 2,764, 뇌간 5,193, 소뇌 18,712이고 MC 82, 527, 664, 739, 1,760, 1,991, 2,244, 2,317, 4,783, 19,849다. 소뇌 하나가 피질 ROI 중앙값의 약 60배라 S7의 가중치 수에서 따로 본다. 한 voxel이 여러 ROI에 드는 비율은 참가자별 22.85~29.20%다(분모는 ROI에 든 고유 voxel, 피질끼리 겹침도 많음). S6에서 배타적인 라벨로 바꾸지 않고, 가중치 수는 고유 voxel이 아니라 ROI별 voxel 수의 합으로 센다(HK sub-01은 149,203개 대 189,954개). ROI 표의 행은 저자의 voxel 순서이므로 S2에서 좌표로 QC mask의 열 번호에 맞춘다 | 5-5 | 2026-11-04 |
| S1. 피질하 10개의 정의와 출처 | Horikawa 외(2020) 공개 코드의 roiInf.mat으로 확인했다(표 manifests/subcortex_definition.tsv). 10개 모두 좌우를 합친다. AAL(aal_MNI_V4): 시상, 해마, 창백핵, 편도체. Talairach Daemon: 시상하부와 조가비핵(TD_brodmann), 뇌간과 소뇌(TD_hemisphere), 미상핵(TD_label), 측좌핵(TD_brodmann의 brodmann area 34). 판: 공개 ROI가 MNI_atlas_templates 판에 가깝다. fMRIPrep 변환으로 두 판을 옮겨 비교하면 sub-03을 뺀 HK 4명의 24개 비교 중 20개에서 이 판이 높다(소뇌 Dice 0.88 대 0.56, 뇌간 0.78 대 0.67, manifests/td_version_check.tsv, 코드 s1_original_roi_align.py). 이 비교는 PickAtlas의 SPM MNI 공간을 MNI152NLin2009cAsym과 같다고 놓은 것이라, 판을 알아보는 단서이고 저자가 쓴 판의 증명은 아니다 | 5-5 | 2026-11-04 |
| S1. 남은 공통 ROI 수와 결정에 쓴 자료 | 370개(정할 것 5, 6, 11/4 정함). 370은 목표가 아니라 기준을 적용한 결과다. 자료는 피질 저자 지도, 피질하 새 mask(1 mm 중심 방식)와 QC mask의 교집합이고 뇌 반응, 성능은 쓰지 않았다. 표 manifests/roi_final_check.tsv(코드 s1_roi_final_check.py). 11명 모두 mask의 voxel 수가 뇌 배열의 열 수와 같다. 배열의 열 순서가 QC mask의 NumPy 순서라는 것은 전처리 기록(PREPROCESSING_FINAL.md 165행)에 있고 S2에서 이웃 voxel 상관으로 11명 모두 확인했다(S2 분할 행). 가장 적은 곳은 MC sub-05 왼쪽 25번 영역 14개이고 피질하는 MC sub-01 시상하부 25개다. roi_valid 규칙(10개 이상, 20% 이상)이었다면 363개다. MC의 촬영 정보를 HK 입력 정의에 썼다. 점검 범위: 시상, 소뇌, 뇌간의 ±3 voxel 범위 국소 최적 이동은 시상, 소뇌가 1 voxel 이내, 뇌간이 3 voxel 이내다. 경계값 3은 범위 밖을 알 수 없으므로 이것만으로 등록 실패가 없다고 하지 않는다(z축 −40~+40 mm 검색은 6 mm 이내, 정할 것 7). 시상하부는 aseg VentralDC와의 겹침 47~92%로 대략적 위치만 점검했다. VentralDC에는 다른 구조도 들어가므로 시상하부 경계의 정확도는 검증하지 않았다. 이번 aseg에는 별도 시상하부 라벨이 없다. BA34 기반 ROI는 aseg 측좌핵을 0~5% 덮고(분모 aseg 측좌핵), ROI 안에서 aseg 측좌핵에 드는 비율은 0~1.85%다 | C6 | 2026-11-04 |
| S1. 새 지도의 0단계 신뢰도 | HK만 냈다. MC 시험 반응은 최종 때까지 쓰지 않으므로(11/3 석진 님) MC 반복 신뢰도는 내지 않았다. 지도를 정한 뒤의 점검이고 이 결과로 지도를 바꾸지 않는다. 반복 쌍(같은 내용이 두 번 제시된 15쌍에서 MC 72개와 같은 내용 1쌍을 뺀 14쌍, sub-01은 빠진 block 때문에 13쌍): 370개 영역 평균 패턴의 같은 쌍 r 평균 0.228, 다른 쌍 0.010, 짝 찾기 0.723. 묶음별 voxel 패턴의 짝 찾기는 2차 시각 0.838이 가장 높고 Subcortex 0.589, Orbito-Affective 0.503이 가장 낮다. 표 manifests/s2/reliability_hk_repeat_pairs.tsv(코드 s2_manifest.py --stage brain) | 5-5 | 2026-11-04 |
| S1. MC와 HK 참가자 겹침 | 겹치지 않음. docs/archive/pre-final-2026-10/04_DECISION_REGISTER의 D32(10/28 석진 님 확인)에 따르며, Horikawa 2020은 ATR과 교토 Verio, MC는 NTT와 도쿄 Prisma에서 촬영했다. 공개 자료(ds002425, ds005191)에는 participants.tsv가 없어 이 세션에서 표로 대조하지는 못했다. MC S1의 예비 실험 자극 노출은 D32에 따로 있다 | 6-3 | 2026-11-04 |
| S1. HK 참가자 국적 | [미확인]. 공개 README(ds002425)와 공개 코드에 없고, 보충자료는 이 세션에서 열지 못했다(PMC와 Cell 모두 접근 거부) | A9, 2-7 | 2026-11-04 |
| S1. Horikawa 외(2020)의 복셀 선택 규칙, fold 정의, Yeo 17과 주 경사 세부 | 공개 코드 KamitaniLab/EmotionVideoNeuralRepresentation(commit 8fe23a0)로 확인했다. 복셀 선택: ROI마다, 목표마다 학습 자료에서 voxel과 목표의 상관 절댓값 상위 500개를 고른다(nSelectVoxels = 500, ROI voxel이 더 적으면 전부. perform_decoding_analysis.m 140~145행). 정칙화: λ는 logspace(1,4,20), 즉 10~10,000의 20개이고 안쪽 5겹으로 목표마다 고른다(emotion2020_analysis_BATCH.m 96~101행). GPT 11/3 서술과 같다. 주의: 같은 코드는 fold를 나누기 전에 voxel과 목표를 전체 표본으로 z-score한다(perform_decoding_analysis.m 74~76행). fold 안에서 다시 정규화하지만 S5의 복셀 선택 ridge에 전체 z-score를 옮기지 않는다(H5). fold: 연속 run 1~10, 11~20, 21~30, 31~40, 41~50, 51~61이다(run2FoldAssignIdx). 우리 분할과의 차이는 불일치 9. 중복: dupidx = [1, 4:8, 11, 859, 866, 1673, 2157, 2187, 2188, 2194, 2195]로 불일치 3의 15개와 같다. Yeo 17: roiInf.network17, 표면 기반 yeo2011_17_r_lh와 rh의 17Networks_1~17, 양반구를 합쳐 17개. 주 경사: 참가자별 SubjectN_pringrad_values.mat(figshare 11988351)를 그림 코드(draw_figure5GH.m, draw_figure4E_5BCD.m)가 읽는다. 그 값을 만든 코드는 공개 코드에 없다[미확인] | I7, 2-0, 6-4 | 2026-11-04 |
| S1. semantic_features.csv와 공개 자료의 일치, 변환 이력 | 일치. figshare 11988351의 feature.tar.gz 안 semantic.mat(2,196 × 73)과 열 이름, 순서, 값이 같다(최대 차이 1e-16). 값을 바꾼 변환이 없으므로 변환 이력 문서는 필요 없다. 44개 열의 최댓값이 1보다 작고 82%가 0인 것은 공개 자료 자체의 값이다. 표기: 코드 s1_public_checks.py, 공개 파일 사본 PM/atlas_sources/horikawa2020_figshare/ | 4-2, 4-3 | 2026-11-04 |
| S1. V-JEPA 2 공식 평가 설정과 기존 캐시 설정 | facebookresearch/vjepa2의 학습 설정(configs/train/vitg16/pretrain-256px-16f, cooldown-256px-64f)은 crop 256, patch 16, tubelet 2, fps 4, vit_giant_xformers다. 3-2의 초당 4장, 64프레임과 같다. 공식 평가 설정(configs/eval/vitg-384/k400)은 384 해상도 판 기준으로 frames_per_clip 16, frame_step 4, segment 8개, view 3개라 우리가 쓰는 fpc64-256과 다르다. 기존 캐시: facebook/vjepa2-vitg-fpc64-256, 16프레임 균등, 마지막 출력(extract_video_embeddings.py 22~23행). 3-2의 규칙과 달라 다시 뽑는다(S0 행) | 3-2, 부록 3 | 2026-11-04 |
| S1. Horikawa(2025) 공개 코드: DeBERTa 체크포인트와 층 번호, TimeSformer 체크포인트와 클립 구성 | 공개 코드 horikawa-t/MindCaptioning(commit 4c39764). DeBERTa: microsoft/deberta-large, DebertaModel(mcap_utils_demo.py 1341~1354행). 층 번호는 hidden_states[litr + 1], litr = 0~23이라 층 i = i번째 block 출력이고 embedding 출력은 쓰지 않는다. O15와 같다. token 평균은 특수 token을 뺀다(같은 파일 1034~1052행, set_skip_token_ids). 3-3과 같다. TimeSformer: 공개 코드에 추출 코드와 체크포인트 이름이 없다. O14의 클립 구성은 코드로 확인하지 못했으므로 O14대로 "Horikawa(2025)와 같은 처리"라고 쓰지 않는다. 대조 자료: figshare 25808179의 feature.zip(331 MB)에 저자가 낸 deberta-large 24개 층과 timesformer 12개 층의 영상별 특징이 있다. S3에서 우리 추출값과 비교할 수 있다(설계 변경 아님, 아직 받지 않음) | 3-3, O14, O15 | 2026-11-04 |
| S1. CLIP 판, VideoMAE 체크포인트 이름, baseline 모델의 사전학습 전용 가중치 | VideoMAE: MCG-NJU/videomae-base. Hugging Face 설명이 "base-sized model, pre-trained only", Kinetics-400 1,600 epoch 자기 지도 학습이라 O11과 3-1에 맞는다. CLIP: MC 공개 코드에는 언어 모델 후보로 CLIP 텍스트(openai/clip-vit-base-patch32, mcap_utils_demo.py 1291~1295행)만 있고 이미지 쪽 판은 없다[미확인]. 3-1에 따라 OpenAI ViT-B/16을 쓴다. TimeSformer: S0의 캐시는 facebook/timesformer-base-finetuned-k400이고 MC가 쓴 체크포인트는 코드로 확인하지 못했다 | 3-1, O11 | 2026-11-04 |
| S1. 8초 반복의 종료 시점 | 기록으로 확정하지 못했다(불일치 8). events_audited.tsv(5명)에서 8초 미만 영상 1,573회는 블록이 모두 10초다. 8초 이상 영상의 블록은 영상 길이 + 2초를 TR(2초) 단위로 올린 값이다(블록 − 2초 − 영상 길이 = 0.03~2.0초). 시각 기록이 모두 TR 단위라 짧은 영상의 제시가 8초에서 끝나고 2초 쉬었는지, 8초를 넘길 때까지 반복한 뒤 10초 안에서 끝났는지 구별되지 않는다. 표: manifests/s1/presentation_length.tsv | 3-2 | 2026-11-03 |
| S1. Du 외(2023)의 OSF 특징을 받을 수 있는지 | 받을 수 있다. osf.io/9uyn2는 공개이고 Data 폴더에 motion_energy.npy(115 MB), semantic_feature.mat 등이 있다. 아직 받지 않았다. S3의 대조(O12)에서 받는다 | 3-6 | 2026-11-04 |
| S1. 캡션 파일 출처, 영상당 캡션 수, 정서어 181개 목록 | 캡션: 레포 data/caption_ck20.csv는 horikawa-t/MindCaptioning(commit 4c39764)의 data/caption/caption_ck20.csv와 md5가 같다(dd3f4361...). 2,196개 영상 × 20개 = 43,920개, 크라우드소싱으로 사람이 쓴 캡션이다(MC data/README). 정서어: archive/project_pre_final/analysis/prelim_2026-10/features/build_caption_noemo.py의 AFFECT_WORDS, 서로 다른 단어 181개(11/4 다시 셈) | 3-4, 부록 2, 부록 3 | 2026-11-04 |
| S1. MC run 구성, 사건 기록과 반응 추출 코드 | run 구성(QC 전 samples 표): 6명 모두 학습 세션 10개에 run 60개, 시험 세션 2개에 run 10개. 시험 영상 72개는 6명 모두 학습 run의 59, 60번째(run_index 순)에 있다. 나머지 58개 run의 학습 블록이 2,108개(QC 뒤 sub-01 2,103, sub-02 2,108, sub-03 2,106, sub-04 2,107, sub-05 2,108, sub-06 2,081). O29의 검증 run(다섯째마다)은 이 58개 run의 5, 10, ..., 55번째 11개다. 표: manifests/s1/mc_train_runs.tsv. 평가 구간(11/4): samples와 segments 표에는 평가 구간을 가리키는 행이 없다(part는 train, test, baseline뿐). 대신 run 안에서 앞 블록 끝과 다음 onset 사이의 빈 구간으로 찾을 수 있다. sub-01 학습 run은 run마다 2~4개(평균 3.5개), 길이 22초 이상이고, 나머지 블록 사이는 0초다. 시험 run에도 같은 빈 구간이 있다. 블록 반응은 표의 onset과 길이로 [onset + 4초, 끝 + 4초)만 평균하므로, 평가 직전 블록은 마지막 4초가 평가 시작과 시간상 겹친다. 반응 추출 코드는 response_v2.py다. 원 BIDS event와 독립 대조는 하지 않아, 평가 구간 신호가 전혀 없다고 실증한 것은 아니다 | 6-3, O29 | 2026-11-03 |
| S1. 이상 block과 run, sub-05 block 수 | B6 결정(11/3)에 따라 아래 block과 run은 빼지 않고 기록으로만 쓴다. 0단계 정의(raw 블록 voxel 간 표준편차의 강건 z 절댓값 > 5 또는 run 안 z 최대 절댓값 > 15, run은 run 중앙값의 강건 z 절댓값 > 4)를 Perlmutter의 v3_qc 사본에 다시 적용했다. 기준(중앙값, MAD)은 개발 단계에서 쓰는 블록만으로 낸다(11/3 석진 님: MC와 겹치는 것은 뺀다). 그래서 MC 72개와 같은 내용의 블록과 나중에 제시된 중복 블록(참가자마다 84~87개)을 빼고 계산했다. 이상 block은 0단계(모든 블록으로 계산)와 같은 5개다: sub-02 영상 892(ses-06 run-05), 289(ses-07 run-04), 312(ses-07 run-05), sub-03 영상 1158(ses-05 run-05), sub-04 영상 879(ses-07 run-08). 다섯 모두 MC 72개가 아니다. 이상 run은 달라졌다(정할 것 4). sub-03의 ses-05 run-03, 04, 05(run_index 31, 32, 33)가 모두 기준 근처다. 모든 블록으로 계산하면 강건 z가 4.05, 4.00, 3.71이라 run 31이, 개발 블록으로 계산하면 3.93, 3.91, 4.27이라 run 33이 걸린다. 세 run의 FD 중앙값은 0.20~0.27 mm로 높지 않다. QC 뒤 block 수 sub-01 2,191, sub-02 2,195, sub-03 2,187, sub-04 2,175, sub-05 2,085(B7). FD > 0.9 mm block 제거와 상수 voxel 125개 제거는 project/data/qc_exclusions.json에 있다. 표: manifests/s1/abnormal_blocks_hk.tsv(개발 블록 기준, 코드 s1_abnormal_blocks.py) | B6, B7 | 2026-11-03 |
| S1. 뇌 전체 평균과 block 신호 크기의 정의, 참가자 간 일치도의 계산 방법 | 뇌 전체 평균과 block 신호 크기: 정규화 전 block 반응(blocks_common36_qc.npy)의 block마다 voxel 평균과 voxel 간 표준편차(archive/project_pre_final/analysis/prelim_2026-10/prelim/confound_and_block_check.py 169행). 일치도: 영역 평균 반응(run 안 z)에서 5명 공통 영상에 걸쳐 한 명과 나머지 평균의 상관을 영역마다 낸다(brain_reliability.py 133~157행). HK는 5명의 제시 순서가 같아 순서 효과가 섞일 수 있다(PRELIM_STAGE0_REPORT 212행). 이 코드의 HK 계산은 나중 중복만 빼고 MC 72개를 빼지 않았다. S2에서 CAB-NP 13묶음으로 다시 낼 때는 개발 영상만 쓴다(0-3) | I7, K7 | 2026-11-04 |
| S1. 문헌 항목(소리, He 외 2026, DOI, KHBM 마감, 신규성 검색) | He 외 2026은 N39에 확인됨. Cowen 평정자가 소리를 들었는지, Conwell 2025 DOI 연도, GED와 GE-END의 DOI는 레포 기록에서 찾지 못했다[미확인]. KHBM: 2026 추계학술대회 공지 제목만 확인, 초록 규정과 마감은 [미확인]. 신규성 검색은 A4에 11/3 기록이 있다 | 부록 3, N39 | 2026-11-04 |
| S2. 분할 | split_id hk_dev_rungroup6_v4, manifests/s2/split_hk_dev.tsv(개발 영상 2,109개), fold는 통합문서처럼 1~6(불일치 4 해소). run 묶음 45개를 정서 평정과 영상 길이로 층화해 배정했다(정할 것 12, seed 20261106, 뇌 자료는 쓰지 않음). 1349와 1363은 같은 fold 4다(불일치 2 해소). fold별 영상 337, 380, 349, 348, 378, 317개, run 10, 11, 10, 10, 11, 9개. fold 평균과 전체 평균의 차이는 표준편차 단위로 정서 중앙값 0.016, 최댓값 0.070(층화 전 v2 0.027, 0.126, 무작위 run 배정의 중앙값 0.033, 최댓값 0.143), 정서마다 fold당 0이 아닌 영상 최소 17개(v2 15개), 로그 길이 최대 0.041(v2 0.122), 30초 이상 영상 fold당 5, 4, 5, 7, 4, 5개, 16초 이상 19, 11, 12, 13, 15, 16개, 이름표 73개 중앙값 0.035, 최댓값 0.153(맞추지 않음, v2 0.034, 0.144). 표 manifests/s2/fold_balance.tsv. MC 72개와 그 중복은 빠졌다(불일치 1 해소). 참가자별 개발 block은 2,105, 2,108, 2,100, 2,088, 2,001개이고 5명 공통 영상은 1,969개다(manifests/s2/participant_blocks_hk.tsv). fold 역할은 manifests/s2/fold_roles.tsv(H2, O7). 이상 block과 run은 표시만 했다(B6). 열 순서: 직접 근거는 생성 코드의 volume[mask].T(HK response_v3.py 414행, MC response_v2.py 383행)와 QC 열 보존 기록이다. 진단으로 NumPy와 Fortran 두 후보의 공간 연속성을 봤다. NumPy 순서는 11명 모두 세 축의 이웃 voxel 상관이 0.078 이상, Fortran 순서는 세 축 최솟값이 0.011 이하다(HK 개발 block, MC 입력층 학습 block 앞 40개의 정규화 전 평균, manifests/s2/column_order_check.tsv). 모든 열 순서를 배제한 증명은 아니다 | 2-0, B2, H2, O7 | 2026-11-04 |
| S2. 세션 조건 표와 판정 | 통과(O8, 층화 뒤 v4). 참가자, fold마다 시험 run이 6~8개 세션에서 왔고 한 세션에서 온 run은 최대 3개다. 모든 run이 한 세션에서 온 경우는 없다. 표 manifests/s2/session_check.tsv. 통과해도 새 세션으로의 일반화는 검정하지 않는다 | 2-0, O8 | 2026-11-04 |
| S2. 세션별 정서 평균 차이 | 세션 평균과 전체 평균의 차이를 그 정서의 표준편차로 나눈 절댓값이 참가자별 중앙값 0.04, 최댓값 0.16~0.24다(가장 큰 곳 sub-05 joy). 표 manifests/s2/session_emotion_means.tsv, session_emotion_summary.tsv. 분할을 정하는 데 쓰지 않았다 | 2-0 | 2026-11-04 |
| S2. 구역 크기, 대표 이름표, 거리 점검 | 개발 영상 2,109개, KMeans(n_clusters=5, n_init=10, random_state=0), scikit-learn 1.8.0(4-3의 11/2 계산은 1.9.1, 분석 영상 2,181개). 같은 설정으로 다시 돌려 같은 배정임을 확인했다. 구역(크기, 많이 붙은 이름표): 1 633개 People, Indoor scenes, Men / 2 507개 People, Outdoor scenes, Men / 3 367개 Art, People, Indoor scenes / 4 359개 Land animals, Small animals, Outdoor scenes / 5 243개 Outdoor scenes, Daytime scenes, Nature. 거리 점검(구역 제외 대 학습량 대조, 정할 것 8의 표본 방식, 실제 가중치 학습 영상 기준): 구역, fold 30개 조합 모두 거리가 늘었다. 20번 평균의 진단 통계는 비율 최소 1.32(검증 포함 1.34), 구역별 평균 비율 1.67, 1.39, 1.92, 1.87, 1.49, 대조보다 먼 시험 영상 94.3, 87.3, 92.6, 94.0, 86.8%다. 실제 학습에 쓰는 고정 표본은 비율 최소 1.34(구역 2, fold 3. 검증 포함 1.35), 구역별 평균 비율 1.67, 1.39, 1.92, 1.87, 1.51, 먼 시험 영상 93.1, 85.6, 91.6, 93.1, 85.6%다. 구역 배정은 층화 전과 같다. 이 값으로 표본을 다시 뽑지 않는다. 구역 제외의 가중치 학습 영상은 963~1,302개, 검증 영상은 221~346개, fold마다 시험 영상은 31~120개다. 표 manifests/s2/content_blocks.tsv, content_block_distance.tsv, content_blocks_assignment.tsv | 4-3, J2 | 2026-11-04 |
| S2. 구역별 정서마다 0이 아닌 학습 영상 수 | 구역, fold, 정서별 표 manifests/s2/content_block_nonzero.tsv(가중치 학습과 검증을 나눠 적음). 가중치 학습 기준 구역별 최솟값은 구역 제외 31, 48, 53, 45, 66개, 학습량 대조 47, 50, 58, 56, 65개다. 구역을 고정한 뒤에 계산했고 이것을 보고 구역을 바꾸지 않는다 | 4-3 | 2026-11-04 |
| S2. 학습량 대조 표본의 seed | 6-2 학습용 표본 seed [20261104, 구역, fold], 거리 점검 seed [20261105, 구역, fold](numpy default_rng, 학습 fold에서 먼저 뽑고 검증 fold에서 뽑는다). 표본 manifests/s2/content_block_control_samples.tsv(role train, val). 영상 수는 30개 조합 모두 구역 제외와 같다. 참가자별 block 수는 QC로 빠진 block 때문에 달라질 수 있어(차이 최대 학습 10개, 검증 3개) 다시 뽑지 않고 manifests/s2/content_block_participant_counts.tsv에 적었다 | 4-3 | 2026-11-04 |
| S2. 짝 거리 분포, 동점 수, 짝 영상이 빠진 참가자의 쌍 수, 서로가 최근접인 쌍 수 | 방향 있는 짝 2,109개, 거리 중앙값 0.089, 최댓값 0.187. 동점이 있는 영상 1개(영상 ID가 작은 쪽, O9). 순서 없는 쌍 1,690개, 그중 서로 최근접 419쌍. 연결 묶음 419개, 크기 2~24. 빠진 쌍(방향 있는 짝 / 순서 없는 쌍): sub-01 4 / 4, sub-02 1 / 1, sub-03 16 / 12, sub-04 38 / 33, sub-05 186 / 158. 거의 같은 내용인 1349와 1363은 서로 최근접 쌍이다(거리 0.041). 규칙대로 두었고, 자기 자신이 아니므로 뺄 근거가 없다. 표 manifests/s2/pairs_directed.tsv, pairs_unordered.tsv, pair_groups.tsv, pair_missing_counts.tsv | 4-2, O4, O9 | 2026-11-04 |
| S2. CAB-NP 묶음별 ROI 수, 13묶음 참가자 간 일치도 | 배정 출처: ColeLab/ColeAnticevicNetPartition(commit e4ea9fd)의 LabelKey를 HCP 라벨 이름으로 대응했다(PM/atlas_sources/cab_np/). ROI 수: Default 77, Cingulo-Opercular 56, Visual2 54, Frontoparietal 50, Somatomotor 39, Language 23, Dorsal-Attention 23, Auditory 15, Subcortex 10, Posterior-Multimodal 7, Orbito-Affective 6, Visual1 6, Ventral-Multimodal 4. 일치도(0단계 방법, 영역 평균 run 안 z, 5명 공통 개발 영상 1,969개, 한 명 대 나머지 평균, ROI별 5명 평균의 묶음 중앙값): Posterior-Multimodal 0.528, Visual2 0.509, Visual1 0.483, Dorsal-Attention 0.463, Somatomotor 0.323, Language 0.299, Cingulo-Opercular 0.249, Default 0.246, Frontoparietal 0.207, Auditory 0.182, Ventral-Multimodal 0.147, Orbito-Affective 0.142, Subcortex 0.114. HK는 5명의 제시 순서가 같아 순서 효과가 섞일 수 있다. 이 결과로 묶음을 바꾸지 않고, 일치도가 낮은 묶음의 낮은 성능을 정보 없음으로 읽지 않는다. 표 manifests/s2/roi_table.tsv, cabnp_groups.tsv, agreement_hk_13groups.tsv, agreement_hk_roi.tsv. ROI별 voxel 열 번호는 outputs/s2_manifest/roi_voxels/(11명, git 밖), 수는 manifests/s2/roi_voxel_counts.tsv | 6-4, K7, C6 | 2026-11-04 |
| S2. MC 시험 반응 접근 기록 | 11/4 S2의 열 순서 점검 첫 판(s2_manifest.py --stage order, cc82896)이 MC 6명 배열의 앞 40행을 읽었다. MC 배열은 시험 세션이 맨 앞이라 6명 모두 시험 block이었고, 합계 240개, 모두 MC 최종 시험 72개에 드는 영상이다. 정규화 전 평균 패턴의 이웃 voxel 상관을 계산하는 데만 썼다. 사람 평정과 함께 쓰지 않았고, 모델 학습이나 지도, 분할, 묶음 결정에 쓰지 않았다. 보고에 "MC 시험 반응은 읽지 않았다"고 잘못 적었고 Codex가 찾았다(2026-11-05_s2_audit_cc82896.md). 코드를 고쳤다. 반응 배열은 metadata로 허용 행을 정한 뒤 read_rows로만 읽고(HK 개발 block, MC input_train), 허용되지 않은 행은 읽기 전에 멈춘다. stage_check에 시험 행이 배열 앞에 있는 상태의 회귀 검사를 넣었다. 다시 만든 표는 지난 접근을 없애지 않으므로 N1에 기록한다. 같은 이유로 HK 쪽도 고쳤다. 첫 판의 brain 단계와 s1_abnormal_blocks.py는 전체 행을 읽어, 개발에서 빠지는 행(참가자별 84~87개)까지 읽었다. 그중 MC 72개와 같은 내용은 참가자별 70~73개이고 나머지는 나중 중복이다. HK 일치도, 반복 신뢰도, 이상 block 계산에서는 빠져 있었고, 고친 뒤 이 표들은 값이 그대로다. 첫 판 order 단계의 앞 40행에는 참가자마다 MC 72개와 같은 내용 3행이 들어가 이웃 상관 계산에 실제로 쓰였다 | N1, 0-3, 6-3 | 2026-11-04 |
| S2. MC 표 | stage_mc는 반응을 읽지 않고 표만 만들었다. 입력층 학습 run 58개를 O29대로 나눴다(5, 10, ..., 55번째 11개 run이 검증). 고유 영상은 2,103, 2,108, 2,106, 2,107, 2,108, 2,081개, 입력 학습/검증 block은 표 참조. 시험 72개 block은 360, 360, 360, 360, 359, 357개(영상당 4~5회, manifests/s2/mc_test_repeats.tsv). 시험 영상이 든 두 run의 72 block은 쓰지 않는다. MC 영상 2,180개 중 HK 개발에 없는 것은 시험 72개뿐이다. 표 manifests/s2/mc_blocks.tsv, hk_mc_id_map.tsv | 6-3, O29 | 2026-11-04 |
| S3. 실제 Vision feature와 Caption feature 차원 | 영상 2,196개, 모두 float32, 비유한 값 0개. V-JEPA 2 blocks (2196, 40, 1408), 목표 5,632. DeBERTa (2196, 24, 1024), 목표 4,096, 캡션 43,920개(영상당 20개). 정서어 제거판도 같은 크기이고 1,063개 영상의 값이 원판과 다르다. VideoMAE (2196, 4, 768), 목표 3,072. TimeSformer (2196, 12, 768), 목표 3,072. CLIP (2196, 512). MPNet (2196, 768). 저수준 (2196, 6558). 목표가 지정한 층을 이어 붙인 값과 같음을 V-JEPA 2와 DeBERTa에서 확인했다. 시각과 움직임 특징에서 완전히 같은 영상 쌍은 15쌍이고 manifests/duplicates_15.tsv와 정확히 일치한다 | 5-4, D9 | 2026-11-06 |
| S3. 영상별 원래 초당 장 수, 홀수 프레임에서 뺀 장 수, 끝에 맞춘 window 수 | 원래 초당 장 수 1.25~100, 중앙값 14.3, 15 미만 1,238개. V-JEPA 2: N이 64 이하이고 홀수라 한 장 뺀 영상 141개, window로 나뉜 영상 81개, 모두 마지막 window를 끝에 맞췄고 window는 최대 6개. VideoMAE: 모든 영상이 16장을 넘어 window로 나뉘고 끝에 맞춘 영상 576개. 값은 s3_features/<모델>/video_info.tsv | O10, O11 | 2026-11-06 |
| S3. 움직임 에너지 필터 수, Du 외(2023) 특징과의 대조 | 필터 6,555개. Du 외(2023) 공개 특징과의 대조는 Codex가 산출물 검토에서 했다(project/output/audits/codex/2026-11-06_s3_outputs_ef9bd8a.md). 같은 영상 r 중앙값 0.945, 최대 절대 차이 21.2로 같은 값이 아니고 원인은 분리하지 않았다. 저자와 같은 특징이라고 쓰지 않는다 | 3-6, O12 | 2026-11-06 |
| S3. 추출 manifest의 위치 | outputs/s3_features/<모델>/manifest.json(git 무시 대상). 8개 판 모두 추출 커밋 fabb336, 코드 변경 없는 상태에서 추출 | M2 | 2026-11-06 |
| S4. fold별 Stimulus Model의 epoch 수, r, weight decay | | E2, E3, N26, O16 | |
| S5. ridge 정칙화 선택값, 양 끝이 뽑힌 횟수, 실행 시간 | | H3, 3-2, O18 | |
| S6. 조건별 학습 가중치 수 | d = 64 어림에서 입력층 W 57,226,304개, Brain → Emotion 전체 57,423,266개, Brain + Decoded Feature → Emotion(r = 8) 전체 58,481,526개다. 표는 manifests/s6/weight_counts.tsv이고 d는 S7에서 정한다 | F8, 5-5 | 2026-11-08 |
| S7. 파일럿 실행 시간과 메모리 | | N34, 5-4 | |
| S7. G13 수렴 확인 | | G13 | |
| S7. d와 입력층 weight decay의 후보, K | | 5-5, 7-L | |
| S7. ML-BVAE 칸 수 범위 | | 5-2, O28 | |
| S7. 실행량과 예상 GPU 시간 | | 7-L | |
| S9. 짝 연결 묶음의 크기 분포 | | O4 | |
| S10. 순열 p의 계산식과 방향 | 정함: O4 (6) | O4, 6-1 | 2026-11-03 |
| S9. 쌍 비교의 순서 없는 쌍 | 정함: O4 (7). O33은 O4 (7)을 가리킨다 | O33, O4 | 2026-11-03 |
| S7. 실행 사양 동결 commit 해시 | | M5 | |
| S8. fold별 선택값(d, 입력층 weight decay, λ, α, r) | | 5-5, G10 | |
| S8. 0이 뽑힌 fold | | G10 | |
| S8. 미실행 항목 | | G16, L3 | |
| S9. N8에서 평균만 옮긴 차원 수 | | N8, O35 | |
| 파일럿 뒤 구조 변경 | | N34 | |
| 통합문서와 레포의 불일치 | 아래 행들 | 0-2 | 2026-11-03 |
| 불일치 1. 분할 파일에 MC 72개 제외가 없다 | horikawa_rungroup6_v1에는 MC 최종 시험 영상을 표시하는 열이 없고, 72개가 6 fold에 퍼져 있다(내용 기준 72개 모두 분석 영상에 있음. 1번의 같은 내용은 2186으로 남아 있어 video_id로만 세면 71개). 개발 영상 분할을 새로 만들었다(S2 분할 행). 10월 사전 분석은 72개를 포함해 돌았다(N1) | 0절, B1 | 2026-11-03 |
| 불일치 2. 1349/1363을 같은 fold로 묶지 않았다 | crosswalk와 near_duplicate_pairs.tsv:26은 같은 내용으로 보지만 분할은 fold 4와 5에 따로 둔다. 두 제시를 모두 남길지는 threads/T002에서 석진 님 결정으로 남아 있다. 정함(11/3 석진 님): Horikawa 외(2020)처럼 둘 다 분석 영상에 남기고(분석 영상 2,181개 그대로) 같은 fold에 묶는다. S2의 새 분할에 넣었다(S2 분할 행). 01의 0절, 2-0, B2를 고쳤고 03, 04(S1)를 맞췄다(11/3) | B2, 2-0 | 2026-11-03 |
| 불일치 3. 중복 쌍에서 어느 제시를 남기는지 | 분할은 쌍마다 먼저 제시된 쪽을 남긴다. 그래서 1~11과 2186~2196 쌍 가운데 7쌍은 2186~2196 쪽 반응을 쓴다(빠진 것: 1, 4, 5, 6, 7, 8, 11, 2187, 2188, 2194, 2195, 859, 866, 1673, 2157). B2는 "2186~2196 제외"라고 적었다. 라벨은 content_id(1~2185)로 붙으므로 어느 쪽을 남겨도 라벨은 맞는다 | B2 | 2026-11-03 |
| 불일치 4. fold 번호 | 분할 파일의 fold는 0~5이고 통합문서는 1~6이다(H2, O7). 구현은 "통합문서의 fold k = 파일의 fold k − 1"로 옮긴다. ex) O7의 fold 1 = 파일의 fold 0 | H2, O7 | 2026-11-03 |
| 불일치 5. 영상당 반응을 평균하는 구간 | 정함(11/3 석진 님): 반응을 다시 추정하지 않고 01 C1의 문구를 고친다(02, 03, 04를 맞춤). 평균 구간: Horikawa 외(2020) Transparent Methods는 신호를 4초(volume 2개) 밀어 "영상 제시 구간과 뒤따르는 2초 휴지" 블록 안에서 평균했다(Mac 세션 11/3 확인). PM/Horikawa/PREPROCESSING_FINAL.md 2.3절 5번의 v3_qc 구간 [onset + 4초, onset + 블록 길이 + 4초)도 같은 블록이다. PMC 본문은 "volumes measured over the course of each video presentation were shifted by 4 s and averaged"까지만 적어, Perlmutter 세션은 보충자료를 직접 확인하지 못했다. 정규화 대조: 원문은 블록 평균 뒤 영상 전체에 걸쳐 voxel마다 z-score했고(Mac 세션 확인), v3_qc는 같은 run의 블록들로 voxel마다 z-score했다(같은 문서 6번). run 안 z도 시험 run은 그 run 자체의 통계로 정규화된다. 정규화는 C1의 결정이고, 원문과 표준화 범위(영상 전체 대 run 안)가 다르다는 점을 방법 절에 적는다(11/3 석진 님) | C1, C5 | 2026-11-03 |
| 불일치 6. pilot 코드가 MC 참가자를 거부한다 | project/baseline/brain_decoding/config.json:29와 pilot_adapter.py:64는 "MC는 학습과 tuning에 쓰지 않는다"(옛 D28)를 따른다. 6-3은 MC 입력층을 MC 시청 자료로 학습한다. 다시 쓸 때 이 제한을 고친다 | 6-3 | 2026-11-03 |
| 불일치 7. 개인 공간의 HCP360 지도가 없다 | 전처리 결과의 지도 19종(v3/atlas/, roi_valid.tsv)에 HCP360이 없다. 11/4에 정할 것 5, 7로 바뀌었다(피질은 저자 공개 ROI, 피질하는 11명 모두 새로 만듦). 11/3의 결정은 원문 방식을 따르는 것이었다. 원문은 fsaverage 표면의 HCP360 label을 FreeSurfer로 개인 표면에 옮기고 FSL flirt로 2 mm voxel에 다시 보간했다(fsLR이 아님). 피질하 10개는 WFU PickAtlas의 AAL과 Talairach Daemon mask를 표준 공간에서 개인 T1w로 옮겨 2 mm로 다시 보간했고, 측좌핵은 Brodmann area 34다(Mac 세션이 Transparent Methods로 11/3 확인). 원문 기준 ROI당 voxel 수는 92~2,122개, 중앙값 339개(5명 평균). 01 5-5를 고치고 02, 03, 04(S1)를 맞췄다 | 5-5, C2, S1 | 2026-11-03 |
| 불일치 9. fold 정의 | Horikawa 외(2020) 공개 코드의 fold는 연속 run 1~10, ..., 51~61이다. 우리는 2-0(11/1 결정)대로 같은 내용이 든 run을 묶어 fold에 배정하고 세션 조건을 더한다. 그래서 fold 구성이 다르다(manifests/original_folds.tsv). 공개 코드는 1349와 1363을 다른 fold(1, 4)에 두고, 우리는 B2대로 같은 fold에 묶는다. 설계를 바꾸지 않고 방법 절에 차이를 적는다. 01 2-0의 "Horikawa의 fold 정의는 보충자료를 확인하지 못함" 문구는 이 행으로 고칠 수 있다 | 2-0, B2 | 2026-11-04 |
| 불일치 8. 8초 반복의 종료 시점 | 01 3-2와 PREPROCESSING_FINAL.md는 "8초를 넘을 때까지 반복"이라고 적었다. 그런데 events_audited.tsv에서 8초 미만 영상의 블록(제시 + 휴지)은 모두 10초다. 8초를 넘길 때까지 반복했다면 7초 영상은 14초를 제시해야 해서 블록 10초 안에 들어가지 않는다. 그래서 제시는 블록 10초 안에서 잘렸다. 8.0초에서 자르고 2초 쉬었는지, 10초 안의 다른 시점에서 잘렸는지는 TR 단위 기록으로 알 수 없다. 특징 추출(S3)에 넣을 "참가자가 본 영상"의 길이가 이 값에 달려 있다. 공개 자료(11/4): OpenNeuro ds002425의 events.tsv도 duration이 TR 단위(8초 미만 영상은 10초)이고 README에 반복 규칙이 없다. 원문 문구를 11/5에 확인했고 정할 것 11에서 8.0초로 정했다 | 3-2, O10 | 2026-11-05 |
| N1. 11/3 KHBM 초록용 분석의 노출 | 설계 동결 전에 개발 영상 2,108개(MC 72개와 1363 제외)의 시험 fold 결과를 봤다. 조건 비교, 더하기 head와 상호작용 head, 바꿔 끼우기와 정서별 경로 차이, 선택된 λ, α, r. 입력은 466개 영역 평균, 특징은 V-JEPA 2 마지막 block과 MPNet, 모델은 작은 MLP로 본 실험과 다르다. 설계와 후보값을 이 결과로 고르지 않았고, 보류된 결정 1~4의 근거로 쓰지 않는다. 코드 archive/project_pre_final/analysis/prelim_2026-10/perlmutter/khbm_pilot.py, 결과 project/output/prelim_2026-10/17_khbm_pilot/. 10월 말 위계 분석(16_hierarchy)도 같은 성격이다 11/4 S2 열 순서 점검 첫 판은 MC 6명의 시험 block 240개의 정규화 전 반응을 읽었다(S2 MC 시험 반응 접근 기록 행) | N1, M6 | 2026-11-04 |
| 통합문서로 정할 수 없던 것 | 아래 행들 | 0-2 | 2026-11-03 |
| 정할 것 1. 중복 쌍에서 남길 제시 | 정함(11/3 석진 님): (가) 먼저 제시된 쪽을 남긴다. Horikawa 외(2020) Methods가 같은 규칙이다("discarded samples that were presented later in the experiment"). 지금 분할이 이 규칙이므로 바꾸지 않고, 01의 B2를 고쳤고 02, 03, 04를 맞췄다(11/3) | B2 | 2026-11-03 |
| 정할 것 2. H2 검증 fold의 사람 평정이 Stimulus 예측 평정을 거쳐 Brain Model 학습에 들어간다 | E4와 O16은 Stimulus Model의 fold 밖 출력을 D_k의 5개 fold 전체로 만든다. 그래서 학습 영상의 Stimulus 예측 평정을 낸 안쪽 모델 가운데 4개는 H2 검증 fold의 사람 평정으로도 학습한다. 뇌 모델이 이 점수로 학습한 뒤 같은 검증 fold로 α와 조기 종료를 정하면, Brain → Emotion [distillation]이 들어간 조건만 검증 점수에서 유리해질 수 있다. 시험 fold로 새지는 않는다. 옛 규칙(docs/archive/pre-final-2026-10/04 C01, 02:78~110)은 Stimulus Model을 검증 fold 밖에서 다시 만들어 이를 막았다. 정함(11/3 석진 님): Brain → Emotion [distillation]에 쓰는 Stimulus 예측 평정은 H2의 학습 fold 4개 안에서만 안쪽 4겹으로 만든다. 검증 fold와 바깥 시험 fold는 Stimulus Model의 학습, 설정 선택, 조기 종료에 쓰지 않는다. 01의 E4, O16, H3, 5-0을 고쳤고 02, 03과 04의 0-3 표, S4를 맞췄다(11/3) | E4, O16, H2 | 2026-11-03 |
| 정할 것 3. 원문 방식의 지도를 만들 재료와 도구 | 11/4 정할 것 5로 대체됐다. FreeSurfer 폴더 전송, HCP360 annot, FLIRT는 쓰지 않는다. 11/3 기록: 내려받기 허락, FreeSurfer 폴더는 석진 님이 연구실 서버에서 옮긴다. (1) HCP360: figshare의 "HCP-MMP1.0 projected on fsaverage"(Mills, 2016, doi 10.6084/m9.figshare.3498446.v2)의 lh, rh.HCP-MMP1.annot을 PM/atlas_sources/hcp_mmp1_fsaverage/에 받았다(md5가 figshare 값과 같음, 꼭짓점 163,842개, 반구마다 영역 180개와 미지정 1개). 원문이 같은 파일을 썼는지는 [미확인]. (2) WFU PickAtlas: NITRC(group 46)는 로그인이 필요해, Codex가 공개 사본 UMPsychMethodsCore/MethodsCore(commit 1cff4ae)의 3.0.5b를 PM/atlas_sources/wfu_pickatlas/WFU_PickAtlas_3.0.5b_MethodsCore/에 받았다(출처 기록 CODEX_* 파일). 검증(11/3, PM/atlas_sources/README.md): 두 번째 공개 사본 superkeyor/SPMJobs12와 지도 파일 122개가 같은 내용이다(11개는 줄바꿈 방식만 다름). AAL은 GIN의 aal_for_SPM12(2015) ROI_MNI_V4.nii와 116개 영역의 voxel 구성과 이름이 모두 같다(저장 방향과 라벨 번호만 다름). 공식 배포본 대조(11/4): 석진 님이 NITRC에서 받은 3.0.5b를 PM/atlas_sources/wfu_pickatlas/official/에 두었다. 공통 파일 435개 중 421개는 바이트까지 같고 14개는 줄바꿈 방식만 달라, 사본에 내용 차이가 없다. AAL과 Talairach Daemon 두 판의 지도도 모두 같다. 이후 코드는 공식본 경로를 쓴다. Talairach Daemon 지도는 두 판(MNI_atlas_templates, TD-ICBM_MNI_atlas_templates)이 있고 파일이 다르다. 공식 설명서는 MNI_atlas_templates만 적고, 저자 공개 ROI도 이 판에 더 가깝다(S1 피질하 행). (3) FreeSurfer 폴더: HK는 처음 fMRIPrep 실행의 /storage/bigdata/Horikawa/fmriprep/horikawa_preprocess_sub0X/fmriprep/output/sourcedata/freesurfer/sub-0X(fmriprep_sdc 실행이 여기서 복사함), MC는 /storage/bigdata/MindCaptioning/fmriprep/sub-0X/output/sourcedata/freesurfer/sub-0X(fMRIPrep 기본 위치로 추정, [미확인]). 받는 곳: PM/Horikawa/freesurfer/sub-0X(5명), PM/MindCaptioning/freesurfer/sub-0X(6명), fsaverage는 PM/Horikawa/freesurfer/fsaverage. (4) 도구: shifter의 nipreps/fmriprep:25.0.0 이미지에 FreeSurfer 도구(mri_surf2surf, mri_label2vol, recon과 같은 7.3.2 판, PREPROCESSING_FINAL.md 2.2절)와 FSL FLIRT 6.0이 있다(11/3 확인). 원문과 같은 도구로 할 수 있다. | 5-5, 불일치 7 | 2026-11-03 |
| 정할 것 4. B6의 이상 block과 이상 run | 정함(11/3 석진 님): 빼지 않는다. 01 B6을 고쳤고 02, 03, 04(S1, S2)를 맞췄다. 기준값의 출처: 5(블록 신호 크기), 15(run 안 z 최대 절댓값), 4(run)는 0단계 점검 코드(archive/project_pre_final/analysis/prelim_2026-10/prelim/confound_and_block_check.py:178, 206, 10/22)가 정한 값이고 근거 문헌이나 이유가 기록되어 있지 않다. 0단계 기록은 이 표시를 "표시만 했고 제외 안 함"(stage1/00_status/zero_handoff.tsv:8)으로 다뤘다. B6이 이 표시를 제외 기준으로 옮겼고, B6의 이유 칸 "움직임 지표(FD, DVARS) 기준"은 실제 정의(블록 신호 크기, run 안 z)와 다르다. MC와 겹치는 블록을 빼고 다시 내면 이상 run이 sub-03 run_index 31에서 33으로 바뀐다(S1 이상 block 행). FD와 DVARS 비교(개발 블록 안의 백분위, manifests/s1/abnormal_motion_check.tsv, 코드 s1_abnormal_motion.py): 블록 892(sub-02) FD 0.276 mm 89%, DVARS 1.431 84%. 289(sub-02) FD 0.313 mm 93%, DVARS 1.553 97%. 312(sub-02) FD 71%, DVARS 3%. 1158(sub-03) FD 24%, DVARS 50%. 879(sub-04) FD 22%, DVARS 73%. run(sub-03 run 61개 안의 백분위): 31 평균 FD 0.193 mm 77%, 평균 DVARS 41%, 최대 FD 1.19 mm(volume 2.2% 검열, 그 근처 블록 2개는 이미 FD QC로 빠짐). 32 FD 69%, DVARS 5%. 33 FD 21%, DVARS 7%. 다섯 블록과 세 run 모두 이미 적용된 QC 기준(블록 반응 구간의 FD > 0.9 mm, run 평균 FD > 0.5 mm 등, PREPROCESSING_FINAL.md 1.2절)을 넘지 않는다. 289가 가장 높지만 FD 0.31 mm다. 석진 님 지시(11/3): 뚜렷한 원인(움직임, 신호 급변)이 있는 것만 그 이유로 빼고, 원인이 없으면 반응 크기 기준으로는 빼지 않는다(despike만) | B6 | 2026-11-03 |
| 정할 것 5. ROI 지도의 출처 | 정함(11/4 석진 님): (나). 피질 360개는 공개 ROI, 피질하 10개는 11명 모두 같은 절차로 새로 만든다. 01의 5-5를 고쳤고 02, 03, 04를 맞췄다. 근거, 발견(11/4): 공개 자료에 저자가 쓴 참가자별 ROI가 voxel 좌표와 함께 있다(HK figshare 11988351의 fmri_SubjectN_Session1.h5 metadata, MC figshare 25808179의 testPerception_SN.mat metainf). 370개 모두 있고 11명 모두 좌표가 우리 T1w 2 mm 격자 간격에 맞는다(최대 잔차 2e-6 voxel, manifests/original_roi_grid.tsv). 격자에 맞는 것과 촬영 범위 안에 있는 것은 다르다. 격자 밖 voxel이 HK sub-02에 71개, sub-03에 6,589개 있다. 받은 파일의 판과 md5는 manifests/original_roi_sources.tsv다. 피질 360개의 합집합은 FreeSurfer aseg 피질과 안 옮겼을 때 가장 잘 맞고(11명 모두, Dice 0.67~0.72) HK voxel 수가 논문 값과 같다. 개별 영역의 경계까지 검증한 것은 아니다. 피질하는 aseg로 비교할 수 있는 8종에서 10명에게 큰 위치 이상이 없다(ROI별 10명 평균 Dice 0.47~0.82, z축으로 옮겨도 가장 좋은 위치가 6 mm 이내). 시상하부와 측좌핵(BA34)은 aseg에 없어 이 비교에 들어가지 않는다. HK sub-03만 어긋난다. 그대로는 해마 Dice 0.00, 소뇌 0.05다. z축으로만 옮겨 찾으면 해마 +24, 시상 +20, 편도체 +16, 창백핵 +12, 조가비핵 +8, 미상핵 +4, 뇌간 +24, 소뇌 +32 mm에서 가장 좋지만 그래도 Dice 0.21~0.57이라 단순 이동으로 복구되지 않는다. 격자 안의 소뇌 voxel 1,870개는 다른 사람의 약 12분의 1이다. 격자가 작아서 생긴 일은 아니다(공개 해마 3,582개 중 3,572개가 격자 안인데 aseg 해마와 겹치는 voxel이 0개). 피질은 정상이다. 이것은 현재 격자에서 공개 sub-03 피질하를 그대로 쓸 수 없는 정렬 이상이고, 어느 단계가 원인인지는 미확인이다. 선택지: (가) 피질 360개와 피질하(10명)는 공개 ROI를 쓰고, sub-03 피질하만 같은 지도(PickAtlas MNI_atlas_templates, AAL)와 fMRIPrep 변환으로 새로 만든다 (나) 피질은 공개 ROI, 피질하는 11명 모두 새로 만든다 (다) 정할 것 3대로 FreeSurfer부터 모두 새로 만든다. 새로 만드는 방법은 정할 것 7이다. 공개 mask를 임의로 옮겨 쓰지 않는다. 다른 선택지로 자동 전환하는 규칙도 두지 않는다. (가)와 (나)는 FreeSurfer 폴더 전송이 필요 없다. | 5-5, C6, 정할 것 3 | 2026-11-04 |
| 정할 것 6. 공통 ROI의 기준 | 정함(11/4 석진 님): (가). 370은 목표가 아니라 이 기준을 적용한 결과다. 01의 C6를 고쳤다. 근거: C6는 "해부학적 mask와 촬영 범위의 교집합"이라고만 적었고 voxel 수 기준이 없다. (가) QC mask 안에 voxel이 있으면 유효, 참가자별 남은 voxel 수와 비율을 기록한다. 지금 공개 mask로 370개 (나) 전처리의 roi_valid 규칙(10개 이상, 20% 이상). 지금 362개, sub-03 수정 뒤 363개로 예상한다. 지금은 모두 14개 이상이라 차이는 사실상 20% 기준이다. 이 기준이 신호 품질을 보장한다는 근거도, 14개가 충분하다는 근거도 없다. (나)는 MC sub-04, sub-05 등의 일부 영역 때문에 OFC와 25번 등이 11명 모두에서 빠진다. (가)는 그 token이 그 사람에게 남은 부분의 신호이지 영역 전체가 아니라는 한계를 네트워크 분석과 전이 해석에 적는다. 수는 S1 공통 ROI 행 |
| 정할 것 7. 피질하를 새로 만드는 방법 | 정함(11/4 석진 님): PickAtlas MNI_T1.nii 직접 등록, overlap_2mm. 측좌핵 ROI는 표와 논문에서 "BA34 기반 ROI"라고 부르고 원자료 키 nuc_accum과의 대응은 유지한다. 근거. 공간: PickAtlas 설명서는 지도를 SPM MNI 기준이라고 적고, fMRIPrep 변환은 MNI152NLin2009cAsym 기준이다. 두 공간을 같다고 놓을 근거가 없으므로 fMRIPrep 변환을 쓰지 않고, PickAtlas의 MNI_T1.nii(moving)를 개인 T1w(fixed)에 ANTs로 직접 등록한다(antsRegistrationSyNQuick.sh 기본값 -t s, 참가자당 2~3분). 복셀화 후보: 미리 정한 둘은 코드 이름 nn_2mm(2 mm 격자로 최근접 이웃)와 overlap_2mm다. overlap_2mm의 실제 정의는 라벨을 T1w 1 mm 격자로 최근접 이웃으로 옮기고, ROI에 속한 1 mm voxel의 중심이 드는 2 mm voxel을 포함하는 것이다. 정확한 부피 교차 판정이 아니다. 결과(manifests/subcortex_rebuild_check.tsv, 코드 s1_subcortex_rebuild.py): HK sub-03의 overlap_2mm는 aseg와 Dice 해마 0.64, 시상 0.80, 소뇌 0.86, z축 최적 위치 −2~0 mm이고 QC mask 안의 시상하부 37개, 측좌핵 349개다. 나머지 10명에서 aseg 8종의 평균 Dice는 공개 mask 0.62, nn_2mm 0.66, overlap_2mm 0.65이고 z축 최적 위치는 각각 6, 8, 6 mm 이내다. 공개 mask 대비 크기는 ROI별 10명 평균 기준 nn_2mm 0.21~0.93배, overlap_2mm 0.52~1.03배이고, 개인 × ROI 전체로는 0.156~1.008배, 0.444~1.169배다. 공개 mask와의 Dice는 ROI별 10명 평균 기준 nn_2mm 0.31~0.86, overlap_2mm 0.54~0.87이다. aseg는 사람 평정이 아니고 지도 정의도 달라 이 차이로 어느 mask가 더 정확하다고 하지 않는다. 시상하부와 측좌핵(BA34)은 aseg 비교에 없다. 크기 진단(manifests/subcortex_size_check.tsv, 코드 s1_subcortex_size_check.py): 같은 변환으로 ROI를 선형 보간하고 보간값 기준을 바꾸면 시상하부가 0.5 이상 10.5개, 0.25 이상 27.5개, 0.1 이상 49.3개, 0.001 이상 79.7개다(공개 84.5개). 0.001 이상이면 ROI별 10명 평균 크기가 공개 mask의 0.92~1.13배이고 공개 mask와 Dice는 0.71~0.90이다. 보간값은 부피 겹침 비율이 아니다(Codex 반례, 실제 겹침 0에서 보간값 0.125). 크기가 경계 처리에 민감하다는 것과 경계 처리로 크기 차이를 설명할 수 있다는 근거이고, 저자의 실제 처리와 차이의 기여량, 남은 차이의 원인은 미확인이다. 0.001 기준은 채택하지 않는다. 크기를 본 뒤 저자 크기에 맞추려고 더한 기준이고, ROI 범위 밖 voxel까지 포함할 수 있으며, (나)의 이유인 절차 통일에는 저자 크기에 맞출 필요가 없다. 새 mask가 공개 mask보다 작다는 것만으로 잘못이라고도, 맞다고도 하지 않는다. (나)에 overlap_2mm를 고른 것은 정확도 측정의 결론이 아니라 11명에게 같은 절차를 쓰고, 규칙이 명확하며, 추가 기준을 고르지 않는다는 방법 선택이다. "원문 재현"이라고 쓰지 않는다. fMRI 해상도가 1 mm가 되는 것이 아니고, 작은 ROI의 경계 voxel에는 주변 조직 신호가 섞일 수 있으므로 시상하부 token을 순수한 시상하부 신호로 해석하지 않는다. 실행 기록: 등록과 크기 진단은 login21에서 돌렸다(등록 3명씩 병렬, 8 thread, 약 12분). 이런 가볍고 간단한 계산은 로그인 노드에서 바로 돌려도 된다(11/4 석진 님) | 5-5, 정할 것 5 | 2026-11-04 |
| Codex 검토(S1 ROI 결정) | 보고서 project/output/audits/codex/2026-11-04_s1_roi_decisions_3a71fd59.md. 반드시 고칠 것 4개를 모두 받아들였다. (1) sub-03 피질하와 (2) 공간과 복셀화는 정할 것 5, 7로 남는다. (3) 이동 검사의 경계 감김은 좌표 이동으로 고쳤고 큰 이동 진단을 코드에 넣었다(s1_original_roi_align.py). 값은 z축 검색으로 다시 냈다. (4) 실패 전파와 완전성 검사를 고쳤다(두 .sh의 set -e, summary의 11명 × 370개 검사, 코드와 mask 해시로 건너뛰기, manifests/original_roi_sources.tsv). 추출은 다시 돌리지 않았다. 수치가 바뀌지 않고, 좌표는 ijk와 affine으로 되살릴 수 있다. npz의 affine과 shape는 다음 추출부터 들어간다. Codex 첫 판단은 결정 1, 2 모두 (가)였다. 추천을 알고 검토했으므로 맹검 검토는 아니지만, 코드와 mask를 따로 계산해 수치를 재현했다. 후속 보고서 2개(2026-11-05_s1_roi_followup_d307d7f.md, s1_boundary_rule_c26d05c.md)의 설명 정정을 정할 것 7에 반영했다. Codex의 최신 의견은 (나)에 overlap_2mm다 | 정할 것 5, 6, 7 | 2026-11-04 |
| 정할 것 8. 학습량 대조와 H2의 연결 | 정함(11/5 석진 님): (가). 01의 4-3, J3과 02, 03, 04를 고치고 표본과 거리 점검을 다시 만들었다. 경위: 4-3의 학습량 대조는 시험 fold를 뺀 영상에서 구역 제외 학습과 같은 수를 뽑는다. 그런데 H2는 그중 다음 fold를 검증으로 떼므로, 실제 가중치 학습 영상 수는 30개 조합 중 28개에서 달라진다(최대 23개, 중앙값 5개, 학습 958~1,259개 기준. ex) 구역 1, 시험 fold 1은 구역 제외 965개, 대조 978개). 선택지: (가) 학습 fold 4개와 검증 fold에서 각각 구역 제외 조건과 같은 수를 뽑아 학습, 검증 수를 모두 맞춘다 (나) 지금 표본을 쓰고 수 차이를 보고한다. (가)가 영상 수 차이를 줄이려는 대조의 목적에 맞다. 정서별 학습 사례 분포와 참가자별 QC 결측 차이는 남으므로, 성능 차이를 내용 차이만의 영향으로 분리하지 않는다(01의 4-3). 뇌 반응과 성능은 보지 않았다 | 4-3, H2 | 2026-11-04 |
| 정할 것 9. MC 시험 영상의 반복이 4회인 경우 | 정함(11/5 석진 님): (가). 원 논문과 같이 같은 영상의 반복을 평균한다. 원문(Horikawa, 2025, doi 10.1126/sciadv.adw1464)은 5회 평균이라고 적었고, 키워드로 찾은 범위에서 움직임으로 block을 뺀다는 문장은 없다. 4회는 우리 움직임 QC에서 생겼으므로 남은 반복을 평균한다. 4회인 영상은 4로 나누고, 참가자, 영상별 반복 수를 manifests/s2/mc_test_repeats.tsv에 적었으며, 평균 구현은 시험 단계에서 이 표를 따른다. 경위: 6-3은 5회 반복 평균이라고 적었다. QC 뒤 MC sub-05 영상 219, sub-06 영상 189, 1594, 1642는 4회만 남았고, 72개 영상은 모두 있다. 선택지: (가) 남은 반복으로 평균하고 영상을 유지하며 목록을 적는다(B7의 있는 block만 쓴다와 같은 원칙) (나) 5회가 모두 남은 영상만 평가한다. 표는 metadata만 봤고 MC 시험 성능을 보기 전에 정했다. 4회 평균의 정밀도가 5회와 같다고 주장하지 않는다 | 6-3, B7 | 2026-11-04 |
| Codex 검토(S2) | 보고서 project/output/audits/codex/2026-11-05_s2_audit_cc82896.md. 판정: 핵심 manifest와 수치는 재현됐고, S2 전체 통과는 아니다. 반드시 고칠 것: (1) MC 시험 반응 접근은 고쳤다(S2 MC 시험 반응 접근 기록 행). (2) 학습량 대조는 정할 것 8, (3) MC 4회 반복은 정할 것 9로 남았다. 보완: 열 순서 표현과 평가 구간 표현을 고쳤고, provenance에 QC mask, samples, ROI 파일과 산출물 해시를, stage_check에 MC와 ROI 파일 검사를 넣었다. 재검토(2026-11-05_s2_fix_aa6f48c.md): 응답 접근 수정은 통과, S2 전체는 두 결정 반영과 표 재생성 뒤 확인. 재검토의 숫자 정정은 S2 MC 시험 반응 접근 기록 행에 반영했다. Codex는 고친 항목만 다시 본다 | 0-3, 4-3, 6-3 | 2026-11-04 |
| Codex 재검토(S2, 05a7d96) | 보고서 project/output/audits/codex/2026-11-05_s2_recheck_05a7d96.md. 판정: 이번 S2 변경 코드와 실제 표의 검산은 통과했다. S3와 이후 구현을 통과시킨 판정은 아니다. 실제 뇌 반응은 읽지 않았다. 반드시 고칠 것: Claude Code의 보고 문장 "성능 차이를 내용을 뺀 효과로 읽을 수 있다"는 01의 4-3보다 강해 철회한다. 쓸 수 있는 범위: 학습과 검증의 영상 수를 각각 맞춘 무작위 대조와 내용 구역 제외 조건을 비교한다. 정서별 학습 사례 분포와 참가자별 QC 결측 차이는 남으므로, 성능 차이를 내용 차이만의 영향으로 분리하지 않는다. 보완 반영(11/5): (1) stage_check가 반복표의 참가자 행 전체 누락과 중복을 잡지 못했다. 전체 키 일치와 중복 검사, 잘못된 표를 실제로 거절하는지 보는 검사를 넣었다. (2) 1.33은 20번 평균의 진단 통계이고 실제 고정 표본의 최솟값은 1.30이다. 고정 표본의 거리를 표에 더했고 표본은 바꾸지 않았다. (3) 거리 동률 허용 오차 1e-12를 넣었다. 대조보다 먼 시험 영상의 비율이 구역 4 fold 4와 구역 5 fold 5에서 영상 1개씩 줄었다. 진단 값이고 표본과 결정에는 영향이 없다. 미반영: 03의 419행 5회 평균 문장은 11/5 갱신 규칙에 따라 동결 때 고친다. 아직 확인하지 않은 것: MC 실제 평균 계산과 시험 forward(후속 코드) | 4-3, 6-3, S2 | 2026-11-05 |
| Codex 재검토(S2, 756fb35) | 보고서 project/output/audits/codex/2026-11-05_s2_recheck_756fb35.md. 판정: 코드와 표의 검산은 통과. S3 이후와 긴 영상 평균의 예측상 타당성을 승인한 것은 아니다. 실제 뇌 반응은 읽지 않았다. 반드시 고칠 것 1건을 고쳤다(11/5): 16초 이상(87개), 16초 초과(86개), 64프레임 초과(81개)를 구별하고, window 기준을 프레임 수 N으로, 홀수 처리는 N이 64 이하일 때만으로 적었다(O11의 문장 순서와 "프레임을 버리지 않고"를 따른 해석이다. 달라지는 영상은 N = 65인 338 하나다). 층화의 16초 이상 지표는 그대로 두고 "window로 나뉘는 영상"이라는 설명만 뺐다. 보완 반영: 코드 머리말의 옛 분할 설명, 04의 옛 "지금" 표현, MC 차이의 "마지막 약 2초" 표현을 고쳤다. Claude Code의 보고 문장 "어느 fold도 특정 정서나 긴 영상에 치우치지 않는다"는 범위를 넘어 철회한다. 쓸 수 있는 범위: 정한 균형 지표가 개선됐고 크기와 세션 조건을 통과했다. 긴 영상 시간 비율은 16초 초과 원 영상 기준으로 개발 영상 17.3%다(앞서 보고한 17.5%는 16초 이상 기준). 미확인: 제시 로그, 평균 특징의 실제 손실, S3 이후 | 2-0, O11, S2 | 2026-11-05 |
| 정할 것 10. K1a Stimulus Model의 설정 선택 경로 | 정함(11/5 석진 님): (나). 학습 횟수는 learning rate 후보를 넣은 뒤(11/6) 1,362회다. 아래의 462회는 그 전 값이다. 범주를 맞힐 때와 같게 한다("14개 정서 차원도 범주 맞힐 때랑 동일하게"). 01의 K1a, H3, 7-L과 04의 S4를 고쳤다. 경위: 11/5 결정문의 두 문장이 서로 다른 규칙을 가리켜 이 항목만 반영을 멈췄다. "설정 선택과 조기 종료는 H2의 검증 fold를 쓴다"와 "head는 K1의 Stimulus Model과 같고, 그 밖의 학습 설정은 Stimulus Model와 같다"이다. Stimulus Model와 K1 head는 H2가 아니라 H3, O16, O17을 따른다. D_k 안쪽 5겹의 평균 곡선으로 후보와 epoch 수를 정하고 D_k 전체에서 다시 학습한다. 선택 기준(14개 차원 r 평균)과 조기 종료 기준(MSE)은 두 경우 모두 같고, 시험 fold는 어느 쪽도 쓰지 않는다(H5). 선택지: (가) H2의 검증 fold 하나. 학습 fold 4개로 학습하고 고른 모델을 그대로 시험한다. 학습 90회(후보 15개 × 6 fold). 정서와 차원 ridge의 주 비교판, 뇌 모델과 같은 검증 fold를 쓰고, 그 fold가 head 학습에 들어가지 않는다. 대신 head의 학습 자료가 K1 head보다 한 fold 적고, 선택이 fold 하나에 달리며, Stimulus Model에 없는 값을 새로 정해야 한다(O16은 300 epoch 곡선의 최저점을 쓰고 patience가 없다. G13의 patience 30은 뇌 모델 값이다). (나) H3, O16, O17을 그대로 쓴다. 학습 462회(후보 15개 × 안쪽 5겹 × 6 fold + 최종 모델 2개 × 6 fold). K1 head와 학습 경로가 같고 새로 정할 값이 없다. (나)는 결정문의 "K1과 같다"를 그대로 지키고 새 값을 만들지 않는다. 뇌를 받지 않는 작은 모델이라 학습 수 차이의 부담이 작을 것으로 본다(실행 시간은 재지 않았다) | K1a, H2, H3, O16, O17, G13 | 2026-11-05 |
| S0. 14개 차원 사람 평정 파일과 평정 신뢰도(B4, K1a) | 사람 평정 파일을 확인했다(11/5). data/cowen_horikawa_labels.csv의 *_score 열 14개(arousal, dominance, valence, approach, attention, certainty, commitment, control, effort, fairness, identity, obstruction, safety, upswing)이고 2,185행에 결측이 없다. 개발 영상 2,109개의 content_id가 모두 있다. Perlmutter의 PM/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv와 같은 2,185개의 값이 모두 같다(최대 차이 0). 확인 때 2,185개 전체(MC 72개 포함)의 차원별 최소, 평균, 최대를 봤고 뇌 반응과 성능은 보지 않았다. 평정 신뢰도: 개별 평정이 없어 계산할 수 없다(원문은 평균 평정만 요청 가능, 01의 2-6). Cowen & Keltner(2017)의 PMC 본문에서 14개 차원의 신뢰도 값을 찾지 못했다. 본문 뒤쪽 일부와 보충자료는 직접 읽지 못했으므로 값이 없다고 단정하지 않고 [미확인]으로 둔다 | B4, K1a | 2026-11-05 |
| 정할 것 11. 8초 미만 영상의 제시 종료 시점 | 정함(11/5 석진 님): (가) 8.0초에서 자른다. 01의 3-2와 D4, 04의 S3를 고쳤다. 원문 문구를 확보했다(11/5. Codex가 찾았고 Claude Code가 같은 PDF를 받아 확인했다). Horikawa 외(2020) Supplemental Information(mmc1.pdf) 15쪽, Transparent Methods의 Experimental design: "For stimulus blocks with videos shorter than 8 s, the same video stimulus was repeatedly presented until the total presentation duration went beyond 8 s. For stimulus blocks with videos longer than 8 s, the video stimulus was presented once and followed by ~2-s rest period so that the total duration of each stimulus block can be divided by 2 s (TR). All stimulus blocks were followed by an additional 2-s rest period." 마지막 반복을 어디서 끝냈는지는 적혀 있지 않다. 문구와 기록을 함께 보면 다음과 같다. (1) 모든 자극 block 뒤에 2초 휴지가 있고, 8초 미만 영상의 block은 모두 10초이므로 자극 block은 8초로 읽힌다. 길이 경계에서도 7.98초 영상은 10초, 8.00초 영상은 12초(8 + 약 2 + 2)다. (2) 마지막 반복을 끝까지 재생했다면 파일 1,573개 모두 8초를 넘어 2초 휴지를 더하면 10초를 넘는다. 휴지를 줄였다고 해도 557개(35%)는 10초 안에 들어가지 않는다. 그래서 끝까지 재생은 기록과 맞지 않는다. 남는 불확실성: 문구가 8.0초를 직접 쓰지 않았고, TR 단위 기록으로는 8초보다 조금 길게 재생되어 휴지가 그만큼 짧았을 가능성을 없앨 수 없다. 선택지: (가) 8.0초에서 자른다. 장 수는 O10대로 floor(8 × f)이고 초당 4장이면 32장, 초당 15장이면 120장이다. 분석 영상의 72%(1,564개)에 적용된다. 방법 절에는 문구와 기록에서 추론한 값이라고 적는다. (나) 연구실 서버의 제시 로그나 제시 코드(/storage/bigdata/Horikawa/raw, 이 세션에서 접근할 수 없음)를 먼저 확인하고 정한다. 추천은 (가)다. 문구와 기록을 함께 만족하는 가장 단순한 값이고, 제시 길이를 코드 한 곳에서 받게 만들면 나중에 로그가 나와도 다시 뽑을 수 있다. | 3-2, O10, O12, D4, 불일치 8 | 2026-11-05 |
| 정할 것 12. 분할에 정서 평정과 영상 길이 층화 넣기 | 정함(11/5 석진 님): 다시 짠다. 정서만 맞춘 v3 뒤에 길이도 맞추라고 정해 v4로 확정했다(v3는 30초 이상 영상이 fold마다 1, 9, 5, 5, 6, 4개로 쏠렸다). 결과는 S2 분할 행. 경위: 11/5 석진 님 지적: 분할은 정서 평정을 보고 fold마다 고르게 나눠야 한다. 층화 전 분할(v2)은 영상 수만 맞췄고 정서 평정을 쓰지 않았다. 6/22 지시("stim 은 stratified sampling")가 01 2-0에 옮겨지지 않은 채 v1을 그대로 썼다. 영상 단위로는 나눌 수 없다. 이웃 block의 혈류 반응이 섞이지 않게 run 단위로 나누기 때문이다(2-0). 그래서 run 묶음 45개(33~103개 영상)를 fold에 배정하는 층화만 가능하다. v2의 상태(개발 영상, 정서 평정만 사용, 뇌 반응과 성능은 보지 않음): fold 평균과 전체 평균의 차이는 정서 표준편차 단위로 중앙값 0.027, 최댓값 0.126이다. run을 무작위 배정한 300번의 중앙값은 0.033, 최댓값의 중앙값은 0.143이라 무작위 수준이다. 정서가 0이 아닌 영상은 fold, 정서마다 최소 15개다. 미리보기(세션 조건 없이 영상 수 ±10%, 정서 평균만 맞춤): 중앙값 0.016, 최댓값 0.070, fold 영상 317~378개, 0이 아닌 영상 최소 13개. 무작위 배정과 미리보기는 임시 스크립트의 진단(무작위 seed 0)이라 커밋된 코드로 재현되지 않으며, 분할을 정하는 데 쓰지 않았다. 평균만 맞추면 드문 정서의 수가 줄 수 있어 기준에 함께 넣어야 한다. 다시 나누면 S2의 fold에 달린 표(짝, 대조 표본, 거리, 세션 표)를 다시 만들고 Codex 재검토를 그 뒤에 한다. 내용 구역 배정은 fold와 무관하다 | 2-0, H1, O8, S2 | 2026-11-05 |
| 정할 것 13. MC 영상의 반복 길이 | 정함(11/5 석진 님): (가) MC에도 HK와 같은 8.0초판 특징을 쓴다. 10초판을 따로 뽑지 않는다. 경위: MC 참가자는 10초보다 짧은 영상을 10초를 넘을 때까지 반복해서 봤다(Horikawa, 2025: "videos shorter than 10 s were repeated until the total duration exceeded 10 s"). 선례: Horikawa(2025) 본문의 특징 계산은 영상마다("For each video") 프레임을 고르고 8개 미만이면 "to cover the entire video length"로 뽑으며, Horikawa 외(2020)도 "all frames"를 "within each video" 평균했다. 두 본문 모두 특징 계산에서 제시 반복을 재현한다는 문장은 찾지 못했다(키워드 검색, 공개 코드는 확인하지 않음). 그래서 MC만 제시 길이에 맞춰 따로 뽑는 근거가 없고, HK로 학습한 모델과 같은 특징을 유지한다. 한계: MC의 실제 반복 제시 시간축을 그대로 재현한 특징은 아니다. 8~10초 영상도 MC에서는 반복됐고 HK 특징에는 반복이 없다. 방법 절에 적는다. 별도 기록: 우리 3-2의 "8초 반복을 재현해 특징을 뽑는다"는 두 원 논문 본문의 서술과 다르다. 11/5 보고했고 석진 님이 유지로 정했다. 차이는 방법 절에 적는다 | 3-2, O30, 6-3, 정할 것 11 | 2026-11-05 |
| S3. 코드와 시험 실행 | 코드 src/s3_common.py, s3_vision.py, s3_text.py, s3_lowlevel.py, s3_collect.py와 각 .sh. 뇌 반응과 사람 평정은 읽지 않는다. 복호기: 시스템 ffmpeg에 h264 복호기가 없어 PM/swift_PTL2/bin의 ffmpeg, ffprobe 7.0.2를 쓴다(prereg_v2 기록과 같은 복호기). 파일 2,196개 모두 복호 프레임 수와 프레임 시각 수가 같고 8초 미만 1,573개는 초당 4장에서 32장이다. stimuli.tsv의 n_decoded_frames와 다른 영상: 649(41 대 181), 1643(421 대 1,402)은 예전 기록이 프레임을 채워 넣은 값이고 실제 프레임은 앞의 수다. 745, 850, 1420, 1875, 1951은 packet 수가 복호 프레임 수보다 많아 packet이 아니라 복호 프레임의 시각을 쓴다. 11/5 Codex 지적으로 코드를 고쳤다(Codex 검토 S3 행). 아래 CPU 시험은 고치기 전 코드의 기록이다. 저자 특징 대조는 본 추출 뒤 s3_author_check.py로 전체를 다시 낸다. 저자 특징 대조(figshare 25808179 feature.zip, 영상 1~40): DeBERTa 층 6, 12, 18, 24의 영상 평균이 저자 값과 소수 넷째 자리까지 같다(최대 차이 0.0000, 같은 영상 r = 1.00000, 다음 영상 r 0.83~0.94). 영상 순서도 같다. TimeSformer 층 12는 짧은 영상 8개에서 저자 값과의 r 중앙값이 반복 재현 0.915, 반복 없음 0.920, 다른 영상 0.643이다. 같지 않고 두 입력의 차이도 작아 저자가 반복을 재현했는지 이 값으로는 정할 수 없다. O14대로 "Horikawa(2025)와 같은 처리"라고 쓰지 않는다. 체크포인트가 다를 수도 있다(04 S1). CPU 시험: V-JEPA 2(영상 2개, 65프레임 두 window 포함), VideoMAE, TimeSformer, CLIP, DeBERTa, MPNet, 저수준 모두 차원이 맞고 NaN이 없다. 시험 결과는 지웠다. CPU에서 V-JEPA 2는 영상 2개에 91초다(GPU 시간은 아직 재지 않았다). 받은 파일: microsoft/deberta-large, MCG-NJU/videomae-base, openai/clip-vit-base-patch16 가중치, pymoten 0.1.3(PM/pydeps/pymoten에 따로 설치) | 3-2, O10~O15, M2 | 2026-11-05 |
| Codex 검토(S3 코드, e09c351) | 보고서 project/output/audits/codex/2026-11-05_s3_code_e09c351.md. 판정: 미통과. 반드시 고칠 것 4건을 모두 받아들여 고쳤다. (1) 반복 경계: np.mod의 부동소수 오차로 정확한 반복 시작 시각에 마지막 프레임이 골라졌다(ex) 영상 243의 4.0초). 시간 계산으로 4 fps 46개 영상 51시점, 15 fps 104개 영상 156시점에 해당한다. 경계를 먼저 처리하게 고쳤고, 8초 미만 파일 전체를 정확한 분수 계산과 비교해 어긋난 시점이 0이다. (2) 화면 순서: 문서는 줄인 뒤 가운데 자르기인데 코드는 반대였다. 문서대로 고쳤다. RGB 중앙값만 원래 화소에서 낸다. 보간 방식도 체크포인트 설정 값으로 맞췄다(이전 코드는 모두 bicubic). (3) 출처: 조각마다 사양 번호를 넣고, 사양이 다른 조각은 건너뛰지 않고 멈춘다. 커밋하지 않은 코드로는 본 추출을 시작하지 않는다. 추출 커밋과 모으는 커밋을 따로 적고, 영상별 원래 프레임 수를 video_info.tsv에 남긴다. (4) 수집 검사: RGB NaN, window별 값의 NaN과 누락, 평균과 window 평균의 불일치, 정서어 제거판과 캡션별 파일 누락, 캡션 영상 번호 오류, MPNet 값 오류를 거절한다. 회귀 시험 s3_tests.py 29개 통과. 캡션 추출은 이어 뽑지 않고 끊기면 처음부터 돌린다고 설명을 고쳤다 | 3-2, O10, O13, M2 | 2026-11-05 |
| Codex 재검토(S3 코드, 74ba7e2) | 보고서 project/output/audits/codex/2026-11-05_s3_recheck_74ba7e2.md. 판정: 미통과. 반복 경계, 화면 순서, 시각과 저수준 조각의 출처, 수집 오류는 수정을 확인했다. 반드시 고칠 것 2건을 받아들여 고쳤다. (1) 캡션 출처: 계산이 끝난 뒤 커밋과 해시를 읽어, 계산 중에 코드나 캡션이 바뀌면 나중 값이 기록되고 수집을 통과했다. 계산 전에 커밋, 코드 해시, 캡션 내용, 정서어 목록을 고정해 그 내용으로 처리하고, 저장 전에 코드와 입력이 바뀌었으면 저장하지 않고 멈춘다. 커밋만 바뀐 경우는 실행 커밋을 그대로 두고 저장 때의 커밋을 따로 적는다. (2) 저자 특징 비교: NaN이 있으면 차이 비교가 거짓이 되어 통과했다. 입력의 NaN과 무한대를 거절하고, 판정을 NaN도 실패로 잡히는 식으로 바꾸고, 상수 벡터 수를 따로 적는다. 보완 반영: 화면 시험을 화소 비교로 바꿔 옛 순서를 잡게 했고, 시험 자료의 해시를 맞춘 뒤 영상 번호와 NaN 검사를 직접 시험하고, 커밋 전 코드로 뽑은 결과를 수집이 거절하게 했으며(시험에서만 S3_ALLOW_DIRTY_COLLECT=1), TimeSformer의 화면 기록을 세 위치로 고치고, 01 3-2에 RGB 예외를 적었다. 회귀 시험 45개 통과. DeBERTa 저자 대조의 합격 기준은 최대 절대 차이 1e-3 이하다 | 3-2, O13, M2 | 2026-11-05 |
| Codex 재검토(S3 코드, 26f0160) | 보고서 project/output/audits/codex/2026-11-05_s3_recheck_26f0160.md. 판정: 미통과. 계산 중 입력 변경 차단, NaN 거절, 커밋 전 출력 거절, 화면 시험과 문서 수정은 확인했다. 반드시 고칠 것 2건을 받아들여 고쳤다. (1) 출처 고정 시점: 모델을 불러오는 동안 코드가 바뀌면 나중 커밋과 해시가 기록됐다. 코드를 불러온 순간의 커밋과 해시(s3_common의 START_HEAD, START_CODE)를 쓰고, 모델을 불러온 뒤 계산 전에 다시 비교해 멈춘다. 같은 구간이 있던 시각과 저수준 추출의 사양에도 적용했다. (2) 저자 비교: 상수 행을 지운 뒤 다음 영상을 정해 비교 대상이 달라졌다. 원래 순서에서 짝을 먼저 정하고, 상수 여부를 행의 값 범위로 판단하고, 유효한 짝이 없으면 계산 불가로 적는다. 절대 차이 판정은 그대로다. 보간: Codex도 체크포인트 설정의 보간을 추천했다. 보간 종류와 정규화는 체크포인트 설정을, 화면 범위는 프로젝트 공통 규칙을 따른다. 영향을 재지는 않았다. 보간은 체크포인트 설정 값으로 정함(11/6 석진 님) | M2, S3 | 2026-11-06 |
| S3. 화면 크기(11/6 석진 님) | V-JEPA 2가 주 모델이므로 그 모델의 공식 입력 처리를 따른다. 짧은 변 292에서 가운데 256을 자른다. 이전 코드는 공통 화면 범위를 위해 짧은 변 256에서 256을 잘랐다. 01 3-2의 "같은 화면 범위" 규칙을 고쳤다. 설정 파일은 공식 입력 처리의 값이고, 학습 때의 전처리와 완전히 같다고 확인한 것은 아니다. 움직임 에너지는 모델 입력이 아니라 짧은 변 전체를 쓴다 | 3-2, O10 | 2026-11-06 |
| Codex 재검토(S3 코드, 7187a31) | 보고서 project/output/audits/codex/2026-11-06_s3_recheck_7187a31.md. 판정: 통과. 지난번 필수 지적 두 건(코드를 불러오는 동안 바뀌는 경우의 출처 기록, 저자 비교의 다음 영상 짝)이 고쳐졌다. 시험 52개 통과 | M2 | 2026-11-06 |
| Codex 재검토(S3 코드, 218c9bc) | 보고서 project/output/audits/codex/2026-11-06_s3_recheck_218c9bc.md. 판정: 통과. 반드시 고칠 것 없음. 시험 57개 통과. 출처, 저자 비교, 화면 크기(짧은 변 292에서 가운데 256 등)를 합성 입력과 합성 모델로 확인했다. 실제 사전학습 모델의 전체 추출, GPU 시간과 메모리, 화면 변경이 성능에 주는 크기는 확인 범위 밖이다. 보완 사항 한 건(01 3-6의 옛 "같은 화면 범위" 문장, 3-2의 약 88%가 변 길이 기준임)을 01에 반영했다 | 3-2, 3-6, M2 | 2026-11-06 |
| S3. GPU 시간 측정 | 코드 scripts/s3_timing.sh. 무작위 영상 30개(seed 20261106, 길이 평균 6.3초, 전체 평균 6.6초)와 가장 긴 영상 879번(90초)을 시각 모델 넷으로 뽑는다. 결과는 s3_timing 폴더에 따로 저장한다. 측정값은 실행 뒤 적는다 | N34 | 2026-11-06 |
| S3. 추출 완료와 시간 | 11/6 로그인 노드 GPU에서 bash로 실행했다(석진 님). 모델별로 시작부터 저장까지 V-JEPA 2 약 1시간 43분, VideoMAE 약 21분, TimeSformer 약 26분, CLIP 약 18분(동시 실행, 공유 GPU). 저수준은 CPU 동시 10개로 약 35분. 시간 측정(s3_timing.sh)의 GPU 메모리 최대 13,128 MiB | N34, M4 | 2026-11-06 |
| S3. 저자 공개 특징 대조 | manifests/s3/author_feature_check.tsv. DeBERTa 네 층: 2,196개 모두 같은 영상 r 1.000, 최대 절대 차이 0.00003으로 일치한다. TimeSformer: 같은 영상 r 중앙값(다음 영상 r 중앙값)이 층 3 0.668(0.425), 층 6 0.982(0.957), 층 9 0.991(0.967), 층 12 0.927(0.695)이고 값이 같지 않다. 8초 이상이라 반복하지 않은 영상에서도 r이 크게 오르지 않아 반복만으로 설명되지 않는다. 저자 추출 코드가 공개되지 않아 원인은 확인하지 못했다. TimeSformer는 baseline이고 저자와 같은 특징이라고 쓰지 않는다 | O14, M2 | 2026-11-06 |
| S4. 코드와 합성 자료 시험 | 코드 src/s4_common.py, s4_feature_model.py, s4_ridge.py, s4_window_change.py, s4_collect.py, s4_tests.py와 각 .sh. 합성 자료 시험 107개 통과(11/6, B1~B5 반영 뒤). 실제 사람 평정과 뇌 반응은 읽지 않았고 실제 결과를 내지 않았다. 실제 자료로 돌리려면 설계 동결 커밋을 주어야 하며 없으면 멈춘다. window 사이 변화량의 지표: 개발 영상으로 표준화한 좌표의 block 10, 20, 30, 40에서, 한 영상 안 window 쌍의 코사인 거리 평균을 그 영상과 다른 개발 영상 500개(seed 20261106) 사이 거리의 중앙값과 비교한다(결정 문서 B4에서 확인받는다). 무작위 숫자로 잰 학습 한 번(300 epoch, 입력 5,632와 4,096차원, 영상 1,400개, batch 64)은 CPU 8 thread로 약 25초다. GPU 시간은 재지 않았다 | S4, O16, O22, 3-2 | 2026-11-06 |
| Codex 검토(S4 코드, a81231f) | 보고서 project/output/audits/codex/2026-11-06_s4_code_a81231f.md. 판정: 수정 후 재검토. 합성 실행으로 시험 fold, H2 검증 사람 평정, MC 경계와 OOF의 가중치 학습 제외는 확인됐다. 반드시 고칠 것 3건을 고쳤다. (1) 코드만 같으면 입력이 달라도 옛 결과를 재사용하던 것: 코드, 입력 파일, S2 표, 설정, 동결 커밋을 묶은 실행 번호로 비교하고, 입력 해시를 읽기 전에 내어 읽은 뒤와 저장 전에 다시 본다. (2) NaN 예측을 선택 점수 0으로 처리하던 것: 입력, 표준화, 손실, 예측, 가중치의 NaN과 Inf에서 저장 전에 멈추고, 유효한 점수가 없으면 첫 후보를 고르지 않는다. (3) 시험 예측의 누락과 중복을 허용하던 것: 모든 과제를 정해진 시험 영상과 정확히 대조하고 평가에도 그 목록만 쓴다. 보완 2건도 반영했다(D12 시험 예측과 정서어 제거 ridge의 λ 저장, window 변화량의 계산 불가 건수). 실제 결과가 오염됐다는 지적이 아니라 잘못된 입력에서 멈추지 않는다는 지적이다. 시험 96개 통과. OOF는 가중치 학습에서 fold 밖 값이지만 설정 선택에는 그 fold가 함께 쓰인다는 점은 O16의 설계이고 01에 이미 적혀 있다 | M1, M2, O6, O16, O20, 4-3 | 2026-11-06 |
| Codex 재검토(S4 코드, f92e422) | 보고서 project/output/audits/codex/2026-11-06_s4_recheck_f92e422.md. 판정: 필수 2, 3번은 수정 확인, 1번은 수집 단계에 한 경로가 남았다. 수집이 입력을 파일 경로로 비교해, 내용이 다른 특징 사본을 쓴 fold 결과가 섞여도 통과했다. 고쳤다: 입력을 역할 이름(시각 목표, 원 캡션, 정서어 제거 캡션, 사람 평정, S2 표)으로 기록하고 경로와 상관없이 역할별 내용 해시를 대조한다. 같은 과제의 설정도 대조한다. 보완 사항인 예측 배열의 전체 크기 검사도 넣었다(한 열이 34개 정서로 복제되는 경우). 시험 102개 통과 | M1, M2 | 2026-11-06 |
| 결정 문서 B1~B5(11/6 석진 님) | B1 6-3 전용 Stimulus 예측 평정을 만들지 않음(01 E4, 코드에서 hkfinal 삭제). B2 Stimulus Model의 intercept에 weight decay를 적용하지 않음(01 O16, 코드). B3 initialization, last batch, seed 하나, 300 epoch 후 평균 곡선 선택을 유지하고 근거 수준을 01 O16에 적음. 고른 epoch가 300인지 표에 적음(selection 표의 at_cap). B4 window 사이 cosine distance는 점검표로만 씀. B5 D12의 R²는 모은 시험 영상의 평균 기준. 뇌 모델의 intercept는 보류된 결정 3과 함께 정한다. 01, 04의 "window"을 window로 바꿨고 02, 03은 동결 때 맞춘다 | E4, O16, O22, 3-2 | 2026-11-06 |
| 결정 C1~C12(11/6 석진 님) | C2 Stimulus Model의 learning rate를 1e-4, 1e-3, 1e-2 후보로 넣는다(후보 45개, Stimulus Model 학습 약 18,700회, 코드 반영). C4 표준화를 모델마다 그 학습 자료로 맞춘다(N3를 고침, Codex 11/6과 저자 코드 근거). 안쪽 validation 영상의 feature와 14개 차원 사람 평정이 들어가던 것을 뺐다. C7 λ를 저자 공개 decoding 코드의 10^1~10^6 로그 간격 10개로 맞춘다(논문 본문의 encoding 설명과 코드가 달라 코드를 따른다). 나머지 C1, C3, C5, C6, C8, C10, C12는 문서대로다. 시험 114개 통과. 같은 표준화 원칙을 S5의 ridge와 S6의 뇌 모델에도 적용한다(아래 행) | E3, N3, O6, O16, O18, C5, D9 | 2026-11-06 |
| Codex 재검토(S4 코드, 2382f73) | 보고서 project/output/audits/codex/2026-11-07_s4_recheck_2382f73.md. 판정: 범위 통과, 반드시 고칠 것 없음. 그 뒤 C2, C4, C7로 코드를 다시 바꿔 그 부분의 재검토가 필요하다 | M1, O16 | 2026-11-06 |
| Codex 재검토(S4 코드, 6338375) | 보고서 project/output/audits/codex/2026-11-07_s4_recheck_6338375.md. 판정: 범위 통과, 반드시 고칠 것 없음. 보완으로 표준화 설명의 옛 문구를 고쳤다. 표준화 규칙 N3을 S5 ridge와 S6 뇌 모델에도 적용하기로 정했다(11/6 석진 님, Codex 동의) | N3, C5, D9, O30 | 2026-11-06 |
| S5. 코드와 합성 자료 시험 | 코드 src/s5_common.py, s5_decoding.py, s5_baselines.py, s5_collect.py, s5_tests.py와 각 .sh. 합성 자료 시험 115개 통과(11/7, Codex 재검토 반영 뒤). 실제 사람 평정과 뇌 반응은 읽지 않았고, 동결 커밋 없이는 실제 자료로 돌지 않는다. 순열 검정과 편상관은 S10에서 한다. block 신호 크기는 prelim_2026-10/prelim/confound_and_block_check.py 169행과 같게 QC mask 전체의 voxel 평균과 표준편차다. **정할 것:** (1) Horikawa 2020 ridge의 ROI ensemble(공개 코드의 안쪽 r 0.095 이상 ROI 평균)을 주 비교값으로 쓸지. 기준을 넘는 ROI가 없을 때 코드는 시험 성능이 가장 높은 ROI를 쓰는데, 시험 정보를 쓰지 않도록 안쪽 r로 바꿨다. (2) 이 기준선의 시간(CPU 8 thread 상한 추정 약 22시간)이 커서 필수 범위와 L3 순서를 어떻게 둘지. (3) 뇌 입력 기준선의 intercept(보류된 결정 3과 함께). (4) 길이와 저수준 기준선을 주 비교판 규칙으로 개발 영상 전체에 대해 fold마다 하나씩 학습하는 가정. 실제 크기 파일과 GPU 시간은 확인하지 않았다 | I7, I10, O18, O23, O24 | 2026-11-06 |
| Codex 검토(S5 코드, a078190) | 보고서 project/output/audits/codex/2026-11-07_s5_code_a078190.md. 판정: 수정 후 재검토. 정상 자료의 ridge 계산은 독립 계산과 맞았다. 반드시 고칠 것 5건을 고쳤다. (1) 수집이 지금 입력과 같은 과제의 설정을 대조하지 않던 것(역할별 내용 해시와 설정 대조, 수집 중 변경도 저장 전에 멈춤). (2) 영상 식별의 눈금에 그 참가자에게 없는 영상이 들어가던 것(그 참가자의 D_k로 맞춤). (3) 상수 벡터의 식별을 0점으로 처리하던 것(규칙이 없어 오류로 멈춤). (4) 안쪽 fold 밖 예측과 λ 선택 기록이 없어도 완료되던 것(과제별 필수 파일과 배열 검사). (5) 음수와 중복 qc_row를 허용하던 것(반응을 열기 전에 멈춤. 지금 표에는 이상이 없다). 보완도 반영했다: S5에 결정적 모드 연결(GPU 동작은 미확인), h2020이 원문 재현이 아닌 점을 코드에 적음, 실행 안내의 sbatch와 bash 구분. 시험 108개 통과 | M1, N3, O19, O32, O34 | 2026-11-06 |
| Codex 재검토(S5 코드, 7bca72a) | 보고서 project/output/audits/codex/2026-11-07_s5_recheck_7bca72a.md. 판정: 1, 2, 3, 5번 수정 확인, 4번의 수정이 새 오류를 만들었다. 수집이 Horikawa ridge의 기준 통과 ROI 수 0을 거절해, 기준을 넘는 ROI가 없어 안쪽 r이 가장 높은 ROI를 쓴 정상 결과에서 멈췄다. 고쳤다: 0을 허용하고 실제 함수에서 저장과 점검까지 잇는 시험을 넣었다. 보완으로 λ 번호의 NaN과 소수도 막았다. 시험 115개 통과 | I7, M1 | 2026-11-07 |
| Codex 재검토(S5 코드, ccf3495) | 보고서 project/output/audits/codex/2026-11-07_s5_recheck_ccf3495.md. 판정: 범위 통과, 반드시 고칠 것 없음. 실제 크기 파일과 GPU 동작은 확인 범위 밖이다 | I7, M1 | 2026-11-07 |
| 결정(11/7 석진 님) | 뇌 모델의 learning rate를 모든 조건의 후보로 넣는다(01 G13, 7-L 실행량을 고침). Horikawa 2020 ridge를 baseline으로 둔다(I7). 문서 위치는 docs/final이고, 옛 docs/current를 docs/archive/pre-final-2026-10으로 옮겨 CLAUDE.md, AGENTS.md, README.md, CONTEXT_EMOBRAIN.md, project/README.md, docs/coordination/README.md의 경로를 고쳤다. AGENTS.md의 역할 문구는 CLAUDE_EmoBrain 5절을 가리키게 했다. 02, 03의 경로는 동결 때 맞춘다. 보류된 결정 3(weight decay 범위)은 아직이다 | G13, I7, 7-L, N37 | 2026-11-07 |
| 결정과 코드(11/7 석진 님) | soft BCE 선형은 learning rate와 weight decay의 9개 조합에서 고른다(코드 반영, 시험 116개 통과). 길이와 저수준 기준선은 바깥 fold마다 공통 모델 하나다(O23). GPT 전체 검증은 끝났다는 확인이 없다. 지정 커밋의 Codex 코드 검토 통과와 다른 일이고, 설계 동결은 그 확인 뒤에 한다. 조건 이름 변경은 석진 님 확인 뒤에 한다 | G13, O23, O24, M5 | 2026-11-07 |
| 조건 이름(11/7 석진 님) | 핵심 다섯 조건을 Brain → Emotion, Brain → Emotion [distillation], Brain → Emotion + Vision + Caption, Brain + Decoded Feature → Emotion, Brain + Decoded Feature → Emotion [distillation]로 부른다. 옛 이름은 직접 학습, 출력 distillation, 특징 맞히기 연습, 주 조건, 주 조건 + 출력 distillation이다. 01, 04, CLAUDE_EmoBrain을 바꿨고 02, 03은 동결 때 맞춘다. 코드 이름은 brain_only, brain_only_distill, brain_only_featdec, brain_decoded, brain_decoded_distill이다 | 1-1 | 2026-11-07 |
| 용어(11/7 석진 님) | Stimulus Model(논문에서는 teacher), Stimulus 예측 평정, 사람 평정, 예측 평정으로 통일한다. 01, 04, CLAUDE_EmoBrain의 특징 모델, T_VS, teacher 점수, teacher 출력을 바꿨다. [distillation] 표시는 유지한다. 시각 특징, 캡션 특징, 정답, 정서 점수는 뜻을 행마다 보고 고쳤다(11/7). 인용문과 논문 문장은 그대로 두었고, 논문 문장의 용어는 03을 맞출 때 정한다. G16과 뇌를 받는 모델(T_BVS)의 teacher 표기도 남아 있다. S4 코드의 T_VS 이름은 다음 코드 수정 때 바꾼다 | 1-1 | 2026-11-07 |
| 모델 정리(11/7 석진 님) | GPT가 정리한 모델과 학습 흐름을 01 5-A에 넣었다. 중심 모델은 Brain + Decoded Feature → Emotion이다. 조건 7을 더해 뇌 모델 학습 조건이 일곱이다. 입력이 Brain + Vision + Caption인 teacher를 Multimodal Model로 부른다. 01의 나머지 행도 5-A에 맞춰 고쳤다 | 5-A, G16, 7-L | 2026-11-07 |
| S2. 구역 안 이름표 짝(6-2) | s2_manifest.py --stage pairs_within_block. 같은 fold, 같은 구역의 시험 영상에서 찾는다. 방향 있는 짝 2,109개, 순서 없는 쌍 1,691개, 짝 없는 영상 0개, 구역과 fold의 시험 영상 31~120개다. 참가자별 block이 없어 빠지는 짝은 sub-01 4, sub-02 1, sub-03 14, sub-04 40, sub-05 187개다. 짝이 같은 구역과 fold 안에 있고 가장 가까운지 stage_check가 확인한다. S9, S10의 계산은 뇌 모델 저장 형식이 정해진 뒤 넣는다 | 6-2, 4-2, O9 | 2026-11-07 |
| S4, S5. 점검 항목 반영 | S4: 과제 이름을 stimulus로 바꿨고, 시험 예측에 더하기 head와 상호작용 head의 예측을 함께 저장한다. baseline 특징의 Stimulus Model을 더했다(VideoMAE, TimeSformer, CLIP은 시각 입력만, MPNet은 캡션 입력만 교체, 6 fold, 5,424회). nested OOF와 K1 head는 그 조건에서 쓰지 않아 만들지 않는다. D12, 정서어 제거 ridge, window 변화의 존재와 크기를 수집에서 점검한다. S5: 영상 식별은 모든 영상 A의 평균이다(O19). Horikawa ridge를 돌리지 않으면 --without h2020을 명시하고 collection_status.tsv에 남긴다. S4, S5의 done.json에 실행 시간을 남긴다. 담당을 정했다: 층별 순열 기준은 S10, O21의 이어 붙이기는 S9가 맡는다. 시험 s4 133개, s5 126개 통과 | O19, O21, M1, 3-1 | 2026-11-07 |
| MPNet의 거의 상수인 차원(11/8 정함) | 개발 영상에서 768차원 중 4개(756, 555, 688, 34)의 표준편차가 2e-35~1e-7이고 중앙값은 0.025다. 표준화하면 수치 잡음이 표준편차 1로 커진다. 11/8 석진 님 결정: 각 학습 자료에서 표준편차가 1e-6보다 작은 차원을 빼고 쓴다. baseline 비교용이라 단순하게 두고 SI에 한 줄로만 보고한다(01 3-3). 구현은 S4 Stimulus Model 실행이 끝난 뒤 S4 baseline과 S6 baseline에 넣는다(실행 중에 s4_*.py를 고치지 않는다). MPNet baseline에만 해당한다 | 3-3, D9 | 2026-11-08 |
| Codex 재검토(S2, S4, S5 코드, 011d7bd) | 보고서 project/output/audits/codex/2026-11-08_s2_s4_s5_recheck_011d7bd.md. 판정: 범위 통과, 반드시 고칠 것 없음. 시험 S4 133개, S5 126개와 독립 검사 60개. 이 커밋에만 적용하고, 코드 검토 통과이지 설계 전체 검증 완료가 아니다. MPNet 네 차원의 실제 값은 Codex가 독립 확인하지 못했고 메인 세션이 계산했다 | M1, O19 | 2026-11-08 |
| S6. 코드와 합성 자료 시험 | 코드 src/s6_model.py, s6_common.py, s6_train.py, s6_tests.py와 .sh. 합성 자료 시험 333개 통과(Codex 지적 반영 뒤). 일곱 조건, 필수 대조군, 더하기와 상호작용 head, 평균 pooling판을 구현했다. S9가 읽을 저장 형식은 s6_train.py 머리말에 있다. 실제 자료와 GPU로는 돌리지 않았다. **구현하지 않은 것:** 외부 baseline 셋(GED, ML-BVAE, EmoGrowth), 네트워크 단독 학습, MC 입력층 학습(S8 범위). **정할 값:** K와 lr_follows_brain_only(S7), lr 1e-2 등에서 NaN이 날 때 fold 전체를 멈출지, 상수 voxel, W, b, e(r)의 초기값, label smoothing의 평균을 행 단위로 낼지, 두 섞기 대조의 순열, attention 저장 범위(어림 약 75 GB, 전체 약 145 GB), 결과 폴더 이름(코드는 brain_only 등, 04와 01 M3은 1-1의 이름에서 만들게 적음). CPU 측정: d = 64, 65행 batch에서 한 step 약 1.2초. GPU 시간은 재지 않았다 | S6, F8, M1, N34 | 2026-11-08 |
| S6. GPU 시간 어림(합성 자료) | s6_timing_gpu.sh를 login34의 공유 GPU에서 돌렸다(11/8 석진 님). d = 64, 65행 batch에서 한 step 0.24초, GPU 최대 메모리 1.2 GB(뇌 입력을 GPU에 올리는 양은 포함하지 않음). 학습 6,934행이면 epoch당 108 step으로 약 26초이고 평가를 더하면 약 30초로 어림한다. 실제 epoch 수는 재지 않았다. S7의 측정을 대신하지 않는다 | N34, L3 | 2026-11-08 |
| S4, S5. 동결 전 실행(11/8 석진 님 요청) | 석진 님이 밤새 돌려 두기로 했다. 최종 설계 동결 전이므로 이 커밋을 --design-freeze 값으로 쓴다. 조건: 결과 파일을 석진 님, Claude Code, Codex, GPT 누구도 동결 전에 열지 않는다. 실행 로그의 진행 메시지만 본다. 대상은 stimulus, k1a, D12, window 변화, S5 decoding이다. MPNet 처리가 미정이라 baseline 과제는 돌리지 않는다. 설계가 이 값을 바꾸면 해당 과제를 다시 돌린다. 방법 절에 이 순서를 그대로 적는다 | M5, S4, S5 | 2026-11-08 |
| Codex 검토(S6 코드, 8006d50) | 보고서 project/output/audits/codex/2026-11-08_s6_code_8006d50.md. 판정: 수정 후 재검토. stop-gradient, frozen head의 역전파, weight decay 묶음, 학습 자료만 쓰는 표준화는 맞았다. 반드시 고칠 것 3건을 고쳤다. (1) 파일럿이 시험 fold의 뇌 반응을 읽은 뒤 버리던 것: 원본 배열을 인덱싱하기 전에 이번 실행의 영상 행으로 줄인다(s5 코드는 실행 중인 S4, 끝난 S5의 실행 번호를 지키려고 고치지 않고 S6에 같은 경로를 둠). (2) S4 Stimulus 예측 평정의 출처를 대조하지 않던 것: S4 완료 기록을 요구하고, 과제, 바깥 fold, S4가 쓴 입력의 내용이 지금과 같은지 학습 전에 확인하며 S4 실행 번호를 S6 기록에 넣는다. (3) 배열 크기를 확인하지 않아 한 열이나 한 행이 복제되던 것: (학습 영상 수, 34)를 강제한다. 보완으로 체크포인트 복원 함수가 추론용이고 고정 상태를 되살리지 않는다고 적었다. 시험 333개 통과 | N34, E4, M1 | 2026-11-08 |
| 동결 때 02, 03에 맞출 것 | 11/5 갱신 규칙(CLAUDE_EmoBrain 5절)에 따라 미룬 항목이다. 14개 차원(B4, K1a), 8초 종료 규칙(정할 것 11), 정서 층화 분할(정할 것 12), MC 4회 평균의 상태, 03의 419행 5회 평균 문장(Codex 재검토), window 평균의 근거 문헌을 부록 1, 4와 references.bib에 넣는 일(Arnab 외 2021, Wang 외 2016, Korbar 외 2019, Feichtenhofer 외 2019, Wu 외 2019, Du 외 2023 등). 동결 전에 01과 차례로 대조한다 | CLAUDE_EmoBrain 5절 | 2026-11-05 |
| 보류된 결정 1. 질문 2의 뒷부분 | 정함(11/6 석진 님): (가). 6-2의 Brain + Decoded Feature → Emotion 모델로 그 구역의 시험 영상에서도 바꿔 끼우기를 한다. 탐색 결과로 표시한다. 01의 6-2와 A4를 고쳤다. 짝 규칙과 학습량 대조 모델의 비교도 정했다(11/6). S2에 구역 안 짝 목록을, S9에 계산을 더해야 한다. 구역은 이름표 73개를 하나씩 뺀 것이 아니라 그 73개로 묶은 5개다. 구역 수 5개를 근거를 다시 확인하고 유지했고, 01 4-3의 이유와 논문 문장을 "blockCV 기본값 채택"에서 "영상 수와 학습 비용을 고려한 설계 선택"으로 고쳤다. 문헌 Shirakawa 외(2025)를 01 부록 1, 4에 더했고 references.bib는 동결 때 맞춘다 | 1-3, 6-2, A4 | 2026-11-06 |
| 보류된 결정 2. 1-1의 주 검정 | 정함(11/6 석진 님): 01의 가설과 6-1을 지금대로 둔다. 정서별 두 경로의 효과와 차이를 보고하고, 정서 사이의 패턴은 결과를 두고 해석한다. 가설 검증과 결과 해석을 구분한다. 03 1.7.2의 문구는 동결 때 01에 맞춘다. Kragel 외(2019) 비교는 보조로 둔다 | 1-3, 6-1, 03 1.7.2 | 2026-11-06 |
| 보류된 결정 3. G13 weight decay 0.01의 범위 | 정함(11/7 석진 님): 입력층 weight는 d와 함께 후보에서 고른다. 나머지 linear와 attention의 weight, query, ROI embedding은 0.01이다. bias와 LayerNorm에는 적용하지 않는다(01 G13). 코드에서 파라미터마다 어느 묶음인지 명시한다 | G13, 5-5 | 2026-11-07 |
| 보류된 결정 4. S7 수렴 확인 뒤 바꿀 수 있는 것 | 정함(11/7 석진 님): learning rate는 모든 조건의 후보로 넣는다(G13). 첫 fold의 안쪽 자료는 수렴 확인에만 쓰고 값을 고르지 않는다. 수렴하지 않으면 혼자 바꾸지 않고 측정값과 함께 보고한다 | G13, S7 | 2026-11-07 |
| 01 글 수정 목록(설계 변경 아님) | 7-O 머리말에 "통합문서에 넣을 초안" 문장이 남아 있다. 7-O 4절은 O1~O5를 "석진 님 결정"이라고 적지만 표는 "정함"이다. 5-5 논문 문장의 "Fu et al., 2022"는 참고문헌의 Fu 외(2024)와 다르다. 부록 1 ML-BVAE 행의 "게재처 미확인"은 5-2에서 확인한 내용과 다르다. 부록 1의 Romero 외(2015)는 본문에서 인용하지 않는다. 5-6이 말하는 fig56_v2.py와 .svg가 docs/final에 없다 | 7-O, 5-5, 5-6, 부록 1 | 2026-11-03 |

## 3. 하지 않는 것

### 3-1. 필수 실행 범위 밖(L2와 각 절의 후속)

- 뇌를 받는 모델의 성능 점검(T_BVS 대 Stimulus Model). 선형판과 딥러닝판 모두 보류한다(E7, 1-3 관점 B).
- encoding(N42)
- MC 회상(6-3, A11). 회상 구간 분리 확인도 하지 않는다.
- 14개 차원으로 뇌 모델을 학습하는 분석과 14개 교체 분석(B4). B4 ridge(S5)와 K1의 14개판(K1a, S4, S9)은 필수 범위의 보조 분석이다.
- 패턴 발견(단서 수준 분석)(N44)
- 기여도 방법(IG 등)(K8). attention 가중치를 기여도로 읽지도 않는다.
- GLMsingle과 LSS(C1)
- 출력 distillation-시각과 -캡션, 거기에 쓰는 시각만, 캡션만 받는 Stimulus Model(E5, G2)
- 빼고 다시 학습(6-4)
- 중간 표현 distillation 가운데 G16 밖의 판(ex) 뇌 표현 복사 대조), FiLM, I²MoE, ModDrop(L2)
- 정서 손실의 역전파를 허용한 Brain + Decoded Feature → Emotion(5-0의 후속)
- 두 단계 학습(decoding 먼저, 정서 미세조정)(N35)
- N36의 후속 목록: 뇌와 내용의 상호작용, 뇌를 학습 때만 쓰는 영상 정서 학습, 사건 핵심 3층 분리, 비슷한 감각 다른 상황 쌍, 정서별 시각 다양성, Stimulus Model 오류 전이 진단, 더 강한 뇌 단독 방법(증강, 자기지도), CLIP 공간에서 영상과 캡션과 뇌를 함께 맞추는 설계, 처음 보는 참가자(LOSO), 라벨 효율 학습 곡선, 한국어 평정, White 외부 검증
- 370개 ROI마다의 ridge decoding 지도(6-4)
- Yeo 대응표와 Yeo로 다시 한 분석(6-4)
- 입력 방식 비교와 복셀 압축 비교(5-5)

### 3-2. 필수 범위에 없는 SI와 보조. 할지는 석진 님이 정한다

- 다시 학습한 head(K2), 특징만 학습한 모델(K1, G6)
- Vision feature만 decoding, Caption feature만 decoding(G6)
- 같은 용량의 probe(N25)
- 추가 분석 후보(N33)
- Vision feature(V-JEPA 2)로 나눈 구역판(N27)
- 실제 Vision feature와 Caption feature를 head에 넣는 개입(Koh 외, 2020의 test-time intervention)(5-0)
- Horikawa 외(2020)의 VGG19와 이름표 73개의 닮음과 쓸모 비교(3-7)
- V-JEPA 2의 4초 window 평균판(3-2)
- 평균 pooling판(F7)의 실행(O31)
- 같은 ROI 수의 무작위 묶음 대조, 피질하 10개의 개별 교란, 주 경사 그림(6-4의 보조)
- 전역 신호를 뺀 입력판(N21)

### 3-3. 쓰지 않기로 한 방법

- 자료와 라벨
    - 34개를 27개로 줄이기, 사람 평정의 z-score(B3), 34개 합을 1로 맞추기(2-5), softmax(2-1)
    - 평정자 수 가중(2-2), 거꾸로 센 평정자 수(B8), 평정자 수를 가정한 상한선(2-6)
    - 이진화 지표와 분포 거리(2-4), 16개 정서만의 평균, "0.5를 넘는 영상이 없으면 해석하지 않음"(2-6), J6의 0.3 기준(4-1)
    - 켜짐/꺼짐형 대 넓게 옅은형 묶음, "Brain → Emotion이 약한 정서" 묶음(I9)
- 특징
    - 학습 목표의 PCA, Stimulus Model 입력의 PCA(D9, 5-4)
    - 마지막 block 하나만 목표로 쓰기, 앞쪽 block을 따로 두 번째 목표로 두기(3-2, E1, F5)
    - 예전 추출(영상 전체에서 16프레임 linspace), 마지막 프레임으로 채우기, 프레임 보간(3-2, O10)
    - TimeSformer의 4초 window, 초당 2장 안(3-2)
    - Kinetics로 미세조정한 VideoMAE, DINOv2, V-JEPA 2.1, DeBERTa-v3-large, 최신 대형 언어 모델, 영상 기반 캡션 생성 모델(3-1, 3-3, 3-4)
    - 캡션을 학습마다 하나씩 고르기, 20개를 이어 붙이기(3-4b)
    - 세 층 구분(3-5)
    - 간단한 화면 통계 33개를 저수준 특징이나 기준선으로 쓰기(3-6)
    - Jang & Kragel(2025)의 공간 주파수 힘 2개(3-6)
    - CLIP 공간에 뇌를 맞추는 새 모델(3-1)
    - Horikawa 외(2020)의 VGG19와 이름표 73개를 주 분석의 목표로 쓰기(3-7). 이름표 73개를 학습 목표나 개념 병목으로 쓰기(D11, N18)
- 비교 단위
    - 캡션 TF-IDF 0.4 쌍(4-2)
    - "이름표 73개로 묶고 MPNet으로 고르기"(4-2)
    - "이름표 73개로 예측한 부분을 뺀 나머지 분석"(4-2)
    - 거리 상한(caliper), Tukey 기준, 가까운 절반 SI, 사람이 쌍을 판정하는 절차(4-2)
    - Mahalanobis 거리(4-2)
    - 표준화한 이름표로 만든 군집, 크기 제약(constrained k-means, 크기를 똑같이)(4-3)
    - Gap statistic과 silhouette으로 구역 수 정하기. 보조 진단으로만 남는다(4-3).
- 모델
    - 칸 평균(ROI pooling) 입력(우리 모델), 이전 469개 지도, Tian S2로 피질하 나누기(5-5)
    - subroi4 ridge와 subroi4 MLP(I7, F2)
    - FC 입력(C8), 뇌 기반 모델의 사전학습(C9)
    - 이전 F6 구조(decoded features를 token으로 만들어 ROI token과 함께 attention)(5-4)
    - Brain + Decoded Feature → Emotion의 λ = 0 후보(G9)
    - 핵심 다섯 조건에 frozen head 쓰기(5-2)
    - CCA 공통 성분 교체(5-0)
    - G16의 뇌 표현 복사 대조, G16의 Multimodal Model을 5개 fold 전체로 학습하기(G16)
    - 옛 Study 1, Study 2 틀과 T_BVS(0절)
- 학습과 평가
    - 뇌 모델의 안쪽 5겹 설정 선택, 바깥 학습 자료 전체로 다시 학습하기(H2, L9)
    - Stimulus 예측 평정, 섞은 목표, feature decoding loss로 설정을 고르거나 조기 종료하기(0-2)
    - seed 예측의 앙상블(G14)
    - 모집단 유병률 추정(Ince 외, 2021), 동등성 검정, "5명 중 4명" 문턱(6-1)
    - Yeo 7의 0단계 값으로 묶음을 고르거나 해석하기(6-4)
    - MC로 처음부터 다시 학습하기(6-3)
    - 경로 평가에서 시각만, 캡션만 head를 쓰기, ROI token 경로 넣기, 비율로 보고하기, 겹침 항 계산(K1, N6)
- 용어
    - "context lift"(A6), "맥락"을 공식 용어로 쓰기(1-1)
    - feature decoding을 "distillation", "reconstruction", "특징 복원"이라고 부르기(5-2)
| Codex 재검토(S6, 50b4724)와 분할 목록 파일 | 보고서 project/output/audits/codex/2026-11-08_s6_recheck_50b4724.md. 필수 1(파일럿의 읽기 경계), 3(Stimulus 예측 평정 배열 크기) 수정 확인. 필수 2의 남은 결함을 받아들여 고쳤다. S4 완료 기록에 입력 해시가 빠져 있으면(사람 평정 해시 누락, S2 표 해시 누락, inputs 자체 누락) 출처 검사를 건너뛰던 것을, S4 stimulus 과제가 반드시 남기는 역할 8개(visual_target, caption_target, labels, S2 표 5개)가 모두 있어야 통과하도록 했다(s6_common.STIMULUS_REQUIRED_ROLES). 실제 fold1 done.json의 역할 이름이 이 8개와 같음을 확인했다(값은 열지 않음). 11/8 석진 님 요청으로 실행 단위별 분할 목록 파일을 만들었다. s2_split_files.py가 split_hk_dev.tsv와 fold_roles.tsv에서 manifests/s2/splits/{outer_fold1~6, final_for_mc}/{train,val,test}.txt를 만들고 --check로 대조한다. S6는 이 파일을 읽고(s6_common.load_plan) 두 표로 다시 낸 목록과 다르면 멈추며, 파일 해시를 실행 기록에 넣는다. 파일럿은 test.txt를 읽지 않는다. 구역 제외 분할의 목록 파일은 아직 없다. S4, S5는 실행 중이거나 끝난 실행 번호를 바꾸지 않으려고 아직 표에서 직접 분할을 낸다. 코드 정리 때 같은 목록 파일을 읽도록 바꾼다. 시험 s6 349개 통과(새 시험 16개). 규칙은 CLAUDE_EmoBrain.md 5절 '코드 디렉토리와 배포 준비'에 넣었다 | E4, M1, N34, H2 | 2026-11-08 |
| S6. 손실 흐름 허용판 추가(11/8 석진 님) | 01 5-0의 후속 분석이던 '정서 loss의 역전파를 허용한 Brain + Decoded Feature → Emotion'을 성능 비교 전용 보조 조건으로 올렸다. 조건 이름 brain_decoded_grad. 구조, 후보, 선택 규칙은 brain_decoded와 같고 Readout의 stop_gradient=False만 다르다(s6_model.Readout.combine). 바꿔 끼우기, K1, 결합 지표, 네트워크, 구역 제외, MC에 쓰지 않으므로 S9와 S10은 이 조건을 성능 표에만 넣는다. 기본 run 분할에서만 돈다(ZONE_CONDITIONS 밖). 실행량 fold마다 26, 합계 156(01 7-L). 시험 s6 356개 통과(새 시험 7개). 가중치 수 표(manifests/s6/weight_counts.tsv)를 d 32, 64, 128로 다시 냈다. 허용판의 가중치 수는 brain_decoded와 같다 | G8, 5-0, 7-L | 2026-11-08 |
| 결과를 본 뒤의 변경 규칙(11/8 석진 님) | 11/1의 '결과를 보고 설계를 고르지 않는다'를 바꿨다(01 0절). 설정과 분석은 결과를 보고 바꿀 수 있다. 비교는 가능하면 검증 fold로 하고, 결과를 보고 바꾼 것은 이 기록 칸에 날짜, 무엇을, 왜를 남기며 논문에 한 줄로 밝힌다. MC 최종 시험 72개는 튜닝과 선택에 쓰지 않는다. 01의 개별 문장(5-0 허용판, 5-4 더하기 head, K1a, L3, 3-2 층 선택)을 이 규칙에 맞췄다. 설계 동결은 여전히 결과를 처음 여는 시점의 기준 커밋으로 남긴다. 그 뒤 바뀐 것은 이 표에 쌓인다. S4, S5 재실행 정정: 폴더 정리처럼 계산이 같은 변경은 다시 돌리지 않고 계산이 같음을 확인해 기존 실행 출처를 보존한다. Stimulus Model(6 fold 끝, 11/8 16시)과 k1a는 그대로 쓰고, D12, window, S5 decoding은 25분이라 다시 돌린다. 같은 이유로 Stimulus Model 후보 병렬화는 하지 않는다 | 0절, M5 | 2026-11-08 |
| S6 학습 규칙 결정(11/8 석진 님) | (1) 뇌 모델과 soft BCE 선형 기준선의 learning rate 후보를 {1e-5, 1e-4, 1e-3}으로 바꿨다(s6_common.LEARNING_RATES, s5_common.SOFT_BCE_LRS). Stimulus Model은 {1e-4, 1e-3, 1e-2}로 6 fold를 마쳐 그대로 쓴다. (2) 발산: 설정 후보 고르기(seed 0)에서 손실이 NaN, Inf면 s6_train.Diverged로 그 후보만 done.json에 diverged로 남기고(모델 저장 없음) 선택에서 뺀다. 모두 발산하면 fold를 멈춘다. 고른 설정의 seed 1, 2가 발산하면 멈춘다. (3) 학습 행에서 상수인 voxel은 표시하고 모든 행에서 0으로 둔다(s6_common.voxel_standardizer, standardization.npz의 voxel_constant). (4) 초기값 PyTorch 기본값, 두 섞기 대조의 같은 순열(이미 그렇게 구현됨), 고른 모델의 attention 저장(이미 구현), 결과 폴더는 코드 이름(이미 구현, README 대응표는 폴더 정리 때). 시험 s6 369개, s5 126개 통과. S5 soft BCE 기준선은 아직 돌리지 않아 영향이 없다 | G13, O24, O16 | 2026-11-08 |
| S4. Stimulus Model learning rate 변경과 재실행(11/8 석진 님) | s4_feature_model.LEARNING_RATES를 {1e-5, 1e-4, 1e-3}으로 바꿨다(뇌 모델과 같음). stimulus와 k1a가 이 후보를 쓰므로 둘 다 다시 돌린다. 옛 후보로 끝낸 결과(stimulus 6 fold, k1a 6 fold, design-freeze e13265f)는 열지 않은 채 outputs/s4_no_brain/superseded/lr_1e-2_20261108/로 옮겼다. D12, window는 이 변경과 무관하지만 코드 해시가 바뀌어 다음 실행 때 함께 다시 낸다(합계 15분). 시험 s4 133개 통과 | O16, E3, K1a | 2026-11-08 |
| 화요일 발표용 예비 실행 준비(11/8 석진 님, 발표 11/10 09시) | 내일 아침까지 결과를 내려고 순서를 바꿨다. (1) Stimulus Model: 1e-5 재실행은 발표 뒤로 미루고, 옛 후보({1e-4, 1e-3, 1e-2})로 끝낸 6 fold를 superseded에서 s4_no_brain/stimulus로 되돌려 예비 실행의 distillation 정답에 쓴다. k1a는 superseded에 둔다. 발표 자료에 이 점을 적는다. (2) S6 예비 설정 manifests/s6/run_config_prelim_20261108.json: d 64, 입력층 weight decay 0.01(AdamW 기본값), learning rate 1e-4, seed 0. λ, r, α 후보는 G9 그대로라 fold마다 17회 학습한다. 핵심 여섯 조건(Brain → Emotion, Brain → Emotion + Vision + Caption, Brain + Decoded Feature → Emotion의 상호작용 head와 더하기 head, 두 distillation). 결과는 s6_brain_prelim에 따로 둔다. (3) Config에 seeds를 더했다(SEEDS의 앞부분만, 후보 고르기는 항상 seed 0). (4) s6_prelim_20261108.sh: GPU shared QOS의 array 6개, fold마다 GPU 하나. 시험 s6 372개 통과 | G13, L9, S7 | 2026-11-08 |
| Codex 재검토(S6, 0a36925) | 보고서 project/output/audits/codex/2026-11-08_s6_recheck_0a36925.md. 이전 필수 2번 수정 확인, 필수 2건을 고쳤다. (1) 모델 안에서 생긴 NaN, Inf(가중치, 기울기, v̂ 등)가 일반 ValueError로 나 fold가 멈추던 경로를 s6_train.numeric과 check_finite_state로 Diverged에 연결했다. backward 뒤 기울기, step 뒤 가중치를 검사한다. shape와 자료 경계 오류는 그대로 멈춘다. (2) S5 soft BCE가 함수 인자로 받은 1e-2를 그대로 학습하던 것을 check_soft_bce_candidates로 학습 전에 거절한다. 시험 s6 377개, s5 127개 통과. 예비 실행 방식은 아래 Codex 재검토(9d35ea0) 행을 따른다 | G13, O24 | 2026-11-08 |
| 레포 디렉토리 정리(11/8 석진 님) | 공개 논문 레포 형태로 옮겼다. 코드 project/analysis/final_2026-11/*.py → src/, .sh → scripts/(공통 머리 scripts/_env.sh, 레포 최상위에서 실행), 시험 → tests/. 분할 원본 split_hk_dev.tsv, fold_roles.tsv와 목록 → splits/hk_dev_v4/. S1 표 → manifests/s1/, S2, S3, S6 표 → manifests/s2, s3, s6/. 실행 설정 → configs/s6/. 입력 표(정서 평정, 캡션, 자극 목록, 번호 대응, 사건 표) → data/. 정서어 목록의 원본 build_caption_noemo.py → data/. 서버 경로는 src/paths.py가 configs/paths.yaml(git 밖, 예시 configs/paths.example.yaml)에서 읽고, 실행 Python은 configs/env.sh(git 밖)에서 읽는다. 큰 산출물은 outputs/(이 서버에서는 project/output/final_2026-11 링크, git 밖). s4_collect, s5_collect의 결과 표는 레포 대신 outputs/s4_collect, s5_collect에 쓴다. 옛 폴더(project의 code, data, legacy, shared, analysis/prelim_2026-10 등, prereg_v2, tools, CONTEXT_EMOBRAIN.md, 옛 README)는 archive/로 옮겼다. 계산은 바꾸지 않았다. 입력의 역할 이름과 내용 해시가 같아 S4의 출처 기록과 S6의 대조가 그대로 맞는다. 코드 해시는 바뀌었으므로 같은 과제를 다시 돌리면 실행 번호가 달라진다. 문서의 경로도 새 위치로 바꿨다. 시험 s3 57개, s4 133개, s5 127개, s6 377개 통과, 분할 목록 대조 통과. 11/8 발표용 예비 실행은 정리 전 커밋 e57c9dc의 고정 사본(/pscratch/sd/s/sjmoon/EmoBrain_run_e57c9dc)에서 돌린다 | M3, 배포 규칙 | 2026-11-08 |
| 결과를 처음 연 시점(11/8 석진 님 허락) | 11/8 17시 KST, 커밋 9d35ea0에서 S4와 S5 결과를 처음 열었다. 연 것: Stimulus Model 6 fold(옛 learning rate 후보 {1e-4, 1e-3, 1e-2}, e13265f 실행)의 시험 예측과 선택표, D12, window 변화, S5 층별 decoding 30개. 이 시점 뒤에 결과를 보고 바꾼 설정은 01 0절 규칙대로 이 표에 날짜와 이유를 남긴다. 계산 스크립트는 레포 밖의 임시 파일이다(시험 r은 6 fold 시험 예측을 모아 정서별 Pearson r) | 0절, M5 | 2026-11-08 |
| Codex 재검토(레포 정리, 9d35ea0) | 보고서 project/output/audits/codex/2026-11-08_release_recheck_9d35ea0.md. S6 수정 2건 통과(시험 s4 133, s5 127, s6 377, 독립 146). 반드시 고칠 것 2건을 고쳤다. (1) login node에서 장시간 학습을 띄우는 scripts/s6_prelim_login_20261108.sh를 지웠다. NERSC login node 정책상 학습은 Slurm(shared QOS)으로 낸다. README도 'Slurm으로 할당받은 compute node'로 고쳤다. (2) data/stimuli.tsv의 영상 경로 2,196개가 서버 절대 경로라 data_root를 바꿔도 S3가 옛 경로를 읽었다. path를 video_root 기준 상대 경로로 바꾸고 머리말의 서버 경로를 지웠으며, s3_common.stimulus_table이 configs/paths.yaml의 video_root에 붙인다. 영상 내용과 sha256은 그대로다. 이 표의 해시가 바뀌었으므로 S3를 다시 모으면(s3_collect) 추출 당시 기록과 달라 멈춘다. S3는 끝났고 특징은 그대로 쓴다. S4, S6의 입력이 아니라 Stimulus 출처 검사에는 영향이 없다. 레포의 다른 표(data/cowen_horikawa_labels.csv, events_audited.tsv, stimulus_crosswalk.tsv, manifests/s2/provenance.json)에도 서버 경로 문자열이 남아 있다. 정서 평정 파일은 S4 출처 해시에 묶여 있어 지금 바꾸면 S6 검사가 멈추므로, Stimulus Model 재실행 때 함께 정리한다. 시험 s3 61개 통과 | 배포 규칙 | 2026-11-08 |
| 27개 평가판 추가(11/8 석진 님) | 학습과 주 결과는 34개 그대로 두고, 평가에서 Cowen & Keltner(2017) 본문의 7개(pride, triumph, contempt, disappointment, sympathy, guilt, envy)를 뺀 27개판을 함께 낸다. 저장된 예측표에서 열만 빼므로 학습을 다시 하지 않는다. 계기: 11/8 결과에서 이 7개가 Stimulus Model과 뇌 ridge 모두에서 가장 약했다(수치는 레포 밖 결과 요약에 있다). 정서 선택의 기준은 선행 연구이고 우리 결과가 아니다. 01 0절의 고정 사실 문장을 고쳤다 | 0절, 6-0 | 2026-11-08 |
| 예비 실행 결과와 조건 8 추가(11/9 석진 님) | 예비 실행(d 64, 입력층 weight decay 0.01, learning rate 1e-4, seed 0, 공용 encoder) 6 fold, 학습 144회가 오류와 발산 없이 끝났다(fold당 7.1~7.6시간, 학습 1회 16~30분). 조건 1~5와 Multimodal은 4~8 epoch에서 가장 좋았고, 조건 6, 7은 9~33 epoch. 결과 요약은 outputs/s6_brain_prelim/summary/(정서별 r, R², MAE 표와 계산 스크립트, 레포 밖). fold 1, 6의 조건 2는 λ = 0이 뽑혀 조건 1의 모델이 쓰였다(G10). 결과를 본 뒤 조건 8(조건 3의 encoder 분리판)을 더하기로 했다. 조건 3, 5는 그대로 두고 따로 더한다. 구현은 S6 코드 수정, 시험, Codex 검토 뒤에 낸다 | 5-A, G8, 7-L | 2026-11-09 |
| S6. 조건 8, 9 구현(11/9 석진 님) | 조건 3, 5는 그대로 두고 encoder 분리판을 더했다. (1) feature_encoder(encoder 2): feature 손실((Vision MSE + Caption MSE) / 2)만 쓰고 정서 쪽에 기울기가 가지 않는다. d와 입력층 weight decay는 그 fold의 brain_only 선택, learning rate는 검증 feature MSE로 고르고 같은 값으로 조기 종료한다(s6_train.feature_val_loss, val_score = −MSE). 정서 예측을 내지 않아 decoded_test/val과 decoding_accuracy만 저장한다. (2) brain_decoded_sep(조건 8), brain_decoded_sep_distill(조건 9): s6_model.SeparateDecodedModel이 encoder 1(조건 3과 같은 BrainModel, 보조 feature head 포함)과 고정한 encoder 2(같은 seed의 feature_encoder 선택, 입력층까지 따로)를 묶는다. 정서 계산은 encoder 2의 v̂₂, ĉ₂를 쓰고, 손실의 feature 항은 encoder 1의 보조 출력 v̂₁, ĉ₁로 낸다. encoder 2는 no_grad와 고정으로 기울기를 받지 않고 학습 뒤 가중치 해시가 같은지 확인한다. outputs의 decoded_*.npz는 v̂₂, ĉ₂(바꿔 끼우기용), aux_decoded_*.npz는 v̂₁, ĉ₁다. 조건 9는 조건 8의 λ, r을 이어 받고 α = 0 후보는 조건 8이다(G10). (3) scripts/s6_main.sh에 세 조건을 넣었다. 가중치 수 표를 d 32, 64로 다시 냈다(조건 8, 9는 encoder 1만 학습 가중치로 센다). 시험 s6 400개 통과(새 시험 16개 포함). 본실험 설정의 note를 검증 곡선 근거로 고쳐 썼다(시험 성능을 근거로 쓰지 않음) | 5-A, G8, G9, G10 | 2026-11-09 |
| S6. 조건 10 구현(11/9 석진 님) | brain_features_only: s6_model.FeatureHeadModel이 고정한 encoder 2(같은 seed의 feature_encoder 선택)의 v̂₂, ĉ₂ 위에 정서 head(a, b, A, B, U)만 학습한다. 뇌에서 바로 정서를 읽는 경로가 없다. r 0, 1, 2, 4, 8 × learning rate. 저장은 정서 출력만(쓴 v̂₂, ĉ₂는 feature_encoder 출력과 같음). 시험 s6 406개 통과. scripts/s6_main.sh에 넣었다. 같은 날 확인: 예비 실행 144회는 모두 커밋 468c0b1, 미커밋 코드 없음. 조건 3은 6 fold 중 4개에서 λ 1.0이 뽑혔는데도 decoded feature가 약했다(정서 검증 손실로 4~8 epoch에 멈춤) | 5-A, 7-L | 2026-11-09 |
| 조건 이름을 묶음으로(11/9 석진 님) | 만든 순서의 번호(조건 1~10) 대신 장면 정보를 쓰는 정도로 묶은 이름을 쓴다. A-1 = 옛 조건 1, A-2 = 4, B-1 = 2, C-1 = 3, C-2 = 5, D-1 = 8, D-2 = 9, E-1 = 10, F-고정 = 6, F-학습 = 7. -2는 같은 묶음에 distillation을 더한 것이고, F는 head 고정 여부라 -1, -2 대신 고정, 학습으로 부른다. 주 조건은 정하지 않는다(01 5-A의 '중심 모델' 표기를 뺐다). 코드 이름과 결과 폴더는 그대로 두고 s6_common.DISPLAY에 대응을 넣었다. 01, OVERVIEW, README, 이 문서의 작업 지시 부분, 코드 주석과 시험 문구를 새 이름으로 고쳤다. 이 표의 지난 기록 행은 옛 번호 그대로 두고 01 5-A의 대응표로 읽는다. 시험 s6 409개 통과 | 5-A, 1-1 용어 | 2026-11-09 |
| 입력층 점검 준비(11/9 석진 님) | 예비 실행에서 뇌 모델이 voxel 전체 ridge보다 낮았다. ridge를 ROI 단위 입력(ROI 평균 370개, ROI별 주성분 32, 64개)으로 돌려도 정서별 r이 거의 같아서(레포 밖 outputs/checks/roi_ridge_20261109), ROI 단위가 아니라 voxel을 token으로 바꾸는 학습 단계를 점검한다. s6_model.BrainItRoiInput: Brain-IT tokenizer(Beliy 외 2026, 4절, 부록 D.1)를 ROI 370개를 군집으로 두고 얹었다(부록 A.2의 해부 기반 묶음과 같은 구성). voxel embedding × voxel 값을 key와 value로, 참가자 공유 ROI embedding을 query로 둔 head 1개 attention, root 항, 학습 때 voxel 뽑기(비율 0.375 또는 0). 설정 tokenizer, voxel_sampling(기본 linear, 0이라 본 설계는 그대로). A-1만 예비 실행과 같은 설정(d 64, 입력층 weight decay 0.01, learning rate 1e-4, seed 0)으로 돌린다: scripts/s6_check_brainit_20261109.sh, 결과는 s6_check_brainit_{sample,nosample}. 같이 고친 것: S6이 Stimulus 예측 평정을 쓰는 조건(A-2, C-2, D-2, Stimulus 예측 섞기 대조군)이 있을 때만 S4 출력을 읽고 대조한다(s6_common.needs_stimulus). 시험 s6 425개 통과 | 5-5, G13 | 2026-11-09 |
| D-1, D-2 예비 실행 준비(11/9 석진 님) | 11/8 예비 실행과 같은 설정(run_config_prelim_20261108.json)으로 A-1, encoder 2, D-1, D-2를 돌려 C-1, C-2와 비교한다. scripts/s6_prelim_sep_20261109.sh, 결과는 s6_brain_prelim_sep. encoder 2와 D의 d, weight decay가 같은 실행의 A-1 선택을 따르므로 A-1도 다시 돈다. D-2의 Stimulus 예측 평정은 예비 실행의 A-2, C-2가 쓴 옛 Stimulus 실행(superseded/lr_1e-2_20261108)을 S4_OUT으로 가리켜 쓴다 | 5-A, L9 | 2026-11-09 |
| 입력층 점검을 저자 코드에 맞춤(11/9 석진 님) | Brain-IT 공개 코드(github.com/WeizmannVision/brainit-fmri의 models/decoder_models.py)와 대조해 BrainItRoiInput에 빠졌던 두 가지를 넣었다. 모은 token 뒤 ReLU와 LayerNorm, voxel embedding과 군집 embedding의 초기값 0.1 / (2√d) × N(0, 1). PyG TransformerConv로 저자 코드의 tokenizer 부분을 그대로 따라 한 값과 같음을 확인했다(최대 차이 5e-7, 레포 밖 일회 확인). 옛 구현으로 띄운 점검 12개는 취소하고 결과는 outputs/superseded/s6_check_brainit_old_impl_20261109로 옮겼다. 저자 코드는 별도 오픈소스 라이선스가 없어 복사하지 않고 같은 계산을 우리 코드로 짰다. 시험 s6 426개 통과 | 5-5 | 2026-11-09 |
| 입력층 점검에 ROI 평균과 8칸 평균 추가(11/9 석진 님) | 입력층 후보 가운데 ROI PCA는 빼고 ROI 평균과 칸 평균을 A-1로 확인한다. 칸 평균은 같은 Horikawa 2020 자료의 선행 모델(GED, ML-BVAE, EmoGrowth)이 쓴 ROI pooling이고 칸 수는 EmoGrowth의 8칸(축마다 둘)이다. ML-BVAE 절제에서 영역 평균 하나는 중간 칸 수보다 낮았다(01 부록 4). s2_roi_cells.py: QC mask에서 voxel 좌표를 다시 구해 ROI마다 칸 번호를 만든다(mask 해시가 ROI 표와 같을 때만, ROI 대부분 8칸이 차고 가장 적은 ROI도 5칸). s6_model.RoiCellInput: 칸 평균(학습 행으로 표준화한 voxel 값) × 참가자, ROI, 칸마다 d차원 가중치 + b + e. 참가자당 입력층 가중치는 ROI 평균 약 2.4만, 8칸 약 19만(지금 입력층 약 1,200만). 칸 번호 파일은 S6 입력 해시에 들어간다. 실행: scripts/s6_check_roi_20261109.sh, 결과는 s6_check_roi_mean, s6_check_roi_cells. D-1, D-2 예비 실행(6c70784로 띄운 것)은 내가 실행 중에 s6_model.py를 고쳐 '시작 뒤 코드가 바뀌었다'로 멈췄다. 이후 코드는 도는 실행이 없을 때만 공유 사본에 합친다. 시험 s6 439개 통과 | 5-5 | 2026-11-09 |
| D 묶음 정리: D-3, D-4, E(11/9 석진 님) | 석진 님: E-1(brain_features_only)을 D-3으로 이름만 바꾼다. D-1과 같은 Encoder 2를 쓰므로 D 묶음에 둔다. D-4를 새로 넣는다. 장면 특징으로만 학습해 고정한 Encoder 2의 token H 위에 A-1과 같은 정서 head만 학습한다. 이유: 장면 특징으로 미리 학습한 Encoder의 표현에서 정서를 읽을 수 있는지를 A-1과 한 군데만 바꿔 묻기 위해서다. D-3은 D-4의 효과가 장면 특징에서 오는지 보는 짝으로 둔다. 예비 실행(11/8) 뒤에 넣은 조건이다. 같이 한 것: 옛 F-고정, F-학습을 E-고정, E-학습으로 당겼다(코드 이름과 결과 폴더는 그대로, s6_common.DISPLAY만 바꿈). 구현: 코드 이름 brain_frozen_feature_encoder, s6_model.FrozenEncoderModel. 같은 바깥 fold, 같은 seed의 feature_encoder 체크포인트로 입력층과 encoder를 채우고 고정한다(requires_grad 끔, 평가 상태). 정서 query와 정서별 선형층은 새로 초기화한다. 후보는 learning rate 3개, d와 입력층 weight decay는 A-1 값. ORDER에서 feature_encoder 바로 뒤, planned_runs에 learning rate 수 + seed 2, linear 입력층만. 시험: (a) 학습 전후 encoder 2 해시 같음, (b) 고정 parameter에 기울기 없음, (c) d가 encoder 2와 같음, (d) 짝지은 encoder 2 체크포인트 해시를 실행 기록에 남김, (e) 검증, 시험 영상만 예측하고 분할 점검이 MC 72개에서 멈춤. 시험 s6 457개 통과. 예비 실행 스크립트 scripts/s6_prelim_d34_20261109.sh(A-1, encoder 2, D-4, D-3, 결과는 s6_brain_prelim_d34). 점검 약속: encoder 2가 끝나면 바깥 fold마다 학습 영상과 검증 영상의 v̂₂, ĉ₂ 정확도(decoding_accuracy.tsv)를 석진 님에게 보고한다. encoder 2까지 정서로 다시 학습하는 판은 후속(01 5-A) | 5-A, 1-1, 7-L | 2026-11-09 |
| encoder 2의 2단계 학습 영상, D-4 짝 학습, 외부 딥러닝 기준선(11/9 석진 님) | 근거: 예비 실행(fold 2, 3, 5, 참가자 5명 평균)에서 encoder 2의 차원별 r이 학습 영상 Vision 0.67~0.69, Caption 0.65~0.68, 검증 영상 Vision 0.16~0.21, Caption 0.34였다(MSE 학습 0.48~0.57, 검증 0.87~0.99, 표준화 단위에서 1이 평균만 맞히는 수준). D 묶음의 2단계가 encoder 2가 이미 본 영상으로 정서 쪽을 학습해, 학습 때와 시험 때 v̂₂, ĉ₂(또는 H)의 질이 크게 다르다. (1) D-1, D-2, D-3의 2단계는 OOF v̂₂, ĉ₂로 학습한다(예비와 본실험). 바깥 fold마다 학습 fold 4개를 넷으로 나눠 하나씩 뺀 encoder 2 네 개, 원래 단위로 되돌린 뒤 바깥 fold 통계로 다시 표준화, 검증과 시험은 학습 fold 4개 전체의 encoder 2. Stimulus Model의 nested OOF(E4, O16)와 같은 구조. (2) D-4는 짝지어 학습한다. 위 encoder 2 네 개마다 head를 따로 두고 그 encoder가 보지 않은 1/4 영상의 H로만 학습, 조기 종료는 검증 fold, 시험은 네 짝 예측의 평균. 이유: H는 encoder마다 좌표가 달라 섞을 수 없다. 한계: head 하나가 약 350개 영상만 본다. D-3도 같은 짝 방식으로 한 번 더 내서 D-3 대 D-4를 같은 조건에서 비교한다(D-3 주 결과는 (1)). (3) 지금 도는 실행(s6_brain_prelim_sep, s6_brain_prelim_d34)은 버리지 않고 '이미 본 영상판'으로 SI의 학습과 시험 차이 자료로 쓴다. (4) 우리 모델을 더 고치기 전에 외부 딥러닝 기준선을 먼저 확보한다. 순서: GED(학습 fold로만 정규화) → ML-BVAE, EmoGrowth(바꾼 항목 기록) → MLP(입력: 전체 voxel, ROI 평균, ROI 8칸 평균). CNN은 그 뒤에 정한다. 평가 규칙은 O27. 구현은 작업 사본에서 하고 지금 도는 실행이 끝난 뒤 합친다. GPU 학습은 앞으로 GPU 노드 batch(sbatch, salloc)로 하고 석진 님이 띄운다(NERSC login node 정책). 같이 고침: 01의 '참가자당 학습 영상 약 1,750개'를 '가중치를 학습하는 영상 약 1,390개(검증 fold까지 약 1,750개)'로(F3 외 4곳) | 5-A, 5-2, F3, O27 | 2026-11-09 |
| fold 밖 encoder 2, 짝 학습, MLP 기준선 구현(11/9 석진 님) | (가)~(라)는 추천대로 정함: 넷으로 나누는 단위는 학습 fold 4개, fold 밖 encoder 2의 learning rate는 전체 encoder 2가 고른 값(조기 종료는 검증 feature MSE), 짝 조건의 learning rate는 네 짝 공통으로 검증 점수 평균으로 선택, 시험은 네 짝 예측 평정의 평균(짝마다의 예측도 저장해 짝 하나씩의 성능을 따로 냄). 구현: s6_common.inner_plans, prepare_fold(stats_videos), Condition.paired, brain_features_only_paired(D-3 짝), s6_train.FoldRunner.oof(fold 밖 encoder 2 넷, 원래 단위로 되돌린 뒤 바깥 fold 통계로 다시 표준화, feature_encoder_oof/seed{s}/inner{j}), oof_forward(학습 행은 fold 밖 값, 검증, 시험은 전체 encoder 2, 섞이면 멈춤), _run_paired(짝 j는 j번째 fold로 head 학습, 입력은 encoder j의 학습 영상으로 표준화, ensemble/에 평균과 짝별 예측). MLP 기준선: s5_baselines.py의 mlp 과제(full voxel, 은닉층 1개, GELU, dropout 0.1, MSE, 선형 출력, 폭 {32, 64} × 첫 층 weight decay {0.1, 1, 10} × learning rate {1e-5, 1e-4, 1e-3}, 검증 fold 정서별 r 평균으로 선택, seed 0, 1, 2, 시험 예측은 seed마다). 외부 baseline 레포 확인: GED(MIT), ML-BVAE, EmoGrowth(라이선스 없음) 모두 받을 수 있다. 라이선스 없는 코드는 공개 레포에 넣지 않는다. 실행: scripts/s6_prelim_oof_20261109.sh(D 묶음 예비, fold 밖판, 결과 s6_brain_prelim_oof), scripts/s5_baselines.sh mlp <참가자> <커밋>. 시험 s6 470개, s5 134개 통과 | 5-A, 5-2, 7-L, I7 | 2026-11-09 |
| 외부 baseline GED 구현(11/9 석진 님) | 공식 코드(github.com/zhongyu1998/GED, commit 3ea8492, MIT)의 graphcnn.py, mlp.py를 third_party/ged에 LICENSE와 함께 넣었다(torch.sparse.FloatTensor → sparse_coo_tensor만 바꿈, 계산 같음). src/s5_ged.py: 원 코드의 영역 64칸 평균(area_pooling)과 정서-영역 그래프(load_adj, l 150, m 50)를 그대로 옮기고, 우리 370개 지도와 QC mask 좌표로 입력을 만든다. 학습은 원 코드 설정(층 5, MLP 층 2, 은닉 64, dropout 0.5, MSE 합, Adam 0.01, StepLR 50 × 0.5, batch 16, 최대 300 epoch). O27대로 바꾼 것: 우리 run 6 fold, 정규화는 학습 영상의 최소~최대(평가 때 되돌림), epoch는 검증 fold에서 되돌린 예측을 [1e-6, 1 − 1e-6]로 자른 soft BCE와 patience 30으로 고름, seed 0, 1, 2. 실제 자료 확인(sub-01): 입력 404 node × 64칸, 빈 칸 31%(원 방식 그대로), 간선 3,400개. s5_baselines.py ged 과제, --folds로 fold를 나눠 낼 수 있다. 시험 s5 142개 통과 | 5-2, O27 | 2026-11-09 |
| 외부 baseline ML-BVAE 구현(11/9 석진 님) | 공개 코드(github.com/KaichengFu1997/ML-BVAE, commit 9cb9884)는 라이선스가 없어 복사하지 않고 논문(arXiv 2211.02629 3절, 4.C절)과 코드의 계산을 src/s5_mlbvae.py에 다시 짰다. 따른 것: 피질 360개 영역의 n³칸 평균(좌 180, 우 180, 차이 세 보기, 칸 평균은 공개되지 않은 전처리라 GED의 area_pooling 사용), 보기마다 encoder 512-512, decoder 512-512-512, 잠재 64, Product of Experts와 표준 정규 prior, KL annealing 100 epoch, 네 가지 입력(함께, 왼쪽, 오른쪽, 차이)의 ELBO와 분류 손실, label-aware 분류망과 정서 공존 mask self-attention, Adam 1e-4, weight decay 0.1, batch 100, 30 epoch(공개 코드), float64. 후보(원 논문 그대로, O28): 칸 수 {8, 27, 64, 125, 216, 343} × λ1/λ2 {0.001, 0.01, 0.1, 1, 2, 5, 10, 15, 20}, 검증 fold의 정서별 r 평균으로 seed 0에서 선택 후 seed 1, 2. λ2 = 0.1(공개 코드), λ1 = 비 × 0.1. 바꾼 것: 34개 평정 비율 목표, asymmetric focal loss → soft BCE, 정서 공존 mask는 학습 영상 평정을 0.1에서 이진화해 만듦, 우리 run 6 fold. 실제 자료(sub-01): 343칸이면 보기 하나 61,740차원, 모델 1.9억 가중치(Adam 포함 약 6 GB). 시험 s5 150개 통과 | 5-2, O27, O28 | 2026-11-09 |
| 외부 baseline EmoGrowth 구현(11/9 석진 님) | 공개 코드(github.com/ChangdeDu/EmoGrowth, commit b98109d)는 라이선스가 없어 복사하지 않고 논문(PMLR 267, 3절, 부록 B.4)과 코드(CLIFModel, layers, inc_net_ml, clif_ml의 첫 단계)의 계산을 src/s5_emogrowth.py에 다시 짰다. 가져온 것(01, 11/2 결정): 정서 관계 그래프(학습 영상 라벨의 대칭 조건부 확률, 평정 0.1 이진화), 고정 무작위 정서 입력 → GIN 1층(128, 256) 정서 embedding, 특징 분리(뇌 → 512 → 64, embedding → 64 sigmoid, 곱 → 64), 정서별 분류기, MultiLabelSoftMarginLoss + λ3 × 그래프 복원 손실. 입력은 피질 360개 × 8칸(2,880차원, 원 논문 Brain27), 표준화 없음. Adam 1e-4, weight decay 0.005, batch 128, 40 epoch(공개 코드 첫 단계). 뺀 것: 증분 학습과 RKD(λ1, λ2 항). λ3 ∈ {0.001, 0.01, 0.1, 1, 2, 5, 10}(원 논문 부록 B.4)을 검증 fold의 정서별 r 평균으로 seed 0에서 고르고 seed 1, 2. 34개 평정 비율 목표. 시험 s5 159개 통과 | 5-2, O27 | 2026-11-09 |
| 외부 baseline ML-BVAE 손실 수정, EmoGrowth 점검(11/10) | ML-BVAE: 11/9 실행(e21fd01)의 시험 예측이 정서마다 영상과 무관한 상수였다. 원인은 다시 짠 코드의 분류 손실이 평균(binary_cross_entropy_with_logits 기본값)이었던 것. 공개 코드의 손실(aslloss.py)은 batch와 정서 전체의 합이라, 평균이면 분류 gradient가 batch × 정서 수만큼 작아지고 Adam의 weight decay 0.1이 이겨 encoder 첫 층 가중치가 30 epoch 안에 거의 0이 된다(sub-01 fold 1에서 학습 중 가중치 크기와 예측 퍼짐을 기록해 확인). 고침: soft BCE를 reduction="sum"으로(src/s5_mlbvae.py), 합인지 확인하는 시험 추가(s5 160개 통과). 나머지 계산(encoder, decoder, Product of Experts, 분류망, ELBO, KL annealing, optimizer)은 공개 코드 model.py, train.py와 줄 단위로 다시 대조해 같았다. 11/9 ML-BVAE 결과는 superseded로 옮기고 다시 돌린다. EmoGrowth: 공개 코드(CLIFModel, layers, inc_net_ml, clif_ml)와 구조, 초기화, 손실(MultiLabelSoftMarginLoss 평균), optimizer가 같음을 다시 대조했다. 그런데 34개 평정 비율을 목표로 하면 학습 영상에서도 정서별 평균만 맞히는 상태로 수렴하고 weight decay가 첫 층을 줄인다(200 epoch까지 같음, λ3와 무관). 원 논문처럼 0.1에서 이진화한 목표로 학습하면 같은 설정에서 뇌 입력을 쓰기 시작한다. 목표를 바꿀지는 석진 님 결정 대기 | 5-2, O27 | 2026-11-10 |
| 검증 total loss로 되돌리기, Brain-IT 입력층 전 조건, 1순위 본 실행과 배분(11/10 석진 님) | (1) 조기 종료와 되돌릴 epoch: s6_train.total_val_loss. 검증 영상에 학습 손실과 같은 식을 적용하고 정서 항의 목표는 실제 y. distillation과 섞은 목표는 학습 행에서만 만들므로(train_target) 빠지고, feature 항(ac.decoding_loss, 같은 λ)과 representation 항(Teacher.o_val, 학습 행 통계로 표준화)은 더한다. feature 짝 섞기 대조군은 audition_codex의 검증 규칙대로 원래 feature. fit(restore_fn), history.tsv에 val_emotion_bce 열 추가. 정서 항만 있는 조건과 encoder 2는 예전과 같은 식. (2) Brain-IT 입력층을 모든 조건에: build_model의 막음을 roi_mean, roi_cells에만 남기고, MultimodalModel(tokenizer, voxel_sampling), D-3과 D-4의 안쪽 encoder 2, fold 밖 encoder 2, 짝 학습이 설정의 입력층을 따른다. 11/10 전 체크포인트는 tokenizer 키가 없어 선형으로 되살린다. (3) 1순위 설정 run_config_p1_linear.json, run_config_p1_brainit.json(01 7-L). (4) scripts/s6_dispatch.py, .sh와 tests/s6_dispatch_tests.py: 의존 규칙을 S의 표에서 만들고, 같은 fold를 나눠 돌릴 때 run_key가 조건 목록(Stimulus 사용 여부)에 따라 달라지는 문제와 fold 밖 encoder 2 캐시 충돌을 피하려고 fold당 갈래를 brain_only, decoded, separate_encoder, multimodal 넷으로 둔다. 어림 3시간 넘는 갈래는 sbatch(shared, GPU 시간 상한), 나머지는 login node. 동결 commit과 run worktree를 확인하고 다시 켜도 중복 실행하지 않는다. 시험: s6(total loss, Brain-IT 전 조건 생성과 체크포인트 되살리기 추가), s6_dispatch 8개 | 5-5, G13, O6, 7-L | 2026-11-10 |
| EmoGrowth 학습 라벨 이진화(11/10 석진 님) | 11/10 점검(04 위 기록)에서 평정 비율 목표로는 EmoGrowth가 학습되지 않았다. 원 논문의 라벨처럼 평정 비율을 0.1에서 이진화해 학습한다(s5_emogrowth.train_targets). 정서 관계 그래프의 이진화 기준(0.1)과 같다. 선택(검증 r)과 평가(시험 r)는 평정 비율 그대로다. 11/9 EmoGrowth 결과는 superseded로 옮기고 ML-BVAE(f5c8569에서 손실 합으로 고침)와 함께 다시 돌린다. 시험 s5 161개 통과 | 5-2, O27 | 2026-11-10 |
| 선형 입력층 voxel 뽑기(원인 분리 점검, 11/12 석진 님) | s6_model.RoiInput(voxel_sampling): 학습 때 예시마다 voxel을 Brain-IT 입력층과 같은 방식으로 복원 추출하고(전체의 voxel_sampling 비율), 선형 합이라 뽑힌 횟수에 1/비율을 곱해 기댓값을 맞춘다. 평가 때는 모든 voxel. make_input_layer와 load_config가 linear의 voxel 뽑기를 받는다(roi_mean, roi_cells는 여전히 막음). 기본값 0이면 예전과 같다. 설정 run_config_p1_linear_sampling.json(1순위 선형판 + 0.375), A-1과 B-1만, 결과 s6_brain_p1_linear_sampling. 시험: 평가 때 뽑기 없는 입력층과 같은 값, 학습 때 평균이 전체 값에 가까움, 뽑히지 않은 voxel에 기울기 없음, 설정 읽기 | 5-5, 7-L | 2026-11-12 |
| 본 실행 설정 변경(11/13 석진 님) | 원인 분리 점검(위 행) 결과에 따라 선형 입력층에 voxel 뽑기 0.375를 넣고, 입력층 weight decay 후보를 {1, 10, 100}으로 옮겼다(1순위 선형판과 점검이 6 fold 모두 끝값 10을 골랐음). 결과를 본 뒤 바꾼 설정이다. 코드 변경은 없고 설정 configs/s6/run_config_sampling_main.json만 더했다(bb23a1c). 조건 8개(A-1, A-2, B-1, C-1, C-2, 대조군 셋), d 64, learning rate 1e-4, seed 0. 실행은 bb23a1c에 맞춘 run worktree에서 scripts/s6_dispatch.sh(tag sampling_main, --sbatch-gpu-hours-cap 0, --exclude 28)로 login node에만 띄운다. 어림 18개 작업, 138회, 약 150 GPU 시간. 다시 학습하는 A-1, B-1(점검과 같은 후보)도 실행 번호가 달라 새로 돈다. 논문 한 줄: 입력층의 voxel 뽑기와 weight decay 후보는 예비 결과를 본 뒤 정했다 | 5-5, 7-L | 2026-11-13 |
| weight decay 1000 점검(11/13 석진 님) | 본 실행 A-1이 6 fold 모두 끝값 100을 골라, A-1만 weight decay 1000으로 fold마다 1회 돌린다. 설정 configs/s6/run_config_wd1000_check.json, 결과 s6_brain_wd1000_check. 코드 변경 없음. login node 6개(fold마다 하나), sbatch 없음. 비교는 selection.tsv의 검증 r(본 실행 100 대 점검 1000)만 본다 | 5-5, 7-L | 2026-11-13 |
| 370개 ROI 지도(11/13 석진 님) | src/s5_roi_map.py, scripts/s5_roi_map.sh. 참가자, 바깥 fold, ROI마다 그 ROI voxel만으로 DualRidge(학습 행 표준화). 정서는 s5_common.main_version과 같은 계산(정서마다 검증 r로 λ), Vision feature(vjepa2/target)와 Caption feature(deberta/target)는 묶음마다 검증 차원별 r 평균으로 λ 하나. 정서는 시험 예측(시험 행 × 370 × 34)을 저장하고, feature는 6 fold를 모은 r(O19)을 내도록 ROI와 차원마다 예측의 합, 제곱합, 실제 값과의 곱의 합과 실제 값의 합, 제곱합을 fold마다 저장한다(s5_roi_map.pooled_r). 시험 s5_tests.t_roi_map: 그 ROI만 넣은 main_version과 같음, 시험 fold 정답을 바꿔도 λ와 예측이 같음, 다른 ROI voxel을 바꿔도 같음, 합으로 낸 r이 이어 붙인 예측의 r과 같음(s5 166개 통과). 실제 자료 CPU 8 thread에서 ROI 하나, fold 하나에 1.6~2.4초. ROI별 교란은 S9 코드와 함께 만든다 | 6-4 | 2026-11-13 |
| S9 바꿔 끼우기와 입력 교란 구현(11/13) | src/s9_saved_models.py, scripts/s9_saved_models.sh, tests/s9_tests.py(13개 통과). 모델은 S6 selected.json의 seed 폴더 model.pt. 자료는 S6 main과 같은 함수(load_plan, load_known, load_brains, prepare_fold)로 다시 만들고, 다시 만든 voxel 표준화가 plan/standardization.npz와 다르거나 다시 계산한 g, decoded features가 outputs에 저장한 값과 다르면 멈춘다. swap: audition_codex.interchange_intervention과 summarize_interventions를 그대로 쓴다. 짝은 manifests/s2/pairs_directed.tsv에서 그 fold, 그 참가자에게 두 영상이 모두 있는 것만 쓰고 뺀 수를 pairs_used.tsv에 남긴다. 대조 seed는 (swap, 참가자, fold, seed)의 sha256에서 정한다. perturb: 선형 입력층에서 ROI 입력 교체는 그 ROI token 교체와 같으므로 token을 바꿔 넣는다(Brain-IT 입력층이면 멈춤). 실행마다 첫 참가자, 첫 묶음에서 입력을 직접 바꾼 결과와 같은지 확인한다. 배정은 같은 참가자, 같은 fold의 다른 시험 영상, 20회, seed는 (perturb, fold)의 sha256. 단위는 CAB-NP 13묶음과 ROI 370개. 참가자마다 6 fold를 모은 r을 내도록 원래와 교란 예측의 합, 제곱합, 사람 평정과의 곱의 합을 fold마다 저장한다(s9_saved_models.pooled_r) | 4-2, 5-0, 6-4b, O2, O3 | 2026-11-13 |
| learning rate × 입력층 weight decay grid 실행(11/13 석진 님) | 코드: (1) s6_common.candidates의 brain_only 후보에서 learning rate × 입력층 weight decay ≥ 1을 뺀다. (2) s6_train --only-candidates: 같은 실행 번호로 A-1 후보 일부만 seed 0으로 학습하고 선택 없이 끝낸다. 실행 번호를 맞추려고 조건 목록은 brain_only,brain_only_distill로 부른다. scripts/s6_train.sh는 다섯째 인자부터 그대로 넘긴다. (3) scripts/s6_grid.py: A-1 후보를 learning rate별 묶음(1e-5는 둘로 나눔)으로 나눠 빈 login node GPU에 띄우고, fold마다 plan을 만든 뒤 나머지를 띄운다. 사라지면 한 번 다시 띄우고 sbatch는 내지 않는다. (4) s6_dispatch --split-decoded: 장면 특징 줄을 (B-1, feature 섞기, Stimulus 예측 섞기)와 (C-1, C-2)로 나눈다. sbatch 시간 상한은 shared QOS 상한(48시간, sacctmgr)까지로 올렸다. 시험: s6_tests.t_grid_1113, s6_dispatch_tests.t_split_decoded, t_grid_groups(10/10), t_sbatch_routing의 상한 값 갱신. 실행: 1단계 A-1 grid 24개 작업(102회, login node), 2단계 dispatcher 18개 작업(120회). 작업 하나의 어림이 24시간을 넘으면 sbatch로 낸다(석진 님 11/13). 설정 configs/s6/run_config_grid_main.json, 결과 s6_brain_grid_main | G13, 5-5, 7-L | 2026-11-13 |
| 2단계 실행 방식(11/14 석진 님) | A-1 grid가 끝나 6 fold 모두 learning rate 1e-3, 입력층 weight decay 100을 고르게 되었다. C-1, C-2 줄을 GPU 한 장에서 차례로 돌리면 fold 1, 2, 4, 5에서 24시간을 넘고 sbatch로 내면 남은 할당을 거의 다 쓴다. 그래서 1단계처럼 후보를 나눠 login node에 띄운다. src를 고치면 실행 번호가 바뀌어 A-1 102회를 다시 학습해야 하므로 src는 그대로 두고, scripts/s6_candidates.py가 run worktree의 s6_train을 불러 같은 실행 번호로 지정한 조건의 후보만 학습한다(실행 번호가 다르면 FoldRunner의 plan 검사와 selected()가 멈춘다). A-1 선택만 읽는 조건(A-2, label smoothing, B-1, 대조군 셋, C-1)만 받는다. scripts/s6_grid.py --target이 fold마다 A-1 선택이 생긴 뒤 조건마다 후보를 묶어 띄운다. 순서: dispatcher(brain_only 줄: A-1 선택, A-2, label smoothing) → s6_grid --target(C-1 2개씩, B-1, feature 섞기, Stimulus 섞기) → dispatcher --split-decoded(나머지 선택과 C-2). 시험 s6_dispatch_tests.t_target_mode(11/11) | G13, 7-L | 2026-11-14 |
