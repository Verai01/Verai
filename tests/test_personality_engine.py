 # tests/test_personality_engine.py

import unittest
from src.game.agent_platform.personality_engine import PersonalityEngine, PersonalityTrait, SuperPower

class TestPersonalityEngine(unittest.TestCase):
    def setUp(self):
        """Wird vor jedem Test ausgeführt"""
        self.engine = PersonalityEngine()

        self.test_traits = {
            PersonalityTrait.AGGRESSION: 0.7,
            PersonalityTrait.COURAGE: 0.6,
            PersonalityTrait.WISDOM: 0.5,
            PersonalityTrait.CHARISMA: 0.4,
            PersonalityTrait.LOYALTY: 0.8
        }

        self.test_powers = [
            SuperPower.TELEKINESIS,
            SuperPower.ENERGY_BLAST
        ]

    def test_trait_validation(self):

        self.assertTrue(self.engine._validate_traits(self.test_traits))

        invalid_traits = self.test_traits.copy()
        invalid_traits[PersonalityTrait.AGGRESSION] = 1.5
        self.assertFalse(self.engine._validate_traits(invalid_traits))

    def test_power_configuration(self):

        personality = {
            'core_traits': self.test_traits
        }

        power_config = self.engine._configure_powers(self.test_powers, personality)

        self.assertEqual(len(power_config), len(self.test_powers))

        for power, config in power_config.items():
            self.assertGreater(config['effectiveness'], 0)
            self.assertLess(config['effectiveness'], 2)
            self.assertGreater(config['energy_cost'], 0)

    def test_behavior_analysis(self):

        tendencies = self.engine._analyze_behavior_tendencies(self.test_traits)

        expected_tendencies = ['aggressive', 'cautious', 'social', 'loyal', 
                             'risk_taking', 'leadership']
        for tendency in expected_tendencies:
            self.assertIn(tendency, tendencies)

        for value in tendencies.values():
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)

    def test_power_influence(self):

        influence = self.engine._calculate_power_influence(self.test_powers)

        expected_aspects = ['combat', 'social', 'mobility', 'utility']
        for aspect in expected_aspects:
            self.assertIn(aspect, influence)

        max_influence = max(influence.values())
        self.assertLessEqual(max_influence, 1)
        self.assertGreaterEqual(min(influence.values()), 0)

    def test_behavior_patterns(self):

        personality = {
            'core_traits': self.test_traits,
            'behavior_tendencies': self.engine._analyze_behavior_tendencies(self.test_traits)
        }

        patterns = self.engine._configure_behavior_patterns(personality)

        expected_patterns = ['combat', 'exploration', 'social', 'trading', 'learning']
        for pattern in expected_patterns:
            self.assertIn(pattern, patterns)

        for value in patterns.values():
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)

    def test_create_personality(self):

        result = self.engine.create_personality(
            self.test_traits,
            self.test_powers
        )

        self.assertTrue(result['success'])

        self.assertIn('personality', result)
        self.assertIn('behavior_patterns', result)
        self.assertIn('power_config', result)

if __name__ == '__main__':
    unittest.main()