# Terraform outputs

output "lambda_function_name" {
  description = "Lambda function name for client invocation"
  value       = aws_lambda_function.conversation_handler.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.conversation_handler.arn
}

output "lambda_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_execution.arn
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for conversation state"
  value       = aws_dynamodb_table.conversations.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.conversations.arn
}

output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = var.AWS_REGION
}

output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment         = var.ENVIRONMENT
    lambda_function     = aws_lambda_function.conversation_handler.function_name
    dynamodb_table      = aws_dynamodb_table.conversations.name
    lambda_memory_mb    = var.LAMBDA_MEMORY_SIZE
    lambda_timeout_sec  = var.LAMBDA_TIMEOUT
  }
}

# Instructions for next steps
output "next_steps" {
  description = "Next steps for deployment"
  value = <<-EOT
    Infrastructure deployed successfully!

    Next steps:
    1. Build Lambda function:
       cd ../lambda && npm install && npm run build

    2. Deploy Lambda code:
       ./deploy.sh

    3. Test with Python client:
       cd .. && python client.py --function ${aws_lambda_function.conversation_handler.function_name} --profile ${var.AWS_PROFILE}

    4. Verify in Braintrust UI:
       - Open Braintrust dashboard
       - Navigate to project: ${var.BRAINTRUST_PROJECT_ID}
       - Check for multi-turn trace structure
  EOT
}
