#!/usr/bin/env python3
"""Export panel-ready CCN figures from completed analysis outputs.

This script never fits a model. It reads existing result files, writes concise
poster panels, and records which corrected analyses are still missing.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def find_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "CLAUDE.md").is_file() and (candidate / "study1").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CCN root")


ROOT = find_root()
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "study1/data/.matplotlib"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


BLUE = "#2463A6"
ORANGE = "#D55E00"
GREEN = "#009E73"
MAGENTA = "#B35C9B"
CHARCOAL = "#252A2E"
MID_GRAY = "#7A8288"
LIGHT_GRAY = "#E8ECEF"
NETWORKS = ["Vis", "SomMot", "DorsAttn", "SalVentAttn", "Limbic", "Cont", "Default"]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "study1/results/poster_export",
    )
    parser.add_argument("--watch-minutes", type=float, default=0.0)
    parser.add_argument("--interval-seconds", type=int, default=120)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "savefig.facecolor": "white",
        }
    )


def save_figure(fig, output_dir: Path, stem: str):
    png = output_dir / f"{stem}.png"
    pdf = output_dir / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return [png, pdf]


def box(ax, xy, width, height, title, subtitle, color):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.8,
        edgecolor=color,
        facecolor="white",
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height * 0.64, title, ha="center", va="center",
            fontsize=13, fontweight="bold", color=CHARCOAL)
    ax.text(xy[0] + width / 2, xy[1] + height * 0.30, subtitle, ha="center", va="center",
            fontsize=9, color=MID_GRAY, linespacing=1.2)


def arrow(ax, start, end, color=CHARCOAL):
    ax.add_patch(
        FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                        linewidth=1.5, color=color)
    )


def figure_framework(output_dir: Path):
    fig, ax = plt.subplots(figsize=(14, 4.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    box(ax, (0.02, 0.57), 0.18, 0.28, "Video foundation model",
        "V-JEPA2\nvideo-only pretraining", BLUE)
    box(ax, (0.02, 0.15), 0.18, 0.28, "Brain foundation models",
        "corrected Brain-JEPA\nSwiFT / NeuroSTORM", GREEN)
    box(ax, (0.29, 0.36), 0.19, 0.30, "Cross-domain channel",
        "held-out stimulus alignment\nno emotion supervision", MAGENTA)
    box(ax, (0.57, 0.57), 0.18, 0.28, "Shared cortical signal",
        "parcel-wise held-out R2\nYeo networks", BLUE)
    box(ax, (0.57, 0.15), 0.18, 0.28, "Complementary affect",
        "E34 | video + content\n34D versus A/V", ORANGE)
    box(ax, (0.82, 0.36), 0.16, 0.30, "Cortical transformation",
        "shared visuocognitive channel\n+ fine-grained affect", CHARCOAL)

    arrow(ax, (0.20, 0.71), (0.29, 0.55), BLUE)
    arrow(ax, (0.20, 0.29), (0.29, 0.47), GREEN)
    arrow(ax, (0.48, 0.54), (0.57, 0.70), MAGENTA)
    arrow(ax, (0.48, 0.45), (0.57, 0.29), MAGENTA)
    arrow(ax, (0.75, 0.70), (0.82, 0.56), BLUE)
    arrow(ax, (0.75, 0.29), (0.82, 0.46), ORANGE)
    ax.text(0.5, 0.96, "Independent foundation models reveal shared and transformed affective information",
            ha="center", va="top", fontsize=15, fontweight="bold", color=CHARCOAL)
    return save_figure(fig, output_dir, "figure_1_framework")


def locate_shared_result():
    base = ROOT / "study1/data/corrected_reanalysis"
    candidates = [
        ("permutation-confirmed", base / "shared_alignment_confirm/brain_alignment_vjepa2_pretrained.npz"),
        ("descriptive-screen", base / "shared_alignment_screen/brain_alignment_vjepa2_pretrained.npz"),
    ]
    return next(((status, path) for status, path in candidates if path.is_file()), (None, None))


def figure_shared(output_dir: Path):
    status, path = locate_shared_result()
    if path is None:
        return None, {"status": "missing", "expected": "corrected shared alignment"}
    with np.load(path) as payload:
        r2 = np.asarray(payload["seq_r2_raw"], dtype=float)
        corr = np.asarray(payload["seq_pearson_r"], dtype=float)
        cumulative = np.asarray(payload["cumulative_variance"], dtype=float)
        q = np.asarray(payload["seq_q_raw"], dtype=float)
        n_perm = int(payload["n_perm"])

    n_show = min(20, len(r2))
    pcs = np.arange(1, n_show + 1)
    colors = np.where(r2[:n_show] > 0, BLUE, LIGHT_GRAY)
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), gridspec_kw={"width_ratios": [1.4, 1.4, 1.0]})

    axes[0].bar(pcs, r2[:n_show], color=colors, edgecolor="none")
    axes[0].axhline(0, color=CHARCOAL, linewidth=0.9)
    axes[0].set(xlabel="V-JEPA2 principal component", ylabel="Held-out raw $R^2$",
                title="Corrected Brain-JEPA -> V-JEPA2")
    axes[0].set_xticks([1, 4, 8, 12, 16, 20])
    finite_q = np.isfinite(q[:n_show])
    for x, y, q_value in zip(pcs[finite_q], r2[:n_show][finite_q], q[:n_show][finite_q]):
        if q_value < 0.05 and y > 0:
            axes[0].text(x, y + max(np.nanmax(r2[:n_show]), 0.01) * 0.035, "*",
                         ha="center", va="bottom", fontsize=12)

    axes[1].bar(pcs, corr[:n_show], color=np.where(corr[:n_show] > 0, GREEN, LIGHT_GRAY))
    axes[1].axhline(0, color=CHARCOAL, linewidth=0.9)
    axes[1].set(xlabel="V-JEPA2 principal component", ylabel="Held-out Pearson $r$",
                title="Cross-domain correlation")
    axes[1].set_xticks([1, 4, 8, 12, 16, 20])

    axes[2].plot(pcs, cumulative[:n_show] * 100, marker="o", markersize=3.5,
                 linewidth=2, color=MAGENTA)
    axes[2].set(xlabel="Number of video PCs", ylabel="Cumulative video variance (%)",
                title="Video variance retained")
    axes[2].set_xticks([1, 4, 8, 12, 16, 20])
    axes[2].grid(axis="y", color=LIGHT_GRAY, linewidth=0.8)

    positive = int(np.sum(r2 > 0))
    confirmed = int(np.sum(np.isfinite(q) & (q < 0.05) & (r2 > 0)))
    label = f"{status.replace('-', ' ')} | permutations={n_perm:,} | positive raw R2={positive}"
    if n_perm:
        label += f" | positive R2 and FDR q<.05={confirmed}"
    fig.suptitle(label, fontsize=11, color=MID_GRAY, y=1.02)
    fig.tight_layout()
    files = save_figure(fig, output_dir, "figure_2_corrected_shared_channel")
    return files, {
        "status": "complete" if status == "permutation-confirmed" else "provisional",
        "evidence_status": status,
        "source": str(path),
        "n_perm": n_perm,
        "positive_r2_count": positive,
        "fdr_count": confirmed if n_perm else None,
        "top_raw_r2": [
            {"pc": int(i + 1), "r2": float(r2[i]), "pearson_r": float(corr[i])}
            for i in np.argsort(r2)[::-1][:5]
        ],
    }


def q_text(value):
    if not np.isfinite(value):
        return "q=n/a"
    return "q<.001" if value < 0.001 else f"q={value:.3f}"


def benjamini_hochberg(values):
    """Return Benjamini-Hochberg adjusted p-values, preserving NaNs."""
    values = np.asarray(values, dtype=float)
    adjusted = np.full(values.shape, np.nan, dtype=float)
    finite = np.flatnonzero(np.isfinite(values))
    if not len(finite):
        return adjusted
    order = finite[np.argsort(values[finite])]
    ranked = values[order] * len(order) / np.arange(1, len(order) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted[order] = np.minimum(ranked, 1.0)
    return adjusted


def figure_content_affect(output_dir: Path):
    source = ROOT / "study1/results/content_affect_partition"
    group_path = source / "map_statistics_group.csv"
    network_path = source / "network_summary_subjectwise.csv"
    if not group_path.is_file() or not network_path.is_file():
        return None, {"status": "missing", "expected": str(source)}
    group = pd.read_csv(group_path).set_index("map")
    network = pd.read_csv(network_path)
    contrasts = ["unique_e34_vc", "fine_grained_vs_av", "resolution_34d_vs_2d"]
    labels = ["E34 | video + content", "34D > arousal-valence", "34D > emotion PCA-2D"]
    colors = [ORANGE, GREEN, MAGENTA]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), gridspec_kw={"width_ratios": [1.0, 1.0, 1.6]})
    y = np.arange(len(contrasts))

    means = group.loc[contrasts, "cortical_mean"].to_numpy()
    low = group.loc[contrasts, "cortical_ci_low"].to_numpy()
    high = group.loc[contrasts, "cortical_ci_high"].to_numpy()
    axes[0].errorbar(means, y, xerr=np.vstack([means - low, high - means]), fmt="none",
                     ecolor=CHARCOAL, capsize=3, linewidth=1.5)
    axes[0].scatter(means, y, s=65, c=colors, zorder=3)
    axes[0].axvline(0, color=MID_GRAY, linewidth=0.9)
    axes[0].set_yticks(y, labels)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Cortical mean held-out delta $R^2$")
    axes[0].set_title("Complementary affective variance")
    for i, name in enumerate(contrasts):
        axes[0].text(high[i], i - 0.18, q_text(group.loc[name, "cortical_q_fdr"]), fontsize=8)

    hmean = group.loc[contrasts, "transmodal_minus_visual"].to_numpy()
    hlow = group.loc[contrasts, "hierarchy_ci_low"].to_numpy()
    hhigh = group.loc[contrasts, "hierarchy_ci_high"].to_numpy()
    axes[1].errorbar(hmean, y, xerr=np.vstack([hmean - hlow, hhigh - hmean]), fmt="none",
                     ecolor=CHARCOAL, capsize=3, linewidth=1.5)
    axes[1].scatter(hmean, y, s=65, c=colors, zorder=3)
    axes[1].axvline(0, color=MID_GRAY, linewidth=0.9)
    axes[1].set_yticks(y, ["" for _ in y])
    axes[1].invert_yaxis()
    axes[1].set_xlabel("(Control + Default) / 2 - Visual")
    axes[1].set_title("Relative transmodal enrichment")
    for i, name in enumerate(contrasts):
        axes[1].text(hhigh[i], i - 0.18, q_text(group.loc[name, "hierarchy_q_fdr"]), fontsize=8)

    width = 0.23
    x = np.arange(len(NETWORKS))
    for offset, name, label, color in zip([-width, 0, width], contrasts, labels, colors):
        subset = network[network["map"] == name]
        values = [subset.loc[subset["network"] == net, "mean"].to_numpy() for net in NETWORKS]
        means_net = np.array([np.mean(v) for v in values])
        sems = np.array([np.std(v, ddof=1) / np.sqrt(len(v)) for v in values])
        axes[2].bar(x + offset, means_net, width=width, yerr=sems, capsize=2,
                    color=color, label=label)
    axes[2].axhline(0, color=CHARCOAL, linewidth=0.8)
    axes[2].set_xticks(x, NETWORKS, rotation=28, ha="right")
    axes[2].set_ylabel("Held-out delta $R^2$")
    axes[2].set_title("Fine-grained gain across Yeo networks")
    axes[2].legend(frameon=False, loc="upper left")
    fig.tight_layout()
    files = save_figure(fig, output_dir, "figure_3_content_affect_partition")

    copied = []
    for suffix in ("png", "pdf"):
        original = source / f"content_affect_brain_maps.{suffix}"
        if original.is_file():
            target = output_dir / f"figure_3b_content_affect_brain_maps.{suffix}"
            shutil.copy2(original, target)
            copied.append(target)
    return files + copied, {
        "status": "complete",
        "source": str(source),
        "video_content_mean_r2": float(group.loc["video_content", "cortical_mean"]),
        "contrasts": {
            name: {
                "mean_delta_r2": float(group.loc[name, "cortical_mean"]),
                "cortical_q_fdr": float(group.loc[name, "cortical_q_fdr"]),
                "transmodal_minus_visual": float(group.loc[name, "transmodal_minus_visual"]),
                "hierarchy_q_fdr": float(group.loc[name, "hierarchy_q_fdr"]),
            }
            for name in contrasts
        },
    }


def mean_column(frame):
    for name in ("mean_value", "mean"):
        if name in frame.columns:
            return name
    raise ValueError("Network summary has no mean column")


def figure_corrected_cortex(output_dir: Path):
    source = ROOT / "study1/results/corrected_reanalysis/cortical_transformation"
    network_path = source / "network_summary_subjectwise.csv"
    stats_path = source / "hierarchy_group_statistics.csv"
    brain_png = source / "cortical_brain_maps.png"
    if not network_path.is_file() or not stats_path.is_file() or not brain_png.is_file():
        return None, {"status": "missing", "expected": str(source)}
    network = pd.read_csv(network_path)
    stats = pd.read_csv(stats_path)
    if "hierarchy_q_fdr" not in stats.columns:
        stats["hierarchy_q_fdr"] = benjamini_hochberg(stats["hierarchy_p"])
    stats = stats.set_index("map")
    value_col = mean_column(network)
    maps = ["shared", "unique_e34_shared", "fine_grained_advantage"]
    labels = ["Shared channel", "E34 | shared", "34D > arousal-valence"]
    colors = [BLUE, ORANGE, GREEN]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.0))
    for ax, map_name, label, color in zip(axes, maps, labels, colors):
        subset = network[network["map"] == map_name]
        values = [subset.loc[subset["network"] == net, value_col].to_numpy() for net in NETWORKS]
        means = np.array([np.mean(v) for v in values])
        sems = np.array([np.std(v, ddof=1) / np.sqrt(len(v)) for v in values])
        x = np.arange(len(NETWORKS))
        ax.bar(x, means, yerr=sems, color=color, alpha=0.88, capsize=2)
        for xi, vals in zip(x, values):
            ax.scatter(np.full(len(vals), xi), vals, s=13, color=CHARCOAL, alpha=0.45, zorder=3)
        ax.axhline(0, color=CHARCOAL, linewidth=0.8)
        ax.set_xticks(x, NETWORKS, rotation=30, ha="right")
        ax.set_ylabel("Held-out $R^2$ or delta $R^2$")
        suffix = ""
        if map_name in stats.index:
            direction = "visual - transmodal" if map_name == "shared" else "transmodal - visual"
            suffix = f"\n{direction}: {q_text(stats.loc[map_name, 'hierarchy_q_fdr'])}"
        ax.set_title(label + suffix)
    fig.tight_layout()
    files = save_figure(fig, output_dir, "figure_4_corrected_cortical_networks")
    for suffix in ("png", "pdf"):
        original = source / f"cortical_brain_maps.{suffix}"
        if original.is_file():
            target = output_dir / f"figure_4b_corrected_cortical_brain_maps.{suffix}"
            shutil.copy2(original, target)
            files.append(target)
    return files, {"status": "complete", "source": str(source)}


def locate_consensus():
    base = ROOT / "study1/results/brain_encoder_validation"
    candidates = [base / "consensus", base]
    for candidate in candidates:
        if (candidate / "pretrained_vs_scratch.csv").is_file() and "smoke" not in candidate.parts:
            return candidate
    return None


def figure_encoder_consensus(output_dir: Path):
    source = locate_consensus()
    if source is None:
        return None, {"status": "missing", "expected": "full brain-encoder consensus"}
    delta = pd.read_csv(source / "pretrained_vs_scratch.csv")
    targets = ["raw_vjepa2", "emotion_34d", "arousal_valence"]
    target_labels = ["V-JEPA2", "Fine-grained emotion", "Arousal-valence"]
    families = list(dict.fromkeys(delta["family"]))
    palette = [BLUE, GREEN, ORANGE, MAGENTA]
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.9), sharex=True)
    for ax, target, target_label in zip(axes, targets, target_labels):
        subset = delta[delta["target"] == target]
        values = [subset.loc[subset["family"] == family, "pretrained_minus_scratch"].to_numpy()
                  for family in families]
        means = np.array([np.mean(v) for v in values])
        sems = np.array([np.std(v, ddof=1) / np.sqrt(len(v)) for v in values])
        x = np.arange(len(families))
        ax.bar(x, means, yerr=sems, color=palette[: len(families)], capsize=2)
        for xi, vals in zip(x, values):
            ax.scatter(np.full(len(vals), xi), vals, s=16, color=CHARCOAL, alpha=0.55)
        ax.axhline(0, color=CHARCOAL, linewidth=0.9)
        ax.set_xticks(x, [f.replace("_", "\n") for f in families], rotation=25, ha="right")
        ax.set_ylabel("Pretrained - scratch held-out $R^2$")
        ax.set_title(target_label)
    fig.tight_layout()
    files = save_figure(fig, output_dir, "figure_5_brain_encoder_consensus")
    return files, {"status": "complete", "source": str(source), "families": families}


def file_record(path: Path):
    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
    }


def export_once(output_dir: Path, check_only=False):
    output_dir.mkdir(parents=True, exist_ok=True)
    style()
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "policy": "Corrected Brain-JEPA only for shared/cortical panels; no legacy fallback.",
        "panels": {},
    }
    builders = [
        ("framework", figure_framework),
        ("corrected_shared", figure_shared),
        ("content_affect", figure_content_affect),
        ("corrected_cortex", figure_corrected_cortex),
        ("encoder_consensus", figure_encoder_consensus),
    ]
    if check_only:
        status, shared_path = locate_shared_result()
        content_source = ROOT / "study1/results/content_affect_partition"
        cortex_source = ROOT / "study1/results/corrected_reanalysis/cortical_transformation"
        consensus_source = locate_consensus()
        checks = {
            "framework": ("available", None),
            "corrected_shared": (status or "missing", shared_path),
            "content_affect": (
                "available" if (content_source / "map_statistics_group.csv").is_file() else "missing",
                content_source,
            ),
            "corrected_cortex": (
                "available"
                if all((cortex_source / name).is_file() for name in (
                    "network_summary_subjectwise.csv",
                    "hierarchy_group_statistics.csv",
                    "cortical_brain_maps.png",
                ))
                else "missing",
                cortex_source,
            ),
            "encoder_consensus": (
                "available" if consensus_source is not None else "missing",
                consensus_source,
            ),
        }
        for name, (status, source) in checks.items():
            manifest["panels"][name] = {
                "status": status,
                "source": str(source) if source is not None else None,
                "files": [],
            }
            print(f"[{status}] {name}" + (f": {source}" if source else ""))
        return manifest

    for name, builder in builders:
        try:
            if name == "framework":
                files = builder(output_dir)
                info = {"status": "complete"}
            else:
                files, info = builder(output_dir)
            info["files"] = [file_record(path) for path in (files or [])]
            manifest["panels"][name] = info
            print(f"[{info['status']}] {name}")
        except Exception as error:
            manifest["panels"][name] = {"status": "error", "error": repr(error), "files": []}
            print(f"[error] {name}: {error}")

    manifest_path = output_dir / "poster_figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    lines = ["# CCN Poster Figure Manifest", "", f"Generated: {manifest['generated_utc']}", ""]
    for name, info in manifest["panels"].items():
        lines.append(f"- **{name}**: {info['status']}")
        if info.get("expected"):
            lines.append(f"  - waiting for: `{info['expected']}`")
        for record in info.get("files", []):
            lines.append(f"  - `{record['path']}`")
    (output_dir / "poster_figure_manifest.md").write_text("\n".join(lines) + "\n")
    return manifest


def main():
    args = parse_args()
    if args.watch_minutes < 0 or args.interval_seconds < 10:
        raise ValueError("watch-minutes must be >=0 and interval-seconds must be >=10")
    if args.check_only:
        export_once(args.output_dir, check_only=True)
        return
    deadline = time.time() + args.watch_minutes * 60
    while True:
        manifest = export_once(args.output_dir)
        missing = [name for name, info in manifest["panels"].items() if info["status"] != "complete"]
        print(f"Poster export complete. Missing: {missing or 'none'}")
        if args.watch_minutes == 0 or time.time() >= deadline or not missing:
            break
        sleep_for = min(args.interval_seconds, max(0, int(deadline - time.time())))
        if sleep_for <= 0:
            break
        print(f"Watching for running outputs; next check in {sleep_for}s")
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()
