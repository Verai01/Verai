# src/game/world/interaction.py

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import uuid
from datetime import datetime
import numpy as np

class InteractionType(Enum):    DIALOGUE = "dialogue"
    TRADE = "trade"
    COMBAT = "combat"
    SOCIAL = "social"
    TRAINING = "training"
    QUEST = "quest"
    SPECIAL = "special"

class InteractionPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class InteractionContext:
    location: Tuple[float, float, float]
    participants: List[str]
    environment_state: Dict
    time: datetime
    conditions: Dict
    special_factors: Optional[Dict] = None

class InteractionSystem:

    def __init__(self):
        self.active_interactions: Dict[str, Dict] = {}
        self.interaction_history: List[Dict] = []
        self.pending_interactions: Dict[str, List[Dict]] = {}
        self.interaction_rules = self._load_interaction_rules()

    def create_interaction(self,
                         interaction_type: InteractionType,
                         initiator_id: str,
                         target_ids: List[str],
                         context: InteractionContext,
                         priority: InteractionPriority = InteractionPriority.MEDIUM) -> Dict:

        try:
            interaction_id = str(uuid.uuid4())

            validation = self._validate_interaction(
                interaction_type,
                initiator_id,
                target_ids,
                context
            )

            if not validation['valid']:
                return {'success': False, 'reason': validation['reason']}

            interaction = {
                'id': interaction_id,
                'type': interaction_type,
                'initiator': initiator_id,
                'targets': target_ids,
                'context': context,
                'priority': priority,
                'state': 'initializing',
                'start_time': datetime.now(),
                'events': [],
                'outcomes': {}
            }

            self._initialize_interaction_type(interaction)

            self.active_interactions[interaction_id] = interaction

            return {
                'success': True,
                'interaction_id': interaction_id,
                'interaction': interaction
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def update_interaction(self,
                         interaction_id: str,
                         action: Dict,
                         actor_id: str) -> Dict:

        if interaction_id not in self.active_interactions:
            return {'success': False, 'reason': 'Interaction not found'}

        try:
            interaction = self.active_interactions[interaction_id]

            if not self._validate_action(action, actor_id, interaction):
                return {'success': False, 'reason': 'Invalid action'}

            result = self._process_action(action, interaction)

            interaction['events'].append({
                'timestamp': datetime.now(),
                'actor': actor_id,
                'action': action,
                'result': result
            })

            if self._check_interaction_completion(interaction):
                self._complete_interaction(interaction_id)

            return {
                'success': True,
                'result': result,
                'interaction_state': interaction['state']
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def handle_dialogue(self,
                       interaction_id: str,
                       speaker_id: str,
                       dialogue_data: Dict) -> Dict:

        try:
            interaction = self.active_interactions.get(interaction_id)
            if not interaction or interaction['type'] != InteractionType.DIALOGUE:
                return {'success': False, 'reason': 'Invalid dialogue interaction'}

            response = self._process_dialogue(
                speaker_id,
                dialogue_data,
                interaction
            )

            self._update_relationships_from_dialogue(
                speaker_id,
                interaction['targets'],
                response
            )

            return {
                'success': True,
                'response': response,
                'effects': self._calculate_dialogue_effects(response)
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def handle_training(self,
                       interaction_id: str,
                       trainer_id: str,
                       student_id: str,
                       training_data: Dict) -> Dict:

        try:
            interaction = self.active_interactions.get(interaction_id)
            if not interaction or interaction['type'] != InteractionType.TRAINING:
                return {'success': False, 'reason': 'Invalid training interaction'}

            results = self._calculate_training_results(
                trainer_id,
                student_id,
                training_data
            )

            self._apply_training_effects(
                student_id,
                results
            )

            return {
                'success': True,
                'results': results,
                'improvements': self._calculate_improvements(results)
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def handle_special_interaction(self,
                                 interaction_id: str,
                                 special_type: str,
                                 participants: List[str],
                                 special_data: Dict) -> Dict:

        try:
            interaction = self.active_interactions.get(interaction_id)
            if not interaction or interaction['type'] != InteractionType.SPECIAL:
                return {'success': False, 'reason': 'Invalid special interaction'}

            validation = self._validate_special_interaction(
                special_type,
                participants,
                special_data
            )

            if not validation['valid']:
                return {'success': False, 'reason': validation['reason']}

            effects = self._process_special_effects(
                special_type,
                participants,
                special_data
            )

            self._apply_special_effects(effects)

            return {
                'success': True,
                'effects': effects,
                'impact': self._calculate_special_impact(effects)
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _process_dialogue(self,
                         speaker_id: str,
                         dialogue_data: Dict,
                         interaction: Dict) -> Dict:

        sentiment = self._analyze_dialogue_sentiment(dialogue_data['content'])
        context = self._get_dialogue_context(interaction)

        response = self._generate_dialogue_response(
            dialogue_data,
            sentiment,
            context
        )

        self._update_dialogue_context(
            interaction,
            dialogue_data,
            response
        )

        return {
            'response': response,
            'sentiment': sentiment,
            'context_updates': context
        }