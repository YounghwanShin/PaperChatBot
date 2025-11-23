'use client';

import React, { useState } from 'react';
import { BookOpen } from 'lucide-react';
import PaperSearch from '@/components/PaperSearch';
import PaperUpload from '@/components/PaperUpload';
import ChatInterface from '@/components/ChatInterface';
import { PaperMetadata } from '@/lib/api';

export default function Home() {
  const [selectedPaper, setSelectedPaper] = useState<PaperMetadata | null>(null);
  const [activeTab, setActiveTab] = useState<'search' | 'upload' | 'chat'>('search');

  const handlePaperSelect = (paper: PaperMetadata) => {
    setSelectedPaper(paper);
    setActiveTab('chat');
  };

  const handleUploadSuccess = (paper: { paper_id: string; title: string }) => {
    setActiveTab('search');
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Paper Research Assistant
                </h1>
                <p className="text-xs text-gray-500">
                  Search, upload, and chat with research papers
                </p>
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('search')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'search'
                    ? 'bg-blue-500 text-white shadow-md'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Search Papers
              </button>
              <button
                onClick={() => setActiveTab('upload')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'upload'
                    ? 'bg-blue-500 text-white shadow-md'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Upload Paper
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                disabled={!selectedPaper}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeTab === 'chat'
                    ? 'bg-blue-500 text-white shadow-md'
                    : selectedPaper
                    ? 'bg-white text-gray-600 hover:bg-gray-50'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                Chat
              </button>
            </div>
          </div>

          {/* Selected Paper Info */}
          {selectedPaper && (
            <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-900">
                    Selected: {selectedPaper.title}
                  </p>
                  <p className="text-xs text-blue-600">
                    {selectedPaper.authors}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedPaper(null)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Clear
                </button>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'search' && (
          <PaperSearch onSelectPaper={handlePaperSelect} />
        )}
        {activeTab === 'upload' && (
          <PaperUpload onUploadSuccess={handleUploadSuccess} />
        )}
        {activeTab === 'chat' && selectedPaper && (
          <ChatInterface paper={selectedPaper} />
        )}
        {activeTab === 'chat' && !selectedPaper && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                No Paper Selected
              </h3>
              <p className="text-gray-500">
                Please search for and select a paper to start chatting
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
