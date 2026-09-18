import { expect, test } from "@playwright/test";

const surfaces = [
  "Opportunity Intake",
  "Eligibility Scorecard",
  "Problem Formulation",
  "Constraint & Feasibility Inspector",
  "Benchmark Arena",
  "Solution Comparison",
  "Value & Sensitivity Studio",
  "Quantum-Readiness Gate",
  "Pilot Builder",
  "Proposal & Evidence Export",
];

test("navigates ten evidence surfaces without page overflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Prove the decision is worth optimizing." })).toBeVisible();
  const navigation = page.getByRole("complementary", { name: "Validation lab surfaces" });
  for (const surface of surfaces) {
    const button = navigation.getByRole("button", { name: new RegExp(surface) });
    await button.click();
    await expect(button).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("heading", { name: surface })).toBeVisible();
  }
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth);
});

test("creates, assesses, values, pilots, and exports synthetic evidence", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Record synthetic opportunity" }).click();
  await expect(page.getByText("Opportunity recorded with synthetic inputs")).toBeVisible();
  await page.getByRole("button", { name: /Eligibility Scorecard/ }).click();
  await page.getByRole("button", { name: "Assess opportunity" }).click();
  await expect(page.getByText("EXPERIMENT_QUANTUM_READY", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: /Value & Sensitivity Studio/ }).click();
  await page.getByRole("button", { name: "Calculate scenario" }).click();
  await expect(page.getByText("annualized_value_range", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: /Pilot Builder/ }).click();
  await page.getByRole("button", { name: "Draft pilot" }).click();
  await expect(page.getByText('"auto_actuation": false', { exact: false })).toBeVisible();
  await page.getByRole("button", { name: /Proposal & Evidence Export/ }).click();
  await page.getByRole("button", { name: "Create candidate" }).click();
  await expect(page.getByText("technical_candidate_unapproved", { exact: false })).toBeVisible();
});

test("enforces the read-only reviewer boundary", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Demo identity").selectOption("risk-reviewer");
  await page.getByRole("button", { name: "Record synthetic opportunity" }).click();
  await expect(page.getByText("identity is read-only")).toBeVisible();
  await page.getByRole("button", { name: /Benchmark Arena/ }).click();
  await expect(page.getByRole("button", { name: "Run local development benchmark" })).toBeDisabled();
});

test("exposes keyboard focus and reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.locator(":focus")).toBeVisible();
  const reduced = await page.evaluate(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
  expect(reduced).toBe(true);
});

test("keeps quantum and economics claims bounded", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Quantum-Readiness Gate/ }).click();
  await expect(page.getByText("Quantum advantage")).toBeVisible();
  await expect(page.getByText("not claimed")).toBeVisible();
  await page.getByRole("button", { name: /Value & Sensitivity Studio/ }).click();
  await expect(page.getByText("Ranges, never promises")).toBeVisible();
});
