import fs from 'fs';
import os from 'os';
import path from 'path';
import { fetchAvatars } from '../src/server/fetchAvatars';
import { jest } from '@jest/globals';

function makePngBuffer() {
  // Minimal valid PNG header + IHDR chunk to avoid pngjs parsing in tests if read directly.
  return Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
}

describe('fetchAvatars server', () => {
  const tmpRoot = path.join(os.tmpdir(), `ak-chars-fetchavatars-${Date.now()}`);
  beforeEach(() => {
    if (!fs.existsSync(tmpRoot)) fs.mkdirSync(tmpRoot, { recursive: true });
  });
  afterEach(() => {
    try {
      if (fs.existsSync(tmpRoot)) fs.rmSync(tmpRoot, { recursive: true, force: true });
    } catch (e) {
      // ignore
    }
  });

  it('downloads a few avatars respecting limit', async () => {
    const chars = [{ id: 'one' }, { id: 'two' }, { id: 'three' }, { id: 'four' }];

    const originalFetch = (global as any).fetch;
    (global as any).fetch = (jest.fn() as any).mockImplementation(async () => ({
      ok: true,
      arrayBuffer: async () => makePngBuffer(),
    }));

    await fetchAvatars({
      chars,
      outDir: path.join(tmpRoot, 'avatars'),
      limit: 2,
    });

    const files = fs.readdirSync(path.join(tmpRoot, 'avatars'));
    expect(files.length).toBeGreaterThanOrEqual(2);
    expect(files.some((f) => f.endsWith('.png'))).toBe(true);

    (global as any).fetch = originalFetch;
  });
});
