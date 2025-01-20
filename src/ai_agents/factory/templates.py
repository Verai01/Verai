# src/ai_agents/factory/templates.py

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import json
import logging
from ..basic_agent import BasicAgent, AgentStats, AgentPersonality

class TemplateType(Enum):    MERCHANT = "merchant"
    WARRIOR = "warrior"
    SCHOLAR = "scholar"
    CRAFTSMAN = "craftsman"
    ADVENTURER = "adventurer"
    GUARDIAN = "guardian"
    SPECIALIST = "specialist"

@dataclass
class AgentTemplate:
    type: TemplateType
    base_stats: AgentStats
    skills: List[str]
    equipment: List[str]
    personality: AgentPersonality
    dialogue_tree: Dict
    behavior_patterns: Dict
    special_abilities: List[str]

class AgentTemplates:

    def __init__(self):
        self.templates: Dict[str, AgentTemplate] = {}
        self._load_default_templates()

    def create_agent_from_template(self,
                                 template_type: TemplateType,
                                 name: str,
                                 customization: Optional[Dict] = None) -> BasicAgent:

        try:
            template = self.templates.get(template_type.value)
            if not template:
                raise ValueError(f"Template {template_type.value} not found")

            agent = BasicAgent(name)

            self._apply_template(agent, template, customization)

            return agent

        except Exception as e:
            logging.error(f"Error creating agent from template: {str(e)}")
            raise

    def register_template(self,
                         template_type: TemplateType,
                         template_data: Dict) -> Dict:

        try:

            if not self._validate_template(template_data):
                return {'success': False, 'reason': 'Invalid template data'}

            template = AgentTemplate(
                type=template_type,
                base_stats=AgentStats(**template_data['base_stats']),
                skills=template_data['skills'],
                equipment=template_data['equipment'],
                personality=AgentPersonality(template_data['personality']),
                dialogue_tree=template_data['dialogue_tree'],
                behavior_patterns=template_data['behavior_patterns'],
                special_abilities=template_data['special_abilities']
            )

            self.templates[template_type.value] = template

            return {
                'success': True,
                'template_type': template_type.value
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _load_default_templates(self):

        self.register_template(
            TemplateType.MERCHANT,
            {
                'base_stats': {
                    'health': 80,
                    'energy': 90,
                    'strength': 8,
                    'agility': 10,
                    'intelligence': 12,
                    'charisma': 15,
                    'luck': 12
                },
                'skills': ['bargaining', 'appraisal', 'persuasion'],
                'equipment': ['merchant_clothes', 'money_pouch', 'ledger'],
                'personality': 'FRIENDLY',
                'dialogue_tree': self._load_dialogue_tree('merchant'),
                'behavior_patterns': {
                    'trading': 0.8,
                    'exploring': 0.2,
                    'combat': 0.1
                },
                'special_abilities': ['price_negotiation', 'market_insight']
            }
        )

        self.register_template(
            TemplateType.WARRIOR,
            {
                'base_stats': {
                    'health': 120,
                    'energy': 100,
                    'strength': 15,
                    'agility': 12,
                    'intelligence': 8,
                    'charisma': 10,
                    'luck': 10
                },
                'skills': ['combat', 'weapon_mastery', 'tactics'],
                'equipment': ['basic_armor', 'training_sword', 'shield'],
                'personality': 'AGGRESSIVE',
                'dialogue_tree': self._load_dialogue_tree('warrior'),
                'behavior_patterns': {
                    'combat': 0.8,
                    'training': 0.6,
                    'exploring': 0.4
                },
                'special_abilities': ['power_strike', 'battle_stance']
            }
        )

    def _apply_template(self,
                       agent: BasicAgent,
                       template: AgentTemplate,
                       customization: Optional[Dict]) -> None:

        agent.stats = template.base_stats

        for skill in template.skills:
            agent.skills[skill] = {'level': 1, 'experience': 0}

        for item in template.equipment:
            agent.inventory.append({'item': item, 'quantity': 1})

        agent.personality = template.personality

        agent.knowledge_base['dialogue_tree'] = template.dialogue_tree

        agent.knowledge_base['behavior_patterns'] = template.behavior_patterns

        for ability in template.special_abilities:
            agent.skills[ability] = {'level': 1, 'experience': 0}

        if customization:
            self._apply_customization(agent, customization)