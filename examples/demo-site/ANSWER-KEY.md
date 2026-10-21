# Demo site answer key

[`broken.html`](broken.html) is a one-page clinic booking form with planted barriers. [`fixed.html`](fixed.html) is the same page remediated. Use them to try the kit, to calibrate an agent's audit, or to check that the browser snippets still work after a change.

Serve the repository root locally so the snippets can be fetched by path:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8765/examples/demo-site/broken.html`.

## Planted barriers

The tool column shows which bundled helper produces evidence for the barrier. "Manual" means a person or agent must operate the page; that is deliberate, because no script can prove those criteria.

| ID | Criterion | Barrier in `broken.html` | Found by | Fix in `fixed.html` |
|---|---|---|---|---|
| B1 | 3.1.1 A | `<html>` has no `lang` | `page-inventory.js` | `lang="en"` |
| B2 | 2.4.2 A | Title is "Page" | `page-inventory.js` + manual review | "Book an appointment \| Riverbend Clinic" |
| B3 | 1.3.1 A | Page and section headings are styled `div`s; no heading structure | `page-inventory.js` (0 headings) | `h1` and `h2` |
| B4 | 1.1.1 A | Hero image has no `alt` | `page-inventory.js` | Real text instead of an image |
| B5 | 1.4.5 AA | Hero message is an image of text | Manual | Same as B4 |
| B6 | 1.4.3 AA | Muted text `#a0a0a0` on white is 2.61:1 | `contrast.py` | `#767676` (4.54:1) |
| B7 | 1.4.12 AA | Notice has fixed `height` and `overflow: hidden`; text clips under spacing overrides | `text-spacing.js` | Height removed |
| B8 | 1.4.10 AA | Schedule grid is 900 px wide; page scrolls horizontally at 320 px | `reflow.js` | Wrapping flex layout |
| B9 | 1.4.1 A | "Pick a green slot"; selected slot is shown by background color only | Manual + `contrast.py` (1.13:1) | Check mark, bold text, and a dark border |
| B10 | 2.1.1 A, 4.1.2 A | Time slots and "Book now" are clickable `div`s with no role, no focus, no keyboard support | `page-inventory.js` + keyboard | Radio group and a real submit `button` |
| B11 | 2.5.3 A | "Book now" has `aria-label="Submit form"` | `page-inventory.js` | Visible text is the name |
| B12 | 3.3.2 A, 1.3.1 A | Fields use placeholders instead of labels | `page-inventory.js` | `<label for>` on every field |
| B13 | 1.3.5 AA | Name, date of birth, and phone lack `autocomplete` | `page-inventory.js` | `name`, `bday`, `tel` |
| B14 | 2.4.3 A | Positive `tabindex` puts date of birth before name | `page-inventory.js` + keyboard | `tabindex` removed |
| B15 | 3.3.1 A, 1.4.1 A | Date-of-birth error is a red border with no text | Manual | Text error, `aria-invalid`, `aria-describedby` |
| B16 | 1.4.11 AA | Input borders `#e3e3e3` on white are 1.28:1 | `contrast.py` | `#767676` borders (4.54:1) |
| B17 | 2.4.7 AA | `outline: none` on every focused element | Keyboard | `:focus-visible` outline |
| B18 | 4.1.2 A | Print button is an unnamed icon | `page-inventory.js` | Visible "Print" text; icon hidden from AT |
| B19 | 2.4.4 A, 4.1.2 A | Social links are empty | `page-inventory.js` | Text links in a named `nav` |
| B20 | 4.1.2 A | A focusable link sits inside `aria-hidden="true"` | `page-inventory.js` | Removed |
| B21 | 2.5.8 AA | Social links are 16×16 px with 2 px gaps | `target-size.js` | At least 24×24 px |
| B22 | 4.1.3 AA | "Appointment saved" appears with no status role | `page-inventory.js` (0 live regions) + screen reader | `role="status"` |

`fixed.html` also adds a skip link and labelled landmarks. Neither is required on a page this small, but both are good practice.

## Expected tool results

Checked in Chromium on 2026-10-21. The fixed page returns zero candidates from every snippet at both 1024 px and 320 px widths.

| Snippet | `broken.html` | `fixed.html` |
|---|---|---|
| `page-inventory.js` | No `lang`; 0 headings; 1 image without alt; 4 unnamed controls; 3 placeholder-only fields; 1 label-in-name mismatch; 6 clickable non-interactive elements; 2 positive tabindex; 1 focusable inside `aria-hidden`; 3 autocomplete candidates; 0 live regions | All lists empty; 3 headings; 1 status region |
| `target-size.js` | 3 fail candidates (social links) | 0 undersized |
| `text-spacing.js` | 1 newly clipped element (notice) | 0 |
| `reflow.js` at 320 px | Page scrolls horizontally; schedule overflows | No overflow |

Not every barrier is visible to a script. B5, B9, B15, B17 and the announcement in B22 need someone to look, operate the keyboard, or listen with a screen reader. An audit that reports only the script findings has missed part of the page.
