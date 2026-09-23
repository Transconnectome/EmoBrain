---
title: "EmoBrain Phase 0–3 data audit"
subtitle: "action_items_v1.md A0-*, A1-*, A2-*, A3-* 실행 결과와 Gate 0 판정"
date: "2026-09-23"
---

# 0. 이 문서의 지위

`action_items_v1.md` 의 Phase 0–3 만 실행한 결과다. 모델은 학습하지 않았다. 모든 수치는
실제 파일과 metadata 에서 측정한 값이고, 설계 문서에 적힌 수치는 `claims` 로 따로 두고
대조했다. 각 산출물에는 source path, file hash, git commit, python 경로, asset registry
hash 가 provenance header 로 들어있다. 기존 산출물은 덮어쓰지 않고
`manifests/superseded/<이름>.<이전 mtime>` 으로 이동한 뒤 새로 썼다.

재실행은 `bash /pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code/run_all_phase0_3.sh` 하나로 된다.

**설계 문서 5종은 이 저장소에 없었다.** 대화 첨부로만 존재해 소실 위험이 있었으므로
`prereg_v2/design_docs/` 로 복원해 두었고, p0 가 각 문서의 sha256 을 기록한다. 이 audit 의
모든 판정은 그 hash 의 문서 본문을 기준으로 한다.

# 1. 확인된 dataset 구조

## 1.1 cohort

| prereg_v2 | 역할 | local 상태 |
|---|---|---|
| D1 Mind Captioning ds005191, 6 participants | **primary** | **존재하지 않음** (`/pscratch/sd/s/sjmoon/ds005191` 없음) |
| D2 Horikawa 2020, 5 participants | replication | 존재. 이 audit 의 전체 대상 |
| Emo-FilM (ds004872, Emo-FilM) | prereg_v2 D1–D8 에 역할 없음 | 디렉터리는 있으나 전부 git-annex symlink. 실데이터 미다운로드 |

## 1.2 자극

| 항목 | 값 |
|---|---|
| video 파일 | 2,196 (`0001.mp4`–`2196.mp4`), 1.79 GB, 전부 h264 |
| raw sha256 unique | 2,181 |
| decoded-frame sha256 unique | 2,181 |
| canonical stimulus (near-duplicate 병합 후) | **2,180** |
| decode 실패 | 0 |
| resolution | 서로 다른 값 900개 이상 (`82x146` ~ `1920x1080`) |
| frame rate | 1.25 ~ 100 fps, 55개 값 |
| container duration | 0.152 ~ 90.07 s, 평균 6.61 s |
| audio stream 보유 | **4개** (745, 1420, 1875, 1951), 전부 실제 소리 있음 |

## 1.3 annotation

| 항목 | 값 |
|---|---|
| label 행 | 2,185 × 53 |
| key | `stim_num_int` 1–2185, 중복 0, 결측 0 |
| EmoBrain / EmoViS 사본 | byte-identical |
| 34-D | `score_0`–`score_33`, 범위 [0,1], 결측 0, zero 비율 73.75% |
| 34-D 자극당 non-zero 범주 | 평균 8.92 (min 1, max 28) |
| 34-D row sum | 평균 1.714, min 1.000, max 4.273 → **합이 1이 아님** |
| 14-D | 14개 전부 존재, 범위 [1,9], 결측 0 |
| caption | 43,920행, video 2,196개 × 정확히 20개씩, 빈 문자열 0 |

## 1.4 fMRI

| 항목 | 값 |
|---|---|
| participants | 5 (sub-01 ~ sub-05) |
| `fmri_raw.npy` | (5, 2196, 450) float32 |
| `roi_timeseries/sub-0N.pt` | `roi_timeseries` (2185, 47, 450), `roi_mean` (2185, 450), `mask`, `original_T`, `stim_num` |
| parcel | 450 (Schaefer cortical + Tian subcortical) |
| session / run | 8 session, 61 run, 전 참가자 동일 |
| presentation | 2,196 + baseline block 61개 |
| presented duration | 10 ~ 94 s (TR 2.0s 기준 5 ~ 47 TR), 평균 12.16 s |
| voxel level | `EmoViS/data/raw/step7_voxel`, 70.7 GB, 자극당 (97,115,97,T) MNI |

## 1.5 직접 검증한 정합성

- `fmri_raw[s, j, :]` 는 subject `s` 의 자극 `j+1` 에 대한 `roi_mean` 과 동일하다
  (max abs diff 2.4e-07). 문서에 적힌 대응이 아니라 값으로 확인했다.
- `main_stim_indices.npy` 는 `arange(2185)` 이다. 선택 index 가 아니라 항등 index다.
- 5명의 자극 key 집합이 완전히 동일하다.
- `roi_timeseries` 의 `original_T` 가 event sidecar 의 `duration_tr` 과 전 자극에서 일치한다
  (불일치 0). 파생 뇌 데이터가 event 기록에 올바르게 정렬되어 있다.
- run 내 presentation 중첩 0, 중복 onset 0, 결측 timing 0.

# 2. 생성된 manifest 와 crosswalk

```text
prereg_v2/
  design_docs/        복원된 설계 문서 5종 (p0 가 sha256 기록)
  code/               .py 8개 + 각각의 .sh + run_all_phase0_3.sh
  manifests/
    file_inventory.tsv        2,206행. 파일별 size, mtime, sha256
    datasets.tsv              12행. asset 별 존재 여부와 declared role
    declared_paths.json       데이터 파일이 참조하는 경로 검증, 설계 문서 hash
    stimuli.tsv               2,196행. raw/decoded hash, 해상도, fps, duration, audio
    stimulus_crosswalk.tsv    2,196행. canonical id × label × brain × caption
    duplicate_report.tsv      30행 (raw 15 + decoded 15 group)
    near_duplicate_pairs.tsv  16행. signature 상관 기반
    participants.tsv          5행
    events_audited.tsv        11,285행. participant × session × run × onset × duration
    runs.tsv                  305행 (5 × 61)
    event_audit.json          timing 무결성과 반복 구조 판정
    repeat_reliability.json   반복 제시의 뇌/annotation 일치도
    target34_codebook.tsv     34행
    target14_codebook.tsv     14행
    target_lowdim_mapping.json
    annotation_audit.json
    superseded/               이전 산출물 보존
  splits/
    outer_folds.tsv           2,180행
    inner_folds.tsv           8,720행
    folds.json                fold 멤버십 + folds_sha256
    split_config.json         seed, fold 수, 실현된 균형
  configs/
    inference_contract.json   A3-4
    environment.lock.json     A0-2
  tests/
    leakage_report.json
    leakage_negative_control.json
    test_inference_contract.py
  logs/
```

## 2.1 A1-3 방법 보완

시스템 ffmpeg(3.4.2)에 h264 decoder 가 없어 decoded-frame 작업이 불가능했다.
`/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg` (7.0.2) 로 디코딩했다.

처음 쓴 difference hash 는 **해상도가 다른 같은 장면을 놓쳤다.** 그래서 32×32 gray 로
디코딩한 뒤 8×8 block mean 을 16 frame 으로 시간 resampling 한 1,024차원 signature 로
교체했다. 이 signature 는 해상도, frame rate, 길이에 불변이다. exact duplicate 15쌍을
모두 회수하고 hash 가 놓친 1쌍을 추가로 잡았다.

# 3. 발견된 불일치

## 3.1 2,180 / 2,181 차이 — 해소됨

```
2,196 video 파일  = presentation 수. 전부 fmri_raw 행과 caption 을 가진다
  − 11             video 2186–2196. annotation 행도 roi_timeseries 항목도 없다
= 2,185 annotated  label 행 수, 참가자별 roi_timeseries 자극 수
  − 4              (259,866) (472,859) (846,1673) (2157,2184). decoded 내용이 byte 동일
= 2,181            content hash 기준 unique  →  prereg_v2 D5 replication, README 와 일치
  − 1              (1349,1363). 같은 장면의 332×240 / 276×200 판본. frame별 r ≈ 0.999
= 2,180            near-duplicate 병합 후 unique  →  prereg_v2 D5 primary 와 일치
```

**2,180 과 2,181 의 차이는 정확히 rescaled 복제본 한 쌍이다.** 두 수치 모두 이 하나의
자극 집합에서 나온다. 서로 다른 두 cohort 의 자극 수가 아니라, 같은 집합을 어떤 기준으로
세느냐의 차이일 가능성이 높다. 이 판정은 파일 내용 해시에 근거하며 파일명이나 문서
기술에 근거하지 않는다.

한편 video 2186–2196 은 video 1–11 과 decoded 내용이 byte 동일하다. 즉 **실험 말미에
앞부분 11개 자극을 재제시한 것**이고, 그 11개 제시의 뇌 반응은 `fmri_raw` 에만 있고
`roi_timeseries` 에는 없다.

## 3.2 반복 제시 72개가 없다

| | |
|---|---|
| prereg_v2 D5/D7 주장 | repeated test 72 자극 |
| 파일 번호 기준 측정 | 반복 0 (2,196개가 각각 1회) |
| **canonical content 기준 측정** | **16 자극이 2회 제시** |
| 그중 두 제시가 모두 annotation 을 가진 것 | **5** |

`roi_timeseries` 안에서만 보면 반복은 5개뿐이고, `fmri_raw` 까지 쓰면 16개다. 72개는 없다.

이것이 영향을 주는 항목은 prereg_v2 D7, B9, 그리고 action_items A4-2 전부다. 그 셋 모두
반복 제시를 전제로 reliability, noise ceiling, 최종 held-out 평가, 그리고 기존 block
response 와 GLMsingle 사이의 label-blind 선택을 수행하도록 되어 있다.

크기뿐 아니라 크기의 의미를 보기 위해 일치도 자체를 측정했다 (label-blind, 기술적).

| | 값 |
|---|---|
| ROI pattern 반복 상관 (16자극 × 5명 = 80관측) | 평균 r = 0.182, 중앙값 0.210, 범위 −0.442 ~ 0.660 |
| 자극 불일치 null (같은 자극 vs 무작위 다른 자극) | 평균 r = −0.011, sd 0.231 |
| 반복 − null | 0.192 |
| 34-D annotation 반복 일치 (5쌍) | 평균 r = 0.650, 최소 0.277 |
| 14-D annotation 반복 일치 (5쌍) | 평균 r = 0.831 |

읽는 방법. 450-parcel block mean 표상에서 같은 자극의 두 제시는 서로 r ≈ 0.18 로만
일치하고, 이는 null 의 1 표준편차 안쪽이다. 이 값이 이 표상에서 자극 고정 성분을 예측할
때의 상한이다. 동시에 같은 클립에 대한 두 번의 34-D 평정이 r ≈ 0.65 로만 일치하므로,
target 쪽에도 상당한 잡음이 있다. 두 수치 모두 관측 수가 각각 80과 5로 작아 정밀도가
낮고, 반복쌍 중 11개는 한쪽이 실험 말미 block 이라 session 차이가 섞여 있다. 그러므로
estimator 선택의 근거로는 쓸 수 없고 기술 통계로만 취급해야 한다.

## 3.3 무음 자극이라는 기술이 틀렸다

`README.md` 는 이 자극 집합을 무음으로 기술하고, 무음이 "사운드트랙·대사·음향을 추가
통제 없이 배제한다"고 설계상의 이점으로 제시한다. 실제로는 4개 클립이 audio stream 을
가지며 전부 실제 소리가 있다.

| video | mean volume | max volume |
|---|---|---|
| 745 | −12.4 dB | 0.0 dB |
| 1420 | −21.5 dB | −5.9 dB |
| 1875 | −19.2 dB | −3.6 dB |
| 1951 | −12.8 dB | 0.0 dB |

4개 모두 modeling 집합(1–2185) 안에 있다. 스캐너에서 실제로 소리가 재생되었는지는 local
파일로 알 수 없다. 그러나 파일 수준의 기술은 사실과 다르므로 README 문장을 고치거나,
"제시 시 무음이었다"는 별도 근거를 제시해야 한다.

## 3.4 34-D 는 다중 선택 비율이다

row sum 이 1이 아니다 (평균 1.714, 최대 4.273). 각 열은 그 범주를 선택한 평정자의 비율이고
평정자는 여러 범주를 선택할 수 있다. row sum 은 그 자극에서 평정자 1인이 고른 범주 수의
평균이다. **단일 선택 분포가 아니므로 softmax 는 적용 대상이 아니다.** prereg_v2 L1 의 기술과
일치한다.

`CONTEXT_EMOBRAIN.md` 의 "자극당 평균 활성 범주 1.7개" 는 row sum 을 가리킨 것이고,
"non-zero 범주 8.92개" 와 모순되지 않는다. 두 값은 서로 다른 양이다.

## 3.5 rater 수는 부분적으로만 복원된다 (A2-1, prereg_v2 L10)

값이 놓인 격자 간격이 평정자 수를 식별한다.

- **34-D.** 모든 값이 어떤 k/n 위에 있고, 2,185 자극 전부에서 최소 분모가 존재한다
  (7 ~ 32, 중앙값 13). k = round(p·n) 이 전 자극에서 정확히 재구성된다. 그러나 모든 자극에
  동시에 맞는 단일 n 은 없고, 각 자극은 자기 분모와 그 정수배를 모두 허용한다. 즉 k/n 은
  정확하지만 **n 자체는 확정되지 않는다.** n 이 2배 틀리면 binomial likelihood 의 가중이
  2배 달라지므로, prereg_v2 L10 과 A2-1 의 "k,n 확인" 조건은 충족되지 않는다.
  → primary loss 는 unweighted SoftBCE 유지. binomial NLL 은 confirmatory 에 넣지 않는다.
- **14-D.** 모든 값이 1/9 격자 위에 있고 유효 n 은 9의 배수뿐이다. 1–9 척도를 **9명**
  (또는 9의 배수) 평정자로 평균한 값이다.

## 3.6 로컬 파일로 확인할 수 없는 것

- **34-D 범주 이름과 순서.** 열 이름이 `score_0`–`score_33` 로 위치 정보뿐이다. Cowen-Keltner
  범주 순서를 원 배포본에서 복원하기 전에는 범주별 주장을 할 수 없다. A2-1 은 그 순서를
  pipeline 전반에서 hash 로 고정하도록 요구한다.
- **14-D 방향과 역채점.** 범위가 [1,9] 이고 9명 평균이라는 것은 측정했으나, 각 차원의
  질문 문구와 극성은 어떤 로컬 파일에도 없다. A2-2 의 codebook 대조를 수행할 수 없다.
- **VA-2 / VAD-3 mapping.** `valence_score`, `arousal_score`, `dominance_score` 열이
  존재하고 이름이 구성개념과 일치하지만, A2-3 이 요구하는 방향 확인이 불가능하다.
  prereg_v2 L3 의 "dominance mapping 이 불충분하면 VAD-3 제거" 결정을 아직 내릴 수 없다.

## 3.7 경로와 환경

- label 의 `video_path` 열이 `/pscratch/sd/s/sjmoon/EmoFM/videos/CowenEmotionVideos/` 를
  가리키는데 이 경로는 없다. 실제 파일은 `EmoViS/data/raw/CowenEmotionVideos/` 에 있다.
- step7 전처리 provenance 가 참조하는 `/storage/bigdata/Horikawa/preprocessing_output` 과
  `/storage/bigdata/Horikawa/raw` 는 이 시스템에 없다. **raw BOLD 와 원본 `events.tsv` 가
  없다**는 뜻이고, A4-2 의 GLMsingle 경로가 현재 불가능하다.
- `brain-jepa-env` 에 **nilearn 이 없다** (A4-3 atlas mapping 필요). `tribev2/.venv` 에는
  nilearn 이 있으나 torch 가 깨져 있다 (`torch_shm_manager` 없음).
- 어느 환경에도 **pytest 와 glmsingle 이 없다.** 테스트는 pytest 없이 직접 실행되도록 작성했다.

## 3.8 34-D 과 log1p_z 의 충돌

`README.md` 와 `docs/paper_logic_merged.md` 는 decoder target 을 `log1p_z` 로 기술한다.
prereg_v2 L8 은 raw [0,1] proportion 을 확정하고 z-score 와 log1p 를 금지한다. 둘은 동시에
성립할 수 없다. 저장된 값은 raw [0,1] 이므로 데이터는 L8 과 일치한다.

# 4. Leakage 검사 결과

`splits/` 의 분할은 **canonical stimulus** 단위이며, 전 참가자가 같은 2,196 제시를 보았으므로
fold vector 가 참가자 간 동일하다는 것이 구조적으로 성립하고, 이를 가정이 아니라 hash 로
확인했다.

| 항목 | 값 |
|---|---|
| 분할 단위 | canonical_stimulus_id |
| 자극 수 | 2,180 |
| outer fold | 5 × 436 |
| inner fold | outer train 안에서 5개 |
| seed | 20260923 |
| folds_sha256 | `8f82e381626e5c95da9fa005d08e4d9eeb9fda0a240684b4aeea2e3168ce6ea2` |
| fold 간 범주 평균 최대 차 | 0.0287 |

8개 검사 전부 통과.

1. 모든 canonical 자극이 정확히 하나의 outer fold 에 속함
2. outer fold 쌍 교집합 0
3. **중복·near-duplicate 파일이 같은 outer fold 에 묶임**
4. outer fold 배정이 참가자 간 동일 (fold vector sha256 5개 일치)
5. 모든 참가자 자극이 fold 를 가짐
6. inner fold 가 outer test 와 disjoint
7. inner fold 가 outer train 을 정확히 1회 분할
8. 분할 집합이 annotation ∩ brain 집합과 정확히 일치

## 4.1 검사가 실패할 수 있음을 보인 negative control

통과만 하는 검사는 증거가 아니다. 같은 seed·같은 fold 수로 **파일 번호** 에 대해 분할하면
(content hash 없이 자연스럽게 나오는 분할) 5개 중복 그룹 중 **4개가 fold 를 가로질러 쪼개진다.**

```
[259, 866]   -> fold 2, 3
[472, 859]   -> fold 0, 2
[846, 1673]  -> fold 1, 3
[1349, 1363] -> fold 0, 2
```

3번 검사는 이 분할에서 실패한다. 따라서 canonical 분할의 통과는 정보를 담는다.

동시에 이 쌍들의 annotation 일치도가 낮다는 점이 중요하다.

| 쌍 | 34-D 프로파일 r | max abs diff |
|---|---|---|
| 259, 866 | 0.707 | 0.343 |
| 472, 859 | 0.664 | 0.467 |
| 846, 1673 | 0.685 | 0.167 |
| 1349, 1363 | 0.916 | 0.182 |
| 2157, 2184 | 0.277 | 0.583 |

같은 영상인데 두 번의 평정이 r = 0.28 ~ 0.92 로만 일치한다. 즉 이 leakage 는 정답을
그대로 넘겨주지는 않지만, 자극 수준 일반화를 측정해야 할 held-out 점수에 기억된 자극을
섞는다.

## 4.2 A3-4 통계 단위 계약

`configs/inference_contract.json` 에 동결했고 5개 테스트가 통과한다.

- 추론 단위는 **참가자**, 일반화 단위는 자극, seed 는 추론 표본이 아니다
- 자극쌍 2,556개를 독립 관측으로 세지 않는다
- bootstrap 은 참가자를 cluster 로 resample 한다. 참가자 offset 이 있는 자료에서
  participant-clustered 구간이 stimulus-level 구간보다 3배 이상 넓어야 한다는 테스트로
  clustering 이 실제로 일어나는지 확인한다
- 참가자가 5명이므로 구간이 넓다. stimulus-level resampling 에서만 유의한 대비는 이
  계약 하에서 증거가 아니다

# 5. 아직 결정해야 할 사항

## 5.1 진행을 막는 것

1. **primary cohort 가 없다.** prereg_v2 D1 은 Mind Captioning ds005191 (6명) 을 primary 로,
   Horikawa (5명) 를 replication 으로 지정한다. ds005191 이 이 시스템에 없다. 선택지는
   (a) ds005191 를 확보한다, (b) 역할을 맞바꾸고 그 변경을 결과를 보기 전의 변경으로
   기록한다. (b) 를 택하면 A3-3 replication freeze split 의 의미도 다시 정의해야 한다.
   어느 쪽이든 결정 전에는 D3·D4 의 participant 독립성 확인도 불가능하다.
2. **반복 제시 72개가 없다 (실측 16, annotated 5).** D7, B9, A4-2 를 그대로 실행할 수 없다.
   대안은 (a) reliability·noise ceiling·최종 held-out 을 반복 없이 재정의한다,
   (b) 16개로 기술 통계만 보고하고 estimator 선택을 다른 label-blind 기준으로 바꾼다,
   (c) 원 데이터셋에 반복 session 이 따로 있는지 확인해 확보한다.
3. **raw BOLD 와 events.tsv 가 없다.** A4-2 의 GLMsingle 경로가 불가능하다. 기존 block
   response 를 primary 로 고정하거나 raw 를 확보해야 한다.
4. **nilearn 이 작업 환경에 없다.** A4-3 atlas mapping 에 필요하다. `brain-jepa-env` 에
   설치하거나 torch 가 성한 별도 환경을 정해야 한다.

## 5.2 동결 전 확인이 필요한 것

5. **34-D 범주 이름과 순서** 를 원 배포본에서 복원하고 hash 로 고정 (A2-1).
6. **14-D codebook** 을 확보해 각 차원의 방향과 역채점 확인 (A2-2). 확보 못 하면 어떤
   차원을 primary 에서 뺄지 결과를 보기 전에 결정해야 한다.
7. **VA-2 / VAD-3 열 매핑과 방향** 확정, dominance 가 불충분하면 VAD-3 제거 (A2-3, L3).
8. **34-D target 변환.** prereg_v2 L8 의 raw [0,1] 과 README·paper_logic_merged 의 `log1p_z`
   중 하나를 고르고 다른 쪽 문서를 고쳐야 한다.
9. **binomial NLL 을 robustness 로 돌릴지.** n 이 정수배까지만 복원되므로 돌린다면 최소
   분모와 그 2배 두 조건을 함께 보고해야 한다.
10. **fold 수.** prereg_v2 와 implementation_v2 어디에도 outer/inner fold 수가 없다. 현재
    분할은 5/5, seed 20260923 이며 `split_config.json` 에 `PROVISIONAL` 로 표시했다.
11. **stratification.** A3-1 은 사전 정의된 summary 로만 허용하는데 정의된 것이 없어
    무층화로 두고 실현 균형만 보고했다 (fold 간 범주 평균 최대 차 0.0287).
12. **near-duplicate 임계값.** signature 상관 0.98 이상을 같은 자극으로 병합했다. 이 값이
    2,180 과 2,181 을 가른다. 임계값을 확정하거나, 1349/1363 을 sensitivity set 으로 빼는
    쪽을 택해야 한다.
13. **제시 길이 이질성.** 10 ~ 94 s 이고 대부분 10 s 다. 고정 길이 boxcar 가정은 틀리며,
    prereg_v2 B10 의 duration 민감도 분석 범위를 정해야 한다.
14. **해상도·frame rate 이질성.** 900개 이상의 해상도와 1.25 ~ 100 fps 가 섞여 있다.
    V-JEPA 2 와 low-level control 의 전처리에서 이것들이 자극 정체와 교락되지 않도록
    입력 규격을 결과를 보기 전에 고정해야 한다 (F0, F1).
15. **audio 4개 클립 처리.** README 수정과, 필요하면 민감도 분석에서 제외할지 결정.

# 6. Gate 0 판정

Gate 0 은 "participant, stimulus, annotation, brain response 가 one-to-one 또는 명시적인
one-to-many key 로 연결되고 2,180/2,181 차이가 설명되어야 한다" 이다.

**Horikawa cohort (prereg_v2 D2) 에 대해서는 통과한다.**

- 2,196 video ↔ 2,196 fmri_raw 제시 ↔ 2,196 caption 집합이 1:1 이다
- 2,185 annotation 행 ↔ 2,185 roi_timeseries 자극이 1:1 이고, 제외된 11개의 정체가 확인된다
- canonical stimulus ↔ video 파일이 명시적 one-to-many 이며 그 many 가 content hash 로 열거된다
- 참가자 5명 × 2,196 제시가 session, run, onset, duration 수준까지 유일하게 연결되고
  timing 위반이 0이다
- 2,180 과 2,181 의 차이가 rescaled 복제본 한 쌍으로 완전히 설명된다
- 8개 leakage 검사가 통과하고, 그 검사가 실패할 수 있음을 negative control 로 보였다

**그러나 prereg_v2 가 쓰인 대로의 설계에 대해서는 통과하지 못한다.** D1 primary cohort 의
데이터가 이 시스템에 없어 primary 쪽 key 연결을 판정할 수 없고, D7 의 repeated test 72 는
실재하지 않는다.

## 판정

> **Gate 0: CONDITIONAL PASS.**
> 자극·annotation·뇌 반응·event 의 key 구조는 완전히 해소되었고 2,180/2,181 도 설명되었다.
> Phase 4 는 **Horikawa cohort 단독**으로, 그리고 §5.1 의 1–4 에 대한 결정을 기록한 뒤에만
> 시작할 수 있다. 특히 §5.1 의 2 와 3 은 Phase 4 의 내용 자체를 바꾸므로 (A4-2 가 현재
> 형태로 실행 불가능하다) 결정 전에 Phase 4 를 시작하면 A4-2 를 사후에 재정의하게 된다.
> prereg_v2 §3 의 primary/replication 역할은 현재 상태로 집행할 수 없으며, 결과를 보기
> 전에 재지정하고 그 사실을 변경 이력에 남겨야 한다.

## 다음 단계 제안 순서

1. ds005191 확보 여부를 결정한다. 확보하지 않으면 D1/D2 역할을 맞바꾸고 prereg_v2 §3 과
   §14 체크리스트를 결과를 보기 전에 갱신한다.
2. 반복 제시가 원 데이터셋에 따로 있는지 확인한다. 없으면 D7·B9·A4-2 를 재정의한다.
3. raw BOLD 확보 여부로 A4-2 의 GLMsingle 경로를 살릴지 접을지 정한다.
4. 34-D 범주 순서와 14-D codebook 을 원 배포본에서 확보한다.
5. §5.2 의 나머지를 `freeze_manifest.json` 에 동결한다 (A0-3, implementation_v2 3.2).
