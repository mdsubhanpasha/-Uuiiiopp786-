# WHY: Multi-Cloud Configuration Variables for Terraform.
# WHAT: Defines input variables for AWS us-west-2, GCP, and Azure deployments.
# WHERE USED: 1-terraform/main.tf
# RECRUITER ANSWER: "Enables single-parameter region switching with us-west-2 default for cost and compliance optimization."

variable "aws_region" {
  type        = string
  default     = "us-west-2"
  description = "Primary AWS region"
}

variable "gcp_project_id" {
  type        = string
  default     = "pasha-q-omni-2050-project"
  description = "GCP Project ID for GKE Autopilot"
}

variable "gcp_region" {
  type        = string
  default     = "us-west1"
  description = "Primary GCP region"
}

variable "azure_location" {
  type        = string
  default     = "westus2"
  description = "Primary Azure region"
}

variable "azure_resource_group" {
  type        = string
  default     = "pasha-q-omni-rg"
  description = "Azure Resource Group"
}

variable "aws_eks_role_arn" {
  type        = string
  default     = "arn:aws:iam::123456789012:role/PashaEKSClusterRole"
  description = "IAM Role ARN for EKS Cluster"
}

variable "aws_node_role_arn" {
  type        = string
  default     = "arn:aws:iam::123456789012:role/PashaEKSNodeRole"
  description = "IAM Role ARN for EKS Node Group"
}
