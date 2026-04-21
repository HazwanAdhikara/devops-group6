variable "resource_group_name" {
  description = "Nama Resource Group Azure"
  default     = "rg-observability-project"
}

variable "location" {
  description = "Region Azure"
  default     = "Southeast Asia"
}

variable "vm_size" {
  description = "Ukuran VM (2 vCPU, 4GB RAM)"
  default     = "Standard_B2s_v2" # Spesifikasi 2 vCPU, 4GB RAM
}

variable "admin_username" {
  description = "Username admin untuk VM"
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  description = "Path ke file SSH public key"
  type     = string
}

variable "my_ip" {
  description = "IP Publik untuk akses SSH dan Grafana"
  type        = string
}