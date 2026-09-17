---
name: server-info
description: >-
  Ground work involving the M5 home-lab server, its AAP deployment,
  execution environments, and managed-device capacity in verified host facts
  and the user's operating constraints. Use before planning or changing
  infrastructure on M5 or selecting the runtime for external development.
---

# Server info

Draft for user review. This records established operating agreements and a dated
host snapshot; it does not approve new infrastructure or resume earlier work.

Read [the server reference](references/m5.md) before making decisions that depend
on M5's resources, network, services, images, or execution environment. Refresh
only the facts relevant to the current task, and distinguish observations,
inferences, recommendations, and unverified items in reports.

## Keep the lab grounded

- M5 hosts the existing AAP platform and is intended to support managed lab
  devices too. Treat its running platform as infrastructure to preserve, not
  an implicit target for configuration, patching, or reboot demonstrations.
- Development, editing, linting, and Navigator validation happen only on an
  external device. M5 hosts AAP and managed lab targets; do not set up a
  development VM, checkout, or development-validation workspace there.
  A separate development VM is not a prerequisite: use suitable tooling on
  the external device. Running Controller jobs on M5 remains the intended
  deployment/execution workflow.
- Prefer the existing working setup when it meets the requested outcome.
  Explain a concrete need and the resource cost before proposing another VM,
  service, runtime image, or development environment. Do not turn a proposed
  improvement into an installation task without user authorization.
- Check current available memory, swap activity, storage, and running workloads
  before allocating resources. A point-in-time memory reading is not a VM
  budget; no reserved-memory policy or standard guest size has been agreed.
- Ask a focused question when target identity, resource allocation, or a
  material architectural choice cannot be resolved from the user's request
  and current evidence. Continue independent read-only work where useful.

## Preserve the established workflow

- The user alone pushes to GitHub. Never push on their behalf. AAP synchronizes
  the Git-backed Project from that repository. Do not substitute direct uploads
  into Controller's project directory or developer working copies on M5.
- Validate new or changed automation through `ansible-navigator` with an
  explicitly selected EE. Host-installed Ansible passing a check is not
  evidence that the EE passes it.
- For runtime tests, use the intended Controller EE and record its resolved
  digest. Inspect project collection overrides and the selected Job Template
  where relevant; a Controller default is not proof of what a particular job
  uses. Do not silently pull a newer `latest` image while reproducing a run.
- Lint tooling and the runtime EE can be separate. First check whether a
  suitable existing tooling image is available; do not assume a custom EE is
  required. Report missing tools instead of bypassing Navigator or claiming
  unperformed checks passed.
- An EE-local ping verifies that Ansible runs inside the container. It does
  not establish SSH access to a managed host, its readiness, or successful
  Controller execution. Label each validation result with its actual scope.
- This skill is context, not inventory. When implementing automation, put
  environment values in inventory or appropriate runtime inputs rather than
  copying host addresses and usernames into reusable role logic.

## Inspect without changing the platform

Use the SSH identity in the reference and preserve SSH host-key verification.
Prefer targeted reads: OS information, `free -h`, `df -h`, Podman lists and
selected image fields, and read-only libvirt queries. Try
`virsh --readonly --connect qemu:///system` for discovery before requesting
privileged management access. List both running and stopped objects when the
task depends on their absence; distinguish user and root container storage.

Do not export raw container environments, registry auth files, installer
inventories, Controller credential records, private keys, or whole configuration
trees into this skill. Retain only nonsecret facts needed for future decisions.
Credentials supplied during a session must never become persistent skill data.

Run development validation through Navigator on the external device, using a
scoped project or temporary directory for its mounts and artifacts. If that
external device lacks Navigator or a container runtime, report the prerequisite;
do not move development validation onto M5 to work around it. Existing tools
on M5 do not override this placement constraint. Read-only server discovery is
still appropriate when needed. Do not change packages, services, networking,
libvirt objects, image tags, or Controller settings to resolve a documentation-only
inspection problem.

After an interruption, inspect current state before retrying a mutation. A
prepared cloud-init file is not a created VM; a QCOW2 file is not a container
image; an EE reference in Controller is not proof of a locally cached image.

## Maintain the reference

Date new observations and identify how they were obtained. Record failures as
unknowns, not absence. Keep volatile resource readings and immutable image
identifiers separate from user decisions. Update only facts actually checked;
do not replace the snapshot with a transcript or mark the draft approved without
the user's review.
