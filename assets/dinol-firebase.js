// ─────────────────────────────────────────────────────────────
// 디자인 놀이터 — Firebase 연동 (디놀 톡톡 방명록 + 댓글 + 좋아요)
// 공통 모듈: 모든 브리핑에서 이 파일 하나만 불러온다.
// 댓글: guestbook/{글ID}/comments/{댓글ID} 서브컬렉션. 비번은 방명록과 동일(SHA-256, 4자리).
// ─────────────────────────────────────────────────────────────
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getFirestore, collection, addDoc, getDocs, getDoc, doc,
  updateDoc, deleteDoc, query, orderBy, serverTimestamp,
  runTransaction, setDoc, increment
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import {
  initializeAppCheck, ReCaptchaV3Provider
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app-check.js";

const firebaseConfig = {
  apiKey: "AIzaSyD84D4xoyD74W263XBiy7uRfNX-Oree5Xo",
  authDomain: "dinol-news.firebaseapp.com",
  projectId: "dinol-news",
  storageBucket: "dinol-news.firebasestorage.app",
  messagingSenderId: "212617826818",
  appId: "1:212617826818:web:e5ab06e9bad469c7e00d1b"
};

// reCAPTCHA v3 사이트 키 (공개용)
const RECAPTCHA_SITE_KEY = "6LcW4kQtAAAAAJ5-eZc-SpxCrQ37bfTaYHs7v_yd";

// 관리자 마스터 비밀번호(스팸 정리용) — 아무 글/댓글이나 이 값으로 수정/삭제 가능
const ADMIN_PW = "481516";

const app = initializeApp(firebaseConfig);

// App Check (reCAPTCHA v3) — 봇/스팸 차단. 사용자에겐 보이지 않음.
try {
  initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider(RECAPTCHA_SITE_KEY),
    isTokenAutoRefreshEnabled: true
  });
} catch (e) { /* App Check 초기화 실패 시에도 앱은 계속 동작 */ }

const db = getFirestore(app);

// ── 공통 유틸 ──────────────────────────────────────────────
async function sha256(str) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}
function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
function likeKey(url) {
  // 기사 URL → Firestore 문서 ID로 안전한 키
  return url.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 300) || "x";
}
function isMobile() { return window.matchMedia("(max-width: 580px)").matches; }

// ═════════════════════════════════════════════════════════════
// 1) 좋아요 (기사 URL 기준 카운트)
// ═════════════════════════════════════════════════════════════
(function initLikes() {
  const cards = [...document.querySelectorAll("a.card")];
  if (!cards.length) return;

  // 토스트
  const toast = document.createElement("div");
  toast.className = "gb-toast";
  document.body.appendChild(toast);
  let tTimer;
  function showToast(msg) {
    toast.textContent = msg; toast.classList.add("show");
    clearTimeout(tTimer); tTimer = setTimeout(() => toast.classList.remove("show"), 1800);
  }

  const state = {}; // href -> {count, liked}
  function likedLocally(href) { return localStorage.getItem("dinol_liked_" + likeKey(href)) === "1"; }

  function paint(likeEl, countEl, st) {
    if (!likeEl) return;
    likeEl.classList.toggle("liked", st.liked);
    countEl.textContent = st.count > 0 ? st.count : "";
  }
  function renderCard(card) {
    paint(card.querySelector(".act-like"), card.querySelector(".act-count"), state[card.href]);
  }
  function doShare(href, title) {
    if (navigator.share) navigator.share({ title, url: href }).catch(() => {});
    else if (navigator.clipboard) navigator.clipboard.writeText(href).then(() => showToast("링크가 복사되었어요")).catch(() => showToast("링크: " + href));
    else showToast("링크: " + href);
  }

  // 드로어(팝업) 액션
  let currentCard = null;
  const dLike = document.getElementById("drawerLike"),
        dShare = document.getElementById("drawerShare"),
        dCount = document.getElementById("drawerLikeCount");
  function renderDrawer() { if (currentCard && dLike) paint(dLike, dCount, state[currentCard.href]); }

  async function toggleLike(card) {
    const st = state[card.href];
    const key = likeKey(card.href);
    const ref = doc(db, "likes", key);
    const willLike = !st.liked;
    // 낙관적 UI
    st.liked = willLike; st.count = Math.max(0, st.count + (willLike ? 1 : -1));
    renderCard(card); if (currentCard && currentCard.href === card.href) renderDrawer();
    try {
      await runTransaction(db, async (tx) => {
        const snap = await tx.get(ref);
        const cur = snap.exists() ? (snap.data().count || 0) : 0;
        const next = Math.max(0, cur + (willLike ? 1 : -1));
        tx.set(ref, { count: next, url: card.href }, { merge: true });
      });
      if (willLike) localStorage.setItem("dinol_liked_" + key, "1");
      else localStorage.removeItem("dinol_liked_" + key);
    } catch (e) {
      // 실패 시 롤백
      st.liked = !willLike; st.count = Math.max(0, st.count + (willLike ? -1 : 1));
      renderCard(card); renderDrawer();
      showToast("잠시 후 다시 시도해주세요");
    }
  }

  // 초기 카운트 로드 + 이벤트 바인딩
  cards.forEach(async (card) => {
    state[card.href] = { count: 0, liked: likedLocally(card.href) };
    const like = card.querySelector(".act-like"), share = card.querySelector(".act-share");
    if (like && share) {
      renderCard(card);
      like.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); toggleLike(card); });
      share.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); doShare(card.href, (card.querySelector(".card-title") || {}).textContent || "디자인 놀이터"); });
    }
    card.addEventListener("click", () => { currentCard = card; renderDrawer(); });
    // Firestore에서 카운트 읽기
    try {
      const snap = await getDoc(doc(db, "likes", likeKey(card.href)));
      if (snap.exists()) { state[card.href].count = snap.data().count || 0; renderCard(card); if (currentCard === card) renderDrawer(); }
    } catch (e) { /* 무시 */ }
  });

  if (dLike) dLike.addEventListener("click", (e) => { e.stopPropagation(); if (currentCard) toggleLike(currentCard); });
  if (dShare) dShare.addEventListener("click", (e) => { e.stopPropagation(); if (currentCard) doShare(currentCard.href, (currentCard.querySelector(".card-title") || {}).textContent || "디자인 놀이터"); });
})();

// ═════════════════════════════════════════════════════════════
// 2) 디놀 톡톡 (방명록 + 댓글) — Firestore 저장 + PC 페이지네이션 / MO 무한스크롤
// ═════════════════════════════════════════════════════════════
(function initGuestbook() {
  const list = document.getElementById("gbList");
  if (!list) return;
  const pager = document.getElementById("gbPager"),
        nick = document.querySelector(".gb-nick"),
        pw = document.querySelector(".gb-pw"),
        content = document.querySelector(".gb-content"),
        submit = document.getElementById("gbSubmit"),
        count = document.getElementById("gbCount");

  const PER = 10, WINDOW = 5;
  let page = 1;          // PC 페이지네이션 현재 페이지
  let moShown = PER;     // MO 무한스크롤 현재 표시 개수
  let editingId = null;  // 수정 중인 글 ID
  let entries = [];      // 글 목록 {id, nick, body, pwHash, ts, commentCount}

  // 글별 댓글 상태 (재렌더에도 유지) : postId -> {loaded, expanded, list, count, editingId}
  const commentState = {};
  function cstate(pid) {
    if (!commentState[pid]) commentState[pid] = { loaded: false, expanded: false, list: [], count: 0, editingId: null, composerOpen: false };
    return commentState[pid];
  }

  const EMOJI = ["😀","😃","😄","😊","🙂","😎","🤓","🧐","🤩","😌","🥰","😉","😆","🤗","😙","🙃","😇","😺","🤠","😸"];
  function avatar(nk) { if (nk === "운영자K") return "✨"; let h = 0; for (let i = 0; i < nk.length; i++) h = (h * 31 + nk.charCodeAt(i)) >>> 0; return EMOJI[h % EMOJI.length]; }
  const CEMOJI = ["😀","😃","😄","😁","😆","😊","🙂","😉","😍","🥰","😎","🤩","😌","😙","😇","🥳","😂","🤣","🥹","😝","😜","🤪","😢","😭","🥺","😳","😮","🤔","🙄","😅","😴","😤","👍","👏","🙌","🙏","👌","💪","🤙","👀","🤗","🙈","❤️","💜","💙","🔥","✨","🎉"];

  function digitsOnly(el, max = 4) { el && el.addEventListener("input", () => { el.value = el.value.replace(/\D/g, "").slice(0, max); }); }
  // 비번: 일반은 4자리에서 컷, 관리자(481516) 입력 경로만 6자리 허용
  pw && pw.addEventListener("input", () => { const v = pw.value.replace(/\D/g, ""); pw.value = v.slice(0, ADMIN_PW.startsWith(v) ? 6 : 4); });

  // ── 인라인 아이콘 (사이트엔 아이콘 폰트가 없으므로 SVG로 직접) ──
  const ICON_KEBAB = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="1.7"/><circle cx="12" cy="12" r="1.7"/><circle cx="12" cy="19" r="1.7"/></svg>';
  const ICON_BUBBLE = '<svg width="17" height="17" viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="6" width="14" height="10.5" rx="4" fill="#6f66cc"/><rect x="3" y="4" width="14" height="10.5" rx="4" fill="#fff"/><path d="M6.5 14 L4.5 17.6 L10 14 Z" fill="#fff"/><circle cx="6.8" cy="9.2" r="1.15" fill="#6f66cc"/><circle cx="10" cy="9.2" r="1.15" fill="#6f66cc"/><circle cx="13.2" cy="9.2" r="1.15" fill="#6f66cc"/></svg>';
  const ICON_SMILE = '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="#c9c9d4" stroke-width="1.7"/><path d="M8.5 14 Q12 17 15.5 14" fill="none" stroke="#c9c9d4" stroke-width="1.7" stroke-linecap="round"/><circle cx="9.3" cy="10.2" r="1.1" fill="#c9c9d4"/><circle cx="14.7" cy="10.2" r="1.1" fill="#c9c9d4"/></svg>';
  const ICON_EDIT = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>';
  const ICON_TRASH = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/><path d="M10 11v5"/><path d="M14 11v5"/></svg>';
  function chev(up) { return '<svg class="gb-cchev' + (up ? ' up' : '') + '" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'; }

  function fmtTime(ts) {
    const d = ts && ts.toDate ? ts.toDate() : (ts instanceof Date ? ts : new Date());
    const now = new Date();
    const diff = Math.floor((now - d) / 1000); // 초 단위 경과
    if (diff < 60) return "방금 전";
    if (diff < 3600) return Math.floor(diff / 60) + "분 전";
    if (diff < 86400) return Math.floor(diff / 3600) + "시간 전";
    const days = Math.floor(diff / 86400);
    if (days === 1) return "어제";
    if (days < 7) return days + "일 전";
    const p = n => String(n).padStart(2, "0");
    return d.getFullYear() + ". " + p(d.getMonth() + 1) + ". " + p(d.getDate());
  }

  // ── 댓글 아이템 HTML ──
  function commentHTML(pid, c) {
    const cs = cstate(pid);
    const nk = c.nick.length > 12 ? c.nick.slice(0, 12) + "…" : c.nick;
    const timeStr = fmtTime(c.ts);
    if (cs.editingId === c.id) {
      return '<div class="gb-comment editing" data-cid="' + c.id + '">' +
        '<div class="gb-entry-row"><span class="gb-avatar gb-avatar-sm">' + avatar(c.nick) + '</span>' +
        '<div class="gb-entry-main">' +
        '<div class="gb-entry-head"><span class="gb-entry-nick">' + esc(nk) + '</span>' +
        '<span class="gb-entry-time">' + esc(timeStr) + '</span></div>' +
        '<div class="gb-cedit"><textarea class="gb-cedit-text" maxlength="500">' + esc(c.body) + '</textarea>' +
        '<div class="gb-cedit-btns"><button class="gb-cedit-cancel" data-post="' + pid + '">취소</button>' +
        '<button class="gb-cedit-save" data-post="' + pid + '" data-cid="' + c.id + '">저장</button></div></div>' +
        '</div></div></div>';
    }
    return '<div class="gb-comment" data-cid="' + c.id + '">' +
      '<div class="gb-entry-row"><span class="gb-avatar gb-avatar-sm">' + avatar(c.nick) + '</span>' +
      '<div class="gb-entry-main">' +
      '<div class="gb-entry-head"><span class="gb-entry-nick">' + esc(nk) + '</span>' +
      '<span class="gb-entry-time">' + esc(timeStr) + '</span>' +
      '<button class="gb-kebab gb-ckebab" data-post="' + pid + '" data-cid="' + c.id + '" aria-label="옵션">' + ICON_KEBAB + '</button></div>' +
      '<div class="gb-entry-body">' + esc(c.body) + '</div>' +
      '</div></div></div>';
  }

  // ── 댓글 입력 폼 HTML ──
  function composerHTML(pid) {
    return '<div class="gb-cform" data-post="' + pid + '">' +
      '<div class="gb-cform-row">' +
        '<input class="gb-cnick" type="text" maxlength="12" placeholder="닉네임 (분야)">' +
        '<input class="gb-cpw" type="password" inputmode="numeric" maxlength="6" placeholder="비밀번호 4자리">' +
      '</div>' +
      '<div class="gb-cform-body"><textarea class="gb-ccontent" maxlength="500" placeholder="댓글을 남겨보세요"></textarea>' +
      '<span class="gb-ccount">0 / 500</span></div>' +
      '<div class="gb-cform-bar"><button type="button" class="gb-csmile" aria-label="이모지">' + ICON_SMILE + '</button>' +
      '<div class="gb-cactions"><button class="gb-ccancel" data-post="' + pid + '">취소</button>' +
      '<button class="gb-csubmit" data-post="' + pid + '">등록</button></div></div>' +
    '</div>';
  }

  // ── 댓글 영역(리스트 + 컴포저). 토글/댓글쓰기 버튼은 글의 액션 행에 있음 ──
  function commentSectionHTML(pid) {
    const cs = cstate(pid);
    if (!cs.expanded && !cs.composerOpen) return '';
    let html = '<div class="gb-comments">';
    if (cs.composerOpen) html += composerHTML(pid);
    if (cs.expanded) {
      if (!cs.loaded) html += '<div class="gb-cloading">댓글을 불러오는 중…</div>';
      else if (!cs.list.length) html += '<div class="gb-cempty">첫 댓글을 남겨보세요.</div>';
      else html += '<div class="gb-clist">' + cs.list.map(c => commentHTML(pid, c)).join("") + '</div>';
    }
    return html + '</div>';
  }

  // ── 글 엔트리 HTML ──
  function entryHTML(e) {
    const nk = e.nick.length > 12 ? e.nick.slice(0, 12) + "…" : e.nick;
    const timeStr = fmtTime(e.ts);
    if (editingId === e.id) {
      return '<div class="gb-entry editing" data-id="' + e.id + '">' +
        '<div class="gb-entry-row"><span class="gb-avatar">' + avatar(e.nick) + '</span>' +
        '<div class="gb-entry-main">' +
        '<div class="gb-entry-head"><span class="gb-entry-nick">' + esc(nk) + '</span>' +
        '<span class="gb-entry-time">' + esc(timeStr) + '</span></div>' +
        '<div class="gb-edit-area"><textarea class="gb-edit-text" maxlength="1000">' + esc(e.body) + '</textarea>' +
        '<div class="gb-edit-btns"><button class="gb-edit-cancel">취소</button>' +
        '<button class="gb-edit-save" data-id="' + e.id + '">저장</button></div></div>' +
        '</div></div></div>';
    }
    const cs = cstate(e.id);
    return '<div class="gb-entry" data-id="' + e.id + '">' +
      '<div class="gb-entry-row"><span class="gb-avatar">' + avatar(e.nick) + '</span>' +
      '<div class="gb-entry-main">' +
      '<div class="gb-entry-head"><span class="gb-entry-nick">' + esc(nk) + '</span>' +
      '<span class="gb-entry-time">' + esc(timeStr) + '</span>' +
      '<button class="gb-kebab gb-pkebab" data-post="' + e.id + '" aria-label="옵션">' + ICON_KEBAB + '</button></div>' +
      '<div class="gb-entry-body">' + esc(e.body) + '</div>' +
      '<div class="gb-action-row">' +
      '<button class="gb-cwrite" data-post="' + e.id + '">댓글쓰기</button>' +
      ((cs.count || 0) > 0 ? '<button class="gb-ctoggle" data-post="' + e.id + '">댓글 <span class="gb-cnum">' + cs.count + '</span>' + chev(cs.expanded) + '</button>' : '') +
      '</div>' +
      commentSectionHTML(e.id) +
      '</div></div></div>';
  }

  function renderList() {
    if (!entries.length) { list.innerHTML = '<div class="gb-empty">아직 남겨진 글이 없어요. 첫 이야기를 남겨보세요!</div>'; if (pager) pager.innerHTML = ""; return; }
    if (isMobile()) {
      if (moShown > entries.length) moShown = entries.length;
      list.innerHTML = entries.slice(0, moShown).map(entryHTML).join("");
      if (pager) pager.innerHTML = "";
    } else {
      const tp = Math.max(1, Math.ceil(entries.length / PER));
      if (page > tp) page = tp; if (page < 1) page = 1;
      const start = (page - 1) * PER;
      list.innerHTML = entries.slice(start, start + PER).map(entryHTML).join("");
      renderPager(tp);
    }
  }

  function renderPager(tp) {
    if (!pager) return;
    pager.innerHTML = "";
    if (tp <= 1) return;
    function mk(label, target, disabled, active, nav) {
      const btn = document.createElement("button");
      let cls = "gb-page-btn"; if (active) cls += " active";
      if (nav) { cls += " gb-page-nav"; if (nav !== "nav") cls += " " + nav; }
      btn.className = cls; btn.textContent = label; btn.disabled = !!disabled;
      if (!disabled && !active) btn.addEventListener("click", () => { page = target; renderList(); });
      pager.appendChild(btn);
    }
    mk("«", 1, page === 1, false, "nav");
    mk("‹", page - 1, page === 1, false, "nav-prev");
    const half = Math.floor(WINDOW / 2);
    let s = Math.max(1, page - half), e = Math.min(tp, s + WINDOW - 1);
    s = Math.max(1, e - WINDOW + 1);
    for (let n = s; n <= e; n++) mk(String(n), n, false, n === page, null);
    mk("›", page + 1, page === tp, false, "nav-next");
    mk("»", tp, page === tp, false, "nav");
  }

  // 모바일 무한스크롤
  const sentinel = document.createElement("div");
  sentinel.style.height = "1px";
  list.parentNode.insertBefore(sentinel, list.nextSibling);
  const io = new IntersectionObserver((ents) => {
    if (!isMobile()) return;
    if (ents[0].isIntersecting && moShown < entries.length) { moShown += PER; renderList(); }
  }, { rootMargin: "200px" });
  io.observe(sentinel);

  let wasMobile = isMobile();
  window.addEventListener("resize", () => {
    const now = isMobile();
    if (now !== wasMobile) { wasMobile = now; page = 1; moShown = PER; renderList(); }
  });

  // ── 옵션(⋯) 메뉴 ──
  let openMenu = null;
  function closeMenu() { if (openMenu) { openMenu.remove(); openMenu = null; } }
  function showMenu(kebabBtn, scope, pid, cid) {
    closeMenu();
    const menu = document.createElement("div");
    menu.className = "gb-menu";
    menu.innerHTML = '<button class="gb-menu-item gb-menu-edit">' + ICON_EDIT + '수정</button><button class="gb-menu-item gb-menu-del">' + ICON_TRASH + '삭제</button>';
    menu.querySelector(".gb-menu-edit").addEventListener("click", (ev) => { ev.stopPropagation(); closeMenu(); openModal("edit", scope, pid, cid); });
    menu.querySelector(".gb-menu-del").addEventListener("click", (ev) => { ev.stopPropagation(); closeMenu(); openModal("delete", scope, pid, cid); });
    kebabBtn.parentNode.appendChild(menu); // head가 position:relative
    openMenu = menu;
  }

  // ── 이모지 피커 ──
  function closePickers(except) { document.querySelectorAll(".gb-emoji-pick").forEach(p => { if (p !== except) p.remove(); }); }
  function toggleEmojiPicker(smileBtn) {
    const existing = smileBtn.parentNode.querySelector(".gb-emoji-pick");
    if (existing) { existing.remove(); return; }
    closePickers(); closeMenu();
    const pick = document.createElement("div");
    pick.className = "gb-emoji-pick";
    pick.innerHTML = CEMOJI.map(em => '<button type="button" class="gb-emoji-btn">' + em + '</button>').join("");
    pick.addEventListener("click", (e) => {
      const b = e.target.closest(".gb-emoji-btn"); if (!b) return; e.stopPropagation();
      const form = smileBtn.closest(".gb-cform");
      const ta = form.querySelector(".gb-ccontent");
      if (ta) { ta.value = (ta.value + b.textContent).slice(0, 500); const cnt = form.querySelector(".gb-ccount"); if (cnt) cnt.textContent = ta.value.length + " / 500"; ta.focus(); }
    });
    smileBtn.parentNode.appendChild(pick); // bar가 position:relative
  }

  // 바깥 클릭 시 메뉴/피커 닫기
  document.addEventListener("click", (e) => {
    if (openMenu && !openMenu.contains(e.target)) closeMenu();
    if (!e.target.closest(".gb-emoji-pick") && !e.target.closest(".gb-csmile") && !e.target.closest(".gb-tsmile")) closePickers();
  });

  // ── 비번 확인 모달 (글/댓글 공용) ──
  const mOverlay = document.getElementById("gbModalOverlay"),
        modal = document.getElementById("gbModal"),
        mTitle = document.getElementById("gbModalTitle"),
        mPw = document.getElementById("gbModalPw"),
        mErr = document.getElementById("gbModalErr"),
        mOk = document.getElementById("gbModalOk"),
        mCancel = document.getElementById("gbModalCancel");
  digitsOnly(mPw, 6);
  if (mPw) mPw.addEventListener("input", () => { mOk.disabled = !/^\d{4,6}$/.test(mPw.value); });
  let pending = null; // {action, scope:'post'|'comment', pid, cid}
  function openModal(action, scope, pid, cid) {
    pending = { action, scope, pid, cid };
    mTitle.textContent = action === "delete" ? "삭제하려면 비밀번호를 입력하세요" : "수정하려면 비밀번호를 입력하세요";
    mPw.value = ""; mErr.textContent = ""; mOk.disabled = true;
    mOverlay.classList.add("show"); modal.classList.add("show"); setTimeout(() => mPw.focus(), 50);
  }
  function closeModal() { mOverlay.classList.remove("show"); modal.classList.remove("show"); pending = null; }
  async function confirmModal() {
    if (!pending) return;
    const input = mPw.value.trim();
    if (!/^\d{4,6}$/.test(input)) { mErr.textContent = "비밀번호를 입력하세요."; return; }
    let pwHash;
    if (pending.scope === "post") {
      const e = entries.find(x => x.id === pending.pid); if (!e) { closeModal(); return; } pwHash = e.pwHash;
    } else {
      const cs = cstate(pending.pid); const c = cs.list.find(x => x.id === pending.cid); if (!c) { closeModal(); return; } pwHash = c.pwHash;
    }
    const inputHash = await sha256(input);
    const ok = (input === ADMIN_PW) || (pwHash && inputHash === pwHash);
    if (!ok) { mErr.textContent = "비밀번호가 일치하지 않습니다."; return; }
    const { action, scope, pid, cid } = pending; closeModal();
    if (scope === "post") {
      if (action === "delete") {
        try { await deleteDoc(doc(db, "guestbook", pid)); entries = entries.filter(x => x.id !== pid); if (editingId === pid) editingId = null; delete commentState[pid]; renderList(); }
        catch (err) { alert("삭제에 실패했어요. 잠시 후 다시 시도해주세요."); }
      } else { editingId = pid; renderList(); }
    } else {
      if (action === "delete") {
        try {
          await deleteDoc(doc(db, "guestbook", pid, "comments", cid));
          try { await updateDoc(doc(db, "guestbook", pid), { commentCount: increment(-1) }); } catch (e2) {}
          const cs = cstate(pid); cs.list = cs.list.filter(x => x.id !== cid); cs.count = Math.max(0, (cs.count || 1) - 1);
          if (cs.editingId === cid) cs.editingId = null; renderList();
        } catch (err) { alert("삭제에 실패했어요. 잠시 후 다시 시도해주세요."); }
      } else { cstate(pid).editingId = cid; renderList(); }
    }
  }
  if (mOk) mOk.addEventListener("click", confirmModal);
  if (mPw) mPw.addEventListener("keydown", ev => { if (ev.key === "Enter") confirmModal(); });
  if (mCancel) mCancel.addEventListener("click", closeModal);
  if (mOverlay) mOverlay.addEventListener("click", closeModal);

  // ── 댓글 로드(지연) ──
  async function loadComments(pid) {
    const cs = cstate(pid);
    if (cs.loaded) return;
    try {
      const snap = await getDocs(query(collection(db, "guestbook", pid, "comments"), orderBy("createdAt", "asc")));
      cs.list = snap.docs.map(d => { const v = d.data(); return { id: d.id, nick: v.nick || "", body: v.body || "", pwHash: v.pwHash || "", ts: v.createdAt }; });
      cs.loaded = true; cs.count = cs.list.length;
    } catch (e) { cs.loaded = true; cs.list = []; }
  }
  async function toggleComments(pid) {
    const cs = cstate(pid);
    cs.expanded = !cs.expanded;
    renderList();
    if (cs.expanded && !cs.loaded) { await loadComments(pid); renderList(); }
  }
  function openComposer(pid) {
    for (const k in commentState) { if (k !== pid) commentState[k].composerOpen = false; }
    cstate(pid).composerOpen = true;
    renderList();
  }

  async function addComment(pid, form, btn) {
    const p = (form.querySelector(".gb-cpw").value || "").trim();
    const isAdmin = (p === ADMIN_PW);
    const n = isAdmin ? "운영자K" : (form.querySelector(".gb-cnick").value || "").trim().slice(0, 12);
    const b = (form.querySelector(".gb-ccontent").value || "").trim().slice(0, 500);
    if (!n) { alert("닉네임을 입력해주세요."); return; }
    if (!isAdmin && !/^\d{4}$/.test(p)) { alert("비밀번호 4자리(숫자)를 입력해주세요."); return; }
    if (!b) { alert("댓글을 입력해주세요."); return; }
    btn.disabled = true;
    try {
      const pwHash = await sha256(p);
      const ref = await addDoc(collection(db, "guestbook", pid, "comments"), { nick: n, body: b, pwHash, createdAt: serverTimestamp() });
      try { await updateDoc(doc(db, "guestbook", pid), { commentCount: increment(1) }); } catch (e2) {}
      const cs = cstate(pid);
      cs.count = (cs.count || 0) + 1; cs.composerOpen = false; cs.expanded = true;
      if (cs.loaded) cs.list.push({ id: ref.id, nick: n, body: b, pwHash, ts: new Date() });
      else await loadComments(pid);
      renderList();
    } catch (err) { alert("댓글 등록에 실패했어요. 잠시 후 다시 시도해주세요."); btn.disabled = false; }
  }

  async function saveCommentEdit(pid, cid, ta) {
    const val = (ta.value || "").trim().slice(0, 500); if (!val) { alert("내용을 입력해주세요."); return; }
    try {
      await updateDoc(doc(db, "guestbook", pid, "comments", cid), { body: val });
      const cs = cstate(pid); const c = cs.list.find(x => x.id === cid); if (c) c.body = val;
      cs.editingId = null; renderList();
    } catch (err) { alert("수정에 실패했어요. 잠시 후 다시 시도해주세요."); }
  }

  // ── 리스트 클릭 위임 ──
  list.addEventListener("click", async (ev) => {
    const kebab = ev.target.closest(".gb-kebab");
    if (kebab) { ev.stopPropagation(); showMenu(kebab, kebab.classList.contains("gb-ckebab") ? "comment" : "post", kebab.dataset.post, kebab.dataset.cid); return; }
    const toggle = ev.target.closest(".gb-ctoggle");
    if (toggle) { toggleComments(toggle.dataset.post); return; }
    const cwrite = ev.target.closest(".gb-cwrite");
    if (cwrite) { openComposer(cwrite.dataset.post); return; }
    const csmile = ev.target.closest(".gb-csmile");
    if (csmile) { ev.stopPropagation(); toggleEmojiPicker(csmile); return; }
    const ccancel = ev.target.closest(".gb-ccancel");
    if (ccancel) { cstate(ccancel.dataset.post).composerOpen = false; renderList(); return; }
    const csubmit = ev.target.closest(".gb-csubmit");
    if (csubmit) { addComment(csubmit.dataset.post, csubmit.closest(".gb-cform"), csubmit); return; }
    const cCancel = ev.target.closest(".gb-cedit-cancel");
    if (cCancel) { cstate(cCancel.dataset.post).editingId = null; renderList(); return; }
    const cSave = ev.target.closest(".gb-cedit-save");
    if (cSave) { saveCommentEdit(cSave.dataset.post, cSave.dataset.cid, cSave.closest(".gb-cedit").querySelector(".gb-cedit-text")); return; }
    // 글 수정 저장/취소
    const t = ev.target;
    if (t.classList.contains("gb-edit-cancel")) { editingId = null; renderList(); }
    else if (t.classList.contains("gb-edit-save")) {
      const id = t.dataset.id, ta = t.closest(".gb-entry").querySelector(".gb-edit-text");
      const val = ta.value.trim(); if (!val) { alert("내용을 입력해주세요."); return; }
      try { await updateDoc(doc(db, "guestbook", id), { body: val }); const e = entries.find(x => x.id === id); if (e) e.body = val; editingId = null; renderList(); }
      catch (err) { alert("수정에 실패했어요. 잠시 후 다시 시도해주세요."); }
    }
  });

  // ── 리스트 입력 위임 (댓글 글자수·비번 숫자) ──
  list.addEventListener("input", (ev) => {
    const t = ev.target;
    if (t.classList.contains("gb-ccontent")) { const c = t.closest(".gb-cform").querySelector(".gb-ccount"); if (c) c.textContent = t.value.length + " / 500"; }
    else if (t.classList.contains("gb-cpw")) { const v = t.value.replace(/\D/g, ""); t.value = v.slice(0, ADMIN_PW.startsWith(v) ? 6 : 4); }
  });

  // ── 글 등록 ──
  function updateSubmit() { const p = pw.value.trim(), a = (p === ADMIN_PW); submit.disabled = !((a || nick.value.trim()) && (a || /^\d{4}$/.test(p)) && content.value.trim()); }
  [nick, pw, content].forEach(el => el && el.addEventListener("input", updateSubmit));
  content && content.addEventListener("input", () => { count.textContent = content.value.length + " / 1000"; });
  updateSubmit();

  // 상단 폼 이모지 (본문에만 삽입)
  const gbSmile = document.getElementById("gbSmile");
  if (gbSmile) {
    const toggleSmile = () => { gbSmile.style.display = content.value.trim() ? "inline-flex" : "none"; };
    toggleSmile();
    content && content.addEventListener("input", toggleSmile);
    gbSmile.addEventListener("click", (e) => {
      e.stopPropagation();
      const existing = gbSmile.parentNode.querySelector(".gb-emoji-pick");
      if (existing) { existing.remove(); return; }
      closePickers(); closeMenu();
      const pick = document.createElement("div");
      pick.className = "gb-emoji-pick";
      pick.innerHTML = CEMOJI.map(em => '<button type="button" class="gb-emoji-btn">' + em + '</button>').join("");
      pick.addEventListener("click", (ev) => {
        const b = ev.target.closest(".gb-emoji-btn"); if (!b) return; ev.stopPropagation();
        content.value = (content.value + b.textContent).slice(0, 1000);
        count.textContent = content.value.length + " / 1000";
        updateSubmit(); content.focus();
      });
      gbSmile.parentNode.appendChild(pick);
    });
  }

  submit && submit.addEventListener("click", async () => {
    const p = pw.value.trim(), isAdmin = (p === ADMIN_PW);
    const n = isAdmin ? "운영자K" : nick.value.trim().slice(0, 12), b = content.value.trim();
    if (!n) { alert("닉네임을 입력해주세요."); return; }
    if (!isAdmin && !/^\d{4}$/.test(p)) { alert("비밀번호 4자리(숫자)를 입력해주세요."); return; }
    if (!b) { alert("내용을 입력해주세요."); return; }
    submit.disabled = true;
    try {
      const pwHash = await sha256(p);
      const ref = await addDoc(collection(db, "guestbook"), { nick: n, body: b, pwHash, commentCount: 0, createdAt: serverTimestamp() });
      entries.unshift({ id: ref.id, nick: n, body: b, pwHash, commentCount: 0, ts: new Date() });
      cstate(ref.id).count = 0;
      nick.value = ""; pw.value = ""; content.value = ""; count.textContent = "0 / 1000"; if (gbSmile) gbSmile.style.display = "none";
      page = 1; moShown = PER; editingId = null; renderList(); updateSubmit();
    } catch (err) { alert("등록에 실패했어요. 잠시 후 다시 시도해주세요."); updateSubmit(); }
  });

  // ── 초기 로드 ──
  (async function load() {
    try {
      const snap = await getDocs(query(collection(db, "guestbook"), orderBy("createdAt", "desc")));
      entries = snap.docs.map(d => {
        const v = d.data();
        return { id: d.id, nick: v.nick || "", body: v.body || "", pwHash: v.pwHash || "", commentCount: v.commentCount || 0, ts: v.createdAt };
      });
      entries.forEach(e => { cstate(e.id).count = e.commentCount || 0; });
      renderList();
    } catch (e) {
      list.innerHTML = '<div class="gb-empty">방명록을 불러오지 못했어요. 새로고침 해주세요.</div>';
    }
  })();
})();
