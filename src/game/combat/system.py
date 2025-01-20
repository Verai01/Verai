# src/game/combat/system.py

from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import uuid

class CombatStyle(Enum):
    AGGRESSIVE = "aggressive"    DEFENSIVE = "defensive"
    TACTICAL = "tactical"
    AERIAL = "aerial"
    BALANCED = "balanced"

@dataclass
class CombatStats:
    health: float = 100.0
    stamina: float = 100.0
    strength: float = 10.0
    agility: float = 10.0
    defense: float = 10.0
    critical_chance: float = 0.05
    combo_multiplier: float = 1.0
    aerial_bonus: float = 0.0

class CombatSystem:

    def __init__(self, 
                 agent_id: str,
                 initial_stats: CombatStats,
                 preferred_style: CombatStyle = CombatStyle.BALANCED):
        self.agent_id = agent_id
        self.stats = initial_stats
        self.preferred_style = preferred_style
        self.current_targets: List[str] = []
        self.combo_counter: int = 0
        self.aerial_state: bool = False
        self.current_stance: CombatStyle = preferred_style
        self.combat_history: List[Dict] = []

        self.damage_dealt: float = 0
        self.damage_received: float = 0
        self.successful_combos: int = 0
        self.aerial_hits: int = 0
        self.perfect_blocks: int = 0

        self.state = {
            'in_combat': False,
            'executing_combo': False,
            'can_aerial': True,
            'stamina_regenerating': True,
            'vulnerable': False
        }

    def initiate_combat(self, targets: List[str]) -> Dict:

        self.current_targets = targets
        self.state['in_combat'] = True
        return self._prepare_combat_engagement()

    def execute_attack(self, 
                      target_id: str,
                      attack_type: str,
                      position: Tuple[float, float, float],
                      context: Dict) -> Dict:

        if not self._validate_attack(target_id, attack_type, context):
            return {'success': False, 'reason': 'Invalid attack parameters'}

        damage, effects = self._calculate_attack_impact(
            attack_type,
            position,
            context
        )

        if self.state['executing_combo']:
            damage *= self.stats.combo_multiplier
            self.combo_counter += 1

        if self.aerial_state:
            damage *= (1 + self.stats.aerial_bonus)
            self.aerial_hits += 1

        self.damage_dealt += damage

        return {
            'success': True,
            'damage': damage,
            'effects': effects,
            'combo': self.combo_counter,
            'position': position
        }

    def defend(self, 
              attack_vector: Dict,
              reaction_time: float) -> Dict:

        if reaction_time < 0.2:  # Perfect block timing
            self.perfect_blocks += 1
            damage_reduction = 0.9
            counter_opportunity = True
        else:
            damage_reduction = 0.5
            counter_opportunity = False

        mitigated_damage = attack_vector['damage'] * (1 - damage_reduction)
        self.damage_received += mitigated_damage

        return {
            'success': True,
            'damage_mitigated': attack_vector['damage'] - mitigated_damage,
            'perfect_block': reaction_time < 0.2,
            'counter_available': counter_opportunity
        }

    def execute_aerial_maneuver(self, 
                              maneuver_type: str,
                              position: Tuple[float, float, float],
                              velocity: Tuple[float, float, float]) -> Dict:

        if not self.state['can_aerial']:
            return {'success': False, 'reason': 'Aerial maneuver not available'}

        stamina_cost = self._calculate_aerial_stamina_cost(maneuver_type)
        if self.stats.stamina < stamina_cost:
            return {'success': False, 'reason': 'Insufficient stamina'}

        self.stats.stamina -= stamina_cost
        self.aerial_state = True

        effects = self._calculate_aerial_effects(
            maneuver_type,
            position,
            velocity
        )

        return {
            'success': True,
            'maneuver': maneuver_type,
            'effects': effects,
            'position': position,
            'velocity': velocity
        }

    def _calculate_attack_impact(self,
                               attack_type: str,
                               position: Tuple[float, float, float],
                               context: Dict) -> Tuple[float, List[str]]:

        base_damage = self.stats.strength * 0.5

        multipliers = {
            'light': 0.7,
            'heavy': 1.3,
            'special': 1.5,
            'execution': 2.0
        }

        damage = base_damage * multipliers.get(attack_type, 1.0)

        if np.random.random() < self.stats.critical_chance:
            damage *= 2
            effects = ['critical']
        else:
            effects = []

        distance = np.linalg.norm(position)
        if distance > 5.0:  # Long-range attack
            damage *= 0.8

        return damage, effects