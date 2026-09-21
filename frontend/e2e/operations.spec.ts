import { expect, test } from '@playwright/test';

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
