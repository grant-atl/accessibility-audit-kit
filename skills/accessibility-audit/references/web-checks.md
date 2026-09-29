# Web and component checks

Use the rows relevant to the actual scope. For a formal AA evaluation, assess all applicable A/AA success criteria in the [normative WCAG 2.2 reference](https://www.w3.org/TR/WCAG22/); this shortlist is not a substitute. Include the complete user process and document technology/support assumptions.

| Area | What to inspect and exercise | Useful criteria |
|---|---|---|
| Semantics and navigation | Page title/language, headings, landmarks, skip mechanism, reading order, table header relationships, meaningful links | 1.3.1, 1.3.2, 2.4.1–2.4.6, 3.1.1–3.1.2 |
| Controls | Correct role and name, visible label included in accessible name, states updated, real button/link/input semantics | 2.5.3, 4.1.2 |
| Keyboard and focus | Tab/Shift+Tab order, Enter/Space activation as appropriate, composite-widget keys, no trap, visible focus, overlays/sticky regions, focus on open/close and after DOM changes | 2.1.1–2.1.2, 2.4.3, 2.4.7, 2.4.11 |
| Forms | Visible labels/instructions, related groups, appropriate autocomplete, required/error meaning, helpful correction, preserved data, repeat-entry behavior, consequential review/correction | 1.3.5, 3.3.1–3.3.4, 3.3.7 |
| Authentication | Password managers, paste/autofill, OTP, recovery and accessible alternatives; no unavoidable unaided memory/puzzle task | 3.3.8 |
| Updates | Loading, validation, search results, successful actions and status available without relying on color or unexpected focus changes | 1.4.1, 4.1.3 |
| Visual presentation | Text and non-text contrast, color-independent meaning, text resize, reflow, text spacing, hover/focus disclosures | 1.4.1, 1.4.3–1.4.5, 1.4.10–1.4.13 |
| Pointer and mobile | Target size/spacing, alternative to dragging or complex gestures, cancellation, orientation, motion alternatives | 1.3.4, 2.5.1–2.5.4, 2.5.7–2.5.8 |
| Time, movement and media | Applicable timeout alternatives/extensions, pause/stop controls, flashes, text alternatives, captions and audio description | 1.1.1, applicable 1.2.x, 2.2.1–2.2.2, 2.3.1 |
| Consistency | Repeated navigation, identification, help, predictable focus/input behavior | 3.2.1–3.2.4, 3.2.6 |

## Measurements that are easy to misreport

- Text contrast generally needs 4.5:1, or 3:1 for large text (at least 18pt regular or 14pt bold). Examine actual foreground, background, opacity, and states. Certain text has defined exceptions. Non-text contrast under 1.4.11 has its own scope and exceptions. Do not measure antialiased edge pixels as the text color.
- Test 200% text resizing. Test reflow at a width equivalent to 320 CSS pixels for horizontally written content, typically a 1280 CSS-pixel viewport at 400% zoom. Preserve functionality; note essential two-dimensional layout exceptions such as some tables/maps. A small screenshot does not demonstrate browser zoom support.
- Apply user text spacing: line height 1.5 times font size, paragraph spacing 2 times, letter spacing 0.12 times, word spacing 0.16 times. Check for lost or clipped content/functionality.
- Under 2.4.11 AA, author-created content must not **completely** hide the focused component. Fully visible focus (2.4.12) and the additional measurable Focus Appearance requirements (2.4.13) are AAA. Check AA Focus Visible separately.
- Under 2.5.8 AA, use 24×24 CSS pixels **or a qualifying exception**. For the spacing exception, examine 24 CSS-pixel diameter circles centered on undersized targets: they must not intersect another target or another undersized target's circle. Equivalent, inline, user-agent and essential exceptions also exist. 44×44 targets belong to 2.5.5 AAA or a chosen design goal, not the AA minimum. [W3C target-size explanation](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- Test reduced-motion preference when relevant and label the basis correctly. Animation from interaction is 2.3.3 AAA; pause/stop and flashing requirements can apply at A. Do not mark every animation as an AA failure.

## Running automated checks

Inspect package scripts, test setup and installed versions first. Run the existing accessibility check if present. In Playwright projects that already use `@axe-core/playwright`, navigate and establish the relevant state before `AxeBuilder.analyze()`. Scan opened dialogs and errors as well as the initial page. Confirm the installed axe version's WCAG tags; WCAG 2.2 AA testing needs applicable earlier A/AA tags plus supported 2.2 tags, not just `wcag22aa`. Best-practice rules should be labeled separately. [Official Playwright guide](https://playwright.dev/docs/accessibility-testing)

Record rule IDs, affected locations and engine version. Review incomplete/needs-review results. Keep raw HTML and full scanner output local when it contains sensitive data. A scoped component scan may miss surrounding relationships, portals, document-level failures, or cross-frame content; inspect those separately. Do not disable rules or exclude broad containers just to make a check pass.

Pair automation with actual keyboard operation and the supported browser/screen-reader combinations that are available. Record combinations tested, such as VoiceOver/Safari or NVDA/Firefox, without inventing a universal support matrix. If screen-reader access is unavailable, provide precise human checks rather than claiming an accessibility tree is equivalent. [W3C testing with users](https://www.w3.org/WAI/test-evaluate/involving-users/)
