# Phase 1. Foundation (Week 1-6)

Updated: 2026-05-19
Reference: [`docs/masterplan_v2.md`](../docs/masterplan_v2.md) Phase 1.


## 목적

4 트랙 병행으로 다음 phase 진입 준비.

- Track 1: BrainVLM env setup + Architecture A baseline 준비 (LLM token 통합용 환경)
- Track 2: BFM frozen probe (Tier 2 ceiling). 4 BFM × 6 task × 2 mode 결과
- Track 3: Video-only probe (Tier 3 reference baseline). 9 video model × 6 task
- Track 4: EmoViS stimulus feature 통합 (Track 3 의 입력)

각 트랙의 scientific question:
- **Track 2 (BFM probe)**: 각 brain foundation model 의 frozen embedding 이 emotion 의 어떤 측면을 capture 하나?
- **Track 3 (Video probe)**: 자극 feature 만으로 emotion 예측 ceiling 은? Brain 의 added value 측정의 reference baseline. Reviewer 의 가장 큰 challenge ("brain 이 video 위에 추가하는 게 있나?") 의 직접 답.


## Track 1. Architecture Option A (LLM token, BrainVLM) transfer test (critical path)

**Goal**: ABCD 에서 학습된 BrainVLM (UMBRELLA_qwen, Qwen3-VL backbone) 이 Horikawa naturalistic fMRI 에 transfer 가능한가 검증. 이는 fMRI 통합 4 option 중 **Option A (LLM token 화)** 의 baseline architecture 검증. Option A 가 fail 시 Phase 2 의 main path 를 Option B/C/D 로 전환.

**작업**:
- W1-2: BrainVLM env setup. `/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen/` 의 environment + ABCD checkpoint 확보. fMRI patchifier (`project/model/patch_embed.py:13-121`) 동작 확인
- W3-4: Horikawa fMRI 5 subject 를 frozen patchifier + vision tower 통과 → token 추출. ABCD vs Horikawa token distribution (mean, var, KL divergence) 측정
- W5-6: Token-level emotion linear probe (token → V/A regression). Brain-VLM 의 ABCD-learned representation 이 emotion-relevant 한지 정량화

**산출물**:
- `code/brainvlm/load_brainvlm.py`. checkpoint loader
- `code/brainvlm/zero_shot_transfer.py`. fMRI → token + distribution analysis
- `output/brainvlm_tokens/sub-XX.pt`. 추출된 token
- `results/phase1/brainvlm_zeroshot_stats.json`. KL + token shape stats
- `results/phase1/brainvlm_zeroshot_probe.csv`. token-level V/A probe metrics

**Gate (W6)**:
- Token-level V/A linear probe r ≥ 0.3 → Option A main path 로 Phase 2 진입 (L1 frozen embedding 주입)
- r < 0.3 → Option A 약함, Phase 2 에서 Option B (cross-attention) 또는 C (contrastive) 를 main path 로 전환


## Track 2. BFM 추출 완성 (병행, vision tower 후보 3 종 준비)

**Goal**: 3 BFM (SwiFT 6 변종, Brain-JEPA, NeuroSTORM) 의 5 subject × 2 init × proper mean padding 추출 완성. Phase 2 의 L1 swap 비교에 필요. (BrainLM 은 490 timepoint × A424 atlas 고정으로 Horikawa 비호환, scope 제외.)

**현재 상태**:
- ✅ NewE96 / Brain-JEPA / NeuroSTORM × 5 subj × 2 init × **spatial_only padding** (legacy mean): 완료
- 🔄 NewE96 / Brain-JEPA / NeuroSTORM × 5 subj × 2 init × **proper mean padding**: 진행 중 (30 cell). 명령: `bash code/bfm_embeddings/run_full/proper_mean_all.sh`
- ⏳ SwiFT 5 변종 (NewE36, NewE192, UAH 5M, UAH 51M, UAH 202M) × 5 subj × 2 init: padding ablation 결과의 best padding 으로 W3-4 시작 예정. 명령: `bash code/bfm_embeddings/run_full/extract_swift_variants_with_padding.sh <best_padding>`

**산출물**:
- `output/embeddings/<model>_<init>_pad-mean/sub-XX.pt` × 7 model × 2 init × 5 subj
- `output/embeddings/roi_schaefer400tian50_mean/sub-XX.pt` (Tier 1 floor 후보, 이미 추출 완료)

**Gate (W6)**:
- 3 BFM × 5 subj × 2 init × main padding = 최소 30 cell 추출 완료


## Track 3. EmoViS stimulus feature 통합 (가벼움)

**Goal**: EmoViS 의 stimulus feature 를 FEEL 에서 즉시 사용 가능하도록 통합. FEEL 에서는 추출 안 함.

**작업**:
- W1: `data/stimulus_features/` 에 EmoViS symlink (이미 완료):
  - `caption_embed.npy` (2185, 768) Qwen-VL caption embedding
  - `captions.json` (2185 free-form caption)
  - `vjepa2_pretrained.npy`, `vjepa2_scratch.npy` (2185, 1408)
  - `clip_pretrained.npy`, `clip_scratch.npy`
  - `dinov2_pretrained.npy`, `dinov2_scratch.npy`
  - `videomae_pretrained.npy`, `videomae_scratch.npy`
- W2-3: FEEL 용 unified feature loader 작성 (`code/brainvlm/data_loader.py`). stim_idx 와 brain stimulus_num align (0-indexed vs 1-indexed) 처리
- W4-5: Reference caption 분석 (Qwen-VL caption 의 emotion 분포, length, vocabulary)

**산출물**:
- `code/brainvlm/data_loader.py`. fMRI + video feature + caption 통합 dataset
- `results/phase1/caption_reference_analysis.md`. Qwen-VL caption 의 affect distribution


## W6. Phase 1 종료 task list

체크리스트:
- [ ] Track 1: BrainVLM transfer 검증 완료, token V/A r 측정값 기록
- [ ] Track 2: 3 BFM (SwiFT 변종 포함) × 5 subj × proper mean padding 100% 추출
- [ ] Track 3: EmoViS feature 9 종 로딩 sanity check 통과, caption reference 분석
- [ ] Phase 2 진입 결정 작성:
  - Track 1 gate 통과 → Option A (LLM token) 의 L1 (frozen brain encoder embedding 주입) 으로 Phase 2 진입
  - Gate 미통과 → Phase 2 의 main architecture path 를 Option B (cross-attention) / C (contrastive) / D (late fusion) 중 선택해서 전환
- [ ] `CHANGELOG.md` 에 Phase 1 결정 기록 (날짜, gate 결과, 다음 action)
- [ ] README.md phase status 업데이트 (Phase 1 → 완료, Phase 2 → 진행 중)


## Pivot scenarios

- **Track 1 gate fail (Option A 부적합)**: BrainVLM 이 우리 데이터에 zero-shot 안 됨. 우회 1: BrainVLM 의 patchifier 만 가져와서 처음부터 학습. 우회 2: Phase 2 의 main path 를 Option B (cross-attention) 또는 C (contrastive) 로 전환
- **Track 3 의 caption diversity 부족**: Qwen-VL caption 이 emotion 묘사 빈약하면 prompt 재설계 (추가 추출)
