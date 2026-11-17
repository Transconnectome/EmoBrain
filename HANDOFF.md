# EmoBrain 인수인계 — b300 연계 트랙

2026-11-18 08:47 KST Git·Teams 재확인 스냅샷. 서버·시험 상태는 아래 명시한 11/17 측정 기록이다. 로컬 `/home/juke/git/EmoBrain`, 통합 브랜치 `feat/b300-s1-s10-onboarding`. 정본은 `origin/design/emobrain-final-2026-11-03 @ df9bc625afb3c07bca55bb9339dcd2c4ca22e23f`이다. 읽기 순서: `docs/final/01_integrated_document.md` → `docs/final/04_claude_code_workorder.md` → 이 문서 → `docs/FUTURE_RESEARCH_PLAN.md`.

## 1. 현재 상태

- 11/17 20:15 fetch 때 정본은 d1cbf59였으나 20:37 원격에서 새 2개 커밋을 발견했다. `1acd935`(s10_content)와 `df9bc62`(01 6-4f)를 병합한 `e63b03ea16ee452c7137c86a8a76b739c609e1e4`를 PR #14 브랜치에 푸시했다. 11/17 당시 로컬 HEAD·원격 feature·b300 HEAD가 이 커밋이었고, 로컬·b300 `src/` 차이는 정본 대비 0바이트였다. 11/18 fetch에서도 정본은 df9bc62 그대로이며 새 커밋은 0개, 로컬 `src/` 차이도 0바이트다.
- b300 동기화는 `git merge --ff-only`로 했다. 기존 미추적 12개를 보존했다. 경로는 `/scratch/emobrain/code`, Python은 `/scratch/envs/centaur/bin/python`이다.
- 새 모듈은 b300 CPU에서 합성 시험 3개(SciPy Spearman 대조, 부분상관 폐쇄식 대조, 캡션 빈도·불용어·정서어 필터)를 실행해 3/3 통과했다. `s10_content.py --help`와 셸 문법 검사도 통과했다. 실제 결과 분석·GPU 작업은 실행하지 않았다. S6 533개 시험은 병합 뒤 미실행 상태를 유지한다.
- `docs/FUTURE_RESEARCH_PLAN.md`와 아래 같은 Google Doc의 본문·제목을 df9bc62 기준으로 수정했다. Distillation 추가 사용 종료, 27개 해석판/34개 사전 검정판 구분, MC 확장·회상·6-4e 및 새 6-4f 완료 기록과 수치 미수령을 반영했다. [사전] 2-3(바)는 C-2 vs C-1로 바로잡았다.
- S3 표기는 정본의 V-JEPA 2 ViT-g 40개 block과 microsoft/deberta-large 24개 층으로 바로잡았다. 이는 구성 요구사항이며, 실제 특징 파일·manifest 및 b300 보존 상태를 이번 세션에 재점검하거나 새로 추출한 것은 아니다.
- 11/18 사용자 요청에 따른 문서 커밋 범위는 `docs/FUTURE_RESEARCH_PLAN.md`와 `HANDOFF.md` 두 파일뿐이다. 기준 e63b03e는 정본 병합 커밋이다. 문서 커밋 SHA와 실제 원격 반영 여부는 세션 완료 응답과 `git log -1 -- HANDOFF.md docs/FUTURE_RESEARCH_PLAN.md`로 확인한다. 이번에는 b300 문서 동기화나 GPU 작업을 실행하지 않는다.

## 2. 막혀 있는 것

| 항목 | 현재 근거·막힌 이유 | 다음 해제 조건 |
| --- | --- | --- |
| 정본 결과 수치 | `s10_stats/` 미수령. 실제 출력·manifest를 보지 못함 | 문석진 선생님 결과 공유 |
| 남은 GPU 분담 | 확인된 잔여 과업 없음 | 담당자 확인 후 범위 확정 |
| 정본 ROI | 20:38 독립 검사 exit 2, authentic 0/11, synthetic hash mismatch 11 | 정본 11개 수령/재구축 및 verifier exit 0 |
| Holm15 | 구현 기록은 있으나 실제 15개 실행·출력 완료 미확인 | 결과 수령 뒤 15개와 participant/mean5 묶음 검사 |
| 6-4a·depth4 | 후속 사용 기록은 있으나 이 트랙에 완료 manifest 미수령 | 결과 반입 때 실제 완료 수 확인 |

11/18 08:47 KST에 지정된 Teams 세 채팅을 다시 조회했다. 캐시 동기화 시각은 11/18 08:40:06 KST이며, 이전 확인 기준(11/17 20:10:05 KST) 이후 새 메시지는 세 채팅 모두 0개다. 마지막 메시지는 문석진 선생님 1:1 11/17 17:11:08 KST, 이태양 선생님 1:1 11/17 17:28:03 KST, 단체방 11/16 21:37:37 KST다. 따라서 갱신된 캐시에도 결과 공유·잔여 GPU 회신은 없다. 실시간 연결 도구 조회는 HTTP 403으로 거절됐고, 별도 CLI sync 직전 MemAvailable이 16,223,360 kB로 16 GiB보다 작아 실행하지 않았다. 08:40 이후의 실시간 무응답까지 단정하지 않으며, 재촉하는 메시지도 보내지 않았다.

## 3. 유지할 결정과 제약

- Distillation A-2·C-2·D-2 추가 사용 종료. A-2/C-2는 [사전] 결과, D-2는 SI. 이후 모델은 A-1, B-1, C-1, D-1, D-3(짝 포함), D-4이며 E의 기존 결과만 보존한다.
- 학습 34개판 유지, 이후 해석·분석은 27개판. 이미 시행한 34개 사전 검정은 그대로 보고한다. 6-4f는 저장 예측·캡션·73개 이름표의 기술 분석이며 검정·판정이 없다.
- 독립 b300 완결 실행은 차지욱 교수님의 별도 지시가 있을 때만 시작한다. 결과 미수령이나 연락 지연으로 전환하지 않는다.
- b300 GPU는 Slurm(sbatch/srun)만. SSH는 `ssh -O check b300-01` 성공 뒤 BatchMode로 다중화한다. 원격 dirty 상태를 확인하고 hard reset하지 않는다.
- connectome `/storage`·`/scratch`에서 find, du, grep -r, ls -R 금지. 정확한 경로나 labfind를 쓴다.
- dgx-spark Python은 MemAvailable 6 GB 이상, Teams sync는 16 GB 이상에서만. 학생·연구원은 항상 선생님과 존댓말. 감사에는 수·커밋·막힌 이유를 쓴다.

## 4. 모니터링과 다음 단계

1. 다음 세션에는 Git fetch와 정확한 Teams 세 채팅 조회부터 반복한다. 11/17 20:45 반복 관찰은 `job_ledger.py record --run-id emobrain-core-v2`에 기록했다. Step 1은 0/2, Step 2 분모는 미확정이다. 기존 장부 제목·job ID에 과거 431c1bc가 남아 있으므로 최신 note의 정확한 SHA를 읽는다.
2. 이번 세션 전용 30분 source-check 및 2시간 expiry 타이머는 20:57:42 KST에 정리했다. 두 타이머와 두 서비스 모두 `LoadState=not-found`, `ActiveState=inactive`, `SubState=dead`를 재조회했다. 서비스는 예정 실행 전부터 unloaded 상태였다. 실제 20:45 반복 점검 기록은 남아 있으나, 예정됐던 21:15 자동 실행이나 자동 만료가 관찰된 것은 아니다. 재개 시에는 필요에 맞게 세션 전용 점검을 다시 설정한다.
3. 기존 `long-job-mon-emobrain-core-v2.timer`(15분 Telegram)는 변경하지 않았고 정리 후에도 active/waiting이었다. 모든 probe가 null이라 Git/Teams를 확인하지 않는다. 이 기존 서비스에는 Python 메모리 사전 게이트가 없으며, 이번 작업에서 수정한 속성으로 보고하지 않는다.
4. `s10_stats/` 수령 후에만 results/ 정본판 반입 → MASTER_RESULTS_SUMMARY.md·그림 갱신 → deliverable-audit·research-audit를 진행한다. Holm15 15개, 27/34 정서판, S4 teacher 한계, 6-2 pride 제외를 대조한다. 실제 결과가 없으므로 이 단계는 미착수다.
5. 잔여 GPU 과업이 확인되면 아래 ROI 입력으로 수령/재구축 → verify_s2_roi_voxels.py exit 0 → b300-live 유휴 GPU 확인 → sbatch로 분담한다.

11/17 20:57:42 KST에 실행한 세션 전용 종료 명령:
```bash
systemctl --user stop emobrain-source-check-20261117-2045.timer emobrain-source-check-20261117-2045.service emobrain-source-expire-20261117-2045.timer emobrain-source-expire-20261117-2045.service
```

## 5. 산출물 지도·재개 입력

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

## 6. 파일 소유권과 함정

- 로컬 미추적 `.agents/`, `PROJECT.md`, `tests/test_challenger_m2_author.py`, `tests/test_s2_adversarial.py`는 기존 타 작업물이 포함돼 있어 일괄 stage하지 않는다.
- b300 미추적 12개는 `remote_final.log`에 남겼고 보존했다. 과거 근사 ROI 결과는 정본 수치로 쓰지 않는다.
- qv는 같은 Doc을 열 뿐 변경된 Markdown을 자동 덮어쓰지 않는다. 본문을 revision guard로 부분 수정한 뒤 재조회해야 한다. 이번 변경은 같은 Doc 제목까지 df9bc62로 맞췄다.
- 첫 실행 담당자 응답이 끊겨 중단한 뒤, 실행 전용 프로세스·타이머·파일 mtime·index lock을 확인하고 복구 담당자가 소유권을 인수했다. 기존 Doc 수정 영수증은 보존했다. 새 병합·시험·20:45 점검은 복구 담당자의 실제 실행 증거다.
