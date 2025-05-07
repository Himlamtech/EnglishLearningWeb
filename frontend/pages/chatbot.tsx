import React, { useState, useRef, useEffect } from 'react';
import { api, ChatMessage } from '../app/api';
import { toast } from 'react-hot-toast';

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your language learning assistant. How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Add all previous messages to provide context
      const response = await api.chat.sendMessage([...messages, userMessage]);
      
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response
        }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to get response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold gradient-text">Language Chatbot</h1>
        <p className="mt-2 text-gray-600">
          Chat with an AI assistant to improve your language skills
        </p>
      </div>

      <div className="card max-w-3xl mx-auto p-0 overflow-hidden">
        {/* Chat Messages */}
        <div className="h-[500px] overflow-y-auto p-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${
                message.role === 'user' ? 'text-right' : 'text-left'
              }`}
            >
              <div
                className={`inline-block max-w-[80%] px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-primary-dark text-white rounded-tr-none'
                    : 'bg-white text-gray-800 shadow rounded-tl-none'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="text-left mb-4">
              <div className="inline-block max-w-[80%] px-4 py-2 rounded-lg bg-white text-gray-800 shadow rounded-tl-none">
                <p className="animate-pulse">Thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-4 border-t">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              className="input-field flex-grow"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="btn-primary px-4"
              disabled={loading || !input.trim()}
            >
              Send
            </button>
          </form>
        </div>
      </div>

      <div className="max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Suggested Topics</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <button
            onClick={() => setInput('Can you explain the difference between "their", "there", and "they\'re"?')}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Explain "their", "there", "they're"
          </button>
          <button
            onClick={() => setInput('What are some common Vietnamese greetings?')}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Vietnamese greetings
          </button>
          <button
            onClick={() => setInput('How do I use past tense in English?')}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Past tense in English
          </button>
          <button
            onClick={() => setInput('What\'s the difference between "a" and "the"?')}
            className="text-left p-2 bg-gray-100 hover:bg-gray-200 rounded"
          >
            Articles: "a" vs "the"
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
