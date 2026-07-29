# -----------------------------------------------------------------------------
# OpsBoard development environment variables
#
# Defines environment-specific Kubernetes topology and networking values.
# These variables are passed into reusable Terraform modules from the
# development environment.
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

variable "network_cidr" {
  description = "CIDR block used by the development infrastructure network."
  type        = string
  default     = "10.0.2.0/24"

  validation {
    condition     = can(cidrnetmask(var.network_cidr))
    error_message = "network_cidr must be a valid IPv4 CIDR block."
  }
}

variable "control_plane_ips" {
  description = "IP addresses assigned to development control-plane nodes."
  type        = list(string)
  default     = ["10.0.2.5"]

  validation {
    condition = alltrue([
      for ip in var.control_plane_ips : can(cidrhost("${ip}/32", 0))
    ])

    error_message = "Every control-plane address must be a valid IPv4 address."
  }
}

variable "worker_ips" {
  description = "IP addresses assigned to development worker nodes."
  type        = list(string)
  default     = ["10.0.2.6"]

  validation {
    condition = alltrue([
      for ip in var.worker_ips : can(cidrhost("${ip}/32", 0))
    ])

    error_message = "Every worker address must be a valid IPv4 address."
  }
}
