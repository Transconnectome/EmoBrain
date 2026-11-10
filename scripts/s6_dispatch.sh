#!/bin/bash
# S6 본실험 dispatcher를 login node에서 오래 도는 CPU 프로세스(nohup)로 켠다. GPU는 쓰지 않는다.
# dispatcher는 login01~40의 GPU 메모리와 내 s6_train 프로세스를 ssh로 보고, 빈 node마다 stream 하나를 run worktree의 scripts/s6_train.sh로 띄운다.
# stream마다 GPU 시간을 어림해(학습 횟수 x 조건별 학습 한 번의 분) --long-threshold-hours(기본 3)보다 긴 stream은 바로 sbatch(m5187_g, gpu, shared, GPU 1,
# 시간 상한 = 어림 x 2, 2~24 h)로 내고, 짧은 stream은 빈 login node를 기다린다. 낸 job의 청구 시간이 --sbatch-gpu-hours-cap(기본 160 GPU-h = 40 node-h)을
# 넘게 되면 긴 stream도 login node를 기다린다. job은 취소하지 않는다. --sbatch-gpu-hours-cap 0이면 모두 login node에서 돈다.
# 조건 사이 의존, stream 나누기, 같은 fold를 동시에 돌릴 때 위험한 점은 scripts/s6_dispatch.py 머리말에 있다.
# 준비
#   1. 동결 커밋에 맞춘 run worktree를 따로 만든다. ex) git worktree add --detach <run worktree> <동결 커밋>
#   2. run worktree에 configs/env.sh와 configs/paths.yaml을 복사한다(git 밖이라 worktree에 없다)
#   3. 먼저 --dry-run으로 stream, wave, 학습 횟수, GPU 시간 어림을 본다(ssh 없음)
# 사용(레포 최상위에서): bash scripts/s6_dispatch.sh <tag> <run worktree> <동결 커밋> --variant <이름:config:S6_OUT 하위 폴더> [--variant ...] [s6_dispatch.py 옵션]
#   ex) bash scripts/s6_dispatch.sh p1 <run worktree> <동결 커밋> --variant linear:configs/s6/run_config_p1_linear.json:s6_brain_p1_linear \
#         --variant brainit:configs/s6/run_config_p1_brainit.json:s6_brain_p1_brainit --conditions brain_only,brain_only_distill,...
#   다른 옵션: --folds 1-6, --nodes 01-40, --exclude 05,17, --poll-minutes 5, --grace-minutes 10, --max-jobs 0(상한 없음),
#     --minutes-per-training feature_encoder=25,brain_only=18 (조건=분, default=분), --long-threshold-hours 3, --sbatch-gpu-hours-cap 160, --dry-run(앞에서 돌고 끝남)
# 상태 표: <output_root>/logs/s6_dispatch_state_<tag>.tsv (variant, fold, stream, login 또는 sbatch, 조건, node 또는 job 번호, 띄운 시각 KST, log, 상태, 청구 GPU-h). 같은 명령으로 다시 켜면 이 표에서 잇는다.
# dispatcher의 log: <output_root>/logs/s6_dispatch_<tag>.log. stream마다의 log: <output_root>/logs/s6_dispatch_<tag>/
# 멈출 때: dispatcher만 끄면(kill <pid>) 띄운 학습과 낸 job은 계속 돈다. 학습까지 멈추려면 상태 표의 node와 pid(login), job 번호(sbatch)를 보고 직접 끈다.
set -euo pipefail
source "$(dirname "$0")/_env.sh"
TAG="${1:?tag}"; RUN_ROOT="${2:?run worktree}"; FREEZE="${3:?동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1
ARGS=(--tag "$TAG" --run-root "$RUN_ROOT" --freeze "$FREEZE" "$@")
for x in "$@"; do
    if [ "$x" = "--dry-run" ]; then
        exec "$PY" "$ROOT/scripts/s6_dispatch.py" "${ARGS[@]}"
    fi
done
LOG="$LOGS/s6_dispatch_${TAG}.log"
nohup "$PY" "$ROOT/scripts/s6_dispatch.py" "${ARGS[@]}" >> "$LOG" 2>&1 < /dev/null &
echo "dispatcher pid $! (host $(hostname)), log $LOG"
