# Selected-control exceptions

Evaluates three demo controls on RHEL 9: `snmp_service`, `snmp_community`, and
`console_login_banner`. These are descriptive policy IDs, not verified CIS IDs.
This role resolves approvals, invokes the reusable SNMP and banner roles, and
publishes one `compliance_results` host record for AAP workflow hand-off.

| Input | Default | Purpose |
| --- | --- | --- |
| `compliance_exceptions_operation` | `audit` | Read-only assessment or `remediate` |
| `compliance_exceptions_profile` | `linux_demo` | Implemented demonstration profile |
| `compliance_exceptions_group` | `[]` | Group-scoped records inherited through inventory |
| `compliance_exceptions_host` | `[]` | Host-scoped records |
| `compliance_exceptions_control` | `[]` | Host/control-specific records, including waivers |
| `compliance_exceptions_controls` | Three IDs above | Fixed implemented catalog |

Every record requires `id`, `control`, `profile`, `status`, `kind`, `reason`,
`approved_by`, `ticket`, and a quoted `expires: YYYY-MM-DD`. Group records require
the exact `group` membership; other records require the exact inventory `host`.
The ticket is reviewed metadata, not a live Remedy approval verification.

`kind: alternate` requires a `value` mapping appropriate to the control:

- `snmp_service`: `enabled: true` or `false` (a boolean).
- `snmp_community`: `community_ref: standard` or another supplied credential key.
- `console_login_banner`: newline-terminated `text`.

`kind: waiver` accepts the observed deviation and suppresses that control's
enforcement. It takes no alternate value and never counts as a pass. The banner
waiver covers both text and permissions in this selected demo control. It does
not waive unrelated SNMP controls. SNMP service waivers also prevent service
activation/restart and dependent configuration writes; unresolved community drift
remains visible rather than claiming it was repaired.

Selection order is explicit: control record, then host record, then group record.
Reports retain the selected scope and superseded IDs. Duplicate IDs and multiple
records for the same control at one level fail validation. An expired, pending,
or revoked selected record blocks fallback to a less-specific approval and blocks
remediation before any control is changed. Expiry includes the whole UTC date.

Ansible replaces inventory lists; it does not merge sibling group lists. This
demo uses one exception-bearing group. Consolidate the reviewed group list when
introducing multiple applicable groups; do not rely on alphabetical group precedence.
Keep policy data Git-backed and restrict inventory editing/extra vars to reviewers.

The old `compliance_banner_exception` remains for the original banner-only demo.
This role explicitly supplies its own normalized banner exception so the two
examples do not silently combine.

Results distinguish `pass`, `approved_deviation`, `approved_waiver`, `drift`,
`not_applicable`, `exception_review_required`, and `unknown`. A community check is
not applicable when effective policy disables SNMP; this is computed policy
applicability, not a free-form exception status. Missing community credentials
or unavailable service facts produce unknown evidence. Failed/unreachable hosts
are represented as missing by the report's independently defined expected scope.

The result includes before/observed match flags, timestamp, profile, approval
metadata, operation/check-mode status, and AAP job/revision when available.
No raw SNMP configuration or community string belongs in its output.
Match fields contain booleans when evaluated and `not_evaluated` when evidence
is unavailable or the community control is not applicable.
