# Eval results

## Demo-site audit, source only (2026-10-21)

**Setup.** Claude Code 2.1.128 in headless mode with `--plugin-dir .`, running in a copy of the repository with `ANSWER-KEY.md`, `fixed.html`, `sample-report.md`, and `evals/` removed. The prompt was eval 1 in [`accessibility-audit/evals.json`](accessibility-audit/evals.json) with "no browser available". Allowed tools: Read, Grep, Glob, Skill, and `python3`. Each run was graded by hand against the 22 barriers in the [answer key](../examples/demo-site/ANSWER-KEY.md).

| Run | Skill version | Found | Partial | Missed | Notes |
|---|---|---|---|---|---|
| 1 | v1.1.0 draft | 20 | 1 (B13 autocomplete, filed as untested) | 1 (B11 label in name) | Used `contrast.py` for every pair. Overstated the notice as already clipped at default size. |
| 2 | Added "source-only review" checklist | 18 | 3 (B5, B7, B21) | 1 (B11) | Missed the 16×16 social links that run 1 caught; shows run-to-run variance. |
| 3 | Checklist covers label-in-name on role-less elements, declared target sizes, images of text in SVG | **22** | 0 | 0 | One criterion misattribution: cited 2.4.11 alongside 2.4.7 for `outline: none`. |

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

## Not yet run

- Trigger evals (`*/triggers.json`). They need a machine where these skills are not already installed globally; see [README](README.md).
- Behavior evals for the standards, checks, and healthcare skills.

Results vary between runs, so rerun after any change to a skill description or reference that the audit relies on.
