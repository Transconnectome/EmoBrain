> ⚠️ **ARCHIVED — 역사 기록. 현행 문서가 아니다.**
> 현행 논증 = `docs/paper_logic_merged.md` (대전제 · RQ · 가설 H1–H4). 운영 규칙 = `CLAUDE.md`.
>
> 아래 내용 중 다음은 **뒤집혔다.** (a) Qwen3-VL 등 LLM backbone 사용 — 금지.
> (b) open-vocabulary / cross-taxonomy 전이를 headline novelty 로 삼는 프레임 — 폐기.
> (c) 학습에 없던 감정 zero-shot — 폐기(원칙적 분할 기준 없음, RQ 와 무관).
> (d) "EmoBrain 과 EmoViS 는 별도 논문 2편" — 현재는 **한 편의 논문**.
> (e) "EmoBrain 은 cortical location 을 주장하지 않는다" — 현재 **H3 이 cortical location 주장**이다.

# EmoBrain Framework

> **SUPERSEDED 2026-08-17 — LLM backbone removed.** The paper framing is being
> revised to the label-query direction in `docs/direction_v6_labelquery_20260817.md`
> (LLM-free; novelty = open-vocabulary emotion decoding FROM BRAIN + transfer). The
> Qwen3-VL-4B framing below is historical and pending rewrite.

## Working Title

**EmoBrain: Foundation-Model Transfer for Fine-Grained Emotion Decoding from
Short-Window Task fMRI**

EmoBrain asks what pretrained brain and vision representations transfer to
short-window, low-data task-fMRI, and whether video-semantic context available
during training can improve a brain-only decoder at inference.

The canonical model uses Qwen3-VL-4B and two encoder families: E1 ViT and E2
BFM, with Brain-JEPA and SwiFT as E2 variants. It predicts 34 independent emotion
endorsement scores. A context teacher receives brain, V-JEPA2 video, and
human-written MindCaptioning descriptions; a student receives brain only and is
trained with hard-label and teacher-output MSE.

The MindCaptioning paper describes its captions as crowdsourced detailed visual
descriptions with quality checking, not as affect-neutral annotations. We use
that precise terminology and assess possible affective shortcuts empirically.

The project does not use a raw-plus-BFM dual branch. BFM transfer is evaluated
through independent encoder conditions, pretrained-versus-scratch contrasts,
distillation benefit, short-window sensitivity, and neuroscientific analyses.
Planned extensions include cortical interpretation, visual/semantic controls,
cross-subject transfer, and cross-dataset generalization.
