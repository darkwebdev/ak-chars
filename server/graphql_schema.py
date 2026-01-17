"""GraphQL schema for Arknights character data."""
import strawberry
from typing import Optional, List
import os
import json
from pathlib import Path


USE_FIXTURES = os.getenv('USE_FIXTURES', 'true').lower() == 'true'


def load_fixture_data():
    """Load user data from fixture file for development."""
    fixture_path = Path(__file__).parent / 'tests' / 'user_data_response.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


async def get_user_data_with_auth(channel_uid: str, yostar_token: str, server: str):
    """Get user data using authentication credentials."""
    if USE_FIXTURES:
        fixture_data = load_fixture_data()
        return fixture_data.get('data', {}).get('user', {})
    
    # Import here to avoid circular dependency
    from .ark_client import get_user_data
    full_data = await get_user_data(channel_uid, yostar_token, server)
    return full_data.get('user', {})


async def send_auth_code(email: str, server: str):
    """Send authentication code to email."""
    from .ark_client import send_game_auth_code
    await send_game_auth_code(email, server)


async def get_token_from_code(email: str, code: str, server: str):
    """Get authentication token from email code."""
    from .ark_client import get_game_token_from_code
    channel_uid, token = await get_game_token_from_code(email, code, server)
    return {
        'channelUid': channel_uid,
        'yostarToken': token,
        'server': server
    }


@strawberry.type
class Skill:
    """Operator skill information."""
    unlock: int
    level: int
    state: Optional[int] = None
    specialize_level: Optional[int] = None
    complete_upgrade_time: Optional[int] = None


@strawberry.type
class EquipLevel:
    """Equipment level information."""
    level: int
    hide: int


@strawberry.type
class TmplEquip:
    """Equipment template information."""
    id: str
    level: EquipLevel


@strawberry.type
class Operator:
    """Arknights operator (character) data."""
    char_id: str
    level: int
    evolve_phase: int
    potential_rank: int
    main_skill_lvl: int
    favor_point: int
    skin: Optional[str] = None
    default_skill_index: Optional[int] = None
    gain_time: Optional[int] = None
    skills: Optional[List[Skill]] = None
    current_equip: Optional[str] = None
    
    @strawberry.field
    def id(self) -> str:
        """Unique identifier (same as char_id)."""
        return self.char_id
    
    @strawberry.field
    def elite(self) -> int:
        """Elite level (alias for evolve_phase)."""
        return self.evolve_phase
    
    @strawberry.field
    def potential(self) -> int:
        """Potential level (alias for potential_rank)."""
        return self.potential_rank
    
    @strawberry.field
    def skill_level(self) -> int:
        """Main skill level (alias for main_skill_lvl)."""
        return self.main_skill_lvl
    
    @strawberry.field
    def trust(self) -> int:
        """Trust points (alias for favor_point)."""
        return self.favor_point


@strawberry.type
class UserStatus:
    """User account status information."""
    nick_name: str
    nick_number: str
    level: int
    exp: int
    social_point: int
    uid: str
    
    @strawberry.field
    def display_name(self) -> str:
        """Full display name with number."""
        return f"{self.nick_name}#{self.nick_number}"


@strawberry.type
class Query:
    """GraphQL query root."""
    
    @strawberry.field
    def operators(
        self,
        ids: Optional[List[str]] = None,
        min_level: Optional[int] = None,
        max_level: Optional[int] = None,
        min_elite: Optional[int] = None,
        max_elite: Optional[int] = None,
        min_potential: Optional[int] = None,
    ) -> List[Operator]:
        """
        Get operator roster with flexible filtering.
        
        Args:
            ids: Filter by specific operator IDs (char_id)
            min_level: Minimum operator level
            max_level: Maximum operator level
            min_elite: Minimum elite level (0-2)
            max_elite: Maximum elite level (0-2)
            min_potential: Minimum potential rank (0-5)
        """
        fixture_data = load_fixture_data()
        chars_dict = fixture_data.get('data', {}).get('user', {}).get('troop', {}).get('chars', {})
        
        operators = []
        for char_data in chars_dict.values():
            # Map snake_case to camelCase for GraphQL
            operator = Operator(
                char_id=char_data.get('charId', ''),
                level=char_data.get('level', 0),
                evolve_phase=char_data.get('evolvePhase', 0),
                potential_rank=char_data.get('potentialRank', 0),
                main_skill_lvl=char_data.get('mainSkillLvl', 0),
                favor_point=char_data.get('favorPoint', 0),
                skin=char_data.get('skin'),
                default_skill_index=char_data.get('defaultSkillIndex', -1),
                gain_time=char_data.get('gainTime'),
                skills=[
                    Skill(
                        unlock=s.get('unlock', 0),
                        level=s.get('level', 0),
                        state=s.get('state'),
                        specialize_level=s.get('specializeLevel'),
                        complete_upgrade_time=s.get('completeUpgradeTime'),
                    )
                    for s in char_data.get('skills', [])
                ] if 'skills' in char_data else None,
                current_equip=char_data.get('currentEquip'),
            )
            
            # Apply filters
            if ids and operator.char_id not in ids:
                continue
            if min_level and operator.level < min_level:
                continue
            if max_level and operator.level > max_level:
                continue
            if min_elite is not None and operator.evolve_phase < min_elite:
                continue
            if max_elite is not None and operator.evolve_phase > max_elite:
                continue
            if min_potential is not None and operator.potential_rank < min_potential:
                continue
            
            operators.append(operator)
        
        return operators
    
    @strawberry.field
    def operator(self, char_id: str) -> Optional[Operator]:
        """Get a specific operator by ID."""
        fixture_data = load_fixture_data()
        chars_dict = fixture_data.get('data', {}).get('user', {}).get('troop', {}).get('chars', {})
        
        for char_data in chars_dict.values():
            if char_data.get('charId') == char_id:
                return Operator(
                    char_id=char_data.get('charId', ''),
                    level=char_data.get('level', 0),
                    evolve_phase=char_data.get('evolvePhase', 0),
                    potential_rank=char_data.get('potentialRank', 0),
                    main_skill_lvl=char_data.get('mainSkillLvl', 0),
                    favor_point=char_data.get('favorPoint', 0),
                    skin=char_data.get('skin'),
                    default_skill_index=char_data.get('defaultSkillIndex', -1),
                    gain_time=char_data.get('gainTime'),
                    skills=[
                        Skill(
                            unlock=s.get('unlock', 0),
                            level=s.get('level', 0),
                            state=s.get('state'),
                            specialize_level=s.get('specializeLevel'),
                            complete_upgrade_time=s.get('completeUpgradeTime'),
                        )
                        for s in char_data.get('skills', [])
                    ] if 'skills' in char_data else None,
                    current_equip=char_data.get('currentEquip'),
                )
        
        return None
    
    @strawberry.field
    def user_status(self) -> Optional[UserStatus]:
        """Get user account status information."""
        fixture_data = load_fixture_data()
        status_data = fixture_data.get('data', {}).get('user', {}).get('status', {})
        
        if not status_data:
            return None
        
        return UserStatus(
            nick_name=status_data.get('nickName', ''),
            nick_number=status_data.get('nickNumber', ''),
            level=status_data.get('level', 0),
            exp=status_data.get('exp', 0),
            social_point=status_data.get('socialPoint', 0),
            uid=status_data.get('uid', ''),
        )
    
    @strawberry.field
    async def my_roster(
        self,
        channel_uid: str,
        yostar_token: str,
        server: str = "en"
    ) -> List[Operator]:
        """Get authenticated user's roster (equivalent to GET /my/roster)."""
        user_data = await get_user_data_with_auth(channel_uid, yostar_token, server)
        chars_dict = user_data.get('troop', {}).get('chars', {})
        
        operators = []
        for char_data in chars_dict.values():
            operators.append(Operator(
                char_id=char_data.get('charId', ''),
                level=char_data.get('level', 0),
                evolve_phase=char_data.get('evolvePhase', 0),
                potential_rank=char_data.get('potentialRank', 0),
                main_skill_lvl=char_data.get('mainSkillLvl', 0),
                favor_point=char_data.get('favorPoint', 0),
                skin=char_data.get('skin'),
                default_skill_index=char_data.get('defaultSkillIndex', -1),
                gain_time=char_data.get('gainTime'),
                skills=[
                    Skill(
                        unlock=s.get('unlock', 0),
                        level=s.get('level', 0),
                        state=s.get('state'),
                        specialize_level=s.get('specializeLevel'),
                        complete_upgrade_time=s.get('completeUpgradeTime'),
                    )
                    for s in char_data.get('skills', [])
                ] if 'skills' in char_data else None,
                current_equip=char_data.get('currentEquip'),
            ))
        
        return operators
    
    @strawberry.field
    async def my_status(
        self,
        channel_uid: str,
        yostar_token: str,
        server: str = "en"
    ) -> Optional[UserStatus]:
        """Get authenticated user's status (equivalent to GET /my/status)."""
        user_data = await get_user_data_with_auth(channel_uid, yostar_token, server)
        status_data = user_data.get('status', {})
        
        if not status_data:
            return None
        
        return UserStatus(
            nick_name=status_data.get('nickName', ''),
            nick_number=status_data.get('nickNumber', ''),
            level=status_data.get('level', 0),
            exp=status_data.get('exp', 0),
            social_point=status_data.get('socialPoint', 0),
            uid=status_data.get('uid', ''),
        )


@strawberry.type
class AuthCodeResult:
    """Result from sending authentication code."""
    success: bool
    message: str


@strawberry.type
class AuthTokenResult:
    """Result from getting authentication token."""
    success: bool
    channel_uid: Optional[str] = None
    yostar_token: Optional[str] = None
    server: Optional[str] = None
    error: Optional[str] = None


@strawberry.type
class Mutation:
    """GraphQL mutation root."""
    
    @strawberry.mutation
    async def send_auth_code(
        self,
        email: str,
        server: str = "en"
    ) -> AuthCodeResult:
        """Send authentication code to email (equivalent to POST /auth/game-code)."""
        try:
            await send_auth_code(email, server)
            return AuthCodeResult(success=True, message="Code sent successfully")
        except Exception as e:
            return AuthCodeResult(success=False, message=str(e))
    
    @strawberry.mutation
    async def get_auth_token(
        self,
        email: str,
        code: str,
        server: str = "en"
    ) -> AuthTokenResult:
        """Get authentication token from email code (equivalent to POST /auth/game-token)."""
        try:
            result = await get_token_from_code(email, code, server)
            return AuthTokenResult(
                success=True,
                channel_uid=result.get('channelUid'),
                yostar_token=result.get('yostarToken'),
                server=result.get('server')
            )
        except Exception as e:
            return AuthTokenResult(success=False, error=str(e))


schema = strawberry.Schema(query=Query, mutation=Mutation)
