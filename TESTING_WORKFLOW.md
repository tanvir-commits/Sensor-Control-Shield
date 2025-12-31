# Testing Workflow

## Overview

This document outlines the testing workflow for the Device Panel project. Testing happens in two phases: **Ubuntu (development machine) first**, then **Raspberry Pi (hardware) when needed**.

## Testing Philosophy

### Ubuntu First, RPi When Needed

**Why**: 
- Faster iteration on Ubuntu
- Don't need hardware for UI/logic testing
- Catch most bugs before hardware testing
- More convenient for daily development

**When to use RPi**:
- Hardware-specific functionality (GPIO, I2C, ADC)
- Integration testing with real sensors
- Performance testing
- Final verification before merge

---

## Phase 1: Ubuntu Testing

### What to Test on Ubuntu

✅ **Unit Tests**
- Individual component tests
- Mock hardware objects
- Logic and algorithms
- Data structures

✅ **UI Tests**
- Window rendering
- Widget interactions
- Layout and styling
- User interactions

✅ **Integration Tests**
- Component interactions
- Feature integration
- Mock hardware scenarios
- Error handling

✅ **Code Quality**
- Linting
- Type checking
- Code coverage
- Documentation

### Running Tests on Ubuntu

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_power_profiler.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run app with mock hardware
python device_panel.py
```

### Mock Hardware

For Ubuntu testing, hardware is mocked:

```python
# Hardware managers use mocks when hardware unavailable
# GPIO: MockGPIO (simulates button presses, LED states)
# ADC: MockADC (returns test values)
# I2C: MockI2C (simulates device responses)
```

### Success Criteria for Ubuntu Testing

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] UI renders correctly
- [ ] App launches without errors
- [ ] Features work with mock hardware
- [ ] Code coverage meets requirements (70%+)
- [ ] No linting errors
- [ ] No type errors

---

## Phase 2: RPi Testing

### When to Test on RPi

- ✅ Hardware-specific functionality ready
- ✅ Ubuntu tests all pass
- ✅ Ready for hardware integration
- ✅ Need to verify real sensor behavior

### RPi Assignment

- **RPi 1** (192.168.101): `feature/smart-suggestions` testing
  - Username: `a`
  - Password: `1`
  - Purpose: Automatic app suggestion feature testing
  
- **RPi 2** (192.168.102): `feature/power-profiler` testing
  - Username: `pi` (default, verify if different)
  - Purpose: Power profiler feature testing
  
- **Future**: Additional RPis for `feature/test-sequences` or `dev` integration

### What to Test on RPi

✅ **Hardware Integration**
- GPIO reads/writes
- I2C communication
- ADC measurements
- SPI communication
- UART communication

✅ **Real Sensors**
- Sensor detection
- Sensor data reading
- Sensor control
- Sensor accuracy

✅ **Performance**
- Response times
- Update rates
- Memory usage
- CPU usage

✅ **End-to-End**
- Full application flow
- User interactions
- Real-world scenarios
- Stress testing

### Deploying to RPi

See `scripts/deploy-to-pi.sh` for automated deployment.

**Manual Deployment**:
```bash
# On development machine
git push origin feature/your-branch

# On RPi
cd /opt/device-panel  # or your install location
git fetch origin
git checkout feature/your-branch
git pull origin feature/your-branch

# Install dependencies (if needed)
pip3 install -r requirements.txt

# Run app
python3 device_panel.py
```

### Success Criteria for RPi Testing

- [ ] Hardware managers work correctly
- [ ] Sensors detected and readable
- [ ] GPIO control works
- [ ] ADC measurements accurate
- [ ] I2C communication reliable
- [ ] App performance acceptable
- [ ] No hardware-related crashes
- [ ] Features work with real hardware

---

## Testing by Feature

### Power Profiler

**Ubuntu Testing**:
- Power measurement logic
- Sequence execution (mock)
- UI rendering
- Data processing

**RPi Testing**:
- INA260 sensor detection
- Real power measurements
- GPIO control for sequences
- UART communication
- Event-triggered measurements

### Test Sequences

**Ubuntu Testing**:
- Sequence definition/parsing
- Sequence execution logic
- Step type implementations (mock)
- Error handling

**RPi Testing**:
- Real GPIO sequences
- Real ADC sequences
- Real UART sequences
- Timing accuracy
- Error recovery

### Smart Suggestions

**Ubuntu Testing**:
- Device detection logic (mock)
- Suggestion engine
- Pattern matching
- App framework

**RPi Testing**:
- Real I2C device detection
- Real sensor combinations
- App launching
- UI rendering

---

## Testing Checklist

### Before Ubuntu Testing

- [ ] Code compiles/runs
- [ ] No syntax errors
- [ ] Dependencies installed

### During Ubuntu Testing

- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Test UI manually
- [ ] Check code coverage
- [ ] Fix any issues found

### Before RPi Testing

- [ ] All Ubuntu tests pass
- [ ] Hardware-specific code ready
- [ ] RPi assigned and accessible
- [ ] Hardware connected

### During RPi Testing

- [ ] Deploy code to RPi
- [ ] Test hardware functionality
- [ ] Test with real sensors
- [ ] Verify performance
- [ ] Document any issues

### Before Merge to dev

- [ ] All Ubuntu tests pass
- [ ] All RPi tests pass (if hardware needed)
- [ ] No regressions
- [ ] Documentation updated
- [ ] Ready for integration

---

## Continuous Testing

### Automated Testing (CI/CD)

**On every commit**:
- Unit tests
- Integration tests
- Linting
- Type checking

**On merge to dev**:
- Full test suite
- Integration tests
- Coverage report

### Manual Testing

**Daily**:
- Run test suite locally
- Quick UI check
- Verify features work

**Before merge**:
- Full test suite
- RPi testing (if needed)
- Integration testing

---

## Troubleshooting

### Tests Fail on Ubuntu

1. Check mock hardware setup
2. Verify test data
3. Check dependencies
4. Review test logs

### Tests Fail on RPi

1. Check hardware connections
2. Verify I2C/SPI enabled
3. Check permissions
4. Review hardware logs
5. Verify sensor connections

### App Doesn't Launch

1. Check Python version
2. Verify dependencies
3. Check Qt/PySide6 installation
4. Review error messages
5. Check display settings (for GUI)

---

## Best Practices

### Do This

- ✅ Test on Ubuntu first
- ✅ Use mocks for hardware testing
- ✅ Test frequently
- ✅ Fix issues immediately
- ✅ Document test results
- ✅ Test with features enabled/disabled

### Don't Do This

- ❌ Skip Ubuntu testing
- ❌ Test only on RPi
- ❌ Ignore test failures
- ❌ Skip integration tests
- ❌ Test only happy path

---

## Test Data

### Mock Data

Store mock test data in `tests/data/`:
- `tests/data/mock_sensor_data.json`
- `tests/data/mock_i2c_responses.json`
- `tests/data/expected_results.json`

### Real Data

When testing on RPi, save real data for comparison:
- `tests/data/real_sensor_readings.csv`
- `tests/data/performance_metrics.json`

---

## Summary

1. **Ubuntu First**: Test logic, UI, integration on Ubuntu
2. **RPi When Needed**: Test hardware, sensors, performance on RPi
3. **Automated**: Run tests on every commit
4. **Manual**: Verify UI and real-world scenarios
5. **Document**: Keep test results and issues documented

The goal: **Catch most issues on Ubuntu, verify hardware on RPi**.

