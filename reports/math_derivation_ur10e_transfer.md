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

## V4 Stationary Force Feedback

The first closed-loop stationary normal-force feedback smoke is represented by:

- `src/tase_repro/force_feedback.py`
- `scripts/run_stationary_force_feedback.py`
- `tests/test_force_feedback.py`
- `reports/stationary_force_feedback_report.md`

It combines:

- positive MuJoCo contact-frame normal force;
- finite-time force error command;
- bounded velocity-level UR10e joint solve;
- hard velocity and joint-limit metrics.

Verification:

```bash
scripts/run_tests.sh
python3 scripts/run_stationary_force_feedback.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5
```

Current result:

- `16 passed`
- initial force `5.886648180968636 N`
- final force `5.000002800044511 N`
- tail mean absolute force error `2.8000475610912012e-06 N`
- solver success fraction `1.0`
- max qdot violation `0.0`
- max joint-limit violation `0.0`

## V5 Tangential Force-Motion Smoke

The first low-speed force-motion smoke is represented by:

- `scripts/run_tangential_force_motion.py`
- `tests/test_force_motion.py`
- `reports/tangential_force_motion_report.md`
- extended `src/tase_repro/force_feedback.py`

It adds tangential x motion while retaining the normal-force feedback command:

```text
v_cmd = [v_tangent + Kp * (p_desired_tangent - p_tangent), v_normal_force]
```

Verification:

```bash
scripts/run_tests.sh
python3 scripts/run_tangential_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --tangential-velocity 0.0005,0.0 --tangential-kp 0.5
```

Current result:

- `17 passed`
- final x displacement `0.0019989989469737 m`
- desired x displacement `0.0019990000000000008 m`
- tail mean absolute force error `1.775978411200585e-05 N`
- solver success fraction `1.0`
- contact present fraction `1.0`
- max qdot violation `0.0`
- max joint-limit violation `0.0`

## V6 Paper E1 Cycloid Force-Motion Smoke

The first paper-shaped planar force-motion smoke is represented by:

- `src/tase_repro/trajectories.py`
- `scripts/run_paper_trajectory_force_motion.py`
- `tests/test_trajectories.py`
- `reports/paper_trajectory_force_motion_report.md`

It uses the PDF-extracted Section VI Experiment 1 cycloid:

```text
x = x0 + 0.015 * (0.1 t - sin(0.1 t))
y = y0 + 0.015 * (1 - cos(0.1 t))
```

The controller remains:

```text
v_cmd = [v_planar_desired + Kp * (p_desired_planar - p_planar), v_normal_force]
```

Verification:

```bash
scripts/run_tests.sh
python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --trajectory e1-cycloid --amplitude-m 0.015 --omega-rad-s 0.1 --paper-time-scale 1.0 --planar-kp 0.5
```

Current result:

- `20 passed`
- final tangential displacement `[0.0012394851720925958, 0.004549066283786667] m`
- desired tangential displacement `[0.0012387489718280922, 0.00454724750054618] m`
- tail mean absolute force error `0.00898488092600231 N`
- solver success fraction `1.0`
- contact present fraction `1.0`
- max qdot violation `0.0`
- max joint-limit violation `0.0`

## V7 Paper Trajectory Matrix

The planar trajectory library now covers the PDF-extracted Section VI E1-E4
trajectory family:

- E1 cycloid.
- E2 figure-eight.
- E3 circle.
- E4 cardioid.

Verification:

```bash
scripts/run_tests.sh
```

Current test result: `25 passed`.

Simulation matrix evidence:

- `runs/paper_trajectory_matrix/20260524T014139`: full-speed matrix under
  `0.05 rad/s`; E2/E3 lost contact.
- `runs/paper_trajectory_matrix/20260524T014244`: full-speed matrix under
  `0.15 rad/s`; E2/E3 still lost contact.
- `runs/paper_trajectory_matrix/20260524T014344`: low-speed matrix with
  `paper_time_scale = 0.25`; all E1-E4 trajectories maintained contact and
  hard-limit compliance.

Accepted low-speed matrix result:

| trajectory | tail mean abs force error N | max position error m | solver success | contact present |
| --- | ---: | ---: | ---: | ---: |
| E1 cycloid | `2.7377314706467093e-06` | `1.2975956668356727e-07` | `1.0` | `1.0` |
| E2 figure-eight | `0.22110301894575918` | `2.236053449085177e-06` | `1.0` | `1.0` |
| E3 circle | `0.07713928700031802` | `1.4999786407036843e-06` | `1.0` | `1.0` |
| E4 cardioid | `2.7477968988542934e-06` | `2.621139110103472e-07` | `1.0` | `1.0` |

## V8 Weighted Normal Force-Motion Diagnostic

The velocity solve now supports row-wise Cartesian axis weights:

```text
minimize ||W_axis (Jp qdot - v_cmd)||^2 + damping ||qdot||^2
```

The diagnostic full-speed matrix used:

- `axis_weights = [1, 1, 100]`
- `force_gain = 5e-4`
- `qdot_limit = 0.15 rad/s`
- `paper_time_scale = 1.0`

Result:

| trajectory | tail mean abs force error N | contact present | max position error m | max qdot rad/s |
| --- | ---: | ---: | ---: | ---: |
| E1 cycloid | `0.00033862693701109726` | `1.0` | `1.9594095253937445e-06` | `0.14999999924398735` |
| E2 figure-eight | `0.04680027821015285` | `1.0` | `0.02114519099848796` | `0.14999999999999997` |
| E3 circle | `0.013411903132922096` | `1.0` | `0.016169767707432416` | `0.14999999999999997` |
| E4 cardioid | `0.0015612634092028888` | `1.0` | `0.0016367063021719241` | `0.14999999999999997` |

Interpretation:

Axis weighting can rescue contact and force regulation, but E2/E3 still fail
the trajectory-tracking bar. This supports moving from a blended least-squares
controller to a prioritized or slack-aware solve.
