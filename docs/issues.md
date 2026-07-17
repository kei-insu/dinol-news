# issues.md — 오류/이슈 문서

| 최종 갱신 | 최근 변경 |
|---|---|
| 2026-07-15 | 마스터 비번 Auth 전환(코드 완료)·클라이언트 검증 한계·고아 댓글·죽은 CSS 등록 |
| 2026-07-10 | 상세 정보 복원(압축 해제), 강도 열 추가 |

> 크리티컬 이슈·해결·재발 방지. 강도: 높음 / 중간 / 낮음. 상태: 완료 / 진행중 / 외부.
> **원칙: 간결함보다 정확·완전한 정보 우선. 길어도 됨.**

## 주요 이슈

| 날짜 | 강도 | 이슈 | 증상 | 원인 | 해결/교훈(상세) | 상태 |
|---|---|---|---|---|---|---|
| 2026-07-15 | 높음 | 마스터(운영자) 비밀번호 공개 노출 | `assets/dinol-firebase.js`에 `const ADMIN_PW = "481516"` 하드코딩. public repo + 브라우저에서 그대로 조회되어 **누구나 마스터 비번을 읽어 모든 글/댓글을 수정·삭제 가능**했음 | 클라이언트 JS에 인증 비밀을 둠. 마스터 권한 판별을 클라이언트에 위임(클라이언트 검증은 UX 편의일 뿐 보안 경계가 아님) | **코드 조치 완료**: ①`ADMIN_PW`·`ADMIN_HASH` 상수 **제거**(잔여 참조 0) ②운영자 판별을 **Firebase Auth 세션**(`onAuthStateChanged` → `IS_ADMIN`)으로 이전 ③로그인 API `window.dinolAdmin.login/logout` ④운영자 아바타(✨)를 해시 대조 → 문서의 `admin:true` 필드 기준으로 변경 ⑤비번 입력 6자리 예외 제거(4자리 고정). ⛔ **비번 값 변경이 아니라 폐기** — 새 Auth 계정 비밀번호로 `481516` 재사용 금지(이미 공개됨). **남은 작업(사용자)**: Firebase 콘솔에서 Auth 이메일/비번 활성화 + 운영자 계정 생성 + UID를 `firestore.rules`에 반영(`firestore-admin.rules.md` 참조) | 진행중 |
| 2026-07-15 | 중간 | 일반 사용자 비번 검증이 클라이언트에만 존재 | 방명록 글·댓글의 4자리 비번 대조를 브라우저 JS가 수행. Firestore 규칙은 `update`·`delete`를 넓게 허용 → **API를 직접 호출하면 남의 글을 지울 수 있음** | 규칙이 사용자 비번을 알 수 없어 서버측 소유권 검증 불가. 방명록의 "비번 4자리" UX가 Auth 없이 설계됨 | 마스터 비번 이슈와 **별개**. 근본 해결은 사용자도 Firebase Auth(익명 로그인 등)로 소유권을 갖게 하고 규칙에서 `request.auth.uid == resource.data.uid` 대조. 방명록 UX 변경이 필요해 범위가 큼 → 보류. 현재 위험도: 스팸/장난 삭제 가능하나 App Check(reCAPTCHA v3 Enforce)가 일부 완화 | 보류 |
| 2026-07-15 | 중간 | 글 삭제 시 고아 댓글 문서 잔존 | 방명록 글을 삭제해도 하위 `guestbook/{글}/comments` 문서가 남는다. UI엔 안 보이지만 Firestore에 계속 존재 | Firestore는 문서 삭제 시 **하위 서브컬렉션을 자동 삭제하지 않는다**(설계상 동작) | 대응 후보: ①글 삭제 시 클라이언트가 댓글을 일괄 삭제(문서 수 많으면 실패 위험) ②Cloud Functions 재귀 삭제(Spark 무료 티어에선 불가) ③주기적 수동 정리. 현재는 **읽기 비용·UI 영향 없음**이라 보류. Spark 유지 방침상 ③이 현실적 | 진행중 |
| 2026-07-15 | 낮음 | 죽은 CSS 잔존 (`gb-entry-actions`) | `assets/dinol.css` 678줄의 `.gb-entry-actions .gb-act-edit/.gb-act-del`(모바일 min-height 34px) 규칙이 남아 있음 | 방명록 옵션이 **케밥 메뉴(`.gb-kebab`)로 대체**됐는데 구 CSS를 안 지움. 실제 렌더 코드(`dinol-firebase.js`)에서 `gb-entry-actions` 참조 **0회**로 확인 | 이 죽은 규칙 때문에 design-guide에 "모바일 터치 34px 예외"가 유령 규칙으로 남아 접근성 기준(44px)을 훼손하고 있었음 → **가이드에서 예외 삭제 완료**. CSS 제거 + 회귀 테스트 후 dev-history.md에 기록하고 이 이슈 종료 | 진행중 |
| 2026-07-10 | 높음 | HTML 미배포 | 상단 폼 이모지·카운터가 사이트에 안 보임. CSS는 반영됐는데 HTML만 옛 버전 | 상단 방명록 폼 마크업이 template+모든 브리핑에 복제돼 있는데 일부만 배포됨. 또는 제공한 새 HTML을 로컬에 안 덮어써서 git이 "변경 없음"으로 인식(git status에 안 뜸) | ①폼 변경 시 template+브리핑 전체를 다 고치고 배포. ②`git diff --stat <파일>`이 비면 이미 최신(변경 없음). `git log --oneline -- <파일>`로 커밋 이력 확인. ③배포 전 git status로 스테이징 확인. ④콘솔 F12에서 `document.getElementById('gbSmile')`가 null이면 옛 HTML | 완료 |
| 2026-07-10 | 중간 | 루틴 옛 폼 | 7/8 브리핑만 상단 폼이 구버전(gb-tsmile·gb-content-wrap 없음, gbSmile=null) | 루틴이 template 업데이트 전에 생성했거나 옛 template을 캐시/참조. 7/9는 최신 template 참조라 정상 | 해당 파일 상단 폼을 새 구조로 수동 변환(정규식 치환). template 최신화 후 루틴 생성물은 자동으로 새 구조. 외부 에셋(dinol.css/js) 쓰므로 폼 마크업만 고치면 나머지는 자동 적용 | 완료 |
| 2026-07-10 | 중간 | git add 전체 실패 | `git add ... firestore.rules ...` 실행 시 "pathspec did not match any files"로 전체 실패→아무것도 스테이징 안 됨 | firestore.rules가 로컬 저장소에 없음(Firebase 콘솔에만 붙여넣음). git은 명령 내 파일 하나라도 없으면 전체 취소 | firestore.rules는 콘솔 전용이므로 git add에서 제외하고 나머지만 올림. 기록용으로 git에 두려면 로컬에 파일 생성 후 함께 커밋 | 완료 |
| 2026-07-10 | 높음 | Actions 배포 멈춤 | push 후 pages-build-deployment가 "Queued"로 수 분~수십 분 멈춤. 로그에 "Waiting for a runner to pick up this job" | GitHub 인프라 장애. githubstatus.com에서 Actions "Degraded" 확인됨. 사용자 코드·설정 문제 아님(Pages는 Normal, 러너만 안 붙음) | githubstatus.com에서 Actions 상태 확인. 장애면 복구 대기(코드는 이미 push돼 안전). 정상인데 멈추면 해당 run에서 `Re-run jobs` 또는 빈 커밋(`git commit --allow-empty -m "재시도"`)으로 재트리거 | 외부 |
| 2026-07-14 | 중간 | 7/14 카드 필드 누락 | 드로어에 실무영향도·큐레이션노트 안 뜸 | 7/14가 옛 스킴으로 생성됨: `data-impact`(텍스트)를 씀(드로어는 `data-impact-score` 정수를 읽음) + `data-comment` 누락. 라이브 루틴이 레포 지침보다 옛 버전이었을 가능성 | 8장에 `data-impact-score`(정수)+`data-comment`(큐레이션 노트) 패치. routine_instruction.md를 라이브 지침(지침.txt)과 동기화. 재발 방지: 루틴 UI=지침.txt 일치 확인 | 완료 |
| 2026-07-10 | 높음 | 규칙 미반영 긴 글 거부 | 코드에서 글자수 늘렸는데(500/1000) 긴 글 저장 시 거부됨 | Firestore 규칙(콘솔)의 body.size() 제한을 안 바꿈. 코드-규칙 불일치 | 글자수 변경 시 firestore.rules 4곳(글 create/update, 댓글 create/update) 동시 반영 후 콘솔 게시. sed 체이닝 주의: `s/300/500/; s/500/1000/`는 300→500→1000 연쇄로 댓글까지 1000 되는 버그 발생했음. 라인별로 정확히 치환 | 완료 |

## 반복 함정 (체크리스트)

| 날짜 | 강도 | 함정 | 방지법(상세) |
|---|---|---|---|
| 2026-07-10 | 중간 | iOS 입력 줌 | iOS Safari는 폰트 16px 미만 입력칸에 포커스 시 페이지를 확대→화면이 튐/이동. 모바일 입력칸은 16px 이상 유지. (데스크톱은 15px여도 무관) |
| 2026-07-10 | 낮음 | CSS margin 단축 | `margin: t r b auto` 단축 표기가 앞서 선언한 `margin-left: auto`를 덮어써 우측 정렬이 깨짐. 우측 정렬 유지하려면 단축에서 left를 auto로 |
| 2026-07-10 | 중간 | sed 체이닝 | 한 sed에 `s/A/B/; s/B/C/`처럼 연쇄하면 A→B→C로 이중 적용됨(의도치 않게 전부 C). 라인 지정 또는 개별 실행 |
| 2026-07-10 | 낮음 | OneDrive + git | 저장소가 OneDrive 동기화 폴더에 있으면 OneDrive↔git 충돌 가능(파일 잠금·중복 동기화). 문제 시 의심 |
| 2026-07-10 | 중간 | 다중 PC 작업 | 다른 PC(다른 계정)로 옮기면 로컬이 최신 아닐 수 있음. `git pull` 먼저 해서 원격과 맞추기 |
| 2026-07-10 | 낮음 | 진단 팁 | `document.getElementById('gbSmile')`=null → 옛 HTML 배포됨. `git diff --stat <파일>` 빈 결과 → 로컬=원격, 이미 최신. `git log --oneline -- <파일>` → 커밋 이력 확인 |
| 2026-07-10 | 중간 | 좋아요 이월(중복 발행) | 새 브리핑 카드에 좋아요가 이미 찍혀 보임 | ①좋아요가 URL 기준 저장이라 같은 URL 재등장 시 과거 좋아요 이월 ②같은 기사를 다시 큐레이션(중복 발행)함. 실제 7/1~7/9에 URL 3건 중복 확인 | ①likeKey에 브리핑 날짜 접두어 추가(날짜+URL)→매일 분리 ②published_urls.json 대장으로 중복 발행 차단. ⚠️key 변경으로 기존 좋아요 카운트는 0으로 리셋됨 | 완료 |
| 2026-07-07 | 중간 | 고아 댓글 문서 | 방명록 글 삭제 시 하위 comments 서브컬렉션은 **자동 삭제 안 됨**(Firestore 특성). 글은 사라져도 댓글 문서가 남아 고아가 됨. 필요 시 별도 정리 로직 고려 |

_git 이력이 상세 버전 관리를 대신함._
