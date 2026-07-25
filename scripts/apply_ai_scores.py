#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content/news/ 의 AI 섹션 카드에 재채점 impactScore 를 반영한다.

동작:
1. AI_SCORES 딕셔너리의 contentId 에 해당하는 카드의 impactScore 를 교체한다.
2. _todo 에서 "impactScore.rubric" 을 제거한다.
3. AI_SCORES 에 있는데 파일이 없거나, AI 섹션 파일인데 AI_SCORES 에 없으면
   오류로 출력하고 종료코드 1 로 종료한다.
4. 실행 후 before/after 점수 분포와 변경 건수를 출력한다.
"""

import json
import sys
from collections import Counter
from pathlib import Path

AI_SCORES = {
    "20260701-ai-001": 1, "20260701-ai-002": 1, "20260701-ai-003": 1, "20260701-ai-004": 3,
    "20260701-ai-005": 1, "20260701-ai-006": 4, "20260701-ai-007": 1,
    "20260702-ai-001": 1, "20260702-ai-002": 1, "20260702-ai-003": 1, "20260702-ai-004": 3,
    "20260702-ai-005": 2, "20260702-ai-006": 2, "20260702-ai-007": 1,
    "20260703-ai-001": 3, "20260703-ai-002": 1, "20260703-ai-003": 1, "20260703-ai-004": 1,
    "20260703-ai-005": 1, "20260703-ai-006": 1, "20260703-ai-007": 1,
    "20260704-ai-001": 3, "20260704-ai-002": 2, "20260704-ai-003": 4, "20260704-ai-004": 1,
    "20260705-ai-001": 1, "20260705-ai-002": 2,
    "20260706-ai-001": 4, "20260706-ai-002": 2, "20260706-ai-003": 2, "20260706-ai-004": 3, "20260706-ai-005": 5,
    "20260707-ai-001": 1, "20260707-ai-002": 1, "20260707-ai-003": 1, "20260707-ai-004": 3,
    "20260708-ai-001": 2, "20260708-ai-002": 2, "20260708-ai-003": 1, "20260708-ai-004": 3,
    "20260709-ai-001": 3, "20260709-ai-002": 2, "20260709-ai-003": 1, "20260709-ai-004": 1,
    "20260710-ai-001": 3, "20260710-ai-002": 3, "20260710-ai-003": 3, "20260710-ai-004": 1,
    "20260711-ai-001": 4, "20260711-ai-002": 1, "20260711-ai-003": 1, "20260711-ai-004": 3,
    "20260712-ai-001": 3, "20260712-ai-002": 3, "20260712-ai-003": 1, "20260712-ai-004": 1,
    "20260713-ai-001": 1, "20260713-ai-002": 1, "20260713-ai-003": 3, "20260713-ai-004": 1,
    "20260714-ai-001": 1, "20260714-ai-002": 2, "20260714-ai-003": 2, "20260714-ai-004": 1,
    "20260715-ai-001": 3, "20260715-ai-002": 1, "20260715-ai-003": 2, "20260715-ai-004": 1,
    "20260716-ai-001": 1, "20260716-ai-002": 2, "20260716-ai-003": 2, "20260716-ai-004": 1,
    "20260717-ai-001": 1, "20260717-ai-002": 1, "20260717-ai-003": 3, "20260717-ai-004": 1,
    "20260718-ai-001": 3, "20260718-ai-002": 3, "20260718-ai-003": 1, "20260718-ai-004": 1,
    "20260719-ai-001": 2, "20260719-ai-002": 1, "20260719-ai-003": 4, "20260719-ai-004": 1,
    "20260720-ai-001": 2, "20260720-ai-002": 5, "20260720-ai-003": 5, "20260720-ai-004": 1,
    "20260721-ai-001": 3, "20260721-ai-002": 3, "20260721-ai-003": 1, "20260721-ai-004": 2,
    "20260722-ai-001": 1, "20260722-ai-002": 2, "20260722-ai-003": 1, "20260722-ai-004": 2,
    "20260723-ai-001": 1, "20260723-ai-002": 3, "20260723-ai-003": 2, "20260723-ai-004": 1,
    "20260724-ai-001": 1, "20260724-ai-002": 2, "20260724-ai-003": 2, "20260724-ai-004": 5,
}

NEWS_DIR = Path(__file__).resolve().parent.parent / "content" / "news"


def fmt_dist(counter):
    return " · ".join(f"★{s} {counter.get(s, 0)}" for s in range(1, 6))


def main():
    if not NEWS_DIR.is_dir():
        print(f"[오류] 디렉터리가 없습니다: {NEWS_DIR}", file=sys.stderr)
        return 1

    # 파일에서 실제 AI 섹션 카드 수집
    files_by_id = {}
    for path in sorted(NEWS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if data.get("section") == "ai":
            files_by_id[data["contentId"]] = (path, data)

    file_ids = set(files_by_id)
    score_ids = set(AI_SCORES)

    missing_files = sorted(score_ids - file_ids)   # 점수는 있는데 파일 없음
    missing_scores = sorted(file_ids - score_ids)  # AI 파일인데 점수 없음

    if missing_files or missing_scores:
        if missing_files:
            print("[오류] AI_SCORES 에 있으나 파일이 없는 contentId:", file=sys.stderr)
            for cid in missing_files:
                print(f"  - {cid}", file=sys.stderr)
        if missing_scores:
            print("[오류] AI 섹션 파일이나 AI_SCORES 에 없는 contentId:", file=sys.stderr)
            for cid in missing_scores:
                print(f"  - {cid}", file=sys.stderr)
        return 1

    before = Counter()
    after = Counter()
    changed = 0

    for cid, new_score in AI_SCORES.items():
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

    total = len(AI_SCORES)
    print(f"대상 카드: {total}장")
    print(f"변경 건수(impactScore): {changed}장")
    print(f"BEFORE {fmt_dist(before)}")
    print(f"AFTER  {fmt_dist(after)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
