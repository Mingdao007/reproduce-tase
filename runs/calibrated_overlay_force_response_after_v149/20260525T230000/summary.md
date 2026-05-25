# Calibrated Overlay Force Response Summary

Run root: `/home/andy/reproduce-tase/runs/calibrated_overlay_force_response_after_v149/20260525T230000`

- Audit passed: `True`
- Force-response ladder passed: `True`
- Rows: `7`
- Clean target contact in all rows: `True`
- Force at 1 mm: `11.078794158483424` N
- Max force: `14.36943859842967` N
- Completion claim allowed: `False`

| penetration m | target force N | target contacts | non-target contacts | min distance m |
| ---: | ---: | ---: | ---: | ---: |
| `0.0` | `0.0` | `1` | `0` | `0.0` |
| `0.0001` | `7.432339543010282` | `1` | `0` | `-0.00010000000000000286` |
| `0.00025` | `7.93408449665741` | `1` | `0` | `-0.0002500000000000002` |
| `0.0005` | `8.977491430922026` | `1` | `0` | `-0.0005000000000000004` |
| `0.001` | `11.078794158483424` | `1` | `0` | `-0.0010000000000000009` |
| `0.0015` | `12.724636394431727` | `1` | `0` | `-0.0015000000000000013` |
| `0.002` | `14.36943859842967` | `1` | `0` | `-0.0020000000000000087` |

Interpretation:

- The collision-masked overlay has a clean target-only contact response over the diagnostic penetration ladder.
- This is an offline diagnostic force-response probe only, not accepted contact calibration or hardware evidence.
