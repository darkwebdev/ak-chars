import {
  extractJsonFromGviz,
  tableToMatrix,
  buildCharMapFromMatrix,
  fetchSheet,
} from '../src/server/extractor';
import { jest } from '@jest/globals';

describe('extractor', () => {
  it('builds char->tier map from alternating rows', () => {
    const table = {
      cols: [{ id: 'A' }, { id: 'B' }, { id: 'C' }],
      rows: [
        { c: [null, { v: 'Vanguards' }, { v: 'Guards' }] },
        { c: [{ v: 'EX' }, null, null] },
        { c: [null, { v: 'Ines' }, { v: 'Mountain' }] },
        { c: [{ v: 'S+' }, null, null] },
        { c: [null, { v: 'Ulpianus' }, { v: 'Qiubai' }] },
      ],
    };

    const { rows } = tableToMatrix(table as any);
    const map = buildCharMapFromMatrix(rows);
    expect(map['Ines']).toBe('EX');
    expect(map['Mountain']).toBe('EX');
    expect(map['Ulpianus']).toBe('S+');
  });

  test('extractJsonFromGviz parses wrapped response', () => {
    const obj = { hello: 'world' };
    const text = `/*comment*/google.visualization.Query.setResponse(${JSON.stringify(obj)});`;
    const parsed = extractJsonFromGviz(text);
    expect(parsed).toEqual(obj);
  });

  test('extractJsonFromGviz throws on invalid input', () => {
    expect(() => extractJsonFromGviz('no callback here')).toThrow(/Failed to parse gviz response/);
  });

  test('tableToMatrix uses cell.f when v is undefined and maps cols labels', () => {
    const table = {
      cols: [{ label: 'Tier' }, { id: 'C1' }],
      rows: [
        { c: [{ v: 'hdr1' }, { v: 'hdr2' }] },
        { c: [{ v: 'EX' }, { f: 'CharA' }] },
        { c: [{ v: null }, { v: 'CharB' }] },
      ],
    } as any;

    const res = tableToMatrix(table);
    expect(res.cols).toEqual(['Tier', 'C1']);
    expect(res.rows[1][1]).toBe('CharA');
  });

  test('fetchSheet calls fetch and returns table', async () => {
    const fakeTable = { cols: [], rows: [] };
    const wrapped = `google.visualization.Query.setResponse(${JSON.stringify({
      table: fakeTable,
    })});`;
    (global as any).fetch = (jest.fn() as any).mockResolvedValue({
      ok: true,
      text: async () => wrapped,
    });

    const table = await fetchSheet('sheet-id', 'SheetName');
    expect(table).toEqual(fakeTable);
  });
});
