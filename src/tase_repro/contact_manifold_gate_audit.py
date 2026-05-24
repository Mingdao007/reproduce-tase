from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import mujoco
import numpy as np
from scipy.optimize import least_squares

from tase_repro.contact import unit_vector
from tase_repro.contact_ladder import positive_contact_normal_force_between
from tase_repro.force_feedback import apply_base_z_offset
from tase_repro.kinematics import (
    joint_ranges,
    load_model,
    make_data,
    orientation_error_rotvec,
    set_qpos,
    site_position,
    site_rotation_matrix,
)
from tase_repro.orientation import rotation_aligning_local_z_to_normal
from tase_repro.setup_terminal_ik import SetupTerminalThresholds


@dataclass(frozen=True)
class GateAuditCandidate:
    seed_label: str
    q: np.ndarray
    cost: float
    nfev: int
    success: bool
    status: int
    optimized_terms: tuple[str, ...]
    tcp_m: np.ndarray
    reference_xy_m: np.ndarray
    tangential_error_m: float
    orientation_error_rad: float
    force_N: float
    force_error_N: float
    target_contact_count: int
    signed_surface_distance_m: float
    signed_surface_distance_error_m: float
    passed: bool
    failed_criteria: list[str]
    max_gate_ratio: float

    def to_dict(self) -> dict:
        return {
            "seed_label": self.seed_label,
            "q": [float(x) for x in self.q],
            "cost": float(self.cost),
            "nfev": int(self.nfev),
            "success": bool(self.success),
            "status": int(self.status),
            "optimized_terms": list(self.optimized_terms),
            "tcp_m": [float(x) for x in self.tcp_m],
            "reference_xy_m": [float(x) for x in self.reference_xy_m],
            "tangential_error_m": float(self.tangential_error_m),
            "orientation_error_rad": float(self.orientation_error_rad),
            "force_N": float(self.force_N),
            "force_error_N": float(self.force_error_N),
            "target_contact_count": int(self.target_contact_count),
            "signed_surface_distance_m": float(self.signed_surface_distance_m),
            "signed_surface_distance_error_m": float(self.signed_surface_distance_error_m),
            "passed": bool(self.passed),
            "failed_criteria": list(self.failed_criteria),
            "max_gate_ratio": float(self.max_gate_ratio),
        }


@dataclass(frozen=True)
class GateAuditCase:
    name: str
    optimized_terms: tuple[str, ...]
    candidate_count: int
    pass_count: int
    best_candidate: GateAuditCandidate
    best_optimized_candidate: GateAuditCandidate

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "optimized_terms": list(self.optimized_terms),
            "candidate_count": int(self.candidate_count),
            "pass_count": int(self.pass_count),
            "best_candidate": self.best_candidate.to_dict(),
            "best_optimized_candidate": self.best_optimized_candidate.to_dict(),
        }


@dataclass(frozen=True)
class ContactManifoldGateAuditResult:
    model_path: str
    initial_q: np.ndarray
    base_z_offset_m: float
    target_force_N: float
    site_name: str
    contact_geom_name: str
    plane_geom_name: str
    reference_xy_m: np.ndarray
    surface_normal_world: np.ndarray
    target_signed_surface_distance_m: float
    thresholds: SetupTerminalThresholds
    seed_labels: list[str]
    cases: list[GateAuditCase]

    @property
    def strict_case(self) -> GateAuditCase:
        for case in self.cases:
            if case.name == "xy_force_orientation":
                return case
        raise ValueError("strict case not found")

    def to_dict(self) -> dict:
        return {
            "model_path": self.model_path,
            "initial_q": [float(x) for x in self.initial_q],
            "base_z_offset_m": float(self.base_z_offset_m),
            "target_force_N": float(self.target_force_N),
            "site_name": self.site_name,
            "contact_geom_name": self.contact_geom_name,
            "plane_geom_name": self.plane_geom_name,
            "reference_xy_m": [float(x) for x in self.reference_xy_m],
            "surface_normal_world": [float(x) for x in self.surface_normal_world],
            "target_signed_surface_distance_m": float(self.target_signed_surface_distance_m),
            "thresholds": self.thresholds.to_dict(),
            "seed_count": len(self.seed_labels),
            "seed_labels": list(self.seed_labels),
            "cases": [case.to_dict() for case in self.cases],
            "strict_case_pass_count": self.strict_case.pass_count,
            "strict_case_best": self.strict_case.best_candidate.to_dict(),
        }


def _named_id(model: mujoco.MjModel, obj_type: mujoco.mjtObj, name: str) -> int:
    obj_id = mujoco.mj_name2id(model, obj_type, name)
    if obj_id < 0:
        raise ValueError(f"{obj_type.name} not found: {name}")
    return obj_id


def _surface_distance(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    *,
    contact_geom_id: int,
    surface_normal_world: np.ndarray,
) -> float:
    radius = float(model.geom_size[contact_geom_id, 0])
    return float(np.dot(data.geom_xpos[contact_geom_id], surface_normal_world) - radius)


def _make_seeds(
    q0: np.ndarray,
    q_min: np.ndarray,
    q_max: np.ndarray,
    *,
    random_seed: int,
    random_seed_stds_rad: Iterable[float],
    random_seed_count_per_std: int,
) -> list[tuple[str, np.ndarray]]:
    seeds: list[tuple[str, np.ndarray]] = [("initial", q0.copy())]
    rng = np.random.default_rng(int(random_seed))
    for std in random_seed_stds_rad:
        std_float = float(std)
        if std_float < 0.0:
            raise ValueError("random seed std values must be nonnegative")
        for idx in range(int(random_seed_count_per_std)):
            q = np.clip(q0 + rng.normal(0.0, std_float, size=q0.shape), q_min, q_max)
            seeds.append((f"random_std_{std_float:g}_{idx:03d}", q))
    return seeds


def run_contact_manifold_gate_audit(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    base_z_offset_m: float,
    target_force_N: float,
    thresholds: SetupTerminalThresholds,
    surface_normal_world: np.ndarray,
    site_name: str = "tcp_site_unverified_85mm",
    contact_geom_name: str = "contact_tip",
    plane_geom_name: str = "contact_plane",
    random_seed: int = 761,
    random_seed_stds_rad: Iterable[float] = (0.03, 0.1, 0.3, 0.8),
    random_seed_count_per_std: int = 32,
    max_nfev: int = 800,
) -> ContactManifoldGateAuditResult:
    """Run gate-combination audits from known target-contact neighborhoods."""
    if random_seed_count_per_std < 0:
        raise ValueError("random_seed_count_per_std must be nonnegative")
    if max_nfev <= 0:
        raise ValueError("max_nfev must be positive")
    model_path = Path(model_path)
    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset_m)
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    q0 = np.asarray(initial_q, dtype=float)
    if q0.shape != (model.nq,):
        raise ValueError(f"initial_q shape {q0.shape} does not match model.nq={model.nq}")

    normal = unit_vector(np.asarray(surface_normal_world, dtype=float))
    contact_geom_id = _named_id(model, mujoco.mjtObj.mjOBJ_GEOM, contact_geom_name)
    _named_id(model, mujoco.mjtObj.mjOBJ_GEOM, plane_geom_name)
    _named_id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)

    set_qpos(model, data, q0)
    reference_xy = site_position(model, data, site_name)[:2].copy()
    desired_rotation = rotation_aligning_local_z_to_normal(
        normal,
        reference_rotation=site_rotation_matrix(model, data, site_name),
    )
    target_signed_surface_distance = _surface_distance(
        model,
        data,
        contact_geom_id=contact_geom_id,
        surface_normal_world=normal,
    )
    seeds = _make_seeds(
        q0,
        q_min,
        q_max,
        random_seed=random_seed,
        random_seed_stds_rad=random_seed_stds_rad,
        random_seed_count_per_std=random_seed_count_per_std,
    )

    def evaluate(
        q: np.ndarray,
        *,
        seed_label: str,
        optimized_terms: tuple[str, ...],
        cost: float,
        nfev: int,
        success: bool,
        status: int,
    ) -> GateAuditCandidate:
        set_qpos(model, data, q)
        tcp = site_position(model, data, site_name)
        rotation = site_rotation_matrix(model, data, site_name)
        orientation_error = float(np.linalg.norm(orientation_error_rotvec(desired_rotation, rotation)))
        tangential_error = float(np.linalg.norm(tcp[:2] - reference_xy))
        force, contact_count = positive_contact_normal_force_between(
            model,
            data,
            geom_a_name=plane_geom_name,
            geom_b_name=contact_geom_name,
        )
        force_error = abs(float(force) - float(target_force_N))
        signed_distance = _surface_distance(
            model,
            data,
            contact_geom_id=contact_geom_id,
            surface_normal_world=normal,
        )
        signed_error = abs(float(signed_distance) - target_signed_surface_distance)
        failed = []
        if force_error > thresholds.max_force_error_N:
            failed.append("force_error_N")
        if tangential_error > thresholds.max_tangential_error_m:
            failed.append("tangential_error_m")
        if orientation_error > thresholds.max_orientation_error_rad:
            failed.append("orientation_error_rad")
        if contact_count <= 0:
            failed.append("contact_present")
        ratios = [
            force_error / thresholds.max_force_error_N,
            tangential_error / thresholds.max_tangential_error_m,
            orientation_error / thresholds.max_orientation_error_rad,
            0.0 if contact_count > 0 else float("inf"),
        ]
        return GateAuditCandidate(
            seed_label=seed_label,
            q=np.asarray(q, dtype=float).copy(),
            cost=float(cost),
            nfev=int(nfev),
            success=bool(success),
            status=int(status),
            optimized_terms=tuple(optimized_terms),
            tcp_m=tcp.copy(),
            reference_xy_m=reference_xy.copy(),
            tangential_error_m=tangential_error,
            orientation_error_rad=orientation_error,
            force_N=float(force),
            force_error_N=float(force_error),
            target_contact_count=int(contact_count),
            signed_surface_distance_m=float(signed_distance),
            signed_surface_distance_error_m=float(signed_error),
            passed=not failed,
            failed_criteria=failed,
            max_gate_ratio=float(np.max(ratios)),
        )

    def residual(q: np.ndarray, optimized_terms: tuple[str, ...]) -> np.ndarray:
        set_qpos(model, data, q)
        tcp = site_position(model, data, site_name)
        rotation = site_rotation_matrix(model, data, site_name)
        force, _contact_count = positive_contact_normal_force_between(
            model,
            data,
            geom_a_name=plane_geom_name,
            geom_b_name=contact_geom_name,
        )
        parts: list[np.ndarray] = []
        if "xy" in optimized_terms:
            parts.append((tcp[:2] - reference_xy) / thresholds.max_tangential_error_m)
        if "force" in optimized_terms:
            parts.append(np.array([(force - float(target_force_N)) / thresholds.max_force_error_N]))
        if "orientation" in optimized_terms:
            parts.append(
                orientation_error_rotvec(desired_rotation, rotation)
                / thresholds.max_orientation_error_rad
            )
        if not parts:
            return np.zeros(1, dtype=float)
        return np.concatenate(parts)

    case_defs = [
        ("xy_force", ("xy", "force")),
        ("xy_orientation", ("xy", "orientation")),
        ("force_orientation", ("force", "orientation")),
        ("xy_force_orientation", ("xy", "force", "orientation")),
    ]
    cases: list[GateAuditCase] = []
    for case_name, optimized_terms in case_defs:
        candidates: list[GateAuditCandidate] = []
        for seed_label, seed_q in seeds:
            result = least_squares(
                lambda q, terms=optimized_terms: residual(q, terms),
                seed_q,
                bounds=(q_min, q_max),
                max_nfev=int(max_nfev),
                xtol=1e-12,
                ftol=1e-12,
                gtol=1e-12,
            )
            candidates.append(
                evaluate(
                    result.x,
                    seed_label=seed_label,
                    optimized_terms=optimized_terms,
                    cost=float(result.cost),
                    nfev=int(result.nfev),
                    success=bool(result.success),
                    status=int(result.status),
                )
            )
        candidates.sort(key=lambda candidate: (candidate.max_gate_ratio, candidate.cost, candidate.seed_label))
        optimized_sorted = sorted(candidates, key=lambda candidate: (candidate.cost, candidate.max_gate_ratio, candidate.seed_label))
        cases.append(
            GateAuditCase(
                name=case_name,
                optimized_terms=optimized_terms,
                candidate_count=len(candidates),
                pass_count=sum(1 for candidate in candidates if candidate.passed),
                best_candidate=candidates[0],
                best_optimized_candidate=optimized_sorted[0],
            )
        )

    return ContactManifoldGateAuditResult(
        model_path=str(model_path),
        initial_q=q0.copy(),
        base_z_offset_m=float(base_z_offset_m),
        target_force_N=float(target_force_N),
        site_name=site_name,
        contact_geom_name=contact_geom_name,
        plane_geom_name=plane_geom_name,
        reference_xy_m=reference_xy.copy(),
        surface_normal_world=normal.copy(),
        target_signed_surface_distance_m=float(target_signed_surface_distance),
        thresholds=thresholds,
        seed_labels=[label for label, _ in seeds],
        cases=cases,
    )
