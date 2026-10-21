// Eval fixture: Playwright starts a static server so test:a11y is self-contained.
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  webServer: {
    command: "python3 -m http.server 3000 --bind 127.0.0.1 --directory public",
    url: "http://127.0.0.1:3000/",
    reuseExistingServer: !process.env.CI,
  },
});
