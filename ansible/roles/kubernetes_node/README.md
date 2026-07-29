# OpsBoard Kubernetes Node Role

This Ansible role prepares Ubuntu control-plane and worker nodes for Kubernetes.

It configures the operating-system requirements that must be in place before installing `kubeadm`, `kubelet`, and `kubectl`.

## What This Role Does

The role:

- disables swap immediately
- disables swap persistently in `/etc/fstab`
- loads the `overlay` kernel module
- loads the `br_netfilter` kernel module
- preserves required kernel modules across reboots
- enables IPv4 packet forwarding
- enables bridge traffic processing by iptables
- preserves Kubernetes sysctl settings across reboots

## Why These Settings Are Required

Kubernetes nodes require specific Linux settings for container networking and kubelet operation.

The preparation flow is:

```text
Ubuntu node
    ↓
Disable swap
    ↓
Load kernel modules
    ↓
Configure sysctl networking
    ↓
Ready for Kubernetes packages
```

## Role Location

```text
ansible/roles/kubernetes_node/
```

Important files:

```text
defaults/main.yml   Configurable swap, kernel-module, and sysctl values
tasks/main.yml      Kubernetes node-preparation tasks
handlers/main.yml   Loads modules and reapplies sysctl settings
meta/main.yml       Ansible Galaxy role metadata
README.md           Role documentation
```

## Target Hosts

This role will run on:

```yaml
hosts: all
```

In the current development inventory, that means:

```text
ubuntuvm1   Kubernetes control-plane node
ubuntuvm2   Kubernetes worker node
```

Both types of Kubernetes nodes require these operating-system settings.

## Swap Configuration

Kubernetes uses the default kubelet behavior that expects swap to be disabled.

The role runs:

```bash
swapoff -a
```

It also comments out active swap entries in:

```text
/etc/fstab
```

This prevents swap from returning after a reboot.

## Kernel Modules

The role loads:

```text
overlay
br_netfilter
```

Their persistent configuration is stored in:

```text
/etc/modules-load.d/kubernetes.conf
```

### `overlay`

The `overlay` module supports the overlay filesystem used by container runtimes.

### `br_netfilter`

The `br_netfilter` module allows Linux bridge traffic to be processed by iptables rules.

This is required for Kubernetes pod networking and the future Flannel CNI configuration.

## Sysctl Networking Configuration

The persistent settings are stored in:

```text
/etc/sysctl.d/99-kubernetes.conf
```

The role configures:

```text
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
```

These settings allow:

- bridged container traffic to reach iptables
- IPv4 packets to be forwarded between network interfaces
- pods on different Kubernetes nodes to communicate

## Configurable Defaults

Default values are defined in:

```text
ansible/roles/kubernetes_node/defaults/main.yml
```

The main variables are:

```yaml
kubernetes_disable_swap: true

kubernetes_kernel_modules:
  - overlay
  - br_netfilter

kubernetes_modules_config_file: "/etc/modules-load.d/kubernetes.conf"

kubernetes_sysctl_settings:
  net.bridge.bridge-nf-call-iptables: 1
  net.bridge.bridge-nf-call-ip6tables: 1
  net.ipv4.ip_forward: 1

kubernetes_sysctl_config_file: "/etc/sysctl.d/99-kubernetes.conf"
```

These values can later be overridden through environment or inventory variables.

## Expected Verification

After the role runs, swap should be disabled:

```bash
swapon --show
```

Expected output:

```text
No output
```

The kernel modules should be loaded:

```bash
lsmod | grep -E 'overlay|br_netfilter'
```

The networking settings should return `1`:

```bash
sysctl net.bridge.bridge-nf-call-iptables
sysctl net.bridge.bridge-nf-call-ip6tables
sysctl net.ipv4.ip_forward
```

## Idempotency

Running the role again should not modify configuration when the desired state already exists.

The expected repeated-run result is:

```text
changed=0
failed=0
```
