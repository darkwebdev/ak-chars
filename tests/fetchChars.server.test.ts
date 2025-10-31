import fs from 'fs';
import os from 'os';
import path from 'path';
import { fetchChars } from '../src/server/fetchChars';
import { jest } from '@jest/globals';

describe('fetchChars server', () => {
  const tmpRoot = path.join(os.tmpdir(), `ak-chars-fetchchars-${Date.now()}`);
  beforeEach(() => {
    if (!fs.existsSync(tmpRoot)) fs.mkdirSync(tmpRoot, { recursive: true });
  });
  afterEach(() => {
    try {
      if (fs.existsSync(tmpRoot)) fs.rmSync(tmpRoot, { recursive: true, force: true });
    } catch (e) {
      // ignore cleanup errors
    }
  });

  it('fetches char table and writes chars.json including id', async () => {
    const sample = {
      char_1: {
        name: 'Foo',
        rarity: 'TIER_1',
        profession: 'MEDIC',
        subProfessionId: 'phys',
      },
      char_2: {
        name: 'Bar',
        rarity: 'TIER_3',
        profession: 'SNIPER',
        subProfessionId: 'snip',
      },
    };

  const originalFetch = (global as any).fetch;
  (global as any).fetch = (jest.fn() as any).mockResolvedValue({ ok: true, json: async () => sample });

  const chars = await fetchChars();
  const outPath = path.join(tmpRoot, 'chars.json');
  fs.writeFileSync(outPath, JSON.stringify(chars, null, 2), 'utf8');
  const written = JSON.parse(fs.readFileSync(outPath, 'utf8')) as any[];
    expect(Array.isArray(written)).toBe(true);
    expect(written.some((c) => c.id === 'char_1')).toBe(true);
    expect(written.some((c) => c.id === 'char_2')).toBe(true);

    (global as any).fetch = originalFetch;
  });
});
