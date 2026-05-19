# Brain-JEPA — Embedding Extraction Settings

> FEELIN Phase 1, Brain-JEPA resting-pretrained & scratch

---

## 1. Model

| 항목 | 값 | 출처 |
|---|---|---|
| Architecture | ViT-Base (`vit_base`) | EmoDe pipeline |
| Embedding dim | 768 | EmoDe README |
| Patch size | 16 | argparse default |
| Attention mode | flash_attn | argparse default |
| Add-w mode | mapping | argparse default |

## 2. Pretrained checkpoint

| 항목 | 값 |
|---|---|
| Resting-pretrained ckpt | `baseline/brain_jepa/jepa-ep300.pth` |
| Original source | ABCD resting-state fMRI (Brain-JEPA paper, epoch 300) |
| Symlink target | `/pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/Brain-JEPA/pretrained_models/jepa-ep300.pth` |
| File size | 1.5 GB |
| Scratch init | 동일 architecture, random weights (`--finetune ""` 또는 `None`) |

## 3. Input format

| 항목 | 값 | 비고 |
|---|---|---|
| Input type | ROI time series | 4D volumetric 아님 |
| Atlas | Schaefer 400 17-network + Tian S3 50 = **450 ROIs** | FEELIN canonical atlas |
| Source data | `/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series/sub-XX/stimulus_YYY/` | EmoDe에서 이미 parcellation 완료 |
| File format | `fMRI.Schaefer17n400p.csv.gz` (cortex) + `fMRI.Tian_Subcortex_S3_3T.csv.gz` (subcortex) | 두 파일 concat |
| Shape per stimulus | `(450 ROIs, T frames)` where T ∈ {5, ..., 47} | variable duration |
| Crop size (model 입력) | `450, 20` (450 ROIs × 20 frames) | EmoDe argparse default |

## 4. Padding / Window policy

Horikawa stimulus 길이 분포 (확인 결과):
- T = 5: 1,573 (71.6%)
- T ≤ 20: 2,178 (99.1%)
- T > 20: 19 (0.9%)

Model 입력은 20 frames 고정.

| Stimulus T | 처리 |
|---|---|
| T < 20 | **Replicate last frame** → 20 frames |
| T = 20 | 그대로 사용 |
| T > 20 | **앞 20 frames 사용** (전체의 0.9%만 해당) |

Replicate 선택 이유:
- Brain-JEPA는 resting-state로 pretrained → 연속 신호 가정
- Zero pad는 갑작스러운 discontinuity → OOD
- Replicate는 자극 종료 후 신호 감쇠를 근사 (mean pool에도 의미 있는 값)

`padding_ratio = (20 - T) / 20` 을 metadata에 함께 저장 → post-hoc 분석.

## 5. Normalization

- 원 데이터 (Horikawa preprocess) 에서 이미 적용된 normalization 사용
- `horikawa_preprocess_JEPA_ROI/normalization_params.npz` 참고
- 추가 normalization 없음

## 6. Embedding extraction

| 항목 | 값 |
|---|---|
| Layer | (TBD — EmoDe와 동일하게 last block 또는 CLS token) |
| Pooling | mean over tokens (EmoDe와 동일) |
| Output dim | 768 |
| Output shape per stimulus | `(768,)` |
| Per-subject embedding 수 | 2,185 (canonical) |
| 전체 embedding 수 | 2,185 × 5 subjects = 10,925 |

## 7. Output location

```
output/embeddings/brain_jepa_resting/sub-XX/stimulus_YYY.pt   # shape (768,)
output/embeddings/brain_jepa_scratch/sub-XX/stimulus_YYY.pt   # shape (768,)
```

## 8. Compute

| 항목 | 추정 |
|---|---|
| Per-stimulus inference | < 1 s on A100 |
| Per-subject (2,185 stimuli) | ~20 min |
| 전체 5 subjects | ~2 hr |
| GPU memory | < 4 GB (batch=32) |

## 9. Sanity checks (실행 후 기록)

- [ ] Output shape 검증 (모든 stimulus가 (768,) 인가)
- [ ] NaN/Inf 없음
- [ ] Subject간 embedding distribution 비교 (RDM cross-subject correlation)
- [ ] Resting vs Scratch 차이 비교 (Scratch는 chance-level 패턴이어야 함)
- [ ] EmoDe 결과 (`emotion34 Pearson r = 0.165`) 재현 가능한지 spot check

## 10. 확정 결정사항 (2026-05-16)

- **Layer / Pooling**: Final block + mean pool over patch tokens (`global_pool=True`). JEPA 표준, paper 그대로
- **Stratification**: V quartile × A quartile multilabel stratified split (8 label, iterative-stratification)
- **L0 Binary task**: V Q4 vs V Q1 (top/bottom 25%, middle 50% 제외) ~1,092 stimuli, A 동일
- **Training mode**: Pooled + Per-subject 둘 다 진행
- **Normalize**: Robust scaling (median/IQR per ROI), pad 후 적용
- **Normalize source**: `normalization_params.npz` (전체 데이터)
- **dtype**: float32
- **Subject identity**: 입력에서 제외 (subject block 안 씀, Phase 2 별도 axis)
- **Padding (3 conditions 모두 추출)**:
  - A. **Replicate last frame**: 자극 마지막 frame 복제 → 신호 천천히 감쇠 가정
  - B. **Zero pad**: padded = 0 → baseline 즉시 복귀 가정
  - C. **Mean → replicate**: 5 TR 평균 1 vector → 20 frames 복제 (시간 정보 죽임, spatial-only control)
- **Head (Linear + MLP 둘 다)**:
  - Linear: ridge (L1), logistic (L0/L2/L3), multi-output ridge (L3 multi-label)
  - MLP: 2-layer, hidden 256, ReLU, dropout 0.3
- **Training mode**: Pooled + Per-subject 둘 다
- **Phase 1 cell 수**: 6 embedding sets (2 init × 3 padding) × 5 task × 2 head × 2 mode

## 11. 미해결

- [ ] Padding 전략 최종 (replicate vs raw 재추출 vs T=5 모델 사용)
- [ ] T 길이 sweep (T=5/10/20) 가능성 — pretrained pos_embed interpolation 검증 필요
