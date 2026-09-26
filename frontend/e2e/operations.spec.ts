import { expect, test } from '@playwright/test';

test.afterEach(async ({ page }) => {
  // Let in-flight authenticated reads release SQLite sessions before the
  // browser context is torn down and its requests are cancelled.
  await page.waitForTimeout(1000);
});

async function login(page: any, username = 'admin') {
  await page.goto('/login');
  await expect(page.getByText('DEV AUTH BYPASS')).toBeVisible();
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill('local-demo');
  await page.getByRole('button', { name: 'Access Command Centre' }).click();
  await expect(page).toHaveURL(/\/$/);
}

async function openNavItem(page: any, name: string) {
  if ((page.viewportSize()?.width || 1000) < 768) {
    await expect(page.getByLabel('Open navigation')).toBeVisible();
    await page.getByLabel('Open navigation').click();
  }
  await page.getByText(name, { exact: true }).click();
}

test('login, readiness, Copilot and core navigation', async ({ page }) => {
  await login(page);
  await expect(page.getByText('FLEET STATUS')).toBeVisible();
  await openNavItem(page, 'System Readiness');
  await expect(page.getByRole('heading', { name: 'System Readiness' })).toBeVisible();
  await page.getByLabel('Open PRAHARI Copilot').click();
  await page.getByLabel('Ask PRAHARI Copilot').fill('How is the system?');
  await page.getByLabel('Send message').click();
  await expect(page.getByText(/PRAHARI.*system|nodes|risk/i).last()).toBeVisible({ timeout: 15_000 });
});

test('admin can drive flood and recovery scenarios', async ({ page }) => {
  await login(page);
  await openNavItem(page, 'Simulator');
  await page.getByRole('button', { name: 'Engage Flood Water Ramp' }).click();
  await expect(page.getByText(/FLOOD_RAMP|Flood Water Ramp/i).first()).toBeVisible();
  await page.getByRole('button', { name: /Reset/i }).first().click();
});

test('five dedicated domain intelligence maps expose truthful layer states', async ({ page }) => {
  await login(page);
  const domains = [
    ['jala', 'JALA River & Flood Intelligence'],
    ['agni', 'AGNI Fire Intelligence'],
    ['bhumi', 'BHUMI Terrain & Landslide Intelligence'],
    ['vayu', 'VAYU Air & Smoke Intelligence'],
    ['akasha', 'AKASHA Weather Intelligence'],
  ];
  for (const [path, heading] of domains) {
    await page.goto(`/live/${path}`);
    await expect(page.getByRole('heading', { name: heading })).toBeVisible();
    await expect(page.getByText('Operational layers')).toBeVisible();
    await expect(page.getByText(/Data limitation:/)).toBeVisible();
  }
});

test('cross-hazard intelligence exposes rule provenance and consensus limits', async ({ page }) => {
  await login(page);
  await openNavItem(page, 'Cross-Hazard Intelligence');
  await expect(page.getByRole('heading', { name: 'Cross-Hazard Intelligence' })).toBeVisible();
  await page.getByRole('button', { name: 'Reevaluate' }).click();
  await expect(page.getByText('CONFIGURED_RELATIONSHIP').first()).toBeVisible();
  await expect(page.getByText('TRANSPARENT_RULE').first()).toBeVisible();
  await expect(page.getByText('INSUFFICIENT_NEIGHBOURS').first()).toBeVisible();
});
