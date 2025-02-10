import { expect, test } from '@playwright/test';

test.describe('Home Page', () => {
  test('visit home page', async ({ page }) => {
    await page.goto('/');

    // Scroll down to make sure the text is visible
    // Smoothly scroll down in steps
    await page.evaluate(async () => {
      for (let i = 0; i < document.body.scrollHeight; i += 100) {
        window.scrollBy(0, 100); // Scroll down by 100px per step
        await new Promise((resolve) => setTimeout(resolve, 100)); // Wait 100ms for smooth effect
      }
    });

    // Wait for the text to be visible in the DOM
    await expect(page.locator('text=Healthcheck status: success')).toBeVisible();
  });
});
