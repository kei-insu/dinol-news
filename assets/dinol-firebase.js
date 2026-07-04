// ─────────────────────────────────────────────────────────────
// 디자인 놀이터 — Firebase 연동 (디놀 톡톡 방명록 + 좋아요)
// 공통 모듈: 모든 브리핑에서 이 파일 하나만 불러온다.
// ─────────────────────────────────────────────────────────────
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getFirestore, collection, addDoc, getDocs, getDoc, doc,
  updateDoc, deleteDoc, query, orderBy, serverTimestamp,
  runTransaction, setDoc
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

// 관리자 마스터 비밀번호(스팸 정리용) — 아무 글이나 이 값으로 수정/삭제 가능
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
// 2) 디놀 톡톡 (방명록) — Firestore 저장 + PC 페이지네이션 / MO 무한스크롤
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
  let editingId = null;
  let entries = [];      // {id, nick, body, pwHash, time, ts}

  const EMOJI = ["😀","😃","😄","😊","🙂","😎","🤓","🧐","🤩","😌","🥰","😉","😆","🤗","😙","🙃","😇","😺","🤠","😸"];
  function avatar(nk) { let h = 0; for (let i = 0; i < nk.length; i++) h = (h * 31 + nk.charCodeAt(i)) >>> 0; return EMOJI[h % EMOJI.length]; }
  function digitsOnly(el) { el && el.addEventListener("input", () => { el.value = el.value.replace(/\D/g, "").slice(0, 4); }); }
  digitsOnly(pw);

  function fmtTime(ts) {
    const d = ts && ts.toDate ? ts.toDate() : new Date();
    const p = n => String(n).padStart(2, "0");
    return d.getFullYear() + ". " + p(d.getMonth() + 1) + ". " + p(d.getDate()) + " " + p(d.getHours()) + ":" + p(d.getMinutes());
  }

  function entryHTML(e) {
    const head = '<div class="gb-entry-head"><span class="gb-entry-nick">' + avatar(e.nick) + " " + esc(e.nick) + '</span>' +
      '<span class="gb-entry-time">' + esc(e.time) + '</span>' +
      '<div class="gb-entry-actions"><button class="gb-act-edit" data-id="' + e.id + '">수정</button><button class="gb-act-del" data-id="' + e.id + '">삭제</button></div></div>';
    if (editingId === e.id) {
      return '<div class="gb-entry editing" data-id="' + e.id + '">' + head +
        '<div class="gb-edit-area"><textarea class="gb-edit-text" maxlength="200">' + esc(e.body) + '</textarea>' +
        '<div class="gb-edit-btns"><button class="gb-edit-cancel">취소</button><button class="gb-edit-save" data-id="' + e.id + '">저장</button></div></div></div>';
    }
    return '<div class="gb-entry" data-id="' + e.id + '">' + head + '<div class="gb-entry-body">' + esc(e.body) + '</div></div>';
  }

  function renderList() {
    if (!entries.length) { list.innerHTML = '<div class="gb-empty">아직 남겨진 글이 없어요. 첫 이야기를 남겨보세요!</div>'; if (pager) pager.innerHTML = ""; return; }
    if (isMobile()) {
      // 모바일: 위에서부터 moShown개 표시 (아래로 계속)
      if (moShown > entries.length) moShown = entries.length;
      list.innerHTML = entries.slice(0, moShown).map(entryHTML).join("");
      if (pager) pager.innerHTML = "";
    } else {
      // PC: 10개 단위 페이지네이션
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

  // 모바일 무한스크롤: 바닥 근처면 10개 더
  const sentinel = document.createElement("div");
  sentinel.style.height = "1px";
  list.parentNode.insertBefore(sentinel, list.nextSibling);
  const io = new IntersectionObserver((ents) => {
    if (!isMobile()) return;
    if (ents[0].isIntersecting && moShown < entries.length) { moShown += PER; renderList(); }
  }, { rootMargin: "200px" });
  io.observe(sentinel);

  // PC↔MO 전환 시 재렌더
  let wasMobile = isMobile();
  window.addEventListener("resize", () => {
    const now = isMobile();
    if (now !== wasMobile) { wasMobile = now; page = 1; moShown = PER; renderList(); }
  });

  // ── 비번 확인 모달 ──
  const mOverlay = document.getElementById("gbModalOverlay"),
        modal = document.getElementById("gbModal"),
        mTitle = document.getElementById("gbModalTitle"),
        mPw = document.getElementById("gbModalPw"),
        mErr = document.getElementById("gbModalErr"),
        mOk = document.getElementById("gbModalOk"),
        mCancel = document.getElementById("gbModalCancel");
  digitsOnly(mPw);
  if (mPw) mPw.addEventListener("input", () => { mOk.disabled = !/^\d{4}$/.test(mPw.value); });
  let pending = null; // {type, id}
  function openModal(type, id) {
    pending = { type, id };
    mTitle.textContent = type === "delete" ? "삭제하려면 비밀번호를 입력하세요" : "수정하려면 비밀번호를 입력하세요";
    mPw.value = ""; mErr.textContent = ""; mOk.disabled = true;
    mOverlay.classList.add("show"); modal.classList.add("show"); setTimeout(() => mPw.focus(), 50);
  }
  function closeModal() { mOverlay.classList.remove("show"); modal.classList.remove("show"); pending = null; }
  async function confirmModal() {
    if (!pending) return;
    const input = mPw.value.trim();
    if (!/^\d{4}$/.test(input)) { mErr.textContent = "4자리 숫자를 입력하세요."; return; }
    const e = entries.find(x => x.id === pending.id);
    if (!e) { closeModal(); return; }
    const inputHash = await sha256(input);
    const ok = (input === ADMIN_PW) || (e.pwHash && inputHash === e.pwHash);
    if (!ok) { mErr.textContent = "비밀번호가 일치하지 않습니다."; return; }
    const type = pending.type, id = pending.id; closeModal();
    if (type === "delete") {
      try { await deleteDoc(doc(db, "guestbook", id)); entries = entries.filter(x => x.id !== id); if (editingId === id) editingId = null; renderList(); }
      catch (err) { alert("삭제에 실패했어요. 잠시 후 다시 시도해주세요."); }
    } else { editingId = id; renderList(); }
  }
  if (mOk) mOk.addEventListener("click", confirmModal);
  if (mPw) mPw.addEventListener("keydown", ev => { if (ev.key === "Enter") confirmModal(); });
  if (mCancel) mCancel.addEventListener("click", closeModal);
  if (mOverlay) mOverlay.addEventListener("click", closeModal);

  // 리스트 이벤트 위임 (수정/삭제/저장/취소)
  list.addEventListener("click", async (ev) => {
    const t = ev.target;
    if (t.classList.contains("gb-act-del")) openModal("delete", t.dataset.id);
    else if (t.classList.contains("gb-act-edit")) openModal("edit", t.dataset.id);
    else if (t.classList.contains("gb-edit-cancel")) { editingId = null; renderList(); }
    else if (t.classList.contains("gb-edit-save")) {
      const id = t.dataset.id, ta = t.closest(".gb-entry").querySelector(".gb-edit-text");
      const val = ta.value.trim(); if (!val) { alert("내용을 입력해주세요."); return; }
      try {
        await updateDoc(doc(db, "guestbook", id), { body: val });
        const e = entries.find(x => x.id === id); if (e) e.body = val;
        editingId = null; renderList();
      } catch (err) { alert("수정에 실패했어요. 잠시 후 다시 시도해주세요."); }
    }
  });

  // 등록 버튼 활성/비활성
  function updateSubmit() { submit.disabled = !(nick.value.trim() && /^\d{4}$/.test(pw.value.trim()) && content.value.trim()); }
  [nick, pw, content].forEach(el => el && el.addEventListener("input", updateSubmit));
  content && content.addEventListener("input", () => { count.textContent = content.value.length + " / 200"; });
  updateSubmit();

  submit && submit.addEventListener("click", async () => {
    const n = nick.value.trim(), b = content.value.trim(), p = pw.value.trim();
    if (!n) { alert("닉네임을 입력해주세요."); return; }
    if (!/^\d{4}$/.test(p)) { alert("비밀번호 4자리(숫자)를 입력해주세요."); return; }
    if (!b) { alert("내용을 입력해주세요."); return; }
    submit.disabled = true;
    try {
      const pwHash = await sha256(p);
      const ref = await addDoc(collection(db, "guestbook"), { nick: n, body: b, pwHash, createdAt: serverTimestamp() });
      // 로컬 목록 맨 앞에 추가 (서버 시간 반영 전 임시 표시)
      entries.unshift({ id: ref.id, nick: n, body: b, pwHash, time: fmtTime(null), ts: null });
      nick.value = ""; pw.value = ""; content.value = ""; count.textContent = "0 / 200";
      page = 1; moShown = PER; editingId = null; renderList(); updateSubmit();
    } catch (err) {
      alert("등록에 실패했어요. 잠시 후 다시 시도해주세요."); updateSubmit();
    }
  });

  // ── 초기 로드: Firestore에서 전체 조회 (최신순) ──
  (async function load() {
    try {
      const snap = await getDocs(query(collection(db, "guestbook"), orderBy("createdAt", "desc")));
      entries = snap.docs.map(d => {
        const v = d.data();
        return { id: d.id, nick: v.nick || "", body: v.body || "", pwHash: v.pwHash || "", time: fmtTime(v.createdAt), ts: v.createdAt };
      });
      renderList();
    } catch (e) {
      list.innerHTML = '<div class="gb-empty">방명록을 불러오지 못했어요. 새로고침 해주세요.</div>';
    }
  })();
})();
