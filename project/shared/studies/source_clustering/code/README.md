# `clustering/` — exploratory clustering pipeline

Standalone. D1 / D2 의 학습에 통합되지 않은 분석 단계. "Task B 의 universal label 후보 결정" 의 전 단계 evidence 만 수집.

## 무엇을 하는가

5 embedding source 위에서 4 algo × ~9 K sweep + 평가.

| Side | Source | Path | D |
|------|--------|------|---|
| Video | V-JEPA2 pretrained | `data/stimulus_features/vjepa2_pretrained.npy` | 1408 |
| Video | CLIP pretrained | `data/stimulus_features/clip_pretrained.npy` | 1024 |
| Brain | ROI mean (Schaefer-400 + Tian-50) | `output/embeddings/roi_schaefer400tian50_mean/sub-XX.pt` | 450 |
| Brain | Brain-JEPA hidden state | `output/embeddings/brain_jepa_resting_pad-mean/sub-XX.pt` | 768 |
| Brain | SwiFT NewE96 | `output/embeddings/swift_NewE96_SL20_resting_pad-mean/sub-XX.pt` | 768 |

Brain side 는 5 subject 의 (N_stim, D) 을 단순 평균해서 pooled brain embedding 으로.

| Algo | 설명 |
|------|------|
| `kmeans` | centroid, spherical, K 고정 |
| `agglomerative_ward` | hierarchical Ward linkage, K 고정 |
| `gmm` | Gaussian mixture, diagonal cov, K 고정 |
| `hdbscan` | density, K 자동 |

| K | 의미 |
|---|------|
| 2, 3 | binary-like split |
| 5, 6 | broad emotion family (Cowen broad) |
| 10, 15, 20 | mid-grained |
| 34 | Cowen 34-cat 와 직접 비교 |
| 50 | over-clustering 한계 보임 |

## 실행

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/shared/code/clustering/run_all.sh
```

CPU 만, login node 에서 1 회 통째로 돌림. 약 5-20 분.

## 산출

```
project/shared/results/clustering/
├── <source>/<algo>_K<K>/labels.csv     per-stim (stim_idx, cluster_id)
├── quality_summary.csv                  source × setting 의 silhouette / DB / CH / NMI vs Cat34 / ARI vs Cat34 / V/A spread
├── video_vs_brain.csv                   video × brain 의 NMI / ARI
├── _confusion/<v>__vs__<b>__<setting>.npy   per-comparison confusion matrix
└── figures/<source>_<setting>.png       UMAP scatter (cluster id 색칠) + <source>_cowen.png (Cowen cat34 색칠)
```

## 무엇을 보면 되는가

- `quality_summary.csv` 의 `nmi_vs_cat34`. cluster 가 Cowen 34 와 얼마나 일치하는지. 높으면 → cluster 가 emotion-meaningful.
- `quality_summary.csv` 의 `va_spread`. cluster 내 V/A 의 표준편차. 낮으면 → cluster 가 emotion-coherent.
- `video_vs_brain.csv` 의 `nmi`. video 와 brain 의 cluster 일치도. 높으면 → "brain 이 video surface 반영", 낮으면 → "brain 이 다른 구조 추가".
- `figures/` 의 UMAP. cluster 분리가 시각적으로 깨끗한지.

## Task B 와의 연결

이 단계의 결과가 충분히 의미있어 보이면, 다음 step:
- video cluster id (또는 brain cluster id) 를 D1 / D2 의 새 supervision (`ClusterIdHead`) 으로 통합.
- cluster id 가 Cat34 보다 더 안정적이거나 cross-dataset 일관성이 높으면 Task B 의 universal label 후보로 확정.

지금 단계는 D1 / D2 코드에 cluster id 통합 안 함.
