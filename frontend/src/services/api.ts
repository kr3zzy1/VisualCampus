import type { Job, University } from '../types';

// Оставляем пустым, чтобы запросы шли через прокси Vercel на один и тот же домен
const API_BASE = '';

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
