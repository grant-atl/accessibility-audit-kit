# Design review and handoff

Review actual frames, variants and tokens when available. Use an available design connector or exported assets; do not require a particular vendor. If only an image exists, state what cannot be measured or exercised. Do not assume layer order will become DOM order.

## Inspect what designers can resolve

- Find the task and its full flow. Include error, loading, empty, selected, disabled, hover, focus and narrow-screen states where they affect use. Missing states are handoff gaps, not proven runtime failures.
- Read contrast from actual tokens and composited colors when possible. Account for overlays, transparency, images and gradients. If only screenshot pixels are available, label measurements as estimates and request source values before a definitive borderline finding.
- Check whether labels, instructions, validation messages and action names remain understandable without position, shape, color, or an icon alone. Use text alongside status colors. Suggest concise correction messages without inventing product facts.
- Inspect text hierarchy, content order, density, wrapping, truncation and layouts at enlarged text/narrow width. Drawn dimensions are design units; convert to CSS or platform units only when the scale is known.
- Evaluate target area and separation, including invisible hit areas only if explicitly specified. Keep AA target-size exceptions and optional larger-touch recommendations distinct.
- Identify intended keyboard paths, focus visibility/placement, dismiss behavior, alternatives to dragging, motion controls and timing. Prototype mouse interaction cannot establish keyboard or screen-reader support.
- For charts and complex images, define the information/task the equivalent text or table must support. Do not require verbose alternative text for decorative imagery.

## Make the handoff implementable

For each relevant component specify the visible label, intended native element/role, state, relationships, keyboard behavior, focus transitions, and announcement need. Prefer established platform semantics. Include acceptance criteria that an engineer can test in the rendered product.

Example handoff for a modal: visible title provides its accessible name; focus moves inside when opened; Tab stays within the active modal; Escape dismisses where appropriate; focus returns to the invoking control or next logical destination. The rendered implementation still needs testing. Use the [W3C dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) when a custom modal is necessary.

Separate findings into observed design barriers, incomplete specifications, and implementation checks. Keep good design choices intact. Do not redesign branding or label a screenshot “WCAG compliant.” For plain language, distinguish general usability improvements from specific WCAG A/AA obligations.
