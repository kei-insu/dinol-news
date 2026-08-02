// ============================================================
// rules.test.mjs — firestore.rules 좋아요 규칙 11건 자동 테스트
//   @firebase/rules-unit-testing + Firestore 에뮬레이터.
//   실행: npm run emulators:rules  (firebase emulators:exec --only firestore)
//   ※ 서버(규칙)가 "막는지"만 본다. 클라이언트가 "안 보내는지"는 likes.test.mjs.
// ============================================================
import { initializeTestEnvironment, assertSucceeds, assertFails } from "@firebase/rules-unit-testing";
import { doc, setDoc, updateDoc, deleteDoc } from "firebase/firestore";
import { readFileSync } from "node:fs";

const PROJECT = "dinol-news-rules-test";
const VALID = "20260710-design-003";
const results = [];
const rec = (name, ok, extra = "") => results.push([ok, name, extra]);

let env;

// 비정상 사전 데이터는 규칙을 우회해서 심는다.
async function seed(id, data) {
  await env.withSecurityRulesDisabled(async (admin) => {
    await setDoc(doc(admin.firestore(), "likes", id), data);
  });
}
async function pass(name, factory) {
  try { await assertSucceeds(factory()); rec(name, true); }
  catch (e) { rec(name, false, e.message); }
}
async function fail(name, factory) {
  try { await assertFails(factory()); rec(name, true); }
  catch (e) { rec(name, false, e.message); }
}

async function main() {
  env = await initializeTestEnvironment({
    projectId: PROJECT,
    firestore: {
      rules: readFileSync(new URL("../firestore.rules", import.meta.url), "utf8"),
      host: "127.0.0.1",
      port: 8080,
    },
  });
  const db = env.unauthenticatedContext().firestore();
  const L = (id) => doc(db, "likes", id);

  // 1. create (count 1, url) → 허용
  await env.clearFirestore();
  await pass("1 create(count1,url) 허용", () => setDoc(L(VALID), { count: 1, url: "https://a.com/x" }));

  // 2. 같은 문서 update 0→1, 1→0 → 허용
  await env.clearFirestore();
  await seed(VALID, { count: 0, url: "https://a.com/x" });
  await pass("2a update 0→1 허용", () => updateDoc(L(VALID), { count: 1 }));
  await pass("2b update 1→0 허용", () => updateDoc(L(VALID), { count: 0 }));

  // 3. count 1→10 → 차단 (|Δ| != 1)
  await env.clearFirestore();
  await seed(VALID, { count: 1, url: "https://a.com/x" });
  await fail("3 update 1→10 차단", () => updateDoc(L(VALID), { count: 10 }));

  // 4. update 시 {count,url} → 차단 (affectedKeys 에 url)
  await env.clearFirestore();
  await seed(VALID, { count: 1, url: "https://a.com/x" });
  await fail("4 update {count,url} 차단", () => updateDoc(L(VALID), { count: 2, url: "https://a.com/y" }));

  // 5. create 시 {count,url,foo} → 차단 (keys.hasOnly 위반)
  await env.clearFirestore();
  await fail("5 create {count,url,foo} 차단", () => setDoc(L(VALID), { count: 1, url: "https://a.com/x", foo: 1 }));

  // 6. 문서 ID 접두어형 (20260710_https___...) create → 차단
  await env.clearFirestore();
  await fail("6 id 접두어형 create 차단",
    () => setDoc(L("20260710_https___a_com_x"), { count: 1, url: "https://a.com/x" }));

  // 7. 문서 ID 무접두어형 (https___...) create → 차단
  await env.clearFirestore();
  await fail("7 id 무접두어형 create 차단",
    () => setDoc(L("https___a_com_x"), { count: 1, url: "https://a.com/x" }));

  // 8. delete → 차단
  await env.clearFirestore();
  await seed(VALID, { count: 1, url: "https://a.com/x" });
  await fail("8 delete 차단", () => deleteDoc(L(VALID)));

  // 9. id 형식 위반: 8자리 아님 / 순번 3자리 아님 → 차단
  await env.clearFirestore();
  await fail("9a id 2026071-ai-001 차단", () => setDoc(L("2026071-ai-001"), { count: 1, url: "https://a.com/x" }));
  await fail("9b id 20260710-ai-0001 차단", () => setDoc(L("20260710-ai-0001"), { count: 1, url: "https://a.com/x" }));

  // 10. count:"3"(문자열) 문서에 update → 차단 (resource.data.count is int 실패)
  await env.clearFirestore();
  await seed(VALID, { count: "3", url: "https://a.com/x" });
  await fail("10 count 문자열 문서 update 차단", () => updateDoc(L(VALID), { count: 4 }));

  // 11. count:0 문서에 -1 update → 차단 (count >= 0 실패)
  await env.clearFirestore();
  await seed(VALID, { count: 0, url: "https://a.com/x" });
  await fail("11 count 0 → -1 update 차단", () => updateDoc(L(VALID), { count: -1 }));

  await env.cleanup();

  // 출력
  const passed = results.filter(([ok]) => ok).length;
  console.log("\nFirestore 규칙 테스트 (likes) 13건\n" + "=".repeat(52));
  for (const [ok, name, extra] of results)
    console.log(`  [${ok ? "PASS" : "FAIL"}] ${name}${ok ? "" : "  ← " + extra}`);
  console.log("=".repeat(52));
  console.log(`총 ${passed}/${results.length} PASS`);
  process.exit(passed === results.length ? 0 : 1);
}

main().catch((e) => { console.error(e); process.exit(1); });
