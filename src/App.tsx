import { ChatWindow } from './components/ChatWindow';
import { useChat } from './hooks/useChat';
import './App.css';

function App() {
  const {
    messages,
    isLoading,
    error,
    useRag,
    setUseRag,
    promptKey,
    setPromptKey,
    availablePrompts,
    sendMessage,
    clearChat
  } = useChat({
    onError: (err) => console.error('Chat error:', err)
  });

  return (
    <div className="app">
      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        error={error}
        onSendMessage={sendMessage}
        onClearChat={clearChat}
        useRag={useRag}
        onToggleRag={setUseRag}
        promptKey={promptKey}
        onChangePrompt={setPromptKey}
        availablePrompts={availablePrompts}
      />
    </div>
  );
}

export default App;
