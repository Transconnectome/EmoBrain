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
