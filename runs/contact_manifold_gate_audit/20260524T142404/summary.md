# Contact-Manifold Gate Audit Summary

Run root: `/home/andy/reproduce-tase/runs/contact_manifold_gate_audit/20260524T142404`

## Result

- Seed count: `161`
- Target signed surface distance m: `-1.7843686194222996e-05`
- Strict pass count: `0`
- Strict best failed criteria: `tangential_error_m;orientation_error_rad`
- Strict best max gate ratio: `2.413534442118322`
- Strict best force error N: `0.005097551486581864`
- Strict best x/y error m: `0.0030075787462736734`
- Strict best orientation error rad: `0.07240603326354965`

## Gate Cases

### xy_force

- Optimized terms: `xy,force`
- Pass count: `0 / 161`
- Best failed criteria: `orientation_error_rad`
- Best force error N: `2.4868995751603507e-14`
- Best x/y error m: `1.2984463881799684e-15`
- Best orientation error rad: `0.14697007178233126`
- Best optimized failed criteria: `orientation_error_rad`
- Best optimized force error N: `2.4868995751603507e-14`
- Best optimized x/y error m: `1.2984463881799684e-15`
- Best optimized orientation error rad: `0.14697007178233126`

### xy_orientation

- Optimized terms: `xy,orientation`
- Pass count: `0 / 161`
- Best failed criteria: `force_error_N;contact_present`
- Best force error N: `5.0`
- Best x/y error m: `5.204170427930421e-18`
- Best orientation error rad: `5.551115123125783e-17`
- Best optimized failed criteria: `force_error_N;contact_present`
- Best optimized force error N: `5.0`
- Best optimized x/y error m: `5.204170427930421e-18`
- Best optimized orientation error rad: `5.551115123125783e-17`

### force_orientation

- Optimized terms: `force,orientation`
- Pass count: `0 / 161`
- Best failed criteria: `tangential_error_m;orientation_error_rad`
- Best force error N: `0.001940953114571542`
- Best x/y error m: `0.0076531799334050655`
- Best orientation error rad: `0.0875519802334906`
- Best optimized failed criteria: `tangential_error_m`
- Best optimized force error N: `1.6253665080512292e-13`
- Best optimized x/y error m: `0.014127706733724453`
- Best optimized orientation error rad: `3.608594916770049e-14`

### xy_force_orientation

- Optimized terms: `xy,force,orientation`
- Pass count: `0 / 161`
- Best failed criteria: `tangential_error_m;orientation_error_rad`
- Best force error N: `0.005097551486581864`
- Best x/y error m: `0.0030075787462736734`
- Best orientation error rad: `0.07240603326354965`
- Best optimized failed criteria: `tangential_error_m;orientation_error_rad`
- Best optimized force error N: `0.005097551486581864`
- Best optimized x/y error m: `0.0030075787462736734`
- Best optimized orientation error rad: `0.07240603326354965`

## Limits

This audit probes terminal gate compatibility from target-contact
neighborhoods. It does not prove global infeasibility and does not
authorize hardware use.
