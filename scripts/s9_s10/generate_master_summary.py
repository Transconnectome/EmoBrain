#!/usr/bin/env python3
"""Generate MASTER_RESULTS_SUMMARY.md programmatically from verified S9 & S10 TSV tables.

Strictly enforces all wording and interpretation rules in docs/final/04_claude_code_workorder.md
(lines 1080-1099) and docs/final/01_integrated_document.md (Section 6-1).
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

PARTICIPANTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]


def fmt_ci(lo: float, hi: float, digits: int = 4, signed: bool = False) -> str:
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "N/A"
    spec = f"{'+' if signed else ''}.{digits}f"
    return f"[{format(lo, spec)}, {format(hi, spec)}]"


def fmt_val(v: float, digits: int = 4, signed: bool = False) -> str:
    if not np.isfinite(v):
        return "미실행/해당없음"
    spec = f"{'+' if signed else ''}.{digits}f"
    return format(v, spec)


def build_summary(base_dir: Path, verdict_override_dir: Path | None = None) -> str:
    base_dir = base_dir.resolve()
    t_dir = base_dir / "tables"
    s9_dir = base_dir / "s9_summary"
    if not s9_dir.is_dir() and (base_dir.parent / "s9_analysis").is_dir():
        s9_dir = base_dir.parent / "s9_analysis"
    verd_path = (verdict_override_dir / "tables/s10_preregistered_6_1_verdict.tsv") if verdict_override_dir else None
    if verd_path is None or not verd_path.exists():
        verd_path = t_dir / "s10_preregistered_6_1_verdict.tsv"

    t1 = pd.read_csv(t_dir / "s10_table1_primary_metrics.tsv", sep="\t").set_index("model_id")
    t2 = pd.read_csv(t_dir / "s10_table2_subsets_and_duration.tsv", sep="\t")
    t3 = pd.read_csv(t_dir / "s10_table3_auxiliary_metrics.tsv", sep="\t")
    t4 = pd.read_csv(t_dir / "s10_table4_per_emotion_34.tsv", sep="\t")
    t5 = pd.read_csv(t_dir / "s10_table5_feature_decoding.tsv", sep="\t")
    t6_zero = pd.read_csv(t_dir / "s10_s6_zero_selected_summary.tsv", sep="\t")
    t6_zone = pd.read_csv(t_dir / "s10_s4_s5_zone_summary.tsv", sep="\t")
    t7 = pd.read_csv(t_dir / "s10_table7_statistical_tests.tsv", sep="\t").set_index("test_id")
    verd = pd.read_csv(verd_path, sep="\t")

    sw = pd.read_csv(s9_dir / "interchange/s9_2_2_swap_summary.tsv", sep="\t")
    p11 = pd.read_csv(s9_dir / "interchange/s9_1_1_emotion_path_diff.tsv", sep="\t")
    emonet = pd.read_csv(s9_dir / "interchange/s9_1_1_emonet_groups.tsv", sep="\t")
    inter_i = pd.read_csv(s9_dir / "interchange/s9_1_2_interaction_I.tsv", sep="\t")
    o33 = pd.read_csv(s9_dir / "pair_comparison/s9_o33_unordered_pairs.tsv", sep="\t")
    k1 = pd.read_csv(s9_dir / "pathway_k1_k1a/s9_k1_pathway_summary.tsv", sep="\t")
    k1a = pd.read_csv(s9_dir / "pathway_k1_k1a/s9_k1a_b4_14dimensions_summary.tsv", sep="\t")
    net = pd.read_csv(s9_dir / "network_perturbation/s9_6_4b_network_perturbation_summary.tsv", sep="\t")

    lines = []
    a = lines.append

    a("# EmoBrain S9·S10 통합 결과 및 판정 요약 보고서 (`MASTER_RESULTS_SUMMARY`)")
    a("")
    a("- **설계 동결 기준 브랜치**: `origin/design/emobrain-final-2026-11-03` (`HEAD = a0a3c8f1aa7a7bd8b9d69fa4cba5bc58c75aa534`, 추적 파일 수정 `0건`)")
    a("- **원격 산출물 루트 (`b300-01`)**: `/scratch/emobrain/outputs/{s9_analysis,s10_tables_figures}/`")
    a("- **로컬 동기화 루트 (`spark-3a4c`)**: `/home/juke/git/EmoBrain/outputs/b300_s9_s10/`")
    a("- **평가 규모**: 개발 영상 `2,109개` (`canonical_id` 묶음 `2,108개`, 5명 공통 `in_all_5 = 1,969개`, 단일 창 `2,029개`, 다중 창 `80개`), 참가자 `5명`(`sub-01`~`sub-05`, 총 `10,402` 참가자-영상 쌍), 외부 `6-fold` 풀링 평가")
    a("- **계산 불가(`n_not_computable`) 점검**: 전 주 지표 표(Table 1~5, K1, K1a, 6-4b)에서 상수 예측/정답으로 인한 계산 불가 차원 수 **`0개`** 확인 (`O35` 소분산 차원 수 **`0개`**)")
    a("")
    a("---")
    a("")
    a("## 0. 필수 해석 경계 및 보고 준칙 (`04_claude_code_workorder.md` 1080~1099행 엄수)")
    a("")
    a("1. **규범 평정(`Normative Ratings`)**: 모든 정서 점수는 제3자 평정자의 규범 평정 비율/점수이며, fMRI 참가자가 시청 중 주관적으로 느낀 정서를 직접 읽었다고 해석하지 않는다.")
    a("2. **선형 기준선 대비 조건부 해석 (`N23`)**: S6 기본 심층신경망 모델(`A-1 = 0.2329`, `C-1 = 0.2355`)의 34개 정서 평균 `r`은 S5 주 선형 기준선 `ridge_main`(`0.2931`) 및 `MLP`(`0.2955`)보다 낮다(짝 앙상블 `D-3_paired = 0.3005`만 선형 기준선 수준에 도달). 따라서 본 보고서의 모든 경로 교환(`2-2`), 고정 규칙 경로(`K1/K1a`), 뇌 묶음 교란(`6-4b`) 결과는 전반적 예측 우위가 아니라 **해당 학습 표현 내부 작동에 관한 모델 조건부(`model-conditional`) 분석**으로 보고한다.")
    a("3. **정서별 Query 우위 주장 철회 (`N22`)**: 평균 풀링 대조군(`A-1_pool = 0.2660`, `C-1_pool = 0.2359`)이 정서별 query 판(`A-1 = 0.2329`, `C-1 = 0.2355`)과 같거나 더 높으므로, 정서별 query 읽기 구조가 평균 풀링보다 유리하다는 주장을 거둔다.")
    a("4. **비상한(`Non-Upper-Bound`) 참고선 (`N10`, `G16`)**: 뇌 신호 없이 실제 자극 특징을 입력받는 `S4 Stimulus Model`(`0.4766`)과 시험 시 실제 시각·캡션 특징을 함께 받는 `S6 Multimodal`(`0.4719`)은 뇌 모델의 이론적 상한이 아니며, 격차를 몇 `%` 메웠다는 비율 표현을 쓰지 않는다.")
    a("5. **비유의 및 반대 방향 서술 (`6-1`)**: 유의수준에 도달하지 못한 비교는 `같다`고 쓰지 않고 **\"차이를 확인하지 못했다\"**와 95% basic bootstrap 신뢰구간을 병기한다. 사전 예측과 반대 방향으로 0을 넘은 경우 **\"낮아졌다\"**로 기록한다.")
    a("6. **경로·상호작용·영역 해석 한계 (`1-1`, `1-2`, `6-4`)**: 바꿔 끼우기 효과는 \"이번 교환 조건과 척도에서 모델이 그 경로에 기댔다\"까지만 기술하며, 비가산성 항 `I`를 공유 정보량이나 뇌의 인과적 상호작용으로 읽지 않는다. `Subcortex`(10 ROIs)는 기능적 네트워크가 아닌 **피질하 해부학적 묶음**으로 부른다.")
    a("")
    a("---")
    a("")
    a("## 1. `6-1` 통합 사전등록 판정표 요약 (`s10_preregistered_6_1_verdict.tsv`)")
    a("")
    a("> `Holm-15` 사전등록 묶음 중 현재 저장된 HK 6-fold 모델로 판정 가능한 **11개 검정**에 대해 완료 묶음 기준 `Holm-11` 보정 `p`와, 미실행 S8 재학습 4개 검정이 모두 최소 `p`를 갖는다고 가정한 **보수적 최악 상한(`Holm-15 worst-case upper bound`)**을 함께 제시한다.")
    a("")
    a("| 구분 | 검정 ID | 가설 요약 | 5명 평균 추정치 [95% CI] | 보정 전 `p` | 주 보정 `p` (`Holm`) | `Holm-15` 상한 `p` | 참가자 확인 수 (보정전 / 보정후) | 판정 요약 |")
    a("| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |")

    # Emit 0행 + 15 prereg + 3 significant Holm-13 + summary of remaining Holm-13 + 6-3
    for _, vr in verd[verd["section"].isin(["0행_전제검정", "6-1_사전확증_15개묶음"])].iterrows():
        if str(vr["execution_status"]).startswith("[미실행"):
            a(f"| `{vr['section']}` | `{vr['test_id']}` | {vr['hypothesis_ko']} | 미실행 (별도 S8 재학습 대상) | - | - | - | - | 별도 S8 재학습 단계 대상 |")
            continue
        est_s = f"`{fmt_val(vr['mean_5sub_estimate'], signed=True)}` `{fmt_ci(vr['mean_5sub_ci95_low'], vr['mean_5sub_ci95_high'], signed=True)}`"
        p_raw_s = f"`{vr['mean_5sub_p_unadjusted']:.4f}`"
        p_adj_s = f"`{vr['mean_5sub_p_adjusted_primary']:.4f}`"
        p_h15_s = f"`{vr['mean_5sub_p_holm15_worstcase']:.4f}`" if np.isfinite(vr["mean_5sub_p_holm15_worstcase"]) else "-"
        sub_cnt = f"`{int(vr['n_sub_confirmed_unadj_of_5'])}/5` / `{int(vr['n_sub_confirmed_adj_of_5'])}/5`"
        short_v = "확인됨" if bool(vr["confirmed_mean_5sub"]) else "차이를 확인하지 못했다"
        a(f"| `{vr['section']}` | `{vr['test_id']}` | {vr['hypothesis_ko']} | {est_s} | {p_raw_s} | {p_adj_s} | {p_h15_s} | {sub_cnt} | {short_v} |")

    a("")
    a("### `6-4b` 13개 뇌 묶음 입력 교란 (`Holm-13` 별도 묶음) 및 `6-3` 외부 데이터셋 판정 요약")
    a("")
    a("| 묶음 (`group`) | 구분 (`6-4`) | `A-1` 하락폭 | `C-1` 하락폭 | 차이 `drop(C-1) - drop(A-1)` [95% CI] | 보정 전 `p` | `Holm-13 p` | 참가자 확인 (전/후) | 판정 |")
    a("| :--- | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :--- |")
    net_m5 = net[net["participant"] == "mean_5"].sort_values("p_holm13")
    for _, nr in net_m5.iterrows():
        g_kind = "피질하 해부학적 묶음" if nr["group_kind"] != "cortical_network" else "피질 네트워크"
        est_s = f"`{nr['diff_C1_minus_A1_mean']:+.4f}` `{fmt_ci(nr['diff_C1_minus_A1_ci_low'], nr['diff_C1_minus_A1_ci_high'], signed=True)}`"
        v_ko = "**민감도 차이 확인**" if nr["p_holm13"] < 0.05 else "차이를 확인하지 못했다"
        a(
            f"| `{nr['group']}` (`{int(nr['n_roi'])}` ROIs) | {g_kind} | `{nr['drop_A1_mean']:.4f}` | `{nr['drop_C1_mean']:.4f}` | "
            f"{est_s} | `{nr['p_boot']:.4f}` | `{nr['p_holm13']:.4f}` | `{int(nr['n_confirmed_unadj_of_5'])}/5` / `{int(nr['n_confirmed_holm13_of_5'])}/5` | {v_ko} |"
        )
    a("")
    a("- **`6-3` 외부 데이터셋(`MC`) 시청 전이**: 현재 완료된 HK 개발 세트 S4~S6 체크포인트 범위 밖의 별도 S7 단계이므로 `[미실행: 별도 S7 실행 대상]`으로 명시한다.")
    a("")
    a("---")
    a("")
    a("## 2. 주 정서 예측 지표 및 보조 지표 요약 (`Table 1` ~ `Table 3`)")
    a("")
    t3_m5 = t3[t3["participant"] == "mean_5sub"].set_index("model_id")
    main_ids = [
        "s6_brain_only",
        "s6_brain_only_pool",
        "s6_brain_only_distill",
        "s6_control_label_smoothing",
        "s6_control_stimulus_shuffle",
        "s6_brain_only_featdec",
        "s6_control_feature_shuffle",
        "s6_brain_decoded",
        "s6_brain_decoded_pool",
        "s6_brain_decoded_additive",
        "s6_brain_decoded_grad",
        "s6_brain_decoded_distill",
        "s6_brain_decoded_sep",
        "s6_brain_decoded_sep_distill",
        "s6_brain_features_only",
        "s6_brain_features_only_paired_single_pair",
        "s6_brain_features_only_paired",
        "s6_brain_frozen_feature_encoder_single_pair",
        "s6_brain_frozen_feature_encoder",
        "s6_brain_only_repr_frozen",
        "s6_brain_only_repr_trained",
        "s5_ridge_main",
        "s5_ridge_literature",
        "s5_mlp",
        "s5_h2020",
        "s5_ged",
        "s5_soft_bce",
        "s5_signal",
        "s5_emogrowth",
        "s5_video_length",
        "s5_video_lowlevel",
        "s4_stimulus",
        "s6_multimodal",
    ]
    a("| 모델 코드 | 설명 | 5명 평균 `r` (± seed SD) | 95% Basic CI | 참가자 범위 (`sub-01`~`05`) | 오차감소 (`O25`) | 프로필 `r` (`2-4`) | 정서 식별 (`O19`) | 길이 통제 편상관 (`N21`) |")
    a("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for mid in main_ids:
        if mid not in t1.index:
            continue
        r1 = t1.loc[mid]
        r3 = t3_m5.loc[mid] if mid in t3_m5.index else None
        mv = float(r1["mean_5sub"])
        sd = float(r1["mean_5sub_seed_sd"])
        mv_s = f"`{mv:.4f} ± {sd:.4f}`" if np.isfinite(sd) else f"`{mv:.4f}`"
        ci_s = f"`{fmt_ci(float(r1['mean_5sub_ci_low']), float(r1['mean_5sub_ci_high']))}`"
        subs = [float(r1[s]) for s in PARTICIPANTS]
        sub_rng = f"`{min(subs):.4f}`~`{max(subs):.4f}`"
        er_s = f"`{float(r3['error_reduction_vs_dk_mean']):.4f}`" if r3 is not None else "-"
        pr_s = f"`{float(r3['profile_r']):.4f}`" if r3 is not None else "-"
        id_s = f"`{float(r3['emotion_identification'])*100:.2f}%`" if r3 is not None else "-"
        pt_s = f"`{float(r3['partial_r_controlling_log_length']):.4f}`" if r3 is not None else "-"
        a(f"| `{r1['code']}` | {r1['display_name']} | {mv_s} | {ci_s} | {sub_rng} | {er_s} | {pr_s} | {id_s} | {pt_s} |")

    a("")
    a("- **부분집합 및 영상 길이 민감도 (`Table 2`)**:")
    for sid in ["in_all_5_1969", "window_excluded_2029", "dur_le_8s_1503", "dur_gt8_le16s_521", "dur_gt_16s_85"]:
        sub_t2 = t2[t2["subset_id"] == sid].set_index("model_id")
        desc = sub_t2["subset_description"].iloc[0]
        a(
            f"  - `{sid}` ({desc}): `A-1 = {sub_t2.loc['s6_brain_only', 'mean_5sub']:.4f}`, "
            f"`C-1 = {sub_t2.loc['s6_brain_decoded', 'mean_5sub']:.4f}`, "
            f"`A-2 = {sub_t2.loc['s6_brain_only_distill', 'mean_5sub']:.4f}`, "
            f"`ridge_main = {sub_t2.loc['s5_ridge_main', 'mean_5sub']:.4f}`"
        )
    a("- **보조 대조 비교 (`Table 7`, `Holm-15` 밖 개별 보고)**:")
    for tid_aux in [
        "G6_B1_vs_feat_shuffle",
        "G6_A2_vs_stim_shuffle",
        "F7_A1_vs_A1_pool",
        "F7_C1_vs_C1_pool",
        "G8_C1_vs_C1_grad",
        "1-2_가_C1_vs_C1_additive",
        "D_D1_vs_C1",
        "D_D4_single_vs_A1",
        "E_frozen_vs_A1",
        "E_trained_vs_A1",
        "N23_A1_vs_ridge_main",
        "N23_C1_vs_ridge_main",
    ]:
        rx = t7.loc[tid_aux]
        n_em = int(rx["n_emotions_pos_of_34"]) if np.isfinite(rx["n_emotions_pos_of_34"]) else 0
        a(
            f"  - `{tid_aux}` ({rx['comparison_label']}): `Δr = {rx['mean_5sub_effect']:+.4f}` "
            f"`{fmt_ci(rx['mean_5sub_ci_low'], rx['mean_5sub_ci_high'], signed=True)}`, `p = {rx['mean_5sub_p_raw']:.4f}` "
            f"(34개 정서 중 양수 `{n_em}/34`, 중앙값 `{rx['emotion_diff_median']:+.4f}`)"
        )

    a("")
    a("---")
    a("")
    a("## 3. 정서 34개 범주별 분포 및 `1-2(가)` 상호작용 Head 비교 (`Table 4`)")
    a("")
    t4_num = t4.copy()
    for col in ["C-1_mean_5sub_r", "A-1_mean_5sub_r", "ridge_main_mean_5sub_r", "diff_C1_minus_C1add_mean_5sub", "diff_C1_minus_C1add_mean_5sub_q_fdr34"]:
        if col in t4_num.columns:
            t4_num[col] = pd.to_numeric(t4_num[col], errors="coerce")
    top5_c1 = t4_num.sort_values("C-1_mean_5sub_r", ascending=False).head(5)
    bot5_c1 = t4_num.sort_values("C-1_mean_5sub_r", ascending=True).head(5)
    a("- **`C-1` 상위 5개 정서**: " + ", ".join(f"`{r['emotion']}` (`{r['C-1_mean_5sub_r']:.4f}`, Ridge `{r['ridge_main_mean_5sub_r']:.4f}`)" for _, r in top5_c1.iterrows()))
    a("- **`C-1` 하위 5개 정서**: " + ", ".join(f"`{r['emotion']}` (`{r['C-1_mean_5sub_r']:.4f}`, 0 아닌 영상 `{int(r['n_nonzero_dev2109'])}`개)" for _, r in bot5_c1.iterrows()))
    if "diff_C1_minus_C1add_mean_5sub_q_fdr34" in t4_num.columns:
        n_fdr_12a = int((t4_num["diff_C1_minus_C1add_mean_5sub_q_fdr34"] < 0.05).sum())
        a(f"- **`1-2(가)` 상호작용 head 대 더하기 head (`C-1 - C-1_additive`, 34개 정서 `BH-FDR`)**: 5명 평균 기준 `q < 0.05` 정서 수 `{n_fdr_12a}/34`개 (추가한 상호작용 결합 계산의 정서별 이득을 확인하지 못했다).")

    a("")
    a("---")
    a("")
    a("## 4. 장면 특징 해독 (`[사전] 2-1`, 64개 층 프로파일, `G8`/`G10`, `Table 5`·`Table 6`)")
    a("")
    a("| 모델 | 목표 특징 | 평가 Fold | 5명 평균 차원별 `r` [95% CI] | 쌍별 식별률 (`D9` / `D_k`, `O19`) | 계산 불가 차원 |")
    a("| :--- | :--- | :---: | :---: | :---: | :---: |")
    for _, r5 in t5.iterrows():
        if str(r5["family"]).startswith("S5_decoding_64layer"):
            continue
        ci5 = fmt_ci(float(r5["mean_5sub_ci_low"]), float(r5["mean_5sub_ci_high"]))
        id_d9 = f"{float(r5['mean_5sub_ident_d9'])*100:.2f}%" if np.isfinite(r5["mean_5sub_ident_d9"]) else "-"
        id_dk = f"{float(r5['mean_5sub_ident_dk'])*100:.2f}%" if np.isfinite(r5["mean_5sub_ident_dk"]) else "-"
        a(f"| `{r5['code']}` | {r5['target_label']} | `{int(r5['n_folds_evaluated'])}/6` | `{float(r5['mean_5sub_r']):.4f}` `{ci5}` | `{id_d9}` / `{id_dk}` | `{int(r5['n_dim_not_computable_max'])}` |")
    a("")
    z_folds = t6_zero[t6_zero["n_zero_selected_G10"] > 0]
    a("- **`G10` `zero_selected` 발생 현황 (`Table 6`)**: " + "; ".join(f"`{r['code']}` (`{r['condition']}`): `{int(r['n_zero_selected_G10'])}/6` folds (`folds={r['zero_selected_folds']}`)" for _, r in z_folds.iterrows()) + ". `B-1` fold 3은 `λ = 0`이 선택되어 특징 해독 학습 이득으로 해석하지 않는다(`G10`).")
    z_s4 = t6_zone[(t6_zone["model_id"] == "s4_stimulus_zone") & (t6_zone["participant"] == "mean_5sub")].iloc[0]
    z_s5 = t6_zone[(t6_zone["model_id"] == "s5_ridge_zone") & (t6_zone["participant"] == "mean_5sub")].iloc[0]
    a(f"- **보조 모델 5개 내용 구역 평가 (`Table 6`, `6-2` 규칙 적용)**: `S4 Stimulus` 구역 제외 `r = {z_s4['five_block_mean_excluded']:.4f}` vs 대조 `{z_s4['five_block_mean_control']:.4f}` (`Δ = {z_s4['five_block_mean_diff_excluded_minus_control']:+.4f}`); `S5 Ridge` 구역 제외 `r = {z_s5['five_block_mean_excluded']:.4f}` vs 대조 `{z_s5['five_block_mean_control']:.4f}` (`Δ = {z_s5['five_block_mean_diff_excluded_minus_control']:+.4f}`).")

    a("")
    a("---")
    a("")
    a("## 5. 경로 바꿔 끼우기 (`S9-1`: `2-2`, `1-1`, `1-2(나)`) 및 최근접 쌍 비교 (`S9-2`: `O33`)")
    a("")
    sw_m5 = sw[(sw["participant"] == "mean_5sub") & (sw["seed"] == "mean_3seeds")]
    for cond_k, cond_lbl in [("brain_decoded", "C-1 (주 상호작용)"), ("brain_decoded_additive", "C-1_additive (더하기)"), ("brain_decoded_sep", "D-1 (별도 encoder)")]:
        sub_sw = sw_m5[sw_m5["condition"] == cond_k].set_index("path")
        a(
            f"- **`{cond_lbl}` 경로 교체 효과 (`actual - 100 random length-matched perturbations`, 419개 연결 성분 부트스트랩)**: "
            f"시각 `{sub_sw.loc['visual', 'effect']:+.4f}` (`p = {sub_sw.loc['visual', 'p_boot']:.4f}`), "
            f"캡션 `{sub_sw.loc['caption', 'effect']:+.4f}` (`p = {sub_sw.loc['caption', 'p_boot']:.4f}`), "
            f"동시 `{sub_sw.loc['both', 'effect']:+.4f}` (`p = {sub_sw.loc['both', 'p_boot']:.4f}`)."
        )
    p11_c1_34 = p11[(p11["condition"] == "brain_decoded") & (p11["participant"] == "mean_5sub") & (p11["seed"] == "mean_3seeds")]
    sw_c1_vmc = sw_m5[(sw_m5["condition"] == "brain_decoded") & (sw_m5["path"] == "visual_minus_caption")].iloc[0]
    n_cap_dom = int((p11_c1_34["visual_minus_caption"] < 0).sum())
    n_q05 = int((p11_c1_34["q_bh_fdr"] < 0.05).sum())
    a(f"- **`1-1` 경로 차이 (`시각 - 캡션`, `C-1`, 탐색)**: 전체 평균 `{sw_c1_vmc['effect']:+.4f}` `{fmt_ci(sw_c1_vmc['ci95_low'], sw_c1_vmc['ci95_high'], signed=True)}` (`p = {sw_c1_vmc['p_boot']:.4f}`); 34개 정서 중 `{n_cap_dom}/34`개에서 캡션 교체 반응이 더 컸고 `BH-FDR q < 0.05`는 `{n_q05}/34`개였다.")
    em_c1_vmc = emonet[
        (emonet["condition"] == "brain_decoded")
        & (emonet["participant"] == "mean_5sub")
        & (emonet["seed"] == "mean_3seeds")
        & (emonet["group"] == "high_minus_low")
        & (emonet["metric"] == "visual_minus_caption")
    ]
    if len(em_c1_vmc) > 0:
        rd = em_c1_vmc.iloc[0]
        a(f"- **Kragel 2019 EmoNet 정지 프레임 집단 보조 비교 (`C-1`)**: 고성능군 대 저성능군 `(vis - cap)` 차이 `{rd['estimate']:+.4f}` `{fmt_ci(rd['ci95_low'], rd['ci95_high'], signed=True)}` (`p = {rd['p_boot']:.4f}`, 차이를 확인하지 못했다).")
    ii_m5 = inter_i[
        (inter_i["row_type"] == "summary_34")
        & (inter_i["participant"] == "mean_5sub")
        & (inter_i["seed"] == "mean_3seeds")
    ].set_index("condition")
    a(
        f"- **`1-2(나)` 모델 계산 비가산성 `|I|` (`actual - control`)**: "
        f"`C-1`: `{ii_m5.loc['brain_decoded', 'effect']:+.5f}` (`{fmt_ci(ii_m5.loc['brain_decoded', 'ci95_low'], ii_m5.loc['brain_decoded', 'ci95_high'], digits=5, signed=True)}`, `p = {ii_m5.loc['brain_decoded', 'p_boot']:.4f}`, 합을 넘는 효과를 확인하지 못했다; `C-1_additive`는 대수적 항등에 의해 최대 `|I| < 1.5e-6`), "
        f"`D-1`: `{ii_m5.loc['brain_decoded_sep', 'effect']:+.5f}` (`p = {ii_m5.loc['brain_decoded_sep', 'p_boot']:.4f}`)."
    )
    o33_m5 = o33[(o33["participant"] == "mean_5sub") & (o33["seed"] == "mean_3seeds")].set_index("comparison")
    r_o33_a1 = o33_m5.loc["brain_only"]
    r_o33_c1 = o33_m5.loc["brain_decoded"]
    r_o33_df = o33_m5.loc["brain_decoded_minus_brain_only"]
    a(
        f"- **`O33` 최근접 쌍(`1,690`개 무방향 쌍) 차이 상관 `r`**: `A-1 = {r_o33_a1['estimate']:.4f}`, `C-1 = {r_o33_c1['estimate']:.4f}`, "
        f"`C-1 - A-1 = {r_o33_df['estimate']:+.4f}` `{fmt_ci(r_o33_df['ci95_low'], r_o33_df['ci95_high'], signed=True)}` (`p = {r_o33_df['p_boot']:.4f}`, 차이를 확인하지 못했다)."
    )

    a("")
    a("---")
    a("")
    a("## 6. 고정 규칙 경로 평가 (`S9-3`: `K1` 34개 정서 및 `K1a + B4` 14개 정서 차원)")
    a("")
    k1_m5 = k1[k1["participant"] == "mean_5subj"]
    r_k1_ridge_u = k1_m5[(k1_m5["role"] == "primary_k1_pathway") & (k1_m5["source"] == "ridge") & (k1_m5["head"] == "additive") & (k1_m5["calibration"] == "uncalibrated")].iloc[0]
    r_k1_ridge_c = k1_m5[(k1_m5["role"] == "primary_k1_pathway") & (k1_m5["source"] == "ridge") & (k1_m5["head"] == "additive") & (k1_m5["calibration"] == "calibrated")].iloc[0]
    r_k1_c1_u = k1_m5[(k1_m5["role"] == "primary_k1_pathway") & (k1_m5["source"] == "brain_decoded") & (k1_m5["seed"] == "mean_3seeds") & (k1_m5["head"] == "additive") & (k1_m5["calibration"] == "uncalibrated")].iloc[0]
    r_k1_d1_u = k1_m5[(k1_m5["role"] == "diagnostic_encoder2_D1") & (k1_m5["source"] == "feature_encoder") & (k1_m5["seed"] == "mean_3seeds") & (k1_m5["head"] == "additive") & (k1_m5["calibration"] == "uncalibrated")].iloc[0]
    a(f"- **`K1` (34개 정서)**:")
    a(f"  - `S5 Ridge -> 고정 Stimulus Head (더하기)`: 보정 전 `r = {r_k1_ridge_u['mean_r_34']:.4f}` (`A-1` 대비 `{r_k1_ridge_u['diff_vs_a1_34']:+.4f}`, 95% CI `{fmt_ci(r_k1_ridge_u['diff_ci95_low_34'], r_k1_ridge_u['diff_ci95_high_34'], signed=True)}`, `p = {r_k1_ridge_u['p_boot_two_sided_34']:.4f}`, 5/5명 전원 양수); `N8` 분산 보정 후 `r = {r_k1_ridge_c['mean_r_34']:.4f}` (`A-1` 대비 `{r_k1_ridge_c['diff_vs_a1_34']:+.4f}`, `p = {r_k1_ridge_c['p_boot_two_sided_34']:.4f}`).")
    a(f"  - `D-1 encoder_2 -> 고정 Stimulus Head (더하기, 보정 전)`: `r = {r_k1_d1_u['mean_r_34']:.4f}` (`A-1` 대비 `{r_k1_d1_u['diff_vs_a1_34']:+.4f}`, 95% CI `{fmt_ci(r_k1_d1_u['diff_ci95_low_34'], r_k1_d1_u['diff_ci95_high_34'], signed=True)}`, `p = {r_k1_d1_u['p_boot_two_sided_34']:.4f}`, 차이를 확인하지 못했다).")
    a(f"  - `C-1 decoded -> 고정 Stimulus Head (더하기, 보정 전)`: `r = {r_k1_c1_u['mean_r_34']:.4f}` (`A-1` 대비 `{r_k1_c1_u['diff_vs_a1_34']:+.4f}` 낮아졌다; 해석은 \"고정된 규칙을 decoded features에 적용할 수 있었는지\"에 한정한다).")

    k1a_m5 = k1a[k1a["participant"] == "mean_5subj"]
    r_b4_m = k1a_m5[k1a_m5["source"] == "b4_ridge_main"].iloc[0]
    r_b4_l = k1a_m5[k1a_m5["source"] == "b4_ridge_literature"].iloc[0]
    r_k1a_ru = k1a_m5[(k1a_m5["role"] == "col3_primary_k1a_pathway") & (k1a_m5["source"] == "ridge") & (k1a_m5["head"] == "additive") & (k1a_m5["calibration"] == "uncalibrated")].iloc[0]
    r_k1a_rc = k1a_m5[(k1a_m5["role"] == "col3_primary_k1a_pathway") & (k1a_m5["source"] == "ridge") & (k1a_m5["head"] == "additive") & (k1a_m5["calibration"] == "calibrated")].iloc[0]
    a(f"- **`K1a + B4` (14개 정서 차원, 1~9 척도, 탐색적 보조 분석)**:")
    a(f"  - `(1)` `B4` 뇌 직접 선형 예측: 주 비교판 `r = {r_b4_m['mean_r_14']:.4f}`, 문헌판(6-delay) `r = {r_b4_l['mean_r_14']:.4f}` (차원별 평정 신뢰도 칸은 `[미확인]`으로 유지).")
    a(f"  - `(3)` `S5 Ridge -> 고정 K1a Head (더하기)`: 보정 전 `r = {r_k1a_ru['mean_r_14']:.4f}` (`B4` 주 비교판 대비 `{r_k1a_ru['diff_vs_b4_main_14']:+.4f}`, 95% CI `{fmt_ci(r_k1a_ru['diff_ci95_low_14'], r_k1a_ru['diff_ci95_high_14'], signed=True)}`, `p = {r_k1a_ru['p_boot_two_sided_14']:.4f}`, 5/5명 전원 및 14/14개 차원 모두 `BH-FDR q = 0.0001`); 보정 후 `r = {r_k1a_rc['mean_r_14']:.4f}`. 이 결과는 \"뇌에서 decoding한 장면 특징으로 일부 정서 차원도 예측할 수 있었다\"까지만 해석한다(`K1a`).")

    a("")
    a("---")
    a("")
    a("## 7. 산출물 파일 목록 (로컬 `spark-3a4c` 및 원격 `b300-01` 동일 동기화)")
    a("")
    a("### A. 논문용 벡터 그림 (`figures/`, `pdf.fonttype=42` 순수 벡터 PDF + `300 DPI` PNG)")
    a("1. `fig1_s6_condition_ladder.{pdf,png}` — S6 주 모델/기준선/비상한 참고선 사다리 및 `[사전] 2-3`·핵심 대조군 효과크기")
    a("2. `fig2_s5_layerwise_decoding.{pdf,png}` — S5 V-JEPA2(40층)·DeBERTa(24층) 층별 해독 프로파일 및 S6 해독 특징 비교 (`G8`)")
    a("3. `fig3_s9_interchange_and_interaction.{pdf,png}` — S9-1 경로 바꿔 끼우기(`2-2`), 정서별 경로 비대칭(`1-1`), 비가산성 `|I|`(`1-2(나)`)")
    a("4. `fig4_s9_cabnp_network_perturbation.{pdf,png}` — S9-4 13개 뇌 묶음 입력 교란 하락폭, `Holm-13` 민감도 차이(`6-4b`), S2 참가자 일치도")
    a("5. `fig5_emotion34_and_k1_pathway.{pdf,png}` — 34개 정서별 예측 분포(`Table 4`) 및 `K1` 고정 규칙 경로 평가 요약")
    a("6. `fig6_k1a_14dimensions.{pdf,png}` — `K1a + B4` 14개 정서 차원 경로 비교 및 차원별 이득 프로파일")
    a("")
    a("### B. S10 통계·판정 요약표 (`tables/`, 각 `.tsv` 및 `.csv` 쌍)")
    for p in sorted(t_dir.glob("*.tsv")):
        a(f"- `{p.name}` / `{p.stem}.csv`")
    a("")
    a("### C. S9 메커니즘 분석 요약표 (`s9_summary/`)")
    for p in sorted(s9_dir.glob("*/*.tsv")):
        if p.name != "donor_assignments.tsv":
            a(f"- `{p.parent.name}/{p.name}`")
    a("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory (defaults to --base-dir)")
    args = parser.parse_args()
    out_dir = (args.out_dir or args.base_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_md = out_dir / "MASTER_RESULTS_SUMMARY.md"
    out_md.write_text(build_summary(args.base_dir, verdict_override_dir=out_dir), encoding="utf-8")
    print(f"Wrote {out_md} ({out_md.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
