"""v4 멀티에이전트 — 리뷰어 + 집계자 (Gate F, Ch 30).

- 작성자(writer): classifier 가 이미 낸 분류.
- 리뷰어(reviewer): 동의 여부만 반환한다. 재작성 금지 — 출력 스키마로 역할을 강제.
- 집계자(aggregator): 규칙 기반. 불일치 시 재작성 1회, 그래도 불일치면 other 로 강등.
"""
from __future__ import annotations

import json

from .classifier import Classification, classify
from .llm import LLM
from .types import Ticket

_REVIEWER_SYSTEM = """너는 분류 리뷰어다. 작성자의 (category, priority) 판정에 동의하는지만 답한다.
bug 로 의심될 근거를 먼저 찾아본다(작성자와 다른 관점을 유지).
답변을 새로 쓰지 마라. 출력 JSON 만: {"agree": true|false, "objection": "반대 근거 한 문장 또는 null"}
"""

_MAX_ROUNDS = 1


def review_and_aggregate(ticket: Ticket, writer: Classification, llm: LLM | None = None) -> Classification:
    """리뷰어 판정을 받아 집계 규칙을 적용한다.

    Returns:
        최종 ``Classification``. 합의 시 작성자안, 불일치 시 재작성 1회 후에도
        불일치면 ``("other", "P3")`` 로 강등.
    """
    llm = llm or LLM("tier2")
    current = writer

    for _round in range(_MAX_ROUNDS + 1):
        verdict = _review(ticket, current, llm)
        if verdict["agree"]:
            return current
        if _round == _MAX_ROUNDS:
            break
        # 재작성 1회 — 리뷰어 근거를 작성자에게 힌트로 전달.
        hint = f"\n\n리뷰어 반대: {verdict['objection']}"
        rewritten = classify(
            Ticket(ticket.ticket_id, ticket.subject, ticket.body + hint), llm=llm
        )
        current = rewritten

    return Classification(
        "other", "P3", min(current.confidence, 0.49),
        f"{current.reasoning} | 리뷰어와 최종 불일치 → other/P3 강등",
    )


def _review(ticket: Ticket, c: Classification, llm: LLM) -> dict[str, object]:
    user = (
        f"<ticket>\n{ticket.text}\n</ticket>\n\n"
        f"작성자 판정: category={c.category}, priority={c.priority}"
    )
    raw = llm.complete(system=_REVIEWER_SYSTEM, user=user, max_tokens=120)
    try:
        start, end = raw.index("{"), raw.rindex("}") + 1
        data = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return {"agree": True, "objection": None}  # 리뷰어 파싱 실패 시 작성자안 유지
    return {"agree": bool(data.get("agree", True)), "objection": data.get("objection")}
