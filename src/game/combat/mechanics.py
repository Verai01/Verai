# src/game/combat/mechanics.py

from typing import Dict, List, Tuple
import numpy as np
from enum import Enum

class AttackType(Enum):
    LIGHT = "light"
    HEAVY = "heavy"
    SPECIAL = "special"    AERIAL = "aerial"
    EXECUTION = "execution"

class ComboPhase(Enum):
    STARTER = "starter"
    LINKER = "linker"
    ENDER = "ender"

class CombatMechanics:

    def __init__(self):
        self.combo_sequences = self._initialize_combo_sequences()
        self.aerial_moves = self._initialize_aerial_moves()
        self.execution_conditions = self._initialize_execution_conditions()

    def _initialize_combo_sequences(self) -> Dict:

        return {
            'basic': {
                'sequence': [
                    (AttackType.LIGHT, ComboPhase.STARTER),
                    (AttackType.LIGHT, ComboPhase.LINKER),
                    (AttackType.HEAVY, ComboPhase.ENDER)
                ],
                'damage_multiplier': 1.2,
                'stamina_cost': 25
            },
            'aerial': {
                'sequence': [
                    (AttackType.AERIAL, ComboPhase.STARTER),
                    (AttackType.LIGHT, ComboPhase.LINKER),
                    (AttackType.AERIAL, ComboPhase.ENDER)
                ],
                'damage_multiplier': 1.4,
                'stamina_cost': 35
            },
            'execution': {
                'sequence': [
                    (AttackType.HEAVY, ComboPhase.STARTER),
                    (AttackType.SPECIAL, ComboPhase.LINKER),
                    (AttackType.EXECUTION, ComboPhase.ENDER)
                ],
                'damage_multiplier': 1.8,
                'stamina_cost': 50
            }
        }

    def _initialize_aerial_moves(self) -> Dict:

        return {
            'air_dash': {
                'stamina_cost': 15,
                'damage_multiplier': 1.2,
                'height_requirement': 2.0,
                'momentum_factor': 1.5
            },
            'air_slam': {
                'stamina_cost': 25,
                'damage_multiplier': 1.6,
                'height_requirement': 4.0,
                'momentum_factor': 2.0
            },
            'aerial_execution': {
                'stamina_cost': 40,
                'damage_multiplier': 2.0,
                'height_requirement': 3.0,
                'momentum_factor': 2.5
            }
        }

    def calculate_combo_damage(self,
                             base_damage: float,
                             combo_sequence: List[AttackType],
                             execution_multiplier: float = 1.0) -> float:

        total_damage = 0
        combo_multiplier = 1.0

        for i, attack in enumerate(combo_sequence):

            combo_multiplier += 0.1 * i

            attack_damage = base_damage * combo_multiplier

            if attack == AttackType.HEAVY:
                attack_damage *= 1.5
            elif attack == AttackType.AERIAL:
                attack_damage *= 1.3
            elif attack == AttackType.EXECUTION:
                attack_damage *= execution_multiplier

            total_damage += attack_damage

        return total_damage

    def validate_aerial_move(self,
                           move_name: str,
                           player_height: float,
                           current_stamina: float) -> bool:

        if move_name not in self.aerial_moves:
            return False

        move = self.aerial_moves[move_name]

        if player_height < move['height_requirement']:
            return False

        if current_stamina < move['stamina_cost']:
            return False

        return True

    def calculate_execution_threshold(self,
                                   target_health_percentage: float,
                                   player_level: int,
                                   difficulty_modifier: float = 1.0) -> bool:

        base_threshold = 0.25  # 25% health
        level_bonus = 0.01 * player_level  # 1% per level

        final_threshold = (base_threshold + level_bonus) * difficulty_modifier

        return target_health_percentage <= final_threshold