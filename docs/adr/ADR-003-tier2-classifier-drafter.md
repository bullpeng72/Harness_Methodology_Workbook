# ADR-003 — Classifier·Drafter는 Tier 2, 채점은 Tier 1

## 맥락
ST-101: 이터레이션 비용이 Tier 1 API 요금에 비례하면 안 된다. Part V–VI에서 수십~수백 회 재실행.

## 결정
- Classifier·Drafter 추론 = Tier 2 (로컬, `models.lock`의 `tier2`)
- LLMJudge faithfulness 채점 = Tier 1 — 채점은 판정이라 작은 모델은 버전 비교를 흔든다
- SPEC·설계·RCA = Tier 1 (1회성)
- CI에서 Ollama 없으면 `tier2_fallback`(Claude Haiku) — 이 경우 절대 점수가 로컬과 다를 수
  있으므로 CI는 회귀 게이트 위주로 판정

## 결과
- 반복 비용이 API 요금과 분리됨
- (비용) Tier 2 정확도가 Tier 1보다 낮음 — 이 책의 목적은 최고 정확도가 아니라 방법론 시연

## 대안과 기각
- 전부 Tier 1: Gate D(비용) 장에서 개선할 여지가 사라짐
