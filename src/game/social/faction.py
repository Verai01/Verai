# src/game/social/faction.py

from typing import Dict, List, Optional, Set
import numpy as np
from enum import Enum
from dataclasses import dataclass
import uuid

class FactionType(Enum):
    COMBAT = "combat"    TRADE = "trade"
    EXPLORATION = "exploration"
    SPIRITUAL = "spiritual"
    TECHNOLOGICAL = "technological"

@dataclass
class FactionStats:
    influence: float = 100.0
    resources: float = 1000.0
    territory: int = 1
    members: int = 1
    reputation: float = 50.0
    tech_level: float = 1.0

class FactionSystem:

    def __init__(self,
                 faction_id: Optional[str] = None,
                 faction_type: FactionType = FactionType.COMBAT,
                 initial_stats: Optional[FactionStats] = None):
        self.faction_id = faction_id or str(uuid.uuid4())
        self.faction_type = faction_type
        self.stats = initial_stats or FactionStats()

        self.members: Set[str] = set()
        self.leaders: Set[str] = set()
        self.allies: Dict[str, float] = {}  # faction_id: alliance_strength
        self.rivals: Dict[str, float] = {}  # faction_id: rivalry_strength

        self.controlled_territories: Dict[str, Dict] = {}
        self.resource_production: Dict[str, float] = {}
        self.tech_tree_progress: Dict[str, float] = {}

        self.policies: Dict[str, Dict] = {}
        self.active_projects: List[Dict] = []
        self.faction_history: List[Dict] = []

    def add_member(self,
                  agent_id: str,
                  rank: str = "member",
                  contribution: float = 0.0) -> Dict:

        if agent_id in self.members:
            return {'success': False, 'reason': 'Already a member'}

        member_data = {
            'rank': rank,
            'joined_date': np.datetime64('now'),
            'contribution': contribution,
            'achievements': [],
            'permissions': self._get_rank_permissions(rank)
        }

        self.members.add(agent_id)
        if rank == "leader":
            self.leaders.add(agent_id)

        self.stats.members += 1

        return {
            'success': True,
            'member_data': member_data
        }

    def manage_territory(self,
                        territory_id: str,
                        action: str,
                        resources: Optional[Dict] = None) -> Dict:

        if action == "claim":
            if territory_id in self.controlled_territories:
                return {'success': False, 'reason': 'Territory already claimed'}

            territory_data = {
                'claimed_date': np.datetime64('now'),
                'resources': resources or {},
                'development_level': 1,
                'defenders': [],
                'projects': []
            }

            self.controlled_territories[territory_id] = territory_data
            self.stats.territory += 1

        elif action == "develop":
            if territory_id not in self.controlled_territories:
                return {'success': False, 'reason': 'Territory not controlled'}

            territory = self.controlled_territories[territory_id]
            development_cost = self._calculate_development_cost(territory)

            if self.stats.resources >= development_cost:
                self.stats.resources -= development_cost
                territory['development_level'] += 1
                self._update_resource_production(territory_id)
            else:
                return {'success': False, 'reason': 'Insufficient resources'}

        return {
            'success': True,
            'territory_data': self.controlled_territories.get(territory_id, {})
        }

    def form_alliance(self,
                     target_faction_id: str,
                     alliance_terms: Dict) -> Dict:

        if target_faction_id in self.allies:
            return {'success': False, 'reason': 'Alliance already exists'}

        alliance_strength = self._calculate_alliance_strength(alliance_terms)

        self.allies[target_faction_id] = alliance_strength

        self._apply_alliance_benefits(target_faction_id, alliance_terms)

        return {
            'success': True,
            'alliance_strength': alliance_strength,
            'terms': alliance_terms
        }

    def declare_rivalry(self,
                       target_faction_id: str,
                       rivalry_reason: str) -> Dict:

        if target_faction_id in self.rivals:
            return {'success': False, 'reason': 'Rivalry already exists'}

        rivalry_strength = 0.5  # Initial rivalry strength

        self.rivals[target_faction_id] = rivalry_strength

        self._apply_rivalry_effects(target_faction_id)

        return {
            'success': True,
            'rivalry_strength': rivalry_strength,
            'reason': rivalry_reason
        }

    def _calculate_alliance_strength(self, terms: Dict) -> float:

        strength = 0.5  # Base strength

        if 'resource_sharing' in terms:
            strength += 0.1
        if 'military_support' in terms:
            strength += 0.2
        if 'technology_exchange' in terms:
            strength += 0.15
        if 'trade_agreements' in terms:
            strength += 0.1

        return min(strength, 1.0)

    def _apply_alliance_benefits(self,
                               faction_id: str,
                               terms: Dict):

        if 'resource_sharing' in terms:
            self.stats.resources *= 1.1
        if 'technology_exchange' in terms:
            self.stats.tech_level *= 1.05

    def _apply_rivalry_effects(self, faction_id: str):

        self._update_military_stance(aggressive=True)

        self._update_trade_relations(faction_id, penalty=0.2)