# src/ai_agents/core/agent_brain.py

import numpy as np
from tensorflow import keras
from typing import Dict, List, Optional
import json
from datetime import datetime
from .personality import PersonalitySystem
from .memory_system import MemorySystem
class AgentBrain:

    def __init__(self, personality_traits: Dict[str, float]):

        self.personality_system = PersonalitySystem()
        self.memory_system = MemorySystem()

        self.decision_network = self._create_decision_network()
        self.perception_network = self._create_perception_network()
        self.learning_network = self._create_learning_network()

        self.current_state = {}
        self.goals = []
        self.personality = personality_traits
        self.last_update = datetime.now()

        self.performance_metrics = {}

    def process_input(self, input_data: Dict) -> Dict:

        try:

            self._update_state(input_data)

            perception_result = self._process_perception(input_data)

            decision = self._make_decision(perception_result)

            self._learn_from_experience(input_data, decision)

            return {
                'success': True,
                'decision': decision,
                'state_update': self.current_state
            }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def update(self, delta_time: float) -> Dict:

        updates = {
            'state_changes': [],
            'decisions': [],
            'learning_progress': {}
        }

        memory_updates = self.memory_system.update(delta_time)
        personality_updates = self.personality_system.update(delta_time)

        goal_updates = self._process_goals(delta_time)

        self._update_networks(delta_time)

        updates['state_changes'].extend(memory_updates)
        updates['state_changes'].extend(personality_updates)
        updates['decisions'].extend(goal_updates)

        self.last_update = datetime.now()
        return {'success': True, 'updates': updates}

    def learn(self, training_data: Dict) -> Dict:

        try:
            results = {
                'decision_training': self._train_decision_network(training_data),
                'perception_training': self._train_perception_network(training_data),
                'learning_training': self._train_learning_network(training_data)
            }

            return {'success': True, 'training_results': results}

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _create_decision_network(self) -> keras.Model:

        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(64,)),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

    def _create_perception_network(self) -> keras.Model:

        model = keras.Sequential([
            keras.layers.Dense(256, activation='relu', input_shape=(128,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(32, activation='sigmoid')
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

        return model

    def _create_learning_network(self) -> keras.Model:

        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(64,)),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='linear')
        ])

        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )

        return model