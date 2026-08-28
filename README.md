# SupportTriage — 《하니스 메서드 실습서》 러닝 예제

지원 티켓을 분류(6종)·우선순위(P1/P2/P3)·답변 초안·에스컬레이션 판정하는 에이전트.
실습서 Part I~X를 거치며 v0(규칙기반) → v4(RAG + 리뷰어/집계자)로 자란다. 이 저장소는
**v4 최종 상태**다.

> 코드 주석·이 문서의 `Ch NN`·`Part N`·`§N.N` 은 모두 이 저장소와 함께 배포되는
> 《하니스 메서드 실습서》의 장·절을 가리킨다(그 책은 이 저장소에 포함돼 있지 않다).
> `docs/SPEC.md`·`docs/DESIGN.md` 등은 실습서 Part II~IV를 따라가며 독자가 만드는
> 이 저장소 자체의 산출물이다.

## 빠른 실행

```bash
# 오프라인 (결정적 스텁 — 네트워크·키 불필요, 파이프라인 검증용)
SUPPORT_TRIAGE_OFFLINE=1 python demo.py

# 실제 모델
export ANTHROPIC_API_KEY=...        # 또는 Ollama 실행 (models.lock 의 tier2)
python demo.py

# 배치 평가 (agent-evaluator 필요)
pip install -e ".[dev]"
python eval/run_batch.py --tickets data/tickets/sample.jsonl
agent-eval gate results/evaluation.json --tcr 85 --accuracy 70
```

> **오프라인 모드 주의**: `SUPPORT_TRIAGE_OFFLINE=1` 은 실제 추론이 아니라 키워드
> 매칭 스텁이다. 파이프라인이 끝까지 도는지 확인하는 용도이며, 분류 정확도·RAG
> 근거·인젝션 방어는 실제 모델에서만 의미가 있다(재현 가능성 계약 §1.2).

## 구조

```
src/support_triage/
  types.py        Ticket · TriageResult · Escalation · 상수 (schema_version, 임계값)
  llm.py          티어 추상화 (Anthropic / Ollama / 오프라인 스텁)
  sanitize.py     입력 인젝션 중화 (ST-006) · 출력 PII 스크럽 (ST-007)
  classifier.py   카테고리·우선순위·confidence (ST-001/002/005)
  retriever.py    KB top-k 검색 (ST-004 근거 확보)
  drafter.py      근거 기반 초안, 근거 없으면 "근거 없음" (ST-004)
  escalation.py   부작용 없는 에스컬레이션 판정 (ST-003) — refund/account_unlock 은 미구현
  review.py       v4 리뷰어 + 규칙 기반 집계자 (Gate F)
  pipeline.py     classify_ticket() — 전체 오케스트레이션
eval/run_batch.py  @agent_eval 배치 하네스 (Ch 13 에서 정한 Config 만 연결)
.claude/.agent-evaluator/guardrail_config.json   실시간 LiveGuardrail 설정 (Ch 19/34)
models.lock        모델 핀 (재현 계약)
```

## 요구사항 매핑 (docs/SPEC.md · docs/GATE_MAP.md)

| ID | 요구사항 | 구현 | Gate |
|---|---|---|---|
| ST-001/002 | 카테고리 6종·우선순위 1개 | `classifier.classify` | A |
| ST-003 | 환불·계정변경은 실행 금지, 에스컬레이션 | `escalation.check_escalation` (+ `refund` 는 `NotImplementedError`) | E, B |
| ST-004 | 근거 없으면 "근거 없음" | `drafter.draft_reply` (`GROUNDING_THRESHOLD`) | C |
| ST-005 | confidence < 0.5 → other/P3 | `classifier.classify` | A |
| ST-006 | 티켓 지시 무시 | `sanitize.sanitize_ticket_text` + sandwich 프롬프트 | E |
| ST-007 | 타 고객 PII 미포함 | `sanitize.scrub_pii` (drafter 출력 + 파이프라인 출구 이중) | E |
| ST-100 | p95 <= 4000ms | `eval/run_batch.py` `SLAConfig` | D |
