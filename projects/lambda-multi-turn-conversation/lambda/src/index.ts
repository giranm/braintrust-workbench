// Main Lambda handler with multi-turn Braintrust tracing

import { initLogger, traced, wrapOpenAI } from "braintrust";
import OpenAI from "openai";
import { getConversationState, saveConversationState } from "./conversation";
import {
  LambdaEvent,
  LambdaResponse,
  RequestBody,
  Message,
  LLMResponse,
} from "./types";

// Initialize Braintrust logger and keep reference for explicit flushing
// CRITICAL: asyncFlush: false ensures logs are flushed before Lambda terminates
const logger = initLogger({
  projectId: process.env.BRAINTRUST_PROJECT_ID!,
  apiKey: process.env.BRAINTRUST_API_KEY!,
  asyncFlush: false,
});

// Initialize OpenAI client with Braintrust wrapper for automatic tracing
const openai = wrapOpenAI(
  new OpenAI({
    apiKey: process.env.OPENAI_API_KEY!,
  })
);

console.log("Braintrust logger and OpenAI client initialized");

/**
 * Call OpenAI API with conversation messages
 */
async function callLLM(messages: Message[]): Promise<LLMResponse> {
  console.log("Calling OpenAI API...", {
    model: "gpt-4o-mini",
    messageCount: messages.length,
  });

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: messages,
    temperature: 0.7,
  });

  const content = response.choices[0].message.content || "";
  const usage = response.usage || {
    prompt_tokens: 0,
    completion_tokens: 0,
    total_tokens: 0,
  };

  console.log("OpenAI response received", {
    contentLength: content.length,
    usage,
  });

  return {
    message: content,
    usage: {
      prompt_tokens: usage.prompt_tokens,
      completion_tokens: usage.completion_tokens,
      total_tokens: usage.total_tokens,
    },
  };
}

/**
 * Lambda handler with multi-turn tracing
 */
export const handler = async (event: LambdaEvent): Promise<LambdaResponse> => {
  console.log("Lambda invoked:", {
    requestId: event.requestContext?.requestId,
    hasBody: !!event.body,
  });

  try {
    // Parse request body
    const { conversationId, messages, userId }: RequestBody = JSON.parse(event.body);

    console.log(`Processing message for conversation: ${conversationId}`, {
      userId,
      messageCount: messages.length,
    });

    // Validate required fields
    if (!conversationId || !messages || !userId) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          error: "Missing required fields: conversationId, messages, userId",
        }),
      };
    }

    // Fetch conversation state from DynamoDB
    let state = await getConversationState(conversationId);
    const messageNumber = (state?.message_count || 0) + 1;
    const isFirstMessage = messageNumber === 1;

    console.log(`Message number: ${messageNumber}`, {
      hasExistingState: !!state,
      previousMessageCount: state?.message_count || 0,
      isFirstMessage,
    });

    // Variable to store the result
    let result: LLMResponse;

    // If this is the first message, create a root "conversation" span
    // and nest turn-1 inside it so we can log the first response
    if (isFirstMessage) {
      console.log("Creating root conversation span with first turn nested...");

      await traced(
        async (conversationSpan) => {
          // Log initial input and metadata for the conversation
          conversationSpan.log({
            input: {
              initial_message: messages[0], // First user message
              conversation_started: new Date().toISOString(),
            },
            metadata: {
              conversation_id: conversationId,
              user_id: userId,
              created_at: new Date().toISOString(),
            },
          });

          // Create turn-1 span NESTED inside the root conversation span
          result = await traced(
            async (turnSpan) => {
              console.log("Inside turn-1 span (nested in conversation)");

              // Log input with metadata
              turnSpan.log({
                input: messages,
                metadata: {
                  conversation_id: conversationId,
                  user_id: userId,
                  message_number: 1,
                  request_id: event.requestContext?.requestId,
                  source_ip: event.requestContext?.identity?.sourceIp,
                },
              });

              // Call LLM
              console.log("Calling LLM...");
              const llmResponse = await callLLM(messages);
              console.log("LLM response received");

              // Log output and metrics to turn span
              turnSpan.log({
                output: llmResponse.message,
                metrics: {
                  prompt_tokens: llmResponse.usage.prompt_tokens,
                  completion_tokens: llmResponse.usage.completion_tokens,
                  total_tokens: llmResponse.usage.total_tokens,
                },
              });

              return llmResponse;
            },
            {
              name: `turn-1`,
              type: "llm",
              // Turn-1 has no parent here - it's nested in the conversation span
            }
          );

          // Now log the first response as OUTPUT to the conversation span
          conversationSpan.log({
            output: {
              first_response: result.message,
              tokens_used: result.usage,
            },
          });

          // Export the conversation span at the END
          const rootExport = await conversationSpan.export();
          console.log("Root conversation span exported with first response");

          // Save root span to DynamoDB
          await saveConversationState(conversationId, {
            root_span_export: rootExport,
            last_span_export: rootExport,
            message_count: 1,
          });

          // Reload state with root span
          state = await getConversationState(conversationId);
        },
        {
          name: `conversation`,
          type: "task",
          // No parent - this is the root span
        }
      );

      // Explicit flush after root span to ensure it's sent to Braintrust
      console.log("Flushing root conversation span to Braintrust...");
      await logger.flush();
      console.log("Root span flushed");
    } else {
      // For subsequent messages, create turn span as child of root conversation
      result = await traced(
        async (span) => {
          console.log("Inside message span", {
            messageNumber,
            hasRootParent: !!state?.root_span_export,
          });

          // Log input with metadata
          span.log({
            input: messages,
            metadata: {
              conversation_id: conversationId,
              user_id: userId,
              message_number: messageNumber,
              request_id: event.requestContext?.requestId,
              source_ip: event.requestContext?.identity?.sourceIp,
            },
          });

          // Call LLM
          console.log("Calling LLM...");
          const llmResponse = await callLLM(messages);
          console.log("LLM response received", {
            responseLength: llmResponse.message.length,
            tokens: llmResponse.usage,
          });

          // Log output and metrics
          span.log({
            output: llmResponse.message,
            metrics: {
              prompt_tokens: llmResponse.usage.prompt_tokens,
              completion_tokens: llmResponse.usage.completion_tokens,
              total_tokens: llmResponse.usage.total_tokens,
            },
          });

          return llmResponse;
        },
        {
          name: `turn-${messageNumber}`,
          type: "llm",
          // KEY: All messages are children of the ROOT conversation span
          parent: state?.root_span_export,
        }
      );
    }

    // Update message count in DynamoDB AFTER span completes
    await saveConversationState(conversationId, {
      root_span_export: state!.root_span_export,
      last_span_export: state!.root_span_export, // Keep root, don't chain messages
      message_count: messageNumber,
    });

    console.log("Turn span completed, flushing to Braintrust...");

    // Explicit flush to ensure turn span is sent immediately to Braintrust
    // This prevents the "1 message delay" issue where spans appear in progress
    await logger.flush();
    console.log("Turn span flushed - trace now visible in Braintrust UI");

    return {
      statusCode: 200,
      body: JSON.stringify({
        response: result!.message,
        conversationId,
        messageNumber,
        usage: result!.usage,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    };
  } catch (error) {
    console.error("Error processing request:", error);

    return {
      statusCode: 500,
      body: JSON.stringify({
        error: "Internal server error",
        message: error instanceof Error ? error.message : String(error),
      }),
      headers: {
        "Content-Type": "application/json",
      },
    };
  }
};
