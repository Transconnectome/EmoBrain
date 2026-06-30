# Option B — Direct Regression Head (REG variant)

작성 2026-06-28. v1+v2 (token output) 실패 (V Pearson r 0.035 vs Phase 1 ROI ridge baseline 0.416) 회복 plan.
상세 negative result = `docs/reports/d1_brainvlm_va_negative_result_20260628.md`.

## 무엇이 바뀌나

| 항목 | v2 (token output) | REG (this) |
|---|---|---|
| Output path | `<Valence_value>0.72</Valence_value> <Arousal_value>0.41</Arousal_value>` autoregressive 토큰 | 2-layer MLP (`hidden_size -> 256 -> 2`) on pooled hidden state |
| Loss | Causal LM cross-entropy on assistant tokens | MSE(va_pred, va_target) |
| Target source | Tokenized assistant XML string | Collator 가 `metadata.ground_truth.query.va_regression` 에서 직접 파싱 → `(B, 2)` float |
| Eval | `model.generate(...)` + XML 파싱 + Pearson on parsed value | Forward 만 → head output → per-dim Pearson r + MSE 직접 산출 |
| `metric_for_best_model` | `eval_task_0_token_acc` | `eval_task_0_v_pearson` |
| Pool 전략 | n/a | `mean_brain_tokens` (default. query_C trial 의 brain image token 평균). 대안 `last_query_token` |
| Pad side | left (generation 위해) | right (forward 만이라 무관) |
| Vision tower / patch_embed / merger / monkey patch | NoPool 과 동일 | NoPool 과 동일 (변경 없음) |
| Generation 길이 | `max_new_tokens=256` | 해당 없음 (generation 0) |
| Trainable param | merger + patch_embed + (LoRA 옵션) | 동일 + head (`hidden_size×256 + 256×2`) |

## 왜 mean_brain_tokens

- D1 BrainVLM 의 본질 = "query brain signal → emotion code" 회귀.
- `mean_brain_tokens` 는 query trial 의 ROI brain image token 만 평균 (ref_A, ref_B brain 은 제외) → 입력 representation 과 출력 사이 path 가 명시적으로 brain 신호 기반.
- `last_query_token` 은 chat template trigger 의 마지막 보일러플레이트 토큰에 의존 → prompt structure 미세 변화 가 학습 신호 노이즈 가 됨.
- ref_A / ref_B brain token 까지 평균 하면 ICL context (다른 사람 의 brain) 가 query decoding 에 섞여 들어옴. 분리.

`pool` 옵션은 yaml `model.regression_head.pool` 로 toggle. CLI `--head-pool` 도 가능.

## 실행 (NERSC. login = GPU 없음)

```bash
# 1 GPU = A100 80 GB. 예상 4-6 hr.
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/sbatch_Qwen3VL2B_REG.sh
```

salloc + bash (debug):
```bash
salloc -A m4641 -C gpu -q interactive -N 1 --gpus-per-node=1 -t 2:00:00
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL2B_REG.sh
```

## 평가 target

| Task | Phase 1 ROI ridge baseline | REG target | v2 (token output) 실측 |
|---|---|---|---|
| V regression Pearson r | 0.416 | ≥ 0.40 | 0.035 |
| A regression Pearson r | 0.233 | ≥ 0.23 | (n/a, 측정 안 됨) |

`metric_for_best_model = eval_task_0_v_pearson` (higher better).

## 예상 cost

| 단계 | 시간 |
|---|---|
| eval-on-start (1 회) | 2-3 min |
| epoch (~ train 7000 sample / batch 4 = 1750 step) | 25-35 min |
| 총 10 epoch + eval (~ 1100 step 마다) | 4-6 hr |

generation 이 없어 v2 (5-7 hr) 대비 빠름. checkpoint 자동 resume 박혀 있음 (LATEST_CKPT).

## 변경된 파일

| 파일 | 역할 |
|---|---|
| `project/training/main_umbrella_training_qwen_REG.py` | Entry. monkey patch + model wrap + Trainer 구성. |
| `project/training/umbrella_trainer_qwen_REG.py` | `BrainVLMRegressionHead`, `UMBRELLATrainerQwenREG`, `RegressionCollatorWrap`. |
| `project/config/umbrella_Qwen3VL2B_train_Horikawa_Emotion_ROI_VA_regression_REG.yaml` | REG-specific yaml. `regression_head` 블록 + `metric_for_best_model`. |
| `sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL2B_REG.sh` | torchrun launcher. |
| `sample_scripts/sbatch_Qwen3VL2B_REG.sh` | NERSC sbatch wrapper (m4641, gpu, 12 hr). |

NoPool 버전 (main/trainer/yaml/sh) 은 **그대로 보존**. 새 파일은 alongside.

## 데이터

- JSONL = 기존 `sample_data/Horikawa_Emotion_va_regression_icl_3subj_3stim/{train,validation,test}.jsonl` 그대로 사용. **재생성 X**.
- target 파싱 = collator (`RegressionCollatorWrap`) 가 `metadata.ground_truth.query.va_regression.{valence_value,arousal_value}` 에서 직접 (B,2) float 으로 변환. assistant message XML 토큰화/디코딩 우회.

## binary 변형 (선택)

이 README 작성 시점에선 별도 binary main / yaml 미작성. `RegressionCollatorWrap(binary=True)` + `--binary-mode` CLI 플래그 + BCE loss 로 확장 가능. 작업 끝의 summary 참조.

## v2 와 동시 비교 가능

같은 train/eval JSONL → REG 와 v2 의 V/A pearson 을 직접 비교. 두 outputdir 의 wandb run 을 같은 project 에 띄우고 step-별 metric overlay.
