# Stage A Contact Path Audit Report

## Summary

v61 adds an offline quasi-static contact-manifold path audit from the ordinary
setup initial q to the v58 selected
`ur10e_adapted_terminal_setup_diagnostic` target.

The formal run is:

- `runs/stage_a_contact_path_audit/20260524T151201`
- command: `scripts/audit_stage_a_contact_path.py`
- code commit: `878bb1649f876344f703a3a4d8156ece32847c12`

The audit finds a 128-knot optimized path that keeps target contact, target
force, scheduled x/y, and scheduled orientation within the diagnostic path
criteria. The minimum duration required to respect the `0.15 rad/s` joint
velocity limit is `14.332635022800167 s`.

## Metrics

From `runs/stage_a_contact_path_audit/20260524T151201/metrics.yaml`:

- path gate pass: `true`
- terminal diagnostic gate pass: `true`
- target contact present fraction: `1.0`
- max force error: `0.005097546556703136 N`
- max scheduled x/y error: `8.729156782886492e-09 m`
- max scheduled orientation error: `3.761810174085662e-07 rad`
- terminal force error: `0.005097546556703136 N`
- terminal reference x/y error: `0.0030075762251302427 m`
- terminal force-normal orientation error: `0.07240605683117463 rad`
- max force-normal orientation error along the path:
  `0.17453292523411995 rad`
- min duration for `0.15 rad/s`: `14.332635022800167 s`
- max qdot at that duration: `0.15 rad/s`
- qdot saturation fraction at that duration: `0.007874015748031496`
- all intermediate least-squares knots report solver success

## Claim Boundary

This result is useful because it closes the previous "no Stage A path from the
ordinary initial q" gap at the offline kinematic/contact-manifold level.

It does not prove:

- an online Stage A controller can track the path
- robustness to controller discretization, contact transients, or model error
- strict paper-equivalent trajectory feasibility
- hardware readiness

The path uses scheduled orientation interpolation from the initial pose to the
selected target. It does not keep the force-normal orientation under the
terminal diagnostic threshold at every intermediate knot; the reported maximum
along-path force-normal orientation error is `0.17453292523411995 rad`.

## Next Step

Use this path as a target for an online qdot-aware Stage A tracking prototype.
Keep the v60 slowed handoff parameters and this v61 offline path in separate
claim buckets until one executable controller reaches the selected target and
then performs the handoff under one explicit timing and acceptance policy.
