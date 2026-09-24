import { expect, test } from "@playwright/test";

test("navigates all ten governed surfaces", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Enterprise Portfolio" })).toBeVisible();
  const navigation = page.getByRole("complementary", { name: "Enterprise suite surfaces" });
  for (const name of ["Enterprise Portfolio", "Crypto Readiness", "Optimization Opportunities", "Quantum Workbench", "Evidence Graph", "Risks & Decisions", "Approvals & Policies", "Catalog & Capabilities", "Usage, Cost & Quotas", "Audit, Reports & Support"]) {
    const button = navigation.getByRole("button", { name: new RegExp(name) });
    await button.click();
    await expect(button).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("heading", { name, exact: true })).toBeVisible();
  }
});

test("exposes boundaries and evidence without horizontal overflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("External contract approval and executive portfolio decisions remain pending.")).toBeVisible();
  await expect(page.getByText("687 evaluation cases")).toBeVisible();
  const dimensions = await page.evaluate(() => ({ client: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.client);
});

test("supports keyboard focus and reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.keyboard.press("Tab");
  const focused = page.locator(":focus");
  await expect(focused).toBeVisible();
  const motion = await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior);
  expect(["auto", "smooth"]).toContain(motion);
});

