import type { Message, ToolCall } from '../types/chat';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

const TOOL_DISPLAY_NAMES: Record<string, string> = {
  schedule_technician: 'קביעת תור לטכנאי',
  send_confirmation_email: 'שליחת אימייל אישור'
};

function ToolCallDisplay({ toolCall }: Readonly<{ toolCall: ToolCall }>) {
  const displayName = TOOL_DISPLAY_NAMES[toolCall.tool] || toolCall.tool;
  const result = toolCall.result;
  const isSuccess = result.success === true;
  const message = typeof result.message === 'string' ? result.message : '';

  return (
    <div className={`tool-call ${isSuccess ? 'success' : 'error'}`}>
      <div className="tool-call-header">
        <span className="tool-icon">{isSuccess ? '✅' : '❌'}</span>
        <span className="tool-name">{displayName}</span>
      </div>
      {message && (
        <div className="tool-call-result">{message}</div>
      )}
    </div>
  );
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-role">{isUser ? 'You' : 'Assistant'}</span>
          <span className="message-time">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
        </div>

        {/* Display tool calls if any */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="tool-calls">
            {message.toolCalls.map((tc, index) => (
              <ToolCallDisplay key={index} toolCall={tc} />
            ))}
          </div>
        )}

        <div className="message-text">{message.content}</div>
      </div>
    </div>
  );
}
