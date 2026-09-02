# SKILL CANDIDATES — SupportTriage

작성: 유진·민수 (Part IX)  ·  방향: **본편 14개 스킬과 먼저 대조**한 뒤, 도메인 고유의 반복만 새로 만든다 (본편 원칙 4).

## 1. 본편 스킬 라이브러리(부록 B.2, 14개)와 대조

Part I~VIII에서 3회 이상 반복된 절차 → 본편 스킬로 커버되는지 확인.

| 이 프로젝트가 반복한 절차 | 밟은 장 | 본편 스킬로 커버되나 |
|---|---|---|
| SPEC·실패모드·골든셋·세션목표 템플릿 채우기 | Ch 6, 9, 11 | ✅ `spec-driven-artifacts` — 그대로 재사용 |
| 요구사항 → Gate 매핑표 | Ch 7 | ✅ `spec-driven-artifacts`의 "3) Gate 매핑 초안" 절 |
| HITL 승인/재수정 루프 (SPEC·DESIGN 승인) | Ch 8, 15 | ✅ `human-approval-loop` |
| 설계 결정을 ADR로 | Ch 15 | ✅ `adr-template` |
| LiveGuardrail 표준 설정 + SPEC-041 안전장치 | Ch 2, 19 | ✅ `liveguardrail-standard-config` |
| TDD-AI red-green-refactor 순환 | Ch 16, 21, 24 | ✅ `tdd-ai-workflow-checklist` |
| 한 Gate를 목표선까지 올리는 성분 분해 루프 | Ch 25–31 (7회) | ✅ `gate-improvement-loop` — 도메인 무관 절차. 이 프로젝트는 **적용**할 뿐 |
| 버전 비교 → 채택 의사결정 (주 지표 사전등록) | Ch 22 | ✅ `abtest-decision-workflow` |
| `agent-eval gate` 종료 코드(1/2/3/4)를 CI 스텝으로 | Ch 23, 35 | ✅ `harness-gate-ci` |
| 클레임 감사를 CI에 | Ch 33, 35 | ✅ `claims-audit-ci` |
| Gate 하락 → recommend_fix → 적용 → 검증 | Ch 39, 40 | ✅ `recommend-fix-workflow` |
| PR 리뷰 체크 / 커밋·PR 메시지 | Ch 35 | ✅ `code-review-checklist` · `commit-pr-message-rules` |
| 배포 후 인시던트 회고 | Ch 42 (롤백 절차) | ✅ `incident-postmortem` |

## 2. 남는 것 — 본편 14개로 커버 안 되는, 도메인 고유의 반복만

### 도메인 지식 (domain)
- **D1**: SupportTriage 티켓 라벨링 규칙 (카테고리 우선순위, P1/P2/P3 기준, how-to vs bug) — Ch 20에서 6회+
- **D2**: 인젝션 중화 패턴 (Ch 29의 sandwich + 마스킹) — Ch 29 *(현재는 `src/support_triage/sanitize.py`에 코드로만. 스킬화는 반복 3회 관측 후)*

### 절차/범용 — 본편 스킬의 "도메인 특화" 얇은 래퍼가 필요한 경우만
- **P1'**: `gate-chapter-loop` — 본편 `gate-improvement-loop`을 SupportTriage 7개 Gate·golden 셋 이름에 맞춰 얇게 감싼 것 (본편 절차를 대체하지 않고, "이 프로젝트에서 어느 파일·어느 golden 셋을 보는지"만 채운다)
- **M1'**: `requirement-gate-map` — 본편 `spec-driven-artifacts`의 Gate 매핑 절만 떼어내 EARS 요구사항 형식에 특화

## 3. 만들지 않는 것

| 후보 | 처리 | 이유 |
|---|---|---|
| M2 HITL 체크리스트 | 만들지 않음 | 본편 `human-approval-loop`에 이미 있음 |
| M3 골든셋 2인 라벨링 | 만들지 않음 | D1(라벨링 규칙 스킬)에 절차가 포함 |

## 4. 세 갈래 결론

| 후보 | 처리 |
|---|---|
| SPEC·HITL·ADR·가드레일·TDD-AI·abtest·CI·RCA 절차 | 본편 스킬 그대로 재사용 |
| `gate-chapter-loop` / `requirement-gate-map` | 본편 스킬의 얇은 도메인 래퍼 (`> 절차 정본:` 줄로 명시) |
| `support-triage-labeling` (D1) | 새 도메인 스킬 (`skills/support-triage-labeling/`) |
| M2 / M3 | 만들지 않음 |

**실제로 만든 것**: `skills/support-triage-labeling`, `skills/requirement-gate-map`, `skills/gate-chapter-loop` (Ch 37).
