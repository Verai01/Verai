from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import logging
from threading import Lock

class ControlCommand(Enum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"    STOP = "stop"
    RESET = "reset"
    SAVE = "save"
    LOAD = "load"

class SimulationState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class SandboxController:

    def __init__(self, simulation: 'SandboxSimulation'):
        self.simulation = simulation
        self.command_history: List[Dict] = []
        self.save_states: Dict[str, Any] = {}
        self.active_commands: Dict[str, Dict] = {}

        self._lock = Lock()  # Neu: Thread-Lock
        self.is_processing = False
        self.last_update = datetime.now()
        self.error_count = 0

        self.MAX_HISTORY_ENTRIES = 1000
        self.MAX_SAVE_STATES = 10

        self._setup_logging()

    def _setup_logging(self):

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='sandbox_controller.log'
        )

    def _trim_history(self):

        if len(self.command_history) > self.MAX_HISTORY_ENTRIES:
            self.command_history = self.command_history[-self.MAX_HISTORY_ENTRIES:]

    def _trim_save_states(self):

        if len(self.save_states) > self.MAX_SAVE_STATES:
            oldest_save = min(self.save_states.keys())
            del self.save_states[oldest_save]

    def execute_command(self, command: ControlCommand, params: Dict = None) -> Dict:

        with self._lock:  # Neu: Thread-safe execution
            if self.is_processing:
                return {'success': False, 'reason': 'Controller is busy'}

            self.is_processing = True
            result = {'success': False, 'command': command.value}

            try:
                if command == ControlCommand.START:
                    result = self._start_simulation(params)
                elif command == ControlCommand.PAUSE:
                    result = self._pause_simulation()
                elif command == ControlCommand.RESUME:
                    result = self._resume_simulation()
                elif command == ControlCommand.STOP:
                    result = self._stop_simulation()
                elif command == ControlCommand.RESET:
                    result = self._reset_simulation()
                elif command == ControlCommand.SAVE:
                    result = self._save_state(params)
                elif command == ControlCommand.LOAD:
                    result = self._load_state(params)

                self._log_command(command, params, result)
                self._trim_history()  

            except Exception as e:
                logging.error(f"Command execution error: {str(e)}")
                result['reason'] = str(e)
                self.error_count += 1

            finally:
                self.is_processing = False

            return result

    def _start_simulation(self, params: Optional[Dict]) -> Dict:

        if self.simulation.state != SimulationState.INITIALIZING:
            return {'success': False, 'reason': 'Simulation already started'}

        try:

            if params:
                self._apply_simulation_params(params)

            self.simulation.state = SimulationState.RUNNING
            self.last_update = datetime.now()

            return {
                'success': True,
                'simulation_id': self.simulation.simulation_id,
                'start_time': self.last_update
            }

        except Exception as e:
            self.simulation.state = SimulationState.ERROR
            raise e

    def _save_state(self, params: Optional[Dict]) -> Dict:

        save_id = str(datetime.now().timestamp())

        try:
            state_data = self.simulation.get_state()
            self.save_states[save_id] = state_data
            self._trim_save_states()  

            return {
                'success': True,
                'save_id': save_id,
                'timestamp': datetime.now()
            }

        except Exception as e:
            logging.error(f"Save state error: {str(e)}")
            return {'success': False, 'reason': str(e)}

    def _load_state(self, params: Dict) -> Dict:

        save_id = params.get('save_id')
        if not save_id or save_id not in self.save_states:
            return {'success': False, 'reason': 'Save state not found'}

        try:
            state_data = self.save_states[save_id]
            self.simulation.set_state(state_data)

            return {
                'success': True,
                'save_id': save_id,
                'timestamp': datetime.now()
            }

        except Exception as e:
            logging.error(f"Load state error: {str(e)}")
            return {'success': False, 'reason': str(e)}

    def _log_command(self, command: ControlCommand, params: Dict, result: Dict):

        log_entry = {
            'timestamp': datetime.now(),
            'command': command.value,
            'params': params,
            'result': result
        }
        self.command_history.append(log_entry)
