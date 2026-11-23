#!/usr/bin/env python3
"""S10 회상 질문 3의 예측 변수(01 6-3): 정서마다의 Vision 대 Caption 지수. CPU, 1초. 뇌 자료를 쓰지 않는다.

이 값은 11/17에 회상 자료를 보기 전에 계산해 s10_stats/imagery_prereg/vision_over_caption_index.tsv로 고정했다
(README.json의 code_commit bca3597). 그때는 이 계산을 코드 파일로 남기지 않아 11/20에 같은 계산을 이 파일로 옮겼다.
고정한 파일과 바이트 단위로 같게 다시 만든다.

계산
- 입력은 6-4d의 s10_stats/beyond_scene/features_only.tsv다. r_V_to_T와 r_C_to_T는 HK 개발 영상에서 바깥 fold마다
  D_k로만 맞춘 cross-fitted ridge가 Vision feature만, Caption feature만으로 사람 평정을 예측한 r이다(src/s10_beyond_scene.py).
- 정서 34개(manifests/s1/label_map_34.tsv의 name 순서)마다 r_vision = r_V_to_T, r_caption = r_C_to_T,
  vision_over_caption = r_vision ÷ r_caption. valence와 arousal은 뺀다.
- 표는 pandas 기본 설정으로 읽고 쓴다(11/17 원래 계산과 같은 방식. 읽는 방식을 바꾸면 마지막 자리가 달라질 수 있다).
출력(--out, 기본 s10_stats/imagery_prereg/)
- vision_over_caption_index.tsv: emotion, r_vision, r_caption, vision_over_caption
- 이 파일이 이미 있으면 덮어쓰지 않고, 다시 계산한 값과 바이트 단위로 같은지만 확인한다. 다르면 멈춘다(고정한 예측 변수라 바꾸지 않는다).
- 파일이 없는 새 폴더에는 표와 run_info.json(입력 경로와 sha256, 코드 커밋)을 쓴다.
읽는 코드: src/s10_imagery.py(6-3_imagery의 Q3), src/s10_per_emotion.py(per_emotion_models의 Q3)
사용: s10_imagery_prereg.py --stats <s10_stats/beyond_scene> [--out <폴더>]
"""
import argparse
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

import s4_common as c

FILE = "vision_over_caption_index.tsv"


def build(stats):
    src = Path(stats) / "features_only.tsv"
    f = pd.read_csv(src, sep="\t").set_index("target")
    names = pd.read_csv(c.LABEL_MAP, sep="\t")["name"].tolist()
    if len(names) != 34 or len(set(names)) != 34:
        raise SystemExit(f"{c.LABEL_MAP}: 정서 이름이 34개가 아니다")
    missing = [n for n in names if n not in f.index]
    if missing:
        raise SystemExit(f"{src}: 정서 {missing}가 없다")
    rv, rc = f.loc[names, "r_V_to_T"], f.loc[names, "r_C_to_T"]
    if not (np.isfinite(rv).all() and np.isfinite(rc).all()) or (rc == 0).any():
        raise SystemExit(f"{src}: r_V_to_T, r_C_to_T에 유한하지 않은 값이나 0이 있다")
    table = pd.DataFrame(dict(emotion=names, r_vision=rv.to_numpy(), r_caption=rc.to_numpy(), vision_over_caption=(rv / rc).to_numpy()))
    buf = io.StringIO()
    table.to_csv(buf, sep="\t", index=False)
    return src, buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description="S10 회상 질문 3의 Vision 대 Caption 지수")
    ap.add_argument("--stats", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    out = Path(a.out or Path(a.stats).parent / "imagery_prereg")
    src, text = build(a.stats)
    target = out / FILE
    if target.exists():
        old = target.read_text()
        if old != text:
            diff = next(((i, x, y) for i, (x, y) in enumerate(zip(old.splitlines(), text.splitlines()))
                         if x != y), (None, "", ""))
            raise SystemExit(f"{target}: 고정한 파일과 다시 계산한 값이 다르다. 덮어쓰지 않는다. 첫 차이 행 {diff[0]}\n고정: {diff[1]}\n다시: {diff[2]}")
        print(f"고정한 파일과 바이트 단위로 같다: {target}", flush=True)
        return
    out.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    info = dict(stage="S10 회상 질문 3의 Vision 대 Caption 지수(01 6-3)", source=str(src), source_sha256=c.sha256(src),
                label_map=str(c.LABEL_MAP), code_commit=c.START_HEAD, code_dirty=c.START_DIRTY)
    (out / "run_info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(json.dumps(info, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
