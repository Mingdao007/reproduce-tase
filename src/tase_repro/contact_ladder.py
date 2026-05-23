from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mujoco
import numpy as np


@dataclass(frozen=True)
class StaticContactMeasurement:
    base_z_offset_m: float
    mean_normal_force_N: float
    max_normal_force_N: float
    final_tcp_z_m: float
    mean_contact_count: float


@dataclass(frozen=True)
class InitialContactMeasurement:
    base_z_offset_m: float
    normal_force_N: float
    tcp_z_m: float
    contact_count: int


def positive_contact_normal_force(model: mujoco.MjModel, data: mujoco.MjData) -> float:
    total = 0.0
    for contact_idx in range(data.ncon):
        wrench = np.zeros(6)
        mujoco.mj_contactForce(model, data, contact_idx, wrench)
        total += max(0.0, float(wrench[0]))
    return total


def positive_contact_normal_force_vector(model: mujoco.MjModel, data: mujoco.MjData) -> np.ndarray:
    """Return the summed positive contact-normal force vector in world frame."""
    total = np.zeros(3, dtype=float)
    for contact_idx in range(data.ncon):
        contact = data.contact[contact_idx]
        wrench = np.zeros(6)
        mujoco.mj_contactForce(model, data, contact_idx, wrench)
        normal_force = max(0.0, float(wrench[0]))
        if normal_force > 0.0:
            normal_world = contact.frame.reshape(3, 3)[0].copy()
            total += normal_force * normal_world
    return total


def measure_static_contact_force(
    model_path: str | Path,
    *,
    base_z_offset_m: float,
    steps: int,
    tail_steps: int,
    site_name: str = "tcp_site_unverified_85mm",
) -> StaticContactMeasurement:
    """Measure steady contact normal force after offsetting base_link z.

    This is a simulation contact-model probe. It changes the model base
    position to create static penetration and must not be interpreted as a real
    robot command.
    """
    model = mujoco.MjModel.from_xml_path(str(Path(model_path)))
    base_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "base_link")
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)
    if base_id < 0:
        raise ValueError("base_link body not found")
    if site_id < 0:
        raise ValueError(f"site not found: {site_name}")
    model.body_pos[base_id, 2] += float(base_z_offset_m)

    data = mujoco.MjData(model)
    force_hist = np.empty(steps, dtype=float)
    contact_hist = np.empty(steps, dtype=int)
    for idx in range(steps):
        mujoco.mj_step(model, data)
        force_hist[idx] = positive_contact_normal_force(model, data)
        contact_hist[idx] = data.ncon

    tail = max(1, min(int(tail_steps), int(steps)))
    return StaticContactMeasurement(
        base_z_offset_m=float(base_z_offset_m),
        mean_normal_force_N=float(np.mean(force_hist[-tail:])),
        max_normal_force_N=float(np.max(force_hist)),
        final_tcp_z_m=float(data.site_xpos[site_id, 2]),
        mean_contact_count=float(np.mean(contact_hist[-tail:])),
    )


def measure_initial_contact_force(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    base_z_offset_m: float,
    site_name: str = "tcp_site_unverified_85mm",
) -> InitialContactMeasurement:
    """Measure contact force at a fixed initial posture and base z offset."""
    model = mujoco.MjModel.from_xml_path(str(Path(model_path)))
    base_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "base_link")
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)
    if base_id < 0:
        raise ValueError("base_link body not found")
    if site_id < 0:
        raise ValueError(f"site not found: {site_name}")
    q = np.asarray(initial_q, dtype=float)
    if q.shape != (model.nq,):
        raise ValueError(f"initial_q shape {q.shape} does not match model.nq={model.nq}")

    model.body_pos[base_id, 2] += float(base_z_offset_m)
    data = mujoco.MjData(model)
    data.qpos[:] = q
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)
    return InitialContactMeasurement(
        base_z_offset_m=float(base_z_offset_m),
        normal_force_N=positive_contact_normal_force(model, data),
        tcp_z_m=float(data.site_xpos[site_id, 2]),
        contact_count=int(data.ncon),
    )


def calibrate_base_z_for_initial_q_target_force(
    model_path: str | Path,
    *,
    initial_q: np.ndarray,
    target_force_N: float,
    lower_offset_m: float,
    upper_offset_m: float,
    tolerance_N: float,
    max_iterations: int = 50,
) -> InitialContactMeasurement:
    """Find a base z offset that starts a fixed posture near target force."""
    target = float(target_force_N)
    lower = float(lower_offset_m)
    upper = float(upper_offset_m)
    low_meas = measure_initial_contact_force(
        model_path,
        initial_q=initial_q,
        base_z_offset_m=lower,
    )
    high_meas = measure_initial_contact_force(
        model_path,
        initial_q=initial_q,
        base_z_offset_m=upper,
    )
    if low_meas.normal_force_N < target:
        raise ValueError(
            f"lower offset force {low_meas.normal_force_N:.6g} N is below target {target:.6g} N"
        )
    if high_meas.normal_force_N > target:
        raise ValueError(
            f"upper offset force {high_meas.normal_force_N:.6g} N is above target {target:.6g} N"
        )

    best = low_meas
    for _ in range(max_iterations):
        mid = 0.5 * (lower + upper)
        meas = measure_initial_contact_force(
            model_path,
            initial_q=initial_q,
            base_z_offset_m=mid,
        )
        best = meas
        if abs(meas.normal_force_N - target) <= tolerance_N:
            break
        if meas.normal_force_N > target:
            lower = mid
        else:
            upper = mid
    if abs(best.normal_force_N - target) > tolerance_N:
        raise ValueError(
            "could not calibrate initial posture to target force: "
            f"best force {best.normal_force_N:.6g} N, target {target:.6g} N, "
            f"tolerance {float(tolerance_N):.6g} N"
        )
    return best


def calibrate_base_z_for_target_force(
    model_path: str | Path,
    *,
    target_force_N: float,
    lower_offset_m: float,
    upper_offset_m: float,
    steps: int,
    tail_steps: int,
    tolerance_N: float,
    max_iterations: int = 40,
) -> StaticContactMeasurement:
    """Find a base z offset whose static contact force matches a target."""
    target = float(target_force_N)
    lower = float(lower_offset_m)
    upper = float(upper_offset_m)
    low_meas = measure_static_contact_force(
        model_path,
        base_z_offset_m=lower,
        steps=steps,
        tail_steps=tail_steps,
    )
    high_meas = measure_static_contact_force(
        model_path,
        base_z_offset_m=upper,
        steps=steps,
        tail_steps=tail_steps,
    )
    if low_meas.mean_normal_force_N < target:
        raise ValueError(
            f"lower offset force {low_meas.mean_normal_force_N:.6g} N is below target {target:.6g} N"
        )
    if high_meas.mean_normal_force_N > target:
        raise ValueError(
            f"upper offset force {high_meas.mean_normal_force_N:.6g} N is above target {target:.6g} N"
        )

    best = low_meas
    for _ in range(max_iterations):
        mid = 0.5 * (lower + upper)
        meas = measure_static_contact_force(
            model_path,
            base_z_offset_m=mid,
            steps=steps,
            tail_steps=tail_steps,
        )
        best = meas
        if abs(meas.mean_normal_force_N - target) <= tolerance_N:
            break
        if meas.mean_normal_force_N > target:
            lower = mid
        else:
            upper = mid
    return best
