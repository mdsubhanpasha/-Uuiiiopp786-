# Security Group for NAYEEM-EDGE Server
resource "aws_security_group" "edge_sg" {
  name        = "nayeem-edge-security-group"
  description = "Allow inbound HTTP, HTTPS, and SSH traffic for Enterprise Edge Delivery Fabric"

  ingress {
    description = "HTTP Inbound"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Inbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "nayeem-edge-sg"
    Environment = var.environment
    Project     = "NAYEEM-EDGE"
  }
}

# Ubuntu 22.04 LTS AMI Data Source
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

# EC2 Instance for NAYEEM-EDGE Nginx Edge Node
resource "aws_instance" "edge_server" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t3.micro"
  vpc_security_group_ids = [aws_security_group.edge_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y nginx certbot python3-certbot-nginx
              systemctl enable nginx
              systemctl start nginx
              EOF

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name        = "nayeem-edge-ec2-server"
    Environment = var.environment
    Project     = "NAYEEM-EDGE"
    ManagedBy   = "Terraform"
  }
}

# Elastic IP for Edge Delivery Fabric
resource "aws_eip" "edge_eip" {
  instance = aws_instance.edge_server.id
  domain   = "vpc"

  tags = {
    Name        = "nayeem-edge-eip"
    Environment = var.environment
    Project     = "NAYEEM-EDGE"
  }
}
