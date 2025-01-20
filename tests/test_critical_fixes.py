import unittest
import asyncio
from threading import Thread
import time
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.game.sandbox.controller import SandboxController, ControlCommand, SimulationState
from src.api.agent_interface import AgentInterface, AgentState

class MockSimulation:
    def __init__(self):
        self.state = SimulationState.INITIALIZING
        self.simulation_id = "test_sim_001"

    def get_state(self):
        return {"test": "state"}

    def set_state(self, state):
        pass

class TestCriticalFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    def setUp(self):
        self.mock_sim = MockSimulation()
        self.controller = SandboxController(self.mock_sim)
        self.agent_interface = self.loop.run_until_complete(self.async_setup())

    async def async_setup(self):
        agent_interface = AgentInterface()
        await agent_interface.initialize()
        return agent_interface

    def tearDown(self):
        self.loop.run_until_complete(self.async_teardown())

    async def async_teardown(self):
        if hasattr(self, 'agent_interface'):
            await self.agent_interface.cleanup()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    def test_sandbox_controller_thread_safety(self):

        results = []

        def run_commands():
            for _ in range(10):
                result = self.controller.execute_command(ControlCommand.START, {})
                results.append(result['success'])
                time.sleep(0.01)

        threads = [Thread(target=run_commands) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertLessEqual(len(self.controller.command_history),
                           self.controller.MAX_HISTORY_ENTRIES)

    def test_sandbox_controller_memory_management(self):

        for _ in range(self.controller.MAX_HISTORY_ENTRIES + 100):
            self.controller.execute_command(ControlCommand.START, {})

        self.assertLessEqual(len(self.controller.command_history),
                           self.controller.MAX_HISTORY_ENTRIES)

    def test_agent_interface_connection_management(self):

        async def async_test():

            agent_data = {'id': 'test_agent_001'}
            result = await self.agent_interface.register_agent(agent_data)
            self.assertTrue(result['success'], "Agent registration failed")

            connect_result = await self.agent_interface.connect_agent('test_agent_001')
            self.assertTrue(connect_result['success'], 
                          f"Agent connection failed: {connect_result.get('reason', 'Unknown error')}")

            await asyncio.sleep(0.1)
            self.assertEqual(
                self.agent_interface.agent_states['test_agent_001'],
                AgentState.ACTIVE,
                "Agent state should be ACTIVE"
            )

        self.loop.run_until_complete(async_test())

    def test_agent_interface_cleanup(self):

        async def async_test():

            for i in range(10):
                agent_data = {'id': f'test_agent_{i}'}
                await self.agent_interface.register_agent(agent_data)
                await self.agent_interface.connect_agent(f'test_agent_{i}')

            original_interval = self.agent_interface.CLEANUP_INTERVAL
            self.agent_interface.CLEANUP_INTERVAL = 2
            await asyncio.sleep(3)

            active_connections = len(self.agent_interface.active_connections)
            self.assertLessEqual(active_connections, self.agent_interface.MAX_CONNECTIONS)

            self.agent_interface.CLEANUP_INTERVAL = original_interval

        self.loop.run_until_complete(async_test())

if __name__ == '__main__':
    unittest.main()
