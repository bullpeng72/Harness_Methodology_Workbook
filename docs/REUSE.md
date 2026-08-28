# REUSE — 새로 만들지 않고 재사용하는 것

작성: 유진·민수.  본편 원칙 4 — 검색하지 않은 확신은 기술부채.

검색한 곳: `agent_evaluator` 설치본(`pip show agent-evaluator` → 소스), 팀 스킬 디렉토리(없음 — 신규 프로젝트), `search_violations`(이력 없음 — 신규).

| 필요한 것 | 새로 만들지 않고 | 근거 |
|---|---|---|
| 분류 정확도 채점 | `AccuracyEvaluator` (task_type 기반) | SDK 내장, 골든셋만 주면 됨 |
| 답변 충실도 채점 | `LLMJudge`(faithfulness) | SDK 내장 |
| SLA 판정 | `SLAConfig(p95_ms=...)` | Gate D 표준 |
| 인젝션 / PII | `InputSanitizationTracker` / `OutputLeakageDetector` + `enable_pii_redaction` | Gate E 표준 보안 트래커 |
| 배치 리포트·게이트 | `PerformanceMonitor` + `agent-eval gate` | 두 폐루프의 배치 쪽 |
| 실시간 위험 차단 | `LiveGuardrail` (runtime 프로파일) | 두 폐루프의 실시간 쪽 |
| 버전 비교 | `agent-eval abtest` / `--baseline-version` / `trend` | SDK CLI |
| RCA | `agent-eval diagnose` / `verify_recommendation_outcome` | SDK `rca/` |
| 멀티에이전트 조율 채점 | `AgentRoleConfig` / `ConsensusConfig` / `ConflictResolutionConfig` | Gate F 표준 |

## 새로 만드는 것 (최소)

- `src/support_triage/**` — 도메인 로직 (분류·검색·초안·에스컬레이션·리뷰)
- `eval/run_batch.py` — 위 SDK 요소에 SupportTriage를 연결하는 `@agent_eval` 계층
- `data/golden/**` — 골든셋 (2인 라벨)
- `data/adversarial/**` — 인젝션·PII 셋
- `skills/**` — 반복 절차 3개 (Part IX)

## 안 만들기로 한 것

- 분류 정확도 계산 함수 → `AccuracyEvaluator` 존재
- "가중치 합이 1인지" 류 검증 → 어느 SPEC 항목과도 연결 안 됨 (근거 없는 가정)
