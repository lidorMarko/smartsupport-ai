import type { Message } from '../types/chat';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

interface BackendChatResponse {
  message: string;
  sources?: string[];
  tool_calls?: ToolCall[];
}

export interface ChatResult {
  message: string;
  toolCalls?: ToolCall[];
}

interface ChatOptions {
  useRag?: boolean;
  promptKey?: string;
  useTools?: boolean;
}

export interface PromptOption {
  key: string;
  name: string;
  description: string;
}

export async function sendChatMessage(
  messages: Message[],
  options: ChatOptions = {}
): Promise<ChatResult> {
  const { useRag = true, promptKey = 'default', useTools = true } = options;

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      use_rag: useRag,
      prompt_key: promptKey,
      use_tools: useTools,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  const data: BackendChatResponse = await response.json();

  // Append sources if available
  let message = data.message;
  if (data.sources && data.sources.length > 0) {
    message += `\n\n📚 *Sources: ${data.sources.join(', ')}*`;
  }

  return {
    message,
    toolCalls: data.tool_calls,
  };
}

// Get available system prompts
export async function getAvailablePrompts(): Promise<PromptOption[]> {
  const response = await fetch(`${API_BASE_URL}/api/prompts`);

  if (!response.ok) {
    throw new Error('Failed to fetch prompts');
  }

  return response.json();
}

// Document management functions
export async function uploadDocument(file: File): Promise<{ chunks_added: number; message: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || `Upload error: ${response.status}`);
  }

  return response.json();
}

export async function addTextToKnowledgeBase(
  texts: string[],
  metadatas?: Record<string, string>[]
): Promise<{ chunks_added: number; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/documents/add-text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ texts, metadatas }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to add text' }));
    throw new Error(error.detail || `Error: ${response.status}`);
  }

  return response.json();
}

export async function getKnowledgeBaseStats(): Promise<{
  total_documents: number;
  collection_name: string;
}> {
  const response = await fetch(`${API_BASE_URL}/api/documents/stats`);

  if (!response.ok) {
    throw new Error('Failed to get stats');
  }

  return response.json();
}

export async function clearKnowledgeBase(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/documents/clear`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to clear knowledge base');
  }
}
