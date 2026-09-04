terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS Region for Edge Infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Target domain name for NAYEEM-EDGE"
  type        = string
  default     = "nayeem-edge.enterprise.io"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}
