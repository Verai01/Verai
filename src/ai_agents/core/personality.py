# src/ai_agents/core/personality.py

from enum import Enum
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import random

class PersonalityTrait(Enum):    AGGRESSION = "aggression"
    COOPERATION = "cooperation"
    CURIOSITY = "curiosity"
    LOYALTY = "loyalty"
    RISK_TAKING = "risk_taking"
    EMPATHY = "empathy"
    CREATIVITY = "creativity"
    DISCIPLINE = "discipline"
    CONFIDENCE = "confidence"
    ADAPTABILITY = "adaptability"

@dataclass
class PersonalityProfile:
    traits: Dict[PersonalityTrait, float]
    dominant_traits: List[PersonalityTrait]
    personality_type: str
    behavior_weights: Dict[str, float]

class PersonalitySystem:

    def __init__(self):
        self.trait_ranges = {trait: (0.0, 1.0) for trait in PersonalityTrait}
        self.personality_types = self._load_personality_types()
        self.behavior_patterns = self._load_behavior_patterns()

    def generate_personality(self, base_type: str = None) -> PersonalityProfile:

        traits = {}

        if base_type and base_type in self.personality_types:

            base_traits = self.personality_types[base_type]
            for trait in PersonalityTrait:
                base_value = base_traits.get(trait.value, 0.5)
                variation = random.uniform(-0.1, 0.1)
                traits[trait] = max(0.0, min(1.0, base_value + variation))
        else:

            for trait in PersonalityTrait:
                traits[trait] = random.uniform(
                    self.trait_ranges[trait][0],
                    self.trait_ranges[trait][1]
                )

        dominant_traits = self._determine_dominant_traits(traits)

        personality_type = self._determine_personality_type(traits)

        behavior_weights = self._calculate_behavior_weights(traits)

        return PersonalityProfile(
            traits=traits,
            dominant_traits=dominant_traits,
            personality_type=personality_type,
            behavior_weights=behavior_weights
        )

    def modify_trait(self,
                    profile: PersonalityProfile,
                    trait: PersonalityTrait,
                    amount: float) -> PersonalityProfile:

        current_value = profile.traits[trait]
        new_value = max(0.0, min(1.0, current_value + amount))

        profile.traits[trait] = new_value

        profile.dominant_traits = self._determine_dominant_traits(profile.traits)
        profile.personality_type = self._determine_personality_type(profile.traits)
        profile.behavior_weights = self._calculate_behavior_weights(profile.traits)

        return profile

    def calculate_decision_weights(self,
                                 profile: PersonalityProfile,
                                 context: Dict) -> Dict[str, float]:

        weights = {}

        for action, base_weight in context.get('possible_actions', {}).items():
            weight = base_weight

            for trait, value in profile.traits.items():
                modifier = self._get_trait_action_modifier(trait, action)
                weight *= (1 + modifier * value)

            context_modifier = self._get_context_modifier(action, context)
            weight *= context_modifier

            weights[action] = max(0.0, min(1.0, weight))

        return weights