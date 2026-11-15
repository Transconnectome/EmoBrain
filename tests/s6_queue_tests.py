#!/usr/bin/env python3
"""scripts/s6_queue.py 합성 시험 (2026-11-15). ssh와 GPU를 쓰지 않는다. node는 가짜, 결과 폴더는 임시 폴더다.
시험: 작업 목록 확인(24시간, run worktree 밖 설정, 겹침), 빈 node에만 하나씩 띄움, 끝남 판정, 사라진 작업은 한 번만 다시 띄움, 상태가 남은 작업 수.
사용: s6_queue_tests.py
"""
import sys as _sys
_sys.dont_write_bytecode = True
import importlib.util
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("s6_queue", REPO / "scripts" / "s6_queue.py")
Q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Q)
D = Q.D
RESULTS = []


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print(("통과 " if ok else "실패 ") + name, flush=True)


class Fake:
    def __init__(self, nodes):
        self.gpu = {n: 0 for n in nodes}
        self.procs = {n: [] for n in nodes}
        self.launches = []
        self.pid = 100

    def probe(self, node):
        text = D.GPU_MARK + "\n" + f"{self.gpu[node]} MiB\n" + D.PS_MARK + "\n" + "".join(f" {p} {a}\n" for p, a in self.procs[node])
        return D.parse_probe(text)

    def launch(self, node, cmd):
        args = cmd.split("nohup ", 1)[1].split(" > ", 1)[0].replace("'", "")
        self.pid += 1
        self.procs[node].append((self.pid, args))
        self.launches.append((node, args))
        return self.pid

    def end(self, node):
        self.procs[node] = []
        self.gpu[node] = 0


def stops_exit(f):
    try:
        f()
    except SystemExit:
        return True
    return False


def write_jobs(tmp, rows):
    p = tmp / "jobs.tsv"
    p.write_text("\t".join(Q.COLUMNS) + "\n" + "".join("\t".join(str(x) for x in r) + "\n" for r in rows))
    return p


def main():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        run_root = tmp / "run"
        (run_root / "configs").mkdir(parents=True)
        cfg = run_root / "configs" / "a.json"
        cfg.write_text("{}")
        out = tmp / "out" / "s6_x"
        rows = [("zone_1", "zone_block1_fold1_excluded", "brain_only,brain_decoded", cfg, out, 8),
                ("zone_2", "zone_block1_fold1_control", "brain_only,brain_decoded", cfg, out, 8),
                ("net_1", "outer_fold1", "brain_only,brain_decoded", cfg, tmp / "out" / "s6_net", 2)]
        jobs = Q.read_jobs(write_jobs(tmp, rows), run_root)
        check("작업 목록을 읽는다", len(jobs) == 3 and jobs[0]["status"] == "pending")
        for bad, why in ((rows[:1] + [rows[0]], "이름 겹침"), ([rows[0][:5] + (25,)], "24시간 넘음"), ([(rows[0][0], rows[0][1], rows[0][2], tmp / "x.json", out, 8)], "run worktree 밖 설정")):
            try:
                Q.read_jobs(write_jobs(tmp, bad), run_root)
                ok = False
            except SystemExit:
                ok = True
            check(f"작업 목록 오류는 멈춘다({why})", ok)
        fake = Fake(["login01", "login02"])
        log_dir = tmp / "logs"
        left = Q.step(jobs, fake, ["login01", "login02"], run_root, "c0ffee", log_dir, 2000, out=lambda s: None)
        check("빈 node 두 개에 하나씩 띄운다", left == 3 and len(fake.launches) == 2 and {j["status"] for j in jobs[:2]} == {"running"} and jobs[2]["status"] == "pending")
        check("명령은 run worktree의 s6_train.sh에 분할, 조건, 설정, 커밋을 준다", all(f"scripts/s6_train.sh {j['plan']} brain_only,brain_decoded {cfg} c0ffee" in a for j, (_, a) in zip(jobs[:2], fake.launches)))
        Q.step(jobs, fake, ["login01", "login02"], run_root, "c0ffee", log_dir, 2000, out=lambda s: None)
        check("node가 바쁘면 더 띄우지 않는다", len(fake.launches) == 2)
        for c in ("brain_only", "brain_decoded"):  # zone_1을 끝낸다
            (out / jobs[0]["plan"] / c).mkdir(parents=True)
            (out / jobs[0]["plan"] / c / "selected.json").write_text("{}")
        fake.end("login01")
        fake.end("login02")  # zone_2는 끝나지 않고 사라진다
        left = Q.step(jobs, fake, ["login01", "login02"], run_root, "c0ffee", log_dir, 2000, out=lambda s: None)
        check("끝난 작업은 done, 사라진 작업은 다시 띄운다", jobs[0]["status"] == "done" and jobs[1]["status"] == "running" and jobs[1]["attempts"] == 2 and jobs[2]["status"] == "running" and left == 2)
        fake.end("login01")
        fake.end("login02")
        Q.step(jobs, fake, ["login01", "login02"], run_root, "c0ffee", log_dir, 2000, out=lambda s: None)
        check("두 번 실패하면 failed로 두고 더 띄우지 않는다", jobs[1]["status"] == "failed")
        more = Q.read_jobs(write_jobs(tmp, [("z9", "zone_block2_fold1_excluded", "brain_only,brain_decoded", cfg, out, 8)]), run_root)
        fake.end("login01")
        fake.end("login02")

        class Racing(Fake):  # 첫 확인 뒤 다른 실행기가 login01을 잡는다
            def __init__(self, base):
                self.__dict__.update(base.__dict__)
                self.calls = 0

            def probe(self, node):
                self.calls += 1
                if node == "login01" and self.calls > 2:
                    self.procs["login01"] = [(9, "python s6_train.py --plan outer_fold3 --config other.json")]
                return Fake.probe(self, node)
        race = Racing(fake)
        n0 = len(race.launches)
        Q.step(more, race, ["login01", "login02"], run_root, "c0ffee", log_dir, 2000, out=lambda s: None)
        check("띄우기 직전 다시 봐서 다른 실행기가 잡은 node는 건너뛴다", len(race.launches) == n0 + 1 and race.launches[-1][0] == "login02")
        # --share-own: 이 사용자의 다른 s6_train이 있는 node도 메모리가 남으면 쓴다. 같은 작업이 이미 돌면 띄우지 않는다
        own = Fake(["login01", "login02"])
        own.procs["login01"] = [(7, "python s6_train.py --plan outer_fold9 --config other.json")]
        own.gpu["login01"] = 8000
        own.gpu["login02"] = 39000
        sj = Q.read_jobs(write_jobs(tmp, [("s1", "outer_fold1", "brain_decoded_additive", cfg, tmp / "out" / "s6_own", 2), ("s2", "outer_fold2", "brain_decoded_additive", cfg, tmp / "out" / "s6_own", 2)]), run_root)
        Q.step(sj, own, ["login01", "login02"], run_root, "c0ffee", log_dir, 30000, out=lambda s: None)
        check("share_own이 없으면 우리 작업이 있는 node에 띄우지 않는다", len(own.launches) == 0)
        Q.step(sj, own, ["login01", "login02"], run_root, "c0ffee", log_dir, 30000, out=lambda s: None, share_own=True)
        check("share_own이면 메모리가 남는 node에 하나만 띄우고 메모리가 찬 node는 건너뛴다", [n for n, _ in own.launches] == ["login01"] and sj[0]["status"] == "running" and sj[1]["status"] == "pending")
        own2 = Fake(["login03"])
        own2.procs["login03"] = [(8, f"python s6_train.py --plan outer_fold2 --conditions brain_decoded_additive --config {cfg}")]
        sj2 = Q.read_jobs(write_jobs(tmp, [("s2", "outer_fold2", "brain_decoded_additive", cfg, tmp / "out" / "s6_own2", 2)]), run_root)
        Q.step(sj2, own2, ["login03"], run_root, "c0ffee", log_dir, 30000, out=lambda s: None, share_own=True)
        check("share_own이어도 같은 작업이 이미 돌면 띄우지 않는다", len(own2.launches) == 0 and sj2[0]["status"] == "pending")
        own3 = Fake(["login04"])
        own3.procs["login04"] = [(9, f"python s6_train.py --plan outer_fold2 --conditions multimodal,brain_only_repr_frozen --config {cfg}")]
        sj3 = Q.read_jobs(write_jobs(tmp, [("s2", "outer_fold2", "brain_decoded_additive", cfg, tmp / "out" / "s6_own3", 2)]), run_root)
        Q.step(sj3, own3, ["login04"], run_root, "c0ffee", log_dir, 30000, out=lambda s: None, share_own=True)
        check("같은 분할과 설정이라도 조건이 다른 작업은 다른 작업으로 본다", [n for n, _ in own3.launches] == ["login04"])
        # --stack-mib: 한 GPU에 여유만큼 여러 작업. 10GB 쓰는 GPU에 9GB 어림이면 (40GB - 4GB 여유)까지 두 개, 그다음 node로
        from datetime import datetime as _dt
        st = Fake(["login07", "login08"])
        st.gpu["login07"], st.gpu["login08"] = 10000, 30000
        sj4 = Q.read_jobs(write_jobs(tmp, [(f"k{i}", f"outer_fold{i}", "brain_only_pool", cfg, tmp / "out" / "s6_stack", 2) for i in range(1, 5)]), run_root)
        clock = _dt.now(Q.KST)
        Q.step(sj4, st, ["login07", "login08"], run_root, "c0ffee", log_dir, 30000, out=lambda s: None, share_own=True, stack_mib=9000, clock=clock)
        where = [n for n, _ in st.launches]
        check("stack: 여유를 계산해 같은 GPU에 두 개 올리고, 자리가 없는 GPU에는 올리지 않는다", where == ["login07", "login07"] and [j["status"] for j in sj4] == ["running", "running", "pending", "pending"])
        check("stack은 share_own 없이 쓰면 멈춘다", stops_exit(lambda: Q.step(sj4, st, ["login07"], run_root, "c0ffee", log_dir, 30000, out=lambda s: None, stack_mib=9000)))
    bad = [n for n, ok in RESULTS if not ok]
    print("통과", len(RESULTS) - len(bad), "실패", len(bad), bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    import sys
    main()
