# -----------------------------------------------------------------------------
# OpsBoard development environment
#
# Connects the reusable compute module to the current development topology.
# Provider-specific infrastructure resources will be added after the target
# infrastructure platform has been selected.
# -----------------------------------------------------------------------------

module "compute" {
  source = "../../modules/compute"

  control_plane_count = var.control_plane_count
  worker_count        = var.worker_count
}

module "networking" {
  source = "../../modules/networking"

  network_cidr      = var.network_cidr
  control_plane_ips = var.control_plane_ips
  worker_ips        = var.worker_ips
}
