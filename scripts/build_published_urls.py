#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-07-25: 브리핑 카드 href 가 내부 상세 페이지 URL 로 변경되어
# HTML 에서 원문 URL 을 추출할 수 없다.
# 원문 URL 의 단일 진실 원천은 content/news/*.json 의 url 필드다.
# 대장은 누적 이력이므로 기존 항목을 삭제하지 않고 병합한다.
"""
발행 이력 대장(published_urls.json) 재생성 — 매일 돌아가는 영구 운영 스크립트.

출력 포맷 유지: { "기사URL": "YYYYMMDD" }  (URL → 최초 발행일)

★핵심★ published_urls.json 은 산출물이 아니라 누적된 중복 방지 이력이다.
JSON 코퍼스에 근거가 없다고 기존 항목을 지우지 않는다. 병합만 한다.

일회성 마이그레이션 검증(main·특정 날짜 비교 등)은 이 파일에 넣지 않는다.
→ git·main 브랜치·BeautifulSoup·특정 날짜에 영구 의존하게 되기 때문.

실행 순서:
  ① .next 잔존 확인 → 있으면 종료코드 1
  ② 입력 JSON 검사
  ③ 기존 대장 검사 + 원본 바이트 보관
  ④ contentId 충돌·중복
  ⑤ ERROR 있으면 임시 파일 없이 종료
  ⑥ generated → merged
  ⑦ .next 작성
  ⑧ 후보 재읽기
  ⑨ 원자적 교체(예외 처리)
  ⑩ 최종 재읽기(예외·불일치 모두 복구)
"""
import os
import sys
import glob
import json
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEWS_GLOB = str(ROOT / "content" / "news" / "*.json")
OUTPUT_PATH = ROOT / "published_urls.json"
TEMP_PATH = ROOT / "published_urls.next.json"


def parse_date(value, fmt):
    """strftime 왕복까지 확인(예: 2026-7-25 · 2026-02-31 차단)."""
    try:
        parsed = datetime.strptime(value, fmt)
    except (ValueError, TypeError):
        return None
    if parsed.strftime(fmt) != value:
        return None
    return parsed


def restore_existing_ledger(output_path, existing_bytes):
    """실패 시 기존 대장 상태로 복구. 쓰기와 재검증을 같은 try 안에서 수행."""
    try:
        if existing_bytes is not None:
            output_path.write_bytes(existing_bytes)
            restored_ok = output_path.read_bytes() == existing_bytes
        else:
            output_path.unlink(missing_ok=True)
            restored_ok = not output_path.exists()
    except OSError as exc:
        print(f"[FATAL] 기존 대장 복구 또는 복구 검증 실패: {exc}")
        return False
    if not restored_ok:
        print("[FATAL] 복구 후 원본 상태 검증 실패")
        return False
    print("[RECOVERED] 기존 published_urls.json 상태를 복구했습니다.")
    return True


def main():
    # ── ① .next 잔존 확인 ──
    if TEMP_PATH.exists():
        print("[ERROR] published_urls.next.json 이 이미 존재합니다.")
        print("        이전 실패 결과일 수 있으니 확인 후 제거하세요.")
        return 1

    errors = []

    # ── ② 입력 JSON 검사 ──
    files = sorted(glob.glob(NEWS_GLOB))
    records = []   # (cid, url, ymd, fname)
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
        pd = parse_date(date, "%Y-%m-%d")

        if not ok_cid:
            errors.append(("②contentId", f"{fname}: contentId 누락/빈값"))
        if not ok_url:
            errors.append(("②url", f"{fname}: url 누락 또는 http(s) 아님: {url!r}"))
        if pd is None:
            errors.append(("②date", f"{fname}: date 형식/실재 위반: {date!r}"))

        if ok_cid and ok_url and pd is not None:
            records.append((cid, url, date.replace("-", ""), fname))
            dates_seen.add(date)

    # ── ③ 기존 대장 검증 + 원본 바이트 보관 ──
    existing = {}
    existing_bytes = OUTPUT_PATH.read_bytes() if OUTPUT_PATH.exists() else None
    existing_note = ""
    if existing_bytes is not None:
        try:
            existing = json.loads(existing_bytes.decode("utf-8-sig"))
        except Exception as e:
            print(f"[ERROR] 기존 published_urls.json 파싱 실패: {e}")
            print("        (임시 파일을 만들지 않고 종료)")
            return 1
        if not isinstance(existing, dict):
            print("[ERROR] 기존 published_urls.json 의 최상위가 dict 아님")
            return 1
        for k, v in existing.items():
            if not (isinstance(k, str) and k.startswith(("http://", "https://"))):
                errors.append(("③기존키", f"기존 대장 키가 http(s) URL 아님: {k!r}"))
            if parse_date(v, "%Y%m%d") is None:
                errors.append(("③기존값", f"기존 대장 값이 YYYYMMDD 실재 날짜 아님: {k!r} → {v!r}"))
    else:
        existing_note = "(기존 대장 없음 → 빈 dict 로 시작)"

    # ── ④ contentId 충돌(세 유형) + url 중복 WARN ──
    cid_files = defaultdict(list)
    cid_urls = defaultdict(set)
    cid_dates = defaultdict(set)
    url_cids = defaultdict(set)
    for cid, url, ymd, fname in records:
        cid_files[cid].append(fname)
        cid_urls[cid].add(url)
        cid_dates[cid].add(ymd)
        url_cids[url].add(cid)

    n_dupfile = n_diffurl = n_diffdate = 0
    for cid, fnames in cid_files.items():
        if len(fnames) > 1:
            n_dupfile += 1
            errors.append(("④id-중복파일", f"contentId {cid} 가 여러 파일에 저장됨: {sorted(fnames)}"))
    for cid, urls in cid_urls.items():
        if len(urls) > 1:
            n_diffurl += 1
            errors.append(("④id-다른url", f"contentId {cid} 가 서로 다른 url: {sorted(urls)}"))
    for cid, ds in cid_dates.items():
        if len(ds) > 1:
            n_diffdate += 1
            errors.append(("④id-다른date", f"contentId {cid} 가 여러 날짜: {sorted(ds)}"))

    dup_url_detail = []
    for url, cids in url_cids.items():
        if len(cids) > 1:
            detail = sorted((c, y) for c, u, y, f in records if u == url)
            dup_url_detail.append((url, detail))

    # ── 기본 지표 ──
    url_counter = Counter(u for _, u, _, _ in records)
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
    if dup_url_detail:
        for url, detail in sorted(dup_url_detail):
            print(f"  · {url}  (등장 {len(detail)}회)")
            for c, y in detail:
                print(f"      - {c} · {y}")
    else:
        print("  (중복 URL 없음)")

    print(f"\n[기존 대장] {existing_note if existing_note else f'{len(existing)}개 키 검증'}")
    print(f"[contentId 충돌] 중복파일 {n_dupfile} · 다른url {n_diffurl} · 다른date {n_diffdate}")
    print(f"[URL 중복 WARN] {len(dup_url_detail)}종")

    # ── ⑤ ERROR gate ──
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
    print("  (없음)")

    # ── ⑥ generated → merged ──
    generated = {}
    for cid, url, ymd, fname in records:
        if url not in generated:
            generated[url] = ymd
        else:
            generated[url] = min(
                parse_date(generated[url], "%Y%m%d"),
                parse_date(ymd, "%Y%m%d"),
            ).strftime("%Y%m%d")

    merged = dict(existing)
    for url, date in generated.items():
        if url not in merged:
            merged[url] = date
        else:
            merged[url] = min(
                parse_date(merged[url], "%Y%m%d"),
                parse_date(date, "%Y%m%d"),
            ).strftime("%Y%m%d")

    # ── §2 3집합 대조 ──
    existing_urls = set(existing)
    generated_urls = set(generated)
    existing_only = existing_urls - generated_urls
    generated_only = generated_urls - existing_urls
    common = existing_urls & generated_urls
    same_date, existing_earlier, generated_earlier = [], [], []
    for u in common:
        ev, gv = existing[u], generated[u]
        if ev == gv:
            same_date.append(u)
        elif parse_date(ev, "%Y%m%d") < parse_date(gv, "%Y%m%d"):
            existing_earlier.append((u, ev, gv))
        else:
            generated_earlier.append((u, ev, gv))

    print("\n" + "=" * 60)
    print("[3집합 대조: 기존 대장 ↔ JSON 생성]")
    print("=" * 60)
    print(f"  common          : {len(common)}  (same_date {len(same_date)} · "
          f"existing_earlier {len(existing_earlier)} · generated_earlier {len(generated_earlier)})")
    for u, ev, gv in existing_earlier[:20]:
        print(f"    [기존이 이름] {u}  기존={ev} 생성={gv}")
    for u, ev, gv in generated_earlier[:20]:
        print(f"    [생성이 이름] {u}  기존={ev} 생성={gv}")
    print(f"  generated_only  : {len(generated_only)}")
    for u in sorted(generated_only)[:20]:
        print(f"    + {u}  ({generated[u]})")
    print(f"  existing_only   : {len(existing_only)}")
    for u in sorted(existing_only):
        print(f"    · {u}  최초발행일={existing[u]}  "
              f"(현재 JSON 코퍼스에서 근거를 찾지 못한 기존 발행 이력)")

    # 병합 후 항목 수 감소 금지
    if len(merged) < len(existing):
        print(f"\n[ERROR] 병합 후 항목 수 감소: {len(existing)} → {len(merged)}")
        return 1
    print(f"\n[항목 수] 기존 {len(existing)} → 병합 {len(merged)} (감소 없음)")

    # ── ⑦ .next 작성 ──
    with open(TEMP_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    # ── ⑧ 후보 재읽기 ──
    with open(TEMP_PATH, encoding="utf-8") as f:
        candidate = json.load(f)
    if candidate != merged:
        print("[ERROR] 후보(.next) 대장 재검증 불일치 → 교체하지 않음")
        return 1
    print("[⑧] 후보 재읽기 검증 일치")

    # ── ⑨ 원자적 교체(예외 처리) ──
    try:
        TEMP_PATH.replace(OUTPUT_PATH)
    except OSError as exc:
        print(f"[ERROR] 원자적 교체 실패: {exc}")
        print("        기존 대장은 유지되고 .next 가 남습니다. 자동 삭제하지 않습니다(진단 상태).")
        return 1
    print("[⑨] 원자적 교체 완료")

    # ── ⑩ 최종 재읽기(예외·불일치 모두 복구) ──
    try:
        with OUTPUT_PATH.open("r", encoding="utf-8") as f:
            final = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"[ERROR] 최종 대장 재읽기 실패: {exc}")
        if not restore_existing_ledger(OUTPUT_PATH, existing_bytes):
            print("[FATAL] 수동 복구가 필요합니다.")
        return 1

    if final != merged:
        print("[ERROR] 최종 대장 교체 후 내용 불일치")
        if not restore_existing_ledger(OUTPUT_PATH, existing_bytes):
            print("[FATAL] 수동 복구가 필요합니다.")
        return 1

    print("[PASS] 최종 대장 재읽기 검증 일치")

    print("\n" + "=" * 60)
    print("[완료]")
    print(f"  merged 항목 수 : {len(merged)}  (기존 {len(existing)} + 신규 {len(merged) - len(existing)})")
    print(f"  .next 잔존     : {'있음(문제)' if TEMP_PATH.exists() else '없음'}")
    print(f"  existing_only  : {len(existing_only)}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
