from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import yaml

from scripts.audit_robustness_dependency_frontier_after_v141 import build_payload


ROOT = pathlib.Path(__file__).resolve().parents[1]
POST_V141_GATE = ROOT / "runs" / "post_v140_completion_gate" / "20260525T150000" / "metrics.yaml"
MATRIX_RESTATEMENT = (
    ROOT / "runs" / "weighted_profile_matrix_restatement" / "20260525T075040" / "metrics.yaml"
)


def build_current_payload(**overrides):
    kwargs = {
        "post_v141_gate_path": POST_V141_GATE,
        "matrix_restatement_path": MATRIX_RESTATEMENT,
        "run_id": "TEST",
    }
    kwargs.update(overrides)
    return build_payload(**kwargs)


def test_robustness_frontier_classifies_failed_cells_without_closure() -> None:
    payload = build_current_payload()
    summary = payload["summary"]

    assert summary["audit_passed"] is True
    assert summary["overall_goal_complete"] is False
    assert summary["completion_claim_allowed"] is False
    assert summary["robustness_complete"] is False
    assert summary["accepted_as_robustness_proof"] is False
    assert summary["candidate_matrix_complete"] is False
    assert summary["all_failed_cells_closed"] is False
    assert summary["closed_cell_count"] == 0
    assert summary["source_failed_cell_count"] == 4
    assert summary["frontier_row_count"] == 4
    assert summary["profile_overlay_supported_noncanonical_count"] == 2
    assert summary["profile_overlay_supported_noncanonical_cell_ids"] == [
        "base_z_plus1mm",
        "positive_fast_timing_0p0075",
    ]
    assert summary["gate_or_contact_acceptance_blocked_count"] == 2
    assert summary["gate_or_contact_acceptance_blocked_cell_ids"] == [
        "positive_orientation_gate_0p119",
        "weighted_plus1mm_0p119_gate",
    ]
    assert summary["new_simulation_selected"] is False
    assert summary["additional_failed_cell_execution_recommended"] is False
    assert summary["requires_approved_read_only_evidence_for_closure"] is True
    assert summary["requires_contact_setup_target_acceptance_for_closure"] is True
    assert summary["requires_orientation_gate_acceptance_for_gate_rows"] is True
    assert summary["source_approved_read_only_run_count"] == 0
    assert summary["source_approved_read_only_audit_passed_count"] == 0
    assert summary["source_accepted_orientation_review_count"] == 0
    assert summary["source_accepted_contact_setup_target_review_count"] == 0
    assert summary["do_not_mark_goal_complete"] is True
    assert payload["claim_boundary"]["new_simulation_run"] is False
    assert payload["claim_boundary"]["robustness_proof"] is False

    rows = {row["cell_id"]: row for row in payload["frontier_rows"]}
    assert rows["base_z_plus1mm"]["frontier_class"] == "profile_overlay_supported_noncanonical"
    assert rows["positive_fast_timing_0p0075"]["frontier_class"] == (
        "profile_overlay_supported_noncanonical"
    )
    assert rows["positive_orientation_gate_0p119"]["frontier_class"] == (
        "gate_or_contact_acceptance_blocked"
    )
    assert rows["weighted_plus1mm_0p119_gate"]["frontier_class"] == (
        "gate_or_contact_acceptance_blocked"
    )
    assert all(row["failed_cell_closed"] is False for row in rows.values())


def test_robustness_frontier_rejects_robustness_claim_drift(tmp_path) -> None:
    restatement = yaml.safe_load(MATRIX_RESTATEMENT.read_text(encoding="utf-8"))
    restatement["summary"]["accepted_as_robustness_proof"] = True
    restatement["summary"]["closed_cell_count"] = 4
    restatement["failed_cell_restatement_rows"][0]["failed_cell_closed"] = True
    drifted = tmp_path / "restatement.yaml"
    drifted.write_text(yaml.safe_dump(restatement, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(matrix_restatement_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert (
        "weighted_profile_matrix_restatement.summary.accepted_as_robustness_proof is True, expected False"
        in payload["summary"]["violations"]
    )
    assert "base_z_plus1mm unexpectedly closed" in payload["summary"]["violations"]


def test_robustness_frontier_rejects_completion_gate_drift(tmp_path) -> None:
    gate = yaml.safe_load(POST_V141_GATE.read_text(encoding="utf-8"))
    gate["summary"]["approved_read_only_run_count"] = 1
    gate["summary"]["accepted_orientation_review_count"] = 1
    drifted = tmp_path / "post_v141.yaml"
    drifted.write_text(yaml.safe_dump(gate, sort_keys=False), encoding="utf-8")

    payload = build_current_payload(post_v141_gate_path=drifted)

    assert payload["summary"]["audit_passed"] is False
    assert (
        "post_v141_completion_gate.summary.approved_read_only_run_count is 1, expected 0"
        in payload["summary"]["violations"]
    )
    assert (
        "post_v141_completion_gate.summary.accepted_orientation_review_count is 1, expected 0"
        in payload["summary"]["violations"]
    )


def test_robustness_frontier_cli_writes_no_alias_metrics(tmp_path) -> None:
    out_dir = tmp_path / "robustness_dependency_frontier"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/audit_robustness_dependency_frontier_after_v141.py",
            "--output-dir",
            str(out_dir),
            "--run-id",
            "TEST_FRONTIER",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert completed.stdout.strip() == str(out_dir)
    metrics_yaml_text = (out_dir / "metrics.yaml").read_text(encoding="utf-8")
    metrics = yaml.safe_load(metrics_yaml_text)
    metrics_json = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics_json == metrics
    assert "&id" not in metrics_yaml_text
    assert "*id" not in metrics_yaml_text
    assert metrics["summary"]["audit_passed"] is True
    assert metrics["summary"]["robustness_complete"] is False
    assert metrics["summary"]["new_simulation_selected"] is False
    assert metrics["summary"]["additional_failed_cell_execution_recommended"] is False
    assert metrics["claim_boundary"]["robustness_proof"] is False
    assert (out_dir / "summary.md").exists()
    assert (out_dir / "git_state.md").exists()
