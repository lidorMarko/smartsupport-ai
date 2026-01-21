import type { Message } from '../types/chat';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface BackendChatResponse {
  message: string;
  sources?: string[];
}

interface ChatOptions {
  useRag?: boolean;
  promptKey?: string;
}

export interface PromptOption {
  key: string;
  name: string;
  description: string;
}

export async function sendChatMessage(
  messages: Message[],
  options: ChatOptions = {}
): Promise<string> {
  const { useRag = true, promptKey = 'default' } = options;

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
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  const data: BackendChatResponse = await response.json();

  // Append sources if available
  let result = data.message;
  if (data.sources && data.sources.length > 0) {
    result += `\n\n📚 *Sources: ${data.sources.join(', ')}*`;
  }

  return result;
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
