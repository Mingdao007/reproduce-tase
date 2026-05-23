# Math Derivation: 7DOF Paper Method To UR10e 6DOF

This is a preliminary transfer note. It records the current UR10e adapted
formulation target before PDF truth extraction is complete.

## Variables And Frames

- `q in R^6`: UR10e joint vector.
- `qdot in R^6`: UR10e joint velocity.
- `x in SE(3)`: TCP pose.
- `V = [v; omega] in R^6`: TCP spatial velocity in the chosen control frame.
- `J(q) in R^(6x6)`: UR10e geometric Jacobian, with `V = J(q) qdot`.
- `f_tcp in R^3`: TCP force vector after selecting a force source and frame.
- `n in R^3`: contact surface normal, unit length.
- `P_t = I - n n^T`: tangential projection matrix.
- `f_n = n^T f_tcp`: scalar normal force.
- `f_d`: desired normal force.

All force signs must be verified in MuJoCo and then again against the selected
hardware force source. Existing OnRobot TCP DAQ values are not control truth.

## Finite-Time Error Law

For an error `e`, the scalar finite-time template is:

```text
e_dot = -k |e|^r sign(e), 0 < r < 1, k > 0
```

With `V(e) = 0.5 e^2`, the derivative satisfies a finite-time style bound:

```text
V_dot = -k |e|^(r+1) = -c V^((r+1)/2)
```

Since `(r + 1) / 2 < 1`, convergence is finite-time under the continuous-time
ideal assumptions. The simulation implementation still needs discrete-time
stability checks and saturation logging.

## Force-Motion Split

For a contact normal `n`, tangential motion is:

```text
v_t = P_t v
```

Normal force feedback can be converted into a desired normal velocity term:

```text
v_n_cmd = -k_f |f_n - f_d|^r sign(f_n - f_d)
v_cmd = v_t_des + n v_n_cmd
```

The sign is provisional. It must be tested by increasing penetration in
MuJoCo and confirming whether `f_n` increases in the expected direction.

## UR10e 6DOF Transfer

The paper's 7DOF setting can use redundancy for secondary objectives. UR10e
has no spare joint dimension in the generic nonsingular case because:

```text
J(q) in R^(6x6)
```

Therefore joint-limit avoidance, posture objectives, and optional orientation
compliance cannot be assumed to fit in a null space. They must be formulated as
prioritized tasks or soft residuals.

## Proposed QP

At each control step, solve for `qdot` and slacks:

```text
minimize
  ||W_f (A_f J qdot - b_f)||^2
  + ||W_t (A_t J qdot - b_t)||^2
  + ||W_o (A_o J qdot - b_o)||^2
  + ||W_s s||^2
  + lambda ||qdot||^2

subject to
  qdot_min <= qdot <= qdot_max
  q_min + margin <= q + dt qdot <= q_max - margin
  hard force/contact safety bounds
```

Task meaning:

- `A_f`: normal force regulation task.
- `A_t`: tangential tracking task.
- `A_o`: orientation compliance task.
- `s`: slack for soft tasks, never for hard joint or velocity limits.

Priority:

1. Joint and velocity limits: hard.
2. Contact safety bounds: hard.
3. Normal force regulation: highest task weight.
4. Tangential tracking: soft with logged slack.
5. Orientation compliance: soft and disable-able.

If the QP is infeasible, output no motion in simulation and record
`ControllerInfeasibleError`. Do not clip `qdot` after solving and call it
successful.

## Immediate Tests Needed

- Finite-time scalar convergence ordering for `r = 0.2..1.0`.
- Jacobian finite-difference check.
- Contact force sign check.
- QP hard-limit test.
- Slack and infeasible-solver logging test.

## V1 Contract Implementation

The first testable contracts are now represented in code:

- `src/tase_repro/finite_time.py`: scalar finite-time template.
- `src/tase_repro/kinematics.py`: MuJoCo model loading, joint metadata, TCP
  site Jacobian, and finite-difference Jacobian check.
- `src/tase_repro/contact.py`: contact normal, tangential projector, force
  error velocity template, and sphere-plane penetration helper.
- `src/tase_repro/constraints.py`: bounded velocity least-squares contract
  enforcing velocity and one-step position limits inside the solve.

Verification command:

```bash
scripts/run_tests.sh
```

Current result: `11 passed`.

## V2 Controller Smoke

The first simulation-only controller path is now represented by:

- `src/tase_repro/controller.py`
- `scripts/run_controller_smoke.py`
- `tests/test_controller.py`

The controller solves a velocity-level TCP linear velocity task with hard
joint and velocity bounds enforced inside the bounded least-squares solve. It
does not perform force control or contact control.

Verification:

```bash
scripts/run_tests.sh
python3 scripts/run_controller_smoke.py --config configs/mujoco_ur10e.yaml --duration-s 1.0
```

Current result:

- `13 passed`
- `solver_success_fraction = 1.0`
- `max_qdot_violation_rad_s = 0.0`
- `max_joint_limit_violation_rad = 0.0`

## V3 Static Contact Force Ladder

The first contact-model force ladder is represented by:

- `src/tase_repro/contact_ladder.py`
- `scripts/run_contact_force_ladder.py`
- `tests/test_contact_ladder.py`
- `reports/contact_force_ladder_report.md`

The method calibrates tiny `base_link` z offsets to produce static MuJoCo
contact normal forces. It verifies contact force sign and target-force
measurement behavior, not closed-loop force control.

Verification:

```bash
scripts/run_tests.sh
python3 scripts/run_contact_force_ladder.py --config configs/mujoco_ur10e.yaml --steps 500 --tail-steps 100 --tolerance-N 0.01
```

Current result:

- `15 passed`
- target forces `[0.5, 1.0, 2.0, 5.0] N`
- max absolute force error `0.0088706346160502 N`
