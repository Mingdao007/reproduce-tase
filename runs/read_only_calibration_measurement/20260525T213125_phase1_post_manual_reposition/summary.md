# Read-Only Calibration Measurement Summary

Run id: `20260525T213125_phase1_post_manual_reposition`
Run root: `/home/andy/reproduce-tase/runs/read_only_calibration_measurement/20260525T213125_phase1_post_manual_reposition`

Status: `scaffold_created_not_executed`

This run folder was scaffolded from
`templates/read_only_calibration_measurement`.

No live hardware access, robot motion, configuration write, zeroing, or
force-control action was performed by the scaffold command.

All recovery, calibration, gate-relaxation, paper-equivalent, robustness,
and hardware-readiness claims remain false until concrete measurements
are collected and audited.

## Indexed Auxiliary Evidence

- `photos_manifest.md` now indexes the 2026-05-26 caliper and KSM-8N source
  photos by Mac original path and SHA256.
- `ksm8n_factory_cad_evidence.md` records the KSM-8N drawing/photo evidence,
  the v13 EOAT CAD cross-check, and the boundary that these artifacts can only
  support the mounted measurement. They do not replace physical
  `tcp_contact_measurements.csv` rows.
- `mounted_stack_visual_assumption_audit.md` records the 2026-05-26 mounted
  visual audit. The photos support `85.0 mm` as a stronger working candidate,
  but still do not finalize mounted-stack calibration.
- `provisional_85mm_contact_experiment_gate.md` records the decision not to
  block all later contact-force work on unavailable metrology equipment. It
  allows `85.0 mm` as a provisional low-risk contact experiment preparation
  candidate while keeping calibration and hardware-readiness claims false.
- `pre_contact_readiness_ladder.md` defines the small pre-contact experiments:
  static no-motion checks, read-only UR state checks, no-contact force baseline,
  and a separate explicit SOP boundary before any real contact.
- `n1_n2_readiness_report_20260526T181617HKT.md` records the first N1/N2 run:
  UR network/interfaces/Dashboard/payload-TCP readbacks passed machine-side
  checks, and a 30 s no-contact `actual_TCP_force` baseline was captured.
- `rtde_frequency_check_after_power_cycle_20260526T182347HKT.md` records the
  post-power-cycle RTDE frequency check. A `1000 Hz` request returned about
  `500 Hz` for UR RTDE `actual_TCP_force`; this is not a `1 kHz` readback.
