> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# part3 step2. voxel k-means with SELECTED voxels

## What

step1 (whole-brain voxel) 의 paper-faithful 버전. part2 step1 의 encoding-significant voxel selected_idx 만 사용해서 k-means.

## Process

1. `results/voxel_patterns/sub-XX.npy` 로드 (whole-brain).
2. `results/voxel_selection/sub-XX_selected_idx.npy` 로드 (part2 step1 output).
3. `x = x_all[:, selected_idx]` 로 voxel pool 축소.
4. StandardScaler -> PCA 256 -> L2 normalize (correlation distance proxy).
5. KMeans K=15, 27, 50.

## Output

`results/per_subject/voxel_selected__sub-XX/kmeans_K{15,27,50}/labels.csv`

(step1 의 `voxel__sub-XX/` 와 *다른 prefix* `voxel_selected__sub-XX/` 사용 -> part4 paper_metric 이 양쪽 모두 자동 scan)

## Why both step1 and step2

- step1 = whole-brain (우리 default).
- step2 = selected voxel only (paper-faithful).
- part4 paper_metric 이 양쪽 결과에 동일 metric (sorted histogram + entropy + perm null) 적용.
- 두 결과 비교 -> *voxel selection 이 cluster entropy 에 얼마나 영향* 정량.

## Dependency

`part1 step1` (voxel_extract) + `part2 step1` (encoding_ridge_voxel_select) 둘 다 끝나야 실행 가능.

## How to run

```bash
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/code/part3_clustering/step2_voxel_kmeans_selected.sh
```

Cost. ~5-15 min CPU (selected voxel = 5-10% of whole-brain).
