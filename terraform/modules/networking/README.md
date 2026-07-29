# Networking Module

The `networking` module will provision the network foundation required by the OpsBoard Kubernetes platform.

Its design will support reusable, environment-specific networking across development, staging, and production deployments.

## Responsibilities

This module will manage:

- virtual networks or VPCs
- public and private subnets
- routing tables
- internet or NAT gateway connectivity
- firewall or security-group rules
- Kubernetes API access
- internal node-to-node communication
- load-balancer connectivity
- configurable network CIDR ranges
- standardized naming and tags

## Network Configuration

Network values must be provided through variables instead of being hardcoded inside the module.

Example:

```hcl
network_cidr            = "10.10.0.0/16"
control_plane_subnet_cidr = "10.10.10.0/24"
worker_subnet_cidr        = "10.10.20.0/24"
```

A different environment may use:

```hcl
network_cidr              = "10.20.0.0/16"
control_plane_subnet_cidr = "10.20.10.0/24"
worker_subnet_cidr        = "10.20.20.0/24"
```

The reusable module should not require changes when network ranges differ. Environment-specific inputs should define the desired address space.

## Security Design

Network access should follow the principle of least privilege.

The module will support rules for:

- SSH access from approved administrative sources
- Kubernetes API access from approved sources
- control-plane communication
- worker-to-control-plane communication
- node-to-node cluster traffic
- application ingress
- monitoring and observability traffic

Public exposure should be limited to services that explicitly require it.

## High Availability

Highly available Kubernetes control planes require a stable API endpoint.

The networking module may later provide:

- a load balancer
- a virtual IP
- health checks
- backend registration for multiple control-plane nodes

Ansible and Kubernetes configuration should reference the stable API endpoint instead of a single control-plane node IP.

## Provider Independence

The module structure is being created before selecting the final infrastructure provider.

Provider-specific networking resources will be added later when the target platform is known, such as:

- cloud virtual networks
- provider firewalls
- managed load balancers
- private networking features
- virtual private server networking

This prevents the reusable design from being tied prematurely to one provider.

## Relationship with Compute

The networking module creates the network resources used by the compute module.

The compute module will attach control-plane and worker nodes to the appropriate networks or subnets.

Terraform outputs may later expose:

- control-plane IP addresses
- worker IP addresses
- Kubernetes API endpoint
- subnet identifiers
- network identifiers

These outputs can then be consumed by Ansible inventory generation and other automation.
