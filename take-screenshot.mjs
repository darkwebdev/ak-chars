import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5193/ak-chars/');
  await page.waitForLoadState('networkidle');
  await page.waitForSelector('.card', { state: 'visible', timeout: 10000 });
  
  // Click a few characters to make them owned
  const cards = page.locator('.card');
  await cards.nth(0).click();
  await page.waitForTimeout(500);
  await cards.nth(2).click();
  await page.waitForTimeout(500);
  await cards.nth(4).click();
  await page.waitForTimeout(500);
  
  // Move mouse away from cards to avoid hover state
  await page.mouse.move(0, 0);
  await page.waitForTimeout(200);
  
  // Take screenshot
  await page.screenshot({ path: 'character-ownership-state.png', fullPage: false });
  
  console.log('Screenshot saved to character-ownership-state.png');
  
  await browser.close();
})();
