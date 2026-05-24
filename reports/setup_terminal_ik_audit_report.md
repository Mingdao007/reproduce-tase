# Setup Terminal IK Audit Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v37-terminal-ik-audit`

## Scope

This iteration tests a mathematical Stage A alternative after v36 closed the
simple align -> recenter -> settle scheduling path. Instead of simulating
another velocity phase, it asks whether a terminal UR10e joint state can be
found that directly satisfies the setup gate:

- final x/y error to the original setup point `<= 0.002 m`
- final force error `<= 0.25 N`
- final force-normal orientation error `<= 0.03 rad`
- contact present

The probe is terminal-only nonlinear least squares. It deliberately removes
path feasibility and the Stage A velocity law from the question, so it is a
configuration audit, not a controller pass.

The work is simulation-only. No real robot motion, hardware writes, TCP
writes, payload writes, URCap writes, or OnRobot setting changes were
performed.

## Artifacts

- Run root:
  `runs/setup_terminal_ik_audit/20260524T111150`
- Tracked files:
  - `metrics.yaml`
  - `metrics.json`
  - `summary.md`
  - `git_state.md`

## Common Setup

```text
initial_q = [0, -0.1, 0.15, -0.05, 0, 0]
base_z_offset_m = -0.0011631221220595766
target_force_N = 5.0
surface_normal_world = [0.1736481777010905, 0, 0.9848077530061847]
reference_xy_m = [0.00497792942394327, 0]
random_seed_count = 64
random_seed_std_rad = 0.15
random_seed = 37
max_nfev = 300
posture_weight = 0.0001
```

The command was:

```bash
scripts/run_setup_terminal_ik_probe.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --random-seed-count 64 \
  --random-seed-std-rad 0.15 \
  --random-seed 37 \
  --max-nfev 300 \
  --posture-weight 0.0001
```

## Result

- Terminal candidates: `65`
- Terminal setup passes: `0 / 65`
- Initial state:
  - force error: `3.3218849893046354e-09 N`
  - x/y error: `0.0 m`
  - orientation error: `0.17453292523412012 rad`
- Best optimized candidate:
  - seed: `initial`
  - pass: `False`
  - failed criteria: `tangential_error_m;orientation_error_rad`
  - max gate ratio: `1.733278048340598`
  - force error: `0.004835673570861232 N`
  - x/y error: `0.002178947478445584 m`
  - orientation error: `0.05199834145021794 rad`
  - contact present: `True`

## Interpretation

This terminal audit finds the same conflict without using a phase schedule.
The optimizer can keep the force target and contact while moving close to the
setup x/y gate, but the best local terminal state still misses both the
`2 mm` x/y gate and the `0.03 rad` force-normal orientation gate.

The result is stronger than another negative velocity-phase run because path
constraints were relaxed away. It is still not a global infeasibility proof:
the probe uses deterministic local least-squares seeds around the current
setup and the approximate tilted-plane MJCF with the unverified 85 mm TCP.

## Conclusion

The terminal IK audit does not provide an accepted Stage A solution. Under the
current model, gate definitions, and local seed set, the evidence now points
away from more phase scheduling and toward one of two decisions:

- explicitly relax the setup x/y/orientation budget and keep that result
  separate from paper-equivalent full staged feasibility; or
- revisit model/TCP/contact geometry and run a broader terminal feasibility
  audit before designing another Stage A controller.

## 2026-05-24 v53 Rerun After TCP/Contact Audit

The v53 TCP/contact model audit found that the configured 85 mm TCP site is
coincident with the center of the `contact_tip` sphere, while MuJoCo contact
with the plane occurs one sphere radius away from that site. The relevant
evidence is in `reports/tcp_contact_model_audit_report.md` and
`runs/tcp_contact_model_audit/20260524T135607`.

The terminal IK audit was rerun with the same command and model at:

- `runs/setup_terminal_ik_audit/20260524T135619`

The rerun reproduces the v37 result:

- terminal candidates: `65`
- terminal setup passes: `0 / 65`
- initial force error: `3.3218849893046354e-09 N`
- initial x/y error: `0.0 m`
- initial orientation error: `0.17453292523412012 rad`
- best force error: `0.004835673570861232 N`
- best x/y error: `0.002178947478445584 m`
- best orientation error: `0.05199834145021794 rad`
- best failed criteria: `tangential_error_m;orientation_error_rad`

This preserves the previous terminal-gate failure and adds a concrete model
reason to avoid treating it as hardware evidence: the current MJCF has not
resolved whether the 85 mm EOAT note denotes the physical contact point or the
center/frame of a colliding proxy sphere.

## 2026-05-24 v54 Rerun With TCP Contact-Point Variant

The v54 replacement model moves the `contact_tip` sphere center to local
`[0, 0, 0.045]` while keeping `tcp_site_unverified_85mm` at the EOAT candidate
contact point. This resolves the v53 site/center coincidence for a named
simulation convention. Evidence is in
`reports/tcp_contact_point_model_variant_report.md` and
`runs/tcp_contact_model_audit/20260524T140535`.

The terminal IK audit was rerun against:

- `configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`
- `runs/setup_terminal_ik_audit/20260524T140539`

The strict setup gate still fails:

- terminal candidates: `65`
- terminal setup passes: `0 / 65`
- initial force error: `3.2605029787191597e-12 N`
- initial x/y error: `0.0 m`
- initial orientation error: `0.17453292523412012 rad`
- best force error: `0.0050975519688662985 N`
- best x/y error: `0.0030075788240061675 m`
- best orientation error: `0.07240603253666981 rad`
- best failed criteria: `tangential_error_m;orientation_error_rad`

This closes the simple TCP/contact convention replacement step, but it does
not provide a strict Stage A solution.

## Verification

- `python3 -m py_compile src/tase_repro/setup_terminal_ik.py scripts/run_setup_terminal_ik_probe.py`
- `scripts/run_tests.sh` -> `66 passed in 1.38s`
