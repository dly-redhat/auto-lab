# Console banner policy

Assess or enforce one console warning banner on RHEL 9 / Oracle Linux 9.
No Galaxy dependencies. Integration with real RHEL/Oracle guests must be verified
separately from the EE-local fixtures.

| Input | Default | Meaning |
| --- | --- | --- |
| `compliance_banner_operation` | `audit` | `audit` or `remediate` |
| `compliance_banner_profile` | `linux_demo` | Only the implemented demo profile is accepted |
| `compliance_banner_baseline_text` | Empty; required | Nonempty text ending in a newline |
| `compliance_banner_target_path` | `/etc/issue` | Absolute managed file path; trusted configuration only |
| `compliance_banner_owner` / `compliance_banner_group` | `root` | Required ownership |
| `compliance_banner_file_mode` | `0644` | Required quoted four-digit octal mode |
| `compliance_banner_become` | `true` | Escalate when needed for reads and for remediation writes |
| `compliance_banner_exception` | `{}` | Optional reviewed exception record |

An exception requires `control: console_login_banner`, the exact inventory
`host`, the `profile`, nonempty `reason`, `approved_by`, `approval_ref`, quoted
`expires: YYYY-MM-DD`, and newline-terminated `allowed_text`. Dates are evaluated
using the EE's UTC clock. That record approves alternate wording only; file
permissions and ownership remain enforced.

Example usage is in `playbooks/check_policy.yml` and `playbooks/remediate_policy.yml`.
Keep policy inputs in trusted inventory/Git. Only expose intended operator inputs
in AAP surveys; do not enable arbitrary extra variables or inventory editing for
operators, because Ansible extra vars can override role/inventory variables.

The role returns `compliance_banner_result` and publishes a host-keyed
`compliance_results` map using `ansible.builtin.set_stats` for workflow hand-off.
An approved deviation is distinct from meeting the baseline. The result includes
before and observed states, operation/check-mode context, date, and available AAP
job/revision identifiers. It does not contain actual file content outside the
approved policy text. Files over 64 KiB and nonregular paths are rejected.

Run `tests/banner.yml` inside the supported EE through Navigator to exercise
drift, idempotence, scoped exceptions, expiry, and invalid metadata. Run
`tests/check_mode.yml --check` separately to verify preview leaves actual file
contents and permissions unchanged.
