# Contributing

Thanks for helping improve the Accessibility Audit Kit. Issues and pull requests are welcome.

## Ground rules

- **Accuracy over coverage.** Every WCAG statement must match the normative [WCAG 2.2](https://www.w3.org/TR/WCAG22/) text and its Understanding documents. Cite the criterion number and level, and keep AAA separate from AA.
- **Original wording.** Summarize standards in your own words and link the primary source. Do not paste large passages from W3C or other publications.
- **Honest evidence.** Guidance must never let an agent claim a test ran when it did not, or turn a partial review into a conformance claim.
- **Dated legal content.** Changes to `legal-map.md` or the healthcare legal section need an official source link and an updated "last verified" date.
- **No private data.** Never commit audit results, screenshots, session state, health information, or real URLs from authenticated systems.

## Layout

```text
.claude-plugin/      plugin and marketplace manifests
agents/              Claude Code subagents
hooks/               Claude Code hook registration
skills/<name>/       one installable skill per directory
  SKILL.md           instructions and frontmatter
  references/        loaded on demand by the skill
  scripts/           standard-library Python helpers
  assets/            templates and examples
  agents/openai.yaml Codex display metadata
evals/               trigger and behavior evals per skill
examples/demo-site/  broken and fixed demo pages with an answer key
tests/               unittest suite and browser snippet check
```

Keep each skill independently installable: a skill may mention another skill by name, but must not link into another skill's directory. `contrast.py` is therefore duplicated in the audit and fix skills; a test keeps the copies identical.

## Making a change

1. Edit the skill, reference, or script.
2. Run the checks:

   ```sh
   python3 -m unittest discover -s tests -v
   claude plugin validate .
   node tests/browser/check-snippets.mjs   # after changing a browser snippet or the demo site
   ```

   If you change a snippet or a demo page, update the expected results in `examples/demo-site/ANSWER-KEY.md` and `tests/browser/check-snippets.mjs` together. If you change a skill description, rerun its trigger evals (see `evals/README.md`).

3. Add an entry under a new version heading in `CHANGELOG.md`.

Scripts must stay on the Python 3.9+ standard library, make no network calls, and avoid printing locations or evidence that may be private.

## Releasing

1. Bump the version in `.claude-plugin/plugin.json`, both places in `.claude-plugin/marketplace.json`, and `metadata.version` in every `SKILL.md`. The test suite fails if they disagree.
2. Finish the `CHANGELOG.md` entry and its compare link.
3. Tag the release with `claude plugin tag . --push`, which creates `accessibility-audit-kit--v<version>` after checking that the manifests agree, then publish a GitHub release from the changelog entry.
