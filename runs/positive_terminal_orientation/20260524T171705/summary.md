# Positive Terminal Orientation Summary

Run root: `/home/andy/reproduce-tase/runs/positive_terminal_orientation/20260524T171705`

- Case count: `16`
- Variant count: `2`

| variant | diagnostic pass | force/x-y/contact pass | max diagnostic delta mm | threshold for all force/x-y/contact cases rad | max full error rad | max yaw gap rad |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `contact_point` | `0` | `8` | `None` | `0.11948560786548146` | `0.11948560786548146` | `4.884981308350689e-15` |
| `legacy_center` | `6` | `8` | `0.5` | `0.09525838838593075` | `0.09525838838593075` | `2.400857290751901e-15` |

| variant | delta mm | diagnostic pass | force/x-y/contact | full rotation rad | force-normal-only rad | -z convention rad |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| `contact_point` | `0.05` | `False` | `True` | `0.0838175590896232` | `0.08381755908962295` | `3.0577750945001703` |
| `contact_point` | `0.1` | `False` | `True` | `0.08565245135290023` | `0.08565245135289722` | `3.055940202236896` |
| `contact_point` | `0.15` | `False` | `True` | `0.0874945141256073` | `0.08749451412560418` | `3.054098139464189` |
| `contact_point` | `0.2` | `False` | `True` | `0.08934348318237911` | `0.08934348318237903` | `3.052249170407414` |
| `contact_point` | `0.25` | `False` | `True` | `0.09119904265401833` | `0.09119904265401542` | `3.0503936109357777` |
| `contact_point` | `0.5` | `False` | `True` | `0.10056247728510045` | `0.10056247728509893` | `3.0410301763046945` |
| `contact_point` | `0.75` | `False` | `True` | `0.11002164736335575` | `0.11002164736335086` | `3.0315710062264425` |
| `contact_point` | `1.0` | `False` | `True` | `0.11948560786548146` | `0.11948560786547915` | `3.022107045724314` |
| `legacy_center` | `0.05` | `True` | `True` | `0.06075402900960788` | `0.06075402900960761` | `3.0808386245801858` |
| `legacy_center` | `0.1` | `True` | `True` | `0.06254943406970642` | `0.06254943406970456` | `3.0790432195200887` |
| `legacy_center` | `0.15` | `True` | `True` | `0.06435234861052946` | `0.06435234861052797` | `3.077240304979265` |
| `legacy_center` | `0.2` | `True` | `True` | `0.0661622106647289` | `0.06616221066472865` | `3.0754304429250645` |
| `legacy_center` | `0.25` | `True` | `True` | `0.06797837648702` | `0.0679783764870176` | `3.0736142771027755` |
| `legacy_center` | `0.5` | `True` | `True` | `0.07712556389339752` | `0.07712556389339624` | `3.064467089696397` |
| `legacy_center` | `0.75` | `False` | `True` | `0.08628270519469884` | `0.08628270519469683` | `3.0553099483950965` |
| `legacy_center` | `1.0` | `False` | `True` | `0.09525838838593075` | `0.09525838838593054` | `3.0463342652038627` |

Interpretation:

- Full-rotation and force-normal-only errors are effectively identical when the yaw gap is near zero.
- The `legacy_center` variant is a known flawed geometry comparison, not a hardware-ready fix.
- This audit is terminal-state simulation evidence only; it does not prove path recovery, robustness, or hardware readiness.
