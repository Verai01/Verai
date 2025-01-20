from typing import Dict, Optional
from ..core.personality import PersonalityTrait
from ..behaviors.combat import CombatStats
import json
import uuid

class AgentTemplate:
    def __init__(self, template_data: Dict):
        self.name = template_data['name']
        self.personality_baseline = template_data['personality']        self.combat_stats = template_data['combat_stats']
        self.behavior_patterns = template_data['behavior_patterns']
        self.specializations = template_data['specializations']

class AgentCreator:
    def __init__(self):
        self.templates = self._load_templates()
        self.customization_options = self._get_customization_options()
        self.created_agents: Dict = {}

    def _load_templates(self) -> Dict[str, AgentTemplate]:

        with open('templates/agent_templates.json', 'r') as f:
            templates_data = json.load(f)
        return {
            name: AgentTemplate(data) 
            for name, data in templates_data.items()
        }

    def create_agent(self,
                    template_name: Optional[str] = None,
                    custom_traits: Optional[Dict] = None) -> Dict:

        agent_id = str(uuid.uuid4())
        base = template_name and self.templates[template_name] or self._create_base_agent()

        if custom_traits:
            self._apply_customization(base, custom_traits)

        agent_data = self._initialize_agent(base)
        self.created_agents[agent_id] = agent_data
        return {'agent_id': agent_id, 'agent_data': agent_data}