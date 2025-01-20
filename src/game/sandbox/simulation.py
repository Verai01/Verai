# src/game/sandbox/simulation.py

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
import uuid
from enum import Enum
import logging
from datetime import datetime

from ..ai_agents.core.agent_brain import AgentBrain
from ..game.combat.system import CombatSystem
from ..game.social.relationships import RelationshipSystem
from ..game.social.faction import FactionSystem
from ..game.world.environment import EnvironmentSystem
from ..game.world.physics import PhysicsSystem

class SimulationState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class SimulationStats:
    active_agents: int = 0
    total_interactions: int = 0
    combat_events: int = 0
    social_events: int = 0
    environmental_changes: int = 0
    simulation_time: float = 0.0
    performance_score: float = 0.0

class SandboxSimulation:

    def __init__(self, config: Optional[Dict] = None):
        self.simulation_id = str(uuid.uuid4())
        self.state = SimulationState.INITIALIZING
        self.stats = SimulationStats()
        self.config = config or self._default_config()

        self.environment = EnvironmentSystem()
        self.physics = PhysicsSystem()
        self.agents: Dict[str, AgentBrain] = {}
        self.combat_manager = self._initialize_combat_manager()
        self.social_manager = self._initialize_social_manager()
        self.faction_manager = self._initialize_faction_manager()

        self.current_time = 0.0
        self.time_scale = 1.0
        self.event_log: List[Dict] = []
        self.performance_metrics: Dict[str, float] = {}

        self._initialize_simulation()

    def update(self, delta_time: float) -> Dict:

        if self.state != SimulationState.RUNNING:
            return {'success': False, 'reason': f'Simulation not running: {self.state}'}

        scaled_delta = delta_time * self.time_scale
        updates = {
            'time': self.current_time,
            'events': [],
            'metrics': {}
        }

        try:

            self._pre_update(scaled_delta)

            env_updates = self.environment.update(scaled_delta)
            physics_updates = self.physics.update(scaled_delta)

            agent_updates = self._update_agents(scaled_delta)

            combat_updates = self._resolve_combat(scaled_delta)

            social_updates = self._update_social(scaled_delta)

            faction_updates = self._update_factions(scaled_delta)

            self._post_update(scaled_delta)

            updates['events'].extend(self._collect_events(
                env_updates,
                physics_updates,
                agent_updates,
                combat_updates,
                social_updates,
                faction_updates
            ))

            self._update_metrics(updates['metrics'])

            self.current_time += scaled_delta

        except Exception as e:
            logging.error(f"Simulation update error: {str(e)}")
            self.state = SimulationState.ERROR
            return {'success': False, 'reason': str(e)}

        return {'success': True, 'updates': updates}

    def add_agent(self,
                 agent_type: str,
                 initial_position: Tuple[float, float, float],
                 properties: Dict) -> Dict:

        agent_id = str(uuid.uuid4())

        agent = AgentBrain(agent_id=agent_id, properties=properties)

        combat_component = CombatSystem(agent_id=agent_id)
        social_component = RelationshipSystem(agent_id=agent_id)

        physics_properties = self._generate_physics_properties(agent_type)
        self.physics.add_object(agent_id, physics_properties, initial_position)

        self.agents[agent_id] = agent
        self.stats.active_agents += 1

        return {
            'success': True,
            'agent_id': agent_id,
            'agent_data': {
                'type': agent_type,
                'position': initial_position,
                'properties': properties
            }
        }

    def _update_agents(self, delta_time: float) -> List[Dict]:

        updates = []

        for agent_id, agent in self.agents.items():

            context = self._get_agent_context(agent_id)

            agent_update = agent.update(delta_time, context)

            self._process_agent_decisions(agent_id, agent_update)

            updates.append({
                'agent_id': agent_id,
                'update': agent_update
            })

        return updates

    def _resolve_combat(self, delta_time: float) -> List[Dict]:

        combat_events = []

        engagements = self._get_active_combat()

        for engagement in engagements:
            result = self.combat_manager.resolve_combat(
                engagement['attacker'],
                engagement['defender'],
                engagement['context']
            )

            self._apply_combat_results(result)
            combat_events.append(result)

        self.stats.combat_events += len(combat_events)
        return combat_events

    def _update_social(self, delta_time: float) -> List[Dict]:

        social_events = []

        interactions = self._get_pending_interactions()

        for interaction in interactions:
            result = self.social_manager.process_interaction(
                interaction['initiator'],
                interaction['target'],
                interaction['type'],
                interaction['context']
            )

            self._apply_social_results(result)
            social_events.append(result)

        self.stats.social_events += len(social_events)
        return social_events