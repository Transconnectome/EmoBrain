#!/bin/bash
# S10 장면 표현으로 선형으로 얻어지지 않는 정서 평정 정보(src/s10_beyond_scene.py). GPU 없음. 규칙과 미리 적은 판정, 예측은 파이썬 파일 머리말.
# 11/18: 환경 변수 S10_LEVELS=1을 주면 물체(N), 물체 + 속성(NA) 캡션 판을 더해 돈다(출력 폴더를 따로 준다).
#        S10_LEVELS_RANDOM=1을 주면 parser 판 옆에 단어 수를 맞춘 무작위 판(RO, RA, RR)을 둔다(출력 폴더를 따로 준다).
#        S10_LEVELS_GRAPH=1을 주면 그 위에 parser 판(GO, GA, GR)과 단어 섞은 판(CS)을 더한다(출력 폴더를 따로 준다).
# targets는 몇 분(평정과 feature만), fit은 참가자당 10~20분(CPU 16 thread, 뇌 전체 포함), summarize는 몇 분.
# 사용(레포 최상위): bash scripts/s10_beyond_scene.sh targets <출력 폴더 절대 경로> <동결 커밋>
#                   bash scripts/s10_beyond_scene.sh fit <출력 폴더> <동결 커밋> <참가자 01~05>
#                   bash scripts/s10_beyond_scene.sh summarize <출력 폴더> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
STEP="${1:?targets|fit|summarize}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?동결 커밋}"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
cd "$ROOT/src"
if [ "$STEP" = fit ]; then
    "$PY" s10_beyond_scene.py fit --participant "${4:?참가자}" --out "$OUT" --design-freeze "$FREEZE" --threads 16 ${S10_LEVELS:+--levels} ${S10_LEVELS_GRAPH:+--levels-graph} ${S10_LEVELS_RANDOM:+--levels-random}
else
    "$PY" s10_beyond_scene.py "$STEP" --out "$OUT" --design-freeze "$FREEZE" --threads 16 ${S10_LEVELS:+--levels} ${S10_LEVELS_GRAPH:+--levels-graph} ${S10_LEVELS_RANDOM:+--levels-random}
fi
