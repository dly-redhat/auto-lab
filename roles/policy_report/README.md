# Policy evidence report

Accepts `policy_report_results` (defaults to AAP's inherited `compliance_results`),
`policy_report_expected_hosts` (defaults to all demo targets), and a required
`policy_report_host` present in inventory. Writes `results.json` and `report.md`
under `policy_report_directory/policy_report_run_id` on that host. Defaults:
`/var/tmp/auto-lab-reports`, and the AAP job ID or a UTC timestamp.
The role resolves that identifier once so every task uses the same directory,
including standalone executions that rely on the timestamp default.

The connection account must be able to create the private directory. No web
server, sudo, external collection, or database is needed. Files are mode `0600`
inside a `0700` directory. Retrieve them using the account's approved SSH access.
Choose retention and cleanup before sustained scheduled use; no automatic cleanup
is performed by this milestone. A target's normal temporary-file cleanup may
eventually remove `/var/tmp` evidence, so configure a retained path for long-term
use. A missing expected host is explicitly shown as NO EVIDENCE.

Run via `playbooks/report_policy.yml` as the final workflow node. Standalone local
runs must supply a saved results map; separate Navigator invocations do not inherit
`set_stats` automatically. Reports are policy evidence, not full CIS assessments.

The entry-point play uses Ansible's implicit localhost connection. Do not set
`connection: local` at play level: delegated writes would inherit it and could
land inside the disposable EE. Report hosts must use their actual inventory
connection. Verify persistence by fetching the files in a separate EE invocation.
