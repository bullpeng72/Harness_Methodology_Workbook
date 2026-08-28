# ITERATIONS — SupportTriage (트랙 M)

실측만 기록한다 (본편 §2⑦). 예시 수치 금지.
데이터: `results/baselines/<version>.json`(커밋됨), 전체 리포트 `results/final/<version>.json`.
채점: 골든셋 33건(core18+boundary6+priority9), SDK lib 1.0.0rc3 / CLI 1.0.0rc2, `SUPPORT_TRIAGE_OFFLINE=1`.

> ⚠ **오프라인 스텁 모드** — Classifier/Drafter가 실제 LLM이 아니라 키워드 규칙 스텁이다.
> 절대 정확도는 실모델(`models.lock` tier2)에서 재측정하며, 트랙 간 비교(Part XI)와
> Gate 통과 여부·회귀 방향은 이 모드에서도 유효하다.

| version | prompt_version | 무엇을 바꿈 | golden acc | TCR | Gate A | Gate G | gate 결과 |
|---|---|---|---|---|---|---|---|
| **v0** (`v0-baseline`, 태그 `ch16-end`) | v0-baseline | 규칙기반 분류기 + drafter stub. `@agent_eval` 하네스 첫 연결 | 56.1% | 50.0% | 0.53 warn | 0.52 warn | `agent-eval gate --tcr 85 --accuracy 70` → **FAIL, exit 1** |

## v0 전체 스코어카드 (실측)

| Gate | score | status | 비고 |
|---|---|---|---|
| A 목표 달성 | 0.526 | warn | 카테고리·우선순위 정확도 낮음 (스텁). GATE_MAP 기준 A>=0.85 미달 → Part VI 작업 |
| B 행동 무결성 | 1.00 | pass | 규칙기반이라 루프·스코프 위반 없음 |
| C 신뢰성 | 0.80 | pass | LLMJudge 미적용 (S5에서 켬) — hallucination 폴백값 |
| D 성능 계약 | 0.888 | pass | 스텁이라 지연 ~0.5ms |
| E 보안 경계 | 1.00 | pass | **adversarial 셋 미포함** (이번 run은 골든셋만) — S5/Ch29에서 injection·pii 포함해 재측정 |
| F 멀티에이전트 | n/a | — | 하네스가 `agent_interactions` 미기록 (ST-009, S5에서 배선) |
| G 관측성 | 0.515 | warn | 스텁 `reasoning`에 KB 인용 없음 → explainability 낮음. GATE_MAP G>=0.85 미달 |

**FAIL/미달 4개(A·G warn + E 미측정 + F n/a)가 전부 "다음 파트에서 고칠 것"으로 매핑된다** — 이게 Part VI 작업 목록.
