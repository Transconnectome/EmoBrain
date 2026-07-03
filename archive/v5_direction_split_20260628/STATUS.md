# v5 Three Directions archive

**시점.** 2026-06-28 pivot 로 archive 됐고, 2026-07-02 에 physical mv 완료.

## 이전 framing (superseded)

이 폴더 는 EmoBrain 의 이전 framing (2026-06-08 ~ 2026-06-28) 인 **Three Directions** 의 code / output / checkpoint 를 보존.

| Direction | 위치 | 상태 |
|-----------|------|------|
| D1 BrainVLM | `dir1_brainvlm/` (~174 GB) | Superseded. VA binary / regression 학습 실패 evidence (Pearson r 0.008-0.035 vs ROI ridge 0.416). Phase 1 negative result 의 base. |
| D2 fMRI-LM | `dir2_fmri_lm/` (~316 MB) | Superseded. Adapter scaffolding 만. 학습 미진행. |
| D3 CCN | `dir3_ccn/` (~2.1 GB) | Superseded. Alignment pilot scaffolding + smoke PASS. |

## 왜 pivot 했는가

- D1 BrainVLM 의 negative result (Pearson r 0.008-0.035, ROI ridge baseline 못 넘음, 3 backbone size plateau).
- Frozen BFM (Brain-JEPA, NeuroSTORM, SwiFT 6 변종) 도 ROI ridge 못 넘음 (`docs/reports/phase1_audit_20260604/`).
- 두 결과 종합 → single-modality 접근 의 한계 확정 → **multi-modal LLM fusion + modular brain encoder + 34D 독립 readout** 의 single project framing 으로 pivot (2026-06-29).

## Current framing pointer

- `docs/notes/implementation_spec_20260702.md` (code 구현 명세, canonical).
- `Paper/framework_EN.md`, `Paper/framework_KR.md` (spine narrative).
- `docs/notes/architecture_design_20260629.md` (architecture spec).
- `docs/notes/project_decisions.md` (2026-06-29 pivot entry).

## 이 폴더 를 쓰는 경우

Preserved evidence base 로만 참조.
- D1 v1/v2 의 negative result 를 새 framework 의 motivation evidence 로 인용 시 (`docs/reports/d1_brainvlm_va_negative_result_20260628.md` 가 이미 요약).
- Ablation reference (E4 image pretrain + fMRI fine-tune 의 hidden state) 로 활용 시 (implementation_spec §6-2 의 E4).
- 그 외 는 read-only.

**신규 학습 / 코드 는 이 폴더 에 추가 하지 않음.** `project/code/` 하위 에서 진행 (single unified pipeline).
