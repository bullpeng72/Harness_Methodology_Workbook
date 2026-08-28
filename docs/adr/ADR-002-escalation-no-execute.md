# ADR-002 — 에스컬레이션은 판정만, 실행하지 않는다

## 맥락
ST-003: 환불·계정 잠금 해제는 사람 승인이 필요하다. 되돌리기 비용 = 실제 금전·계정 피해.

## 결정
Escalation Layer는 **부작용 없는 순수 판정 함수**다. `escalate` 필드만 채운다.
`escalation.py`의 `refund()`·`account_unlock()`는 존재하되 호출되면 `NotImplementedError`.
배치 `ScopeConfig(forbidden_tools=[...])` + runtime `guardrail_profiles/runtime.json`이 이중으로
그 도구 호출을 막는다.

## 결과
- 에이전트가 구조적으로 그 액션을 실행할 수 없음 (방어 by construction)
- Gate E/B는 "금지 도구 호출 0건"을 확인 — 회귀(누가 실수로 `refund()` 배선) 시 CI가 잡음
- `IRREVERSIBLE.md` 등재

## 대안과 기각
- "승인되면 자동 실행": 승인 채널·롤백까지 이 프로젝트 범위를 넘음. 사람 큐로 넘기는 게 맞음
