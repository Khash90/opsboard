# OpsBoard Kubernetes Worker Role

This Ansible role joins worker nodes to an existing kubeadm Kubernetes cluster.

It runs only on hosts in the `workers` inventory group.

## What This Role Does

The role:

- checks whether each worker has already joined the cluster
- generates a fresh kubeadm join command on the control-plane node
- keeps the bootstrap token out of Ansible output
- joins only workers that are not already cluster members
- explicitly configures containerd as the runtime
- prevents repeated join attempts on subsequent runs

## Target Hosts

```yaml
hosts: workers
```

In the current development inventory:

```text
ubuntuvm2
```

## Join-State Detection

After a successful worker join, kubeadm creates:

```text
/etc/kubernetes/kubelet.conf
```

The role uses this file as its idempotency guard.

When the file already exists, the worker join task is skipped.

## Join Command Generation

A fresh join command is generated on the first control-plane node using:

```bash
kubeadm token create --print-join-command
```

The generated command contains:

- the Kubernetes API endpoint
- a temporary bootstrap token
- the cluster CA certificate hash

The token is generated only when at least one worker still needs to join.

## Token Protection

The worker join task uses:

```yaml
no_log: true
```

This prevents the bootstrap token and complete join command from appearing in Ansible output or logs.

No token is stored in:

- role defaults
- inventory files
- Git
- permanent configuration files

## Container Runtime

The worker joins through the containerd socket:

```text
unix:///run/containerd/containerd.sock
```

## Timeout

The default maximum join duration is:

```text
300 seconds
```

This can be changed through:

```yaml
kubernetes_worker_join_timeout
```

## Expected Result

After a successful run:

```bash
kubectl get nodes -o wide
```

should show both nodes:

```text
ubuntuvm1   Ready   control-plane
ubuntuvm2   Ready   <none>
```

A worker role label will be added separately so VM2 displays:

```text
worker
```

## Idempotency

On later playbook runs:

- the existing kubelet configuration is detected
- no new token is generated
- `kubeadm join` is skipped
- the worker remains connected to the cluster
