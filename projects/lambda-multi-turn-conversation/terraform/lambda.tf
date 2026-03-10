# Lambda function for conversation handling with Braintrust tracing

# IAM role for Lambda execution
resource "aws_iam_role" "lambda_execution" {
  name               = "${var.ENVIRONMENT}-${var.PROJECT_NAME}-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.ENVIRONMENT}-${var.PROJECT_NAME}-lambda-role"
      Component = "iam"
    }
  )
}

# Attach AWS managed policy for basic Lambda execution (CloudWatch Logs)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy for DynamoDB access
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "${var.ENVIRONMENT}-${var.PROJECT_NAME}-dynamodb-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.conversations.arn
      }
    ]
  })
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.ENVIRONMENT}-${var.FUNCTION_NAME}"
  retention_in_days = var.LOG_RETENTION_DAYS

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.ENVIRONMENT}-${var.FUNCTION_NAME}-logs"
      Component = "logging"
    }
  )
}

# Lambda function
resource "aws_lambda_function" "conversation_handler" {
  function_name = "${var.ENVIRONMENT}-${var.FUNCTION_NAME}"
  role          = aws_iam_role.lambda_execution.arn

  # Placeholder configuration - actual code deployed via deploy.sh
  filename         = "${path.module}/lambda_placeholder.zip"
  source_code_hash = fileexists("${path.module}/lambda_placeholder.zip") ? filebase64sha256("${path.module}/lambda_placeholder.zip") : null

  runtime = "nodejs20.x"
  handler = "index.handler"

  memory_size = var.LAMBDA_MEMORY_SIZE
  timeout     = var.LAMBDA_TIMEOUT

  environment {
    variables = {
      BRAINTRUST_API_KEY     = var.BRAINTRUST_API_KEY
      BRAINTRUST_PROJECT_ID  = var.BRAINTRUST_PROJECT_ID
      OPENAI_API_KEY         = var.OPENAI_API_KEY
      CONVERSATION_TABLE     = aws_dynamodb_table.conversations.name
      NODE_ENV               = var.ENVIRONMENT
    }
  }

  # Ensure log group is created before Lambda
  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy_attachment.lambda_basic_execution
  ]

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.ENVIRONMENT}-${var.FUNCTION_NAME}"
      Component = "conversation-handler"
      Runtime   = "nodejs20"
    }
  )
}

# Create placeholder zip for initial terraform apply
resource "null_resource" "create_placeholder_zip" {
  triggers = {
    # Only recreate if the zip file doesn't exist
    zip_exists = fileexists("${path.module}/lambda_placeholder.zip") ? "exists" : "missing"
  }

  provisioner "local-exec" {
    command = <<-EOT
      if [ ! -f ${path.module}/lambda_placeholder.zip ]; then
        mkdir -p ${path.module}/placeholder
        echo 'exports.handler = async (event) => { return { statusCode: 200, body: "Placeholder" }; };' > ${path.module}/placeholder/index.js
        cd ${path.module}/placeholder && zip -q ../lambda_placeholder.zip index.js
        rm -rf ${path.module}/placeholder
      fi
    EOT
  }
}
