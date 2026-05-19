# Phase 1 — Foundation (Week 1-6)

Updated: 2026-05-19
Reference: [`docs/masterplan_v2.md`](../docs/masterplan_v2.md) Phase 1.


## 목적

3 트랙 병행으로 다음 phase 진입 준비.

- Track 1 (critical path): Brain-VLM 이 우리 데이터에 transfer 되는지 검증
- Track 2: BFM 추출 완성 (vision tower 후보 4 종 준비)
- Track 3: EmoViS stimulus feature 통합 + reference caption 분석


## Track 1 — Brain-VLM transfer test (critical path)

**Goal**: ABCD 에서 학습된 BrainVLM (UMBRELLA_qwen, Qwen3-VL backbone) 이 Horikawa naturalistic fMRI 에 transfer 가능한가 검증. 이게 안 되면 Phase 2/3 plan 전면 재검토.

**작업**:
- W1-2: BrainVLM env setup. `/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen/` 의 environment + ABCD checkpoint 확보. fMRI patchifier (`project/model/patch_embed.py:13-121`) 동작 확인
- W3-4: Horikawa fMRI 5 subject 를 frozen patchifier + vision tower 통과 → token 추출. ABCD vs Horikawa token distribution (mean, var, KL divergence) 측정
- W5-6: Token-level emotion linear probe (token → V/A regression). Brain-VLM 의 ABCD-learned representation 이 emotion-relevant 한지 정량화

**산출물**:
- `code/brainvlm/load_brainvlm.py` — checkpoint loader
- `code/brainvlm/zero_shot_transfer.py` — fMRI → token + distribution analysis
- `output/brainvlm_tokens/sub-XX.pt` — 추출된 token
- `results/phase1/brainvlm_zeroshot_stats.json` — KL + token shape stats
- `results/phase1/brainvlm_zeroshot_probe.csv` — token-level V/A probe metrics

**Gate (W6)**:
- Token-level V/A linear probe r ≥ 0.3 → Phase 2 진입 (L1 frozen embedding 주입 가능)
- r < 0.3 → BrainVLM 직접 fine-tune 으로 우회 검토 (Phase 2 계획 조정)


## Track 2 — BFM 추출 완성 (병행, vision tower 후보 4 종 준비)

**Goal**: 4 BFM (SwiFT 5 변종, Brain-JEPA, NeuroSTORM, BrainLM) 의 5 subject × 2 init × proper mean padding 추출 완성. Phase 2 의 L1 swap 비교에 필요.

**현재 상태**:
- ✅ NewE96 / Brain-JEPA / NeuroSTORM × 5 subj × 2 init × **spatial_only padding** (legacy mean): 완료
- 🔄 NewE96 / Brain-JEPA / NeuroSTORM × 5 subj × 2 init × **proper mean padding**: 진행 중 (30 cell). 명령: `bash code/bfm_embeddings/run_full/proper_mean_all.sh`
- ⏳ SwiFT 나머지 4 변종 (NewE36, NewE192, UAH 51M, UAH 806M) × 5 subj × 2 init × proper mean: W3-4 시작 예정
- ⏳ BrainLM: 추출 인프라 점검 필요 (atlas 호환성 — Brain-JEPA 와 다른 A424 / 490 TR fixed)

**산출물**:
- `output/embeddings/<model>_<init>_pad-mean/sub-XX.pt` × 5 model × 2 init × 5 subj
- `output/embeddings/roi_schaefer400tian50_mean/sub-XX.pt` (Tier 1 floor 후보, 이미 추출 완료)

**Gate (W6)**:
- 4 BFM × 5 subj × 2 init = 최소 40 cell 추출 완료
- BrainLM 가능 여부 결정


## Track 3 — EmoViS stimulus feature 통합 (가벼움)

**Goal**: EmoViS 의 stimulus feature 를 FEELIN 에서 즉시 사용 가능하도록 통합. FEELIN 에서는 추출 안 함.

**작업**:
- W1: `data/stimulus_features/` 에 EmoViS symlink (이미 완료):
  - `caption_embed.npy` (2185, 768) Qwen-VL caption embedding
  - `captions.json` (2185 free-form caption)
  - `vjepa2_pretrained.npy`, `vjepa2_scratch.npy` (2185, 1408)
  - `clip_pretrained.npy`, `clip_scratch.npy`
  - `dinov2_pretrained.npy`, `dinov2_scratch.npy`
  - `videomae_pretrained.npy`, `videomae_scratch.npy`
- W2-3: FEELIN 용 unified feature loader 작성 (`code/brainvlm/data_loader.py`). stim_idx 와 brain stimulus_num align (0-indexed vs 1-indexed) 처리
- W4-5: Reference caption 분석 (Qwen-VL caption 의 emotion 분포, length, vocabulary)

**산출물**:
- `code/brainvlm/data_loader.py` — fMRI + video feature + caption 통합 dataset
- `results/phase1/caption_reference_analysis.md` — Qwen-VL caption 의 affect distribution


## W6 — Phase 1 종료 task list

체크리스트:
- [ ] Track 1: BrainVLM transfer 검증 완료, token V/A r 측정값 기록
- [ ] Track 2: 4 BFM × 5 subj × proper mean padding 100% 추출. BrainLM 가능 여부 결정
- [ ] Track 3: EmoViS feature 9 종 로딩 sanity check 통과, caption reference 분석
- [ ] Phase 2 진입 결정 작성:
  - Track 1 gate 통과 → L1 (frozen BFM embedding 주입) 으로 Phase 2 진입
  - Gate 미통과 → BrainVLM 직접 fine-tune 으로 Phase 2 계획 수정
- [ ] `CHANGELOG.md` 에 Phase 1 결정 기록 (날짜, gate 결과, 다음 action)
- [ ] README.md phase status 업데이트 (Phase 1 → 완료, Phase 2 → 진행 중)


## Pivot scenarios

- **Track 1 gate fail**: BrainVLM 이 우리 데이터에 zero-shot 안 됨. 우회: BrainVLM 의 patchifier 만 가져와서 처음부터 학습 (frozen LLM + 우리 데이터로 patchifier + projection 학습)
- **Track 2 의 BrainLM 비호환**: 3 BFM (SwiFT / Brain-JEPA / NeuroSTORM) 만으로 진행. Paper 의 BFM 비교 axis 가 4 → 3 으로 축소
- **Track 3 의 caption diversity 부족**: Qwen-VL caption 이 emotion 묘사 빈약하면 prompt 재설계 (EmoViS 측에 요청 또는 FEELIN 측에서 추가 추출)
