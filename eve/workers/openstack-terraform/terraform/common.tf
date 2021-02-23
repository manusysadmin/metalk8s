variable "prefix" {
  type    = string
  default = ""
}

variable "rhsm_username" {
  type    = string
  default = ""
}

variable "rhsm_password" {
  type    = string
  default = ""
}

variable "debug" {
  type    = bool
  default = false
}

variable "nodes_count" {
  type    = string
  default = "2"
}

variable "offline" {
  type    = bool
  default = true
}

variable "proxy_ip" {
  type    = string
  default = "10.100.4.67"
}

variable "proxy_port" {
  type    = string
  default = "3128"
}

resource "random_string" "current" {
  length  = 5
  special = false
}

locals {
  prefix = "metalk8s-${
    var.prefix != "" ? var.prefix : random_string.current.result
  }"
}
