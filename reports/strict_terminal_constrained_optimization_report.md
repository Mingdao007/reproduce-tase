# Strict Terminal Constrained Optimization Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v116-strict-terminal-constrained-optimization`

Implementation commit: `IMPLEMENTATION_COMMIT_PENDING`

## Objective

Probe the v116 offline strict-feasibility step after v115: test a stronger
constrained terminal optimization over the accepted contact-point model, rather
than another Stage A controller schedule or qdot-timed path matrix.

The audit seeds from the v56 contact-manifold terminal candidates and runs
bounded smooth-minimax optimizers over normalized strict force, x/y, and
orientation errors with a no-contact penalty. It does not run a Stage A
controller, Stage B trajectory, hardware read, hardware write, or force-control
step.

## Artifacts

- New audit script:
  `scripts/audit_strict_terminal_constrained_optimization.py`
- New run:
  `runs/strict_terminal_constrained_optimization/20260525T085000`
- New test:
  `tests/test_strict_terminal_constrained_optimization.py`

## Result

The v116 audit reports:

```text
optimization_case_count = 12
strict_terminal_pass_count = 0 / 12
optimizer_success_count = 10 / 12
best_case_id = xy_force_orientation__best_candidate__slsqp
best_max_gate_ratio = 2.11994927622362
v56_strict_best_max_gate_ratio = 2.413534442118322
best_ratio_improvement = 0.29358516589470174
strict_terminal_constrained_optimization_complete = false
strict_paper_equivalent_feasibility = false
do_not_mark_goal_complete = true
```

The best optimized row remains target-contacting, but still fails all three
strict terminal scalar gates:

```text
force_error_N = 0.26697482058387756  (ratio 1.0678992823355102)
tangential_error_m = 0.003940556880295705  (ratio 1.9702784401478524)
orientation_error_rad = 0.0635984782867086  (ratio 2.11994927622362)
target_contact_count = 1
```

Failure counts across all optimization rows:

```text
force_error_N = 10
orientation_error_rad = 10
tangential_error_m = 9
target_contact_count = 3
```

Interpretation:

- The stronger smooth-minimax optimizer improves the v56 best strict terminal
  max-gate ratio from `2.413534442118322` to `2.11994927622362`.
- The improvement is not enough for a strict terminal pass.
- The best compromise remains outside force, x/y, and orientation thresholds.
- This supports the v115 conclusion that strict terminal compatibility remains
  blocked under the current accepted contact-point model and gate.

## Claim Boundary

V116 is offline simulation only. It does not prove strict paper-equivalent
feasibility, run a Stage A controller, run a Stage B trajectory, make a
canonical controller change, accept a replacement orientation gate, close
failed cells, prove robustness, calibrate contact geometry, establish hardware
readiness, or authorize hardware motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_strict_terminal_constrained_optimization.py`
  passed.
- `scripts/run_tests.sh tests/test_strict_terminal_constrained_optimization.py`
  passed with `4 passed in 0.12s`.
- `python3 scripts/audit_strict_terminal_constrained_optimization.py --output-dir runs/strict_terminal_constrained_optimization/20260525T085000`
  created the v116 run.
- `rg -n "&id|\*id" runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/strict_terminal_constrained_optimization/20260525T085000 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `178 passed in 7.16s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `BRANCH_PUSH_PENDING`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
V116 already tested a stronger bounded smooth-minimax terminal optimization
over the accepted contact model, so the next strict-feasibility work should not
repeat the same seed and objective family. The practical next blocker remains
approved read-only calibration evidence or a new, explicitly accepted
contact/setup-target definition.
