#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원본 브리핑 HTML(7/25)을 마커 기준으로 잘라 Astro 컴포넌트 조각 7개를 만들고,
card-footer 내부 HTML 을 추출해 Card.astro 의 __CARD_FOOTER__ 를 치환한다.

정규식으로 grid 를 파싱하지 않는다. 마커는 str.index/count 로 찾는다.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_HTML = ROOT / "news" / "2026" / "07" / "Dinol_news_20260725.html"
COMP = ROOT / "src" / "components"
CARD = COMP / "Card.astro"

M1 = "<!-- ── DRAWER ── -->"
M2 = "<!-- ── HEADER ── -->"
M3 = "<!-- ══════════════════════ AI ══════════════════════ -->"
M4 = "<!-- ── 아카이브 · 오픈채팅방 이동 (카드 끝, 푸터 위) ── -->"
M5 = "<!-- ── 방명록 ── -->"
M6 = "<!-- ── FOOTER ── -->"
M7 = "<!-- ── 맨 위로 (모바일 전용, 스크롤 시 노출) ── -->"
MARKERS = [M1, M2, M3, M4, M5, M6, M7]


def die(msg):
    print(f"[오류] {msg}", file=sys.stderr)
    sys.exit(1)


def add_is_inline(text):
    """<script ...> 여는 태그마다 is:inline 을 넣는다 (이미 있으면 건너뜀)."""
    return re.sub(r'<script(?![^>]*\bis:inline\b)', '<script is:inline', text)


def extract_card_footer_inner(html):
    """첫 번째 card 의 card-footer 내부 HTML 을 태그 깊이 계산으로 추출."""
    a_idx = html.index('<a class="card')
    open_tag = '<div class="card-footer">'
    fo = html.index(open_tag, a_idx)
    inner_start = fo + len(open_tag)
    depth = 1
    inner_end = None
    for m in re.finditer(r'<div\b|</div>', html[inner_start:]):
        tok = m.group()
        if tok == '</div>':
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            inner_end = inner_start + m.start()
            break
    if inner_end is None:
        die("card-footer 의 대응 닫는 </div> 를 찾지 못했습니다")
    return html[inner_start:inner_end]


def main():
    # 전제: Card.astro 존재
    if not CARD.is_file():
        die(f"Card.astro 가 없습니다: {CARD} (먼저 §2 를 생성하세요)")
    if not SRC_HTML.is_file():
        die(f"원본 HTML 이 없습니다: {SRC_HTML}")

    html = SRC_HTML.read_text(encoding="utf-8")

    # 검증 1) 마커 각 1회
    for i, mk in enumerate(MARKERS, 1):
        c = html.count(mk)
        if c != 1:
            die(f"마커 M{i} 등장 횟수가 1이 아님: {c}회  ({mk})")

    # 슬라이스
    head_start = html.index("<head>") + len("<head>")
    head_end = html.index("</head>")
    frag = {
        "Head": html[head_start:head_end],
        "Drawer": html[html.index(M1):html.index(M2)],
        "Header": html[html.index(M2):html.index(M3)],
        "ArchiveCta": html[html.index(M4):html.index(M5)],
        "Guestbook": html[html.index(M5):html.index(M6)],
        "SiteFooter": html[html.index(M6):html.index(M7)],
        "Scripts": html[html.index(M7):html.index("</body>")],
    }

    # 3-2) Head title 치환
    old_title = "<title>디자인 놀이터 — 2026. 07. 25</title>"
    new_title = "<title>디자인 놀이터 — {titleDate}</title>"
    head_title_hits = frag["Head"].count(old_title)
    if head_title_hits != 1:
        die(f"Head title 원본 문자열이 1회가 아님: {head_title_hits}회")
    frag["Head"] = frag["Head"].replace(old_title, new_title)

    # 3-3) Header site-date 치환
    old_date = '<div class="site-date">July 25, 2026</div>'
    new_date = '<div class="site-date">{siteDate}</div>'
    header_date_hits = frag["Header"].count(old_date)
    if header_date_hits != 1:
        die(f"Header site-date 원본 문자열이 1회가 아님: {header_date_hits}회")
    frag["Header"] = frag["Header"].replace(old_date, new_date)

    # 3-4) is:inline (Head, Scripts)
    frag["Head"] = add_is_inline(frag["Head"])
    frag["Scripts"] = add_is_inline(frag["Scripts"])

    # 프론트매터 부착
    frag["Head"] = "---\nconst { titleDate } = Astro.props;\n---\n" + frag["Head"]
    frag["Header"] = "---\nconst { siteDate } = Astro.props;\n---\n" + frag["Header"]

    # 검증 3) 조각에 '<a class="card' 없음
    for name, txt in frag.items():
        if '<a class="card' in txt:
            die(f"조각 {name}.astro 에 '<a class=\"card' 가 존재함")

    # 조각 저장
    for name, txt in frag.items():
        (COMP / f"{name}.astro").write_text(txt, encoding="utf-8")

    # 3-5) card-footer 추출 + Card.astro 치환
    footer_inner = extract_card_footer_inner(html)
    card_txt = CARD.read_text(encoding="utf-8")
    if card_txt.count("__CARD_FOOTER__") != 1:
        die(f"Card.astro 의 __CARD_FOOTER__ 가 1회가 아님: {card_txt.count('__CARD_FOOTER__')}회")
    card_txt = card_txt.replace("__CARD_FOOTER__", footer_inner)
    CARD.write_text(card_txt, encoding="utf-8")

    # ────────── 검증 출력 ──────────
    print("=== 검증 1) 마커 M1~M7 각 1회 ===")
    print("  OK — 7개 마커 모두 정확히 1회")

    print("=== 검증 2) 조각 7개 문자 수 (모두 > 0) ===")
    ok2 = True
    for name in ["Head", "Drawer", "Header", "ArchiveCta", "Guestbook", "SiteFooter", "Scripts"]:
        n = len(frag[name])
        if n == 0:
            ok2 = False
        print(f"  {name:12s}: {n}자")
    if not ok2:
        die("빈 조각이 존재")

    print("=== 검증 3) 조각에 '<a class=\"card' 없음 ===")
    print("  OK — 7개 조각 모두 0회")

    print("=== 검증 4) Head/Header 치환 각 1회 ===")
    print(f"  Head title 치환: {head_title_hits}회 · Header site-date 치환: {header_date_hits}회")
    # 치환 후 새 표현식이 들어갔는지
    print(f"  Head 에 {{titleDate}} 존재: {'{titleDate}' in frag['Head']}")
    print(f"  Header 에 {{siteDate}} 존재: {'{siteDate}' in frag['Header']}")

    print("=== 검증 5) <script> 개수 == is:inline 개수 (Head+Scripts) ===")
    script_open = len(re.findall(r'<script\b', frag["Head"])) + len(re.findall(r'<script\b', frag["Scripts"]))
    inline_cnt = frag["Head"].count("is:inline") + frag["Scripts"].count("is:inline")
    print(f"  <script 여는 태그: {script_open}개 · is:inline: {inline_cnt}개 · 일치: {script_open == inline_cnt}")
    if script_open != inline_cnt:
        die("script 개수와 is:inline 개수 불일치")
    # 스타일시트 href 원본 유지
    css_ok = '<link rel="stylesheet" href="../../../assets/dinol.css">' in frag["Head"]
    fonts_ok = 'fonts.googleapis.com/css2' in frag["Head"] and 'rel="stylesheet"' in frag["Head"]
    print(f"  Head dinol.css 링크 원본 유지: {css_ok} · 폰트 스타일시트 유지: {fonts_ok}")
    if not css_ok:
        die("Head 의 dinol.css 스타일시트 링크가 원본과 다름")

    print("=== 검증 6) Card.astro __CARD_FOOTER__ 0회 + 내부 요소 ===")
    left = card_txt.count("__CARD_FOOTER__")
    like = footer_inner.count("act-like")
    share = footer_inner.count("act-share")
    svg = footer_inner.count("<svg")
    print(f"  __CARD_FOOTER__ 잔여: {left}회 · act-like: {like} · act-share: {share} · <svg>: {svg}")
    if left != 0 or like != 1 or share != 1 or svg != 2:
        die("Card.astro 치환 결과가 기대와 다름")

    print("\n[성공] 조각 7개 생성 + Card.astro 치환 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
