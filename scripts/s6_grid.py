#!/usr/bin/env python3
"""S6 A-1(brain_only) 후보 grid를 빈 login node GPU 여러 장에 나눠 띄운다 (11/13 석진 님).

왜 따로 두나
- s6_train은 한 조건의 후보를 한 프로세스에서 차례로 학습한다. learning rate 3개 × 입력층 weight decay 6개(17개)를 한 GPU에서 차례로 돌리면 fold 하나에 하루가 넘는다.
- 그래서 후보를 learning rate별 묶음으로 나눠 프로세스 여럿이 같은 실행 번호로 돌린다(s6_train --only-candidates). 끝나면 dispatcher의 brain_only stream이
  같은 실행 번호의 끝난 후보를 건너뛰고 선택만 한다.
- 실행 번호가 같으려면 조건 목록에 Stimulus 예측 평정을 쓰는 조건이 있어야 하므로(s6_dispatch 머리말 1) brain_only,brain_only_distill로 부르고
  --only-candidates가 brain_only 후보만 학습하고 끝낸다.
- plan 폴더는 FoldRunner가 처음 만들 때 다른 프로세스와 겹치면 안 되므로, fold마다 첫 작업이 plan을 만든 뒤에 나머지를 띄운다.
- 작업 하나는 login node 한 장이다. 사라졌는데 후보가 다 끝나지 않았으면 다른 node에서 한 번만 다시 띄운다(s6_train은 끝난 후보를 건너뛴다).
- 이 스크립트는 sbatch를 내지 않는다. 작업 하나의 어림이 24시간을 넘으면 띄우지 않고 멈춘다(그때는 --split으로 더 나누거나 sbatch로 따로 낸다).
사용(레포 최상위): python scripts/s6_grid.py --run-root <run worktree> --freeze <커밋> --config configs/s6/<설정>.json --s6-out <출력 폴더 절대 경로>
                 [--folds 1-6] [--split 1e-05=2] [--minutes 1e-05=200,0.0001=45,0.001=20] [--exclude 28] [--dry-run]
"""
import argparse
import json
import shlex
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s6_dispatch as D  # noqa: E402

KST = ZoneInfo("Asia/Seoul")
CARRIER = "brain_only,brain_only_distill"


def now():
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")


def make_groups(S, config, split):
    """learning rate마다 후보를 입력층 weight decay 순으로 묶는다. split: lr -> 나눌 수."""
    cands = S.candidates("brain_only", k_candidates=config.k_candidates, learning_rates=config.learning_rates)
    by_lr = {}
    for c in cands:
        by_lr.setdefault(c["lr"], []).append(c)
    out = []
    for lr in sorted(by_lr):
        cs = sorted(by_lr[lr], key=lambda c: (c["d"], c["input_wd"]))
        n = int(split.get(lr, 1))
        size = -(-len(cs) // n)
        for i in range(0, len(cs), size):
            out.append(dict(lr=lr, ids=[S.candidate_id(c) for c in cs[i:i + size]], wds=[c["input_wd"] for c in cs[i:i + size]]))
    if sorted(i for g in out for i in g["ids"]) != sorted(S.candidate_id(c) for c in cands):
        raise SystemExit("묶음이 후보를 한 번씩 덮지 않는다")
    return out


def done_ids(s6_out, k, ids, cond="brain_only"):
    return [i for i in ids if (Path(s6_out) / f"outer_fold{k}" / cond / f"{i}_seed0" / "done.json").exists()]


def target_groups(S, config, s6_out, k, sizes):
    """11/14. --target 모드. 그 fold의 A-1 선택으로 조건마다 후보를 만들고(s6_common.candidates) sizes개씩 묶는다."""
    sel = json.loads((Path(s6_out) / f"outer_fold{k}" / "brain_only" / "selected.json").read_text())
    out = []
    for cond, size in sizes.items():
        cands = S.candidates(cond, k_candidates=config.k_candidates, base=sel["candidate"], learning_rates=config.learning_rates, lr_follows_brain_only=config.lr_follows_brain_only)
        ids = [S.candidate_id(c) for c in cands]
        for i in range(0, len(ids), size):
            out.append(dict(cond=cond, ids=ids[i:i + size], lr=sel["candidate"]["lr"], wds=[sel["candidate"]["input_wd"]]))
    return out


def plan_ready(s6_out, k):
    return (Path(s6_out) / f"outer_fold{k}" / "plan" / "done.json").exists()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--freeze", required=True)
    ap.add_argument("--config", required=True, help="run worktree 기준 상대 경로")
    ap.add_argument("--s6-out", required=True)
    ap.add_argument("--folds", default="1-6")
    ap.add_argument("--split", default="", help="ex) 1e-05=2. 그 learning rate의 후보를 몇 작업으로 나눌지")
    ap.add_argument("--minutes", default="", help="어림용 학습 한 번의 분. ex) 1e-05=200,0.0001=45,0.001=20")
    ap.add_argument("--nodes", default="01-40")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--free-mib", type=int, default=2000)
    ap.add_argument("--poll", type=int, default=120)
    ap.add_argument("--target", default="", help="11/14. A-1 밖 조건의 후보를 나눠 띄운다. ex) brain_decoded=2,brain_only_featdec=2. fold마다 A-1 selected.json이 생긴 뒤 띄우고, scripts/s6_candidates.sh를 쓴다")
    ap.add_argument("--target-minutes", type=float, default=0, help="--target 모드의 어림용 학습 한 번의 분")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run_root = Path(a.run_root).resolve()
    D.check_freeze(run_root, a.freeze)
    S = D.load_rules(run_root / "src")
    config = S.load_config(run_root / a.config)
    split = {float(k): int(v) for k, v in (x.split("=") for x in a.split.split(",") if x)}
    minutes = {float(k): float(v) for k, v in (x.split("=") for x in a.minutes.split(",") if x)}
    folds = D.parse_folds(a.folds)
    if a.target:
        sizes = {k: int(v) for k, v in (x.split("=") for x in a.target.split(",") if x)}
        wait = [k for k in folds if not (Path(a.s6_out) / f"outer_fold{k}" / "brain_only" / "selected.json").exists()]
        while wait and not a.dry_run:  # A-1 선택이 모든 fold에 생길 때까지 기다린다(dispatcher의 brain_only stream이 만든다)
            print(f"[{now()}] A-1 선택을 기다린다: fold {wait}", flush=True)
            time.sleep(a.poll)
            wait = [k for k in folds if not (Path(a.s6_out) / f"outer_fold{k}" / "brain_only" / "selected.json").exists()]
        if wait:
            raise SystemExit(f"dry-run: A-1 선택이 없는 fold {wait}")
        jobs = []
        for k in folds:
            for g, gr in enumerate(target_groups(S, config, a.s6_out, k, sizes)):
                jobs.append(dict(fold=k, group=g, cond=gr["cond"], lr=gr["lr"], ids=gr["ids"], wds=gr["wds"], status="pending", attempts=0, node="", log="", launched=""))
        log_dir = Path(a.s6_out).parent / "logs" / f"s6_grid_{Path(a.s6_out).name}_targets"
        print(f"[{now()}] --target 작업 {len(jobs)}개", flush=True)
        for j in jobs[:len(jobs) // len(folds)]:
            est = a.target_minutes * len(j["ids"]) / 60
            print(f"  {j['cond']} 후보 {len(j['ids'])}개, 어림 {est:.1f} h", flush=True)
            if est > 24:
                raise SystemExit("작업 하나의 어림이 24시간을 넘는다(login node 규칙). 묶음을 줄인다")
    else:
        groups = make_groups(S, config, split)
        jobs = [dict(fold=k, group=g, cond="brain_only", lr=gr["lr"], ids=gr["ids"], wds=gr["wds"], status="pending", attempts=0, node="", log="", launched="") for k in folds for g, gr in enumerate(groups)]
        log_dir = Path(a.s6_out).parent / "logs" / f"s6_grid_{Path(a.s6_out).name}"
        print(f"[{now()}] 작업 {len(jobs)}개(fold {len(folds)} × 묶음 {len(groups)}), 후보 {sum(len(g['ids']) for g in groups)}개/fold", flush=True)
        for g, gr in enumerate(groups):
            est = minutes.get(gr["lr"], 0) * len(gr["ids"]) / 60
            print(f"  묶음 {g}: lr {gr['lr']}, weight decay {gr['wds']}, 어림 {est:.1f} h", flush=True)
            if est > 24:
                raise SystemExit(f"묶음 {g}의 어림이 24시간을 넘는다. --split으로 더 나누거나 sbatch로 따로 낸다(login node 규칙)")
    state_path = log_dir / "state.json"
    if a.dry_run:
        return
    log_dir.mkdir(parents=True, exist_ok=True)
    if state_path.exists():  # 다시 켜면 잇는다
        old = {(j["fold"], j["group"]): j for j in json.loads(state_path.read_text())}
        for j in jobs:
            o = old.get((j["fold"], j["group"]))
            if o and o["ids"] == j["ids"] and o.get("cond", "brain_only") == j["cond"]:
                j.update({k: o[k] for k in ("status", "attempts", "node", "log", "launched")})
    remote = D.Remote()
    exclude = set(D.parse_nodes(a.exclude)) if a.exclude else set()
    nodes = [n for n in D.parse_nodes(a.nodes) if n not in exclude]
    marker = lambda j: f"--target {j['cond']}:{','.join(j['ids'])}" if a.target else f"--only-candidates {','.join(j['ids'])}"
    while True:
        with ThreadPoolExecutor(16) as ex:
            probes = dict(zip(nodes, ex.map(remote.probe, nodes)))
        # 도는 작업 확인
        for j in jobs:
            if j["status"] != "running":
                continue
            if len(done_ids(a.s6_out, j["fold"], j["ids"], j["cond"])) == len(j["ids"]):
                j["status"] = "done"
                print(f"[{now()}] 끝남 fold {j['fold']} 묶음 {j['group']} ({j['node']})", flush=True)
                continue
            p = probes.get(j["node"])
            if p is None:
                continue  # node를 못 봤으면 다음 확인까지 기다린다
            alive = any(f"outer_fold{j['fold']}" in args and marker(j) in args for _, args in p.procs)
            if not alive:
                j["status"] = "pending" if j["attempts"] < D.MAX_ATTEMPTS else "failed"
                print(f"[{now()}] 사라짐 fold {j['fold']} 묶음 {j['group']} ({j['node']}), 끝난 후보 {len(done_ids(a.s6_out, j['fold'], j['ids'], j['cond']))}/{len(j['ids'])} -> {j['status']}", flush=True)
        # 새로 띄우기. fold마다 plan이 없으면 그 fold의 첫 작업 하나만 띄운다
        busy = {j["node"] for j in jobs if j["status"] == "running"}
        free = [n for n in nodes if n not in busy and D.free_gpu(probes.get(n), a.free_mib) is not None]
        for j in jobs:
            if not free:
                break
            if j["status"] != "pending":
                continue
            if len(done_ids(a.s6_out, j["fold"], j["ids"], j["cond"])) == len(j["ids"]):
                j["status"] = "done"
                continue
            if not plan_ready(a.s6_out, j["fold"]) and any(o["fold"] == j["fold"] and o["status"] == "running" for o in jobs):
                continue
            node = free.pop(0)
            gpu = D.free_gpu(probes[node], a.free_mib)
            j["attempts"] += 1
            j["log"] = str(log_dir / f"fold{j['fold']}_group{j['group']}_try{j['attempts']}.log")
            q = shlex.quote
            if a.target:  # 같은 실행 번호로 그 조건의 후보만 학습한다(scripts/s6_candidates.py, src는 run worktree 것)
                wrapper = Path(__file__).resolve().parent / "s6_candidates.sh"
                cmd = (f"S6_OUT={q(a.s6_out)} CUDA_VISIBLE_DEVICES={gpu} nohup bash {q(str(wrapper))} {q(str(run_root))} --plan outer_fold{j['fold']} --conditions {CARRIER} "
                       f"--config {q(str(run_root / a.config))} --design-freeze {q(a.freeze)} --target {j['cond']}:{','.join(j['ids'])} --device cuda > {q(j['log'])} 2>&1 < /dev/null & echo {D.PID_MARK}$!")
            else:
                cmd = (f"cd {q(str(run_root))} && S6_OUT={q(a.s6_out)} CUDA_VISIBLE_DEVICES={gpu} nohup bash scripts/s6_train.sh outer_fold{j['fold']} {CARRIER} "
                       f"{q(str(run_root / a.config))} {q(a.freeze)} --only-candidates {','.join(j['ids'])} > {q(j['log'])} 2>&1 < /dev/null & echo {D.PID_MARK}$!")
            remote.launch(node, cmd)
            j.update(status="running", node=node, launched=now())
            print(f"[{now()}] 띄움 fold {j['fold']} 묶음 {j['group']} ({j['cond']}, 후보 {len(j['ids'])}, lr {j['lr']}, wd {j['wds']}) -> {node} 시도 {j['attempts']}", flush=True)
        state_path.write_text(json.dumps(jobs, indent=1))
        left = [j for j in jobs if j["status"] in ("pending", "running")]
        if not left:
            bad = [j for j in jobs if j["status"] == "failed"]
            print(f"[{now()}] 모두 끝. 실패 {len(bad)}개", flush=True)
            return
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
