# 역할 정의 — SupportTriage 개발 팀

이 저장소는 《하니스 메서드 실습서》의 러닝 예제를 **역할을 나눈 팀**이 실제로 개발한 기록이다.
워크북 각 장은 이 팀이 밟은 과정과 측정 결과를 정리한 것이다.

| 역할 | 가칭 | git author | 하는 일 | 소유 산출물 |
|---|---|---|---|---|
| **PM** | 박 | `pm-park` | 스펙·설계 HITL 관문 승인/반려, `IRREVERSIBLE.md` 관리, Gate 임계값·릴리즈 판정, 스프린트 계획·회고 | `docs/gates/*.md`(승인 로그), `docs/IRREVERSIBLE.md`, `docs/GATE_MAP.md` 승인란 |
| **개발자 A** | 유진 | `dev-eugene` | Classifier·Retriever. worktree, 클레임, TDD-AI 루프 | `src/support_triage/classifier.py`·`retriever.py`, 해당 이터레이션 로그 |
| **개발자 B** | 민수 | `dev-minsu` | Drafter·Escalation·Review(멀티에이전트) | `src/support_triage/drafter.py`·`escalation.py`·`review.py` |
| **워크북 저자** | 관찰자 | `author` | **개발을 주도하지 않는다.** 과정 관찰, Gate 리포트·명령 출력 verbatim 캡처, 두 트랙 비교, 챕터 집필 | 워크북 원고, `docs/observations/*.md` |
| **대조군 개발자** | 도현 | `dev-c-dohyun` | 방법론·agent-evaluator **없이** 같은 SupportTriage를 프롬프트만으로 개발 | `baseline/` (트랙 C) |

## 규칙

- 한 사람이 여러 역할을 겸할 수 있으나, **역할마다 다른 git author 서명**을 써서 관문 승인·클레임·PR 이력이 실제로 분리돼 남게 한다(`git commit --author`).
- PM은 코드를 쓰지 않는다. 개발자는 관문을 스스로 통과시키지 않는다.
- 저자는 개발 결정에 개입하지 않는다 — 관찰·기록·질문만.
- 대조군(도현)은 트랙 M과 **동일 시간·동일 모델(`models.lock`)·동일 목표**를 받고, 방법론 도구만 빠진다. 일부러 못하게 하지 않는다. 상세 규칙은 [TRACKS.md](TRACKS.md).

## Claude Code 가드레일 프로파일 (본편 §8.4·§34.4)

| 프로파일 | 경로 | 용도 |
|---|---|---|
| dev | `.claude/.agent-evaluator/guardrail_config.json` | 이 저장소를 편집·저작하는 사람의 세션 — 파일 본문 미스캔, `consecutive_repeat`만 하드 차단, 서킷 브레이커 |
| runtime | `guardrail_profiles/runtime.json` | SupportTriage 에이전트가 자율 실행하는 런타임 — `forbidden_tools`, `protected_write_paths` 포함. `eval/`·배포 하네스가 참조 |
