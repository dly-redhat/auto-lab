# Managed target pre-check

Read-only readiness checks for the managed Linux 9 KVM demo guests. The current
demo inventory contains two RHEL guests.
The role verifies distribution, virtualization, enforcing SELinux, Python over
SSH, completed cloud-init without errors, and effective root access through sudo.
It has no collection dependencies and makes no configuration changes.

`target_precheck_distribution` is required (`RedHat` or `OracleLinux`), supplied
by the OS inventory group. `target_precheck_major_version` defaults to `'9'`;
`target_precheck_cloud_init_timeout` defaults to 180 seconds. These are trusted
inventory settings, not operator survey inputs.

Run `playbooks/precheck_targets.yml` through Navigator after verifying host keys.
In check mode the waiting task is skipped, but existing first-boot evidence must
still be readable. Failure stops the play before proceeding to another guest.
M5 itself is deliberately excluded by the OS and virtualization requirements.
