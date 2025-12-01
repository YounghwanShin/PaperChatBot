'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, Loader2, CheckCircle, XCircle, Download, Clock } from 'lucide-react';
import { apiClient, ArxivFetchResponse, ArxivFetchTaskStatus } from '@/lib/api';
import { FILE_UPLOAD } from '@/lib/constants';

interface PaperUploadProps {
  onUploadSuccess: (paper: { paper_id: string; title: string }) => void;
}

export default function PaperUpload({ onUploadSuccess }: PaperUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [abstract, setAbstract] = useState('');
  const [authors, setAuthors] = useState('');
  const [year, setYear] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  // arXiv fetch states
  const [isFetchingArxiv, setIsFetchingArxiv] = useState(false);
  const [arxivFetchResult, setArxivFetchResult] = useState<ArxivFetchResponse | null>(null);
  const [arxivFetchStatus, setArxivFetchStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [arxivProgress, setArxivProgress] = useState<string>('');
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      if (selectedFile.size > FILE_UPLOAD.MAX_SIZE) {
        setErrorMessage(`File size must be less than ${FILE_UPLOAD.MAX_SIZE / 1024 / 1024}MB`);
        setUploadStatus('error');
        return;
      }

      if (!selectedFile.name.endsWith('.pdf')) {
        setErrorMessage('Only PDF files are allowed');
        setUploadStatus('error');
        return;
      }

      setFile(selectedFile);
      setUploadStatus('idle');
      setErrorMessage('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file || !title.trim() || !abstract.trim()) {
      setErrorMessage('Please fill in all required fields and select a PDF file');
      setUploadStatus('error');
      return;
    }

    try {
      setIsUploading(true);
      setUploadStatus('idle');
      setErrorMessage('');

      const response = await apiClient.uploadPaper(
        file,
        title,
        abstract,
        authors,
        year ? parseInt(year) : undefined
      );

      setUploadStatus('success');
      setTimeout(() => {
        onUploadSuccess(response);
        resetForm();
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      setErrorMessage('Failed to upload paper. Please try again.');
      setUploadStatus('error');
    } finally {
      setIsUploading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setTitle('');
    setAbstract('');
    setAuthors('');
    setYear('');
    setUploadStatus('idle');
    setErrorMessage('');
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const pollTaskStatus = async (taskId: string) => {
    try {
      const status = await apiClient.getFetchStatus(taskId);

      // Update progress
      if (status.progress) {
        setArxivProgress(status.progress);
      }

      // Check if completed
      if (status.status === 'completed' && status.result) {
        // Clear polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }

        setArxivFetchResult(status.result);
        setArxivFetchStatus('success');
        setIsFetchingArxiv(false);
        setArxivProgress('');

        // Auto-hide success message after 5 seconds
        setTimeout(() => {
          setArxivFetchStatus('idle');
        }, 5000);
      } else if (status.status === 'failed') {
        // Clear polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }

        setArxivFetchStatus('error');
        setIsFetchingArxiv(false);
        setArxivProgress('');
        console.error('arXiv fetch failed:', status.error);
      }
    } catch (error) {
      console.error('Error polling task status:', error);
      // Continue polling even if one request fails
    }
  };

  const handleFetchRecentPapers = async () => {
    try {
      setIsFetchingArxiv(true);
      setArxivFetchStatus('idle');
      setArxivFetchResult(null);
      setArxivProgress('Starting...');

      // Start background task
      const taskStart = await apiClient.fetchRecentPapers(7);

      // Start polling for status
      pollingIntervalRef.current = setInterval(() => {
        pollTaskStatus(taskStart.task_id);
      }, 2000); // Poll every 2 seconds

    } catch (error) {
      console.error('arXiv fetch error:', error);
      setArxivFetchStatus('error');
      setIsFetchingArxiv(false);
      setArxivProgress('');
    }
  };

  return (
    <div className="h-full p-6 overflow-y-auto">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* arXiv recent Fetch Section */}
        <div className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-2xl p-6 shadow-md">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Download className="w-6 h-6 text-purple-600" />
                Auto-Fetch from arXiv
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Automatically fetch and process NLP papers from the last 7 days
              </p>
            </div>
          </div>

          <button
            onClick={handleFetchRecentPapers}
            disabled={isFetchingArxiv}
            className="w-full px-6 py-4 bg-gradient-to-br from-purple-500 to-indigo-600 text-white rounded-xl hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200 flex items-center justify-center gap-2 font-medium shadow-md"
          >
            {isFetchingArxiv ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {arxivProgress || 'Processing...'}
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Fetch Recent NLP Papers
              </>
            )}
          </button>

          {/* arXiv Fetch Results */}
          {arxivFetchStatus === 'success' && arxivFetchResult && (
            <div className="mt-4 p-4 bg-white rounded-lg border border-purple-200">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-gray-900">Fetch Completed!</span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-gray-600">Total Found</div>
                  <div className="text-2xl font-bold text-blue-600">{arxivFetchResult.total_found}</div>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-gray-600">Successfully Processed</div>
                  <div className="text-2xl font-bold text-green-600">{arxivFetchResult.successfully_processed}</div>
                </div>
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <div className="text-gray-600">Duplicates Skipped</div>
                  <div className="text-2xl font-bold text-yellow-600">{arxivFetchResult.skipped_duplicates}</div>
                </div>
                <div className="bg-red-50 p-3 rounded-lg">
                  <div className="text-gray-600">Failed</div>
                  <div className="text-2xl font-bold text-red-600">{arxivFetchResult.failed}</div>
                </div>
              </div>
              {arxivFetchResult.papers.length > 0 && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg max-h-40 overflow-y-auto">
                  <div className="text-xs font-semibold text-gray-600 mb-2">Added Papers:</div>
                  {arxivFetchResult.papers.map((paper, idx) => (
                    <div key={idx} className="text-xs text-gray-700 mb-1">
                      • {paper.title} ({paper.chunks_created} chunks)
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {arxivFetchStatus === 'error' && (
            <div className="mt-4 flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <XCircle className="w-5 h-5" />
              <span>Failed to fetch papers from arXiv. Please try again.</span>
            </div>
          )}
        </div>

        {/* Manual Upload Section */}
        <div className="bg-white/90 backdrop-blur border border-gray-200 rounded-2xl p-8 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Upload className="w-7 h-7 text-blue-500" />
            Manual Upload
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PDF File *
              </label>
              <div className="flex items-center gap-4">
                <label className="flex-1 cursor-pointer">
                  <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 hover:border-blue-400 transition-all">
                    <div className="flex flex-col items-center gap-2">
                      <FileText className="w-8 h-8 text-gray-400" />
                      <p className="text-sm text-gray-600">
                        {file ? file.name : 'Click to select PDF file'}
                      </p>
                      {file && (
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      )}
                    </div>
                  </div>
                  <input
                    type="file"
                    accept={FILE_UPLOAD.ACCEPTED_TYPES}
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Paper Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter paper title"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all"
                required
              />
            </div>

            {/* Authors */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Authors
              </label>
              <input
                type="text"
                value={authors}
                onChange={(e) => setAuthors(e.target.value)}
                placeholder="e.g., John Doe, Jane Smith"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all"
              />
            </div>

            {/* Year */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Publication Year
              </label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                placeholder="e.g., 2024"
                min="1900"
                max={new Date().getFullYear()}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all"
              />
            </div>

            {/* Abstract */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Abstract *
              </label>
              <textarea
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                placeholder="Enter paper abstract..."
                rows={6}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all resize-none"
                required
              />
            </div>

            {/* Status Messages */}
            {uploadStatus === 'success' && (
              <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
                <CheckCircle className="w-5 h-5" />
                <span>Paper uploaded successfully!</span>
              </div>
            )}

            {uploadStatus === 'error' && errorMessage && (
              <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                <XCircle className="w-5 h-5" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={isUploading || !file || !title.trim() || !abstract.trim()}
                className="flex-1 px-6 py-4 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-2xl hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200 flex items-center justify-center gap-2 font-medium shadow-md"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Uploading & Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    Upload Paper
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={resetForm}
                disabled={isUploading}
                className="px-6 py-4 bg-gray-100 text-gray-700 rounded-2xl hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
              >
                Reset
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
