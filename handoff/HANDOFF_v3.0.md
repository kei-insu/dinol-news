# 디자인 놀이터 (dinol-news) — 세션 핸드오프 v3.0

> 작성: 2026-07-16 / 목적: 다음 세션 작업 연속성 인계
> **이번 사이클 핵심: 운세 코너(오늘의 별자리) UI 완성 + 사이트 전체 디자인 토큰 시스템 구축(폰트·컴포넌트·컬러) + 마스터 비밀번호 보안 패치.**
> **다음 세션 최우선: ① Firebase 콘솔 Auth 설정(보안 패치 마무리) ② 운세 실데이터 파이프라인(GitHub Action → fortune.json).**
> 이전 이력(v1~v2.5: 브리핑 생성·Firebase·팝업 개편·공용 CSS/JS 분리)은 §7 요약 참조.
>
> 📌 **이 핸드오프는 "상태"만 담는다.** 디자인 작업의 *방식*(피드백 실측 검증·토큰 원칙·가드레일)은 **`dinol-design-review` 스킬**에 있다. 디자인 피드백 검토나 스타일 수정 요청이 오면 그 스킬이 자동 트리거된다 — 여기 규칙을 중복 서술하지 않는다.

---

## 1. 사이트 개요

- **배포**: `https://kei-insu.github.io/dinol-news/` (GitHub Pages, 정적)
- **저장소**: `kei-insu/dinol-news` (main)
- **로컬**: 두 PC 사용 — kgblu `C:\Users\kgblu\OneDrive\바탕 화면\dinol-news\dinol-news` · jrdo `C:\Users\jrdo\Desktop\dinol-news\dinol-news`. **오갈 때 git 충돌 잦음 → 작업 전 반드시 `git pull`.**
- **배포**: `./deploy.ps1 "메시지"` (PowerShell, `$PSScriptRoot` 기반 PC 독립). Claude는 파일만 만들어 전달 → 인수님이 로컬 배치 후 deploy. **Claude는 직접 push 못 함.**
- **컨셉**: 매일 AI·디자인 뉴스 이중언어(한/영) 카드 브리핑 + 방명록(디놀 톡톡) + 좋아요 + **운세 코너(신규)**.
- **파일명 정책**: 전부 소문자·영문. 예외: 브리핑만 `Dinol_news_YYYYMMDD.html`(dinol.js READ_KEY 정규식·archive URL 연동).
- **문서 자동 동기화**: 코드/UI/구조 변경 시 관련 docs 같은 변경에 갱신. **단 변경 이력은 git이 관리** → design-guide엔 최종 스펙만(인라인 날짜·"이전 X→Y" 금지).

---

## 2. ★ 이번 사이클 작업 (핵심 — 전부 검증 완료, 배포 대기)

> 작업 *방식*(실측 검증·동의/반박·토큰 원칙·가드레일)은 **`dinol-design-review` 스킬** 참조. 아래는 *결과 상태*만.

### A. 디자인 토큰 시스템 — `docs/design-guide.md` (~900줄)
사이트 전체 폰트·크기·컬러의 단일 원천. 운세를 **최초 적용 영역**으로 삼음.
- **0장 값 원칙**: 공통값(토큰)/페이지 고유값(로컬 px)/예외값 분류. 스케일 밖 값을 근처 토큰에 끼워맞추기 금지, 죽은 토큰 금지. (규칙 상세 → 스킬)
- **1장 타이포**: **10단계** `12/14/16/18/20/24/28/32/36/40`. 프리미티브(`--step-*`)/시맨틱(`--fs-*`) 2계층. 행간 정수 px. **모바일=제목류(display·h1·h2·h3)만 한 칸 내림, 본문류 동일**. body 16/26(한글 163%). MO: display 36·h1 28·h2 20·h3 18. (기존 "MO가 PC보다 큼" 규칙은 폐기.)
- **2장 컴포넌트**: 높이 28/32/40/48(디놀 기본)/56 · 터치 44 · 아이콘 16/20/24/32 · 간격 4px그리드(`--space-*`) · radius 4/8/12/16/full · border 1/2.
- **3장 버튼**: 위계(Primary/Secondary/Tertiary/Destructive/Icon) 우선. 상태표는 "전환 시 생성" 토큰 표기(아직 미정의).
- **4장 컬러**: 3계층. 프리미티브 **35종**(Neutral 25·Ink 1·Orange 4·Purple 1·Red 2·Kakao 2). **포인트 `#ff7f3e`(--orange-500) 고정 = 디놀 아이덴티티, 변경 금지.** 4-7 대비 실측표(49조합): muted는 hover 표면 금지(4.04), disabled는 비활성 전용(어느 표면도 4.5 미달). 4-9 레거시 전환표(87 UI HEX→35 프리미티브). `--color-accent` 범용 금지(역할별로 text/icon/border/grad 분리).
- **5·8·10장**: 뉴스·톡톡·브리핑팝업 = ⏳ **전환 예정**(레거시 HEX 유지, 새 화면엔 쓰지 말 것). 10장은 UI 스펙만 — 데이터/보안 스펙은 dev-history·guardrails·issues로 이관 완료.
- **11장 운세**: ✅ 토큰 적용 완료(CSS·JS HEX 0). 페이지 고유값 표(원형 64px 등) 명시.

### B. 운세 화면 — `fortune.html` (~1500줄, UI 완성 / 데이터는 프리뷰)
- 자체 `<style>` 사용(dinol.css 미참조, 코너 전용 UI). 토큰 `:root` 파일 내 포함. 다른 영역 전환 시 dinol.css로 승격.
- **메인**: 3×4 그리드(max 880px). 카드 = 왼쪽 **원형 더미**(PC 64/MO 56, 이미지 미정) + 국문→영문(캡션)→기간(`MM.DD ~ MM.DD`). **모바일은 세로 스택**(2열 가로배치 시 텍스트 폭 64px로 깨짐 → 세로로). 심볼 이모지 삭제. 헤더 "오늘의 별자리"+"- 디자이너편 -"(오렌지).
- **팝업(드로어)**: PC 560 / MO 풀폭 바텀시트 90vh. 순서 = 심볼박스→국문→영문→운세→오늘의 확률→오늘의 기운(폰트·컬러)→오늘의 궁합. 별자리명에 럭키폰트 적용 안 함(기본 흰색).
- **오늘의 확률**(5항목): 항목당 3행 [아이콘 항목명 ··· %·상태]/[설명]/[전체폭 게이지]. **항목명 nowrap 필수**(고정폭 열 두면 4/5 줄바꿈). 게이지 전체폭.
- **오늘의 궁합**: 중앙 "나"+6 관계노드(팀장·동료디자이너·기획자·개발자·대표·클라이언트). matchType 6종(TYPE_W 가중치 찰떡5·영감4·안정4·성장3·변수2·긴장1). 등급 라벨·"최악 궁합" 금지(→ 스킬 가드레일). 최고/주의 배지만: 최고=굵은실선+행운색+링, 주의=점선+muted. 노드 클릭 → 하단 rel-detail 전환(기본=최고).
- 데이터: 파일 내 EMBEDDED 프리뷰 12종 + `fetch('fortune.json')` 폴백. 영문명·기간은 JS 상수 `SIGN_META`(fortune.json 스키마 밖). luckyColor는 데이터(토큰 아님). TYPE_W·STATE(확률 상태명 사다리)·LEGEND(유형 설명)는 fortune.html JS 상단 상수.

### C. 보안 패치 — 마스터 비밀번호 (`assets/dinol-firebase.js`, 코드 완료)
- **문제**: `const ADMIN_PW="481516"`이 public repo+브라우저 노출 → 누구나 마스터 비번 읽어 모든 글/댓글 삭제 가능. (v2에서 "이 값만 수정하면 됨"으로 안일하게 뒀던 것이 실은 심각한 노출이었음.)
- **조치(구조 개선, 값 변경 아님)**: ADMIN_PW/ADMIN_HASH **제거**(잔여 0). 운영자 판별 → **Firebase Auth 세션**(`onAuthStateChanged`→`IS_ADMIN`). 로그인 API `window.dinolAdmin.login(email,pw)/logout()`. 아바타(✨)는 문서 `admin:true` 필드로. addDoc에 `admin` 저장. 비번 6자리 예외 제거(4자리 고정). `node --check` 통과.
- ⛔ **481516은 폐기.** 새 Auth 계정 비번으로 재사용 금지(이미 공개됨).
- **남은 작업(인수님 · Firebase 콘솔)** → `firestore-admin.rules.md` 참조:
  Auth 이메일/비번 활성화 → 운영자 계정 생성(≠481516) → UID를 `firestore.rules`에 **병합**(콘솔 규칙 덮어쓰지 말 것). 이거 전에 dinol-firebase.js 배포하면 운영자 기능만 잠시 비활성(일반 흐름 정상).
- **정직한 한계(남음)**: 일반 사용자 4자리 비번 검증은 여전히 클라이언트 → API 직접 호출로 남의 글 삭제 가능. **별개 이슈**로 issues.md에 보류 등록(방명록 UX 변경 필요, 범위 큼).

---

## 3. ⚠️ 배포 대기 파일 (`/mnt/user-data/outputs/`)

| 파일 | 배치 | 비고 |
|---|---|---|
| `fortune.html` | 루트 | 덮어쓰기 |
| `docs/design-guide.md` | docs/ | 덮어쓰기 |
| `docs/issues.md` `docs/guardrails.md` `docs/dev-history.md` | docs/ | 덮어쓰기(보안·이관 반영) |
| `assets/dinol-firebase.js` | **assets/** | ⚠️ 콘솔 Auth 설정과 함께/후에. **루트 저장 금지(§5 함정)** |
| `firestore-admin.rules.md` | docs/(선택) | 콘솔 작업 안내서 |
| `docs/HANDOFF_v3.0.md` | docs/ | 이 문서 |

**배포 순서 안전**: 운세·docs 먼저 OK(방명록 무관, 운세는 자체 style이라 회귀 없음). dinol-firebase.js는 콘솔 Auth 후. 운세는 아직 어느 페이지에도 링크 없음 → 배포해도 방문자에 안 보임(URL 직접만). 정식 오픈 시 template+전체 브리핑에 진입점 추가 필요.

---

## 4. ⏭️ 다음 세션 미완 / 후보

- **[최우선] Firebase 콘솔 Auth 설정** (§2-C) → dinol-firebase.js 배포.
- **[핵심 미완] 운세 실데이터 파이프라인**: GitHub Action `.github/workflows/horoscope.yml`(freehoroscopeapi.com 매일 fetch → horoscope_raw.json) → 루틴이 번역·재해석 → `fortune.json` 생성. 현재 fortune.html은 EMBEDDED 프리뷰로만 돌아감.
- **별자리 일러스트**: 원형 더미(.z-illust)·심볼박스(.d-symbox)에 `<img>`만 넣으면 됨. 이전에 12종 캐릭터 일러스트(1024×1536)를 WebP 640px 최적화한 적 있으나, 카드가 원형으로 바뀌어 **원형 크롭 기준 재작업 검토**.
- **죽은 CSS 제거**: dinol.css ~678줄 `.gb-entry-actions/.gb-act-edit/.gb-act-del`(케밥으로 대체, 렌더 0회). issues.md 기록됨. 톡톡 회귀 테스트 후 제거 → dev-history 이동.
- **레거시 토큰 전환**: 뉴스·톡톡·브리핑팝업 폰트/컬러를 토큰으로(5·8·10장 ⏳).
- **[상시] 유지보수 로드맵**: 1단계 공용 CSS/JS 분리(✅ 완료) → 2단계 카드 콘텐츠 JSON 분리 → 3단계 Eleventy/Astro. (§7)

---

## 5. 운영/기술 참고 (재발 방지)

- **★★ 배포 함정 = 파일 위치**: `dinol-firebase.js`를 **루트에 잘못 저장**하면 HTML이 읽는 `assets/dinol-firebase.js`는 구버전 그대로 → 배포해도 안 바뀜. 반드시 **assets\ 안에** 덮어쓰고 루트 중복본 삭제. JS 수정 안 먹힐 때: ①`Select-String -Path "assets\dinol-firebase.js" -Pattern "고친로직"` ②`(Get-Item ...).Length` ③`git status`(clean이면 파일 안 바뀐 것) ④배포 후 콘솔 `fetch("../../../assets/dinol-firebase.js?v="+Date.now())`로 라이브 검증.
- **배포 반영 확인**: Ctrl+Shift+R 강력 새로고침 / Network 200·최신 / 콘솔 fetch 내용 검증. CDN 캐시로 구버전 잔존 쉬움.
- **재배포 트리거**: "Deployment failed" (GitHub 일시장애) → 빈 커밋 `git commit --allow-empty -m "retrigger" && git push`. 단 실제 파일 수정 시엔 `git add` 후 커밋(빈 커밋만 날려 구버전 유지 실수 주의).
- **샌드박스 검증**: Playwright(chromium 설치됨) headless 렌더·측정 가능. raw.githubusercontent.com으로 현재 배포본 curl 가능(**api.github.com은 rate limit**). Firebase 실통신(gstatic/googleapis)은 샌드박스 차단 → 배포 후 라이브에서만. fortune.html을 file://로 열면 fetch('fortune.json') 403 정상(EMBEDDED 폴백).
- **스크린샷**: 이미지 뷰어가 간헐적으로 [image]만 반환 → getComputedStyle 실측으로 교차검증.
- **보안 한계**: 방명록 비번 검증 클라이언트 측(§2-C). Spark 플랜이라 Cloud Functions 미사용.
- **중복 발행 방지**: `published_urls.json` 대장 + `build_published_urls.py`. 루틴 확인선 "대장 대조: 후보 N·중복 제외 M·최종 8(전부 신규)" 후에만 배포.

### Firebase (완료·배포·검증됨)
- 프로젝트 `dinol-news`(Spark), Firestore `asia-northeast3(Seoul)`, `(default)` DB.
- 톡톡: `guestbook` 컬렉션 `{nick, body, pwHash(SHA-256), admin, createdAt}` + 서브컬렉션 `comments`(+`commentCount`). 좋아요: `likes` 컬렉션.
- App Check: reCAPTCHA v3 **Enforce ON** 검증됨. 사이트키 `6LcW4kQtAAAAAJ5-eZc-SpxCrQ37bfTaYHs7v_yd`.
- config(공개 가능): apiKey `AIzaSyD84D4xoyD74W263XBiy7uRfNX-Oree5Xo` · authDomain `dinol-news.firebaseapp.com` · projectId `dinol-news` · storageBucket `dinol-news.firebasestorage.app` · messagingSenderId `212617826818` · appId `1:212617826818:web:e5ab06e9bad469c7e00d1b`.
- Firestore 보안규칙은 **콘솔에만**(git 아님) → 구조 변경 시 규칙도 함께.

---

## 6. 폴더 구조

```
dinol-news/
├── index.html · archive.html · privacy.html · template.html
├── fortune.html          ★ 운세(신규, UI 완성·데이터 프리뷰)
├── index.json · published_urls.json · deploy.ps1 · .nojekyll
├── assets/  dinol.css · dinol.js · dinol-firebase.js ★ · ai-design-news.png
├── docs/    design-guide.md · claude.md · routine_instruction.md · dinol_policy.md(policy)
│            · news_sources.md · dev-history.md · guardrails.md · issues.md
│            · fortune-handoff.md · HANDOFF_v3.0.md ★
├── scripts/ build_published_urls.py
└── news/2026/MM/Dinol_news_YYYYMMDD.html   (루트참조 ../../../)
```

**스킬** (레포 밖, Claude 스킬 디렉터리): `dinol-design-review` — 디자인 피드백 검토·스타일 수정 시 자동 트리거. 실측 검증 방식·토큰 원칙·가드레일 담음. 핸드오프와 역할 분리(핸드오프=상태 / 스킬=방식).
경로: 브리핑은 `news/YYYY/MM/`(3단계) → `../../../`로 루트 참조.

---

## 7. 이전 세션 요약 (v1~v2.5)

- **v1~v2**: 사이트 구축, 폴더 재구성(news/YYYY/MM/), Firebase 연동(톡톡·좋아요·App Check), 헤더 로고 이미지화, 썸네일 언어정책(C안=기사 원문 언어).
- **v2.5**: App Check 차단 이슈 해결(원인=구버전 배포, App Check 코드 없던 것). 방명록 비번 관련·autofill 흰박스(`:-webkit-autofill` box-shadow inset 오버라이드). 팝업 UI 대개편(폰트·컬러 명도차 구분, 화살표↗ 제거, 닉네임 12자, em대시 제거·pre-line 단락).
- **v2.5~현재 사이**: **공용 CSS/JS 분리 완료**(assets/dinol.css·dinol.js — 브리핑은 link 한 줄, 전역 스타일 1곳 수정으로 소급). 이번 v3.0의 토큰 시스템은 이 위에서 진행.
- 상세: `journal.txt` 카탈로그 및 `/mnt/transcripts/` 참조. **이번 v3.0 세션도 압축(compaction) 발생한 긴 세션 → 다음은 새 세션 권장.** 직전 트랜스크립트: `/mnt/transcripts/2026-07-19-06-37-55-dinol-fortune-design-system.txt`.
