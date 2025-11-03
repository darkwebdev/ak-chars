import { jest } from '@jest/globals';
import { fetchKroosterBrowser } from '../src/client/utils/krooster';

// Helper to convert name arrays to char objects for testing
function makeChars(names: string[]): Array<{ id: string; name: string }> {
  return names.map((name, i) => ({
    id: `char_${String(i).padStart(3, '0')}_test`,
    name,
  }));
}

describe('fetchKroosterMatching', () => {
  const realFetch = global.fetch;

  afterEach(() => {
    // restore original global.fetch
    // @ts-ignore
    global.fetch = realFetch;
    jest.resetAllMocks?.();
  });

  it('returns only names present in the page text', async () => {
    const html = '<html><body><div>Alice</div><div>Other</div></body></html>';
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const chars = [
      { id: 'char_001_alice', name: 'Alice' },
      { id: 'char_002_bob', name: 'Bob' },
    ];
    const out = await fetchKroosterBrowser('user', chars);
    expect(out).toEqual(['Alice']);
  });

  it('excludes names inside elements with class hidden or unowned', async () => {
    const html = `
      <html><body>
        <ul>
          <li class="hidden">HiddenName</li>
          <li>VisibleName</li>
        </ul>
        <div class="some unowned extra">AlsoHidden</div>
      </body></html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const chars = [
      { id: 'char_001_hidden', name: 'HiddenName' },
      { id: 'char_002_visible', name: 'VisibleName' },
      { id: 'char_003_alsohidden', name: 'AlsoHidden' },
    ];
    const out = await fetchKroosterBrowser('user', chars);
    expect(out).toEqual(['VisibleName']);
  });

  it('normalizes names (ignores punctuation/diacritics) when matching', async () => {
    const html = '<html><body><div>Mr Nothing</div><div>José</div></body></html>';
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const chars = [
      { id: 'char_001_mrnothing', name: 'Mr. Nothing' },
      { id: 'char_002_jose', name: 'Jose' },
      { id: 'char_003_jose2', name: 'José' },
    ];
    const out = await fetchKroosterBrowser('user', chars);
    // 'Jose' should match 'José' after normalization
    expect(out).toEqual(expect.arrayContaining(['Jose']));
  });

  it('matches alter characters with "the" format (e.g., "Texas the Omertosa")', async () => {
    // Krooster displays alter characters with subtitle and main name in separate divs
    const html = `
      <html><body>
        <div class="MuiBox-root css-1pcyk9x">Omertosa</div>
        <div class="MuiBox-root css-14q7abb">Texas</div>
        <div class="MuiBox-root css-1pcyk9x">Decadenza</div>
        <div class="MuiBox-root css-14q7abb">Lappland</div>
        <div>Regular Character</div>
      </body></html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const out = await fetchKroosterBrowser(
      'user',
      makeChars([
        'Texas the Omertosa',
        'Lappland the Decadenza',
        'Regular Character',
        'Not Present',
      ]),
    );

    expect(out).toContain('Texas the Omertosa');
    expect(out).toContain('Lappland the Decadenza');
    expect(out).toContain('Regular Character');
    expect(out).not.toContain('Not Present');
    expect(out.length).toBe(3);
  });

  it('matches when alter name appears with extra spacing or newlines', async () => {
    // More realistic: whitespace/newlines between divs
    const html = `
      <html><body>
        <div class="MuiBox-root css-1pcyk9x">
          Omertosa
        </div>
        <div class="MuiBox-root css-14q7abb">
          Texas
        </div>
      </body></html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const out = await fetchKroosterBrowser('user', makeChars(['Texas the Omertosa']));

    expect(out).toContain('Texas the Omertosa');
  });

  it('matches when there are many other characters on the page', async () => {
    // Realistic scenario: page with multiple characters where order matters
    const html = `
      <html><body>
        <div>Amiya</div>
        <div class="MuiBox-root css-1pcyk9x">Omertosa</div>
        <div class="MuiBox-root css-14q7abb">Texas</div>
        <div>Ch'en</div>
        <div class="MuiBox-root css-1pcyk9x">Decadenza</div>
        <div class="MuiBox-root css-14q7abb">Lappland</div>
        <div>Exusiai</div>
      </body></html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const out = await fetchKroosterBrowser(
      'user',
      makeChars(['Texas the Omertosa', 'Lappland the Decadenza', 'Amiya', 'Exusiai', "Ch'en"]),
    );

    expect(out).toContain('Texas the Omertosa');
    expect(out).toContain('Lappland the Decadenza');
    expect(out).toContain('Amiya');
    expect(out).toContain('Exusiai');
    expect(out).toContain("Ch'en");
    expect(out.length).toBe(5);
  });

  it('does NOT match base character when looking for alter', async () => {
    // If krooster only has "Texas" (base), it should NOT match "Texas the Omertosa"
    const html = `
      <html><body>
        <div>Texas</div>
        <div>Lappland</div>
      </body></html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const out = await fetchKroosterBrowser(
      'user',
      makeChars(['Texas the Omertosa', 'Lappland the Decadenza', 'Texas', 'Lappland']),
    );

    // Should only match base characters, not alters
    expect(out).not.toContain('Texas the Omertosa');
    expect(out).not.toContain('Lappland the Decadenza');
    expect(out).toContain('Texas');
    expect(out).toContain('Lappland');
    expect(out.length).toBe(2);
  });

  it('does NOT match false positives from CSS or HTML noise', async () => {
    // Real-world problem: inline styles and data attributes
    const html = `
      <html>
        <body>
          <div style="font-family: Lato; webkit-font-smoothing: antialiased">
            <span data-testid="Line">Actual Character Name</span>
            <div class="css-box-sizing-border-box">W</div>
          </div>
        </body>
      </html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const out = await fetchKroosterBrowser(
      'user',
      makeChars(['Lato', 'Line', 'Box', 'W', 'Actual Character Name']),
    );

    // textContent should only get the visible text, not attributes
    expect(out).not.toContain('Lato');
    expect(out).not.toContain('Line');
    expect(out).not.toContain('Box');
    expect(out).toContain('W');
    expect(out).toContain('Actual Character Name');
    expect(out.length).toBe(2);
  });

  it('works with realistic Krooster HTML structure', async () => {
    // Based on actual Krooster page structure with css-rl7vtn container
    const html = `
      <html>
        <body>
          <li class="MuiBox-root css-1obf64m">
            <div class="MuiBox-root css-rl7vtn">
              <div class="MuiBox-root css-1pcyk9x">Omertosa</div>
              <div class="MuiBox-root css-14q7abb">Texas</div>
            </div>
          </li>
          <li class="MuiBox-root css-1obf64m">
            <div class="MuiBox-root css-rl7vtn">
              <div class="MuiBox-root css-14q7abb">Exusiai</div>
            </div>
          </li>
          <li class="MuiBox-root css-1obf64m unowned">
            <div class="MuiBox-root css-rl7vtn">
              <div class="MuiBox-root css-14q7abb">W</div>
            </div>
          </li>
        </body>
      </html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const out = await fetchKroosterBrowser(
      'user',
      makeChars(['Texas the Omertosa', 'Texas', 'Exusiai', 'W']),
    );

    expect(out).toContain('Texas the Omertosa');
    expect(out).not.toContain('Texas'); // Should NOT match base when alter is present
    expect(out).toContain('Exusiai');
    expect(out).not.toContain('W'); // Should be filtered by 'unowned' class
    expect(out.length).toBe(2);
  });

  it('extracts character IDs from __NEXT_DATA__ JSON when present', async () => {
    // Test the new JSON-based extraction method
    const html = `
      <html>
        <head>
          <script id="__NEXT_DATA__" type="application/json">
            {
              "props": {
                "pageProps": {
                  "username": "test-user",
                  "data": {
                    "roster": {
                      "char_002_amiya": {
                        "skin": "char_002_amiya",
                        "elite": 2,
                        "level": 90
                      },
                      "char_4064_mlynar": {
                        "skin": "char_4064_mlynar",
                        "elite": 2,
                        "level": 90
                      },
                      "char_1012_skadi2": {
                        "skin": "char_1012_skadi2",
                        "elite": 2,
                        "level": 90
                      }
                    }
                  }
                }
              }
            }
          </script>
        </head>
        <body></body>
      </html>
    `;
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const chars = [
      { id: 'char_002_amiya', name: 'Amiya' },
      { id: 'char_003_kalts', name: "Kal'tsit" },
      { id: 'char_4064_mlynar', name: 'Mlynar' },
      { id: 'char_1012_skadi2', name: 'Skadi the Corrupting Heart' },
    ];

    const out = await fetchKroosterBrowser('user', chars);

    // Should match by ID, not by name matching
    expect(out).toContain('Amiya');
    expect(out).not.toContain("Kal'tsit"); // Not in roster
    expect(out).toContain('Mlynar');
    expect(out).toContain('Skadi the Corrupting Heart');
    expect(out.length).toBe(3);
  });
});
