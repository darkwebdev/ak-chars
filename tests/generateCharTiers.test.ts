import { generateCharTiers } from '../src/server/extractor';
import fs from 'fs';

describe('generateCharTiers', () => {
  const originalFetch = (global as any).fetch;

  beforeEach(() => {
    jest.restoreAllMocks();
  });

  afterAll(() => {
    (global as any).fetch = originalFetch;
  });

  it('fetches gviz sheet, builds map and writes to data/charTiers.json', async () => {
    // Build a fake gviz response wrapping a table with rows that follow the paired layout
    const tableObj = {
      table: {
        cols: [{ label: 'Tier' }, { label: 'Col1' }],
        rows: [
          // header row (not used)
          { c: [{ v: 'Header1' }, { v: 'Header2' }] },
          // tier row: first column is tier label
          { c: [{ v: 'S' }, { v: null }] },
          // data row: character names in subsequent columns
          { c: [{ v: null }, { v: 'TestChar' }] },
        ],
      },
    };

    const gvizText = `/*OK*/google.visualization.Query.setResponse(${JSON.stringify(tableObj)});`;

    (global as any).fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => gvizText });

    const writeSpy = jest.spyOn(fs, 'writeFileSync').mockImplementation(() => undefined as any);

    const outPath = await generateCharTiers('dummy-sheet-id');

    expect(writeSpy).toHaveBeenCalled();
    // inspect the content written
    const [[calledPath, calledContent]] = writeSpy.mock.calls as unknown as [string, string][];
    expect(
      calledPath.endsWith('data/charTiers.json') || calledPath.endsWith('data\\charTiers.json'),
    ).toBeTruthy();
    const parsed = JSON.parse(calledContent as unknown as string);
    expect(parsed).toEqual({ TestChar: 'S' });
    // outPath should be the same path
    expect(outPath).toContain('charTiers.json');
  });
});
