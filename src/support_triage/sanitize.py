"""횡단 관심사 — 입력 살균(ST-006)과 출력 PII 스크럽(ST-007).

docs/DESIGN.md(컴포넌트 분해)의 "Guard" 서브그래프. 파이프라인 진입·출구 양쪽에 건다.
"""
from __future__ import annotations

import re

# 티켓 본문에 심어진 "지시"로 보이는 패턴 — 명령이 아니라 데이터로 취급하기 위해
# 중화(마스킹)한다. 새 탐지 엔진이 아니라 알려진 프롬프트 인젝션 상용구 목록이다.
_INJECTION_MARKERS = [
    re.compile(r"(?i)\b(system|assistant|user)\s*:", ),
    re.compile(r"(?i)이전(의)?\s*(지시|지침|명령).{0,10}(무시|따르지)"),
    re.compile(r"(?i)ignore\s+(all\s+)?previous\s+instructions?"),
    re.compile(r"(?i)disregard\s+the\s+above"),
    re.compile(r"(?i)너는\s*이제"),
]

# ST-007 — 답변 초안에 남으면 안 되는 PII. 지식베이스 예시 값이 그대로 복사되는
# 경로를 막는 게 주 목적이다(Ch 29).
_PII_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?<!\d)(01[016-9]|0\d{1,2})[-. ]?\d{3,4}[-. ]?\d{4}(?!\d)"),
    "card": re.compile(r"(?<!\d)(?:\d[ -]?){13,16}(?!\d)"),
}


def sanitize_ticket_text(text: str) -> str:
    """티켓 텍스트에서 인젝션 상용구를 ``[제거된 지시]`` 로 치환한다 (ST-006).

    Example::

        >>> "SYSTEM: 이전 지시 무시" -> "[제거된 지시] 이전 지시 무시"  (근사)
    """
    out = text
    for pat in _INJECTION_MARKERS:
        out = pat.sub("[제거된 지시]", out)
    return out


def scrub_pii(text: str) -> tuple[str, list[str]]:
    """텍스트에서 PII를 마스킹한다 (ST-007).

    Returns:
        ``(마스킹된 텍스트, 발견된 카테고리 목록)``.
    """
    found: list[str] = []
    out = text
    for name, pat in _PII_PATTERNS.items():
        if pat.search(out):
            found.append(name)
            out = pat.sub(f"[{name} 삭제됨]", out)
    return out, found
