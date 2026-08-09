# 핸드오프 — 파일 전달 시 저장 경로 표기 (2026-07-25)

업데이트한 파일을 사용자에게 전달(다운로드)할 때는, **다운로드 링크 위에 레포 저장 경로를 함께 표기**한다. 형식: `dinol-news > <폴더> 폴더`.

| 파일 종류 | 저장 경로 |
|---|---|
| 일일 브리핑 `Dinol_news_YYYYMMDD.html` | `dinol-news > news > 2026 > MM 폴더` |
| 문서 `*.md` | `dinol-news > docs 폴더` |
| 에셋 `dinol.css`·`dinol.js`·`dinol-firebase.js` | `dinol-news > assets 폴더` |
| 루트 파일 `index.html`·`archive.html`·`privacy.html`·`template.html`·`index.json` | `dinol-news 루트` |
| 스크립트 `*.py`·`*.mjs` | `dinol-news > scripts 폴더` |
| 카드 데이터 `{contentId}.json` | `dinol-news > content 폴더 > news 폴더` |

> ⚠️ 경로는 **폴더를 하나씩 끊어서** 표기한다. `content/news 폴더` 처럼 쓰면
> 슬래시가 폴더 이름의 일부로 오해된다. `content 폴더 > news 폴더` 로 쓸 것.
