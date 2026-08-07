# 디자인 놀이터 — 일일 브리핑 자동 생성 (루틴 교체용 · WebSearch 전용 · 2026-08)

| 최종 갱신 | 상태 |
|---|---|
| 2026-08-07 | §1 브리핑 날짜 기준 변경(실행 당일 → 실행 시점 +1일) + 수동 재실행 보정. 22:00 실행 시 index.json 최신 항목과 충돌해 "이미 있음"으로 오판하던 문제 해소 |
| 2026-08-06 | §3 소스 목록 확장(국내 16→37 · 해외 41→58, AI×디자인·유럽·일본·중국 축 신설) + 크롤링 폭 최소 기준 + 계열 판정 주의 |
| 2026-08-03 | 카드 스키마 동기화(`data-category` 한국어 canonical · `data-category-en` · `data-position`) + 별점 루브릭 명문화 + §10 발행 게이트(브랜치·validate.py·localhost) |
| 2026-07-26 | §3-1 구성 균형 확정(섹션당 국내2·해외2 예외없음 · 동일매체 전체합산 2건) + AI 실무접점 목표 |
| 2026-07-14 | 라이브 루틴과 동기화 + 팝업 6필드 필수 검증(§5-2) 추가 |

> 이 문서 = **실제 라이브 루틴(루틴 UI)과 동일본**. 수정 시 루틴 UI도 함께 갱신할 것.


세션 시작 즉시 아래 절차를 자동 실행한다. 사용자 요청 없이 시작.
결과물은 이 세션 안에 저장하고 알림만 보낸다. **git/배포는 하지 않는다**(사람이 세션에서 검수 후 직접 배포).

> **이 환경의 제약(중요):** 이 세션은 뉴스 도메인으로의 아웃바운드 접속이 막혀 있다(WebFetch 시 403). **뉴스 기사 페이지는 WebFetch 하지 말 것.** 기사 정보는 **오직 WebSearch 결과(제목·게재일·요약 스니펫)**로만 수집한다. (단, `raw.githubusercontent.com`은 허용되므로 template·index.json·published_urls.json은 WebFetch 가능.)
> 스니펫 기반이라 날짜·세부가 부정확할 수 있다 → **사람이 세션에서 반드시 검수한다.**

> **원칙:** HTML/CSS는 직접 정의하지 않는다. 디자인·구조의 단일 기준은 GitHub 최신 `template.html`이며, 매 실행 시 불러와 그대로 복제하고 **카드만 채운다.**

> **갱신 이력:** 2026-08-03 — 07-25 이후 확정된 카드 스키마가 루틴에 반영돼 있지 않아 매일 같은 결함이 반복됐다. ① `data-category-en`(EN 카드 필수, 07-25 도입)이 §7 패턴에 없어 EN 카드마다 누락 → 7/26~8/1 브리핑에서 매일 수동 보정. ② `data-category` 예시가 `Design · Architecture`로 적혀 있어 8/3 브리핑에서 Design 4장 전부 canonical 위반(ERROR 4건). Design 카드는 `디자인 · `, AI 카드는 `AI · ` 접두어여야 한다. ③ `data-position`(07-25 도입) 누락. ④ 별점 루브릭(policy.md §1-2)이 없어 `data-impact-score`가 ★2~3에 몰림. ⑤ §10에 `validate.py` 실행과 브랜치 규칙이 없어 결함이 발행 후 브라우저에서야 발견됨. / 2026-07-26 — §3-1 구성 균형 규칙 확정. 46행의 "50:50 강제 아님"이 §3-1과 모순되어 삭제하고, 섹션당 국내 2·해외 2를 예외 없이 고정. 동일 매체 상한을 "섹션당 1건 권장"에서 "AI·Design 전체 합산 2건"으로 변경(섹션당 2건씩 넣어 4건이 되는 우회 차단). 실측 근거: 7/06~7/18은 5:5 충족 1일(8%)·Design 국내 0건이 11일이었으나, 7/19 이후 8일 연속 2:2 달성. / 2026-07-14 — 팝업 6필드 필수 검증(§5-2) 추가. 7/14 브리핑에서 `data-impact-score`·`data-comment` 누락(옛 `data-impact` 텍스트 사용)으로 실무영향도·큐레이션노트가 안 뜬 사고 재발 방지. / 2026-07-12 — 발행 중복 차단 관문 추가(§0 대장 불러오기 · §5 대장 대조 필수화 + 확인 한 줄 강제 · §10 배포 시 대장 재생성). 2026-07 다수 중복(RIBA·zdnet·design.co.kr·archdaily·yanko)의 원인이 이 대조 누락이었음.

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
- **브리핑 날짜 = 실행 시점 KST(GMT+9) 날짜 + 1일, `YYYYMMDD`.**
  (루틴은 매일 저녁 22:00 실행 기준 — 그날 밤에 "다음날" 브리핑을 미리 생성한다. **이하 이 문서의 모든 날짜 표기는 이 브리핑 날짜를 가리킨다.**)
- **보정:** 산출된 브리핑 날짜가 index.json 최근 발행일보다 **2일 이상** 앞서면, 브리핑 날짜를 `index.json 최근 발행일 + 1일`로 되돌린다.
  (22:00 자동 실행이 실패해 다음날 수동 재실행할 때 날짜가 하루 밀리는 것을 막는다. 정상 실행에서는 이 조건이 걸리지 않는다.)
- 수집 기간 = index.json 최근 발행일 다음날 ~ 브리핑 날짜.(비면 며칠 넓혀도 됨)

## 2. 중복 생성 방지
index.json에 브리핑 날짜가 이미 있으면 → 생성 생략, "해당 날짜 브리핑이 이미 있습니다" 알림. 없으면 진행.

---

## 3. 기사 수집 — WebSearch 전용 (본문 fetch 금지)

**8카드 목표: AI 4 + Design 4.** 구성 균형은 §3-1 을 따른다.

방법:
1. 주제/소스별로 **WebSearch를 여러 번** 돌린다(아래 소스명·키워드 + 날짜 조합). 예: `인공지능신문 AI 7월`, `dezeen design news`, `techcrunch AI [브리핑 날짜]`.
2. 각 검색 결과에서 **제목·출처·게재일·요약 스니펫**을 취한다. **기사 페이지는 WebFetch 하지 않는다.**
3. 게재일이 스니펫에 안 보이거나 애매하면 → **그 기사 제목+출처로 한 번 더 검색**해 날짜를 교차확인. 그래도 불명확하면 그 카드는 **제외**.
4. **후보를 넉넉히 모은다(목표 8개보다 여유 있게).** §5의 대장 대조에서 중복이 걸러지면 즉시 대체할 예비 기사가 필요하다.

### 3-1. 선별 정책 — 2026-07-26

**[구성 균형]**
- 하루 총 8장: **AI 4장 · Design 4장**.
- **각 섹션은 국내 2장 · 해외 2장으로 구성한다. 예외는 허용하지 않는다.**
- 전체 구성은 국내 4장 · 해외 4장이다.
- **국내·해외 구분은 기사 언어나 `.thumb-en` 배지가 아니라 원문을 발행한 매체의 국적을 기준으로 판정한다.**
  - 글로벌 매체의 한국 법인·한국판은 국내로, 본사 원문은 해외로 계산한다.
  - 예: `ZDNet Korea` · `Business Insider Korea` = 국내 / `TechCrunch` · `Dezeen` = 해외
  - `.thumb-en` 배지는 판정 결과를 표시하는 UI 요소이며 구성 균형의 판단 기준으로 쓰지 않는다.
- **동일 매체는 AI·Design 전체를 합산해 하루 최대 2건까지만 허용한다.**
  (섹션당 2건씩 넣어 총 4건이 되는 우회를 막는다)
- 동일 매체 또는 동일 계열사가 운영하는 매체는 하나의 소스로 계산한다.
  디자인플러스와 헤이팝은 디자인하우스 계열로 묶어 동일 소스로 센다.
- 국내 후보의 실무 가치가 낮더라도 지역 구성 기준은 유지하되, `data-impact-score` 는 실제 기준에 따라 낮게 평가한다.
  (지역 균형을 맞추려고 별점을 부풀리지 않는다)

**[AI 실무 접점]**
- AI 섹션은 **★4~5 카드를 최소 1장** 포함하는 것을 우선 목표로 한다.
- 적합한 후보가 없으면 별점을 임의로 높이지 않는다.
- ★4~5 카드가 없는 날은 §9-1 에 사유를 기록한다.
- **★1 카드에는 별도 수량 상한을 두지 않는다.**
  (정책·반도체·M&A 는 업계에서 중요할 수 있고, 별점이 이미 실무와의 거리를 표시한다)

**[별점 루브릭 — policy.md §1-2]**
- `data-impact-score` 는 아래 기준으로 매긴다. **★2~3 에 몰리지 않게 실제로 분산시킨다.**

| 점수 | 기준 |
|---|---|
| ★5 | 즉시 적용 가능한 방법론·툴 사용법 |
| ★4 | 실무에 적용 가능한 인사이트 |
| ★3 | 중간 |
| ★2 | 낮음 |
| ★1 | M&A · 정책 · 증시 |

- **디자인 방법론·툴 사용법 콘텐츠는 원칙적으로 ★4~5** 로 매긴다.
- 지역 균형이나 별점 분산을 맞추려고 점수를 부풀리거나 낮추지 않는다.

**[후보 선별]**
- **후보 풀 먼저.** 검색으로 N건 나왔다고 그 N건을 바로 채택하지 않는다. 여러 매체를 넓게 돌려 후보를 넉넉히 모은 뒤 그 안에서 고른다.
- **디자인 관련도 가중.** 후보를 "디자인 놀이터 독자 관점"의 관련도로 평가해 상위만 채택. AI 카드도 디자인 툴·생성형/크리에이티브 AI·브랜드/제품/UX 영향 등 관련도로 판단(단순 증시·실적·투자 뉴스는 제외).
- **날짜 분산.** 수집 창 안에서 같은 날짜 기사만 몰지 않는다.
- **최신성 vs 관련도.** 신선한 KR 건이 얇으면 관련도·품질을 우선한다(며칠 지난 건 허용). 단 그 이유를 §9-1 에 한 줄 남긴다.

> 소스 단일 출처는 `news_sources.md`. 아래는 그중 매일 도는 목록이다. **한쪽을 고치면 다른 쪽도 같은 변경에서 고친다.**
> WebSearch 전용이므로 URL 접근이 안 되는 매체도 **매체명을 검색어에 넣어** 후보를 찾는다(중국 매체 등).

### AI 소스 (넓게 크롤링 · 국내 16 · 해외 23)
- **국내 · AI 전문**: 인공지능신문(aitimes.kr)·AI타임스(aitimes.com)·테크42
- **국내 · IT 매체**: zdnet.co.kr·bloter.net·byline.network·etnews.com·디지털데일리(ddaily.co.kr)·IT조선
- **국내 · 스타트업·산업**: 플래텀·벤처스퀘어·매일경제·조선비즈 IT/사이언스·연합뉴스 IT/과학
- **국내 · 실무 커뮤니티**: 요즘IT(yozm.wishket)·GeekNews(news.hada.io)
- **해외 뉴스**: techcrunch·the verge·wired·ars technica·venturebeat·MIT Technology Review·UN News(정책)
- **해외 논평·큐레이션**: The Batch·Import AI·Simon Willison·TLDR AI·The Rundown AI·Hugging Face Blog
- **해외 기업·연구**: OpenAI News·Anthropic News·Google DeepMind·Google Research·Meta AI·Microsoft AI
- **AI×디자인**(이 축을 반드시 1회 이상 돌린다): Creative Bloq AI 섹션·Adobe Blog·Figma Blog·Canva Design School·European Commission(AI 규제)

### Design 소스 (넓게 크롤링 · 국내 21 · 해외 35)
- **국내 · 디자인 매체**: 디자인플러스(design.co.kr)·디자인 나침반(designcompass.org)·헤이팝(heypop.kr)·디자인정글(jungle.co.kr)·디자인DB(designdb·kidp)·네이버 디자인프레스
- **국내 · 브랜드·패션·컬처**: 아이즈매거진·Hypebeast KR·매거진 B·캐릿·디에디트(the-edit.co.kr)·무신사 매거진
- **국내 · 공간·전시·공공**: 서울디자인재단·DDP·KCDF·행복이 가득한 집·한국콘텐츠진흥원
- **국내 · 프로덕트·UX 실무**: 토스 tech·우아한형제들 기술블로그·요즘IT
- **국내 · 게임·리빙**: 게임메카·인벤·리빙센스(smlounge)
- **해외 종합**: dezeen·designboom·yanko design·it's nice that·core77·archdaily·creative boom·creative bloq·wallpaper*·design milk
- **해외 브랜드·그래픽·타이포**: Brand New·The Brand Identity·BP&O·The Dieline·AIGA Eye on Design·Print Magazine·Fonts In Use·Typewolf
- **해외 UX·트렌드**: UX Collective·NN/g·Smashing Magazine·Fast Company Co.Design·Codrops
- **해외 광고·캠페인**: Adweek·The Drum·Campaign·Muse by Clio
- **해외 모션·영상**: Motionographer·Stash Media·Art of the Title
- **유럽(EU)**: Slanted(DE)·Frame(NL)·Eye Magazine(UK)·Design Week(UK)
- **일본(JP)**: AXIS·Pen Online·JDN(Japan Design Net)·Casa BRUTUS·Spoon & Tamago·Tokyo Art Beat
- **중국(CN)**: 站酷 ZCOOL·Design360°·TOPYS ※URL 접근 불가, 검색어로만 사용

디자인 카테고리는 UXUI·시각·제품·공간·건축·패키지·브랜딩·편집·광고·모션·게임 등 다양하게. **주가·투자 등 무관한 것 제외.**

### 크롤링 폭 최소 기준
한 번에 8카드를 채우려면:
- AI: **국내 3회 + 해외 3회 + AI×디자인 2회 이상** 검색
- Design: **국내 3회 + 영어권 3회 + 유럽/일본/중국 중 2개 축 이상** 검색
- **국내 3회는 매번 다른 하위 축에서 뽑는다.** 위 국내 목록이 축별로 나뉘어 있는 이유다. 3회를 전부 '디자인 매체' 축에 쓰면 매일 같은 2~3곳만 나온다.
- 한 축에서 기간 내 신규가 없으면 **다음 축으로 넘어간다.** 같은 축을 3회 이상 재검색하지 않는다.

> **계열 판정 주의** — 계열 합산은 `news_sources.md`에 명시된 것만 적용한다(현재: 디자인플러스·헤이팝·행복이 가득한 집 = 디자인하우스). 문서에 없는 계열을 세션마다 즉석 판단하지 않는다. 확인되면 `news_sources.md`에 먼저 명시한다.

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
5. **§3-1 구성 균형 준수 확인:**
   - AI 4 + Design 4
   - 각 섹션 국내 2 + 해외 2 (예외 없음 · 매체 국적 기준)
   - 동일 매체·동일 계열 매체 **전체 합산 2건 이하**
   - AI 섹션 ★4~5 최소 1장 (없으면 §9-1 에 사유 기록)

### 5-2. 팝업 6필드 필수 검증 (누락 시 재작성 · 건너뛰기 금지)
⚠️ 2026-07-14 브리핑에서 `data-impact-score`·`data-comment`가 누락돼(옛 `data-impact` 텍스트 사용) 드로어에 **실무 영향도·큐레이션 노트가 안 뜬 사고**가 있었다. 카드 확정 전 아래를 반드시 통과한다.

카드 8장을 **1장씩** 점검해, 각 카드가 아래 6필드를 **전부** 가졌는지 확인한다:
`data-summary` · `data-points` · `data-designer` · `data-impact-score` · `data-recommend` · `data-comment`
1. **하나라도 빠졌거나 형식이 틀리면 그 카드를 재작성**한다(빈 채로 넘기지 않는다).
2. ⚠️ `data-impact-score`는 **정수 1~5**여야 한다. `data-impact`(텍스트)는 드로어가 렌더하지 못하므로 **절대 쓰지 않는다**.
3. ⚠️ `data-comment`(큐레이션 노트, 2~3문단)는 **필수**다. 절대 생략하지 않는다. (이 사이트의 핵심 부가가치)
4. 영문 카드는 위 6필드 + `-kr` 짝(`data-summary-kr`·`data-points-kr`·`data-designer-kr`·`data-recommend-kr`·`data-comment-kr`) + `data-title-en` + **`data-category-en`** 도 확인.
5. ⚠️ **`data-category` 접두어 검사(8장 전부).** Design 카드는 `디자인` 또는 `디자인 · ` 로, AI 카드는 `AI` 또는 `AI · ` 로 시작해야 한다. `Design · ` 은 **위반**이다.
6. ⚠️ **영문 슬롯이 한국어면 안 된다.** EN 카드의 `data-summary`·`data-points`·`data-designer`·`data-recommend`·`data-comment` 는 영문, `-kr` 짝은 한국어다. 두 값이 같으면(번역 누락) 재작성한다.
7. 점검 결과를 §9 알림·§9-1 파일 제시에 한 줄 남긴다: 「6필드 검증: 8/8 통과」 (통과 못 하면 배포 보류)

---

## 6. HTML 생성 (Write → 세션에 저장)

template.html을 복제하고 **아래 세 곳만** 채운다. 그 외(스타일·header·footer·드로어·스크립트·에셋 링크)는 원본 그대로.
1. `<title>` = `디자인 놀이터 — YYYY. MM. DD`(**브리핑 날짜** 기준), `.site-date` = 영문 날짜(**브리핑 날짜** 기준, 예: `August 8, 2026`)
2. **AI·Design 섹션의 `.grid` 내부** = 7번 패턴으로 카드 8장
3. (template 스크립트/READ_KEY가 날짜 하드코딩을 요구하면) 브리핑 날짜로 맞춤

저장: `/home/user/Dinol_news_YYYYMMDD.html` (**YYYYMMDD = 브리핑 날짜**, 텍스트 요약 출력 금지, 파일로만).
※ 배포 위치는 `news/2026/MM/`이며 template 상대경로가 이를 전제한다.

---

## 7. 카드 패턴 (★현재 구조 — 반드시 이대로)

**공통**
- **라벨·카드 제목은 영문 기사도 한글.** 영어 원제목은 `data-title-en`에 보존.
- 팝업 6필드를 **모두** 채운다: `data-summary`·`data-points`·`data-designer`·`data-impact-score`·`data-recommend`·`data-comment`. 영문 기사는 각 `-kr` 짝도. **하나라도 빠지면 카드 재작성(§5-2 검증). `data-impact`(텍스트)·빈 `data-comment` 금지.**
- `data-points`는 3개를 `|`로. `data-impact-score`는 **1~5 정수**. `data-comment`(큐레이션 노트)는 **2~3문단(실제 \n)**.
- 본문에 **em대시(—) 금지**.
- **`data-category` 는 한국어 canonical.** 구분자는 ` · ` 한 가지만 쓴다.
  - AI 카드: `AI · ` 로 시작 (예: `AI · 툴 · 생산성`, `AI · 정책 · 전략`)
  - Design 카드: **`디자인 · ` 로 시작** (예: `디자인 · 브랜딩 · 타이포그래피`, `디자인 · UXUI · 프로덕트`)
  - ⚠️ `Design · ` 은 위반이다. 발행 전 검증에서 ERROR 로 걸린다.
- **EN 카드는 `data-category-en` 을 함께 넣는다**(영문 표기, 예: `Design · Branding · Typography`). 국문 카드에는 넣지 않는다.
- **`data-position`**: 이 카드가 도움이 되는 직무를 `|` 로 **최대 2개**. 아래 20종 ID 외의 값은 쓰지 않는다.
  `ux-designer` `ui-designer` `product-designer` `service-designer` `brand-designer` `bx-designer` `graphic-designer` `editorial-designer` `motion-designer` `video-designer` `illustrator` `art-director` `industrial-designer` `space-designer` `architect` `package-designer` `typographer` `fashion-designer` `design-lead` `design-manager`
- gradient 는 아래 중에서 고르되 **8장 전부 서로 다른 색을 쓴다(중복 금지)**: `g-teal g-navy g-slate g-plum g-violet g-amber g-crimson g-forest g-indigo g-olive g-rust`
- **card-footer(좋아요·공유)는 template 예시 카드의 것을 그대로 복사**(직접 작성 금지).
- 첫 카드 `class="card featured"` 허용. ※ 실제 운영은 AI·Design 각 첫 카드 1장씩(총 2장)이다. **정책 미확정 — 확정 시 이 줄을 갱신할 것.**

### 한국어 기사 카드
```html
<a class="card" href="[URL]" target="_blank"
   data-category="[한국어 canonical · 예: AI · 정책 · 전략 / 디자인 · 브랜딩 · 아이덴티티]"
   data-position="[직무 ID 최대 2개, | 로 구분]"
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
   data-category="[한국어 canonical · 예: 디자인 · 브랜딩 · 타이포그래피]" data-category-en="[영문 · 예: Design · Branding · Typography]"
   data-position="[직무 ID 최대 2개, | 로 구분]"
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
0번에서 불러온 index.json 배열 맨 앞에 브리핑 날짜 `YYYYMMDD` 추가(중복이면 생략) → `/home/user/index.json` 저장.

> **주의:** 루틴은 `published_urls.json`을 **읽기만** 한다(§0·§5). 대장 파일 자체는 **갱신하지 않는다** — 배포 시 사람이 브리핑 파일에서 재생성한다(§10).

## 9. 완료 알림
PushNotification: `디자인놀이터 브리핑 초안 생성 — AI [N] / Design [N] / [브리핑 날짜, YYYY-MM-DD]. 대장 대조: 후보 N · 중복 제외 M · 최종 8(전부 신규). 6필드 검증: 8/8 통과. 검색 스니펫 기반 초안이니 세션에서 검수 후 배포하세요.`

## 9-1. 파일 제시 (필수)
파일 저장 후, 생성한 두 파일을 사용자가 바로 받을 수 있도록 제시한다:
- Dinol_news_YYYYMMDD.html (다운로드 링크, **YYYYMMDD = 브리핑 날짜**)
- index.json (다운로드 링크)

그리고 아래를 함께 출력한다:
- **대장 대조 결과 한 줄**: 「대장 대조: 후보 N · 중복 제외 M · 최종 8(전부 신규)」 (§5-0 필수)
- "AI N / Design N, 게재일·사실관계 검수 후 news/2026/MM/ 에 배포하세요" 안내

## 10. 검수·배포 (사람)

### 10-0. 브랜치 — 먼저 확인
**브리핑 확인·발행은 `main` 브랜치에서만 한다.** `astro` 브랜치는 카드 구조가 `article.card + a.card-link` 로 리팩터돼 있어(커밋 `0ed94e3`), 구 구조로 생성된 브리핑을 astro 에서 열면 `assets/dinol.js` 가 링크를 못 찾아 **8장 전부 「⚠ 링크 없음」 배지 + 「중복 링크 1건」 배너**가 뜬다. 파일 결함이 아니라 환경 오탐이다.

```
git status -sb        # 브랜치 확인
git checkout main     # astro 면 전환 (수정 파일이 있으면 git stash 먼저)
```

### 10-1. 사전 검증 (필수 게이트)
파일을 `news/2026/MM/` 에 넣은 뒤, 레포 루트에서:
```
python scripts/validate.py news/2026/MM/Dinol_news_YYYYMMDD.html
```
→ **ERROR 0건이어야 발행한다.** WARN 은 사유를 §9-1 에 남기고 진행 가능.
validate.py 는 HTML 원문을 직접 읽으므로 브라우저 캐시·에셋 버전의 영향을 받지 않는다. **브라우저 화면보다 이 결과가 먼저다.**

### 10-2. 화면 확인
```
python -m http.server 8000
```
→ `http://localhost:8000/news/2026/MM/Dinol_news_YYYYMMDD.html`
- `file://` 로 열지 않는다. `dinol-firebase.js` 가 ESM 모듈이라 CORS 로 차단되어 좋아요·디놀 톡톡이 뜨지 않는다.
- 확인할 것: 「⚠ 링크 없음」 배지 없음 · 하단 빨간 배너 없음 · 콘솔에 `✅ 콘텐츠 검토 통과` · 디놀 톡톡 글 목록 표시

### 10-3. 대장 재생성 → 배포
```
python scripts/build_published_urls.py
```
→ "중복 등장 URL 없음" 확인 후 `git add … → commit → push`(또는 `./deploy.ps1 "메시지"`). 이렇게 하면 오늘 발행한 URL이 대장에 반영되어, 다음 실행의 §5-0 대조가 최신 상태로 작동한다.

> **astro 머지 시 필수 후속 작업:** astro 의 카드 구조(`article.card + a.card-link`)가 main 으로 넘어오면 **§7 카드 패턴을 신 구조로 교체**해야 한다. 교체 전까지 루틴은 구 구조(`a.card`)를 유지한다.
