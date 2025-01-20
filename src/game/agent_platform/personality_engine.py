# src/game/agent_platform/personality_engine.py

from typing import Dict, List, Optional, Tuple
import numpy as np
from enum import Enum
import json

class PersonalityTrait(Enum):
    AGGRESSION = "aggression"
    COURAGE = "courage"    WISDOM = "wisdom"
    CHARISMA = "charisma"
    LOYALTY = "loyalty"
    CREATIVITY = "creativity"
    DISCIPLINE = "discipline"
    EMPATHY = "empathy"

class SuperPower(Enum):
    TELEKINESIS = "telekinesis"
    SUPER_SPEED = "super_speed"
    ENERGY_BLAST = "energy_blast"
    HEALING = "healing"
    TIME_CONTROL = "time_control"
    SHAPE_SHIFTING = "shape_shifting"

class PersonalityEngine:

    def __init__(self):

        self.trait_definitions = self._load_trait_definitions()
        self.power_definitions = self._load_power_definitions()
        self.personality_templates = self._load_personality_templates()

    def _load_trait_definitions(self) -> Dict:

        return {
            PersonalityTrait.AGGRESSION: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'Tendency towards aggressive behavior'
            },
            PersonalityTrait.COURAGE: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.6,
                'description': 'Bravery and willingness to face danger'
            },
            PersonalityTrait.WISDOM: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'Decision making and knowledge application'
            },
            PersonalityTrait.CHARISMA: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'Social influence and leadership'
            },
            PersonalityTrait.LOYALTY: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.7,
                'description': 'Faithfulness to allies and causes'
            },
            PersonalityTrait.CREATIVITY: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'Ability to think outside the box'
            },
            PersonalityTrait.DISCIPLINE: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'Self-control and organization'
            },
            PersonalityTrait.EMPATHY: {
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': 'Understanding and sharing feelings'
            }
        }

    def _load_power_definitions(self) -> Dict:

        return {
            SuperPower.TELEKINESIS: {
                'energy_cost': 10,
                'cooldown': 5,
                'range': 20,
                'description': 'Move objects with mind power',
                'effectiveness': 0.75
            },
            SuperPower.SUPER_SPEED: {
                'energy_cost': 15,
                'cooldown': 3,
                'range': 50,
                'description': 'Move at superhuman speeds',
                'effectiveness': 0.8
            },
            SuperPower.ENERGY_BLAST: {
                'energy_cost': 25,
                'cooldown': 8,
                'range': 30,
                'description': 'Release powerful energy blasts',
                'effectiveness': 0.9
            },
            SuperPower.HEALING: {
                'energy_cost': 20,
                'cooldown': 10,
                'range': 5,
                'description': 'Heal self or allies',
                'effectiveness': 0.85
            },
            SuperPower.TIME_CONTROL: {
                'energy_cost': 50,
                'cooldown': 30,
                'range': 15,
                'description': 'Manipulate the flow of time',
                'effectiveness': 1.0
            },
            SuperPower.SHAPE_SHIFTING: {
                'energy_cost': 30,
                'cooldown': 15,
                'range': 0,
                'description': 'Transform into different forms',
                'effectiveness': 0.7
            }
        }

    def _load_personality_templates(self) -> Dict:

        return {
            'hero': {
                PersonalityTrait.COURAGE: 0.8,
                PersonalityTrait.WISDOM: 0.7,
                PersonalityTrait.LOYALTY: 0.9,
                PersonalityTrait.CHARISMA: 0.6,
                PersonalityTrait.AGGRESSION: 0.4,
                PersonalityTrait.CREATIVITY: 0.6,
                PersonalityTrait.DISCIPLINE: 0.7,
                PersonalityTrait.EMPATHY: 0.8
            },
            'antihero': {
                PersonalityTrait.COURAGE: 0.7,
                PersonalityTrait.WISDOM: 0.6,
                PersonalityTrait.LOYALTY: 0.5,
                PersonalityTrait.CHARISMA: 0.7,
                PersonalityTrait.AGGRESSION: 0.6,
                PersonalityTrait.CREATIVITY: 0.8,
                PersonalityTrait.DISCIPLINE: 0.5,
                PersonalityTrait.EMPATHY: 0.4
            },
            'mentor': {
                PersonalityTrait.COURAGE: 0.6,
                PersonalityTrait.WISDOM: 0.9,
                PersonalityTrait.LOYALTY: 0.8,
                PersonalityTrait.CHARISMA: 0.7,
                PersonalityTrait.AGGRESSION: 0.3,
                PersonalityTrait.CREATIVITY: 0.7,
                PersonalityTrait.DISCIPLINE: 0.8,
                PersonalityTrait.EMPATHY: 0.9
            }
        }

    def _configure_powers(self, powers: List[SuperPower], personality: Dict) -> Dict:

        power_config = {}
        for power in powers:
            if power in self.power_definitions:
                base_power = self.power_definitions[power].copy()

                effectiveness_mod = self._calculate_power_effectiveness(power, personality)
                base_power['effectiveness'] *= effectiveness_mod

                energy_mod = self._calculate_energy_modifier(power, personality)
                base_power['energy_cost'] = max(1, int(base_power['energy_cost'] * energy_mod))

                power_config[power] = base_power

        return power_config

    def _calculate_power_influence(self, powers: List[SuperPower]) -> Dict[str, float]:

        influence = {
            'combat': 0.0,
            'social': 0.0,
            'mobility': 0.0,
            'utility': 0.0
        }

        for power in powers:
            if power in self.power_definitions:
                power_data = self.power_definitions[power]

                if power in [SuperPower.ENERGY_BLAST, SuperPower.TELEKINESIS]:
                    influence['combat'] += power_data['effectiveness'] * 0.8
                elif power in [SuperPower.HEALING, SuperPower.TIME_CONTROL]:
                    influence['utility'] += power_data['effectiveness'] * 0.7
                elif power in [SuperPower.SUPER_SPEED]:
                    influence['mobility'] += power_data['effectiveness'] * 0.9
                elif power in [SuperPower.SHAPE_SHIFTING]:
                    influence['social'] += power_data['effectiveness'] * 0.6

        max_value = max(influence.values())
        if max_value > 0:
            influence = {k: v/max_value for k, v in influence.items()}

        return influence

    def _analyze_behavior_tendencies(self, traits: Dict[PersonalityTrait, float]) -> Dict[str, float]:

        tendencies = {
            'aggressive': traits.get(PersonalityTrait.AGGRESSION, 0.5),
            'cautious': traits.get(PersonalityTrait.WISDOM, 0.5),
            'social': traits.get(PersonalityTrait.CHARISMA, 0.5),
            'loyal': traits.get(PersonalityTrait.LOYALTY, 0.5),
            'creative': traits.get(PersonalityTrait.CREATIVITY, 0.5),
            'disciplined': traits.get(PersonalityTrait.DISCIPLINE, 0.5),
            'empathetic': traits.get(PersonalityTrait.EMPATHY, 0.5)
        }

        tendencies['risk_taking'] = (tendencies['aggressive'] * 0.7 + 
                                   (1 - tendencies['cautious']) * 0.3)
        tendencies['leadership'] = (tendencies['social'] * 0.6 + 
                                  tendencies['disciplined'] * 0.4)

        return tendencies

    def _configure_behavior_patterns(self, personality: Dict) -> Dict[str, float]:

        core_traits = personality.get('core_traits', {})
        tendencies = personality.get('behavior_tendencies', {})

        patterns = {
            'combat': self._calculate_combat_tendency(core_traits, tendencies),
            'exploration': self._calculate_exploration_tendency(core_traits, tendencies),
            'social': self._calculate_social_tendency(core_traits, tendencies),
            'trading': self._calculate_trading_tendency(core_traits, tendencies),
            'learning': self._calculate_learning_tendency(core_traits, tendencies)
        }

        return patterns

    def _calculate_combat_tendency(self, traits: Dict, tendencies: Dict) -> float:

        return (traits.get(PersonalityTrait.AGGRESSION, 0.5) * 0.4 +
                traits.get(PersonalityTrait.COURAGE, 0.5) * 0.3 +
                tendencies.get('risk_taking', 0.5) * 0.3)

    def _calculate_exploration_tendency(self, traits: Dict, tendencies: Dict) -> float:

        return (traits.get(PersonalityTrait.CREATIVITY, 0.5) * 0.4 +
                traits.get(PersonalityTrait.COURAGE, 0.5) * 0.3 +
                (1 - traits.get(PersonalityTrait.DISCIPLINE, 0.5)) * 0.3)

    def _calculate_social_tendency(self, traits: Dict, tendencies: Dict) -> float:

        return (traits.get(PersonalityTrait.CHARISMA, 0.5) * 0.4 +
                traits.get(PersonalityTrait.EMPATHY, 0.5) * 0.3 +
                tendencies.get('social', 0.5) * 0.3)

    def _calculate_trading_tendency(self, traits: Dict, tendencies: Dict) -> float:

        return (traits.get(PersonalityTrait.WISDOM, 0.5) * 0.4 +
                traits.get(PersonalityTrait.CHARISMA, 0.5) * 0.3 +
                (1 - traits.get(PersonalityTrait.AGGRESSION, 0.5)) * 0.3)

    def _calculate_learning_tendency(self, traits: Dict, tendencies: Dict) -> float:

        return (traits.get(PersonalityTrait.WISDOM, 0.5) * 0.4 +
                traits.get(PersonalityTrait.DISCIPLINE, 0.5) * 0.3 +
                traits.get(PersonalityTrait.CREATIVITY, 0.5) * 0.3)

    def _calculate_power_effectiveness(self, power: SuperPower, personality: Dict) -> float:

        core_traits = personality.get('core_traits', {})
        base_effectiveness = 1.0

        if power == SuperPower.TELEKINESIS:
            base_effectiveness += (core_traits.get(PersonalityTrait.DISCIPLINE, 0.5) - 0.5)
        elif power == SuperPower.ENERGY_BLAST:
            base_effectiveness += (core_traits.get(PersonalityTrait.AGGRESSION, 0.5) - 0.5)
        elif power == SuperPower.HEALING:
            base_effectiveness += (core_traits.get(PersonalityTrait.EMPATHY, 0.5) - 0.5)
        elif power == SuperPower.TIME_CONTROL:
            base_effectiveness += (core_traits.get(PersonalityTrait.WISDOM, 0.5) - 0.5)

        return max(0.5, min(1.5, base_effectiveness))

    def _calculate_energy_modifier(self, power: SuperPower, personality: Dict) -> float:

        core_traits = personality.get('core_traits', {})
        base_modifier = 1.0

        discipline = core_traits.get(PersonalityTrait.DISCIPLINE, 0.5)
        base_modifier -= (discipline - 0.5) * 0.3

        aggression = core_traits.get(PersonalityTrait.AGGRESSION, 0.5)
        base_modifier += (aggression - 0.5) * 0.2

        return max(0.7, min(1.3, base_modifier))

    def create_personality(self,
                         base_traits: Dict[PersonalityTrait, float],
                         special_powers: List[SuperPower],
                         additional_config: Optional[Dict] = None) -> Dict:

        try:

            if not self._validate_traits(base_traits):
                return {'success': False, 'reason': 'Invalid trait values'}

            personality = {
                'core_traits': base_traits,
                'power_influence': self._calculate_power_influence(special_powers),
                'behavior_tendencies': self._analyze_behavior_tendencies(base_traits)
            }

            behavior_patterns = self._configure_behavior_patterns(personality)

            power_config = self._configure_powers(special_powers, personality)

            return {
                'success': True,
                'personality': personality,
                'behavior_patterns': behavior_patterns,
                'power_config': power_config
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _validate_traits(self, traits: Dict[PersonalityTrait, float]) -> bool:

        try:
            for trait, value in traits.items():
                if trait not in self.trait_definitions:
                    return False

                trait_def = self.trait_definitions[trait]
                if not (trait_def['min'] <= value <= trait_def['max']):
                    return False

            return True

        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False