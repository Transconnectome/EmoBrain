# EmoBrain Build Log

각 코드 사이클 완료 (파일 구현 + sanity 통과) 시 상단 append.
결정 사항 은 `project_decisions.md` 별도.

Spec §12 build order 기준.
1. data 모듈 (labels, datasets, caption_map, fmri_adapter)
2. models/losses + evaluation/metrics
3. baseline (B1 ridge, B2 modality solo)
4. models (encoders, projector, prompt, llm_backbone)
5. student (hard only)
6. teacher + video_encoder
7. distillation
8. eval 확장

---

## 2026-07-13. Cycle 22. 스펙 1-3 Acceptance 감사 + Horikawa 전처리 QC/QA

**What.** (a) 실험 시작 전 스펙 build 1-3 단계 재사용 가능 여부 를 Acceptance 로 실측 감사. (b) 우리가 실제 학습 에 쓰는 Horikawa 전처리 데이터 의 무결성 QC 와 시간평균 정보손실 진단.

**Files.** `project/scripts/audit_spec_stage123.py` + `.sh`, `project/scripts/qc_horikawa_data.py` + `.sh`. 출력 `project/shared/results/spec_stage123_audit.json`, `project/shared/results/qc/horikawa_data_qc.json`.

**감사 결과 (17/17 PASS).** 34 감정 순서 부록 A 일치, 라벨 crowd proportion [0,1] (zero 73.8%, row-sum 1.71), z-score train-only fit, split 누출 0 (test 220 이 5 subject 공통), 지표 7 종 + Pearson/CCC/Spearman, B1 ridge 리포트 존재. → **data / labels / caption_map / fmri_adapter / metrics / losses / baseline 재사용 확정.** 단 기본 normalizer 가 `log1p_z` 로 스펙 §5-2 (순수 z-score) 이탈 발견 → decision log 2026-07-13 에서 log1p_z 를 canonical 로 확정 + config 노출.

**QC 결과 (0 FAIL, 실질 WARN 0).** NaN/Inf 0 (ROI·볼륨·raw), 자극 5×2185 결측 0, **roi_mean = 마스크된 시간평균 정확 일치 (9.5e-08)**, 죽은 ROI 0, 이상치 |z|>5 가 0.02% 미만, subject 자극 순서 동일 + ISC +0.238 (기존 0.235 재현), 볼륨 shape 일관 / NaN 0 / global_stats 40/40 일치 / brain mask 23%. 초기 WARN 2 건 은 전부 설명 됨. 볼륨 dir 10980 = 5×2196 (11 repeat 포함), 프레임 수 편차 는 `n_frame == original_T == valid_TR` 일치율 100% 로 자극 길이 그 자체.

**핵심 진단. 시간평균 은 신호 를 안 버렸다.** roi_mean (450) test profile pearson **+0.2961** vs 시간요약 mean+std+max+min (1800) **+0.2854** (delta −0.011). 시간 정보 를 4 배 늘려도 디코딩 이 나아지지 않음. → **Stage 0 R0 (ROI-mean 천장 0.31) 이 전처리 아티팩트 가 아님 을 실증.** "시간축 을 버려서 그렇다" 는 반론 차단. 단 이는 hand-crafted 시간요약 에 한정 이며 학습된 시간 모델 (SwiFT 4D, Brain-JEPA) 은 미배제 (E3 finetune 이 시험 대상).

**남은 headroom 후보 (좁혀짐).** 시간 해상도 배제 → **공간 해상도 (450 ROI 가 brain voxel 약 12.5 만 개 를 278 배 압축)** 가 최유력, 그 다음 학습된 encoder (E3 finetune), fusion 축.

## 2026-07-21. Cycle 24. Architecture 전체 세팅 (스펙 §6-8, project/code) — swappable encoder × Qwen3-VL × teacher/student

**What.** 사용자 지시 "architecture 전체 세팅". 탐색 종료, 스펙 §6-8 을 `project/code/` 에 구축. Encoder 라인업 재정의 (ridge baseline / ViT Encoder1 / BFM Encoder2, simple projection 폐기).

**Files.**
- `brain_encoder/`. `base.py` (계약 + adapt 축 frozen/lora/full), `registry.py` (swap 팩토리), `e2_ridge_encoder.py` (등록명 `ridge`), `e_vit.py` (ViT, frozen/LoRA), `e_bfm.py` (Brain-JEPA/SwiFT, frozen=precomputed 임베딩 실구현 / finetune=명시적 NotImplementedError). `e1_projection.py` 삭제.
- `adapters/projector.py` (MLP + Q-Former, per-encoder/per-modality).
- `fusion/`. `prompt.py` (Question/Caption 필드 §8-3 + token order §7.2), `backbone.py` (계약 + stub), `backbone_qwen.py` (Qwen3-VL-4B, LoRA), `model.py` (EmoBrainModel, modality flag 로 teacher/student 통합), `head.py` (Linear34 z-space), `build.py` (config 팩토리).
- `losses.py` (supervised + distillation mse/kl, curriculum active_mask).
- `training/trainer.py` + `.sh` (config-driven, Track A direct).
- `configs/` 6 종 (_cpu_smoke, ridge/vit/bfm_jepa/bfm_swift student, ridge teacher).

**검증 (CPU).** (1) 인코더 3 종 교체 = 동일 배치 → (B,34), ridge(D_enc 34)/vit(768)/bfm(768) 이 하류 동일. (2) frozen/lora 축 = vit frozen projector 만 1.22M vs vit lora +ViT q,v 590k = 1.81M, frozen 시 grad 0. (3) teacher 폼 video+caption+brain+question 조립 정상. (4) loss supervised(full/mask)/distill(mse/kl)/total 작동. (5) bfm finetune 명시적 에러. (6) **end-to-end trainer 실데이터 (8740 train/1085 val) 1 epoch 통과** (stub backbone, 배선 검증).

**Runnable.** Track A direct 는 지금 실행 가능 (모든 encoder × modality). GPU config = Qwen3-VL-4B (다운로드 완료). **미구현 = (a) BFM in-loop finetune (Brain-JEPA/SwiFT forward 통합), (b) Track B distillation soft-label 캐싱, (c) video/caption dropout 학습 전략.** 이는 다음 사이클.

## 2026-07-21 (3). Cycle 26. Track B distillation 배선 (스펙 §8.6.1 offline 3 단계)

**What.** Track B 를 코드로 완성 (실행 은 GPU). 이전 = distillation loss 함수 만 있고 trainer 는 lambda_dist=0.

**Files.**
- `training/train_teacher.py` + `.sh`. teacher (brain+video+caption) 를 34D 라벨 로 학습, best val 시점 weight 를 checkpoint 저장.
- `training/cache_soft_labels.py` + `.sh`. 얼린 teacher 를 train+val 전 자극 에 forward → raw 34D (softmax 없음, §8.4) 를 `(subject|stim)` 키 로 `teacher_soft_labels/<tag>/soft_labels.pt` 저장.
- `training/train_student_distill.py` + `.sh`. student (brain-only, 추론 form) 가 캐시 를 조회 → `L_main + lambda·L_distill`. 캐시 miss 는 active_mask 로 distill 만 제외.
- `trainer.make_collate` 에 subject 추가 (soft-label 키). configs `_cpu_teacher`, `_cpu_student_distill`, `ridge_student_distill_qwen`, `ridge_teacher_qwen` (teacher_ckpt/run.name).

**검증 (CPU stub, end-to-end 3 단계).** teacher 학습 → checkpoint 저장 → soft-label 9825 개 (8740 train + 1085 val) 캐싱 → student 가 캐시 로드 후 distill loss 로 학습. student loss Track A ~1.2 → Track B 56.8 = **distill 항 실제 engage 확인** (stub teacher 랜덤 출력 이라 값 큼, 배선 검증). 음수 pearson 은 랜덤 stub 5 배치 라 예상.

**남은 것.** BFM in-loop finetune, caption/video dropout, distillation 검증 A/B (variance partitioning + brain-ablated student, §8.9.2). Context lift = student-distill − Track A direct (둘 다 brain-only) 는 GPU 실행 후 산출.

## 2026-07-21 (2). Cycle 25. 마커 토큰 + CCC loss + verbalize(alpha) layer

**What.** Cycle 24 architecture 정련 3 건.

**1. 세그먼트 마커 토큰 (red-team C4, 스펙 §6-5).** `fusion/model.py` 에 fresh learnable `<seg_start>`/`<seg_end>` (brain/video/caption/question 각 2 개, 총 8 개). 이전 조립 은 순서 로만 암묵 구분. 검증 = 각 세그먼트 +2 토큰, 출력 (B,34) 유지.

**2. CCC loss (스펙 §9-1 headline 정렬).** `losses.py` 에 per-clip `ccc_loss` (1 − CCC over 34 emotions per clip). config `loss.hard_kind: mse|huber|ccc|mse+ccc` + `ccc_weight`. Trainer 연결. 검증 = 완벽예측 0, **스케일 절반(Pearson=1) 0.207** (MSE/correlation 이 못 잡는 진폭 miscalibration 을 CCC 가 잡음, Pearson 0.30 vs CCC 0.17 격차 의 직접 대응). 기본값 은 mse 유지 (34D sparse 에서 CCC 우위 는 GPU A/B 로 실측 후 결정).

**3. verbalize alpha layer (`evaluation/verbalize.py`).** 34D z 예측 → expm1 역변환 → 상위 감정 → 템플릿 문장. 학습 없는 순수 후처리. 공존(bittersweet) 보존 (softmax 없음). 검증 = 실제 라벨 로 정확한 문장 생성.
- **위치 정직화.** 이는 편의/발표 layer 이지 decoder/기여 아님. "자연어 디코딩" framing 금지. 자연어 생성 을 진짜 decoder 로 하는 beta 경로 (EmoMind 식 = 34D condition → LLM caption 생성) 는 **EmoMind 과 정면 중복 이라 미채택** (decision log 2026-07-21). D1 이 실패 한 것 은 "매핑 을 생성 으로 학습" 이고 EmoMind 도 이를 피함 (stage1 ridge + stage2 rewriter).

## 2026-07-13. Cycle 23. tylee `Horikawa_Haka` NIfTI 데이터 QC + Qwen3-VL-4B 확보

**What.** tylee 권한 개방 후 `/pscratch/sd/t/tylee/Horikawa_Haka` QC. 우리가 그동안 "nii 없음" 으로 알던 것 의 정정. 여기 **`.nii.gz` 11,285 개** 존재.

**구조.** `img/sub-0X/sub-0X_stimulus-N.nii.gz` (자극당 4D 볼륨 1 개) + `meta/` (horikawa_meta_data_with_dimension_binary.csv, semantic_features.csv, vision_features.csv, splits/).

**개수 정합 (초기 불일치 는 해소).** subject 당 2257 파일 = `stimulus-N.nii.gz` 2197 개 (N=0..2196) + `stimulus-0_vN.nii.gz` 60 개. **stimulus-0 = rest/fixation 블록 (총 61 개)**, 실제 자극 은 1~2196 = 전체 presentation 수 와 정확히 일치. 우리 canonical 2185 는 전부 포함, 추가 12 개 = rest + 11 repeat. **데이터 문제 아님.**

**품질 (30 샘플 × 5 subject).** 공간 shape (97,115,97) 단일, 2mm 등방, affine 일관. TR 5/7/9/11 가변 (영상 길이 반영). **NaN/Inf 0.** brain mask 22.5~23.9%.

**정규화 확답.** tylee 볼륨 은 **파일 자체 가 z-score** (brain mean 0.02, std 0.95, 값 −5.8~6.1). 우리 `.pt` 는 raw (비음수) 로 저장 하고 SwiFT 로드 시 `znorm_minback` 적용. **두 파이프라인 다 정규화 되어 있고 단계 만 다름.** "볼륨 normalization 누락" 우려 는 해소.

**두 파이프라인 비교.** tylee 97×115×97 @2mm (약 108 만 voxel, z-score 완료, 표준 NIfTI) vs ours 74×91×81 (약 55 만, raw, 프레임별 .pt). **tylee 가 해상도 약 2 배 + 표준 포맷.**

**의미.** Cycle 22 에서 시간축 은 무죄 로 판명 됐고 남은 용의자 는 공간 해상도 (450 ROI = voxel 약 12.5 만 개 의 278 배 압축). **tylee nii 가 그 가설 을 시험할 최적 재료** (전체 voxel 격자 + z-score + 표준 포맷). voxel 수준 디코딩 이 0.31 을 넘는지 가 R0 의 범위 를 결정.

**부수.** Qwen3-VL-4B-Instruct 를 `/pscratch/sd/s/sjmoon/hf_cache` 에 다운로드 완료 (계산노드 오프라인 대비).

## 2026-07-09. Cycle 21. Stage 0 emotion-space decoding noise ceiling (critic-revised)

**What.** Stage 0 gate 의 decoding noise ceiling 을 34D-profile Pearson 자 위 에서 계산. 이전 sqrt(ISC) ROI-space 방법 은 철회 (wrong units + Case I 못 잡음). emovi-method-critic (2026-07-09) 판정 반영 하여 in-units 2-anchor 보수적 구성 으로 재작성.

**Files.**
- `project/scripts/stage0_decoding_ceiling.py` + `.sh` (신규). anchor A (inter-subject decoding 합의) + anchor B (representation saturation, kernel vs linear ridge) + 11-repeat 서술 + inflation 진단 + Case 판정.
- 출력 `project/shared/results/noise_ceiling/decoding_ceiling.json` (신규, 덮어쓰기 없음).
- 재사용 = FmriAdapter roi_mean, Cowen34 z-score, horikawa_split (test 220 자극 subject 공통 확인), profile_correlation. ridge 0.294 와 동일 파이프라인.

**Result (ROI-mean).** ridge pooled 0.294 / within 0.307. kernel ridge within 0.313 (flex−linear +0.006). anchor A inter-subject 합의 0.678 인데 decoder-vs-truth 0.307 (gap +0.371) → **anchor A 는 shared-label-structure inflation, ceiling 실격** (critic 예측 적중). Operative ceiling (B) 0.313, headroom +0.019 → **Case I (R0), ROI-mean 한정**.

**판정.** ROI-mean 표현 은 포화 (~0.31). E1/E2 는 이 천장 에 갇힘. E3(BFM)/E4(VLM) 는 richer input 이라 이 천장 에 안 묶임 → richer-rep ceiling 측정 이 pending gate. Smoke = 전 컴포넌트 CPU 통과, 11-repeat 0.088 재현.

## 2026-07-08. Cycle 20. E3 (frozen BFM) 경로 — SwiFT/JEPA/NeuroSTORM 배관

**What.** encoder ladder 확장. E1(raw ROI) 옆에 E3(frozen BFM). 핵심 = encoder 새로 안 짜고 **dataset 이 내주는 brain 벡터만 교체** (raw ROI 450 → frozen BFM 임베딩). Phase 1 임베딩 35 variant (SwiFT 20 / brain_jepa 8 / neurostorm 6 / roi 1) 이 `project/shared/output/embeddings/<variant>/sub-XX.pt` 에 (2185, dim) 로 이미 존재 (추출 불필요).

**Files.**
- `project/data/bfm_source.py` (BFMSource. variant .pt 로드 = embeddings(2185,dim)+stim_num, `get(subject,stim)` 로 임베딩. FmriAdapter 와 동일 인터페이스).
- `project/data/datasets.py` (`brain_source` 파라미터. roi_mean→FmriAdapter, 아니면 BFMSource variant).
- `project/models/encoders/identity.py` (frozen 벡터 passthrough, 학습 param 0 = "projector 만"). `build.py` 등록.
- `project/training/train.py` (config data.brain_source 를 dataset 에 전달).
- configs. `trackA_e3_swift_stub_cpu.yaml` (smoke), `trackA_e3_{swift,jepa,neurostorm}_qwen.yaml` (dim 768/768/288).

**CPU stub smoke.** enc=identity, trainable 627k (projector+stub+head, encoder 0). SwiFT 768 배관 흐름 확인 (에러 0). val ~0 (예상. identity encoder + tiny 무작위 stub 은 frozen BFM 못 읽음. E1-stub 이 0.17 인 건 trainable MLP encoder 덕분). **E3 판정은 Qwen 에서** (Phase 1 ridge 는 이 임베딩으로 ~0.30 → 신호 있음).

**Meaning.** 35 variant 이 config 스왑 (brain_source + encoder.dim). E1(raw) vs E3(frozen BFM) = "사전학습 BFM 이 raw ROI 보다 낫나". 다음 = E3 Qwen 3종 GPU 실행 → E1(0.25)/ridge(0.30) 대비. E2(ridge latent)/E4(fine-tune)는 이후.

---

## 2026-07-08. Cycle 19. Qwen backbone 첫 가동 (GPU, E1+LoRA end-to-end 학습 확인)

**What.** stub → 실제 Qwen2.5-3B-Instruct backbone. E1(MLP) + LoRA(attention) + projector + head 를 GPU 에서 학습. peft 0.19.1 설치. NERSC offline 대응 (login predownload → HF_HOME scratch cache → bash/GPU 실행, 사용자 salloc GPU 노드).

**Files.** `configs/trackA_e1_qwen_gpusmoke.yaml`, `trackA_e1_qwen_full.yaml`. `scripts/predownload_qwen.py`+`.sh`. `training/train_qwen.sh` (HF_HOME set bash launcher), `train_qwen_gpusmoke.sbatch`. `models/backbones/qwen.py` (tokenize/pad 보정). `models/emobrain_model.py` (dtype cast 2곳. brain token → backbone bf16, pooled → head fp32). `train.py` (step 로깅 + robust check = windowed train loss OR val_pearson gain).

**버그 2개 잡음.** (1) brain token fp32 → LLM bf16 concat dtype mismatch. (2) LLM bf16 pooled → head fp32 mismatch. 둘 다 dtype cast 로 해결. + check 노이즈 오판 (per-batch loss 26~135 변동 → 단일 step 비교 무의미 → windowed avg + val gain 으로 교체).

**GPU smoke (bash, 사용자, Qwen2.5-3B, 50 batch).** trainable 42.5M (LoRA+E1+proj+head, LLM base frozen). **step loss 135→48→31→30→26 명확 하강**, check drop +38 → OK learning. head/LoRA 가 50 step 만에 큰 초기 출력 잡고 train 맞춰감. val 0.02 (50 step 뿐, 무의미).

**Meaning.** 실제 3B LLM 경로 (load, LoRA, brain+question forward, backward, optim, eval) 전부 검증. 학습 명확히 작동. 다음 = full config (전체 데이터, epoch 3, batch 8) → **E1+Qwen(LoRA) 의 ridge(0.30/0.17) 대비 첫 실 val 숫자.**

---

## 2026-07-08. Cycle 18. 학습 루프 train.py (CPU stub 검증 통과)

**What.** `training/train.py` = config → build_model → AdamW 학습 루프 → val 평가 (compute_metrics profile/error). 모델 갈아끼워도 루프 불변. Track A / E1 / CPU-stub config 로 최적화 동작 검증 (정확도 아님).

**Files.** `project/training/train.py`, `configs/trackA_e1_stub_cpu.yaml` (stub, cpu, 20 batch × 5 epoch), `training/train.sh`.

**Smoke (CPU, bash, 사용자 실행).** train_loss 34.58 → 32.96 (drop +1.62) = `OK optimization runs`. 더 중요. **val 단조 상승** (pearson -0.02→+0.17, ccc→+0.07, mse_z 1.13→1.07 단조 하강). held-out val 이 오르는 건 파이프라인 (진짜 fMRI→E1→projector→stub transformer→head) 이 뇌→감정 신호 를 실제로 학습 한다는 신호. 100 step tiny stub 인데도 val pearson +0.17 (ridge 0.30 절반, 진짜 LLM 아님). train_loss 노이즈 (epoch2 spike) 는 shuffle+서브셋+tiny 탓, 신뢰 신호 는 val 단조.

**Meaning.** 학습 루프 + 데이터 배관 + loss + eval 전부 정상. 다음 = Qwen backbone (config 한 줄 스왑 stub→qwen, cpu→cuda) + sbatch. NERSC 함정. compute 노드 offline → login 노드 에서 모델 pre-download 후 offline 로드. 모델 선택 (text-only Qwen vs Qwen3-VL) + GPU account/queue 확정 필요.

---

## 2026-07-08. Cycle 17. Data <-> model 어댑터 (실데이터 배치 → 모델 → loss)

**What.** 골격(더미 텐서)에 실제 HorikawaDataset 을 연결. dataset dict (fmri, label, meta) + spec §8-3 고정 question 을 모델 forward 입력 (fmri, text_ids, text_mask) 으로 변환. Backbone 계약에 `tokenize` 추가 (stub 간이 hash / qwen 실제 tokenizer) → collate 는 backbone-agnostic.

**Files.**
- `project/models/prompt.py` (spec §8-3 고정 Question, cowen34_order 에서 34감정 목록 자동 채움, TRACK_A_QUESTION).
- `project/training/collate.py` (make_collate(question, backbone) → collate_fn. fmri/label stack + question tokenize + caption 별도 유지).
- `project/models/base.py` + `backbones/stub.py` + `backbones/qwen.py` (Backbone.tokenize 추가. stub = deterministic hash 간이 tokenizer, qwen = 실제 tokenizer + pad_token 보정).
- `project/scripts/data_model_smoke.py` + `.sh`.

**Smoke (CPU, bash, no download).** val 1085 샘플 → collate → build_model(stub) forward → `pred (8,34)` finite → `supervised_loss = 35.95`. loss ≈ 34 는 z-space 무작위 예측 기대값 (감정당 ~1 std, 합 ~34, losses_smoke scale sanity 와 일치) → loss 계산 정상 부착 확인. text_ids (8,85) = 고정 question 85 토큰. student 형태 (brain + question) 그대로.

**Meaning.** 디스크→모델→loss 배관 완성. 학습 루프는 이제 optimizer + epoch + eval 만 얹으면 됨. 다음 = Qwen backbone 실장 (GPU) + `training/train.py` (config → build_model → loop → metrics), sbatch (사전 승인). E1-through-LLM 첫 실결과 = ridge (0.30) 대비.

---

## 2026-07-07. Cycle 16. Swappable model skeleton (registry + factory, Step 4 시작)

**What.** 모델 컴포넌트 를 config/이름 으로 갈아끼우는 골격 (NV3 swappable adapter). 학습 스크립트 는 "어떤 모델" 만 config 로 지정, encoder/backbone 교체 = config 한 줄. LLM-free E1/E2 는 ridge baseline 과 중복 이라 폐기, encoder 는 처음부터 LLM 통과 로 확정 (design_plan §5.1 미결 해소).

**계약 (갈아끼우기 핵심).** `base.py` 4 계약. BrainEncoder(.out_dim 노출) / Projector(any in_dim → llm_dim, n_tokens 고정) / Backbone(.hidden_dim, embed_text) / Head(34D z-space, no activation). build.py 가 dim 자동 주입 (projector.in_dim=encoder.out_dim, head.hidden_dim=backbone.hidden_dim) → downstream dim 하드코딩 없음.

**Files.**
- `project/models/base.py` (계약), `registry.py` (register/build/available), `build.py` (factory, qwen lazy import), `emobrain_model.py` (배선. brain token prepend + text embed, modalities 토글 = teacher/student).
- `encoders/e1_raw_roi.py` (E1 = ROI→MLP), `projectors/mlp.py` (pool→n_tokens×llm_dim), `backbones/stub.py` (CPU smoke 용 tiny transformer, no download), `backbones/qwen.py` (real, transformers lazy, GPU), `heads/linear34.py` (linear, softmax 금지).
- `configs/smoke_e1_stub.yaml`, `scripts/model_build_smoke.py` + `.sh`.

**Smoke (CPU, bash, no download).** `build_model(cfg)` → forward [4,34] 통과. config 만 바꿔 n_tokens 8→16, enc out_dim 128→256, brain on→off (ablation) 이 코드 수정 0 으로 다른 모델 재배선 됨을 확인. 전부 finite, softmax 없음.

**CAUTION 준수.** softmax 없음 / text 는 tokenizer+embed 만 (projector 안 붙임) / caption 별도 field / frozen·finetune 은 별개 축 (config) / brain-ablated student 는 modalities 토글.

**Meaning.** "스크립트에서 모델만 지정" 이 실물 로 동작. 이후 E2/E3/E4 encoder, Qwen backbone, Q-Former projector 는 파일 1개 + `@register` 로 config 선택 대상. 다음 = 실제 데이터 배치 로 forward (HorikawaDataset ↔ 모델 입력 어댑터) + Qwen backbone 실장 + 학습 루프 (sbatch, 사전 승인).

---

## 2026-07-07. Cycle 15. report_0707 외부 검토 반영 (사실/해석 오류 정정, no new code)

**What.** report_0707.md 외부 검토 (사용자) 의 6 지적 을 verify 후 반영. 2 는 반드시 고칠 사실/해석 오류, 4 는 완성도.

**반드시 고친 것 (사실/해석 오류).**
1. **Stimulus 수 = 2185 unique (재확인, 2185 가 맞음).** 검토자 는 "2196" 을 제안 했으나 사용자 정정 + EmoViS DECISIONS (2026-05-08) 확인 결과 **2185 가 맞음**. fMRI session 에 2196 presentation 이 있으나 11 개 는 reliability check 로 두 번 제시된 중복. Unique = 2196 − 11 = 2185. 우리 canonical 2185 정확. (내가 fmri_raw.npy 축 2196 만 보고 잠깐 2196 으로 바꿨다가 원복. presentation 수 ≠ unique stimulus 수.) CLAUDE.md / CONTEXT / report 에 "2185 unique, 2196 presentation w/ 11 repeat" 로 명시.
2. **EmoMind RSA 0.09 vs 우리 RSA 0.78 비교 = apples-to-oranges.** 두 RSA 는 측정 대상 다름. EmoMind = brain-decoded RDM vs caption RDM 의 cross-modal Spearman (이질 공간, 원래 낮음). 우리 0.78 = predicted 34D vs target 34D 의 same-space RSA (원래 높음). 우리 자체 노트 (emomind_exploitation_20260622) 도 "정량 동일시 금지" 명시. report §6-4 에서 대소 비교 제거 + 두 정의 명시. §4.1 RSA 행 도 "same-space" 명시.

**완성도 정정.**
3. MindCaptioning 연도 2024 → 2025 (Science Advances 2025, bioRxiv preprint 2024).
4. Label 스케일 명시. 원점수 = crowd 비율 0-1, 학습/평가 는 log1p_z 후 z-space. §4.1 의 정답 range [-1,+4] 는 log1p_z 후 값 (원점수 아님) 명시.
5. 열린질문 1 ISC ceiling 표현 정정. ISC 는 decoding ceiling 아니라 뇌 신호 subject 간 신뢰도 (다른 축), LOSO 는 transfer 성능 이지 상한 아님. 둘 다 상한 직접 대리 아님.
6. **열린질문 2 (distillation 검증) 를 Track B 필수 항목 으로 승격.** Video (B2 CLIP 0.60 >> brain 0.30) 우회 주입 을 "brain decoding" 으로 오인 방지. 검증 A (variance partitioning) + 검증 B (brain-ablated student). architecture §8.9.2 + ACTION_PLAN S10.2 에 필수 로 추가.

**부가.** within-subject n_train (1748, pooled 의 1/5) 를 §4.3 표 에 추가 (데이터 적은데도 최고 라는 handicap 감안).

**Meaning.** 이 프로젝트 의 가장 날카로운 질문 (distillation 이 brain vs video 중 무엇 을 학습) 을 열어두지 않고 Track B 성공 판정 조건 (context lift + 검증 A/B) 으로 못박음. 사실 오류 (stimulus 수, RSA 비교) 는 리뷰어 가 즉시 지적 할 것 이라 정정 필수 였음.

---

## 2026-07-07. Cycle 14. CCC metric 추가 (Pearson + CCC + MSE 함께)

**What.** 사용자 지적 ("패턴 만 맞으면 되나, MSE 로 판단 해야 하는 거 아냐?") → 웹 조사 후 CCC (Concordance Correlation Coefficient) 를 headline metric 에 추가. CCC 는 shape (Pearson) + value/scale (MSE 성분) 을 하나 로 합침. 감정 인식 (AVEC) 표준.

**Files.**
- `project/evaluation/metrics.py` (`_ccc`, profile 에 ccc_mean, per_emotion 에 per_emotion_ccc + rare_ccc)
- `project/scripts/metrics_smoke.py` (half-scale 검증 추가)
- `project/training/train_baseline_ridge.py`, `train_modality_solo.py` (print 에 CCC)

**CCC 공식.** `2ρσxσy / (σx² + σy² + (μx−μy)²)`. 분자 = correlation, 분모 = 분산 차이 + 평균 차이. 모양 + 값 동시 penalize. 범위 [-1, 1].

**Smoke 검증.** Perfect → CCC 1.0. **Half-scale (값 을 절반 으로) → Pearson 1.0 인데 CCC 0.80.** CCC 가 scale mismatch 를 penalize 함 을 실증. 사용자 우려 를 metric 으로 구현.

**B1/B2 재확인 (Pearson vs CCC).**
| Modality | Pearson | CCC | gap |
|----------|---------|-----|-----|
| Brain | 0.296 | 0.173 | -42% |
| Video V-JEPA2 | 0.449 | 0.343 | -24% |
| Video CLIP | 0.597 | 0.506 | -15% |
| Caption | 0.479 | 0.377 | -21% |

**해석.** 모든 modality 에서 CCC < Pearson. Ridge 가 regularization 으로 예측 진폭 을 눌러 (예측 range [-0.45,+0.36] vs 정답 [-1,+4]) 패턴 은 맞아도 값 이 작음 → CCC 가 이 진폭 mismatch 를 잡음. Brain gap 이 가장 큼 (-42%, 신호 약해 특히 conservative). Rare emotion CCC 0.096 (Pearson 0.20 의 절반) — rare 를 거의 0 으로만 예측. **CCC 가 baseline 의 진짜 그림 을 드러냄. Brain-only 는 Pearson 0.30 이지만 CCC 0.17 로 값 을 절반 도 못 맞춤.**

**Meaning.** Headline = Pearson (모양) + CCC (모양+값) + MSE (보조). 하나 만 보면 속음 (Pearson 은 scale-blind, MSE 는 sparse 에서 무딤). 앞으로 LLM model 은 Pearson 뿐 아니라 CCC (진폭) 도 올려야. Ridge 가 진폭 을 못 살렸으니 개선 여지 가 CCC 로 더 명확. 문서 반영 (framework_EN/KR primary metric, implementation_spec §9).

---

## 2026-07-07. Cycle 13. B2 modality solo (baseline ladder 완성)

**What.** Single-modality ridge (brain / video / caption 각 단독 → 34D). Video 지배 가 34D task 에서도 성립 하는지 확인. Baseline ladder 완성.

**Files.**
- `project/training/train_modality_solo.py`, `project/scripts/train_modality_solo.sh`
- Output. `project/shared/results/baseline/b2_modality_solo.json`

**결과 (test, log1p_z, profile pearson).**
- Brain ROI mean = 0.296 (RSA 0.777, p@1 0.19).
- Video V-JEPA2 = 0.449 (RSA 0.796, p@1 0.31).
- **Video CLIP = 0.597** (RSA 0.868, p@1 0.45) — modality 최고.
- Caption = 0.479 (RSA 0.835, p@1 0.31).

**해석. Video 지배 34D 에서도 명확.** CLIP video 0.60 vs brain 0.30 (2배). VA binary 의 dominance (video probe 0.97 vs brain 0.72) 가 34D 에서 재현. Video/caption 모두 brain 을 크게 앞섬. RSA 도 video (0.87) > brain (0.78).

**Framework 함의.** B2 는 leakage 위험 의 실증. Teacher 에 video 직접 주고 joint 학습 하면 model 이 video (0.60) 에 의존, brain (0.30) 무시 → spine 붕괴. 그래서 student 는 brain-only, video 는 teacher soft label 통해 간접 전달 (Track B distillation). B2 가 이 설계 정당성 을 정량 입증. Context lift 상한 시사 (teacher 최소 video 0.60 수준, student 가 distill 로 얼마나 따라가나).

**Baseline ladder.** chance ~0.00 / brain 0.30 / V-JEPA2 0.45 / caption 0.48 / CLIP 0.60. Track A (encoder) 가 brain-only 로 0.30 을 얼마나 올리나, Track B 가 context 로 얼마나 끌어올리나 가 다음.

**Meaning.** Baseline 전부 완성. Modality dominance 정량 확정. 다음 = Step 4 models (encoder E1-E4) 진입, Track A.

---

## 2026-07-07. Cycle 12. Label 전처리 log1p_z 확정 + LOSO chance

**What.** Label 전처리 를 log1p_z 로 확정. `Cowen34Normalizer` 에 mode 파라미터 (zscore / log1p_z) 추가, 두 mode 별도 norm_stats 파일 생성. LOSO chance level 을 permutation 으로 확정.

**Files.**
- `project/data/labels.py` (mode 파라미터. log1p_z default. save/load 에 mode 저장)
- `project/scripts/labels_fit.py` (두 mode 다 fit → `cowen34_train_{log1p_z,zscore}.pt` + default `cowen34_train.pt` = log1p_z)

**LOSO chance (permutation).**
- LOSO real 0.232 vs permutation chance 0.001 ± 0.015 (label shuffle, 15 perm).
- Real 이 chance 대비 15.3 SD 위. Correlation metric 의 chance 는 실제 로 0 근처 확정. LOSO 0.232 는 압도적 유의 = universal code 진짜 신호.

**Label 전처리 결정.** log1p_z default. 근거. 3 전처리 비교 (Cycle 8) 에서 log1p_z 가 rare emotion 이득 + 극단 z 완화 (max 20.4 → 17.5) + clip 처럼 순위 손실 없음. 차이 미미 (0.294 → 0.296) 하지만 균형적. NN 학습 gradient 안정 에도 도움. norm_stats 는 별도 파일 (사용자 요청) — mode 별 파일 + default 파일 3 개.

**B1 재실행 (log1p_z).** profile 0.294 → 0.296, RSA 0.768 → 0.777, MAE(raw) 0.063 → 0.054. 미세 개선.

**Meaning.** 모든 후속 실험 이 log1p_z 사용 (default norm_stats). zscore 도 파일 유지 (필요 시 ablation). Label 전처리 확정 완료.

---

## 2026-07-07. Cycle 11. Subject regime 비교 (within / pooled / LOSO) + universal framing 확정

**What.** ISC (0.23) < ridge (0.29) 의 두 해석 을 within/pooled/LOSO ridge 비교 로 구별. 결과 로 pooling 의 목적 을 "universal emotion code 학습" 으로 확정 (개인차 극복 아님).

**Files.**
- `project/scripts/ridge_subject_regimes.py`, `.sh`
- Output. `project/shared/results/noise_ceiling/ridge_subject_regimes.json`

**결과 (profile pearson, test).**
- Within-subject (각 subject 따로, avg 5) = 0.305.
- Pooled (5 subj) = 0.294.
- LOSO (4 train → 1 held-out, avg 5 fold) = 0.232.
- **Within > Pooled > LOSO.** 해석 2 (label-anchored, 개인 뇌-label 매핑 이 subject 마다 다름) 확정.

**해석 (universal framing, 사용자 확정).**
- Pooling 목적 = **universal (subject-공통) emotion code 만 학습**. 개인차 극복 이 아니라 개인차 를 의도적 으로 배제 하고 공통 신호 만 잡음.
- Within > Pooled 는 예상 된 결과 (feature, not bug). Within 은 개인 특화 를 학습 해서 높지만, 그건 우리 spine question (사람 일반 의 감정 표상) 과 다른 질문 (subject-specific) 에 답 하는 것. Within 성능 이 높아도 우리 관심 아님.
- **LOSO 0.232 가 가장 의미 있는 숫자.** 본 적 없는 subject 에 전이 = pure universal code. Chance (0) 대비 확실 히 높음 = universal emotion code 가 뇌 에 존재 하는 증거.
- Pooled 는 universal 지향 (개인차 평균), LOSO 는 pure universal (새 subject). 두 숫자 가 spine 의 target.

**Context lift 의 위치 재정리.** Context (video/caption) 는 개인차 극복 도구 가 아니라 **universal code 의 SNR 개선 도구**. 뇌 만 으로 universal code 를 뽑는데 뇌 신호 가 noisy → subject-invariant context (모든 사람 같은 영상) 가 감정 정보 보강 → teacher 가 더 정확한 universal soft label → student distill. Track B context lift 가 이걸 검증.

**개인차 는 다음 step.** Universal 확립 (Step 1, 지금) → 개인차 가 universal 위 에 어떻게 얹히나 (Step 2, 별도/future work).

**주의 (over-claim 방지).** LOSO 0.232 < pooled 0.294 (개인차 때문 에 새 subject 하락). "우리 model 이 새 subject 에 전이 된다" 는 chance 이상 이지만 성능 하락 을 인정 하며 서술. Over-claim 금지.

**Meaning.** ISC 0.23 은 실제 cross-subject 제약 이었고 (LOSO 하락 으로 확인), 그게 R0 를 부분 지지. 하지만 universal 관점 에서 는 문제 아님 (LOSO 가 chance 이상 = universal code 존재). Pooling 정당성 = 성능 최적화 아니라 universal code 검증 설계. 다음 = label 전처리 확정 후 B2 modality solo, 그 다음 Track A encoder.

---

## 2026-07-07. Cycle 10. Brain cross-subject ISC (noise ceiling estimator)

**What.** 5 subject 가 같은 자극 을 봤을 때 뇌 반응 의 subject 간 일관성. Ridge 0.29 를 맥락화 하는 첫 noise ceiling estimator. Cowen concordance (categorical) 를 estimator 에서 뺀 뒤 실제 측정 가능한 것.

**Files.**
- `project/evaluation/noise_ceiling.py` (`spatial_isc`, `per_roi_isc`)
- `project/scripts/measure_brain_isc.py`, `.sh`
- Output. `project/shared/results/noise_ceiling/{brain_isc.json, per_roi_isc.npy}`

**결과 (test split, 10 subject pair).**
- Spatial ISC (자극별 450-ROI pattern 의 subject 간 correlation) mean 0.235, median 0.233.
- Per-ROI ISC (ROI별 자극 profile 의 subject 간 correlation) mean 0.149, median 0.127.
- Top ROI ISC 0.51 (idx 210, 261, ...) = 일부 영역 (초기 시각 피질 추정) 은 subject 간 매우 일관, 대부분 영역 은 낮음.
- ALL stimuli 도 유사 (spatial 0.238, per-ROI 0.151).

**해석.** ISC 0.23 은 낮은 편. 뇌 신호 가 subject 간 상당히 idiosyncratic. 시각 자극 이라 시각 영역 은 공통, 고차 영역 은 개인차 큼 (예상 부합). ISC 는 감정 decoding ceiling 이 아니라 stimulus-driven 뇌 신호 일관성. Ridge 0.29 > ISC 0.23 의 의미 는 Cycle 11 에서 within/pooled/LOSO 로 규명.

**Meaning.** Noise ceiling estimator 첫 측정. Cowen concordance 를 뺀 뒤 우리 데이터 로 잴 수 있는 실제 estimator. 다음 (Cycle 11) 에서 이 낮은 ISC 가 decoding 에 실제 제약 인지 판정.

---

## 2026-07-07. Cycle 9. Cowen 2017 문헌 검증 + 34D 라벨 정의 확정 (문서 정정, no new code)

**What.** 사용자 지적 으로 "ICC 0.54" 원출처 를 웹 검증. Cowen-Keltner 2017 원문 (PMC5617253) 확인 결과 오류 발견. 34D 라벨 의 실제 정의 를 우리 데이터 로 확정.

**문헌 검증 (원문).**
- "concordance averaging 54% (chance 27%)". **ICC 아님.** Concordance = 같은 category 를 고른 rater 비율.
- 영상당 9-17 rater, 34 category yes/no. 34 rating → 27 cluster.

**라벨 정의 (우리 데이터 검증).**
- 각 값 = crowd proportion (k/n, n=영상별 rater 9-30 median 13). 기약분수 저장. "1-9 점수" 아님.
- 영상당 34D 합 1.71, 73.8% 0. Sparse 는 yes/no 응답 본질.

**철회.** ICC 0.54 를 continuous metric ceiling 으로 fraction normalize 하는 계획. Concordance 는 categorical 이라 continuous Pearson 과 단위 다름. Stage 0 estimator 에서 concordance 제외, brain ISC / label split-half 로 대체.

**Files (문서 만, 코드 없음).** framework_EN/KR (6곳), architecture_design (§8.5.4/5, §11), implementation_spec (§3/5-1/5-2), ACTION_PLAN, ppt_outline, project_decisions (2026-07-07 entry).

**Meaning.** Label 이 crowd proportion (yes/no 비율) 임 이 확정 되어 sparse (73.8% 0) 가 데이터 특성 으로 재확인. Noise ceiling 은 문헌 concordance 가 아니라 우리 가 직접 측정 (brain ISC 가능, label split-half 는 rater-level 확보 시). Label 전처리 결정 (log1p_z vs zscore) 은 여전히 baseline 성능 기준 으로, ceiling 무관. 다음 = brain cross-subject ISC 측정 또는 label 전처리 확정 후 B2 / Track A.

---

## 2026-07-03. Cycle 8. B1 ridge baseline + metric 확장 + label 진단 (Step 3 시작)

**What.** 첫 실질 실험. LLM 없는 순수 ridge (fMRI ROI mean → 34D z-scored label, 감정 별 독립). Metric 을 전 계열 로 확장 (correlation + MSE/MAE/R2 + sparse retrieval). Label 전처리 3 종 비교 + heavy-zero 진단.

**Files.**
- `project/training/train_baseline_ridge.py`, `project/scripts/train_baseline_ridge.sh`
- `project/evaluation/metrics.py` (확장. error + sparse_retrieval 추가, profile 에 median/cosine)
- `project/scripts/metrics_smoke.py` (확장 검증)
- `project/scripts/compare_label_preprocess.py`, `.sh` (3 전처리 비교, decision experiment)

**B1 결과 (test).**
- Headline profile pearson mean/median 0.294 / 0.315, spearman 0.211, cosine 0.292.
- MSE(z) 0.904 vs all-zero 0.989 (improve +0.085, R2 0.080). Sparse label 이라 MSE 개선폭 작지만 양수 R2 = 학습 됨.
- Sparse retrieval p@1 0.19 (chance 0.029 대비 6.5×), p@5 0.34 (chance 0.15 대비 2.3×).
- Per-emotion mean 0.274, range [0.09, 0.46], rare 0.20.
- RSA 0.768 (이미 높음). Dim-compression k=1 0.65 → k≥2 0.26-0.37 (저차원 잡고 고차원 약함).

**Null model 검증.** 0.29 가 trivial 아님 을 3 null 로 확인. 평균-profile 예측 -0.03, label shuffle +0.004, fMRI shuffle 후 ridge +0.0003. 실제 fMRI-label 매칭 있을 때만 0.29 나옴.

**Label 진단 (중요).**
- Raw label 73.8% 가 0. 영상당 평균 8.9/34 감정 만 활성 (영상당 34D 합 1.71). **Sparse 가 감정 데이터 의 본질** (rater 가 영상당 느낀 감정 몇 개 만 선택), 데이터 오류 아님.
- "전부 0 예측 MSE ~1.0" 은 z-score 의 수학적 성질 (z 분산 = 1), 데이터 문제 아님. Model 이 이걸 넘으면 (ridge 0.90) 학습 된 것.
- 감정별 편차 큼. Pearson range 0.09 (guilt, envy, 추상적/사회적) ~ 0.46 (sexual desire, aesthetic, disgust, 시각적으로 뚜렷). 빈도 낮은 감정 이 대체로 성능 낮음.

**Label 전처리 3 종 비교 (미결).** zscore / log1p_z / zscore_clip. Profile pearson 0.294 / 0.296 / 0.304, 차이 미미 (0.01). 감정별 로는 log1p_z 가 rare 에서 이득 (0.236 vs clip 0.227), clip 은 Spearman 희생 + rare 손실. log1p_z 가 균형적 이나 효과 작음. **결정 은 noise ceiling 측정 후 로 보류. 현재 순수 zscore 유지.**

**결정.** Metric 은 "구할 수 있는 모든 것" 방침 (사용자). Label 전처리 확정 은 rating reliability ceiling (다음 사이클, 20 rater split-half) 측정 후.

**Meaning.** 우리 pipeline (data + loss + metric) 이 실제 결과 를 내는 첫 검증 통과. Baseline 이 모든 metric 에서 chance 대비 신호 있으나 절대값 낮음 = 우리 LLM model 이 올릴 target 명확 (sparse retrieval p@1, dim-compression 고차원, rare emotion). RSA 는 이미 높아 개선 여지 작음. B2 modality solo + Track A encoder 가 이 baseline 을 anchor 로.

---

## 2026-07-03. Cycle 7. Evaluation metrics (Step 2 완성)

**What.** 채점용 metric 4 개. Loss 는 학습 연료, metric 은 성적표. Headline = per-clip 34D profile Pearson + Spearman. 부가 = per-emotion Pearson, RSA, dim compression curve. Config-selectable dispatcher `compute_metrics`.

**설계.**
- `profile_correlation(pred, target)`. HEADLINE. Clip 마다 34D vector 간 Pearson + Spearman → clip 평균. "이 영상 의 감정 profile 이 정답 profile 과 닮았나".
- `per_emotion_correlation(pred, target, rare_idx)`. 감정 마다 clip 을 가로질러 Pearson → 34 값 + 전체 mean + rare subset mean.
- `rsa(pred, target)`. Predicted 34×34 corr matrix upper-triangle vs target upper-triangle Pearson. Structure preservation.
- `dim_compression_curve(pred, target, ks)`. Target PCA top-k 축 에 사영 후 profile correlation 유지율. 고차원 구조 실재 검증.
- `compute_metrics(pred, target, which)`. Dispatcher.

**결정.** Constant vector (std=0) clip 은 correlation undefined → skip + skip 수 report (NaN 오염 방지). 표준.

**Files.**
- `project/evaluation/metrics.py`
- `project/scripts/metrics_smoke.py`, `.sh`

**Sanity.**
- profile. Perfect → Pearson 1.0, Spearman 1.0. Random → ±0.006 (≈ 0). Constant clip 1 개 → skipped=1, 나머지 199 used (NaN 안 섞임).
- per_emotion. Perfect → mean 1.0, rare_mean 1.0.
- rsa. Perfect → 1.0 (561 pair = C(34,2)). Emotion order shuffle → 0.04 (구조 깨짐).
- dim_compression. Perfect → 모든 k 에서 1.0. k=1 은 single dim 이라 sign agreement proxy.
- dispatcher. `which=["profile","rsa"]` → 정확 히 두 키.

**의존성.** scipy 1.17.1 (Spearman), sklearn 1.8.0 (PCA). tribev2 venv 에 존재 확인.

**Meaning.** Step 2 완성. Baseline B1 부터 최종 model 까지 모든 결과 를 이 metric 으로 채점. Headline = per-clip profile Pearson 확정. 다음 = Step 3 baseline (`train_baseline_ridge.py` = 첫 실질 실험). Distillation loss (`models/losses/distillation.py`) 는 teacher 있을 때 (Step 6-7) 추가.

---

## 2026-07-03. Cycle 6. Loss 함수 (Step 2 시작)

**What.** 두 loss function. `supervised.py` (per-emotion MSE, main, 항상 ON) + `structure.py` (34×34 correlation matrix matching, optional, 기본 OFF). Stateless function 으로 구현 (class 불필요).

**설계.**
- `supervised_loss(pred, target, active, per_emotion_weight, huber_delta)`. Per-sample 34 감정 sum → batch mean. Softmax / KL / CE 없음. `active` mask 로 curriculum subset (top-1/2/k) 지원. `per_emotion_weight` optional. `huber_delta` optional (Huber 대안).
- `structure_loss(pred, target, min_batch)`. Batch 안 predicted 34×34 correlation matrix vs target correlation matrix 의 MSE. Batch < 4 reject (correlation 불안정).
- Total loss 는 trainer 에서 `λ_hard × L_main + λ_struct × L_struct`. Default `λ_struct = 0.0` (관계 학습 OFF).

**결정.** 감정 간 관계 학습 은 기본 OFF (structure loss). Loss 는 각 감정 독립 회귀 만. 관계 는 (a) model shared representation 이 implicit 학습, (b) metric (per-clip Pearson, RSA) 으로 사후 관찰. Structure loss 는 config 로 켜는 실험 축 (`lambda_struct` sweep) 으로 남김.

**Files.**
- `project/models/losses/supervised.py`
- `project/models/losses/structure.py`
- `project/scripts/losses_smoke.py`, `.sh`

**Sanity.**
- Supervised. pred==target → 0. z-space scale 검증 (모든 감정 +1 std off → loss 정확 히 34). Active top-1 mask → loss 정확 히 1.0. Per-emotion weight (emo0 ×2) → 35.0. Wrong emotion dim reject.
- Structure. pred==target → 0. Shared-factor target (감정 간 실제 correlation 존재) 에서 감정 절반 sign flip → loss 0.651 (0 대비 크게 증가, sensitivity 확인). Tiny batch (2) reject.
- Smoke test 초안 은 random Gaussian target 으로 structure 를 test 했 는데, i.i.d. Gaussian 은 감정 축 이 무상관 이라 sign flip 해도 loss 변화 미미. Shared-factor target 으로 수정 하여 correlation 구조 가 실재 하도록 fix.

**Meaning.** Neural network training (Step 4+) 의 loss 접점. 이후 어떤 model (E1-E4, teacher, student) 을 붙여도 loss 는 여기 서 import. Baseline B1 (closed-form ridge) 은 loss function 을 직접 안 쓰지만 같은 metric 으로 비교. 다음 사이클 = `evaluation/metrics.py` (per-clip Pearson + Spearman headline).

---

## 2026-07-03. Cycle 5. CaptionMap + Dataset 연결 (Step 1 완성)

**What.** MindCaptioning 스타일 human caption (`caption_ck20.csv`, 43920 row = 2196 stim × 20 rater) 을 stim_num → caption string 으로 매핑 하는 `CaptionMap` class. Rater 정책 = 옵션 3 (train 은 epoch 별 random, val/test 는 stim 별 fixed seed). `HorikawaDataset` 에 `caption_mode="human"` 파라미터 로 연결.

**결정.** Rater 정책 = 옵션 3 (deterministic random). 근거. 옵션 2 (train random, eval rater=0) 는 data leakage 는 아니지만 evaluation bias (rater 0 특성 에 종속). 옵션 3 은 eval 도 20 rater 를 balanced 하게 사용 하되 fixed seed 로 재현 성 유지.

**Files.**
- `project/data/caption_map.py` (`CaptionMap`, `_rater_idx`)
- `project/data/datasets.py` (수정. `caption_mode` + `set_epoch()` 추가)
- `project/scripts/datasets_smoke.py` (수정. Caption sanity 추가)

**Mapping 검증.**
- 우리 `stim_num_int` = Cowen 원본 filename (`0001.mp4`..`2185.mp4`).
- Human `video_id` 도 Cowen 원본 순서 (1-based). 매핑 = **stim_num == video_id** 확정.
- Qwen-VL caption 은 sample 검증 결과 stim 마다 부정확 하게 다른 자극 을 서술 하는 경우 발견 (예. stim 457 인 gun 자극 을 seashells 로 서술). Qwen 자체 부정확 (매핑 은 정상). `captions.json` 은 지금 skip, 별도 사이클 에서 재검증 or 재생성 후 사용.

**Sanity.**
- Coverage. 2196 stim 모두 정확 히 20 rater. 우리 canonical 2185 stim 을 모두 커버.
- Sample 에 `caption` 필드 attach. Non-empty string.
- Train deterministic within epoch. 같은 (stim_num, epoch) → 같은 rater_idx.
- Train cross-epoch variation. Train[0] 을 epoch {0,1,2} 에서 호출 → 3 distinct captions ("A woman walking on catwalk falls" / "A model slips and falls on runway" / "A woman walks on catwalk but slips"). 20 rater 를 augmentation 으로 활용.
- Val / test epoch-invariant. `set_epoch(99)` 무시. Val[0] 은 항상 같은 rater.

**Meaning.** Step 1 data 모듈 완성. 앞으로 teacher (Step 6) 가 caption 을 input 으로 씀. 지금 Baseline B1 (LLM 없는 ridge) 은 caption 안 씀. Trainer 는 `dataset.set_epoch(epoch)` 를 epoch 시작 마다 호출 해야 rater rotation 이 정상 작동. Qwen-VL caption 재생성 / 재검증 은 별도 사이클 (Step 6 진입 전).

---

## 2026-07-03. Cycle 4. FmriAdapter + Dataset 연결 (Step 1 마무리 앞 사이클)

**What.** Cycle 3 에서 만든 `roi_timeseries/sub-XX.pt` 를 memory 에 load 하는 얇은 `FmriAdapter` class. `HorikawaDataset` 이 이 adapter 를 참조 하여 placeholder zeros 를 실제 fMRI 로 교체. 두 mode 지원. `mean` = `(450,)`, `timeseries` = `(T_max=47, 450)` + `(T_max,)` bool mask + `original_T`.

**Files.**
- `project/data/fmri_adapter.py` (`FmriAdapter` class)
- `project/data/datasets.py` (수정. `fmri_mode` 파라미터 추가, adapter 호출)
- `project/scripts/datasets_smoke.py` (전체 재작성. Real fmri sanity + 두 mode 검증 + padding-invariance)

**Sanity.**
- Split 개수 유지. train 8740, val 1085, test 1100.
- Mean mode. sample fmri shape `(450,)`. Zeros 아님, range `[-0.311, +0.754]` (실제 BOLD).
- Cross-subject 검증. 같은 stim (stim 3) 에서 5 subject 의 fMRI std (ROI 평균) `+0.1795`. Label 은 identical (subject-invariant) 이지만 fMRI 는 subject 별 다름. Pool 방식 실증.
- Timeseries mode. sample fmri shape `(47, 450)`, mask shape `(47,)` bool, `original_T=8` (stim 3 의 실제 T). Padding zone `[T=8..46]` 이 exact zero.
- Padding-invariance under mask. Padding 자리 를 scale-1e3 random noise 로 바꾸고 masked mean 을 재계산 해도 원본 과 max abs diff `0.00e+00` (bit-for-bit identical). Mask 가 padding 을 완벽 히 차단.

**Meaning.** Step 1 data 모듈 의 마지막 core 파일. 이 사이클 후 부터 baseline / model 이 즉시 `HorikawaDataset` 을 사용 가능. Sample 구조 는 앞으로 모든 encoder / model 이 받는 계약. 다음 사이클 (caption_map) 은 Baseline B1 에는 필요 없지만 data 모듈 완성 을 위해.

---

## 2026-07-03. Cycle 3. ROI time-series build (Step 1 지속)

**What.** Raw ROI CSV (Schaefer 400 + Tian 50) 를 subject 별 통합 pt 로 변환. Right-padded T_max=47 + mask + metadata. Baseline / E1 / E2 (roi_mean) 과 E3 BFM (roi_timeseries + mask) 이 공유 할 fMRI 원본 form.

**Files.**
- `project/scripts/build_roi_timeseries.py`
- `project/scripts/build_roi_timeseries.sh`

**Output.**
- `project/shared/data/roi_timeseries/sub-{01..05}.pt` (5 파일, 각 184 MB, 합 920 MB)
- Per pt. `roi_timeseries (2185, 47, 450)` + `roi_mean (2185, 450)` + `mask (2185, 47)` + `original_T` + `stim_num` + `T_max=47` + `n_roi=450` + `missing_stim`

**Sanity.**
- Missing 0 stim / subject. Canonical 2185 완벽.
- Valid ratio 12.9 % (T_max=47, median T=5 이라 storage 87 % zero padding).
- Regenerated `roi_mean` vs 기존 reference `roi_schaefer400tian50_mean/sub-XX.pt` embeddings. Max abs diff `~10⁻⁷`, mean abs diff `~10⁻⁹` (float32 precision 한계). 우리 pipeline 이 기존 mean 을 numerically 재생성 함.
- Padding-invariance. Padding 자리 를 scale-1e3 random noise 로 대체 해도 mask 적용 mean 이 원본 과 identical (max abs diff `~10⁻⁷`). Padding zero 가 downstream 에 leak 안 됨 검증.

**Meaning.** Baseline B1 이 이 pt 의 roi_mean 을 받아 34D 예측 예정. "엄격 controlled baseline" 원칙 (baseline 과 우리 model 이 동일 source, 동일 preprocess) 이 여기 서 성립. Bit-for-bit 재생성 이 아닌 float32 tolerance 안 identical 이라 실질 결과 identical. Padding 정책 (right-pad + mask + 3 규칙) 은 앞으로 encoder / model 이 반드시 강제.

---

## 2026-07-03. Cycle 2. HorikawaDataset pool 로더 (Step 1 지속)

**What.** PyTorch `Dataset` 하나. Pool 5-subject × 2185-stim 을 (subject, stim) 개별 sample 로 batch 접근. 지금 은 fMRI 필드 를 zeros placeholder 로 두고 label + metadata 만 실제 값.

**Files.**
- `project/data/datasets.py` (`HorikawaDataset`)
- `project/scripts/datasets_smoke.py`, `.sh`

**Sanity.**
- Split sample 수 정확. train 8740 (5 subj × 1748 stim), val 1085 (5 × 217), test 1100 (5 × 220). 합 10925.
- 같은 stim 에서 5 subject 의 label 이 identical (subject-invariant label). Pool 방식 검증.
- Sample dict = `{subject_id, stim_idx, stim_num, label (34,), fmri (16, 450) placeholder}`.
- Z-scored label 전체 range [-0.881, +20.353], mean ~ 0, std 1. Long-tail 은 원 데이터 가 대부분 0 fraction 이라 정상.

**Meaning.** 앞으로 baseline / model 이 다 이 dataset 을 `DataLoader` 로 감싸 학습. 데이터 로딩 접점 하나 로 통일. fMRI 는 다음 사이클 (fmri_adapter) 에서 실제 값 으로 교체 예정.

---

## 2026-07-02. Cycle 1. Cowen 34D label z-score preprocessing (Step 1 시작)

**What.** 34D emotion rating 을 train-fit z-score 로 rescale 하는 `Cowen34Normalizer` class. Sklearn `StandardScaler` 관례 (fit / transform / save / load) 를 torch native 로 구현. 실제 로 train 통계 fit + mu / std pt 저장.

**Files.**
- `project/data/labels.py` (`Cowen34Normalizer` class)
- `project/scripts/labels_fit.py`, `.sh`

**Data prep.**
- `project/shared/data/cowen_horikawa_labels.csv` 를 symlink 에서 실제 file 로 copy (사용자 규칙, symlink 금지).
- 34D score 는 0-1 fraction (rater agreement). Row sum mean 1.71 → distribution 아님, 독립 score 형태.
- V/A 는 1-9 Likert (별도).

**Output.**
- `project/shared/data/norm_stats/cowen34_train.pt` (mu 34D + std 34D + emotion_dim=34).

**Sanity.**
- Train unique stimuli 1748, val 217, test 220 (총 2185).
- Post-transform train mean range `[-1.24e-7, +1.01e-7]` (거의 0), std range `[+1.0000, +1.0000]` (거의 1).
- CAUTION 준수. Train 만 fit, val/test 는 이후 transform 만.

**Meaning.** 앞으로 모든 loss / metric / model 은 이 z-score 공간 에서 동작. 표시 용 raw scale 은 별도 inverse_transform. 이 파일 이 spec §12 build order 의 첫 진입점.
