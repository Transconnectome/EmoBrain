---
title: "Horikawa 전처리 전수검사"
subtitle: "어느 단계를 유지하고 어느 단계부터 다시 할지에 대한 판정"
date: "2026-09-28"
---

# 0. 범위와 근거

검사 대상은 이 시스템에 있는 Horikawa 파생물 전부다.

| 대상 | 수량 | 검사 방식 |
|---|---|---|
| step7 NIfTI 구간 | 5명 × 2,257 = 11,285 (70.7 GB) | 전수, voxel 단위 |
| filtered frame (MONAI) | 66,755 | 전수, 값 단위 |
| ROI CSV | 10,985 쌍 | 전수, 재계산값과 대조 |
| `roi_timeseries/sub-XX.pt` | 5 | 전수 |
| `fmri_raw.npy` | 5 × 2,196 × 450 | 전수 |

판단의 기준 문서는 Horikawa et al. (2020) iScience 23, 101060 의 Transparent Methods 원문이다
(`docs/reference/papers/` 의 PDF 에서 직접 확인). 모든 검사는 label 을 쓰지 않았다.
단 q3b 는 뇌 반응 없이 자극 배치와 annotation 의 관계만 본다.

코드는 `prereg_v2/code/q0`–`q3b`, 산출물은 `prereg_v2/qc/`, 재실행은
`bash /pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code/run_all_preproc_qc.sh`.

# 1. 파생 경로

```
원자료 (OpenNeuro ds002425)                         이 시스템에 없음
  → step1–6 재전처리 (MNI, run 단위 z-score)          이 시스템에 없음, 기록 없음
  → step7 구간 NIfTI                                   EmoViS/data/raw/step7_voxel
      ├→ horikawa_parcellation.py (nilearn, mask 없음)
      │    → ROI CSV → build_roi_timeseries.py → .pt → (fmri_raw.npy)
      └→ MONAI (builder 접근 불가) → filtered frame → SwiFT·NeuroSTORM 임베딩
```

원 논문의 분석은 **native space** 에서 이루어졌다 ("resampled onto their original space (2 × 2 × 2 mm
voxels)"). 우리가 가진 MNI 데이터는 논문의 파이프라인이 아니라 별도 재전처리의 산물이고,
그 템플릿, nuisance 회귀, 필터링에 대한 기록이 없다.

# 2. 단계별 판정

| 단계 | 판정 | 근거 |
|---|---|---|
| step1–6 (재전처리) | **검증 불가 · 논문과 일부 다름** | 입력이 없다. despike 흔적이 없다 (§3.6). 템플릿 불명 (§3.3) |
| step7 구간 분할 | **통과** | §3.1, §3.2 |
| 반응 구간 (4 s 지연 포함) | **통과** | §3.4 |
| atlas 적용 | **조건부. 수정 필요** | §3.3, §3.5 |
| CSV → `.pt` → `fmri_raw` | **통과** | §3.7 |
| 표본 선택 (중복 처리) | **수정 필요** | §3.8 |
| filtered frame | **불통과. 재생성 필요** | §3.9 |

# 3. 세부 결과

## 3.1 step7 구간은 run 을 손대지 않고 자른 것이다

- 11,285개 모두 97×115×97, 2 mm, float32, qform/sform code 4, affine 동일
- TR 수가 meta 의 `duration_tr` 과 전부 일치, NaN·Inf·전부 0인 volume 0
- 305개 run 모두 TR 0 부터 빈틈·겹침 없이 이어진다 (경계 10,980개 중 불연속 0)
- 이어붙인 run 은 voxel 마다 평균 |0.0014|, 표준편차 0.9998. 모든 run 에서 voxel 100% 가 ±0.02
  이내다. step6 가 run 전체를 z-score 했고 step7 은 자르기만 했다
- 경계에서의 TR 간 변화량이 구간 안 변화량과 같다 (중앙값 비율 1.009, 최대 1.073). 구간별 재정규화가 없다

따라서 **step7 로부터 run 전체를 정확히 복원할 수 있다.** 이 사실이 §4 의 수정 경로를 가능하게 한다.

## 3.2 구간 길이는 논문의 설계와 일치한다

원문. "For stimulus blocks with videos shorter than 8 s, the same video stimulus was repeatedly presented
until the total presentation duration went beyond 8 s ... All stimulus blocks were followed by an additional
2-s rest period. Additional 32- and 6-s rest periods were added to the beginning and end of each run."

구간 최소 10 s (8 s 반복 재생 + 2 s 휴지), 영상 파일 평균 6.6 s 라는 불일치는 이것으로 설명된다.

## 3.3 atlas 와 fMRI 의 템플릿이 다를 수 있다

- fMRI 격자 97×115×97, 원점 (−96.5, −132.5, −78.5)
- atlas 는 FSL MNI152 (MNI152NLin6Asym) 91×109×91, 좌우 반전 저장
- 두 격자는 축마다 1/4 voxel 어긋나 nearest 대응 자체는 모호하지 않고 450개 label 이 모두 살아남는다
- 그러나 fMRI 가 어떤 MNI 템플릿으로 정규화됐는지 기록이 없다. 격자 크기는 fMRIPrep 의
  MNI152NLin2009cAsym 2 mm 와 같다. 그렇다면 두 템플릿은 수 mm 다르고, 차이는 복측·전두엽에서 크다

## 3.4 반응 구간은 이미 4 s 지연이 보정돼 있다

처음 가설은 "지연 보정 없이 잘라 직전 클립 반응이 섞인다" 였다. **이 가설은 틀렸다.**

- run 시작 곡선 (32 s baseline 뒤 첫 자극) 에 canonical block 반응을 맞추면, 데이터는 자극이
  명목 onset 보다 평균 **4.9 s** (3.0–6.5 s) 먼저 시작된 것처럼 행동한다
- 원문. "The data were temporally shifted by 4 s (2 volumes) to compensate for hemodynamic delays"
- label 없이 비교한 반복 신뢰도 (16쌍, 서로 다른 위치·직전 자극에서 제시되어 오염에 면역)

| 구간 | −2 TR | −1 TR | **0** | +1 TR | +2 TR | +3 TR | +4 TR | GLM |
|---|---|---|---|---|---|---|---|---|
| 반복 r (5명 평균) | 0.106 | 0.142 | **0.158** | 0.150 | 0.124 | 0.096 | 0.080 | 0.067–0.080 |

참가자별 최적은 −1 ~ +2 TR 로 갈린다. 쌍이 16개라 참가자 단위 추정은 잡음이 크다. 평균으로는 현재 구간이
가장 지지되고 **바꿀 근거가 없다.** 이것이 최적이라는 증명은 아니다.

남는 현상이 하나 있다. 인접 자극의 패턴이 먼 자극보다 **덜** 비슷하다 (참가자 내 −0.133, 참가자 간 비율
−0.13). 직전 클립 반응의 사후 undershoot (canonical HRF 에서 정점의 약 1/6) 가 다음 구간에 들어오면 이
크기의 음의 상관이 나온다. 신경 적응으로도 설명될 수 있어 둘을 구분하지 못했다. 5명의 제시 순서가 완전히
같으므로 이 성분은 참가자 간에 공유되고, 참가자 간 일치도를 "공유된 자극 반응" 으로 읽을 때 섞여 들어간다.

GLM (LSA, canonical HRF) 은 onset 을 보정해도 인접 beta 가 거의 같게 나온다 (참가자 간 비율 0.95). 빈틈 없는
설계에서는 자극 regressor 의 합이 상수에 가까워 절편과 저주파 drift 에 공선적이기 때문이다. **이 설계에서
단일 시행 GLM 은 그대로는 불량조건이다.** GLMsingle 을 쓰려면 이 점을 먼저 해결해야 한다.

## 3.5 신호 소실 parcel 과 run 간 희석

brain mask 는 run 마다 조금씩 다르다 (모든 run 공통 228–244k voxel, 어느 run 에든 포함 262–272k).
전형적인 자기장 불균일 부위에서 parcel 이 절반 넘게 비는 경우가 있다.

| 위치 (MNI 중심) | 예 |
|---|---|
| 내측 안와전두 · 복내측 전전두 | (9, 63, −14) 최저 덮임 0.075, (−15, 64, −8), (8, 47, −23) |
| 측두극 | (−25, 6, −38), (−37, −5, −42), (28, −1, −40) |
| 후두극 · 하후두 | (25, −97, −10), (−24, −97, −12) |

한 참가자라도 절반 미만으로 덮이는 parcel 19개, 80% 미만 59개. Tian 피질하 50개는 모두 80% 이상.
**H3 의 대상인 mPFC 가 이 목록에 들어 있다.**

더 큰 문제는 평균 방식이다. `horikawa_parcellation.py` 는 mask 없이 parcel 안의 모든 voxel 을 평균하므로
뇌 밖의 0 이 섞인다. 그러면 parcel 값은 그 run 의 덮임 비율만큼 축소되고, 덮임은 run 마다 다르다.
한 참가자 안에서 run 간 덮임 차이가 0.10 을 넘는 parcel 이 78개, 0.25 를 넘는 parcel 이 31개이고
최악은 0.09 ~ 0.97 이다. 이 parcel 들은 run 에 따라 값의 축척이 최대 10배 바뀐다.
전체 반복 신뢰도에는 거의 영향이 없었지만 (0 포함 평균 0.158, 뇌 voxel 만 0.159), 해당 parcel 을 개별로
해석하는 분석에서는 치명적이다.

## 3.6 despike 가 되어 있지 않다

원 논문은 run 마다 ±3 SD 로 despike 했다. step7 에는 |z| 최대 7.5, |z|>3 인 값이 0.48% (정규분포 기대
0.27%) 로 남아 있다. motion 회귀가 되었는지는 확인할 방법이 없다 (confound 파일이 없다).
DVARS 기준 이상치 TR 은 run 당 중앙값 7개, 최대 39개다.

## 3.7 파생 ROI 파일은 전부 정확히 재현된다

| 파일 | 재계산값과의 최대 차이 |
|---|---|
| ROI CSV (5명 × 2,196) | 1.2e−07 |
| `.pt` `roi_timeseries` | 0.0 |
| `.pt` `roi_mean` | 9.5e−08 |
| `fmri_raw.npy` | 2.4e−07 |

label 순서, 0 padding, 참가자 순서 모두 맞다. 이 단계들은 step7 과 atlas 가 가진 성질을 그대로 물려받으며,
§3.3 과 §3.5 의 문제도 그대로 물려받는다.

## 3.8 중복 자극의 표본 선택이 논문과 다르다

원문. "Because the presented video stimulus set happened to include identical videos (15 duplicates), we
discarded samples that were presented later in the experiment from each of those duplicates, and used
remaining 2181 unique samples."

- **15개 중복과 2,181 은 논문이 직접 밝힌 수치와 정확히 일치한다.**
- 현재 modeling 집합 (파일 번호 1–2185) 은 번호로 잘랐기 때문에, 1–11 과 2186–2196 쌍 11개 중
  **7개에서 나중에 제시된 반응** (두 번째 시청) 만 쓰고 있다 (1, 4, 5, 6, 7, 8, 11).
- 나머지 중복 4쌍 (259/866, 472/859, 846/1673, 2157/2184) 과 1349/1363 은 두 반응이 모두 집합에 있다.
  분할은 canonical 단위라 leakage 는 없지만, 논문 규칙과 다르다.

논문은 반복 노출이 반응을 바꾼다고 명시한다. 먼저 제시된 반응으로 바꾸는 것은 재전처리 없이
`fmri_raw` 와 step7 에서 가능하다.

## 3.9 filtered frame 은 신호의 절반을 버렸다

- 66,755개 전부에서 frame = max(step7, 0) 을 [12:86, 12:103, 1:82] 로 자른 것 (차이 0.0)
- run 단위 z-score 된 BOLD 에서 **평균보다 낮은 값 49.9% 를 0 으로 만들었다**
- 자르기로 뇌 voxel 이 구간당 최대 1,663개 빠진다

이 frame 으로 만든 SwiFT·NeuroSTORM 임베딩은 이 결함을 물려받는다. 그 임베딩을 쓰는 결과는
재생성 없이는 인용할 수 없다.

## 3.10 제시 순서

- 5명의 제시 순서가 2,196개 전부 같다. run 번호 붙이는 방식만 다르다
- 순서는 영상 내용과 무관하다 (인접−먼 쌍 signature 차이 0.003, 95% CI [−0.010, 0.016])
- 34-D annotation 은 인접 쌍이 아주 약간 더 비슷하다 (0.017, CI [0.001, 0.034]). 세 검정 중 하나가
  경계선에 걸린 수준이지만, §3.4 의 인접 성분과 결합하면 label 과 상관된 교란이 될 수 있다

# 4. 다시 할 것인가

## 4.1 step7 에서 고칠 수 있는 것 (원자료 불필요)

run 을 정확히 복원할 수 있으므로 다음은 지금 가진 자료로 된다.

1. **brain-mask 평균** 으로 ROI 재계산 (§3.5). 모든 run 공통 mask 를 쓰면 run 간 축척 변동이 사라진다
2. **despike** ±3 SD, run 단위 (§3.6, 논문과 일치시킴)
3. **먼저 제시된 반응** 으로 표본 선택 (§3.8)
4. **frame 재생성** (음수 보존, 자르기 범위 재설정), 필요할 때만 (§3.9)

## 4.2 원자료 (ds002425) 가 있어야 하는 것

1. **native space 분석.** prereg_v2 B2 는 "participant-native response 를 기본" 으로 정했다. 현재 자료는
   MNI 뿐이므로 B2 를 지키려면 재전처리가 필수다
2. **템플릿 확정** (§3.3). atlas 와 같은 템플릿으로 정규화하거나 native 에서 atlas 를 역변환
3. **motion confound** 회귀와 FD 기반 censoring
4. **GLMsingle.** 다만 §3.4 대로 빈틈 없는 설계에서는 단일 시행 GLM 이 불량조건이므로, 원자료가
   있어도 block 평균이 여전히 합리적인 추정량일 수 있다

## 4.3 권고

- **시간 축 (구간 분할, 4 s 보정) 은 다시 할 이유가 없다.** 논문 설계와 일치하고 경험적으로도 지지된다
- **공간 축 (템플릿, mask, native/MNI) 은 문제가 있다.** 그리고 prereg_v2 B2 를 유지한다면 어차피
  원자료부터 다시 해야 한다
- 따라서 결정은 사실상 하나다. **B2 (native space) 를 유지하는가.**
  - 유지 → ds002425 를 받아 fMRIPrep 부터 다시 한다. §4.1 의 네 가지도 그 파이프라인에 넣는다
  - MNI 로 바꾼다 → §4.1 만 적용하고, 템플릿 불확실성 (§3.3) 을 한계로 명시하고 B2 를 결과 전에 개정한다
- 어느 쪽이든 filtered frame 기반 임베딩은 폐기 또는 재생성한다

# 5. 앞 보고서 (PHASE0_3_REPORT.md) 정정

| 항목 | 앞 보고서 | 정정 |
|---|---|---|
| video 2186–2196 | 실험 말미에 1–11 을 재제시 | 8개 session 전체에 흩어져 제시됐다. 파일 번호만 끝이다 |
| 무음 기술 (§3.3) | README 의 무음 기술이 틀렸다 | 파일 4개에 소리가 있지만 원문에 "no sound was delivered in our experiment" 라고 명시돼 있다. README 는 제시 조건으로서 맞다 |
| 반복 72개 | 없다 | 원 설계가 모든 영상을 한 번씩만 제시했다 ("presented only once"). D7 은 이 cohort 에 해당하지 않는다 |
| 2,180 | 1349/1363 병합으로 설명 | 2,181 은 논문의 수치로 확인됐다. 2,180 은 primary cohort (Mind Captioning) 의 수치이고, 1349/1363 은 가능한 설명일 뿐 확인되지 않았다 |
