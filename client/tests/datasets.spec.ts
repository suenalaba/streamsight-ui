import { expect, test } from '@playwright/test';

test.describe('Datasets Tab', () => {
  test('should navigate to New Dataset Page', async ({ page }) => {
    await page.goto('/datasets');

    await page.getByRole('link', { name: 'New Dataset' }).click();

    await expect(page).toHaveURL('https://github.com/suenalaba/streamsightv2/issues');
  });

  test('should navigate to Amazon Music Data Page', async ({ page, context }) => {
    await page.goto('/datasets');

    const pagePromise = context.waitForEvent('page');
    await page.getByRole('link', { name: 'Amazon Music Data' }).click(); // Click the link
    const newPage = await pagePromise;

    await expect(newPage).toHaveURL('https://amazon-reviews-2023.github.io/');
    await expect(newPage).toHaveTitle("Amazon Reviews'23");
  });

  test('should navigate to LastFM Data Page', async ({ page, context }) => {
    await page.goto('/datasets');

    const pagePromise = context.waitForEvent('page');
    await page.getByRole('link', { name: 'LastFM Dataset' }).click(); // Click the link
    const newPage = await pagePromise;

    await expect(newPage).toHaveURL(
      'https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-readme.txt'
    );
  });

  test('should navigate to MovieLens Data Page', async ({ page, context }) => {
    await page.goto('/datasets');

    const pagePromise = context.waitForEvent('page');
    await page.getByRole('link', { name: 'MovieLens Dataset' }).click(); // Click the link
    const newPage = await pagePromise;

    await expect(newPage).toHaveURL('https://grouplens.org/datasets/movielens/100k/');
    await expect(newPage).toHaveTitle('MovieLens 100K Dataset | GroupLens');
  });

  test('should navigate to Yelp Data Page', async ({ page, context }) => {
    await page.goto('/datasets');

    const pagePromise = context.waitForEvent('page');
    await page.getByRole('link', { name: 'Yelp Dataset' }).click(); // Click the link
    const newPage = await pagePromise;

    await expect(newPage).toHaveURL('https://business.yelp.com/data/resources/open-dataset/');
    await expect(newPage).toHaveTitle('Open Dataset | Yelp Data Licensing');
  });

  test('should display all datasets when scrolling', async ({ page }) => {
    await page.goto('/datasets');

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    await expect(page.getByText(/Amazon Book Data/)).toBeVisible();
  });
});
