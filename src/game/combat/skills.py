# src/game/combat/skills.py

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid
import math
import random

class SkillType(Enum):    ATTACK = "attack"           
    DEFENSE = "defense"         
    SUPPORT = "support"         
    CONTROL = "control"        
    MOVEMENT = "movement"      
    SPECIAL = "special"       
    ULTIMATE = "ultimate"      

class SkillEffect(Enum):
    DAMAGE = "damage"
    HEAL = "heal"
    SHIELD = "shield"
    BUFF = "buff"
    DEBUFF = "debuff"
    STUN = "stun"
    KNOCKBACK = "knockback"
    TELEPORT = "teleport"
    DRAIN = "drain"
    TRANSFORM = "transform"

@dataclass
class SkillData:
    id: str
    name: str
    type: SkillType
    level: int
    base_power: float
    energy_cost: float
    cooldown: float
    range: float
    area_of_effect: float
    effects: List[Dict]
    requirements: Dict

class SkillSystem:

    def __init__(self):
        self.skills: Dict[str, SkillData] = {}
        self.skill_combinations: Dict[str, List[str]] = {}
        self.evolution_paths: Dict[str, Dict] = {}

    def create_skill(self, skill_config: Dict) -> Dict:

        try:
            skill_id = str(uuid.uuid4())

            validation = self._validate_skill_config(skill_config)
            if not validation['valid']:
                return {'success': False, 'reason': validation['reason']}

            skill = SkillData(
                id=skill_id,
                name=skill_config['name'],
                type=SkillType(skill_config['type']),
                level=1,
                base_power=skill_config['base_power'],
                energy_cost=skill_config['energy_cost'],
                cooldown=skill_config['cooldown'],
                range=skill_config['range'],
                area_of_effect=skill_config.get('area_of_effect', 0),
                effects=skill_config['effects'],
                requirements=skill_config.get('requirements', {})
            )

            self.skills[skill_id] = skill

            return {
                'success': True,
                'skill_id': skill_id,
                'skill': skill
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def calculate_skill_effects(self,
                              skill_id: str,
                              caster_stats: Dict,
                              target_stats: Dict,
                              environment: Dict) -> Dict:

        try:
            skill = self.skills.get(skill_id)
            if not skill:
                return {'success': False, 'reason': 'Skill not found'}

            effects = []

            for effect in skill.effects:

                base_value = self._calculate_base_effect(
                    effect,
                    skill,
                    caster_stats
                )

                modified_value = self._apply_modifiers(
                    base_value,
                    effect,
                    caster_stats,
                    target_stats,
                    environment
                )

                effects.append({
                    'type': effect['type'],
                    'value': modified_value,
                    'duration': effect.get('duration', 0),
                    'conditions': effect.get('conditions', [])
                })

            return {
                'success': True,
                'effects': effects,
                'energy_cost': self._calculate_energy_cost(skill, caster_stats)
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def evolve_skill(self,
                    skill_id: str,
                    evolution_path: str,
                    resources: Dict) -> Dict:

        try:
            skill = self.skills.get(skill_id)
            if not skill:
                return {'success': False, 'reason': 'Skill not found'}

            if not self._check_evolution_requirements(skill, evolution_path, resources):
                return {'success': False, 'reason': 'Evolution requirements not met'}

            evolved_skill = self._perform_evolution(skill, evolution_path)

            self.skills[skill_id] = evolved_skill

            return {
                'success': True,
                'skill_id': skill_id,
                'evolved_skill': evolved_skill
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def combine_skills(self,
                      skill_ids: List[str],
                      combination_type: str) -> Dict:

        try:

            skills = [self.skills.get(skill_id) for skill_id in skill_ids]
            if None in skills:
                return {'success': False, 'reason': 'One or more skills not found'}

            if not self._validate_combination(skills, combination_type):
                return {'success': False, 'reason': 'Invalid combination'}

            combined_skill = self._create_combined_skill(
                skills,
                combination_type
            )

            return {
                'success': True,
                'new_skill': combined_skill
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _calculate_base_effect(self,
                             effect: Dict,
                             skill: SkillData,
                             caster_stats: Dict) -> float:

        base_value = effect['base_value'] * skill.base_power

        for stat, scaling in effect.get('scaling', {}).items():
            if stat in caster_stats:
                base_value += caster_stats[stat] * scaling

        return base_value
