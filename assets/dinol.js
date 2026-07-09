/* ============================================================
   dinol.js — 디자인 놀이터 공용 로직 (팝업 열기/닫기 · KR/EN 토글 ·
   읽음상태 · 별점/포인트 렌더 · 콘텐츠 자동검토)
   ★ 전역 로직은 이 파일 하나만 수정하면 전 브리핑에 소급 반영됨.
   좋아요/방명록/App Check 는 dinol-firebase.js 에 별도(상호 독립).
   READ_KEY 날짜는 파일명(Dinol_news_YYYYMMDD)에서 자동 추출.
   추출 기준: Dinol_news_20260705.html (5개 브리핑 JS 로직 동일)
   ============================================================ */
/* ── 콘텐츠 검토 로직 ──────────────────────────────────────────
   페이지 로드 시 자동으로 아래 항목을 검사합니다.
   1. 중복 URL — 같은 링크가 2개 이상이면 해당 카드에 경고 표시
   2. 빈 링크 — href가 없거나 '#'인 카드 감지
   개발/검토용 표시이며 콘텐츠 영역 위에 요약 배너가 표시됩니다.
──────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const cards = [...document.querySelectorAll('a.card')];

  /* ── 맨 위로 플로팅 버튼 ──────────────────────────────────
     600px 이상 스크롤되면 .show로 페이드인, 클릭 시 상단으로 부드럽게 이동.
     노출 자체는 CSS @media(max-width:580px)에서만 display:flex → 모바일 전용.
  ──────────────────────────────────────────────────────────── */
  const toTop = document.getElementById('toTop');
  if (toTop) {
    const SHOW_AFTER = 600;
    const onScroll = () => {
      if (window.scrollY > SHOW_AFTER) toTop.classList.add('show');
      else toTop.classList.remove('show');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    toTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ── 읽음 상태 (localStorage) ──────────────────────────────
     카드를 한 번 열람(드로어 오픈)하면 해당 URL을 기록하고,
     card-title에 .read 클래스(font-weight 450, color #a3a3a3)를 부여합니다.
  ──────────────────────────────────────────────────────────── */
  const READ_KEY = (function () {
    const m = location.pathname.match(/Dinol_news_(\d{8})/);
    return 'dinol_read_' + (m ? m[1] : 'default');
  })();

  function getReadUrls() {
    try { return new Set(JSON.parse(localStorage.getItem(READ_KEY) || '[]')); }
    catch (e) { return new Set(); }
  }

  function markAsRead(card) {
    const read = getReadUrls();
    read.add(card.href);
    localStorage.setItem(READ_KEY, JSON.stringify([...read]));
    card.querySelector('.card-title')?.classList.add('read');
  }

  (function applyReadState() {
    const read = getReadUrls();
    cards.forEach(card => {
      if (read.has(card.href)) {
        card.querySelector('.card-title')?.classList.add('read');
      }
    });
  })();

  /* ── 드로어 (슬라이드업 요약 패널) ── */
  const drawer           = document.getElementById('drawer');
  const overlay          = document.getElementById('drawerOverlay');
  const drawerClose      = document.getElementById('drawerClose');
  const drawerThumb      = document.getElementById('drawerThumb');
  const drawerLabel      = document.getElementById('drawerLabel');
  const drawerEn         = document.getElementById('drawerEn');
  const drawerSource     = document.getElementById('drawerSource');
  const drawerTitle      = document.getElementById('drawerTitle');
  const drawerCategory   = document.getElementById('drawerCategory');
  const drawerOneline    = document.getElementById('drawerOneline');
  const drawerDesigner   = document.getElementById('drawerDesigner');
  const drawerImpact     = document.getElementById('drawerImpact');
  const drawerPoints     = document.getElementById('drawerPoints');
  const drawerRecommend  = document.getElementById('drawerRecommend');
  const drawerComment    = document.getElementById('drawerComment');
  const drawerCommentWrap= document.getElementById('drawerCommentWrap');
  const drawerCta        = document.getElementById('drawerCta');
  const drawerLangToggle = document.getElementById('drawerLangToggle');
  const btnKr            = document.getElementById('btnKr');
  const btnEn            = document.getElementById('btnEn');

  /* 6필드: 각 필드의 EN(기본)/KR 값 보관 */
  const F = {
    title:{}, oneline:{}, designer:{}, points:{}, recommend:{}, comment:{}
  };

  function renderPoints(str) {
    drawerPoints.innerHTML = '';
    (str || '').split('|').map(s => s.trim()).filter(Boolean).forEach(p => {
      const li = document.createElement('li'); li.textContent = p; drawerPoints.appendChild(li);
    });
  }

  function renderStars(score) {
    const n = Math.max(0, Math.min(5, parseInt(score, 10) || 0));
    const wrap = drawerImpact.closest(".drawer-field");
    if (!n) { if (wrap) wrap.style.display = "none"; return; }
    if (wrap) wrap.style.display = "flex";
    let html = "";
    for (let i = 1; i <= 5; i++) { html += "<span class='" + (i <= n ? "star-on" : "star-off") + "'>★</span>"; }
    drawerImpact.innerHTML = html;
  }

  function setField(el, val) {
    el.textContent = val || '';
    const wrap = el.closest('.drawer-field');
    if (wrap) wrap.style.display = (val && val.trim()) ? 'flex' : 'none';
  }

  function setLang(lang) {
    const k = (lang === 'kr') ? 'kr' : 'en';
    drawerTitle.textContent = F.title[k];
    setField(drawerOneline, F.oneline[k]);
    setField(drawerDesigner, F.designer[k]);
    renderPoints(F.points[k]);
    const pWrap = drawerPoints.closest('.drawer-field');
    if (pWrap) pWrap.style.display = drawerPoints.children.length ? 'flex' : 'none';
    setField(drawerRecommend, F.recommend[k]);
    const cmt = F.comment[k] || '';
    drawerComment.textContent = cmt;
    drawerCommentWrap.style.display = cmt.trim() ? 'flex' : 'none';
    btnKr.classList.toggle('active', k === 'kr');
    btnEn.classList.toggle('active', k === 'en');
  }

  btnKr.addEventListener('click', () => setLang('kr'));
  btnEn.addEventListener('click', () => setLang('en'));

  function openDrawer(card) {
    const thumb = card.querySelector('.thumb');
    const gradClass = [...thumb.classList].find(c => c.startsWith('g-')) || '';
    drawerThumb.className = `drawer-thumb ${gradClass}`;

    /* 기존 이미지 제거 후 카드 썸네일 이미지 복사 */
    const prevImg = drawerThumb.querySelector('.thumb-img');
    if (prevImg) prevImg.remove();
    const cardImg = thumb.querySelector('img.thumb-img');
    if (cardImg) {
      const img = document.createElement('img');
      img.className = 'thumb-img';
      img.src = cardImg.src;
      img.alt = '';
      drawerThumb.prepend(img);
    }

    drawerLabel.textContent = card.querySelector('.thumb-label')?.textContent || '';
    const hasEn = !!card.querySelector('.thumb-en');
    drawerEn.style.display = hasEn ? 'block' : 'none';
    drawerSource.textContent = card.querySelector('.card-source')?.textContent || '';

    const d = card.dataset;
    /* 카테고리(언어중립, 공유) */
    drawerCategory.textContent = d.category || '';
    drawerCategory.style.display = d.category ? 'block' : 'none';

    /* 기본값(EN 슬롯) = 카드 언어, -kr 슬롯 = 한국어(없으면 기본값 복제) */
    const baseTitle = card.querySelector('.card-title')?.textContent || '';
    F.title.en     = d.titleEn || baseTitle;
    F.oneline.en   = d.summary   || '';
    F.designer.en  = d.designer  || '';
    F.points.en    = d.points    || '';
    F.recommend.en = d.recommend || '';

    F.title.kr     = d.titleKr     || baseTitle;
    F.oneline.kr   = d.summaryKr   || F.oneline.en;
    F.designer.kr  = d.designerKr  || F.designer.en;
    F.points.kr    = d.pointsKr    || F.points.en;
    F.recommend.kr = d.recommendKr || F.recommend.en;

    /* 큐레이션 코멘트: EN 카드는 data-comment(영문)+data-comment-kr(한국어), 한글 카드는 data-comment 단일 */
    F.comment.en   = d.comment    || '';
    F.comment.kr   = d.commentKr  || F.comment.en;

    /* 영문 기사(-kr 번역 있음) → KR/EN 토글 / 한국어 기사 → KR만 활성 표시(EN 버튼 숨김, 토글 기능 없음) */
    if (hasEn && d.titleEn) {
      drawerLangToggle.style.display = 'flex';
      btnEn.style.display = '';
      setLang('kr');
    } else {
      drawerLangToggle.style.display = 'flex';
      btnEn.style.display = 'none';
      setLang('kr');
    }

    drawerCta.href = card.href;

    /* 실무 영향도 별점 (언어 무관) */
    renderStars(card.dataset.impactScore);

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
    card.addEventListener('click', e => {
      e.preventDefault();
      openDrawer(card);
      markAsRead(card);
    });
  });
  drawerClose.addEventListener('click', closeDrawer);
  overlay.addEventListener('click', closeDrawer);

  /* 섹션 아코디언 (AI·Design 접기/펼치기) */
  document.querySelectorAll('.section-header').forEach(header => {
    header.addEventListener('click', () => {
      header.closest('.section').classList.toggle('collapsed');
    });
  });

  /* 1. 중복 URL 검사 */
  const urlCount = {};
  cards.forEach(c => {
    const url = c.href;
    urlCount[url] = (urlCount[url] || 0) + 1;
  });
  const dupeUrls = Object.keys(urlCount).filter(u => urlCount[u] > 1);

  dupeUrls.forEach(url => {
    cards.filter(c => c.href === url).forEach(card => {
      card.style.outline = '2px solid #ff4444';
      const badge = document.createElement('div');
      badge.textContent = '⚠ 중복 링크';
      badge.style.cssText = [
        'position:absolute', 'top:0', 'left:0',
        'background:#ff4444', 'color:#fff',
        'font-size:10px', 'font-weight:700',
        'padding:2px 8px', 'z-index:10',
        'border-radius:0 0 6px 0'
      ].join(';');
      card.style.position = 'relative';
      card.prepend(badge);
    });
  });

  /* 2. 빈 링크 검사 */
  const emptyLinks = cards.filter(c => !c.getAttribute('href') || c.getAttribute('href') === '#');
  emptyLinks.forEach(card => {
    card.style.outline = '2px solid #ffaa00';
    const badge = document.createElement('div');
    badge.textContent = '⚠ 링크 없음';
    badge.style.cssText = [
      'position:absolute', 'top:0', 'left:0',
      'background:#ffaa00', 'color:#000',
      'font-size:10px', 'font-weight:700',
      'padding:2px 8px', 'z-index:10',
      'border-radius:0 0 6px 0'
    ].join(';');
    card.style.position = 'relative';
    card.prepend(badge);
  });

  /* 3. 요약 배너 */
  const issues = dupeUrls.length + emptyLinks.length;
  if (issues > 0) {
    const banner = document.createElement('div');
    banner.innerHTML = `⚠ 콘텐츠 검토 결과: 중복 링크 <b>${dupeUrls.length}건</b>, 빈 링크 <b>${emptyLinks.length}건</b> 발견 — 빨간/노란 테두리 카드를 확인하세요.`;
    banner.style.cssText = [
      'position:fixed', 'bottom:20px', 'left:50%',
      'transform:translateX(-50%)',
      'background:#ff4444', 'color:#fff',
      'font-size:12px', 'font-weight:600',
      'padding:10px 20px', 'border-radius:8px',
      'z-index:9999', 'box-shadow:0 4px 20px rgba(0,0,0,0.5)',
      'white-space:nowrap'
    ].join(';');
    document.body.appendChild(banner);
    console.warn('[디자인놀이터] 검토 오류:', { dupeUrls, emptyLinks: emptyLinks.map(c => c.querySelector('.card-title')?.textContent) });
  } else {
    console.log('[디자인놀이터] ✅ 콘텐츠 검토 통과 — 중복 링크 없음, 빈 링크 없음');
  }
});
