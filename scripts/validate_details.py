#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_details.py — 상세 페이지 209개를 JSON 과 1:1 전수 대조 (V1~V36).

파서: BeautifulSoup(html.parser). 파서 반환값 그대로 비교.
html.unescape 추가 적용 금지. 줄바꿈만 CRLF·CR → LF. strip/연속공백 축약 금지.
"""

import os
import re
import sys
import glob
import json
from collections import defaultdict
from bs4 import BeautifulSoup

NEWS = "content/news"
DIST = "dist/news"
SITE = "https://kei-insu.github.io"
BASE = "/dinol-news"

POSITIONS = {
    'ux-designer': 'UX디자이너', 'ui-designer': 'UI디자이너', 'product-designer': '프로덕트디자이너',
    'service-designer': '서비스디자이너', 'brand-designer': '브랜드디자이너', 'bx-designer': 'BX디자이너',
    'graphic-designer': '그래픽디자이너', 'editorial-designer': '편집디자이너', 'motion-designer': '모션디자이너',
    'video-designer': '영상디자이너', 'illustrator': '일러스트레이터', 'art-director': '아트디렉터',
    'industrial-designer': '제품디자이너', 'space-designer': '공간디자이너', 'architect': '건축가',
    'package-designer': '패키지디자이너', 'typographer': '타이포그래퍼', 'fashion-designer': '패션디자이너',
    'design-lead': '디자인리드', 'design-manager': '디자인매니저',
}

# 유효 칩이 없을 때 표시하는 기본 칩 라벨/툴팁. src/lib/positions.ts 와 값이 같아야 한다(4-0 동기화 검사).
FALLBACK_POSITION_LABEL = '공통 참고'
FALLBACK_POSITION_TITLE = '특정 디자인 직무에 한정되지 않는 공통 참고 콘텐츠'
POSITIONS_TS = "src/lib/positions.ts"


def check_label_sync():
    """positions.ts 의 FALLBACK_POSITION_LABEL·FALLBACK_POSITION_TITLE 값이 스크립트 상수와 같은지 확인."""
    try:
        text = open(POSITIONS_TS, encoding="utf-8").read()
    except OSError as e:
        return False, f"positions.ts 읽기 실패: {e}"
    checks = [
        ("FALLBACK_POSITION_LABEL", FALLBACK_POSITION_LABEL),
        ("FALLBACK_POSITION_TITLE", FALLBACK_POSITION_TITLE),
    ]
    found = {}
    for name, expected in checks:
        m = re.search(name + r"\s*=\s*['\"](.+?)['\"]", text)
        if not m:
            return False, f"positions.ts 에서 {name} 을 찾지 못함"
        ts_val = m.group(1)
        if ts_val != expected:
            return False, f"{name} 불일치: positions.ts={ts_val!r} vs validate={expected!r}"
        found[name] = ts_val
    return True, f"LABEL={found['FALLBACK_POSITION_LABEL']!r} · TITLE={found['FALLBACK_POSITION_TITLE']!r}"


def norm(s):
    if s is None:
        return None
    return s.replace("\r\n", "\n").replace("\r", "\n")


def has_value(s):
    """섹션 렌더 여부 판정: None/빈문자열/공백만 이면 False (DetailPage 가드와 동일)."""
    return bool(s is not None and s.strip() != "")


def make_description(text, max_len=150):
    if not text:
        return None
    if len(text) <= max_len:
        return text
    s = text[:max_len]
    i = s.rfind(' ')
    return s[:i] if i >= (max_len * 7) // 10 else s


def to_paragraphs(v):
    return [p for p in re.split(r'\n\s*\n|\n', (v or '').replace('\r\n', '\n').replace('\r', '\n')) if p != '']


class R:
    def __init__(self):
        self.fail = defaultdict(list)  # code -> [(cid, detail)]

    def bad(self, code, cid, a, b):
        self.fail[code].append((cid, a, b))


def main():
    # 4-0. 명칭 상수 동기화 검사 — positions.ts 와 어긋나면 즉시 종료.
    ok_sync, sync_msg = check_label_sync()
    if not ok_sync:
        print(f"[4-0] 명칭 동기화 검사 ERROR: {sync_msg}")
        return 1
    print(f"[4-0] 명칭 동기화 검사 통과 (LABEL·TITLE): {sync_msg}")

    date_arg = None
    for a in sys.argv[1:]:
        if re.match(r'^\d{8}$', a):
            date_arg = a

    json_files = sorted(glob.glob(f"{NEWS}/*.json"))
    json_ids = {os.path.basename(p)[:-5] for p in json_files}
    det_files = glob.glob(f"{DIST}/2026/*/*.html")
    det_ids = {os.path.basename(p)[:-5] for p in det_files
               if re.match(r'^\d{8}-(ai|design)-\d{3}$', os.path.basename(p)[:-5])}

    missing = sorted(json_ids - det_ids)   # JSON 에 있는데 HTML 없음
    extra = sorted(det_ids - json_ids)     # HTML 인데 JSON 없음

    targets = sorted(json_ids & det_ids)
    if date_arg:
        targets = [c for c in targets if c.startswith(date_arg + "-")]

    r = R()
    ldjson_errors = 0
    unknown_pos = []
    crashed = []

    # V37 집합 수집기
    set_A = set()            # positions 가 실제 빈 배열인 카드
    set_B = set()            # positions 값은 있으나 유효 ID 가 하나도 없는 카드
    set_B_detail = []        # (cid, positions) — B 상세
    set_valid = set()        # 유효 직무 칩 카드
    rendered_fb = set()      # HTML 에 .detail-chip-fallback 이 렌더된 카드 (C)

    for cid in targets:
        try:
            data = json.load(open(f"{NEWS}/{cid}.json", encoding="utf-8"))
            y, m, dd = data["date"].split("-")
            html = norm(open(f"{DIST}/{y}/{m}/{cid}.html", encoding="utf-8").read())
            s = BeautifulSoup(html, "html.parser")

            def sel1(css):
                el = s.select_one(css)
                return el.get_text() if el else None

            def meta_prop(p):
                el = s.find("meta", attrs={"property": p})
                return el.get("content") if el else None

            def meta_name(n):
                el = s.find("meta", attrs={"name": n})
                return el.get("content") if el else None

            # V1 파일명 == contentId (targets 는 이미 교집합이라 항상 통과, 형식만 확인)
            if not re.match(r'^\d{8}-(ai|design)-\d{3}$', cid):
                r.bad("V1", cid, cid, "형식")

            # V2 Drawer 없음
            if s.find(id="drawer") or s.find(id="drawerOverlay") or 'id="drawer' in html:
                r.bad("V2", cid, "drawer 존재", "")
            # V3 Guestbook 없음 (gb- id/class)
            gb = [el for el in s.find_all(True)
                  if (el.get("id", "") or "").startswith("gb")
                  or any(c.startswith("gb-") for c in (el.get("class") or []))]
            if gb:
                r.bad("V3", cid, f"gb 요소 {len(gb)}개", "")

            # V4 h1 == title.kr
            h1 = sel1("h1.detail-title")
            if h1 != data["title"]["kr"]:
                r.bad("V4", cid, h1, data["title"]["kr"])
            # V5 title-en
            te = s.select_one(".detail-title-en")
            te = te.get_text() if te else None
            if data["title"]["en"] is None:
                if te is not None:
                    r.bad("V5", cid, te, "(요소 없어야)")
            else:
                if te != data["title"]["en"]:
                    r.bad("V5", cid, te, data["title"]["en"])
            # V6 source
            pub = data["source"]["publishedAt"]
            disp = ". ".join(pub.split("-")) if pub else ""
            exp_src = f'{data["source"]["name"]} · {disp}' if data["source"]["name"] else disp
            if sel1(".detail-source") != exp_src:
                r.bad("V6", cid, sel1(".detail-source"), exp_src)
            # V7 category
            if sel1(".detail-category") != data["category"]["kr"]:
                r.bad("V7", cid, sel1(".detail-category"), data["category"]["kr"])
            # V8 한 줄 요약 : .detail-summary-block 안의 .detail-summary
            sb = s.select_one(".detail-summary-block .detail-summary")
            sumtext = sb.get_text() if sb else None
            sk = data["summary"]["kr"]
            if not has_value(sk):
                if sb is not None:
                    r.bad("V8", cid, "summary 존재", "비면 없어야")
            else:
                if sumtext != sk:
                    r.bad("V8", cid, sumtext, sk)
            # V9 별점 : .detail-impact-block 안 .detail-stars 의 on/off = 5개, on == impactScore
            allstar = s.select(".detail-impact-block .detail-stars .on") \
                + s.select(".detail-impact-block .detail-stars .off")
            on = len(s.select(".detail-impact-block .detail-stars .on"))
            if len(allstar) != 5 or on != data["impactScore"]:
                r.bad("V9", cid, f"total={len(allstar)} on={on}", f"impact={data['impactScore']}")
            # V10 chips — 칩은 209개 전부에 존재(fallback 포함). 칩 텍스트는 strip 비교(4-1).
            for p in data["positions"]:
                if p not in POSITIONS:
                    unknown_pos.append((cid, p))
            exp_chips = [POSITIONS[p] for p in data["positions"] if p in POSITIONS]
            is_fallback = len(exp_chips) == 0
            if is_fallback:
                exp_chips = [FALLBACK_POSITION_LABEL]
            boxes = s.select(".detail-positions")
            box = boxes[0] if boxes else None
            chip_els = s.select(".detail-positions .detail-chip")
            actual_chips = [c.get_text(strip=True) for c in chip_els]  # 4-1 칩만 strip
            # .detail-positions 는 모든 페이지에서 정확히 1개
            if len(boxes) != 1:
                r.bad("V10", cid, f".detail-positions {len(boxes)}개", "정확히 1개")
            # 칩 텍스트·순서 일치
            if actual_chips != exp_chips:
                r.bad("V10", cid, str(actual_chips), str(exp_chips))
            # fallback 여부에 따른 detail-chip-fallback 클래스 + 접근성 속성(title·aria-label)
            fb_flags = ["detail-chip-fallback" in (c.get("class") or []) for c in chip_els]
            if is_fallback:
                if len(chip_els) != 1 or not (len(fb_flags) == 1 and fb_flags[0]):
                    r.bad("V10", cid, f"fallback 칩수={len(chip_els)} fb_flags={fb_flags}",
                          "칩 1개 + detail-chip-fallback")
                if chip_els:
                    chip = chip_els[0]
                    # ★fallback 칩에 title 속성이 없어야 함★ (툴팁 제거, aria-label 전용으로 전환)
                    if chip.has_attr("title"):
                        r.bad("V10", cid, f"fallback 칩 title 존재={chip.get('title')!r}", "title 없어야")
                    # aria-label 은 접근성용으로 계속 사용
                    if not chip.has_attr("aria-label") or chip.get("aria-label") != FALLBACK_POSITION_TITLE:
                        r.bad("V10", cid, f"aria-label={chip.get('aria-label') if chip.has_attr('aria-label') else '(없음)'!r}",
                              FALLBACK_POSITION_TITLE)
            else:
                if any(fb_flags):
                    r.bad("V10", cid, f"fb 클래스 존재 {fb_flags}", "실제 직무엔 fallback 없어야")
                # 실제 직무 칩엔 title·aria-label 이 없어야 함
                for c in chip_els:
                    if c.has_attr("title"):
                        r.bad("V10", cid, f"직무칩 title 존재={c.get('title')!r}", "title 없어야")
                    if c.has_attr("aria-label"):
                        r.bad("V10", cid, f"직무칩 aria-label 존재={c.get('aria-label')!r}", "aria-label 없어야")
            # .detail-positions 직접 자식은 detail-chip span 만 (텍스트 노드 제외)
            if box is not None:
                direct = box.find_all(recursive=False)
                invalid = [e for e in direct
                           if not (e.name == "span" and "detail-chip" in (e.get("class") or []))]
                if invalid:
                    desc = [f"{e.name}.{'.'.join(e.get('class') or [])}" for e in invalid]
                    r.bad("V10", cid, f"잘못된 직접자식 {desc}", "detail-chip span 만")
            # V37 집합 분류 (A/B/valid/C)
            _positions = data["positions"]
            _valid_ids = [i for i in _positions if i in POSITIONS]
            if not _positions:
                set_A.add(cid)
            elif not _valid_ids:
                set_B.add(cid)
                set_B_detail.append((cid, _positions))
            if _valid_ids:
                set_valid.add(cid)
            if s.select_one(".detail-chip-fallback") is not None:
                rendered_fb.add(cid)
            # V11 points
            blocks = s.select("section.detail-block")
            def block_by_h2(title):
                for b in blocks:
                    h2 = b.find("h2")
                    if h2 and h2.get_text() == title:
                        return b
                return None
            pb = block_by_h2("핵심 인사이트")
            pk = data["points"]["kr"]
            if not (isinstance(pk, list) and len(pk) > 0):
                if pb is not None:
                    r.bad("V11", cid, "points 섹션 존재", "비면 없어야")
            else:
                lis = [li.get_text() for li in pb.select("li")] if pb else None
                if lis != pk:
                    r.bad("V11", cid, str(lis), str(pk))
            # V12 designer
            db = block_by_h2("디자인 관점")
            dk = data["designer"]["kr"]
            dpars = to_paragraphs(dk)
            if not dpars:
                if db is not None:
                    r.bad("V12", cid, "designer 섹션 존재", "비면 없어야")
            else:
                ps = [p.get_text() for p in db.select("p")] if db else None
                if ps != dpars:
                    r.bad("V12", cid, str(ps), str(dpars))
            # V13 comment
            cb = block_by_h2("큐레이션 노트")
            ck = data["comment"]["kr"]
            cpars = to_paragraphs(ck)
            if not cpars:
                if cb is not None:
                    r.bad("V13", cid, "comment 섹션 존재", "비면 없어야")
            else:
                ps = [p.get_text() for p in cb.select("p")] if cb else None
                if ps != cpars:
                    r.bad("V13", cid, str(ps), str(cpars))
            # V14 recommend
            rb = block_by_h2("활용 추천")
            rk = data["recommend"]["kr"]
            if not (rk and rk.strip()):
                if rb is not None:
                    r.bad("V14", cid, "recommend 섹션 존재", "비면 없어야")
            else:
                rt = rb.find("p").get_text() if (rb and rb.find("p")) else None
                if rt != rk:
                    r.bad("V14", cid, rt, rk)
            # V15 원문 링크
            cta = s.select_one(".detail-cta")
            if not cta or cta.get("href") != data["url"] or cta.get("target") != "_blank" or not cta.get("rel"):
                r.bad("V15", cid, cta.get("href") if cta else None, data["url"])
            # V16 브리핑 링크
            back = s.select_one(".detail-back")
            exp_back = f'Dinol_news_{y}{m}{dd}.html'
            if not back or back.get("href") != exp_back:
                r.bad("V16", cid, back.get("href") if back else None, exp_back)

            # SEO
            title = s.find("title").get_text() if s.find("title") else None
            exp_title = f'{data["title"]["kr"]} — 디자인 놀이터'
            if title != exp_title:
                r.bad("V17", cid, title, exp_title)
            desc = meta_name("description")
            exp_desc = make_description(data["summary"]["kr"])
            if desc != exp_desc:
                r.bad("V18", cid, desc, exp_desc)
            can = s.find("link", rel="canonical")
            can = can.get("href") if can else None
            exp_can = f'{SITE}{BASE}/news/{y}/{m}/{cid}.html'
            if can != exp_can or "//dinol-news/" in (can or "") or "dinol-news/dinol-news/" in (can or ""):
                r.bad("V19", cid, can, exp_can)
            if meta_prop("og:url") != exp_can:
                r.bad("V20", cid, meta_prop("og:url"), exp_can)
            if meta_prop("og:type") != "article":
                r.bad("V21", cid, meta_prop("og:type"), "article")
            if meta_prop("og:title") != title:
                r.bad("V22", cid, meta_prop("og:title"), title)
            if meta_prop("og:description") != desc:
                r.bad("V23", cid, meta_prop("og:description"), desc)
            exp_img = f'{SITE}{BASE}/assets/ai-design-news.png'
            if meta_prop("og:image") != exp_img:
                r.bad("V24", cid, meta_prop("og:image"), exp_img)
            if meta_prop("og:site_name") != "디자인 놀이터" or meta_prop("og:locale") != "ko_KR":
                r.bad("V25", cid, f'{meta_prop("og:site_name")}/{meta_prop("og:locale")}', "디자인 놀이터/ko_KR")
            if meta_name("twitter:card") != "summary_large_image":
                r.bad("V26", cid, meta_name("twitter:card"), "summary_large_image")

            # JSON-LD
            lds = s.find_all("script", attrs={"type": "application/ld+json"})
            if len(lds) != 1:
                r.bad("V27", cid, f"{len(lds)}개", "1개")
                ld = None
            else:
                try:
                    ld = json.loads(lds[0].string)
                except Exception as e:
                    ld = None
                    ldjson_errors += 1
                    r.bad("V27", cid, f"파싱실패 {e}", "")
            if ld is not None:
                if ld.get("@type") != "Article":
                    r.bad("V28", cid, ld.get("@type"), "Article")
                if ld.get("headline") != data["title"]["kr"]:
                    r.bad("V29", cid, ld.get("headline"), data["title"]["kr"])
                if ld.get("description") != data["summary"]["kr"]:
                    r.bad("V30", cid, ld.get("description"), data["summary"]["kr"])
                if ld.get("datePublished") != data["date"]:
                    r.bad("V31", cid, ld.get("datePublished"), data["date"])
                if ld.get("mainEntityOfPage") != exp_can:
                    r.bad("V32", cid, ld.get("mainEntityOfPage"), exp_can)
                cit = ld.get("citation", {})
                if cit.get("url") != data["url"]:
                    r.bad("V33", cid, cit.get("url"), data["url"])
                if cit.get("datePublished") != data["source"]["publishedAt"]:
                    r.bad("V34", cid, cit.get("datePublished"), data["source"]["publishedAt"])
                cpub = cit.get("publisher", {}).get("name")
                if cpub != data["source"]["name"]:
                    r.bad("V35", cid, cpub, data["source"]["name"])

            # V36 직계 자식 순서 "완전 일치" (부분수열 금지)
            expected = ["head"]
            if has_value(data["summary"]["kr"]):
                expected.append("summary")
            expected.append("positions")  # ★조건 없이 항상★ (fallback 칩 포함)
            if data["points"]["kr"]:
                expected.append("points")
            expected.append("impact")  # 항상 존재
            if has_value(data["designer"]["kr"]):
                expected.append("designer")
            if has_value(data["recommend"]["kr"]):
                expected.append("recommend")
            if has_value(data["comment"]["kr"]):
                expected.append("comment")
            expected.append("actions")  # 항상 존재

            article = s.select_one("article.detail")
            actual_tokens = []
            if article is None:
                r.bad("V36", cid, "article.detail 없음", str(expected))
            else:
                for child in article.find_all(recursive=False):  # 텍스트 노드 제외
                    classes = set(child.get("class") or [])
                    if "detail-head" in classes:
                        token = "head"
                    elif "detail-summary-block" in classes:
                        token = "summary"
                    elif "detail-positions" in classes:
                        token = "positions"
                    elif "detail-points-block" in classes:
                        token = "points"
                    elif "detail-impact-block" in classes:
                        token = "impact"
                    elif "detail-designer-block" in classes:
                        token = "designer"
                    elif "detail-recommend-block" in classes:
                        token = "recommend"
                    elif "detail-note" in classes:
                        token = "comment"
                    elif "detail-actions" in classes:
                        token = "actions"
                    else:
                        token = f"unknown:{','.join(sorted(classes)) or child.name}"
                    actual_tokens.append(token)
                if actual_tokens != expected:
                    r.bad("V36", cid, str(actual_tokens), str(expected))
        except Exception as e:
            crashed.append((cid, f"{type(e).__name__}: {e}"))

    # 출력
    print(f"검사 상세 페이지 : {len(targets)}")
    print(f"누락(JSON O·HTML X): {len(missing)}  {missing if missing else ''}")
    print(f"초과(HTML O·JSON X): {len(extra)}  {extra if extra else ''}")
    print(f"JSON-LD 파싱 오류 : {ldjson_errors}")
    print(f"알 수 없는 position ID : {len(unknown_pos)}건  {unknown_pos[:5] if unknown_pos else ''}")
    print()
    print("── 항목별 불일치 (V1~V36, 전부 0이어야) ──")
    total = 0
    for i in range(1, 37):
        code = f"V{i}"
        n = len(r.fail.get(code, []))
        total += n
        mark = "" if n == 0 else "  ← 불일치"
        print(f"  {code}: {n}{mark}")
        for cid, a, b in r.fail.get(code, [])[:3]:
            print(f"      {cid}\n        HTML[:80]={str(a)[:80]!r}\n        JSON[:80]={str(b)[:80]!r}")
    print()
    print(f"불일치 합계: {total}")

    # ── V37: fallback contentId 집합 비교 (개수 아닌 집합) ──
    expected_fb = set_A | set_B          # A ∪ B
    missing_fb = expected_fb - rendered_fb   # 기대엔 있는데 렌더 안 됨
    extra_fb = rendered_fb - expected_fb     # 렌더됐는데 기대엔 없음
    v37_set_ok = (rendered_fb == expected_fb)
    v37_b_ok = (len(set_B) == 0)
    print()
    print("── V37: 기본 칩(fallback) 집합 검증 ──")
    print(f"  빈 positions 카드 (A)       : {len(set_A)}")
    print(f"  유효 직무 카드              : {len(set_valid)}")
    print(f"  fallback 렌더 카드 (C)      : {len(rendered_fb)}   (A∪B={len(expected_fb)} 와 같아야)")
    print(f"  미등록 ID fallback (B)      : {len(set_B)}   (★0 이어야 함)")
    print(f"  집합 일치 (C == A∪B)        : {v37_set_ok}")
    if not v37_set_ok:
        print(f"    누락(기대O 렌더X): {sorted(missing_fb)}")
        print(f"    과잉(렌더O 기대X): {sorted(extra_fb)}")
    if not v37_b_ok:
        print(f"  ★B 상세 (미등록 ID 로 fallback 된 카드):")
        for cid, pos in set_B_detail:
            print(f"    {cid}: positions={pos}")

    if crashed:
        print(f"★검사 중 예외 {len(crashed)}건:")
        for cid, e in crashed:
            print(f"  {cid}: {e}")
    else:
        print("★예외 없이 전수 완주")
    ok = (total == 0 and not missing and not extra and ldjson_errors == 0
          and not unknown_pos and not crashed and v37_set_ok and v37_b_ok)
    print("\n결과:", "PASS ✅" if ok else "FAIL ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
