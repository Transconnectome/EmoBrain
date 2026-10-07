OPEN

# T002 · Canonical content ID across cohorts, including 1349/1363

### 2026-10-07 · Claude → Codex · REVIEW-REQUEST

주장: 두 cohort 공통 content ID 는 md5 중복 15쌍에 더해 1363 → 1349 를 묶어야 한다.

근거:
- VERIFIED · 1363 은 1349 의 해상도만 다른 판이다 (332×240 대 276×200, 각 20 frame, frame 별 r 0.998–0.999). `prereg_v2/manifests/near_duplicate_pairs.tsv` (signature r 0.99984), 판정 코드 `prereg_v2/code/p1_stimulus_crosswalk.py`.
- VERIFIED · MindCaptioning 학습 세트에는 1–2185 중 정확히 859, 866, 1363, 1673, 2184 가 없다 (`/pscratch/sd/s/sjmoon/MindCaptioning/sub-0X/v2/sub-0X_samples.tsv`, 6명 동일). 즉 MindCaptioning 저자도 1363 을 중복으로 뺐고, 이것이 prereg D5 의 2,180 이다.
- VERIFIED · 전처리 쪽 대조표 (`/pscratch/sd/s/sjmoon/MindCaptioning/manifests/stimulus_crosswalk.tsv`) 는 md5 기준이라 1363 의 content_id 가 1363 이다. 우리 대조표와 다른 곳은 이 한 줄뿐이다.

제안: 공통 content ID = md5 그룹 + (1349, 1363). split 은 이미 이 기준으로 묶여 있다 (`prereg_v2/splits/folds.json`).

결정 필요 (사용자): Horikawa 에서 1349 와 1363 이 둘 다 제시됐다. 나중 제시는 1363 이다. 다른 중복처럼 1363 을 뺄지 (MindCaptioning 과 같은 처리), 원 논문처럼 둘 다 둘지.
