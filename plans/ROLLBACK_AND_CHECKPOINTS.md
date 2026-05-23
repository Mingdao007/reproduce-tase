# Rollback And Checkpoints

## Scope

Keep every reproduction stage recoverable through Git branches, commits,
manifests, and Markdown decisions.

## Assumptions

- `Mingdao007/reproduce-tase` is the authoritative repository.
- Heavy local artifacts may not be in Git history.

## Exact Files Touched

- `plans/ROLLBACK_AND_CHECKPOINTS.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`

## Commands To Run

```bash
git status --short --branch
git log --oneline --decorate -5
git diff --stat
```

## Expected Outputs

- Branch names align with iteration stage.
- Each run records commit SHA or clearly says it was migrated from a legacy
  pre-repo run.
- Every major decision has a decision-record entry.

## Pass/Fail Criteria

Pass:

- Work can be reverted by commit or branch.
- Legacy artifacts are discoverable from manifests.

Fail:

- A report references a local artifact with no path, hash, or run ID.

## Rollback Point Or Recovery Command

For local uncommitted work:

```bash
git diff > /tmp/reproduce-tase-before-rollback.patch
```

Then revert only files from the current task, never unrelated user work.

## Unresolved Risks

- Initial source material came from an untracked old workspace.
- Future raw data may exceed ordinary Git limits.

## Next Executable Step

Commit this v0 baseline and push the branch once smoke verification is recorded.

