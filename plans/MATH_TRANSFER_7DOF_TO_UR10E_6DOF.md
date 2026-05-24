# Math Transfer Plan: 7DOF Paper To UR10e 6DOF

## Scope

Translate the paper's 7DOF force-motion control formulation into a UR10e 6DOF
adapted formulation without relying on redundant null-space behavior.

## Assumptions

- Paper platform is 7DOF; UR10e is 6DOF.
- UR10e adapted reproduction must be labeled separately from paper-faithful
  reproduction.
- Paper truth extraction has no remaining `pending_pdf_verify` fields, but
  Section V orientation and `z0` remain paper ambiguities.
- The v41 paper-platform executable is diagnostic until contact/force behavior
  and Panda DH provenance are verified.

## Exact Files Touched

- `reports/math_derivation_ur10e_transfer.md`
- `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
- `src/tase_repro/panda_kinematics.py`
- `src/tase_repro/paper_7dof.py`
- Future controller code under `src/tase_repro/`

## Commands To Run

```bash
scripts/run_tests.sh tests/test_kinematics.py
scripts/run_tests.sh tests/test_constraints.py
scripts/run_tests.sh tests/test_panda_kinematics.py tests/test_paper_7dof.py
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
- The v41 paper-platform line executes, but its paper-literal normal-force
  loop loses tail contact and cannot support a paper-equivalent claim yet.
- The v42 contact-stabilized paper-platform line passes tail contact and force
  error, but only as a diagnostic variant using `pinv_bounded` and a capped
  force integral.

## Next Executable Step

For the paper-platform line, debug the KKT-projection contact loss or define a
parity gate against the legacy MATLAB/RNN outputs. Keep this separate from
UR10e adapted controller iterations.
