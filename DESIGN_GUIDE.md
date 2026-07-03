# 디자인 놀이터 — 디자인 가이드

> 사이트 전반의 **텍스트 · 버튼 · 아이콘 · 컬러** 스펙 단일 기준.
> 모든 값은 `template.html`에 실제로 반영되어 있으며, 매일 생성되는 브리핑(`Dinol_news_YYYYMMDD.html`)도 이 가이드를 따른다.
> 값을 변경할 때는 이 문서와 해당 파일을 함께 수정한다.
> 최종 갱신: 2026-07-02

---

## 1. 텍스트

| 페이지 | 용어 (class) | 예시 | PC | MO | 컬러(hex) |
|---|---|---|---|---|---|
| **메인** | 사이트 타이틀 `site-title` | 디자인 놀이터 | 18px / w300 | 15px | `#aaaaaa` |
| | 히어로 부제 `site-sub` | AI & Design News | 46px / w700 | 32px | `#ffffff` |
| | 발행일자 `site-date` | July 2, 2026 | 11px / w400 | 11px | `#888888` |
| | 섹션 헤더 `section-header h2` | AI · Design | 21px / w700 (자간 7px) | 16px (자간 4px) | `#ffffff` |
| | 카드 출처 `card-source` | AI타임스 · 2026. 07. 01 | 11px / w400 | 12px | `#999999` |
| | 카드 제목 `card-title` | 앤트로픽, '페이블 5'… | 15px / w600 | 17px | `#ffffff` |
| | EN 배지 `thumb-en` | EN | 12px / w400 · italic | 13px | `#ffffff` |
| | 썸네일 라벨 `thumb-label` | 복귀 · 투자 | 28px / w300 | 26px | `#ffffff` (투명도 42%) |
| | 저작권 `footer-copy` | © 2026 디자인놀이터… | 13px / w600 (lh 1.6) | 13px | `#888888` |
| | 푸터 안내문 `footer-notice` | 본 서비스의 디자인… | 13px / w400 (lh 1.45) | 13px | `#666666` |
| | 개인정보 링크 `footer-link` | 개인정보처리방침 | 16px / w400 · 밑줄 | 16px | `#666666` |
| **팝업** | 팝업 출처 `drawer-source` | AI타임스 · 2026. 07. 01 | 12px / w400 | 동일 | `#888888` |
| | 팝업 제목 `drawer-title` | 앤트로픽, '페이블 5'… | 17px / w700 | 동일 | `#ffffff` |
| | 팝업 요약 `drawer-summary` | 미 상무부가 앤트로픽의… | 15px / w400 | 동일 | `#aaaaaa` |
| **아카이브** | 사이트 타이틀 `site-title` | 디자인 놀이터 | 18px / w300 | 15px | `#aaaaaa` |
| | 히어로 부제 `site-sub` | AI & Design 아카이브 | 46px / w700 | 32px | `#ffffff` |
| | 월 헤더 `month-label` | 2026년 7월 | 14px / w700 | 16px | `#e8e8f0` |
| | 날짜 항목 `item-date` | 2026. 07. 02 | 15px / w600 | 17px | `#e8e8f0` |
| | 저작권 `footer-copy` | © 2026 디자인놀이터… | 13px / w600 | 13px | `#888888` |
| | 개인정보 링크 `footer-link` | 개인정보처리방침 | 16px / w400 · 밑줄 | 16px | `#666666` |
| **개인정보** | 사이트 타이틀 `site-title` | 디자인 놀이터 | 18px / w300 | 18px | `#aaaaaa` |
| | 히어로 부제 `site-sub` | 개인정보처리방침 | 32px / w700 | 32px | `#ffffff` |
| | 시행일 `updated` | 시행일: 2026. 07. 02 | 12px | 12px | `#666666` |
| | 조항 제목 `section h2` | 1. 개요 | 16px / w700 | 16px | `#ffffff` |
| | 본문 `section p` | 디자인 놀이터(이하…)… | 14px / w400 | 14px | `#b0b0bc` |
| | 저작권 `footer-copy` | © 2026 디자인놀이터… | 13px / w600 | 13px | `#888888` |

**비고**
- 푸터 안내문 2줄("본 서비스…" / "제공되는…")은 하나의 `<p>` 안에서 `<br>`로 줄바꿈해 **한 덩어리**로 처리한다.

---

## 2. 버튼 (크기 · 내부 여백)

| 버튼 용어 (class) | 크기 (W×H) | 내부 패딩 | 반경 | 텍스트 | 배경 |
|---|---|---|---|---|---|
| 아카이브 버튼 `archive-cta` | 240 × 48px | `0 16px` | 24px | 16px / w500 `#191919` | `#c9ccd4` |
| 오픈채팅 버튼 `kakao-cta` | 240 × 48px | `0 16px` | 24px | 16px / w500 `#191919` | `#FEE500` |
| 메인으로 버튼 `nav-cta` | 240 × 48px | `0 16px` | 24px | 16px / w400 `#191919` | `#c9ccd4` |
| 원문 버튼 `drawer-cta` | 420 × 44px | `14px` (lh 1) | 10px | 16px / w400 `#ffffff` | `#1e1e2e` |
| 닫기 버튼 `drawer-close` | 420 × 44px | `14px` (lh 1) | 10px | 16px / w400 `#888888` | 없음(테두리) |

---

## 3. 아이콘 (크기 · 컬러)

| 아이콘 용어 (class) | 위치 | 크기 | 컬러(hex) | 형태 |
|---|---|---|---|---|
| 월 화살표 `month-chevron` | 아카이브 월 헤더 우측 | 15px, 세로 `scaleY(0.8)` | `#cccccc` | ▼ 펼침 / ▲ 접힘(180° 회전) |
| 이동 아이콘 `item-arrow` | 아카이브 날짜 항목 우측 | 16 × 16px | `#a9a9b8` | ↗ SVG (선 두께 2.4) |

---

## 4. 공통 토큰

- **배경**: `#0d0d12`
- **폰트 패밀리**: Cormorant Garamond 300 + Noto Sans KR 700 + Noto Serif KR 300
- **브랜드 컬러**: 카카오 옐로우 `#FEE500`, 버튼 그레이 `#c9ccd4`
- **팝업(drawer)**: 가로 480px 고정, 세로 80vh 고정, 요약 영역만 스크롤
- **body 하단 여백(푸터 아래)**: 72px / 라인→버튼 48px / 라인→저작권 28px

---

## 5. 팝업(드로어) — 구조화 요약

카드 클릭 시 뜨는 요약 팝업.

**규격**
- 데스크톱: 480px × **90vh** 중앙 모달 / 모바일: 100% × **90vh** 바텀시트
- 본문(`.drawer-body`) 영역만 스크롤 — 커스텀 스크롤바(폭 6px, thumb `#33333f`, 투명 트랙)
- 닫기 버튼 아래 여백: PC 21px / 모바일 28px + `env(safe-area-inset-bottom)`
- 영문 기사: KR/EN 토글로 6필드 전체 언어 전환. 값이 빈 필드는 자동 숨김

**구성 (위→아래)**
1. 팝업 출처 `drawer-source` — 12px `#888888`
2. 썸네일 `drawer-thumb`
3. 카테고리 `drawer-category` — 12px/w600 `#8a8aff`
4. 팝업 제목 `drawer-title` — 17px/w700 `#ffffff`
5. **한 줄 요약** / **디자이너 관점** / **실무 영향도** / **볼 포인트**(목록) / **추천**
   - 필드 라벨 `drawer-field-label` — 12px/w700 `#d0d0e0`
   - 필드 본문 `drawer-field-text` / `drawer-points li` — 14px `#a6a6b8`
6. 원문 버튼 `drawer-cta` / 닫기 버튼 `drawer-close` — 각 420×44, 16px/w400

**데이터 규칙 (카드 `data-*`)**
- 공통: `data-category`
- 6필드 기본: `data-summary`(한 줄 요약) · `data-designer` · `data-impact` · `data-points`(`|`구분) · `data-recommend`
- 영문 카드: 위 기본(영문) + `-kr` 접미사(한국어) 각각 + `data-title-kr`
