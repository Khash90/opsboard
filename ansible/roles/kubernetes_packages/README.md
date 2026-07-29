# OpsBoard Kubernetes Packages Role

This Ansible role installs the Kubernetes command-line and node packages required by the OpsBoard cluster.

It is intended to run after the operating-system preparation and container runtime roles.

## What This Role Does

The role:

- adds the official Kubernetes APT repository
- installs `kubeadm` and `kubelet` on every Kubernetes node
- installs `kubectl` only on control-plane administration nodes
- enables `kubelet` at boot
- holds Kubernetes packages at their installed versions
- prevents accidental upgrades through normal `apt upgrade` operations

## Why These Packages Are Required

### `kubeadm`

`kubeadm` creates the control plane and joins additional nodes to the cluster.

It will later be used for:

```text
VM1: kubeadm init
VM2: kubeadm join
```

### `kubelet`

`kubelet` runs on every Kubernetes node.

It communicates with the Kubernetes control plane and ensures the required pods and containers are running on the node.

### `kubectl`

`kubectl` is the Kubernetes administration command-line tool.

It will be installed only on VM1 because VM1 is the administration and control-plane node.

After cluster initialization, the `khash1` user will use commands such as:

```bash
kubectl get nodes
kubectl get pods -A
kubectl describe node ubuntuvm2
```

## Role Location

```text
ansible/roles/kubernetes_packages/
```

Important files:

```text
defaults/main.yml   Repository, version, package, and package-hold settings
tasks/main.yml      Repository configuration and package installation tasks
meta/main.yml       Ansible Galaxy role metadata
README.md           Role documentation
```

## Target Packages

### VM1 — control-plane and administration node

```text
kubeadm
kubelet
kubectl
```

### VM2 — worker node

```text
kubeadm
kubelet
```

`kubectl` is not required on the worker node.

## Kubernetes Repository

The role uses the official version-specific Kubernetes repository:

```text
https://pkgs.k8s.io/core:/stable:/v1.36/deb/
```

The minor release is configurable through:

```yaml
kubernetes_minor_version: "v1.36"
```

Changing this value updates both the repository URL and signing-key URL.

## Package Holding

Kubernetes packages are held after installation.

The equivalent manual commands would be:

```bash
sudo apt-mark hold kubeadm kubelet kubectl
```

On worker nodes where `kubectl` is not installed, only these packages are held:

```bash
sudo apt-mark hold kubeadm kubelet
```

This prevents automatic upgrades that could create unsupported Kubernetes version differences between nodes.

During a planned upgrade, packages can temporarily be unheld:

```bash
sudo apt-mark unhold kubeadm kubelet kubectl
```

After the controlled upgrade, they should be held again.

## Configurable Defaults

The main defaults are stored in:

```text
ansible/roles/kubernetes_packages/defaults/main.yml
```

Important variables include:

```yaml
kubernetes_minor_version: "v1.36"

kubernetes_node_packages:
  - kubeadm
  - kubelet

kubernetes_control_plane_packages:
  - kubectl

kubernetes_package_state: "present"
kubernetes_hold_packages: true
kubelet_service_enabled: true
```

## Kubelet Behavior Before Cluster Creation

The kubelet service is enabled immediately.

Before the node is initialized or joined with `kubeadm`, kubelet may restart repeatedly because its Kubernetes configuration does not exist yet.

That behavior is expected.

After:

```text
kubeadm init
```

or:

```text
kubeadm join
```

the required kubelet configuration files will be created.

## Expected Verification

On VM1:

```bash
kubeadm version
kubelet --version
kubectl version --client
```

On VM2:

```bash
kubeadm version
kubelet --version
```

Package holds can be checked with:

```bash
apt-mark showhold
```

## Idempotency

Running the role again should not reinstall packages, recreate repository files, or change package holds when the desired state already exists.

The expected repeated-run result is:

```text
changed=0
failed=0
```
