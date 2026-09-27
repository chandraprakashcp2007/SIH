export type CachedOperationalData<T> = {
  data: T;
  source: 'CACHED';
  stale: true;
  fetchedAt: string;
  ageSeconds: number;
};

const prefix = 'prahari_cache_';

export function writeOperationalCache<T>(key: string, data: T): void {
  localStorage.setItem(`${prefix}${key}`, JSON.stringify({ data, fetchedAt: new Date().toISOString() }));
}

export function readOperationalCache<T>(key: string): CachedOperationalData<T> | null {
  try {
    const raw = localStorage.getItem(`${prefix}${key}`);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed?.fetchedAt || !('data' in parsed)) return null;
    return {
      data: parsed.data,
      source: 'CACHED',
      stale: true,
      fetchedAt: parsed.fetchedAt,
      ageSeconds: Math.max(0, Math.round((Date.now() - new Date(parsed.fetchedAt).getTime()) / 1000)),
    };
  } catch {
    return null;
  }
}

function authFailure(status: number) {
  return status === 401 || status === 403;
}

export async function fetchOperationalJson<T>(key: string, url: string, init?: RequestInit): Promise<T> {
  try {
    const response = await fetch(url, init);
    if (!response.ok) {
      const error: any = new Error(`Request failed (${response.status})`);
      error.status = response.status;
      error.disableCacheFallback = authFailure(response.status);
      if (response.status === 401 && typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('prahari:auth-required', { detail: { status: response.status } }));
      }
      throw error;
    }
    const data = await response.json() as T;
    writeOperationalCache(key, data);
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      return { ...data, _dataState: { source: 'LIVE', fetchedAt: new Date().toISOString(), ageSeconds: 0 } };
    }
    return data;
  } catch (error: any) {
    if (error?.disableCacheFallback) throw error;
    const cached = readOperationalCache<T>(key);
    if (!cached) throw error;
    if (cached.data && typeof cached.data === 'object' && !Array.isArray(cached.data)) {
      return { ...cached.data, _dataState: { source: cached.source, fetchedAt: cached.fetchedAt, ageSeconds: cached.ageSeconds } };
    }
    return cached.data;
  }
}
