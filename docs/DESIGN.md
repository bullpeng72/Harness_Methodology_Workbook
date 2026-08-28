# DESIGN — SupportTriage

작성: 유진 (설계자)  ·  승인: 박 (관문 2, 아래 승인란)
이 문서는 `src/support_triage/`에 실제로 구현된 설계를 기술한다 (서술이 아니라 코드와 1:1).

## 1. 컴포넌트 분해 (GATE_MAP → 아키텍처)

```
Ticket
  └─ sanitize (진입)         ST-006  Gate E
  └─ Classifier               ST-001/002/005  Gate A
       │ confidence < 0.5 → other/P3 조기 종료 (ST-005)
  └─ Reviewer + Aggregator    ST-009  Gate F   (v4)
  └─ Retriever (top_k=4)      ST-004 근거 확보  Gate C/G
  └─ Drafter                  ST-004 근거 기반  Gate C
       │ top passage 유사도 < 0.35 → "근거 없음"
  └─ Escalation Layer         ST-003  Gate E/B   (부작용 없음)
  └─ scrub_pii (출구)         ST-007  Gate E
  └─ TriageResult (JSON, schema_version="1")
```

| 컴포넌트 | 파일 | 책임 SPEC | 비고 |
|---|---|---|---|
| Classifier | `classifier.py` | ST-001/002/005 | v0 규칙, v1+ LLM(Tier 2). confidence 반환 필수 |
| Reviewer/Aggregator | `review.py` | ST-009 | 리뷰어=agree/objection만, 집계자=규칙(재작성 1회, 실패 시 other/P3) |
| Retriever | `retriever.py` | ST-004 | `top_k=4` (S7 RCA에서 5→4로 조정 예정 지점) |
| Drafter | `drafter.py` | ST-004 | passage에 없는 사실 금지, 유사도 < `GROUNDING_THRESHOLD`면 "근거 없음" |
| Escalation Layer | `escalation.py` | ST-003 | `refund()`/`account_unlock()`는 `NotImplementedError` — 호출 대상 아님 |
| sanitize / scrub_pii | `sanitize.py` | ST-006 / ST-007 | 파이프라인 진입·출구 양쪽 |
| 오케스트레이션 | `pipeline.py` | — | 순서 제약: retrieve는 draft보다 앞, classify 저신뢰는 review 건너뜀 |

## 2. 출력 스키마 (IRREVERSIBLE — schema_version)

```json
{"schema_version": "1", "ticket_id": "str",
 "category": "billing|bug|how-to|account|abuse|other",
 "priority": "P1|P2|P3", "confidence": 0.0,
 "draft_reply": "str | '근거 없음'", "reasoning": "str (>=40자, 근거 인용)",
 "kb_citations": ["KB-12"],
 "escalate": {"action": "refund_request|account_unlock", "reason": "str"} | null,
 "error": {"stage": "...", "type": "...", "retries": 1} | null}
```

## 3. Harness Config 켬/끔 (본편 §17.1 — 요구사항이 구동)

### 켠다
| Config | Gate | 파라미터 | 요구사항 |
|---|---|---|---|
| InstructionConfig | A | required_output_keys, fail_on_violation=True | ST-001/002/005 |
| GoalAlignmentConfig | A | **비도구 에이전트라 `use_llm_scoring=True` 병기** (아니면 상수 0.0 — SDK 확인) | ST-001 |
| SubtaskConfig | A | expected_subtasks=[classify, prioritize, draft, escalate_check] | — |
| SLAConfig | D | p95_ms=4000 | ST-100 |
| ThreatSeverityConfig / ComplianceConfig | E | + `enable_pii_redaction` | ST-006/007 |
| ScopeConfig | E,B | forbidden_tools=["refund","account_unlock"] | ST-003 |
| LLMJudge (faithfulness) | C | judge_model=tier1, judge_sample_rate=0.3 | ST-004 |
| ExplainabilityConfig | G | min_reasoning_length=40, require_evidence=True | ST-008 |
| AgentRoleConfig / ConflictResolutionConfig | F | max_resolution_rounds=1, 하네스가 agent_interactions 기록 | ST-009 |

### 끈다 (근거 + 켤 시점)
| Config | 왜 |
|---|---|
| DeadlockConfig | 단일 에이전트(v0~v3), 위임 없음 — v4에서도 리뷰어는 위임 아님 |
| ReproducibilityConfig | S5(Gate C 장)에서 켠다 |
| ContextWindowConfig | 티켓 1건은 짧음 |

## 4. 모델 티어 (본편 원칙 5)

| 작업 | 티어 | 근거 |
|---|---|---|
| SPEC·설계·RCA | T1 | 1회성, 판단 |
| Classifier·Drafter 추론 | T2 | 수십~수백 회 반복 (ST-101) |
| LLMJudge faithfulness 채점 | T1 | 채점은 판정 — T2는 버전 비교를 흔든다 |

## 5. 에러 정책

| 상황 | 동작 |
|---|---|
| LLM 호출 실패 | 최대 1회 재시도 → 실패 시 other/P3 + `error` 필드 |
| KB 검색 0건 / 유사도 미달 | ST-004대로 "근거 없음" (에러 아님) |
| 출력 스키마 검증 실패 | 태스크 실패로 기록(Gate A), 재시도 안 함 |

## 6. NEEDS CLARIFICATION 해소

- ST-004 `GROUNDING_THRESHOLD` = **0.35** (유진 결정, Part VI에서 골든셋으로 재조정) — `types.py` 상수
- ST-009 재작성 라운드 상한 = **1** (민수 검증: 2회 이상은 지연·비용만 늘고 boundary 정확도 개선 미미할 것으로 판단, S5에서 실측)

## 승인 (HITL 관문 2)

- [x] 모든 ST-NNN에 책임 컴포넌트가 정확히 하나
- [x] 켠 Config가 GATE_MAP과 일치, 끈 Config에 근거+시점
- [x] 티어 배정에서 판정 작업이 전부 T1
- [x] 출력 스키마·에러 정책 명시
- [x] 되돌리기 어려운 결정이 ADR로 남음 (ADR-001~004)
- [x] GoalAlignmentConfig 비도구 함정 대응 명시

승인자: 박 (PM) · 2026-08-28 · 상태: **APPROVED** (반려 1회 후 — `docs/gates/gate2-review.md`)
