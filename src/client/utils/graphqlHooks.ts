import { useState } from 'react';
import { graphqlClient, SEND_AUTH_CODE_MUTATION, GET_AUTH_TOKEN_MUTATION, GET_MY_ROSTER_QUERY, GET_MY_STATUS_QUERY } from './graphqlClient';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type AnyRecord = Record<string, any>;

export interface AuthTokenData {
  success: boolean;
  channelUid?: string;
  yostarToken?: string;
  server?: string;
  error?: string;
}

export interface AuthCodeData {
  success: boolean;
  message: string;
}

export interface Operator {
  id: string;
  charId: string;
  level: number;
  elite: number;
  potential: number;
  skillLevel: number;
  trust: number;
  skin?: string;
  defaultSkillIndex?: number;
  gainTime?: number;
  skills?: Array<{
    unlock: number;
    level: number;
    state?: number;
    specializeLevel?: number;
    completeUpgradeTime?: number;
  }>;
  currentEquip?: string;
}

export interface UserStatus {
  displayName: string;
  nickName: string;
  nickNumber: string;
  level: number;
  exp: number;
  socialPoint: number;
  uid: string;
}

export function useSendAuthCode() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendCode = async (email: string, server: string = 'en') => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphqlClient.mutate({
        mutation: SEND_AUTH_CODE_MUTATION,
        variables: { email, server },
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data = (result.data as any)?.sendAuthCode;
      if (!data?.success) {
        throw new Error(data?.message || 'Failed to send auth code');
      }
      return data;
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const errorMsg = (e as any)?.message || String(e);
      setError(errorMsg);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { sendCode, loading, error };
}

export function useGetAuthToken() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getToken = async (email: string, code: string, server: string = 'en'): Promise<AuthTokenData> => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphqlClient.mutate({
        mutation: GET_AUTH_TOKEN_MUTATION,
        variables: { email, code, server },
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data = (result.data as any)?.getAuthToken;
      if (!data?.success) {
        throw new Error(data?.error || 'Failed to get auth token');
      }
      return data;
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const errorMsg = (e as any)?.message || String(e);
      setError(errorMsg);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { getToken, loading, error };
}

export function useGetMyRoster() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getRoster = async (
    channelUid: string,
    yostarToken: string,
    server: string = 'en'
  ): Promise<Operator[]> => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphqlClient.query({
        query: GET_MY_ROSTER_QUERY,
        variables: { channelUid, yostarToken, server },
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (result.data as any)?.myRoster || [];
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const errorMsg = (e as any)?.message || String(e);
      setError(errorMsg);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { getRoster, loading, error };
}

export function useGetMyStatus() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getStatus = async (
    channelUid: string,
    yostarToken: string,
    server: string = 'en'
  ): Promise<UserStatus | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphqlClient.query({
        query: GET_MY_STATUS_QUERY,
        variables: { channelUid, yostarToken, server },
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (result.data as any)?.myStatus || null;
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const errorMsg = (e as any)?.message || String(e);
      setError(errorMsg);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { getStatus, loading, error };
}
