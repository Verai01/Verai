# src/game/social/relationships.py

from typing import Dict, List, Optional, Tuple
import numpy as np
from enum import Enum
import networkx as nx
from dataclasses import dataclass
import uuid

class RelationType(Enum):    ALLY = "ally"
    RIVAL = "rival"
    NEUTRAL = "neutral"
    MENTOR = "mentor"
    STUDENT = "student"
    ENEMY = "enemy"
    FRIEND = "friend"

@dataclass
class SocialStats:
    influence: float = 10.0
    charisma: float = 10.0
    reputation: float = 50.0
    trust_rating: float = 50.0
    leadership: float = 10.0
    social_currency: float = 100.0

class RelationshipSystem:

    def __init__(self, agent_id: str, initial_stats: Optional[SocialStats] = None):
        self.agent_id = agent_id
        self.stats = initial_stats or SocialStats()
        self.relationships = {}
        self.social_network = nx.Graph()
        self.interaction_history = []
        self.reputation_by_faction = {}

        self.metrics = {
            'total_allies': 0,
            'total_rivals': 0,
            'successful_interactions': 0,
            'failed_interactions': 0,
            'influence_gained': 0.0,
            'trust_accumulated': 0.0
        }

        self.current_state = {
            'in_conversation': False,
            'in_trade': False,
            'in_conflict': False,
            'current_interaction_partner': None
        }

    def establish_relationship(self, 
                             target_id: str,
                             relation_type: RelationType,
                             initial_strength: float = 0.5) -> Dict:

        if not self._validate_relationship_parameters(target_id, initial_strength):
            return {'success': False, 'reason': 'Invalid relationship parameters'}

        relationship_data = {
            'type': relation_type,
            'strength': initial_strength,
            'trust_level': self._calculate_initial_trust(initial_strength),
            'interaction_count': 0,
            'last_interaction': None,
            'shared_experiences': [],
            'mutual_connections': []
        }

        self.relationships[target_id] = relationship_data
        self._update_social_network(target_id, relationship_data)

        return {
            'success': True,
            'relationship': relationship_data
        }

    def interact(self,
                target_id: str,
                interaction_type: str,
                context: Dict) -> Dict:

        if not self._can_interact(target_id):
            return {'success': False, 'reason': 'Interaction not possible'}

        success_prob = self._calculate_interaction_success(
            target_id,
            interaction_type,
            context
        )

        outcome = self._determine_interaction_outcome(
            success_prob,
            interaction_type,
            context
        )

        self._update_relationship(target_id, outcome)

        self._record_interaction(target_id, interaction_type, outcome)

        return {
            'success': True,
            'outcome': outcome,
            'relationship_change': outcome['relationship_delta']
        }

    def _calculate_interaction_success(self,
                                    target_id: str,
                                    interaction_type: str,
                                    context: Dict) -> float:

        base_chance = 0.5

        if target_id in self.relationships:
            relationship = self.relationships[target_id]
            base_chance += relationship['strength'] * 0.2

        base_chance += (self.stats.charisma / 100) * 0.15

        if context.get('environment_friendly', True):
            base_chance += 0.1
        if context.get('previous_success', False):
            base_chance += 0.05

        return min(max(base_chance, 0.1), 0.9)

    def _update_relationship(self,
                           target_id: str,
                           interaction_outcome: Dict):

        if target_id not in self.relationships:
            return

        relationship = self.relationships[target_id]

        delta = interaction_outcome['relationship_delta']
        relationship['strength'] = max(min(
            relationship['strength'] + delta,
            1.0
        ), 0.0)

        trust_change = self._calculate_trust_change(
            interaction_outcome['success'],
            interaction_outcome['impact']
        )
        relationship['trust_level'] += trust_change

        relationship['interaction_count'] += 1

        self._check_relationship_evolution(target_id)

    def _calculate_trust_change(self,
                              success: bool,
                              impact: float) -> float:

        base_change = 0.05 if success else -0.05
        return base_change * impact

    def _check_relationship_evolution(self, target_id: str):

        relationship = self.relationships[target_id]

        if relationship['strength'] >= 0.8 and relationship['trust_level'] >= 0.7:
            if relationship['type'] != RelationType.ALLY:
                relationship['type'] = RelationType.ALLY
                self._notify_relationship_change(target_id, RelationType.ALLY)

        elif relationship['strength'] <= 0.2 and relationship['trust_level'] <= 0.3:
            if relationship['type'] != RelationType.RIVAL:
                relationship['type'] = RelationType.RIVAL
                self._notify_relationship_change(target_id, RelationType.RIVAL)