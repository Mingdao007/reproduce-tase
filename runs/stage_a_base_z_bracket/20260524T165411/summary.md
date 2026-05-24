# Stage A Base-Z Bracket Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_base_z_bracket/20260524T165411`

- Case count: `13`
- Start pass count: `5`
- Terminal pass count: `5`
- Path geometry pass count: `4`
- Duration recovered count: `7`
- Max positive terminal-pass delta mm: `None`
- Max positive recovered delta mm: `None`

| delta mm | status | start | terminal | path min duration s | recovered durations | terminal orientation rad |
| ---: | --- | --- | --- | ---: | --- | ---: |
| `-1.0` | `recovered_at_tested_duration` | `True` | `True` | `15.652271522331025` | `16.0` | `0.047179212704768526` |
| `-0.75` | `path_geometry_failed` | `True` | `True` | `138.0288650739265` | `none` | `0.0555614106508681` |
| `-0.5` | `recovered_at_tested_duration` | `True` | `True` | `14.625580232388335` | `15.0, 16.0` | `0.06415852510723632` |
| `-0.25` | `recovered_at_tested_duration` | `True` | `True` | `14.37320363810477` | `15.0, 16.0` | `0.0729704774221456` |
| `0.0` | `recovered_at_tested_duration` | `True` | `True` | `14.332635022800167` | `15.0, 16.0` | `0.07240605683117833` |
| `0.05` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.0838175590896232` |
| `0.1` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.08565245135290023` |
| `0.15` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.0874945141256073` |
| `0.2` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.08934348318237911` |
| `0.25` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.09119904265401833` |
| `0.5` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.10056247728510045` |
| `0.75` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.11002164736335575` |
| `1.0` | `start_and_terminal_not_found` | `False` | `False` | `None` | `none` | `0.11948560786548146` |

Interpretation:

- This compact bracket locates where diagnostic start, terminal, path, and stitched feasibility break as base-z is perturbed.
- It does not replace strict paper-equivalent setup, contact-model calibration, or hardware validation.
