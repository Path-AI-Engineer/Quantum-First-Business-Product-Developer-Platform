import { expect, test } from "@playwright/test";

test("navigates all twelve strategy views", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Win with evidence/ })).toBeVisible();
  const navigation = page.getByRole("complementary", { name: "Strategy Control Tower views" });
  for (const name of ["Strategy Thesis", "1 / 3 / 10 Roadmap", "Scenario Comparator", "Initiative Portfolio", "Capability Graph", "Architecture Evolution", "Capital & Unit Economics", "Risks, Signals & Gates", "Providers & Partners", "PQC / AI / Quantum Governance", "Organization & Talent", "Decision and Evidence Log"]) {
    const button = navigation.getByRole("button", { name: new RegExp(name.replaceAll("/", "\\/")) });
    await button.click();
    await expect(button).toHaveAttribute("aria-current", "page");
  }
});

test("exposes scenario and truth boundaries without overflow", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Scenario").selectOption("conservative");
  await expect(page.getByText("conservative case")).toBeVisible();
  await expect(page.getByText(/technical candidate unapproved/i)).toBeVisible();
  const viewport = await page.evaluate(() => ({ client: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  expect(viewport.scroll).toBeLessThanOrEqual(viewport.client);
});

test("supports focus visibility and reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const skipLink = page.getByRole("link", { name: "Skip to decision surface" });
  await skipLink.focus();
  await expect(skipLink).toBeFocused();
  await expect(page.locator("main")).toContainText("No cloud, staffing, product, or financial side effects.");
});
