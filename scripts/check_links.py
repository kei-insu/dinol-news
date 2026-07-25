#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 실행 전: pip install -r requirements.txt
"""
dist/ 산출물의 내부 링크 무결성 검사.

대상 HTML:
    dist/index.html, dist/archive.html, dist/privacy.html
    dist/fortune.html          (존재할 때만)
    dist/news/2026/07/*.html   (25개)

추출: 모든 요소의 href / src 속성.
외부·특수 스킴은 제외하고, 내부 경로만 실제 파일 존재로 판정한다.
모든 내부 링크의 최종 해석 경로는 반드시 dist/ 아래여야 한다(이탈 방지).
"""

import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
DIST_ROOT = DIST.resolve()

# 파일 존재 검사에서 제외할 스킴
SKIP_SCHEMES = ("http:", "https:", "//", "mailto:", "tel:", "javascript:", "data:", "blob:")


def target_html_files():
    files = []
    for name in ("index.html", "archive.html", "privacy.html", "fortune.html"):
        p = DIST / name
        if p.is_file():
            files.append(p)
    news_dir = DIST / "news" / "2026" / "07"
    if news_dir.is_dir():
        files.extend(sorted(news_dir.glob("*.html")))
    return files


def extract_links(soup):
    """(속성종류, 원본링크문자열) 리스트"""
    out = []
    for el in soup.find_all(True):
        for attr in ("href", "src"):
            if el.has_attr(attr):
                out.append((attr, el.get(attr)))
    return out


def is_skipped_scheme(link):
    low = link.strip().lower()
    for s in SKIP_SCHEMES:
        if low.startswith(s):
            return s
    if low.startswith("#"):
        return "#(fragment)"
    return None


def resolve_candidate(html_file, path):
    """경로 해석 규칙 a/b/c. (candidate_Path, rule) 반환."""
    if path.startswith("/dinol-news/") or path == "/dinol-news":
        # b) /dinol-news 를 떼고 dist/ 기준
        rest = path[len("/dinol-news"):].lstrip("/")
        return (DIST / rest), "b(/dinol-news)"
    if path.startswith("/"):
        # c) 사이트 루트 = dist/
        rest = path.lstrip("/")
        return (DIST / rest), "c(site-root)"
    # a) 상대경로 → HTML 파일 부모 기준
    return (html_file.parent / path), "a(relative)"


def exists_target(candidate):
    """디렉터리 링크(/로 끝남)는 내부 index.html 로 판정."""
    if candidate.is_dir():
        return (candidate / "index.html").is_file()
    return candidate.is_file()


def main():
    files = target_html_files()
    total_links = 0
    checked = 0
    skip_counts = {}
    broken = []   # (html, raw, resolved, reason)

    for html_file in files:
        raw = html_file.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        soup = BeautifulSoup(raw, "html.parser")
        for attr, link in extract_links(soup):
            total_links += 1
            if link is None:
                continue
            # 스킴 제외
            sk = is_skipped_scheme(link)
            if sk:
                skip_counts[sk] = skip_counts.get(sk, 0) + 1
                continue
            # URL 분해 → path 만
            parsed = urlsplit(link)
            path = unquote(parsed.path)
            if path == "":
                # "#top", "?v=2" 등 → 경로 없음, 제외
                skip_counts["빈 path(#/?만)"] = skip_counts.get("빈 path(#/?만)", 0) + 1
                continue

            checked += 1
            candidate, rule = resolve_candidate(html_file, path)

            # dist 이탈 방지 (필수)
            resolved = candidate.resolve()
            try:
                resolved.relative_to(DIST_ROOT)
            except ValueError:
                broken.append((html_file, link, str(resolved), "dist 이탈"))
                continue

            if not exists_target(candidate):
                broken.append((html_file, link, str(resolved), "파일 없음"))

    # ── 출력 ──
    print("=" * 60)
    print("링크 무결성 검사 (dist/)")
    print("=" * 60)
    print(f"\n검사한 HTML 파일 수 : {len(files)}")
    for f in files:
        print(f"    - {f.relative_to(DIST)}")
    print(f"\n추출 링크 총 개수    : {total_links}")
    print(f"검사 대상 링크 수    : {checked}")

    print(f"\n스킴별 제외 건수:")
    if skip_counts:
        for k in sorted(skip_counts):
            print(f"    {k:20s}: {skip_counts[k]}")
    else:
        print("    (없음)")
    print(f"    제외 합계          : {sum(skip_counts.values())}")

    print(f"\n깨진 링크: {len(broken)}건")
    if broken:
        print(f"\n  {'HTML':32s} {'사유':10s} 원본링크 → 해석경로")
        for html_file, raw, resolved, reason in broken:
            rel_html = html_file.relative_to(DIST)
            try:
                rel_res = Path(resolved).relative_to(DIST_ROOT)
                rel_res = f"dist/{rel_res}"
            except ValueError:
                rel_res = resolved
            print(f"  · [{rel_html}] ({reason})")
            print(f"      링크={raw!r}")
            print(f"      해석={rel_res}")
    else:
        print("  → 깨진 링크 없음 (정상)")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
