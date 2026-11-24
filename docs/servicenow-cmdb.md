# ServiceNow CMDB inventory demonstration

ServiceNow's CMDB is the inventory source of truth for the two demo guests.
AAP reads hosts from the CMDB, scans their facts, and renders a report that
shows whether each CMDB record still matches the real host. Every connection
goes from AAP out to ServiceNow, so a free ServiceNow developer instance works
and nothing on M5 is exposed to the internet.

## What it adds

| Piece | File | Purpose |
| --- | --- | --- |
| CMDB inventory | `inventories/lab/now.yml` | `servicenow.itsm.now` inventory source |
| CMDB sync | `playbooks/sync_cmdb.yml`, `roles/cmdb_sync/` | Seed or correct CMDB records from facts |
| CMDB report | `playbooks/cmdb_report.yml`, `roles/cmdb_report/` | Facts vs CMDB HTML report |
| Controller objects | `roles/aap_demo/tasks/servicenow.yml` | Credential, inventory, two job templates |
| Overlay | `controller/servicenow-demo.yml` | Turns the Controller objects on |

The CMDB inventory returns the same host names (`rhel_standard`,
`rhel_exception`) and groups (`demo_targets`, `rhel`, `database_servers`) as
`inventories/lab/hosts.yml`, so the existing group_vars, host_vars and
exception records apply unchanged. Group membership comes from CMDB fields:

| Group | CMDB condition |
| --- | --- |
| `demo_targets` | Every record with `correlation_id` starting `auto-lab:` |
| `rhel` | Operating system contains `Red Hat` |
| `database_servers` | Category is `Database` |

`ansible_host` comes from the CMDB IP address. The guests' `192.168.122.x`
addresses are reachable only from M5, which is where Controller runs the jobs.

## One-time setup

1. Request a free personal developer instance at developer.servicenow.com. Note
   its URL (`https://devNNNNN.service-now.com`) and admin password. The instance
   is reclaimed after about ten days without activity; the sync job rebuilds the
   CMDB records in one run if that happens.
2. Push this change and note the commit SHA.
3. Put the commit SHA in `controller/servicenow-demo.yml`.
4. Add the ServiceNow connection to the private `/run/aap-session/auth.json`
   file you already mount for `configure_controller.yml` (never commit it). In
   that JSON file it is an `aap_demo_servicenow` object; shown here as YAML:

   ```yaml
   aap_demo_servicenow:
     instance: https://devNNNNN.service-now.com
     username: admin
     password: <developer instance password>
   ```

5. Run the bootstrap with both overlays. Put the exception overlay first so the
   ServiceNow overlay's revision wins:

   ```bash
   ANSIBLE_NAVIGATOR_CONFIG=/path/to/private/navigator.yml \
     ansible-navigator run playbooks/configure_controller.yml \
     -e @controller/exception-demo.yml -e @controller/servicenow-demo.yml \
     -e @/run/aap-session/auth.json --dc false
   ```

   The exception overlay still needs `aap_demo_snmp_communities` in the same
   private file, as described in [the exception runbook](exception-demo.md).

This creates:

- the `Auto Lab | ServiceNow ITSM` credential type (injects `SN_HOST`,
  `SN_USERNAME`, `SN_PASSWORD`) and a credential of that type;
- the `Auto Lab | ServiceNow CMDB` inventory, whose source syncs on every launch;
- `Auto Lab | Sync CMDB from facts - admin only` on the Git inventory;
- `Auto Lab | CMDB fact report` on the CMDB inventory, executable by operators.

## Demo sequence

1. **Empty CMDB.** Sync the `Auto Lab | ServiceNow CMDB` inventory. It returns
   no hosts, because nothing is registered yet.
2. **Seed.** Run `Sync CMDB from facts`. It scans both guests and creates two
   `cmdb_ci_linux_server` records. Show them in ServiceNow under
   *Configuration > Servers > Linux*. A second run reports no changes.
3. **CMDB as inventory.** Sync the CMDB inventory again. Both guests appear,
   already in `demo_targets`, `rhel` and (for `rhel_exception`) `database_servers`.
4. **Report.** Run `CMDB fact report`. Both hosts show "Matches the CMDB".
5. **Drift.** In ServiceNow, change `rhel_standard`'s OS version (for example to
   `9.0`). Run the report again: that field is flagged in red.
6. **Correct.** Run `Sync CMDB from facts`, then the report. Both match again.

The existing policy jobs can also be pointed at the CMDB inventory, because the
host names, groups and variables are the same.

## CVE counts in the CMDB

`playbooks/security_to_cmdb.yml` puts each host's vulnerability picture from Red
Hat Lightspeed into its CMDB record, so the security team sees patch level in
ServiceNow next to OS and version.

1. On localhost it creates any missing custom fields on `cmdb_ci_linux_server`
   (`roles/cmdb_sync/tasks/fields.yml`), so a reset developer instance is rebuilt
   by the same job.
2. On each host it runs `security_facts` (needs the Lightspeed credential), then
   `cmdb_sync` writes the counts. A host with no CVE counts fails instead of
   being recorded without them.

| CMDB field | Meaning | `security_facts_record` key |
| --- | --- | --- |
| `u_cve_critical` | Critical CVEs with a fix available | `fixable_critical` |
| `u_cve_important` | Important CVEs with a fix available | `fixable_important` |
| `u_cve_total` | All CVEs with a fix available | `fixable_total` |
| `u_cve_known_exploit` | CVEs with a known exploit | `known_exploit` |
| `u_cve_no_fix` | Critical or important CVEs without a fix | `no_fix_critical_important` |
| `u_last_package_change` | Date of the newest package install or update | `last_package_change_date` |
| `u_last_security_scan` | When Lightspeed last evaluated the host | `lightspeed_last_evaluation` |

Values change only when Lightspeed's data changes, so a repeat run against
unchanged hosts reports no changes.

Controller job template (created by hand for now):

- Name: `Auto Lab | Security facts to CMDB`
- Inventory: `Auto Lab | ServiceNow CMDB`, so the CMDB decides which hosts are scanned
- Playbook: `playbooks/security_to_cmdb.yml`
- Credentials: guest SSH, verified guest host keys, the ServiceNow credential
  (the job writes to ServiceNow), and the Red Hat Lightspeed credential that
  injects `LIGHTSPEED_CLIENT_ID` and `LIGHTSPEED_CLIENT_SECRET`

The ServiceNow account must be allowed to add dictionary fields (the developer
instance admin is). To see the values, add the fields to the Linux Server list or
form in ServiceNow (right-click the list header, *Configure > List Layout*).

## Report location

The report is saved on `rhel_standard` at
`/var/tmp/auto-lab-reports/<job id>/cmdb.html`, alongside the security dashboard.
If the report viewer from `security_report` is running, the job output prints its
link; use the same SSH tunnel shown in that job's output to open it from the Mac.

## Limits

- The CMDB records carry only the fields this demo compares. Discovery,
  relationships and other CI classes are out of scope.
- Category `Database` is a demo classification; no database is installed.
- The developer instance's admin account is used for simplicity. For anything
  beyond a lab, create a dedicated ServiceNow user with only CMDB read/write roles.
