# issues.md — 오류/이슈 문서

| 최종 갱신 | 최근 변경 |
|---|---|
| 2026-07-10 | 상세 정보 복원(압축 해제), 강도 열 추가 |

> 크리티컬 이슈·해결·재발 방지. 강도: 높음 / 중간 / 낮음. 상태: 완료 / 진행중 / 외부.
> **원칙: 간결함보다 정확·완전한 정보 우선. 길어도 됨.**

## 주요 이슈

| 날짜 | 강도 | 이슈 | 증상 | 원인 | 해결/교훈(상세) | 상태 |
|---|---|---|---|---|---|---|
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
