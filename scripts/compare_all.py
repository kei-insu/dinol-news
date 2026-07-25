#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 실행 전: pip install -r requirements.txt
"""
25일치 브리핑을 두 축으로 대조한다.

[축 1] 생성본 HTML ↔ JSON 정본   (가장 중요)
    - 209장 전 카드에 대해 J1~J9 검사
    - 속성 존재 여부(has_attr)와 값(get)을 분리해서 판정 (a/b/c 규칙)

[축 2] 생성본 HTML ↔ 원본 HTML
    - 날짜별 PASS / EXPECTED DIFF / FAIL 3등급

비교 규칙 (두 축 공통):
    - 양쪽을 같은 파서(BeautifulSoup, html.parser)로 파싱
    - 파서가 반환한 속성값 그대로 비교. html.unescape 추가 적용 금지
    - 줄바꿈만 정규화: CRLF·CR → LF. strip / 연속공백 축약 금지
    - 카드 식별은 섹션 + DOM 순번 (card-title 로 매핑 확인)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "content" / "news"
ORIG_DIR = ROOT / "news" / "2026" / "07"
GEN_DIR = ROOT / "dist" / "news" / "2026" / "07"

SEC_NAME = {"ai": "AI", "design": "Design"}

# ── D3: EN 슬롯을 새로 채운 13개 필드 (date, section, index0, field) ──
D3_LIST = [
    ("2026-07-20", "ai", 0, "comment"),
    ("2026-07-20", "ai", 3, "comment"),
    ("2026-07-20", "design", 0, "comment"),
    ("2026-07-20", "design", 3, "comment"),
    ("2026-07-25", "ai", 1, "summary"),
    ("2026-07-25", "ai", 1, "points"),
    ("2026-07-25", "ai", 3, "summary"),
    ("2026-07-25", "ai", 3, "points"),
    ("2026-07-25", "ai", 3, "recommend"),
    ("2026-07-25", "design", 1, "points"),
    ("2026-07-25", "design", 1, "recommend"),
    ("2026-07-25", "design", 3, "points"),
    ("2026-07-25", "design", 3, "recommend"),
]
D3_SET = set(D3_LIST)

# ── D6: 원본이 반쯤 만든 EN 카드가 있는 날짜 ──
D6_DATES = {"2026-07-03", "2026-07-24"}

# ── D7: 원본에만 있는 잔재(legacy) 속성 (사전조사 D1~D6 이 놓친 카테고리) ──
#   data-impact / data-impact-kr : 텍스트 임팩트 문구. JSON 스키마에 없고 어떤 JS 도 읽지 않음
#   data-title-kr                : 국문 제목 중복. 드로어 JS 가 `d.titleKr || baseTitle` 로
#                                  card-title 텍스트(=title.kr)에 폴백하므로 값 동일 → 무해
D7_ORIG_ONLY = {"data-impact", "data-impact-kr", "data-title-kr"}

FIELD_ATTR = {
    "summary": "data-summary",
    "points": "data-points",
    "designer": "data-designer",
    "recommend": "data-recommend",
    "comment": "data-comment",
}


def norm_nl(s):
    if s is None:
        return None
    return s.replace("\r\n", "\n").replace("\r", "\n")


def load_html(p):
    raw = norm_nl(p.read_text(encoding="utf-8"))
    return BeautifulSoup(raw, "html.parser")


def sec_cards(soup):
    """섹션 이름 -> DOM 순번의 카드 리스트"""
    out = {}
    for sec in soup.find_all("div", class_="section"):
        h2 = sec.find("h2")
        name = h2.get_text() if h2 else "?"
        out[name] = sec.find_all("a", class_="card")
    return out


def all_cards(soup):
    return soup.find_all("a", class_="card")


def thumb_grad(card):
    thumb = card.find("div", class_="thumb")
    if not thumb:
        return None
    for c in thumb.get("class", []):
        if c.startswith("g-"):
            return c
    return None


def thumb_label(card):
    el = card.find("span", class_="thumb-label")
    return el.get_text() if el else None


def has_en_badge(card):
    return card.find("span", class_="thumb-en") is not None


def card_title(card):
    el = card.find("div", class_="card-title")
    return el.get_text() if el else None


def card_source(card):
    el = card.find("div", class_="card-source")
    return el.get_text() if el else None


def data_names(card):
    return {k for k in card.attrs if k.startswith("data-")}


# ─────────────────────────────────────────────────────────
# JSON 정본 로드
# ─────────────────────────────────────────────────────────
def load_json_cards():
    by_date = defaultdict(lambda: {"ai": [], "design": []})
    for p in sorted(JSON_DIR.glob("*.json")):
        j = json.loads(p.read_text(encoding="utf-8"))
        by_date[j["date"]][j["section"]].append(j)
    for d in by_date:
        for s in ("ai", "design"):
            by_date[d][s].sort(key=lambda c: c["order"])
    return by_date


def expected_attrs(j):
    """Card.astro 로직을 그대로 재현한 기대 속성 dict.
    값이 None 이면 '속성이 없어야 정상'을 뜻한다."""
    isEn = j["isEn"]

    def pick(pair):
        return pair["en"] if isEn else pair["kr"]

    exp = {}
    exp["data-category"] = norm_nl(j["category"]["kr"])
    exp["data-summary"] = norm_nl(pick(j["summary"]))
    exp["data-points"] = "|".join(j["points"]["en"] if isEn else j["points"]["kr"])
    exp["data-designer"] = norm_nl(pick(j["designer"]))
    exp["data-impact-score"] = "null" if j["impactScore"] is None else str(j["impactScore"])
    exp["data-recommend"] = norm_nl(pick(j["recommend"]))
    exp["data-comment"] = norm_nl(pick(j["comment"]))
    # data-points 는 join 결과라 항상 문자열(빈 배열이면 ""), 절대 None 아님
    exp["data-points"] = norm_nl(exp["data-points"])
    if isEn:
        exp["data-summary-kr"] = norm_nl(j["summary"]["kr"])
        exp["data-points-kr"] = norm_nl("|".join(j["points"]["kr"]))
        exp["data-designer-kr"] = norm_nl(j["designer"]["kr"])
        exp["data-recommend-kr"] = norm_nl(j["recommend"]["kr"])
        exp["data-comment-kr"] = norm_nl(j["comment"]["kr"])
        exp["data-title-en"] = norm_nl(j["title"]["en"])
    else:
        exp["data-summary-kr"] = None
        exp["data-points-kr"] = None
        exp["data-designer-kr"] = None
        exp["data-recommend-kr"] = None
        exp["data-comment-kr"] = None
        exp["data-title-en"] = None
    return exp


# EN 카드에서 반드시 존재해야 하는 6속성 (rule b)
EN_MUST_EXIST = [
    "data-summary-kr", "data-points-kr", "data-designer-kr",
    "data-recommend-kr", "data-comment-kr", "data-title-en",
]


def axis1():
    print("=" * 60)
    print("[축 1] 생성본 HTML ↔ JSON 정본 대조 (209장)")
    print("=" * 60)
    by_date = load_json_cards()

    # J 항목별 불일치 카운트
    jfail = {f"J{i}": 0 for i in range(1, 10)}
    jdetails = defaultdict(list)   # J코드 -> [상세]
    abc_violations = []            # (card_id, attr, kind, gen, exp)
    checked = 0

    for date in sorted(by_date):
        y, m, d = date.split("-")
        gen_p = GEN_DIR / f"Dinol_news_{y}{m}{d}.html"
        if not gen_p.is_file():
            jdetails["J0"].append(f"{date}: 생성 HTML 없음 {gen_p}")
            continue
        gsecs = sec_cards(load_html(gen_p))
        for sec in ("ai", "design"):
            jcards = by_date[date][sec]
            gcards = gsecs.get(SEC_NAME[sec], [])
            if len(jcards) != len(gcards):
                jdetails["J0"].append(
                    f"{date} {sec}: JSON {len(jcards)} vs 생성 {len(gcards)} 카드수 불일치")
            for idx, j in enumerate(jcards):
                if idx >= len(gcards):
                    break
                g = gcards[idx]
                cid = j["contentId"]
                checked += 1
                exp = expected_attrs(j)

                # J6 card-title == title.kr  (매핑 확인 겸)
                gt = card_title(g)
                if gt != norm_nl(j["title"]["kr"]):
                    jfail["J6"] += 1
                    jdetails["J6"].append(f"{cid}: title.kr!=card-title | gen={gt!r} json={j['title']['kr']!r}")

                # J7 href == url
                if g.get("href") != j["url"]:
                    jfail["J7"] += 1
                    jdetails["J7"].append(f"{cid}: href gen={g.get('href')} json={j['url']}")

                # J8 thumb-en 배지 == isEn
                if has_en_badge(g) != j["isEn"]:
                    jfail["J8"] += 1
                    jdetails["J8"].append(f"{cid}: thumb-en gen={has_en_badge(g)} isEn={j['isEn']}")

                # J9 thumb-label / gradient
                tl = thumb_label(g)
                exp_tl = j["thumbLabel"] if j["thumbLabel"] is not None else ""
                if tl != exp_tl:
                    jfail["J9"] += 1
                    jdetails["J9"].append(f"{cid}: thumb-label gen={tl!r} json={j['thumbLabel']!r}")
                if thumb_grad(g) != j["thumbGradient"]:
                    jfail["J9"] += 1
                    jdetails["J9"].append(f"{cid}: gradient gen={thumb_grad(g)} json={j['thumbGradient']}")

                # J1~J5: 속성 존재/값 검사 (a/b/c 규칙)
                # 각 속성을 어느 J 항목으로 집계할지 매핑
                attr_j = {
                    "data-impact-score": "J1",
                    "data-category": "J2",
                    "data-summary": "J3", "data-summary-kr": "J3",
                    "data-points": "J4", "data-points-kr": "J4",
                    "data-designer": "J4", "data-designer-kr": "J4",
                    "data-recommend": "J4", "data-recommend-kr": "J4",
                    "data-comment": "J4", "data-comment-kr": "J4",
                    "data-title-en": "J5",
                }
                for attr, expected in exp.items():
                    jc = attr_j[attr]
                    has = g.has_attr(attr)
                    val = norm_nl(g.get(attr)) if has else None
                    must_exist = j["isEn"] and attr in EN_MUST_EXIST

                    if expected is None and not must_exist:
                        # 속성이 없어야 정상
                        if has:
                            jfail[jc] += 1
                            abc_violations.append((cid, attr, "규칙a/c: JSON null 인데 속성 존재", (val or "")[:80], "<absent 기대>"))
                            jdetails[jc].append(f"{cid}: {attr} 존재하면 안 됨 gen={(val or '')[:60]!r}")
                    else:
                        # 속성이 반드시 있어야 하고 값이 같아야 정상
                        if must_exist and expected is None:
                            # isEn 인데 JSON 값이 null → 데이터 모순
                            jfail[jc] += 1
                            abc_violations.append((cid, attr, "규칙b: isEn 인데 JSON 값 null", (val or "")[:80] if has else "<absent>", "<non-null 기대>"))
                            jdetails[jc].append(f"{cid}: {attr} isEn 카드인데 JSON null")
                            continue
                        if not has:
                            jfail[jc] += 1
                            abc_violations.append((cid, attr, "규칙b: 속성 없음", "<absent>", (expected or "")[:80]))
                            jdetails[jc].append(f"{cid}: {attr} 누락 exp={(expected or '')[:60]!r}")
                        elif val != expected:
                            jfail[jc] += 1
                            jdetails[jc].append(f"{cid}: {attr} 값불일치\n    gen[:80]={(val or '')[:80]!r}\n    json[:80]={(expected or '')[:80]!r}")

    print(f"\n검사한 카드 수: {checked}")
    print("\nJ 항목별 불일치 건수 (전부 0 이어야 정상):")
    labels = {
        "J1": "impact-score",
        "J2": "category.kr",
        "J3": "summary(+kr)",
        "J4": "points/designer/recommend/comment(+kr)",
        "J5": "title-en",
        "J6": "card-title",
        "J7": "href",
        "J8": "thumb-en 배지",
        "J9": "thumb-label/gradient",
    }
    total = 0
    for i in range(1, 10):
        k = f"J{i}"
        total += jfail[k]
        print(f"  {k} {labels[k]:42s}: {jfail[k]}")
    print(f"  {'합계':46s}: {total}")

    if jdetails.get("J0"):
        print("\n[구조 경고]")
        for m in jdetails["J0"]:
            print("  · " + m)

    if abc_violations:
        print("\n[속성 존재 여부 위반 (a/b/c) 상세]")
        for cid, attr, kind, gen, exp in abc_violations:
            print(f"  · {cid} / {attr} / {kind} / gen={gen!r} / exp={exp}")

    if total:
        print("\n[불일치 상세]")
        for i in range(1, 10):
            k = f"J{i}"
            for m in jdetails[k]:
                print(f"  ({k}) {m}")

    return total == 0 and not jdetails.get("J0")


# ─────────────────────────────────────────────────────────
# 축 2
# ─────────────────────────────────────────────────────────
def gb_count(soup):
    ids = sum(1 for el in soup.find_all(id=True) if el.get("id", "").startswith("gb"))
    cls = 0
    for el in soup.find_all(class_=True):
        cls += sum(1 for c in el.get("class", []) if c.startswith("gb-"))
    return ids, cls


def drawer_count(soup):
    return sum(1 for el in soup.find_all(id=True) if el.get("id", "").startswith("drawer"))


def scripts_src(soup):
    return [s.get("src") for s in soup.find_all("script")]


def css_href(soup):
    return [l.get("href") for l in soup.find_all("link", rel="stylesheet")]


def title_str(soup):
    t = soup.find("title")
    return t.get_text() if t else None


def site_date_str(soup):
    el = soup.find("div", class_="site-date")
    return el.get_text() if el else None


def axis2():
    print("\n" + "=" * 60)
    print("[축 2] 생성본 HTML ↔ 원본 HTML 대조 (25일)")
    print("=" * 60)

    by_date = load_json_cards()
    rows = []           # (date, verdict, note)
    fail_details = []   # 상세
    d3_hits = set()     # 실제로 관측된 D3 (date,section,idx,field)
    d6_diff_count = 0   # D6 로 분류된 diff 수
    d6_detail = []
    d7_diff_count = 0   # D7(원본 잔재 속성) 로 분류된 diff 수
    d7_detail = []
    a1a2_706 = None

    for day in range(1, 26):
        date = f"2026-07-{day:02d}"
        y, m, d = date.split("-")
        op = ORIG_DIR / f"Dinol_news_{y}{m}{d}.html"
        gp = GEN_DIR / f"Dinol_news_{y}{m}{d}.html"
        if not op.is_file() or not gp.is_file():
            rows.append((date, "FAIL", f"파일 없음 orig={op.is_file()} gen={gp.is_file()}"))
            fail_details.append(f"{date}: 파일 없음")
            continue
        o = load_html(op)
        g = load_html(gp)
        is_d6 = date in D6_DATES

        real_fail = []   # 설명 안 되는 diff
        d3_here = []
        d6_here = []
        d7_here = []

        oc, gc = all_cards(o), all_cards(g)
        osec, gsec = sec_cards(o), sec_cards(g)

        # A1 카드 개수
        if len(oc) != len(gc):
            real_fail.append(f"A1 카드수 orig={len(oc)} gen={len(gc)}")

        # A2 섹션별 카드 수
        for nm in ("AI", "Design"):
            oo = len(osec.get(nm, []))
            gg = len(gsec.get(nm, []))
            if oo != gg:
                real_fail.append(f"A2 {nm} orig={oo} gen={gg}")

        if date == "2026-07-06":
            a1a2_706 = {
                "A1": (len(oc), len(gc)),
                "AI": (len(osec.get("AI", [])), len(gsec.get("AI", []))),
                "Design": (len(osec.get("Design", [])), len(gsec.get("Design", []))),
            }

        n = min(len(oc), len(gc))

        # A3 href / A4 title / A5 source (순서 포함)
        for i in range(n):
            if oc[i].get("href") != gc[i].get("href"):
                real_fail.append(f"A3 href#{i+1} orig={oc[i].get('href')} gen={gc[i].get('href')}")
            if card_title(oc[i]) != card_title(gc[i]):
                real_fail.append(f"A4 title#{i+1} orig={card_title(oc[i])!r} gen={card_title(gc[i])!r}")
            if card_source(oc[i]) != card_source(gc[i]):
                real_fail.append(f"A5 source#{i+1} orig={card_source(oc[i])!r} gen={card_source(gc[i])!r}")

        # A6 thumb-label + gradient
        for i in range(n):
            if thumb_label(oc[i]) != thumb_label(gc[i]):
                real_fail.append(f"A6 thumb-label#{i+1} orig={thumb_label(oc[i])!r} gen={thumb_label(gc[i])!r}")
            if thumb_grad(oc[i]) != thumb_grad(gc[i]):
                real_fail.append(f"A6 gradient#{i+1} orig={thumb_grad(oc[i])} gen={thumb_grad(gc[i])}")

        # A7 thumb-en (D6 날짜는 EXPECTED)
        for i in range(n):
            oe, ge = has_en_badge(oc[i]), has_en_badge(gc[i])
            if oe != ge:
                if is_d6:
                    d6_here.append(f"A7 thumb-en#{i+1} orig={oe} gen={ge}")
                else:
                    real_fail.append(f"A7 thumb-en#{i+1} orig={oe} gen={ge}")

        # A8 data-* 이름 집합
        #   - orig 전용이 D7 잔재 속성뿐이면 → D7 (무해)
        #   - gen 전용이 있으면 → 무조건 real FAIL (생성본이 없는 속성을 만들어냄)
        #   - 그 외 orig 전용은 D6 날짜면 D6, 아니면 real FAIL
        for i in range(n):
            oa, ga = data_names(oc[i]), data_names(gc[i])
            orig_only = oa - ga
            gen_only = ga - oa
            d7 = orig_only & D7_ORIG_ONLY
            rest_orig = orig_only - D7_ORIG_ONLY
            if d7:
                d7_here.append(f"A8 data-이름#{i+1} orig잔재={sorted(d7)}")
            if gen_only:
                real_fail.append(f"A8 data-이름#{i+1} gen전용(생성본 초과)={sorted(gen_only)}")
            if rest_orig:
                msg = f"A8 data-이름#{i+1} orig전용={sorted(rest_orig)}"
                if is_d6:
                    d6_here.append(msg)
                else:
                    real_fail.append(msg)

        # A9 gb / drawer
        if gb_count(o) != gb_count(g):
            real_fail.append(f"A9 gb count orig={gb_count(o)} gen={gb_count(g)}")
        if drawer_count(o) != drawer_count(g):
            real_fail.append(f"A9 drawer orig={drawer_count(o)} gen={drawer_count(g)}")

        # A10 script/footer/to-top
        if scripts_src(o) != scripts_src(g):
            real_fail.append(f"A10 scripts orig={scripts_src(o)} gen={scripts_src(g)}")
        if len(o.find_all("footer")) != len(g.find_all("footer")):
            real_fail.append(f"A10 footer orig={len(o.find_all('footer'))} gen={len(g.find_all('footer'))}")
        if (o.find(id="toTop") is not None) != (g.find(id="toTop") is not None):
            real_fail.append("A10 to-top 유무 불일치")

        # A11 stylesheet href
        if css_href(o) != css_href(g):
            real_fail.append(f"A11 css orig={css_href(o)} gen={css_href(g)}")

        # A12 title / site-date
        if title_str(o) != title_str(g):
            real_fail.append(f"A12 title orig={title_str(o)!r} gen={title_str(g)!r}")
        if site_date_str(o) != site_date_str(g):
            real_fail.append(f"A12 site-date orig={site_date_str(o)!r} gen={site_date_str(g)!r}")

        # A13 값 비교 (섹션+순번). D3/D6 분류
        for sec in ("ai", "design"):
            ocs = osec.get(SEC_NAME[sec], [])
            gcs = gsec.get(SEC_NAME[sec], [])
            for i in range(min(len(ocs), len(gcs))):
                for field, attr in FIELD_ATTR.items():
                    ov = norm_nl(ocs[i].get(attr))
                    gv = norm_nl(gcs[i].get(attr))
                    if ov == gv:
                        continue
                    key = (date, sec, i, field)
                    if key in D3_SET:
                        d3_hits.add(key)
                        d3_here.append(f"A13 {sec}#{i+1} {field}")
                    elif is_d6:
                        d6_here.append(f"A13 {sec}#{i+1} {field}")
                    else:
                        real_fail.append(
                            f"A13 {sec}#{i+1} {field}\n      orig[:80]={(ov or '')[:80]!r}\n      gen [:80]={(gv or '')[:80]!r}")

        # 판정
        if real_fail:
            rows.append((date, "FAIL", f"{len(real_fail)}건"))
            for f in real_fail:
                fail_details.append(f"{date}: {f}")
        elif d3_here or d6_here or d7_here:
            tags = []
            if d3_here:
                tags.append(f"D3×{len(d3_here)}")
            if d6_here:
                tags.append(f"D6×{len(d6_here)}")
                d6_detail.extend(f"{date}: {x}" for x in d6_here)
            if d7_here:
                tags.append(f"D7×{len(d7_here)}")
                d7_detail.extend(f"{date}: {x}" for x in d7_here)
            rows.append((date, "EXPECTED DIFF", ", ".join(tags)))
        else:
            rows.append((date, "PASS", ""))

        d6_diff_count += len(d6_here)
        d7_diff_count += len(d7_here)

    # 표 출력
    print(f"\n{'날짜':12s} {'판정':16s} 비고")
    print("-" * 50)
    for date, verdict, note in rows:
        print(f"{date:12s} {verdict:16s} {note}")

    # FAIL 상세
    if fail_details:
        print("\n[FAIL 상세]")
        for f in fail_details:
            print("  · " + f)
    else:
        print("\n[FAIL 없음]")

    # D3 검증
    print(f"\n[D3] 정의 13개 필드 중 실제 관측 {len(d3_hits)}개")
    missing_d3 = D3_SET - d3_hits
    extra_note = ""
    if missing_d3:
        print("  · 정의됐지만 실제 차이 없던 항목(원본==생성):")
        for k in sorted(missing_d3):
            print(f"      {k}")
    if len(d3_hits) == 13:
        print("  → 정확히 13개 필드 (초과 없음)")
    else:
        print(f"  → 관측 {len(d3_hits)}개 (정의 13개와 비교)")

    # D6 검증
    print(f"\n[D6] EXPECTED 처리된 diff {d6_diff_count}건 (0703·0724)")
    for x in d6_detail:
        print("  · " + x)

    # D7 검증 (사전조사가 놓친 원본 잔재 속성)
    print(f"\n[D7] 원본 잔재 속성 diff {d7_diff_count}건 "
          f"(data-impact / data-impact-kr / data-title-kr · JS 미사용/폴백)")
    for x in d7_detail:
        print("  · " + x)

    # 7/06 A1·A2
    print(f"\n[7/06 A1·A2] {a1a2_706}")
    if a1a2_706:
        ok = (a1a2_706["A1"][0] == a1a2_706["A1"][1]
              and a1a2_706["AI"] == (5, 5)
              and a1a2_706["Design"] == (3, 3))
        print(f"  → AI 5/5, Design 3/3, 카드수 일치: {'PASS' if ok else 'FAIL'}")

    verdicts = [r[1] for r in rows]
    return "FAIL" not in verdicts, rows


def main():
    a1_ok = axis1()
    a2_ok, rows = axis2()
    print("\n" + "=" * 60)
    print("종합")
    print("=" * 60)
    print(f"  축 1 (생성본↔JSON): {'PASS' if a1_ok else 'FAIL'}")
    print(f"  축 2 (생성본↔원본): {'FAIL 없음' if a2_ok else 'FAIL 있음'}")
    return 0 if (a1_ok and a2_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
