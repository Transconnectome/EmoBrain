#!/usr/bin/env python3
"""S6 한 조건의 후보 일부만 같은 실행 번호로 학습한다 (11/14 석진 님. 학습 코드 src는 고치지 않는다).

왜 src 밖에 두나
- 실행 번호(run_key)에는 src의 s4~s6 코드 지문이 들어간다. src를 고치면 이미 끝난 A-1 grid 102회의 실행 번호가 달라져 다시 학습해야 한다.
- 그래서 run worktree의 s6_train을 그대로 불러 같은 순서로 자료와 실행 번호를 만들고, 마지막의 후보 학습만 지정한 조건의 지정한 후보로 바꾼다.
- 실행 번호가 다르면 s6_train의 원래 검사가 멈춘다(FoldRunner가 plan/done.json의 실행 번호를 대조하고, selected()가 A-1 선택의 실행 번호를 대조한다).
- 후보는 함수 밖에서 만들지 않는다. s6_common.candidates가 그 fold의 A-1 선택(d, 입력층 weight decay, learning rate)으로 만든 목록에서 candidate_id로 고른다.
- A-1 선택만 읽는 조건만 받는다. C-2처럼 다른 조건의 선택을 읽는 조건은 dispatcher가 차례대로 돌린다.
사용(run worktree의 _env.sh가 src로 cd한 뒤): python s6_candidates.py --plan outer_fold1 --conditions brain_only,brain_only_distill --config <설정> --design-freeze <커밋>
                                              --target brain_decoded:<id>,<id> [--device cuda]
"""
import os
import sys

sys.path.insert(0, os.getcwd())  # run worktree의 src(_env.sh가 cd한다). 그 코드로 실행 번호를 만든다
import s6_common as S  # noqa: E402
import s6_train as T  # noqa: E402

ALLOWED = ("brain_only_distill", "control_label_smoothing", "control_stimulus_shuffle", "brain_only_featdec", "control_feature_shuffle", "brain_decoded")


def parse_target(text):
    cond, _, ids = text.partition(":")
    ids = [x for x in ids.split(",") if x]
    if cond not in ALLOWED:
        raise SystemExit(f"--target 조건은 A-1 선택만 읽는 {ALLOWED} 가운데 하나다: {cond}")
    if not ids or len(set(ids)) != len(ids):
        raise SystemExit("--target 후보 번호가 비었거나 겹친다")
    return cond, ids


def pick(cond, ids, config, base):
    cands = S.candidates(cond, k_candidates=config.k_candidates, base=base, learning_rates=config.learning_rates, lr_follows_brain_only=config.lr_follows_brain_only)
    by = {S.candidate_id(c): c for c in cands}
    missing = [x for x in ids if x not in by]
    if missing:
        raise SystemExit(f"{cond}: 이 fold의 후보가 아닌 번호 {missing}")
    return [by[x] for x in ids]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--target" not in argv or "--only-candidates" in argv:
        raise SystemExit("--target을 주고 --only-candidates는 주지 않는다")
    i = argv.index("--target")
    cond, ids = parse_target(argv[i + 1])
    del argv[i:i + 2]
    sentinel, done = object(), []
    original = T.FoldRunner.train_one

    def train_one(self, condition, cand, seed, search=False):
        if cand is not sentinel:
            return original(self, condition, cand, seed, search)
        base = self.selected("brain_only")["candidate"]  # A-1 선택. 실행 번호가 다르면 여기서 멈춘다
        for c in pick(cond, ids, self.config, base):
            original(self, cond, c, seed, search=True)
        done.append(cond)

    T.only_candidates = lambda text, config: [sentinel]  # s6_train.main이 --only-candidates 자리에서 부른다
    T.FoldRunner.train_one = train_one
    T.main(argv + ["--only-candidates", "target"])
    if not done:
        raise SystemExit("후보를 학습하지 않았다")


if __name__ == "__main__":
    main()
