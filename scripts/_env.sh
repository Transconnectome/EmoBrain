# 모든 scripts/*.sh가 처음에 읽는다. 레포 최상위에서 실행한다(sbatch도 레포 최상위에서 제출한다).
# 실행 환경은 configs/env.sh, 경로는 configs/paths.yaml에서 읽는다(예시는 configs/*.example.*).
ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
[ -f "$ROOT/src/paths.py" ] || { echo "레포 최상위에서 실행해야 한다: $ROOT" >&2; exit 1; }
[ -f "$ROOT/configs/env.sh" ] && source "$ROOT/configs/env.sh"
PY="${EMOBRAIN_PYTHON:-python}"
PY_CPU="${EMOBRAIN_PYTHON_CPU:-python}"
_cfg() { [ -f "${EMOBRAIN_PATHS:-$ROOT/configs/paths.yaml}" ] && awk -F': *' -v k="$1" '$1==k{print $2}' "${EMOBRAIN_PATHS:-$ROOT/configs/paths.yaml}"; return 0; }
DATA_ROOT="$(_cfg data_root)"
OUT_ROOT="$(_cfg output_root)"; OUT_ROOT="${OUT_ROOT:-$ROOT/outputs}"
LOGS="$OUT_ROOT/logs"; mkdir -p "$LOGS"
export PYTHONDONTWRITEBYTECODE=1
cd "$ROOT/src"
