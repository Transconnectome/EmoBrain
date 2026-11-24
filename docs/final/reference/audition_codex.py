"""EmoBrain audition, 2026-11-03 specification. Requires Python >=3.10 and PyTorch.

Run: /opt/anaconda3/bin/python audition_codex.py
Import: DecodedFeatureReadout, decoding_loss, interchange_intervention,
        summarize_interventions, make_scene_pair_shuffle,
        apply_shuffled_scene_pairs, shuffled_scene_pair_loss.

Sources in EmoBrain_final_2026-11-03/:
  01_integrated_document.md: F4/F5, G8/G9, D9/N4, O1/O2/O3/O5/O26.
  SHA256 a99c7ac4debe7769cc781b5bf43cdbd0eb4aaa87fd494519ace3e3d6adf35e4b
  04_claude_code_workorder.md: S5/S6/S8; interventions are specified in S9.
  SHA256 36194e6be40441937e3dcb3444fa43c31d916892152575d991f42d04c25178e8

Scope: readout starts at H, AFTER the encoder's final LayerNorm. The encoder,
ROI input layers, standardizer fitting, teacher training, model selection and
bootstrap tests are outside this standalone component. Real feature targets
must already be in the training-derived D9 coordinates; they NEVER enter
forward(). No PCA, no extra MLP, no query self-attention, no feature token
insertion into the emotion queries.

Intervention tensors represent ONE participant / outer fold / seed / checkpoint.
Use summarize_interventions() after collecting all six folds for that participant
and seed; do not average fold-wise correlations. Retain raw pair-wise results for
the separately specified connected-component bootstrap. The 100 control draws
are NOT a null distribution for p-values.

Unspecified degenerate control case: if C-A is zero but B-A is nonzero, this file
raises ValueError instead of inventing a new sampling distribution. Likewise it
does not silently drop undefined correlations or replace them by zero. These
are explicit diagnostics, not additional scientific decisions.
"""

from __future__ import annotations

import hashlib
import math
import random
import unittest
from dataclasses import dataclass
from typing import Mapping, Sequence

import torch
from torch import Tensor, nn
from torch.nn import functional as F


VISUAL_DIM = 5632
CAPTION_DIM = 4096
N_EMOTIONS = 34
CONTROL_REPEATS = 100
PATH_ORDER = ("visual", "caption", "both")


def _tensor(x: Tensor, name: str, shape: tuple[int | None, ...]) -> None:
    if not isinstance(x, Tensor) or not x.is_floating_point():
        raise TypeError(f"{name} must be a floating-point tensor")
    if x.ndim != len(shape) or any(
        size is not None and size != got for size, got in zip(shape, x.shape)
    ):
        raise ValueError(f"{name}: expected {shape}, got {tuple(x.shape)}")
    if x.numel() == 0 or not torch.isfinite(x).all():
        raise ValueError(f"{name} must be nonempty and finite")


def _same_coordinates(*xs: Tensor) -> None:
    if any(x.device != xs[0].device or x.dtype != xs[0].dtype for x in xs):
        raise ValueError("Tensors must share dtype and device (and D9 coordinates)")


def _ratings(y: Tensor, n: int) -> None:
    _tensor(y, "ratings", (n, N_EMOTIONS))
    if ((y < 0) | (y > 1)).any():
        raise ValueError("Ratings must be the original proportions in [0, 1]")


class QueryReadout(nn.Module):
    """F4/F5/O26: q + Dropout(MHA(LN(q), H, H)), then LN; no FFN."""

    def __init__(self, d: int, n_queries: int):
        super().__init__()
        if not isinstance(d, int) or isinstance(d, bool) or d < 4 or d % 4:
            raise ValueError("d must be a positive multiple of four")
        self.d = d
        self.query = nn.Parameter(torch.empty(n_queries, d))
        # Query initialization is an implementation choice, not a selected width.
        nn.init.normal_(self.query, std=d ** -0.5)
        self.query_norm = nn.LayerNorm(d)
        self.attention = nn.MultiheadAttention(d, 4, dropout=0.1, batch_first=True)
        self.residual_dropout = nn.Dropout(0.1)
        self.output_norm = nn.LayerNorm(d)

    def forward(self, H: Tensor) -> tuple[Tensor, Tensor]:
        _tensor(H, "H", (None, None, self.d))
        q = self.query.unsqueeze(0).expand(H.shape[0], -1, -1)
        attended, weights = self.attention(
            self.query_norm(q), H, H, need_weights=True, average_attn_weights=False
        )
        return self.output_norm(q + self.residual_dropout(attended)), weights


class FeatureHead(nn.Module):
    def __init__(self, d: int):
        super().__init__()
        self.readout = QueryReadout(d, 2)
        self.visual = nn.Linear(d, VISUAL_DIM)
        self.caption = nn.Linear(d, CAPTION_DIM)

    def forward(self, H: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        o, attention = self.readout(H)
        return self.visual(o[:, 0]), self.caption(o[:, 1]), attention


@dataclass
class ReadoutOutput:
    z: Tensor
    p: Tensor
    g: Tensor
    v_hat: Tensor
    c_hat: Tensor
    emotion_attention: Tensor
    feature_attention: Tensor


class DecodedFeatureReadout(nn.Module):
    """H [batch, ROI, d] -> 34 logits/probabilities; features are brain-decoded.

    rank=0 is the additive comparison. rank in {1,2,4,8} is the interaction
    head. d and rank are explicit so the constructor cannot silently select
    a hyperparameter. H is the only forward input.
    """

    def __init__(self, d: int, rank: int):
        super().__init__()
        if isinstance(rank, bool) or rank not in (0, 1, 2, 4, 8):
            raise ValueError("rank must be 0 (additive), 1, 2, 4, or 8")
        self.d, self.rank = d, rank
        self.emotion_query = QueryReadout(d, N_EMOTIONS)
        self.emotion_linears = nn.ModuleList(nn.Linear(d, 1) for _ in range(N_EMOTIONS))
        self.feature_head = FeatureHead(d)
        self.a = nn.Linear(VISUAL_DIM, N_EMOTIONS, bias=True)
        self.b = nn.Linear(CAPTION_DIM, N_EMOTIONS, bias=True)
        self.A = nn.Linear(VISUAL_DIM, rank, bias=False) if rank else None
        self.B = nn.Linear(CAPTION_DIM, rank, bias=False) if rank else None
        self.U = nn.Linear(rank, N_EMOTIONS, bias=False) if rank else None

    def combine(self, g: Tensor, v_hat: Tensor, c_hat: Tensor) -> Tensor:
        """G8 stop-gradient at EVERY decoded-feature entry, including product."""
        _tensor(g, "g", (None, N_EMOTIONS))
        _tensor(v_hat, "v_hat", (g.shape[0], VISUAL_DIM))
        _tensor(c_hat, "c_hat", (g.shape[0], CAPTION_DIM))
        _same_coordinates(g, v_hat, c_hat)
        v, c = v_hat.detach(), c_hat.detach()
        z = g + self.a(v) + self.b(c)
        if self.rank:
            z = z + self.U(self.A(v) * self.B(c))
        return z

    def forward(self, H: Tensor) -> ReadoutOutput:
        o, emotion_attention = self.emotion_query(H)
        g = torch.cat([layer(o[:, e]) for e, layer in enumerate(self.emotion_linears)], dim=-1)
        v_hat, c_hat, feature_attention = self.feature_head(H)
        z = self.combine(g, v_hat, c_hat)
        return ReadoutOutput(z, z.sigmoid(), g, v_hat, c_hat, emotion_attention, feature_attention)


@dataclass
class LossTerms:
    L_emo: Tensor
    L_feat: Tensor
    L: Tensor


def decoding_loss(
    output: ReadoutOutput, y: Tensor, visual_target: Tensor, caption_target: Tensor,
    *, lambda_feat: float, condition: str = "decoded_feature_readout",
) -> LossTerms:
    """S6/N4: mean soft BCE + lambda * (mean visual MSE + mean caption MSE)/2.

    auxiliary_feature_decoding uses g(H) ONLY, including for shuffled pairs.
    Target extraction/standardization happens outside this module, in D9 space.
    No teacher score, emotion reweighting, or target sum-to-one normalization.
    """
    allowed = {"decoded_feature_readout": (0.1, 1.0),
               "auxiliary_feature_decoding": (0.0, 0.1, 1.0)}
    if condition not in allowed or lambda_feat not in allowed[condition]:
        raise ValueError("Condition or lambda is outside G9's fixed candidates")
    n = output.z.shape[0]
    _ratings(y, n)
    _tensor(visual_target, "visual_target", (n, VISUAL_DIM))
    _tensor(caption_target, "caption_target", (n, CAPTION_DIM))
    _same_coordinates(output.z, output.v_hat, output.c_hat, y, visual_target, caption_target)
    logits = output.z if condition == "decoded_feature_readout" else output.g
    L_emo = F.binary_cross_entropy_with_logits(logits, y.detach(), reduction="mean")
    L_feat = (F.mse_loss(output.v_hat, visual_target.detach(), reduction="mean")
              + F.mse_loss(output.c_hat, caption_target.detach(), reduction="mean")) / 2
    return LossTerms(L_emo, L_feat, L_emo + lambda_feat * L_feat)


def swap_2x2(
    model: DecodedFeatureReadout, g_a: Tensor,
    v_a: Tensor, c_a: Tensor, v_b: Tensor, c_b: Tensor,
) -> tuple[Tensor, Tensor, Tensor]:
    """Returns z,p [pair, visual A/B, caption A/B, emotion], I [pair,emotion].

    g(H_A) is reused verbatim in all four cells. I uses logits, never sigmoid p.
    This low-level function also supports length-matched C-direction features.
    """
    z_aa = model.combine(g_a, v_a, c_a)
    z_ab = model.combine(g_a, v_a, c_b)
    z_ba = model.combine(g_a, v_b, c_a)
    z_bb = model.combine(g_a, v_b, c_b)
    z = torch.stack((torch.stack((z_aa, z_ab), 1), torch.stack((z_ba, z_bb), 1)), 1)
    I = (z_bb - z_ba) - (z_ab - z_aa)
    return z, z.sigmoid(), I


def _delta_p(p: Tensor) -> Tensor:
    """[..., pair,2,2,emotion] -> [...,pair,3,emotion]; visual,caption,both."""
    base = p[..., 0, 0, :]
    return torch.stack((p[..., 1, 0, :] - base, p[..., 0, 1, :] - base,
                        p[..., 1, 1, :] - base), dim=-2)


def length_matched_change(a: Tensor, b: Tensor, c: Tensor) -> tuple[Tensor, Tensor]:
    """O3: a + ||b-a|| * (c-a)/||c-a||, separately within each feature space.

    Actual zero-length changes remain exactly a. An undefined nonzero change
    raises, rather than silently resampling C or adding Gaussian noise.
    """
    _tensor(a, "a", (None, None))
    _tensor(b, "b", tuple(a.shape))
    _tensor(c, "c", tuple(a.shape))
    _same_coordinates(a, b, c)
    length = torch.linalg.vector_norm(b - a, dim=-1)
    direction = c - a
    norm = torch.linalg.vector_norm(direction, dim=-1)
    bad = (length > 0) & (norm == 0)
    if bad.any():
        rows = bad.nonzero().flatten().tolist()
        raise ValueError(f"Undefined C-A direction at rows {rows}; O3 gives no fallback")
    safe_norm = torch.where(norm == 0, torch.ones_like(norm), norm)
    changed = a + direction * (length / safe_norm).unsqueeze(-1)
    if not torch.isfinite(changed).all():
        raise ValueError("Length matching overflowed; do not silently clip features")
    return changed, length


@dataclass
class FoldInterventions:
    participant: str
    fold: int
    seed: int
    checkpoint_id: str
    video_ids: tuple[int, ...]
    pairs: Tensor                    # [P,2], local row indices, directed A -> B
    control_indices: Tensor          # [100,P], local C; same C for both paths
    z: Tensor                        # [P,2,2,34]
    p: Tensor
    I: Tensor                        # [P,34]
    delta_p: Tensor                  # [P,3,34]
    delta_y: Tensor                  # [P,34], always original y_B-y_A
    actual_lengths: Tensor           # [P,2], D9 coordinates
    control_z: Tensor                # [100,P,2,2,34]
    control_p: Tensor
    control_I: Tensor                # [100,P,34]
    control_delta_p: Tensor          # [100,P,3,34]
    control_lengths: Tensor          # [100,P,2], measured AFTER transformation
    control_seed: int


@torch.no_grad()
def interchange_intervention(
    model: DecodedFeatureReadout, H: Tensor, ratings: Tensor, pairs: Tensor, *,
    video_ids: Sequence[int], participant: str, fold: int, seed: int,
    checkpoint_id: str, control_seed: int,
) -> FoldInterventions:
    """S9/O3, one held-out fold. H contains all eligible videos for this participant.

    Caller supplies the fixed semantic-nearest-neighbour pairs from the manifest;
    they are NOT selected from ratings, H or predictions here. Supply only the
    same fold's videos, same participant, and same checkpoint. Metadata records
    that contract; this component cannot verify provenance against external files.
    All results are detached CPU tensors suitable for torch.save and resampling.
    """
    _tensor(H, "H", (None, None, model.d))
    n = H.shape[0]
    _ratings(ratings, n)
    _same_coordinates(H, ratings)
    ids = tuple(int(i) for i in video_ids)
    if len(ids) != n or len(set(ids)) != n:
        raise ValueError("Supply one unique canonical video ID per H row")
    if n < 3:
        raise ValueError("O3 needs at least three eligible videos: distinct A, B, C")
    if not participant or not checkpoint_id or fold not in range(1, 7) or seed not in (0, 1, 2):
        raise ValueError("Supply participant/checkpoint, outer fold 1..6 and seed 0..2")
    if not isinstance(pairs, Tensor) or pairs.dtype != torch.long or pairs.ndim != 2 or pairs.shape[1] != 2 or not pairs.shape[0]:
        raise ValueError("pairs must be a nonempty int64 [P,2] index tensor")
    pairs = pairs.detach().cpu()
    if (pairs < 0).any() or (pairs >= n).any() or (pairs[:, 0] == pairs[:, 1]).any():
        raise ValueError("A/B must be distinct indices of this fold's videos")
    if len(set(map(tuple, pairs.tolist()))) != len(pairs):
        raise ValueError("Duplicate directed pairs are not allowed")
    a, b = pairs[:, 0].to(H.device), pairs[:, 1].to(H.device)
    generator = torch.Generator(device="cpu").manual_seed(control_seed)
    c_indices = torch.empty(CONTROL_REPEATS, len(pairs), dtype=torch.long)
    for j, (ai, bi) in enumerate(pairs.tolist()):
        eligible = torch.tensor([i for i in range(n) if i not in (ai, bi)])
        c_indices[:, j] = eligible[torch.randint(len(eligible), (CONTROL_REPEATS,), generator=generator)]

    # Fix stochastic layers during intervention. Restore all original mode flags.
    modes = [(module, module.training) for module in model.modules()]
    model.eval()
    try:
        output = model(H)
        g, va, ca = output.g[a], output.v_hat[a], output.c_hat[a]
        vb, cb = output.v_hat[b], output.c_hat[b]
        z, p, I = swap_2x2(model, g, va, ca, vb, cb)
        actual_lengths = torch.stack((torch.linalg.vector_norm(vb-va, dim=-1),
                                      torch.linalg.vector_norm(cb-ca, dim=-1)), -1)
        control_z, control_p, control_I, lengths = [], [], [], []
        for cs in c_indices:
            cs = cs.to(H.device)
            v_random, _ = length_matched_change(va, vb, output.v_hat[cs])
            c_random, _ = length_matched_change(ca, cb, output.c_hat[cs])
            rz, rp, ri = swap_2x2(model, g, va, ca, v_random, c_random)
            control_z.append(rz.cpu())
            control_p.append(rp.cpu())
            control_I.append(ri.cpu())
            lengths.append(torch.stack((torch.linalg.vector_norm(v_random-va, dim=-1),
                                        torch.linalg.vector_norm(c_random-ca, dim=-1)), -1).cpu())
        controls_p = torch.stack(control_p)
        return FoldInterventions(
            participant, fold, seed, checkpoint_id, ids, pairs, c_indices,
            z.cpu(), p.cpu(), I.cpu(), _delta_p(p).cpu(), (ratings[b]-ratings[a]).cpu(),
            actual_lengths.cpu(), torch.stack(control_z), controls_p,
            torch.stack(control_I), _delta_p(controls_p), torch.stack(lengths), control_seed,
        )
    finally:
        for module, training in modes:
            module.training = training


@dataclass
class Alignment:
    r: Tensor
    constant_target: Tensor
    constant_prediction: Tensor
    zero_target: Tensor
    insufficient_pairs: bool


def change_alignment(delta_p: Tensor, delta_y: Tensor) -> Alignment:
    """O2: Pearson across pairs, NOT across emotions; retain zero-delta pairs.

    delta_p [pair,...,34], delta_y [pair,34]. Outputs [...,34]. NaN explicitly
    marks an undefined r. A nonzero constant delta_y is also mathematically
    undefined and is flagged separately from the specified all-zero case.
    """
    if delta_p.ndim < 2:
        raise ValueError("delta_p needs a pair axis and an emotion axis")
    _tensor(delta_p, "delta_p", (None,) * (delta_p.ndim-1) + (N_EMOTIONS,))
    _tensor(delta_y, "delta_y", (delta_p.shape[0], N_EMOTIONS))
    _same_coordinates(delta_p, delta_y)
    p = delta_p.double()
    y = delta_y.double().reshape((len(delta_y),) + (1,)*(p.ndim-2) + (N_EMOTIONS,))
    const_p = (p == p[0:1]).all(dim=0)
    const_y = (delta_y == delta_y[0:1]).all(dim=0)
    zero_y = (delta_y == 0).all(dim=0)
    x_centered, y_centered = p-p.mean(0), y-y.mean(0)
    denom = torch.linalg.vector_norm(x_centered, dim=0) * torch.linalg.vector_norm(y_centered, dim=0)
    valid = (~const_p) & (~const_y) & (denom > 0)
    r = (x_centered*y_centered).sum(0) / torch.where(denom > 0, denom, torch.ones_like(denom))
    r = torch.where(valid, r.clamp(-1, 1), torch.full_like(r, float("nan")))
    return Alignment(r, const_y, const_p, zero_y, len(delta_y) < 2)


def summarize_interventions(results: Sequence[FoldInterventions]) -> dict[str, Tensor | tuple]:
    """O2/O3: pool pairs across folds, calculate EACH draw's r, then average r.

    Can summarize a subset for diagnostics; returned folds/n_pairs document that
    it is not the final six-fold estimate. Seeds and participants cannot mix.
    Undefined controls propagate NaN instead of redefining the 100-draw average.
    The overall mean uses only variable-target emotions; constant predictions
    propagate NaN and are reported, rather than being silently excluded.
    """
    if not results:
        raise ValueError("At least one fold result is required")
    key = {(x.participant, x.seed) for x in results}
    if len(key) != 1 or len({x.fold for x in results}) != len(results):
        raise ValueError("Pool one participant/seed with at most one result per fold")
    all_ids = [i for x in results for i in x.video_ids]
    if len(set(all_ids)) != len(all_ids):
        raise ValueError("A canonical video occurs in multiple outer test folds")
    dp = torch.cat([x.delta_p for x in results], 0)
    dy = torch.cat([x.delta_y for x in results], 0)
    control_dp = torch.cat([x.control_delta_p for x in results], 1)
    real = change_alignment(dp, dy)
    # [100,P,3,34] -> [P,100,3,34], so r is computed over P for each draw.
    controls = change_alignment(control_dp.movedim(1, 0), dy)
    control_r = controls.r.mean(0)
    effect = real.r - control_r
    eligible = ~real.constant_target
    effect_mean = effect[:, eligible].mean(-1) if eligible.any() else torch.full((3,), float("nan"), dtype=torch.float64)
    abs_I = torch.cat([x.I for x in results], 0).double().abs().mean(0)
    control_abs_I_each = torch.cat([x.control_I for x in results], 1).double().abs().mean(1)
    return {
        "folds": tuple(sorted(x.fold for x in results)), "path_order": PATH_ORDER,
        "n_pairs": torch.tensor(len(dy)), "actual_r": real.r,
        "control_r_each": controls.r, "control_r_mean": control_r,
        "effect": effect, "effect_mean": effect_mean,
        "visual_minus_caption_effect": effect[0]-effect[1],
        "zero_target": real.zero_target, "constant_target": real.constant_target,
        "constant_prediction": real.constant_prediction,
        "control_constant_prediction": controls.constant_prediction,
        "n_constant_prediction": real.constant_prediction.sum(-1),
        "n_control_constant_prediction": controls.constant_prediction.sum(-1),
        "n_eligible_emotions": eligible.sum(), "mean_abs_I": abs_I,
        "control_mean_abs_I_each": control_abs_I_each,
        "control_mean_abs_I": control_abs_I_each.mean(0),
        "mean_abs_I_effect": abs_I-control_abs_I_each.mean(0),
    }


@dataclass(frozen=True)
class ScenePairShuffle:
    """Save this immutable mapping with the run; reuse every epoch/candidate."""
    outer_fold: int
    seed: int
    random_seed: int
    manifest: tuple[tuple[int, int], ...]
    mc_test_ids: tuple[int, ...]
    mapping: tuple[tuple[int, int], ...]  # recipient -> donor, canonical video IDs

    @property
    def validation_fold(self) -> int:
        return self.outer_fold % 6 + 1


def make_scene_pair_shuffle(
    run_fold_by_video: Mapping[int, int], *, outer_fold: int, seed: int,
    mc_test_ids: Sequence[int],
) -> ScenePairShuffle:
    """O1/H2: fixed video-level derangement of the FOUR weight-training folds.

    Manifest uses canonical IDs (duplicates of MC clips must be canonicalized or
    included in mc_test_ids). Does not depend on input row order, participant,
    lambda, or epoch. Rejection from uniform permutations gives a derangement;
    a cyclic roll would sample a different, unnecessarily restricted family.
    """
    if outer_fold not in range(1, 7) or seed not in (0, 1, 2):
        raise ValueError("outer_fold must be 1..6; seed must be 0, 1, or 2")
    manifest = tuple(sorted((int(i), int(f)) for i, f in run_fold_by_video.items()))
    if not manifest or any(f not in range(1, 7) for _, f in manifest):
        raise ValueError("A nonempty canonical video -> run-fold manifest is required")
    excluded = tuple(sorted(set(map(int, mc_test_ids))))
    validation = outer_fold % 6 + 1
    train_ids = [i for i, f in manifest if f not in (outer_fold, validation) and i not in excluded]
    if len(train_ids) < 2:
        raise ValueError("A derangement requires at least two eligible training videos")
    # Stable Python-independent seed derivation; store both user and derived seeds.
    digest = hashlib.sha256(f"EmoBrain/O1/{outer_fold}/{seed}".encode()).digest()
    random_seed = int.from_bytes(digest[:8], "big")
    rng = random.Random(random_seed)
    donor_ids = list(train_ids)
    while True:
        rng.shuffle(donor_ids)
        if all(a != b for a, b in zip(train_ids, donor_ids)):
            break
    return ScenePairShuffle(outer_fold, seed, random_seed, manifest, excluded,
                            tuple(zip(train_ids, donor_ids)))


def apply_shuffled_scene_pairs(
    plan: ScenePairShuffle, row_video_ids: Sequence[int], feature_video_ids: Sequence[int],
    visual_targets: Tensor, caption_targets: Tensor, *, split: str,
) -> tuple[Tensor, Tensor, tuple[int, ...]]:
    """Apply O1 to targets only. Brain inputs and emotion ratings are not arguments.

    row_video_ids can contain five participant rows for the same video, in any
    order: all get the same donor pair. Validation/test return original targets.
    Banks are video-level, already standardized by the external D9 preprocessing.
    """
    ids = tuple(map(int, feature_video_ids))
    rows = tuple(map(int, row_video_ids))
    if not rows or len(set(ids)) != len(ids):
        raise ValueError("Nonempty batch and unique canonical feature-bank IDs required")
    _tensor(visual_targets, "visual_targets", (len(ids), VISUAL_DIM))
    _tensor(caption_targets, "caption_targets", (len(ids), CAPTION_DIM))
    _same_coordinates(visual_targets, caption_targets)
    if split not in ("train", "validation", "test"):
        raise ValueError("split must be train, validation, or test")
    manifest, mapping = dict(plan.manifest), dict(plan.mapping)
    expected_train = {i for i, f in plan.manifest if f not in (plan.outer_fold, plan.validation_fold) and i not in plan.mc_test_ids}
    if set(mapping) != expected_train or set(mapping.values()) != expected_train or any(a == b for a, b in mapping.items()):
        raise ValueError("Saved plan is not a derangement of the permitted training set")
    bank = {i: j for j, i in enumerate(ids)}
    donors = []
    for i in rows:
        if i not in manifest or i in plan.mc_test_ids:
            raise ValueError(f"Video {i} is unknown or excluded from HK development")
        f = manifest[i]
        valid = (i in expected_train if split == "train" else
                 f == (plan.validation_fold if split == "validation" else plan.outer_fold))
        if not valid:
            raise ValueError(f"Video {i} violates the {split} boundary")
        donor = mapping[i] if split == "train" else i
        if donor not in bank:
            raise ValueError(f"Missing feature-bank video {donor}")
        donors.append(donor)
    index = torch.tensor([bank[i] for i in donors], device=visual_targets.device)
    return visual_targets[index], caption_targets[index], tuple(donors)


def shuffled_scene_pair_loss(
    output: ReadoutOutput, y: Tensor, plan: ScenePairShuffle,
    row_video_ids: Sequence[int], feature_video_ids: Sequence[int],
    visual_targets: Tensor, caption_targets: Tensor, *, lambda_feat: float,
) -> tuple[LossTerms, tuple[int, ...]]:
    """The specified G6 control: AUXILIARY decoding with fixed incorrect pairs.

    Uses g(H) for emotion BCE, not the main model's feature-readout logits.
    Validation/early stopping must use actual y, not these shuffled targets.
    """
    if lambda_feat not in (0.1, 1.0):
        raise ValueError("The shuffled-pair control uses lambda 0.1 or 1.0 (S6)")
    v, c, donors = apply_shuffled_scene_pairs(
        plan, row_video_ids, feature_video_ids, visual_targets, caption_targets, split="train"
    )
    return decoding_loss(output, y, v, c, lambda_feat=lambda_feat,
                         condition="auxiliary_feature_decoding"), donors


# Standalone synthetic verification functions. No real data, GPU or repository
# training code is needed. Unrelated S6 teacher/encoder tests are not claimed.
def verify_readout_and_loss() -> None:
    torch.manual_seed(10)
    H = torch.randn(4, 11, 16, dtype=torch.float64)
    model = DecodedFeatureReadout(16, 2).double().eval()
    out = model(H)
    assert out.z.shape == out.p.shape == (4, 34)
    assert out.v_hat.shape == (4, 5632) and out.c_hat.shape == (4, 4096)
    assert out.emotion_attention.shape == (4, 4, 34, 11)
    assert out.feature_attention.shape == (4, 4, 2, 11)
    assert model.a.bias is not None and model.b.bias is not None
    assert model.A.bias is model.B.bias is model.U.bias is None
    for rank in (0, 1, 2, 4, 8):
        assert DecodedFeatureReadout(8, rank)(H.float()[..., :8]).z.shape == (4, 34)
    torch.testing.assert_close(out.p, out.z.sigmoid())
    explicit = out.g + model.a(out.v_hat) + model.b(out.c_hat)
    explicit += model.U(model.A(out.v_hat)*model.B(out.c_hat))
    torch.testing.assert_close(out.z, explicit)
    y = torch.rand(4, 34, dtype=H.dtype)
    # Unequal feature dimensions must NOT produce unequal modality weights.
    v, c = out.v_hat.detach()+2, out.c_hat.detach()+3
    losses = decoding_loss(out, y, v, c, lambda_feat=0.1)
    torch.testing.assert_close(losses.L_feat, torch.tensor(6.5, dtype=H.dtype))
    emo = -(y*F.logsigmoid(out.z)+(1-y)*F.logsigmoid(-out.z)).mean()
    torch.testing.assert_close(losses.L_emo, emo)
    torch.testing.assert_close(losses.L, emo+0.65)
    aux = decoding_loss(out, y, v, c, lambda_feat=0, condition="auxiliary_feature_decoding")
    torch.testing.assert_close(aux.L, F.binary_cross_entropy_with_logits(out.g, y))
    with unittest.TestCase().assertRaises(ValueError):
        decoding_loss(out, y, v, c, lambda_feat=0)
    with unittest.TestCase().assertRaises(ValueError):
        DecodedFeatureReadout(6, 2)


def verify_gradient_routes() -> None:
    torch.manual_seed(11)
    for rank in (0, 2):
        model = DecodedFeatureReadout(8, rank).double().eval()
        H = torch.randn(3, 7, 8, dtype=torch.float64, requires_grad=True)
        out = model(H)
        y = torch.rand(3, 34, dtype=H.dtype)
        losses = decoding_loss(out, y, torch.randn_like(out.v_hat),
                               torch.randn_like(out.c_hat), lambda_feat=1)
        losses.L_emo.backward()
        assert all(p.grad is None or not p.grad.any() for p in model.feature_head.parameters())
        assert H.grad is not None and H.grad.abs().sum() > 0
        assert model.emotion_query.query.grad.abs().sum() > 0
        assert model.a.weight.grad.abs().sum() > 0 and model.b.weight.grad.abs().sum() > 0
        if rank:
            assert all(x.weight.grad.abs().sum() > 0 for x in (model.A, model.B, model.U))
        model.zero_grad(set_to_none=True)
        H.grad = None
        out = model(H)
        losses = decoding_loss(out, y, torch.randn_like(out.v_hat),
                               torch.randn_like(out.c_hat), lambda_feat=1)
        losses.L_feat.backward()
        assert all(p.grad is not None and p.grad.abs().sum() > 0 for p in model.feature_head.parameters())
        assert H.grad.abs().sum() > 0
        assert all(p.grad is None for p in model.emotion_query.parameters())
        # Both losses can train together with finite, nonzero feature gradients.
        model.zero_grad(set_to_none=True)
        out = model(H)
        losses = decoding_loss(out, y, torch.randn_like(out.v_hat),
                               torch.randn_like(out.c_hat), lambda_feat=0.1)
        losses.L.backward()
        assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())


def verify_swap_algebra() -> None:
    torch.manual_seed(12)
    g = torch.randn(5, 34, dtype=torch.float64)
    va, vb = [torch.randn(5, VISUAL_DIM, dtype=g.dtype) for _ in range(2)]
    ca, cb = [torch.randn(5, CAPTION_DIM, dtype=g.dtype) for _ in range(2)]
    for rank in (0, 1, 2, 4, 8):
        model = DecodedFeatureReadout(8, rank).double().eval()
        z, p, I = swap_2x2(model, g, va, ca, vb, cb)
        assert z.shape == p.shape == (5, 2, 2, 34)
        torch.testing.assert_close(z[:, 1, 0], model.combine(g, vb, ca))
        torch.testing.assert_close(z[:, 0, 1], model.combine(g, va, cb))
        if rank:
            expected = model.U(model.A(vb-va)*model.B(cb-ca))
            torch.testing.assert_close(I, expected, atol=1e-12, rtol=1e-11)
            assert I.abs().max() > 1e-6
        else:
            torch.testing.assert_close(I, torch.zeros_like(I), atol=1e-12, rtol=0)
            # A probability-scale contrast can be nonzero even for an additive head.
            pI = p[:, 1, 1]-p[:, 1, 0]-p[:, 0, 1]+p[:, 0, 0]
            assert pI.abs().max() > 1e-5
        _, _, identical_I = swap_2x2(model, g, va, ca, va, ca)
        torch.testing.assert_close(identical_I, torch.zeros_like(I), atol=0, rtol=0)


def verify_length_matching_and_undefined_cases() -> None:
    a = torch.tensor([[0., 0.], [1., 1.], [0., 0.]], dtype=torch.float64)
    b = torch.tensor([[3., 4.], [1., 1.], [0., 2.]], dtype=torch.float64)
    c = torch.tensor([[0., 2.], [1., 1.], [4., 0.]], dtype=torch.float64)
    changed, length = length_matched_change(a, b, c)
    torch.testing.assert_close(changed, torch.tensor([[0., 5.], [1., 1.], [2., 0.]], dtype=a.dtype))
    torch.testing.assert_close(torch.linalg.vector_norm(changed-a, dim=-1), length)
    with unittest.TestCase().assertRaises(ValueError):
        length_matched_change(a, b, a)
    y = torch.zeros(5, 34, dtype=torch.float64)
    y[:, 0] = torch.tensor([0., 0., 0.1, 0.4, -0.2])
    y[:, 2] = 0.3  # nonzero constant: mathematically undefined too
    dp = torch.zeros(5, 3, 34, dtype=y.dtype)
    dp[:, 0, 0], dp[:, 1, 0] = y[:, 0]*2, -y[:, 0]
    aligned = change_alignment(dp, y)
    torch.testing.assert_close(aligned.r[:2, 0], torch.tensor([1., -1.], dtype=y.dtype))
    assert torch.isnan(aligned.r[2, 0]) and aligned.constant_prediction[2, 0]
    assert aligned.zero_target[1] and aligned.constant_target[2] and not aligned.zero_target[2]
    assert change_alignment(dp[:1], y[:1]).insufficient_pairs


def verify_control_and_fold_aggregation() -> None:
    torch.manual_seed(13)
    model = DecodedFeatureReadout(8, 2).double()
    results = []
    H0 = None
    for fold in (1, 2):
        H = torch.randn(7, 9, 8, dtype=torch.float64)
        y = torch.rand(7, 34, dtype=torch.float64)
        y[:, 3] = 0
        pairs = torch.tensor([[i, (i+1) % 7] for i in range(7)])
        kwargs = dict(video_ids=list(range(fold*100, fold*100+7)), participant="synthetic-1",
                      fold=fold, seed=0, checkpoint_id=f"test-fold-{fold}", control_seed=17)
        result = interchange_intervention(model, H, y, pairs, **kwargs)
        assert model.training  # eval mode is restored
        assert result.control_z.shape == (100, 7, 2, 2, 34)
        assert not result.z.requires_grad and not result.control_z.requires_grad
        assert ((result.control_indices != pairs[:, 0]) & (result.control_indices != pairs[:, 1])).all()
        torch.testing.assert_close(result.delta_y, y[pairs[:, 1]]-y[pairs[:, 0]])
        torch.testing.assert_close(result.control_lengths, result.actual_lengths.expand(100, -1, -1))
        torch.testing.assert_close(result.control_z[:, :, 0, 0], result.z[:, 0, 0].expand(100, -1, -1))
        # Independently reconstruct a control from its recorded C; both paths use it.
        model.eval()
        out = model(H)
        model.train()
        ai, bi, ci = int(pairs[0, 0]), int(pairs[0, 1]), int(result.control_indices[0, 0])
        v, _ = length_matched_change(out.v_hat[ai:ai+1], out.v_hat[bi:bi+1], out.v_hat[ci:ci+1])
        c, _ = length_matched_change(out.c_hat[ai:ai+1], out.c_hat[bi:bi+1], out.c_hat[ci:ci+1])
        expected = model.combine(out.g[ai:ai+1], v, c)
        torch.testing.assert_close(result.control_z[0, 0, 1, 1], expected[0])
        if fold == 1:
            repeated = interchange_intervention(model, H, y, pairs, **kwargs)
            assert torch.equal(repeated.control_indices, result.control_indices)
            torch.testing.assert_close(repeated.control_p, result.control_p, rtol=0, atol=0)
            H0 = H
        results.append(result)
    summary = summarize_interventions(results)
    dy = torch.cat([x.delta_y for x in results])
    dp = torch.cat([x.delta_p for x in results])
    controls = torch.cat([x.control_delta_p for x in results], 1)
    expected_r = torch.corrcoef(torch.stack((dp[:, 0, 0], dy[:, 0])))[0, 1]
    torch.testing.assert_close(summary["actual_r"][0, 0], expected_r)
    each_r = torch.stack([torch.corrcoef(torch.stack((draw[:, 0, 0], dy[:, 0])))[0, 1] for draw in controls])
    torch.testing.assert_close(summary["control_r_mean"][0, 0], each_r.mean())
    wrong_r = torch.corrcoef(torch.stack((controls[:, :, 0, 0].mean(0), dy[:, 0])))[0, 1]
    assert not torch.isclose(each_r.mean(), wrong_r, atol=1e-6)
    torch.testing.assert_close(summary["effect"], summary["actual_r"]-summary["control_r_mean"], equal_nan=True)
    assert summary["zero_target"][3] and torch.isnan(summary["effect"][:, 3]).all()
    assert summary["n_eligible_emotions"].item() == 33
    assert summary["folds"] == (1, 2) and summary["n_pairs"].item() == 14
    with unittest.TestCase().assertRaises(ValueError):
        summarize_interventions([results[0], results[0]])
    # Float32 additive model: I=0 also holds for actual and random swaps.
    additive = DecodedFeatureReadout(8, 0)
    r = interchange_intervention(additive, H0.float(), torch.rand(7, 34), pairs,
                                 video_ids=range(7), participant="s", fold=1, seed=0,
                                 checkpoint_id="additive", control_seed=3)
    torch.testing.assert_close(r.I, torch.zeros_like(r.I), atol=2e-6, rtol=0)
    torch.testing.assert_close(r.control_I, torch.zeros_like(r.control_I), atol=2e-6, rtol=0)


def verify_shuffle_and_application() -> None:
    torch.manual_seed(14)
    manifest = {i: i % 6+1 for i in range(24)}
    excluded = (2, 8)
    plan = make_scene_pair_shuffle(manifest, outer_fold=1, seed=0, mc_test_ids=excluded)
    again = make_scene_pair_shuffle(dict(reversed(list(manifest.items()))), outer_fold=1, seed=0, mc_test_ids=excluded)
    assert plan == again  # order, epochs, lambda and participants cannot change it
    expected_train = {i for i, f in manifest.items() if f not in (1, 2) and i not in excluded}
    mapping = dict(plan.mapping)
    assert set(mapping) == set(mapping.values()) == expected_train
    assert all(a != b for a, b in mapping.items())
    last_fold = make_scene_pair_shuffle(manifest, outer_fold=6, seed=1, mc_test_ids=excluded)
    assert last_fold.validation_fold == 1
    # Reordered feature bank, repeated participant rows, and paired targets.
    ids = list(reversed(range(24)))
    v = torch.tensor(ids, dtype=torch.float64)[:, None].expand(-1, VISUAL_DIM)
    c = (torch.tensor(ids, dtype=torch.float64)+100)[:, None].expand(-1, CAPTION_DIM)
    row_id = sorted(expected_train)[0]
    rows = [row_id]*5 + [sorted(expected_train)[1]]
    sv, sc, donors = apply_shuffled_scene_pairs(plan, rows, ids, v, c, split="train")
    assert len(set(donors[:5])) == 1 and donors[0] != row_id
    torch.testing.assert_close(sv[:, 0], torch.tensor(donors, dtype=torch.float64))
    torch.testing.assert_close(sc[:, 0]-100, sv[:, 0])
    for split, selected in (("validation", [1, 7]), ("test", [0, 6])):
        uv, uc, unchanged = apply_shuffled_scene_pairs(plan, selected, ids, v, c, split=split)
        assert unchanged == tuple(selected)
        torch.testing.assert_close(uv[:, 0], torch.tensor(selected, dtype=torch.float64))
    for forbidden in (0, 1, 2, 8):
        with unittest.TestCase().assertRaises(ValueError):
            apply_shuffled_scene_pairs(plan, [forbidden], ids, v, c, split="train")
    with unittest.TestCase().assertRaises(ValueError):
        make_scene_pair_shuffle({0: 3}, outer_fold=1, seed=0, mc_test_ids=())
    model = DecodedFeatureReadout(8, 2).double().eval()
    H = torch.randn(len(rows), 5, 8, dtype=torch.float64)
    y = torch.rand(len(rows), 34, dtype=torch.float64)
    H_before, y_before = H.clone(), y.clone()
    out = model(H)
    loss, used_ids = shuffled_scene_pair_loss(out, y, plan, rows, ids, v, c, lambda_feat=0.1)
    assert used_ids == donors and torch.equal(H, H_before) and torch.equal(y, y_before)
    torch.testing.assert_close(loss.L_emo, F.binary_cross_entropy_with_logits(out.g, y))
    torch.testing.assert_close(loss.L_feat, (F.mse_loss(out.v_hat, sv)+F.mse_loss(out.c_hat, sc))/2)
    loss.L.backward()
    assert model.feature_head.visual.weight.grad.abs().sum() > 0
    assert model.a.weight.grad is None and model.b.weight.grad is None
    assert all(layer.weight.grad is None for layer in (model.A, model.B, model.U))


def run_self_tests() -> bool:
    """Run six independent groups; failures print tracebacks and return False."""
    tests = (
        verify_readout_and_loss, verify_gradient_routes, verify_swap_algebra,
        verify_length_matching_and_undefined_cases, verify_control_and_fold_aggregation,
        verify_shuffle_and_application,
    )
    suite = unittest.TestSuite(unittest.FunctionTestCase(test) for test in tests)
    threads = torch.get_num_threads()
    deterministic = torch.are_deterministic_algorithms_enabled()
    warn_only = torch.is_deterministic_algorithms_warn_only_enabled()
    try:
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        with torch.random.fork_rng(devices=[]):
            result = unittest.TextTestRunner(verbosity=2).run(suite)
        print(f"EmoBrain synthetic verification: {result.testsRun-len(result.failures)-len(result.errors)}/{result.testsRun} groups passed.")
        return result.wasSuccessful()
    finally:
        torch.set_num_threads(threads)
        torch.use_deterministic_algorithms(deterministic, warn_only=warn_only)


if __name__ == "__main__":
    raise SystemExit(0 if run_self_tests() else 1)
