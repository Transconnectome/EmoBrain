# part2 step1. encoding ridge voxel selection

## What

Per-subject, voxel-wise 5-fold CV ridge regression `Cat34 (soft 34-dim) -> BOLD voxel`. Per voxel cv-Pearson r squared (sign preserved). Threshold to select voxels whose BOLD activity is linearly predictable from Cowen 34-cat ratings. This mimics Horikawa et al. (2020) Figure 6 의 voxel selection step (paper restricted clustering to encoding-significant voxels, not whole-brain).

## Process

1. Load `shared/data/cowen_horikawa_labels.csv` -> X shape (2185, 34) Cowen 34-cat soft probability.
2. For each subject in {1..5}:
   - Load `results/voxel_patterns/sub-XX.npy` -> Y shape (2185, N_voxel).
   - 5-fold CV (`KFold(shuffle=True, random_state=0)`):
     - per fold: multi-output `Ridge(alpha=1.0)` fit on train, predict on test.
     - all V voxels share fit via multi-output ridge -> 5 ridge fits total, not 5*V.
   - Per voxel: cv-Pearson r = sum(yc * pc) / sqrt(sum(yc^2) * sum(pc^2)). Signed r squared = sign(r) * r^2.
   - Threshold r^2 >= 0.05 -> selected voxel indices.
3. Save `sub-XX_r2_map.npy` (full per-voxel signed r^2) + `sub-XX_selected_idx.npy` (indices).

Alpha = 1.0 fixed (no inner CV). R^2 threshold = 0.05 fixed (paper exact threshold not confirmed; common emotion-encoding voxel cutoff).

## Expected outcome

- r^2 distribution per subject. mean ~ 0.01-0.03, max ~ 0.10-0.30 (typical fMRI encoding scale).
- Selected voxel count per subject. ~1-10% of whole-brain (~500-5000 of ~50k). Paper-comparable range.
- Posterior visual + STS + amygdala voxels expected to dominate (per Horikawa paper).

## Narrative role

External benchmark prerequisite. part3 (k-means clustering) uses these voxel masks instead of whole-brain so result is comparable to paper Figure 6. EmoBrain main paper claim 영향 없음 (이건 external benchmark verification).

## How to run

```bash
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/code/part2_voxel_selection/step1_encoding_ridge_voxel_select.sh
```

Cost. 5 subj * (5-fold ridge fit on ~50k voxel) ~ 5-15 min per subj on CPU. Total ~25-75 min single CPU.

## Downstream

part3 step1 (`step1_voxel_kmeans_correlation.py`) 이 이 selected_idx 를 *옵션으로* 받아 쓸 수 있도록 추후 수정. 현재 part3 는 whole-brain 모든 voxel 사용 중. part2 결과 확인 후 part3 에 `--selected-voxel-dir` 인자 추가 예정.
