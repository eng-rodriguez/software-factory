terraform {
  required_version = ">= 1.6.0, < 2.0.0"
}
variable "replicas" {
  type = number
}
output "replicas" {
  value = var.replicas
}
