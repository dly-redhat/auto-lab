# Validation

All Ansible checks must run through Navigator on an external device. The project
configuration selects the supported x86_64 EE by digest. The tooling image is a
separate, explicitly selected image when lint tools are absent from that runtime.

Required checks:

1. Navigator exec: `yamllint .` and `ansible-lint --offline` in the tooling image.
2. Navigator inventory: inspect the example inventory graph.
3. Navigator run: syntax-check every playbook and test in the supported EE.
4. Navigator run: execute `tests/banner.yml`, `tests/report.yml`, and
   `tests/check_mode.yml --check` in the supported EE.
5. After provisioning: external Navigator SSH check, remediation, check mode,
   second-run idempotence, and functional checks on both RHEL demo targets.
6. After the user pushes: verify Project sync, the same selected EE, workflow
   artifact hand-off, report persistence, RBAC, rejection/timeout, and schedule behavior.

The EE-local tests use temporary files inside the container. They do not prove
guest networking, sudo, actual console display, Oracle behavior, or Controller
workflow behavior. Test fixture cleanup is separate from policy idempotence.

## External tooling

On the Mac, Navigator 26.8.0 runs with Podman 6.1.2 in the
`auto-lab-validation` machine (2 vCPUs, 4 GiB RAM, 30 GiB virtual disk).
The runtime is external to M5. Start it with
`podman machine start auto-lab-validation` when needed and stop it with
`podman machine stop auto-lab-validation` to release its memory.

The lint image is the upstream Ansible development-tools image, independently
selected from the supported runtime EE. It is tooling, not an additional
collection dependency of this project. On this ARM Mac, the verified image is:

```text
ghcr.io/ansible/community-ansible-dev-tools@sha256:b0d93c387531363921868482042dbe22f141056b1f8bd4b3647dc224bbb51feb
```

Run lint through Navigator, overriding the runtime architecture for this ARM image:

```bash
ansible-navigator exec --mode stdout \
  --eei ghcr.io/ansible/community-ansible-dev-tools@sha256:b0d93c387531363921868482042dbe22f141056b1f8bd4b3647dc224bbb51feb \
  --co=--platform=linux/arm64 --pp never --dc false \
  'export ANSIBLE_COLLECTIONS_PATH="$PWD/.ansible/collections:/usr/share/ansible/collections"; yamllint . && ansible-lint --offline'
```

YAML lint and Ansible lint's `production` profile passed on 2026-09-16.
No managed-host or Controller pass is implied by a syntax check.

For the Controller bootstrap, lint also needs the two certified collections in
`controller/requirements.yml` for module resolution. This Mac has copies from the
verified supported EE under ignored `.ansible/collections/`. The override above
makes those available to the separate lint image. On another device, install the
declared versions through Navigator with appropriate Automation Hub access, or
copy them from the same verified EE. Do not silently substitute unpinned versions.

## Supported runtime on this Mac

The supported EE was exported from M5's existing image cache and imported on the
Mac. No Ansible development tests ran on M5. The original registry manifest digest
is pinned in `ansible-navigator.yml`. Docker-archive import did not retain that
registry reference; both machines have the same image configuration ID:

```text
sha256:d0ec1ac135c1eb831bb6c5fa6784e9ebebc407bec6141823b89c665b2a65f511
```

This ID is distinct from the registry manifest digest. Use the verified local
image explicitly when running the copied image:

```bash
runtime_ee=sha256:d0ec1ac135c1eb831bb6c5fa6784e9ebebc407bec6141823b89c665b2a65f511
ansible-navigator exec --eei "$runtime_ee" --dc false 'ansible --version'
ansible-navigator exec --eei "$runtime_ee" --dc false \
  'ansible-inventory -i inventories/lab/hosts.yml --graph'
ansible-navigator run playbooks/check_policy.yml --syntax-check --eei "$runtime_ee" --dc false
ansible-navigator run tests/banner.yml -i tests/inventory.yml --eei "$runtime_ee" --dc false
ansible-navigator run tests/report.yml -i tests/inventory.yml --eei "$runtime_ee" --dc false
ansible-navigator run tests/check_mode.yml -i tests/inventory.yml --check --eei "$runtime_ee" --dc false
```

Navigator confirmed Ansible Core 2.16.19 and Python 3.12.13 inside that x86_64 EE.
The inventory graph and syntax checks for all four entry-point playbooks passed.
The check-mode test uses the real CLI flag because a task-level override does not
set Ansible's global `ansible_check_mode` flag. It creates and removes only its
disposable fixture with `check_mode: false`; the role runs in actual check mode.

## Results recorded on 2026-09-16 (America/Chicago)

The EE's UTC date during testing was 2026-09-17.

| Check | Result |
| --- | --- |
| YAML and Ansible lint through Navigator | Passed; production profile, zero lint findings |
| Inventory graph | Passed; three placeholder hosts in RHEL/Oracle groups |
| Entry-point playbook syntax | All four passed in the supported EE |
| Test playbook syntax | All three passed in the supported EE |
| Banner behavior | Passed; 192 tasks OK, zero unhandled failures |
| Actual check-mode behavior | Passed; predicted change with unchanged text and permissions |
| Report behavior | Passed; valid persisted JSON/Markdown and explicit missing-host evidence |

The banner test verifies baseline and exception idempotence, text and permission
drift, exact allowed exception wording, expiry blocking remediation without a
write, rejection of incomplete approval metadata, and restoration after exception
removal. Its two rescued failures are intentional negative tests that require the
expected rejection message. Fixture setup, drift injection, and cleanup account
for expected changes in test recaps; repeated remediation itself reports no change.

At the end of the first milestone, real guests and Controller behavior had not
been tested. The managed-target milestone below supersedes that guest limitation.
No full CIS or Tenable assessment was performed.

## Managed-target milestone — 2026-09-17 UTC

The user authenticated M5's privileged bootstrap in their terminal. All three
isolated KVM guests booted successfully. The Mac's Navigator supported EE can reach
them through M5 using console-verified SSH host keys. No development validation
was moved onto M5.

`playbooks/precheck_targets.yml` passed on all three guests: RHEL 9.8 (two),
Oracle Linux 9.8 (one), KVM identity, enforcing SELinux, completed cloud-init with
no errors, working Python/SSH, and effective root via sudo. Each host reported
`changed=0`, `unreachable=0`, and `failed=0`. The new playbook's supported-EE syntax
check passed; YAML lint and Ansible lint's production profile also passed through
the tooling EE.

Live results:

| Check | Verified result |
| --- | --- |
| Initial audit | Drift on all three hosts; zero configuration changes |
| Check-mode preview | One predicted banner update on each host; observed drift retained |
| First remediation | One change per host, followed by successful read-back verification |
| Second remediation | `changed=0`, `unreachable=0`, `failed=0` on all three hosts |
| Exception host | Exact alternate text and correct permissions; `approved_deviation` |
| Drift without opt-in | Expected rejection before any write, `changed=0` |
| Authorized drift on standard RHEL | Text and permissions both detected as drift |
| Drift remediation | One repair; subsequent audit `meets_baseline` |
| Final audit | Both standard hosts meet baseline; exception remains an approved deviation |
| Live report | JSON/Markdown fetched from the guest in a fresh EE; content and mode `0600` verified |
| Report regression test | Explicit and generated identifiers passed; zero failures |

The report role now resolves its run identifier once per invocation. This prevents
the timestamp default changing between directory creation and file writes.
Its regression test, supported-EE syntax checks, YAML lint, and Ansible production
lint all passed after the fix. No new collection dependency was added.

A separate EE retrieval also exposed the report play's explicit local connection
overriding delegated writes. The entry point now relies on implicit localhost,
allowing the report guest's SSH connection to apply. Persistence is verified by
fetching from the guest after the report-producing EE has exited.

The successful report is on `rhel_standard` under
`/var/tmp/auto-lab-reports/20260917T044928Z/`. A fresh Navigator invocation fetched
`report.md` and `results.json` into ignored `artifacts/live-evidence/` on the Mac.
The fetched JSON exactly matches the final audit results, and Markdown includes
all three hosts and the exception approval reference. Guest-side `stat` confirmed
the report is owned by `aapdemo` with mode `0600`.

Live job output is retained locally under ignored `artifacts/live-*.log`.
`artifacts/live-policy-evidence.json` contains the actual final audit results used
for the standalone report invocation; it was extracted from that run's structured
debug results. This explicitly supplied hand-off does not test AAP workflow
artifact propagation.

M5 reported 6.6 GiB available RAM after the live tests, with no swap-in/out in
the sampled intervals. All three guests remain running with autostart disabled.
This verifies the lightweight file-policy workload, not peak AAP or scanner load.

At this milestone, AAP Project synchronization, jobs, workflow artifact hand-off,
RBAC, and schedules were still untested. The Controller results below supersede
that limitation. RHEL subscription registration and package management are outside
this file-policy milestone. See [managed targets](managed-targets.md) for the
resource measurements and reproduction commands.

## Controller milestone — 2026-09-17

The user's pushed commit `93605e91180e8eca0b690dc386e7ffc98a36ac43` was verified
against GitHub and synchronized as Project 7. Inventory source 8 imported the
three guests and their policy variables into inventory 2. All demo job templates
select EE 6, pinned to the same registry manifest digest used for external tests.
Bootstrap ran through Navigator on the Mac using certified Controller/platform
collections; TLS verification remained enabled using the existing AAP CA.

| Check | Observed result |
| --- | --- |
| New bootstrap syntax | Passed in the supported EE |
| YAML and production Ansible lint | Passed through Navigator; 49 files, zero findings |
| Controller pre-check job 11 | All three guests passed; zero changes |
| Wrong host key, temporary job 15 | Failed with SSH host-key rejection; test objects removed |
| Audit workflow 20 | Pre-check, check 22, report 23 succeeded |
| Drift seed job 24 | Deliberate text/permission drift on standard RHEL only |
| Approved workflow 25 | Remediation job 29 repaired standard RHEL once; others unchanged |
| Repeat approved workflow 32 | Remediation job 36 changed zero items on all three guests |
| Exception treatment | RHEL exception remained `approved_deviation`; standards met baseline |
| Operator restrictions | HTTP 403 for direct remediation, drift injection, approval, Project and inventory edits |
| Approver restriction | HTTP 403 for direct remediation; workflow approval succeeded |
| Survey validation | Out-of-range readiness timeout rejected with HTTP 400 |
| Rejected approval, workflow 39 | Remediate, verify, and report nodes never launched |
| Expired approval, workflow 43 | Same stop behavior; temporary 15-second timeout restored to 600 |
| Workflow evidence | Report inputs exactly matched the final check's artifacts and job/revision IDs |
| Report persistence | Fresh Mac EE fetched report 38 from the guest; JSON matched verification job 37 |
| Report permissions | Both files owned by `aapdemo`, mode `0600` |
| Schedule 5 | Daily 14:00 UTC rule configured and verified disabled; scheduler firing not tested |
| Repeat Controller bootstrap | `ok=20`, `changed=1`, zero failures; only explicit inventory sync changed |

The report is retained at `rhel_standard:/var/tmp/auto-lab-reports/38/`.
Local copies are in ignored `artifacts/controller-evidence/`. Nonsecret API test
results are in `artifacts/controller-validation.json`; normal AAP job history also
retains the corresponding runs. Expected negative-test jobs remain visible as
failed jobs and do not indicate failing platform services.

The temporary non-admin verification accounts and their tokens were removed after
RBAC testing. Real user membership remains an administrator task. Configuration
resources were unchanged on the final repeat bootstrap; the inventory-source
update task reports a change because it deliberately launches a synchronization.
The temporary administrator setup token was also revoked and confirmed rejected;
private token/key staging files were removed from the Mac. The Controller guest
Machine credential remains available for normal job execution.

Two configuration issues were resolved before the passing runs: the installed
Controller collection requires approval-template creation and node associations
in separate calls; the report template must leave its host limit empty because
the play selects implicit localhost and delegates writes to the report guest.
No change to the pushed managed-host runtime code was needed.

M5 had about 5.2 GiB available RAM during these tests. The two sampled subsequent
`vmstat` intervals showed no swap-in/out, although allocated swap was about
561 MiB. These results cover the small file-policy demo, not scanner capacity.

Recurring execution, report retention, external notifications, actual human team
membership, scanner integration, and full CIS coverage are not established by
this milestone. The daily schedule remains disabled.

## Oracle retirement — 2026-10-23

At the user's request, the demo now contains only `rhel_standard` and
`rhel_exception`. Historical three-host results above remain unchanged.

The native removal script checked the Oracle domain UUID, dedicated disk/seed
paths, lack of shared attachments or snapshots, and exact DHCP reservation before
mutation. The user authenticated sudo and applied it on M5. Subsequent read-only
inspection verified that the domain, QCOW2 disk, seed ISO, and live reservation
were absent and both RHEL domains remained running. The script also removed the
persistent reservation, as confirmed by its successful output. Local and remote
bootstrap target lists exclude the retired guest; source images were preserved.

TLS-verified AAP API calls removed `oracle_standard` and the empty `oracle_linux`
group from inventory 2. Report template 12 now expects exactly the two RHEL hosts.
API reads verified both changes. The Git inventory, Controller configuration, and
current documentation were updated locally; no Git push or Project revision
advance was performed. Do not synchronize the earlier three-host Git revision.

External validation used the same explicit runtime image ID and tooling digest
documented above, through Navigator on the Mac:

| Check | Result |
| --- | --- |
| YAML and production Ansible lint | Passed; 48 files processed, zero findings |
| Inventory graph | Exactly the two RHEL hosts under `demo_targets` |
| Playbook syntax | All six entry points passed in the supported EE |
| Existing report regression | Passed; 21 tasks OK, zero failures |
| Live AAP inventory and report configuration | Verified by API reads |
| New Controller audit | Not verified: launch returned HTTP 403; diagnostic retry failed with no route to host |

The initial Navigator attempts could not access the stopped external Podman VM.
Starting that VM and running validation in one session resolved the issue; no
replacement image was pulled and no development validation ran on M5. No new
managed-host remediation or idempotence run was needed for this inventory-only
scope reduction. Earlier remediation results are historical, not a new test pass.

## Git revision advancement — 2026-10-23

The user explicitly authorized pushing the changes, overriding the standing
user-only push agreement for this work. Commit
`225a3c5b0621a542ce45b31c754cd88421b4ebbe` was pushed to `origin/main`.
The user then authorized advancing the live AAP Project and synchronizing its
inventory. TLS-verified API calls changed Project 7's pin to that commit.
Project update 65 succeeded, and both `scm_branch` and `scm_revision` matched it.
`controller/demo.yml` now records the same pin for future configuration runs.

Inventory update 66 parsed the Git YAML at that revision but ended in `error`:
`job_explanation: Subscription has expired!`, with `license_error: true`.
No subscription changes or licensing bypasses were attempted. The inventory
remains exactly `rhel_standard` and `rhel_exception`, with only `demo_targets`
and `rhel` groups; report template 12 still expects the same two hosts.
Renew the subscription and retry the inventory update to complete synchronization.

Navigator checks for the changed pin passed on the Mac: YAML lint, Ansible lint
production profile for the Controller playbook/role (five files, zero findings),
and Controller playbook syntax in the explicitly selected supported runtime EE.
The same tooling digest and runtime image ID documented above were used.
The external Podman validation VM was stopped afterward. This is a Project sync
pass and configuration validation, not a successful inventory import or policy job.
