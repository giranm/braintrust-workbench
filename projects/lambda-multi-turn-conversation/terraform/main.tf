# Main Terraform configuration

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }

  # Using local state for development
  # For production, consider using S3 backend:
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "braintrust-validation/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# AWS Provider configuration
provider "aws" {
  region = var.AWS_REGION
  profile = var.AWS_PROFILE
  default_tags {
    tags = local.common_tags
  }
}
