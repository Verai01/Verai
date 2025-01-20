# src/ai_agents/core/memory_system.py

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from collections import defaultdict
import json

@dataclassclass Memory:
    id: str
    timestamp: datetime
    category: str
    content: Dict
    importance: float
    emotional_value: float
    related_entities: List[str]
    tags: List[str]

class MemorySystem:

    def __init__(self, capacity: int = 1000):
        self.short_term_memory: List[Memory] = []
        self.long_term_memory: Dict[str, Memory] = {}
        self.emotional_memory: Dict[str, List[Memory]] = defaultdict(list)
        self.procedural_memory: Dict[str, Dict] = {}

        self.capacity = capacity
        self.importance_threshold = 0.5
        self.consolidation_interval = 100
        self.memory_count = 0

    def add_memory(self,
                  category: str,
                  content: Dict,
                  importance: float = 0.5,
                  emotional_value: float = 0.0,
                  related_entities: List[str] = None,
                  tags: List[str] = None) -> Dict:

        try:
            memory = Memory(
                id=f"mem_{self.memory_count}",
                timestamp=datetime.now(),
                category=category,
                content=content,
                importance=importance,
                emotional_value=emotional_value,
                related_entities=related_entities or [],
                tags=tags or []
            )

            self.short_term_memory.append(memory)
            self.memory_count += 1

            if len(self.short_term_memory) >= self.consolidation_interval:
                self._consolidate_memories()

            return {'success': True, 'memory_id': memory.id}

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def recall(self,
              query: Dict,
              limit: int = 10,
              threshold: float = 0.0) -> List[Memory]:

        memories = []

        stm_results = self._search_memories(
            self.short_term_memory,
            query,
            threshold
        )
        memories.extend(stm_results)

        ltm_results = self._search_memories(
            list(self.long_term_memory.values()),
            query,
            threshold
        )
        memories.extend(ltm_results)

        memories.sort(key=lambda x: self._calculate_relevance(x, query),
                     reverse=True)

        return memories[:limit]

    def forget(self, conditions: Dict) -> Dict:

        removed_count = 0

        self.short_term_memory = [
            mem for mem in self.short_term_memory
            if not self._matches_conditions(mem, conditions)
        ]

        to_remove = []
        for mem_id, memory in self.long_term_memory.items():
            if self._matches_conditions(memory, conditions):
                to_remove.append(mem_id)
                removed_count += 1

        for mem_id in to_remove:
            del self.long_term_memory[mem_id]

        return {
            'success': True,
            'removed_count': removed_count
        }

    def update_memory(self, memory_id: str, updates: Dict) -> Dict:

        for memory in self.short_term_memory:
            if memory.id == memory_id:
                self._apply_updates(memory, updates)
                return {'success': True, 'memory': memory}

        if memory_id in self.long_term_memory:
            memory = self.long_term_memory[memory_id]
            self._apply_updates(memory, updates)
            return {'success': True, 'memory': memory}

        return {'success': False, 'reason': 'Memory not found'}