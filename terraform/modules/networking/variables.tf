# -----------------------------------------------------------------------------
# OpsBoard networking module variables
#
# Defines provider-neutral networking inputs for the OpsBoard Kubernetes
# infrastructure. Provider-specific resources will be added after the target
# hosting platform and its capabilities are known.
# -----------------------------------------------------------------------------

variable "network_cidr" {
  description = "CIDR block assigned to the infrastructure network."
  type        = string
  default     = "10.0.2.0/24"

  validation {
    condition     = can(cidrnetmask(var.network_cidr))
    error_message = "network_cidr must be a valid IPv4 CIDR block."
  }
}

variable "control_plane_ips" {
  description = "IP addresses assigned to Kubernetes control-plane nodes."
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
  description = "IP addresses assigned to Kubernetes worker nodes."
  type        = list(string)
  default     = ["10.0.2.6"]

  validation {
    condition = alltrue([
      for ip in var.worker_ips : can(cidrhost("${ip}/32", 0))
    ])

    error_message = "Every worker address must be a valid IPv4 address."
  }
}
