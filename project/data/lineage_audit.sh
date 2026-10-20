#!/bin/bash
#SBATCH --account=m5187
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --job-name=emobrain_lineage_audit
# W01 (issue #6) read-only lineage inventory; light enough for a login node (about a minute).
# Usage: bash /pscratch/sd/s/sjmoon/EmoBrain/project/data/lineage_audit.sh [--reconstructed REPO_PATH=FILE ...]
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)   # checkout that holds this script
REPO=/pscratch/sd/s/sjmoon/EmoBrain                          # shared server checkout being inventoried
OUT=$REPO/project/output/audits/w01_lineage/lineage_$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$REPO/project/output/audits/w01_lineage"
cd "$CODE"
"$PY" -B -m project.data.lineage_audit --repo "$REPO" --out "$OUT" "$@"
