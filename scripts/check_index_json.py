#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 실행 전: pip install -r requirements.txt
"""
index.json 정합성 검사 — 보고 전용. 파일을 절대 수정하지 않는다.

7-0 형식 확인 → 7-1 기본정보 → 7-2 양방향 대조.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
INDEX_JSON = DIST / "index.json"
NEWS_DIR = DIST / "news" / "2026" / "07"

YMD_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
DATE_FIELDS = ("date", "ymd", "day", "id")   # 객체일 때 날짜 필드 후보


def parse_ymd(s):
    """YYYYMMDD 문자열이면 (실제 날짜 파싱까지) date 반환, 아니면 None."""
    if not isinstance(s, str):
        return None
    m = YMD_RE.match(s)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def item_ymd(item):
    """항목에서 YYYYMMDD 문자열을 뽑아낸다. (raw_str, date|None, note)"""
    if isinstance(item, str):
        return item, parse_ymd(item), "문자열"
    if isinstance(item, dict):
        for f in DATE_FIELDS:
            if f in item:
                v = item[f]
                return f"{f}={v!r}", parse_ymd(str(v)), f"객체.{f}"
        return repr(item)[:60], None, "객체(날짜필드 못찾음)"
    return repr(item)[:60], None, f"타입={type(item).__name__}"


def main():
    print("=" * 60)
    print("index.json 정합성 검사 (보고 전용, 수정 안 함)")
    print("=" * 60)
    print(f"대상: {INDEX_JSON}")

    if not INDEX_JSON.is_file():
        print("[오류] dist/index.json 없음")
        return 1

    raw_bytes = INDEX_JSON.read_bytes()
    has_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    if has_bom:
        print("  (참고) 파일 선두에 UTF-8 BOM 있음 → utf-8-sig 로 디코드")
    raw = raw_bytes.decode("utf-8-sig")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}")
        return 1

    # ── 7-0 형식 확인 ──
    print("\n[7-0] 형식 확인")
    if not isinstance(data, list):
        print(f"  ★최상위가 배열이 아님 (타입={type(data).__name__}). 이하 검사 건너뜀.")
        # 참고로 dict 이면 키만 출력
        if isinstance(data, dict):
            print(f"    최상위 키: {list(data.keys())[:20]}")
        return 1
    print(f"  최상위 배열 OK (길이 {len(data)})")

    parsed = []      # (index, raw_str, date|None, note)
    bad = []         # 잘못된 항목
    for i, item in enumerate(data):
        raws, dt, note = item_ymd(item)
        parsed.append((i, raws, dt, note))
        if dt is None:
            bad.append((i, raws, note))

    if bad:
        print(f"  ★잘못된 항목 {len(bad)}건 (인덱스·원본값):")
        for i, raws, note in bad:
            print(f"    [{i}] {raws}  ({note})")
    else:
        print("  모든 항목이 유효한 YYYYMMDD (실제 날짜 파싱 성공)")

    valid = [(i, raws, dt) for (i, raws, dt, note) in parsed if dt is not None]
    dates = [dt for (_, _, dt) in valid]

    # ── 7-1 기본 정보 ──
    print("\n[7-1] 기본 정보")
    print(f"  배열 길이            : {len(data)}")
    if not dates:
        print("  유효 날짜가 없어 이하 통계 생략")
        return 1
    first_raw = parsed[0][1]
    first_dt = parsed[0][2]
    max_dt = max(dates)
    max_raw = max_dt.strftime("%Y%m%d")
    print(f"  배열 첫 값           : {first_raw}  (파싱={first_dt})")
    print(f"  날짜 기준 실제 최댓값 : {max_raw}")
    match_first_max = (first_dt == max_dt)
    print(f"  첫 값 == 최댓값       : {match_first_max}  (내림차순이면 True 여야 정상)")

    # 중복
    seen = {}
    dups = []
    for (_, _, dt) in valid:
        seen[dt] = seen.get(dt, 0) + 1
    for dt, c in seen.items():
        if c > 1:
            dups.append((dt.strftime("%Y%m%d"), c))
    print(f"  날짜 중복            : {'없음' if not dups else dups}")

    # 정렬 방향
    asc = all(dates[i] <= dates[i + 1] for i in range(len(dates) - 1))
    desc = all(dates[i] >= dates[i + 1] for i in range(len(dates) - 1))
    if desc and not asc:
        direction = "내림차순"
    elif asc and not desc:
        direction = "오름차순"
    elif asc and desc:
        direction = "단일/동일"
    else:
        direction = "섞임"
    print(f"  정렬 방향            : {direction}")

    # ── 7-2 양방향 대조 ──
    print("\n[7-2] 양방향 대조")
    # index.json → HTML 존재
    json_dates = set()
    missing_html = []
    for (i, raws, dt) in valid:
        ymd = dt.strftime("%Y%m%d")
        json_dates.add(ymd)
        html = NEWS_DIR / f"Dinol_news_{ymd}.html"
        if not html.is_file():
            missing_html.append((i, ymd))
    print(f"  index.json → HTML 없는 항목: {len(missing_html)}건")
    for i, ymd in missing_html:
        print(f"    [{i}] {ymd} → {NEWS_DIR / ('Dinol_news_'+ymd+'.html')} 없음")

    # HTML → index.json 없음
    html_dates = set()
    for p in sorted(NEWS_DIR.glob("Dinol_news_*.html")):
        m = re.search(r"Dinol_news_(\d{8})\.html$", p.name)
        if m:
            html_dates.add(m.group(1))
    only_html = sorted(html_dates - json_dates)
    print(f"  HTML 에만 있고 index.json 에 없는 날짜: {len(only_html)}건")
    for ymd in only_html:
        print(f"    {ymd}")

    print(f"  dist HTML 총 개수     : {len(html_dates)}")
    print(f"  index.json 날짜 수    : {len(json_dates)}")

    # 20260725 포함 여부
    print(f"  20260725 index.json 포함: {'20260725' in json_dates}")
    print(f"  20260725 HTML 존재      : {'20260725' in html_dates}")

    # ── P2 판정 재료 ──
    all_json_have_html = (len(missing_html) == 0)
    all_html_in_json = (len(only_html) == 0)
    first_is_latest = (first_raw_ymd := first_dt.strftime("%Y%m%d")) == "20260725" and (max_raw == "20260725")
    print("\n[P2 재료]")
    print(f"  · 모든 index.json 항목이 HTML 존재 : {all_json_have_html}")
    print(f"  · 25개 브리핑 전부 index.json 포함  : {all_html_in_json} (HTML {len(html_dates)}개)")
    print(f"  · 배열 첫 값 == 최신 20260725       : {first_raw_ymd == '20260725'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
