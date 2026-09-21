import { beforeEach, describe, expect, it, vi } from 'vitest';
import { readOperationalCache, writeOperationalCache } from './cache';

describe('operational cache', () => {
  beforeEach(() => { localStorage.clear(); vi.useFakeTimers(); });

  it('returns labeled cached data with its original timestamp', () => {
    vi.setSystemTime(new Date('2026-09-21T10:00:00Z'));
    writeOperationalCache('nodes', [{ id: 'JALA-01' }]);
    vi.setSystemTime(new Date('2026-09-21T10:01:00Z'));
    expect(readOperationalCache('nodes')).toEqual({
      data: [{ id: 'JALA-01' }], source: 'CACHED', fetchedAt: '2026-09-21T10:00:00.000Z', ageSeconds: 60,
    });
    vi.useRealTimers();
  });

  it('returns null for malformed cache entries', () => {
    localStorage.setItem('prahari_cache_nodes', '{bad json');
    expect(readOperationalCache('nodes')).toBeNull();
  });
});
