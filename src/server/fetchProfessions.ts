const CN_URL =
  'https://raw.githubusercontent.com/ArknightsAssets/ArknightsGameData/master/cn/gamedata/excel/uniequip_table.json';
const EN_URL =
  'https://raw.githubusercontent.com/ArknightsAssets/ArknightsGameData/master/en/gamedata/excel/uniequip_table.json';

type SubProfessionWithCat = {
  subProfessionId: string;
  subProfessionName: string;
  subProfessionCatagory: number;
};

export async function fetchProfessions(): Promise<SubProfessionWithCat[]> {
  const [cnRes, enRes] = await Promise.all([fetch(CN_URL), fetch(EN_URL)]);
  if (!cnRes.ok) throw new Error(`Failed to fetch CN data: ${cnRes.status}`);
  if (!enRes.ok) throw new Error(`Failed to fetch EN data: ${enRes.status}`);

  const cn = (await cnRes.json()) as unknown;
  const en = (await enRes.json()) as unknown;

  const cnSubRaw = (cn && (cn as unknown as Record<string, unknown>)['subProfDict']) || {};
  const enSubRaw = (en && (en as unknown as Record<string, unknown>)['subProfDict']) || {};
  const cnSub = cnSubRaw as Record<string, unknown>;
  const enSub = enSubRaw as Record<string, unknown>;

  const result: SubProfessionWithCat[] = [];

  for (const [id, cnEntry] of Object.entries(cnSub)) {
  const enEntry = enSub[id] as unknown as Partial<SubProfessionWithCat> | undefined;
  const name = enEntry?.subProfessionName || id; // prefer EN name, fallback to id
  const cnEntryRec = cnEntry as unknown as Partial<SubProfessionWithCat> | undefined;
  const cat = cnEntryRec?.subProfessionCatagory ?? enEntry?.subProfessionCatagory;
  result.push({ subProfessionId: id, subProfessionName: name, subProfessionCatagory: cat as number });
    if (!enEntry)
      console.log(`subProfessionId ${id} missing in EN data, no translation available.`);
  }

  // Sort by category asc
  result.sort((a, b) => {
    const aCat = a.subProfessionCatagory ?? Number.MAX_SAFE_INTEGER;
    const bCat = b.subProfessionCatagory ?? Number.MAX_SAFE_INTEGER;
    return aCat - bCat;
  });

  return result;
}
