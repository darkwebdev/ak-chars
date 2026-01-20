import React, { useState } from 'react';
import { useGetMyRoster, useSendAuthCode, useGetAuthToken } from '../utils/graphqlHooks';

type Props = {
  chars?: Array<{ id: string; name: string }>;
  onApply?: (charIds: string[]) => void;
};

export function GraphQLRosterButton({ chars = [], onApply }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // Email-based auth flow
  const [email, setEmail] = useState('');
  const [codeSent, setCodeSent] = useState(false);
  const [code, setCode] = useState('');
  const [channelUid, setChannelUid] = useState('');
  const [yostarToken, setYostarToken] = useState('');

  const { getRoster, loading: fetchingRoster, error: fetchError } = useGetMyRoster();
  const { sendCode, loading: sendingCode } = useSendAuthCode();
  const { getToken, loading: verifyingCode } = useGetAuthToken();

  const handleSendCode = async () => {
    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    setError(null);
    try {
      await sendCode(email.trim(), 'en');
      setCodeSent(true);
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError(String(err));
    }
  };

  const handleVerifyCode = async () => {
    if (!code.trim()) {
      setError('Code is required');
      return;
    }

    setError(null);
    try {
      const result = await getToken(email.trim(), code.trim(), 'en');
      if (result.success && result.channelUid && result.yostarToken) {
        setChannelUid(result.channelUid);
        setYostarToken(result.yostarToken);
      } else {
        setError(result.error || 'Failed to verify code');
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError(String(err));
    }
  };

  const handleImportRoster = async () => {
    if (!channelUid.trim() || !yostarToken.trim()) {
      setError('Please complete authentication first');
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
            {/* Email input and Send/Resend button */}
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                type="email"
                placeholder="your-email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ padding: 8, flex: 1 }}
                disabled={sendingCode || verifyingCode || channelUid !== ''}
              />
              <button
                onClick={handleSendCode}
                disabled={sendingCode || !email.trim() || channelUid !== ''}
                style={{ whiteSpace: 'nowrap' }}
              >
                {sendingCode ? 'Sending…' : codeSent ? 'Resend Code' : 'Send Code'}
              </button>
            </div>

            {/* Code input appears after code is sent */}
            {codeSent && !channelUid && (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  type="text"
                  placeholder="6-digit code"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  style={{ padding: 8, flex: 1 }}
                  maxLength={6}
                  disabled={verifyingCode}
                />
                <button
                  onClick={handleVerifyCode}
                  disabled={verifyingCode || !code.trim()}
                  style={{ whiteSpace: 'nowrap' }}
                >
                  {verifyingCode ? 'Verifying…' : 'Verify Code'}
                </button>
              </div>
            )}

            {/* Import button appears after authentication */}
            {channelUid && yostarToken && (
              <div style={{ padding: 8, background: '#041318', borderRadius: 4, fontSize: 12 }}>
                ✓ Authenticated
              </div>
            )}

            {channelUid && yostarToken && (
              <button
                onClick={handleImportRoster}
                disabled={loading || fetchingRoster}
              >
                {loading || fetchingRoster ? 'Importing…' : 'Import Roster'}
              </button>
            )}
          </div>
          {(error || fetchError) && <div style={{ color: '#ff6b6b', marginTop: 8 }}>{error || fetchError}</div>}
        </>
      )}
    </div>
  );
}
