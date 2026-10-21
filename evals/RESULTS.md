# Eval results

## Demo-site audit, source only (2026-10-21)

**Setup.** Claude Code 2.1.128 in headless mode with `--plugin-dir .`, running in a copy of the repository with `ANSWER-KEY.md`, `fixed.html`, `sample-report.md`, and `evals/` removed. The prompt was eval 1 in [`accessibility-audit/evals.json`](accessibility-audit/evals.json) with "no browser available". Allowed tools: Read, Grep, Glob, Skill, and `python3`. Each run was graded by hand against the 22 barriers in the [answer key](../examples/demo-site/ANSWER-KEY.md).

| Run | Skill version | Found | Partial | Missed | Notes |
|---|---|---|---|---|---|
| 1 | v1.1.0 draft | 20 | 1 (B13 autocomplete, filed as untested) | 1 (B11 label in name) | Used `contrast.py` for every pair. Overstated the notice as already clipped at default size. |
| 2 | Added "source-only review" checklist | 18 | 3 (B5, B7, B21) | 1 (B11) | Missed the 16×16 social links that run 1 caught; shows run-to-run variance. |
| 3 | Checklist covers label-in-name on role-less elements, declared target sizes, images of text in SVG | **22** | 0 | 0 | One criterion misattribution: cited 2.4.11 alongside 2.4.7 for `outline: none`. |
| 4 | Checklist states that a missing indicator is 2.4.7 only | **22** | 0 | 0 | 2.4.11 now appears only among checks needing real focus traversal. Run isolated from user-level skills and settings. |

All three runs:

- marked the rendered checks (reflow, text spacing, target size) as predicted or untested, not passed;
- listed screen-reader and keyboard checks as not performed;
- made no conformance claim;
- kept AAA out of AA findings.

## Contrast fix (2026-10-21)

Eval 2 in [`accessibility-fix/evals.json`](accessibility-fix/evals.json).

| Run | Result |
|---|---|
| 1 | Correct answer (`#767676`, 4.54:1), but computed by hand instead of running `contrast.py`. |
| 2 | After the skill named the script explicitly: ran `contrast.py --target 4.5` and quoted its output. All 4 expectations met. |

## Other skills (2026-10-21)

Run headless with `--setting-sources project,local` so only the plugin's skills were available, each in its own copy of the repository.

| Skill | Eval | Result | Notes |
|---|---|---|---|
| accessibility-standards | 1: is 44×44 required at AA? | 4/4 | 24×24 for 2.5.8 with exceptions; 44×44 identified as 2.5.5 AAA and allowed as a design goal. |
| accessibility-standards | 2: city of 30,000 | 3/4, then **4/4** | First run called 2.2 AA a "superset" of 2.1 AA. After the skill noted that 2.2 removed 4.1.1, the rerun checked DOJ live, gave April 26, 2028, and flagged 4.1.1 for the 2.1-based rule. |
| accessibility-checks | 1: Husky + CI | 5/5 | Inspected Husky and appended to its hook instead of setting `core.hooksPath`. Wrote an argument-array config with `claude: false` and added the CI step. The headless harness blocked the `.husky/pre-commit` edit as a sensitive file; the agent reported this instead of working around it. It also noticed the fixture had no server, which is now fixed. |
| healthcare-accessibility | 1: lab results table | 4/5, then **5/5** | Values, units, and ranges unchanged; no inferred direction or severity. The first run did not ask for clinical-owner review of new wording; after the skill required it, the rerun listed every wording change for confirmation. It cited 1.3.3 for a color-only flag, which mainly applies to instructions. |

## Trigger evals (2026-10-21)

`run_triggers.py`, all five skills loaded together, isolated from user-level skills and settings.

| Run | Setup | Passed | Misses |
|---|---|---|---|
| 1 | 2 runs per query, first tool call only | 47/50 | Audit: end-to-end VoiceOver/keyboard test, evidence ledger. Fix: focus trap. |
| 2 | Sharper audit and fix descriptions, 3 runs per query, audit and fix sets only | 20/22 | Evidence ledger (the model chose a docs connector), and a remediation prompt where the model read the file before choosing. |
| 3 | Runner isolates MCP servers and waits for the first Skill call; all sets, 3 runs per query | 48/50 | "Run a11y tests after Claude edits" went to the built-in `update-config` skill; a county-hospital legal question went to healthcare 2 of 3 times. |
| 4 | Checks description names post-edit automation; standards covers which rules apply to an organization; healthcare defers legal-only questions to standards | **50/50** | 49 of 50 unanimous across 3 runs. The remaining query passed 2 of 3. |

Run 2 also exposed two artifacts in the runner rather than the skills: MCP connectors were still loaded, and reading a file before choosing a skill counted as "no skill". The runner now passes `--strict-mcp-config` and waits for the first Skill call.

Results vary between runs, so rerun after any change to a skill description or reference that the audit relies on.
