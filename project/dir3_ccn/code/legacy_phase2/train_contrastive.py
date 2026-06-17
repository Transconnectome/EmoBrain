"""
Phase 2 Architecture C — Stage 1: train brain<->video contrastive alignment (CLIP-style).

InfoNCE loss on (brain, video) pairs per stimulus. Same 5-fold split as Phase 1.
For each fold, train on train+val (with val for HP/epoch selection), save the aligned
projection heads as a .pt for downstream probing.

Output: results/phase2/C/aligner_fold<K>_seed<S>.pt
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/project/dir2_multimodal/code/legacy_phase2")
sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/project/dir2_multimodal/code/legacy_phase2/architectures")

from _lib import (load_brain_embeddings, load_video_feature, get_fold_split,
                  fit_standardizer, apply_standardizer,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO,
                  ALL_SUBJECTS)
from arch_C_contrastive import ContrastiveAligner

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
OUT_DIR = FEELIN / "project/shared/results/phase2/C"


def build_pairs(brain_dict, video_feat, vstim, stim_set):
    """For each stim in stim_set, for each subject, make (brain, video) pair.
    Returns brain (N, D_b), video (N, D_v)."""
    stim_to_video = {int(s): i for i, s in enumerate(vstim)}
    bs, vs = [], []
    for subj, (emb, stim_arr) in brain_dict.items():
        s2b = {int(s): i for i, s in enumerate(stim_arr)}
        for stim in stim_set:
            if stim not in s2b or stim not in stim_to_video:
                continue
            bs.append(emb[s2b[stim]])
            vs.append(video_feat[stim_to_video[stim]])
    return np.stack(bs, axis=0), np.stack(vs, axis=0)


def train_one_fold(brain, video, vstim, split, seed, device,
                   d_model=256, temperature=0.07, lr=1e-3, batch_size=256,
                   epochs=80, patience=10, weight_decay=1e-4):
    train_stim = split[split["split"] == "train"]["stimulus_num"].tolist()
    val_stim = split[split["split"] == "val"]["stimulus_num"].tolist()

    b_tr, v_tr = build_pairs(brain, video, vstim, train_stim)
    b_va, v_va = build_pairs(brain, video, vstim, val_stim)

    # Standardize on train
    b_mu, b_std = fit_standardizer(b_tr)
    v_mu, v_std = fit_standardizer(v_tr)
    b_tr = apply_standardizer(b_tr, b_mu, b_std)
    v_tr = apply_standardizer(v_tr, v_mu, v_std)
    b_va = apply_standardizer(b_va, b_mu, b_std)
    v_va = apply_standardizer(v_va, v_mu, v_std)

    torch.manual_seed(seed)
    np.random.seed(seed)

    model = ContrastiveAligner(brain_dim=b_tr.shape[1], video_dim=v_tr.shape[1],
                               d_model=d_model, temperature=temperature).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    tr_ds = TensorDataset(torch.from_numpy(b_tr), torch.from_numpy(v_tr))
    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True, drop_last=True)

    best_val, best_state, since = np.inf, None, 0
    for epoch in range(epochs):
        model.train()
        for bb, vv in tr_loader:
            bb, vv = bb.to(device), vv.to(device)
            opt.zero_grad()
            loss = model(bb, vv)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            v_loss = model(torch.from_numpy(b_va).to(device),
                           torch.from_numpy(v_va).to(device)).item()
        if v_loss < best_val:
            best_val = v_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            since = 0
        else:
            since += 1
            if since >= patience:
                break

    return best_state, best_val, (b_mu, b_std, v_mu, v_std)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain_model", default=DEFAULT_BRAIN)
    ap.add_argument("--brain_init", default=DEFAULT_BRAIN_INIT)
    ap.add_argument("--brain_padding", default=DEFAULT_BRAIN_PAD)
    ap.add_argument("--video", default=DEFAULT_VIDEO)
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--out_dir", default=str(OUT_DIR))
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    folds = [int(f) for f in args.folds.split(",")]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"=== Phase 2 C: Contrastive alignment ===")
    print(f"  brain={args.brain_model}/{args.brain_init}/{args.brain_padding} video={args.video}")
    print(f"  seeds={seeds} folds={folds} device={device}")

    t0 = time.time()
    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    video, vstim = load_video_feature(args.video)
    print(f"  load t={time.time()-t0:.1f}s")

    for fold in folds:
        split = get_fold_split(fold)
        for seed in seeds:
            t1 = time.time()
            state, val_loss, stdz = train_one_fold(brain, video, vstim, split, seed, device)
            elapsed = time.time() - t1
            out_pt = out_dir / f"aligner_fold{fold}_seed{seed}.pt"
            torch.save({
                "state_dict": state,
                "val_loss": val_loss,
                "standardizer": stdz,
                "brain_model": args.brain_model, "brain_init": args.brain_init,
                "brain_padding": args.brain_padding, "video": args.video,
                "fold": fold, "seed": seed,
            }, out_pt)
            print(f"  fold={fold} seed={seed} val_loss={val_loss:.3f} t={elapsed:.1f}s → {out_pt.name}")

    print(f"\n[done]")


if __name__ == "__main__":
    main()
