export type ChatMessage = {
  id: string;
  user_id: string;
  cheatsheet_id: string;
  role: "user" | "assistant";
  message: string;
  created_at: string;
};

export type ChatAskResponse = {
  answer: string;
  retrieved_chunks: number;
  processing_time_ms: number;
};
