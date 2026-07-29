# -----------------------------------------------------------------------------
# OpsBoard compute module outputs
#
# Exposes validated node counts for environment-level Terraform configuration
# and future provider-specific resources.
# -----------------------------------------------------------------------------

output "control_plane_count" {
  description = "Validated number of Kubernetes control-plane nodes."
  value       = var.control_plane_count
}

output "worker_count" {
  description = "Validated number of Kubernetes worker nodes."
  value       = var.worker_count
}

output "total_node_count" {
  description = "Total number of Kubernetes nodes."
  value       = var.control_plane_count + var.worker_count
}
