# Contact Force Ladder Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v3-contact-force-ladder`

Run:

`runs/contact_force_ladder/20260524T012524`

Command:

```bash
python3 scripts/run_contact_force_ladder.py --config configs/mujoco_ur10e.yaml --steps 500 --tail-steps 100 --tolerance-N 0.01
```

## Scope

This is a MuJoCo contact-model probe for the v1 approximate UR10e model. It
calibrates static contact force by applying tiny `base_link` z offsets and
measuring the positive MuJoCo contact-frame normal wrench.

It is not closed-loop force control, not a real robot command, and not
hardware-ready.

## Results

| target force N | base z offset mm | measured force N | error N | contact count |
| ---: | ---: | ---: | ---: | ---: |
| 0.5 | 0.136719 | 0.506434 | 0.006434 | 1.0 |
| 1.0 | 0.124023 | 0.991129 | -0.008871 | 1.0 |
| 2.0 | 0.097656 | 2.002217 | 0.002217 | 1.0 |
| 5.0 | 0.021484 | 5.000019 | 0.000019 | 1.0 |

Maximum absolute force error: `0.0088706346160502 N`.

## Interpretation

The MuJoCo contact-force sign convention used by this repository is:

`positive MuJoCo contact-frame normal wrench[0]`

The current model's contact stiffness is steep. Small z offsets around
`0.02 mm` to `0.14 mm` span the 5 N to 0.5 N range. This is useful for
simulation sign and target-force sanity checks, but it does not validate the
real OnRobot or UR RTDE force source.

## Limitations

- The MJCF is approximate and not calibrated.
- The 85 mm TCP is still an unverified CAD guess.
- The offsets are direct model edits, not robot motion or controller output.
- No tangential trajectory tracking is included.
- No orientation compliance is included.

## Next Step

Build a stationary contact controller simulation that uses measured contact
normal force feedback and the bounded velocity solve, while logging solver
status, active bounds, force error, and hard stop conditions.

