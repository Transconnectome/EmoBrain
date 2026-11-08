#!/bin/bash
# Scientific question: SwiFT 5 변종 (UAH_5M / UAH_51M / UAH_202M (ver9, TP2) +
# NewE36 / NewE192 (ver11, TP1)) 의 frozen embedding 이 NewE96 (main grid 기준) 대비
# 어떤 emotion task 에서 강한가? Same SL=20, same depths (2,2,18,2).
# Model size × architecture (ver9 vs ver11) 가 emotion representation 에 미치는 영향.
# (NewE96 은 main grid 에 있음. UAH_806M / 3B / NEWdeepE192 / SL60 / HCP 는 scope 밖.)
#
# 사용법:
#   bash SwiFT_variants.sh <padding>   # padding ∈ {mean, replicate, zero, spatial_only}
# 권장: ablation 결과 의 best padding 값을 넣어줘.
#
# 5 variants × 2 init × 6 task × 2 mode × 2 head × 5 fold × 1 seed.  ~5-7h on 1 GPU.
set -e
PADDING="${1:-mean}"
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set swift_variants \
    --swift_variants_padding "${PADDING}" \
    --out_csv "results/phase1/bfm_probe_SwiFT_variants_pad-${PADDING}.csv" \
    --summary_csv "results/phase1/bfm_probe_SwiFT_variants_pad-${PADDING}_summary.csv"
