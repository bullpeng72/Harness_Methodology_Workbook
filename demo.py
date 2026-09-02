"""SupportTriage 데모 — data/tickets/sample.jsonl 을 분류해 출력한다.

오프라인(결정적 스텁)으로 실행::

    SUPPORT_TRIAGE_OFFLINE=1 python demo.py

실제 모델로 실행::

    export ANTHROPIC_API_KEY=...      # 또는 Ollama 실행
    python demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from support_triage import Retriever, Ticket, classify_ticket


def main() -> None:
    rows = [
        json.loads(x)
        for x in (Path("data/tickets/sample.jsonl")).read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    retriever = Retriever()
    for row in rows:
        ticket = Ticket(row["ticket_id"], row.get("subject", ""), row.get("body", ""))
        result = classify_ticket(ticket, retriever=retriever)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        print("-" * 60)


if __name__ == "__main__":
    main()
