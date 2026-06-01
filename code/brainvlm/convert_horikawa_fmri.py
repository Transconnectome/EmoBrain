"""
Convert Horikawa per-stimulus frame .pt files into a single 4D tensor per (subject, stim)
in BrainVLM-compatible format.

Input layout:
  /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img/
    sub-XX_stimulus_N/
      frame_0.pt, frame_1.pt, ..., frame_{T-1}.pt    each (74, 91, 81, 1) tensor

Output layout (one .pt per (subject, stim)):
  output/brainvlm_fmri/<padding>/sub-XX/stimulus_N.pt
    tensor shape (1, 1, 96, 96, 96, 20)  ← matches BrainVLM PatchEmbedQwen.fMRI input
    dtype float32

The .pt files are then loaded by a custom Horikawa dataset for BrainVLM training/inference.

Default padding = zero (matches Phase 1 main grid convention).
"""
import argparse
import sys
from pathlib import Path

import torch

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/code/brainvlm")
from _lib import load_horikawa_fmri

FEELIN_ROOT = Path("/pscratch/sd/s/sjmoon/FEELIN")
OUT_ROOT = FEELIN_ROOT / "output/brainvlm_fmri"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", default="sub-01,sub-02,sub-03,sub-04,sub-05",
                    help="comma-separated subjects")
    ap.add_argument("--padding", default="zero",
                    choices=["zero", "mean", "replicate"],
                    help="temporal padding mode (default: zero)")
    ap.add_argument("--T_target", type=int, default=20)
    ap.add_argument("--n_stim", type=int, default=2185,
                    help="number of stimuli (1..n_stim). default 2185 canonical.")
    ap.add_argument("--limit", type=int, default=None,
                    help="if set, only process first N stim (smoke test)")
    args = ap.parse_args()

    subjects = [s.strip() for s in args.subjects.split(",")]
    out_dir = OUT_ROOT / f"pad-{args.padding}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {out_dir}")
    print(f"Subjects: {subjects}")
    print(f"Padding: {args.padding}, T_target: {args.T_target}")

    for subj in subjects:
        subj_out = out_dir / subj
        subj_out.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {subj} ===")
        n_done = 0
        n_skip = 0
        n_miss = 0
        for stim in range(1, args.n_stim + 1):
            if args.limit and stim > args.limit:
                break
            out_pt = subj_out / f"stimulus_{stim}.pt"
            if out_pt.exists():
                n_skip += 1
                continue
            stim_name = f"stimulus_{stim}"
            try:
                y = load_horikawa_fmri(subj, stim_name, T_target=args.T_target,
                                       padding=args.padding)
                # y shape: (1, 1, 96, 96, 96, T_target)
                torch.save(y.contiguous(), str(out_pt))
                n_done += 1
                if stim % 200 == 0:
                    print(f"  ...{stim}/{args.n_stim}")
            except FileNotFoundError:
                n_miss += 1
            except Exception as e:
                print(f"  [WARN] {subj}/{stim_name}: {type(e).__name__}: {e}")
                n_miss += 1
        print(f"  done={n_done} skip={n_skip} miss={n_miss}")


if __name__ == "__main__":
    main()
