#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daily_import.py — 매일 카드 추출·검증을 한 줄로.

    python scripts/daily_import.py 20260728

[0]~[10] 단계를 순서대로 수행하고, 어느 단계든 실패하면 즉시 중단한다.
매체 목록은 ★scripts/source_rules.json 이 단일 기준★ — 이 파일에 하드코딩하지 않는다.
"""
import os
import re
import sys
import json
import glob
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# 같은 폴더의 공용 모듈 재사용 (중복 구현 금지)
from extract_cards import parse_cards, inner, parse_source
from validation_common import VALID_POSITIONS

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "content" / "news"
SOURCE_RULES = ROOT / "scripts" / "source_rules.json"
DAILY_DIR = ROOT / "scripts" / "daily"
LEDGER = ROOT / "published_urls.json"


class DailyImportError(Exception):
    """포착 가능한 전용 실패 예외. 내부 _readerthread 인코딩 오류와 달리 잡을 수 있다."""


def fail(stage, reason, detail=""):
    raise DailyImportError(f"{stage} {reason}\n{detail}".rstrip())


def die(msg, code=1):
    # 파이프라인 단계 실패 — 전용 예외로 던져 main()에서 traceback 없이 종료코드 1로 변환.
    raise DailyImportError(msg)


def parse_ymd(value):
    """8자리 실제 날짜만 통과 (strftime 왕복). 아니면 None."""
    try:
        d = datetime.strptime(value, "%Y%m%d")
    except (ValueError, TypeError):
        return None
    if d.strftime("%Y%m%d") != value:
        return None
    return d


def sha(b):
    return hashlib.sha256(b).hexdigest()


def snapshot():
    return {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p.read_bytes())
            for p in sorted(NEWS_DIR.glob("*.json"))}


# ────────────────────────────────────────────────────────────
# 서브프로세스 — ★text=False 로 바이트 수신, 메인 스레드에서 디코딩★
#   내부 _readerthread 에서 디코딩하면 try/except 로 못 잡는다.
# ────────────────────────────────────────────────────────────
def decode_python_output(data, stage, stream, command):
    """A. Python 자식은 UTF-8 강제했으므로 strict. cp949 fallback 없음(설정 안 먹은 것이므로 실패가 맞다)."""
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail(stage, "Python 자식 프로세스 UTF-8 디코딩 실패",
             f"command={command}, stream={stream}, "
             f"start={exc.start}, end={exc.end}, reason={exc.reason}")


def run_python(args, stage):
    """A. Python 자식 프로세스 — PYTHONIOENCODING=utf-8 강제 + strict."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    command = [sys.executable, *args]
    try:
        result = subprocess.run(command, cwd=str(ROOT), capture_output=True,
                                text=False, env=env)          # ★바이트 수신★
    except OSError as exc:                                     # ★실행 자체 실패★
        fail(stage, "서브프로세스 실행 실패",
             f"command={command}, type={type(exc).__name__}, reason={exc}")
    stdout = decode_python_output(result.stdout, stage, "stdout", command)
    stderr = decode_python_output(result.stderr, stage, "stderr", command)
    return result.returncode, stdout, stderr


def decode_console(data, stage, stream, command):
    """B. Git·npm 은 UTF-8 → CP949 fallback."""
    for encoding in ("utf-8", "cp949"):
        try:
            return data.decode(encoding, errors="strict")
        except UnicodeDecodeError:
            continue
    fail(stage, "콘솔 출력 디코딩 실패",
         f"command={command}, stream={stream}, encodings=utf-8,cp949")


def run_command(args, stage):
    """B. Git·npm 등 비파이썬 — 두 스트림 모두 디코딩해 반환(호출부가 누락 못 함)."""
    try:
        result = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=False)
    except OSError as exc:                                     # ★실행 자체 실패★
        fail(stage, "서브프로세스 실행 실패",
             f"command={args}, type={type(exc).__name__}, reason={exc}")
    stdout = decode_console(result.stdout, stage, "stdout", args)
    stderr = decode_console(result.stderr, stage, "stderr", args)
    return result.returncode, stdout, stderr


def git_show_bytes(ref, stage):
    """blob 바이트 원본 (CRLF/LF 비교용). OSError 전용 예외 변환."""
    try:
        result = subprocess.run(["git", "show", ref], cwd=str(ROOT),
                                capture_output=True, text=False)
    except OSError as exc:
        fail(stage, "서브프로세스 실행 실패",
             f"command=git show {ref}, type={type(exc).__name__}, reason={exc}")
    return result.returncode, result.stdout


# ────────────────────────────────────────────────────────────
# source_rules.json — 스키마만 검증 (매체 목록은 하드코딩하지 않는다)
# ────────────────────────────────────────────────────────────
def _no_dup_pairs(pairs):
    """모든 객체 계층에서 중복 키를 잡는다 (재귀 hook)."""
    keys = [k for k, _ in pairs]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    if dups:
        raise ValueError(f"중복 키: {dups}")
    return dict(pairs)


def load_source_rules(path=SOURCE_RULES):
    """(rules, errors) 반환. errors 가 비어 있어야 정상."""
    errors = []
    if not path.is_file():
        return None, [f"source_rules.json 없음: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_no_dup_pairs)
    except ValueError as e:
        return None, [f"source_rules.json 파싱/중복키: {e}"]
    if not isinstance(data, dict):
        return None, ["최상위가 객체가 아님"]
    if len(data) < 1:
        return None, ["매체가 1개 이상이어야 함"]
    for name, val in data.items():
        if not (isinstance(name, str) and name.strip()):
            errors.append(f"매체명이 비어있지 않은 문자열이 아님: {name!r}")
            continue
        if not isinstance(val, dict):
            errors.append(f"{name}: 값이 객체가 아님"); continue
        if set(val.keys()) != {"region", "group"}:
            errors.append(f"{name}: 키가 region·group 정확히 2개가 아님: {sorted(val.keys())}"); continue
        if val["region"] not in ("국내", "해외"):
            errors.append(f"{name}: region 은 국내|해외 만: {val['region']!r}")
        if not (isinstance(val["group"], str) and val["group"].strip()):
            errors.append(f"{name}: group 이 비어있지 않은 문자열이 아님: {val['group']!r}")
    return data, errors


# ────────────────────────────────────────────────────────────
# [1] HTML 사전 파싱 (추출 전, 읽기 전용) — 테스트에서도 호출
# ────────────────────────────────────────────────────────────
def precheck_html(html_text, ymd, rules):
    """
    반환: dict(ok, cards, ids_match, sources[(cid,name)], empty, dup_ids, unknown[], msg)
    카드 수·ID 집합·source 개수를 UNKNOWN 보다 먼저 확정한다.
    """
    blocks = parse_cards(html_text)   # [(section, block, order)]
    n_cards = len(blocks)
    ids = []
    sources = []
    empty = 0
    for section, block, order in blocks:
        cid = f"{ymd}-{section}-{order:03d}"
        ids.append(cid)
        raw = inner(block, "card-source")
        # 구분자(·)가 없으면 형식이 바뀐 신호 → 오류
        if not raw or "·" not in raw:
            sources.append((cid, None)); empty += 1; continue
        name, _ = parse_source(raw)
        if not (isinstance(name, str) and name.strip()):
            sources.append((cid, None)); empty += 1; continue
        sources.append((cid, name.strip()))

    expected_ids = ([f"{ymd}-ai-{i:03d}" for i in range(1, 5)]
                    + [f"{ymd}-design-{i:03d}" for i in range(1, 5)])
    ids_match = set(ids) == set(expected_ids)
    dup_ids = len(ids) - len(set(ids))
    unknown = sorted({name for _, name in sources if name is not None and name not in rules})
    return {
        "cards": n_cards, "ids": ids, "ids_match": ids_match,
        "sources": sources, "empty": empty, "dup_ids": dup_ids,
        "unknown": unknown, "expected_ids": expected_ids,
    }


def balance(sources_named, rules):
    """(rows, tally) — sources_named: [(cid, section, name)]"""
    rows = []
    for cid, section, name in sources_named:
        r = rules.get(name)
        rows.append((cid, section, name,
                     r["region"] if r else "UNKNOWN",
                     r["group"] if r else "UNKNOWN"))
    return rows


# ────────────────────────────────────────────────────────────
# [4] 판정값 원자적 적용
# ────────────────────────────────────────────────────────────
def _matches(card, v):
    return (isinstance(card.get("category"), dict)
            and card["category"].get("kr") == v["category_kr"]
            and card["category"].get("en") == v["category_en"]
            and card.get("impactScore") == v["impactScore"]
            and card.get("positions") == list(v["positions"])
            and card.get("_todo") == [])


def apply_atomic(data, targets):
    """targets: {cid: path}. data: 판정값. 반환 (status, msg). status: 'ok'|'error'|'fatal'"""
    paths = [targets[c] for c in data]
    temps = {p: p.parent / (p.name + ".fill-next") for p in paths}

    def cleanup():
        for tp in temps.values():
            try:
                tp.unlink(missing_ok=True)
            except OSError:
                pass

    # (a) 사전검증
    prepared = {}
    errs = []
    for cid, v in data.items():
        p = targets[cid]
        if not p.is_file():
            errs.append(f"{cid}: 파일 없음"); continue
        try:
            card = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            errs.append(f"{cid}: 파싱 실패 {e}"); continue
        if card.get("contentId") != cid:
            errs.append(f"{cid}: 내부 contentId 불일치"); continue
        if not isinstance(card.get("category"), dict):
            errs.append(f"{cid}: category dict 아님"); continue
        if not isinstance(v["impactScore"], int) or isinstance(v["impactScore"], bool):
            errs.append(f"{cid}: impactScore 타입"); continue
        if not (isinstance(v["positions"], list)
                and all(isinstance(x, str) and x in VALID_POSITIONS for x in v["positions"])):
            errs.append(f"{cid}: positions 가 VALID_POSITIONS 밖이거나 형식 오류: {v['positions']}"); continue
        card["category"]["kr"] = v["category_kr"]
        card["category"]["en"] = v["category_en"]
        card["impactScore"] = v["impactScore"]
        card["positions"] = list(v["positions"])
        card["_todo"] = []
        prepared[p] = json.dumps(card, ensure_ascii=False, indent=2)
    if errs:
        return "error", "사전검증 실패:\n  " + "\n  ".join(errs)

    # (b) 원본 보관
    original = {p: p.read_bytes() for p in paths}
    original_sha = {p: sha(original[p]) for p in paths}

    def restore():
        ok = True
        for p in paths:
            try:
                p.write_bytes(original[p])
                if sha(p.read_bytes()) != original_sha[p]:
                    ok = False
            except OSError:
                ok = False
        return ok

    try:
        # (c) 임시 기록
        for p in paths:
            temps[p].write_text(prepared[p], encoding="utf-8")
        # (d) 임시 재검증
        mism = [c for c, v in data.items()
                if not _matches(json.loads(temps[targets[c]].read_text(encoding="utf-8")), v)]
        if mism:
            return "error", f"임시 재검증 불일치: {mism} (실제 파일 무변경)"
        # (e) 교체
        try:
            for p in paths:
                temps[p].replace(p)
        except OSError as e:
            if restore():
                return "error", f"교체 실패 후 원본 복구 성공: {e}"
            return "fatal", f"교체 실패 + 원본 복구 실패: {e}"
        # (f) 최종 대조
        fm = [c for c, v in data.items()
              if not _matches(json.loads(targets[c].read_text(encoding="utf-8")), v)]
        if fm:
            if restore():
                return "error", f"교체 후 불일치 {fm}, 원본 복구 성공"
            return "fatal", f"교체 후 불일치 {fm} + 원본 복구 실패"
        return "ok", "8개 최종 상태 적용"
    finally:
        cleanup()


# ────────────────────────────────────────────────────────────
# git 상태
# ────────────────────────────────────────────────────────────
def git_branch():
    _, out, _ = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], "[0]")
    return out.strip()


def git_porcelain():
    _, out, _ = run_command(["git", "status", "--porcelain"], "[0]")
    return [ln for ln in out.split("\n") if ln.strip()]


def run_pipeline():
    t0 = time.monotonic()
    argv = sys.argv[1:]

    # ── 인자 검증 (맨 처음) ──
    if len(argv) != 1:
        die("[인자] 사용법: python scripts/daily_import.py YYYYMMDD")
    ymd = argv[0]
    if parse_ymd(ymd) is None:
        die(f"[인자] 유효하지 않은 날짜: {ymd!r} (YYYYMMDD 실제 날짜여야 함)")
    mm = ymd[4:6]

    # ── source_rules.json 스키마 검증 ──
    rules, rule_errs = load_source_rules()
    if rule_errs:
        die("[source_rules] 스키마 오류:\n  " + "\n  ".join(rule_errs))
    print(f"[source_rules] {len(rules)}종 로드 · 스키마 통과")

    html_path = ROOT / "news" / "2026" / mm / f"Dinol_news_{ymd}.html"
    daily_path = DAILY_DIR / f"{ymd}.json"

    # ── [0] 사전 확인 ──
    if git_branch() != "astro":
        die(f"[0] 브랜치가 astro 가 아님: {git_branch()}")
    allowed = {f"scripts/daily/{ymd}.json", "scripts/source_rules.json"}
    blockers = []
    for ln in git_porcelain():
        xy, path = ln[:2], ln[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if "U" in xy or xy in ("AA", "DD"):
            blockers.append(f"충돌 {xy} {path}"); continue
        if xy == "??":
            if path not in allowed:
                blockers.append(f"untracked {path}")
            continue
        if xy[0] != " ":                       # staged
            blockers.append(f"staged {xy} {path}"); continue
        if path not in allowed:
            blockers.append(f"tracked 변경 {xy} {path}")
    if blockers:
        die("[0] Git 상태 위반 (허용: scripts/daily/{ymd}.json · scripts/source_rules.json):\n  "
            + "\n  ".join(blockers))
    # source_rules 변경 시 추가만 허용
    changed_sr = any(ln[3:].strip().strip('"') == "scripts/source_rules.json" for ln in git_porcelain())
    if changed_sr:
        rc, head_txt, _ = run_command(["git", "show", "HEAD:scripts/source_rules.json"], "[0]")
        if rc == 0:
            try:
                head_rules = json.loads(head_txt)
                removed = sorted(set(head_rules) - set(rules))
                changed = sorted(k for k in (set(head_rules) & set(rules)) if head_rules[k] != rules[k])
                if removed or changed:
                    die(f"[0] source_rules.json 에 삭제·변경 감지 (추가만 허용):\n"
                        f"  삭제={removed}\n  변경={changed}\n  → 사용자 판단 필요")
                print(f"[0] source_rules.json 변경: 추가만 {sorted(set(rules)-set(head_rules))}")
            except ValueError:
                die("[0] HEAD source_rules.json 파싱 실패")
    if not html_path.is_file():
        die(f"[0] 브리핑 HTML 없음: {html_path}")
    # main blob 대조 (RAW 또는 LF 정규화 후 일치)
    rc, _, _ = run_command(["git", "cat-file", "-e", f"main:news/2026/{mm}/Dinol_news_{ymd}.html"], "[0]")
    if rc == 0:
        _, main_bytes = git_show_bytes(f"main:news/2026/{mm}/Dinol_news_{ymd}.html", "[0]")
        w = html_path.read_bytes()
        if not (w == main_bytes or w.replace(b"\r\n", b"\n") == main_bytes.replace(b"\r\n", b"\n")):
            die("[0] 워킹트리 HTML 이 main 배포본과 다름 (LF 정규화 후에도 불일치) → 중단")
        print("[0] main blob 대조 통과 (RAW 또는 LF 일치)")
    else:
        print("[0] main 에 해당 HTML 없음 — blob 대조 건너뜀")
    # 판정값 파일
    if not daily_path.is_file():
        die(f"[0] 판정값 없음: {daily_path}")
    try:
        judg = json.loads(daily_path.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        die(f"[0] 판정값 JSON 오류: {e}")
    exp_keys = set([f"{ymd}-ai-{i:03d}" for i in range(1, 5)]
                   + [f"{ymd}-design-{i:03d}" for i in range(1, 5)])
    if set(judg) != exp_keys:
        die(f"[0] 판정값 키가 8개 형식과 불일치: {sorted(set(judg) ^ exp_keys)}")
    for k, v in judg.items():
        if set(v.keys()) < {"category_kr", "category_en", "impactScore", "positions"}:
            die(f"[0] 판정값 {k} 필수 필드 누락")
    # 기존 카드 0개
    existing = sorted(NEWS_DIR.glob(f"{ymd}-*.json"))
    if existing:
        die(f"[0] 기존 {ymd} 카드 {len(existing)}개 존재 → 중단:\n  "
            + "\n  ".join(p.name for p in existing))
    # 대장 원본 보관
    ledger_original_bytes = LEDGER.read_bytes() if LEDGER.exists() else None
    ledger_original_data = json.loads(ledger_original_bytes.decode("utf-8-sig")) if ledger_original_bytes else {}
    ledger_before = len(ledger_original_data)
    s0 = snapshot()
    print(f"[0] 사전 확인 통과 · S0 {len(s0)}개 · ledger_before {ledger_before}")

    # ── [1] HTML 사전 매체 검사 (추출 전) ──
    html_text = html_path.read_text(encoding="utf-8")
    pc = precheck_html(html_text, ymd, rules)
    print(f"[1] HTML cards={pc['cards']}, expected_ids_match={pc['ids_match']}")
    if pc["cards"] != 8:
        die(f"[1] 카드 수가 8이 아님: {pc['cards']}")
    if not pc["ids_match"]:
        die(f"[1] 카드 ID 집합 불일치: {sorted(set(pc['ids']) ^ set(pc['expected_ids']))}")
    print(f"[1] sources={len([1 for _, n in pc['sources'] if n])}, empty={pc['empty']}, duplicate_card_ids={pc['dup_ids']}")
    if pc["empty"] or pc["dup_ids"]:
        die(f"[1] source 누락 {pc['empty']} / 중복 ID {pc['dup_ids']} → 중단")
    if pc["unknown"]:
        print(f"[1] UNKNOWN={len(pc['unknown'])}: {pc['unknown']}")
        print("    scripts/source_rules.json 에 아래 형식으로 추가 후 같은 명령을 재실행하세요:")
        for nm in pc["unknown"]:
            print(f'      "{nm}": {{ "region": "국내|해외", "group": "{nm}" }}')
        die("[1] UNKNOWN 매체 → JSON 추출하지 않고 중단")
    print("[1] UNKNOWN=0")

    # ── [2] 추출 ──
    rc, out, err = run_python(["scripts/extract_cards.py", str(html_path.relative_to(ROOT)).replace("\\", "/"), "--out", "content/news"], "[2]")
    if rc != 0:
        die(f"[2] extract_cards 실패 (rc={rc})\n{out}\n{err}")
    s1 = snapshot()
    new = sorted(set(s1) - set(s0))
    deleted = sorted(set(s0) - set(s1))
    changed = sorted(k for k in (set(s0) & set(s1)) if s0[k] != s1[k])
    exp_new = {f"content/news/{ymd}-{s}-{i:03d}.json" for s in ("ai", "design") for i in range(1, 5)}
    if set(new) != exp_new or deleted or changed:
        die(f"[2] S0→S1 위반: 신규{len(new)} 삭제{len(deleted)} 기존변경{len(changed)}")
    print(f"[2] 추출 8개 · 기존 무변경 · 삭제 0")

    # ── [3] 구성 균형 (JSON 기준 교차검증) ──
    targets = {c: NEWS_DIR / f"{c}.json" for c in exp_keys}
    named = []
    for c in sorted(exp_keys):
        d = json.loads(targets[c].read_text(encoding="utf-8"))
        named.append((c, d["section"], d["source"]["name"]))
    rows = balance(named, rules)
    print("[3] | contentId | 섹션 | source.name | region | group |")
    for cid, sec, name, region, group in rows:
        print(f"    | {cid} | {sec} | {name} | {region} | {group} |")
    unknown = [r for r in rows if r[3] == "UNKNOWN"]
    if unknown:
        die(f"[3] UNKNOWN {len(unknown)} (추출기가 매체명 변형?): {[r[2] for r in unknown]}")
    from collections import Counter
    ai = [r for r in rows if r[1] == "ai"]; ds = [r for r in rows if r[1] == "design"]
    def cnt(rs, reg): return sum(1 for r in rs if r[3] == reg)
    grp = Counter(r[4] for r in rows)
    over = [g for g, c in grp.items() if c > 2]
    ok3 = (cnt(ai, "국내") == 2 and cnt(ai, "해외") == 2 and cnt(ds, "국내") == 2
           and cnt(ds, "해외") == 2 and not over)
    print(f"[3] AI 국내{cnt(ai,'국내')}·해외{cnt(ai,'해외')} / Design 국내{cnt(ds,'국내')}·해외{cnt(ds,'해외')} / group {dict(grp)}")
    if not ok3:
        die("[3] 구성 균형 위반 → 중단.\n"
            f"    생성된 content/news/{ymd}-*.json 8개를 삭제한 뒤 브리핑을 수정하고 다시 실행하세요.\n"
            f"    삭제: Remove-Item content\\news\\{ymd}-*.json")

    # ── [4] 판정값 원자 적용 ──
    status, msg = apply_atomic(judg, targets)
    print(f"[4] {status}: {msg}")
    if status == "fatal":
        die("[4] FATAL — 이후 단계 전부 중단하고 즉시 보고", 2)
    if status != "ok":
        die("[4] ERROR — 원본 복구됨, 재시도 가능")
    s2 = snapshot()
    changed2 = sorted(k for k in (set(s1) & set(s2)) if s1[k] != s2[k])
    new2 = sorted(set(s2) - set(s1)); del2 = sorted(set(s1) - set(s2))
    if not (set(changed2) <= exp_new and not new2 and not del2):
        die(f"[4] S1→S2 위반: 변경범위 {changed2}")
    if not all(_matches(json.loads(targets[c].read_text(encoding="utf-8")), judg[c]) for c in judg):
        die("[4] 최종 상태 불일치")
    print(f"[4] S1→S2 통과 · 실제 변경 {len(changed2)}개 · 최종 상태 일치")

    # ── [5] AI ★4~5 ──
    ai_scores = [json.loads((NEWS_DIR / f"{ymd}-ai-{i:03d}.json").read_text(encoding="utf-8"))["impactScore"] for i in range(1, 5)]
    high = sum(1 for x in ai_scores if x >= 4)
    print(f"[5] AI scores {ai_scores} · high45 {high}" + ("" if high else "  (0장 — §9-1 기록 대상, 실패 아님)"))

    # ── [6] JSON 검증 (ERROR 집계로 판정) ──
    rc, out, err = run_python(["scripts/validate_json.py"], "[6]")
    m = re.search(r"ERROR (\d+)건 · WARN (\d+)건", out)
    if not m:
        die(f"[6] validate_json 출력 파싱 실패\n{out}\n{err}")
    e_cnt, w_cnt = int(m.group(1)), int(m.group(2))
    total_m = re.search(r"검사 대상 (\d+)장", out)
    print(f"[6] validate_json ERROR {e_cnt} · WARN {w_cnt} · 총 {total_m.group(1) if total_m else '?'}장")
    if e_cnt > 0:
        die(f"[6] validate_json ERROR {e_cnt}건 → 중단\n{out}")
    if rc != 0 and w_cnt == 0:
        die(f"[6] returncode {rc} 인데 정상 WARN 으로 설명 안 됨\n{out}\n{err}")

    # ── [7] 발행 대장 ──
    rc, out, err = run_python(["scripts/build_published_urls.py"], "[7]")
    if rc != 0:
        die(f"[7] build_published_urls 실패 (rc={rc})\n{out}\n{err}")
    current_data = json.loads(LEDGER.read_text(encoding="utf-8-sig")) if LEDGER.exists() else {}
    if current_data == ledger_original_data:
        if LEDGER.exists() and LEDGER.read_bytes() != (ledger_original_bytes or b""):
            run_command(["git", "restore", "--", "published_urls.json"], "[7]")
            print("[7] 대장 의미상 동일 · 바이트 차이 → git restore")
        else:
            print("[7] 대장 변화 없음")
    else:
        ak, bk = set(ledger_original_data), set(current_data)
        added = sorted(bk - ak); removed = sorted(ak - bk)
        changed_date = [k for k in (ak & bk) if ledger_original_data[k] != current_data[k]]
        die(f"[7] 대장 실질 변경 → 자동 restore 금지, 중단\n"
            f"    added={added[:10]}\n    removed={removed[:10]}\n    changed_date={changed_date[:10]}")
    uniq = len({json.loads(p.read_text(encoding='utf-8'))['url'] for p in NEWS_DIR.glob('*.json')})
    print(f"[7] ledger_before {ledger_before} · 최종 대장 {len(current_data)} · 고유 URL {uniq}")
    if not (len(current_data) == uniq and len(current_data) >= ledger_before):
        die(f"[7] 대장 판정 실패: 최종 {len(current_data)} · 고유 {uniq} · before {ledger_before}")

    # ── [8] 빌드 ──
    # Windows 는 npm 이 npm.cmd 라 subprocess 가 직접 실행 못 함 → cmd /c 로 감싼다.
    npm_cmd = ["cmd", "/c", "npm", "run", "build"] if os.name == "nt" else ["npm", "run", "build"]
    rc, out, err = run_command(npm_cmd, "[8]")
    if rc != 0:
        die(f"[8] 빌드 실패\n{out[-2000:]}\n{err[-1000:]}")
    dist = ROOT / "dist" / "news" / "2026" / "07"
    brief = len(list(dist.glob("Dinol_news_*.html")))
    detail = len([p for p in dist.glob("*.html") if re.match(r"^\d{8}-(ai|design)-\d{3}$", p.stem)])
    exp_detail = len(list(NEWS_DIR.glob("*.json")))
    exp_brief = len({json.loads(p.read_text(encoding='utf-8'))['date'] for p in NEWS_DIR.glob('*.json')})
    print(f"[8] 빌드 · 브리핑 {brief}/{exp_brief} · 상세 {detail}/{exp_detail}")
    if brief != exp_brief or detail != exp_detail:
        die("[8] 빌드 산출물 개수 불일치")

    # ── [9] 페이지 검증 ──
    rc, out, err = run_python(["scripts/validate_details.py"], "[9]")
    if "불일치 합계: 0" not in out or "PASS" not in out:
        die(f"[9] validate_details 실패\n{out[-2000:]}")
    # V37 동적 대조
    cards = [json.loads(p.read_text(encoding="utf-8")) for p in NEWS_DIR.glob("*.json")]
    empty_pos = {c["contentId"] for c in cards if not c["positions"]}
    valid_pos = {c["contentId"] for c in cards if c["positions"]}
    unknown_id = sum(1 for c in cards for pid in c["positions"] if pid not in VALID_POSITIONS)
    if not (len(empty_pos) + len(valid_pos) == len(cards) and unknown_id == 0):
        die(f"[9] V37 동적 대조 실패: 빈{len(empty_pos)}+유효{len(valid_pos)}≠{len(cards)} · 미등록{unknown_id}")
    print(f"[9] validate_details PASS · V37 빈{len(empty_pos)}/유효{len(valid_pos)}/미등록0")
    rc, out, err = run_python(["scripts/validate_briefing.py"], "[9]")
    if "불일치 합계: 0" not in out or "PASS" not in out:
        die(f"[9] validate_briefing 실패\n{out[-2000:]}")
    print("[9] validate_briefing PASS")

    # ── [10] 링크 ──
    rc, out, err = run_python(["scripts/check_links.py"], "[10]")
    hm = re.search(r"검사한 HTML 파일 수\s*:\s*(\d+)", out)
    if "깨진 링크: 0건" not in out:
        die(f"[10] 깨진 링크 존재\n{out[-1500:]}")
    print(f"[10] 링크 OK · 검사 HTML {hm.group(1) if hm else '?'}개")

    # ── 마지막 ──
    dt = time.monotonic() - t0
    print(f"\n[PASS] 전체 통과 · {dt:.1f}s")
    print("커밋 대상:")
    print(f"  content/news/{ymd}-*.json  8개")
    print(f"  scripts/daily/{ymd}.json   1개")
    if changed_sr:
        print(f"  scripts/source_rules.json  (매체 추가)")
    print(f"예시: git add -- content/news/{ymd}-*.json scripts/daily/{ymd}.json")
    return 0


def main():
    try:
        run_pipeline()
        return 0
    except DailyImportError as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
