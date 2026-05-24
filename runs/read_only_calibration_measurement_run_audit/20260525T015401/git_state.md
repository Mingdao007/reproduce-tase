# Git State

- Branch: `exp/tase-ur10e-v93-orientation-acceptance-boundary`
- Commit: `24cfc1977941e4ef527a34cbb451bf9c50f8ade4`
- Dirty tree: `True`
- Status:

```text
M scripts/audit_read_only_calibration_measurement_run.py
 M scripts/finalize_read_only_calibration_measurement_evidence.py
 M templates/read_only_calibration_measurement/metrics.yaml
 M templates/read_only_calibration_measurement/orientation_gate_decision.md
 M tests/test_read_only_calibration_measurement_template.py
?? runs/read_only_calibration_measurement/20260525T015400/
?? runs/read_only_calibration_measurement_run_audit/20260525T015401/
```

- Command:

```bash
/usr/bin/python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T015400 --audit-mode scaffold --run-id 20260525T015401
```
