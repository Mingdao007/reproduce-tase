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
  for the next Stage A simulation prototype. This does not make the model
  hardware-ready.
- Contact stiffness and damping are not paper- or hardware-verified.

## Next Executable Step

Keep hardware use blocked until mounted-stack geometry is measured. The next
simulation controller prototype should target the v58 selected diagnostic
terminal setup unless a later decision changes the label.
