#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fill_en_slots.py — EN 카드 8장의 영문 슬롯 13개를 채운다.

- EN_SLOTS 의 contentId 파일을 열어 지정 필드의 .en 만 교체
- 나머지 필드는 건드리지 않는다
- json.dump(..., ensure_ascii=False, indent=2), 끝 개행 없이 저장
- 대상 파일이 없으면 오류 후 종료코드 1
- 수정 전후 content/news/*.json 전체 해시를 비교해 정확히 8개만 바뀌었는지 검증
"""

import sys
import json
import glob
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "content" / "news"

EN_SLOTS = {
"20260720-ai-001": {
  "comment": "Netflix paying in the $500M range rather than the $60M range for Ben Affleck's AI filmmaking startup reads less like an experimental bet and more like a serious wager on production infrastructure. The pattern of content giants absorbing AI production tools in-house is likely to accelerate.\n\nFor designers and planners, the point worth noting is that the question of where AI substitutes and where humans remain is now reaching high-involvement creative territory like filmmaking. The deal figure and the startup's specific technical stack are still snippet-level information, so confirming against the official announcement is advisable."
},
"20260720-ai-004": {
  "comment": "More notable than the one-trillion-yen figure itself is the shift it signals: governments are now treating physical AI as a national strategic agenda on par with semiconductors and infrastructure. Read alongside Korea's physical AI alliance discussions, this looks like the outline of a regional competition.\n\nThat said, the detailed execution plan behind the investment announcement and the list of specific beneficiary companies are not visible in the snippet, so verification against the actual policy documents is needed."
},
"20260720-design-001": {
  "comment": "What makes this interesting is that a studio behind the Lunark lunar habitat experiment and ISS lighting systems applied the logic of space habitation, arguably the most constrained architecture there is, directly to a summer house. The claimed 80 percent reduction in carbon emissions reads as a case where the resource-efficiency thinking native to space architecture translated into measurable results.\n\nThe combination of compact living, bio-based materials and digital fabrication offers plenty to draw on for small houses and second homes in Korea. Details such as construction cost or post-occupancy feedback are not confirmable from the snippet alone, so anyone interested should check the original article and sources like ArchDaily."
},
"20260720-design-004": {
  "comment": "Where smart home discourse usually collapses into a spec race over devices and automation, Moooi starts from a different question: how does it feel to walk into this space. The installation layering light, movement and scent in collaboration with a choreographer reads as an attempt to redefine interiors as sensory experience.\n\nThe collaboration with Everyhuman, which uses AI to translate mood into scent, is a reminder that AI does not have to arrive as a screen or an automation feature. Whether this collaboration is a commercial product or an exhibition concept is not clear from the snippet, so the original article is worth checking."
},
"20260725-ai-002": {
  "summary": "An open letter signed by Hugging Face, Meta, Microsoft, Mistral and Nvidia urges policymakers not to impose broad restrictions across open-weight models as the US shapes its response to Chinese AI.",
  "points": [
    "Open letter signed by a big tech coalition including Meta, Microsoft, Mistral and Nvidia",
    "Urges against open-weight restrictions amid debate over responding to Chinese AI",
    "Follows the policy thread running from June's pre-deployment testing executive order"
  ]
},
"20260725-ai-004": {
  "summary": "Midjourney, the AI lab best known for its image and video generation models, has acquired the social astrology app Co-Star.",
  "points": [
    "Midjourney acquires the social astrology app Co-Star",
    "Expands from image and video generation into lifestyle apps",
    "A case of an AI lab diversifying into consumer-facing brands"
  ],
  "recommend": "Useful as a light industry-trend reference · Save if relevant"
},
"20260725-design-002": {
  "points": [
    "Introduces a way of working that treats typography as image",
    "Builds a visual world through lettering alone, without illustration or photography",
    "Spotlighted as an emerging studio in It's Nice That's Discover column"
  ],
  "recommend": "Worth saving as a source for typography and branding moodboards"
},
"20260725-design-004": {
  "points": [
    "Light Flip, a $299 5G clamshell phone, has launched",
    "Attempts to shape usage habits through form factor rather than screen-time apps",
    "Part of a growing category of simplified devices aimed at digital detox"
  ],
  "recommend": "Save as reference for digital wellbeing and minimal device planning"
}
}


def hash_all():
    out = {}
    for p in sorted(NEWS_DIR.glob("*.json")):
        out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main():
    if not NEWS_DIR.is_dir():
        print(f"[오류] 디렉터리 없음: {NEWS_DIR}", file=sys.stderr)
        return 1

    # 대상 파일 존재 확인 (수정 전에 일괄)
    missing = [cid for cid in EN_SLOTS if not (NEWS_DIR / f"{cid}.json").is_file()]
    if missing:
        print("[오류] 대상 파일 없음:", file=sys.stderr)
        for cid in missing:
            print(f"  - {cid}", file=sys.stderr)
        return 1

    before = hash_all()

    field_count = 0
    for cid, fields in EN_SLOTS.items():
        path = NEWS_DIR / f"{cid}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for field, value in fields.items():
            if not isinstance(data.get(field), dict):
                print(f"[오류] {cid}: '{field}' 가 객체가 아님", file=sys.stderr)
                return 1
            data[field]["en"] = value
            field_count += 1
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  갱신: {cid}  필드={list(fields.keys())}")

    after = hash_all()

    # 전후 해시 비교
    changed = sorted(k for k in before if before[k] != after.get(k))
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))

    print(f"\n필드 교체 수: {field_count} (기대 13)")
    print(f"변경된 파일 수: {len(changed)} (기대 8)")
    for k in changed:
        print(f"  * {k}")
    if added:
        print(f"[경고] 새로 생긴 파일: {added}")
    if removed:
        print(f"[경고] 사라진 파일: {removed}")

    expected = {f"{cid}.json" for cid in EN_SLOTS}
    if set(changed) != expected or added or removed:
        print("[오류] 변경 파일 집합이 대상 8개와 다릅니다.", file=sys.stderr)
        print(f"  기대: {sorted(expected)}", file=sys.stderr)
        print(f"  실제: {changed}", file=sys.stderr)
        return 1

    print("[성공] 정확히 대상 8개 파일만 변경됨")
    return 0


if __name__ == "__main__":
    sys.exit(main())
