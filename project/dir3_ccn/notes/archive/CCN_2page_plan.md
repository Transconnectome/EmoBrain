# CCN 2-Page Abstract Plan
## Neural Emotion Representations Are Aligned with Temporal Video Foundation Models

**Deadline:** April 2, 2026
**Data:** Horikawa et al. (2020) — 5 subjects, 2196 emotionally evocative videos, whole-brain fMRI

---

## What Horikawa Did (and Didn't Do)

| Horikawa 2020 | 우리 |
|---------------|------|
| Static/semantic visual features (AlexNet) | **Temporal video model (V-JEPA2)** |
| "감정은 categorical하게 표상됨" 확인 | 그 표상이 video model과 **얼마나, 어떻게** align되는가? |
| 5 subjects pooled → 공유 구조만 분석 | 공유 구조 + **개인 구조 분리** |

---

## Core Novel Claim

> Emotions are inherently **temporal** — fear builds, awe unfolds, nostalgia accumulates.
> We show that a temporal video foundation model (V-JEPA2) captures neural emotion representations
> significantly better than static models, and that this alignment varies systematically across emotion categories.

---

## Figure 1 — Temporal Video Model Aligns with Neural Emotion Representations

**Analysis:** CKA between V-JEPA2 RSM and Brain-JEPA RSM

- 5 subjects의 Brain-JEPA RSM (2196×2196) 계산
- V-JEPA2 RSM (2196×2196) 계산
- CKA alignment score (전체 + per emotion category)
- 비교 baseline: CLIP ViT-L/14 (static) vs V-JEPA2 (temporal)

**Expected result:**
- V-JEPA2 > CLIP in overall CKA alignment
- Alignment은 emotion category마다 다름
- Temporal dynamics가 강한 감정(awe, horror, excitement)에서 V-JEPA2 advantage가 큼

**Message:** 감정 신경 표상은 static visual content보다 temporal video dynamics와 더 잘 align된다

---

## Figure 2 — Shared vs Individual Structure in Neural Emotion Space

**Analysis:** Inter-subject RSA decomposition

- Per-subject RSM (raw fMRI, Schaefer 400 parcels)
- Shared component: mean RSM across 5 subjects
- Individual component: per-subject deviation from mean RSM

**Comparison:**
- Shared RSM → V-JEPA2와 high CKA (visually grounded)
- Individual RSM → V-JEPA2와 low CKA (beyond visual)
- Per-emotion: 어떤 감정이 더 individual한가?

**Message:**
- 공유 구조 = visually grounded (V-JEPA2가 설명)
- 개인 구조 = visual model이 설명 못함 → 개인 경험, affective processing

---

## Theoretical Grounding

| 연구 | 발견 | 우리 연구와의 관계 |
|------|------|-------------------|
| Horikawa 2020 | 감정 표상: high-dimensional, categorical, distributed | 공유 구조의 baseline |
| Conwell 2025 | Affectless visual machines explain majority of variance in **behavioral** affect | 우리는 **neural** 레벨로 확장 |
| Lee 2026 | 통증: 완전히 개인화, cross-subject transfer 실패 | 감정: 공유 구조가 강함 (대비) |
| Barrett 2017 | Complex emotions = individually constructed | Individual RSM에서 검증 |

---

## Novel Contributions

1. **첫 번째 temporal video foundation model (V-JEPA2) ↔ 감정 신경 표상 alignment 분석**
2. **신경 감정 표상의 공유/개인 성분 분리** + 각각이 video model로 설명되는 정도 비교
3. **감정 카테고리별 alignment 프로파일** — temporal dynamics가 중요한 감정 vs 그렇지 않은 감정

---

## Limitations (Be Honest)

- n=5 subjects: individual structure 해석에 통계적 한계
- Horikawa paradigm: 피험자별 behavioral emotion rating 없음 (crowd-sourced ratings만 존재)
- Brain-JEPA는 subject-invariant → individual structure는 raw fMRI로 분석

---

## Connection to Full Paper

```
CCN (이번):
    V-JEPA2 ↔ Brain-JEPA alignment (공유 구조)
    공유 vs 개인 성분 분리 (preliminary)
        ↓
Full Paper:
    Figure 1: Shared vs Individual structure (확장, 더 많은 피험자)
    Figure 2: Alignment profile across 34 emotion categories
    Figure 3: 공유 구조의 차원성 (~27)
    Figure 4: Brain Tuning — V-JEPA2를 Brain-JEPA에 align시켜 fine-tuning
```

---

## Timeline (3/30 ~ 4/2)

| 날짜 | 분석 | 코드 |
|------|------|------|
| 3/30 (오늘) | V-JEPA2 ↔ Brain-JEPA CKA 계산 | 05_cka_analysis.py |
| 3/31 | Raw fMRI 로드 + inter-subject RSA | 06_raw_fmri_rsa.py |
| 3/31 | Per-emotion alignment 분석 | 07_per_emotion_analysis.py |
| 4/1 | Figure 1, 2 제작 | 08_plot_figures.py |
| 4/1~2 | 글 작성 | CCN_draft.md |
| 4/2 | 제출 | |
