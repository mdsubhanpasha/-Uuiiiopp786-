output "edge_server_public_ip" {
  description = "Elastic IP address allocated to NAYEEM-EDGE EC2 server"
  value       = aws_eip.edge_eip.public_ip
}

output "edge_domain_name" {
  description = "Route53 managed domain name"
  value       = var.domain_name
}

output "edge_http_url" {
  description = "Primary HTTP Endpoint"
  value       = "http://${var.domain_name}"
}

output "edge_https_url" {
  description = "Primary Secure HTTPS Endpoint"
  value       = "https://${var.domain_name}"
}

output "edge_instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.edge_server.id
}
