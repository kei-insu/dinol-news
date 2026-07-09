# claude.md — 디놀 프로젝트 인덱스 & 핸드오프 규칙

| 최종 갱신 | 최근 변경 |
|---|---|
| 2026-07-10 | 날짜 확인 프로세스 유지, 갱신정보 상단 이동 |

> **이 문서 하나만 세션 시작 시 로드한다.** 나머지는 목차를 보고 그 세션에 필요한 것만 읽는다.
> 원본(단일 진실 원천): `github.com/kei-insu/dinol-news/docs/`
> raw 읽기: `https://raw.githubusercontent.com/kei-insu/dinol-news/main/docs/<파일명>`

---

## ⚑ 세션 시작 프로세스 (Claude가 매번 순서대로)

| 순서 | 할 일 |
|---|---|
| 1 | **오늘 날짜 확인** — 아래 "날짜 확인" 규칙 참조. 문서 스탬프·브리핑에 쓸 오늘 날짜를 먼저 확정 |
| 2 | 이 `claude.md`(인덱스) 읽기 |
| 3 | 목차에서 **오늘 작업에 관련된 문서만** 추가로 읽기(전부 X → 토큰 절약) |
| 4 | 작업 수행 |
| 5 | 코드·구조 변경 시 **관련 문서에 행 추가/갱신 + 오늘 날짜 스탬프** |

### 날짜 확인 규칙 (중요)
- Claude는 현재 날짜를 스스로 정확히 알기 어려움 → **세션 시작 시 사용자에게 오늘 날짜를 확인**하거나, 사용자가 명시한 날짜를 사용한다.
- 확인된 날짜를 그 세션의 모든 문서 스탬프·브리핑 날짜에 일괄 사용.
- 문서에 날짜를 넣을 때: **확실히 아는 건 해당일**, 불확실은 **오늘 날짜** 또는 `~오늘날짜`(= "이 시점엔 이미 존재") 표기.
- 사용자 시작 멘트 예시: *"디놀 작업 이어서. 오늘은 2026-07-10. docs/claude.md 읽고 시작해."*

---

## 문서 목차

| 문서 | 언제 읽나 | 내용 | 날짜 열 |
|---|---|---|---|
| `policy.md` | 정책·규칙·컨벤션 | 확정 정책(파일명·문서화·언어·톡톡·발행·확장) | 확정일 |
| `dev-history.md` | 기존 기능 이해·확장 | 개발한 것(기능/파일/내용/상태) | 완료일 |
| `issues.md` | 버그·장애 대응 | 크리티컬 이슈·해결·재발방지 | 발생일 |
| `design-guide.md` | UI·스타일 | 컬러·폰트·컴포넌트·톡톡 UI 규칙 | — |
| `guardrails.md` | 배포·보안·위험 작업 전 | 하면 안 되는 것 | — |
| `testing.md` | 배포 전 검증 | 검증 절차·체크리스트 | — |

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
├─ scripts/ build_briefing.py
└─ docs/                  ← 이 문서들
```

### 핵심 원칙
| # | 원칙 |
|---|---|
| 1 | 상단 방명록 폼은 template + 모든 브리핑에 복제 → 변경 시 전체 파일 수정 |
| 2 | 배포 시 `git status`로 스테이징 확인 필수 |
| 3 | `firestore.rules`는 Firebase 콘솔에 붙여넣기(git 아님) |
| 4 | 작업 후 관련 문서 갱신 + 날짜 스탬프 |


_git 이력이 상세 버전 관리를 대신함._
