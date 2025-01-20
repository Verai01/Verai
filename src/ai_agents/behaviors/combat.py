from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np

@dataclass
class CombatStats:
    health: float = 100.0
    stamina: float = 100.0
    strength: float = 10.0
    agility: float = 10.0
    defense: float = 10.0
    critical_chance: float = 0.05

class CombatSystem:
    def __init__(self, agent_stats: CombatStats):
        self.stats = agent_stats
        self.current_health = agent_stats.health
        self.current_stamina = agent_stats.stamina
        self.combat_history: List[Dict] = []
        self.learned_patterns: Dict = {}

    def evaluate_threat(self, opponent_stats: CombatStats) -> float:

        threat_score = (
            opponent_stats.strength * 1.5 +
            opponent_stats.agility * 1.2 +
            opponent_stats.defense * 1.0
        ) / self.stats.defense
        return min(max(threat_score, 0.0), 10.0)

    def choose_combat_action(self, 
                           opponent_stats: CombatStats,
                           distance: float,
                           environmental_factors: Dict) -> Dict:

        threat_level = self.evaluate_threat(opponent_stats)
        stamina_ratio = self.current_stamina / self.stats.stamina
        health_ratio = self.current_health / self.stats.health

        action_weights = {
            'attack': self._calculate_attack_weight(threat_level, stamina_ratio),
            'defend': self._calculate_defend_weight(threat_level, health_ratio),
            'retreat': self._calculate_retreat_weight(threat_level, health_ratio),
            'special': self._calculate_special_weight(stamina_ratio, distance)
        }

        chosen_action = max(action_weights.items(), key=lambda x: x[1])[0]
        return self._execute_action(chosen_action, opponent_stats, distance)

    def learn_from_combat(self, combat_result: Dict):

        self.combat_history.append(combat_result)
        if len(self.combat_history) > 100:
            self._update_learned_patterns()
            self.combat_history = self.combat_history[-50:]