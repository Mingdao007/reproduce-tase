from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_posture_feasibility_sweep as sweep


def test_summary_markdown_records_failed_posture_calibration(tmp_path: Path) -> None:
    out_path = tmp_path / "summary.md"
    sweep.write_summary_markdown(
        out_path,
        run_root=tmp_path,
        rows=[],
        posture_calibrations=[
            {
                "posture": "bend_0p20",
                "calibrated_base_z_offset_m": None,
                "initial_force_N": None,
                "initial_contact_count": None,
                "calibration_pass": False,
                "calibration_error": "could not calibrate initial posture to target force",
            }
        ],
        trajectories=["e2-figure-eight"],
        thresholds=sweep.FeasibilityThresholds(
            max_orientation_error_rad_max=0.03,
            max_angular_velocity_slack_rad_s_max=0.03,
        ),
    )

    text = out_path.read_text(encoding="utf-8")
    assert "## Posture Calibration" in text
    assert "| bend_0p20 | `False` | `None` | `None` | `None` |" in text
    assert "could not calibrate initial posture to target force" in text
    assert "`max_orientation_error_rad_max`: `0.03`" in text
