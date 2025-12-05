# Test Fixtures

## user_data_response.json

Full authenticated user data response from `/my/roster` endpoint.

**Source:** Real game API response via `arkprts` client  
**Date:** 2025-11-14  
**Server:** EN (English/Global)  
**Operators:** 257

### Structure

```json
{
  "ok": true,
  "data": {
    "user": {
      "troop": {
        "chars": {
          /* 257 operators */
        }
      },
      "inventory": {
        /* materials, items */
      },
      "building": {
        /* base/infrastructure */
      },
      "status": {
        /* player status */
      }
      // ... many other fields
    },
    "result": 0,
    "ts": 1731650000
  }
}
```

### Operator Data Fields

Each operator in `data.user.troop.chars` includes:

- `charId` — operator identifier (e.g., "char_002_amiya")
- `instId` — instance ID
- `level` — current level
- `evolvePhase` — elite promotion (0, 1, or 2)
- `potentialRank` — potential level (0-5)
- `mainSkillLvl` — skill mastery level (1-7)
- `favorPoint` — trust value
- `skills` — array of skill details with specialization levels
- `equip` — module/equipment data
- `tmpl` — template data for multi-form operators (like Amiya)
- `voiceLan` — voice language setting
- `skin` — current skin ID
- `gainTime` — timestamp when operator was obtained

### Usage in Tests

```python
import json
from pathlib import Path

fixture_path = Path(__file__).parent / "fixtures" / "user_data_response.json"
with open(fixture_path) as f:
    response = json.load(f)

roster = response["data"]["user"]["troop"]["chars"]
print(f"Operators: {len(roster)}")
```
