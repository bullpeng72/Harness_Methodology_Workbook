"""도구 체인·모델 핀·데이터 재현 상태 점검 (실습서 Ch 3).

`just doctor` 가 이 스크립트를 부른다. 각 줄이 하나의 재현 전제이고, 하나라도
FAIL 이면 이후 장에서 책과 다른 수치를 보게 된다. tier2(Ollama)는 Part VI 전까지
`[SKIP]` 이어도 정상.

실행::

    python eval/doctor.py        # 또는 `just doctor`
    echo $?                      # FAIL 있으면 1
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

_OK, _FAIL, _SKIP = "OK", "FAIL", "SKIP"
_rows: list[tuple[str, str, str]] = []


def _add(label: str, status: str, detail: str = "") -> None:
    _rows.append((label, status, detail))


def _py() -> None:
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 10)
    _add(f"Python {v.major}.{v.minor}.{v.micro}", _OK if ok else _FAIL,
         "" if ok else "need >= 3.10")


def _just() -> None:
    p = shutil.which("just")
    _add("just", _OK if p else _FAIL, p or "not on PATH — `brew install just`")


def _agent_eval() -> None:
    try:
        import agent_evaluator
        _add(f"agent-eval {agent_evaluator.__version__}", _OK)
    except Exception as e:  # noqa: BLE001
        _add("agent-eval", _FAIL, f"import failed: {e}")


def _hooks() -> None:
    for base in (_ROOT / ".claude", Path.home() / ".claude"):
        sf = base / "settings.json"
        if not sf.is_file():
            continue
        try:
            hooks = json.loads(sf.read_text(encoding="utf-8")).get("hooks", {})
        except Exception:  # noqa: BLE001
            _add("Claude Code hooks", _FAIL, f"{sf} unparseable")
            return
        have = {k for k in ("PreToolUse", "PostToolUse", "SessionEnd") if k in hooks}
        if have == {"PreToolUse", "PostToolUse", "SessionEnd"}:
            _add("Claude Code hooks (Pre/Post/SessionEnd)", _OK, str(sf))
        else:
            _add("Claude Code hooks", _FAIL, f"{sf}: missing {set(('PreToolUse','PostToolUse','SessionEnd')) - have}")
        return
    _add("Claude Code hooks", _SKIP, "run `agent-eval claude install` (per-machine)")


def _guardrail() -> None:
    gc = _ROOT / ".claude" / ".agent-evaluator" / "guardrail_config.json"
    if not gc.is_file():
        _add("guardrail_config.json", _FAIL, "missing — `git checkout s0-setup -- .claude/`")
        return
    try:
        cfg = json.loads(gc.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        _add("guardrail_config.json", _FAIL, f"unparseable: {e}")
        return
    prof = str(cfg.get("_profile", "")).split(" ")[0] or "?"
    _add(f"guardrail_config.json (profile={prof})", _OK)


def _models_lock() -> None:
    ml = _ROOT / "models.lock"
    if not ml.is_file():
        _add("models.lock", _FAIL, "missing")
        return
    pins = {}
    for line in ml.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and ":" in line:
            k, _, v = line.partition(":")
            pins[k.strip()] = v.strip()
    _add("models.lock", _OK, f"tier1={pins.get('tier1', '?')} tier2={pins.get('tier2', '?')}")
    # tier1 key
    if os.getenv("ANTHROPIC_API_KEY"):
        _add("  tier1 (Claude) — API key", _OK)
    else:
        _add("  tier1 (Claude) — API key", _SKIP, "ANTHROPIC_API_KEY unset — needed from Part IV")
    # tier2 ollama model
    tier2 = pins.get("tier2", "")
    try:
        out = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        base = tier2.split(":")[0]
        if base and base in out.stdout:
            _add("  tier2 (Ollama) — model pulled", _OK, tier2)
        else:
            _add("  tier2 (Ollama) — model pulled", _SKIP, f"`ollama pull {tier2}` — needed from Part VI")
    except Exception:  # noqa: BLE001
        _add("  tier2 (Ollama)", _SKIP, "ollama not installed — needed from Part VI")


def _data() -> None:
    d = _ROOT / "data"
    def _count_jsonl(p: Path) -> int:
        return sum(1 for _ in p.open(encoding="utf-8")) if p.is_file() else 0
    def _golden(name: str) -> int:
        p = d / "golden" / name
        return len(json.loads(p.read_text(encoding="utf-8")).get("cases", [])) if p.is_file() else 0
    core = _golden("golden_core.json")
    bnd = _golden("golden_boundary.json")
    prio = _golden("golden_priority.json")
    inj = _count_jsonl(d / "adversarial" / "injection.jsonl")
    pii = _count_jsonl(d / "adversarial" / "pii.jsonl")
    kb = len(list((d / "kb").glob("KB-*.md")))
    tickets = _count_jsonl(d / "tickets" / "sample.jsonl")
    ok = core and bnd and prio and inj and pii and kb
    _add("data/  golden=%d(%d+%d+%d)  adv=%d(%d+%d)  kb=%d  tickets=%d"
         % (core + bnd + prio, core, bnd, prio, inj + pii, inj, pii, kb, tickets),
         _OK if ok else _FAIL)


def _results_writable() -> None:
    r = _ROOT / "results"
    try:
        r.mkdir(exist_ok=True)
        t = r / ".doctor_write_test"
        t.write_text("ok", encoding="utf-8")
        t.unlink()
        _add("results/ writable", _OK)
    except Exception as e:  # noqa: BLE001
        _add("results/ writable", _FAIL, str(e))


def main() -> int:
    for chk in (_py, _just, _agent_eval, _hooks, _guardrail, _models_lock, _data, _results_writable):
        chk()
    width = max(len(r[0]) for r in _rows)
    n_ok = n_fail = n_skip = 0
    for label, status, detail in _rows:
        n_ok += status == _OK
        n_fail += status == _FAIL
        n_skip += status == _SKIP
        line = f"[doctor] {label.ljust(width)}  {status}"
        if detail:
            line += f"  ({detail})"
        print(line)
    print(f"\ndoctor: {len(_rows)} checks, {n_ok} OK, {n_skip} SKIP, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
