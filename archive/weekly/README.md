# Weekly Tracking

> 매주 작업 기록을 GitHub PR과 동기화

---

## 폴더 구조

```
weekly/
├── README.md (이 파일)
├── 2026-05-11/        ← 이번 주
│   ├── plan.md        ← 월요일 계획
│   ├── checkins.md    ← 화-금 매일 체크인 기록
│   └── results.md     ← 금요일 결과 정리
└── 2026-05-18/        ← 다음 주
```

---

## 주간 사이클

### ① 월요일. Draft PR + 폴더 생성

```bash
git checkout main && git pull
git checkout -b weekly/2026-05-11
mkdir -p weekly/2026-05-11
cp weekly/TEMPLATE/* weekly/2026-05-11/  # 템플릿 복사
git add weekly/2026-05-11/
git commit -m "[WEEKLY] 2026-05-11 시작"
git push -u origin weekly/2026-05-11
```

push URL 열기 → 제목 `[WEEKLY] 2026-05-11. sjmoon` → Draft PR 생성

### ② 화-금 매일 오전 10시. 체크인

GitHub PR 페이지에 `[체크인]` 코멘트 1줄.
로컬에는 `weekly/2026-05-11/checkins.md`에 동기화 가능 (선택).

### ③ 주중. Commit & Push

태그 사용:
- `[EXP]` 실험·분석
- `[FIX]` 버그 수정
- `[DRAFT]` 논문 초안
- `[DATA]` 데이터 처리

### ④ 금요일. Ready for Review

같은 PR description 업데이트 → 결과 체크리스트 수정 → Ready for review 클릭.
로컬 `weekly/2026-05-11/results.md`에 같은 내용 동기화.

---

## 주의

- **새 PR 만들지 말 것**. 월요일 PR을 금요일까지 같은 것 사용
- **`[체크인]` 태그 필수**. 자동 수집 안 됨
- 체크인 안 한 날은 ❌로 표시되어 Teams digest에 노출됨
