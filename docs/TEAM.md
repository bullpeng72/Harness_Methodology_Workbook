# TEAM — 동시성 모델과 협업 그라운드 룰

작성: 유진·민수 (S4, Part VIII)  ·  승인: 박 (PM)
역할 정의는 [ROLES.md](ROLES.md), 역할별 프로토콜은 실습서 부록 H.

## 1. 동시성 모델 = git worktree

두 번째 개발자(민수)가 합류해 유진과 **동시에** 다른 파일을 고치는 상황에서
세 방식을 비교했다.

| | git worktree | Agent Teams | 브랜치만 |
|---|---|---|---|
| 격리 단위 | 디렉토리(작업트리) | 에이전트 세션 | 브랜치 |
| 동시 편집 충돌 감지 | 파일 시스템 레벨 | 세션 간 조율 필요 | merge 시점에야 발견 |
| LiveGuardrail 연동 | `team_concurrency`로 클레임 공유 | 〃 | 클레임 수동 |
| 적합 규모 | 2~4인, 명확히 나뉘는 작업 | 다수 에이전트 병렬 | 1~2인, 거의 안 겹침 |
| **이 프로젝트** | **✅ 선택** | 과함 | 충돌 위험 |

**근거**: 작업이 파일 단위로 나뉘고(`retriever.py` vs `drafter.py`+`data/kb/`), 각자 별도
디렉토리에서 배치 평가를 돌려도 서로 방해하지 않으며, `.aoo/claims.jsonl`로 겹침을 실행
전에 잡을 수 있다.

```bash
git worktree add ../stw-retriever -b feat/embed-swap    # 유진
git worktree add ../stw-drafter   -b feat/kb-cleanup    # 민수
git worktree list        # 현황
git worktree remove <경로>   # 병합 후 정리 (안 하면 stale 브랜치가 쌓임)
```

## 2. worktree만으로는 부족한 것

worktree는 **파일을 분리**하지만 "민수가 지금 `drafter.py`를 만지고 있다"는 **의도**는
공유하지 않는다. 이 간극을 메우는 것:

- **클레임 로그** (`.aoo/claims.jsonl`, `agent-eval claims`) — 스코프를 실행 전에 선언.
  두 worktree가 메인 저장소 경로의 같은 파일을 본다. CI `claims-audit` 잡이 TTL 초과·겹침을 exit 1로 잡는다.
- **브랜치 보호** (`guardrail_profiles/` `BranchGuardConfig`) — 보호 브랜치 직접 커밋/푸시 차단.

## 3. 그라운드 룰

- 역할마다 다른 git author 서명(`git commit --author`).
- 개발자는 자기 Gate를 자기가 통과시키지 않는다 — 리뷰는 다른 개발자 또는 PM 서명(`docs/gates/`).
- 파일을 만지기 전에 클레임을 연다. 끝나면 `agent-eval claims release`.
- 보호 브랜치(`main`)에는 PR + `pr-verify` 통과로만 머지.
