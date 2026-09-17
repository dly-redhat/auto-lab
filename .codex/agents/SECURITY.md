# Security Standards

## Secrets
Never commit:
- passwords;
- SSH private keys;
- API tokens;
- vault passwords;
- cloud credentials;
- AAP credentials;
- private certificates or keys.

Use one of:
- AAP credential objects;
- Ansible Vault;
- environment-backed credentials;
- an external secret manager.

## Git Ignore
The repository should ignore common secret material, including:

```gitignore
*.retry
*.vault-password
vault_password*
.env
.env.*
*.pem
*.key
id_rsa
id_ed25519
```

Do not assume `.gitignore` makes a secret safe after it has already been committed.

## Sensitive Output
Use `no_log: true` for tasks that could expose credentials or sensitive return values.

Example:
```yaml
- name: Use API credential
  ansible.builtin.uri:
    url: "{{ service_url }}"
    headers:
      Authorization: "Bearer {{ service_token }}"
  no_log: true
```

Apply `no_log` narrowly enough that troubleshooting remains practical.

## TLS
Keep certificate validation enabled by default.
Do not set certificate validation to false simply to make a demo work.

For a lab with self-signed certificates:
- install/trust the lab CA where practical; or
- explicitly document a lab-only exception.

## Least Privilege
- Use `become: true` only where required.
- Prefer scoped service accounts.
- Do not automate everything as root when a narrower privilege model is possible.
- In AAP, use separate credentials when different privilege boundaries exist.

## Input Validation
Runtime inputs from surveys or extra vars must be treated as untrusted operator input.

Where practical:
- constrain choices in Controller surveys;
- use `ansible.builtin.assert`;
- validate ranges, states, host groups, and allowed operations.

Example:
```yaml
- name: Validate requested service state
  ansible.builtin.assert:
    that:
      - requested_state in ["started", "stopped", "restarted"]
    fail_msg: "requested_state must be started, stopped, or restarted"
```

## Dangerous Operations
Destructive operations require an explicit opt-in variable.

Example:
```yaml
allow_destructive_operation: false
```

Then assert the opt-in before executing the operation.

## Logging
Design automation so logs explain:
- what was targeted;
- what was changed;
- what failed;
- what validation ran.

Do not log secrets.
