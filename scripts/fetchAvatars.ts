import { fetchAvatars } from '../src/server/fetchAvatars';
import chars from '../data/chars.json';
import { Char } from '../src/types';

const arg = process.argv.find((s) => s.startsWith('--limit='));
const limit = arg ? Number(arg.split('=')[1]) : undefined;
const concurrencyArg = process.argv.find((s) => s.startsWith('--concurrency='));
const concurrency = concurrencyArg ? Number(concurrencyArg.split('=')[1]) : undefined;

(async () => {
  try {
    if (!chars || !Array.isArray(chars))
      throw new Error('data/chars.json not found or invalid. Run "yarn fetch-chars" first.');

    await fetchAvatars({
      chars: chars as Char[],
      limit: Number.isFinite(limit) ? limit : undefined,
      concurrency: Number.isFinite(concurrency) ? concurrency : undefined,
    });
    console.log('Done');
  } catch (err: any) {
    console.error(err?.stack ?? err);
    process.exit(1);
  }
})();
