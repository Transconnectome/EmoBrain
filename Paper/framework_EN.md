# EmoBrain Framework

## Working Title

**EmoBrain: Foundation-Model Transfer for Fine-Grained Emotion Decoding from
Short-Window Task fMRI**

EmoBrain asks what pretrained brain and vision representations transfer to
short-window, low-data task-fMRI, and whether video-semantic context available
during training can improve a brain-only decoder at inference.

The canonical model uses Qwen3-VL-4B and two encoder families: E1 ViT and E2
BFM, with Brain-JEPA and SwiFT as E2 variants. It predicts 34 independent emotion
endorsement scores. A context teacher receives brain, V-JEPA2 video, and
human-written MindCaptioning descriptions; a student receives brain only and is
trained with hard-label and teacher-output MSE.

The MindCaptioning paper describes its captions as crowdsourced detailed visual
descriptions with quality checking, not as affect-neutral annotations. We use
that precise terminology and assess possible affective shortcuts empirically.

The project does not use a raw-plus-BFM dual branch. BFM transfer is evaluated
through independent encoder conditions, pretrained-versus-scratch contrasts,
distillation benefit, short-window sensitivity, and neuroscientific analyses.
Planned extensions include cortical interpretation, visual/semantic controls,
cross-subject transfer, and cross-dataset generalization.
