# Staging Environment

The `staging` environment will provide a production-like OpsBoard platform for validating infrastructure, Kubernetes changes, application releases, and operational procedures before promotion to production.

It should closely resemble production while using smaller capacity where appropriate.

## Purpose

Staging will be used to validate:

- Terraform infrastructure changes
- Ansible roles and playbooks
- Kubernetes upgrades
- Helm chart changes
- Argo CD synchronization
- security controls
- monitoring and alerting
- application release candidates
- backup and recovery procedures

## Desired Topology

A typical staging environment may use:

```hcl
control_plane_count = 3
worker_count        = 2
```

Three control-plane nodes provide a realistic highly available topology for testing without requiring production-scale capacity.

Node counts remain configurable and may be adjusted through environment-specific variables.

## High Availability

The staging control plane should use:

- an odd number of control-plane nodes
- a stable Kubernetes API endpoint
- load balancing or a virtual IP
- health checks for control-plane nodes
- redundant worker capacity where practical

The environment should validate the same high-availability patterns intended for production.

## Environment-Specific Values

Staging configuration may define:

- infrastructure provider
- region or data-center location
- control-plane node count
- worker node count
- instance sizes
- network and subnet CIDRs
- Kubernetes API endpoint
- approved administrative CIDRs
- SSH key references
- DNS names
- load-balancer configuration
- resource tags and labels

These values should remain outside reusable Terraform modules.

## Security

Staging should follow production-like security practices:

- least-privilege firewall rules
- restricted SSH access
- encrypted secrets
- no credentials committed to Git
- controlled Kubernetes API access
- auditable infrastructure changes
- isolated staging data
- no use of sensitive production data unless explicitly approved and protected

## Relationship with Ansible

Terraform will provision the staging infrastructure and expose connection details through outputs.

Those outputs may be used to generate an Ansible inventory such as:

```text
ansible/inventories/staging/hosts.yml
```

Ansible will then configure the operating system, container runtime, Kubernetes components, and platform services.

## Promotion Workflow

Changes should normally follow this order:

```text
development → staging → production
```

A change should be promoted to production only after staging validation succeeds.
