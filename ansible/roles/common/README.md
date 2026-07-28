# Common Role

The `common` role applies the shared Linux baseline required by every OpsBoard node.

It is designed to be reusable across control-plane nodes, worker nodes, and future environments such as development, staging, and production.

## Responsibilities

The role currently:

- installs shared operating system packages;
- keeps package configuration centralized and reusable;
- provides the foundation for later Kubernetes host preparation.

Additional shared host configuration will be added incrementally as the platform evolves.

## Requirements

- Ubuntu 24.04 or another supported Debian-based system
- Python 3 available on each managed node
- SSH connectivity from the Ansible control node
- Privilege escalation through `sudo`

## Role Variables

The following variable is defined in `defaults/main.yml`:

```yaml
common_packages:
  - apt-transport-https
  - ca-certificates
  - curl
  - gnupg
  - jq
  - software-properties-common
  - unzip
```

The package list can be overridden in inventory variables or environment-specific configuration without modifying the role tasks.

## Example Playbook

```yaml
---
- name: Apply the shared Linux baseline
  hosts: all
  become: true

  roles:
    - common
```

## Idempotency

The role is designed to be idempotent. Re-running the playbook should report no changes when the target systems already match the desired state.

## License

MIT-0
