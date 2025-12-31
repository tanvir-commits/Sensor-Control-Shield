# Development Guidelines

## Overview

This document provides overall development guidelines for the Device Panel project. All developers and AI agents should follow these guidelines.

## Project Structure

```
DeviceOps/
├── device_panel.py          # Main entry point (PROTECTED)
├── config/                  # Configuration files
├── hardware/                # Hardware managers (PROTECTED)
├── ui/                      # UI components
├── devices/                 # Device plugins
├── features/                # Feature extensions
│   ├── power_profiler/     # Power profiler feature
│   ├── test_sequences/     # Test sequences feature
│   └── smart_suggestions/  # Smart suggestions feature
└── tests/                   # Test files
```

## Branch Strategy

```
prod (production releases)
  └── dev (development integration)
      ├── feature/power-profiler
      ├── feature/test-sequences
      └── feature/smart-suggestions
```

### Branch Rules

1. **prod**: Production-ready code only. Tagged releases.
2. **dev**: Integration branch. All features merge here first.
3. **feature/***: Individual feature development branches.

See `BRANCH_STRATEGY.md` for detailed branch workflow.

## Protected Files

Certain files are protected and require special care:

- `device_panel.py` - Main entry point (minimal changes only)
- `ui/main_window.py` - Core UI structure (feature flag checks only)
- `hardware/*.py` - Hardware managers (read-only for features)
- `config/pins.py` - Pin definitions (read-only)

See `PROTECTED_FILES.md` for complete list and modification rules.

## Feature Development

### Feature Flags

All features must use feature flags in `config/feature_flags.py`:

```python
ENABLE_POWER_PROFILER = True
ENABLE_TEST_SEQUENCES = False
ENABLE_SMART_SUGGESTIONS = False
```

### Feature Isolation

- Features must not break the app when disabled
- All feature code in try/except blocks
- Features access hardware via existing managers only
- No direct hardware access from features

### Adding a Feature

1. Create feature branch from `dev`
2. Add feature flag
3. Implement feature in `features/` directory
4. Add tests in `tests/`
5. Update documentation
6. Merge to `dev` after tests pass

## Testing Requirements

- All new code must have tests
- Core functionality tests must always pass
- Feature tests can be skipped if feature disabled
- Minimum 70% code coverage for new code
- Integration tests verify no regressions

See `TESTING_STRATEGY.md` for detailed testing procedures.

## Code Quality

- Follow PEP 8 style guide
- Type hints for all functions
- Docstrings for all classes and functions
- No breaking changes to existing APIs
- Backward compatibility maintained

## Merge Requirements

Before merging to `dev`:
- All tests must pass
- No conflicts with `dev`
- Feature flag set correctly
- Documentation updated
- Code review (if required)

## Getting Help

- Check branch-specific `.md` files for feature details
- See `BRANCH_STRATEGY.md` for workflow questions
- See `PROTECTED_FILES.md` for modification rules
- See `TESTING_STRATEGY.md` for testing questions

