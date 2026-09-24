import { defineConfig } from "@playwright/test";
import path from "node:path";

const root = path.resolve(__dirname, "../..");
const python =
  process.platform === "win32"
    ? path.join(root, ".venv/Scripts/python.exe")
    : path.join(root, ".venv/bin/python");

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  forbidOnly: true,
  retries: 0,
  maxFailures: 1,
  timeout: 60000,
  expect: { timeout: 10000 },
  reporter: [
    ["list"],
    ["json", { outputFile: "../../reports/week-223/playwright.local.json" }],
  ],
  use: {
    actionTimeout: 15000,
    baseURL: "http://127.0.0.1:3055",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 1000 } } },
    { name: "tablet", use: { viewport: { width: 834, height: 1112 } } },
    {
      name: "mobile",
      use: {
        viewport: { width: 375, height: 812 },
        isMobile: true,
        hasTouch: true,
      },
    },
  ],
  webServer: [
    {
      command: `"${python}" -m uvicorn venture_evidence.api:app --host 127.0.0.1 --port 8955`,
      cwd: root,
      url: "http://127.0.0.1:8955/health",
      reuseExistingServer: false,
      timeout: 30000,
    },
    {
      command:
        "node node_modules/next/dist/bin/next start --hostname 127.0.0.1 -p 3055",
      url: "http://127.0.0.1:3055",
      reuseExistingServer: false,
      timeout: 60000,
    },
  ],
});
