// TypeScript type definitions for the Lambda handler

export interface LambdaEvent {
  body: string;
  headers?: Record<string, string>;
  requestContext?: {
    requestId: string;
    identity?: {
      sourceIp?: string;
    };
  };
}

export interface LambdaResponse {
  statusCode: number;
  body: string;
  headers?: Record<string, string>;
}

export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface RequestBody {
  conversationId: string;
  messages: Message[];
  userId: string;
}

export interface ConversationState {
  conversation_id: string;
  root_span_export: string;
  last_span_export: string;
  message_count: number;
  created_at?: number;
  updated_at?: number;
}

export interface LLMResponse {
  message: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
