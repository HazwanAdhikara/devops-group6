output "app_node_public_ip" {
  value = azurerm_public_ip.app_ip.ip_address
}

output "monitoring_node_public_ip" {
  value = azurerm_public_ip.mon_ip.ip_address
}

output "app_node_private_ip" {
  value = azurerm_linux_virtual_machine.app_node.private_ip_address
}

output "monitoring_node_private_ip" {
  value = azurerm_linux_virtual_machine.mon_node.private_ip_address
}