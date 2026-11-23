#!/usr/bin/env python3
"""S9 Dec-바(01 6-2b) 모델 확장: 캡션 구역 분할(capzone)에 C-1, D-3, D-4를 더한다(11/19 석진 님 "모두 진행"). GPU.

왜 별도 스크립트인가
- A-1 60개는 cabc1f7 코드와 configs/s6/run_config_capzone.json으로 S6_OUT=s6_brain_capzone에 있다. s6 코드나 설정을 고치면 실행 번호가 바뀌어
  A-1 결과를 이어 쓸 수 없다. 그래서 같은 코드판(cabc1f7)과 같은 설정으로 실행 번호를 똑같이 다시 내고, 같은 결과 폴더에 이어 붙인다.
  다시 낸 실행 번호가 A-1 선택(brain_only/selected.json)의 실행 번호와 다르면 멈춘다.
- s6_train.main은 내용 구역 분할에서 A-1, C-1만 허용한다(check_conditions, 6-2 규칙). Dec-바는 석진 님이 D 묶음까지 넓혔으므로 이 스크립트가 그 검사 대신 쓰인다.
후보(새로 고르지 않음)
- encoder 2(feature_encoder): 설정의 후보 하나(lr 1e-3, d 64, 입력층 weight decay 100). HK 6 fold 모두 같은 값을 골랐다.
- C-1, D-3, D-4: HK 주 비교(s6_brain_final, learning rate 두 실행을 합친 폴더)가 같은 바깥 fold에서 고른 후보를 그대로 쓴다.
  분할의 시험 fold와 검증 fold는 그 바깥 fold와 같다. A-1도 HK 표준 실행이 고른 값으로 고정했다(6-2와 같은 원리).
순서와 저장(FoldRunner 그대로)
- feature_encoder(선택 포함) → C-1(train_one) → D-3(train_one. 학습 행은 fold 밖 encoder 2 넷의 v̂₂, ĉ₂이고 FoldRunner.oof가 그 넷을 만든다) → D-4(짝 넷, 시험은 짝 평균).
- 끝난 단계는 같은 실행 번호일 때 건너뛴다(s4_common.done_or_new). 결과는 <S6_OUT>/<분할>/<조건>/ 아래에 다른 조건과 같은 꼴로 쓴다.
사용(cabc1f7 위에 이 파일만 더한 run worktree의 src에서)
  python s9_capzone_models.py --plan capzone_block<b>_fold<k>_<excluded|control> --config <run_config_capzone.json> --s6-out <s6_brain_capzone>
         --hk-final <s6_brain_final> --design-freeze cabc1f7 [--models c1,d3,d4] [--device cuda]
"""
import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

MODELS = {"c1": "brain_decoded", "d3": "brain_features_only", "d4": "brain_frozen_feature_encoder"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Dec-바 C-1, D-3, D-4")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--s6-out", required=True)
    ap.add_argument("--hk-final", required=True)
    ap.add_argument("--design-freeze", required=True)
    ap.add_argument("--models", default="c1,d3,d4")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args(argv)
    if not a.plan.startswith("capzone_block"):
        raise SystemExit("캡션 구역 분할(capzone_block...)만 돌린다")
    os.environ["S6_OUT"] = str(Path(a.s6_out).resolve())
    import torch
    import s4_common as c
    import s6_common as S
    import s6_train as T
    c.guard(a.design_freeze)
    config = S.load_config(a.config)
    split = c.load_split()
    plan = S.load_plan(a.plan, split)
    spec = S.Spec(seeds=config.seeds, input_lr_scale=config.input_lr_scale)
    run = S.Run(a.design_freeze, {**S.input_paths(plan, stimulus=False, cells=config.tokenizer == "roi_cells"), "config": a.config}, stimulus_run_key=None, plan=plan.name,
                config=asdict(config), spec=asdict(spec), torch=torch.__version__, deterministic=torch.are_deterministic_algorithms_enabled(), nondeterministic_ops=[])
    root = S.OUT / plan.name
    a1 = json.loads((root / "brain_only" / "selected.json").read_text())
    if a1["run_key"] != run.key:
        raise SystemExit(f"{plan.name}: 다시 낸 실행 번호가 A-1 선택의 실행 번호와 다르다. 코드판과 설정이 A-1과 같은지 확인한다")
    hk = lambda cond: json.loads((Path(a.hk_final) / f"outer_fold{plan.outer_fold}" / cond / "selected.json").read_text())["candidate"]
    y, v, cap = T.load_known(split, plan, False)
    brains = S.load_brains(split, list(plan.train) + list(plan.val) + list(plan.test))
    fd = S.prepare_fold(brains, split, y, v, cap, plan, stimulus=None, include_test_features=False, device=a.device, roi_keep=S.roi_keep(config))
    run.check()
    runner = T.FoldRunner(fd, split, run, spec, config, root)
    runner.raw = (brains, y, v, cap)
    seed = spec.seeds[0]

    def done_selection(cond):
        p = root / cond / "selected.json"
        return p.exists() and json.loads(p.read_text())["run_key"] == run.key

    def fixed(cond, cand):
        if done_selection(cond):
            print(cond, "끝나 있음", flush=True)
            return
        d = runner.train_one(cond, cand, seed)
        rel = str(runner.run_dir(cond, cand, seed).relative_to(runner.root))
        runner._write_selection(cond, [runner._row(cand, d)], cand, None, {str(seed): rel})
        runner.save_outputs(runner.root / rel)
        runner.run.check()
        print(cond, "저장", rel, flush=True)

    if a1["candidate"]["d"] != 64 or a1["candidate"]["input_wd"] != 100.0:
        raise SystemExit("A-1 후보가 HK와 다르다")
    if not done_selection("feature_encoder"):
        runner.run_condition("feature_encoder")
    wanted = a.models.split(",")
    if "c1" in wanted:
        fixed(MODELS["c1"], hk(MODELS["c1"]))
    if "d3" in wanted:
        fixed(MODELS["d3"], hk(MODELS["d3"]))
    if "d4" in wanted:
        cond = MODELS["d4"]
        if not done_selection(cond):
            cand = hk(cond)
            S.check_candidate(cond, cand)
            ds = runner._pairs(cond, [cand], seed)[S.candidate_id(cand)]
            runner._ensemble(cond, cand, seed, ds)
            rows = [dict(cand, candidate_id=S.candidate_id(cand), val_score=sum(d["val_score"] for d in ds) / len(ds), val_loss=sum(d["val_loss"] for d in ds) / len(ds),
                         best_epoch=[d["best_epoch"] for d in ds], diverged=False, source_condition=None, source_id=None)]
            runner._write_selection(cond, rows, cand, None, {str(seed): str(runner.run_dir(cond, cand, seed).relative_to(runner.root))})
            runner.run.check()
            print(cond, "저장", flush=True)
    print(plan.name, "끝", flush=True)


if __name__ == "__main__":
    sys.exit(main())
