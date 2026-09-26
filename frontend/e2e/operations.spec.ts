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

test('JALA downstream intelligence withholds unvalidated travel time', async ({ page }) => {
  await login(page);
  await openNavItem(page, 'Predictions');
  await expect(page.getByText('JALA Downstream Threat Intelligence')).toBeVisible();
  await page.getByRole('button', { name: 'Evaluate downstream' }).click();
  await expect(page.getByText('NOT_CONFIGURED').first()).toBeVisible();
  await expect(page.getByText('UNAVAILABLE').first()).toBeVisible();
  await expect(page.getByText(/validated topology and travel-time basis/i)).toBeVisible();
});

test('digital twin exposes uncertainty and blind spots separately', async ({ page }) => {
  await login(page);
  await openNavItem(page, 'Digital Twin');
  await page.getByRole('button', { name: 'Refresh twin' }).click();
  await expect(page.getByText('Confidence', { exact: false }).first()).toBeVisible();
  await expect(page.getByText('Uncertainty', { exact: false }).first()).toBeVisible();
  await expect(page.getByText('Blind spots:', { exact: false }).first()).toBeVisible();
  await expect(page.getByText('NOT_CONFIGURED').first()).toBeVisible();
});
test('impact intelligence withholds exposure and safe-route claims',async({page})=>{await login(page);await openNavItem(page,'Impact & Evacuation');await page.getByRole('button',{name:'Evaluate current state'}).click();await expect(page.getByText('Population exposed: UNAVAILABLE')).toBeVisible();await expect(page.getByText('Guaranteed safe: NO')).toBeVisible();await expect(page.getByText('Verified zones: 0')).toBeVisible()});
test('CAP centre distinguishes export capability from delivery integration',async({page})=>{await login(page);await openNavItem(page,'CAP Warning Centre');await expect(page.getByRole('heading',{name:'CAP 1.2 Warning Centre'})).toBeVisible();await expect(page.getByText('NOT_CONFIGURED').first()).toBeVisible();await expect(page.getByText(/no official NDMA\/SACHET connection/i)).toBeVisible()});
test('continuity view labels unavailable transports and stale cache',async({page})=>{await login(page);await openNavItem(page,'Offline Continuity');await expect(page.getByText('LORA',{exact:true})).toBeVisible();await expect(page.getByText('PLANNED').first()).toBeVisible();await expect(page.getByText(/labeled CACHED and stale/i)).toBeVisible()});
test('security centre reports key configuration and audit-chain state',async({page})=>{await login(page);await openNavItem(page,'Security Event Centre');await expect(page.getByRole('heading',{name:'Security Event Centre'})).toBeVisible();await expect(page.getByText('NOT_CONFIGURED')).toBeVisible();await expect(page.getByText('VALID')).toBeVisible();await expect(page.getByText(/never returned to this client/i)).toBeVisible()});
