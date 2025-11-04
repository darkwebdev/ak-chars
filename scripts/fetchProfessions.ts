import fs from 'fs';
import path from 'path';
import { fetchProfessions } from '../src/server/fetchProfessions';

(async () => {
  try {
    const professions = await fetchProfessions();
    const outDir = path.resolve(process.cwd(), 'data');
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
    const outPath = path.join(outDir, 'professions.json');
    fs.writeFileSync(outPath, JSON.stringify(professions, null, 2), 'utf8');
    console.log('Wrote', outPath);
  } catch (err: any) {
    console.error(err?.stack ?? err);
    process.exit(1);
  }
})();
