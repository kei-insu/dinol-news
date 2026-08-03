# claude.md — 디놀 프로젝트 인덱스 & 핸드오프 규칙

| 최종 갱신 | 최근 변경 |
|---|---|
| 2026-08-01 | 3자 검토 프로토콜 + `review-checklist.md` 신설 · main 예외 3종 · 저장 경로 형식 고정 · 5-A-2R/5-B 백로그 등록 |
| 2026-07-31 | 작업 PC kgblu 단독 확정 + 개발(astro)/상용(main) 브랜치 분리 명문화 |
| 2026-07-26 | 명령 작성 전 자체 검토 체크리스트 신설 |

> **이 문서 하나만 세션 시작 시 로드한다.** 나머지는 목차를 보고 그 세션에 필요한 것만 읽는다.
> 원본(단일 진실 원천): `github.com/kei-insu/dinol-news/docs/`
> raw 읽기(개발 문서): `https://raw.githubusercontent.com/kei-insu/dinol-news/astro/docs/<계층>/<파일명>`

---

## ⚑ 세션 시작 프로세스 (Claude가 매번 순서대로)

| 순서 | 할 일 |
|---|---|
| 1 | **오늘 날짜 확인** — 아래 "날짜 확인" 규칙 참조. 문서 스탬프·브리핑에 쓸 오늘 날짜를 먼저 확정 |
| 2 | 이 `claude.md`(인덱스) 읽기 |
| 3 | 목차에서 **오늘 작업에 관련된 문서만** 추가로 읽기(전부 X → 토큰 절약) |
| 4 | 작업 수행 |
| 5 | 코드·구조 변경 시 **관련 문서에 행 추가/갱신 + 오늘 날짜 스탬프** |
| 6 | **작업 일지(Notion) 기록** — 아래 "작업 일지" 규칙 참조. 사용자가 묻기 전에 Claude가 먼저 한다 |

### 날짜 확인 규칙 (중요)
- Claude는 현재 날짜를 스스로 정확히 알기 어려움 → **세션 시작 시 사용자에게 오늘 날짜를 확인**하거나, 사용자가 명시한 날짜를 사용한다.
- 확인된 날짜를 그 세션의 모든 문서 스탬프·브리핑 날짜에 일괄 사용.
- 문서에 날짜를 넣을 때: **확실히 아는 건 해당일**, 불확실은 **오늘 날짜** 또는 `~오늘날짜`(= "이 시점엔 이미 존재") 표기.
- 사용자 시작 멘트 예시: *"디놀 작업 이어서. 오늘은 2026-07-10. docs/claude.md 읽고 시작해."*

---

## 문서 목차

| 문서 | 언제 읽나 | 내용 | 날짜 열 |
|---|---|---|---|
| `rules/policy.md` | 정책·규칙·컨벤션 | 확정 정책(파일명·문서화·언어·톡톡·발행·확장) | 확정일 |
| `dev-history.md` | 기존 기능 이해·확장 | 개발한 것(기능/파일/내용/상태) | 완료일 |
| `issues.md` | 버그·장애 대응 | 크리티컬 이슈·해결·재발방지 | 발생일 |
| `reference/design-guide.md` | UI·스타일 | 컬러·폰트·컴포넌트·톡톡 UI 규칙 | — |
| `rules/guardrails.md` | 배포·보안·위험 작업 전 | 하면 안 되는 것 + 배포 절차(순서 고정)·충돌 마커 금지 | 07-13 |
| `howto/testing.md` | 배포 전 검증 | 검증 절차·체크리스트 | — |
| `reference/news_sources.md` | 브리핑 소스 선정 | 크롤링/큐레이션 소스 목록(12분류·RSS) | 07-06 |
| `howto/routine_instruction.md` | 루틴 이해·수정 | 브리핑 자동생성 절차(⚠️일부 구버전, 라이브는 WebSearch 전용). 발행 중복 대조 필수 관문화 | 07-12 |
| `reference/detail-page-schema.md` | 상세 페이지·Astro 전환 | contentId·URL 규칙·데이터 스키마·Firebase 키 정책·품질 게이트 | 07-25 |
| `reference/fortune-schema.md` | 운세 코너 | `fortune.json` 스키마(별자리 12·확률 6·궁합 6·폰트 10) | 07-13 |
| `howto/review-checklist.md` | **복잡한 코드 작업 전·후** | 실제 사고 10건 기반 선택형 검토 기준(65항목). ⛔기계적 전수 적용 금지 | 08-01 |

---

## 프로젝트 한눈에

| 항목 | 값 |
|---|---|
| 서비스 | 디자인 놀이터(디놀) — AI·디자인 뉴스 큐레이션 + 커뮤니티(톡톡) |
| 레포 | `github.com/kei-insu/dinol-news` (main) |
| URL | `https://kei-insu.github.io/dinol-news/` |
| 호스팅 | GitHub Pages |
| 백엔드 | Firebase Firestore(asia-northeast3, Spark) |
| 로컬 | Windows PowerShell · **kgblu 단독**(`C:\Users\kgblu\OneDrive\바탕 화면\dinol-news\dinol-news`) |
| 배포 | 사용자 로컬 수동(git). Claude 컨테이너는 push 불가 |
| 브랜치 | **개발 = `astro` / 상용 = `main`.** GitHub Pages는 `main`만 빌드. **main 허용은 아래 3종뿐**이고, 그 외 코드·정본 JSON·문서는 `astro`에 쌓는다<br>① 일간 브리핑 발행<br>② **발행본 결함 수정** — 누락 속성·잘못된 링크 등 이미 나간 콘텐츠 교정 (7/29 `4074d82`, 8/1 `8b227e1`)<br>③ **main에서 실행하는 도구** — `deploy.ps1`. astro에 두면 병합 전까지 main에 구버전이 남아 가드가 무용지물 (8/1 `96cba39`) |

### 파일 구조
```
레포/
├─ index.html / archive.html / privacy.html
├─ template.html          브리핑 기준 템플릿
├─ index.json             브리핑 날짜 배열(최신 맨앞)
├─ firestore.rules        보안 규칙 — 배포 경로는 핵심 원칙 3 참조
├─ assets/ dinol.css · dinol.js · dinol-firebase.js · ai-design-news.png
├─ news/2026/MM/Dinol_news_YYYYMMDD.html
├─ content/news/{contentId}.json   카드 데이터 정본(Astro 전환 후 원본)
├─ scripts/ build_briefing.py · build_published_urls.py · validate.py 외
├─ handoff/ HANDOFF_v3.0.md · fortune-handoff.md
└─ docs/                  ← 이 문서들
   ├─ claude.md · dev-history.md · issues.md
   ├─ rules/      policy.md · guardrails.md
   ├─ reference/  design-guide.md · detail-page-schema.md · news_sources.md · fortune-schema.md
   └─ howto/      routine_instruction.md · review-checklist.md · testing.md
```

> **Astro 전환 진행 중**(`astro` 브랜치). GitHub Pages는 `main`만 배포하므로
> `astro` 브랜치 작업은 라이브에 영향이 없다. 상세는 `detail-page-schema.md`.

### 배포 (매일 브리핑)
- 브리핑 파일을 `news/YYYY/MM/`에 넣은 뒤, 터미널에서 **`./deploy.ps1`** 한 줄이면 끝(pull→add→commit→push 자동, 커밋 메시지에 오늘 날짜).
- 메시지 지정: `./deploy.ps1 "add: 7/11 브리핑"`. 스크립트는 레포 루트 `deploy.ps1`.
- `firestore.rules`는 별도. 핵심 원칙 3 참조.

### 핵심 원칙
| # | 원칙 |
|---|---|
| 1 | 상단 방명록 폼은 template + 모든 브리핑에 복제 → 변경 시 전체 파일 수정 |
| 2 | 배포 시 `git status`로 스테이징 확인 필수 |
| 3 | `firestore.rules` 변경 시 **배포 경로를 확인**한다. `firebase.json`·`.firebaserc`가 커밋되기 전까지는 콘솔 수동 반영, 이후는 `npm run deploy:rules`(⛔사용자 승인 후) |
| 4 | 작업 후 관련 문서 갱신 + 날짜 스탬프 |
| 5 | 작업 후 **Notion 작업 일지 기록** (위 "작업 일지" 규칙) |
| 6 | `main`에 변경이 생기면 `astro` 브랜치에서 `git merge main` — 매일 브리핑 발행 시 특히 |

**발행본 결함 수정 순서 (②)** — 이 순서를 지켜야 한다.
```
main 수정·배포 → git checkout astro → git merge main → daily_import.py {ymd} --redo
```
astro에서 먼저 고치면 `daily_import.py` 게이트 `[0]`의 **main blob 대조에 막힌다.**

**커밋 전제조건** — `daily_import.py`는 `[PASS] 전체 통과`가 떠야 커밋 대상이다.
중단되면 원인부터 해결한다.


---

## 명령 작성 전 자체 검토 (2026-07-26)

Claude Code 명령을 발송하기 전 아래 7가지를 확인한다.
GPT 리뷰에서 반복 지적된 유형을 1차에서 거르기 위함이다.

| # | 항목 | 확인 내용 |
|---|---|---|
| 1 | 모순 | 같은 대상에 상반된 지시가 있나 (예: `git merge`는 커밋을 만드는데 "커밋하지 마") |
| 2 | 수치 | 모든 숫자를 이번 데이터로 재계산했나 ★앞 답변 복사 금지. bash로 계산★ |
| 3 | 방어 | null · 빈값 · 타입오류 · 예외 경로를 다뤘나 |
| 4 | 환경 | PowerShell·Python 특수성 (`ls` 와일드카드, `curl` 별칭, `bool`은 `int`) |
| 5 | 정리 | 임시 파일이 남거나 커밋되나 |
| 6 | 범위 | 일회성 로직이 영구 운영 코드에 들어가나 |
| 7 | 파급 | 이 변경이 다른 스크립트·문서를 깨나 |

**2번과 7번이 실제 사고로 이어진 적이 있다.**
2번: 링크 검사 238 → 실제 247, V37 71 → 실제 73 등 앞 답변 수치를 그대로 복사.
7번: 카드 `href` 변경이 `build_published_urls.py`를 깨뜨린 것을 뒤늦게 발견.

---

## 3자 검토 프로토콜 (2026-08-01)

Claude가 명령을 쓰고 GPT가 검토하는 구조는 유효하다.
다만 **검토가 결함 찾기에만 쏠리면 명세가 계속 비대해진다.** 근거·사례는 `review-checklist.md`.

### 1. GPT에게 과잉 여부도 함께 묻는다

```
[기존] "검토해. 빠진 것 지적해"
[변경] "검토해. 빠진 것과 과잉인 것을 둘 다 지적해"
```

AI 코드 리뷰어의 목적은 결함 발견만이 아니라 **과잉 엔지니어링 방지**다.
지금 반드시 필요한 것과 나중에 해도 되는 것을 구분하도록 요청한다.

### 2. 왕복 3회를 넘으면 접근을 바꾼다

⛔ 같은 방식으로 항목을 더 추가하지 않는다.

전환 방향: **다른 설계로 갈아탄다 · 범위를 쪼갠다 · 직접 코드를 쓴다**

**3회는 "명세가 부족하다"가 아니라 "접근이 잘못됐다"는 신호다.**

### 3. 상세 기준은 `review-checklist.md` 에

상시 지침에 모든 사례를 넣지 않는다. 복잡한 코드 작업에서는
`docs/howto/review-checklist.md` 에서 ★현재 작업과 관련된 항목만★ 골라 쓴다.
⛔ 전수 적용하거나 무관한 검증을 추가하지 않는다.
구체적인 파일·명령어·수치는 각 작업 프롬프트에 쓴다.

### 4. 한 명세는 파일 2개 이내

한 프롬프트에 여러 목적을 묶으면 검토할 때마다 새 의존성이 생긴다.
**초과하면 쪼갠다.** 검증 통과 시점을 중간에 두는 편이 낫다.

### 5. 구현이 끝난 뒤에는 감사로 전환

⛔ 이미 작성된 코드에 구현 전 지시를 반복하지 않는다.

```
구현 전 : 명세 보완
구현 후 : 실제 diff 감사 — 코드를 인용해 명세대로인지 확인
```

불일치를 발견하면 **자동 수정하지 말고 파일·행번호·위반 내용을 보고 후 중단**한다.
감사 결과와 테스트 기준점이 섞이면 안 된다.

---


## 작업 일지 (Notion) — 2026-07-25

**Claude가 사용자에게 묻기 전에 먼저 기록한다.**

| 항목 | 값 |
|---|---|
| DB | `dinol-news 작업 일지` |
| DB ID | `33a617d6-8ebc-4ee8-816a-d4323dff0311` |
| 속성 | 작업명 · 구분 · 날짜 · 진행도 · 내용 |
| 구분 | 기획 · IA · 사이트맵 · 와이어프레임 · 디자인 · 개발 · 문서 · 기타 |

> ※ 별자리 카드(zodiac) 작업은 기존 `별자리 카드 작업 일지` DB를 계속 쓴다.

### 기록 시점

| 시점 | 진행도 |
|---|---|
| 작업 착수 | `진행중` |
| 파일 전달 완료 | `완료` |
| 결정만 하고 미착수 | `대기` |
| 논의 후 보류 | `보류` |

### 작성 원칙
- **무엇을 왜 했는지**를 남긴다. 파일명 나열이 아니라 판단 근거와 수치를 적는다.
- 발견한 결함·수치(예: "EN 카드 8장 결함", "전수 검증 209장 0건")를 함께 적는다.
- 세션 종료 전 미기록 항목이 없는지 확인한다.

---

## 핸드오프 — 파일 전달 시 저장 경로 표기 (2026-07-25)

업데이트한 파일을 사용자에게 전달(다운로드)할 때는, **다운로드 링크 위에 레포 저장 경로를 함께 표기**한다.

**표기 형식 — 아래를 그대로 쓴다 (2026-08-01 고정)**

```
### 📁 저장 경로 — dinol-news > <폴더> 폴더
```

- **반드시 헤딩(`###`)으로 쓴다.** 굵은 글씨 한 줄은 앞 블록(표·문단)에 붙어 렌더링에서 삼켜진다.
- 헤딩 앞뒤로 **빈 줄을 둔다.**
- 이 헤딩은 **다운로드 카드 바로 직전**에 놓는다. 사이에 다른 문장을 끼우지 않는다.
- 파일이 여러 개이고 경로가 다르면 **경로별로 나눠 전달**한다.

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

---

## 수정 예정 백로그

세션 시작 시 확인. 처리하면 행 삭제하고 `dev-history.md`/해당 문서에 반영.

| 등록일 | 항목 | 비고 |
|---|---|---|
| 2026-08-01 | **5-A-2R 작업 트리 대기** | `firestore.rules`·`package.json`·`.firebaserc`·`firebase.json`·`scripts/rules.test.mjs` **미커밋 상태**. **JDK 21 이상** 설치 후 규칙 11건(`npm run emulators:rules`) 실행 → 커밋. ⛔배포는 5-B 마이그레이션 완료 후 프런트와 **함께** |
| 2026-08-01 | 5-B 좋아요 마이그레이션 | 214건(count 387) legacy → contentId. 이관 제외 7건은 legacy 문서로 보존. Admin SDK 배치·dry-run·실행 직전 신규 문서 0건 재확인 |
| 2026-07-25 | `guardrails.md`·`issues.md` 7/19 결정 반영 | Auth 롤백을 원칙 변경이 아닌 **승인된 예외**로 기록. `481516`은 배지용이 아니라 전체 수정·삭제 마스터 키 |
| 2026-07-25 | 마스터 비밀번호 값 교체 검토 | `config/site` 공개 읽기 + 6자리 숫자 → 복원 가능. App Check로 차단 안 됨. 현행 유지 결정, 위험 인지 상태 |
| 2026-07-25 | `handoff/` 폴더 정리 | `HANDOFF_v3.0.md`가 7/19 철회된 Auth 지시를 담고 있어 다음 세션을 오도할 수 있음. 살릴 내용은 각 문서로 이관 후 폴더 삭제 |
| 2026-07-25 | OG 이미지 규격 | `ai-design-news.png` 1200×395. 권장 1200×630 미달로 SNS에서 잘릴 수 있음 |
| 2026-07-25 | EN 카드 언어 슬롯 정책 승격 | `validate.py`·`validate_json.py`의 `EN_LANGUAGE_POLICY_FROM`이 `None`. HTML 원본을 안 고치므로 Astro 전환 완료 후 날짜 기입 |
| 2026-07-25 | 필드 라벨 EN 모드 처리 | 드로어 필드 라벨이 EN 모드에서도 한국어. 상세 페이지 전환 후 재검토 |

_git 이력이 상세 버전 관리를 대신함._
