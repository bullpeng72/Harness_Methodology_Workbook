# 성숙도 자기평가 — SupportTriage 팀 (2026-08-28, S7)

본편 §33 (5단계). 목표 단계가 아니라 **현재 관행**으로 채점.

## L1 개인 실험 ✅ (넘어섬)
- 한 사람이 도구를 쓰고 눈으로 평가 → 트랙 C(도현)가 여기 머묾.

## L2 반복 가능 ✅ 충족
- [x] 배치 평가 하네스 (`eval/run_batch.py`, S3)
- [x] `agent-eval gate` CI 게이트 (`pr-verify.yml`, S4)
- [x] 골든셋 43건 2인 라벨 + 버전 비교 (`abtest`, S4)
- [x] 커밋된 회귀 기준선 (`results/baselines/current.json`, S6)

## L3 팀 조율 ✅ 충족
- [x] 역할 분리 (PM/개발자 A·B/저자/대조군) — 커밋·태그·관문 로그로 분리 확인
- [x] 클레임 로그 (`.aoo/claims.jsonl`, 유진·민수, S4)
- [x] HITL 관문 2개 (`spec-approved`·`design-approved`), 각 반려 1회 후 승인
- [x] PR 검증 파이프라인 (gate + claims-audit + security-review, S4)
- [ ] `BranchGuardConfig` 서버 강제 — dev 프로파일에만 있음, 서버 required-check 미설정

## L4 거버넌스 🟡 부분
- [x] RCA + 조치 검증 폐루프 — `diagnose`(S5) → 조치(S6) → `verify_recommendation_outcome`
      **confirmed** (C·D 둘 다), `results/recommendation_outcomes.jsonl` 기록 (S7)
- [x] 정직한 한계 문서 (`docs/LIMITS.md`, 5항목 실측 근거)
- [ ] 성숙도 정기 추적 — 이번이 첫 측정, 분기별 계획 필요
- [x] 온보딩 스킬 3종 작성 (`skills/`, Part IX) — `support-triage-labeling` +
      본편 스킬 도메인 래퍼 2개(`requirement-gate-map`·`gate-chapter-loop`).
      정기화·신규 인원 실투입에 따른 리드타임 측정은 미완

## L5 조직 확장 ❌ 미해당
- 팀 하나. 여러 팀 공통 기준은 논의 대상 아님.

## 현재 위치: **L3 완성 / L4 진입 중**

L4를 완성하려면: 성숙도 분기별 추적 + 온보딩 스킬 **정기화**(스킬 3종은 작성됨 — Part IX) + Gate 임계값의 팀 합의(현재 GATE_MAP은 박·유진).
L2가 목표 규모에 맞는 하한 — 이 프로젝트는 L4가 적정.
