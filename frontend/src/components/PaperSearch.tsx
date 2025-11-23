'use client';

import React, { useState, useEffect } from 'react';
import { Search, FileText, Users, Calendar, Loader2 } from 'lucide-react';
import { apiClient, PaperMetadata } from '@/lib/api';

interface PaperSearchProps {
  onSelectPaper: (paper: PaperMetadata) => void;
}

export default function PaperSearch({ onSelectPaper }: PaperSearchProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PaperMetadata[]>([]);
  const [allPapers, setAllPapers] = useState<PaperMetadata[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAllPapers();
  }, []);

  const loadAllPapers = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.listPapers();
      setAllPapers(response.papers);
      setSearchResults(response.papers);
      setError(null);
    } catch (err) {
      setError('Failed to load papers');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults(allPapers);
      return;
    }

    try {
      setIsSearching(true);
      setError(null);
      const response = await apiClient.searchPapers({
        query: searchQuery,
        top_k: 10,
        score_threshold: 0.5,
      });
      setSearchResults(response.results as any);
    } catch (err) {
      setError('Search failed');
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="h-full p-6 overflow-y-auto">
      <div className="max-w-5xl mx-auto">
        {/* Search Bar */}
        <div className="mb-6">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Search papers by title, abstract, or keywords..."
                className="w-full px-5 py-4 pr-12 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all bg-white shadow-sm"
              />
              <Search className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="px-6 py-4 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-2xl hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200 flex items-center justify-center gap-2 font-medium shadow-md min-w-[120px]"
            >
              {isSearching ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Searching
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Search
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        )}

        {/* Results */}
        {!isLoading && searchResults.length === 0 && (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No Papers Found
            </h3>
            <p className="text-gray-500">
              {searchQuery ? 'Try adjusting your search terms' : 'Upload a paper to get started'}
            </p>
          </div>
        )}

        <div className="space-y-4">
          {searchResults.map((paper) => (
            <div
              key={paper.paper_id}
              className="bg-white/90 backdrop-blur border border-gray-200 rounded-2xl p-6 hover:border-blue-400 hover:shadow-lg transition-all duration-300 cursor-pointer"
              onClick={() => onSelectPaper(paper)}
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-bold text-gray-900 flex-1 pr-4">
                  {paper.title}
                </h3>
                {paper.score !== undefined && (
                  <div className="flex items-center gap-2 bg-blue-50 px-3 py-1 rounded-full">
                    <span className="text-xs text-blue-700 font-medium">
                      {(paper.score * 100).toFixed(0)}% match
                    </span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                {paper.authors && (
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    <span>{paper.authors}</span>
                  </div>
                )}
                {paper.year && (
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>{paper.year}</span>
                  </div>
                )}
              </div>

              <p className="text-sm text-gray-700 line-clamp-3">
                {paper.abstract}
              </p>

              <div className="mt-4 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {paper.page_count} pages
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectPaper(paper);
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  Select & Chat →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
