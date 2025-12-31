# Smart Suggestions Feature Branch

## Project Overview

The Smart Suggestions feature automatically detects connected sensors and displays, then suggests applications that combine them in useful ways. For example, detecting a temperature sensor and LCD suggests a thermometer app, or detecting an accelerometer and LCD suggests a game.

## Branch Relationships

- **Source**: Created from `dev` branch
- **Destination**: Merges to `dev` when complete
- **Dependencies**: Uses device detection system
- **Isolation**: Works independently, doesn't break other features

## High-Level Plan

### Core Functionality

1. **Device Detection**
   - Scan I2C buses for devices
   - Identify device types (sensor, display, etc.)
   - Detect device combinations
   - Track device capabilities

2. **Suggestion Engine**
   - Rule-based suggestion system
   - Pattern matching (sensor + display = app)
   - Suggestion ranking
   - Context-aware suggestions

3. **Suggested Apps**
   - Thermometer (temp sensor + LCD)
   - Accelerometer game (IMU + LCD)
   - Data logger (sensor + storage)
   - Dashboard (multiple sensors + display)
   - Custom apps framework

4. **User Interface**
   - Suggestions displayed in device tabs
   - One-click app launch
   - App store interface
   - App management

### Architecture

- **Detection**: Uses existing I2C scanner and device registry
- **Suggestions**: Rule-based pattern matching
- **Apps**: Small, focused applications
- **Framework**: Extensible app framework

## Development Rules

### Protected Files

- Do NOT modify: `device_panel.py`, `ui/main_window.py`, `hardware/*.py`
- Use feature flags: `ENABLE_SMART_SUGGESTIONS`
- Use try/except: All feature code must handle failures gracefully
- Extend, don't modify: Use existing device detection

### Code Organization

- Feature code in: `features/smart_suggestions/`
- Suggestion engine: `features/smart_suggestions/suggestion_engine.py`
- App framework: `features/smart_suggestions/app_framework.py`
- Suggested apps: `features/smart_suggestions/apps/`
- Tests in: `tests/test_smart_suggestions.py`

### Testing Requirements

- Unit tests for suggestion engine
- Unit tests for pattern matching
- Unit tests for app framework
- Integration tests with device detection
- End-to-end tests
- Visual tests (human verification)

### Merge Requirements

- All tests must pass
- Feature flag works (enabled and disabled)
- No breaking changes to core
- Documentation updated

## Success Criteria

Feature is complete when:

1. Devices are detected correctly
2. Suggestions are accurate and useful
3. Apps launch correctly
4. App framework is extensible
5. UI is intuitive
6. All tests pass
7. App works with feature disabled
8. App works with feature enabled

## Dependencies & Integration

### Dependencies

- Device detection system: `I2CScanner`, `DeviceRegistry`
- Device plugins: For device identification
- Feature flag: `ENABLE_SMART_SUGGESTIONS`

### Integration Points

- Main app: Optional suggestions in device tabs
- Device system: Uses existing device detection
- UI: Adds suggestion widgets to device tabs

### Cross-Feature

- Independent feature
- Doesn't conflict with other features
- Can work alongside other features

## Testing Requirements

### Unit Tests

- Suggestion engine tests
- Pattern matching tests
- App framework tests
- Device combination detection tests

### Integration Tests

- Suggestions with real device detection
- App launch tests
- UI integration tests

### End-to-End Tests

- App launches with feature enabled
- App launches with feature disabled
- Suggestions appear correctly
- Apps launch and work

### RPi Testing

- **Assigned RPi**: RPi 1 (192.168.101)
- **Username**: `a`
- **Password**: `1`
- **Deploy**: `./scripts/deploy-to-pi.sh -b feature/smart-suggestions -h 192.168.101 -u a`
- **Setup**: `./scripts/setup-pi-for-branch.sh -h 192.168.101 -b feature/smart-suggestions -u a`
- See `RPI_ASSIGNMENTS.md` for details

## Implementation Details

### Suggestion Rules

```python
rules = [
    {"devices": ["temp_sensor", "lcd"], "suggestion": "thermometer"},
    {"devices": ["accelerometer", "lcd"], "suggestion": "game"},
    {"devices": ["sensor", "display"], "suggestion": "dashboard"},
]
```

### App Framework

- Simple app interface
- Lifecycle management (start, stop, update)
- Hardware access via managers
- UI components

### Suggested Apps

- **Thermometer**: Temp sensor + LCD
- **Accelerometer Game**: IMU + LCD
- **Data Logger**: Sensor + storage
- **Dashboard**: Multiple sensors + display
- **Custom**: User-created apps

## Common Issues & Solutions

### Issue: Suggestions not appearing

**Solution**: Check device detection, verify device registry, check suggestion rules

### Issue: App doesn't launch

**Solution**: Check app framework, verify hardware access, check app code

### Issue: Suggestions inaccurate

**Solution**: Refine suggestion rules, improve pattern matching, test combinations

## Related Branches

- **dev**: Integration branch (merge target)
- **feature/power-profiler**: Independent feature
- **feature/test-sequences**: Independent feature

## Notes

- Focus on user experience
- Make suggestions helpful, not annoying
- Keep apps simple and focused
- Support extensibility
- Encourage exploration

