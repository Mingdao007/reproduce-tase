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

