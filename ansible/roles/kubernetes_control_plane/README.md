# OpsBoard Kubernetes Control Plane Role

This Ansible role initializes and configures the first OpsBoard Kubernetes control-plane node.

It runs only on the control-plane inventory group.

## What This Role Does

The role:

- checks whether the control plane is already initialized
- runs `kubeadm init` only when required
- configures the Kubernetes API server address and port
- configures the pod and service network ranges
- uses containerd as the container runtime
- creates the regular user's `.kube` directory
- copies the administrator kubeconfig
- allows `kubectl` to run without `sudo`
- waits for the Kubernetes API server
- verifies the control-plane node

Flannel installation and worker-node joining will be added separately.

## Role Location

```text
ansible/roles/kubernetes_control_plane/
```

Important files:

```text
defaults/main.yml   Cluster networking, API, runtime, and kubeconfig settings
tasks/main.yml      Control-plane initialization and kubectl configuration
meta/main.yml       Ansible Galaxy role metadata
README.md           Role documentation
```

## Target Host

This role is intended for:

```yaml
hosts: control_plane
```

In the current development inventory:

```text
ubuntuvm1
```

VM2 will be joined separately as a worker node.

## Cluster Networks

The current development values are:

```text
VM network:       10.0.2.0/24
Pod network:      10.244.0.0/16
Service network:  10.96.0.0/12
```

These ranges must not overlap.

### VM Network

```text
10.0.2.0/24
```

This is the existing VirtualBox network used by VM1 and VM2.

### Pod Network

```text
10.244.0.0/16
```

This range will be used by Flannel for Kubernetes pod addresses.

### Service Network

```text
10.96.0.0/12
```

This range is used for Kubernetes virtual service addresses such as `ClusterIP`.

## Control-Plane Initialization

The role runs the equivalent of:

```bash
sudo kubeadm init \
  --apiserver-advertise-address=10.0.2.5 \
  --apiserver-bind-port=6443 \
  --pod-network-cidr=10.244.0.0/16 \
  --service-cidr=10.96.0.0/12 \
  --cri-socket=unix:///run/containerd/containerd.sock
```

This creates:

- Kubernetes API server
- controller manager
- scheduler
- etcd
- cluster certificates
- kubeconfig files
- control-plane static pod manifests

## Idempotency Guard

The role checks for:

```text
/etc/kubernetes/admin.conf
```

This file is created after a successful `kubeadm init`.

When it already exists, Ansible skips cluster initialization. This prevents an existing control plane from being initialized again.

## kubectl Configuration

Kubeadm creates the administrator configuration at:

```text
/etc/kubernetes/admin.conf
```

The role copies it to:

```text
/home/khash1/.kube/config
```

Ownership and permissions are set to:

```text
User:        khash1
Group:       khash1
Permissions: 0600
```

Afterward, the regular user can run:

```bash
kubectl get nodes
kubectl get pods -A
```

without `sudo`.

## API Readiness Check

The role waits for:

```text
/readyz
```

on the Kubernetes API server.

This allows time for the control-plane components to start before Ansible continues.

## Current Limitations

This role does not yet:

- install Flannel
- create the pod network
- generate the worker join command
- join VM2
- label VM2 as a worker

Those steps are handled in later automation.

## Expected Result

After successful initialization:

```bash
kubectl get nodes -o wide
```

should show VM1 as the control-plane node.

Before Flannel is installed, the node may temporarily show:

```text
NotReady
```

That is expected because the cluster does not yet have a CNI network plugin.

## Idempotency

After initialization, running the role again should not run `kubeadm init` again.

The expected repeated-run result is:

```text
changed=0
failed=0
```
