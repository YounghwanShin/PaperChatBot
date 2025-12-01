'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { apiClient, ChatMessage as ApiChatMessage, PaperMetadata } from '@/lib/api';
import { Message, createMessage, getErrorMessage } from '@/lib/messageUtils';
import { MAX_CONVERSATION_HISTORY } from '@/lib/constants';
import ReactMarkdown from 'react-markdown';

interface ChatInterfaceProps {
  paper: PaperMetadata;
}

export default function ChatInterface({ paper }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Reset messages when paper changes
    setMessages([]);
  }, [paper.paper_id]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    const userMessage = createMessage('user', inputMessage);
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const conversationHistory: ApiChatMessage[] = messages
        .slice(-MAX_CONVERSATION_HISTORY)
        .map(msg => ({ role: msg.role, content: msg.content }));

      const response = await apiClient.chatWithPaper(
        paper.paper_id,
        inputMessage,
        conversationHistory
      );

      const assistantMessage = createMessage(
        'assistant',
        response.answer,
        response.confidence,
        response.rewritten_query
      );

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error:', error);

      const errorContent = getErrorMessage(error);
      const errorMessage = createMessage('assistant', errorContent);

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 custom-scrollbar">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-16 px-4 animate-fade-in">
              <div className="relative inline-block mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl">
                  <Bot className="w-10 h-10 text-white" />
                </div>
              </div>

              <h2 className="text-3xl font-bold text-gray-900 mb-3">
                Ask me about this paper!
              </h2>
              <p className="text-gray-600 mb-6 max-w-md mx-auto text-lg">
                {paper.title}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-3xl mx-auto">
                {[
                  'What is the main contribution of this paper?',
                  'What methodology did the authors use?',
                  'What are the key findings?',
                  'What are the limitations of this work?',
                ].map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputMessage(question)}
                    className="group text-left p-5 bg-white/70 backdrop-blur border border-gray-200 rounded-2xl hover:border-blue-400 hover:shadow-lg hover:bg-white transition-all duration-300 hover:-translate-y-1"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <span className="text-blue-600 font-semibold text-sm">Q</span>
                      </div>
                      <p className="text-sm text-gray-700 font-medium pt-1">{question}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 items-start animate-slide-in ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}

              <div
                className={`max-w-2xl ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg'
                    : 'bg-white/90 backdrop-blur border border-gray-200 shadow-md'
                } px-5 py-4 rounded-2xl`}
              >
                <div className={`prose prose-sm max-w-none ${
                  message.role === 'user' ? 'text-white prose-invert' : 'text-gray-800'
                }`}>
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {message.role === 'assistant' && (message.confidence || message.rewrittenQuery) && (
                  <div className="mt-3 pt-3 border-t border-gray-200/50 space-y-2">
                    {message.rewrittenQuery && (
                      <div className="text-xs text-gray-500 italic">
                        <span className="font-semibold">Query optimized:</span> {message.rewrittenQuery}
                      </div>
                    )}
                    {message.confidence && (
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full rounded-full transition-all duration-500"
                            style={{ width: `${message.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600 font-medium">
                          {(message.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-9 h-9 bg-gradient-to-br from-gray-200 to-gray-300 rounded-xl flex items-center justify-center shadow-md">
                  <User className="w-5 h-5 text-gray-600" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 items-start animate-pulse">
              <div className="flex-shrink-0 w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white/90 backdrop-blur border border-gray-200 px-5 py-4 rounded-2xl shadow-md">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                  <span className="text-sm text-gray-600">Analyzing paper...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200/50 bg-white/80 backdrop-blur-md px-4 py-4 shadow-lg">
        <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask a question about this paper..."
                className="w-full px-5 py-4 pr-12 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all bg-white shadow-sm disabled:bg-gray-50 disabled:text-gray-400"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="px-6 py-4 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-2xl hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200 flex items-center justify-center gap-2 font-medium shadow-md"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
