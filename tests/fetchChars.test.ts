import { transformCharacterTable } from '../src/server/charUtils';

describe('transformCharacterTable', () => {
  it('extracts selected fields from character table object', () => {
    const input = {
      char_1: {
        name: 'A',
        rarity: 'TIER_1',
        profession: 'MEDIC',
        subProfessionId: 'phys',
        isNotObtainable: false,
      },
      char_2: {
        name: 'B',
        rarity: 'TIER_5',
        profession: 'SNIPER',
        subProfessionId: 'snip',
        isNotObtainable: false,
      },
      non_char: {
        appellation: 'A',
        rarity: 'TIER_1',
        profession: 'MEDIC',
        subProfessionId: 'phys',
      },
      char_not4sale: {
        name: 'C',
        rarity: null,
        profession: 42,
        subProfessionId: undefined,
        isNotObtainable: true,
      },
    };

    const out = transformCharacterTable(input as any);
    expect(out).toEqual([
      {
        id: 'char_1',
        name: 'A',
        rarity: 'TIER_1',
        profession: 'MEDIC',
        subProfessionId: 'phys',
      },
      {
        id: 'char_2',
        name: 'B',
        rarity: 'TIER_5',
        profession: 'SNIPER',
        subProfessionId: 'snip',
      },
    ]);
  });
});
