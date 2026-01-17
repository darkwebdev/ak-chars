# ak-chars — server

This small FastAPI server provides endpoints to get Arknights player data and operator rosters by authenticating with the game API.

## 🔒 Security

This server handles sensitive authentication credentials. Review [SECURITY.md](./SECURITY.md) for:

- Security best practices
- How credentials are protected
- Safe development guidelines

**Key points:**

- All logs automatically sanitize sensitive data (tokens, passwords, etc.)
- Never commit `.env` files or credentials
- Use environment variables for all secrets
- Consider installing pre-commit hooks (see `.pre-commit-config.yaml` in repo root)

## Environment

Set these environment variables as needed (create a `.env` file in the `server/`
directory for local development — this project loads `server/.env` using
python-dotenv):

- `ARKPRTS_API_KEY` — (optional) API key for the `arkprts` client. If unset the
  server returns stubbed data for development.

**Important:** Copy `.env.example` to `.env` and fill in your values. Never commit `.env`.

## Developer notes

- If you have an `arkprts` package installed and a mismatched client API the
  wrapper may raise errors; leaving `ARKPRTS_API_KEY` unset forces the stubbed
  response which is safe for local testing.

## Run locally (recommended)

Use the included virtualenv pattern to isolate dependencies. From the repository
root run:

```bash
# create venv (only if you don't already have .venv)
python3 -m venv .venv

# activate (zsh / bash)
. .venv/bin/activate

# install requirements
python -m pip install --upgrade pip
python -m pip install -r server/requirements.txt
# start uvicorn (background)
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload > server/server.log 2>&1 & echo $! > server/server.pid

# view logs
tail -f server/server.log

# run tests
python -m pytest server/tests/ -v
```

## GraphQL API

The server provides a GraphQL endpoint at `/graphql` for flexible operator data queries. This allows you to request exactly the fields you need.

**Access GraphQL Playground:**
Open http://127.0.0.1:8000/graphql in your browser for an interactive query interface.

**Example Queries:**

```graphql
# Get all operators with selected fields
{
  operators {
    charId
    level
    elite
    potential
    trust
  }
}

# Filter operators by level and elite
{
  operators(minLevel: 70, minElite: 2) {
    charId
    level
    elite
    skillLevel
  }
}

# Get specific operators by ID
{
  operators(ids: ["char_002_amiya", "char_151_myrtle"]) {
    charId
    level
    potential
    trust
  }
}

# Get single operator
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

# Get user status
{
  userStatus {
    displayName
    level
    uid
  }
}
```

**Available Fields:**

- `charId` - Character ID (e.g., "char_002_amiya")
- `level` - Operator level (1-90)
- `elite` / `evolvePhase` - Elite level (0, 1, 2)
- `potential` / `potentialRank` - Potential level (0-5)
- `skillLevel` / `mainSkillLvl` - Main skill level
- `trust` / `favorPoint` - Trust points
- `skin` - Current skin ID
- `currentEquip` - Current equipment/module

**Available Filters:**

- `ids: [String]` - Filter by specific char IDs
- `minLevel: Int` - Minimum operator level
- `maxLevel: Int` - Maximum operator level
- `minElite: Int` - Minimum elite level
- `maxElite: Int` - Maximum elite level
- `minPotential: Int` - Minimum potential rank

## Development Mode

By default, the server uses fixture data from `server/tests/user_data_response.json` for development and testing. This allows you to test the API without real game credentials.

Set `USE_FIXTURES=true` in your `.env` file (default behavior) to use fixture data.
Set `USE_FIXTURES=false` to use live game API calls (requires real credentials).

**Test the REST endpoints with fixture data:**

```bash
# Get operator roster (returns user.troop.chars only)
curl -X POST http://127.0.0.1:8000/my/roster \
  -H "Content-Type: application/json" \
  -d '{"channel_uid":"any","yostar_token":"any"}' | jq '.chars | keys | length'

# Get user status (returns user.status only)
curl -X POST http://127.0.0.1:8000/my/status \
  -H "Content-Type: application/json" \
  -d '{"channel_uid":"any","yostar_token":"any"}' | jq '.status | {nickName, level, uid}'
```

**Test the GraphQL endpoint:**

```bash
# Query high-level operators
curl -X POST http://127.0.0.1:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ operators(minLevel: 80) { charId level elite } }"}'
```

## Production: Get your operator roster

The `/my/roster` endpoint returns your operator roster (user.troop.chars) by authenticating directly with the game API.

**Requirements:**

- Set `USE_FIXTURES=false` in your `.env` file
- Your game credentials (see below for how to get them)

### Easy method: Get game credentials via API

Use these endpoints to get your game credentials without manual network inspection:

```bash
# 1. Request a game authentication code (sent to your game account email)
curl -X POST http://127.0.0.1:8000/auth/game-code \
  -H "Content-Type: application/json" \
  -d '{"email":"your-game-email@example.com","server":"en"}'

# 2. Check your email for the code, then exchange it for credentials
curl -X POST http://127.0.0.1:8000/auth/game-token \
  -H "Content-Type: application/json" \
  -d '{"email":"your-game-email@example.com","code":"123456","server":"en"}' | jq

# Response contains your credentials:
# {
#   "ok": true,
#   "channel_uid": "your-channel-uid",
#   "yostar_token": "your-token",
#   "server": "en"
# }
```

### Get your roster

Once you have your game credentials:

```bash
curl -X POST http://127.0.0.1:8000/my/roster \
  -H "Content-Type: application/json" \
  -d '{
    "channel_uid": "your-channel-uid",
    "yostar_token": "your-yostar-token",
    "server": "en"
  }' | jq
```

The response contains your full game data including:

- Complete operator roster (all 100+ operators you own) in `data.user.troop.chars`
- Operator levels, elite phases, skills, potential, trust, modules
- Inventory, materials, currency in `data.user.inventory`
- Base/infrastructure data in `data.user.building`
- Mission progress and achievements

**Note on data structure:** The roster is in `data.user.troop.chars` as an object where keys are operator instance IDs. Each operator includes:

- `charId` — operator ID (e.g., "char_002_amiya")
- `level`, `evolvePhase` — level and elite promotion
- `potentialRank` — potential level (0-5)
- `mainSkillLvl` — skill mastery level
- `skills` — array of skill details with specialization levels
- `favorPoint` — trust value
- `equip` — module/equipment data
- `tmpl` — template data for multi-form operators

**Security note:** Your game credentials grant full access to your account. Keep them secure and never share them. The server does not store these credentials.

## Complete workflow example

Here's the complete flow to get your operator roster:

```bash
# Step 1: Request game authentication code
curl -X POST http://127.0.0.1:8000/auth/game-code \
  -H "Content-Type: application/json" \
  -d '{"email":"your-game-email@example.com","server":"en"}'

# Step 2: Check your email for the 6-digit code

# Step 3: Exchange code for game credentials
curl -X POST http://127.0.0.1:8000/auth/game-token \
  -H "Content-Type: application/json" \
  -d '{"email":"your-game-email@example.com","code":"123456","server":"en"}' | jq

# Step 4: Use the credentials to get your roster
curl -X POST http://127.0.0.1:8000/my/roster \
  -H "Content-Type: application/json" \
  -d '{
    "channel_uid": "<channel_uid-from-step-3>",
    "yostar_token": "<yostar_token-from-step-3>",
    "server": "en"
  }' | jq '.data.user.troop.chars | keys | length'

# This will show the count of operators you own
```

## Extra endpoints

Two developer-friendly endpoints were added to `server/players.py`:

- GET /characters/{player_id} — return a compact player summary for a single
  player id. Useful when you already have a player id and want name/level.
- GET /avatars/{player_id} — attempt to proxy the player's avatar image from
  the arkprts client. Returns 404 if no avatar can be fetched.

Examples:

```bash
# fetch a single character summary
curl -sS http://127.0.0.1:8000/characters/48808515 | jq

# fetch a player's avatar (will return image bytes)
curl -v -o avatar.png http://127.0.0.1:8000/avatars/48808515
file avatar.png
```

Additional developer endpoints (bulk / search):

```bash
# expand multiple ids into compact player summaries
curl -sS -X POST http://127.0.0.1:8000/players/expand -H "Content-Type: application/json" -d '{"ids":["20173387","27120031"]}' | jq

# search players by nickname
curl -sS -X POST http://127.0.0.1:8000/players/search -H "Content-Type: application/json" -d '{"nickname":"alice","limit":10}' | jq
```

## Raw upstream payload endpoints

For full fidelity (avatars, full roster, per-operator stats and nested fields) the server exposes endpoints that return the raw upstream JSON returned by the game API via the arkprts client.

- GET /players/raw/{player_id} — returns the raw JSON payload for a single id.
- POST /players/raw — accepts JSON { ids: [..], server?: 'en' } and returns raw payloads for multiple ids.

Examples:

```bash
# single id
curl -sS http://127.0.0.1:8000/players/raw/20173387 | jq

# multiple ids
curl -sS -X POST http://127.0.0.1:8000/players/raw -H "Content-Type: application/json" -d '{"ids":["20173387","27120031"]}' | jq
```

## Security and performance notes

- The raw payloads can be large; prefer requesting only the ids you need rather than bulk dumping the entire player database.
- These endpoints are unauthenticated to make debugging easier in local dev; consider adding rate limiting or IP restrictions before exposing to any untrusted network.
- Avatar fields in the raw payload are usually asset ids (for example `avatar_special_35`). Resolving those to image bytes may require the arkprts client's `assets` helper; the `/avatars/{player_id}` endpoint attempts resolution but can still return 404 if the assets cannot be resolved.

## Player data available

**Public player data** (from `/players/raw`, `/characters`, etc.):

When `arkprts` is available the server returns compact player summaries from
`get_players` / `search_players`, and you can also call `get_raw_player_info`
to obtain the full raw payload returned by the game APIs. Fields commonly
available (may vary between `arkprts` versions and servers):

- `uid` / `id` — player id
- `nickName` / `nickname` — display name
- `nickNumber` — nick number suffix
- `level` — player level
- `serverName` — friendly server name
- `avatar` — object with `{ type, id }` (e.g. `{"type":"ICON","id":"avatar_special_35"}`)
- `avatarId` — alternate numeric/string id
- `secretarySkinSp`, `secretary`, `secretary_skin_id`
- `assistCharList` / `team_v2` — **support units only** (not full roster, just the ~12 characters shown as friend support)
- `friendNumLimit` — friends cap
- `last_online_time`, `register_ts`
- `recent_visited`, `info_share` — additional metadata

**Important:** The public player endpoints do NOT return the full operator roster. They only return support units (`assistCharList`). To get all 100+ operators a player owns, use the `/my/roster` endpoint with game credentials (see above).

**Authenticated user data** (from `/my/roster`):

When authenticated with game credentials, `get_data()` / `get_raw_data()` returns the complete game state including:

- Full operator roster (`data.user.troop.chars`) with all owned operators
- Detailed operator stats: level, elite phase, skills, potential, trust, modules
- Inventory, materials, currency (`data.user.inventory`)
- Base/infrastructure data (`data.user.building`)
- Mission progress, challenge records, achievements

If you need more than the compact summary the server-side ark client exposes
methods that can be used (and the server wrapper can be extended to surface
them):

- `get_players(ids, server=...)` — bulk player models (used for `/players/expand`).
- `get_partial_players(ids, server=...)` — lighter-weight partial player models.
- `search_players(nickname, server=..., limit=...)` — search by nickname.
- `get_raw_player_info([ids], server=...)` — raw JSON payloads from the upstream API (contains avatar ids, full roster and stats).
- `get_data()` / `get_raw_data()` — various cached/global asset or user data depending on client.

## Notes on avatars

- Avatars in the raw payload are often asset ids (for example `avatar_special_35`).
  The `arkprts` client may provide an `assets` helper to resolve those ids to
  real files or URLs (`assets.get_file`, `assets.get_item`, etc.). The server's
  `/avatars/{player_id}` endpoint attempts multiple resolution strategies but
  will return 404 if no usable image can be fetched.

## Developer tip

When debugging or extending the server it's useful to call the `get_raw_player_info`
method (or `/players/expand` which uses `get_players`) and inspect the returned
JSON to see which fields are present for your target server and arkprts version.
