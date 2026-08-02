# OpsBoard Docker Role

This Ansible role installs Docker build and local container-testing tools on the designated OpsBoard build host.

In the current development environment, the role runs only on `ubuntuvm1`.

## Why Ubuntu Docker Packages Are Used

The Kubernetes cluster already uses Ubuntu's `containerd` package as its container runtime.

Installing Docker CE from Docker's repository would normally install the conflicting `containerd.io` package and could replace the runtime used by the Kubernetes control plane.

To avoid disrupting the working cluster, this role installs Docker from Ubuntu's repositories:

```text
docker.io
docker-compose-v2
docker-buildx
```

This preserves the existing Kubernetes containerd installation.

## What This Role Does

The role:

- validates that a Docker user is configured
- installs Docker Engine
- installs Docker Compose v2
- installs Docker Buildx
- enables and starts the Docker service
- adds the configured build user to the `docker` group
- verifies the installed Docker tools
- displays their versions

## Target Host

The role is intended for the build and administration host:

```yaml
hosts: control_plane
```

In the current development inventory:

```text
ubuntuvm1
```

Docker is not installed on `ubuntuvm2` because Kubernetes already uses containerd there and VM2 is not an image-building host.

## Required Variable

The environment inventory must define:

```yaml
docker_user: "khash1"
```

The role default is intentionally empty because Linux usernames are environment-specific.

## Installed Tools

After a successful run, these commands should work:

```bash
docker --version
docker buildx version
docker compose version
```

## Non-Root Docker Access

The configured user is added to the `docker` group so Docker commands can run without `sudo`.

A new login session, or the following command, may be required before the updated group membership becomes active:

```bash
newgrp docker
```

## Kubernetes Runtime

Kubernetes continues using:

```text
containerd
```

Docker is installed only for:

- building application images
- running local containers
- testing the application with Docker Compose
- preparing images for a container registry

Docker does not replace the Kubernetes runtime.

## Idempotency

Repeated Ansible runs should leave installed packages, service state, and group membership unchanged.

The expected repeated-run result is:

```text
changed=0
failed=0
```
