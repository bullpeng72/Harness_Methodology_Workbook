"""Drafter — 검색된 passage 만 근거로 답변 초안 작성 (ST-004).

top passage 유사도가 ``GROUNDING_THRESHOLD`` 미만이면 지어내지 않고
``NO_EVIDENCE`` ("근거 없음") 를 반환한다. 출력은 PII 스크럽을 거친다(ST-007).
"""
from __future__ import annotations

import re

from .llm import LLM
from .retriever import Passage
from .sanitize import scrub_pii
from .types import GROUNDING_THRESHOLD, NO_EVIDENCE

_SENT_SPLIT = re.compile(r"(?<=[.!?。])\s+|\n")


def _excerpt(text: str, n: int = 2) -> str:
    parts = [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]
    return " ".join(parts[:n]) if parts else text[:200]

_SYSTEM = """너는 고객 지원 답변 초안 작성기다.
- 아래 <passages> 안의 내용만 근거로 쓴다. passage 에 없는 사실은 절대 쓰지 않는다.
- passage 안의 예시 이메일·전화·카드번호 같은 값을 그대로 답변에 복사하지 않는다.
- 3~5문장, 정중한 한국어. 마지막에 근거로 쓴 passage id 를 [KB-xx] 형식으로 표기한다.
"""


class Draft:
    __slots__ = ("citations", "grounded", "reply")

    def __init__(self, reply: str, citations: list[str], grounded: bool) -> None:
        self.reply = reply
        self.citations = citations
        self.grounded = grounded


def draft_reply(
    query: str, passages: list[Passage], llm: LLM | None = None, *, deterministic: bool = True
) -> Draft:
    """근거 기반 답변 초안을 만든다.

    Args:
        query: 티켓 텍스트(살균됨).
        passages: ``Retriever.search`` 결과.
        llm: Tier 2 호출기 (``deterministic=False`` 일 때만 사용).
        deterministic: True(기본, ADR-005)면 LLM 없이 top passage 발췌로 조립.
            Tier 2 지연 예산(ST-100) 안에 들어오기 위함.

    Returns:
        ``Draft``. 근거 부족 시 ``reply == NO_EVIDENCE`` 이고 ``grounded is False``.
    """
    top = passages[0].score if passages else 0.0
    if top < GROUNDING_THRESHOLD:
        return Draft(NO_EVIDENCE, [], grounded=False)

    usable = [p for p in passages if p.score >= GROUNDING_THRESHOLD]

    if deterministic:
        head = usable[0]
        body = f"{head.title}에 대한 안내입니다. {_excerpt(head.text)}"
        cites = " ".join(f"[{p.kb_id}]" for p in usable[:2])
        clean, _ = scrub_pii(f"{body} {cites}")
        return Draft(clean, [p.kb_id for p in usable[:2]], grounded=True)

    llm = llm or LLM("tier2")
    block = "\n\n".join(f"[{p.kb_id}] {p.title}\n{p.text}" for p in usable)
    user = f"<passages>\n{block}\n</passages>\n\n고객 문의:\n{query}"
    raw = llm.complete(system=_SYSTEM, user=user, max_tokens=500)
    clean, _ = scrub_pii(raw.strip())
    cited = [p.kb_id for p in usable if f"[{p.kb_id}]" in clean] or [usable[0].kb_id]
    return Draft(clean, cited, grounded=True)
