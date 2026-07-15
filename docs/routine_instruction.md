# 디자인 놀이터 — 일일 브리핑 자동 생성 (루틴 교체용 · WebSearch 전용 · 2026-07)

| 최종 갱신 | 상태 |
|---|---|
| 2026-07-14 | 라이브 루틴과 동기화 + 팝업 6필드 필수 검증(§5-2) 추가 |

> 이 문서 = **실제 라이브 루틴(루틴 UI)과 동일본**. 수정 시 루틴 UI도 함께 갱신할 것.


세션 시작 즉시 아래 절차를 자동 실행한다. 사용자 요청 없이 시작.
결과물은 이 세션 안에 저장하고 알림만 보낸다. **git/배포는 하지 않는다**(사람이 세션에서 검수 후 직접 배포).

> **이 환경의 제약(중요):** 이 세션은 뉴스 도메인으로의 아웃바운드 접속이 막혀 있다(WebFetch 시 403). **뉴스 기사 페이지는 WebFetch 하지 말 것.** 기사 정보는 **오직 WebSearch 결과(제목·게재일·요약 스니펫)**로만 수집한다. (단, `raw.githubusercontent.com`은 허용되므로 template·index.json·published_urls.json은 WebFetch 가능.)
> 스니펫 기반이라 날짜·세부가 부정확할 수 있다 → **사람이 세션에서 반드시 검수한다.**

> **원칙:** HTML/CSS는 직접 정의하지 않는다. 디자인·구조의 단일 기준은 GitHub 최신 `template.html`이며, 매 실행 시 불러와 그대로 복제하고 **카드만 채운다.**

> **갱신 이력:** 2026-07-14 — 팝업 6필드 필수 검증(§5-2) 추가. 7/14 브리핑에서 `data-impact-score`·`data-comment` 누락(옛 `data-impact` 텍스트 사용)으로 실무영향도·큐레이션노트가 안 뜬 사고 재발 방지. / 2026-07-12 — 발행 중복 차단 관문 추가(§0 대장 불러오기 · §5 대장 대조 필수화 + 확인 한 줄 강제 · §10 배포 시 대장 재생성). 2026-07 다수 중복(RIBA·zdnet·design.co.kr·archdaily·yanko)의 원인이 이 대조 누락이었음.

---

## 0. 최신 파일 불러오기 (가장 먼저, 필수 — 여기만 WebFetch 허용)

WebFetch로 아래 세 파일을 읽는다(raw.githubusercontent는 접속 허용됨). **매 실행 새로 읽는다(캐시 금지).**
```
https://raw.githubusercontent.com/kei-insu/dinol-news/main/template.html
https://raw.githubusercontent.com/kei-insu/dinol-news/main/index.json
https://raw.githubusercontent.com/kei-insu/dinol-news/main/published_urls.json
```
- **template.html**: `<head>`·header·section·footer·드로어(팝업) 마크업, 외부 에셋 링크(`../../../assets/…`)를 **그대로 기준**으로 삼는다. 스타일 값은 임의로 바꾸지 않는다.
- **index.json**: 아카이브 목록. **맨 앞 = 최근 발행일**을 확인한다.
- **published_urls.json**: 발행 이력 대장(형식 `{"기사URL": "YYYYMMDD"}`). **이미 발행된 기사를 다시 쓰지 않기 위한 대조용**이다. §5에서 후보 URL과 1:1 대조한다. (이 파일은 배포 때 사람이 재생성하므로 항상 직전 배포까지의 발행분을 담고 있다.)
- template 접근 실패 시 대체: `https://kei-insu.github.io/dinol-news/template.html`

## 1. 날짜·기간
- 오늘 날짜(GMT+9, `YYYYMMDD`)를 확인한다.
- 수집 기간 = index.json 최근 발행일 다음날 ~ 오늘.(비면 며칠 넓혀도 됨)

## 2. 중복 생성 방지
index.json에 오늘 날짜가 이미 있으면 → 생성 생략, "오늘 브리핑이 이미 있습니다" 알림. 없으면 진행.

---

## 3. 기사 수집 — WebSearch 전용 (본문 fetch 금지)

**8카드 목표: AI 4 + Design 4.** 국내·해외 섞되 50:50 강제는 아님(모두 한글 표시라, 기간 내 좋은 기사 우선). 국내가 얇으면 해외 비중↑.

방법:
1. 주제/소스별로 **WebSearch를 여러 번** 돌린다(아래 소스명·키워드 + 날짜 조합). 예: `인공지능신문 AI 7월`, `dezeen design news`, `techcrunch AI [오늘날짜]`.
2. 각 검색 결과에서 **제목·출처·게재일·요약 스니펫**을 취한다. **기사 페이지는 WebFetch 하지 않는다.**
3. 게재일이 스니펫에 안 보이거나 애매하면 → **그 기사 제목+출처로 한 번 더 검색**해 날짜를 교차확인. 그래도 불명확하면 그 카드는 **제외**.
4. **후보를 넉넉히 모은다(목표 8개보다 여유 있게).** §5의 대장 대조에서 중복이 걸러지면 즉시 대체할 예비 기사가 필요하다.

### AI 소스(검색어에 활용)
국내: 인공지능신문(aitimes.kr)·AI타임스(aitimes.com)·zdnet.co.kr·etnews.com·bloter.net
해외: techcrunch·the verge·wired·buildfastwithai·UN News(정책)

### Design 소스
해외: dezeen·yanko design·it's nice that·core77·archdaily
국내: designdb·kidp·etnews(디자인)·연합뉴스

디자인 카테고리는 UXUI·시각·제품·공간·건축·패키지·브랜딩·편집·게임 등 다양하게. **주가·투자 등 무관한 것 제외.**

---

## 4. 썸네일 = 그라디언트 + 한글 라벨
모든 카드는 gradient 클래스 + `.noise` + 한글 `.thumb-label`. (OG 이미지·`thumb-img`는 쓰지 않는다 — 어차피 이미지 fetch도 막힘.)

---

## 5. 검증 — 발행 중복 차단이 최우선 관문 (건너뛰기 금지)

### 5-0. 발행 대장 대조 (필수 관문 · 카드 확정 전 반드시 통과)
⚠️ 2026-07 다수 중복(RIBA·zdnet·design.co.kr·archdaily·yanko)의 원인이 바로 이 대조를 라이브 루틴이 **조용히 건너뛴 것**이었다. **절대 생략하지 않는다.**

1. 0번에서 불러온 `published_urls.json`(형식 `{기사URL: YYYYMMDD}`)을 **후보 카드 URL과 1:1 대조**한다.
2. 후보 URL이 대장에 **이미 있으면** → 그 카드를 버리고 **다른 신규 기사로 대체**(같은 기사 재발행 금지).
3. URL이 달라도 **최근 3~4일 브리핑과 같은 사건·주제**면 재탕으로 보고 배제(제목·핵심 사실이 겹치면 URL이 달라도 중복 취급).
4. **대조 결과를 §9 알림과 §9-1 파일 제시에 반드시 한 줄 남긴다:**
   > 대장 대조: 후보 N · 중복 제외 M · 최종 8(전부 신규)

   **이 줄이 없으면 관문을 건너뛴 것으로 간주 → 검수자는 배포를 보류한다.**

### 5-1. 이어서 아래도 확인
1. 브리핑 **내부** URL 중복 없음(동일 URL 1카드).
2. 게재일 = **검색 결과에 표시된 날짜**로 판단, 애매하면 추가 검색 교차확인, 안 되면 제외.
3. 검색 결과가 **개별 기사 페이지**인지 URL·제목으로 판단 — **목록·롤업·태그·홈·월간특집·리스티클 URL 금지**. (예: "○월 최고의 EDC 8선", "아크데일리 ○월 편집 주제" 같은 묶음/특집 페이지는 카드로 쓰지 않는다. 이런 페이지는 며칠 뒤 재등장해 중복을 유발한다.)
4. 카드 요약·제목이 검색 스니펫과 모순되지 않게 작성(스니펫에 없는 사실을 단정하지 말 것).
5. AI 4 + Design 4 균형.

### 5-2. 팝업 6필드 필수 검증 (누락 시 재작성 · 건너뛰기 금지)
⚠️ 2026-07-14 브리핑에서 `data-impact-score`·`data-comment`가 누락돼(옛 `data-impact` 텍스트 사용) 드로어에 **실무 영향도·큐레이션 노트가 안 뜬 사고**가 있었다. 카드 확정 전 아래를 반드시 통과한다.

카드 8장을 **1장씩** 점검해, 각 카드가 아래 6필드를 **전부** 가졌는지 확인한다:
`data-summary` · `data-points` · `data-designer` · `data-impact-score` · `data-recommend` · `data-comment`
1. **하나라도 빠졌거나 형식이 틀리면 그 카드를 재작성**한다(빈 채로 넘기지 않는다).
2. ⚠️ `data-impact-score`는 **정수 1~5**여야 한다. `data-impact`(텍스트)는 드로어가 렌더하지 못하므로 **절대 쓰지 않는다**.
3. ⚠️ `data-comment`(큐레이션 노트, 2~3문단)는 **필수**다. 절대 생략하지 않는다. (이 사이트의 핵심 부가가치)
4. 영문 카드는 위 6필드 + `-kr` 짝(`data-summary-kr`·`data-points-kr`·`data-designer-kr`·`data-recommend-kr`·`data-comment-kr`) + `data-title-en`도 확인.
5. 점검 결과를 §9 알림·§9-1 파일 제시에 한 줄 남긴다: 「6필드 검증: 8/8 통과」 (통과 못 하면 배포 보류)

---

## 6. HTML 생성 (Write → 세션에 저장)

template.html을 복제하고 **아래 세 곳만** 채운다. 그 외(스타일·header·footer·드로어·스크립트·에셋 링크)는 원본 그대로.
1. `<title>` = `디자인 놀이터 — YYYY. MM. DD`, `.site-date` = 영문 날짜(예: `July 8, 2026`)
2. **AI·Design 섹션의 `.grid` 내부** = 7번 패턴으로 카드 8장
3. (template 스크립트/READ_KEY가 날짜 하드코딩을 요구하면) 오늘 날짜로 맞춤

저장: `/home/user/Dinol_news_YYYYMMDD.html` (텍스트 요약 출력 금지, 파일로만).
※ 배포 위치는 `news/2026/MM/`이며 template 상대경로가 이를 전제한다.

---

## 7. 카드 패턴 (★현재 구조 — 반드시 이대로)

**공통**
- **라벨·카드 제목은 영문 기사도 한글.** 영어 원제목은 `data-title-en`에 보존.
- 팝업 6필드를 **모두** 채운다: `data-summary`·`data-points`·`data-designer`·`data-impact-score`·`data-recommend`·`data-comment`. 영문 기사는 각 `-kr` 짝도. **하나라도 빠지면 카드 재작성(§5-2 검증). `data-impact`(텍스트)·빈 `data-comment` 금지.**
- `data-points`는 3개를 `|`로. `data-impact-score`는 **1~5 정수**. `data-comment`(큐레이션 노트)는 **2~3문단(실제 \n)**.
- 본문에 **em대시(—) 금지**. `data-category` 예: `AI · 정책`, `Design · Architecture`.
- gradient 8종 다양하게: `g-teal g-navy g-slate g-plum g-violet g-amber g-crimson g-forest`.
- **card-footer(좋아요·공유)는 template 예시 카드의 것을 그대로 복사**(직접 작성 금지).
- 첫 카드 `class="card featured"` 허용.

### 한국어 기사 카드
```html
<a class="card" href="[URL]" target="_blank"
   data-category="[예: AI · 정책]"
   data-summary="[한 줄 요약]"
   data-points="[포인트1|포인트2|포인트3]"
   data-designer="[디자이너 관점 1~2문장]"
   data-impact-score="[1~5]"
   data-recommend="[활용 추천]"
   data-comment="[큐레이션 노트 2~3문단]">
  <div class="thumb [gradient]">
    <div class="noise"></div>
    <span class="thumb-label">[한글 라벨]</span>
  </div>
  <div class="card-body">
    <div class="card-source">[출처] · [YYYY. MM. DD]</div>
    <div class="card-title">[한글 제목]</div>
  </div>
  [template 카드의 card-footer 그대로]
</a>
```

### 영문 기사 카드 (한글 표시 + 영어 원문 보존)
```html
<a class="card" href="[URL]" target="_blank"
   data-category="[예: Design · Architecture]"
   data-summary="[English summary]" data-summary-kr="[한국어 요약]"
   data-points="[EN p1|p2|p3]" data-points-kr="[한국어 포인트]"
   data-designer="[English angle]" data-designer-kr="[한국어 관점]"
   data-impact-score="[1~5]"
   data-recommend="[English rec]" data-recommend-kr="[한국어 추천]"
   data-comment="[English comment]" data-comment-kr="[한국어 코멘트]"
   data-title-en="[영어 원제목 원문]">
  <div class="thumb [gradient]">
    <div class="noise"></div>
    <span class="thumb-label">[한글 라벨]</span>
    <span class="thumb-en">EN</span>
  </div>
  <div class="card-body">
    <div class="card-source">[Source] · [YYYY. MM. DD]</div>
    <div class="card-title">[한글 제목]</div>
  </div>
  [template 카드의 card-footer 그대로]
</a>
```

---

## 8. index.json 갱신
0번에서 불러온 index.json 배열 맨 앞에 오늘 `YYYYMMDD` 추가(중복이면 생략) → `/home/user/index.json` 저장.

> **주의:** 루틴은 `published_urls.json`을 **읽기만** 한다(§0·§5). 대장 파일 자체는 **갱신하지 않는다** — 배포 시 사람이 브리핑 파일에서 재생성한다(§10).

## 9. 완료 알림
PushNotification: `디자인놀이터 브리핑 초안 생성 — AI [N] / Design [N] / [YYYY-MM-DD]. 대장 대조: 후보 N · 중복 제외 M · 최종 8(전부 신규). 6필드 검증: 8/8 통과. 검색 스니펫 기반 초안이니 세션에서 검수 후 배포하세요.`

## 9-1. 파일 제시 (필수)
파일 저장 후, 생성한 두 파일을 사용자가 바로 받을 수 있도록 제시한다:
- Dinol_news_YYYYMMDD.html (다운로드 링크)
- index.json (다운로드 링크)

그리고 아래를 함께 출력한다:
- **대장 대조 결과 한 줄**: 「대장 대조: 후보 N · 중복 제외 M · 최종 8(전부 신규)」 (§5-0 필수)
- "AI N / Design N, 게재일·사실관계 검수 후 news/2026/MM/ 에 배포하세요" 안내

## 10. 검수·배포 (사람)
세션에서 `Dinol_news_YYYYMMDD.html` 검수(제목·요약·출처·**날짜 정확성**·팝업 필드 + **§5-0 대장 대조 한 줄 존재 여부**) → 이상 없으면 `index.json`과 함께 다운로드 → repo `news/2026/MM/`·루트에 넣는다.
**배포 직전, 레포 루트에서 대장을 재생성한다:**
```
python scripts/build_published_urls.py
```
→ "중복 등장 URL 없음" 확인 후 `git add … → commit → push`(또는 `./deploy.ps1 "메시지"`). 이렇게 하면 오늘 발행한 URL이 대장에 반영되어, 다음 실행의 §5-0 대조가 최신 상태로 작동한다.
