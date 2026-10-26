#!/usr/bin/env python3
"""EmoBrain 1단계 핵심 1·2: task 계약, target 사전, 0단계 인계·준비 상태 표 (2026-10-24). 표만 읽어 쓴다.
출력: stage1/01_task/{task_contract.yaml, target_dictionary.tsv, baseline_compatibility.tsv}
      stage1/00_status/{input_manifest.tsv, zero_handoff.tsv, readiness.tsv, decision_log.md}
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

S1 = Path("/storage/bigdata/EmoBrain_response/stage1")
LAB = Path("/scratch/connectome/seokjin14/EmoBrain/project/shared/data")
META = Path("/storage/bigdata/Horikawa/metadata/horikawa_meta_data_with_dimension_binary.csv")
SPLIT = Path("/storage/bigdata/EmoBrain_response/splits/horikawa_rungroup6_v1.tsv")
DIMS14 = ["valence", "arousal", "dominance", "approach", "attention", "certainty", "commitment", "control",
          "effort", "fairness", "identity", "obstruction", "safety", "upswing"]


def main():
    (S1 / "01_task").mkdir(parents=True, exist_ok=True); (S1 / "00_status").mkdir(parents=True, exist_ok=True)
    names = [l.strip() for l in open(LAB / "cowen34_order.txt") if l.strip()]
    split = pd.read_csv(SPLIT, sep="\t"); vids = split[split.analysis_row].video_id.values
    D = pd.read_csv(META); D.index = D.stimulus_num.str.replace("stimulus_", "").astype(int)
    C = pd.read_csv(LAB / "cowen_horikawa_labels.csv"); C.index = C.stim_num_int

    # target 사전
    rows = []
    for i, n in enumerate(names):
        y = D.loc[vids, f"score_{i}"].values
        rows.append(dict(target_space="A34", index=i, source_column=f"score_{i}", name=n,
                         raw_scale="그 범주를 고른 평정자 비율 [0,1] (분모 = 영상별 평정자 수, 7~32명 추정)",
                         n_observed=int(np.isfinite(y).sum()), mean=y.mean(), sd=y.std(), n_zero=int((y == 0).sum()),
                         n_ge_0p5=int((y >= 0.5).sum()), missing=int((~np.isfinite(y)).sum())))
    for i, d in enumerate(DIMS14):
        y = C.reindex(vids)[f"{d}_score"].values
        rows.append(dict(target_space="A14", index=i, source_column=f"{d}_score", name=d,
                         raw_scale="1~9 척도 평정의 영상별 평균", n_observed=int(np.isfinite(y).sum()),
                         mean=np.nanmean(y), sd=np.nanstd(y), n_zero=np.nan, n_ge_0p5=np.nan, missing=int((~np.isfinite(y)).sum())))
    TD = pd.DataFrame(rows); TD.to_csv(S1 / "01_task/target_dictionary.tsv", sep="\t", index=False, float_format="%.4f")
    miss14 = sorted(int(v) for v in vids[~np.isfinite(C.reindex(vids)["valence_score"].values)])

    common = dict(
        unit="피험자 1명이 영상 1개를 본 블록 반응 1개 (Horikawa v3_qc, QC 통과 블록, 같은 내용 중복의 나중 제시 15개 제외)",
        participant_scope="Horikawa 2020 (주 데이터) sub-01~05. 피험자마다 따로 학습·평가. MindCaptioning 은 재현용으로 이번 범위에서 쓰지 않음",
        generalization_target="같은 피험자가 처음 보는 영상 (참가자 내 새 영상). 다른 사람·다른 내용 집단 일반화는 별도 후속 평가",
        preprocessing_version="Horikawa v3_qc (common36 블록 반응, run 안 z, fieldmap 없는 보정 SyN-SDC, QC D22)",
        stimulus_manifest=str(SPLIT), split_id="horikawa_rungroup6_v1",
        split_rule="run_index 단위 6겹, 같은 내용 쌍이 든 run 은 묶음, 5명 공통. 안쪽 = 바깥 학습 fold 5개",
        sharing_structure="출력(차원)마다 가중치와 손실이 분리된 독립 선형 모델. 감정 간 공유 표현 없음 (공유 학습 비교는 후속 F-3)",
        primary_metric="차원별 영상 간 Pearson r (피험자별, 6개 fold 의 평가 예측을 모아 계산. fold 별 r 평균도 함께 보존)",
        metric_axis="참가자와 차원을 고정하고 평가 영상 방향",
        secondary_metrics=["train 평균 대비 오차 감소율 1 - SSE/SSE(train 평균)", "원척도 MSE",
                           "영상별 프로필 상관 (차원 방향, train 평균 프로필 기준선과 함께)"],
        baseline=["train_mean", "duration (학습 분위 구간 원-핫)", "lowlevel_L (저수준 시각 33개)",
                  "brain_global (블록 voxel 전체 평균·표준편차)"],
        baseline_rule="기준선은 대안 설명을 따로 보는 비교이며 모두 이겨야 하는 통과 조건이 아님",
        input_condition_main="brain_roi469: 기본 지도 469개 영역 평균 (run 안 z 의 영역 평균, 유효 영역만). voxel 패턴 입력은 후속",
        dimension_exclusion="낮은 점수·드문 감정이라는 이유로 차원을 빼지 않음. 상수이면 NA 와 이유 기록",
        supported_claim="선택한 뇌 입력과 선형 readout 으로 외부 평정자 집단의 영상별 평정 차이를 예측하는 정도. fMRI 참가자 개인의 감정이나 정서 생성 원리가 아님",
    )
    contract = {"tasks": [
        dict(task_id="hk_A34_brain_baseline_v1",
             scientific_question="현재 전처리된 Horikawa 뇌 입력만으로 처음 보는 영상의 34개 범주 평정 차이를 얼마나 예측하는가?",
             target_source=str(META) + " (score_0~33, 이름 = cowen34_order.txt 알파벳 순)",
             target_version="horikawa_meta_data_with_dimension_binary.csv, 2026-01-19", dimension_names=names,
             raw_scale="[0,1] 범주 응답 비율. 한 영상에 여러 범주 공존 (합 1~4.3). 합을 1로 강제하지 않음",
             missing_policy="결측 없음 (2,181개 모두 관측)", train_transform="없음 (원 비율 그대로)",
             model_family="L2 정규화 선형 sigmoid 출력 (감정마다 독립)", training_loss="soft BCE: -y log p - (1-y) log(1-p)",
             selection_metric="안쪽 검증 soft BCE (차원마다 λ 선택, λ = 10 ~ 1e-3 의 9개)", **common),
        dict(task_id="hk_A14_brain_baseline_v1",
             scientific_question="같은 뇌 입력으로 14개 정서 척도의 영상 간 차이를 얼마나 예측하는가?",
             target_source=str(LAB / "cowen_horikawa_labels.csv") + " (*_score)",
             target_version="cowen_horikawa_labels.csv (2,185행)", dimension_names=DIMS14,
             raw_scale="1~9 척도 평정의 영상별 평균",
             missing_policy=f"관측된 영상만 사용 (분석 영상 중 결측 {len(miss14)}개: {miss14}). 같은 내용 영상 값으로 채우지 않음",
             train_transform="차원별 train 평균·표준편차로 표준화 후 학습, 예측은 원척도로 되돌려 저장",
             model_family="ridge (척도마다 독립)", training_loss="제곱오차 + α||w||²",
             selection_metric="안쪽 검증 MSE (차원마다 α 선택, α = 0.1 ~ 1e6 의 15개)", **common)]}
    (S1 / "01_task/task_contract.yaml").write_text(yaml.safe_dump(contract, allow_unicode=True, sort_keys=False, width=200))

    pd.DataFrame([
        dict(existing="EmoBrain project/data·scripts/train_label_query.py 계열", target="34-D log1p-z + MSE",
             preprocessing="옛 전처리 (v3_qc 이전)", compatible=False, reason="target 변환·loss·전처리·분할이 계약과 다름 (구현 상태 문서 08)"),
        dict(existing="prelim 0단계 label_lowlevel_r2 / duration_r2", target="A34·A14 (교차검증 R²)",
             preprocessing="해당 없음 (영상 단위)", compatible=False, reason="영상 무작위 5겹·선형 회귀 R². 이번 split·모델과 다르므로 원예측을 새로 만듦"),
        dict(existing="hk_v2_v3_compare (10/13)", target="내용 특징 → 뇌 (encoding)", preprocessing="v2·v3 (QC 전)",
             compatible=False, reason="방향이 반대(내용→뇌)이고 정서 target 이 아님. 참고용"),
    ]).to_csv(S1 / "01_task/baseline_compatibility.tsv", sep="\t", index=False)

    # 0단계 인계
    Z = [("0-D/0-3", "라벨 분포·자료량", "verified", "ready", "label_distribution_*.tsv. 0.5 는 기술용 임계값, 제외 기준 아님"),
         ("0-1", "34개 범주 중복·차원", "verified", "ready", "Pearson 상관행렬 고유값(항목 표준화와 같음), 유효 차원=(Σλ)²/Σλ²"),
         ("0-2", "34↔14 양방향 R²", "verified", "ready", "약한 ridge(1e-3·n) 선형, 영상 무작위 5겹, 합친 예측의 R². 뇌 r 와 직접 비교 금지"),
         ("0-4", "평정자 수 역산·라벨 신뢰도", "verified", "conditional", "분모는 비율을 정수로 만드는 최소 n 이라 유일하지 않을 수 있음. 상한으로 정규화하지 않음"),
         ("0-5", "제시 조건·움직임과 라벨", "verified", "conditional", "라벨 부분은 2026-10-24 A14 관측값만으로 재계산(결과 변화 없음). 뇌 신호 크기×라벨 표(block_signal_vs_labels)는 결측 7개를 같은 내용 값으로 채운 판"),
         ("0-6", "저수준 시각 특징 → 라벨", "verified", "ready", "33개 정의는 lowlevel_features.py. 이번 기준선에서 같은 split 으로 다시 예측"),
         ("0-7", "블록·run 품질", "verified", "ready", "MAD×1.4826 기준 강건 z>5 또는 |z|>15. 표시만 했고 제외 안 함"),
         ("0-8", "참가자 간 일치도·반복 안정성", "verified", "conditional", "MindCaptioning 반복은 홀수 3회·짝수 2회에 동등 절반 Spearman-Brown 적용(근사). 라벨 미사용"),
         ("0-9", "영상 길이 → 라벨, 뇌 신호 크기", "verified", "ready", "길이 구간 경계·평균은 학습 fold 에서만 계산(누수 없음). 이번 기준선에서 같은 split 으로 다시 예측")]
    pd.DataFrame(Z, columns=["item", "내용", "근거_수준", "실행_상태", "비고"]).to_csv(S1 / "00_status/zero_handoff.tsv", sep="\t", index=False)
    pd.DataFrame([
        dict(input="뇌 B (영역 평균)", path="/storage/bigdata/EmoBrain_response/prelim/roi_blocks/Horikawa_sub-XX_roi469_*",
             version="v3_qc runz → 469 영역 평균 (2026-10-22)", status="ready", note="voxel 패턴과 다른 입력. 유효 영역 467~469개"),
         dict(input="뇌 B (voxel)", path="/storage/bigdata/Horikawa/response_t1w/sub-XX/v3_qc/", version="v3_qc", status="ready", note="이번 기준선은 영역 평균부터"),
         dict(input="A34", path=str(META), version="2026-01-19", status="ready", note="[0,1] 비율 확인"),
         dict(input="A14", path=str(LAB / "cowen_horikawa_labels.csv"), version="2,185행", status="ready", note=f"분석 영상 결측 {len(miss14)}개"),
         dict(input="분할", path=str(SPLIT), version="horikawa_rungroup6_v1", status="ready", note="기존 무작위 split 은 삭제"),
         dict(input="영상 길이", path="response_t1w/sub-XX/v3/sub-XX_samples.tsv duration_sec", version="", status="ready", note="72%가 10초"),
         dict(input="저수준 시각 L", path="/storage/bigdata/EmoBrain_response/prelim/lowlevel_video_features.tsv", version="33개 (2026-10-22)", status="ready", note=""),
         dict(input="뇌 전역 요약", path="/storage/bigdata/EmoBrain_response/prelim/block_stats_Horikawa_sub-XX.tsv", version="voxel 원자료에서 계산", status="ready", note="영역 평균의 평균 아님"),
         dict(input="영상 표현 V", path="없음 (Perlmutter EmoViS 결과 미확인)", version="", status="blocked", note="핵심 4·5 보류"),
         dict(input="caption 원문", path=str(LAB / "caption_ck20.csv"), version="영상당 약 20개", status="conditional", note="생성 출처·평정 접근 여부 미확인"),
         dict(input="caption 표현 S", path="없음 (Perlmutter 미확인)", version="", status="blocked", note="핵심 4·5 보류"),
    ]).to_csv(S1 / "00_status/input_manifest.tsv", sep="\t", index=False)
    pd.DataFrame([
        dict(analysis="핵심 3 뇌 단독 기준선 (A34·A14, 기준선 넷)", status="ready", reason="입력·분할·계약 모두 준비"),
        dict(analysis="핵심 4 V/S/V+S → 정서", status="blocked", reason="V·S cache 없음. caption 출처 미확인"),
        dict(analysis="핵심 5 뇌 → V/S", status="blocked", reason="V·S cache 없음"),
        dict(analysis="ROI 단독·제외 비교 (F-4)", status="conditional", reason="핵심 3 뒤. 편도체(Tian S3)·시각(Schaefer Vis) 정의는 지도에 있음"),
        dict(analysis="MindCaptioning 재현", status="conditional", reason="개발 절차 고정 후. MC split 은 같은 규칙으로 그때 생성"),
    ]).to_csv(S1 / "00_status/readiness.tsv", sep="\t", index=False)
    (S1 / "00_status/decision_log.md").write_text("""# 1단계 결정 기록

| 날짜 | 결정 | 근거 |
|---|---|---|
| 2026-10-22 | 주 데이터 = Horikawa 2020, 재현 = MindCaptioning | 사용자 정정 ("명확히 박아놔"). 저장소 문서 02·09, 서버 README 수정 |
| 2026-10-22 | 분할 = horikawa_rungroup6_v1 (run 묶음 6겹, 같은 내용 쌍 같은 쪽, 5명 공통), 기존 무작위 split 삭제 | 사용자 결정. 기존 split 은 61개 run 모두에 fold 가 섞여 누수 위험 (`splits/README.md`) |
| 2026-10-22 | 피험자별 모델, 결과는 피험자별 보존 | 개인 공간 voxel 비대응, 라벨이 영상별 외부 평정, 질문이 참가자 내 새 영상 |
| 2026-10-22 | A34 비율 그대로(합 강제 없음)·A14 별도. 주 지표 = 차원별 영상 간 r, 보완 = 평균 대비 오차 감소, 보조 = 프로필 상관 | GPT 패키지 task_definition·core_questions 와 일치 |
| 2026-10-22 | 드문 감정·낮은 점수 차원을 빼지 않음. A14 결측은 채우지 않음 | GPT 패키지 server_instructions |
| 2026-10-24 | A34 = L2 선형 sigmoid + soft BCE, A14 = ridge. λ·α 는 차원마다 안쪽 검증 손실로 선택 | 패키지 시작안. 기존 코드의 soft BCE 기준선은 없음(08 문서) → 새로 fit |
| 2026-10-24 | 첫 입력 = 469개 영역 평균 | 계산이 가볍고 영역 단위 해석이 쉬움. voxel 입력은 다음 |
| 2026-10-24 | (밝힘) 실행 시간 점검 중 sub-03 fold 0 의 선택 전 중간 λ 결과(r 중앙값 0.36)가 출력됨. 어떤 설정 선택에도 쓰지 않음 | 정직한 기록 |
""")
    print("작성:", sorted(str(p.relative_to(S1)) for p in S1.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
