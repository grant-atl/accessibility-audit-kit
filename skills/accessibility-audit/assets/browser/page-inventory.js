// Accessibility Audit Kit: page inventory snippet.
// Paste into a browser console or run through an agent's JavaScript tool on the state under test.
// Returns candidates for manual review, not verdicts. The accessible-name logic is a simplified
// approximation of the W3C algorithm; confirm names in the browser's accessibility tree and with AT.
(() => {
  const MAX = 50;
  const text = (s) => (s || "").replace(/\s+/g, " ").trim();
  const short = (s) => (s.length > 80 ? s.slice(0, 77) + "..." : s);
  const visible = (el) => {
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && (rect.width > 0 || rect.height > 0);
  };
  const selector = (el) => {
    if (el.id) return `#${CSS.escape(el.id)}`;
    const parts = [];
    for (let node = el; node && node.nodeType === 1 && parts.length < 4; node = node.parentElement) {
      let part = node.localName;
      if (node.id) { parts.unshift(`#${CSS.escape(node.id)}`); break; }
      const siblings = node.parentElement ? [...node.parentElement.children].filter((c) => c.localName === node.localName) : [];
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
      parts.unshift(part);
    }
    return parts.join(" > ");
  };
  const byIds = (ids) => text((ids || "").split(/\s+/).map((id) => document.getElementById(id)?.textContent || "").join(" "));
  const name = (el) => {
    const labelledby = byIds(el.getAttribute("aria-labelledby"));
    if (labelledby) return { name: labelledby, source: "aria-labelledby" };
    const aria = text(el.getAttribute("aria-label"));
    if (aria) return { name: aria, source: "aria-label" };
    if (el.labels && el.labels.length) {
      const label = text([...el.labels].map((l) => l.textContent).join(" "));
      if (label) return { name: label, source: "label" };
    }
    if (el.localName === "img" || (el.localName === "input" && el.type === "image")) {
      if (el.hasAttribute("alt")) return { name: text(el.alt), source: "alt" };
    }
    if (["button", "a", "summary"].includes(el.localName) || /^(button|link|tab|menuitem|option|switch|checkbox|radio)$/.test(el.getAttribute("role") || "")) {
      const clone = el.cloneNode(true);
      clone.querySelectorAll("[aria-hidden='true']").forEach((n) => n.remove());
      const alts = [...clone.querySelectorAll("img[alt], svg title, [aria-label], [aria-labelledby]")].map((n) =>
        n.getAttribute("aria-label") || byIds(n.getAttribute("aria-labelledby")) || n.getAttribute("alt") || n.textContent).join(" ");
      const content = text(clone.textContent + " " + alts);
      if (content) return { name: content, source: "content" };
    }
    if (el.localName === "input" && ["submit", "reset", "button"].includes(el.type) && el.value) return { name: el.value, source: "value" };
    const title = text(el.getAttribute("title"));
    if (title) return { name: title, source: "title" };
    const placeholder = text(el.getAttribute("placeholder"));
    if (placeholder) return { name: placeholder, source: "placeholder-only" };
    return { name: "", source: "none" };
  };
  const cap = (list) => ({ count: list.length, items: list.slice(0, MAX) });

  const headings = [...document.querySelectorAll("h1,h2,h3,h4,h5,h6,[role='heading']")].filter(visible).map((h) => ({
    level: Number(h.getAttribute("aria-level") || h.localName.slice(1)) || null,
    text: short(text(h.textContent)),
  }));
  const landmarks = [...document.querySelectorAll("header,nav,main,aside,footer,form[aria-label],form[aria-labelledby],section[aria-label],section[aria-labelledby],[role='banner'],[role='navigation'],[role='main'],[role='complementary'],[role='contentinfo'],[role='search'],[role='region'],[role='form']")]
    .filter(visible).map((el) => ({ element: el.getAttribute("role") || el.localName, name: short(name(el).name) }));

  const images = [...document.querySelectorAll("img, [role='img'], svg, input[type='image']")].filter(visible);
  const imageIssues = images.flatMap((el) => {
    if (el.closest("[aria-hidden='true']")) return [];
    // Inline SVG without role="img" is treated as part of its container; unnamed containers are reported separately.
    if (el.localName === "svg" && el.getAttribute("role") !== "img") return [];
    const n = name(el);
    if (el.localName === "img" && !el.hasAttribute("alt")) return [{ selector: selector(el), issue: "img has no alt attribute (1.1.1)" }];
    if (el.localName === "img" && el.alt === "") return [{ selector: selector(el), issue: "empty alt: confirm the image is decorative (1.1.1)" }];
    if (!n.name && el.localName !== "svg") return [{ selector: selector(el), issue: "image has no text alternative (1.1.1)" }];
    return [{ selector: selector(el), issue: `review alt for purpose: "${short(n.name)}"` }];
  });

  const focusableSelector = "a[href],button,input:not([type='hidden']),select,textarea,summary,iframe,[tabindex],[contenteditable='true']";
  const controls = [...document.querySelectorAll(focusableSelector + ",[role='button'],[role='link'],[role='checkbox'],[role='radio'],[role='tab'],[role='switch'],[role='menuitem'],[role='combobox'],[role='slider']")]
    .filter(visible).filter((el) => !el.disabled)
    // tabindex="-1" on a generic element (for example a heading used as a focus target) does not make it a control.
    .filter((el) => el.matches("a[href],button,input,select,textarea,summary,iframe,[contenteditable='true'],[role]") || el.tabIndex >= 0);
  const unnamed = [];
  const placeholderOnly = [];
  controls.forEach((el) => {
    const n = name(el);
    if (n.source === "none") unnamed.push({ selector: selector(el), element: el.localName, role: el.getAttribute("role") || "" });
    if (n.source === "placeholder-only") placeholderOnly.push({ selector: selector(el), placeholder: n.name });
  });
  // Any element whose author-supplied name omits its visible text, including elements missing a role.
  // Containers (sections, forms, dialogs) are named by headings, so only leaf-like elements are compared.
  const containerContent = "a,button,input,select,textarea,h1,h2,h3,h4,h5,h6,p,li,section,form,table";
  const labelMismatch = [...document.querySelectorAll("[aria-label],[aria-labelledby]")].filter(visible).flatMap((el) => {
    if (el.querySelector(containerContent) || /^(section|form|nav|main|aside|header|footer|dialog|fieldset|table|ul|ol)$/.test(el.localName)) return [];
    const n = name(el);
    // A field's visible label is its <label>, not its current value or selected option.
    const field = ["input", "select", "textarea"].includes(el.localName);
    const visibleText = field ? text([...(el.labels || [])].map((l) => l.textContent).join(" ")) : text(el.innerText || "");
    if (!visibleText || !n.name || n.name.toLowerCase().includes(visibleText.toLowerCase())) return [];
    return [{ selector: selector(el), visibleLabel: short(visibleText), accessibleName: short(n.name), role: el.getAttribute("role") || el.localName }];
  });

  const interactiveTags = new Set(["a", "button", "input", "select", "textarea", "summary", "label", "option", "details"]);
  const clickableNonInteractive = [...document.querySelectorAll("body *")].filter((el) => {
    if (interactiveTags.has(el.localName) || el.getAttribute("role") || el.hasAttribute("tabindex") || !visible(el)) return false;
    if (el.closest("a,button,label,summary")) return false;
    const pointer = getComputedStyle(el).cursor === "pointer" && getComputedStyle(el.parentElement || el).cursor !== "pointer";
    return el.hasAttribute("onclick") || pointer;
  }).map((el) => ({ selector: selector(el), text: short(text(el.textContent)), issue: "click target without role or keyboard access (2.1.1, 4.1.2)" }));

  const positiveTabindex = [...document.querySelectorAll("[tabindex]")].filter((el) => el.tabIndex > 0)
    .map((el) => ({ selector: selector(el), tabindex: el.tabIndex }));
  const hiddenFocusable = [...document.querySelectorAll("[aria-hidden='true']")].flatMap((root) =>
    [root, ...root.querySelectorAll(focusableSelector)].filter((el) => el.matches(focusableSelector) && el.tabIndex >= 0 && !el.disabled && visible(el))
  ).map((el) => ({ selector: selector(el) }));

  const autocompleteCandidates = [...document.querySelectorAll("input:not([type='hidden']):not([type='checkbox']):not([type='radio']):not([type='submit']):not([type='button'])")]
    .filter(visible).filter((el) => !el.getAttribute("autocomplete"))
    .filter((el) => /name|email|phone|tel|mobile|address|street|city|zip|postal|country|birth|dob|bday|organi[sz]ation|username/i.test([el.type, el.name, el.id, name(el).name].join(" ")))
    .map((el) => ({ selector: selector(el), label: short(name(el).name) }));

  const liveRegions = [...document.querySelectorAll("[aria-live],[role='status'],[role='alert'],[role='log'],output")]
    .map((el) => ({ selector: selector(el), role: el.getAttribute("role") || el.localName, live: el.getAttribute("aria-live") || "implicit" }));

  const lang = document.documentElement.getAttribute("lang") || "";
  return {
    note: "Candidates for manual verification. Names are approximate; confirm with the accessibility tree and real assistive technology.",
    url: location.href,
    title: { value: document.title, issue: document.title.trim() ? "confirm it describes topic or purpose (2.4.2)" : "missing title (2.4.2)" },
    lang: { value: lang, issue: lang ? "confirm it matches the page language (3.1.1)" : "missing html lang (3.1.1)" },
    headings: { count: headings.length, h1: headings.filter((h) => h.level === 1).length, outline: headings.slice(0, MAX) },
    landmarks: cap(landmarks),
    images: cap(imageIssues),
    unnamedControls: cap(unnamed),
    placeholderOnlyFields: cap(placeholderOnly),
    labelInNameMismatches: cap(labelMismatch),
    clickableNonInteractive: cap(clickableNonInteractive),
    positiveTabindex: cap(positiveTabindex),
    focusableInsideAriaHidden: cap(hiddenFocusable),
    autocompleteCandidates: cap(autocompleteCandidates),
    liveRegions: cap(liveRegions),
  };
})();
