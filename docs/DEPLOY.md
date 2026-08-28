# 배포 체크리스트 — SupportTriage v3

승인: 박 (PM) + (프로덕션 배포는 IRREVERSIBLE 최상위 — 지원팀 리드·보안 사전 승인 필요)

## 배포 판정 (S7)

v3는 **제한 릴리스(limited release)** 대상이다 — 절대 게이트 전부 통과는 아니지만, 문서화된
한계 위에서 배포 가치가 있다.

| Gate | 상태 | 배포 영향 |
|---|---|---|
| A 0.60 warn / TCR 50% | ⚠ `LIMITS.md` L2 | category 정확도 ~85%는 상담원 1차 검토 전제로 수용. priority는 규칙 강화 필요(S-later) |
| B 1.0 · E 1.0 | ✅ | 위험 행동·인젝션·PII 통과 |
| C 0.757 | ✅ pass | 근거 없으면 "근거 없음", degradation 0.78 |
| D 0.57 warn / p95 3.02s | ⚠ `LIMITS.md` L1 | SLA(4000ms) 통과. raw efficiency는 로컬 모델 하한 — 프로덕션은 빠른 추론 |
| F n/a | ⚠ `LIMITS.md` L4 | 리뷰어 계측 미배선 — v3는 confidence<0.80일 때만 리뷰어 |
| G 1.0 | ✅ | reasoning + KB 인용 |

## 배포 전 (실데이터 전환)

- [ ] 실제 티켓 200건으로 골든셋 재라벨 (2인, S2 절차) — 합성 43건은 스타터
- [ ] 실분포 측정 → SLA·비용 계산에 반영 (P1 ~8% 관측)
- [ ] 실제 KB로 임베딩 인덱스 재빌드, `GROUNDING_THRESHOLD` 재조정
- [ ] adversarial 셋에 실제 인젝션 로그 추가
- [ ] Gate E를 실데이터로 재검증 (PII 패턴이 합성보다 다양)
- [ ] `models.lock` 프로덕션 값 확정 (tier2 = 프로덕션 서빙 모델)

## 롤백 계획

- 배포 단위: `git tag prod-YYYYMMDD`
- 롤백 트리거:
  - `pr-verify` 게이트 FAIL (자동)
  - 상담원 수정률 > 40% (초안을 40% 넘게 고치면 무용)
  - 인젝션/PII 사고 1건 (즉시)
- 롤백 방법: 이전 `prod-*` 태그로 배포. 또는 **"전부 escalate" 모드**로 폴백
  (에이전트를 끄지 않고 모든 티켓을 사람 큐로 — `escalate` 필드가 이 안전장치)
- 롤백 후: `agent-eval diagnose` (S5) → `verify_recommendation_outcome` (S7) → 재배포

## 운영 관측 (`agent-eval monitor`)

| 신호 | 알림 임계값 |
|---|---|
| 분류 confidence 평균 이동 | -0.1 이상 하락 |
| "근거 없음" 반환율 | > 30% (KB 커버리지 문제) |
| escalate 비율 급증 | 분류 신뢰도 저하 or 인젝션 파상 |
| p95 지연 | SLA 4000ms의 80% 도달 |
