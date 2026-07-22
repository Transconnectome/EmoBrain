# EmoBrain

EmoBrain studies fine-grained emotion decoding from short-window, low-data
task-fMRI using pretrained brain and vision representations.

The canonical system uses `Qwen/Qwen3-VL-4B-Instruct` with two swappable brain
encoder families:

- **E1 ViT:** an image-pretrained ViT adapted to an fMRI ROI grid.
- **E2 BFM:** Brain-JEPA or SwiFT pretrained brain representations.

It predicts 34 independent emotion scores. A multimodal teacher receives brain,
V-JEPA2 video, and human-written MindCaptioning descriptions; a brain-only
student learns from both hard labels and cached teacher outputs. The scientific
scope includes transfer under short temporal windows and limited task-fMRI,
contextual supervision, future cross-dataset generalization, and cortical
interpretability.

The only supported implementation is `project/code/`. The earlier Qwen2.5
pipeline is preserved under `project/legacy/qwen25/` for provenance and must not
be used for new experiments.

See [README_KR.md](README_KR.md) and
[`docs/notes/implementation_spec_20260702.md`](docs/notes/implementation_spec_20260702.md).
