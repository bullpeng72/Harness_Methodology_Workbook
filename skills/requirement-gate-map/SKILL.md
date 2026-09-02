---
name: requirement-gate-map
description: EARS 요구사항 목록을 Gate A–G 측정 지표에 매핑하는 표를 만든다. 절차 본문은 본편 spec-driven-artifacts "3) Gate 매핑 초안"을 따르고, 여기서는 EARS 문장을 매핑 행으로 바꾸는 입력 규칙만 다룬다. 요구사항 리뷰, GATE_MAP 작성·갱신에 사용.
---

# 요구사항 → Gate 매핑 (EARS 입력용 래퍼)

> **절차 정본**: 본편 스킬 `spec-driven-artifacts`의 "3) Gate 매핑 초안". 이 파일은 그 절차를
> EARS 요구사항 목록이라는 입력 형식에 적용할 때의 규칙만 추가한다 — 절차 본문을 복붙하지 않는다.

각 EARS 요구사항("WHEN <조건>, THE SYSTEM SHALL <동작>")에 대해 한 행을 만든다:

1. **어느 Gate가 측정하나** — A 목표 / B 행동 / C 신뢰 / D 성능 / E 보안 / F 조율 / G 관측
2. **측정 수단** — Config · 트래커 · 골든셋 중 무엇
3. **정량 판정 기준** — `>= 85%`, `< 5%`, `0건` 형태. 서술 금지("자연스럽다" 같은 문구는 반송)

## 반송 규칙

- 측정 수단이 안 나오면 → "측정 불가" 칸에 적고 SPEC으로 되돌린다.
- 모든 요구사항이 Gate A에 몰리면 → 부정형·비기능 요구사항(B/D/E)이 부족한 것.
- 대응 요구사항이 없는 Gate는 `not_measured`로 둔다 — 억지로 만들지 않는다(본편 §17.1).

## 산출물

`docs/GATE_MAP.md` — 매핑표 + "측정 불가로 반송" 표 + `not_measured` Gate 목록 + PM 승인란.
`.aoo/targets.json`(`agent-eval target set`)의 값과 GATE_MAP의 "정량 판정 기준"은 **같은 숫자**여야 한다.

이 래퍼는 특정 평가 도구 이름을 본문에 넣지 않는다 — Gate 개념만 있으면 다른 도구로도 쓸 수 있다.
