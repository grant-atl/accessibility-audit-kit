# Security policy

## Reporting a vulnerability

Please report security issues privately through [GitHub's private vulnerability reporting](https://github.com/grant-atl/accessibility-audit-kit/security/advisories/new) rather than a public issue. Include the affected file, the steps to reproduce, and the impact you observed. You should receive an initial response within a week.

## Scope

The parts of this repository that execute code are:

- `skills/accessibility-checks/scripts/checks.py`, which runs a configured project command from Git hooks, CI, or the Claude Code `PostToolUse` hook.
- `skills/accessibility-audit/scripts/coverage.py`, which reads a local scope file and CSV ledger.
- `hooks/hooks.json`, which registers the Claude Code hook.

Reports about these are especially welcome, for example a way for a cloned repository to run a command without a local `trust` record, a way to escape the configured argument array into a shell, or output that leaks private locations or evidence.

## Design guarantees

- Installing the plugin runs no project command. The hook is a no-op until a repository has `"claude": true` in `.accessibility-checks.json` **and** a local trust record that matches the exact configuration.
- Trust records live in the Git directory, are never committed or cloned, and are invalidated by any configuration change.
- Commands run as literal argument arrays with no shell, a bounded timeout, and their own process group.
- Hook feedback discards child output and uses fixed diagnostics.
- Neither script makes network calls or collects telemetry.

A trust record authorizes the configured command and the repository's code with your privileges; it is not a sandbox. Review untrusted branches before enabling automation.
