import { useEffect, useRef } from 'react';
import type { Message } from '../types/chat';
import type { PromptOption } from '../services/chatService';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import './ChatWindow.css';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onSendMessage: (message: string) => void;
  onClearChat?: () => void;
  useRag: boolean;
  onToggleRag: (enabled: boolean) => void;
  promptKey: string;
  onChangePrompt: (key: string) => void;
  availablePrompts: PromptOption[];
}

export function ChatWindow({
  messages,
  isLoading,
  error,
  onSendMessage,
  onClearChat,
  useRag,
  onToggleRag,
  promptKey,
  onChangePrompt,
  availablePrompts
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const currentPrompt = availablePrompts.find(p => p.key === promptKey);

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="chat-avatar">🤖</div>
          <div>
            <h1 className="chat-title">SmartSupport AI</h1>
            <span className="chat-status">
              {isLoading ? 'Thinking...' : 'Online'}
            </span>
          </div>
        </div>
        <div className="chat-header-actions">
          <div className="rag-toggle">
            <label className="toggle-label">
              <span className="toggle-text">RAG</span>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={useRag}
                  onChange={(e) => onToggleRag(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </div>
            </label>
          </div>
          {onClearChat && messages.length > 0 && (
            <button
              className="clear-chat-button"
              onClick={onClearChat}
              aria-label="Clear chat"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Prompt Selector Bar */}
      <div className="prompt-selector-bar">
        <label htmlFor="prompt-select">System Prompt:</label>
        <select
          id="prompt-select"
          value={promptKey}
          onChange={(e) => onChangePrompt(e.target.value)}
          className="prompt-select"
        >
          {availablePrompts.map((prompt) => (
            <option key={prompt.key} value={prompt.key}>
              {prompt.name}
            </option>
          ))}
        </select>
        {currentPrompt && (
          <span className="prompt-description">{currentPrompt.description}</span>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="welcome-icon">💬</div>
            <h2>Welcome to SmartSupport AI</h2>
            <p>Ask me anything! I'm here to help you.</p>
            <div className="settings-status">
              <p className="rag-status">
                RAG: <strong>{useRag ? 'ON' : 'OFF'}</strong>
              </p>
              <p className="prompt-status">
                Prompt: <strong>{currentPrompt?.name || 'Default'}</strong>
              </p>
            </div>
            <div className="suggested-prompts">
              <button onClick={() => onSendMessage('What can you help me with?')}>
                What can you help me with?
              </button>
              <button onClick={() => onSendMessage('Tell me about RAG')}>
                Tell me about RAG
              </button>
              <button onClick={() => onSendMessage('How do AI agents work?')}>
                How do AI agents work?
              </button>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}

        {isLoading && (
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}

        {error && (
          <div className="chat-error">
            <span>⚠️</span> {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSendMessage={onSendMessage} disabled={isLoading} />
    </div>
  );
}
