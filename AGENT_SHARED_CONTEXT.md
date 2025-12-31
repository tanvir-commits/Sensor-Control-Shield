# Agent Shared Context

**Last Updated**: 2024-12-31

This file is a shared workspace for all agents to communicate current status, blockers, discoveries, and coordination needs. **Update this file when your status changes.**

---

## Current Status by Branch

### feature/power-profiler

**Status**: Not started  
**Agent**: (assign when agent starts)  
**Last Update**: 2024-12-31

**Current Work**:
- (Update when work begins)

**Blockers**:
- (List any blockers here)

**Dependencies**:
- May use sequence engine from `feature/test-sequences` (when available)

**Recent Discoveries**:
- (Share any gotchas or insights here)

**Next Steps**:
- (What you plan to do next)

---

### feature/test-sequences

**Status**: Not started  
**Agent**: (assign when agent starts)  
**Last Update**: 2024-12-31

**Current Work**:
- (Update when work begins)

**Blockers**:
- (List any blockers here)

**Dependencies**:
- None (standalone feature)

**Recent Discoveries**:
- (Share any gotchas or insights here)

**Next Steps**:
- (What you plan to do next)

---

### feature/smart-suggestions

**Status**: Not started  
**Agent**: (assign when agent starts)  
**Last Update**: 2024-12-31

**Current Work**:
- (Update when work begins)

**Blockers**:
- (List any blockers here)

**Dependencies**:
- Uses device detection system (already in main)

**Recent Discoveries**:
- (Share any gotchas or insights here)

**Next Steps**:
- (What you plan to do next)

---

## Cross-Branch Coordination

### API Changes

**None yet** - Update this section when APIs change that affect other branches.

Example format:
```
[Date] - feature/test-sequences: Sequence API updated
- Added callback support for custom actions
- Power profiler may need to update
- See: BRANCH_TEST_SEQUENCES.md
```

### Shared Code Needs

**None yet** - Update if you need shared code or utilities.

### Integration Notes

**None yet** - Update when features need to work together.

---

## Blockers and Issues

### Current Blockers

**None** - Update this section if you're blocked and need help from another agent.

Example format:
```
[Date] - feature/power-profiler: Blocked on sequence API
- Need sequence engine API finalized
- Waiting on: feature/test-sequences
- Workaround: (if any)
```

### Known Issues

**None** - Update if you discover issues that affect other branches.

---

## Recent Discoveries

### Gotchas and Insights

**None yet** - Share things you learned that might help others.

Example format:
```
[Date] - feature/power-profiler: INA260 timing issue
- INA260 needs 10ms delay after config write
- Affects: Any code using INA260
- Fix: Added delay in power measurement manager
```

### Best Practices

**None yet** - Share patterns or practices that worked well.

---

## Testing Status

### Ubuntu Testing

- **Power Profiler**: Not started
- **Test Sequences**: Not started
- **Smart Suggestions**: Not started

### RPi Testing

- **RPi 1**: Assigned to power-profiler (when ready)
- **RPi 2**: Assigned to test-sequences (when ready)
- **Future**: Additional RPis for other features or dev integration

---

## Communication Log

### Recent Messages

**None yet** - Use this for quick messages between agents.

Example format:
```
[Date] - Agent A to Agent B:
"Sequence API is ready, see BRANCH_TEST_SEQUENCES.md for details"
```

---

## How to Use This File

### When to Update

1. **Start of work**: Update your branch status
2. **Status changes**: Update when you start/finish major work
3. **Blockers**: Update when blocked or unblocked
4. **Discoveries**: Share insights that help others
5. **API changes**: Document changes that affect others
6. **End of day**: Update status before finishing

### What to Include

- **Current Work**: What you're actively working on
- **Blockers**: What's preventing progress
- **Dependencies**: What you need from others
- **Discoveries**: Insights, gotchas, best practices
- **Next Steps**: What you plan to do next

### What NOT to Include

- Detailed implementation plans (use branch docs)
- Long explanations (link to branch docs instead)
- Personal notes (use your own files)

---

## Template for Updates

When updating your branch section, use this format:

```markdown
### feature/your-branch

**Status**: In progress / Blocked / Complete  
**Agent**: Your identifier  
**Last Update**: YYYY-MM-DD

**Current Work**:
- Working on: [specific task]
- Progress: [percentage or milestone]

**Blockers**:
- [Blocker description] - Waiting on: [who/what]

**Dependencies**:
- Need: [what you need]
- From: [which branch/agent]

**Recent Discoveries**:
- [Discovery] - Affects: [who]

**Next Steps**:
- [What you'll do next]
```

---

## Notes

- Keep updates concise
- Update regularly (at least daily)
- Be specific about blockers and dependencies
- Share discoveries that help others
- This file is in git, so all agents can see updates

---

**Remember**: This is a living document. Update it as your status changes!

