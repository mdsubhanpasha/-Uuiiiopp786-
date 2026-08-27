output "instance_id" {
  description = "ID of the deployed EC2 application instance"
  value       = aws_instance.app_server.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 application instance"
  value       = aws_instance.app_server.public_ip
}

output "security_group_id" {
  description = "Security group ID associated with the application instance"
  value       = aws_security_group.app_sg.id
}
