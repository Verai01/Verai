# src/game/world/physics.py

from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum

class PhysicsLayer(Enum):
    DEFAULT = "default"
    COMBAT = "combat"    INTERACTION = "interaction"
    TRIGGER = "trigger"
    PROJECTILE = "projectile"

@dataclass
class PhysicsProperties:
    mass: float = 1.0
    friction: float = 0.5
    restitution: float = 0.5
    is_kinematic: bool = False
    gravity_scale: float = 1.0
    collision_layer: PhysicsLayer = PhysicsLayer.DEFAULT

class PhysicsSystem:

    def __init__(self, gravity: Tuple[float, float, float] = (0.0, -9.81, 0.0)):
        self.gravity = np.array(gravity)
        self.objects: Dict[str, Dict] = {}
        self.constraints: List[Dict] = []
        self.collision_pairs: List[Tuple[str, str]] = []

        self.time_step = 1/60  # 60 Hz physics update
        self.max_substeps = 8
        self.solver_iterations = 10

        self.performance_metrics = {
            'average_update_time': 0.0,
            'collision_checks': 0,
            'active_objects': 0
        }

    def add_object(self,
                  object_id: str,
                  properties: PhysicsProperties,
                  position: Tuple[float, float, float],
                  rotation: Tuple[float, float, float, float] = (0, 0, 0, 1)) -> Dict:

        if object_id in self.objects:
            return {'success': False, 'reason': 'Object already exists'}

        object_data = {
            'properties': properties,
            'position': np.array(position),
            'rotation': np.array(rotation),
            'velocity': np.zeros(3),
            'angular_velocity': np.zeros(3),
            'forces': np.zeros(3),
            'torques': np.zeros(3),
            'awake': True
        }

        self.objects[object_id] = object_data
        self.performance_metrics['active_objects'] += 1

        return {
            'success': True,
            'object_data': object_data
        }

    def update(self, delta_time: float) -> Dict:

        updates = {
            'collisions': [],
            'position_updates': {},
            'performance': {}
        }

        start_time = np.datetime64('now')

        substep_time = delta_time / self.max_substeps

        for _ in range(self.max_substeps):
            self._update_forces()
            self._integrate(substep_time)
            collisions = self._detect_collisions()
            self._resolve_collisions(collisions)

            updates['collisions'].extend(collisions)

        end_time = np.datetime64('now')
        update_time = (end_time - start_time).astype(float)
        self._update_performance_metrics(update_time)

        updates['performance'] = self.performance_metrics
        updates['position_updates'] = self._get_position_updates()

        return updates

    def apply_force(self,
                   object_id: str,
                   force: Tuple[float, float, float],
                   point: Optional[Tuple[float, float, float]] = None) -> Dict:

        if object_id not in self.objects:
            return {'success': False, 'reason': 'Object not found'}

        obj = self.objects[object_id]

        if point is None:

            obj['forces'] += np.array(force)
        else:

            obj['forces'] += np.array(force)
            r = np.array(point) - obj['position']
            torque = np.cross(r, force)
            obj['torques'] += torque

        return {
            'success': True,
            'applied_force': force,
            'applied_point': point
        }

    def _integrate(self, dt: float):

        for obj in self.objects.values():
            if not obj['properties'].is_kinematic and obj['awake']:

                acceleration = (obj['forces'] / obj['properties'].mass +
                              self.gravity * obj['properties'].gravity_scale)
                obj['velocity'] += acceleration * dt
                obj['angular_velocity'] += (obj['torques'] /
                                          obj['properties'].mass) * dt

                obj['velocity'] *= (1.0 - obj['properties'].friction * dt)
                obj['angular_velocity'] *= (1.0 - obj['properties'].friction * dt)

                obj['position'] += obj['velocity'] * dt

                w = obj['angular_velocity']
                q = obj['rotation']
                q_dot = 0.5 * np.quaternion(0, w[0], w[1], w[2]) * q
                obj['rotation'] += q_dot * dt
                obj['rotation'] /= np.linalg.norm(obj['rotation'])

                obj['forces'].fill(0)
                obj['torques'].fill(0)

    def _detect_collisions(self) -> List[Dict]:

        collisions = []
        self.performance_metrics['collision_checks'] = 0

        potential_pairs = self._broad_phase()

        for obj1_id, obj2_id in potential_pairs:
            self.performance_metrics['collision_checks'] += 1

            if self._check_collision(obj1_id, obj2_id):
                collision_data = self._generate_collision_data(obj1_id, obj2_id)
                collisions.append(collision_data)

        return collisions