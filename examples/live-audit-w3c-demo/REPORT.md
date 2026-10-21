# Accessibility audit: W3C "Before" demo home page (live site)

> A full 86-criterion audit of a live public page, run with this kit's workflow and tools, then checked against W3C's own published evaluation of the same page. The [ledger](coverage.csv) and [coverage rollup](coverage-summary.md) are the actual files produced by `coverage.py`.

| | |
|---|---|
| **Scope** | [`https://www.w3.org/WAI/demos/bad/before/home.html`](https://www.w3.org/WAI/demos/bad/before/home.html), the demo content inside `#page`. W3C's surrounding banner and footer are excluded. State: initial. |
| **Target** | WCAG 2.2 Level AA (A + AA required; AAA reported separately) |
| **Audit date** | 2026-10-21 |
| **Environment** | Chrome 155 via Playwright on macOS. Viewports: 1280×900, 640 CSS px (200% zoom equivalent), and 320 CSS px. Keyboard tested with a scripted Tab pass. **No screen reader.** |
| **Tools** | `page-inventory.js`, `target-size.js`, `text-spacing.js`, `reflow.js`, `contrast.py`, `coverage.py`; source review; visual review of screenshots |
| **Coverage** | 1 location × 1 state × 86 criteria, every row recorded with evidence |

## Summary

Keyboard users cannot use most of this page. Fourteen links, including the entire left navigation, call `blur()` when they receive focus, so focus is thrown away and the links can never be activated. The navigation is images of text with no alternatives. The quick menu navigates to another site as soon as an option is selected. The page is not conformant to WCAG 2.2 AA.

| Target criteria (55 A/AA) | Count |
|---|---|
| Fail | 18 |
| Pass | 11 |
| Not applicable | 20 |
| Needs review | 2 (1.3.3, 1.4.11) |
| Not tested | 4 (2.4.5, 3.2.3, 3.2.4, 3.2.6: cross-page criteria; scope is one page) |

Supplemental AAA: 8 fail, 6 pass, 14 not applicable, 1 needs review, 2 not tested.

## Findings

| # | Priority | Barrier | Criteria | Evidence |
|---|---|---|---|---|
| 1 | P1 | 14 links discard focus on arrival (`onFocus="blur()"`) and cannot be activated by keyboard | 2.1.1, 2.4.7, 3.2.1 | Scripted Tab pass landed on `BODY` 14 times |
| 2 | P1 | Image navigation (HOME, NEWS, TICKETS, SURVEY) has no text alternative; links have no name | 1.1.1, 1.4.5, 2.4.4, 2.5.3, 4.1.2 | `page-inventory.js`: 33 images without `alt`; 7 unnamed links |
| 3 | P1 | Quick menu navigates on selection without warning and has no label | 3.2.2, 3.3.2, 1.3.1, 4.1.2 | Selecting option 1 loaded `offsite.html` |
| 4 | P2 | No headings, landmarks, or skip link in the demo | 1.3.1, 2.4.1 | `page-inventory.js`: 0 demo headings, 0 landmarks |
| 5 | P2 | News grid separates each story from its headline when linearized | 1.3.2 | Markup lists headlines, then photos, then stories |
| 6 | P2 | Hotline number is an image whose alt text is wrong: alt "1234 56789", image shows "(1) 2G9 C-H-O-K-E" | 1.1.1, 1.4.5 | Visual review of screenshot |
| 7 | P2 | Fixed 800 px layout scrolls horizontally at 320 px | 1.4.10 | `reflow.js`: `#page > table` |
| 8 | P2 | "Free Penguins" heading contrast 3.88:1 (13 px bold) | 1.4.3 | `contrast.py`: `#41545d` on `#a9b8bf` |
| 9 | P3 | Inline links rely on color, with no underline on hover or focus | 1.4.1 | `contrast.py`: link vs text 3.60:1 |
| 10 | P3 | No `lang`; every page shares the title "Welcome to CityLights!" | 3.1.1, 2.4.2 | `page-inventory.js` on all four demo pages |

Passing results that rest on measurement include:
- text spacing (`text-spacing.js`, 0 clipped, plus visual review);
- 200% zoom (content complete at 640 CSS px);
- target size (`target-size.js`: undersized demo targets pass the 24 px spacing exception);
- contrast of body text (21:1), news panels (17.93:1), and links (5.82:1);
- no flashing (every GIF is single-frame).

## Comparison with W3C's own evaluation

W3C publishes a [WCAG 2.0 report for this page](https://www.w3.org/WAI/demos/bad/before/reports/home.html). WCAG 2.0 has 38 A/AA criteria, and 37 of them still exist in 2.2 (4.1.1 was removed). On those 37:

- **First pass: 29 agreed.** Three were genuine misses, where the kit said pass and W3C said fail:
  - **1.3.2, the row-by-row news grid.** I checked overall page order but not the card grid.
  - **2.4.2, the title shared across pages.** The cross-page data was available but not compared.
  - **1.4.1.** The kit flagged it as "needs review" instead of failing it.

  The matrix and source checklist now cover all three, and the ledger was corrected.
- **After correction: 32 agree.**
- **Five still differ, and none contradicts W3C:**
  - **2.4.6:** W3C fails it because headings aren't marked up. The current [Understanding document](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html) places markup under 1.3.1, which the kit fails, and limits 2.4.6 to whether headings are descriptive.
  - **1.3.3:** recorded as "needs review"; W3C says pass.
  - **2.4.5, 3.2.3, 3.2.4:** not tested because they need the other pages; W3C evaluated the whole site.
- **WCAG 2.1 failures W3C couldn't report:** the kit also found 1.4.10 Reflow and 2.5.3 Label in Name. The 2012 report predates those criteria.

## Not tested

- Screen-reader output (no screen reader available). Name and role findings rest on the accessibility tree.
- Cross-page criteria 2.4.5, 3.2.3, 3.2.4, 3.2.6.
- AAA 1.3.6 and 1.4.8.

---

*Prepared with the Accessibility Audit Kit. This report is a testing aid, not a legal certification.*
