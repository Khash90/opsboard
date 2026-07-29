# -----------------------------------------------------------------------------
# OpsBoard compute module variables
#
# These inputs control the number of Kubernetes control-plane and worker nodes.
# Provider-specific settings will be added after the infrastructure provider
# has been selected.
# -----------------------------------------------------------------------------

variable "control_plane_count" {
  description = "Number of Kubernetes control-plane nodes to provision."
  type        = number
  default     = 1

  validation {
    condition = (
      var.control_plane_count == 1 ||
      (
        var.control_plane_count >= 3 &&
        var.control_plane_count % 2 == 1
      )
    )

    error_message = "control_plane_count must be 1 for a lab, or an odd number greater than or equal to 3 for high availability."
  }
}

variable "worker_count" {
  description = "Number of Kubernetes worker nodes to provision."
  type        = number
  default     = 1

  validation {
    condition = (
      var.worker_count >= 1 &&
      floor(var.worker_count) == var.worker_count
    )

    error_message = "worker_count must be a whole number greater than or equal to 1."
  }
}
