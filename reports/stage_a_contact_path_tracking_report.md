# Stage A Contact Path Tracking Report

## Summary

v62 tracks the v61 offline contact path with a qdot-limited joint-path replay
prototype. The tracker reads
`runs/stage_a_contact_path_audit/20260524T151201/path.csv`, follows the path
over `15.0 s`, and evaluates every simulated sample against the same target
contact, force, scheduled x/y, scheduled orientation, qdot, and terminal
diagnostic gates.

The formal run is:

- `runs/stage_a_contact_path_tracking/20260524T152346`
- command: `scripts/track_stage_a_contact_path.py`
- code commit: `6edddf4a05fae2671ee91f62bc653ec11d2f6058`

## Metrics

From `runs/stage_a_contact_path_tracking/20260524T152346/metrics.yaml`:

- tracking gate pass: `true`
- terminal diagnostic gate pass: `true`
- duration: `15.0 s`
- sample count: `7501`
- max qdot: `0.14332635022814824 rad/s`
- max qdot utilization: `0.9555090015209883`
- qdot saturation fraction: `0.0`
- final tracking error norm: `0.0 rad`
- target contact present fraction: `1.0`
- max force error: `0.13962429878283 N`
- max scheduled x/y error: `8.352155120555089e-08 m`
- max scheduled orientation error: `3.7582991511547844e-07 rad`
- terminal force error: `0.005097546556703136 N`
- terminal reference x/y error: `0.0030075762251302427 m`
- terminal force-normal orientation error: `0.07240605683117463 rad`

## Claim Boundary

This result upgrades v61 from an offline path existence audit to an executable
qdot-limited joint-path tracking prototype.

It does not prove:

- a force-feedback optimizer can recover from path disturbances
- robustness to contact transients or model error
- a connected Stage A plus Stage B trajectory claim
- strict paper-equivalent feasibility
- hardware readiness

The tracker follows the v61 path in joint space. It is intentionally narrower
than a full online force-motion controller. It also does not connect the final
Stage A state to the v60 slowed low-gain handoff in this run.

## Next Step

Run a single stitched simulation that executes the v62 Stage A tracker and then
the v60 slowed handoff under one explicit timing and acceptance policy. Keep
the stitched result separate from strict paper-equivalent feasibility unless it
uses the strict setup and trajectory labels.
