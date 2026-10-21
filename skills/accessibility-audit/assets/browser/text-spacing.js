// Accessibility Audit Kit: WCAG 1.4.12 text spacing snippet.
// First run applies the four spacing overrides to the whole document and reports elements whose text
// now clips or overflows. Run it again to remove the overrides. Content inside iframes and shadow roots is not covered.
// Always inspect the page visually as well: overlap between siblings and lost function can occur without overflow.
(() => {
  const ID = "a11y-kit-text-spacing";
  const existing = document.getElementById(ID);
  if (existing) {
    existing.remove();
    return { applied: false, note: "Text spacing overrides removed." };
  }
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
  const clipped = (el) => {
    const style = getComputedStyle(el);
    const hidesY = /hidden|clip/.test(style.overflowY) && el.scrollHeight > el.clientHeight + 1;
    const hidesX = /hidden|clip/.test(style.overflowX) && el.scrollWidth > el.clientWidth + 1;
    const ellipsis = style.textOverflow === "ellipsis" && el.scrollWidth > el.clientWidth + 1;
    const clamp = style.webkitLineClamp && style.webkitLineClamp !== "none" && el.scrollHeight > el.clientHeight + 1;
    return hidesY || hidesX || ellipsis || clamp;
  };
  const hasText = (el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) || el.innerText?.trim();
  const before = new Set([...document.querySelectorAll("body *")].filter((el) => hasText(el) && clipped(el)));

  const style = document.createElement("style");
  style.id = ID;
  style.textContent = "* { line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important; } p, li, dd, dt, blockquote, figcaption, h1, h2, h3, h4, h5, h6 { margin-bottom: 2em !important; }";
  document.head.appendChild(style);

  const after = [...document.querySelectorAll("body *")].filter((el) => hasText(el) && clipped(el));
  const newlyClipped = after.filter((el) => !before.has(el)).map((el) => ({
    selector: selector(el),
    text: (el.innerText || "").trim().replace(/\s+/g, " ").slice(0, 60),
    box: `${el.clientWidth}x${el.clientHeight}`,
    content: `${el.scrollWidth}x${el.scrollHeight}`,
  }));
  return {
    applied: true,
    note: "Overrides applied: line-height 1.5, paragraph spacing 2em, letter-spacing 0.12em, word-spacing 0.16em. Inspect the page now, then run again to remove.",
    viewport: `${innerWidth}x${innerHeight}`,
    newlyClipped: newlyClipped.slice(0, 100),
    count: newlyClipped.length,
    alreadyClippedBefore: before.size,
  };
})();
