# horikawa_replication

**External benchmark replication.** Horikawa et al. (2020) *iScience* Figure 6 의 voxel-level k-means clustering 결과를 우리 데이터에서 재현. EmoBrain main 연구 (D1 BrainVLM, D2 fMRI-LM, D3 CCN) 아님. paper claim 의 우리 데이터 적용 가능성 verify.

## 핵심 질문

paper 의 K=27 voxel cluster (per-subject, encoding-significant voxel, correlation distance) 가 *우리 5 subj × 2185 stim* 에서도 *top 5% high-score sample 의 low entropy* 로 나오는가.

## Pipeline (part 순서)

```
part1 voxel extraction
  -> part2 voxel selection
    -> part3 clustering
      -> part4 paper metric
```

### part1_voxel_extraction

| 항목 | 값 |
|------|-----|
| 무엇 | per-subject per-stim mean voxel pattern 추출 |
| Input | `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img/sub-XX_stimulus_N/frame_T.pt` (per-TR 3D volume) |
| Process | 모든 frame_T.pt mean across TR -> brain mask (union of nonzero voxels over 5 probe stim) -> 1D vector per stim |
| Output | `results/voxel_patterns/sub-XX.npy` shape (2185, N_voxel_masked) + `sub-XX_mask.npy` |
| Cost | 5 subj × 2185 stim × ~5 TR. CPU + I/O bound. ~1-3 hr. |

### part2_voxel_selection

| 항목 | 값 |
|------|-----|
| 무엇 | voxel-wise ridge regression (Cat34 -> BOLD) -> R² > threshold voxel 만 선택 |
| Input | part1 의 voxel_patterns + Cowen 34-cat soft rating |
| Process | 5-fold CV ridge regression voxel-by-voxel; cv R² per voxel; threshold (default p < 0.05 permutation or R² > 0.05 fixed) |
| Output | `results/voxel_selection/sub-XX_selected_voxel_idx.npy` + R² map |
| Cost | per-subject ridge over ~50k voxel × 5-fold. CPU. ~30-60 min per subj. |

### part3_clustering

| 항목 | 값 |
|------|-----|
| 무엇 | paper-style k-means K=15, 27, 50 per subject |
| Input | part1 voxel_patterns + part2 selected_voxel_idx |
| Process | StandardScaler -> PCA 256 -> L2 normalize (correlation distance proxy) -> KMeans |
| Output | `results/per_subject/voxel__sub-XX/kmeans_K{15,27,50}/labels.csv` |
| Cost | CPU only. ~10-30 min. |

### part4_paper_metric

| 항목 | 값 |
|------|-----|
| 무엇 | paper Fig 6 D/E metric. top 5% high-score sample 의 cluster sorted histogram + entropy + permutation null |
| Input | part3 의 labels.csv + Cowen 34-cat soft rating |
| Process | 각 emotion 의 top 5% sample (~109 of 2185) cluster 분포 -> sorted histogram -> entropy -> 100k 회 permutation null 과 비교 |
| Output | `results/paper_metric.csv` (source × setting × emotion × entropy + p_perm) |
| Cost | CPU. ~10-20 min (perm scales with K). |

## How to run

각 .sh 는 절대경로. sbatch 사전 승인 필수.

```bash
# part1 voxel extraction (~1-3 hr CPU + I/O)
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/code/part1_voxel_extraction/step1_voxel_extract.sh

# part2 voxel selection (~30-60 min × 5 subj CPU)
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/code/part2_voxel_selection/step1_encoding_ridge_voxel_select.sh

# part3 per-subject k-means (~10-30 min CPU)
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/code/part3_clustering/step1_voxel_kmeans_correlation.sh

# part4 paper metric (~10-20 min CPU)
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/code/part4_paper_metric/step1_sorted_histogram_entropy_perm.sh
```

## Paper 와의 정확한 일치 / 불일치 점

| 차원 | Paper | 우리 구현 | 일치? |
|---|---|---|---|
| Input type | per-subject voxel | per-subject voxel | **OK** |
| Voxel selection | encoding-significant (Methods Sec) | encoding R² > threshold (part2) | **OK** (threshold value 는 우리 default, paper exact threshold 미확인) |
| Distance | correlation (1-r) | L2-normalized PCA 256 proxy | **proxy** (cosine ≈ correlation up to mean) |
| Algorithm | k-means | k-means | **OK** |
| K | 27 main, 15/50 supp | 15, 27, 50 | **OK** |
| Evaluation | sorted histogram + entropy + permutation null | 동일 | **OK** |
