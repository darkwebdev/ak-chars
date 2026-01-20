# GraphQL Examples

## Access GraphQL Playground

Open http://127.0.0.1:8000/graphql in your browser for an interactive GraphQL interface with autocomplete and documentation.

## Example Queries

### Basic Queries

#### Get all operators with basic info

```graphql
{
  operators {
    charId
    level
    elite
  }
}
```

#### Get specific operator

```graphql
{
  operator(charId: "char_002_amiya") {
    charId
    level
    elite
    potential
    skillLevel
    trust
  }
}
```

#### Get user status

```graphql
{
  userStatus {
    displayName
    level
    uid
  }
}
```

### Filtered Queries

#### Get high-level operators

```graphql
{
  operators(minLevel: 80) {
    charId
    level
    elite
  }
}
```

#### Get Elite 2 operators

```graphql
{
  operators(minElite: 2) {
    charId
    elite
    level
    potential
  }
}
```

#### Get operators in level range

```graphql
{
  operators(minLevel: 70, maxLevel: 90, minElite: 2) {
    charId
    level
    elite
    skillLevel
    trust
  }
}
```

#### Get specific operators by ID

```graphql
{
  operators(ids: ["char_002_amiya", "char_151_myrtle", "char_108_silent"]) {
    charId
    level
    elite
    potential
  }
}
```

### Advanced Queries with Aliases

```graphql
{
  elite2Ops: operators(minElite: 2) {
    charId
    level
  }

  highLevel: operators(minLevel: 80) {
    charId
    elite
  }

  amiya: operator(charId: "char_002_amiya") {
    charId
    trust
  }
}
```

### Custom Field Selection

Request only the fields you need:

```graphql
{
  operators {
    charId
    trust
  }
}
```

This returns operators with only `charId` and `trust` fields, reducing payload size.

## cURL Examples

### Query from command line

```bash
# Get all operators
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ operators { charId level elite } }"}'

# Get filtered operators
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ operators(minLevel: 80) { charId level elite potential } }"}'

# Get single operator
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ operator(charId: \"char_002_amiya\") { charId level trust } }"}'

# Get user status
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ userStatus { displayName level uid } }"}'
```

## JavaScript/TypeScript Example

```typescript
async function fetchOperators() {
  const query = `
    {
      operators(minLevel: 80, minElite: 2) {
        charId
        level
        elite
        potential
        trust
      }
    }
  `;

  const response = await fetch('http://127.0.0.1:8000/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  const { data } = await response.json();
  return data.operators;
}
```

## Python Example

```python
import requests

def fetch_operators(min_level=80):
    query = """
    {
      operators(minLevel: %d) {
        charId
        level
        elite
        potential
      }
    }
    """ % min_level

    response = requests.post(
        'http://127.0.0.1:8000/graphql',
        json={'query': query}
    )

    return response.json()['data']['operators']
```

## Benefits of GraphQL

1. **Request only what you need** - Reduce payload size by selecting specific fields
2. **Single request** - Get related data in one query instead of multiple REST calls
3. **Type-safe** - GraphQL schema provides strong typing and validation
4. **Self-documenting** - Schema acts as documentation (visible in playground)
5. **Flexible filtering** - Combine multiple filters in a single query

## Authentication

### Mutations

#### Send authentication code

```graphql
mutation {
  sendAuthCode(email: "your.email@example.com", server: "en") {
    success
    message
  }
}
```

#### Get authentication token

```graphql
mutation {
  getAuthToken(email: "your.email@example.com", code: "123456", server: "en") {
    success
    channelUid
    yostarToken
    server
    error
  }
}
```

### Authenticated Queries

#### Get my roster

```graphql
{
  myRoster(channelUid: "your-uid", yostarToken: "your-token") {
    charId
    level
    elite
    potential
    skillLevel
    trust
  }
}
```

#### Get my status

```graphql
{
  myStatus(channelUid: "your-uid", yostarToken: "your-token") {
    displayName
    level
    exp
    uid
  }
}
```

### Authentication Flow Example

```javascript
// 1. Send auth code
const sendCodeMutation = `
  mutation {
    sendAuthCode(email: "your.email@example.com") {
      success
      message
    }
  }
`;

let response = await fetch('http://127.0.0.1:8000/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: sendCodeMutation }),
});

// 2. Get token with code from email
const getTokenMutation = `
  mutation {
    getAuthToken(email: "your.email@example.com", code: "123456") {
      success
      channelUid
      yostarToken
      error
    }
  }
`;

response = await fetch('http://127.0.0.1:8000/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: getTokenMutation }),
});

const { data } = await response.json();
const { channelUid, yostarToken } = data.getAuthToken;

// 3. Query your roster
const rosterQuery = `
  {
    myRoster(channelUid: "${channelUid}", yostarToken: "${yostarToken}") {
      charId
      level
      elite
    }
  }
`;

response = await fetch('http://127.0.0.1:8000/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: rosterQuery }),
});

const roster = await response.json();
```

## Player Search and Expand

### Search players by nickname

```graphql
{
  searchPlayers(nickname: "TestDoctor", server: "en", limit: 10) {
    ok
    players {
      playerId
      nickName
      level
      avatar
    }
  }
}
```

### Expand player IDs to get details

```graphql
{
  expandPlayers(ids: ["12345", "67890"], server: "en") {
    ok
    players {
      playerId
      nickName
      level
      avatar
    }
  }
}
```

### Get single player

```graphql
{
  getPlayer(playerId: "12345", server: "en") {
    playerId
    nickName
    level
    avatar
    avatarUrl
  }
}
```

## Player Avatars and Raw Data

### Get player avatar URL

```graphql
{
  getPlayerAvatarUrl(playerId: "12345", server: "en")
}
```

This returns a URL string that can be used to fetch the avatar image via the REST endpoint.

### Get raw player data

```graphql
{
  getRawPlayerData(playerId: "12345", server: "en")
}
```

Returns the full raw upstream JSON payload as a string for debugging and accessing complete player data.

### Get raw data for multiple players

```graphql
{
  getRawPlayersData(ids: ["12345", "67890"], server: "en")
}
```

## REST vs GraphQL Endpoints

Complete parity between REST and GraphQL - every endpoint is available in both:

| REST Endpoint                  | GraphQL Equivalent                          | Type     |
| ------------------------------ | ------------------------------------------- | -------- |
| `GET /fixtures/operators`      | `query { operators { ... } }`               | Query    |
| `GET /fixtures/operator/{id}`  | `query { operator(charId: "...") { ... } }` | Query    |
| `GET /fixtures/user-status`    | `query { userStatus { ... } }`              | Query    |
| `POST /players/search`         | `query { searchPlayers(...) { ... } }`      | Query    |
| `POST /players/expand`         | `query { expandPlayers(...) { ... } }`      | Query    |
| `GET /characters/{id}`         | `query { getPlayer(...) { ... } }`          | Query    |
| `GET /avatars/{id}`            | `query { getPlayerAvatarUrl(...) }`         | Query    |
| `GET /players/raw/{id}`        | `query { getRawPlayerData(...) }`           | Query    |
| `POST /players/raw`            | `query { getRawPlayersData(...) }`          | Query    |
| `POST /auth/game-code`         | `mutation { sendAuthCode(...) { ... } }`    | Mutation |
| `POST /auth/game-token`        | `mutation { getAuthToken(...) { ... } }`    | Mutation |
| `POST /my/roster`              | `query { myRoster(...) { ... } }`           | Query    |
| `POST /my/status`              | `query { myStatus(...) { ... } }`           | Query    |

**Advantages of GraphQL:**

- Request exactly the fields you need
- Combine multiple queries in one request
- Type-safe with schema validation
- Better developer experience with GraphQL playground
