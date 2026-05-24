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

## V9 Normal Guard Diagnostic

The force-motion simulation now records `planar_scale` and can apply a scalar
normal-force guard:

```text
scale = clamp(force / (force_target * guard_fraction), min_scale, 1)
v_xy_guarded = scale * v_xy_command
```

Diagnostic result:

- Equal-axis guarded E2/E3 still lost force at full speed.
- Guarded `normal_axis_weight = 50` kept E1-E4 in contact but did not remove
  the force/tracking tradeoff.

Guarded `normal_axis_weight = 50` matrix:

| trajectory | tail force error N | max position error m | contact present |
| --- | ---: | ---: | ---: |
| E1 cycloid | `0.00033856499675277707` | `1.9594057514147845e-06` | `1.0` |
| E2 figure-eight | `0.5085483615637729` | `0.020166709027307318` | `1.0` |
| E3 circle | `0.14769228903285758` | `0.015963081975681002` | `1.0` |
| E4 cardioid | `0.008334236881239064` | `0.0016131684506960832` | `1.0` |

Conclusion:

The scalar guard is not a sufficient full-speed controller. The next solver
must report normal and planar residuals separately and make the task tradeoff
explicit.

## V10 Residual Metrics

The controller result now records unweighted TCP velocity residuals:

```text
residual = actual_linear_velocity - desired_linear_velocity
planar_residual = ||residual_xy||
normal_residual = residual_z
```

Representative full-speed E2/E3 comparison:

| run | tail force error N | contact present | max planar velocity residual m/s | max normal velocity residual m/s | max position error m |
| --- | ---: | ---: | ---: | ---: | ---: |
| E2 equal | `5.0` | `0.46725` | `4.616584808830004e-05` | `0.0012211832551020988` | `6.701093192370075e-05` |
| E2 weighted | `0.04680027821015285` | `1.0` | `0.013308364152647561` | `0.00010776051130989523` | `0.02114519099848796` |
| E3 equal | `5.0` | `0.42725` | `6.865700971642382e-05` | `0.0012373628185900344` | `0.00011339128879628036` |
| E3 weighted | `0.013411903132922096` | `1.0` | `0.0105921848161393` | `5.415531503391008e-05` | `0.016169767707432416` |

This confirms that a future pass/fail gate must inspect residual allocation,
not just `solver_success`.

## V11 Slack-Aware Velocity Solve

The bounded velocity solve now has an opt-in explicit task slack form:

```text
Jp qdot + slack = v_cmd
```

with hard joint/velocity bounds on `qdot` and separate planar/normal slack
penalties.

Representative E2/E3 full-speed result:

| run | normal slack weight | tail force error N | contact present | max planar slack m/s | max normal slack m/s | max position error m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E2 | `100` | `5.0` | `0.568` | `0.0036232839672081176` | `0.0011754316818573876` | `0.0057693956482014275` |
| E2 | `10000` | `0.047984` | `1.0` | `0.013217` | `0.00010718` | `0.021143` |
| E3 | `100` | `5.0` | `0.656` | `0.005359207304529535` | `0.0011612165102032775` | `0.008504621058720654` |
| E3 | `10000` | `0.01441` | `1.0` | `0.010693` | `0.00005457` | `0.016176` |

Interpretation:

The full-speed E2/E3 task is not feasible under the current posture, qdot cap,
and velocity-level controller without accepting large planar slack.

## V15 Orientation-Hold Spatial Velocity Rows

The controller now supports an opt-in stacked spatial velocity task:

```text
[Jp] qdot + s_linear  = v_cmd
[Jr] qdot + s_angular = omega_cmd
```

For the first UR10e-adapted orientation experiment, the desired orientation is
the initial TCP site orientation:

```text
R_desired = R_tcp(t0)
omega_cmd = k_R log(R_desired R_tcp(t)^T)
```

This keeps hard joint and velocity bounds on `qdot` and reports:

- orientation error rotation-vector norm;
- angular velocity residual;
- angular slack;
- force/contact/planar gates from v12.

Orientation is deliberately a soft task. The v15 sweep shows the 6DOF
allocation tradeoff:

| angular slack weight | E1-E4 force-motion gate pass | max orientation error rad | max angular slack rad/s | interpretation |
| ---: | ---: | ---: | ---: | --- |
| `0.1` | `0/4` | `0.022792200960046364` | `0.024703715417836912` | stronger angular priority breaks planar tracking |
| `0.001` | `3/4` | `0.0792791337407633` | `0.0869211753487964` | E2 fails sustained qdot utilization |
| `0.0001` | `4/4` | `0.08108796381776726` | `0.08895566203803207` | preserves force-motion gates with weak orientation hold |

Therefore v15 turns orientation from an unmodeled omission into a measured
soft task, but it does not yet establish paper-faithful orientation
compliance. A future gate must define acceptable orientation error and decide
whether that gate is feasible through timing, posture, or stricter task
priority.

## V16 Orientation Feasibility Gates

The feasibility evaluator now optionally adds orientation gates:

```text
max ||log(R_desired R_tcp(t)^T)|| <= epsilon_R
max ||s_angular|| <= epsilon_sR
```

The first provisional values are:

```text
epsilon_R = 0.03 rad
epsilon_sR = 0.03 rad/s
```

With angular slack weight `0.1` and the v14 `bend_0p10` posture, the fastest
tested passing scales are:

| trajectory | fastest passing scale |
| --- | ---: |
| E1 cycloid | `0.5` |
| E2 figure-eight | `0.1` |
| E3 circle | `0.075` |
| E4 cardioid | `0.5` |

A common E1-E4 matrix at `paper_time_scale = 0.075` passes all current force,
contact, planar, qdot, joint-limit, orientation-error, and angular-slack
gates. This gives a conservative orientation-gated simulation baseline, while
showing that full-speed orientation-gated UR10e transfer remains infeasible
under the current velocity-level controller and posture.

## V17 Orientation-Gated Posture Search

The v17 posture search tests whether the full-speed E2/E3 blocker can be
removed by changing the initial UR10e posture while keeping the same
orientation-hold gate:

```text
paper_time_scale = 1.0
epsilon_R = 0.03 rad
epsilon_sR = 0.03 rad/s
```

Only `bend_0p10` and `bend_0p125` calibrated to the `5 N` initial-contact
target in the default MuJoCo base-offset bracket. Larger tested bends were
recorded as calibration failures rather than aborting the sweep.

At angular slack weight `0.1`, the calibrated postures pass the orientation
gates for E2/E3 but fail planar position/slack gates. Reducing angular slack
weight through `0.03`, `0.01`, and `0.003` shows the expected tradeoff: planar
tracking improves, but E3 loses the orientation gate before a combined
full-speed pass appears.

Therefore small posture tuning and scalar angular-priority tuning are not
enough to recover full-speed orientation-gated E2/E3 with the current
velocity-level 6DOF formulation. The next mathematical step is a task-priority
or null-space-aware solve, or a more faithful extraction of the paper's
orientation signal.

## V18 Linear-Primary Orientation Hierarchy

The v18 controller adds a two-stage velocity hierarchy for orientation hold.
First, solve the linear force-motion task:

```text
Jp qdot_1 + s_p = v_cmd
```

with the same hard joint and velocity bounds as v16/v17. Then solve the
secondary orientation problem:

```text
min ||Jr qdot - omega_cmd||^2
subject to Jp qdot = Jp qdot_1
           qdot_min <= qdot <= qdot_max
```

This preserves the first-stage TCP linear velocity instead of trading planar
tracking against orientation through a single weighted slack objective.

The result is cleaner but not faster. At full speed, E2 and E3 keep very small
planar error and slack, but orientation correction saturates the `0.15 rad/s`
qdot cap and still violates orientation gates. Both trajectories pass the
combined gates at `paper_time_scale = 0.075`; the E1-E4 common `0.075` matrix
also passes.

Therefore the current best orientation-gated UR10e simulation baseline remains
slowed to `0.075`, now with a more defensible linear-primary controller. Moving
toward full speed likely requires the paper-specific orientation law,
trajectory/orientation scheduling, or an explicit qdot-budget decision rather
than more scalar task weighting.

## V19 Paper Orientation Truth Extraction

The paper's orientation compliance law is not an initial-orientation hold. The
PDF-grounded contract is:

```text
u = F / ||F||, u in R^3
S = skew(u)
R_d = I + sin(u) S + (1 - cos(u)) S^2
e_qua = Q_d^-1 Q
xdot_o = xdot_od + k_o e_o
```

For an unknown surface, the paper assumes the desired angular velocity cannot
be obtained and the orientation process is slow, so `xdot_od = 0` and
`xdot_o = k_o e_o`, with an angular-velocity limit.

This creates a transfer gap for the current UR10e implementation:

- Section III defines `u` as a 3D normalized force vector.
- Section V gives `u = [cos(0.1t), sin(0.1t)]`, which is only two-dimensional
  in the extracted text.
- Eq. (10) uses `sin(u)` and `cos(u)` even though `u` has just been defined as
  a vector, so the intended scalar angle/axis construction is not uniquely
  recoverable from text extraction alone.

Therefore the v18 linear-primary controller remains a valid UR10e adapted
orientation-hold feasibility baseline, but not a paper-faithful orientation
compliance implementation. The next derivation step must define one of:

- a paper-faithful interpretation of the missing third component and scalar
  angle in the orientation signal;
- an explicitly adapted UR10e orientation schedule with its own decision
  record and acceptance gates;
- or a manual figure/source audit that proves the extracted text omitted
  required notation.

## V20 Orientation Signal Audit Resolution

The manual/source audit did not find omitted notation. Layout, raw,
fixed-width, XML, and bbox extraction all preserve the same mismatch:

- Section III: `u = F / ||F||`, `u in R^3`, with Eq. (9) using `u1`, `u2`,
  and `u3`.
- Section V: `u = [cos(0.1t), sin(0.1t)]`.

Therefore the missing third component should not be guessed. For the UR10e
transfer, the next paper-oriented implementation should use a 3D force-normal
orientation target:

```text
u_force = normalize(F_contact)
```

or, in simulation terms, the contact-normal vector with a clear force-frame
convention. A 2D Section V schedule can still be useful as a synthetic adapted
trajectory, but it must not be reported as the paper's force-normal
orientation compliance law.

## V21 Force-Normal Orientation Convention

The first UR10e adapted implementation of the Section III orientation contract
uses the measured/simulated 3D contact-normal force vector:

```text
u_force = normalize(F_contact)
R_desired[:, 2] = u_force
omega_cmd = k_o log(R_desired R_tcp^T)
```

Because the paper does not specify yaw about `u_force`, this repo preserves
the initial TCP local x-axis projected into the tangent plane. This is an
explicit adaptation:

```text
x_desired = normalize(x_initial - u_force (u_force^T x_initial))
y_desired = normalize(u_force x x_desired)
R_desired = [x_desired, y_desired, u_force]
```

This makes the orientation target testable without pretending the Section V
2D signal supplied a hidden third component. The current flat-plane MuJoCo
smoke has `u_force = [0, 0, 1]`, so it verifies the data path and constraints.
A tilted or curved contact surface is still needed to validate nontrivial
force-normal orientation adaptation.

## V22 Tilted-Plane Normal Mapping

The tilted-plane model rotates the analytic MuJoCo plane 10 degrees about the
world y-axis, so the expected contact normal is:

```text
n_tilt = [sin(10 deg), 0, cos(10 deg)]
       = [0.1736481777, 0.0, 0.9848077530]
```

The scalar finite-time force correction remains a one-dimensional normal-force
task. On the tilted surface, however, the scalar correction should be mapped
along the measured contact-normal direction rather than hard-coded to world z:

```text
v_normal = v_f n_tilt
v_cmd = v_tangent + v_normal
```

where `v_f` is the force feedback scalar and `v_tangent` is the x/y paper
trajectory command. This is implemented as `normal_velocity_mode =
"contact_normal"` while retaining the older `world_z` default for historical
flat-plane runs.

The same measured force-normal vector drives the v21 orientation target:

```text
R_desired[:, 2] = normalize(F_contact) ~= n_tilt
```

The first tilted smokes show that the geometric mapping works but the
orientation transition is now constrained by the UR10e velocity budget. A high
orientation gain reduces the error faster but saturates the `0.15 rad/s` qdot
limit; a low gain preserves qdot margin but leaves the TCP orientation far from
the tilted normal over the tested duration. The next derivation/controller
decision should therefore be a staged orientation approach or an explicit
velocity-budget relaxation, not an unlabeled scalar-gain tweak.

## V23 Tilted Orientation Gate Implication

The tilted gain/timing sweep confirms a structural issue with the current gate
definition and controller start condition. The desired force-normal orientation
changes from the flat initial TCP orientation to the tilted normal at the first
paper-trajectory sample:

```text
theta_initial ~= acos([0, 0, 1]^T n_tilt) ~= 0.1745 rad
```

The existing orientation gate is a maximum-error gate:

```text
max_t ||e_R(t)|| <= 0.03 rad
```

Therefore any run that begins from the old flat orientation and immediately
uses the tilted force-normal target is rejected before gain tuning can help.
Low gains preserve qdot margin but keep `max ||e_R|| ~= 0.174 rad`; higher
gains reduce the tail more quickly but exceed the qdot and angular-slack
budgets.

The correct next simulation transfer is a two-stage task:

```text
stage A: align TCP local z to n_tilt under qdot and angular-slack limits
stage B: start paper trajectory only after ||e_R|| <= gate
```

If stage A is not added, the alternative is an explicit decision to relax the
`0.15 rad/s` qdot budget or the max-error gate. That would be an adapted UR10e
assumption, not a paper-faithful result.

## V24 Staged Orientation Approach Transfer

The first staged implementation separates the initial tilted-normal alignment
from the paper trajectory:

```text
Stage A:
  v_xy,desired = 0
  v_normal = v_f n_tilt
  omega_desired = k_o log(R_normal R_tcp^T)

Stage B:
  reset trajectory origin at Stage A terminal TCP pose
  run paper x/y trajectory with force-normal orientation already near gate
```

This changes the meaning of the orientation gate. The Stage B gate is no
longer dominated by the initial `0.174 rad` tilt mismatch, so the E1 trajectory
phase can pass with:

```text
max ||e_R|| = 0.0020303573682621625 rad
qdot saturation fraction = 0.003
```

However, Stage A uses a weighted orientation solve rather than the
linear-primary trajectory solve. It reaches:

```text
final ||e_R|| = 0.0020237968932491765 rad
first ||e_R|| <= 0.03 rad at 0.912 s
```

but also records:

```text
qdot saturation fraction = 0.961
max planar drift = 0.009738544642078033 m
max angular slack = 0.06085033484246333 rad/s
```

Therefore v24 is a useful decomposition, not a complete maneuver solution.
The UR10e transfer now needs either an approach controller that reduces planar
drift and sustained qdot saturation, or an explicit decision that approach and
paper-trajectory tracking use different budgets/gates.

## V25 Stage A Bracket Implication

The Stage A bracket tested whether the v24 approach failure can be repaired by
changing only scalar gains and slack weights:

```text
approach priority in {weighted, linear-primary}
k_o in {0.5, 1.0, 2.0}
planar slack weight in {1, 10, 100}
angular slack weight in {1, 10}
```

No case satisfies the ordinary approach feasibility gate. The weighted cases
can make the terminal orientation small enough for the following E1 trajectory
to pass, but they do so by spending the velocity budget:

```text
trajectory-enabling weighted qdot saturation fraction in [0.8875, 0.9995]
planar drift in [0.007650647578364729, 0.012530340042995497] m
```

The linear-primary approach preserves planar position:

```text
max planar drift = 9.543399245007592e-06 m
```

but it stalls above the orientation threshold:

```text
final ||e_R|| = 0.07414766093770783 rad > 0.03 rad
```

Therefore the current transfer cannot be finished by reweighting the same
velocity-level objective. The next derivation step needs an explicit approach
schedule or a different approach controller that treats position hold,
force-normal alignment, contact maintenance, and qdot budget as separate
contracts.

## V26 Longer Approach Implication

Longer lower-gain approaches test the hypothesis that the v25 issue is only a
duration problem. The tested weighted schedules were:

```text
(k_o, T_A) in {(0.50, 4s), (0.35, 6s), (0.25, 8s), (0.15, 12s), (0.10, 18s)}
```

Only the first three reached the terminal orientation threshold, and none
passed the terminal approach budget:

```text
qdot saturation fraction remains >= 0.5261111111111111
tail max qdot utilization remains 1.0
max planar drift remains >= 0.0039015944234095656 m
```

The long `linear-primary` reference preserves planar position but does not
solve orientation alignment:

```text
final ||e_R|| = 0.07416325057807228 rad
```

Therefore the Stage A problem is not just scalar timing. The next controller
derivation should add an explicit orientation-rate-limited schedule or another
mechanism that caps desired angular velocity before the hard joint-velocity
solve, while separately tracking position hold, contact force, and terminal
orientation.
