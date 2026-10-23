# Controller demo configuration

Run `playbooks/configure_controller.yml` externally through Navigator with the
certified collections pinned in `controller/requirements.yml`. The play reads
reviewable environment data from `controller/demo.yml`. It does not push Git or
copy working automation into Controller's project directory.

Supply `aap_demo_token` using a private extra-vars file mounted in the EE. Defaults
expect the CA at `/run/aap-session/ca.crt` and the existing guest private key at
`/run/aap-session/fleet_key`; override those path variables when needed. Keep the
mount outside Git and remove the temporary token after configuration. The
console-verified public host keys default to `artifacts/m5_guest_known_hosts`.

The role creates an isolated organization, two teams, pinned EE and Git Project,
SCM inventory, credentials, five job templates, two workflows, and a disabled
daily audit schedule. It intentionally grants operators no direct remediation,
drift-injection, inventory-edit, project-edit, or credential-use permissions.
Approvers receive only the remediation workflow's approval role. Team membership
must be managed separately for actual users.

The readiness survey accepts a bounded integer wait timeout. Policy wording,
exceptions, target addresses, and credentials are trusted configuration. Only the
administrator-only drift template prompts for arbitrary extra vars, with its
opt-in still false by default.

Project and inventory synchronization are explicit operations and may report
changes on repeat bootstrap runs. Resource creation and configuration should be
idempotent; machine credentials use `update_secrets: false` to avoid unnecessary
private-key replacement. Rotate that key through an intentional credential change.

Runtime approval authorizes execution, not new policy. Workflow failure, rejection,
and timeout have no edge to remediation. The daily schedule remains disabled until
report retention and ongoing operation are agreed.
