"""SupportTriage — 지원 티켓 분류·초안·에스컬레이션 에이전트.

《하니스 메서드 실습서》의 러닝 예제. 최종 상태(v4): 7개 Gate 전부 PASS.

Example::

    from support_triage import classify_ticket, Ticket

    result = classify_ticket(Ticket(
        ticket_id="T-1043",
        subject="결제가 두 번 됐어요",
        body="오늘 오전에 카드로 두 번 청구된 것 같습니다. 환불 부탁드려요.",
    ))
    print(result.to_dict())
"""
from __future__ import annotations

from .llm import LLM
from .pipeline import classify_ticket
from .retriever import Retriever
from .types import (
    CATEGORIES,
    PRIORITIES,
    SCHEMA_VERSION,
    Category,
    Escalation,
    Priority,
    Ticket,
    TriageResult,
)

__all__ = [
    "classify_ticket",
    "Ticket",
    "TriageResult",
    "Escalation",
    "Category",
    "Priority",
    "CATEGORIES",
    "PRIORITIES",
    "SCHEMA_VERSION",
    "Retriever",
    "LLM",
]

__version__ = "0.4.0"  # v4 — Ch 31 종료 시점
