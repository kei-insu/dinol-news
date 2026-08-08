# HANDOFF — dinol-news

> 갱신: 2026-08-08 / 세션 4

## [작업 규칙] — 이 문서를 읽은 세션이 즉시 적용 (5개 고정, 증설 금지)

1. §3 폐기한 접근에 있는 방향은 다시 제안하지 않는다.
2. §2 확정 사항을 변경해야 한다고 판단되면 임의로 바꾸지 말고
   먼저 사용자에게 확인받는다.
3. 이 문서의 전문을 되뱉지 않는다. 필요한 항목만 참조한다.
4. 핸드오프는 **변경이 생기면 그 시점에 갱신한다** — 커밋·worktree·백로그·확정 사항이
   바뀌면 즉시 반영한다. 세션 마감은 먼저 권하지 않는다.
5. 이 문서와 실제 코드/산출물이 어긋나면 즉시 사용자에게 알린다.

---

## 1. 현재 단계

세션 4는 5-B-2 를 진행하지 않았다. **일일 브리핑 운영과 그 주변 자동화**에 집중했고,
8/7·8/8 두 회차를 발행한 뒤 발행 절차의 구멍 세 곳을 막았다.

① 루틴이 **실행 당일** 을 브리핑 날짜로 잡아 `index.json` 최신 항목과 충돌하던 문제를
`routine_instruction.md` §1 을 **실행 시점 +1일** 로 바꿔 해소했다(수동 재실행 보정 포함).
② `deploy.ps1` 에 `[4/6] validate` 게이트를 넣어 ERROR 브리핑이 커밋 전에 막히게 했다.
③ 루틴이 §3 소스 목록 밖 매체를 뽑아오는 것을 확인하고 `news_sources.md` 에
**제외 매체** 섹션과 판정 기준 4항목을 신설했다.

`main` 10커밋 · `astro` 4커밋을 만들었고 **둘 다 push 완료**다. `astro` 는 `main` 을 두 번
머지해 미머지 0건이며(`astro..main` 빈 출력), 두 번째 머지에서 `claude.md` 충돌 4건을 해소했다.

5-B-2 는 세션 3 종료 시점 그대로다 — `migrate-likes.mjs` 는 여전히 dry-run 전용이고,
**execute·delta·verify 모드 구현(A-1)이 여전히 1순위**다. 착수 조건은 §4 를 그대로 따르면 된다.

## 2. 확정 사항 — 변경 금지

- 5-B 전환 순서는 C-2 — 5-B-2를 에뮬레이터 실증까지로 축소하고 운영 Firestore 쓰기 0건. 5-A-2F가 Astro 전제라 레거시 브리핑에 배포 불가하기 때문
- 전환 순서 4(프런트 배포)·6(규칙 배포)·10-A(운영 브라우저 검증)는 Astro 전환 시점으로 이동 — 프런트 없이 규칙을 배포하면 legacy 키 쓰기가 차단됨
- 설계 19(`deployments.frontend`/`.rules` 없으면 final delta 차단)는 유지 — C-2에서 최종 delta 오실행을 구조적으로 막아줌
- corpusOrphan 4건은 3-A 보존, multiCandidate 3건은 4-C 보류 — 합산 복제·임의 분할 금지 원칙과 정합하고 나중에 되돌릴 수 있음
- 5-B-2는 `scripts/migrate-likes.mjs` 확장으로 구현 — 파일 자체가 "execute·delta·verify는 5-B-2에서 구현"을 명시하고 인자 차단·manifest 빈 슬롯을 미리 두고 있음
- 문서 7계층: 인덱스 / 규칙 / 레퍼런스 / 하우투 / 결정(ADR) / 이력 / 핸드오프 — 규모에 따라 절이냐 파일이냐만 달라지고 계층 이름과 순서는 프로젝트 공통
- 핸드오프 원본은 MD + git. 노션은 사람용 미러 — `세션 핸드오프 운영 가이드 v2.0` §3.8
- `deploy.ps1` 검증 게이트는 staged 파일 대상(`--diff-filter=ACMR`) — 날짜 기준을 쓰면 과거 브리핑 수정·교체가 검증에서 빠짐
- 문서 저장소 배치 — 규칙·레퍼런스·하우투·결정은 git, 이력은 Notion DB, 핸드오프는 루트 `HANDOFF.md` 단일 파일. 노션 원본화 금지(`세션 핸드오프 운영 가이드 v2.0` §3.8)
- `docs/` 계층 폴더 확정 — `rules/`(2) · `reference/`(4) · `howto/`(3). `claude.md`·`dev-history.md`·`issues.md`는 `docs/` 직속 유지

### 세션 3 추가

- Q-A = **A-1** (`migrate-likes.mjs` 단일 파일 확장) — 파일이 top-level 스크립트라 A-2(분리)는 검증된 코드 전체를 export 함수로 재작성해야 하고, `toolHashes` 가 `import.meta.url` 자기해시라 분리 시 실제 로직이 manifest에 고정되지 않음
- Q-B = **B-1 재정의: 우회가 아니라 상호 요구** — 에뮬레이터 셸에도 `GOOGLE_APPLICATION_CREDENTIALS` 가 설정돼 있어 3중 대조가 그대로 통과한다. 따라서 우회 코드는 불필요하고, `--emulator` 와 `FIRESTORE_EMULATOR_HOST` 가 한쪽만 있으면 중단하는 게이트를 **추가**한다. 기존 인증·3중 대조는 한 줄도 바꾸지 않는다
- `applicationDefault()` 분기 삭제 확정 — 에뮬레이터에서도 정상 초기화됨이 실증됨
- `emulators:exec --project X` 는 자식 프로세스에 `GCLOUD_PROJECT` 를 내려준다 — CLI 실제 프로젝트와의 대조가 가능하므로 게이트에 포함
- 에뮬레이터 projectId 는 `dinol-news` 유지 — `demo-` 접두어를 쓰면 `EXPECTED_PROJECT_ID` 검사를 완화해야 하는데 그건 B-1을 택한 이유 자체를 무너뜨린다
- 정본 manifest = `%USERPROFILE%\dinol-manifest\5b-manifest-20260802-232639.json` (`migrationId 5b-20260802142639907-b10ee191`). 같은 날 12분 앞선 `…-2314.json` 은 구버전 도구 산출물이라 제외 — `toolHashes` 대조 없이는 구분되지 않는다
- 시드 원본은 **S-1(정본 manifest 재활용)** — 운영 Firestore 접근 0건. manifest에 229건 legacyId·count가 모두 있다
- `EXCEPTION_MAP` 은 `assets/likes-core.js` 에 있고 `migrate-likes.mjs` 는 해시 계산용으로만 참조한다. 방향은 **contentId → legacyId** 이며 조회는 `legacyKeyOf(contentId, url)` 내부에서 일어난다. migrate 222건 중 B형 30건
- 픽스처 해시 게이트 구조 — `migrationTool`(정본 manifest 출처값, 현재 파일과 대조 금지) / `runtimeMigrationTool`(현재 파일과 대조) / `contentCorpus` / `likesCore` / `exceptionMap`. `migrationTool` 을 현재 파일과 대조하면 도구를 고치는 순간 영구 실패한다
- 픽스처 파일 자체의 개행은 게이트에 영향 없음 — JSON 파싱 후 내부 문자열을 읽기 때문. `seed-emulator.mjs` 도 어느 게이트의 대상이 아니다
- `.gitattributes` 는 **최소 범위**로만 쓴다 — `scripts/migrate-likes.mjs text eol=lf` 한 줄. `.mjs`·`.json` 전체 규칙을 넣으면 코퍼스 273개가 renormalize되어 `contentCorpus` 가 무효화된다
- 커밋 브랜치는 `5b-2-emulator`(`63c640c` 에서 분기) — `astro` 는 코퍼스 파일 32개가 추가된 후속 상태라 전환하면 `contentCorpus` 게이트가 깨진다

### 세션 3 재갱신 추가

- **worktree 4개 고정 구조** — 브랜치를 전환하지 않고 폴더로 구분한다. 전환 시 OneDrive 때문에 디렉터리 삭제가 실패하고(`y/n` 프롬프트 7건), 해당 브랜치에만 있는 파일이 폴더에서 사라져 혼동을 낳는다

  | 폴더 | 브랜치 | 용도 | 터미널 라벨 |
  |---|---|---|---|
  | `dinol-news` | `main` | 브리핑 발행, `deploy.ps1` | `[터미널-프론트(로컬) · dinol-news]` |
  | `dinol-astro` | `astro` | 개발·문서·**`HANDOFF.md` 정본** | `[터미널-프론트(로컬) · dinol-astro]` |
  | `dinol-5b` | `5b-2-emulator` | 5-B-2 마이그레이션 | `[터미널-프론트(로컬) · dinol-5b]` |
  | `dinol-news-5a2f-check` | (detached) | 잔존물. §6 참조 | 사용 안 함 |

- `HANDOFF.md` 는 `astro` 에서만 추적된다 — `main`·`5b-2-emulator` 에는 없다(확인됨). 사본이 갈라질 여지가 없다
- **핸드오프는 기억이 아니라 조회 출력으로 작성한다** — 갱신 전 `git log --all --oneline --since=<세션시작>` · `git worktree list` · worktree별 `git status --short` · 노션 이번 세션 생성 행을 조회하고, 그 출력만 근거로 §5·§6 을 쓴다. 세션 3에서 기억으로 작성했다가 worktree 신설·`main` 커밋·백로그 2건이 누락됐다
- 파일을 Claude 에게 전달할 때는 **붙여넣기가 아니라 업로드** — 세션 3에서 업로드 사본의 SHA-256 이 워크트리 실물과 일치함이 `Get-FileHash` 로 확인됐다. 바이트가 보존되므로 개행·해시 논의가 오염되지 않는다. push 는 불필요하다
- **문서는 변경 발생 시점에 즉시 갱신한다** — 코드·UI·동작·구조·운영 방식이 바뀌면 관련 문서를 **같은 작업 안에서** 날짜 스탬프와 함께 고친다. "나중에 한 번에"는 누락을 만든다(세션 3에서 worktree 신설·`main` 커밋·백로그 2건이 그렇게 빠졌다). **`HANDOFF.md` 도 예외가 아니다**(작업 규칙 4)
- `claude.md` 의 `수정 예정 백로그` 표에 **신규 과제를 넣지 않는다** — 노션 백로그 DB 가 정본(`ef204c0`). 그 표는 문서 작업 중 즉시 눈에 띄어야 하는 것만 남기고, 처리된 행은 삭제 후 `dev-history.md` 에 반영한다

### 세션 4 추가

- **브리핑 날짜 = 루틴 실행 시점 KST + 1일**(`routine_instruction.md` §1). 22:00 실행으로 다음날 브리핑을 미리 만든다. 산출 날짜가 `index.json` 최근 발행일보다 2일 이상 앞서면 `최근 발행일 + 1일` 로 되돌린다(수동 재실행 시 밀림 방지)
- **문서 스탬프와 브리핑 날짜는 다르다** — 문서에 찍는 날짜는 실행 당일, 브리핑 날짜는 +1일. `claude.md` 「날짜 확인 규칙」에 명시됨
- `routine_instruction.md` 에 **경계 마커**(`<!-- ===== 여기부터 루틴 UI에 그대로 붙여넣는다 ===== -->`)를 넣었다. 마커 **위**는 레포 전용(갱신 이력·근거), **아래**가 루틴 UI 실행 프롬프트다. UI 갱신 시 **마커 아래 전체를 통째로 복사**한다 — 부분 수정 금지. 16,382자 → 14,401자(12.1%) 축소
- **제외 매체 규칙**(`news_sources.md` 「제외 매체」) — 여기 있는 매체는 검색에 떠도 카드 출처로 쓰지 않는다. 현재 ROOT IN NEWS 1건(창간 4개월·기자 서명 없음·주최사 제공 보도자료). 판정 기준 4항목: ① 기자 서명 ② 보도자료 전재 여부 ③ 1차 소스 인용 ④ 분야 전문성
- `deploy.ps1` 은 `[1/6]~[6/6]` 6단계다. `[4/6]` 이 validate 게이트 — **스테이징된 `news/**/Dinol_news_*.html` 만** 검사하고 브리핑 변경이 없으면 건너뛴다. 우회 스위치는 두지 않았다
- 게이트 판정은 **`validate.py` 종료 코드가 기준**이다(양방향 실증: 정상 exit 0 / ERROR exit 1). 출력 문자열 파싱은 보조이며, 파싱 실패가 배포를 막지 않는다 — 한글이 든 정규식은 콘솔 인코딩에 따라 매칭이 깨져 정상 브리핑까지 차단했다(`0aba576` 결함 → `c63a702` 수정)
- `validate.py` 는 **인자가 없으면 `news/` 전체를 검사**한다. 대상이 없을 때는 호출 자체를 하지 않아야 한다
- 작업 일지 노션 DB 스키마(조회로 확인) — 속성 8개(작업명·구분·결과·커밋·이전커밋·버전·날짜·내용) / 구분 7개(기획·디자인·분석·개발·변환·배포·문서) / 결과 5개(완료·실패·롤백·보류·대기). **옵션을 새로 만들지 않는다.** `claude.md` 에 있던 `IA`·`사이트맵`·`와이어프레임`·`진행도`·`진행중` 은 실재하지 않아 삭제했다
- 작업 일지 `날짜` 는 **git 커밋 타임스탬프**로 쓴다(`git log -1 --date=iso --format="%h %cd"`). 컨테이너·세션 시계를 쓰면 커밋 순서와 어긋난다(§6)
- **astro 문서 경로는 계층 구조다** — `docs/howto/routine_instruction.md` · `docs/reference/news_sources.md` · `docs/rules/guardrails.md`. `main` 은 `docs/` 최상위 평면 구조라 머지 시 rename 추적에 의존한다. 두 번의 머지 모두 추적에 성공했고 중복 파일은 생기지 않았다(확인됨)
- `main` 은 GitHub Pages 빌드 대상이라 `deploy.ps1` 로만 배포한다. `astro` 는 빌드 대상이 아니므로 `git` 명령으로 직접 커밋한다 — `deploy.ps1` 은 `main` 전용
- **(§6→§2 이동)** `deploy.ps1` 게이트 — 세션 3의 「검증 2건 미완」은 해소됐다. `[4/6]` 로 구현·커밋됐고 하네스 4케이스(정상·결함·인코딩 깨짐·파싱 실패)를 통과했다. **잔여는 실검사 경로 1건뿐이며 §4 로 옮겼다**
- **(§6→§2 이동)** push 상태 — `main`(`c63a702`)·`astro`(`459b216`) 모두 원격과 동기화됨(확인됨). `5b-2-emulator`(`e263c90`) 의 push 여부는 세션 4에서 확인하지 않았다(**모름**)

### 세션 5 추가

- `5b-2-emulator` 는 **push 되지 않았다**(확인됨) — `git ls-remote --heads origin 5b-2-emulator` 빈 출력. 세션 4의 「모름」이 해소됐다. 원격에 없으므로 raw URL 로 읽을 수 없고, 파일 전달은 업로드가 유일한 경로다
- `claude.md` 현행화 3건 반영 — worktree 4개 구조(「로컬」 행) · 핵심 원칙 4 「즉시 갱신」 강화 · 5-B 수치 214→229. 5-A-2R 행은 `dev-history.md` 반영이 선행돼야 해 §4 에 남긴다
- 작업 일지 노션 DB 에 **`브랜치` 속성 신설**(단일 선택: `main`·`astro`·`5b-2-emulator`·`없음`). 속성 9개가 됐다. **커밋이 남은 브랜치**를 넣고, 커밋 없는 작업은 `없음`. 배포/관리 세션과 개발 세션이 같은 DB를 쓰므로 구분용이다 — 세션 4 기재(속성 8개)는 그 시점 기준이라 그대로 둔다

## 3. 폐기한 접근 — 재제안 금지

- 5-A-2F를 레거시 브리핑에 배포 → `likes.js` 로드 HTML 0건, dataset 3종 0건, `dinol-firebase.js`에서 `likeKey()`·`initLikes()` 삭제됨
- 규칙 후퇴(id 정규식을 create에만 적용) → 규칙 미배포가 이미 같은 효과를 내고, 5-A-2R에서 기각한 안
- 핸드오프를 노션 페이지 원본으로 신설 → 가이드 v2.0이 명시적으로 금지(복사본은 갈라진다)
- 문서 폴더 이동을 5-B-2 완료 후로 미루기 → `sourceHead` 제약은 dry-run 이후에만 걸리므로 지금이 오히려 적기

### 세션 3 추가

- `seed-emulator.mjs` 의 `migrationTool` 대조를 `contentCorpus` 로 **교체** → 두 해시는 대체 관계가 아니다. `contentCorpus` 는 입력이, `migrationTool` 은 분류·검산 로직이 같은지를 본다. 교체하면 `NEW_ID_RE`·`bySlug`·blocker 판정 변경을 잡지 못한다. `contentCorpus` 는 추가 게이트로만 넣는다
- `.gitattributes` 로 `.mjs`·`.json` 전체 LF 고정 → 코퍼스 273개와 `likes-core.js` 가 renormalize되어 `contentCorpus`·`likesCore` 기대값이 동시에 무효화된다
- Fixture A 실행으로 픽스처 적합성까지 판정 → 검증 대상과 테스트 데이터 적합성을 같은 실행에 섞으면 실패 원인이 4가지로 갈려 구분되지 않는다
- Fixture B의 blocker 3종을 픽스처 3개로 분리 → 분류~사전검사 구간(184~280행)에 조기 중단이 없어 blocker가 누적 수집됨이 코드·실행으로 확인됨. 분리는 실행 3회로 늘 뿐 얻는 게 없다

## 4. 다음 액션

- [ ] **(즉시)** 8/9 브리핑 배포 때 `deploy.ps1` `[4/6]` **실검사 경로**를 확인한다 — ① `대상 1개` + 브리핑 경로 나열 ② validate 출력 ③ `통과 (exit=0)`. 브리핑 파일이 있는데 `브리핑 변경 없음 — 검증 건너뜀` 이 나오면 필터 정규식 `^news/.*/Dinol_news_\d{8}\.html$` 문제다. 현재까지 건너뜀 경로와 하네스 4케이스만 검증됨
- [ ] **(1순위)** `migrate-likes.mjs` 에 execute·delta·verify 모드 구현 (A-1). dry-run 전용 하드코딩 10개 지점을 모드 분기로 전환 — 특히 `existsSync(OUT)` die(execute는 정반대), `deployments` 초기화 금지(설계 19 무력화), `migrationId` 재사용, `runs[]` append, `sourceHead`·`inputHashes` 비교. 나머지 지점은 코드에서 재도출한다
  - 착수 방법: `dinol-5b\scripts\migrate-likes.mjs` 를 **업로드**하고, 해시가 `221fc9d0…` 인지 `Get-FileHash` 로 대조
- [ ] 구현 후 Fixture A/B로 에뮬레이터 쓰기 검증 → 그 시점의 `runtimeMigrationTool` 로 픽스처 2개 갱신 (1순위에 종속)
- [ ] `docs/rules/guardrails.md` 에 게이트 원칙 반영 — 미반영 상태. `dinol-astro` 에서 별도 diff·별도 커밋. **`deploy.ps1` 게이트가 실제로 생겼으므로(`0aba576`) 내용을 그에 맞춰 쓴다**
- [ ] `claude.md` 백로그 2행 정리 — 5-A-2R(19b21d2 완료) · 5-B(229문서/count 421/migrate 222). **표에 새로 쓰지 말고**, 완료된 행을 삭제하고 `dev-history.md` 에 반영한다(§2 노션 정본 원칙)
- [ ] ADR 신설 + `dev-history.md`·`issues.md` 판단 근거 이관 (문서 개편 5단계). 착수 시 노션 백로그의 `fortune-handoff.md 미이관 4건` 을 **함께 처리**한다 — 따로 하면 중복 작업
- [ ] `scripts/inspect-likes.mjs` · `inspect-0802.mjs` 커밋 여부 결정 (`dinol-5b` 에 미추적 유지 중, 세션 4 조회로 재확인)
- [ ] `5b-2-emulator` → `astro` 병합 시점·방식 결정. 병합 시 코퍼스가 305장이 되므로 새 dry-run 선행 필요
- [ ] 노션 작업 일지 `날짜` 순서 역전 정정 여부 결정 (§6). 커밋 타임스탬프로 소급 수정할지, 그대로 둘지
- [ ] `459b216`(HANDOFF 세션 3 재갱신) 노션 작업 일지 미기입 — 이번 세션 갱신 커밋과 함께 처리

## 5. 산출물

| 경로 | 버전 | 상태 |
|---|---|---|
| `scripts/migrate-likes.mjs` | 5-B-1 + B-1 게이트 | 커밋됨(e263c90). SHA-256 `221fc9d0…`. execute·delta·verify 미구현 |
| `scripts/seed-emulator.mjs` | 5-B-2 | 커밋됨(e263c90). 4중 게이트, `{ count }` 만 기록, 빈 컬렉션 fail-fast |
| `scripts/fixtures/likes-a.json` · `likes-b.json` | 5-B-2 | 커밋됨(e263c90). 20건(passed) / 23건(blocked) |
| `.gitattributes` | — | 커밋됨(e263c90). `scripts/migrate-likes.mjs text eol=lf` 한 줄 |
| 정본 dry-run manifest | 5-B-1 | `%USERPROFILE%\dinol-manifest\5b-manifest-20260802-232639.json`. git 밖. **삭제 금지** |
| `HANDOFF.md` | 세션 4 | 커밋됨(`57125ab`→`459b216`, astro). `dinol-astro` 루트에 상시 노출. **`astro` 에서만 추적** |
| `handoff/HANDOFF_v3.0.md` | — | **삭제됨**(`82c88a5`, main). 2026-07-19 이후 미수정, 이관 대상 아님이 확인됨 |
| `handoff/fortune-handoff.md` | — | `main` 에만 잔존. **삭제 금지** — 미이관 4건 있음(노션 백로그 등록됨) |
| `scripts/inspect-likes.mjs` · `inspect-0802.mjs` | — | 조사용. `dinol-5b` 에 미추적(`git status` 조회로 확인). 커밋 여부 미정 |
| `deploy.ps1` | `[4/6]` 게이트 | 커밋됨(`0aba576` 추가 → `c63a702` 판정 수정, main). 6단계. 하네스 4케이스 통과. **실검사 경로 미검증** — 8/9 배포 시 확인(§4) |
| `docs/rules/guardrails.md` 게이트 원칙 | — | 미반영. main 배치본은 checkout 으로 되돌림. astro `docs/rules/guardrails.md` 에 별도 반영 필요 |
| `firestore.rules` | 5-A-2R | 커밋됨(19b21d2). 배포는 Astro 전환 시점 |
| `scripts/daily/20260807.json` · `20260808.json` | 세션 4 | 커밋됨(`83b2a27`, astro). 카드 8장씩 메타(contentId·category_kr·category_en·impactScore·positions). **KR 카드 8장의 `category_en` 은 원본 HTML 에 없어 대응 표기함** |
| `docs/reference/news_sources.md` 「제외 매체」 | 세션 4 | 커밋됨(`8b5eeb2`, main → `43281ae` astro 반영). ROOT IN NEWS 1건 + 판정 기준 4항목 |
| `docs/howto/routine_instruction.md` 경계 마커 | 세션 4 | 커밋됨(`63f021e`, main → `43281ae` astro). 루틴 UI 사본은 마커 아래와 바이트 일치해야 함 |
| `news/2026/08/Dinol_news_20260807.html` · `20260808.html` | 세션 4 | 발행됨(`a4c5279` / 루틴 배포분). `published_urls.json` 317건 |
| 5-B-2 확정 설계 25항목 | — | 본 문서에 복사하지 않음. 세션 시작 메모 참조 |

## 6. 미해결 · 판단 보류

- `dinol-news-5a2f-check` worktree 제거 실패 — `.git`이 OneDrive 재분석 지점(`-a---l`, 105B). 하이드레이션 확인 미실행
- `5a2f-staged.patch`(42KB, 바탕화면) — `git apply --check --reverse` 가 `package.json:5` 에서 실패. 미반영분이 남은 것인지 이후 변경 때문인지 미판정. **삭제 금지**
- 날짜 스탬프 오류 — 이 세션 커밋·Notion 일부가 `2026-08-03` 으로 기록됐으나 실제는 `2026-08-05`. git 커밋 타임스탬프가 정본
- **노션 작업 일지 날짜 순서 역전** — 세션 4 기입 10행 중 앞부분은 컨테이너 시계, 뒷부분은 커밋 타임스탬프로 넣어 정렬이 깨졌다. `c63a702`(02:43 기록)가 `0aba576`(03:55 기록)보다 앞서 있으나 git 순서는 그 반대다. 시간을 넣는 목적이 「같은 날 순서 복원」이므로 **정정 여부를 결정해야 한다**(§4)
- `contentCorpus`·`likesCore` 해시가 작업 트리 개행에 의존 — 현재 Windows `core.autocrlf=true` 에서는 CRLF로 재현되지만 Linux·`autocrlf=false` 에서는 값이 달라진다. 백로그 등록됨
- `seed-emulator.mjs` BOM — 원본·패치본 모두 포함. 동작·게이트 영향 없어 조사하지 않기로 함. 백로그 미등록
- 세션 4 커밋 14건 — `main` 10건(`a4c5279`·`6510f95`·`6be7e45`·`6de8e63`·`b3f991e`·`8b5eeb2`·`63f021e`·`95b99d9`·`0aba576`·`c63a702`) / `astro` 4건(`25afce2`·`83b2a27`·`43281ae`·`459b216`). 조회로 확인
- 작업 트리 상태(세션 4 종료 시점, 조회로 확인) — `dinol-astro` clean · `dinol-news` clean · `dinol-5b` 미추적 2건(`inspect-*.mjs`) · `dinol-news-5a2f-check` 미확인
- `astro` 에 미완료 머지가 방치돼 있었다(`MERGE_HEAD=82c88a5`, 세션 3 잔여). 세션 4에서 `25afce2` 로 완료. **머지를 시작하면 그 세션 안에서 끝낸다**
- 8/8 브리핑 WARN 1건 수용 — AI 4장이 구독전략·점유율·모델공개·보안협의체로 전부 산업 동향이라 ★4~5 후보가 실제로 없었다. **별점을 올려 WARN 을 지우지 않았다**. AI×디자인 축이 §3 에 있는데 4장 중 0장이었던 것이 근본 원인
- `%TEMP%\HANDOFF_backup_20260808.md` — 머지 전 백업본. 개행만 다르고 내용은 동일. 삭제해도 무방
- 노션 백로그 등록 4건 — ① `--resume` 재개 경로 설계(선결: execute 구현·검증) ② 해시 게이트의 작업 트리 개행 의존 제거 ③ 저장소 OneDrive 경로 분리(선결: 5-B-2 완료, 우선순위 낮음) ④ `fortune-handoff.md` 미이관 4건 분해·이관 후 `handoff/` 폐기(선결: ADR 신설 시 함께)

---

## [갱신 규칙] — 다음 세션이 반드시 지킬 것

1. 이 파일을 **새로 쓰지 말고 읽고 수정**한다.
2. §2 확정 사항, §3 폐기한 접근의 기존 줄은
   **한 글자도 바꾸지 않고 그대로 복사**한다. 요약·의역·통합 금지.
3. §1, §4 는 전면 교체한다.
4. §6 에서 해결된 항목은 §2 로 **이동**시킨다(삭제 아님).
5. 산출물에 반영 완료된 §2 항목만 삭제하고, 지운 목록을 보고한다.
6. §3 은 삭제하지 않는다. 단, 해당 접근이 **물리적으로 불가능해진 경우에만**
   (구조가 바뀌어 그 방향 자체가 성립 안 될 때) GRAVEYARD.md 로 이관한다.
7. 상단 [작업 규칙]은 5개를 유지한다. 항목을 늘리지 않는다.
8. 헤더의 세션 번호와 날짜를 올린다.
