#!/bin/bash
#SBATCH --job-name=s10_perturb
#SBATCH --account=m5361
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --cpus-per-task=256
#SBATCH --time=02:00:00
#SBATCH --output=outputs/logs/s10_perturb_%j.log
# S10 6-4b 네트워크 단위 입력 교란과 ROI판(src/s10_perturb.py). GPU 없음. 6 fold가 모두 있어야 최종 표를 낸다. 규칙은 파이썬 파일 머리말.
# 영상 단위 재표집 10,000회를 단위 383 × 모델 2 × 참가자 5번 한다. 단위마다 프로세스 하나(--workers)로 나누고 BLAS는 1 thread로 둔다.
# 시간(11/15, 실제 크기의 합성 자료, 붐비는 login node): 1 thread로 단위 하나(묶음, ROI 비슷) 약 130초, 383개 합계 약 14 CPU 시간이다.
# 그래서 CPU node에 sbatch로 낸다. 128 프로세스면 10분 안팎으로 어림한다(측정하지 않음). 프로세스 하나의 메모리는 1 GB 아래로 어림한다
# 사용(레포 최상위): sbatch scripts/s10_perturb.sh <S9 perturb 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> --repeat-handling <fixed|resample> --drop-bh-family <by_model|pooled> [--s6-dir <S6 결과 폴더>]
# login node에서는 bash로 같은 인자를 준다. 프로세스 수는 S10_WORKERS(기본 4, sbatch 안에서는 128)다. --partial-check는 점검용이다
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PERT="${1:?S9 perturb 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
WORKERS="${S10_WORKERS:-$([ -n "${SLURM_JOB_ID:-}" ] && echo 128 || echo 4)}"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
"$PY" s10_perturb.py --perturb-dir "$PERT" --out "$OUT" --design-freeze "$FREEZE" --workers "$WORKERS" "$@"
