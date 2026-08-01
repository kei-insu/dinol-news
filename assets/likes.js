// ============================================================
// likes.js — Firebase·DOM 어댑터 (도메인 로직은 likes-core.js 소유)
//   · dinol-firebase.js 가 공개한 __dinolFirebaseReady 를 소비.
//   · Firestore 트랜잭션 API·localStorage·알림을 어댑터로 감싸 core 에 주입.
//   · ⛔ 여기서 stale 조건을 재판정하지 않는다(판단은 전부 core).
// ============================================================
import { doc, getDoc, runTransaction } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import { createLikesCore, PERMISSION_DENIED } from "./likes-core.js";

const PERMISSION_MSG = "좋아요 기능이 업데이트되었습니다. 페이지를 새로고침한 뒤 다시 시도해 주세요.";
const GENERIC_MSG = "잠시 후 다시 시도해주세요";

(async function initLikes() {
  const boxes = [...document.querySelectorAll(".like-box")];
  if (!boxes.length) return;

  let ctx;
  try {
    ctx = await window.__dinolFirebaseReady;         // 없거나 실패면 조용히 종료(throw 금지)
  } catch (e) {
    console.warn("[likes] Firebase 준비 실패 — 좋아요 비활성", e);
    return;
  }
  if (!ctx || !ctx.db) {
    console.warn("[likes] __dinolFirebaseReady 없음 — 좋아요 비활성");
    return;
  }
  const db = ctx.db;

  // ── 알림 어댑터 (토스트) ──
  const toastEl = document.createElement("div");
  toastEl.className = "gb-toast";
  document.body.appendChild(toastEl);
  let tTimer;
  const notify = {
    toast(msg) {
      toastEl.textContent = msg;
      toastEl.classList.add("show");
      clearTimeout(tTimer);
      tTimer = setTimeout(() => toastEl.classList.remove("show"), 1800);
    },
  };

  // ── 저장소 어댑터 (localStorage) ──
  const storage = {
    get: (k) => localStorage.getItem(k),
    set: (k, v) => localStorage.setItem(k, v),
    remove: (k) => localStorage.removeItem(k),
  };

  // ── Firestore 어댑터 ──
  // getLike: 단발 읽기(초기 카운트·stale 재조회). runTransaction: 핸들러에 tx 어댑터 주입.
  const firestore = {
    async getLike(id) {
      const snap = await getDoc(doc(db, "likes", id));
      return snap.exists() ? { exists: true, count: snap.data().count } : { exists: false };
    },
    runTransaction: (handler) =>
      runTransaction(db, async (firebaseTx) => {
        const adapter = {
          async getLike(id) {
            const snap = await firebaseTx.get(doc(db, "likes", id));
            return snap.exists() ? { exists: true, count: snap.data().count } : { exists: false };
          },
          createLike(id, data) { firebaseTx.set(doc(db, "likes", id), data); },        // {count,url} 만 set(merge 없음)
          updateLikeCount(id, count) { firebaseTx.update(doc(db, "likes", id), { count }); }, // {count} 만 update
        };
        return handler(adapter);
      }),
  };

  const core = createLikesCore({ firestore, storage, notify });

  boxes.forEach(bindBox);

  function bindBox(box) {
    // dataset 3종만 사용. location.pathname·href·JSON-LD·.detail-cta 추론 금지.
    const contentId = box.dataset.contentId;
    const sourceUrl = box.dataset.sourceUrl;
    const shareUrl = box.dataset.shareUrl;
    if (!contentId || !sourceUrl || !shareUrl) return;   // 셋 중 하나라도 없으면 건너뜀

    const likeBtn = box.querySelector(".act-like");
    const countEl = box.querySelector(".act-count");
    const shareBtn = box.querySelector(".act-share");

    let { liked } = core.resolveInitial(contentId, sourceUrl);
    let count = 0;
    let busy = false;

    function paint() {
      if (likeBtn) {
        likeBtn.classList.toggle("liked", liked);
        likeBtn.setAttribute("aria-pressed", liked ? "true" : "false");
      }
      if (countEl) countEl.textContent = count > 0 ? String(count) : "";
    }
    paint();

    // 초기 표시용 카운트(실패해도 0)
    core.loadCount(contentId).then((c) => { count = c; paint(); });

    if (likeBtn) likeBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();   // 카드(article) 클릭 → markAsRead 로 버블링 방지
      if (busy) return;
      busy = true;
      const willLike = !liked;
      const prevLiked = liked, prevCount = count;
      // 낙관적 UI
      liked = willLike;
      count = Math.max(0, count + (willLike ? 1 : -1));
      paint();
      try {
        const r = await core.toggle(contentId, sourceUrl, { willLike, lastCount: prevCount });
        liked = r.liked;
        count = r.count;
        paint();
      } catch (err) {
        // 트랜잭션 거부 → 롤백 + 오류 UI
        liked = prevLiked;
        count = prevCount;
        paint();
        if (err && err.code === PERMISSION_DENIED) notify.toast(PERMISSION_MSG);
        else notify.toast(GENERIC_MSG);
      } finally {
        busy = false;
      }
    });

    if (shareBtn) shareBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();   // 카드(article) 클릭 → markAsRead 로 버블링 방지
      const title = document.title || "디자인 놀이터";
      if (navigator.share) {
        navigator.share({ title, url: shareUrl }).catch(() => {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl)
          .then(() => notify.toast("링크가 복사되었어요"))
          .catch(() => notify.toast("링크: " + shareUrl));
      } else {
        notify.toast("링크: " + shareUrl);
      }
    });
  }
})();
