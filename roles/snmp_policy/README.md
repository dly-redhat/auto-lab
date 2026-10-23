# SNMP policy

Audit or enforce a small, explicitly managed Net-SNMP configuration on RHEL 9.
The demo uses SNMPv2c community strings to match the customer example; it does not
implement SNMPv3. Default listening and source addresses are loopback only.

RHEL System Roles were checked against the
[documented role catalog](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/automating_system_administration_by_using_rhel_system_roles/intro-to-rhel-system-roles_automating-system-administration-by-using-rhel-system-roles);
no SNMP subsystem role was identified. Built-in package, template, service facts,
stat, slurp, and systemd modules provide this capability without a new collection.

| Input | Default | Meaning |
| --- | --- | --- |
| `snmp_policy_operation` | `audit` | `audit` or `remediate` |
| `snmp_policy_baseline_enabled` | `true` | Standard service requirement |
| `snmp_policy_enabled` | Baseline | Effective approved service requirement |
| `snmp_policy_baseline_community_ref` | `standard` | Baseline secret-map key |
| `snmp_policy_community_ref` | Baseline reference | Effective secret-map key |
| `snmp_policy_communities` | `{}` | Private mapping of references to actual strings |
| `snmp_policy_manage_service` / `snmp_policy_manage_community` | `true` | Enforcement permissions resolved by the exception role |
| `snmp_policy_package` / `snmp_policy_service` | `net-snmp` / `snmpd.service` | Managed package and unit |
| `snmp_policy_path` | `/etc/snmp/snmpd.conf` | Entire managed configuration file |
| `snmp_policy_owner` / `snmp_policy_group` / `snmp_policy_mode` | `root` / `root` / `0600` | Configuration ownership and mode |
| `snmp_policy_listen_address` / `snmp_policy_port` | `127.0.0.1` / `161` | Local demo listener |
| `snmp_policy_source` | `127.0.0.1` | Allowed polling source |

The approved strings must contain 8–64 letters, digits, underscores, or hyphens.
Supply them through a Controller credential, Vault, or a private EE-mounted input
outside the repository. Secret reads, rendering, and writes use `no_log`; template
diffs are disabled. Reports contain match flags and credential reference names only.

An enabled policy requires a usable package repository if `net-snmp` is absent.
A disabled policy does not install it; an absent service meets the disabled
requirement when service facts are available. Unavailable service facts are
unknown, not proof that the unit is absent, and suppress SNMP enforcement.
The role does not register RHEL subscriptions or create package repositories.

The role manages the complete named file, including a read-only system MIB view,
and verifies configuration matches plus service running/boot state afterward.
Review existing SNMP deployment, unit overrides, included/persistent files, and
monitoring dependencies before production use; this is not exhaustive process,
network, or SNMP protocol validation.

Configuration changes notify a restart handler. Inputs are constrained before
rendering. Net-SNMP's documented `-H` lists directives; it is not presented as a
configuration syntax-validation command. Actual daemon activation and protocol
testing remain required on a package-enabled RHEL target. Reference:
[snmpd](https://www.net-snmp.org/docs/man/snmpd.html) and
[snmpd.conf](https://www.net-snmp.org/docs/man/snmpd.conf.html).

In check mode the role observes and reports desired-vs-actual differences without
installing packages, writing configuration, or changing services. It does not
claim a post-remediation pass. `snmp_policy_before`, `snmp_policy_observed`, and
`snmp_policy_service_evidence` are its nonsecret evidence outputs.
