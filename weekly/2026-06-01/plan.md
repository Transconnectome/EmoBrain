# Weekly Plan: 2026-06-01

> 월요일 작성. PR description의 "이번 주 계획" 섹션과 동기화.

## 이번 주 목표

Phase 2 brain-only paradigm benchmark 마무리 + BrainVLM 자체 학습 첫 시도 (lab ckpt 안 기다리고 random init 부터 우리 데이터로 supervised training).

## Action Items

- [ ] Phase 2 brain-only 4 method (I/II/III/IV) × 4 task = 16 cell full benchmark. 산출물: `results/phase2/brain_only/<method>/<task>.csv` × 16
- [ ] Phase 2 unified analysis (joint + brain-only + Direction 2 encoding 통합). 산출물: `results/phase2/_benchmark_<task>.{csv,md}`, `figures/phase2/*.png`
- [ ] Phase 2 wrap-up paper draft v0. 산출물: `reports/phase2_wrapup/main.tex` (Phase 1 format 재사용)
- [ ] BrainVLM training loop 작성 (PatchEmbedQwen + Merger trainable, Qwen3-VL frozen). 산출물: `code/brainvlm/train_brainvlm.py` + smoke run log
- [ ] BrainVLM fold 1 smoke training (1 epoch, ~6500 sample) + train loss 검증. 산출물: ckpt + loss curve
- [ ] BrainVLM fold 1 full training (3 epoch) + emotion VQA inference + V/A 평가. 산출물: `results/brainvlm/fold1_*.csv`
- [ ] (시간 여유) Subject-conditioned variability 분석 (Phase 2 trained model 의 5 subj output variance). 산출물: `results/phase2/subject_variability/*.csv`

## 의존성 / 막힐 수 있는 것

- Lab ABCD ckpt 안 와도 진행 (random init 으로 학습)
- BrainVLM GPU 메모리 (Qwen3-VL-2B forward + 학습). smoke 에서 확인 후 batch size 조정
- 5 subj × 2185 stim 의 small N regime 에서 PatchEmbedQwen + Merger 학습이 의미 있는 representation 학습하나의 위험. 결과 보고 LoRA 추가 여부 결정
