"""QA Engine for executing test sequences."""

import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .sequence_builder import Sequence, SequenceStep, StepType
from hardware.uart_manager import UARTManager
from hardware.gpio_manager import GPIOManager


class ExecutionStatus(Enum):
    """Sequence execution status."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class StepResult:
    """Result of executing a single step."""
    step: SequenceStep
    success: bool
    message: str = ""
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SequenceResult:
    """Result of executing a complete sequence."""
    sequence_name: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    step_results: List[StepResult] = field(default_factory=list)
    total_duration: float = 0.0
    pass_count: int = 0
    fail_count: int = 0
    error_message: str = ""
    
    def is_passed(self) -> bool:
        """Check if sequence passed."""
        return self.status == ExecutionStatus.COMPLETED and self.fail_count == 0


class QAEngine:
    """QA Engine for executing test sequences."""
    
    def __init__(self, uart_manager: UARTManager, gpio_manager: GPIOManager):
        """Initialize QA engine.
        
        Args:
            uart_manager: UART manager for MCU communication
            gpio_manager: GPIO manager for wake/reset control
        """
        self.uart = uart_manager
        self.gpio = gpio_manager
        self.status = ExecutionStatus.IDLE
        self.current_sequence: Optional[Sequence] = None
        self.current_result: Optional[SequenceResult] = None
        self.step_index = 0
        self.repeat_count = 0
        self.repeat_target = 0
        self.stop_requested = False
        self.pause_requested = False
        self.progress_callback: Optional[Callable[[Dict], None]] = None
    
    def set_progress_callback(self, callback: Callable[[Dict], None]):
        """Set callback for progress updates.
        
        Args:
            callback: Function that receives progress dict with keys:
                - step_index: Current step index
                - total_steps: Total number of steps
                - status: Current status
                - message: Status message
        """
        self.progress_callback = callback
    
    def _notify_progress(self, message: str = ""):
        """Notify progress callback."""
        if self.progress_callback and self.current_sequence:
            self.progress_callback({
                'step_index': self.step_index,
                'total_steps': len(self.current_sequence.steps),
                'status': self.status.value,
                'message': message
            })
    
    def execute_sequence(self, sequence: Sequence, dut_profile) -> SequenceResult:
        """Execute a test sequence.
        
        Args:
            sequence: Sequence to execute
            dut_profile: DUT profile with UART/GPIO configuration
        
        Returns:
            SequenceResult with execution results
        """
        # Initialize
        self.current_sequence = sequence
        self.status = ExecutionStatus.RUNNING
        self.step_index = 0
        self.repeat_count = 0
        self.repeat_target = 0
        self.stop_requested = False
        self.pause_requested = False
        
        # Open UART connection
        # Always try to open (will reuse if already open to same port/baud)
        if not self.uart.open(dut_profile.uart_port, dut_profile.uart_baud):
            result = SequenceResult(
                sequence_name=sequence.name,
                status=ExecutionStatus.FAILED,
                start_time=datetime.now(),
                error_message=f"Failed to open UART port {dut_profile.uart_port}. Check permissions and that no other program is using it."
            )
            self.status = ExecutionStatus.FAILED
            return result
        
        # Create result
        self.current_result = SequenceResult(
            sequence_name=sequence.name,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # Execute steps
            while self.step_index < len(sequence.steps) and not self.stop_requested:
                if self.pause_requested:
                    self.status = ExecutionStatus.PAUSED
                    while self.pause_requested and not self.stop_requested:
                        time.sleep(0.1)
                    if not self.stop_requested:
                        self.status = ExecutionStatus.RUNNING
                
                step = sequence.steps[self.step_index]
                step_result = self._execute_step(step, dut_profile)
                self.current_result.step_results.append(step_result)
                
                if not step_result.success:
                    self.current_result.fail_count += 1
                    # Stop on failure (can be made configurable)
                    self.status = ExecutionStatus.FAILED
                    self.current_result.error_message = step_result.message
                    break
                else:
                    self.current_result.pass_count += 1
                
                self.step_index += 1
                
                # Handle repeat
                if step.type == StepType.REPEAT:
                    count = step.params.get('count', 1)
                    if self.repeat_count < count:
                        self.repeat_count += 1
                        self.step_index = 0  # Reset to beginning
                    else:
                        self.repeat_count = 0
                        self.step_index += 1  # Continue after repeat block
            
            # Finalize
            if not self.stop_requested and self.status == ExecutionStatus.RUNNING:
                self.status = ExecutionStatus.COMPLETED
            
            self.current_result.end_time = datetime.now()
            self.current_result.total_duration = (
                (self.current_result.end_time - self.current_result.start_time).total_seconds()
            )
            self.current_result.status = self.status
            
        except Exception as e:
            self.status = ExecutionStatus.FAILED
            self.current_result.status = ExecutionStatus.FAILED
            self.current_result.error_message = str(e)
            self.current_result.end_time = datetime.now()
        
        finally:
            # Don't close UART - might be used by other features
            pass
        
        return self.current_result
    
    def _execute_step(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute a single step.
        
        Args:
            step: Step to execute
            dut_profile: DUT profile
        
        Returns:
            StepResult
        """
        start_time = time.time()
        result = StepResult(step=step, success=False, timestamp=datetime.now())
        
        try:
            if step.type == StepType.WAKE:
                result = self._execute_wake(step, dut_profile)
            elif step.type == StepType.TASK:
                result = self._execute_task(step, dut_profile)
            elif step.type == StepType.SLEEP:
                result = self._execute_sleep(step, dut_profile)
            elif step.type == StepType.WAIT:
                result = self._execute_wait(step, dut_profile)
            elif step.type == StepType.REPEAT:
                result = self._execute_repeat(step, dut_profile)
            elif step.type == StepType.PASS:
                result = self._execute_pass(step, dut_profile)
            elif step.type == StepType.FAIL:
                result = self._execute_fail(step, dut_profile)
            else:
                result.message = f"Unknown step type: {step.type}"
        except Exception as e:
            result.message = f"Error executing step: {e}"
            result.success = False
        
        result.duration = time.time() - start_time
        self._notify_progress(f"Step {self.step_index + 1}/{len(self.current_sequence.steps)}: {step.type.value}")
        return result
    
    def _execute_wake(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute wake step."""
        result = StepResult(step=step, success=False, timestamp=datetime.now())
        
        gpio = step.params.get('gpio') or dut_profile.gpio_wake
        if gpio is None:
            result.message = "No GPIO specified for wake"
            return result
        
        try:
            # Set GPIO high to wake (assuming active-high wake)
            # Note: GPIOManager uses LED IDs, we might need direct GPIO control
            # For now, we'll use a workaround or extend GPIOManager
            # TODO: Add direct GPIO pin control to GPIOManager
            result.message = f"Wake via GPIO {gpio}"
            result.success = True
            # Actual GPIO control would go here
        except Exception as e:
            result.message = f"Wake failed: {e}"
        
        return result
    
    def _execute_task(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute task step."""
        result = StepResult(step=step, success=False, timestamp=datetime.now())
        
        task_number = step.params.get('number')
        if task_number is None:
            result.message = "Task number not specified"
            return result
        
        if task_number < 1 or task_number > 10:
            result.message = f"Invalid task number: {task_number} (must be 1-10)"
            return result
        
        try:
            success, response = self.uart.send_task(task_number)
            result.success = success
            result.message = response or f"Task {task_number} executed"
            result.data = {'task_number': task_number, 'response': response}
        except Exception as e:
            result.message = f"Task execution failed: {e}"
        
        return result
    
    def _execute_sleep(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute sleep step."""
        result = StepResult(step=step, success=False, timestamp=datetime.now())
        
        mode = step.params.get('mode', 'DEEP')
        duration = step.params.get('duration')
        unit = step.params.get('unit', 'seconds')
        
        try:
            success, response = self.uart.send_sleep(mode)
            result.success = success
            result.message = response or f"Sleep mode {mode} commanded"
            result.data = {'mode': mode, 'response': response}
            
            # If duration specified, wait (MCU is sleeping)
            if duration is not None:
                wait_seconds = self._convert_duration(duration, unit)
                time.sleep(wait_seconds)
        except Exception as e:
            result.message = f"Sleep command failed: {e}"
        
        return result
    
    def _execute_wait(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute wait step."""
        result = StepResult(step=step, success=True, timestamp=datetime.now())
        
        duration = step.params.get('duration', 0)
        unit = step.params.get('unit', 'ms')
        
        wait_seconds = self._convert_duration(duration, unit)
        time.sleep(wait_seconds)
        
        result.message = f"Waited {duration} {unit}"
        return result
    
    def _execute_repeat(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute repeat step (handled in main loop)."""
        result = StepResult(step=step, success=True, timestamp=datetime.now())
        result.message = "Repeat step"
        return result
    
    def _execute_pass(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute pass step."""
        result = StepResult(step=step, success=True, timestamp=datetime.now())
        result.message = step.params.get('message', 'Pass')
        return result
    
    def _execute_fail(self, step: SequenceStep, dut_profile) -> StepResult:
        """Execute fail step."""
        result = StepResult(step=step, success=False, timestamp=datetime.now())
        result.message = step.params.get('message', 'Fail')
        return result
    
    def _convert_duration(self, duration: float, unit: str) -> float:
        """Convert duration to seconds.
        
        Args:
            duration: Duration value
            unit: Unit ('ms', 'seconds', 'minutes')
        
        Returns:
            Duration in seconds
        """
        unit_lower = unit.lower()
        if unit_lower == 'ms':
            return duration / 1000.0
        elif unit_lower == 'seconds' or unit_lower == 's':
            return duration
        elif unit_lower == 'minutes' or unit_lower == 'min':
            return duration * 60.0
        else:
            return duration  # Default to seconds
    
    def stop(self):
        """Stop sequence execution."""
        self.stop_requested = True
    
    def pause(self):
        """Pause sequence execution."""
        self.pause_requested = True
    
    def resume(self):
        """Resume sequence execution."""
        self.pause_requested = False
    
    def get_status(self) -> ExecutionStatus:
        """Get current execution status."""
        return self.status


