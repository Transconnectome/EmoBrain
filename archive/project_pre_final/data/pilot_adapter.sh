#!/bin/bash
#SBATCH -A m5187
#SBATCH -q shared
#SBATCH -C cpu
#SBATCH -c 4
#SBATCH --mem=24G
#SBATCH -t 00:30:00
#SBATCH -J pilot_data_audit
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/output/audits/pilot_data/slurm-%j.out
# T004 pilot data audit: inventory, full observation manifests, annotation joins,
# connected run groups, pilot-only exclusions and a metadata-only dev subset.
# Read-only over data. Writes a new directory under project/output/audits/pilot_data/.
# Usage: bash /pscratch/sd/s/sjmoon/EmoBrain/project/data/pilot_adapter.sh [--hash-arrays none|pilot|all]
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
REPO=/pscratch/sd/s/sjmoon/EmoBrain
OUT=$REPO/project/output/audits/pilot_data/audit_$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$REPO/project/output/audits/pilot_data"
cd "$REPO"
"$PY" -m project.data.pilot_adapter audit --out "$OUT" "$@"
echo "wrote $OUT"
