import { fetchChars } from '../src/server/fetchChars';
import { jest } from '@jest/globals';

describe('fetchChars CN merge', () => {
  it('appends CN-only chars with name set from CN', async () => {
    const enSample = {
      char_1: {
        name: 'english name',
        rarity: 'TIER_1',
        profession: 'MEDIC',
        subProfessionId: 'phys',
      },
    };

    // CN has char_2 which EN does not
    const cnSample = {
      char_1: {
        name: 'english name',
        rarity: 'TIER_1',
        profession: 'MEDIC',
        subProfessionId: 'phys',
      },
      char_2: {
        name: 'chinese name',
        rarity: 'TIER_3',
        profession: 'SNIPER',
        subProfessionId: 'snip',
        appellation: 'cn only english name',
      },
    };

    const originalFetch = (global as any).fetch;
    // mock fetch: first call EN, second call CN
    let call = 0;
    (global as any).fetch = (jest.fn() as any).mockImplementation(() => {
      call += 1;
      if (call === 1) return Promise.resolve({ ok: true, json: async () => enSample });
      return Promise.resolve({ ok: true, json: async () => cnSample });
    });

    const chars = await fetchChars();

    // EN char present
    expect(chars.find((c) => c.id === 'char_1')).toHaveProperty('name', 'english name');
    // CN-only appended
    expect(chars.find((c) => c.id === 'char_2')).toHaveProperty('name', 'cn only english name');

    (global as any).fetch = originalFetch;
  });
});
