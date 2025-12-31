# Development Branch (dev)

## Project Overview

The `dev` branch is the integration branch where all features come together. It serves as the staging area before production releases. All feature branches merge here first, and code is tested and integrated before moving to `prod`.

## Branch Relationships

- **Source**: All `feature/*` branches merge here
- **Destination**: Merges to `prod` for releases
- **Purpose**: Integration and testing of all features
- **Protection**: Automated tests must pass before merge

## High-Level Plan

The `dev` branch integrates all features:

1. **Integration Point**: All features merge here
2. **Testing**: Full test suite runs on every merge
3. **Stability**: Must remain stable for other features
4. **Sync**: Feature branches rebase from here
5. **Preparation**: Prepares code for `prod` releases

## Development Rules

### Merge Requirements

- **Source**: Feature branches only
- **Testing**: All automated tests must pass
- **Conflicts**: Must be resolved before merge
- **Feature Flags**: Must be set correctly
- **Documentation**: Must be updated

### Code Quality

- All tests must pass
- No breaking changes to core
- Features must be isolated
- Protected files must not be modified incorrectly
- Integration tests must pass

### Protection

- No direct commits (except hotfixes)
- All changes via feature branch merges
- Automated checks must pass
- Code review may be required

## Success Criteria

`dev` is healthy when:

1. All features integrate successfully
2. Full test suite passes
3. No regressions
4. Features work together
5. Ready for release candidate

## Dependencies & Integration

- **Depends on**: Feature branches
- **Integrates**: All features
- **Feeds**: `prod` branch
- **Syncs**: Feature branches rebase from here

## Testing Requirements

Before merging feature to `dev`:

1. Feature tests pass
2. Integration tests pass
3. Core tests still pass
4. No conflicts with `dev`
5. Feature flag works correctly

## Merge Process

1. Feature branch is complete
2. Rebase on latest `dev`: `git rebase dev`
3. Resolve conflicts if any
4. Run full test suite
5. Create pull request to `dev`
6. CI runs automated tests
7. After approval, merge to `dev`
8. Delete feature branch

## Cross-Feature Coordination

If features need to work together:

1. Feature A merges to `dev`
2. Feature B rebases from `dev`
3. Feature B gets Feature A's changes
4. Both features work together

## Common Issues & Solutions

### Issue: Feature breaks other features

**Solution**: Fix on feature branch, test, then merge to `dev`

### Issue: Merge conflicts

**Solution**: Rebase feature branch on `dev`, resolve conflicts, test, then merge

### Issue: Tests fail after merge

**Solution**: Fix on feature branch, test, then re-merge to `dev`

## Related Branches

- **prod**: Production branch (destination for releases)
- **feature/power-profiler**: Power profiler feature
- **feature/test-sequences**: Test sequences feature
- **feature/smart-suggestions**: Smart suggestions feature

## Notes

- Keep `dev` stable for other features
- Rebase feature branches frequently
- Test thoroughly before merging
- Communicate with other developers

