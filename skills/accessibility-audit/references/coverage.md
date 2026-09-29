# Full-audit coverage

The matrix contains all 86 WCAG 2.2 success criteria: 31 A, 24 AA, 31 AAA. Obsolete 4.1.1 is not an active 2.2 criterion. A full review records each criterion for every in-scope location/state. A criterion can be inapplicable, but it cannot disappear. Legal scope and whole-site conformance require more than completing a spreadsheet.

Also review WCAG's [five conformance requirements](https://www.w3.org/TR/WCAG22/#conformance-reqs): the selected level, full pages, complete processes, accessibility-supported ways of using technologies, and non-interference. Third-party or non-relied-upon content can still interfere through traps, audio, motion or flashes. Record support assumptions and conforming-alternate-version claims explicitly; do not use an alternate version as a blanket excuse for an inaccessible primary journey. WCAG does not recommend requiring AAA for entire sites because some content cannot satisfy all AAA criteria; evaluating all AAA rows still reveals applicable improvements.

## Inventory before testing

Discover routes from the app and sitemap when available; traverse navigation and process steps. Record authenticated roles, locale/direction, viewports, embedded services, downloads and redirects when relevant. Include meaningful states such as menu-open, error, modal, session-warning, and media-playing. Do not brute-force infinite calendar dates or query strings. Identify equivalent templates and explain any intentional sampling; a sample is not an all-pages audit.

Use the browser/platform tools available. Preserve the user's scope and existing credentials without exporting them. If access, rate limits or tooling prevent full coverage, enumerate the remaining locations and test methods. Never shrink the stated scope to make the result appear complete.

Create a local JSON scope file using this structure (replace the example locations and states):

```json
[
  {"location": "https://example.test/", "states": ["desktop-initial", "mobile-menu-open"]},
  {"location": "https://example.test/contact", "states": ["initial", "validation-error"]}
]
```

From this installed skill's directory, use Python 3 (standard library only):

```sh
python3 scripts/coverage.py --scope scope.json --output coverage.csv --target AA
```

This creates every criterion/state row as `not-tested`, including AAA as supplemental under an AA target. It refuses to overwrite an existing ledger. Keep the scope, ledger, screenshots and reports in private working storage by default, outside public version control. They may disclose private URLs or personal data.

## Fill evidence, not guesses

Statuses are `not-tested`, `pass`, `fail`, `not-applicable`, `blocked`, and `needs-review`. A pass/fail needs actual observed evidence; not-applicable needs a specific reason. `blocked` and `needs-review` remain unresolved. Record viewport/browser/OS, assistive technology and versions as relevant; do not invent them. Use the notes field for user impact, fix, retest and private evidence references. Reuse shared evidence only when you have verified the same implementation and context apply, and identify that basis.

For full keyboard testing, traverse the full journey without pointer shortcuts. For VoiceOver, test actual reading/navigation and interactions; list precisely what needs a human when no screen-reader control is available. Inspect both concise control names and meaningful image descriptions, including decorative images and complex chart equivalents. Review document/page titles, language and structure metadata. SEO descriptions, social preview metadata and a preferred minimum font size are not universal WCAG requirements; flag them separately if requested. Text resizing, reflow, spacing, contrast and user overrides still need explicit tests.

Summarize and validate against the same scope file:

```sh
python3 scripts/coverage.py --scope scope.json --summary coverage.csv --target AA
```

The summary rejects dropped/duplicate rows, wrong criterion metadata and completed rows without evidence. It prints totals without printing private locations. Exit 0 means all target-level rows have evidence and are pass/not-applicable; exit 1 means target failures or unresolved rows; exit 2 means invalid input. AAA totals remain visible even when the target is AA. This is a ledger validation, **not a test engine or certification**: it cannot verify that supplied evidence is truthful or that the inventory includes the entire site.

For an “everything” request, do not call the review complete while supplemental AAA rows or any promised human tests are unresolved, even when the AA ledger gate exits 0. Report target conformance evidence and breadth of review separately. Automated project hooks are a regression layer, not a replacement for this ledger or manual/AT evaluation.
