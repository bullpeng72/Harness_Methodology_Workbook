---
name: support-triage-labeling
description: SupportTriage 티켓에 카테고리(6종)·우선순위(P1/P2/P3) 정답 라벨을 다는 규칙. 골든셋 라벨링, 라벨 불일치 조정, 새 상담원 온보딩, 티켓 분류 기준 확인에 사용.
---

# SupportTriage 티켓 라벨링

> 이 스킬은 `data/golden/README.md`의 라벨링 규칙과 **한 소스에서** 나온다. 둘이
> 어긋나면 라벨링이 갈린다 — 규칙을 바꾸면 두 곳을 함께 고친다.

## 카테고리 (하나만)

`billing` · `bug` · `how-to` · `account` · `abuse` · `other`

우선순위 규칙:
1. 결제·청구·환불 관련 언급이 있으면 `billing` (`account`보다 우선)
2. 재현되는데 동작 안 함 = `bug` / 절차·방법을 물음 = `how-to`
3. 계정 접근·정보 변경 = `account`
4. 욕설·악용·조작 시도 = `abuse`
5. 6종 어디에도 안 맞으면 `other` — 새 카테고리를 만들지 말 것 (`docs/IRREVERSIBLE.md` 등재 항목)

## 우선순위 (하나만)

- **P1**: 결제 실패 · 서비스 중단 · 보안
- **P2**: 기능 오류 · 계정 접근 문제
- **P3**: 사용법 문의 · 기타

## 에스컬레이션 (실행하지 않음 — 판정만)

환불 · 계정 잠금해제 · 2FA 재설정을 요청 = `escalate`. 도구는 호출하지 않는다
(`refund()`/`account_unlock()`는 `NotImplementedError`).

## 경계 케이스

- **how-to vs bug**: "이렇게 쓰는 게 맞나요"만 = `how-to` / "재현되는데 안 됩니다" = `bug`
- **billing vs account**: 돈이 걸리면 `billing`

## 라벨 불일치 조정

2인이 **독립적으로** 라벨 → 불일치 건을 `data/golden/_disagreements.md`에 기록 →
토론 후 확정. 여전히 불일치면 **낮은 우선순위 / 더 일반적인 카테고리**를 선택.
3회 이상 불일치하는 티켓은 골든셋에서 제외한다 (억지 정답보다 낫다).

**라벨 불일치율이 곧 골든셋의 상한 정확도다** — 에이전트가 그 선을 크게 넘으면
라벨 품질을 먼저 의심한다(이 프로젝트: 불일치 11.6%).

상세 예시: `references/category-rules.md`
