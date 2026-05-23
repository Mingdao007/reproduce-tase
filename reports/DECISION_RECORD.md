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

## D005: Keep Orientation Signal Ambiguity Open

- Date: 2026-05-24
- Status: accepted
- Decision:
  Record the Section V signal `u = [cos(0.1t), sin(0.1t)]` as PDF-extracted,
  but keep its implementation interpretation unresolved.
- Reason:
  Earlier in the paper, orientation compliance is described using a force
  direction vector and rotation matrix. The Section V notation appears
  lower-dimensional and cannot be transferred to UR10e without an explicit
  convention.
- Consequence:
  `configs/paper_truth.yaml` keeps orientation dimension resolution in
  `pending_pdf_verify`.

## D006: Use Repo Test Wrapper With Pytest Plugin Autoload Disabled

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use `scripts/run_tests.sh` as the test entry point.
- Reason:
  The bench has system pytest `6.2.5` and a user-site `anyio` pytest plugin
  that expects newer pytest internals. Direct `python3 -m pytest` failed during
  plugin loading before collecting repo tests.
- Consequence:
  The wrapper sets `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and then runs
  `python3 -m pytest -q`.

## D007: Start Controller With No-Contact Velocity-Level Smoke

- Date: 2026-05-24
- Status: accepted
- Decision:
  Implement the first controller path as a simulation-only velocity-level TCP
  smoke test, not as force/contact control.
- Reason:
  The MuJoCo model is approximate, the force source is unresolved, and
  OnRobot/RTDE force-frame issues are still open. A bounded velocity task is
  the smallest useful step that validates the UR10e 6DOF hard-limit contract.
- Consequence:
  Contact-force ladder work must come next before any claim about force-motion
  control.

## D008: Use Static Model Offset For First Contact Force Ladder

- Date: 2026-05-24
- Status: accepted
- Decision:
  Use tiny `base_link` z offsets to create calibrated static contact forces in
  the v1 approximate MuJoCo model.
- Reason:
  The current objective is to verify contact force sign and target-force
  measurement behavior before implementing closed-loop force control. Direct
  model offsets are deterministic and avoid pretending a controller exists.
- Consequence:
  The ladder results are valid only as MuJoCo contact-model evidence. They are
  not robot motion, not closed-loop control, and not hardware validation.
