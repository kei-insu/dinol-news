#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
발행 이력 대장(published_urls.json) 재생성 스크립트.

모든 브리핑(news/**/Dinol_news_*.html)에서 카드 URL을 추출해
{ "URL": "최초발행일(YYYYMMDD)" } 형태로 저장한다.

- 중복 발행 방지의 '원본 데이터'.
- 새 브리핑 발행 후 이 스크립트를 다시 돌리면 최신 상태로 갱신됨.
- 여러 브리핑에 중복 등장한 URL이 있으면 경고로 알려준다.

사용법 (레포 루트에서):
    python scripts/build_published_urls.py
"""
import re, json, glob
from collections import Counter

CARD_HREF = re.compile(r'<a\s+class="card[^"]*"\s+href="(https?://[^"]+)"')
DATE_RE   = re.compile(r'Dinol_news_(\d{8})\.html')

def main():
    files = sorted(glob.glob("news/**/Dinol_news_*.html", recursive=True))
    if not files:
        print("브리핑 파일을 찾지 못했습니다. 레포 루트에서 실행하세요.")
        return

    ledger = {}          # URL -> 최초 발행일
    all_refs = []        # 중복 탐지용 (URL, date)
    for f in files:
        m = DATE_RE.search(f)
        date = m.group(1) if m else "00000000"
        html = open(f, encoding="utf-8").read()
        for href in CARD_HREF.findall(html):
            all_refs.append(href)
            if href not in ledger or date < ledger[href]:
                ledger[href] = date   # 가장 이른 날짜를 최초 발행일로

    # 저장 (URL 알파벳순으로 정렬해 diff 안정화)
    ordered = dict(sorted(ledger.items()))
    json.dump(ordered, open("published_urls.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # 리포트
    dup = {u: n for u, n in Counter(all_refs).items() if n > 1}
    print(f"브리핑 {len(files)}개 스캔 · 고유 URL {len(ledger)}개 → published_urls.json 저장")
    if dup:
        print(f"\n⚠️ 여러 브리핑에 중복 등장한 URL {len(dup)}개 (이미 발행된 중복):")
        for u, n in sorted(dup.items(), key=lambda x: -x[1]):
            print(f"  [{n}회] {u}")
        print("→ 앞으로 루틴이 published_urls.json을 대조하면 이런 중복을 막을 수 있습니다.")
    else:
        print("중복 등장 URL 없음.")

if __name__ == "__main__":
    main()
