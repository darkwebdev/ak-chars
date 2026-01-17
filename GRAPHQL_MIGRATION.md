# GraphQL Integration Summary

## Overview
Successfully migrated the frontend authentication and roster fetching from REST API to GraphQL. The "import Krooster" feature has been replaced with direct GraphQL-based authentication and roster fetching from the Arknights game API.

## Changes Made

### 1. Dependencies Added
- `@apollo/client@4.0.9` - Apollo Client for GraphQL
- `graphql@16.12.0` - GraphQL core library

### 2. New Files Created

#### `src/client/utils/graphqlClient.ts`
- Apollo Client configuration
- GraphQL queries and mutations:
  - `SEND_AUTH_CODE_MUTATION` - Send authentication code to email
  - `GET_AUTH_TOKEN_MUTATION` - Verify code and get auth token
  - `GET_MY_ROSTER_QUERY` - Fetch user's operator roster
  - `GET_MY_STATUS_QUERY` - Fetch user account status

#### `src/client/utils/graphqlHooks.ts`
- Custom React hooks for GraphQL operations:
  - `useSendAuthCode()` - Hook for sending auth codes
  - `useGetAuthToken()` - Hook for verifying codes and getting tokens
  - `useGetMyRoster()` - Hook for fetching roster with auth
  - `useGetMyStatus()` - Hook for fetching user status

#### `src/client/components/GraphQLRosterButton.tsx`
- New component replacing KroosterButton
- Provides direct Arknights account authentication
- Imports roster directly from GraphQL server
- Stores credentials (Channel UID, Yostar Token) in localStorage

### 3. Modified Files

#### `src/client/components/AuthPage.tsx`
- Complete rewrite using GraphQL
- Replaced REST API calls with GraphQL mutations and queries
- Stores Channel UID and Yostar Token in localStorage
- Integrated roster and status fetching directly in auth page

#### `src/client/App.tsx`
- Replaced `KroosterButton` import with `GraphQLRosterButton`
- Removed Krooster normalization logic
- Simplified roster import to use GraphQL data directly

### 4. Files Created (Can be Cleaned Up)

#### `src/client/components/AuthPageGraphQL.tsx`
- Backup/alternative version of AuthPage (same as the updated AuthPage.tsx)
- Can be deleted as it's now redundant

## How It Works

### Authentication Flow
1. User enters email on auth page
2. GraphQL mutation sends code to email (uses game auth service)
3. User receives code and enters it
4. `getAuthToken` mutation verifies code and returns:
   - `channelUid` - User's Arknights channel ID
   - `yostarToken` - Authentication token
5. Credentials are stored in localStorage

### Roster Import Flow
1. User provides stored credentials (Channel UID + Yostar Token)
2. `GraphQLRosterButton` accepts manual credential input
3. GraphQL query fetches roster using credentials
4. Roster charIds are matched with local character data
5. Matched IDs are saved to `ownedChars` localStorage

## GraphQL Server Integration

The frontend now connects to `http://localhost:8000/graphql` (configurable via `VITE_API_BASE`).

The GraphQL server provides:
- `sendAuthCode(email, server)` mutation
- `getAuthToken(email, code, server)` mutation
- `myRoster(channelUid, yostarToken, server)` query
- `myStatus(channelUid, yostarToken, server)` query

## Migration Notes

### Removed
- Krooster HTML parsing functionality (not removed, but no longer used)
- KroosterButton component (not removed, but no longer imported)
- REST API calls to `/auth/request-code`, `/auth/verify`, `/fetch-chars`

### New Behavior
- Authentication now uses GraphQL mutations instead of REST endpoints
- Roster import uses GraphQL queries instead of REST endpoints
- No more need for pasting Krooster page HTML
- Direct authentication with Arknights game credentials via GraphQL

## Environment Configuration

Configure GraphQL endpoint via environment variable:
```
VITE_API_BASE=http://localhost:8000
```

Default: `http://localhost:8000/graphql`

## TypeScript Compliance

All files are fully typed and pass linting requirements:
- No implicit `any` types
- Proper error handling with type guards
- Full GraphQL type support via gql definitions
