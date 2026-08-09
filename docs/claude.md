# claude.md — 디놀 프로젝트 인덱스 & 핸드오프 규칙

| 최종 갱신 | 최근 변경 |
|---|---|
| 2026-08-10 | main→astro 병합. `claude.md` 충돌 해소 — 「커밋 후 점검」은 본문 유지, 「3자 검토 프로토콜」은 `rules/command-review.md §2` 로 병합 |
| 2026-08-09 | `docs/` 5계층 분리(rules·reference·howto·history·adr) · `claude.md` 슬림화(16.4KB → 7KB) · 백로그 노션 이관 |
| 2026-08-08 | 루틴 UI 경계 마커 도입(실행 프롬프트 분리) · 제외 매체 판정 규칙 신설 · 작업 일지 스키마 정정 · deploy.ps1 validate 게이트 |
| 2026-08-07 | 루틴 브리핑 날짜 기준 변경(실행일 → 실행일+1) · 문서 스탬프와 분리 |
| 2026-08-06 | 소스 목록 3사본 동기화 규칙 신설(news_sources · routine_instruction §3 · 루틴 UI) |
| 2026-07-26 | 명령 작성 전 자체 검토 체크리스트 신설 |
| 2026-07-25 | 작업 일지(Notion) 기록 규칙 명문화 + 문서 목차 2건 추가 + 백로그 갱신 |
| 2026-07-13 | 배포 절차 순서 고정 + deploy.ps1 하드닝(guardrails·issues 반영) |
| 2026-07-12 | 루틴 발행 중복 대조 필수 관문화(routine_instruction·issues 반영) |
| 2026-07-10 | 날짜 확인 프로세스 유지, 갱신정보 상단 이동 |

> **이 문서 하나만 세션 시작 시 로드한다.** 나머지는 목차를 보고 그 세션에 필요한 것만 읽는다.
> 원본(단일 진실 원천): `github.com/kei-insu/dinol-news/docs/`
> raw 읽기: `https://raw.githubusercontent.com/kei-insu/dinol-news/main/docs/<파일명>`

---

## 문서 목차

| 문서 | 언제 읽나 | 내용 | 날짜 열 |
|---|---|---|---|
| `docs/rules/policy.md` | 정책·규칙·컨벤션 | 확정 정책(파일명·문서화·언어·톡톡·발행·확장) | 확정일 |
| `docs/history/dev-history.md` | 기존 기능 이해·확장 | 개발한 것(기능/파일/내용/상태) | 완료일 |
| `docs/history/issues.md` | 버그·장애 대응 | 크리티컬 이슈·해결·재발방지 | 발생일 |
| `docs/reference/design-guide.md` | UI·스타일 | 컬러·폰트·컴포넌트·톡톡 UI 규칙 | — |
| `docs/rules/guardrails.md` | 배포·보안·위험 작업 전 | 하면 안 되는 것 + 배포 절차(순서 고정)·충돌 마커 금지 | 07-13 |
| `docs/howto/testing.md` | 배포 전 검증 | 검증 절차·체크리스트 | — |
| `docs/reference/news_sources.md` | 브리핑 소스 선정 | 크롤링/큐레이션 소스 목록(14분류·RSS). **소스 단일 출처.** 유럽(EU)·중국(CN) 섹션 + 제외 매체 | 08-08 |
| `docs/howto/routine_instruction.md` | 루틴 이해·수정 | 브리핑 자동생성 절차(WebSearch 전용). **§1 브리핑 날짜(실행일+1)** · 발행 중복 대조 관문 · 카드 스키마 · 별점 루브릭 · §3 확장 소스 목록 · §10 발행 게이트 | 08-08 |
| `docs/reference/detail-page-schema.md` | 상세 페이지·Astro 전환 | contentId·URL 규칙·데이터 스키마·Firebase 키 정책·품질 게이트 | 07-25 |
| `docs/reference/fortune-schema.md` | 운세 코너 | `fortune.json` 스키마(별자리 12·확률 6·궁합 6·폰트 10) | 07-13 |
| `docs/howto/session-start.md` | 세션 시작 | 세션 시작 프로세스 6단계 + 날짜 확인 규칙 | 08-07 |
| `docs/rules/command-review.md` | 명령 발송 전 · 검토 왕복 시 | §1 자체 검토 8항목(보고 형식 포함) · §2 3자 검토 5원칙 | 08-10 |
| `docs/reference/worklog-schema.md` | 작업 일지 기록 | Notion 작업 일지 DB·구분 판정·기록 시점·필드 규칙 | 08-08 |
| `docs/howto/file-delivery.md` | 파일 전달 시 | 다운로드 링크 위 저장 경로 표기 규칙 | 07-25 |
| `docs/rules/source-sync.md` | 소스 목록 변경 시 | 소스 3사본 동기화·경계 마커·제외 매체 판정 | 08-08 |
| `docs/howto/review-checklist.md` | **복잡한 코드 작업 전·후** | 실제 사고 10건 기반 선택형 검토 기준(65항목). ⛔기계적 전수 적용 금지 | 08-01 |
| `docs/adr/NNNN-*.md` | **지난 결정을 다시 논할 때** | 왜 그 방식을 택했나(배경·결정·근거·검토했으나 버린 안·결과). 1결정 1파일. 템플릿 `adr/0000-template.md` | — |

> **수정 예정 백로그** — 노션 백로그 DB로 이관 완료(2026-08-09, 9건 등록 · 3건 중복 스킵). 신규 과제는 노션이 정본이므로 이 인덱스에는 링크를 두지 않는다.

docs/history/ — 이력 계층. 가이드 §2는 이력 저장소를 Notion DB로 규정하나,
dev-history.md·issues.md는 내용 재구성 없이 옮길 수 없어 git에 둔다(§9 단서 적용).
노션 작업 일지 DB와의 역할 분담은 백로그.

---

## 프로젝트 한눈에

| 항목 | 값 |
|---|---|
| 서비스 | 디자인 놀이터(디놀) — AI·디자인 뉴스 큐레이션 + 커뮤니티(톡톡) |
| 레포 | `github.com/kei-insu/dinol-news` (main) |
| URL | `https://kei-insu.github.io/dinol-news/` |
| 호스팅 | GitHub Pages |
| 백엔드 | Firebase Firestore(asia-northeast3, Spark) |
| 로컬 | Windows PowerShell(경로 PC마다 다름, 현재 OneDrive 폴더) |
| 배포 | 사용자 로컬 수동(git). Claude 컨테이너는 push 불가 |

### 파일 구조
```
레포/
├─ index.html / archive.html / privacy.html
├─ template.html          브리핑 기준 템플릿
├─ index.json             브리핑 날짜 배열(최신 맨앞)
├─ firestore.rules        보안 규칙(콘솔에 수동 반영)
├─ assets/ dinol.css · dinol.js · dinol-firebase.js · ai-design-news.png
├─ news/2026/MM/Dinol_news_YYYYMMDD.html
├─ content/news/{contentId}.json   카드 데이터 정본(Astro 전환 후 원본)
├─ scripts/ build_briefing.py · build_published_urls.py · validate.py 외
├─ handoff/ fortune-handoff.md   ※ 정리 대상(백로그)
├─ HANDOFF.md             세션 재개용 단일 상태 문서
└─ docs/                  ← 이 문서들 (계층: rules · reference · howto · history · adr)
   ├─ claude.md           인덱스(이 파일)
   ├─ rules/     policy.md · guardrails.md · command-review.md · source-sync.md
   ├─ reference/ news_sources.md · design-guide.md · detail-page-schema.md · fortune-schema.md · worklog-schema.md
   ├─ howto/     routine_instruction.md · testing.md · session-start.md · file-delivery.md · review-checklist.md
   ├─ history/   dev-history.md · issues.md
   └─ adr/       0000-template.md
```

> **Astro 전환 진행 중**(`astro` 브랜치). GitHub Pages는 `main`만 배포하므로
> `astro` 브랜치 작업은 라이브에 영향이 없다. 상세는 `detail-page-schema.md`.

### 배포 (매일 브리핑)
- 브리핑 파일을 `news/YYYY/MM/`에 넣은 뒤, 터미널에서 **`./deploy.ps1`** 한 줄이면 끝(fetch→add→충돌검사→**validate**→commit→push, 6단계).
- 메시지 지정: `./deploy.ps1 "add: 7/11 브리핑"`. 스크립트는 레포 루트 `deploy.ps1`.
- 최초 1회만 실행권한: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **`[4/6]` validate 게이트(2026-08-08 추가)** — 스테이징된 `news/**/Dinol_news_*.html` 만 `scripts/validate.py` 로 검사하고, ERROR 가 있으면 **커밋 전에 중단**한다. 브리핑 변경이 없으면 건너뛴다. 우회 스위치는 두지 않았다.
- `firestore.rules`는 별도(콘솔 붙여넣기). 규칙 바꾼 날은 콘솔도 반영.

### 핵심 원칙
| # | 원칙 |
|---|---|
| 1 | 상단 방명록 폼은 template + 모든 브리핑에 복제 → 변경 시 전체 파일 수정 |
| 2 | 배포 시 `git status`로 스테이징 확인 필수 |
| 3 | `firestore.rules` 변경 시 **배포 경로를 확인**한다. `firebase.json`·`.firebaserc`가 커밋되기 전까지는 콘솔 수동 반영, 이후는 `npm run deploy:rules`(⛔사용자 승인 후) |
| 4 | **문서는 변경 발생 시점에 즉시 갱신** + 날짜 스탬프. 코드·UI·동작·구조·운영 방식이 바뀌면 **같은 작업 안에서** 관련 문서를 고친다. "나중에 한 번에"는 누락을 만든다 (2026-08-07) |
| 5 | 작업 후 **Notion 작업 일지 기록** (`reference/worklog-schema.md`). 커밋 시각을 물을 때 **밀린 항목 점검을 함께 출력**한다 — 아래 「커밋 후 점검」 |
| 6 | `main`에 변경이 생기면 `astro` 브랜치에서 `git merge main` — 매일 브리핑 발행 시 특히 |

---

## 커밋 후 점검 (2026-08-08)

노션 `날짜` 용으로 커밋 시각을 물을 때 **같은 블록에서 밀린 항목까지 확인**한다.
핸드오프 갱신·`main`→`astro` 머지·push 는 작업 끝에 붙는 잡일이라 대화가 길어지면 빠진다.
기억에 의존하지 않도록, 반드시 하는 동작(커밋 시각 조회)에 점검을 얹는다.

```powershell
git log -1 --date=iso --format="COMMIT   %h %cd"
"MERGE    main->astro 미반영 " + (git log --oneline astro..main | Measure-Object).Count + "건"
"PUSH     astro " + (git log --oneline origin/astro..astro | Measure-Object).Count + "건 / main " + (git log --oneline origin/main..main | Measure-Object).Count + "건"
"HANDOFF  " + (git log -1 --format="%h %cd" --date=iso astro -- HANDOFF.md)
"LATEST   astro " + (git log -1 --format="%h %cd" --date=iso astro)
"LATEST   main  " + (git log -1 --format="%h %cd" --date=iso main)
"LATEST   5b    " + (git log -1 --format="%h %cd" --date=iso 5b-2-emulator) + "  (원격 없음 = 전부 미push)"
```

| 출력 | 조치 |
|---|---|
| `HANDOFF` 시각 < `LATEST` 시각 | 핸드오프가 뒤처짐 → 갱신 후 커밋 |
| `MERGE` 1건 이상 | `dinol-astro` 에서 `git merge main`. 머지는 그 세션 안에서 끝낸다 |
| `PUSH` 누적 | push 는 기본 절차에서 제외. ①raw URL 읽기 필요 ②장기 백업 때만 판단 |

⛔ **커밋이 없는 작업(판단·분석·조사)에서는 이게 안 돈다.** 그때는 사용자가 `dinol-status`
스킬(Claude 설정 > Features 등록)로 부른다. 같은 조회를 온디맨드로 실행한다.

**발행본 결함 수정 순서** — 이 순서를 지켜야 한다.
```
main 수정·배포 → git checkout astro → git merge main → daily_import.py {ymd} --redo
```
astro에서 먼저 고치면 `daily_import.py` 게이트 `[0]`의 **main blob 대조에 막힌다.**

**커밋 전제조건** — `daily_import.py`는 `[PASS] 전체 통과`가 떠야 커밋 대상이다.
중단되면 원인부터 해결한다.
