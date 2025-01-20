# src/game/social/reputation.py

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid
from datetime import datetime
import logging
import numpy as np
class ReputationType(Enum):
    GENERAL = "general"           
    COMBAT = "combat"            
    TRADING = "trading"          
    DIPLOMATIC = "diplomatic"     
    SOCIAL = "social"            
    HONOR = "honor"            
    INFLUENCE = "influence"     
    EXPERTISE = "expertise"     

class ReputationTier(Enum):
    LEGENDARY = "legendary"      # 90-100
    RENOWNED = "renowned"        # 75-89
    RESPECTED = "respected"      # 60-74
    KNOWN = "known"             # 45-59
    NEUTRAL = "neutral"         # 30-44
    DUBIOUS = "dubious"         # 15-29
    INFAMOUS = "infamous"       # 0-14

@dataclass
class ReputationEvent:
    event_id: str
    timestamp: datetime
    actor_id: str
    target_id: str
    event_type: str
    reputation_change: float
    context: Dict
    witnesses: List[str]

class ReputationSystem:

    def __init__(self):
        self.reputations: Dict[str, Dict[ReputationType, float]] = {}
        self.reputation_history: Dict[str, List[ReputationEvent]] = {}
        self.faction_modifiers: Dict[str, Dict[str, float]] = {}
        self.event_weights: Dict[str, float] = self._initialize_event_weights()

    def create_reputation_profile(self, entity_id: str) -> Dict:

        try:
            if entity_id in self.reputations:
                return {'success': False, 'reason': 'Profile already exists'}

            reputation_values = {
                rep_type: 50.0  
                for rep_type in ReputationType
            }

            self.reputations[entity_id] = reputation_values
            self.reputation_history[entity_id] = []

            return {
                'success': True,
                'entity_id': entity_id,
                'reputation': reputation_values
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def record_event(self,
                    actor_id: str,
                    event_type: str,
                    context: Dict,
                    witnesses: List[str] = None) -> Dict:

        try:
            event_id = str(uuid.uuid4())
            timestamp = datetime.now()

            reputation_change = self._calculate_reputation_change(
                actor_id,
                event_type,
                context
            )

            event = ReputationEvent(
                event_id=event_id,
                timestamp=timestamp,
                actor_id=actor_id,
                target_id=context.get('target_id', ''),
                event_type=event_type,
                reputation_change=reputation_change,
                context=context,
                witnesses=witnesses or []
            )

            self._update_reputation(event)

            self.reputation_history[actor_id].append(event)

            return {
                'success': True,
                'event_id': event_id,
                'reputation_change': reputation_change
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def get_reputation(self,
                      entity_id: str,
                      reputation_type: Optional[ReputationType] = None) -> Dict:

        try:
            if entity_id not in self.reputations:
                return {'success': False, 'reason': 'Entity not found'}

            if reputation_type:
                value = self.reputations[entity_id][reputation_type]
                tier = self._get_reputation_tier(value)
                return {
                    'success': True,
                    'value': value,
                    'tier': tier,
                    'type': reputation_type
                }
            else:

                return {
                    'success': True,
                    'reputations': {
                        rep_type: {
                            'value': value,
                            'tier': self._get_reputation_tier(value)
                        }
                        for rep_type, value in self.reputations[entity_id].items()
                    }
                }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def modify_faction_relations(self,
                               faction_id: str,
                               entity_id: str,
                               modifier: float) -> Dict:

        try:
            if faction_id not in self.faction_modifiers:
                self.faction_modifiers[faction_id] = {}

            self.faction_modifiers[faction_id][entity_id] = modifier

            return {
                'success': True,
                'faction_id': faction_id,
                'entity_id': entity_id,
                'modifier': modifier
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def decay_reputation(self, delta_time: float) -> Dict:

        try:
            updates = []

            for entity_id in self.reputations:
                for rep_type in self.reputations[entity_id]:
                    old_value = self.reputations[entity_id][rep_type]

                    decay = self._calculate_decay(
                        old_value,
                        rep_type,
                        delta_time
                    )

                    new_value = max(0, min(100, old_value - decay))
                    self.reputations[entity_id][rep_type] = new_value

                    if abs(new_value - old_value) > 0.1:
                        updates.append({
                            'entity_id': entity_id,
                            'type': rep_type,
                            'old_value': old_value,
                            'new_value': new_value
                        })

            return {'success': True, 'updates': updates}

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _calculate_reputation_change(self,
                                   actor_id: str,
                                   event_type: str,
                                   context: Dict) -> float:

        base_change = self.event_weights.get(event_type, 0.0)

        context_modifier = self._get_context_modifier(context)

        faction_modifier = self._get_faction_modifier(
            actor_id,
            context.get('faction_id')
        )

        change = base_change * context_modifier * faction_modifier

        return max(-100, min(100, change))

    def _get_reputation_tier(self, value: float) -> ReputationTier:

        if value >= 90:
            return ReputationTier.LEGENDARY
        elif value >= 75:
            return ReputationTier.RENOWNED
        elif value >= 60:
            return ReputationTier.RESPECTED
        elif value >= 45:
            return ReputationTier.KNOWN
        elif value >= 30:
            return ReputationTier.NEUTRAL
        elif value >= 15:
            return ReputationTier.DUBIOUS
        else:
            return ReputationTier.INFAMOUS
