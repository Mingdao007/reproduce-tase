# Paper 7DOF Contact Loop Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v42-paper-7dof-contact-loop`

## Scope

This branch follows the v41 paper-platform 7DOF diagnostic, which executed but
lost tail contact under the KKT-projection setting. The v42 question is narrow:
can the same separate 7DOF Section V executable maintain tail contact and
normal force under an explicitly labeled diagnostic setting?

No UR10e or OnRobot hardware commands were run.

## Change

`scripts/run_paper_7dof_section_v.py` now exposes these existing simulation
parameters at the command line:

- `--communication-delay-s`
- `--force-integral-limit`
- `--force-integral-leak`

A regression test records the contact-stabilized diagnostic setting:

```bash
scripts/run_tests.sh tests/test_paper_7dof.py
```

## Command

```bash
scripts/run_paper_7dof_section_v.py \
  --duration-s 5.0 \
  --dt-s 0.002 \
  --solver-mode pinv_bounded \
  --orientation-mode force_shortest_arc \
  --communication-delay-s 0.032 \
  --force-integral-limit 0.1 \
  --force-integral-leak 0.0
```

Run:

`runs/paper_7dof_section_v/20260524T114244`

Git state recorded by run:

- commit: `16ba42368f81145f2970c8d8d295f6ed238e7be4`
- dirty status before output creation: clean

## Metrics

| Metric | v41 KKT diagnostic | v42 contact-stabilized diagnostic |
|---|---:|---:|
| execution success | `true` | `true` |
| contact-force tail success | `false` | `true` |
| solver mode | `kkt_projection` | `pinv_bounded` |
| force-integral limit | `inf` | `0.1` |
| max abs qdot | `0.6318376969546269 rad/s` | `1.256600582289784 rad/s` |
| q bound violations | `0` | `0` |
| qdot bound violations | `0` | `0` |
| contact fraction | `0.273890443822471` | `0.4722111155537785` |
| tail contact fraction | `0.0` | `1.0` |
| tail force error mean | `5.0 N` | `0.013764149103712913 N` |
| final force error | `5.0 N` | `-0.0019105539077397538 N` |
| tail position error mean | `0.0030910509183547244 m` | `3.0743737697039117e-06 m` |
| tail orientation error mean | `0.00018635025045757645 rad` | `2.611691856523906e-06 rad` |

## Interpretation

The v42 run closes the v41 contact-tail failure for the separate 7DOF
diagnostic line. It does not close the paper-equivalent claim.

The improvement is explicitly diagnostic because it switches from
`kkt_projection` to `pinv_bounded` and caps the force integral. That makes the
Section V paper-platform line useful for continued simulation debugging, but
it is not the paper's finite-time KKT-projection result.

The correct claim after v42 is:

```text
paper_platform_7dof_contact_stabilized_diagnostic:
  execution_success = true
  contact_force_tail_success = true
  paper_faithful_kkt_parity = false
  hardware_readiness = false
```

## Remaining Blockers

- The paper-faithful KKT-projection 7DOF line still loses tail contact.
- Panda/Franka DH parameters are inherited from legacy MATLAB files and remain
  unverified against a vendor/manual model.
- The Section V desired-orientation signal remains a verified paper ambiguity.
- No Fig.5/Fig.6 numerical parity gate exists for the 7DOF Python line yet.
- No real hardware motion is authorized.

## Next Step

Either debug why the KKT-projection 7DOF line loses contact, or define a
separate paper-platform parity gate that compares the Python diagnostic line
against the legacy MATLAB/RNN outputs without mixing it with the UR10e adapted
claim.
