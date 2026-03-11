# DynamoDB table for conversation state

resource "aws_dynamodb_table" "conversations" {
  name         = "${var.ENVIRONMENT}-${var.PROJECT_NAME}-conversations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "conversation_id"

  attribute {
    name = "conversation_id"
    type = "S"
  }

  # Enable point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = true
  }

  # Enable TTL for automatic cleanup of old conversations
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = merge(
    local.common_tags,
    {
      Name      = "${var.ENVIRONMENT}-${var.PROJECT_NAME}-conversations"
      Component = "conversation-state"
    }
  )
}
