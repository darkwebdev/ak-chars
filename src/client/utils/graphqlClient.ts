import { ApolloClient, InMemoryCache, HttpLink, gql } from '@apollo/client';

function getApiBase(): string {
  if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test') {
    return 'http://localhost:8000';
  }
  // @ts-expect-error - import.meta.env is a Vite feature
  return import.meta.env?.VITE_API_BASE || 'http://localhost:8000';
}

const API_BASE = getApiBase();

export const graphqlClient = new ApolloClient({
  link: new HttpLink({
    uri: `${API_BASE}/graphql`,
    credentials: 'include',
  }),
  cache: new InMemoryCache(),
});

export const SEND_AUTH_CODE_MUTATION = gql`
  mutation SendAuthCode($email: String!, $server: String!) {
    sendAuthCode(email: $email, server: $server) {
      success
      message
    }
  }
`;

export const GET_AUTH_TOKEN_MUTATION = gql`
  mutation GetAuthToken($email: String!, $code: String!, $server: String!) {
    getAuthToken(email: $email, code: $code, server: $server) {
      success
      channelUid
      yostarToken
      server
      error
    }
  }
`;

export const GET_MY_ROSTER_QUERY = gql`
  query GetMyRoster($channelUid: String!, $yostarToken: String!, $server: String!) {
    myRoster(channelUid: $channelUid, yostarToken: $yostarToken, server: $server) {
      id
      charId
      level
      elite
      potential
      skillLevel
      trust
      skin
      defaultSkillIndex
      gainTime
      skills {
        unlock
        level
        state
        specializeLevel
        completeUpgradeTime
      }
      currentEquip
    }
  }
`;

export const GET_MY_STATUS_QUERY = gql`
  query GetMyStatus($channelUid: String!, $yostarToken: String!, $server: String!) {
    myStatus(channelUid: $channelUid, yostarToken: $yostarToken, server: $server) {
      displayName
      nickName
      nickNumber
      level
      exp
      socialPoint
      uid
    }
  }
`;
