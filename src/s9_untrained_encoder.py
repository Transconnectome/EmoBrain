#!/usr/bin/env python3
"""S9 D-4 대조. 학습하지 않은 encoder 2를 고정하고 그 위에 정서 head만 학습한다(11/18 석진 님 "뿌려놓고 돌려놓긴 하자"; 06 5절 D-4의 주의, 14절 11번, 01 5-A).

왜: D-4(brain_frozen_feature_encoder)는 장면 특징만 맞히도록 학습한 encoder 2의 token 위에서 정서 평정을 읽는다. token은 장면 특징 공간에 묶여 있지 않아
장면과 관계없는 뇌 정보도 지나갈 수 있다. 그래서 같은 구조의 encoder를 학습하지 않은 채(무작위 초기값) 고정해도 D-4만큼 읽히는지 본다.
D-4가 이 대조보다 높아야 "장면 특징을 배운 encoder라서 읽혔다"고 쓸 수 있다.

D-4와 같게 두는 것(차이는 encoder 2의 가중치 하나)
- 코드판: HK 주 비교(S6_OUT = s6_brain_grid_main)를 학습한 1bca774의 s4~s6 코드. 이 스크립트는 그 코드 위에서만 돌린다.
  실행 번호(run key)를 주 비교와 같은 방식으로 다시 내고, 이미 있는 D-4 선택(selected.json)의 실행 번호와 같지 않으면 멈춘다.
- 짝 구조(11/9): 바깥 fold마다 학습 fold 4개를 하나씩 뺀 짝 넷. 짝 j의 head는 j번째 fold 영상으로만 학습하고, 표준화는 짝 j의 encoder 2와 같은 영상 통계다.
  시험 예측은 네 짝의 예측 평정 평균이다. 짝의 학습, 검증, 시험 영상과 표준화는 D-4가 쓴 fold 밖 encoder 2 기록(feature_encoder_oof)에서 그대로 받는다.
- 후보: D-4가 그 fold에서 고른 후보(d, 입력층 weight decay, learning rate) 하나. 새로 고르지 않는다. seed 0.
- 초기값: D-4의 train_pair와 같이 seed_everything(seed) 뒤 build_model을 부른다. D-4는 여기서 encoder 2 가중치를 학습한 체크포인트로 덮어쓰고,
  이 대조는 덮어쓰지 않는다. 그래서 정서 head의 초기값은 D-4와 같다. 입력층(ROI → token)과 encoder 블록 모두 학습하지 않은 무작위 값이다.
- 학습: s6_train.fit, 손실 make_loss("brain_frozen_feature_encoder"), 조기 종료와 저장 규칙이 D-4와 같다. 학습 뒤 encoder 2 가중치가 바뀌지 않았는지 해시로 확인한다.
출력(레포 밖 --out): <out>/outer_fold<k>/brain_frozen_untrained_encoder/<후보>_seed0/{pair<j>/{history.tsv, val_pred.npz, test_pred.npz, done.json}, ensemble/{val_pred.npz, test_pred.npz, done.json}}
  체크포인트(model.pt)는 남기지 않는다(encoder는 seed로 다시 만들 수 있고 head만 다르다).
summarize: 6 fold 시험 예측을 모아 A-1, D-4, 이 대조의 정서별 r(참가자마다, 그다음 5명 평균)과 차이(대조 − D-4, D-4 − A-1, 대조 − A-1)를 낸다.
  bootstrap은 s10_per_emotion의 HK와 같다(내용 묶음 단위, BOOT_SEED 20261115, 10,000회, 모든 모델과 5명에 같은 재표집). 34개와 27개 평균을 함께 낸다.
사용(1bca774 위에 이 파일만 더한 run worktree의 src에서)
  python s9_untrained_encoder.py train --plan outer_fold<k> --config <run_config_grid_main.json> --s6-root <s6_brain_grid_main> --out <폴더> --design-freeze 1bca774 [--device cuda]
  python s9_untrained_encoder.py summarize --s6-root <s6_brain_grid_main> --out <폴더>
"""
import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

COND = "brain_frozen_feature_encoder"  # D-4. 구조, 손실, 짝 규칙을 그대로 빌린다
NAME = "brain_frozen_untrained_encoder"  # 이 대조의 출력 폴더 이름
CK_SEVEN = ("pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy")
BOOT_SEED = 20261115


def _json(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=float))


def train(a):
    os.environ["S6_OUT"] = str(Path(a.s6_root).resolve())
    import torch
    import s4_common as c
    import s6_common as S
    import s6_model as M
    import s6_train as T
    c.guard(a.design_freeze)
    config = S.load_config(a.config)
    split = c.load_split()
    plan = S.load_plan(a.plan, split)
    if not plan.name.startswith("outer_fold"):
        raise SystemExit("HK 바깥 fold(outer_fold1~6)만 돌린다")
    spec = S.Spec(seeds=config.seeds)
    # 주 비교의 실행 번호를 같은 방식으로 다시 낸다(s6_train.main). 주 비교는 Stimulus 예측을 쓰는 조건과 함께 돌았으므로 그 입력 해시가 들어 있다
    probe = S.Run(a.design_freeze, {**S.input_paths(plan), "config": a.config})
    stimulus_run = S.check_stimulus_source(S.stimulus_path(plan.outer_fold).parent / "done.json", plan.outer_fold, probe.hashes)
    run = S.Run(a.design_freeze, {**S.input_paths(plan, stimulus=True, cells=config.tokenizer == "roi_cells"), "config": a.config}, stimulus_run_key=stimulus_run, plan=plan.name,
                config=asdict(config), spec=asdict(spec), torch=torch.__version__, deterministic=torch.are_deterministic_algorithms_enabled(), nondeterministic_ops=[])
    root = Path(a.s6_root) / plan.name
    sel = json.loads((root / COND / "selected.json").read_text())
    if sel["run_key"] != run.key:
        raise SystemExit(f"{plan.name}: 다시 낸 실행 번호가 D-4 선택의 실행 번호와 다르다. 코드판, 입력, 설정이 주 비교와 같은지 확인한다")
    for j, *_ in S.inner_plans(plan, split):
        if not (root / "feature_encoder_oof" / "seed0" / f"inner{j}" / "done.json").exists():
            raise SystemExit(f"{plan.name}: fold 밖 encoder 2(inner{j})가 없다. 이 스크립트는 encoder 2를 새로 학습하지 않는다")
    cand = sel["candidate"]
    seed = spec.seeds[0]
    y, v, cap = T.load_known(split, plan, False)
    brains = S.load_brains(split, list(plan.train) + list(plan.val) + list(plan.test))
    fd = S.prepare_fold(brains, split, y, v, cap, plan, stimulus=None, include_test_features=False, device=a.device)
    run.check()
    runner = T.FoldRunner(fd, split, run, spec, config, root)  # 주 비교의 plan을 읽기만 한다(같은 실행 번호라 다시 쓰지 않음)
    runner.raw = (brains, y, v, cap)
    oof = runner.oof(seed)  # 이미 있는 fold 밖 encoder 2 넷의 학습, 시험 영상과 통계. 가중치는 쓰지 않는다
    script_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    key = hashlib.sha256(json.dumps(dict(run=run.key, control=NAME, candidate=cand, seed=seed, script=script_sha), sort_keys=True).encode()).hexdigest()
    folder = Path(a.out) / plan.name / NAME / f"{S.candidate_id(cand)}_seed{seed}"
    pairs = []
    for enc in oof["encoders"]:
        path = folder / f"pair{enc['fold']}"
        if c.done_or_new(path, key):
            pairs.append(json.loads((path / "done.json").read_text()))
            continue
        fdj = runner._inner_fold_head(enc)
        started = time.time()
        T.seed_everything(seed)
        model = S.build_model(COND, cand, fdj.voxel_counts, config.tokenizer, config.voxel_sampling)  # D-4와 같은 순서로 초기화한다. 여기서 체크포인트를 넣지 않는다
        M.freeze(model.feature_model)
        digest0 = M.state_digest(model.feature_model)
        model = model.to(fdj.device)
        forward = T.brain_forward(fdj)
        result = T.fit(model, fdj, spec, lr=cand["lr"], input_wd=cand["input_wd"], feature_wd=None, loss_fn=T.make_loss(COND, cand, fdj), forward=forward, seed=seed)
        if M.state_digest(model.feature_model) != digest0:
            raise ValueError("학습하지 않은 encoder 2가 학습 중에 바뀌었다")
        with c.Atomic(path) as tmp:
            result.history.to_csv(tmp / "history.tsv", sep="\t", index=False)
            for name, rows in (("val_pred.npz", fdj.rows("val")), ("test_pred.npz", fdj.rows("test"))):
                z = T.collect(model, rows, forward, spec.batch)["z"]
                np.savez(tmp / name, participant=fdj.participant_names(rows), video_id=fdj.row_video[rows], logit=z.numpy(), p=z.sigmoid().numpy())
            run._check_code()
            done = dict(run.prov, run_key=key, base_run_key=run.key, script_sha256=script_sha, plan=fdj.plan.name, condition=NAME, borrowed_condition=COND, encoder="untrained (random init after seed_everything, frozen)",
                        encoder_digest=digest0, candidate=cand, candidate_id=S.candidate_id(cand), seed=seed, held_fold=enc["fold"], n_head_rows=len(fdj.rows("train")),
                        d4_encoder_sha256_not_loaded=enc["sha256"], best_epoch=result.best_epoch, val_loss=result.val_loss, val_score=result.val_score, n_epochs=result.n_epochs, **c.timing(started))
            _json(done, tmp / "done.json")
        print("저장", path, f"epoch {result.best_epoch}/{result.n_epochs}, 검증 r {result.val_score:.4f}", flush=True)
        pairs.append(done)
        del fdj, model
        torch.cuda.empty_cache()
    out = folder / "ensemble"
    if not c.done_or_new(out, key):
        with c.Atomic(out) as tmp:
            for name in ("val_pred.npz", "test_pred.npz"):
                parts = [np.load(folder / f"pair{d['held_fold']}" / name) for d in pairs]
                keys = [list(zip(z["participant"].tolist(), z["video_id"].tolist())) for z in parts]
                if any(k != keys[0] for k in keys):
                    raise ValueError("짝마다 예측한 행이 다르다")
                pm = np.stack([z["p"] for z in parts]).mean(0)
                np.savez(tmp / name, participant=parts[0]["participant"], video_id=parts[0]["video_id"], p=pm, logit=np.log(pm) - np.log1p(-pm), p_pairs=np.stack([z["p"] for z in parts]), held_folds=np.array([d["held_fold"] for d in pairs]))
            _json(dict(run.prov, run_key=key, base_run_key=run.key, condition=NAME, candidate=cand, seed=seed, pairs=[dict(held_fold=d["held_fold"], val_score=d["val_score"], best_epoch=d["best_epoch"]) for d in pairs]), tmp / "done.json")
    print(plan.name, "끝", folder, flush=True)


def summarize(a):
    os.environ["S6_OUT"] = str(Path(a.s6_root).resolve())
    import s4_common as c
    import s10_performance as PF
    import s10_stats as st
    split = c.load_split()
    y, cols = c.load_scores(split, "emotions")
    lm = pd.read_csv(c.LABEL_MAP, sep="\t")
    emotions = lm.set_index("score_col").loc[cols, "name"].tolist()
    ck = np.array([e in CK_SEVEN for e in emotions])
    found = PF.find_predictions(a.s6_root)
    plan_rows = {k: PF.plan_test_rows(a.s6_root, k) for k in range(1, PF.N_FOLDS + 1)}
    paths = {}
    for cond in ("brain_only", COND):
        f = found[(found.condition == cond) & (found.seed == 0) & (found.status == "ok")]
        if sorted(f.fold.tolist()) != list(range(1, PF.N_FOLDS + 1)):
            raise SystemExit(f"{cond}: seed 0의 6 fold 예측이 다 있지 않다")
        paths[cond] = dict(zip(f.fold.astype(int), f.path))
    ctrl = {}
    for k in range(1, PF.N_FOLDS + 1):
        hits = sorted((Path(a.out) / f"outer_fold{k}" / NAME).glob("*_seed0/ensemble/test_pred.npz"))
        if len(hits) != 1:
            raise SystemExit(f"outer_fold{k}: 대조 예측이 {len(hits)}개다")
        ctrl[k] = hits[0]
    paths[NAME] = ctrl
    data = {cond: PF.load_condition(p, split, plan_rows, y.shape[1]) for cond, p in paths.items()}
    videos = PF.same_rows(data)
    pids = sorted(videos)
    U = np.array(sorted(set().union(*[set(v.tolist()) for v in videos.values()])), np.int64)
    sp = split.set_index("video_id").loc[U]
    split_pos = {v: i for i, v in enumerate(split.video_id.tolist())}
    yU = np.asarray(y, np.float64)[[split_pos[v] for v in U]]
    pos = {q: np.searchsorted(U, videos[q]) for q in pids}
    codes, n_units = st.unit_codes(sp.canonical_id.to_numpy())
    W = st.bootstrap_counts(n_units, a.n_boot, np.random.default_rng(BOOT_SEED))
    point, boot = {}, {}
    for q in pids:
        yq = yU[pos[q]]
        rb = st.boot_r(W[:, codes[pos[q]]], yq, {cond: data[cond][q][1] for cond in data})
        for cond in data:
            point.setdefault(cond, []).append(st.pearson_columns(yq, data[cond][q][1]))
            boot.setdefault(cond, []).append(rb[cond])
    res = {cond: (PF.nanmean0(np.stack(point[cond])), PF.nanmean0(np.stack(boot[cond]))) for cond in data}
    label = {"brain_only": "A-1", COND: "D-4", NAME: "D-4 대조(학습하지 않은 encoder)"}
    per = pd.DataFrame([dict(emotion=emotions[e], ck27=not ck[e], **{label[cd]: float(res[cd][0][e]) for cd in res}) for e in range(len(emotions))])
    rows, summ = [], []
    for x, ref in ((NAME, COND), (COND, "brain_only"), (NAME, "brain_only")):
        d, db = res[x][0] - res[ref][0], res[x][1] - res[ref][1]
        lo, hi = st.basic_ci(d, db)
        p = st.centered_p(d, db)
        rows += [dict(comparison=f"{label[x]} − {label[ref]}", emotion=emotions[e], ck27=not ck[e], diff=float(d[e]), ci_low=float(lo[e]), ci_high=float(hi[e]), p=float(p[e])) for e in range(len(emotions))]
        for setname, m in (("34", np.ones(len(emotions), bool)), ("27", ~ck)):
            dm, dbm = float(np.nanmean(d[m])), np.nanmean(db[:, m], 1)
            l2, h2 = st.basic_ci(np.array([dm]), dbm[:, None])
            summ.append(dict(comparison=f"{label[x]} − {label[ref]}", set=setname, mean_r_model=float(np.nanmean(res[x][0][m])), mean_r_ref=float(np.nanmean(res[ref][0][m])),
                             diff=dm, ci_low=float(l2[0]), ci_high=float(h2[0]), p=float(st.centered_p(np.array([dm]), dbm[:, None])[0])))
    o = Path(a.out) / "summary"
    o.mkdir(parents=True, exist_ok=True)
    per.to_csv(o / "per_emotion.tsv", sep="\t", index=False)
    pd.DataFrame(rows).to_csv(o / "differences.tsv", sep="\t", index=False)
    pd.DataFrame(summ).to_csv(o / "summary.tsv", sep="\t", index=False)
    _json(dict(participants=pids, n_videos_union=len(U), n_bootstrap_units=n_units, n_boot=a.n_boot, boot_seed=BOOT_SEED, code_commit=c.START_HEAD, code_dirty=c.START_DIRTY), o / "run_info.json")
    print(pd.DataFrame(summ).to_string(index=False), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="D-4 대조: 학습하지 않은 encoder 2")
    ap.add_argument("step", choices=("train", "summarize"))
    ap.add_argument("--plan")
    ap.add_argument("--config")
    ap.add_argument("--s6-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--design-freeze", default="")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--n-boot", type=int, default=10_000)
    a = ap.parse_args(argv)
    if a.step == "train":
        if not (a.plan and a.config):
            raise SystemExit("train에는 --plan과 --config가 필요하다")
        train(a)
    else:
        summarize(a)


if __name__ == "__main__":
    sys.exit(main())
