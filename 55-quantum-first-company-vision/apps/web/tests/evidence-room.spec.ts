import { test, expect, type Page } from "@playwright/test";
import path from "node:path";
import fs from "node:fs/promises";

const names = [
  "Thesis Overview",
  "Evidence Graph",
  "ICP & JTBD Atlas",
  "Opportunity Comparator",
  "Scenario & Sensitivity Lab",
  "Experiment Backlog",
  "Risk / Kill-Gate Register",
  "Product Sequence",
  "Decision Log",
  "Handoff Export",
];
async function navigate(page: Page, name: string) {
  const toggle = page.getByRole("button", {
    name: "Evidence Room",
    exact: false,
  });
  if (
    (await toggle.isVisible()) &&
    (await toggle.getAttribute("aria-expanded")) === "false"
  )
    await toggle.click();
  await page
    .getByRole("navigation")
    .getByRole("button", { name, exact: false })
    .click();
  await expect(
    page.getByRole("heading", { name, exact: true, level: 1 }),
  ).toBeVisible();
}
async function bounded(page: Page) {
  const viewport = await page.evaluate(() => ({
    width: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  expect(viewport.scroll).toBeLessThanOrEqual(viewport.width);
}

test("all ten surfaces render real evidence with no page overflow", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Build on evidence/ }),
  ).toBeVisible();
  const capture = path.resolve(__dirname, "../../../reports/visual");
  await fs.mkdir(capture, { recursive: true });
  await page.screenshot({
    path: path.join(capture, `overview-${info.project.name}.png`),
    fullPage: true,
  });
  for (const name of names) {
    await navigate(page, name);
    await bounded(page);
  }
  const download = page.waitForEvent("download");
  await page
    .getByRole("link", { name: "Download candidate bundle", exact: false })
    .click();
  expect((await download).suggestedFilename()).toBe("company-vision-v1.zip");
  expect(await (await download).failure()).toBeNull();
  expect(errors).toEqual([]);
});

test("source tracing, contradictory evidence and empty results are inspectable", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Build on evidence/ }),
  ).toBeVisible();
  await navigate(page, "Evidence Graph");
  await page
    .getByLabel("Evidence stance", { exact: true })
    .selectOption("contradicts");
  await expect(page.locator(".evidence-table article").first()).toBeVisible();
  const first = page.locator(".evidence-table article").first();
  await first.getByRole("button").click();
  await expect(page.locator(".lineage")).toContainText("C3");
  expect(await first.getByRole("link").getAttribute("href")).toMatch(
    /^https:\/\//,
  );
  await page.getByLabel("Search evidence").fill("no-such-record-xyz");
  await expect(
    page.getByText("No matching evidence.", { exact: false }),
  ).toBeVisible();
  await bounded(page);
});

test("scenario controls recompute via API, reject invalid price and keep explicit hypotheses", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Build on evidence/ }),
  ).toBeVisible();
  await navigate(page, "Scenario & Sensitivity Lab");
  await page
    .getByLabel("Scenario", { exact: true })
    .selectOption("conservative");
  await page.getByLabel("Illustrative annual price (USD)").fill("6000");
  const response = page.waitForResponse(
    (r) => r.url().includes("/api/economics?") && r.status() === 200,
  );
  await page
    .getByRole("button", { name: "Recalculate scenario", exact: true })
    .click();
  expect((await (await response).json()).tam).toBe(1500000);
  await expect(
    page.getByText("Scenario recalculated by local API."),
  ).toBeVisible();
  await expect(page.locator(".metrics.economics")).toContainText("$1,500,000");
  await page.getByLabel("Illustrative annual price (USD)").fill("-1");
  expect(
    await page
      .getByLabel("Illustrative annual price (USD)")
      .evaluate((e: HTMLInputElement) => e.checkValidity()),
  ).toBe(false);
  await expect(
    page.getByText("not market measurements", { exact: false }),
  ).toBeVisible();
  await bounded(page);
});

test("loading, failure recovery, keyboard focus and reduced motion", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  let fail = true;
  let release!: () => void;
  const hold = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/room", async (route) => {
    if (fail) {
      await hold;
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: '{"error":"Test connection failure"}',
      });
    } else await route.continue();
  });
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Loading");
  release();
  await expect(page.getByRole("main").getByRole("alert")).toBeVisible();
  fail = false;
  await page.getByRole("button", { name: "Retry connection" }).click();
  await expect(
    page.getByRole("heading", { name: /Build on evidence/ }),
  ).toBeVisible();
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Build on evidence/ })).toBeVisible();
  await page.keyboard.press("Tab");
  await expect(page.locator(".skip")).toBeFocused();
  expect(
    await page
      .locator(".skip")
      .evaluate((e) => getComputedStyle(e).outlineStyle),
  ).not.toBe("none");
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();
  expect(
    await page.evaluate(
      () => matchMedia("(prefers-reduced-motion: reduce)").matches,
    ),
  ).toBe(true);
  await expect(page.locator(".error")).toHaveCount(0);
});
