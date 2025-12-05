type TableCell = { v?: unknown; f?: unknown } | null;
type TableRow = { c: TableCell[] };
type Table = { cols: { label?: string; id?: string }[]; rows: TableRow[] };

export function extractJsonFromGviz(text: string) {
  const m = text.match(/setResponse\(([\s\S]*)\);?\s*%?$/);
  if (!m) throw new Error('Failed to parse gviz response');
  return JSON.parse(m[1]);
}

export function tableToMatrix(table: Table) {
  const extractCell = (cell: TableCell) => {
    if (!cell) return null;
    if (cell.v !== undefined) return cell.v;
    const f = cell.f;
    if (typeof f === 'string') {
      // Try to extract alt or title attributes from HTML (common when images are used)
      const altMatch = f.match(/alt=(?:"|')([^"']+)(?:"|')/i);
      if (altMatch) return altMatch[1];
      const titleMatch = f.match(/title=(?:"|')([^"']+)(?:"|')/i);
      if (titleMatch) return titleMatch[1];
      // Otherwise strip tags and return text content
      const stripped = f.replace(/<[^>]+>/g, '').trim();
      return stripped === '' ? null : stripped;
    }
    return f !== undefined ? f : null;
  };

  const rows = table.rows.map((r) => r.c.map((cell) => extractCell(cell)));
  return { cols: table.cols.map((c) => c.label || c.id || ''), rows };
}

// Given matrix rows (from tableToMatrix), where first row is header and then
// tier rows alternate with data rows (tier in first column, characters in next row),
// return char->tier mapping.
export function buildCharMapFromMatrix(rows: unknown[][]) {
  const map: Record<string, string> = {};
  // More robust approach: don't assume strict alternating rows. Instead,
  // for each row that contains a tier label in column 0, look for character
  // data either on the same row (columns 1+) or on the next non-empty data row.
  for (let r = 1; r < rows.length; r++) {
    const tierRow = rows[r] || [];
    const tierVal = tierRow[0];
    const tier = tierVal !== undefined && tierVal !== null ? String(tierVal).trim() : null;
    if (!tier) continue;

    // Helper to map a data row's columns (1..end) to the given tier
    const mapDataRow = (dataRow: unknown[] | undefined) => {
      if (!dataRow) return;
      for (let c = 1; c < dataRow.length; c++) {
        const val = dataRow[c];
        if (val !== null && val !== undefined) {
          const s = String(val).trim();
          if (s !== '') map[s] = tier;
        }
      }
    };

    // First, check if the same row contains character names in columns 1+
    const sameRow = tierRow;
    const hasSameRowChars =
      sameRow &&
      sameRow.slice(1).some((v) => v !== null && v !== undefined && String(v).trim() !== '');
    if (hasSameRowChars) {
      mapDataRow(sameRow);
      continue; // done with this tier
    }

    // Otherwise, search forward for the next row that contains character names
    let dataRowIndex = r + 1;
    while (dataRowIndex < rows.length) {
      const candidate = rows[dataRowIndex] || [];
      // If we hit another tier label, stop searching — no data for this tier
      const candidateTier = candidate[0];
      if (
        candidateTier !== null &&
        candidateTier !== undefined &&
        String(candidateTier).trim() !== ''
      ) {
        break;
      }
      const hasChars = candidate
        .slice(1)
        .some((v) => v !== null && v !== undefined && String(v).trim() !== '');
      if (hasChars) {
        mapDataRow(candidate);
        break;
      }
      dataRowIndex++;
    }
    // Continue scanning; don't skip ahead because there may be consecutive tiers
  }
  return map;
}

// Secondary helper: given the matrix rows, for any data cell not yet mapped,
// try to find the nearest tier by scanning upward in column 0.
export function backfillTiersFromMatrix(rows: unknown[][], map: Record<string, string>) {
  for (let r = 1; r < rows.length; r++) {
    const row = rows[r] || [];
    for (let c = 1; c < row.length; c++) {
      const val = row[c];
      if (val === null || val === undefined) continue;
      const s = String(val).trim();
      if (s === '') continue;
      if (map[s]) continue; // already mapped

      // search upward for nearest non-empty tier in column 0
      let foundTier: string | null = null;
      for (let i = r - 1; i >= 1; i--) {
        const candidate = rows[i] || [];
        const candTier = candidate[0];
        if (candTier !== null && candTier !== undefined && String(candTier).trim() !== '') {
          foundTier = String(candTier).trim();
          break;
        }
      }
      if (foundTier) map[s] = foundTier;
    }
  }
}

// Fetch a Google sheet (gviz endpoint) and return the parsed table object
export async function fetchSheet(sheetId: string, sheetName = 'The Tier List') {
  const url = `https://docs.google.com/spreadsheets/d/${sheetId}/gviz/tq?tqx=out:json&sheet=${encodeURIComponent(
    sheetName,
  )}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch sheet: ${res.status} ${res.statusText}`);
  const text = await res.text();
  return extractJsonFromGviz(text).table;
}

// High-level helper: fetch sheet, build char->tier map and write to data/charTiers.json
export async function generateCharTiers(sheetId: string, sheetName = 'The Tier List') {
  const table = await fetchSheet(sheetId, sheetName);
  const { rows } = tableToMatrix(table as Table);
  const map = buildCharMapFromMatrix(rows);
  // Backfill any unmapped data cells by scanning upward for nearest tier
  backfillTiersFromMatrix(rows, map);
  return map;
}
