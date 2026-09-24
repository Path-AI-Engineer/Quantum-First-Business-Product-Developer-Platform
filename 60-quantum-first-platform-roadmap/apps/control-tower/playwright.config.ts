import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

const root = path.resolve(__dirname, "../..");

export default defineConfig({
  testDir: "./tests",
  timeout: 45_000,
  workers: 3,
  reporter: "list",
  use: { baseURL: "http://127.0.0.1:8960", trace: "retain-on-failure", screenshot: "only-on-failure" },
  webServer: [
    { command: `.venv\\Scripts\\python.exe -m uvicorn strategy_control_tower.api:app --host 127.0.0.1 --port 8060`, cwd: root, url: "http://127.0.0.1:8060/health", reuseExistingServer: true, timeout: 120_000, env: { PYTHONPATH: `${path.join(root, "src")};${root}` } },
    { command: "npm run dev", cwd: __dirname, url: "http://127.0.0.1:8960", reuseExistingServer: true, timeout: 120_000 },
  ],
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } } },
    { name: "tablet", use: { ...devices["iPad Mini"] } },
    { name: "mobile", use: { ...devices["iPhone 13"] } },
  ],
});

