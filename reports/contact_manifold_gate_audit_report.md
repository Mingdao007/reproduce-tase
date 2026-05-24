# Contact-Manifold Gate Audit Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v56-contact-manifold-gate-audit`

## Scope

This iteration tests the strict setup gate on the v54 TCP contact-point model
from known target-contact neighborhoods. It asks which gate combination is
blocking the terminal setup:

- x/y position at the original setup point
- target force from the intended `contact_plane` / `contact_tip` pair
- force-normal TCP orientation

The work is simulation-only. No real UR10e motion, TCP writes, payload writes,
URCap writes, ROS config writes, or OnRobot configuration changes were
performed.

## Method

Added:

- `src/tase_repro/contact_manifold_gate_audit.py`
- `scripts/audit_contact_manifold_setup_gate.py`
- `tests/test_contact_manifold_gate_audit.py`

The audit seeds from the known 5 N target-contact initial state and local
perturbations around it, then solves four terminal gate combinations:

- `xy_force`
- `xy_orientation`
- `force_orientation`
- `xy_force_orientation`

Every final candidate is evaluated against the full strict gate using the
target contact pair only.

## Run

Run:

- `runs/contact_manifold_gate_audit/20260524T142404`

Command:

```bash
scripts/audit_contact_manifold_setup_gate.py \
  --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml \
  --random-seed-count-per-std 40 \
  --random-seed-stds-rad 0.03,0.1,0.3,0.8 \
  --random-seed 761 \
  --max-nfev 800
```

## Result

- seed count: `161`
- strict pass count: `0`
- target signed surface distance: `-1.7843686194222996e-05 m`

### Gate Matrix

| Case | Pass Count | Main Residual |
|---|---:|---|
| `xy_force` | `0 / 161` | orientation error `0.14697007178233126 rad` |
| `xy_orientation` | `0 / 161` | target force error `5.0 N`; no target contact |
| `force_orientation` | `0 / 161` | optimized force/orientation solution has x/y error `0.014127706733724453 m` |
| `xy_force_orientation` | `0 / 161` | best still has x/y error `0.0030075787462736734 m` and orientation error `0.07240603326354965 rad` |

The strict best candidate:

- force error: `0.005097551486581864 N`
- x/y error: `0.0030075787462736734 m`
- orientation error: `0.07240603326354965 rad`
- failed criteria: `tangential_error_m;orientation_error_rad`

## Interpretation

The gate combinations are mutually in tension in the current 6DOF UR10e
adapted setup:

- The model can satisfy x/y and force, but not orientation.
- The model can satisfy x/y and orientation, but it leaves the target contact
  manifold and loses force.
- The model can satisfy force and orientation, but only with centimeter-scale
  x/y drift.

This is stronger than the v55 broad random audit because the seeds start from
known target-contact neighborhoods instead of asking non-contact seeds to
discover contact. It is still not a formal global infeasibility proof.

## Conclusion

The strict setup gate remains unsolved. Under the current v54 TCP contact-point
model and v56 target-contact gate accounting, the next engineering decision is
not another scalar phase schedule. The project should either:

- explicitly relax or redefine the adapted UR10e setup gate; or
- change the setup target definition so x/y, force, and force-normal
  orientation are physically compatible for the 6DOF UR10e model.

## Verification

- `scripts/run_tests.sh tests/test_contact_manifold_gate_audit.py` -> `1 passed`
- `scripts/run_tests.sh` -> `90 passed in 2.44s`
- `git diff --check` passed
