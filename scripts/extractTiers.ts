import { generateCharTiers } from '../src/server/extractor';
import fs from 'fs';
import path from 'path';

const GoogleSheetId = '1E7HmgKWiV8pKpJpvpVzziYxnaQTP01Vtw_PXEdL7XPA';

async function main() {
  try {
    const map = await generateCharTiers(GoogleSheetId);
    const outDir = path.resolve(process.cwd(), 'data');
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
    const outPath = path.join(outDir, 'charTiers.json');
    fs.writeFileSync(outPath, JSON.stringify(map, null, 2), 'utf8');
    console.log('Wrote char->tier map to', outPath);
  } catch (err) {
    console.error(err && (err as Error).stack ? (err as Error).stack : err);
    process.exit(1);
  }
}

main();
