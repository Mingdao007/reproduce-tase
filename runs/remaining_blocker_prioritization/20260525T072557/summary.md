# Remaining Blocker Prioritization Summary

Run root: `runs/remaining_blocker_prioritization/20260525T072557`

- Overall goal complete: `False`
- Completion blocked: `True`
- Top priority blocker: `approved_read_only_calibration_evidence`
- Remaining blockers: `6`
- Live or approval blocked blockers: `4`
- Offline-actionable non-final blockers: `2`
- Profile-overlay supported cells: `2`
- Gate-acceptance blocked cells: `2`
- Closed cells: `0`
- Approval-required blockers: `approved_read_only_calibration_evidence, orientation_gate_acceptance, calibrated_contact_geometry, hardware_readiness`
- Offline-actionable non-final blockers: `strict_paper_equivalent_full_staged_feasibility, robustness_to_contact_model_perturbations`
- Non-profile-covered gate-blocked cells: `positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate`

| rank | blocker | category | status | offline | approval | completion claim |
| ---: | --- | --- | --- | --- | --- | --- |
| `0` | `approved_read_only_calibration_evidence` | `approval_blocked_prerequisite` | `approval_required_prerequisite` | `False` | `True` | `False` |
| `1` | `orientation_gate_acceptance` | `evidence_and_review_blocked` | `blocked_on_evidence_and_separate_review` | `False` | `True` | `False` |
| `2` | `calibrated_contact_geometry` | `measurement_blocked` | `blocked_on_approved_measurements` | `False` | `True` | `False` |
| `3` | `strict_paper_equivalent_full_staged_feasibility` | `offline_actionable_nonfinal` | `offline_actionable_nonfinal` | `True` | `False` | `False` |
| `4` | `robustness_to_contact_model_perturbations` | `offline_actionable_nonfinal_but_gate_contact_blocked` | `offline_actionable_but_final_claim_blocked` | `True` | `False` | `False` |
| `5` | `hardware_readiness` | `approval_and_evidence_blocked_terminal` | `blocked_on_evidence_chain` | `False` | `True` | `False` |

Interpretation:

- Approved read-only calibration evidence is the prerequisite for gate acceptance, contact calibration, and hardware readiness.
- Strict feasibility and robustness bookkeeping can still advance offline, but only as non-final evidence.
- The v111 named-profile restatement does not remove the gate-acceptance blocked rows.
