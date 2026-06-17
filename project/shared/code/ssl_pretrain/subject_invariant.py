"""
FEEL Phase 3b Track A. Subject-invariant SSL pretrain.

Goal. Universal emotion code 의 sub-claim 3 (subject-invariant alignment) 의 direct
evidence. 같은 stimulus 를 본 5 subject 의 brain representation 이 서로 비슷한 latent
로 mapping 되도록 contrastive 학습.

Setup.
- Backbone. BFM frozen embedding (default Brain-JEPA resting pad-mean).
- Projection head. Linear (default, Phase 1 finding) 또는 MLP (ablation).
- Loss. InfoNCE.
    positive = (stim k, subj A brain) ↔ (stim k, subj B brain)
    negative = (stim k, subj A) ↔ (stim m, subj_any) (m ≠ k)
- 학습 후 출력 = projection head checkpoint + 학습 후 z 의 subject alignment metric.

Honest scope. Backbone frozen. Projection head 만 학습 (~수만 parameter, 5 subj data 에
overfitting 안전). Optional LoRA on backbone 은 다음 step.

Usage.
    python subject_invariant.py --head linear --epochs 100
    python subject_invariant.py --head mlp --epochs 100 --temperature 0.05
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

FEEL = Path("/pscratch/sd/s/sjmoon/EmoBrain")
EMB_ROOT = FEEL / "output/embeddings"
DATA = FEEL / "data"
OUT_ROOT = FEEL / "output/ssl_pretrain"
RES_ROOT = FEEL / "results/phase3_universal_code/track_a"

ALL_SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]


# ============================================================
# Data loading
# ============================================================

def load_bfm_embeddings(bfm_dir: str):
    """Load BFM frozen embeddings for all 5 subjects.

    Returns dict[subject] = (embeddings tensor [N_stim, D], stim_num tensor [N_stim]).
    """
    out = {}
    for subj in ALL_SUBJECTS:
        fp = EMB_ROOT / bfm_dir / f"{subj}.pt"
        if not fp.exists():
            raise FileNotFoundError(f"Missing BFM embedding: {fp}")
        d = torch.load(fp, map_location="cpu", weights_only=False)
        emb = d["embeddings"].float()  # [N, D]
        stim_num = d["stim_num"].long()  # [N]
        out[subj] = (emb, stim_num)
    return out


def load_fold_split(fold_csv: str):
    """5-fold stim-stratified split. Returns dict[stimulus_num] = fold_id (1-5)."""
    df = pd.read_csv(fold_csv)
    return dict(zip(df["stimulus_num"], df["fold"]))


# ============================================================
# Dataset
# ============================================================

class SubjectPairDataset(Dataset):
    """For each stimulus k, enumerate all unordered (A, B) subject pairs.

    Each item = (stim_k, brain_Ak, brain_Bk).
    Negatives are drawn at batch time (all other stims/subjects in batch).
    """

    def __init__(self, brain_dict: dict, stim_ids: list[int]):
        self.subjects = list(brain_dict.keys())
        self.brain_dict = brain_dict
        self.stim_ids = list(stim_ids)

        # Build (subj, stim) → embedding row index for fast lookup.
        self.s2idx = {}
        for subj, (emb, stim) in brain_dict.items():
            for i, s in enumerate(stim.tolist()):
                self.s2idx[(subj, int(s))] = i

        # Build all (stim, subjA, subjB) pairs, A < B.
        pairs = []
        for stim in self.stim_ids:
            present = [s for s in self.subjects if (s, stim) in self.s2idx]
            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    pairs.append((stim, present[i], present[j]))
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        stim, subjA, subjB = self.pairs[idx]
        embA = self.brain_dict[subjA][0][self.s2idx[(subjA, stim)]]
        embB = self.brain_dict[subjB][0][self.s2idx[(subjB, stim)]]
        return {
            "stim": stim,
            "brain_A": embA,
            "brain_B": embB,
        }


# ============================================================
# Model
# ============================================================

class LinearHead(nn.Module):
    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.fc = nn.Linear(in_dim, out_dim)

    def forward(self, x):
        return self.fc(x)


class MLPHead(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, hidden: int = 512, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)


def build_head(kind: str, in_dim: int, out_dim: int):
    if kind == "linear":
        return LinearHead(in_dim, out_dim)
    if kind == "mlp":
        return MLPHead(in_dim, out_dim)
    raise ValueError(f"Unknown head: {kind}")


# ============================================================
# InfoNCE loss (symmetric, 2 view contrastive)
# ============================================================

def info_nce_symmetric(zA: torch.Tensor, zB: torch.Tensor, temperature: float = 0.07):
    """Symmetric InfoNCE between two views (zA, zB), L2-normalized.

    Each row i of zA / zB is a paired view of the same stimulus. Negatives = all
    other rows in the batch. Returns scalar loss.
    """
    zA = F.normalize(zA, dim=-1)
    zB = F.normalize(zB, dim=-1)
    logits_AB = zA @ zB.T / temperature  # [B, B]. logits_AB[i, j] = sim(A_i, B_j)
    logits_BA = zB @ zA.T / temperature

    B = zA.shape[0]
    target = torch.arange(B, device=zA.device)
    loss = (F.cross_entropy(logits_AB, target) + F.cross_entropy(logits_BA, target)) / 2.0
    return loss, logits_AB


# ============================================================
# Evaluation. Subject alignment metric
# ============================================================

@torch.no_grad()
def compute_subject_alignment(model, brain_dict, stim_ids, device, batch_size=256):
    """For held-out stims, compute mean cosine similarity between same-stim
    representations across all subject pairs vs random-stim representations.

    Returns dict with:
      - mean_pos_cos: mean cos(z_Ak, z_Bk) for k in stim_ids, all subj pairs
      - mean_neg_cos: mean cos(z_Ak, z_Bm) for k != m, all subj pairs (random pairs)
      - alignment_gap: pos - neg (larger = more subject-invariant)
    """
    model.eval()
    # Compute all z per subject for stim_ids.
    subj_z = {}
    for subj, (emb, stim_arr) in brain_dict.items():
        s2i = {int(s): i for i, s in enumerate(stim_arr.tolist())}
        rows = [s2i[s] for s in stim_ids if s in s2i]
        x = emb[rows].to(device)
        z = F.normalize(model(x), dim=-1).cpu()
        subj_z[subj] = z

    subjects = list(subj_z.keys())
    n_stim = len(stim_ids)

    # Positive. Same stim, different subjects.
    pos_cos = []
    for i in range(len(subjects)):
        for j in range(i + 1, len(subjects)):
            zA = subj_z[subjects[i]]
            zB = subj_z[subjects[j]]
            cos = (zA * zB).sum(-1)  # [n_stim]
            pos_cos.append(cos)
    pos_cos = torch.cat(pos_cos)
    mean_pos = pos_cos.mean().item()

    # Negative. Different stim, all subject pairs (random shuffle).
    perm = torch.randperm(n_stim)
    neg_cos = []
    for i in range(len(subjects)):
        for j in range(i + 1, len(subjects)):
            zA = subj_z[subjects[i]]
            zB = subj_z[subjects[j]][perm]
            cos = (zA * zB).sum(-1)
            neg_cos.append(cos)
    neg_cos = torch.cat(neg_cos)
    mean_neg = neg_cos.mean().item()

    return {
        "mean_pos_cos": mean_pos,
        "mean_neg_cos": mean_neg,
        "alignment_gap": mean_pos - mean_neg,
        "n_pos": len(pos_cos),
        "n_neg": len(neg_cos),
    }


# ============================================================
# Training
# ============================================================

def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"BFM: {args.bfm}")
    print(f"Head: {args.head}")
    print(f"Temperature: {args.temperature}")
    print(f"Output dim: {args.out_dim}")
    print()

    # Set seed.
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    # Load BFM embeddings (frozen).
    brain_dict = load_bfm_embeddings(args.bfm)
    in_dim = brain_dict[ALL_SUBJECTS[0]][0].shape[1]
    print(f"BFM embedding dim: {in_dim}")

    # Load fold split.
    fold_map = load_fold_split(str(DATA / "horikawa_5fold.csv"))
    test_fold = args.fold
    val_fold = (args.fold % 5) + 1

    test_stims = [s for s, f in fold_map.items() if f == test_fold]
    val_stims = [s for s, f in fold_map.items() if f == val_fold]
    train_stims = [s for s, f in fold_map.items() if f not in (test_fold, val_fold)]
    print(f"Train stims: {len(train_stims)}, val: {len(val_stims)}, test: {len(test_stims)}")

    # Build datasets.
    train_ds = SubjectPairDataset(brain_dict, train_stims)
    print(f"Train pairs (stim × subj_pair): {len(train_ds)}")
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=2, drop_last=True)

    # Model.
    head = build_head(args.head, in_dim, args.out_dim).to(device)
    n_params = sum(p.numel() for p in head.parameters() if p.requires_grad)
    print(f"Head: {args.head}, trainable params: {n_params:,}")

    # Optimizer.
    optim = torch.optim.AdamW(head.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optim, T_max=args.epochs)

    # Output dirs.
    tag = f"{args.bfm}_head-{args.head}_dim-{args.out_dim}_tau-{args.temperature}_fold{args.fold}_seed{args.seed}"
    ckpt_dir = OUT_ROOT / tag
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # Baseline (pre-training) alignment.
    print("\n--- Pre-training (random projection) baseline ---")
    pre = compute_subject_alignment(head, brain_dict, val_stims, device)
    print(f"  Val pos cos: {pre['mean_pos_cos']:.4f}")
    print(f"  Val neg cos: {pre['mean_neg_cos']:.4f}")
    print(f"  Val alignment gap: {pre['alignment_gap']:.4f}")

    # Training loop.
    history = []
    best_gap = -float("inf")

    print("\n--- Training ---")
    for epoch in range(1, args.epochs + 1):
        head.train()
        epoch_loss = 0.0
        n_batches = 0
        t0 = time.time()
        for batch in train_loader:
            brainA = batch["brain_A"].to(device, non_blocking=True)
            brainB = batch["brain_B"].to(device, non_blocking=True)
            zA = head(brainA)
            zB = head(brainB)
            loss, _ = info_nce_symmetric(zA, zB, temperature=args.temperature)

            optim.zero_grad()
            loss.backward()
            optim.step()
            epoch_loss += loss.item()
            n_batches += 1
        scheduler.step()

        avg_loss = epoch_loss / max(1, n_batches)
        elapsed = time.time() - t0

        if epoch == 1 or epoch % args.eval_every == 0 or epoch == args.epochs:
            metrics = compute_subject_alignment(head, brain_dict, val_stims, device)
            print(f"Epoch {epoch:3d}/{args.epochs}  loss {avg_loss:.4f}  "
                  f"val pos {metrics['mean_pos_cos']:.4f}  neg {metrics['mean_neg_cos']:.4f}  "
                  f"gap {metrics['alignment_gap']:.4f}  ({elapsed:.1f}s)")
            history.append({
                "epoch": epoch,
                "loss": avg_loss,
                **{f"val_{k}": v for k, v in metrics.items()},
            })

            if metrics["alignment_gap"] > best_gap:
                best_gap = metrics["alignment_gap"]
                torch.save({
                    "head_state": head.state_dict(),
                    "epoch": epoch,
                    "val_metrics": metrics,
                    "args": vars(args),
                }, ckpt_dir / "best.pt")
        else:
            print(f"Epoch {epoch:3d}/{args.epochs}  loss {avg_loss:.4f}  ({elapsed:.1f}s)")

    # Final test eval.
    print("\n--- Final test eval (best ckpt) ---")
    best_state = torch.load(ckpt_dir / "best.pt", map_location=device, weights_only=False)
    head.load_state_dict(best_state["head_state"])
    test_metrics = compute_subject_alignment(head, brain_dict, test_stims, device)
    print(f"  Test pos cos: {test_metrics['mean_pos_cos']:.4f}")
    print(f"  Test neg cos: {test_metrics['mean_neg_cos']:.4f}")
    print(f"  Test alignment gap: {test_metrics['alignment_gap']:.4f}")

    # Save history + final.
    pd.DataFrame(history).to_csv(ckpt_dir / "history.csv", index=False)
    summary = {
        "args": vars(args),
        "tag": tag,
        "n_train_pairs": len(train_ds),
        "head_params": n_params,
        "pre_train_alignment": pre,
        "best_val_alignment_gap": best_gap,
        "test_alignment": test_metrics,
        "best_epoch": best_state["epoch"],
    }
    with open(ckpt_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Also append to results/phase3_universal_code/track_a/subject_alignment.csv.
    RES_ROOT.mkdir(parents=True, exist_ok=True)
    out_csv = RES_ROOT / "subject_alignment.csv"
    row = {
        "tag": tag,
        "bfm": args.bfm,
        "head": args.head,
        "out_dim": args.out_dim,
        "temperature": args.temperature,
        "fold": args.fold,
        "seed": args.seed,
        "n_train_pairs": len(train_ds),
        "head_params": n_params,
        "epochs": args.epochs,
        "pre_pos_cos": pre["mean_pos_cos"],
        "pre_neg_cos": pre["mean_neg_cos"],
        "pre_gap": pre["alignment_gap"],
        "val_best_gap": best_gap,
        "test_pos_cos": test_metrics["mean_pos_cos"],
        "test_neg_cos": test_metrics["mean_neg_cos"],
        "test_gap": test_metrics["alignment_gap"],
        "best_epoch": best_state["epoch"],
    }
    df_row = pd.DataFrame([row])
    if out_csv.exists():
        df_old = pd.read_csv(out_csv)
        df_row = pd.concat([df_old, df_row], ignore_index=True)
    df_row.to_csv(out_csv, index=False)

    print(f"\nSaved to {ckpt_dir}")
    print(f"Aggregate CSV: {out_csv}")
    return summary


# ============================================================
# CLI
# ============================================================

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bfm", default="brain_jepa_resting_pad-mean",
                   help="BFM embedding folder name under output/embeddings/")
    p.add_argument("--head", default="linear", choices=["linear", "mlp"],
                   help="Projection head type (Phase 1 finding: linear default)")
    p.add_argument("--out_dim", type=int, default=256,
                   help="Output projection dim")
    p.add_argument("--temperature", type=float, default=0.07)
    p.add_argument("--batch_size", type=int, default=256)
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--weight_decay", type=float, default=0.05)
    p.add_argument("--fold", type=int, default=1, choices=[1, 2, 3, 4, 5])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--eval_every", type=int, default=5)
    args = p.parse_args()

    train(args)


if __name__ == "__main__":
    main()
