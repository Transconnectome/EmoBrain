#!/bin/bash
# D2 setup.
# fMRI-LM 본체는 EmoBrain repo 의 submodule 로 등록되어 있다.
#   external/repos/fMRI-LM   ->  https://github.com/yuxiangwei0808/fMRI-LM
#   external/repos/BrainVLM  ->  https://github.com/Transconnectome/BrainVLM
# 협업자는 EmoBrain clone 시 다음 한 줄로 두 submodule 을 가져온다.
#   git clone --recursive git@github.com:Transconnectome/EmoBrain.git
#   또는 clone 후
#   cd EmoBrain && git submodule update --init --recursive
#
# Stage 1/2 checkpoint 는 별도 다운로드.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
EXT_CKPT=${REPO}/external/checkpoints

cd "${REPO}"
git submodule update --init --recursive external/repos/fMRI-LM external/repos/BrainVLM

mkdir -p "${EXT_CKPT}"

cat <<EOF
[setup] submodules ready.
  external/repos/fMRI-LM   $(git -C external/repos/fMRI-LM rev-parse --short HEAD 2>/dev/null || echo "not-yet-init")
  external/repos/BrainVLM  $(git -C external/repos/BrainVLM rev-parse --short HEAD 2>/dev/null || echo "not-yet-init")

[setup] manual step. Stage 1 / 2 checkpoint 다운로드 (필요 시).
  Google Drive folder.
    https://drive.google.com/drive/folders/1vGN12_bCg4CY2d7AodLw163TuP1QKlkG
  타겟 경로.
    ${EXT_CKPT}/fmri_lm_stage12/
EOF
