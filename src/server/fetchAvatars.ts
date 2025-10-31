import fs from 'fs';
import path from 'path';
import type { Char } from '../types';

const BASE =
  'https://raw.githubusercontent.com/akgcc/arkdata/main/assets/torappu/dynamicassets/arts/charavatars';

type Options = {
  chars: Char[];
  outDir?: string;
  limit?: number;
  concurrency?: number;
};

export async function fetchAvatars({
  chars,
  outDir = 'data/avatars',
  limit = 3,
  concurrency = 8,
}: Options) {
  if (!chars)
    throw new Error(
      'No chars provided. Use the script to read data/chars.json and pass chars array.',
    );

  const outPath = path.resolve(process.cwd(), outDir);
  if (!fs.existsSync(outPath)) fs.mkdirSync(outPath, { recursive: true });

  let inFlight = 0;
  let index = 0;

  async function downloadOne(charId: string, outPath: string) {
    const url = `${BASE}/${charId}.png`;
    const res = await fetch(url);
    if (!res.ok) {
      console.warn(`Failed ${res.status} ${res.statusText} for ${url}`);
    }
    const ab = await res.arrayBuffer();
    fs.writeFileSync(outPath, Buffer.from(ab));
  }

  async function next(): Promise<void> {
    if (limit !== undefined && index >= limit) return;
    if (index >= chars.length) return;
    const char = chars[index++];
    if (!char.id) return next();
    const outPath = path.join(outDir, `${char.id}.png`);
    if (fs.existsSync(outPath)) {
      return next();
    }
    inFlight++;
    try {
      await downloadOne(char.id, outPath);
      console.log('Avatar saved to', outPath);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error('Error fetching avatar', char.id, msg);
    } finally {
      inFlight--;
      await next();
    }
  }

  const starters: Promise<void>[] = [];
  for (let i = 0; i < concurrency; i++) starters.push(next());
  // wait for completion
  while (inFlight > 0 || index < (limit ?? chars.length)) {
    // small sleep
    // eslint-disable-next-line no-await-in-loop
    await new Promise((r) => setTimeout(r, 200));
    if (limit !== undefined && index >= limit && inFlight === 0) break;
    if (index >= chars.length && inFlight === 0) break;
  }
}
