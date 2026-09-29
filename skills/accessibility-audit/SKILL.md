---
name: accessibility-audit
description: Audit websites, pages, user journeys, UI components, and designs against all WCAG 2.2 criteria. Use for full accessibility audits or focused reviews covering contrast, text resizing, keyboard/focus, screen readers, images, metadata, forms and media. Produce criterion-by-state evidence and developer/designer handoffs, including healthcare.
license: MIT
---

# Accessibility audit

Find barriers that prevent people from completing the requested task. Produce reproducible findings and a practical fix order. Audit the supplied scope; an audit request alone does not request edits, installation, hooks, or publication.

## Establish scope from the request

Identify the URL, page, journey, component, repository, or design frames. Use available context before asking for missing access. Default to **WCAG 2.2 Level AA** as an engineering target unless the user specifies another target. AA includes applicable A criteria. Keep legal requirements separate; verify a law's scope, incorporated version, and current dates from official sources before giving compliance guidance. WCAG 3 is draft work, not a replacement compliance target.

Choose the evidence available:

| Input | Inspect | State the limit |
|---|---|---|
| Live site or running app | Rendered states, semantics, navigation, keyboard, layout, existing automated tools | Unvisited states and unavailable assistive technologies remain untested |
| Component or source | Shared implementation, callers, styles, tests; render in its real context if possible | Source alone does not prove runtime focus, layout, or assistive-technology behavior |
| Figma or other design file | Actual layers, tokens, variants, prototypes, annotations when tools are available | Design intent does not prove DOM semantics or implemented keyboard behavior |
| Screenshot | Visible labels, content, hierarchy, contrast candidates, layout | Pixels cannot establish accessible names, reading order, keyboard behavior, CSS target sizes, or conformance |

For a **full WCAG 2.2 audit**, read the complete [86-criterion matrix](references/wcag-22-matrix.md) and [coverage workflow](references/coverage.md). Evaluate all applicable A/AA criteria plus a separately labeled AAA review unless the user limits the levels. Review every matrix row; do not silently select only easy or automated checks. For focused requests, narrow locations/states as requested and identify the resulting coverage limit.

For another requested WCAG version, use that version's official criteria and a separate local evidence ledger. The bundled matrix and CSV utility cover **2.2 only**; do not label their output as a 2.0/2.1 evaluation or silently add later-version obligations. Include 4.1.1 in an earlier-version crosswalk where the applicable policy requires it, checking its current W3C guidance. Report optional 2.2 improvements separately.

Read [web-checks.md](references/web-checks.md) for live or source testing, [design-review.md](references/design-review.md) for design inputs, and [healthcare.md](references/healthcare.md) for patient or clinical services. These practical guides supplement the full matrix.

## Inspect the real experience

1. **Inventory the scope.** For a full site audit, combine routes/source, sitemaps, navigation and user journeys to inventory reachable in-scope pages, roles, locales, responsive views and meaningful states. Include alternate templates, errors, documents and third-party steps. Reconcile discovered links against the inventory; keep inaccessible/unvisited areas visible. Bound calendars, query permutations and personalized data without silently claiming exhaustive coverage. If only a sample is feasible, label the result partial and continue remaining coverage when access permits. For a component, include variants and surrounding context rather than expanding to the entire site. Follow the coverage workflow to create a criterion-by-state ledger.
2. **Use the tools already available.** Prefer the project's test commands, browser tools, accessibility tree, and scanner. If tools or credentials are unavailable, continue with supported inspection and clearly list what could not run. Do not claim an axe scan, screen-reader test, or measurement happened unless it did. Add dependencies only when authorized and needed; a scanner is not required to find an obvious barrier.
3. **Exercise states.** Check initial, expanded/open, validation error, loading, empty, success, and disabled states when relevant. Traverse the entire in-scope journey using keyboard alone; inspect focus outlines, order, traps, visibility, obstruction and return. Test VoiceOver or the supported screen reader when available, including names, descriptions, reading order, rotor/headings, control states, errors and announcements. A scripted mouse click or accessibility-tree snapshot is not a keyboard or screen-reader test. Use test accounts and synthetic data. Avoid real purchases, appointments, messages, consent, deletions, or other consequential submissions without authorization.
4. **Connect evidence to impact.** Record location, state, reproduction, observed behavior, affected task, and applicable criterion. Verify criterion numbers and levels against [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) or its linked Understanding pages when uncertain. Distinguish confirmed failures from suspected issues, incomplete automated results, and recommended improvements. A scanner severity is evidence, not the final task priority.
5. **Group root causes.** One shared field or dialog bug may affect many pages. Report the shared defect with representative occurrences and describe the reach actually inspected. Prioritize task blockers, safety/privacy risks, and frequent interactions before isolated friction. These priorities are local triage labels, not WCAG levels.

Use the [W3C evaluation guidance](https://www.w3.org/WAI/test-evaluate/) for broader audits. Plan disability-inclusive user testing when the scope warrants it; never imply a model substitutes for participants or assistive technology.

## Return an actionable audit

Lead with the most consequential verified barrier. Keep a small review short; for a larger audit use this structure:

- **Scope and evidence:** pages/frames/files, journey states, target, date, browser/viewport/tools actually used, and sampled or excluded areas.
- **Findings:** ID; task priority; confirmed/suspected status; location and state; reproduction; observed barrier and user impact; WCAG criterion and level or “best practice”; smallest credible fix; acceptance check.
- **Coverage:** criterion-by-state ledger with pass, fail, not-applicable (reason), not-tested, blocked or needs-review; include evidence and test environment. Report A/AA coverage separately from AAA. Unperformed manual/AT checks remain open. A lack of findings is not proof of conformance.
- **Next actions:** shared fixes first, owners by discipline if useful, then explicit unresolved testing or access gaps.

For developers, identify the shared source component and affected callers when available. For designers, specify the visual/interaction change plus implementation annotations needed. Link evidence without copying unnecessary page content. Keep authenticated URLs, session data, health records, raw DOM, and screenshots containing personal information out of public reports; use sanitized summaries and private artifacts only when needed. Accessible alternatives must preserve information needed for equivalent use.

Report “no issues found in these checks” when appropriate. Never convert a scanner score, design review, component pass, or sampled audit into a legal certification or whole-product WCAG claim.
