"""
Build Horikawa conversation JSONL in BrainVLM-compatible format.

Output format mirrors the ABCD sample data structure in BrainVLM/UMBRELLA_qwen/sample_data/
but for emotion VQA on Horikawa naturalistic fMRI.

Each conversation = one (subject, stimulus) fMRI sample + emotion question.

Produces train / val / test splits aligned with the 5-fold stim-stratified CV.

Output:
  output/brainvlm_conversations/<split>/sub-XX/<task>_conversations.jsonl
"""
import argparse
import json
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/shared/code/brainvlm")

EmoBrain_ROOT = Path("/pscratch/sd/s/sjmoon/EmoBrain")
DATA = EmoBrain_ROOT / "data"
FMRI_ROOT = EmoBrain_ROOT / "output/brainvlm_fmri"  # output of convert_horikawa_fmri.py
OUT_ROOT = EmoBrain_ROOT / "output/brainvlm_conversations"


def build_emotion_va_prompt() -> str:
    return ("<Clinical_Task>\n"
            "You are an expert AI affective neuroscientist. Analyze the fMRI activity "
            "recorded while the subject viewed a short naturalistic video clip and "
            "describe the elicited emotional experience.\n"
            "</Clinical_Task>\n\n"
            "<Subject_Data>\n"
            "  <Modality type=\"functional MRI (4D BOLD across the whole brain)\">")


def build_va_question(target: str = "VA") -> str:
    if target == "VA":
        return ("\n  </Modality>\n</Subject_Data>\n\n"
                "<Question>\n"
                "Predict the elicited emotional experience along two continuous scales: "
                "valence (1 = very negative, 5 = very positive) and arousal (1 = very calm, "
                "5 = very intense). Provide the prediction in the following XML format:\n"
                "<Emotion_Analysis>\n"
                "<Valence>...</Valence>\n"
                "<Arousal>...</Arousal>\n"
                "<Caption>brief affective description</Caption>\n"
                "</Emotion_Analysis>\n"
                "</Question>")
    if target == "caption":
        return ("\n  </Modality>\n</Subject_Data>\n\n"
                "<Question>\n"
                "Provide a brief free-form description of the emotional experience evoked in "
                "the subject. Keep it concise and centred on affect.\n"
                "</Question>")
    raise ValueError(target)


def build_answer(row: pd.Series, target: str = "VA") -> str:
    """Build assistant answer using ground truth labels from cowen_horikawa_labels.csv."""
    if target == "VA":
        v = row["valence_score"]
        a = row["arousal_score"]
        return ("<Emotion_Analysis>\n"
                f"<Valence>{v:.2f}</Valence>\n"
                f"<Arousal>{a:.2f}</Arousal>\n"
                "<Caption>(ground-truth caption placeholder)</Caption>\n"
                "</Emotion_Analysis>")
    raise ValueError(target)


def build_conversation_record(subj: str, stim_num: int, fmri_path: str,
                              row: pd.Series, target: str = "VA") -> dict:
    sys_prompt = build_emotion_va_prompt()
    question = build_va_question(target)
    answer = build_answer(row, target)
    return {
        "task_id": f"emotion_{target}_{subj}_stimulus_{stim_num}",
        "task_type": "Emotion_VQA_Horikawa",
        "subject_ids": [subj],
        "conversations": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": sys_prompt},
                    {"type": "image", "modality": "fMRI", "image_path": fmri_path},
                    {"type": "text", "text": question},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": answer}],
            },
        ],
        "metadata": {
            "subject": subj,
            "stim_num": int(stim_num),
            "valence": float(row["valence_score"]),
            "arousal": float(row["arousal_score"]),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", default="sub-01,sub-02,sub-03,sub-04,sub-05")
    ap.add_argument("--fmri_padding", default="zero",
                    help="must match the padding used in convert_horikawa_fmri.py")
    ap.add_argument("--target", default="VA", choices=["VA", "caption"])
    ap.add_argument("--fold_csv", default=str(DATA / "horikawa_5fold.csv"))
    ap.add_argument("--label_csv", default=str(DATA / "cowen_horikawa_labels.csv"))
    ap.add_argument("--limit", type=int, default=None,
                    help="if set, only first N stim (smoke test)")
    args = ap.parse_args()

    subjects = [s.strip() for s in args.subjects.split(",")]

    # Load labels + folds
    labels = pd.read_csv(args.label_csv)
    labels = labels.rename(columns={"stimulus_num": "stim_str", "stim_num_int": "stimulus_num"})
    folds = pd.read_csv(args.fold_csv)

    fmri_dir = FMRI_ROOT / f"pad-{args.fmri_padding}"
    out_root = OUT_ROOT / f"pad-{args.fmri_padding}_{args.target}"

    # Build 5 splits (each fold is test, others are train; we emit per-fold variants)
    for test_fold in range(1, 6):
        val_fold = (test_fold % 5) + 1
        train_folds = [f for f in range(1, 6) if f not in (test_fold, val_fold)]

        split_assign = folds.copy()
        split_assign["split"] = "train"
        split_assign.loc[split_assign["fold"].isin([test_fold]), "split"] = "test"
        split_assign.loc[split_assign["fold"].isin([val_fold]), "split"] = "val"

        for split in ["train", "val", "test"]:
            stim_set = split_assign[split_assign["split"] == split]["stimulus_num"].tolist()
            for subj in subjects:
                out_dir = out_root / f"fold{test_fold}" / split
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = out_dir / f"{subj}_conversations.jsonl"
                n_written = 0
                with open(out_file, "w") as f:
                    for stim_num in stim_set:
                        if args.limit and n_written >= args.limit:
                            break
                        fmri_path = fmri_dir / subj / f"stimulus_{stim_num}.pt"
                        if not fmri_path.exists():
                            continue
                        row = labels[labels["stimulus_num"] == stim_num]
                        if len(row) == 0:
                            continue
                        row = row.iloc[0]
                        rec = build_conversation_record(subj, stim_num, str(fmri_path), row,
                                                       target=args.target)
                        f.write(json.dumps(rec) + "\n")
                        n_written += 1
                if test_fold == 1 and split == "train":  # avoid log spam, only first split
                    print(f"  fold{test_fold}/{split:5s}/{subj}: {n_written} samples → {out_file.name}")
    print(f"\n[done] all splits at: {out_root}")


if __name__ == "__main__":
    main()
