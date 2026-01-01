#!/usr/bin/env python3
"""Device Panel - Main entry point.

A GUI application for monitoring and controlling hardware interfaces
on a Raspberry Pi expansion board.
"""

import sys
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from hardware.gpio_manager import GPIOManager
from hardware.adc_manager import ADCManager
from hardware.i2c_scanner import I2CScanner
from hardware.spi_tester import SPITester
from hardware.power_manager import PowerManager
from config.pins import I2C_BUS

# Optional power profiler feature
try:
    from config.feature_flags import ENABLE_POWER_PROFILER
    if ENABLE_POWER_PROFILER:
        try:
            from hardware.power_measurement import PowerMeasurementManager
            from features.power_profiler.power_profiler import PowerProfiler
            from features.power_profiler.sequence_engine import SequenceEngine
            POWER_PROFILER_AVAILABLE = True
        except Exception as e:
            print(f"Power profiler not available: {e}")
            POWER_PROFILER_AVAILABLE = False
    else:
        POWER_PROFILER_AVAILABLE = False
except Exception as e:
    POWER_PROFILER_AVAILABLE = False

# Optional test sequences feature
try:
    from config.feature_flags import ENABLE_TEST_SEQUENCES
    if ENABLE_TEST_SEQUENCES:
        try:
            from hardware.uart_manager import UARTManager
            from features.test_sequences.dut_profile import DUTProfileManager
            from features.test_sequences.sequence_builder import SequenceBuilder
            from features.test_sequences.qa_engine import QAEngine
            from features.test_sequences.results import ResultsManager
            TEST_SEQUENCES_AVAILABLE = True
        except Exception as e:
            print(f"Test sequences not available: {e}")
            TEST_SEQUENCES_AVAILABLE = False
    else:
        TEST_SEQUENCES_AVAILABLE = False
except Exception as e:
    TEST_SEQUENCES_AVAILABLE = False


class Hardware:
    """Container for all hardware managers."""
    
    def __init__(self):
        self.gpio = GPIOManager()
        self.adc = ADCManager()
        self.i2c = I2CScanner(bus=I2C_BUS)
        self.spi = SPITester()
        self.power = PowerManager()
        
        # Optional power profiler feature
        if POWER_PROFILER_AVAILABLE:
            try:
                self.power_measurement = PowerMeasurementManager()
                self.power_profiler = PowerProfiler(
                    power_manager=self.power_measurement,
                    gpio_manager=self.gpio,
                    adc_manager=self.adc
                )
                self.sequence_engine = SequenceEngine(
                    profiler=self.power_profiler,
                    gpio_manager=self.gpio,
                    adc_manager=self.adc
                )
            except Exception as e:
                print(f"Failed to initialize power profiler: {e}")
                self.power_measurement = None
                self.power_profiler = None
                self.sequence_engine = None
        else:
            self.power_measurement = None
            self.power_profiler = None
            self.sequence_engine = None
        
        # Optional test sequences feature
        if TEST_SEQUENCES_AVAILABLE:
            try:
                self.uart = UARTManager()
                self.dut_profile_manager = DUTProfileManager()
                self.sequence_builder = SequenceBuilder()
                self.qa_engine = QAEngine(
                    uart_manager=self.uart,
                    gpio_manager=self.gpio
                )
                self.results_manager = ResultsManager()
            except Exception as e:
                print(f"Failed to initialize test sequences: {e}")
                self.uart = None
                self.dut_profile_manager = None
                self.sequence_builder = None
                self.qa_engine = None
                self.results_manager = None
        else:
            self.uart = None
            self.dut_profile_manager = None
            self.sequence_builder = None
            self.qa_engine = None
            self.results_manager = None


def get_git_branch():
    """Get current git branch name.
    
    Returns:
        str: Branch name (e.g., 'main', 'dev', 'feature/power-profiler')
             Returns 'unknown' if git is not available or not in a git repo.
    """
    try:
        # Get the directory containing this script
        script_dir = Path(__file__).parent.absolute()
        
        # Try to get branch name
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch else 'unknown'
        else:
            return 'unknown'
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # Git not available, not in git repo, or other error
        return 'unknown'


def main():
    """Main application entry point."""
    try:
        # Get current git branch for display
        branch = get_git_branch()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app_name = f"DeviceOps [{branch}]"
        app.setApplicationName(app_name)
        
        # Create hardware managers
        hardware = Hardware()
        
        # Create and show main window (pass branch for display)
        window = MainWindow(mock_hardware=hardware, branch=branch)
        window.show()
        
        # Run application
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        print(f"Error launching GUI: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
