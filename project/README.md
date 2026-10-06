# EmoBrain implementation

_Code navigation and migration boundary · 2026-10-06_

---

<a id="english"></a>

## 📚 English

[한국어 버전으로 이동](#korean)

### Current specification

Use [the study index](../docs/current/00_README.md),
[implementation specification](../docs/current/02_IMPLEMENTATION_SPEC.md) and
[implementation status](../docs/current/08_IMPLEMENTATION_STATUS.md).
The former project contract is preserved in the [archive](../docs/archive/pre-handoff-2026-10-06/project/README.md).

### Existing code is not the current pipeline

| Path | Existing role | Current-design status |
| --- | --- | --- |
| `code/decoder/` | Emotion-label-query decoder | Historical implementation / possible baseline, not brain-query teacher |
| `code/fusion/`, `code/training/`, `code/configs/` | Qwen-era teacher/cache/student | Legacy; not nested OOF |
| `data/` | Horikawa ROI-mean, 34-D normalization, captions | Needs current cohort / voxel / target / manifest adapters |
| `scripts/` | Prior training, gates and QC | Audit before reuse; old launch commands are not endorsed |
| `evaluation/` | Profile metrics and ISC | Reuse only after target, scale and estimand checks |
| `tests/` | Earlier core tests | Current split / OOF / content-access tests still required |
| `shared/`, `output/`, `legacy/` | Existing assets, experiments and records | Preserve; do not silently relabel as current results |

No source code, feature cache, checkpoint or experiment result is migrated by this documentation change.
Do not launch the old training script merely because documentation now points at the new specification.

### Before implementation

1. Inventory the server commit, local modifications, data manifests and prior test exposure.
2. Resolve canonical IDs and run/content grouping before fitting transforms or teachers.
3. Implement scoped data contracts and leakage tests before full experiments.
4. Preserve old baselines with their original preprocessing, split and target provenance.
5. Keep run outputs outside maintained design documents; create no backup copies in the repository root.

---

<a id="korean"></a>

## 📚 한국어

[Back to English](#english)

_코드 안내와 최신 설계 전환의 범위 · 2026-10-06_

### 현재 기준 문서

[연구 문서 목차](../docs/current/00_README.md),
[구현 사양](../docs/current/02_IMPLEMENTATION_SPEC.md),
[구현 상태](../docs/current/08_IMPLEMENTATION_STATUS.md)를 기준으로 작업한다.
이전 프로젝트 규약은 [보관함](../docs/archive/pre-handoff-2026-10-06/project/README.md)에 보존되어 있다.

### 기존 코드와 최신 파이프라인은 다르다

| 경로 | 기존 역할 | 최신 설계 기준 상태 |
| --- | --- | --- |
| `code/decoder/` | 감정 label-query decoder | 과거 구현 / baseline 후보; brain-query teacher가 아님 |
| `code/fusion/`, `code/training/`, `code/configs/` | Qwen 기반 teacher/cache/student | 과거 구현; 중첩 OOF가 아님 |
| `data/` | Horikawa ROI 평균, 34-D 정규화, caption | 최신 cohort / voxel / target / manifest에 맞춘 adapter 필요 |
| `scripts/` | 이전 학습, 판정 gate, QC | 재사용 전 검토 필요; 기존 실행 명령을 그대로 승인하지 않음 |
| `evaluation/` | 프로필 지표와 ISC | target, 척도, 추정 대상 확인 후에만 재사용 |
| `tests/` | 이전 핵심 테스트 | 최신 split / OOF / content 접근 차단 테스트 추가 필요 |
| `shared/`, `output/`, `legacy/` | 기존 자료, 실험, 기록 | 보존하며 최신 설계의 결과로 임의 재분류하지 않음 |

이번 문서 변경은 소스 코드, feature cache, checkpoint, 실험 결과를 최신 설계로 전환한 것이 아니다.
문서가 새 사양을 가리킨다는 이유만으로 기존 학습 스크립트를 실행하지 않는다.

### 구현 전에 할 일

1. 서버 커밋, 로컬 변경, 데이터 manifest, 기존 test 노출 이력을 확인한다.
2. 변환기나 teacher를 학습하기 전에 canonical ID와 run/content 그룹을 확정한다.
3. 전체 실험 전에 범위가 명확한 데이터 규약과 누출 방지 테스트를 구현한다.
4. 기존 baseline의 원래 전처리, split, target 출처 기록을 보존한다.
5. 실행 산출물은 현재 설계 문서와 분리해 관리하고, 저장소 루트에 백업 사본을 만들지 않는다.
