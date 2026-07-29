# Development Environment

The `dev` environment represents the local OpsBoard development and validation setup.

Its purpose is to test Terraform structure, Ansible automation, Kubernetes installation, and application deployment before the same patterns are applied to staging or production infrastructure.

## Current Infrastructure

The current development environment uses two manually created VirtualBox virtual machines:

- `ubuntuvm1`
  - role: Kubernetes control-plane node
  - IP address: `10.0.2.5`

- `ubuntuvm2`
  - role: Kubernetes worker node
  - IP address: `10.0.2.6`

These VMs existed before Terraform was introduced into the project.

## Terraform Ownership

Terraform does not currently create, modify, or destroy the VirtualBox VMs in this environment.

The existing machines are used to validate:

- Ansible connectivity
- operating-system configuration
- container runtime installation
- Kubernetes installation
- cluster initialization
- worker-node joining
- platform deployment

Terraform configuration for this environment will remain provider-neutral until a supported infrastructure provider is selected.

## Desired Topology

The current development topology is:

```hcl
control_plane_count = 1
worker_count        = 1
```

A single control-plane node is appropriate for this non-production lab.

## Environment-Specific Values

Future development variables may include:

- node counts
- instance sizes
- network CIDRs
- SSH usernames
- SSH key references
- Kubernetes API endpoint
- provider region
- provider-specific identifiers

These values should remain outside reusable modules.

## Relationship with Ansible

Ansible currently uses the inventory file:

```text
ansible/inventories/dev/hosts.yml
```

That inventory contains the connection details for the existing VirtualBox nodes.

When Terraform later provisions infrastructure, its outputs may be used to generate or update the Ansible inventory automatically.

## Safety

No Terraform configuration in this environment should attempt to import or take ownership of the existing VirtualBox VMs unless an explicit migration plan is created and reviewed.
