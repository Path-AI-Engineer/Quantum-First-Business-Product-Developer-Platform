import { expect, test } from "@playwright/test";

const surfaces = ["Quickstart", "API Reference", "Capability Catalog", "API Keys & Environments", "Job Explorer", "Artifact Inspector", "Webhook Workbench", "Usage & Quotas", "Audit & Correlation", "Status / SLO Lab"];

async function navigation(page: import("@playwright/test").Page) {
  const menu = page.getByRole("button", { name: "Menu" });
  const sidebar = page.getByRole("complementary", { name: "Developer portal surfaces" });
  if ((await menu.isVisible()) && !(await sidebar.isVisible())) await menu.click();
  return sidebar;
}

test("navigates every evidence surface", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Run a quantum-ready job in minutes" })).toBeVisible();
  for (const label of surfaces) {
    const nav = await navigation(page);
    const button = nav.getByRole("button", { name: label, exact: true });
    await button.click();
    if (label !== "Quickstart") {
      const reopened = await navigation(page);
      await expect(reopened.getByRole("button", { name: label, exact: true })).toHaveAttribute("aria-current", "page");
    }
  }
});

test("has bounded responsive layout and keyboard focus", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.locator(":focus-visible")).toBeVisible();
  const sizes = await page.evaluate(() => ({ client: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  expect(sizes.scroll).toBeLessThanOrEqual(sizes.client);
  await navigation(page);
  await expect(page.getByText("No arbitrary code. No cloud credentials. No commercial SLA.")).toBeVisible();
});

test("renders live capability evidence through the API proxy", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("25 provider-operation records")).toBeVisible();
  await expect(page.getByText("Cloud spend")).toBeVisible();
  await expect(page.getByText("$0.00")).toBeVisible();
});
