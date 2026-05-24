# Paper 7DOF KKT Contact Recovery Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v43-paper-7dof-kkt-sweep`

## Scope

This branch follows v42. v42 showed that the 7DOF Section V diagnostic can
hold contact with an instantaneous `pinv_bounded` projection and a capped force
integral. The remaining question was whether the paper-style
`kkt_projection` path itself could maintain tail contact.

No UR10e or OnRobot hardware commands were run.

## Change

Added a regression test for the capped-integral KKT diagnostic:

```bash
scripts/run_tests.sh tests/test_paper_7dof.py
```

The executable code path already existed from v42. This branch records a clean
KKT run using those CLI parameters.

## Command

```bash
scripts/run_paper_7dof_section_v.py \
  --duration-s 5.0 \
  --dt-s 0.002 \
  --solver-mode kkt_projection \
  --orientation-mode force_shortest_arc \
  --communication-delay-s 0.032 \
  --force-integral-limit 0.1 \
  --force-integral-leak 0.0
```

Run:

`runs/paper_7dof_section_v/20260524T114736`

Git state recorded by run:

- commit: `38216bba5e08af8fbf0f078583f438c044990d68`
- dirty status before output creation: clean

## Metrics

| Metric | v41 KKT diagnostic | v43 capped-integral KKT |
|---|---:|---:|
| execution success | `true` | `true` |
| contact-force tail success | `false` | `true` |
| solver mode | `kkt_projection` | `kkt_projection` |
| force-integral limit | `inf` | `0.1` |
| max abs qdot | `0.6318376969546269 rad/s` | `0.6331334903981037 rad/s` |
| q bound violations | `0` | `0` |
| qdot bound violations | `0` | `0` |
| contact fraction | `0.273890443822471` | `0.6173530587764894` |
| tail contact fraction | `0.0` | `1.0` |
| tail force error mean | `5.0 N` | `0.06720487008205062 N` |
| final force error | `5.0 N` | `-0.019054957571588815 N` |
| tail position error mean | `0.0030910509183547244 m` | `0.00044122814610554124 m` |
| tail orientation error mean | `0.00018635025045757645 rad` | `2.7345108152399078e-05 rad` |

## Interpretation

The v43 run closes the KKT contact-loss symptom under a bounded-integral
diagnostic setting. The failure was not intrinsic to the `kkt_projection`
mapping; the unbounded force integral in v41 was enough to drive the normal
loop out of tail contact.

This still does not prove paper-equivalent numerical parity:

- The force-integral cap is an explicit simulation anti-windup decision, not a
  PDF-verified Section V parameter.
- The Panda/Franka DH parameters are inherited from legacy MATLAB audit files.
- The desired orientation remains based on the documented force-normal
  shortest-arc interpretation of an ambiguous paper equation.
- At v43, no Fig.5/Fig.6 parity gate had been defined for the Python 7DOF
  line. v44 adds that gate and records it as failing for this candidate.

The correct claim after v43 is:

```text
paper_platform_7dof_capped_integral_kkt_contact_diagnostic:
  execution_success = true
  contact_force_tail_success = true
  paper_equivalent_numerical_parity = false
  hardware_readiness = false
```

## Next Step

Use the v44 paper-platform parity gate with a 30 s Python candidate, or
separately audit the Panda/Franka DH model against a vendor/manual source
before using the Python 7DOF line for stronger paper-platform claims.
