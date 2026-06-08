"""
Phase 1 Audit Step 1A. Embedding inventory.

Scans /pscratch/sd/s/sjmoon/FEELIN/output/embeddings/ and reports for every
.pt file: variant (model + init + padding), subject, tensor shape, stim count,
embed dim, file size, mtime, and any structural anomalies.

Writes:
  reports/phase1_audit_20260604/1A_embeddings_inventory.csv
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import torch

EMB_ROOT = Path("/pscratch/sd/s/sjmoon/FEELIN/output/embeddings")
OUT_CSV = Path(
    "/pscratch/sd/s/sjmoon/FEELIN/reports/phase1_audit_20260604/1A_embeddings_inventory.csv"
)
CANONICAL_STIM = 2185


def parse_variant(name: str) -> dict:
    """Parse variant directory name into structured fields.

    Examples:
      brain_jepa_resting_pad-mean
        -> model=brain_jepa, init=resting, padding=mean, sub_variant=
      brain_jepa_LEGACY_T20first16_resting_pad-mean
        -> model=brain_jepa, init=resting, padding=mean, sub_variant=LEGACY_T20first16
      swift_NewE96_SL20_resting_pad-mean
        -> model=swift, init=resting, padding=mean, sub_variant=NewE96_SL20
      swift_NewE96_SL20_resting_pad-cyclic_replicate
        -> model=swift, init=resting, padding=cyclic_replicate, sub_variant=NewE96_SL20
      roi_schaefer400tian50_mean
        -> model=roi, init=NA, padding=mean, sub_variant=schaefer400tian50
    """
    if name.startswith("roi_"):
        rest = name[len("roi_"):]
        if rest.endswith("_mean"):
            return dict(
                model="roi",
                init="NA",
                padding="mean",
                sub_variant=rest[:-len("_mean")],
            )
        return dict(model="roi", init="NA", padding="UNK", sub_variant=rest)

    # Identify model prefix.
    if name.startswith("brain_jepa"):
        model = "brain_jepa"
        rest = name[len("brain_jepa"):].lstrip("_")
    elif name.startswith("neurostorm"):
        model = "neurostorm"
        rest = name[len("neurostorm"):].lstrip("_")
    elif name.startswith("swift_"):
        model = "swift"
        rest = name[len("swift_"):]
    else:
        return dict(model="UNK", init="UNK", padding="UNK", sub_variant=name)

    # Split padding off via "_pad-".
    if "_pad-" in rest:
        head, pad = rest.rsplit("_pad-", 1)
    else:
        head, pad = rest, "UNK"

    # In head, last token before _pad- is init (resting / scratch). Anything
    # before that is sub_variant (e.g. NewE96_SL20, LEGACY_T20first16).
    tokens = head.split("_")
    init = "UNK"
    for marker in ("resting", "scratch"):
        if marker in tokens:
            idx = tokens.index(marker)
            init = marker
            sub_variant = "_".join(tokens[:idx])
            break
    else:
        sub_variant = head

    return dict(model=model, init=init, padding=pad, sub_variant=sub_variant)


def inspect_pt(path: Path) -> dict:
    """Load .pt and return shape info. Does not require GPU."""
    try:
        obj = torch.load(path, map_location="cpu", weights_only=False)
    except Exception as exc:
        return dict(
            load_ok=False,
            err=str(exc)[:200],
            shape="",
            stim_n=-1,
            embed_dim=-1,
            ndim=-1,
            dtype="",
            obj_type="",
        )

    obj_type = type(obj).__name__
    tensor = None
    if isinstance(obj, torch.Tensor):
        tensor = obj
    elif isinstance(obj, dict):
        # Heuristic: common keys
        for k in ("embedding", "embeddings", "feat", "feats", "x", "data"):
            if k in obj and isinstance(obj[k], torch.Tensor):
                tensor = obj[k]
                break
        if tensor is None:
            # Pick largest tensor.
            cands = [(k, v) for k, v in obj.items() if isinstance(v, torch.Tensor)]
            if cands:
                cands.sort(key=lambda kv: kv[1].numel(), reverse=True)
                tensor = cands[0][1]

    if tensor is None:
        return dict(
            load_ok=True,
            err="no tensor found",
            shape="",
            stim_n=-1,
            embed_dim=-1,
            ndim=-1,
            dtype="",
            obj_type=obj_type,
        )

    shape = tuple(tensor.shape)
    return dict(
        load_ok=True,
        err="",
        shape=str(shape),
        stim_n=shape[0] if len(shape) >= 1 else -1,
        embed_dim=shape[-1] if len(shape) >= 1 else -1,
        ndim=tensor.ndim,
        dtype=str(tensor.dtype).replace("torch.", ""),
        obj_type=obj_type,
    )


def main():
    rows = []
    variant_dirs = sorted([d for d in EMB_ROOT.iterdir() if d.is_dir()])
    print(f"[1A] {len(variant_dirs)} variant directories", file=sys.stderr)

    for vd in variant_dirs:
        parsed = parse_variant(vd.name)
        pt_files = sorted(vd.glob("sub-*.pt"))
        if not pt_files:
            rows.append({
                "variant": vd.name,
                **parsed,
                "subject": "",
                "file_path": str(vd),
                "file_exists": False,
                "file_size_mb": 0.0,
                "mtime": "",
                "load_ok": False,
                "err": "no sub-*.pt files",
                "shape": "",
                "stim_n": -1,
                "embed_dim": -1,
                "ndim": -1,
                "dtype": "",
                "obj_type": "",
                "stim_match_canonical": False,
            })
            continue
        for pf in pt_files:
            stat = pf.stat()
            info = inspect_pt(pf)
            rows.append({
                "variant": vd.name,
                **parsed,
                "subject": pf.stem,
                "file_path": str(pf),
                "file_exists": True,
                "file_size_mb": round(stat.st_size / 1e6, 3),
                "mtime": __import__("datetime").datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                **info,
                "stim_match_canonical": info["stim_n"] == CANONICAL_STIM,
            })
            print(f"  {vd.name}/{pf.name}: {info['shape']}", file=sys.stderr)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    cols = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[1A] wrote {len(rows)} rows to {OUT_CSV}", file=sys.stderr)


if __name__ == "__main__":
    main()
