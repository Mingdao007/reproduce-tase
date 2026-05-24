# TCP Contact Model Audit Summary

Run root: `/home/andy/reproduce-tase/runs/tcp_contact_model_audit/20260524T140535`

## Result

- Config TCP guess matches model body offset: `True`
- Config TCP guess matches EOAT note distance: `True`
- Site coincident with contact geom center: `False`
- Contact surface offset requires model decision: `False`
- Parent-to-site distance m: `0.085`
- Contact geom local pos m: `[0.0, 0.0, 0.045]`
- Contact geom radius m: `0.045`
- Contact count: `1`
- Normal force N: `4.9999999999967395`
- Site-to-sphere-surface projection on normal m: `0.0006836511144550518`
- Parent-to-sphere-surface distance m: `0.0846776706744086`
- Surface extension beyond declared TCP m: `-0.00068365111445505`

## Interpretation

The current model separates the TCP site from the colliding sphere
center. This resolves the v53 center/site coincidence for a
contact-point convention, but it remains an approximate simulation
proxy. Any residual site-to-surface projection reflects the current
posture and plane-normal alignment; hardware use still requires
mounted-stack measurement and explicit approval.
