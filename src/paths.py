"""레포 안 위치와 서버마다 다른 위치를 한곳에서 정한다.

레포 안: src(코드), splits(분할), manifests(단계별 작은 표), data(작은 입력 표), configs(설정).
서버마다 다른 위치는 configs/paths.yaml(git 밖)에 적는다. 형식은 configs/paths.example.yaml을 본다.
EMOBRAIN_PATHS 환경 변수로 다른 설정 파일을 줄 수 있다.
"""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
SPLITS = REPO / "splits/hk_dev_v4"
MANIFESTS = REPO / "manifests"
S1 = MANIFESTS / "s1"
S2 = MANIFESTS / "s2"
DATA = REPO / "data"
CONFIGS = REPO / "configs"
REFERENCE = REPO / "docs/final/reference"
KEYS = ("data_root", "video_root", "output_root", "ffmpeg", "ffprobe", "pymoten_dir")


def _read(path):
    """'키: 값' 한 줄씩. 빈 줄과 #으로 시작하는 줄은 건너뛴다."""
    out = {}
    for line in Path(path).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            k, v = (x.strip() for x in line.split(":", 1))
            out[k] = v.strip("'\"")
    return out


def _config():
    path = Path(os.environ.get("EMOBRAIN_PATHS", CONFIGS / "paths.yaml"))
    if not path.exists():
        return {}
    cfg = _read(path)
    unknown = set(cfg) - set(KEYS)
    if unknown:
        raise ValueError(f"{path}: 알 수 없는 키 {sorted(unknown)}")
    return cfg


_CFG = _config()


def need(key):
    """설정 값. 없으면 무엇을 적어야 하는지 알려 주고 멈춘다."""
    if key not in _CFG:
        raise SystemExit(f"configs/paths.yaml에 {key}를 적어야 한다(configs/paths.example.yaml 참고)")
    return _CFG[key]


DATA_ROOT = Path(_CFG.get("data_root", REPO / "external_data"))  # 원자료: Horikawa/, MindCaptioning/, atlas_sources/, Horikawa_embedding/
VIDEO_ROOT = Path(_CFG.get("video_root", DATA_ROOT / "videos"))  # 자극 영상 2,196개. data/stimuli.tsv의 path는 이 폴더 기준이다
OUT = Path(_CFG.get("output_root", REPO / "outputs"))  # 큰 산출물과 로그. git 밖
