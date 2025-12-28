// Helper to access Vite environment variables that works in tests
export function getBaseUrl(): string {
  // Check if we're in a test environment
  if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test') {
    // In Jest tests, use globalThis.import.meta.env
    return ((globalThis as any).import?.meta?.env?.BASE_URL as string) || '/';
  }

  // In production/dev with Vite
  // @ts-expect-error - import.meta.env is a Vite feature
  return import.meta.env.BASE_URL || '/';
}
