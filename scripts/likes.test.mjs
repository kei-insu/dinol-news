// ============================================================
// likes.test.mjs — 클라이언트 도메인 테스트 5건 (mock 주입, Emulator·브라우저 불필요)
//   likes-core.js 만 import. 어댑터 호출 횟수를 계측해 판정한다.
//   실행: node scripts/likes.test.mjs
// ============================================================
import { createLikesCore, legacyKeyOf } from "../assets/likes-core.js";

let passed = 0, failed = 0;
const results = [];
function ok(name, cond, extra = "") {
  results.push([cond, name, extra]);
  if (cond) passed++; else failed++;
}

// ── mock 저장소 ──
function makeStorage(initial = {}) {
  const m = new Map(Object.entries(initial));
  return {
    get: (k) => (m.has(k) ? m.get(k) : null),
    set: (k, v) => m.set(k, String(v)),
    remove: (k) => m.delete(k),
    _has: (k) => m.has(k),
    _get: (k) => (m.has(k) ? m.get(k) : null),
    _map: m,
  };
}

// ── mock Firestore (어댑터 호출 계측) ──
// doc: null(문서없음) 또는 { count }. failStandaloneAfterTx: 트랜잭션 이후 단발 getLike 만 reject.
function makeFirestore({ doc = null, failStandaloneAfterTx = false } = {}) {
  const calls = { getLike: 0, txGetLike: 0, createLike: 0, updateLikeCount: 0, runTransaction: 0 };
  let current = doc ? { count: doc.count } : null;
  let txDone = false;
  return {
    calls,
    _current: () => current,
    async getLike(id) {
      calls.getLike++;
      if (failStandaloneAfterTx && txDone) throw new Error("standalone getLike fail (후속만 실패)");
      return current ? { exists: true, count: current.count } : { exists: false };
    },
    runTransaction: async (handler) => {
      calls.runTransaction++;
      const tx = {
        async getLike(id) { calls.txGetLike++; return current ? { exists: true, count: current.count } : { exists: false }; },
        createLike(id, data) { calls.createLike++; current = { count: data.count }; },
        updateLikeCount(id, count) { calls.updateLikeCount++; current = { count }; },
      };
      const r = await handler(tx);
      txDone = true;
      return r;
    },
  };
}

function makeNotify() {
  const msgs = [];
  return { toast: (m) => msgs.push(m), _msgs: msgs };
}

const CID = "20260710-ai-001";
const URL = "https://example.com/a";
const NK = "dinol_liked_" + CID;
const MK = "dinol_like_migrated_" + CID;
const LK = "dinol_liked_" + legacyKeyOf(CID, URL);

// ════════════════════════════════════════════════════════════
// 1. legacy 승계: legacy "1" · 신규·마커 없음
//    → 신규 "1" + 마커 "1" · createLike 0 · updateLikeCount 0
// ════════════════════════════════════════════════════════════
{
  const storage = makeStorage({ [LK]: "1" });
  const firestore = makeFirestore({ doc: null });
  const core = createLikesCore({ firestore, storage, notify: makeNotify() });
  const st = core.resolveInitial(CID, URL);
  ok("T1 승계: liked=true", st.liked === true);
  ok("T1 신규키 저장됨 '1'", storage._get(NK) === "1", `NK=${storage._get(NK)}`);
  ok("T1 마커 저장됨 '1'", storage._get(MK) === "1", `MK=${storage._get(MK)}`);
  ok("T1 legacy 유지", storage._get(LK) === "1");
  ok("T1 createLike 0", firestore.calls.createLike === 0, `=${firestore.calls.createLike}`);
  ok("T1 updateLikeCount 0", firestore.calls.updateLikeCount === 0, `=${firestore.calls.updateLikeCount}`);
  ok("T1 트랜잭션 0(승계는 Firestore 미접근)", firestore.calls.runTransaction === 0);
}

// ════════════════════════════════════════════════════════════
// 2. 승계 후 취소 → 재초기화
//    → 신규 제거 · 마커 유지 · legacy 유지 · 다시 좋아요 되지 않음
// ════════════════════════════════════════════════════════════
{
  const storage = makeStorage({ [NK]: "1", [MK]: "1", [LK]: "1" });
  const firestore = makeFirestore({ doc: { count: 1 } });  // 문서 존재 count 1
  const core = createLikesCore({ firestore, storage, notify: makeNotify() });
  // 취소(willLike=false): 문서 count1 → updated 0 · 신규 제거
  const r = await core.toggle(CID, URL, { willLike: false, lastCount: 1 });
  ok("T2 취소 updated", r.status === "updated" && r.count === 0, `status=${r.status} count=${r.count}`);
  ok("T2 신규 제거됨", !storage._has(NK));
  ok("T2 마커 유지", storage._get(MK) === "1");
  ok("T2 legacy 유지", storage._get(LK) === "1");
  // 재초기화 → 마커 존재 → legacy 재조회 금지 → liked false
  const st2 = core.resolveInitial(CID, URL);
  ok("T2 재초기화 liked=false (다시 좋아요 안 됨)", st2.liked === false);
  ok("T2 재초기화 후에도 신규 미생성", !storage._has(NK));
}

// ════════════════════════════════════════════════════════════
// 3. 문서 없음 + 로컬 좋아요 → 취소
//    → createLike 0 · updateLikeCount 0 · 재조회 후 해제 · permission-denied 안내 없음
// ════════════════════════════════════════════════════════════
{
  const storage = makeStorage({ [NK]: "1" });
  const firestore = makeFirestore({ doc: null });  // 문서 없음
  const notify = makeNotify();
  const core = createLikesCore({ firestore, storage, notify });
  const r = await core.toggle(CID, URL, { willLike: false, lastCount: 1 });
  ok("T3 stale 판정", r.status === "stale-local-state", `status=${r.status}`);
  ok("T3 createLike 0", firestore.calls.createLike === 0);
  ok("T3 updateLikeCount 0", firestore.calls.updateLikeCount === 0);
  ok("T3 재조회 발생(standalone getLike≥1)", firestore.calls.getLike >= 1, `=${firestore.calls.getLike}`);
  ok("T3 해제 liked=false", r.liked === false);
  ok("T3 count 0(문서없음 재조회)", r.count === 0, `count=${r.count}`);
  ok("T3 신규 제거", !storage._has(NK));
  ok("T3 permission-denied 안내 없음", notify._msgs.length === 0, `msgs=${JSON.stringify(notify._msgs)}`);
}

// ════════════════════════════════════════════════════════════
// 4. count 0 문서 + 로컬 좋아요 → 취소
//    → createLike 0 · updateLikeCount 0 · 신규 제거 · 마커 유지 · count 0
// ════════════════════════════════════════════════════════════
{
  const storage = makeStorage({ [NK]: "1", [MK]: "1", [LK]: "1" });
  const firestore = makeFirestore({ doc: { count: 0 } });
  const core = createLikesCore({ firestore, storage, notify: makeNotify() });
  const r = await core.toggle(CID, URL, { willLike: false, lastCount: 0 });
  ok("T4 stale 판정(count0 취소)", r.status === "stale-local-state", `status=${r.status}`);
  ok("T4 createLike 0", firestore.calls.createLike === 0);
  ok("T4 updateLikeCount 0", firestore.calls.updateLikeCount === 0);
  ok("T4 신규 제거", !storage._has(NK));
  ok("T4 마커 유지", storage._get(MK) === "1");
  ok("T4 legacy 유지", storage._get(LK) === "1");
  ok("T4 count 0", r.count === 0, `count=${r.count}`);
}

// ════════════════════════════════════════════════════════════
// 5. stale 반환 직후 후속 getLike 만 실패
//    → stale 판정 성공 · 쓰기 0 · 마지막 성공 count 유지 · 해제만 반영 · 상위 미중단
// ════════════════════════════════════════════════════════════
{
  const storage = makeStorage({ [NK]: "1" });
  const firestore = makeFirestore({ doc: null, failStandaloneAfterTx: true });  // 문서없음 + 후속 단발 getLike reject
  const notify = makeNotify();
  const core = createLikesCore({ firestore, storage, notify });
  let threw = false, r = null;
  try {
    r = await core.toggle(CID, URL, { willLike: false, lastCount: 5 });  // 마지막 성공 count=5
  } catch (e) { threw = true; }
  ok("T5 toggle 정상 반환(상위 초기화 미중단)", threw === false);
  ok("T5 stale 판정 성공", r && r.status === "stale-local-state", `status=${r && r.status}`);
  ok("T5 쓰기 0 (create+update)", firestore.calls.createLike === 0 && firestore.calls.updateLikeCount === 0);
  ok("T5 후속 단발 getLike 시도됨", firestore.calls.getLike >= 1);
  ok("T5 마지막 성공 count 유지(5)", r && r.count === 5, `count=${r && r.count}`);
  ok("T5 해제 반영 liked=false", r && r.liked === false);
  ok("T5 신규 제거", !storage._has(NK));
  ok("T5 permission-denied 안내 없음", notify._msgs.length === 0);
}

// ── 출력 ──
console.log("\n클라이언트 좋아요 테스트 (likes-core.js · mock)\n" + "=".repeat(52));
for (const [cond, name, extra] of results) {
  console.log(`  [${cond ? "PASS" : "FAIL"}] ${name}${cond ? "" : "  ← " + extra}`);
}
console.log("=".repeat(52));
console.log(`총 ${passed}/${passed + failed} PASS`);
process.exit(failed === 0 ? 0 : 1);
