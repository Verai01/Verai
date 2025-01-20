# src/game/world/environment.py

from typing import Dict, List, Optional, Tuple, Set
import numpy as np
from enum import Enum
from dataclasses import dataclass
import uuid

class BiomeType(Enum):
    DOJO = "dojo"    ARENA = "arena"
    WILDERNESS = "wilderness"
    SETTLEMENT = "settlement"
    SACRED_GROUNDS = "sacred_grounds"
    CORRUPTED = "corrupted"

class WeatherEffect(Enum):
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"
    MYSTIC_AURA = "mystic_aura"
    CORRUPTED_MIST = "corrupted_mist"

@dataclass
class EnvironmentStats:
    size: Tuple[float, float, float]
    population_capacity: int
    resource_richness: float
    danger_level: float
    stability: float
    magic_potency: float

class EnvironmentSystem:

    def __init__(self,
                 environment_id: Optional[str] = None,
                 biome_type: BiomeType = BiomeType.ARENA,
                 initial_stats: Optional[EnvironmentStats] = None):
        self.environment_id = environment_id or str(uuid.uuid4())
        self.biome_type = biome_type
        self.stats = initial_stats or self._generate_default_stats()

        self.current_weather = WeatherEffect.CLEAR
        self.active_effects: List[Dict] = []
        self.dynamic_objects: Dict[str, Dict] = {}
        self.static_objects: Dict[str, Dict] = {}

        self.resources: Dict[str, float] = {}
        self.resource_nodes: Dict[str, Dict] = {}
        self.resource_regeneration_rates: Dict[str, float] = {}

        self.stability_factors: Dict[str, float] = {}
        self.threat_levels: Dict[str, float] = {}
        self.population_distribution: Dict[str, int] = {}

        self._initialize_environment()

    def _generate_default_stats(self) -> EnvironmentStats:

        base_stats = {
            BiomeType.DOJO: EnvironmentStats(
                size=(100.0, 100.0, 30.0),
                population_capacity=50,
                resource_richness=0.5,
                danger_level=0.2,
                stability=0.9,
                magic_potency=0.7
            ),
            BiomeType.ARENA: EnvironmentStats(
                size=(200.0, 200.0, 50.0),
                population_capacity=100,
                resource_richness=0.3,
                danger_level=0.8,
                stability=0.7,
                magic_potency=0.5
            ),

        }
        return base_stats.get(self.biome_type, EnvironmentStats(
            size=(150.0, 150.0, 40.0),
            population_capacity=75,
            resource_richness=0.4,
            danger_level=0.5,
            stability=0.8,
            magic_potency=0.6
        ))

    def update_environment(self, delta_time: float) -> Dict:

        updates = {
            'weather_changed': False,
            'effects_added': [],
            'effects_removed': [],
            'resource_updates': {}
        }

        if self._should_update_weather():
            new_weather = self._calculate_next_weather()
            if new_weather != self.current_weather:
                updates['weather_changed'] = True
                self.current_weather = new_weather

        self._update_active_effects(delta_time, updates)

        self._update_resources(delta_time, updates)

        self._update_stability(delta_time)

        return updates

    def add_dynamic_object(self,
                          object_id: str,
                          object_type: str,
                          position: Tuple[float, float, float],
                          properties: Dict) -> Dict:

        if object_id in self.dynamic_objects:
            return {'success': False, 'reason': 'Object already exists'}

        object_data = {
            'type': object_type,
            'position': position,
            'properties': properties,
            'state': 'active',
            'affected_by_weather': properties.get('weather_affected', True),
            'affects_stability': properties.get('stability_impact', 0.0)
        }

        self.dynamic_objects[object_id] = object_data
        self._update_stability_factors()

        return {
            'success': True,
            'object_data': object_data
        }

    def apply_weather_effect(self,
                           effect: WeatherEffect,
                           duration: float,
                           intensity: float = 1.0) -> Dict:

        if effect == self.current_weather:
            return {'success': False, 'reason': 'Effect already active'}

        previous_weather = self.current_weather
        self.current_weather = effect

        impact_data = self._calculate_weather_impacts(effect, intensity)

        self._apply_weather_effects(impact_data)

        return {
            'success': True,
            'previous_weather': previous_weather,
            'impact_data': impact_data,
            'duration': duration
        }

    def _update_active_effects(self,
                             delta_time: float,
                             updates: Dict):

        for effect in self.active_effects[:]:  # Copy list for safe removal
            effect['duration'] -= delta_time

            if effect['duration'] <= 0:
                self.active_effects.remove(effect)
                updates['effects_removed'].append(effect['type'])
                continue

            self._apply_effect_impacts(effect, delta_time)

    def _calculate_weather_impacts(self,
                                 weather: WeatherEffect,
                                 intensity: float) -> Dict:

        impacts = {
            'visibility': 1.0,
            'movement_speed': 1.0,
            'resource_generation': 1.0,
            'magic_potency': 1.0,
            'stability': 0.0
        }

        if weather == WeatherEffect.RAIN:
            impacts.update({
                'visibility': 0.7 * intensity,
                'movement_speed': 0.8 * intensity,
                'resource_generation': 1.2 * intensity
            })
        elif weather == WeatherEffect.STORM:
            impacts.update({
                'visibility': 0.4 * intensity,
                'movement_speed': 0.6 * intensity,
                'stability': -0.2 * intensity,
                'magic_potency': 1.3 * intensity
            })
        elif weather == WeatherEffect.MYSTIC_AURA:
            impacts.update({
                'magic_potency': 1.5 * intensity,
                'resource_generation': 1.3 * intensity,
                'stability': 0.1 * intensity
            })

        return impacts