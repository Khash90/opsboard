# -----------------------------------------------------------------------------
# OpsBoard development environment variables
#
# Defines environment-specific Kubernetes topology values. These variables are
# passed into reusable Terraform modules from the development environment.
# -----------------------------------------------------------------------------

variable "control_plane_count" {
  description = "Number of Kubernetes control-plane nodes in development."
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

    error_message = "control_plane_count must be 1, or an odd number greater than or equal to 3."
  }
}

variable "worker_count" {
  description = "Number of Kubernetes worker nodes in development."
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
