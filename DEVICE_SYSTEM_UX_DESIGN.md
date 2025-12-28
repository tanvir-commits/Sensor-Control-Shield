# Device System UX Design

## User Workflow

### Step 1: Scan I2C Bus
- User clicks "Scan I²C" (existing button)
- System finds devices: `0x3C`, `0x48`, etc.
- **Enhancement**: Show device suggestions next to each address

### Step 2: Device Suggestions
In I2C scan results, show:
```
Bus 1 (J12/J13):
  0x48 [Board ADC] - ADS1115/ADS1015
  0x3C [Unknown] - Possible: SSD1306 OLED, SH1106 OLED, ...
```

### Step 3: Open Device
- User clicks on a device address (e.g., `0x3C`)
- **New tab opens**: "Device: 0x3C"
- Tab shows device information and testing interface

### Step 4: Select Exact Device
If multiple suggestions:
- Dropdown: "Select device type:"
  - SSD1306 OLED (128x64)
  - SSD1309 OLED (128x64)
  - SH1106 OLED (128x64)
  - Unknown/Other

### Step 5: Plugin Management
- If plugin exists: Auto-load and show test interface
- If no plugin: Show "Add Plugin" button
  - User can:
    - Download community plugin (if available)
    - Create custom plugin (template provided)
    - Load plugin file from disk

---

## Tab Design: Device Tab

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│ Device: 0x3C (SSD1306 OLED)              [×]   │
├─────────────────────────────────────────────────┤
│                                                 │
│ [Device Info] [Test] [Config] [Plugin]        │
│                                                 │
│ ┌───────────────────────────────────────────┐ │
│ │ Device Information                        │ │
│ │                                           │ │
│ │ Type: SSD1306 OLED Display               │ │
│ │ Resolution: 128x64 pixels                │ │
│ │ Interface: I2C                            │ │
│ │ Address: 0x3C                            │ │
│ │                                           │ │
│ │ [View Datasheet] [Plugin Documentation]  │ │
│ └───────────────────────────────────────────┘ │
│                                                 │
│ ┌───────────────────────────────────────────┐ │
│ │ Test Interface                           │ │
│ │                                           │ │
│ │ [Text Input Field]                        │ │
│ │ ┌─────────────────────────────────────┐  │ │
│ │ │ Type text to display on LCD...      │  │ │
│ │ └─────────────────────────────────────┘  │ │
│ │                                           │ │
│ │ [Send to Display] [Clear] [Test Pattern] │ │
│ │                                           │ │
│ │ Status: Connected ✓                       │ │
│ └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Tab Sections

#### 1. Device Info Tab
- Device name and type
- Specifications
- Datasheet link
- Plugin information
- Connection status

#### 2. Test Tab
- Device-specific test interface
- Real-time interaction
- Example for LCD: Text input → Display on screen
- Example for sensor: Read values, show graph

#### 3. Config Tab
- Device configuration options
- Settings (if applicable)
- Calibration (if applicable)

#### 4. Plugin Tab
- Current plugin status
- Load custom plugin
- Plugin documentation
- Create new plugin (template)

---

## Device Selection Flow

### Scenario 1: Known Device (Plugin Exists)
1. User scans → sees `0x3C`
2. System suggests: "SSD1306 OLED"
3. User clicks `0x3C` → Device tab opens
4. System auto-detects: "SSD1306 OLED detected"
5. Plugin loads automatically
6. Test interface appears

### Scenario 2: Multiple Suggestions
1. User scans → sees `0x68`
2. System suggests: "MPU6050, MPU6500, or DS3231"
3. User clicks `0x68` → Device tab opens
4. Dropdown appears: "Select device:"
   - MPU6050 (IMU)
   - MPU6500 (IMU)
   - DS3231 (RTC)
   - Unknown
5. User selects → Plugin loads (if available)

### Scenario 3: Unknown Device (No Plugin)
1. User scans → sees `0x50`
2. System suggests: "Unknown device"
3. User clicks `0x50` → Device tab opens
4. Shows: "No plugin available"
5. Options:
   - "Search for plugin" (community plugins)
   - "Create custom plugin" (template)
   - "Load plugin file" (from disk)

---

## Plugin System Design

### Plugin File Structure

```python
# devices/ssd1306.py
from devices.base import DevicePlugin

class SSD1306Plugin(DevicePlugin):
    """SSD1306 OLED Display Plugin"""
    
    # Device identification
    addresses = [0x3C, 0x3D]
    name = "SSD1306"
    manufacturer = "Solomon Systech"
    description = "128x64 OLED Display"
    
    def detect(self, bus, address):
        """Try to detect if this is SSD1306"""
        try:
            # Try to read device ID register
            # Return True if detected
            pass
        except:
            return False
    
    def get_test_ui(self):
        """Return test interface widget"""
        return SSD1306TestWidget(self.bus, self.address)
    
    def get_info(self):
        """Return device information"""
        return {
            "name": self.name,
            "resolution": "128x64",
            "interface": "I2C",
            "datasheet": "https://..."
        }
```

### Test Widget Example (LCD)

```python
class SSD1306TestWidget(QWidget):
    def __init__(self, bus, address):
        # Text input field
        self.text_input = QLineEdit()
        self.text_input.textChanged.connect(self.update_display)
        
        # Buttons
        self.send_button = QPushButton("Send to Display")
        self.clear_button = QPushButton("Clear")
        
        # Real-time update as user types
        self.text_input.textChanged.connect(self.update_display)
```

---

## User Adds Custom Plugin

### Option 1: Load Plugin File
1. Click "Load Plugin" button
2. File dialog opens
3. User selects `.py` file
4. System validates plugin
5. Plugin loads and appears in device tab

### Option 2: Create from Template
1. Click "Create Plugin" button
2. System shows template:
   ```python
   from devices.base import DevicePlugin
   
   class MyDevicePlugin(DevicePlugin):
       addresses = [0x??]  # User fills in
       name = "My Device"
       
       def get_test_ui(self):
           # User implements test interface
           pass
   ```
3. User edits template
4. Saves to `devices/my_device.py`
5. Plugin loads automatically

### Option 3: Download Community Plugin
1. Click "Search Plugins"
2. Shows list of available plugins
3. User selects and downloads
4. Plugin installs automatically

---

## Example: LCD Text Display

### UI Design
```
┌─────────────────────────────────────┐
│ Text to Display on LCD              │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ Hello World!                    │ │ ← User types here
│ └─────────────────────────────────┘ │
│                                     │
│ [Send] [Clear] [Test Pattern]      │
│                                     │
│ Preview (128x64):                  │
│ ┌─────────────────────────────┐   │
│ │                             │   │
│ │   Hello World!              │   │ ← Real-time preview
│ │                             │   │
│ └─────────────────────────────┘   │
│                                     │
│ Status: ✓ Connected                 │
└─────────────────────────────────────┘
```

### Real-time Updates
- As user types, preview updates
- "Send" button sends to actual LCD
- "Clear" clears both input and LCD
- "Test Pattern" shows demo pattern

---

## Implementation Details

### Tab Management
- Device tabs are **dynamic** (created when device opened)
- Each device gets its own tab
- Tabs can be closed independently
- Main "Hardware" tab always available

### Plugin Loading
```python
# When user opens device
def open_device(address):
    # 1. Identify device
    suggestions = device_registry.lookup(address)
    
    # 2. Show device tab
    tab = DeviceTab(address, suggestions)
    
    # 3. If plugin exists, load it
    plugin = plugin_loader.load_for_address(address)
    if plugin:
        tab.set_plugin(plugin)
    else:
        tab.show_plugin_options()
```

### Plugin Discovery
- Check `devices/` directory for plugins
- Each plugin file = one device type
- Plugins auto-register on load
- User plugins in `devices/user/` directory

---

## Benefits

✅ **Intuitive**: Click device → get device tab
✅ **Flexible**: User selects exact device
✅ **Extensible**: Easy to add custom plugins
✅ **Interactive**: Real-time testing (type → see on LCD)
✅ **Educational**: Learn how devices work
✅ **Practical**: Actually test your hardware

