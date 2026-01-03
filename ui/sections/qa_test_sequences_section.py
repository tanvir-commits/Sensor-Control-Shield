"""QA Test Sequences section for device-agnostic test execution."""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                               QSpinBox, QLineEdit, QTextEdit, QTabWidget, QWidget,
                               QHeaderView, QMessageBox, QFileDialog, QCheckBox, QSizePolicy,
                               QScrollArea)
from PySide6.QtCore import Qt, Signal, QThread, QEvent
from PySide6.QtGui import QFont
from typing import Dict, List, Optional
import time
import json

try:
    import serial.tools.list_ports
except ImportError:
    serial = None

try:
    from features.test_sequences.dut_profile import DUTProfileManager, DUTProfile
    from features.test_sequences.sequence_builder import SequenceBuilder, Sequence, SequenceStep, StepType
    from features.test_sequences.qa_engine import QAEngine, ExecutionStatus
    from features.test_sequences.results import ResultsManager
    TEST_SEQUENCES_AVAILABLE = True
except ImportError as e:
    print(f"Test sequences modules not available: {e}")
    TEST_SEQUENCES_AVAILABLE = False
    # Define dummy types for type hints when module not available
    QAEngine = None
    Sequence = None
    SequenceStep = None
    DUTProfile = None
    DUTProfileManager = None
    SequenceBuilder = None
    ResultsManager = None
    ExecutionStatus = None


class ExecutionThread(QThread):
    """Thread for executing sequences without blocking UI."""
    
    finished = Signal(object)  # Emits SequenceResult
    progress = Signal(dict)  # Emits progress dict
    
    def __init__(self, engine, sequence, dut_profile):
        super().__init__()
        self.engine = engine
        self.sequence = sequence
        self.dut_profile = dut_profile
    
    def run(self):
        """Execute sequence in thread."""
        # Set progress callback
        self.engine.set_progress_callback(self.progress.emit)
        
        # Execute
        result = self.engine.execute_sequence(self.sequence, self.dut_profile)
        self.finished.emit(result)


class DUTProfileWidget(QWidget):
    """Widget for managing DUT profiles."""
    
    def __init__(self, profile_manager: DUTProfileManager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.current_profile: Optional[DUTProfile] = None
        self.setup_ui()
        self.refresh_profiles()
    
    def setup_ui(self):
        """Set up DUT profile UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Profile selection
        profile_group = QGroupBox("DUT Profile")
        profile_layout = QVBoxLayout()
        
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.on_profile_selected)
        select_layout.addWidget(self.profile_combo)
        
        new_button = QPushButton("New")
        new_button.clicked.connect(self.on_new_profile)
        select_layout.addWidget(new_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.on_delete_profile)
        select_layout.addWidget(delete_button)
        
        profile_layout.addLayout(select_layout)
        
        # Profile details
        details_group = QGroupBox("Profile Details")
        details_layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        details_layout.addLayout(name_layout)
        
        # UART settings
        uart_layout = QHBoxLayout()
        uart_layout.addWidget(QLabel("UART Port:"))
        self.uart_port_combo = QComboBox()
        self.uart_port_combo.setEditable(True)
        self.uart_port_combo.setMinimumWidth(200)
        uart_layout.addWidget(self.uart_port_combo)
        
        # Refresh button for serial ports
        refresh_uart_button = QPushButton("Refresh")
        refresh_uart_button.setToolTip("Refresh list of available serial ports")
        refresh_uart_button.clicked.connect(self.refresh_serial_ports)
        uart_layout.addWidget(refresh_uart_button)
        
        uart_layout.addWidget(QLabel("Baud:"))
        self.baud_spinbox = QSpinBox()
        self.baud_spinbox.setMinimum(9600)
        self.baud_spinbox.setMaximum(921600)
        self.baud_spinbox.setValue(115200)
        uart_layout.addWidget(self.baud_spinbox)
        details_layout.addLayout(uart_layout)
        
        # Populate serial ports on startup
        self.refresh_serial_ports()
        
        # GPIO settings
        gpio_layout = QHBoxLayout()
        gpio_layout.addWidget(QLabel("Wake GPIO:"))
        self.wake_gpio_spinbox = QSpinBox()
        self.wake_gpio_spinbox.setMinimum(0)
        self.wake_gpio_spinbox.setMaximum(40)
        self.wake_gpio_spinbox.setSpecialValueText("None")
        gpio_layout.addWidget(self.wake_gpio_spinbox)
        
        gpio_layout.addWidget(QLabel("Reset GPIO:"))
        self.reset_gpio_spinbox = QSpinBox()
        self.reset_gpio_spinbox.setMinimum(0)
        self.reset_gpio_spinbox.setMaximum(40)
        self.reset_gpio_spinbox.setSpecialValueText("None")
        gpio_layout.addWidget(self.reset_gpio_spinbox)
        details_layout.addLayout(gpio_layout)
        
        # Task descriptions
        task_group = QGroupBox("Task Descriptions (1-4)")
        task_layout = QVBoxLayout()
        
        self.task_edits = {}
        for i in range(1, 5):
            task_layout_item = QHBoxLayout()
            task_layout_item.addWidget(QLabel(f"Task {i}:"))
            task_edit = QLineEdit()
            task_edit.setPlaceholderText(f"Description for task {i}")
            self.task_edits[i] = task_edit
            task_layout_item.addWidget(task_edit)
            task_layout.addLayout(task_layout_item)
        
        task_group.setLayout(task_layout)
        details_layout.addWidget(task_group)
        
        details_group.setLayout(details_layout)
        profile_layout.addWidget(details_group)
        
        # Save button
        save_button = QPushButton("Save Profile")
        save_button.clicked.connect(self.on_save_profile)
        profile_layout.addWidget(save_button)
        
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def showEvent(self, event):
        """Refresh serial ports when widget becomes visible."""
        super().showEvent(event)
        # Refresh serial ports when tab is shown
        self.refresh_serial_ports()
    
    def refresh_profiles(self):
        """Refresh profile list."""
        # Disconnect signal temporarily
        try:
            self.profile_combo.currentTextChanged.disconnect()
        except (TypeError, RuntimeError):
            pass
        
        self.profile_combo.clear()
        profiles = self.profile_manager.list_profiles()
        self.profile_combo.addItems(profiles)
        
        if profiles:
            # Try to restore last selected profile
            last_profile = self._load_last_dut_profile()
            if last_profile and last_profile in profiles:
                self.profile_combo.setCurrentText(last_profile)
                self.on_profile_selected(last_profile)
            else:
                # Prefer "mock" profile if it exists, otherwise use first profile
                if "mock" in profiles:
                    self.profile_combo.setCurrentText("mock")
                    self.on_profile_selected("mock")
                else:
                    self.profile_combo.setCurrentIndex(0)
                    self.on_profile_selected(profiles[0])
        
        # Reconnect signal
        self.profile_combo.currentTextChanged.connect(self.on_profile_selected)
    
    def refresh_serial_ports(self):
        """Refresh the list of available serial ports."""
        if serial is None:
            # Fallback if pyserial not available
            current_text = self.uart_port_combo.currentText()
            self.uart_port_combo.clear()
            self.uart_port_combo.addItem("/dev/ttyUSB0")
            self.uart_port_combo.addItem("/dev/ttyACM0")
            self.uart_port_combo.addItem("/dev/ttyACM1")
            if current_text:
                self.uart_port_combo.setCurrentText(current_text)
            return
        
        # Store current selection (get actual device path, not display text)
        current_port = self._get_uart_port_value()
        
        # Get list of available serial ports
        ports = []
        try:
            available_ports = serial.tools.list_ports.comports()
            for port in available_ports:
                # Filter for USB serial devices (ttyUSB, ttyACM) and common serial ports
                if any(port.device.startswith(prefix) for prefix in ['/dev/ttyUSB', '/dev/ttyACM', 'COM']):
                    # Format: "/dev/ttyUSB0 - USB Serial (description)"
                    display_text = f"{port.device}"
                    if port.description:
                        display_text += f" - {port.description}"
                    ports.append((port.device, display_text))
        except Exception as e:
            print(f"Error detecting serial ports: {e}")
        
        # Clear and populate combo box
        self.uart_port_combo.clear()
        
        # Add detected ports
        for device, display_text in ports:
            self.uart_port_combo.addItem(display_text, device)
        
        # If no ports found, add common defaults
        if not ports:
            self.uart_port_combo.addItem("/dev/ttyUSB0")
            self.uart_port_combo.addItem("/dev/ttyACM0")
            self.uart_port_combo.addItem("/dev/ttyACM1")
        
        # Restore previous selection if it still exists
        if current_port:
            # Try to find exact match by device path
            for i in range(self.uart_port_combo.count()):
                item_data = self.uart_port_combo.itemData(i)
                if item_data == current_port:
                    self.uart_port_combo.setCurrentIndex(i)
                    return
            
            # If not found, try to set as editable text
            self.uart_port_combo.setCurrentText(current_port)
        elif ports:
            # If no previous selection, select first port
            self.uart_port_combo.setCurrentIndex(0)
    
    def _get_uart_port_value(self) -> str:
        """Get the actual UART port device path from combo box."""
        # Try to get data (actual device path) first
        current_index = self.uart_port_combo.currentIndex()
        if current_index >= 0:
            item_data = self.uart_port_combo.itemData(current_index)
            if item_data:
                return str(item_data)
        
        # Fallback to current text
        text = self.uart_port_combo.currentText()
        # If text contains " - ", extract just the device path
        if " - " in text:
            return text.split(" - ")[0]
        return text
    
    def on_profile_selected(self, name: str):
        """Handle profile selection."""
        if not name:
            return
        
        # Save as last selected profile
        self._save_last_dut_profile(name)
        
        profile = self.profile_manager.get_profile(name)
        if profile:
            self.current_profile = profile
            self.name_edit.setText(profile.name)
            # Set UART port - try to match by device path or display text
            port_found = False
            for i in range(self.uart_port_combo.count()):
                item_data = self.uart_port_combo.itemData(i)
                item_text = self.uart_port_combo.itemText(i)
                # Match by device path (data) or by display text
                if (item_data and str(item_data) == profile.uart_port) or \
                   (item_text and profile.uart_port in item_text):
                    self.uart_port_combo.setCurrentIndex(i)
                    port_found = True
                    break
            if not port_found:
                # Port from profile doesn't exist in current list - set as editable text
                # This allows user to see what's saved, but they should update it
                self.uart_port_combo.setCurrentText(profile.uart_port)
                # Show a tooltip warning
                self.uart_port_combo.setToolTip(
                    f"Warning: Port '{profile.uart_port}' from profile is not currently available. "
                    f"Select an available port and save the profile to update it."
                )
            self.baud_spinbox.setValue(profile.uart_baud)
            self.wake_gpio_spinbox.setValue(profile.gpio_wake or 0)
            self.reset_gpio_spinbox.setValue(profile.gpio_reset or 0)
            
            for i in range(1, 5):
                task_desc = profile.tasks.get(str(i), "")
                self.task_edits[i].setText(task_desc)
    
    def on_new_profile(self):
        """Create new profile."""
        self.current_profile = None
        self.name_edit.clear()
        # Refresh ports and set default
        self.refresh_serial_ports()
        if self.uart_port_combo.count() > 0:
            self.uart_port_combo.setCurrentIndex(0)
        else:
            self.uart_port_combo.setCurrentText("/dev/ttyUSB0")
        self.baud_spinbox.setValue(115200)
        self.wake_gpio_spinbox.setValue(0)
        self.reset_gpio_spinbox.setValue(0)
        for i in range(1, 5):
            self.task_edits[i].clear()
    
    def on_delete_profile(self):
        """Delete current profile."""
        name = self.profile_combo.currentText()
        if not name:
            return
        
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Delete profile '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.profile_manager.delete(name):
                self.refresh_profiles()
    
    def on_save_profile(self):
        """Save profile."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Profile name is required")
            return
        
        # Get the actual port value (device path, not display text)
        uart_port = self._get_uart_port_value()
        if not uart_port:
            QMessageBox.warning(self, "Error", "UART port is required")
            return
        
        # Create profile
        profile = DUTProfile(
            name=name,
            uart_port=uart_port,
            uart_baud=self.baud_spinbox.value(),
            gpio_wake=self.wake_gpio_spinbox.value() if self.wake_gpio_spinbox.value() > 0 else None,
            gpio_reset=self.reset_gpio_spinbox.value() if self.reset_gpio_spinbox.value() > 0 else None,
            tasks={str(i): self.task_edits[i].text().strip() for i in range(1, 11) if self.task_edits[i].text().strip()}
        )
        
        if self.profile_manager.save(profile):
            QMessageBox.information(self, "Success", f"Profile '{name}' saved with UART port: {uart_port}")
            self.refresh_profiles()
            self.profile_combo.setCurrentText(name)
            # Clear tooltip after saving
            self.uart_port_combo.setToolTip("")
        else:
            QMessageBox.warning(self, "Error", "Failed to save profile")
    
    def _save_last_dut_profile(self, profile_name: str):
        """Save last selected DUT profile to settings."""
        if not profile_name:
            return
        
        try:
            from pathlib import Path
            settings_file = Path.home() / '.device_panel' / 'execution_settings.json'
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        settings = json.load(f)
                except:
                    pass
            
            settings['last_dut_profile'] = profile_name
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save last DUT profile: {e}")
    
    def _load_last_dut_profile(self) -> Optional[str]:
        """Load last selected DUT profile from settings."""
        try:
            from pathlib import Path
            settings_file = Path.home() / '.device_panel' / 'execution_settings.json'
            
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('last_dut_profile')
        except Exception as e:
            print(f"Failed to load last DUT profile: {e}")
        
        return None


class SequenceBuilderWidget(QWidget):
    """Widget for building test sequences."""
    
    def __init__(self, sequence_builder: SequenceBuilder, profile_manager: DUTProfileManager = None, parent=None):
        super().__init__(parent)
        self.sequence_builder = sequence_builder
        self.profile_manager = profile_manager
        self.current_sequence: Optional[Sequence] = None
        self.current_profile_name: Optional[str] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up sequence builder UI."""
        # Create scroll area to prevent vertical overflow
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create content widget
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Sequence name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Sequence Name:"))
        self.sequence_name_edit = QLineEdit()
        self.sequence_name_edit.setPlaceholderText("Enter sequence name")
        name_layout.addWidget(self.sequence_name_edit)
        
        new_button = QPushButton("New")
        new_button.clicked.connect(self.on_new_sequence)
        name_layout.addWidget(new_button)
        
        layout.addLayout(name_layout)
        
        # Sequence selector (load existing sequences)
        seq_selector_layout = QHBoxLayout()
        seq_selector_layout.addWidget(QLabel("Load Sequence:"))
        self.sequence_selector_combo = QComboBox()
        self.sequence_selector_combo.addItem("(Select a sequence to load)")
        self._populate_sequence_selector()
        self.sequence_selector_combo.currentTextChanged.connect(self.on_sequence_selected)
        seq_selector_layout.addWidget(self.sequence_selector_combo)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._populate_sequence_selector)
        seq_selector_layout.addWidget(refresh_button)
        
        layout.addLayout(seq_selector_layout)
        
        # DUT Profile selector (for task descriptions)
        if self.profile_manager:
            profile_layout = QHBoxLayout()
            profile_layout.addWidget(QLabel("DUT Profile (for task descriptions):"))
            self.profile_combo = QComboBox()
            profiles = self.profile_manager.list_profiles()
            if profiles:
                self.profile_combo.addItems(profiles)
                self.current_profile_name = profiles[0]
                self.profile_combo.setCurrentText(profiles[0])
            else:
                self.profile_combo.addItem("(No profiles - create one in DUT Profiles tab)")
                self.current_profile_name = None
            self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
            profile_layout.addWidget(self.profile_combo)
            layout.addLayout(profile_layout)
        
        # Add step controls
        self.step_group = QGroupBox("Add Step")
        self.step_group.setToolTip("Configure parameters for a new step, then click 'Add Step' to add it to the sequence")
        self.step_group.setMinimumHeight(180)
        self.step_group.setMinimumWidth(400)  # Prevent horizontal shrinking
        self.step_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        step_layout = QVBoxLayout()
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Step Type:"))
        self.step_type_combo = QComboBox()
        self.step_type_combo.addItems([
            "Wake", "Task", "Sleep", "Wait", "Repeat", "Pass", "Fail"
        ])
        self.step_type_combo.currentTextChanged.connect(self.on_step_type_changed)
        type_layout.addWidget(self.step_type_combo)
        type_layout.addStretch()  # Add stretch to push content to left, but allow expansion
        step_layout.addLayout(type_layout)
        
        # Step parameters (dynamic based on type)
        # Simple widget with minimum height and width to prevent shrinking
        self.params_widget = QWidget()
        self.params_widget.setMinimumHeight(80)
        self.params_widget.setMinimumWidth(200)  # Prevent horizontal shrinking
        # Use Expanding size policy to prevent horizontal shrinking
        self.params_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.params_layout = QVBoxLayout()
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(5)
        self.params_widget.setLayout(self.params_layout)
        step_layout.addWidget(self.params_widget)
        
        add_button = QPushButton("Add Step")
        add_button.clicked.connect(self.on_add_step)
        step_layout.addWidget(add_button)
        
        self.step_group.setLayout(step_layout)
        layout.addWidget(self.step_group)
        
        # Sequence steps table
        steps_table_label = QLabel("Sequence Steps (read-only - delete and re-add to modify)")
        steps_table_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(steps_table_label)
        
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(4)
        self.steps_table.setHorizontalHeaderLabels(["#", "Type", "Parameters", "Status"])
        self.steps_table.setToolTip("Parameters shown here are read-only. To modify a step, delete it and add a new one with different parameters.")
        self.steps_table.horizontalHeader().setStretchLastSection(True)
        self.steps_table.setAlternatingRowColors(True)
        self.steps_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.steps_table.setSelectionMode(QTableWidget.SingleSelection)  # Single selection for step execution
        # Set maximum height to prevent overflow (about 10 rows visible)
        self.steps_table.setMaximumHeight(300)
        layout.addWidget(self.steps_table)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.on_delete_selected_steps)
        control_layout.addWidget(delete_button)
        
        move_up_button = QPushButton("Move Up")
        move_up_button.clicked.connect(self.on_move_selected_up)
        control_layout.addWidget(move_up_button)
        
        move_down_button = QPushButton("Move Down")
        move_down_button.clicked.connect(self.on_move_selected_down)
        control_layout.addWidget(move_down_button)
        
        control_layout.addStretch()
        
        save_button = QPushButton("Save Sequence")
        save_button.clicked.connect(self.on_save_sequence)
        control_layout.addWidget(save_button)
        
        # Step execution controls (new section)
        exec_group = QGroupBox("Test Individual Steps")
        exec_layout = QVBoxLayout()
        
        exec_button_layout = QHBoxLayout()
        
        self.run_selected_button = QPushButton("Run Selected Step")
        self.run_selected_button.clicked.connect(self.on_run_selected_step)
        self.run_selected_button.setEnabled(False)  # Disabled until step selected
        exec_button_layout.addWidget(self.run_selected_button)
        
        self.run_next_button = QPushButton("Run & Advance")
        self.run_next_button.clicked.connect(self.on_run_and_advance)
        self.run_next_button.setEnabled(False)
        exec_button_layout.addWidget(self.run_next_button)
        
        exec_button_layout.addStretch()
        
        exec_layout.addLayout(exec_button_layout)
        
        # Status label for step execution
        self.step_exec_status = QLabel("No step selected")
        self.step_exec_status.setStyleSheet("color: #666; font-style: italic;")
        exec_layout.addWidget(self.step_exec_status)
        
        exec_group.setLayout(exec_layout)
        layout.addWidget(exec_group)
        
        load_button = QPushButton("Load Sequence")
        load_button.clicked.connect(self.on_load_sequence)
        control_layout.addWidget(load_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.on_clear_sequence)
        control_layout.addWidget(clear_button)
        
        layout.addLayout(control_layout)
        
        # Don't add stretch - wrap in scroll area instead
        # Set content widget layout
        content_widget.setLayout(layout)
        scroll.setWidget(content_widget)
        
        # Set scroll area as main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
        # Set size policy to prevent vertical expansion
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Connect table selection to enable/disable buttons
        self.steps_table.selectionModel().selectionChanged.connect(self.on_step_selection_changed)
        
        self.on_step_type_changed("Wake")  # Initialize params
    
    def on_profile_changed(self, profile_name: str):
        """Handle profile selection change."""
        if profile_name and not profile_name.startswith("(No profiles"):
            self.current_profile_name = profile_name
        else:
            self.current_profile_name = None
        # Refresh table to update task descriptions
        if self.current_sequence:
            self.update_steps_table()
    
    def _populate_sequence_selector(self):
        """Populate sequence selector with available sequences."""
        self.sequence_selector_combo.clear()
        self.sequence_selector_combo.addItem("(Select a sequence to load)")
        
        # Find sequences in default directory
        from pathlib import Path
        seq_dir = Path.home() / '.device_panel' / 'sequences'
        if seq_dir.exists():
            sequences = sorted(seq_dir.glob('*.json'))
            for seq_file in sequences:
                # Try to load and get name
                try:
                    sequence = self.sequence_builder.load_sequence(str(seq_file))
                    if sequence:
                        self.sequence_selector_combo.addItem(sequence.name, str(seq_file))
                except:
                    # If loading fails, just use filename
                    self.sequence_selector_combo.addItem(seq_file.stem, str(seq_file))
    
    def on_sequence_selected(self, sequence_name: str):
        """Handle sequence selection from dropdown."""
        if sequence_name == "(Select a sequence to load)":
            return
        
        filepath = self.sequence_selector_combo.currentData()
        if filepath:
            sequence = self.sequence_builder.load_sequence(filepath)
            if sequence:
                self.current_sequence = sequence
                self.sequence_name_edit.setText(sequence.name)
                self.update_steps_table()
    
    def _delete_layout(self, layout):
        """Recursively delete all items in a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())
    
    def on_step_type_changed(self, step_type: str):
        """Update parameter widgets based on step type."""
        # Clear existing params
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
            elif item.layout():
                # Recursively delete layout items
                self._delete_layout(item.layout())
        
        # Add type-specific params
        if step_type == "Wake":
            layout = QHBoxLayout()
            layout.addWidget(QLabel("GPIO:"))
            self.wake_gpio_spinbox = QSpinBox()
            self.wake_gpio_spinbox.setMinimum(0)
            self.wake_gpio_spinbox.setMaximum(40)
            layout.addWidget(self.wake_gpio_spinbox)
            layout.addStretch()
            self.params_layout.addLayout(layout)
        
        elif step_type == "Task":
            # Task Number row
            task_layout = QHBoxLayout()
            task_layout.addWidget(QLabel("Task Number (1-4):"))
            self.task_number_spinbox = QSpinBox()
            self.task_number_spinbox.setMinimum(1)
            self.task_number_spinbox.setMaximum(4)
            task_layout.addWidget(self.task_number_spinbox)
            task_layout.addStretch()
            # Insert before spacer
            self.params_layout.insertLayout(self.params_layout.count() - 1, task_layout)
        
        elif step_type == "Sleep":
            # Mode row
            mode_layout = QHBoxLayout()
            mode_layout.addWidget(QLabel("Mode:"))
            self.sleep_mode_combo = QComboBox()
            self.sleep_mode_combo.addItems(["ACTIVE", "LIGHT", "DEEP", "SHUTDOWN"])
            mode_layout.addWidget(self.sleep_mode_combo)
            mode_layout.addStretch()
            # Insert before spacer
            self.params_layout.insertLayout(self.params_layout.count() - 1, mode_layout)
            
            # Duration row
            duration_layout = QHBoxLayout()
            duration_layout.addWidget(QLabel("Duration:"))
            self.sleep_duration_spinbox = QSpinBox()
            self.sleep_duration_spinbox.setMinimum(0)
            self.sleep_duration_spinbox.setMaximum(10000)
            duration_layout.addWidget(self.sleep_duration_spinbox)
            
            self.sleep_unit_combo = QComboBox()
            self.sleep_unit_combo.addItems(["ms", "seconds", "minutes"])
            duration_layout.addWidget(self.sleep_unit_combo)
            duration_layout.addStretch()
            # Insert before spacer
            self.params_layout.insertLayout(self.params_layout.count() - 1, duration_layout)
        
        elif step_type == "Wait":
            layout = QHBoxLayout()
            layout.addWidget(QLabel("Duration:"))
            self.wait_duration_spinbox = QSpinBox()
            self.wait_duration_spinbox.setMinimum(0)
            self.wait_duration_spinbox.setMaximum(10000)
            layout.addWidget(self.wait_duration_spinbox)
            
            self.wait_unit_combo = QComboBox()
            self.wait_unit_combo.addItems(["ms", "seconds", "minutes"])
            layout.addWidget(self.wait_unit_combo)
            layout.addStretch()
            self.params_layout.addLayout(layout)
        
        elif step_type == "Repeat":
            layout = QHBoxLayout()
            layout.addWidget(QLabel("Count:"))
            self.repeat_count_spinbox = QSpinBox()
            self.repeat_count_spinbox.setMinimum(1)
            self.repeat_count_spinbox.setMaximum(10000)
            layout.addWidget(self.repeat_count_spinbox)
            layout.addStretch()
            self.params_layout.addLayout(layout)
        
        elif step_type in ["Pass", "Fail"]:
            layout = QHBoxLayout()
            layout.addWidget(QLabel("Message:"))
            self.passfail_message_edit = QLineEdit()
            self.passfail_message_edit.setPlaceholderText("Optional message")
            layout.addWidget(self.passfail_message_edit)
            self.params_layout.addLayout(layout)
        
        # Minimum width is set in setup_ui, so QGroupBox won't shrink
        # No additional action needed
    
    def on_new_sequence(self):
        """Create new sequence."""
        name = self.sequence_name_edit.text().strip()
        if not name:
            name = "New Sequence"
            self.sequence_name_edit.setText(name)
        
        self.current_sequence = self.sequence_builder.create_sequence(name)
        self.update_steps_table()
    
    def on_add_step(self):
        """Add step to sequence."""
        if not self.current_sequence:
            self.on_new_sequence()
        
        step_type = self.step_type_combo.currentText()
        
        if step_type == "Wake":
            gpio = self.wake_gpio_spinbox.value()
            self.sequence_builder.add_wake_step(self.current_sequence, gpio)
        
        elif step_type == "Task":
            task_num = self.task_number_spinbox.value()
            # Description comes from DUT profile, not user input
            self.sequence_builder.add_task_step(self.current_sequence, task_num, "")
        
        elif step_type == "Sleep":
            mode = self.sleep_mode_combo.currentText()
            duration = self.sleep_duration_spinbox.value() if self.sleep_duration_spinbox.value() > 0 else None
            unit = self.sleep_unit_combo.currentText()
            self.sequence_builder.add_sleep_step(self.current_sequence, mode, duration, unit)
        
        elif step_type == "Wait":
            duration = self.wait_duration_spinbox.value()
            unit = self.wait_unit_combo.currentText()
            self.sequence_builder.add_wait_step(self.current_sequence, duration, unit)
        
        elif step_type == "Repeat":
            count = self.repeat_count_spinbox.value()
            self.sequence_builder.add_repeat_step(self.current_sequence, count)
        
        elif step_type == "Pass":
            message = self.passfail_message_edit.text().strip()
            self.sequence_builder.add_pass_step(self.current_sequence, message)
        
        elif step_type == "Fail":
            message = self.passfail_message_edit.text().strip()
            self.sequence_builder.add_fail_step(self.current_sequence, message)
        
        self.update_steps_table()
    
    def on_delete_selected_steps(self):
        """Delete selected steps from sequence."""
        if not self.current_sequence:
            QMessageBox.warning(self, "Error", "No sequence loaded")
            return
        
        selected_rows = self.steps_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Info", "No steps selected")
            return
        
        # Get row indices (sorted in descending order to remove from end first)
        row_indices = sorted([row.row() for row in selected_rows], reverse=True)
        num_steps = len(row_indices)
        
        # Confirm removal
        reply = QMessageBox.question(
            self, "Delete Steps",
            f"Delete {num_steps} selected step(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove steps from sequence (in reverse order to maintain indices)
            for row in row_indices:
                if 0 <= row < len(self.current_sequence.steps):
                    self.current_sequence.steps.pop(row)
            
            # Update table
            self.update_steps_table()
    
    def on_move_selected_up(self):
        """Move selected steps up by one position."""
        if not self.current_sequence:
            QMessageBox.warning(self, "Error", "No sequence loaded")
            return
        
        selected_rows = self.steps_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Info", "No steps selected")
            return
        
        # Get row indices (sorted ascending)
        row_indices = sorted([row.row() for row in selected_rows])
        
        # Check if any row is already at the top
        if row_indices[0] == 0:
            QMessageBox.information(self, "Info", "Cannot move up: step is already at the top")
            return
        
        # Move each selected step up (swap with step above)
        # Process from top to bottom to avoid index shifting issues
        for row in row_indices:
            if row > 0:  # Can't move first row up
                # Swap steps in sequence
                self.current_sequence.steps[row], self.current_sequence.steps[row - 1] = \
                    self.current_sequence.steps[row - 1], self.current_sequence.steps[row]
        
        # Update table and restore selection
        self.update_steps_table()
        
        # Restore selection (shifted up by 1)
        self.steps_table.clearSelection()
        for row in row_indices:
            if row > 0:
                self.steps_table.selectRow(row - 1)
    
    def on_move_selected_down(self):
        """Move selected steps down by one position."""
        if not self.current_sequence:
            QMessageBox.warning(self, "Error", "No sequence loaded")
            return
        
        selected_rows = self.steps_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Info", "No steps selected")
            return
        
        # Get row indices (sorted descending for moving down)
        row_indices = sorted([row.row() for row in selected_rows], reverse=True)
        
        # Check if any row is already at the bottom
        if row_indices[0] >= len(self.current_sequence.steps) - 1:
            QMessageBox.information(self, "Info", "Cannot move down: step is already at the bottom")
            return
        
        # Move each selected step down (swap with step below)
        # Process from bottom to top to avoid index shifting issues
        for row in row_indices:
            if row < len(self.current_sequence.steps) - 1:  # Can't move last row down
                # Swap steps in sequence
                self.current_sequence.steps[row], self.current_sequence.steps[row + 1] = \
                    self.current_sequence.steps[row + 1], self.current_sequence.steps[row]
        
        # Update table and restore selection
        self.update_steps_table()
        
        # Restore selection (shifted down by 1)
        self.steps_table.clearSelection()
        for row in row_indices:
            if row < len(self.current_sequence.steps) - 1:
                self.steps_table.selectRow(row + 1)
    
    def update_steps_table(self):
        """Update steps table display."""
        if not self.current_sequence:
            self.steps_table.setRowCount(0)
            return
        
        self.steps_table.setRowCount(len(self.current_sequence.steps))
        for i, step in enumerate(self.current_sequence.steps):
            # Step number (read-only)
            step_num_item = QTableWidgetItem(str(i + 1))
            step_num_item.setFlags(step_num_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 0, step_num_item)
            
            # Step type (read-only)
            type_item = QTableWidgetItem(step.type.value)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 1, type_item)
            
            # Parameters (read-only)
            params_str = self._format_step_params(step)
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 2, params_item)
            
            # Status column (initially empty, will be filled after execution)
            status_item = QTableWidgetItem("")
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 3, status_item)
        
        # Don't resize columns automatically - this triggers parent layout recalculation
        # that causes the QGroupBox to shrink. User can manually resize columns if needed.
    
    def _get_task_description(self, task_number: int) -> str:
        """Get task description from current DUT profile.
        
        Args:
            task_number: Task number (1-4)
        
        Returns:
            Task description or empty string if not found
        """
        if not self.profile_manager or not self.current_profile_name:
            return ""
        
        profile = self.profile_manager.get_profile(self.current_profile_name)
        if profile and profile.tasks:
            return profile.tasks.get(str(task_number), "")
        return ""
    
    def _format_step_params(self, step: SequenceStep) -> str:
        """Format step parameters for human-readable display.
        
        Args:
            step: SequenceStep to format
        
        Returns:
            Human-readable parameter string
        """
        if step.type == StepType.TASK:
            task_num = step.params.get('number', '?')
            # Look up description from profile
            desc = self._get_task_description(task_num)
            if desc:
                return f"Task {task_num} ({desc})"
            return f"Task {task_num}"
        
        elif step.type == StepType.WAKE:
            gpio = step.params.get('gpio', '?')
            return f"GPIO {gpio}"
        
        elif step.type == StepType.SLEEP:
            mode = step.params.get('mode', '?')
            duration = step.params.get('duration')
            unit = step.params.get('unit', 'seconds')
            if duration is not None and duration > 0:
                return f"{mode} for {duration} {unit}"
            return mode
        
        elif step.type == StepType.WAIT:
            duration = step.params.get('duration', 0)
            unit = step.params.get('unit', 'ms')
            return f"{duration} {unit}"
        
        elif step.type == StepType.REPEAT:
            count = step.params.get('count', 0)
            return f"{count} times"
        
        elif step.type == StepType.PASS:
            message = step.params.get('message', '')
            if message:
                return f"Pass: {message}"
            return "Pass"
        
        elif step.type == StepType.FAIL:
            message = step.params.get('message', '')
            if message:
                return f"Fail: {message}"
            return "Fail"
        
        # Fallback to JSON if unknown type
        return json.dumps(step.params, indent=0)
    
    def on_save_sequence(self):
        """Save sequence to file."""
        if not self.current_sequence:
            QMessageBox.warning(self, "Error", "No sequence to save")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Sequence", "", "JSON Files (*.json)"
        )
        
        if filepath:
            if self.sequence_builder.save_sequence(self.current_sequence, filepath):
                QMessageBox.information(self, "Success", "Sequence saved")
            else:
                QMessageBox.warning(self, "Error", "Failed to save sequence")
    
    def on_load_sequence(self):
        """Load sequence from file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Sequence", "", "JSON Files (*.json)"
        )
        
        if filepath:
            sequence = self.sequence_builder.load_sequence(filepath)
            if sequence:
                self.current_sequence = sequence
                self.sequence_name_edit.setText(sequence.name)
                self.update_steps_table()
                QMessageBox.information(self, "Success", "Sequence loaded")
            else:
                QMessageBox.warning(self, "Error", "Failed to load sequence")
    
    def on_clear_sequence(self):
        """Clear current sequence."""
        self.current_sequence = None
        self.sequence_name_edit.clear()
        self.steps_table.setRowCount(0)
    
    def get_current_sequence(self) -> Optional[Sequence]:
        """Get current sequence."""
        return self.current_sequence
    
    def on_step_selection_changed(self, selected, deselected):
        """Handle step selection change."""
        selected_rows = self.steps_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) == 1  # Only enable if exactly one row selected
        
        self.run_selected_button.setEnabled(has_selection and self.current_sequence is not None)
        self.run_next_button.setEnabled(has_selection and self.current_sequence is not None)
        
        if has_selection:
            row = selected_rows[0].row()
            step_num = row + 1
            self.step_exec_status.setText(f"Selected: Step {step_num}")
        else:
            self.step_exec_status.setText("No step selected")
    
    def on_run_selected_step(self):
        """Run the currently selected step (stays on same step)."""
        selected_rows = self.steps_table.selectionModel().selectedRows()
        if not selected_rows or len(selected_rows) != 1:
            QMessageBox.warning(self, "Error", "Select exactly one step to run")
            return
        
        if not self.current_sequence:
            QMessageBox.warning(self, "Error", "No sequence loaded")
            return
        
        row = selected_rows[0].row()
        if row >= len(self.current_sequence.steps):
            QMessageBox.warning(self, "Error", "Invalid step index")
            return
        
        # Get DUT profile
        profile_name = self.profile_combo.currentText() if hasattr(self, 'profile_combo') else None
        if not profile_name or profile_name.startswith("(No profiles"):
            QMessageBox.warning(self, "Error", "Select a DUT profile first")
            return
        
        from features.test_sequences.dut_profile import DUTProfileManager
        profile_manager = DUTProfileManager()
        profile = profile_manager.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(self, "Error", "Profile not found")
            return
        
        # Execute the step (stays on same row)
        step = self.current_sequence.steps[row]
        self._execute_single_step(step, profile, row)
    
    def on_run_and_advance(self):
        """Run the currently selected step and automatically advance to next step."""
        selected_rows = self.steps_table.selectionModel().selectedRows()
        if not selected_rows or len(selected_rows) != 1:
            QMessageBox.warning(self, "Error", "Select exactly one step to run")
            return
        
        if not self.current_sequence:
            QMessageBox.warning(self, "Error", "No sequence loaded")
            return
        
        row = selected_rows[0].row()
        if row >= len(self.current_sequence.steps):
            QMessageBox.warning(self, "Error", "Invalid step index")
            return
        
        # Get DUT profile
        profile_name = self.profile_combo.currentText() if hasattr(self, 'profile_combo') else None
        if not profile_name or profile_name.startswith("(No profiles"):
            QMessageBox.warning(self, "Error", "Select a DUT profile first")
            return
        
        from features.test_sequences.dut_profile import DUTProfileManager
        profile_manager = DUTProfileManager()
        profile = profile_manager.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(self, "Error", "Profile not found")
            return
        
        # Execute the current step
        step = self.current_sequence.steps[row]
        self._execute_single_step(step, profile, row)
        
        # Automatically advance to next step (if exists)
        next_row = row + 1
        if next_row < len(self.current_sequence.steps):
            self.steps_table.clearSelection()
            self.steps_table.selectRow(next_row)
            # Scroll to make sure next step is visible
            self.steps_table.scrollToItem(
                self.steps_table.item(next_row, 0),
                QTableWidget.EnsureVisible
            )
        else:
            QMessageBox.information(self, "Info", "Reached end of sequence")
    
    def _execute_single_step(self, step, profile, step_index):
        """Execute a single step and show result.
        
        Args:
            step: SequenceStep to execute
            profile: DUTProfile to use
            step_index: Index of step in sequence (for display)
        """
        from features.test_sequences.qa_engine import QAEngine
        from hardware.uart_manager import UARTManager
        from hardware.gpio_manager import GPIOManager
        
        # Create engine instance (or reuse if available)
        uart = UARTManager()
        gpio = GPIOManager()
        engine = QAEngine(uart, gpio)
        
        # Open UART connection (like execution tab does)
        if not uart.open(profile.uart_port, profile.uart_baud):
            error_msg = f"Failed to open UART port {profile.uart_port}. Check permissions and that no other program is using it."
            self.step_exec_status.setText(f"✗ Error: {error_msg}")
            self.step_exec_status.setStyleSheet("color: #cc0000; font-weight: bold;")
            QMessageBox.warning(self, "UART Error", error_msg)
            return
        
        # Set current sequence on engine (needed for _execute_step to work)
        # Create a dummy sequence with just this step for execution context
        from features.test_sequences.sequence_builder import Sequence
        dummy_sequence = Sequence(name="Single Step Execution", steps=[step])
        engine.current_sequence = dummy_sequence
        engine.step_index = 0
        
        # Update status
        self.step_exec_status.setText(f"Executing step {step_index + 1}...")
        self.step_exec_status.setStyleSheet("color: #0066cc; font-weight: bold;")
        
        try:
            # Execute step
            step_result = engine._execute_step(step, profile)
            
            # Show result in status label
            if step_result.success:
                status_text = f"✓ Step {step_index + 1} PASSED: {step_result.message}"
                self.step_exec_status.setStyleSheet("color: #006600; font-weight: bold;")
            else:
                status_text = f"✗ Step {step_index + 1} FAILED: {step_result.message}"
                self.step_exec_status.setStyleSheet("color: #cc0000; font-weight: bold;")
            
            self.step_exec_status.setText(status_text)
            
            # Update status column in table
            status_display = f"✓ PASS ({step_result.duration:.3f}s)" if step_result.success else f"✗ FAIL: {step_result.message}"
            status_item = QTableWidgetItem(status_display)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            if step_result.success:
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item.setForeground(Qt.red)
            self.steps_table.setItem(step_index, 3, status_item)
            
            # Only show dialog for failures
            if not step_result.success:
                QMessageBox.warning(
                    self, 
                    "Step Execution Failed",
                    f"Step {step_index + 1} ({step.type.value})\n\n"
                    f"Status: FAILED\n"
                    f"Message: {step_result.message}\n"
                    f"Duration: {step_result.duration:.3f}s"
                )
            
        except Exception as e:
            error_msg = f"Error executing step: {e}"
            self.step_exec_status.setText(f"✗ Error: {error_msg}")
            self.step_exec_status.setStyleSheet("color: #cc0000; font-weight: bold;")
            QMessageBox.warning(self, "Execution Error", error_msg)
        finally:
            # Clean up (don't close UART - might be reused)
            pass


class ExecutionWidget(QWidget):
    """Widget for executing sequences."""
    
    def __init__(self, qa_engine: QAEngine, profile_manager: DUTProfileManager, 
                 results_manager: ResultsManager, parent=None):
        super().__init__(parent)
        self.qa_engine = qa_engine
        self.profile_manager = profile_manager
        self.results_manager = results_manager
        self.execution_thread: Optional[ExecutionThread] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up execution UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Profile and sequence selection
        select_group = QGroupBox("Execution Setup")
        select_layout = QVBoxLayout()
        
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("DUT Profile:"))
        self.profile_combo = QComboBox()
        self._populate_profiles()  # This will connect the signal
        profile_layout.addWidget(self.profile_combo)
        
        refresh_profile_button = QPushButton("Refresh")
        refresh_profile_button.clicked.connect(self._populate_profiles)
        profile_layout.addWidget(refresh_profile_button)
        select_layout.addLayout(profile_layout)
        
        sequence_layout = QHBoxLayout()
        sequence_layout.addWidget(QLabel("Sequence:"))
        self.sequence_combo = QComboBox()
        self.sequence_combo.addItem("(Select a sequence)")
        self._populate_sequences()
        sequence_layout.addWidget(self.sequence_combo)
        
        refresh_seq_button = QPushButton("Refresh")
        refresh_seq_button.clicked.connect(self._populate_sequences)
        sequence_layout.addWidget(refresh_seq_button)
        
        load_button = QPushButton("Load File...")
        load_button.clicked.connect(self.on_load_sequence)
        sequence_layout.addWidget(load_button)
        select_layout.addLayout(sequence_layout)
        
        select_group.setLayout(select_layout)
        layout.addWidget(select_group)
        
        # Execution controls
        control_group = QGroupBox("Execution Controls")
        control_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.on_start)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.on_pause)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.on_stop)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        control_layout.addLayout(button_layout)
        
        # Progress
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        control_layout.addLayout(progress_layout)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Execution log
        log_group = QGroupBox("Execution Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Results summary
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Step", "Type", "Status", "Message", "Duration"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)
        
        save_results_button = QPushButton("Save Results")
        save_results_button.clicked.connect(self.on_save_results)
        results_layout.addWidget(save_results_button)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _populate_profiles(self):
        """Populate profile combo with available profiles."""
        # Disconnect signal temporarily to avoid saving during population
        try:
            self.profile_combo.currentTextChanged.disconnect()
        except (TypeError, RuntimeError):
            # Signal not connected yet, that's fine
            pass
        
        self.profile_combo.clear()
        profiles = self.profile_manager.list_profiles()
        if profiles:
            self.profile_combo.addItems(profiles)
            # Restore last selected profile
            last_profile = self._load_last_profile()
            if last_profile and last_profile in profiles:
                index = self.profile_combo.findText(last_profile)
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
        else:
            self.profile_combo.addItem("(No profiles - create one in DUT Profiles tab)")
        
        # Reconnect signal
        self.profile_combo.currentTextChanged.connect(self._save_last_profile)
    
    def _save_last_profile(self, profile_name: str):
        """Save last selected profile to settings."""
        if not profile_name or profile_name.startswith("(No profiles"):
            return
        
        try:
            from pathlib import Path
            settings_file = Path.home() / '.device_panel' / 'execution_settings.json'
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        settings = json.load(f)
                except:
                    pass
            
            settings['last_profile'] = profile_name
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print(f"Saved last profile: {profile_name}")  # Debug
        except Exception as e:
            print(f"Failed to save last profile: {e}")
    
    def _load_last_profile(self) -> Optional[str]:
        """Load last selected profile from settings."""
        try:
            from pathlib import Path
            settings_file = Path.home() / '.device_panel' / 'execution_settings.json'
            
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    profile = settings.get('last_profile')
                    if profile:
                        print(f"Loaded last profile: {profile}")  # Debug
                    return profile
        except Exception as e:
            print(f"Failed to load last profile: {e}")
        
        return None
    
    def _populate_sequences(self):
        """Populate sequence combo with available sequences."""
        self.sequence_combo.clear()
        self.sequence_combo.addItem("(Select a sequence)")
        
        # Find sequences in default directory
        from pathlib import Path
        from features.test_sequences.sequence_builder import SequenceBuilder
        builder = SequenceBuilder()
        
        seq_dir = Path.home() / '.device_panel' / 'sequences'
        if seq_dir.exists():
            sequences = sorted(seq_dir.glob('*.json'))
            for seq_file in sequences:
                # Try to load and get name
                try:
                    sequence = builder.load_sequence(str(seq_file))
                    if sequence:
                        self.sequence_combo.addItem(sequence.name, sequence)
                except:
                    # If loading fails, just use filename
                    self.sequence_combo.addItem(seq_file.stem, None)
    
    def on_load_sequence(self):
        """Load sequence file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Sequence", "", "JSON Files (*.json)"
        )
        
        if filepath:
            from features.test_sequences.sequence_builder import SequenceBuilder
            builder = SequenceBuilder()
            sequence = builder.load_sequence(filepath)
            if sequence:
                self.sequence_combo.clear()
                self.sequence_combo.addItem(sequence.name, sequence)
                self.sequence_combo.setCurrentIndex(0)
                QMessageBox.information(self, "Success", "Sequence loaded")
            else:
                QMessageBox.warning(self, "Error", "Failed to load sequence")
    
    def on_start(self):
        """Start sequence execution."""
        profile_name = self.profile_combo.currentText()
        if not profile_name or profile_name.startswith("(No profiles"):
            QMessageBox.warning(self, "Error", "Select a DUT profile")
            return
        
        sequence_data = self.sequence_combo.currentData()
        if not sequence_data or self.sequence_combo.currentText() == "(Select a sequence)":
            QMessageBox.warning(self, "Error", "Select a sequence first")
            return
        
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            QMessageBox.warning(self, "Error", "Profile not found")
            return
        
        # Clear previous results
        self.results_table.setRowCount(0)
        
        # Enable/disable buttons
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.profile_combo.setEnabled(False)
        self.sequence_combo.setEnabled(False)
        
        # Clear and initialize log
        self.log_text.clear()
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"=== Execution Started at {timestamp} ===")
        self.log_text.append(f"Profile: {profile_name}")
        self.log_text.append(f"Sequence: {sequence_data.name}")
        self.log_text.append(f"Steps: {len(sequence_data.steps)}")
        self.log_text.append("")
        
        # Execute in thread
        self.execution_thread = ExecutionThread(self.qa_engine, sequence_data, profile)
        self.execution_thread.progress.connect(self.on_progress)
        self.execution_thread.finished.connect(self.on_finished)
        self.execution_thread.start()
    
    def on_pause(self):
        """Pause execution."""
        if self.qa_engine.get_status() == ExecutionStatus.RUNNING:
            self.qa_engine.pause()
            self.pause_button.setText("Resume")
            self.log_text.append("Execution paused")
        else:
            self.qa_engine.resume()
            self.pause_button.setText("Pause")
            self.log_text.append("Execution resumed")
    
    def on_stop(self):
        """Stop execution."""
        self.qa_engine.stop()
        self.log_text.append("Execution stopped")
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.stop_button.setEnabled(False)
    
    def on_progress(self, progress_dict: dict):
        """Handle progress update."""
        step_idx = progress_dict.get('step_index', 0)
        total_steps = progress_dict.get('total_steps', 0)
        message = progress_dict.get('message', '')
        status = progress_dict.get('status', '')
        
        # Update progress label
        self.progress_label.setText(f"Step {step_idx + 1}/{total_steps}: {message}")
        
        # Add to log with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] Step {step_idx + 1}/{total_steps}: {message}"
        self.log_text.append(log_msg)
        
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_finished(self, result):
        """Handle execution finished."""
        # Re-enable controls
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.stop_button.setEnabled(False)
        self.profile_combo.setEnabled(True)
        self.sequence_combo.setEnabled(True)
        
        # Update results table
        self.results_table.setRowCount(len(result.step_results))
        for i, step_result in enumerate(result.step_results):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.results_table.setItem(i, 1, QTableWidgetItem(step_result.step.type.value))
            status = "✓ PASS" if step_result.success else "✗ FAIL"
            status_item = QTableWidgetItem(status)
            if not step_result.success:
                status_item.setForeground(Qt.red)
            else:
                status_item.setForeground(Qt.darkGreen)
            self.results_table.setItem(i, 2, status_item)
            self.results_table.setItem(i, 3, QTableWidgetItem(step_result.message))
            self.results_table.setItem(i, 4, QTableWidgetItem(f"{step_result.duration:.3f}s"))
        
        # Log result
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_text = "PASSED" if result.is_passed() else "FAILED"
        
        self.log_text.append("")
        self.log_text.append(f"=== Execution Finished at {timestamp} ===")
        self.log_text.append(f"Status: {status_text}")
        self.log_text.append(f"Total Duration: {result.total_duration:.3f}s")
        self.log_text.append(f"Passed: {result.pass_count}, Failed: {result.fail_count}")
        if result.error_message:
            self.log_text.append(f"Error: {result.error_message}")
        
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # Save result
        try:
            self.results_manager.add_result(result)
            self.results_manager.save_result(result)
        except Exception as e:
            self.log_text.append(f"Warning: Failed to save result: {e}")
        
        self.progress_label.setText(f"Finished: {status_text}")
    
    def on_save_results(self):
        """Save results to file."""
        if not self.results_manager.results:
            QMessageBox.warning(self, "Error", "No results to save")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if filepath:
            format = 'json' if filepath.endswith('.json') else 'csv'
            if self.results_manager.save_result(self.results_manager.results[-1], format):
                QMessageBox.information(self, "Success", "Results saved")
            else:
                QMessageBox.warning(self, "Error", "Failed to save results")


class QATestSequencesSection(QGroupBox):
    """QA Test Sequences section with tabs."""
    
    def __init__(self, qa_engine: QAEngine, profile_manager: DUTProfileManager,
                 sequence_builder: SequenceBuilder, results_manager: ResultsManager,
                 parent=None):
        super().__init__("QA Test Sequences", parent)
        self.qa_engine = qa_engine
        self.profile_manager = profile_manager
        self.sequence_builder = sequence_builder
        self.results_manager = results_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Set up QA Test Sequences UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # DUT Profile tab
        self.profile_widget = DUTProfileWidget(self.profile_manager)
        self.tab_widget.addTab(self.profile_widget, "DUT Profiles")
        
        # Sequence Builder tab
        self.builder_widget = SequenceBuilderWidget(
            self.sequence_builder,
            profile_manager=self.profile_manager
        )
        self.tab_widget.addTab(self.builder_widget, "Sequence Builder")
        
        # Execution tab
        self.execution_widget = ExecutionWidget(
            self.qa_engine, self.profile_manager, self.results_manager
        )
        self.tab_widget.addTab(self.execution_widget, "Execution")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
        # Set size policy to prevent vertical expansion beyond screen
        # Use Maximum instead of Preferred to respect parent constraints
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        # Calculate maximum height based on screen size
        # This ensures the widget doesn't overflow even on smaller screens
        if self.window() and hasattr(self.window(), 'screen') and self.window().screen():
            try:
                screen_height = self.window().screen().availableGeometry().height()
                # Reserve space for window chrome, menu bar, status bar, etc. (about 150px)
                max_height = screen_height - 150
                self.setMaximumHeight(max_height)
            except:
                # Fallback if screen info not available
                self.setMaximumHeight(800)
        else:
            # Fallback if window not yet shown
            self.setMaximumHeight(800)

