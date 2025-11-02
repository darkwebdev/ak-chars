import React, { useState } from 'react';
import { fetchKroosterBrowser } from '../utils/krooster';

type Props = {
  username?: string;
  kroosterNames?: string[];
  // eslint-disable-next-line no-unused-vars
  onApply?: (names: string[]) => void;
};

export function KroosterButton(props: Props) {
  const { username = 'tibalt', kroosterNames = [], onApply } = props;
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      if (!kroosterNames || kroosterNames.length === 0)
        throw new Error('No character names provided');
      const res = await fetchKroosterBrowser(username, kroosterNames);
      setCount(res.length);
      if (onApply) {
        const ok =
          typeof window !== 'undefined'
            ? window.confirm(
                `Replace owned list with ${res.length} characters from Krooster? This will overwrite your current owned list.`,
              )
            : true;
        if (ok) onApply(res);
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <button onClick={run} disabled={loading}>
        {loading ? 'Running…' : 'Fetch Krooster'}
      </button>
      {count != null && <span>{count} visible chars</span>}
      {error && <span style={{ color: 'red' }}>{error}</span>}
    </div>
  );
}
