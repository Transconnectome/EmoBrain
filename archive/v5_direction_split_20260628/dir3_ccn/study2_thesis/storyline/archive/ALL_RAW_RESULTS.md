# ALL RAW RESULTS — Every NPZ File Dumped

Generated: 2026-04-10
Total files: 30


======================================================================
ALL RESULT FILES — RAW VALUES
======================================================================

--- brain_jepa_rsm_stats.npz ---
File: CCN2026/results/brain_jepa_rsm_stats.npz
Keys: ['rsa_cross_subject', 'off_diag_mean', 'off_diag_std']
  rsa_cross_subject: shape=(5, 5), dtype=float64
    values=[[1.     0.332  0.3185 0.2853 0.3293]
 [0.332  1.     0.3809 0.3589 0.4122]
 [0.3185 0.3809 1.     0.327  0.3672]
 [0.2853 0.3589 0.327  1.     0.3603]
 [0.3293 0.4122 0.3672 0.3603 1.    ]]
  off_diag_mean: shape=(), dtype=float64
    values=0.3472
  off_diag_std: shape=(), dtype=float64
    values=0.0342

--- brain_pred_subspace_prediction.npz ---
File: CCN2026/results/brain_pred_subspace_prediction.npz
Keys: ['target_names', 'emotion_labels', 'dim_labels', 'r2_pred_vjepa', 'r2_unpred_vjepa', 'r2_all_vjepa', 'pred_idx_vjepa', 'r2_pred_clip', 'r2_unpred_clip', 'r2_all_clip', 'pred_idx_clip']
  target_names: shape=(37,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Arousal' 'Valence' 'Dominance']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  r2_pred_vjepa: shape=(37,), dtype=float64
    values=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045  0.0059 0.0128 0.1715 0.1057 0.0293 0.0518
 0.0651 0.0112 0.    ]
  r2_unpred_vjepa: shape=(37,), dtype=float64
    values=[0.     0.2677 0.1687 0.1805 0.0512 0.166  0.2219 0.0487 0.0832 0.1284 0.0072 0.0204 0.3386 0.     0.0953 0.     0.1527
 0.     0.0629 0.1963 0.     0.1318 0.072  0.1241 0.1832 0.     0.0852 0.2234 0.0322 0.0306 0.3005 0.0678 0.     0.0518
 0.0037 0.1562 0.    ]
  r2_all_vjepa: shape=(37,), dtype=float64
    values=[2.7007e-03 3.5966e-01 5.5093e-01 3.2192e-01 6.7057e-02 2.3945e-01 2.5379e-01 8.3853e-02 1.2283e-01 3.1757e-01
 9.4531e-03 2.0796e-02 3.6426e-01 0.0000e+00 1.8227e-01 6.5927e-03 3.9551e-01 0.0000e+00 1.4472e-01 2.6669e-01
 0.0000e+00 1.5615e-01 1.5515e-01 2.2346e-01 1.9750e-01 0.0000e+00 1.2214e-01 2.7627e-01 4.3999e-02 4.6547e-02
 4.9898e-01 1.8283e-01 2.4083e-02 1.5171e-01 8.8923e-02 1.8167e-01 3.8625e-04]
  pred_idx_vjepa: shape=(3,), dtype=int64
    values=[0 1 2]
  r2_pred_clip: shape=(37,), dtype=float64
    values=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308 0.1959 0.0436 0.5379 0.1882 0.103  0.1211
 0.0621 0.2706 0.0565]
  r2_unpred_clip: shape=(37,), dtype=float64
    values=[0.0308 0.3933 0.1468 0.0913 0.0325 0.1609 0.1493 0.0242 0.0512 0.1442 0.0545 0.     0.4409 0.     0.1483 0.0112 0.1364
 0.     0.0085 0.1525 0.     0.0699 0.0356 0.2418 0.2808 0.0405 0.0099 0.2437 0.0632 0.029  0.1367 0.0534 0.0609 0.0148
 0.0585 0.18   0.    ]
  r2_all_clip: shape=(37,), dtype=float64
    values=[0.0695 0.5462 0.6505 0.4711 0.2321 0.392  0.385  0.1281 0.1738 0.3611 0.0934 0.0595 0.6394 0.0542 0.3671 0.0774 0.4663
 0.0123 0.2083 0.43   0.0094 0.2999 0.2616 0.3879 0.5251 0.1109 0.126  0.6074 0.2795 0.0767 0.7275 0.26   0.1764 0.2078
 0.1355 0.4787 0.0639]
  pred_idx_clip: shape=(6,), dtype=int64
    values=[0 1 2 4 5 6]

--- brain_pred_subspace_prediction_14d.npz ---
File: CCN2026/results/brain_pred_subspace_prediction_14d.npz
Keys: ['metadata_path', 'target_names', 'emotion_labels', 'dim_labels', 'dim_cols', 'r2_pred_vjepa', 'r2_unpred_vjepa', 'r2_all_vjepa', 'pred_idx_vjepa', 'r2_pred_clip', 'r2_unpred_clip', 'r2_all_clip', 'pred_idx_clip']
  metadata_path: shape=(1,), dtype=<U113
    values=['/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv']
  target_names: shape=(48,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment'
 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity' 'Obstruction' 'Safety' 'Upswing' 'Valence']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(14,), dtype=<U11
    values=['Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment' 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity'
 'Obstruction' 'Safety' 'Upswing' 'Valence']
  dim_cols: shape=(14,), dtype=<U17
    values=['approach_score' 'arousal_score' 'attention_score' 'certainty_score' 'commitment_score' 'control_score'
 'dominance_score' 'effort_score' 'fairness_score' 'identity_score' 'obstruction_score' 'safety_score' 'upswing_score'
 'valence_score']
  r2_pred_vjepa: shape=(48,), dtype=float64
    values=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045  0.0059 0.0128 0.1715 0.1057 0.0293 0.0518
 0.0266 0.0651 0.048  0.0256 0.0653 0.0443 0.     0.024  0.007  0.0287 0.0147 0.0685 0.     0.0112]
  r2_unpred_vjepa: shape=(48,), dtype=float64
    values=[0.     0.2677 0.1687 0.1805 0.0512 0.166  0.2219 0.0487 0.0832 0.1284 0.0072 0.0204 0.3386 0.     0.0953 0.     0.1527
 0.     0.0629 0.1963 0.     0.1318 0.072  0.1241 0.1832 0.     0.0852 0.2234 0.0322 0.0306 0.3005 0.0678 0.     0.0518
 0.1523 0.0037 0.     0.087  0.1234 0.1728 0.     0.0795 0.1153 0.0625 0.0336 0.2028 0.0873 0.1562]
  r2_all_vjepa: shape=(48,), dtype=float64
    values=[2.7007e-03 3.5966e-01 5.5093e-01 3.2192e-01 6.7057e-02 2.3945e-01 2.5379e-01 8.3853e-02 1.2283e-01 3.1757e-01
 9.4531e-03 2.0796e-02 3.6426e-01 0.0000e+00 1.8227e-01 6.5927e-03 3.9551e-01 0.0000e+00 1.4472e-01 2.6669e-01
 0.0000e+00 1.5615e-01 1.5515e-01 2.2346e-01 1.9750e-01 0.0000e+00 1.2214e-01 2.7627e-01 4.3999e-02 4.6547e-02
 4.9898e-01 1.8283e-01 2.4083e-02 1.5171e-01 1.8601e-01 8.8923e-02 4.5172e-02 1.2068e-01 1.9736e-01 2.2606e-01
 3.8625e-04 1.2129e-01 1.2835e-01 9.7029e-02 5.5916e-02 2.8134e-01 9.5944e-02 1.8167e-01]
  pred_idx_vjepa: shape=(3,), dtype=int64
    values=[0 1 2]
  r2_pred_clip: shape=(48,), dtype=float64
    values=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308 0.1959 0.0436 0.5379 0.1882 0.103  0.1211
 0.2473 0.0621 0.0575 0.1748 0.1071 0.3156 0.0565 0.1882 0.2771 0.116  0.1441 0.3259 0.1793 0.2706]
  r2_unpred_clip: shape=(48,), dtype=float64
    values=[0.0308 0.3933 0.1468 0.0913 0.0325 0.1609 0.1493 0.0242 0.0512 0.1442 0.0545 0.     0.4409 0.     0.1483 0.0112 0.1364
 0.     0.0085 0.1525 0.     0.0699 0.0356 0.2418 0.2808 0.0405 0.0099 0.2437 0.0632 0.029  0.1367 0.0534 0.0609 0.0148
 0.2026 0.0585 0.0141 0.1038 0.2363 0.0975 0.     0.1383 0.0699 0.124  0.0501 0.1761 0.0811 0.18  ]
  r2_all_clip: shape=(48,), dtype=float64
    values=[0.0695 0.5462 0.6505 0.4711 0.2321 0.392  0.385  0.1281 0.1738 0.3611 0.0934 0.0595 0.6394 0.0542 0.3671 0.0774 0.4663
 0.0123 0.2083 0.43   0.0094 0.2999 0.2616 0.3879 0.5251 0.1109 0.126  0.6074 0.2795 0.0767 0.7275 0.26   0.1764 0.2078
 0.4739 0.1355 0.0959 0.2971 0.3567 0.4389 0.0639 0.3476 0.3701 0.2596 0.2087 0.5245 0.2813 0.4787]
  pred_idx_clip: shape=(6,), dtype=int64
    values=[0 1 2 4 5 6]

--- brain_predictable_dims.npz ---
File: CCN2026/results/brain_predictable_dims.npz
Keys: ['r2_vjepa_per_dim', 'r2_clip_per_dim', 'cumul_vjepa_var_order', 'cumul_clip_var_order', 'cumul_vjepa_sorted', 'cumul_clip_sorted', 'vjepa_pca_var_ratio', 'clip_pca_var_ratio', 'sat_vjepa_var_order', 'sat_clip_var_order', 'sat_vjepa_sorted', 'sat_clip_sorted']
  r2_vjepa_per_dim: shape=(100,), dtype=float64
    values=[3.7284e-01 7.4791e-02 8.7770e-02 3.1729e-04 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00]
  r2_clip_per_dim: shape=(100,), dtype=float64
    values=[0.2613 0.1559 0.1271 0.     0.1154 0.0167 0.0125 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.    ]
  cumul_vjepa_var_order: shape=(100,), dtype=float64
    values=[0.3728 0.4476 0.5354 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357]
  cumul_clip_var_order: shape=(100,), dtype=float64
    values=[0.2613 0.4171 0.5442 0.5442 0.6597 0.6764 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889]
  cumul_vjepa_sorted: shape=(100,), dtype=float64
    values=[0.3728 0.4606 0.5354 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357
 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357 0.5357]
  cumul_clip_sorted: shape=(100,), dtype=float64
    values=[0.2613 0.4171 0.5442 0.6597 0.6764 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889
 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889 0.6889]
  vjepa_pca_var_ratio: shape=(100,), dtype=float64
    values=[0.1702 0.0553 0.0507 0.0366 0.0354 0.0288 0.0277 0.025  0.0213 0.0188 0.017  0.0166 0.0157 0.0142 0.0138 0.0125 0.0122
 0.0117 0.011  0.0101 0.0099 0.0094 0.0088 0.0086 0.0084 0.0081 0.008  0.0075 0.0074 0.0071 0.0066 0.0065 0.0063 0.0059
 0.0057 0.0056 0.0053 0.005  0.0049 0.0049 0.0048 0.0046 0.0045 0.0043 0.0042 0.0042 0.004  0.0038 0.0038 0.0036 0.0036
 0.0035 0.0034 0.0033 0.0033 0.0032 0.0031 0.003  0.003  0.0029 0.0028 0.0027 0.0027 0.0026 0.0025 0.0025 0.0024 0.0024
 0.0022 0.0022 0.0021 0.0021 0.0021 0.002  0.002  0.0019 0.0019 0.0018 0.0018 0.0018 0.0017 0.0017 0.0016 0.0016 0.0016
 0.0015 0.0015 0.0015 0.0015 0.0014 0.0014 0.0014 0.0014 0.0014 0.0013 0.0013 0.0013 0.0013 0.0012 0.0012]
  clip_pca_var_ratio: shape=(100,), dtype=float64
    values=[0.0827 0.0626 0.0517 0.0401 0.0347 0.0293 0.0245 0.0212 0.0199 0.016  0.0145 0.0142 0.0133 0.0127 0.0118 0.0108 0.0104
 0.0101 0.0092 0.0089 0.0085 0.0083 0.008  0.0078 0.0077 0.0075 0.0067 0.0066 0.0061 0.006  0.0059 0.0057 0.0055 0.0053
 0.0052 0.0051 0.0049 0.0048 0.0047 0.0046 0.0044 0.0043 0.0042 0.0041 0.0041 0.0039 0.0039 0.0038 0.0037 0.0037 0.0036
 0.0035 0.0034 0.0033 0.0033 0.0033 0.0032 0.0031 0.003  0.003  0.003  0.0029 0.0028 0.0028 0.0028 0.0027 0.0027 0.0027
 0.0026 0.0026 0.0025 0.0025 0.0025 0.0024 0.0024 0.0023 0.0023 0.0023 0.0023 0.0022 0.0022 0.0022 0.0022 0.0021 0.0021
 0.0021 0.002  0.002  0.002  0.002  0.0019 0.0019 0.0019 0.0019 0.0018 0.0018 0.0018 0.0017 0.0017 0.0017]
  sat_vjepa_var_order: shape=(), dtype=int64
    values=3
  sat_clip_var_order: shape=(), dtype=int64
    values=5
  sat_vjepa_sorted: shape=(), dtype=int64
    values=3
  sat_clip_sorted: shape=(), dtype=int64
    values=4

--- cca_brain_video_results.npz ---
File: CCN2026/results/cca_brain_video_results.npz
Keys: ['cc_r', 'brain_cc', 'video_cc', 'sig_mask', 'p_values', 'p_corrected', 'cc_r_null', 'corr_cc_emo', 'pval_cc_emo', 'corr_cc_emo_brain', 'corr_cc_av', 'max_r_per_cc', 'r2_cca_sig', 'r2_cca_all', 'r2_pca_3', 'r2_pca_10', 'r2_pca_100', 'cc_r_per_subj', 'emotion_labels', 'n_pca', 'n_cc', 'n_perm']
  cc_r: shape=(100,), dtype=float64
    values=[0.7737 0.6792 0.6492 0.6082 0.5715 0.5217 0.4952 0.4941 0.4604 0.4574 0.4385 0.428  0.4151 0.4008 0.3895 0.368  0.361
 0.3573 0.3484 0.3331 0.336  0.3283 0.3247 0.3178 0.3135 0.3069 0.3065 0.2967 0.2955 0.287  0.2775 0.2746 0.273  0.2679
 0.2613 0.2557 0.249  0.2427 0.2364 0.2287 0.2312 0.2235 0.2189 0.2164 0.2144 0.2072 0.2061 0.2018 0.1951 0.1908 0.1869
 0.1867 0.179  0.1762 0.1681 0.166  0.1641 0.162  0.1577 0.155  0.1539 0.1463 0.1403 0.1352 0.1295 0.1271 0.1251 0.1234
 0.1205 0.1191 0.1152 0.1099 0.1045 0.1038 0.1015 0.0929 0.0893 0.0822 0.08   0.0773 0.0722 0.0706 0.0628 0.0606 0.0575
 0.053  0.0507 0.0476 0.0431 0.0366 0.0339 0.0325 0.0259 0.0235 0.0182 0.0146 0.0114 0.0061 0.006  0.002 ]
  brain_cc: shape=(2196, 100), dtype=float64
    [0,:20]=[ 0.0137 -0.3179 -1.4359 -0.7095 -0.5204  0.8006 -0.0231 -0.0082  0.7429  0.3735  0.2354  0.5115 -0.5256  0.1354
 -0.2381 -0.5374 -0.3993 -0.1248 -0.9552  1.7078]
  video_cc: shape=(2196, 100), dtype=float64
    [0,:20]=[ 0.6901 -0.5556 -1.1838  0.1885 -0.3443 -0.2142 -0.2574 -0.1332 -0.1954 -0.1873  0.0688  0.4416 -0.2474  1.2912
  0.6173  0.1126  0.8868  0.4243 -1.2871  0.2323]
  sig_mask: shape=(100,), dtype=bool
    values=[ True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True
  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True
  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True
  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True  True
  True  True  True  True  True  True False  True  True False  True  True  True False False  True False False False
 False False False False False]
  p_values: shape=(100,), dtype=float64
    values=[0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.
 0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.
 0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.
 0.    0.    0.    0.    0.    0.    0.001 0.005 0.    0.    0.    0.    0.    0.    0.    0.    0.    0.    0.
 0.    0.008 0.001 0.    0.006 0.    0.071 0.025 0.022 0.052 0.019 0.013 0.03  0.256 0.175 0.03  0.333 0.191 0.45
 0.486 0.448 0.836 0.183 0.269]
  p_corrected: shape=(100,), dtype=float64
    values=[0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.0013 0.0063 0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.0098 0.0013 0.     0.0074 0.     0.0789 0.0291 0.0259
 0.0584 0.0226 0.0157 0.0341 0.2723 0.1923 0.0341 0.3469 0.2054 0.4592 0.4909 0.4592 0.836  0.1989 0.2832]
  cc_r_null: shape=(100, 1000), dtype=float64
    [0,:20]=[0.4201 0.4008 0.4063 0.4209 0.4101 0.411  0.4119 0.4146 0.4121 0.4009 0.4104 0.4105 0.4091 0.414  0.4215 0.4115 0.4217
 0.4193 0.4009 0.4046]
  corr_cc_emo: shape=(100, 34), dtype=float64
    [0,:20]=[ 0.1072 -0.059  -0.1702  0.1965  0.1512  0.3354  0.1261 -0.1137 -0.1679 -0.2114  0.0868 -0.0133 -0.1845  0.0728
 -0.0979  0.1915 -0.1127 -0.0643  0.225   0.3375]
  pval_cc_emo: shape=(100, 34), dtype=float64
    [0,:20]=[4.7410e-07 5.7189e-03 9.7408e-16 1.4580e-20 1.0500e-12 7.2912e-59 3.0059e-09 9.2814e-08 2.3947e-15 1.2929e-23
 4.6577e-05 5.3228e-01 2.9065e-18 6.3900e-04 4.2596e-06 1.3690e-19 1.1887e-07 2.5576e-03 1.3545e-26 1.2658e-59]
  corr_cc_emo_brain: shape=(100, 34), dtype=float64
    [0,:20]=[ 0.0668 -0.0598 -0.1301  0.1493  0.1393  0.3138  0.0954 -0.1104 -0.1488 -0.1825  0.0678 -0.0266 -0.1451  0.055
 -0.0796  0.1647 -0.0773 -0.0514  0.1903  0.297 ]
  corr_cc_av: shape=(100, 2), dtype=float64
    first row=[ 0.2373 -0.1507]
  max_r_per_cc: shape=(100,), dtype=float64
    values=[0.4558 0.4366 0.1838 0.292  0.1873 0.3271 0.1771 0.2682 0.1969 0.1622 0.1391 0.1774 0.1551 0.1807 0.1059 0.1212 0.1051
 0.1389 0.0729 0.0588 0.0555 0.0647 0.0836 0.0749 0.1334 0.1138 0.0718 0.0703 0.0828 0.0729 0.1328 0.0616 0.0777 0.0683
 0.0955 0.0753 0.0959 0.0588 0.0496 0.0895 0.0987 0.0679 0.0395 0.0867 0.0486 0.0677 0.0796 0.0554 0.0731 0.0658 0.1202
 0.057  0.0853 0.0816 0.0685 0.0592 0.0566 0.0616 0.0771 0.059  0.0988 0.0546 0.0561 0.1002 0.0724 0.0474 0.0485 0.0614
 0.0582 0.0702 0.061  0.054  0.1042 0.1203 0.0733 0.07   0.0799 0.0768 0.0843 0.0524 0.058  0.0618 0.0825 0.0966 0.0638
 0.0692 0.0767 0.0662 0.0452 0.0548 0.0552 0.0529 0.057  0.0567 0.0553 0.0466 0.0591 0.0731 0.0483 0.0736]
  r2_cca_sig: shape=(36,), dtype=float64
    values=[0.0129 0.3831 0.5329 0.3329 0.0862 0.2565 0.2746 0.0925 0.1309 0.3142 0.012  0.0498 0.3542 0.0117 0.2045 0.0159 0.4025
 0.     0.1556 0.2778 0.     0.1475 0.1638 0.225  0.1844 0.0013 0.1403 0.3127 0.0515 0.0492 0.5394 0.1994 0.032  0.1639
 0.1039 0.2181]
  r2_cca_all: shape=(36,), dtype=float64
    values=[0.0031 0.3966 0.558  0.3314 0.0818 0.2599 0.2721 0.0912 0.1269 0.3275 0.0087 0.0479 0.3718 0.0038 0.2037 0.0093 0.4211
 0.     0.1564 0.2726 0.     0.146  0.1606 0.2285 0.2069 0.     0.1397 0.3167 0.0498 0.0384 0.5485 0.1965 0.0277 0.1688
 0.1011 0.2089]
  r2_pca_3: shape=(36,), dtype=float64
    values=[0.0018 0.0885 0.3299 0.1074 0.0132 0.0736 0.0513 0.0301 0.01   0.1477 0.     0.     0.0091 0.     0.0238 0.0041 0.1965
 0.     0.0609 0.0634 0.     0.0248 0.0602 0.0795 0.0041 0.     0.0284 0.1105 0.0058 0.0088 0.1276 0.0969 0.0271 0.0282
 0.0609 0.0095]
  r2_pca_10: shape=(36,), dtype=float64
    values=[0.019  0.154  0.468  0.2048 0.0578 0.1614 0.1369 0.075  0.1219 0.2138 0.0124 0.0158 0.0453 0.0217 0.0759 0.0175 0.3653
 0.007  0.0941 0.1755 0.0026 0.0809 0.115  0.096  0.0485 0.0204 0.1002 0.2051 0.039  0.0232 0.2606 0.1546 0.0451 0.0789
 0.076  0.0649]
  r2_pca_100: shape=(36,), dtype=float64
    values=[0.0031 0.3966 0.558  0.3314 0.0818 0.2599 0.2721 0.0912 0.1269 0.3275 0.0087 0.0479 0.3718 0.0038 0.2037 0.0093 0.4211
 0.     0.1564 0.2726 0.     0.146  0.1606 0.2285 0.2069 0.     0.1397 0.3167 0.0498 0.0384 0.5485 0.1965 0.0277 0.1688
 0.1011 0.2089]
  cc_r_per_subj: shape=(5, 100), dtype=float64
    [0,:20]=[0.7369 0.6109 0.5687 0.5357 0.5182 0.4603 0.4428 0.4369 0.4238 0.408  0.3938 0.3824 0.3763 0.3617 0.3548 0.3535 0.3457
 0.3381 0.3337 0.3299]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  n_pca: shape=(), dtype=int64
    values=100
  n_cc: shape=(), dtype=int64
    values=100
  n_perm: shape=(), dtype=int64
    values=1000

--- cka_rsa_vs_k.npz ---
File: CCN2026/results/cka_rsa_vs_k.npz
Keys: ['k_values', 'cka_brain_vjepa', 'cka_brain_clip', 'rsa_brain_vjepa', 'rsa_brain_clip']
  k_values: shape=(14,), dtype=int64
    values=[  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  cka_brain_vjepa: shape=(14,), dtype=float64
    values=[0.1172 0.1175 0.1192 0.1218 0.1258 0.126  0.1265 0.1266 0.1266 0.1268 0.127  0.1272 0.1276 0.1278]
  cka_brain_clip: shape=(14,), dtype=float64
    values=[0.0955 0.0949 0.1005 0.1072 0.1087 0.1093 0.1094 0.1094 0.1096 0.1098 0.1101 0.1101 0.1104 0.1106]
  rsa_brain_vjepa: shape=(14,), dtype=float64
    values=[0.0964 0.1034 0.1067 0.1124 0.1181 0.1189 0.1197 0.1196 0.1196 0.1199 0.1199 0.1202 0.1204 0.1205]
  rsa_brain_clip: shape=(14,), dtype=float64
    values=[0.0932 0.0969 0.1011 0.1077 0.1082 0.1081 0.1079 0.1076 0.1078 0.1079 0.1081 0.1083 0.108  0.108 ]

--- crossspace_rsa_results.npz ---
File: CCN2026/results/crossspace_rsa_results.npz
Keys: ['emotion_labels', 'rsa_brain', 'rsa_vjepa2', 'rsa_clip', 'alignment', 'divergence']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  rsa_brain: shape=(34,), dtype=float64
    values=[-1.8824e-02  5.6880e-03  2.2610e-02 -8.2621e-02 -2.0797e-03 -3.6861e-02 -4.3583e-02  1.5989e-02 -1.1447e-03
  3.7007e-02 -2.6636e-02 -3.2911e-03  3.0783e-02 -7.4421e-05  2.6774e-02 -1.4773e-02 -1.2570e-02  9.6396e-03
 -1.9927e-02 -2.7501e-02  3.3932e-03 -2.5987e-03 -6.8246e-02 -6.0835e-03  3.8634e-02 -6.0793e-03 -1.5026e-02
  5.0138e-02 -1.8333e-02 -4.0270e-02  6.2026e-02 -1.0847e-01 -2.2637e-02 -3.7373e-02]
  rsa_vjepa2: shape=(34,), dtype=float64
    values=[ 0.0146  0.0919 -0.1273  0.1803  0.0283  0.0393 -0.0067  0.0446 -0.0431 -0.0822  0.0277 -0.0011  0.0045  0.0236
  0.064   0.048  -0.1031 -0.0086  0.0203  0.0625  0.0171  0.0678 -0.0571  0.0984  0.0085  0.013   0.0336  0.0187
  0.042   0.0011  0.0303  0.151   0.073   0.038 ]
  rsa_clip: shape=(34,), dtype=float64
    values=[-0.014   0.0815 -0.0027  0.1335  0.0315  0.1299  0.0918  0.0145 -0.0931 -0.0529  0.0931 -0.0192  0.0166 -0.0012
  0.0447  0.0564  0.019  -0.0149  0.016   0.151   0.0096  0.1356  0.0479  0.0178 -0.0175 -0.0186  0.0478  0.0425
  0.0403 -0.0105  0.066   0.22    0.0634  0.0135]
  alignment: shape=(34,), dtype=float64
    values=[-1.8824e-02  5.6880e-03 -1.2734e-01 -8.2621e-02 -2.0797e-03 -3.6861e-02 -4.3583e-02  1.5989e-02 -4.3090e-02
 -8.2173e-02 -2.6636e-02 -3.2911e-03  4.5209e-03 -7.4421e-05  2.6774e-02 -1.4773e-02 -1.0310e-01 -8.5679e-03
 -1.9927e-02 -2.7501e-02  3.3932e-03 -2.5987e-03 -6.8246e-02 -6.0835e-03  8.5282e-03 -6.0793e-03 -1.5026e-02
  1.8697e-02 -1.8333e-02 -4.0270e-02  3.0325e-02 -1.0847e-01 -2.2637e-02 -3.7373e-02]
  divergence: shape=(34,), dtype=float64
    values=[0.0335 0.0862 0.1499 0.2629 0.0304 0.0762 0.0369 0.0286 0.0419 0.1192 0.0544 0.0022 0.0263 0.0237 0.0372 0.0628 0.0905
 0.0182 0.0402 0.09   0.0137 0.0704 0.0111 0.1045 0.0301 0.0191 0.0487 0.0314 0.0603 0.0414 0.0317 0.2594 0.0956 0.0754]

--- dimensional_emotion_results.npz ---
File: CCN2026/results/dimensional_emotion_results.npz
Keys: ['corr_vjepa_avd', 'pval_vjepa_avd', 'pval_vjepa_avd_fdr', 'corr_clip_avd', 'pval_clip_avd', 'pval_clip_avd_fdr', 'r2_brain_avd', 'r2_vjepa_avd_k27', 'r2_clip_avd_k27', 'r2_vjepa_k_avd', 'r2_clip_k_avd', 'r2_brain_k_avd', 'k_values', 'avd_labels', 'r2_vjepa_per_dim', 'r2_clip_per_dim', 'brain_pred_mask_vjepa', 'brain_pred_mask_clip', 'vjepa_var_ratio', 'clip_var_ratio']
  corr_vjepa_avd: shape=(100, 3), dtype=float64
    [0,:20]=[ 0.1408 -0.1259  0.0422]
  pval_vjepa_avd: shape=(100, 3), dtype=float64
    [0,:20]=[3.4629e-11 3.2353e-09 4.8032e-02]
  pval_vjepa_avd_fdr: shape=(100, 3), dtype=float64
    [0,:20]=[2.9966e-09 1.9412e-07 1.8402e-01]
  corr_clip_avd: shape=(100, 3), dtype=float64
    [0,:20]=[-0.1337  0.1983  0.0293]
  pval_clip_avd: shape=(100, 3), dtype=float64
    [0,:20]=[3.1919e-10 6.4273e-21 1.7031e-01]
  pval_clip_avd_fdr: shape=(100, 3), dtype=float64
    [0,:20]=[8.7052e-09 3.8564e-19 3.7567e-01]
  r2_brain_avd: shape=(3,), dtype=float64
    values=[0.     0.0652 0.    ]
  r2_vjepa_avd_k27: shape=(3,), dtype=float64
    values=[0.0833 0.1203 0.0162]
  r2_clip_avd_k27: shape=(3,), dtype=float64
    values=[0.1059 0.4397 0.0834]
  r2_vjepa_k_avd: shape=(14, 3), dtype=float64
    values=[[0.0651 0.0112 0.    ]
 [0.0665 0.0136 0.0033]
 [0.0703 0.0274 0.0086]
 [0.0833 0.04   0.0104]
 [0.0812 0.083  0.0201]
 [0.0775 0.101  0.019 ]
 [0.0837 0.1207 0.0151]
 [0.0833 0.1203 0.0162]
 [0.0911 0.1202 0.0213]
 [0.0928 0.1212 0.0231]
 [0.1003 0.1465 0.0241]
 [0.102  0.1635 0.0181]
 [0.0968 0.1816 0.0125]
 [0.0889 0.1817 0.0004]]
  r2_clip_k_avd: shape=(14, 3), dtype=float64
    values=[[0.0205 0.0499 0.0083]
 [0.0851 0.0864 0.0153]
 [0.0897 0.3035 0.0587]
 [0.0914 0.3857 0.0636]
 [0.0985 0.3908 0.0725]
 [0.0985 0.43   0.0816]
 [0.107  0.4338 0.083 ]
 [0.1059 0.4397 0.0834]
 [0.1125 0.4394 0.0822]
 [0.1146 0.4515 0.0826]
 [0.1274 0.4535 0.0859]
 [0.1254 0.4728 0.088 ]
 [0.1321 0.4781 0.0756]
 [0.1355 0.4787 0.0639]]
  r2_brain_k_avd: shape=(14, 3), dtype=float64
    values=[[0.026  0.0255 0.    ]
 [0.0298 0.0404 0.    ]
 [0.0296 0.1056 0.    ]
 [0.0336 0.1089 0.0018]
 [0.0384 0.1127 0.0004]
 [0.0393 0.1164 0.0052]
 [0.0374 0.122  0.0178]
 [0.0351 0.1269 0.0171]
 [0.0367 0.1344 0.0169]
 [0.0342 0.1379 0.0174]
 [0.0359 0.1353 0.0189]
 [0.0424 0.148  0.0151]
 [0.0369 0.158  0.0064]
 [0.0196 0.163  0.    ]]
  k_values: shape=(14,), dtype=int64
    values=[  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  avd_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  r2_vjepa_per_dim: shape=(100,), dtype=float64
    values=[3.7284e-01 7.4791e-02 8.7770e-02 3.1729e-04 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00]
  r2_clip_per_dim: shape=(100,), dtype=float64
    values=[0.2613 0.1559 0.1271 0.     0.1154 0.0167 0.0125 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.    ]
  brain_pred_mask_vjepa: shape=(100,), dtype=int8
    values=[1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
  brain_pred_mask_clip: shape=(100,), dtype=int8
    values=[1 1 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
  vjepa_var_ratio: shape=(100,), dtype=float64
    values=[0.1702 0.0553 0.0507 0.0366 0.0354 0.0288 0.0277 0.025  0.0213 0.0188 0.017  0.0166 0.0157 0.0142 0.0138 0.0125 0.0122
 0.0117 0.011  0.0101 0.0099 0.0094 0.0088 0.0086 0.0084 0.0081 0.008  0.0075 0.0074 0.0071 0.0066 0.0065 0.0063 0.0059
 0.0057 0.0056 0.0053 0.005  0.0049 0.0049 0.0048 0.0046 0.0045 0.0043 0.0042 0.0042 0.004  0.0038 0.0038 0.0036 0.0036
 0.0035 0.0034 0.0033 0.0033 0.0032 0.0031 0.003  0.003  0.0029 0.0028 0.0027 0.0027 0.0026 0.0025 0.0025 0.0024 0.0024
 0.0022 0.0022 0.0021 0.0021 0.0021 0.002  0.002  0.0019 0.0019 0.0018 0.0018 0.0018 0.0017 0.0017 0.0016 0.0016 0.0016
 0.0015 0.0015 0.0015 0.0015 0.0014 0.0014 0.0014 0.0014 0.0014 0.0013 0.0013 0.0013 0.0013 0.0012 0.0012]
  clip_var_ratio: shape=(100,), dtype=float64
    values=[0.0827 0.0626 0.0517 0.0401 0.0347 0.0293 0.0245 0.0212 0.0199 0.016  0.0145 0.0142 0.0133 0.0127 0.0118 0.0108 0.0104
 0.0101 0.0092 0.0089 0.0085 0.0083 0.008  0.0078 0.0077 0.0075 0.0067 0.0066 0.0061 0.006  0.0059 0.0057 0.0055 0.0053
 0.0052 0.0051 0.0049 0.0048 0.0047 0.0046 0.0044 0.0043 0.0042 0.0041 0.0041 0.0039 0.0039 0.0038 0.0037 0.0037 0.0036
 0.0035 0.0034 0.0033 0.0033 0.0033 0.0032 0.0031 0.003  0.003  0.003  0.0029 0.0028 0.0028 0.0028 0.0027 0.0027 0.0027
 0.0026 0.0026 0.0025 0.0025 0.0025 0.0024 0.0024 0.0023 0.0023 0.0023 0.0023 0.0022 0.0022 0.0022 0.0022 0.0021 0.0021
 0.0021 0.002  0.002  0.002  0.002  0.0019 0.0019 0.0019 0.0019 0.0018 0.0018 0.0018 0.0017 0.0017 0.0017]

--- embedding_2d.npz ---
File: CCN2026/results/embedding_2d.npz
Keys: ['emb_brain', 'emb_vjepa2', 'emb_clip', 'emb_overlay_brain', 'emb_overlay_vjepa', 'dominant_emo', 'emotion_labels', 'pca_var_explained']
  emb_brain: shape=(2196, 2), dtype=float32
    [0,:20]=[3.1412 2.4704]
  emb_vjepa2: shape=(2196, 2), dtype=float32
    [0,:20]=[10.0459 10.1157]
  emb_clip: shape=(2196, 2), dtype=float32
    [0,:20]=[0.6868 9.761 ]
  emb_overlay_brain: shape=(2196, 2), dtype=float64
    [0,:20]=[0.0008 0.0001]
  emb_overlay_vjepa: shape=(2196, 2), dtype=float64
    [0,:20]=[0.0004 0.0007]
  dominant_emo: shape=(2196,), dtype=int64
    first 20=[22 24  3  3 10 24  2  2 28 30  3  3  3 32 19  2 10 30 12  2]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  pca_var_explained: shape=(), dtype=float64
    values=48.7824

--- exp14_robustness_results.npz ---
File: CCN2026/results/exp14_robustness_results.npz
Keys: ['thresholds', 'n_pred_vjepa', 'n_pred_clip', 'exp12_mean_cat_vjepa', 'exp12_mean_dim_vjepa', 'exp12_mean_cat_clip', 'exp12_mean_dim_clip', 'exp13_partial_cat_vjepa', 'exp13_partial_dim_vjepa', 'exp13_partial_cat_clip', 'exp13_partial_dim_clip', 'exp12_boot_vjepa', 'exp12_boot_clip', 'exp13_boot_vjepa', 'exp13_boot_clip', 'ci_exp12_vjepa', 'ci_exp12_clip', 'ci_exp13_vjepa', 'ci_exp13_clip', 'confound_sets', 'emotion_labels', 'dim_labels', 'target_names', 'confound_ablation_r2_vjepa', 'confound_ablation_r2_clip', 'confound_ablation_rsa']
  thresholds: shape=(5,), dtype=float64
    values=[0.005 0.01  0.02  0.03  0.05 ]
  n_pred_vjepa: shape=(5,), dtype=int64
    values=[3 3 3 3 3]
  n_pred_clip: shape=(5,), dtype=int64
    values=[6 6 4 4 4]
  exp12_mean_cat_vjepa: shape=(5,), dtype=float64
    values=[0.055 0.055 0.055 0.055 0.055]
  exp12_mean_dim_vjepa: shape=(5,), dtype=float64
    values=[0.0254 0.0254 0.0254 0.0254 0.0254]
  exp12_mean_cat_clip: shape=(5,), dtype=float64
    values=[0.1659 0.1659 0.1142 0.1142 0.1142]
  exp12_mean_dim_clip: shape=(5,), dtype=float64
    values=[0.1297 0.1297 0.0413 0.0413 0.0413]
  exp13_partial_cat_vjepa: shape=(5,), dtype=float64
    values=[0.0051 0.0051 0.0051 0.0051 0.0051]
  exp13_partial_dim_vjepa: shape=(5,), dtype=float64
    values=[0.0029 0.0029 0.0029 0.0029 0.0029]
  exp13_partial_cat_clip: shape=(5,), dtype=float64
    values=[0.0134 0.0134 0.0111 0.0111 0.0111]
  exp13_partial_dim_clip: shape=(5,), dtype=float64
    values=[0.0086 0.0086 0.0011 0.0011 0.0011]
  exp12_boot_vjepa: shape=(100, 3), dtype=float64
    [0,:20]=[0.0581 0.035  1.66  ]
  exp12_boot_clip: shape=(100, 3), dtype=float64
    [0,:20]=[0.1746 0.1369 1.2757]
  exp13_boot_vjepa: shape=(100, 3), dtype=float64
    [0,:20]=[4.1362e-03 0.0000e+00 4.1362e+07]
  exp13_boot_clip: shape=(100, 3), dtype=float64
    [0,:20]=[8.7427e-03 0.0000e+00 8.7427e+07]
  ci_exp12_vjepa: shape=(3, 3), dtype=float64
    values=[[0.0551 0.0232 1.5268]
 [0.0584 0.0298 1.9773]
 [0.0626 0.0389 2.5044]]
  ci_exp12_clip: shape=(3, 3), dtype=float64
    values=[[0.1624 0.1162 1.1512]
 [0.17   0.136  1.2559]
 [0.1774 0.1508 1.4086]]
  ci_exp13_vjepa: shape=(3, 3), dtype=float64
    values=[[9.6558e-04 0.0000e+00 2.6080e-01]
 [3.9218e-03 0.0000e+00 1.2813e+07]
 [8.7862e-03 1.3707e-02 7.8670e+07]]
  ci_exp13_clip: shape=(3, 3), dtype=float64
    values=[[1.6210e-03 0.0000e+00 2.4442e-01]
 [5.6089e-03 0.0000e+00 2.5682e+07]
 [1.0142e-02 1.9723e-02 9.7191e+07]]
  confound_sets: shape=(3,), dtype=<U15
    values=['vision_only' 'semantic_only' 'vision_semantic']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  target_names: shape=(37,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Arousal' 'Valence' 'Dominance']
  confound_ablation_r2_vjepa: shape=(3, 37), dtype=float64
    first row=[0.     0.0238 0.1317 0.023  0.     0.002  0.     0.     0.     0.0841 0.     0.     0.     0.     0.     0.     0.0613
 0.     0.0163 0.0003 0.     0.     0.0118 0.0061 0.     0.     0.     0.013  0.     0.0077 0.0403 0.0166 0.     0.
 0.0338 0.     0.    ]
  confound_ablation_r2_clip: shape=(3, 37), dtype=float64
    first row=[0.     0.0325 0.2033 0.144  0.1046 0.0636 0.038  0.0104 0.0006 0.0613 0.0188 0.     0.0125 0.058  0.103  0.0167 0.0896
 0.     0.1037 0.078  0.     0.0761 0.1114 0.0306 0.093  0.0187 0.0049 0.1821 0.1198 0.     0.1986 0.0639 0.0561 0.028
 0.0212 0.1567 0.    ]
  confound_ablation_rsa: shape=(1,), dtype=object
    values=["{'vision_only': {'Brain-JEPA': {'V-JEPA2': (np.float64(-0.007062931282308947), np.float64(-0.0078071694043384005)), 'CLIP': (np.float64(-0.06971020476765742), np.float64(-0.07021268820705448))}, 'Raw fMRI': {'V-JEPA2': (np.float64(0.09561730537876985), np.float64(0.08463917878466468)), 'CLIP': (np.float64(0.08863207203584224), np.float64(0.07941565968107915))}}, 'semantic_only': {'Brain-JEPA': {'V-JEPA2': (np.float64(-0.007062931282308947), np.float64(-0.003131982801696355)), 'CLIP': (np.float64(-0.06971020476765742), np.float64(-0.06809515756786676))}, 'Raw fMRI': {'V-JEPA2': (np.float64(0.09561730537876985), np.float64(0.08148384230808607)), 'CLIP': (np.float64(0.08863207203584224), np.float64(0.07427900811700669))}}, 'vision_semantic': {'Brain-JEPA': {'V-JEPA2': (np.float64(-0.007062931282308947), np.float64(-0.004500470034535597)), 'CLIP': (np.float64(-0.06971020476765742), np.float64(-0.06855760166379064))}, 'Raw fMRI': {'V-JEPA2': (np.float64(0.09561730537876985), np.float64(0.07762574421543185)), 'CLIP': (np.float64(0.08863207203584224), np.float64(0.07174453425766851))}}}"]

--- exp15_stability_results.npz ---
File: CCN2026/results/exp15_stability_results.npz
Keys: ['subj_r2_vjepa', 'subj_r2_clip', 'subj_mask_vjepa', 'subj_mask_clip', 'mean_mask_vjepa', 'mean_mask_clip', 'jaccard_vjepa', 'jaccard_clip', 'selection_freq_vjepa', 'selection_freq_clip', 'resample_summary_vjepa', 'resample_summary_clip', 'top5_freq_vjepa', 'top5_freq_clip', 'alpha', 'exp12_cat_vjepa', 'exp12_dim_vjepa', 'exp12_cat_clip', 'exp12_dim_clip', 'exp13_cat_vjepa', 'exp13_dim_vjepa', 'exp13_cat_clip', 'exp13_dim_clip', 'emotion_labels', 'dim_labels']
  subj_r2_vjepa: shape=(5, 100), dtype=float64
    [0,:20]=[0.1359 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.    ]
  subj_r2_clip: shape=(5, 100), dtype=float64
    [0,:20]=[0.1472 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.    ]
  subj_mask_vjepa: shape=(5, 100), dtype=bool
    [0,:20]=[ True False False False False False False False False False False False False False False False False False False
 False]
  subj_mask_clip: shape=(5, 100), dtype=bool
    [0,:20]=[ True False False False False False False False False False False False False False False False False False False
 False]
  mean_mask_vjepa: shape=(100,), dtype=bool
    values=[ True  True  True False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False]
  mean_mask_clip: shape=(100,), dtype=bool
    values=[ True  True  True False  True  True  True False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False]
  jaccard_vjepa: shape=(5, 5), dtype=float64
    values=[[1.  0.5 0.5 1.  1. ]
 [0.5 1.  1.  0.5 0.5]
 [0.5 1.  1.  0.5 0.5]
 [1.  0.5 0.5 1.  1. ]
 [1.  0.5 0.5 1.  1. ]]
  jaccard_clip: shape=(5, 5), dtype=float64
    values=[[1.  0.5 0.5 1.  1. ]
 [0.5 1.  1.  0.5 0.5]
 [0.5 1.  1.  0.5 0.5]
 [1.  0.5 0.5 1.  1. ]
 [1.  0.5 0.5 1.  1. ]]
  selection_freq_vjepa: shape=(100,), dtype=float64
    values=[1.  0.  0.4 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.
 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.
 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.
 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0. ]
  selection_freq_clip: shape=(100,), dtype=float64
    values=[1.  0.4 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.
 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.
 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.
 0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0.  0. ]
  resample_summary_vjepa: shape=(100, 3), dtype=float64
    [0,:20]=[0.0529 0.0189 2.7965]
  resample_summary_clip: shape=(100, 3), dtype=float64
    [0,:20]=[0.1587 0.116  1.3675]
  top5_freq_vjepa: shape=(34,), dtype=int64
    values=[  0   0 100  79   0   0   0   0   0  83   0   0   0   0   0   0 100   0   0   0   0   0   0   1   0   0   0   0   0
   0 100  37   0   0]
  top5_freq_clip: shape=(34,), dtype=int64
    values=[  0   0 100 100   0   0   0   0   0   0   0   0   0   0   0   0  94   0   0  13   0   0   0   0   0   0   0  93   0
   0 100   0   0   0]
  alpha: shape=(4,), dtype=float64
    values=[  0.1   1.   10.  100. ]
  exp12_cat_vjepa: shape=(4,), dtype=float64
    values=[0.055  0.055  0.055  0.0551]
  exp12_dim_vjepa: shape=(4,), dtype=float64
    values=[0.0254 0.0254 0.0254 0.0254]
  exp12_cat_clip: shape=(4,), dtype=float64
    values=[0.1659 0.1659 0.166  0.1661]
  exp12_dim_clip: shape=(4,), dtype=float64
    values=[0.1297 0.1297 0.1298 0.1296]
  exp13_cat_vjepa: shape=(4,), dtype=float64
    values=[0.0051 0.0051 0.0051 0.0053]
  exp13_dim_vjepa: shape=(4,), dtype=float64
    values=[0.0029 0.0029 0.003  0.0031]
  exp13_cat_clip: shape=(4,), dtype=float64
    values=[0.0134 0.0134 0.0135 0.0139]
  exp13_dim_clip: shape=(4,), dtype=float64
    values=[0.0086 0.0086 0.0086 0.0089]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']

--- exp16_incremental_baseline_results.npz ---
File: CCN2026/results/exp16_incremental_baseline_results.npz
Keys: ['target_names', 'emotion_labels', 'dim_labels', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_baseline', 'r2_vjepa_only', 'r2_clip_only', 'r2_combined_vjepa', 'r2_combined_clip', 'delta_vjepa', 'delta_clip']
  target_names: shape=(37,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Arousal' 'Valence' 'Dominance']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  pred_idx_vjepa: shape=(3,), dtype=int64
    values=[0 1 2]
  pred_idx_clip: shape=(6,), dtype=int64
    values=[0 1 2 4 5 6]
  r2_baseline: shape=(37,), dtype=float64
    values=[0.     0.1427 0.3549 0.0114 0.     0.     0.     0.     0.     0.     0.     0.     0.3873 0.     0.2008 0.     0.0907
 0.     0.     0.0632 0.     0.2984 0.     0.     0.     0.     0.     0.4791 0.     0.     0.6769 0.     0.     0.
 0.     0.2974 0.    ]
  r2_vjepa_only: shape=(37,), dtype=float64
    values=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045  0.0059 0.0128 0.1715 0.1057 0.0293 0.0518
 0.0651 0.0112 0.    ]
  r2_clip_only: shape=(37,), dtype=float64
    values=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308 0.1959 0.0436 0.5379 0.1882 0.103  0.1211
 0.0621 0.2706 0.0565]
  r2_combined_vjepa: shape=(37,), dtype=float64
    values=[0.     0.1546 0.3936 0.0178 0.     0.     0.     0.     0.     0.     0.     0.     0.3911 0.     0.2    0.     0.1049
 0.     0.     0.0691 0.     0.2951 0.     0.     0.     0.     0.     0.4776 0.     0.     0.6773 0.     0.     0.
 0.     0.2979 0.    ]
  r2_combined_clip: shape=(37,), dtype=float64
    values=[0.     0.1518 0.4115 0.0654 0.     0.     0.     0.     0.     0.     0.     0.     0.3881 0.     0.2176 0.     0.1165
 0.     0.     0.085  0.     0.2976 0.     0.     0.0166 0.     0.     0.4976 0.     0.     0.6796 0.     0.     0.
 0.     0.3212 0.    ]
  delta_vjepa: shape=(37,), dtype=float64
    values=[ 0.      0.0118  0.0387  0.0063  0.      0.      0.      0.      0.      0.      0.      0.      0.0038  0.
 -0.0008  0.      0.0141  0.      0.      0.0059  0.     -0.0033  0.      0.      0.      0.      0.     -0.0015
  0.      0.      0.0004  0.      0.      0.      0.      0.0004  0.    ]
  delta_clip: shape=(37,), dtype=float64
    values=[ 0.      0.009   0.0567  0.054   0.      0.      0.      0.      0.      0.      0.      0.      0.0008  0.
  0.0168  0.      0.0258  0.      0.      0.0218  0.     -0.0007  0.      0.      0.0166  0.      0.      0.0185
  0.      0.      0.0027  0.      0.      0.      0.      0.0238  0.    ]

--- exp16_incremental_baseline_results_14d.npz ---
File: CCN2026/results/exp16_incremental_baseline_results_14d.npz
Keys: ['metadata_path', 'target_names', 'emotion_labels', 'dim_labels', 'dim_cols', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_baseline', 'r2_vjepa_only', 'r2_clip_only', 'r2_combined_vjepa', 'r2_combined_clip', 'delta_vjepa', 'delta_clip']
  metadata_path: shape=(1,), dtype=<U113
    values=['/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv']
  target_names: shape=(48,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment'
 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity' 'Obstruction' 'Safety' 'Upswing' 'Valence']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(14,), dtype=<U11
    values=['Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment' 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity'
 'Obstruction' 'Safety' 'Upswing' 'Valence']
  dim_cols: shape=(14,), dtype=<U17
    values=['approach_score' 'arousal_score' 'attention_score' 'certainty_score' 'commitment_score' 'control_score'
 'dominance_score' 'effort_score' 'fairness_score' 'identity_score' 'obstruction_score' 'safety_score' 'upswing_score'
 'valence_score']
  pred_idx_vjepa: shape=(3,), dtype=int64
    values=[0 1 2]
  pred_idx_clip: shape=(6,), dtype=int64
    values=[0 1 2 4 5 6]
  r2_baseline: shape=(48,), dtype=float64
    values=[0.     0.1427 0.3549 0.0114 0.     0.     0.     0.     0.     0.     0.     0.     0.3873 0.     0.2008 0.     0.0907
 0.     0.     0.0632 0.     0.2984 0.     0.     0.     0.     0.     0.4791 0.     0.     0.6769 0.     0.     0.
 0.2463 0.     0.     0.     0.     0.242  0.     0.0072 0.0896 0.     0.     0.3051 0.1329 0.2974]
  r2_vjepa_only: shape=(48,), dtype=float64
    values=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045  0.0059 0.0128 0.1715 0.1057 0.0293 0.0518
 0.0266 0.0651 0.048  0.0256 0.0653 0.0443 0.     0.024  0.007  0.0287 0.0147 0.0685 0.     0.0112]
  r2_clip_only: shape=(48,), dtype=float64
    values=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308 0.1959 0.0436 0.5379 0.1882 0.103  0.1211
 0.2473 0.0621 0.0575 0.1748 0.1071 0.3156 0.0565 0.1882 0.2771 0.116  0.1441 0.3259 0.1793 0.2706]
  r2_combined_vjepa: shape=(48,), dtype=float64
    values=[0.     0.1546 0.3936 0.0178 0.     0.     0.     0.     0.     0.     0.     0.     0.3911 0.     0.2    0.     0.1049
 0.     0.     0.0691 0.     0.2951 0.     0.     0.     0.     0.     0.4776 0.     0.     0.6773 0.     0.     0.
 0.248  0.     0.     0.     0.     0.2463 0.     0.0222 0.089  0.     0.     0.3101 0.1284 0.2979]
  r2_combined_clip: shape=(48,), dtype=float64
    values=[0.     0.1518 0.4115 0.0654 0.     0.     0.     0.     0.     0.     0.     0.     0.3881 0.     0.2176 0.     0.1165
 0.     0.     0.085  0.     0.2976 0.     0.     0.0166 0.     0.     0.4976 0.     0.     0.6796 0.     0.     0.
 0.2671 0.     0.     0.     0.     0.2894 0.     0.0297 0.1211 0.     0.     0.3387 0.1478 0.3212]
  delta_vjepa: shape=(48,), dtype=float64
    values=[ 0.      0.0118  0.0387  0.0063  0.      0.      0.      0.      0.      0.      0.      0.      0.0038  0.
 -0.0008  0.      0.0141  0.      0.      0.0059  0.     -0.0033  0.      0.      0.      0.      0.     -0.0015
  0.      0.      0.0004  0.      0.      0.      0.0017  0.      0.      0.      0.      0.0043  0.      0.015
 -0.0006  0.      0.      0.0049 -0.0046  0.0004]
  delta_clip: shape=(48,), dtype=float64
    values=[ 0.      0.009   0.0567  0.054   0.      0.      0.      0.      0.      0.      0.      0.      0.0008  0.
  0.0168  0.      0.0258  0.      0.      0.0218  0.     -0.0007  0.      0.      0.0166  0.      0.      0.0185
  0.      0.      0.0027  0.      0.      0.      0.0208  0.      0.      0.      0.      0.0474  0.      0.0225
  0.0315  0.      0.      0.0336  0.0148  0.0238]

--- exp17_av2d_results.npz ---
File: CCN2026/results/exp17_av2d_results.npz
Keys: ['metadata_path', 'fmri_path', 'target_names', 'emotion_labels', 'dim_labels', 'dim_cols', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_pred_vjepa', 'r2_unpred_vjepa', 'r2_all_vjepa', 'r2_pred_clip', 'r2_unpred_clip', 'r2_all_clip', 'raw_k_values', 'raw_mean_cat', 'raw_mean_dim', 'raw_cat_dim_ratio', 'r2_raw_k27', 'r2_raw_full']
  metadata_path: shape=(1,), dtype=<U113
    values=['/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv']
  fmri_path: shape=(1,), dtype=<U57
    values=['/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy']
  target_names: shape=(36,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Arousal' 'Valence']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(2,), dtype=<U7
    values=['Arousal' 'Valence']
  dim_cols: shape=(2,), dtype=<U13
    values=['arousal_score' 'valence_score']
  pred_idx_vjepa: shape=(3,), dtype=int64
    values=[0 1 2]
  pred_idx_clip: shape=(6,), dtype=int64
    values=[0 1 2 4 5 6]
  r2_pred_vjepa: shape=(36,), dtype=float64
    values=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045  0.0059 0.0128 0.1715 0.1057 0.0293 0.0518
 0.0651 0.0112]
  r2_unpred_vjepa: shape=(36,), dtype=float64
    values=[0.     0.2677 0.1687 0.1805 0.0512 0.166  0.2219 0.0487 0.0832 0.1284 0.0072 0.0204 0.3386 0.     0.0953 0.     0.1527
 0.     0.0629 0.1963 0.     0.1318 0.072  0.1241 0.1832 0.     0.0852 0.2234 0.0322 0.0306 0.3005 0.0678 0.     0.0518
 0.0037 0.1562]
  r2_all_vjepa: shape=(36,), dtype=float64
    values=[0.0027 0.3597 0.5509 0.3219 0.0671 0.2394 0.2538 0.0839 0.1228 0.3176 0.0095 0.0208 0.3643 0.     0.1823 0.0066 0.3955
 0.     0.1447 0.2667 0.     0.1561 0.1552 0.2235 0.1975 0.     0.1221 0.2763 0.044  0.0465 0.499  0.1828 0.0241 0.1517
 0.0889 0.1817]
  r2_pred_clip: shape=(36,), dtype=float64
    values=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308 0.1959 0.0436 0.5379 0.1882 0.103  0.1211
 0.0621 0.2706]
  r2_unpred_clip: shape=(36,), dtype=float64
    values=[0.0308 0.3933 0.1468 0.0913 0.0325 0.1609 0.1493 0.0242 0.0512 0.1442 0.0545 0.     0.4409 0.     0.1483 0.0112 0.1364
 0.     0.0085 0.1525 0.     0.0699 0.0356 0.2418 0.2808 0.0405 0.0099 0.2437 0.0632 0.029  0.1367 0.0534 0.0609 0.0148
 0.0585 0.18  ]
  r2_all_clip: shape=(36,), dtype=float64
    values=[0.0695 0.5462 0.6505 0.4711 0.2321 0.392  0.385  0.1281 0.1738 0.3611 0.0934 0.0595 0.6394 0.0542 0.3671 0.0774 0.4663
 0.0123 0.2083 0.43   0.0094 0.2999 0.2616 0.3879 0.5251 0.1109 0.126  0.6074 0.2795 0.0767 0.7275 0.26   0.1764 0.2078
 0.1355 0.4787]
  raw_k_values: shape=(14,), dtype=int64
    values=[  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  raw_mean_cat: shape=(14,), dtype=float64
    values=[0.033  0.0523 0.0683 0.0865 0.0921 0.1018 0.1061 0.1075 0.1088 0.1102 0.1112 0.114  0.1166 0.1154]
  raw_mean_dim: shape=(14,), dtype=float64
    values=[0.0382 0.0563 0.0709 0.1142 0.1138 0.1302 0.1396 0.1431 0.1466 0.1489 0.147  0.1517 0.1605 0.1609]
  raw_cat_dim_ratio: shape=(14,), dtype=float64
    values=[0.8653 0.9277 0.9633 0.7569 0.8091 0.7814 0.7601 0.7514 0.7422 0.7396 0.7565 0.7513 0.726  0.7177]
  r2_raw_k27: shape=(36,), dtype=float64
    values=[0.0276 0.1391 0.2335 0.2126 0.0476 0.1889 0.134  0.0728 0.0836 0.1131 0.0761 0.0115 0.072  0.0222 0.267  0.0951 0.2107
 0.     0.0662 0.1857 0.     0.1319 0.127  0.1288 0.1161 0.0203 0.0823 0.1102 0.0418 0.0481 0.3226 0.1789 0.0321 0.0571
 0.0681 0.2181]
  r2_raw_full: shape=(36,), dtype=float64
    values=[0.     0.     0.1351 0.0774 0.     0.051  0.     0.     0.     0.     0.     0.     0.     0.     0.1205 0.     0.1107
 0.     0.     0.0626 0.     0.0021 0.     0.     0.     0.     0.     0.     0.     0.     0.2919 0.0265 0.     0.
 0.     0.1461]

--- exp18_subjectwise_claim_check.npz ---
File: CCN2026/results/exp18_subjectwise_claim_check.npz
Keys: ['row_labels', 'ontology_order', 'model_order', 'emotion_labels', 'dim3_labels', 'dim14_labels', 'dim2_labels', 'r2_pc_vjepa', 'r2_pc_clip', 'mask_vjepa', 'mask_clip', 'pc_count_vjepa', 'pc_count_clip', 'r2_3d_vjepa', 'r2_3d_clip', 'r2_14d_vjepa', 'r2_14d_clip', 'r2_2d_vjepa', 'r2_2d_clip', 'agreement_3d_vjepa', 'agreement_3d_clip', 'agreement_14d_vjepa', 'agreement_14d_clip', 'agreement_2d_vjepa', 'agreement_2d_clip', 'agreement_rate_3d_vjepa', 'agreement_rate_3d_clip', 'agreement_rate_14d_vjepa', 'agreement_rate_14d_clip', 'agreement_rate_2d_vjepa', 'agreement_rate_2d_clip']
  row_labels: shape=(6,), dtype=<U5
    values=['mean' 'subj1' 'subj2' 'subj3' 'subj4' 'subj5']
  ontology_order: shape=(3,), dtype=<U3
    values=['3D' '14D' '2D']
  model_order: shape=(2,), dtype=<U5
    values=['vjepa' 'clip']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim3_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  dim14_labels: shape=(14,), dtype=<U11
    values=['Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment' 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity'
 'Obstruction' 'Safety' 'Upswing' 'Valence']
  dim2_labels: shape=(2,), dtype=<U7
    values=['Arousal' 'Valence']
  r2_pc_vjepa: shape=(6, 100), dtype=float64
    [0,:20]=[3.7284e-01 7.4791e-02 8.7770e-02 3.1729e-04 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00]
  r2_pc_clip: shape=(6, 100), dtype=float64
    [0,:20]=[0.2613 0.1559 0.1271 0.     0.1154 0.0167 0.0125 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.    ]
  mask_vjepa: shape=(6, 100), dtype=bool
    [0,:20]=[ True  True  True False False False False False False False False False False False False False False False False
 False]
  mask_clip: shape=(6, 100), dtype=bool
    [0,:20]=[ True  True  True False  True  True  True False False False False False False False False False False False False
 False]
  pc_count_vjepa: shape=(6,), dtype=int64
    values=[3 1 2 2 1 1]
  pc_count_clip: shape=(6,), dtype=int64
    values=[6 1 2 2 1 1]
  r2_3d_vjepa: shape=(6, 37), dtype=float64
    [0,:20]=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598]
  r2_3d_clip: shape=(6, 37), dtype=float64
    [0,:20]=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536]
  r2_14d_vjepa: shape=(6, 48), dtype=float64
    [0,:20]=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598]
  r2_14d_clip: shape=(6, 48), dtype=float64
    [0,:20]=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536]
  r2_2d_vjepa: shape=(6, 36), dtype=float64
    [0,:20]=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598]
  r2_2d_clip: shape=(6, 36), dtype=float64
    [0,:20]=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536]
  agreement_3d_vjepa: shape=(5,), dtype=int64
    values=[1 1 1 1 1]
  agreement_3d_clip: shape=(5,), dtype=int64
    values=[1 1 1 1 1]
  agreement_14d_vjepa: shape=(5,), dtype=int64
    values=[1 1 1 1 1]
  agreement_14d_clip: shape=(5,), dtype=int64
    values=[1 0 0 1 1]
  agreement_2d_vjepa: shape=(5,), dtype=int64
    values=[1 1 1 1 1]
  agreement_2d_clip: shape=(5,), dtype=int64
    values=[0 0 0 0 0]
  agreement_rate_3d_vjepa: shape=(1,), dtype=float64
    values=[1.]
  agreement_rate_3d_clip: shape=(1,), dtype=float64
    values=[1.]
  agreement_rate_14d_vjepa: shape=(1,), dtype=float64
    values=[1.]
  agreement_rate_14d_clip: shape=(1,), dtype=float64
    values=[0.6]
  agreement_rate_2d_vjepa: shape=(1,), dtype=float64
    values=[1.]
  agreement_rate_2d_clip: shape=(1,), dtype=float64
    values=[0.]

--- exp19_subjectwise_direct_decoding.npz ---
File: CCN2026/results/exp19_subjectwise_direct_decoding.npz
Keys: ['row_labels', 'setting_order', 'ontology_order', 'emotion_labels', 'dim3_labels', 'dim14_labels', 'dim2_labels', 'r2_3d_k27', 'r2_14d_k27', 'r2_2d_k27', 'r2_3d_full', 'r2_14d_full', 'r2_2d_full', 'agreement_k27_3d', 'agreement_k27_14d', 'agreement_k27_2d', 'agreement_full_3d', 'agreement_full_14d', 'agreement_full_2d', 'agreement_rate_k27_3d', 'agreement_rate_k27_14d', 'agreement_rate_k27_2d', 'agreement_rate_full_3d', 'agreement_rate_full_14d', 'agreement_rate_full_2d']
  row_labels: shape=(6,), dtype=<U5
    values=['mean' 'subj1' 'subj2' 'subj3' 'subj4' 'subj5']
  setting_order: shape=(2,), dtype=<U4
    values=['k27' 'full']
  ontology_order: shape=(3,), dtype=<U3
    values=['3D' '14D' '2D']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim3_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  dim14_labels: shape=(14,), dtype=<U11
    values=['Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment' 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity'
 'Obstruction' 'Safety' 'Upswing' 'Valence']
  dim2_labels: shape=(2,), dtype=<U7
    values=['Arousal' 'Valence']
  r2_3d_k27: shape=(6, 37), dtype=float64
    [0,:20]=[0.0133 0.0704 0.0932 0.0749 0.0299 0.1098 0.0867 0.0281 0.0225 0.0332 0.0386 0.     0.0119 0.     0.1242 0.0597 0.1062
 0.0084 0.034  0.0999]
  r2_14d_k27: shape=(6, 48), dtype=float64
    [0,:20]=[0.0133 0.0704 0.0932 0.0749 0.0299 0.1098 0.0867 0.0281 0.0225 0.0332 0.0386 0.     0.0119 0.     0.1242 0.0597 0.1062
 0.0084 0.034  0.0999]
  r2_2d_k27: shape=(6, 36), dtype=float64
    [0,:20]=[0.0133 0.0704 0.0932 0.0749 0.0299 0.1098 0.0867 0.0281 0.0225 0.0332 0.0386 0.     0.0119 0.     0.1242 0.0597 0.1062
 0.0084 0.034  0.0999]
  r2_3d_full: shape=(6, 37), dtype=float64
    [0,:20]=[0.     0.     0.0821 0.     0.     0.0026 0.     0.     0.     0.     0.     0.     0.     0.     0.0327 0.     0.0387
 0.     0.     0.    ]
  r2_14d_full: shape=(6, 48), dtype=float64
    [0,:20]=[0.     0.     0.0821 0.     0.     0.0026 0.     0.     0.     0.     0.     0.     0.     0.     0.0327 0.     0.0387
 0.     0.     0.    ]
  r2_2d_full: shape=(6, 36), dtype=float64
    [0,:20]=[0.     0.     0.0821 0.     0.     0.0026 0.     0.     0.     0.     0.     0.     0.     0.     0.0327 0.     0.0387
 0.     0.     0.    ]
  agreement_k27_3d: shape=(5,), dtype=int64
    values=[0 0 1 0 0]
  agreement_k27_14d: shape=(5,), dtype=int64
    values=[1 1 1 1 1]
  agreement_k27_2d: shape=(5,), dtype=int64
    values=[1 0 1 1 1]
  agreement_full_3d: shape=(5,), dtype=int64
    values=[0 1 0 1 1]
  agreement_full_14d: shape=(5,), dtype=int64
    values=[0 1 0 1 1]
  agreement_full_2d: shape=(5,), dtype=int64
    values=[0 1 0 1 1]
  agreement_rate_k27_3d: shape=(1,), dtype=float64
    values=[0.2]
  agreement_rate_k27_14d: shape=(1,), dtype=float64
    values=[1.]
  agreement_rate_k27_2d: shape=(1,), dtype=float64
    values=[0.8]
  agreement_rate_full_3d: shape=(1,), dtype=float64
    values=[0.6]
  agreement_rate_full_14d: shape=(1,), dtype=float64
    values=[0.6]
  agreement_rate_full_2d: shape=(1,), dtype=float64
    values=[0.6]

--- exp23_reverse_pca_ridge.npz ---
File: CCN2026/results/exp23_reverse_pca_ridge.npz
Keys: ['r2_obs', 'mse_obs', 'r2_null', 'p_values', 'p_corrected', 'sig_mask', 'brain_pca_var_ratio', 'corr_brain_emo', 'corr_brain_av', 'max_r_per_pc', 'emotion_labels', 'n_perm', 'r2_decode_Brain_PC1_3', 'r2_decode_Brain_PC1_10', 'r2_decode_Brain_all_100']
  r2_obs: shape=(100,), dtype=float64
    values=[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.
 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.
 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  mse_obs: shape=(100,), dtype=float64
    values=[5.7824e+00 2.8736e+00 2.1417e+00 1.2835e+00 1.0631e+00 9.9795e-01 6.3841e-01 6.8667e-01 3.1639e-01 3.1492e-01
 3.0305e-01 1.9902e-01 1.8638e-01 1.3353e-01 1.2252e-01 1.1778e-01 1.0410e-01 9.8982e-02 8.6653e-02 6.4937e-02
 6.6608e-02 5.2787e-02 4.7126e-02 4.5140e-02 4.9354e-02 3.6980e-02 3.2390e-02 3.3501e-02 3.2199e-02 2.6431e-02
 2.6648e-02 2.6400e-02 2.1383e-02 2.2933e-02 2.1412e-02 1.8985e-02 1.9277e-02 1.6875e-02 1.6561e-02 1.7258e-02
 1.5362e-02 1.3258e-02 1.3093e-02 1.1473e-02 1.1269e-02 1.1360e-02 1.0487e-02 8.6636e-03 8.6918e-03 8.7274e-03
 9.1143e-03 6.8350e-03 7.6404e-03 7.1591e-03 6.4846e-03 6.7438e-03 6.5556e-03 6.4848e-03 5.8468e-03 5.5602e-03
 5.4832e-03 5.1497e-03 4.9191e-03 4.9803e-03 4.5045e-03 4.2112e-03 4.0436e-03 4.4202e-03 4.1231e-03 3.9703e-03
 3.5782e-03 3.9029e-03 3.3290e-03 3.3274e-03 3.6952e-03 3.1550e-03 3.1515e-03 2.7257e-03 2.7531e-03 2.4938e-03
 2.6520e-03 2.6599e-03 2.3141e-03 2.2736e-03 2.2990e-03 2.2343e-03 2.3476e-03 2.0695e-03 2.1106e-03 2.0697e-03
 1.9604e-03 1.5892e-03 1.8760e-03 1.7516e-03 1.8670e-03 1.7599e-03 1.7029e-03 1.4713e-03 1.5688e-03 1.4188e-03]
  r2_null: shape=(100, 1000), dtype=float64
    [0,:20]=[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  p_values: shape=(100,), dtype=float64
    values=[1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.]
  p_corrected: shape=(100,), dtype=float64
    values=[1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.]
  sig_mask: shape=(100,), dtype=bool
    values=[False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False]
  brain_pca_var_ratio: shape=(100,), dtype=float64
    values=[3.2655e-01 1.6272e-01 1.1987e-01 6.6838e-02 6.1605e-02 5.0841e-02 3.6031e-02 2.8628e-02 1.8560e-02 1.4861e-02
 1.4353e-02 1.1198e-02 8.6624e-03 6.6713e-03 5.6357e-03 5.2995e-03 4.9085e-03 4.6965e-03 4.2112e-03 3.2093e-03
 3.0537e-03 2.3282e-03 2.2388e-03 2.1424e-03 1.9740e-03 1.8012e-03 1.5857e-03 1.5365e-03 1.3893e-03 1.3046e-03
 1.2185e-03 1.1763e-03 1.0088e-03 9.7362e-04 9.2345e-04 8.5418e-04 8.2832e-04 8.0459e-04 7.0793e-04 6.9959e-04
 6.5218e-04 6.1178e-04 5.5034e-04 5.3484e-04 5.1887e-04 4.7983e-04 4.4774e-04 4.1615e-04 3.7669e-04 3.7138e-04
 3.5303e-04 3.4210e-04 3.3516e-04 3.0913e-04 2.9879e-04 2.9574e-04 2.8039e-04 2.7276e-04 2.5643e-04 2.4635e-04
 2.3418e-04 2.2921e-04 2.2337e-04 2.1298e-04 2.0922e-04 1.9361e-04 1.8775e-04 1.8138e-04 1.8027e-04 1.7144e-04
 1.6891e-04 1.6184e-04 1.5217e-04 1.4440e-04 1.4080e-04 1.3608e-04 1.2794e-04 1.2391e-04 1.2105e-04 1.1566e-04
 1.1111e-04 1.0813e-04 1.0475e-04 1.0032e-04 9.7620e-05 9.7354e-05 9.5235e-05 9.2358e-05 8.9309e-05 8.6225e-05
 8.2941e-05 8.1686e-05 7.8880e-05 7.6758e-05 7.4269e-05 7.3935e-05 6.9875e-05 6.6333e-05 6.5189e-05 6.2050e-05]
  corr_brain_emo: shape=(100, 34), dtype=float64
    [0,:20]=[-0.0281  0.0197  0.0399 -0.1501 -0.0137 -0.0912 -0.1016  0.0553  0.116   0.0828 -0.0786  0.0632  0.0728  0.0282
  0.0099 -0.1002 -0.0193  0.0585 -0.0452 -0.0851]
  corr_brain_av: shape=(100, 2), dtype=float64
    first row=[-0.1017  0.0752]
  max_r_per_pc: shape=(100,), dtype=float64
    values=[0.2234 0.147  0.2041 0.1835 0.1047 0.1724 0.1781 0.0844 0.1974 0.1213 0.0889 0.1764 0.1213 0.1083 0.0832 0.0786 0.0807
 0.2063 0.0922 0.0728 0.084  0.0866 0.0682 0.1191 0.0713 0.0802 0.0863 0.0791 0.0996 0.0968 0.0697 0.1026 0.093  0.0648
 0.0725 0.0666 0.098  0.0763 0.0792 0.0803 0.0675 0.0569 0.0686 0.0712 0.0892 0.0939 0.0844 0.08   0.124  0.0709 0.0576
 0.0414 0.0493 0.0724 0.0947 0.0451 0.0712 0.0726 0.1022 0.1343 0.0884 0.0713 0.07   0.0695 0.0904 0.0442 0.06   0.0542
 0.0821 0.0909 0.0471 0.0561 0.0673 0.0588 0.0563 0.0659 0.0389 0.0726 0.0577 0.0467 0.0523 0.0723 0.056  0.0702 0.0579
 0.0762 0.0646 0.0772 0.0894 0.0862 0.0603 0.0686 0.0838 0.0733 0.061  0.0633 0.1065 0.0778 0.0516 0.0599]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  n_perm: shape=(), dtype=int64
    values=1000
  r2_decode_Brain_PC1_3: shape=(36,), dtype=float64
    values=[0.002  0.0034 0.0078 0.0086 0.0062 0.0365 0.0156 0.0119 0.0054 0.0003 0.0024 0.     0.     0.     0.0249 0.0114 0.0314
 0.     0.0192 0.045  0.     0.0219 0.0393 0.     0.0109 0.0005 0.03   0.0266 0.0122 0.0264 0.0352 0.0587 0.0151 0.0224
 0.026  0.0255]
  r2_decode_Brain_PC1_10: shape=(36,), dtype=float64
    values=[0.0092 0.0355 0.0698 0.0638 0.0363 0.072  0.0748 0.0249 0.0095 0.0277 0.035  0.     0.0145 0.008  0.0805 0.0537 0.0864
 0.0044 0.0277 0.0753 0.     0.0795 0.105  0.0422 0.0241 0.009  0.0503 0.0459 0.0263 0.0285 0.0814 0.0971 0.0285 0.0297
 0.0336 0.1089]
  r2_decode_Brain_all_100: shape=(36,), dtype=float64
    values=[0.     0.0742 0.1253 0.0843 0.0055 0.1348 0.0951 0.0214 0.     0.0412 0.0276 0.     0.0019 0.     0.1731 0.0534 0.1216
 0.     0.0012 0.1297 0.     0.1303 0.1145 0.0546 0.046  0.     0.0158 0.0773 0.     0.     0.2146 0.1115 0.     0.
 0.0196 0.163 ]

--- k_sweep_results.npz ---
File: CCN2026/results/k_sweep_results.npz
Keys: ['k_values', 'disparity_vjepa', 'disparity_clip', 'decoding_brain', 'decoding_vjepa', 'decoding_clip', 'k_elbow', 'k_plateau']
  k_values: shape=(14,), dtype=int64
    values=[  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  disparity_vjepa: shape=(14,), dtype=float64
    values=[0.9316 0.9383 0.9427 0.9404 0.9355 0.9372 0.9376 0.938  0.9387 0.9386 0.939  0.9397 0.9404 0.9406]
  disparity_clip: shape=(14,), dtype=float64
    values=[0.9336 0.9398 0.9364 0.9351 0.9364 0.9369 0.9381 0.9385 0.9389 0.9393 0.9398 0.9406 0.9417 0.9426]
  decoding_brain: shape=(14,), dtype=float64
    values=[0.0156 0.0226 0.0346 0.0428 0.0488 0.0537 0.0561 0.0561 0.0568 0.0583 0.059  0.0606 0.0574 0.0543]
  decoding_vjepa: shape=(14,), dtype=float64
    values=[0.055  0.0726 0.0797 0.0955 0.1136 0.1196 0.1292 0.1317 0.1334 0.1397 0.1463 0.1554 0.1678 0.1704]
  decoding_clip: shape=(14,), dtype=float64
    values=[0.0941 0.1366 0.1884 0.2115 0.2361 0.2534 0.2653 0.2696 0.2743 0.2816 0.2841 0.2906 0.294  0.2907]
  k_elbow: shape=(), dtype=int64
    values=15
  k_plateau: shape=(), dtype=int64
    values=34

--- pc_emotion_correlation.npz ---
File: CCN2026/results/pc_emotion_correlation.npz
Keys: ['corr_vjepa_emo', 'pval_vjepa_emo', 'pval_vjepa_emo_fdr', 'corr_clip_emo', 'pval_clip_emo', 'pval_clip_emo_fdr', 'corr_vjepa_avd', 'pval_vjepa_avd_fdr', 'corr_clip_avd', 'pval_clip_avd_fdr', 'emotion_labels', 'avd_labels', 'r2_vjepa', 'r2_clip', 'brain_pred_mask_vjepa', 'brain_pred_mask_clip', 'vjepa_var_ratio', 'clip_var_ratio']
  corr_vjepa_emo: shape=(100, 34), dtype=float64
    [0,:20]=[ 1.0059e-01  6.0729e-02 -3.2772e-01  2.6261e-01  1.0628e-01  2.0344e-01  4.6160e-02 -8.6845e-05 -1.4571e-01
 -2.8805e-01  5.2382e-02  5.0571e-04 -1.6401e-01  6.6872e-02  2.3842e-02  1.2128e-01 -2.4032e-01 -2.8492e-02
  1.9719e-01  2.0983e-01]
  pval_vjepa_emo: shape=(100, 34), dtype=float64
    [0,:20]=[2.3205e-06 4.4154e-03 3.8314e-56 5.8427e-36 5.9813e-07 6.0453e-22 3.0539e-02 9.9675e-01 6.8464e-12 3.1927e-43
 1.4088e-02 9.8110e-01 1.0422e-14 1.7160e-03 2.6409e-01 1.1901e-08 3.2102e-30 1.8198e-01 1.0904e-20 2.8383e-23]
  pval_vjepa_emo_fdr: shape=(100, 34), dtype=float64
    [0,:20]=[5.7588e-05 3.1942e-02 4.7695e-53 2.4831e-33 1.6534e-05 1.1419e-19 1.3012e-01 9.9899e-01 4.1567e-10 1.8092e-40
 7.4844e-02 9.8954e-01 9.0862e-13 1.5435e-02 5.0643e-01 4.4960e-07 9.9223e-28 4.0786e-01 1.7655e-18 5.6765e-21]
  corr_clip_emo: shape=(100, 34), dtype=float64
    [0,:20]=[-0.0604 -0.1073  0.3419 -0.2993 -0.2081 -0.3445 -0.1562  0.0924  0.2426  0.2437 -0.0577  0.0058  0.2723 -0.1414
  0.0071 -0.218   0.2258  0.1349 -0.1166 -0.3473]
  pval_clip_emo: shape=(100, 34), dtype=float64
    [0,:20]=[4.6503e-03 4.7078e-07 2.9241e-61 1.1127e-46 6.6261e-23 3.1759e-62 1.8318e-13 1.4499e-05 8.5823e-31 4.6958e-31
 6.8173e-03 7.8719e-01 1.2711e-38 2.8519e-11 7.4090e-01 4.9479e-25 8.7453e-27 2.2275e-10 4.2848e-08 2.8587e-63]
  pval_clip_emo_fdr: shape=(100, 34), dtype=float64
    [0,:20]=[3.7467e-02 9.4155e-06 7.6476e-59 2.2254e-44 3.8843e-21 8.9983e-60 6.5559e-12 2.2407e-04 7.8864e-29 4.4349e-29
 5.1508e-02 9.2579e-01 1.6622e-36 9.1475e-10 9.0776e-01 3.3645e-23 6.3264e-25 6.6433e-09 1.0047e-06 8.8361e-61]
  corr_vjepa_avd: shape=(100, 3), dtype=float64
    [0,:20]=[ 0.1408 -0.1259  0.0422]
  pval_vjepa_avd_fdr: shape=(100, 3), dtype=float64
    [0,:20]=[2.9966e-09 1.9412e-07 1.8402e-01]
  corr_clip_avd: shape=(100, 3), dtype=float64
    [0,:20]=[-0.1337  0.1983  0.0293]
  pval_clip_avd_fdr: shape=(100, 3), dtype=float64
    [0,:20]=[8.7052e-09 3.8564e-19 3.7567e-01]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  avd_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  r2_vjepa: shape=(100,), dtype=float64
    values=[3.7284e-01 7.4791e-02 8.7770e-02 3.1729e-04 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00]
  r2_clip: shape=(100,), dtype=float64
    values=[0.2613 0.1559 0.1271 0.     0.1154 0.0167 0.0125 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.    ]
  brain_pred_mask_vjepa: shape=(100,), dtype=int8
    values=[1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
  brain_pred_mask_clip: shape=(100,), dtype=int8
    values=[1 1 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
  vjepa_var_ratio: shape=(100,), dtype=float64
    values=[0.1702 0.0553 0.0507 0.0366 0.0354 0.0288 0.0277 0.025  0.0213 0.0188 0.017  0.0166 0.0157 0.0142 0.0138 0.0125 0.0122
 0.0117 0.011  0.0101 0.0099 0.0094 0.0088 0.0086 0.0084 0.0081 0.008  0.0075 0.0074 0.0071 0.0066 0.0065 0.0063 0.0059
 0.0057 0.0056 0.0053 0.005  0.0049 0.0049 0.0048 0.0046 0.0045 0.0043 0.0042 0.0042 0.004  0.0038 0.0038 0.0036 0.0036
 0.0035 0.0034 0.0033 0.0033 0.0032 0.0031 0.003  0.003  0.0029 0.0028 0.0027 0.0027 0.0026 0.0025 0.0025 0.0024 0.0024
 0.0022 0.0022 0.0021 0.0021 0.0021 0.002  0.002  0.0019 0.0019 0.0018 0.0018 0.0018 0.0017 0.0017 0.0016 0.0016 0.0016
 0.0015 0.0015 0.0015 0.0015 0.0014 0.0014 0.0014 0.0014 0.0014 0.0013 0.0013 0.0013 0.0013 0.0012 0.0012]
  clip_var_ratio: shape=(100,), dtype=float64
    values=[0.0827 0.0626 0.0517 0.0401 0.0347 0.0293 0.0245 0.0212 0.0199 0.016  0.0145 0.0142 0.0133 0.0127 0.0118 0.0108 0.0104
 0.0101 0.0092 0.0089 0.0085 0.0083 0.008  0.0078 0.0077 0.0075 0.0067 0.0066 0.0061 0.006  0.0059 0.0057 0.0055 0.0053
 0.0052 0.0051 0.0049 0.0048 0.0047 0.0046 0.0044 0.0043 0.0042 0.0041 0.0041 0.0039 0.0039 0.0038 0.0037 0.0037 0.0036
 0.0035 0.0034 0.0033 0.0033 0.0033 0.0032 0.0031 0.003  0.003  0.003  0.0029 0.0028 0.0028 0.0028 0.0027 0.0027 0.0027
 0.0026 0.0026 0.0025 0.0025 0.0025 0.0024 0.0024 0.0023 0.0023 0.0023 0.0023 0.0022 0.0022 0.0022 0.0022 0.0021 0.0021
 0.0021 0.002  0.002  0.002  0.002  0.0019 0.0019 0.0019 0.0019 0.0018 0.0018 0.0018 0.0017 0.0017 0.0017]

--- permutation_test_results.npz ---
File: CCN2026/results/permutation_test_results.npz
Keys: ['r2_obs', 'r2_null', 'p_values', 'p_corrected', 'brain_pred_mask', 'n_perm', 'alpha']
  r2_obs: shape=(100,), dtype=float64
    values=[3.7285e-01 7.4784e-02 8.7835e-02 2.5107e-04 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00]
  r2_null: shape=(100, 1000), dtype=float64
    [0,:20]=[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  p_values: shape=(100,), dtype=float64
    values=[0. 0. 0. 0. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.]
  p_corrected: shape=(100,), dtype=float64
    values=[0. 0. 0. 0. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.]
  brain_pred_mask: shape=(100,), dtype=bool
    values=[ True  True  True  True False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False False False False False False False False False False False False False False False
 False False False False False]
  n_perm: shape=(), dtype=int64
    values=1000
  alpha: shape=(), dtype=float64
    values=0.05

--- procrustes_results.npz ---
File: CCN2026/results/procrustes_results.npz
Keys: ['k_used', 'brain_std', 'vjepa_aligned', 'clip_aligned', 'disparity_vjepa', 'disparity_clip', 'error_vjepa', 'error_clip', 'emotion_error_vjepa', 'emotion_error_clip', 'brain_k', 'vjepa_k', 'clip_k', 'emotion_labels']
  k_used: shape=(), dtype=int64
    values=27
  brain_std: shape=(2196, 27), dtype=float64
    [0,:20]=[ 7.9874e-04 -6.8641e-05 -4.2326e-03 -6.0135e-03 -1.3521e-03 -3.7560e-03  3.5465e-03 -1.0234e-03  2.4291e-03
 -4.5788e-03 -2.5167e-03 -1.3155e-04 -1.5924e-05 -7.3071e-04  1.0924e-05  1.4498e-04  4.0496e-04  5.1185e-04
 -1.3908e-03 -1.4966e-03]
  vjepa_aligned: shape=(2196, 27), dtype=float64
    [0,:20]=[ 4.2918e-04  6.0224e-04 -1.8227e-03  6.2173e-04  1.3788e-04  2.5838e-03  1.7119e-05  9.7244e-04  4.3173e-04
  6.0264e-04 -1.8073e-03 -8.9908e-06 -8.9465e-04  5.1525e-04 -7.9167e-04  1.4773e-03 -3.7522e-04  1.0267e-03
 -1.3959e-03  3.2746e-03]
  clip_aligned: shape=(2196, 27), dtype=float64
    [0,:20]=[ 2.2957e-04  9.4323e-04 -1.9508e-03 -2.0252e-04 -1.3977e-03  5.5759e-05 -1.8600e-03  3.6514e-04 -8.0226e-04
  3.0250e-04 -4.4224e-04  1.1727e-04  3.6808e-04 -2.3926e-03 -1.2887e-03  3.2598e-04  8.0634e-04  1.7539e-04
  7.4779e-04  6.2175e-05]
  disparity_vjepa: shape=(), dtype=float64
    values=0.938
  disparity_clip: shape=(), dtype=float64
    values=0.9385
  error_vjepa: shape=(2196,), dtype=float64
    first 20=[0.0132 0.0225 0.0263 0.0267 0.0241 0.0178 0.021  0.0131 0.0137 0.018  0.0109 0.0294 0.0096 0.0294 0.0141 0.0214 0.0243
 0.0149 0.0099 0.0289]
  error_clip: shape=(2196,), dtype=float64
    first 20=[0.012  0.0249 0.0273 0.0288 0.0244 0.0163 0.0188 0.0121 0.014  0.0173 0.0129 0.0307 0.0104 0.0298 0.0135 0.0195 0.0246
 0.0126 0.0111 0.0284]
  emotion_error_vjepa: shape=(34,), dtype=float64
    values=[0.0201 0.0189 0.0182 0.0201 0.0191 0.0199 0.0196 0.0184 0.0192 0.0175 0.0194 0.0195 0.0168 0.0196 0.0181 0.0201 0.0188
 0.0185 0.0194 0.0197 0.0191 0.0198 0.0205 0.0192 0.0174 0.0199 0.02   0.0171 0.0197 0.0202 0.0166 0.0208 0.0201 0.0215]
  emotion_error_clip: shape=(34,), dtype=float64
    values=[0.0202 0.019  0.0183 0.0202 0.0191 0.02   0.0197 0.0182 0.0192 0.0176 0.0193 0.0196 0.0169 0.0195 0.0181 0.02   0.0189
 0.0185 0.0195 0.0198 0.0192 0.0198 0.0205 0.0192 0.0175 0.02   0.0202 0.0164 0.0197 0.0203 0.0163 0.0208 0.02   0.0217]
  brain_k: shape=(2196, 27), dtype=float64
    [0,:20]=[ 0.0858 -0.0074 -0.4545 -0.6458 -0.1452 -0.4034  0.3809 -0.1099  0.2609 -0.4917 -0.2703 -0.0141 -0.0017 -0.0785
  0.0012  0.0156  0.0435  0.055  -0.1494 -0.1607]
  vjepa_k: shape=(2196, 27), dtype=float64
    [0,:20]=[  2.2088  -4.9836  17.6515 -16.4138  -2.6157   2.2057  11.5405  -1.2947   1.5851  -5.1795  -3.9728  -1.7456  -8.0904
  -0.258   -2.1483  -1.2844  -2.8475   4.0404   2.353   -1.6459]
  clip_k: shape=(2196, 27), dtype=float64
    [0,:20]=[-0.1322 -0.1878 -0.1276  0.0585 -0.0019  0.1962  0.0848 -0.0538  0.1221 -0.006   0.1592  0.0318 -0.0199 -0.1427
 -0.1102  0.1455 -0.0248 -0.0698  0.0496  0.0118]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']

--- raw_embedding_2d.npz ---
File: CCN2026/results/raw_embedding_2d.npz
Keys: ['emb_raw', 'emb_vjepa2', 'emb_clip', 'emb_overlay_raw', 'emb_overlay_vjepa', 'overlay_errors', 'dominant_emo', 'emotion_labels', 'procrustes_disparity', 'pca_var_explained']
  emb_raw: shape=(2196, 2), dtype=float32
    [0,:20]=[0.6148 0.2475]
  emb_vjepa2: shape=(2196, 2), dtype=float32
    [0,:20]=[0.248  0.0925]
  emb_clip: shape=(2196, 2), dtype=float32
    [0,:20]=[-0.3472  0.1236]
  emb_overlay_raw: shape=(2196, 2), dtype=float64
    [0,:20]=[-0.1616 -0.7157]
  emb_overlay_vjepa: shape=(2196, 2), dtype=float64
    [0,:20]=[-0.0024 -0.0013]
  overlay_errors: shape=(2196,), dtype=float64
    first 20=[0.7319 3.4489 1.0674 4.6526 1.0704 2.0288 1.3617 0.9885 0.8522 1.7801 1.0812 4.2861 0.5885 1.2076 1.3142 4.7719 1.9707
 1.7389 1.226  5.0306]
  dominant_emo: shape=(2196,), dtype=int64
    first 20=[22 24  3  3 10 24  2  2 28 30  3  3  3 32 19  2 10 30 12  2]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  procrustes_disparity: shape=(), dtype=float64
    values=0.914
  pca_var_explained: shape=(), dtype=float64
    values=54.253

--- raw_exp12_14d_results.npz ---
File: CCN2026/results/raw_exp12_14d_results.npz
Keys: ['metadata_path', 'fmri_path', 'target_names', 'emotion_labels', 'dim_labels', 'dim_cols', 'k_values', 'mean_cat', 'mean_dim', 'cat_dim_ratio', 'r2_k27', 'r2_full']
  metadata_path: shape=(1,), dtype=<U113
    values=['/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv']
  fmri_path: shape=(1,), dtype=<U57
    values=['/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy']
  target_names: shape=(48,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment'
 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity' 'Obstruction' 'Safety' 'Upswing' 'Valence']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(14,), dtype=<U11
    values=['Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment' 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity'
 'Obstruction' 'Safety' 'Upswing' 'Valence']
  dim_cols: shape=(14,), dtype=<U17
    values=['approach_score' 'arousal_score' 'attention_score' 'certainty_score' 'commitment_score' 'control_score'
 'dominance_score' 'effort_score' 'fairness_score' 'identity_score' 'obstruction_score' 'safety_score' 'upswing_score'
 'valence_score']
  k_values: shape=(14,), dtype=int64
    values=[  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  mean_cat: shape=(14,), dtype=float64
    values=[0.033  0.0523 0.0683 0.0865 0.0921 0.1018 0.1061 0.1075 0.1088 0.1102 0.1112 0.114  0.1166 0.1154]
  mean_dim: shape=(14,), dtype=float64
    values=[0.0428 0.0544 0.0785 0.1223 0.1237 0.1428 0.1501 0.1557 0.1589 0.1586 0.1579 0.1636 0.1726 0.1779]
  cat_dim_ratio: shape=(14,), dtype=float64
    values=[0.7721 0.9619 0.87   0.7071 0.7443 0.7126 0.707  0.6907 0.6845 0.6945 0.7042 0.6968 0.6751 0.6489]
  r2_k27: shape=(48,), dtype=float64
    values=[0.0276 0.1391 0.2335 0.2126 0.0476 0.1889 0.134  0.0728 0.0836 0.1131 0.0761 0.0115 0.072  0.0222 0.267  0.0951 0.2107
 0.     0.0662 0.1857 0.     0.1319 0.127  0.1288 0.1161 0.0203 0.0823 0.1102 0.0418 0.0481 0.3226 0.1789 0.0321 0.0571
 0.2155 0.0681 0.0745 0.1735 0.1353 0.2436 0.049  0.1821 0.1613 0.1281 0.1041 0.2493 0.1771 0.2181]
  r2_full: shape=(48,), dtype=float64
    values=[0.     0.     0.1351 0.0774 0.     0.051  0.     0.     0.     0.     0.     0.     0.     0.     0.1205 0.     0.1107
 0.     0.     0.0626 0.     0.0021 0.     0.     0.     0.     0.     0.     0.     0.     0.2919 0.0265 0.     0.
 0.1286 0.     0.     0.0139 0.     0.1624 0.     0.0752 0.0657 0.     0.     0.1677 0.0949 0.1461]

--- raw_k_sweep_results.npz ---
File: CCN2026/results/raw_k_sweep_results.npz
Keys: ['k_values', 'disp_raw_vjepa', 'disp_raw_clip', 'decoding_raw', 'decoding_vjepa', 'decoding_clip', 'k_elbow', 'k_plateau', 'brainjp_r2_ref', 'brainjp_disp_ref']
  k_values: shape=(14,), dtype=int64
    values=[  3   5   7  10  15  20  25  27  30  34  40  50  75 100]
  disp_raw_vjepa: shape=(14,), dtype=float64
    values=[0.9287 0.9183 0.919  0.9135 0.9111 0.9135 0.9133 0.914  0.9147 0.9147 0.9142 0.9137 0.9124 0.9113]
  disp_raw_clip: shape=(14,), dtype=float64
    values=[0.9365 0.9043 0.895  0.8941 0.8987 0.8997 0.9022 0.9031 0.9033 0.9036 0.9043 0.9046 0.9054 0.9055]
  decoding_raw: shape=(14,), dtype=float64
    values=[0.033  0.0523 0.0683 0.0865 0.0921 0.1017 0.1061 0.1074 0.1088 0.1104 0.1112 0.1137 0.1169 0.115 ]
  decoding_vjepa: shape=(14,), dtype=float64
    values=[0.055  0.0726 0.0797 0.0955 0.1136 0.1198 0.1291 0.1317 0.1331 0.1399 0.1463 0.1564 0.1677 0.1706]
  decoding_clip: shape=(14,), dtype=float64
    values=[0.0941 0.1366 0.1884 0.2116 0.2361 0.2535 0.2654 0.2694 0.2744 0.282  0.2836 0.2897 0.2931 0.2907]
  k_elbow: shape=(), dtype=int64
    values=5
  k_plateau: shape=(), dtype=int64
    values=40
  brainjp_r2_ref: shape=(14,), dtype=float64
    values=[0.0156 0.0226 0.0346 0.0428 0.0488 0.0537 0.0561 0.0561 0.0568 0.0583 0.059  0.0606 0.0574 0.0543]
  brainjp_disp_ref: shape=(14,), dtype=float64
    values=[0.9316 0.9383 0.9427 0.9404 0.9355 0.9372 0.9376 0.938  0.9387 0.9386 0.939  0.9396 0.9404 0.9406]

--- raw_rsa_cka_results.npz ---
File: CCN2026/results/raw_rsa_cka_results.npz
Keys: ['cross_subj_r_mat', 'cross_subj_off_diag_mean', 'cross_subj_off_diag_std', 'rsm_mean_stats', 'emotion_labels', 'rsa_raw', 'rsa_vjepa2', 'rsa_clip', 'alignment', 'divergence', 'rsa_raw_per_subj', 'cka_mean_vjepa', 'cka_mean_clip', 'cka_delta', 'cka_vjepa_per_subj', 'cka_clip_per_subj', 'cka_delta_per_subj', 'perm_cka_vjepa', 'perm_cka_clip', 'perm_delta', 'p_val_vjepa', 'p_val_clip', 'p_val_delta', 'boot_cka_vjepa', 'boot_cka_clip', 'boot_delta', 'ci_vjepa', 'ci_clip', 'ci_delta']
  cross_subj_r_mat: shape=(5, 5), dtype=float64
    values=[[1.     0.0886 0.0776 0.0606 0.0612]
 [0.0886 1.     0.126  0.0852 0.0949]
 [0.0776 0.126  1.     0.0831 0.0876]
 [0.0606 0.0852 0.0831 1.     0.066 ]
 [0.0612 0.0949 0.0876 0.066  1.    ]]
  cross_subj_off_diag_mean: shape=(), dtype=float64
    values=0.0831
  cross_subj_off_diag_std: shape=(), dtype=float64
    values=0.0183
  rsm_mean_stats: shape=(4,), dtype=float64
    values=[-8.2607e-01  1.0000e+00  9.5496e-04  1.7534e-01]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  rsa_raw: shape=(34,), dtype=float64
    values=[0.0057 0.0179 0.042  0.0116 0.0139 0.0224 0.0108 0.0097 0.0091 0.0254 0.013  0.0019 0.019  0.0075 0.0207 0.0263 0.0272
 0.0071 0.0119 0.0232 0.0024 0.0247 0.0117 0.0143 0.0181 0.005  0.0172 0.0234 0.0157 0.008  0.0303 0.0351 0.0208 0.0173]
  rsa_vjepa2: shape=(34,), dtype=float64
    values=[ 0.0146  0.0919 -0.1273  0.1803  0.0283  0.0393 -0.0067  0.0446 -0.0431 -0.0822  0.0277 -0.0011  0.0045  0.0236
  0.064   0.048  -0.1031 -0.0086  0.0203  0.0625  0.0171  0.0678 -0.0571  0.0984  0.0085  0.013   0.0336  0.0187
  0.042   0.0011  0.0303  0.151   0.073   0.038 ]
  rsa_clip: shape=(34,), dtype=float64
    values=[-0.014   0.0815 -0.0027  0.1335  0.0315  0.1299  0.0918  0.0145 -0.0931 -0.0529  0.0931 -0.0192  0.0166 -0.0012
  0.0447  0.0564  0.019  -0.0149  0.016   0.151   0.0096  0.1356  0.0479  0.0178 -0.0175 -0.0186  0.0478  0.0425
  0.0403 -0.0105  0.066   0.22    0.0634  0.0135]
  alignment: shape=(34,), dtype=float64
    values=[ 0.0057  0.0179 -0.1273  0.0116  0.0139  0.0224 -0.0067  0.0097 -0.0431 -0.0822  0.013  -0.0011  0.0045  0.0075
  0.0207  0.0263 -0.1031 -0.0086  0.0119  0.0232  0.0024  0.0247 -0.0571  0.0143  0.0085  0.005   0.0172  0.0187
  0.0157  0.0011  0.0303  0.0351  0.0208  0.0173]
  divergence: shape=(34,), dtype=float64
    values=[8.9020e-03 7.4050e-02 1.6929e-01 1.6872e-01 1.4389e-02 1.6872e-02 1.7434e-02 3.4911e-02 5.2144e-02 1.0757e-01
 1.4698e-02 3.0015e-03 1.4433e-02 1.6130e-02 4.3292e-02 2.1750e-02 1.3032e-01 1.5715e-02 8.3986e-03 3.9281e-02
 1.4608e-02 4.3132e-02 6.8830e-02 8.4152e-02 9.6194e-03 8.0338e-03 1.6444e-02 4.7025e-03 2.6251e-02 6.8963e-03
 1.3735e-05 1.1589e-01 5.2201e-02 2.0757e-02]
  rsa_raw_per_subj: shape=(5, 34), dtype=float64
    first row=[0.0011 0.0082 0.0292 0.0038 0.0063 0.0072 0.0075 0.002  0.0045 0.0195 0.0027 0.0003 0.0108 0.0039 0.007  0.0078 0.0161
 0.008  0.0085 0.0086 0.0008 0.0068 0.0077 0.0053 0.0116 0.0008 0.008  0.0175 0.0045 0.0072 0.018  0.0111 0.0073 0.0065]
  cka_mean_vjepa: shape=(), dtype=float64
    values=0.1515
  cka_mean_clip: shape=(), dtype=float64
    values=0.1702
  cka_delta: shape=(), dtype=float64
    values=-0.0187
  cka_vjepa_per_subj: shape=(5,), dtype=float64
    values=[0.0698 0.0958 0.0919 0.0639 0.0761]
  cka_clip_per_subj: shape=(5,), dtype=float64
    values=[0.076  0.1101 0.0985 0.0784 0.0838]
  cka_delta_per_subj: shape=(5,), dtype=float64
    values=[-0.0063 -0.0143 -0.0066 -0.0145 -0.0077]
  perm_cka_vjepa: shape=(1000,), dtype=float64
    first 20=[0.0117 0.0117 0.0129 0.0131 0.0123 0.0123 0.0147 0.0124 0.012  0.0126 0.013  0.0127 0.0117 0.0131 0.0119 0.0114 0.0125
 0.0124 0.0126 0.0122]
  perm_cka_clip: shape=(1000,), dtype=float64
    first 20=[0.0176 0.0167 0.0181 0.0184 0.0174 0.0184 0.0181 0.018  0.0175 0.0179 0.017  0.0184 0.0172 0.0171 0.0175 0.0174 0.0187
 0.0172 0.018  0.0174]
  perm_delta: shape=(1000,), dtype=float64
    first 20=[-0.0059 -0.005  -0.0052 -0.0054 -0.0051 -0.0061 -0.0034 -0.0057 -0.0055 -0.0052 -0.0041 -0.0056 -0.0055 -0.0041
 -0.0056 -0.0059 -0.0062 -0.0048 -0.0054 -0.0052]
  p_val_vjepa: shape=(), dtype=float64
    values=0.
  p_val_clip: shape=(), dtype=float64
    values=0.
  p_val_delta: shape=(), dtype=float64
    values=1.
  boot_cka_vjepa: shape=(1000,), dtype=float64
    first 20=[0.1604 0.1607 0.1659 0.161  0.1694 0.1558 0.1688 0.1602 0.1668 0.1688 0.1725 0.1704 0.163  0.1672 0.1576 0.1667 0.16
 0.1629 0.1643 0.1557]
  boot_cka_clip: shape=(1000,), dtype=float64
    first 20=[0.1818 0.1906 0.1909 0.182  0.1849 0.1752 0.1892 0.1807 0.1874 0.1844 0.1869 0.189  0.1778 0.1876 0.1885 0.1922 0.1799
 0.1865 0.1862 0.1811]
  boot_delta: shape=(1000,), dtype=float64
    first 20=[-0.0214 -0.0299 -0.025  -0.021  -0.0155 -0.0194 -0.0204 -0.0204 -0.0206 -0.0156 -0.0144 -0.0186 -0.0148 -0.0204
 -0.0309 -0.0256 -0.0199 -0.0236 -0.0219 -0.0255]
  ci_vjepa: shape=(2,), dtype=float64
    values=[0.151  0.1734]
  ci_clip: shape=(2,), dtype=float64
    values=[0.1751 0.1938]
  ci_delta: shape=(2,), dtype=float64
    values=[-0.0321 -0.0128]

--- subject_cka_results.npz ---
File: CCN2026/results/subject_cka_results.npz
Keys: ['cka_vjepa_per_subj', 'cka_clip_per_subj', 'delta_per_subj', 'mean_cka_vjepa', 'mean_cka_clip']
  cka_vjepa_per_subj: shape=(5,), dtype=float64
    values=[0.0548 0.0633 0.0554 0.0458 0.0726]
  cka_clip_per_subj: shape=(5,), dtype=float64
    values=[0.0474 0.06   0.0508 0.0513 0.0603]
  delta_per_subj: shape=(5,), dtype=float64
    values=[ 0.0075  0.0033  0.0046 -0.0054  0.0123]
  mean_cka_vjepa: shape=(), dtype=float64
    values=0.0584
  mean_cka_clip: shape=(), dtype=float64
    values=0.0539

--- vision_semantic_partial_results.npz ---
File: CCN2026/results/vision_semantic_partial_results.npz
Keys: ['source_names', 'model_names', 'rsa_original', 'rsa_partial', 'rsa_pvalue', 'emotion_labels', 'dim_labels', 'target_names', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_original_vjepa', 'r2_partial_vjepa', 'r2_original_clip', 'r2_partial_clip']
  source_names: shape=(2,), dtype=<U10
    values=['Brain-JEPA' 'Raw fMRI']
  model_names: shape=(2,), dtype=<U7
    values=['V-JEPA2' 'CLIP']
  rsa_original: shape=(2, 2), dtype=float64
    values=[[-0.0071 -0.0697]
 [ 0.0956  0.0886]]
  rsa_partial: shape=(2, 2), dtype=float64
    values=[[-0.0045 -0.0686]
 [ 0.0776  0.0717]]
  rsa_pvalue: shape=(2, 2), dtype=float64
    values=[[2.8123e-12 0.0000e+00]
 [0.0000e+00 0.0000e+00]]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(3,), dtype=<U9
    values=['Arousal' 'Valence' 'Dominance']
  target_names: shape=(37,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Arousal' 'Valence' 'Dominance']
  pred_idx_vjepa: shape=(3,), dtype=int64
    values=[0 1 2]
  pred_idx_clip: shape=(6,), dtype=int64
    values=[0 1 2 4 5 6]
  r2_original_vjepa: shape=(37,), dtype=float64
    values=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045  0.0059 0.0128 0.1715 0.1057 0.0293 0.0518
 0.0651 0.0112 0.    ]
  r2_partial_vjepa: shape=(37,), dtype=float64
    values=[0.     0.0072 0.0515 0.0042 0.     0.0004 0.     0.     0.     0.061  0.     0.     0.0053 0.     0.     0.     0.0097
 0.     0.0068 0.002  0.     0.     0.     0.     0.0027 0.003  0.     0.     0.0019 0.0055 0.0028 0.0077 0.0022 0.
 0.0088 0.     0.    ]
  r2_original_clip: shape=(37,), dtype=float64
    values=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308 0.1959 0.0436 0.5379 0.1882 0.103  0.1211
 0.0621 0.2706 0.0565]
  r2_partial_clip: shape=(37,), dtype=float64
    values=[0.     0.     0.0935 0.0494 0.0145 0.0145 0.     0.     0.     0.0564 0.     0.     0.     0.     0.0038 0.002  0.0259
 0.0053 0.0323 0.0235 0.     0.     0.0192 0.0028 0.0162 0.0031 0.     0.041  0.0306 0.     0.0095 0.0087 0.0034 0.
 0.     0.0258 0.    ]

--- vision_semantic_partial_results_14d.npz ---
File: CCN2026/results/vision_semantic_partial_results_14d.npz
Keys: ['metadata_path', 'source_names', 'model_names', 'emotion_labels', 'dim_labels', 'dim_cols', 'target_names', 'rsa_original', 'rsa_partial', 'rsa_pvalue', 'pred_idx_vjepa', 'pred_idx_clip', 'r2_original_vjepa', 'r2_partial_vjepa', 'r2_original_clip', 'r2_partial_clip']
  metadata_path: shape=(1,), dtype=<U113
    values=['/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv']
  source_names: shape=(2,), dtype=<U10
    values=['Brain-JEPA' 'Raw fMRI']
  model_names: shape=(2,), dtype=<U7
    values=['V-JEPA2' 'CLIP']
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']
  dim_labels: shape=(14,), dtype=<U11
    values=['Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment' 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity'
 'Obstruction' 'Safety' 'Upswing' 'Valence']
  dim_cols: shape=(14,), dtype=<U17
    values=['approach_score' 'arousal_score' 'attention_score' 'certainty_score' 'commitment_score' 'control_score'
 'dominance_score' 'effort_score' 'fairness_score' 'identity_score' 'obstruction_score' 'safety_score' 'upswing_score'
 'valence_score']
  target_names: shape=(48,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt' 'Approach' 'Arousal' 'Attention' 'Certainty' 'Commitment'
 'Control' 'Dominance' 'Effort' 'Fairness' 'Identity' 'Obstruction' 'Safety' 'Upswing' 'Valence']
  rsa_original: shape=(2, 2), dtype=float64
    values=[[-0.0071 -0.0697]
 [ 0.0956  0.0886]]
  rsa_partial: shape=(2, 2), dtype=float64
    values=[[-0.0045 -0.0686]
 [ 0.0776  0.0717]]
  rsa_pvalue: shape=(2, 2), dtype=float64
    values=[[2.8123e-12 0.0000e+00]
 [0.0000e+00 0.0000e+00]]
  pred_idx_vjepa: shape=(3,), dtype=int64
    values=[0 1 2]
  pred_idx_clip: shape=(6,), dtype=int64
    values=[0 1 2 4 5 6]
  r2_original_vjepa: shape=(48,), dtype=float64
    values=[0.0235 0.0805 0.3231 0.1159 0.0118 0.0611 0.0222 0.0308 0.0196 0.1361 0.     0.     0.0166 0.0088 0.0741 0.0024 0.2001
 0.     0.057  0.0598 0.0028 0.0167 0.0576 0.0793 0.0094 0.0071 0.0313 0.045  0.0059 0.0128 0.1715 0.1057 0.0293 0.0518
 0.0266 0.0651 0.048  0.0256 0.0653 0.0443 0.     0.024  0.007  0.0287 0.0147 0.0685 0.     0.0112]
  r2_partial_vjepa: shape=(48,), dtype=float64
    values=[0.0000e+00 7.2451e-03 5.1488e-02 4.2377e-03 0.0000e+00 3.9496e-04 0.0000e+00 0.0000e+00 0.0000e+00 6.1010e-02
 0.0000e+00 0.0000e+00 5.3326e-03 0.0000e+00 0.0000e+00 0.0000e+00 9.6839e-03 0.0000e+00 6.7757e-03 1.9762e-03
 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 2.7115e-03 2.9824e-03 0.0000e+00 0.0000e+00 1.8578e-03 5.4933e-03
 2.7991e-03 7.7306e-03 2.2437e-03 0.0000e+00 1.3652e-03 8.7950e-03 0.0000e+00 0.0000e+00 3.8012e-05 7.1606e-03
 0.0000e+00 1.2020e-02 0.0000e+00 0.0000e+00 0.0000e+00 7.5965e-03 0.0000e+00 0.0000e+00]
  r2_original_clip: shape=(48,), dtype=float64
    values=[0.0266 0.1424 0.4473 0.3397 0.1818 0.2036 0.2096 0.0913 0.1011 0.1655 0.0291 0.0493 0.1482 0.0847 0.1964 0.0564 0.2866
 0.0385 0.1709 0.2536 0.0289 0.21   0.1818 0.1236 0.1922 0.0544 0.1058 0.3308 0.1959 0.0436 0.5379 0.1882 0.103  0.1211
 0.2473 0.0621 0.0575 0.1748 0.1071 0.3156 0.0565 0.1882 0.2771 0.116  0.1441 0.3259 0.1793 0.2706]
  r2_partial_clip: shape=(48,), dtype=float64
    values=[0.     0.     0.0935 0.0494 0.0145 0.0145 0.     0.     0.     0.0564 0.     0.     0.     0.     0.0038 0.002  0.0259
 0.0053 0.0323 0.0235 0.     0.     0.0192 0.0028 0.0162 0.0031 0.     0.041  0.0306 0.     0.0095 0.0087 0.0034 0.
 0.0181 0.     0.0037 0.0148 0.     0.068  0.     0.0107 0.0371 0.0003 0.0184 0.0549 0.0161 0.0258]

--- main/comprehensive_interpretation.npz ---
File: main/results/comprehensive_interpretation.npz
Keys: ['emo_mean', 'emo_std', 'emo_skewness', 'emo_nonzero', 'emo_range', 'r2_vs_std_r', 'r2_vs_std_p', 'r2_vs_mean_r', 'r2_vs_mean_p', 'r2_fmri_to_vpc', 'r2_bj_to_vpc', 'r2_fmri_emo', 'r2_bj_emo', 'r2_vjepa_emo', 'emo_pca_var', 'r2_residual', 'emotion_labels']
  emo_mean: shape=(34,), dtype=float64
    values=[0.0363 0.0586 0.0787 0.2038 0.0166 0.0662 0.1074 0.0273 0.0444 0.037  0.0623 0.0105 0.0221 0.0139 0.0874 0.0265 0.0436
 0.0075 0.0482 0.0785 0.0046 0.064  0.1133 0.0811 0.0331 0.0071 0.0184 0.0308 0.0475 0.0412 0.0526 0.091  0.0331 0.0194]
  emo_std: shape=(34,), dtype=float64
    values=[0.0708 0.1218 0.1537 0.233  0.0592 0.1253 0.1407 0.0694 0.0817 0.0874 0.105  0.0324 0.1139 0.0419 0.1985 0.0785 0.0891
 0.0272 0.0818 0.154  0.0204 0.1392 0.1303 0.1286 0.1119 0.0318 0.0641 0.1268 0.1247 0.0671 0.1796 0.1186 0.0765 0.0608]
  emo_skewness: shape=(34,), dtype=float64
    values=[2.4355 2.5684 2.3676 1.0212 4.6162 2.6404 1.4228 4.1837 2.7108 3.595  2.5356 3.7281 6.2672 3.8894 2.7383 4.307  2.6406
 4.2868 2.2809 2.2666 4.9187 2.7956 1.46   1.9997 4.3318 7.4936 5.0343 4.68   3.661  1.993  3.779  1.5907 3.1944 4.3928]
  emo_nonzero: shape=(34,), dtype=float64
    values=[0.2778 0.2832 0.3329 0.6407 0.1066 0.352  0.5246 0.2099 0.3329 0.2523 0.3989 0.1125 0.0724 0.1266 0.2842 0.1617 0.2846
 0.0806 0.3629 0.3128 0.0524 0.2828 0.6352 0.4294 0.1448 0.0656 0.1207 0.0861 0.2227 0.3543 0.122  0.5246 0.2304 0.1393]
  emo_range: shape=(34,), dtype=float64
    values=[0.5    0.8333 0.8182 1.     0.5454 0.9167 0.7    0.75   0.6667 0.6923 0.9    0.3462 1.     0.3846 1.     0.8333 0.6364
 0.2727 0.5833 0.9091 0.2308 0.9167 0.6923 0.7273 0.8182 0.6364 0.6364 0.9231 0.9167 0.5833 1.     0.75   0.7    0.5454]
  r2_vs_std_r: shape=(), dtype=float64
    values=0.4797
  r2_vs_std_p: shape=(), dtype=float64
    values=0.0041
  r2_vs_mean_r: shape=(), dtype=float64
    values=0.3842
  r2_vs_mean_p: shape=(), dtype=float64
    values=0.0249
  r2_fmri_to_vpc: shape=(10,), dtype=float64
    values=[0.354  0.2274 0.3068 0.1469 0.0825 0.0361 0.     0.     0.0036 0.    ]
  r2_bj_to_vpc: shape=(10,), dtype=float64
    values=[3.7284e-01 7.4791e-02 8.7770e-02 3.1729e-04 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00 0.0000e+00]
  r2_fmri_emo: shape=(36,), dtype=float64
    values=[0.     0.     0.1351 0.0774 0.     0.051  0.     0.     0.     0.     0.     0.     0.     0.     0.1205 0.     0.1107
 0.     0.     0.0626 0.     0.0021 0.     0.     0.     0.     0.     0.     0.     0.     0.2919 0.0265 0.     0.
 0.     0.1461]
  r2_bj_emo: shape=(36,), dtype=float64
    values=[0.     0.     0.0821 0.     0.     0.0026 0.     0.     0.     0.     0.     0.     0.     0.     0.0327 0.     0.0387
 0.     0.     0.     0.     0.0011 0.     0.     0.     0.     0.     0.0006 0.     0.     0.192  0.     0.     0.
 0.     0.0652]
  r2_vjepa_emo: shape=(36,), dtype=float64
    values=[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  emo_pca_var: shape=(34,), dtype=float64
    values=[0.1969 0.1304 0.1011 0.0809 0.0626 0.0468 0.0404 0.0363 0.0309 0.0295 0.0262 0.0247 0.0229 0.0196 0.0168 0.0155 0.012
 0.0115 0.0111 0.0103 0.0094 0.009  0.0088 0.0078 0.0072 0.0069 0.0059 0.0052 0.0046 0.0028 0.0018 0.0017 0.0015 0.0008]
  r2_residual: shape=(34,), dtype=float64
    values=[0.0291 0.0895 0.327  0.1504 0.0121 0.025  0.0249 0.0195 0.0149 0.1225 0.     0.     0.012  0.0094 0.0834 0.0046 0.1943
 0.     0.0386 0.0243 0.0069 0.     0.0532 0.117  0.002  0.0078 0.0196 0.0441 0.0137 0.0204 0.197  0.0802 0.028  0.0538]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']

--- main/deep_analysis.npz ---
File: main/results/deep_analysis.npz
Keys: ['vjepa_separability', 'emo_max_corr', 'emo_strong', 'r2_ranked', 'r2_raw_fwd', 'r2_raw_rev', 'r2_raw_pred_emo', 'raw_pred_mask', 'vp_results', 'r2_brain_resid', 'clusters_3', 'clusters_5', 'emo_profiles_bp', 'r_mantel_sb', 'r_mantel_sbeh', 'r_mantel_bbeh', 'r_partial_mantel', 'p_partial_mantel', 'r2_clip_fwd', 'emotion_labels']
  vjepa_separability: shape=(34,), dtype=float64
    values=[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  emo_max_corr: shape=(34,), dtype=float64
    values=[0.3648 0.6229 0.5573 0.3642 0.4413 0.7636 0.3516 0.2177 0.1964 0.5113 0.2032 0.4413 0.1534 0.4121 0.3991 0.4332 0.5573
 0.2273 0.3493 0.7636 0.3533 0.5339 0.3615 0.6229 0.1765 0.3918 0.292  0.3057 0.6259 0.3408 0.3057 0.2161 0.6259 0.3918]
  emo_strong: shape=(34,), dtype=float64
    values=[0.01   0.0638 0.0997 0.2964 0.0128 0.0606 0.1125 0.0128 0.0219 0.0291 0.0433 0.0005 0.0255 0.0018 0.1088 0.0205 0.0319
 0.     0.0223 0.1056 0.     0.076  0.0974 0.0783 0.041  0.0009 0.0132 0.0405 0.0505 0.0077 0.0669 0.0697 0.0209 0.0123]
  r2_ranked: shape=(34,), dtype=float64
    values=[0.0114 0.0762 0.2618 0.1147 0.0163 0.0657 0.0202 0.0383 0.0157 0.0877 0.     0.     0.0461 0.0124 0.071  0.0042 0.1844
 0.     0.0417 0.0658 0.0011 0.0128 0.0548 0.0577 0.     0.0085 0.0355 0.0676 0.0106 0.0032 0.1462 0.1279 0.0384 0.083 ]
  r2_raw_fwd: shape=(20,), dtype=float64
    values=[0.354  0.2274 0.3068 0.1469 0.0825 0.0361 0.     0.     0.0036 0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.    ]
  r2_raw_rev: shape=(20,), dtype=float64
    values=[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  r2_raw_pred_emo: shape=(36,), dtype=float64
    values=[0.0271 0.0818 0.3717 0.1568 0.0297 0.1082 0.0758 0.0647 0.0975 0.1564 0.003  0.0132 0.0347 0.0095 0.0769 0.0115 0.2427
 0.     0.0587 0.1113 0.0042 0.0387 0.081  0.0909 0.0457 0.0178 0.0425 0.0908 0.0237 0.0125 0.2008 0.1126 0.0377 0.0622
 0.0698 0.0209]
  raw_pred_mask: shape=(20,), dtype=bool
    values=[ True  True  True  True  True  True False False False False False False False False False False False False False
 False]
  vp_results: shape=(34, 4), dtype=float64
    first row=[0.     0.     0.0235 0.    ]
  r2_brain_resid: shape=(36,), dtype=float64
    values=[0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.     0.
 0.     0.0081]
  clusters_3: shape=(34,), dtype=int32
    values=[3 3 1 3 3 2 2 3 1 1 2 3 1 3 3 3 1 1 2 2 3 2 2 3 1 3 2 1 3 2 1 2 3 3]
  clusters_5: shape=(34,), dtype=int32
    values=[5 4 1 5 5 3 2 4 1 1 3 5 1 5 4 5 1 1 3 3 5 3 2 5 1 5 3 1 5 3 1 3 5 5]
  emo_profiles_bp: shape=(34, 3), dtype=float64
    first row=[ 3.1678 -0.7556  2.1949]
  r_mantel_sb: shape=(), dtype=float64
    values=0.075
  r_mantel_sbeh: shape=(), dtype=float64
    values=0.1596
  r_mantel_bbeh: shape=(), dtype=float64
    values=-0.0389
  r_partial_mantel: shape=(), dtype=float64
    values=-0.0314
  p_partial_mantel: shape=(), dtype=float64
    values=1.4364e-28
  r2_clip_fwd: shape=(10,), dtype=float64
    values=[0.2613 0.1559 0.1271 0.     0.1154 0.0167 0.0125 0.     0.     0.    ]
  emotion_labels: shape=(34,), dtype=<U22
    values=['Admiration' 'Adoration' 'Aesthetic appreciation' 'Amusement' 'Anger' 'Anxiety' 'Awe' 'Awkwardness' 'Boredom'
 'Calmness' 'Confusion' 'Contempt' 'Craving' 'Disgust' 'Empathic pain' 'Entrancement' 'Excitement' 'Fear' 'Horror'
 'Interest' 'Joy' 'Nostalgia' 'Relief' 'Romance' 'Sadness' 'Satisfaction' 'Sexual desire' 'Surprise' 'Sympathy'
 'Triumph' 'Uncomfortable' 'Annoyance' 'Envy' 'Guilt']