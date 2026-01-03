"""UART manager for serial communication with MCUs."""

import serial
import serial.tools.list_ports
import time
from typing import Optional, List, Tuple
from hardware.platform import is_raspberry_pi


class UARTManager:
    """UART manager for communicating with MCU QA Agents.
    
    Supports:
    - Opening/closing UART connections
    - Sending commands to MCU
    - Receiving responses (OK/ERR)
    - Listing available serial ports
    """
    
    def __init__(self):
        self.is_pi = is_raspberry_pi()
        self.connection: Optional[serial.Serial] = None
        self.port: Optional[str] = None
        self.baud_rate: int = 115200
        self.timeout: float = 1.0  # Default timeout in seconds
    
    def list_ports(self) -> List[Tuple[str, str]]:
        """List available serial ports.
        
        Returns:
            List of tuples: [(port_name, description), ...]
        """
        ports = []
        try:
            for port in serial.tools.list_ports.comports():
                ports.append((port.device, port.description))
        except Exception as e:
            print(f"Error listing ports: {e}")
        return ports
    
    def open(self, port: str, baud_rate: int = 115200, timeout: float = 1.0) -> bool:
        """Open UART connection.
        
        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0' or 'COM3')
            baud_rate: Baud rate (default 115200)
            timeout: Read timeout in seconds (default 1.0)
        
        Returns:
            True if opened successfully, False otherwise
        """
        try:
            # If already open to the same port with same baud rate, no need to reopen
            if self.connection and self.connection.is_open:
                if self.port == port and self.baud_rate == baud_rate:
                    return True  # Already open to correct port
                else:
                    # Close existing connection if port or baud changed
                    self.close()
            
            # Try to open the port
            self.connection = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Wait for connection to stabilize
            time.sleep(0.1)
            
            self.port = port
            self.baud_rate = baud_rate
            self.timeout = timeout
            return True
        except serial.SerialException as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if "Permission denied" in error_msg or "could not open port" in error_msg.lower():
                print(f"Error opening UART port {port}: Permission denied. Make sure:")
                print(f"  1. You are in the 'dialout' or 'plugdev' group: sudo usermod -a -G dialout $USER")
                print(f"  2. No other program is using the port")
                print(f"  3. The port exists: ls -l {port}")
            elif "No such file or directory" in error_msg:
                print(f"Error opening UART port {port}: Port does not exist")
                print(f"  Available ports: {[p.device for p in serial.tools.list_ports.comports()]}")
            else:
                print(f"Error opening UART port {port}: {e}")
            self.connection = None
            return False
        except Exception as e:
            print(f"Error opening UART port {port}: {e}")
            self.connection = None
            return False
    
    def close(self):
        """Close UART connection."""
        if self.connection:
            try:
                if self.connection.is_open:
                    self.connection.close()
            except Exception as e:
                print(f"Error closing UART: {e}")
            finally:
                self.connection = None
                self.port = None
    
    def is_open(self) -> bool:
        """Check if UART connection is open."""
        return self.connection is not None and self.connection.is_open
    
    def send_command(self, command: str, expect_response: bool = True) -> Tuple[bool, Optional[str]]:
        """Send command to MCU and optionally wait for response.
        
        Args:
            command: Command string to send (e.g., 'TASK 1', 'SLEEP DEEP')
            expect_response: If True, wait for OK/ERR response
        
        Returns:
            Tuple of (success: bool, response: Optional[str])
            - success: True if command sent successfully
            - response: Response string if expect_response=True, None otherwise
        """
        if not self.is_open():
            return False, "UART not open"
        
        try:
            # Clear any pending data in the input buffer (HEARTBEAT messages, etc.)
            self.connection.reset_input_buffer()
            
            # Send command with newline
            cmd_bytes = (command + '\n').encode('ascii')
            self.connection.write(cmd_bytes)
            self.connection.flush()
            
            if not expect_response:
                return True, None
            
            # Wait for response - read lines until we get OK/ERR or timeout
            import time
            start_time = time.time()
            timeout = 2.0  # 2 second timeout
            
            while (time.time() - start_time) < timeout:
                if self.connection.in_waiting > 0:
                    response = self.connection.readline().decode('ascii', errors='ignore').strip()
                    
                    # Skip HEARTBEAT messages and debug output
                    if response.startswith('HEARTBEAT') or response.startswith('[') or response.startswith('CMD:'):
                        continue
                    
                    # Check for OK/ERR response
                    if response.startswith('OK'):
                        return True, response
                    elif response.startswith('ERR'):
                        return False, response
                    else:
                        # Unexpected response - might be a partial line, continue reading
                        continue
                
                # Small delay to avoid CPU spinning
                time.sleep(0.01)
            
            # Timeout - no valid response received
            return False, "Timeout waiting for response"
        
        except Exception as e:
            return False, f"Error sending command: {e}"
    
    def send_task(self, task_number: int) -> Tuple[bool, Optional[str]]:
        """Send TASK command to MCU.
        
        Args:
            task_number: Task number (1-14, firmware supports up to 14 tasks)
        
        Returns:
            Tuple of (success: bool, response: Optional[str])
        """
        if task_number < 1 or task_number > 4:
            return False, "Task number must be 1-4"
        
        return self.send_command(f"TASK {task_number}")
    
    def send_sleep(self, mode: str) -> Tuple[bool, Optional[str]]:
        """Send SLEEP command to MCU.
        
        Args:
            mode: Sleep mode ('ACTIVE', 'LIGHT', 'DEEP', 'SHUTDOWN')
        
        Returns:
            Tuple of (success: bool, response: Optional[str])
        """
        valid_modes = ['ACTIVE', 'LIGHT', 'DEEP', 'SHUTDOWN']
        if mode.upper() not in valid_modes:
            return False, f"Invalid sleep mode. Must be one of: {valid_modes}"
        
        return self.send_command(f"SLEEP {mode.upper()}")
    
    def read_response(self, timeout: Optional[float] = None) -> Optional[str]:
        """Read response from MCU (non-blocking if no data).
        
        Args:
            timeout: Optional timeout override
        
        Returns:
            Response string or None if no data available
        """
        if not self.is_open():
            return None
        
        try:
            old_timeout = self.connection.timeout
            if timeout is not None:
                self.connection.timeout = timeout
            
            if self.connection.in_waiting > 0:
                response = self.connection.readline().decode('ascii', errors='ignore').strip()
                self.connection.timeout = old_timeout
                return response
            
            self.connection.timeout = old_timeout
            return None
        except Exception as e:
            print(f"Error reading response: {e}")
            return None
    
    def flush(self):
        """Flush UART buffers."""
        if self.is_open():
            try:
                self.connection.reset_input_buffer()
                self.connection.reset_output_buffer()
            except Exception as e:
                print(f"Error flushing UART: {e}")
