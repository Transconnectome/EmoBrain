#!/bin/bash
# source_clustering full pipeline (pooled). CPU only, login node, ~5-20 min.
# 1. K-means + agglomerative + GMM + HDBSCAN sweep, 5 source x 4 algo x ~49 K
# 2. Quality summary (silhouette / DB / CH / NMI vs Cat34 / V/A spread)
# 3. video vs brain cluster alignment (NMI / ARI / confusion)
# 4. UMAP figures (5 coloring + cluster K=2,6,10,20,24,34,50)
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
STUDY="${REPO}/project/shared/studies/source_clustering"
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

mkdir -p "${STUDY}/results" "${STUDY}/logs"
cd "${STUDY}/code"
export PYTHONPATH="${STUDY}/code"

echo "[1/4] sweep (pooled)"
python -m part2_kmeans_sweep.step1_pooled_sweep 2>&1 | tee "${STUDY}/logs/_sweep.log"

echo "[2/4] quality summary"
python -m part3_quality_metric.quality_metrics 2>&1 | tee "${STUDY}/logs/_quality.log"

echo "[3/4] video vs brain compare"
python -m part5_cross_source.step1_compare_video_brain 2>&1 | tee "${STUDY}/logs/_compare.log"

echo "[4/4] UMAP figures"
python -m part5_cross_source.step2_visualize_umap 2>&1 | tee "${STUDY}/logs/_viz.log"

echo "[done] results under ${STUDY}/results/"
