# AAP policy remediation demo

This repository demonstrates the hand-off after a security team receives a
Tenable finding: check the current setting, resolve an approved host exception,
remediate through AAP, verify the result, and retain evidence.

The first implemented control is the **console login warning banner** at
`/etc/issue`, including its ownership and permissions. The baseline and approved
alternate wording are synthetic examples. This is selected-policy automation,
not a CIS Level 2 scanner, a Tenable integration, or evidence of full CIS compliance.
Exact CIS identifiers must be mapped to the client's confirmed OS and benchmark
versions before using them in customer reports. `/etc/issue` is the console banner;
this milestone does not configure the SSH `Banner` directive.

## Development and execution

1. Edit and validate on a device external to M5.
2. Run checks through Navigator with the explicitly selected EE.
3. The user reviews and pushes the repository to GitHub.
4. AAP synchronizes its Project from Git and runs against managed demo targets.

M5 is not a remediation target. No development checkout belongs on M5. The
lab inventory contains the verified NAT addresses of the two isolated RHEL guests.
External access requires the Mac-only jump-host overlay described in
[managed-target provisioning](docs/managed-targets.md).
Supply SSH identities through AAP machine credentials or your external SSH agent;
never put private keys or passwords into this repository. Keep SSH host-key
verification enabled and establish trust before the first run.

## Repository layout

| Location | Purpose |
| --- | --- |
| `playbooks/` | Thin pre-check, check, remediate, report, and opt-in drift entry points |
| `roles/target_precheck/` | Read-only guest identity, initialization, and access checks |
| `roles/compliance_banner/` | Policy validation, checks, remediation, verification, evidence |
| `roles/policy_report/` | Consolidated Markdown and JSON evidence |
| `roles/demo_drift/` | Explicitly authorized demonstration drift |
| `roles/aap_demo/` | External bootstrap of isolated Controller objects and permissions |
| `controller/` | Reviewed Controller configuration and certified bootstrap dependencies |
| `inventories/lab/` | Two managed RHEL guests, baseline, and one scoped exception |
| `tests/` | Disposable EE-local behavior tests; not a managed-host certification |
| `docs/` | AAP configuration, demonstration steps, and validation record |
| `ansible-navigator.yml` | Supported runtime EE pinned by digest |
| `requirements.yml` | Empty managed-host dependency list; workload uses built-ins |

## First run

The external device needs Navigator and a working container runtime. The pinned
supported EE must already be cached or pulled with your own registry access.
Navigator uses `pull.policy: never` to avoid silently changing the test runtime.
On Apple Silicon this x86_64 image requires working emulation; an ARM-only check
is not proof that the Controller's x86_64 image works.

On this Mac, the image was copied from M5 as a Docker archive. That preserves
its verified image ID but not the registry digest reference. Append the local
`--eei` override documented in [validation](docs/validation.md) to the commands
below until the registry-referenced image is available locally.

From the repository root:

```bash
ansible-navigator inventory -i inventories/lab/hosts.yml --graph
ansible-navigator run playbooks/check_policy.yml --syntax-check
ansible-navigator run tests/banner.yml -i tests/inventory.yml
```

For live tests from the Mac, use the local overlay and verified EE override shown
in [managed-target provisioning](docs/managed-targets.md). The policy sequence is:

```bash
runtime_ee=sha256:d0ec1ac135c1eb831bb6c5fa6784e9ebebc407bec6141823b89c665b2a65f511
ansible-navigator run playbooks/check_policy.yml --limit rhel_standard \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee"
ansible-navigator run playbooks/remediate_policy.yml --limit rhel_standard --check --diff \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee"
ansible-navigator run playbooks/remediate_policy.yml --limit rhel_standard \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee"
ansible-navigator run playbooks/remediate_policy.yml --limit rhel_standard \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee"
```

The last run must make zero unexpected configuration changes. A check-mode report
describes observed state and predicted changes; it does not claim remediation
actually occurred. Normal checks publish evidence even when drift is present.
Check the result's `disposition`; a successful Ansible job does not mean the
host passed its policy. Invalid policy, unreadable evidence, and unsafe paths
fail the job instead of being reported as compliant.

## Design choices

- The desired text is inventory data. The role implements the mechanism.
- Approved exceptions specify an exact alternate value. They are not blanket
  skips: an unexpected third value or wrong permissions is still drift.
- A timestamped exception valid through its UTC expiry date applies only to its
  named host, profile, and control. Expired records are reported; remediation
  stops until a reviewer renews or removes the exception in Git.
- Runtime approval authorizes a job. Git review authorizes policy and exceptions.
  An approval reference is evidence metadata, not external ticket validation.
- RHEL System Roles were checked for a fitting subsystem role. A console text
  file is adequately managed by `ansible.builtin.template`, `stat`, and `slurp`.
  No certified collection is needed for this file-only capability. No community
  collection, shell command, or new scanner dependency is introduced.
- No restart handler is needed: the console reads the banner file for display.
  Future service configuration should use a handler when activation requires it.
- Audits use escalation only to read a file the connection user cannot read;
  remediation escalates for the privileged file write. Reports use the report
  host's connection account without escalation.

See [the AAP runbook](docs/aap-demo.md), [validation](docs/validation.md), and
[managed-target provisioning](docs/managed-targets.md), plus
[role inputs](roles/compliance_banner/README.md). Documentation under `.codex/`
remains the repository authority; the existing server-info draft is still pending
user review.
