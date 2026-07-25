#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 실행 전: pip install -r requirements.txt
"""
원본 브리핑 HTML 과 Astro 생성 HTML 을 비교한다.

비교 규칙:
- 양쪽을 같은 파서(BeautifulSoup, html.parser)로 파싱한다.
- 파서가 반환한 속성값을 그대로 비교한다. html.unescape() 를 추가 적용하지 않는다.
- 줄바꿈만 정규화: CRLF·CR → LF. 줄 끝 공백/연속 공백은 보존한다.
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / "news" / "2026" / "07" / "Dinol_news_20260725.html"
GEN = ROOT / "dist" / "news" / "2026" / "07" / "Dinol_news_20260725.html"

FAIL = []


def norm_nl(s):
    return s.replace("\r\n", "\n").replace("\r", "\n")


def load(p):
    raw = norm_nl(p.read_text(encoding="utf-8"))
    return BeautifulSoup(raw, "html.parser"), raw


def cards(soup):
    return soup.find_all("a", class_="card")


def section_counts(soup):
    out = {}
    for sec in soup.find_all("div", class_="section"):
        h2 = sec.find("h2")
        name = h2.get_text() if h2 else "?"
        out[name] = len(sec.find_all("a", class_="card"))
    return out


def thumb_grad(card):
    thumb = card.find("div", class_="thumb")
    if not thumb:
        return None
    for c in thumb.get("class", []):
        if c.startswith("g-"):
            return c
    return None


def txt(card, cls):
    el = card.find("div", class_=cls)
    return el.get_text() if el else None


def data_names(card):
    return {k for k in card.attrs if k.startswith("data-")}


def fail(msg):
    FAIL.append(msg)
    print(f"  [불일치] {msg}")


def main():
    if not ORIG.is_file():
        print(f"[오류] 원본 없음: {ORIG}"); return 1
    if not GEN.is_file():
        print(f"[오류] 생성본 없음: {GEN}"); return 1

    o, o_raw = load(ORIG)
    g, g_raw = load(GEN)
    oc, gc = cards(o), cards(g)

    print("========== [A] 일치해야 하는 항목 ==========")

    # 1) card 개수
    print(f"\n[A1] <a class=\"card\"> 개수  원본={len(oc)} 생성={len(gc)} (기대 8)")
    if not (len(oc) == len(gc) == 8):
        fail(f"카드 개수: 원본 {len(oc)} / 생성 {len(gc)}")

    # 2) 섹션별 카드 수
    os_, gs_ = section_counts(o), section_counts(g)
    print(f"[A2] 섹션별 카드 수  원본={os_} 생성={gs_}")
    if os_.get("AI") != 4 or os_.get("Design") != 4 or gs_.get("AI") != 4 or gs_.get("Design") != 4:
        fail(f"섹션 카드 수 불일치: 원본 {os_} / 생성 {gs_}")

    n = min(len(oc), len(gc))

    # 3) href
    print("[A3] 카드별 href")
    for i in range(n):
        a, b = oc[i].get("href"), gc[i].get("href")
        if a != b:
            fail(f"href #{i+1}: 원본={a} 생성={b}")
    if not FAIL:
        print("     OK")

    # 4) card-title
    before = len(FAIL)
    print("[A4] 카드별 card-title")
    for i in range(n):
        a, b = txt(oc[i], "card-title"), txt(gc[i], "card-title")
        if a != b:
            fail(f"card-title #{i+1}: 원본={a!r} 생성={b!r}")
    if len(FAIL) == before:
        print("     OK")

    # 5) card-source
    before = len(FAIL)
    print("[A5] 카드별 card-source")
    for i in range(n):
        a, b = txt(oc[i], "card-source"), txt(gc[i], "card-source")
        if a != b:
            fail(f"card-source #{i+1}: 원본={a!r} 생성={b!r}")
    if len(FAIL) == before:
        print("     OK")

    # 6) thumb-label + gradient
    before = len(FAIL)
    print("[A6] 카드별 thumb-label / gradient 클래스")
    for i in range(n):
        la, lb = txt(oc[i], "thumb-label"), txt(gc[i], "thumb-label")
        ga, gb = thumb_grad(oc[i]), thumb_grad(gc[i])
        if la != lb:
            fail(f"thumb-label #{i+1}: 원본={la!r} 생성={lb!r}")
        if ga != gb:
            fail(f"thumb gradient #{i+1}: 원본={ga} 생성={gb}")
    if len(FAIL) == before:
        print("     OK")

    # 7) thumb-en 유무
    before = len(FAIL)
    print("[A7] 카드별 thumb-en 배지 유무")
    for i in range(n):
        a = oc[i].find("span", class_="thumb-en") is not None
        b = gc[i].find("span", class_="thumb-en") is not None
        if a != b:
            fail(f"thumb-en #{i+1}: 원본={a} 생성={b}")
    if len(FAIL) == before:
        print("     OK")

    # 8) data-* 이름 집합
    before = len(FAIL)
    print("[A8] 카드별 data-* 속성 이름 집합")
    for i in range(n):
        a, b = data_names(oc[i]), data_names(gc[i])
        if a != b:
            fail(f"data-* 이름 #{i+1}: 원본만={sorted(a-b)} 생성만={sorted(b-a)}")
    if len(FAIL) == before:
        print("     OK")

    # 9) data-* 값 비교
    VAL_ATTRS = [
        "data-summary", "data-summary-kr", "data-points", "data-points-kr",
        "data-designer", "data-designer-kr", "data-recommend", "data-recommend-kr",
        "data-comment", "data-comment-kr", "data-title-en",
    ]
    before = len(FAIL)
    print("[A9] 카드별 data-* 값 비교")
    for i in range(n):
        for attr in VAL_ATTRS:
            a, b = oc[i].get(attr), gc[i].get(attr)
            if a == b:
                continue
            fail(f"{attr} #{i+1} 값 불일치")
            a80 = (a or "")[:80]
            b80 = (b or "")[:80]
            print(f"        원본[:80]={a80!r}")
            print(f"        생성[:80]={b80!r}")
            if attr == "data-comment":
                anl = (a or "").count(chr(10))
                bnl = (b or "").count(chr(10))
                print(f"        data-comment 줄바꿈 수  원본={anl} 생성={bnl}")
    if len(FAIL) == before:
        print("     OK")
    # data-comment 줄바꿈 수는 일치 여부와 무관하게 참고 출력
    print("     · data-comment 줄바꿈 수 (원본/생성):")
    for i in range(n):
        a, b = oc[i].get("data-comment") or "", gc[i].get("data-comment") or ""
        print(f"        #{i+1}: {a.count(chr(10))} / {b.count(chr(10))}")

    # 10) gb- id/class 개수
    def gb_count(soup):
        ids = sum(1 for el in soup.find_all(id=True) if el.get("id", "").startswith("gb"))
        cls = 0
        for el in soup.find_all(class_=True):
            cls += sum(1 for c in el.get("class", []) if c.startswith("gb-"))
        return ids, cls
    oi, ocl = gb_count(o); gi, gcl = gb_count(g)
    print(f"[A10] gb id 개수 원본={oi} 생성={gi} · gb- class 개수 원본={ocl} 생성={gcl}")
    if (oi, ocl) != (gi, gcl):
        fail(f"gb 카운트 불일치: 원본 id={oi} class={ocl} / 생성 id={gi} class={gcl}")

    # 11) drawer id 개수
    od = sum(1 for el in o.find_all(id=True) if el.get("id", "").startswith("drawer"))
    gd = sum(1 for el in g.find_all(id=True) if el.get("id", "").startswith("drawer"))
    print(f"[A11] drawer id 개수  원본={od} 생성={gd}")
    if od != gd:
        fail(f"drawer id 개수 불일치: 원본 {od} / 생성 {gd}")

    # 12) script/ footer/ to-top
    def scripts(soup):
        return [s.get("src") for s in soup.find_all("script")]
    osc, gsc = scripts(o), scripts(g)
    print(f"[A12] <script> 개수  원본={len(osc)} 생성={len(gsc)}")
    print(f"      원본 src={osc}")
    print(f"      생성 src={gsc}")
    if osc != gsc:
        fail(f"script src 목록 불일치")
    ofoot, gfoot = len(o.find_all("footer")), len(g.find_all("footer"))
    otop = o.find(id="toTop") is not None
    gtop = g.find(id="toTop") is not None
    print(f"      <footer> 개수 원본={ofoot} 생성={gfoot} · to-top 원본={otop} 생성={gtop}")
    if ofoot != gfoot:
        fail(f"footer 개수 불일치: {ofoot}/{gfoot}")
    if otop != gtop:
        fail(f"to-top 버튼 유무 불일치: {otop}/{gtop}")

    # 13) stylesheet href
    def css(soup):
        return [l.get("href") for l in soup.find_all("link", rel="stylesheet")]
    ocss, gcss = css(o), css(g)
    print(f"[A13] <link rel=stylesheet> href  원본={ocss} 생성={gcss}")
    if ocss != gcss:
        fail(f"stylesheet href 불일치")

    # 14) title / site-date
    ot = o.find("title").get_text() if o.find("title") else None
    gt = g.find("title").get_text() if g.find("title") else None
    osd = o.find("div", class_="site-date")
    gsd = g.find("div", class_="site-date")
    osd = osd.get_text() if osd else None
    gsd = gsd.get_text() if gsd else None
    print(f"[A14] <title> 원본={ot!r} 생성={gt!r}")
    print(f"      site-date 원본={osd!r} 생성={gsd!r}")
    if ot != gt:
        fail(f"title 불일치")
    if osd != gsd:
        fail(f"site-date 불일치")

    print("\n========== [B] 다른 게 정상 — 양쪽 값 나란히 ==========")
    # 15) impact-score
    print("[B15] 카드별 data-impact-score (원본 / 생성)")
    for i in range(n):
        print(f"      #{i+1}: {oc[i].get('data-impact-score')} / {gc[i].get('data-impact-score')}")
    # 16) data-category
    print("[B16] 카드별 data-category (원본 / 생성)")
    for i in range(n):
        print(f"      #{i+1}: {oc[i].get('data-category')!r} / {gc[i].get('data-category')!r}")
    # 17) 파일 크기
    print("[B17] 파일 크기 (bytes)")
    print(f"      원본={ORIG.stat().st_size} 생성={GEN.stat().st_size}")

    print("\n========== [C] 내부 링크 대상 존재 (참고) ==========")
    base = GEN.parent  # dist/news/2026/07
    rels = [
        ("../../../archive.html", "없는 게 정상"),
        ("../../../privacy.html", "없는 게 정상"),
        ("../../../assets/dinol.css", "반드시 존재"),
        ("../../../assets/dinol.js", "반드시 존재"),
        ("../../../assets/dinol-firebase.js", "반드시 존재"),
        ("../../../assets/ai-design-news.png", "반드시 존재"),
    ]
    print(f"  {'경로':40s} {'존재':6s} {'기대'}")
    for rel, note in rels:
        exists = (base / rel).resolve().is_file()
        print(f"  {rel:40s} {str(exists):6s} {note}")

    print("\n========== 결과 ==========")
    if FAIL:
        print(f"[A] 실패 — 불일치 {len(FAIL)}건")
        for m in FAIL:
            print(f"  · {m}")
        return 1
    print("[A] 전부 일치 (PASS). B·C 는 참고 출력.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
