import fs from 'fs';
import path from 'path';

function normalizeName(s: string) {
  return s
    .normalize('NFKD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim()
    .toLowerCase();
}

function similar(a: string, b: string) {
  const na = normalizeName(a);
  const nb = normalizeName(b);
  if (na === nb) return true;
  if (na.includes(nb) || nb.includes(na)) return true;
  return false;
}

function main() {
  const dataDir = path.resolve(process.cwd(), 'data');
  const charsPath = path.join(dataDir, 'chars.json');
  const tiersPath = path.join(dataDir, 'charTiers.json');

  if (!fs.existsSync(charsPath) || !fs.existsSync(tiersPath)) {
    console.error('Missing data files in data/');
    process.exit(1);
  }

  const chars = JSON.parse(fs.readFileSync(charsPath, 'utf8')) as any[];
  const tiers = JSON.parse(fs.readFileSync(tiersPath, 'utf8')) as Record<string, string>;

  const tierKeys = Object.keys(tiers || {});

  const missing: { name: string; id: string; suggestions: string[] }[] = [];
  for (const ch of chars) {
    // prefer `name` (new key), fall back to legacy `appellation` if present
    const name = ch.name || ch.appellation || '';
    if (!name) continue;
    if (tiers[name]) continue;
    // Try normalized existence
    const nname = normalizeName(name);
    const found = tierKeys.find((k) => normalizeName(k) === nname || similar(k, name));
    if (!found) {
      // find few close candidates
      const suggestions = tierKeys.filter((k) => similar(k, name)).slice(0, 5);
      missing.push({ name, id: ch.id, suggestions });
    }
  }

  if (missing.length === 0) {
    console.log('No missing characters found.');
    return;
  }
  console.log(`Found ${missing.length} characters missing from charTiers.json`);
  for (const m of missing) {
    console.log(`- ${m.name} (${m.id})`);
    if (m.suggestions.length) console.log(`   suggestions: ${m.suggestions.join(', ')}`);
  }
}

main();
