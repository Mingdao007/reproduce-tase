# Contact Orientation Calibration Margin Report

## Objective

V85 is a bounded post-hoc calibration/definition audit for the remaining
weighted `+1.0 mm`, `0.119 rad` diagnostic orientation miss. It asks what
physical or modeling correction would be sufficient to close the margin, while
preserving the existing claim boundary.

This audit does not rerun MuJoCo with a calibrated model, does not change
controller defaults, and does not accept a replacement diagnostic gate.

## Source Runs

- v84 weighted orientation model sensitivity:
  `runs/weighted_orientation_model_sensitivity/20260524T233945/metrics.yaml`
- v83 weighted gate/time matrix:
  `runs/weighted_gate_time_matrix/20260524T232637/metrics.yaml`
- v69 positive terminal orientation audit:
  `runs/positive_terminal_orientation/20260524T171705/metrics.yaml`
- v77 positive orientation-gate boundary:
  `runs/positive_orientation_gate_boundary/20260524T221842/metrics.yaml`

## Command

```bash
python3 scripts/audit_contact_orientation_calibration_margin.py
```

Formal run:

- `runs/contact_orientation_calibration_margin/20260524T235723`

Parent commit before v85 changes:

- `49083e145d0ff5b3741c40139527b772cd9345a7`

## Critical Rows

| group | time scale | Stage A orientation | Stage B orientation | Stage B excess over `0.119` | qdot saturation | tail qdot |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `time0p0075_gate0p119:weighted_kp0_normal1` | `0.0075` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` | `0.5177926211135458` |
| `time0p0075_gate0p119:weighted_kp0_normal30` | `0.0075` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` | `0.5177926211135458` |
| `time0p01_gate0p119:weighted_kp0_normal1` | `0.01` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` | `0.520987929048311` |
| `time0p01_gate0p119:weighted_kp0_normal30` | `0.01` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` | `0.520987929048311` |

The hardest row is
`time0p01_gate0p119:weighted_kp0_normal1`, tied numerically with the
`normal30` row.

## Equivalent Corrections

| quantity | value |
| --- | ---: |
| required normal rotation | `0.0005664520369604714 rad` |
| required normal rotation | `0.03245531101442353 deg` |
| continuous required gate | `0.11956645203696047 rad` |
| discrete v83 first passing gate at `paper_time_scale = 0.01` | `0.1196 rad` |
| terminal slope proxy | `0.03785584200850284 rad/mm` |
| equivalent base-z/contact-point correction | `0.014963398168061883 mm` |
| equivalent base-z/contact-point correction | `14.963398168061882 um` |
| contact-point versus legacy-center orientation delta | `0.024227219479550713 rad` |
| convention-shift / required-rotation ratio | `42.77011626536238` |

The required correction is small relative to the current unmeasured
contact-convention sensitivity. It is not an accepted measurement-noise claim:
there is no measured TCP/contact point, contact patch, plane normal, or
force-frame calibration budget in the repository yet.

## Gate Options

| gate option | recovered by existing metric | accepted replacement gate | evidence scope |
| --- | --- | --- | --- |
| `0.119` | `false` | `false` | full positive-delta weighted matrix fails at `+1.0 mm` |
| `0.11955` | `true` | `false` | focused `+1.0 mm`, `paper_time_scale = 0.0075` boundary only |
| `0.1196` | `true` | `false` | focused `+1.0 mm`, `paper_time_scale = 0.01` boundary only |
| `0.11995` | `true` | `false` | full positive-delta weighted matrix at `paper_time_scale = 0.01` |

Existing metrics show which rows recover at these gates. They do not justify
accepting `0.11955 rad`, `0.1196 rad`, or `0.11995 rad` as a replacement
diagnostic gate without calibrated geometry/normal evidence.

## V85 Answers

1. Remaining margin: the hardest known row exceeds the `0.119 rad` gate by
   `0.0005664520369604714 rad` (`0.03245531101442353 deg`).
2. Required normal correction: at least the same
   `0.0005664520369604714 rad` if the correction acts in the error-reducing
   direction.
3. Equivalent geometry correction: `0.014963398168061883 mm`
   (`14.963398168061882 um`) under the v84 high-end terminal slope proxy.
4. Plausibility: the correction is small relative to the current unmeasured
   contact-convention ambiguity, but no accepted measurement noise budget
   exists.
5. Required measurements: mounted-stack TCP/contact point, contact patch or
   sphere convention, plane normal in robot base frame, force-source frame and
   zero reconciliation, and accepted force-normal versus full-frame
   orientation-gate definition.
6. Gate acceptance: existing metrics do not justify replacing the current gate
   by `0.11955`, `0.1196`, or `0.11995 rad`.
7. Stage B qdot tuning: not supported as the next primary action because the
   critical weighted rows have `0.0` qdot saturation.

## Interpretation

V85 strengthens the v84 attribution. The remaining miss is a small
calibration/definition margin, not a qdot-saturation problem. The useful next
step is measured geometry and contact/normal definition work, or a documented
accepted diagnostic gate derived from those measurements.

The legacy sphere-center model remains only a sensitivity comparison. It is
not an acceptable calibrated model by itself.

## Claim Boundary

This audit is not:

- a recovery of the `+1.0 mm`, `0.119 rad` gate
- an accepted relaxed diagnostic gate
- a calibrated contact model
- a canonical controller default
- a robustness proof
- strict paper-equivalent feasibility
- hardware readiness or authorization to move/configure the real UR10e

## Validation

- `python3 -m py_compile scripts/audit_contact_orientation_calibration_margin.py`
  passed.
- `python3 scripts/audit_contact_orientation_calibration_margin.py` produced
  `runs/contact_orientation_calibration_margin/20260524T235723`.
- `scripts/run_tests.sh`: `115 passed in 2.69s`.
- `git diff --check` passed.
- Artifact audit: `4` files, `48K`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under `runs/contact_orientation_calibration_margin/20260524T235723`.
- Branch push was verified at
  `e9603612a47fed63e19d9aa0f90bd925d2015991`.

## Next Executable Step

Collect or define the missing calibration facts before another controller
tuning branch: mounted-stack TCP/contact point, contact surface convention,
plane normal in the robot base frame, and force-source/frame reconciliation.
Any real-hardware work remains read-only unless the user approves a separate
hardware SOP.
