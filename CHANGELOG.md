# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-10-21

### Added

- `accessibility-auditor` subagent for splitting large audits into parallel, evidence-only slices.
- `contrast.py` in the audit and fix skills: exact WCAG ratios, alpha compositing, threshold verdicts that never round up, and nearest-passing-color suggestions.
- Browser snippets for page inventory, 2.5.8 target size, 1.4.12 text spacing, and 1.4.10 reflow, with a measurement-tools reference.
- `coverage.py --merge` combines subagent slice results into the ledger atomically, rejecting conflicts and formula injection.
- Demo site: a broken clinic booking page with 22 documented barriers, a remediated version, an answer key, and a sample report.
- Headless Chromium regression check that runs every snippet against the demo pages and ten edge-case pages; CI job included.
- Graded end-to-end eval runs in `evals/RESULTS.md`.
- `evals/run_triggers.py` measures skill triggering with all five skills competing, isolated from user-level skills and MCP connectors.
- External validation against W3C's Before and After Demonstration, run in CI as a non-blocking step.
- End-to-end test that the bundled pre-commit hook blocks and allows real commits.
- Complete 86-criterion audit of a live W3C demo page, with its ledger, compared against W3C's own evaluation.
- Matrix guidance for row-by-row card grids (1.3.2), titles shared across a page set (2.4.2), and color-only inline links (1.4.1).
- Hook feedback now states that the edit was saved, so agents do not report a post-edit check as having blocked the write.
- Trigger and behavior evals for every skill in skill-creator format.
- Audit report template and example scope file in `skills/accessibility-audit/assets/`.
- `coverage.py --report` writes a Markdown coverage rollup that names criteria but never locations or evidence.
- Test suite for manifests, skill frontmatter, the WCAG matrix, relative links, evals, contrast math, the ledger utility, and the check runner's trust model.
- GitHub Actions CI on Linux and macOS with Python 3.9 and 3.13.
- `CONTRIBUTING.md`, `SECURITY.md`, and this changelog.

### Changed

- Plugin and marketplace manifests now carry author, homepage, category, keywords, and a shared version.
- Skill descriptions rewritten for more reliable triggering; frontmatter adds `compatibility` and `metadata`.
- README reorganized around installation, usage, the audit workflow, hooks, and limits.
- The audit skill points to the subagent for large scopes and to the report template for written reports.

### Fixed

- Broken Understanding link for 2.5.6 Concurrent Input Mechanisms in the WCAG matrix.

## [1.0.2] - 2026-09-28

### Changed

- Clarified version-specific guidance in the standards skill and web checks.

## [1.0.1] - 2026-09-28

### Fixed

- Hook command works with Claude Code versions that lack hook `args` support.

### Changed

- Clarified that the matrix and coverage utility cover WCAG 2.2 only.

## [1.0.0] - 2026-09-28

### Added

- Initial release: `accessibility-audit`, `accessibility-fix`, `accessibility-standards`, `accessibility-checks`, and `healthcare-accessibility` skills, the WCAG 2.2 coverage ledger utility, the opt-in check runner, and the Claude Code plugin with its `PostToolUse` hook.

[1.1.0]: https://github.com/grant-atl/accessibility-audit-kit/compare/e6ef8bc...v1.1.0
[1.0.2]: https://github.com/grant-atl/accessibility-audit-kit/compare/58e0adb...e6ef8bc
[1.0.1]: https://github.com/grant-atl/accessibility-audit-kit/compare/8f97fa8...58e0adb
[1.0.0]: https://github.com/grant-atl/accessibility-audit-kit/commit/8f97fa8
