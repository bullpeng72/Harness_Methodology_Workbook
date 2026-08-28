# 두 트랙 — 방법론 有(M) / 대조군(C)

같은 SupportTriage를 두 방식으로 만들고, 마지막에 **동일한 골든셋·adversarial 셋으로 채점**해
차이를 측정한다. 워크북 Part XI가 이 비교를 다룬다.

## 공통 (조작 방지)

- 동일 목표: `docs/PROBLEM.md`의 "무엇을 해결하나"를 두 트랙 모두에게 준다.
- 동일 모델: `models.lock`의 `tier1`/`tier2`.
- 동일 캘린더 시간: 스프린트 S0–S7.
- 동일 최종 채점: `data/golden/`·`data/adversarial/`로 사후 1회.

## 트랙 M (방법론)

`src/support_triage/` + `docs/` 전체 산출물 + `eval/` + `.github/workflows/` + `skills/`.
PROBLEM→SPEC→GATE_MAP→관문1→DESIGN→ADR→관문2→v0→반복(TDD-AI)→Gate 정면돌파→팀 확장→배포.

## 트랙 C (대조군)

`baseline/` 디렉토리.
- 도현은 "지원 티켓을 분류하는 에이전트를 만들어줘" 한 줄로 시작한다.
- SPEC·GATE_MAP·골든셋·가드레일·CI 게이트 없음.
- 눈으로 몇 건 돌려보고 "되는 것 같으면" 다음 기능으로.
- agent-evaluator를 설치하지 않는다.
- 개발 로그(`baseline/DEVLOG.md`)에 리드타임·재작업만 기록한다.

## 측정 지표 (S8 실측 — `docs/observations/S8.md` Part XI 표)

| # | 지점 | 트랙 M (v3) | 트랙 C |
|---|---|---|---|
| 1 | 착수~첫 배포 | S0–S7, 관문 반려 2회(계획됨), 제한 릴리스 | v0 0.5일, 롤백 4회(계획 없음) |
| 2 | "됐다" 판정 | golden category 83.3% / TCR 50%, 실데이터 갭 측정 계획 有 | category 38.9%, priority 0%, 갭 개념 없음 |
| 3 | 위험 명령 | Gate B 1.0, forbidden_tools + NotImplementedError, 실행 0 | 차단 장치 0, 계측 없음 |
| 4 | 프롬프트 인젝션 | Gate E 1.0, adversarial 성공 0/6 | 인젝션 본문 6/6 프롬프트 노출 |
| 5 | 동시 작업 | 클레임 2건, 겹침 0, 머지 충돌 0 | 1인 작업 — 축 없음 |
| 6 | 회귀 | 회귀 PR 1건 차단(exit 2, PM 보류) | 회귀 게이트 없음, 차단 0 |
| 7 | 원인 진단 | `diagnose` 공유원인(SLA) 자동 지목, 1회 실행 | Gate 개념 없음 — 로그·감 |
| 8 | 지식 전파 | 미측정 (온보딩 스킬 미작성) | 미측정 |
| 9 | 비용 | 결정적 Drafter + tier2 로컬, p95 3.02s, 이터레이션당 ≈ $0 | 미측정 |

> 트랙 C 수치는 **오프라인 스텁 + 3종→6종 관대 매핑**(대조군에 유리) 조건에서 측정. 그래도
> 방향은 유효 — 자유 텍스트라 Gate A~G는 애초에 채점 불가.
