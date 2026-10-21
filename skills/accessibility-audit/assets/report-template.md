# Accessibility audit: {{product or scope name}}

> Replace every `{{placeholder}}`. Delete sections that do not apply to a small review, but never delete open coverage gaps.

| | |
|---|---|
| **Scope** | {{site, journey, component, or design frames}} |
| **Target** | WCAG 2.2 Level {{AA}} (A + AA required; AAA reported separately) |
| **Audit dates** | {{YYYY-MM-DD to YYYY-MM-DD}} |
| **Environment** | {{browsers, OS, viewports, assistive technology and versions actually used}} |
| **Coverage** | {{n}} locations × {{n}} states × 86 criteria; {{full inventory / labelled sample}} |
| **Auditor** | {{name or team}} |

## Summary

{{Two to four sentences. Lead with the most consequential verified barrier and who it blocks. State plainly whether target-level coverage is complete. Do not claim conformance or legal compliance.}}

| Target criteria (A/AA) | Count |
|---|---|
| Pass | {{n}} |
| Fail | {{n}} |
| Not applicable | {{n}} |
| Blocked / needs review / not tested | {{n}} |

Supplemental AAA results: {{pass n, fail n, unresolved n}}.

## Findings

Order by task impact, then reach. Priority is local triage, not a WCAG level.

### {{ID}}. {{Short barrier description}}

| | |
|---|---|
| **Priority** | {{P1 blocks a task / P2 major friction / P3 minor}} |
| **Status** | {{Confirmed / Suspected}} |
| **Criterion** | {{1.4.3 Contrast (Minimum), AA}} or "Best practice" |
| **Where** | {{location and state; shared component if known}} |
| **Reach** | {{occurrences inspected, e.g. "all 14 form pages use this field"}} |

**Steps to reproduce**
1. {{step}}

**Observed:** {{what happened, with evidence reference}}

**Impact:** {{who is affected and which task fails}}

**Fix:** {{smallest credible change at the shared cause}}

**Acceptance check:** {{observable test that proves the fix}}

## Coverage and open items

- **Ledger:** {{private path to coverage.csv; summary from `coverage.py --report`}}
- **Not tested or blocked:** {{criteria, states, and reasons, e.g. "VoiceOver on iOS: no device available"}}
- **Excluded from scope:** {{areas and why}}
- **Needs human or specialist review:** {{captions, flash analysis, reading level, user testing}}

A lack of findings in these checks is not proof of conformance.

## Next actions

1. {{Shared fixes first, with owner by discipline}}
2. {{Retest plan}}
3. {{Unresolved testing or access gaps}}

---

*Prepared with the Accessibility Audit Kit. This report is a testing aid, not a legal certification.*
