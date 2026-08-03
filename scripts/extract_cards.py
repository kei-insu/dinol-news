#!/usr/bin/env python3
"""
extract_cards.py — 브리핑 HTML → 카드별 JSON 추출

사용법:
    python scripts/extract_cards.py                         # news/ 전체
    python scripts/extract_cards.py news/2026/07/Dinol_news_20260725.html
    python scripts/extract_cards.py --out content/news       # 출력 경로 지정
    python scripts/extract_cards.py --report                 # 파일 안 쓰고 요약만

출력:
    content/news/20260724-ai-003.json   (카드 1장 = 파일 1개)

스키마 정본: docs/reference/detail-page-schema.md
"""

import re
import os
import sys
import json
import glob
import html as htmllib
from collections import Counter

OUT_DIR = "content/news"
ALLOWED_SECTIONS = {"AI": "ai", "Design": "design"}

# 채워야 할 항목(추출만으로는 값을 만들 수 없는 것)
TODO_KEYS = {
    "category.kr": "EN 카드의 카테고리 한국어 표기 필요",
    "category.en": "KR 카드의 카테고리 영문 표기 (KR 카드는 EN 토글이 없어 선택)",
    "positions": "관련 직무 부여 필요",
    "impactScore.rubric": "섹션별 별점 기준으로 재채점 필요",
}


def clean(s):
    if s is None:
        return None
    s = htmllib.unescape(s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s.strip() or None


def one_line(s):
    return re.sub(r"\s+", " ", s).strip() if s else None


def attr(block, name):
    m = re.search(r'data-%s="([^"]*)"' % re.escape(name), block)
    return clean(m.group(1)) if m else None


def split_pipe(s):
    if not s:
        return []
    return [x.strip() for x in s.split("|") if x.strip()]


def inner(block, cls):
    m = re.search(r'class="%s">(.*?)</div>' % re.escape(cls), block, re.S)
    return one_line(htmllib.unescape(m.group(1))) if m else None


def parse_source(raw):
    """'Music Business Worldwide · 2026. 07. 21' -> (name, '2026-07-21')"""
    if not raw:
        return None, None
    parts = [p.strip() for p in raw.split("·")]
    name = parts[0] if parts else None
    published = None
    if len(parts) > 1:
        d = re.findall(r"\d+", parts[-1])
        if len(d) >= 3:
            published = f"{d[0]}-{d[1].zfill(2)}-{d[2].zfill(2)}"
    return name, published


def parse_cards(html):
    """[(section_key, card_block, order), ...]"""
    out = []
    parts = re.split(r"<h2>(AI|Design)</h2>", html)
    section = None
    counters = Counter()
    for chunk in parts:
        if chunk in ALLOWED_SECTIONS:
            section = ALLOWED_SECTIONS[chunk]
            continue
        if section is None:
            continue
        for m in re.finditer(r'<a class="card[^"]*"(?:.*?)</a>', chunk, re.S):
            counters[section] += 1
            out.append((section, m.group(0), counters[section]))
    return out


def build_card(section, block, order, ymd):
    date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
    content_id = f"{ymd}-{section}-{order:03d}"

    is_en = "thumb-en" in block
    href = re.search(r'href="([^"]*)"', block)
    href = htmllib.unescape(href.group(1)) if href else None

    title_kr = inner(block, "card-title")
    title_en = attr(block, "title-en")

    src_name, published = parse_source(inner(block, "card-source"))

    category_raw = attr(block, "category")
    grad = re.search(r'class="thumb ([a-z-]+)"', block)
    label = re.search(r'class="thumb-label">(.*?)</span>', block, re.S)

    def pair(base):
        """EN 카드: data-X=영문, data-X-kr=한국어 / KR 카드: data-X=한국어"""
        raw = attr(block, base)
        raw_kr = attr(block, base + "-kr")
        if is_en:
            return {"kr": raw_kr, "en": raw}
        return {"kr": raw, "en": None}

    summary = pair("summary")
    designer = pair("designer")
    recommend = pair("recommend")
    comment = pair("comment")
    pts = pair("points")

    score_raw = attr(block, "impact-score")
    score = int(score_raw) if score_raw and score_raw.isdigit() else None

    card = {
        "contentId": content_id,
        "date": date,
        "section": section,
        "order": order,
        "source": {"name": src_name, "publishedAt": published},
        "url": href,
        "isEn": is_en,
        "featured": "card featured" in block,
        "category": {
            "kr": None if is_en else category_raw,
            "en": category_raw if is_en else None,
        },
        "title": {"kr": title_kr, "en": title_en},
        "summary": summary,
        "points": {"kr": split_pipe(pts["kr"]), "en": split_pipe(pts["en"])},
        "positions": [],
        "designer": designer,
        "impactScore": score,
        "recommend": recommend,
        "comment": comment,
        "thumbLabel": one_line(htmllib.unescape(label.group(1))) if label else None,
        "thumbGradient": grad.group(1) if grad else None,
    }

    todo = []
    if is_en and not card["category"]["kr"]:
        todo.append("category.kr")
    if not card["positions"]:
        todo.append("positions")
    todo.append("impactScore.rubric")
    card["_todo"] = todo

    return card


def missing_fields(card):
    """필수 값이 비어 있으면 목록으로 반환."""
    miss = []
    if not card["url"]:
        miss.append("url")
    if not card["title"]["kr"]:
        miss.append("title.kr")
    if not card["summary"]["kr"]:
        miss.append("summary.kr")
    if not card["points"]["kr"]:
        miss.append("points.kr")
    if not card["designer"]["kr"]:
        miss.append("designer.kr")
    if card["impactScore"] is None:
        miss.append("impactScore")
    if not card["recommend"]["kr"]:
        miss.append("recommend.kr")
    if not card["comment"]["kr"]:
        miss.append("comment.kr")
    if card["isEn"] and not card["title"]["en"]:
        miss.append("title.en")
    return miss


def main():
    argv = sys.argv[1:]
    out_dir = OUT_DIR
    report_only = "--report" in argv
    if "--out" in argv:
        out_dir = argv[argv.index("--out") + 1]
    files = [a for a in argv if a.endswith(".html")]

    if not files:
        files = sorted(glob.glob("news/**/Dinol_news_*.html", recursive=True))
    if not files:
        print("브리핑 파일을 찾을 수 없습니다.")
        return 1

    if not report_only:
        os.makedirs(out_dir, exist_ok=True)

    all_cards = []
    problems = []

    for path in files:
        m = re.search(r"Dinol_news_(\d{8})\.html$", os.path.basename(path))
        if not m:
            problems.append((path, "파일명 규칙 위반"))
            continue
        ymd = m.group(1)
        with open(path, encoding="utf-8") as f:
            doc = f.read()

        cards = parse_cards(doc)
        if not cards:
            problems.append((path, "카드 없음"))
            continue

        for section, block, order in cards:
            card = build_card(section, block, order, ymd)
            miss = missing_fields(card)
            if miss:
                problems.append((card["contentId"], "누락: " + ", ".join(miss)))
            all_cards.append(card)

            if not report_only:
                dest = os.path.join(out_dir, card["contentId"] + ".json")
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump(card, f, ensure_ascii=False, indent=2)

    # ── 요약 ──
    ids = [c["contentId"] for c in all_cards]
    dup = [i for i, n in Counter(ids).items() if n > 1]
    by_sec = Counter(c["section"] for c in all_cards)
    by_score = Counter(c["impactScore"] for c in all_cards)
    en_n = sum(1 for c in all_cards if c["isEn"])
    need_cat_kr = sum(1 for c in all_cards if "category.kr" in c["_todo"])

    print(f"브리핑 {len(files)}개 → 카드 {len(all_cards)}장")
    print(f"  AI {by_sec['ai']} · Design {by_sec['design']} · EN 카드 {en_n}")
    print("  별점 분포 " + " · ".join(f"★{k} {by_score[k]}" for k in sorted(k for k in by_score if k)))
    if not report_only:
        print(f"  출력: {out_dir}/")
    print()
    print("추출 후 채워야 할 항목")
    print(f"  category.kr  {need_cat_kr}장 (EN 카드 카테고리 한국어 표기)")
    print(f"  positions    {len(all_cards)}장 (관련 직무)")
    print(f"  impactScore  {len(all_cards)}장 (섹션별 기준 재채점)")

    if dup:
        print()
        print("contentId 중복:")
        for d in dup:
            print("  " + d)
    if problems:
        print()
        print(f"확인 필요 {len(problems)}건:")
        for who, what in problems[:40]:
            print(f"  {os.path.basename(str(who))}  {what}")
        if len(problems) > 40:
            print(f"  ... 외 {len(problems) - 40}건")

    return 1 if dup else 0


if __name__ == "__main__":
    sys.exit(main())
