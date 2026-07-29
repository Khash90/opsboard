# Compute Module

The `compute` module will provision the server instances required by the OpsBoard Kubernetes platform.

Its design will support reusable, variable-driven infrastructure across development, staging, and production environments.

## Responsibilities

This module will manage:

- Kubernetes control-plane nodes
- Kubernetes worker nodes
- configurable node counts
- configurable instance sizes
- consistent naming conventions
- standard labels and tags
- SSH access configuration
- server network attachment

## Scaling

Node quantities must be provided through variables rather than hardcoded in resource definitions.

Example:

```hcl
control_plane_count = 1
worker_count        = 1
```

A larger environment may use:

```hcl
control_plane_count = 3
worker_count        = 20
```

The reusable module should not require changes when node counts increase. Environment-specific inputs should control the desired infrastructure size.

## High Availability

A production control plane may use an odd number of nodes, such as:

- 3 control-plane nodes
- 5 control-plane nodes
- 7 control-plane nodes

A single control-plane node is acceptable for a development lab.

Validation will be added so the control-plane count must be either:

- `1` for a non-high-availability environment; or
- an odd number greater than or equal to `3`

## Provider Independence

The module structure is being created before selecting the final infrastructure provider.

Provider-specific resources will be added later when the target platform is known, such as:

- a cloud provider
- a virtual private server provider
- a supported virtualization platform

This prevents reusable infrastructure design from being tied prematurely to one provider.

## Relationship with Ansible

Terraform provisions servers and returns connection information such as hostnames and IP addresses.

Ansible then uses that information to:

- prepare the operating system
- install containerd
- install Kubernetes components
- initialize control-plane nodes
- join worker nodes to the cluster

Terraform must not install Kubernetes packages or configure operating-system services directly.
