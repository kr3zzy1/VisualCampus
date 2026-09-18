import type { Job, University } from '../types';

// Прямой адрес бэкенда обходит проблемный прокси Vite
const API_BASE = 'http://127.0.0.1:8000';

async function req<T>(url: string, o?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...o
  });
  if (!r.ok) {
    const d = await r.json().catch(() => ({}));
    throw Error(d.detail || 'Request failed');
  }
  return r.json();
}

export const suggest = (q: string) => req<University[]>(`/api/universities/suggest?query=${encodeURIComponent(q)}`);
export const search = (query: string) => req<Job>('/api/search', { method: 'POST', body: JSON.stringify({ query }) });
export const job = (id: string) => req<Job>(`/api/search/${id}`);
export const select = (id: string, u: University) => req<Job>(`/api/search/${id}/select`, { method: 'POST', body: JSON.stringify(u) });