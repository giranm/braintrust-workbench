// DynamoDB conversation state management

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
} from "@aws-sdk/lib-dynamodb";
import { ConversationState } from "./types";

const client = new DynamoDBClient({});
const dynamodb = DynamoDBDocumentClient.from(client);

const TABLE_NAME = process.env.CONVERSATION_TABLE || "braintrust-conversations-dev";

/**
 * Get conversation state from DynamoDB
 */
export async function getConversationState(
  conversationId: string
): Promise<ConversationState | null> {
  try {
    console.log(`Fetching conversation state for: ${conversationId}`);

    const result = await dynamodb.send(
      new GetCommand({
        TableName: TABLE_NAME,
        Key: { conversation_id: conversationId },
      })
    );

    if (!result.Item) {
      console.log(`No existing state found for conversation: ${conversationId}`);
      return null;
    }

    return result.Item as ConversationState;
  } catch (error) {
    console.error("Error fetching conversation state:", error);
    throw new Error(`Failed to fetch conversation state: ${error}`);
  }
}

/**
 * Save conversation state to DynamoDB
 */
export async function saveConversationState(
  conversationId: string,
  state: Omit<ConversationState, "conversation_id" | "created_at" | "updated_at">
): Promise<void> {
  try {
    console.log(`Saving conversation state for: ${conversationId}`);

    const now = Date.now();
    const item: ConversationState = {
      conversation_id: conversationId,
      ...state,
      updated_at: now,
    };

    // Only set created_at on first save (when message_count is 1)
    if (state.message_count === 1) {
      item.created_at = now;
    }

    await dynamodb.send(
      new PutCommand({
        TableName: TABLE_NAME,
        Item: item,
      })
    );

    console.log(`Successfully saved state for conversation: ${conversationId}`);
  } catch (error) {
    console.error("Error saving conversation state:", error);
    throw new Error(`Failed to save conversation state: ${error}`);
  }
}
