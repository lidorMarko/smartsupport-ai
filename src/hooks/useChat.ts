import { useState, useCallback, useEffect } from 'react';
import type { Message } from '../types/chat';
import { sendChatMessage, getAvailablePrompts, type PromptOption } from '../services/chatService';

const generateId = () => Math.random().toString(36).substring(2, 15);

interface UseChatOptions {
  onError?: (error: Error) => void;
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useRag, setUseRag] = useState(true);
  const [useTools, setUseTools] = useState(true);
  const [promptKey, setPromptKey] = useState('default');
  const [availablePrompts, setAvailablePrompts] = useState<PromptOption[]>([]);

  // Fetch available prompts on mount
  useEffect(() => {
    getAvailablePrompts()
      .then(setAvailablePrompts)
      .catch((err) => console.error('Failed to fetch prompts:', err));
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const result = await sendChatMessage(
        [...messages, userMessage],
        { useRag, promptKey, useTools }
      );

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: result.message,
        timestamp: new Date(),
        toolCalls: result.toolCalls
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      options.onError?.(err instanceof Error ? err : new Error(errorMessage));
    } finally {
      setIsLoading(false);
    }
  }, [messages, useRag, useTools, promptKey, options]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const retryLastMessage = useCallback(async () => {
    const lastUserMessage = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUserMessage) {
      setMessages((prev) => {
        const lastIndex = prev.length - 1;
        if (prev[lastIndex]?.role === 'assistant') {
          return prev.slice(0, lastIndex);
        }
        return prev;
      });
      await sendMessage(lastUserMessage.content);
    }
  }, [messages, sendMessage]);

  return {
    messages,
    isLoading,
    error,
    useRag,
    setUseRag,
    useTools,
    setUseTools,
    promptKey,
    setPromptKey,
    availablePrompts,
    sendMessage,
    clearChat,
    retryLastMessage
  };
}
