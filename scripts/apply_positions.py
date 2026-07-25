#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content/news/ 카드에 positions(연관 디자인 직무) 를 반영한다.

동작:
1. POSITIONS_MAP 의 contentId 에 해당하는 카드의 positions 를 새 값으로 교체한다.
   (지금은 AI 104장만 포함. Design 분량은 추후 추가)
2. _todo 에서 "positions" 를 제거한다.
3. 나머지 필드는 건드리지 않는다.
4. json.dump(..., ensure_ascii=False, indent=2), 끝 개행 없이 저장한다.

사전 검증 (하나라도 실패하면 파일 수정 없이 종료코드 1):
- POSITIONS_MAP 값에 VALID_POSITIONS 밖의 ID 가 있으면 오류
- 한 카드에 3개 이상이면 오류
- POSITIONS_MAP 에 있는데 파일이 없으면 오류

실행 후 출력:
- 부여 장수 / 생략 장수
- 직무별 사용 빈도
- _todo 에 "positions" 남은 카드 수
"""

import json
import sys
from collections import Counter
from pathlib import Path

VALID_POSITIONS = {
    "ux-designer", "ui-designer", "product-designer", "service-designer",
    "brand-designer", "bx-designer", "graphic-designer", "editorial-designer",
    "motion-designer", "video-designer", "illustrator", "art-director",
    "industrial-designer", "space-designer", "architect", "package-designer",
    "typographer", "fashion-designer", "design-lead", "design-manager",
}

POSITIONS_MAP = {
    "20260701-ai-001": [], "20260701-ai-002": [], "20260701-ai-003": [],
    "20260701-ai-004": ["product-designer"], "20260701-ai-005": [],
    "20260701-ai-006": ["graphic-designer", "illustrator"], "20260701-ai-007": [],
    "20260702-ai-001": [], "20260702-ai-002": [], "20260702-ai-003": [],
    "20260702-ai-004": [], "20260702-ai-005": [], "20260702-ai-006": [], "20260702-ai-007": [],
    "20260703-ai-001": ["product-designer"], "20260703-ai-002": [], "20260703-ai-003": [],
    "20260703-ai-004": [], "20260703-ai-005": [], "20260703-ai-006": [], "20260703-ai-007": [],
    "20260704-ai-001": ["product-designer", "service-designer"], "20260704-ai-002": [],
    "20260704-ai-003": ["ux-designer", "product-designer"], "20260704-ai-004": [],
    "20260705-ai-001": [], "20260705-ai-002": ["illustrator", "graphic-designer"],
    "20260706-ai-001": ["graphic-designer", "art-director"], "20260706-ai-002": ["art-director"],
    "20260706-ai-003": ["brand-designer"], "20260706-ai-004": ["product-designer"],
    "20260706-ai-005": ["ui-designer", "ux-designer"],
    "20260707-ai-001": [], "20260707-ai-002": [], "20260707-ai-003": [],
    "20260707-ai-004": ["product-designer"],
    "20260708-ai-001": [], "20260708-ai-002": ["design-lead", "design-manager"],
    "20260708-ai-003": [], "20260708-ai-004": ["product-designer", "ux-designer"],
    "20260709-ai-001": ["product-designer"], "20260709-ai-002": ["design-lead"],
    "20260709-ai-003": [], "20260709-ai-004": [],
    "20260710-ai-001": ["product-designer"], "20260710-ai-002": ["product-designer"],
    "20260710-ai-003": ["product-designer"], "20260710-ai-004": [],
    "20260711-ai-001": ["graphic-designer", "illustrator"], "20260711-ai-002": [],
    "20260711-ai-003": [], "20260711-ai-004": ["ux-designer", "service-designer"],
    "20260712-ai-001": ["product-designer"], "20260712-ai-002": ["product-designer"],
    "20260712-ai-003": [], "20260712-ai-004": [],
    "20260713-ai-001": [], "20260713-ai-002": [], "20260713-ai-003": [], "20260713-ai-004": [],
    "20260714-ai-001": [], "20260714-ai-002": ["service-designer"],
    "20260714-ai-003": ["design-lead", "design-manager"], "20260714-ai-004": [],
    "20260715-ai-001": ["product-designer"], "20260715-ai-002": [],
    "20260715-ai-003": [], "20260715-ai-004": [],
    "20260716-ai-001": [], "20260716-ai-002": ["design-lead"],
    "20260716-ai-003": ["product-designer"], "20260716-ai-004": [],
    "20260717-ai-001": [], "20260717-ai-002": [],
    "20260717-ai-003": ["product-designer"], "20260717-ai-004": [],
    "20260718-ai-001": ["product-designer"], "20260718-ai-002": ["brand-designer", "product-designer"],
    "20260718-ai-003": [], "20260718-ai-004": [],
    "20260719-ai-001": [], "20260719-ai-002": [],
    "20260719-ai-003": ["motion-designer", "video-designer"], "20260719-ai-004": [],
    "20260720-ai-001": ["video-designer", "motion-designer"],
    "20260720-ai-002": ["art-director", "graphic-designer"],
    "20260720-ai-003": ["ui-designer", "ux-designer"], "20260720-ai-004": [],
    "20260721-ai-001": ["product-designer"], "20260721-ai-002": ["design-lead"],
    "20260721-ai-003": [], "20260721-ai-004": ["industrial-designer", "space-designer"],
    "20260722-ai-001": [], "20260722-ai-002": ["illustrator", "graphic-designer"],
    "20260722-ai-003": [], "20260722-ai-004": [],
    "20260723-ai-001": [], "20260723-ai-002": ["product-designer"],
    "20260723-ai-003": [], "20260723-ai-004": [],
    "20260724-ai-001": [], "20260724-ai-002": ["illustrator", "graphic-designer"],
    "20260724-ai-003": ["brand-designer"], "20260724-ai-004": ["design-lead", "product-designer"],

    "20260701-design-001": [], "20260701-design-002": ["brand-designer", "industrial-designer"],
    "20260701-design-003": ["art-director"], "20260701-design-004": [],
    "20260701-design-005": ["architect"], "20260701-design-006": ["brand-designer", "typographer"],
    "20260701-design-007": [],
    "20260702-design-001": ["brand-designer", "graphic-designer"],
    "20260702-design-002": ["architect", "space-designer"], "20260702-design-003": ["industrial-designer"],
    "20260702-design-004": ["space-designer", "architect"], "20260702-design-005": ["architect"],
    "20260702-design-006": ["industrial-designer"],
    "20260703-design-001": ["space-designer"], "20260703-design-002": ["industrial-designer"],
    "20260703-design-003": ["graphic-designer"], "20260703-design-004": ["design-lead", "brand-designer"],
    "20260704-design-001": [], "20260704-design-002": ["industrial-designer", "graphic-designer"],
    "20260705-design-001": ["industrial-designer"], "20260705-design-002": ["industrial-designer"],
    "20260705-design-003": ["industrial-designer"],
    "20260706-design-001": ["brand-designer", "graphic-designer"],
    "20260706-design-002": ["brand-designer", "space-designer"],
    "20260706-design-003": ["brand-designer", "bx-designer"],
    "20260707-design-001": ["architect"], "20260707-design-002": ["industrial-designer"],
    "20260707-design-003": ["industrial-designer"], "20260707-design-004": ["industrial-designer"],
    "20260708-design-001": ["architect"], "20260708-design-002": ["industrial-designer"],
    "20260708-design-003": ["architect"], "20260708-design-004": ["industrial-designer"],
    "20260709-design-001": ["architect"], "20260709-design-002": ["industrial-designer"],
    "20260709-design-003": [], "20260709-design-004": ["motion-designer", "art-director"],
    "20260710-design-001": ["architect"], "20260710-design-002": ["industrial-designer"],
    "20260710-design-003": ["industrial-designer"], "20260710-design-004": ["architect"],
    "20260711-design-001": ["architect", "space-designer"], "20260711-design-002": ["design-lead"],
    "20260711-design-003": ["industrial-designer"], "20260711-design-004": ["architect"],
    "20260712-design-001": ["industrial-designer"], "20260712-design-002": ["fashion-designer"],
    "20260712-design-003": ["architect", "space-designer"], "20260712-design-004": ["architect"],
    "20260713-design-001": ["architect"], "20260713-design-002": ["architect"],
    "20260713-design-003": ["typographer", "brand-designer"],
    "20260713-design-004": ["editorial-designer", "graphic-designer"],
    "20260714-design-001": ["industrial-designer", "ux-designer"], "20260714-design-002": ["architect"],
    "20260714-design-003": ["space-designer"], "20260714-design-004": ["industrial-designer"],
    "20260715-design-001": ["architect"], "20260715-design-002": ["industrial-designer"],
    "20260715-design-003": ["architect"], "20260715-design-004": ["industrial-designer", "ux-designer"],
    "20260716-design-001": ["industrial-designer"], "20260716-design-002": ["industrial-designer"],
    "20260716-design-003": ["architect"], "20260716-design-004": ["package-designer", "brand-designer"],
    "20260717-design-001": ["architect"], "20260717-design-002": ["architect"],
    "20260717-design-003": ["illustrator", "editorial-designer"], "20260717-design-004": ["industrial-designer"],
    "20260718-design-001": ["fashion-designer"], "20260718-design-002": ["architect"],
    "20260718-design-003": ["typographer", "graphic-designer"], "20260718-design-004": ["industrial-designer"],
    "20260719-design-001": ["package-designer", "brand-designer"], "20260719-design-002": ["architect"],
    "20260719-design-003": [], "20260719-design-004": ["architect"],
    "20260720-design-001": ["architect", "space-designer"], "20260720-design-002": ["bx-designer", "brand-designer"],
    "20260720-design-003": ["brand-designer", "graphic-designer"],
    "20260720-design-004": ["space-designer", "brand-designer"],
    "20260721-design-001": [], "20260721-design-002": ["architect"],
    "20260721-design-003": ["bx-designer", "graphic-designer"],
    "20260721-design-004": ["illustrator", "graphic-designer"],
    "20260722-design-001": ["industrial-designer"], "20260722-design-002": ["ux-designer", "service-designer"],
    "20260722-design-003": ["architect"], "20260722-design-004": ["space-designer", "bx-designer"],
    "20260723-design-001": ["architect"], "20260723-design-002": ["brand-designer", "bx-designer"],
    "20260723-design-003": [], "20260723-design-004": ["art-director"],
    "20260724-design-001": ["architect"], "20260724-design-002": ["industrial-designer"],
    "20260724-design-003": ["ui-designer", "ux-designer"],
    "20260724-design-004": ["editorial-designer", "brand-designer"],
}

NEWS_DIR = Path(__file__).resolve().parent.parent / "content" / "news"


def main():
    if not NEWS_DIR.is_dir():
        print(f"[오류] 디렉터리가 없습니다: {NEWS_DIR}", file=sys.stderr)
        return 1

    # 사전 검증 1·2: VALID_POSITIONS 밖 ID / 카드당 3개 이상
    errors = []
    for cid, positions in POSITIONS_MAP.items():
        invalid = [p for p in positions if p not in VALID_POSITIONS]
        if invalid:
            errors.append(f"[오류] {cid}: 허용되지 않은 직무 ID {invalid}")
        if len(positions) >= 3:
            errors.append(f"[오류] {cid}: positions 가 3개 이상 ({len(positions)}개)")

    # 파일 인덱싱 (contentId -> (path, data))
    files_by_id = {}
    for path in sorted(NEWS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        files_by_id[data["contentId"]] = (path, data)

    # 사전 검증 3: POSITIONS_MAP 에 있으나 파일 없음
    missing_files = sorted(set(POSITIONS_MAP) - set(files_by_id))
    for cid in missing_files:
        errors.append(f"[오류] 파일이 없는 contentId: {cid}")

    # 사전 검증 4: 전체 커버리지 — 파일에 있으나 POSITIONS_MAP 에 없음
    missing_map = sorted(set(files_by_id) - set(POSITIONS_MAP))
    for cid in missing_map:
        errors.append(f"[오류] POSITIONS_MAP 에 없는 contentId: {cid}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print("\n검증 실패 — 파일을 수정하지 않고 중단합니다.", file=sys.stderr)
        return 1

    # 반영
    assigned = 0   # positions 를 1개 이상 부여한 카드
    skipped = 0    # positions 가 빈 카드
    usage = Counter()

    for cid, positions in POSITIONS_MAP.items():
        path, data = files_by_id[cid]

        if positions:
            assigned += 1
            usage.update(positions)
        else:
            skipped += 1

        modified = False
        if data.get("positions") != positions:
            data["positions"] = list(positions)
            modified = True

        todo = data.get("_todo")
        if isinstance(todo, list) and "positions" in todo:
            data["_todo"] = [t for t in todo if t != "positions"]
            modified = True

        if modified:
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"대상 카드: {len(POSITIONS_MAP)}장")
    print(f"부여: {assigned}장 · 생략: {skipped}장")
    print("직무별 사용 빈도:")
    for pos, cnt in sorted(usage.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {pos}: {cnt}")

    # _todo 에 "positions" 남은 카드 수 (POSITIONS_MAP 대상 범위)
    remaining = 0
    for cid in POSITIONS_MAP:
        _, data = files_by_id[cid]
        todo = data.get("_todo")
        if isinstance(todo, list) and "positions" in todo:
            remaining += 1
    print(f"_todo 에 positions 남은 카드: {remaining}장")

    # 미사용 직무 검사
    unused = sorted(VALID_POSITIONS - set(usage))
    print(f"사용 직무: {len(usage)}종 / 미사용: {len(unused)}종")
    if unused:
        print(f"  미사용 목록: {unused}")

    # content/news/ 전체: _todo 가 빈 배열이 아닌 카드
    nonempty_todo = []
    for path in sorted(NEWS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        todo = data.get("_todo")
        if todo:  # 빈 배열([]) / None 이 아니면
            nonempty_todo.append((data.get("contentId", path.stem), todo))

    print(f"_todo 가 비어있지 않은 카드: {len(nonempty_todo)}장")
    for cid, todo in nonempty_todo:
        print(f"  {cid}: {todo}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
