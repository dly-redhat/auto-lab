# Demonstration drift

Only for isolated, disposable demo targets. `demo_drift_allowed` defaults to
`false` and must be explicitly set to boolean `true`. The role requires a member
of `demo_targets` running RHEL/Oracle Linux 9 and restricts the path to `/etc/issue`.
It replaces the text with `demo_drift_text` and sets mode `0600`, producing a
detectable text/permissions deviation. `playbooks/seed_demo_drift.yml` is its entry
point. Keep its AAP template available to the demo administrator only.

Restore the correct value using `playbooks/remediate_policy.yml`; an active wording
exception restores its approved alternate value. No dependency or restart is needed.

For the exception demo, `demo_drift_control: snmp_community` selects SNMP drift
instead of the default `console_login_banner`. It requires RHEL 9, the existing
`/etc/snmp/snmpd.conf` regular file, and exactly the four-line loopback-only layout
created by `snmp_policy`. It replaces only the community with `public`, conceals
the previous secret, and restarts `snmpd.service` through a handler when changed.
The guarded defaults `demo_drift_snmp_path` and `demo_drift_snmp_service` cannot
select a different path or service. No network listener or firewall is opened.
The exception-mode Controller bootstrap selects this control for the admin-only
seed template. Restore it with `playbooks/remediate_exceptions.yml` or the approved
remediation workflow, then repeat and verify zero configuration changes.
