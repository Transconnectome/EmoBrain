#!/usr/bin/env python3
"""S6 본실험을 login node GPU와 sbatch job에 나눠 띄우는 dispatcher (2026-11-10).

한 일
- 바깥 fold 6개 x 입력층 변형(--variant)마다 조건을 stream 4개로 나누고, 앞 조건의 selected.json이 생기면 뒤 stream을 빈 login node에 띄운다.
- 실행은 설계 동결 커밋에 맞춘 별도 run worktree(--run-root)에서 scripts/s6_train.sh로 한다. 한 node에 작업 하나다.
- 상태는 <output_root>/logs/s6_dispatch_state_<tag>.tsv에 쓴다. dispatcher를 다시 켜면 이 표를 읽고 이어 간다(같은 stream을 두 번 띄우지 않는다).
- 프로세스가 사라졌는데 조건이 다 끝나지 않았으면 실패로 적고, 다른 node에서 한 번만 다시 띄운다(s6_train은 끝난 학습을 건너뛴다).
- stream마다 GPU 시간을 어림한다(학습 횟수 x 조건별 학습 한 번의 분, --minutes-per-training). 어림이 --long-threshold-hours(기본 3)보다 긴 stream은
  바로 sbatch로 낸다(account m5187_g, constraint gpu, qos shared, GPU 1, CPU 32, 시간 상한 = 어림 x 2, 2~24 h). 나머지는 빈 login node를 기다린다.
  sbatch job도 같은 wrapper(scripts/s6_train.sh)를 run worktree에서 돌린다. sbatch는 run worktree를 현재 폴더로 해서 부르므로
  SLURM_SUBMIT_DIR이 run worktree가 된다(_env.sh의 ROOT).
- 이 dispatcher가 낸 job의 청구 GPU 시간은 sacct의 ElapsedRaw로 상태 표에 적는다. 상한 계산에서 끝난 job은 Elapsed, 도는 job과 기다리는 job은
  시간 상한 전체로 센다. 새 job을 더해 --sbatch-gpu-hours-cap(기본 160 GPU-h)을 넘으면 그 긴 stream도 login node를 기다린다. shared QOS는 GPU 1시간을 node 1/4시간으로
  청구하므로 요약에는 GPU-h와 node-h를 함께 적는다. job은 취소하지 않는다. sbatch job도 끝난 상태인데 조건이 남았으면 실패로 보고 한 번 다시 띄운다.

조건 사이의 의존 (한 바깥 fold 안. 줄 번호는 2026-11-10 작업 사본의 src 기준이고 함수 이름을 함께 적는다)
- brain_only(A-1)가 맨 앞이다. brain_only가 아닌 조건은 모두 그 fold의 brain_only selected.json에서 d와 입력층 weight decay를 이어 받는다
  (s6_train.py 498 FoldRunner.run_condition의 base, 595 _run_paired, s6_common.py 185-189 candidates).
- pooling판은 표준 실행의 선택을 그대로 쓴다. brain_only_pool은 brain_only, brain_decoded_pool은 brain_decoded (s6_common.py 106 POOLED, s6_train.py 620 _run_pooled).
- C-2는 C-1, D-2는 D-1의 λ와 r을 이어 받는다 (s6_common.py 104 DECODED_SOURCE, s6_train.py 499).
- A-2, B-1, C-2, D-2의 0 후보는 앞 조건의 학습 행이다 (s6_common.py 107 ZERO_SOURCE, s6_train.py 503-505). A-2와 B-1은 brain_only, C-2는 C-1, D-2는 D-1.
- E-고정, E-학습은 multimodal의 고른 모델을 teacher로 읽는다 (s6_train.py 330-334 teacher, 417).
- D 묶음(D-1, D-2, D-3, D-3 짝, D-4)은 feature_encoder의 고른 모델(s6_train.py 336-344 feature_encoder, 422)과
  그 learning rate로 학습하는 fold 밖 encoder 2 넷(s6_train.py 352-397 oof, 358, 431, 556 _pairs)을 쓴다.
- 의존 조건은 모두 S.ORDER에서 앞에 있다. s6_train.main은 받은 조건을 S.ORDER 순서로 돈다 (s6_train.py 809-811, s6_common.py 101).
- 앞 조건의 selected.json이 없거나 실행 번호(run_key)가 다르면 s6_train은 그 자리에서 멈춘다 (s6_train.py 483-490 selected).
condition_deps가 이 규칙을 S의 표(CONDITIONS의 표시, POOLED, DECODED_SOURCE, ZERO_SOURCE)에서 다시 만든다. 손으로 쓴 의존 표는 없다.

같은 fold의 다른 조건 묶음을 동시에 다른 프로세스로 돌릴 때 위험한 점과 이 설계가 피하는 방법
1. 실행 번호가 조건 목록에 따라 달라진다. main은 받은 조건 가운데 Stimulus 예측 평정을 쓰는 조건(A-2, C-2, D-2, Stimulus 예측 섞기 대조군)이
   하나라도 있을 때만 Stimulus 파일을 입력 해시와 설정에 넣는다 (s6_train.py 793, 797, s6_common.py 736-738 needs_stimulus, 760-772 input_paths).
   그래서 brain_only만 돈 프로세스와 A-2를 함께 돈 프로세스는 run_key가 다르고, 뒤 프로세스는 plan/done.json에서 바로 멈춘다
   (s6_train.py 313-316 write_plan, s4_common.py 196-203 done_or_new). 같은 fold의 모든 stream이 같은 run_key를 갖도록
   stream마다 Stimulus를 쓰는 조건을 하나 이상 넣는다(check_streams가 확인). 그런 조건은 넷뿐이라 fold당 stream은 4개까지다.
   다시 띄울 때 끝난 조건을 목록에서 빼더라도 그 stream의 Stimulus 조건 하나(운반 조건)는 남긴다(launch_conditions). 끝난 운반 조건은
   학습 없이 selected.json을 같은 내용으로 다시 쓴다(s6_train.py 411-412, 630-636). 운반 조건은 다른 조건이 읽지 않는 조건으로만 고른다.
   --design-freeze 문자열도 run_key에 들어가므로 dispatcher는 --freeze를 받은 그대로 넘기고, 다시 켤 때 다른 값이면 멈춘다.
2. fold 밖 encoder 2 캐시가 공유된다. oof(seed)는 끝난 기록이 없으면 feature_encoder_oof/seed<s>/inner<j>를 학습하고 Atomic으로 옮긴다(s6_train.py 365-383).
   두 프로세스가 같은 seed를 동시에 부르면 같은 학습을 두 번 하고, Atomic의 지우고 옮기기(s4_common.py 206-225)가 겹쳐 읽는 쪽이 파일을 잃거나
   비어 있지 않은 폴더 위로 옮기다 멈춘다. 그래서 oof를 부르는 조건(D-1, D-2, D-3, D-3 짝, D-4)은 feature_encoder와 함께 한 stream에 둔다.
3. plan/ 폴더는 FoldRunner를 만들 때마다 확인하고 없으면 쓴다(s6_train.py 313-322). brain_only stream이 fold마다 혼자 먼저 돌아 plan을 만들고,
   나머지 stream은 brain_only의 selected.json이 생긴 뒤에 띄우므로 plan을 동시에 쓰지 않는다.
4. selected.json은 Atomic이 아니라 바로 쓴다(s6_train.py 294-295, 636). dispatcher는 JSON으로 읽히고 run_key가 있을 때만 끝난 것으로 본다.
   selected.json은 _prune과 save_outputs보다 먼저 쓰이므로(s6_train.py 517-521), 조건이 끝났다는 판정은 selected.json의 seed 폴더마다
   outputs/done.json(짝 조건은 ensemble/done.json, s6_train.py 576, 608)까지 있을 때로 한다. 뒤 stream은 selected.json만 있으면 띄운다.
5. 조건마다 결과 폴더(<조건>/<후보>_seed<s>)가 따로이고 Atomic의 임시 폴더 이름은 mkdtemp라 서로 다른 조건끼리는 겹치지 않는다.
   teacher, encoder 2, shuffle은 읽기만 하거나 프로세스 안에서 만든다(s6_train.py 324-344). 그래서 위 1, 2만 지키면 다른 stream은 함께 돌아도 된다.

stream (fold와 변형마다)
- brain_only: A-1, A-2, A-2 대조군(label smoothing), A-1 평균 pooling판. A-1의 선택이 나머지를 모두 연다
- decoded: B-1, C-1, C-1 더하기 head, C-1 손실 흐름 허용판, C-2, B-1 대조군(feature 짝 섞기), C-1 평균 pooling판
- separate_encoder: encoder 2, D-4, D-1, D-2, D-3, D-3 짝 (fold 밖 encoder 2 넷 x seed 수 포함)
- multimodal: Multimodal Model, E-고정, E-학습, A-2 대조군(Stimulus 예측 섞기)
우선순위: 뒤 stream을 가장 많이 여는 것(brain_only stream) 먼저, 그다음 학습 횟수가 많은 stream 먼저, 같으면 변형 순서와 fold 순서.

사용: s6_dispatch.py --tag main --run-root <run worktree> --freeze <동결 커밋> --variant linear:configs/s6/run_config.json:s6_brain [--variant ...] [--conditions a,b,...] [--dry-run]
--conditions로 일부 조건만 돌리면 위 stream 표에서 그 조건만 남기고 빈 stream은 뺀다. 남긴 조건이 읽는 앞 조건이 빠져 있으면 멈춘다.
"""
import argparse
import fcntl
import getpass
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[1]
KST = ZoneInfo("Asia/Seoul")
DEFAULT_MINUTES = 18.0  # 어림용. 학습 한 번의 GPU 시간(분). --minutes-per-training으로 조건마다 바꾼다
MINUTES = {"feature_encoder": 25.0, "brain_decoded_sep": 20.0, "brain_decoded_sep_distill": 21.0, "brain_features_only": 10.0, "brain_only": 18.0}  # fold 밖 encoder 2는 feature_encoder 값
LONG_HOURS = 3.0  # 어림이 이보다 긴 stream은 sbatch로 낸다
# scripts/s6_main.sh의 조건 목록과 같다
MAIN_CONDITIONS = ("brain_only", "brain_only_featdec", "brain_decoded", "brain_decoded_additive", "brain_decoded_grad", "brain_only_distill", "brain_decoded_distill",
                   "feature_encoder", "brain_frozen_feature_encoder", "brain_decoded_sep", "brain_decoded_sep_distill", "brain_features_only", "brain_features_only_paired",
                   "multimodal", "brain_only_repr_frozen", "brain_only_repr_trained", "control_label_smoothing", "control_stimulus_shuffle", "control_feature_shuffle",
                   "brain_only_pool", "brain_decoded_pool")
STREAMS = {
    "brain_only": ("brain_only", "brain_only_distill", "control_label_smoothing", "brain_only_pool"),
    "decoded": ("brain_only_featdec", "brain_decoded", "brain_decoded_additive", "brain_decoded_grad", "brain_decoded_distill", "control_feature_shuffle", "brain_decoded_pool"),
    "separate_encoder": ("feature_encoder", "brain_frozen_feature_encoder", "brain_decoded_sep", "brain_decoded_sep_distill", "brain_features_only", "brain_features_only_paired"),
    "multimodal": ("multimodal", "brain_only_repr_frozen", "brain_only_repr_trained", "control_stimulus_shuffle"),
}
STATE_COLUMNS = ("variant", "fold", "stream", "attempt", "backend", "conditions", "node", "gpu", "pid", "job_id", "launch_kst", "launch_epoch", "log", "status",
                 "slurm_state", "reserved_gpu_h", "gpu_h", "end_kst", "note")
# login node가 오래 비지 않을 때 쓰는 sbatch 설정(scripts/s6_main.sh와 같은 자원)
SBATCH = dict(account="m5187_g", constraint="gpu", qos="shared", ntasks=1, gpus=1, cpus=32)
NODE_H_PER_GPU_H = 0.25  # shared QOS는 GPU 하나를 node의 1/4로 청구한다
SLURM_ACTIVE = {"PENDING", "RUNNING", "CONFIGURING", "COMPLETING", "REQUEUED", "REQUEUE_HOLD", "REQUEUE_FED", "RESIZING", "SUSPENDED", "SIGNALING", "STAGE_OUT"}
ACTIVE = ("launching", "running")
SUBMIT_ERROR = "submit_error"  # sbatch가 job을 받지 않았다. 시도로 세지 않는다
MAX_ATTEMPTS = 2  # 처음 한 번 + 실패 뒤 다시 한 번
GPU_MARK, PS_MARK, PID_MARK = "@@S6D_GPU@@", "@@S6D_PS@@", "@@S6D_PID@@"
S6_PROC = re.compile(r"s6_train\.(py|sh)\b")


class FreezeError(SystemExit):
    """run worktree가 동결 커밋과 다르다. 띄우지 않는다."""


# ---------- 조건 규칙 (S = run worktree의 s6_common) ----------

def load_rules(src):
    """src 폴더의 s6_common을 불러온다. 실제로 돌 코드의 표를 쓰려고 run worktree의 src를 먼저 쓴다."""
    sys.dont_write_bytecode = True  # src에 __pycache__를 남기지 않는다
    sys.path.insert(0, str(src))
    import s6_common
    return s6_common


def uses_oof(cfg):
    """fold 밖 encoder 2를 부르는 조건. (separate 또는 head_only이고 짝이 아님) s6_train.py 431, 짝 조건은 _pairs 556."""
    return bool(cfg.separate or cfg.head_only or cfg.paired)


def condition_deps(name, S):
    """name이 띄워지기 전에 selected.json이 있어야 하는 조건들(모듈 머리말의 의존 규칙)."""
    cfg = S.CONDITIONS[name]
    deps = set()
    if name in S.POOLED:
        deps.add(S.POOLED[name])  # _run_pooled는 원래 조건의 선택만 읽는다(620)
    elif name != "brain_only":
        deps.add("brain_only")  # run_condition 498, _run_paired 595
    if name in S.DECODED_SOURCE:
        deps.add(S.DECODED_SOURCE[name])  # 499
    if name in S.ZERO_SOURCE:
        deps.add(S.ZERO_SOURCE[name][0])  # 504
    if cfg.representation:
        deps.add("multimodal")  # teacher 330-334
    if cfg.separate or cfg.head_only or cfg.frozen_encoder or uses_oof(cfg):
        deps.add("feature_encoder")  # feature_encoder 336-344, oof 358
    order = S.ORDER.index(name)
    for d in deps:
        if S.ORDER.index(d) >= order:
            raise ValueError(f"{name}의 앞 조건 {d}가 S.ORDER에서 뒤에 있다. s6_train이 이 순서로 돌 수 없다")
    return deps


def check_streams(streams, conditions, S):
    """stream 표가 머리말의 1, 2를 지키는지 본다. 어기면 멈춘다."""
    names = [c for cs in streams.values() for c in cs]
    if len(names) != len(set(names)):
        raise ValueError("한 조건이 두 stream에 있다. 같은 결과 폴더를 두 프로세스가 쓰게 된다")
    if set(names) != set(conditions):
        raise ValueError(f"stream 표와 조건 목록이 다르다: 빠짐 {sorted(set(conditions) - set(names))}, 더함 {sorted(set(names) - set(conditions))}")
    for name in names:
        unknown = condition_deps(name, S) - set(conditions)
        if unknown:
            raise ValueError(f"{name}({S.DISPLAY.get(name, name)})은 {sorted(unknown)}의 selected.json을 읽는데 그 조건이 --conditions에 없다. 그 조건을 넣거나 {name}을 뺀다")
    oof = {s for s, cs in streams.items() for c in cs if uses_oof(S.CONDITIONS[c])}
    if len(oof) > 1:
        raise ValueError(f"fold 밖 encoder 2를 부르는 조건이 여러 stream에 있다: {sorted(oof)}. 같은 캐시를 동시에 쓴다")
    if S.needs_stimulus(conditions):
        read_by_others = {d for c in conditions for d in condition_deps(c, S)}
        for s, cs in streams.items():
            if not [c for c in cs if S.needs_stimulus([c]) and c not in read_by_others]:
                raise ValueError(f"stream {s}에 다른 조건이 읽지 않는 Stimulus 조건이 없다. 같은 fold인데 run_key가 달라진다")
    stream_deps(streams, S)  # 순환이 있으면 멈춘다


def stream_deps(streams, S):
    """stream 이름 -> 먼저 selected.json이 있어야 하는 (다른 stream의) 조건들."""
    where = {c: s for s, cs in streams.items() for c in cs}
    out = {s: {d for c in cs for d in condition_deps(c, S) if where[d] != s} for s, cs in streams.items()}
    seen, done = set(), set()

    def visit(s):
        if s in done:
            return
        if s in seen:
            raise ValueError(f"stream 사이에 순환이 있다: {s}")
        seen.add(s)
        for d in out[s]:
            visit(where[d])
        done.add(s)
    for s in streams:
        visit(s)
    return out


def trainings(config, conditions, S):
    """조건마다 학습 횟수(S.planned_runs, k는 config의 k_candidates 수). fold 밖 encoder 2(N_PAIRS x seed 수)는 planned_runs에 없어 따로 센다."""
    k, n_lr, n_seeds = len(config.k_candidates), len(config.learning_rates), len(config.seeds)
    full = S.planned_runs(k, n_lr, n_seeds)
    follow = S.planned_runs(k, 1, n_seeds) if config.lr_follows_brain_only else full
    counts = {c: (full if c == "brain_only" else follow)[c] for c in conditions}
    oof = S.N_PAIRS * n_seeds if any(uses_oof(S.CONDITIONS[c]) for c in conditions) else 0
    return counts, oof


# ---------- 계획 ----------

@dataclass
class Variant:
    name: str
    config: Path  # 절대 경로
    s6_out: Path


@dataclass
class Stream:
    variant: str
    fold: int
    name: str
    conditions: tuple  # S.ORDER 순서
    config: Path
    s6_out: Path
    counts: dict
    oof: int  # 이 stream이 학습하는 fold 밖 encoder 2 수
    deps: set  # 다른 stream의 조건
    priority: tuple = ()
    carriers: tuple = ()  # 다른 조건이 읽지 않는 Stimulus 조건
    oof_conds: frozenset = frozenset()  # 이 stream에서 fold 밖 encoder 2를 부르는 조건

    @property
    def key(self):
        return (self.variant, self.fold, self.name)

    @property
    def root(self):
        return self.s6_out / f"outer_fold{self.fold}"

    @property
    def total(self):
        return sum(self.counts.values()) + self.oof


def subset_streams(conditions, streams=STREAMS):
    """--conditions로 받은 조건만 남긴 stream 표. 빈 stream은 뺀다. 표에 없는 조건 이름은 멈춘다."""
    known = {c for cs in streams.values() for c in cs}
    unknown = [c for c in conditions if c not in known]
    if unknown:
        raise SystemExit(f"stream 표에 없는 조건: {unknown}")
    if len(set(conditions)) != len(conditions):
        raise SystemExit("--conditions에 같은 조건이 두 번 있다")
    table = {s: tuple(c for c in cs if c in conditions) for s, cs in streams.items()}
    return {s: cs for s, cs in table.items() if cs}


def build_plan(variants, folds, S, streams=STREAMS, conditions=MAIN_CONDITIONS):
    check_streams(streams, conditions, S)
    deps = stream_deps(streams, S)
    where = {c: s for s, cs in streams.items() for c in cs}
    read_by_others = {d for c in conditions for d in condition_deps(c, S)}
    plan = []
    for vi, v in enumerate(variants):
        config = S.load_config(v.config)
        counts, oof = trainings(config, conditions, S)
        for fold in folds:
            for name, cs in streams.items():
                ordered = tuple(c for c in S.ORDER if c in cs)
                has_oof = any(uses_oof(S.CONDITIONS[c]) for c in cs)
                carriers = tuple(c for c in ordered if S.needs_stimulus([c]) and c not in read_by_others) if S.needs_stimulus(conditions) else ()
                plan.append(Stream(v.name, fold, name, ordered, v.config, v.s6_out, {c: counts[c] for c in ordered}, oof if has_oof else 0, deps[name], carriers=carriers,
                                   oof_conds=frozenset(c for c in ordered if uses_oof(S.CONDITIONS[c]))))
    # 우선순위: 뒤 stream을 많이 여는 것, 학습이 많은 것, 변형 순서, fold 순서
    downstream = {}
    for name in streams:
        opened, todo = set(), [name]
        while todo:
            s = todo.pop()
            for t, ds in deps.items():
                if t not in opened and any(where[d] == s for d in ds):
                    opened.add(t)
                    todo.append(t)
        downstream[name] = opened
    vorder = {v.name: i for i, v in enumerate(variants)}
    for st in plan:
        down = sum(x.total for x in plan if x.variant == st.variant and x.fold == st.fold and x.name in downstream[st.name])
        st.priority = (-down, -st.total, vorder[st.variant], st.fold)
    plan.sort(key=lambda s: s.priority)
    return plan


def waves(streams_table, S):
    deps = stream_deps(streams_table, S)
    where = {c: s for s, cs in streams_table.items() for c in cs}
    depth = {}

    def d(s):
        if s not in depth:
            depth[s] = 1 + max((d(where[x]) for x in deps[s]), default=-1)
        return depth[s]
    for s in streams_table:
        d(s)
    return depth


def fold_timeline(plan_fold, S, minutes):
    """한 fold에서 stream마다 (시작, 끝) 시간 어림. 앞 조건의 selected.json이 나오는 때 = 그 stream의 시작 + 그 조건까지의 누적 학습 시간."""
    by = {s.name: s for s in plan_fold}
    finish, span = {}, {}

    def cond_finish(c):
        if c not in finish:
            st = next(s for s in plan_fold if c in s.conditions)
            start = stream_span(st.name)[0]
            acc, oof_added = 0, False
            for x in st.conditions:
                if st.oof and not oof_added and uses_oof(S.CONDITIONS[x]):
                    acc += st.oof * minutes_of("feature_encoder", minutes) / 60
                    oof_added = True
                acc += st.counts[x] * minutes_of(x, minutes) / 60
                finish.setdefault(x, start + acc)
        return finish[c]

    def stream_span(name):
        if name not in span:
            st = by[name]
            start = max((cond_finish(d) for d in st.deps), default=0)
            span[name] = (start, start + estimate_hours(st, st.conditions, minutes))
        return span[name]
    for name in by:
        stream_span(name)
    return span


def route(est_h, long_h, cap):
    return "sbatch" if cap > 0 and est_h > long_h else "login"


def print_dry_run(plan, variants, streams_table, S, minutes, long_h, cap, out=print):
    depth = waves(streams_table, S)
    out("[dependency waves] 같은 wave의 stream은 앞 wave 조건의 selected.json이 생긴 뒤 함께 돈다")
    for w in sorted(set(depth.values())):
        out(f"  wave {w}: {', '.join(s for s in streams_table if depth[s] == w)}")
    deps = stream_deps(streams_table, S)
    for s in streams_table:
        out(f"  {s}: 먼저 있어야 하는 다른 stream의 조건 = {sorted(deps[s]) or '없음'}")
    used = {c: minutes_of(c, minutes) for st in plan for c in st.conditions}
    out(f"[학습 한 번의 분] 기본 {minutes.get('default', DEFAULT_MINUTES):g}, " + ", ".join(f"{c} {m:g}" for c, m in used.items() if c in minutes) + f", fold 밖 encoder 2는 feature_encoder 값")
    out(f"[나누는 규칙] 어림이 {long_h:g} h보다 긴 stream은 sbatch(시간 상한 = 어림 x 2, 2~24 h), 나머지는 빈 login node를 기다린다. sbatch 청구 상한 {cap:g} GPU-h"
        f" = {cap * NODE_H_PER_GPU_H:g} node-h(shared QOS는 GPU 1시간을 node 1/4시간으로 청구). 상한을 넘으면 긴 stream도 login node를 기다린다")
    grand_h, sb_est, sb_res = 0.0, 0.0, 0.0
    for v in variants:
        rows = [s for s in plan if s.variant == v.name]
        config = S.load_config(v.config)
        out("")
        out(f"[variant {v.name}] config {v.config}  S6_OUT {v.s6_out}")
        out(f"  k_candidates {len(config.k_candidates)}, learning rate {len(config.learning_rates)}, seed {len(config.seeds)}, tokenizer {config.tokenizer}")
        first = [s for s in rows if s.fold == rows[0].fold]
        for st in sorted(first, key=lambda s: depth[s.name]):
            est = estimate_hours(st, st.conditions, minutes)
            r = route(est, long_h, cap)
            lim = f", 시간 상한 {sbatch_limit(est)[1]}" if r == "sbatch" else ""
            out(f"  stream {st.name} (wave {depth[st.name]}, 학습 {st.total}회, 어림 {est:.1f} GPU-h -> {r}{lim}, 운반 조건 {', '.join(st.carriers) or '없음'})")
            for c in st.conditions:
                out(f"    {S.DISPLAY.get(c, c):<28} {c:<30} {st.counts[c]:>4}회 x {minutes_of(c, minutes):g}분")
            if st.oof:
                out(f"    {'fold 밖 encoder 2':<28} {'feature_encoder_oof':<30} {st.oof:>4}회 x {minutes_of('feature_encoder', minutes):g}분")
        n_folds = len({s.fold for s in rows})
        per_fold = sum(estimate_hours(s, s.conditions, minutes) for s in first)
        span = fold_timeline(first, S, minutes)
        make = max(e for _, e in span.values())
        out(f"  fold 하나: 학습 {sum(s.total for s in first)}회 = {per_fold:.1f} GPU-h. GPU가 충분할 때 가장 긴 의존 경로 {make:.1f} h")
        for name, (a, b) in span.items():
            out(f"    {name:<18} 시작 {a:6.1f} h, 끝 {b:6.1f} h")
        out(f"  fold {n_folds}개: {per_fold * n_folds:.1f} GPU-h")
        for st in rows:
            est = estimate_hours(st, st.conditions, minutes)
            if route(est, long_h, cap) == "sbatch":
                sb_est += est
                sb_res += sbatch_limit(est)[0]
        done = [s for s in rows if all(condition_state(s.root, c, S) == "complete" for c in s.conditions)]
        if done:
            out(f"  이미 끝난 stream {len(done)}개: {', '.join(f'fold{s.fold}/{s.name}' for s in done)}")
        grand_h += per_fold * n_folds
    out("")
    out(f"[전체] {sum(s.total for s in plan)}회 = {grand_h:.1f} GPU-h")
    out(f"[sbatch] account {SBATCH['account']}, constraint {SBATCH['constraint']}, qos {SBATCH['qos']}, GPU {SBATCH['gpus']}, CPU {SBATCH['cpus']}. job은 취소하지 않는다")
    out(f"  sbatch로 가는 stream의 어림 합 {sb_est:.1f} GPU-h = {sb_est * NODE_H_PER_GPU_H:.1f} node-h, 시간 상한 합 {sb_res:.1f} GPU-h = {sb_res * NODE_H_PER_GPU_H:.1f} node-h")
    out(f"  상한 계산은 끝난 job의 sacct Elapsed + 도는 job과 기다리는 job의 시간 상한 전체다. 상한 {cap:g} GPU-h 안에서 한꺼번에 낼 수 있는 시간 상한 합은 {cap:g} GPU-h이고,"
        f" job이 일찍 끝나면 그만큼 더 낸다. 넘치는 긴 stream은 login node에서 돈다")
    out("  학습 횟수는 S.planned_runs의 상한이다. 0 후보(앞 조건의 학습)가 뽑히면 seed 1, 2를 새로 학습하지 않아 줄어든다")
    out("[실행 순서] 우선순위대로")
    for st in plan:
        est = estimate_hours(st, st.conditions, minutes)
        out(f"  {st.variant} fold{st.fold} {st.name} (학습 {st.total}, 어림 {est:.1f} h, {route(est, long_h, cap)})")


# ---------- 결과 폴더 ----------

def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None  # 없거나 쓰는 중이다


def condition_state(root, name, S):
    """none: selected.json 없음. selected: 뒤 조건이 읽을 수 있음. complete: seed마다 outputs(짝 조건은 ensemble)까지 저장됨."""
    sel = read_json(Path(root) / name / "selected.json")
    if not isinstance(sel, dict) or not sel.get("run_key") or not isinstance(sel.get("seeds"), dict) or not sel["seeds"]:
        return "none"
    marker = "ensemble" if S.CONDITIONS[name].paired else "outputs"
    if all((Path(root) / rel / marker / "done.json").exists() for rel in sel["seeds"].values()):
        return "complete"
    return "selected"


def fold_run_keys(root):
    """그 fold 결과에 적힌 run_key들. 둘 이상이면 섞인 것이다."""
    keys = set()
    plan = read_json(Path(root) / "plan" / "done.json")
    if isinstance(plan, dict) and plan.get("run_key"):
        keys.add(plan["run_key"])
    for p in Path(root).glob("*/selected.json"):
        sel = read_json(p)
        if isinstance(sel, dict) and sel.get("run_key"):
            keys.add(sel["run_key"])
    return keys


def launch_conditions(st, S):
    """띄울 조건. 끝난 조건은 빼고, 남은 목록에 Stimulus 조건이 없으면 운반 조건 하나를 넣는다(머리말 1)."""
    todo = [c for c in st.conditions if condition_state(st.root, c, S) != "complete"]
    if todo and st.carriers and not S.needs_stimulus(todo):
        todo.append(st.carriers[0])
    return tuple(c for c in S.ORDER if c in todo)


# ---------- node ----------

@dataclass
class Probe:
    gpus: list  # GPU마다 사용 중 메모리(MiB)
    procs: list = field(default_factory=list)  # (pid, args), 이 사용자의 프로세스


def parse_probe(text):
    """probe 명령의 출력을 읽는다. login shell이 내는 module 안내 같은 줄은 표시 앞에 있으므로 버린다. 표시가 없으면 None."""
    if GPU_MARK not in text or PS_MARK not in text:
        return None
    gpu_part, ps_part = text.split(GPU_MARK, 1)[1].split(PS_MARK, 1)
    gpus = []
    for line in gpu_part.strip().splitlines():
        m = re.fullmatch(r"\s*(\d+)\s*(MiB)?\s*", line)
        if m:
            gpus.append(int(m.group(1)))
        elif line.strip():
            return Probe([], _procs(ps_part))  # nvidia-smi 오류. GPU를 쓸 수 없다고 본다
    return Probe(gpus, _procs(ps_part))


def _procs(text):
    out = []
    for line in text.strip().splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[0].isdigit():
            out.append((int(parts[0]), parts[1]))
    return out


def free_gpu(probe, free_mib):
    """비어 있으면 GPU 번호, 아니면 None. 이 사용자의 s6_train이 그 node에 있으면 GPU 메모리가 아직 작아도(자료를 읽는 중) 쓰지 않는다."""
    if probe is None or any(S6_PROC.search(a) for _, a in probe.procs):
        return None
    for i, mib in enumerate(probe.gpus):
        if mib < free_mib:
            return i
    return None


def stream_procs(probe, st):
    """probe에서 이 stream(같은 fold, 같은 config)의 s6_train 프로세스."""
    if probe is None:
        return []
    return [(p, a) for p, a in probe.procs if S6_PROC.search(a) and f"outer_fold{st.fold}" in a.split() and str(st.config) in a]


def parse_nodes(spec):
    out = []
    for part in [x for x in spec.split(",") if x.strip()]:
        part = part.strip()
        if part.startswith("login"):
            out.append(part)
            continue
        a, _, b = part.partition("-")
        for i in range(int(a), int(b or a) + 1):
            out.append(f"login{i:02d}")
    return out


class Remote:
    """ssh로 node를 본다. 실제 실행에서만 쓴다. 시험은 같은 꼴의 가짜를 쓴다."""

    def __init__(self, user=None, timeout=60):
        self.user, self.timeout = user or getpass.getuser(), timeout

    def _ssh(self, node, command):
        try:
            r = subprocess.run(["ssh", "-n", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", node, command], capture_output=True, text=True, timeout=self.timeout)
        except (subprocess.TimeoutExpired, OSError):
            return None
        return r.stdout if r.returncode == 0 else None

    def probe(self, node):
        out = self._ssh(node, f"echo {GPU_MARK}; nvidia-smi --query-gpu=memory.used --format=csv,noheader; echo {PS_MARK}; ps -u {shlex.quote(self.user)} -o pid=,args=")
        return None if out is None else parse_probe(out)

    def launch(self, node, command):
        out = self._ssh(node, command)
        m = re.search(PID_MARK + r"(\d+)", out or "")
        return int(m.group(1)) if m else None

    def sbatch(self, args, cwd, env):
        """job 번호와 오류 글. cwd가 SLURM_SUBMIT_DIR이 되어 s6_train.sh가 run worktree의 _env.sh를 읽는다."""
        try:
            r = subprocess.run(["sbatch", "--parsable", *args], cwd=str(cwd), env=env, capture_output=True, text=True, timeout=120)
        except (subprocess.TimeoutExpired, OSError) as e:
            return None, str(e)
        if r.returncode != 0 or not r.stdout.strip():
            return None, r.stderr.strip()
        return r.stdout.strip().split(";")[0], ""

    def sacct(self, ids=(), name=None):
        """job 번호 -> 상태, 지난 시간, 시간 상한. 읽지 못하면 None."""
        cmd = ["sacct", "-X", "-n", "-P", "-o", "JobID,JobName,State,ElapsedRaw,TimelimitRaw"]
        cmd += ["-j", ",".join(ids)] if ids else ["--name", name, "-S", "now-14days"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except (subprocess.TimeoutExpired, OSError):
            return None
        return parse_sacct(r.stdout) if r.returncode == 0 else None


def parse_sacct(text):
    out = {}
    for line in text.strip().splitlines():
        f = line.split("|")
        if len(f) < 5 or not f[0].strip():
            continue
        limit = f[4].strip()
        out[f[0].strip()] = dict(name=f[1].strip(), state=(f[2].split() or ["UNKNOWN"])[0], elapsed_s=int(f[3]) if f[3].strip().isdigit() else 0,
                                 limit_min=int(limit) if limit.isdigit() else None)
    return out


def hours_of(limit):
    """sbatch 시간 상한(ex) 12:00:00, 1-00:00:00)을 시간으로."""
    days, _, rest = limit.rpartition("-")
    parts = [int(x) for x in rest.split(":")]
    while len(parts) < 3:
        parts = [0] + parts
    return int(days or 0) * 24 + parts[0] + parts[1] / 60 + parts[2] / 3600


def minutes_of(c, minutes):
    return minutes.get(c, minutes.get("default", DEFAULT_MINUTES))


def estimate_hours(st, conditions, minutes):
    """stream 하나(또는 다시 띄울 때 남은 조건)의 GPU 시간 어림. 학습 횟수 x 조건별 학습 한 번의 분. fold 밖 encoder 2는 feature_encoder의 분으로 센다."""
    m = sum(st.counts[c] * minutes_of(c, minutes) for c in conditions if c in st.counts)
    if st.oof and any(c in st.oof_conds for c in conditions):
        m += st.oof * minutes_of("feature_encoder", minutes)
    return m / 60


def sbatch_limit(est_h):
    """sbatch 시간 상한. 어림의 2배, 2시간 이상 24시간 이하, 분 단위 올림."""
    minutes = int(-(-min(24.0, max(2.0, 2 * est_h)) * 60 // 1))
    return minutes / 60, f"{minutes // 60:02d}:{minutes % 60:02d}:00"


def sbatch_args(run_root, st, conditions, freeze, log, time_limit, job_name):
    q = shlex.quote
    wrap = f"bash scripts/s6_train.sh outer_fold{st.fold} {q(','.join(conditions))} {q(str(st.config))} {q(freeze)}"
    return [f"--job-name={job_name}", f"--account={SBATCH['account']}", f"--constraint={SBATCH['constraint']}", f"--qos={SBATCH['qos']}",
            f"--ntasks={SBATCH['ntasks']}", f"--gpus={SBATCH['gpus']}", f"--cpus-per-task={SBATCH['cpus']}", f"--time={time_limit}",
            f"--output={log}", f"--chdir={run_root}", "--export=ALL", f"--wrap={wrap}"]


def launch_command(run_root, st, conditions, gpu, freeze, log):
    """run worktree의 scripts/s6_train.sh로 띄운다(_env.sh가 run worktree의 configs/env.sh와 paths.yaml을 읽는다)."""
    q = shlex.quote
    return (f"cd {q(str(run_root))} && mkdir -p {q(str(log.parent))} && S6_OUT={q(str(st.s6_out))} CUDA_VISIBLE_DEVICES={int(gpu)} "
            f"nohup bash scripts/s6_train.sh outer_fold{st.fold} {q(','.join(conditions))} {q(str(st.config))} {q(freeze)} > {q(str(log))} 2>&1 < /dev/null & echo {PID_MARK}$!")


# ---------- 동결 확인 ----------

def run_git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise FreezeError(f"git {' '.join(args)} 실패: {r.stderr.strip()}")
    return r.stdout.strip()


def check_freeze(run_root, freeze, git=run_git):
    """run worktree의 HEAD가 동결 커밋이고 src에 커밋되지 않은 변경이 없을 때만 통과한다."""
    run_root = Path(run_root)
    head = git(run_root, "rev-parse", "HEAD")
    want = git(run_root, "rev-parse", "--verify", f"{freeze}^{{commit}}")
    if head != want:
        raise FreezeError(f"{run_root}의 HEAD {head[:12]}가 동결 커밋 {freeze}({want[:12]})와 다르다. 띄우지 않는다")
    dirty = git(run_root, "status", "--porcelain", "--", "src")
    if dirty:
        raise FreezeError(f"{run_root}/src에 커밋되지 않은 변경이 있다. 띄우지 않는다:\n{dirty}")
    for rel in ("configs/env.sh", "configs/paths.yaml", "scripts/s6_train.sh", "scripts/_env.sh"):
        if not (run_root / rel).exists():
            raise FreezeError(f"{run_root / rel}이 없다. run worktree에 서버 설정을 복사해야 한다")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------- 상태 표 ----------

def now_kst(clock=time.time):
    return datetime.fromtimestamp(clock(), KST).strftime("%Y-%m-%d %H:%M:%S KST")


class State:
    def __init__(self, path):
        self.path = Path(path)
        self.rows = []
        if self.path.exists():
            lines = self.path.read_text().splitlines()
            if not lines or tuple(lines[0].split("\t")) != STATE_COLUMNS:
                raise SystemExit(f"{self.path}: 상태 표의 열이 다르다")
            for line in lines[1:]:
                if line.strip():
                    vals = line.split("\t")
                    self.rows.append(dict(zip(STATE_COLUMNS, vals + [""] * (len(STATE_COLUMNS) - len(vals)))))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
        body = "\t".join(STATE_COLUMNS) + "\n" + "".join("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in STATE_COLUMNS) + "\n" for r in self.rows)
        tmp.write_text(body)
        os.replace(tmp, self.path)

    def attempts(self, key):
        v, f, s = key
        return [r for r in self.rows if r["variant"] == v and r["fold"] == str(f) and r["stream"] == s]


# ---------- dispatcher ----------

class Dispatcher:
    def __init__(self, plan, S, *, state_path, run_root, freeze, nodes, remote, log_dir, free_mib=2000, grace_s=600, max_jobs=0,
                 clock=time.time, git=run_git, say=print, tag="t", minutes=None, long_h=LONG_HOURS, sbatch_cap_gpu_h=160.0):
        self.plan, self.S, self.run_root, self.freeze = plan, S, Path(run_root), freeze
        self.tag, self.long_h, self.sbatch_cap = tag, long_h, sbatch_cap_gpu_h
        self.minutes = dict(MINUTES if minutes is None else minutes)
        self.cap_logged = False
        self.state = State(state_path)
        self.nodes, self.remote, self.log_dir = list(nodes), remote, Path(log_dir)
        self.free_mib, self.grace_s, self.max_jobs = free_mib, grace_s, max_jobs
        self.clock, self.git, self.say = clock, git, say
        self.config_sha = {}
        self._check_meta()

    def _check_meta(self):
        """다시 켤 때 동결 커밋 문자열, run worktree, 변형별 config 내용이 처음과 같아야 한다(run_key가 바뀌지 않도록)."""
        meta_path = self.state.path.with_suffix(".meta.json")
        configs = {}
        for st in self.plan:
            configs.setdefault(st.variant, dict(config=str(st.config), sha256=sha256(st.config), s6_out=str(st.s6_out)))
        meta = dict(freeze=self.freeze, run_root=str(self.run_root), variants=configs, streams={st.name: list(st.conditions) for st in self.plan})
        old = read_json(meta_path)
        if old is not None and old != meta:
            raise SystemExit(f"{meta_path}: 처음 켰을 때와 동결 커밋, run worktree, config 가운데 무엇이 다르다. 같은 tag로 잇지 않는다\n처음 {old}\n지금 {meta}")
        if old is None:
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False))
        self.config_sha = {v: m["sha256"] for v, m in configs.items()}

    def log(self, msg):
        self.say(f"[{now_kst(self.clock)}] {msg}")

    def _latest(self, st):
        rows = self.state.attempts(st.key)
        return rows[-1] if rows else None

    def _complete(self, st):
        return all(condition_state(st.root, c, self.S) == "complete" for c in st.conditions)

    def _log_age(self, row):
        """log가 마지막으로 바뀐 뒤 지난 초. log가 아직 없으면 띄운 때부터 센다."""
        try:
            return self.clock() - os.path.getmtime(row["log"])
        except OSError:
            return self.clock() - float(row["launch_epoch"]) if row.get("launch_epoch") else float("inf")

    def refresh(self):
        """띄운 stream이 살아 있는지 본다. probe가 프로세스 없음이라고 하고, log도 grace 동안 바뀌지 않았을 때만 끝난 것으로 본다."""
        changed = self._refresh_sbatch([(st, row) for st, row in self._active() if row.get("backend") == "sbatch"])
        active = [(st, row) for st, row in self._active() if row.get("backend") != "sbatch"]
        with ThreadPoolExecutor(max_workers=16) as ex:
            probes = list(ex.map(self.remote.probe, [row["node"] for _, row in active]))
        for (st, row), probe in zip(active, probes):
            if probe is None:
                if self._log_age(row) > 3600:
                    self.log(f"경고 {row['node']}에 닿지 않고 log도 1시간 넘게 그대로다: {st.key}. 확인할 때까지 실행 중으로 둔다")
                continue
            pid = int(row["pid"]) if row["pid"] else None
            alive = any(p == pid and S6_PROC.search(a) for p, a in probe.procs) or bool(stream_procs(probe, st))
            if alive:
                if row["status"] == "launching":
                    row["status"] = "running"
                    changed = True
                continue
            complete = self._complete(st)
            if not complete and self._log_age(row) <= self.grace_s:
                continue
            row["status"] = "done" if complete else "failed"
            row["end_kst"] = now_kst(self.clock)
            if not complete:
                row["note"] = "프로세스가 사라졌는데 끝나지 않은 조건이 있다. " + self._tail(row["log"])
            self.log(f"{'끝남' if complete else '실패'} {st.variant} fold{st.fold} {st.name} ({row['node']})")
            changed = True
        if changed:
            self.state.save()

    def _job_name(self, row):
        return f"s6d_{self.tag}_{row['variant']}_f{row['fold']}_{row['stream']}_t{row['attempt']}"

    def _refresh_sbatch(self, active):
        """sbatch로 낸 job은 sacct의 상태로 본다. 끝난 상태이면 조건이 다 끝났는지로 done, failed를 정한다. job은 취소하지 않는다."""
        if not active:
            return False
        ids = [row["job_id"] for _, row in active if row["job_id"]]
        info = (self.remote.sacct(ids=ids) or {}) if ids else {}
        changed = False
        for st, row in active:
            rec = info.get(row["job_id"]) if row["job_id"] else None
            if not row["job_id"]:  # sbatch 결과를 적기 전에 dispatcher가 죽었다. 이름으로 찾는다
                found = self.remote.sacct(name=self._job_name(row)) or {}
                if found:
                    row["job_id"], rec = max(found.items(), key=lambda kv: kv[0])
                    changed = True
                elif self._log_age(row) > self.grace_s:
                    row["status"], row["end_kst"], row["note"] = SUBMIT_ERROR, now_kst(self.clock), "sbatch job을 찾지 못했다"
                    changed = True
            if rec is None:
                continue  # sacct에 아직 없거나 읽지 못했다. 시간 상한 전체를 쓴 것으로 센다
            row["slurm_state"], row["gpu_h"] = rec["state"], f"{rec['elapsed_s'] / 3600:.3f}"
            changed = True
            if rec["state"] in SLURM_ACTIVE:
                row["status"] = "running"
                continue
            complete = self._complete(st)
            row["status"], row["end_kst"] = ("done" if complete else "failed"), now_kst(self.clock)
            if not complete:
                row["note"] = f"job {rec['state']}인데 끝나지 않은 조건이 있다. " + self._tail(row["log"])
            used, committed = self.sbatch_hours()
            self.log(f"{'끝남' if complete else '실패'} {st.variant} fold{st.fold} {st.name} (job {row['job_id']} {rec['state']}, {float(row['gpu_h']):.2f} GPU-h). "
                     f"sbatch 누적 {used:.1f} GPU-h = {used * NODE_H_PER_GPU_H:.1f} node-h")
        return changed

    def sbatch_hours(self):
        """(끝난 job의 청구 GPU 시간 합 + 도는 job의 지난 시간, 상한 계산용 합). 상한 계산에서 도는 job과 기다리는 job은 시간 상한 전체로 센다."""
        used = committed = 0.0
        for r in self.state.rows:
            if r.get("backend") != "sbatch" or r["status"] == SUBMIT_ERROR:
                continue
            g, res = float(r["gpu_h"] or 0), float(r["reserved_gpu_h"] or 0)
            used += g
            committed += max(g, res) if r["status"] in ACTIVE else g
        return used, committed

    @staticmethod
    def _tail(path):
        try:
            lines = [x for x in Path(path).read_text(errors="replace").splitlines() if x.strip()]
            return ("마지막 줄: " + lines[-1][:200]) if lines else "log가 비어 있다"
        except OSError:
            return "log가 없다"

    def _ready(self):
        ready, blocked = [], []
        for st in self.plan:
            rows = self.state.attempts(st.key)
            last = rows[-1] if rows else None
            if last is not None and last["status"] in ACTIVE + ("done",):
                continue
            n_failed = sum(r["status"] == "failed" for r in rows)
            if self._complete(st):
                self.state.rows.append(dict(variant=st.variant, fold=str(st.fold), stream=st.name, attempt=str(len(rows) + 1), backend="-", conditions=",".join(st.conditions), node="-",
                                            status="done", end_kst=now_kst(self.clock), note="띄우기 전에 이미 끝나 있었다"))
                self.state.save()
                continue
            if n_failed >= MAX_ATTEMPTS:
                blocked.append((st, f"{MAX_ATTEMPTS}번 실패해 멈춤"))
                continue
            missing = [d for d in st.deps if condition_state(st.root, d, self.S) == "none"]
            if missing:
                blocked.append((st, f"앞 조건 대기 {','.join(sorted(missing))}"))
                continue
            keys = fold_run_keys(st.root)
            if len(keys) > 1:
                blocked.append((st, f"fold 결과의 run_key가 {len(keys)}개다. 섞인 결과를 정리해야 한다"))
                continue
            ready.append(st)
        ready.sort(key=lambda s: s.priority)
        return ready, blocked

    def _active(self):
        out = []
        for st in self.plan:
            row = self._latest(st)
            if row is not None and row["status"] in ACTIVE:
                out.append((st, row))
        return out

    def step(self):
        """한 번 돈다. 할 일이 남았으면 True."""
        self.refresh()
        ready, blocked = self._ready()
        active = self._active()
        if not active and not ready:
            self.summary(blocked)
            return False
        if ready:
            self._launch_ready(ready, active)
        return True

    def _launch_ready(self, ready, active):
        """긴 stream(어림 > long_h)은 청구 상한 안이면 바로 sbatch로 낸다. 짧은 stream과 상한에 걸린 긴 stream은 빈 login node를 기다린다."""
        if self.max_jobs and len(active) >= self.max_jobs:
            return
        busy = {row["node"] for _, row in active if row.get("backend") != "sbatch"}
        candidates = [n for n in self.nodes if n not in busy]
        with ThreadPoolExecutor(max_workers=16) as ex:
            probes = dict(zip(candidates, ex.map(self.remote.probe, candidates)))
        free = [n for n in candidates if free_gpu(probes[n], self.free_mib) is not None]
        foreign = [(n, a) for n in candidates if probes[n] is not None for _, a in probes[n].procs if S6_PROC.search(a)]
        n_active = len(active)
        for st in ready:
            if self.max_jobs and n_active >= self.max_jobs:
                break
            conds = launch_conditions(st, self.S)
            clash = [(n, a) for n, a in foreign if f"outer_fold{st.fold}" in a.split() and str(st.config) in a and set(conds) & set(re.split(r"[,\s]+", a))]
            if clash:
                self.log(f"건너뜀 {st.key}: 상태 표에 없는 s6_train이 같은 fold와 config로 돈다 ({clash[0][0]}: {clash[0][1][:150]})")
                continue
            est = estimate_hours(st, conds, self.minutes)
            if route(est, self.long_h, self.sbatch_cap) == "sbatch":
                reserve, limit = sbatch_limit(est)
                used, committed = self.sbatch_hours()
                if committed + reserve <= self.sbatch_cap:
                    self.cap_logged = False
                    self._submit(st, conds, reserve, limit, est)
                    n_active += 1
                    continue
                if not self.cap_logged:
                    self.log(f"sbatch 상한: 낸 job {committed:.1f} GPU-h + {st.name} {reserve:.1f} GPU-h가 상한 {self.sbatch_cap:.1f} GPU-h"
                             f"({self.sbatch_cap * NODE_H_PER_GPU_H:.1f} node-h)를 넘는다. 긴 stream도 login node를 기다린다")
                    self.cap_logged = True
            failed_nodes = {r["node"] for r in self.state.attempts(st.key) if r["status"] == "failed"}
            for node in [n for n in free if n not in failed_nodes]:
                fresh = self.remote.probe(node)  # 띄우기 바로 전에 다시 본다
                gpu = free_gpu(fresh, self.free_mib)
                free.remove(node)
                if gpu is None:
                    continue
                self._launch(st, conds, node, gpu)
                n_active += 1
                break

    def _submit(self, st, conds, reserve, limit, est):
        check_freeze(self.run_root, self.freeze, self.git)
        if sha256(st.config) != self.config_sha[st.variant]:
            raise FreezeError(f"{st.config}가 dispatcher를 켠 뒤 바뀌었다. 내지 않는다")
        rows = self.state.attempts(st.key)
        attempt = len([r for r in rows if r["status"] not in ("done", SUBMIT_ERROR)]) + 1
        log = self.log_dir / f"{st.variant}_fold{st.fold}_{st.name}_try{attempt}_sbatch.log"
        row = dict(variant=st.variant, fold=str(st.fold), stream=st.name, attempt=str(attempt), backend="sbatch", conditions=",".join(conds), node="sbatch", job_id="",
                   launch_kst=now_kst(self.clock), launch_epoch=f"{self.clock():.0f}", log=str(log), status="launching", reserved_gpu_h=f"{reserve:.3f}", gpu_h="0")
        self.state.rows.append(row)
        self.state.save()  # sbatch 전에 적는다. 도중에 dispatcher가 죽어도 job 이름으로 찾는다
        self.log_dir.mkdir(parents=True, exist_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("CUDA_VISIBLE_DEVICES", "OMP_NUM_THREADS") and not k.startswith("SLURM_")}
        env["S6_OUT"] = str(st.s6_out)
        job, err = self.remote.sbatch(sbatch_args(self.run_root, st, conds, self.freeze, log, limit, self._job_name(row)), cwd=self.run_root, env=env)
        if job:
            row["job_id"], row["status"], row["slurm_state"] = job, "running", "SUBMITTED"
        else:
            row["status"], row["end_kst"], row["note"] = SUBMIT_ERROR, now_kst(self.clock), f"sbatch 거부: {err[:200]}"
        self.state.save()
        used, committed = self.sbatch_hours()
        self.log(f"sbatch {'냄' if job else '실패'} {st.variant} fold{st.fold} {st.name} job {job} (어림 {est:.1f} h, 시간 상한 {limit}) 조건 {','.join(conds)} log {log}. "
                 f"상한 계산 {committed:.1f}/{self.sbatch_cap:.1f} GPU-h ({committed * NODE_H_PER_GPU_H:.1f}/{self.sbatch_cap * NODE_H_PER_GPU_H:.1f} node-h)")

    def _launch(self, st, conds, node, gpu):
        check_freeze(self.run_root, self.freeze, self.git)
        if sha256(st.config) != self.config_sha[st.variant]:
            raise FreezeError(f"{st.config}가 dispatcher를 켠 뒤 바뀌었다. 띄우지 않는다")
        rows = self.state.attempts(st.key)
        attempt = len([r for r in rows if r["status"] not in ("done", SUBMIT_ERROR)]) + 1
        log = self.log_dir / f"{st.variant}_fold{st.fold}_{st.name}_try{attempt}.log"
        row = dict(variant=st.variant, fold=str(st.fold), stream=st.name, attempt=str(attempt), backend="login", conditions=",".join(conds), node=node, gpu=str(gpu), pid="",
                   launch_kst=now_kst(self.clock), launch_epoch=f"{self.clock():.0f}", log=str(log), status="launching", end_kst="", note="")
        self.state.rows.append(row)
        self.state.save()  # ssh 전에 적는다. 도중에 dispatcher가 죽어도 다시 켜면 이 node를 먼저 본다
        pid = self.remote.launch(node, launch_command(self.run_root, st, conds, gpu, self.freeze, log))
        if pid is not None:
            row["pid"], row["status"] = str(pid), "running"
        else:
            row["note"] = "ssh가 pid를 돌려주지 않았다. 다음 확인에서 프로세스를 찾는다"
        self.state.save()
        self.log(f"띄움 {st.variant} fold{st.fold} {st.name} -> {node} GPU {gpu} pid {pid} 조건 {','.join(conds)} log {log}")

    def summary(self, blocked):
        done = [st for st in self.plan if (self._latest(st) or {}).get("status") == "done"]
        self.log(f"끝: stream {len(self.plan)}개 가운데 {len(done)}개 끝남")
        used, _ = self.sbatch_hours()
        self.log(f"  sbatch로 낸 job의 청구 {used:.1f} GPU-h = {used * NODE_H_PER_GPU_H:.1f} node-h (상한 {self.sbatch_cap:.1f} GPU-h)")
        for st, why in blocked:
            self.log(f"  남음 {st.variant} fold{st.fold} {st.name}: {why}")

    def run(self, poll_s, sleep=time.sleep):
        while self.step():
            sleep(poll_s)


# ---------- 실행 ----------

def out_root_of(root):
    """_env.sh와 같은 규칙. configs/paths.yaml의 output_root, 없으면 <root>/outputs."""
    p = Path(root) / "configs" / "paths.yaml"
    if p.exists():
        for line in p.read_text().splitlines():
            k, _, v = line.partition(":")
            if k.strip() == "output_root" and v.strip():
                return Path(v.strip())
    return Path(root) / "outputs"


def parse_variant(text, run_root, out_root):
    parts = text.split(":")
    if len(parts) != 3 or not all(parts):
        raise SystemExit(f"--variant는 이름:config 경로:S6_OUT 하위 폴더 꼴이다: {text}")
    name, cfg, sub = parts
    path = Path(cfg)
    if not path.is_absolute():
        path = (run_root / cfg) if (run_root / cfg).exists() else (REPO / cfg)
    if not path.exists():
        raise SystemExit(f"{name}의 config가 없다: {cfg}")
    return Variant(name, path.resolve(), out_root / sub)


def parse_folds(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out.extend(range(int(a), int(b or a) + 1))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="S6 본실험 dispatcher (짧은 stream은 login node, 긴 stream은 sbatch)")
    ap.add_argument("--tag", required=True, help="상태 표 이름. <output_root>/logs/s6_dispatch_state_<tag>.tsv")
    ap.add_argument("--run-root", required=True, help="동결 커밋에 맞춘 run worktree")
    ap.add_argument("--freeze", default="", help="설계 동결 커밋. s6_train의 --design-freeze로 그대로 넘긴다")
    ap.add_argument("--variant", action="append", required=True, help="이름:config 경로:S6_OUT 하위 폴더. 여러 번 줄 수 있다")
    ap.add_argument("--folds", default="1-6")
    ap.add_argument("--conditions", default=",".join(MAIN_CONDITIONS), help="쉼표로 나눈 조건. 기본은 scripts/s6_main.sh의 전체 목록. 앞 조건이 빠지면 멈춘다")
    ap.add_argument("--nodes", default="01-40", help="ex) 01-40 또는 login05,login07")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--poll-minutes", type=float, default=5)
    ap.add_argument("--grace-minutes", type=float, default=10, help="프로세스가 없고 log가 이만큼 그대로일 때 끝난 것으로 본다")
    ap.add_argument("--max-jobs", type=int, default=0, help="동시에 띄울 stream 수 상한. 0은 상한 없음")
    ap.add_argument("--free-mib", type=int, default=2000)
    ap.add_argument("--minutes-per-training", action="append", default=[], help="조건=분. 여러 번 또는 쉼표로. default=분은 나머지 조건. 기본 " + ", ".join(f"{k}={v:g}" for k, v in MINUTES.items()) + f", 나머지 {DEFAULT_MINUTES:g}")
    ap.add_argument("--long-threshold-hours", type=float, default=LONG_HOURS, help="어림이 이보다 긴 stream은 sbatch로 낸다(시간 상한 = 어림 x 2, 2~24 h)")
    ap.add_argument("--sbatch-gpu-hours-cap", type=float, default=160, help="이 dispatcher가 낸 sbatch job의 청구 GPU 시간 상한. 0이면 sbatch를 쓰지 않고 모두 login node에서 돈다")
    ap.add_argument("--out-root", default="", help="기본은 run worktree의 configs/paths.yaml의 output_root")
    ap.add_argument("--dry-run", action="store_true", help="계획과 어림만 낸다. ssh와 git을 쓰지 않는다")
    a = ap.parse_args(argv)
    run_root = Path(a.run_root).resolve()
    base = run_root if (run_root / "src" / "s6_common.py").exists() else REPO
    out_root = Path(a.out_root) if a.out_root else out_root_of(base)
    variants = [parse_variant(v, run_root, out_root) for v in a.variant]
    if len({v.name for v in variants}) != len(variants) or len({v.s6_out for v in variants}) != len(variants):
        raise SystemExit("변형 이름과 S6_OUT 하위 폴더는 서로 달라야 한다")
    S = load_rules(base / "src")
    minutes = dict(MINUTES)
    for item in [x for arg in a.minutes_per_training for x in arg.split(",") if x.strip()]:
        k, _, v = item.partition("=")
        if k.strip() != "default" and k.strip() not in S.CONDITIONS:
            raise SystemExit(f"--minutes-per-training의 조건 이름이 없다: {k}")
        minutes[k.strip()] = float(v)
    conditions = tuple(c.strip() for c in a.conditions.split(",") if c.strip())
    table = subset_streams(conditions)
    try:
        plan = build_plan(variants, parse_folds(a.folds), S, table, conditions)
    except ValueError as e:
        raise SystemExit(f"stream을 만들 수 없다: {e}")
    if a.dry_run:
        print(f"[dry-run] 조건 규칙은 {base / 'src'}의 s6_common, output_root {out_root}, run worktree {run_root}{'' if base == run_root else ' (아직 없어 이 레포의 src를 읽음)'}")
        print(f"[조건] {len(conditions)}개: {','.join(conditions)}")
        print_dry_run(plan, variants, table, S, minutes, a.long_threshold_hours, a.sbatch_gpu_hours_cap)
        return
    if not a.freeze:
        raise SystemExit("--freeze가 필요하다")
    check_freeze(run_root, a.freeze)
    exclude = set(parse_nodes(a.exclude)) if a.exclude else set()
    nodes = [n for n in parse_nodes(a.nodes) if n not in exclude]
    logs = out_root / "logs"
    state_path = logs / f"s6_dispatch_state_{a.tag}.tsv"
    logs.mkdir(parents=True, exist_ok=True)
    lock = open(state_path.with_suffix(".lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit(f"같은 tag({a.tag})의 dispatcher가 이미 돌고 있다")
    except OSError as e:
        print(f"경고 잠금 파일을 잠그지 못했다({e}). 같은 tag로 두 개를 켜지 않도록 직접 확인한다", flush=True)
    d = Dispatcher(plan, S, state_path=state_path, run_root=run_root, freeze=a.freeze, nodes=nodes, remote=Remote(), log_dir=logs / f"s6_dispatch_{a.tag}",
                   free_mib=a.free_mib, grace_s=a.grace_minutes * 60, max_jobs=a.max_jobs, say=lambda m: print(m, flush=True), tag=a.tag,
                   minutes=minutes, long_h=a.long_threshold_hours, sbatch_cap_gpu_h=a.sbatch_gpu_hours_cap)
    d.log(f"시작 stream {len(plan)}개, node {len(nodes)}개, 상태 표 {state_path}")
    d.run(a.poll_minutes * 60)


if __name__ == "__main__":
    main()
