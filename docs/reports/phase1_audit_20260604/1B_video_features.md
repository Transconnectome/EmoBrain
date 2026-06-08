# Phase 1 Audit — 1B. Video feature inventory + alignment (deep)

Date: 2026-06-04
Auditor: Claude (Opus 4.7)
Scope: `/pscratch/sd/s/sjmoon/FEELIN/project/shared/data/stimulus_features/` (Track 3 video probe 의 base material). EmoViS 의 추출 코드는 audit 대상 외 (사용자 결정: video side 는 black-box input).
Inventory CSV: `1B_video_alignment.csv` (10 row)

---

## 점검 대상

- 9 video feature `.npy` (4 vision encoder × pretrained/scratch + caption_embed) + captions.json + stim_idx
- 각 파일의 shape, dtype, NaN / Inf, mean / std, symlink target
- FEEL ↔ EmoViS stim_idx 일치
- pretrained vs scratch 의 실제 차이 (scratch 가 진짜 random init 인지)
- FEEL master `feelin_canonical_stimuli.csv` 의 stim 수 / 컬럼
- Probe 측 (`run_video_probe.py`) 에서 video feature 가 어떻게 load 되는지 라인 단위 cross-check

## 점검 방법

1. 각 `.npy` 를 `np.load`, shape / mean / std / NaN / Inf 측정.
2. `os.path.islink` 로 symlink target 추적.
3. FEEL stim_idx vs EmoViS stim_idx 직접 `np.array_equal` 비교.
4. pretrained vs scratch pair × 4: mean abs diff + flattened cosine.
5. `run_video_probe.py:110-117` (`load_video_feature`) 와 `:145-180` (`build_task_data`) 를 라인 단위로 읽음.

## PASS 항목

### P_B1. 모든 video feature shape `(2185, embed_dim)`, NaN / Inf 0

| Feature | shape | dtype | mean | std |
|---------|-------|-------|------|-----|
| caption_embed | (2185, 768) | float32 | −0.000 | 0.036 |
| clip_pretrained | (2185, 1024) | float32 | +0.153 | 0.97 |
| clip_scratch | (2185, 1024) | float32 | −0.000 | 1.00 |
| dinov2_pretrained | (2185, 1536) | float32 | −0.004 | 1.28 |
| dinov2_scratch | (2185, 1536) | float32 | +0.000 | 0.92 |
| videomae_pretrained | (2185, 1280) | float32 | +0.820 | **18.46** |
| videomae_scratch | (2185, 1280) | float32 | +0.173 | 3.45 |
| vjepa2_pretrained | (2185, 1408) | float32 | −0.018 | 1.61 |
| vjepa2_scratch | (2185, 1408) | float32 | −0.000 | 0.86 |

NaN / Inf 0 in 모든 file. `finite_all = True`.

### P_B2. Symlink 통한 single source of truth

10 파일 모두 EmoViS `study1/results/00_embeddings/*/{file}` 으로의 symlink. 데이터 중복 없음. FEELIN side 에서 별도 복사본 없음 (디스크 효율). 단, EmoViS 측에서 본체 변경 시 silent propagate (informational only, 결정사항).

### P_B3. FEEL stim_idx == EmoViS stim_idx (완전 일치)

- FEEL `project/shared/data/stimulus_features/stim_idx.npy`: shape (2185,), dtype int32, 0..2184 sequential, `np.array_equal(np.arange(2185))` True
- EmoViS `study1/results/00_embeddings/caption/stim_idx.npy`: 위와 완전 일치 (`np.array_equal` True)
- 즉 FEEL row i 의 video feature = EmoViS row i = stim_idx i. canonical_stimuli.csv 의 stim_idx i 와 동일 매핑.

### P_B4. master_stimulus_index.csv 의 stim_idx 와도 일관 (PASS, 1D 의 P10 결과 활용)

`EmoViS/study1/data/master_stimulus_index.csv` 의 stim_idx (0..2184) 와 FEEL canonical `stim_idx` (0..2184) 가 정렬상 일치. score_0~33 + arousal/dominance/valence + 14 dim 모두 같은 row 에서 접근 가능. `feelin_canonical_stimuli.csv` 와 1.000000 V/A correlation (1D 의 결과) 으로 cross-validate 완료.

### P_B5. pretrained vs scratch 의 실질적 차이

4 pair 모두 cosine ≈ 0.006~0.018, mean abs diff 1~7. 직교에 가까움.

| Pair | mean abs diff | cosine |
|------|----------------|--------|
| CLIP pretrained / scratch | 1.09 | +0.006 |
| DINOv2 pretrained / scratch | 1.25 | +0.002 |
| VideoMAE pretrained / scratch | 7.44 | +0.007 |
| V-JEPA2 pretrained / scratch | 1.06 | +0.018 |

이는 scratch checkpoint 가 진짜 random init 임을 강력 시사 (cosine 이 0 근처). 만약 우연히 비슷했다면 ablation 자체가 무의미했을 것.

### P_B6. Captions.json 무결

- `project/shared/data/stimulus_features/captions.json`: 2185 entries, key = stim_idx str (0~2184)
- 모든 row 가 string caption (sample row 0: "The video shows a cityscape at dusk or early evening...")
- key range 와 video feature index 모두 일치

### P_B7. Video probe 측 load 정합

`run_video_probe.py:110-117` (`load_video_feature`):
```
feat = np.load(FEAT_DIR / filename).astype(np.float32)
stim_num = np.arange(1, feat.shape[0] + 1, dtype=np.int64)
if feat.shape[0] != 2185:
    raise ValueError(...)
```
- stim_num 을 `1..2185` 로 직접 생성 (EmoViS stim_idx 가 0..2184 이지만 FEEL canonical `stimulus_num` 은 1..2185 이므로 +1 shift)
- shape assert 로 2185 보장

`run_video_probe.py:145-180` (`build_task_data`):
- label_df merge on `stimulus_num` (1-indexed)
- `stim_to_idx` mapping → row 매핑
- StandardScaler X normalize ✓ (1A 의 F6 해결 cross-confirm)
- regression y standardize ✓ (BFM probe 와 동일)

즉 video feature side 의 0-indexed 와 brain probe side 의 1-indexed 차이가 `load_video_feature` 의 `+1` shift 로 정확히 매칭. row i 가 stim_idx i = stimulus_num (i+1).

## FLAG / 발견

### F_B1. VideoMAE 의 feature scale 이 다른 feature 의 ~10~20 배 (PASS via StandardScaler)

videomae_pretrained 의 std = 18.46. 다른 encoder std ≈ 1. 처리 책임은 probe 의 `StandardScaler` 가 짐 (`run_video_probe.py:175-178`). probe input 단계에서 unit-variance 정규화되므로 결과 비교에 confound 없음 PASS.

### F_B2. Video probe 의 코멘트와 실제 코드 불일치

`run_video_probe.py:24` docstring: "Linear + MLP heads, 3 seeds". 그러나 `SEEDS = [0]` (line 91). 즉 docstring 이 outdated (BFM probe 와 동일 default 1 seed).

→ 결과 해석에 직접적 영향 없음. 1F (BrainVLM) 와는 무관. 다만 doc 수정 필요한 minor flag.

### F_B3. EmoViS 본체 변경 시 silent propagate

10 npy 모두 symlink → EmoViS. EmoViS team 측에서 본체 재추출 시 FEELIN side 결과가 silently 바뀜. 합의된 single-source-of-truth design 이므로 의도된 동작. 단, 결과 lock 후에는 FEELIN side 에 hard copy 보존이 안전 (정책 결정 사항).

## FAIL 항목

없음.

## Verdict

**Step 1B (deep): PASS.**

- 모든 video feature shape, NaN, mean/std, symlink, stim_idx 일관성, pretrained-vs-scratch sanity, probe load 정합 모두 통과.
- EmoViS 추출 코드는 audit 대상 외 (사용자 결정).
- F_B2 (docstring) 만 minor 정정 권고.

## Action items

- F_B2: `run_video_probe.py:24` docstring 의 "3 seeds" → "default 1 seed; --seeds 0,1,2 로 final 단계 확장" 으로 정정 (실행 단계가 아닌 doc 단계).
- 결과 lock 후 video feature 본체 변경 방지를 위해 hard copy 또는 git LFS 정책 결정 (선택사항).
