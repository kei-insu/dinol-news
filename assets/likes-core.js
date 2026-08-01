// ============================================================
// likes-core.js — 좋아요 도메인 로직 (Firebase·DOM 의존 없음)
//   · 트랜잭션 판단·마커 승계·stale 후처리를 모두 이 계층이 소유한다.
//   · 외부 의존(Firestore/localStorage/알림)은 전부 주입받는다 → mock 으로 테스트.
//   · CDN import 금지. 브라우저(likes.js)와 Node 테스트(likes.test.mjs) 양쪽에서 import.
// ============================================================

// ── 예외 매핑 30건 (D1-E: 무접두어 legacy 키를 쓰는 contentId) ──────────
// 산출: likes_dump.json + content/news/*.json, 무접두어 중 265장 exact 후보 1개.
// 검증: 30건 · unique 30/30 · 양방향 유일성 · A(184)와 contentId·legacyKey 중복 0.
// JS 객체 리터럴로 내장(fetch·import 금지).
export const EXCEPTION_MAP = {
  "20260701-design-003": "https___www_newsis_com_view_NISX20260701_0003690673",
  "20260704-design-002": "https___www_designweek_co_uk_xtool_launches_worlds_first_4_in_1_omni_printer_and_expands_european_operations_",
  "20260706-ai-001": "https___www_aitimes_com_news_articleView_html_idxno_212315",
  "20260706-ai-002": "https___www_aitimes_kr_news_articleView_html_idxno_40829",
  "20260706-ai-003": "https___www_mediatoday_co_kr_news_articleView_html_idxno_335476",
  "20260706-ai-004": "https___www_axios_com_2026_07_03_anthropic_ai_models_revived_behind_the_scenes",
  "20260706-ai-005": "https___www_figma_com_blog_config_2026_recap_",
  "20260706-design-001": "https___theladylearner_com_3513_",
  "20260706-design-002": "https___www_dezeen_com_2026_07_01_dezeen_asus_ppa_awards_win_design_you_can_feel_exhibition_",
  "20260706-design-003": "https___www_dezeen_com_2026_06_15_zha_zaha_hadid_architects_rebrand_patrik_schumacher_",
  "20260707-ai-001": "https___www_aitimes_kr_news_articleView_html_idxno_40833",
  "20260707-ai-002": "https___www_aitimes_kr_news_articleView_html_idxno_40737",
  "20260707-ai-003": "https___news_un_org_en_story_2026_07_1167862",
  "20260707-ai-004": "https___www_buildfastwithai_com_blogs_ai_news_today_july_6_2026",
  "20260707-design-001": "https___www_yankodesign_com_2026_07_03_frank_gehrys_final_gift_to_abu_dhabi_is_a_building_that_moves_like_music_",
  "20260707-design-002": "https___www_yankodesign_com_2026_07_04_the_kneeling_chair_from_1979_finally_gets_its_color_moment_",
  "20260707-design-003": "https___www_yankodesign_com_2026_07_03_these_ceramics_look_hand_drawn_in_black_ink_but_theyre_actually_porcelain_pretending_to_be_paper_",
  "20260707-design-004": "https___www_yankodesign_com_2026_07_04_the_air_purifier_that_rolls_toward_smoke_before_it_fills_the_room_",
  "20260708-ai-001": "https___www_aitimes_com_news_articleView_html_idxno_212506",
  "20260708-ai-002": "https___zdnet_co_kr_view__no_20260707102607",
  "20260708-ai-003": "https___news_un_org_en_story_2026_07_1167873",
  "20260708-ai-004": "https___techcrunch_com_2026_07_06_vercel_ceo_guillermo_rauch_on_the_fight_to_split_off_models_from_agents_",
  "20260708-design-001": "https___www_dezeen_com_2026_07_07_office_to_residential_conversion_building_at_risk_of_collapse_in_new_york_",
  "20260708-design-002": "https___www_yankodesign_com_2026_07_07_the_8_best_tech_gadgets_of_july_2026_",
  "20260708-design-004": "https___www_core77_com_posts_144609_Core77_Weekly_Roundup_6_29_26_to_7_2_26",
  "20260709-ai-001": "https___www_aitimes_com_news_articleView_html_idxno_212555",
  "20260709-ai-002": "https___www_inven_co_kr_webzine_news__news_318233",
  "20260709-ai-003": "https___www_techtimes_com_articles_319766_20260706_itu_ai_summit_day_zero_what_new_44_member_un_commission_can_cannot_do_htm",
  "20260709-ai-004": "https___techcrunch_com_2026_07_08_these_ai_startups_are_growing_revenue_at_faster_and_faster_rates_",
  "20260709-design-004": "https___news_seoul_go_kr_culture_archives_533444",
};

// legacy localStorage 키 계산. 예외 매핑에 있으면 그 키(무접두어)를 우선한다.
export function legacyKeyOf(contentId, sourceUrl) {
  if (Object.prototype.hasOwnProperty.call(EXCEPTION_MAP, contentId)) {
    return EXCEPTION_MAP[contentId];
  }
  const date = contentId.slice(0, 8);
  const slug = sourceUrl.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 280) || "x";
  return date + "_" + slug;
}

const newKeyOf = (cid) => "dinol_liked_" + cid;
const markerKeyOf = (cid) => "dinol_like_migrated_" + cid;

// 오류 상태 코드 — likes.js 가 UI 문구를 결정할 때 참조.
export const PERMISSION_DENIED = "permission-denied";

// ── 코어 팩토리 ────────────────────────────────────────────
// 주입: firestore.getLike(id) / firestore.runTransaction(handler),
//       storage.get/set/remove, notify.toast(msg)
export function createLikesCore({ firestore, storage, notify }) {
  // storage.get 은 null/undefined 를 "없음" 으로 취급.
  const has = (k) => {
    const v = storage.get(k);
    return v !== null && v !== undefined;
  };

  // ── 체크리스트 3: 마커는 실제 legacy 승계 시에만 저장 ──
  // 조회 순서
  //  1) 신규 키 있음            → 현재 상태 사용 · 마커 저장 안 함
  //  2) 신규 없음 + 마커 있음    → legacy 재조회 금지 (해제 상태 유지)
  //  3) 신규 없음 + 마커 없음    → legacy 확인
  //       legacy=="1" → 신규 + 마커 함께 저장(승계) · 아니면 아무것도 저장 안 함
  // ★승계는 Firestore 를 건드리지 않는다(localStorage 만).★
  function resolveInitial(contentId, sourceUrl) {
    const nk = newKeyOf(contentId);
    const mk = markerKeyOf(contentId);

    if (has(nk)) {
      return { liked: storage.get(nk) === "1" };   // (1) 마커 저장 안 함
    }
    if (has(mk)) {
      return { liked: false };                      // (2) legacy 재조회 금지
    }
    const lk = "dinol_liked_" + legacyKeyOf(contentId, sourceUrl);
    if (storage.get(lk) === "1") {                  // (3) 승계
      storage.set(nk, "1");
      storage.set(mk, "1");
      return { liked: true };
    }
    return { liked: false };                         // 신규 사용자 → 마커 생성 안 함
  }

  // 초기 표시용 카운트 로드(읽기). 실패해도 0 으로 표시(초기화 중단 없음).
  async function loadCount(contentId) {
    try {
      const snap = await firestore.getLike(contentId);
      return snap && snap.exists ? snap.count : 0;
    } catch (e) {
      return 0;
    }
  }

  // ── 토글: 트랜잭션 판단은 전적으로 core 소유 ──
  // 체크리스트 4: 문서 없음·count===0 취소 시 createLike/updateLikeCount 를 호출조차 하지 않는다.
  // runTransaction 의 거부(permission-denied 등)는 상위(likes.js)로 전파 → 오류 UI.
  async function toggle(contentId, sourceUrl, { willLike, lastCount }) {
    const result = await firestore.runTransaction(async (tx) => {
      const snap = await tx.getLike(contentId);

      if (!snap.exists) {
        if (!willLike) {
          return { status: "stale-local-state" };            // 호출 없음
        }
        tx.createLike(contentId, { count: 1, url: sourceUrl });
        return { status: "created", count: 1 };
      }

      const current = snap.count;

      if (!willLike && current === 0) {
        return { status: "stale-local-state" };              // 호출 없음
      }

      const next = current + (willLike ? 1 : -1);
      tx.updateLikeCount(contentId, next);                   // url 안 씀
      return { status: "updated", count: next };
    });

    const nk = newKeyOf(contentId);

    if (result.status === "created" || result.status === "updated") {
      if (willLike) storage.set(nk, "1");
      else storage.remove(nk);                                // 마커·legacy 유지
      return { liked: willLike, count: result.count, status: result.status };
    }

    // ── stale 후처리 (정상·stale 공통 취소 경로) ──
    // 1) 쓰기 없이 종료 → 2) getLike 재조회 → 3) 있으면 그 count·없으면 0
    // 7) 재조회 실패 시 마지막 성공 count 유지 · 6) permission-denied 안내 안 함
    let count = lastCount;
    try {
      const snap = await firestore.getLike(contentId);
      count = snap && snap.exists ? snap.count : 0;
    } catch (e) {
      count = lastCount;                                      // 마지막 성공 count 유지
    }
    storage.remove(nk);                                       // 해제; 마커·legacy 유지
    return { liked: false, count, status: "stale-local-state" };
  }

  return { resolveInitial, loadCount, toggle, legacyKeyOf, newKeyOf, markerKeyOf, notify };
}
