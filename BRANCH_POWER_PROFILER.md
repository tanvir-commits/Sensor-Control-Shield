# Power Profiler Feature Branch

## Project Overview

The Power Profiler feature enables comprehensive power measurement and automated testing sequences. It supports multiple I2C buses with user-defined names (LCD, MCU, Motor, etc.), provides sequence-based testing with GPIO/ADC/UART control, and includes event-triggered measurements.

## Branch Relationships

- **Source**: Created from `dev` branch
- **Destination**: Merges to `dev` when complete
- **Dependencies**: May use `feature/test-sequences` for sequence engine
- **Isolation**: Works independently, doesn't break other features

## High-Level Plan

### Core Functionality

1. **Power Measurement**
   - Support INA260 current sensors
   - Multiple I2C buses with user naming
   - Real-time current, voltage, and power measurement
   - Calibration and accuracy features

2. **Device Control**
   - GPIO toggle (wake MCU, control devices)
   - UART commands (send commands to MCU)
   - ADC sampling (voltage monitoring)
   - Event-triggered measurements

3. **Sequence Engine**
   - Define test sequences (GPIO, UART, ADC, measurement)
   - Execute sequences with timing
   - Log results and generate reports
   - Save/load sequences

4. **User Interface**
   - Separate window/tab (not in device tabs)
   - Real-time power graphs
   - Sequence builder (visual or script-based)
   - Results visualization

### Architecture

- **Hardware**: INA260 sensors on multiple I2C buses
- **UI**: Standalone window/tab for test automation focus
- **Integration**: Uses existing hardware managers (GPIO, ADC, I2C)
- **Isolation**: Feature flag controlled, doesn't break app when disabled

## Development Rules

### Protected Files

- Do NOT modify: `device_panel.py`, `ui/main_window.py`, `hardware/*.py`
- Use feature flags: `ENABLE_POWER_PROFILER`
- Use try/except: All feature code must handle failures gracefully
- Extend, don't modify: Use existing hardware managers, don't change them

### Code Organization

- Feature code in: `features/power_profiler/`
- Hardware manager: `hardware/power_measurement.py` (new file)
- UI component: `ui/sections/power_profiler_section.py` (new file)
- Tests in: `tests/test_power_profiler.py`

### Testing Requirements

- Unit tests for power measurement
- Unit tests for sequence engine
- Integration tests with hardware managers
- End-to-end tests (app launch, feature works)
- Visual tests (human verification)

### Merge Requirements

- All tests must pass
- Feature flag works (enabled and disabled)
- No breaking changes to core
- Documentation updated

## Success Criteria

Feature is complete when:

1. INA260 sensors detected and measured correctly
2. Multiple buses supported with user naming
3. Sequences execute correctly
4. GPIO/UART/ADC control works
5. Event-triggered measurements work
6. UI is functional and responsive
7. All tests pass
8. App works with feature disabled
9. App works with feature enabled

## Dependencies & Integration

### Dependencies

- Existing hardware managers: `GPIOManager`, `ADCManager`, `I2CScanner`
- INA260 sensor hardware
- Feature flag: `ENABLE_POWER_PROFILER`

### Integration Points

- Main app: Optional tab/window loading via feature flag
- Hardware: Uses existing managers, doesn't modify them
- Config: Adds `config/power_config.py` for power profiler settings

### Cross-Feature

- May use `feature/test-sequences` sequence engine (if available)
- Doesn't conflict with other features
- Can work alongside other features

## Testing Requirements

### Unit Tests

- Power measurement manager tests
- INA260 sensor detection
- Multi-bus support
- Sequence engine tests
- Sequence execution tests

### Integration Tests

- Power profiler with GPIO manager
- Power profiler with ADC manager
- Power profiler with I2C scanner
- Full sequence execution

### End-to-End Tests

- App launches with power profiler enabled
- App launches with power profiler disabled
- Power profiler tab/window appears
- Sequences execute correctly
- Measurements are accurate

### Visual Tests (Human)

- UI renders correctly
- Graphs display properly
- Sequence builder is intuitive
- Results are clear

### RPi Testing

- **Assigned RPi**: RPi 2 (192.168.102)
- **Username**: `pi` (verify if different)
- **Deploy**: `./scripts/deploy-to-pi.sh -b feature/power-profiler -h 192.168.102 -u pi`
- **Setup**: `./scripts/setup-pi-for-branch.sh -h 192.168.102 -b feature/power-profiler -u pi`
- See `RPI_ASSIGNMENTS.md` for details

## Implementation Details

### Hardware Support

- INA260 current sensor (I2C address 0x40, 0x41, etc.)
- Multiple sensors on different I2C buses
- User-defined bus names (LCD, MCU, Motor, etc.)

### Sequence Types

- GPIO toggle (set high/low, with timing)
- UART send/receive (commands, responses)
- ADC read (channel, sample rate)
- Power measurement (triggered or continuous)
- Delay (fixed or variable)
- Conditional (if/then based on measurements)

### UI Components

- Power measurement display (current, voltage, power)
- Real-time graphs
- Sequence builder interface
- Sequence execution controls
- Results table and graphs

## Common Issues & Solutions

### Issue: INA260 not detected

**Solution**: Check I2C bus, address, wiring, pull-up resistors

### Issue: Measurements inaccurate

**Solution**: Calibrate sensor, check shunt resistor value, verify connections

### Issue: Sequence execution fails

**Solution**: Check hardware connections, verify sequence definition, check timing

### Issue: Feature breaks app when disabled

**Solution**: Ensure all code in try/except, feature flag checks work correctly

## Related Branches

- **dev**: Integration branch (merge target)
- **feature/test-sequences**: May provide sequence engine
- **feature/smart-suggestions**: Independent feature

## Notes

- Focus on test automation use case
- UI should be separate window/tab for focus
- Support multiple buses for complex systems
- Event-triggered measurements are key feature
- Keep sequences flexible and powerful

