NetFeeliX 연구 관련 문헌과 코드를 탐색하고 reference에 저장하라.

검색 토픽: $ARGUMENTS

## 실행 순서

### 1단계: 로컬 reference 확인

먼저 아래 파일을 읽는다.

1. `/pscratch/sd/s/sjmoon/NetFeeliX/CLAUDE.md`
2. `/pscratch/sd/s/sjmoon/NetFeeliX/reference/papers.md`
3. `/pscratch/sd/s/sjmoon/NetFeeliX/reference/literature_map.md`
4. `/pscratch/sd/s/sjmoon/NetFeeliX/reference/code_resources.md`
5. `/pscratch/sd/s/sjmoon/NetFeeliX/reference/datasets.md`

이미 충분히 정리된 내용이면 외부 검색을 생략하고 업데이트만 수행한다.

### 2단계: 외부 검색

검색 범위:

- fMRI foundation model
- BrainLM, Brain-JEPA, NeuroSTORM, Omni-fMRI, Brain-DiT
- SwiFT, SwiFUN
- TRIBE, TRIBE v2, Algonauts 2025
- HCP movie-watching fMRI
- emotion fMRI, naturalistic affective neuroscience
- Horikawa, Emo-FilM, Koide-Majima, dynamic arousal prediction

### 3단계: 저장

신규 검색 결과는 다음 파일에 저장한다.

`/pscratch/sd/s/sjmoon/NetFeeliX/reference/search_[topic_slug].md`

각 항목 형식:

```markdown
### Paper or Resource
- **Type**:
- **Venue/date**:
- **Summary**:
- **NetFeeliX relevance**:
- **URL/DOI**:
- **Action**:
```

### 4단계: 핵심 reference 업데이트

직접 관련 있는 신규 항목은 `papers.md`, `datasets.md`, 또는 `code_resources.md`에도 반영한다.

