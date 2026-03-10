# Terraform variables for Braintrust conversation Lambda
variable "AWS_REGION" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "AWS_PROFILE" {
  description = "AWS profile"
  type        = string
  default     = "profile"
}

variable "ENVIRONMENT" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "PROJECT_NAME" {
  description = "Project name for resource naming (AWS)"
  type        = string
  default     = "braintrust-multi-turn-conversation"
}

variable "FUNCTION_NAME" {
  description = "Lambda function name (AWS)"
  type        = string
  default     = "braintrust-multi-turn-conversation-lambda"
}

variable "OWNER" {
  description = "Owner tag value (AWS)"
  type        = string
  default     = "admin@example.com"
}

variable "COMMON_TAGS" {
  description = "Additional tags to apply to all resources (AWS)"
  type        = map(string)
  default     = {}
}

# Lambda configuration
variable "LAMBDA_MEMORY_SIZE" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 512
}

variable "LAMBDA_TIMEOUT" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

# Braintrust configuration
variable "BRAINTRUST_API_KEY" {
  description = "Braintrust API key"
  type        = string
  sensitive   = true
}

variable "BRAINTRUST_PROJECT_ID" {
  description = "Braintrust project ID"
  type        = string
}

# OpenAI configuration
variable "OPENAI_API_KEY" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

# Logging
variable "LOG_RETENTION_DAYS" {
  description = "CloudWatch Logs retention period in days"
  type        = number
  default     = 7
}

# Tags configuration
locals {
  common_tags = merge(
    {
      Environment = var.ENVIRONMENT
      Project     = var.PROJECT_NAME
      ManagedBy   = "terraform"
      Owner       = var.OWNER
      Purpose     = "multi-turn-tracing-lambda-example"
      Repository  = "braintrust-workbench"
    },
    var.COMMON_TAGS
  )
}
