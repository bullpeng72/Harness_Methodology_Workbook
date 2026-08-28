"""결과 JSON → self-contained HTML 리포트 (Agent-Evaluator).

    python eval/make_report.py results/evaluation.json [--baseline results/baselines/current.json]
    python eval/make_report.py --final          # results/final/v0..v3.json → v*.html (직전 버전 기준선)

워크북 Ch 17·22·39 / 부록 A·C·I 참조.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_evaluator.reporting.comprehensive_report import generate_html_from_result_file
from agent_evaluator.serve.loader import parse_file

_PREV = {"v0": None, "v1": "v0", "v2": "v1", "v3": "v2"}


def _one(src: Path, baseline_path: Path | None) -> Path:
    rf = parse_file(src)
    baseline = None
    if baseline_path and baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    out = src.with_suffix(".html")
    out.write_text(generate_html_from_result_file(rf, baseline=baseline), encoding="utf-8")
    tag = f"(baseline={baseline_path})" if baseline else "(no baseline)"
    print(f"wrote {out}  {tag}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", nargs="?", help="결과 JSON 경로")
    ap.add_argument("--baseline", type=Path, default=None)
    ap.add_argument("--final", action="store_true", help="results/final/v*.json 일괄")
    args = ap.parse_args()

    if args.final:
        base = Path("results/final")
        for v, prev in _PREV.items():
            src = base / f"{v}.json"
            if not src.exists():
                continue
            bp = base / f"{prev}.json" if prev else None
            _one(src, bp)
        return 0

    if not args.result:
        ap.error("result 경로가 필요하다 (또는 --final)")
    _one(Path(args.result), args.baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
