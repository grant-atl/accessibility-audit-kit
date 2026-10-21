// External validation: runs the snippets on W3C's Before and After Demonstration
// (https://www.w3.org/WAI/demos/bad/), an independent inaccessible site with a remediated twin.
// Needs network access. Install Playwright as for check-snippets.mjs, then:
//   node tests/browser/check-w3c-demo.mjs

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const snippet = (name) => readFileSync(join(root, "skills/accessibility-audit/assets/browser", name), "utf8");
const { chromium } = await import("playwright").catch(() => import("playwright-core"));

const failures = [];
const expect = (label, ok, detail) => {
  console.log(`${ok ? "ok  " : "FAIL"} ${label}: ${detail}`);
  if (!ok) failures.push(label);
};

const browser = await chromium.launch(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {});
try {
  for (const name of ["home", "news", "tickets", "survey"]) {
    const result = {};
    for (const version of ["before", "after"]) {
      const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
      await page.goto(`https://www.w3.org/WAI/demos/bad/${version}/${name}.html`);
      result[version] = await page.evaluate(snippet("page-inventory.js"));
      await page.close();
    }
    const { before, after } = result;
    expect(`${name} lang`, !before.lang.value && after.lang.value === "en", `before "${before.lang.value}", after "${after.lang.value}"`);
    expect(`${name} images without alternatives`, before.images.count > 0 && after.images.count === 0, `before ${before.images.count}, after ${after.images.count}`);
    expect(`${name} unnamed controls`, before.unnamedControls.count > 0 && after.unnamedControls.count === 0, `before ${before.unnamedControls.count}, after ${after.unnamedControls.count}`);
    expect(`${name} headings`, after.headings.count > before.headings.count, `before ${before.headings.count}, after ${after.headings.count}`);
  }
} finally {
  await browser.close();
}

if (failures.length) {
  console.error(`\n${failures.length} external expectation(s) failed.`);
  process.exit(1);
}
console.log("\nSnippets separate the W3C inaccessible and accessible demo pages as expected.");
