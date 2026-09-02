# .aoo/improve/

`agent-eval improve start <result.json> --gate <X> --yes` writes one stub per proposal here
as `<Gate>_<change-type>_<id>.md` (before/after + a 3-step "apply -> re-run -> verify").

In this reproduction the S5–S7 RCA closed loop (diagnose -> act -> verify) was done by hand
(workbook Ch 39–40); that history lives in `.aoo/experiments.jsonl` and
`results/recommendation_outcomes.jsonl`. Running `improve start` directly regenerates the
result stubs into this directory (Ch 25.5).
