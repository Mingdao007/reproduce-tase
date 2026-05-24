# Broad Terminal Feasibility Audit Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v55-broad-terminal-feasibility`

## Scope

This iteration broadens the v54 terminal setup search on the TCP contact-point
model and fixes a terminal-gate weakness: setup force must come from the named
`contact_plane` / `contact_tip` contact pair, not arbitrary MuJoCo contacts.

The work is simulation-only. No real UR10e motion, hardware setting writes,
TCP writes, payload writes, URCap writes, ROS config writes, or OnRobot
configuration changes were performed.

## Gate Fix

Before this iteration, `solve_setup_terminal_ik` used total positive contact
normal force from all MuJoCo contacts. A broad exploratory run showed this can
produce false terminal passes from robot self-collision force while the TCP
site is far from the plane.

The v55 code now:

- computes target force only for the unordered geom pair
  `contact_plane` / `contact_tip`
- records `total_normal_force_N` separately for diagnostics
- records `target_contact_count`
- treats `contact_present` as target-pair contact presence
- adds a regression test for the self-collision false positive

## Broad Audit Run

Run:

- `runs/setup_terminal_ik_audit/20260524T141321`

Command:

```bash
scripts/run_setup_terminal_ik_probe.py \
  --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml \
  --random-seed-count 512 \
  --random-seed-std-rad 2.0 \
  --random-seed 541 \
  --max-nfev 800 \
  --posture-weight 0.0
```

## Result

- candidates: `513`
- terminal setup passes: `0 / 513`
- target contact geom: `contact_tip`
- plane geom: `contact_plane`
- initial target contact count: `1`
- initial target force: `4.9999999999967395 N`
- initial orientation error: `0.17453292523412012 rad`
- best seed: `initial`
- best target contact count: `1`
- best target force: `4.994902453443297 N`
- best force error: `0.005097546556703136 N`
- best x/y error: `0.0030075762251302427 m`
- best orientation error: `0.07240605683117833 rad`
- best failed criteria: `tangential_error_m;orientation_error_rad`

Failure-class counts:

- `512` candidates: `force_error_N;contact_present`
- `1` candidate: `tangential_error_m;orientation_error_rad`

## Interpretation

The wide random seed set does not find a strict terminal setup solution once
force/contact are restricted to the intended tool-plane pair. Most broad seeds
lose target contact entirely and do not recover it through the local
least-squares solve. The only target-contact candidate that stays near the
force objective is still outside the x/y and orientation gates.

This is stronger than the v54 local rerun because it closes the false-positive
self-collision path and broadens the seed distribution. It is still not a
global infeasibility proof: MuJoCo contact is discontinuous, so local
least-squares from non-contact broad seeds is a weak method for discovering a
contact manifold.

## Conclusion

The strict setup terminal gate remains unsolved for the v54 contact-point
model. The next useful simulation step is a contact-manifold or gate-definition
audit: seed from known target-contact states, or explicitly test whether the
current x/y, force, and orientation gates are mutually compatible under the
UR10e 6DOF geometry.

## Verification

- `scripts/run_tests.sh tests/test_setup_terminal_ik.py tests/test_tcp_contact_model_audit.py` -> `6 passed`
- `scripts/run_tests.sh` -> `89 passed in 2.27s`
- `git diff --check` passed
