// Runs the browser snippets against the demo pages in headless Chromium and checks the
// results recorded in examples/demo-site/ANSWER-KEY.md. Requires Python 3 and Playwright:
//   npm install --no-save playwright@1.49.1 && npx playwright install chromium
//   node tests/browser/check-snippets.mjs
// Set PLAYWRIGHT_CHANNEL=chrome to use an installed Chrome with playwright-core instead.

import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const snippet = (name) => readFileSync(join(root, "skills/accessibility-audit/assets/browser", name), "utf8");
const { chromium } = await import("playwright").catch(() => import("playwright-core"));

const port = 8000 + Math.floor(Math.random() * 1000);
const server = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1", "--directory", root], { stdio: "ignore" });
const base = `http://127.0.0.1:${port}/examples/demo-site/`;

const failures = [];
const expect = (label, actual, expected) => {
  const ok = actual === expected;
  console.log(`${ok ? "ok  " : "FAIL"} ${label}: ${JSON.stringify(actual)}${ok ? "" : ` (expected ${JSON.stringify(expected)})`}`);
  if (!ok) failures.push(label);
};

async function waitForServer() {
  for (let i = 0; i < 50; i++) {
    try {
      if ((await fetch(base + "broken.html")).ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error("Demo server did not start.");
}

let browser;
const run = async (page, name) => page.evaluate(snippet(name));
try {
  await waitForServer();
  browser = await chromium.launch(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {});

  for (const [file, width] of [["broken.html", 1024], ["fixed.html", 1024], ["broken.html", 320], ["fixed.html", 320]]) {
    const page = await browser.newPage({ viewport: { width, height: 768 } });
    await page.goto(base + file);
    const tag = `${file}@${width}`;
    const broken = file === "broken.html";

    const inv = await run(page, "page-inventory.js");
    if (width === 1024) {
      expect(`${tag} lang`, inv.lang.value, broken ? "" : "en");
      expect(`${tag} headings`, inv.headings.count, broken ? 0 : 3);
      const counts = {
        images: [1, 0], unnamedControls: [4, 0], placeholderOnlyFields: [3, 0], labelInNameMismatches: [1, 0],
        clickableNonInteractive: [6, 0], positiveTabindex: [2, 0], focusableInsideAriaHidden: [1, 0],
        autocompleteCandidates: [3, 0], liveRegions: [0, 1],
      };
      for (const [key, [b, f]] of Object.entries(counts)) expect(`${tag} ${key}`, inv[key].count, broken ? b : f);

      const spacing = await run(page, "text-spacing.js");
      expect(`${tag} text-spacing clipped`, spacing.count, broken ? 1 : 0);
      expect(`${tag} text-spacing removable`, (await run(page, "text-spacing.js")).applied, false);
    }

    const target = await run(page, "target-size.js");
    expect(`${tag} target-size fail candidates`, target.failCandidates, broken ? 3 : 0);

    if (width === 320) {
      const reflow = await run(page, "reflow.js");
      expect(`${tag} reflow horizontal scroll`, reflow.pageScrollsHorizontally, broken);
      expect(`${tag} reflow overflowing`, reflow.overflowing.length, broken ? 1 : 0);
    }
    await page.close();
  }

  // Edge cases found in review: each is a small page with one known answer.
  const cases = [
    { name: "targets inside a focusable scroll region", width: 1024, snippet: "target-size.js", html: `<div tabindex="0" style="overflow:auto"><a href="#a" style="display:inline-block;width:12px;height:12px"></a><a href="#b" style="display:inline-block;width:12px;height:12px"></a></div>`, check: (r) => r.failCandidates, expected: 2 },
    { name: "targets inside an onclick wrapper", width: 1024, snippet: "target-size.js", html: `<div onclick="void 0"><a href="#a" style="display:inline-block;width:12px;height:12px"></a><a href="#b" style="display:inline-block;width:12px;height:12px"></a></div>`, check: (r) => r.failCandidates, expected: 2 },
    { name: "custom checkboxes measured by label", width: 1024, snippet: "target-size.js", html: `<label style="display:inline-block;width:16px;height:16px"><input type="checkbox" style="position:absolute;width:0;height:0;opacity:0"></label><label style="display:inline-block;width:16px;height:16px"><input type="checkbox" style="position:absolute;width:0;height:0;opacity:0"></label>`, check: (r) => r.failCandidates, expected: 2 },
    { name: "wide content inside an app shell", width: 320, snippet: "reflow.js", html: `<div style="height:100vh;overflow-y:auto"><div style="width:900px">wide</div></div>`, check: (r) => r.horizontalScrollRegions.length, expected: 1 },
    { name: "off-screen skip link", width: 320, snippet: "reflow.js", html: `<a href="#m" style="position:absolute;left:-9999px">Skip</a><main id="m">Hi</main>`, check: (r) => r.overflowing.length, expected: 0 },
    { name: "heading focus target with tabindex -1", width: 1024, snippet: "page-inventory.js", html: `<h1 tabindex="-1">Home</h1>`, check: (r) => r.unnamedControls.count, expected: 0 },
    { name: "button named by child svg aria-label", width: 1024, snippet: "page-inventory.js", html: `<button><svg role="img" aria-label="Close" width="10" height="10"></svg></button>`, check: (r) => r.unnamedControls.count, expected: 0 },
    { name: "field values are not labels", width: 1024, snippet: "page-inventory.js", html: `<select aria-label="Sort by"><option>Newest</option></select><input aria-label="Search" value="shoes">`, check: (r) => r.labelInNameMismatches.count, expected: 0 },
    { name: "aria-label hiding a visible label", width: 1024, snippet: "page-inventory.js", html: `<label for="q">Find</label><input id="q" aria-label="Search">`, check: (r) => r.labelInNameMismatches.count, expected: 1 },
    { name: "closed dialog inside aria-hidden", width: 1024, snippet: "page-inventory.js", html: `<div aria-hidden="true" style="display:none"><button>OK</button></div>`, check: (r) => r.focusableInsideAriaHidden.count, expected: 0 },
  ];
  for (const c of cases) {
    const page = await browser.newPage({ viewport: { width: c.width, height: 768 } });
    await page.setContent(`<!doctype html><html lang="en"><title>t</title><body style="margin:0">${c.html}</body></html>`);
    expect(`edge: ${c.name}`, c.check(await run(page, c.snippet)), c.expected);
    await page.close();
  }
} finally {
  await browser?.close();
  server.kill();
}

if (failures.length) {
  console.error(`\n${failures.length} snippet expectation(s) failed.`);
  process.exit(1);
}
console.log("\nAll snippet expectations match the answer key.");
