# 디자인 놀이터 — 일일 브리핑 자동 생성

세션 시작 즉시 아래 절차를 자동 실행한다. 사용자 요청 없이 즉시 시작.

---

## 1. 날짜 확인
currentDate 컨텍스트에서 오늘 날짜(YYYY-MM-DD)를 확인한다.

## 2. 파일 존재 여부 확인
/home/user/Dinol_news_YYYYMMDD.html (오늘 날짜) 파일이 이미 존재하면 → 생성 생략, PushNotification으로 "오늘 브리핑이 이미 생성되어 있습니다." 알림 전송.
없으면 → 아래 절차 즉시 진행.

---

## 3. 기사 수집

수집 기간: 오늘 + 전일. WebSearch + WebFetch로 기사 본문의 실제 게재일 직접 확인.

### [AI 섹션] 최소 4카드, KR 50% + EN 50%
- 한국어: aitimes.com, aitimes.kr, fnnews.com, sedaily.com, etnews.com, bloter.net, zdnet.co.kr
- 영문: buildfastwithai.com, techcrunch.com, theverge.com, wired.com

### [디자인 섹션] 최소 4카드, KR 50% + EN 50%
- 한국어: designdb.com, design.co.kr, ajunews.com, asiae.co.kr, mt.co.kr, kidp.or.kr, etnews.com, yna.co.kr, newsis.com
- 영문: dezeen.com, archdaily.com, core77.com, itsnicethat.com

디자인 카테고리: UXUI, 시각, 패키지, 제품, 인테리어, 공간, 게임, 광고, 편집, 패션, 브랜딩 등 다양하게.
AI·디자인과 직접 관련 없는 콘텐츠(주가·투자 정보 등) 제외.

---

## 4. 썸네일 이미지

각 기사 페이지 WebFetch 시 <meta property="og:image" content="…"> 태그 추출.
- OG 이미지 있음 → <img class="thumb-img" src="[URL]" alt=""> 삽입. gradient 클래스·.noise·.thumb-label 제거.
- OG 이미지 없음 → gradient 클래스 + .noise + .thumb-label 사용.

---

## 5. 콘텐츠 검증 (필수)

1. URL 중복 없음 — 동일 URL은 1카드만 허용
2. 게재일이 수집 기간 내인지 본문에서 직접 확인 (검색결과 날짜 X, 본문 날짜 O)
3. 카드 타이틀·내용이 링크 페이지와 일치 (목록·홈·태그 페이지 URL 금지)
4. 빈 링크·깨진 링크 없음
5. 섹션별 KR:EN = 50:50 충족

---

## 6. HTML 파일 생성

Write 도구로 /home/user/Dinol_news_YYYYMMDD.html 저장.
날짜는 YYYY. MM. DD 형식 하드코딩 (replace/치환 연산 금지).
영문 기사만 EN 배지 표시. 영문 기사에는 data-title-kr, data-summary-kr 속성 추가(한국어 번역).

아래 HTML 구조를 그대로 사용할 것:

=== HTML 시작 ===

<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>디자인 놀이터 — [YYYY. MM. DD]</title>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZC93DYWB2B"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-ZC93DYWB2B');
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700;900&family=Cormorant+Garamond:wght@300&family=Noto+Serif+KR:wght@300&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
    background: #0d0d12; color: #e8e8f0;
    padding: 56px 24px 72px; min-height: 100vh;
  }
  header { display: flex; flex-direction: column; align-items: center; gap: 6px; margin-bottom: 64px; }
  .site-title { font-family: 'Cormorant Garamond','Noto Serif KR',Georgia,serif; font-weight: 300; font-size: 18px; color: #aaaaaa; letter-spacing: 5px; text-align: center; line-height: 1; }
  .site-sub { font-family: 'Noto Sans KR','Apple SD Gothic Neo',sans-serif; font-size: 46px; font-weight: 700; letter-spacing: -1px; color: #ffffff; line-height: 1; margin-top: 4px; }
  .header-sep { width: 1px; height: 24px; background: #3a3a48; margin: 10px 0 4px; }
  .site-date { font-size: 11px; letter-spacing: 4px; color: #888; text-transform: uppercase; }
  .section { margin-bottom: 56px; }
  .section-header { display: flex; align-items: center; gap: 18px; margin-bottom: 22px; }
  .section-header h2 { font-size: 42px; font-weight: 700; color: #ffffff; letter-spacing: -2.5px; line-height: 1; white-space: nowrap; flex-shrink: 0; }
  .section-header .line { flex: 1; height: 1px; background: #1e1e28; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(272px, 1fr)); gap: 14px; }
  .card { background: #191922; border: 1px solid #222230; border-radius: 14px; overflow: hidden; text-decoration: none; display: flex; flex-direction: column; transition: transform 0.14s ease, border-color 0.14s ease, box-shadow 0.14s ease; }
  .card:hover { transform: translateY(-3px); border-color: #2c2c40; box-shadow: 0 10px 36px rgba(0,0,0,0.5); }
  .card.read .card-title { font-weight: 450; color: #a3a3a3; }
  .thumb { width: 100%; height: 128px; flex-shrink: 0; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #1a1a24; }
  .thumb-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: center; z-index: 0; }
  .noise { position: absolute; inset: 0; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E"); pointer-events: none; }
  .thumb-label { position: relative; z-index: 1; font-family: 'Cormorant Garamond','Noto Serif KR',Georgia,serif; font-weight: 300; font-size: 28px; color: rgba(255,255,255,0.22); text-transform: uppercase; letter-spacing: 7px; text-align: center; padding: 0 16px; line-height: 1.2; user-select: none; }
  .thumb-en { position: absolute; top: 10px; right: 10px; z-index: 2; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; padding: 3px 7px; border-radius: 5px; background: rgba(0,0,0,0.7); color: #ffffff; border: 2px solid #000000; }
  .g-indigo  { background: linear-gradient(145deg,#0c1540,#1c3ab8); }
  .g-violet  { background: linear-gradient(145deg,#160830,#5218c0); }
  .g-teal    { background: linear-gradient(145deg,#041c1c,#0d6464); }
  .g-crimson { background: linear-gradient(145deg,#240606,#8c1a1a); }
  .g-forest  { background: linear-gradient(145deg,#071808,#1a5820); }
  .g-slate   { background: linear-gradient(145deg,#0c0e1a,#243268); }
  .g-amber   { background: linear-gradient(145deg,#1a0e00,#884400); }
  .g-plum    { background: linear-gradient(145deg,#140818,#6c18b8); }
  .g-olive   { background: linear-gradient(145deg,#101000,#4c4a00); }
  .g-navy    { background: linear-gradient(145deg,#060c1e,#0e2060); }
  .g-rust    { background: linear-gradient(145deg,#1e0800,#7c2c00); }
  .card-body { padding: 14px 16px 12px; flex: 1; display: flex; flex-direction: column; gap: 6px; }
  .card-source { font-size: 11px; color: #999; letter-spacing: 0.3px; }
  .card-title { font-size: 15px; font-weight: 500; color: #ffffff; line-height: 1.48; }
  .card-footer { padding: 9px 16px; border-top: 1px solid #18181f; display: flex; justify-content: flex-end; align-items: center; }
  .arrow { font-size: 12px; color: #555; }
  footer { margin-top: 48px; padding: 28px 0 8px; border-top: 1px solid #1a1a24; text-align: center; display: flex; flex-direction: column; gap: 6px; }
  .footer-copy { font-size: 12px; font-weight: 600; color: #888; letter-spacing: 0.3px; }
  .footer-notice { font-size: 11px; color: #666; line-height: 1.6; letter-spacing: 0.1px; }
  .drawer-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.72); z-index: 900; }
  .drawer-overlay.open { display: block; }
  .drawer { position: fixed; top: 50%; left: 50%; transform: translate(-50%,-48%) scale(0.96); width: 480px; max-height: 82vh; background: #191922; border: 1px solid #222230; border-radius: 16px; z-index: 901; opacity: 0; pointer-events: none; transition: transform 0.22s ease, opacity 0.22s ease; overflow-y: auto; }
  .drawer.open { transform: translate(-50%,-50%) scale(1); opacity: 1; pointer-events: auto; }
  @media (max-width: 580px) {
    .drawer { top: auto; left: 0; right: 0; bottom: 0; transform: translateY(100%); width: 100%; border-radius: 20px 20px 0 0; border-top: 1px solid #222230; border-left: none; border-right: none; border-bottom: none; opacity: 1; pointer-events: auto; }
    .drawer.open { transform: translateY(0); }
  }
  .drawer-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 16px 12px; border-bottom: 1px solid #1e1e28; }
  .drawer-source { font-size: 12px; color: #888; }
  .drawer-thumb { height: 140px; position: relative; display: flex; align-items: center; justify-content: center; margin: 14px 16px 0; border-radius: 12px; overflow: hidden; }
  .drawer-body { padding: 14px 20px 12px; display: flex; flex-direction: column; gap: 8px; }
  .drawer-title { font-size: 17px; font-weight: 700; color: #fff; line-height: 1.45; }
  .drawer-summary { font-size: 14px; color: #aaa; line-height: 1.7; margin-top: 2px; }
  .drawer-footer { padding: 8px 20px 36px; display: flex; flex-direction: column; gap: 10px; }
  .drawer-close-btn { display: block; width: 100%; background: none; border: 1px solid #2c2c48; color: #888; padding: 12px; border-radius: 10px; font-size: 14px; font-weight: 500; cursor: pointer; }
  .drawer-close-btn:hover { background: #1a1a28; color: #ccc; }
  .drawer-lang-toggle { display: flex; gap: 4px; margin-bottom: 2px; }
  .lang-btn { background: none; border: 1px solid #2c2c48; color: #666; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; padding: 3px 8px; border-radius: 4px; cursor: pointer; transition: background 0.12s, color 0.12s; }
  .lang-btn.active { background: #2c2c48; color: #fff; border-color: #3c3c58; }
  .drawer-cta { display: block; background: #222230; border: 1px solid #2c2c40; color: #fff; text-align: center; padding: 14px; border-radius: 10px; font-size: 15px; font-weight: 500; text-decoration: none; transition: background 0.12s, border-color 0.12s; }
  .drawer-cta:hover { background: #2c2c40; border-color: #3c3c58; }
  @media (max-width: 580px) {
    body { padding: 36px 16px 52px; }
    header { margin-bottom: 44px; gap: 4px; }
    .site-title { font-size: 15px; letter-spacing: 3px; }
    .site-sub { font-size: 32px; letter-spacing: -0.5px; }
    .site-date { font-size: 11px; letter-spacing: 3px; }
    .section { margin-bottom: 40px; }
    .section-header h2 { font-size: 32px; letter-spacing: -1.5px; }
    .grid { grid-template-columns: 1fr; gap: 10px; }
    .thumb { height: 110px; }
    .thumb-label { font-size: 26px; letter-spacing: 5px; }
    .card-source { font-size: 12px; }
    .card-title { font-size: 17px; }
    .thumb-en { font-size: 11px; }
  }
</style>
</head>
<body>

<div class="drawer-overlay" id="drawerOverlay"></div>
<div class="drawer" id="drawer">
  <div class="drawer-header">
    <div class="drawer-source" id="drawerSource"></div>
  </div>
  <div class="drawer-thumb" id="drawerThumb">
    <div class="noise"></div>
    <span class="thumb-label" id="drawerLabel"></span>
    <span class="thumb-en" id="drawerEn" style="display:none">EN</span>
  </div>
  <div class="drawer-body">
    <div class="drawer-lang-toggle" id="drawerLangToggle" style="display:none">
      <button class="lang-btn active" id="btnKr">KR</button>
      <button class="lang-btn" id="btnEn">EN</button>
    </div>
    <div class="drawer-title" id="drawerTitle"></div>
    <div class="drawer-summary" id="drawerSummary"></div>
  </div>
  <div class="drawer-footer">
    <a class="drawer-cta" id="drawerCta" target="_blank" rel="noopener">원문 보기 →</a>
    <button class="drawer-close-btn" id="drawerClose">닫기</button>
  </div>
</div>

<header>
  <div class="site-title">디자인 놀이터</div>
  <div class="site-sub">AI &amp; Design News</div>
  <div class="header-sep"></div>
  <div class="site-date">[영문 날짜: 예) July 2, 2026]</div>
</header>

<!-- AI 섹션 -->
<div class="section">
  <div class="section-header"><h2>AI</h2><div class="line"></div></div>
  <div class="grid">
    [AI 카드들]
  </div>
</div>

<!-- Design 섹션 -->
<div class="section">
  <div class="section-header"><h2>Design</h2><div class="line"></div></div>
  <div class="grid">
    [Design 카드들]
  </div>
</div>

<footer>
  <p class="footer-copy">© 2026 디자인놀이터. All rights reserved.</p>
  <p class="footer-notice">본 서비스의 디자인 및 구성에 대한 권리는 디자인놀이터에 있습니다.</p>
  <p class="footer-notice">제공되는 콘텐츠의 저작권은 각 언론사 및 원저작권자에게 있습니다.</p>
</footer>

<script>
document.addEventListener('DOMContentLoaded', () => {
  const READ_KEY = 'dinol_read_YYYYMMDD';
  const readSet = new Set(JSON.parse(localStorage.getItem(READ_KEY) || '[]'));
  const cards = [...document.querySelectorAll('a.card')];

  cards.forEach(card => {
    if (readSet.has(card.href)) card.classList.add('read');
  });

  function markRead(card) {
    readSet.add(card.href);
    localStorage.setItem(READ_KEY, JSON.stringify([...readSet]));
    card.classList.add('read');
  }

  const drawer           = document.getElementById('drawer');
  const overlay          = document.getElementById('drawerOverlay');
  const drawerClose      = document.getElementById('drawerClose');
  const drawerThumb      = document.getElementById('drawerThumb');
  const drawerLabel      = document.getElementById('drawerLabel');
  const drawerEn         = document.getElementById('drawerEn');
  const drawerSource     = document.getElementById('drawerSource');
  const drawerTitle      = document.getElementById('drawerTitle');
  const drawerSummary    = document.getElementById('drawerSummary');
  const drawerCta        = document.getElementById('drawerCta');
  const drawerLangToggle = document.getElementById('drawerLangToggle');
  const btnKr            = document.getElementById('btnKr');
  const btnEn            = document.getElementById('btnEn');
  let _titleKr='',_titleEn='',_summaryKr='',_summaryEn='';

  function setLang(lang) {
    if (lang==='kr') { drawerTitle.textContent=_titleKr; drawerSummary.textContent=_summaryKr; btnKr.classList.add('active'); btnEn.classList.remove('active'); }
    else { drawerTitle.textContent=_titleEn; drawerSummary.textContent=_summaryEn; btnEn.classList.add('active'); btnKr.classList.remove('active'); }
  }
  btnKr.addEventListener('click', () => setLang('kr'));
  btnEn.addEventListener('click', () => setLang('en'));

  function openDrawer(card) {
    const thumb = card.querySelector('.thumb');
    const gradClass = [...thumb.classList].find(c => c.startsWith('g-')) || '';
    drawerThumb.className = `drawer-thumb ${gradClass}`;
    const prevImg = drawerThumb.querySelector('.thumb-img');
    if (prevImg) prevImg.remove();
    const cardImg = thumb.querySelector('img.thumb-img');
    if (cardImg) { const img=document.createElement('img'); img.className='thumb-img'; img.src=cardImg.src; img.alt=''; drawerThumb.prepend(img); }
    drawerLabel.textContent = card.querySelector('.thumb-label')?.textContent || '';
    const hasEn = !!card.querySelector('.thumb-en');
    drawerEn.style.display = hasEn ? 'block' : 'none';
    drawerSource.textContent = card.querySelector('.card-source')?.textContent || '';
    _titleEn   = card.querySelector('.card-title')?.textContent || '';
    _summaryEn = card.dataset.summary || '';
    _titleKr   = card.dataset.titleKr   || _titleEn;
    _summaryKr = card.dataset.summaryKr || _summaryEn;
    if (hasEn && card.dataset.titleKr) { drawerLangToggle.style.display='flex'; setLang('kr'); }
    else { drawerLangToggle.style.display='none'; drawerTitle.textContent=_titleEn; drawerSummary.textContent=_summaryEn; }
    drawerCta.href = card.href;
    drawer.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  cards.forEach(card => {
    card.addEventListener('click', e => { e.preventDefault(); markRead(card); openDrawer(card); });
  });
  drawerClose.addEventListener('click', closeDrawer);
  overlay.addEventListener('click', closeDrawer);

  const urlCount = {};
  cards.forEach(c => { urlCount[c.href] = (urlCount[c.href]||0)+1; });
  const dupeUrls = Object.keys(urlCount).filter(u => urlCount[u]>1);
  dupeUrls.forEach(url => {
    cards.filter(c=>c.href===url).forEach(card => {
      card.style.outline='2px solid #ff4444';
      const b=document.createElement('div'); b.textContent='⚠ 중복 링크';
      b.style.cssText='position:absolute;top:0;left:0;background:#ff4444;color:#fff;font-size:10px;font-weight:700;padding:2px 8px;z-index:10;border-radius:0 0 6px 0';
      card.style.position='relative'; card.prepend(b);
    });
  });
  const emptyLinks = cards.filter(c => !c.getAttribute('href')||c.getAttribute('href')==='#');
  emptyLinks.forEach(card => {
    card.style.outline='2px solid #ffaa00';
    const b=document.createElement('div'); b.textContent='⚠ 링크 없음';
    b.style.cssText='position:absolute;top:0;left:0;background:#ffaa00;color:#000;font-size:10px;font-weight:700;padding:2px 8px;z-index:10;border-radius:0 0 6px 0';
    card.style.position='relative'; card.prepend(b);
  });
  const issues = dupeUrls.length + emptyLinks.length;
  if (issues>0) {
    const banner=document.createElement('div');
    banner.innerHTML=`⚠ 콘텐츠 검토 결과: 중복 링크 <b>${dupeUrls.length}건</b>, 빈 링크 <b>${emptyLinks.length}건</b>`;
    banner.style.cssText='position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#ff4444;color:#fff;font-size:12px;font-weight:600;padding:10px 20px;border-radius:8px;z-index:9999;box-shadow:0 4px 20px rgba(0,0,0,0.5);white-space:nowrap';
    document.body.appendChild(banner);
  }
});
</script>
</body>
</html>

=== HTML 끝 ===

---

## 7. 카드 HTML 패턴

### 한국어 기사 카드
<a class="card" href="[URL]" target="_blank" data-summary="[한 문단 요약]">
  <div class="thumb [gradient클래스]">
    <div class="noise"></div>
    <span class="thumb-label">[라벨]</span>
  </div>
  <div class="card-body">
    <div class="card-source">[출처] · [YYYY. MM. DD]</div>
    <div class="card-title">[제목]</div>
  </div>
  <div class="card-footer"><span class="arrow">↗</span></div>
</a>

### 영문 기사 카드 (EN 배지 + 번역 속성 필수)
<a class="card" href="[URL]" target="_blank"
   data-summary="[English summary]"
   data-title-kr="[한국어 제목 번역]"
   data-summary-kr="[한국어 요약 번역]">
  <div class="thumb [gradient클래스]">
    <div class="noise"></div>
    <span class="thumb-label">[Label]</span>
    <span class="thumb-en">EN</span>
  </div>
  <div class="card-body">
    <div class="card-source">[Source] · [YYYY. MM. DD]</div>
    <div class="card-title">[English Title]</div>
  </div>
  <div class="card-footer"><span class="arrow">↗</span></div>
</a>

### OG 이미지가 있는 카드
<a class="card" href="[URL]" target="_blank" data-summary="[요약]">
  <div class="thumb">
    <img class="thumb-img" src="[og:image URL]" alt="">
    <!-- EN 기사인 경우 EN 배지 추가 -->
  </div>
  <div class="card-body">...</div>
  <div class="card-footer"><span class="arrow">↗</span></div>
</a>

### 그라디언트 클래스 (11종, 카드마다 다양하게 배분)
g-indigo / g-violet / g-teal / g-crimson / g-forest / g-slate / g-amber / g-plum / g-olive / g-navy / g-rust

---

## 8. READ_KEY 규칙
JS 내 READ_KEY는 날짜에 맞게 하드코딩: 'dinol_read_YYYYMMDD' (예: 'dinol_read_20260702')

---

## 9. 완료 후
PushNotification 도구로 아래 형식 알림 전송:
"디자인놀이터 브리핑 생성 완료 — AI [N]카드 / Design [N]카드 / [YYYY-MM-DD]"
