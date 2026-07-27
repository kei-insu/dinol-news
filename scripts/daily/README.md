# scripts/daily/ — 일일 판정값

`daily_import.py` 가 카드 8장에 적용하는 **판정값(category·별점·직무)** 을
날짜별 JSON 으로 보관한다. 브리핑 HTML 에는 없는 큐레이션 판단이라 별도 관리한다.

## 파일명
`{YYYYMMDD}.json` — 예: `20260728.json`

## 형식
```json
{
  "20260728-ai-001": {
    "category_kr": "AI · 모델 · 출시",
    "category_en": "AI · Model · Launch",
    "impactScore": 3,
    "positions": ["product-designer"]
  },
  "...나머지 7개 (ai-002~004 · design-001~004)": {}
}
```

## 규칙
- 키는 정확히 8개: `{YYYYMMDD}-ai-001~004` · `{YYYYMMDD}-design-001~004`
- 각 값의 필드: `category_kr`(문자열) · `category_en`(문자열) · `impactScore`(1~5 정수) · `positions`(직무 ID 배열, 최대 2개, `src/lib/positions.ts` 어휘)
- `positions` 는 빈 배열 허용. 그 외 필드는 필수.

## 운영
1. 브리핑 HTML 을 `news/2026/MM/` 에 배치(main 배포본과 동일해야 함).
2. 이 폴더에 `{YYYYMMDD}.json` 판정값을 작성.
3. `python scripts/daily_import.py {YYYYMMDD}` 실행 → 추출·검증 일괄.
4. PASS 시 안내되는 커밋 대상을 직접 `git add`.

## 이력
- `20260727.json` — 형식 예시 겸 이력(커밋된 `content/news/20260727-*.json` 에서 역추출).
