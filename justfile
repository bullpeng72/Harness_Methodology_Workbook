# SupportTriage — just 타깃 (워크북 부록 D 참조)
# 오프라인 스텁 기본. 실모델 실행은 SUPPORT_TRIAGE_OFFLINE 미설정 + models.lock tier2 pull.

_open := if os() == "macos" { "open" } else { "xdg-open" }

# 도구 체인·모델 핀 점검
doctor:
    @python -c "import agent_evaluator, sys; print('agent_evaluator', agent_evaluator.__version__)"
    @python -c "import pathlib; print('models.lock', 'OK' if pathlib.Path('models.lock').exists() else 'MISSING')"
    @agent-eval --version || true

# 배치 평가 1회 → results/evaluation.{json,html}
eval note="v0 규칙기반 기준선":
    SUPPORT_TRIAGE_OFFLINE=1 python eval/run_batch.py --golden data/golden --note "{{note}}" --out evaluation

# 골든셋 코어 18건만 (빠른 반복)
eval-core note="v3-det-draft":
    SUPPORT_TRIAGE_OFFLINE=1 python eval/run_batch.py --golden data/golden --note "{{note}}" --out evaluation --s5 --limit 18

# adversarial 셋 포함
eval-adversarial:
    SUPPORT_TRIAGE_OFFLINE=1 python eval/run_adversarial.py

# 트랙 C 대조군 채점
eval-baseline:
    SUPPORT_TRIAGE_OFFLINE=1 python eval/run_baseline.py

# 마지막 결과로 게이트
gate:
    agent-eval gate results/evaluation.json --tcr 85 --accuracy 70 --baseline-version current --fail-on-regression 12

# HTML 리포트를 브라우저로 연다
report:
    {{_open}} results/evaluation.html

# 현재 결과 + 커밋된 기준선 → 회귀 진단 모드 HTML
report-baseline:
    python eval/make_report.py results/evaluation.json --baseline results/baselines/current.json
    {{_open}} results/evaluation.html

# 버전별 확정 리포트 재생성 (results/final/v*.json → v*.html, 직전 버전 기준선)
report-final:
    python eval/make_report.py --final

test:
    SUPPORT_TRIAGE_OFFLINE=1 python -m pytest -q
