# AAP configuration and demonstration

This page describes the original banner-only configuration. The live lab now uses
the [group, host, and control exception demo](exception-demo.md) through
`controller/exception-demo.yml`, with the same template and workflow names.
Use that runbook for the current presentation; running this page's bootstrap
without the exception overlay selects the original banner configuration.

## Prerequisites

- External Navigator validation passed and reviewed code pushed by the user.
- Two provisioned targets: standard RHEL and RHEL with the synthetic exception.
  Their NAT addresses are in the lab
  inventory. Verify Controller connectivity separately from the tested external
  Navigator route. The M5 host must never join `demo_targets`.
- Project synchronized from Git, with the reviewed revision fixed for a workflow
  run. Keep inventory policy data and code on the same approved revision.
- Machine credentials, trusted host keys, and required sudo on targets.
- Explicit supported EE digest matching external runtime validation.

Do not install OpenSCAP, Tenable, Lockdown, OPA, or another platform just for this
milestone. Start the narrative after a representative security finding was handed
to operations. No report parser or external ticket integration is implemented.

## Controller configuration

The external bootstrap is `playbooks/configure_controller.yml`, with environment
data in `controller/demo.yml` and reusable implementation in `roles/aap_demo/`.
It creates objects in the isolated **Auto Lab** organization. The banner-only
configuration uses the public HTTPS Git repository and pins reviewed commit
`225a3c5b0621a542ce45b31c754cd88421b4ebbe`. Project updates and branch overrides
at launch are disabled. Advance that revision deliberately after the user pushes
and the new runtime content passes external validation.

Bootstrap dependencies are declared separately in `controller/requirements.yml`:
certified `ansible.controller` 4.8.6 and `ansible.platform` 2.7.20260812, already
present in the verified supported EE. Platform modules manage gateway-owned
organizations and teams; Controller modules manage automation objects and their
roles. The managed-host jobs still use built-ins only.

Run configuration from the Mac through Navigator. Supply an AAP gateway OAuth
token in a private mounted extra-vars file, the lab CA, the existing fleet private
key, and verified public guest host keys. See [bootstrap inputs](../roles/aap_demo/README.md).
Keep CA verification enabled. Resolve `rhel-m5.lan` inside the EE, and set both
`SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` there: the platform action plugin performs
its API request in the control process. Do not put tokens or private keys under
the repository, including its ignored artifacts directory.

With those private mounts and environment settings in your local Navigator config:

```bash
ANSIBLE_NAVIGATOR_CONFIG=/path/to/private/navigator.yml \
  ansible-navigator run playbooks/configure_controller.yml \
  -e @/run/aap-session/auth.json --dc false
```

The token file contains the `aap_demo_token` variable. Revoke temporary tokens and
remove their private staging files after use. The guest Machine credential remains
encrypted in Controller for job execution; bootstrap does not rotate its key.

The separate SSH trust credential injects verified public host keys into each
job and requires strict checking. It does not disable checks globally.

## Job templates and access

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

Workflow: Pre-check -> Check -> Approval -> Remediate -> Check -> Report. Use sequential nodes,
not parallel merges of the same `compliance_results` artifact. A check that finds
drift completes successfully and records `disposition: drift`; it is not a scanner
execution failure. Rejection or timeout must not reach remediation. Route failed
execution to an operational failure notification/review, not to a report claiming
all targets were verified. The report consumes the last successful check evidence.

The audit workflow is Pre-check -> Check -> Report, without unattended remediation.
Job output and workflow artifacts provide execution evidence; Markdown/JSON files
on the report host survive EE teardown. Configure retention before recurring runs.

The October 23, 2026 Oracle retirement removes `oracle_standard` and its empty
group from the live demo inventory and reduces the report template's expected
hosts to the two RHEL guests. The reviewed Git revision above contains that
two-host inventory. Do not revert to the earlier three-host revision: inventory
synchronization would reintroduce the retired host. Project and inventory updates
on launch remain disabled.

Project update 65 successfully synchronized this revision on October 23, 2026.
Inventory update 66 parsed the two-host YAML but failed with
`Subscription has expired!`. The existing live inventory was verified to contain
only the two RHEL hosts and the `demo_targets`/`rhel` groups. Renew the AAP
subscription and retry inventory synchronization before claiming a successful
import of this revision.

The **Auto Lab Operators** team can execute both workflows and the standalone
pre-check/check templates. **Auto Lab Approvers** can approve the remediation
workflow, but cannot directly execute remediation. Add real users to the
appropriate team separately. Keep operator and approver identities separate for
the demonstration; using a platform administrator hides these permission boundaries.

The readiness survey accepts a timeout from 30 to 300 seconds, default 180.
Policy text, exceptions, inventory, and credentials are not survey inputs. The
administrator-only drift template requires the boolean `demo_drift_allowed: true`.

The approval expires after 600 seconds. All workflow edges are success-only;
rejection, timeout, or execution failure stops that path. There is no external
notification integration yet. Operators review failures in Controller.

The daily audit schedule is created **disabled**, at 14:00 UTC with a start date
of September 18, 2026. Enabling it is a separate operational decision after report
retention is defined. There is no unattended remediation schedule.

## Live sequence

1. Show a synthetic finding: console warning text or permissions differ from policy.
2. Show the shared baseline and the exception host's approved alternate wording.
3. Run Check and inspect actual values' match results for both RHEL hosts.
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
