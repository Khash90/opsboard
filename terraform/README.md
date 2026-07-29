# Terraform Infrastructure

The `terraform/` directory contains the reusable infrastructure-as-code foundation for OpsBoard.

Terraform is responsible for provisioning infrastructure such as servers, networking, addresses, and environment-specific resources. It does not install or configure Kubernetes, containerd, Docker, or operating-system packages. Those responsibilities belong to Ansible.

## Directory Structure

```text
terraform/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── modules/
    ├── compute/
    └── networking/
```

## Environments

Each environment contains the configuration and input values required for that deployment.

- `dev` — local development and testing
- `staging` — pre-production validation
- `prod` — production infrastructure

Environment-specific values may include:

- control-plane node count
- worker node count
- instance sizes
- IP ranges
- regions
- network CIDRs
- provider credentials or references

Sensitive credentials must never be committed to Git.

## Reusable Modules

### Compute

The `compute` module will define reusable server resources for:

- Kubernetes control-plane nodes
- Kubernetes worker nodes
- configurable machine counts
- configurable instance sizes
- standardized naming and tagging

### Networking

The `networking` module will define reusable networking resources such as:

- virtual networks
- subnets
- routing
- firewall or security rules
- load-balancer connectivity
- Kubernetes API access

## Scaling Design

Counts and capacity settings will be exposed as variables rather than hardcoded.

Example:

```hcl
control_plane_count = 1
worker_count        = 1
```

A future highly available environment may use:

```hcl
control_plane_count = 3
worker_count        = 20
```

Reusable modules should not require changes when scaling. Environment values should control the desired size.

## Current Development Lab

The current VirtualBox VMs were created manually before Terraform was introduced:

- `ubuntuvm1` — Kubernetes control-plane node
- `ubuntuvm2` — Kubernetes worker node

Terraform will not attempt to take ownership of these existing VMs. They are used to validate the Ansible and Kubernetes automation locally.

A future cloud or rented-server implementation will use the Terraform modules to create infrastructure from scratch.
