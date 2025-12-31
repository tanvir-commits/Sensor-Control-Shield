# Testing Strategy

## Overview

Comprehensive testing ensures the application works correctly and features don't break each other. All code must be tested.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_core.py             # Core app smoke tests
├── test_hardware/           # Hardware manager tests
│   ├── test_gpio.py
│   ├── test_adc.py
│   └── test_i2c.py
├── test_features/           # Feature-specific tests
│   ├── test_power_profiler.py
│   ├── test_test_sequences.py
│   └── test_smart_suggestions.py
└── test_integration.py      # End-to-end integration tests
```

## Test Types

### 1. Unit Tests

Test individual components in isolation:

```python
def test_gpio_set_led():
    manager = GPIOManager()
    manager.set_led(1, True)
    assert manager.get_led(1) == True
```

**Requirements:**
- Test all public methods
- Test error cases
- Test edge cases
- Mock external dependencies

### 2. Integration Tests

Test components working together:

```python
def test_power_profiler_with_gpio():
    hardware = Hardware()
    profiler = PowerProfiler(hardware)
    profiler.start_measurement()
    hardware.gpio.set_led(1, True)
    # Verify measurement captured GPIO change
```

**Requirements:**
- Test feature with real hardware managers
- Test feature interactions
- Test error propagation

### 3. End-to-End Tests

Test full application flow:

```python
def test_app_launch_with_power_profiler():
    app = QApplication([])
    hardware = Hardware()
    window = MainWindow(hardware)
    # Verify window opens, power profiler tab exists
```

**Requirements:**
- Test app launches
- Test features load correctly
- Test features can be disabled
- Test no crashes

### 4. Visual Tests (Human Verification)

Some tests require human verification:

1. UI renders correctly
2. Graphs display properly
3. Colors and styling correct
4. Responsiveness feels good

**Process:**
1. Run automated tests
2. Launch app manually
3. Verify visually
4. Document in test results

## Test Requirements

### Coverage Requirements

- **New code**: Minimum 70% coverage
- **Core code**: Minimum 80% coverage
- **Critical paths**: 100% coverage

### Test Execution

**Before commit:**
```bash
pytest tests/ -v
```

**Before merge to dev:**
```bash
pytest tests/ -v --cov=. --cov-report=html
```

**CI/CD:**
- Runs on every push
- Must pass before merge
- Generates coverage report

## Test Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture
def mock_hardware():
    """Mock hardware for testing."""
    return MockHardware()

@pytest.fixture
def app():
    """Qt application for UI tests."""
    app = QApplication([])
    yield app
    app.quit()
```

## Feature Testing

### Testing with Feature Disabled

```python
def test_app_works_without_power_profiler():
    config.feature_flags.ENABLE_POWER_PROFILER = False
    app = create_app()
    # Verify app launches, no power profiler tab
    assert "Power Profiler" not in get_tab_names()
```

### Testing with Feature Enabled

```python
def test_app_works_with_power_profiler():
    config.feature_flags.ENABLE_POWER_PROFILER = True
    app = create_app()
    # Verify app launches, power profiler tab exists
    assert "Power Profiler" in get_tab_names()
```

### Testing Feature Isolation

```python
def test_feature_failure_doesnt_crash_app():
    # Simulate feature failure
    with patch('hardware.power_measurement.PowerMeasurementManager') as mock:
        mock.side_effect = Exception("Hardware not available")
        app = create_app()
        # Verify app still launches
        assert app.is_running()
```

## Hardware Testing

### Mock Hardware

For development and CI:

```python
class MockHardware:
    def __init__(self):
        self.gpio = MockGPIO()
        self.adc = MockADC()
```

### Real Hardware Testing

For final verification:

1. Test on actual Raspberry Pi
2. Test with real sensors
3. Test with real GPIO
4. Document hardware setup

## Test Data

### Test Sequences

Store test sequences in `tests/data/`:

```
tests/data/
├── sequences/
│   ├── simple_gpio.json
│   └── power_test.json
└── expected_results/
    └── power_test_expected.csv
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_power_profiler.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Integration Tests Only

```bash
pytest tests/test_integration.py -v
```

## CI/CD Testing

### GitHub Actions (if using GitHub)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/ -v
```

### Pre-commit Hooks

Run tests before commit:

```bash
pre-commit run --all-files
```

## Test Maintenance

### Keeping Tests Updated

- Update tests when adding features
- Update tests when fixing bugs
- Remove obsolete tests
- Refactor duplicate test code

### Test Documentation

- Document test purpose
- Document test data requirements
- Document hardware requirements
- Document known limitations

## AI Agent Testing

AI agents can:

1. **Generate tests**: Create test cases for new code
2. **Run tests**: Execute test suite
3. **Fix tests**: Update tests when code changes
4. **Analyze coverage**: Identify untested code

### Visual Verification

AI agents cannot verify visual aspects. Human must:

1. Review UI rendering
2. Verify graph accuracy
3. Check color schemes
4. Test user experience

## Success Criteria

Tests are successful when:

1. All automated tests pass
2. Coverage meets requirements
3. Integration tests pass
4. Visual verification complete
5. No regressions detected

