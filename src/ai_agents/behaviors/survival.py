from typing import Dict, List, Tuple
import numpy as np

class SurvivalBehavior:
    def __init__(self, initial_resources: Dict[str, float] = None):
        self.resources = initial_resources or {
            'health': 100.0,
            'energy': 100.0,
            'food': 50.0,
            'water': 50.0        }
        self.survival_priorities = self._initialize_priorities()
        self.risk_threshold = 0.3
        self.resource_history: List[Dict] = []

    def _initialize_priorities(self) -> Dict[str, float]:
        return {
            'immediate_threat': 1.0,
            'critical_resource': 0.8,
            'resource_gathering': 0.6,
            'shelter_seeking': 0.4,
            'exploration': 0.2
        }

    def assess_situation(self, 
                        environment_state: Dict,
                        nearby_threats: List[Dict]) -> Dict[str, float]:

        threat_level = self._calculate_threat_level(nearby_threats)
        resource_status = self._evaluate_resources()
        environmental_danger = self._assess_environmental_danger(environment_state)

        return {
            'threat_level': threat_level,
            'resource_status': resource_status,
            'environmental_danger': environmental_danger,
            'overall_risk': (threat_level + environmental_danger) / 2
        }

    def decide_survival_action(self, 
                             situation_assessment: Dict,
                             available_actions: List[str]) -> Tuple[str, Dict]:

        if situation_assessment['threat_level'] > self.risk_threshold:
            return self._handle_threat_situation(situation_assessment)

        if situation_assessment['resource_status'] < 0.3:
            return self._handle_resource_crisis(situation_assessment)

        return self._normal_survival_behavior(situation_assessment)