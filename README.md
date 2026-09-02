# SupportTriage — 《하니스 메서드 실습서》 러닝 예제

지원 티켓을 분류(6종)·우선순위(P1/P2/P3)·답변 초안·에스컬레이션 판정하는 에이전트.
이 저장소는 **역할을 나눈 팀**이 AC(Agent-Evaluator + Claude Code) + 하네스 방법론으로 실제로
개발한 기록이며, 같은 것을 방법론 없이 만든 **대조군(트랙 C)**과 나란히 둔다.

> `Ch NN`·`Part N`·`§N.N` 은 함께 배포되는 《하니스 메서드 실습서》의 장·절이다(저장소에 포함 안 됨).
> `본편 §NN` 은 《하니스 메서드》. `SDK 가이드` 는 《AI 에이전트 Harness Engineering 실무 가이드》.

## 구조

```
docs/            방법론 산출물 — 실제로 생산된 파일 (서술이 아님)
  ROLES.md · TEAM.md · TRACKS.md · PROBLEM.md · SPEC.md · GATE_MAP.md · REUSE.md
  IRREVERSIBLE.md · FAILURE_MODES.md(S2) · ITERATIONS.md(S3+) · MATURITY.md · LIMITS.md · DEPLOY.md
  SKILL_CANDIDATES.md · SKILL_DEPLOY.md(Part IX)
  gates/         HITL 관문 승인·반려 로그
  (저자 관찰 S0–S8 원문은 저장소가 아니라 《하니스 메서드 실습서》 부록 J에 있다)
src/support_triage/   트랙 M 에이전트 (v0→v1.0→v2→v3, 실제 커밋 이력)
baseline/            트랙 C 대조군 (도현이 한 줄 프롬프트로. 수정 안 함)
eval/  run_batch.py(@agent_eval 배치) · run_adversarial.py · run_baseline.py · make_report.py · validate_skills.py
data/  kb/ · tickets/ · golden/(2인 라벨, core18+boundary6+priority9) · adversarial/(injection6+pii4)
skills/  support-triage-labeling(도메인) · requirement-gate-map · gate-chapter-loop (본편 스킬 도메인 래퍼, Part IX)
results/  baselines/(회귀 기준점, 커밋됨 · 본편 §20.4.3) · final/(v0..v3 확정 리포트, 커밋됨) · recommendation_outcomes.jsonl(RCA 폐루프 이력, 커밋됨)
.aoo/  claims.jsonl(팀 클레임 — CI claims-audit가 읽음) · targets.json(SLO) · experiments.jsonl · reference.json · improve/
guardrail_profiles/runtime.json   에이전트 런타임용 가드레일 (dev 세션용과 분리, 본편 §8.4)
.claude/.agent-evaluator/guardrail_config.json   dev 세션용 (편집·저작)
models.lock         모델 + SDK 버전 고정 (재현 계약 · 본편 §34.4)
```

## git 태그

`s0-setup` · `spec-approved`(관문 1) · `design-approved`(관문 2, S2) · `chNN-start`/`end`(S3+) ·
`prod-YYYYMMDD`(S7) · `workbook-complete`.

## 빠른 실행

```bash
SUPPORT_TRIAGE_OFFLINE=1 python demo.py          # 트랙 M 파이프라인 (오프라인 스텁)
SUPPORT_TRIAGE_OFFLINE=1 python baseline/triage.py   # 트랙 C v0
SUPPORT_TRIAGE_OFFLINE=1 python -m pytest -q
pip install -e ".[dev]" && python eval/run_batch.py  # 실제 Gate 측정
```

## 진행 상태 (S8 종료 — 스프린트 완료)

- [x] S0 준비 — 저장소·버전 고정·가드레일 프로파일·트랙 C v0 (`s0-setup`)
- [x] S1 관문 1 — PROBLEM/SPEC(ST-001~009,100,101)/GATE_MAP/IRREVERSIBLE, 반려 1회 후 `spec-approved`
- [x] S2 분석·설계 — FAILURE_MODES(F1–F10), 골든셋 43건 2인 라벨(불일치 11.6%), DESIGN(코드와 1:1)/ADR-001~004, 반려 1회 후 `design-approved`
- [x] S3 v0 + 첫 gate — `@agent_eval` 골든셋 33건 채점 → **FAIL exit 1** (TCR 50%, acc 56%, A 0.53/G 0.52 warn). 실행 중 SDK API 오류 3건 발견·수정. `results/baselines/v0-baseline.json` 커밋. `ch16-end`
- [x] S4 v1.0 LLM — acc 56→76% (abtest p=0.036, d=0.53) but Gate C 0.8→0.2 & D 0.89→0 regressed; regression gate exit 2; PM held. pr-verify.yml, claims log. `ch21-end`
- [x] S5 v2 — RAG(임베딩)·LLM 호출 축소, Gate C 0.20→0.60·G 0.52→1.0. `diagnose`가 C·D 공유원인(SLA) 지목. `ch27-end`
- [x] S6 v3 — Drafter 결정적화(ADR-005), p95 12s→3.02s, Gate C 0.757 PASS·D warn. `current`=v3. `LIMITS.md`. `ch28-end`
- [x] S7 — RCA 폐루프: `verify_recommendation_outcome` → C·D **confirmed**. `MATURITY.md`(L3/L4), `DEPLOY.md`. 제한 릴리스 `prod-20260828`
- [x] S8 — 두 트랙 동일 채점: `eval/run_baseline.py` → 트랙 C category 38.9% / priority 0% / 인젝션 6/6 노출 / Gate 채점 불가. Part XI 9지표 표 완성(실습서 부록 J §J.S8). `workbook-complete`
- [x] Part IX — 반복 절차 → 스킬 3종(`skills/`), `docs/SKILL_CANDIDATES.md` · `SKILL_DEPLOY.md`, `just validate-skills` + CI 잡

> **실측 원칙** (본편 §2⑦): `docs/ITERATIONS.md`의 수치는 전부 실제 `agent-eval` 실행 결과다.
> 오프라인 스텁 모드라 절대 정확도는 실모델에서 재측정하지만, Gate 통과 여부·회귀 방향·
> 트랙 비교는 이 모드에서도 유효하다.
