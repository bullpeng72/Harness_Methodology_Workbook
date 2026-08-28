# ADR-005 — Drafter는 기본적으로 결정적(무-LLM), 근거 발췌 조립

## 맥락
S5 RCA: Gate C·D 동시 하락의 공유 원인 = SLA breach 100% (p95 12~15s).
per-ticket LLM 호출 = classify(1) + draft(1, grounded 시). exaone3.5:7.8b 는 호출당 4~6s →
draft 호출이 grounded 티켓의 p95를 좌우한다. ST-100 (p95 <= 4000ms)을 못 맞춘다.

## 결정
Drafter는 grounded 시 **LLM을 부르지 않고** top passage 의 제목 + 앞 1~2문장 발췌 +
`[KB-xx]` 인용으로 답변 초안을 조립한다. `근거 없음` 경로는 그대로.
LLM 조립 경로는 `draft_reply(..., deterministic=False)` 로 남겨둔다(품질 비교·Tier 1 가용 시).

## 결과
- per-ticket LLM 호출 = classify(1) 만 (+ 불확실 시 리뷰어, + 키워드 시 escalation) → p95 대폭 감소
- Gate G citation·reasoning 은 유지 (발췌에 `[KB-xx]` 포함)
- (비용) 답변이 "자연스러운 문장"이 아니라 발췌 조립 — 상담원이 다듬는 전제(PROBLEM "검토·수정만")와
  부합. faithfulness 는 발췌라 오히려 높음(passage 에 없는 말을 못 함)

## 대안과 기각
- max_tokens 만 줄이기: 호출 자체가 4~6s라 토큰 축소로는 4000ms 못 맞춤
- 더 빠른 로컬 모델: exaone3.5:7.8b 가 이미 최소. qwen3-coder 는 더 큼
- 병렬 실행: throughput 은 늘지만 per-ticket p95(Gate D 지표)는 안 바뀜
