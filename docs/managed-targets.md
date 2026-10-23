# Managed demo targets

Current scope: two RHEL guests, one standard and one with an approved policy
exception. On October 23, 2026, the Oracle guest was retired at the user's request:
its domain, dedicated QCOW2 disk, seed ISO, and live/persistent DHCP reservation
were removed. Both RHEL domains remained running. Source images were preserved.
The local and M5 bootstrap target lists now exclude Oracle to prevent recreation.

External Navigator and Controller validation for the original three-host demo
is preserved as historical evidence in [validation](validation.md). Those older
reports legitimately contain Oracle; current inventories and new reports do not.

## Capacity and placement

The September 16/17 inspection found no system or user-session libvirt guests,
9.5 GiB available RAM, no swap-in/out during the sampled intervals, and 825 GiB
free on `/home`. This is a snapshot, not reserved capacity.

| Inventory name | Libvirt domain | OS | Verified DHCP address |
| --- | --- | --- | --- |
| `rhel_standard` | `aap-demo-rhel-standard` | RHEL 9.8 | `192.168.122.101` |
| `rhel_exception` | `aap-demo-rhel-exception` | RHEL 9.8 | `192.168.122.102` |

Each guest uses 2 vCPUs, 2 GiB RAM, and a 40 GiB sparse standalone disk. This gives
4 GiB total configured guest RAM and up to 80 GiB of logical disk capacity.
The bootstrap checks available memory before each new guest, retaining a proposed
3 GiB minimum margin. That margin is a guard, not a guarantee against AAP workload
spikes. Recheck memory under real Controller load before declaring demo capacity.
At the original three-guest provisioning, M5 reported 6.5 GiB available RAM and
no swap-in/out in the sampled intervals. Disk image sizes were approximately 1.4 GiB per RHEL
guest and 809 MiB for Oracle. Libvirt confirmed persistent guests with 2 GiB RAM,
2 vCPUs, enforcing sVirt isolation, and autostart disabled for each.

Guests have autostart disabled. They use the existing `default` NAT network and
DHCP reservations; M5's physical network and AAP services are not reconfigured.
The Mac reaches guests with SSH ProxyJump through M5. AAP's direct guest-network
reachability was verified separately in the Controller milestone.

Guest disks live in `/home/aap-demo-vms`, avoiding the existing incorrectly labeled
user-home storage path. The bootstrap applies a persistent `virt_image_t` mapping
to that dedicated directory. Source images remain unchanged; no backing-file
dependency is introduced. SELinux stays enforcing.

## Image provenance

The existing RHEL source is `/home/diem/rhel-9.8-x86_64-kvm.qcow2`. Its measured
SHA-256 is `b99091f1b4489111004d449398d9cc6aa024cb48b02c72fa99e6ca1fc48a7e4e`.
This records the supplied file's identity; a Red Hat published checksum was not
independently retrieved during this milestone. Both QCOW2 sources passed
`qemu-img check`.

The retained source for the retired Oracle guest, `OL9U8_x86_64-kvm-b293.qcow2`,
was downloaded directly from the
[official image catalog](https://yum.oracle.com/oracle-linux-templates.html).
Its verified published SHA-256 is
`b12103391327abee8090686759c0d62dac9a7af2bf0f45fdf6b0d085a0fbb52b`.
The [image README](https://yum.oracle.com/templates/OracleLinux/OL9/u8/x86_64/README_OL9U8.txt)
lists cloud-init and the minimal guest packages. No scanner or hardening framework
is required for this banner-policy milestone.

## Bootstrap and authentication

The concrete, environment-specific bundle is in ignored
`artifacts/m5-provision/` on the Mac and
`/home/diem/aap-demo-bootstrap/bundle/` on M5. It contains a reviewed Bash bootstrap,
settings, two active RHEL host records, and cloud-init data with public SSH keys only.
This is a native hypervisor bootstrap, not an Ansible development checkout on M5.
It uses existing `virt-install`, `virsh`, `qemu-img`, and `xorriso`; the repository
does not acquire a libvirt community collection for this one-time setup.

Navigator validated Bash syntax and the generated YAML externally. The bootstrap's
read-only `--check` verified source checksums, QCOW2 integrity, the active NAT
network, and absence of conflicting reservations. The user then ran the privileged
creation successfully from their own terminal.

In the user's terminal:

```bash
ssh -t diem@192.168.86.44 \
  'sudo bash /home/diem/aap-demo-bootstrap/bundle/provision.sh --apply'
```

Enter the sudo password in that terminal only. SSH key access is already working,
but the inspected account cannot manage system libvirt without authentication.
No blanket passwordless-sudo or polkit grant is needed on M5.

The script preserves existing matching domains, refuses unrelated disks and
conflicting reservations, and stops on errors. It does not remove failed guests or
disks automatically. Inspect a partial failure before continuing. Source images
and any already-created guests are retained.

Cloud-init creates the guest-only `aapdemo` account with the Mac's existing public
key and the existing M5 demo-fleet public key. Password login is disabled and new
host keys are generated. Passwordless sudo is scoped to this account on these
isolated demo guests; it provides root-equivalent automation access, so protect
the corresponding private keys and limit AAP credential use with RBAC. No private
keys are stored in the repository or cloud-init data. RHEL subscription registration
and package updating are deferred; they are not required to test the existing file
policy, but are required before later RHEL package/patch demonstrations.

## Establish trust and validate externally

1. Read each guest's public host keys from the hypervisor-captured serial output
   under `/home/aap-demo-vms/hostkeys/`. They were verified through the already-trusted
   M5 SSH connection and placed in ignored `artifacts/m5_guest_known_hosts` on the
   Mac. The external inventory explicitly selects this guest trust file.
   Do not substitute `StrictHostKeyChecking=no` or unverified `ssh-keyscan` output.
2. Confirm cloud-init completed and the account can connect through M5.
3. Use the ignored `inventories/local/m5.yml` overlay alongside the lab inventory.
   It supplies the connection user, trust file, and Mac-only ProxyJump setting
   while inheriting the verified addresses and Git policy/exception data.
   Navigator's existing SSH-key mounts worked on this Mac; no private key was
   copied into the repository or baked into an image.
4. Run the pre-check and policy sequence through the supported EE:

```bash
runtime_ee=sha256:d0ec1ac135c1eb831bb6c5fa6784e9ebebc407bec6141823b89c665b2a65f511
ansible-navigator run playbooks/precheck_targets.yml \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee" --dc false
ansible-navigator run playbooks/check_policy.yml \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee" --dc false
ansible-navigator run playbooks/remediate_policy.yml --check --diff \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee" --dc false
ansible-navigator run playbooks/remediate_policy.yml \
  -i inventories/lab/hosts.yml -i inventories/local/m5.yml --eei "$runtime_ee" --dc false
```

Repeat remediation and require zero unexpected changes on every guest. Then test
the opt-in drift job on one standard guest, detect and remediate that drift, and
check the standard RHEL host and the exception RHEL host. Oracle is outside the
current demo scope.

The pre-check role uses only built-in modules. It verifies the expected OS, KVM
guest identity, enforcing SELinux, SSH/Python execution, cloud-init results, and
effective sudo access. It intentionally rejects the physical M5 host.

The completed live sequence is recorded in [validation](validation.md). Its report
is retained on `rhel_standard` at
`/var/tmp/auto-lab-reports/20260917T044928Z/`; verified copies are in ignored
`artifacts/live-evidence/` on the Mac. Report files were retrieved in a new EE
invocation, confirming that they survive the producing container's teardown.

The original readiness verification passed for all three guests with zero changes.
Verified addresses replaced the example inventory placeholders. The user reviews and
pushes; AAP then synchronizes from Git. Mac-only jump-host configuration must not
become a Controller dependency.

Verified ED25519 fingerprints:

| Guest | SHA-256 fingerprint |
| --- | --- |
| `rhel_standard` | `VoexpsrNYMfRUQBpUb+33RSSZ/GCfB/w2FpzlBu/LwM` |
| `rhel_exception` | `Im/enIXjC97iQolFeOcGM/CkycoeBwTXGc5fFNUpZrg` |
