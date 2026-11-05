#!/usr/bin/env python3
"""S3 캡션 특징: DeBERTa-large(주), MPNet(비교용) (04 S3, 01 3-3, 3-4, 3-4b, D7, D8, O15, 2026-11-05).

사용: s3_text.py --model deberta [--no-emotion-words] [--device cuda]. 이어 뽑지 않는다. 끊기면 처음부터 다시 돌린다. 파일은 끝까지 계산한 뒤 임시 이름에서 옮기고 manifest.json을 마지막에 쓴다.
DeBERTa: microsoft/deberta-large, 층 i = hidden_states[i](1~24), 특수 token을 뺀 평균(Horikawa, 2025 공개 코드, 04 S1). 캡션 20개를 평균해 영상당 하나로 만들고 캡션별 벡터도 저장한다.
MPNet: 모델 카드 처리. 마지막 층 token을 attention mask로 평균하고 L2 정규화한다. 384 word piece에서 자른다. 20개를 평균하고 다시 정규화하지 않는다.
--no-emotion-words: 정서어를 단어 단위로 지운 캡션(3-4, D8, SI). 목록은 10월 코드와 같다.
"""
import argparse
import ast
import hashlib
import io
import json
import re

import numpy as np
import pandas as pd
import torch

import s3_common as c

NOEMO_SOURCE = c.REPO / "project/analysis/prelim_2026-10/features/build_caption_noemo.py"
CODE_FILES = ("s3_common.py", "s3_text.py")
CHECKPOINT = dict(deberta="microsoft/deberta-large", mpnet="sentence-transformers/all-mpnet-base-v2")


def affect_words():
    tree = ast.parse(NOEMO_SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "AFFECT_WORDS":
            return sorted(set(node.value.func.value.value.split()), key=len, reverse=True)
    raise ValueError("AFFECT_WORDS를 찾지 못했다")


def load_captions(no_emotion, raw=None, words=None):
    """raw는 읽어 둔 캡션 파일의 내용이다. 주면 파일을 다시 읽지 않는다. 기록한 해시와 실제로 처리한 내용을 묶기 위해서다."""
    cap = pd.read_csv(io.BytesIO(raw) if raw is not None else c.CAPTIONS, encoding="utf-8-sig")
    if not (cap.groupby("video_id").size().eq(20).all() and set(cap.video_id) == set(range(1, c.N_VIDEOS + 1))):
        raise ValueError("캡션이 영상 2,196개 × 20개가 아니다")
    cap = cap.sort_values("video_id", kind="stable").reset_index(drop=True)
    text = cap.description.fillna("").astype(str)
    if no_emotion:
        pat = re.compile(r"\b(?:" + "|".join(words if words is not None else affect_words()) + r")\b", re.I)
        text = text.map(lambda t: re.sub(r"\s{2,}", " ", pat.sub("", t)).strip() or ".")
    return cap.video_id.to_numpy(), text.tolist()


def freeze_inputs(no_emotion):
    """계산 전에 실행 커밋, 코드, 캡션, 정서어 목록을 고정한다. 끝에서 다시 읽어 기록하지 않는다."""
    raw = c.CAPTIONS.read_bytes()
    words = affect_words() if no_emotion else []
    return dict(raw=raw, words=words, extraction_commit=c.git_head(), code_dirty_at_extraction=c.code_dirty(), code_sha256={f: c.sha256(c.CODE_DIR / f) for f in CODE_FILES}, captions_sha256=hashlib.sha256(raw).hexdigest(), affect_words_sha256=hashlib.sha256(" ".join(sorted(words)).encode()).hexdigest() if words else "")


def assert_unchanged(frozen, no_emotion):
    """계산하는 동안 코드나 입력이 바뀌었으면 저장하지 않고 멈춘다. 커밋만 바뀐 경우(문서 커밋 등)는 실행 커밋을 그대로 둔다."""
    for f, h in frozen["code_sha256"].items():
        if c.sha256(c.CODE_DIR / f) != h:
            raise SystemExit(f"계산 중에 {f}가 바뀌었다. 저장하지 않는다")
    if c.sha256(c.CAPTIONS) != frozen["captions_sha256"]:
        raise SystemExit("계산 중에 캡션 파일이 바뀌었다. 저장하지 않는다")
    if no_emotion and sorted(affect_words()) != sorted(frozen["words"]):
        raise SystemExit("계산 중에 정서어 목록이 바뀌었다. 저장하지 않는다")


def main(a):
    from transformers import AutoModel, AutoTokenizer
    name = CHECKPOINT[a.model]
    snap = c.hf_snapshot(name)
    if c.code_dirty() and not a.allow_dirty:
        raise SystemExit("커밋하지 않은 코드 변경이 있어 추출 출처를 남길 수 없다")
    tok = AutoTokenizer.from_pretrained(snap["path"], local_files_only=True)
    model = AutoModel.from_pretrained(snap["path"], local_files_only=True).to(a.device).eval()
    frozen = freeze_inputs(a.no_emotion_words)
    vid, text = load_captions(a.no_emotion_words, frozen["raw"], frozen["words"])
    if a.limit:
        keep = np.isin(vid, np.unique(vid)[:a.limit])
        vid, text = vid[keep], [t for t, k in zip(text, keep) if k]
    order = np.argsort([len(t) for t in text], kind="stable")
    out = None
    with torch.no_grad():
        for s in range(0, len(text), a.batch):
            pick = order[s:s + a.batch]
            enc = tok([text[i] for i in pick], padding=True, return_tensors="pt", return_special_tokens_mask=True, **(dict(truncation=True, max_length=384) if a.model == "mpnet" else {}))
            special = enc.pop("special_tokens_mask").bool()
            enc = {k: v.to(a.device) for k, v in enc.items()}
            r = model(**enc, output_hidden_states=True)
            if a.model == "deberta":
                h = r.hidden_states
                if len(h) != 25:
                    raise ValueError(f"층 수가 24가 아니다: {len(h) - 1}")
                m = (enc["attention_mask"].bool() & ~special.to(a.device)).unsqueeze(-1).float()
                v = torch.stack([(h[i] * m).sum(1) / m.sum(1).clamp(min=1) for i in range(1, 25)], 1)  # 캡션, 층, 차원
            else:
                m = enc["attention_mask"].unsqueeze(-1).float()
                v = torch.nn.functional.normalize((r.last_hidden_state * m).sum(1) / m.sum(1).clamp(min=1), dim=1)[:, None]
            v = v.cpu().numpy().astype(np.float32)
            if out is None:
                out = np.zeros((len(text),) + v.shape[1:], np.float32)
            out[pick] = v
            if s % (a.batch * 100) == 0:
                print(s, "/", len(text), flush=True)
    assert_unchanged(frozen, a.no_emotion_words)
    uv = np.unique(vid)
    mean = np.stack([out[vid == v].mean(0) for v in uv])
    if a.model == "mpnet":
        mean = mean[:, 0]  # (영상, 768)
    d = c.OUT / (a.model + ("_no_emotion_words" if a.no_emotion_words else ""))
    d.mkdir(parents=True, exist_ok=True)
    tag = f"_smoke{a.limit}" if a.limit else ""
    (d / f"manifest{tag}.json").unlink(missing_ok=True)  # 끝나지 않은 실행을 완료로 읽지 않게 먼저 지운다
    files = {f"video_mean{tag}.npy": mean}
    if a.model == "deberta":
        files[f"per_caption{tag}.npy"] = out
    for f, x in files.items():
        tmp = d / (f + ".tmp.npy")
        np.save(tmp, x)
        tmp.replace(d / f)
    ids_name = f"per_caption_video_id{tag}.tsv"
    pd.DataFrame(dict(video_id=vid)).to_csv(d / ids_name, sep="\t", index=False)
    info = dict(model=a.model, checkpoint=name, revision=snap["revision"], weights_sha256=snap["weights_sha256"], extraction_commit=frozen["extraction_commit"], head_at_save=c.git_head(), code_dirty_at_extraction=frozen["code_dirty_at_extraction"], code_sha256=frozen["code_sha256"], transformers=__import__("transformers").__version__, torch=torch.__version__, no_emotion_words=a.no_emotion_words, n_affect_words=len(frozen["words"]), affect_words_sha256=frozen["affect_words_sha256"], captions_sha256=frozen["captions_sha256"], layers=list(range(1, 25)) if a.model == "deberta" else "last_hidden_state", pooling="특수 token을 뺀 평균, 캡션 20개 평균" if a.model == "deberta" else "attention mask 평균, L2 정규화, 캡션 20개 평균, 다시 정규화하지 않음", shape=list(mean.shape), max_length=384 if a.model == "mpnet" else "자르지 않음", file_sha256={f: c.sha256(d / f) for f in [*files, ids_name]})
    (d / f"manifest{tag}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    print("저장", d, mean.shape)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(CHECKPOINT), required=True)
    ap.add_argument("--no-emotion-words", action="store_true")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--limit", type=int, default=0, help="시험용. 앞 영상 몇 개만")
    ap.add_argument("--allow-dirty", action="store_true", help="시험용. 커밋 전 코드로 돌린다")
    main(ap.parse_args())
