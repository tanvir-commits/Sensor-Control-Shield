# Agent Quick Start Guide

Welcome! This guide will get you started quickly on your assigned feature branch.

## First Steps (5 minutes)

### 1. Identify Your Branch

Check which feature you're working on:
- **Power Profiler**: `feature/power-profiler`
- **Test Sequences**: `feature/test-sequences`
- **Smart Suggestions**: `feature/smart-suggestions`

### 2. Check Out Your Branch

```bash
# Make sure you're in the project directory
cd /home/a/projects/DeviceOps

# Check out your feature branch
git checkout feature/power-profiler  # Replace with your branch
git pull origin feature/power-profiler
```

### 3. Read Your Branch Documentation

**CRITICAL**: Read these files in order:

1. **Your branch doc**: `BRANCH_[YOUR_FEATURE].md`
   - Example: `BRANCH_POWER_PROFILER.md`
   - Contains: Your feature's plan, rules, success criteria

2. **Development guidelines**: `DEVELOPMENT.md`
   - Contains: Overall project rules and structure

3. **Branch strategy**: `BRANCH_STRATEGY.md`
   - Contains: How to work with branches, merge process

4. **Protected files**: `PROTECTED_FILES.md`
   - Contains: What files you CANNOT modify

5. **Decision log**: `DECISION_LOG.md`
   - Contains: Why things are designed this way

6. **Agent communication**: `AGENT_COMMUNICATION.md`
   - Contains: How to coordinate with other agents

### 4. Check Shared Context

Read `AGENT_SHARED_CONTEXT.md` to see:
- What other agents are working on
- Any blockers or dependencies
- Recent discoveries or gotchas

---

## Understanding the Project

### Project Structure

```
DeviceOps/
├── device_panel.py          # Main entry (PROTECTED - minimal changes)
├── hardware/                # Hardware managers (PROTECTED - read-only)
├── ui/                      # UI components
├── devices/                 # Device plugins
├── features/                # Feature code (YOUR CODE GOES HERE)
│   ├── power_profiler/     # Power profiler feature
│   ├── test_sequences/     # Test sequences feature
│   └── smart_suggestions/   # Smart suggestions feature
├── config/                  # Configuration files
└── tests/                   # Test files
```

### Key Concepts

1. **Feature Flags**: All features use `config/feature_flags.py`
2. **Protected Files**: Core files you cannot modify (see `PROTECTED_FILES.md`)
3. **Hardware Abstraction**: Use existing hardware managers, don't modify them
4. **Isolation**: Your feature must work when disabled

---

## Development Workflow

### Daily Workflow

1. **Start of day**:
   ```bash
   git checkout feature/your-branch
   git pull origin feature/your-branch
   git rebase origin/dev  # Stay in sync with dev
   ```

2. **During work**:
   - Write code in `features/your-feature/`
   - Use feature flags
   - Test on Ubuntu first
   - Commit frequently with clear messages

3. **End of day**:
   ```bash
   git push origin feature/your-branch
   # Update AGENT_SHARED_CONTEXT.md with your status
   ```

### Testing Workflow

1. **Ubuntu Testing** (this machine):
   - Unit tests: `pytest tests/`
   - UI tests: Run app with mock hardware
   - Integration tests: Test with other features

2. **RPi Testing** (hardware required):
   - Deploy to your assigned RPi
   - Test with real hardware
   - Verify performance

See `TESTING_WORKFLOW.md` for details.

---

## Communication

### With Other Agents

1. **Git Commits**: Reference other branches in commit messages
2. **Documentation**: Update branch docs with cross-branch notes
3. **Shared Context**: Update `AGENT_SHARED_CONTEXT.md` with your status
4. **Branch Status**: Create/update `BRANCH_STATUS.md` in your branch

### When You Need Help

1. Check `DECISION_LOG.md` for reasoning
2. Check `AGENT_SHARED_CONTEXT.md` for current status
3. Check other branch docs for dependencies
4. Update `AGENT_SHARED_CONTEXT.md` with your question

---

## Common Tasks

### Adding a New File

```bash
# Create file in your feature directory
touch features/your-feature/new_file.py

# Add to git
git add features/your-feature/new_file.py
git commit -m "feat(your-feature): Add new_file.py"
```

### Modifying a Protected File

**STOP**: Protected files require special care!

1. Read `PROTECTED_FILES.md` for rules
2. Use feature flags
3. Wrap in try/except
4. Test with feature disabled
5. Get approval if required

### Syncing with dev

```bash
# Fetch latest changes
git fetch origin

# Rebase your branch on dev
git rebase origin/dev

# Resolve conflicts if any
# Test after rebase
git push origin feature/your-branch --force-with-lease
```

### Testing Your Feature

```bash
# Enable your feature flag
# Edit config/feature_flags.py
ENABLE_YOUR_FEATURE = True

# Run tests
pytest tests/

# Run app
python device_panel.py
```

---

## Rules to Remember

### ✅ DO

- Read branch documentation first
- Use feature flags
- Test on Ubuntu first
- Commit frequently
- Update shared context
- Use existing hardware managers
- Wrap feature code in try/except

### ❌ DON'T

- Modify protected files without care
- Break the app when feature is disabled
- Commit directly to `dev` or `prod`
- Ignore other agents' work
- Skip documentation
- Access hardware directly (use managers)

---

## Success Checklist

Before considering your feature complete:

- [ ] Feature works when enabled
- [ ] Feature doesn't break app when disabled
- [ ] All tests pass
- [ ] Tested on Ubuntu
- [ ] Tested on RPi (if hardware needed)
- [ ] Documentation updated
- [ ] Shared context updated
- [ ] No conflicts with `dev`
- [ ] Ready to merge to `dev`

---

## Getting Unstuck

### Issue: Don't know where to start

1. Read your `BRANCH_[FEATURE].md` file
2. Check "High-Level Plan" section
3. Start with smallest piece
4. Test frequently

### Issue: Feature breaks app when disabled

1. Check feature flag is used correctly
2. Ensure all code in try/except
3. Test with feature flag False
4. Check protected files weren't modified incorrectly

### Issue: Need something from another branch

1. Check `BRANCH_[OTHER_FEATURE].md` for API
2. Check `AGENT_SHARED_CONTEXT.md` for status
3. Document dependency in your branch doc
4. Implement using their API (when available)

### Issue: Merge conflicts

1. Rebase on latest `dev`
2. Resolve conflicts carefully
3. Test after resolution
4. Document resolution if complex

---

## Next Steps

1. ✅ Check out your branch
2. ✅ Read your branch documentation
3. ✅ Read `DEVELOPMENT.md`
4. ✅ Check `AGENT_SHARED_CONTEXT.md`
5. ✅ Start coding!

Good luck! 🚀

---

## Quick Reference

| Task | Command |
|------|---------|
| Check branch | `git branch` |
| Switch branch | `git checkout feature/your-branch` |
| Sync with dev | `git rebase origin/dev` |
| Run tests | `pytest tests/` |
| Run app | `python device_panel.py` |
| Check protected files | `python scripts/check_protected_files.py` |

