"""Retriever — 지식베이스 top-k 검색 (ST-004 근거 확보).

Ch 28: 임베딩은 빌드 타임에 계산해 ``data/kb/index.json`` 에 저장하고, 요청 시엔
쿼리만 임베딩한다. 임베딩 모델이 없으면 결정적 토큰 자카드 유사도로 폴백한다
(오프라인 재현 경로).
"""
from __future__ import annotations

import json
import math
import os
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

_KB_DIR = Path(__file__).resolve().parents[2] / "data" / "kb"
_INDEX = _KB_DIR / "index.json"
_TOP_K = 4  # Ch 39 RCA 이후 5 → 4
_LOCK = Path(__file__).resolve().parents[2] / "models.lock"


def _embed_model() -> str:
    if _LOCK.exists():
        for line in _LOCK.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("embed:"):
                return line.split(":", 1)[1].strip()
    return ""


def _embed(text: str) -> list[float] | None:
    """쿼리 임베딩 (Ollama). 실패하면 None → shingle 폴백."""
    model = _embed_model()
    if not model or os.getenv("SUPPORT_TRIAGE_OFFLINE") == "1":
        return None
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        req = urllib.request.Request(
            f"{host}/api/embeddings",
            data=json.dumps({"model": model, "prompt": text}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:  # noqa: S310 — 로컬
            return json.loads(r.read()).get("embedding")
    except Exception:  # noqa: BLE001
        return None


def _cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


@dataclass(frozen=True)
class Passage:
    kb_id: str
    title: str
    text: str
    score: float


def _shingles(text: str) -> set[str]:
    """정규화 문자열의 2-gram 집합.

    한국어는 조사가 붙어 단어 경계가 흔들리므로(예: "결제가" vs "결제는"),
    임베딩 모델이 없는 오프라인 폴백에서는 단어 토큰 대신 문자 2-gram 으로
    유사도를 잰다.
    """
    norm = re.sub(r"[^0-9a-z가-힣]+", "", text.lower())
    return {norm[i : i + 2] for i in range(len(norm) - 1)} if len(norm) >= 2 else set()


def _coverage(query: set[str], doc: set[str]) -> float:
    """쿼리 shingle 이 문서에 얼마나 덮이는지 (retrieval recall 근사).

    자카드 대신 비대칭 커버리지를 쓴다 — 긴 KB 문서가 길이 때문에 불이익을
    받지 않도록.
    """
    if not query:
        return 0.0
    return len(query & doc) / len(query)


class Retriever:
    """KB 문서를 로드해 쿼리에 대한 상위 passage 를 반환한다.

    Example::

        r = Retriever()
        hits = r.search("결제가 두 번 청구됐어요")
    """

    def __init__(self, top_k: int = _TOP_K) -> None:
        self.top_k = top_k
        self._docs: list[dict[str, str]] = self._load()

    def _load(self) -> list[dict[str, str]]:
        if _INDEX.exists():
            return json.loads(_INDEX.read_text(encoding="utf-8"))
        docs: list[dict[str, str]] = []
        for md in sorted(_KB_DIR.glob("*.md")):
            head, _, body = md.read_text(encoding="utf-8").partition("\n")
            docs.append({"kb_id": md.stem, "title": head.lstrip("# ").strip(), "text": body.strip()})
        return docs

    def search(self, query: str) -> list[Passage]:
        """상위 ``top_k`` passage 를 유사도 내림차순으로 반환한다.

        Note:
            점수는 0~1 정규화된 근사값이다. 호출자(Drafter)는
            ``types.GROUNDING_THRESHOLD`` 와 비교해 "근거 없음" 여부를 판정한다.
        """
        # 1순위: 임베딩 (index.json 에 embedding 필드가 있고 쿼리 임베딩 성공 시)
        if self._docs and "embedding" in self._docs[0]:
            qv = _embed(query)
            if qv is not None:
                scored = [
                    Passage(d["kb_id"], d["title"], d["text"], round(_cos(qv, d["embedding"]), 4))
                    for d in self._docs
                ]
                scored.sort(key=lambda p: p.score, reverse=True)
                return scored[: self.top_k]

        # 폴백: 문자 2-gram 커버리지 (오프라인 재현 경로)
        q = _shingles(query)
        scored = []
        for d in self._docs:
            doc_sh = _shingles(d["title"] + " " + d["text"])
            title_sh = _shingles(d["title"])
            score = max(_coverage(q, doc_sh), _coverage(title_sh, q))
            scored.append(Passage(d["kb_id"], d["title"], d["text"], round(score, 4)))
        scored.sort(key=lambda p: p.score, reverse=True)
        return scored[: self.top_k]
