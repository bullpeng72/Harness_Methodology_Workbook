"""파이프라인 오케스트레이션 — docs/DESIGN.md(컴포넌트 분해)의 진입점.

순서(제약): sanitize → classify → (저신뢰면 조기 종료) → review+aggregate →
retrieve → draft → escalation-check → PII scrub → TriageResult.

S5(Gate C/D 공유 원인 = SLA): LLM 호출 수를 줄여 p95 지연을 낮춘다.
- 리뷰어: classifier confidence >= REVIEW_CONF_SKIP 이면 건너뛴다(단일 에이전트 경로).
- 에스컬레이션: 환불·잠금 키워드가 없으면 LLM 확인 없이 escalate=None.
둘 다 정확도에 영향을 주는 축소가 아니다(고신뢰 분류·키워드 없는 티켓만 스킵).
"""
from __future__ import annotations

import re
import time

from .classifier import classify
from .drafter import draft_reply
from .escalation import check_escalation
from .llm import LLM
from .retriever import Retriever
from .review import review_and_aggregate
from .sanitize import sanitize_ticket_text, scrub_pii
from .types import NO_EVIDENCE, Ticket, TriageResult

_MAX_LLM_RETRIES = 1  # docs/DESIGN.md(에러 정책) / Ch 15
REVIEW_CONF_SKIP = 0.80  # S5: 이 이상 confidence면 리뷰어 스킵 (단일 에이전트)
_ESCALATION_KEYWORDS = re.compile(
    r"환불|결제\s*취소|중복\s*청구|refund|잠긴|잠금\s*해제|계정\s*풀|unlock|2fa|otp|비밀번호\s*초기화"
)


def classify_ticket(
    ticket: Ticket,
    *,
    retriever: Retriever | None = None,
    llm: LLM | None = None,
) -> TriageResult:
    """티켓 1건을 분류·초안·에스컬레이션 판정한다.

    Args:
        ticket: 입력 티켓.
        retriever: KB 리트리버(재사용 시 주입). 미지정 시 새로 생성.
        llm: Tier 2 호출기(재사용 시 주입).

    Returns:
        완전한 ``TriageResult`` (docs/DESIGN.md 출력 스키마). LLM 호출이 재시도 후에도
        실패하면 ``category="other", priority="P3"`` 와 ``error`` 필드로 폴백한다.
    """
    llm = llm or LLM("tier2")
    retriever = retriever or Retriever()
    stage_ms: dict[str, float] = {}

    try:
        # 1) classify (재시도 포함)
        t0 = time.perf_counter()
        writer = _with_retry(lambda: classify(ticket, llm=llm), "classify")
        # 2) 저신뢰 조기 종료 / 고신뢰 리뷰어 스킵 (S5 — LLM 호출 축소)
        if writer.category == "other" and writer.priority == "P3":
            clf = writer                                           # ST-005 강등, 검토 불필요
        elif writer.confidence >= REVIEW_CONF_SKIP:
            clf = writer                                           # 고신뢰 → 단일 에이전트
        else:
            clf = review_and_aggregate(ticket, writer, llm=llm)    # 불확실 → 리뷰어+집계자
        stage_ms["classify"] = (time.perf_counter() - t0) * 1000

        # 3) retrieve
        t1 = time.perf_counter()
        safe_query = sanitize_ticket_text(ticket.text)
        passages = retriever.search(safe_query)
        stage_ms["retrieve"] = (time.perf_counter() - t1) * 1000

        # 4) draft
        t2 = time.perf_counter()
        draft = _with_retry(lambda: draft_reply(safe_query, passages, llm=llm), "draft")
        stage_ms["draft"] = (time.perf_counter() - t2) * 1000

        # 5) escalation check (부작용 없음, ST-003) — 키워드가 있을 때만 LLM 확인
        escalation = (
            check_escalation(ticket, llm=llm)
            if _ESCALATION_KEYWORDS.search(ticket.text)
            else None
        )

    except _StageError as err:
        return TriageResult(
            ticket_id=ticket.ticket_id, category="other", priority="P3",
            confidence=0.0, draft_reply=NO_EVIDENCE,
            reasoning="LLM 호출 실패 — 폴백",
            error={"stage": err.stage, "type": err.kind, "retries": _MAX_LLM_RETRIES,
                   "last_message": err.message},
        )

    # 6) 출력 PII 스크럽 (ST-007) — 이중 방어
    clean_reply, leaked = scrub_pii(draft.reply)

    reasoning = (
        f"{clf.reasoning} | 근거 {len(draft.citations)}건"
        + (" | PII 마스킹됨" if leaked else "")
        + f" | 지연 {stage_ms.get('draft', 0):.0f}ms(draft)"
    )
    return TriageResult(
        ticket_id=ticket.ticket_id,
        category=clf.category,
        priority=clf.priority,
        confidence=clf.confidence,
        draft_reply=clean_reply,
        reasoning=reasoning,
        kb_citations=draft.citations,
        escalate=escalation,
    )


# --------------------------------------------------------------------------- util
class _StageError(Exception):
    def __init__(self, stage: str, kind: str, message: str) -> None:
        self.stage, self.kind, self.message = stage, kind, message
        super().__init__(f"{stage}: {message}")


def _with_retry(fn, stage: str):  # type: ignore[no-untyped-def]  (내부 헬퍼)
    """``fn`` 을 최대 ``_MAX_LLM_RETRIES`` 회 재시도한다. 마지막 실패는 ``_StageError``."""
    last: Exception | None = None
    for _ in range(_MAX_LLM_RETRIES + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last = exc
    raise _StageError(stage, type(last).__name__, str(last) if last else "unknown")
