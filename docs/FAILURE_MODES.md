# FAILURE MODES — SupportTriage

작성: 유진·민수 (S2 분석).  각 행은 `SPEC.md`의 `ST-NNN` 하나를 뒤집어 파생한다 —
어느 SPEC과도 연결 안 되는 행이 있으면 근거 없이 상상한 것이다(본편 §15.2).

| # | 실패 모드 | 파생 SPEC | 사용자 영향 | 예상 빈도 | 골든셋 반영 |
|---|---|---|---|---|---|
| F1 | billing 티켓을 account로 오분류 | ST-001 | 중 — 잘못된 팀으로 라우팅 | 높음 | golden_core (billing 3건) |
| F2 | 우선순위를 규칙과 다르게 매김 (결제 실패인데 P2) | ST-002 | 중 — 대응 지연 | 높음 | golden_priority |
| F3 | 근거 없는데 그럴듯한 답변을 지어냄 | ST-004 | 높 — 고객이 틀린 정보 받음 | 중간 | golden_core (KB 없는 케이스) |
| F4 | 티켓 본문의 "이전 지시 무시하고…"를 따름 | ST-006 | 높 — 인젝션 성공 | 낮음 | adversarial/injection |
| F5 | 답변 초안에 KB passage의 예시 이메일을 그대로 복사 | ST-007 | 높 — PII 유출 | 낮음 | adversarial/pii |
| F6 | 환불 요청에 escalate 없이 "환불 처리했습니다" 응답 | ST-003 | 높 — 잘못된 기대 + 실행 위험 | 중간 | golden_core (refund 케이스) |
| F7 | 신뢰도 낮은데 other/P3로 안 보내고 억지 분류 | ST-005 | 중 | 중간 | golden_boundary |
| F8 | 분류 근거(reasoning)가 20자 미만이거나 비어 있음 | ST-008 | 중 — 상담원이 검토 불가 | 중간 | (전 케이스 공통 체크) |
| F9 | 리뷰어가 동의/반대 대신 답변을 통째로 다시 씀 (역할 이탈) | ST-009 | 중 — 조율 실패, 재작성 루프 | 중간 | golden_boundary (v4 채점) |
| F10 | how-to 티켓을 bug로 (또는 반대로) 오분류 | ST-001 | 낮 — 경계 케이스 | 높음(12% 관측 예상) | golden_boundary |

## 관측 근거 (샘플 100건 검토 — 유진·민수 각자)

- billing ↔ account 겹침: 결제수단 변경 문의가 대표. → GATE_MAP 규칙 "결제 관련이면 billing 우선"
- how-to ↔ bug 모호: 약 12%. → golden_boundary로 별도 측정
- P1 비율: 약 8% (실분포). 골든셋은 측정을 위해 P1/P2/P3 균형을 맞추고, 실분포는 별도 기록
- 인젝션 의심 티켓 2건 발견 → adversarial/injection.jsonl 시드
