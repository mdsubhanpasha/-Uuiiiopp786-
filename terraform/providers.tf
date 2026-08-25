terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "finagent-ops-tf-state"
    key            = "terraform/state/finagent-ops.tfstate"
    region         = "us-east-1"
    dynamodb_table = "finagent-ops-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "FinAgent-Ops"
      ManagedBy   = "Terraform"
    }
  }
}
