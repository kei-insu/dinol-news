# 5-A 구현 명세 — 좋아요·공유 contentId 재도입

작성일 2026-08-02 · 대상 브랜치 `astro` · 확정 상태: **인수님 확인 대기**

## 이 문서의 범위

프런트엔드 코드와 보안 규칙 구현까지. **마이그레이션(5-B)은 포함하지 않는다.**
5-A 검증이 끝나기 전에 5-B로 넘어가지 않는다.

## 확정된 정책 (2026-08-02)

| # | 항목 | 결정 |
|---|---|---|
| 1 | 전환 정책 | **A — 즉시 차단.** legacy 키 쓰기를 허용하지 않는다 |
| 2 | localStorage 승계 | **(c)** — A 184건 런타임 계산 + D1-E 30건 예외 매핑 (gzip 1,045 B) |
| 3 | Firebase CLI | `firebase.json`·`.firebaserc` 추가. firestore 전용 |

---

## 1. 데이터 계약 — 가장 중요

### 문제

현재 구조가 페이지마다 다르다.

| 페이지 | contentId | 원문 URL |
|---|---|---|
| 브리핑 카드 | `data-content-id` 있음 | **없음** |
| 상세 페이지 | **없음** (경로·canonical·JSON-LD에만) | `.detail-cta` href · JSON-LD citation |

공통 모듈이 `location.pathname`·`.detail-cta`·JSON-LD·`card.href`를 각각 추론하면
**다시 페이지별 분기가 생긴다.** 무접두어 사고의 원인이 정확히 이것이었다.

### 계약

**Astro 컴포넌트가 값을 명시적으로 전달하고, JS는 전달값만 사용한다.**

좋아요 컨테이너가 아래 3종을 제공한다.

```html
<div class="like-box"
     data-content-id="20260710-design-003"
     data-source-url="https://www.yankodesign.com/2026/07/08/..."
     data-share-url="https://kei-insu.github.io/dinol-news/news/2026/07/20260710-design-003.html">
  <button class="act-like" ...>...</button>
  <span class="act-count">0</span>
  <button class="act-share" ...>...</button>
</div>
```

| 속성 | 용도 |
|---|---|
| `data-content-id` | **Firestore 문서 ID** |
| `data-source-url` | **`likes.url` 필드에 기록** — 원문 기사 URL |
| `data-share-url` | **공유에 사용** — 자사 상세 canonical |

- 카드와 상세가 **같은 컨테이너 구조**를 쓴다.
- 셋 중 하나라도 없으면 그 컨테이너는 **초기화를 건너뛴다**(오류 없이).
- JS는 이 셋 외에 어떤 값도 추론하지 않는다.

---

## 2. 공통 모듈 분리

### 현재 걸림돌

- `initLikes()`가 `a.card` 목록을 전제한다 (상세엔 `a.card`가 없다)
- 드로어 전역 변수(`currentCard`·`dLike`·`dCount`)와 얽혀 있다
- 상태 키가 `card.href`다

### 분리

```
공유 (카드·상세 공통)
  · 문서 ID 생성 = contentId 그대로
  · 읽기 (getDoc)
  · 토글 (runTransaction + set merge)
  · 중복 방지 (localStorage)
  · 승계 로직

개별
  · DOM 바인딩 (컨테이너를 찾아 연결)
  · 렌더 위치
```

**핵심 변경**

| 항목 | 현재 | 변경 |
|---|---|---|
| 진입점 | `document.querySelectorAll("a.card")` | `document.querySelectorAll(".like-box")` |
| 문서 ID | `likeKey(card.href)` | `box.dataset.contentId` |
| 상태 키 | `state[card.href]` | `state[contentId]` |
| 드로어 연동 | `currentCard` 전역 | **제거** (드로어는 4-2에서 폐기됨) |

`likeKey()` 함수는 **승계 계산 전용**으로만 남긴다. 새 문서 ID 생성에는 쓰지 않는다.

---

## 3. Firestore 쓰기

기존 방식을 유지한다. `increment()`로 바꾸지 않는다.

```js
await runTransaction(db, async (tx) => {
  const snap = await tx.get(ref);
  const cur  = snap.exists() ? (snap.data().count || 0) : 0;
  const next = Math.max(0, cur + (willLike ? 1 : -1));

  if (snap.exists()) {
    tx.update(ref, { count: next });          // url 을 다시 쓰지 않는다
  } else {
    tx.set(ref, { count: next, url: sourceUrl });  // 최초 생성 시에만 url
  }
});
```

**변경점**

| 항목 | 현재 | 변경 |
|---|---|---|
| `url` 기록 | 매 클릭마다 `set(merge)` | **최초 생성 시에만** |
| update | `set(..., {merge:true})` | `update({count})` — 필드 제한 |

강화 규칙이 update를 `count`만 허용하므로 `url`을 함께 보내면 차단된다.

---

## 4. localStorage 승계

### 동작

```
신규 키(dinol_liked_{contentId})가 없고
legacy 키가 "1" 이면:
  1. 신규 키를 "1" 로 저장
  2. UI 를 이미 좋아요 상태로 표시
  3. 기존 legacy 키는 유지 (삭제하지 않는다 — 롤백 시 상태를 잃는다)
```

**승계는 Firestore count를 변경하지 않는다. 로컬 상태 이전일 뿐이다.**

### legacy 키 계산

A 184건은 런타임에 계산한다. Node.js 검산에서 **184/184 일치**했다.

```js
function legacyKeyOf(contentId, sourceUrl) {
  const date = contentId.slice(0, 8);
  const slug = sourceUrl.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 280) || "x";
  return date + "_" + slug;
}
```

D1-E 30건은 계산으로 안 나온다(무접두어). **예외 매핑 파일**을 쓴다.

```
src/data/legacy-like-map.json   ← contentId → legacyKey 30건 (gzip 1,045 B)
```

조회 순서

```
1. 신규 키가 있으면 → 승계 불필요
2. 예외 매핑에 있으면 → 그 키로 조회
3. 없으면 → legacyKeyOf() 로 계산해 조회
4. 둘 다 "1" 이 아니면 → 승계 없음
```

### 제거

승계 코드는 한시적이다. 나중에 예외 파일과 승계 함수를 지우면 된다.
**제거 시점은 5-A 범위 밖.**

---

## 5. 공유

```
공유 URL = data-share-url (자사 상세 canonical)
```

- 카드·상세 모두 동일하다.
- `navigator.share` 폴백 클립보드는 현재 방식을 유지한다.

---

## 6. 보안 규칙 강화

### 초안 (Emulator 검증 필요)

```javascript
match /likes/{id} {
  allow read: if true;

  allow create: if request.resource.data.keys().hasOnly(['count','url'])
                && request.resource.data.count is int
                && request.resource.data.count == 1
                && request.resource.data.url is string
                && request.resource.data.url.size() > 0
                && request.resource.data.url.size() <= 500
                && id.matches('^[0-9]{8}-(ai|design)-[0-9]{3}$');

  allow update: if request.resource.data.diff(resource.data)
                     .affectedKeys().hasOnly(['count'])
                && resource.data.count is int
                && request.resource.data.count is int
                && request.resource.data.count >= 0
                && math.abs(request.resource.data.count - resource.data.count) == 1
                && id.matches('^[0-9]{8}-(ai|design)-[0-9]{3}$');
}
```

**설계 의도**

| 조건 | 막는 것 |
|---|---|
| `keys().hasOnly(['count','url'])` | create 시 임의 필드 추가 |
| `affectedKeys().hasOnly(['count'])` | update 시 `url` 변조 |
| `math.abs(...) == 1` | 한 요청의 큰 값 점프·다단계 변경 |
| `id.matches(...)` (create·update **양쪽**) | legacy 문서 쓰기 · 임의 ID 생성 |
| `resource.data.count is int` | 비정상 기존 문서 기준 계산 |

**한계 — 명시**

`±1` 제한은 한 요청의 점프를 막을 뿐이다.
**반복 `+1` 요청, 다중 기기·브라우저 조작은 막지 못한다.**
익명 구조에서 서버 측 사용자 식별 없이 완전한 중복 방지는 어렵다. 설계 한계로 남긴다.

### 전환 정책 A의 영향

새 규칙 배포 후 **캐시된 구 JS의 legacy 키 쓰기는 실패한다.**

- 신규 페이지 요청의 구 JS 체류: 최대 약 10분 (`max-age=600`)
- **이미 열려 있는 탭은 새로고침 전까지 구 JS를 계속 사용한다**

실패 시 안내

```
좋아요 기능이 업데이트되었습니다.
페이지를 새로고침한 뒤 다시 시도해 주세요.
```

---

## 7. Firebase CLI 구성

```json
// firebase.json
{ "firestore": { "rules": "firestore.rules" } }
```

```json
// .firebaserc
{ "projects": { "default": "dinol-news" } }
```

**오배포 방어 — 복수 장치**

```
1. .firebaserc 에 default = dinol-news 고정
2. 배포 명령에 --project dinol-news 명시
3. 배포 직전 firebase use 또는 projects:list 로 대상 확인
4. 사용자 확인 전 실제 deploy 금지
```

Hosting은 불필요하다. GitHub Pages를 그대로 쓴다.
firebase CLI가 미설치이므로 설치가 선행된다. **버전 고정 여부는 별도 결정.**

---

## 8. 검증 계획

### Emulator (규칙)

| # | 케이스 | 기대 |
|---|---|---|
| 1 | 신규 contentId create (count 1, url 있음) | 허용 |
| 2 | 신규 contentId update (±1) | 허용 |
| 3 | count 점프 (>1 변화) | 차단 |
| 4 | update 시 url 동봉 | 차단 |
| 5 | 임의 필드 추가 | 차단 |
| 6 | 날짜 접두어 legacy create/update | 차단 |
| 7 | 무접두어 legacy create/update | 차단 |
| 8 | delete | 차단 |
| 9 | `matches()` 경계값 (8자리 미만·4자리 순번) | 차단 |
| 10 | `resource.data.count` 비정상일 때 update | 차단 |

### 브라우저 (프런트)

| # | 케이스 | 기대 |
|---|---|---|
| 1 | 카드에서 좋아요 → 상세로 이동 | **같은 상태** |
| 2 | 상세에서 좋아요 → 카드로 복귀 | **같은 상태** |
| 3 | 공유 URL | 상세 canonical |
| 4 | legacy 키가 "1" 인 카드 첫 방문 | **하트 채워짐** (승계) |
| 5 | 승계 후 Firestore count | **변화 없음** |
| 6 | 컨테이너 속성 누락 시 | 오류 없이 건너뜀 |
| 7 | 데이터 계약 3종이 카드·상세 모두 있는지 | 빌드 산출물 확인 |

---

## 9. 작업 순서

```
1. 데이터 계약 — Card.astro · DetailPage.astro 컨테이너
2. 공통 모듈 분리 — likes.js (가칭)
3. localStorage 승계 + 예외 매핑 파일
4. 공유 URL 전환
5. firestore.rules 강화
6. firebase.json · .firebaserc
7. Emulator 검증
8. 빌드 후 브라우저 검증
9. 사용자 확인 → 중단
```

**5-B(마이그레이션)는 이 검증이 끝난 뒤 별도 명세로 진행한다.**

---

## 10. 이번 범위에서 제외

| 항목 | 이유 |
|---|---|
| 마이그레이션 실행 | 5-B |
| 이관 제외 7건 처리 | legacy 문서로 보존. 별도 판단 |
| 승계 코드 제거 시점 | 전환 안정화 후 |
| 상세 페이지 배포 | 7단계 |
