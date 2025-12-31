# Branch Strategy and Workflow

## Branch Hierarchy

```
prod (production, stable releases)
  └── dev (development, integration branch)
      ├── feature/power-profiler
      ├── feature/test-sequences
      └── feature/smart-suggestions
```

## Branch Purposes

### prod Branch
- **Purpose**: Production-ready, stable releases
- **Source**: Only merges from `dev` after release approval
- **Protection**: Full regression test suite must pass
- **Releases**: Tagged with version numbers (v0.1, v0.2, etc.)

### dev Branch
- **Purpose**: Integration branch for all features
- **Source**: All feature branches merge here
- **Protection**: Automated tests must pass before merge
- **Workflow**: Features integrate here before going to `prod`

### feature/* Branches
- **Purpose**: Individual feature development
- **Source**: Created from `dev` branch
- **Protection**: Tests must pass before merge to `dev`
- **Lifetime**: Deleted after merge to `dev`

## Workflow

### Starting a Feature

1. Ensure you're on `dev` branch: `git checkout dev`
2. Pull latest: `git pull origin dev`
3. Create feature branch: `git checkout -b feature/your-feature`
4. Start development

### During Development

1. Work on your feature branch
2. Commit frequently with clear messages
3. Run tests locally before pushing
4. Push to remote: `git push origin feature/your-feature`

### Merging to dev

1. Ensure all tests pass locally
2. Rebase on latest `dev`: `git rebase dev`
3. Resolve any conflicts
4. Push rebased branch: `git push origin feature/your-feature --force-with-lease`
5. Create pull request to `dev`
6. CI runs automated tests
7. After approval and passing tests, merge to `dev`
8. Delete feature branch

### Cross-Branch Sync

If feature A needs changes from feature B:

**Option 1: Merge via dev**
1. Feature B merges to `dev`
2. Feature A rebases from `dev`: `git rebase dev`
3. Feature A gets Feature B's changes

**Option 2: Direct merge**
1. Feature A merges Feature B: `git merge feature/B`
2. Both branches stay in sync
3. Both merge to `dev` separately

**Option 3: Sync branch**
1. Create `sync/fix-for-feature-A` branch
2. Apply fix to both Feature A and Feature B
3. Merge sync branch to both features

### Release Process

1. All features merged to `dev`
2. Full test suite passes on `dev`
3. Create release candidate
4. Test release candidate
5. Merge `dev` to `prod`
6. Tag release: `git tag v0.2`
7. Push tags: `git push origin v0.2`

## Conflict Resolution

### Preventing Conflicts

- Rebase frequently from `dev`
- Keep feature branches focused
- Communicate with other developers
- Use feature flags for isolation

### Resolving Conflicts

1. Identify conflicting files
2. Understand both changes
3. Merge manually or use tools
4. Test after resolution
5. Commit resolution

## Best Practices

1. **Small, focused PRs**: Easier to review and merge
2. **Frequent rebases**: Stay in sync with `dev`
3. **Clear commit messages**: Explain what and why
4. **Test before merge**: Don't break `dev`
5. **Document changes**: Update relevant `.md` files

## Automated Checks

Before merge to `dev`:
- All unit tests pass
- Integration tests pass
- No linting errors
- No type errors
- Protected files check passes
- Feature flag check passes

## Emergency Procedures

### Hotfix to prod

1. Create `hotfix/description` from `prod`
2. Fix issue
3. Test thoroughly
4. Merge to both `prod` and `dev`
5. Tag hotfix release

### Reverting a Merge

1. Identify bad commit
2. Revert on `dev`: `git revert <commit>`
3. Test revert
4. Merge revert to `prod` if needed

## Agent Communication

Agents working on different branches can communicate via:

1. **Git commits**: Commit messages can reference other branches
2. **Documentation**: Update `.md` files with cross-branch notes
3. **Shared config**: Use `config/` for shared settings
4. **Issue tracking**: Use GitHub issues (if available)
5. **Branch status files**: Create `BRANCH_STATUS.md` in each branch

See branch-specific `.md` files for feature details.

