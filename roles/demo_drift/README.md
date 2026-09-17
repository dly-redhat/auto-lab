# Demonstration drift

Only for isolated, disposable demo targets. `demo_drift_allowed` defaults to
`false` and must be explicitly set to boolean `true`. The role requires a member
of `demo_targets` running RHEL/Oracle Linux 9 and restricts the path to `/etc/issue`.
It replaces the text with `demo_drift_text` and sets mode `0600`, producing a
detectable text/permissions deviation. `playbooks/seed_demo_drift.yml` is its entry
point. Keep its AAP template available to the demo administrator only.

Restore the correct value using `playbooks/remediate_policy.yml`; an active wording
exception restores its approved alternate value. No dependency or restart is needed.
