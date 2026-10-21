# Accessibility audit: Riverbend Clinic booking page (demo)

> Sample output for the [demo site](demo-site/ANSWER-KEY.md), written from the [report template](../skills/accessibility-audit/assets/report-template.md). Every measurement below came from the kit's own tools and a real keyboard pass. Nothing here is invented, and the screen-reader checks are listed as not performed because none were performed.

| | |
|---|---|
| **Scope** | `examples/demo-site/broken.html`: one page, states *initial*, *date-of-birth error*, *after booking* |
| **Target** | WCAG 2.2 Level AA (A + AA required; AAA reported separately) |
| **Audit date** | 2026-10-21 |
| **Environment** | Chromium (Claude desktop browser pane) at 1024×768 and 320×700; `contrast.py`; `page-inventory.js`, `target-size.js`, `text-spacing.js`, `reflow.js`; keyboard only. No screen reader. |
| **Coverage** | Findings-focused review of one page and three states. The 86-criterion ledger was **not** completed for this sample, so this is not a full audit. |

## Summary

Keyboard users cannot book an appointment. The time slots and the "Book now" control are clickable `div` elements that never receive focus. Even on reachable controls, there is no visible focus indicator anywhere on the page. Screen-reader users meet unlabeled fields, unnamed buttons and links, no headings, and a booking confirmation that is never announced. Target-level coverage is **not complete**: screen-reader behavior, 200% text resize, and orientation were not tested.

| Result | Count |
|---|---|
| Findings | 10 (9 confirmed, 1 suspected) |
| A/AA criteria with a confirmed failure | 20 |
| A/AA criteria with a suspected failure | 1 (4.1.3) |
| AAA findings | None recorded; AAA was not reviewed for this sample |

A full audit would also record pass, not-applicable, and untested results for every one of the 86 criteria in each state. See the [coverage workflow](../skills/accessibility-audit/references/coverage.md).

## Findings

Ordered by task impact. Priority is local triage, not a WCAG level.

### F1. Booking cannot be completed with a keyboard

| | |
|---|---|
| **Priority** | P1, blocks the task |
| **Status** | Confirmed |
| **Criterion** | 2.1.1 Keyboard (A); 4.1.2 Name, Role, Value (A) |
| **Where** | Time slots and "Book now", all states |

**Steps to reproduce**
1. Load the page and press Tab repeatedly.
2. Observe the focus sequence.

**Observed:** Focus moves through date of birth, name, three social links, phone, and the print button, then wraps. The five slots and "Book now" never receive focus. `page-inventory.js` lists all six as clickable elements without a role or keyboard access.

**Impact:** Keyboard, switch, and voice-control users cannot choose a time or submit.

**Fix:** Use a native radio group for the slots and a `<button type="submit">` for booking. Remove the `onclick` handlers on `div` elements.

**Acceptance check:** With keyboard only, select Thursday 3:00 with the arrow keys, press Tab to "Book now", press Enter, and see the confirmation.

### F2. No visible keyboard focus

| | |
|---|---|
| **Priority** | P1 |
| **Status** | Confirmed |
| **Criterion** | 2.4.7 Focus Visible (AA) |
| **Where** | Global stylesheet: `* :focus { outline: none; }` |

**Observed:** In the keyboard pass, each focused element had computed `outline-style: none` and no box-shadow. Nothing visibly changes on focus.

**Impact:** Sighted keyboard users cannot tell where they are.

**Fix:** Remove the rule. Add `:focus-visible { outline: 3px solid #0b5394; outline-offset: 2px; }`, which is 7.83:1 on white (`contrast.py`).

**Acceptance check:** Every Tab stop shows an outline that stays visible against its background.

### F3. Form fields have no labels, and the date error is color-only

| | |
|---|---|
| **Priority** | P1 |
| **Status** | Confirmed |
| **Criterion** | 3.3.2 Labels or Instructions (A); 1.3.1 Info and Relationships (A); 3.3.1 Error Identification (A); 1.4.1 Use of Color (A); 1.3.5 Identify Input Purpose (AA) |
| **Where** | `#name`, `#dob`, `#phone`; *date-of-birth error* state |

**Observed:** `page-inventory.js` reports 3 placeholder-only fields and 3 personal-data fields without `autocomplete`. In the error state, the date of birth is marked only by a red border (`#d93025`), with no text.

**Fix:** Add a `<label for>` to each field. Add `autocomplete="name"`, `"bday"`, and `"tel"`. Add a text error tied to the field with `aria-describedby` and `aria-invalid="true"`, plus a format hint.

**Acceptance check:** Each field's accessible name matches its visible label, autofill works, and the error is announced as text.

### F4. Unnamed controls and links

| | |
|---|---|
| **Priority** | P2 |
| **Status** | Confirmed |
| **Criterion** | 4.1.2 (A); 2.4.4 Link Purpose (A); 2.5.3 Label in Name (A) |
| **Where** | Social links, print button, "Book now" |

**Observed:** `page-inventory.js` reports 4 unnamed controls: three empty social links and the icon-only print button. It also reports 1 focusable link inside `aria-hidden="true"`, and 1 label-in-name mismatch: the visible text "Book now" has the accessible name "Submit form".

**Fix:** Give links visible text or an accessible name. Add visible "Print" text and hide the icon from assistive technology. Let the visible text "Book now" be the button's name.

### F5. Social links are too small and too close together

| | |
|---|---|
| **Priority** | P2 |
| **Status** | Confirmed |
| **Criterion** | 2.5.8 Target Size (Minimum) (AA) |
| **Where** | Header social links |

**Observed:** `target-size.js` measured three targets at 16×16 CSS px with 2 px gaps. At both 1024 px and 320 px, their 24 px spacing circles intersect, so the spacing exception does not apply.

**Fix:** Give each link at least 24×24 CSS px, for example with padding, or space their centers at least 24 px apart.

### F6. Muted text and input borders lack contrast

| | |
|---|---|
| **Priority** | P2 |
| **Status** | Confirmed |
| **Criterion** | 1.4.3 Contrast (Minimum) (AA); 1.4.11 Non-text Contrast (AA) |

**Observed:** `contrast.py` measured the `.muted` text `#a0a0a0` on `#ffffff` at 2.61:1 (16 px regular, needs 4.5:1). Input borders `#e3e3e3` on `#ffffff` measured 1.28:1, and no other cue identifies the fields (needs 3:1).

**Fix:** `contrast.py --target 4.5` suggests `#767676` (4.54:1) for the text. Use the same color for input borders.

### F7. Selected time slot is shown by color alone

| | |
|---|---|
| **Priority** | P2 |
| **Status** | Confirmed |
| **Criterion** | 1.4.1 Use of Color (A); 4.1.2 (A) |

**Observed:** The instruction reads "Pick a green slot". The selected slot differs only by a `#e6f4ea` fill, which is 1.13:1 against white, and its selected state is not exposed programmatically.

**Fix:** Covered by the radio group in F1. Add a check mark or text and a strong border. Rewrite the instruction without color.

### F8. Content breaks at 320 px and under text spacing

| | |
|---|---|
| **Priority** | P2 |
| **Status** | Confirmed |
| **Criterion** | 1.4.10 Reflow (AA); 1.4.12 Text Spacing (AA) |

**Observed:** At 320 px, `reflow.js` reports horizontal page scrolling caused by the 900 px schedule grid. With the 1.4.12 overrides at 1024 px, `text-spacing.js` reports the closure notice clipped: 64 px of content in a 62 px box with `overflow: hidden`, which cuts off the bottom of the last line. Narrower widths wrap to more lines and clip more.

**Fix:** Use a wrapping layout for the schedule. Remove the fixed height on the notice.

### F9. Page structure and metadata

| | |
|---|---|
| **Priority** | P3 |
| **Status** | Confirmed |
| **Criterion** | 3.1.1 Language of Page (A); 2.4.2 Page Titled (A); 1.3.1 (A); 1.1.1 Non-text Content (A); 1.4.5 Images of Text (AA); 2.4.3 Focus Order (A) |

**Observed:**
- `<html>` has no `lang`.
- The title is "Page".
- There are no headings: the "Book an appointment" heading and section titles are styled `div`s.
- The hero image has no `alt` and presents "Same-day visits available" as an image of text.
- A positive `tabindex` puts date of birth before name.

**Fix:**
- Add `lang="en"`.
- Use a descriptive title.
- Use `h1` and `h2` elements.
- Make the hero real text.
- Remove the positive `tabindex` values.

### F10. Booking confirmation is not announced (suspected)

| | |
|---|---|
| **Priority** | P2 |
| **Status** | Suspected (needs a screen reader) |
| **Criterion** | 4.1.3 Status Messages (AA) |

**Observed:** `page-inventory.js` reports no live regions. The "Appointment saved" text is inserted into a plain `div`.

**Fix:** Add `role="status"` to the container.

**Acceptance check:** VoiceOver or NVDA announces the confirmation without moving focus.

## Coverage and open items

- **Ledger:** not completed for this sample. For a full audit, generate it with `coverage.py --output` and report totals from `coverage.py --summary --report`.
- **Not tested:**
  - Screen-reader output in every state (no screen reader available).
  - 200% text-only resize (1.4.4).
  - Orientation on a real device (1.3.4).
  - Speech input (2.5.3 verification).
  - Pointer cancellation on touch (2.5.2).
- **Needs human review:** whether the closure notice's wording is understandable (3.1.5, AAA).
- A remediated version is in [`fixed.html`](demo-site/fixed.html). It returns zero candidates from every snippet. It still needs the same manual and screen-reader checks before anyone calls it conformant.

## Next actions

1. Rebuild the booking form with native controls (F1, F3, F4, F7). This one change addresses most of the form's failures.
2. Restore focus visibility globally (F2) and fix the tokens (F6).
3. Fix layout (F5, F8) and page metadata (F9).
4. Retest with keyboard, VoiceOver on Safari, and NVDA on Firefox, including the confirmation announcement (F10).

---

*Prepared with the Accessibility Audit Kit. This report is a testing aid, not a legal certification.*
