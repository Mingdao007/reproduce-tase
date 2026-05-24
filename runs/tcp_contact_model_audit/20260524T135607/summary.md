# TCP Contact Model Audit Summary

Run root: `/home/andy/reproduce-tase/runs/tcp_contact_model_audit/20260524T135607`

## Result

- Config TCP guess matches model body offset: `True`
- Config TCP guess matches EOAT note distance: `True`
- Site coincident with contact geom center: `True`
- Contact surface offset requires model decision: `True`
- Parent-to-site distance m: `0.085`
- Contact geom radius m: `0.045`
- Contact count: `1`
- Normal force N: `5.000000003321885`
- Site-to-sphere-surface projection on normal m: `0.04500000000000001`
- Parent-to-sphere-surface distance m: `0.12955222618906498`
- Surface extension beyond declared TCP m: `0.04431634888554499`

## Interpretation

The current model places the TCP site at the center of the colliding
sphere. If the 85 mm EOAT note is intended to be the actual contact
point, then this model adds a contact-surface offset of roughly the
sphere radius. If it is intended to be the sphere center, the physical
contact point is not the configured TCP. This remains simulation-only
and is not hardware-ready.
