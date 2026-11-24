# EmoBrain 인수인계 — 독립 B300 트랙

2026-11-23 23:20 KST 실측 스냅샷. 로컬 `/home/juke/git/EmoBrain`, 브랜치 `feat/b300-s1-s10-onboarding`. 정본은 `origin/design/emobrain-final-2026-11-03 @ a714d36`(11/22, 문석진 선생님)이고 이번에 기능 브랜치로 병합했다. 읽기 순서: `docs/final/01_integrated_document.md` → `docs/final/04_claude_code_workorder.md` → 이 문서 → `docs/FUTURE_RESEARCH_PLAN.md`(11/17 기준이라 1–3절보다 낡았다).

## 1. 현재 상태

- **실측 15개 fit 완료·검증.** Slurm 4212(11/19 12:48–15:33, 1 GPU, 2h44m14s)가 14개 단위를 끝냈고, 11/23에 15번째(`d4pair4`)를 재시작 실험으로 채웠다. `fit_units.py verify` 전체 VERIFIED, 예측 파일 10개 행·형태 검사 통과, D3 짝·D4 짝 집계 각 4짝 완료.
- **중단→재시작 검증 통과(11/23).** 6353을 `d4pair4` epoch 3에서 scancel → 6355 재제출: 완료돼 있던 `d4pair3`는 fit 0회·영수증 해시 불변, `d4pair4`는 epoch 1부터 271 epoch(best 241). 별도 루트에서 중단 없이 돌린 6356과 텐서 192개·history·검증 예측이 정확히 일치(허용 오차 0). 재시작은 seed부터 다시 학습하는 방식이며 epoch 이어하기가 아니다.
- **실측 시간(1 GPU, fold 1, seed 0, 후보 1개씩).** A-1 1,330초(144 epoch), 전체 인코더 966초, 안쪽 인코더 448–1,158초, D-3 392초, D-3 짝 362–488초, D-4 짝 426–620초. PyTorch 예약 최대 10.89 GiB. 잡당 고정 비용은 4212에서 476초(첫 로딩 162초 포함), 짧은 잡에서는 로딩 21초.
- **정본 병합.** 9b2b10a 이후 31개 커밋(6-4d 길이 맞춘 무작위 대조, 6-4g BOLD5000, 6-4h 구조 민감도, 6-2b Dec-바, 6-4i USAE)을 병합했다. `src/s6_*`와 `scripts/b300/`는 바뀌지 않았다. `tests/s10_imagery_prereg_tests.py` 통과.
- **B300 코드는 일부러 2b87e25에 둔다.** manifest_v3가 묶은 소스 75개 중 4개(`s10_beyond_scene`, `s10_key_test`, `s10_sensitivity`, `s3_caption_levels`)가 정본에서 바뀌었다. B300을 지금 올리면 run_v3 영수증 검증이 깨진다. 본 학습용 새 freeze를 만들 때 같이 올린다.
- 모니터 장부(`scripts/b300/independent_monitor.py status`): `d3_d4_measurement`·`partition_48h_restart` 완료, `roi_scientific_disposition`·`main_launch_preparation` 미완.

## 2. 막혀 있는 것 — 교수님 결정 3건

| 결정 | 선택지 | 근거 위치 |
| --- | --- | --- |
| GPU 자원 | B300 4대 전체가 `swift7t_100k` 예약(11/21–12/09, connectome)에 묶여 있어 예약 밖 잡은 12/09까지 대기한다. 본 학습 540 fit을 이 예약 안에서 돌릴지, 12/09 이후로 미룰지. 11/23 실험 3건(1 GPU, 합계 약 17분)은 `--reservation=swift7t_100k`로 냈다. | `scontrol show res` |
| lr4 설정 | `literal_source`(원본 JSON의 d64/wd100 그대로) 또는 `fresh_a1_adaptive`(새 A-1 선택의 d/wd를 lr4에 적용). 둘 다 540 fit. 정하지 않으면 main A-1 102개까지만 풀린다. | `production_package/SOURCE_SCOPE_AND_RECIPES.md` |
| ROI 주장 범위 | 독립 검토 2건 모두 계산용 입력은 승인, 과학적 해석은 보류. 뇌실 주변 혼합 신호(시상하부 MC04 13/35 복셀 겹침 등)와 `nuc_accum`이 실제로는 BA34라는 점 때문이다. 네트워크 수준 주장으로 좁혀 받아들일지, 추가 근거를 만들지. | `roi_resolution/SCIENTIFIC_PACKET.md` |

그 밖에 남은 일: Perlmutter `s10_stats/` 수치는 여전히 받지 못했다(11/23 22:40 캐시 기준 Teams 세 채팅에 관련 회신 없음, 재촉하지 않음).

## 3. 다음 단계

1. 본 학습 패키지 마감(`project/output/audits/b300-main-ready-20261119/production_package/`): plan_v4 시험 28개 중 1개 실패(`status_snapshot` 회귀 메시지) 수리 → 11/23 실측으로 `timing_bounds` 채우기 → `pack`으로 46시간 분할 → 독립 E2E·검토.
2. 조건부 추정: 540 fit을 관측 시간으로 합치면 1 GPU 약 139시간(4 GPU 약 35시간 + 의존 순서 대기). B-1·C-1·D-1은 11/18 파일럿 값, 대조 2종은 대리값이고 후보별 epoch 수 차이는 반영하지 못했다. 최대 300 epoch 상한으로 잡으면 A-1 한 개가 3.6시간까지 간다.
3. 위 결정 3건이 나면 새 정본으로 B300 freeze → main A-1 102개부터 sbatch.
4. `s10_stats/`를 받으면 FUTURE_RESEARCH_PLAN Phase 1–3(반입, Holm15 대조, 표·그림)을 진행한다.
5. 로컬 미커밋 `scripts/b300/independent_monitor.py`(durable progress 패치, sha 216918aa…)는 검토 뒤 커밋한다. `OPEN_HELPER_BOUNDARIES.md`의 helper RED 2건도 남아 있다.

증거: `project/output/audits/b300-main-ready-20261119/runtime_execution/restart_evidence/RESTART_RESULT.json`, 같은 폴더 `metrics_20261123T1409*.json`. 원격 산출물은 b300-01 `/scratch/emobrain/outputs/b300_main_ready_20261119/{run_v3,compare_u2_v3}`.

## 4. 유지할 결정과 제약

- Distillation A-2·C-2·D-2 추가 사용 종료. A-2/C-2는 [사전] 결과, D-2는 SI. 이후 모델은 A-1, B-1, C-1, D-1, D-3(짝 포함), D-4이며 E의 기존 결과만 보존한다.
- 학습 34개판 유지, 이후 해석·분석은 27개판. 이미 시행한 34개 사전 검정은 그대로 보고한다. 6-4f는 저장 예측·캡션·73개 이름표의 기술 분석이며 검정·판정이 없다.
- 독립 b300 완결 실행은 차지욱 교수님의 별도 지시가 있을 때만 시작한다. 결과 미수령이나 연락 지연으로 전환하지 않는다.
- b300 GPU는 Slurm(sbatch/srun)만. SSH는 `ssh -O check b300-01` 성공 뒤 BatchMode로 다중화한다. 원격 dirty 상태를 확인하고 hard reset하지 않는다.
- connectome `/storage`·`/scratch`에서 find, du, grep -r, ls -R 금지. 정확한 경로나 labfind를 쓴다.
- dgx-spark Python은 MemAvailable 6 GB 이상, Teams sync는 16 GB 이상에서만. 학생·연구원은 항상 선생님과 존댓말. 감사에는 수·커밋·막힌 이유를 쓴다.


## 6. 재개 입력(11/18 기록, 경로 유지)

| 항목 | 위치·값 | 상태 |
| --- | --- | --- |
| 계획 검토본 | https://docs.google.com/document/d/1r4Xu4JoH2uoL7VluRaym3RE-k5yYWNfyjWWr1mip5Xg/edit | 같은 Doc 부분 수정, qv 재사용, 댓글 0개였음 |
| 종료·S3 수정 증거 | `/home/juke/git/EmoBrain/project/output/audits/20261117_b300_continue/closeout_worker/` | 같은 Doc S3 부분 수정·네 유닛 정리 응답·최종 해시 |
| 이번 증거 | `/home/juke/git/EmoBrain/project/output/audits/20261117_b300_continue/worker_recovery/` | 합성 시험·원격 SHA·Doc 갱신·source-check 로그 |
| 협업 메타데이터 | `/home/juke/git/EmoBrain/.agents/teamwork/20261117-b300-continue/` | 독립 검토·진행·실패 이력 |
| 문석진 선생님 1:1 | `19:baa70085-4a80-454d-8c7f-081ffb7009c0_ca7196c0-5030-4213-9988-2f0c4000d49b@unq.gbl.spaces` | Teams 캐시 조회 대상 |
| EmoBrain 단체방 | `19:79d735a888e6484abb103d71571caa93@thread.v2` | Teams 캐시 조회 대상 |
| 이태양 선생님 1:1 | `19:505d52bb-4c36-466f-9840-f6ebec102f17_baa70085-4a80-454d-8c7f-081ffb7009c0@unq.gbl.spaces` | Teams 캐시 조회 대상 |
| HK T1w | `/storage/bigdata/Horikawa/fmriprep/horikawa_preprocess_sub0X/fmriprep/output/sub-0X/ses-anatomy/anat/sub-0X_ses-anatomy_desc-preproc_T1w.nii.gz` | connectome 재구축 입력 |
| MC T1w | `/storage/bigdata/MindCaptioning/fmriprep/sub-0X/output/sub-0X/ses-anat/anat/sub-0X_ses-anat_desc-preproc_T1w.nii.gz` | connectome 재구축 입력 |
| roiInf.mat | `/scratch/connectome/seokjin14/Horikawa_origin/EmotionVideoNeuralRepresentation/data/fmri/misc/roiInf.mat` | connectome 재구축 입력 |
| 재구축 순서 | scripts/s1_original_rois.sh → scripts/s1_subcortex_rebuild.sh → src/s2_manifest.py --stage roi | 현재 실행하지 않음 |
| 외부 ROI 기준 | Figshare 11988351, 25808179; UMPsychMethodsCore/MethodsCore@1cff4ae; ColeLab/ColeAnticevicNetPartition@e4ea9fd | 기존 인계 출처 |
| b300 | 코드 /scratch/emobrain/code; 자료 /scratch/emobrain/data; 산출물 /scratch/emobrain/outputs | 경로 유지 |

## 7. 파일 소유권과 함정

- 로컬 미추적 `.agents/`, `PROJECT.md`, `tests/test_challenger_m2_author.py`, `tests/test_s2_adversarial.py`는 기존 타 작업물이 포함돼 있어 일괄 stage하지 않는다.
- b300 미추적 12개는 `remote_final.log`에 남겼고 보존했다. 과거 근사 ROI 결과는 정본 수치로 쓰지 않는다.
- qv는 같은 Doc을 열 뿐 변경된 Markdown을 자동 덮어쓰지 않는다. 본문을 revision guard로 부분 수정한 뒤 재조회해야 한다. 이번 변경은 같은 Doc 제목까지 df9bc62로 맞췄다.
- 첫 실행 담당자 응답이 끊겨 중단한 뒤, 실행 전용 프로세스·타이머·파일 mtime·index lock을 확인하고 복구 담당자가 소유권을 인수했다. 기존 Doc 수정 영수증은 보존했다. 새 병합·시험·20:45 점검은 복구 담당자의 실제 실행 증거다.
