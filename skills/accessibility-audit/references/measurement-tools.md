# Measurement tools

The bundled tools produce exact measurements and candidate lists, so evidence rests on numbers rather than estimates. They never decide conformance on their own. Each result still needs a person or agent to confirm it against the criterion's exceptions and the actual experience.

## Contrast calculator

`scripts/contrast.py` implements the WCAG 2.2 relative-luminance formula, composites translucent colors, and never rounds a ratio up to a passing threshold. Python 3.9+, standard library only.

```sh
python3 scripts/contrast.py "#767676" "#ffffff"
python3 scripts/contrast.py "rgba(0,0,0,.55)" "#f4f1de" --target 4.5
python3 scripts/contrast.py "#ffffff" "rgba(0,0,0,.4)" --base "#2a5d8f" --json
```

- It accepts hex (`#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`), `rgb()`/`rgba()` with commas or spaces, and `white`/`black`. Read colors from computed styles or design tokens, not antialiased screenshot pixels.
- A translucent foreground is composited over the background. A translucent background is composited over `--base`. Confirm what is really underneath, including images and gradients; for gradients, measure the worst-case stop behind the text.
- Ratios are truncated to two decimals, never rounded up, in both text and `--json` output (`ratio_exact` holds the full value). The output covers 1.4.3 (AA), 1.4.6 (AAA), and 1.4.11 (AA non-text). Choose the row that matches the content: large text is at least 18pt (24 CSS px) regular or 14pt (about 18.66 CSS px) bold.
- `--target` suggests the closest foreground color, mixed toward black or white, that meets the ratio. Treat it as a starting point for design review, not an automatic token change.

## Browser snippets

The `assets/browser/` scripts are self-contained and run in any browser console or agent JavaScript tool. Each one returns JSON. Load the page, establish the state under test (menu open, error shown, dialog open), then run the snippet. Record the viewport and browser with the result.

An agent can run a snippet by pasting the file's contents into its JavaScript tool. When the files are served from the same origin, it can also fetch and evaluate them:

```js
(0, eval)(await (await fetch("/path/to/page-inventory.js")).text())
```

Only do this on pages you are authorized to test. The snippets read the DOM and computed styles. Only `text-spacing.js` changes the page, by adding one style element that a second run removes.

| Snippet | Criteria | What it returns | What it cannot tell you |
|---|---|---|---|
| `page-inventory.js` | 1.1.1, 1.3.1, 1.3.5, 2.1.1, 2.4.2, 2.4.3, 2.5.3, 3.1.1, 3.3.2, 4.1.2, 4.1.3 | Title, `lang`, heading outline, landmarks, images without alternatives, unnamed controls, placeholder-only fields, label-in-name mismatches, clickable elements without roles, positive `tabindex`, focusable content inside `aria-hidden`, likely `autocomplete` gaps, live regions | Whether names and alternatives are *meaningful*; actual screen-reader output; keyboard behavior of custom widgets; handlers attached with `addEventListener` and no pointer cursor |
| `target-size.js` | 2.5.8 (and a count for 2.5.5) | Every undersized target, with a spacing-exception verdict using 24 px circles | Hit areas extended by pseudo-elements or parents; whether the inline, equivalent, user-agent, or essential exception applies |
| `text-spacing.js` | 1.4.12 | Applies the four spacing overrides and lists text that newly clips or truncates. Run again to remove. | Overlap between siblings, hidden controls, or lost function without overflow, so inspect visually while it is applied |
| `reflow.js` | 1.4.10 | Outermost elements that extend past the right edge of the viewport, and containers (such as app shells) that scroll horizontally themselves | Whether two-dimensional layout is essential; content clipped by `overflow: hidden` rather than overflowing. Set the viewport to 320 CSS px first. |

## Evidence wording

Quote the measurement and the method in the ledger, for example:

- `fail: .muted text #a0a0a0 on #ffffff = 2.61:1 (contrast.py), 16px regular; needs 4.5:1`
- `fail: 3 social links 16x16 CSS px, 24px circles intersect (target-size.js, 1024x768 Chromium)`
- `pass: no clipping with 1.4.12 overrides (text-spacing.js) and visual check at 1280x800`

A clean snippet result is supporting evidence for a pass, not a pass by itself. Combine it with the manual and assistive-technology checks the matrix lists for that criterion.
