import { ApolloClient, InMemoryCache, HttpLink, gql } from '@apollo/client';

interface ImportMeta {
  env: {
    VITE_API_BASE?: string;
  };
}

const API_BASE = ((import.meta as unknown) as ImportMeta).env?.VITE_API_BASE || 'http://localhost:8000';

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
