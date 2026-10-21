// Accessibility Audit Kit: WCAG 1.4.10 reflow snippet.
// Set the viewport to 320 CSS px wide (or 1280 px at 400% zoom) first, then run this on each state.
// Lists the outermost elements that extend past the viewport and cause horizontal scrolling.
// Also lists containers that scroll horizontally themselves. Content that legitimately needs two dimensions
// (data tables, maps, diagrams) may be excepted; decide manually. Content clipped by overflow: hidden is not
// listed, so check visually for lost content too.
(() => {
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
  const width = document.documentElement.clientWidth;
  const scrolls = document.documentElement.scrollWidth > width + 1;
  const scrollsX = (el) => /auto|scroll/.test(getComputedStyle(el).overflowX) && el.scrollWidth > el.clientWidth + 1;
  // Containers that themselves scroll horizontally, such as an app shell with overflow-y: auto
  // (which computes overflow-x to auto) wrapping wide content.
  const scrollRegions = [...document.querySelectorAll("body *")].filter((el) => {
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && scrollsX(el);
  });
  const contained = (el) => {
    for (let node = el.parentElement; node && node !== document.body; node = node.parentElement) {
      if (scrollRegions.includes(node) || /hidden|clip/.test(getComputedStyle(node).overflowX)) return true;
    }
    return false;
  };
  // Only rightward overflow causes horizontal scrolling; off-screen skip links parked at negative left are ignored.
  const wide = [...document.querySelectorAll("body *")].filter((el) => {
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return false;
    return rect.right > width + 1 && !contained(el);
  });
  const outermost = wide.filter((el) => !wide.some((other) => other !== el && other.contains(el)));
  return {
    note: "1.4.10 AA: content should reflow at 320 CSS px without two-dimensional scrolling, except where two-dimensional layout is essential.",
    viewportWidth: width,
    warning: width > 320 ? "Viewport is wider than 320 CSS px; resize before treating this as reflow evidence." : null,
    pageScrollsHorizontally: scrolls,
    horizontalScrollRegions: scrollRegions.filter((el) => !scrollRegions.some((o) => o !== el && o.contains(el))).slice(0, 50).map((el) => ({
      selector: selector(el),
      element: el.localName,
      visibleWidth: el.clientWidth,
      contentWidth: el.scrollWidth,
    })),
    overflowing: outermost.slice(0, 50).map((el) => ({
      selector: selector(el),
      element: el.localName,
      left: Math.round(el.getBoundingClientRect().left),
      right: Math.round(el.getBoundingClientRect().right),
      width: Math.round(el.getBoundingClientRect().width),
    })),
  };
})();
