import { useEffect, useState } from 'react';
import type { Category, Job, University } from './types';
import { select, job as getSearchJob, search, suggest } from './services/api';
import ImageCard from './components/ImageCard';

const labels: Record<Category, string> = {
  campus: 'Campus',
  dormitory: 'Dormitories',
  classroom: 'Classrooms',
  library: 'Libraries',
  city: 'City',
  sports: 'Sports',
  laboratories: 'Laboratories',
  student_life: 'Student life'
};

const categories = Object.keys(labels) as Category[];

export default function App() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<University[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<Category | 'all'>('all');

  useEffect(() => {
    if (query.trim().length < 2) {
      setSuggestions([]);
      return;
    }
    const t = window.setTimeout(
      () => suggest(query).then(setSuggestions).catch(() => setSuggestions([])),
      300
    );
    return () => window.clearTimeout(t);
  }, [query]);

  async function track(next: Job) {
    setJob(next);
    if (next.status === 'processing') {
      const timer = window.setInterval(async () => {
        try {
          const updated = await getSearchJob(next.id);
          setJob(updated);
          if (updated.status !== 'processing') window.clearInterval(timer);
        } catch {
          window.clearInterval(timer);
          setError('Unable to receive search progress.');
        }
      }, 800);
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setJob(null);
    setSuggestions([]);
    try {
      await track(await search(query));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Search failed');
    }
  }

  const hasImages =
    job?.profile?.categories &&
    categories.some((c) => (job.profile?.categories?.[c]?.length ?? 0) > 0);

  return (
    <main>
      <header>
        <h1>University Visual Profile</h1>
        <p>Source-linked campus research, with honest verification signals.</p>
        <form onSubmit={submit}>
          <div className="search-wrap">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Start typing a university name or abbreviation"
              autoComplete="off"
            />
            {suggestions.length > 0 && (
              <div className="suggestions">
                {suggestions.map((u) => (
                  <button
                    type="button"
                    key={u.name}
                    onClick={() => {
                      setQuery(u.name);
                      setSuggestions([]);
                    }}
                  >
                    <strong>{u.name}</strong>
                    <small>University entity</small>
                  </button>
                ))}
              </div>
            )}
          </div>
          <button>Search</button>
        </form>
      </header>

      {error && <div className="notice error">{error}</div>}

      {job?.status === 'ambiguous' && (
        <section className="notice">
          <h2>Choose a university</h2>
          {job.candidates.map((u) => (
            <button
              className="choice"
              key={u.name}
              onClick={() => select(job.id, u).then(track)}
            >
              {u.name}
            </button>
          ))}
        </section>
      )}

      {job?.status === 'processing' && (
        <section className="progress">
          <h2>Analyzing {query}</h2>
          {job.progress.map((p, i) => (
            <p key={i}>
              <span>✓</span>
              {p}
            </p>
          ))}
          <p className="muted">Only traceable sources are included.</p>
        </section>
      )}

      {job?.status === 'failed' && <div className="notice error">{job.error}</div>}

      {job?.profile && (
        <section className="profile">
          <div className="profile-head">
            <div>
              <span className="eyebrow">VERIFIED RESEARCH PROFILE</span>
              <h2>{job.profile.university?.name}</h2>
              <p>
                {[
                  job.profile.university?.region,
                  job.profile.university?.country
                ]
                  .filter(Boolean)
                  .join(', ') || 'Location metadata unavailable'}
              </p>
              {job.profile.university?.website && (
                <a
                  href={job.profile.university.website}
                  target="_blank"
                  rel="noreferrer"
                >
                  Official website ↗
                </a>
              )}
            </div>
            <div className="score">
              {hasImages ? 'Sources found' : 'No photos'}
              <small>research status</small>
            </div>
          </div>

          {job.profile.summary && (
            <div className="summary-card" style={{ background: 'white', border: '1px solid #dce3de', borderRadius: '16px', padding: '24px 28px', margin: '28px 0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.03)' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '1.1rem', color: '#183e2f', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>📖</span> University Overview & Academic Profile
              </h3>
              <p style={{ margin: 0, fontSize: '1.05rem', lineHeight: '1.7', color: '#2b3d33' }}>
                {job.profile.summary}
              </p>
            </div>
          )}

          {hasImages ? (
            <>
              <nav>
                <button
                  className={filter === 'all' ? 'active' : ''}
                  onClick={() => setFilter('all')}
                >
                  All
                </button>
                {categories.map((c) => (
                  <button
                    className={filter === c ? 'active' : ''}
                    onClick={() => setFilter(c)}
                    key={c}
                  >
                    {labels[c]}
                  </button>
                ))}
              </nav>

              {categories
                .filter((c) => filter === 'all' || filter === c)
                .map(
                  (c) =>
                    (job.profile?.categories?.[c]?.length ?? 0) > 0 && (
                      <section className="category" key={c}>
                        <h2>{labels[c]}</h2>
                        <div className="grid">
                          {job.profile!.categories[c].map((i: any) => (
                            <ImageCard 
                              key={i.id || Math.random()} 
                              photo={{
                                id: i.id || String(Math.random()),
                                url: i.url || i.image_url || '',
                                source: i.source || i.source_name || 'Wikimedia Commons'
                              }} 
                            />
                          ))}
                        </div>
                      </section>
                    )
                )}
            </>
          ) : (
            <div className="notice">
              <h2>University found, but no verified photos</h2>
              <p>
                Choose a suggestion or try the university’s full official name.
                Missing sources are never replaced with fake images.
              </p>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
