# 디자인 놀이터 — 뉴스 브리핑 제작 정책

> 파일 저장 위치: `/home/user/dinol_policy.md`  
> 산출물 저장 위치: `/home/user/Dinol_news_YYYYMMDD.html`

---

## 1. 파일 규칙

| 항목 | 규칙 |
|---|---|
| 파일명 | `Dinol_news_YYYYMMDD.html` (예: `Dinol_news_20260630.html`) |
| 저장 위치 | `/home/user/` |
| 인코딩 | UTF-8 |

---

## 2. 크롤링 기간 정책

- **수집 범위: 해당일 + 전일**
  - 예) 오늘 2026-06-30이면 → 2026-06-29 ~ 2026-06-30 기사만 수집
- 기사 본문의 **실제 게재일**을 기준으로 판단 (검색 결과 날짜 × → 본문 날짜 ○)
- URL에 날짜가 인코딩된 소스 우선 활용 (검증 용이)

---

## 3. 크롤링 범위

- 뉴스 기사 + 소스 공유 + 인사이트 자료 등 다양한 읽을거리 포함
- **섹션별 최소 4개 이상** 카드 수집
- 디자인 카테고리는 다양하게 수집:
  - UXUI, 시각, 패키지, 제품, 인테리어, 공간, 굿즈, 게임, 광고, 편집, 출판, 패션, 브랜딩 등
- **AI·디자인과 직접 관련 없는 콘텐츠는 수집 제외** (예: AI 관련주 주가·투자 정보)
- 무료 매거진, 무료 SNS 채널(예: 브런치, 뉴스레터) 포함 가능
- 국내·해외 소스 모두 수집
- 단일 링크에 여러 콘텐츠가 포함된 경우, 해당 페이지의 **대제목을 카드 타이틀 기준**으로 사용

---

## 4. 언어 비율 정책

- **섹션별 한국어 : 영문 = 50:50 유지**
- 예) 6카드 섹션 → KR 3개 + En 3개
- 영문 기사로만 채워지지 않도록 한국어 소스 우선 탐색

### 한국어 소스 (디자인)
- `designdb.com` (국내 디자인 뉴스)
- `design.co.kr` (월간디자인)
- `ajunews.com`, `asiae.co.kr`, `mt.co.kr`, `zdnet.co.kr`
- `kidp.or.kr` (한국디자인진흥원)
- `etnews.com`, `yna.co.kr`, `newsis.com`

### 한국어 소스 (AI)
- `aitimes.com`, `aitimes.kr`
- `fnnews.com`, `sedaily.com`, `etnews.com`
- `bloter.net`, `zdnet.co.kr`

### 영문 소스 (디자인)
- `dezeen.com` (URL에 날짜 인코딩: `/YYYY/MM/DD/`)
- `archdaily.com`, `core77.com`, `itsnicethat.com`

### 영문 소스 (AI)
- `buildfastwithai.com`, `techcrunch.com`
- `theverge.com`, `wired.com`

---

## 5. 콘텐츠 검증 체크리스트 (크롤링 후 반드시 수행)

1. **URL 중복 확인** — 동일 URL은 1개 카드만 허용
2. **날짜 확인** — 기사 본문의 실제 게재일이 수집 기간(해당일+전일) 내인지 검증
3. **카드 타이틀 ↔ 목적지 URL 일치 확인**
   - 카드에 표시된 타이틀·내용이 링크 도착 페이지의 실제 내용과 일치해야 함
   - **콘텐츠의 최종 목적지는 반드시 본문 페이지** — 목록·메인·태그 페이지 URL 사용 금지
   - 실제 페이지를 확인하지 않은 내용은 카드에 기재하지 않음
4. **빈 링크·깨진 링크 사용 금지**
5. **언어 비율 최종 점검** — 섹션별 KR:En = 50:50 충족 여부 확인

---

## 6. 표기 규칙

| 항목 | 규칙 |
|---|---|
| 날짜 형식 | `YYYY. MM. DD` (예: `2026. 06. 30`) |
| 날짜 입력 방식 | **하드코딩** (replace/치환 연산 사용 금지) |
| 영문 배지 | 영문 기사만 `En` 배지 표시, 국문 기사는 배지 없음 |
| 언어 배지 위치 | 썸네일 영역 우측 상단 (absolute, top-right) |

---

## 7. HTML 레이아웃 구조

### 헤더 (4줄)
```
디자인 놀이터          ← Cormorant Garamond 300, #aaa, letter-spacing 5px
AI & Design News       ← Noto Sans KR 700, 46px, white
│ (구분선)             ← .header-sep: width 1px, height 24px, background #3a3a48, margin 10px 0 4px
July 1, 2026          ← 11px, letter-spacing 4px, #888
```

### 카드 구조
- 썸네일 (gradient 배경 + noise + 중앙 라벨 + En 배지)
  - **이미지 있는 경우**: 기사 본문 `og:image` 메타태그를 대표 이미지로 사용 (gradient 대체)
    - 이미지 여러 장이면 `og:image`(OG 태그) 우선 → 없으면 첫 번째 `<img>` 사용
    - 사이즈 처리: `object-fit: cover` + `object-position: center` (가로폭 기준 crop)
    - HTML 패턴: `<div class="thumb">` + `<img class="thumb-img" src="…" alt="">` + (En 배지 선택)
    - `.noise`, `.thumb-label` 미포함 (이미지가 있을 때는 라벨 불필요)
  - **이미지 없는 경우**: gradient 배경 + `.noise` + `.thumb-label` 사용
- 카드 본문 (출처·날짜 / 타이틀)
- 카드 푸터 (화살표 ↗ 만)
- featured 카드: `grid-column: span 2`, thumb 168px

### 그라디언트 클래스 (12종)
`g-indigo` `g-violet` `g-teal` `g-crimson` `g-forest` `g-slate`
`g-amber` `g-plum` `g-olive` `g-navy` `g-rust` + 향후 추가 가능

### 읽음 상태 (Read State)
- 카드를 한 번 열람(드로어 오픈)하면 `card-title`에 `.read` 클래스 부여
- 스타일: `font-weight: 450`, `color: #a3a3a3` (미열람 기본값 `font-weight: 600`, `color: #ffffff`)
- 열람 기록은 `localStorage`(`dinol_read_urls` 키, URL 배열)에 저장 → 페이지 재방문 시에도 유지
- 구현 위치: `template.html`의 `<style>` (`.card-title.read`)와 하단 `<script>`(`getReadUrls` / `markAsRead` / `applyReadState`)

### 검증 JS
페이지 하단 `<script>` 블록에서 DOMContentLoaded 시:
- 중복 URL → 빨간 테두리 + ⚠ 중복 링크 배지
- 빈 링크 → 노란 테두리 + ⚠ 링크 없음 배지
- 이슈 발생 시 하단 고정 배너 표시

### 푸터 (3줄)
```
© YYYY 디자인놀이터. All rights reserved.
본 서비스의 디자인, 구성, 자체 제작 콘텐츠에 대한 권리는 디자인놀이터에 있습니다.
제공되는 콘텐츠의 저작권은 각 언론사 및 원저작권자에게 있습니다.
```

---

## 8. 참고 파일

| 파일 | 설명 |
|---|---|
| `/home/user/template.html` | 디자인 템플릿 (CSS·카드·JS 구조 참고용) |
| `/home/user/Dinol_news_20260630.html` | 2026-06-30 기준 완성본 |
| `/home/user/dinol_policy.md` | 이 문서 |
