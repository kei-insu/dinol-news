#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디자인 놀이터 — 브리핑 빌드 스크립트 (결정론적 조립)
사용법:
    python scripts/build_briefing.py scripts/cards.json
동작:
    1) cards.json(큐레이션 완료된 8장) + template.html 을 읽어
    2) news/YYYY/MM/Dinol_news_YYYYMMDD.html 생성 (현재 카드 규칙 그대로)
    3) index.json 맨 앞에 날짜 추가
    4) 구조 자가검증(카드 수·필드·라벨 한글·em대시 등) 후 통과/실패 출력
※ git push 는 하지 않는다. (검수 후 사람이 배포)

카드 규칙(2026-07 기준):
    - 라벨·카드 제목은 한글. 영문 카드는 영어 원제목을 data-title-en 에 보존(팝업 토글).
    - 영문 카드만 *_en/*_kr 이중언어 + thumb-en 배지 + data-title-en.
    - data-impact-score 는 정수 1~5. 큐레이션 노트 = data-comment(+ -kr).
    - 본문(요약/포인트/디자이너/추천/코멘트)에 em대시(—) 금지.
"""
import sys, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FOOTER = ('<div class="card-footer"><div class="card-actions">'
          '<span class="act act-like" role="button" aria-label="좋아요"><svg viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg><span class="act-count"></span></span>'
          '<span class="act act-share" role="button" aria-label="공유"><svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></span>'
          '</div></div>')

REQUIRED_KR = ["url", "source", "date", "label", "category", "grad", "title_kr",
               "impact", "summary_kr", "points_kr", "designer_kr", "recommend_kr", "comment_kr"]
REQUIRED_EN = REQUIRED_KR + ["title_en", "summary_en", "points_en", "designer_en", "recommend_en", "comment_en"]


def attr(s):
    """data-* 속성값용: 큰따옴표만 이스케이프(속성 구분자 보호)."""
    return str(s).replace('"', "&quot;")


def kr_card(c):
    cls = "card featured" if c.get("featured") else "card"
    return f'''    <a class="{cls}" href="{c['url']}" target="_blank"
       data-category="{attr(c['category'])}"
       data-summary="{attr(c['summary_kr'])}"
       data-points="{attr(c['points_kr'])}"
       data-designer="{attr(c['designer_kr'])}"
       data-impact-score="{int(c['impact'])}"
       data-recommend="{attr(c['recommend_kr'])}"
       data-comment="{attr(c['comment_kr'])}">
      <div class="thumb {c['grad']}">
        <div class="noise"></div>
        <span class="thumb-label">{c['label']}</span>
      </div>
      <div class="card-body">
        <div class="card-source">{c['source']} · {c['date']}</div>
        <div class="card-title">{c['title_kr']}</div>
      </div>
      {FOOTER}
    </a>'''


def en_card(c):
    cls = "card featured" if c.get("featured") else "card"
    return f'''    <a class="{cls}" href="{c['url']}" target="_blank"
       data-category="{attr(c['category'])}"
       data-summary="{attr(c['summary_en'])}" data-summary-kr="{attr(c['summary_kr'])}"
       data-points="{attr(c['points_en'])}" data-points-kr="{attr(c['points_kr'])}"
       data-designer="{attr(c['designer_en'])}" data-designer-kr="{attr(c['designer_kr'])}"
       data-impact-score="{int(c['impact'])}"
       data-recommend="{attr(c['recommend_en'])}" data-recommend-kr="{attr(c['recommend_kr'])}"
       data-comment="{attr(c['comment_en'])}" data-comment-kr="{attr(c['comment_kr'])}"
       data-title-en="{attr(c['title_en'])}">
      <div class="thumb {c['grad']}">
        <div class="noise"></div>
        <span class="thumb-label">{c['label']}</span>
        <span class="thumb-en">EN</span>
      </div>
      <div class="card-body">
        <div class="card-source">{c['source']} · {c['date']}</div>
        <div class="card-title">{c['title_kr']}</div>
      </div>
      {FOOTER}
    </a>'''


def build_card(c):
    lang = c.get("lang", "kr")
    need = REQUIRED_EN if lang == "en" else REQUIRED_KR
    missing = [k for k in need if k not in c or c[k] in (None, "")]
    if missing:
        raise SystemExit(f"[에러] 카드 필드 누락({c.get('label','?')} / {lang}): {missing}")
    return en_card(c) if lang == "en" else kr_card(c)


def section(name, heading, cards_html):
    return (f'<!-- ══════════════════════ {name} ══════════════════════ -->\n'
            f'<div class="section">\n'
            f'  <div class="section-header">\n'
            f'    <h2>{heading}</h2>\n'
            f'    <div class="line"></div>\n'
            f'    <span class="section-chevron">▼</span>\n'
            f'  </div>\n'
            f'  <div class="grid">\n\n{cards_html}\n\n  </div>\n'
            f'</div>\n\n\n')


def main():
    if len(sys.argv) < 2:
        raise SystemExit("사용법: python scripts/build_briefing.py <cards.json>")
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    date = str(data["date"])                       # 예: "20260709"
    y, m = date[:4], date[4:6]
    tdate = data.get("title_date", f"{y}. {m}. {date[6:8]}")
    sdate = data.get("site_date", tdate)

    tmpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()

    ai_html = "\n\n".join(build_card(c) for c in data["cards"]["ai"])
    dz_html = "\n\n".join(build_card(c) for c in data["cards"]["design"])

    html = re.sub(r'<!-- ═+ AI ═+ -->.*?(?=<!-- ═+ DESIGN ═+ -->)',
                  section("AI", "AI", ai_html), tmpl, count=1, flags=re.S)
    html = re.sub(r'<!-- ═+ DESIGN ═+ -->.*?(?=<!-- ── 아카이브)',
                  section("DESIGN", "Design", dz_html), html, count=1, flags=re.S)
    html = re.sub(r'<title>디자인 놀이터[^<]*</title>', f'<title>디자인 놀이터 — {tdate}</title>', html)
    html = re.sub(r'<div class="site-date">[^<]*</div>', f'<div class="site-date">{sdate}</div>', html)

    outdir = os.path.join(ROOT, "news", y, m)
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f"Dinol_news_{date}.html")
    open(outpath, "w", encoding="utf-8").write(html)

    # index.json 갱신 (맨 앞에 추가, 중복 방지)
    idxpath = os.path.join(ROOT, "index.json")
    idx = json.load(open(idxpath, encoding="utf-8"))
    if date not in idx:
        idx.insert(0, date)
        json.dump(idx, open(idxpath, "w", encoding="utf-8"), ensure_ascii=False)

    # ── 자가검증 ──
    errs = []
    ncards = len(re.findall(r'class="card( featured)?"', html))
    if ncards != 8:
        errs.append(f"카드 수 {ncards} (8이어야 함)")
    n_ai, n_dz = len(data["cards"]["ai"]), len(data["cards"]["design"])
    if n_ai != 4 or n_dz != 4:
        errs.append(f"섹션 구성 AI {n_ai}/Design {n_dz} (권장 4/4)")
    # 라벨 순수 영문 금지(AI 같은 관용 약어는 허용)
    for lab in re.findall(r'<span class="thumb-label">([^<]*)</span>', html):
        if not any('\uac00' <= ch <= '\ud7a3' for ch in lab):
            errs.append(f"영문 라벨: '{lab}' (한글 라벨이어야 함)")
    # 콘텐츠 em대시 금지 (title 태그·주석 제외)
    body = re.sub(r'<title>[^<]*</title>', '', html)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    if '—' in body:
        errs.append("본문에 em대시(—) 있음")
    # impact-score 정수 검증
    for sc in re.findall(r'data-impact-score="([^"]*)"', html):
        if not re.fullmatch(r'[1-5]', sc):
            errs.append(f"impact-score 비정상: '{sc}'")

    print(f"✅ 생성: news/{y}/{m}/Dinol_news_{date}.html  (AI {n_ai} + Design {n_dz})")
    print(f"   index.json 선두: {idx[:3]}")
    if errs:
        print("⚠️  검증 경고:")
        for e in errs:
            print("   -", e)
        sys.exit(1)
    print("✅ 자가검증 통과 (카드 8 · 라벨 한글 · em대시 없음 · impact 정수)")
    print("👉 다음: 브라우저로 파일 열어 검수 후 직접 git push (자동 배포 아님)")


if __name__ == "__main__":
    main()
