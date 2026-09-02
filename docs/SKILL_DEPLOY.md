# 스킬 배포 체크리스트

`skills/` 를 팀에 배포하기 전에 확인한다 (Part IX / Ch 38).

- [ ] `just validate-skills` 통과 (WARN 0)
- [ ] 도메인 스킬(`support-triage-labeling`)이 `data/golden/README.md` 와 한 소스인지 확인
- [ ] `description` 으로 실제 호출되는지 3가지 표현으로 테스트 ("골든셋 라벨 불일치 조정해줘" / "티켓 분류 기준 알려줘" / "새 상담원 온보딩")
- [ ] 두 래퍼(`requirement-gate-map`·`gate-chapter-loop`)가 `> 절차 정본:` 줄로 본편 스킬을 참조하고, 절차 본문을 복붙하지 않았는지
- [ ] 팀 스킬 저장소(공유 위치)에 커밋
- [ ] 온보딩 문서에 "새 상담원은 `support-triage-labeling` 스킬을 읽는다" 추가
- [ ] `pr-verify` CI 에 `validate-skills` 잡이 추가됨

## 플랫폼 종속 3단계 (Ch 38.3)

| 종속 정도 | 예 | 허용 스킬 유형 |
|---|---|---|
| 완전 무관 | "요구사항을 Gate에 매핑" | 범용 · 도메인 · 절차 전부 |
| 개념 결합 | "`agent-eval gate` 로 판정" | 절차 스킬은 OK(팀 워크플로), 범용은 지양 |
| 문법 결합 | `$ARGUMENTS`, Claude Code 전용 훅 | 절차 스킬도 지양 — 예시로만 |

`support-triage-labeling`(도메인)·`requirement-gate-map`(범용)은 **완전 무관** 수준 유지.
`gate-chapter-loop`(절차)은 이 팀 도구를 언급해도 되지만 러너 명령은 예시로 격리한다.
