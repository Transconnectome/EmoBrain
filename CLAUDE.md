# EmoBrain Canonical Rules

## Scope

- Canonical code: `project/code/`
- Canonical backbone: `Qwen/Qwen3-VL-4B-Instruct`
- Canonical encoders: E1 ViT and E2 BFM only
- E2 variants: corrected Brain-JEPA and matched-length SwiFT
- Output: 34 independent `log1p_z` emotion scores; no softmax across emotions
- Full GPU jobs are run by the user. Provide a single absolute `bash ...sh` command.

## Prohibited Paths

- Do not add a task-supervised target-space encoder.
- Do not add a raw+BFM dual branch as the main architecture.
- Do not use `project/legacy/qwen25/` for new experiments.
- Do not present legacy output JSON files as Qwen3-VL-4B results.
- Do not modify CCN when working on the main EmoBrain framework.

## Brain-JEPA

Use `brain_jepa_pretrained_native_mean`, imported from the validated native
one-patch condition with:

```bash
bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/import_corrected_brain_jepa.sh
```

Describe it as short-window transfer. The 16-TR patch size is native, but the
input has one temporal patch and does not support claims about native long-range
Brain-JEPA dynamics.

## Training Order

1. E1 ViT direct brain-only student.
2. E2 Brain-JEPA and SwiFT direct brain-only students.
3. Best defensible E2 teacher with brain + V-JEPA2 + human caption.
4. Cache teacher 34D outputs for train/val.
5. Train the same E2 brain-only student with hard + distillation MSE.
6. Student-side ablations and neuroscientific analyses follow after the core run.

Always select checkpoints on val and report the untouched stimulus-held-out test.
