# HANDOFF — dinol-news

> 갱신: 2026-08-07 / 세션 3 (재갱신)

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

Q-A·Q-B가 모두 해소됐고 5-B-2의 **실증 환경 구축이 끝났다**. B-1 오실행 방지 게이트,
시드 스크립트, 픽스처 2종을 `5b-2-emulator` 브랜치(`e263c90`)에 커밋했고
Fixture A(passed)·Fixture B(blocked, blocker 3종) 실증을 통과했다.

남은 것은 **execute·delta·verify 모드 구현**이다. `migrate-likes.mjs` 는 여전히 dry-run 전용이며,
A-1(단일 파일 확장)으로 dry-run 전용 하드코딩 10개 지점을 모드 분기로 바꿔야 한다.
그 10개 지점은 **코드에서 직접 도출한 것**이지 별도 설계 메모에서 나온 것이 아니다.
따라서 `migrate-likes.mjs` 실물만 있으면 착수 가능하고, 25항목 설계 메모가 없어도 막히지 않는다.

작업 트리는 **worktree 4개로 분리**됐다(§2). 브랜치 전환이 필요 없으므로
`git switch` 를 쓰지 말고 해당 폴더의 터미널에서 작업한다.
문서 개편은 5단계 중 ADR 신설만 남아 있다.

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

- [ ] **(1순위)** `migrate-likes.mjs` 에 execute·delta·verify 모드 구현 (A-1). dry-run 전용 하드코딩 10개 지점을 모드 분기로 전환 — 특히 `existsSync(OUT)` die(execute는 정반대), `deployments` 초기화 금지(설계 19 무력화), `migrationId` 재사용, `runs[]` append, `sourceHead`·`inputHashes` 비교. 나머지 지점은 코드에서 재도출한다
  - 착수 방법: `dinol-5b\scripts\migrate-likes.mjs` 를 **업로드**하고, 해시가 `221fc9d0…` 인지 `Get-FileHash` 로 대조
- [ ] 구현 후 Fixture A/B로 에뮬레이터 쓰기 검증 → 그 시점의 `runtimeMigrationTool` 로 픽스처 2개 갱신 (1순위에 종속)
- [ ] `docs/rules/guardrails.md` 에 게이트 원칙 반영 — 미반영 상태. `dinol-astro` 에서 별도 diff·별도 커밋
- [ ] `claude.md` 백로그 2행 정리 — 5-A-2R(19b21d2 완료) · 5-B(229문서/count 421/migrate 222). **표에 새로 쓰지 말고**, 완료된 행을 삭제하고 `dev-history.md` 에 반영한다(§2 노션 정본 원칙)
- [ ] ADR 신설 + `dev-history.md`·`issues.md` 판단 근거 이관 (문서 개편 5단계). 착수 시 노션 백로그의 `fortune-handoff.md 미이관 4건` 을 **함께 처리**한다 — 따로 하면 중복 작업
- [ ] `scripts/inspect-likes.mjs` · `inspect-0802.mjs` 커밋 여부 결정 (`dinol-5b` 에 미추적 유지 중, 조회로 확인됨)
- [ ] `5b-2-emulator` → `astro` 병합 시점·방식 결정. 병합 시 코퍼스가 305장이 되므로 새 dry-run 선행 필요

## 5. 산출물

| 경로 | 버전 | 상태 |
|---|---|---|
| `scripts/migrate-likes.mjs` | 5-B-1 + B-1 게이트 | 커밋됨(e263c90). SHA-256 `221fc9d0…`. execute·delta·verify 미구현 |
| `scripts/seed-emulator.mjs` | 5-B-2 | 커밋됨(e263c90). 4중 게이트, `{ count }` 만 기록, 빈 컬렉션 fail-fast |
| `scripts/fixtures/likes-a.json` · `likes-b.json` | 5-B-2 | 커밋됨(e263c90). 20건(passed) / 23건(blocked) |
| `.gitattributes` | — | 커밋됨(e263c90). `scripts/migrate-likes.mjs text eol=lf` 한 줄 |
| 정본 dry-run manifest | 5-B-1 | `%USERPROFILE%\dinol-manifest\5b-manifest-20260802-232639.json`. git 밖. **삭제 금지** |
| `HANDOFF.md` | 세션 3 | 커밋됨(`57125ab`, astro). `dinol-astro` 루트에 상시 노출 |
| `handoff/HANDOFF_v3.0.md` | — | **삭제됨**(`82c88a5`, main). 2026-07-19 이후 미수정, 이관 대상 아님이 확인됨 |
| `handoff/fortune-handoff.md` | — | `main` 에만 잔존. **삭제 금지** — 미이관 4건 있음(노션 백로그 등록됨) |
| `scripts/inspect-likes.mjs` · `inspect-0802.mjs` | — | 조사용. `dinol-5b` 에 미추적(`git status` 조회로 확인). 커밋 여부 미정 |
| `deploy.ps1` | 게이트 추가본 | main 작업 트리 배치. **검증 2/4에서 중단**, 8/3·8/5 발행은 수동이라 미실행 |
| `docs/rules/guardrails.md` 게이트 원칙 | — | 미반영. main 배치본은 checkout 으로 되돌림. astro `docs/rules/guardrails.md` 에 별도 반영 필요 |
| `firestore.rules` | 5-A-2R | 커밋됨(19b21d2). 배포는 Astro 전환 시점 |
| 5-B-2 확정 설계 25항목 | — | 본 문서에 복사하지 않음. 세션 시작 메모 참조 |

## 6. 미해결 · 판단 보류

- `dinol-news-5a2f-check` worktree 제거 실패 — `.git`이 OneDrive 재분석 지점(`-a---l`, 105B). 하이드레이션 확인 미실행
- `deploy.ps1` 게이트 검증 2건 미완 — staged 추출·중단 지점 도달. 다음 `./deploy.ps1` 실행 때 확인
- `5a2f-staged.patch`(42KB, 바탕화면) — `git apply --check --reverse` 가 `package.json:5` 에서 실패. 미반영분이 남은 것인지 이후 변경 때문인지 미판정. **삭제 금지**
- 날짜 스탬프 오류 — 이 세션 커밋·Notion 일부가 `2026-08-03` 으로 기록됐으나 실제는 `2026-08-05`. git 커밋 타임스탬프가 정본
- `contentCorpus`·`likesCore` 해시가 작업 트리 개행에 의존 — 현재 Windows `core.autocrlf=true` 에서는 CRLF로 재현되지만 Linux·`autocrlf=false` 에서는 값이 달라진다. 백로그 등록됨
- `seed-emulator.mjs` BOM — 원본·패치본 모두 포함. 동작·게이트 영향 없어 조사하지 않기로 함. 백로그 미등록
- 노션 백로그 등록 4건 — ① `--resume` 재개 경로 설계(선결: execute 구현·검증) ② 해시 게이트의 작업 트리 개행 의존 제거 ③ 저장소 OneDrive 경로 분리(선결: 5-B-2 완료, 우선순위 낮음) ④ `fortune-handoff.md` 미이관 4건 분해·이관 후 `handoff/` 폐기(선결: ADR 신설 시 함께)
- 세션 3 커밋 3건(조회로 확인) — `e263c90`(5b-2-emulator) · `57125ab`(astro) · `82c88a5`(main). **셋 다 push 안 함.** `astro` 는 origin 대비 33커밋 앞섬

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
