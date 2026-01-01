"""Sequence builder for defining QA test sequences."""

import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class StepType(Enum):
    """Sequence step types."""
    WAKE = "wake"
    TASK = "task"
    SLEEP = "sleep"
    WAIT = "wait"
    REPEAT = "repeat"
    PASS = "pass"
    FAIL = "fail"


@dataclass
class SequenceStep:
    """A single step in a test sequence."""
    type: StepType
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.params is None:
            self.params = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type.value,
            **self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SequenceStep':
        """Create from dictionary."""
        step_type = StepType(data['type'])
        params = {k: v for k, v in data.items() if k != 'type'}
        return cls(type=step_type, params=params)


@dataclass
class Sequence:
    """A complete test sequence."""
    name: str
    steps: List[SequenceStep]
    description: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'steps': [step.to_dict() for step in self.steps]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Sequence':
        """Create from dictionary."""
        steps = [SequenceStep.from_dict(step) for step in data.get('steps', [])]
        return cls(
            name=data['name'],
            steps=steps,
            description=data.get('description', '')
        )


class SequenceBuilder:
    """Builder for creating test sequences."""
    
    def __init__(self):
        """Initialize sequence builder."""
        self.sequences: Dict[str, Sequence] = {}
    
    def create_sequence(self, name: str, description: str = "") -> Sequence:
        """Create a new sequence.
        
        Args:
            name: Sequence name
            description: Optional description
        
        Returns:
            New Sequence object
        """
        sequence = Sequence(name=name, steps=[], description=description)
        self.sequences[name] = sequence
        return sequence
    
    def add_wake_step(self, sequence: Sequence, gpio: int) -> SequenceStep:
        """Add wake step to sequence.
        
        Args:
            sequence: Sequence to add step to
            gpio: GPIO pin number for wake
        
        Returns:
            Created step
        """
        step = SequenceStep(
            type=StepType.WAKE,
            params={'gpio': gpio}
        )
        sequence.steps.append(step)
        return step
    
    def add_task_step(self, sequence: Sequence, task_number: int, 
                     description: str = "") -> SequenceStep:
        """Add task step to sequence.
        
        Args:
            sequence: Sequence to add step to
            task_number: Task number (1-10)
            description: Optional description
        
        Returns:
            Created step
        """
        step = SequenceStep(
            type=StepType.TASK,
            params={
                'number': task_number,
                'description': description
            }
        )
        sequence.steps.append(step)
        return step
    
    def add_sleep_step(self, sequence: Sequence, mode: str, 
                      duration: Optional[float] = None, 
                      unit: str = "seconds") -> SequenceStep:
        """Add sleep step to sequence.
        
        Args:
            sequence: Sequence to add step to
            mode: Sleep mode ('ACTIVE', 'LIGHT', 'DEEP', 'SHUTDOWN')
            duration: Optional duration
            unit: Duration unit ('ms', 'seconds', 'minutes')
        
        Returns:
            Created step
        """
        params = {'mode': mode.upper()}
        if duration is not None:
            params['duration'] = duration
            params['unit'] = unit
        step = SequenceStep(type=StepType.SLEEP, params=params)
        sequence.steps.append(step)
        return step
    
    def add_wait_step(self, sequence: Sequence, duration: float, 
                     unit: str = "ms") -> SequenceStep:
        """Add wait step to sequence.
        
        Args:
            sequence: Sequence to add step to
            duration: Wait duration
            unit: Duration unit ('ms', 'seconds', 'minutes')
        
        Returns:
            Created step
        """
        step = SequenceStep(
            type=StepType.WAIT,
            params={
                'duration': duration,
                'unit': unit
            }
        )
        sequence.steps.append(step)
        return step
    
    def add_repeat_step(self, sequence: Sequence, count: int) -> SequenceStep:
        """Add repeat step to sequence.
        
        Args:
            sequence: Sequence to add step to
            count: Number of times to repeat
        
        Returns:
            Created step
        """
        step = SequenceStep(
            type=StepType.REPEAT,
            params={'count': count}
        )
        sequence.steps.append(step)
        return step
    
    def add_pass_step(self, sequence: Sequence, message: str = "") -> SequenceStep:
        """Add pass step to sequence.
        
        Args:
            sequence: Sequence to add step to
            message: Optional pass message
        
        Returns:
            Created step
        """
        step = SequenceStep(
            type=StepType.PASS,
            params={'message': message} if message else {}
        )
        sequence.steps.append(step)
        return step
    
    def add_fail_step(self, sequence: Sequence, message: str = "") -> SequenceStep:
        """Add fail step to sequence.
        
        Args:
            sequence: Sequence to add step to
            message: Optional fail message
        
        Returns:
            Created step
        """
        step = SequenceStep(
            type=StepType.FAIL,
            params={'message': message} if message else {}
        )
        sequence.steps.append(step)
        return step
    
    def save_sequence(self, sequence: Sequence, filepath: str) -> bool:
        """Save sequence to file.
        
        Args:
            sequence: Sequence to save
            filepath: File path to save to
        
        Returns:
            True if saved successfully
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(sequence.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving sequence: {e}")
            return False
    
    def load_sequence(self, filepath: str) -> Optional[Sequence]:
        """Load sequence from file.
        
        Args:
            filepath: File path to load from
        
        Returns:
            Sequence or None if error
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return Sequence.from_dict(data)
        except Exception as e:
            print(f"Error loading sequence: {e}")
            return None


