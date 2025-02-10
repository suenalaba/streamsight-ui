import { expect, test } from '@playwright/test';

test.describe('Navigation Bar', () => {
  test('should navigate to datasets page', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: 'Datasets' }).click();

    await expect(page).toHaveURL(/\/datasets/);
  });

  test('should navigate to getting started page', async ({ page }) => {
    await page.goto('/datasets');

    await page.getByRole('link', { name: 'Getting Started' }).click();

    await expect(page).toHaveURL(/\/getting-started/);
  });

  test('should navigate to stream dashboard page', async ({ page }) => {
    await page.goto('/getting-started');

    await page.getByRole('link', { name: 'Stream Management' }).click();

    const streamDashboardButton = page.getByRole('link', { name: 'Stream Dashboard' });

    await expect(streamDashboardButton).toBeVisible();
    await streamDashboardButton.click();

    await expect(page).toHaveURL('/stream');
    await expect(page.getByRole('heading', { name: 'Stream Dashboard' })).toBeVisible();
    await expect(page.getByText(/No Rows To Show/)).toBeVisible();
  });

  test('should navigate to create stream page', async ({ page }) => {
    await page.goto('/stream');

    await page.getByRole('link', { name: 'Stream Management' }).click();

    const createStreamButton = page.getByRole('link', { name: 'Create Stream' });

    await expect(createStreamButton).toBeVisible();
    await createStreamButton.click();

    await expect(page).toHaveURL('/stream/create');
    await expect(page.getByRole('heading', { name: 'Create Stream' })).toBeVisible();
  });

  test('should navigate to home page', async ({ page }) => {
    await page.goto('/stream/create');

    await page.getByRole('link', { name: 'Home' }).click();

    await expect(page).toHaveURL('/');
    await expect(page.getByText(/Level up with Streamsight/)).toBeVisible();
  });
});
