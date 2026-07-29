# -----------------------------------------------------------------------------
# OpsBoard networking module outputs
#
# Exposes validated network information for environment-level configuration,
# Ansible inventory generation, and future provider-specific resources.
# -----------------------------------------------------------------------------

output "network_cidr" {
  description = "CIDR block assigned to the infrastructure network."
  value       = var.network_cidr
}

output "control_plane_ips" {
  description = "IP addresses assigned to Kubernetes control-plane nodes."
  value       = var.control_plane_ips
}

output "worker_ips" {
  description = "IP addresses assigned to Kubernetes worker nodes."
  value       = var.worker_ips
}

output "all_node_ips" {
  description = "Combined list of all Kubernetes node IP addresses."
  value       = concat(var.control_plane_ips, var.worker_ips)
}
