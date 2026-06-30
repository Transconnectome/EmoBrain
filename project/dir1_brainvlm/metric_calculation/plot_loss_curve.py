"""Plot loss curve from HuggingFace Trainer state.

Reads `trainer_state.json` (HF Trainer 의 표준 log file) from given output_dir,
extracts train/eval loss + token_acc 같은 metric, plots to PNG.

Input.
  <output_dir>/checkpoint-<step>/trainer_state.json   (학습 중간 저장)
  또는 <output_dir>/trainer_state.json                  (학습 끝나면 root 에 저장)

Output.
  <output_dir>/loss_curve.png
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def find_trainer_state(output_dir: Path) -> Path:
    """Find latest trainer_state.json (root 또는 latest checkpoint)."""
    root = output_dir / "trainer_state.json"
    if root.exists():
        return root
    ckpts = sorted(
        output_dir.glob("checkpoint-*"),
        key=lambda p: int(p.name.split("-")[-1]),
    )
    if not ckpts:
        raise FileNotFoundError(f"no trainer_state.json or checkpoint-* under {output_dir}")
    return ckpts[-1] / "trainer_state.json"


def extract_loss(state_path: Path) -> dict[str, list]:
    """Returns dict of {metric_name: list of (step, value)}."""
    state = json.loads(state_path.read_text())
    log_history = state.get("log_history", [])
    series: dict[str, list[tuple[int, float]]] = {}
    for entry in log_history:
        step = entry.get("step", 0)
        for k, v in entry.items():
            if k in ("step", "epoch") or not isinstance(v, (int, float)):
                continue
            series.setdefault(k, []).append((step, float(v)))
    return series


def plot_loss_curve(series: dict, out_path: Path, title: str = "") -> None:
    """One subplot per metric. 2-col layout."""
    metrics = sorted(series.keys())
    n = len(metrics)
    if n == 0:
        print("[plot] no metrics found in trainer_state.json log_history. skip.")
        return
    ncols = 2
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(10, 3 * nrows), squeeze=False)
    for ax, m in zip(axes.flat, metrics):
        steps, vals = zip(*series[m])
        ax.plot(steps, vals, marker="o", markersize=3, linewidth=1)
        ax.set_title(m, fontsize=10)
        ax.set_xlabel("step")
        ax.grid(alpha=0.3)
    for ax in axes.flat[n:]:
        ax.set_visible(False)
    if title:
        fig.suptitle(title, fontsize=12, y=1.005)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] saved {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, required=True,
                        help="HF Trainer 의 output_dir (예. dir1_brainvlm/output/horikawa_emotion_cat34_top1_SMOKE)")
    parser.add_argument("--out-png", type=str, default=None,
                        help="output PNG path. default = <output_dir>/loss_curve.png")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    state_path = find_trainer_state(out_dir)
    print(f"[plot] reading {state_path}")
    series = extract_loss(state_path)
    print(f"[plot] {len(series)} metrics: {list(series.keys())}")

    png_path = Path(args.out_png) if args.out_png else (out_dir / "loss_curve.png")
    plot_loss_curve(series, png_path, title=out_dir.name)


if __name__ == "__main__":
    main()
