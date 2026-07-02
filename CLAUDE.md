# 디자인 놀이터 — 세션 시작 지침

이 세션이 시작되면 아래 절차를 **자동으로** 실행한다. 사용자의 별도 요청 없이 즉시 시작할 것.

---

## 자동 실행 절차

### 1. 오늘 날짜 확인
`currentDate` 컨텍스트에서 오늘 날짜(YYYY-MM-DD)를 확인한다.

### 2. 오늘 파일 존재 여부 확인
`/home/user/Dinol_news_YYYYMMDD.html` (오늘 날짜)이 이미 존재하는지 확인한다.
- **파일이 있으면** → 생성 생략, 사용자에게 "오늘 브리핑이 이미 생성되어 있습니다." 안내 후 대기
- **파일이 없으면** → 아래 절차 즉시 진행

### 3. 정책 파일 읽기
`/home/user/dinol_policy.md` 를 읽어 전체 정책을 숙지한다.

### 4. 참조 HTML 읽기
`/home/user/template.html` 을 읽어 CSS·카드 마크업·JS 검증 블록 구조를 파악한다.

### 5. 기사 수집 + OG 이미지 추출
수집 기간 = **오늘 + 전일**. WebSearch + WebFetch로 각 기사의 본문 게재일을 직접 확인한다.

**[AI 섹션] 최소 4카드, KR 50% + En 50%**
- 한국어: aitimes.com, aitimes.kr, fnnews.com, sedaily.com, etnews.com, bloter.net, zdnet.co.kr
- 영문: buildfastwithai.com, techcrunch.com, theverge.com, wired.com

**[디자인 섹션] 최소 4카드, KR 50% + En 50%**
- 한국어: designdb.com, design.co.kr, ajunews.com, asiae.co.kr, mt.co.kr, kidp.or.kr, etnews.com, yna.co.kr, newsis.com
- 영문: dezeen.com, archdaily.com, core77.com, itsnicethat.com

**[썸네일 이미지]** 기사 페이지 WebFetch 시 `<meta property="og:image" content="…">` 태그 추출.
- OG 이미지 있음 → 카드 썸네일에 `<img class="thumb-img" src="[URL]" alt="">` 삽입, gradient 클래스·`.noise`·`.thumb-label` 제거
- OG 이미지 없음 → 기존대로 gradient 클래스 + `.noise` + `.thumb-label` 사용

### 6. 콘텐츠 검증 (필수)
1. URL 중복 없음
2. 게재일이 수집 기간 내인지 본문에서 직접 확인
3. 카드 타이틀·내용이 링크 페이지와 일치 (목록·홈 페이지 URL 금지)
4. 빈 링크·깨진 링크 없음
5. 섹션별 KR:En = 50:50 충족

### 7. HTML 파일 생성 및 저장
**Write 도구로 `/home/user/Dinol_news_YYYYMMDD.html` 에 저장한다. 텍스트 요약 출력 금지.**

구조는 참조 파일(`template.html`)과 동일하게:
- 헤더: "디자인 놀이터" / "AI & Design News" / `.header-sep` (구분선) / 날짜
- 폰트: Cormorant Garamond 300 + Noto Sans KR 700 + Noto Serif KR 300
- 카드 그리드, EN 배지(영문 기사만, 흰색 텍스트·검정 배경 70%·검정 테두리 2px), 그라디언트 클래스, 읽음 상태(`.card-title.read`, weight 450 / `#a3a3a3`, localStorage 기반), 검증 JS 모두 포함
- **카드 그리드 끝(푸터 위)에 버튼 2개를 `.archive-cta-wrap`(세로 정렬, gap 12px)로 배치** — 두 버튼은 동일 폭(width 240px, 좌우 padding 16px)·동일 높이(min-height 48px, 모바일 터치 가이드 충족), 모두 검정 텍스트(#191919)
  - "AI & Design 아카이브" 버튼(`.archive-cta`, 그레이 배경 #c9ccd4, `href="./archive.html"`)
  - "디자인놀이터 오픈채팅방" 버튼(`.kakao-cta`, 카카오 옐로우 #FEE500, `href="https://open.kakao.com/o/g3XICwx"`, `target="_blank"` `rel="noopener noreferrer"`)
- **"맨 위로 ↑" 플로팅 버튼(`.to-top`, `#toTop`) 포함** — 모바일(≤580px)에서만 노출, 스크롤 600px 이상 시 `.show`로 페이드인, 클릭 시 상단으로 스무스 스크롤
- 푸터에는 개인정보처리방침 링크만 포함(아카이브 링크는 상기 pill 버튼으로 대체)
- `<head>`에 Google AdSense 자동 광고 스크립트(`ca-pub-XXXXXXXXXXXXXXXX`, template.html과 동일한 값) 포함
- 날짜는 하드코딩 (YYYY. MM. DD 형식, replace 연산 금지)

### 8. 아카이브 목록(index.json) 갱신
`/home/user/index.json` 을 읽어 오늘 날짜(YYYYMMDD)를 배열에 추가하고 다시 저장한다.
- 형식: 날짜 문자열 배열. 예) `["20260702", "20260701", "20260630"]`
- **이미 오늘 날짜가 있으면 추가하지 않는다** (중복 금지)
- 파일이 없으면 오늘 날짜 하나만 담아 새로 생성한다
- 정렬·중복 제거는 `archive.html`이 렌더링 시 처리하므로, 여기서는 오늘 날짜를 배열에 넣기만 하면 된다
- 이 파일은 `archive.html`이 읽어 "아카이브" 목록을 그리는 원본이다

### 9. 알림 전송
PushNotification 도구로 생성 결과를 알린다.

---

## 참고 파일
- 정책: `/home/user/dinol_policy.md`
- 구조 참조: `/home/user/template.html`
- 산출물: `/home/user/Dinol_news_YYYYMMDD.html`
- 아카이브 목록: `/home/user/index.json` (아카이브 목록 원본)
