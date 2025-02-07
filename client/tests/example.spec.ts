import { expect, test } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Playwright/);
});

test('get started link', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Click the get started link.
  await page.getByRole('link', { name: 'Get started' }).click();

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
});

test('visit home page', async ({ page }) => {
  await page.goto('/');

  // Scroll down to make sure the text is visible
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

  // Wait for the text to be visible in the DOM
  await expect(page.locator('text=Healthcheck status: success')).toBeVisible();
});
