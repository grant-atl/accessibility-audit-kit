// Accessibility Audit Kit: WCAG 2.2 target size snippet (2.5.8 AA, with 2.5.5 AAA for reference).
// Run on the state and viewport under test. Measures bounding boxes in CSS pixels.
// Limits: hit areas extended by pseudo-elements or parent click handlers are not measured, and the
// inline, equivalent, user-agent, and essential exceptions need human judgment. Treat output as evidence to verify.
(() => {
  const MIN = 24;
  const ENHANCED = 44;
  const selector = (el) => {
    const parts = [];
    for (let node = el; node && node.nodeType === 1 && parts.length < 4; node = node.parentElement) {
      if (node.id) { parts.unshift(`#${CSS.escape(node.id)}`); break; }
      let part = node.localName;
      const siblings = node.parentElement ? [...node.parentElement.children].filter((c) => c.localName === node.localName) : [];
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
      parts.unshift(part);
    }
    return parts.join(" > ");
  };
  const query = "a[href],button,input:not([type='hidden']),select,textarea,summary,[role='button'],[role='link'],[role='checkbox'],[role='radio'],[role='switch'],[role='tab'],[role='menuitem'],[role='option'],[role='slider'],[tabindex]:not([tabindex='-1']),[onclick]";
  const native = "a[href],button,input,select,textarea,summary,[role]";
  const candidates = [...document.querySelectorAll(query)].filter((el) => {
    if (el.disabled) return false;
    const style = getComputedStyle(el);
    return style.display !== "none" && style.visibility !== "hidden" && style.pointerEvents !== "none";
  });
  // A focusable or clickable generic wrapper around other targets is a region, not a target itself;
  // its descendants are measured instead.
  const targets = candidates.filter((el) => el.matches(native) || !candidates.some((o) => o !== el && el.contains(o)));
  // A visually hidden native input inside a label is operated through the label, so measure the label.
  const effective = targets.map((el) => {
    const rect = el.getBoundingClientRect();
    const label = el.labels && el.labels[0];
    if (label && (rect.width < 2 || rect.height < 2 || getComputedStyle(el).opacity === "0")) return { el, rect: label.getBoundingClientRect(), via: "label" };
    return { el, rect, via: "self" };
  }).filter((t) => t.rect.width > 0 && t.rect.height > 0);

  const center = (r) => ({ x: r.left + r.width / 2, y: r.top + r.height / 2 });
  const circleHitsRect = (c, r) => {
    const dx = Math.max(r.left - c.x, 0, c.x - r.right);
    const dy = Math.max(r.top - c.y, 0, c.y - r.bottom);
    return dx * dx + dy * dy < (MIN / 2) ** 2;
  };
  const inlineCandidate = (el) => {
    if (el.localName !== "a") return false;
    const block = el.parentElement;
    if (!block) return false;
    const siblingText = [...block.childNodes].filter((n) => n !== el && n.nodeType === 3).map((n) => n.textContent.trim()).join("");
    return siblingText.length > 20 && getComputedStyle(el).display === "inline";
  };

  const undersized = effective.filter((t) => t.rect.width < MIN || t.rect.height < MIN);
  const results = undersized.map((t) => {
    const c = center(t.rect);
    const overlapsTarget = effective.find((o) => o !== t && !o.el.contains(t.el) && !t.el.contains(o.el) && circleHitsRect(c, o.rect));
    const overlapsCircle = undersized.find((o) => {
      if (o === t) return false;
      const oc = center(o.rect);
      return Math.hypot(oc.x - c.x, oc.y - c.y) < MIN;
    });
    const conflict = overlapsTarget || overlapsCircle;
    let verdict = conflict ? "fail-candidate" : "passes-by-spacing";
    if (conflict && inlineCandidate(t.el)) verdict = "check-inline-exception";
    return {
      selector: selector(t.el),
      text: (t.el.innerText || t.el.getAttribute("aria-label") || t.el.value || "").trim().slice(0, 40),
      size: `${Math.round(t.rect.width * 10) / 10}x${Math.round(t.rect.height * 10) / 10}`,
      measuredVia: t.via,
      verdict,
      conflictsWith: conflict ? selector(conflict.el) : null,
    };
  });
  const failing = results.filter((r) => r.verdict === "fail-candidate");
  return {
    note: "2.5.8 AA: targets under 24x24 CSS px pass only if a 24 px circle centered on each does not intersect another target or another undersized target's circle, or another exception applies. Verify exceptions manually.",
    viewport: `${innerWidth}x${innerHeight}`,
    targetsMeasured: effective.length,
    undersized: results.length,
    failCandidates: failing.length,
    results: results.slice(0, 100),
    below44ForAAA: effective.filter((t) => t.rect.width < ENHANCED || t.rect.height < ENHANCED).length,
  };
})();
