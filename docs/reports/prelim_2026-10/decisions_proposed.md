# 사전 분석에서 정했거나 제안한 사항 (2026-10-21 ~ 10-24, 랩서버)

공유 결정 기록(`docs/current/04_DECISION_REGISTER.md`)은 다른 작업자와 충돌하지 않도록 이 브랜치에서 수정하지 않았다. 원격 결정 기록은 D27 까지 쓰였으므로, 아래를 옮길 때는 그 뒤 번호를 붙인다. (2026-10-28: 감정 요약 집합은 D31, 참가자 중복은 D32 로 옮겨 확정했다.)

| 항목 | 내용 | 상태 | 근거 |
|---|---|---|---|
| 전처리 QC 단계 | 블록 FD > 0.9mm(반응 구간 ±2볼륨) 제외 후 run 안 z 재계산, 상수 voxel 제외, ROI 10 voxel 미만 또는 20% 미만 결측. 산출물 `v2_qc`(MC)·`v3_qc`(HK) | 사용자 승인·서버 적용 (2026-10-21). 번호 미부여 | 랩서버 PREPROCESSING_FINAL 1.2절 |
| cohort 역할 | 주(개발) = Horikawa 2020, 재현 = MindCaptioning | 사용자 결정. 원격에도 2026-10-19 T004 커밋으로 같은 내용 기록됨 | `stage1/00_status/decision_log.md` |
| 분할 | `horikawa_rungroup6_v1`: run_index 단위 6겹, 같은 내용 쌍이 든 run 묶음, 5명 공통, 안쪽 = 바깥 학습 fold 5개 | 이번 분석에 사용. **분할은 다시 만들 예정** (사용자, 2026-10-26) | `splits/README.md` |
| 피험자 처리 | 피험자별 모델, 결과는 피험자별 보존, 다른 사람 예측을 이어 붙여 r 계산하지 않음 | 사용자 확인 (2026-10-22) | `splits/README.md` |
| target 과 모델 | A34 비율 그대로(합 강제 없음) → L2 선형 sigmoid + soft BCE, A14 → ridge. 규제는 차원별 안쪽 검증 손실로 선택 | GPT 패키지 시작안과 일치. 이번 분석에 사용 | `stage1/01_task/task_contract.yaml` |
| 지표 | 주 = 차원별 영상 간 Pearson r, 보완 = train 평균 대비 오차 감소율, 보조 = 영상별 프로필 상관(평균 프로필 기준선과 함께) | 이번 분석에 사용 | 같은 계약 |
| 감정 요약 집합 | Cowen & Keltner 2017 이 구별되지 않는다고 보고한 7개(pride, triumph, contempt, disappointment, sympathy, guilt, envy)를 뺀 27개로 주 요약. 34개 모두 예측·보고 | **확정 (사용자, 2026-10-28, `docs/current/04` D31): 34개 전체가 주 결과, noise ceiling 정규화(r / √라벨 신뢰도) 함께 보고, 27개는 미리 정한 보조 결과.** 7개의 라벨 신뢰도 guilt 0.28·envy 0.32·contempt 0.33 은 27개 최저(0.41)보다 낮고, disappointment 0.49·pride 0.53·sympathy 0.67·triumph 0.69 는 27개 범위 안 | Cowen & Keltner 2017. Horikawa 2020 은 decoding·encoding 을 34개 범주와 14개 척도로 했고, 27개는 결과 서술, UMAP 색 지정, 군집 수(27개)에 썼다 |
| 드문 감정 처리 | 낮은 점수·자료 부족을 이유로 차원을 빼지 않음 | GPT 패키지 원칙과 일치 | |
| 14개 척도 결측 | 분석 영상 중 7개 결측은 채우지 않고 관측 행만 사용 | 이번 분석에 적용 | |
| 한국인 재현 설계 (참고) | 자극 일부만 사용. 영상 수는 학습 곡선으로 근거 마련(609개 ≈ 84%, 924개 ≈ 91%). 영상 선택 규칙은 라벨 기준(감정 균형, 평정 합의)으로 정하고 Horikawa 뇌 결과로 고르지 않음 | 논의 중 | `stage1/05_learning_curve/` |
