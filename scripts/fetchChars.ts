import fs from 'fs';
import path from 'path';
import { fetchChars } from '../src/server/fetchChars';

(async () => {
  try {
    const chars = await fetchChars();
    const outDir = path.resolve(process.cwd(), 'data');
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
    const outPath = path.join(outDir, 'chars.json');
    fs.writeFileSync(outPath, JSON.stringify(chars, null, 2), 'utf8');
    console.log('Wrote', outPath);
  } catch (err: any) {
    console.error(err?.stack ?? err);
    process.exit(1);
  }
})();
