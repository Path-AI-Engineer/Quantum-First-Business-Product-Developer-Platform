import { defineConfig } from "@playwright/test";
import path from "node:path";

const root = path.resolve(__dirname, "../..");
const python = process.platform === "win32" ? path.join(root, ".venv/Scripts/python.exe") : path.join(root, ".venv/bin/python");

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  forbidOnly: true,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: "list",
  use: { baseURL: "http://127.0.0.1:3058", trace: "retain-on-failure", screenshot: "only-on-failure" },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "tablet", use: { viewport: { width: 834, height: 1112 } } },
    { name: "mobile", use: { viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true } },
  ],
  webServer: [
    { command: `"${python}" -m uvicorn quantum_platform.api:app --app-dir src --host 127.0.0.1 --port 8058`, cwd: root, url: "http://127.0.0.1:8058/health", reuseExistingServer: false, timeout: 45_000 },
    { command: "node node_modules/next/dist/bin/next start --hostname 127.0.0.1 -p 3058", cwd: path.join(root, "apps/portal"), url: "http://127.0.0.1:3058", reuseExistingServer: false, timeout: 90_000 },
  ],
});

