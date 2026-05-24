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
- The v43 capped-integral KKT paper-platform line passes tail contact and
  force error using `kkt_projection`, but the integral cap is not yet
  PDF-verified paper truth.
- The v44 strict parity gate formalizes the comparison against the legacy
  MATLAB/RNN outputs. The then-current Python 7DOF candidate has tail
  convergence agreement with the formula-faithful reference but fails strict
  parity on duration, Fig.5/Fig.6 landmark coverage, and capped-integral
  assumptions.
- The v45 30 s Python 7DOF candidate closes the duration-coverage gap and
  records q7 at 22 s. It still fails strict parity because q7 at 22 s is
  `1.6755097668200787 rad` rather than `2.5 rad`, Fig.5 r-sweep coverage is
  missing, and the force-integral cap remains an adapted assumption.
- The v46 Python 7DOF Fig.5 sweep closes the Fig.5 coverage gap. Strict
  parity still fails because q7 at 22 s remains mismatched and the
  force-integral cap remains an adapted assumption.

## Next Executable Step

For the paper-platform line, investigate the q7-at-22 s mismatch, remove or
justify the force-integral cap, or verify the Panda/Franka DH model before
upgrading the claim. Keep this separate from UR10e adapted controller
iterations.
