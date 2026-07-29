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
