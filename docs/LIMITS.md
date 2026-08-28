# LIMITS — 이 스택/이 재현으로 해결하지 못한 것

본편 §34.3·§34.4 — 정직한 한계 목록. 실측 근거와 함께.

## L1. Gate D 완전 통과 — 로컬 추론 지연 하한

- **상태**: S6(v3) 이후 p95 3.02s (SLA 4000ms 통과), SLA penalty 0. 그러나 Gate D score 0.57 (warn) —
  `avg_budget_score` 0.68 · efficiency 성분이 절대 기준 미달.
- **원인**: `models.lock` tier2 = `exaone3.5:7.8b` 로컬 추론이 호출당 ~3s. 분류 1콜만으로도
  이 지연·토큰 비용이 `EfficiencyConfig`/`ResourceBudgetConfig` 의 절대 임계값을 못 넘는다.
- **이 스택 밖**: 프로덕션은 더 빠른 추론(전용 GPU·서빙 프레임워크·더 작은 파인튜닝 모델)을 쓴다.
  ST-100(p95 ≤ 4000ms)은 그 환경 기준이고, 로컬 재현은 경계선에 있다.
- **재현 계약(본편 §2⑦)**: Gate D 절대 점수는 하드웨어·모델에 종속 → 계약 밖. Gate D의
  **SLA breach 여부·회귀 방향**은 계약 안.

## L2. TCR 50% — category·priority 동시 정답률

- **상태**: accuracy 83.3%(부분 점수 평균)인데 TCR 50%. `--tcr 85` 절대 게이트가 계속 FAIL.
- **원인**: `score_fn` 이 category 0.5 + priority 0.5. 둘 다 맞는 케이스가 ~50%(각각 ~85%/~80%인데
  곱해지면). priority 판정(P1/P2/P3 규칙)이 category보다 어렵다.
- **다음**: S7/Ch 25(Gate A)에서 priority few-shot·규칙 프롬프트로. 이 재현 범위 안.

## L3. Gate C faithfulness 미측정 — Tier 1 키 부재

- LLMJudge(faithfulness)는 Tier 1(ADR-003)인데 `ANTHROPIC_API_KEY` 없음.
  Gate C는 `graceful_degradation`·`idempotency`·SLA로만 채점됨(그래도 pass).
  키 확보 시 faithfulness 재측정 필요.

## L4. Gate F 계측 — 하네스 미배선

- ST-009(리뷰어 역할)은 하네스가 `agent_interactions` 를 monitor에 넘겨야 채점된다.
  `run_batch.py` 미배선 → Gate F `n/a`. S-later에서 배선하거나 Part XI에서 "계측 후 목표"로 명시.

## L5. 오프라인 스텁 vs 실모델

- `SUPPORT_TRIAGE_OFFLINE=1` 은 키워드 스텁 — 절대 정확도가 실모델과 다르다.
  Gate 통과 여부·회귀 방향·트랙 비교는 두 모드에서 유효.
