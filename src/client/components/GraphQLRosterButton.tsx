import React, { useState } from 'react';
import { useGetMyRoster } from '../utils/graphqlHooks';

type Props = {
  chars?: Array<{ id: string; name: string }>;
  onApply?: (charIds: string[]) => void;
};

export function GraphQLRosterButton({ chars = [], onApply }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [channelUid, setChannelUid] = useState('');
  const [yostarToken, setYostarToken] = useState('');
  const { getRoster, loading: fetchingRoster, error: fetchError } = useGetMyRoster();

  const handleImportRoster = async () => {
    if (!channelUid.trim()) {
      setError('Channel UID is required');
      return;
    }
    if (!yostarToken.trim()) {
      setError('Yostar Token is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const roster = await getRoster(channelUid.trim(), yostarToken.trim(), 'en');

      if (chars.length === 0) {
        throw new Error('No characters provided');
      }

      // Map charId from roster to our character IDs
      const charIdSet = new Set(roster.map((op) => op.charId));
      const importedIds = chars.filter((ch) => charIdSet.has(ch.id)).map((ch) => ch.id);

      if (importedIds.length === 0) {
        setError('No matching characters found');
        return;
      }

      if (onApply) {
        const ok =
          typeof window !== 'undefined'
            ? window.confirm(
                `Import ${importedIds.length} characters from your Arknights account? This will replace your current owned list.`
              )
            : true;

        if (ok) {
          onApply(importedIds);
          setShowForm(false);
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: 12 }}>
      <button onClick={() => setShowForm(!showForm)} style={{ marginBottom: showForm ? 8 : 0 }}>
        {showForm ? 'Hide Import' : 'Import from Arknights Account'}
      </button>

      {showForm && (
        <>
          <div style={{ display: 'flex', gap: 8, flexDirection: 'column', marginTop: 8 }}>
            <input
              type="text"
              placeholder="Channel UID"
              value={channelUid}
              onChange={(e) => setChannelUid(e.target.value)}
              style={{ padding: 8 }}
              disabled={loading || fetchingRoster}
            />
            <input
              type="password"
              placeholder="Yostar Token"
              value={yostarToken}
              onChange={(e) => setYostarToken(e.target.value)}
              style={{ padding: 8 }}
              disabled={loading || fetchingRoster}
            />
            <button
              onClick={handleImportRoster}
              disabled={loading || fetchingRoster || !channelUid.trim() || !yostarToken.trim()}
            >
              {loading || fetchingRoster ? 'Importing…' : 'Import Roster'}
            </button>
          </div>
          {(error || fetchError) && <div style={{ color: '#ff6b6b', marginTop: 8 }}>{error || fetchError}</div>}
        </>
      )}
    </div>
  );
}
