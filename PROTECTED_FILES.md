# Protected Files

## Overview

Protected files are core application files that must be modified with extreme care. Features should avoid modifying these files directly, and when modifications are necessary, they must be minimal and non-breaking.

## Protected Files List

### Critical (No Changes Without Approval)

1. **`device_panel.py`**
   - Main application entry point
   - Allowed: Optional imports with try/except, feature flag checks
   - Not allowed: Breaking changes, removal of functionality

2. **`ui/main_window.py`**
   - Core UI structure
   - Allowed: Optional tab/widget loading with feature flags
   - Not allowed: Breaking changes to existing UI, removal of tabs

3. **`hardware/gpio_manager.py`**
   - GPIO hardware manager
   - Allowed: Read-only access from features
   - Not allowed: Modification of existing methods, breaking API changes

4. **`hardware/adc_manager.py`**
   - ADC hardware manager
   - Allowed: Read-only access from features
   - Not allowed: Modification of existing methods, breaking API changes

5. **`hardware/i2c_scanner.py`**
   - I2C scanner
   - Allowed: Read-only access from features
   - Not allowed: Modification of scanning logic

6. **`config/pins.py`**
   - Pin definitions
   - Allowed: Read-only access
   - Not allowed: Any modifications (hardware-specific)

### Semi-Protected (Changes Require Testing)

1. **`config/device_config.py`**
   - Device system configuration
   - Allowed: Adding new config options
   - Not allowed: Removing existing options

2. **`devices/base.py`**
   - Device plugin base class
   - Allowed: Adding optional methods
   - Not allowed: Breaking changes to required methods

## Modification Rules

### Rule 1: Feature Flags

All modifications to protected files must be behind feature flags:

```python
# In device_panel.py
if config.feature_flags.ENABLE_POWER_PROFILER:
    try:
        from hardware.power_measurement import PowerMeasurementManager
        hardware.power_measurement = PowerMeasurementManager()
    except Exception as e:
        print(f"Power profiler not available: {e}")
```

### Rule 2: Try/Except Blocks

All feature code in protected files must be in try/except:

```python
try:
    # Feature code
    pass
except Exception as e:
    # Graceful degradation
    print(f"Feature not available: {e}")
```

### Rule 3: No Breaking Changes

- Never remove existing functionality
- Never change existing method signatures
- Never remove existing imports
- Maintain backward compatibility

### Rule 4: Minimal Changes

- Only add code, don't modify existing code
- Use optional parameters, not required ones
- Extend, don't replace

## Checking Protected Files

Before committing, run:

```bash
python scripts/check_protected_files.py
```

This script will:
- Check if protected files were modified
- Verify feature flags are used
- Verify try/except blocks
- Report any violations

## Approval Process

If you must modify a protected file:

1. Document why the change is necessary
2. Ensure feature flag is used
3. Add try/except blocks
4. Test that app works with feature disabled
5. Test that app works with feature enabled
6. Get approval (if required)
7. Update this document if adding new protected files

## Feature Development Best Practices

### Do This

```python
# In your feature code
from hardware.gpio_manager import GPIOManager

# Use existing hardware manager
hardware.gpio.set_led(1, True)  # OK - using existing API
```

### Don't Do This

```python
# Modifying protected file directly
# In hardware/gpio_manager.py
def new_feature_method(self):  # DON'T - modifying protected file
    pass
```

### Instead, Do This

```python
# Create new file for feature
# In hardware/power_measurement.py (new file)
class PowerMeasurementManager:
    def __init__(self, gpio_manager):
        self.gpio = gpio_manager  # Use existing manager
        # Add new functionality here
```

## Testing Protected Files

When modifying protected files:

1. Test with feature disabled (should work normally)
2. Test with feature enabled (should work with feature)
3. Test with feature enabled but hardware unavailable (graceful degradation)
4. Run full test suite
5. Test on actual hardware (if possible)

## Adding New Protected Files

If you add a new core file that should be protected:

1. Add it to this list
2. Document why it's protected
3. Document allowed modifications
4. Update check script

## Violations

If protected file rules are violated:

1. CI will fail
2. Merge will be blocked
3. Fix violations before merging
4. Update documentation if needed

