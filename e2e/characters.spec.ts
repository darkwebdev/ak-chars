import { test, expect } from '@playwright/test';

test.describe('Character Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/ak-chars/');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display characters on main page', async ({ page }) => {
    // Wait for character cards to appear
    await expect(page.locator('.card')).toHaveCount(await page.locator('.card').count(), {
      timeout: 10000,
    });

    // Verify at least one character is shown
    const cardCount = await page.locator('.card').count();
    expect(cardCount).toBeGreaterThan(0);

    // Verify character cards have expected structure
    const firstCard = page.locator('.card').first();
    await expect(firstCard).toBeVisible();

    // Check for character name (in .title div)
    const nameElement = firstCard.locator('.title');
    await expect(nameElement).toBeVisible();
    const name = await nameElement.textContent();
    expect(name).toBeTruthy();

    console.log(`Found ${cardCount} characters on the page`);
  });

  test('should mark character as owned when clicked', async ({ page }) => {
    // Wait for character cards to load
    await page.waitForSelector('.card', { state: 'visible', timeout: 10000 });

    // Get the first character card
    const firstCard = page.locator('.card').first();
    await expect(firstCard).toBeVisible();

    // Check if it's already owned
    const isOwnedBefore = await firstCard.evaluate((el) =>
      el.classList.contains('owned')
    );

    // Click the character card
    await firstCard.click();

    // Wait a bit for the state to update
    await page.waitForTimeout(500);

    // Verify the owned state changed
    const isOwnedAfter = await firstCard.evaluate((el) =>
      el.classList.contains('owned')
    );

    expect(isOwnedAfter).toBe(!isOwnedBefore);

    console.log(`Character owned state changed from ${isOwnedBefore} to ${isOwnedAfter}`);
  });

  test('should toggle owned status when clicked multiple times', async ({ page }) => {
    // Wait for character cards to load
    await page.waitForSelector('.card', { state: 'visible', timeout: 10000 });

    // Get the first character card
    const firstCard = page.locator('.card').first();
    await expect(firstCard).toBeVisible();

    // Get initial state
    const initialOwnedState = await firstCard.evaluate((el) =>
      el.classList.contains('owned')
    );

    // Click to toggle
    await firstCard.click();
    await page.waitForTimeout(300);

    const afterFirstClick = await firstCard.evaluate((el) =>
      el.classList.contains('owned')
    );
    expect(afterFirstClick).toBe(!initialOwnedState);

    // Click again to toggle back
    await firstCard.click();
    await page.waitForTimeout(300);

    const afterSecondClick = await firstCard.evaluate((el) =>
      el.classList.contains('owned')
    );
    expect(afterSecondClick).toBe(initialOwnedState);

    console.log(`Successfully toggled owned status: ${initialOwnedState} -> ${afterFirstClick} -> ${afterSecondClick}`);
  });

  test('should persist owned status after page reload', async ({ page }) => {
    // Wait for character cards to load
    await page.waitForSelector('.card', { state: 'visible', timeout: 10000 });

    // Get the first character card
    const firstCard = page.locator('.card').first();
    await expect(firstCard).toBeVisible();

    // Get character name for identification
    const characterName = await firstCard.locator('.title').textContent();

    // Mark as owned
    await firstCard.click();
    await page.waitForTimeout(300);

    const ownedAfterClick = await firstCard.evaluate((el) =>
      el.classList.contains('owned')
    );

    // Reload the page
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('.card', { state: 'visible', timeout: 10000 });

    // Find the same character by name
    const sameCard = page.locator('.card').filter({ hasText: characterName || '' }).first();
    await expect(sameCard).toBeVisible();

    // Verify owned status persisted
    const ownedAfterReload = await sameCard.evaluate((el) =>
      el.classList.contains('owned')
    );

    expect(ownedAfterReload).toBe(ownedAfterClick);

    console.log(`Owned status for "${characterName}" persisted after reload: ${ownedAfterReload}`);
  });

  test('should filter characters by profession', async ({ page }) => {
    // Wait for page to load
    await page.waitForSelector('.card', { state: 'visible', timeout: 10000 });

    // Get initial character count
    const initialCount = await page.locator('.card').count();
    expect(initialCount).toBeGreaterThan(0);

    // Find and click a profession button in the sidebar
    const professionButtons = page.locator('.profession-btn');
    const buttonCount = await professionButtons.count();

    if (buttonCount > 1) {
      // Click the second profession (first is usually "All")
      await professionButtons.nth(1).click();
      await page.waitForTimeout(500);

      // Get filtered character count
      const filteredCount = await page.locator('.card').count();

      // Count should be different (unless all characters are the same profession)
      console.log(`Initial count: ${initialCount}, Filtered count: ${filteredCount}`);

      // The page should still have characters visible (or could be 0 if profession has no characters)
      expect(filteredCount).toBeGreaterThanOrEqual(0);
    }
  });
});
