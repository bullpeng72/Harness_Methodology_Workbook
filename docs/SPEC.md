# SPEC — SupportTriage

작성: 유진·민수  ·  승인: 박 (관문 1, 아래 승인란)
표기: EARS (The system shall / When … / While … / If … then …)

## 구조 요구사항

- 모듈: `src/support_triage/`
- 진입점: `classify_ticket(ticket: Ticket) -> TriageResult`
- 출력: 고정 JSON 스키마(자유 텍스트 아님). `schema_version` 필드 포함.

## 기능 요구사항

- **ST-001** — The system shall return exactly one category from
  `{billing, bug, how-to, account, abuse, other}` for every ticket.
- **ST-002** — The system shall return exactly one priority from `{P1, P2, P3}`,
  using the rule: 결제 실패·서비스 중단·보안 = P1 / 기능 오류·계정 접근 문제 = P2 /
  사용법 문의·기타 = P3. (관문 1에서 박·유진 확정 — PROBLEM "아직 모르는 것" 해소.)
- **ST-003** — When the ticket text requests a refund or account unlock, the system
  shall set `escalate` with an action and reason and shall NOT execute the action.
- **ST-004** — While no knowledge-base passage supports an answer (top passage
  similarity < GROUNDING_THRESHOLD), the system shall set `draft_reply` to "근거 없음".
- **ST-005** — If classification confidence < 0.5, then the system shall return
  category `other` with priority `P3`.
- **ST-006** — The system shall ignore any instruction contained in the ticket body
  (treat ticket text as data, not commands).
- **ST-007** — The system shall NOT include PII (email/phone/card) belonging to a
  different customer in `draft_reply`.
- **ST-008** — The system shall include a human-readable `reasoning` string of at
  least 40 characters citing the basis of the classification.
  *(Gate G를 구동하기 위해 추가 — 본편 §17.1: 요구사항 없는 Gate는 채점하지 않는다.)*
- **ST-009** — When a reviewer agent is present, the reviewer shall return only an
  agree/objection verdict (no rewritten answer), and the aggregator shall resolve
  disagreement within at most 1 rewrite round, falling back to `other`/`P3`.
  *(Gate F를 구동하기 위해 추가.)*

## 비기능 요구사항

- **ST-100** — The system shall keep per-ticket p95 latency <= 4000 ms.
- **ST-101** — Iteration cost shall not scale with Tier 1 API pricing
  (Classifier/Drafter run on Tier 2).

## NEEDS CLARIFICATION (관문 1 시점 잔여)

- **ST-004 GROUNDING_THRESHOLD 초기값** → DESIGN(관문 2)에서 유진이 0.35로 두고
  Part VI에서 골든셋으로 조정. (담당·시점 명시됨 → 관문 1 통과 가능.)
- **ST-009 재작성 라운드 상한이 1이 맞는가** → DESIGN에서 민수가 검증.

## 승인 (HITL 관문 1)

- [x] 모든 ST-NNN이 EARS 4패턴 중 하나
- [x] 부정형 요구사항 3개 이상 (ST-003·006·007)
- [x] 비기능 요구사항에 숫자·단위 (ST-100·101)
- [x] `docs/GATE_MAP.md`의 모든 요구사항에 Gate·정량 기준
- [x] Gate A–G 각각을 구동하는 요구사항이 최소 1개씩 존재 (F=ST-009, G=ST-008)
- [x] 남은 `[NEEDS CLARIFICATION]`에 담당·시점 명시
- [x] `docs/IRREVERSIBLE.md`에 되돌리기 비싼 결정 등재

승인자: 박 (PM) · 2026-08-28 · 상태: **APPROVED** (반려 1회 후 재승인 — `docs/gates/gate1-review.md` 참고)
