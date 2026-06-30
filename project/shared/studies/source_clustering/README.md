# source_clustering

**Internal source comparison.** 우리가 가진 여러 embedding source 의 cluster 구조를 같은 metric 으로 비교. EmoBrain D1/D2/D3 main 연구는 아니지만, 어느 source 가 emotion-meaningful cluster 를 만드는지가 *Task B (universal label candidate 결정)* 의 motivation evidence.

## 핵심 질문

8 embedding source 중 어느 것이 *Cowen 34-cat 과 가장 일치하는 cluster* 또는 *V/A 와 가장 coherent 한 cluster* 를 만드는가. video 와 brain 의 cluster 가 같은 자극을 같은 그룹으로 묶는가.

## Source 정의 (총 8개)

| 약어 | 정체 | shape (n_stim × dim) | 비고 |
|---|---|---|---|
| video.vjepa2 | V-JEPA2 ViT-G pretrained, 16-frame uniform sampling, last-block embed | (2185, 1408) | video temporal |
| video.clip | OpenAI CLIP ViT-L/14 image encoder, 3-frame mean (25/50/75%) | (2185, 1024) | image, not true video |
| video.dinov2 | DINOv2 ViT-G pretrained, 3-frame mean | (2185, D) | object recognition |
| video.videomae | VideoMAE v2 ViT-G pretrained, 16-frame | (2185, D) | masked video |
| video.caption | Qwen2.5-VL caption -> SBERT all-mpnet-base-v2 embed | (2185, 768) | narrative semantic |
| brain.roi_mean | Schaefer-400 + Tian-S3 50 ROI mean BOLD, mean across 5 subj | (2185, 450) | raw fMRI baseline |
| brain.brain_jepa | Brain Foundation Model. Brain-JEPA resting-pretrained checkpoint hidden state, mean across 5 subj | (2185, 768) | BFM |
| brain.swift | SwiFT NewE96_SL20 resting-pretrained checkpoint hidden state, mean across 5 subj | (2185, 768) | BFM |

약어. **BFM** = Brain Foundation Model. **SBERT** = Sentence-BERT.

## Pipeline (part 순서)

```
part1 embedding load
  -> part2 k-means sweep (pooled + per-subject)
    -> part3 quality metric
    -> part5 cross-source
```

### part1_embedding_load
- 8 source 각각의 .npy / .pt loader. Cowen label loader (`load_cowen_labels`).
- Self-contained helper module. 다른 part 가 import.

### part2_kmeans_sweep
- **step1 pooled sweep.** 5 source x 4 algo (kmeans, agglomerative_ward, gmm, hdbscan) x 49 K (K=2..50) sweep on pooled embedding. brain 은 5 subj mean.
- **step2 per_subject sweep.** brain 3 source x 5 subj x 4 algo x 49 K. brain side only.

### part3_quality_metric
- silhouette + Davies-Bouldin + Calinski-Harabasz + NMI vs Cat34 top1 + ARI vs Cat34 top1 + cluster 내 V/A 표준편차.
- Output. `results/quality_summary.csv` 1 row per (source, algo, K).

### part4_paper_metric (TBD)
- Paper Fig 6 D/E style metric (horikawa_replication 의 part4 와 같은 방법) 을 8 source 에 적용. 현재는 horikawa_replication 의 voxel cluster 에만 적용 중. 필요 시 추가.

### part5_cross_source
- **step1 compare_video_brain.** 같은 algo + 같은 K 에서 video source 와 brain source 의 cluster assignment NMI / ARI / confusion matrix.
- **step2 visualize_umap.** 5 coloring (cowen top1, top2, entropy, valence, arousal) + cluster K=2/6/10/20/24/34/50 의 UMAP 산점도.

## How to run

```bash
# 전체 (pooled 4 단계, ~5-20 min CPU)
bash /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/source_clustering/code/run_all.sh

# per-subject sweep (brain 만, ~15-30 min CPU)
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/source_clustering/code/part2_kmeans_sweep/step2_per_subject_sweep.sh
```

## horikawa_replication 과의 관계

| 차원 | horikawa_replication | source_clustering |
|---|---|---|
| 목적 | paper Fig 6 의 우리 데이터 재현 (external benchmark) | 우리 source 의 cluster 정성 비교 (internal motivation evidence) |
| Input | brain voxel only (~50k voxel) | 8 embedding source |
| Subject | per-subject | pooled mean + per-subject (brain) |
| Distance | correlation (paper) | standard L2 (PCA 128) |
| K | 15, 27, 50 (paper main + supp) | 2..50 sweep |
| Evaluation | sorted histogram + entropy + perm null | silhouette + DB + CH + NMI + ARI + V/A spread |

두 study 의 결과를 합쳐 보면 *brain representation 의 추상화 수준* (voxel 50k -> ROI mean 450 -> BFM hidden 768) 에 따라 cluster 의 emotion-coherence 가 어떻게 변하는지 부가로 확인 가능.
