// MongoDB initialization for conversation content storage
// Usage:
//   mongosh "mongodb://localhost:27017/zhixue" mongo-init.js

const zhixueDb = db.getSiblingDB("zhixue");

zhixueDb.createCollection("conversation_threads", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["qnaSessionId", "userId", "currentMode", "title", "createdAt", "updatedAt"],
      properties: {
        qnaSessionId: { bsonType: "string", description: "PostgreSQL app.qna_session.id" },
        smartEngineSessionId: { bsonType: ["string", "null"] },
        userId: { bsonType: "string", description: "User UUID" },
        currentMode: { enum: ["QNA", "SMART_ENGINE"] },
        title: { bsonType: "string" },
        latestMessageSeq: { bsonType: ["int", "long", "null"] },
        metadata: { bsonType: ["object", "null"] },
        createdAt: { bsonType: "date" },
        updatedAt: { bsonType: "date" }
      }
    }
  }
});

zhixueDb.conversation_threads.createIndex(
  { qnaSessionId: 1 },
  { unique: true, name: "uq_thread_qna_session" }
);

zhixueDb.conversation_threads.createIndex(
  { userId: 1, updatedAt: -1 },
  { name: "idx_thread_user_updated" }
);

zhixueDb.conversation_threads.createIndex(
  { smartEngineSessionId: 1 },
  {
    name: "idx_thread_engine_session",
    partialFilterExpression: { smartEngineSessionId: { $type: "string" } }
  }
);

zhixueDb.createCollection("conversation_messages", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["threadId", "qnaSessionId", "userId", "messageId", "messageSeq", "role", "content", "createdAt"],
      properties: {
        threadId: { bsonType: "objectId", description: "conversation_threads._id" },
        qnaSessionId: { bsonType: "string" },
        smartEngineSessionId: { bsonType: ["string", "null"] },
        userId: { bsonType: "string" },
        messageId: { bsonType: "string" },
        messageSeq: { bsonType: ["int", "long"] },
        role: { enum: ["user", "assistant", "system", "agent"] },
        messageType: { bsonType: ["string", "null"] },
        content: { bsonType: "string" },
        references: {
          bsonType: ["array", "null"],
          items: {
            bsonType: "object",
            properties: {
              title: { bsonType: ["string", "null"] },
              snippet: { bsonType: ["string", "null"] },
              score: { bsonType: ["double", "int", "long", "null"] },
              resourceId: { bsonType: ["string", "null"] },
              url: { bsonType: ["string", "null"] }
            }
          }
        },
        confidence: { bsonType: ["double", "int", "long", "null"] },
        safetyFlags: { bsonType: ["array", "null"], items: { bsonType: "string" } },
        createdAt: { bsonType: "date" }
      }
    }
  }
});

zhixueDb.conversation_messages.createIndex(
  { qnaSessionId: 1, messageSeq: 1 },
  { unique: true, name: "uq_message_session_seq" }
);

zhixueDb.conversation_messages.createIndex(
  { qnaSessionId: 1, messageId: 1 },
  { unique: true, name: "uq_message_session_id" }
);

zhixueDb.conversation_messages.createIndex(
  { threadId: 1, messageSeq: 1 },
  { name: "idx_message_thread_seq" }
);

zhixueDb.conversation_messages.createIndex(
  { userId: 1, createdAt: -1 },
  { name: "idx_message_user_created" }
);

zhixueDb.createCollection("conversation_stream_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["threadId", "qnaSessionId", "eventType", "payload", "createdAt"],
      properties: {
        threadId: { bsonType: "objectId" },
        qnaSessionId: { bsonType: "string" },
        eventType: { bsonType: "string" },
        payload: { bsonType: "object" },
        createdAt: { bsonType: "date" },
        expiresAt: { bsonType: ["date", "null"] }
      }
    }
  }
});

zhixueDb.conversation_stream_events.createIndex(
  { qnaSessionId: 1, createdAt: 1 },
  { name: "idx_stream_session_created" }
);

zhixueDb.conversation_stream_events.createIndex(
  { expiresAt: 1 },
  {
    name: "ttl_stream_events",
    expireAfterSeconds: 0,
    partialFilterExpression: { expiresAt: { $type: "date" } }
  }
);

print("MongoDB init completed for database: zhixue");
