#!/usr/bin/env python3
"""S6 분할 여러 개를 빈 login node GPU에 차례로 띄운다 (11/15 석진 님. 6-2 구역 분할 60개, 6-4a 묶음 13개 × fold 6, HK 최종 모델).

- 작업 하나는 s6_train 한 번이다(분할 하나, 조건 목록, 설정 하나, 결과 폴더 하나). 작업 목록은 TSV이고 열은 name, plan, conditions, config, s6_out, est_hours다.
  config는 run worktree 안의 절대 경로다. 실행 번호(run_key)는 s6_train이 그 설정과 코드로 만든다.
- 끝남은 조건마다 <s6_out>/<plan>/<조건>/selected.json이 있고 프로세스가 사라진 것이다. selected.json은 모든 seed를 학습한 뒤에 쓰인다.
  프로세스가 사라졌는데 끝나지 않았으면 다른 node에서 한 번 더 띄운다(s6_train은 끝난 후보를 건너뛴다).
- node는 이 사용자의 s6_train이 없고 GPU 메모리가 빈 것만 쓴다(s6_dispatch.free_gpu). login node GPU는 다른 사용자도 쓰므로 node 묶음을 나누지 않고,
  띄우기 직전에 그 node를 다시 본다. 다른 실행기(dispatcher)가 그 사이 잡았으면 건너뛴다.
- 어림이 24시간을 넘는 작업은 받지 않는다(login node 규칙). sbatch를 내지 않는다. 목록의 순서대로 띄운다.
- 다시 켜면 상태 파일(<s6_out 부모>/logs/s6_queue_<tag>/state.json)에서 잇는다.
사용(레포 최상위): python scripts/s6_queue.py --tag <이름> --run-root <run worktree> --freeze <커밋> --jobs <작업 TSV> --nodes 17-40 [--exclude 28] [--dry-run]
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

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s6_dispatch as D  # noqa: E402

KST = ZoneInfo("Asia/Seoul")
COLUMNS = ("name", "plan", "conditions", "config", "s6_out", "est_hours")


def now():
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")


def read_jobs(path, run_root):
    """작업 TSV를 읽고 확인한다. 이름이 겹치거나, 같은 결과 폴더의 같은 분할이 둘이거나, 설정이 run worktree 밖이거나, 어림이 24시간을 넘으면 멈춘다."""
    t = pd.read_csv(path, sep="\t", dtype=str)
    if tuple(t.columns) != COLUMNS:
        raise SystemExit(f"작업 TSV의 열은 {COLUMNS}이어야 한다")
    if t.name.duplicated().any() or t.duplicated(["s6_out", "plan"]).any():
        raise SystemExit("작업 이름이나 (결과 폴더, 분할)이 겹친다")
    jobs = []
    for r in t.itertuples(index=False):
        cfg = Path(r.config)
        if not cfg.is_absolute() or Path(run_root) not in cfg.parents or not cfg.exists():
            raise SystemExit(f"{r.name}: 설정은 run worktree 안의 절대 경로여야 한다 {cfg}")
        if not Path(r.s6_out).is_absolute():
            raise SystemExit(f"{r.name}: 결과 폴더는 절대 경로여야 한다")
        est = float(r.est_hours)
        if not 0 < est <= 24:
            raise SystemExit(f"{r.name}: 어림 {est} h. login node는 24시간 이하만 띄운다")
        jobs.append(dict(name=r.name, plan=r.plan, conditions=r.conditions, config=str(cfg), s6_out=r.s6_out, est_hours=est, status="pending", attempts=0, node="", log="", launched=""))
    return jobs


def finished(job):
    return all((Path(job["s6_out"]) / job["plan"] / c / "selected.json").exists() for c in job["conditions"].split(","))


def job_procs(probe, job):
    """probe에서 이 작업(같은 분할, 같은 설정)의 s6_train 프로세스."""
    if probe is None:
        return []
    return [(p, a) for p, a in probe.procs if D.S6_PROC.search(a) and job["plan"] in a.split() and job["config"] in a]


def command(run_root, job, gpu, freeze):
    q = shlex.quote
    log = Path(job["log"])
    return (f"cd {q(str(run_root))} && mkdir -p {q(str(log.parent))} && S6_OUT={q(job['s6_out'])} CUDA_VISIBLE_DEVICES={int(gpu)} "
            f"nohup bash scripts/s6_train.sh {q(job['plan'])} {q(job['conditions'])} {q(job['config'])} {q(freeze)} > {q(str(log))} 2>&1 < /dev/null & echo {D.PID_MARK}$!")


def step(jobs, remote, nodes, run_root, freeze, log_dir, free_mib, out=print):
    """한 번 확인하고 띄운다. 돌려주는 값: 아직 끝나지 않은 작업 수."""
    with ThreadPoolExecutor(16) as ex:
        probes = dict(zip(nodes, ex.map(remote.probe, nodes)))
    for j in jobs:
        if j["status"] != "running":
            continue
        p = probes.get(j["node"])
        if p is None:
            continue  # node를 못 봤으면 다음 확인까지 기다린다
        if job_procs(p, j):
            continue
        if finished(j):
            j["status"] = "done"
            out(f"[{now()}] 끝남 {j['name']} ({j['node']})")
        else:
            j["status"] = "pending" if j["attempts"] < D.MAX_ATTEMPTS else "failed"
            out(f"[{now()}] 사라짐 {j['name']} ({j['node']}) -> {j['status']}")
    busy = {j["node"] for j in jobs if j["status"] == "running"}
    free = [n for n in nodes if n not in busy and D.free_gpu(probes.get(n), free_mib) is not None]
    for j in jobs:
        if not free:
            break
        if j["status"] != "pending":
            continue
        if finished(j):
            j["status"] = "done"
            continue
        gpu = None
        while free and gpu is None:  # 11/15. 띄우기 직전에 다시 본다. 다른 실행기(dispatcher)가 그 사이 같은 node를 잡았으면 다음 node로 넘어간다
            node = free.pop(0)
            gpu = D.free_gpu(remote.probe(node), free_mib)
        if gpu is None:
            break
        j["attempts"] += 1
        j["log"] = str(log_dir / f"{j['name']}_try{j['attempts']}.log")
        remote.launch(node, command(run_root, j, gpu, freeze))
        j.update(status="running", node=node, launched=now())
        out(f"[{now()}] 띄움 {j['name']} ({j['plan']}, {j['conditions']}, 어림 {j['est_hours']:.1f} h) -> {node} 시도 {j['attempts']}")
    return sum(j["status"] in ("pending", "running") for j in jobs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--freeze", required=True)
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--nodes", default="01-40")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--free-mib", type=int, default=2000)
    ap.add_argument("--poll", type=float, default=300)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run_root = Path(a.run_root).resolve()
    jobs = read_jobs(a.jobs, run_root)
    exclude = set(D.parse_nodes(a.exclude)) if a.exclude else set()
    nodes = [n for n in D.parse_nodes(a.nodes) if n not in exclude]
    total = sum(j["est_hours"] for j in jobs)
    print(f"[{now()}] 작업 {len(jobs)}개, 어림 합 {total:.0f} GPU-h, node {len(nodes)}개({nodes[0]}~{nodes[-1]}), 고르게 돌면 약 {total / max(1, len(nodes)):.0f} h", flush=True)
    for name, g in pd.DataFrame(jobs).groupby(pd.DataFrame(jobs).name.str.split("_").str[0], sort=False):
        print(f"  {name}: {len(g)}개, 하나 {g.est_hours.min():.1f}~{g.est_hours.max():.1f} h", flush=True)
    if a.dry_run:
        return
    log_dir = Path(jobs[0]["s6_out"]).parent / "logs" / f"s6_queue_{a.tag}"
    log_dir.mkdir(parents=True, exist_ok=True)
    state_path = log_dir / "state.json"
    if state_path.exists():
        old = {j["name"]: j for j in json.loads(state_path.read_text())}
        for j in jobs:
            o = old.get(j["name"])
            if o and o["plan"] == j["plan"] and o["config"] == j["config"]:
                j.update({k: o[k] for k in ("status", "attempts", "node", "log", "launched")})
    remote = D.Remote()
    while True:
        left = step(jobs, remote, nodes, run_root, a.freeze, log_dir, a.free_mib, out=lambda s: print(s, flush=True))
        state_path.write_text(json.dumps(jobs, indent=1))
        if not left:
            print(f"[{now()}] 모두 끝. 실패 {sum(j['status'] == 'failed' for j in jobs)}개", flush=True)
            return
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
