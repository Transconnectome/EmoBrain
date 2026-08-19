> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# Phase 1 Audit — 1A. Embedding inventory + extraction code + .pt internals (deep)

Date: 2026-06-04
Auditor: Claude (Opus 4.7)
Scope: Zero padding only (사용자 결정, 2026-06-04).
Files audited:
- `project/shared/code/bfm_embeddings/_lib/brain_jepa.py` (329 line)
- `project/shared/code/bfm_embeddings/_lib/neurostorm.py` (268 line)
- `project/shared/code/bfm_embeddings/_lib/swift.py` (424 line)
- `project/shared/code/probes/extract_roi_features.py` (110 line, Tier 1 ROI)
- 모든 zero padding .pt 파일의 내부 payload (175 → zero scope 16 variant × 5 subj = 80 file)
Inventory CSV: `1A_embeddings_inventory.csv`

---

## 점검 대상 (확장)

표면적 무결성 (1A 첫 pass) 위에 추가로:
- 추출 코드의 frozen / no_grad / eval mode 보장 여부
- 모델별 T (시계열 길이) 처리 정책 (crop / truncate / padding)
- Pretrained checkpoint loading 의 shape adaptation
- 모델별 pooling 방식
- 모든 .pt 파일 내부의 `stim_num`, `padding_ratio`, `original_T` 메타데이터 검증
- Horikawa stim 의 실제 T 분포

## 점검 방법

`Read` 로 모든 추출 코드를 직접 읽고, 한 변종/subject 당 .pt 를 로드해 metadata 통계 측정. T 분포는 한 file 의 `original_T` 텐서에서 직접 산출.

---

## PASS 항목

### P1. 모든 추출 경로가 frozen + no_grad + eval mode

- Brain-JEPA `brain_jepa.py:279-287`: `model.head = torch.nn.Identity()` (classifier 제거), `model.to(device).eval()`, `with torch.no_grad():`
- NeuroSTORM `neurostorm.py:222-228`: `model.to(device).eval()`, `with torch.no_grad():`
- SwiFT `swift.py:352-361`: `model.to(device).eval()`, `with torch.no_grad():`
- ROI features `extract_roi_features.py:44`: 단순 numpy mean (모델 없음).

세 BFM 모두 학습 가능한 head 없이 frozen encoder forward 만 수행. PASS.

### P2. Scratch init 의 reproducibility

- 모든 코드에서 `torch.manual_seed(args.seed)` + `np.random.seed(args.seed)`, build_model 후 pretrained load 생략.
- 모든 subject 에 같은 seed (default 0) → 같은 random weights → cross-subject 비교 fair.

### P3. Pretrained loading 의 prefix stripping (NS, SwiFT)

- NeuroSTORM `neurostorm.py:154-164`: `model.` prefix 제거, `output_head` 제외, `strict=False` load.
- SwiFT `swift.py:235-261`: `_forward_module.` / `module.` / `model.` 다중 prefix 제거, `output_head` / `decoder` 제외, `strict=False` load. Missing / unexpected key 출력으로 가시적 확인 가능.

### P4. ROI feature 추출은 padding 영향 없음 (Tier 1 floor)

- `extract_roi_features.py:30-44`: Schaefer 17n400p (cortical 400) + Tian S3 50 (subcortical) = 450 ROI 각각의 csv.gz 를 로드해 시간축 평균. (450, T) → (450,).
- T 가 짧든 길든 시간축 mean 이라 dim 일정. padding 의 영향 없음.
- 즉 Tier 1 floor 는 padding artifact 의 confound 없는 깨끗한 baseline.

### P5. .pt 내부 payload 모두 정상 (zero padding scope, 80 file)

| 항목 | 결과 |
|------|------|
| `stim_num` 텐서 = 1..2185 sequential | 80 / 80 file PASS |
| `embeddings` shape = (2185, embed_dim) | 80 / 80 PASS |
| NaN / Inf | 0 |
| Embedding row 의 unique count | 모든 file 에서 2185 (collapse 없음) |
| 5 subject 간 `original_T` 동일성 | 완전 일치 (모든 subject 가 같은 stim 에서 같은 T) |
| `padding_ratio` 메타데이터 저장 | 80 / 80 |

### P6. Embed dim 의 모델 정합성

각 BFM 의 output dim 이 모델 정의로부터 예측 가능한 값과 일치.

| Model | base embed_dim | depths | c_multiplier | last stage dim | 측정된 .pt dim |
|-------|----------------|--------|--------------|----------------|----------------|
| Brain-JEPA | ViT-Base | n/a | n/a | 768 (CLS) | 768 ✓ |
| NeuroSTORM | 36 | (2,2,6,2) | 2 | 36 × 2^3 = 288 | 288 ✓ |
| SwiFT NewE36 | 36 | (2,2,18,2) | 2 | 288 | 288 ✓ |
| SwiFT NewE96 | 96 | 동일 | 2 | 768 | 768 ✓ |
| SwiFT NewE192 | 192 | 동일 | 2 | 1536 | 1536 ✓ |
| SwiFT UAH_5M | 36 | 동일 | 2 | 288 | 288 ✓ |
| SwiFT UAH_51M | 96 | 동일 | 2 | 768 | 768 ✓ |
| SwiFT UAH_202M | 192 | 동일 | 2 | 1536 | 1536 ✓ |

## FLAG / 발견 (critical, 결과 해석에 결정적)

### E1 (critical). 세 BFM 의 시계열 (T) 처리 정책이 서로 다름

`brain_jepa.py:81-118`, `neurostorm.py:81-108`, `swift.py:142-172` 라인 단위 비교.

| Model | NUM_FRAMES | T ≥ NUM_FRAMES 처리 | T < NUM_FRAMES 처리 |
|-------|------------|---------------------|---------------------|
| Brain-JEPA | **16** | **center crop** (앞/뒤 동일하게 trim, middle 16 TR) | padding |
| NeuroSTORM | **20** | **앞 20 TR truncate** (`y[..., :NUM_FRAMES]`) | padding |
| SwiFT | **20** | **앞 20 TR truncate** | padding |

결과: 같은 stim 의 T=20 이면 BJ 는 middle 16 TR 보고, NS/SwiFT 는 first 20 TR 봄. **BFM 간 직접 비교가 같은 brain signal 을 보고 있는 게 아니라 다른 frame window 위에서 수행됨**.

행동 권고: 1E 결과 정합성 단계에서 BJ vs NS/SwiFT 의 metric 차이가 model 차이인지 frame window 차이인지 분리 불가능함을 명기.

### E2 (critical). Brain-JEPA pretrained checkpoint 의 shape adaptation

`brain_jepa.py:188-223`. 사전학습된 BJ checkpoint 가 우리 input (NUM_FRAMES=16) 과 다르게 만들어진 상태라서 두 번의 shape 수술이 들어감.

1. `pos_embed_proj.emb_h` (line 195-207): ckpt 의 시간 방향 positional embedding 이 10 time patch 분량인데 우리는 1 time patch. **10 개를 단순 평균** 해서 1 개로 collapse.
2. `patch_embed.proj.weight` (line 209-219): ckpt kernel size 가 우리 kernel 과 다름. `F.interpolate(mode="linear")` 로 linear interpolation 적용.

해석: 우리가 measuring 하는 것은 "Brain-JEPA original" 이 아니라 "BJ pretrained weight 의 시간 평균 + kernel interpolation 된 변종". Pretrained 의 시간 dynamics 정보 일부가 손실됐을 가능성. 결과의 absolute level 은 BJ paper 의 reference 와 직접 비교 부적절.

행동 권고: paper / report 에서 "Brain-JEPA frozen probe" 라고만 쓰지 말고, "Brain-JEPA pretrained (1 time-patch adapted, kernel interpolated)" 식으로 명기. 또는 architecture 매칭이 가능한 NS/SwiFT 가 main reference 이고 BJ 는 reference 로 통일.

### E3 (critical). Horikawa stim 의 T 분포가 padding 을 dominant 하게 만듦

sub-01 의 `original_T` 텐서 통계 (5 subject 모두 동일):

| 통계 | 값 |
|------|-----|
| min | 5 |
| max | 47 |
| mean | 6.08 |
| median | **5** |
| std | 2.81 |
| p10 / p25 / p50 / p75 / p90 / p99 | 5 / 5 / 5 / 6 / 9 / 19 |

**Top 빈도 T**: T=5 stim 이 **1565 / 2185 = 71.6%**, T=6 이 130, T=7 이 124, T=9 가 203.

Padding 받는 stim 의 비율:

| Model | NUM_FRAMES | padded stim 수 | padded 비율 |
|-------|------------|----------------|-------------|
| Brain-JEPA | 16 | 2152 | **98.5%** |
| NeuroSTORM | 20 | 2163 | **99.0%** |
| SwiFT | 20 | 2163 | **99.0%** |

평균 `padding_ratio` (zero padding scope, .pt 메타데이터에서 직접 확인):

| Model | mean padding_ratio | mean T (역산) |
|-------|--------------------|----------------|
| Brain-JEPA | 0.627 | 5.97 |
| NeuroSTORM | 0.699 | 6.02 |
| SwiFT | 0.699 | 6.02 |

해석: zero padding 의 경우, 모델 입력의 평균 ~63% (BJ) 또는 ~70% (NS/SwiFT) 가 zero vector. 모델이 보는 정보의 30~37% 만 실제 BOLD signal. 가장 짧은 case (T=5 stim, 전체의 71.6%) 의 NS/SwiFT input 은 5 real + 15 zero (75% zero).

User decision (2026-06-04): zero padding 만 main scope 로 사용하기로 합의됨. 이 padding 비율 자체는 결과 해석 시 narrative 에서 함께 설명하는 것으로 처리. 즉 본 발견은 "audit 단계의 정량 보고" 이지 "결과 무효화" 가 아님. paper / report 에 padding_ratio 통계를 함께 reporting 하면 정직성 확보.

### E4. SwiFT 의 layer-wise 추출 옵션 미사용

`swift.py:264-289`, `--save_layers` flag = `final` (default) 또는 `all` (per-stage pooled). 현재 zero padding 결과는 final layer pooled 만 사용. layer-wise 비교 (early vs late stage) 는 결과 CSV 에 없음. 의도된 design.

### E5. NS pretrained checkpoint 는 architecture mismatch 없음 (PASS, E2 와 대조)

`neurostorm.py:154-164`. `model.` prefix 만 떼고 strict=False 로 load. shape transformation 없음. NS pretrained 는 우리 input shape 와 정확히 매칭됨.

## 추가 발견 (informational)

### N1. Subject-level T identity

모든 5 subject 의 `original_T` 가 완전히 동일. Horikawa stim 의 video duration 이 stim 마다 고정 (subject 무관). 즉 "stim → T" 가 1:1 mapping.

### N2. 정규화 방식 모델별 상이

- BJ: per-ROI median / IQR robust scaling (`brain_jepa.py:120-122`). normalization_params.npz 에서 medians, iqrs 로드.
- NS: 별도 normalize 없음. 4D volume raw value 그대로.
- SwiFT: NS 와 동일하게 별도 normalize 없음.

이 차이도 cross-BFM 비교 시 confound. BJ 가 robust scaling 의 이득 (또는 손실) 을 받음.

### N3. NeuroSTORM 의 spatial pad value = background fill

`neurostorm.py:71`: `bg = float(y.flatten()[0].item())`. 첫 voxel 의 값을 background 로 사용해 padding. 의도는 cortex 외부 voxel 의 값을 그대로 채운다는 것. 정상.

### N4. .pt payload 의 metadata 풍부

각 .pt 가 `embeddings`, `stim_num`, `padding_ratio`, `original_T`, `init`, `padding`, `seed`, `model` 메타데이터를 모두 포함. 사후 분석에서 padding_ratio 로 필터링 가능. 좋은 design.

## FAIL 항목

없음.

## Verdict (재확인)

**Step 1A (deep): PASS with serious caveats (E1, E2, E3).**

- 코드 무결성, payload, scratch reproducibility, ROI extraction 모두 PASS.
- E1, E2, E3 는 결과의 over-interpretation 을 방지하기 위해 paper / report 단계에서 반드시 명기해야 할 caveat.
- 특히 E3 (T 분포가 짧아서 padding 이 dominant) 는 BFM 결과 해석의 가장 큰 single confound. 1E 단계에서 padding_ratio < 0.5 stim subset 만으로 결과 재측정 권고.

## Action items (1E 단계로 이월)

1. **E2 follow-up**: paper / report 에서 BJ 결과를 "BJ (adapted: 1 time-patch averaged + kernel interpolated)" 로 라벨링. NS/SwiFT 는 "pretrained as-is".
2. **E1 follow-up**: 결과 표에서 "frame window: middle 16 (BJ) vs first 20 (NS/SwiFT)" 차이를 footnote 로 명기.
3. **E3 follow-up (해소)**: zero padding 사용 결정 + narrative 에서 padding 비율 함께 설명하는 방식으로 정리. 추가 subset 재측정은 보류.
