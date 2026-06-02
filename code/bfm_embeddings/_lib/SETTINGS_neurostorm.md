# NeuroSTORM. Embedding Extraction Settings

> FEEL Phase 1, NeuroSTORM resting-pretrained & scratch

---

## 1. Model

| 항목 | 값 | 출처 |
|---|---|---|
| Architecture | Swin 4D Transformer (NeuroSTORM) | EmoDe pipeline |
| embed_dim | 36 | EmoDe README |
| depth | [2, 2, 6, 2] | EmoDe README |
| c_multiplier | 2 | EmoDe README |
| patch_size | [6, 6, 6, 1] (x, y, z, t) | EmoDe README |
| window_size | [4, 4, 4, 4] | EmoDe README |
| Output embedding dim | 288 | EmoDe README |

## 2. Pretrained checkpoint

| 항목 | 값 |
|---|---|
| Resting-pretrained ckpt | `baseline/neurostorm/pt_neurostorm_mae_ratio0.5.ckpt` |
| Original source | ABCD resting-state, MAE objective, mask_ratio=0.5 |
| HuggingFace mirror | `zxcvb20001/fMRI-GPT` (자동 다운로드 fallback) |
| Symlink target | `/pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/NeuroSTORM/output/neurostorm/pt_neurostorm_mae_ratio0.5.ckpt` |
| Scratch init | 동일 architecture, random weights |

## 3. Input format

| 항목 | 값 | 비고 |
|---|---|---|
| Input type | 4D volumetric fMRI | ROI 아님 |
| Source data | `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img/sub-XX_stimulus_YYY/frame_*.pt` | EmoDe preprocessing 산출물 |
| Raw shape per frame | `(74, 91, 81, 1)` | MNI cropped volume |
| Per-stimulus shape | `(74, 91, 81, T)` where T ∈ {5, ..., 47} | variable duration |
| Model 입력 shape | `(1, 96, 96, 96, 20)` | 모델 expectation |
| dtype | float32 | min-max normalized |

## 4. Padding / Window policy

EmoDe와 동일하게 두 단계 padding 적용.

### 4.1 Spatial padding: (74, 91, 81) → (96, 96, 96)

| 축 | 원 | 목표 | Pad |
|---|---|---|---|
| X | 74 | 96 | +11 left, +11 right |
| Y | 91 | 96 | +2 left, +3 right |
| Z | 81 | 96 | +7 left, +8 right |

Pad value: background value (MNI mask 바깥 voxel과 동일).

### 4.2 Temporal padding: T → 20

| Stimulus T | 처리 |
|---|---|
| T < 20 | **Replicate last frame** → 20 frames |
| T = 20 | 그대로 사용 |
| T > 20 | **앞 20 frames 사용** (전체의 0.9%만 해당) |

이 정책은 Brain-JEPA와 일치. `padding_ratio` metadata 함께 저장.

Replicate 선택 이유: NeuroSTORM도 resting-state로 pretrained, 연속 신호 가정에 부합.

## 5. Normalization

- 원 데이터에서 이미 min-max normalized 적용 (`frame_*.pt` 파일 안)
- `global_stats.pt`에 valid_voxels, mean, std, max 저장됨
- 추가 normalization 없음

## 6. Embedding extraction

| 항목 | 값 |
|---|---|
| Extraction point | (TBD. EmoDe 동일하게 final block output, mean pool) |
| Pooling | global mean over spatial-temporal tokens |
| Output dim | 288 |
| Output shape per stimulus | `(288,)` |
| Per-subject embedding 수 | 2,185 |
| 전체 embedding 수 | 2,185 × 5 = 10,925 |

## 7. Output location

```
output/embeddings/neurostorm_resting/sub-XX/stimulus_YYY.pt   # shape (288,)
output/embeddings/neurostorm_scratch/sub-XX/stimulus_YYY.pt   # shape (288,)
```

## 8. Compute

| 항목 | 추정 |
|---|---|
| Per-stimulus inference | ~1-2 s on A100 |
| Per-subject (2,185 stimuli) | ~1 hr |
| 전체 5 subjects | ~5-6 hr |
| GPU memory | ~10-15 GB (batch=8) |

## 9. Sanity checks (실행 후 기록)

- [ ] Output shape 검증 (모든 stimulus가 (288,) 인가)
- [ ] NaN/Inf 없음
- [ ] Spatial padding이 모델 output에 의도치 않은 영향 미치지 않는지 (mask 적용 안 했음, padded voxels가 background-zero이면 attention 영향 최소)
- [ ] Temporal padding 비율별 embedding similarity (5TR padded vs 20TR raw 자극의 embedding distance가 자연스러운지)
- [ ] EmoDe 결과 (emotion34 Pearson r = 0.154) 재현 spot check

## 10. 확정 결정사항 (2026-05-16)

- **Layer / Pooling**: Final block + global mean pool over spatial-temporal tokens
- **Stratification**: V quartile × A quartile multilabel stratified split (8 label, iterative-stratification)
- **L0 Binary task**: V Q4 vs V Q1 (top/bottom 25%, middle 50% 제외), A 동일
- **Training mode**: Pooled + Per-subject 둘 다 진행
- **Normalize**: 원 데이터 min-max normalized (frame_*.pt 안에 적용됨), 추가 처리 없음
- **dtype**: float32
- **Subject identity**: 입력에서 제외 (subject block 안 씀)
- **Padding (3 conditions 모두 추출)**:
  - A. **Replicate last frame** (temporal)
  - B. **Zero pad** (temporal)
  - C. **Mean → replicate** (temporal): 5 TR 평균 → 1 volume → 20 복제 (spatial-only control)
  - Spatial padding은 background-zero 그대로 (74,91,81 → 96,96,96)
- **Head (Linear + MLP 둘 다)**:
  - Linear: ridge (L1), logistic (L0/L2/L3), multi-output ridge (L3)
  - MLP: 2-layer, hidden 256, ReLU, dropout 0.3
- **Training mode**: Pooled + Per-subject 둘 다
- **Phase 1 cell 수**: 6 embedding sets (2 init × 3 padding) × 5 task × 2 head × 2 mode
- **Seed**: 1개 우선 (scratch만 영향, frozen pretrained는 seed 영향 없음)

## 11. 미해결

- [ ] Spatial padding 시 brain mask zero-out 여부 (현재는 background-zero 그대로)
- [ ] Window attention이 padded temporal frames를 보는지. replicate라 큰 문제 아닐 듯
- [ ] T 길이 sweep 가능성
