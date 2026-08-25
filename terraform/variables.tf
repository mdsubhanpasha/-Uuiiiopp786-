variable "aws_region" {
  description = "The AWS region where resources will be provisioned."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (e.g. production, staging, dev)."
  type        = string
  default     = "production"
}

variable "cluster_name" {
  description = "Name of the Kubernetes (EKS) cluster."
  type        = string
  default     = "finagent-ops-cluster"
}

variable "vpc_cidr" {
  description = "CIDR block for the Virtual Private Cloud (VPC)."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "availability_zones" {
  description = "Availability zones for subnet distribution."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "node_group_min_size" {
  description = "Minimum number of worker nodes in EKS node group."
  type        = number
  default     = 2
}

variable "node_group_max_size" {
  description = "Maximum number of worker nodes in EKS node group."
  type        = number
  default     = 10
}

variable "node_group_desired_size" {
  description = "Desired number of worker nodes in EKS node group."
  type        = number
  default     = 3
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS worker nodes."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "container_repository_name" {
  description = "Name of the Container Registry (ECR) repository."
  type        = string
  default     = "finagent-ops"
}
