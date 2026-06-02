# SwiFT. Embedding Extraction Settings

> FEEL Phase 1, SwiFT 5 lab pretrained models + scratch init

---

## 1. 사용 모델 5개

| Model | Code version | embed_dim | patch_size | params (대략) |
|---|---|---|---|---|
| UAH_P2_51M | ver9 | 96 | (6,6,6,2) | ~51M |
| UAH_P3_806M | ver9 | 384 | (6,6,6,2) | ~806M |
| NewUAH_newE36 | ver11 | 36 | (6,6,6,1) | ~9M |
| NewUAH_newE96 | ver11 | 96 | (6,6,6,1) | ~66M |
| NewUAH_newE192 | ver11 | 192 | (6,6,6,1) | ~264M |

**공통:** depths=(2,2,18,2), num_heads=(6,12,24,48), c_multiplier=2, last_layer_full_MSA=True, use_MuTransfer=True

**Old vs New:**
- ver9 (UAH 계열): 옛 모델, temporal patch=2
- ver11 (NewUAH 계열): 새 모델, temporal patch=1, RoPE 4D 적용

---

## 2. Pretrained Checkpoints

`baseline/swift/` 에 symlink로 두지 않고, 코드에서 직접 lab 경로 참조 (큰 파일).

```
UAH_P2_51M:    /pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P2_51M_MR_0p6_L1e-4/best.pt
UAH_P3_806M:   /pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P3_806M_MR_0p6_L2e-4/best.pt
NewUAH_newE36: /pscratch/sd/j/jubchoi/260225_newmodel/NewUAH_newE36_TP1_SL20_MR_0p8_L1e-4/best.pt
NewUAH_newE96: /pscratch/sd/j/jubchoi/260225_newmodel/NewUAH_newE96_TP1_SL20_MR_0p8_L1e-4/best.pt
NewUAH_newE192: /pscratch/sd/j/jubchoi/260225_newmodel/NewUAH_newE192_TP1_SL20_MR_0p8_L1e-4/best.pt
```

Pretrained source: UKB / ABCD resting-state, SimMIM (masked image modeling) objective, mask ratio 0.6 또는 0.8.

---

## 3. Input format

- 4D volumetric fMRI
- Shape: `(B, 1, 96, 96, 96, 20)`. batch × channel × D × H × W × T
- Spatial: (74,91,81) → (96,96,96) F.pad with background-zero (NeuroSTORM과 동일 방식)
- Temporal: T → 20 via padding mode

---

## 4. Padding (3 conditions 모두 추출)

| 조건 | 의미 |
|---|---|
| A. Replicate last frame | 자극 마지막 frame 복제 |
| B. Zero pad | padded = 0 |
| C. Mean → replicate | 5 TR 평균 → 1 vector → 20 복제 (spatial-only control) |

Spatial padding은 background-zero 고정.

---

## 5. Embedding 추출

- Final block feature → mean pool over (spatial × temporal) tokens
- Output dim per model:
  - UAH_P2_51M (embed_dim=96): final dim 96 × 2³ = 768
  - UAH_P3_806M (embed_dim=384): 3072
  - NewUAH_newE36: 288
  - NewUAH_newE96: 768
  - NewUAH_newE192: 1536
- 정확한 dim은 c_multiplier=2 × 3 stages of downsampling 으로 계산

---

## 6. Output

```
output/embeddings/swift_{MODEL}_{init}_pad-{padding}/sub-XX.npz
  - embeddings: (2185, D)
  - stim_num, padding_ratio, original_T
  - init, padding, seed, model, embed_dim, version
```

---

## 7. Compute estimate

| Model | GPU mem | Per-subject (2185 stim) | 1 padding × 5 sub |
|---|---|---|---|
| UAH_P2_51M (51M) | ~8GB | ~30 min | 2.5 hr |
| NewUAH_newE36 (9M) | ~4GB | ~15 min | 1.25 hr |
| NewUAH_newE96 (66M) | ~10GB | ~40 min | 3.3 hr |
| NewUAH_newE192 (264M) | ~20GB | ~80 min | 7 hr |
| UAH_P3_806M (806M) | ~40GB | ~3 hr | 15 hr |

5 model × 2 init × 3 padding = 30 model conditions × 5 subjects = 150 jobs.
Total GPU 시간 추정 (대략): 100~200 GPU-hours.

---

## 8. 확정 결정사항

- 5 model 모두 동일 input format (96³ × 20)
- 동일 3 padding 조건 비교
- Resting + Scratch 둘 다
- Pooled + Per-subject 학습 둘 다 (head 단계에서)
- Linear + MLP head 둘 다

---

## 9. 실행 환경

- conda env: `/pscratch/sd/s/sjmoon/swift_PTL2` (lab 표준)
- SwiFT_v2 codebase: `/pscratch/sd/s/sjmoon/SwiFT_v2/`
- Lightning + DeepSpeed 필요 없음 (우리는 frozen forward만)
