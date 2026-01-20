"""REST endpoints for fixture data (development/testing)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path


router = APIRouter()


def load_fixture_data():
    """Load user data from fixture file for development."""
    fixture_path = Path(__file__).parent / 'tests' / 'user_data_response.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


@router.get('/fixtures/operators')
async def get_operators(
    ids: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    min_elite: Optional[int] = None,
    max_elite: Optional[int] = None,
    min_potential: Optional[int] = None
):
    """Get operators from fixture data with optional filtering.

    Equivalent to GraphQL query: operators

    Query parameters:
    - ids: Comma-separated character IDs
    - min_level: Minimum operator level
    - max_level: Maximum operator level
    - min_elite: Minimum elite level (0-2)
    - max_elite: Maximum elite level (0-2)
    - min_potential: Minimum potential rank (0-5)
    """
    try:
        fixture_data = load_fixture_data()
        chars_dict = fixture_data.get('data', {}).get('user', {}).get('troop', {}).get('chars', {})

        # Parse comma-separated IDs
        id_list = ids.split(',') if ids else None

        operators = []
        for char_data in chars_dict.values():
            char_id = char_data.get('charId', '')
            level = char_data.get('level', 0)
            evolve_phase = char_data.get('evolvePhase', 0)
            potential_rank = char_data.get('potentialRank', 0)

            # Apply filters
            if id_list and char_id not in id_list:
                continue
            if min_level and level < min_level:
                continue
            if max_level and level > max_level:
                continue
            if min_elite is not None and evolve_phase < min_elite:
                continue
            if max_elite is not None and evolve_phase > max_elite:
                continue
            if min_potential is not None and potential_rank < min_potential:
                continue

            operators.append({
                'charId': char_id,
                'level': level,
                'evolvePhase': evolve_phase,
                'elite': evolve_phase,  # alias
                'potentialRank': potential_rank,
                'potential': potential_rank,  # alias
                'mainSkillLvl': char_data.get('mainSkillLvl', 0),
                'favorPoint': char_data.get('favorPoint', 0),
                'skin': char_data.get('skin'),
                'defaultSkillIndex': char_data.get('defaultSkillIndex', -1),
                'gainTime': char_data.get('gainTime'),
                'skills': char_data.get('skills', []),
                'currentEquip': char_data.get('currentEquip')
            })

        return {'ok': True, 'operators': operators}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/fixtures/operator/{char_id}')
async def get_operator(char_id: str):
    """Get a specific operator by ID from fixture data.

    Equivalent to GraphQL query: operator
    """
    try:
        fixture_data = load_fixture_data()
        chars_dict = fixture_data.get('data', {}).get('user', {}).get('troop', {}).get('chars', {})

        for char_data in chars_dict.values():
            if char_data.get('charId') == char_id:
                return {
                    'ok': True,
                    'operator': {
                        'charId': char_data.get('charId', ''),
                        'level': char_data.get('level', 0),
                        'evolvePhase': char_data.get('evolvePhase', 0),
                        'elite': char_data.get('evolvePhase', 0),
                        'potentialRank': char_data.get('potentialRank', 0),
                        'potential': char_data.get('potentialRank', 0),
                        'mainSkillLvl': char_data.get('mainSkillLvl', 0),
                        'favorPoint': char_data.get('favorPoint', 0),
                        'skin': char_data.get('skin'),
                        'defaultSkillIndex': char_data.get('defaultSkillIndex', -1),
                        'gainTime': char_data.get('gainTime'),
                        'skills': char_data.get('skills', []),
                        'currentEquip': char_data.get('currentEquip')
                    }
                }

        raise HTTPException(status_code=404, detail=f'Operator {char_id} not found')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/fixtures/user-status')
async def get_user_status():
    """Get user account status from fixture data.

    Equivalent to GraphQL query: userStatus
    """
    try:
        fixture_data = load_fixture_data()
        status_data = fixture_data.get('data', {}).get('user', {}).get('status', {})

        if not status_data:
            raise HTTPException(status_code=404, detail='Status data not found')

        return {
            'ok': True,
            'status': {
                'nickName': status_data.get('nickName', ''),
                'nickNumber': status_data.get('nickNumber', ''),
                'level': status_data.get('level', 0),
                'exp': status_data.get('exp', 0),
                'socialPoint': status_data.get('socialPoint', 0),
                'uid': status_data.get('uid', '')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
