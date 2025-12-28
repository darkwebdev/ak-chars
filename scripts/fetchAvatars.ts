import { fetchAvatars } from '../src/server/fetchAvatars';
import { readFileSync } from 'fs';
import { join } from 'path';
import { Char } from '../src/types.js';

const chars = JSON.parse(
  readFileSync(join(process.cwd(), 'data', 'chars.json'), 'utf-8')
) as Char[];

const arg = process.argv.find((s) => s.startsWith('--limit='));
const limit = arg ? Number(arg.split('=')[1]) : undefined;

(async () => {
  try {
    if (!chars || !Array.isArray(chars))
      throw new Error('data/chars.json not found or invalid. Run "yarn fetch-chars" first.');

    await fetchAvatars({
      chars: chars as Char[],
      limit: Number.isFinite(limit) ? limit : undefined,
    });
    console.log('Done');
  } catch (err: any) {
    console.error(err?.stack ?? err);
    process.exit(1);
  }
})();
