#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 실행 전: pip install -r requirements.txt
"""
validate_briefing.py — 상세 페이지 중심 구조 전환(4-2) 후 브리핑 25개 전수 검증.

브리핑은 원본과 의도적으로 달라졌으므로 원본 대조가 아니라
"의도한 대로 바뀌었는가"(B1~B16)를 JSON 기준으로 검사한다.

파서: BeautifulSoup(html.parser). 줄바꿈만 CRLF·CR → LF.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "content" / "news"
GEN_ROOT = ROOT / "dist" / "news" / "2026"
SEC_NAME = {"ai": "AI", "design": "Design"}

# 이전(before-4-2)과 동일해야 하는 값 — 외곽 조각은 안 바꿨으므로 고정.
EXPECT_SCRIPTS = [
    "https://www.googletagmanager.com/gtag/js?id=G-ZC93DYWB2B",
    "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX",
    "../../../assets/dinol.js",
    "../../../assets/dinol-firebase.js",
    "../../../assets/likes.js",
]


def norm(s):
    return None if s is None else s.replace("\r\n", "\n").replace("\r", "\n")


def load_json_by_date():
    by_date = defaultdict(lambda: {"ai": [], "design": []})
    for p in sorted(JSON_DIR.glob("*.json")):
        j = json.loads(p.read_text(encoding="utf-8"))
        by_date[j["date"]][j["section"]].append(j)
    for d in by_date:
        for s in ("ai", "design"):
            by_date[d][s].sort(key=lambda c: c["order"])
    return by_date


def data_names(card):
    return {k for k in card.attrs if k.startswith("data-")}


def thumb_grad(card):
    t = card.find("div", class_="thumb")
    if not t:
        return None
    for c in t.get("class", []):
        if c.startswith("g-"):
            return c
    return None


def txt(card, cls):
    el = card.find(class_=cls)
    return el.get_text() if el else None


def sec_cards(soup):
    # 5-A-1 구조전환: 카드 최상위는 <article class="card">(내부에 <a class="card-link">).
    out = {}
    for sec in soup.find_all("div", class_="section"):
        h2 = sec.find("h2")
        out[h2.get_text() if h2 else "?"] = sec.find_all("article", class_="card")
    return out


def main():
    by_date = load_json_by_date()
    fails = defaultdict(list)   # Bcode -> [msg]

    def bad(code, msg):
        fails[code].append(msg)

    gb_total = 0
    checked_cards = 0
    href_targets_missing = []

    for date in sorted(by_date):
        y, m, d = date.split("-")
        gen_p = GEN_ROOT / m / f"Dinol_news_{y}{m}{d}.html"
        if not gen_p.is_file():
            bad("B0", f"{date}: 브리핑 HTML 없음")
            continue
        raw = norm(gen_p.read_text(encoding="utf-8"))
        soup = BeautifulSoup(raw, "html.parser")
        gsecs = sec_cards(soup)
        all_cards = soup.find_all("article", class_="card")

        # B1 카드 개수 (JSON 기준)
        exp_n = len(by_date[date]["ai"]) + len(by_date[date]["design"])
        if len(all_cards) != exp_n:
            bad("B1", f"{date}: 카드 {len(all_cards)} != JSON {exp_n}")

        # 카드별 (섹션+순번) 대조
        for sec in ("ai", "design"):
            jcards = by_date[date][sec]
            gcards = gsecs.get(SEC_NAME[sec], [])
            if len(jcards) != len(gcards):
                bad("B1", f"{date} {sec}: 카드수 JSON {len(jcards)} != HTML {len(gcards)}")
            for i, j in enumerate(jcards):
                if i >= len(gcards):
                    break
                g = gcards[i]
                cid = j["contentId"]
                checked_cards += 1

                # 5-A-1: 이동 링크는 article 내부의 <a class="card-link"> 가 소유(정확히 1개).
                links = g.find_all("a", class_="card-link")
                link = links[0] if links else None
                if len(links) != 1:
                    bad("B2", f"{cid}: card-link {len(links)}개 (1개여야 함)")
                # B2 href == {contentId}.html  (card-link 의 href)
                if link is None or link.get("href") != f"{cid}.html":
                    bad("B2", f"{cid}: href={link.get('href') if link else None}")
                # B3 data-content-id == contentId  (article 소유)
                if g.get("data-content-id") != cid:
                    bad("B3", f"{cid}: data-content-id={g.get('data-content-id')}")
                # B4 data-* 이름 집합 == {data-content-id} (집합+값, article 기준)
                names = data_names(g)
                if names != {"data-content-id"}:
                    bad("B4", f"{cid}: data-* 이름집합={sorted(names)}")
                # B5 target 속성 없음  (이동 링크=card-link 에 target 없어야)
                if link is not None and link.has_attr("target"):
                    bad("B5", f"{cid}: target={link.get('target')!r} 존재")
                # B6 (5-A-2 갱신) like-box 정형성: article.card 안 · a.card-link 밖에 like-box 1개,
                #   dataset 3종(content-id/source-url/share-url) · 버튼 2종(type=button·aria-label) ·
                #   act-count · 앵커(card-link) 안에는 button 없음(중첩 interactive 방지).
                boxes = g.find_all("div", class_="like-box")
                if len(boxes) != 1:
                    bad("B6", f"{cid}: like-box {len(boxes)}개 (1개여야 함)")
                else:
                    box = boxes[0]
                    if box.find_parent("a", class_="card-link") is not None:
                        bad("B6", f"{cid}: like-box 가 card-link 앵커 안에 있음")
                    if box.get("data-content-id") != cid:
                        bad("B6", f"{cid}: like-box data-content-id={box.get('data-content-id')}")
                    if not (box.get("data-source-url") or "").strip():
                        bad("B6", f"{cid}: like-box data-source-url 비어있음")
                    if not (box.get("data-share-url") or "").strip():
                        bad("B6", f"{cid}: like-box data-share-url 비어있음")
                    for nm in ("act-like", "act-share"):
                        b = box.find("button", class_=nm)
                        if b is None:
                            bad("B6", f"{cid}: {nm} 버튼 없음")
                        else:
                            if b.get("type") != "button":
                                bad("B6", f"{cid}: {nm} type != button")
                            if not (b.get("aria-label") or "").strip():
                                bad("B6", f"{cid}: {nm} aria-label 없음")
                    if box.find("span", class_="act-count") is None:
                        bad("B6", f"{cid}: act-count 없음")
                if link is not None and link.find_all("button"):
                    bad("B6", f"{cid}: card-link 앵커 안에 button 존재")
                # B7 thumb-en == isEn
                has_en = g.find("span", class_="thumb-en") is not None
                if has_en != j["isEn"]:
                    bad("B7", f"{cid}: thumb-en={has_en} isEn={j['isEn']}")
                # B8 thumb-label / gradient
                if txt(g, "thumb-label") != (j["thumbLabel"] if j["thumbLabel"] is not None else ""):
                    bad("B8", f"{cid}: thumb-label={txt(g,'thumb-label')!r} json={j['thumbLabel']!r}")
                if thumb_grad(g) != j["thumbGradient"]:
                    bad("B8", f"{cid}: gradient={thumb_grad(g)} json={j['thumbGradient']}")
                # B9 card-source
                pub = j["source"]["publishedAt"]
                disp = ". ".join(pub.split("-")) if pub else ""
                exp_src = f'{j["source"]["name"]} · {disp}' if j["source"]["name"] else disp
                if txt(g, "card-source") != exp_src:
                    bad("B9", f"{cid}: source={txt(g,'card-source')!r} != {exp_src!r}")
                # B10 card-title == title.kr
                if txt(g, "card-title") != norm(j["title"]["kr"]):
                    bad("B10", f"{cid}: card-title != title.kr")
                # B16 href 대상 상세 HTML 실제 존재
                target = GEN_ROOT / cid[4:6] / f"{cid}.html"
                if not target.is_file():
                    bad("B16", f"{cid}: 상세 {cid}.html 없음")
                    href_targets_missing.append(cid)

        # B6 (문서 전역) like-box 개수 == 카드 개수 · 드로어 시절 .card-footer 잔존 없음
        if len(soup.find_all("div", class_="like-box")) != len(all_cards):
            bad("B6", f"{date}: like-box 수 {len(soup.find_all('div', class_='like-box'))} != 카드 {len(all_cards)}")
        if soup.select(".card-footer"):
            bad("B6", f"{date}: 문서에 .card-footer 잔존")

        # B11 drawer 요소 0개
        drawer_ids = [el for el in soup.find_all(id=True)
                      if (el.get("id") or "").startswith("drawer")]
        drawer_cls = soup.select("[class*='drawer-']")
        if drawer_ids or drawer_cls or soup.find(id="drawer") or soup.find(id="drawerOverlay"):
            bad("B11", f"{date}: drawer 요소 id={len(drawer_ids)} .drawer-*={len(drawer_cls)}")

        # B12 btnKr/btnEn/drawer-lang-toggle 0개
        if soup.find(id="btnKr") or soup.find(id="btnEn") or soup.find(id="drawerLangToggle") \
                or soup.select(".drawer-lang-toggle"):
            bad("B12", f"{date}: 언어토글 요소 잔존")

        # B13 방명록 gb- 요소 존재 (개수 집계)
        gb = [el for el in soup.find_all(True)
              if (el.get("id", "") or "").startswith("gb")
              or any(c.startswith("gb-") for c in (el.get("class") or []))]
        gb_total += len(gb)
        if not gb:
            bad("B13", f"{date}: 방명록 gb- 요소 0개 (있어야 함)")

        # B14 script src 목록
        srcs = [s.get("src") for s in soup.find_all("script") if s.get("src")]
        if srcs != EXPECT_SCRIPTS:
            bad("B14", f"{date}: script src={srcs}")

        # B15 title / site-date (이전과 동일: 포맷 검증)
        title = soup.find("title")
        title = title.get_text() if title else None
        exp_title = f"디자인 놀이터 — {y}. {m}. {d}"
        if title != exp_title:
            bad("B15", f"{date}: title={title!r} != {exp_title!r}")
        sd = soup.find("div", class_="site-date")
        sd = sd.get_text() if sd else None
        MON = ['January','February','March','April','May','June','July','August',
               'September','October','November','December']
        exp_sd = f"{MON[int(m)-1]} {int(d)}, {y}"
        if sd != exp_sd:
            bad("B15", f"{date}: site-date={sd!r} != {exp_sd!r}")

    # ── 출력 ──
    print("=" * 56)
    print("B축 — 브리핑 25개 전수 검증 (4-2 구조전환)")
    print("=" * 56)
    print(f"검사 카드 수: {checked_cards}")
    labels = {
        "B0": "브리핑 HTML 존재", "B1": "카드 개수(JSON)", "B2": "href={cid}.html",
        "B3": "data-content-id==cid", "B4": "data-* 집합=={data-content-id}",
        "B5": "target 없음", "B6": "like-box 정형(dataset3·버튼2)", "B7": "thumb-en==isEn",
        "B8": "thumb-label/gradient", "B9": "card-source", "B10": "card-title",
        "B11": "drawer 요소 0", "B12": "언어토글 0", "B13": "방명록 존재",
        "B14": "script src 동일", "B15": "title/site-date", "B16": "href 대상 존재",
    }
    total = 0
    print("\n항목별 불일치 (전부 0이어야 정상):")
    for i in range(0, 17):
        code = f"B{i}"
        if code == "B0" and code not in fails:
            continue
        n = len(fails.get(code, []))
        total += n
        mark = "" if n == 0 else "  ← 불일치"
        print(f"  {code:4s} {labels.get(code,''):26s}: {n}{mark}")
        for msg in fails.get(code, [])[:5]:
            print(f"        · {msg}")
    print(f"\n  방명록 gb- 요소 총계(B13, 참고): {gb_total}")
    print(f"\n불일치 합계: {total}")
    print("결과:", "PASS ✅" if total == 0 else "FAIL ❌")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
