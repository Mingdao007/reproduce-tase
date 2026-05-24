# MuJoCo Environment Plan

## Scope

Build a reproducible UR10e MuJoCo baseline with explicit model limitations,
contact sign checks, and run metadata.

## Assumptions

- `assets/mjcf/ur10e_nominal.xml` is an approximate nominal model.
- `assets/urdf/ur10e_nominal.urdf` is not calibrated to the real UR10e.
- OnRobot/EOAT geometry is approximate unless later replaced by verified CAD.

## Exact Files Touched

- `assets/mjcf/ur10e_nominal.xml`
- `assets/urdf/ur10e_nominal.urdf`
- `configs/mujoco_ur10e.yaml`
- `scripts/run_ur10e_mujoco_adaptation.py`
- `runs/*`

## Commands To Run

```bash
python3 -c "import mujoco; print(mujoco.__version__)"
python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke
```

## Expected Outputs

- Headless model load.
- Smoke run metrics.
- Contact force sign and TCP site checks.
- Run folder with config, metrics, plots, git state, and failure notes.

## Pass/Fail Criteria

Pass:

- Model loads without error.
- Contact force sign is documented.
- Joint order and limits are checked against the model/config.

Fail:

- MuJoCo run succeeds but omits frame/contact metadata.

## Rollback Point Or Recovery Command

Keep model edits in small commits. Revert the last model commit if loading or
contact behavior regresses.

## Unresolved Risks

- The current TCP guess is unverified. v54 adds a contact-point variant where
  the 85 mm site is separated from the `0.045 m` colliding sphere center, but
  this is still an unmeasured simulation proxy. v55 enforces the intended
  `contact_plane` / `contact_tip` force pair in terminal setup audits, and
  v56 identifies the strict setup blocker as a gate-definition conflict. v57
  adds a diagnostic terminal setup gate, and v58 selects that diagnostic target
  for the next Stage A simulation prototype. v59 evaluates direct Stage B
  handoff from that target and keeps target contact, but qdot saturation still
  blocks a trajectory claim. v60 shows slowed low-gain direct-target handoff
  can avoid saturation, and v61 finds an offline qdot-limited contact path to
  the selected target. v62 tracks that path with qdot-limited joint replay, but
  this still does not make the model hardware-ready. v63 stitches the tracker
  to the slowed handoff. v64 sensitivity passes only `4 / 9` cases, failing
  1 mm base-z/contact perturbations and tighter timing/qdot cases, so the
  result is still simulation-only, nominal, and diagnostic-label. v65 recovers
  the qdot/timing side with explicit margins. v66 recovers the `-1 mm` base-z
  side only with a rebalanced start, reoptimized path, and `16.0 s` Stage A
  duration; `+1 mm` remains unresolved. v67 brackets the positive side and
  shows start/terminal feasibility already fails at `+0.05 mm`. v68 shows the
  positive-side start contact can be recovered through `+1.0 mm` with broader
  seeds, leaving terminal orientation as the current positive-side blocker.
  v69 shows the current contact-point model itself drives the orientation
  margin: force/x-y/contact passes all positive terminal cases, but the
  `0.08 rad` diagnostic orientation gate passes none, and yaw handling is not
  the cause. v70 uses a run-local `0.12 rad` diagnostic orientation envelope
  and recovers positive start, terminal, and path feasibility through
  `+1.0 mm`, but stitched recovery still fails on Stage B E2 qdot saturation.
  v71 shows E2 recovers for all positive deltas at
  `paper_time_scale = 0.005`; qdot-limit-only relaxation at original `0.01`
  timing still fails the hardest `+1.0 mm` row because orientation remains
  just above `0.12 rad`. v72 combines that timing with the v70 relaxed
  terminal/path setup and recovers the full positive E1-E4 stitched diagnostic
  matrix `8 / 8` through `+1.0 mm`. v73 stress-tests that recovered policy and
  passes `37 / 40` compact sensitivity cells, with failures at
  `qdot012_stage_a18s` `+0.2 mm`, `paper_time_scale_0p0075` `+1.0 mm`, and
  `orientation_gate_0p119` `+1.0 mm`. v74 isolates the qdot012 `+0.2 mm`
  failure as a narrow Stage A duration margin that recovers at `18.035 s`. v75
  folds that duration into all positive qdot012 rows and recovers `8 / 8`
  stitched rows through `+1.0 mm`.
- Contact stiffness and damping are not paper- or hardware-verified.

## Next Executable Step

Keep hardware use blocked until mounted-stack geometry is measured. The next
simulation controller prototype should move to the harder `+1.0 mm`
timing/orientation sensitivity limits unless the qdot012 branch is intentionally
stopped at the recovered diagnostic matrix.
