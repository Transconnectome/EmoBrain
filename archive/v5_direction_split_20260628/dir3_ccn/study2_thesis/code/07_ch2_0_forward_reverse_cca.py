"""
Chapter 2-0: Video-Brain Embedding Alignment (2185 unique videos)

CCN 분석 재실행 (2196→2185 수정) + Raw fMRI 추가.
Chapter 2 본분석(Variance Partitioning)의 motivation.

분석:
  A. Forward PCA+Ridge: Brain → V-JEPA2/CLIP PC (뇌가 AI를 읽는가?)
  B. Reverse PCA+Ridge: V-JEPA2/CLIP → Brain PC (AI가 뇌를 읽는가?)
  C. CCA: Brain ↔ V-JEPA2/CLIP (공유 축은?)

"Forward는 되고 Reverse는 안 된다 → AI가 뇌를 놓치고 있다
 → Variance Partitioning으로 그 부분을 분리해야 한다"
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold
from sklearn.cross_decomposition import CCA
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
OUT  = BASE / "main/results"

# ── Load ──────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa = np.load(BASE / "video_embeddings/vjepa2_embeddings.npy").astype(np.float64)[:2185]
clip_emb = np.load(BASE / "video_embeddings/clip_embeddings.npy").astype(np.float64)[:2185]
fmri = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)[:, :2185, :]
fmri_mean = fmri.mean(axis=0)  # (2185, 450)
brain_jepa = np.load(BASE / "brain_embeddings/brain_jepa_embeddings.npy").astype(np.float64)[:, :2185, :]
bj_mean = brain_jepa.mean(axis=0)  # (2185, 768)

print(f"V-JEPA2: {vjepa.shape}, CLIP: {clip_emb.shape}")
print(f"Raw fMRI: {fmri_mean.shape}, Brain-JEPA: {bj_mean.shape}")

N_PC = 100
alphas = np.logspace(-2, 10, 20)

def forward_ridge(brain_data, model_data, model_name, brain_name, n_pc=20):
    """Brain → Model PC prediction. Returns R² per PC."""
    pca = PCA(n_components=n_pc, random_state=42)
    model_pcs = pca.fit_transform(model_data)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    r2_fwd = np.zeros(n_pc)
    r_fwd = np.zeros(n_pc)
    for i in range(n_pc):
        y_pred = np.zeros(brain_data.shape[0])
        for tr, te in kf.split(brain_data):
            sc = StandardScaler()
            X_tr = sc.fit_transform(brain_data[tr])
            X_te = sc.transform(brain_data[te])
            ridge = RidgeCV(alphas=alphas)
            ridge.fit(X_tr, model_pcs[tr, i])
            y_pred[te] = ridge.predict(X_te)
        r, _ = pearsonr(model_pcs[:, i], y_pred)
        ss_res = np.sum((model_pcs[:, i] - y_pred)**2)
        ss_tot = np.sum((model_pcs[:, i] - model_pcs[:, i].mean())**2)
        r2_fwd[i] = max(1 - ss_res/ss_tot, 0) if ss_tot > 0 else 0
        r_fwd[i] = r

    print(f"\n  Forward: {brain_name} → {model_name} PC")
    for i in range(min(10, n_pc)):
        if r2_fwd[i] > 0.005:
            print(f"    PC{i+1}: R²={r2_fwd[i]:.4f}, r={r_fwd[i]:.4f}")
    n_sig = (r2_fwd > 0.01).sum()
    print(f"    Significant (R²>0.01): {n_sig}/{n_pc}")
    return r2_fwd, r_fwd, pca.explained_variance_ratio_

def reverse_ridge(model_data, brain_data, model_name, brain_name, n_pc=20):
    """Model → Brain PC prediction."""
    pca = PCA(n_components=n_pc, random_state=42)
    brain_pcs = pca.fit_transform(brain_data)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    r2_rev = np.zeros(n_pc)
    for i in range(n_pc):
        y_pred = np.zeros(model_data.shape[0])
        for tr, te in kf.split(model_data):
            sc = StandardScaler()
            X_tr = sc.fit_transform(model_data[tr])
            X_te = sc.transform(model_data[te])
            ridge = RidgeCV(alphas=alphas)
            ridge.fit(X_tr, brain_pcs[tr, i])
            y_pred[te] = ridge.predict(X_te)
        ss_res = np.sum((brain_pcs[:, i] - y_pred)**2)
        ss_tot = np.sum((brain_pcs[:, i] - brain_pcs[:, i].mean())**2)
        r2_rev[i] = max(1 - ss_res/ss_tot, 0) if ss_tot > 0 else 0

    print(f"\n  Reverse: {model_name} → {brain_name} PC")
    for i in range(min(5, n_pc)):
        print(f"    PC{i+1} (var={pca.explained_variance_ratio_[i]*100:.1f}%): R²={r2_rev[i]:.4f}")
    n_sig = (r2_rev > 0.01).sum()
    print(f"    Significant (R²>0.01): {n_sig}/{n_pc}")
    return r2_rev, pca.explained_variance_ratio_

def run_cca(brain_data, model_data, model_name, brain_name, n_pca=50, n_cc=30):
    """CCA between brain and model."""
    sc_b = StandardScaler(); sc_m = StandardScaler()
    pca_b = PCA(n_components=n_pca, random_state=42)
    pca_m = PCA(n_components=n_pca, random_state=42)

    brain_pca = pca_b.fit_transform(sc_b.fit_transform(brain_data))
    model_pca = pca_m.fit_transform(sc_m.fit_transform(model_data))

    cca = CCA(n_components=n_cc, max_iter=1000)
    brain_cc, model_cc = cca.fit_transform(brain_pca, model_pca)

    cc_r = np.array([np.corrcoef(brain_cc[:, i], model_cc[:, i])[0, 1] for i in range(n_cc)])

    print(f"\n  CCA: {brain_name} ↔ {model_name} (PCA{n_pca} → CCA{n_cc})")
    for i in range(min(10, n_cc)):
        print(f"    CC{i+1}: r={cc_r[i]:.4f}")
    n_sub = (cc_r > 0.3).sum()
    print(f"    CCs with r>0.3: {n_sub}/{n_cc}")
    return cc_r

# ── A. Forward ────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("A. FORWARD: Brain → AI Model PC")
print("="*70)

fwd_raw_vj, fwd_raw_vj_r, _ = forward_ridge(fmri_mean, vjepa, "V-JEPA2", "Raw fMRI")
fwd_raw_cl, fwd_raw_cl_r, _ = forward_ridge(fmri_mean, clip_emb, "CLIP", "Raw fMRI")
fwd_bj_vj, fwd_bj_vj_r, _ = forward_ridge(bj_mean, vjepa, "V-JEPA2", "Brain-JEPA")
fwd_bj_cl, fwd_bj_cl_r, _ = forward_ridge(bj_mean, clip_emb, "CLIP", "Brain-JEPA")

# ── B. Reverse ────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("B. REVERSE: AI Model → Brain PC")
print("="*70)

rev_vj_raw, _ = reverse_ridge(vjepa, fmri_mean, "V-JEPA2", "Raw fMRI")
rev_cl_raw, _ = reverse_ridge(clip_emb, fmri_mean, "CLIP", "Raw fMRI")
rev_vj_bj, _ = reverse_ridge(vjepa, bj_mean, "V-JEPA2", "Brain-JEPA")

# ── C. CCA ────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("C. CCA: Brain ↔ AI Model")
print("="*70)

cca_raw_vj = run_cca(fmri_mean, vjepa, "V-JEPA2", "Raw fMRI")
cca_raw_cl = run_cca(fmri_mean, clip_emb, "CLIP", "Raw fMRI")
cca_bj_vj = run_cca(bj_mean, vjepa, "V-JEPA2", "Brain-JEPA")

# ── Summary ───────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"\nForward (brain-pred PCs with R²>0.01):")
print(f"  Raw→V-JEPA2: {(fwd_raw_vj>0.01).sum()}, Raw→CLIP: {(fwd_raw_cl>0.01).sum()}")
print(f"  BJ→V-JEPA2:  {(fwd_bj_vj>0.01).sum()},  BJ→CLIP:  {(fwd_bj_cl>0.01).sum()}")

print(f"\nReverse (R²>0.01):")
print(f"  V-JEPA2→Raw: {(rev_vj_raw>0.01).sum()}, CLIP→Raw: {(rev_cl_raw>0.01).sum()}")
print(f"  V-JEPA2→BJ:  {(rev_vj_bj>0.01).sum()}")

print(f"\nCCA (CCs with r>0.3):")
print(f"  Raw↔V-JEPA2: {(cca_raw_vj>0.3).sum()}, Raw↔CLIP: {(cca_raw_cl>0.3).sum()}")
print(f"  BJ↔V-JEPA2:  {(cca_bj_vj>0.3).sum()}")

# ── Save ──────────────────────────────────────────────────────────────────
np.savez(OUT / 'ch2_0_alignment.npz',
    fwd_raw_vj=fwd_raw_vj, fwd_raw_cl=fwd_raw_cl,
    fwd_bj_vj=fwd_bj_vj, fwd_bj_cl=fwd_bj_cl,
    rev_vj_raw=rev_vj_raw, rev_cl_raw=rev_cl_raw, rev_vj_bj=rev_vj_bj,
    cca_raw_vj=cca_raw_vj, cca_raw_cl=cca_raw_cl, cca_bj_vj=cca_bj_vj,
)
print(f"\nSaved → {OUT}/ch2_0_alignment.npz")
print("Done.")
