# ITERATIONS — SupportTriage (트랙 M)

실측만 기록한다 (본편 §2⑦). 예시 수치 금지.
데이터: `results/baselines/<version>.json`(커밋됨), 전체 리포트 `results/final/<version>.json`.
채점: 골든셋 33건(core18+boundary6+priority9), SDK lib 1.0.5 / CLI 1.0.5 (`models.lock`, S8 정렬 후 post-S8 마이그레이션), `SUPPORT_TRIAGE_OFFLINE=1`.

> ⚠ **오프라인 스텁 모드** — Classifier/Drafter가 실제 LLM이 아니라 키워드 규칙 스텁이다.
> 절대 정확도는 실모델(`models.lock` tier2)에서 재측정하며, 트랙 간 비교(Part XI)와
> Gate 통과 여부·회귀 방향은 이 모드에서도 유효하다.

> ℹ **post-S8 마이그레이션 (v1.0.0 → v1.0.5)** — SPEC-042(하네스 정합)·043(개발 지원)·044
> (HTML 리포트)를 반영했다. 전부 옵트인이라 기본 채점 경로는 불변 — 아래 v0~v3 표의 Gate
> 값·회귀 방향은 그대로다(옵트인 기능을 켜지 않는 한). 결과 JSON에 새 `insights` 키가
> 추가되고, `results/final/v*.html`은 3계층(판정 / 이터레이션 / 증거) 레이아웃으로
> 재생성됐다(`eval/make_report.py --final`). 아래 실측값은 v1.0.0 시점 real-Ollama
> 스냅샷이며, LLM 비결정성 탓에 재실행 시 소수점은 달라진다 — 이 표는 **방향의 정본**이다
> (본편 §20.2). 스프린트 태그 `ch16-end`~`ch28-end`의 `results/`는 v1.0.0 측정본으로
> 동결돼 있다.

| version | prompt_version | 무엇을 바꿈 | golden acc | TCR | Gate A/C/D | gate 결과 | abtest(acc) vs 직전 |
|---|---|---|---|---|---|---|---|
| **v0** (`v0-baseline`, `ch16-end`) | v0-baseline | 규칙기반 스텁. `@agent_eval` 하네스 첫 연결 | 56.1% | 50.0% | 0.53 / 0.80 / 0.89 | `--tcr 85 --accuracy 70` → **FAIL exit 1** | — |
| **v1.0** (`v1-llm`, `ch21-end`) | v1.0-llm | Classifier·Drafter를 실제 Ollama `exaone3.5:7.8b`로 (models.lock 정정) | **75.8%** | 50.0% | 0.585 / **0.20** / **0.00** | `--tcr 85 --accuracy 70` → FAIL exit 1 · 회귀게이트 vs v0 → **exit 2** | +19.7pp, **p=0.036, d=0.53 (유의)** |

| **v2** (`v2-rag`, `ch27-end`) | v2-rag-s5 | RCA(diagnose)로 C·D 공유원인=SLA 확인 → LLM 호출 축소(고신뢰 리뷰어 스킵/키워드 없으면 escalation LLM 스킵) + 실제 임베딩 RAG(`mxbai-embed-large`) + Gate C Config(hallucination/degradation/fault-tol/idempotency) | **83.3%** (golden_core 18) | 50.0% | 0.615 / **0.597** / 0.011 | `--tcr 85 --accuracy 70` → FAIL exit 1 (acc PASS, TCR FAIL). Gate **G 0.52→1.0**, C **0.20→0.60** | vs v1: 회귀 없음 (`diagnose` → No Gate detected) |

| **v3** (`v3-det`, `ch28-end`) | v3-det-draft | Drafter 결정적화(ADR-005, draft LLM 콜 제거) + classify max_tokens 300→120 + escalation 키워드전용 + Gate D Config | 83.3% (golden_core 18) | 50.0% | 0.605 / **0.757** / **0.570** | `--tcr 85` FAIL (acc PASS). **Gate C PASS, D fail→warn, p95 12.1→3.02s** | vs v2: No Gate detected |

## v3 판정 — SLA/공유원인 해소, 아직 미승격 (박, PM)

**S5 RCA가 지목한 C·D 공유원인(SLA breach)이 해소됐다** — p95 12.1s→**3.02s**(< 4000ms), SLA breach
100%→~0%. **Gate C 0.60→0.76 (PASS)**, Gate D 0.01→0.57 (fail→warn). `sla_window_penalty`·
`sla_budget_penalty` 둘 다 0 — D의 남은 gap은 SLA가 아니라 로컬 7.8B 추론의 raw efficiency다
(`docs/LIMITS.md` L1). 절대 게이트는 여전히 TCR 50%로 FAIL (`LIMITS.md` L2 — category·priority
동시 정답률, S7/Ch 25에서).

**`current` 기준선을 v0 → v3 로 advance** — v0는 스텁이라 실LLM 버전과의 회귀 비교가 노이즈
("p95 0s→4s = 800000% 회귀"). v3부터 의미 있는 회귀 추적. v3가 절대 게이트를 통과한 건 아니지만
"현재 최선"으로 삼는다.

## v2 판정 — 승격 안 함, 진전 (박, PM)

v1의 Gate C 회귀를 되돌렸다(0.20→0.60) — `graceful_degradation` 0.98·`idempotency` 1.0가 측정됐고,
LLM 호출 축소로 p95 15.2s→12.1s. **Gate G는 0.52→1.0** (실제 reasoning + KB 인용). 하지만
C·D는 여전히 v0(0.80/0.89) 아래 — **SLA breach 100%(p95 12.1s ≫ 4000ms)가 C의 상한을 누르고
D를 fail시킨다.** 이건 C·D 공유 원인이고, D는 아직 안 고쳤다(S6). `current` 기준선은 v0 유지.
faithfulness(LLMJudge)는 Tier1 키 없어 미측정 — 키 확보 시 재측정.

## v1.0 판정 — 승격 안 함 (박, PM)

정확도는 유의하게 올랐으나(56→76%, p=0.036), **Gate C 0.80→0.20, Gate D 0.89→0.00 회귀** —
회귀 게이트 exit 2. p95 지연 0s→**15.2s**(실제 LLM, SLA 4000ms 초과). "정확도가 올랐으니 괜찮다"는
원칙 2가 막는다. v1.0은 "LLM이 분류엔 도움이 되지만 파이프라인이 C(근거·판정)와 D(지연·티어)를
못 받친다"는 것을 데이터로 보여주는 체크포인트다. 회귀 기준선(`current`)은 v0에 유지, S5(Gate C)·
S6(Gate D)에서 해소 후 승격.

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
