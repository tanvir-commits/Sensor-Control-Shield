# Decision Log

This document records key architectural and design decisions, along with the reasoning behind them. This helps new agents understand *why* things are the way they are, not just *what* they are.

## Table of Contents

1. [Architecture Decisions](#architecture-decisions)
2. [Technology Choices](#technology-choices)
3. [Development Workflow](#development-workflow)
4. [Testing Strategy](#testing-strategy)
5. [Hardware Abstraction](#hardware-abstraction)

---

## Architecture Decisions

### 1. Plugin-Based Device System

**Decision**: Use a plugin-based architecture for device support instead of hardcoding each device.

**Reasoning**:
- **Extensibility**: New devices can be added without modifying core code
- **Isolation**: Device plugin failures don't crash the app
- **Maintainability**: Each device is self-contained
- **Backward Compatibility**: Core app works even if device system fails to load

**Trade-offs**:
- Slightly more complex than hardcoding
- Requires plugin interface design
- **Chosen**: Complexity is worth the flexibility and safety

**Implementation**: See `devices/base.py` and `DEVICE_SYSTEM_PLAN.md`

---

### 2. Hardware Abstraction Layer

**Decision**: Separate hardware managers (`hardware/`) from UI (`ui/`) and device plugins (`devices/`).

**Reasoning**:
- **Separation of Concerns**: Hardware logic separate from presentation
- **Testability**: Can mock hardware for UI testing
- **Reusability**: Hardware managers can be used by features
- **Protection**: Hardware layer is read-only for features (prevents breaking changes)

**Trade-offs**:
- More files to navigate
- **Chosen**: Better organization and safety

**Implementation**: `hardware/gpio_manager.py`, `hardware/adc_manager.py`, etc.

---

### 3. Feature Flags for All Features

**Decision**: All new features must use feature flags and be optional.

**Reasoning**:
- **Safety**: App works even if feature code has bugs
- **Flexibility**: Can disable features without code changes
- **Testing**: Can test with features enabled/disabled
- **Production**: Can ship with features disabled until stable

**Trade-offs**:
- Slight overhead checking flags
- **Chosen**: Safety and flexibility are critical

**Implementation**: `config/feature_flags.py`

---

### 4. Protected Files System

**Decision**: Certain core files are "protected" and require special care to modify.

**Reasoning**:
- **Stability**: Core app functionality must not break
- **Coordination**: Multiple agents need to know what's safe to modify
- **Safety**: Prevents accidental breaking changes
- **Documentation**: Forces explicit documentation of changes

**Trade-offs**:
- Can slow down development slightly
- **Chosen**: Prevents catastrophic failures

**Implementation**: See `PROTECTED_FILES.md`

---

### 5. Branch Strategy: prod → dev → feature/*

**Decision**: Use hierarchical branch structure with integration branch.

**Reasoning**:
- **Stability**: `prod` always has stable code
- **Integration**: `dev` allows features to integrate before production
- **Isolation**: Features don't interfere with each other
- **Testing**: Can test features individually and together

**Trade-offs**:
- More branches to manage
- **Chosen**: Better organization and safety

**Implementation**: See `BRANCH_STRATEGY.md`

---

## Technology Choices

### 1. PySide6 (Qt6 for Python)

**Decision**: Use PySide6 for GUI instead of tkinter, PyQt5, or web-based UI.

**Reasoning**:
- **Modern**: Qt6 is modern and well-maintained
- **Performance**: Native performance, not web-based
- **Cross-platform**: Works on Linux (RPi) and development machines
- **Rich Widgets**: Better widgets than tkinter
- **Free**: PySide6 is LGPL (free for our use)

**Trade-offs**:
- Larger dependency than tkinter
- **Chosen**: Better user experience and modern API

---

### 2. gpiozero for GPIO Control

**Decision**: Use `gpiozero` library instead of direct `RPi.GPIO` or `gpiod`.

**Reasoning**:
- **Simplicity**: Higher-level API, easier to use
- **Safety**: Built-in protections and abstractions
- **Documentation**: Well-documented
- **Compatibility**: Works on RPi and can be mocked for testing

**Trade-offs**:
- Slightly less control than direct GPIO
- **Chosen**: Easier to use and maintain

---

### 3. smbus2 for I2C

**Decision**: Use `smbus2` for I2C communication.

**Reasoning**:
- **Modern**: Better than old `smbus`
- **Pythonic**: Clean Python API
- **Compatibility**: Works with standard Linux I2C drivers
- **Error Handling**: Better error messages

**Trade-offs**:
- Requires I2C kernel support (standard on RPi)
- **Chosen**: Best balance of simplicity and functionality

---

### 4. Plugin System: ABC (Abstract Base Classes)

**Decision**: Use Python's `abc` module for plugin interface.

**Reasoning**:
- **Standard**: Built into Python, no extra dependencies
- **Clear Contracts**: Forces plugins to implement required methods
- **Type Safety**: Can use type hints effectively
- **Documentation**: Clear interface definition

**Trade-offs**:
- Slightly more verbose than duck typing
- **Chosen**: Better safety and clarity

---

## Development Workflow

### 1. Ubuntu Testing First, Then RPi

**Decision**: Test on Ubuntu development machine first, only use RPi for hardware-specific testing.

**Reasoning**:
- **Speed**: Faster iteration on Ubuntu
- **Convenience**: Don't need RPi for every change
- **Cost**: Can test UI/logic without hardware
- **Efficiency**: Catch most bugs before hardware testing

**Trade-offs**:
- Some hardware-specific bugs only show on RPi
- **Chosen**: Much faster development cycle

**Implementation**: Mock hardware for Ubuntu testing, real hardware on RPi

---

### 2. Separate RPis for Feature Testing

**Decision**: Use separate RPis for each feature branch testing.

**Reasoning**:
- **Isolation**: Features don't interfere with each other
- **Parallel Testing**: Can test multiple features simultaneously
- **Stability**: One feature's issues don't affect others
- **Flexibility**: Can configure each RPi differently

**Trade-offs**:
- Need multiple RPis (but they're relatively cheap)
- **Chosen**: Better isolation and parallel work

---

### 3. Feature Folders for Code Organization

**Decision**: Put feature code in `features/` directory, not mixed with core code.

**Reasoning**:
- **Organization**: Clear separation of features
- **Isolation**: Features don't clutter core code
- **Maintainability**: Easy to find feature code
- **Removability**: Can remove features easily if needed

**Trade-offs**:
- Slightly more directory navigation
- **Chosen**: Better organization

---

## Testing Strategy

### 1. Mock Hardware for Unit Tests

**Decision**: Use mock hardware objects for unit and integration tests.

**Reasoning**:
- **Speed**: Tests run fast without hardware
- **Reliability**: Tests don't depend on hardware availability
- **CI/CD**: Can run tests in CI without hardware
- **Isolation**: Test logic separately from hardware

**Trade-offs**:
- Need to ensure mocks match real hardware behavior
- **Chosen**: Essential for automated testing

---

### 2. Feature Flags for Testing

**Decision**: Test features both enabled and disabled.

**Reasoning**:
- **Safety**: Ensure app works with features disabled
- **Integration**: Test features work together
- **Regression**: Catch regressions when features change

**Trade-offs**:
- More test cases
- **Chosen**: Better coverage and safety

---

## Hardware Abstraction

### 1. Hardware Managers Pattern

**Decision**: Create separate manager classes for each hardware subsystem (GPIO, ADC, I2C, etc.).

**Reasoning**:
- **Single Responsibility**: Each manager handles one subsystem
- **Testability**: Can test/manage each subsystem independently
- **Reusability**: Features can use managers without duplicating code
- **Protection**: Managers are read-only for features (prevents breaking changes)

**Trade-offs**:
- More classes to maintain
- **Chosen**: Better organization and safety

---

### 2. Read-Only Hardware Access for Features

**Decision**: Features can read from hardware managers but not modify them.

**Reasoning**:
- **Safety**: Prevents features from breaking core hardware functionality
- **Stability**: Core hardware behavior remains predictable
- **Coordination**: Multiple features can use hardware without conflicts

**Trade-offs**:
- Features can't directly modify hardware (must go through managers)
- **Chosen**: Safety and stability are more important

---

## UI Design Decisions

### 1. Tabbed Interface for Devices

**Decision**: Use tabs to separate hardware view from device-specific views.

**Reasoning**:
- **Organization**: Clear separation of concerns
- **Scalability**: Can add more tabs without cluttering
- **User Experience**: Easy to switch between views
- **Optional**: Can fall back to single view if device system unavailable

**Trade-offs**:
- Slightly more complex than single view
- **Chosen**: Better organization and UX

---

### 2. Status Bar for System Health

**Decision**: Show system status (power, I2C, SPI, IP) in a top status bar.

**Reasoning**:
- **Visibility**: Always visible system state
- **Quick Diagnosis**: Easy to see if something is wrong
- **Professional**: Looks more polished

**Trade-offs**:
- Takes up some screen space
- **Chosen**: Better user experience

---

## Future Considerations

### Decisions to Revisit

1. **Web-based UI**: Consider if we need remote access (currently native GUI)
2. **Database for Device Registry**: Currently in-memory, consider persistence if needed
3. **Plugin Marketplace**: Consider if we want external plugins (currently internal only)
4. **Multi-language Support**: Currently English only, consider i18n if needed

---

## How to Use This Document

- **New Agents**: Read this to understand why things are designed this way
- **Making Changes**: Consider if your change conflicts with these decisions
- **Documenting**: Add new decisions here when making significant architectural choices
- **Debating**: Use this to understand trade-offs that were already considered

---

## Contributing to This Document

When making a significant architectural decision:

1. Document the decision
2. Explain the reasoning
3. List trade-offs considered
4. Explain why this choice was made
5. Update this document

This helps future agents (and yourself) understand the context.

