from typing import Dict, Optional, Set
import logging
from enum import Enum
from datetime import datetime
import asyncio
from threading import Lock
import weakref

class AgentState(Enum):
    INITIALIZING = "initializing"    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class AgentInterface:

    def __init__(self):

        self.MAX_CONNECTIONS = 1000
        self.CONNECTION_TIMEOUT = 30  
        self.CLEANUP_INTERVAL = 300   

        self._lock = Lock()

        self.registered_agents: Dict[str, Dict] = {}
        self.agent_states: Dict[str, AgentState] = {}

        self.active_connections: Dict[str, weakref.ref] = {}
        self.connection_timestamps: Dict[str, datetime] = {}

        self.event_handlers: Dict[str, Dict] = {}
        self.last_event_time: Dict[str, datetime] = {}

        self._setup_logging()

    async def initialize(self):

        self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
        return self

    async def cleanup(self):

        if hasattr(self, 'cleanup_task'):
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

    def _setup_logging(self):

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='agent_interface.log'
        )

    async def _periodic_cleanup(self):

        while True:
            try:
                await asyncio.sleep(self.CLEANUP_INTERVAL)
                await self._cleanup_inactive_connections()
                self._cleanup_old_events()
            except Exception as e:
                logging.error(f"Cleanup error: {str(e)}")

    async def _cleanup_inactive_connections(self):

        current_time = datetime.now()
        with self._lock:
            for agent_id, timestamp in list(self.connection_timestamps.items()):
                if (current_time - timestamp).seconds > self.CONNECTION_TIMEOUT:
                    await self._disconnect_agent(agent_id)

    def _cleanup_old_events(self):

        current_time = datetime.now()
        with self._lock:
            for agent_id in list(self.event_handlers.keys()):
                if agent_id not in self.registered_agents:
                    del self.event_handlers[agent_id]

    async def register_agent(self, agent_data: Dict) -> Dict:

        with self._lock:
            try:
                agent_id = agent_data.get('id')
                if not agent_id:
                    return {'success': False, 'reason': 'No agent ID provided'}

                if len(self.registered_agents) >= self.MAX_CONNECTIONS:
                    return {'success': False, 'reason': 'Maximum connections reached'}

                if agent_id in self.registered_agents:
                    return {'success': False, 'reason': 'Agent already registered'}

                self.registered_agents[agent_id] = agent_data
                self.agent_states[agent_id] = AgentState.INITIALIZING

                logging.info(f"Agent registered: {agent_id}")

                return {
                    'success': True,
                    'agent_id': agent_id,
                    'timestamp': datetime.now()
                }

            except Exception as e:
                logging.error(f"Agent registration error: {str(e)}")
                return {'success': False, 'reason': str(e)}

    async def connect_agent(self, agent_id: str) -> Dict:

        with self._lock:
            try:
                if agent_id not in self.registered_agents:
                    return {'success': False, 'reason': 'Agent not registered'}

                connection_obj = type('Connection', (), {'data': {}})()

                self.agent_states[agent_id] = AgentState.ACTIVE
                self.connection_timestamps[agent_id] = datetime.now()
                self.active_connections[agent_id] = weakref.ref(connection_obj)

                return {
                    'success': True,
                    'connection': self.active_connections[agent_id],
                    'session_id': f"session_{agent_id}_{datetime.now().timestamp()}"
                }

            except Exception as e:
                logging.error(f"Agent connection error: {str(e)}")
                return {'success': False, 'reason': str(e)}

    async def _establish_connection(self, agent_id: str) -> Dict:

        try:

            await asyncio.wait_for(
                self._connect_agent_internal(agent_id),
                timeout=self.CONNECTION_TIMEOUT
            )

            return {
                'success': True,
                'connection': weakref.ref({}),  
                'session_id': f"session_{agent_id}_{datetime.now().timestamp()}"
            }

        except asyncio.TimeoutError:
            return {'success': False, 'reason': 'Connection timeout'}
        except Exception as e:
            return {'success': False, 'reason': str(e)}

    async def _connect_agent_internal(self, agent_id: str):

        await asyncio.sleep(0.1) 

    async def _disconnect_agent(self, agent_id: str):

        with self._lock:
            if agent_id in self.active_connections:
                del self.active_connections[agent_id]
            if agent_id in self.connection_timestamps:
                del self.connection_timestamps[agent_id]
            if agent_id in self.agent_states:
                self.agent_states[agent_id] = AgentState.DISCONNECTED

    def register_event_handler(self, agent_id: str, event_type: str, handler: callable) -> Dict:

        with self._lock:
            try:
                if agent_id not in self.registered_agents:
                    return {'success': False, 'reason': 'Agent not found'}

                if not callable(handler):
                    return {'success': False, 'reason': 'Invalid handler'}

                if agent_id not in self.event_handlers:
                    self.event_handlers[agent_id] = {}

                self.event_handlers[agent_id][event_type] = handler
                self.last_event_time[agent_id] = datetime.now()

                return {
                    'success': True,
                    'agent_id': agent_id,
                    'event_type': event_type
                }

            except Exception as e:
                logging.error(f"Event handler registration error: {str(e)}")
                return {'success': False, 'reason': str(e)}
