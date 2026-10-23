# Group, host, and control exceptions demonstration

This demo assesses three selected controls on the existing two RHEL 9 guests.
It does not implement or score all 350 client controls, and no CIS numbers have
been assigned without the client's exact OS/benchmark/profile mapping.

## Two-host scenario

| Host | Control | Approved requirement | Expected result once configured |
| --- | --- | --- | --- |
| `rhel_standard` | SNMP service | Enabled, standard baseline | `pass` |
| `rhel_standard` | SNMP community | Host-specific `special` credential | `approved_deviation` |
| `rhel_standard` | Console banner | Standard banner | `pass` |
| `rhel_exception` | SNMP service | Disabled by `database_servers` policy | `approved_deviation` |
| `rhel_exception` | SNMP community | No community requirement while SNMP is disabled | `not_applicable` |
| `rhel_exception` | Console banner | Approved control waiver; still observe its actual state | `approved_waiver` |

Group membership is an example classification; no database is installed.
Approved records are synthetic and expire March 1, 2027, inclusive in UTC.
The group record lives in `inventories/lab/group_vars/database_servers.yml`;
the host and control records live in their corresponding `host_vars` files.

The same schema also supports a server-specific SNMP-disabled alternate: put a
`snmp_service` record with `value: {enabled: false}` in that host's
`compliance_exceptions_host` list and specify its exact `host`. Host records take
precedence over group records. An alternate is actively enforced; a waiver
suppresses enforcement but retains observations and never becomes a pass.

## Current readiness

On October 23, 2026, both RHEL guests were verified registered, with BaseOS and
AppStream repositories enabled. The renewed AAP trial is active. Controller is
pinned to validated runtime commit
`d7d2d71bac52ba63304483ca4ba2804c7cd5c508` and injects the two community values
through a private credential.

SNMP is installed, enabled, and running on the standard host, listening only on
`127.0.0.1:161` for this demonstration. It uses the host's approved alternate
community. The exception host keeps SNMP disabled. Live Controller runs proved
the clean assessment, deliberate `public` drift, and approved repair; actual
SNMP queries verified the community before and after repair. The banner waiver
remained visible throughout. See [the validation log](validation.md) for results.
Repeat remediation made zero configuration changes on both guests.

Existing report checkpoints are 80 (clean), 85 (drift), 92 (repaired), and 99
(unchanged repeat), saved on `rhel_standard` under
`/var/tmp/auto-lab-reports/<report-job-id>/`. Each directory contains `report.md`
and `results.json`. Repair job 90 also records the original and final match flags.

This is a loopback demonstration, not a remotely reachable monitoring endpoint.
Reports retain the observed state, including drift or missing evidence if a
future run cannot verify the required configuration.

## External assessment and report

Use the Mac's existing Navigator runtime and local SSH overlay. This changes no
managed policy; it writes only evidence on the selected report host:

```bash
runtime_ee=sha256:d0ec1ac135c1eb831bb6c5fa6784e9ebebc407bec6141823b89c665b2a65f511
ansible-navigator run playbooks/demo_exceptions.yml \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml \
  --eei "$runtime_ee" --dc false \
  -e policy_report_host=rhel_standard
```

To compare communities, add `-e @/run/demo-secrets/snmp.yml` after arranging a
private read-only EE mount outside this repository. That input must define
`snmp_policy_communities` with `standard` and `special` secret keys. Do not put
actual community strings into Git, host variables, command arguments, or screenshots.

`playbooks/remediate_exceptions.yml` is the enforcement entry point after package
access and credentials are ready. Preview with `--check` first, apply, then repeat
and require zero unexpected configuration changes. It blocks before any writes
when a selected exception is expired, pending, or revoked.

## Presentation sequence

1. Show the inventory's `database_servers` membership and group approval.
2. Show the standard host's alternate credential reference and host approval.
3. Show the other host's banner control waiver, approver, ticket, and expiry.
4. Launch **Auto Lab | Scheduled audit and report** in Controller and explain
   its actual six host/control rows. Manual launch works while its schedule is disabled.
5. Show that the waived banner is still inspected and its mismatch remains visible.
6. Show the isolated test results: approved alternate vs unapproved `public`,
   expiry/revocation, conflict rejection, waiver non-enforcement, banner repair,
   idempotence, and explicit missing evidence. Label these as fixtures.
7. Show the clean audit checkpoint before introducing drift.
8. Launch **Auto Lab | Seed intentional drift - admin only** with
   `demo_drift_allowed: true`. In exception mode this changes the standard host's
   loopback-only SNMP community to `public` and restarts the service.
9. Run the audit workflow to retain the drift evidence, then run **Approved
   remediation**, approve its gate, and show the verification/report jobs.
10. Repeat remediation to demonstrate zero configuration changes. The group
    exception and banner waiver must remain visible in every report.

To repeat the isolated validation on the Mac, use the `runtime_ee` value above:

```bash
ansible-navigator exec --eei "$runtime_ee" --pp never --dc false \
  'python3 -m unittest discover -s tests -p test_exception_policy.py -v'
ansible-navigator run tests/exceptions.yml -i tests/inventory.yml \
  --eei "$runtime_ee" --dc false
ansible-navigator run tests/exceptions_check_mode.yml -i tests/inventory.yml \
  --eei "$runtime_ee" --dc false --check
```

These fixtures use disposable files inside the EE; they do not prove real SNMP
service behavior. See [the validation record](validation.md#three-scope-exception-preparation--2026-10-23)
for the checks performed and remaining limits.

The Markdown report includes every expected host/control. JSON includes an
expected-scope manifest and each observed result, with original and final match
flags, UTC timestamp, policy profile, exception metadata, and job/revision context.
An unreachable host or missing control must be discussed as missing evidence.
The audit is periodic/point-in-time; it does not prove continuous compliance.

## Controller activation

The exception overlay pins the reviewed, pushed runtime commit. Run the external
Controller bootstrap with `-e @controller/exception-demo.yml` plus
the existing private authentication/key mounts. Supply
`aap_demo_snmp_communities` privately with the two approved strings.

The overlay selects the new audit, remediation, and report entry points under
the existing constrained templates/workflows. It uses an exact revision
and adds a secret Controller credential only to the audit/remediation templates.
The operator approval boundary and disabled schedule remain in place. Credential
injection and workflow execution have been verified on this deployment; repeat
those checks when deploying to another environment.

Continue managing approved policy through Git review. Editing variables directly
in an SCM-managed AAP inventory can be overwritten on sync, and broad extra vars
can override inventory values. Approval dates and ticket strings are not an
external approval system; Remedy integration remains a separate milestone.
