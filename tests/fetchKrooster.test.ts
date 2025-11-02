import { jest } from '@jest/globals';
import { fetchKroosterBrowser } from '../src/client/utils/krooster';

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

    const out = await fetchKroosterBrowser('user', ['Alice', 'Bob']);
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

    const out = await fetchKroosterBrowser('user', ['HiddenName', 'VisibleName', 'AlsoHidden']);
    expect(out).toEqual(['VisibleName']);
  });

  it('normalizes names (ignores punctuation/diacritics) when matching', async () => {
    const html = '<html><body><div>Mr Nothing</div><div>José</div></body></html>';
    // @ts-ignore
    global.fetch = jest.fn().mockResolvedValue({ ok: true, text: async () => html });

    const out = await fetchKroosterBrowser('user', ['Mr. Nothing', 'Jose', 'José']);
    // 'Jose' should match 'José' after normalization
    expect(out).toEqual(expect.arrayContaining(['Jose']));
  });
});
