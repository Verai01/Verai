# src/game/social/faction_system.py

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import uuid
from datetime import datetime
import logging
import numpy as np
class FactionType(Enum):
    MILITARY = "military"
    MERCHANT = "merchant"
    SPIRITUAL = "spiritual"
    SCIENTIFIC = "scientific"
    NEUTRAL = "neutral"
    ROGUE = "rogue"

class FactionRank(Enum):
    LEADER = "leader"
    ELDER = "elder"
    VETERAN = "veteran"
    MEMBER = "member"
    RECRUIT = "recruit"
    OUTSIDER = "outsider"

class DiplomaticStatus(Enum):
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    WAR = "war"

@dataclass
class FactionMember:
    id: str
    rank: FactionRank
    join_date: datetime
    contribution_points: int
    roles: List[str]
    permissions: Dict[str, bool]
    achievements: List[str]

class FactionSystem:

    def __init__(self):
        self.factions: Dict[str, Dict] = {}
        self.relationships: Dict[str, Dict[str, float]] = {}
        self.alliance_threshold = 0.7
        self.conflict_threshold = -0.3

        self.faction_history: Dict[str, List[Dict]] = {}
        self.diplomatic_events: List[Dict] = []
        self.territory_control: Dict[str, List[str]] = {}

        self.influence_scores: Dict[str, float] = {}
        self.resource_pools: Dict[str, Dict[str, int]] = {}

    def create_faction(self,
                      name: str,
                      faction_type: FactionType,
                      leader_id: str,
                      initial_resources: Dict[str, int] = None) -> Dict:

        try:
            faction_id = str(uuid.uuid4())

            faction = {
                'id': faction_id,
                'name': name,
                'type': faction_type,
                'founded': datetime.now(),
                'leader_id': leader_id,
                'members': {},
                'resources': initial_resources or {},
                'territory': [],
                'relationships': {},
                'policies': self._default_policies(),
                'stats': {
                    'influence': 0.0,
                    'member_count': 1,
                    'resource_value': 0
                }
            }

            self._add_member(faction_id, leader_id, FactionRank.LEADER)

            self._initialize_relationships(faction_id)

            self.factions[faction_id] = faction

            return {
                'success': True,
                'faction_id': faction_id,
                'faction': faction
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def update(self, delta_time: float) -> Dict:

        updates = {
            'diplomatic_changes': [],
            'territory_changes': [],
            'resource_changes': [],
            'events': []
        }

        try:

            self._update_relationships(delta_time)

            self._update_resources(delta_time)

            self._update_territories(delta_time)

            self._update_influence_scores()

            self._check_diplomatic_events(updates)

            return {'success': True, 'updates': updates}

        except Exception as e:
            logging.error(f"Faction system update error: {str(e)}")
            return {'success': False, 'reason': str(e)}

    def handle_diplomatic_action(self,
                               initiator_id: str,
                               target_id: str,
                               action_type: str,
                               details: Dict) -> Dict:

        try:
            if not self._validate_diplomatic_action(
                initiator_id,
                target_id,
                action_type,
                details
            ):
                return {'success': False, 'reason': 'Invalid diplomatic action'}

            result = self._execute_diplomatic_action(
                initiator_id,
                target_id,
                action_type,
                details
            )

            self._update_relationship_from_action(
                initiator_id,
                target_id,
                action_type,
                result
            )

            return {
                'success': True,
                'result': result,
                'relationship_change': self._get_relationship_change(
                    initiator_id,
                    target_id
                )
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def manage_territory(self,
                        faction_id: str,
                        territory_id: str,
                        action: str) -> Dict:

        try:
            if action == "claim":
                result = self._claim_territory(faction_id, territory_id)
            elif action == "abandon":
                result = self._abandon_territory(faction_id, territory_id)
            else:
                return {'success': False, 'reason': 'Invalid territory action'}

            if result['success']:
                self._update_influence_from_territory(faction_id)

            return result

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def manage_resources(self,
                        faction_id: str,
                        resource_type: str,
                        amount: int,
                        action: str) -> Dict:

        try:
            if action == "add":
                result = self._add_resources(faction_id, resource_type, amount)
            elif action == "remove":
                result = self._remove_resources(faction_id, resource_type, amount)
            elif action == "trade":
                result = self._trade_resources(faction_id, resource_type, amount)
            else:
                return {'success': False, 'reason': 'Invalid resource action'}

            if result['success']:
                self._update_faction_stats(faction_id)

            return result

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _update_relationships(self, delta_time: float):

        for faction_id in self.factions:
            for other_id in self.factions:
                if faction_id != other_id:

                    change = self._calculate_natural_relationship_change(
                        faction_id,
                        other_id,
                        delta_time
                    )

                    self._apply_relationship_change(
                        faction_id,
                        other_id,
                        change
                    )

                    self._check_relationship_thresholds(
                        faction_id,
                        other_id
                    )

    def _update_influence_scores(self):

        for faction_id, faction in self.factions.items():

            territory_influence = self._calculate_territory_influence(faction_id)
            resource_influence = self._calculate_resource_influence(faction_id)
            diplomatic_influence = self._calculate_diplomatic_influence(faction_id)
            member_influence = self._calculate_member_influence(faction_id)

            total_influence = (
                territory_influence +
                resource_influence +
                diplomatic_influence +
                member_influence
            )

            faction['stats']['influence'] = total_influence
            self.influence_scores[faction_id] = total_influence