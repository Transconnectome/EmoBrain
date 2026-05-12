# FEELIN Phase 1 Benchmark

> Datasets × Models × Tasks

---

| **Datasets** | **Models × Init** | **Tasks** |
|---|---|---|
| **Horikawa / Cowen**<br>5 subjects. 2,185 short emotion-evoking videos. 34 categories + 14 affective dimension ratings. | **SwiFT**<br>resting-pretrained ckpt (Transconnectome lab) / scratch random init. 4D fMRI volume input. | **Level 0 — High / Low Valence / Arousal**<br>단순화된 binary classification |
| **Emo-FilM**<br>30 subjects. 14 short films. 50 emotion / component / appraisal annotations. TR 1.3 s. | **Brain-JEPA**<br>resting-pretrained jepa-ep300.pth (ABCD) / scratch random init. ROI time-series input. | **Level 1 — Valence / Arousal regression**<br>연속 차원 수치 |
| **REELMO**<br>1 long video (Jojo Rabbit). 20 fMRI participants. 20-category affect trajectory at 1 s resolution. | **NeuroSTORM**<br>resting-pretrained pt_neurostorm_mae_ratio0.5.ckpt / scratch random init. Raw 4D fMRI input. | **Level 2 — One-hot classification**<br>이산 카테고리 Top-1 label |
| **Koide-Majima / Nishimoto**<br>8 subjects. 135 movie clips (10–20 s). 80-emotion high-dimensional ratings. | | **Level 3 — Multi-label classification**<br>이산 카테고리 속 분포 |
| **IAPS / OASIS / NSD**<br>Static image fMRI. valence / arousal / category targets. | | **Level 4 — Continuous dynamics regression**<br>시계열 감정 변화 |

---

FEELIN | Phase 1 Benchmark | 2026
