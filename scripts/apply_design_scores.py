#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content/news/ 의 Design 섹션 카드에 재채점 impactScore 를 반영한다.

동작:
1. DESIGN_SCORES 딕셔너리의 contentId 에 해당하는 카드의 impactScore 를 교체한다.
2. _todo 에서 "impactScore.rubric" 을 제거한다.
3. DESIGN_SCORES 에 있는데 파일이 없거나, Design 섹션 파일인데 DESIGN_SCORES 에 없으면
   오류로 출력하고 종료코드 1 로 종료한다(파일 수정 없이 중단).
4. 실행 후 before/after 점수 분포와 변경 건수를 출력한다.
5. 마지막에 content/news/ 전체를 훑어 _todo 에 "impactScore.rubric" 이 남아 있는
   카드 개수를 출력한다(0 이어야 정상).
"""

import json
import sys
from collections import Counter
from pathlib import Path

DESIGN_SCORES = {
    "20260701-design-001": 2, "20260701-design-002": 3, "20260701-design-003": 2, "20260701-design-004": 2,
    "20260701-design-005": 2, "20260701-design-006": 5, "20260701-design-007": 2,
    "20260702-design-001": 4, "20260702-design-002": 2, "20260702-design-003": 2, "20260702-design-004": 2,
    "20260702-design-005": 3, "20260702-design-006": 2,
    "20260703-design-001": 3, "20260703-design-002": 2, "20260703-design-003": 2, "20260703-design-004": 3,
    "20260704-design-001": 2, "20260704-design-002": 4,
    "20260705-design-001": 2, "20260705-design-002": 4, "20260705-design-003": 3,
    "20260706-design-001": 5, "20260706-design-002": 2, "20260706-design-003": 4,
    "20260707-design-001": 2, "20260707-design-002": 2, "20260707-design-003": 2, "20260707-design-004": 2,
    "20260708-design-001": 3, "20260708-design-002": 2, "20260708-design-003": 3, "20260708-design-004": 2,
    "20260709-design-001": 3, "20260709-design-002": 2, "20260709-design-003": 2, "20260709-design-004": 2,
    "20260710-design-001": 2, "20260710-design-002": 2, "20260710-design-003": 2, "20260710-design-004": 3,
    "20260711-design-001": 3, "20260711-design-002": 3, "20260711-design-003": 2, "20260711-design-004": 2,
    "20260712-design-001": 2, "20260712-design-002": 3, "20260712-design-003": 2, "20260712-design-004": 2,
    "20260713-design-001": 2, "20260713-design-002": 2, "20260713-design-003": 4, "20260713-design-004": 4,
    "20260714-design-001": 4, "20260714-design-002": 3, "20260714-design-003": 3, "20260714-design-004": 2,
    "20260715-design-001": 3, "20260715-design-002": 2, "20260715-design-003": 2, "20260715-design-004": 3,
    "20260716-design-001": 2, "20260716-design-002": 3, "20260716-design-003": 3, "20260716-design-004": 2,
    "20260717-design-001": 2, "20260717-design-002": 2, "20260717-design-003": 5, "20260717-design-004": 2,
    "20260718-design-001": 2, "20260718-design-002": 2, "20260718-design-003": 5, "20260718-design-004": 2,
    "20260719-design-001": 4, "20260719-design-002": 3, "20260719-design-003": 2, "20260719-design-004": 3,
    "20260720-design-001": 3, "20260720-design-002": 4, "20260720-design-003": 4, "20260720-design-004": 3,
    "20260721-design-001": 2, "20260721-design-002": 2, "20260721-design-003": 4, "20260721-design-004": 5,
    "20260722-design-001": 2, "20260722-design-002": 5, "20260722-design-003": 2, "20260722-design-004": 4,
    "20260723-design-001": 3, "20260723-design-002": 5, "20260723-design-003": 2, "20260723-design-004": 2,
    "20260724-design-001": 3, "20260724-design-002": 2, "20260724-design-003": 4, "20260724-design-004": 4,
}

NEWS_DIR = Path(__file__).resolve().parent.parent / "content" / "news"


def fmt_dist(counter):
    return " · ".join(f"★{s} {counter.get(s, 0)}" for s in range(1, 6))


def main():
    if not NEWS_DIR.is_dir():
        print(f"[오류] 디렉터리가 없습니다: {NEWS_DIR}", file=sys.stderr)
        return 1

    # Design 섹션 카드 수집
    files_by_id = {}
    for path in sorted(NEWS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if data.get("section") == "design":
            files_by_id[data["contentId"]] = (path, data)

    file_ids = set(files_by_id)
    score_ids = set(DESIGN_SCORES)

    missing_files = sorted(score_ids - file_ids)   # 점수는 있는데 파일 없음
    missing_scores = sorted(file_ids - score_ids)  # Design 파일인데 점수 없음

    if missing_files or missing_scores:
        if missing_files:
            print("[오류] DESIGN_SCORES 에 있으나 파일이 없는 contentId:", file=sys.stderr)
            for cid in missing_files:
                print(f"  - {cid}", file=sys.stderr)
        if missing_scores:
            print("[오류] Design 섹션 파일이나 DESIGN_SCORES 에 없는 contentId:", file=sys.stderr)
            for cid in missing_scores:
                print(f"  - {cid}", file=sys.stderr)
        return 1

    before = Counter()
    after = Counter()
    changed = 0

    for cid, new_score in DESIGN_SCORES.items():
        path, data = files_by_id[cid]
        old_score = data.get("impactScore")
        before[old_score] += 1
        after[new_score] += 1

        modified = False
        if old_score != new_score:
            data["impactScore"] = new_score
            changed += 1
            modified = True

        todo = data.get("_todo")
        if isinstance(todo, list) and "impactScore.rubric" in todo:
            data["_todo"] = [t for t in todo if t != "impactScore.rubric"]
            modified = True

        if modified:
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    total = len(DESIGN_SCORES)
    print(f"대상 카드: {total}장")
    print(f"변경 건수(impactScore): {changed}장")
    print(f"BEFORE {fmt_dist(before)}")
    print(f"AFTER  {fmt_dist(after)}")

    # content/news/ 전체 rubric 잔여 검사
    remaining = 0
    for path in sorted(NEWS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        todo = data.get("_todo")
        if isinstance(todo, list) and "impactScore.rubric" in todo:
            remaining += 1
    print(f"impactScore.rubric 잔여: {remaining}장")

    return 0


if __name__ == "__main__":
    sys.exit(main())
