# EmoBrain 인수인계 (b300 연계 트랙, 2026-11-17 20시 KST 기준)

다음 세션 작업자가 이 문서만 읽고 바로 이어갈 수 있도록 쓴 인수인계 문서다. 설계 기준은 항상 `docs/final/01_integrated_document.md`(통합문서)이고, 실행 기록은 `docs/final/04_claude_code_workorder.md`다. 이 문서와 두 문서가 다르면 두 문서를 따른다.

## 1. 현재 목표

- 문석진 선생님이 NERSC Perlmutter에서 정본 파이프라인(`origin/design/emobrain-final-2026-11-03`)을 직접 실행하고 있다. 이 트랙(PR #14, `feat/b300-s1-s10-onboarding`)의 역할은 세 가지다.
  1. 정본 브랜치의 새 커밋을 PR #14와 `b300-01:/scratch/emobrain/code`에 병합하되 `src/`는 정본과 0바이트 차이로 유지하고, 새 합성 시험을 `b300-01`에서 돌려 확인한다.
  2. Perlmutter의 완료 결과표(`output/final_2026-11/s10_stats/`)를 받아 결과 요약과 그림에 통합하고 산출물 감사를 한다.
  3. Perlmutter에서 남은 GPU 작업이 있다고 확인되면 정본 `roi_voxels` 11개와 함께 `b300`에서 Slurm으로 분담 실행한다.
- 차지욱 교수님 질문(11/16)에 대한 답: Perlmutter 모델 체크포인트는 필요 없다. `roi_voxels` 11개도 `connectome` 원자료로 b300에서 독립 재구축할 수 있다(5절). 독립 실행으로 바꿀지는 아직 지시가 없다.

## 2. 지금 상태 (20:05 KST 확인)

- Git
  - PR #14 브랜치는 정본 `d1cbf59`까지 병합된 상태다(병합 커밋 `729a6f7`, 푸시 완료, `src/` 차이 0바이트). `b300-01:/scratch/emobrain/code`도 `729a6f7`로 맞췄다. `configs/paths.yaml`, `configs/env.sh`는 git 밖이며 `scripts/b300/configs/`에서 복사한다.
  - 로컬 미추적 파일(`.agents/`, `PROJECT.md`, `tests/test_challenger_m2_author.py`, `tests/test_s2_adversarial.py`)은 이 트랙 작업이 아니라 커밋하지 않는다.
- Perlmutter 진행(정본 커밋 기록 기준, 11/17 하루 동안 26개 커밋)
  - 6-2 구역 학습 60개 완료. 구역 3 pride(`sub-05`에서만 평정 상수)는 5명 모두에서 빼기로 확정(`464f516`, 석진 님 선택지 (나)).
  - 11/17 결정: distillation 조건(A-2, C-2, D-2)은 더 쓰지 않음. A-2, C-2는 [사전] 2-3 (다), (바)로 그대로 보고, D-2는 SI(`a1eb7fe`). 이후 분석과 MC 전이에 쓰는 모델은 A-1, B-1, C-1, D-1, D-3, D-4(`49929d1`).
  - 11/17 결정: 해석과 추가 분석은 Cowen과 Keltner의 7개를 뺀 27개 정서판을 쓴다. [사전] 34개 검정은 돌린 그대로 보고(`d1cbf59`).
  - MC 전이를 B-1, D-1, D-3, D-4로 확장(`fb71b1b`), MC 회상(imagery) 분석 완료(`e7d3808`, `302d99e`: 질문 1, 2 확인, 질문 2a, 3 미확인, 질문 3 규칙 부호 오류 기록), 6-4e 네트워크 교란과 표현 비교(`86d29a2`, `7ccfd17`), MC 개인 모델 비교(`9ddee0e`, 사전 예측 미충족), MC ridge 기준선(`e62e655`).
  - 결과 수치는 공개 레포에 넣지 않고 Perlmutter 산출물 폴더의 README에 있다고 기록되어 있다. 이 트랙에는 아직 수치가 없다.
  - [사전] 15개 Holm(`src/s10_holm15.py`)의 실행 완료 기록은 아직 04에서 확인하지 못했다.
- 협업 채널(Teams)
  - 11/16 21:37 KST에 문석진 선생님 1:1(message 1794832654618)과 EmoBrain 단체방(1794832657750)으로 `s10_stats/` 공유와 남은 GPU 작업 확인을 요청했다. 이 요청에 대한 답은 아직 없다.
  - 11/17 오후 대화는 다른 주제였다. 문석진 선생님은 오늘 밤 KHBM 포스터 마감, 이태양 선생님은 리뷰 답변 작업으로 바쁘다고 했다. 재촉하지 않는다.
- b300
  - `b300-01`의 정본 `roi_voxels`: 0/11(`scripts/b300/verify_s2_roi_voxels.py --json`). 이것이 통과하기 전에는 `scripts/b300/*.sbatch`가 GPU 작업을 막는다.
  - 20:05 KST에 4개 노드 모두 GPU 8/8 할당(`b300-live`). 다른 사용자 작업을 방해하지 않는다.
- 모니터링
  - 장부: `~/.local/state/long-job-monitor/emobrain-core-v2.json`(Step 0 완료, Step 1 0/2 대기, Step 2 분모 미확정, Step 3 대기).
  - systemd user timer `long-job-mon-emobrain-core-v2.timer`가 active다(15분 주기, Telegram 알림). 세션 안 schedule 타이머는 지금 걸려 있지 않다.

## 3. 유지할 결정과 제약

- `src/`는 정본과 같게 둔다. 병합 뒤 `git diff origin/design/emobrain-final-2026-11-03 -- src/ | wc -c`가 0인지 확인한다. 설계 변경은 석진 님과 Claude가 01에서 한다(04 0-2).
- b300 GPU는 Slurm(`sbatch`, `srun`)으로만 쓴다. ssh나 tmux로 GPU 작업을 띄우지 않는다. SSH는 `ssh -O check b300-01`로 기존 ControlMaster가 살아 있을 때 `ssh -o BatchMode=yes b300-01 ...`로 다중화한다.
- `connectome`에서는 `/storage`, `/scratch`에 `find`, `du`, `grep -r`, `ls -R`를 쓰지 않는다. 정확한 경로나 `labfind`를 쓴다.
- 로컬 dgx-spark: `chavis-teams sync`는 `MemAvailable` 16 GB 이상일 때만, Python은 6 GB 이상일 때만 돌린다(earlyoom).
- 학생과 연구원 호칭은 항상 "OO 선생님"과 존댓말이다. 산출물 감사 보고에는 이모지와 "검증 완료" 같은 표시를 쓰지 않고 수, 커밋, 막힌 이유를 그대로 적는다.
- `gh`는 `~/.local/bin/gh`, `pandoc`은 `~/.local/bin/pandoc`에 있다.

## 4. 이번 세션에서 한 검증

- 정본 병합 때마다 `b300-01`에서 해당 합성 시험을 돌렸다: s4 133, s5 166, s10(4개 묶음), s10b 64(11/17 `464f516` 반영 뒤), s8, s9, s9_stimulus_swap, s10_geometry_checks, s10_rating_parts, s10_beyond_scene, s6_dispatch 11, s6_queue 17, s6_merge 모두 통과.
- `d1cbf59` 병합분의 새 시험(`tests/s8_tests.py`, `s10_mc_ridge_tests.py`, `s10_per_emotion_tests.py`, `s10_perturb_models_tests.py`, `s10b_tests.py`) 결과는 이 문서를 커밋한 뒤의 완료 보고에 적는다. 끝나지 않았거나 실패했으면 다음 세션에서 먼저 다시 돌린다.
- S6 시험(`tests/s6_tests.py`, 533개)은 시간이 길어 이번 병합 뒤 b300에서 돌리지 않았다.

## 5. 다음에 할 일 (순서대로)

1. 상태 다시 보기
   - `git -C ~/git/EmoBrain fetch origin && git -C ~/git/EmoBrain log --oneline d1cbf59..origin/design/emobrain-final-2026-11-03`
   - `sqlite3 ~/.agents/registry/chavis_teams/teams.db`의 `messages` 표에서 위 세 chat의 2026-11-16T12:37:38Z 뒤 메시지(문석진, 이태양 선생님)를 본다. chat_id는 2절의 Teams 기록과 아래 표에 있다.
   - `python3 ~/.gemini/config/skills/long-job-monitor/scripts/job_ledger.py status --run-id emobrain-core-v2`
2. 새 정본 커밋이 있으면 PR #14에 병합하고 푸시한 뒤 `b300-01`을 맞추고 새 시험을 돌린다.
   ```bash
   ssh -o BatchMode=yes b300-01 'cd /scratch/emobrain/code && git fetch origin --quiet && git reset --hard origin/feat/b300-s1-s10-onboarding && cp scripts/b300/configs/paths.b300.yaml configs/paths.yaml && cp scripts/b300/configs/env.b300.sh configs/env.sh && PYTHONPATH=src /scratch/envs/centaur/bin/python tests/<새 시험>.py'
   ```
3. `docs/FUTURE_RESEARCH_PLAN.md`를 11/17 결정에 맞게 고친다. 지금 판은 `464f516` 기준이라 다음이 옛 내용이다: 6-3 MC 전이와 6-4a를 "완료 확인 대기"로 둔 것, distillation 재학습을 선택 항목으로 둔 것, 27개 정서판 결정과 회상, 6-4e, MC 확장이 빠진 것. 고친 뒤 `qv docs/FUTURE_RESEARCH_PLAN.md`로 같은 Google Doc 검토본을 다시 연다(지금 검토본 https://docs.google.com/document/d/1r4Xu4JoH2uoL7VluRaym3RE-k5yYWNfyjWWr1mip5Xg/edit , 댓글 0개).
4. 문석진 선생님이 `s10_stats/`를 공유하면
   - 로컬과 `b300-01`에 받아 `results/` 아래에 정본판으로 두고, 옛 b300 v1 결과(`results/b300_hk_6fold/`, 근사 `roi_voxels` 60.3% 판)는 대체됨으로 표시한다.
   - `MASTER_RESULTS_SUMMARY.md`와 그림을 정본 수치로 다시 만들고 산출물 감사(deliverable-audit)와 연구 감사(research-audit)를 한다. 감사 때 볼 것: [사전] 15개 Holm 결과가 15개 모두 있는지, 27개판과 34개판을 섞어 쓰지 않았는지, S4 teacher 한계 문장, 6-2 pride 처리 기록.
5. Perlmutter에 남은 GPU 작업이 있다고 확인되면
   - 정본 `roi_voxels` 11개를 받거나 `connectome`에서 재구축한다(아래 표), `verify_s2_roi_voxels.py`가 0으로 끝나는지 확인한다.
   - `b300-live`(`http://100.92.111.86:8879/api/state`, `.slurm.nodes[].gpus_alloc`)로 빈 GPU를 확인하고 `sbatch`로만 낸다. 그 작업으로 장부 Step 2의 분모를 정한다.
6. 차지욱 교수님이 독립 실행을 지시하면 5의 재구축 경로로 바로 들어간다.

| 항목 | 값 |
| --- | --- |
| 문석진 선생님 1:1 chat | `19:baa70085-4a80-454d-8c7f-081ffb7009c0_ca7196c0-5030-4213-9988-2f0c4000d49b@unq.gbl.spaces` |
| EmoBrain 단체방 | `19:79d735a888e6484abb103d71571caa93@thread.v2` |
| 이태양 선생님 1:1 | `19:505d52bb-4c36-466f-9840-f6ebec102f17_baa70085-4a80-454d-8c7f-081ffb7009c0@unq.gbl.spaces` |
| `roi_voxels` 재구축 입력(connectome) | HK T1w `/storage/bigdata/Horikawa/fmriprep/horikawa_preprocess_sub0X/fmriprep/output/sub-0X/ses-anatomy/anat/sub-0X_ses-anatomy_desc-preproc_T1w.nii.gz`, MC T1w `/storage/bigdata/MindCaptioning/fmriprep/sub-0X/output/sub-0X/ses-anat/anat/sub-0X_ses-anat_desc-preproc_T1w.nii.gz`, `roiInf.mat` `/scratch/connectome/seokjin14/Horikawa_origin/EmotionVideoNeuralRepresentation/data/fmri/misc/roiInf.mat` |
| 재구축 순서 | `scripts/s1_original_rois.sh` → `scripts/s1_subcortex_rebuild.sh` → `src/s2_manifest.py --stage roi` (CPU 약 35~45분). 공개 자료 Figshare 11988351, 25808179, `UMPsychMethodsCore/MethodsCore@1cff4ae`(PickAtlas), `ColeLab/ColeAnticevicNetPartition@e4ea9fd` |
| b300 경로 | 코드 `/scratch/emobrain/code`, 자료 `/scratch/emobrain/data`, 산출물 `/scratch/emobrain/outputs`, Python `/scratch/envs/centaur/bin/python` |

## 6. 이번 커밋에 넣지 않은 것

- 로컬 미추적 파일 4개(2절). 이 트랙 작업이 아니다.
- 결과 수치. Perlmutter 결과표를 아직 받지 못했다.
