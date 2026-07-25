#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validation_common.py — HTML 검증(validate.py)과 JSON 검증(validate_json.py)이
공유하는 정책 상수·공용 함수. 양쪽이 동일한 기준을 쓰게 하기 위한 단일 출처.

★설계 원칙★
  여기의 함수는 어떤 입력이 들어와도 예외를 던지지 않는다.
  방어는 호출부가 아니라 여기서 끝낸다.
"""

import re
from datetime import datetime

# ────────────────────────────────────────────────────────────
# 정책 적용일 상수 (None 이면 해당 검사 비활성)
# ────────────────────────────────────────────────────────────
CARD_COUNT_POLICY_FROM     = "2026-07-06"   # 8카드(AI 4 + Design 4) 구조 확립일
POSITION_SCHEMA_FROM       = None           # data-position 도입일 (코드 반영 시 기입)
CATEGORY_EN_SCHEMA_FROM    = None           # data-category-en 도입일 (코드 반영 시 기입)
CONTENT_ID_SCHEMA_FROM     = None           # 상세 페이지 전환 확정 시 날짜 기입
SECTION_RUBRIC_POLICY_FROM = None           # 섹션별 별점 기준 적용일(재채점 후 기입)
EN_LANGUAGE_POLICY_FROM    = None           # EN 카드 언어 슬롯 정책 적용일

# ────────────────────────────────────────────────────────────
# 상수
# ────────────────────────────────────────────────────────────
VALID_POSITIONS = {
    "ux-designer", "ui-designer", "product-designer", "service-designer",
    "brand-designer", "bx-designer", "graphic-designer", "editorial-designer",
    "motion-designer", "video-designer", "illustrator", "art-director",
    "industrial-designer", "space-designer", "architect", "package-designer",
    "typographer", "fashion-designer", "design-lead", "design-manager",
}

ALLOWED_SECTIONS = ("ai", "design")

CONTENT_ID_RE = re.compile(r'^\d{8}-(?:ai|design)-\d{3}$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

_HANGUL_RE = re.compile(r'[가-힣ᄀ-ᇿ㄰-㆏]')
_LATIN_RE = re.compile(r'[A-Za-z]')


# ────────────────────────────────────────────────────────────
# 함수
# ────────────────────────────────────────────────────────────
def applies(policy_from, file_date):
    """정책 적용 대상인지. policy_from 이 None 이면 비활성(False)."""
    if policy_from is None:
        return False
    try:
        return file_date >= policy_from
    except TypeError:
        return False


def normalize_slot(value):
    """
    None → None
    list → '|'.join(str(v))
    str  → CRLF·CR 을 LF 로만 정규화 (strip/연속공백 축약 금지)
    그 외 → str(value) (방어)
    """
    if value is None:
        return None
    if isinstance(value, list):
        return "|".join(str(v) for v in value)
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n")
    return str(value)


def is_korean_slot(value):
    """
    ★normalize_slot() 을 거친 문자열만 넣을 것★
    has_hangul and (not has_latin or 한글비율 >= 0.5)
    """
    if not isinstance(value, str):
        return False
    h = len(_HANGUL_RE.findall(value))
    l = len(_LATIN_RE.findall(value))
    if h == 0:
        return False
    if l == 0:
        return True
    return (h / (h + l)) >= 0.5


def is_missing_slot(value):
    """
    ★문자열·배열 전용. 숫자·불리언에 쓰지 마★
    None / 빈문자열(strip 후) / 빈배열 / 배열 안 빈문자열 → True
    """
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        if len(value) == 0:
            return True
        for el in value:
            if el is None:
                return True
            if isinstance(el, str) and el.strip() == "":
                return True
        return False
    # 문자열·배열이 아니면 판단 대상 아님 → 누락 아님으로 본다(방어)
    return False


def has_slot_value(value):
    return not is_missing_slot(value)


def is_plain_int(value):
    """★isinstance(True, int) 는 True 다. bool 반드시 제외★"""
    return isinstance(value, int) and not isinstance(value, bool)


def get_pair(data, key):
    """부모가 dict 가 아니면 None 반환."""
    if isinstance(data, dict):
        return data.get(key)
    return None


def is_real_date(s, fmt="%Y-%m-%d"):
    """strptime 으로 실제 파싱까지 확인 (2026-02-31 차단)."""
    if not isinstance(s, str):
        return False
    try:
        datetime.strptime(s, fmt)
        return True
    except (ValueError, TypeError):
        return False
