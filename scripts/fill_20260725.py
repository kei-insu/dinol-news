#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7/25 카드 8장에 category / impactScore / positions 를 채우고 _todo 를 비운다.

동작:
- DATA 의 contentId 8개에 해당하는 content/news/*.json 만 수정한다.
- category.kr / category.en / impactScore / positions 를 교체하고 _todo 는 [] 로 설정한다.
- 나머지 필드는 건드리지 않는다.
- json.dump(..., ensure_ascii=False, indent=2), 끝 개행 없이 저장한다.
- DATA 키에 해당하는 파일이 없으면 오류 출력 후 종료코드 1 (파일 수정 없이 중단).
"""

import json
import sys
from pathlib import Path

DATA = {
    "20260725-ai-001": {
        "category_kr": "AI · 정책 · 산업", "category_en": "AI · Policy · Industry",
        "impactScore": 1, "positions": []
    },
    "20260725-ai-002": {
        "category_kr": "AI · 정책 · 오픈소스", "category_en": "AI · Policy · Open Source",
        "impactScore": 2, "positions": ["product-designer"]
    },
    "20260725-ai-003": {
        "category_kr": "AI · 툴 · 사용법", "category_en": "AI · Tool · How-to",
        "impactScore": 4, "positions": ["motion-designer", "video-designer"]
    },
    "20260725-ai-004": {
        "category_kr": "AI · 비즈니스 · M&A", "category_en": "AI · Business · M&A",
        "impactScore": 1, "positions": []
    },
    "20260725-design-001": {
        "category_kr": "디자인 · 브랜딩 · BX", "category_en": "Design · Branding · BX",
        "impactScore": 4, "positions": ["bx-designer", "brand-designer"]
    },
    "20260725-design-002": {
        "category_kr": "디자인 · 그래픽 · 타이포그래피", "category_en": "Design · Graphic · Typography",
        "impactScore": 3, "positions": ["typographer", "graphic-designer"]
    },
    "20260725-design-003": {
        "category_kr": "디자인 · 방법론 · AI 워크플로우", "category_en": "Design · Methodology · AI Workflow",
        "impactScore": 5, "positions": ["product-designer", "design-lead"]
    },
    "20260725-design-004": {
        "category_kr": "디자인 · 제품 · 테크", "category_en": "Design · Product · Tech",
        "impactScore": 2, "positions": ["industrial-designer"]
    },
}

NEWS_DIR = Path(__file__).resolve().parent.parent / "content" / "news"


def main():
    if not NEWS_DIR.is_dir():
        print(f"[오류] 디렉터리가 없습니다: {NEWS_DIR}", file=sys.stderr)
        return 1

    # 사전 검증: DATA 키에 해당하는 파일이 모두 있는지
    paths = {}
    missing = []
    for cid in DATA:
        p = NEWS_DIR / f"{cid}.json"
        if p.is_file():
            paths[cid] = p
        else:
            missing.append(cid)

    if missing:
        print("[오류] 파일이 없는 contentId:", file=sys.stderr)
        for cid in missing:
            print(f"  - {cid}", file=sys.stderr)
        print("\n파일을 수정하지 않고 중단합니다.", file=sys.stderr)
        return 1

    # 반영
    for cid, fields in DATA.items():
        path = paths[cid]
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        data.setdefault("category", {})
        data["category"]["kr"] = fields["category_kr"]
        data["category"]["en"] = fields["category_en"]
        data["impactScore"] = fields["impactScore"]
        data["positions"] = list(fields["positions"])
        data["_todo"] = []

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  갱신: {cid}  ★{fields['impactScore']}  positions={fields['positions']}")

    print(f"\n총 {len(DATA)}개 카드 갱신 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
