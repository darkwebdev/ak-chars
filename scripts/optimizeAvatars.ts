import fs from 'fs';
import path from 'path';
import { optimizeImage } from '../src/server/optimiseImages.js';

function parseLimit(): number | undefined {
  const a = process.argv.slice(2).find((s) => s.startsWith('--limit='));
  if (!a) return undefined;
  const n = Number(a.split('=')[1]);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : undefined;
}

async function main(dirArg?: string) {
  // pick first non-flag argument as dir, otherwise default to data/avatars
  const nonFlag = process.argv.slice(2).find((s) => !s.startsWith('--'));
  const readFromDir = dirArg || nonFlag || path.join(process.cwd(), 'data', 'avatars');
  const writeToDir = path.join(process.cwd(), 'public', 'avatars');
  if (!fs.existsSync(readFromDir)) {
    fs.mkdirSync(readFromDir, { recursive: true });
  }
  const limit = parseLimit();
  const files = fs
    .readdirSync(readFromDir)
    .filter((f) => ['.png', '.webp', '.gif', '.jpeg'].includes(path.extname(f).toLowerCase()))
    .map((f) => path.join(readFromDir, f));
  let convertedCount = 0;
  const toProcess = typeof limit === 'number' ? files.slice(0, limit) : files;
  for (const f of toProcess) {
    // do not parallelize to avoid memory spikes
    // eslint-disable-next-line no-await-in-loop
    const ok = await optimizeImage(f, writeToDir, 'png');
    if (ok) convertedCount += 1;
    else console.log('Skipped', f);
  }
  console.log(`Optimiser: converted ${convertedCount} file(s) in ${readFromDir}`);
  return convertedCount;
}

main()
  .then((n) => {
    console.log(`Optimiser finished, converted ${n} file(s)`);
    process.exit(0);
  })
  .catch((err) => {
    console.error('Optimiser failed:', err && err.stack ? err.stack : err);
    process.exit(1);
  });
