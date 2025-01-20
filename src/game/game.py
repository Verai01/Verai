# src/game/game.py

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import logging
from enum import Enum

from .world.environment import EnvironmentSystem
from .world.physics import PhysicsSystemfrom .world.interaction import InteractionSystem
from .social.relationships import RelationshipSystem
from .social.faction import FactionSystem
from .combat.system import CombatSystem
from .ai_agents.core.agent_brain import AgentBrain
from .sandbox.simulation import SandboxSimulation
from .sandbox.controller import SandboxController
from .agent_platform.creator import AgentCreator
from .agent_platform.sharing import AgentSharing
from .agent_platform.avatar_system import AvatarSystem
from .agent_platform.personality_engine import PersonalityEngine

class GameState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class Game:

    def __init__(self, config: Optional[Dict] = None):
        self.game_id = str(uuid.uuid4())
        self.state = GameState.INITIALIZING
        self.start_time = datetime.now()
        self.config = config or self._default_config()

        self.players = []
        self.ai_agents = []

        self.environment = EnvironmentSystem()
        self.physics = PhysicsSystem()
        self.interaction = InteractionSystem()

        self.relationships = RelationshipSystem()
        self.factions = FactionSystem()

        self.combat = CombatSystem()

        self.simulation = SandboxSimulation()
        self.controller = SandboxController(self.simulation)

        self.agent_creator = AgentCreator()
        self.agent_sharing = AgentSharing()
        self.avatar_system = AvatarSystem()
        self.personality_engine = PersonalityEngine()

        self.current_time = 0.0
        self.time_scale = 1.0
        self.performance_metrics: Dict[str, float] = {}
        self.event_log: List[Dict] = []

        self._initialize_game()

    def update(self, delta_time: float) -> Dict:

        if self.state != GameState.RUNNING:
            return {'success': False, 'reason': f'Game not running: {self.state}'}

        try:
            scaled_delta = delta_time * self.time_scale
            updates = {
                'time': self.current_time,
                'events': [],
                'metrics': {}
            }

            self._update_core_systems(scaled_delta, updates)

            self._update_social_systems(scaled_delta, updates)

            combat_updates = self.combat.update(scaled_delta)
            updates['events'].extend(combat_updates.get('events', []))

            sim_updates = self.simulation.update(scaled_delta)
            updates['events'].extend(sim_updates.get('events', []))

            self._update_performance_metrics(updates['metrics'])

            self.current_time += scaled_delta
            return {'success': True, 'updates': updates}

        except Exception as e:
            logging.error(f"Game update error: {str(e)}")
            self.state = GameState.ERROR
            return {'success': False, 'reason': str(e)}

    def add_player(self, player_data: Dict) -> Dict:

        try:
            player_id = str(uuid.uuid4())

            player = {
                'id': player_id,
                'data': player_data,
                'joined_at': datetime.now(),
                'agents': [],
                'state': 'active'
            }

            self.players.append(player)

            return {
                'success': True,
                'player_id': player_id,
                'player': player
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def add_ai_agent(self, agent_config: Dict) -> Dict:

        try:

            agent_result = self.agent_creator.create_agent(agent_config)

            if not agent_result['success']:
                return agent_result

            agent_id = agent_result['agent_id']

            avatar_result = self.avatar_system.create_avatar(
                agent_result['config'],
                agent_config.get('style_preferences', {})
            )

            personality_result = self.personality_engine.create_personality(
                agent_config.get('base_traits', {}),
                agent_config.get('special_powers', [])
            )

            self.ai_agents.append({
                'id': agent_id,
                'config': agent_result['config'],
                'avatar': avatar_result.get('avatar'),
                'personality': personality_result.get('personality'),
                'state': 'active'
            })

            return {
                'success': True,
                'agent_id': agent_id,
                'agent_data': agent_result['config']
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def handle_interaction(self,
                         interaction_type: str,
                         initiator_id: str,
                         target_ids: List[str],
                         interaction_data: Dict) -> Dict:

        try:
            result = self.interaction.create_interaction(
                interaction_type,
                initiator_id,
                target_ids,
                interaction_data
            )

            if result['success']:
                self._process_interaction_effects(result['interaction'])

            return result

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _update_core_systems(self, delta_time: float, updates: Dict):

        env_updates = self.environment.update(delta_time)
        updates['events'].extend(env_updates.get('events', []))

        physics_updates = self.physics.update(delta_time)
        updates['events'].extend(physics_updates.get('events', []))

        interaction_updates = self.interaction.update_all(delta_time)
        updates['events'].extend(interaction_updates.get('events', []))

    def _update_social_systems(self, delta_time: float, updates: Dict):

        rel_updates = self.relationships.update(delta_time)
        updates['events'].extend(rel_updates.get('events', []))

        faction_updates = self.factions.update(delta_time)
        updates['events'].extend(faction_updates.get('events', []))

    def _update_performance_metrics(self, metrics: Dict):

        metrics.update({
            'fps': self._calculate_fps(),
            'active_players': len(self.players),
            'active_agents': len(self.ai_agents),
            'memory_usage': self._get_memory_usage(),
            'cpu_usage': self._get_cpu_usage()
        })