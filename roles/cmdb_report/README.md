# CMDB report

Compares each host's ServiceNow CMDB record with what the host reports in its
gathered facts, and renders a one-page HTML report. It shows whether the CMDB can
be trusted as the inventory source of truth.

Run it with the CMDB inventory (`inventories/lab/now.yml`) so the CMDB values
arrive as host variables. `tasks/scan.yml` runs on each host after fact gathering;
`tasks/main.yml` runs on localhost and renders the report on `cmdb_report_host`.

Compared fields: hostname, FQDN, IP address and OS version. The report also lists
kernel, vCPUs, memory, uptime and SELinux mode from the facts. A host the CMDB lists
but that returns no facts is reported as not scanned, never as accurate.

Supported platforms: the RHEL 9 demo guests. No collections are needed at run
time; the inventory sync needs `servicenow.itsm`.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `cmdb_report_title` | `CMDB accuracy report` | Report heading |
| `cmdb_report_hosts` | `groups['demo_targets']` | Hosts expected in the report |
| `cmdb_report_host` | `rhel_standard` | Inventory host that stores the report |
| `cmdb_report_directory` | `/var/tmp/auto-lab-reports` | Report root on that host |
| `cmdb_report_file` | `cmdb.html` | File name within the run directory |
| `cmdb_report_run_id` | Controller job ID or UTC time | Run directory name |
| `cmdb_report_web_port` | `8080` | Port of the existing report viewer, for the printed link |

The report is written to `<directory>/<run_id>/cmdb.html`, the same tree the
security dashboard publishes. If that viewer is running, the job prints its link.

## Example

See `playbooks/cmdb_report.yml`.
