# OpsBoard Containerd Role

This Ansible role installs and configures `containerd` on OpsBoard Kubernetes nodes.

It is intended to run on both control-plane and worker nodes before Kubernetes is installed.

## What This Role Does

The role:

- installs the Ubuntu `containerd` package
- creates `/etc/containerd`
- generates the default containerd configuration
- enables the `systemd` cgroup driver
- enables the containerd service at boot
- ensures the containerd service is running
- restarts containerd only when its configuration changes

## Why Containerd Is Required

Kubernetes needs a container runtime to start and manage containers.

OpsBoard uses:

```text
Kubernetes
    ↓
containerd
    ↓
Linux containers
```

Docker Engine is not required on Kubernetes nodes for the cluster runtime.

Docker may still be installed later on the build machine for building and testing application images.

## Role Location

```text
ansible/roles/containerd/
```

Important files:

```text
defaults/main.yml   Configurable package, service, and path values
tasks/main.yml      Installation and configuration tasks
handlers/main.yml   Restarts containerd after configuration changes
meta/main.yml       Ansible Galaxy role metadata
README.md           Role documentation
```

## Target Hosts

The role is applied to:

```yaml
hosts: all
```

In the current development inventory, this means:

```text
ubuntuvm1   Kubernetes control-plane node
ubuntuvm2   Kubernetes worker node
```

Both nodes require containerd.

## Main Configuration File

Containerd is configured through:

```text
/etc/containerd/config.toml
```

The role generates the default configuration and changes:

```toml
SystemdCgroup = false
```

to:

```toml
SystemdCgroup = true
```

This keeps the container runtime cgroup driver consistent with Kubernetes and systemd.

## Configurable Defaults

The default variables are defined in:

```text
ansible/roles/containerd/defaults/main.yml
```

They include:

```yaml
containerd_package_name: "containerd"
containerd_package_state: "present"
containerd_service_name: "containerd"

containerd_config_directory: "/etc/containerd"
containerd_config_file: "/etc/containerd/config.toml"

containerd_systemd_cgroup: true

containerd_service_enabled: true
containerd_service_state: "started"
```

These values can be overridden through environment or inventory variables when needed.

## Main Playbook

The role is called from:

```text
ansible/playbooks/site.yml
```

The relevant play is:

```yaml
- name: Configure the Kubernetes container runtime
  hosts: all
  become: true
  gather_facts: true

  roles:
    - containerd
```

## Running the Role

From the repository root:

```bash
ansible-playbook ansible/playbooks/site.yml
```

To check syntax without changing any hosts:

```bash
ansible-playbook ansible/playbooks/site.yml --syntax-check
```

## Expected Result

After a successful run:

```bash
systemctl is-enabled containerd
systemctl is-active containerd
```

should return:

```text
enabled
active
```

The configuration should also contain:

```toml
SystemdCgroup = true
```

## Idempotency

Running the playbook again should not rewrite the configuration or restart containerd when nothing has changed.

The expected second-run result is:

```text
changed=0
failed=0
```
