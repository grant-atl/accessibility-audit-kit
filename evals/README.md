# Evals

Two kinds of evaluation per skill, in the format used by Anthropic's `skill-creator` plugin. They live outside `skills/` so they are not installed with the skills.

| File | Purpose |
|---|---|
| `<skill>/triggers.json` | Prompts that should and should not activate the skill. Negatives are deliberate near-misses that belong to a sibling skill or an unrelated task, so the descriptions stay distinct. |
| `<skill>/evals.json` | Tasks with checkable expectations. Several use the [demo site](../examples/demo-site/ANSWER-KEY.md), so results can be graded against known barriers. |

## Run trigger evals

`run_triggers.py` loads the whole plugin into headless Claude Code, so all five skills compete for every query, as they would in real use. It excludes user-level settings and skills (`--setting-sources project,local`) and MCP servers (`--strict-mcp-config`), so globally installed copies and connectors cannot interfere. Each query runs in an empty temporary directory, limited to the Skill and Read tools, and stops at the first Skill call:

```sh
python3 evals/run_triggers.py --runs 2 --workers 6
```

A query passes when its trigger rate is on the correct side of 0.5. A negative passes when a sibling skill or no skill is chosen. To tune a single description in isolation, Anthropic's skill-creator plugin also accepts these files (`scripts/run_eval.py --eval-set ... --skill-path ...`).

## Run behavior evals

Load the plugin from the repository and give a headless session each prompt:

```sh
claude -p --setting-sources project,local --plugin-dir . "Use the accessibility-audit-kit:accessibility-audit skill. <prompt from evals.json>"
```

Grade the output against `expectations`. Fixtures for the checks and healthcare evals are in [`files/`](files). For demo-site evals, also compare against [ANSWER-KEY.md](../examples/demo-site/ANSWER-KEY.md). Remove `ANSWER-KEY.md` and `fixed.html` from the working copy first so the agent cannot read the answers.

## What a good result looks like

- Finds most planted barriers from source alone and names the criterion and level correctly.
- Uses the bundled tools for measurements instead of estimating.
- Lists keyboard, screen-reader, and visual checks it could not perform, instead of passing them.
- Never claims conformance or certification.
