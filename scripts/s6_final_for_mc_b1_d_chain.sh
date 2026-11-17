#!/bin/bash
# MC 전이용 HK 전체 모델(final_for_mc)을 B-1, D-1, D-3, D-4로 넓히는 학습 순서 실행기 (11/17 석진 님). login node에서 nohup으로 켠다.
# 설정은 configs/s6/run_config_final_for_mc_b1_d.json(규칙은 그 파일의 note). seed 0. 결과는 S6_OUT(아래 OUT).
# 순서(앞 조건의 selected.json과 fold 밖 encoder 2 캐시를 기다림. 같은 실행 번호를 쓰도록 모두 같은 run worktree, 설정, 동결 커밋으로 부른다)
#   1. 이 node: A-1(B-1과 D의 앞 조건)
#   2. 빈 node 하나: B-1 / 이 node: encoder 2
#   3. 이 node: D-4(뒤에서 돎). D-4가 fold 밖 encoder 2 다섯을 먼저 한 번만 만든다(캐시)
#   4. 캐시가 다 생기면 빈 node 여덟: D-1 후보 8개(--part i/8) / 빈 node 하나: D-3(후보 10개와 선택)
#   5. D-1 후보가 다 끝나면 D-1 선택(학습 없음), D-4가 끝날 때까지 기다림
# 빈 node: NODES 가운데 이 사용자의 학습 프로세스가 없고 GPU 메모리 사용이 1 GB 아래인 node. 없으면 5분마다 다시 본다.
# 사용: nohup bash scripts/s6_final_for_mc_b1_d_chain.sh <run worktree> <동결 커밋> > <log> 2>&1 &
set -uo pipefail
RUN_ROOT="${1:?run worktree}"; FREEZE="${2:?동결 커밋}"
OUT=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/s6_brain_final_for_mc_b1_d
CFG="$RUN_ROOT/configs/s6/run_config_final_for_mc_b1_d.json"
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s6_final_for_mc_b1_d
NODES="${NODES:-login01 login02 login03 login04 login06 login07 login08 login09 login10 login11 login12 login13 login14 login15}"
mkdir -p "$OUT" "$LOGS"
say() { echo "[$(TZ=Asia/Seoul date '+%F %T')] $*"; }
train_here() {  # $1 이름, 나머지 s6_train 인자
    local name=$1; shift
    say "시작 $name (여기 $(hostname))"
    (cd "$RUN_ROOT" && S6_OUT="$OUT" CUDA_VISIBLE_DEVICES=0 bash scripts/s6_train.sh final_for_mc "$@" > "$LOGS/$name.log" 2>&1)
    local rc=$?; say "끝 $name (종료 코드 $rc)"; return $rc
}
free_node() {
    while true; do
        for n in $NODES; do
            [ -f "$LOGS/busy_$n" ] && continue
            s=$(timeout 20 ssh -n -o ConnectTimeout=6 "$n" "ps -u $USER -o args | grep -v grep | grep -c -E 's6_train.py|s9_|s8_mc'; nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1" 2>/dev/null | tail -2 | tr '\n' ' ')
            set -- $s
            if [ "${1:-9}" = 0 ] && [ "${2:-99999}" -lt 1000 ]; then echo "$n"; return; fi
        done
        sleep 300
    done
}
train_remote() {  # $1 이름, 나머지 s6_train 인자. 빈 node에 띄우고 node 이름을 돌려준다
    local name=$1; shift
    local n; n=$(free_node); touch "$LOGS/busy_$n"
    timeout 30 ssh -n -o ConnectTimeout=8 "$n" "cd $RUN_ROOT && S6_OUT=$OUT CUDA_VISIBLE_DEVICES=0 setsid nohup bash scripts/s6_train.sh final_for_mc $* > $LOGS/$name.log 2>&1 < /dev/null & echo ok" > /dev/null 2>&1
    say "띄움 $name -> $n"
    echo "$name $n" >> "$LOGS/placement.txt"
}
selected() { [ -f "$OUT/final_for_mc/$1/selected.json" ]; }
oof_ready() { for j in 2 3 4 5 6; do [ -f "$OUT/final_for_mc/feature_encoder_oof/seed0/inner$j/done.json" ] || return 1; done; }
n_done() { ls "$OUT"/final_for_mc/"$1"/*_seed0/done.json 2>/dev/null | wc -l; }

train_here a1 brain_only "$CFG" "$FREEZE" || exit 1
train_remote b1 brain_only_featdec "$CFG" "$FREEZE"
train_here encoder2 feature_encoder "$CFG" "$FREEZE" || exit 1
train_here d4 brain_frozen_feature_encoder "$CFG" "$FREEZE" &
D4=$!
until oof_ready; do kill -0 $D4 2>/dev/null || { say "D-4가 fold 밖 encoder 2를 다 만들기 전에 끝났다. 멈춤"; exit 1; }; sleep 300; done
say "fold 밖 encoder 2 다섯 준비됨"
for i in 0 1 2 3 4 5 6 7; do train_remote "d1_part$i" brain_decoded_sep "$CFG" "$FREEZE" --part "$i/8"; done
train_remote d3 brain_features_only "$CFG" "$FREEZE"
while [ "$(n_done brain_decoded_sep)" -lt 8 ]; do sleep 300; done
wait $D4 || say "D-4 종료 코드가 0이 아니다. 기록을 볼 것"
train_here d1_select brain_decoded_sep "$CFG" "$FREEZE" || exit 1
while ! { selected brain_only_featdec && selected brain_features_only && selected brain_frozen_feature_encoder && selected brain_decoded_sep; }; do sleep 300; done
rm -f "$LOGS"/busy_*
say "모두 끝: A-1, B-1, encoder 2, D-1, D-3, D-4"
