import { expect, test } from '@playwright/test';

test.describe('Create Stream Tab', () => {
  test('should fail to create stream if dataset is not selected', async ({ page }) => {
    await page.goto('/stream/create');

    await page.getByLabel('Top K').fill('2');

    await page.getByRole('textbox', { name: 'Metrics' }).click();
    await page.getByRole('option', { name: 'PrecisionK' }).click();
    await page.getByRole('option', { name: 'RecallK' }).click();

    await page.getByLabel('Background Timestamp').fill('4');

    await page.getByLabel('Window Size').fill('3');

    await page.getByRole('button', { name: 'Create Stream' }).click();

    await expect(page.getByText(/Dataset ID is required/)).toBeVisible();
  });

  test('should fail to create stream if metrics is not selected', async ({ page }) => {
    await page.goto('/stream/create');

    await page.getByRole('textbox', { name: 'Dataset' }).fill('test');
    await page.getByRole('option', { name: 'test' }).click();

    await page.getByLabel('Top K').fill('2');

    await page.getByLabel('Background Timestamp').fill('4');

    await page.getByLabel('Window Size').fill('3');

    await page.getByRole('button', { name: 'Create Stream' }).click();

    await expect(page.getByText(/At least one metric is required/)).toBeVisible();
  });

  test('should fail to create stream when user not logged in', async ({ page }) => {
    await page.goto('/stream/create');

    await page.getByRole('textbox', { name: 'Dataset' }).fill('test');
    await page.getByRole('option', { name: 'test' }).click();

    await page.getByLabel('Top K').fill('2');

    await page.getByRole('textbox', { name: 'Metrics' }).click();
    await page.getByRole('option', { name: 'PrecisionK' }).click();
    await page.getByRole('option', { name: 'RecallK' }).click();

    await page.getByLabel('Background Timestamp').fill('4');

    await page.getByLabel('Window Size').fill('3');

    await page.getByRole('button', { name: 'Create Stream' }).click();

    await expect(page.getByText(/Failed to create stream/)).toBeVisible();
  });
});
