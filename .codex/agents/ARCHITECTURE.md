# Repository Architecture

## Objective
Keep this AAP demo repository simple enough to teach from and structured enough to
show production-quality Ansible habits.

## Architectural Principles

### Thin Playbooks, Reusable Roles
Top-level playbooks describe intent and target groups.
Implementation logic belongs in roles.

Example:

```text
playbooks/
├── baseline.yml
├── patch.yml
├── web.yml
└── site.yml

roles/
├── baseline/
├── patching/
└── web_server/
```

### Separate Code from Environment Data
Automation logic belongs in playbooks and roles.
Environment-specific values belong under inventory.

```text
inventories/
└── lab/
    ├── hosts.yml
    ├── group_vars/
    │   ├── all.yml
    │   ├── web.yml
    │   └── database.yml
    └── host_vars/
```

### Inventory Grouping
Group hosts by meaningful characteristics such as:
- function: `web`, `database`, `automation`;
- location: `lab`, `edge`;
- lifecycle: `dev`, `test`, `prod`.

Do not encode implementation logic into hostnames.

### Dependency Management
Declare required collections and roles in `requirements.yml`.

Example:

```yaml
---
collections:
  - name: ansible.posix
  - name: community.general
```

Pin versions when repeatability is more important than automatically receiving the
latest version.

### Execution Environment Readiness
The repository should not assume packages or collections exist on a developer laptop.
Anything required at execution time should be available through:
- the execution environment image;
- `requirements.yml`;
- repository files;
- Controller credentials or variables.

## Suggested Demo Progression

### Phase 1 — Connectivity
Demonstrate:
- inventory;
- SSH connectivity;
- `ansible.builtin.ping`;
- facts.

### Phase 2 — Linux Baseline
Demonstrate:
- package management;
- users/groups;
- time synchronization;
- MOTD;
- services.

### Phase 3 — Configuration Management
Demonstrate:
- templating;
- handlers;
- firewall configuration;
- service configuration;
- repeatable/idempotent runs.

### Phase 4 — Operations
Demonstrate:
- patching;
- reboot control;
- health checks;
- reporting;
- rolling execution using `serial`.

### Phase 5 — AAP
Demonstrate:
- Git-backed project;
- inventory;
- credentials;
- job templates;
- surveys for safe operator inputs;
- workflows;
- RBAC;
- schedules;
- notifications where useful.

## Naming
Use lowercase `snake_case` for:
- role names;
- variable names;
- inventory groups.

Use descriptive playbook names based on intent.

Good:
- `patch_rhel.yml`
- `configure_web.yml`
- `baseline.yml`

Avoid:
- `test1.yml`
- `stuff.yml`
- `final.yml`
