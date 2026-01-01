# QA Test Sequences Feature Branch

## Project Overview

The **QA Test Sequences** feature provides a **device-agnostic QA test execution layer** for embedded devices. It allows users to run repeatable QA tests on MCUs (DUTs) by orchestrating test sequences from the Raspberry Pi via UART and GPIO, while the MCU runs a minimal QA Agent that executes numbered tasks and enters defined sleep modes.

**Key Design Principle**: Intelligence lives on the Pi, firmware remains simple.

See `QA_Test_Sequences_Design.md` for complete design details.

## Branch Relationships

- **Source**: Created from `dev` branch
- **Destination**: Merges to `dev` when complete
- **Used by**: Power Profiler and other features
- **Isolation**: Works independently, reusable by other features

## High-Level Plan

### Core Functionality

1. **DUT Profile Setup**
   - Configure UART port and baud rate
   - Configure GPIO for WAKE and RESET
   - Document what each task (TASK 1-10) does
   - No MCU model selection required (MCU-agnostic)

2. **Sequence Builder**
   - Define sequences using high-level actions:
     - Trigger Task N (1-10)
     - Send UART command
     - Enter sleep mode (Active, Light Sleep, Deep Sleep, Shutdown)
     - Wait (ms/seconds/minutes)
     - Loop/repeat
     - Pass/fail conditions
   - Save/load sequences (JSON/YAML format)

3. **Sequence Execution**
   - Execute sequences one command at a time
   - Each command requires OK/ERR response
   - Wake, sleep, and reset events logged
   - Failures stop or flag the sequence
   - Timing data collection

4. **Results & Reporting**
   - Pass/Fail outcomes
   - Failure reasons
   - Timing data
   - Execution logs
   - Exportable QA records

### Architecture

- **MCU-Agnostic**: Works with any MCU via standardized UART protocol
- **Pi Orchestrates**: Pi decides what, when, and why
- **MCU Executes Primitives**: MCU runs simple QA Agent with 10 task slots
- **Separation of Concerns**: Intelligence on Pi, simplicity on MCU

## Development Rules

### Protected Files

- Do NOT modify: `device_panel.py`, `ui/main_window.py`, `hardware/*.py`
- Use feature flags: `ENABLE_TEST_SEQUENCES`
- Use try/except: All feature code must handle failures gracefully
- Extend, don't modify: Use existing hardware managers

### Code Organization

- Feature code in: `features/test_sequences/`
- Core engine: `features/test_sequences/qa_engine.py`
- UART manager: `features/test_sequences/uart_manager.py` (or use existing if available)
- DUT profile: `features/test_sequences/dut_profile.py`
- Sequence builder: `features/test_sequences/sequence_builder.py`
- UI components: `ui/sections/qa_test_sequences_section.py`
- Tests in: `tests/test_test_sequences.py`

### Testing Requirements

- Unit tests for sequence engine
- Unit tests for each step type
- Integration tests with hardware managers
- End-to-end tests
- Visual tests (human verification)

### Merge Requirements

- All tests must pass
- Feature flag works (enabled and disabled)
- No breaking changes to core
- API is stable and documented
- Documentation updated

## Success Criteria

Feature is complete when:

1. DUT profiles can be configured (UART, GPIO, task documentation)
2. Sequences can be defined and saved
3. Sequences execute correctly via UART
4. Task execution (TASK 1-10) works
5. Sleep control works (Active, Light Sleep, Deep Sleep, Shutdown)
6. Wake via GPIO works
7. Timing is accurate
8. Error handling works (OK/ERR responses)
9. Results are logged correctly (Pass/Fail, timing, logs)
10. QA records are exportable
11. All tests pass
12. App works with feature disabled
13. App works with feature enabled
14. Works with any MCU (MCU-agnostic)

## Dependencies & Integration

### Dependencies

- Existing hardware managers: `GPIOManager` (for WAKE/RESET GPIO)
- UART communication: Need UART manager or implement in feature
- Feature flag: `ENABLE_TEST_SEQUENCES`
- MCU QA Agent: Users provide firmware template (not part of this feature)

### Integration Points

- Main app: Optional loading via feature flag
- Hardware: Uses `GPIOManager` for WAKE/RESET, UART for communication
- UART: May need to create UART manager or use existing if available
- Other features: Independent feature, may be used by Power Profiler later

### Cross-Feature

- Independent feature focused on QA test execution
- Doesn't conflict with other features
- May be used by Power Profiler for power-aware sequences (future)

## Testing Requirements

### Unit Tests

- Sequence engine tests
- Step type tests (GPIO, ADC, UART, delay, conditional)
- Sequence save/load tests
- Validation tests

### Integration Tests

- Sequence execution with hardware managers
- Error handling tests
- Timing accuracy tests

### End-to-End Tests

- App launches with feature enabled
- App launches with feature disabled
- Sequences execute correctly
- Results are accurate

## Implementation Details

### UART Protocol (MCU Side)

The MCU QA Agent must support:
- `TASK N` - Execute task N (1-10)
- `SLEEP <mode>` - Enter sleep mode (ACTIVE, LIGHT, DEEP, SHUTDOWN)
- `WAKE` - Wake from sleep (via GPIO, but acknowledge via UART)
- `RESET` - Reset MCU (via GPIO)
- Responses: `OK` or `ERR <reason>`

### Sequence Format

```json
{
  "name": "LCD Test",
  "steps": [
    {"type": "wake", "gpio": 5},
    {"type": "task", "number": 1, "description": "LCD_INIT"},
    {"type": "wait", "duration": 200, "unit": "ms"},
    {"type": "task", "number": 2, "description": "LCD_ON"},
    {"type": "wait", "duration": 2, "unit": "s"},
    {"type": "task", "number": 3, "description": "LCD_BITMAP", "param": 1},
    {"type": "wait", "duration": 5, "unit": "s"},
    {"type": "task", "number": 4, "description": "LCD_OFF"},
    {"type": "sleep", "mode": "DEEP", "duration": 10, "unit": "minutes"},
    {"type": "repeat", "count": 100}
  ]
}
```

### Step Types

- **wake**: Wake DUT via GPIO
- **task**: Execute TASK N (1-10) via UART
- **sleep**: Command sleep mode via UART
- **wait**: Delay (ms/seconds/minutes)
- **repeat**: Loop sequence
- **pass/fail**: Conditional logic based on responses

### DUT Profile Format

```json
{
  "name": "STM32U5 DUT",
  "uart": {
    "port": "/dev/ttyUSB0",
    "baud": 115200
  },
  "gpio": {
    "wake": 5,
    "reset": 6
  },
  "tasks": {
    "1": "LCD_INIT",
    "2": "LCD_ON",
    "3": "LCD_BITMAP",
    "4": "LCD_OFF",
    ...
  }
}
```

## Common Issues & Solutions

### Issue: Sequence execution fails

**Solution**: Check sequence definition, verify hardware connections, check timing

### Issue: Timing inaccurate

**Solution**: Use system timers, account for execution time, test timing accuracy

### Issue: Step type not working

**Solution**: Check step definition, verify hardware manager, test step in isolation

## Related Branches

- **dev**: Integration branch (merge target)
- **feature/power-profiler**: May use this feature
- **feature/smart-suggestions**: Independent feature

## Notes

- **MCU-Agnostic**: Don't require MCU selection in UI
- **Simple MCU Side**: MCU only executes primitives, no script parsing
- **Pi Orchestrates**: All intelligence and decision-making on Pi
- **QA Focus**: This is a QA test executive, not a debugger or power instrument
- **Task Numbers**: Use TASK 1-10, not named tasks (keeps protocol simple)
- **Sleep Control**: Always via UART, wake via GPIO
- **Documentation**: Users document what each task does in DUT profile

## Non-Goals

This feature does **not**:
- Generate CubeMX `.ioc` files
- Flash firmware
- Inspect LCD pixels or SPI traffic
- Replace power instruments
- Parse scripts on MCU

See `QA_Test_Sequences_Design.md` for complete design rationale.

