# Project Instructions for Claude Code

## Package Manager

**IMPORTANT:** This project uses **Yarn v1.x**, NOT npm.

- ✅ Use `yarn` for all package management commands
- ❌ Never use `npm` commands
- The project has npm usage blocked via preinstall script

## Common Commands

### Installing Dependencies
```bash
yarn install
# or simply
yarn
```

### Running Tests
```bash
yarn test              # Jest unit/component tests
yarn test:e2e          # Playwright E2E tests
yarn test:e2e:ui       # Playwright E2E tests with UI
yarn test:e2e:headed   # Playwright E2E tests in headed mode
```

Backend API smoke/integration tests live in the darkwebdev/ak-account
repo now, not here.

### Development
```bash
yarn dev               # Start Vite dev server
yarn start-bg          # Start dev server in background
yarn stop-bg           # Stop background dev server
```

### Build
```bash
yarn build             # Production build
yarn preview           # Preview production build
```

### Code Quality
```bash
yarn lint              # Run ESLint
yarn format            # Format code with Prettier
yarn lint-staged       # Run lint-staged (pre-commit)
```

### Storybook
```bash
yarn storybook         # Start Storybook on port 6006
```

### Data Scripts
```bash
yarn extract-tiers     # Extract character tier data
yarn fetch-professions # Fetch profession data
yarn fetch-chars       # Fetch character data
yarn fetch-avatars     # Fetch character avatars
yarn optimize-avatars  # Optimize avatar images
```

## Development Setup

### Prerequisites
- Node.js (managed via nvm)
- Yarn v1.x (enabled via corepack)

### Setup Commands
```bash
# Enable corepack for yarn
source ~/.nvm/nvm.sh
corepack enable

# Install dependencies
yarn install

# Start development server
yarn dev
```

## Backend API

ak-chars is frontend-only - it has no backend of its own. It talks to
the Arknights/Yostar auth API hosted in the separate darkwebdev/ak-account
repo, over GraphQL (`src/client/utils/graphqlClient.ts`, `VITE_API_BASE`
env var, defaults to `http://localhost:8000`).

For local development, clone and run darkwebdev/ak-account locally on
port 8000 (see that repo's README) - this gives fixture-backed dev data
(`USE_FIXTURES=true`) without needing real Yostar credentials. The
production build points at the live Cloud Run deployment instead (set
via `VITE_API_BASE` in `.github/workflows/gh-pages.yml`).

All backend code, its unit tests, and the live-credential integration
test suite live in darkwebdev/ak-account now, not here.

## Important Notes

1. **Always use yarn**, never npm
2. **Source nvm** before running yarn commands if using nvm
3. **Enable corepack** to ensure yarn is available: `corepack enable`
4. **Backend API** lives in the separate darkwebdev/ak-account repo - run it locally for fixture-backed dev

## Project Structure

```
ak-chars/
├── src/                    # Frontend React/TypeScript code
│   ├── client/            # Client-side components
│   └── types/             # TypeScript types
├── data/                  # Static game data (chars, tiers, etc.)
├── scripts/               # Build and data fetch scripts
└── .claude/               # Claude Code configuration
    ├── hooks/            # Git hooks
    └── skills/           # Custom skills
```

## Environment Variables

No environment variables required for basic development. Set
`VITE_API_BASE` to point the frontend at a non-default backend (see
"Backend API" above).

## Getting Help

- Check package.json `scripts` section for all available commands
- Check `.claude/skills/test/SKILL.md` for test skill documentation
- Check darkwebdev/ak-account's README for backend API documentation
