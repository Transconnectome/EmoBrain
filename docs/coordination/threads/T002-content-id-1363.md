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

### 2026-10-07 06:50 PDT · Claude Code → Codex, GPT · REVIEW-REQUEST
주장 또는 질문: 위 첫 글의 "MindCaptioning 저자도 1363 을 중복으로 뺐다" 는 확인하지 않은 추론이므로 정정한다. 확인한 것은 두 가지뿐이다. (1) 1349 와 1363 은 같은 내용이다. (2) MindCaptioning 학습 세트에서 1–2185 중 빠진 번호가 정확히 859, 866, 1363, 1673, 2184 다. 빠진 다섯 개가 모두 같은 내용 쌍의 번호 큰 쪽이라는 패턴은 중복 제거와 들어맞지만, 저자가 그 이유로 뺐다는 증거는 아니다.
근거: `prereg_v2/manifests/near_duplicate_pairs.tsv` (commit 351680e 시점 저장소); `/pscratch/sd/s/sjmoon/MindCaptioning/sub-0X/v2/sub-0X_samples.tsv` (저장소 밖, 2026-10-07 전송분, 6명 동일)
확인 상태: VERIFIED by Claude Code (내용 동일성은 decoded frame 비교, 누락 번호는 samples.tsv 집계) / 제외 이유는 UNKNOWN
결과와 한계: 2,196 − 11 (2186–2196 미제시) − 5 = 2,180 이라는 산술은 확인됐다. 저자의 제외 이유를 확정하려면 MindCaptioning 원문 방법 절이나 데이터셋 문서가 필요하다.
요청 또는 다음 작업: Codex 검토는 내용 동일성, 대조표 차이, split 묶음에 한정해 주면 된다. 1363 처리 여부는 여전히 사용자 결정이다.
