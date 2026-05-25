# Robustness Dependency Frontier After V141

Run root: `/home/andy/reproduce-tase/runs/robustness_dependency_frontier_after_v141/20260525T160000`

- Audit passed: `True`
- Robustness complete: `False`
- Accepted as robustness proof: `False`
- Closed cell count: `0`
- Frontier rows: `4`
- Profile-overlay noncanonical rows: `['base_z_plus1mm', 'positive_fast_timing_0p0075']`
- Gate/contact blocked rows: `['positive_orientation_gate_0p119', 'weighted_plus1mm_0p119_gate']`
- New simulation selected: `False`
- Additional failed-cell execution recommended: `False`
- Do not mark goal complete: `True`

## Frontier Rows

- `base_z_plus1mm`: `profile_overlay_supported_noncanonical`
  - restated status: `failed_with_noncanonical_profile_overlay`
  - blocking dependencies: `canonical_controller_or_profile_acceptance, contact_setup_target_acceptance, approved_read_only_calibration_evidence`
- `positive_fast_timing_0p0075`: `profile_overlay_supported_noncanonical`
  - restated status: `failed_with_noncanonical_profile_overlay`
  - blocking dependencies: `canonical_controller_or_profile_acceptance, contact_setup_target_acceptance, approved_read_only_calibration_evidence`
- `positive_orientation_gate_0p119`: `gate_or_contact_acceptance_blocked`
  - restated status: `failed_without_profile_overlay`
  - blocking dependencies: `orientation_gate_acceptance, contact_setup_target_acceptance, approved_read_only_calibration_evidence`
- `weighted_plus1mm_0p119_gate`: `gate_or_contact_acceptance_blocked`
  - restated status: `failed_without_profile_overlay`
  - blocking dependencies: `orientation_gate_acceptance, contact_setup_target_acceptance, approved_read_only_calibration_evidence`

## Claim Boundary

This audit is offline bookkeeping only. It does not run simulations,
close failed robustness cells, accept a controller or gate, collect
live evidence, prove robustness, or establish hardware readiness.
