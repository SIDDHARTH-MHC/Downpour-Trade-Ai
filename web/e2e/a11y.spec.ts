import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

function criticalViolations(results: Awaited<ReturnType<AxeBuilder["analyze"]>>) {
  return results.violations.filter((v) => v.impact === "critical" || v.impact === "serious");
}

test.describe("accessibility", () => {
  test("dashboard has no serious/critical axe violations", async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector("h1", { timeout: 30_000 });
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(criticalViolations(results), formatViolations(results)).toEqual([]);
  });

  test("glossary has no serious/critical axe violations", async ({ page }) => {
    await page.goto("/glossary");
    await page.waitForSelector("h1");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(criticalViolations(results), formatViolations(results)).toEqual([]);
  });

  test("pair page shell when analyze loads", async ({ page }) => {
    test.skip(!process.env.A11Y_PAIR_URL, "Set A11Y_PAIR_URL=1 when API is reachable in CI");
    await page.goto("/pair/BTC%2FUSDT", { waitUntil: "domcontentloaded", timeout: 60_000 });
    await page.waitForSelector("h1", { timeout: 60_000 });
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(criticalViolations(results), formatViolations(results)).toEqual([]);
  });
});

function formatViolations(results: Awaited<ReturnType<AxeBuilder["analyze"]>>) {
  return criticalViolations(results)
    .map((v) => `${v.id}: ${v.help} (${v.nodes.length} nodes)`)
    .join("\n");
}
