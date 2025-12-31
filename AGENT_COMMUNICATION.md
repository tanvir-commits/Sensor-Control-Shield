# Agent Communication Guide

## Overview

When multiple AI agents work on different branches simultaneously, they need ways to communicate and coordinate. This document outlines the available communication methods.

## Communication Methods

### 1. Git Commits and Messages

**Method**: Use descriptive commit messages that reference other branches or features.

**Example**:
```
feat(power-profiler): Add INA260 support
- Uses sequence engine from feature/test-sequences
- See BRANCH_TEST_SEQUENCES.md for sequence API
```

**Best Practices**:
- Reference related branches in commit messages
- Mention dependencies or conflicts
- Document breaking changes clearly

### 2. Documentation Files

**Method**: Update `.md` files with cross-branch information.

**Files to Update**:
- Branch-specific `.md` files (e.g., `BRANCH_POWER_PROFILER.md`)
- `DEVELOPMENT.md` for general notes
- `BRANCH_STRATEGY.md` for workflow changes

**Example**:
```markdown
## Cross-Branch Notes

- Power Profiler uses sequence engine from feature/test-sequences
- If test-sequences changes API, update power-profiler accordingly
```

### 3. Shared Configuration

**Method**: Use `config/` directory for shared settings.

**Files**:
- `config/feature_flags.py` - Feature enable/disable
- `config/power_config.py` - Power profiler settings (if shared)
- `config/sequence_config.py` - Sequence engine settings (if shared)

**Example**:
```python
# In config/feature_flags.py
ENABLE_POWER_PROFILER = True
ENABLE_TEST_SEQUENCES = True  # Required by power profiler
```

### 4. Shared Context File (NEW - Recommended)

**Method**: Update `AGENT_SHARED_CONTEXT.md` for real-time coordination.

**Content**:
- Current status of all branches
- Blockers and dependencies
- Recent discoveries and gotchas
- API changes affecting others
- Quick messages between agents

**Example**:
```markdown
### feature/power-profiler

**Status**: In progress
**Current Work**: Implementing INA260 support
**Blockers**: Need sequence engine API from test-sequences
**Recent Discoveries**: INA260 needs 10ms delay after config write
```

**Best Practices**:
- Update at start/end of work session
- Update when status changes
- Share discoveries that help others
- Keep updates concise

### 5. Branch Status Files

**Method**: Create `BRANCH_STATUS.md` in each branch for detailed status.

**Content**:
- Detailed current work status
- Blockers or dependencies
- Recent changes
- Next steps

**Example**:
```markdown
# Power Profiler Branch Status

## Current Status
- Implementing INA260 support
- Waiting for sequence engine API from test-sequences

## Blockers
- Need sequence engine API finalized

## Recent Changes
- Added power measurement manager
- Integrated with GPIO manager
```

### 6. Decision Log

**Method**: Read `DECISION_LOG.md` to understand why decisions were made.

**Content**:
- Architectural decisions and reasoning
- Technology choices and trade-offs
- Design patterns and their rationale

**Use Cases**:
- Understanding existing code structure
- Making informed changes
- Avoiding re-debating settled decisions

**Example**:
```markdown
## Hardware Abstraction Layer

**Decision**: Separate hardware managers from UI
**Reasoning**: Separation of concerns, testability, reusability
**Trade-offs**: More files, but better organization
```

### 7. Quick Start Guide

**Method**: New agents should read `AGENT_QUICK_START.md` first.

**Content**:
- First steps for new agents
- What to read in what order
- Common tasks and workflows
- Getting unstuck

### 8. GitHub Issues (if available)

**Method**: Use GitHub issues for tracking and communication.

**Use Cases**:
- Report bugs found in other branches
- Request features from other branches
- Coordinate breaking changes
- Track dependencies

### 9. Code Comments

**Method**: Add comments in code referencing other branches.

**Example**:
```python
# TODO: Update when feature/test-sequences merges to dev
# See BRANCH_TEST_SEQUENCES.md for sequence API
def execute_sequence(self, sequence):
    pass
```

### 10. Shared Test Files

**Method**: Use `tests/shared/` for cross-feature tests.

**Example**:
- `tests/shared/test_power_with_sequences.py` - Tests power profiler using sequences

## Communication Workflows

### Scenario 1: Feature A Needs Feature B

**Workflow**:
1. Feature A agent checks `BRANCH_FEATURE_B.md` for API
2. Feature A agent adds dependency note in its branch doc
3. Feature A agent implements using Feature B's API
4. If Feature B changes API, Feature A updates accordingly
5. Both merge to `dev` when ready

### Scenario 2: Feature A Breaks Feature B

**Workflow**:
1. Feature A agent commits change
2. Feature B agent tests, finds breakage
3. Feature B agent updates `BRANCH_STATUS.md` with blocker
4. Feature A agent fixes issue or coordinates solution
5. Both branches stay in sync

### Scenario 3: Shared Code Needed

**Workflow**:
1. Identify shared code need
2. Create shared module in `features/shared/` or appropriate location
3. Both features use shared code
4. Document in both branch docs

## Best Practices

### Do This

1. **Read branch docs first**: Check `BRANCH_*.md` files before starting
2. **Update docs**: Keep branch docs current with status
3. **Use feature flags**: Coordinate via feature flags
4. **Test integration**: Test with other features when possible
5. **Communicate changes**: Update docs when APIs change

### Don't Do This

1. **Don't modify other branches directly**: Work on your own branch
2. **Don't break APIs silently**: Document breaking changes
3. **Don't ignore dependencies**: Check what other features need
4. **Don't skip documentation**: Keep docs updated

## Coordination Checklist

Before merging to `dev`:

- [ ] Checked other branch docs for dependencies
- [ ] Updated own branch doc with status
- [ ] Tested with other features (if applicable)
- [ ] Documented any API changes
- [ ] Resolved any conflicts
- [ ] All tests pass

## Example Communication

### Agent A (Power Profiler) to Agent B (Test Sequences)

**Agent A commits**:
```
feat(power-profiler): Add sequence execution
- Uses sequence engine from feature/test-sequences
- See BRANCH_TEST_SEQUENCES.md for API details
- Note: May need to update if sequence API changes
```

**Agent B responds** (in commit or doc):
```
feat(test-sequences): Update sequence API
- Added callback support for custom actions
- Power profiler may need to update implementation
- See BRANCH_POWER_PROFILER.md for integration notes
```

## Tools for Communication

### Git Commands

```bash
# Check what other branches have
git log dev..feature/other-branch

# See changes in other branch
git diff dev feature/other-branch

# Check if your branch conflicts
git merge-base dev feature/your-branch
```

### Documentation

- Read `BRANCH_*.md` files for feature details
- Check `BRANCH_STATUS.md` for current status
- Review `DEVELOPMENT.md` for guidelines

## Summary

Agents communicate through:
1. **Git commits** - Reference other branches
2. **Documentation** - Update `.md` files
3. **Shared config** - Use `config/` for coordination
4. **Shared context** - Real-time coordination via `AGENT_SHARED_CONTEXT.md` ⭐ NEW
5. **Decision log** - Understand reasoning via `DECISION_LOG.md` ⭐ NEW
6. **Quick start** - Onboard quickly via `AGENT_QUICK_START.md` ⭐ NEW
7. **Status files** - Track current work
8. **Code comments** - Reference dependencies

The key is: **Document everything, communicate clearly, coordinate via `dev` branch, update shared context regularly**.

## Recommended Daily Workflow

1. **Start of day**:
   - Read `AGENT_SHARED_CONTEXT.md` for current status
   - Check your branch status
   - Sync with `dev` branch

2. **During work**:
   - Update `AGENT_SHARED_CONTEXT.md` when status changes
   - Commit with clear messages referencing other branches
   - Document discoveries in shared context

3. **End of day**:
   - Update `AGENT_SHARED_CONTEXT.md` with your status
   - Push your branch
   - Note any blockers or dependencies

