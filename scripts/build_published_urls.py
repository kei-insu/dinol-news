#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-07-25: 브리핑 카드 href 가 내부 상세 페이지 URL 로 변경되어
# HTML 에서 원문 URL 을 추출할 수 없다.
# 원문 URL 의 단일 진실 원천은 content/news/*.json 의 url 필드다.
# 대장은 누적 이력이므로 기존 항목을 삭제하지 않고 병합한다.
"""
발행 이력 대장(published_urls.json) 재생성.

출력 포맷 유지: { "기사URL": "YYYYMMDD" }  (URL → 최초 발행일)

★핵심★ published_urls.json 은 산출물이 아니라 누적된 중복 방지 이력이다.
JSON 코퍼스에 근거가 없다고 기존 항목을 지우지 않는다(과거 발행분·삭제된 카드·
수동 추가분·JSON 범위 밖 기록일 수 있다). 병합만 한다.

실행 순서(고정):
  ① .next 잔존 확인
  ② 입력 JSON 전수 검사
  ③ 기존 대장 검사
  ④ 충돌 검사
  ⑤ ERROR 있으면 임시 파일 만들지 않고 종료코드 1
  ⑥ generated → merged
  ⑦ published_urls.next.json 작성
  ⑧ 재읽기 검증
  ⑨ 원자적 교체
"""
import os
import re
import sys
import glob
import json
from datetime import datetime
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_GLOB = os.path.join(ROOT, "content", "news", "*.json")
OUTPUT_PATH = os.path.join(ROOT, "published_urls.json")
TEMP_PATH = os.path.join(ROOT, "published_urls.next.json")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_real_date(s, fmt):
    if not isinstance(s, str):
        return False
    try:
        datetime.strptime(s, fmt)
        return True
    except (ValueError, TypeError):
        return False


def main():
    errors = []   # (항목, 메시지)
    warns = []

    # ── ① .next 잔존 확인 (맨 처음) ──
    if os.path.exists(TEMP_PATH):
        print("[ERROR] published_urls.next.json 이 이미 존재합니다.")
        print("        이전 실패 결과일 수 있으니 확인 후 제거하세요.")
        return 1

    # ── ② 입력 JSON 전수 검사 ──
    files = sorted(glob.glob(NEWS_GLOB))
    records = []   # (contentId, url, yyyymmdd)
    dates_seen = set()
    read_ok = 0

    for path in files:
        fname = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            errors.append(("②JSON파싱", f"{fname}: 파싱 실패 {e}"))
            continue
        if not isinstance(data, dict):
            errors.append(("②최상위", f"{fname}: 최상위가 dict 아님"))
            continue
        read_ok += 1

        cid = data.get("contentId")
        url = data.get("url")
        date = data.get("date")

        ok_cid = isinstance(cid, str) and cid.strip() != ""
        ok_url = isinstance(url, str) and url.startswith(("http://", "https://"))
        ok_date = isinstance(date, str) and bool(DATE_RE.match(date)) and is_real_date(date, "%Y-%m-%d")

        if not ok_cid:
            errors.append(("②contentId", f"{fname}: contentId 누락/빈값"))
        if not ok_url:
            errors.append(("②url", f"{fname}: url 누락 또는 http(s) 아님: {url!r}"))
        if not ok_date:
            errors.append(("②date", f"{fname}: date 형식/실재 위반: {date!r}"))

        if ok_cid and ok_url and ok_date:
            ymd = date.replace("-", "")
            records.append((cid, url, ymd))
            dates_seen.add(date)

    # ── ③ 기존 대장 검증 ──
    existing = {}
    existing_load_note = ""
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, encoding="utf-8") as f:
                existing = json.load(f)
        except Exception as e:
            print(f"[ERROR] 기존 published_urls.json 파싱 실패: {e}")
            print("        (임시 파일을 만들지 않고 종료)")
            return 1
        if not isinstance(existing, dict):
            print("[ERROR] 기존 published_urls.json 의 최상위가 dict 아님")
            return 1
        for k, v in existing.items():
            if not (isinstance(k, str) and k.startswith(("http://", "https://"))):
                errors.append(("③기존키", f"기존 대장 키가 http(s) 문자열 아님: {k!r}"))
            if not (isinstance(v, str) and is_real_date(v, "%Y%m%d")):
                errors.append(("③기존값", f"기존 대장 값이 YYYYMMDD 실재 날짜 아님: {k!r} → {v!r}"))
    else:
        existing_load_note = "(기존 대장 없음 → 빈 dict 로 시작)"

    # ── ④ 충돌 검사 ──
    cid_urls = defaultdict(set)    # contentId -> {url}
    cid_dates = defaultdict(set)   # contentId -> {ymd}
    url_cids = defaultdict(set)    # url -> {contentId}
    for cid, url, ymd in records:
        cid_urls[cid].add(url)
        cid_dates[cid].add(ymd)
        url_cids[url].add(cid)

    for cid, urls in cid_urls.items():
        if len(urls) > 1:
            errors.append(("④id-url충돌", f"contentId {cid} 가 서로 다른 url {sorted(urls)}"))
    for cid, ds in cid_dates.items():
        if len(ds) > 1:
            errors.append(("④id-날짜충돌", f"contentId {cid} 가 여러 날짜 {sorted(ds)}"))
    dup_url_warns = []  # (url, [(cid, ymd), ...])
    for url, cids in url_cids.items():
        if len(cids) > 1:
            detail = sorted((cid, ymd) for cid, u, ymd in records if u == url)
            dup_url_warns.append((url, detail))
            warns.append(("④url중복", f"url 이 {len(cids)}개 contentId 에 등장: {url}"))

    # ── 기본 지표(ERROR 여부와 무관하게 먼저 산출) ──
    url_counter = Counter(u for _, u, _ in records)
    unique_urls = set(url_counter)
    dup_urls = {u: n for u, n in url_counter.items() if n > 1}
    dup_card_total = sum(dup_urls.values())
    excess = len(records) - len(unique_urls)

    print("=" * 60)
    print("발행 URL 대장 재생성 — content/news/*.json 기반")
    print("=" * 60)
    print("[기본 지표]")
    print(f"  1. 읽은 JSON 파일 수        : {read_ok} / {len(files)}")
    print(f"  2. 고유 날짜 수             : {len(dates_seen)}")
    print(f"  3. 전체 카드 URL 수         : {len(records)}")
    print(f"  4. 고유 URL 수             : {len(unique_urls)}")
    print(f"  5. 중복 URL 종수           : {len(dup_urls)}")
    print(f"  6. 중복 해당 전체 카드 수   : {dup_card_total}")
    print(f"  7. 고유 URL 대비 초과 출현  : {excess}")

    print("\n[중복 URL 상세 (WARN)]")
    if dup_url_warns:
        for url, detail in sorted(dup_url_warns):
            print(f"  · {url}  (등장 {len(detail)}회)")
            for cid, ymd in detail:
                print(f"      - {cid} · {ymd}")
    else:
        print("  (중복 URL 없음)")

    if existing_load_note:
        print(f"\n[기존 대장] {existing_load_note}")
    else:
        print(f"\n[기존 대장] {len(existing)}개 키 검증 완료")

    # ── ⑤ ERROR 있으면 종료(임시 파일 없이) ──
    print("\n[ERROR 목록]")
    if errors:
        by_cat = defaultdict(list)
        for cat, msg in errors:
            by_cat[cat].append(msg)
        for cat in sorted(by_cat):
            print(f"  {cat}: {len(by_cat[cat])}건")
            for msg in by_cat[cat][:10]:
                print(f"     - {msg}")
        print(f"\n[중단] ERROR {len(errors)}건 → 임시 파일을 만들지 않고 종료코드 1")
        return 1
    else:
        print("  (없음)")

    # ── ⑥ generated → merged ──
    generated = {}
    for cid, url, ymd in records:
        if url not in generated:
            generated[url] = ymd
        else:
            generated[url] = min(
                datetime.strptime(generated[url], "%Y%m%d"),
                datetime.strptime(ymd, "%Y%m%d"),
            ).strftime("%Y%m%d")

    merged = dict(existing)
    for url, date in generated.items():
        if url not in merged:
            merged[url] = date
        else:
            merged[url] = min(
                datetime.strptime(merged[url], "%Y%m%d"),
                datetime.strptime(date, "%Y%m%d"),
            ).strftime("%Y%m%d")

    # ── §3 기존 대장과 3집합 대조 ──
    existing_urls = set(existing)
    generated_urls = set(generated)
    existing_only = existing_urls - generated_urls
    generated_only = generated_urls - existing_urls
    common = existing_urls & generated_urls

    same_date = []
    existing_earlier = []
    generated_earlier = []
    for u in common:
        ev, gv = existing[u], generated[u]
        if ev == gv:
            same_date.append(u)
        elif datetime.strptime(ev, "%Y%m%d") < datetime.strptime(gv, "%Y%m%d"):
            existing_earlier.append((u, ev, gv))
        else:
            generated_earlier.append((u, ev, gv))

    print("\n" + "=" * 60)
    print("[3집합 대조: 기존 대장 ↔ JSON 생성]")
    print("=" * 60)
    print(f"  common          : {len(common)}")
    print(f"    same_date        : {len(same_date)}")
    print(f"    existing_earlier : {len(existing_earlier)}")
    print(f"    generated_earlier: {len(generated_earlier)}")
    for u, ev, gv in existing_earlier[:20]:
        print(f"      [기존이 이름] {u}  기존={ev} 생성={gv}")
    for u, ev, gv in generated_earlier[:20]:
        print(f"      [생성이 이름] {u}  기존={ev} 생성={gv}")
    print(f"  generated_only  : {len(generated_only)}")
    for u in sorted(generated_only)[:20]:
        print(f"      + {u}  ({generated[u]})")
    print(f"  existing_only   : {len(existing_only)}")
    for u in sorted(existing_only):
        print(f"      · {u}  최초발행일={existing[u]}")
        print(f"        현재 JSON 코퍼스에서 근거를 찾지 못한 기존 발행 이력")

    # ── ⑦ 임시 파일 작성 ──
    with open(TEMP_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    # ── ⑧ 재읽기 검증 ──
    with open(TEMP_PATH, encoding="utf-8") as f:
        written = json.load(f)
    if written != merged:
        print("\n[ERROR] 임시 대장 재검증 불일치 → 교체하지 않음")
        return 1

    # ── ⑨ 원자적 교체 ──
    os.replace(TEMP_PATH, OUTPUT_PATH)

    print("\n" + "=" * 60)
    print("[완료]")
    print(f"  merged 대장 항목 수 : {len(merged)}  (기존 {len(existing)} + 신규 {len(merged) - len(existing)})")
    print(f"  재읽기 검증        : 통과")
    print(f"  원자적 교체        : 완료 (published_urls.json)")
    print(f"  .next 잔존         : {'있음(문제)' if os.path.exists(TEMP_PATH) else '없음'}")
    print(f"  existing_only      : {len(existing_only)}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
