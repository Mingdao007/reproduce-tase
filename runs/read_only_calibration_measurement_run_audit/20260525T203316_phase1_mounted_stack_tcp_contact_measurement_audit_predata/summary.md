# Read-Only Calibration Measurement Run Audit

Run root: `/home/andy/reproduce-tase/runs/read_only_calibration_measurement_run_audit/20260525T203316_phase1_mounted_stack_tcp_contact_measurement_audit_predata`
Audited run: `/home/andy/reproduce-tase/runs/read_only_calibration_measurement/20260525T203316_phase1_mounted_stack_tcp_contact_measurement`

- Audit mode: `approved-read-only`
- Audit passed: `False`
- Run status: `scaffold_created_not_executed`
- File count: `14`
- Heavy payloads: `[]`

## Claim Boundary

- Live hardware accessed: `False`
- User confirmed read-only step: `False`
- Robot motion commanded: `False`
- Configuration written: `False`
- Force control run: `False`
- Supports gate relaxation: `False`
- Orientation gate decision: `not_accepted`
- Orientation evidence only: `True`
- Supports hardware claim: `False`
- Hardware readiness: `False`

## Violations

- metrics status is not approved_read_only_evidence
- approved read-only mode requires execution.user_confirmed_read_only_step true
- approved read-only mode requires at least one evidence_status field to change
- read_only_evidence_finalization is required in approved-read-only mode
