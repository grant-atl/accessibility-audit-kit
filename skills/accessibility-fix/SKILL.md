---
name: accessibility-fix
description: Fix verified accessibility barriers in website or UI component code and design specifications. Use for semantic markup, keyboard/focus behavior, accessible forms and authentication, contrast, responsive layouts, and regression checks while preserving product behavior.
license: MIT
---

# Accessibility fix

Repair the barrier at its shared cause, preserve the user's task, and verify the result. This skill works independently; an audit report is useful but not required.

## Trace, fix, verify

1. Establish the affected task, observed barrier, target and reproduction. Default to WCAG 2.2 AA for engineering unless specified otherwise; include applicable A requirements. Verify a cited criterion against [WCAG 2.2](https://www.w3.org/TR/WCAG22/) when uncertain. Separate required fixes from best-practice/AAA improvements.
2. Read the component, every relevant caller, styles and current tests. Reproduce the affected state when runtime access is available. Reuse an accessible shared primitive or native control before adding custom behavior. For design-only work, update specifications/annotations and state which runtime checks remain.
3. Change the smallest shared implementation that fixes affected uses. Preserve visible design and behavior except where the barrier requires a change. Do not replace components wholesale, add an overlay, or silence scanner rules as a substitute for repair.
4. Re-run the reproduction and affected callers/states. Use existing project checks. Add one focused behavioral regression check for nontrivial interaction or logic where a runnable harness exists; assert names, keyboard actions, focus, states, or error recovery rather than matching markup strings. If the environment cannot run a needed test, state that plainly and give the exact manual acceptance check.
5. Report the change, evidence of verification, and remaining gaps. Do not claim an entire product conforms because the changed component passes.

## Choose a reliable implementation

- **Names and semantics:** use native buttons for actions and anchors with destinations for navigation. Associate visible labels with form controls; use fieldsets/legends where grouping matters. Include visible label text in the accessible name. Do not add ARIA that overrides useful native semantics or hides focusable/meaningful content.
- **Keyboard and focus:** preserve logical DOM order; avoid positive tabindex. Use the existing accessible dialog/composite primitive. When custom widgets are necessary, use the corresponding [ARIA Authoring Practices pattern](https://www.w3.org/WAI/ARIA/apg/patterns/) and implement its keyboard behavior, not just roles. Check open/close, tab order, focus return, errors and content removal. Native dialogs still need a name and tested focus behavior.
- **Forms:** keep instructions and errors associated with the correct control, set invalid state only when appropriate, preserve valid entries, and make error recovery reachable. A focused summary or tested announcement strategy should avoid duplicate speech. Do not show every field as invalid before user interaction without reason.
- **Authentication and time:** support password managers, paste/autofill and accessible recovery/MFA mechanisms. Avoid unaided cognitive challenges. Follow applicable timeout extension/alternative requirements and verify exceptions. Do not remove security controls or store sensitive form data persistently to simplify accessibility.
- **Status and toggles:** announce meaningful asynchronous status without stealing focus. A toggle button with `aria-pressed` normally keeps a stable label and changes its state. An action button with changing text, such as “Mute”/“Unmute,” can instead communicate the next action; do not combine patterns inconsistently. Keep actual state and exposed state synchronized. [W3C button pattern](https://www.w3.org/WAI/ARIA/apg/patterns/button/)
- **Visual changes:** measure contrast against actual backgrounds/states. Preserve visible focus and prevent complete obstruction at AA; quantitative Focus Appearance is AAA. Respect target-size spacing/exceptions rather than mechanically inflating all inline links. Preserve zoom, text resizing, reflow and user text spacing. Label optional enhancements honestly.
- **Images, tables and media:** write alternatives for purpose in context; mark genuinely decorative images appropriately. Use headers/relationships for data tables. Supply applicable captions, transcripts and descriptions; do not assume a transcript replaces every media requirement.
- **Design handoff:** specify labels/roles, states, keyboard path, focus placement, responsive behavior, announcements and acceptance checks. A design annotation is intended behavior until the implementation is tested.

For healthcare, retain units, ranges, clinical meaning and equivalent information; never invent medical interpretations. Use synthetic data in tests and private local evidence where needed. Third-party barriers remain part of the affected journey: identify a vendor action or equivalent accessible route rather than claiming first-party fixes resolved an untested embedded flow.

Use available automated checks plus actual keyboard/assistive-technology testing appropriate to the change. Never describe an accessibility-tree inspection as a screen-reader test. Keep missing tests visible in the handoff.
