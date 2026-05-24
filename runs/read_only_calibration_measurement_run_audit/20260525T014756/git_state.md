# Git State

- Branch: `exp/tase-ur10e-v92-readonly-worksheet-coverage`
- Commit: `c7f111cfd5993ca1b862d84904ca8ad4fba8f1a6`
- Dirty tree: `True`
- Status:

```text
M scripts/audit_read_only_calibration_measurement_run.py
 M scripts/finalize_read_only_calibration_measurement_evidence.py
 M templates/read_only_calibration_measurement/README.md
 M templates/read_only_calibration_measurement/measurement_plan.md
 M templates/read_only_calibration_measurement/operator_checklist.md
 M tests/test_read_only_calibration_measurement_template.py
?? runs/read_only_calibration_measurement/20260525T014755/
?? runs/read_only_calibration_measurement_run_audit/20260525T014756/
?? templates/read_only_calibration_measurement/ksm_contact_patch_convention.csv
?? templates/read_only_calibration_measurement/orientation_gate_semantics.csv
```

- Command:

```bash
/usr/bin/python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T014755 --audit-mode scaffold --run-id 20260525T014756
```
