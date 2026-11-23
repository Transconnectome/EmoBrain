#!/usr/bin/env python3
"""s10_imagery_prereg 합성 자료 시험(11/20). 실제 결과를 읽지 않는다(정서 이름은 레포의 manifests/s1/label_map_34.tsv). src에서 실행한다.

보는 것: 값이 r_V_to_T ÷ r_C_to_T이고 정서 이름표 순서다, valence와 arousal은 빠진다, 새 폴더에는 표와 run_info.json을 쓴다,
같은 파일이 있으면 그대로 두고, 다른 파일이 있으면 덮어쓰지 않고 멈춘다, 정서가 빠지거나 r_C_to_T가 0이면 멈춘다.
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s10_imagery_prereg as S  # noqa: E402
import s4_common as c  # noqa: E402

fails = []


def check(name, ok):
    print(("통과 " if ok else "실패 ") + name)
    if not ok:
        fails.append(name)


def stops(fn):
    try:
        fn()
    except SystemExit:
        return True
    return False


names = pd.read_csv(c.LABEL_MAP, sep="\t")["name"].tolist()
rng = np.random.default_rng(0)
rows = [dict(target=n, r_Sw_to_T=0.1, r_V_to_T=rng.uniform(0.1, 0.8), r_C_to_T=rng.uniform(0.3, 0.9)) for n in names[::-1]]
rows += [dict(target=t, r_Sw_to_T=0.1, r_V_to_T=0.5, r_C_to_T=0.6) for t in ("valence", "arousal")]
with tempfile.TemporaryDirectory() as tmp:
    stats, out = Path(tmp) / "beyond_scene", Path(tmp) / "imagery_prereg"
    stats.mkdir()
    feat = pd.DataFrame(rows)
    feat.to_csv(stats / "features_only.tsv", sep="\t", index=False)
    S.main(["--stats", str(stats), "--out", str(out)])
    t = pd.read_csv(out / S.FILE, sep="\t")
    f = feat.set_index("target")
    check("정서 34개, 이름표 순서", t.emotion.tolist() == names)
    check("valence, arousal 없음", not {"valence", "arousal"} & set(t.emotion))
    check("지수 = r_V_to_T ÷ r_C_to_T", np.allclose(t.vision_over_caption, f.loc[names, "r_V_to_T"].to_numpy() / f.loc[names, "r_C_to_T"].to_numpy()))
    check("새 폴더에 run_info.json", (out / "run_info.json").exists())
    before = (out / S.FILE).read_text()
    check("같은 파일이면 그대로 둠", not stops(lambda: S.main(["--stats", str(stats), "--out", str(out)])) and (out / S.FILE).read_text() == before)
    feat.loc[0, "r_V_to_T"] += 0.01
    feat.to_csv(stats / "features_only.tsv", sep="\t", index=False)
    check("다른 파일이면 멈추고 덮어쓰지 않음", stops(lambda: S.main(["--stats", str(stats), "--out", str(out)])) and (out / S.FILE).read_text() == before)
    feat.drop(index=1).to_csv(stats / "features_only.tsv", sep="\t", index=False)
    check("정서가 빠지면 멈춤", stops(lambda: S.build(stats)))
    bad = pd.DataFrame(rows)
    bad.loc[2, "r_C_to_T"] = 0.0
    bad.to_csv(stats / "features_only.tsv", sep="\t", index=False)
    check("r_C_to_T가 0이면 멈춤", stops(lambda: S.build(stats)))
print(f"s10_imagery_prereg 시험 {'통과' if not fails else '실패 ' + str(len(fails)) + '개'}")
sys.exit(1 if fails else 0)
