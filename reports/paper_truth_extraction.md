# Paper Truth Extraction

Date: 2026-05-24

Branch: `exp/tase-ur10e-v19-paper-orientation-truth`

Source PDF:

`/home/andy/Zotero/storage/UZRF97KG/Xu 等 - 2026 - Finite-Time Convergence Neural Network-Based Force-Motion Control for Unknown Surface With Orientati.pdf`

Extraction commands:

```bash
pdfinfo "<paper-pdf>"
pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt
wc -l /tmp/tase_paper_layout.txt
```

Extraction metadata:

- `pdfinfo` reports 13 pages and file size `4078389` bytes.
- The layout text extraction produced 886 lines.
- Evidence references below use `/tmp/tase_paper_layout.txt:<line-range>`.

## Scope

This pass updates the PDF-grounded contract for the reproduction. It resolves
the Section VI controller parameters and force-sensor filtering note that were
previously still marked `pending_pdf_verify`, and it records the actual paper
orientation law rather than only the early UR10e orientation-hold substitute.

It does not claim a full paper-faithful implementation. Two items remain open:

- Section V gives a two-component orientation signal, while the orientation
  controller definition requires a three-component force-normal vector.
- Section V leaves `z0` undefined in the extracted text. Section VI defines
  `z0` from the initial manipulator position, but that statement appears in
  the experiment section, not the simulation section.

## Control Objectives And Spaces

The paper's objectives are force control, orientation compliance, motion
tracking, and minimum joint angular velocity with joint angle and velocity
constraints. The evidence is in lines 166-188.

The task-space split is based on specification matrices:

```text
Phi_E = Diag(1, 1, 0)
Phi_bar_E = I - Phi_E
Phi_O = R_d^T Phi_E
Phi_bar_O = R_d^T Phi_bar_E
```

Evidence: `/tmp/tase_paper_layout.txt:178-193`.

Motion control projects the desired planar trajectory through the motion
specification:

```text
xdot_t = Phi_O (xdot_pd + k_p e_p)
```

Evidence: `/tmp/tase_paper_layout.txt:239-247`.

## Orientation Compliance Law

The paper defines the desired orientation from force feedback:

```text
u = F / ||F||,  u in R^3
```

It then builds a skew matrix from `u` and writes the desired rotation as:

```text
S = skew(u)
R_d = I + sin(u) S + (1 - cos(u)) S^2
```

Evidence: `/tmp/tase_paper_layout.txt:250-271`.

Important ambiguity:

- Lines 255-257 define `u = [u1, u2, u3]^T`.
- Line 462 later states the Section V orientation signal as
  `u = [cos(0.1t), sin(0.1t)]`.
- Eq. (10) applies `sin` and `cos` to `u`, even though the preceding line
  defines `u` as a vector. That looks like an axis-angle/Rodrigues notation
  mismatch in the paper text, not enough by itself to implement a faithful
  three-dimensional desired orientation.

The outer-loop orientation controller computes a desired quaternion from
`R_d`, forms quaternion error, converts it to a 3D orientation error, and uses:

```text
xdot_o = xdot_od + k_o e_o
```

For the unknown surface case, the paper sets `xdot_od = 0`, so the implemented
orientation command is the error term `k_o e_o`, with a velocity limit to avoid
excessive initial angular velocity.

Evidence: `/tmp/tase_paper_layout.txt:278-316`.

Implication for this repo:

The current v18 `linear-primary` option is still an adapted UR10e orientation
hold around the initial TCP orientation. It is not the paper's force-normal
orientation compliance law. A paper-faithful implementation needs a deliberate
resolution of the 2D/3D `u` ambiguity and the missing scalar angle in Eq. (10).

## Force-Motion Law

The paper starts from classical impedance:

```text
M_d (xddot_pd - xddot_p)
  + B_d (xdot_pd - xdot_p)
  + K_d (x_pd - x_p)
  = F_d - F
```

Evidence: `/tmp/tase_paper_layout.txt:209-224`.

It then uses an improved impedance model with `K_d = 0` and an integral force
term:

```text
e_p = x_pd - x_p
e_f = F_d - F
xddot_p = (e_f + k_f integral(e_f dt) - B_d xdot_p) / M_d
```

Evidence: `/tmp/tase_paper_layout.txt:278-281` and
`/tmp/tase_paper_layout.txt:318-347`.

The velocity-level command combines motion and force components:

```text
xdot_p(t) =
  Phi_O (xdot_pd + k_p e_p)
  + Phi_bar_O (xdot_p(t - T) + xddot_p(t) T)
```

Evidence: `/tmp/tase_paper_layout.txt:287-296`.

## Optimization And Inner Loop

The dynamic-programming problem minimizes joint velocity norm while enforcing
the Cartesian command and joint constraints:

```text
min  qdot^T qdot / 2
s.t. xdot_c = [xdot_p; xdot_o] = J(theta) qdot
     omega^- <= qdot <= omega^+
```

Evidence: `/tmp/tase_paper_layout.txt:241-254` and
`/tmp/tase_paper_layout.txt:299-336`.

The finite-time RNN inner loop is written as Eq. (23), with tunable `epsilon`
and `r`, and the torque command is written through robot dynamics in Eq. (24).

Evidence: `/tmp/tase_paper_layout.txt:371-411`.

The convergence discussion states that smaller `r` converges faster but can
show early oscillation, while `r` near 1 is slower.

Evidence: `/tmp/tase_paper_layout.txt:442-480`.

## Section V Simulation Verification

PDF-grounded Section V setup:

| item | extracted value | evidence |
| --- | --- | --- |
| initial joint angle | `[0, -pi/4, 0, -3pi/4, 0, pi/2, pi/4]` | lines 457-461 |
| desired trajectory | `[0.2 cos(0.2t), 0.2 sin(0.2t), z0]` | lines 460-461 |
| orientation signal | `[cos(0.1t), sin(0.1t)]` | lines 461-462 |
| joint angle limits | `[-2.5, 2.5] rad` | lines 462-466 |
| joint velocity limits | `[-1.5, 1.5] rad/s` | lines 467-470 |
| desired normal force | `fd = 5 N` | lines 470-472 |

Fig.5 convergence times reported in text:

| r | convergence time |
| --- | ---: |
| 0.2 | about `0.15 s` |
| 0.4 | about `0.26 s` |
| 0.6 | about `0.38 s` |
| 0.8 | about `0.55 s` |
| 1.0 | about `0.89 s` |

Evidence: `/tmp/tase_paper_layout.txt:447-461`.

Remaining Section V gaps:

- `z0` is not defined in the extracted Section V text.
- The Section V orientation signal is two-dimensional, while the orientation
  law in Section III requires a three-dimensional normalized force vector.

## Section VI Experimental Verification

The paper states the experimental platform as a FRANKA manipulator and later
summarizes it as a 7DOF Franka-Panda setup.

Evidence: `/tmp/tase_paper_layout.txt:487-490` and
`/tmp/tase_paper_layout.txt:639-645`.

Section VI defines `z0` for the experiments as the anticipated z position
equal to the initial manipulator position. It also gives the controller
parameters:

```text
M_d = Diag(12, ..., 12)
B_d = Diag(550, ..., 550)
epsilon = 0.022
k_p = 4
k_o = 5
k_f = 1
```

Evidence: `/tmp/tase_paper_layout.txt:487-496`.

The paper says no filter was added to force sensor signals, but an unspecified
communication delay was introduced in orientation control to handle
force-sensor noise before contact.

Evidence: `/tmp/tase_paper_layout.txt:497-503`.

The experimental safety constraints are:

```text
theta in [-3.0, 3.0] rad
qdot in [-0.15, 0.15] rad/s
```

Evidence: `/tmp/tase_paper_layout.txt:504-510`.

### Experiment Matrix

| experiment | surface | trajectory | q0 source | force | timing evidence |
| --- | --- | --- | --- | --- | --- |
| E1 cycloid | fixed material | `x0 + 0.015(0.1t - sin(0.1t))`, `y0 + 0.015(1 - cos(0.1t))` | E1 q0 in lines 526-528 | `-5 N` | contact `2 s`, orientation `6 s`, force error within `+/-1 N` |
| E2 figure-eight | fixed material | `x0 + 0.04 sin(0.1t)`, `y0 + 0.01 sin(0.2t)` | E2 q0 in lines 523-525 | `-5 N` | contact `2 s`, orientation `7 s`, total duration `60 s`, force error within `+/-1 N` |
| E3 circle | variable material | `x0 + 0.03 cos(0.1t)`, `y0 + 0.03 sin(0.1t)` | same as E1 q0 in lines 566-568 | `-5 N` | contact `3.5 s`, orientation `8 s`, position and force `9 s` |
| E4 cardioid | variable material | `x0 + 0.015(2 cos(0.1t) - cos(0.2t))`, `y0 + 0.015(2 sin(0.1t) - sin(0.2t))` | not reprinted in extracted text | `-5 N` | contact `1.5 s`, position `2 s`, orientation and force `7 s` |

Evidence:

- E1/E2: `/tmp/tase_paper_layout.txt:516-545`.
- E3: `/tmp/tase_paper_layout.txt:560-587`.
- E4: `/tmp/tase_paper_layout.txt:602-632`.

## Comparative Experiment

The comparison setup is stated as the same as Experiment 3. The metric is the
Mean Integral of Absolute Error over the force error norm.

Extracted values:

| method | MIAE or reduction |
| --- | ---: |
| proposed framework | `1.190` |
| constant impedance, `K = 10I` | `5.232`, reduction `77.26%` |
| integral impedance | `3.221`, reduction `63.06%` |
| constant impedance, `K = 0` | `2.532`, reduction `53.00%` |
| LQR optimal impedance | reduction `55.72%` |
| DDPG variable impedance | reduction `79.11%` |

Evidence: `/tmp/tase_paper_layout.txt:607-632` and
`/tmp/tase_paper_layout.txt:660-680`.

Extraction note:

Line 623 contains an obvious inconsistent value, `11.90`, in the sentence
describing the first reduction. The surrounding text and arithmetic indicate
the proposed value is `1.190`, which is also stated at lines 615-619 and used
by the other comparison reductions.

## Config Status After V19

`configs/paper_truth.yaml` should now treat these fields as PDF-verified:

- Section V: `q0`, trajectory formula, raw orientation signal, joint limits,
  velocity limits, desired normal force, and Fig.5 `r` sweep timings.
- Section VI: `z0` experiment source, `M_d`, `B_d`, `epsilon`, `k_p`, `k_o`,
  `k_f`, force-filter statement, orientation-delay statement, joint limits,
  velocity limits, E1-E4 trajectory formulas, contact timings, convergence
  timings, and comparison values.

The remaining `pending_pdf_verify` values should be exactly:

- `orientation_signal_dimension_resolution`
- `z0_source`

Those remaining pending values are Section V issues only.

## Implementation Consequences

- Keep calling UR10e results "UR10e adapted reproduction", not "original
  paper platform reproduction".
- The v18 orientation-hold controller is a useful simulation feasibility
  baseline, but it should not be presented as the paper's orientation
  compliance controller.
- The next implementation step should either resolve the paper's orientation
  signal mathematically or add an explicit adapted orientation-scheduling
  decision before further full-speed orientation-gated claims.
