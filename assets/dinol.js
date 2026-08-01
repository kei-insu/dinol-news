/* ============================================================
   dinol.js — 디자인 놀이터 공용 로직 (읽음상태 · 섹션 접기 ·
   to-top · 콘텐츠 자동검토)
   ★ 전역 로직은 이 파일 하나만 수정하면 전 브리핑에 소급 반영됨.
   좋아요/방명록/App Check 는 dinol-firebase.js 에 별도(상호 독립).
   READ_KEY 날짜는 파일명(Dinol_news_YYYYMMDD)에서 자동 추출.
   ── 4-2 구조전환: 카드 클릭 → 상세 페이지 이동(앵커 기본 탐색).
      드로어/KR·EN 토글/별점·포인트 렌더는 상세 페이지로 이관되어 제거됨.
   ============================================================ */
/* ── 콘텐츠 검토 로직 ──────────────────────────────────────────
   페이지 로드 시 자동으로 아래 항목을 검사합니다.
   1. 중복 URL — 같은 링크가 2개 이상이면 해당 카드에 경고 표시
   2. 빈 링크 — href가 없거나 '#'인 카드 감지
   개발/검토용 표시이며 콘텐츠 영역 위에 요약 배너가 표시됩니다.
   ※ 4-2 이후 카드 href 는 원문이 아니라 상세 페이지({contentId}.html)다.
     contentId 는 카드마다 유일하므로 이 검사는 사실상 항상 통과한다.
     "같은 원문을 두 번 실은 중복"을 잡던 원래 목적은 더는 수행하지 못한다.
──────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // 5-A-1 구조전환: 카드 최상위는 <article class="card">(data-content-id 소유),
  // 이동 링크는 내부 <a class="card-link">(href 소유). 읽음상태는 article 기준,
  // href 기반 검사는 linkOf() 로 내부 링크에서 읽는다.
  const cards = [...document.querySelectorAll('.card')];
  const linkOf = card => card.querySelector('.card-link');

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
     카드를 한 번 클릭(상세 페이지로 이동)하면 해당 contentId를 기록하고,
     card-title에 .read 클래스(font-weight 450, color #a3a3a3)를 부여합니다.
     ── 4-2: 기존 키는 card.href(원문 URL)였으나 href가 상세 URL로 바뀌었으므로
        contentId로 전환한다. 기존 href 기반 기록은 버려진다(localStorage라 영향 작음).
  ──────────────────────────────────────────────────────────── */
  const READ_KEY = (function () {
    const m = location.pathname.match(/Dinol_news_(\d{8})/);
    return 'dinol_read_' + (m ? m[1] : 'default');
  })();

  // 이제 URL 이 아니라 contentId 집합을 반환한다(개명).
  function getReadIds() {
    try { return new Set(JSON.parse(localStorage.getItem(READ_KEY) || '[]')); }
    catch (e) { return new Set(); }
  }

  function markAsRead(card) {
    const cid = card.dataset.contentId;
    if (!cid) return;
    const read = getReadIds();
    read.add(cid);
    localStorage.setItem(READ_KEY, JSON.stringify([...read]));
    card.querySelector('.card-title')?.classList.add('read');
  }

  (function applyReadState() {
    const read = getReadIds();
    cards.forEach(card => {
      if (read.has(card.dataset.contentId)) {
        card.querySelector('.card-title')?.classList.add('read');
      }
    });
  })();

  /* ── 카드 클릭 → 상세 페이지 이동 + 읽음 기록 ──────────────
     preventDefault 가 없으므로 앵커 기본 탐색은 전부 유지된다.
       좌클릭 → 이동 / Ctrl+클릭 → 새 탭 / 중클릭 → 새 탭 / Tab+Enter → 이동
     다만 읽음 기록은 click 이벤트 기준이라
       ★중클릭·우클릭 후 새 탭 열기는 읽음으로 기록되지 않는다★ (의도된 동작)
     중클릭 순간 읽음을 찍으면 실제로 보지 않아도 읽음이 되기 때문이다.
     중클릭까지 잡으려면 상세 페이지 진입 시 기록하는 방식이 정확하고,
     그건 5단계에서 통합한다. (auxclick 을 지금 추가하지 않는다)
  ──────────────────────────────────────────────────────────── */
  cards.forEach(card => {
    card.addEventListener('click', () => {
      markAsRead(card);
    });
  });

  /* 섹션 아코디언 (AI·Design 접기/펼치기) */
  document.querySelectorAll('.section-header').forEach(header => {
    header.addEventListener('click', () => {
      header.closest('.section').classList.toggle('collapsed');
    });
  });

  /* 1. 중복 URL 검사 (4-2: href가 상세 페이지라 contentId 유일 → 실질 무해) */
  const urlCount = {};
  cards.forEach(c => {
    const url = linkOf(c)?.href;
    urlCount[url] = (urlCount[url] || 0) + 1;
  });
  const dupeUrls = Object.keys(urlCount).filter(u => urlCount[u] > 1);

  dupeUrls.forEach(url => {
    cards.filter(c => linkOf(c)?.href === url).forEach(card => {
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
  const emptyLinks = cards.filter(c => {
    const h = linkOf(c)?.getAttribute('href');
    return !h || h === '#';
  });
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
