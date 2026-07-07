"""Sanity check for supervised and structure losses.

Verifies.
    supervised.
        - pred == target -> loss 0.
        - random pred -> positive scalar.
        - shape assert on wrong dim.
        - curriculum active mask zeroes non-active emotions.
        - per-emotion weight scales contribution.
        - z-space scale sanity (1 std off per emotion -> loss ~ 34).
    structure.
        - pred == target -> loss ~ 0.
        - inverted structure -> large loss.
        - tiny batch rejected.

Run.
    bash project/scripts/losses_smoke.sh
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
from project.models.losses.supervised import supervised_loss, C  # noqa: E402
from project.models.losses.structure import structure_loss  # noqa: E402


def check_supervised() -> None:
    print("[supervised]")
    torch.manual_seed(0)
    B = 16
    target = torch.randn(B, C)

    # pred == target -> 0
    loss0 = supervised_loss(target.clone(), target)
    print(f"  pred==target       loss = {loss0.item():.3e}")
    assert loss0.item() < 1e-10

    # random pred -> positive
    pred = torch.randn(B, C)
    loss1 = supervised_loss(pred, target)
    print(f"  random pred        loss = {loss1.item():.3f}")
    assert loss1.item() > 0

    # z-space scale: exactly 1 std off per emotion -> per-sample sum = 34
    off = target + 1.0
    loss2 = supervised_loss(off, target)
    print(f"  +1.0 per emotion   loss = {loss2.item():.3f}  (expect ~ {C})")
    assert abs(loss2.item() - C) < 1e-4

    # curriculum active mask: top-1 only (one emotion per sample)
    active = torch.zeros(B, C)
    active[:, 0] = 1.0  # only emotion 0 counts
    loss_full = supervised_loss(off, target)
    loss_top1 = supervised_loss(off, target, active=active)
    print(f"  active top-1       loss = {loss_top1.item():.3f}  (expect ~ 1.0)")
    assert abs(loss_top1.item() - 1.0) < 1e-4

    # per-emotion weight scales
    w = torch.ones(C)
    w[0] = 2.0
    loss_w = supervised_loss(off, target, per_emotion_weight=w)
    print(f"  weight emo0 x2     loss = {loss_w.item():.3f}  (expect ~ {C + 1})")
    assert abs(loss_w.item() - (C + 1)) < 1e-4

    # shape assert
    try:
        supervised_loss(torch.randn(B, 10), torch.randn(B, 10))
        raise AssertionError("should have rejected wrong emotion dim")
    except AssertionError as e:
        if "expected" in str(e):
            print("  wrong dim rejected: OK")
        else:
            raise


def check_structure() -> None:
    print("")
    print("[structure]")
    torch.manual_seed(0)
    B = 64

    # Build a target with REAL inter-emotion structure: emotions share latent
    # factors so correlations are non-trivial (unlike i.i.d. Gaussian).
    factor = torch.randn(B, 3)               # 3 shared latent factors
    loading = torch.randn(3, C)              # each emotion loads on factors
    target = factor @ loading + 0.1 * torch.randn(B, C)

    # pred == target -> ~0
    loss0 = structure_loss(target.clone(), target)
    print(f"  pred==target       loss = {loss0.item():.3e}")
    assert loss0.item() < 1e-8

    # inverted structure: flip sign of half the emotions -> correlations with
    # the other half flip sign, so the correlation matrix changes a lot.
    pred = target.clone()
    pred[:, ::2] = -pred[:, ::2]
    loss1 = structure_loss(pred, target)
    print(f"  inverted structure loss = {loss1.item():.3f}  (expect large)")
    assert loss1.item() > loss0.item() + 0.1

    # sanity: same value scale but shuffled structure should differ from 0
    print(f"  structure sensitivity confirmed (delta = {loss1.item() - loss0.item():.3f})")

    # tiny batch rejected
    try:
        structure_loss(torch.randn(2, C), torch.randn(2, C))
        raise AssertionError("should have rejected tiny batch")
    except AssertionError as e:
        if "batch >=" in str(e):
            print("  tiny batch rejected: OK")
        else:
            raise


def main() -> None:
    check_supervised()
    check_structure()
    print("")
    print("all checks OK")


if __name__ == "__main__":
    main()
