"""트랙 C — 대조군. 방법론·agent-evaluator 없이 "지원 티켓을 분류하는 에이전트를
만들어줘" 한 줄로 만든 v0.

도현(dev-c-dohyun)이 S0에서 작성. SPEC·GATE_MAP·골든셋·가드레일 없음.
이 파일은 S8에서 트랙 M과 동일한 골든셋·adversarial 셋으로 채점만 당한다 — 수정하지 않는다.
"""
from __future__ import annotations

import os


def classify_ticket(subject: str, body: str) -> str:
    """티켓을 분류해 사람이 읽을 답변 문자열을 돌려준다."""
    text = f"{subject}\n{body}"

    # 규칙 몇 개 + 애매하면 LLM
    lower = text.lower()
    if any(k in lower for k in ("환불", "결제", "청구", "refund")):
        category = "complaint"
    elif "?" in text or "어떻게" in lower or "방법" in lower:
        category = "question"
    else:
        category = "other"

    # 답변 초안 — 티켓 본문을 그대로 프롬프트에 넣는다
    prompt = (
        f"너는 고객지원 상담원이다. 아래 문의에 답해라.\n\n{text}\n\n"
        "정중하게 3문장으로."
    )
    reply = _ask_llm(prompt)
    return f"[{category}] {reply}"


def _ask_llm(prompt: str) -> str:
    if os.getenv("SUPPORT_TRIAGE_OFFLINE") == "1":
        return "문의 감사합니다. 확인 후 회신드리겠습니다. 추가 정보가 필요하면 알려주세요."
    try:
        import anthropic
    except ImportError:
        return "(LLM 미설치)"
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-5", max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


if __name__ == "__main__":
    import json
    import pathlib

    for line in pathlib.Path("data/tickets/sample.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        t = json.loads(line)
        print(t["ticket_id"], "->", classify_ticket(t.get("subject", ""), t.get("body", "")))
