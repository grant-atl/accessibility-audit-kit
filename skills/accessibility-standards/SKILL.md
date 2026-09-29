---
name: accessibility-standards
description: Select and explain accessibility standards, WCAG versions and success criteria, or map jurisdiction and procurement requirements to an engineering target. Use for standards questions and audit scoping; not as a substitute for testing a site or implementing fixes.
license: MIT
---

# Accessibility standards

Help developers and designers choose a precise target and interpret requirements. Keep technical conformance, legal applicability, and usability recommendations distinct.

## Select the target

- Respect a supplied version, level, contract, or policy. If none is specified, use **WCAG 2.2 Level AA** as the engineering default and identify it as a recommendation, not a universal legal requirement. AA includes all applicable A and AA criteria.
- Identify the surface: web page/component, complete web process, native software, document, authoring tool, or broader ICT. A component review supports a page audit; it cannot establish whole-page or whole-process conformance.
- Ask for missing jurisdiction, public/private entity status, funding, or procurement context only when it affects the requested legal mapping. Continue explaining the technical target with stated assumptions.
- For jurisdiction, compliance deadlines, or procurement questions, read [references/legal-map.md](references/legal-map.md), then verify the relevant current official sources. Treat its dated entries as orientation. If live verification is unavailable, label the mapping provisional and omit an asserted current deadline.

## Interpret accurately

Use the normative text and Understanding documents for the selected WCAG version. For the default 2.2 target, use the [normative WCAG 2.2 text](https://www.w3.org/TR/WCAG22/) for the requirement and its exceptions, and the [Understanding documents](https://www.w3.org/WAI/WCAG22/Understanding/) for explanation. Cite the exact criterion and level. Techniques, ARIA patterns, and design recommendations explain possible solutions; they do not create extra success criteria.

The following boundaries describe WCAG 2.2; check criterion availability in the selected version before applying them:

- **Focus:** 2.4.7 requires visible keyboard focus (AA); 2.4.11 addresses a focused component being completely hidden by author-created content (AA). Full visibility under 2.4.12 and the quantitative indicator rules under 2.4.13 are AAA. A stronger design target can be recommended with that label.
- **Target size:** 2.5.8 is AA and uses 24 by 24 CSS pixels with spacing and other exceptions. The 44 by 44 criterion, 2.5.5, is AAA. Do not report every smaller target as an automatic failure.
- **Dragging:** 2.5.7 requires a single-pointer alternative unless an exception applies. A keyboard alternative alone does not satisfy that particular criterion.
- **Authentication:** 3.3.8 (AA) permits defined alternatives or assistance and specific exceptions. Do not characterize all passwords, MFA, or CAPTCHAs as categorically prohibited; examine the actual step and available assistance.
- **Versions:** WCAG 2.2 removes 4.1.1 Parsing. An earlier incorporated standard may still require reporting it; check the applicable policy. Broken semantics can fail other criteria regardless.
- **Conformance:** complete web processes are already required in WCAG 2. A passing scanner, selected component, or sampled page set cannot by itself establish product-wide conformance.
- **Drafts:** WCAG 3 is work in progress, not the production baseline. Do not convert proposed harm categories, reporting tiers, or experimental contrast methods into WCAG 2 AA obligations.

For native software or documents, consult [WCAG2ICT](https://www.w3.org/TR/wcag2ict/) and the applicable platform or ICT standard; WCAG2ICT is informative guidance. For custom web controls, consult the [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/) while preferring suitable native semantics. [WCAG-EM](https://www.w3.org/TR/wcag-em-2/) is an informative evaluation methodology, not an additional conformance standard.

## Deliver the decision

Give the selected engineering target, the relevant criterion/version/level, and the reason. For a legal crosswalk, add the potentially applicable rule, the facts needed to confirm coverage, the exact source, and the verification date. Label an unresolved applicability question rather than certifying legal compliance.

Explain what evidence an audit would need when useful, but do not claim tests ran. Distinguish a proven criterion failure from a usability concern or a recommendation above the chosen level. Keep the answer to the user's component, page, process, or jurisdiction; do not expand it into an unrelated audit or code change.
