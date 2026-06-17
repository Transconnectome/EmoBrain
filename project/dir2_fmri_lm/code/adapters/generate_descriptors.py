"""Descriptor CSV generator.

fMRI-LM 의 paired-text supervision 은 descriptors_rewritten/<type>_descriptors.csv 형식.
Reference. external/repos/fmri-lm/nbs_data/get_fmri_discriptor.py

이 파일은 emotion-specific descriptor 생성 가이드. 협업자가 dataset 별로 채워서 사용.

Output CSV schema (official 기준):
    columns: sample_id (str), text (str)
    rows: per sample text descriptor (1 sample = 1 row)

Emotion task 의 4 desc_type 후보 (fMRI-LM 의 fc/ica/gradient/graph 대신).
    - va_descriptor     valence/arousal 값을 자연어로
    - cat_descriptor    categorical emotion (top1, top-k>threshold) 자연어로
    - caption           외부 vision model caption (Qwen-VL 등)
    - mixed             위 셋을 모두 결합한 single descriptor
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


VA_TEMPLATE = "This brain response shows valence {v} and arousal {a}."
CAT_TEMPLATE_TOP1 = "The dominant emotional response is {top1}."
CAT_TEMPLATE_TOPK = "The activated emotions are: {tops}."
MIXED_TEMPLATE = (
    "{va} {cat} {caption}"
)


def make_va(va_df: pd.DataFrame, v_col: str, a_col: str, sample_col: str) -> pd.DataFrame:
    return pd.DataFrame({
        "sample_id": va_df[sample_col],
        "text": va_df.apply(lambda r: VA_TEMPLATE.format(v=f"{r[v_col]:.2f}", a=f"{r[a_col]:.2f}"), axis=1),
    })


def make_cat_top1(cat_df: pd.DataFrame, label_cols: list[str], sample_col: str) -> pd.DataFrame:
    arr = cat_df[label_cols].to_numpy()
    top1 = [label_cols[i] for i in arr.argmax(axis=1)]
    return pd.DataFrame({"sample_id": cat_df[sample_col], "text": [CAT_TEMPLATE_TOP1.format(top1=t) for t in top1]})


def make_cat_topk(cat_df: pd.DataFrame, label_cols: list[str], sample_col: str, threshold: float = 0.10) -> pd.DataFrame:
    arr = cat_df[label_cols].to_numpy()
    rows = []
    for i in range(arr.shape[0]):
        active = [label_cols[k] for k in range(len(label_cols)) if arr[i, k] >= threshold]
        if not active:
            active = [label_cols[int(arr[i].argmax())]]
        rows.append(CAT_TEMPLATE_TOPK.format(tops=", ".join(active)))
    return pd.DataFrame({"sample_id": cat_df[sample_col], "text": rows})


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--va-csv", help="rows of (sample_id, valence, arousal)")
    p.add_argument("--cat-csv", help="rows of (sample_id, <K emotion-name columns>) soft distribution")
    p.add_argument("--label-cols-file", help="text file: one label name per line, matches cat-csv columns")
    p.add_argument("--sample-col", default="sample_id")
    p.add_argument("--v-col", default="valence")
    p.add_argument("--a-col", default="arousal")
    p.add_argument("--out-dir", required=True, help="data/<DATASET>/fmri/<ATLAS>/descriptors_rewritten/")
    p.add_argument("--threshold", type=float, default=0.10)
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.va_csv:
        va_df = pd.read_csv(args.va_csv)
        df = make_va(va_df, args.v_col, args.a_col, args.sample_col)
        df.to_csv(out / "va_descriptors.csv", index=False)
        print(f"[desc] wrote {len(df)} va descriptors")

    if args.cat_csv and args.label_cols_file:
        label_cols = [ln.strip() for ln in open(args.label_cols_file) if ln.strip()]
        cat_df = pd.read_csv(args.cat_csv)
        df_t1 = make_cat_top1(cat_df, label_cols, args.sample_col)
        df_t1.to_csv(out / "cat_top1_descriptors.csv", index=False)
        df_tk = make_cat_topk(cat_df, label_cols, args.sample_col, threshold=args.threshold)
        df_tk.to_csv(out / "cat_topk_descriptors.csv", index=False)
        print(f"[desc] wrote {len(df_t1)} cat_top1 + cat_topk descriptors (threshold {args.threshold})")


if __name__ == "__main__":
    main()
