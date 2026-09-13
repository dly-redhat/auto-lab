# Ansible Development Standards

## YAML
- Start Ansible YAML files with `---`.
- Use 2-space indentation.
- Do not use tabs.
- Keep lines reasonably short.
- Use booleans as `true` and `false`.
- Use clear comments only where intent is not obvious.

## Naming
Every play and task must be named.

Good:
```yaml
- name: Ensure chronyd is installed
  ansible.builtin.package:
    name: chrony
    state: present
```

Bad:
```yaml
- package:
    name: chrony
```

## Fully Qualified Collection Names
Use FQCNs for modules and plugins.

Good:
```yaml
ansible.builtin.copy:
ansible.builtin.template:
ansible.builtin.service:
ansible.posix.firewalld:
```

## Idempotence
A second run against an already-compliant host should normally report no changes.

Prefer declarative modules:

```yaml
- name: Ensure httpd is installed
  ansible.builtin.package:
    name: httpd
    state: present
```

Avoid:

```yaml
- name: Install httpd
  ansible.builtin.shell: dnf install -y httpd
```

## Variables
Prefix role-specific variables with the role name when it improves clarity.

Example:
```yaml
web_server_port: 8080
web_server_document_root: /var/www/html
```

Prefer:
1. role defaults for safe defaults;
2. group vars for group/environment customization;
3. host vars only for truly host-specific differences;
4. Controller extra vars/surveys for intentional runtime input.

Do not hard-code:
- IP addresses;
- usernames;
- passwords;
- ports that should be configurable;
- environment-specific paths;
- hostnames.

## Handlers
Use handlers for restart/reload actions that only need to occur after a change.

```yaml
- name: Deploy httpd configuration
  ansible.builtin.template:
    src: httpd.conf.j2
    dest: /etc/httpd/conf/httpd.conf
    owner: root
    group: root
    mode: "0644"
  notify: Restart httpd
```

```yaml
# handlers/main.yml
---
- name: Restart httpd
  ansible.builtin.service:
    name: httpd
    state: restarted
```

## File Permissions
Always set explicit permissions when deploying sensitive or operational configuration
files.

Quote octal modes:
```yaml
mode: "0640"
```

## Packages and Services
State the desired state explicitly.

```yaml
- name: Ensure chronyd is enabled and running
  ansible.builtin.service:
    name: chronyd
    enabled: true
    state: started
```

## Shell and Command
Use `ansible.builtin.shell` only when shell features are required.
Use `ansible.builtin.command` if a module does not exist and shell features are unnecessary.

Before using either, verify there is no appropriate module.

Where needed, make command execution deterministic using:
- `creates`;
- `removes`;
- `changed_when`;
- `failed_when`.

## Privilege Escalation
Do not globally apply privilege escalation without reason.
Use `become: true` at the play/block/task level where root access is required.

## Error Handling
Avoid `ignore_errors: true`.

Prefer:
- `block` / `rescue` / `always`;
- explicit `failed_when`;
- validation before a disruptive operation.

## Safety
For disruptive operations consider:
- `serial`;
- `max_fail_percentage`;
- pre-checks;
- post-checks;
- explicit maintenance/reboot variables.

Example:
```yaml
- name: Patch RHEL systems
  hosts: rhel
  become: true
  serial: 25%
```

## Facts
Use gathered facts when they materially simplify OS-aware logic.
Do not repeatedly call fact gathering tasks when normal play-level facts are sufficient.

Use facts for conditions such as:
```yaml
when: ansible_facts["os_family"] == "RedHat"
```

## Tags
Use tags for meaningful operator workflows, not every individual task.

Examples:
- `baseline`
- `packages`
- `firewall`
- `configuration`
- `validation`

## Role Structure
Typical reusable role:

```text
roles/example/
├── README.md
├── defaults/
│   └── main.yml
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   └── main.yml
├── templates/
└── files/
```

Do not create empty directories solely for appearance.

## Controller Compatibility
Do not use `vars_prompt`.
AAP jobs must be non-interactive.
Use:
- surveys;
- extra vars;
- credentials;
- inventory variables.

## Documentation
Every role should document:
- purpose;
- supported platforms;
- variables;
- defaults;
- dependencies;
- example usage.
