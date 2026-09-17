# AAP configuration and demonstration

## Prerequisites

- External Navigator validation passed and reviewed code pushed by the user.
- Three provisioned targets: standard RHEL, standard Oracle Linux,
  and RHEL with the synthetic exception. Their NAT addresses are in the lab
  inventory. Verify Controller connectivity separately from the tested external
  Navigator route. The M5 host must never join `demo_targets`.
- Project synchronized from Git, with the reviewed revision fixed for a workflow
  run. Keep inventory policy data and code on the same approved revision.
- Machine credentials, trusted host keys, and required sudo on targets.
- Explicit supported EE digest matching external runtime validation.

Do not install OpenSCAP, Tenable, Lockdown, OPA, or another platform just for this
milestone. Start the narrative after a representative security finding was handed
to operations. No report parser or external ticket integration is implemented.

## Controller objects to configure after the user pushes

| Template | Playbook | Intended access |
| --- | --- | --- |
| Pre-check targets | `playbooks/precheck_targets.yml` | Read-only readiness verification |
| Check policy | `playbooks/check_policy.yml` | Operator / scheduled read-only checks |
| Remediate policy | `playbooks/remediate_policy.yml` | Execute through approved workflow |
| Report policy | `playbooks/report_policy.yml` | Workflow final node |
| Seed demo drift | `playbooks/seed_demo_drift.yml` | Demo administrator only |

Give the report template `policy_report_host: rhel_standard` through trusted
configuration. Ensure its machine credential can reach that host. If the selected
workflow scope is smaller than the inventory, set `policy_report_expected_hosts`
to that exact scope so missing evidence is meaningful. Do not pass a managed-host
limit that excludes `localhost` to the report template.

Use RBAC to separate operator, policy editor, and approver responsibilities. Do not
grant operators Project/Inventory administration, arbitrary extra vars, editable
credentials, or direct execution of the remediation template. Confirm effective
permissions with the intended test users; a diagram alone does not enforce them.
Surveys should offer only supported target choices/profile names. Policy text,
file paths, exceptions, and report destinations are not operator inputs.

Workflow: Check -> Approval -> Remediate -> Check -> Report. Use sequential nodes,
not parallel merges of the same `compliance_results` artifact. A check that finds
drift completes successfully and records `disposition: drift`; it is not a scanner
execution failure. Rejection or timeout must not reach remediation. Route failed
execution to an operational failure notification/review, not to a report claiming
all targets were verified. The report consumes the last successful check evidence.

Schedule Check -> Report for drift monitoring without unattended remediation.
Job output and workflow artifacts provide execution evidence; Markdown/JSON files
on the report host survive EE teardown. Configure retention before recurring runs.

## Live sequence

1. Show a synthetic finding: console warning text or permissions differ from policy.
2. Show the shared baseline and the exception host's approved alternate wording.
3. Run Check and inspect actual values' match results for all three hosts.
4. Approve remediation. Show standard hosts meeting baseline and the exception
   host meeting its allowed value, while remaining a recorded baseline deviation.
5. Run remediation a second time: no unexpected configuration changes.
6. On one standard target, run the administrator-only drift job with explicit
   boolean opt-in. Check again, approve correction, and show successful verification.
7. In a reviewed Git change, expire/remove the exception. The user pushes, AAP
   syncs, and Check shows its new disposition. An expired record blocks remediation;
   remove or renew it through review before proceeding. Do not bypass this with a survey.
8. Open the consolidated report and the related AAP jobs. Distinguish baseline
   matches, allowed deviations, drift, expired approvals, and missing evidence.

This scope demonstrates policy remediation and exception governance. It does not
claim complete CIS Level 2 coverage, reproduce Tenable scoring, or prove an
external approval ticket is authentic. OS/benchmark-specific CIS mapping comes
when the customer's precise versions and selected controls are confirmed.
