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
`/home/user/Dinol_news_20260630.html` 을 읽어 CSS·카드 마크업·JS 검증 블록 구조를 파악한다.

### 5. 기사 수집
수집 기간 = **오늘 + 전일**. WebSearch + WebFetch로 각 기사의 본문 게재일을 직접 확인한다.

**[AI 섹션] 최소 4카드, KR 50% + En 50%**
- 한국어: aitimes.com, aitimes.kr, fnnews.com, sedaily.com, etnews.com, bloter.net, zdnet.co.kr
- 영문: buildfastwithai.com, techcrunch.com, theverge.com, wired.com

**[디자인 섹션] 최소 4카드, KR 50% + En 50%**
- 한국어: designdb.com, design.co.kr, ajunews.com, asiae.co.kr, mt.co.kr, kidp.or.kr, etnews.com, yna.co.kr, newsis.com
- 영문: dezeen.com, archdaily.com, core77.com, itsnicethat.com

### 6. 콘텐츠 검증 (필수)
1. URL 중복 없음
2. 게재일이 수집 기간 내인지 본문에서 직접 확인
3. 카드 타이틀·내용이 링크 페이지와 일치 (목록·홈 페이지 URL 금지)
4. 빈 링크·깨진 링크 없음
5. 섹션별 KR:En = 50:50 충족

### 7. HTML 파일 생성 및 저장
**Write 도구로 `/home/user/Dinol_news_YYYYMMDD.html` 에 저장한다. 텍스트 요약 출력 금지.**

구조는 참조 파일(`Dinol_news_20260630.html`)과 동일하게:
- 헤더: "디자인 놀이터" / "AI & Design News" / `.header-sep` (구분선) / 날짜
- 폰트: Cormorant Garamond 300 + Noto Sans KR 700 + Noto Serif KR 300
- 카드 그리드, featured 카드, En 배지, 그라디언트 클래스, 검증 JS, 푸터 모두 포함
- 날짜는 하드코딩 (YYYY. MM. DD 형식, replace 연산 금지)

### 8. 알림 전송
PushNotification 도구로 생성 결과를 알린다.

---

## 참고 파일
- 정책: `/home/user/dinol_policy.md`
- 구조 참조: `/home/user/Dinol_news_20260630.html`
- 산출물: `/home/user/Dinol_news_YYYYMMDD.html`
