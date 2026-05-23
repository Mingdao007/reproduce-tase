# Paper Truth Extraction

Date: 2026-05-24

Source PDF:

`/home/andy/Zotero/storage/UZRF97KG/Xu 等 - 2026 - Finite-Time Convergence Neural Network-Based Force-Motion Control for Unknown Surface With Orientati.pdf`

Extraction command:

```bash
pdftotext "<paper-pdf>" /tmp/tase_paper.txt
pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt
```

## Scope

This is the first PDF-grounded extraction pass. It resolves several values that
were previously provisional in `configs/paper_truth.yaml`, but it does not yet
close all paper-truth gates.

## Simulation Verification: Section V

The paper states the Section V simulation setup as:

- Initial joint angle:
  `q0 = [0, -pi/4, 0, -3pi/4, 0, pi/2, pi/4]`.
- Desired trajectory and orientation:
  `xpd = [0.2 cos(0.2t), 0.2 sin(0.2t), z0]`.
- Orientation signal:
  `u = [cos(0.1t), sin(0.1t)]`.
- Joint angle bounds:
  `theta_i+ = 2.5 rad`, `theta_i- = -2.5 rad`.
- Joint velocity bounds:
  `thetadot_i+ = 1.5 rad/s`, `thetadot_i- = -1.5 rad/s`.
- Desired normal force:
  `fd = 5 N`.

Fig.5 convergence times reported in text:

| r | convergence time |
| --- | ---: |
| 0.2 | about 0.15 s |
| 0.4 | about 0.26 s |
| 0.6 | about 0.38 s |
| 0.8 | about 0.55 s |
| 1.0 | about 0.89 s |

The text also states that lower `r` converges faster but smaller values can
produce early-stage instability or oscillation.

## Experimental Verification: Section VI

The platform is stated in the conclusion as a `FRANKA-PANDA manipulator with
7-DOFs`.

### Experiment 1

- Trajectory: cycloid.
- Initial joint angles:
  `[0.308701, 0.548698, -0.189603, -2.33053, 0.232508, 2.83806, 0.778152] rad`.
- Desired trajectory:
  `xpd = [x0 + 0.015(0.1t - sin(0.1t)), y0 + 0.015(1 - cos(0.1t)), z0] m`.
- Desired contact force: `fd = -5 N`.
- Contact starts at `t = 2 s`.
- Orientation error converges by about `t = 6 s`.
- Stable contact force error is reported within `+/- 1 N`.
- Surface type: fixed material.

### Experiment 2

- Trajectory: figure-eight.
- Initial joint angles:
  `[0.260378, 0.873101, -0.138578, -1.63611, 0.118616, 2.48961, 0.835513] rad`.
- Desired trajectory:
  `xpd = [x0 + 0.04 sin(0.1t), y0 + 0.01 sin(0.2t), z0] m`.
- Desired contact force: `fd = -5 N`.
- Contact starts at `t = 2 s`.
- Orientation error converges by about `t = 7 s`.
- Total motion duration is stated as `60 s`.
- Stable contact force error is reported within `+/- 1 N`.
- Surface type: fixed material.

### Experiment 3

- Trajectory: circle.
- Desired trajectory:
  `xpd = [x0 + 0.03 cos(0.1t), y0 + 0.03 sin(0.1t), z0] m`.
- Desired contact force: `fd = -5 N`.
- Initial joint angles:
  `[0.308701, 0.548698, -0.189603, -2.33053, 0.232508, 2.83806, 0.778152] rad`.
- Contact starts at `t = 3.5 s`.
- Orientation error converges by about `t = 8 s`.
- Position and force errors converge by about `t = 9 s`.
- Surface type: variable material.

### Experiment 4

- Trajectory: cardioid.
- Desired trajectory:
  `xpd = [x0 + 0.015(2 cos(0.1t) - cos(0.2t)), y0 + 0.015(2 sin(0.1t) - sin(0.2t)), z0] m`.
- Desired contact force: `fd = -5 N`.
- Contact starts at `t = 1.5 s`.
- Position error converges by about `t = 2 s`.
- Orientation and force errors converge by about `t = 7 s`.
- Force error is reported within `+/- 1 N` despite force sensor noise.
- Surface type: variable material.

## Comparative Experiment

The comparison setup is stated as the same as Experiment 3.

- Proposed framework MIAE: `1.190`.
- Constant impedance, `K = 10I`: `5.232`, reduction `77.26%`.
- Integral impedance: `3.221`, reduction `63.06%`.
- Constant impedance, `K = 0`: `2.532`, reduction `53.00%`.
- LQR optimal impedance reduction: about `55.72%`.
- DDPG variable impedance reduction: about `79.11%`.

Text extraction produced one obvious typo-like line, `e0 = 11.90`, in the
paragraph describing the `77.26%` result. The surrounding text and all other
mentions indicate the proposed MIAE is `1.190`.

## Still Unresolved

- Section III orientation signal dimension: the paper defines a force-normal
  vector from force feedback, but Section V writes `u = [cos(0.1t), sin(0.1t)]`.
  This needs a deliberate interpretation before implementation.
- `z0` source and contact surface height are not resolved.
- Dynamic/impedance parameters `Md`, `Bd`, `Kd`, and any gains used in the
  experiment still need extraction or confirmation.
- Table I content was not fully extracted by text conversion; figure/table
  inspection may be required.
- The UR10e 6DOF adaptation must not use 7DOF redundancy or Franka limits.

