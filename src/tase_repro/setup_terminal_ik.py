from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mujoco
import numpy as np
from scipy.optimize import least_squares

from tase_repro.contact import unit_vector
from tase_repro.contact_ladder import positive_contact_normal_force, positive_contact_normal_force_between
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


@dataclass(frozen=True)
class SetupTerminalThresholds:
    max_force_error_N: float = 0.25
    max_tangential_error_m: float = 0.002
    max_orientation_error_rad: float = 0.03

    def to_dict(self) -> dict:
        return {
            "max_force_error_N": float(self.max_force_error_N),
            "max_tangential_error_m": float(self.max_tangential_error_m),
            "max_orientation_error_rad": float(self.max_orientation_error_rad),
        }


@dataclass(frozen=True)
class SetupTerminalCandidate:
    seed_label: str
    q: np.ndarray
    cost: float
    success: bool
    status: int
    message: str
    nfev: int
    tcp_m: np.ndarray
    target_force_N: float
    force_N: float
    total_normal_force_N: float
    force_error_N: float
    tangential_error_xy_m: np.ndarray
    tangential_error_m: float
    orientation_error_rotvec: np.ndarray
    orientation_error_rad: float
    contact_present: bool
    target_contact_count: int
    criteria: dict
    failed_criteria: list[str]
    passed: bool
    max_gate_ratio: float

    def to_dict(self) -> dict:
        cost = None if not np.isfinite(self.cost) else float(self.cost)
        criteria = {
            name: {
                key: value
                for key, value in criterion.items()
            }
            for name, criterion in self.criteria.items()
        }
        return {
            "seed_label": self.seed_label,
            "q": [float(x) for x in self.q],
            "cost": cost,
            "success": bool(self.success),
            "status": int(self.status),
            "message": self.message,
            "nfev": int(self.nfev),
            "tcp_m": [float(x) for x in self.tcp_m],
            "target_force_N": float(self.target_force_N),
            "force_N": float(self.force_N),
            "total_normal_force_N": float(self.total_normal_force_N),
            "force_error_N": float(self.force_error_N),
            "tangential_error_xy_m": [float(x) for x in self.tangential_error_xy_m],
            "tangential_error_m": float(self.tangential_error_m),
            "orientation_error_rotvec": [float(x) for x in self.orientation_error_rotvec],
            "orientation_error_rad": float(self.orientation_error_rad),
            "contact_present": bool(self.contact_present),
            "target_contact_count": int(self.target_contact_count),
            "criteria": criteria,
            "failed_criteria": list(self.failed_criteria),
            "passed": bool(self.passed),
            "max_gate_ratio": float(self.max_gate_ratio),
        }


@dataclass(frozen=True)
class SetupTerminalIKResult:
    reference_xy_m: np.ndarray
    surface_normal_world: np.ndarray
    initial_q: np.ndarray
    initial_candidate: SetupTerminalCandidate
    candidates: list[SetupTerminalCandidate]
    best_candidate: SetupTerminalCandidate
    thresholds: SetupTerminalThresholds

    @property
    def pass_count(self) -> int:
        return sum(1 for candidate in self.candidates if candidate.passed)

    def to_dict(self) -> dict:
        return {
            "reference_xy_m": [float(x) for x in self.reference_xy_m],
            "surface_normal_world": [float(x) for x in self.surface_normal_world],
            "initial_q": [float(x) for x in self.initial_q],
            "thresholds": self.thresholds.to_dict(),
            "candidate_count": len(self.candidates),
            "pass_count": self.pass_count,
            "initial_candidate": self.initial_candidate.to_dict(),
            "best_candidate": self.best_candidate.to_dict(),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


def _criterion(actual: float, threshold: float, *, lower_is_better: bool = True) -> dict:
    if lower_is_better:
        passed = float(actual) <= float(threshold)
        operator = "<="
    else:
        passed = float(actual) >= float(threshold)
        operator = ">="
    return {
        "actual": float(actual),
        "operator": operator,
        "threshold": float(threshold),
        "passed": bool(passed),
    }


def evaluate_setup_terminal_candidate(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    *,
    q: np.ndarray,
    seed_label: str,
    cost: float,
    success: bool,
    status: int,
    message: str,
    nfev: int,
    site_name: str,
    contact_geom_name: str = "contact_tip",
    plane_geom_name: str = "contact_plane",
    reference_xy_m: np.ndarray,
    desired_rotation: np.ndarray,
    target_force_N: float,
    thresholds: SetupTerminalThresholds,
) -> SetupTerminalCandidate:
    q_array = np.asarray(q, dtype=float)
    set_qpos(model, data, q_array)
    mujoco.mj_forward(model, data)
    tcp = site_position(model, data, site_name)
    rotation = site_rotation_matrix(model, data, site_name)
    total_force = positive_contact_normal_force(model, data)
    force, target_contact_count = positive_contact_normal_force_between(
        model,
        data,
        geom_a_name=plane_geom_name,
        geom_b_name=contact_geom_name,
    )
    force_error = abs(float(force) - float(target_force_N))
    tangential_error_xy = tcp[:2] - np.asarray(reference_xy_m, dtype=float)
    tangential_error = float(np.linalg.norm(tangential_error_xy))
    orientation_error = orientation_error_rotvec(desired_rotation, rotation)
    orientation_error_norm = float(np.linalg.norm(orientation_error))
    criteria = {
        "force_error_N": _criterion(force_error, thresholds.max_force_error_N),
        "tangential_error_m": _criterion(tangential_error, thresholds.max_tangential_error_m),
        "orientation_error_rad": _criterion(orientation_error_norm, thresholds.max_orientation_error_rad),
        "contact_present": {
            "actual": bool(data.ncon > 0),
            "target_contact_count": int(target_contact_count),
            "operator": "is",
            "threshold": True,
            "passed": bool(target_contact_count > 0),
        },
    }
    failed = [name for name, criterion in criteria.items() if not criterion["passed"]]
    ratios = [
        force_error / thresholds.max_force_error_N,
        tangential_error / thresholds.max_tangential_error_m,
        orientation_error_norm / thresholds.max_orientation_error_rad,
        0.0 if target_contact_count > 0 else float("inf"),
    ]
    return SetupTerminalCandidate(
        seed_label=seed_label,
        q=q_array.copy(),
        cost=float(cost),
        success=bool(success),
        status=int(status),
        message=str(message),
        nfev=int(nfev),
        tcp_m=tcp.copy(),
        target_force_N=float(target_force_N),
        force_N=float(force),
        total_normal_force_N=float(total_force),
        force_error_N=float(force_error),
        tangential_error_xy_m=tangential_error_xy.copy(),
        tangential_error_m=tangential_error,
        orientation_error_rotvec=orientation_error.copy(),
        orientation_error_rad=orientation_error_norm,
        contact_present=bool(target_contact_count > 0),
        target_contact_count=int(target_contact_count),
        criteria=criteria,
        failed_criteria=failed,
        passed=not failed,
        max_gate_ratio=float(np.max(ratios)),
    )


def solve_setup_terminal_ik(
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
    random_seed_count: int = 32,
    random_seed_std_rad: float = 0.15,
    random_seed: int = 37,
    max_nfev: int = 300,
    posture_weight: float = 1e-4,
    extra_seed_qs: dict[str, np.ndarray] | None = None,
) -> SetupTerminalIKResult:
    """Audit whether a terminal setup q can satisfy x/y, force, and orientation gates.

    This is a terminal nonlinear least-squares feasibility probe, not a motion
    controller. It intentionally ignores path feasibility so it can distinguish
    terminal-configuration feasibility from the current Stage A velocity law.
    """
    if thresholds.max_force_error_N <= 0.0:
        raise ValueError("max_force_error_N must be positive")
    if thresholds.max_tangential_error_m <= 0.0:
        raise ValueError("max_tangential_error_m must be positive")
    if thresholds.max_orientation_error_rad <= 0.0:
        raise ValueError("max_orientation_error_rad must be positive")
    if random_seed_count < 0:
        raise ValueError("random_seed_count must be nonnegative")
    if random_seed_std_rad < 0.0:
        raise ValueError("random_seed_std_rad must be nonnegative")
    if max_nfev <= 0:
        raise ValueError("max_nfev must be positive")
    if posture_weight < 0.0:
        raise ValueError("posture_weight must be nonnegative")
    extra_seeds = {} if extra_seed_qs is None else dict(extra_seed_qs)

    model = load_model(model_path)
    apply_base_z_offset(model, base_z_offset_m)
    data = make_data(model)
    q_min, q_max = joint_ranges(model)
    q0 = np.asarray(initial_q, dtype=float)
    if q0.shape != (model.nq,):
        raise ValueError(f"initial_q shape {q0.shape} does not match model.nq={model.nq}")
    normal = unit_vector(np.asarray(surface_normal_world, dtype=float))

    set_qpos(model, data, q0)
    mujoco.mj_forward(model, data)
    reference_xy = site_position(model, data, site_name)[:2].copy()
    start_rotation = site_rotation_matrix(model, data, site_name)
    desired_rotation = rotation_aligning_local_z_to_normal(normal, reference_rotation=start_rotation)
    initial_candidate = evaluate_setup_terminal_candidate(
        model,
        data,
        q=q0,
        seed_label="initial_unoptimized",
        cost=float("nan"),
        success=True,
        status=0,
        message="not optimized",
        nfev=0,
        site_name=site_name,
        contact_geom_name=contact_geom_name,
        plane_geom_name=plane_geom_name,
        reference_xy_m=reference_xy,
        desired_rotation=desired_rotation,
        target_force_N=target_force_N,
        thresholds=thresholds,
    )

    seeds: list[tuple[str, np.ndarray]] = [("initial", q0.copy())]
    extra_seed_items: list[tuple[str, np.ndarray]] = []
    for label, seed_q in extra_seeds.items():
        seed = np.asarray(seed_q, dtype=float)
        if seed.shape != (model.nq,):
            raise ValueError(f"extra seed {label!r} shape {seed.shape} does not match model.nq={model.nq}")
        clipped = np.clip(seed, q_min, q_max)
        extra_seed_items.append((f"extra_{label}_unoptimized", clipped))
        seeds.append((f"extra_{label}", clipped))
    rng = np.random.default_rng(int(random_seed))
    for idx in range(int(random_seed_count)):
        perturbation = rng.normal(0.0, float(random_seed_std_rad), size=q0.shape)
        seeds.append((f"random_{idx:03d}", np.clip(q0 + perturbation, q_min, q_max)))

    def residual(q: np.ndarray) -> np.ndarray:
        set_qpos(model, data, q)
        mujoco.mj_forward(model, data)
        tcp = site_position(model, data, site_name)
        rotation = site_rotation_matrix(model, data, site_name)
        force, _target_contact_count = positive_contact_normal_force_between(
            model,
            data,
            geom_a_name=plane_geom_name,
            geom_b_name=contact_geom_name,
        )
        orientation_error = orientation_error_rotvec(desired_rotation, rotation)
        return np.concatenate(
            [
                (tcp[:2] - reference_xy) / thresholds.max_tangential_error_m,
                np.array([(force - float(target_force_N)) / thresholds.max_force_error_N]),
                orientation_error / thresholds.max_orientation_error_rad,
                float(posture_weight) * (q - q0),
            ]
        )

    candidates: list[SetupTerminalCandidate] = [
        evaluate_setup_terminal_candidate(
            model,
            data,
            q=seed_q,
            seed_label=label,
            cost=float("nan"),
            success=True,
            status=0,
            message="extra seed not optimized",
            nfev=0,
            site_name=site_name,
            contact_geom_name=contact_geom_name,
            plane_geom_name=plane_geom_name,
            reference_xy_m=reference_xy,
            desired_rotation=desired_rotation,
            target_force_N=target_force_N,
            thresholds=thresholds,
        )
        for label, seed_q in extra_seed_items
    ]
    for label, seed_q in seeds:
        result = least_squares(
            residual,
            seed_q,
            bounds=(q_min, q_max),
            max_nfev=int(max_nfev),
            xtol=1e-12,
            ftol=1e-12,
            gtol=1e-12,
        )
        candidate = evaluate_setup_terminal_candidate(
            model,
            data,
            q=result.x,
            seed_label=label,
            cost=float(result.cost),
            success=bool(result.success),
            status=int(result.status),
            message=str(result.message),
            nfev=int(result.nfev),
            site_name=site_name,
            contact_geom_name=contact_geom_name,
            plane_geom_name=plane_geom_name,
            reference_xy_m=reference_xy,
            desired_rotation=desired_rotation,
            target_force_N=target_force_N,
            thresholds=thresholds,
        )
        candidates.append(candidate)

    candidates.sort(key=lambda candidate: (candidate.max_gate_ratio, candidate.cost, candidate.seed_label))
    best_candidate = candidates[0]
    return SetupTerminalIKResult(
        reference_xy_m=reference_xy,
        surface_normal_world=normal,
        initial_q=q0.copy(),
        initial_candidate=initial_candidate,
        candidates=candidates,
        best_candidate=best_candidate,
        thresholds=thresholds,
    )
