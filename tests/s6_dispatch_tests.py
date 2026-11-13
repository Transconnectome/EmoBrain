#!/usr/bin/env python3
"""scripts/s6_dispatch.py 합성 시험 (2026-11-10). ssh와 GPU를 쓰지 않는다. node는 가짜 launcher, 결과 폴더는 임시 폴더다.
조건 규칙은 src의 s6_common을 그대로 읽는다(불러오는 데 1~2분 걸린다).
시험: 의존 순서, 다시 켤 때 중복 없음, 실패 뒤 한 번만 다시 띄움, 동결 확인 거부, node 비었는지 읽기, 긴 stream의 sbatch 경로(가짜 sbatch, sacct)와 청구 상한.
사용: s6_dispatch_tests.py
"""
import importlib.util
import sys as _sys
_sys.dont_write_bytecode = True  # scripts, src에 __pycache__를 남기지 않는다
import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("s6_dispatch", REPO / "scripts" / "s6_dispatch.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
S = D.load_rules(REPO / "src")
NODES = [f"login{i:02d}" for i in range(1, 9)]
FREEZE = "c0ffee"


class FakeRemote:
    """가짜 node. probe는 진짜 ssh 출력과 같은 꼴의 글을 만들어 D.parse_probe로 읽는다."""

    def __init__(self, nodes=NODES):
        self.gpu = {n: 0 for n in nodes}
        self.procs = {n: [] for n in nodes}
        self.unreachable = set()
        self.next_pid = 1000
        self.launches = []
        self.submits = []
        self.jobs = {}

    def probe(self, node):
        if node in self.unreachable:
            return None
        text = "  1) gcc-native/14 => gcc-native/12\n" + D.GPU_MARK + "\n" + f"{self.gpu[node]} MiB\n" + D.PS_MARK + "\n" + "".join(f" {p} {a}\n" for p, a in self.procs[node])
        return D.parse_probe(text)

    def launch(self, node, command):
        args = command.split("nohup ", 1)[1].split(" > ", 1)[0].replace("'", "")
        pid = self.next_pid
        self.next_pid += 1
        self.procs[node].append((pid, args))
        self.gpu[node] = 300  # 자료를 읽는 동안은 GPU 메모리가 작다. 그래도 프로세스가 있어 바쁜 node로 보아야 한다
        self.launches.append(dict(node=node, pid=pid, conditions=args.split()[3].split(","), fold=int(args.split()[2].replace("outer_fold", "")), command=command))
        return pid

    def sbatch(self, args, cwd, env):
        jid = str(5000 + len(self.submits))
        name = next(x.split("=", 1)[1] for x in args if x.startswith("--job-name="))
        self.submits.append(dict(job=jid, args=args, cwd=Path(cwd), env=env, name=name))
        self.jobs[jid] = dict(name=name, state="PENDING", elapsed_s=0, limit_min=720)
        return jid, ""

    def sacct(self, ids=(), name=None):
        """진짜 sacct -X -n -P -o JobID,JobName,State,ElapsedRaw,TimelimitRaw와 같은 꼴의 글을 만들어 D.parse_sacct로 읽는다."""
        pick = [j for j in self.jobs if (j in ids if ids else self.jobs[j]["name"] == name)]
        return D.parse_sacct("".join(f"{j}|{self.jobs[j]['name']}|{self.jobs[j]['state']}|{self.jobs[j]['elapsed_s']}|{self.jobs[j]['limit_min']}\n" for j in pick))

    def kill(self, pid):
        for n in self.procs:
            self.procs[n] = [(p, a) for p, a in self.procs[n] if p != pid]
            if not self.procs[n]:
                self.gpu[n] = 0


def fake_git_ok(root, *args):
    if args[0] == "rev-parse":
        return FREEZE * 6
    return ""


class Env:
    def __init__(self, folds=(1,), conditions=D.MAIN_CONDITIONS, k=((64, 0.1), (64, 1.0))):
        self.tmp = Path(tempfile.mkdtemp(prefix="s6_dispatch_tests_"))
        cfg = self.tmp / "cfg.json"
        cfg.write_text(json.dumps(dict(k_candidates=[list(x) for x in k], learning_rates=[1e-4], seeds=[0], tokenizer="linear")))
        self.run_root = self.tmp / "run"
        for rel in ("configs/env.sh", "configs/paths.yaml", "scripts/s6_train.sh", "scripts/_env.sh"):
            (self.run_root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.run_root / rel).write_text("")
        self.variants = [D.Variant("linear", cfg.resolve(), self.tmp / "out" / "s6_brain")]
        self.table = D.subset_streams(tuple(conditions))
        self.plan = D.build_plan(self.variants, list(folds), S, self.table, tuple(conditions))
        self.remote = FakeRemote()
        self.now = [1.8e9]
        self.msgs = []

    def dispatcher(self, freeze=FREEZE, git=fake_git_ok, **kw):
        kw.setdefault("sbatch_cap_gpu_h", 0.0)  # sbatch 시험(t_sbatch_routing) 밖에서는 login node만 쓴다
        return D.Dispatcher(self.plan, S, **kw,
                            state_path=self.tmp / "logs" / "s6_dispatch_state_t.tsv", run_root=self.run_root, freeze=freeze, nodes=NODES, remote=self.remote,
                            log_dir=self.tmp / "logs" / "d", grace_s=600, clock=lambda: self.now[0], git=git, say=self.msgs.append)

    def root(self, fold=1):
        return self.variants[0].s6_out / f"outer_fold{fold}"

    def finish(self, cond, fold=1, outputs=True):
        """조건 하나가 끝난 것처럼 결과 폴더를 만든다. outputs=False면 selected.json만 있다(save_outputs 전)."""
        folder = self.root(fold) / cond
        rel = f"{cond}/cand_seed0"
        (self.root(fold) / rel).mkdir(parents=True, exist_ok=True)
        (folder / "selected.json").write_text(json.dumps(dict(run_key="K", condition=cond, seeds={"0": rel})))
        if outputs:
            marker = "ensemble" if S.CONDITIONS[cond].paired else "outputs"
            (self.root(fold) / rel / marker).mkdir(exist_ok=True)
            (self.root(fold) / rel / marker / "done.json").write_text("{}")

    def stream(self, launch):
        return next(st for st in self.plan if st.fold == launch["fold"] and set(launch["conditions"]) <= set(st.conditions))


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def t_dependency_rules():
    """S의 표에서 다시 만든 의존이 s6_train의 읽기와 같고, 위험한 stream 표는 거부한다."""
    expect = dict(brain_only=set(), brain_only_distill={"brain_only"}, brain_only_featdec={"brain_only"}, brain_decoded_distill={"brain_only", "brain_decoded"},
                  brain_decoded_pool={"brain_decoded"}, brain_only_pool={"brain_only"}, brain_only_repr_frozen={"brain_only", "multimodal"},
                  brain_frozen_feature_encoder={"brain_only", "feature_encoder"}, brain_decoded_sep_distill={"brain_only", "brain_decoded_sep", "feature_encoder"},
                  brain_features_only_paired={"brain_only", "feature_encoder"}, feature_encoder={"brain_only"}, multimodal={"brain_only"})
    for name, deps in expect.items():
        check(D.condition_deps(name, S) == deps, f"{name}: {D.condition_deps(name, S)} != {deps}")
    D.check_streams(D.STREAMS, D.MAIN_CONDITIONS, S)
    bad = {k: list(v) for k, v in D.STREAMS.items()}
    bad["separate_encoder"].remove("brain_features_only")
    bad["decoded"].append("brain_features_only")
    try:
        D.check_streams(bad, D.MAIN_CONDITIONS, S)
        raise AssertionError("fold 밖 encoder 2를 두 stream이 쓰는데 통과했다")
    except ValueError as e:
        check("fold 밖 encoder 2" in str(e), str(e))
    bad = {k: list(v) for k, v in D.STREAMS.items()}
    bad["multimodal"].remove("control_stimulus_shuffle")
    bad["brain_only"].append("control_stimulus_shuffle")
    try:
        D.check_streams(bad, D.MAIN_CONDITIONS, S)
        raise AssertionError("Stimulus 조건이 없는 stream이 통과했다")
    except ValueError as e:
        check("run_key" in str(e), str(e))
    sub = tuple(c for c in D.MAIN_CONDITIONS if c != "brain_decoded")
    try:
        D.build_plan(Env().variants, [1], S, D.subset_streams(sub), sub)
        raise AssertionError("앞 조건이 빠진 부분 목록이 통과했다")
    except ValueError as e:
        check("brain_decoded" in str(e) and "--conditions" in str(e), str(e))
    env = Env()
    per_fold = sum(st.total for st in env.plan)
    check(per_fold == sum(S.planned_runs(2, 1, 1).values()) + S.N_PAIRS, f"학습 횟수 {per_fold}")


def t_dependency_order():
    """처음에는 brain_only stream만 뜨고, 그 selected.json이 생긴 뒤 같은 fold의 나머지가 우선순위대로 뜬다. 띄울 때마다 앞 조건이 있어야 한다."""
    env = Env(folds=(1, 2))
    d = env.dispatcher()
    seen = 0

    def new_launches():
        nonlocal seen
        out = env.remote.launches[seen:]
        seen = len(env.remote.launches)
        for x in out:
            st = env.stream(x)
            for dep in st.deps:
                check(D.condition_state(st.root, dep, S) != "none", f"{st.key}를 {dep} 전에 띄웠다")
        return out

    check(d.step(), "할 일이 남았는데 끝났다")
    first = new_launches()
    check(sorted((x["fold"], env.stream(x).name) for x in first) == [(1, "brain_only"), (2, "brain_only")], f"첫 실행: {first}")
    check(first[0]["conditions"][0] == "brain_only", "brain_only가 맨 앞이 아니다")
    d.step()
    check(new_launches() == [], "앞 조건 없이 더 띄웠다")
    env.finish("brain_only", fold=1, outputs=False)  # selected.json만 있어도 뒤 stream을 연다
    d.step()
    nxt = new_launches()
    check([env.stream(x).name for x in nxt] == ["separate_encoder", "decoded", "multimodal"] and all(x["fold"] == 1 for x in nxt), f"둘째 실행: {[(x['fold'], env.stream(x).name) for x in nxt]}")
    nodes = [x["node"] for x in env.remote.launches]
    check(len(nodes) == len(set(nodes)), "한 node에 둘을 띄웠다")


def t_restart_no_duplicate():
    env = Env()
    d = env.dispatcher()
    d.step()
    check(len(env.remote.launches) == 1, "brain_only stream 하나만 떠야 한다")
    d2 = env.dispatcher()  # 다시 켬
    d2.step()
    check(len(env.remote.launches) == 1, "다시 켠 뒤 같은 stream을 또 띄웠다")
    # ssh는 되었는데 pid를 적기 전에 dispatcher가 죽은 경우
    rows = D.State(d2.state.path)
    rows.rows[-1]["pid"], rows.rows[-1]["status"] = "", "launching"
    rows.save()
    d3 = env.dispatcher()
    d3.step()
    check(len(env.remote.launches) == 1, "pid 없는 launching 줄을 다시 띄웠다")
    check(D.State(d3.state.path).rows[-1]["status"] == "running", "돌고 있는 프로세스를 찾지 못했다")
    try:
        env.dispatcher(freeze="other")
        raise AssertionError("다른 동결 커밋으로 같은 tag를 이었다")
    except SystemExit as e:
        check("처음 켰을 때" in str(e), str(e))


def t_failure_relaunch_once():
    env = Env()
    d = env.dispatcher()
    d.step()
    first = env.remote.launches[0]
    env.remote.kill(first["pid"])
    d.step()  # log가 아직 새것이다(grace 안). 실패로 보지 않는다
    check(D.State(d.state.path).rows[-1]["status"] == "running", "grace 안에서 실패로 봤다")
    env.now[0] += 601
    d.step()
    rows = D.State(d.state.path).rows
    check([r["status"] for r in rows] == ["failed", "running"], f"상태 {[r['status'] for r in rows]}")
    second = env.remote.launches[1]
    check(second["node"] != first["node"], "실패한 node에 다시 띄웠다")
    env.remote.kill(second["pid"])
    env.now[0] += 601
    more = d.step()
    check(len(env.remote.launches) == 2, "두 번 실패한 stream을 또 띄웠다")
    check(not more and any("2번 실패" in m for m in env.msgs), "멈춘 이유를 알리지 않았다")
    # 끝난 조건은 빼고 다시 띄우되 Stimulus 운반 조건은 남긴다
    env2 = Env()
    env2.finish("brain_only")
    env2.finish("brain_only_distill")
    st = next(s for s in env2.plan if s.name == "brain_only")
    check(D.launch_conditions(st, S) == ("brain_only_distill", "control_label_smoothing", "brain_only_pool"), f"{D.launch_conditions(st, S)}")
    # 프로세스가 사라졌고 모두 끝났으면 done
    d2 = env2.dispatcher()
    d2.step()
    launched = next(x for x in env2.remote.launches if env2.stream(x).name == "brain_only")
    for c in st.conditions:
        env2.finish(c)
    env2.remote.kill(launched["pid"])
    d2.step()
    row = next(r for r in D.State(d2.state.path).rows if r["stream"] == "brain_only")
    check(row["status"] == "done", f"끝난 stream 상태 {row['status']}")


def t_freeze_refusal():
    tmp = Path(tempfile.mkdtemp(prefix="s6_dispatch_git_"))
    g = ["git", "-C", str(tmp), "-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run(["git", "init", "-q", str(tmp)], check=True)
    for rel in ("src/a.py", "configs/env.sh", "configs/paths.yaml", "scripts/s6_train.sh", "scripts/_env.sh"):
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp / rel).write_text("x = 1\n")
    subprocess.run(g + ["add", "."], check=True)
    subprocess.run(g + ["commit", "-q", "-m", "a"], check=True)
    first = subprocess.run(["git", "-C", str(tmp), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    D.check_freeze(tmp, first)
    (tmp / "README").write_text("b")
    subprocess.run(g + ["add", "README"], check=True)
    subprocess.run(g + ["commit", "-q", "-m", "b"], check=True)
    for label, act in (("다른 커밋", lambda: None), ("src 변경", lambda: (tmp / "src" / "a.py").write_text("x = 2\n")), ("src 새 파일", lambda: (tmp / "src" / "b.py").write_text(""))):
        act()
        try:
            D.check_freeze(tmp, first if label == "다른 커밋" else "HEAD")
            raise AssertionError(f"{label}인데 통과했다")
        except D.FreezeError:
            pass
        subprocess.run(["git", "-C", str(tmp), "checkout", "-q", "--", "src"], check=True)
        (tmp / "src" / "b.py").unlink(missing_ok=True)
    D.check_freeze(tmp, "HEAD")
    env = Env()
    d = env.dispatcher(git=lambda root, *a: "aaa" if a[:2] == ("rev-parse", "HEAD") else ("bbb" if a[0] == "rev-parse" else ""))
    try:
        d.step()
        raise AssertionError("HEAD가 동결 커밋과 다른데 띄웠다")
    except D.FreezeError:
        pass
    check(env.remote.launches == [], "거부했는데 띄웠다")
    check(D.State(d.state.path).rows == [], "거부했는데 상태 표에 적었다")


def t_node_parsing():
    noise = "  1) gcc-native/14 => gcc-native/12\nLmod is automatically replacing\n"
    p = D.parse_probe(noise + f"{D.GPU_MARK}\n10257 MiB\n{D.PS_MARK}\n 12 -bash\n 99 sshd: sjmoon@notty\n")
    check(p.gpus == [10257] and D.free_gpu(p, 2000) is None, "10257 MiB를 비었다고 봤다")
    p = D.parse_probe(f"{D.GPU_MARK}\n1999 MiB\n{D.PS_MARK}\n")
    check(D.free_gpu(p, 2000) == 0, "1999 MiB를 바쁘다고 봤다")
    check(D.free_gpu(D.parse_probe(f"{D.GPU_MARK}\n2000 MiB\n{D.PS_MARK}\n"), 2000) is None, "2000 MiB를 비었다고 봤다")
    check(D.free_gpu(D.parse_probe(f"{D.GPU_MARK}\n40000 MiB\n3 MiB\n{D.PS_MARK}\n"), 2000) == 1, "두 번째 GPU를 찾지 못했다")
    p = D.parse_probe(f"{D.GPU_MARK}\n5 MiB\n{D.PS_MARK}\n 777 /env/bin/python s6_train.py --plan outer_fold3 --conditions brain_only --config /c.json\n")
    check(D.free_gpu(p, 2000) is None, "s6_train이 도는 node를 비었다고 봤다")
    p = D.parse_probe(f"{D.GPU_MARK}\n5 MiB\n{D.PS_MARK}\n 778 bash scripts/s6_train.sh outer_fold3 brain_only /c.json abc\n")
    check(D.free_gpu(p, 2000) is None, "s6_train.sh 단계의 node를 비었다고 봤다")
    p = D.parse_probe(f"{D.GPU_MARK}\nNo devices were found\n{D.PS_MARK}\n")
    check(p is not None and D.free_gpu(p, 2000) is None, "nvidia-smi 오류를 비었다고 봤다")
    check(D.parse_probe(noise + "ssh: connect to host login99 port 22: Connection refused\n") is None, "표시 없는 출력을 읽었다")
    check(D.parse_nodes("01-03,login07,10") == ["login01", "login02", "login03", "login07", "login10"], "node 목록")
    env = Env()
    st = env.plan[0]
    cmd = D.launch_command(env.run_root, st, st.conditions, 0, FREEZE, env.tmp / "x.log")
    for part in (f"cd {env.run_root}", f"S6_OUT={st.s6_out}", "CUDA_VISIBLE_DEVICES=0", "nohup bash scripts/s6_train.sh outer_fold1", "< /dev/null &", D.PID_MARK):
        check(part in cmd, f"명령에 {part}가 없다: {cmd}")


def t_sbatch_routing():
    """어림이 3시간보다 긴 stream은 바로 sbatch, 짧은 stream은 login node. 청구 상한을 넘으면 긴 stream도 login node를 기다린다. 다시 켜도 또 내지 않는다."""
    env = Env(folds=(1, 2))
    for n in NODES:
        env.remote.gpu[n] = 30000  # 다른 사람이 모든 login node GPU를 쓴다
    kw = dict(long_h=3.0, sbatch_cap_gpu_h=45.0)  # 11/13. 시간 상한이 48시간으로 바뀌어 sep 상한이 약 27시간(26:58)이다. 두 job이 들어가고 그다음은 상한을 넘는 구성을 유지
    by = {(s.fold, s.name): s for s in env.plan}
    sep, dec = by[(1, "separate_encoder")], by[(1, "decoded")]
    # 학습 횟수(k 2, learning rate 1, seed 1) x 분: encoder 2 1x25 + fold 밖 4x25 + D-4 4x18 + D-1 8x20 + D-2 2x21 + D-3 5x10 + D-3 짝 20x18
    check(abs(D.estimate_hours(sep, sep.conditions, D.MINUTES) - 809 / 60) < 1e-9, f"separate_encoder 어림 {D.estimate_hours(sep, sep.conditions, D.MINUTES)}")
    check(abs(D.estimate_hours(dec, dec.conditions, D.MINUTES) - 25 * 18 / 60) < 1e-9, "decoded 어림")
    check(D.sbatch_limit(809 / 60)[1] == "26:58:00" and D.sbatch_limit(30)[1] == "48:00:00" and D.sbatch_limit(7.5)[1] == "15:00:00" and D.sbatch_limit(0.5)[1] == "02:00:00" and D.sbatch_limit(4.2)[1] == "08:24:00", "시간 상한")
    d = env.dispatcher(**kw)
    d.step()
    check(env.remote.submits == [] and env.remote.launches == [], "짧은 brain_only stream을 sbatch로 냈다")
    env.remote.gpu["login01"] = 0
    d.step()
    check([(x["fold"], env.stream(x).name, x["node"]) for x in env.remote.launches] == [(1, "brain_only", "login01")], f"{env.remote.launches}")
    env.finish("brain_only", fold=1, outputs=False)
    env.remote.gpu["login02"] = 0
    d.step()
    check([(x["fold"], env.stream(x).name, x["node"]) for x in env.remote.launches][1:] == [(2, "brain_only", "login02")], "fold 2 brain_only가 login02에 떠야 한다")
    names = [s["name"] for s in env.remote.submits]
    check(names == ["s6d_t_linear_f1_separate_encoder_t1", "s6d_t_linear_f1_decoded_t1"], f"sbatch {names}")
    times = [next(x for x in s["args"] if x.startswith("--time=")) for s in env.remote.submits]
    check(times == ["--time=26:58:00", "--time=15:00:00"], f"{times}")  # 11/13. 상한 48시간
    sub = env.remote.submits[0]
    for part in ("--account=m5187_g", "--constraint=gpu", "--qos=shared", "--gpus=1", "--cpus-per-task=32", f"--chdir={env.run_root}"):
        check(part in sub["args"], f"sbatch 인자에 {part}가 없다: {sub['args']}")
    wrap = next(x for x in sub["args"] if x.startswith("--wrap="))
    check("bash scripts/s6_train.sh outer_fold1 feature_encoder," in wrap and FREEZE in wrap, wrap)
    check(sub["cwd"] == env.run_root and sub["env"]["S6_OUT"] == str(env.variants[0].s6_out) and "CUDA_VISIBLE_DEVICES" not in sub["env"], "sbatch 환경")
    check(any(x.startswith("--output=") and str(env.tmp / "logs") in x for x in sub["args"]), "log가 output_root/logs 아래가 아니다")
    check(abs(d.sbatch_hours()[1] - (1618 / 60 + 15)) < 1e-3, f"상한 계산 {d.sbatch_hours()}")  # sbatch_hours는 소수 셋째 자리로 반올림한다
    # fold 2의 긴 stream: 42.0 + 27.0 > 45라 login node를 기다린다. login03이 비면 거기에 띄운다
    env.finish("brain_only", fold=2, outputs=False)
    d.step()
    check(len(env.remote.submits) == 2 and any("sbatch 상한" in m for m in env.msgs), "상한을 넘겨 냈거나 알리지 않았다")
    env.remote.gpu["login03"] = 0
    d.step()
    check((2, "separate_encoder", "login03") in [(x["fold"], env.stream(x).name, x["node"]) for x in env.remote.launches], "상한에 걸린 긴 stream을 login node에 띄우지 않았다")
    d2 = env.dispatcher(**kw)  # 다시 켬
    d2.step()
    check(len(env.remote.submits) == 2, "다시 켠 뒤 같은 job을 또 냈다")
    # 첫 job이 5시간 만에 끝나면 상한 계산이 5 + 15 = 20이 되어(상한 45) fold 2의 decoded(15)를 낸다
    for c in sep.conditions:
        env.finish(c, fold=1)
    env.remote.jobs[env.remote.submits[0]["job"]].update(state="COMPLETED", elapsed_s=5 * 3600)
    d2.step()
    row = D.State(d2.state.path).rows
    first = next(r for r in row if r["job_id"] == env.remote.submits[0]["job"])
    check(first["status"] == "done" and abs(float(first["gpu_h"]) - 5.0) < 1e-6 and first["backend"] == "sbatch", f"끝난 job {first}")
    check([s["name"] for s in env.remote.submits][2:] == ["s6d_t_linear_f2_decoded_t1"], f"{[s['name'] for s in env.remote.submits]}")
    check(abs(d2.sbatch_hours()[0] - 5.0) < 1e-6 and abs(d2.sbatch_hours()[1] - 35.0) < 1e-6, f"청구 계산 {d2.sbatch_hours()}")
    # 둘째 job이 TIMEOUT으로 끝나고 조건이 남으면 실패. 다시 띄워야 하지만 5 + 15 + 15 + 15 > 45라 login node를 기다린다
    env.remote.jobs[env.remote.submits[1]["job"]].update(state="TIMEOUT", elapsed_s=15 * 3600)
    d2.step()
    rows = D.State(d2.state.path).rows
    tr = next(r for r in rows if r["job_id"] == env.remote.submits[1]["job"])
    check(tr["status"] == "failed" and "TIMEOUT" in tr["note"], f"TIMEOUT 줄 {tr}")
    check(len(env.remote.submits) == 3, "상한을 넘겨 다시 냈다")
    check(not hasattr(env.remote, "scancel") and not hasattr(D.Remote, "scancel"), "job을 취소하는 경로가 있다")


def t_sbatch_parsing():
    z = D.parse_sacct("123|s6d_p1_linear_f1_brain_only_t1|CANCELLED by 999|3600|720\n124|x|RUNNING|60|Partition_Limit\n\n")
    check(z["123"]["state"] == "CANCELLED" and z["123"]["elapsed_s"] == 3600 and z["123"]["limit_min"] == 720, f"{z}")
    check(z["124"]["limit_min"] is None, f"{z}")
    check(D.hours_of("12:00:00") == 12 and D.hours_of("1-06:30:00") == 30.5 and D.hours_of("30:00") == 0.5, "시간 상한 읽기")


TESTS = [t_dependency_rules, t_dependency_order, t_restart_no_duplicate, t_failure_relaunch_once, t_freeze_refusal, t_node_parsing, t_sbatch_routing, t_sbatch_parsing]


def t_split_decoded():
    """11/13. 장면 특징 줄을 둘로 나눈 표. 8개 조건이면 줄 3개이고 줄마다 운반 조건이 있다. Multimodal Model이 함께 있으면 운반 조건이 없어 멈춘다."""
    eight = ["brain_only", "brain_only_distill", "control_label_smoothing", "brain_only_featdec", "brain_decoded", "brain_decoded_distill", "control_feature_shuffle", "control_stimulus_shuffle"]
    table = D.subset_streams(eight, D.STREAMS_SPLIT_DECODED)
    assert set(table) == {"brain_only", "decoded_aux", "decoded"}, table
    v = D.parse_variant("linear:configs/s6/run_config_grid_main.json:s6_x", REPO, REPO / "outputs")
    plan = D.build_plan([v], [1], S, table, eight)
    assert all(st.carriers for st in plan), [(st.name, st.carriers) for st in plan]
    assert {c for cs in table.values() for c in cs} == set(eight)
    D.check_streams(table, eight, S)
    try:
        D.check_streams(D.subset_streams(eight + ["multimodal"], D.STREAMS_SPLIT_DECODED), eight + ["multimodal"], S)
        raise AssertionError("운반 조건이 없는 줄을 막지 않았다")
    except ValueError:
        pass


def t_grid_groups():
    """11/13. A-1 grid 묶음. 17개 후보를 learning rate별로 묶고 1e-5는 둘로 나눈다. 모든 후보를 한 번씩 덮는다."""
    spec = importlib.util.spec_from_file_location("s6_grid", REPO / "scripts" / "s6_grid.py")
    G = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(G)
    config = S.load_config(REPO / "configs/s6/run_config_grid_main.json")
    groups = G.make_groups(S, config, {1e-5: 2})
    sizes = [(g["lr"], len(g["ids"])) for g in groups]
    assert sizes == [(1e-5, 3), (1e-5, 3), (1e-4, 6), (1e-3, 5)], sizes
    assert 1000.0 not in groups[3]["wds"]


def t_target_mode():
    """11/14. A-1 밖 조건의 후보 나누기. 그 fold의 A-1 선택으로 후보를 만들고, C-2처럼 다른 선택을 읽는 조건과 잘못된 번호는 막는다."""
    spec = importlib.util.spec_from_file_location("s6_grid", REPO / "scripts" / "s6_grid.py")
    G = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(G)
    spec2 = importlib.util.spec_from_file_location("s6_candidates", REPO / "scripts" / "s6_candidates.py")
    W = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(W)
    config = S.load_config(REPO / "configs/s6/run_config_grid_main.json")
    base = [c for c in S.candidates("brain_only", k_candidates=config.k_candidates, learning_rates=config.learning_rates) if c["lr"] == 1e-3 and c["input_wd"] == 100.0][0]
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "outer_fold1" / "brain_only"
        d.mkdir(parents=True)
        (d / "selected.json").write_text(json.dumps(dict(candidate=base)))
        groups = G.target_groups(S, config, td, 1, {"brain_decoded": 2, "brain_only_featdec": 2, "control_feature_shuffle": 2, "control_stimulus_shuffle": 2})
    assert [(g["cond"], len(g["ids"])) for g in groups] == [("brain_decoded", 2)] * 4 + [("brain_only_featdec", 2), ("control_feature_shuffle", 2), ("control_stimulus_shuffle", 2)], groups
    c1 = [S.candidate_id(c) for c in S.candidates("brain_decoded", k_candidates=config.k_candidates, base=base, learning_rates=config.learning_rates, lr_follows_brain_only=True)]
    assert sorted(i for g in groups if g["cond"] == "brain_decoded" for i in g["ids"]) == sorted(c1)
    picked = W.pick("brain_decoded", c1[:2], config, base)
    assert [S.candidate_id(c) for c in picked] == c1[:2] and all(c["lr"] == 1e-3 and c["input_wd"] == 100.0 for c in picked)
    for bad in ("brain_decoded_distill:x", "brain_decoded:", "brain_decoded:a,a", "brain_only:x"):
        try:
            W.parse_target(bad)
            raise AssertionError(f"{bad}를 막지 않았다")
        except SystemExit:
            pass
    try:
        W.pick("brain_decoded", ["없는번호"], config, base)
        raise AssertionError("없는 후보 번호를 막지 않았다")
    except SystemExit:
        pass


TESTS += [t_split_decoded, t_grid_groups, t_target_mode]


def main():
    failed = 0
    for t in TESTS:
        try:
            t()
            print("통과", t.__name__, flush=True)
        except Exception:
            failed += 1
            print("실패", t.__name__, flush=True)
            traceback.print_exc()
    print(f"{len(TESTS) - failed}/{len(TESTS)} 통과")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
