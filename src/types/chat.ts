export type MessageRole = 'user' | 'assistant' | 'system';

export interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
