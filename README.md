# ak-chars

Arknights characters management system.

# Quick start

```bash
# install dependencies
yarn

# run tests
yarn test

# run
yarn dev
```

We use Yarn for this project. Please run `yarn` / `yarn <script>` instead of `npm`.

## Deployment (GitHub Pages)

This repository is configured to automatically build and publish the site to GitHub Pages on every push to `main` using the workflow file at `.github/workflows/gh-pages.yml`.

- Build command: `yarn build` (Vite).
- Publish directory: `dist` (configured in `vite.config.ts`).
- Pages branch: `gh-pages` (the workflow writes to this branch).

The workflow uses the repository's built-in `GITHUB_TOKEN` so no additional secrets are required for basic publishing. If you'd prefer to use a personal access token (for example to publish from forks or to have a stable token), create a secret (for example `GH_PAGES_TOKEN`) in the repository and update the workflow to use it instead of `GITHUB_TOKEN`.

To verify locally:

```bash
# build locally
yarn build

# preview production build
yarn preview
```
