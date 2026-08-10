# 디자인 놀이터 — 크롤링/큐레이션 소스 목록 (news_sources.md)

> 매일 **AI 8카드 + 디자인 8카드** 선별을 위한 소스 레퍼런스.
> 최초 정리: 2026-07-06 · 최종 갱신: **2026-08-11**(PetaPixel 등록) · 관리 방식: 새 소스 추가/삭제 시 이 파일만 갱신.

## 읽는 법 (컬럼 설명)

- **지역**: `KR` 국내 · `EN` 영어권 · `EU` 유럽(비영어권 포함) · `JP` 일본 · `CN` 중국 · `글로벌`
- **수집**: `자동` = RSS/정적 크롤링이 쉬움(뉴스·매거진·블로그) · `수동` = 로그인·JS 렌더링·RSS 없음 → 자동 크롤링 부적합, 사람이 참고
- **RSS**: `○` 있음(추정) · `△` 부분/불명 · `✕` 없음(추정)
- ⭐ = 이번에 새로 추가한 소스

> ⚠️ **수집·RSS 컬럼은 카테고리 기반 추정치**입니다(사이트별 피드를 일일이 검증한 값이 아님). 실제 등록 전에 각 사이트의 `/rss`, `/feed`, `/rss.xml` 존재 여부를 확인하세요. 썸네일 라벨은 소스 원문 언어 기준(C안): KR 소스=한글, EN/JP 소스=영문.

---

## 선별·매체 분산 원칙 (2026-07-20)

> 선별 절차 상세는 `routine_instruction.md` §3-1 참조. 이 파일은 그 원칙이 전제하는 **크롤링 폭**을 담는다.

- **넓게 크롤링, 좁게 선정.** 검색 N건 = 채택 N건이 아니다. 여러 매체를 폭넓게 돌려 후보를 모은 뒤 디자인 관련도로 상위만 고른다.
- **매체 분산.** 섹션당 동일 매체 1건 권장(최대 2). **계열 매체는 같은 소스로 센다.** 예: 디자인플러스·헤이팝·행복이 가득한 집 = 디자인하우스 계열.
- **날짜 분산.** 같은 날짜 기사만 몰지 않는다.
- 소스 풀이 좁으면 분산이 불가능하므로 이 목록을 꾸준히 넓게 유지한다.

---

## 1. AI — 큐레이션 / 뉴스레터 ⭐ (최우선 등록 권장)

> 남이 이미 걸러준 소식이라 매일 선별 시간을 크게 줄여줌. The Batch·Import AI·Simon Willison은 논평이 실려 있어 **오리지널 코멘트(AdSense 부가가치)** 재료로 좋음.

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| ⭐ The Batch | EN | https://www.deeplearning.ai/the-batch/ | 자동 | ○ | 주간, Andrew Ng 개인 논평 포함 |
| ⭐ TLDR AI | EN | https://tldr.tech/ai | 자동 | ○ | 매일, 초압축 요약 |
| ⭐ The Rundown AI | EN | https://www.therundown.ai/ | 자동 | △ | 매일, 툴·활용 중심 |
| ⭐ Import AI | EN | https://importai.substack.com/ | 자동 | ○ | 주간 심층(정책·안전), Jack Clark |
| ⭐ Hugging Face Blog | EN | https://huggingface.co/blog | 자동 | ○ | 모델·오픈소스 릴리스 1차 소스 |
| ⭐ Simon Willison's Weblog | EN | https://simonwillison.net/ | 자동 | ○ | 실전 LLM 검증·논평 |

## 2. AI — 뉴스 / 연구 / 기업

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| TechCrunch | EN | https://techcrunch.com/ | 자동 | ○ | AI 스타트업·투자·신제품 |
| The Verge | EN | https://www.theverge.com/ | 자동 | ○ | AI 제품·디바이스·UX |
| Wired | EN | https://www.wired.com/ | 자동 | ○ | 기술사회·디지털 문화 |
| MIT Technology Review | EN | https://www.technologyreview.com/ | 자동 | ○ | 심층 분석 (뉴스레터 The Algorithm 별도 구독 가능) |
| VentureBeat AI | EN | https://venturebeat.com/category/ai/ | 자동 | ○ | 엔터프라이즈 AI·LLM·에이전트 |
| Artificial Intelligence News | EN | https://www.artificialintelligence-news.com/ | 자동 | ○ | ※ 기존 "AI News"와 동일 소스(통합) |
| Google DeepMind Blog | EN | https://deepmind.google/discover/blog/ | 자동 | ○ | 연구·모델·안전성 |
| OpenAI News | EN | https://openai.com/news/ | 자동 | ○ | 제품·모델·연구 |
| Anthropic News | EN | https://www.anthropic.com/news | 자동 | ○ | Claude·AI 안전 |
| Meta AI Blog | EN | https://ai.meta.com/blog/ | 자동 | ○ | Llama·멀티모달·오픈소스 |
| Microsoft AI Blog | EN | https://blogs.microsoft.com/ai/ | 자동 | ○ | Copilot·엔터프라이즈 AI |
| Google Research Blog | EN | https://research.google/blog/ | 자동 | ○ | ※ 기존 "Google AI Blog(ai.googleblog.com)" 대체 |
| MarkTechPost ⭐ | EN | https://www.marktechpost.com/ | 자동 | ○ | 모델 출시 기술 분석(벤치마크·가격·배포성). ⚠️ 유료 프로모션 병행 매체 — 제품 출시 기사는 **공식 블로그와 교차확인 후** 사용 |

## 3. 디자인 — 큐레이션 / 에디토리얼 ⭐

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| ⭐ Sidebar | EN | https://sidebar.io/ | 자동 | ○ | 매일 사람이 고른 디자인 링크 5개 |
| ⭐ Muzli | EN | https://muz.li/ | 수동 | △ | 디자인 영감·트렌드 아그리게이터 |
| ⭐ AIGA Eye on Design | EN | https://eyeondesign.aiga.org/ | 자동 | ○ | 그래픽·편집 에디토리얼(깊이 있는 관점) |
| ⭐ UX Collective | EN | https://uxdesign.cc/ | 자동 | ○ | UX 실무 아티클 대량(Medium) |
| ⭐ Codrops | EN | https://tympanus.net/codrops/ | 자동 | ○ | 웹 인터랙션·프론트엔드(기술×디자인) |
| ⭐ Fast Company (Co.Design) | EN | https://www.fastcompany.com/co-design | 자동 | ○ | 디자인 + 비즈니스 관점 |

## 4. 디자인 — UX / UI / 웹 / 도구

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| Nielsen Norman Group | EN | https://www.nngroup.com/articles/ | 자동 | ○ | UX 리서치·사용성(최우선) |
| Smashing Magazine | EN | https://www.smashingmagazine.com/ | 자동 | ○ | UX·웹·접근성·프론트엔드 |
| Awwwards | EN | https://www.awwwards.com/ | 수동 | △ | 웹 어워드 — JS 위주 |
| CSS Design Awards | EN | https://www.cssdesignawards.com/ | 수동 | ✕ | 웹 어워드 |
| Mobbin | EN | https://mobbin.com/ | 수동 | ✕ | 앱 UI 패턴 — 로그인 필요 |
| Page Flows | EN | https://pageflows.com/ | 수동 | ✕ | UX 플로우 — 유료/로그인 |
| UI Sources | EN | https://www.uisources.com/ | 수동 | ✕ | 앱 UX 플로우 — 로그인 |
| Godly | EN | https://godly.website/ | 수동 | △ | 웹 비주얼 레퍼런스 |
| Land-book | EN | https://land-book.com/ | 수동 | △ | 랜딩페이지·SaaS |
| Lapa Ninja | EN | https://www.lapa.ninja/ | 수동 | △ | 랜딩페이지 |
| Figma Blog | EN | https://www.figma.com/blog/ | 자동 | ○ | 디자인 시스템·AI 도구 |
| Adobe Blog | EN | https://blog.adobe.com/ | 자동 | ○ | Firefly·생성형 이미지/영상 |
| Webflow Blog | EN | https://webflow.com/blog | 자동 | ○ | 웹디자인·노코드 |
| Framer Blog | EN | https://www.framer.com/blog/ | 자동 | ○ | 인터랙티브 웹·프로토타이핑 |
| Canva Design School | EN | https://www.canva.com/learn/ | 자동 | ○ | 콘텐츠·SNS 디자인 교육 |

## 5. 디자인 — 브랜드 / 패키지 / 그래픽 / 타이포

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| Brand New | EN | https://www.underconsideration.com/brandnew/ | 자동 | ○ | 리브랜딩·로고 분석(최적) |
| BP&O | EN | https://bpando.org/ | 자동 | ○ | 브랜딩·패키지·아이덴티티 |
| The Brand Identity | EN | https://the-brandidentity.com/ | 자동 | ○ | 감도 높은 브랜드 사례 |
| World Brand Design Society | EN | https://worldbranddesign.com/ | 자동 | ○ | 브랜드·패키지·어워드 |
| The Dieline | EN | https://thedieline.com/ | 자동 | ○ | 패키지 디자인(최우선) |
| Packaging of the World | EN | https://packagingoftheworld.com/ | 자동 | ○ | 전 세계 패키지 사례 |
| Lovely Package | EN | https://lovelypackage.com/ | 자동 | △ | 패키지 보조 소스 |
| It's Nice That | EN | https://www.itsnicethat.com/ | 자동 | ○ | 그래픽·일러스트·크리에이티브 |
| Creative Boom | EN | https://www.creativeboom.com/ | 자동 | ○ | 업계 뉴스·작가 인터뷰 |
| Creative Bloq | EN | https://www.creativebloq.com/ | 자동 | ○ | 디자인 툴·트렌드·생성형 AI |
| The Inspiration Grid | EN | https://theinspirationgrid.com/ | 자동 | ○ | 비주얼·모션·제품·일러스트 |
| Fonts In Use | EN | https://fontsinuse.com/ | 자동 | ○ | 실제 서체 사용 사례 |
| Typewolf | EN | https://www.typewolf.com/ | 자동 | ○ | 웹 타이포·폰트 조합 |
| Eye Magazine | EN | https://www.eyemagazine.com/ | 자동 | △ | 편집·그래픽 비평 |
| Slanted | EN | https://www.slanted.de/ | 자동 | ○ | 타이포·편집·그래픽 |
| Print Magazine | EN | https://www.printmag.com/ | 자동 | ○ | 인쇄·편집·디자인 역사 |
| People of Print | EN | https://www.peopleofprint.com/ | 자동 | △ | 리소·실크스크린·후가공 |
| Behance | 글로벌 | https://www.behance.net/ | 수동 | △ | 포트폴리오 — 로그인/JS |
| Dribbble | 글로벌 | https://dribbble.com/ | 수동 | △ | UI·아이콘·일러스트 — 로그인/JS |
| Pinterest | 글로벌 | https://www.pinterest.com/ | 수동 | ✕ | 무드보드 — 로그인/API 필요 |

## 6. 디자인 — 공간 / 제품 / 건축

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| Dezeen | EN | https://www.dezeen.com/ | 자동 | ○ | 건축·인테리어·제품(최우선) |
| Designboom | EN | https://www.designboom.com/ | 자동 | ○ | 제품·건축·아트·기술 |
| Wallpaper* | EN | https://www.wallpaper.com/ | 자동 | ○ | 고감도 디자인·라이프스타일 |
| Design Milk | EN | https://design-milk.com/ | 자동 | ○ | 가구·조명·인테리어·제품 |
| Interior Design Magazine | EN | https://interiordesign.net/ | 자동 | ○ | 상업공간·오피스·호텔 |
| Frame | EN | https://frameweb.com/ | 자동 | △ | 브랜드 공간·리테일·전시 |
| ArchDaily | EN | https://www.archdaily.com/ | 자동 | ○ | 건축·공공공간·도시 |
| Core77 | EN | https://www.core77.com/ | 자동 | ○ | 제품·산업디자인·하드웨어 |
| Yanko Design | EN | https://www.yankodesign.com/ | 자동 | ○ | 콘셉트 제품·가젯 |
| Material District | EN | https://materialdistrict.com/ | 자동 | ○ | 신소재·친환경 소재 |

## 7. 패션 / 라이프스타일 / 마케팅 / 광고

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| Vogue Business | EN | https://www.voguebusiness.com/ | 자동 | ○ | 패션 산업·리테일·테크(일부 유료) |
| Business of Fashion | EN | https://www.businessoffashion.com/ | 자동 | △ | 패션 비즈니스(유료 많음) |
| Hypebeast | 글로벌 | https://hypebeast.com/ | 자동 | ○ | 패션·스니커즈·협업 |
| Highsnobiety | EN | https://www.highsnobiety.com/ | 자동 | ○ | 스트리트·브랜드 캠페인 |
| Adweek | EN | https://www.adweek.com/ | 자동 | ○ | 광고·브랜드 마케팅 |
| The Drum | EN | https://www.thedrum.com/ | 자동 | ○ | 글로벌 마케팅·캠페인 |
| Campaign | EN | https://www.campaignlive.com/ | 자동 | ○ | 광고 업계 뉴스 |
| Muse by Clio | EN | https://musebycl.io/ | 자동 | ○ | 캠페인·브랜드 필름 |

## 8. 모션 / 영상 / 게임

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| Motionographer | EN | https://motionographer.com/ | 자동 | ○ | 모션그래픽·브랜드 영상 |
| Stash Media | EN | https://www.stashmedia.tv/ | 자동 | △ | 영상 디자인·모션 |
| Art of the Title | EN | https://www.artofthetitle.com/ | 자동 | ○ | 타이틀 시퀀스 |
| Vimeo Staff Picks | 글로벌 | https://vimeo.com/channels/staffpicks | 수동 | △ | 영상·실험 영상 |
| Game UI Database | EN | https://www.gameuidatabase.com/ | 수동 | ✕ | 게임 UI·HUD — JS |
| Interface In Game | EN | https://interfaceingame.com/ | 수동 | ✕ | 게임 인터페이스 스크린샷 |
| ArtStation | 글로벌 | https://www.artstation.com/ | 수동 | △ | 게임 아트·3D — 로그인/JS |
| 80 Level | EN | https://80.lv/ | 자동 | ○ | 게임 제작·3D·테크아트 |
| PetaPixel | EN | https://petapixel.com/ | 자동 | ○ | 사진·영상·이미징 기술 전문(2009년 창간). 어도비·캔바 등 크리에이티브 툴 뉴스도 다룸 |

## 9. 유럽 (EU) ⭐

> 영어권 매체만으로는 후보 풀이 좁아 EN 소스 고갈이 반복됐다(2026-07-26~08-06, 8일 연속). 유럽·일본·중국을 별도 축으로 둔다.
> **표기 규칙:** 이 섹션 매체도 §3-1 구성 균형에서는 **해외**로 계산한다.

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| ⭐ Slanted | EU (DE) | https://www.slanted.de/ | 자동 | ○ | 타이포·편집·그래픽(§5에도 등재, 유럽 축으로 재분류) |
| ⭐ Frame | EU (NL) | https://frameweb.com/ | 자동 | △ | 브랜드 공간·리테일·전시 |
| ⭐ Eye Magazine | EU (UK) | https://www.eyemagazine.com/ | 자동 | △ | 편집·그래픽 비평 |
| ⭐ Design Week | EU (UK) | https://www.designweek.co.uk/ | 자동 | ○ | 영국 디자인 업계 뉴스·리브랜딩 |
| ⭐ It's Nice That | EU (UK) | https://www.itsnicethat.com/ | 자동 | ○ | §5 중복 등재 — 유럽 축 계산 시 참고 |
| ⭐ Creative Boom | EU (UK) | https://www.creativeboom.com/ | 자동 | ○ | §5 중복 등재 — 유럽 축 계산 시 참고 |
| ⭐ Dezeen | EU (UK) | https://www.dezeen.com/ | 자동 | ○ | §6 중복 등재 — 유럽 축 계산 시 참고 |
| ⭐ Designboom | EU (IT) | https://www.designboom.com/ | 자동 | ○ | §6 중복 등재 — 유럽 축 계산 시 참고 |

## 10. 중국 (CN) ⭐

> 중국 매체는 대부분 로그인·JS 렌더링이라 **자동 크롤링 부적합**이다. 루틴이 WebSearch 전용이므로, URL 직접 접근 대신 **매체명을 검색어에 넣어** 후보를 찾는 방식으로 쓴다.

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| ⭐ 站酷 ZCOOL | CN | https://www.zcool.com.cn/ | 수동 | ✕ | 중국 최대 디자이너 커뮤니티(2006년 설립, 회원 1,500만+). 로그인·JS |
| ⭐ Design360° | CN | **미확정 — URL 확인 필요** | 수동 | △ | 광저우 기반 디자인 매거진. 검색어 `Design360 中国设计`로 사용 |
| ⭐ TOPYS | CN | **미확정 — URL 확인 필요** | 수동 | △ | 크리에이티브·광고 큐레이션. 검색어 `TOPYS 创意`로 사용 |

> ⚠️ `미확정` 표시된 2건은 URL을 실제로 확인하기 전까지 **자동 파이프라인에 등록하지 않는다.** 검색어로만 쓴다.

## 11. 일본 (JP)

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| Spoon & Tamago | JP | https://www.spoon-tamago.com/ | 자동 | ○ | 일본 디자인·공예·문화 |
| Tokyo Art Beat | JP | https://www.tokyoartbeat.com/ | 자동 | ○ | 일본 전시·아트 |
| AXIS Magazine | JP | https://www.axismag.jp/ | 자동 | ○ | 일본 제품·산업디자인 |
| Pen Online | JP | https://www.pen-online.jp/ | 자동 | ○ | 일본 라이프스타일·디자인 |
| ⭐ JDN (Japan Design Net) | JP | https://www.japandesign.ne.jp/ | 자동 | ○ | 일본 디자인 업계 뉴스·공모·인터뷰 |
| ⭐ Casa BRUTUS | JP | https://casabrutus.com/ | 자동 | ○ | 건축·인테리어·프로덕트 |

## 12. 국내 (KR) — 디자인 / 산업 / 공모 / 문화

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| 디자인플러스 | KR | https://design.co.kr/ | 자동 | △ | ※ "월간 디자인"과 동일 소스(통합) · 디자인하우스 계열 |
| ⭐ 디자인 나침반 | KR | https://designcompass.org/ | 자동 | ○ | 브랜드·BX·프로덕트 분석(독립 매체) |
| ⭐ 헤이팝 | KR | https://heypop.kr/ | 자동 | △ | 팝업·공간·브랜드 이슈 · 디자인하우스 계열 |
| 디자인DB | KR | https://www.designdb.com/ | 자동 | △ | 공모전·정책·산업자료 |
| 디자인정글 | KR | https://www.jungle.co.kr/ | 자동 | △ | 전시·공모·행사 |
| 매거진 B | KR | https://magazine-b.com/ | 수동 | ✕ | 브랜드 심층(콘텐츠 적음) |
| 아이즈매거진 | KR | https://eyesmag.com/ | 자동 | △ | 패션·브랜드·문화 |
| Hypebeast KR | KR | https://hypebeast.kr/ | 자동 | ○ | 스트리트·협업·컬처 |
| 무신사 매거진 | KR | https://www.musinsa.com/mz/magazine | 수동 | ✕ | 패션·룩북 — 커머스 JS |
| 우먼센스/리빙센스 | KR | https://www.smlounge.co.kr/ | 자동 | △ | 인테리어·리빙 |
| 행복이 가득한 집 | KR | https://happy.designhouse.co.kr/ | 자동 | △ | 공간·공예 감도 |
| 서울디자인재단 | KR | https://www.seouldesign.or.kr/ | 자동 | △ | 공공디자인·전시·정책 |
| DDP | KR | https://ddp.or.kr/ | 자동 | △ | 전시·페스티벌·팝업 |
| KCDF | KR | https://www.kcdf.or.kr/ | 자동 | △ | 공예·문화상품·굿즈 |
| 한국콘텐츠진흥원 | KR | https://www.kocca.kr/ | 자동 | △ | 콘텐츠·게임·캐릭터·IP |
| 게임메카 | KR | https://www.gamemeca.com/ | 자동 | ○ | 게임 출시·산업·UI |
| 인벤 | KR | https://www.inven.co.kr/ | 자동 | ○ | 게임 서비스·UI·유저 반응 |
| 네이버 디자인프레스 | KR | https://post.naver.com/designpress2016 | 수동 | ✕ | 네이버 포스트 — 정식 RSS 없음 |

## 13. 국내 (KR) — AI / IT / 테크

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| 플래텀 | KR | https://platum.kr/ | 자동 | ○ | 스타트업·AI·투자 |
| 벤처스퀘어 | KR | https://www.venturesquare.net/ | 자동 | ○ | 스타트업·AI·서비스 |
| 테크42 | KR | https://www.tech42.co.kr/ | 자동 | ○ | AI·로봇·빅테크 |
| AI타임스 | KR | https://www.aitimes.com/ | 자동 | ○ | 국내외 AI 뉴스(최우선) |
| 지디넷코리아 | KR | https://zdnet.co.kr/ | 자동 | ○ | IT·AI·플랫폼·디바이스 |
| 블로터 | KR | https://www.bloter.net/ | 자동 | ○ | 테크 기업·플랫폼·AI |
| IT조선 | KR | https://it.chosun.com/ | 자동 | ○ | AI·반도체·로봇 |
| 바이라인네트워크 | KR | https://byline.network/ | 자동 | ○ | AI·SaaS·커머스 분석 |
| 디지털데일리 | KR | https://www.ddaily.co.kr/ | 자동 | ○ | AI 인프라·반도체·통신 |
| 전자신문 | KR | https://www.etnews.com/ | 자동 | ○ | AI·반도체·산업기술 |
| 매일경제 | KR | https://www.mk.co.kr/ | 자동 | ○ | AI 산업·투자·기업 전략 |
| 조선비즈 IT/사이언스 | KR | https://biz.chosun.com/it-science/ | 자동 | ○ | AI 기업·테크 산업 |
| 연합뉴스 IT/과학 | KR | https://www.yna.co.kr/industry/science-technology | 자동 | ○ | 공신력 있는 AI·정책 |

## 14. 국내 (KR) — 개발 / 프로덕트 실무 ⭐

| 사이트 | 지역 | URL | 수집 | RSS | 비고 |
|---|---|---|---|---|---|
| ⭐ GeekNews | KR | https://news.hada.io/ | 자동 | ○ | 링크 + 한국어 요약 커뮤니티(카드화 쉬움) |
| ⭐ 요즘IT | KR | https://yozm.wishket.com/magazine/ | 자동 | ○ | 개발·디자인·기획 실무 매거진(매일) |
| ⭐ 토스 tech | KR | https://toss.tech/ | 자동 | ○ | 국내 최고 수준 프로덕트 디자인·개발 |
| ⭐ 우아한형제들 기술블로그 | KR | https://techblog.woowahan.com/ | 자동 | ○ | 대규모 서비스 개발·디자인 |
| ⭐ 디에디트 | KR | https://the-edit.co.kr/ | 자동 | ○ | 제품·라이프스타일 리뷰(감도) |
| ⭐ 캐릿 | KR | https://www.careet.net/ | 자동 | △ | Z세대·트렌드·마케팅 |
| ⭐ 잡코리아 커리어스토리 | KR | https://www.jobkorea.co.kr/goodjob/tip | 자동 | △ | 실무자 인터뷰 시리즈(프로덕트 디자이너·마케터). ⚠️ 채용 플랫폼 자체 콘텐츠 — 디자인 전문 매체가 아니고 채용 홍보성 글이 섞임. **인터뷰형만 사용**하고 연봉·취업통계·이벤트 글은 카드로 쓰지 않는다 |

---

## 우선 등록 순서 (이 프로젝트 기준)

> "자동 크롤링이 되고, 이미 큐레이션돼 있으며, 매일/주간 갱신"인 소스부터. 논평이 실린 소스는 오리지널 코멘트 재료로도 씀.

**AI (매일 8카드용)**
1. TLDR AI — 매일 초압축, 그날 핵심
2. The Batch — 주간, Andrew Ng 논평
3. TechCrunch — 스타트업·투자·신제품
4. The Verge — 제품·UX 관점
5. Import AI / Simon Willison — 심층·논평(오리지널 코멘트용)
6. AI타임스 (KR) — 국내 AI 이슈

**디자인 (매일 8카드용)**
1. Sidebar — 매일 큐레이션 링크
2. Dezeen — 공간·제품·건축 안정적
3. It's Nice That / AIGA Eye on Design — 그래픽·에디토리얼
4. Brand New — 브랜딩·리브랜딩
5. The Dieline — 패키지
6. NN/g / Smashing — UX/UI
7. 요즘IT · GeekNews (KR) — 국내 실무·기술

---

## 제외 매체 (카드 출처로 쓰지 않음)

> 루틴이 §3 소스 목록 밖에서 뽑아온 매체를 검증한 결과다. **여기 있는 매체는 카드 출처로 쓰지 않는다.** 검색 결과에 떠도 후보에서 제외한다.

| 매체 | 판정일 | 사유 | 예외 |
|---|---|---|---|
| ROOT IN NEWS (rootinnews.com) | 2026-08-08 | ㈜씨서노 · 등록 2026-04-17로 창간 4개월. 기자 서명 없이 매체명(`webmaster@`)으로 발행. 사진·내용이 주최사(메쎄이상) 제공 보도자료이고 본문이 티켓 예매 안내로 끝남. 섹션 분류가 `MICE > 브랜드 리포트`로 디자인 전문 매체가 아님 | 국내 디자인 행사·전시 **라인업 사실 확인용 참고**는 가능. 단 카드 출처로는 쓰지 않고, 1차 소스(주최사 공식·행사 홈페이지)를 찾아 대체한다 |

**판정 기준** — ① 기자 서명 유무 ② 보도자료 전재 여부(사진 출처가 주최사·기업 제공인지) ③ 1차 소스를 인용·링크하는지 ④ 해당 분야 전문 매체인지. 새 매체가 카드에 등장하면 이 4가지를 확인하고 등록 또는 제외로 분류한다.

---

## 유지보수 메모

- **중복 정리 완료**: `AI News`↔`Artificial Intelligence News`(동일), `월간 디자인`↔`디자인플러스`(동일), `Dezeen Japan`↔`Dezeen`(동일) → 각각 1개로 통합.
- **URL 갱신 확인 필요**: `Google AI Blog(ai.googleblog.com)` → `research.google/blog`로 대체 반영함(구글 블로그 통합).
- **수동 분류 소스**는 자동 파이프라인에서 제외하고 별도 "수동 참고" 리스트로 운영 권장(포트폴리오·어워드·로그인·무RSS).
- 시작 규모 가이드: 국내 15~20 / 해외 30~40에서 시작 → 카드는 하루 AI 8 + 디자인 8만 선별.
- **2026-08-06 갱신**: EN 소스 고갈이 07-26~08-06 8일 연속 발생(요청 주제에 맞는 기간 내 1차 출처 미확보). 원인은 이 파일이 아니라 **`routine_instruction.md` §3의 소스 목록이 이 파일의 일부만 반영**하고 있던 것 → 루틴 §3을 이 파일 기준으로 확장했다. 두 파일이 다시 어긋나지 않도록, 이 파일을 고치면 루틴 §3도 같은 변경에서 함께 고친다.
- **중국(CN)·유럽(EU) 섹션 신설**: 루틴은 WebSearch 전용이라 URL 접근이 불가한 매체도 **매체명 검색어**로는 쓸 수 있다. 수집 컬럼이 `수동`이어도 루틴 후보 풀에는 포함한다.
- **미확정 URL 2건**(Design360°·TOPYS): 확인 전까지 자동 등록 금지.
- **2026-08-08 갱신**: 8/8 브리핑에서 루틴이 §3 목록 밖 매체 2곳(MarkTechPost·ROOT IN NEWS)을 뽑아왔다. 검증 결과 MarkTechPost는 자체 기술 분석이 있어 등록, ROOT IN NEWS는 주최사 보도자료 전재라 제외했다. 이를 계기로 **제외 매체 섹션**을 신설했다. 루틴 §3에도 MarkTechPost를 같은 변경에서 반영했다.
- **2026-08-10 갱신**: 8/10 브리핑에서 `source_rules.json` 미등록 매체 2건이 게이트 [1]에 걸렸다. `VentureBeat`는 이 파일에 `VentureBeat AI`로 **이미 등록**돼 있었고 표기만 달랐다(신규 아님). `잡코리아 커리어스토리`는 미등록이라 4항목 판정 후 **조건부 등록**했다 — ①기자 서명 △ ②보도자료 전재 아님 ③인터뷰이가 1차 소스 ④디자인 전문 매체 아님. ④만 미달이라 ROOT IN NEWS(4항목 전부 미달)와 달리 제외하지 않고 §14에 제약 조건과 함께 넣었다. 루틴 §3에도 같은 변경에서 반영했다.
- **2026-08-11 갱신**: 8/11 브리핑에서 `PetaPixel`이 게이트 [1] UNKNOWN으로 걸렸다. 4항목 **전부 통과**라 제약 없이 등록했다 — ①편집장 Jaron Schneider 등 서명 체계 ②뉴스 에디터·라이터를 둔 자체 취재 ③심층 분석·법/정책까지 1차 취재 ④사진·영상·이미징 독립 전문 매체(2009년 창간). 사진 축이 이 문서에 없어 **§8(모션/영상/게임)** 에 넣었고, 루틴 §3은 실제로 잡힌 맥락(어도비·챗GPT·캔바 기사)에 맞춰 **AI×디자인 축**에 반영했다. 두 문서의 축이 일대일 대응하지 않는 점은 의도된 선택이다.
