#!/usr/bin/env python3
"""Run TRIBE v2 on Horikawa/Cowen emotional video stimuli.

The first NetFeeliX use case is deliberately simple:

1. choose a few Horikawa/Cowen stimulus ids,
2. run TRIBE v2 in video-only mode,
3. save fsaverage5 predicted brain responses,
4. save static cortical heatmaps for mean and absolute-mean activation.

This script does not compare against observed fMRI yet. It creates the
stimulus-side teacher outputs needed for the later TRIBE-SwiFT alignment track.
"""

from __future__ import annotations

import argparse
import json
import os
import traceback
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_VIDEO_DIR = Path("/pscratch/sd/s/sjmoon/CCN_Emotion/videos/CowenEmotionVideos")
DEFAULT_META = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/"
    "horikawa_filtered_MNI_to_TRs/metadata/"
    "horikawa_meta_data_with_dimension_binary.csv"
)


def parse_stimulus_id(value: str | int) -> int:
    text = str(value).strip()
    if text.startswith("stimulus_"):
        text = text.split("_", 1)[1]
    return int(text)


def stimulus_to_video(video_dir: Path, stimulus_id: int) -> Path:
    path = video_dir / f"{stimulus_id:04d}.mp4"
    if not path.exists():
        raise FileNotFoundError(f"Missing Horikawa/Cowen video: {path}")
    return path


def select_stimuli(meta_path: Path, selector: str, n: int) -> list[int]:
    df = pd.read_csv(meta_path)
    df["stimulus_id"] = df["stimulus_num"].map(parse_stimulus_id)
    if selector == "top_valence":
        picked = df.sort_values("valence_score", ascending=False).head(n)
    elif selector == "low_valence":
        picked = df.sort_values("valence_score", ascending=True).head(n)
    elif selector == "top_arousal":
        picked = df.sort_values("arousal_score", ascending=False).head(n)
    elif selector == "low_arousal":
        picked = df.sort_values("arousal_score", ascending=True).head(n)
    else:
        raise ValueError(f"Unknown selector: {selector}")
    return picked["stimulus_id"].astype(int).tolist()


def all_stimuli(meta_path: Path) -> list[int]:
    df = pd.read_csv(meta_path)
    return sorted(df["stimulus_num"].map(parse_stimulus_id).astype(int).tolist())


def build_video_only_events(video_path: Path) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "type": "Video",
                "filepath": str(video_path),
                "start": 0,
                "timeline": "default",
                "subject": "default",
            }
        ]
    )


def save_heatmap(preds: np.ndarray, out_png: Path, summary: str, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if summary == "mean":
        signal = preds.mean(axis=0)
        symmetric = True
    elif summary == "absmean":
        signal = np.abs(preds).mean(axis=0)
        symmetric = False
    elif summary == "maxabs":
        signal = preds[np.argmax(np.abs(preds).mean(axis=1))]
        symmetric = True
    else:
        raise ValueError(f"Unknown heatmap summary: {summary}")

    out_png.parent.mkdir(parents=True, exist_ok=True)

    def save_fallback(reason: str) -> None:
        fig, axes = plt.subplots(2, 1, figsize=(10, 5), gridspec_kw={"height_ratios": [2, 1]})
        im = axes[0].imshow(preds, aspect="auto", cmap="coolwarm")
        axes[0].set_title(title)
        axes[0].set_xlabel("fsaverage5 vertex")
        axes[0].set_ylabel("kept segment")
        fig.colorbar(im, ax=axes[0], shrink=0.85)
        axes[1].plot(signal, linewidth=0.6)
        axes[1].set_xlabel("fsaverage5 vertex")
        axes[1].set_ylabel(summary)
        axes[1].set_title(f"Fallback plot: {reason}")
        fig.tight_layout()
        fig.savefig(out_png, dpi=180, bbox_inches="tight")
        plt.close(fig)
        print(f"WARNING: {reason}; saved fallback heatmap instead: {out_png}")

    try:
        from tribev2.plotting.cortical import PlotBrainNilearn
    except ModuleNotFoundError as exc:
        save_fallback(f"optional TRIBE plotting dependency `{exc.name}` is not installed")
        return

    try:
        plotter = PlotBrainNilearn(mesh="fsaverage5")
        fig, axes = plt.subplots(
            2,
            2,
            figsize=(8, 6),
            subplot_kw={"projection": "3d"},
            gridspec_kw={"wspace": 0, "hspace": -0.15},
        )
        plotter.plot_surf(
            signal,
            views=["left", "right", "medial_left", "medial_right"],
            axes=axes.flatten(),
            norm_percentile=98,
            symmetric_cbar=symmetric,
            colorbar=True,
            colorbar_title=summary,
            cmap="cold_hot" if symmetric else "hot",
        )
        fig.suptitle(title, fontsize=12)
        fig.savefig(out_png, dpi=180, bbox_inches="tight")
        plt.close(fig)
    except Exception as exc:
        try:
            plt.close(fig)
        except Exception:
            pass
        save_fallback(f"TRIBE cortical surface plotting failed ({type(exc).__name__}: {exc})")


def read_summary(stim_dir: Path) -> dict | None:
    summary_path = stim_dir / "summary.json"
    pred_path = stim_dir / "tribe_preds_fsaverage5.npy"
    if not summary_path.exists() or not pred_path.exists():
        return None
    return json.loads(summary_path.read_text(encoding="utf-8"))


def write_manifest(out_dir: Path) -> None:
    summaries = []
    for summary_path in sorted(out_dir.glob("stimulus_*/summary.json")):
        stim_dir = summary_path.parent
        if not (stim_dir / "tribe_preds_fsaverage5.npy").exists():
            continue
        summaries.append(json.loads(summary_path.read_text(encoding="utf-8")))
    summaries = sorted(summaries, key=lambda row: int(row["stimulus_id"]))
    (out_dir / "manifest.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TRIBE v2 on Horikawa videos.")
    parser.add_argument(
        "--checkpoint",
        default="facebook/tribev2",
        help="HuggingFace repo id or local checkpoint directory with config.yaml/best.ckpt.",
    )
    parser.add_argument(
        "--cache-folder",
        default="/pscratch/sd/s/sjmoon/NetFeeliX/setup/results/tribe_cache",
    )
    parser.add_argument("--video-dir", default=str(DEFAULT_VIDEO_DIR))
    parser.add_argument("--meta-path", default=str(DEFAULT_META))
    parser.add_argument("--out-dir", default="setup/results/tribe_horikawa")
    parser.add_argument("--device", default="auto", help="auto, cuda, or cpu")
    parser.add_argument(
        "--stimuli",
        nargs="*",
        default=[],
        help="Stimulus ids, e.g. 10 stimulus_1423 2002. Overrides --selector.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all stimuli listed in the metadata file.",
    )
    parser.add_argument(
        "--selector",
        default="top_arousal",
        choices=["top_valence", "low_valence", "top_arousal", "low_arousal"],
    )
    parser.add_argument("--n", type=int, default=3, help="Number selected by selector.")
    parser.add_argument(
        "--skip-heatmaps",
        action="store_true",
        help="Only save predictions and metadata.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recompute stimuli even if prediction and summary files already exist.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop immediately when one stimulus fails. By default, write error.json and continue.",
    )
    args = parser.parse_args()

    os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-netfeelix")

    from tribev2 import TribeModel

    root = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    video_dir = Path(args.video_dir)
    if args.stimuli:
        stimulus_ids = [parse_stimulus_id(x) for x in args.stimuli]
    elif args.all:
        stimulus_ids = all_stimuli(Path(args.meta_path))
    else:
        stimulus_ids = select_stimuli(Path(args.meta_path), args.selector, args.n)

    print(f"Planned stimuli: {len(stimulus_ids)}")

    model = TribeModel.from_pretrained(
        args.checkpoint,
        cache_folder=args.cache_folder,
        device=args.device,
    )

    for idx, stimulus_id in enumerate(stimulus_ids, start=1):
        video_path = stimulus_to_video(video_dir, stimulus_id)
        stim_dir = out_dir / f"stimulus_{stimulus_id:04d}"
        stim_dir.mkdir(parents=True, exist_ok=True)

        cached = read_summary(stim_dir)
        if cached is not None and not args.force:
            print(f"[{idx}/{len(stimulus_ids)}] Skip existing stimulus {stimulus_id:04d}: {stim_dir}")
            write_manifest(out_dir)
            continue

        try:
            events = build_video_only_events(video_path)
            events.to_csv(stim_dir / "events_video_only.csv", index=False)

            print(f"[{idx}/{len(stimulus_ids)}] Running stimulus {stimulus_id:04d}: {video_path}", flush=True)
            preds, segments = model.predict(events)
            np.save(stim_dir / "tribe_preds_fsaverage5.npy", preds)

            segment_rows = [
                {"segment_index": i, "start": getattr(seg, "start", None), "duration": getattr(seg, "duration", None)}
                for i, seg in enumerate(segments)
            ]
            pd.DataFrame(segment_rows).to_csv(stim_dir / "segments.csv", index=False)

            stats = {
                "stimulus_id": stimulus_id,
                "video_path": str(video_path),
                "pred_shape": list(preds.shape),
                "pred_mean": float(np.mean(preds)),
                "pred_std": float(np.std(preds)),
                "pred_absmean": float(np.mean(np.abs(preds))),
            }
            (stim_dir / "summary.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

            if not args.skip_heatmaps:
                save_heatmap(
                    preds,
                    stim_dir / "heatmap_mean.png",
                    summary="mean",
                    title=f"TRIBE v2 mean prediction: stimulus {stimulus_id:04d}",
                )
                save_heatmap(
                    preds,
                    stim_dir / "heatmap_absmean.png",
                    summary="absmean",
                    title=f"TRIBE v2 absolute mean prediction: stimulus {stimulus_id:04d}",
                )

            write_manifest(out_dir)
            print(f"Saved stimulus {stimulus_id:04d}: {stim_dir}", flush=True)
        except Exception as exc:
            error = {
                "stimulus_id": stimulus_id,
                "video_path": str(video_path),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            (stim_dir / "error.json").write_text(json.dumps(error, indent=2), encoding="utf-8")
            print(f"ERROR: stimulus {stimulus_id:04d} failed ({type(exc).__name__}: {exc})", flush=True)
            if args.stop_on_error:
                raise
            continue

    write_manifest(out_dir)
    print(f"Wrote manifest: {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
