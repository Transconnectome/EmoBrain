# FEELIN: Toward an Emotion-Specific Brain Foundation Model

> Where does emotion signal live in brain foundation models, and what training regime makes it transferable?

---

| **Goal** | **Research Question** | **Research Gap** |
|---|---|---|
| Build a brain foundation model whose representations preserve emotion-relevant structure across datasets, stimuli, subjects, and target types. | How can we develop a brain foundation model that best captures emotion-relevant representation across naturalistic fMRI datasets and emotion tasks? | Three silos that do not connect: fMRI BFMs (SwiFT, Brain-JEPA, NeuroSTORM) lack emotion specificity; stimulus→brain models (TRIBE) optimize encoding not emotion; affective FMs (AffectGPT, VidEmo) lack brain grounding. |
| BFMs exist but are not emotion-specific. Affective FMs exist but lack brain grounding. | Sub: where does emotion signal live? does resting-state pretraining help? which target is robust? does multimodal context add value? | FEELIN bridges all three. |

---

## Strategy Roadmap

```
                    ╔═══════════════════════════════════════╗
                    ║         PHASE 1 — BENCHMARK            ║
                    ║                                        ║
                    ║   Map where emotion signal lives       ║
                    ║   across Datasets × BFMs × Tasks       ║
                    ╚═══════════════════╦═══════════════════╝
                                        ║
                                        ║   results inform branching
                                        ║
                ┌═══════════════════════╩═══════════════════════┐
                ║                                               ║
                ▼                                               ▼
╔═══════════════════════════════╗               ╔═══════════════════════════════╗
║          BRANCH A              ║               ║          BRANCH B              ║
║   Pretraining + Adaptation     ║               ║   Multimodal Brain–Stimulus    ║
║                                ║               ║                                ║
║  • task / movie fMRI           ║               ║  • TRIBE-style                 ║
║    pretraining                 ║               ║    stimulus-to-brain           ║
║  • masked / JEPA / contrastive ║               ║    alignment                   ║
║    objectives                  ║               ║  • video/audio/text features   ║
║  • adapters, affective heads,  ║               ║    as controls and teachers    ║
║    subject adaptation          ║               ║  • late fusion, joint latent   ║
╚═══════════════╦═══════════════╝               ╚═══════════════╦═══════════════╝
                ║                                               ║
                └═══════════════════════╦═══════════════════════┘
                                        ▼
                    ╔═══════════════════════════════════════╗
                    ║   Emotion-Specific Brain Foundation    ║
                    ║              Model                     ║
                    ╚═══════════════════════════════════════╝
```

FEELIN | Transconnectome Lab | 2026
