# Current Results Snapshot - 2026-05-07

This archive preserves the current curved/paper-aligned work before starting
the full paper reproduction pass.

## Contents

- `results_snapshot.tar.gz`: compressed copy of the local `results/` tree.
- `MANIFEST.sha256`: checksum for the compressed snapshot.
- `git_status_at_snapshot.txt`: worktree state recorded immediately after the
  archive was created.

## Source Context

- Source branch before archiving: `feat/paper-ideal-force-loop`.
- Archive branch: `archive/curved-paper-aligned-2026-05-07`.
- Base committed head before local dirty changes: `749bb47`.
- Main preserved outputs:
  - `results/paper_simulation_figures/paper_simulation_figures_bundle.zip`
  - `results/paper_simulation_figures_v2/paper_simulation_figures_bundle_v2.zip`
  - `results/step_surface_force_paper_aligned/step_surface_force_paper_aligned_results_report.md`
  - `results/math_method_audit.md`

## Verification

Run from the repository root:

```bash
sha256sum -c artifacts/2026-05-07-current-results/MANIFEST.sha256
```

The archive is intentionally stored outside the ignored `results/` path so it
can be tracked through Git LFS.
