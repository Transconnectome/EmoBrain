#!/usr/bin/env python3
"""결과 폴더(output_root) 정리와 폴더별 README (11/16 석진 님). GPU 없음, 몇 초.

하는 일(순서대로)
1. move. 돌고 있는 학습이 읽거나 쓰지 않는 폴더만 새 자리로 옮긴다(MOVES). 이미 옮겼으면 건너뛴다.
   새 자리에 이미 무언가 있으면 멈춘다. 옮길 폴더 경로가 지금 도는 프로세스의 명령줄이나 logs의 작업 목록에 있으면 멈춘다.
2. views. s6_brain_model/ 아래에 사람이 여는 폴더를 만들고, 학습 결과 폴더로 가는 상대 링크를 단다.
   학습 결과 폴더는 옮기지 않는다. s6 코드는 fold 폴더 안에 조건 폴더를 쓰고, 같은 fold의 조건들이 plan/을 같이 쓰기 때문이다.
   아직 없는 결과는 링크하지 않고, 대상이 사라진 링크는 지운다. 다시 돌리면 새로 생긴 결과의 링크가 붙는다.
3. readmes. 폴더마다 README.md를 쓴다. 그 폴더가 무슨 분석인지, 무엇이 저장되는지, 안쪽 구조(파일까지), 만든 코드.
   학습 결과 폴더(S6)는 맨 위에만 쓴다. 조건 폴더와 fold 폴더 안에는 쓰지 않는다(코드가 그 폴더의 목록을 읽는다).

아직 하지 않는 것(2단계, 학습이 모두 끝난 뒤): s1~s6 학습 결과, s8, logs를 새 자리로 옮기기.
지금 옮기면 돌고 있는 학습이 입력(s2_manifest, s3_features, s4_no_brain)을 찾지 못하거나 결과를 엉뚱한 곳에 쓴다.

사용: output_layout.py [--dry-run] [--skip-moves]
"""
import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import paths as P  # noqa: E402

OUT = P.OUT
FOLDS = range(1, 7)
BLOCKS = range(1, 6)

# ---------------------------------------------------------------- 1. 옮기기
CHECK_DIRS = [
    "s6_brain_prelim", "s6_brain_prelim_d34", "s6_brain_prelim_oof", "s6_brain_prelim_sep",
    "s6_brain_p1_brainit", "s6_brain_p1_linear", "s6_brain_p1_linear_sampling",
    "s6_check_brainit_nosample", "s6_check_brainit_sample", "s6_check_roi_cells", "s6_check_roi_mean",
    "s6_brain_dense_check", "s6_brain_keep80_check", "s6_brain_wd1000_check",
    "s6_brain_inputstep_lr", "s6_brain_inputstep_mean", "s6_brain_sampling_main",
    "s8_mc_check", "s10_check2", "s10_check3", "s10_network_partial", "smoke_20261109", "superseded",
]
MOVES = [(d, f"checks/{d}") for d in CHECK_DIRS] + [
    ("s9_saved_models/perturb", "checks/s9_perturb_sums_only"),
    ("RESULTS_FOR_CODEX_20261112.md", "notes/RESULTS_FOR_CODEX_20261112.md"),
    ("decisions_before_freeze_2026-11-06.md", "notes/decisions_before_freeze_2026-11-06.md"),
    ("reviews", "notes/reviews"),
    ("docs_explain", "notes/docs_explain"),
    ("s9_saved_models/swap", "s9_saved_model_tests/2-2_swap"),
    ("s9_saved_models_pervideo/perturb", "s9_saved_model_tests/6-4b_perturb"),
    ("s9_path_eval", "s9_saved_model_tests/K1_path_eval"),
    ("s10_feature_decoding", "s10_stats/2-1_feature_decoding"),
    ("s10_swap", "s10_stats/2-2_swap"),
    ("s10_performance", "s10_stats/2-3_performance"),
    ("s10_perturb", "s10_stats/6-4b_perturb"),
    ("s10_k1", "s10_stats/K1_path_eval"),
    ("s10_sensitivity", "s10_stats/ablation_sensitivity"),
]
REMOVE_IF_EMPTY = ["s9_saved_models", "s9_saved_models_pervideo"]


def in_use(rel):
    """옮길 경로가 이 node의 프로세스 명령줄, logs의 작업 목록과 대기 스크립트에 있으면 그 줄을 돌려준다.
    대기 스크립트는 $O/<폴더> 꼴로 쓰므로 절대 경로가 아니라 "/<폴더>" 뒤에 /, 공백, 따옴표, 줄 끝이 오는지로 찾는다."""
    pat = re.compile(r"/" + re.escape(rel) + r"(?=[/\s\"']|$)")
    hits = []
    ps = subprocess.run(["ps", "-u", os.environ.get("USER", ""), "-o", "args="], capture_output=True, text=True).stdout
    hits += [f"ps: {line[:120]}" for line in ps.splitlines() if pat.search(line) and "output_layout" not in line]
    for f in sorted((OUT / "logs").glob("s6_queue_jobs_*.tsv")) + sorted((OUT / "logs").glob("*.sh")):
        for line in f.read_text(errors="ignore").splitlines():
            if pat.search(line):
                hits.append(f"{f.name}: {line[:120]}")
    return hits


def do_moves(dry):
    for src, dst in MOVES:
        s, d = OUT / src, OUT / dst
        if not s.exists() and d.exists():
            print(f"이미 옮김: {dst}")
            continue
        if not s.exists():
            print(f"없음(건너뜀): {src}")
            continue
        if d.exists():
            raise SystemExit(f"새 자리에 이미 있다: {dst}")
        hits = in_use(src)
        if hits:
            raise SystemExit(f"{src}를 쓰는 곳이 있어 멈춘다:\n  " + "\n  ".join(hits))
        print(f"옮김: {src} -> {dst}")
        if not dry:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(s), str(d))
    for name in REMOVE_IF_EMPTY:
        p = OUT / name
        if p.is_dir() and not any(p.iterdir()):
            print(f"빈 폴더 지움: {name}")
            if not dry:
                p.rmdir()


# ---------------------------------------------------------------- 2. 링크
def networks():
    with open(P.S2 / "cabnp_groups.tsv") as f:
        return [(r["group"], r["group_ko"], int(r["n_roi"])) for r in csv.DictReader(f, delimiter="\t")]


VIEW = OUT / "s6_brain_model"
MERGED = "s6_brain_final"

# (보이는 폴더 이름, 코드 이름, 표시 이름, Input → Output, 설명, 질문, 꼴)
MAIN = [
    ("A-1_brain_only", "brain_only", "A-1", "Brain → Emotion",
     "뇌 반응만으로 정서 34개를 학습한다. 장면 정보를 쓰지 않는 기준 모델이다. 다른 모든 조건의 d, 입력층 weight decay는 그 fold의 A-1이 고른 값을 따른다.",
     "01 5-A, 2-3", "plain"),
    ("A-2_brain_only_distill", "brain_only_distill", "A-2", "Brain → Emotion [distillation]",
     "A-1과 구조가 같고 학습 정답만 다르다. 사람 평정과 Stimulus Model 예측 평정을 비율 α로 섞은 값을 정답으로 쓴다. ex) α가 0.5이면 둘을 반씩 섞는다. α가 0이면 A-1과 같아서 새로 학습하지 않는다.",
     "01 5-A, 2-3의 [사전] (다), (라), (마)", "plain"),
    ("B-1_brain_only_featdec", "brain_only_featdec", "B-1", "Brain → Emotion + Vision + Caption",
     "정서와 함께 Vision feature, Caption feature도 맞히게 학습한다. 맞힌 v̂, ĉ는 손실에만 쓰고 정서 계산에는 넣지 않는다. 그래서 A-1과의 차이는 feature를 맞히는 학습을 더했는지 하나다.",
     "01 5-A, 2-3의 [사전] (가), (나), (마)", "feature"),
    ("C-1_brain_decoded", "brain_decoded", "C-1", "Brain + Decoded Feature → Emotion",
     "정서 = g + a(v̂) + b(ĉ) + U[(Av̂) ⊙ (Bĉ)]. g는 ROI token 경로의 점수, v̂와 ĉ는 같은 encoder에서 맞힌 Vision feature와 Caption feature다. 정서 손실이 v̂, ĉ를 만드는 쪽으로 흐르지 않게 막는다(stop-gradient). 바꿔 끼우기(2-2), 처음 보는 장면(6-2), 네트워크 분석(6-4), MC 전이(6-3)는 모두 이 모델과 A-1로 한다.",
     "01 5-A, 2-3의 [사전] (나), (바)", "feature"),
    ("C-2_brain_decoded_distill", "brain_decoded_distill", "C-2", "Brain + Decoded Feature → Emotion [distillation]",
     "C-1과 구조가 같고, 정답만 사람 평정과 Stimulus Model 예측 평정을 섞은 값이다. λ와 rank는 같은 fold의 C-1이 고른 값을 이어받고 α만 고른다.",
     "01 5-A, 2-3의 [사전] (바)", "feature"),
    ("D-1_brain_decoded_sep", "brain_decoded_sep", "D-1", "Brain + Decoded Feature → Emotion [separate feature encoder]",
     "C-1의 식에 Encoder2가 맞힌 v̂₂, ĉ₂를 넣는다. Encoder2는 Vision feature와 Caption feature만으로 학습해 고정한 별도 encoder다(main/D-prep_Encoder2_feature_encoder). 학습 영상의 v̂₂, ĉ₂는 fold 하나를 뺀 Encoder2 넷이 낸 값이고(main/D-prep_Encoder2_minus_one_fold), 검증과 시험 영상은 Encoder2 전체가 낸 값이다. ex) 공유 encoder를 거쳐 정서 학습의 영향이 v̂에 섞이는 길을 끊은 C-1이다.",
     "01 5-A의 D 묶음", "sep"),
    ("D-2_brain_decoded_sep_distill", "brain_decoded_sep_distill", "D-2", "Brain + Decoded Feature → Emotion [separate feature encoder, distillation]",
     "D-1에 distillation을 더했다. λ와 rank는 같은 fold의 D-1이 고른 값을 이어받는다.",
     "01 5-A의 D 묶음", "sep"),
    ("D-3_brain_features_only", "brain_features_only", "D-3", "Decoded Feature → Emotion [separate feature encoder, no direct path]",
     "정서 = a(v̂₂) + b(ĉ₂) + U[(Av̂₂) ⊙ (Bĉ₂)]. ROI token 경로 g가 없다. Encoder2가 맞힌 장면 특징만으로 정서를 얼마나 맞히는지 본다. D-4를 해석하기 위한 짝이다.",
     "01 5-A의 D 묶음", "head_only"),
    ("D-3_paired_brain_features_only_paired", "brain_features_only_paired", "D-3 짝", "Decoded Feature → Emotion [paired]",
     "D-3을 D-4와 같은 짝 방식으로 학습한 비교판이다. 짝 j는 학습 fold j를 뺀 Encoder2와, fold j 영상으로만 학습한 정서 계산이다. 시험 예측은 네 짝의 평균이다.",
     "01 5-A의 D 묶음(11/9)", "paired"),
    ("D-4_brain_frozen_feature_encoder", "brain_frozen_feature_encoder", "D-4", "Brain → Emotion [frozen feature encoder]",
     "고정한 Encoder2의 ROI token H 위에 A-1과 같은 정서 head(emotion query 34개)만 학습한다. 장면 특징으로 미리 학습한 encoder의 표현에서 정서를 읽을 수 있는지 본다. 짝 4개를 학습하고 시험 예측은 네 짝의 평균이다.",
     "01 5-A의 D 묶음(11/9)", "paired"),
    ("E-fixed_brain_only_repr_frozen", "brain_only_repr_frozen", "E-고정", "Brain → Emotion [representation, frozen head]",
     "Multimodal Model(Brain + Vision + Caption)의 head 바로 앞 중간 표현을 뇌만으로 맞히게 학습하고, 정서는 Multimodal Model의 head를 고정해 낸다. 질문 1의 해석에는 쓰지 않는 보조 성능 비교다.",
     "01 5-A의 E 묶음, G16", "repr"),
    ("E-trained_brain_only_repr_trained", "brain_only_repr_trained", "E-학습", "Brain → Emotion [representation, trained head]",
     "E-고정과 같고 Multimodal Model에서 가져온 head도 함께 학습한다.",
     "01 5-A의 E 묶음, G16", "repr"),
]
PREP = [
    ("D-prep_Encoder2_feature_encoder", "feature_encoder", "Encoder2",
     "뇌 반응에서 Vision feature와 Caption feature만 맞히게 학습한 Encoder2다. 정서 출력이 없다. D 묶음이 이 Encoder2를 고정해서 쓴다. learning rate는 검증 feature MSE로 고른다.", "encoder2"),
    ("D-prep_Encoder2_minus_one_fold", "feature_encoder_oof", "fold 하나를 뺀 Encoder2 4개",
     "학습 fold 4개 가운데 하나씩 빼고 학습한 Encoder2 4개다. 뺀 fold 영상의 v̂₂, ĉ₂를 내서 D-1, D-2, D-3의 학습 영상 입력으로 쓴다. 학습 영상의 v̂₂, ĉ₂를 Encoder2 전체로 내면 이미 학습한 영상이라 시험 때보다 훨씬 정확해지기 때문이다.", "oof"),
    ("E-prep_Multimodal_Model", "multimodal", "Multimodal Model",
     "Brain + Vision + Caption → Emotion. 시험 입력에 실제 feature가 들어가서 주 비교 표에는 넣지 않는다. E-고정과 E-학습이 이 모델의 중간 표현과 head를 가져다 쓴다.", "plain"),
]
CONTROL = [
    ("for_A-2_label_smoothing", "control_label_smoothing", "A-2 대조군(label smoothing)",
     "A-2처럼 정답을 섞되, Stimulus Model 예측 대신 학습 영상의 정서 평균 쪽으로만 부드럽게 한다. A-2의 이득이 Stimulus 예측의 내용 때문인지, 정답을 부드럽게 한 것만으로 생기는지 구분한다.", "01 G11, 2-3의 [사전] (라)", "plain"),
    ("for_A-2_shuffled_stimulus_predictions", "control_stimulus_shuffle", "A-2 대조군(Stimulus 예측 섞기)",
     "Stimulus Model 예측 평정을 학습 영상 안에서 다른 영상의 것과 섞은 뒤 정답에 섞는다. ex) 웃긴 영상의 정답에 슬픈 영상의 Stimulus 예측이 섞인다.", "01 G12", "plain"),
    ("for_B-1_shuffled_feature_pairs", "control_feature_shuffle", "B-1 대조군(feature 짝 섞기)",
     "B-1에서 맞힐 Vision feature와 Caption feature를 다른 영상의 것과 짝을 섞어 학습한다. B-1의 이득이 그 영상의 장면 특징 때문인지 본다.", "01 G12", "feature"),
]
ABLATION = [
    ("C-1_additive_head_without_interaction_term", "brain_decoded_additive", MERGED, "C-1 더하기 head",
     "정서 = g + a(v̂) + b(ĉ). C-1에서 두 feature를 곱하는 항 U[(Av̂) ⊙ (Bĉ)]만 뺐다. 두 정보가 따로 보태는지, 서로에 따라 달라지는지 묻는 1-2의 본문 분석이다.", "01 1-2, 4-1", "feature"),
    ("C-1_feature_head_also_learns_from_emotion_loss", "brain_decoded_grad", MERGED, "C-1 손실 흐름 허용판",
     "C-1에서는 정서 손실이 v̂, ĉ를 만드는 쪽(feature query와 그 앞)으로 흐르지 않게 막는다. 이 판은 막지 않는다. 성능 비교에만 쓰고 바꿔 끼우기와 K1에는 쓰지 않는다.", "01 G8", "feature"),
    ("A-1_ROI_token_average_instead_of_query", "brain_only_pool", MERGED, "A-1 ROI token 평균판",
     "본 설계는 정서마다 학습하는 emotion query 34개가 ROI token 370개 가운데 어디를 얼마나 읽을지 attention으로 고른다. 이 판은 그 대신 ROI token 370개를 그냥 평균 내 64차원 벡터 하나로 만들고, 정서 34개를 각각 그 벡터의 선형 함수로 계산한다. ex) fear도 joy도 같은 평균 벡터를 보고, 곱하는 가중치만 다르다. 나머지 설정은 같은 fold의 A-1이 고른 값 그대로다.", "01 F7, N22, O31", "pool_plain"),
    ("C-1_ROI_token_average_instead_of_query", "brain_decoded_pool", MERGED, "C-1 ROI token 평균판",
     "C-1에서 emotion query 34개 대신 ROI token 370개의 평균 벡터 하나로 g를 계산한다(A-1 ROI token 평균판과 같은 방식). v̂, ĉ를 맞히는 feature query 2개는 그대로 있다. 나머지 설정은 같은 fold의 C-1이 고른 값 그대로다.", "01 F7, N22, O31", "pool_feature"),
    ("A-1_encoder_2_blocks", "brain_only", "s6_brain_depth2", "A-1 encoder block 2개",
     "encoder의 self-attention block을 1개에서 2개로 늘린 A-1이다. 나머지 설정은 A-1이 고른 설정 그대로이고(configs/s6/run_config_depth2.json) 후보는 하나다. 본 설계는 결과와 상관없이 바꾸지 않고 보고만 한다.", "01 F3(11/15)", "plain"),
]
ZONE_CONDS = [("A-1_brain_only", "brain_only", "A-1"), ("C-1_brain_decoded", "brain_decoded", "C-1")]


def rel_link(link, target, dry, made):
    rel = os.path.relpath(target, link.parent)
    if link.is_symlink():
        if os.readlink(link) == rel:
            made.append(link)
            return
        if not dry:
            link.unlink()
    elif link.exists():
        raise SystemExit(f"링크 자리에 실제 파일이나 폴더가 있다: {link}")
    if not dry:
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(rel, link)
    made.append(link)


def prune(folder, dry):
    if not folder.is_dir():
        return
    for p in folder.rglob("*"):
        if p.is_symlink() and not p.exists():
            print(f"대상이 없는 링크 지움: {p.relative_to(OUT)}")
            if not dry:
                p.unlink()


def build_views(dry):
    """만든 링크의 상태를 돌려준다. {보이는 폴더: (만든 링크 수, 기대한 수)}"""
    prune(VIEW, dry)
    status = {}

    def folds(view_dir, raw_root, code):
        made = []
        for k in FOLDS:
            t = OUT / raw_root / f"outer_fold{k}" / code
            if t.exists():
                rel_link(view_dir / f"fold{k}", t, dry, made)
        return len(made)

    for name, code, *_ in MAIN:
        status[f"main/{name}"] = (folds(VIEW / "main" / name, MERGED, code), 6)
    for name, code, *_ in PREP:
        n = 0
        for lr, raw in (("lr1e-3", "s6_brain_grid_main"), ("lr1e-4", "s6_brain_grid_lr4")):
            n += folds(VIEW / "main" / name / lr, raw, code)
        status[f"main/{name}"] = (n, 12)
    for name, code, *_ in CONTROL:
        status[f"control/{name}"] = (folds(VIEW / "control" / name, MERGED, code), 6)
    for name, code, raw, *_ in ABLATION:
        status[f"ablation/{name}"] = (folds(VIEW / "ablation" / name, raw, code), 6)
    for name, code, _ in ZONE_CONDS:
        made = []
        for b in BLOCKS:
            for k in FOLDS:
                for kind, shown in (("excluded", "held_out"), ("control", "random_same_size")):
                    t = OUT / "s6_brain_zone" / f"zone_block{b}_fold{k}_{kind}" / code
                    if t.exists():
                        rel_link(VIEW / "analysis/6-2_unseen_content" / name / f"content{b}_fold{k}_{shown}", t, dry, made)
        status[f"analysis/6-2_unseen_content/{name}"] = (len(made), 60)
    for net, _, _ in networks():
        for name, code, _ in ZONE_CONDS:
            status[f"analysis/6-4a_single_network/{net}/{name}"] = (folds(VIEW / "analysis/6-4a_single_network" / net / name, f"s6_brain_net_{net}", code), 6)
    made = []
    for name, code, _ in ZONE_CONDS:
        t = OUT / "s6_brain_final_for_mc/final_for_mc" / code
        if t.exists():
            rel_link(VIEW / "analysis/6-3_model_for_mc" / name, t, dry, made)
    status["analysis/6-3_model_for_mc"] = (len(made), 2)
    if not dry:
        for d in [VIEW / "main" / n for n, *_ in MAIN + PREP] + [VIEW / "control" / n for n, *_ in CONTROL] + [VIEW / "ablation" / n for n, *_ in ABLATION]:
            d.mkdir(parents=True, exist_ok=True)
        for net, _, _ in networks():
            for name, _, _ in ZONE_CONDS:
                (VIEW / "analysis/6-4a_single_network" / net / name).mkdir(parents=True, exist_ok=True)
        for name, _, _ in ZONE_CONDS:
            (VIEW / "analysis/6-2_unseen_content" / name).mkdir(parents=True, exist_ok=True)
        (VIEW / "analysis/6-3_model_for_mc").mkdir(parents=True, exist_ok=True)
    return status


# ---------------------------------------------------------------- 3. README 글
PLAN_TREE = """plan/                          이 분할의 공통 정보. 같은 fold의 모든 조건이 같이 쓴다
├── done.json                  실행 번호(run_key), 코드 커밋, 입력 파일 해시, 설정
├── plan.json                  학습, 검증, 시험 영상 번호
├── rows.npz                   행 순서(participant, video_id, role. role은 0 학습, 1 검증, 2 시험)
└── standardization.npz        학습 fold 4개로 낸 voxel, Vision feature, Caption feature의 평균과 표준편차"""


OUT_FILES = {  # outputs/ 안의 파일(s6_train.FoldRunner.save_outputs)
    "test_outputs": "test_outputs.npz           시험 영상의 logit, p, g(ROI token 경로의 점수)",
    "test_outputs_nog": "test_outputs.npz           시험 영상의 logit, p(ROI token 경로가 없어 g가 없다)",
    "att_emo": "attention_emotion_test.npy 시험 행 × head 4 × 정서 34 × ROI token 370의 attention",
    "att_feat": "attention_feature_test.npy 시험 행 × head 4 × 2(시각, 캡션) × ROI token 370의 attention",
    "dec_test": "decoded_test.npz           시험 영상의 v̂, ĉ",
    "dec_val": "decoded_val.npz            검증 영상의 v̂, ĉ",
    "dec_acc": "decoding_accuracy.tsv      학습, 검증 영상에서 v̂, ĉ가 실제 feature와 맞는 정도(feature 짝을 섞은 대조군에는 없다)",
    "dec2_test": "decoded_test.npz           정서 계산에 쓴 Encoder2의 v̂₂, ĉ₂(시험 영상)",
    "dec2_val": "decoded_val.npz            같은 값(검증 영상)",
    "aux_test": "aux_decoded_test.npz       이 모델 자기 encoder(Encoder1)의 feature head가 맞힌 v̂, ĉ(손실에만 씀, 시험 영상)",
    "aux_val": "aux_decoded_val.npz        같은 값(검증 영상)",
    "acc_aux": "decoding_accuracy_aux.tsv  Encoder1 보조 출력이 실제 feature와 맞는 정도",
}
KIND_OUT = {
    "plain": ["test_outputs", "att_emo"],
    "repr": ["test_outputs", "att_emo"],
    "feature": ["test_outputs", "att_emo", "att_feat", "dec_test", "dec_val", "dec_acc"],
    "pool_plain": ["test_outputs"],
    "pool_feature": ["test_outputs", "att_feat", "dec_test", "dec_val", "dec_acc"],
    "sep": ["test_outputs", "att_emo", "dec2_test", "dec2_val", "aux_test", "aux_val", "acc_aux"],
    "head_only": ["test_outputs_nog"],
    "encoder2": ["dec_test", "dec_val", "dec_acc"],
}


def cand_tree(kind, indent=""):
    """조건 폴더 하나의 안쪽(s6_train.py 머리말의 저장 형식, save_outputs)."""
    lines = [
        "├── selection.tsv              후보마다 설정(d, 입력층 weight decay, learning rate, λ, α, rank)과 검증 점수, 멈춘 epoch",
        "├── selected.json              고른 후보, 0 후보를 골랐는지(zero_selected), seed마다 결과 폴더 위치(seeds)",
        "└── <후보 번호>_seed0/          후보 하나를 학습한 결과. 후보 번호는 후보 설정에서 만든 12자리 이름이다",
    ]
    if kind == "paired":
        lines += [
            "    ├── pair<j>/               짝 하나. j는 학습 fold 번호다(ex) fold 1이 시험이면 j는 3, 4, 5, 6)",
            "    │   ├── done.json          실행 기록",
            "    │   ├── history.tsv        epoch마다 학습 손실과 검증 손실",
            "    │   ├── model.pt           학습한 가중치",
            "    │   ├── val_pred.npz       검증 영상 예측",
            "    │   └── test_pred.npz      시험 영상 예측(이 짝 하나)",
            "    └── ensemble/              네 짝의 예측 평정(0~1)을 평균한 예측",
            "        ├── done.json",
            "        ├── val_pred.npz",
            "        └── test_pred.npz      성능 표(S10)가 읽는 시험 예측",
        ]
    elif kind == "oof":
        return "\n".join([
            "└── seed0/",
            "    └── inner<j>/              학습 fold j를 빼고 학습한 Encoder2. j는 학습 fold 번호다(ex) fold 1이 시험이면 3, 4, 5, 6)",
            "        ├── done.json          실행 기록",
            "        ├── history.tsv        epoch마다 학습 손실과 검증 feature 손실",
            "        ├── model.pt           학습한 가중치",
            "        └── held.npz           뺀 fold j 영상의 v̂₂, ĉ₂ (D-1, D-2, D-3의 학습 영상 입력)",
        ])
    else:
        lines += [
            "    ├── done.json              실행 기록(코드 커밋, 입력 해시, 설정, 멈춘 epoch, 검증 점수, 가중치 수, 걸린 시간, GPU 메모리)",
            "    ├── model.pt               학습한 가중치. 고르지 않은 후보는 지운다",
            "    ├── parameter_groups.json  파라미터마다 weight decay 묶음",
        ]
        if kind == "encoder2":
            lines += ["    ├── history.tsv            epoch마다 학습 손실과 검증 feature 손실. 정서 출력이 없어 val_pred, test_pred가 없다"]
        else:
            lines += [
                "    ├── history.tsv            epoch마다 학습 손실, 검증 정서 soft BCE, 검증 손실(조기 종료 기준)",
                "    ├── val_pred.npz           검증 영상 예측(participant, video_id, logit, p)",
                "    ├── test_pred.npz          시험 영상 예측. 후보마다 저장하지만 고를 때는 쓰지 않는다",
            ]
        if kind == "repr":
            lines += [
                "    ├── representation_stats.npz  Multimodal Model 중간 표현의 평균과 표준편차",
                "    ├── teacher.json           짝지은 Multimodal Model 체크포인트의 해시",
            ]
        files = ["done.json                  outputs를 만든 기록"] + [OUT_FILES[x] for x in KIND_OUT[kind]]
        lines += ["    └── outputs/               고른 후보에만 있다"]
        lines += [f"        {'└──' if i == len(files) - 1 else '├──'} {f}" for i, f in enumerate(files)]
    return "\n".join(indent + x for x in lines)


MERGED_NOTE = """합친 폴더(s6_brain_final)의 조건 폴더는 두 가지 꼴이다.
- learning rate 1e-3 실행의 조건 폴더 전체로 가는 링크. ex) A-1은 1e-3 실행만 있어서 이 꼴이다
- selected.json과, 고른 후보 폴더로 가는 링크만 든 폴더. 이때 selection.tsv는 없고 후보 전체 표는 원래 실행 폴더(s6_brain_grid_main 또는 s6_brain_grid_lr4)에 있다
어느 실행을 골랐는지는 s6_brain_final/merge_record.tsv에 있다."""


FEATURE_NOTE = "(C-1 꼴이다. A-1에는 attention_feature_test.npy, decoded_*.npz, decoding_accuracy.tsv가 없다. 조건마다 정확한 파일은 s6_brain_model/의 조건 README에 있다)"


def rd(title, summary, what, stored, tree, code, extra=""):
    parts = [f"# {title}\n", summary.strip() + "\n", "## 무엇을 하는 분석인가\n", what.strip() + "\n", "## 무엇이 저장되는가\n", stored.strip() + "\n",
             "## 안쪽 구조\n", "```text\n" + tree.strip("\n") + "\n```\n"]
    if extra:
        parts.append(extra.strip() + "\n")
    parts += ["## 만든 코드\n", code.strip() + "\n", "\n이 README는 scripts/output_layout.py가 만든다. 고칠 때는 그 파일을 고치고 다시 돌린다.\n"]
    return "\n".join(parts)


def cond_readme(name, code, display, io, desc, question, kind, raw_desc, status):
    made, want = status
    st = f"지금 링크 {made}개 / {want}개." + ("" if made == want else " 아직 없는 fold는 학습이나 합치기가 끝나면 scripts/output_layout.sh를 다시 돌려 붙인다.") + " 링크 안에 selected.json이 있어야 그 fold의 학습이 끝난 것이다."
    sub = "fold1/ … fold6/" if want == 6 else "lr1e-3/fold1/ … lr1e-4/fold6/"
    first = "fold<k>/" if want == 6 else "lr1e-3/fold<k>/, lr1e-4/fold<k>/"
    tree = f"{name}/\n├── README.md\n└── {first}   바깥 fold k를 시험으로 쓴 학습 결과로 가는 링크. 안쪽은 아래와 같다\n" + cand_tree(kind, "    ")
    stored = f"""바깥 fold 6개마다 이 조건을 학습한 결과다. {sub}는 실제 학습 결과 폴더로 가는 링크다.
- 링크가 가리키는 곳: {raw_desc}
- {st}
- 시험 예측은 fold마다 그 fold 영상(약 350개 영상 × 참가자)이고, 6 fold를 모으면 개발 영상 전체가 한 번씩 시험된다."""
    return rd(name, f"{display}. {io}. 코드 이름 {code}", desc + f"\n\n관련 절: {question}", stored, tree, "src/s6_train.py(학습), src/s6_model.py(구조), src/s6_common.py(조건과 후보). 합치기는 scripts/s6_merge_lr.py",
              MERGED_NOTE if raw_desc.startswith("s6_brain_final") else "")


def write(path, text, dry, written):
    written.append(path)
    if dry:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def root_readme(status):
    return rd("final_2026-11 (EmoBrain 결과 폴더)",
              "EmoBrain의 큰 산출물(feature, 학습한 모델, 예측, 통계 표, 로그)이 모두 여기 있다. 레포 밖이고 git에 올리지 않는다. 폴더 이름의 s1~s10은 코드(src/s1_*.py ~ src/s10_*.py)의 단계 번호와 같다.",
              """단계마다 앞 단계가 저장한 파일을 뒤 단계가 읽는다.
s1 원자료 점검 → s2 경계 고정 → s3 feature 뽑기 → s4 뇌 없는 모델 → s5 ridge와 기준선 → s6 뇌 모델 학습 → s8 MC 전이 → s9 저장한 모델로 실험 → s10 통계.
s7은 파일럿과 실행 설정 동결 단계라 폴더가 없다.

11/16에 정리를 두 번에 나눴다.
- 1단계(지금): 돌고 있는 학습이 읽거나 쓰지 않는 것만 옮겼다. 점검 실행은 checks/, 메모는 notes/, s9 결과는 s9_saved_model_tests/, s10 결과는 s10_stats/로 갔다. s6 학습 결과는 옮기지 않고 s6_brain_model/에 사람이 여는 폴더(링크)를 만들었다.
- 2단계(학습이 모두 끝난 뒤): s1~s6 학습 결과, s8, logs를 아래 목표 구조로 옮긴다. 지금 옮기면 돌고 있는 학습이 입력(s2_manifest, s3_features, s4_no_brain)을 찾지 못하거나 결과를 엉뚱한 곳에 쓴다.""",
              """- 논문에 쓰는 결과: s1~s10 폴더
- s6 결과를 볼 때는 s6_brain_model/부터 연다. 주 비교(main), 대조군(control), 모델 한 부분만 바꾼 판(ablation), 질문 하나를 위해 다시 학습한 것(analysis)으로 나눠 표시했다
- 논문에 쓰지 않는 점검 실행: checks/
- 메모와 검토 보고서: notes/
- 실행 기록: logs/""",
              """final_2026-11/
├── README.md
├── s1_original_rois/          저자 공개 ROI를 우리 뇌 격자로 옮긴 결과(S1)                    → 2단계에 s1_data_checks/로
├── s1_subcortex_rebuild/      피질하 ROI 10개를 새로 만든 결과(S1)                              → 2단계에 s1_data_checks/로
├── s2_manifest/               참가자마다 ROI 370개의 voxel 값 배열(S2). 학습이 읽는 중         → 2단계까지 그대로
├── s3_features/               Vision feature, Caption feature 등(S3). 학습이 읽는 중           → 2단계까지 그대로
├── s3_timing/                 feature 추출 전 시간과 메모리 측정(S3)                            → 2단계에 s3_features/ 아래로
├── s4_no_brain/               Stimulus Model 등 뇌 없는 모델(S4). 학습이 읽는 중               → 2단계에 s4_no_brain_models/로
├── s4_no_brain_lr/            Stimulus Model learning rate 다시 본 판(S4, 쓰지 않음)            → 2단계에 s4_no_brain_models/ 아래로
├── s5_ridge/                  ridge decoding, 기준선, 외부 모델, ROI 지도(S5)                    → 2단계에 s5_ridge_and_baselines/로
├── s6_brain_model/            s6 결과를 조건 기준으로 보는 폴더(링크). 여기부터 연다
├── s6_brain_grid_main/        s6 학습 원본. learning rate 1e-3 실행                              → 2단계에 s6_brain_model/raw_runs_by_fold/lr1e-3/로
├── s6_brain_grid_lr4/         s6 학습 원본. learning rate 1e-4 실행                              → 2단계에 raw_runs_by_fold/lr1e-4/로
├── s6_brain_final/            두 실행을 조건, fold마다 검증 r로 합친 폴더(링크)                   → 2단계에 raw_runs_by_fold/merged/로
├── s6_brain_zone/             6-2 처음 보는 장면용 학습 원본                                     → 2단계에 raw_runs_by_fold/unseen_content/로
├── s6_brain_net_<묶음>/        6-4a 네트워크 하나만으로 학습한 원본(13개)                         → 2단계에 raw_runs_by_fold/single_network/로
├── s6_brain_final_for_mc/     6-3 MC 전이용 모델 원본                                            → 2단계에 raw_runs_by_fold/model_for_mc/로
├── s6_brain_depth2/           encoder block 2개 민감도 원본                                      → 2단계에 raw_runs_by_fold/encoder_2_blocks/로
├── s9_saved_model_tests/      저장한 모델로 입력만 바꿔 낸 예측(S9)
├── s10_stats/                 통계 표(S10). 질문마다 폴더 하나
├── checks/                    논문에 쓰지 않는 점검 실행
├── notes/                     메모, 검토 보고서, 설명 페이지
└── logs/                      실행 로그, 작업 목록, 대기 스크립트                               → 2단계에 단계별 하위 폴더로""",
              "scripts/output_layout.py(이 정리와 README). 각 폴더를 만든 코드는 그 폴더의 README에 있다.",
              """## 2단계 목표 구조

```text
final_2026-11/
├── s1_data_checks/            s1_original_rois, s1_subcortex_rebuild
├── s2_manifest/
├── s3_features/               s3_timing 포함
├── s4_no_brain_models/        s4_no_brain, s4_no_brain_lr
├── s5_ridge_and_baselines/    brain_to_feature_ridge, emotion_baselines, external_models, roi_map
├── s6_brain_model/
│   ├── main/  control/  ablation/  analysis/      지금과 같은 이름(링크)
│   └── raw_runs_by_fold/      코드가 쓰는 원본. lr1e-3, lr1e-4, merged, unseen_content, single_network, model_for_mc, encoder_2_blocks
├── s8_mc_transfer/            6-3_mc_transfer/{A-1_brain_only, C-1_brain_decoded}
├── s9_saved_model_tests/
├── s10_stats/
├── checks/
├── notes/
└── logs/
```""")


CHECK_ENTRIES = [
    ("s6_brain_prelim", "11/8", "화요일 발표용 예비 실행. d 64, 입력층 weight decay 0.01, learning rate 1e-4, seed 0(run_config_prelim_20261108.json). 11/15 입력층 학습 폭 점검의 요약 표(summary/)도 여기 있다", "11/13 본 실행(s6_brain_grid_main)"),
    ("s6_brain_prelim_d34", "11/9", "D-3, D-4 예비 실행", "D 묶음 본 실행(s6_brain_grid_main, s6_brain_grid_lr4)"),
    ("s6_brain_prelim_oof", "11/9", "fold 하나를 뺀 Encoder2 4개와 짝 학습(D-4, D-3 짝)의 예비 실행", "D 묶음 본 실행"),
    ("s6_brain_prelim_sep", "11/9", "D-1, D-2 예비 실행. 같은 설정의 C-1, C-2와 비교하려고 A-1, Encoder2도 다시 돌렸다", "D 묶음 본 실행"),
    ("s6_check_brainit_nosample", "11/9", "입력층 점검. Brain-IT tokenizer를 ROI 370개에 얹은 입력층, voxel 뽑기 없음. A-1", "11/10 1순위 실행에서 두 입력층 비교"),
    ("s6_check_brainit_sample", "11/9", "입력층 점검. Brain-IT tokenizer, voxel 뽑기 있음. A-1", "11/10 1순위 실행"),
    ("s6_check_roi_cells", "11/9", "입력층 점검. ROI마다 8칸 평균(GED, ML-BVAE, EmoGrowth의 ROI pooling). A-1", "본 설계(선형 입력층) 유지"),
    ("s6_check_roi_mean", "11/9", "입력층 점검. ROI마다 voxel 평균 하나. A-1", "본 설계(선형 입력층) 유지"),
    ("s6_brain_p1_linear", "11/10", "1순위 실행. 선형 입력층으로 조건 전부", "11/13 본 실행(voxel 뽑기를 넣은 선형 입력층)"),
    ("s6_brain_p1_brainit", "11/10", "1순위 실행. Brain-IT 입력층으로 조건 전부", "11/13 본 실행"),
    ("s6_brain_p1_linear_sampling", "11/12", "원인 분리 점검. 선형 입력층에 voxel 뽑기 0.375만 더한 A-1, B-1. Brain-IT 입력층의 이득이 어디서 오는지 확인", "11/13 본 실행 설정 변경의 근거"),
    ("s6_brain_sampling_main", "11/13", "선형 입력층 + voxel 뽑기 0.375, 입력층 weight decay {1, 10, 100}, learning rate 1e-4로 8개 조건", "같은 날 learning rate × weight decay grid 실행(s6_brain_grid_main)"),
    ("s6_brain_wd1000_check", "11/13", "A-1 입력층 weight decay 1000 점검(후보 끝값을 골라서 한 칸 더 본 것)", "후보 범위 유지"),
    ("s6_brain_dense_check", "11/14", "MindEye2 꼴 입력층 점검. ROI로 묶지 않고 모든 voxel을 참가자별 선형층 하나로 token 하나에 보낸다. A-1", "본 설계(ROI 370개 token) 유지"),
    ("s6_brain_keep80_check", "11/14", "voxel 뽑기(약 31% 남김) 대신 voxel마다 20% 확률로 빼는 입력 dropout 점검. A-1", "본 설계 유지"),
    ("s6_brain_inputstep_lr", "11/15", "입력층 W만 learning rate를 10배 낮춘 점검. A-1", "지금 설계 유지(04 11/15 기록)"),
    ("s6_brain_inputstep_mean", "11/15", "ROI token을 voxel의 합 대신 평균으로 만든 점검. A-1", "지금 설계 유지(04 11/15 기록)"),
    ("s8_mc_check", "11/14~15", "MC 전이 확인 실행. 최종 모델 전에 시간과 동작을 확인했다. s10_mc.py는 확인 실행을 거절한다", "MC 본 실행(HK 최종 모델이 끝나면 자동으로 뜸)"),
    ("s10_check2", "11/15", "S10 코드를 일부 결과로 돌려 본 점검(2-1, 2-2, 6-2, 6-3, 6-4a, 6-4b, Holm). 일부는 빠진 입력 때문에 거절된 기록이다", "s10_stats/의 계산"),
    ("s10_check3", "11/15", "K1 경로 평가(S9, S10)를 점검 모드로 돌려 본 것", "s9_saved_model_tests/K1_path_eval, s10_stats/K1_path_eval"),
    ("s10_network_partial", "11/15", "6-4a를 끝난 fold만으로 낸 중간 표", "6-4a 학습이 끝나면 s10_stats/6-4a_single_network에 낼 최종 표"),
    ("s9_perturb_sums_only", "11/14", "6-4b 입력 교란의 첫 계산. 참가자별 합만 저장했다. 안에 s6_brain_grid_main(합치기 전 1e-3 실행), s6_brain_final이 있다", "영상별 예측까지 저장한 판(s9_saved_model_tests/6-4b_perturb). 영상 단위 bootstrap을 하려고 다시 냈다"),
    ("smoke_20261109", "11/9", "D 예비 실행 제출을 확인한 메모(dprelim_submit.txt)", "없음"),
    ("superseded", "11/8~9", "버린 판 넷. s5_emogrowth_proportion_target_20261109(EmoGrowth 목표를 평정 비율로 둔 옛 판), s5_mlbvae_mean_loss_20261109(ML-BVAE 손실을 평균으로 둔 옛 판), s6_brain_prelim_sep_codechange_20261109(D 예비 실행 도중 코드가 바뀐 판), s6_check_brainit_old_impl_20261109(Brain-IT 입력층의 옛 구현)", "s5_ridge의 새 판, s6_brain_prelim_sep, s6_check_brainit_*"),
    ("roi_ridge_20261109", "11/9", "ROI 단위 입력 ridge 점검(ROI 평균 370개, ROI별 주성분). 뇌 모델이 voxel 전체 ridge보다 낮았던 원인이 ROI 단위 입력인지 본 것", "입력층 점검(s6_check_*)"),
]


def checks_readme():
    rows = "\n".join(f"├── {n}/" for n, *_ in CHECK_ENTRIES[:-1]) + f"\n└── {CHECK_ENTRIES[-1][0]}/"
    body = "\n".join(f"- **{n}** ({d}). {w}. 대신 쓰는 것: {r}" for n, d, w, r in CHECK_ENTRIES)
    return rd("checks (점검 실행)",
              "논문 표에 들어가지 않는 실행을 모았다. 설정을 정하거나 코드가 잘 도는지 보려고 돌린 것이다. 지우지 않고 근거로 남긴다.",
              "각 폴더가 무엇을 점검했고 무엇으로 대체되었는지는 아래와 같다. 근거와 판정은 docs/final/04_claude_code_workorder.md의 기록 칸과 01에 있다.\n\n" + body,
              "s6 점검 폴더의 안쪽은 s6 학습 원본과 같은 꼴이다(outer_fold<k>/plan/, outer_fold<k>/<조건 코드 이름>/, 후보 폴더). 자세한 파일 설명은 s6_brain_model/README.md에 있다.",
              "checks/\n├── README.md\n" + rows,
              "각 실행의 설정은 레포 configs/s6/run_config_*.json(note 항목)에 있다. 옮긴 것은 scripts/output_layout.py")


def notes_readme():
    return rd("notes (메모와 검토 보고서)",
              "계산 결과가 아닌 글을 모았다.",
              "설계 결정 전후의 메모, Codex 검토 보고서, 석진 님께 드린 설명 페이지다.",
              "- RESULTS_FOR_CODEX_20261112.md: 11/12 Codex 검토용으로 정리한 결과 메모\n- decisions_before_freeze_2026-11-06.md: 설계 동결 전 결정 메모(11/6)\n- reviews/: Codex 검토 보고서\n- docs_explain/: 조건 지도 설명 페이지(HTML, Markdown). emobrain_condition_map_older_copy.*는 11/15 00시 판이고 그 뒤 판이 emobrain_condition_map_20261115.*다",
              """notes/
├── README.md
├── RESULTS_FOR_CODEX_20261112.md
├── decisions_before_freeze_2026-11-06.md
├── reviews/
│   └── codex_lr_wd_dropout_20261114.md   Codex 검토(learning rate, weight decay, dropout)
└── docs_explain/
    ├── emobrain_condition_map_20261115.html / .md   조건 지도(입력층 흐름, 조건별 샘플 흐름)
    └── emobrain_condition_map_older_copy.html / .md  같은 페이지의 앞선 판""",
              "손으로 쓴 문서다.")


def s9_readmes():
    out = {}
    out["s9_saved_model_tests"] = rd("s9_saved_model_tests (저장한 모델로 하는 실험)",
        "S6이 고른 모델을 다시 학습하지 않고 불러, 시험 영상의 입력 일부를 바꿔 넣거나 decoded features를 다른 head에 넣어 예측을 저장한다. 통계는 S10이 이 예측으로 낸다.",
        "모델은 고정되어 있다. 바꾸는 것은 시험 때 넣는 값뿐이다. ex) C-1에서 v̂만 다른 영상의 것으로 바꾸면 정서 예측이 그 영상의 정서 쪽으로 움직이는지 본다.",
        "- 2-2_swap/: 바꿔 끼우기(C-1)\n- 6-4b_perturb/: 네트워크, ROI 입력 교란(A-1, C-1)\n- K1_path_eval/: 경로 평가(K1, K1a)",
        "s9_saved_model_tests/\n├── README.md\n├── 2-2_swap/\n├── 6-4b_perturb/\n└── K1_path_eval/",
        "src/s9_saved_models.py(swap, perturb), src/s9_path_eval.py(K1)")
    out["s9_saved_model_tests/2-2_swap"] = rd("2-2_swap (바꿔 끼우기)",
        "C-1 모델에서 v̂, ĉ를 짝 영상의 것으로 바꿔 넣은 예측이다.",
        """01 2-2(정서를 예측할 때 decoding한 장면 정보를 쓰는가), 1-1(정서마다 어느 정보와 더 강하게 연결되는가), 1-2의 (나)(결합 지표).
- 짝: 같은 시험 fold에서 이름표 73개 거리가 가장 가까운 영상 A, B(S2 pairs_directed.tsv). 그 참가자에게 두 영상이 모두 있는 짝만 쓴다
- ROI token 경로는 A로 고정하고(g(H_A)), 시각만, 캡션만, 둘 다를 B의 값으로 바꾼다
- 같은 크기의 무작위 변경 대조 100회를 함께 낸다
ex) A가 웃긴 강아지 영상, B가 비슷한 장면의 슬픈 영상이면, v̂만 B의 것으로 바꿨을 때 예측이 슬픈 쪽으로 움직이는지 본다.""",
        "바깥 fold와 seed마다 참가자별 교체 전후 예측, 무작위 대조, 쓴 짝 목록.",
        """2-2_swap/
├── README.md
└── s6_brain_final/                 읽은 S6 결과 폴더 이름(합친 폴더)
    └── outer_fold<k>_seed0/        바깥 fold k, seed 0 (k = 1~6)
        ├── done.json               실행 기록(코드, 입력 해시, 설정)
        ├── interventions.pt        참가자마다 교체 전후 logit과 예측, 무작위 대조 100회, 결합 지표
        └── pairs_used.tsv          쓴 짝과, 그 참가자에게 영상이 없어 뺀 짝""",
        "src/s9_saved_models.py --task swap (scripts/s9_saved_models.sh swap)")
    out["s9_saved_model_tests/6-4b_perturb"] = rd("6-4b_perturb (네트워크, ROI 입력 교란)",
        "A-1과 C-1에서 네트워크 묶음 하나 또는 ROI 하나의 입력을 다른 영상의 뇌 반응으로 바꿔 넣은 예측이다.",
        """01 6-4b와 그 ROI판(질문 2-4, 모델은 어느 영역에 기대는가).
- 교체: CAB-NP 13묶음 또는 ROI 하나의 입력을 같은 참가자, 같은 시험 fold의 다른 시험 영상 값으로 바꾼다. 0으로 지우지 않는다
- 다른 영상 배정은 20번 반복하고, 두 모델과 모든 묶음, ROI에 같은 배정표를 쓴다
ex) Visual2 묶음의 ROI 입력만 다른 영상의 것으로 바꿨을 때 정서 r이 얼마나 떨어지는지가 그 묶음에 기대는 정도다.""",
        "바깥 fold마다 원래 예측, 교란 예측(묶음 13개 + ROI 370개 = 단위 383개 × 반복 20회), 참가자별 합. 영상별 예측은 6 fold 합쳐 약 22 GB다.",
        """6-4b_perturb/
├── README.md
└── s6_brain_final/                       읽은 S6 결과 폴더 이름(합친 폴더)
    └── outer_fold<k>_seed0/              바깥 fold k, seed 0 (k = 1~6)
        ├── done.json                     실행 기록, 배정 seed
        ├── perturb_sums.npz              참가자마다 원래, 교란 예측의 합, 제곱합, 사람 평정과의 곱의 합, 배정표
        ├── perturb_pred.npz              행 열쇠(participant, video_id), 단위 이름, 조건마다 원래 예측(행 × 34)
        ├── perturb_pred_brain_only.npy   A-1 교란 예측(단위 383 × 반복 20 × 행 × 34, float32 확률)
        └── perturb_pred_brain_decoded.npy  C-1 교란 예측(같은 꼴)""",
        "src/s9_saved_models.py --task perturb (scripts/s9_saved_models.sh perturb). 합만 저장한 첫 계산은 checks/s9_perturb_sums_only")
    out["s9_saved_model_tests/K1_path_eval"] = rd("K1_path_eval (경로 평가)",
        "실제 Vision feature와 Caption feature로 학습해 고정한 Stimulus Model의 head(S4)에, 뇌에서 decoding한 v̂, ĉ만 넣어 낸 정서 예측이다.",
        """01 K1(정서 34개), K1a(정서 차원 14개). 뇌 모델과 Stimulus Model은 더 학습하지 않고, ROI token 경로는 넣지 않는다.
- 입력 두 판: ridge decoded features(S5) 판, C-1 decoded features 판
- head 두 개: 더하기 head, 상호작용 head
- 보정 전과 N8 보정판(검증 fold 통계로 평균과 크기를 맞춤)
ex) 뇌에서 맞힌 장면 특징만으로도, 영상을 보고 학습한 정서 계산이 얼마나 맞는지 본다.""",
        "fold마다 판별 예측과 출처 기록.",
        """K1_path_eval/
├── README.md
└── s6_brain_final/                 읽은 S6 결과 폴더 이름
    ├── done.json                   입력과 출력 파일의 sha256
    ├── coverage.tsv                fold마다 읽은 파일과 상태
    ├── head_check.tsv              읽은 head가 S4 저장 출력과 같은지
    ├── n8_counts.tsv               N8 보정에서 평균만 옮긴 차원 수
    └── units/
        ├── ridge_fold<k>.npz       ridge decoded features를 넣은 예측(k = 1~6)
        └── c1_seed0_fold<k>.npz    C-1 decoded features(seed 0)를 넣은 예측""",
        "src/s9_path_eval.py (scripts/s9_path_eval.sh)")
    return out


def s10_readmes():
    out = {}
    out["s10_stats"] = rd("s10_stats (통계 표)",
        "저장된 예측만 읽어 정서별 r, bootstrap 구간, p, Holm, BH를 낸다. GPU를 쓰지 않는다. 질문마다 폴더 하나이고 이름은 s6, s9 폴더와 같다.",
        "표는 대부분 두 조건을 비교한다. 그래서 조건이 아니라 질문으로 나눴다. ex) 6-2_unseen_content는 s6_brain_model/analysis/6-2_unseen_content의 학습 결과로 낸 표다.",
        """- 2-1_feature_decoding/, 2-2_swap/, 2-3_performance/, 6-4b_perturb/, K1_path_eval/, ablation_sensitivity/: 지금 있음
- 6-2_unseen_content/, 6-3_mc_transfer/, 6-4a_single_network/, holm_15/: 학습이 끝나면 최종 계산 때 생긴다
- 계산한 날짜, 코드 커밋, 입력 해시는 각 폴더의 run_info.json에 있다. 학습이 모두 끝나면 같은 코드로 다시 계산해 최종 표를 낸다""",
        "s10_stats/\n├── README.md\n├── 2-1_feature_decoding/\n├── 2-2_swap/\n├── 2-3_performance/          중간 계산\n├── 6-4b_perturb/\n├── K1_path_eval/\n└── ablation_sensitivity/",
        "src/s10_*.py, scripts/s10_*.sh")
    out["s10_stats/2-1_feature_decoding"] = rd("2-1_feature_decoding",
        "뇌에서 Vision feature와 Caption feature를 decoding할 수 있는지에 대한 [사전] 2개 검정 표다.",
        "01 2-1. ridge decoding(층 예측을 이어 붙인 Vision feature, Caption feature)의 차원별 r 평균을 순열 기준(같은 fold, 같은 run 안에서 실제 feature를 섞음)과 비교한다. C-1 decoded features도 같은 지표로 낸다.",
        "참가자와 5명 평균의 점수, 구간, 보정 전 p.",
        """2-1_feature_decoding/
├── README.md
├── decoding_scores.tsv        ridge decoding의 차원별 r 평균, 순열 기준, bootstrap 구간, 같은 fold 안 영상 식별
├── c1_decoding_scores.tsv     C-1 decoded features의 같은 지표
├── c1_seed_summary.tsv        C-1 판의 seed 평균과 표준편차
├── prereg_pvalues.tsv         [사전] 2개의 보정 전 p (holm_15가 읽음)
├── coverage.tsv               읽은 파일
├── arrays.npz                 재표집 배열
└── run_info.json              입력 해시, 설정, 코드 커밋, 걸린 시간""",
        "src/s10_feature_decoding.py (scripts/s10_feature_decoding.sh)")
    out["s10_stats/2-2_swap"] = rd("2-2_swap",
        "바꿔 끼우기 결과의 표다. [사전] 3개(시각만, 캡션만, 둘 다 바꿈 대 같은 크기 무작위 변경)와 1-1, 1-2 (나).",
        "01 2-2, 1-1, 1-2. s9_saved_model_tests/2-2_swap의 예측을 읽는다. 짝 연결 묶음 단위 bootstrap을 쓴다.",
        "효과 크기, 구간, 보정 전 p, 정서별 표.",
        """2-2_swap/
├── README.md
└── s6_brain_final/                     읽은 S6 결과 폴더 이름
    ├── swap_scores.tsv                 [사전] 3개의 효과(교체 효과 − 무작위 대조 평균), 구간, p
    ├── swap_per_emotion.tsv            정서별 교체 효과(탐색, BH)
    ├── path_difference_per_emotion.tsv 1-1. 정서별 시각 경로 효과와 캡션 경로 효과의 차이
    ├── interaction_per_emotion.tsv     1-2 (나). 정서별 결합 지표
    ├── kragel_groups.tsv               Kragel 묶음 보조 비교
    ├── clusters.tsv                    짝 연결 묶음의 크기 분포
    ├── prereg_pvalues.tsv              [사전] 3개의 보정 전 p
    ├── coverage.tsv
    └── run_info.json""",
        "src/s10_swap.py (scripts/s10_swap.sh)")
    out["s10_stats/2-3_performance"] = rd("2-3_performance (중간 계산)",
        "조건별 성능 표다. 지금 있는 것은 D, E 묶음과 ablation 결과가 합쳐지기 전에 낸 중간 계산이다. 학습이 모두 끝나면 다시 계산해 덮어쓴다.",
        """01 2-3(그렇게 학습하면 예측과 일반화가 나아지는가), 2-4, 6-0, 6-1.
- 주 지표: 참가자마다, 정서마다 6 fold의 시험 예측을 모아 Pearson r을 한 번 낸다
- 보조 지표: R², MAE(평정 0인 영상과 0보다 큰 영상을 나눔), 평균 예측 대비 오차 감소, 영상별 프로필 상관
- [사전] 2-3 여섯 비교와 보조 비교, 0행 전제 검정(순열)
ex) per_emotion.tsv에서 C-1의 fear 행을 보면 5명 각각의 r과 구간이 있다.""",
        "all/(참가자가 본 영상 전체)과 common5/(5명 모두 본 영상만)에 같은 표를 쓴다.",
        """2-3_performance/
├── README.md
└── s6_brain_final/                     읽은 S6 결과 폴더 이름(합친 폴더)
    ├── all/                            참가자가 본 영상 전체
    │   ├── per_emotion.tsv             조건, 참가자, 정서마다 r, R², MAE, 구간
    │   ├── participant_scores.tsv      조건, 참가자마다 34개 정서 평균 점수
    │   ├── seed_summary.tsv            seed 평균과 표준편차
    │   ├── comparisons.tsv             조건 비교([사전] 여섯과 보조), 차이, 구간, p
    │   ├── comparisons_per_emotion.tsv 정서별 조건 차이(탐색, BH)
    │   ├── premise_tests.tsv           0행 전제 검정(A-1, C-1 대 순열 기준)
    │   ├── premise_per_emotion.tsv     전제 검정의 정서별 표
    │   ├── noncomputable.tsv           계산할 수 없는 r의 수
    │   ├── per_emotion_r_seed0.png     정서별 r 그림
    │   └── participant_scores_seed0.png 참가자 점수 그림
    ├── common5/                        5명 공통 영상만. all/과 같은 파일
    ├── coverage.tsv                    조건, seed, fold마다 읽은 파일과 0 후보 여부
    ├── prereg_pvalues.tsv              [사전] 여섯의 보정 전 p
    ├── rows.tsv                        참가자별 영상 수
    └── run_info.json""",
        "src/s10_performance.py, src/s10_figures.py (scripts/s10_performance.sh)")
    out["s10_stats/6-4b_perturb"] = rd("6-4b_perturb",
        "네트워크, ROI 입력 교란으로 A-1과 C-1의 성능이 얼마나 떨어지는지, 그리고 두 모델의 하락폭 차이(C-1 − A-1)의 표다.",
        """01 6-4b와 ROI판(질문 2-4). s9_saved_model_tests/6-4b_perturb의 영상별 예측을 읽는다.
- 하락 = 원래 r − 교란 r. 20회 배정의 평균
- [사전] 13묶음의 하락폭 차이에 Holm(5명 평균, 참가자마다 따로)
- 나머지(ROI 370개, 묶음 안 정서별, 각 모델의 하락)는 탐색이고 BH
ex) network_drops.tsv의 Visual2, mean5 행에 A-1 하락, C-1 하락, 그 차이와 구간이 있다.""",
        "참가자와 5명 평균마다 묶음별, ROI별, 정서별 하락과 구간, p.",
        """6-4b_perturb/
├── README.md
└── s6_brain_final/                     읽은 S6 결과 폴더 이름
    ├── network_drops.tsv               묶음 13개 × 참가자(5명 평균 포함)의 A-1 하락, C-1 하락, 차이, 구간, p, Holm, BH
    ├── network_confirmed.tsv           묶음마다 Holm 뒤에 우연이 아닌 참가자 수와 방향
    ├── network_drops_per_emotion.tsv   묶음 안 정서별 하락과 차이(탐색, BH)
    ├── roi_drops.tsv                   ROI 370개의 하락과 차이(탐색, BH)
    ├── arrays.npz                      재표집 배열
    ├── coverage.tsv                    fold마다 읽은 파일, 행 수, 단위 수, 반복 수
    └── run_info.json                   보정 묶음, 재표집 설정, 코드 커밋""",
        "src/s10_perturb.py (scripts/s10_perturb.sh)")
    out["s10_stats/K1_path_eval"] = rd("K1_path_eval",
        "경로 평가(K1)와 14개 정서 차원 표(K1a, B4)다.",
        """01 K1, K1a, B4. s9_saved_model_tests/K1_path_eval의 예측을 읽는다.
- K1: A-1과 경로 평가(ridge판, C-1판 × head 둘 × 보정 전과 보정판)의 정서별 r, 참가자 점수, 경로 평가 − A-1의 차이와 구간. p와 비율은 내지 않는다
- 14개 차원 표: (1) B4 ridge, (2) 실제 feature를 넣은 Stimulus Model, (3) decoded features를 넣은 Stimulus Model과 (3) − (1)""",
        "정서별, 차원별 r과 차이, 구간.",
        """K1_path_eval/
├── README.md
└── s6_brain_final/
    ├── k1_scores.tsv                   판마다 참가자 점수
    ├── k1_per_emotion.tsv              판마다 정서별 r
    ├── k1_differences.tsv              경로 평가 − A-1의 점수 차이와 구간
    ├── k1_differences_per_emotion.tsv  정서별 차이
    ├── k1_seed_summary.tsv             seed 평균과 표준편차
    ├── dimensions14.tsv                14개 차원 표((1), (2), (3), (3) − (1))
    ├── dimensions14_seed_summary.tsv
    ├── n8_shift_only.tsv               N8 보정에서 평균만 옮긴 차원
    ├── coverage.tsv
    └── run_info.json""",
        "src/s10_k1.py (scripts/s10_k1.sh)")
    out["s10_stats/ablation_sensitivity"] = rd("ablation_sensitivity",
        "서로 다른 S6 결과 폴더에 있는 두 모델을 같은 시험 영상에서 비교한 표다. 모델 한 부분만 바꾼 판(ablation)과 본 설계를 비교한다.",
        """01 F7(ROI token 평균판 대 emotion query판), F3(encoder block 수). 지금 든 비교 세 개:
- A-1 ROI token 평균판 − A-1
- C-1 ROI token 평균판 − C-1
- A-1 block 2개 − A-1 block 1개
정서별 차이는 탐색이고 BH다. [사전] 15개 Holm에 넣지 않는다. block 4개 판이 생기면 다시 계산한다.""",
        "비교마다 참가자와 5명 평균의 정서별 r, 차이, 구간, p.",
        """ablation_sensitivity/
├── README.md
├── per_emotion.tsv     비교, 참가자(5명 평균 포함), 정서마다 두 모델의 r, 차이, 구간, p, BH
├── scores.tsv          비교, 참가자마다 34개 정서 평균 점수의 차이와 구간
└── run_info.json       비교한 두 폴더와 조건, 재표집 설정""",
        "src/s10_sensitivity.py (scripts/s10_sensitivity.sh)")
    return out


def s6_view_readmes(status):
    out = {}
    nets = networks()
    out["s6_brain_model"] = rd("s6_brain_model (뇌 모델 결과를 조건 기준으로 보는 폴더)",
        "s6 뇌 모델 학습 결과를 조건 이름으로 찾을 수 있게 만든 폴더다. 안의 fold 폴더는 실제 학습 결과 폴더로 가는 링크라서 용량을 차지하지 않는다.",
        """학습을 종류에 따라 넷으로 나눠 표시했다.
- main/: 주 비교. A~E 조건을 바깥 fold 6개에서 모두 학습한 것(2-3의 성능 표)
- control/: 학습 정답이나 feature 짝을 섞은 대조군
- ablation/: 모델 한 부분만 바꾼 판. ex) 곱하는 항을 뺀 C-1, emotion query 대신 ROI token 평균, block 2개
- analysis/: 질문 하나에 답하려고 A-1과 C-1을 다른 학습 자료로 다시 학습한 것. ex) 내용 묶음 하나를 학습에서 뺌(6-2), 네트워크 하나의 입력만 씀(6-4a), 개발 영상 전체로 학습(6-3)
ex) 주 비교의 A-1 결과는 main/A-1_brain_only/fold1~fold6에, 6-2 때문에 따로 학습한 A-1은 analysis/6-2_unseen_content/A-1_brain_only/에 있다.""",
        """실제 파일은 레포 코드가 쓰는 원본 폴더에 있다(지금은 결과 폴더 맨 위의 s6_brain_* 폴더). s6 코드는 fold 폴더 안에 조건 폴더를 쓰고, 같은 fold의 조건들이 plan/을 같이 쓰기 때문에 원본은 fold 기준이다. 학습이 모두 끝나면 원본을 여기 raw_runs_by_fold/ 아래로 옮긴다.

원본 폴더 하나의 꼴(ex) s6_brain_grid_main/)""",
        """s6_brain_model/
├── README.md
├── main/            주 비교
├── control/         대조군
├── ablation/        모델 한 부분만 바꾼 판
└── analysis/        질문 하나를 위해 다시 학습한 것

원본 폴더(s6_brain_grid_main/ 등)의 꼴
<원본 폴더>/
└── outer_fold<k>/              바깥 fold k가 시험, 다음 fold가 검증, 나머지 4개가 학습
""" + "\n".join("    " + x for x in PLAN_TREE.splitlines()) + "\n    └── <조건 코드 이름>/        ex) brain_only, brain_decoded. 안쪽은 아래 " + FEATURE_NOTE + "\n" + cand_tree("feature", "        "),
        "src/s6_train.py, src/s6_model.py, src/s6_common.py. 링크와 README는 scripts/output_layout.py",
        MERGED_NOTE)
    out["s6_brain_model/main"] = rd("main (주 비교)",
        "A~E 조건을 바깥 fold 6개에서 모두 학습한 결과다. 2-3 성능 표가 이것을 읽는다.",
        """조건은 장면 정보를 쓰는 정도로 나뉜다.
- A: 장면 정보를 쓰지 않음(A-1, A-2)
- B: feature를 학습 신호로만(B-1)
- C: decoded feature를 정서 계산에, 공유 encoder(C-1, C-2)
- D: 장면 특징으로만 학습해 고정한 Encoder2(D-1~D-4, D-3 짝)
- E: Multimodal Model의 중간 표현 전달(E-고정, E-학습)
- prep: 다른 조건이 가져다 쓰는 준비 모델(Encoder2, fold 하나를 뺀 Encoder2 4개, Multimodal Model)
폴더 이름은 <표시 이름>_<코드 이름>이다. ex) C-1_brain_decoded""",
        "조건마다 fold1~fold6 링크. 조건 폴더마다 README가 있다. D와 E는 learning rate 두 실행을 합친 뒤에 링크가 생긴다.",
        "main/\n├── README.md\n" + "\n".join(f"├── {n}/" for n, *_ in MAIN + PREP[:-1]) + f"\n└── {PREP[-1][0]}/",
        "src/s6_train.py")
    out["s6_brain_model/control"] = rd("control (대조군)",
        "학습 정답이나 feature 짝을 섞어, 조건의 이득이 그 내용 때문인지 확인하는 대조군이다. 주 비교와 같은 실행에서 같이 학습했다.",
        "\n".join(f"- {n}: {d}. {w}" for n, _, d, w, *_ in CONTROL),
        "대조군마다 fold1~fold6 링크.",
        "control/\n├── README.md\n" + "\n".join(f"├── {n}/" for n, *_ in CONTROL[:-1]) + f"\n└── {CONTROL[-1][0]}/",
        "src/s6_train.py")
    out["s6_brain_model/ablation"] = rd("ablation (모델 한 부분만 바꾼 판)",
        "본 설계에서 한 부분만 빼거나 바꾼 모델이다. 학습 자료는 주 비교와 같다.",
        "\n".join(f"- {n}: {d}. {w}" for n, _, _, d, w, *_ in ABLATION) + "\n\nC-1 더하기 head는 1-2의 본문 분석이다. 나머지는 보조(SI)로 보고하고 본 설계를 바꾸지 않는다.",
        "판마다 fold1~fold6 링크. 손실 흐름 허용판과 ROI token 평균판은 learning rate 두 실행을 합친 뒤에 링크가 생긴다.",
        "ablation/\n├── README.md\n" + "\n".join(f"├── {n}/" for n, *_ in ABLATION[:-1]) + f"\n└── {ABLATION[-1][0]}/",
        "src/s6_train.py, src/s6_model.py")
    out["s6_brain_model/analysis"] = rd("analysis (질문 하나를 위해 다시 학습한 것)",
        "모델은 주 비교의 A-1, C-1과 같고, 학습 자료만 질문에 맞게 바꿔 다시 학습한 것이다. ablation이 아니다(모델의 부분을 바꾸지 않는다).",
        """- 6-2_unseen_content/: 내용 묶음 하나를 학습에서 통째로 빼고 그 묶음 영상으로 시험(처음 보는 장면, 질문 1-4, 2-3). [사전] 검정이다
- 6-4a_single_network/: 네트워크 묶음 하나의 ROI 입력만으로 학습(질문 1-3). [사전] 검정 3개(Visual1, Visual2, Default)가 있다
- 6-3_model_for_mc/: 개발 영상 전체로 학습한 모델. S8이 이 모델을 고정하고 MC 참가자의 입력층만 학습한다(질문 2-3의 다른 참가자 전이)""",
        "아래 폴더마다 README가 있다.",
        "analysis/\n├── README.md\n├── 6-2_unseen_content/\n├── 6-4a_single_network/\n└── 6-3_model_for_mc/",
        "src/s6_train.py(분할 이름 zone_block<b>_fold<k>_<방식>, outer_fold<k> + roi_group, final_for_mc)")
    z = [status.get(f"analysis/6-2_unseen_content/{n}", (0, 60)) for n, *_ in ZONE_CONDS]
    out["s6_brain_model/analysis/6-2_unseen_content"] = rd("6-2_unseen_content (처음 보는 장면)",
        "내용 묶음 하나를 학습에서 통째로 빼고 학습한 A-1, C-1이다.",
        """01 6-2, 4-3(질문 1-4, 2-3).
1. 영상마다 붙은 이름표 73개의 비율로, 내용이 비슷한 영상끼리 5개 내용 묶음으로 나눴다(k-means, S2 content_blocks_assignment.tsv)
2. held_out: 묶음 b의 영상을 학습과 검증에서 모두 빼고 학습한다. 시험은 바깥 fold k의 영상 가운데 묶음 b에 든 영상이다
3. random_same_size: 학습, 검증 영상 수를 held_out과 똑같이 맞추되 묶음과 상관없이 무작위로 뽑는다(S2 content_block_control_samples.tsv). 시험 영상은 held_out과 같다
4. 두 성능의 차이가 "처음 보는 내용이라서" 떨어진 양이다. 학습 영상이 줄어서 떨어진 양은 random_same_size가 함께 겪는다
ex) content3_fold2_held_out은 묶음 3을 빼고 학습해, fold 2 영상 가운데 묶음 3에 든 영상으로 시험한 결과다.
묶음은 이름표로 정의한 내용 묶음이라 "처음 보는 장면 종류"가 아니라 "이름표로 정의한 내용 묶음을 학습에서 뺀 평가"라고 쓴다.""",
        f"내용 묶음 5개 × 바깥 fold 6개 × 두 방식 = 60개 분할, 분할마다 A-1과 C-1. 지금 링크 A-1 {z[0][0]}/60, C-1 {z[1][0]}/60. 링크는 학습 폴더가 생기면 붙으므로, 학습이 끝났는지는 링크 안에 selected.json이 있는지로 본다.",
        """6-2_unseen_content/
├── README.md
├── A-1_brain_only/
│   ├── README.md
│   ├── content<b>_fold<k>_held_out/          → s6_brain_zone/zone_block<b>_fold<k>_excluded/brain_only
│   └── content<b>_fold<k>_random_same_size/  → s6_brain_zone/zone_block<b>_fold<k>_control/brain_only
└── C-1_brain_decoded/                        같은 구조(brain_decoded)

링크 하나의 안쪽(조건 폴더)
""" + FEATURE_NOTE + "\n" + cand_tree("feature") + "\n\n분할마다의 plan/은 원본 s6_brain_zone/zone_block<b>_fold<k>_<방식>/plan/에 있다\n" + PLAN_TREE,
        "src/s6_train.py(분할 zone_block<b>_fold<k>_excluded, _control), src/s4_common.zone_sets(분할 규칙). 학습 목록 logs/s6_queue_jobs_hk_rest.tsv")
    for n, code, disp in ZONE_CONDS:
        made = status.get(f"analysis/6-2_unseen_content/{n}", (0, 60))[0]
        out[f"s6_brain_model/analysis/6-2_unseen_content/{n}"] = rd(f"{n} (6-2)",
            f"6-2 처음 보는 장면 분석의 {disp}다.",
            "상위 폴더 README(6-2_unseen_content/README.md)를 본다.",
            f"60개 분할의 {disp} 학습 결과 링크. 지금 {made}/60. 링크 안에 selected.json이 있어야 그 분할의 학습이 끝난 것이다.",
            f"{n}/\n├── README.md\n├── content1_fold1_held_out/\n├── content1_fold1_random_same_size/\n└── … content5_fold6_random_same_size/\n\n링크 하나의 안쪽\n" + cand_tree("feature" if code == "brain_decoded" else "plain"),
            "src/s6_train.py")
    out["s6_brain_model/analysis/6-4a_single_network"] = rd("6-4a_single_network (네트워크 하나의 입력만으로 학습)",
        "CAB-NP 13개 네트워크 묶음마다 그 묶음의 ROI 입력만으로 A-1과 C-1을 다시 학습한 결과다.",
        """01 6-4a, 1-3(그 연결의 정보는 어느 뇌 영역에 있는가). 바깥 fold 6개, 설정 선택은 주 비교와 같은 규칙이다.
[사전] 검정은 Visual1, Visual2, Default 세 묶음이고 나머지는 탐색이다.
ex) Visual1/A-1_brain_only/fold3은 1차 시각 묶음 ROI 6개의 입력만으로 학습한 A-1을 fold 3 영상으로 시험한 것이다.
결과는 "그 묶음의 신호만으로 예측할 수 있었다"까지를 보여 준다. 학습된 모델이 그 묶음에 기대는 정도는 6-4b(입력 교란)가 따로 본다.""",
        "묶음 13개 × 조건 2개 × fold 6개 링크. 묶음 폴더마다 README가 있다.",
        "6-4a_single_network/\n├── README.md\n" + "\n".join(f"├── {g}/{' ' * max(1, 22 - len(g))}{ko}, ROI {r}개" for g, ko, r in nets[:-1]) + f"\n└── {nets[-1][0]}/{' ' * max(1, 22 - len(nets[-1][0]))}{nets[-1][1]}, ROI {nets[-1][2]}개\n    ├── README.md\n    ├── A-1_brain_only/fold1/ … fold6/\n    └── C-1_brain_decoded/fold1/ … fold6/",
        "src/s6_train.py(설정 roi_group), 설정 configs/s6/run_config_net_<묶음>.json, 묶음 표 manifests/s2/cabnp_groups.tsv")
    for g, ko, r in nets:
        a = status.get(f"analysis/6-4a_single_network/{g}/A-1_brain_only", (0, 6))[0]
        c = status.get(f"analysis/6-4a_single_network/{g}/C-1_brain_decoded", (0, 6))[0]
        out[f"s6_brain_model/analysis/6-4a_single_network/{g}"] = rd(f"{g} (6-4a)",
            f"{ko} 묶음(ROI {r}개)의 입력만으로 학습한 A-1, C-1이다.",
            "상위 폴더 README(6-4a_single_network/README.md)를 본다." + (" [사전] 검정 묶음이다." if g in ("Visual1", "Visual2", "Default") else " 탐색 묶음이다."),
            f"A-1 링크 {a}/6, C-1 링크 {c}/6. 링크는 s6_brain_net_{g}/outer_fold<k>/<조건 코드 이름>으로 간다. plan/은 원본 쪽에 있다.",
            f"{g}/\n├── README.md\n├── A-1_brain_only/\n│   └── fold<k>/     안쪽은 아래\n└── C-1_brain_decoded/\n    └── fold<k>/\n\nfold 링크 하나의 안쪽 " + FEATURE_NOTE + "\n" + cand_tree("feature"),
            f"src/s6_train.py, 설정 configs/s6/run_config_net_{g}.json")
    out["s6_brain_model/analysis/6-3_model_for_mc"] = rd("6-3_model_for_mc (MC 전이용 모델)",
        "개발 영상 전체로 학습한 A-1, C-1이다. 시험 fold가 없다.",
        """01 6-3, O7. fold 1을 검증, 나머지 fold 5개를 학습으로 쓴다. S8은 이 모델의 공유 가중치(encoder, query, feature head, emotion head)를 모두 고정하고, MindCaptioning 참가자 6명마다 ROI 입력층만 새로 학습해 MC 시험 영상 72개로 채점한다.
ex) MC 참가자 mc-01의 뇌는 HK와 voxel 배치가 달라서 입력층만 새로 맞추고, 나머지 계산은 HK에서 배운 그대로 쓴다.""",
        "A-1_brain_only, C-1_brain_decoded가 각각 학습 결과 폴더로 가는 링크다. 시험이 없어 test_pred.npz와 outputs/의 시험 파일이 없다.",
        "6-3_model_for_mc/\n├── README.md\n├── A-1_brain_only     → s6_brain_final_for_mc/final_for_mc/brain_only\n└── C-1_brain_decoded  → s6_brain_final_for_mc/final_for_mc/brain_decoded\n\n링크 하나의 안쪽 " + FEATURE_NOTE + " 시험이 없어 test_pred.npz와 시험 파일은 없다\n" + cand_tree("feature") + "\n\nplan/은 s6_brain_final_for_mc/final_for_mc/plan/에 있다",
        "src/s6_train.py(분할 final_for_mc), 설정 configs/s6/run_config_final_for_mc.json. S8은 src/s8_mc_transfer.py")
    for name, code, disp, io, desc, q, kind in MAIN:
        out[f"s6_brain_model/main/{name}"] = cond_readme(name, code, disp, io, desc, q, kind, f"s6_brain_final/outer_fold<k>/{code} (learning rate 1e-3 실행과 1e-4 실행 가운데 검증 r이 높은 쪽)", status.get(f"main/{name}", (0, 6)))
    for name, code, disp, desc, kind in PREP:
        out[f"s6_brain_model/main/{name}"] = cond_readme(name, code, disp, "준비 모델", desc, "01 5-A", kind, f"lr1e-3/은 s6_brain_grid_main/outer_fold<k>/{code}, lr1e-4/는 s6_brain_grid_lr4/outer_fold<k>/{code}", status.get(f"main/{name}", (0, 12)))
    for name, code, disp, desc, q, kind in CONTROL:
        out[f"s6_brain_model/control/{name}"] = cond_readme(name, code, disp, "대조군", desc, q, kind, f"s6_brain_final/outer_fold<k>/{code}", status.get(f"control/{name}", (0, 6)))
    for name, code, raw, disp, desc, q, kind in ABLATION:
        out[f"s6_brain_model/ablation/{name}"] = cond_readme(name, code, disp, "모델 한 부분만 바꾼 판", desc, q, kind, f"{raw}/outer_fold<k>/{code}", status.get(f"ablation/{name}", (0, 6)))
    return out


def raw_s6(title, summary, what, top_tree, code, extra=""):
    tree = top_tree.rstrip("\n") + "\n\n조건 폴더 하나의 안쪽 " + FEATURE_NOTE + "\n<조건 코드 이름>/\n" + cand_tree("feature") + "\n\nplan/\n" + "\n".join(PLAN_TREE.splitlines()[1:])
    return rd(title, summary, what,
              "사람이 볼 때는 s6_brain_model/의 같은 이름 폴더(링크)부터 연다. 이 폴더는 코드가 쓰는 원본이라 안쪽 조건 폴더와 fold 폴더에는 README를 두지 않는다(코드가 그 폴더의 목록을 읽는다). 학습이 모두 끝나면 s6_brain_model/raw_runs_by_fold/ 아래로 옮긴다.",
              tree, code, extra)


def raw_readmes():
    out = {}
    nets = networks()
    codes = "plan/, brain_only(A-1), brain_only_distill(A-2), brain_only_featdec(B-1), brain_decoded(C-1), brain_decoded_distill(C-2), brain_decoded_additive(C-1 더하기 head), brain_decoded_grad(C-1 손실 흐름 허용판), brain_only_pool, brain_decoded_pool(ROI token 평균판), brain_decoded_sep(D-1), brain_decoded_sep_distill(D-2), brain_features_only(D-3), brain_features_only_paired(D-3 짝), brain_frozen_feature_encoder(D-4), brain_only_repr_frozen(E-고정), brain_only_repr_trained(E-학습), control_label_smoothing, control_stimulus_shuffle, control_feature_shuffle(대조군), feature_encoder(Encoder2), feature_encoder_oof(fold 하나를 뺀 Encoder2 4개), multimodal(Multimodal Model)"
    run_tree = lambda name: f"{name}/\n├── README.md\n└── outer_fold<k>/      k = 1~6. 바깥 fold k가 시험\n    ├── plan/\n    └── <조건 코드 이름>/  학습한 조건마다 하나. 지금 학습 중인 조건은 selected.json이 아직 없다\n\n조건 코드 이름: " + codes
    out["s6_brain_grid_main"] = raw_s6("s6_brain_grid_main (S6 원본, learning rate 1e-3 실행)",
        "주 비교의 첫 실행이다(11/13~). A-1은 learning rate {1e-5, 1e-4, 1e-3} × 입력층 weight decay 후보에서 검증 r로 고르고, 다른 조건은 그 fold의 A-1이 고른 값을 따른다. 대조군, ablation 판, D, E도 이 실행에 함께 있다.",
        "01 5-A, 5-5, 2-3. 설정 configs/s6/run_config_grid_main.json(ROI token 평균판은 run_config_grid_main_pool.json).",
        run_tree("s6_brain_grid_main"), "src/s6_train.py. 작업 목록 logs/s6_queue_jobs_*.tsv, 띄운 기록 logs/s6_queue_<tag>/")
    out["s6_brain_grid_lr4"] = raw_s6("s6_brain_grid_lr4 (S6 원본, learning rate 1e-4 실행)",
        "A-1 밖 조건을 learning rate 1e-4로 다시 학습한 실행이다(11/14~). 1e-3 실행과 조건, fold마다 검증 r로 합친다(s6_brain_final).",
        "01 5-5(조건마다 learning rate {1e-4, 1e-3}, 11/14). 설정 configs/s6/run_config_grid_lr4.json(ROI token 평균판은 run_config_grid_lr4_pool.json).",
        run_tree("s6_brain_grid_lr4"), "src/s6_train.py")
    out["s6_brain_final"] = raw_s6("s6_brain_final (S6 원본, 두 실행을 합친 폴더)",
        "learning rate 1e-3 실행과 1e-4 실행을 조건, fold마다 검증 r이 높은 쪽으로 합친 폴더다. 원래 결과는 옮기지 않고 링크와 selected.json만 만든다. S9과 S10이 이 폴더를 읽는다.",
        "01 5-5. C-2는 합친 C-1의 실행을, D-2는 합친 D-1의 실행을 따른다. 한 실행에만 결과가 있는 조건은 합치지 않고 merge_record.tsv에 missing으로 남긴다. D와 E는 학습이 끝나면 합친다.",
        "s6_brain_final/\n├── README.md\n├── merge_record.tsv     fold, 조건마다 두 실행의 검증 r, learning rate, 고른 쪽, 고른 후보\n└── outer_fold<k>/\n    ├── plan             → 1e-3 실행의 plan\n    └── <조건 코드 이름>   링크, 또는 selected.json + 고른 후보 폴더 링크",
        "scripts/s6_merge_lr.py (scripts/s6_merge_lr.sh)", MERGED_NOTE)
    out["s6_brain_zone"] = raw_s6("s6_brain_zone (S6 원본, 6-2 처음 보는 장면)",
        "내용 묶음 하나를 학습에서 뺀 분할과 같은 수를 무작위로 뺀 분할에서 A-1, C-1을 학습한 원본이다.",
        "01 6-2. 설명은 s6_brain_model/analysis/6-2_unseen_content/README.md. 설정 configs/s6/run_config_zone.json.",
        "s6_brain_zone/\n├── README.md\n└── zone_block<b>_fold<k>_<방식>/   b = 내용 묶음 1~5, k = 바깥 fold 1~6, 방식 = excluded(묶음을 뺌) 또는 control(같은 수를 무작위로 뺌)\n    ├── plan/\n    ├── brain_only/      A-1\n    └── brain_decoded/   C-1",
        "src/s6_train.py. 작업 목록 logs/s6_queue_jobs_hk_rest.tsv")
    for g, ko, r in nets:
        out[f"s6_brain_net_{g}"] = raw_s6(f"s6_brain_net_{g} (S6 원본, 6-4a)",
            f"{ko} 묶음(ROI {r}개)의 입력만으로 A-1, C-1을 학습한 원본이다.",
            "01 6-4a, 1-3. 설명은 s6_brain_model/analysis/6-4a_single_network/README.md.",
            f"s6_brain_net_{g}/\n├── README.md\n└── outer_fold<k>/\n    ├── plan/\n    ├── brain_only/      A-1\n    └── brain_decoded/   C-1",
            f"src/s6_train.py, 설정 configs/s6/run_config_net_{g}.json")
    out["s6_brain_final_for_mc"] = raw_s6("s6_brain_final_for_mc (S6 원본, 6-3 MC 전이용 모델)",
        "개발 영상 전체로 학습한 A-1, C-1의 원본이다. 시험 fold가 없다. 학습이 끝나면 logs/s8_mc_chain.sh가 MC 전이(S8)를 자동으로 띄운다.",
        "01 6-3, O7. 설명은 s6_brain_model/analysis/6-3_model_for_mc/README.md. 설정 configs/s6/run_config_final_for_mc.json.",
        "s6_brain_final_for_mc/\n├── README.md\n└── final_for_mc/\n    ├── plan/\n    ├── brain_only/      A-1\n    └── brain_decoded/   C-1",
        "src/s6_train.py")
    out["s6_brain_depth2"] = raw_s6("s6_brain_depth2 (S6 원본, encoder block 2개)",
        "encoder self-attention block을 2개로 둔 A-1의 원본이다. 후보는 하나다.",
        "01 F3 민감도(11/15). 설정 configs/s6/run_config_depth2.json. 설명은 s6_brain_model/ablation/A-1_encoder_2_blocks/README.md.",
        "s6_brain_depth2/\n├── README.md\n└── outer_fold<k>/\n    ├── plan/\n    └── brain_only/      A-1(block 2개)",
        "src/s6_train.py. 작업 목록 logs/s6_queue_jobs_depth2.tsv")
    out["s1_original_rois"] = rd("s1_original_rois (S1)",
        "저자가 공개한 참가자별 ROI를 우리 T1w 2 mm 격자로 옮긴 결과다.",
        "04 S1. ROI 지도를 정하기 전에 참가자별, ROI별 voxel 수를 원 논문 값과 대조하려고 만들었다. hk는 Horikawa 2020 참가자 5명, mc는 MindCaptioning 참가자 6명이다.",
        "참가자마다 격자 정보, ROI별 voxel 표시, ROI별 voxel 수.",
        "s1_original_rois/\n├── README.md\n├── DONE                      끝 표시\n├── <자료>_sub-XX_grid.tsv    격자(원점, 크기) 정보\n├── <자료>_sub-XX_rois.npz    ROI마다 어느 voxel이 드는지\n└── <자료>_sub-XX_voxels.tsv  ROI마다 voxel 수(원래 수와 우리 QC mask 안의 수)",
        "src/s1_original_rois.py (scripts/s1_original_rois.sh). 작은 표는 레포 manifests/s1/")
    out["s1_subcortex_rebuild"] = rd("s1_subcortex_rebuild (S1)",
        "피질하 ROI 10개를 PickAtlas 표준 mask에서 참가자 11명 모두 새로 만든 결과다.",
        "04 S1, 01 ROI 지도 결정(11/4). 저자 공개 피질하 mask와 FreeSurfer aseg를 해부학적 위치로만 비교했다. 뇌 반응과 정서 점수는 읽지 않는다.",
        "참가자마다 표준 공간과 개인 T1w 사이의 정합 결과, 새 mask, 비교 표.",
        "s1_subcortex_rebuild/\n├── README.md\n├── DONE\n├── <자료>_sub-XX_0GenericAffine.mat   표준 공간 → 개인 T1w 선형 정합\n├── <자료>_sub-XX_1Warp.nii.gz         비선형 정합\n├── <자료>_sub-XX_1InverseWarp.nii.gz  그 역변환\n├── <자료>_sub-XX_registration.log     정합 기록\n├── <자료>_sub-XX_new_masks.npz        새 피질하 mask 10개\n├── <자료>_sub-XX_check.tsv            공개 mask, aseg와의 겹침\n└── <자료>_sub-XX_size.tsv             mask 크기 비교",
        "src/s1_subcortex_rebuild.py, src/s1_subcortex_size_check.py")
    out["s2_manifest"] = rd("s2_manifest (S2, 학습이 읽는 중)",
        "참가자마다 ROI 370개의 voxel 값 배열이다. 뇌 모델과 ridge가 이것을 읽는다. 지금 학습이 읽고 있어 옮기거나 고치지 않는다.",
        "04 S2. 분할, 내용 묶음, 짝, ROI 표 같은 작은 표는 레포 manifests/s2/에 있고, 여기에는 큰 배열만 있다.",
        "- roi_voxels/: 참가자마다 개발 block × (ROI 370개의 voxel을 이어 붙인 열). 한 voxel이 여러 ROI에 들면 ROI마다 한 번씩 들어간다\n- roi_means/: ROI마다 voxel 평균(입력층 점검용)\n- roi_cells/: ROI마다 8칸 번호(입력층 점검용)",
        "s2_manifest/\n├── README.md\n├── roi_voxels/\n│   ├── hk_sub-0X.npz         HK 5명\n│   ├── mc_sub-0X.npz         MC 6명\n│   ├── parts/                참가자별 조각\n│   └── spec_*.json           만든 설정\n├── roi_means/\n│   └── hk_sub-0X_roi370_runz.npy\n└── roi_cells/\n    └── hk_sub-0X.npz",
        "src/s2_manifest.py, src/s2_roi_cells.py")
    out["s3_features"] = rd("s3_features (S3, 학습이 읽는 중)",
        "영상과 캡션에서 뽑은 feature다. 학습은 없다. 뇌 모델이 맞히는 목표(target.npy)가 여기 있어 지금 옮기거나 고치지 않는다.",
        "04 S3, 01 3-1~3-6.\n- 주: vjepa2(Vision feature, V-JEPA 2 block 10, 20, 30, 40의 평균), deberta(Caption feature, DeBERTa-large 층 6, 12, 18, 24)\n- 비교용: videomae, timesformer, clip, mpnet, deberta_no_emotion_words(정서어를 지운 캡션)\n- lowlevel: 움직임 에너지와 RGB 중앙값(저수준 시각 특징)",
        "모델마다 영상별 feature와 추출 기록.",
        "s3_features/\n├── README.md\n├── vjepa2/\n│   ├── target.npy            뇌 모델이 맞히는 Vision feature(영상 × 5,632)\n│   ├── blocks.npy            block별 feature(S5 층별 decoding이 씀)\n│   ├── windows_per_video.npz 영상마다 window 수\n│   ├── video_info.tsv        영상 정보\n│   ├── manifest.json         추출 기록(코드, 설정, 해시)\n│   ├── spec_*.json           추출 설정\n│   └── parts/                영상별 조각\n├── deberta/\n│   ├── target.npy            뇌 모델이 맞히는 Caption feature(영상 × 4,096)\n│   ├── video_mean.npy        캡션 20개 평균\n│   ├── per_caption.npy       캡션별 feature\n│   ├── per_caption_video_id.tsv\n│   └── manifest.json\n├── lowlevel/\n│   ├── lowlevel.npy          움직임 에너지 + RGB 중앙값\n│   ├── motion_energy.npy\n│   ├── rgb_median.npy\n│   └── manifest.json, spec_*.json, video_info.tsv, parts/\n└── videomae/, timesformer/, clip/, mpnet/, deberta_no_emotion_words/   같은 꼴",
        "src/s3_vision.py, src/s3_text.py, src/s3_lowlevel.py, src/s3_collect.py")
    out["s3_timing"] = rd("s3_timing (S3)",
        "feature 추출 전 모델마다 GPU 시간과 메모리를 확인한 기록이다.",
        "04 S3. 추출 작업을 나눌 크기를 정하려고 몇 개 영상으로 먼저 돌렸다.",
        "모델마다 시험 추출 조각과 GPU 메모리 표.",
        "s3_timing/\n├── README.md\n├── gpu_memory.csv            모델마다 GPU 메모리\n└── vjepa2/, videomae/, timesformer/, clip/\n    ├── parts/                시험 추출 조각\n    └── spec_*.json",
        "scripts/s3_timing.sh")
    out["s4_no_brain"] = rd("s4_no_brain (S4, 학습이 읽는 중)",
        "뇌를 쓰지 않는 모델의 결과다. distillation 조건(A-2, C-2, D-2)이 섞는 Stimulus Model 예측 평정(stimulus/fold<k>/oof.npz)을 지금 학습이 읽고 있어 옮기거나 고치지 않는다.",
        "04 S4, 01 E1~E6, K1, D12, 3-2.\n- stimulus/: Stimulus Model. 실제 Vision feature + Caption feature → 정서 34개\n- k1a/: 같은 꼴로 14개 정서 차원을 맞히는 판(K1a)\n- ridge_d12/: V-JEPA 2 block 40개 각각으로 캡션 목표와 저수준 특징을 맞히는 ridge(D12)\n- window_change/: 긴 영상의 window 사이 변화(3-2)\n- superseded/: 예비 실행이 쓴 옛 Stimulus 실행",
        "fold마다 Stimulus Model과 그 예측.",
        "s4_no_brain/\n├── README.md\n├── stimulus/\n│   └── fold<k>/              바깥 fold k (k = 1~6)\n│       ├── oof.npz           학습 영상의 fold 밖 예측 평정(distillation 정답에 섞음)\n│       ├── test_pred.npz     시험 영상 예측\n│       ├── head_additive.pt  더하기 head(K1이 씀)\n│       ├── head_interaction.pt 상호작용 head(K1이 씀)\n│       ├── chosen.json       고른 설정\n│       ├── selection_dk.tsv, selection_oof.tsv   후보마다 점수\n│       ├── curves_dk.npy, curves_oof.npy         학습 곡선\n│       ├── coordinates.npz   표준화 통계\n│       └── done.json\n├── k1a/fold<k>/              stimulus와 같은 꼴(oof 없음)\n├── ridge_d12/\n│   ├── d12.tsv, d12_r2_per_dimension.npz, done.json\n│   └── predictions/\n├── window_change/\n│   └── window_change.tsv, window_change_summary.tsv, done.json\n└── superseded/lr_1e-2_20261108/",
        "src/s4_feature_model.py, src/s4_ridge.py, src/s4_window_change.py")
    out["s4_no_brain_lr"] = rd("s4_no_brain_lr (S4, 쓰지 않음)",
        "Stimulus Model을 learning rate 후보 {1e-4, 1e-3, 1e-2}로 다시 학습한 판이다(11/14). 지금 학습에 쓰는 s4_no_brain/stimulus로 갈아끼우지 않았다.",
        "04 기록 11/14. 6 fold 모두 learning rate 후보 끝값을 골라 범위를 넓혀 다시 봤다. 갈아끼우면 그 예측을 쓰는 A-2, C-2, Stimulus 예측 섞기 대조군을 다시 학습해야 해서 그대로 두었다.",
        "fold마다 Stimulus Model(s4_no_brain/stimulus와 같은 꼴).",
        "s4_no_brain_lr/\n├── README.md\n└── stimulus/fold<k>/   s4_no_brain/stimulus/fold<k>와 같은 파일",
        "src/s4_feature_model.py --learning-rates")
    out["s5_ridge"] = rd("s5_ridge (S5)",
        "뇌 반응을 ridge 등 단순한 모델로 읽은 결과와, 비교에 쓰는 기준선, 외부 모델이다. A~E 뇌 모델 조건이 아니다.",
        "04 S5, 01 2-1, I7, O27, 6-4.\n- decoding/: 뇌 → Vision feature, Caption feature ridge(층별). 2-1과 K1의 ridge판이 쓴다\n- ridge/: 뇌 → 정서 34개와 14개 차원 ridge(정서 기준선)\n- mlp/: 같은 입력의 MLP 기준선\n- signal/: 뇌 전체 평균과 block 신호 크기 기준선\n- video/: 뇌를 쓰지 않는 기준선. 영상 길이(length_fold<k>), 저수준 시각 특징(lowlevel_fold<k>)\n- ged/, mlbvae/, emogrowth/: 같은 Horikawa 2020 자료의 외부 모델을 우리 과제로 학습한 판\n- roi_map/, roi_map_summary/: ROI 370개마다 그 ROI voxel만으로 정서, Vision feature, Caption feature를 ridge로 맞힌 ROI 지도\n- emotion_voxel_clusters/: 정서 반응으로 voxel을 군집으로 묶고 ROI, 네트워크 경계와 겹치는 정도를 본 일회성 탐색 계산(11/13). 레포 코드가 없고 논문에 쓰지 않는다. 2단계에 checks/로 옮긴다",
        "참가자, fold마다 예측과 선택 기록.",
        "s5_ridge/\n├── README.md\n├── decoding/sub-0X_fold<k>/\n│   ├── test_pred.npz         층마다 시험 예측(원래 척도)\n│   ├── inner_oof_target.npz  주 목표 층의 안쪽 fold 밖 예측(N8 보정 통계)\n│   ├── chosen.tsv            층마다 고른 λ\n│   ├── curves.npz            λ 곡선\n│   └── done.json\n├── ridge/sub-0X_fold<k>/      pred.npz(예측), done.json\n├── mlp/, ged/, mlbvae/, emogrowth/   sub-0X_fold<k>/{pred.npz, selection.tsv, done.json}\n├── signal/sub-0X_fold<k>/     pred.npz, done.json\n├── video/length_fold<k>/, lowlevel_fold<k>/\n├── roi_map/sub-0X_fold<k>/    pred.npz(정서 예측, feature는 합과 제곱합), done.json\n├── roi_map_summary/\n│   ├── roi_map_summary.tsv, roi_map_emotion_r.tsv, roi_map_by_participant.npz\n│   └── figures/              ROI 지도 그림\n└── emotion_voxel_clusters/    centers_k*.npy, voxel_clusters.tsv.gz, roi_cluster_fraction_k10.tsv, loo_k10.tsv, summary.json, 그림",
        "src/s5_decoding.py, src/s5_baselines.py(ridge, mlp, signal, video, ged, mlbvae, emogrowth), src/s5_roi_map.py, src/s5_collect.py")
    out["logs"] = rd("logs (실행 기록)",
        "실행 로그, 작업 목록, 작업이 끝나면 다음 작업을 띄우는 대기 스크립트다. 지금 도는 작업이 여기에 쓰고 있어 2단계 전까지 옮기지 않는다.",
        "결과를 어디서 어떤 순서로 돌렸는지 되짚을 때 본다.",
        """- s6_queue_jobs_<tag>.tsv: login GPU에 띄울 작업 목록(name, plan, conditions, config, s6_out, est_hours)
- s6_queue_<tag>/state.json, s6_queue_<tag>.log: 그 목록을 띄운 실행기의 상태와 기록. ex) tag dlogin은 D 본 실행, hk_rest는 구역 분할, 네트워크, MC용 모델
- s6_grid_<결과 폴더>/, s6_dispatch_state_<tag>.tsv: A-1 grid와 본 실행 dispatcher의 상태
- *_chain.sh, *_chain.log: 앞 작업이 끝나기를 기다렸다가 다음 작업을 띄우는 스크립트. ex) s8_mc_chain.sh는 MC용 모델이 끝나면 MC 전이를 띄운다
- s6_m5361/: m5361_g sbatch 로그
- s5_baselines_<작업 번호>.log: S5 sbatch 로그
- s10/: S10 계산 로그
- s6_prelim_*, s6_check_*: 점검 실행의 로그(결과는 checks/)""",
        "logs/\n├── README.md\n├── s6_queue_jobs_<tag>.tsv\n├── s6_queue_<tag>/state.json\n├── s6_queue_<tag>.log\n├── *_chain.sh, *_chain.log\n├── s6_m5361/\n├── s10/\n└── 그 밖의 단계별 로그",
        "scripts/s6_queue.py, scripts/s6_dispatch.py, scripts/s6_grid.py와 각 단계 .sh")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="결과 폴더 정리와 README")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-moves", action="store_true")
    a = ap.parse_args(argv)
    if not OUT.is_dir():
        raise SystemExit(f"output_root가 없다: {OUT}")
    if not a.skip_moves:
        do_moves(a.dry_run)
    status = build_views(a.dry_run)
    for k, (n, want) in sorted(status.items()):
        print(f"링크 {n:>3}/{want:<3} {k}")
    texts = {"": root_readme(status), "checks": checks_readme(), "notes": notes_readme()}
    texts.update(s9_readmes())
    texts.update(s10_readmes())
    texts.update(s6_view_readmes(status))
    texts.update(raw_readmes())
    written = []
    for rel, text in texts.items():
        d = OUT / rel
        if rel and not (d.is_dir() or a.dry_run):
            print(f"README 건너뜀(폴더 없음): {rel}")
            continue
        write(d / "README.md", text, a.dry_run, written)
    print(f"README {len(written)}개" + (" (dry-run, 쓰지 않음)" if a.dry_run else ""))


if __name__ == "__main__":
    main()
