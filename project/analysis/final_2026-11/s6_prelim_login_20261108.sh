#!/bin/bash
# 11/8 발표용 예비 실행을 GPU가 비어 있는 login node 6대에 fold 하나씩 나눠 띄운다(석진 님 11/8 허락). sbatch판은 s6_prelim_20261108.sh.
# 사용: bash s6_prelim_login_20261108.sh <동결 커밋> "<fold1 노드> <fold2 노드> ... <fold6 노드>"
# 로그: project/output/final_2026-11/logs/s6_prelim_fold<k>_<노드>.log. 진행은 각 로그의 "저장"과 "발산" 줄로 본다.
set -euo pipefail
FREEZE="${1:?동결 커밋}"; read -r -a NODES <<< "${2:?노드 6개}"
[ "${#NODES[@]}" -eq 6 ] || { echo "노드는 6개여야 한다"; exit 1; }
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs
for k in 1 2 3 4 5 6; do
  h=${NODES[$((k-1))]}
  ssh -o BatchMode=yes "$h" "SLURM_ARRAY_TASK_ID=$k nohup bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s6_prelim_20261108.sh $FREEZE > $LOGS/s6_prelim_fold${k}_${h}.log 2>&1 < /dev/null &"
  echo "fold $k -> $h"
done
