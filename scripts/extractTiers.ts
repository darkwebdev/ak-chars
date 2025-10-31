import { generateCharTiers } from '../src/server/extractor';

const GoogleSheetId = '1E7HmgKWiV8pKpJpvpVzziYxnaQTP01Vtw_PXEdL7XPA';

async function main() {
  try {
    const out = await generateCharTiers(GoogleSheetId);
    console.log('Wrote char->tier map to', out);
  } catch (err) {
    console.error(err && (err as Error).stack ? (err as Error).stack : err);
    process.exit(1);
  }
}

main();
