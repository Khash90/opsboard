# Production Environment

The `prod` environment will host the production OpsBoard platform.

It must prioritize availability, security, recoverability, controlled change management, and predictable operations.

## Purpose

Production will run:

- the OpsBoard application
- Kubernetes platform services
- GitOps-managed deployments
- monitoring and alerting
- centralized logging
- production ingress and networking
- backup and recovery workflows

All production changes should be reviewed, tested in staging, and applied through version-controlled automation.

## Desired Topology

A typical production environment may use:

```hcl
control_plane_count = 3
worker_count        = 3
```

The exact worker count should depend on workload capacity, availability requirements, and cost.

Control-plane counts must be either:

- `1` for a non-high-availability lab; or
- an odd number greater than or equal to `3`

Production should normally use at least three control-plane nodes.

## High Availability

The production platform should include:

- an odd number of control-plane nodes
- a stable Kubernetes API endpoint
- load balancing or a virtual IP
- health checks for control-plane nodes
- multiple worker nodes
- redundant networking paths where supported
- resilient storage for stateful workloads
- failure-domain awareness when available

The design should avoid unnecessary single points of failure.

## Environment-Specific Values

Production configuration may define:

- infrastructure provider
- region or data-center location
- control-plane node count
- worker node count
- control-plane instance size
- worker instance size
- network and subnet CIDRs
- Kubernetes API endpoint
- approved administrative CIDRs
- SSH key references
- DNS names
- load-balancer configuration
- storage configuration
- backup destinations
- resource tags and labels

These values should remain outside reusable Terraform modules.

## Security

Production must follow strict security controls:

- least-privilege firewall rules
- restricted administrative access
- controlled Kubernetes API exposure
- encrypted secrets
- encrypted traffic
- no credentials committed to Git
- auditable infrastructure changes
- vulnerability scanning
- security updates
- centralized logging
- protected backups
- separation of production and non-production data

Secrets should be supplied through an approved secret-management system or protected CI/CD variables.

## State Management

Production Terraform state must not be stored only on a developer workstation.

The final implementation should use a protected remote backend with:

- encryption at rest
- access controls
- state locking
- versioning or recovery support
- restricted write permissions

Terraform state files and sensitive variable files must never be committed to Git.

## Backup and Recovery

The production design should include documented procedures for:

- infrastructure recreation
- Kubernetes control-plane recovery
- application-data backup
- persistent-volume backup
- secret recovery
- configuration restoration
- disaster-recovery testing

Backups are only useful when restoration procedures are tested successfully.

## Relationship with Ansible

Terraform will provision the production infrastructure and expose connection details through outputs.

Those outputs may be used to generate an Ansible inventory such as:

```text
ansible/inventories/prod/hosts.yml
```

Ansible will then:

- prepare the operating system
- install and configure containerd
- install Kubernetes components
- initialize the control plane
- join additional control-plane nodes
- join worker nodes
- apply host-level security configuration

Terraform must not replace Ansible for operating-system and software configuration.

## Change Management

Production changes should follow this workflow:

```text
development → staging → production
```

Production changes should require:

- successful validation in development
- successful validation in staging
- reviewed Terraform plans
- reviewed Ansible changes
- approved deployment changes
- rollback or recovery planning

Manual production changes should be avoided because they create configuration drift and reduce reproducibility.
