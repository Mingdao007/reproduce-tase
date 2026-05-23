# Decision Record

## D001: Use `Mingdao007/reproduce-tase` As Authoritative Repo

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use `https://github.com/Mingdao007/reproduce-tase` as the authoritative home
  for reproduction code, configs, plans, reports, and lightweight metadata.
- Reason:
  The old UR10e workspace contains many unrelated and untracked experiment
  folders. A dedicated repo is needed for rollback and review.
- Consequence:
  Existing local artifacts are migrated selectively. Heavy raw artifacts are
  represented by manifests unless Git LFS is explicitly configured.

## D002: Keep MuJoCo As Baseline Simulator

- Date: 2026-05-24
- Status: accepted for v0/v1
- Decision:
  Keep MuJoCo as the first reproducible simulation baseline.
- Reason:
  Existing scripts and plans already target MuJoCo, and the user requested it
  as the default while allowing alternatives.
- Consequence:
  Other simulators can be proposed later, but not before the MuJoCo baseline is
  audited.

## D003: No Real Robot Motion Or Writes In Current Phase

- Date: 2026-05-24
- Status: accepted
- Decision:
  Current work is documentation, migration, audit, and simulation only.
- Reason:
  TCP, payload, force source, OnRobot force reference, and contact setup are
  unresolved.
- Consequence:
  Hardware work remains read-only until a separate user-approved SOP exists.

## D004: Treat Existing E1-E4 Results As Synthetic

- Date: 2026-05-24
- Status: accepted
- Decision:
  Existing article-level E1-E4 results are useful migration evidence, but not
  final paper-truth reproduction.
- Reason:
  PDF extraction is still pending and the current configs include provisional
  values.
- Consequence:
  Reports must state "UR10e adapted reproduction" or "synthetic simulation"
  where appropriate.

