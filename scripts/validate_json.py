#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_json.py — content/news/*.json 카드 데이터 검증 (JSON 층)

사용법:
    python scripts/validate_json.py              # 전체
    python scripts/validate_json.py 20260725     # 특정 날짜 상세

★최우선 원칙★
  어떤 데이터가 들어와도 예외로 죽지 않는다. 이상 데이터는 ERROR 로 기록하고
  다음 카드로 넘어가 209장을 끝까지 검사한다.

★로드 규칙★
  날짜 인수가 있어도 content/news 전체를 항상 로드한다.
  - contentId 전역 중복 검사는 언제나 전체 기준
  - 나머지 검사·상세 출력은 지정 날짜로 제한
"""

import os
import re
import sys
import glob
import json
from collections import Counter, defaultdict

from validation_common import (
    EN_LANGUAGE_POLICY_FROM,
    VALID_POSITIONS,
    ALLOWED_SECTIONS,
    CONTENT_ID_RE,
    applies,
    normalize_slot,
    is_korean_slot,
    is_missing_slot,
    has_slot_value,
    is_plain_int,
    get_pair,
    is_real_date,
)

NEWS_GLOB = "content/news/*.json"

PARENTS = ("category", "title", "summary", "points", "designer", "recommend", "comment", "source")
EN_SLOT_FIELDS = ("summary", "points", "designer", "recommend", "comment")


# ────────────────────────────────────────────────────────────
# 리포트 (항목 코드별 집계 지원)
# ────────────────────────────────────────────────────────────
class Report:
    def __init__(self):
        self.errors = []   # (fname, code, msg, detail)
        self.warns = []

    def error(self, fname, code, msg, detail=""):
        self.errors.append((fname, code, msg, detail))

    def warn(self, fname, code, msg, detail=""):
        self.warns.append((fname, code, msg, detail))

    def dump(self):
        for fname, code, msg, detail in self.errors:
            print(f"ERROR  {fname}  [{code}] {msg}")
            if detail:
                print(f"       {detail}")
        for fname, code, msg, detail in self.warns:
            print(f"WARN   {fname}  [{code}] {msg}")
            if detail:
                print(f"       {detail}")
        print()
        print(f"ERROR {len(self.errors)}건 · WARN {len(self.warns)}건")
        return 1 if self.errors else 0

    def error_code_dist(self):
        return Counter(c for _, c, _, _ in self.errors)

    def warn_code_dist(self):
        return Counter(c for _, c, _, _ in self.warns)


# ────────────────────────────────────────────────────────────
# 검사
# ────────────────────────────────────────────────────────────
def card_date(data, fname):
    """카드 날짜: data.date 가 정상 문자열이면 그것, 아니면 파일명 앞 8자리."""
    d = data.get("date") if isinstance(data, dict) else None
    if isinstance(d, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        return d
    m = re.match(r"^(\d{4})(\d{2})(\d{2})-", fname)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return "0000-00-00"


def check_card(fname, data, rep, agg):
    """한 카드 검사. agg 에 F-2/F-3, G 집계를 누적한다."""
    # 1단계: 최상위 dict 확인 (어떤 필드 접근보다 먼저)
    if not isinstance(data, dict):
        rep.error(fname, "A-4", "JSON 최상위가 객체가 아님")
        return

    cdate = card_date(data, fname)

    # 2단계: 부모 객체 8개 확인
    parents = {}
    for key in PARENTS:
        child = get_pair(data, key)
        if not isinstance(child, dict):
            rep.error(fname, "A-4", f"{key} 가 객체가 아님 (dict 아님)")
            parents[key] = None
        else:
            parents[key] = child

    def sub(parent_key, subkey):
        return get_pair(parents.get(parent_key), subkey)

    # ── A-1) 문자열 필수 ──
    for name, val in (
        ("contentId", data.get("contentId")),
        ("date", data.get("date")),
        ("section", data.get("section")),
        ("url", data.get("url")),
    ):
        if is_missing_slot(val):
            rep.error(fname, "A-1", f"필수 문자열 누락/빈값: {name}")
    for parent_key, label in (
        ("title", "title.kr"), ("summary", "summary.kr"),
        ("designer", "designer.kr"), ("recommend", "recommend.kr"),
        ("comment", "comment.kr"),
    ):
        if parents.get(parent_key) is not None:
            if is_missing_slot(sub(parent_key, "kr")):
                rep.error(fname, "A-1", f"필수 문자열 누락/빈값: {label}")

    # ── A-2) 배열 필수: points.kr ──
    if parents.get("points") is not None:
        if is_missing_slot(sub("points", "kr")):
            rep.error(fname, "A-2", "필수 배열 누락/빈값: points.kr")

    # ── A-3) 숫자·불리언 (is_missing_slot 금지) ──
    order = data.get("order")
    if not (is_plain_int(order) and order >= 1):
        rep.error(fname, "A-3", f"order 는 1 이상 정수여야 함: {order!r}")
    impact = data.get("impactScore")
    if not (is_plain_int(impact) and 1 <= impact <= 5):
        rep.error(fname, "A-3", f"impactScore 는 1~5 정수여야 함: {impact!r}")
    if not isinstance(data.get("isEn"), bool):
        rep.error(fname, "A-3", f"isEn 은 불리언이어야 함: {data.get('isEn')!r}")
    if not isinstance(data.get("featured"), bool):
        rep.error(fname, "A-3", f"featured 는 불리언이어야 함: {data.get('featured')!r}")

    # ── A-4) 타입·형식 ──
    # date
    dval = data.get("date")
    if isinstance(dval, str) and dval.strip():
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dval) or not is_real_date(dval):
            rep.error(fname, "A-4", f"date 형식/실재 위반: {dval!r}")
    # section
    sval = data.get("section")
    if isinstance(sval, str) and sval.strip():
        if sval not in ALLOWED_SECTIONS:
            rep.error(fname, "A-4", f"section 값 위반: {sval!r}")
    # positions (검사 순서 고정)
    positions = data.get("positions")
    pos_ok = False
    if not isinstance(positions, list):
        rep.error(fname, "A-4", f"positions 는 배열이어야 함: {type(positions).__name__}")
    else:
        # (2) 원소 전부 비어있지 않은 문자열 — set() 전에 확인
        bad_el = False
        for el in positions:
            if not (isinstance(el, str) and el.strip() != ""):
                bad_el = True
                break
        if bad_el:
            rep.error(fname, "A-4", "positions 는 비어있지 않은 문자열 배열이어야 함")
        else:
            pos_ok = True
            # (3) 내부 중복
            if len(positions) != len(set(positions)):
                rep.error(fname, "A-4", f"positions 내부 중복: {positions}")
            # (4) 개수 상한 → E
            if len(positions) > 2:
                rep.error(fname, "E", f"positions {len(positions)}개 (최대 2)")
            # (5) 어휘 → E
            for pid in positions:
                if pid not in VALID_POSITIONS:
                    rep.error(fname, "E", f"등록되지 않은 position: {pid}")
    # points.kr 문자열 배열
    if parents.get("points") is not None:
        pk = sub("points", "kr")
        if pk is not None:
            if not isinstance(pk, list) or any(not isinstance(x, str) for x in pk):
                rep.error(fname, "A-4", "points.kr 은 문자열 배열이어야 함")
    # .en 슬롯 타입
    for parent_key in ("category", "title", "summary", "designer", "recommend", "comment"):
        if parents.get(parent_key) is not None:
            v = sub(parent_key, "en")
            if v is not None and not isinstance(v, str):
                rep.error(fname, "A-4", f"{parent_key}.en 은 None 또는 문자열이어야 함")
    if parents.get("points") is not None:
        pe = sub("points", "en")
        if pe is not None and (not isinstance(pe, list) or any(not isinstance(x, str) for x in pe)):
            rep.error(fname, "A-4", "points.en 은 None 또는 문자열 배열이어야 함")
    # source 하위
    if parents.get("source") is not None:
        sname = sub("source", "name")
        if sname is not None and not isinstance(sname, str):
            rep.error(fname, "A-4", "source.name 은 None 또는 문자열이어야 함")
        spub = sub("source", "publishedAt")
        if spub is not None:
            if not isinstance(spub, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", spub) or not is_real_date(spub):
                rep.error(fname, "A-4", f"source.publishedAt 은 None 또는 실재 날짜여야 함: {spub!r}")

    # ── B) contentId ──
    cid = data.get("contentId")
    if isinstance(cid, str) and cid.strip():
        if not CONTENT_ID_RE.match(cid):
            rep.error(fname, "B", f"contentId 형식 위반: {cid}")
        else:
            # 앞 8자리 실재 날짜
            if not is_real_date(cid[:8], "%Y%m%d"):
                rep.error(fname, "B", f"contentId 앞 8자리가 실재 날짜 아님: {cid[:8]}")
            parts = cid.split("-")
            # 앞 8 == date 하이픈 제거
            if isinstance(dval, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", dval):
                if cid[:8] != dval.replace("-", ""):
                    rep.error(fname, "B", f"contentId 날짜≠date: {cid[:8]} vs {dval}")
            # 가운데 == section
            if isinstance(sval, str) and parts[1] != sval:
                rep.error(fname, "B", f"contentId 섹션≠section: {parts[1]} vs {sval}")
            # 마지막 3자리 == order
            if is_plain_int(order):
                if int(parts[2]) != order:
                    rep.error(fname, "B", f"contentId 순번≠order: {parts[2]} vs {order}")

    # ── D) design 섹션 impactScore != 1 ──
    if sval == "design" and is_plain_int(impact) and impact == 1:
        rep.error(fname, "D", "Design 섹션 impactScore 1 금지")

    # ── F) isEn == true 카드 ──
    if data.get("isEn") is True:
        # F-1: .en 슬롯 누락
        f1_targets = (
            ("category", "en"), ("title", "en"), ("summary", "en"), ("points", "en"),
            ("designer", "en"), ("recommend", "en"), ("comment", "en"),
        )
        for parent_key, subkey in f1_targets:
            if parents.get(parent_key) is not None:
                if is_missing_slot(sub(parent_key, subkey)):
                    rep.error(fname, "F-1", f"EN 카드 {parent_key}.en 누락/빈값")
        # F-2 / F-3
        en_policy = applies(EN_LANGUAGE_POLICY_FROM, cdate)
        for field in EN_SLOT_FIELDS:
            if parents.get(field) is None:
                continue
            kr_raw = sub(field, "kr")
            en_raw = sub(field, "en")
            if not (has_slot_value(kr_raw) and has_slot_value(en_raw)):
                continue
            kr_v = normalize_slot(kr_raw)
            en_v = normalize_slot(en_raw)
            hard = en_policy and field in ("summary", "points")
            emit = rep.error if hard else rep.warn
            if kr_v == en_v:
                emit(fname, "F-2", f"EN 슬롯 중복: {field} (kr==en)")
                agg["f2"].append((cid or fname, cdate, field))
            if is_korean_slot(en_v):
                emit(fname, "F-3", f"EN 영문 슬롯이 한국어: {field}")
                agg["f3"].append((cid or fname, cdate, field, en_v[:80]))

    # ── G) isEn == false 카드: category.en 은 허용 ──
    if data.get("isEn") is False:
        g_hit = False
        for parent_key in ("title", "summary", "points", "designer", "recommend", "comment"):
            if parents.get(parent_key) is not None:
                if has_slot_value(sub(parent_key, "en")):
                    rep.warn(fname, "G", f"isEn=false 인데 {parent_key}.en 값 존재")
                    g_hit = True
        if g_hit:
            agg["g_cards"].add(cid or fname)

    # ── H) _todo 비어있지 않음 ──
    todo = data.get("_todo")
    if isinstance(todo, list) and len(todo) > 0:
        rep.warn(fname, "H", f"_todo 비어있지 않음: {todo}")


def main():
    date_arg = None
    for a in sys.argv[1:]:
        if re.match(r"^\d{8}$", a):
            date_arg = a

    files = sorted(glob.glob(NEWS_GLOB))
    if not files:
        print("검사할 JSON 이 없습니다.")
        return 0

    # 항상 전체 로드
    parsed = {}   # fname -> ('ok', data) | ('fail', errmsg)
    for path in files:
        fname = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                parsed[fname] = ("ok", json.load(f))
        except Exception as e:
            parsed[fname] = ("fail", f"{type(e).__name__}: {e}")

    # 전역 contentId 중복 (항상 전체 기준)
    cid_map = defaultdict(list)
    for fname, (st, data) in parsed.items():
        if st == "ok" and isinstance(data, dict):
            cid = data.get("contentId")
            if isinstance(cid, str) and cid.strip():
                cid_map[cid].append(fname)

    rep = Report()
    agg = {"f2": [], "f3": [], "g_cards": set()}

    # 전역 중복 ERROR (지정 날짜 밖이어도 출력)
    dup_reported = 0
    for cid, fnames in sorted(cid_map.items()):
        if len(fnames) > 1:
            dup_reported += 1
            rep.error(fnames[0], "B", f"contentId 전역 중복: {cid}",
                      "파일: " + ", ".join(sorted(fnames)))

    # 검사 대상 (날짜 인수 있으면 그 날짜만)
    if date_arg:
        targets = [os.path.basename(p) for p in files
                   if os.path.basename(p).startswith(date_arg + "-")]
    else:
        targets = [os.path.basename(p) for p in files]

    # 카드별 검사 (예외로 죽지 않도록 방어)
    crashed = []
    for fname in targets:
        st, data = parsed[fname]
        if st == "fail":
            rep.error(fname, "A-0", f"json.load 실패: {data}")
            continue
        try:
            check_card(fname, data, rep, agg)
        except Exception as e:
            crashed.append((fname, f"{type(e).__name__}: {e}"))
            rep.error(fname, "EXC", f"검사 중 예외: {type(e).__name__}: {e}")

    # ── 출력 ──
    print(f"검사 대상 {len(targets)}장 (전체 로드 {len(files)}장)")
    if date_arg:
        print(f"날짜 필터: {date_arg}")
    print()
    code = rep.dump()

    # 항목별 ERROR 분포
    print()
    print("── ERROR 항목별 건수 ──")
    edist = rep.error_code_dist()
    for c in ("A-0", "A-1", "A-2", "A-3", "A-4", "B", "D", "F-1", "E", "EXC"):
        if edist.get(c):
            print(f"  {c}: {edist[c]}")
    print("── WARN 항목별 건수 ──")
    wdist = rep.warn_code_dist()
    for c in ("F-2", "F-3", "G", "H"):
        if wdist.get(c):
            print(f"  {c}: {wdist[c]}")

    # ── §4 집계 규칙: 고유 카드 수 기준 ──
    f2, f3 = agg["f2"], agg["f3"]
    f2_cards = {c for c, _, _ in f2}
    f3_cards = {c for c, _, _, _ in f3}
    union_cards = f2_cards | f3_cards
    both_cards = f2_cards & f3_cards

    print()
    print("── F-2/F-3 집계 (고유 카드 수 기준) ──")
    print(f"  F-2 경고 총건수: {len(f2)}")
    print(f"  F-3 경고 총건수: {len(f3)}")
    print(f"  F-2 또는 F-3 걸린 고유 카드 수: {len(union_cards)}")
    print(f"  F-2 와 F-3 동시 고유 카드 수: {len(both_cards)}")

    # 필드별 고유 카드 수 (F-2·F-3 합쳐서)
    field_cards = defaultdict(set)
    for c, _, field in f2:
        field_cards[field].add(c)
    for c, _, field, _ in f3:
        field_cards[field].add(c)
    print("  필드별 고유 카드 수:")
    for field in EN_SLOT_FIELDS:
        print(f"    {field}: {len(field_cards.get(field, set()))}")

    # 날짜별 고유 결함 카드 수
    date_cards = defaultdict(set)
    for c, d, _ in f2:
        date_cards[d].add(c)
    for c, d, _, _ in f3:
        date_cards[d].add(c)
    print("  날짜별 고유 결함 카드 수:")
    for d in sorted(date_cards):
        print(f"    {d}: {len(date_cards[d])}")

    # G 카드 수
    print()
    print(f"── G (isEn=false 인데 .en 존재) 고유 카드 수: {len(agg['g_cards'])} ──")

    # is_korean_slot 과탐 의심 (F-3) 3개까지
    print("── is_korean_slot 과탐 의심 사례 (F-3) 최대 3건 ──")
    if not f3:
        print("  (없음)")
    else:
        for c, d, field, sample in f3[:3]:
            print(f"  {c} · {field} · {d}")
            print(f"    en[:80]={sample!r}")

    # 예외 중단 여부
    print()
    if crashed:
        print(f"★예외 발생 카드 {len(crashed)}건 (검사는 계속됨):")
        for fname, err in crashed:
            print(f"  {fname}: {err}")
    else:
        print("★예외로 중단된 카드 없음 — 209장 전체 완주")

    return code


if __name__ == "__main__":
    sys.exit(main())
