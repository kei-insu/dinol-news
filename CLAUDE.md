# 디자인 놀이터 — 세션 시작 지침

이 세션이 시작되면 아래 절차를 **자동으로** 실행한다. 사용자의 별도 요청 없이 즉시 시작할 것.

---

## 공통 정책: 문서 자동 동기화 (필수)

코드·UI·동작·구조를 수정할 때는, 그 내용을 문서화하는 **관련 문서를 같은 작업에서 반드시 함께 갱신**한다. 사용자의 별도 요청이 없어도 자동으로 반영한다. (문서와 코드가 어긋나면 다음 작업에서 같은 실수가 재발하므로 "코드 수정 = 문서 수정"을 한 세트로 처리한다.)

- **대상 문서**: `design_guide.md`(디자인·UI·인터랙션 스펙) · `routine_instruction.md`(브리핑 생성 절차·카드 패턴) · `claude.md`(세션·정책) · `dinol_policy.md`(콘텐츠 정책) · `news_sources.md`(크롤링 소스)
- **트리거 예**: 팝업 필드·`data-*` 속성, 카드 마크업, 셰브론·버튼·컬러 등 UI, 파일 구조·경로, READ_KEY 등 로직, 공용 CSS/JS 구조 변경
- 변경 항목에는 날짜(예: `2026-07-06`)를 남겨 추적 가능하게 한다.

### 파일명 규칙 (2026-07-06, 전면 소문자 통일)
- **모든 파일 = 소문자.** 여러 단어는 밑줄(`_`) 또는 케밥(`-`)으로 연결한다.
  - 문서(.md): `claude.md` · `design_guide.md` · `routine_instruction.md` · `news_sources.md` · `dinol_policy.md`
  - 코드·자산·페이지: `dinol.css` · `dinol.js` · `dinol-firebase.js` · `template.html` · `index.html` · `index.json` · `archive.html` · `privacy.html`
- **예외 — 일일 브리핑은 `Dinol_news_YYYYMMDD.html` 유지**(`news/YYYY/MM/`). `dinol.js`의 READ_KEY 정규식과 아카이브 URL 생성이 이 패턴에 묶여 있어 그대로 둔다.
- 새 파일도 소문자 규칙을 따른다.
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

> **스타일 단일 기준(디자인 가이드):** 폰트 크기·굵기·컬러·자간, 버튼/아이콘 크기, 푸터 구조 등 모든 시각 스펙은 `template.html`을 **그대로 복사**한다. 임의로 값을 재생성하지 말 것. 전체 스펙 표는 `design_guide.md` 참조. (핵심: 섹션헤더 AI/Design 21px·자간 7px, 버튼 텍스트 16px/w500, EN 배지 12px/italic·명도 유지, 썸네일 라벨 흰색 0.42, 푸터 저작권 13px·안내문 13px 한 덩어리(`<br>`)·개인정보처리방침 16px 밑줄.)

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

## 디놀 톡톡 댓글 기능 (2026-07-07)

방명록 글에 댓글 추가. 서브컬렉션 `guestbook/{글ID}/comments/{댓글ID}` = `{nick, body, pwHash, createdAt}`. 비번 4자리·수정/삭제는 방명록과 동일(클라이언트 SHA-256 검증 + 마스터 481516). 댓글 100자.
- 구현: `assets/dinol-firebase.js`(댓글 CRUD·지연로딩·⋯옵션메뉴·이모지피커), `assets/dinol.css`(댓글/옵션/피커 스타일), `firestore.rules`(서브컬렉션+commentCount 규칙).
- **글·댓글 수정/삭제를 ⋯ 옵션 버튼(팝업)으로 통일**(상시노출 수정/삭제 버튼 폐기). 글 문서에 `commentCount` 필드로 "댓글 N" 표시(increment).
- 캐비앗: 글 삭제 시 댓글 서브컬렉션은 자동 삭제 안 됨(고아 문서).
- UI 스펙 상세는 design_guide.md §10.

## 브리핑 자동 생성 (2026-07-07)
Claude Code로 크롤·큐레이션·빌드까지 자동, 검수·배포는 사람. 상세 절차 = routine_instruction.md "Claude Code 자동 생성 루틴". 빌드는 `python scripts/build_briefing.py scripts/cards.json`(카드 JSON→HTML+index.json+자가검증, push 안 함). 카드 스키마 예시 = `scripts/cards.example.json`.
