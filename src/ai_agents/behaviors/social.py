from enum import Enum
from typing import Dict, List, Optional
import numpy as np

class SocialAction(Enum):
    COOPERATE = "cooperate"
    TRADE = "trade"
    SHARE_INFO = "share_info"
    FORM_ALLIANCE = "form_alliance"
    BETRAY = "betray"    DEFEND_ALLY = "defend_ally"

class SocialBehavior:
    def __init__(self, personality_traits: Dict[str, float]):
        self.personality = personality_traits
        self.relationships: Dict[str, float] = {}
        self.trust_levels: Dict[str, float] = {}
        self.alliance_history: List[Dict] = []
        self.interaction_memory: Dict[str, List] = {}

    def evaluate_interaction(self, 
                           other_agent_id: str, 
                           interaction_type: str,
                           context: Dict) -> float:

        trust = self.trust_levels.get(other_agent_id, 0.5)
        relationship = self.relationships.get(other_agent_id, 0.0)

        base_score = (trust * 0.6 + relationship * 0.4) * self.personality['COOPERATION']

        if context.get('under_attack', False):
            base_score *= (1 + self.personality['LOYALTY'])
        if context.get('resource_scarcity', False):
            base_score *= (1 - self.personality['RISK_TAKING'] * 0.5)

        return base_score

    def decide_social_action(self, 
                           other_agent_id: str,
                           situation: Dict) -> SocialAction:

        interaction_score = self.evaluate_interaction(
            other_agent_id,
            situation.get('interaction_type'),
            situation
        )

        if interaction_score > 0.8:
            return SocialAction.FORM_ALLIANCE
        elif interaction_score > 0.6:
            return SocialAction.COOPERATE
        elif interaction_score > 0.4:
            return SocialAction.TRADE
        elif interaction_score > 0.2:
            return SocialAction.SHARE_INFO
        else:
            return SocialAction.BETRAY