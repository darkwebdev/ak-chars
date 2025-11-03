import React, { useState } from 'react';
import { fetchKroosterBrowser } from '../utils/krooster';

type Props = {
  username?: string;
  chars?: Array<{ id: string; name: string }>;
  // eslint-disable-next-line no-unused-vars
  onApply?: (names: string[]) => void;
};

export function KroosterButton({ username = 'ines-shiny-thighs', chars = [], onApply }: Props) {
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [inputUsername, setInputUsername] = useState(username);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      if (chars.length === 0) throw new Error('No characters provided');
      if (!inputUsername.trim()) throw new Error('Username is required');
      const importedChars = await fetchKroosterBrowser(inputUsername.trim(), chars);
      setCount(importedChars.length);
      if (onApply) {
        const ok =
          typeof window !== 'undefined'
            ? window.confirm(
                `Replace owned list with ${importedChars.length} characters from Krooster? This will overwrite your current owned list.`,
              )
            : true;
        if (ok) onApply(importedChars);
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
      <input
        type="text"
        placeholder="Krooster username"
        value={inputUsername}
        onChange={(e) => setInputUsername(e.target.value)}
        disabled={loading}
        style={{
          padding: '8px 12px',
          borderRadius: '4px',
          border: '1px solid #1f2a37',
          background: '#0b1220',
          color: '#e6eef6',
          fontSize: '14px',
          minWidth: '200px',
        }}
      />
      <button onClick={run} disabled={loading}>
        {loading ? 'Running…' : 'Import from Krooster'}
      </button>
      {count != null && <span>{count} operators imported</span>}
      {error && <span style={{ color: 'red' }}>{error}</span>}
    </div>
  );
}
