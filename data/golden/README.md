# 골든셋 — SupportTriage

`IRREVERSIBLE.md` 등재 항목. 변경은 리뷰 2인 + 변경 이력 커밋.

## 파일

| 파일 | 건수 | 용도 |
|---|---|---|
| `golden_core.json` | 18 | 표준 케이스 (카테고리 3건씩). Gate A 주 채점 |
| `golden_boundary.json` | 6 | how-to↔bug, billing↔account 경계. 별도 측정 |
| `golden_priority.json` | 9 | 우선순위 규칙 검증 (P1/P2/P3 각 3건) |
| `../adversarial/injection.jsonl` | 6 | ST-006 — 정답 = 지시 무시 |
| `../adversarial/pii.jsonl` | 4 | ST-007 — 정답 = PII 미포함 |

**합계 43건.** S2 스타터. Part VI(Ch 20)에서 실티켓으로 확장 예정.

## 라벨링 규칙 (GATE_MAP·DESIGN과 한 소스)

- **카테고리**: 결제·청구·환불 = billing (account보다 우선) / 재현되는 오작동 = bug / 절차·방법 문의 = how-to / 계정 접근·정보 변경 = account / 욕설·악용·조작 시도 = abuse / 6종 밖 = other
- **우선순위**: P1 = 결제 실패·서비스 중단·보안 / P2 = 기능 오류·계정 접근 문제 / P3 = 사용법·기타
- **에스컬레이션**: 환불·계정 잠금해제·2FA 재설정을 요청 = escalate (실행 X)
- **경계 how-to vs bug**: "이렇게 쓰는 게 맞나요"만 = how-to / "재현되는데 안 됩니다" = bug

## 2인 라벨링 절차 (본편 §15.4)

- 유진·민수가 **독립적으로** 라벨 → `_disagreements.md`에 불일치 기록 → 토론 후 확정
- 3회 이상 불일치하는 티켓은 골든셋에서 제외 (억지 정답보다 낫다)
- 라벨 불일치율이 곧 골든셋의 상한 정확도

## 실분포 (측정용 균형과 별개)

샘플 100건 관측: P1 ≈ 8%, abuse ≈ 2%, how-to/bug 경계 모호 ≈ 12%.
골든셋은 각 클래스 측정을 위해 균형화. SLA·비용 계산(Gate D)에는 이 실분포를 쓴다.
