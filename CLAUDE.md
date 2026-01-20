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
yarn test:smoke        # Python smoke tests for production API
```

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

## Python Backend

The project includes a Python FastAPI backend in the `server/` directory.

### Python Setup
```bash
# Create virtual environment (from repo root)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r server/requirements.txt

# Run server
python -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
```

### Python Tests
```bash
# Activate venv first
source .venv/bin/activate

# Run all tests
pytest server/tests/ -v

# Run specific test file
pytest server/tests/test_sanitization.py -v

# Run integration tests
pytest tests/integration/ -v -m integration
```

## Important Notes

1. **Always use yarn**, never npm
2. **Source nvm** before running yarn commands if using nvm
3. **Enable corepack** to ensure yarn is available: `corepack enable`
4. **Python backend** requires separate virtual environment setup
5. **Integration tests** require environment variables (see `tests/integration/README.md`)

## Project Structure

```
ak-chars/
├── src/                    # Frontend React/TypeScript code
│   ├── client/            # Client-side components
│   └── types/             # TypeScript types
├── server/                # Python FastAPI backend
│   ├── tests/            # Python unit tests
│   └── main.py           # FastAPI app entry point
├── tests/integration/     # Integration tests
├── data/                  # Static game data (chars, tiers, etc.)
├── scripts/               # Build and data fetch scripts
└── .claude/               # Claude Code configuration
    ├── hooks/            # Git hooks
    └── skills/           # Custom skills
```

## Environment Variables

### Frontend
No environment variables required for basic development.

### Backend
Create `server/.env` for local development:
```bash
USE_FIXTURES=true          # Use fixture data (default)
ARKPRTS_API_KEY=           # Optional: Real API key for production
CORS_ORIGIN=               # Optional: Production frontend URL
```

### Integration Tests
See `tests/integration/README.md` for required environment variables.

## Getting Help

- Check package.json `scripts` section for all available commands
- Check `server/README.md` for backend-specific documentation
- Check `.claude/skills/test/SKILL.md` for test skill documentation
