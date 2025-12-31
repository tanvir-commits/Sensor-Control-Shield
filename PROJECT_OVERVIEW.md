# Project Overview - Device Panel

## Quick Reference

**Project**: Device Panel - Raspberry Pi Sensor Control Shield GUI  
**Main Entry**: `device_panel.py`  
**Framework**: PySide6 (Qt6)  
**Language**: Python 3.13

---

## Branch Structure

```
prod (production releases)
  └── dev (development integration)
      ├── feature/power-profiler      [Active]
      ├── feature/test-sequences      [Not started]
      └── feature/smart-suggestions   [Active]
```

---

## All Branches

### prod
- **Purpose**: Production-ready, stable releases
- **Status**: Stable (v0.1 released)
- **Source**: Merges from `dev` only
- **Documentation**: `BRANCH_PROD.md`

### dev
- **Purpose**: Integration branch for all features
- **Status**: Active integration
- **Source**: All feature branches merge here
- **Documentation**: `BRANCH_DEV.md`

### feature/power-profiler
- **Purpose**: Power measurement and automated testing sequences
- **Status**: Active development
- **Agent**: `power-profiler`
- **RPi Assignment**: RPi 2 (192.168.102, user: pi)
- **Key Features**:
  - INA260 current sensor support
  - Multiple I2C buses with user naming
  - Sequence-based testing
  - Event-triggered measurements
- **Documentation**: `BRANCH_POWER_PROFILER.md`

### feature/test-sequences
- **Purpose**: General-purpose sequence engine for test automation
- **Status**: Not started
- **Agent**: (not assigned)
- **RPi Assignment**: (not assigned)
- **Key Features**:
  - Sequence definition and execution
  - GPIO, ADC, UART actions
  - Conditional logic
  - Reusable by other features
- **Documentation**: `BRANCH_TEST_SEQUENCES.md`

### feature/smart-suggestions
- **Purpose**: Automatic device detection and app suggestions
- **Status**: Active development
- **Agent**: `smart-suggestions`
- **RPi Assignment**: RPi 1 (192.168.101, user: a, password: 1)
- **Key Features**:
  - Device detection and identification
  - Pattern-based app suggestions
  - One-click app launch
  - App framework
- **Documentation**: `BRANCH_SMART_SUGGESTIONS.md`

---

## RPi Assignments

| RPi | IP Address | Branch | Username | Purpose |
|-----|------------|--------|----------|---------|
| RPi 1 | 192.168.101 | `feature/smart-suggestions` | `a` | Smart suggestions testing |
| RPi 2 | 192.168.102 | `feature/power-profiler` | `pi` | Power profiler testing |

See `RPI_ASSIGNMENTS.md` for detailed connection info and deployment commands.

---

## Active Agents

| Agent Name | Branch | Status | RPi |
|------------|--------|--------|-----|
| `power-profiler` | `feature/power-profiler` | Active | RPi 2 |
| `smart-suggestions` | `feature/smart-suggestions` | Active | RPi 1 |

---

## Project Structure

```
DeviceOps/
├── device_panel.py          # Main entry point (PROTECTED)
├── config/                  # Configuration files
│   ├── feature_flags.py    # Feature enable/disable
│   ├── pins.py             # Pin definitions (PROTECTED)
│   └── testing_config.py   # Environment detection
├── hardware/               # Hardware managers (PROTECTED)
│   ├── gpio_manager.py
│   ├── adc_manager.py
│   └── i2c_scanner.py
├── ui/                      # UI components
│   ├── main_window.py      # Main window (PROTECTED)
│   └── status_bar.py       # Status bar with branch display
├── devices/                 # Device plugins
├── features/                # Feature extensions
│   ├── power_profiler/     # Power profiler code
│   ├── test_sequences/     # Test sequences code
│   └── smart_suggestions/  # Smart suggestions code
├── tests/                   # Test files
└── scripts/                 # Utility scripts
    ├── deploy-to-pi.sh     # Deploy to RPi
    └── setup-pi-for-branch.sh  # Initial RPi setup
```

---

## Key Documentation

### Getting Started
- `AGENT_QUICK_START.md` - Quick start guide for new agents
- `DEVELOPMENT.md` - Overall development guidelines
- `BRANCH_STRATEGY.md` - Branch workflow

### Understanding Decisions
- `DECISION_LOG.md` - Why decisions were made
- `PROTECTED_FILES.md` - What files are protected and why

### Coordination
- `AGENT_SHARED_CONTEXT.md` - Real-time coordination board
- `AGENT_COMMUNICATION.md` - How agents communicate

### Testing
- `TESTING_WORKFLOW.md` - Testing workflow (Ubuntu → RPi)
- `TESTING_STRATEGY.md` - Testing procedures
- `RPI_ASSIGNMENTS.md` - RPi connection details

### Branch-Specific
- `BRANCH_PROD.md` - Production branch
- `BRANCH_DEV.md` - Development branch
- `BRANCH_POWER_PROFILER.md` - Power profiler feature
- `BRANCH_TEST_SEQUENCES.md` - Test sequences feature
- `BRANCH_SMART_SUGGESTIONS.md` - Smart suggestions feature

---

## Current Status

### Active Development
- ✅ `feature/power-profiler` - Power measurement and sequences
- ✅ `feature/smart-suggestions` - Device detection and app suggestions

### Not Started
- ⏳ `feature/test-sequences` - Sequence engine (may be used by power-profiler)

### Stable
- ✅ `prod` - v0.1 released
- ✅ `dev` - Integration branch active

---

## Quick Commands

### Check Current Branch
```bash
git branch
```

### Switch to Feature Branch
```bash
git checkout feature/power-profiler
# or
git checkout feature/smart-suggestions
```

### Deploy to RPi
```bash
# Power profiler (RPi 2)
./scripts/deploy-to-pi.sh -b feature/power-profiler -h 192.168.102 -u pi

# Smart suggestions (RPi 1)
./scripts/deploy-to-pi.sh -b feature/smart-suggestions -h 192.168.101 -u a
```

### Run App
```bash
python device_panel.py
# Window title will show: "Device Panel [branch-name]"
```

---

## Next Steps

1. **New Agents**: Read `AGENT_QUICK_START.md` first
2. **Feature Work**: Check branch-specific `.md` file
3. **Coordination**: Update `AGENT_SHARED_CONTEXT.md`
4. **Testing**: Follow `TESTING_WORKFLOW.md` (Ubuntu first, then RPi)

---

**Last Updated**: 2024-12-31

