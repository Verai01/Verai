# src/ai_agents/basic_agent.py

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import uuid
from datetime import datetime
import logging
import asyncio
from ..api.agent_interface import AgentInterface, AgentState, AgentType, AgentCapabilities
class AgentPersonality(Enum):
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    AGGRESSIVE = "aggressive"
    CAUTIOUS = "cautious"
    HELPFUL = "helpful"
    MYSTERIOUS = "mysterious"

@dataclass
class AgentStats:
    health: float = 100.0
    energy: float = 100.0
    strength: float = 10.0
    agility: float = 10.0
    intelligence: float = 10.0
    charisma: float = 10.0
    luck: float = 10.0

class BasicAgent:

    def __init__(self, name: str, agent_type: AgentType = AgentType.NPC):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = agent_type
        self.state = AgentState.INITIALIZING

        self.level = 1
        self.experience = 0
        self.stats = AgentStats()
        self.personality = AgentPersonality.NEUTRAL

        self.inventory: List[Dict] = []
        self.equipment: Dict[str, Dict] = {}

        self.skills: Dict[str, Dict] = {}
        self.active_effects: List[Dict] = []

        self.relationships: Dict[str, float] = {}
        self.faction_standings: Dict[str, float] = {}

        self.knowledge_base: Dict[str, Any] = {}
        self.memory: List[Dict] = []

        self.goals: List[Dict] = []
        self.current_task: Optional[Dict] = None

        self.metrics: Dict[str, float] = {}
        self.last_update: datetime = datetime.now()

    async def initialize(self, interface: AgentInterface, config: Dict) -> Dict:

        try:

            capabilities = AgentCapabilities(
                combat=True,
                trading=True,
                dialogue=True,
                training=True,
                quest_giving=False,
                crafting=False,
                special_abilities=[]
            )

            registration = await interface.register_agent(
                self.type,
                capabilities,
                config
            )

            if not registration['success']:
                return registration

            await self._initialize_systems(config)

            self.state = AgentState.READY

            return {
                'success': True,
                'agent_id': self.id,
                'registration': registration
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    async def update(self, delta_time: float) -> Dict:

        try:
            updates = {
                'state_changes': [],
                'events': [],
                'metrics': {}
            }

            await self._update_stats(delta_time)
            await self._update_effects(delta_time)

            await self._update_ai(delta_time)
            await self._process_goals(delta_time)

            self._update_metrics(delta_time)

            self.last_update = datetime.now()
            return {'success': True, 'updates': updates}

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    async def handle_interaction(self,
                               interaction_type: str,
                               source_id: str,
                               interaction_data: Dict) -> Dict:

        try:

            if not self._validate_interaction(interaction_type, interaction_data):
                return {'success': False, 'reason': 'Invalid interaction'}

            if interaction_type == "dialogue":
                response = await self._handle_dialogue(source_id, interaction_data)
            elif interaction_type == "trade":
                response = await self._handle_trade(source_id, interaction_data)
            elif interaction_type == "combat":
                response = await self._handle_combat(source_id, interaction_data)
            else:
                response = await self._handle_custom_interaction(
                    interaction_type,
                    source_id,
                    interaction_data
                )

            await self._update_relationship(source_id, response['impact'])

            return response

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def gain_experience(self, amount: int) -> Dict:

        try:
            old_level = self.level
            self.experience += amount

            while self.experience >= self._get_next_level_exp():
                self.level += 1
                await self._handle_level_up()

            return {
                'success': True,
                'gained_exp': amount,
                'total_exp': self.experience,
                'old_level': old_level,
                'new_level': self.level
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}