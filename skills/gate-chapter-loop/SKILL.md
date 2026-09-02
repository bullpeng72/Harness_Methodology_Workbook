---
name: gate-chapter-loop
description: SupportTriage의 한 Gate를 목표선(>= 0.85)까지 올리는 반복. 절차는 본편 gate-improvement-loop을 따르고, 여기서는 이 프로젝트의 파일·golden 셋 이름만 지정한다. 한 Gate 점수가 낮을 때, Gate 정면돌파 작업에 사용.
---

# Gate 개선 루프 — SupportTriage 적용

> **절차 정본**: 본편 스킬 `gate-improvement-loop`. 이 파일은 그 6단계를 이 프로젝트에
> 매핑한 값만 담는다 — 절차 본문을 복붙하지 않으므로, 본편 스킬이 갱신되면 이 래퍼는
> 자동으로 최신 절차를 따른다(특화 ≠ 복제).

| 본편 절차 단계 | 이 프로젝트에서 |
|---|---|
| 1. `details` 열기 | `results/evaluation.json` → `extra_metrics.harness_groups.<Gate>.details` |
| 2. 실패 케이스 수집 | `data/golden/golden_core.json`(카테고리) · `golden_boundary.json`(경계) · `golden_priority.json`(우선순위)에서 대상 성분이 낮은 티켓 |
| 3. 한 가지 수정 | `src/support_triage/`의 classifier/retriever/drafter 중 하나, 또는 프롬프트 하나, 또는 `eval/run_batch.py`의 Config 하나 |
| 4. 재측정 | 배치 평가를 1회 실행하고 `agent-eval gate ... --baseline-version <직전 태그>`로 회귀 확인. (이 저장소의 러너 명령 예: `just eval` → `agent-eval gate results/evaluation.json --baseline-version <태그>`) |
| 5. 기록 | `docs/ITERATIONS.md`에 한 줄 (version · 변경 · 성분 before→after · 증명) |
| 6. 회귀 시 | 되돌린다 — 다른 Gate가 좋아졌어도. Ch 27이 겪은 v1→v2 Gate C·D 동시 하락이 예 |

`agent-eval improve plan/start/verify`(SDK)가 이 루프의 CLI 구현이다 — 성분 분해 → 제안 → 실험
등록 → 예측 대비 실측을 대신 돌린다(Ch 25.5, Ch 40).
