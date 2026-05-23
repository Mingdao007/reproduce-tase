from __future__ import annotations

import numpy as np

from tase_repro.finite_time import sigr, simulate_scalar_convergence


def test_sigr_is_odd_and_preserves_zero() -> None:
    values = np.array([-4.0, -1.0, 0.0, 1.0, 4.0])
    out = sigr(values, 0.5)
    assert out[2] == 0.0
    np.testing.assert_allclose(out, -sigr(-values, 0.5))


def test_lower_r_converges_faster_for_scalar_template() -> None:
    kwargs = dict(initial_error=1.0, gain=5.0, dt=0.0005, duration_s=2.0, convergence_tol=0.001)
    r02 = simulate_scalar_convergence(r=0.2, **kwargs)
    r10 = simulate_scalar_convergence(r=1.0, **kwargs)
    assert r02["convergence_time_s"] < r10["convergence_time_s"]
    assert r02["tail_abs_error"] < 0.001

