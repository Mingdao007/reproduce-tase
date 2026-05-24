# Plus1mm Unresolved Diagnostic Probe Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v104-plus1mm-unresolved-probe`

## Objective

Classify the remaining `+1.0 mm` blocker signatures after all four v99
planned failed-cell commands were executed and audited. This is a narrow
offline probe over existing v100-v103 metrics; it does not rerun MuJoCo,
change controller defaults, accept a replacement gate, or close any failed
cell.

## Artifacts

- New audit script:
  `scripts/audit_plus1mm_unresolved_diagnostic_probe.py`
- New run:
  `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237`
- New tests:
  `tests/test_plus1mm_unresolved_diagnostic_probe.py`

## Result

The v104 probe reads the v103 execution audit and the four executed
failed-cell experiment metrics. It confirms:

```text
planned_failed_cell_count = 4
executed_cell_count = 4
closed_cell_count = 0
not_executed_cell_count = 0
unresolved_cell_count = 4
probe_closes_failed_cells = false
```

Remaining `+1.0 mm` signatures:

| cell | diagnostic class | key margin | qdot saturation |
| --- | --- | ---: | ---: |
| `base_z_plus1mm` | `start_terminal_path_unrecovered` | terminal orientation exceeds `0.119 rad` by `0.0004856078654814633 rad` | `n/a` |
| `positive_fast_timing_0p0075` | `fast_timing_e2_qdot_and_orientation` | E2 Stage B orientation exceeds its `0.12 rad` gate by `0.0002030587287190494 rad` | `0.999` |
| `positive_orientation_gate_0p119` | `unweighted_orientation_margin` | Stage B orientation exceeds `0.119 rad` by `0.0009788204275829049 rad` | `0.006` |
| `weighted_plus1mm_0p119_gate` | `weighted_orientation_margin_without_qdot_saturation` | Stage B orientation exceeds `0.119 rad` by `0.0005664520369604714 rad` | `0.0` |

The only remaining `+1.0 mm` failed cell with a qdot-saturation blocker is
`positive_fast_timing_0p0075`. The orientation-gate rows remain blocked by the
current `0.119 rad` gate and by the lack of calibrated geometry or accepted
gate evidence.

## Claim Boundary

V104 is post-hoc offline bookkeeping over existing metrics. It does not
collect live measurements, execute the read-only SOP, move the UR10e, write
configuration, zero/bias/filter the force sensor, run force control, reconcile
force-source frames, accept a replacement orientation gate, calibrate the
contact model, prove robustness, prove strict paper-equivalent feasibility, or
make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_plus1mm_unresolved_diagnostic_probe.py`
  passed.
- `scripts/run_tests.sh tests/test_plus1mm_unresolved_diagnostic_probe.py`
  passed with `2 passed in 0.22s`.
- `python3 scripts/audit_plus1mm_unresolved_diagnostic_probe.py` created
  `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237`.
- `rg -n "&id|\*id" runs/plus1mm_unresolved_diagnostic_probe/20260525T062237/metrics.yaml`
  found no YAML anchors.
- `scripts/run_tests.sh` passed with `146 passed in 6.74s`.
- `git diff --check` passed after validation.
- Branch push was verified at
  `b412ddf5bbec20682ce021b754aa0efc845a3372`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next narrow offline work should either separate the `base_z_plus1mm`
start-contact miss from its terminal-orientation miss, or isolate the
`positive_fast_timing_0p0075` E2 qdot/usage blocker. Do not accept diagnostic
orientation gates from simulation metrics alone.
