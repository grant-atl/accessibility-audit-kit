# Accessibility Audit Kit

An installable skill library for developers and designers auditing websites, pages, components, and design files. Full audits track **all 86 WCAG 2.2 criteria** against each in-scope page and state, with AA requirements and supplemental AAA checks clearly separated.

It covers contrast, font/text resizing, reflow, text spacing, keyboard navigation and focus, VoiceOver and other screen readers, image alternatives, page titles and language, forms, authentication, media, timing, mobile interaction, and complete user journeys. Healthcare guidance is available when relevant.

| Skill | Use it for |
|---|---|
| `accessibility-audit` | Full-site or focused reviews, a complete criterion matrix, evidence ledger, design review and developer handoff |
| `accessibility-fix` | Repairing verified barriers in shared code or design specifications and checking affected callers |
| `accessibility-standards` | Understanding criteria, choosing standards, and checking legal/procurement mappings against current sources |
| `accessibility-checks` | Configuring repeatable checks with optional Git, CI and Claude Code hooks |
| `healthcare-accessibility` | Specialist reviews of patient journeys, telehealth, clinical results, consent, records and privacy |

## Install the skills

With Node.js/npm available, use the [Agent Skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add grant-atl/accessibility-audit-kit
```

Choose your agent and skills interactively. To install all five globally for Codex and Claude Code:

```sh
npx skills add grant-atl/accessibility-audit-kit --skill '*' -a codex -a claude-code -g
```

Each directory under `skills/` is independently installable. No paid service, API key, MCP server, or scanner dependency is bundled. Actual browser/design inspection uses tools available to your agent and project. The coverage utility needs Python 3; hook integration needs Python 3.9+, Git, and macOS/Linux/WSL. Installing skills does not install hooks or run audits.

## Use it

In Codex, start with:

```text
Use $accessibility-audit for a full audit of this site. Inventory every in-scope
page and meaningful state. Review all 86 WCAG 2.2 criteria, target AA, include
AAA findings separately, and produce the evidence ledger. Test contrast,
text resizing/reflow, keyboard/focus, VoiceOver, alt text, titles/language,
forms and complete journeys. Keep blocked and unperformed checks visible.
```

Other examples:

```text
Use accessibility-audit to review these Figma frames and component variants.
Give me design fixes, implementation annotations, and checks needing runtime testing.

Use accessibility-fix to fix these verified dialog and form errors, then retest.

Use accessibility-standards to map this public hospital's applicable standards.

Use healthcare-accessibility to audit this patient portal from booking through
telehealth, results and follow-up, including documents and vendor steps.

Use accessibility-checks to connect our existing test:a11y command to Git,
CI and Claude Code. Preserve the existing hook setup.
```

The [full coverage workflow](skills/accessibility-audit/references/coverage.md) includes a standard-library script that creates and validates the criterion-by-state CSV ledger. The [complete matrix](skills/accessibility-audit/references/wcag-22-matrix.md) supplies a test prompt and evidence method for every criterion.

For patient services, use the dedicated [healthcare skill](skills/healthcare-accessibility/SKILL.md) alongside the audit workflow. It adds clinical communication, document production, health literacy, privacy and vendor checks without changing the applicable WCAG target.

## Optional Claude Code plugin and hooks

The plugin installs the same skills plus the hook adapter. If you already installed the skills for Claude through the CLI, choose one installation method to avoid duplicate skills. Codex can retain its separate skill installation.

```sh
claude plugin marketplace add grant-atl/accessibility-audit-kit
claude plugin install accessibility-audit-kit@accessibility-audit-kit
```

In Claude Code, invoke the namespaced skill, for example `/accessibility-audit-kit:accessibility-audit`.

Follow [project setup](skills/accessibility-checks/references/setup.md) to configure an existing check command. Automatic Claude checks are opt-in for each trusted Git working tree. They require `claude: true` in the project config plus explicit local trust; installing the plugin alone does not execute the configured test command. Edit/Write hooks provide feedback after edits. Git and CI can gate changes; neither substitutes for manual testing. Git hooks check the working tree, so CI should check the committed revision.

Git and CI templates are included in the checks skill. No global hooks are changed automatically. The runner executes a reviewed argument array without shell expansion, enforces a timeout, and returns failure when an explicit check cannot run. Claude feedback omits child output; explicit local/CI checks show the configured tool's output.

## What a complete audit means

All criteria are considered; irrelevant ones need a reason. Every promised page/state and manual/assistive-technology check stays visible until resolved. A full-site request is not silently reduced to a sample. A component or screenshot review is identified as such.

This library does **not** pretend every requirement can be tested automatically. It records pass, fail, not-applicable, blocked, needs-review and not-tested separately. Actual VoiceOver testing requires an available screen reader and usable controls or a human tester. Source code, screenshots and accessibility trees cannot prove spoken output or full runtime behavior. No agent tool can honestly certify a whole site from a scanner score.

WCAG has no universal minimum font size or requirement for SEO/social metadata. The skills distinguish those design concerns from required text resizing, contrast, reflow, page titles, language and semantic relationships. AA includes A requirements; AAA improvements are labeled rather than misreported as AA failures.

## Privacy and sources

Use synthetic data and local/private evidence for authenticated sites. Keep health records, session state, private URLs, raw DOM and screenshots with personal information out of public repositories and reports. No telemetry or upload service is included. Your agent and configured project commands retain their own data-handling behavior; review them before enabling hooks.

The instructions are original practical guidance derived from accessibility research and linked primary sources, led by [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/), [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/), and [W3C evaluation guidance](https://www.w3.org/WAI/test-evaluate/). The dated legal reference must be rechecked for current questions. This is a testing aid, not a legal certification or medical advice.

The repository contains only distributable skills, references, runtime helpers, install instructions, hook templates and plugin manifests. It does not include private research files, audit results, browser sessions or development fixtures. MIT licensed; third-party standards remain under their respective terms.
