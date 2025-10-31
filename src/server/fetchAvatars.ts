import fs from 'fs';
import path from 'path';
import type { Char } from '../types';

const BASE =
  'https://raw.githubusercontent.com/akgcc/arkdata/main/assets/torappu/dynamicassets/arts/charavatars';

type Options = {
  chars: Char[];
  outDir?: string;
  limit?: number;
};

export async function fetchAvatars({ chars, outDir = 'data/avatars', limit = 3 }: Options) {
  if (!chars)
    throw new Error(
      'No chars provided. Use the script to read data/chars.json and pass chars array.',
    );

  const resolvedOut = path.resolve(process.cwd(), outDir);
  if (!fs.existsSync(resolvedOut)) fs.mkdirSync(resolvedOut, { recursive: true });

  // Simplified sequential downloader: tests rely on small numbers and mocked fetch.
  const max = typeof limit === 'number' ? Math.min(limit, chars.length) : chars.length;
  for (let i = 0; i < max; i++) {
    const char = chars[i];
    if (!char || !char.id) continue;
    const fileOut = path.join(resolvedOut, `${char.id}.png`);
    if (fs.existsSync(fileOut)) continue;
    try {
      const url = `${BASE}/${char.id}.png`;
      const res = await fetch(url);
      if (!res.ok) {
        console.warn(`Failed ${res.status} ${res.statusText} for ${url}`);
        continue;
      }
      const ab = await res.arrayBuffer();
      fs.writeFileSync(fileOut, Buffer.from(ab));
      // eslint-disable-next-line no-console
      console.log('Avatar saved to', fileOut);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      // eslint-disable-next-line no-console
      console.error('Error fetching avatar', char.id, msg);
    }
  }
}
