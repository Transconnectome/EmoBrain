#!/usr/bin/env python3
"""
scientist_ai.py — NetFeeliX Scientist-AI

주어진 모델 디렉토리를 분석하여:
1. 모든 scientific decision point 추출
2. 연구 계획(research_overview.md)과 대조해 blind spot 발굴
3. 실험 트리 + 즉시 결정 필요 항목 생성
4. 마크다운 리포트로 저장

사용법:
    python scientist_ai.py --model-dir /path/to/SwiFT [--context /path/to/overview.md]
    sbatch scientist_ai.sh /path/to/SwiFT
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

RESEARCH_OVERVIEW = ROOT / "research_overview.md"
CLAUDE_MD = ROOT / "CLAUDE.md"

# Claude API 설정
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192

# 코드 분석 대상 파일 패턴 (우선순위 순)
CODE_PATTERNS = [
    "**/*.yaml", "**/*.yml", "**/*.json",       # config
    "**/train*.py", "**/trainer*.py",            # training loop
    "**/dataset*.py", "**/data*.py",             # dataloader
    "**/model*.py", "**/network*.py",            # model definition
    "**/config*.py", "**/args*.py",              # argument parsing
    "**/main*.py", "**/run*.py",                 # entry points
]
MAX_FILES = 12
MAX_FILE_CHARS = 6000  # 파일당 최대 문자 수


def find_code_files(model_dir: Path) -> list[Path]:
    """모델 디렉토리에서 핵심 코드 파일을 우선순위 순으로 수집."""
    seen = set()
    files = []
    for pattern in CODE_PATTERNS:
        for f in sorted(model_dir.glob(pattern)):
            if f.is_file() and f not in seen and "__pycache__" not in str(f):
                seen.add(f)
                files.append(f)
                if len(files) >= MAX_FILES:
                    return files
    return files


def read_file_safe(path: Path, max_chars: int = MAX_FILE_CHARS) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n... [truncated, total {len(text)} chars]"
        return text
    except Exception as e:
        return f"[읽기 실패: {e}]"


def build_prompt(model_dir: Path, code_files: list[Path], context_text: str) -> str:
    model_name = model_dir.name

    code_block = ""
    for f in code_files:
        rel = f.relative_to(model_dir)
        code_block += f"\n\n### {rel}\n```\n{read_file_safe(f)}\n```"

    return f"""당신은 computational neuroscience 전문 scientist-AI다.

아래는 NetFeeliX 프로젝트의 연구 계획과 분석 대상 모델 코드다.
이를 읽고 researcher가 놓쳤을 수 있는 모든 scientific decision point를 발굴하라.

---

## 연구 계획 (research_overview.md 발췌)

{context_text[:8000]}

---

## 분석 대상 모델: {model_name}

{code_block}

---

## 분석 지시

다음 5개 섹션으로 구성된 마크다운 리포트를 작성하라.

### 섹션 1: Decision Points (카테고리별)

코드에서 발견한 모든 configurable parameter와 architectural choice를 다음 형식으로 정리하라.
카테고리: [입력 형식 / 아키텍처 / 학습 전략 / 전처리 / 평가]

각 항목:
```
**[파라미터명]** (현재값: X)
- 옵션 공간: ...
- 과학적 의미: ...
- 제약 조건: ...
- 암묵적 가정: ...
- 파생 RQ: "이 파라미터를 바꾸면 [구체적 scientific question]을 테스트한다"
```

### 섹션 2: Blind Spots

연구 계획에 명시되지 않았거나 암묵적으로 처리된 항목을 찾아라.
각 항목에 대해:
- 무엇이 빠져 있는가
- 왜 문제가 될 수 있는가 (구체적으로)
- 어떻게 해결해야 하는가

특히 다음을 확인하라:
- HRF lag 가정 (명시되어 있는가? emotion dynamics와 맞는가?)
- subject normalization 방식
- train/val/test split 정의 (subject-level vs stimulus-level)
- pretrained weight와 fine-tuning 입력 해상도 일치 여부
- temporal pooling 방식이 emotion time scale과 맞는가
- stimulus-only baseline 정의 여부
- low-level visual/audio confound 통제 계획
- noise ceiling 정의 여부
- shortcut learning 가능성

### 섹션 3: 실험 트리

발굴된 decision point를 트리 구조로 정리하라.
우선순위 레이블: [즉시 결정] / [1라운드] / [2라운드] / [보류]

```
[즉시 결정] sequence_length
├── 20 (pretraining과 동일) → RQ: pretrained weight 사용 시 성능 상한은?
├── 5/10/20 sweep (scratch) → RQ: emotion arc 포착에 최적 window는?
└── 제약: pretrained weight 사용 시 반드시 20 고정
```

### 섹션 4: 즉시 결정 필요 항목

첫 실험 실행 전에 반드시 결정해야 하는 항목만 목록으로.
각 항목에 대해 "결정하지 않으면 어떤 실험이 불가한가"를 명시.

### 섹션 5: 연구 계획 업데이트 권고

research_overview.md에 추가되어야 할 내용을 구체적으로 제안하라.
섹션 이름과 추가할 내용을 명시.

---

비판은 구체적으로 하라.
"temporal 처리가 문제일 수 있다"가 아니라
"sequence_length=20, TR=2.5초이면 50초 window인데,
Horikawa 자극의 median duration이 X초라면 Y% 자극이 window를 벗어난다"처럼.

코드에서 발견한 것만 쓴다. 추측하지 않는다.
명시되지 않은 것은 전부 blind spot으로 올린다.
"""


def run_analysis(model_dir: Path, context_path: Path | None) -> str:
    context_path = context_path or RESEARCH_OVERVIEW
    context_text = read_file_safe(context_path, max_chars=10000)

    code_files = find_code_files(model_dir)
    if not code_files:
        print(f"[경고] {model_dir}에서 코드 파일을 찾지 못했습니다.")

    print(f"[분석 시작] 모델: {model_dir.name}")
    print(f"  코드 파일 {len(code_files)}개 로드: {[f.name for f in code_files]}")

    prompt = build_prompt(model_dir, code_files, context_text)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="당신은 computational neuroscience와 deep learning을 모두 깊이 이해하는 scientist-AI다. 연구자가 놓치는 blind spot을 찾는 것이 핵심 역할이다.",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


def save_report(model_name: str, content: str) -> Path:
    date_str = datetime.now().strftime("%Y%m%d")
    out_path = REPORTS_DIR / f"scientist_{model_name}_{date_str}.md"
    header = f"# Scientist Analysis: {model_name}\n분석일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    out_path.write_text(header + content, encoding="utf-8")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="NetFeeliX Scientist-AI")
    parser.add_argument("--model-dir", required=True, help="분석할 모델 디렉토리 경로")
    parser.add_argument("--context", default=None, help="연구 계획 파일 경로 (기본: research_overview.md)")
    args = parser.parse_args()

    model_dir = Path(args.model_dir).expanduser().resolve()
    if not model_dir.exists():
        print(f"[오류] 디렉토리가 없습니다: {model_dir}", file=sys.stderr)
        sys.exit(1)

    context_path = Path(args.context).resolve() if args.context else None

    result = run_analysis(model_dir, context_path)

    out_path = save_report(model_dir.name, result)
    print(f"\n[완료] 리포트 저장: {out_path}")
    print("\n" + "=" * 60)
    print(result)


if __name__ == "__main__":
    main()
