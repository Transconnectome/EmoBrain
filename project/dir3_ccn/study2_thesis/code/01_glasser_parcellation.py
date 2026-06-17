"""
Glasser HCP-MMP1 Parcellation for Horikawa fMRI data.
360 cortical + 10 subcortical (Tian S1) = 370 regions.
Matches Horikawa (2020) original analysis.

Input: Raw voxel-level fMRI frames (.pt files)
Output: (5 subjects, 2196 stimuli, 370 regions) parcellated fMRI
"""

import numpy as np
import torch
import os
import glob
from pathlib import Path
from tqdm import tqdm
import argparse

def download_glasser_atlas(output_dir):
    """Download Glasser HCP-MMP1 atlas in MNI152 2mm space."""
    import nilearn.datasets as datasets

    # Glasser atlas (360 cortical regions)
    # nilearn doesn't have Glasser directly, so we fetch from templateflow or URL
    atlas_dir = Path(output_dir) / 'atlas'
    atlas_dir.mkdir(parents=True, exist_ok=True)

    glasser_path = atlas_dir / 'HCP-MMP1_on_MNI152_ICBM2009a_nlin_2mm.nii.gz'

    if not glasser_path.exists():
        print("Downloading Glasser HCP-MMP1 atlas...")
        # Try templateflow first
        try:
            import templateflow.api as tflow
            glasser_file = tflow.get('MNI152NLin2009cAsym', atlas='HCPMMP1', resolution=2)
            import shutil
            shutil.copy(str(glasser_file), str(glasser_path))
            print(f"  Downloaded from templateflow → {glasser_path}")
        except Exception as e1:
            print(f"  templateflow failed: {e1}")
            # Fallback: download from URL
            try:
                import urllib.request
                url = "https://github.com/wayalan/HCP-MMP1/raw/master/HCP-MMP1_on_MNI152_ICBM2009a_nlin.nii.gz"
                urllib.request.urlretrieve(url, str(glasser_path))
                print(f"  Downloaded from GitHub → {glasser_path}")
            except Exception as e2:
                print(f"  URL download failed: {e2}")
                # Final fallback: use nilearn's fetch
                from nilearn import datasets as nds
                # Try Schaefer as fallback, but we really need Glasser
                raise RuntimeError("Cannot download Glasser atlas. Please manually download "
                                   "HCP-MMP1_on_MNI152_ICBM2009a_nlin.nii.gz")
    else:
        print(f"  Glasser atlas exists: {glasser_path}")

    # Subcortical: use Tian S1 (10 regions) or existing Tian S3
    # Horikawa used 10 subcortical regions
    # Check existing Tian atlas
    tian_path = Path('/pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/Brain-JEPA/atlas/Tian_Subcortex_S3_3T.nii')

    # For Horikawa compatibility, we need Tian S1 (10 regions) not S3 (50 regions)
    tian_s1_path = atlas_dir / 'Tian_Subcortex_S1_3T.nii.gz'
    if not tian_s1_path.exists():
        print("Downloading Tian S1 subcortical atlas (10 regions)...")
        try:
            import urllib.request
            url = "https://github.com/yetianmed/subcortex/raw/master/Group-Parcellation/3T/Subcortex-Only/Tian_Subcortex_S1_3T.nii"
            urllib.request.urlretrieve(url, str(tian_s1_path).replace('.gz', ''))
            print(f"  Downloaded → {tian_s1_path}")
        except Exception as e:
            print(f"  Tian S1 download failed: {e}")
            print(f"  Will use Tian S3 (50 regions) as fallback")
            tian_s1_path = tian_path
    else:
        print(f"  Tian S1 exists: {tian_s1_path}")

    return str(glasser_path), str(tian_s1_path)


def parcellate_frame(frame_tensor, glasser_img, tian_img):
    """Parcellate a single fMRI frame using Glasser + Tian atlases."""
    import nibabel as nib
    from nilearn.image import resample_to_img, new_img_like
    from nilearn.maskers import NiftiLabelsMasker

    # Convert tensor to nifti-like
    frame_np = frame_tensor.numpy().squeeze()  # (74, 91, 81)

    # Create a temporary nifti image with MNI affine
    # Use the same affine as the atlas
    ref_img = nib.load(glasser_img) if isinstance(glasser_img, str) else glasser_img

    # We need to match the frame to MNI space
    # The frame is already in MNI space (horikawa_filtered_MNI_to_TRs)
    # Create nifti with appropriate affine
    frame_nii = nib.Nifti1Image(frame_np, affine=ref_img.affine[:, :])

    # This may not work directly — the affines may differ
    # Better approach: use the parcellation script's method
    return None  # placeholder


def parcellate_with_masker(fmri_frames_dir, cortical_atlas, subcortical_atlas, subject, stimulus):
    """
    Load all frames for a stimulus, create 4D image, parcellate.
    """
    import nibabel as nib
    from nilearn.maskers import NiftiLabelsMasker
    from nilearn.image import resample_to_img

    # Load frames
    frame_files = sorted(glob.glob(os.path.join(fmri_frames_dir, 'frame_*.pt')))
    if not frame_files:
        return None

    frames = []
    for ff in frame_files:
        t = torch.load(ff, map_location='cpu', weights_only=False)
        frames.append(t.numpy().squeeze())

    # Stack to 4D: (x, y, z, t)
    fmri_4d = np.stack(frames, axis=-1)

    # Load reference for affine
    # We need the correct affine — check global_stats
    stats_path = os.path.join(fmri_frames_dir, 'global_stats.pt')
    if os.path.exists(stats_path):
        stats = torch.load(stats_path, map_location='cpu', weights_only=False)
        if hasattr(stats, 'affine'):
            affine = np.array(stats.affine)
        elif isinstance(stats, dict) and 'affine' in stats:
            affine = np.array(stats['affine'])
        else:
            # Use standard MNI 2mm affine
            affine = np.array([[-2, 0, 0, 90],
                               [0, 2, 0, -126],
                               [0, 0, 2, -72],
                               [0, 0, 0, 1]], dtype=float)
    else:
        affine = np.array([[-2, 0, 0, 90],
                           [0, 2, 0, -126],
                           [0, 0, 2, -72],
                           [0, 0, 0, 1]], dtype=float)

    fmri_img = nib.Nifti1Image(fmri_4d, affine)

    # Cortical parcellation
    cortical_masker = NiftiLabelsMasker(
        labels_img=cortical_atlas,
        resampling_target='data',
        strategy='mean'
    )
    cortical_ts = cortical_masker.fit_transform(fmri_img)  # (T, n_cortical)

    # Subcortical parcellation
    subcortical_masker = NiftiLabelsMasker(
        labels_img=subcortical_atlas,
        resampling_target='data',
        strategy='mean'
    )
    subcortical_ts = subcortical_masker.fit_transform(fmri_img)  # (T, n_subcortical)

    # Concatenate
    full_ts = np.concatenate([cortical_ts, subcortical_ts], axis=1)  # (T, n_cortical + n_subcortical)

    return full_ts


def main():
    parser = argparse.ArgumentParser(description='Glasser parcellation for Horikawa')
    parser.add_argument('--input_dir', type=str,
                        default='/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img')
    parser.add_argument('--output_dir', type=str,
                        default='/pscratch/sd/s/sjmoon/EmoFM/main/results/glasser_parcellation')
    parser.add_argument('--subjects', nargs='+', default=['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05'])
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download atlases
    glasser_path, tian_path = download_glasser_atlas(str(output_dir))

    print(f"\nCortical atlas: {glasser_path}")
    print(f"Subcortical atlas: {tian_path}")

    import nibabel as nib
    g_img = nib.load(glasser_path)
    t_img = nib.load(tian_path)
    g_labels = np.unique(g_img.get_fdata().astype(int))
    t_labels = np.unique(t_img.get_fdata().astype(int))
    n_cortical = len(g_labels) - 1  # exclude 0
    n_subcortical = len(t_labels) - 1
    print(f"Cortical regions: {n_cortical}, Subcortical regions: {n_subcortical}")
    print(f"Total: {n_cortical + n_subcortical}")

    # Process each subject
    for subj in args.subjects:
        print(f"\n{'='*50}")
        print(f"Processing {subj}...")

        # Find all stimulus directories for this subject
        stim_dirs = sorted(glob.glob(os.path.join(args.input_dir, f'{subj}_stimulus_*')))
        print(f"  Found {len(stim_dirs)} stimuli")

        all_ts = []
        stim_ids = []

        for stim_dir in tqdm(stim_dirs, desc=subj):
            stim_name = os.path.basename(stim_dir)
            stim_id = int(stim_name.split('_')[-1])

            ts = parcellate_with_masker(stim_dir, glasser_path, tian_path, subj, stim_id)

            if ts is not None:
                # Average across timepoints (like Horikawa)
                ts_mean = ts.mean(axis=0)  # (n_regions,)
                all_ts.append(ts_mean)
                stim_ids.append(stim_id)

        if all_ts:
            # Sort by stimulus ID
            sort_order = np.argsort(stim_ids)
            all_ts = np.array(all_ts)[sort_order]
            stim_ids = np.array(stim_ids)[sort_order]

            subj_idx = int(subj.split('-')[1]) - 1

            save_path = output_dir / f'{subj}_glasser.npz'
            np.savez(save_path,
                     time_series=all_ts,
                     stim_ids=stim_ids,
                     n_cortical=n_cortical,
                     n_subcortical=n_subcortical)
            print(f"  Saved: {save_path}, shape={all_ts.shape}")

    # Combine all subjects
    print("\nCombining all subjects...")
    all_subj = []
    for subj in args.subjects:
        save_path = output_dir / f'{subj}_glasser.npz'
        if save_path.exists():
            d = np.load(save_path)
            all_subj.append(d['time_series'])

    if all_subj:
        combined = np.stack(all_subj, axis=0)  # (5, N_stim, N_regions)
        np.save(output_dir / 'fmri_glasser.npy', combined)
        print(f"Combined shape: {combined.shape}")
        print(f"Saved: {output_dir}/fmri_glasser.npy")

    print("\nDone.")


if __name__ == '__main__':
    main()
