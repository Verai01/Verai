# src/game/combat/battle_system.py

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid
from datetime import datetime
import logging
import random
from .skills import SkillSystem, SkillType, SkillEffect
class BattleState(Enum):
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class BattleType(Enum):
    DUEL = "duel"             
    TEAM = "team"             
    FREE_FOR_ALL = "ffa"     
    BOSS = "boss"               
    TOURNAMENT = "tournament"    

@dataclass
class BattleParticipant:
    id: str
    team_id: str
    position: Tuple[float, float, float]
    health: float
    energy: float
    status_effects: List[Dict]
    active_skills: List[str]
    cooldowns: Dict[str, float]

class BattleSystem:

    def __init__(self):
        self.active_battles: Dict[str, Dict] = {}
        self.battle_history: List[Dict] = []
        self.skill_system = SkillSystem()
        self.battle_queue: List[Dict] = []

        self.metrics: Dict[str, float] = {}

    def create_battle(self,
                     battle_type: BattleType,
                     participants: List[Dict],
                     settings: Dict) -> Dict:

        try:
            battle_id = str(uuid.uuid4())

            validation = self._validate_battle_setup(
                battle_type,
                participants,
                settings
            )

            if not validation['valid']:
                return {'success': False, 'reason': validation['reason']}

            battle = {
                'id': battle_id,
                'type': battle_type,
                'state': BattleState.PREPARING,
                'start_time': datetime.now(),
                'participants': {},
                'teams': {},
                'rounds': [],
                'current_round': 0,
                'settings': settings,
                'environment': self._create_battle_environment(settings),
                'events': []
            }

            for participant in participants:
                self._add_participant(battle, participant)

            self.active_battles[battle_id] = battle

            return {
                'success': True,
                'battle_id': battle_id,
                'battle': battle
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def update(self, delta_time: float) -> Dict:

        updates = {
            'completed_battles': [],
            'battle_updates': [],
            'events': []
        }

        try:
            for battle_id, battle in self.active_battles.items():
                if battle['state'] == BattleState.IN_PROGRESS:

                    battle_update = self._update_battle(battle, delta_time)
                    updates['battle_updates'].append(battle_update)

                    if self._check_battle_end(battle):
                        self._end_battle(battle)
                        updates['completed_battles'].append(battle_id)

            return {'success': True, 'updates': updates}

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def process_action(self,
                      battle_id: str,
                      actor_id: str,
                      action_type: str,
                      targets: List[str],
                      action_data: Dict) -> Dict:

        try:
            battle = self.active_battles.get(battle_id)
            if not battle:
                return {'success': False, 'reason': 'Battle not found'}

            validation = self._validate_action(
                battle,
                actor_id,
                action_type,
                targets,
                action_data
            )

            if not validation['valid']:
                return {'success': False, 'reason': validation['reason']}

            result = self._execute_action(
                battle,
                actor_id,
                action_type,
                targets,
                action_data
            )

            self._update_battle_state(battle, result)

            return {
                'success': True,
                'result': result,
                'battle_state': battle['state']
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _update_battle(self, battle: Dict, delta_time: float) -> Dict:

        updates = {
            'battle_id': battle['id'],
            'state_changes': [],
            'effects_processed': []
        }

        self._update_cooldowns(battle, delta_time)

        status_updates = self._process_status_effects(battle, delta_time)
        updates['effects_processed'].extend(status_updates)

        position_updates = self._update_positions(battle, delta_time)
        updates['state_changes'].extend(position_updates)

        environment_updates = self._update_environment(battle, delta_time)
        updates['state_changes'].extend(environment_updates)

        return updates

    def _execute_action(self,
                       battle: Dict,
                       actor_id: str,
                       action_type: str,
                       targets: List[str],
                       action_data: Dict) -> Dict:

        results = {
            'effects': [],
            'damage_dealt': {},
            'status_effects': [],
            'position_changes': []
        }

        base_effects = self._calculate_action_effects(
            battle,
            actor_id,
            action_type,
            action_data
        )

        for target_id in targets:
            target_results = self._apply_effects_to_target(
                battle,
                target_id,
                base_effects,
                action_data
            )

            results['effects'].extend(target_results['effects'])
            results['damage_dealt'][target_id] = target_results['damage']
            results['status_effects'].extend(target_results['status_effects'])

        environment_effects = self._process_environment_effects(
            battle,
            action_type,
            action_data
        )

        results['effects'].extend(environment_effects)

        return results
