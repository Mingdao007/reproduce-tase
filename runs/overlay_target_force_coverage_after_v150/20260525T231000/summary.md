# Overlay Target Force Coverage Summary

Run root: `/home/andy/reproduce-tase/runs/overlay_target_force_coverage_after_v150/20260525T231000`

- Audit passed: `True`
- Target force: `5.0` N
- Target force reachable in scan: `False`
- Coverage gap identified: `True`
- Minimum positive force: `7.136494172695263` N
- Best penetration: `1e-12` m
- Best force: `7.136494172695263` N
- Best absolute error: `2.1364941726952633` N
- Completion claim allowed: `False`

| penetration m | target force N | target contacts | non-target contacts |
| ---: | ---: | ---: | ---: |
| `0.0` | `0.0` | `1` | `0` |
| `1e-12` | `7.136494172695263` | `1` | `0` |
| `1e-10` | `7.136494452570067` | `1` | `0` |
| `1e-09` | `7.136496996887648` | `1` | `0` |
| `1e-08` | `7.1365224401727625` | `1` | `0` |
| `1e-07` | `7.136776883947843` | `1` | `0` |
| `1e-06` | `7.139322414876828` | `1` | `0` |
| `2e-06` | `7.142153116999815` | `1` | `0` |
| `5e-06` | `7.150660018343155` | `1` | `0` |
| `1e-05` | `7.1648878180087126` | `1` | `0` |
| `2e-05` | `7.1935318956048215` | `1` | `0` |
| `5e-05` | `7.281019561586294` | `1` | `0` |
| `0.0001` | `7.432339543010282` | `1` | `0` |
| `0.00025` | `7.93408449665741` | `1` | `0` |
| `0.0005` | `8.977491430922026` | `1` | `0` |
| `0.001` | `11.078794158483424` | `1` | `0` |
| `0.0015` | `12.724636394431727` | `1` | `0` |
| `0.002` | `14.36943859842967` | `1` | `0` |

Interpretation:

- The current diagnostic overlay jumps from zero force at tangent contact to a minimum positive force above the 5 N target.
- This is a non-final simulation-debugging blocker, not accepted contact calibration.
