# -----------------------------------------------------------------------------
# OpsBoard development environment outputs
#
# Exposes the validated development topology returned by the reusable compute
# module. Future infrastructure outputs such as IP addresses and hostnames will
# also be defined here.
# -----------------------------------------------------------------------------

output "control_plane_count" {
  description = "Number of Kubernetes control-plane nodes in development."
  value       = module.compute.control_plane_count
}

output "worker_count" {
  description = "Number of Kubernetes worker nodes in development."
  value       = module.compute.worker_count
}

output "total_node_count" {
  description = "Total number of Kubernetes nodes in development."
  value       = module.compute.total_node_count
}
