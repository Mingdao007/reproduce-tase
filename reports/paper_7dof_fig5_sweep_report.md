# Paper 7DOF Fig.5 r Sweep Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v46-paper-7dof-fig5-sweep`

## Scope

This branch adds Python 7DOF Fig.5 r-sweep coverage for the strict
paper-platform parity gate. The sweep records one 0-2 s diagnostic metrics
file for each paper Section V r value: `0.2`, `0.4`, `0.6`, `0.8`, and `1.0`.

This is coverage evidence, not paper-equivalent Fig.5 numerical parity.

## Run

- Command:
  `scripts/run_paper_7dof_fig5_r_sweep.py --duration-s 2.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Output:
  `runs/paper_7dof_fig5_r_sweep/20260524T121033`
- Code commit recorded by the run:
  `43f71fd79988f4f28549e213f542a3fa2fd30d28`
- Git state at run time:
  clean

## Result

All five configured r rows executed successfully and respected hard q/qdot
bounds:

| r | execution | task residual RMS |
| ---: | ---: | ---: |
| `0.2` | `true` | `0.13487857241557796` |
| `0.4` | `true` | `0.1212787876329949` |
| `0.6` | `true` | `0.12141523603923539` |
| `0.8` | `true` | `0.1243757377448289` |
| `1.0` | `true` | `0.12967020697293458` |

The strict parity evaluator now validates that each configured r metrics file
exists, contains the expected `fig5_r_value`, has `execution_success = true`,
and covers the required `2.0 s` window.

## Gate Effect

The v46 parity evaluation at
`runs/paper_platform_parity_eval/20260524T121116` changes
`fig5_r_sweep_coverage` from `false` to `true`.

Strict parity remains failed because:

- `fig6_q7_22s_landmark = false`
- `paper_assumption_compatibility = false`

## Next Step

Investigate the measured q7-at-22 s mismatch and remove or justify the
finite force-integral cap before making stronger paper-platform claims.
