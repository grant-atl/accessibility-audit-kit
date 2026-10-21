# Accessibility Audit Kit

[![CI](https://github.com/grant-atl/accessibility-audit-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/grant-atl/accessibility-audit-kit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![WCAG 2.2](https://img.shields.io/badge/WCAG-2.2-5b2a86.svg)](https://www.w3.org/TR/WCAG22/)

Evidence-based accessibility audits for AI coding agents. The kit gives Claude Code, Codex, and other Agent Skills–compatible agents a disciplined way to audit websites, components, and design files against **all 86 WCAG 2.2 success criteria**, fix what they find, and keep it fixed.

Every audit produces a criterion-by-state evidence ledger. Pass, fail, not-applicable, blocked, needs-review, and not-tested stay separate, so a scanner score or a sampled page can never pass for a full audit.

- [What's inside](#whats-inside)
- [Try it in five minutes](#try-it-in-five-minutes)
- [Install](#install)
- [Usage](#usage)
- [How a full audit works](#how-a-full-audit-works)
- [Regression checks and hooks](#regression-checks-and-hooks)
- [Limits](#limits)
- [Privacy and sources](#privacy-and-sources)
- [Development](#development)

## What's inside

| Skill | Use it for |
|---|---|
| [`accessibility-audit`](skills/accessibility-audit/SKILL.md) | Full-site or focused reviews of pages, journeys, components, and designs, with a complete criterion matrix, evidence ledger, report template, and developer/designer handoff |
| [`accessibility-fix`](skills/accessibility-fix/SKILL.md) | Repairing verified barriers in shared code or design specifications and checking every affected caller |
| [`accessibility-standards`](skills/accessibility-standards/SKILL.md) | Choosing a WCAG target, interpreting criteria, and mapping ADA, Section 508/504, EN 301 549, and EAA requirements against current sources |
| [`accessibility-checks`](skills/accessibility-checks/SKILL.md) | Turning verified requirements into repeatable checks, with optional Git, CI, and Claude Code hooks |
| [`healthcare-accessibility`](skills/healthcare-accessibility/SKILL.md) | Specialist reviews of patient journeys, telehealth, clinical results, consent, records, and privacy |

The Claude Code plugin adds:

| Component | Purpose |
|---|---|
| [`accessibility-auditor` subagent](agents/accessibility-auditor.md) | Tests one slice of a large audit scope and returns ledger rows and findings, so full-site audits can run in parallel |
| [`PostToolUse` hook](hooks/hooks.json) | Opt-in feedback from your project's own accessibility check after Claude edits a file in a trusted working tree |

Measurement and evidence tools. They make no network calls, have no dependencies, and are covered by tests:

| Tool | What it does |
|---|---|
| [`contrast.py`](skills/accessibility-audit/scripts/contrast.py) | Exact WCAG contrast ratios with alpha compositing, AA/AAA/non-text verdicts, and the nearest passing color with `--target` |
| [`coverage.py`](skills/accessibility-audit/scripts/coverage.py) | Creates, merges, validates, and summarizes the criterion-by-state evidence ledger |
| [Browser snippets](skills/accessibility-audit/references/measurement-tools.md#browser-snippets) | Page inventory, 2.5.8 target size with the spacing exception, 1.4.12 text spacing, and 1.4.10 reflow, as JSON from any browser console or agent JavaScript tool |
| [`checks.py`](skills/accessibility-checks/scripts/checks.py) | Runs one reviewed project check command for Git hooks, CI, or Claude Code |

## Try it in five minutes

The repository includes a [deliberately broken clinic booking page](examples/demo-site/broken.html) with 22 documented barriers, a [remediated version](examples/demo-site/fixed.html), and an [answer key](examples/demo-site/ANSWER-KEY.md). From a clone:

```sh
python3 skills/accessibility-audit/scripts/contrast.py "#a0a0a0" "#ffffff" --target 4.5
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/examples/demo-site/broken.html` and paste any snippet from `skills/accessibility-audit/assets/browser/` into the console. Or ask your agent:

```text
Use accessibility-audit to audit examples/demo-site/broken.html for WCAG 2.2 AA.
```

Then compare its findings with the answer key. See a [sample audit report](examples/sample-report.md) produced this way.

## Install

### Claude Code plugin (recommended for Claude)

```sh
claude plugin marketplace add grant-atl/accessibility-audit-kit
claude plugin install accessibility-audit-kit@accessibility-audit-kit
```

This installs all five skills, the auditor subagent, and the hook adapter. Skills are namespaced, for example `/accessibility-audit-kit:accessibility-audit`. Installing the plugin runs nothing on its own; the hook stays silent until you opt a repository in.

### Agent Skills CLI (Codex, Claude Code, and others)

```sh
npx skills add grant-atl/accessibility-audit-kit
```

Pick agents and skills interactively, or install all five globally for Codex and Claude Code:

```sh
npx skills add grant-atl/accessibility-audit-kit --skill '*' -a codex -a claude-code -g
```

Each directory under `skills/` installs independently. If you use both methods for Claude, you will get duplicate skills; choose one.

**Requirements:** no API keys, MCP servers, paid services, or scanners are bundled. Live inspection uses whatever browser, design, and assistive-technology tools your agent already has. `coverage.py` needs Python 3.9+. Hook integration needs Python 3.9+, Git, and macOS, Linux, or WSL.

## Usage

Start a full audit:

```text
Use accessibility-audit for a full audit of this site. Inventory every in-scope
page and meaningful state. Review all 86 WCAG 2.2 criteria, target AA, include
AAA findings separately, and produce the evidence ledger and a written report.
Test contrast, text resizing and reflow, keyboard and focus, VoiceOver, alt text,
titles and language, forms, and complete journeys. Keep blocked and untested
checks visible.
```

More examples:

```text
Use accessibility-audit to review these Figma frames and component variants.
Give me design fixes, implementation annotations, and checks that need runtime testing.

Use accessibility-fix to fix these verified dialog and form errors, then retest.

Use accessibility-standards to map the standards that apply to a public hospital.

Use healthcare-accessibility to audit this patient portal from booking through
telehealth, results, and follow-up, including documents and vendor steps.

Use accessibility-checks to connect our existing test:a11y command to Git,
CI, and Claude Code. Preserve the existing hook setup.
```

In Codex, refer to skills with `$`, for example `$accessibility-audit`.

## How a full audit works

1. **Inventory.** The agent lists every in-scope location and meaningful state (menu open, validation error, modal, session warning) in a scope file. See the [example scope](skills/accessibility-audit/assets/scope.example.json).
2. **Generate the ledger.** `coverage.py` creates one `not-tested` row for every location × state × criterion.

   ```sh
   python3 scripts/coverage.py --scope scope.json --output coverage.csv --target AA
   ```

3. **Test and record evidence.** Each row needs observed evidence for `pass` or `fail` and a specific reason for `not-applicable`. The [86-criterion matrix](skills/accessibility-audit/references/wcag-22-matrix.md) gives a test prompt and evidence method for every criterion, and the [measurement tools](skills/accessibility-audit/references/measurement-tools.md) turn estimates into numbers. Large scopes can be split across `accessibility-auditor` subagents, whose results merge back into one ledger:

   ```sh
   python3 scripts/coverage.py --scope scope.json --target AA --merge coverage.csv --input slice-*.csv
   ```
4. **Validate and summarize.** The summary rejects dropped rows, wrong metadata, and completed rows without evidence. `--report` writes a Markdown rollup for the report's coverage section; it names criteria, never locations or evidence.

   ```sh
   python3 scripts/coverage.py --scope scope.json --summary coverage.csv --target AA --report coverage-summary.md
   ```

   Exit 0 means every target-level row is pass or not-applicable with evidence; 1 means failures or unresolved rows remain; 2 means invalid input.
5. **Report.** The [report template](skills/accessibility-audit/assets/report-template.md) structures findings by task impact, with reproduction steps, criterion, fix, and acceptance check for each.

The [coverage workflow](skills/accessibility-audit/references/coverage.md) has the full details. Audits against WCAG 2.0 or 2.1 use that version's official criteria in a separate ledger; the bundled matrix and generator are 2.2 only.

## Regression checks and hooks

The `accessibility-checks` skill wires an **existing** project check (for example `npm run test:a11y`) into:

- a Git pre-commit hook ([template](skills/accessibility-checks/assets/pre-commit)),
- a CI step ([template](skills/accessibility-checks/assets/github-actions-step.yml)),
- Claude Code feedback after `Edit` and `Write`, through the plugin's hook.

Configuration lives in `.accessibility-checks.json` at the Git root. The command is a literal argument array with no shell expansion and a timeout of at most 120 seconds. Claude automation is opt-in per working tree: it needs `"claude": true` in the config **and** a local `checks.py trust` record that binds the exact config. Cloned configs cannot authorize themselves, and any config change requires trusting again. Hook feedback omits child output; run the check directly to see details.

Follow [project setup](skills/accessibility-checks/references/setup.md) for the full procedure. No global hooks are changed automatically.

## Limits

- **Not everything can be automated.** Keyboard operation, screen-reader output, reading order, captions, and many content criteria need a person or a real assistive technology. Source code, screenshots, and accessibility trees cannot prove spoken output or runtime behavior.
- **No certification.** A clean ledger, scanner score, or component pass is not a legal certification or a whole-product WCAG claim.
- **Levels stay separate.** AA includes A. AAA results are reported as supplemental, never as AA failures.
- **Not every best practice is a requirement.** WCAG has no minimum font size and no SEO or social-metadata rules. The skills keep those separate from required text resizing, contrast, reflow, page titles, language, and semantics.

## Privacy and sources

Use synthetic data and private local evidence for authenticated sites. Keep health records, session state, private URLs, raw DOM, and screenshots with personal information out of public repositories and reports. The kit has no telemetry and no upload service. Your agent and your configured project commands keep their own data handling, so review them before enabling hooks.

Guidance is original and grounded in primary sources: [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/), the [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/), and [W3C evaluation guidance](https://www.w3.org/WAI/test-evaluate/). The dated legal map must be rechecked for current questions. This is a testing aid, not legal or medical advice.

## Development

```sh
python3 -m unittest discover -s tests -v
claude plugin validate .
npm install --no-save playwright@1.49.1 && npx playwright install chromium
node tests/browser/check-snippets.mjs
```

The Python suite covers manifests and version agreement, skill frontmatter, the matrix (86 rows, 31 A / 24 AA / 31 AAA), relative links, evals, the contrast math, the ledger utility, and the check runner's trust model. The browser check runs every snippet against both demo pages at desktop and 320 px widths, compares the results with the answer key, and covers ten known edge cases such as app shells, custom checkboxes, and off-screen skip links. CI runs both on every push. Trigger and behavior [evals](evals/README.md) for each skill use the skill-creator format; the latest graded runs are in [evals/RESULTS.md](evals/RESULTS.md). In the most recent source-only run, the audit skill found all 22 planted barriers in the demo page. See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions and the release process, [SECURITY.md](SECURITY.md) to report a vulnerability, and [CHANGELOG.md](CHANGELOG.md) for history.

MIT licensed. Third-party standards remain under their own terms.
