# Relaxed Setup Budget Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v38-relaxed-setup-budget`

## Scope

This iteration defines an explicit UR10e adapted setup budget after v35-v37
showed that the strict setup terminal-state gate is not met in the current
approximate tilted-plane model.

This does not change the paper-equivalent full staged gate. It adds a separate
label for simulation evidence where:

- setup force/contact and final force-normal orientation pass,
- setup x/y drift is bounded but relaxed to `<= 0.010 m`,
- setup qdot saturation is recorded but not used as a pass/fail criterion, and
- the following trajectory still passes the strict Stage B feasibility gate.

The work is simulation-only. No real robot motion, hardware writes, TCP
writes, payload writes, URCap writes, or OnRobot setting changes were
performed.

## Artifacts

- Acceptance config:
  `configs/ur10e_adapted_acceptance.yaml`
- Evaluation run:
  `runs/relaxed_setup_budget_eval/20260524T111859`
- Source evidence run:
  `runs/staged_orientation_e1e4_posture_regularized/20260524T102747`

## Budget

The accepted UR10e adapted relaxed setup budget is:

```text
max_setup_tangential_drift_m = 0.010
max_final_orientation_error_rad = 0.03
max_tail_mean_abs_force_error_N = 0.25
contact_present_fraction_min = 1.0
max_qdot_violation_rad_s = 1e-9
max_joint_limit_violation_rad = 1e-9
qdot_saturation_policy = record_only
```

Strict paper-equivalent full staged feasibility remains unchanged and still
requires the prior strict setup and trajectory gates.

## Command

```bash
scripts/evaluate_relaxed_setup_budget.py \
  --run-root runs/staged_orientation_e1e4_posture_regularized/20260524T102747 \
  --acceptance-config configs/ur10e_adapted_acceptance.yaml
```

## Result

- Cases: `4`
- Relaxed setup passes: `4 / 4`
- Trajectory feasibility passes: `4 / 4`
- UR10e adapted trajectory-after-relaxed-setup passes: `4 / 4`
- Strict full staged feasibility passes: `0 / 4`

| trajectory | relaxed setup | trajectory | adapted label | setup drift m | setup qdot sat |
|---|---:|---:|---:|---:|---:|
| `e1-cycloid` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |
| `e2-figure-eight` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |
| `e3-circle` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |
| `e4-cardioid` | `True` | `True` | `True` | `0.008347977658392892` | `1.0` |

## Interpretation

The v33 slowed tilted-plane E1-E4 matrix can now be described as a UR10e
adapted trajectory-after-relaxed-setup result. It must not be described as a
paper-equivalent full staged reproduction because strict setup feasibility
remains `0 / 4`.

The relaxed label is intentionally narrow. It accepts the weighted
prealignment setup drift and saturated setup maneuver as a simulation setup
move, while keeping Stage B trajectory feasibility strict and preserving the
negative strict-gate evidence from v35-v37.

## Verification

- `python3 -m py_compile src/tase_repro/relaxed_setup_budget.py scripts/evaluate_relaxed_setup_budget.py`
- `scripts/run_tests.sh` -> `68 passed in 1.38s`
