import { expect, test } from '@playwright/test';

test.describe('Getting Started Tab', () => {
  test.describe('Full Flow Guide', () => {
    test('should navigate to full flow page', async ({ page }) => {
      await page.goto('/getting-started');

      await page.getByRole('link', { name: 'Explore more now' }).click();

      await expect(page).toHaveURL(/\/full-flow-guide/);
    });

    test('should display final step', async ({ page }) => {
      await page.goto('/full-flow-guide');

      // Smoothly scroll down in steps
      await page.evaluate(async () => {
        for (let i = 0; i < document.body.scrollHeight; i += 100) {
          window.scrollBy(0, 100); // Scroll down by 100px per step
          await new Promise((resolve) => setTimeout(resolve, 100)); // Wait 100ms for smooth effect
        }
      });

      // Ensure final step is visible
      await expect(page.getByText('Step 9')).toBeVisible();
    });
  });

  test.describe('Notebooks Examples Guide', () => {
    test('should navigate to notebooks page', async ({ page }) => {
      await page.goto('/getting-started');

      await page.getByRole('link', { name: 'Discover sample notebooks' }).click();

      await expect(page).toHaveURL(/\/notebooks/);
    });

    test('should navigate to New Notebook Page', async ({ page }) => {
      await page.goto('/notebooks');

      await page.getByRole('link', { name: 'New Notebook' }).click();

      await expect(page).toHaveURL('https://github.com/suenalaba/streamsightv2/pulls');
    });

    test('should navigate to sample notebook when clicked', async ({ page, context }) => {
      await page.goto('/notebooks');

      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

      const pagePromise = context.waitForEvent('page');
      await page.getByRole('link', { name: 'RecentPop Algorithm with MovieLens Dataset' }).click(); // Click the link
      const newPage = await pagePromise;

      await expect(newPage).toHaveURL(
        'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_recentpop.ipynb'
      );
    });
  });

  test.describe('Settings Configuration Guide', () => {
    test('should navigate to settings configuration guide page', async ({ page }) => {
      await page.goto('/getting-started');

      await page.getByRole('link', { name: 'Explore settings configurations' }).click();

      await expect(page).toHaveURL(/\/settings-configuration-guide/);
    });

    test('should display definition of last setting', async ({ page }) => {
      await page.goto('/settings-configuration-guide');

      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

      await expect(page.getByText('current_window')).toBeVisible();
    });
  });

  test.describe('Create Own Algorithm Guide', () => {
    test('should navigate to create algorithm guide page', async ({ page }) => {
      await page.goto('/getting-started');

      await page.getByRole('link', { name: 'Create your algorithm now' }).click();

      await expect(page).toHaveURL(/\/create-algorithm-guide/);
    });

    test('should display example of creating own algorithm', async ({ page, context }) => {
      await page.goto('/create-algorithm-guide');

      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

      const createOwnAlgoLink = page.getByRole('link', {
        name: 'https://github.com/suenalaba/streamsightv2/tree/master/streamsightv2/algorithms',
      });
      await expect(createOwnAlgoLink).toBeVisible();
      const pagePromise = context.waitForEvent('page');
      await createOwnAlgoLink.click();

      const newPage = await pagePromise;

      await expect(newPage).toHaveURL(
        'https://github.com/suenalaba/streamsightv2/tree/master/streamsightv2/algorithms'
      );
    });
  });
});
