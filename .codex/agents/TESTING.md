# Testing and Quality Gates

## Required Local Checks
Run validation from the repository root.

### YAML
```bash
yamllint .
```

### Ansible Lint
```bash
ansible-lint
```

### Syntax Check
Run syntax checks against relevant playbooks.

```bash
ansible-playbook   -i inventories/lab/hosts.yml   playbooks/site.yml   --syntax-check
```

### Inventory Validation
```bash
ansible-inventory   -i inventories/lab/hosts.yml   --graph
```

## Idempotence Test
For configuration playbooks:
1. run once;
2. run a second time without changing inputs;
3. verify the second run reports zero unexpected changes.

Any task that changes on every run should be reviewed.

## Check Mode
Use check mode where supported:

```bash
ansible-playbook   -i inventories/lab/hosts.yml   playbooks/site.yml   --check --diff
```

Do not assume every module fully supports check mode.

## Functional Validation
After a role changes something, validate the intended outcome.

Examples:
- service is active;
- port is listening;
- endpoint returns expected status;
- package is installed;
- configuration syntax is valid.

Prefer Ansible modules for validation rather than arbitrary shell commands.

## Molecule
Use Molecule for roles where repeatable isolated testing adds value.

Prioritize Molecule for:
- reusable roles;
- roles with templates and handlers;
- roles containing OS-specific behavior;
- roles likely to grow over time.

A small demo role does not need complicated tests merely to satisfy a framework.

## CI
GitHub Actions should eventually enforce:
- YAML lint;
- Ansible lint;
- syntax checks.

Never place production or lab secrets directly in workflow YAML.

## Pull Request / Change Checklist
Before merging:
- [ ] YAML parses.
- [ ] `yamllint` passes.
- [ ] `ansible-lint` passes.
- [ ] syntax check passes.
- [ ] no secrets are present.
- [ ] role/playbook inputs are documented.
- [ ] first run produces expected changes.
- [ ] second run is idempotent.
- [ ] disruptive behavior is guarded.
- [ ] README/demo instructions are updated where necessary.
