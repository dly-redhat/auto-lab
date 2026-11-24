# CMDB sync

Creates or updates one ServiceNow CMDB record per demo guest from its gathered
facts. Use it once to seed an empty CMDB from the Git inventory, then again
whenever the report shows a record has drifted from the host.

Each record is a `cmdb_ci_linux_server` named after the inventory host, with
`correlation_id` set to `auto-lab:<inventory_hostname>`. That prefix is how
`inventories/lab/now.yml` finds the demo's records and ignores the demo data
already present in a ServiceNow developer instance. Hosts in the
`database_servers` group are recorded with category `Database`, which the CMDB
inventory turns back into the same group so the existing exception policy applies.

Supported platforms: the RHEL 9 demo guests. The ServiceNow call runs on
localhost through `servicenow.itsm.configuration_item`.

## Requirements

- Collection `servicenow.itsm` (declared in `requirements.yml`).
- `SN_HOST`, `SN_USERNAME` and `SN_PASSWORD` in the environment. In Controller,
  attach the `Auto Lab | ServiceNow ITSM` credential; never put them in Git.
- Play-level fact gathering and an inventory that sets `ansible_host`.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `cmdb_sync_table` | `cmdb_ci_linux_server` | CMDB class to write |
| `cmdb_sync_correlation_prefix` | `auto-lab:` | Marks records owned by this demo |
| `cmdb_sync_database_group` | `database_servers` | Group recorded as category `Database` |
| `cmdb_sync_category_database` | `Database` | Category for that group |
| `cmdb_sync_category_default` | `Server` | Category for other hosts |
| `cmdb_sync_environment` | `development` | `development`, `production` or `test` |
| `cmdb_sync_short_description` | demo note | Description shown in ServiceNow |
| `cmdb_sync_security_fields` | seven CVE fields | Custom CMDB fields and their `security_facts_record` sources |
| `cmdb_sync_require_security` | `false` | Fail when CVE counts are missing instead of skipping them |

## CVE counts

When `security_facts` ran earlier in the same play, the role also writes the host's
CVE counts into the custom fields listed in `cmdb_sync_security_fields`.
`tasks/fields.yml` creates those fields on `cmdb_sync_table` if they are missing; run
it on localhost with the same ServiceNow credential. `playbooks/security_to_cmdb.yml`
does both. Values are written as strings so repeat runs compare cleanly.

## Example

```yaml
- name: Register the demo guests in the ServiceNow CMDB from their facts
  hosts: demo_targets
  gather_facts: true
  roles:
    - role: cmdb_sync
```

A second run against unchanged hosts reports no changes; the module only
updates fields whose values differ.
