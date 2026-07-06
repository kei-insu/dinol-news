# 디자인 놀이터 — 일일 브리핑 자동 생성 (교체용 지침)

세션 시작 즉시 아래 절차를 자동 실행한다. 사용자 요청 없이 즉시 시작.

> **중요:** 이 지침에는 HTML/CSS를 직접 넣지 않는다.
> **구조**의 단일 기준은 GitHub 최신 `template.html`, **스타일·JS**는 공용 파일
> `assets/dinol.css` · `assets/dinol.js` 이다(2026-07-06 공용화 리팩터링).
> template은 이 둘을 `../../../assets/`로 **참조만** 하며, 매 실행 시 template을 불러와 그대로 복제한다. (아래 0번)

---

## 0. 최신 템플릿 불러오기 (필수 · 가장 먼저)

WebFetch로 아래 URL을 읽어 **최신 HTML 구조와 공용 자산 참조(`assets/dinol.css`·`assets/dinol.js`)**를 확보한다. (스타일·JS 본문은 template이 아니라 공용 파일에 있으며, template은 참조만 갖는다.)

```
https://raw.githubusercontent.com/kei-insu/dinol-news/main/template.html
```

- template은 스타일·JS를 인라인으로 갖지 않고 `<link rel="stylesheet" href="../../../assets/dinol.css">` · `<script src="../../../assets/dinol.js"></script>`로 **참조**한다. 이 참조 태그와 `<body>`의 header · section · footer · 드로어(팝업) 마크업을 **그대로 기준**으로 삼는다. **공용 CSS/JS 파일(`dinol.css`·`dinol.js`) 자체는 브리핑 생성 시 건드리지 않는다.**
- 폰트 크기·굵기·컬러·자간, 버튼/아이콘 크기, 푸터 구조 등 **어떤 스타일 값도 임의로 바꾸지 않는다.**
- 만약 raw.githubusercontent.com 접근이 실패하면 대체 URL을 사용한다:
  `https://kei-insu.github.io/dinol-news/template.html`

## 1. 날짜 확인
currentDate 컨텍스트에서 오늘 날짜(YYYY-MM-DD)를 확인한다.

## 2. 파일 존재 여부 확인
`/home/user/news/YYYY/MM/Dinol_news_YYYYMMDD.html`(오늘 날짜, news/연/월 폴더)이 이미 존재하면 → 생성 생략, PushNotification으로 "오늘 브리핑이 이미 생성되어 있습니다." 알림 전송.
없으면 → 아래 절차 즉시 진행.

---

## 3. 기사 수집

수집 기간: 오늘 + 전일. WebSearch + WebFetch로 기사 본문의 실제 게재일 직접 확인.

### [AI 섹션] 최소 4카드, KR 50% + EN 50%
- 한국어: aitimes.com, aitimes.kr, fnnews.com, sedaily.com, etnews.com, bloter.net, zdnet.co.kr
- 영문: buildfastwithai.com, techcrunch.com, theverge.com, wired.com

### [디자인 섹션] 최소 4카드, KR 50% + EN 50%
- 한국어: designdb.com, design.co.kr, ajunews.com, asiae.co.kr, mt.co.kr, kidp.or.kr, etnews.com, yna.co.kr, newsis.com
- 영문: dezeen.com, archdaily.com, core77.com, itsnicethat.com

디자인 카테고리: UXUI, 시각, 패키지, 제품, 인테리어, 공간, 게임, 광고, 편집, 패션, 브랜딩 등 다양하게.
AI·디자인과 직접 관련 없는 콘텐츠(주가·투자 정보 등) 제외.

---

## 4. 썸네일 이미지

각 기사 페이지 WebFetch 시 `<meta property="og:image" content="…">` 태그 추출.
- OG 이미지 있음 → `<img class="thumb-img" src="[URL]" alt="">` 삽입. gradient 클래스·`.noise`·`.thumb-label` 제거.
- OG 이미지 없음 → gradient 클래스 + `.noise` + `.thumb-label` 사용.

---

## 5. 콘텐츠 검증 (필수)

1. URL 중복 없음 — 동일 URL은 1카드만 허용
2. 게재일이 수집 기간 내인지 본문에서 직접 확인 (검색결과 날짜 X, 본문 날짜 O)
3. 카드 타이틀·내용이 링크 페이지와 일치 (목록·홈·태그 페이지 URL 금지)
4. 빈 링크·깨진 링크 없음
5. 섹션별 KR:EN = 50:50 충족

---

## 6. HTML 파일 생성

Write 도구로 **`/home/user/news/YYYY/MM/Dinol_news_YYYYMMDD.html`** 저장 (예: `news/2026/07/Dinol_news_20260703.html`). news/연/월 폴더가 없으면 먼저 생성한다. **텍스트 요약 출력 금지.**

> **폴더 구조**: 브리핑 파일은 `news/YYYY/MM/` 아래에 둔다(최상위가 아님). template.html의 이미지·링크 경로는 이미 `../../../`(상위 3단계)로 되어 있어, `news/YYYY/MM/`에 저장하면 루트의 `assets/`·`archive.html`·`privacy.html`을 정확히 참조한다. **경로는 수정하지 말고 template 그대로 복제**한다.

**생성 방식 — 0번에서 불러온 template.html을 복제하고, 아래 세 곳만 오늘 내용으로 채운다:**

1. **`<title>` 과 `.site-date`** — 오늘 날짜 (title은 `디자인 놀이터 — YYYY. MM. DD`, site-date는 영문 `예) July 2, 2026`)
2. **AI 섹션 · Design 섹션의 `.grid` 내부 카드** — 7번 패턴으로 오늘 수집한 카드 채움

이 **두 곳만** 채운다. READ_KEY는 파일명에서 자동 추출되므로 손대지 않는다(8번 참조). 그 외 `<head>`의 `<link>`·폰트, 하단 `<script src>` 참조, header/footer/버튼/드로어 마크업은 **template 원본 그대로 유지**한다(경로 `../../../` 절대 변경 금지). 날짜는 `YYYY. MM. DD` 형식 하드코딩(replace/치환 연산 금지). 영문 기사만 EN 배지 표시 + `data-title-kr`·`data-summary-kr`(한국어 번역) 속성 추가.

---

## 7. 카드 HTML 패턴

> template.html의 `.grid` 내부 카드 구조와 동일해야 한다. 아래는 그 기준 패턴.
>
> **썸네일 라벨 언어 규칙**: `thumb-label`은 기사 원문 언어에 맞춘다 — 영문 기사(EN 배지)는 **영문 라벨**, 한글 기사는 **한글 라벨**.

### 한국어 기사 카드
```html
<a class="card" href="[URL]" target="_blank"
   data-category="[카테고리]"
   data-summary="[한 줄 요약]"
   data-designer="[디자이너 관점]"
   data-impact="[실무 영향도]"
   data-points="[볼포인트1|볼포인트2|볼포인트3]"
   data-recommend="[추천]">
  <div class="thumb [gradient클래스]">
    <div class="noise"></div>
    <span class="thumb-label">[라벨]</span>
  </div>
  <div class="card-body">
    <div class="card-source">[출처] · [YYYY. MM. DD]</div>
    <div class="card-title">[제목]</div>
  </div>
  <div class="card-footer"><div class="card-actions"><span class="act act-like" role="button" aria-label="좋아요"><svg viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg><span class="act-count"></span></span><span class="act act-share" role="button" aria-label="공유"><svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></span></div><span class="arrow">↗</span></div>
</a>
```

### 영문 기사 카드 (EN 배지 + 번역 속성 필수)
```html
<a class="card" href="[URL]" target="_blank"
   data-category="[카테고리]"
   data-summary="[English one-line summary]"      data-summary-kr="[한 줄 요약]"
   data-designer="[Designer's angle]"             data-designer-kr="[디자이너 관점]"
   data-impact="[Practical impact]"               data-impact-kr="[실무 영향도]"
   data-points="[point1|point2|point3]"           data-points-kr="[볼포인트1|볼포인트2|볼포인트3]"
   data-recommend="[Recommendation]"              data-recommend-kr="[추천]"
   data-title-kr="[한국어 제목 번역]">
  <div class="thumb [gradient클래스]">
    <div class="noise"></div>
    <span class="thumb-label">[Label]</span>
    <span class="thumb-en">EN</span>
  </div>
  <div class="card-body">
    <div class="card-source">[Source] · [YYYY. MM. DD]</div>
    <div class="card-title">[English Title]</div>
  </div>
  <div class="card-footer"><div class="card-actions"><span class="act act-like" role="button" aria-label="좋아요"><svg viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg><span class="act-count"></span></span><span class="act act-share" role="button" aria-label="공유"><svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></span></div><span class="arrow">↗</span></div>
</a>
```

### 요약 6필드 작성 규칙 (팝업용)
카드 클릭 시 뜨는 팝업에 아래 6개 필드가 표시된다. 각 카드에 `data-*`로 담는다.
- **`data-category`** — 카테고리 (언어 공유, 예: `AI · UX · Tool`, `디자인 · 브랜딩`)
- **`data-summary`** — 한 줄 요약 (1문장)
- **`data-designer`** — 디자이너 관점 (디자이너에게 어떤 의미인지 1~2문장)
- **`data-impact`** — 실무 영향도 (`높음/중간/낮음 · 어떤 실무자에게 유용한지`)
- **`data-points`** — 볼 포인트 2~3개, **`|`(파이프)로 구분**
- **`data-recommend`** — 추천 (한 줄, 예: `팀 공유 추천 · 디자인 시스템 담당자 저장 추천`)

영문 기사는 위 기본 속성(영문) + 각각의 `-kr`(한국어 번역) 속성을 함께 넣는다. 카테고리는 언어 공유라 `-kr` 불필요.
값이 비면 팝업에서 해당 필드는 자동으로 숨겨지므로, 채울 수 있는 필드만 넣어도 된다(최소 `data-summary`는 필수).

### OG 이미지가 있는 카드
```html
<a class="card" href="[URL]" target="_blank" data-summary="[요약]">
  <div class="thumb">
    <img class="thumb-img" src="[og:image URL]" alt="">
    <!-- EN 기사인 경우 <span class="thumb-en">EN</span> 추가 -->
  </div>
  <div class="card-body">
    <div class="card-source">[출처] · [YYYY. MM. DD]</div>
    <div class="card-title">[제목]</div>
  </div>
  <div class="card-footer"><div class="card-actions"><span class="act act-like" role="button" aria-label="좋아요"><svg viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg><span class="act-count"></span></span><span class="act act-share" role="button" aria-label="공유"><svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></span></div><span class="arrow">↗</span></div>
</a>
```

### 그라디언트 클래스 (11종, 카드마다 다양하게 배분)
`g-indigo` / `g-violet` / `g-teal` / `g-crimson` / `g-forest` / `g-slate` / `g-amber` / `g-plum` / `g-olive` / `g-navy` / `g-rust`

- **첫 카드에는 `class="card featured"`** 도 허용(template과 동일).

---

## 8. READ_KEY 규칙
READ_KEY는 **자동 처리**된다 — `assets/dinol.js`가 파일명(`Dinol_news_YYYYMMDD.html`)에서 날짜를 추출해 `dinol_read_YYYYMMDD` 키를 생성한다. **브리핑 HTML에서 READ_KEY를 직접 쓰거나 수정하지 않는다.** 파일명 규칙(`Dinol_news_YYYYMMDD.html`)만 지키면 날짜별 읽음상태가 자동으로 분리된다.

---

## 9. 아카이브 목록(index.json) 갱신
`/home/user/index.json`(루트 유지) 을 읽어, 오늘 날짜(`YYYYMMDD` 문자열)가 없으면 배열에 **추가**하고 저장한다. index.json에는 **날짜 문자열만** 넣는다(경로 아님). index.html·archive.html이 날짜에서 `news/YYYY/MM/` 경로를 조립한다.
(형식: `["20260702","20260701", …]` — 아카이브 화면이 이 목록을 읽어 월별로 그룹핑한다.)

## 10. 완료 후
PushNotification 도구로 아래 형식 알림 전송:
`디자인놀이터 브리핑 생성 완료 — AI [N]카드 / Design [N]카드 / [YYYY-MM-DD]`
