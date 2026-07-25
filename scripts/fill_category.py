#!/usr/bin/env python3
"""
fill_category.py — EN 카드의 category.kr / category.en 채우기

사용법:
    python scripts/fill_category.py                 # content/news 전체
    python scripts/fill_category.py --dry           # 파일 안 쓰고 미리보기

원칙:
  - 카테고리는 토큰(· 구분) 단위로 번역한다. 문자열 통째 번역 금지.
  - 사전에 없는 토큰이 나오면 오류로 보고하고 그 카드는 건너뛴다.
  - 기존 KR 카드에서 쓰던 어휘를 그대로 따른다(표기 흔들림 방지).
"""

import os
import re
import sys
import json
import glob

CONTENT_DIR = "content/news"
HANGUL = re.compile(r"[가-힣]")

# 영문 토큰 → 한국어 토큰
EN2KR = {
    # 최상위
    "AI": "AI",
    "Design": "디자인",
    # 정책·산업
    "Policy": "정책",
    "Governance": "거버넌스",
    "Global Governance": "글로벌 거버넌스",
    "Geopolitics": "지정학",
    "Legal": "법률",
    "Economy": "경제",
    "Investment": "투자",
    "Business": "비즈니스",
    "Industry": "산업",
    "Strategy": "전략",
    "Startup": "스타트업",
    "Startups": "스타트업",
    "Big Tech": "빅테크",
    "Infrastructure": "인프라",
    "Semiconductor": "반도체",
    "Europe": "유럽",
    "India": "인도",
    "Access": "접근성",
    "Space": "우주",
    "Security": "보안",
    "Identity": "신원",
    # 모델·도구
    "Model": "모델",
    "Models": "모델",
    "Open Model": "오픈모델",
    "Agent": "에이전트",
    "Tool": "도구",
    "Tools": "도구",
    "AI Tool": "AI 도구",
    "Design Tool": "디자인 툴",
    "Productivity": "생산성",
    "Research": "연구",
    "Science": "과학",
    "Pharma": "제약",
    "Healthcare": "의료",
    "Hardware": "하드웨어",
    "Technology": "기술",
    "Tech": "테크",
    "Robotics": "로보틱스",
    "Home": "홈",
    "Web": "웹",
    "Content": "콘텐츠",
    "Image": "이미지",
    "News": "뉴스",
    "Roundup": "라운드업",
    "Reference": "레퍼런스",
    "Digest": "다이제스트",
    "Opinion": "오피니언",
    "Interview": "인터뷰",
    "Leadership": "리더십",
    "Education": "교육",
    "Community": "커뮤니티",
    # 디자인 분야
    "Architecture": "건축",
    "Residential": "주거",
    "Interior": "인테리어",
    "Hospitality": "숙박",
    "Museum": "미술관",
    "Retail": "리테일",
    "Competition": "공모",
    "Preservation": "보존",
    "Renovation": "리노베이션",
    "Heritage": "헤리티지",
    "History": "역사",
    "Product": "제품",
    "Industrial Design": "산업디자인",
    "Furniture": "가구",
    "Automotive": "자동차",
    "Mobility": "모빌리티",
    "Eyewear": "아이웨어",
    "EDC": "EDC",
    "Gaming": "게임",
    "Branding": "브랜딩",
    "Brand": "브랜드",
    "Packaging": "패키지",
    "Graphic": "그래픽",
    "Editorial": "편집",
    "Typography": "타이포그래피",
    "Illustration": "일러스트",
    "Photography": "사진",
    "Visual": "비주얼",
    "Art": "미술",
    "Exhibition": "전시",
    "Installation": "설치",
    "Events": "이벤트",
    "Culture": "문화",
    "Awards": "수상",
    "Craft": "공예",
    "Material": "소재",
    "Making": "제작",
    "Fabrication": "가공",
    "Fashion": "패션",
    "Couture": "쿠튀르",
    "Ecology": "생태",
    "Sustainability": "지속가능성",
    "Social Impact": "소셜임팩트",
    "UX": "UX",
}

# 한국어만 적힌 카드의 역방향 보정 (KR2EN 에 없으면 en 은 비워둔다)
KR2EN_EXTRA = {
    "모델 출시": "Model Launch",
    "인프라": "Infrastructure",
    "투자": "Investment",
    "창작": "Creative",
    "저작권": "Copyright",
    "이미지 생성": "Image Generation",
    "로보틱스": "Robotics",
    "제품": "Product",
    "정책": "Policy",
    "모빌리티": "Mobility",
    "산업": "Industry",
    "오픈소스": "Open Source",
    "비즈니스": "Business",
    "엔터프라이즈": "Enterprise",
    "표준": "Standards",
    "스타트업": "Startup",
    "UX": "UX",
    "국제": "Global",
    "생성형": "Generative",
    "영상": "Video",
    "미디어": "Media",
    "반도체": "Semiconductor",
    "보안": "Security",
    "인테리어": "Interior",
    "트렌드": "Trends",
    "디자인": "Design",
    "AI": "AI",
}

KR2EN = {v: k for k, v in EN2KR.items() if not HANGUL.search(k)}
KR2EN.update(KR2EN_EXTRA)


def is_korean(tok):
    return bool(HANGUL.search(tok))


def convert(raw):
    """카테고리 문자열 → (kr, en, 미매핑 토큰 목록)"""
    toks = [t.strip() for t in raw.split("·") if t.strip()]
    kr, en, unknown = [], [], []
    for t in toks:
        if is_korean(t):
            kr.append(t)
            en.append(KR2EN.get(t))
            if t not in KR2EN:
                unknown.append(t)
        else:
            kr.append(EN2KR.get(t))
            en.append(t)
            if t not in EN2KR:
                unknown.append(t)
    if any(x is None for x in kr):
        return None, None, unknown
    en_str = " · ".join(en) if all(x for x in en) else None
    return " · ".join(kr), en_str, unknown


def main():
    dry = "--dry" in sys.argv
    files = sorted(glob.glob(os.path.join(CONTENT_DIR, "*.json")))
    if not files:
        print(f"{CONTENT_DIR}/ 에 JSON이 없습니다.")
        return 1

    done = skipped = no_en = 0
    unknown_all = {}
    samples = []

    for path in files:
        with open(path, encoding="utf-8") as f:
            card = json.load(f)

        if "category.kr" not in card.get("_todo", []):
            continue

        raw = card["category"]["en"]
        kr, en, unknown = convert(raw)

        if unknown:
            for u in unknown:
                unknown_all.setdefault(u, []).append(card["contentId"])
        if kr is None:
            skipped += 1
            continue

        card["category"]["kr"] = kr
        card["category"]["en"] = en
        if en is None:
            no_en += 1
        card["_todo"] = [t for t in card["_todo"] if t != "category.kr"]
        done += 1

        if len(samples) < 12 and raw != kr:
            samples.append((card["contentId"], raw, kr))

        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(card, f, ensure_ascii=False, indent=2)

    print(f"처리 {done}장 · 건너뜀 {skipped}장" + (" (--dry: 파일 미저장)" if dry else ""))
    if no_en:
        print(f"  category.en 미생성 {no_en}장 (원본이 한국어라 영문 역매핑 불가)")
    print()
    print("변환 예시")
    for cid, a, b in samples:
        print(f"  {cid}")
        print(f"    {a}")
        print(f"    → {b}")
    if unknown_all:
        print()
        print(f"사전에 없는 토큰 {len(unknown_all)}종:")
        for t, ids in unknown_all.items():
            print(f"  {t}  ({len(ids)}장, 예: {ids[0]})")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
