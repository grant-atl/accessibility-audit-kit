# Configure a project check

The runner needs Python 3.9+, Git, and macOS, Linux, or WSL. It uses only Python's standard library. Your accessibility test tools must already be installed and configured.

In the project's Git root, create `.accessibility-checks.json` using the bundled example:

```json
{
  "command": ["npm", "run", "test:a11y"],
  "timeout_seconds": 30,
  "claude": false
}
```

Replace the example command with an existing, noninteractive check that exits nonzero on failures. Arguments are literal strings, with no shell expansion. For multiple checks, use the project's existing test script. Timeout is an integer from 1 to 120 seconds. Unknown keys, shell-string commands, and symlinked config files are rejected. Configuration belongs at the Git root; monorepos can select a package through command arguments. The runner starts there even when called from a subdirectory.

Run from an installed skill, or vendor its single `scripts/checks.py` file into your project as `scripts/accessibility-checks.py`. In these examples that copy is used:

```sh
python3 scripts/accessibility-checks.py run
```

The explicit run streams the configured tool's output and preserves its nonzero status. Missing config, unavailable executables, and timeouts fail. A zero result says only that this command passed. Untested manual and assistive-technology coverage stays pending; no hook result certifies full WCAG conformance. Use test data, review your tool's output handling, and avoid secrets, private URLs, real user data, and authenticated screenshots in published reports or CI logs.

## Git pre-commit

Inspect `git config --show-origin --get core.hooksPath` and existing hooks first. If the project has a hook manager, add the runner invocation to that manager. Otherwise put the bundled `assets/pre-commit` in `.githooks/pre-commit`, make it executable, and opt this clone in:

```sh
chmod +x .githooks/pre-commit
git config --local core.hooksPath .githooks
```

Use that setting only when it does not replace an existing hook path. The wrapper expects the vendored runner at `scripts/accessibility-checks.py`. Git's pre-commit hook runs from the working-tree root and a nonzero exit rejects the commit. See [Git's hook documentation](https://git-scm.com/docs/githooks).

This check reads the **working tree**, not an isolated staged snapshot. Unstaged fixes can mask a broken staged commit. Avoid partial staging for the affected tests, and keep CI checks on the checked-out commit as the merge gate. Local hooks can be bypassed; configure branch protection separately if required. Removing the invocation disables this check; restore the previous `core.hooksPath` if you changed it.

## Continuous integration

Add [the bundled step](../assets/github-actions-step.yml) to the project's existing workflow after normal runtime/dependency/browser/server setup. Ensure `python3`, Git, the vendored runner, and `.accessibility-checks.json` are present. The runner itself installs nothing and does not start the application. Use the same command locally and in CI; make test readiness part of that command. Use your normal trusted workflow and minimal permissions, without publishing screenshots or logs containing private content.

## Claude Code feedback hook

The full library's plugin includes an optional `PostToolUse` hook. Install it using the repository's root instructions. The hook uses `python3` on `PATH`; installing the plugin alone starts no accessibility command. A missing config or trust record is a silent no-op.

After reviewing the command and trusting the repository/toolchain, set `"claude": true` in the config and explicitly enable it for this working tree:

```sh
python3 scripts/accessibility-checks.py trust
```

The trust digest lives in local Git metadata and binds the exact configuration and resolved working-tree root. It is not committed or cloned. Each worktree needs its own trust. Changed config requires review and another `trust` invocation. To disable:

```sh
python3 scripts/accessibility-checks.py revoke
```

Setting `"claude": false` also disables automatic checks. A trust record authorizes the command and its repository code, **not a sandbox**: changes to package scripts, dependencies, executables, and test files can change what the command does. Review untrusted branches before enabling automation. The child inherits your environment; choose a check with no unwanted network or write effects.

The hook uses the JSON event's `cwd`, respects the edited file's project boundary, never reads transcripts, and discards child stdout/stderr. On failure it returns exit 2 with a fixed diagnostic; rerun the explicit command locally for details. The timeout terminates the check's ordinary POSIX process group. Processes that deliberately detach are outside that boundary.

`PostToolUse` feedback cannot undo or block an edit already made. The matcher covers Claude's `Edit`/`Write`, not edits made through shell commands, external editors, or other tools. Git/CI checks cover the final working tree/commit independently. The plugin uses the documented direct-execution `command`/`args` format with `${CLAUDE_PLUGIN_ROOT}`; use a current Claude Code version and verify it under `/hooks`. See the official [hook reference](https://code.claude.com/docs/en/hooks), [plugin manifest reference](https://code.claude.com/docs/en/plugins-reference), and [marketplace instructions](https://code.claude.com/docs/en/plugin-marketplaces).
