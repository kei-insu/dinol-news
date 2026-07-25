#!/usr/bin/env python3
"""
validate.py — 디놀 브리핑 발행 전 검증 (v1)

사용법:
    python scripts/validate.py                          # news/ 전체 검사
    python scripts/validate.py news/2026/07/Dinol_news_20260725.html
    python scripts/validate.py --from 2026-07-19        # 특정일 이후만

배포 절차:
    git pull -> 파일 배치 -> python scripts/validate.py
    -> python scripts/build_published_urls.py -> ./deploy.ps1 "..."

ERROR 가 1건이라도 있으면 종료코드 1 로 끝난다. 배포하지 않는다.
WARN 은 메시지만 남기고 통과시킨다.
"""

import re
import sys
import glob
import os
from collections import Counter

# 정책 상수·공용 함수는 validation_common 이 단일 출처. HTML·JSON 검증이 공유한다.
from validation_common import (
    CARD_COUNT_POLICY_FROM,
    POSITION_SCHEMA_FROM,
    CATEGORY_EN_SCHEMA_FROM,
    CONTENT_ID_SCHEMA_FROM,
    SECTION_RUBRIC_POLICY_FROM,
    EN_LANGUAGE_POLICY_FROM,
    VALID_POSITIONS,
    ALLOWED_SECTIONS,
    CONTENT_ID_RE,
    applies,
    normalize_slot,
    is_korean_slot,
    is_missing_slot,
    has_slot_value,
)

POSITIONS = VALID_POSITIONS

REQUIRED_FIELDS = ("summary", "points", "designer", "impact-score", "recommend", "comment")
REQUIRED_KR_PAIRS = ("summary-kr", "points-kr", "designer-kr", "recommend-kr", "comment-kr")

# EN 카드 언어 슬롯 검사 대상 쌍: 필드 → (영문 attr, 국문 attr)
EN_SLOT_PAIRS = (
    ("summary", "summary", "summary-kr"),
    ("points", "points", "points-kr"),
    ("designer", "designer", "designer-kr"),
    ("recommend", "recommend", "recommend-kr"),
    ("comment", "comment", "comment-kr"),
)


# ────────────────────────────────────────────────────────────
# 리포트
# ────────────────────────────────────────────────────────────
class Report:
    def __init__(self):
        self.errors = []
        self.warns = []

    def error(self, path, msg, detail=""):
        self.errors.append((path, msg, detail))

    def warn(self, path, msg, detail=""):
        self.warns.append((path, msg, detail))

    def dump(self):
        for path, msg, detail in self.errors:
            print(f"ERROR  {os.path.basename(path)}  {msg}")
            if detail:
                print(f"       {detail}")
        for path, msg, detail in self.warns:
            print(f"WARN   {os.path.basename(path)}  {msg}")
            if detail:
                print(f"       {detail}")
        print()
        print(f"ERROR {len(self.errors)}건 · WARN {len(self.warns)}건")
        return 1 if self.errors else 0


# ────────────────────────────────────────────────────────────
# 파싱
# ────────────────────────────────────────────────────────────
def attr(block, name):
    m = re.search(r'data-%s="([^"]*)"' % re.escape(name), block)
    return m.group(1) if m else None


def parse_cards(html):
    """[(section, card_block, index_in_section), ...] 를 문서 순서대로 반환."""
    out = []
    parts = re.split(r"<h2>(AI|Design)</h2>", html)
    section = None
    counters = Counter()
    for chunk in parts:
        if chunk in ("AI", "Design"):
            section = chunk.lower()
            continue
        if section is None:
            continue
        for m in re.finditer(r'<a class="card[^"]*"(.*?)</a>', chunk, re.S):
            counters[section] += 1
            out.append((section, m.group(0), counters[section]))
    return out


def card_href(block):
    m = re.search(r'href="([^"]*)"', block)
    return m.group(1) if m else ""


def card_title(block):
    m = re.search(r'class="card-title">(.*?)</div>', block, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def card_source(block):
    m = re.search(r'class="card-source">(.*?)</div>', block, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def is_en_card(block):
    return "thumb-en" in block


# ────────────────────────────────────────────────────────────
# 검사
# ────────────────────────────────────────────────────────────
def validate_file(path, rep):
    fname = os.path.basename(path)
    m = re.match(r"Dinol_news_(\d{8})\.html$", fname)
    if not m:
        rep.error(path, "파일명 규칙 위반", "형식: Dinol_news_YYYYMMDD.html")
        return
    ymd = m.group(1)
    file_date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"

    with open(path, encoding="utf-8") as f:
        html = f.read()

    # 파일명과 페이지 날짜 일치 (모든 파일)
    site_date = re.search(r'class="site-date">([^<]*)<', html)
    if site_date:
        digits = re.findall(r"\d+", site_date.group(1))
        if len(digits) >= 3:
            y, d_, *_ = digits
            if y != ymd[:4] or d_.zfill(2) != ymd[6:]:
                rep.error(path, "파일명과 페이지 날짜 불일치",
                          f"파일명 {file_date} / 페이지 {site_date.group(1).strip()}")

    cards = parse_cards(html)
    if not cards:
        rep.error(path, "카드를 찾을 수 없음")
        return

    # 카드 수 (기준일 이후)
    if applies(CARD_COUNT_POLICY_FROM, file_date):
        counts = Counter(s for s, _, _ in cards)
        if len(cards) != 8:
            rep.error(path, f"카드 수 {len(cards)}개 (8개여야 함)")
        if counts.get("ai", 0) != 4 or counts.get("design", 0) != 4:
            rep.error(path, "섹션별 카드 수 위반",
                      f"AI {counts.get('ai', 0)} · Design {counts.get('design', 0)} (각 4개여야 함)")

    urls = []
    content_ids = []
    scores = []
    sources = []
    en_count = 0

    for section, block, idx in cards:
        pos = f"{section} {idx}번째"
        href = card_href(block)
        title = card_title(block)[:30]
        tag = f"{pos} · {title}"

        # 링크 (모든 파일)
        if not href or href.strip() in ("", "#"):
            rep.error(path, "빈 링크", tag)
        else:
            urls.append(href)

        # 필수 필드 (모든 파일)
        for f_ in REQUIRED_FIELDS:
            if attr(block, f_) is None or attr(block, f_).strip() == "":
                rep.error(path, f"필수 필드 누락: data-{f_}", tag)

        en = is_en_card(block)
        # -kr 속성이 하나라도 있으면 EN 카드로 간주(배지 누락 방어)
        has_kr_attr = any(attr(block, f_) for f_ in REQUIRED_KR_PAIRS) or bool(attr(block, "title-en"))
        if has_kr_attr and not en:
            rep.error(path, "EN 카드인데 thumb-en 배지 없음",
                      tag + " (-kr 속성 존재)")
            en = True
        if en:
            en_count += 1
            for f_ in REQUIRED_KR_PAIRS:
                if attr(block, f_) is None or attr(block, f_).strip() == "":
                    rep.error(path, f"EN 카드 한국어 짝 누락: data-{f_}", tag)

            # EN 카드 언어 슬롯 결함 검사 (HTML 층)
            en_policy = applies(EN_LANGUAGE_POLICY_FROM, file_date)
            for field, en_attr, kr_attr in EN_SLOT_PAIRS:
                en_raw = attr(block, en_attr)
                kr_raw = attr(block, kr_attr)
                # ★선행 조건★ 영문·국문 둘 다 존재하고 둘 다 비어있지 않을 때만
                if not (has_slot_value(en_raw) and has_slot_value(kr_raw)):
                    continue
                en_v = normalize_slot(en_raw)
                kr_v = normalize_slot(kr_raw)
                # 등급: 정책 적용 전이면 전부 WARN / 적용 후엔 summary·points 만 ERROR
                hard = en_policy and field in ("summary", "points")
                emit = rep.error if hard else rep.warn
                # 검사1: 영문 == 국문 (번역 누락으로 같은 값 중복)
                if en_v == kr_v:
                    emit(path, f"EN 슬롯 중복: {field} (영문==국문)", tag)
                # 검사2: 영문 슬롯이 한국어
                if is_korean_slot(en_v):
                    emit(path, f"EN 영문 슬롯이 한국어: {field}", tag)

        # impact score (모든 파일)
        raw = attr(block, "impact-score")
        if raw is not None and raw.strip():
            if not raw.isdigit() or not (1 <= int(raw) <= 5):
                rep.error(path, f"impact-score 범위 위반: {raw}", tag)
            else:
                sc = int(raw)
                scores.append((section, sc))
                if section == "design" and sc == 1 and applies(SECTION_RUBRIC_POLICY_FROM, file_date):
                    rep.error(path, "Design 섹션 ★1 사용 금지", tag)

        # category-en (기준일 이후, EN 카드만)
        if en and applies(CATEGORY_EN_SCHEMA_FROM, file_date):
            if not attr(block, "category-en"):
                rep.error(path, "EN 카드에 data-category-en 누락", tag)

        # position (기준일 이후)
        if applies(POSITION_SCHEMA_FROM, file_date):
            raw_pos = attr(block, "position")
            if raw_pos:
                ids = [x.strip() for x in raw_pos.split("|") if x.strip()]
                if len(ids) > 2:
                    rep.error(path, f"직무 {len(ids)}개 (최대 2개)", tag)
                for pid in ids:
                    if pid not in POSITIONS:
                        rep.error(path, f"등록되지 않은 position ID: {pid}", tag)

        # contentId (기준일 이후)
        if applies(CONTENT_ID_SCHEMA_FROM, file_date):
            cid = attr(block, "content-id")
            if not cid:
                rep.error(path, "data-content-id 누락", tag)
            elif not CONTENT_ID_RE.match(cid):
                rep.error(path, f"contentId 형식 위반: {cid}",
                          "형식: YYYYMMDD-ai|design-000")
            else:
                content_ids.append(cid)

        src = card_source(block).split("·")[0].strip()
        if src:
            sources.append(src)

    # URL 중복 (모든 파일)
    for u, n in Counter(urls).items():
        if n > 1:
            rep.error(path, f"URL 중복 {n}회", u[:80])

    # contentId 중복
    for c, n in Counter(content_ids).items():
        if n > 1:
            rep.error(path, f"contentId 중복 {n}회", c)

    # ── 이하 WARN ──
    if applies(CARD_COUNT_POLICY_FROM, file_date):
        ai_scores = [s for sec, s in scores if sec == "ai"]
        if ai_scores:
            if sum(1 for s in ai_scores if s == 1) >= 2:
                rep.warn(path, "AI 섹션 ★1이 2장 이상 (상한 1장 권장)")
            if not any(s >= 4 for s in ai_scores):
                rep.warn(path, "AI 섹션에 ★4~5 카드가 없음 (최소 1장 권장)")

        for s, n in Counter(sources).items():
            if n >= 3:
                rep.warn(path, f"동일 매체 {n}개: {s} (상한 2개)")

        if en_count != 4:
            rep.warn(path, f"EN 카드 {en_count}장 (국내:해외 5:5 = EN 4장 권장)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    since = None
    for i, a in enumerate(sys.argv[1:]):
        if a == "--from" and i + 1 < len(sys.argv) - 1:
            since = sys.argv[i + 2]

    if args:
        paths = args
    else:
        paths = sorted(glob.glob("news/**/Dinol_news_*.html", recursive=True))

    if since:
        paths = [p for p in paths
                 if re.search(r"(\d{8})", os.path.basename(p))
                 and re.search(r"(\d{8})", os.path.basename(p)).group(1) >= since.replace("-", "")]

    if not paths:
        print("검사할 파일이 없습니다.")
        return 0

    rep = Report()
    for p in paths:
        validate_file(p, rep)

    print(f"검사 파일 {len(paths)}개")
    print()
    return rep.dump()


if __name__ == "__main__":
    sys.exit(main())
