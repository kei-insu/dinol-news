# detail-page-schema.md — 카드 상세 페이지 스키마

| 최종 갱신 | 최근 변경 |
|---|---|
| 2026-07-25 | 신규 작성. 상세 페이지 전환 1단계 산출물 |

> 카드 팝업(드로어)을 독립 페이지로 전환하기 위한 식별자·URL·데이터 구조 정의.
> 이 문서는 **프레임워크와 무관**하다. 생성기(파이썬 / Astro)가 바뀌어도 이 스키마는 유지한다.

---

## 0. 전환 배경

| 지표 | 현재 | 근거 |
|---|---|---|
| 렌더 화면에 보이는 텍스트 | 10% (898자) | 7/24 브리핑 실측 |
| `data-*` 속성에만 있는 텍스트 | 90% (8,215자) | 동일 |
| 카드당 텍스트 | 평균 1,333자 · 중앙값 1,467자 | 201카드 실측 |

고유 논평이 클릭해야 나오는 구조라, 크롤러와 심사자가 보는 초기 화면에는 기사 제목만 남는다.

---

## 1. contentId

카드의 **영구 식별자**. 좋아요·읽음·공유·향후 댓글이 전부 이 값에 연결된다.

### 형식

```
YYYYMMDD-{섹션}-{3자리 순번}
```

| 예 | 의미 |
|---|---|
| `20260724-ai-003` | 2026-07-24 브리핑 AI 섹션 3번째 카드 |
| `20260724-design-002` | 2026-07-24 브리핑 Design 섹션 2번째 카드 |

### 규칙

| # | 규칙 |
|---|---|
| 1 | 섹션 값은 소문자 `ai` · `design` **만** 허용 |
| 2 | `Design` · `DESIGN` · `des` 등 변형 금지 |
| 3 | 순번은 해당 날짜·섹션 내에서 유일, 3자리 제로패딩 |
| 4 | 최초 생성 시 부여하는 **영구값**. 카드 정렬·대표 카드 변경 시 수정하지 않음 |
| 5 | 삭제된 ID는 **재사용 금지** |
| 6 | 동일 기사를 KR/EN으로 함께 제공해도 **같은 contentId** |
| 7 | 원문 URL·제목이 수정돼도 contentId 유지 |
| 8 | 섹션이 추가되면 이 문서의 허용 목록을 먼저 갱신 |

### 부여 시점

| 대상 | 시점 |
|---|---|
| 신규 카드 | 브리핑 생성 단계에서 자동 부여 |
| 기존 201개 | 상세 페이지 전환 시 일괄 부여 |

### HTML 표기

```html
<a class="card" data-content-id="20260724-ai-003" ...>
```

---

## 2. URL 규칙

### 결정 보류 항목

slug 방식(`/news/deezer-ai-upload-half`)은 가독성이 좋지만, 현재 `dinol-firebase.js` 59행의 좋아요 키가 경로에서 날짜를 추출한다.

```js
const m = location.pathname.match(/Dinol_news_(\d{8})/);
```

→ **URL 확정은 3단계(검증)에서 좋아요 마이그레이션 방침과 함께 결정한다.**

### 후보

| 안 | 형식 | 장점 | 단점 |
|---|---|---|---|
| A | `/news/2026/07/20260724-ai-003.html` | contentId와 1:1, 규칙 단순 | 사람이 읽기 어려움 |
| B | `/news/deezer-ai-upload-half/` | 가독성·SEO 우수 | slug 중복 관리 필요 |
| C | `/news/20260724-ai-003/deezer-ai-upload-half/` | 둘 다 확보 | 경로가 김 |

### 확정 사항 (안과 무관)

| # | 규칙 |
|---|---|
| 1 | 상세 페이지는 **contentId를 페이지 데이터로 보유**한다 (`<body data-content-id="...">`) |
| 2 | URL이 바뀌어도 contentId는 불변 |
| 3 | 각 페이지는 고유 `<title>` · `<meta name="description">` · `<link rel="canonical">` 보유 |
| 4 | 원 브리핑 페이지로 돌아가는 링크 필수 ("이 날짜 브리핑 보기") |
| 5 | 사이트맵에 포함 |
| 6 | 중복 URL 생성 금지 |

---

## 3. 데이터 스키마

카드 1장 = 상세 페이지 1장의 정본 데이터.

```json
{
  "contentId": "20260724-ai-003",
  "date": "2026-07-24",
  "section": "ai",
  "order": 3,

  "source": { "name": "Music Business Worldwide", "publishedAt": "2026-07-21" },
  "url": "https://www.musicbusinessworldwide.com/...",
  "isEn": true,

  "category":   { "kr": "AI · 창작 산업 · 음악", "en": "AI · Creative Industry · Music" },
  "title":      { "kr": "디저 업로드 절반이 AI 음원, 하루 9만 곡 쏟아진다", "en": "..." },
  "summary":    { "kr": "...", "en": "..." },
  "points":     { "kr": ["...", "..."], "en": ["...", "..."] },
  "positions":  ["motion-designer", "video-designer"],
  "designer":   { "kr": "...", "en": "..." },
  "impactScore": 3,
  "recommend":  { "kr": "...", "en": "..." },
  "comment":    { "kr": "...", "en": "..." },

  "thumbLabel": "AI 음원",
  "thumbGradient": "g-navy"
}
```

### 필드 규칙

| 필드 | 필수 | 비고 |
|---|---|---|
| `contentId` | 필수 | §1 형식 |
| `section` | 필수 | `ai` \| `design` |
| `category.kr` | 필수 | 한국어 |
| `category.en` | EN 카드만 | KR 카드는 생략 (EN 토글 미표시) |
| `positions` | 선택 | 내부 ID 배열, 최대 2개 |
| `impactScore` | 필수 | 1~5 정수. Design 섹션은 1 사용 금지 |
| `*.en` | EN 카드만 | KR 카드는 KR값 폴백 |

### 현행 HTML 속성과의 대응

| 스키마 | 현행 `data-*` |
|---|---|
| `contentId` | `data-content-id` (신규) |
| `category.kr` / `.en` | `data-category` / `data-category-en` (신규) |
| `positions` | `data-position` (신규, `\|` 구분) |
| `summary` | `data-summary` / `-kr` |
| `points` | `data-points` / `-kr` (`\|` 구분) |
| `designer` | `data-designer` / `-kr` |
| `impactScore` | `data-impact-score` |
| `recommend` | `data-recommend` / `-kr` |
| `comment` | `data-comment` / `-kr` |

---

## 4. 직무 ID (positions)

내부 ID로 저장하고, 화면 라벨은 `dinol.js`의 `POSITIONS` 맵에서 조회한다.

| ID | 라벨 | 분류 |
|---|---|---|
| `ux-designer` | UX디자이너 | 디지털 제품 |
| `ui-designer` | UI디자이너 | 디지털 제품 |
| `product-designer` | 프로덕트디자이너 | 디지털 제품 |
| `service-designer` | 서비스디자이너 | 디지털 제품 |
| `brand-designer` | 브랜드디자이너 | 브랜드·시각 |
| `bx-designer` | BX디자이너 | 브랜드·시각 |
| `graphic-designer` | 그래픽디자이너 | 브랜드·시각 |
| `editorial-designer` | 편집디자이너 | 브랜드·시각 |
| `motion-designer` | 모션디자이너 | 콘텐츠 |
| `video-designer` | 영상디자이너 | 콘텐츠 |
| `illustrator` | 일러스트레이터 | 콘텐츠 |
| `art-director` | 아트디렉터 | 콘텐츠 |
| `industrial-designer` | 제품디자이너 | 산업·공간 |
| `space-designer` | 공간디자이너 | 산업·공간 |
| `architect` | 건축가 | 산업·공간 |
| `package-designer` | 패키지디자이너 | 산업·공간 |
| `typographer` | 타이포그래퍼 | 전문 영역 |
| `fashion-designer` | 패션디자이너 | 전문 영역 |
| `design-lead` | 디자인리드 | 리더십 |
| `design-manager` | 디자인매니저 | 리더십 |

### 부여 기준

> **Q1 단일 기준** — 해당 직무자가 이 기사에서 얻을 **구체적인 참고점·변화·방법**을 한 문장으로 쓸 수 있는가?
> "관심을 가질 수 있다" 수준은 불통과. 어떤 직무도 특정할 수 없으면 생략한다.

| 항목 | 값 |
|---|---|
| 개수 | 기본 1개, 최대 2개 |
| 자명한 직무 | **표시**(카테고리와 겹쳐도 생략하지 않음) |
| 화면 언어 | 한국어 고정. `positions.en`은 소비처가 생길 때 도입 |
| 미등록 ID | 화면 미노출 + `console.warn` + `validate.py` 오류 |

### 라벨 변경 절차

라벨 표기가 바뀌면 **`POSITIONS` 맵 1줄만** 수정한다. 카드 데이터는 건드리지 않는다.

---

## 5. Firebase 키 정책

### 현행

```js
// dinol-firebase.js 56~63행
function likeKey(url) {
  const m = location.pathname.match(/Dinol_news_(\d{8})/);
  const d = m ? m[1] + "_" : "";
  const u = url.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 280) || "x";
  return d + u;
}
```

| 문제 | 내용 |
|---|---|
| 경로 의존 | URL이 바뀌면 접두어가 사라져 기존 키와 어긋남 |
| 읽음 표시 | `dinol.js` READ_KEY도 같은 정규식 사용 |

### 목표

| 항목 | 목표 |
|---|---|
| 좋아요 키 | `contentId` |
| 읽음 표시 키 | `contentId` |
| 공유 | `contentId` 기반 상세 URL |

### 전환 절차 (3단계에서 확정)

| # | 작업 |
|---|---|
| 1 | 기존 `날짜_URL` 키와 새 `contentId` 매핑표 생성 |
| 2 | 실데이터 규모 확인 (문서 수 · `count` 합계 · 상위 집중도 · `updatedAt` 분포) |
| 3 | 규모에 따라 **이관 또는 초기화** 결정 |
| 4 | 이관 시 일정 기간 구키 fallback 유지 |

### 즉시 적용 (이번 단계)

`likes` 문서에 타임스탬프를 추가한다. 현재 규칙(`count is int && count >= 0`)은 필드 집합을 제한하지 않으므로 **콘솔 재반영 없이 코드만 수정하면 된다.**

```js
await runTransaction(db, async (tx) => {
  const snap = await tx.get(ref);
  const cur  = snap.exists() ? (snap.data().count || 0) : 0;
  const next = Math.max(0, cur + (willLike ? 1 : -1));
  const data = { count: next, url: card.href, updatedAt: serverTimestamp() };
  if (!snap.exists()) data.createdAt = serverTimestamp();
  tx.set(ref, data, { merge: true });
});
```

| 필드 | 의미 |
|---|---|
| `createdAt` | 해당 카드에서 **최초로 좋아요 동작이 발생한** 시점 (문서 생성 시만) |
| `updatedAt` | 마지막으로 좋아요 상태가 변경된 시점 (매번 갱신) |
| `count` | 현재 누적 좋아요 수 |
| `count: 0` | 눌렀다 취소한 이력 존재 = **반응이 있었던 카드** |

`likes.contentId`는 카드에 contentId가 실제 부여된 이후 조건부 저장한다.

```js
if (card.dataset.contentId) data.contentId = card.dataset.contentId;
```

---

## 6. 상세 페이지 정보 위계

7개 필드를 동일 무게로 나열하지 않고 역할별로 묶는다.

| 영역 | 항목 |
|---|---|
| **상단 핵심** | 제목 · 출처·날짜·카테고리 · 관련 직무 · 한 줄 요약 · 실무 영향도 |
| **본문 해설** | 핵심 인사이트 · 디자인 관점 · 큐레이션 노트 |
| **하단 행동** | 활용 추천 · 원문 보기 · 좋아요·공유 · 이 날짜 브리핑 보기 |

| 요소 | 처리 |
|---|---|
| 디놀 톡톡(방명록) | **상세 페이지에 미노출**. 브리핑 페이지에만 유지 |
| 기사별 댓글 | 현재 미도입. 필요 시 `contentId` 기준으로 별도 설계 |

---

## 7. 품질 게이트

**글자 수 기준은 사용하지 않는다.** 구글은 최소 분량을 공표하지 않으며, 판단 기준은 고유성과 독자 가치다.

| 항목 | 통과 조건 |
|---|---|
| 내용 정확성 | 원문과 제목·요약·핵심 사실이 일치 |
| 고유 해석 | 디자인 관점 또는 큐레이션 노트에 자체 판단 존재 |
| 중복 방지 | 요약·인사이트·관점·노트가 같은 말을 반복하지 않음 |
| 독자 가치 | 읽은 뒤 알게 되는 사실이나 판단이 최소 1개 |
| 원문 의존성 | 원문 문장을 단순 축약·번역한 내용만으로 구성되지 않음 |
| 페이지 완결성 | 이 페이지 하나만 봐도 기사 성격과 디놀의 해석을 이해 가능 |

분량은 **재검토 트리거**로만 쓴다.

| 분량 | 처리 |
|---|---|
| 600자 미만 | 자동 재검토 |
| 600~1,000자 | 중복·고유 해석 확인 |
| 1,000자 이상 | 자동 통과하지 않음 |

`noindex`는 품질 보완 수단으로 사용하지 않는다.

---

## 8. 전환 4단계

| 단계 | 작업 | 도구 |
|---|---|---|
| 1 | contentId · URL · 데이터 스키마 · Firebase 키 정책 문서화 | 문서 |
| 2 | 1주치 8개 카드 상세 페이지 시범 생성 | 파이썬 스크립트 |
| 3 | 좋아요·읽음·공유·언어·모바일·SEO 검증 + 좋아요 이관/초기화 확정 | 실측 |
| 4 | 기존 201개 변환 + Astro 도입 여부 확정 | 결정 |

전환 대상은 **★ 등급과 무관하게 201개 전체**다. 일부만 페이지로 열면 같은 목록에서 인터랙션이 갈린다.

---

## 9. 미결 항목

| # | 항목 | 결정 시점 |
|---|---|---|
| 1 | URL 방식 (A/B/C안) | 3단계 |
| 2 | 좋아요 이관 vs 초기화 | 3단계 |
| 3 | Astro 도입 여부 | 4단계 |
| 4 | 기사별 댓글 도입 | 추후 |
| 5 | 상세 페이지에서 필드 라벨의 EN 모드 처리 | 2단계 |
