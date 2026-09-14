import { expect, test } from "@playwright/test";

test("navigates ten evidence surfaces without page overflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Executive Posture" })).toBeVisible();
  await expect(page.getByText("125", { exact: true })).toHaveCount(0);
  const navigation = page.getByRole("navigation", { name: "Evidence surfaces" });
  for (const name of ["Cryptographic Inventory", "Evidence & Conflicts", "Exposure Heatmap",
    "Data-Lifetime Explorer", "Dependency Graph", "Migration Portfolio", "Standard/Vendor Watch",
    "Exceptions & Decisions", "Reports & Evidence Export", "Executive Posture"]) {
    const button = navigation.getByRole("button", { name: new RegExp(name.replace(/[&/]/g, ".")) });
    await button.click();
    await expect(button).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("heading", { name, exact: true })).toBeVisible();
  }
  const width = await page.evaluate(() => ({ client: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  expect(width.scroll).toBeLessThanOrEqual(width.client);
});

test("filters inventory, traces a finding, and reconciles report", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("navigation", { name: "Evidence surfaces" }).getByRole("button", { name: /Cryptographic Inventory/ }).click();
  await page.getByRole("textbox", { name: "Filter assets" }).fill("northstar-asset-000");
  await expect(page.getByText("1 assets shown")).toBeVisible();
  await page.getByRole("navigation", { name: "Evidence surfaces" }).getByRole("button", { name: /Evidence & Conflicts/ }).click();
  await expect(page.getByRole("heading", { name: "Finding evidence" })).toHaveCount(0);
  await expect(page.getByRole("region", { name: "Finding evidence" }).getByText("RSA-2048").first()).toBeVisible();
  await page.getByRole("navigation", { name: "Evidence surfaces" }).getByRole("button", { name: /Reports & Evidence Export/ }).click();
  await page.getByRole("button", { name: "Generate executive report" }).click();
  await expect(page.getByText(/45 assets · .* observations/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Download JSON" })).toBeVisible();
});

test("scopes tenants and blocks reviewer writes", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Organization").selectOption("aster");
  await expect(page.getByText("38", { exact: true }).first()).toBeVisible();
  await page.getByLabel("Demo role").selectOption("reviewer");
  await page.getByRole("navigation", { name: "Evidence surfaces" }).getByRole("button", { name: /Migration Portfolio/ }).click();
  await expect(page.getByRole("button", { name: "Propose lab wave" })).toBeDisabled();
});

test("supports keyboard focus and reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.keyboard.press("Tab");
  const focused = await page.evaluate(() => document.activeElement?.tagName);
  expect(focused).toBe("BUTTON");
  const motion = await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior);
  expect(motion).toBe("auto");
});

test("imports fictional evidence and records human-owned planning only", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Organization").selectOption("harbor");
  const navigation = page.getByRole("navigation", { name: "Evidence surfaces" });
  await navigation.getByRole("button", { name: /Evidence & Conflicts/ }).click();
  await page.getByRole("button", { name: "Import synthetic sample" }).click();
  await expect(page.getByRole("status").last()).toContainText("synthetic observation imported");
  await navigation.getByRole("button", { name: /Exceptions & Decisions/ }).click();
  await page.getByRole("button", { name: "Record synthetic decision" }).click();
  await expect(page.getByRole("status").last()).toContainText("does not change an asset");
  await navigation.getByRole("button", { name: /Migration Portfolio/ }).click();
  await page.getByRole("button", { name: "Propose lab wave" }).click();
  await expect(page.getByRole("status").last()).toContainText("no system change executed");
  await navigation.getByRole("button", { name: /Reports & Evidence Export/ }).click();
  await page.getByLabel("Report type").selectOption("delta");
  await page.getByRole("button", { name: "Generate delta report" }).click();
  await expect(page.getByText(/added observations/)).toBeVisible();
});
