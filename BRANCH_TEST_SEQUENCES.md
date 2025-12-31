# Test Sequences Feature Branch

## Project Overview

The Test Sequences feature provides a general-purpose sequence engine for defining and executing test sequences. It can be used by the Power Profiler and other features for automated testing. The engine supports GPIO, ADC, UART, and custom actions with timing and conditional logic.

## Branch Relationships

- **Source**: Created from `dev` branch
- **Destination**: Merges to `dev` when complete
- **Used by**: Power Profiler and other features
- **Isolation**: Works independently, reusable by other features

## High-Level Plan

### Core Functionality

1. **Sequence Definition**
   - Define sequence steps (GPIO, ADC, UART, delay, conditional)
   - Sequence metadata (name, description, version)
   - Save/load sequences (JSON/YAML format)
   - Sequence validation

2. **Sequence Execution**
   - Execute sequences with timing
   - Handle errors and timeouts
   - Log execution results
   - Support parallel sequences (if needed)

3. **Step Types**
   - GPIO actions (set, toggle, read)
   - ADC actions (read channel, sample rate)
   - UART actions (send, receive, wait for response)
   - Delay actions (fixed, variable, conditional)
   - Measurement actions (trigger measurement)
   - Conditional actions (if/then/else)

4. **Integration API**
   - Simple API for other features to use
   - Callback support for custom actions
   - Event system for sequence events
   - Result reporting

### Architecture

- **Reusable**: Can be used by any feature
- **Extensible**: Easy to add new step types
- **Isolated**: Doesn't depend on specific features
- **Flexible**: Supports various test scenarios

## Development Rules

### Protected Files

- Do NOT modify: `device_panel.py`, `ui/main_window.py`, `hardware/*.py`
- Use feature flags: `ENABLE_TEST_SEQUENCES`
- Use try/except: All feature code must handle failures gracefully
- Extend, don't modify: Use existing hardware managers

### Code Organization

- Feature code in: `features/test_sequences/`
- Core engine: `features/test_sequences/sequence_engine.py`
- Step types: `features/test_sequences/steps/`
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

1. Sequences can be defined and saved
2. Sequences execute correctly
3. All step types work
4. Timing is accurate
5. Error handling works
6. Results are logged correctly
7. API is usable by other features
8. All tests pass
9. App works with feature disabled
10. App works with feature enabled

## Dependencies & Integration

### Dependencies

- Existing hardware managers: `GPIOManager`, `ADCManager`, `I2CScanner`
- Feature flag: `ENABLE_TEST_SEQUENCES`

### Integration Points

- Main app: Optional loading via feature flag
- Hardware: Uses existing managers
- Other features: Provides API for sequence execution

### Cross-Feature

- Used by: Power Profiler, future features
- Doesn't conflict with other features
- Can work alongside other features

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

### Sequence Format

```json
{
  "name": "GPIO Test",
  "steps": [
    {"type": "gpio", "action": "set", "pin": 1, "value": true},
    {"type": "delay", "duration": 1000},
    {"type": "gpio", "action": "set", "pin": 1, "value": false}
  ]
}
```

### Step Types

- **GPIO**: Set, toggle, read GPIO pins
- **ADC**: Read ADC channels with sample rate
- **UART**: Send commands, receive responses
- **Delay**: Fixed or variable delays
- **Measurement**: Trigger measurements
- **Conditional**: If/then/else logic

### API for Other Features

```python
from features.test_sequences import SequenceEngine

engine = SequenceEngine(hardware)
sequence = engine.load_sequence("test.json")
results = engine.execute(sequence)
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

- Focus on reusability
- Keep API simple and stable
- Support extensibility
- Document API thoroughly
- Test with multiple use cases

