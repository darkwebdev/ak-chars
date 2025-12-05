import React, { useState } from 'react';
import { useSendAuthCode, useGetAuthToken, useGetMyRoster, useGetMyStatus } from '../utils/graphqlHooks';

export function AuthPage() {
  const [email, setEmail] = useState('');
  const [requested, setRequested] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const [code, setCode] = useState('');
  const [channelUid, setChannelUid] = useState<string | null>(localStorage.getItem('ak_channel_uid'));
  const [yostarToken, setYostarToken] = useState<string | null>(localStorage.getItem('ak_yostar_token'));

  const { sendCode, loading: sendingCode, error: sendError } = useSendAuthCode();
  const { getToken, loading: verifying, error: verifyError } = useGetAuthToken();
  const { getRoster, loading: fetchingRoster, error: rosterError } = useGetMyRoster();
  const { getStatus, loading: fetchingStatus, error: statusError } = useGetMyStatus();

  const [fetchedRoster, setFetchedRoster] = useState<object[] | null>(null);
  const [fetchedStatus, setFetchedStatus] = useState<object | null>(null);

  const handleRequestCode = async () => {
    setMessage(null);
    try {
      await sendCode(email, 'en');
      setRequested(true);
      setMessage('Code sent — check your email (or server logs in dev).');
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setMessage(`Error: ${(e as any)?.message || String(e)}`);
    }
  };

  const handleVerifyCode = async () => {
    setMessage(null);
    try {
      const result = await getToken(email, code, 'en');
      if (result.success && result.channelUid && result.yostarToken) {
        localStorage.setItem('ak_channel_uid', result.channelUid);
        localStorage.setItem('ak_yostar_token', result.yostarToken);
        setChannelUid(result.channelUid);
        setYostarToken(result.yostarToken);
        setMessage('Verified — credentials saved.');
      }
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setMessage(`Error: ${(e as any)?.message || String(e)}`);
    }
  };

  const handleFetchRoster = async () => {
    if (!channelUid || !yostarToken) {
      setMessage('Missing credentials');
      return;
    }
    try {
      const roster = await getRoster(channelUid, yostarToken, 'en');
      setFetchedRoster(roster);
      setMessage(`Loaded ${roster.length} operators`);
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setMessage(`Error fetching roster: ${(e as any)?.message || String(e)}`);
    }
  };

  const handleFetchStatus = async () => {
    if (!channelUid || !yostarToken) {
      setMessage('Missing credentials');
      return;
    }
    try {
      const status = await getStatus(channelUid, yostarToken, 'en');
      setFetchedStatus(status);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setMessage(`User: ${(status as any)?.displayName}`);
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setMessage(`Error fetching status: ${(e as any)?.message || String(e)}`);
    }
  };

  return (
    <div style={{ padding: 24, color: '#e6eef6', background: '#071017', minHeight: '100vh' }}>
      <div style={{ maxWidth: 640, margin: '0 auto' }}>
        <h2>Sign in with GraphQL</h2>
        <p>Enter your email to receive a 6-digit sign-in code.</p>

        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: 8, flex: 1 }}
            disabled={sendingCode || requested}
          />
          <button onClick={handleRequestCode} disabled={sendingCode || !email}>
            {sendingCode ? 'Sending…' : requested ? 'Sent' : 'Send code'}
          </button>
        </div>

        {requested && (
          <div style={{ marginTop: 8 }}>
            <p>Enter the 6-digit code you received</p>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="123456"
                style={{ padding: 8 }}
              />
              <button onClick={handleVerifyCode} disabled={verifying || !code}>
                {verifying ? 'Verifying…' : 'Verify'}
              </button>
            </div>
          </div>
        )}

        {message && <div style={{ marginTop: 12, color: '#9fb0c8' }}>{message}</div>}
        {(sendError || verifyError) && <div style={{ marginTop: 12, color: '#ff6b6b' }}>Error: {sendError || verifyError}</div>}

        {channelUid && yostarToken && (
          <div style={{ marginTop: 18, padding: 12, background: '#041318', borderRadius: 6 }}>
            <h3>Authenticated</h3>
            <div style={{ fontSize: 12, color: '#cfe7ff' }}>
              Channel UID: {channelUid}
              <br />
              Yostar Token: {yostarToken?.substring(0, 20)}...
            </div>

            <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
              <button onClick={handleFetchStatus} disabled={fetchingStatus}>
                {fetchingStatus ? 'Fetching…' : 'Fetch Status'}
              </button>
              <button onClick={handleFetchRoster} disabled={fetchingRoster}>
                {fetchingRoster ? 'Fetching…' : 'Fetch Roster'}
              </button>
            </div>

            {statusError && <div style={{ color: 'salmon', marginTop: 8 }}>Status Error: {statusError}</div>}
            {fetchedStatus && (
              <div style={{ marginTop: 8 }}>
                <h4>User Status</h4>
                <pre style={{ color: '#9fb0c8', fontSize: 12 }}>{JSON.stringify(fetchedStatus, null, 2)}</pre>
              </div>
            )}

            {rosterError && <div style={{ color: 'salmon', marginTop: 8 }}>Roster Error: {rosterError}</div>}
            {fetchedRoster && (
              <div style={{ marginTop: 8 }}>
                <h4>Roster ({fetchedRoster.length} operators)</h4>
                <pre style={{ color: '#9fb0c8', fontSize: 11, maxHeight: 300, overflow: 'auto' }}>
                  {JSON.stringify(fetchedRoster.slice(0, 5), null, 2)}
                  {fetchedRoster.length > 5 && '\n... and ' + (fetchedRoster.length - 5) + ' more'}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AuthPage;
