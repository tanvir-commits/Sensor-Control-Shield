# Production Branch (prod)

## Project Overview

The `prod` branch contains production-ready, stable releases of the Device Panel application. This branch is protected and only receives code that has been thoroughly tested and approved for release.

## Branch Relationships

- **Source**: Only merges from `dev` branch after release approval
- **Destination**: This is the final destination for stable code
- **Releases**: Tagged with version numbers (v0.1, v0.2, etc.)
- **Purpose**: Provide stable, tested releases to users

## High-Level Plan

The `prod` branch maintains stable releases:

1. **Release Process**: Code flows from `dev` → `prod` after approval
2. **Versioning**: Semantic versioning (major.minor.patch)
3. **Tagging**: Each release is tagged (e.g., `v0.2.0`)
4. **Documentation**: Release notes and changelog maintained
5. **Stability**: Only bug fixes and critical updates after release

## Development Rules

### Merge Requirements

- **Source**: Only from `dev` branch
- **Approval**: Requires explicit release approval
- **Testing**: Full regression test suite must pass
- **Documentation**: Release notes must be updated
- **Tagging**: Version tag must be created

### Code Quality

- All tests must pass
- No known critical bugs
- Documentation complete
- Changelog updated
- Release notes prepared

### Protection

- No direct commits allowed
- All changes via merge from `dev`
- Protected branch (requires approval)
- Automated checks must pass

## Success Criteria

A release is ready when:

1. All features merged to `dev` and tested
2. Full test suite passes
3. No critical bugs
4. Documentation updated
5. Release notes prepared
6. Approval granted

## Dependencies & Integration

- **Depends on**: `dev` branch (source of all code)
- **Integrates**: All features from `dev`
- **Releases**: Tagged versions for distribution
- **Distribution**: Used for Pi image builds

## Testing Requirements

Before merging to `prod`:

1. Run full test suite on `dev`
2. Test on actual hardware
3. Verify all features work
4. Check for regressions
5. Visual verification complete

## Release Process

1. Ensure `dev` is stable and tested
2. Create release candidate branch
3. Test release candidate thoroughly
4. Prepare release notes
5. Get approval
6. Merge `dev` to `prod`
7. Tag release: `git tag v0.2.0`
8. Push tag: `git push origin v0.2.0`
9. Build Pi image from `prod` branch
10. Distribute release

## Common Issues & Solutions

### Issue: Merge conflicts with prod

**Solution**: Rebase `dev` on `prod` first, resolve conflicts, then merge

### Issue: Tests fail after merge

**Solution**: Fix on `dev`, test, then re-merge to `prod`

### Issue: Need hotfix

**Solution**: Create `hotfix/description` branch from `prod`, fix, merge to both `prod` and `dev`

## Related Branches

- **dev**: Development integration branch (source)
- **feature/***: Feature branches (merge to dev first)

## Notes

- This branch should always be stable
- Never commit directly to `prod`
- Always tag releases
- Keep release notes updated

