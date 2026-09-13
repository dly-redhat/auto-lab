# AI Agent Instructions

## Purpose
This repository is a home-lab demonstration of Red Hat Ansible Automation Platform (AAP).
The repository should demonstrate production-minded Ansible development practices while
remaining small, understandable, and easy to demo.

## Primary Goals
1. Demonstrate idempotent automation.
2. Organize reusable automation as roles.
3. Keep environment-specific data out of playbook logic.
4. Make playbooks safe to run repeatedly.
5. Make automation compatible with AAP Automation Controller.
6. Make all generated code pass `ansible-lint` and syntax checks.
7. Prefer built-in or supported collection modules over `shell` or `command`.
8. Keep secrets out of Git.

## Repository Expectations
Use this general layout:

```text
.
├── README.md
├── AGENTS.md
├── ARCHITECTURE.md
├── ANSIBLE_STANDARDS.md
├── SECURITY.md
├── TESTING.md
├── ansible.cfg
├── requirements.yml
├── inventories/
│   └── lab/
│       ├── hosts.yml
│       ├── group_vars/
│       └── host_vars/
├── playbooks/
├── roles/
├── templates/
├── files/
├── tests/
├── .ansible-lint
├── .yamllint
└── .github/
    └── workflows/
```

## Rules for Generated Ansible
- Use YAML inventory.
- Use Fully Qualified Collection Names (FQCN), for example:
  `ansible.builtin.package`, `ansible.builtin.service`, and
  `ansible.posix.firewalld`.
- Every play, task, block, and handler must have a descriptive `name`.
- Explicitly define desired state when a module supports it.
- Prefer modules over `ansible.builtin.shell` or `ansible.builtin.command`.
- If shell/command is unavoidable:
  - explain why in a comment;
  - set `changed_when` when appropriate;
  - set `failed_when` when appropriate;
  - make execution idempotent where possible.
- Use handlers for restart/reload operations triggered by configuration changes.
- Use variables instead of hard-coded hostnames, users, paths, ports, package names,
  and environment-specific values.
- Put role defaults in `roles/<role>/defaults/main.yml`.
- Put values that should not normally be overridden in `roles/<role>/vars/main.yml`
  only when necessary.
- Avoid excessive use of role `vars`; prefer defaults and inventory variables.
- Use templates for configuration files containing variables.
- Validate configuration before triggering a restart whenever the software supports it.
- Use `become: true` only where privilege escalation is required.
- Do not set `ignore_errors: true` unless there is a documented reason.
- Do not disable TLS certificate validation unless the lab scenario explicitly requires it.
- Avoid interactive features such as `vars_prompt`; AAP Controller jobs must run unattended.
- Never embed passwords, tokens, private keys, vault passwords, or credentials in Git.

## Playbook Design
Playbooks should be thin orchestration layers.

Good:
```yaml
---
- name: Configure web servers
  hosts: web
  become: true

  roles:
    - role: web_server
```

Avoid placing dozens of implementation tasks directly in a top-level playbook.

## Role Design
Each role should represent one clear capability, such as:
- `baseline`
- `web_server`
- `firewall`
- `users`
- `patching`
- `compliance`
- `motd`

Roles should be independently reusable when practical.

## AAP Compatibility
Code must work when launched from Automation Controller:
- no interactive prompts;
- no dependency on a developer's local filesystem;
- dependencies declared in `requirements.yml`;
- paths derived from the repository/playbook rather than assumed working directories;
- credentials supplied through Controller credential objects, environment variables,
  Ansible Vault, or another approved secret mechanism;
- inventories should be easy to migrate from static lab inventory to dynamic inventory.

## Change Strategy
When implementing a feature:
1. Inspect existing repo structure and conventions.
2. Propose the smallest logical change.
3. Reuse an existing role if responsibility already exists.
4. Add a new role only for a distinct reusable capability.
5. Update documentation when behavior or required variables change.
6. Add or update tests.
7. Run lint and syntax validation.
8. Report exactly what changed and how to test it.

## Definition of Done
A change is not complete until:
- YAML is valid;
- `ansible-lint` passes;
- `yamllint` passes;
- `ansible-playbook --syntax-check` passes;
- the playbook is safe to run twice;
- secrets are absent from tracked files;
- variable names and expected inputs are documented;
- README/demo instructions are updated if user-facing behavior changed.
