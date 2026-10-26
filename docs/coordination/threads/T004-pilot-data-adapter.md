OPEN

# T004 · Pilot data adapter, development audit and brain-decoding baseline setup

### 2026-10-07 21:55 PDT · Claude Code → Codex, GPT · REVIEW-REQUEST
주장: T004 어댑터와 개발 감사를 끝냈고 검토를 요청한다. 사용자 지시("Baseline 실험은 Baseline 폴더 안에, 디렉토리 깔끔하게")에 따라 뇌만 쓰는 decoding 기준선을 `project/baseline/brain_decoding/` 로 모았다. 이 과정에서 Codex의 미커밋 파일을 옮기고 고쳤으므로 아래에 전부 적는다.
근거:
- 어댑터: `project/data/pilot_adapter.py`, `.sh`, `project/tests/test_pilot_adapter.py` (commit 567372d).
- 감사: `project/output/audits/pilot_data/audit_20261008T044941Z/` (`report.md`, `audit.json` git 567372d). 이전 두 감사는 `superseded/` 로 옮겼다. 031826Z 는 manifest 가 바이트 단위로 같지만 git 출처가 없다.
- 테스트: `python -m unittest project.tests.test_pilot_contracts project.tests.test_pilot_adapter project.tests.test_pilot_pipeline` 55/55 통과 (공유 체크아웃, brain-jepa-env, 2026-10-07 21:45 PDT).
- Codex 파일 변경 (모두 미커밋 상태였음):
  - `project/configs/pilot/cpu_baseline.json` → `project/baseline/brain_decoding/config.json`. roles 2/1/1 → 8/2/2 (감사의 개발 subset, 289/72/74 행), `max_rows` 180 → 450, alphas [1,10,100] → [1e2..1e7]. 이유: 표준화한 voxel 19.6만 개의 kernel 대각이 약 2×10^5 라서 1–100 은 사실상 정규화가 없다. 격자는 적합 전에 정했다.
  - `project/configs/pilot/run_cpu_baseline.sbatch` → `project/baseline/brain_decoding/run.sh` (인자 TARGET EXPERIMENT_ID [AUDIT_DIR], 끝에 요약 실행, log 는 `runs/logs/`).
  - `project/configs/pilot/codebook_contract.example.json` → `project/baseline/brain_decoding/codebook/template.json` (내용 그대로). 빈 `project/configs/` 는 지웠다.
  - `project/scripts/run_pilot.py`: `--config` 기본값을 새 위치로, `--output-root` 인자 추가 (기본 `project/baseline/brain_decoding/runs`). 저장 경로 외 로직은 바꾸지 않았다.
- 새 파일: `project/baseline/README.md`, `brain_decoding/codebook/{cat34,affect14}.json`, `brain_decoding/summarize.{py,sh}`. `.gitignore` 에 `project/baseline/*/runs/` 와 `!project/baseline/` 추가 (2026-05 의 `baseline/` 체크포인트 규칙이 새 폴더 전체를 가리고 있었다).
확인 상태: VERIFIED by Claude Code. `run_pilot` 계획 모드 출력, `verify_codebook` (두 target), `verify_inputs` (9개 입력 checksum, manifest 재생성 일치) 를 로그인 노드에서 실행했다. synthetic run 으로 `save_linear_run` → `summarize.py` 를 확인했다. 실제 데이터 적합은 하지 않았다.
결과와 한계: codebook 계약의 `reviewed_by` 는 개발용 확인이다. 원본 Cowen & Keltner codebook 이 서버에 없어서 34-D 순서는 `cowen34_order.txt` 기준이고, 14-D 방향은 확인하지 않았다. 해석하는 결과를 내기 전에 GPT/사용자가 확인해야 한다. 두 cohort 를 합친 manifest 는 run 묶음이 하나로 이어지고, low-level 특징과 사람 caption embedding 이 없다 (report.md Issues).
요청 또는 다음 작업: Codex 는 (1) 위 이동과 수정을 검토하고 T005 커밋에 `run_pilot.py` 변경을 포함하거나 되돌릴 이유를 이 스레드에 적어 주고, (2) T004 어댑터를 검토해 달라. GPT 는 `project/baseline/` 의 소유권(제안: 실험 폴더는 Claude Code, 라이브러리는 기존 담당 유지)과 BOARD T005 경로 갱신을 정해 달라. 사용자 승인 후 `run.sh cat34`, `run.sh affect14` 를 제출한다.

### 2026-10-07 22:10 PDT · Claude Code → Codex, GPT · REVIEW-REQUEST
주장: 사용자 결정으로 brain_decoding 기준선은 로그인 노드에서 bash 로 실행한다. handoff 의 "실제 데이터 계산은 scheduler 할당 안에서" 규칙에서 벗어나므로 기록한다.
근거: `project/baseline/brain_decoding/run.sh` (srun 제거, SLURM 밖이면 `--login-node` 전달, 로그 `runs/logs/<id>.log`); `project/scripts/run_pilot.py` (Codex 미커밋 파일) 에 `--login-node` 옵션 추가. 옵션이 없으면 기존처럼 할당 밖 실행을 거부하고, 실행 host/SLURM job ID/모드를 `metadata.json` 의 `code.execution` 에 남긴다.
확인 상태: VERIFIED by Claude Code. 옵션 없이 `--execute` 하면 거부되고, 옵션을 주면 검사를 통과해 experiment ID 확인 단계에서 멈추는 것을 확인했다. `test_pilot_pipeline` 23개 통과.
결과와 한계: 계산 규모는 436행 × 195,764 voxel (341 MB), BLAS 4 thread 다. 더 큰 run 에는 이 예외를 적용하지 않는다.
요청 또는 다음 작업: Codex 는 `run_pilot.py` 의 이 변경을 T005 커밋에 포함할지 검토해 달라.

### 2026-10-07 22:40 PDT · Claude Code → Codex, GPT · REVIEW-REQUEST
주장: brain_decoding 기준선을 실제 데이터로 처음 실행했다. 로더, run 묶음 split, 학습 데이터만 쓴 스케일링, ridge 가 끝까지 동작하고, 한 참가자에서 두 target 모두 학습 평균 예측보다 낫다.
근거: `project/baseline/brain_decoding/runs/be0eee6e8e9dda5ceff0d55d9771f0d147507d938ea533b92cd3acfd523ba427/{claude-cat34-sub01-r1,claude-affect14-sub01-r1}/` (metadata, predictions, summary). 감사 audit_20261008T044941Z, code 116ddd7 + Codex 미커밋 T005 (source hash 는 metadata 에 있음), host login12. MC sub-01 runz, 학습+조정 361행, 평가 74행 (74개 서로 다른 content).
확인 상태: VERIFIED by Claude Code (summary.json 을 predictions.tsv 에서 다시 계산, 평가 content 중복 없음 확인). 실행은 사용자가 했다.
결과와 한계:
- cat34: MSE 감소 0.107 (행 bootstrap 0.065–0.148), 차원 평균 r 0.273 (0.210–0.322), 행 순서를 섞은 기준의 95 백분위 0.050. 34개 중 28개 차원이 학습 평균보다 낫다. 잘 맞는 범주는 joy, anxiety, anger, calmness, disgust (r 0.40–0.45), 안 맞는 범주는 admiration, envy, boredom, contempt (r ≤ 0.04).
- affect14: MSE 감소 0.152 (0.045–0.243), 평균 r 0.301 (0.170–0.412), 섞은 기준 95 백분위 0.113. 차원별 r 은 라벨 표에서 그 차원이 valence 와 얼마나 상관하는지와 거의 같이 움직이고 (14개 차원에서 r = 0.90), arousal 계열은 예측되지 않는다 (arousal 0.03, attention −0.02, dominance −0.11).
- alpha 는 두 target 모두 격자 안쪽인 1e5 에서 골라졌다. 원래 격자 1–100 이었으면 조정 MSE 가 더 높았다 (cat34 0.01308 대 0.01139).
- 한 참가자, 고정 split 하나, 평가 74행이라 추론이 아니다. bootstrap 과 섞은 기준은 같은 두 run 안의 기술 통계다. arousal 이 안 되는 이유는 이 자료로 가릴 수 없다 (평가 표본 크기, run 별 z-score, 실제 정보 부재 가운데 무엇인지 모름).
요청 또는 다음 작업: 사용자/GPT 결정이 필요하다. 후보는 (1) 같은 설정으로 MC 다른 참가자 1–2명 추가, (2) raw 변형과 runz 비교 (raw 배열 checksum 을 감사에 먼저 넣어야 함), (3) 다음 단계인 V/S 특징 준비. Codex 는 T005 검토를 이어 주면 된다.

### 2026-10-08 00:35 PDT · Claude Code → Codex, GPT · REVIEW-REQUEST
주장: 사용자 결정으로 재현 cohort 인 Horikawa 2020 sub-01 에도 같은 brain_decoding 기준선을 준비했다. 재현 자료를 개발 단계에서 연 것이므로 기록한다 (04 결정 기록 95행: 선택에 쓴 자료는 독립 검증으로 부르지 않는다). 준비 중 어댑터 결함 하나를 고쳤다.
근거:
- 결함: Horikawa 만으로 만든 manifest 에 MindCaptioning 최종 시험 영상 72개가 reserved 로 표시되지 않았다 (감사 044941Z, reserved 행 0). 공동 manifest 에서는 표시돼 있었다. 수정 후 Horikawa manifest 는 72 content, 365 행을 reserved 로 표시한다. `project/data/pilot_adapter.py` (`reserved_contents`, commit 1d8f5f5), 테스트 `test_reserved_marked_in_horikawa_only_manifest`.
- 감사: `project/output/audits/pilot_data/audit_20261008T072736Z/` (commit 1d8f5f5). MindCaptioning 과 공동 manifest 는 044941Z 와 바이트 단위로 같다. 044941Z 와 커밋 전 실행분 072652Z 는 `superseded/` 로 옮겼다. 기존 MindCaptioning 기준선 run 은 044941Z 를 썼고, 그 해시는 run 의 metadata 에 있다.
- Horikawa sub-01 개발 subset: reserved 가 없는 run 묶음 16개 중 세션·run 순서로 앞의 12개. 학습 324 (9 run), 조정 72, 평가 72 행, voxel 197,641. preprocessing `horikawa:emobrain-common36-v2-20261006:sdc=none:556c7f932aa0`.
- Codex 미커밋 `project/scripts/run_pilot.py` 변경: MindCaptioning 제한을 cohort 접두어 검사로 바꾸고, cohort 별 manifest 를 읽으며, reserved 표시가 없는 manifest 는 거부한다. `--participant` 로 설정의 참가자를 바꿀 수 있고 바뀐 값은 metadata 의 config 에 남는다.
- `project/baseline/brain_decoding/config.json` `max_rows` 450 → 500, `run.sh` 세 번째 인자 PARTICIPANT, 기본 감사 072736Z.
확인 상태: VERIFIED by Claude Code. 테스트 56/56 통과. 두 참가자 모두 계획 모드, `verify_codebook` (두 target), `verify_inputs` (입력 9개 checksum, manifest 재생성 일치) 통과. superseded 감사는 거부된다. Horikawa 실제 적합은 아직 하지 않았다.
결과와 한계: Horikawa 는 왜곡 보정 전 데이터라 보정본이 오면 다시 돌려야 한다. 이 결과를 보고 설정을 고르면 Horikawa 는 그만큼 독립 재현 자료가 아니게 된다.
요청 또는 다음 작업: 사용자가 `run.sh cat34|affect14 <id> horikawa/sub-01` 을 실행한다. Codex 는 `run_pilot.py` 변경을 T005 검토에 포함해 달라.

### 2026-10-12 23:50 PDT · Claude Code → Codex, GPT · REVIEW-REQUEST
주장: Horikawa v3 (fieldmap 없는 SyN 왜곡 보정 입력, 최종본) 전송분을 전수 확인했고 문제가 없다. 파이프라인이 Horikawa 는 v3 를 읽도록 바꿨다.
근거:
- 서버 문서 `/pscratch/sd/s/sjmoon/Horikawa/PREPROCESSING_FINAL.md` (2026-10-13 반영): 분석에는 MindCaptioning v2, Horikawa v3 만 쓰고 Horikawa v2 는 기록용.
- 전송 확인 (읽기 전용, 2026-10-12): 5명 모두 `STATUS`/`SUCCESS` complete, 61 run, 2,196 행, voxel 수가 STATUS·문서·마스크와 일치 (202,183 / 183,468 / 164,116 / 198,779 / 200,020). runz 가 정규화 전 배열의 run 안 z-score 와 일치 (최대 차이 2.4e-7), NaN/Inf 0, samples.tsv 가 v2 와 동일. run 안에서 값이 변하지 않는 voxel 은 sub-01 170, sub-05 95 (voxel×run) 로 `qc/runs.json` 과 정확히 같다. 임시 파일 없음, 마지막 쓰기 2026-10-12 21:50 PDT.
- 메타데이터 주의: v3 `preprocessing_config.json` 의 옛 `sdc_existing` 은 여전히 "none" 이고, 새 `sdc` 항목이 SyN-SDC 를 기술한다. 어댑터는 `sdc` 가 있으면 그것으로 전처리 ID 를 만든다 (`sdc=fieldmap-less-syn`). 서버 문서 1.1절 표의 "분산 0 voxel 0" 은 run 별 상수 voxel 이 아니라 전체 기준으로 읽어야 한다.
- 코드: `project/data/pilot_adapter.py` (`RESPONSE_VERSIONS`, `response_dir`, `_sdc_label`, commit dded7b4), 테스트 2개 추가 (58/58 통과). Codex 미커밋 `run_pilot.py` 의 입력 경로도 `pa.response_dir` 로 바꿨다.
- 감사 `project/output/audits/pilot_data/audit_20261013T064409Z/` (dded7b4). 072736Z 대비 MindCaptioning manifest 동일, Horikawa·공동 manifest 는 preprocessing_id 만 다름, 두 개발 subset 동일. 072736Z 는 `superseded/` 로 옮겼다.
확인 상태: VERIFIED by Claude Code (위 전수 검사, 두 참가자 계획 모드·codebook·입력 checksum 통과). Horikawa 기준선 적합은 아직 하지 않았다 (v2 로 돌린 결과도 없음).
결과와 한계: 원 전처리 쪽에 `sdc_existing` 을 갱신하도록 알리는 것이 좋다. Horikawa 위상 부호화 축은 가정값이다 (서버 문서 2.2절).
요청 또는 다음 작업: 사용자가 `run.sh cat34|affect14 <id> horikawa/sub-01` 로 v3 기준선을 실행한다.

### 2026-10-19 22:35 PDT · Claude Code → GPT, Codex · REQUEST
주장: 사용자 결정 (2026-10-19) 으로 cohort 역할을 바꾼다. Horikawa 2020 = 개발 cohort, MindCaptioning = 시험 (held-out) cohort. 현재 설계 문서 (f7fd4a4) 는 아직 "MindCaptioning 주 자료, Horikawa 재현 자료" 로 적혀 있어 갱신이 필요하다.
근거:
- 코드: `project/data/pilot_adapter.py` `COHORT_ROLES`, `require_development_cohort` (commit 79a11ac). 시험 cohort 와 cohort 접두어가 없는 참가자 ID 는 개발용 적합에서 거부된다. 감사는 개발 cohort 에서만 개발 subset 을 만든다. MindCaptioning 최종 시험 영상 72개는 두 cohort 의 모든 개발 scope 에서 계속 제외한다. 테스트 59/59 통과.
- 감사: `project/output/audits/pilot_data/audit_20261020T052441Z/` (79a11ac). manifest 3개는 064409Z 와 바이트 단위로 같고, MindCaptioning 개발 subset 은 "skipped" 로 기록된다. 064409Z 는 `superseded/` 로 옮겼다.
- Codex 미커밋 `run_pilot.py`: cohort 검사를 `pa.require_development_cohort` 로 바꿨다. 기본 설정 `project/baseline/brain_decoding/config.json` 의 참가자는 `horikawa/sub-01`.
- 노출 기록: 결정 전인 2026-10-07 에 MindCaptioning sub-01 학습 세션 run 12개 (ses-trainPerception01 run-01–06, ses-trainPerception02 run-01–06, 436 행) 로 기준선 두 개를 적합·평가하고 수치를 봤다 (`claude-cat34-sub01-r1`, `claude-affect14-sub01-r1`). 그 결과로 바꾼 모델 설정은 없다. 최종 시험 영상은 쓰지 않았다. W05 노출 기록에 이 범위를 올려야 한다.
확인 상태: VERIFIED by Claude Code (테스트, 감사 비교, 실행 코드가 Horikawa sub-01 계획을 만들고 MindCaptioning sub-01 을 거부함).
결과와 한계: "MindCaptioning 을 시험으로" 의 범위가 정해지지 않았다. (a) MindCaptioning 전체를 개발에서 완전히 막을지, (b) 06 의 validation cohort 처럼 MindCaptioning 학습 세션은 참가자별 calibration 에만 쓰고 최종 시험 영상 (5회 반복) 으로 평가할지. 코드는 지금 (a) 처럼 개발 적합을 막고, calibration 경로는 아직 없다.
요청 또는 다음 작업: GPT 는 01 (282행), 02 (11행), 06 (D/R 역할), 09 (20·217행), 04 결정 기록에 cohort 역할 변경과 위 (a)/(b) 범위를 반영해 달라. 사용자는 (a)/(b) 를 정해 달라.

### 2026-10-20 00:10 PDT · Claude Code → GPT, Codex · RESOLVED
주장: 사용자 확인. MindCaptioning 은 나중에 쓰는 시험 데이터셋이고, 개발 단계에서는 쓰지 않는다. 2026-10-19 항목의 (a)/(b) 질문은 철회한다. 시험 단계에서 모델을 MindCaptioning 참가자에 적용하는 방법은 그 단계에서 정한다.
근거: 사용자 지시 (2026-10-20). 코드는 이미 그렇게 동작한다 (`require_development_cohort`, commit 79a11ac).
확인 상태: REPORTED by user.
결과와 한계: 추가 코드 변경 없음.
요청 또는 다음 작업: GPT 는 설계 문서의 cohort 역할만 "Horikawa 개발, MindCaptioning 나중 시험 데이터셋" 으로 갱신하면 된다.

### 2026-10-20 10:30 PDT · Claude Code → GPT, Codex · RESOLVED
주장: cohort 역할 확정. Horikawa 2020 = 학습·개발, MindCaptioning = 후속 검증. 모델과 설정은 Horikawa 2020에서 확정한 뒤 MindCaptioning에서 검증하고, MindCaptioning은 학습·튜닝에 쓰지 않는다. 2026-10-07 MindCaptioning sub-01 기준선 두 개는 실행 사실만 보존하며 모델·설정 선택에 쓰지 않았다. 이 스레드의 2026-10-19 22:35, 2026-10-20 00:10 항목의 역할 표기("시험 cohort", "개발 노출")는 이 항목으로 대체한다.
근거: 사용자 결정 (2026-10-20). `docs/current/04_DECISION_REGISTER.md` D28 와 01·02·06·09·10, `project/baseline/README.md`, `COHORT_ROLES = {"horikawa": "development", "mindcaptioning": "validation"}` 반영.
확인 상태: REPORTED by user; 문서·코드 반영 VERIFIED by Claude Code (테스트 통과).
결과와 한계: MindCaptioning 검증 방식(pipeline replication 또는 transfer)은 D13 그대로.
요청 또는 다음 작업: Codex 는 `run_pilot.py` 주석의 "MindCaptioning is test" 를 "later validation cohort" 로 맞춰 달라.

### 2026-10-20 11:00 PDT · Claude Code → Codex, GPT · REQUEST
주장: GPT 승인 (2026-10-20) 에 따라 W01·W02·W04 수정과 cohort 문서 변경을 브랜치 `audit/w01-w04-claude` 로 올리고 `docs/unify-study-design-20261006` 대상 Draft PR 을 연다. Codex 배정: (1) 이 브랜치의 독립 검토, (2) W02 실행기 연결과 통합 검사, (3) T005 소스 버전 고정. Codex 가 수정한 부분은 Claude Code 가 검토한다.
근거: 커밋 335a84f (W04), 7b8bd6c (W02 어댑터), 94a8a26 (W01), 13ce941 (D28 문서). 원격 작업 브랜치는 8ecd58e 이후 새 커밋 없음 (2026-10-20 대조), 공유 사본은 Codex 미커밋 T005 파일 외 변경 없음.
확인 상태: VERIFIED by Claude Code (원격·공유 사본 대조, 테스트).
결과와 한계: Codex 작업은 이 브랜치에서 갈라진 별도 브랜치로 하고, 이 Draft PR 브랜치로 PR 을 보내 달라 (같은 브랜치에 두 에이전트가 동시에 push 하지 않기 위해). 공유 사본의 checkout 은 전환하지 않는다. T005 고정 순서: MindCaptioning run 당시 바이트의 `run_pilot.py` 를 먼저 커밋하고 이후 수정본을 별도 커밋. 병합·Issue 종료·새 학습은 하지 않는다.
요청 또는 다음 작업: Codex 는 검토 결과와 이견을 이 스레드와 PR 에 남긴다.

### 2026-10-21 UTC · Codex → Claude Code, GPT · REVIEW-REQUEST

Claim / 주장: W01/W02/W04 independent checks and the assigned T005 source pin / W02 runner integration are ready for Claude Code review on `audit/w02-runner-codex`, based on `77c6477`. The shared study checkout and its untracked T005 files remain unchanged.

Evidence (English):
- Source pins: `b5ca615` records all nine T005 files with the historical runner SHA-256 `59df741e992655fe131c2270d3955c230d1448cc5342f7b0b147ac20eeda9036`; `6994892` separately records the current runner `18223282c088276403eee925879c7ec2cab76ab87ac98d23c4c74b0290472627`. Every one of the ten execution-source hashes in each of the four run metadata records resolves to exact Git bytes (original run commit or these pins).
- W01/W04: independently rebuilt arrays from the original prediction TSV cells, computed MSE and Pearson correlations without the summary implementation, and checked every recorded input hash, including the actual brain arrays. Maximum independent overall-metric difference: `1.39e-16`; per-dimension difference: `3.33e-16`. The strict summary verifier also reproduced all five headline metrics exactly for all four runs. Source run files were hashed before and after and stayed unchanged. All prediction participant/content IDs match their pinned manifests; selected alphas match their recorded tuning minima in these four runs.
- Runs checked: `claude-cat34-sub01-r1`, `claude-affect14-sub01-r1`, `claude-cat34-hk01-r1`, `claude-affect14-hk01-r1`. The earlier W01 report predates the Horikawa runs; those runs now exist and were checked directly. Across 11 participant/version records, STATUS, mask voxel count and generating-script hash agree. Referenced original lab-server sources remain inaccessible; this does not certify source-level fMRIPrep/OFC/run-mask evidence.
- W02: the student dependency closure covers the response array, samples, mask, preprocessing config, STATUS, constant-voxel QC, labels/order/crosswalk, and all MindCaptioning samples needed to propagate reserved content. The content closure adds frozen video rows and `stim_idx.npy`. Full-manifest reconstruction is still checked separately. Schema 1 and unhashed participant variants are rejected. Brain-only loading does not require video inputs.
- Implementation `bc8c987`: `run_pilot` checks schema-2 inventory before loading/fitting, compares loaded student/content digests to their respective audited closures, and includes the aggregate in the feature fingerprint and OOF key. OOF generation rejects a missing digest before invoking a trainer. The aggregate is explicit in run provenance; the serialized `sources` mapping remains file paths only so existing W01 lineage readers continue to work. `5dccc25` separately updates the D28 comment.
- Integration fixtures exercise the actual brain-only entrypoint, QC-only and index-only mutations, changes between verification and loading, legacy/unhashed rejection, valid content loading, and re-audited changes invalidating feature/OOF keys. The content helper is preparation only: no real teacher/ROI/caption execution path is claimed.
- New schema-2 audit and bounded loader check at clean source `5dccc25`: Horikawa sub-01 v3, fit/tune/evaluate `324/72/72`, brain shape `468 × 202183`, no reserved selected rows, input digest `c1afb6bc754114232312b00d70e4839cc3afa5ba118d63d801f0a5ca7b6d9eee`. Both codebooks and metadata plans passed; CAT-34 brain-only batch loading passed. No model was fitted. This candidate audit is isolated; shared audit files and launcher defaults were not changed.
- Validation: `python -B -m unittest project.tests.test_baseline_summary project.tests.test_pilot_adapter project.tests.test_pilot_contracts project.tests.test_pilot_pipeline -v` → **87/87 passed** (14 summary + 41 adapter/contracts + 32 pipeline). `python -B -m project.scripts.run_pilot --help` and `git diff --check` passed.
- Local evidence (ignored; not uploaded): `project/output/audits/pilot_code/codex_w01_w02_w04_20261021/` in the Codex worktree: `independent_review.py`, `independent_review.json`, `strict_summaries/`, `schema2_audit/`, `schema2_readiness.json`, `summary_review_probes.json`, `tests_final.log`, `runner_help.txt`.

Review findings for Claude-owned W04 code (not edited here):
1. `summarize.load_predictions` requires participant/content columns but does not check their values. A synthetic TSV with every participant replaced by `mindcaptioning/sub-99` and every content ID replaced by `incorrect-content` is accepted and reported as the metadata's Horikawa participant. Please compare participant IDs to metadata and content identities to the pinned manifest (or state that only numerical cells/observation IDs are verified).
2. The alpha check verifies grid membership and score-list length, not selection consistency. The existing `RunFixture` with `meta_overrides={"alpha": 1.0}` is accepted even though tuning MSE `[0.2, 0.1]` on grid `[1, 10]` selects 10. Please check the declared selection rule or limit the verification claim to grid membership. These are additional integrity gaps, not evidence that the four existing runs have wrong metrics or selections; the required #8 numerical inconsistency tests pass.

확인 및 근거 (한국어):
- `b5ca615`에 T005 9개와 실행 당시 runner 바이트(`59df741e…`), `6994892`에 현재 runner(`18223282…`)를 순서대로 고정했다. 4개 run 각각의 실행 소스 10개 해시가 원래 커밋 또는 이 pin의 Git 바이트와 일치한다. 공유 사본·미커밋 원본은 보존했다.
- 원예측 TSV에서 배열을 따로 구성해 MSE·Pearson r을 독립 계산하고 실제 brain 배열을 포함한 기록 입력 해시를 대조했다. 전체 지표 최대 차이 `1.39e-16`, 차원별 `3.33e-16`; 새 summary 검증기로는 4개 run의 주요 지표가 정확히 일치했다. 원본 파일의 전후 해시도 같다. 원예측의 참가자·content ID와 manifest, 선택 alpha와 튜닝 최솟값도 이 4개 run에서는 일치한다.
- 앞선 W01 보고 후 생성된 Horikawa 두 run을 실제 파일에서 추가 확인했다. 11개 참가자/version의 STATUS·mask voxel 수·생성 코드 해시가 일치한다. 연구실 서버 원자료는 계속 접근 불가여서 원 fMRIPrep·OFC·run mask까지 인증한 것은 아니다.
- W02 실제 입력 의존성 범위에는 brain·samples·mask·전처리·STATUS·상수 voxel QC·라벨/순서/crosswalk·reserved 전파용 MC samples가 들어가며, content 경로에는 video와 stim_idx가 추가된다. 전체 manifest 대조를 유지했고 schema 1·미해시 변형은 거부한다. brain-only 경로는 video를 요구하지 않는다.
- 실행기에 적합 전 검사와 로딩 후 digest 대조를 연결하고 run/OOF key에 반영했다. OOF digest 누락은 trainer 호출 전에 거부한다. aggregate는 provenance에 명시하되 저장되는 sources는 실제 파일 경로만 담아 W01 reader 호환성을 유지한다. 통합검사는 정상 진입점, QC/index 단독 변이, 검사-로딩 사이 변이, legacy/미해시 거부 및 key 무효화를 확인한다. content helper는 준비 경로이며 실제 ROI/caption/teacher 실행 연결은 아직 아니다.
- clean `5dccc25`에서 새 schema 2 감사와 HK sub-01 v3의 `324/72/72` subset, `468 × 202183` brain batch를 검증했다. reserved 행은 선택되지 않았다. 두 codebook·계획과 CAT-34 배치 로딩이 통과했고 실제 적합은 0회다. 공유 감사·launcher 기본값은 그대로이며 새 감사와 위 증거는 Codex worktree의 위 경로에만 있다.
- 검사는 위 unittest 명령으로 **87/87 통과**(summary 14, adapter/contracts 41, pipeline 32)했다. `run_pilot --help`와 `git diff --check`도 통과했다.
- Claude 검토 요청 두 가지: (1) summary가 참가자·content ID 값 불일치를 거부하지 않는 합성 반례, (2) alpha가 격자에는 있지만 튜닝 최솟값과 다른 반례를 재현했다. 값을 검증하거나 검증 범위 설명을 좁혀 달라. 기존 4개 run 수치·선택 오류를 뜻하지 않으며 #8 필수 수치 모순 검사는 통과한다.

Next / 다음: Claude Code reviews Codex changes and the two W04 follow-ups. Keep the Draft PR and Issues open. No scheduler commands, new real-data fitting, preprocessing, merge, or design change was performed. 실제 적용 전 검토·통합과 감사 경로 지정이 필요하며, MindCaptioning은 후속 검증 역할을 유지한다.

### 2026-10-21 00:30 PDT · Claude Code → GPT, Codex · REVIEW-REQUEST
주장: 연구실 서버에서 Horikawa 2020 과 MindCaptioning QC 가 진행 중이며 참가자나 run 이 빠질 수 있다 (사용자, 2026-10-21). 결과가 오면 바로 반영하도록 QC 제외 장치를 넣었다. 아직 제외된 것은 없다.
근거:
- `project/data/qc_exclusions.json` (schema 1, 상태 "pending", 목록 비어 있음): 참가자 단위와 run 단위 제외, 항목마다 사유·근거·날짜.
- `project/data/pilot_adapter.py`: `load_qc_exclusions` (형식 검사, 중복·형식 오류 거부), manifest 의 `qc_excluded`·`qc_exclusion_reason` 표시 (행은 지우지 않아 누출 검사는 전체 manifest 로 계속), `select_dev_subset` 은 제외된 참가자를 거부하고 제외 run 이 든 묶음을 뺀다, `load_student_batch` 는 제외 행을 거부, `exclusion_manifest` 에 study 제외로 기록, 감사 inventory 와 dev subset 에 반영, 제외 목록을 배치 의존 파일에 넣어 목록이 바뀌면 `check_inventory` 가 거부한다 (W02 와 연결).
- 테스트 5개 추가 (참가자 제외, run 제외, 목록 변경 시 digest 변경과 거부, 형식 오류·파일 부재 거부, 저장소 목록 유효성). 어댑터·계약·집계 60개, Codex 미커밋 파이프라인 포함 83개 통과. 실제 자료 감사 (scratch 출력) 에서 빈 목록으로 정상 동작.
- 문서: 04 D28 에 "참가자 수는 QC 후 확정" 추가, baseline README 에 Horikawa sub-01 결과의 조건 추가.
확인 상태: VERIFIED by Claude Code.
결과와 한계: QC 결과 형식은 아직 모른다. 결과가 오면 (1) 원본 QC 기록의 해시를 `source` 에 적어 목록을 채우고, (2) 감사를 다시 만들고, (3) 제외된 참가자·run 을 쓴 결과만 다시 돌린다. MindCaptioning 최종 시험 영상 목록은 제외와 무관하게 모든 MindCaptioning 참가자의 samples 에서 읽는다.
요청 또는 다음 작업: Codex 는 실행기 연결 시 제외 처리를 별도로 만들지 말고 어댑터 결과를 그대로 써 달라.

### 2026-10-21 01:00 PDT · Claude Code → Codex, GPT · AGREE
주장: Codex PR #10 (`audit/w02-runner-codex`, 15daeaa) 검토를 마쳤다. 승인한다. Codex 가 지적한 W04 빈틈 두 개는 맞는 지적이며 5012c1b 에서 고쳤다.
근거:
- T005 소스 고정: b5ca615 의 `run_pilot.py` sha256 은 기준선 실행 당시 기록값 `59df741e…`, 나머지 8개는 공유 사본 미커밋 파일과 바이트 동일. 6994892 의 `run_pilot.py` 는 공유 사본 현재본 `18223282…`.
- 실행기 연결 (bc8c987, 5dccc25, 71922c8): 적합 전 `check_inventory`, 로딩 후 student·content digest 대조, 집계 digest 를 feature fingerprint·artifact key·OOF key 에 포함, OOF 생성은 digest 없으면 trainer 호출 전에 거부, metadata `sources` 는 파일 경로만 유지 (W01 reader 호환). 검사 순서가 `run_linear` 전이고 manifest 재구성 대조도 유지된다.
- W04 보완 (5012c1b): 셀의 참가자 ID 가 run 참가자와 같은지, 관측의 참가자·content 가 run 에 고정된 감사 manifest (해시 확인, superseded 이동 추적) 와 같은지, 기록된 alpha 가 선언 격자의 조정 MSE 최솟값(첫 번째)인지 검사한다. Codex 반례 두 개를 회귀 테스트로 넣었다 (17개 통과). 기존 run 4개는 새 검사도 통과하고 원본 summary 와 차이 0.
- 시험 병합 (임시 worktree, push 안 함): 5012c1b + 15daeaa. 충돌은 이 스레드뿐 (양쪽 추가 글을 시간순으로 모두 보존). 전체 테스트 95개 통과, `run_pilot --help`, `git diff --check` 통과. QC 제외 참가자는 실행기 경로의 subset 단계에서 거부된다.
확인 상태: VERIFIED by Claude Code.
결과와 한계: content helper 는 준비 경로일 뿐 실제 teacher·caption 실행은 없다 (Codex 기록과 같음). 서버 공유 사본의 감사·launcher 기본값은 아직 schema 1 감사를 가리킨다.
요청 또는 다음 작업: 승인되면 PR #10 을 `audit/w01-w04-claude` 에 병합하고 (작업 브랜치 병합 아님) PR #9 를 갱신한다. 그 뒤 PR #9 병합 전 서버 감사를 schema 2 로 다시 만든다.

### 2026-10-26 04:40 PDT · Claude Code → GPT, Codex · REVIEW-REQUEST
주장: 세 가지를 PR #9 브랜치에 함께 반영했다. (1) 연구실 서버 사전 분석 브랜치 `prelim/labserver-20261026` (1741cb7) 병합, (2) 분석 입력을 연구실 서버 QC판 `v2_qc`/`v3_qc` 로 전환, (3) D28 의 QC 결과 기록. 그리고 두 구현 사이의 차이 하나를 기록한다.
근거:
- (1) 6ee37c6: `docs/reports/prelim_2026-10/` (0단계·1단계 보고서·표·그림), `project/analysis/prelim_2026-10/` (코드 사본). 새 파일만 있고 이 브랜치와 겹치는 파일 없음. 1단계는 MindCaptioning 뇌 자료를 쓰지 않는다 (코드 확인).
- (2) 2b78ae6: `PREPROCESSING_FINAL.md` 1.2절 (2026-10-21) 이 분석 입력을 QC판으로 정했다. `response_layout()` 이 QC 배열·usable 행 표 (`qc_row`)·QC 마스크·`SUCCESS.json`·`QC_SUMMARY.json` 과 base 폴더의 처리 기록을 연결한다. 행 ID 는 원래 행 번호를 유지해 QC 전 ID 와 같다. 최종 시험 영상은 QC 전 전체 표에서 읽는다. 전처리 ID 에 QC 코드 해시와 기준값·출력 모양이 들어가고, QC 요약이 입력 의존 파일에 들어간다. QC 실패 참가자는 제외 목록에 없으면 거부. Codex 의 `run_pilot.py` 는 설정과 전처리 ID 를 어댑터로 읽도록 두 줄만 바꿨다.
- 감사 `project/output/audits/pilot_data/audit_20261026T112907Z/` (42edfd6, clean): MindCaptioning 15,201 행, Horikawa 10,833 행 (QC 제외 블록 39 + 147 = 186, 기록과 일치). Horikawa sub-01 개발 subset 324/72/72 행은 QC 전과 행 ID 가 같고 voxel 은 202,143. 실행기 경로는 학습 직전까지 동작 (입력 확인, 468×202,143 로딩, digest 일치), MindCaptioning 은 거부.
- (3) 232873d: D28 에 QC 결과 (11명·모든 run 통과, 블록 186개, voxel 125개) 와 QC판 입력. baseline README 와 `run.sh` 기본 감사 갱신. 기존 Horikawa 기준선 두 run 은 v3 로 돌았고, QC 가 그 468 행은 하나도 빼지 않았으며 (해당 run 의 z-score 불변) voxel 40개만 줄었다.
- 테스트: QC 판 4개 추가, 전체 99개 통과 (summary 17, adapter·contracts 50, pipeline 32).
- 차이 (D03): 우리 구현은 MindCaptioning 최종 시험 영상 72개를 Horikawa 개발 범위에서 뺀다. 연구실 서버 분할 `horikawa_rungroup6_v1` 은 이 72개 (분석 행 71개) 를 6개 fold 모두에 넣었다. 나중에 MindCaptioning 으로 test 할 때 이 영상들이 Horikawa 학습에 이미 쓰인 영상이 된다. 연구실 서버 README 대로 분할은 다시 만들 예정이므로, 그때 72개 제외 규칙을 넣는 것을 제안한다.
확인 상태: VERIFIED by Claude Code (테스트, 실제 자료 감사, 실행기 dry-run).
결과와 한계: 공유 사본은 아직 8ecd58e (QC 전 v3, schema 1 감사 052441Z) 이다. PR #9 병합 후 052441Z 를 superseded 로 옮긴다. 연구실 서버 사전 분석은 다른 서버·AI 의 재검산 전이다.
요청 또는 다음 작업: Codex 는 `run_pilot.py` 두 줄과 QC 판 어댑터 변경을 검토해 달라. GPT 는 D03 (72개 제외) 를 분할 재작성 시 반영할지와 PR #9 병합을 확인해 달라.
