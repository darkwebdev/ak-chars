---
name: test
description: Run the test suite for the project. Use when the user asks to run tests, test the code, or check if tests pass.
allowed-tools: Bash, Read, TodoWrite, AskUserQuestion
---

# Test Skill

Run the project's test suite

## Instructions

When this skill is invoked:

1. Source nvm and enable corepack (required for yarn in this project)
2. Determine which test suite to run:
   - `yarn test` - Run Jest unit/component tests (default)
   - `yarn test:e2e` - Run Playwright end-to-end tests
   - If unclear which tests to run, ask the user
3. Run the appropriate test suite
4. Report the test results to the user
5. If tests fail, show relevant failure details

## Available Test Commands

- `yarn test` - Jest tests with experimental VM modules
- `yarn test:e2e` - Playwright E2E tests
- `yarn test:e2e:ui` - Playwright E2E tests with UI
- `yarn test:e2e:headed` - Playwright E2E tests in headed mode

## Example

User: "run tests"

You should:
1. Run `source ~/.nvm/nvm.sh && corepack enable && yarn test`
2. Show test results
3. Report pass/fail status

User: "run e2e tests"

You should:
1. Run `source ~/.nvm/nvm.sh && corepack enable && yarn test:e2e`
2. Show test results
3. Report pass/fail status

## Important

- Always source nvm before running yarn commands
- Enable corepack to ensure yarn is available
- Default to `yarn test` (Jest) unless user specifically asks for E2E tests
- Report test failures clearly with relevant error messages
- This project blocks npm usage - always use yarn
