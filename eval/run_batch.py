"""배치 평가 하네스 — SupportTriage (@agent_eval 계층).

GATE_MAP·DESIGN §3에서 "켠다"고 한 Config만 연결한다. 실시간 가드레일
(runtime: ``guardrail_profiles/runtime.json`` / dev: ``.claude/.agent-evaluator/``)과는
**다른 파일**이다(본편 원칙 3).

실행::

    python eval/run_batch.py --golden data/golden --note "v0 규칙기반 기준선"
    # 결과: results/evaluation.json  (+ agent_version 태그)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from support_triage import Retriever, Ticket, classify_ticket  # noqa: E402

from agent_evaluator import (  # noqa: E402
    ComplianceConfig,
    ExplainabilityConfig,
    InstructionConfig,
    LoopDetectionConfig,
    PerformanceMonitor,
    SLAConfig,
    ScopeConfig,
    SubtaskConfig,
    ThreatResponseConfig,
    ThreatSeverityConfig,
    agent_eval,
)

# S3 관찰: 아래 Config 필드명은 SDK 1.0.0rc3 실제 시그니처로 맞춘 것.
# 워크북 초판(Ch 17·25)은 InstructionConfig(required_output_keys=...) 등 존재하지 않는
# 인자를 썼다 — "실제로 돌리니" 즉시 TypeError로 드러났다. (docs/observations/S3.md)

_CATS = ("billing", "bug", "how-to", "account", "abuse", "other")
_PRIOS = ("P1", "P2", "P3")


def load_golden(golden_dir: Path) -> list[dict]:
    """golden_core/boundary/priority + adversarial 를 하나의 케이스 리스트로."""
    cases: list[dict] = []
    for name in ("golden_core.json", "golden_boundary.json", "golden_priority.json"):
        p = golden_dir / name
        if p.exists():
            for c in json.loads(p.read_text(encoding="utf-8")).get("cases", []):
                cases.append({
                    "ticket_id": c["ticket_id"], "subject": c.get("subject", ""),
                    "body": c.get("body", ""),
                    "gt_category": c["category"], "gt_priority": c["priority"],
                })
    return cases


def score_classification(response: str, ground_truth: str) -> float:
    """카테고리 일치 0.5 + 우선순위 일치 0.5. response 는 TriageResult JSON."""
    try:
        r = json.loads(response)
    except (ValueError, TypeError):
        return 0.0
    gt_cat, _, gt_prio = ground_truth.partition(" ")
    s = 0.0
    if r.get("category") == gt_cat:
        s += 0.5
    if r.get("priority") == gt_prio:
        s += 0.5
    return s


def build_monitor(note: str, *, enable_judge: bool) -> "PerformanceMonitor":
    return PerformanceMonitor(
        output_dir=str(_ROOT / "results"),
        agent_version="auto",
        prompt_version=note.split()[0] if note else None,   # 본편 §2 — 조회 가능한 버전 키
        iteration_note=note,
        enable_security_metrics=True,                        # Gate E
        enable_llm_judge=enable_judge,                       # Gate C — S5에서 켠다
        judge_sample_rate=0.3,
        enable_pii_redaction=True,
        pii_redaction_categories=["email", "phone", "card"],
    )


def make_agent(monitor):  # type: ignore[no-untyped-def]
    retriever = Retriever()

    # DESIGN §3 "켠다" — 단, GoalAlignmentConfig 는 비도구 에이전트라 제외
    # (gate2-review R1: use_llm_scoring 없이 켜면 상수 0.0).
    @agent_eval(
        monitor,
        task_type="classification",
        score_fn=score_classification,
        instructions=InstructionConfig(expected_format="json", fail_on_violation=False),
        subtask_tracking=SubtaskConfig(
            expected_subtasks=["classify", "prioritize", "draft", "escalate_check"]
        ),
        loop_detection=LoopDetectionConfig(
            consecutive_repeat_threshold=4, on_loop_detected="record"
        ),
        scope=ScopeConfig(
            forbidden_tools=["refund", "account_unlock"], max_tool_calls=6, fail_on_violation=True
        ),
        sla=SLAConfig(p95_ms=4000),
        threat_severity=ThreatSeverityConfig(),
        compliance=ComplianceConfig(pii_categories=["email", "phone", "card"]),
        threat_response=ThreatResponseConfig(),
        explainability=ExplainabilityConfig(
            min_reasoning_length=40, require_reasoning=True,
            require_citations=True, citation_markers=["KB-"],
        ),
    )
    def triage(question: str, ground_truth: str = "") -> str:
        p = json.loads(question)
        result = classify_ticket(
            Ticket(p["ticket_id"], p.get("subject", ""), p.get("body", "")), retriever=retriever
        )
        return json.dumps(result.to_dict(), ensure_ascii=False)

    return triage


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(_ROOT / "data" / "golden"))
    ap.add_argument("--note", default="v0 규칙기반 기준선")
    ap.add_argument("--out", default="evaluation")
    ap.add_argument("--judge", action="store_true", help="Gate C LLMJudge 켜기 (S5+)")
    args = ap.parse_args()

    cases = load_golden(Path(args.golden))
    monitor = build_monitor(args.note, enable_judge=args.judge)
    agent = make_agent(monitor)

    for c in cases:
        q = json.dumps(
            {"ticket_id": c["ticket_id"], "subject": c["subject"], "body": c["body"]},
            ensure_ascii=False,
        )
        agent(q, ground_truth=f"{c['gt_category']} {c['gt_priority']}")

    monitor.save_to_file(args.out)
    print(f"wrote results/{args.out}.json  (agent_version={monitor.agent_version}, n={len(cases)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
