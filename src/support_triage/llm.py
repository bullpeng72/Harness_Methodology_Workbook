"""모델 티어 추상화 (docs/DESIGN.md 모델 티어 / 실습서 Ch 14).

- Tier 1: 분석·설계·판정 — Anthropic API (LLMJudge 채점 등, 하네스 쪽에서 사용).
- Tier 2: 반복 실행 — Ollama 로컬. 미설치 시 ``tier2_fallback`` (Tier 1) 또는
  오프라인 결정적 스텁으로 폴백한다(``models.lock`` 의 정책).

이 모듈은 프롬프트를 던지고 문자열을 받는 최소 인터페이스만 노출한다. 재현
가능성을 위해 ``temperature`` 기본값은 0.0, 시드는 ``models.lock`` 을 따른다.
"""
from __future__ import annotations

import json
import os
import urllib.request
from contextlib import suppress
from pathlib import Path
from typing import Any

_MODELS_LOCK = Path(__file__).resolve().parents[2] / "models.lock"


def _load_lock() -> dict[str, str]:
    """``models.lock`` (``key: value`` 줄) 을 읽는다. 없으면 빈 dict."""
    if not _MODELS_LOCK.exists():
        return {}
    out: dict[str, str] = {}
    for line in _MODELS_LOCK.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


class LLM:
    """티어 1개에 대한 호출기.

    Args:
        tier: ``"tier1"`` 또는 ``"tier2"``.
        temperature: 샘플링 온도. 재현을 위해 기본 0.0.

    Example::

        clf = LLM("tier2")
        raw = clf.complete(system="너는 분류기다", user="티켓: ...")
    """

    def __init__(self, tier: str = "tier2", temperature: float = 0.0) -> None:
        if tier not in ("tier1", "tier2"):
            raise ValueError(f"tier must be tier1|tier2, got {tier!r}")
        self.tier = tier
        self.temperature = temperature
        lock = _load_lock()
        self.model = lock.get(tier, "")
        self.fallback_model = lock.get("tier2_fallback", lock.get("tier1", ""))
        self.seed = int(lock.get("seed", "7"))
        # 오프라인 모드: 네트워크·키가 전혀 없을 때 결정적 스텁을 쓴다(실습서 Ch 1 "재현 가능성 계약").
        self.offline = os.getenv("SUPPORT_TRIAGE_OFFLINE") == "1"

    # ------------------------------------------------------------------ public
    def complete(self, system: str, user: str, max_tokens: int = 800) -> str:
        """system/user 프롬프트로 1턴 응답을 받는다.

        경로 우선순위: 오프라인 스텁 → Ollama(tier2) → Anthropic(tier1 또는 폴백).
        어느 경로도 불가하면 ``RuntimeError``.
        """
        if self.offline:
            return _offline_stub(system, user)

        if self.tier == "tier2" and self.model:
            # Ollama 실패 시 조용히 아래 Anthropic/폴백 경로로 넘어간다.
            with suppress(Exception):
                return self._ollama(system, user, max_tokens)

        model = self.model if self.tier == "tier1" else self.fallback_model
        if model and os.getenv("ANTHROPIC_API_KEY"):
            return self._anthropic(model, system, user, max_tokens)

        raise RuntimeError(
            "no LLM backend available: set ANTHROPIC_API_KEY, run Ollama, "
            "or export SUPPORT_TRIAGE_OFFLINE=1"
        )

    # ----------------------------------------------------------------- private
    def _ollama(self, system: str, user: str, max_tokens: int) -> str:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        payload = {
            "model": self.model,
            "system": system,
            "prompt": user,
            "stream": False,
            "options": {"temperature": self.temperature, "seed": self.seed, "num_predict": max_tokens},
        }
        req = urllib.request.Request(
            f"{host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body: dict[str, Any] = json.loads(resp.read())
        return str(body.get("response", "")).strip()

    def _anthropic(self, model: str, system: str, user: str, max_tokens: int) -> str:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pip install anthropic") from exc
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in msg.content if block.type == "text").strip()


def _offline_stub(system: str, user: str) -> str:
    """네트워크·키 없이 도는 결정적 스텁.

    실제 추론이 아니라, 파이프라인·평가 하네스가 오프라인에서도 끝까지 도는지
    확인하는 용도다(실습서 Ch 1 "재현 가능성 계약" — 오프라인 경로에서는 수치가 책과 다르다).
    프롬프트 안의 힌트 토큰을 보고 그럴듯한 JSON/텍스트를 만든다.
    """
    text = user.lower()
    if '"category"' in system or "분류기" in system:
        cat = "other"
        for key, label in (
            ("환불", "billing"), ("refund", "billing"), ("청구", "billing"), ("결제", "billing"),
            ("버그", "bug"), ("오류", "bug"), ("안 돼", "bug"),
            ("로그인", "account"), ("계정", "account"),
            ("어떻게", "how-to"), ("방법", "how-to"),
            ("무시하고", "abuse"), ("system:", "abuse"),
        ):
            if key in text:
                cat = label
                break
        prio = "P1" if any(k in text for k in ("결제 실패", "중단", "보안", "긴급")) else "P2"
        if cat in ("how-to", "other"):
            prio = "P3"
        return json.dumps(
            {"category": cat, "priority": prio, "confidence": 0.72,
             "reasoning": f"offline stub: matched category={cat}"},
            ensure_ascii=False,
        )
    # escalation intent
    if "refund_request" in system:
        if any(k in text for k in ("환불", "refund", "결제 취소", "중복 청구", "중복청구")):
            return json.dumps(
                {"action": "refund_request", "reason": "offline stub: 환불 요청 감지"},
                ensure_ascii=False,
            )
        if any(k in text for k in ("잠긴", "잠금 해제", "unlock", "계정 풀")):
            return json.dumps(
                {"action": "account_unlock", "reason": "offline stub: 계정 잠금 해제 요청 감지"},
                ensure_ascii=False,
            )
        return json.dumps({"action": "none", "reason": ""}, ensure_ascii=False)
    # reviewer
    if "리뷰어" in system or "reviewer" in system.lower():
        return json.dumps({"agree": True, "objection": None}, ensure_ascii=False)
    # drafter
    return "확인 결과를 안내드립니다. 자세한 절차는 아래 근거 문서를 참고해 주세요. [KB-12]"
