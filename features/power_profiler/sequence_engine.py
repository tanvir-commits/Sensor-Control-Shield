"""Sequence engine for test automation."""

import time
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class SequenceActionType(Enum):
    """Types of sequence actions."""
    GPIO_TOGGLE = "gpio_toggle"
    UART_SEND = "uart_send"
    UART_RECEIVE = "uart_receive"
    ADC_READ = "adc_read"
    POWER_MEASURE = "power_measure"
    DELAY = "delay"
    CONDITIONAL = "conditional"


class SequenceAction:
    """A single action in a test sequence."""
    
    def __init__(self, action_type: SequenceActionType, params: Dict[str, Any]):
        """Initialize sequence action.
        
        Args:
            action_type: Type of action
            params: Action-specific parameters
        """
        self.action_type = action_type
        self.params = params
        self.result: Optional[Dict] = None
        self.timestamp: Optional[float] = None
    
    def execute(self, context: Dict) -> Dict:
        """Execute this action.
        
        Args:
            context: Execution context with hardware managers, profiler, etc.
        
        Returns:
            Result dictionary with 'success', 'data', 'error' keys
        """
        self.timestamp = time.time()
        
        try:
            if self.action_type == SequenceActionType.GPIO_TOGGLE:
                return self._execute_gpio_toggle(context)
            elif self.action_type == SequenceActionType.UART_SEND:
                return self._execute_uart_send(context)
            elif self.action_type == SequenceActionType.UART_RECEIVE:
                return self._execute_uart_receive(context)
            elif self.action_type == SequenceActionType.ADC_READ:
                return self._execute_adc_read(context)
            elif self.action_type == SequenceActionType.POWER_MEASURE:
                return self._execute_power_measure(context)
            elif self.action_type == SequenceActionType.DELAY:
                return self._execute_delay(context)
            elif self.action_type == SequenceActionType.CONDITIONAL:
                return self._execute_conditional(context)
            else:
                return {'success': False, 'error': f'Unknown action type: {self.action_type}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_gpio_toggle(self, context: Dict) -> Dict:
        """Execute GPIO toggle action."""
        gpio_manager = context.get('gpio_manager')
        if not gpio_manager:
            return {'success': False, 'error': 'GPIO manager not available'}
        
        pin = self.params.get('pin')
        state = self.params.get('state', True)
        duration = self.params.get('duration', 0)  # Duration in seconds
        
        if pin is None:
            return {'success': False, 'error': 'Pin not specified'}
        
        # Set GPIO state
        # Note: gpio_manager uses LED IDs, but we might need direct GPIO control
        # For now, we'll use a simplified approach
        # TODO: Add direct GPIO pin control to GPIOManager or use gpiozero directly
        
        if duration > 0:
            # Toggle for duration
            time.sleep(duration)
        
        return {'success': True, 'data': {'pin': pin, 'state': state}}
    
    def _execute_uart_send(self, context: Dict) -> Dict:
        """Execute UART send action."""
        # TODO: Implement UART send when UART manager is available
        data = self.params.get('data', '')
        return {'success': True, 'data': {'sent': data}}
    
    def _execute_uart_receive(self, context: Dict) -> Dict:
        """Execute UART receive action."""
        # TODO: Implement UART receive when UART manager is available
        timeout = self.params.get('timeout', 1.0)
        return {'success': True, 'data': {'received': ''}}
    
    def _execute_adc_read(self, context: Dict) -> Dict:
        """Execute ADC read action."""
        adc_manager = context.get('adc_manager')
        if not adc_manager:
            return {'success': False, 'error': 'ADC manager not available'}
        
        channel = self.params.get('channel', 0)
        voltage = adc_manager.read_channel(channel)
        
        return {'success': True, 'data': {'channel': channel, 'voltage': voltage}}
    
    def _execute_power_measure(self, context: Dict) -> Dict:
        """Execute power measurement action."""
        profiler = context.get('profiler')
        if not profiler:
            return {'success': False, 'error': 'Power profiler not available'}
        
        bus = self.params.get('bus')
        address = self.params.get('address', 0x40)
        
        if bus is None:
            # Measure all sensors
            measurements = profiler.get_all_measurements()
        else:
            # Measure specific sensor
            measurement = profiler.get_measurement(bus, address)
            measurements = [measurement] if measurement else []
        
        return {'success': True, 'data': {'measurements': measurements}}
    
    def _execute_delay(self, context: Dict) -> Dict:
        """Execute delay action."""
        duration = self.params.get('duration', 0.1)
        time.sleep(duration)
        return {'success': True, 'data': {'duration': duration}}
    
    def _execute_conditional(self, context: Dict) -> Dict:
        """Execute conditional action."""
        condition = self.params.get('condition')
        if_true = self.params.get('if_true')
        if_false = self.params.get('if_false')
        
        # Simple condition evaluation
        # TODO: Implement more sophisticated condition evaluation
        result = {'success': True, 'data': {'condition_met': False}}
        
        return result


class Sequence:
    """A test sequence containing multiple actions."""
    
    def __init__(self, name: str, description: str = ""):
        """Initialize sequence.
        
        Args:
            name: Sequence name
            description: Optional description
        """
        self.name = name
        self.description = description
        self.actions: List[SequenceAction] = []
        self.results: List[Dict] = []
        self.running = False
        self.paused = False
    
    def add_action(self, action: SequenceAction):
        """Add an action to the sequence."""
        self.actions.append(action)
    
    def remove_action(self, index: int):
        """Remove an action from the sequence."""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
    
    def clear_actions(self):
        """Clear all actions."""
        self.actions.clear()
    
    def execute(self, context: Dict, progress_callback: Optional[Callable] = None) -> Dict:
        """Execute the sequence.
        
        Args:
            context: Execution context with hardware managers, profiler, etc.
            progress_callback: Optional callback for progress updates
        
        Returns:
            Summary dictionary with 'success', 'actions_executed', 'errors'
        """
        self.running = True
        self.paused = False
        self.results.clear()
        
        actions_executed = 0
        errors = []
        
        try:
            for i, action in enumerate(self.actions):
                if not self.running:
                    break
                
                # Wait if paused
                while self.paused and self.running:
                    time.sleep(0.1)
                
                if progress_callback:
                    progress_callback(i, len(self.actions), action)
                
                result = action.execute(context)
                action.result = result
                self.results.append({
                    'action_index': i,
                    'action_type': action.action_type.value,
                    'result': result,
                    'timestamp': action.timestamp
                })
                
                actions_executed += 1
                
                if not result.get('success'):
                    errors.append(f"Action {i} ({action.action_type.value}): {result.get('error', 'Unknown error')}")
                
                # Small delay between actions
                time.sleep(0.01)
        
        except Exception as e:
            errors.append(f"Sequence execution error: {e}")
        
        finally:
            self.running = False
            self.paused = False
        
        return {
            'success': len(errors) == 0,
            'actions_executed': actions_executed,
            'total_actions': len(self.actions),
            'errors': errors
        }
    
    def stop(self):
        """Stop sequence execution."""
        self.running = False
    
    def pause(self):
        """Pause sequence execution."""
        self.paused = True
    
    def resume(self):
        """Resume sequence execution."""
        self.paused = False
    
    def to_dict(self) -> Dict:
        """Convert sequence to dictionary for saving."""
        return {
            'name': self.name,
            'description': self.description,
            'actions': [
                {
                    'type': action.action_type.value,
                    'params': action.params
                }
                for action in self.actions
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Sequence':
        """Create sequence from dictionary."""
        sequence = cls(data['name'], data.get('description', ''))
        for action_data in data.get('actions', []):
            action_type = SequenceActionType(action_data['type'])
            action = SequenceAction(action_type, action_data['params'])
            sequence.add_action(action)
        return sequence


class SequenceEngine:
    """Engine for managing and executing test sequences."""
    
    def __init__(self, profiler=None, gpio_manager=None, adc_manager=None):
        """Initialize sequence engine.
        
        Args:
            profiler: PowerProfiler instance
            gpio_manager: GPIOManager instance
            adc_manager: ADCManager instance
        """
        self.profiler = profiler
        self.gpio_manager = gpio_manager
        self.adc_manager = adc_manager
        self.sequences: Dict[str, Sequence] = {}
        self.current_sequence: Optional[Sequence] = None
    
    def add_sequence(self, sequence: Sequence):
        """Add a sequence."""
        self.sequences[sequence.name] = sequence
    
    def remove_sequence(self, name: str):
        """Remove a sequence."""
        if name in self.sequences:
            del self.sequences[name]
    
    def get_sequence(self, name: str) -> Optional[Sequence]:
        """Get a sequence by name."""
        return self.sequences.get(name)
    
    def list_sequences(self) -> List[str]:
        """List all sequence names."""
        return list(self.sequences.keys())
    
    def execute_sequence(self, name: str, progress_callback: Optional[Callable] = None) -> Dict:
        """Execute a sequence by name.
        
        Args:
            name: Sequence name
            progress_callback: Optional progress callback
        
        Returns:
            Execution summary
        """
        sequence = self.get_sequence(name)
        if not sequence:
            return {'success': False, 'error': f'Sequence not found: {name}'}
        
        self.current_sequence = sequence
        
        context = {
            'profiler': self.profiler,
            'gpio_manager': self.gpio_manager,
            'adc_manager': self.adc_manager
        }
        
        result = sequence.execute(context, progress_callback)
        self.current_sequence = None
        
        return result
    
    def stop_current_sequence(self):
        """Stop the currently running sequence."""
        if self.current_sequence:
            self.current_sequence.stop()

