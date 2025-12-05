import React, { useState } from 'react';
import { fetchKroosterBrowser, parseKroosterHtml } from '../utils/krooster';

type Props = {
  username?: string;
  chars?: Array<{ id: string; name: string }>;
  // eslint-disable-next-line no-unused-vars
  onApply?: (names: string[], meta?: { fetched: boolean }) => void;
};

export function KroosterButton({ username = 'ines-shiny-thighs', chars = [], onApply }: Props) {
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [inputUsername, setInputUsername] = useState(username);
  const [usePaste, setUsePaste] = useState(false);
  const [pastedHtml, setPastedHtml] = useState('');
  const [useProxy, setUseProxy] = useState(false);
  const [proxyUrl, setProxyUrl] = useState('https://api.allorigins.win/raw?url=');

  async function run() {
    setLoading(true);
    setError(null);
    try {
      if (chars.length === 0) throw new Error('No characters provided');
      let importedChars: string[] = [];
      if (usePaste) {
        if (!pastedHtml.trim()) throw new Error('Please paste Krooster page HTML');
        importedChars = parseKroosterHtml(pastedHtml, chars);
      } else {
        if (!inputUsername.trim()) throw new Error('Username is required');
        importedChars = await fetchKroosterBrowser(
          inputUsername.trim(),
          chars,
          useProxy && proxyUrl ? proxyUrl : undefined,
        );
      }
      setCount(importedChars.length);
      if (onApply) {
        const ok =
          typeof window !== 'undefined'
            ? window.confirm(
                `Replace owned list with ${importedChars.length} characters from Krooster? This will overwrite your current owned list.`,
              )
            : true;
        if (ok) onApply(importedChars, { fetched: !usePaste });
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
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            type="checkbox"
            checked={usePaste}
            onChange={(e) => setUsePaste(e.target.checked)}
            disabled={loading}
          />
          Paste Krooster HTML
        </label>

        <label style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            type="checkbox"
            checked={useProxy}
            onChange={(e) => setUseProxy(e.target.checked)}
            disabled={loading}
          />
          Use CORS proxy
        </label>

        {useProxy && (
          <input
            type="text"
            placeholder="Proxy prefix (use {url} to insert encoded URL)"
            value={proxyUrl}
            onChange={(e) => setProxyUrl(e.target.value)}
            disabled={loading}
            style={{
              padding: '6px 10px',
              borderRadius: '4px',
              border: '1px solid #1f2a37',
              background: '#071017',
              color: '#e6eef6',
              fontSize: '13px',
              minWidth: 260,
            }}
          />
        )}
        {useProxy && (
          <div style={{ fontSize: 12, color: '#9fb0c8' }}>
            Will try your proxy first, then a couple of public proxies if it fails.
          </div>
        )}

        {!usePaste && (
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
        )}
        {usePaste && (
          <textarea
            placeholder="Paste Krooster page HTML here (press Import to parse)"
            value={pastedHtml}
            onChange={(e) => setPastedHtml(e.target.value)}
            disabled={loading}
            style={{
              minWidth: 400,
              minHeight: 120,
              padding: 8,
              background: '#071017',
              color: '#e6eef6',
              border: '1px solid #1f2a37',
              borderRadius: 4,
            }}
          />
        )}
      </div>

      <button onClick={run} disabled={loading}>
        {loading ? 'Running…' : 'Import from Krooster'}
      </button>
      {count != null && <span>{count} operators imported</span>}
      {error && <span style={{ color: 'red' }}>{error}</span>}
    </div>
  );
}
