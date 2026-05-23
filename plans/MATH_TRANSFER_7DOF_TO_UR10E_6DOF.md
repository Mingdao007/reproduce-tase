# Math Transfer Plan: 7DOF Paper To UR10e 6DOF

## Scope

Translate the paper's 7DOF force-motion control formulation into a UR10e 6DOF
adapted formulation without relying on redundant null-space behavior.

## Assumptions

- Paper platform is 7DOF; UR10e is 6DOF.
- UR10e adapted reproduction must be labeled separately from paper-faithful
  reproduction.
- The current derivation is preliminary until paper truth extraction closes.

## Exact Files Touched

- `reports/math_derivation_ur10e_transfer.md`
- `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
- Future controller code under `src/tase_repro/`

## Commands To Run

```bash
python3 -m pytest tests/test_kinematics.py
python3 -m pytest tests/test_constraints.py
```

## Expected Outputs

- A notation table for frames, wrench signs, task variables, and constraints.
- A UR10e QP or constrained least-squares formulation with slack variables.
- Explicit task priorities and infeasibility handling.

## Pass/Fail Criteria

Pass:

- Joint/velocity limits are hard constraints.
- Force normal task, tangential motion task, and orientation task have defined
  priorities.
- No hidden `qdot` clipping is allowed.

Fail:

- 7DOF redundancy assumptions are copied into UR10e without modification.

## Rollback Point Or Recovery Command

Keep math and controller changes separated. If the derivation changes, update
the decision record and revert only the affected controller commit.

## Unresolved Risks

- Contact normal estimation and force sign convention remain unverified.
- Orientation compliance may need dimensional reduction under UR10e task
  saturation.

## Next Executable Step

Review `reports/math_derivation_ur10e_transfer.md` and turn the QP statement
into tests before implementing a controller.

