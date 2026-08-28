"""SupportTriage 도메인 타입.

docs/DESIGN.md §5 (출력 스키마)의 구현. ``schema_version`` 은 ``docs/IRREVERSIBLE.md`` 에
등재돼 있으므로 변경 시 마이그레이션이 필요하다(optional 필드 추가는 하위호환이라 예외).
"""
from __future__ import annotations

import dataclasses
from typing import Literal

SCHEMA_VERSION = "1"

Category = Literal["billing", "bug", "how-to", "account", "abuse", "other"]
Priority = Literal["P1", "P2", "P3"]
EscalationAction = Literal["refund_request", "account_unlock"]

CATEGORIES: tuple[Category, ...] = ("billing", "bug", "how-to", "account", "abuse", "other")
PRIORITIES: tuple[Priority, ...] = ("P1", "P2", "P3")

# ST-005: 이 값 미만이면 category="other", priority="P3" 로 강등한다.
CONFIDENCE_FLOOR = 0.5
# ST-004: top passage 유사도가 이 값 미만이면 draft_reply 를 "근거 없음" 으로 둔다.
GROUNDING_THRESHOLD = 0.35
NO_EVIDENCE = "근거 없음"


@dataclasses.dataclass(frozen=True)
class Ticket:
    """지원 티켓 1건 (입력).

    Example::

        Ticket(ticket_id="T-1043", subject="결제가 두 번 됐어요",
               body="오늘 오전에 카드로 두 번 청구된 것 같습니다.")
    """

    ticket_id: str
    subject: str
    body: str

    @property
    def text(self) -> str:
        """분류·검색에 쓰는 결합 텍스트 (원문 — 살균 전)."""
        return f"{self.subject}\n\n{self.body}".strip()


@dataclasses.dataclass(frozen=True)
class Escalation:
    """사람 승인이 필요한 액션 (ST-003). 이 객체는 액션을 **실행하지 않는다** —
    실행 대상을 사람 큐로 넘긴다는 선언일 뿐이다."""

    action: EscalationAction
    reason: str


@dataclasses.dataclass
class TriageResult:
    """분류 결과 (출력). ``to_dict()`` 가 docs/DESIGN.md §5 스키마와 1:1 대응한다."""

    ticket_id: str
    category: Category
    priority: Priority
    confidence: float
    draft_reply: str
    reasoning: str = ""
    kb_citations: list[str] = dataclasses.field(default_factory=list)
    escalate: Escalation | None = None
    error: dict[str, object] | None = None
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        """평가 하네스·다운스트림이 파싱하는 JSON 형태."""
        out: dict[str, object] = {
            "schema_version": self.schema_version,
            "ticket_id": self.ticket_id,
            "category": self.category,
            "priority": self.priority,
            "confidence": round(self.confidence, 4),
            "draft_reply": self.draft_reply,
            "reasoning": self.reasoning,
            "kb_citations": list(self.kb_citations),
        }
        if self.escalate is not None:
            out["escalate"] = {"action": self.escalate.action, "reason": self.escalate.reason}
        if self.error is not None:
            out["error"] = self.error
        return out
