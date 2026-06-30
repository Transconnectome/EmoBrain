# REG-binary variant (VA binary, Qwen3-VL-2B, direct head)

D1 BrainVLM recovery plan for the **VA binary** classification task. This is the binary sister of the REG (regression) variant. Head module structure is identical (Linear -> GELU -> Dropout -> Linear -> 2). Only the interpretation of the output and the loss change (logit + BCEWithLogitsLoss instead of scalar + MSE).

## Why this exists

The v2 XML-token autoregressive output failed on VA binary (best token_acc 0.597). Backbone size sweep (2B/4B/8B) confirmed the failure was due to the token output formulation, not backbone capacity. The recovery plan is "Option B" — replace the token output with a direct numeric head. The binary path is run **first** (lift to baseline before tackling regression).

## Target baselines (Phase 1 ROI ridge pooled, Schaefer400 + Tian50, time_mean)

| Dim      | Baseline balanced accuracy | Baseline AUROC |
|----------|----------------------------|----------------|
| Valence  | 0.720                      | 0.789          |
| Arousal  | 0.638                      | 0.678          |
| Average  | 0.679                      | 0.734          |

Goal. lift `eval_avg_balacc` to at least 0.680 (matching pooled ridge). Stretch. exceed 0.700.

## Diff vs REG (regression) variant

| Aspect                | REG (regression)                             | REG-binary                                       |
|-----------------------|-----------------------------------------------|--------------------------------------------------|
| Target dtype          | float scalar (V, A)                           | float in {0, 1, NaN} (NaN for Q2/Q3 missing)     |
| Loss                  | MSE(va_pred, va_target)                       | BCEWithLogitsLoss per dim, NaN-masked             |
| Train log metric      | train_v_pearson, train_a_pearson              | train_v_balacc, train_a_balacc                   |
| Eval main metric      | eval_task_0_v_pearson                         | eval_avg_balacc                                  |
| Eval secondary        | eval_v_mae, eval_a_mae, eval_mse              | eval_v_balacc, eval_a_balacc, eval_v_auroc, eval_a_auroc |
| Collator              | RegressionCollatorWrap (binary=False)         | BinaryCollatorWrap (drops both-missing samples)  |
| Trainer class         | UMBRELLATrainerQwenREG                        | UMBRELLATrainerQwenREG_binary                    |
| Entry script          | main_umbrella_training_qwen_REG.py            | main_umbrella_training_qwen_REG_binary.py        |
| Config yaml           | ...VA_regression_REG.yaml                     | ...VA_binary_REG.yaml                            |
| dataset.ROI_fMRI.target | ["va_regression"]                           | ["va_binary"]                                    |

Everything else (monkey patches, LoRA targets, vision tower path, pool strategy, lr 1e-4, batch 4 × accum 16, 10 epochs, bf16, gradient checkpointing) is byte-identical.

## Expected runtime

4 to 6 hours on 1 A100 (NERSC Perlmutter). Same compute profile as REG (regression). No generation pass means the eval loop is roughly 5x faster than the v2 token-output variant.

## Launch

```bash
sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/sbatch_Qwen3VL2B_REG_binary.sh
```

## Files

- Entry. `project/training/main_umbrella_training_qwen_REG_binary.py`
- Trainer. `project/training/umbrella_trainer_qwen_REG_binary.py`
- Config. `project/config/umbrella_Qwen3VL2B_train_Horikawa_Emotion_ROI_VA_binary_REG.yaml`
- Launcher. `sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_binary_Qwen3VL2B_REG.sh`
- Sbatch. `sample_scripts/sbatch_Qwen3VL2B_REG_binary.sh`
- Data. `sample_data/Horikawa_Emotion_va_binary_icl_3subj_3stim/{train,validation}.jsonl`
- Defs. `project/config/datasets/umbrella_Horikawa_Emotion_VA_binary.yaml`

## Notes

- After file creation run `chmod +x` on both `.sh` files.
- `eval_avg_balacc` is the early-stopping metric (higher is better).
- Samples where both V and A categories are 'missing' (Q2/Q3 quartile) are dropped by `BinaryCollatorWrap`. Samples missing only one dim are kept; the missing dim is masked from both loss and metric.
- `pool: mean_brain_tokens` (default) is the principled choice as in REG; `last_query_token` available via `--head-pool` for ablation.
